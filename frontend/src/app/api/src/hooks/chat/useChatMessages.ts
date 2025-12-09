import { useState, useCallback } from "react";
import {
  fetchMessages,
  sendMessage,
  markConversationAsRead,
  deleteMessage,
  Message,
} from "@/app/api/src/services/chat/chatService";
import getTokenFromCookies from "@/app/api/src/controllers/getTokenFromCookies";

interface UseChatMessagesOutput {
  messages: Message[];
  loading: boolean;
  error: Error | null;
  loadMessages: (conversationId: string, offset?: number, limit?: number) => Promise<void>;
  sendMessage: (conversationId: string, content: string) => Promise<void>;
  markAsRead: (conversationId: string) => Promise<void>;
  deleteMessage: (messageId: string) => Promise<void>;
  addMessageOptimistic: (message: Message) => void;
}

const useChatMessages = (): UseChatMessagesOutput => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  const token = getTokenFromCookies();

  const loadMessages = useCallback(
    async (conversationId: string, offset: number = 0, limit: number = 50) => {
      if (!token) {
        setError(new Error("Token não encontrado"));
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const data = await fetchMessages(token, conversationId, offset, limit);
        // Reverter ordem para que as mensagens mais recentes fiquem por último
        setMessages(data.items.reverse());
      } catch (err) {
        setError(err as Error);
        console.error("Erro ao carregar mensagens:", err);
      } finally {
        setLoading(false);
      }
    },
    [token]
  );

  const sendMessageHandler = useCallback(
    async (conversationId: string, content: string) => {
      if (!token) {
        throw new Error("Token não encontrado");
      }

      try {
        const message = await sendMessage(token, conversationId, content);
        setMessages((prev) => [...prev, message]);
      } catch (err) {
        setError(err as Error);
        console.error("Erro ao enviar mensagem:", err);
        throw err;
      }
    },
    [token]
  );

  const markAsRead = useCallback(
    async (conversationId: string) => {
      if (!token) {
        setError(new Error("Token não encontrado"));
        return;
      }

      try {
        await markConversationAsRead(token, conversationId);
      } catch (err) {
        setError(err as Error);
        console.error("Erro ao marcar como lida:", err);
      }
    },
    [token]
  );

  const deleteMessageHandler = useCallback(
    async (messageId: string) => {
      if (!token) {
        throw new Error("Token não encontrado");
      }

      try {
        await deleteMessage(token, messageId);
        setMessages((prev) => prev.filter((msg) => msg.id !== messageId));
      } catch (err) {
        setError(err as Error);
        console.error("Erro ao deletar mensagem:", err);
        throw err;
      }
    },
    [token]
  );

  const addMessageOptimistic = useCallback((message: Message) => {
    setMessages((prev) => [...prev, message]);
  }, []);

  return {
    messages,
    loading,
    error,
    loadMessages,
    sendMessage: sendMessageHandler,
    markAsRead,
    deleteMessage: deleteMessageHandler,
    addMessageOptimistic,
  };
};

export default useChatMessages;
