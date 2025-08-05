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

// Função para buscar posts do usuário (todas as campanhas que ele criou)
export const fetchUserPosts = async (token: string): Promise<PostsListFeed> => {
  console.log('Fetching user posts');
  const response = await fetch(`${API_URL}/users/me/posts`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ 
      message: 'Erro ao carregar posts do usuário' 
    }));
    throw new Error(errorData.message || 'Erro ao carregar posts do usuário');
  }

  return response.json();
};

// Função para buscar campanhas específicas do usuário
export const fetchUserCampaigns = async (token: string): Promise<PostsListFeed> => {
  console.log('Fetching user campaigns');
  
  try {
    // Primeiro, busca o perfil do usuário para obter suas comunidades
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

    const user: UserProfile = await userResponse.json();
    console.log('User profile loaded for campaigns:', user);

    // Tenta diferentes abordagens para buscar campanhas do usuário
    let response;
    
    // Tentativa 1: Endpoint específico para posts do usuário por tipo
    try {
      response = await fetch(`${API_URL}/users/me/posts?type=campaign`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
      });
      
      if (response.ok) {
        console.log('User campaigns fetched via /users/me/posts');
        return response.json();
      }
    } catch (error) {
      console.log('First attempt failed:', error);
    }

    // Tentativa 2: Buscar no feed geral filtrando por user_id
    try {
      response = await fetch(`${API_URL}/posts/feed?type=campaign`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
      });
      
      if (response.ok) {
        const feedData = await response.json();
        console.log('Campaigns fetched via feed, filtering by user');
        
        // Filtra apenas as campanhas do usuário atual
        const userCampaigns = {
          ...feedData,
          items: (feedData.items || []).filter((post: PostResponse) => post.user?.id === user.id)
        };
        
        console.log('User campaigns after filtering:', userCampaigns.items?.length || 0);
        return userCampaigns;
      }
    } catch (error) {
      console.log('Second attempt failed:', error);
    }

    // Tentativa 3: Se o usuário tem comunidades, busca nas comunidades dele
    if (user.communities && user.communities.length > 0) {
      try {
        const communityId = user.communities[0]?.id || user.communities[0]?._id;
        if (communityId) {
          response = await fetch(`${API_URL}/posts/feed?community_id=${communityId}&type=campaign`, {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
          });
          
          if (response.ok) {
            const feedData = await response.json();
            console.log('Campaigns fetched via community, filtering by user');
            
            // Filtra apenas as campanhas do usuário atual
            const userCampaigns = {
              ...feedData,
              items: (feedData.items || []).filter((post: PostResponse) => post.user?.id === user.id)
            };
            
            console.log('User campaigns from community after filtering:', userCampaigns.items?.length || 0);
            return userCampaigns;
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
    console.error('Error fetching user campaigns:', error);
    throw new Error('Erro ao carregar campanhas do usuário');
  }
};

// Função para buscar posts em discussão (posts com mais atividade recente)
export const fetchTrendingPosts = async (token: string): Promise<PostsListFeed> => {
  console.log('Fetching trending posts');
  
  let response;
  try {
    response = await fetch(`${API_URL}/posts/trending`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
    });
  } catch {
    // Fallback para posts ordenados por atividade recente
    console.log('Trying fallback endpoint for trending posts');
    response = await fetch(`${API_URL}/posts/feed?sort=activity&limit=10`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
    });
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ 
      message: 'Erro ao carregar posts em discussão' 
    }));
    throw new Error(errorData.message || 'Erro ao carregar posts em discussão');
  }

  return response.json();
};

// Função para buscar eventos da agenda comunitária
export const fetchCommunityEvents = async (token: string): Promise<PostsListFeed> => {
  console.log('Fetching community events');
  
  let response;
  try {
    response = await fetch(`${API_URL}/events/community`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
    });
  } catch {
    // Fallback para posts do tipo anúncio que podem incluir eventos
    console.log('Trying fallback endpoint for community events');
    response = await fetch(`${API_URL}/posts/feed?type=announcement&limit=10`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
    });
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ 
      message: 'Erro ao carregar agenda comunitária' 
    }));
    throw new Error(errorData.message || 'Erro ao carregar agenda comunitária');
  }

  return response.json();
};
