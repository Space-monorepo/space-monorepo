import { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Eye, EyeOff } from 'lucide-react';

export default function PasswordInput({ register, error }: any) {
  const [showPassword, setShowPassword] = useState(false);

  return (
    <div className="space-y-2 relative">
      <Input
        type={showPassword ? 'text' : 'password'}
        placeholder="Senha"
        {...register('password')}
      />
      <button
        type="button"
        className="absolute right-3 top-2.5 text-gray-500"
        onClick={() => setShowPassword((prev) => !prev)}
      >
        {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
      </button>
      {error && <span className="text-red-500 text-sm">{error.message}</span>}
    </div>
  );
}