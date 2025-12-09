import { API_URL } from "@/config";

// Função para atualizar o perfil do usuário
export const updateUserProfile = async (token: string, name: string, bio: string) => {
  const response = await fetch(`${API_URL}/users/me`, {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      name,
      bio,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ 
      message: 'Erro ao atualizar perfil' 
    }));
    throw new Error(errorData.message || 'Erro ao atualizar perfil');
  }

  return response.json();
};
