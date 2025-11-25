import { useState } from "react";
import { API_URL } from "@/config";
import getTokenFromCookies from "@/app/api/src/controllers/getTokenFromCookies";

export type ReporterInfo = {
    id: string;
    name: string;
    profile_picture?: string | null;
    role?: string;
};

export type ReportListItem = {
    id: string;
    reporter: ReporterInfo;
    reason: string;
    description: string;
    created_at: string;
};

export type ReportType = "user" | "post" | "comment";

export function useReportersList() {
    const [loading, setLoading] = useState(false);
    const [reporters, setReporters] = useState<ReportListItem[]>([]);
    const [error, setError] = useState<string | null>(null);

    const fetchReporters = async (
        type: ReportType,
        communityId: string,
        targetId: string
    ) => {
        setLoading(true);
        setError(null);
        let url = "";
        if (type === "user") {
            url = `${API_URL}/moderation/${communityId}/list-all-member-reports/${targetId}`;
        } else if (type === "post") {
            url = `${API_URL}/moderation/${communityId}/list-all-post-reports/${targetId}`;
        } else if (type === "comment") {
            url = `${API_URL}/moderation/${communityId}/list-all-comment-reports/${targetId}`;
        }
        try {
            const token = getTokenFromCookies();
            const res = await fetch(url, {
                headers: { Authorization: `Bearer ${token}` },
            });
            if (!res.ok) throw new Error("Erro ao buscar reportes");
            const data = await res.json();
            setReporters(data.items || []);
        } catch (e: any) {
            setError(e.message || "Erro desconhecido");
            setReporters([]);
        } finally {
            setLoading(false);
        }
    };

    return { reporters, loading, error, fetchReporters };
}
