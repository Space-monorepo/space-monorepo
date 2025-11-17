import Cookies from 'js-cookie';
import { API_URL } from '@/config';

export interface ModerateReportPayload {
    report_id: string;
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

    async function updateComplaintStatus(
        communityId: string,
        postId: string,
        complaintStatus: string
    ) {
        const token = Cookies.get('token');
        if (!token) throw new Error('Token não encontrado');

        const response = await fetch(`${API_URL}/moderation/${communityId}/complaint/${postId}/status/${complaintStatus}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`,
            },
        });

        if (!response.ok) {
            const error = await response.text();
            throw new Error(error || 'Erro ao atualizar status da denúncia');
        }

        return response.json();
    }

    return { moderateReport, updateComplaintStatus };
}
