import { useState, useCallback } from 'react';
import { PostResponse } from '../../types/posts/Post';
import { fetchUserCampaigns } from '../../services/post/userPostService';
import getTokenFromCookies from '../../controllers/getTokenFromCookies';

interface UseRightSidebarDataOutput {
  userCampaigns: PostResponse[];
  loading: {
    campaigns: boolean;
  };
  error: {
    campaigns: Error | null;
  };
  fetchUserCampaigns: () => Promise<void>;
  refreshCampaigns: () => Promise<void>;
}

const useRightSidebarData = (): UseRightSidebarDataOutput => {
  const [userCampaigns, setUserCampaigns] = useState<PostResponse[]>([]);
  
  const [loading, setLoading] = useState({
    campaigns: false,
  });
  
  const [error, setError] = useState({
    campaigns: null as Error | null,
  });

  const fetchUserCampaignsCallback = useCallback(async () => {
    const token = getTokenFromCookies();
    if (!token) {
      setError(prev => ({ 
        ...prev, 
        campaigns: new Error('Token não encontrado. Usuário não autenticado.') 
      }));
      return;
    }

    setLoading(prev => ({ ...prev, campaigns: true }));
    setError(prev => ({ ...prev, campaigns: null }));
    
    try {
      console.log('Fetching user campaigns');
      const campaignsData = await fetchUserCampaigns(token);
      
      console.log('User campaigns received:', campaignsData.items?.length || 0);
      
      // Filtro para garantir que apenas campanhas sejam incluídas
      const filteredCampaigns = (campaignsData.items || []).filter(post => post.type_post === 'campaign');
      
      console.log('Filtered user campaigns:', filteredCampaigns.length);
      setUserCampaigns(filteredCampaigns);
      
    } catch (err) {
      setError(prev => ({ ...prev, campaigns: err as Error }));
      console.error("Erro ao buscar campanhas do usuário:", err);
    } finally {
      setLoading(prev => ({ ...prev, campaigns: false }));
    }
  }, []);

  const refreshCampaigns = useCallback(async () => {
    await fetchUserCampaignsCallback();
  }, [fetchUserCampaignsCallback]);

  return { 
    userCampaigns,
    loading,
    error,
    fetchUserCampaigns: fetchUserCampaignsCallback,
    refreshCampaigns
  };
};

export default useRightSidebarData;
