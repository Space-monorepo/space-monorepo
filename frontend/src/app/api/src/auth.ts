import { API_URL } from '@/config';
import axios from 'axios';


export const loginUser = async (formData: FormData) => {
  try {
    const response = await axios.post(`${API_URL}/users/login`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (err: unknown) {
    if (axios.isAxiosError(err)) {
      const apiMessage = err.response?.data?.detail;
      throw new Error(apiMessage || 'Login falhou. Tente novamente.');
    } else if (err instanceof Error) {
      throw new Error(err.message);
    } else {
      throw new Error('Unknown error occurred.');
    }
  }
};

export const registerUser = async (data: {
  name: string;
  email: string;
  password: string;
  profile_image_url?: string;
}) => {
  try {
    // Derive a username from the email (part before @), fallback to name without spaces
    const rawUsername = data.email ? data.email.split('@')[0] : data.name.replace(/\s+/g, '').toLowerCase();
    const username = rawUsername.slice(0, 50);

    // Send only the fields expected by the backend's `UserCreate` schema
    const payload = {
      username,
      name: data.name,
      email: data.email,
      hashed_password: data.password,
      profile_image_url: data.profile_image_url || null,
    } as const;

    const response = await axios.post(`${API_URL}/users/signup`, payload);
    return response.data;
  } catch (err: unknown) {
    if (axios.isAxiosError(err)) {
      const apiMessage = err.response?.data?.detail;
      throw new Error(apiMessage || 'Falha no cadastro. Tente novamente.');
    } else if (err instanceof Error) {
      throw new Error(err.message);
    } else {
      throw new Error('Erro desconhecido.');
    }
  }
};
