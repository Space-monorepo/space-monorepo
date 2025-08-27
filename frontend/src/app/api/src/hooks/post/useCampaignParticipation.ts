import { useState, useCallback } from 'react';
import getTokenFromCookies from '../../controllers/getTokenFromCookies';
import { API_URL } from '@/config';

export function useCampaignParticipation() {
    const [participating, setParticipating] = useState<{ [postId: string]: boolean }>({});
    const [loading, setLoading] = useState<{ [postId: string]: boolean }>({});

    const checkParticipation = useCallback(async (communityId: string, postId: string) => {
        const token = getTokenFromCookies();
        if (!token) return false;
        setLoading((prev) => ({ ...prev, [postId]: true }));
        try {
            const res = await fetch(`${API_URL}/posts/${communityId}/post/${postId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
            });
            if (!res.ok) return false;
            const data = await res.json();
            // Supondo que o backend retorna participantes e userId
            const userId = token && JSON.parse(atob(token.split('.')[1])).sub;
            let isParticipating = false;
            // Ajuste conforme resposta real do backend
            if (data.campaign_participants && Array.isArray(data.campaign_participants)) {
                isParticipating = data.campaign_participants.some((p: any) => p.user_id === userId);
            } else if (data.participants && Array.isArray(data.participants)) {
                isParticipating = data.participants.some((p: any) => p.user_id === userId);
            }
            setParticipating((prev) => ({ ...prev, [postId]: isParticipating }));
            return isParticipating;
        } catch {
            return false;
        } finally {
            setLoading((prev) => ({ ...prev, [postId]: false }));
        }
    }, []);

    const participate = useCallback(async (communityId: string, postId: string) => {
        const token = getTokenFromCookies();
        if (!token) throw new Error('Não autenticado');
        setLoading((prev) => ({ ...prev, [postId]: true }));
        try {
            const res = await fetch(`${API_URL}/posts/${communityId}/post/${postId}/campaign/participate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({ communityId, postId }),
            });
            if (!res.ok) throw new Error('Erro ao participar da campanha');
            setParticipating((prev) => ({ ...prev, [postId]: true }));
            return true;
        } finally {
            setLoading((prev) => ({ ...prev, [postId]: false }));
        }
    }, []);

    return { participating, loading, checkParticipation, participate };
}
