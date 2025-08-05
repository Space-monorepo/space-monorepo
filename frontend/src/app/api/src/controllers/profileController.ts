import { fetchUserProfile as fetchProfileDataService } from './../services/userService';

export const fetchProfileData = async (token: string) => {
  try {
    console.log("Token recebido no controller:", token);
    if (!token) throw new Error("Token não encontrado");

    const user = await fetchProfileDataService(token);
    return user;
  } catch (error) {
    console.error("Erro ao buscar dados do perfil:", error);
    throw new Error("Não foi possível carregar o perfil.");
  }
};
