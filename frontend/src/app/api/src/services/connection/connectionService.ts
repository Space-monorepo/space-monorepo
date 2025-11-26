import { API_URL } from "@/config";

export type ConnectionStatus = "pending" | "accepted" | "rejected";

export interface UserConnection {
  id: string;
  requester_id: string;
  addressee_id: string;
  status: ConnectionStatus;
  created_at: string;
  updated_at: string;
}

export interface ConnectionCreatePayload {
  addressee_id: string;
}

// Enviar pedido de conexão
export const requestConnection = async (
  token: string,
  addresseeId: string
): Promise<UserConnection> => {
  const response = await fetch(`${API_URL}/users/connections/request`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      addressee_id: addresseeId,
    }),
  });

  if (!response.ok) {
    const errorData = await response
      .json()
      .catch(() => ({ message: "Erro ao enviar pedido de conexão" }));
    throw new Error(errorData.message || "Erro ao enviar pedido de conexão");
  }

  return response.json();
};

// Aceitar pedido de conexão
export const acceptConnection = async (
  token: string,
  connectionId: string
): Promise<UserConnection> => {
  const response = await fetch(
    `${API_URL}/users/connections/${connectionId}/accept`,
    {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    const errorData = await response
      .json()
      .catch(() => ({ message: "Erro ao aceitar conexão" }));
    throw new Error(errorData.message || "Erro ao aceitar conexão");
  }

  return response.json();
};

// Rejeitar pedido de conexão
export const rejectConnection = async (
  token: string,
  connectionId: string
): Promise<UserConnection> => {
  const response = await fetch(
    `${API_URL}/users/connections/${connectionId}/reject`,
    {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    const errorData = await response
      .json()
      .catch(() => ({ message: "Erro ao rejeitar conexão" }));
    throw new Error(errorData.message || "Erro ao rejeitar conexão");
  }

  return response.json();
};

// Deletar conexão
export const deleteConnection = async (
  token: string,
  connectionId: string
): Promise<void> => {
  const response = await fetch(`${API_URL}/users/connections/${connectionId}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const errorData = await response
      .json()
      .catch(() => ({ message: "Erro ao deletar conexão" }));
    throw new Error(errorData.message || "Erro ao deletar conexão");
  }
};

// Obter status de conexão com um usuário
export const getConnectionStatus = async (
  token: string,
  userId: string
): Promise<UserConnection | null> => {
  const response = await fetch(`${API_URL}/users/connections/status/${userId}`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    // Status 404 significa que não há conexão
    if (response.status === 404) {
      return null;
    }
    const errorData = await response
      .json()
      .catch(() => ({ message: "Erro ao obter status de conexão" }));
    throw new Error(errorData.message || "Erro ao obter status de conexão");
  }

  return response.json();
};
