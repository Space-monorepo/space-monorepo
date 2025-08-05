import { z } from 'zod';


export const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(15, 'Password must be at least 15 characters'), 
});


export const registerSchema = z.object({
  email: z.string().email('Invalid email address'),
  name: z.string().min(1, 'Name is required').max(255, 'Name is too long'),
  password: z.string().min(15, 'Password must be at least 15 characters'), 
  confirm_password: z.string().min(15, 'Confirm password must be at least 15 characters'),
  profile_image_url: z.string().optional(), 
}).refine((data) => data.password === data.confirm_password, {
  message: 'Passwords do not match',
  path: ['confirm_password'],
});

export type LoginFormData = z.infer<typeof loginSchema>;
export type RegisterFormData = z.infer<typeof registerSchema>;