import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ModalComplaint } from '@/components/modals/posts/ModalComplaint';
import usePostActions from '@/app/api/src/hooks/post/usePostActions';
import { toast } from 'react-toastify';

// Guardar referências para os callbacks passados para usePostActions
let capturedOnSuccess: (() => void) | undefined;
let capturedOnError: ((error: Error) => void) | undefined; // Alterado de any para Error

// O jest.fn() que o componente efetivamente chamará
const mockCreateCampaignAction = jest.fn<Promise<object>, [object]>(); // Tipagem adicionada

jest.mock('@/app/api/src/hooks/post/usePostActions', () => jest.fn(
  (options: { onSuccess?: () => void; onError?: (error: Error) => void }) => { // Alterado de any para Error
    capturedOnSuccess = options.onSuccess;
    capturedOnError = options.onError;
    return {
      createCampaign: mockCreateCampaignAction, // Usar a mesma função mockada, assumindo que a ação é similar
    };
  }
));

jest.mock('react-toastify', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

describe('ModalComplaint', () => {
  const mockOnClose = jest.fn();
  // const communityId = 'test-community-id'; // Remover se não for usado por ModalComplaint

  beforeEach(() => {
    // Resetar mocks
    mockCreateCampaignAction.mockReset();
    (usePostActions as jest.Mock).mockClear();
    mockOnClose.mockReset();
    (toast.success as jest.Mock).mockReset();
    (toast.error as jest.Mock).mockReset();
    capturedOnSuccess = undefined;
    capturedOnError = undefined;

    global.alert = jest.fn();
  });

  test('deve enviar a denúncia com sucesso', async () => {
    mockCreateCampaignAction.mockImplementation(async () => {
      if (capturedOnSuccess) {
        capturedOnSuccess();
      }
      return Promise.resolve({});
    });

    render(<ModalComplaint onClose={mockOnClose} />);

    // Etapa 1: Definir o título
    const titleInput = screen.getByLabelText('Título da campanha');
    fireEvent.change(titleInput, { target: { value: 'Título da Denúncia de Teste' } });
    fireEvent.click(screen.getByRole('button', { name: 'Avançar para a próxima etapa' }));

    // Etapa 2: Escrever a publicação
    // O textarea de conteúdo tem aria-label="Conteúdo da publicação"
    const contentInput = screen.getByLabelText('Conteúdo da publicação');
    fireEvent.change(contentInput, { target: { value: 'Conteúdo da denúncia de teste.' } });

    // O botão na segunda etapa ainda tem o texto "Avançar para a próxima etapa" em ModalComplaint
    const completeButton = screen.getByRole('button', { name: 'Avançar para a próxima etapa' });
    fireEvent.click(completeButton);

    await waitFor(() => {
      expect(mockCreateCampaignAction).toHaveBeenCalledWith({
        title: 'Título da Denúncia de Teste',
        content: 'Conteúdo da denúncia de teste.',
        files: [], // Assumindo que 'files' faz parte do payload
        // community_id: communityId, // Remover se não aplicável
      });
    });

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith('Denúncia criada com sucesso!');
    });

    await waitFor(() => {
      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });
  });

  test('deve mostrar alerta se o título estiver vazio na primeira etapa', () => {
    render(<ModalComplaint onClose={mockOnClose} />);
    fireEvent.click(screen.getByRole('button', { name: 'Avançar para a próxima etapa' }));
    expect(global.alert).toHaveBeenCalledWith('Por favor, insira um título para a campanha'); // Corrigido
  });

  test('deve mostrar alerta se o conteúdo estiver vazio na segunda etapa', async () => {
    render(<ModalComplaint onClose={mockOnClose} />);
    fireEvent.change(screen.getByLabelText('Título da campanha'), { target: { value: 'Título Qualquer' } });
    fireEvent.click(screen.getByRole('button', { name: 'Avançar para a próxima etapa' }));

    // Esperar a transição de etapa e a aparição do campo de conteúdo
    // O textarea de conteúdo tem aria-label="Conteúdo da publicação"
    await screen.findByLabelText('Conteúdo da publicação');

    const completeButton = screen.getByRole('button', { name: 'Avançar para a próxima etapa' });
    fireEvent.click(completeButton);

    // A mensagem de alerta pode ser diferente
    expect(global.alert).toHaveBeenCalledWith('Por favor, insira o conteúdo da publicação'); 
    expect(mockCreateCampaignAction).not.toHaveBeenCalled();
    expect(mockOnClose).not.toHaveBeenCalled();
  });

  test('deve chamar onClose ao clicar no botão de fechar', () => {
    render(<ModalComplaint onClose={mockOnClose} />);

    const closeButton = screen.getByRole('button', { name: '×' });
    fireEvent.click(closeButton);

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  test('deve voltar para etapas anteriores', async () => {
    render(<ModalComplaint onClose={mockOnClose} />);

    const titleInput = screen.getByLabelText('Título da campanha');
    fireEvent.change(titleInput, { target: { value: 'Título para Teste de Voltar' } });
    fireEvent.click(screen.getByRole('button', { name: 'Avançar para a próxima etapa' }));

    // Esperar a transição de etapa e a aparição do campo de conteúdo
    // O textarea de conteúdo tem aria-label="Conteúdo da publicação"
    await screen.findByLabelText('Conteúdo da publicação');
    expect(screen.queryByLabelText('Conteúdo da publicação')).not.toBeNull(); // Corrigido

    const backButton = screen.getByRole('button', { name: 'Voltar para a etapa anterior' });
    fireEvent.click(backButton);

    expect(screen.queryByLabelText('Título da campanha')).not.toBeNull();
    expect(screen.queryByLabelText('Conteúdo da denúncia')).toBeNull();
  });

  test('deve lidar com erro na criação da denúncia', async () => {
    const errorMessage = 'Falha ao criar denúncia';
    mockCreateCampaignAction.mockImplementation(async () => {
      const error = new Error(errorMessage);
      if (capturedOnError) {
        capturedOnError(error);
      }
      return Promise.reject(error);
    });

    render(<ModalComplaint onClose={mockOnClose} />);

    fireEvent.change(screen.getByLabelText('Título da campanha'), { target: { value: 'Título Errado' } });
    fireEvent.click(screen.getByRole('button', { name: 'Avançar para a próxima etapa' }));

    // Esperar a transição de etapa e a aparição do campo de conteúdo
    // O textarea de conteúdo tem aria-label="Conteúdo da publicação"
    await screen.findByLabelText('Conteúdo da publicação');

    fireEvent.change(screen.getByLabelText('Conteúdo da publicação'), { target: { value: 'Conteúdo Errado' } }); // Corrigido
    // O botão na segunda etapa ainda tem o texto "Avançar para a próxima etapa" em ModalComplaint
    fireEvent.click(screen.getByRole('button', { name: 'Avançar para a próxima etapa' }));

    await waitFor(() => {
      expect(mockCreateCampaignAction).toHaveBeenCalledTimes(1);
    });
    
    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith(errorMessage);
    });

    expect(mockOnClose).not.toHaveBeenCalled();
  });
});
