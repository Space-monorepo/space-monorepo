import Cookies from 'js-cookie';
import { API_URL } from '@/config';

export interface ModerateReportPayload {
    moderator_id: string;
    vote: 'tolerate' | 'suspend';
}

export function useModerationActions() {
    async function moderateReport(
        communityId: string,
        reportId: string,
        payload: ModerateReportPayload
    ) {
        const token = Cookies.get('token');
        if (!token) throw new Error('Token não encontrado');

        const response = await fetch(`${API_URL}/moderation/${communityId}/moderate-report/${reportId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            const error = await response.text();
            throw new Error(error);
        }

        return response.json();
    }

    return { moderateReport };
}
