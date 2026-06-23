"use client";

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, Legend } from "recharts";
import { getAQIColor } from "@/lib/utils";

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  color?: string;
}

export function StatCard({ title, value, subtitle, color }: StatCardProps) {
  return (
    <div className="rounded-lg border bg-card p-6">
      <p className="text-sm text-muted-foreground">{title}</p>
      <p className="text-3xl font-bold mt-1" style={color ? { color } : undefined}>{value}</p>
      {subtitle && <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>}
    </div>
  );
}

export function AQICategoryChart({ data }: { data: Record<string, number> }) {
  const chartData = Object.entries(data).map(([name, value]) => ({ name, value }));
  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie data={chartData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label>
          {chartData.map((entry) => (
            <Cell key={entry.name} fill={getAQIColor(entry.name)} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}

export function AQITrendChart({ data }: { data: Array<{ date: string; avg_aqi: number; avg_pm25: number }> }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
        <XAxis dataKey="date" stroke="#94a3b8" tick={{ fontSize: 11 }} />
        <YAxis stroke="#94a3b8" />
        <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid #334155" }} />
        <Legend />
        <Line type="monotone" dataKey="avg_aqi" stroke="#0ea5e9" strokeWidth={2} name="Avg AQI" />
        <Line type="monotone" dataKey="avg_pm25" stroke="#f97316" strokeWidth={2} name="Avg PM2.5" />
      </LineChart>
    </ResponsiveContainer>
  );
}

export function FeatureImportanceChart({ data }: { data: Record<string, number> }) {
  const chartData = Object.entries(data)
    .map(([name, value]) => ({ name, value: Math.round(value * 1000) / 1000 }))
    .sort((a, b) => b.value - a.value);

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chartData} layout="vertical">
        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
        <XAxis type="number" stroke="#94a3b8" />
        <YAxis dataKey="name" type="category" stroke="#94a3b8" width={80} tick={{ fontSize: 11 }} />
        <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid #334155" }} />
        <Bar dataKey="value" fill="#0ea5e9" radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function TemporalHotspotChart({ data }: { data: Array<{ date: string; hotspot_count: number; avg_intensity: number }> }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
        <XAxis dataKey="date" stroke="#94a3b8" tick={{ fontSize: 11 }} />
        <YAxis stroke="#94a3b8" />
        <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid #334155" }} />
        <Legend />
        <Bar dataKey="hotspot_count" fill="#ef4444" name="Hotspot Count" />
        <Bar dataKey="avg_intensity" fill="#f97316" name="Avg Intensity" />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function PollutantContributionChart({ data }: { data: Record<string, number> }) {
  const chartData = Object.entries(data).map(([name, value]) => ({ name: name.toUpperCase(), value }));
  const colors = ["#0ea5e9", "#f97316", "#eab308", "#a855f7"];

  return (
    <ResponsiveContainer width="100%" height={250}>
      <PieChart>
        <Pie data={chartData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
          {chartData.map((_, i) => (
            <Cell key={i} fill={colors[i % colors.length]} />
          ))}
        </Pie>
        <Tooltip formatter={(v: number) => `${v}%`} />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}
