import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { loginSchema, LoginFormData } from '@/app/api/src/schemas/auth';
import { Button } from '@/components/ui/button';
import { useState } from 'react';

export default function LoginForm({ onSubmit }: { onSubmit: (data: LoginFormData) => void }) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const [showPassword, setShowPassword] = useState(false);

  return (
    <form className="flex flex-col gap-6 items-start w-full min-w-0" onSubmit={handleSubmit(onSubmit)} autoComplete="on">
      {/* Campo oculto para ajudar o navegador a identificar login */}
      <input type="text" name="username" autoComplete="username" style={{ display: 'none' }} tabIndex={-1} />
      <div className="flex flex-col items-start w-full">
        <div className="box-border flex gap-2.5 items-center px-4 py-2 w-full bg-zinc-100">
          <input
            id="email"
            type="email"
            placeholder="Email"
            autoComplete="email"
            className="flex-1 bg-transparent outline-none text-zinc-900 text-sm"
            {...register('email')}
            disabled={isSubmitting}
          />
        </div>
        <div className="w-full h-px bg-neutral-500" />
        {errors.email && <span className="text-red-500 text-xs px-4 pt-1">{errors.email.message}</span>}
      </div>
      <div className="flex flex-col items-start w-full">
        <div className="box-border flex gap-2.5 items-center px-4 py-2 w-full bg-zinc-100">
          <input
            id="password"
            type={showPassword ? 'text' : 'password'}
            placeholder='Senha'
            autoComplete="current-password"
            className="flex-1 bg-transparent outline-none text-zinc-900 text-sm"
            {...register('password')}
            disabled={isSubmitting}
          />
          <button
            type="button"
            tabIndex={-1}
            className="ml-2 cursor-pointer text-xs text-zinc-600 hover:text-zinc-900 focus:outline-none"
            onClick={() => setShowPassword((v) => !v)}
            aria-label={showPassword ? 'Ocultar senha' : 'Mostrar senha'}
            disabled={isSubmitting}
          >
            {showPassword ? 'Ocultar' : 'Mostrar'}
          </button>
        </div>
        <div className="w-full h-px bg-neutral-500" />
        {errors.password && <span className="text-red-500 text-xs px-4 pt-1">{errors.password.message}</span>}
      </div>
      <Button
        type="submit"
        className="box-border cursor-pointer mt-20 font-normal flex gap-2.5 items-center px-4 pt-3 pb-4 w-full justify-start bg-neutral-800 hover:bg-neutral-900 transition-colors rounded-none"
        disabled={isSubmitting}
      >
        <div className="text-base leading-6 text-gray-200">
          <div className="text-base text-gray-200">{isSubmitting ? 'Entrando...' : 'Entrar'}</div>
        </div>
      </Button>
    </form>
  );
}