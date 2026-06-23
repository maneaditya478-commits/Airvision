const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ApiError {
  detail: string;
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const res = await fetch(`${API_URL}${endpoint}`, { ...options, headers });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || "Request failed");
  }
  return res.json();
}

export const api = {
  health: () => request<{ status: string; version: string }>("/health"),

  login: async (email: string, password: string) => {
    const form = new URLSearchParams({ username: email, password });
    const res = await fetch(`${API_URL}/api/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: form,
    });
    if (!res.ok) throw new Error("Invalid credentials");
    return res.json();
  },

  getMe: () => request<{ id: number; email: string; full_name: string; role: string }>("/api/v1/auth/me"),

  getDashboardSummary: () => request<{
    total_stations: number;
    avg_aqi: number;
    category_distribution: Record<string, number>;
    worst_city: string | null;
    best_city: string | null;
    last_updated: string | null;
  }>("/api/v1/dashboard/summary"),

  getAQITrends: (days = 30) => request<Array<{ date: string; avg_aqi: number; avg_pm25: number; station_count: number }>>(
    `/api/v1/dashboard/trends?days=${days}`
  ),

  getAQIMap: () => request<Array<{ latitude: number; longitude: number; value: number; category: string | null; label: string | null }>>(
    "/api/v1/dashboard/map"
  ),

  predictAQI: (data: Record<string, number | null>) =>
    request<{
      latitude: number; longitude: number; predicted_pm25: number;
      predicted_aqi: number; aqi_category: string; dominant_pollutant: string;
      model_version: string; shap_values: Record<string, number> | null;
    }>("/api/v1/prediction/predict", { method: "POST", body: JSON.stringify(data) }),

  getPredictionHeatmap: (gridSize = 2) =>
    request<Array<{ latitude: number; longitude: number; value: number; category: string | null }>>(
      `/api/v1/prediction/heatmap?grid_size=${gridSize}`
    ),

  getSHAPExplanation: (lat = 28.6, lon = 77.2) =>
    request<{
      feature_importance: Record<string, number>;
      pollutant_contributions: Record<string, number>;
      base_value: number; prediction: number;
    }>(`/api/v1/prediction/explain?latitude=${lat}&longitude=${lon}`),

  getHotspots: (hours = 72) =>
    request<Array<{
      id: number; cluster_id: number; timestamp: string;
      latitude: number; longitude: number; hcho_mean: number;
      hcho_max: number; point_count: number; intensity: string;
    }>>(`/api/v1/hotspots/?hours=${hours}`),

  detectHotspots: () =>
    request<Array<{
      id: number; cluster_id: number; timestamp: string;
      latitude: number; longitude: number; hcho_mean: number;
      hcho_max: number; point_count: number; intensity: string;
    }>>("/api/v1/hotspots/detect", { method: "POST" }),

  getHotspotTemporal: (days = 7) =>
    request<{ timeline: Array<{ date: string; hotspot_count: number; avg_intensity: number; max_intensity: number }> }>(
      `/api/v1/hotspots/temporal?days=${days}`
    ),

  getFirePoints: (hours = 48) =>
    request<Array<{ id: number; latitude: number; longitude: number; frp: number | null; confidence: number | null }>>(
      `/api/v1/fire/points?hours=${hours}`
    ),

  getFireCorrelation: () =>
    request<{
      fire_count: number; avg_hcho_near_fires: number;
      avg_hcho_away_from_fires: number; correlation_coefficient: number;
      hotspots_near_fires: number;
    }>("/api/v1/fire/correlation"),

  getWindVectors: (resolution = 3) =>
    request<Array<{ latitude: number; longitude: number; u_component: number; v_component: number; speed: number; direction: number }>>(
      `/api/v1/transport/wind?resolution=${resolution}`
    ),

  getTransportPath: (lat: number, lon: number, hours = 24) =>
    request<{ origin_lat: number; origin_lon: number; path: Array<{ lat: number; lon: number; hour: number }>; estimated_hours: number }>(
      `/api/v1/transport/path?lat=${lat}&lon=${lon}&hours=${hours}`
    ),

  getAdminStats: () =>
    request<Record<string, number>>("/api/v1/admin/stats"),

  getDatasets: () =>
    request<Array<{ id: number; name: string; source: string; status: string; record_count: number; created_at: string }>>(
      "/api/v1/admin/datasets"
    ),

  getModels: () =>
    request<Array<{ id: number; name: string; model_type: string; version: string; status: string; metrics: Record<string, number> | null }>>(
      "/api/v1/admin/models"
    ),

  retrainModel: () =>
    request<{ task_id: string; status: string }>("/api/v1/admin/models/retrain", { method: "POST" }),

  getTaskLogs: () =>
    request<Array<{ id: number; task_id: string; task_name: string; status: string; message: string | null; created_at: string }>>(
      "/api/v1/admin/monitoring/logs"
    ),
};
