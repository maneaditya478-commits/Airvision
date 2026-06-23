"use client";

import { useEffect, useState } from "react";
import AppLayout from "@/components/layout/AppLayout";
import IndiaMap from "@/components/maps/IndiaMap";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api } from "@/lib/api";

export default function TransportPage() {
  const [windData, setWindData] = useState<Awaited<ReturnType<typeof api.getWindVectors>>>([]);
  const [path, setPath] = useState<Awaited<ReturnType<typeof api.getTransportPath>> | null>(null);
  const [lat, setLat] = useState("28.6139");
  const [lon, setLon] = useState("77.2090");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getWindVectors(4)
      .then(setWindData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleSimulate = async () => {
    try {
      const result = await api.getTransportPath(parseFloat(lat), parseFloat(lon), 24);
      setPath(result);
    } catch (e) {
      console.error(e);
    }
  };

  const windPoints = windData.map((w) => ({
    latitude: w.latitude,
    longitude: w.longitude,
    value: w.speed,
    label: `Wind: ${w.speed} m/s @ ${w.direction}°`,
  }));

  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Transport Analysis</h1>
          <p className="text-muted-foreground mt-1">ERA5 wind vectors and pollution transport path estimation</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader><CardTitle>Simulate Transport</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Origin Latitude</Label>
                <Input value={lat} onChange={(e) => setLat(e.target.value)} />
              </div>
              <div className="space-y-2">
                <Label>Origin Longitude</Label>
                <Input value={lon} onChange={(e) => setLon(e.target.value)} />
              </div>
              <Button onClick={handleSimulate} className="w-full">Simulate 24h Path</Button>
              {path && (
                <div className="text-sm space-y-1 pt-2 border-t border-border">
                  <p>Origin: {path.origin_lat}, {path.origin_lon}</p>
                  <p>Duration: {path.estimated_hours}h</p>
                  <p>Path points: {path.path.length}</p>
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="lg:col-span-3">
            <CardHeader><CardTitle>Wind Speed & Transport Path</CardTitle></CardHeader>
            <CardContent>
              {loading ? <p className="text-muted-foreground">Loading wind data...</p> : (
                <IndiaMap
                  points={windPoints}
                  path={path?.path}
                  colorMode="value"
                  height="450px"
                />
              )}
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader><CardTitle>Wind Vector Data</CardTitle></CardHeader>
          <CardContent>
            <div className="overflow-x-auto max-h-64 overflow-y-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border text-muted-foreground">
                    <th className="text-left py-2 px-3">Lat</th>
                    <th className="text-left py-2 px-3">Lon</th>
                    <th className="text-left py-2 px-3">Speed (m/s)</th>
                    <th className="text-left py-2 px-3">Direction (°)</th>
                    <th className="text-left py-2 px-3">U</th>
                    <th className="text-left py-2 px-3">V</th>
                  </tr>
                </thead>
                <tbody>
                  {windData.slice(0, 50).map((w, i) => (
                    <tr key={i} className="border-b border-border/50">
                      <td className="py-1.5 px-3">{w.latitude}</td>
                      <td className="py-1.5 px-3">{w.longitude}</td>
                      <td className="py-1.5 px-3">{w.speed}</td>
                      <td className="py-1.5 px-3">{w.direction}</td>
                      <td className="py-1.5 px-3">{w.u_component}</td>
                      <td className="py-1.5 px-3">{w.v_component}</td>
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
