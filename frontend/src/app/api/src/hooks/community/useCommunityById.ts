import { useState, useCallback } from 'react';
import { Community } from '../../types/community/Community';
import { fetchCommunityById } from '../../services/community/communityService';
import getTokenFromCookies from '../../controllers/getTokenFromCookies';

interface UseCommunityByIdOutput {
  community: Community | null;
  loading: boolean;
  error: Error | null;
  fetchCommunity: (communityId: string) => Promise<void>;
}

const useCommunityById = (): UseCommunityByIdOutput => {
  const [community, setCommunity] = useState<Community | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);
  const token = getTokenFromCookies();

  const fetchCommunityCallback = useCallback(async (communityId: string) => {
    if (!token) {
      setError(new Error('Token não encontrado. Usuário não autenticado.'));
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await fetchCommunityById(token, communityId);
      setCommunity(data);
    } catch (err) {
      setError(err as Error);
      console.error("Erro ao buscar comunidade:", err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  return { community, loading, error, fetchCommunity: fetchCommunityCallback };
};

export default useCommunityById;
