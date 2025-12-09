import { useState, useCallback } from 'react';
import { PostResponse } from '../../types/posts/Post';
import {
  fetchCommunityCampaigns,
  fetchCommunityReports,
  fetchCommunityAnnouncements,
  fetchCommunityPolls
} from '../../services/post/postService';
import getTokenFromCookies from '../../controllers/getTokenFromCookies';

interface UseCommunityPostsOutput {
  campaigns: PostResponse[];
  reports: PostResponse[];
  announcements: PostResponse[];
  polls: PostResponse[];
  loading: boolean;
  error: Error | null;
  fetchCommunityPosts: (communityId: string) => Promise<void>;
}

const useCommunityPosts = (): UseCommunityPostsOutput => {
  const [campaigns, setCampaigns] = useState<PostResponse[]>([]);
  const [reports, setReports] = useState<PostResponse[]>([]);
  const [announcements, setAnnouncements] = useState<PostResponse[]>([]);
  const [polls, setPolls] = useState<PostResponse[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchCommunityPosts = useCallback(async (communityId: string) => {
    const token = getTokenFromCookies();
    if (!token) {
      setError(new Error('Token não encontrado. Usuário não autenticado.'));
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      // Buscar posts por tipo específico
      console.log('Fetching community posts for:', communityId);

      const [campaignsData, reportsData, announcementsData, pollsData] = await Promise.all([
        fetchCommunityCampaigns(token, communityId),
        fetchCommunityReports(token, communityId),
        fetchCommunityAnnouncements(token, communityId),
        fetchCommunityPolls(token, communityId)
      ]);

      console.log('Campaigns received:', campaignsData.items?.length || 0);
      console.log('Reports received:', reportsData.items?.length || 0);
      console.log('Announcements received:', announcementsData.items?.length || 0);
      console.log('Polls received:', pollsData.items?.length || 0);

      // Verificar tipos dos posts recebidos
      if (campaignsData.items && campaignsData.items.length > 0) {
        console.log('First campaign type:', campaignsData.items[0].type_post);
      }
      if (reportsData.items && reportsData.items.length > 0) {
        console.log('First report type:', reportsData.items[0].type_post);
      }
      if (announcementsData.items && announcementsData.items.length > 0) {
        console.log('First announcement type:', announcementsData.items[0].type_post);
      }
      if (pollsData.items && pollsData.items.length > 0) {
        console.log('First poll type:', pollsData.items[0].type_post);
      }

      // Filtro adicional para garantir que apenas posts do tipo correto sejam incluídos
      const filteredCampaigns = (campaignsData.items || []).filter(post => post.type_post === 'campaign');
      const filteredReports = (reportsData.items || []).filter(post => post.type_post === 'complaint');
      const filteredAnnouncements = (announcementsData.items || []).filter(post => post.type_post === 'announcement');
      const filteredPolls = (pollsData.items || []).filter(post => post.type_post === 'poll');

      console.log('Filtered campaigns:', filteredCampaigns.length);
      console.log('Filtered reports:', filteredReports.length);
      console.log('Filtered announcements:', filteredAnnouncements.length);
      console.log('Filtered polls:', filteredPolls.length);

      setCampaigns(filteredCampaigns);
      setReports(filteredReports);
      setAnnouncements(filteredAnnouncements);
      setPolls(filteredPolls);

    } catch (err) {
      setError(err as Error);
      console.error("Erro ao buscar posts da comunidade:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    campaigns,
    reports,
    announcements,
    polls,
    loading,
    error,
    fetchCommunityPosts
  };
};

export default useCommunityPosts;
