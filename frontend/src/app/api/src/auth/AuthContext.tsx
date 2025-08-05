'use client';
import { createContext, useEffect, useState, ReactNode } from "react";
import Cookies from "js-cookie";
import { useRouter } from "next/navigation";
import { toast } from "react-toastify";
import { API_URL } from "@/config";
import { useBypassAuth } from "../hooks/useBypassAuth";
import { AuthContextType, User } from "./types";

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
});

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const bypass = useBypassAuth();

  useEffect(() => {
    const checkToken = async () => {
      if (bypass) {
        setLoading(false);
        return;
      }

      const token = Cookies.get("token");
      if (!token) {
        router.push("/login");
        return;
      }

      try {
        const res = await fetch(`${API_URL}/users/me`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (res.ok) {
          const data = await res.json();
          setUser({
            name: data.name,
            username: data.username,
            profile_image_url: data.profile_image_url,
          });
        } else {
          Cookies.remove("token");
          toast.warning("Sessão expirada. Faça login novamente.");
          router.push("/login");
        }
      } catch (err) {
        console.error("Erro ao verificar token:", err);
        Cookies.remove("token");
        toast.error("Erro de sessão. Faça login novamente.");
        router.push("/login");
      } finally {
        setLoading(false);
      }
    };

    checkToken();
  }, [router, bypass]);

  return (
    <AuthContext.Provider value={{ user, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;