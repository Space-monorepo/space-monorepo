import { API_URL } from "@/config";

export interface ImportMembersPayload {
  emails: string[];
}

export interface MemberRoleUpdatePayload {
  new_role: "admin" | "moderator" | "member";
}

export interface CommunityMemberResponse {
  id: string;
  user_id: string;
  community_id: string;
  user: {
    id: string;
    email: string;
    name: string;
    profile_image_url?: string;
    reputation_level: number;
    status: string;
    created_at: string;
    updated_at: string;
  };
  community: {
    id: string;
    name: string;
  };
  role: "admin" | "moderator" | "member";
  status_participation: "active" | "suspended" | "banned";
  reputation: number;
  entered_in: string;
}

export interface PaginationResponse<T> {
  items: T[];
  total: number;
  has_more: boolean;
  current_offset: number;
  current_limit: number;
}

// Importar usuários para a comunidade usando emails
export const importUsersToCommunitya = async (
  token: string,
  communityId: string,
  emails: string[],
): Promise<CommunityMemberResponse[]> => {
  console.log("Importing users to community:", { communityId, emails });

  const response = await fetch(
    `${API_URL}/admin/${communityId}/users/add-users`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        emails: emails,
      }),
    },
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({
      message: "Erro ao importar usuários",
    }));
    throw new Error(errorData.message || "Erro ao importar usuários");
  }

  return response.json();
};

// Listar todos os membros da comunidade
export const listAllMembersFromCommunity = async (
  token: string,
  communityId: string,
  params?: {
    offset?: number;
    limit?: number;
    name?: string;
  },
): Promise<PaginationResponse<CommunityMemberResponse>> => {
  console.log("Listing community members:", { communityId, params });

  const searchParams = new URLSearchParams();
  if (params?.offset) searchParams.append("offset", params.offset.toString());
  if (params?.limit) searchParams.append("limit", params.limit.toString());
  if (params?.name) searchParams.append("name", params.name);

  const url = `${API_URL}/communities/${communityId}/members${searchParams.toString() ? `?${searchParams.toString()}` : ""}`;

  const response = await fetch(url, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({
      message: "Erro ao listar membros",
    }));
    throw new Error(errorData.message || "Erro ao listar membros");
  }

  return response.json();
};

// Atualizar role de um membro específico
export const updateMemberRole = async (
  id: string,
  token: string,
  communityId: string,
  memberId: string,
  newRole: "admin" | "moderator" | "member",
): Promise<CommunityMemberResponse> => {
  console.log("Updating member role:", { communityId, id, memberId, newRole });

  const response = await fetch(
    `${API_URL}/admin/${communityId}/users/${memberId}/update-role`,
    {
      method: "PATCH",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        new_role: newRole,
      }),
    },
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({
      message: "Erro ao atualizar role do membro",
    }));
    throw new Error(errorData.message || "Erro ao atualizar role do membro");
  }

  return response.json();
};

// Remover membro da comunidade
export const removeMemberFromCommunity = async (
  token: string,
  communityId: string,
  memberId: string,
): Promise<void> => {
  console.log("Removing member from community:", { communityId, memberId });

  const response = await fetch(
    `${API_URL}/admin/${communityId}/users/${memberId}/remove`,
    {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    },
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({
      message: "Erro ao remover membro",
    }));
    throw new Error(errorData.message || "Erro ao remover membro");
  }
};
