import { API_URL } from '@/config';
import { PostsListFeed, PostResponse } from '../../types/posts/Post';

// Interface para o usuário
interface UserProfile {
  id: string;
  communities?: Array<{
    id?: string;
    _id?: string;
    name?: string;
  }>;
}

// Função para buscar TODOS os posts do usuário
export const fetchUserPosts = async (token: string, userData?: { id: string, username: string }): Promise<PostsListFeed> => {
  console.log('Fetching ALL user posts for:', userData || 'current user');
  
  try {
    let user: UserProfile;
    
    if (userData) {
      user = { id: userData.id };
    } else {
      // Busca o perfil do usuário logado
      const userResponse = await fetch(`${API_URL}/users/me`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
      });

      if (!userResponse.ok) {
        throw new Error('Erro ao buscar perfil do usuário');
      }

      user = await userResponse.json();
      console.log('User profile loaded for posts:', user);
    }

    // Buscar do feed geral e filtrar por user_id (mesma rota que funciona na home)
    try {
      const response = await fetch(`${API_URL}/posts/feed?limit=9999`, { 
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
      });
      
      if (response.ok) {
        const feedData = await response.json();
        console.log('Posts fetched via feed, filtering by user');
        
        // Filtra apenas as publicações do usuário atual
        const userPosts = {
          ...feedData,
          items: (feedData.items || []).filter((post: PostResponse) => post.user?.id === user.id)
        };
        
        console.log('User posts after filtering:', userPosts.items?.length || 0);
        return userPosts;
      }
    } catch (error) {
      console.log('Feed fetch failed:', error);
    }

    // Se tudo falhar, retorna estrutura vazia
    console.log('All attempts failed, returning empty structure');
    return {
      current_limit: 10,
      current_offset: 0,
      has_more: false,
      items: [],
      total: 0
    };

  } catch (error) {
    console.error('Error fetching user posts:', error);
    throw new Error('Erro ao carregar publicações do usuário');
  }
};