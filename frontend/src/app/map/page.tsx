"use client";

import { useEffect, useState } from "react";
import AppLayout from "@/components/layout/AppLayout";
import InteractiveMap, { MapDataPoint } from "@/components/maps/InteractiveMap";
import { api } from "@/lib/api";

export default function MapPage() {
  const [aqi, setAqi] = useState<MapDataPoint[]>([]);
  const [hcho, setHcho] = useState<MapDataPoint[]>([]);
  const [fires, setFires] = useState<MapDataPoint[]>([]);
  const [wind, setWind] = useState<MapDataPoint[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadMapData() {
      try {
        const [aqiData, hchoData, fireData, windData] = await Promise.all([
          api.getAQIMap().catch(() => []),
          api.getHotspots(72).catch(() => []),
          api.getFirePoints(48).catch(() => []),
          api.getWindVectors(4).catch(() => []),
        ]);

        setAqi(
          aqiData.map((p) => ({
            latitude: p.latitude,
            longitude: p.longitude,
            value: p.value,
            category: p.category,
            label: p.label || `Station AQI: ${p.value}`,
          }))
        );

        setHcho(
          hchoData.map((h) => ({
            latitude: h.latitude,
            longitude: h.longitude,
            value: h.hcho_mean,
            category: h.intensity,
            label: `Hotspot Cluster ${h.cluster_id}`,
          }))
        );

        setFires(
          fireData.map((f) => ({
            latitude: f.latitude,
            longitude: f.longitude,
            value: f.frp || 0,
            label: `Fire FRP: ${f.frp?.toFixed(1) || 0} MW`,
          }))
        );

        setWind(
          windData.map((w) => ({
            latitude: w.latitude,
            longitude: w.longitude,
            value: w.speed,
            label: `Wind Flow: ${w.speed.toFixed(1)} m/s @ ${w.direction.toFixed(1)}°`,
          }))
        );
      } catch (err) {
        console.error("Error loading map telemetry:", err);
      } finally {
        setLoading(false);
      }
    }

    loadMapData();
  }, []);

  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Interactive AQI Map</h1>
          <p className="text-muted-foreground mt-1">Multi-layered geospatial overlay utilizing ground, satellite, wind, and thermal datasets.</p>
        </div>

        {loading ? (
          <div className="flex h-[600px] items-center justify-center rounded-lg border border-border bg-card">
            <p className="text-muted-foreground animate-pulse">Loading geospatial map layers...</p>
          </div>
        ) : (
          <InteractiveMap
            aqiPoints={aqi}
            hchoPoints={hcho}
            firePoints={fires}
            windPoints={wind}
            height="650px"
          />
        )}
      </div>
    </AppLayout>
  );
}
