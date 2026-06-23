"use client";

import { useEffect, useState } from "react";
import AppLayout from "@/components/layout/AppLayout";
import IndiaMap from "@/components/maps/IndiaMap";
import { StatCard } from "@/components/charts/Charts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";

export default function FirePage() {
  const [fires, setFires] = useState<Awaited<ReturnType<typeof api.getFirePoints>>>([]);
  const [correlation, setCorrelation] = useState<Awaited<ReturnType<typeof api.getFireCorrelation>> | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.getFirePoints(), api.getFireCorrelation()])
      .then(([f, c]) => { setFires(f); setCorrelation(c); })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const firePoints = fires.map((f) => ({
    latitude: f.latitude,
    longitude: f.longitude,
    value: f.frp || 0,
    label: `FRP: ${f.frp?.toFixed(1)} MW`,
  }));

  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Fire Correlation Module</h1>
          <p className="text-muted-foreground mt-1">NASA FIRMS fire data overlaid with HCHO concentration analysis</p>
        </div>

        {correlation && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard title="Active Fires" value={correlation.fire_count} subtitle="Last 72 hours" color="#ef4444" />
            <StatCard title="HCHO Near Fires" value={correlation.avg_hcho_near_fires} subtitle="µmol/m² avg" />
            <StatCard title="HCHO Away from Fires" value={correlation.avg_hcho_away_from_fires} subtitle="µmol/m² avg" />
            <StatCard title="Correlation (r)" value={correlation.correlation_coefficient} subtitle={`${correlation.hotspots_near_fires} hotspots near fires`} />
          </div>
        )}

        <Card>
          <CardHeader><CardTitle>NASA FIRMS Fire Points — India</CardTitle></CardHeader>
          <CardContent>
            {loading ? <p className="text-muted-foreground">Loading fire data...</p> : (
              <IndiaMap points={firePoints} colorMode="value" height="500px" />
            )}
          </CardContent>
        </Card>

        {correlation && (
          <Card>
            <CardHeader><CardTitle>Fire-HCHO Correlation Analysis</CardTitle></CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-3">
                  <h3 className="font-semibold">Findings</h3>
                  <ul className="space-y-2 text-sm text-muted-foreground">
                    <li>HCHO levels near active fires are {correlation.avg_hcho_near_fires > correlation.avg_hcho_away_from_fires ? "elevated" : "comparable"} compared to background</li>
                    <li>Correlation coefficient: {correlation.correlation_coefficient} (fire FRP vs nearby HCHO)</li>
                    <li>{correlation.hotspots_near_fires} HCHO hotspots detected within 50km of fire activity</li>
                  </ul>
                </div>
                <div className="space-y-3">
                  <h3 className="font-semibold">Data Sources</h3>
                  <ul className="space-y-2 text-sm text-muted-foreground">
                    <li>NASA FIRMS — Fire Radiative Power (FRP)</li>
                    <li>Sentinel-5P TROPOMI — HCHO column density</li>
                    <li>Spatial correlation radius: 50 km</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </AppLayout>
  );
}
