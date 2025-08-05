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

// Função para buscar denúncias específicas do usuário
export const fetchUserComplaints = async (token: string, userData?: { id: string, username: string }): Promise<PostsListFeed> => {
  console.log('Fetching user complaints for:', userData || 'current user');
  
  try {
    let user: UserProfile;
    
    if (userData) {
      // Se userData foi fornecido, use-o diretamente
      user = { id: userData.id };
    } else {
      // Caso contrário, busca o perfil do usuário logado
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
      console.log('User profile loaded for complaints:', user);
    }

    // Tenta diferentes abordagens para buscar denúncias do usuário
    let response;
    
    // Tentativa 1: Endpoint específico para posts do usuário por tipo
    try {
      response = await fetch(`${API_URL}/users/me/posts?type=complaint`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
      });
      
      if (response.ok) {
        console.log('User complaints fetched via /users/me/posts');
        return response.json();
      }
    } catch (error) {
      console.log('First attempt failed:', error);
    }

    // Tentativa 2: Buscar no feed geral filtrando por user_id
    try {
      response = await fetch(`${API_URL}/posts/feed?type=complaint`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
      });
      
      if (response.ok) {
        const feedData = await response.json();
        console.log('Complaints fetched via feed, filtering by user');
        
        // Filtra apenas as denúncias do usuário atual
        const userComplaints = {
          ...feedData,
          items: (feedData.items || []).filter((post: PostResponse) => post.user?.id === user.id)
        };
        
        console.log('User complaints after filtering:', userComplaints.items?.length || 0);
        return userComplaints;
      }
    } catch (error) {
      console.log('Second attempt failed:', error);
    }

    // Tentativa 3: Se o usuário tem comunidades, busca nas comunidades dele
    if (user.communities && user.communities.length > 0) {
      try {
        const communityId = user.communities[0]?.id || user.communities[0]?._id;
        if (communityId) {
          response = await fetch(`${API_URL}/posts/feed?community_id=${communityId}&type=complaint`, {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
          });
          
          if (response.ok) {
            const feedData = await response.json();
            console.log('Complaints fetched via community, filtering by user');
            
            // Filtra apenas as denúncias do usuário atual
            const userComplaints = {
              ...feedData,
              items: (feedData.items || []).filter((post: PostResponse) => post.user?.id === user.id)
            };
            
            console.log('User complaints from community after filtering:', userComplaints.items?.length || 0);
            return userComplaints;
          }
        }
      } catch (error) {
        console.log('Third attempt failed:', error);
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
    console.error('Error fetching user complaints:', error);
    throw new Error('Erro ao carregar denúncias do usuário');
  }
};
