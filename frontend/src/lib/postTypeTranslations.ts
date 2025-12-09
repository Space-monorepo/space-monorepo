/**
 * Função para traduzir os tipos de posts para português
 */
export const translatePostType = (postType: string): string => {
  const postTypeTranslations: Record<string, string> = {
    // Tipos de posts
    'campaign': 'Campanha',
    'complaint': 'Denúncia',
    'poll': 'Enquete',
    'announcement': 'Anúncio',
    
    // Casos especiais em maiúsculo
    'CAMPAIGN': 'Campanha',
    'COMPLAINT': 'Denúncia',
    'POLL': 'Enquete',
    'ANNOUNCEMENT': 'Anúncio',
    
    // Outras variações possíveis
    'report': 'Denúncia',
    'ad': 'Anúncio',
    'REPORT': 'Denúncia',
    'AD': 'Anúncio',
  };

  // Se o tipo existir no mapeamento, retorna a tradução
  if (postTypeTranslations[postType]) {
    return postTypeTranslations[postType];
  }

  // Se o tipo estiver em lowercase, tenta uppercase
  if (postTypeTranslations[postType.toUpperCase()]) {
    return postTypeTranslations[postType.toUpperCase()];
  }

  // Se não encontrar tradução, capitaliza a primeira letra
  return postType.charAt(0).toUpperCase() + postType.slice(1).toLowerCase();
};
