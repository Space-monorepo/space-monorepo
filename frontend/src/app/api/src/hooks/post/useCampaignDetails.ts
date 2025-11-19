import { useState, useCallback } from 'react';
import { fetchCampaignDetails } from '../../services/post/postService';
import getTokenFromCookies from '../../controllers/getTokenFromCookies';

interface UseCampaignDetailsOutput {
    campaignDetails: any | null;
    loading: boolean;
    error: Error | null;
    fetchCampaignDetailsById: (communityId: string, postId: string) => Promise<void>;
    clearDetails: () => void;
}

const useCampaignDetails = (): UseCampaignDetailsOutput => {
    const [campaignDetails, setCampaignDetails] = useState<any | null>(null);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<Error | null>(null);

    const fetchCampaignDetailsById = useCallback(async (communityId: string, postId: string) => {
        const token = getTokenFromCookies();
        if (!token) {
            setError(new Error('Token não encontrado. Usuário não autenticado.'));
            setLoading(false);
            return;
        }

        setLoading(true);
        setError(null);

        try {
            console.log('Fetching campaign details for:', { communityId, postId });

            const details = await fetchCampaignDetails(token, communityId, postId);

            console.log('Campaign details received:', details);
            setCampaignDetails(details);

        } catch (err) {
            setError(err as Error);
            console.error("Erro ao buscar detalhes da campanha:", err);
        } finally {
            setLoading(false);
        }
    }, []);

    const clearDetails = useCallback(() => {
        setCampaignDetails(null);
        setError(null);
    }, []);

    return {
        campaignDetails,
        loading,
        error,
        fetchCampaignDetailsById,
        clearDetails
    };
};

export default useCampaignDetails;
