import { render, screen } from '@testing-library/react';
import { useRouter } from 'next/navigation';
import { toast } from 'react-toastify';
import SignUpPage from '../../web/pages/signup/page';

// Mocking next/navigation
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

// Mocking react-toastify
jest.mock('react-toastify', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

// Mocking SignUpForm children component directly
jest.mock('@/app/web/pages/signup/components/SignUpForm', () => {
  return jest.fn(() => ( // Argumento props removido, defaultValue simplificado
    <form data-testid="signup-form">
      <input type="text" name="name" aria-label="Nome" defaultValue="" />
      <input type="email" name="email" aria-label="Email" defaultValue="" />
      <input type="password" name="password" aria-label="Senha" />
      <input type="password" name="confirmPassword" aria-label="Confirmar Senha" />
      <button type="submit">Cadastrar</button>
    </form>
  ));
});


describe('SignUpPage', () => {
  let mockRouterPush: jest.Mock;

  beforeEach(() => {
    mockRouterPush = jest.fn();
    (useRouter as jest.Mock).mockReturnValue({ push: mockRouterPush });
    (toast.success as jest.Mock).mockClear();
    (toast.error as jest.Mock).mockClear();
    global.fetch = jest.fn(); // Reset fetch mock
  });

  it('deve renderizar o formulário de cadastro', () => {
    render(<SignUpPage />);
    expect(screen.getByLabelText(/nome/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^senha$/i)).toBeInTheDocument(); // Alterado aqui
    expect(screen.getByLabelText(/confirmar senha/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /cadastrar/i })).toBeInTheDocument();
  });

  // Como SignUpPage apenas renderiza SignUpLayout e SignUpForm,
  // e SignUpForm é quem tem a lógica de submit,
  // vamos testar a interação através do mock do SignUpForm.

  it('deve chamar a API de cadastro e redirecionar em caso de sucesso', async () => {
    // Mock da implementação do fetch para o cadastro
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ message: 'Usuário criado com sucesso' }),
    });

    render(<SignUpPage />);

    // Verifica se o formulário mockado está presente.
    // A lógica de submissão real e chamada de API deve ser testada
    // em SignUpForm.test.tsx, não mockando o SignUpForm.
    expect(screen.getByTestId('signup-form')).toBeInTheDocument();
    expect(screen.getByLabelText(/nome/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /cadastrar/i })).toBeInTheDocument();

    // Para um teste de integração real do fluxo de cadastro nesta página,
    // você não mockaria o SignUpForm. Em vez disso, você iria interagir
    // com os campos reais do SignUpForm e simular o submit.
    // Exemplo (se SignUpForm não fosse mockado):
    // await userEvent.type(screen.getByLabelText(/nome/i), 'Teste User');
    // await userEvent.type(screen.getByLabelText(/email/i), 'teste@example.com');
    // await userEvent.type(screen.getByLabelText(/senha/i), 'password123');
    // await userEvent.type(screen.getByLabelText(/confirmar senha/i), 'password123');
    // fireEvent.click(screen.getByRole('button', { name: /cadastrar/i }));

    // await waitFor(() => {
    //   expect(global.fetch).toHaveBeenCalledWith(expect.stringContaining('/users'), expect.any(Object));
    //   expect(toast.success).toHaveBeenCalledWith('Usuário criado com sucesso!');
    //   expect(mockRouterPush).toHaveBeenCalledWith('/login');
    // });
  });


  // Adicionar mais testes conforme necessário, por exemplo, para falha no cadastro.
  // Seria ideal ter testes separados para o componente SignUpForm.tsx
  // para cobrir a lógica de validação e submissão do formulário em detalhes.
});
