"use client";

import { useState } from "react";
import { Upload, FileText, CheckCircle, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";

const categories = [
  { id: "cpcb", name: "CPCB Ground AQI Data", endpoint: "/api/upload/cpcb" },
  { id: "sentinel", name: "Sentinel-5P Satellite Data", endpoint: "/api/upload/sentinel" },
  { id: "weather", name: "ERA5 Weather Data", endpoint: "/api/upload/weather" },
  { id: "fire", name: "NASA FIRMS Fire Data", endpoint: "/api/upload/fire" },
];

export default function DataUpload() {
  const [selectedCategory, setSelectedCategory] = useState("cpcb");
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<{ status: string; message: string; count?: number } | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setResult(null);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);

    const endpoint = categories.find((c) => c.id === selectedCategory)?.endpoint;
    const token = localStorage.getItem("token");

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}${endpoint}`, {
        method: "POST",
        headers: {
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: formData,
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: "Upload failed" }));
        throw new Error(errorData.detail || "Upload failed");
      }

      const responseData = await res.json();
      setResult({
        status: "success",
        message: `Successfully uploaded ${file.name}!`,
        count: responseData.records_ingested,
      });
      setFile(null);
    } catch (err: any) {
      setResult({
        status: "error",
        message: err.message || "An error occurred during upload.",
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="rounded-lg border border-border bg-card p-6 space-y-6">
      <div className="space-y-2">
        <h3 className="text-lg font-bold text-foreground">Ingest Datasets</h3>
        <p className="text-sm text-muted-foreground">Upload CSV or JSON files to feed the AirVision monitoring pipeline.</p>
      </div>

      <form onSubmit={handleUpload} className="space-y-4">
        <div className="space-y-1.5">
          <label className="text-sm font-semibold text-muted-foreground">Ingestion Category</label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {categories.map((c) => (
              <button
                type="button"
                key={c.id}
                onClick={() => { setSelectedCategory(c.id); setResult(null); }}
                className={`rounded-md border p-2 text-xs font-medium transition-colors text-center ${
                  selectedCategory === c.id
                    ? "border-primary bg-primary/10 text-primary"
                    : "border-border hover:bg-secondary text-muted-foreground"
                }`}
              >
                {c.name}
              </button>
            ))}
          </div>
        </div>

        <div className="flex justify-center rounded-lg border border-dashed border-border px-6 py-10 transition-colors hover:border-muted-foreground/30">
          <div className="text-center space-y-4">
            <Upload className="mx-auto h-10 w-10 text-muted-foreground" />
            <div className="text-sm text-muted-foreground">
              <label className="relative cursor-pointer rounded-md font-semibold text-primary hover:text-primary/80 focus-within:outline-none">
                <span>Select file to upload</span>
                <input
                  type="file"
                  accept=".csv,.json"
                  onChange={handleFileChange}
                  className="sr-only"
                  required
                />
              </label>
            </div>
            {file && (
              <div className="flex items-center justify-center gap-1.5 text-xs text-foreground font-semibold bg-secondary/80 px-3 py-1.5 rounded-full">
                <FileText className="h-3.5 w-3.5 text-primary" />
                <span>{file.name}</span>
                <span className="text-[10px] text-muted-foreground">({(file.size / 1024).toFixed(1)} KB)</span>
              </div>
            )}
          </div>
        </div>

        {result && (
          <div className={`flex items-start gap-3 rounded-lg p-4 border text-sm ${
            result.status === "success"
              ? "bg-green-500/10 border-green-500/20 text-green-400"
              : "bg-destructive/10 border-destructive/20 text-destructive-foreground"
          }`}>
            {result.status === "success" ? (
              <CheckCircle className="h-5 w-5 shrink-0" />
            ) : (
              <AlertTriangle className="h-5 w-5 shrink-0 text-destructive" />
            )}
            <div>
              <p className="font-semibold">{result.status === "success" ? "Success" : "Upload Error"}</p>
              <p className="mt-0.5">{result.message}</p>
              {result.count !== undefined && (
                <p className="mt-1 text-xs font-semibold uppercase tracking-wider">Ingested: {result.count} records</p>
              )}
            </div>
          </div>
        )}

        <Button type="submit" disabled={!file || uploading} className="w-full">
          {uploading ? "Ingesting dataset..." : "Upload & Process File"}
        </Button>
      </form>
    </div>
  );
}
