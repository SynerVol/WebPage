import React, { useState, useEffect, useRef } from "react";
import { MapContainer, TileLayer, Marker, Circle, Polygon, useMapEvents } from "react-leaflet";
import { io } from "socket.io-client";
import "leaflet/dist/leaflet.css";


// Automatically use the IP address of the machine serving the page
// for debug
//const serverIP = window.location.hostname;

// automatic routing with docker compose 
const serverIP = "python-back"

// Connect to your Python Bridge
const socket = io(`http://${serverIP}:8080`, {
  transports: ["websocket", "polling"]
});

export default function App() {
  const [selected, setSelected] = useState(null);
  const [drones, setDrones] = useState({ leader: null, follower: null });
  const [radius, setRadius] = useState(50);

  // Listen for Telemetry from Backend
  useEffect(() => {
    socket.on("telemetry", (data) => {
      setDrones(data);
    });
    return () => socket.off("telemetry");
  }, []);

  const sendMission = () => {
    if (!selected) return alert("Sélectionnez un point sur la carte !");
    socket.emit("start_mission", {
      coordinates: { lat: selected.lat, lng: selected.lng },
      dimensions: { radius: radius }
    });
  };

  const stopMission = () => {
    socket.emit("emergency_stop");
  };

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      {/* Map Side */}
      <div style={{ flex: 1 }}>
        <MapContainer center={[-35.363, 149.165]} zoom={15} style={{ height: "100%" }}>
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
          <MapClick onSelect={setSelected} />

          {selected && <Circle center={[selected.lat, selected.lng]} radius={parseInt(radius)} color="red" />}

          {/* Real-time Drone Markers */}
          {drones.leader && <Marker position={[drones.leader[0], drones.leader[1]]} />}
          {drones.follower && <Marker position={[drones.follower[0], drones.follower[1]]} />}
        </MapContainer>
      </div>

      {/* Control Panel Side */}
      <div style={{ width: "350px", padding: "20px", background: "#f8f9fa" }}>
        <h2>SynerVol Control</h2>
        <p>Status: {drones.leader ? "📡 Connected" : "❌ Disconnected"}</p>

        <label>Rayon (m):</label>
        <input type="number" value={radius} onChange={e => setRadius(e.target.value)} />

        <button onClick={sendMission} style={{ width: "100%", padding: "10px", margin: "10px 0", background: "#0f172a", color: "white" }}>
          🚀 Lancer Mission
        </button>

        <button onClick={stopMission} style={{ width: "100%", padding: "10px", background: "#ef4444", color: "white" }}>
          🛑 ARRÊT D'URGENCE (RTL)
        </button>
      </div>
    </div>
  );
}

function MapClick({ onSelect }) {
  useMapEvents({ click(e) { onSelect({ lat: e.latlng.lat, lng: e.latlng.lng }); } });
  return null;
}