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
          let allComplaints: PostResponse[] = [];

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
                // Filtrar apenas denúncias (complaints)
                const complaints = posts.filter((post: PostResponse) => post.type_post === 'complaint');
                console.log(`Fetched ${complaints.length} complaints from community ${communityId}`);
                allComplaints = [...allComplaints, ...complaints];
              }
            } catch (error) {
              console.log(`Failed to fetch complaints from community ${communityId}:`, error);
            }
          }

          if (allComplaints.length > 0) {
            console.log(`Total complaints fetched: ${allComplaints.length}`);
            return {
              current_limit: allComplaints.length,
              current_offset: 0,
              has_more: false,
              items: allComplaints,
              total: allComplaints.length
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
        console.log('Complaints fetched via feed, filtering by user');
        
        // Filtra apenas as denúncias do usuário atual
        const userComplaints = {
          ...feedData,
          items: (feedData.items || []).filter((post: PostResponse) => post.user?.id === user.id && post.type_post === 'complaint')
        };
        
        console.log('User complaints after filtering:', userComplaints.items?.length || 0);
        return userComplaints;
      }
    } catch (error) {
      console.log('Fallback attempt failed:', error);
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
