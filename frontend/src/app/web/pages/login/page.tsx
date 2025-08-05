'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Cookies from 'js-cookie';
import { toast } from 'react-toastify';
import { API_URL } from '@/config';
import LoginForm from './components/LoginForm';
import SocialLoginButtons from './components/SocialLoginButtons';
import Header from './components/Header';
import ImageSection from './components/ImageSection';
import { loginUser } from '@/app/api/src';
import { Separator } from '@/components/ui/separator';
import { useBypassAuth } from '@/app/api/src/hooks/useBypassAuth';

export default function LoginPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(Cookies.get('token') || null);
  const bypass = useBypassAuth();

  useEffect(() => {
    if (token) {
      const checkTokenValidity = async () => {
        try {
          const response = await fetch(`${API_URL}/users/me`, {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          });

          if (!response.ok) {
            Cookies.remove('token');
            toast.error('Sua sessão expirou. Por favor, faça login novamente.');
          } else {
            router.push('/home');
          }
        } catch (error) {
          console.error('Erro ao verificar o token:', error);
          toast.error('Erro ao verificar o token. Por favor, faça login novamente.');
          Cookies.remove('token');
        }
      };

      checkTokenValidity();
    }
  }, [token, router, bypass]);

  interface LoginData {
    email: string;
    password: string;
  }

  const handleLogin = async (data: LoginData) => {
    try {
      const formData = new FormData();
      formData.append('username', data.email);
      formData.append('password', data.password);

      const response = await loginUser(formData);
      const newToken = response.token || response.data?.token || response.access_token;

      if (newToken) {
        Cookies.set('token', newToken, { path: '/', secure: true, sameSite: 'Lax', expires: 7 });
        setToken(newToken);
        toast.success('Login realizado com sucesso!');
        router.push('/home');
      } else {
        toast.error('Token não encontrado na resposta do servidor');
      }
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Falha no login');
    }
  };

  return (
    <main className="flex min-h-screen flex-col md:flex-row">
      <ImageSection />
      <div className="flex items-center justify-center w-full md:w-1/2 bg-gray-100 p-6">
        <div className="max-w-[400px] w-full space-y-8">
          <Header />
          <LoginForm onSubmit={handleLogin} />
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <Separator className="w-full" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-gray-100 px-2 text-gray-500">Ou entre com</span>
            </div>
          </div>
          <SocialLoginButtons />
        </div>
      </div>
    </main>
  );
}