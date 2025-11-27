import { useState, useCallback } from "react";
import { PostResponse } from "../../types/posts/Post";
import {
  fetchCommunityCampaigns,
  fetchCommunityReports,
  fetchCommunityAnnouncements,
  fetchCommunityPolls,
} from "../../services/post/postService";
import getTokenFromCookies from "../../controllers/getTokenFromCookies";

interface UseCommunityPostsOutput {
  campaigns: PostResponse[];
  reports: PostResponse[];
  announcements: PostResponse[];
  polls: PostResponse[];
  loading: boolean;
  error: Error | null;
  fetchCommunityPosts: (communityId: string) => Promise<void>;
}

const useCommunityPosts = (
  isAdmin: boolean = false,
): UseCommunityPostsOutput => {
  const [campaigns, setCampaigns] = useState<PostResponse[]>([]);
  const [reports, setReports] = useState<PostResponse[]>([]);
  const [announcements, setAnnouncements] = useState<PostResponse[]>([]);
  const [polls, setPolls] = useState<PostResponse[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchCommunityPosts = useCallback(
    async (communityId: string) => {
      const token = getTokenFromCookies();
      if (!token) {
        setError(new Error("Token não encontrado. Usuário não autenticado."));
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);
      try {
        // Buscar posts por tipo específico
        console.log("Fetching community posts for:", communityId);

        let campaignsData = { items: [] as PostResponse[] };
        if (isAdmin) {
          campaignsData = await fetchCommunityCampaigns(token, communityId);
        }

        const [reportsData, announcementsData, pollsData] = await Promise.all([
          fetchCommunityReports(token, communityId),
          fetchCommunityAnnouncements(token, communityId),
          fetchCommunityPolls(token, communityId),
        ]);

        if (isAdmin) {
          console.log("Campaigns received:", campaignsData.items?.length || 0);
          if (campaignsData.items && campaignsData.items.length > 0) {
            console.log(
              "First campaign type:",
              campaignsData.items[0].type_post,
            );
          }
        }
        console.log("Reports received:", reportsData.items?.length || 0);
        console.log(
          "Announcements received:",
          announcementsData.items?.length || 0,
        );
        console.log("Polls received:", pollsData.items?.length || 0);

        // Filtro adicional para garantir que apenas posts do tipo correto sejam incluídos
        const filteredCampaigns = isAdmin
          ? (campaignsData.items || []).filter(
              (post) => post.type_post === "campaign",
            )
          : [];
        const filteredReports = (reportsData.items || []).filter(
          (post) => post.type_post === "complaint",
        );
        const filteredAnnouncements = (announcementsData.items || []).filter(
          (post) => post.type_post === "announcement",
        );
        const filteredPolls = (pollsData.items || []).filter(
          (post) => post.type_post === "poll",
        );

        if (isAdmin) {
          console.log("Filtered campaigns:", filteredCampaigns.length);
        }
        console.log("Filtered reports:", filteredReports.length);
        console.log("Filtered announcements:", filteredAnnouncements.length);
        console.log("Filtered polls:", filteredPolls.length);

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
    },
    [isAdmin],
  );

  return {
    campaigns,
    reports,
    announcements,
    polls,
    loading,
    error,
    fetchCommunityPosts,
  };
};

export default useCommunityPosts;
