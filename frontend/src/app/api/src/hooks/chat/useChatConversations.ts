import { useState, useEffect, useCallback } from "react";
import {
  fetchConversations,
  fetchConversation,
  createConversation,
  Conversation,
} from "@/app/api/src/services/chat/chatService";
import getTokenFromCookies from "@/app/api/src/controllers/getTokenFromCookies";

interface UseChatConversationsOutput {
  conversations: Conversation[];
  loading: boolean;
  error: Error | null;
  selectedConversation: Conversation | null;
  setSelectedConversation: (conversation: Conversation | null) => void;
  loadConversations: (offset?: number, limit?: number, name?: string) => Promise<void>;
  selectConversation: (conversationId: string) => Promise<void>;
  createNewConversation: (participantUserId: string) => Promise<Conversation>;
  refreshConversations: () => Promise<void>;
}

const useChatConversations = (): UseChatConversationsOutput => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null);

  const token = getTokenFromCookies();

  const loadConversations = useCallback(
    async (offset: number = 0, limit: number = 20, name?: string) => {
      if (!token) {
        setError(new Error("Token não encontrado"));
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const data = await fetchConversations(token, offset, limit, name);
        setConversations(data.items);
      } catch (err) {
        setError(err as Error);
        console.error("Erro ao carregar conversas:", err);
      } finally {
        setLoading(false);
      }
    },
    [token]
  );

  const selectConversation = useCallback(
    async (conversationId: string) => {
      if (!token) {
        setError(new Error("Token não encontrado"));
        return;
      }

      try {
        const conversation = await fetchConversation(token, conversationId);
        setSelectedConversation(conversation);
      } catch (err) {
        setError(err as Error);
        console.error("Erro ao carregar conversa:", err);
      }
    },
    [token]
  );

  const createNewConversation = useCallback(
    async (participantUserId: string): Promise<Conversation> => {
      if (!token) {
        throw new Error("Token não encontrado");
      }

      try {
        const conversation = await createConversation(token, participantUserId);
        setConversations((prev) => [conversation, ...prev]);
        setSelectedConversation(conversation);
        return conversation;
      } catch (err) {
        setError(err as Error);
        console.error("Erro ao criar conversa:", err);
        throw err;
      }
    },
    [token]
  );

  const refreshConversations = useCallback(async () => {
    await loadConversations();
  }, [loadConversations]);

  // Carregar conversas ao montar o componente
  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  return {
    conversations,
    loading,
    error,
    selectedConversation,
    setSelectedConversation,
    loadConversations,
    selectConversation,
    createNewConversation,
    refreshConversations,
  };
};

export default useChatConversations;
