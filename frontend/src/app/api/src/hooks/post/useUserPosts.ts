import { useState, useCallback } from 'react';
import { PostResponse } from '../../types/posts/Post';
import { fetchUserPosts } from '../../services/post/fetchUserPosts'; 
import getTokenFromCookies from '../../controllers/getTokenFromCookies';

interface UseUserPostsOutput {
  userPosts: PostResponse[];
  loading: {
    posts: boolean;
  };
  error: {
    posts: Error | null;
  };
  fetchUserPosts: (userData?: { id: string, username: string }) => Promise<void>;
  refreshPosts: () => Promise<void>;
}

const useUserPosts = (): UseUserPostsOutput => {
  const [userPosts, setUserPosts] = useState<PostResponse[]>([]);
  const [loading, setLoading] = useState({
    posts: false,
  });
  const [error, setError] = useState({
    posts: null as Error | null,
  });
  
  const fetchUserPostsCallback = useCallback(async (userData?: { id: string, username: string }) => {
    const token = getTokenFromCookies();
    if (!token) {
      setError(prev => ({ 
        ...prev, 
        posts: new Error('Token não encontrado. Usuário não autenticado.') 
      }));
      return;
    }

    setLoading(prev => ({ ...prev, posts: true }));
    setError(prev => ({ ...prev, posts: null }));
    
    try {
      console.log('Fetching user posts (hook)...');
      const postsData = await fetchUserPosts(token, userData); 
      
      console.log('User posts received (hook):', postsData.items?.length || 0);
      
      // Salva TODOS os posts retornados
      setUserPosts(postsData.items || []);

    } catch (err) {
      setError(prev => ({ ...prev, posts: err as Error }));
      console.error("Erro ao buscar publicações do usuário (hook):", err);
    } finally {
      setLoading(prev => ({ ...prev, posts: false }));
    }
  }, []);

  const refreshPosts = useCallback(async () => {
    await fetchUserPostsCallback();
  }, [fetchUserPostsCallback]);

  return { 
    userPosts,
    loading,
    error,
    fetchUserPosts: fetchUserPostsCallback,
    refreshPosts,
  };
};

export default useUserPosts;