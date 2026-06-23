"use client";

import { useEffect, useState } from "react";
import AppLayout from "@/components/layout/AppLayout";
import { FeatureImportanceChart, PollutantContributionChart } from "@/components/charts/Charts";
import { StatCard } from "@/components/charts/Charts";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { api } from "@/lib/api";

export default function ExplainabilityPage() {
  const [explanation, setExplanation] = useState<Awaited<ReturnType<typeof api.getSHAPExplanation>> | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getSHAPExplanation()
      .then(setExplanation)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-64">
          <p className="text-muted-foreground">Computing SHAP explanations...</p>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Explainable AI</h1>
          <p className="text-muted-foreground mt-1">SHAP-based feature importance and pollutant contribution analysis</p>
        </div>

        {explanation && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <StatCard title="Base PM2.5 Value" value={explanation.base_value} subtitle="Model baseline" />
              <StatCard title="Predicted PM2.5" value={explanation.prediction} subtitle="After feature contributions" />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>SHAP Feature Importance</CardTitle>
                  <CardDescription>Global feature importance from XGBoost model</CardDescription>
                </CardHeader>
                <CardContent>
                  <FeatureImportanceChart data={explanation.feature_importance} />
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Pollutant Contribution</CardTitle>
                  <CardDescription>Relative contribution of each pollutant to PM2.5 prediction</CardDescription>
                </CardHeader>
                <CardContent>
                  <PollutantContributionChart data={explanation.pollutant_contributions} />
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader><CardTitle>SHAP Value Breakdown</CardTitle></CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-border text-muted-foreground">
                        <th className="text-left py-2 px-3">Feature</th>
                        <th className="text-left py-2 px-3">Global Importance</th>
                        <th className="text-left py-2 px-3">Impact Direction</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(explanation.feature_importance)
                        .sort(([, a], [, b]) => b - a)
                        .map(([feature, importance]) => (
                          <tr key={feature} className="border-b border-border/50">
                            <td className="py-2 px-3 font-medium">{feature}</td>
                            <td className="py-2 px-3">{importance.toFixed(4)}</td>
                            <td className="py-2 px-3">
                              <div className="w-full bg-secondary rounded-full h-2">
                                <div
                                  className="bg-primary h-2 rounded-full"
                                  style={{ width: `${Math.min(importance * 500, 100)}%` }}
                                />
                              </div>
                            </td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader><CardTitle>Model Architecture</CardTitle></CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  <div className="p-4 rounded-lg bg-secondary/50">
                    <h3 className="font-semibold mb-2">Current: XGBoost</h3>
                    <p className="text-muted-foreground">Gradient boosted trees for PM2.5 regression with SHAP TreeExplainer</p>
                  </div>
                  <div className="p-4 rounded-lg bg-secondary/50">
                    <h3 className="font-semibold mb-2">Future: CNN-LSTM</h3>
                    <p className="text-muted-foreground">Spatiotemporal deep learning for satellite image sequence analysis</p>
                  </div>
                  <div className="p-4 rounded-lg bg-secondary/50">
                    <h3 className="font-semibold mb-2">Inputs</h3>
                    <p className="text-muted-foreground">NO₂, SO₂, CO, O₃, weather, location, temporal features from Sentinel-5P & ERA5</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </AppLayout>
  );
}
