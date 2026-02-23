import React, { useState, useEffect } from "react";
import { MapContainer, TileLayer, Marker, Circle, Polygon, useMapEvents } from "react-leaflet";
import * as turf from "@turf/turf";
import "leaflet/dist/leaflet.css";
import Logo from "./assets/logo avec arrière-plan supprimé.png";

function MapClick({ onSelect }) {
  useMapEvents({
    click(e) {
      onSelect({ lat: e.latlng.lat, lng: e.latlng.lng });
    }
  });
  return null;
}

export default function App() {
  const [selected, setSelected] = useState(null);
  const [shape, setShape] = useState("circle");
  const [radius, setRadius] = useState(50);
  const [side, setSide] = useState(100);
  const [angle, setAngle] = useState(0);
  const [previewCoords, setPreviewCoords] = useState(null);
  const [scanType, setScanType] = useState("circle");

  useEffect(() => {
    if (!selected) { setPreviewCoords(null); return; }
    if (shape === "circle") {
      const circle = turf.circle([selected.lng, selected.lat], radius/1000, { steps: 64, units: "kilometers" });
      setPreviewCoords(circle.geometry.coordinates[0].map(c => [c[1], c[0]]));
    } else {
      const half = side / 2;
      const square = turf.polygon([[
        [-half, -half], [half, -half], [half, half], [-half, half], [-half, -half]
      ]]);
      const rotated = turf.transformRotate(square, angle);
      const coords = rotated.geometry.coordinates[0].map(pt => {
        const p = turf.destination(turf.point([selected.lng, selected.lat]), Math.sqrt(pt[0]*pt[0]+pt[1]*pt[1])/1000, Math.atan2(pt[1], pt[0])*180/Math.PI, {units: "kilometers"});
        return [p.geometry.coordinates[1], p.geometry.coordinates[0]];
      });
      setPreviewCoords(coords);
    }
  }, [selected, shape, radius, side, angle]);

  return (
  <div style={{ display: "flex", height: "100vh", width: "100vw" }}>

    <div style={{ width: "70%", height: "100vh" }}>
      <MapContainer
        center={[48.8566, 2.3522]}
        zoom={13}
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        <MapClick onSelect={setSelected} />
        {selected && <Marker position={[selected.lat, selected.lng]} />}
          {shape === "circle" && selected && <Circle center={[selected.lat, selected.lng]} radius={radius} />}
          {shape === "square" && previewCoords && <Polygon positions={previewCoords} />}
      </MapContainer>
    </div>
    <div style={{
      width: "30%",
      padding: "2.5rem",
      background: "linear-gradient(180deg, #ffffff 0%, #f3f6fa 100%)",
      borderLeft: "1px solid #d0d6dd",
      boxShadow: "-4px 0 14px rgba(0,0,0,0.07)",
      fontFamily: "Inter, sans-serif",
      color: "#1a1a1a"
    }}>
      <div style={{ 
        textAlign: "center", 
        marginBottom: "2rem",
        paddingBottom: "1rem",
        borderBottom: "1px solid #e0e4e8"
      }}>
        <img
          src={Logo}
          alt="SynerVol Logo"
          style={{
            width: "110px",
            height: "auto",
            marginBottom: "0.8rem",
            opacity: "0.98",
            filter: "drop-shadow(0 0 4px rgba(0,0,0,0.15))"
          }}
        />
        <h2 style={{ margin: 0, fontSize: "2rem", fontWeight: "700", color: "#0f172a" }}>SynerVol</h2>
        <p style={{ margin: 0, fontSize: "1rem", color: "#475569", marginTop: "0.5rem" }}>
          Outil d’orchestration d’exploration cartographique autonome
        </p>
      </div>
      <div style={{
        marginTop: "1.5rem",
        padding: "1rem",
        background: "#ffffff",
        borderRadius: "8px",
        boxShadow: "0 2px 6px rgba(0,0,0,0.05)",
        border: "1px solid #e5e7eb"
      }}>
        <div style={{ fontSize: "1rem", fontWeight: "600", marginBottom: "0.5rem" }}>
          Coordonnées :
        </div>
        {selected ? `${selected.lat.toFixed(5)}, ${selected.lng.toFixed(5)}` : " clique sur la carte"}
      </div>

      <div style={{
        marginTop: "1.5rem",
        padding: "1rem",
        background: "#ffffff",
        borderRadius: "8px",
        boxShadow: "0 2px 6px rgba(0,0,0,0.05)",
        border: "1px solid #e5e7eb"
      }}>
        <label>Forme : </label>
        <select value={shape} onChange={e => setShape(e.target.value)}>
          <option value="circle">Cercle</option>
          <option value="square">Carré</option>
        </select>
      </div>

      <div style={{
        marginTop: "1.5rem",
        padding: "1.2rem",
        background: "#ffffff",
        borderRadius: "8px",
        boxShadow: "0 2px 6px rgba(0,0,0,0.05)",
        border: "1px solid #e5e7eb"
      }}>
        <label>Type de balayage :</label>
        <select value={scanType} onChange={e => setScanType(e.target.value)} style={{
          padding: "0.4rem 0.6rem",
          borderRadius: "6px",
          border: "1px solid #cbd5e1",
          marginTop: "0.4rem",
          width: "100%"
        }}>
          <option value="circle">Circulaire</option>
          <option value="square">Carré</option>
        </select>
      </div>

      {shape === "circle" && (
        <div style={{
          marginTop: "1.5rem",
          padding: "1rem",
          background: "#ffffff",
          borderRadius: "8px",
          boxShadow: "0 2px 6px rgba(0,0,0,0.05)",
          border: "1px solid #e5e7eb"
        }}>
          <label>Rayon (m): </label>
          <input type="number" value={radius} onChange={e => setRadius(e.target.value)} style={{
            padding: "0.4rem 0.6rem",
            borderRadius: "6px",
            border: "1px solid #cbd5e1",
            marginTop: "0.4rem"
          }} />
        </div>
      )}

      {shape === "square" && (
        <div style={{
          marginTop: "1.5rem",
          padding: "1rem",
          background: "#ffffff",
          borderRadius: "8px",
          boxShadow: "0 2px 6px rgba(0,0,0,0.05)",
          border: "1px solid #e5e7eb"
        }}>
          <label>Côté (m): </label>
          <input type="number" value={side} onChange={e => setSide(e.target.value)} style={{
            padding: "0.4rem 0.6rem",
            borderRadius: "6px",
            border: "1px solid #cbd5e1",
            marginTop: "0.4rem"
          }} />
        </div>
      )}

      <button
        onClick={() => {
          const ws = new WebSocket("ws://localhost:8080");
          ws.onopen = () => {
            const payload = {
              type: "mission",
              api_version: "1.0",
              coordinates: selected ? { lat: selected.lat, lng: selected.lng } : null,
              scan_type: scanType,
              dimensions: shape === "circle"
                ? { radius }
                : { side }
            };
            ws.send(JSON.stringify(payload));
            ws.close();
          };
        }}
        style={{
          marginTop: "1.5rem",
          padding: "0.8rem 1rem",
          width: "100%",
          background: "#0f172a",
          color: "white",
          fontWeight: "600",
          borderRadius: "8px",
          border: "none",
          cursor: "pointer",
          fontSize: "1rem",
          boxShadow: "0 2px 6px rgba(0,0,0,0.15)"
        }}
      >
        Envoyer la mission
      </button>
    </div>

  </div>
);
}