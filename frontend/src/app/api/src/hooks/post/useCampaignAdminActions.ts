import { useState } from 'react';
import getTokenFromCookies from '../../controllers/getTokenFromCookies';
import { updateCampaignStatus } from '../../services/post/campaignAdminService';

export function useCampaignAdminActions() {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<Error | null>(null);

    const approveCampaign = async (
        communityId: string,
        postId: string,
        subject: string,
        message: string
    ) => {
        setLoading(true);
        setError(null);
        try {
            const token = getTokenFromCookies();
            if (!token) throw new Error('Token não encontrado. Usuário não autenticado.');
            await updateCampaignStatus({
                token,
                communityId,
                postId,
                status_campaign: 'approved',
                subject,
                message,
            });
        } catch (err) {
            setError(err as Error);
            throw err;
        } finally {
            setLoading(false);
        }
    };

    const rejectCampaign = async (
        communityId: string,
        postId: string,
        subject: string,
        reason: string
    ) => {
        setLoading(true);
        setError(null);
        try {
            const token = getTokenFromCookies();
            if (!token) throw new Error('Token não encontrado. Usuário não autenticado.');
            await updateCampaignStatus({
                token,
                communityId,
                postId,
                status_campaign: 'rejected',
                subject,
                message: reason,
            });
        } catch (err) {
            setError(err as Error);
            throw err;
        } finally {
            setLoading(false);
        }
    };

    return { loading, error, approveCampaign, rejectCampaign };
}
