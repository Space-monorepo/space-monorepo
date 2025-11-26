import { useState, useCallback } from "react";
import {
  requestConnection,
  acceptConnection,
  rejectConnection,
  deleteConnection,
  getConnectionStatus,
  UserConnection,
  ConnectionStatus,
} from "@/app/api/src/services/connection/connectionService";
import getTokenFromCookies from "@/app/api/src/controllers/getTokenFromCookies";

interface UseConnectionActionsOutput {
  loading: boolean;
  error: Error | null;
  sendConnectionRequest: (userId: string) => Promise<UserConnection>;
  acceptConnectionRequest: (connectionId: string) => Promise<UserConnection>;
  rejectConnectionRequest: (connectionId: string) => Promise<UserConnection>;
  removeConnection: (connectionId: string) => Promise<void>;
  checkConnectionStatus: (userId: string) => Promise<UserConnection | null>;
  isConnected: (status: ConnectionStatus | null) => boolean;
}

const useConnectionActions = (): UseConnectionActionsOutput => {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  const token = getTokenFromCookies();

  const sendConnectionRequest = useCallback(
    async (userId: string): Promise<UserConnection> => {
      if (!token) {
        throw new Error("Token não encontrado");
      }

      setLoading(true);
      setError(null);

      try {
        const connection = await requestConnection(token, userId);
        return connection;
      } catch (err) {
        setError(err as Error);
        console.error("Erro ao enviar pedido de conexão:", err);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [token]
  );

  const acceptConnectionRequest = useCallback(
    async (connectionId: string): Promise<UserConnection> => {
      if (!token) {
        throw new Error("Token não encontrado");
      }

      setLoading(true);
      setError(null);

      try {
        const connection = await acceptConnection(token, connectionId);
        return connection;
      } catch (err) {
        setError(err as Error);
        console.error("Erro ao aceitar conexão:", err);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [token]
  );

  const rejectConnectionRequest = useCallback(
    async (connectionId: string): Promise<UserConnection> => {
      if (!token) {
        throw new Error("Token não encontrado");
      }

      setLoading(true);
      setError(null);

      try {
        const connection = await rejectConnection(token, connectionId);
        return connection;
      } catch (err) {
        setError(err as Error);
        console.error("Erro ao rejeitar conexão:", err);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [token]
  );

  const removeConnection = useCallback(
    async (connectionId: string): Promise<void> => {
      if (!token) {
        throw new Error("Token não encontrado");
      }

      setLoading(true);
      setError(null);

      try {
        await deleteConnection(token, connectionId);
      } catch (err) {
        setError(err as Error);
        console.error("Erro ao remover conexão:", err);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [token]
  );

  const checkConnectionStatus = useCallback(
    async (userId: string): Promise<UserConnection | null> => {
      if (!token) {
        throw new Error("Token não encontrado");
      }

      setLoading(true);
      setError(null);

      try {
        const connection = await getConnectionStatus(token, userId);
        return connection;
      } catch (err) {
        setError(err as Error);
        console.error("Erro ao verificar conexão:", err);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [token]
  );

  const isConnected = useCallback((status: ConnectionStatus | null): boolean => {
    return status === "accepted";
  }, []);

  return {
    loading,
    error,
    sendConnectionRequest,
    acceptConnectionRequest,
    rejectConnectionRequest,
    removeConnection,
    checkConnectionStatus,
    isConnected,
  };
};

export default useConnectionActions;
