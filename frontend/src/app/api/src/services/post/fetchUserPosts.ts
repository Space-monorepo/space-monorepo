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

    let response;
    
    // Tentativa 1: Endpoint específico para posts do usuário
    try {
      response = await fetch(`${API_URL}/users/me/posts`, { 
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
      });
      
      if (response.ok) {
        console.log('User posts fetched via /users/me/posts');
        return response.json();
      }
    } catch (error) {
      console.log('First attempt (me/posts) failed:', error);
    }

    // Tentativa 2: Buscar no feed geral filtrando por user_id
    try {
      response = await fetch(`${API_URL}/posts/feed`, { 
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
      console.log('Second attempt (feed) failed:', error);
    }

    // Tentativa 3: Se o usuário tem comunidades, busca nas comunidades dele
    if (user.communities && user.communities.length > 0) {
      try {
        const communityId = user.communities[0]?.id || user.communities[0]?._id;
        if (communityId) {
          response = await fetch(`${API_URL}/posts/feed?community_id=${communityId}`, { 
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
          });
          
          if (response.ok) {
            const feedData = await response.json();
            console.log('Posts fetched via community, filtering by user');
            
            // Filtra apenas os posts do usuário atual
            const userPosts = {
              ...feedData,
              items: (feedData.items || []).filter((post: PostResponse) => post.user?.id === user.id)
            };
            
            console.log('User posts from community after filtering:', userPosts.items?.length || 0);
            return userPosts;
          }
        }
      } catch (error) {
        console.log('Third attempt (community) failed:', error);
      }
    }

    // Se todas as tentativas falharem, retorna estrutura vazia
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