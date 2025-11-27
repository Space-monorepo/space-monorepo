import { useState, useCallback, useEffect } from "react";
import { ConnectionNotification } from "@/app/api/src/types/notifications/Notification";
import { fetchConnections } from "@/app/api/src/services/notifications/notificationService";
import getTokenFromCookies from "@/app/api/src/controllers/getTokenFromCookies";

interface UseConnectionsListOutput {
  connections: ConnectionNotification[];
  loading: boolean;
  error: Error | null;
  refreshConnections: () => Promise<void>;
}

const useConnectionsList = (): UseConnectionsListOutput => {
  const [connections, setConnections] = useState<ConnectionNotification[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const token = getTokenFromCookies();

  const loadConnections = useCallback(async () => {
    if (!token) {
      setError(new Error("Token não encontrado"));
      return;
    }

    setLoading(true);
    setError(null);
    let timeoutTriggered = false;
    const timeoutId = window.setTimeout(() => {
      timeoutTriggered = true;
      setLoading(false);
      setError(
        new Error(
          "Não foi possível carregar suas conexões agora. Atualize a página ou tente novamente."
        )
      );
    }, 8000);

    try {
      const data = await fetchConnections(token);
      if (timeoutTriggered) return;
      clearTimeout(timeoutId);
      setConnections(data);
    } catch (err) {
      if (!timeoutTriggered) {
        clearTimeout(timeoutId);
        setError(err as Error);
        console.error("Erro ao carregar conexões:", err);
      }
    } finally {
      if (!timeoutTriggered) {
        setLoading(false);
      }
    }
  }, [token]);

  useEffect(() => {
    loadConnections();
  }, [loadConnections]);

  return {
    connections,
    loading,
    error,
    refreshConnections: loadConnections,
  };
};

export default useConnectionsList;
