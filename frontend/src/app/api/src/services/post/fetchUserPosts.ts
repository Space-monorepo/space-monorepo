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

    // Primeiro, buscar as comunidades do usuário
    try {
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
        console.log('User communities loaded:', communities.length);

        // Se temos comunidades, buscar posts de cada uma
        if (communities.length > 0) {
          let allPosts: PostResponse[] = [];

          // Buscar posts de cada comunidade
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
                console.log(`Fetched ${posts.length} posts from community ${communityId}`);
                allPosts = [...allPosts, ...posts];
              }
            } catch (error) {
              console.log(`Failed to fetch posts from community ${communityId}:`, error);
            }
          }

          if (allPosts.length > 0) {
            console.log(`Total posts fetched: ${allPosts.length}`);
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
    } catch (error) {
      console.log('Failed to fetch communities:', error);
    }

    // Fallback: Buscar no feed geral filtrando por user_id
    try {
      const response = await fetch(`${API_URL}/posts/feed`, { 
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
      console.log('Fallback attempt (feed) failed:', error);
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