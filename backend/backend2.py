
import collections
import collections.abc

# The Patch: Must happen BEFORE dronekit is imported
collections.MutableMapping = collections.abc.MutableMapping
collections.Iterable = collections.abc.Iterable
collections.Callable = collections.abc.Callable

import socketio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dronekit import connect, Command, LocationGlobalRelative, VehicleMode
from pymavlink import mavutil
import math
import asyncio
import threading
import time

# --- CONFIGURATION ---
LEADER_PORT = 'tcp:127.0.0.1:5763'
FOLLOWER_PORT = 'tcp:127.0.0.1:5773'


class SwarmBackend:
    def __init__(self):
        self.leader = None
        self.follower = None
        self.connected = False
        self.target_location = None

    def connect_drones(self):
        try:
            print("Backend: Connexion au Leader...")
            self.leader = connect(LEADER_PORT, wait_ready=True)
            print("Backend: Connexion au Follower...")
            self.follower = connect(FOLLOWER_PORT, wait_ready=True)
            self.connected = True
            return True
        except Exception as e:
            print(f"Backend Erreur: {e}")
            return False

    def get_drone_positions(self):
        pos = {}
        try:
            if self.leader:
                loc = self.leader.location.global_relative_frame
                if loc.lat: pos['leader'] = (loc.lat, loc.lon)
            if self.follower:
                loc = self.follower.location.global_relative_frame
                if loc.lat: pos['follower'] = (loc.lat, loc.lon)
        except:
            pass
        return pos

    def emergency_stop(self):
        print("!!! ARRÊT D'URGENCE DÉCLENCHÉ !!!")
        if self.leader: self.leader.mode = VehicleMode("RTL")
        if self.follower: self.follower.mode = VehicleMode("RTL")

    def get_location_metres(self, original_location, dNorth, dEast, alt):
        earth_radius = 6378137.0
        dLat = dNorth / earth_radius * 180 / math.pi
        dLon = dEast / (earth_radius * math.cos(math.pi * original_location.lat / 180)) * 180 / math.pi
        return LocationGlobalRelative(original_location.lat + dLat, original_location.lon + dLon, alt)

    def generate_mission_points(self, center_lat, center_lon, radius, spacing, altitude, side="left"):
        mission_items = []
        center_loc_obj = type('obj', (object,), {'lat': center_lat, 'lon': center_lon, 'alt': altitude})
        mission_items.append(mavutil.mavlink.MAV_CMD_NAV_TAKEOFF)
        y = -radius
        direction = 1
        while y <= radius:
            if abs(y) >= radius:
                y += spacing
                continue
            x_span = math.sqrt(radius ** 2 - y ** 2)
            if side == "left":
                x_min, x_max = -x_span, 0
            else:
                x_min, x_max = 0, x_span
            p1 = self.get_location_metres(center_loc_obj, y, x_min if direction == 1 else x_max, altitude)
            p2 = self.get_location_metres(center_loc_obj, y, x_max if direction == 1 else x_min, altitude)
            mission_items.append(p1)
            mission_items.append(p2)
            y += spacing
            direction *= -1
        return mission_items

    def upload_mission_to_vehicle(self, vehicle, waypoints, altitude):
        cmds = vehicle.commands
        cmds.clear()
        cmds.add(
            Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0,
                    0, 0, 0, 0, 0, 0, altitude))
        for wp in waypoints:
            if isinstance(wp, LocationGlobalRelative):
                cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                                 mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, wp.lat, wp.lon, altitude))
        cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                         mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0, 0, 0, 0, 0, 0, 0, 0, 0))
        cmds.upload()

    def start_swarm_mission(self, center_lat, center_lon, radius, alt, fov):
        if not self.connected: return
        largeur_vue = 2 * alt * math.tan(math.radians(fov / 2))
        espacement = largeur_vue * 0.8
        print("Backend: Calcul des trajectoires...")
        wps1 = self.generate_mission_points(center_lat, center_lon, radius, espacement, alt, "left")
        wps2 = self.generate_mission_points(center_lat, center_lon, radius, espacement, alt, "right")
        self.upload_mission_to_vehicle(self.leader, wps1, alt)
        self.upload_mission_to_vehicle(self.follower, wps2, alt)

        print("Backend: Décollage Drone 1...")
        self.leader.mode = VehicleMode("GUIDED")
        self.leader.armed = True
        while not self.leader.armed: time.sleep(0.1)
        self.leader.simple_takeoff(5)
        print("Backend: Décollage Drone 2...")
        self.follower.mode = VehicleMode("GUIDED")
        self.follower.armed = True
        while not self.follower.armed: time.sleep(0.1)
        self.follower.simple_takeoff(5)
        print("Backend: Attente stabilisation...")
        time.sleep(6)
        print("Backend: Passage en AUTO...")
        self.leader.mode = VehicleMode("AUTO")
        self.follower.mode = VehicleMode("AUTO")

app = FastAPI()
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    logger=True,
    engineio_logger=True
)
socket_app = socketio.ASGIApp(sio, app)


class SwarmManager(SwarmBackend):  # Inherits your mission logic
    def __init__(self):
        super().__init__()
        self.connect_drones()

    async def stream_telemetry(self):
        while True:
            pos = self.get_drone_positions()
            if pos:
                await sio.emit('telemetry', pos)
            await asyncio.sleep(0.5)


manager = SwarmManager()


@sio.on('connect')
def handle_connect(sid, environ):
    print(f"Client connected: {sid}")


@sio.on('start_mission')
async def handle_mission(sid, data):
    print(f"Mission Received: {data}")
    try :
        coords = data.get('coordinates')
        dims = data.get('dimensions')
        if coords:
            # Launch in thread so we don't block the WebSocket loop
            threading.Thread(target=manager.start_swarm_mission,
                            args=(coords['lat'], coords['lng'],
                            float(dims.get('radius', 50)), 20, 60)).start()
    except Exception as e:
        print(f"Error parsing mission: {e}")

@sio.on('emergency_stop')
async def handle_stop(sid):
    manager.emergency_stop()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(manager.stream_telemetry())
    uvicorn.run(socket_app, host="0.0.0.0", port=8080)