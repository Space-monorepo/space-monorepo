// src/controllers/userController.ts
import { fetchUserProfile } from "../services/userService";
import { toast } from "react-toastify";

export const loadUserProfile = async (token: string) => {
  try {
    const data = await fetchUserProfile(token);
    return data;
  } catch (err) {
    if (err instanceof Error) {
      toast.warning("Sua sessão expirou. Faça login novamente.");
    } else {
      toast.error("Erro ao carregar os dados do perfil: Erro desconhecido");
    }
  }
};
