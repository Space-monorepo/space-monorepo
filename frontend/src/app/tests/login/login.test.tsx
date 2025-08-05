import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import LoginPage from '../../web/pages/login/page';
import { useRouter } from 'next/navigation';
import Cookies from 'js-cookie';
import { toast } from 'react-toastify';
import { loginUser } from '@/app/api/src';

// Mocking next/navigation
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

// Mocking js-cookie
jest.mock('js-cookie', () => ({
  get: jest.fn(),
  set: jest.fn(),
  remove: jest.fn(),
}));

// Mocking react-toastify
jest.mock('react-toastify', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

// Mocking @/app/api/src
jest.mock('@/app/api/src', () => ({
  loginUser: jest.fn(),
}));

// Mocking @/app/api/src/hooks/useBypassAuth
jest.mock('@/app/api/src/hooks/useBypassAuth', () => ({
  useBypassAuth: jest.fn(() => false), // Default to not bypassing auth
}));

describe('LoginPage', () => {
  let mockRouterPush: jest.Mock;

  beforeEach(() => {
    mockRouterPush = jest.fn();
    (useRouter as jest.Mock).mockReturnValue({ push: mockRouterPush });
    (Cookies.get as jest.Mock).mockReturnValue(null); // No token by default
    (loginUser as jest.Mock).mockClear();
    (toast.success as jest.Mock).mockClear();
    (toast.error as jest.Mock).mockClear();
  });

  it('deve renderizar o formulário de login', () => {
    render(<LoginPage />);
    expect(screen.getByPlaceholderText(/m.example@email.com/i)).toBeInTheDocument(); // Alterado aqui
    expect(screen.getByPlaceholderText(/^senha$/i)).toBeInTheDocument(); // Alterado aqui
    expect(screen.getByRole('button', { name: /entrar/i })).toBeInTheDocument();
  });

  it('deve redirecionar para /home se já existir um token válido', async () => {
    (Cookies.get as jest.Mock).mockReturnValue('fake-token');
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({}),
      })
    ) as jest.Mock;

    render(<LoginPage />);

    await waitFor(() => {
      expect(mockRouterPush).toHaveBeenCalledWith('/home');
    });
  });

  it('deve remover o token e mostrar erro se o token existente for inválido', async () => {
    (Cookies.get as jest.Mock).mockReturnValue('invalid-token');
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: false,
      })
    ) as jest.Mock;

    render(<LoginPage />);

    await waitFor(() => {
      expect(Cookies.remove).toHaveBeenCalledWith('token');
      expect(toast.error).toHaveBeenCalledWith('Sua sessão expirou. Por favor, faça login novamente.');
      expect(mockRouterPush).not.toHaveBeenCalled();
    });
  });

  it('deve chamar loginUser e redirecionar em caso de login bem-sucedido', async () => {
    (loginUser as jest.Mock).mockResolvedValue({ token: 'new-fake-token' });
    render(<LoginPage />);

    await userEvent.type(screen.getByPlaceholderText(/m.example@email.com/i), 'test@example.com');
    await userEvent.type(screen.getByPlaceholderText(/^senha$/i), 'password123456789'); // Alterado aqui
    await userEvent.click(screen.getByRole('button', { name: /entrar/i }));

    await waitFor(() => {
      expect(loginUser).toHaveBeenCalledWith(expect.any(FormData));
      const formData = (loginUser as jest.Mock).mock.calls[0][0] as FormData;
      expect(formData.get('username')).toBe('test@example.com');
      expect(formData.get('password')).toBe('password123456789'); 
      expect(Cookies.set).toHaveBeenCalledWith('token', 'new-fake-token', expect.any(Object)); // Alterado aqui
      expect(toast.success).toHaveBeenCalledWith('Login realizado com sucesso!');
      expect(mockRouterPush).toHaveBeenCalledWith('/home');
    });
  });

  it('deve mostrar mensagem de erro se loginUser falhar', async () => {
    const errorMessage = 'Credenciais inválidas';
    (loginUser as jest.Mock).mockRejectedValue(new Error(errorMessage));
    render(<LoginPage />);

    await userEvent.type(screen.getByPlaceholderText(/m.example@email.com/i), 'wrong@example.com');
    await userEvent.type(screen.getByPlaceholderText(/^senha$/i), 'wrongpassword12345'); // Alterado aqui
    await userEvent.click(screen.getByRole('button', { name: /entrar/i }));

    await waitFor(() => {
      expect(loginUser).toHaveBeenCalledTimes(1);
      expect(toast.error).toHaveBeenCalledWith(errorMessage);
      expect(mockRouterPush).not.toHaveBeenCalled();
    });
  });

  it('deve mostrar mensagem de erro se o token não for encontrado na resposta', async () => {
    (loginUser as jest.Mock).mockResolvedValue({}); // No token in response
    render(<LoginPage />);

    await userEvent.type(screen.getByPlaceholderText(/m.example@email.com/i), 'test@example.com');
    await userEvent.type(screen.getByPlaceholderText(/^senha$/i), 'password123456789'); // Alterado aqui
    await userEvent.click(screen.getByRole('button', { name: /entrar/i }));

    await waitFor(() => {
      expect(loginUser).toHaveBeenCalledTimes(1);
      expect(toast.error).toHaveBeenCalledWith('Token não encontrado na resposta do servidor');
      expect(mockRouterPush).not.toHaveBeenCalled();
    });
  });

  it('deve renderizar botões de login social', () => {
    render(<LoginPage />);
    expect(screen.getByRole('button', { name: /google/i })).toBeInTheDocument();
    // Adicione expect para outros botões de login social se houver
  });
});
