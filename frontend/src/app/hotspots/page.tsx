"use client";

import { useEffect, useState } from "react";
import AppLayout from "@/components/layout/AppLayout";
import IndiaMap from "@/components/maps/IndiaMap";
import { TemporalHotspotChart } from "@/components/charts/Charts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";

export default function HotspotsPage() {
  const [hotspots, setHotspots] = useState<Awaited<ReturnType<typeof api.getHotspots>>>([]);
  const [temporal, setTemporal] = useState<Awaited<ReturnType<typeof api.getHotspotTemporal>> | null>(null);
  const [loading, setLoading] = useState(true);
  const [detecting, setDetecting] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [hs, temp] = await Promise.all([api.getHotspots(), api.getHotspotTemporal()]);
      setHotspots(hs);
      setTemporal(temp);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  const handleDetect = async () => {
    setDetecting(true);
    try {
      const hs = await api.detectHotspots();
      setHotspots(hs);
    } catch (e) {
      console.error(e);
    } finally {
      setDetecting(false);
    }
  };

  const mapPoints = hotspots.map((h) => ({
    latitude: h.latitude,
    longitude: h.longitude,
    value: h.hcho_mean,
    category: h.intensity,
    label: `Cluster ${h.cluster_id}: HCHO ${h.hcho_mean}`,
  }));

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">HCHO Hotspot Detection</h1>
            <p className="text-muted-foreground mt-1">DBSCAN clustering on Sentinel-5P formaldehyde data</p>
          </div>
          <Button onClick={handleDetect} disabled={detecting}>
            {detecting ? "Detecting..." : "Run Detection"}
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card><CardContent className="pt-6"><p className="text-sm text-muted-foreground">Active Hotspots</p><p className="text-3xl font-bold">{hotspots.length}</p></CardContent></Card>
          <Card><CardContent className="pt-6"><p className="text-sm text-muted-foreground">High Intensity</p><p className="text-3xl font-bold text-red-500">{hotspots.filter(h => h.intensity === "high").length}</p></CardContent></Card>
          <Card><CardContent className="pt-6"><p className="text-sm text-muted-foreground">Total Points</p><p className="text-3xl font-bold">{hotspots.reduce((s, h) => s + h.point_count, 0)}</p></CardContent></Card>
        </div>

        <Card>
          <CardHeader><CardTitle>Hotspot Clusters Map</CardTitle></CardHeader>
          <CardContent>
            {loading ? <p className="text-muted-foreground">Loading...</p> : (
              <IndiaMap points={mapPoints} colorMode="intensity" height="450px" />
            )}
          </CardContent>
        </Card>

        {temporal && temporal.timeline.length > 0 && (
          <Card>
            <CardHeader><CardTitle>Temporal Hotspot Analysis</CardTitle></CardHeader>
            <CardContent>
              <TemporalHotspotChart data={temporal.timeline} />
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader><CardTitle>Detected Hotspots</CardTitle></CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border text-muted-foreground">
                    <th className="text-left py-2 px-3">Cluster</th>
                    <th className="text-left py-2 px-3">Location</th>
                    <th className="text-left py-2 px-3">HCHO Mean</th>
                    <th className="text-left py-2 px-3">HCHO Max</th>
                    <th className="text-left py-2 px-3">Points</th>
                    <th className="text-left py-2 px-3">Intensity</th>
                  </tr>
                </thead>
                <tbody>
                  {hotspots.map((h) => (
                    <tr key={h.id} className="border-b border-border/50">
                      <td className="py-2 px-3">{h.cluster_id}</td>
                      <td className="py-2 px-3">{h.latitude.toFixed(2)}, {h.longitude.toFixed(2)}</td>
                      <td className="py-2 px-3">{h.hcho_mean.toFixed(4)}</td>
                      <td className="py-2 px-3">{h.hcho_max.toFixed(4)}</td>
                      <td className="py-2 px-3">{h.point_count}</td>
                      <td className="py-2 px-3">
                        <span className={`px-2 py-0.5 rounded text-xs ${
                          h.intensity === "high" ? "bg-red-500/20 text-red-400"
                          : h.intensity === "medium" ? "bg-orange-500/20 text-orange-400"
                          : "bg-yellow-500/20 text-yellow-400"
                        }`}>{h.intensity}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
