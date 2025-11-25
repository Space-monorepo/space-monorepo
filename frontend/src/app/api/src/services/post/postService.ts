import { API_URL } from '@/config';
import { PostsListFeed } from '../../types/posts/Post';

// Adicionar nova função para buscar posts de uma comunidade específica
export const fetchPostsByCommunity = async (token: string, communityId: string, limit: number = 9999): Promise<PostsListFeed> => {
  const url = `${API_URL}/posts/feed?community_id=${communityId}&limit=${limit}`;
  const response = await fetch(url, {
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
  postType: string,
  limit: number = 9999
): Promise<PostsListFeed> => {
  const url = `${API_URL}/posts/feed?community_id=${communityId}&type=${postType}&limit=${limit}`;

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

  return data;
};

// Funções específicas para cada tipo de post para administração
export const fetchCommunityReports = async (token: string, communityId: string): Promise<PostsListFeed> => {
  // Buscar denúncias do endpoint de moderação, que retorna `ComplaintResponse`
  const url = `${API_URL}/moderation/${communityId}/list-all-complaints`;
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ message: 'Erro ao carregar denúncias da comunidade' }));
    throw new Error(errorData.message || 'Erro ao carregar denúncias da comunidade');
  }

  const data = await response.json();

  // Normalizar para PostsListFeed: cada item será o `post` com campos extras de complaint
  const normalized = {
    ...data,
    items: (data.items || []).map((c: any) => ({
      ...(c.post || {}),
      // campos adicionais provenientes do objeto de complaint
      status_complaint: c.status_complaint,
      level_complaint: c.level_complaint,
      confirmations_count: c.confirmations_count,
      // garantir que report_count reflita confirmações quando disponível
      report_count: c.confirmations_count ?? (c.post && c.post.report_count) ?? 0,
    }))
  };

  return normalized;
};

// Busca campanhas reais do endpoint específico de campanhas
export const fetchCommunityCampaigns = async (token: string, communityId: string): Promise<PostsListFeed> => {
  // Usar rota de administração que retorna o status específico da campanha
  const url = `${API_URL}/admin/${communityId}/post/list-all-campaigns`;
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ message: 'Erro ao carregar campanhas da comunidade' }));
    throw new Error(errorData.message || 'Erro ao carregar campanhas da comunidade');
  }

  const data = await response.json();
  const normalized = {
    ...data,
    items: (data.items || []).map((c: any) => ({
      ...(c.post || {}),
      status_campaign: c.status_campaign,
      target_participants: c.target_participants,
      current_participants: c.current_participants
    }))
  };
  return normalized;
};

export const fetchCommunityAnnouncements = async (token: string, communityId: string): Promise<PostsListFeed> => {
  return fetchPostsByType(token, communityId, 'announcement');
};

export const fetchCommunityPolls = async (token: string, communityId: string): Promise<PostsListFeed> => {
  return fetchPostsByType(token, communityId, 'poll');
};

// Função para buscar detalhes de uma campanha específica
export const fetchCampaignDetails = async (token: string, communityId: string, postId: string): Promise<any> => {
  const url = `${API_URL}/posts/${communityId}/post/${postId}`;

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

  return data;
};

// Função para votar em uma opção da enquete
export const voteOnPoll = async (communityId: string, pollOptionId: string, token?: string): Promise<any> => {
  const url = `${API_URL}/posts/${communityId}/post/poll-options/${pollOptionId}/vote`;
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const response = await fetch(url, {
    method: 'PATCH',
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ message: 'Erro ao votar na enquete' }));
    if (errorData.message === 'Poll vote already exists') {
      return { alreadyVoted: true };
    }
    throw new Error(errorData.message || 'Erro ao votar na enquete');
  }

  return response.json();
};

export async function confirmComplaint(communityId: string, postId: string, token?: string) {
  const res = await fetch(`${API_URL}/posts/${communityId}/complaint/${postId}/confirm`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
  if (!res.ok) throw new Error('Erro ao confirmar problema');
  return await res.json();
}
