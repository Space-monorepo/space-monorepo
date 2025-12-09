import { updateUserProfile } from "../services/updateUserService";

export const updateProfile = async (token: string, name: string, bio: string) => {
  try {
    const data = await updateUserProfile(token, name, bio);
    return data;
  } catch (err) {
    if (err instanceof Error) {
      console.error("Erro ao atualizar perfil:", err.message);
    } else {
      console.error("Erro ao atualizar perfil: Erro desconhecido");
    }
    throw err;
  }
};
