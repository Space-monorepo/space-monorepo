import { useState, useCallback } from 'react';
import { PostResponse } from '../../types/posts/Post';
import { fetchUserComplaints } from '../../services/post/fetchUserComplaints';
import getTokenFromCookies from '../../controllers/getTokenFromCookies';

interface UseUserComplaintsOutput {
  userComplaints: PostResponse[];
  loading: {
    complaints: boolean;
  };
  error: {
    complaints: Error | null;
  };
  fetchUserComplaints: (userData?: { id: string, username: string }) => Promise<void>;
  refreshComplaints: () => Promise<void>;
}

const useUserComplaints = (): UseUserComplaintsOutput => {
  const [userComplaints, setUserComplaints] = useState<PostResponse[]>([]);
  
  const [loading, setLoading] = useState({
    complaints: false,
  });
  
  const [error, setError] = useState({
    complaints: null as Error | null,
  });
  const fetchUserComplaintsCallback = useCallback(async (userData?: { id: string, username: string }) => {
    const token = getTokenFromCookies();
    if (!token) {
      setError(prev => ({ 
        ...prev, 
        complaints: new Error('Token não encontrado. Usuário não autenticado.') 
      }));
      return;
    }

    setLoading(prev => ({ ...prev, complaints: true }));
    setError(prev => ({ ...prev, complaints: null }));
    
    try {
      console.log('Fetching user complaints for:', userData);
      const complaintsData = await fetchUserComplaints(token, userData);
      
      console.log('User complaints received:', complaintsData.items?.length || 0);
      
      // Filtro para garantir que apenas denúncias sejam incluídas
      const filteredComplaints = (complaintsData.items || []).filter(post => post.type_post === 'complaint');
      
      console.log('Filtered user complaints:', filteredComplaints.length);
      setUserComplaints(filteredComplaints);
      
    } catch (err) {
      setError(prev => ({ ...prev, complaints: err as Error }));
      console.error("Erro ao buscar denúncias do usuário:", err);
    } finally {
      setLoading(prev => ({ ...prev, complaints: false }));
    }
  }, []);

  const refreshComplaints = useCallback(async () => {
    await fetchUserComplaintsCallback();
  }, [fetchUserComplaintsCallback]);

  return { 
    userComplaints,
    loading,
    error,
    fetchUserComplaints: fetchUserComplaintsCallback,
    refreshComplaints,
  };
};

export default useUserComplaints;
