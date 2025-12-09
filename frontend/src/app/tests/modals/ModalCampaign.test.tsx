import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ModalCampaign } from '@/components/modals/posts/ModalCampaign';
import usePostActions from '@/app/api/src/hooks/post/usePostActions'; // Importa o real para que o jest.mock funcione nele
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

describe('ModalCampaign', () => {
  const mockOnClose = jest.fn();
  const communityId = 'test-community-id';

  beforeEach(() => {
    // Resetar mocks
    mockCreateCampaignAction.mockReset();
    (usePostActions as jest.Mock).mockClear(); // Limpa o mock do hook em si
    mockOnClose.mockReset();
    (toast.success as jest.Mock).mockReset();
    (toast.error as jest.Mock).mockReset();
    capturedOnSuccess = undefined; // Limpa os callbacks capturados
    capturedOnError = undefined;

    global.alert = jest.fn();
  });

  test('deve enviar a campanha com sucesso', async () => {
    // Configurar o mockCreateCampaignAction para simular sucesso E chamar o onSuccess capturado
    mockCreateCampaignAction.mockImplementation(async () => { // data removido
      if (capturedOnSuccess) {
        capturedOnSuccess();
      }
      return Promise.resolve({}); // Sucesso da chamada de API (mockada)
    });

    render(<ModalCampaign onClose={mockOnClose} communityId={communityId} />);

    // Etapa 1: Definir o título
    const titleInput = screen.getByLabelText('Título da campanha');
    fireEvent.change(titleInput, { target: { value: 'Título da Campanha de Teste' } });

    const nextButton = screen.getByRole('button', { name: 'Avançar para a próxima etapa' });
    fireEvent.click(nextButton);

    // Etapa 2: Escrever a publicação
    const contentInput = screen.getByLabelText('Conteúdo da publicação');
    fireEvent.change(contentInput, { target: { value: 'Conteúdo da publicação de teste.' } });

    // Simular a adição de um arquivo
    // const file = new File(['dummy content'], 'test-file.png', { type: 'image/png' }); // Comentado
    // const fileInput = screen.getByText('Arraste e solte arquivos aqui ou clique para selecionar'); // Comentado
    // Para simular o drop, você pode precisar de uma abordagem mais complexa ou ajustar o componente para facilitar o teste.
    // Por simplicidade, vamos focar no envio do texto por enquanto.
    // Se precisar testar o upload de arquivos, podemos refinar esta parte.

    const completeButton = screen.getByRole('button', { name: 'Avançar para a próxima etapa' });

    // Configurar o mock para simular sucesso na criação da campanha
    // mockCreateCampaign.mockResolvedValueOnce({}); // Removido, pois a lógica está no mockImplementation acima

    fireEvent.click(completeButton);

    await waitFor(() => {
      expect(mockCreateCampaignAction).toHaveBeenCalledWith({ // Verifica se a ação foi chamada com os dados corretos
        title: 'Título da Campanha de Teste',
        content: 'Conteúdo da publicação de teste.',
        files: [], // Ajustar se o teste de upload de arquivo for implementado
        community_id: communityId,
        status: "active",
      });
    });

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith('Campanha criada com sucesso!');
    });

    await waitFor(() => {
      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });
  });

  test('deve mostrar alerta se o título estiver vazio na primeira etapa', () => {
    render(<ModalCampaign onClose={mockOnClose} communityId={communityId} />);
    
    const nextButton = screen.getByRole('button', { name: 'Avançar para a próxima etapa' });
    fireEvent.click(nextButton);

    expect(global.alert).toHaveBeenCalledWith('Por favor, insira um título para a campanha');
    expect(mockCreateCampaignAction).not.toHaveBeenCalled();
    expect(mockOnClose).not.toHaveBeenCalled();
  });

  test('deve mostrar alerta se o conteúdo estiver vazio na segunda etapa', () => {
    render(<ModalCampaign onClose={mockOnClose} communityId={communityId} />);

    // Etapa 1: Preencher título e avançar
    const titleInput = screen.getByLabelText('Título da campanha');
    fireEvent.change(titleInput, { target: { value: 'Título Qualquer' } });
    const nextButton = screen.getByRole('button', { name: 'Avançar para a próxima etapa' });
    fireEvent.click(nextButton);

    // Etapa 2: Tentar concluir sem conteúdo
    const completeButton = screen.getByRole('button', { name: 'Avançar para a próxima etapa' });
    fireEvent.click(completeButton);

    expect(global.alert).toHaveBeenCalledWith('Por favor, insira o conteúdo da publicação');
    expect(mockCreateCampaignAction).not.toHaveBeenCalled();
    expect(mockOnClose).not.toHaveBeenCalled();
  });

  test('deve chamar onClose ao clicar no botão de fechar', () => {
    render(<ModalCampaign onClose={mockOnClose} communityId={communityId} />);

    const closeButton = screen.getByRole('button', { name: '×' });
    fireEvent.click(closeButton);

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  test('deve voltar para a primeira etapa ao clicar em Voltar', () => {
    render(<ModalCampaign onClose={mockOnClose} communityId={communityId} />);

    // Avançar para a segunda etapa
    const titleInput = screen.getByLabelText('Título da campanha');
    fireEvent.change(titleInput, { target: { value: 'Título para Teste de Voltar' } });
    const nextButton = screen.getByRole('button', { name: 'Avançar para a próxima etapa' });
    fireEvent.click(nextButton);

    // Verificar se está na segunda etapa (input de conteúdo visível)
    expect(screen.getByLabelText('Conteúdo da publicação')).toBeInTheDocument();

    // Clicar em Voltar
    const backButton = screen.getByRole('button', { name: 'Voltar para a etapa anterior' });
    fireEvent.click(backButton);

    // Verificar se voltou para a primeira etapa (input de título visível)
    expect(screen.getByLabelText('Título da campanha')).toBeInTheDocument();
    // Verificar se o input de conteúdo não está mais visível (ou o componente WritePost não está renderizado)
    expect(screen.queryByLabelText('Conteúdo da publicação')).not.toBeInTheDocument();
  });

   test('deve lidar com erro na criação da campanha', async () => {
    const errorMessage = 'Falha ao criar campanha';
    // Configurar o mockCreateCampaignAction para simular erro E chamar o onError capturado
    mockCreateCampaignAction.mockImplementation(async () => { // data removido
      const error = new Error(errorMessage);
      if (capturedOnError) {
        capturedOnError(error);
      }
      return Promise.reject(error); // Falha da chamada de API (mockada)
    });

    render(<ModalCampaign onClose={mockOnClose} communityId={communityId} />);

    // Etapa 1
    fireEvent.change(screen.getByLabelText('Título da campanha'), { target: { value: 'Título Errado' } });
    fireEvent.click(screen.getByRole('button', { name: 'Avançar para a próxima etapa' }));

    // Etapa 2
    fireEvent.change(screen.getByLabelText('Conteúdo da publicação'), { target: { value: 'Conteúdo Errado' } });
    
    fireEvent.click(screen.getByRole('button', { name: 'Avançar para a próxima etapa' }));

    await waitFor(() => {
      expect(mockCreateCampaignAction).toHaveBeenCalledTimes(1); // Verifica se a ação foi chamada
    });
    
    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith("Erro ao criar campanha. Tente novamente.");
    });

    expect(mockOnClose).not.toHaveBeenCalled(); // Não deve fechar o modal em caso de erro
  });

});
