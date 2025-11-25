import { useState, useCallback } from 'react';
import { toast } from 'react-toastify';
import {
  importUsersToCommunitya,
  listAllMembersFromCommunity,
  updateMemberRole,
  removeMemberFromCommunity,
  CommunityMemberResponse,
  PaginationResponse
} from '../../services/community/communityUserService';
import getTokenFromCookies from '../../controllers/getTokenFromCookies';

interface UseCommunityUserActionsProps {
  onSuccess?: (message?: string) => void;
  onError?: (error: Error) => void;
}

interface UseCommunityUserActionsOutput {
  isLoading: boolean;
  members: CommunityMemberResponse[];
  pagination: PaginationResponse<CommunityMemberResponse> | null;
  loadMembers: (communityId: string, params?: { offset?: number; limit?: number; name?: string }) => Promise<void>;
  addModeratorByEmail: (id: string, communityId: string, email: string) => Promise<void>;
  removeUserById: (id: string, communityId: string, memberId: string) => Promise<void>;
  updateUserRole: (id: string, communityId: string, memberId: string, newRole: 'admin' | 'moderator' | 'member') => Promise<void>;
  importUsers: (communityId: string, emails: string[]) => Promise<void>;
  refreshMembers: () => Promise<void>;
}

const useCommunityUserActions = ({
  onSuccess,
  onError
}: UseCommunityUserActionsProps = {}): UseCommunityUserActionsOutput => {
  const [isLoading, setIsLoading] = useState(false);
  const [members, setMembers] = useState<CommunityMemberResponse[]>([]);
  const [pagination, setPagination] = useState<PaginationResponse<CommunityMemberResponse> | null>(null);
  const [currentCommunityId, setCurrentCommunityId] = useState<string | null>(null);
  const [currentParams, setCurrentParams] = useState<{ offset?: number; limit?: number; name?: string } | undefined>();

  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };
  const loadMembers = useCallback(async (communityId: string, params?: { offset?: number; limit?: number; name?: string }) => {
    setIsLoading(true);
    setCurrentCommunityId(communityId);
    setCurrentParams(params);

    try {
      const token = getTokenFromCookies();
      if (!token) {
        throw new Error('Token não encontrado. Faça login novamente.');
      }

      const response = await listAllMembersFromCommunity(token, communityId, params);
      console.log('DEBUG: Response from listAllMembersFromCommunity:', response);
      console.log('DEBUG: First member structure:', response.items[0]);
      setMembers(response.items);
      setPagination(response);

    } catch (error) {
      console.error('Erro ao carregar membros:', error);
      const errorMessage = error instanceof Error ? error.message : 'Erro ao carregar membros';
      onError?.(error instanceof Error ? error : new Error(errorMessage));
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [onError]);

  const refreshMembers = useCallback(async () => {
    if (currentCommunityId) {
      setIsLoading(true);
      try {
        const token = getTokenFromCookies();
        if (!token) {
          throw new Error('Token não encontrado. Faça login novamente.');
        }

        const response = await listAllMembersFromCommunity(token, currentCommunityId, currentParams);
        setMembers(response.items);
        setPagination(response);

      } catch (error) {
        console.error('Erro ao recarregar membros:', error);
        const errorMessage = error instanceof Error ? error.message : 'Erro ao recarregar membros';
        onError?.(error instanceof Error ? error : new Error(errorMessage));
        toast.error(errorMessage);
      } finally {
        setIsLoading(false);
      }
    }
  }, [currentCommunityId, currentParams, onError]);
  const findMemberByEmail = (email: string): CommunityMemberResponse | null => {
    return members.find(member =>
      member.user.email.toLowerCase() === email.toLowerCase()
    ) || null;
  };

  const addModeratorByEmail = async (id: string, communityId: string, email: string) => {
    if (!email.trim()) {
      const error = new Error('Por favor, digite um email válido');
      onError?.(error);
      toast.error(error.message);
      return;
    }

    if (!validateEmail(email)) {
      const error = new Error('Por favor, digite um email válido');
      onError?.(error);
      toast.error(error.message);
      return;
    }

    setIsLoading(true);
    try {
      const token = getTokenFromCookies();
      if (!token) {
        throw new Error('Token não encontrado. Faça login novamente.');
      }

      const emailLower = email.trim().toLowerCase();

      // Verificar se o usuário já é membro da comunidade
      const existingMember = findMemberByEmail(emailLower);
      if (existingMember) {
        // Se já é membro, apenas atualizar o papel para moderador
        if (existingMember.role !== 'moderator') {
          await updateMemberRole(id, token, communityId, existingMember.id, 'moderator');
          const successMessage = 'Usuário promovido a moderador com sucesso!';
          onSuccess?.(successMessage);
          toast.success(successMessage);
        } else {
          const infoMessage = 'Este usuário já é um moderador da comunidade.';
          toast.info(infoMessage);
        }
      } else {
        // Se não é membro, importar primeiro e depois atualizar para moderador
        const importedUsers = await importUsersToCommunitya(token, communityId, [emailLower]);

        if (importedUsers.length > 0) {
          const user = importedUsers[0]; if (user.role !== 'moderator') {
            await updateMemberRole(id, token, communityId, user.id, 'moderator');
          }
          const successMessage = 'Usuário importado e promovido a moderador com sucesso!';
          onSuccess?.(successMessage);
          toast.success(successMessage);
        }
      }

      // Recarregar a lista de membros
      await refreshMembers();

    } catch (error) {
      console.error('Erro ao adicionar moderador:', error);
      const errorMessage = error instanceof Error ? error.message : 'Erro ao adicionar moderador';
      onError?.(error instanceof Error ? error : new Error(errorMessage));
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };
  const removeUserById = async (id: string, communityId: string, memberId: string) => {
    console.log('DEBUG: removeUserById called with:', { id, communityId, memberId });
    setIsLoading(true);
    try {
      const token = getTokenFromCookies();
      if (!token) {
        throw new Error('Token não encontrado. Faça login novamente.');
      }

      await removeMemberFromCommunity(token, communityId, memberId);

      const successMessage = 'Usuário removido com sucesso!';
      onSuccess?.(successMessage);
      toast.success(successMessage);

      // Recarregar a lista de membros
      await refreshMembers();

    } catch (error) {
      console.error('Erro ao remover usuário:', error);
      const errorMessage = error instanceof Error ? error.message : 'Erro ao remover usuário';
      onError?.(error instanceof Error ? error : new Error(errorMessage));
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const updateUserRole = async (id: string, communityId: string, memberId: string, newRole: 'admin' | 'moderator' | 'member') => {
    console.log('DEBUG: updateUserRole called with:', { communityId, memberId, newRole });
    setIsLoading(true);
    try {
      const token = getTokenFromCookies();
      if (!token) {
        throw new Error('Token não encontrado. Faça login novamente.');
      }

      await updateMemberRole(id, token, communityId, memberId, newRole);

      const successMessage = `Role atualizado para ${newRole} com sucesso!`;
      onSuccess?.(successMessage);
      toast.success(successMessage);

      // Recarregar a lista de membros
      await refreshMembers();

    } catch (error) {
      console.error('Erro ao atualizar role:', error);
      const errorMessage = error instanceof Error ? error.message : 'Erro ao atualizar role';
      onError?.(error instanceof Error ? error : new Error(errorMessage));
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };
  const importUsers = async (communityId: string, emails: string[]) => {
    const cleanEmails = emails.map(email => email.trim().toLowerCase()).filter(email => email);
    const invalidEmails = cleanEmails.filter(email => !validateEmail(email));

    if (invalidEmails.length > 0) {
      const error = new Error(`Emails inválidos: ${invalidEmails.join(', ')}`);
      onError?.(error);
      toast.error(error.message);
      return;
    }

    if (cleanEmails.length === 0) {
      const error = new Error('Nenhum email válido fornecido');
      onError?.(error);
      toast.error(error.message);
      return;
    }

    setIsLoading(true);
    try {
      const token = getTokenFromCookies();
      if (!token) {
        throw new Error('Token não encontrado. Faça login novamente.');
      }

      // Separar emails de usuários que já são membros dos que não são
      const existingMembers: string[] = [];
      const newEmails: string[] = [];

      cleanEmails.forEach(email => {
        const existingMember = findMemberByEmail(email);
        if (existingMember) {
          existingMembers.push(email);
        } else {
          newEmails.push(email);
        }
      }); let importCount = 0;
      const skippedCount = existingMembers.length;

      // Importar apenas usuários que não são membros
      if (newEmails.length > 0) {
        const importedUsers = await importUsersToCommunitya(token, communityId, newEmails);
        importCount = importedUsers.length;
      }

      // Construir mensagem de sucesso
      let successMessage = '';
      if (importCount > 0 && skippedCount > 0) {
        successMessage = `${importCount} usuários importados com sucesso! ${skippedCount} usuários já eram membros da comunidade.`;
      } else if (importCount > 0) {
        successMessage = `${importCount} usuários importados com sucesso!`;
      } else if (skippedCount > 0) {
        successMessage = `Todos os ${skippedCount} usuários já eram membros da comunidade.`;
      }

      onSuccess?.(successMessage);
      toast.success(successMessage);

      // Recarregar a lista de membros
      await refreshMembers();

    } catch (error) {
      console.error('Erro ao importar usuários:', error);
      const errorMessage = error instanceof Error ? error.message : 'Erro ao importar usuários';
      onError?.(error instanceof Error ? error : new Error(errorMessage));
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return {
    isLoading,
    members,
    pagination,
    loadMembers,
    addModeratorByEmail,
    removeUserById,
    updateUserRole,
    importUsers,
    refreshMembers
  };
};

export default useCommunityUserActions;
