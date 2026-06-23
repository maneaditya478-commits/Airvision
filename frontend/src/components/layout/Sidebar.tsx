"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard, Brain, Flame, MapPin, Wind, BarChart3,
  Settings, LogOut, Satellite,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/map", label: "AQI Map", icon: MapPin },
  { href: "/prediction", label: "AQI Prediction", icon: Brain },
  { href: "/hotspots", label: "HCHO Hotspots", icon: MapPin },
  { href: "/fire", label: "Fire Correlation", icon: Flame },
  { href: "/transport", label: "Transport Analysis", icon: Wind },
  { href: "/forecasting", label: "Forecasting", icon: Brain },
  { href: "/explainability", label: "Explainable AI", icon: BarChart3 },
  { href: "/admin", label: "Admin Panel", icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();

  const handleLogout = () => {
    localStorage.removeItem("token");
    window.location.href = "/login";
  };

  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-64 border-r border-border bg-card">
      <div className="flex h-full flex-col">
        <div className="flex items-center gap-3 border-b border-border px-6 py-5">
          <Satellite className="h-8 w-8 text-primary" />
          <div>
            <h1 className="text-lg font-bold text-foreground">AirVision India</h1>
            <p className="text-xs text-muted-foreground">ISRO PS-3 Platform</p>
          </div>
        </div>

        <nav className="flex-1 space-y-1 px-3 py-4">
          {navItems.map(({ href, label, icon: Icon }) => (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium transition-colors",
                pathname === href
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-secondary hover:text-foreground"
              )}
            >
              <Icon className="h-4 w-4" />
              {label}
            </Link>
          ))}
        </nav>

        <div className="border-t border-border p-4">
          <Button variant="ghost" className="w-full justify-start gap-2" onClick={handleLogout}>
            <LogOut className="h-4 w-4" />
            Logout
          </Button>
        </div>
      </div>
    </aside>
  );
}
