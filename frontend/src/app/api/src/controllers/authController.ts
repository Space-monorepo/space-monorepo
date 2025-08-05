// src/controllers/authController.ts
import { loginUser } from "../../../api/src/services/authService";

export const login = async (formData: FormData) => {
  try {
    const data = await loginUser(formData);
    return data;
  } catch (err) {
    if (err instanceof Error) {
      throw new Error("Erro no login: " + err.message);
    } else {
      throw new Error("Erro no login: Erro desconhecido");
    }
  }
};
