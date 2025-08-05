import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { loginSchema, LoginFormData } from '@/app/api/src/schemas/auth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import PasswordInput from './PasswordInput';

export default function LoginForm({ onSubmit }: { onSubmit: (data: LoginFormData) => void }) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="space-y-2">
        <Input type="email" placeholder="m.example@email.com" {...register('email')} />
        {errors.email && <span className="text-red-500 text-sm">{errors.email.message}</span>}
      </div>

      <PasswordInput register={register} error={errors.password} />

      <Button type="submit" className="w-full text-white bg-black hover:bg-black/90">
        Entrar
      </Button>
    </form>
  );
}