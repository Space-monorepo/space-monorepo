import { useEffect, useState, useRef } from "react";
import { API_URL } from "@/config";
import getTokenFromCookies from "@/app/api/src/controllers/getTokenFromCookies";

/**
 * Hook que faz uma requisição direta a GET ${API_URL}/notifications a cada
 * `pollInterval` ms e devolve a contagem de notificações não-lidas.
 */
export function useUnreadNotificationsCount(pollInterval = 5000) {
    const [unreadCount, setUnreadCount] = useState<number>(0);
    const [loading, setLoading] = useState<boolean>(true);
    const pollingRef = useRef<number | null>(null);

    async function fetchUnread() {
        try {
            setLoading(true);
            const token = getTokenFromCookies();
            const res = await fetch(`${API_URL}/notifications`, {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    ...(token ? { Authorization: `Bearer ${token}` } : {}),
                },
            });
            if (!res.ok) {
                // mantém contagem atual se 404/401 etc.
                return;
            }
            const data = await res.json();
            if (Array.isArray(data)) {
                setUnreadCount(data.filter((n: any) => !n.read).length);
            } else if (typeof data === "object" && data !== null) {
                // tenta suportar resposta agrupada ou com campos de contagem
                if (Array.isArray((data as any).campaigns)) {
                    const groups = ["campaigns", "announcements", "connections", "interactions"];
                    let count = 0;
                    for (const g of groups) {
                        const items = (data as any)[g];
                        if (Array.isArray(items)) count += items.filter((i: any) => !i.read).length;
                    }
                    setUnreadCount(count);
                } else if (typeof (data as any).unread_count === "number") {
                    setUnreadCount((data as any).unread_count);
                } else if (typeof (data as any).unreadCount === "number") {
                    setUnreadCount((data as any).unreadCount);
                } else if (typeof (data as any).count === "number") {
                    setUnreadCount((data as any).count);
                }
            }
        } catch (err) {
            console.error("Erro ao buscar notificações:", err);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        fetchUnread();
        pollingRef.current = window.setInterval(fetchUnread, pollInterval);
        return () => {
            if (pollingRef.current) clearInterval(pollingRef.current);
        };
    }, [pollInterval]);

    return { unreadCount, loading, refetch: fetchUnread };
}


