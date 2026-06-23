import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

interface User {
  id: number;
  email: string;
  full_name: string;
  role: string;
}

export function useAuth(requireAuth = true) {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function checkAuth() {
      const token = localStorage.getItem("token");
      if (!token) {
        if (requireAuth) {
          router.push("/login");
        } else {
          setLoading(false);
        }
        return;
      }

      try {
        const userData = await api.getMe();
        setUser(userData);
      } catch (err) {
        localStorage.removeItem("token");
        if (requireAuth) {
          router.push("/login");
        }
      } finally {
        setLoading(false);
      }
    }

    checkAuth();
  }, [router, requireAuth]);

  const logout = () => {
    localStorage.removeItem("token");
    setUser(null);
    router.push("/login");
  };

  return { user, loading, logout, isAuthenticated: !!user };
}
