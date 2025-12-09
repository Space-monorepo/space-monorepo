import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ModalPoll } from '@/components/modals/posts/ModalPoll';
import usePostActions from '@/app/api/src/hooks/post/usePostActions';
import { toast } from 'react-toastify';

// Guardar referências para os callbacks passados para usePostActions
let capturedOnSuccess: (() => void) | undefined;
let capturedOnError: ((error: Error) => void) | undefined; // Alterado de any para Error

// Mock para a ação createPoll - Definido no escopo do describe para ser consistente
const mockCreatePoll = jest.fn<Promise<object>, [unknown]>();

jest.mock('@/app/api/src/hooks/post/usePostActions', () => jest.fn(
  (options: { onSuccess?: () => void; onError?: (error: Error) => void }) => { // Alterado de any para Error
    capturedOnSuccess = options.onSuccess;
    capturedOnError = options.onError;
    return {
      createPoll: mockCreatePoll, // Usar o mockCreatePoll consistentemente
    };
  }
));

jest.mock('react-toastify', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

describe('ModalPoll', () => {
  const mockOnClose = jest.fn();
  const communityId = 'test-community-id'; // Adicionado communityId

  beforeEach(() => {
    // Resetar mocks
    mockCreatePoll.mockReset(); // Usar mockCreatePoll
    (usePostActions as jest.Mock).mockClear();
    mockOnClose.mockReset();
    (toast.success as jest.Mock).mockReset();
    (toast.error as jest.Mock).mockReset();
    capturedOnSuccess = undefined;
    capturedOnError = undefined;

    global.alert = jest.fn();
  });

  test('deve enviar a enquete com sucesso', async () => {
    mockCreatePoll.mockImplementation(async () => { // Usar mockCreatePoll
      if (capturedOnSuccess) {
        capturedOnSuccess();
      }
      return Promise.resolve({});
    });

    render(<ModalPoll onClose={mockOnClose} communityId={communityId} />); // Adicionado communityId

    // Etapa 1: Definir o título
    // O input de título em ModalPoll tem aria-label="Título da campanha" mas o label é "Título da enquete"
    const titleInput = screen.getByLabelText('Título da campanha');
    fireEvent.change(titleInput, { target: { value: 'Título da Enquete de Teste' } });
    fireEvent.click(screen.getByRole('button', { name: 'Avançar para a próxima etapa' }));

    // Etapa 2: Escrever a publicação
    // Esperar a transição de etapa
    await screen.findByLabelText('Conteúdo da publicação');
    const contentInput = screen.getByLabelText('Conteúdo da publicação');
    fireEvent.change(contentInput, { target: { value: 'Conteúdo da enquete de teste.' } });
    fireEvent.click(screen.getByRole('button', { name: 'Avançar para a próxima etapa' }));

    // Etapa 3: Definir opções da enquete
    // Esperar a transição de etapa
    await screen.findByPlaceholderText('Qual sua pergunta?');
    const questionInput = screen.getByPlaceholderText('Qual sua pergunta?');
    fireEvent.change(questionInput, { target: { value: 'Qual sua opção favorita?' } });

    const optionInputs = screen.getAllByPlaceholderText(/Opção \d+/);
    fireEvent.change(optionInputs[0], { target: { value: 'Opção A' } });
    fireEvent.change(optionInputs[1], { target: { value: 'Opção B' } });

    // O botão de concluir na terceira etapa.
    // O texto do botão muda para "Concluir", mas o aria-label permanece "Avançar para a próxima etapa"
    const completeButton = screen.getByRole('button', { name: 'Avançar para a próxima etapa' });
    fireEvent.click(completeButton);

    await waitFor(() => {
      expect(mockCreatePoll).toHaveBeenCalledWith(expect.objectContaining({ // Usar mockCreatePoll e expect.objectContaining
        title: 'Título da Enquete de Teste',
        content: 'Conteúdo da enquete de teste.',
        files: [],
        pollQuestion: 'Qual sua opção favorita?',
        pollOptions: ['Opção A', 'Opção B'],
        community_id: communityId,
        status: 'active',
      })); // Fechar expect.objectContaining corretamente
    });

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith('Enquete criada com sucesso!');
    });

    await waitFor(() => {
      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });
  });

  test('deve mostrar alerta se o título estiver vazio na primeira etapa', () => {
    render(<ModalPoll onClose={mockOnClose} communityId={communityId} />); // Adicionado communityId
    fireEvent.click(screen.getByRole('button', { name: 'Avançar para a próxima etapa' }));
    expect(global.alert).toHaveBeenCalledWith('Por favor, insira um título para a enquete');
  });

  test('deve mostrar alerta se o conteúdo estiver vazio na segunda etapa', async () => {
    render(<ModalPoll onClose={mockOnClose} communityId={communityId} />); // Adicionado communityId
    fireEvent.change(screen.getByLabelText('Título da campanha'), { target: { value: 'Título Qualquer' } });
    fireEvent.click(screen.getByRole('button', { name: 'Avançar para a próxima etapa' }));
    
    await screen.findByLabelText('Conteúdo da publicação'); // Espera a próxima etapa
    fireEvent.click(screen.getByRole('button', { name: 'Avançar para a próxima etapa' }));
    expect(global.alert).toHaveBeenCalledWith('Por favor, insira o conteúdo da publicação');
  });

  test('deve mostrar alerta se a pergunta da enquete estiver vazia na terceira etapa', async () => {
    render(<ModalPoll onClose={mockOnClose} communityId={communityId} />); // Adicionado communityId
    fireEvent.change(screen.getByLabelText('Título da campanha'), { target: { value: 'Título' } });
    fireEvent.click(screen.getByRole('button', { name: 'Avançar para a próxima etapa' }));

    await screen.findByLabelText('Conteúdo da publicação');
    fireEvent.change(screen.getByLabelText('Conteúdo da publicação'), { target: { value: 'Conteúdo' } });
    fireEvent.click(screen.getByRole('button', { name: 'Avançar para a próxima etapa' }));

    await screen.findByPlaceholderText('Qual sua pergunta?');
    const optionInputs = screen.getAllByPlaceholderText(/Opção \d+/);
    fireEvent.change(optionInputs[0], { target: { value: 'Opção A' } });
    fireEvent.change(optionInputs[1], { target: { value: 'Opção B' } });

    const completeButton = screen.getByRole('button', { name: 'Avançar para a próxima etapa' });
    fireEvent.click(completeButton);
    expect(global.alert).toHaveBeenCalledWith('Por favor, insira a pergunta da enquete');
  });

  test('deve mostrar alerta se alguma opção da enquete estiver vazia na terceira etapa', async () => {
    render(<ModalPoll onClose={mockOnClose} communityId={communityId} />); // Adicionado communityId
    fireEvent.change(screen.getByLabelText('Título da campanha'), { target: { value: 'Título' } });
    fireEvent.click(screen.getByRole('button', { name: 'Avançar para a próxima etapa' }));

    await screen.findByLabelText('Conteúdo da publicação');
    fireEvent.change(screen.getByLabelText('Conteúdo da publicação'), { target: { value: 'Conteúdo' } });
    fireEvent.click(screen.getByRole('button', { name: 'Avançar para a próxima etapa' }));

    await screen.findByPlaceholderText('Qual sua pergunta?');
    fireEvent.change(screen.getByPlaceholderText('Qual sua pergunta?'), { target: { value: 'Pergunta?' } });
    const optionInputs = screen.getAllByPlaceholderText(/Opção \d+/);
    fireEvent.change(optionInputs[0], { target: { value: '' } }); // Opção vazia
    fireEvent.change(optionInputs[1], { target: { value: 'Opção B' } });

    const completeButton = screen.getByRole('button', { name: 'Avançar para a próxima etapa' });
    fireEvent.click(completeButton);
    expect(global.alert).toHaveBeenCalledWith('Por favor, preencha todas as opções da enquete');
  });

  test('deve adicionar e remover opções da enquete', async () => {
    render(<ModalPoll onClose={mockOnClose} communityId={communityId} />); // Adicionado communityId
    fireEvent.change(screen.getByLabelText('Título da campanha'), { target: { value: 'Título' } });
    fireEvent.click(screen.getByRole('button', { name: 'Avançar para a próxima etapa' }));
    await screen.findByLabelText('Conteúdo da publicação');
    fireEvent.change(screen.getByLabelText('Conteúdo da publicação'), { target: { value: 'Conteúdo' } });
    fireEvent.click(screen.getByRole('button', { name: 'Avançar para a próxima etapa' }));

    await screen.findByPlaceholderText('Qual sua pergunta?');
    let optionInputs = screen.getAllByPlaceholderText(/Opção \d+/);
    expect(optionInputs.length).toBe(2); // Começa com 2 opções

    const addOptionButton = screen.getByRole('button', { name: 'Adicionar opção' });
    fireEvent.click(addOptionButton);

    optionInputs = screen.getAllByPlaceholderText(/Opção \d+/);
    expect(optionInputs.length).toBe(3);
    fireEvent.change(optionInputs[2], { target: { value: 'Nova Opção' } });

    const removeButtons = screen.getAllByRole('button', { name: 'Remover' });
    fireEvent.click(removeButtons[0]); // Remove a primeira opção

    optionInputs = screen.getAllByPlaceholderText(/Opção \d+/);
    expect(optionInputs.length).toBe(2);
    // Verifica se a opção correta foi removida e a nova opção ainda existe
    expect(screen.getByDisplayValue('Nova Opção')).not.toBeNull();
  });


  test('deve chamar onClose ao clicar no botão de fechar', () => {
    render(<ModalPoll onClose={mockOnClose} communityId={communityId} />); // Adicionado communityId
    const closeButton = screen.getByRole('button', { name: '×' });
    fireEvent.click(closeButton);
    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  test('deve voltar para etapas anteriores ao clicar em Voltar', async () => {
    render(<ModalPoll onClose={mockOnClose} communityId={communityId} />); // Adicionado communityId
    // Etapa 1 -> Etapa 2
    fireEvent.change(screen.getByLabelText('Título da campanha'), { target: { value: 'Título' } });
    fireEvent.click(screen.getByRole('button', { name: 'Avançar para a próxima etapa' }));
    await screen.findByLabelText('Conteúdo da publicação');

    // Etapa 2 -> Etapa 3
    fireEvent.change(screen.getByLabelText('Conteúdo da publicação'), { target: { value: 'Conteúdo' } });
    fireEvent.click(screen.getByRole('button', { name: 'Avançar para a próxima etapa' }));
    await screen.findByPlaceholderText('Qual sua pergunta?');
    expect(screen.getByPlaceholderText('Qual sua pergunta?')).not.toBeNull();

    // Voltar: Etapa 3 -> Etapa 2
    const backButton = screen.getByRole('button', { name: 'Voltar para a etapa anterior' });
    fireEvent.click(backButton);
    await screen.findByLabelText('Conteúdo da publicação');
    expect(screen.getByLabelText('Conteúdo da publicação')).not.toBeNull();
    expect(screen.queryByPlaceholderText('Qual sua pergunta?')).toBeNull();

    // Voltar: Etapa 2 -> Etapa 1
    fireEvent.click(backButton); // O botão de voltar ainda deve estar acessível
    await screen.findByLabelText('Título da campanha');
    expect(screen.getByLabelText('Título da campanha')).not.toBeNull();
    expect(screen.queryByLabelText('Conteúdo da publicação')).toBeNull();
  });

  test('deve lidar com erro na criação da enquete', async () => {
    const errorMessage = 'Falha ao criar enquete';
    // Configurar a implementação do mockCreatePoll (definido no escopo do describe)
    mockCreatePoll.mockImplementation(async () => {
      const error = new Error(errorMessage);
      if (capturedOnError) { // capturedOnError agora deve ser o correto
        capturedOnError(error);
      }
      return Promise.reject(error);
    });

    // Não sobrescrever usePostActions com mockReturnValue aqui
    // (usePostActions as jest.Mock).mockReturnValue({ createPoll: mockCreatePollAction }); // REMOVIDO

    render(<ModalPoll onClose={mockOnClose} communityId={communityId} />); // Adicionado communityId

    fireEvent.change(screen.getByLabelText('Título da campanha'), { target: { value: 'Título Errado' } });
    fireEvent.click(screen.getByRole('button', { name: 'Avançar para a próxima etapa' }));
    await screen.findByLabelText('Conteúdo da publicação');

    fireEvent.change(screen.getByLabelText('Conteúdo da publicação'), { target: { value: 'Conteúdo Errado' } });
    fireEvent.click(screen.getByRole('button', { name: 'Avançar para a próxima etapa' }));
    await screen.findByPlaceholderText('Qual sua pergunta?');

    fireEvent.change(screen.getByPlaceholderText('Qual sua pergunta?'), { target: { value: 'Pergunta Errada?' } });
    const optionInputs = screen.getAllByPlaceholderText(/Opção \d+/);
    fireEvent.change(optionInputs[0], { target: { value: 'Erro Opção A' } });
    fireEvent.change(optionInputs[1], { target: { value: 'Erro Opção B' } });
    
    const completeButton = screen.getByRole('button', { name: 'Avançar para a próxima etapa' });
    fireEvent.click(completeButton);

    await waitFor(() => {
      expect(mockCreatePoll).toHaveBeenCalledTimes(1); // Usar mockCreatePoll
    });
    
    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith(errorMessage);
    });

    expect(mockOnClose).not.toHaveBeenCalled();
  });
});
