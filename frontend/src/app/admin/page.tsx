"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import AppLayout from "@/components/layout/AppLayout";
import { StatCard } from "@/components/charts/Charts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import DataUpload from "@/components/admin/DataUpload";

export default function AdminPage() {
  const router = useRouter();
  const [stats, setStats] = useState<Record<string, number> | null>(null);
  const [datasets, setDatasets] = useState<Awaited<ReturnType<typeof api.getDatasets>>>([]);
  const [models, setModels] = useState<Awaited<ReturnType<typeof api.getModels>>>([]);
  const [logs, setLogs] = useState<Awaited<ReturnType<typeof api.getTaskLogs>>>([]);
  const [retraining, setRetraining] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) { router.push("/login"); return; }

    Promise.all([
      api.getAdminStats().catch(() => null),
      api.getDatasets().catch(() => []),
      api.getModels().catch(() => []),
      api.getTaskLogs().catch(() => []),
    ]).then(([s, d, m, l]) => {
      setStats(s);
      setDatasets(d);
      setModels(m);
      setLogs(l);
    });
  }, [router]);

  const handleRetrain = async () => {
    setRetraining(true);
    try {
      await api.retrainModel();
      alert("Model retraining task queued successfully");
    } catch (e) {
      alert("Retraining requires admin privileges");
    } finally {
      setRetraining(false);
    }
  };

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Admin Panel</h1>
            <p className="text-muted-foreground mt-1">Dataset management, model retraining, and system monitoring</p>
          </div>
          <Button onClick={handleRetrain} disabled={retraining}>
            {retraining ? "Queuing..." : "Retrain Model"}
          </Button>
        </div>

        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {Object.entries(stats).map(([key, value]) => (
              <StatCard key={key} title={key.replace(/_/g, " ")} value={value} />
            ))}
          </div>
        )}

        <DataUpload />

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader><CardTitle>ML Models</CardTitle></CardHeader>
            <CardContent>
              {models.length === 0 ? (
                <p className="text-muted-foreground text-sm">No models registered yet. Click Retrain to create one.</p>
              ) : (
                <div className="space-y-3">
                  {models.map((m) => (
                    <div key={m.id} className="p-3 rounded-lg bg-secondary/50 text-sm">
                      <p className="font-semibold">{m.name} v{m.version}</p>
                      <p className="text-muted-foreground">Type: {m.model_type} | Status: {m.status}</p>
                      {m.metrics && <p className="text-muted-foreground">R²: {m.metrics.test_r2?.toFixed(3)} | RMSE: {m.metrics.rmse?.toFixed(2)}</p>}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Datasets</CardTitle></CardHeader>
            <CardContent>
              {datasets.length === 0 ? (
                <p className="text-muted-foreground text-sm">No datasets uploaded yet.</p>
              ) : (
                <div className="space-y-3">
                  {datasets.map((d) => (
                    <div key={d.id} className="p-3 rounded-lg bg-secondary/50 text-sm">
                      <p className="font-semibold">{d.name}</p>
                      <p className="text-muted-foreground">Source: {d.source} | Status: {d.status} | Records: {d.record_count}</p>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader><CardTitle>Task Monitoring Logs</CardTitle></CardHeader>
          <CardContent>
            {logs.length === 0 ? (
              <p className="text-muted-foreground text-sm">No task logs yet.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border text-muted-foreground">
                      <th className="text-left py-2 px-3">Task</th>
                      <th className="text-left py-2 px-3">Status</th>
                      <th className="text-left py-2 px-3">Message</th>
                      <th className="text-left py-2 px-3">Time</th>
                    </tr>
                  </thead>
                  <tbody>
                    {logs.map((log) => (
                      <tr key={log.id} className="border-b border-border/50">
                        <td className="py-2 px-3">{log.task_name}</td>
                        <td className="py-2 px-3">
                          <span className={`px-2 py-0.5 rounded text-xs ${
                            log.status === "completed" ? "bg-green-500/20 text-green-400"
                            : log.status === "failed" ? "bg-red-500/20 text-red-400"
                            : "bg-blue-500/20 text-blue-400"
                          }`}>{log.status}</span>
                        </td>
                        <td className="py-2 px-3 text-muted-foreground">{log.message || "—"}</td>
                        <td className="py-2 px-3 text-muted-foreground">{new Date(log.created_at).toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
