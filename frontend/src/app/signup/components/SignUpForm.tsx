"use client";

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { registerSchema, RegisterFormData } from '@/app/api/src/schemas/auth';
import { useRouter } from 'next/navigation';
import { registerUser } from '@/app/api/src';
import SignUpHeader from './SignUpHeader';
import AlternativeSignUpMethods from './AlternativeSignUpMethods';
import { useState } from 'react';
import { toast } from 'react-toastify';


export default function SignUpForm() {
  const router = useRouter();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const onSubmit = async (data: RegisterFormData) => {
    if (data.password !== data.confirm_password) {
      alert('As senhas não coincidem.');
      return;
    }
    // Pega o valor do campo sobrenome manualmente
    const lastNameInput = document.querySelector<HTMLInputElement>('input[name="lastName"]');
    const lastName = lastNameInput ? lastNameInput.value.trim() : '';
    const fullName = `${data.name.trim()}${lastName ? ' ' + lastName : ''}`;

    // Seleciona aleatoriamente uma imagem padrão de perfil
    const profilePics = [
      '/ProfilePic1.svg',
      '/ProfilePic2.svg',
      '/ProfilePic3.svg',
      '/ProfilePic4.svg',
      '/ProfilePic5.svg',
      '/ProfilePic6.svg',
    ];
    const randomPic = profilePics[Math.floor(Math.random() * profilePics.length)];

    const dataToSend = { ...data, name: fullName, profile_image_url: randomPic };
    try {
      const response = await registerUser(dataToSend);
      if (response.id) {
        toast.success('Cadastro realizado com sucesso!');
        router.push('/login');
      }
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Falha no cadastro. Tente novamente.');
    }
  };

  return (
    <div className="max-w-[480px]">
      <SignUpHeader />

      <form onSubmit={handleSubmit(onSubmit)} className="mt-28 w-full text-sm leading-6 text-neutral-500">
        <div className="w-full whitespace-nowrap">
          <div className="flex gap-5 items-center w-full">
            <div className="relative min-h-10 w-[180px]">
              <div className="box-border flex gap-2.5 items-center px-4 py-2 w-full bg-zinc-100">
                <input
                  type="text"
                  placeholder="Nome"
                  {...register('name')}
                  className="flex-1 bg-transparent outline-none text-zinc-900 text-sm"
                />
              </div>
              <div className="flex z-0 max-w-full bg-neutral-500 min-h-px w-[180px]" />
              {errors.name && <span className="text-red-500 text-xs mt-1 block">{errors.name.message}</span>}
            </div>
            <div className="relative min-h-10 min-w-60 w-[280px]">
              <div className="box-border flex gap-2.5 items-center px-4 py-2 w-full bg-zinc-100">
                <input
                  type="text"
                  placeholder="Sobrenome"
                  name="lastName"
                  className="flex-1 bg-transparent outline-none text-zinc-900 text-sm"
                />
              </div>
              <div className="flex z-0 max-w-full bg-neutral-500 min-h-px w-[280px]" />
            </div>
          </div>
          <div className="relative mt-6 w-full min-h-10">
            <div className="box-border flex gap-2.5 items-center px-4 py-2 w-full bg-zinc-100">
              <input
                type="email"
                placeholder="E-mail"
                {...register('email')}
                className="flex-1 bg-transparent outline-none text-zinc-900 text-sm"
              />
            </div>
            <div className="flex z-0 w-full bg-neutral-500 min-h-px" />
            {errors.email && <span className="text-red-500 text-xs mt-1 block">{errors.email.message}</span>}
          </div>
        </div>

        <div className="mt-14 w-full">
          <div className="relative w-full whitespace-nowrap min-h-10">
            <div className="box-border flex gap-2.5 items-center px-4 py-2 w-full bg-zinc-100">
              <input
                type={showPassword ? 'text' : 'password'}
                placeholder="Senha"
                {...register('password')}
                className="flex-1 bg-transparent outline-none text-zinc-900 text-sm"
              />
              <button
                type="button"
                tabIndex={-1}
                className="ml-2 text-xs text-zinc-600 hover:text-zinc-900 focus:outline-none"
                onClick={() => setShowPassword((v) => !v)}
                aria-label={showPassword ? 'Ocultar senha' : 'Mostrar senha'}
              >
                {showPassword ? 'Ocultar' : 'Mostrar'}
              </button>
            </div>
            <div className="flex z-0 w-full bg-neutral-500 min-h-px" />
            {errors.password && <span className="text-red-500 text-xs mt-1 block">{errors.password.message}</span>}
          </div>
          <div className="relative mt-6 w-full min-h-10">
            <div className="box-border flex gap-2.5 items-center px-4 py-2 w-full bg-zinc-100">
              <input
                type={showConfirmPassword ? 'text' : 'password'}
                placeholder="Confirmação da senha"
                {...register('confirm_password')}
                className="flex-1 bg-transparent outline-none text-zinc-900 text-sm"
              />
              <button
                type="button"
                tabIndex={-1}
                className="ml-2 text-xs text-zinc-600 hover:text-zinc-900 focus:outline-none"
                onClick={() => setShowConfirmPassword((v) => !v)}
                aria-label={showConfirmPassword ? 'Ocultar confirmação' : 'Mostrar confirmação'}
              >
                {showConfirmPassword ? 'Ocultar' : 'Mostrar'}
              </button>
            </div>
            <div className="flex z-0 w-full bg-neutral-500 min-h-px" />
            {errors.confirm_password && <span className="text-red-500 text-xs mt-1 block">{errors.confirm_password.message}</span>}
          </div>
          {/* <div className="relative mt-6 w-full min-h-10">
            <div className="box-border flex gap-2.5 items-center px-4 py-2 w-full bg-zinc-100">
              <input
                type="text"
                placeholder="URL da imagem de perfil (opcional)"
                {...register('profile_image_url')}
                className="flex-1 bg-transparent outline-none text-zinc-900 text-sm"
              />
            </div>
            <div className="flex z-0 w-full bg-neutral-500 min-h-px" />
          </div> */}
        </div>

        <div className="mt-28 w-full">
          <button
            type="submit"
            className="flex gap-2.5 items-center pt-3 pr-16 pb-4 pl-4 w-full text-base text-gray-200 bg-neutral-800 hover:bg-neutral-700 transition-colors"
          >
            <span className="self-stretch my-auto">Criar conta</span>
          </button>
        </div>
      </form>

      <AlternativeSignUpMethods />
    </div>
  );
}
