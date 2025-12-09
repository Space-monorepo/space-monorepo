import { API_URL } from "@/config";

interface ConversationParticipantApi {
  id: string;
  name: string;
  email?: string;
  profile_image_url?: string;
  profile_picture?: string;
}

interface ConversationResponseApi {
  id: string;
  user1_id: string;
  user2_id: string;
  created_at: string;
  updated_at: string;
  last_message_id?: string;
  unread_count?: number;
  last_message?: {
    id: string;
    content?: string;
    created_at?: string;
  };
  user1?: ConversationParticipantApi;
  user2?: ConversationParticipantApi;
  other_participant?: ConversationParticipantApi;
  participant?: ConversationParticipantApi;
}

export interface ConversationParticipant {
  id: string;
  name: string;
  email?: string;
  profile_image_url?: string;
  profile_picture?: string;
}

export interface Conversation {
  id: string;
  participant_user_id: string;
  participant: ConversationParticipant;
  last_message?: string;
  last_message_timestamp?: string;
  unread_count?: number;
  created_at: string;
}

export interface Message {
  id: string;
  content: string;
  sender_id: string;
  conversation_id: string;
  created_at: string;
  is_read: boolean;
  reply_to_message_id?: string;
  attachments?: Attachment[];
}

export interface Attachment {
  id: string;
  file_url: string;
  file_type: string;
  file_name: string;
}

export interface ConversationCreatePayload {
  participant_user_id: string;
}

export interface MessageCreatePayload {
  content: string;
  reply_to_message_id?: string;
}

export interface PaginationResponse<T> {
  items: T[];
  total: number;
  offset: number;
  limit: number;
  has_next: boolean;
}

// Buscar todas as conversas do usuário
export const fetchConversations = async (
  token: string,
  offset: number = 0,
  limit: number = 20,
  name?: string
): Promise<PaginationResponse<Conversation>> => {
  const params = new URLSearchParams();
  params.append("offset", offset.toString());
  params.append("limit", limit.toString());
  if (name) params.append("name", name);

  const response = await fetch(`${API_URL}/chat/conversations?${params}`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const errorData = await response
      .json()
      .catch(() => ({ message: "Erro ao carregar conversas" }));
    throw new Error(errorData.message || "Erro ao carregar conversas");
  }

  const data: PaginationResponse<ConversationResponseApi> = await response.json();

  return {
    ...data,
    items: data.items.map(normalizeConversationResponse),
  };
};

// Buscar conversa específica
export const fetchConversation = async (
  token: string,
  conversationId: string
): Promise<Conversation> => {
  const response = await fetch(`${API_URL}/chat/conversations/${conversationId}`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const errorData = await response
      .json()
      .catch(() => ({ message: "Erro ao carregar conversa" }));
    throw new Error(errorData.message || "Erro ao carregar conversa");
  }

  const data: ConversationResponseApi = await response.json();
  return normalizeConversationResponse(data);
};

// Criar nova conversa
export const createConversation = async (
  token: string,
  participantUserId: string
): Promise<Conversation> => {
  const response = await fetch(`${API_URL}/chat/conversations`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      participant_user_id: participantUserId,
    }),
  });

  if (!response.ok) {
    const errorData = await response
      .json()
      .catch(() => ({ message: "Erro ao criar conversa" }));
    throw new Error(errorData.message || "Erro ao criar conversa");
  }

  const data: ConversationResponseApi = await response.json();
  return normalizeConversationResponse(data);
};

// Buscar mensagens de uma conversa
export const fetchMessages = async (
  token: string,
  conversationId: string,
  offset: number = 0,
  limit: number = 50
): Promise<PaginationResponse<Message>> => {
  const params = new URLSearchParams();
  params.append("offset", offset.toString());
  params.append("limit", limit.toString());

  const response = await fetch(
    `${API_URL}/chat/conversations/${conversationId}/messages?${params}`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    const errorData = await response
      .json()
      .catch(() => ({ message: "Erro ao carregar mensagens" }));
    throw new Error(errorData.message || "Erro ao carregar mensagens");
  }

  return response.json();
};

// Enviar mensagem
export const sendMessage = async (
  token: string,
  conversationId: string,
  content: string,
  replyToMessageId?: string
): Promise<Message> => {
  const response = await fetch(
    `${API_URL}/chat/conversations/${conversationId}/messages`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        content,
        reply_to_message_id: replyToMessageId,
      }),
    }
  );

  if (!response.ok) {
    const errorData = await response
      .json()
      .catch(() => ({ message: "Erro ao enviar mensagem" }));
    throw new Error(errorData.message || "Erro ao enviar mensagem");
  }

  return response.json();
};

// Marcar mensagens como lidas
export const markConversationAsRead = async (
  token: string,
  conversationId: string
): Promise<void> => {
  const response = await fetch(
    `${API_URL}/chat/conversations/${conversationId}/messages/read`,
    {
      method: "PATCH",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    const errorData = await response
      .json()
      .catch(() => ({ message: "Erro ao marcar como lida" }));
    throw new Error(errorData.message || "Erro ao marcar como lida");
  }
};

// Deletar mensagem
export const deleteMessage = async (
  token: string,
  messageId: string
): Promise<void> => {
  const response = await fetch(`${API_URL}/chat/messages/${messageId}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const errorData = await response
      .json()
      .catch(() => ({ message: "Erro ao deletar mensagem" }));
    throw new Error(errorData.message || "Erro ao deletar mensagem");
  }
};

// Obter contagem de não lidos
export const getUnreadCount = async (
  token: string,
  conversationId: string
): Promise<number> => {
  const response = await fetch(
    `${API_URL}/chat/conversations/${conversationId}/unread-count`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    const errorData = await response
      .json()
      .catch(() => ({ message: "Erro ao obter contagem de não lidos" }));
    throw new Error(
      errorData.message || "Erro ao obter contagem de não lidos"
    );
  }

  const data = await response.json();
  return data.unread_count || 0;
};

const normalizeConversationResponse = (
  conversation: ConversationResponseApi
): Conversation => {
  const participantSource =
    conversation.other_participant || conversation.participant;

  const participant: ConversationParticipant = {
    id: participantSource?.id || "",
    name: participantSource?.name || "Usuário",
    email: participantSource?.email,
    profile_image_url: participantSource?.profile_image_url,
    profile_picture: participantSource?.profile_picture,
  };

  return {
    id: conversation.id,
    participant_user_id: participant.id,
    participant,
    last_message: conversation.last_message?.content,
    last_message_timestamp: conversation.last_message?.created_at,
    unread_count: conversation.unread_count,
    created_at: conversation.created_at,
  };
};
