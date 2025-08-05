import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ModalAnnouncement } from '@/components/modals/posts/ModalAnnouncement';
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
      createCampaign: mockCreateCampaignAction,
    };
  }
));

jest.mock('react-toastify', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

describe('ModalAnnouncement', () => {
  const mockOnClose = jest.fn();

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

  test('deve enviar o anúncio com sucesso', async () => {
    mockCreateCampaignAction.mockImplementation(async () => {
      if (capturedOnSuccess) {
        capturedOnSuccess();
      }
      return Promise.resolve({});
    });

    render(<ModalAnnouncement onClose={mockOnClose} />);

    // Etapa 1: Definir o título
    const titleInput = screen.getByLabelText('Título da campanha');
    fireEvent.change(titleInput, { target: { value: 'Título do Anúncio de Teste' } });

    const nextButtonStep1 = screen.getByRole('button', { name: 'Avançar para a próxima etapa' });
    fireEvent.click(nextButtonStep1);
    
    // Etapa 2: Definir o conteúdo
    // Esperar a transição de etapa e a aparição do campo de conteúdo
    const contentInput = await screen.findByLabelText('Conteúdo da publicação');
    fireEvent.change(contentInput, { target: { value: 'Conteúdo do anúncio de teste.' } });

    const completeButton = screen.getByRole('button', { name: 'Avançar para a próxima etapa' });
    fireEvent.click(completeButton);

    await waitFor(() => {
      expect(mockCreateCampaignAction).toHaveBeenCalledWith({
        title: 'Título do Anúncio de Teste',
        content: 'Conteúdo do anúncio de teste.',
        files: [], // Assumindo que 'files' faz parte do payload
      });
    });

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith('Anúncio criado com sucesso!');
    });

    await waitFor(() => {
      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });
  });

  test('deve mostrar alerta se o título estiver vazio na primeira etapa', () => {
    render(<ModalAnnouncement onClose={mockOnClose} />);
    
    const nextButton = screen.getByRole('button', { name: 'Avançar para a próxima etapa' });
    fireEvent.click(nextButton);

    expect(global.alert).toHaveBeenCalledWith('Por favor, insira um título para a anúncio'); 
    expect(mockCreateCampaignAction).not.toHaveBeenCalled();
    expect(mockOnClose).not.toHaveBeenCalled();
  });

  test('deve mostrar alerta se o conteúdo estiver vazio na segunda etapa', async () => {
    render(<ModalAnnouncement onClose={mockOnClose} />);
    fireEvent.change(screen.getByLabelText('Título da campanha'), { target: { value: 'Título Qualquer' } });
    fireEvent.click(screen.getByRole('button', { name: 'Avançar para a próxima etapa' }));

    await screen.findByLabelText('Conteúdo da publicação'); // Espera a próxima etapa

    // O botão de avançar/concluir na segunda etapa.
    // O texto do botão muda para "Concluir", mas o aria-label é "Avançar para a próxima etapa"
    const completeButton = screen.getByRole('button', { name: 'Avançar para a próxima etapa' });
    fireEvent.click(completeButton);

    expect(global.alert).toHaveBeenCalledWith('Por favor, insira o conteúdo da publicação');
  });

  test('deve chamar onClose ao clicar no botão de fechar', () => {
    render(<ModalAnnouncement onClose={mockOnClose} />);

    const closeButton = screen.getByRole('button', { name: '×' });
    fireEvent.click(closeButton);

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  test('deve voltar para a primeira etapa ao clicar em Voltar', async () => {
    render(<ModalAnnouncement onClose={mockOnClose} />);

    const titleInput = screen.getByLabelText('Título da campanha');
    fireEvent.change(titleInput, { target: { value: 'Título para Teste de Voltar' } });
    
    const nextButtonStep1 = screen.getByRole('button', { name: 'Avançar para a próxima etapa' });
    fireEvent.click(nextButtonStep1);

    // Esperar a transição de etapa e a aparição do campo de conteúdo
    await screen.findByLabelText('Conteúdo da publicação');
    expect(screen.queryByLabelText('Conteúdo da publicação')).not.toBeNull();

    const backButton = screen.getByRole('button', { name: 'Voltar para a etapa anterior' });
    fireEvent.click(backButton);

    // Esperar a transição de etapa e a aparição do campo de título
    await screen.findByLabelText('Título da campanha');
    expect(screen.queryByLabelText('Título da campanha')).not.toBeNull();
    expect(screen.queryByLabelText('Conteúdo da publicação')).toBeNull();
  });

   test('deve lidar com erro na criação do anúncio', async () => {
    const errorMessage = 'Falha ao criar anúncio';
    mockCreateCampaignAction.mockImplementation(async () => {
      const error = new Error(errorMessage);
      if (capturedOnError) {
        capturedOnError(error);
      }
      return Promise.reject(error);
    });

    render(<ModalAnnouncement onClose={mockOnClose} />);

    fireEvent.change(screen.getByLabelText('Título da campanha'), { target: { value: 'Título Errado' } });
    fireEvent.click(screen.getByRole('button', { name: 'Avançar para a próxima etapa' }));
    
    // Esperar a transição de etapa
    await screen.findByLabelText('Conteúdo da publicação');
    // O texto do botão muda para "Concluir", mas o aria-label é "Avançar para a próxima etapa"
    const completeButton = screen.getByRole('button', { name: 'Avançar para a próxima etapa' });

    fireEvent.change(screen.getByLabelText('Conteúdo da publicação'), { target: { value: 'Conteúdo Errado' } });
    fireEvent.click(completeButton);

    await waitFor(() => {
      expect(mockCreateCampaignAction).toHaveBeenCalledTimes(1);
    });
    
    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith(errorMessage);
    });

    expect(mockOnClose).not.toHaveBeenCalled();
  });
});
