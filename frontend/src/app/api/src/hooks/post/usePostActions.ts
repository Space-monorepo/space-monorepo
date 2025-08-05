import { useState } from "react";
import axios from "axios";
import { API_URL, cloudinary_link } from "@/config"; // Certifique-se que este é o URL base correto da sua API
import { fetchUserProfile } from "@/app/api/src/services/userService";
import getTokenFromCookies from "@/app/api/src/controllers/getTokenFromCookies";
import { PostTypeEnum, PostStatusEnum, PostCreatePayload } from "../../types/posts/Post";

interface UsePostActionsProps {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  onSuccess?: (data?: any) => void; // data pode ser opcional ou ter um tipo mais específico
  onError?: (error: Error | unknown) => void;
  authToken?: string; // Se você quiser passar um token diretamente, mas geralmente pegamos do cookie
}

interface BasePostData {
  title: string;
  content: string;
  files?: File[]; // Mantido como array, mas para campanha, usaremos apenas o primeiro
}

interface AnnouncementData extends BasePostData {
  tags: string[];
  community_id: string; // Adicionado community_id
}

// Interface para os dados que o formulário da campanha envia para o hook
interface CampaignFormData extends BasePostData {
  community_id: string; // ID da comunidade específica para esta campanha
  // files: File[]; // Já está em BasePostData, idealmente apenas um arquivo para campanha
}

interface PollData extends BasePostData {
  community_id: string;
  pollQuestion: string; // Adicionado para tipagem correta
  options: string[];
  endDate: string;
}

interface ComplaintData extends BasePostData { // Modificado para interface
  community_id: string; // Adicionado community_id
}


// Função hipotética para upload de arquivo. Substitua pela sua implementação real.
// Ela deve retornar a URL pública do arquivo upado.
 
const uploadToCloudinary = async (file: File): Promise<string | null> => {
  const formData = new FormData();
  formData.append('file', file);
  // Usar as variáveis de ambiente corretas de config.ts
  formData.append('upload_preset', process.env.NEXT_PUBLIC_CLOUDINARY_UPLOAD_PRESET || '');

  const cloudName = process.env.NEXT_PUBLIC_CLOUDINARY_CLOUD_NAME;
  if (!cloudName) {
    console.error('Cloudinary Cloud Name não está configurado.');
    return null;
  }

  try {
    const response = await fetch(cloudinary_link!, { // Usar cloudinary_link importado
      method: 'POST',
      body: formData,
    });

    if (!response.ok) throw new Error('Erro ao enviar para o Cloudinary');

    const data = await response.json();
    return data.secure_url;
  } catch (error) {
    console.error('Erro no upload para Cloudinary:', error);
    return null;
  }
};


const usePostActions = ({ onSuccess, onError }: UsePostActionsProps = {}) => {
  const [isLoading, setIsLoading] = useState(false);

  const getBasePostData = async () => {
    const token = getTokenFromCookies();
    if (!token) throw new Error("Token não encontrado nos cookies");

    const user = await fetchUserProfile(token); // Supondo que isso retorne { id: string, community_id?: string }
    if (!user || !user.id) throw new Error("ID do usuário não encontrado ou perfil inválido");

    return {
      token,
      userId: user.id,
      // community_id aqui seria um default, mas para campanha, usaremos o específico.
      defaultCommunityId: user.community_id,
    };
  };

  const createAnnouncement = async (data: AnnouncementData) => {
    // ... (sua lógica para createAnnouncement, precisa verificar se usa FormData ou JSON)
    // Se create-post no backend espera FormData com 'files', então está ok.
    // Se espera JSON com image_url, precisa adaptar como createCampaign.
    // O endpoint /posts/create-post é genérico, pode ser que seu backend
    // tenha lógica para tratar type_post e files nele.
    // Por ora, vou assumir que sua lógica atual para createAnnouncement está correta
    // para o endpoint /posts/create-post.
    setIsLoading(true);
    try {
      const { token, userId } = await getBasePostData(); // Removido defaultCommunityId daqui

      // Se o endpoint /posts/create-post for genérico e aceitar community_id no corpo:
      const communityIdForPost = data.community_id; // Usar data.community_id
      if (!communityIdForPost) throw new Error("ID da comunidade não encontrado para o anúncio");


      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const payload: any = { // Use um tipo mais específico se tiver
        user_id: userId,
        community_id: communityIdForPost, // Usar communityIdForPost (que é data.community_id)
        type_post: PostTypeEnum.ANNOUNCEMENT,
        title: data.title,
        content: data.content,
        tags: data.tags, // Supondo que o backend espera um array de strings
        status: PostStatusEnum.ACTIVE,
      };

      // Se o backend /posts/create-post espera JSON e image_url:
      const finalPayload = { ...payload };
      if (data.files && data.files.length > 0) {
        const imageUrl = await uploadToCloudinary(data.files[0]);
        finalPayload.image_url = imageUrl;
      }


      const response = await axios.post(
        `${API_URL}/posts/${communityIdForPost}/create-post`, // Endpoint genérico
        finalPayload, // Enviando JSON
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json", // Mudado para JSON
          },
        }
      );

      onSuccess?.(response.data);
      return response.data;
    } catch (error) {
      console.error("Erro ao criar anúncio:", error);
      onError?.(error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const createCampaign = async (data: CampaignFormData) => {
    setIsLoading(true);
    try {
      const { token, userId } = await getBasePostData();

      if (!data.files || data.files.length === 0) {
        throw new Error("Uma imagem é obrigatória para a campanha.");
      }

      // 1. Fazer upload do arquivo para obter a image_url
      //    Usaremos data.files[0] como a imagem da campanha.
      const imageUrl = await uploadToCloudinary(data.files[0]);

      // 2. Preparar o payload JSON para o backend
      const payload: PostCreatePayload = {
        community_id: data.community_id, // ID da comunidade específica da campanha
        user_id: userId,
        type_post: PostTypeEnum.CAMPAIGN,
        title: data.title,
        content: data.content,
        image_url: imageUrl, // URL da imagem obtida do upload
        status: PostStatusEnum.ACTIVE, // Ou outro status se necessário
      };

      // 3. Enviar a requisição para o endpoint específico de campanha
      const response = await axios.post(
        `${API_URL}/posts/${data.community_id}/post/campaign`, // Endpoint CORRETO para criar campanha
        payload, // Enviando payload JSON
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json", // CORRETO para payload JSON
          },
        }
      );

      onSuccess?.(response.data);
      return response.data;
    } catch (error) {
      console.error("Erro ao criar campanha:", error);
      onError?.(error);
      throw error; // Re-throw para que o componente possa tratar se necessário
    } finally {
      setIsLoading(false);
    }
  };

  const createPoll = async (data: PollData) => {
    setIsLoading(true);
    try {
      const { token, userId, defaultCommunityId } = await getBasePostData();
      const communityIdForPoll = data.community_id || defaultCommunityId;
      if (!communityIdForPoll) throw new Error("ID da comunidade não encontrado para a enquete");

      const payload: {
        post: PostCreatePayload & { image_url?: string | null }; // Permitir string | null para image_url
        question: string;
        options: string[];
      } = {
        post: {
          community_id: communityIdForPoll,
          user_id: userId,
          type_post: PostTypeEnum.POLL,
          title: data.title,
          content: data.content,
          status: PostStatusEnum.ACTIVE,
        },
        question: data.pollQuestion,
        options: data.options.map(optionText => optionText),
      };

      if (data.files && data.files.length > 0) {
        const imageUrl = await uploadToCloudinary(data.files[0]);
        payload.post.image_url = imageUrl; // Agora compatível com string | null
      }

      const response = await axios.post(
        `${API_URL}/posts/${communityIdForPoll}/post/poll`, // Endpoint CORRETO para criar enquete
        payload,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      onSuccess?.(response.data);
      return response.data;
    } catch (error) {
      console.error("Erro ao criar enquete:", error);
      onError?.(error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const createComplaint = async (data: ComplaintData) => {
    setIsLoading(true);
    try {
      const { token, userId } = await getBasePostData(); // Removido defaultCommunityId daqui
      // Para reclamação, talvez o community_id seja sempre o defaultCommunityId
      // ou precise ser determinado de outra forma.
      const communityIdForComplaint = data.community_id; // Usar data.community_id
      if (!communityIdForComplaint) throw new Error("ID da comunidade não encontrado para a reclamação");

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const payload: any = {
        user_id: userId,
        community_id: communityIdForComplaint, // Usar communityIdForComplaint (que é data.community_id)
        type_post: PostTypeEnum.COMPLAINT,
        title: data.title,
        content: data.content,
        status: PostStatusEnum.ACTIVE,
      };

      const finalPayload = { ...payload };
      if (data.files && data.files.length > 0) {
        // Se reclamações podem ter imagens, faça o upload e adicione image_url
        const imageUrl = await uploadToCloudinary(data.files[0]);
        finalPayload.image_url = imageUrl;
      }

      const response = await axios.post(
        `${API_URL}/posts/${communityIdForComplaint}/post/complaint`, // Endpoint CORRETO para criar reclamação
        finalPayload,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      onSuccess?.(response.data);
      return response.data;
    } catch (error) {
      console.error("Erro ao criar reclamação:", error);
      onError?.(error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };


  return {
    isLoading,
    createAnnouncement,
    createCampaign,
    createPoll,
    createComplaint,
  };
};

export default usePostActions;