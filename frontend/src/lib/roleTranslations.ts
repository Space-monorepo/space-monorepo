/**
 * Função para traduzir os roles dos usuários para português
 */
export const translateUserRole = (role: string): string => {
  const roleTranslations: Record<string, string> = {
    // Roles de comunidade
    'admin': 'Administrador',
    'administrator': 'Administrador',
    'moderator': 'Moderador',
    'member': 'Membro',
    'leader': 'Líder',
    'owner': 'Dono',
    'creator': 'Criador',

    // Roles de reputação
    'under_observation': 'Sob observação',
    'sub-observation': 'Sob observação',
    'helper': 'Ajudante',
    'contributor': 'Colaborador',
    'collaborator': 'Colaborador',

    // Casos especiais em maiúsculo
    'ADMIN': 'Administrador',
    'ADMINISTRATOR': 'Administrador',
    'MODERATOR': 'Moderador',
    'MEMBER': 'Membro',
    'LEADER': 'Líder',
    'OWNER': 'Dono',
    'CREATOR': 'Criador',
  };

  // Se o role existir no mapeamento, retorna a tradução
  if (roleTranslations[role]) {
    return roleTranslations[role];
  }

  // Se o role estiver em lowercase, tenta uppercase
  if (roleTranslations[role.toUpperCase()]) {
    return roleTranslations[role.toUpperCase()];
  }

  // Se não encontrar tradução, capitaliza a primeira letra
  return role.charAt(0).toUpperCase() + role.slice(1).toLowerCase();
};
