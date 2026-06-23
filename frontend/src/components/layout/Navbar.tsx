"use client";

import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Activity, Shield } from "lucide-react";

interface User {
  full_name: string;
  role: string;
}

export default function Navbar() {
  const pathname = usePathname();
  const [health, setHealth] = useState<string>("connecting");
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    // Fetch system health
    api.health()
      .then((data) => setHealth(data.status))
      .catch(() => setHealth("offline"));

    // Fetch user details if logged in
    api.getMe()
      .then(setUser)
      .catch(() => setUser(null));
  }, []);

  const getPageTitle = () => {
    const segments = pathname.split("/").filter(Boolean);
    if (segments.length === 0) return "Dashboard";
    const segment = segments[0];
    return segment.charAt(0).toUpperCase() + segment.slice(1).replace(/-/g, " ");
  };

  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-border bg-background/80 px-8 backdrop-blur-md">
      <div className="flex items-center gap-4">
        <h2 className="text-xl font-bold tracking-tight text-foreground">{getPageTitle()}</h2>
        <div className="flex items-center gap-1.5 rounded-full bg-secondary/80 px-2.5 py-1 text-xs">
          <Activity className={`h-3 w-3 ${health === "healthy" ? "text-green-500 animate-pulse" : "text-amber-500 animate-bounce"}`} />
          <span className="text-muted-foreground capitalize">System: {health}</span>
        </div>
      </div>

      {user && (
        <div className="flex items-center gap-3">
          <div className="text-right">
            <p className="text-sm font-semibold text-foreground">{user.full_name}</p>
            <div className="flex items-center justify-end gap-1 text-[10px] text-muted-foreground uppercase tracking-wider">
              <Shield className="h-3 w-3 text-primary" />
              <span>{user.role}</span>
            </div>
          </div>
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary/10 border border-primary/20 text-primary font-bold">
            {user.full_name.charAt(0).toUpperCase()}
          </div>
        </div>
      )}
    </header>
  );
}
