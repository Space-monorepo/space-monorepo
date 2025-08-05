import { useState, useEffect, useCallback } from "react";
import { Community, UpdateCommunity } from "../../types/community/Community";
import {
  fetchAllCommunities,
  updateCommunity,
  deleteCommunity,
} from "../../services/community/communityService";
import getTokenFromCookies from "../../controllers/getTokenFromCookies";

interface UseCommunityActionsOutput {
  communities: Community[];
  loading: boolean;
  error: Error | null;
  fetchCommunities: () => Promise<void>;
  updateCommunity: (
    communityId: string,
    updateData: Partial<UpdateCommunity>
  ) => Promise<Community>;
  deleteCommunity: (communityId: string) => Promise<void>;
}

const useCommunityActions = (): UseCommunityActionsOutput => {
  const [communities, setCommunities] = useState<Community[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);
  const token = getTokenFromCookies();

  const fetchCommunitiesCallback = useCallback(async () => {
    if (!token) {
      setError(new Error("Token não encontrado. Usuário não autenticado."));
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await fetchAllCommunities(token);
      setCommunities(data.items);
    } catch (err) {
      setError(err as Error);
      console.error("Erro ao buscar comunidades:", err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  const updateCommunityCallback = useCallback(
    async (
      communityId: string,
      updateData: Partial<UpdateCommunity>
    ): Promise<Community> => {
      if (!token) {
        throw new Error("Token não encontrado. Usuário não autenticado.");
      }

      setLoading(true);
      setError(null);
      try {
        const updatedCommunity = await updateCommunity(
          token,
          communityId,
          updateData
        );

        // Atualizar a lista local de comunidades
        setCommunities((prev) =>
          prev.map((community) =>
            community.id === communityId ? updatedCommunity : community
          )
        );

        return updatedCommunity;
      } catch (err) {
        setError(err as Error);
        console.error("Erro ao atualizar comunidade:", err);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [token]
  );

  const deleteCommunityCallback = useCallback(
    async (communityId: string): Promise<void> => {
      if (!token) {
        throw new Error("Token não encontrado. Usuário não autenticado.");
      }

      setLoading(true);
      setError(null);
      try {
        await deleteCommunity(token, communityId);

        // Remover a comunidade da lista local
        setCommunities((prev) =>
          prev.filter((community) => community.id !== communityId)
        );
      } catch (err) {
        setError(err as Error);
        console.error("Erro ao excluir comunidade:", err);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [token]
  );

  useEffect(() => {
    fetchCommunitiesCallback();
  }, [fetchCommunitiesCallback]);

  return {
    communities,
    loading,
    error,
    fetchCommunities: fetchCommunitiesCallback,
    updateCommunity: updateCommunityCallback,
    deleteCommunity: deleteCommunityCallback,
  };
};

export default useCommunityActions;
