// src/controllers/userController.ts
import { fetchUserProfile } from "../services/userService";

export const loadUserProfile = async (token: string) => {
  try {
    const data = await fetchUserProfile(token);
    return data;
  } catch (err) {
    if (err instanceof Error) {
      console.error("Erro ao carregar perfil:", err.message);
    } else {
      console.error("Erro ao carregar os dados do perfil: Erro desconhecido");
    }
    throw err; // Re-throw para que o chamador possa tratar
  }
};
