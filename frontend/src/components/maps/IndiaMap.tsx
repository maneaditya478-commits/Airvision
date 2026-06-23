"use client";

import dynamic from "next/dynamic";
import { useEffect } from "react";
import { getAQIColor } from "@/lib/utils";

const MapContainer = dynamic(() => import("react-leaflet").then((m) => m.MapContainer), { ssr: false });
const TileLayer = dynamic(() => import("react-leaflet").then((m) => m.TileLayer), { ssr: false });
const CircleMarker = dynamic(() => import("react-leaflet").then((m) => m.CircleMarker), { ssr: false });
const Popup = dynamic(() => import("react-leaflet").then((m) => m.Popup), { ssr: false });
const Polyline = dynamic(() => import("react-leaflet").then((m) => m.Polyline), { ssr: false });

export interface MapPoint {
  latitude: number;
  longitude: number;
  value: number;
  category?: string | null;
  label?: string | null;
}

interface IndiaMapProps {
  points?: MapPoint[];
  center?: [number, number];
  zoom?: number;
  height?: string;
  colorMode?: "aqi" | "value" | "intensity";
  path?: Array<{ lat: number; lon: number }>;
}

export default function IndiaMap({
  points = [],
  center = [22.5, 79],
  zoom = 5,
  height = "500px",
  colorMode = "aqi",
  path,
}: IndiaMapProps) {
  const getColor = (point: MapPoint) => {
    if (colorMode === "aqi") return getAQIColor(point.category);
    if (colorMode === "intensity") {
      const c = point.category;
      if (c === "high") return "#ef4444";
      if (c === "medium") return "#f97316";
      return "#eab308";
    }
    const v = point.value;
    if (v > 300) return "#7E0023";
    if (v > 200) return "#FF0000";
    if (v > 100) return "#FF7E00";
    if (v > 50) return "#FFFF00";
    return "#00E400";
  };

  const getRadius = (point: MapPoint) => Math.max(6, Math.min(20, point.value / 15));

  return (
    <div style={{ height }} className="rounded-lg overflow-hidden border border-border">
      <MapContainer center={center} zoom={zoom} style={{ height: "100%", width: "100%" }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {points.map((point, i) => (
          <CircleMarker
            key={i}
            center={[point.latitude, point.longitude]}
            radius={getRadius(point)}
            pathOptions={{ color: getColor(point), fillColor: getColor(point), fillOpacity: 0.7 }}
          >
            <Popup>
              <div className="text-sm">
                <p className="font-semibold">{point.label || `Value: ${point.value.toFixed(1)}`}</p>
                {point.category && <p>Category: {point.category}</p>}
              </div>
            </Popup>
          </CircleMarker>
        ))}
        {path && path.length > 1 && (
          <Polyline
            positions={path.map((p) => [p.lat, p.lon] as [number, number])}
            pathOptions={{ color: "#0ea5e9", weight: 3, dashArray: "8 4" }}
          />
        )}
      </MapContainer>
    </div>
  );
}
