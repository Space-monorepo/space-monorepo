import { API_URL } from "@/config";

// src/services/authService.ts
export const loginUser = async (formData: FormData) => {
    const response = await fetch(`${API_URL}/users/login`, {
      method: "POST",
      body: formData,
    });
  
    if (!response.ok) {
      throw new Error("Erro no login");
    }
  
    return response.json();
  };
  