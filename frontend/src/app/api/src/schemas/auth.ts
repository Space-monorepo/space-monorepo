import { z } from 'zod';


export const loginSchema = z.object({
  email: z.string().email('Endereço de e-mail inválido'),
  password: z.string().min(15, 'A senha deve ter pelo menos 15 caracteres'), 
});


export const registerSchema = z.object({
  email: z.string().email('Endereço de e-mail inválido'),
  name: z.string().min(1, 'O nome é obrigatório').max(255, 'O nome é muito longo'),
  password: z.string().min(15, 'A senha deve ter pelo menos 15 caracteres'), 
  confirm_password: z.string().min(15, 'A confirmação de senha deve ter pelo menos 15 caracteres'),
  profile_image_url: z.string().optional(), 
}).refine((data) => data.password === data.confirm_password, {
  message: 'As senhas não coincidem',
  path: ['confirm_password'],
});

export type LoginFormData = z.infer<typeof loginSchema>;
export type RegisterFormData = z.infer<typeof registerSchema>;