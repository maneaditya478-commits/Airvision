"use client";

import dynamic from "next/dynamic";
import { useEffect, useState } from "react";
import { getAQIColor } from "@/lib/utils";

const MapContainer = dynamic(() => import("react-leaflet").then((m) => m.MapContainer), { ssr: false });
const TileLayer = dynamic(() => import("react-leaflet").then((m) => m.TileLayer), { ssr: false });
const CircleMarker = dynamic(() => import("react-leaflet").then((m) => m.CircleMarker), { ssr: false });
const Popup = dynamic(() => import("react-leaflet").then((m) => m.Popup), { ssr: false });

export interface MapDataPoint {
  latitude: number;
  longitude: number;
  value: number;
  category?: string | null;
  label?: string | null;
}

interface InteractiveMapProps {
  aqiPoints?: MapDataPoint[];
  hchoPoints?: MapDataPoint[];
  firePoints?: MapDataPoint[];
  windPoints?: MapDataPoint[];
  height?: string;
}

export default function InteractiveMap({
  aqiPoints = [],
  hchoPoints = [],
  firePoints = [],
  windPoints = [],
  height = "600px",
}: InteractiveMapProps) {
  const [showAQI, setShowAQI] = useState(true);
  const [showHCHO, setShowHCHO] = useState(true);
  const [showFire, setShowFire] = useState(true);
  const [showWind, setShowWind] = useState(false);

  return (
    <div style={{ height }} className="relative rounded-lg overflow-hidden border border-border flex flex-col md:flex-row">
      {/* Map Control Sidebar Overlay */}
      <div className="absolute top-4 right-4 z-[1000] bg-card/90 border border-border backdrop-blur-md p-4 rounded-lg shadow-lg w-64 space-y-4">
        <h4 className="text-sm font-bold text-foreground">Interactive Map Layers</h4>
        <div className="space-y-3">
          <label className="flex items-center gap-3 cursor-pointer select-none text-xs font-semibold text-foreground">
            <input
              type="checkbox"
              checked={showAQI}
              onChange={(e) => setShowAQI(e.target.checked)}
              className="rounded border-border bg-background text-primary focus:ring-primary"
            />
            <span>CPCB Ground AQI Layer</span>
          </label>
          <label className="flex items-center gap-3 cursor-pointer select-none text-xs font-semibold text-foreground">
            <input
              type="checkbox"
              checked={showHCHO}
              onChange={(e) => setShowHCHO(e.target.checked)}
              className="rounded border-border bg-background text-primary focus:ring-primary"
            />
            <span>Sentinel-5P HCHO Layer</span>
          </label>
          <label className="flex items-center gap-3 cursor-pointer select-none text-xs font-semibold text-foreground">
            <input
              type="checkbox"
              checked={showFire}
              onChange={(e) => setShowFire(e.target.checked)}
              className="rounded border-border bg-background text-primary focus:ring-primary"
            />
            <span>NASA FIRMS Fire Layer</span>
          </label>
          <label className="flex items-center gap-3 cursor-pointer select-none text-xs font-semibold text-foreground">
            <input
              type="checkbox"
              checked={showWind}
              onChange={(e) => setShowWind(e.target.checked)}
              className="rounded border-border bg-background text-primary focus:ring-primary"
            />
            <span>ERA5 Wind Flow Layer</span>
          </label>
        </div>
      </div>

      <div className="flex-1 h-full w-full">
        <MapContainer center={[22.5, 79]} zoom={5} style={{ height: "100%", width: "100%" }}>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {/* AQI Layer */}
          {showAQI && aqiPoints.map((p, i) => (
            <CircleMarker
              key={`aqi-${i}`}
              center={[p.latitude, p.longitude]}
              radius={Math.max(8, Math.min(22, p.value / 12))}
              pathOptions={{
                color: getAQIColor(p.category),
                fillColor: getAQIColor(p.category),
                fillOpacity: 0.75,
                weight: 1.5,
              }}
            >
              <Popup>
                <div className="text-xs">
                  <p className="font-bold text-sm text-foreground">{p.label}</p>
                  <p className="mt-1">AQI: <span className="font-bold" style={{ color: getAQIColor(p.category) }}>{p.value}</span> ({p.category})</p>
                </div>
              </Popup>
            </CircleMarker>
          ))}

          {/* HCHO Hotspots Layer */}
          {showHCHO && hchoPoints.map((p, i) => (
            <CircleMarker
              key={`hcho-${i}`}
              center={[p.latitude, p.longitude]}
              radius={10}
              pathOptions={{
                color: p.category === "high" ? "#ef4444" : p.category === "medium" ? "#f97316" : "#eab308",
                fillColor: p.category === "high" ? "#ef4444" : p.category === "medium" ? "#f97316" : "#eab308",
                fillOpacity: 0.6,
                weight: 1.5,
              }}
            >
              <Popup>
                <div className="text-xs">
                  <p className="font-bold text-foreground">{p.label}</p>
                  <p className="mt-0.5">HCHO Density: {p.value.toFixed(4)} µmol/m²</p>
                  <p>Intensity Class: <span className="font-bold uppercase">{p.category}</span></p>
                </div>
              </Popup>
            </CircleMarker>
          ))}

          {/* Fire Points Layer */}
          {showFire && firePoints.map((p, i) => (
            <CircleMarker
              key={`fire-${i}`}
              center={[p.latitude, p.longitude]}
              radius={6}
              pathOptions={{
                color: "#dc2626",
                fillColor: "#ef4444",
                fillOpacity: 0.8,
                weight: 1,
              }}
            >
              <Popup>
                <div className="text-xs">
                  <p className="font-bold text-red-500">Active Fire Detected</p>
                  <p className="mt-0.5">{p.label}</p>
                  <p>Location: {p.latitude.toFixed(4)}, {p.longitude.toFixed(4)}</p>
                </div>
              </Popup>
            </CircleMarker>
          ))}

          {/* Wind Vector Layer */}
          {showWind && windPoints.map((p, i) => (
            <CircleMarker
              key={`wind-${i}`}
              center={[p.latitude, p.longitude]}
              radius={5}
              pathOptions={{
                color: "#0284c7",
                fillColor: "#0ea5e9",
                fillOpacity: 0.5,
                weight: 1,
              }}
            >
              <Popup>
                <div className="text-xs">
                  <p className="font-bold text-sky-400">ERA5 Wind Vector</p>
                  <p className="mt-0.5">{p.label}</p>
                </div>
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>
    </div>
  );
}
