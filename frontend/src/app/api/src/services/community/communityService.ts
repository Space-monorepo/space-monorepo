import { API_URL } from "@/config";
import {
  CommunityListCommunities,
  Community,
  UpdateCommunity,
} from "@/app/api/src/types/community/Community";

export const fetchAllCommunities = async (
  token: string
): Promise<CommunityListCommunities> => {
  console.log("Fetching all communities with token:", token);
  const response = await fetch(`${API_URL}/communities`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const errorData = await response
      .json()
      .catch(() => ({ message: "Erro ao carregar as comunidades" }));
    throw new Error(errorData.message || "Erro ao carregar as comunidades");
  }

  return response.json();
};

export const fetchCommunityById = async (
  token: string,
  communityId: string
): Promise<Community> => {
  console.log(`Fetching community ${communityId} with token:`, token);
  const response = await fetch(`${API_URL}/communities/${communityId}`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const errorData = await response
      .json()
      .catch(() => ({ message: "Erro ao carregar a comunidade" }));
    throw new Error(errorData.message || "Erro ao carregar a comunidade");
  }

  return response.json();
};

export const updateCommunity = async (
  token: string,
  communityId: string,
  updateData: Partial<UpdateCommunity>
): Promise<Community> => {
  console.log(`Updating community ${communityId} with data:`, updateData);
  const response = await fetch(`${API_URL}/communities/${communityId}`, {
    method: "PATCH",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(updateData),
  });

  if (!response.ok) {
    const errorData = await response
      .json()
      .catch(() => ({ message: "Erro ao atualizar a comunidade" }));
    throw new Error(errorData.message || "Erro ao atualizar a comunidade");
  }

  return response.json();
};

export const deleteCommunity = async (
  token: string,
  communityId: string
): Promise<void> => {
  console.log(`Deleting community ${communityId}`);
  const response = await fetch(`${API_URL}/communities/${communityId}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const errorData = await response
      .json()
      .catch(() => ({ message: "Erro ao excluir a comunidade" }));
    throw new Error(errorData.message || "Erro ao excluir a comunidade");
  }
};
