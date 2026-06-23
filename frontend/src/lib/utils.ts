import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function getAQIColor(category: string | null | undefined): string {
  const colors: Record<string, string> = {
    Good: "#00E400",
    Satisfactory: "#92D050",
    Moderate: "#FFFF00",
    Poor: "#FF7E00",
    "Very Poor": "#FF0000",
    Severe: "#7E0023",
  };
  return colors[category || ""] || "#64748b";
}

export function getAQITextColor(category: string | null | undefined): string {
  if (category === "Moderate") return "#000";
  if (category === "Good" || category === "Satisfactory") return "#000";
  return "#fff";
}

export function formatDate(date: string): string {
  return new Date(date).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
}
