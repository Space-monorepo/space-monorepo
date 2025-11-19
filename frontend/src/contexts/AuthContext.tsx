"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import Cookies from "js-cookie";
import { useRouter } from "next/navigation";
import { getPermissions, canAccessRoute, UserRole, UserPermissions } from "@/lib/permissions";

interface User {
    id: string;
    name: string;
    email: string;
    picture?: string;
    role: UserRole;
    is_active: boolean;
}

interface AuthContextType {
    user: User | null;
    permissions: UserPermissions;
    loading: boolean;
    error: string | null;
    logout: () => void;
    canAccess: (route: string) => boolean;
    hasPermission: (permission: keyof UserPermissions) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [permissions, setPermissions] = useState<UserPermissions>(getPermissions("member"));
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const router = useRouter();

    useEffect(() => {
        const fetchUser = async () => {
            const token = Cookies.get("token");
            if (!token) {
                setLoading(false);
                return;
            }
            try {
                const res = await fetch("/api/users/me", {
                    headers: { Authorization: `Bearer ${token}` },
                });
                if (!res.ok) {
                    Cookies.remove("token");
                    setError("Sessão expirada. Faça login novamente.");
                    setTimeout(() => router.push("/login"), 0);
                    return;
                }
                const userData = await res.json();
                setUser(userData);
                setPermissions(getPermissions(userData.role as UserRole));
                setError(null);
            } catch (err) {
                Cookies.remove("token");
                setError("Erro ao buscar usuário");
                setTimeout(() => router.push("/login"), 0);
            } finally {
                setLoading(false);
            }
        };
        fetchUser();
    }, [router]);

    // Verificação periódica do token para logout automático
    useEffect(() => {
        const interval = setInterval(() => {
            const token = Cookies.get("token");
            if (!token) {
                logout();
            }
        }, 30000); // 30 segundos
        return () => clearInterval(interval);
    }, []);

    const logout = () => {
        Cookies.remove("token");
        setUser(null);
        setPermissions(getPermissions("member"));
        router.push("/login");
    };

    const canAccess = (route: string) => {
        if (!user) return false;
        return canAccessRoute(user.role, route);
    };

    const hasPermission = (permission: keyof UserPermissions) => {
        return permissions[permission];
    };

    const value: AuthContextType = {
        user,
        permissions,
        loading,
        error,
        logout,
        canAccess,
        hasPermission,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
}

export function usePermissions() {
    const { permissions, hasPermission } = useAuth();
    return { permissions, hasPermission };
}

export function useCanAccess() {
    const { canAccess } = useAuth();
    return canAccess;
}
