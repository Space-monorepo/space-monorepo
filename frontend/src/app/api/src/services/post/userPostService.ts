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
  
  try {
    // Primeiro, buscar o perfil do usuário
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
    console.log('User profile loaded for posts:', user);

    // Buscar as comunidades do usuário
    const communitiesResponse = await fetch(`${API_URL}/communities/user/${user.id}/communities`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
    });

    if (communitiesResponse.ok) {
      const communitiesData = await communitiesResponse.json();
      const communities = communitiesData.items || [];
      
      if (communities.length > 0) {
        let allPosts: PostResponse[] = [];
        
        for (const community of communities) {
          const communityId = community.id || community._id;
          if (!communityId) continue;

          try {
            const postsResponse = await fetch(
              `${API_URL}/posts/${communityId}/user/${user.id}/list-posts?limit=100`,
              {
                method: 'GET',
                headers: {
                  'Authorization': `Bearer ${token}`,
                  'Content-Type': 'application/json'
                },
              }
            );

            if (postsResponse.ok) {
              const postsData = await postsResponse.json();
              const posts = postsData.items || [];
              allPosts = [...allPosts, ...posts];
            }
          } catch (error) {
            console.log(`Failed to fetch posts from community ${communityId}:`, error);
          }
        }

        if (allPosts.length > 0) {
          return {
            current_limit: allPosts.length,
            current_offset: 0,
            has_more: false,
            items: allPosts,
            total: allPosts.length
          };
        }
      }
    }

    // Fallback: Buscar no feed filtrando por usuário
    const feedResponse = await fetch(`${API_URL}/posts/feed`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
    });

    if (feedResponse.ok) {
      const feedData = await feedResponse.json();
      const userPosts = {
        ...feedData,
        items: (feedData.items || []).filter((post: PostResponse) => post.user?.id === user.id)
      };
      return userPosts;
    }

    throw new Error('Erro ao carregar posts do usuário');
  } catch (error) {
    console.error('Error fetching user posts:', error);
    throw new Error('Erro ao carregar posts do usuário');
  }
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

    // Buscar as comunidades do usuário
    const communitiesResponse = await fetch(`${API_URL}/communities/user/${user.id}/communities`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
    });

    if (communitiesResponse.ok) {
      const communitiesData = await communitiesResponse.json();
      const communities = communitiesData.items || [];
      
      if (communities.length > 0) {
        let allCampaigns: PostResponse[] = [];
        
        for (const community of communities) {
          const communityId = community.id || community._id;
          if (!communityId) continue;

          try {
            const postsResponse = await fetch(
              `${API_URL}/posts/${communityId}/user/${user.id}/list-posts?limit=100`,
              {
                method: 'GET',
                headers: {
                  'Authorization': `Bearer ${token}`,
                  'Content-Type': 'application/json'
                },
              }
            );

            if (postsResponse.ok) {
              const postsData = await postsResponse.json();
              const posts = postsData.items || [];
              const campaigns = posts.filter((post: PostResponse) => post.type_post === 'campaign');
              allCampaigns = [...allCampaigns, ...campaigns];
            }
          } catch (error) {
            console.log(`Failed to fetch campaigns from community ${communityId}:`, error);
          }
        }

        if (allCampaigns.length > 0) {
          return {
            current_limit: allCampaigns.length,
            current_offset: 0,
            has_more: false,
            items: allCampaigns,
            total: allCampaigns.length
          };
        }
      }
    }

    // Fallback: Buscar no feed filtrando por usuário
    const feedResponse = await fetch(`${API_URL}/posts/feed`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
    });

    if (feedResponse.ok) {
      const feedData = await feedResponse.json();
      const userCampaigns = {
        ...feedData,
        items: (feedData.items || []).filter((post: PostResponse) => post.user?.id === user.id && post.type_post === 'campaign')
      };
      return userCampaigns;
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
    response = await fetch(`${API_URL}/posts/feed?sort=activity&limit=50`, {
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
    response = await fetch(`${API_URL}/posts/feed?type=announcement&limit=50`, {
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
