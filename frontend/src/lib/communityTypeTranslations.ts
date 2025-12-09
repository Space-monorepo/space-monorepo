/**
 * Função para traduzir os tipos de comunidade para português
 */
export const translateCommunityType = (communityType: string): string => {
  const communityTypeTranslations: Record<string, string> = {
    // Tipos de comunidade
    'university': 'Universidade',
    'neighborhood': 'Bairro',
    'company': 'Empresa',
    'government': 'Governo',
    'healthcare': 'Saúde',
    'religious': 'Religiosa',
    'commercial': 'Comercial',
    'club': 'Clube',
    
    // Casos especiais em maiúsculo
    'UNIVERSITY': 'Universidade',
    'NEIGHBORHOOD': 'Bairro',
    'COMPANY': 'Empresa',
    'GOVERNMENT': 'Governo',
    'HEALTHCARE': 'Saúde',
    'RELIGIOUS': 'Religiosa',
    'COMMERCIAL': 'Comercial',
    'CLUB': 'Clube',
  };

  // Se o tipo existir no mapeamento, retorna a tradução
  if (communityTypeTranslations[communityType]) {
    return communityTypeTranslations[communityType];
  }

  // Se o tipo estiver em lowercase, tenta uppercase
  if (communityTypeTranslations[communityType.toUpperCase()]) {
    return communityTypeTranslations[communityType.toUpperCase()];
  }

  // Se não encontrar tradução, capitaliza a primeira letra
  return communityType.charAt(0).toUpperCase() + communityType.slice(1).toLowerCase();
};
