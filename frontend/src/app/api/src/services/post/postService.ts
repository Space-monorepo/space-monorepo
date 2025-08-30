import { API_URL } from '@/config';
import { PostsListFeed } from '../../types/posts/Post';

// Adicionar nova função para buscar posts de uma comunidade específica
export const fetchPostsByCommunity = async (token: string, communityId: string): Promise<PostsListFeed> => {
  console.log(`Fetching posts for community ${communityId} with token:`, token);
  const response = await fetch(`${API_URL}/posts/feed`, { // Ajustar endpoint conforme necessário
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ message: 'Erro ao carregar os posts da comunidade' }));
    throw new Error(errorData.message || 'Erro ao carregar os posts da comunidade');
  }

  return response.json();
};

// Função para buscar posts de um tipo específico de uma comunidade
export const fetchPostsByType = async (
  token: string, 
  communityId: string, 
  postType: string
): Promise<PostsListFeed> => {
  console.log(`Fetching ${postType} posts for community ${communityId}`);
  const url = `${API_URL}/posts/feed?community_id=${communityId}&type=${postType}`;
  console.log(`Request URL: ${url}`);
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ 
      message: `Erro ao carregar ${postType} da comunidade` 
    }));
    throw new Error(errorData.message || `Erro ao carregar ${postType} da comunidade`);
  }

  const data = await response.json();
  console.log(`${postType} posts received:`, data.items?.length || 0, 'items');
  console.log(`First ${postType} post type:`, data.items?.[0]?.type_post);
  
  return data;
};

// Funções específicas para cada tipo de post para administração
export const fetchCommunityReports = async (token: string, communityId: string): Promise<PostsListFeed> => {
  console.log('Calling fetchPostsByType with complaint type');
  return fetchPostsByType(token, communityId, 'complaint');
};

export const fetchCommunityCampaigns = async (token: string, communityId: string): Promise<PostsListFeed> => {
  console.log('Calling fetchPostsByType with campaign type');
  return fetchPostsByType(token, communityId, 'campaign');
};

export const fetchCommunityAnnouncements = async (token: string, communityId: string): Promise<PostsListFeed> => {
  console.log('Calling fetchPostsByType with announcement type');
  return fetchPostsByType(token, communityId, 'announcement');
};

// Função para buscar detalhes de uma campanha específica
export const fetchCampaignDetails = async (token: string, communityId: string, postId: string): Promise<any> => {
  console.log(`Fetching campaign details for post ${postId} in community ${communityId}`);
  const url = `${API_URL}/posts/${communityId}/post/${postId}`;
  console.log(`Request URL: ${url}`);
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ 
      message: 'Erro ao carregar detalhes da campanha' 
    }));
    throw new Error(errorData.message || 'Erro ao carregar detalhes da campanha');
  }

  const data = await response.json();
  console.log('Campaign details received:', data);
  
  return data;
};
