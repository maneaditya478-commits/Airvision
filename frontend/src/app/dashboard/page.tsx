"use client";

import { useEffect, useState } from "react";
import AppLayout from "@/components/layout/AppLayout";
import IndiaMap from "@/components/maps/IndiaMap";
import { StatCard, AQICategoryChart, AQITrendChart } from "@/components/charts/Charts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { getAQIColor } from "@/lib/utils";

export default function DashboardPage() {
  const [summary, setSummary] = useState<Awaited<ReturnType<typeof api.getDashboardSummary>> | null>(null);
  const [trends, setTrends] = useState<Awaited<ReturnType<typeof api.getAQITrends>>>([]);
  const [mapPoints, setMapPoints] = useState<Awaited<ReturnType<typeof api.getAQIMap>>>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.getDashboardSummary(), api.getAQITrends(30), api.getAQIMap()])
      .then(([s, t, m]) => { setSummary(s); setTrends(t); setMapPoints(m); })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-64">
          <p className="text-muted-foreground">Loading dashboard...</p>
        </div>
      </AppLayout>
    );
  }

  const avgCategory = summary && summary.averageAQI <= 50 ? "Good"
    : summary && summary.averageAQI <= 100 ? "Satisfactory"
    : summary && summary.averageAQI <= 200 ? "Moderate" : "Poor";

  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Air Quality Dashboard</h1>
          <p className="text-muted-foreground mt-1">Real-time AQI monitoring across India using CPCB & Sentinel-5P data</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard title="Average AQI" value={summary?.averageAQI ?? 0} color={getAQIColor(avgCategory)} subtitle={avgCategory} />
          <StatCard title="Monitoring Stations" value={summary?.stationCount ?? 0} subtitle="CPCB ground stations" />
          <StatCard title="Worst City" value={summary?.worstCity ?? "N/A"} subtitle="Highest average AQI" color="#ef4444" />
          <StatCard title="Best City" value={summary?.bestCity ?? "N/A"} subtitle="Lowest average AQI" color="#22c55e" />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader><CardTitle>AQI Category Distribution</CardTitle></CardHeader>
            <CardContent>
              {summary && <AQICategoryChart data={summary.categoryDistribution} />}
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>30-Day AQI Trend</CardTitle></CardHeader>
            <CardContent>
              <AQITrendChart data={trends} />
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader><CardTitle>Current AQI Map — India</CardTitle></CardHeader>
          <CardContent>
            <IndiaMap points={mapPoints} colorMode="aqi" height="500px" />
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
