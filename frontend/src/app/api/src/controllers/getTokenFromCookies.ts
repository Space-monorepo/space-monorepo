const getTokenFromCookies = () => { // Função para obter o token dos cookies
  if ( typeof document === 'undefined' ) return null; // Verifica se está no servidor
    const cookie = document.cookie
      .split("; ")
      .find((row) => row.startsWith("token="));
  
    if (!cookie) return null;   
    return cookie.split("=")[1];
  };

export default getTokenFromCookies;