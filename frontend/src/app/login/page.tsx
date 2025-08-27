'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Cookies from 'js-cookie';
import { toast } from 'react-toastify';
import { API_URL } from '@/config';
import { loginUser } from '@/app/api/src';
import { useBypassAuth } from '@/app/api/src/hooks/useBypassAuth';
import Header from './components/Header';
import LoginForm from './components/LoginForm';
import SocialLoginButtons from './components/SocialLoginButtons';
import ImageSection from './components/ImageSection';

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



  const handleLogin = async (data: { email: string; password: string }) => {
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
    <main className="flex min-h-screen bg-white overflow-x-hidden">
      {/* Imagem lateral esquerda */}
      <div className="hidden md:flex w-1/2 items-center justify-center">
        <ImageSection />
      </div>
      <div className="flex-1 flex items-center justify-center bg-white">
        <section className="flex flex-col gap-28 items-start w-full max-w-[480px] px-4">
          <Header />

          <section className="flex flex-col gap-8 items-start w-full">
            <LoginForm onSubmit={handleLogin} />
            <div className="flex justify-between items-center w-full">
              <div className="h-px bg-stone-300 w-[152px]" />
              <p className="text-xs leading-4 text-neutral-500">Ou entre com</p>
              <div className="h-px bg-stone-300 w-[152px]" />
            </div>
            <SocialLoginButtons />
          </section>
        </section>
      </div>
    </main>
  );
}