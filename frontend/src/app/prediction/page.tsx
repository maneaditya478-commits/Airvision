"use client";

import { useEffect, useState } from "react";
import AppLayout from "@/components/layout/AppLayout";
import IndiaMap from "@/components/maps/IndiaMap";
import { StatCard } from "@/components/charts/Charts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api } from "@/lib/api";
import { getAQIColor } from "@/lib/utils";

export default function PredictionPage() {
  const [heatmap, setHeatmap] = useState<Awaited<ReturnType<typeof api.getPredictionHeatmap>>>([]);
  const [prediction, setPrediction] = useState<Awaited<ReturnType<typeof api.predictAQI>> | null>(null);
  const [lat, setLat] = useState("28.6139");
  const [lon, setLon] = useState("77.2090");
  const [loading, setLoading] = useState(false);
  const [mapLoading, setMapLoading] = useState(true);

  useEffect(() => {
    api.getPredictionHeatmap(3)
      .then(setHeatmap)
      .catch(console.error)
      .finally(() => setMapLoading(false));
  }, []);

  const handlePredict = async () => {
    setLoading(true);
    try {
      const result = await api.predictAQI({
        latitude: parseFloat(lat),
        longitude: parseFloat(lon),
      });
      setPrediction(result);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">AQI Prediction Module</h1>
          <p className="text-muted-foreground mt-1">XGBoost-based PM2.5 prediction with CPCB AQI calculation</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="lg:col-span-1">
            <CardHeader><CardTitle>Predict at Location</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Latitude</Label>
                <Input value={lat} onChange={(e) => setLat(e.target.value)} />
              </div>
              <div className="space-y-2">
                <Label>Longitude</Label>
                <Input value={lon} onChange={(e) => setLon(e.target.value)} />
              </div>
              <Button onClick={handlePredict} disabled={loading} className="w-full">
                {loading ? "Predicting..." : "Predict AQI"}
              </Button>

              {prediction && (
                <div className="space-y-3 pt-4 border-t border-border">
                  <StatCard title="Predicted PM2.5" value={`${prediction.predicted_pm25} µg/m³`} />
                  <StatCard
                    title="Predicted AQI"
                    value={prediction.predicted_aqi}
                    color={getAQIColor(prediction.aqi_category)}
                    subtitle={prediction.aqi_category}
                  />
                  <p className="text-xs text-muted-foreground">Model: {prediction.model_version}</p>
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="lg:col-span-2">
            <CardHeader><CardTitle>AQI Prediction Heatmap</CardTitle></CardHeader>
            <CardContent>
              {mapLoading ? (
                <p className="text-muted-foreground">Generating heatmap...</p>
              ) : (
                <IndiaMap points={heatmap} colorMode="value" height="450px" zoom={5} />
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </AppLayout>
  );
}
