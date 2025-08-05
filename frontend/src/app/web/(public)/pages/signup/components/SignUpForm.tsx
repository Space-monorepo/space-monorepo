import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { registerSchema, RegisterFormData } from '@/app/api/src/schemas/auth';
import { useRouter } from 'next/navigation';
import { registerUser } from '@/app/api/src';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import SignUpHeader from './SignUpHeader';
import AlternativeSignUpMethods from './AlternativeSignUpMethods';

export default function SignUpForm() {
  const router = useRouter();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterFormData) => {
    try {
      const response = await registerUser(data);
      if (response.id) {
        alert('Cadastro realizado com sucesso!');
        router.push('/login');
      }
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Falha no cadastro. Tente novamente.');
    }
  };

  return (
    <>
      <SignUpHeader />
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="space-y-2">
          <Input type="text" placeholder="Nome completo" {...register('name')} />
          {errors.name && <span className="text-red-500 text-sm">{errors.name.message}</span>}
        </div>
        <div className="space-y-2">
          <Input type="email" placeholder="m.example@email.com" {...register('email')} />
          {errors.email && <span className="text-red-500 text-sm">{errors.email.message}</span>}
        </div>
        <div className="space-y-2">
          <Input type="password" placeholder="Senha" {...register('password')} />
          {errors.password && <span className="text-red-500 text-sm">{errors.password.message}</span>}
        </div>
        <div className="space-y-2">
          <Input type="password" placeholder="Confirmação da senha" {...register('confirm_password')} />
          {errors.confirm_password && <span className="text-red-500 text-sm">{errors.confirm_password.message}</span>}
        </div>
        <div className="space-y-2">
          <Input type="text" placeholder="URL da imagem de perfil (opcional)" {...register('profile_image_url')} />
        </div>
        <Button type="submit" className="w-full text-white bg-black hover:bg-black/90">
          Criar conta
        </Button>
      </form>
      <AlternativeSignUpMethods />
    </>
  );
}