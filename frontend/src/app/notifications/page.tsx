"use client"

import { Close, CheckmarkFilled, Forum, ArrowUp, Filter, SortDescending, FaceSatisfied, TextBold, TextItalic, ListNumbered, ListBulleted } from "@carbon/icons-react";

import { useState, useEffect } from "react"
import { ArrowLeft, Eye } from "lucide-react"
import Sidebar from "@/components/ui/sidebar"
import { useNotifications } from "@/app/api/src/hooks/notifications/useNotifications"
import { Notification } from "@/app/api/src/types/notifications/Notification"
import getCheckmarkColorClass from "@/components/badges/users/CheckmarkColorClasses";
import getRoleBadgeClasses from "@/components/badges/users/RoleBadgesClasses";
import { translateUserRole } from "@/lib/roleTranslations";
import usePostActions from "@/app/api/src/hooks/post/usePostActions";
import { getRelativeTime } from "@/lib/relativeTime";
import {
  PendenteBadge,
  EmAnaliseBadge,
  AprovadaBadge,
  RejeitadaBadge,
  EmProgressoBadge,
  CanceladaBadge,
  FinalizadaBadge
} from "@/components/badges/campaign/CampaignBadges";

interface Comment {
  id: string;
  user: {
    name: string;
    profile_picture?: string;
    profile_image_url?: string;
    member_role?: string;
  };
  content: string;
  created_at: string;
  parent_id?: string | null;
  replies?: Comment[];
  children?: Comment[];
  likes_count?: number;
}

function AnnouncementCommentsModal({
  isOpen,
  onClose,
  announcementId,
  communityId
}: {
  isOpen: boolean;
  onClose: () => void;
  announcementId: string;
  communityId: string;
}) {
  const { listComments, addComment, replyComment, likeComment, unlikeComment } = usePostActions();
  const [likedComments, setLikedComments] = useState<{ [key: string]: boolean }>({});
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [commentInput, setCommentInput] = useState('');
  const [replyingTo, setReplyingTo] = useState<string | null>(null);
  const [replyInput, setReplyInput] = useState<{ [key: string]: string }>({});

  function buildCommentsTree(flatComments: Comment[]): Comment[] {
    const commentsMap: { [key: string]: Comment & { children: Comment[] } } = {};
    const roots: (Comment & { children: Comment[] })[] = [];

    flatComments.forEach(comment => {
      commentsMap[comment.id] = { ...comment, children: [] };
    });

    flatComments.forEach(comment => {
      if (comment.parent_id && commentsMap[comment.parent_id]) {
        commentsMap[comment.parent_id].children.push(commentsMap[comment.id]);
      } else {
        roots.push(commentsMap[comment.id]);
      }
    });

    return roots;
  }

  const fetchComments = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listComments(communityId, announcementId);
      const items = data.items || [];
      setComments(buildCommentsTree(items));
      // Atualiza o estado de likes dos comentários
      const likedMap: { [key: string]: boolean } = {};
      items.forEach((c: any) => {
        likedMap[c.id] = false;
      });
      setLikedComments(likedMap);
    } catch (err: any) {
      setError('Erro ao carregar comentários');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchComments();
    }
  }, [isOpen, communityId, announcementId]);

  const handleAddComment = async () => {
    if (!commentInput.trim()) return;
    try {
      await addComment(communityId, announcementId, commentInput);
      setCommentInput('');
      fetchComments();
    } catch (err) {
      setError('Erro ao comentar');
    }
  };

  const handleReply = async (parentId: string) => {
    const content = replyInput[parentId];
    if (!content?.trim()) return;
    try {
      await replyComment(communityId, announcementId, parentId, content);
      setReplyInput((prev) => ({ ...prev, [parentId]: '' }));
      setReplyingTo(null);
      fetchComments();
    } catch (err) {
      setError('Erro ao responder comentário');
    }
  };

  // Atualiza likes recursivamente na árvore de comentários
  function updateCommentLikes(comments: Comment[], commentId: string, increment: number): Comment[] {
    return comments.map(comment => {
      if (comment.id === commentId) {
        return { ...comment, likes_count: (comment.likes_count || 0) + increment };
      }
      if (comment.children && comment.children.length > 0) {
        return { ...comment, children: updateCommentLikes(comment.children, commentId, increment) };
      }
      if (comment.replies && comment.replies.length > 0) {
        return { ...comment, replies: updateCommentLikes(comment.replies, commentId, increment) };
      }
      return comment;
    });
  }

  // Like/Unlike comentário
  const handleLikeComment = async (comment: Comment) => {
    try {
      if (!likedComments[comment.id]) {
        await likeComment(communityId, comment.id);
        setComments(prev => updateCommentLikes(prev, comment.id, 1));
        setLikedComments(prev => ({ ...prev, [comment.id]: true }));
      } else {
        await unlikeComment(communityId, comment.id);
        setComments(prev => updateCommentLikes(prev, comment.id, -1));
        setLikedComments(prev => ({ ...prev, [comment.id]: false }));
      }
    } catch (err) {
      setError('Erro ao curtir/descurtir comentário');
    }
  };

  function countAllComments(comments: Comment[]): number {
    let count = 0;
    for (const comment of comments) {
      count += 1;
      if (Array.isArray(comment.children) && comment.children.length > 0) {
        count += countAllComments(comment.children);
      }
      if (Array.isArray(comment.replies) && comment.replies.length > 0) {
        count += countAllComments(comment.replies);
      }
    }
    return count;
  }

  const renderComment = (comment: Comment, isChild = false) => (
    <div key={comment.id} className={`${isChild ? 'flex flex-wrap items-start self-end mt-6 max-w-full w-[592px]' : 'flex flex-wrap justify-between w-full max-md:max-w-full'}`}>
      <div className="flex flex-col items-center w-11">
        <img
          src={comment.user && (comment.user.profile_image_url || comment.user.profile_picture) ? (comment.user.profile_image_url || comment.user.profile_picture) : '/no-profile-pic.png'}
          alt={`${comment.user.name} avatar`}
          className={`object-contain w-11 aspect-square ${isChild ? 'rounded-[32px]' : ''}`}
        />
        {!isChild && ((Array.isArray(comment.children) && comment.children.length > 0) || (Array.isArray(comment.replies) && comment.replies.length > 0)) && (
          <div className="flex mt-2 w-px bg-zinc-300 min-h-[78px]" />
        )}
      </div>
      <div className="flex-1 shrink basis-0 min-w-60 max-md:max-w-full">
        <div className="flex flex-wrap gap-3 items-center py-3 w-full max-md:max-w-full">
          <div className={`flex items-center self-stretch my-auto min-w-60 text-neutral-800 ${isChild ? 'w-[360px]' : 'w-[380px]'}`}>
            <div className={`self-stretch my-auto min-w-60 ${isChild ? 'w-[360px]' : 'w-[380px]'}`}>
              <div className="flex gap-2 items-center w-full h-[23px]">
                <div className="flex overflow-hidden gap-2.5 justify-center items-center self-stretch px-3 my-auto">
                  <div className="self-stretch my-auto whitespace-nowrap text-sm text-neutral-800">
                    {comment.user.name}
                  </div>
                  <CheckmarkFilled
                    className={`object-contain shrink-0 self-stretch my-auto aspect-square w-[18px] ${getCheckmarkColorClass(comment.user.member_role)}`}
                    aria-label="Verificado"
                  />
                  <div className="self-stretch my-auto text-[10px] text-black font-semibold">
                    •
                  </div>
                  {comment.user.member_role && (
                    <div className={`flex gap-2.5 justify-center items-center self-stretch px-3 py-1 my-auto text-xs whitespace-nowrap rounded ${getRoleBadgeClasses(comment.user.member_role)}`}>
                      <div className="self-stretch my-auto">
                        {translateUserRole(comment.user.member_role)}
                      </div>
                    </div>
                  )}
                  <div className="self-stretch my-auto text-[10px] text-black">
                    •
                  </div>
                  <div className="self-stretch my-auto text-[10px] whitespace-nowrap font-semibold">
                    <div className="text-neutral-800">
                      {getRelativeTime(comment.created_at)}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="flex gap-4 items-center self-stretch my-auto w-5 min-h-5">
            {/* Menu de opções para comentários pode ser implementado aqui se necessário */}
          </div>
        </div>
        <div className="px-3 mt-2 w-full max-md:max-w-full">
          <div className={`flex ${isChild ? 'overflow-hidden ' : ''}gap-2.5 items-center w-full text-sm leading-5 text-neutral-800 max-md:max-w-full`}>
            <div className="flex-1 shrink self-stretch my-auto basis-0 text-neutral-800 max-md:max-w-full">
              {comment.content}
            </div>
          </div>
          <div className={`flex justify-between items-center mt-4 w-full text-xs font-medium leading-none text-justify ${isChild ? 'whitespace-nowrap ' : ''}text-neutral-500 max-md:max-w-full`}>
            <div className="flex overflow-hidden gap-8 items-center self-stretch my-auto min-h-5">
              <div className={`flex overflow-hidden gap-2 items-center self-stretch my-auto ${isChild ? '' : 'whitespace-nowrap'}`}>
                <ArrowUp
                  className="object-contain shrink-0 self-stretch my-auto w-3 aspect-square cursor-pointer hover:opacity-70 transition-opacity text-neutral-500"
                  onClick={() => handleLikeComment(comment)}
                  aria-label="Curtir"
                />
                <div className={`self-stretch my-auto ${likedComments[comment.id] ? 'text-neutral-600' : 'text-neutral-500'}`}>
                  {comment.likes_count ?? 0}
                </div>
              </div>
              <div className="flex overflow-hidden gap-2 items-center self-stretch my-auto">
                <img
                  src="https://api.builder.io/api/v1/image/assets/367ac41a58454bf7adac62a5f3afc83b/76fc42bedb22beda24433b506515bdee6ba7cab0?placeholderIfAbsent=true"
                  className="object-contain shrink-0 self-stretch my-auto w-4 aspect-square cursor-pointer hover:opacity-70 transition-opacity"
                  onClick={() => setReplyingTo(replyingTo === comment.id ? null : comment.id)}
                  alt="Reply"
                />
                <div className="self-stretch my-auto text-neutral-500 cursor-pointer hover:text-neutral-700 transition-colors" onClick={() => setReplyingTo(replyingTo === comment.id ? null : comment.id)}>
                  {isChild ? 'Responder' : `Responder${((Array.isArray(comment.children) && comment.children.length > 0) || (Array.isArray(comment.replies) && comment.replies.length > 0)) ? ` (${(comment.children?.length || 0) + (comment.replies?.length || 0)})` : ''}`}
                </div>
              </div>
            </div>
          </div>
          {replyingTo === comment.id && (
            <div className="flex flex-col gap-2 items-start self-stretch w-full mt-4">
              <div className="flex flex-col items-start self-stretch w-full">
                <div className="flex flex-col justify-between items-start self-stretch p-4 bg-gray-100 h-[160px] rounded-xs w-full">
                  <textarea
                    className="w-full h-full bg-transparent text-sm leading-6 text-neutral-600 max-sm:text-sm resize-none border-none outline-none placeholder:text-neutral-600"
                    rows={2}
                    placeholder="Digite sua resposta..."
                    value={replyInput[comment.id] || ''}
                    onChange={e => setReplyInput(prev => ({ ...prev, [comment.id]: e.target.value }))}
                    onKeyDown={e => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleReply(comment.id);
                      }
                    }}
                  />
                  <div className="flex flex-row justify-between items-end w-full mt-2">
                    <div className="flex gap-4 items-center max-sm:gap-3">
                      <button type="button" aria-label="Adicionar emoji">
                        <FaceSatisfied size={20} className="toolbar-icon text-neutral-500" />
                      </button>
                      <button type="button" aria-label="Negrito">
                        <TextBold size={20} className="toolbar-icon text-neutral-500" />
                      </button>
                      <button type="button" aria-label="Itálico">
                        <TextItalic size={20} className="toolbar-icon text-neutral-500" />
                      </button>
                      <button type="button" aria-label="Lista numerada">
                        <ListNumbered size={20} className="toolbar-icon text-neutral-500" />
                      </button>
                      <button type="button" aria-label="Lista com marcadores">
                        <ListBulleted size={20} className="toolbar-icon text-neutral-500" />
                      </button>
                    </div>
                    <div className="flex flex-row items-end">
                      <button
                        className="px-3 py-2 bg-neutral-800 text-white rounded-xs font-regular"
                        onClick={() => handleReply(comment.id)}
                      >
                        Enviar
                      </button>
                      <button
                        className="ml-2 px-3 py-2 bg-gray-300 text-gray-700 rounded-xs font-regular hover:bg-gray-400 transition-colors"
                        onClick={() => setReplyingTo(null)}
                      >
                        Cancelar
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
      {/* Renderizar children recursivamente */}
      {Array.isArray(comment.children) && comment.children.length > 0 && (
        <div className="flex flex-wrap items-start self-end mt-6 max-w-full w-[592px]">
          {comment.children.map(child => renderComment(child, true))}
        </div>
      )}
      {/* Renderizar replies recursivamente */}
      {Array.isArray(comment.replies) && comment.replies.length > 0 && (
        <div className="flex flex-wrap items-start self-end mt-6 max-w-full w-[592px] pl-12">
          {comment.replies.map(child => renderComment(child, true))}
        </div>
      )}
    </div>
  );

  const totalComments = countAllComments(comments);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="bg-white rounded shadow-lg w-full max-w-[720px] mx-4 max-h-[90vh] overflow-hidden">
        <div className="flex justify-between items-center p-4 border-b border-[0.5px] border-stone-300">
          <h2 className="text-lg font-semibold text-neutral-800">Comentários do Aviso</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <Close className="h-5 w-5" />
          </button>
        </div>

        <div className="overflow-y-auto" style={{ maxHeight: 'calc(90vh - 80px)' }}>
          <main className="flex flex-col shrink-0 gap-8 items-start p-4 bg-white border-solid border-[0.5px] border-stone-300 w-full max-md:p-3 max-sm:gap-6 max-sm:p-2">
            {/* Comment Input Section */}
            <div className="flex flex-col gap-2 items-start self-stretch">
              <div className="flex flex-col items-start self-stretch">
                <div className="flex flex-col justify-between items-start self-stretch p-4 bg-gray-100 h-[160px] rounded-xs">
                  <textarea
                    id="comment-textarea"
                    value={commentInput}
                    onChange={e => setCommentInput(e.target.value)}
                    placeholder="Adicione um comentário"
                    className="w-full h-full bg-transparent text-sm leading-6 text-neutral-600 max-sm:text-sm resize-none border-none outline-none placeholder:text-neutral-600"
                    rows={2}
                    onKeyDown={e => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleAddComment();
                      }
                    }}
                  />
                  <div className="flex flex-row justify-between items-end w-full mt-2">
                    <div className="flex gap-4 items-center max-sm:gap-3">
                      <button type="button" aria-label="Adicionar emoji">
                        <FaceSatisfied size={20} className="toolbar-icon text-neutral-500" />
                      </button>
                      <button type="button" aria-label="Negrito">
                        <TextBold size={20} className="toolbar-icon text-neutral-500" />
                      </button>
                      <button type="button" aria-label="Itálico">
                        <TextItalic size={20} className="toolbar-icon text-neutral-500" />
                      </button>
                      <button type="button" aria-label="Lista numerada">
                        <ListNumbered size={20} className="toolbar-icon text-neutral-500" />
                      </button>
                      <button type="button" aria-label="Lista com marcadores">
                        <ListBulleted size={20} className="toolbar-icon text-neutral-500" />
                      </button>
                    </div>
                    <div className="flex flex-row items-end">
                      <button
                        className="px-3 py-2 bg-neutral-800 text-white rounded-xs font-regular"
                        onClick={handleAddComment}
                      >
                        Enviar
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            {/* Comments Header */}
            <header className="flex gap-4 items-center self-stretch px-2 py-0 max-md:gap-3 max-md:px-3 max-md:py-0 max-sm:flex-wrap max-sm:gap-2 max-sm:px-2 max-sm:py-0">
              <h2 className="text-base leading-6 text-neutral-800 max-md:text-base max-sm:text-sm">
                Comentários
              </h2>
              <div className="flex flex-col gap-2.5 justify-center items-center px-2 py-1 rounded-xs bg-neutral-800">
                <span className="self-stretch text-base leading-6 text-zinc-100 max-md:text-base max-sm:text-sm">
                  {totalComments}
                </span>
              </div>
            </header>

            {/* Comments List */}
            <section
              className="flex flex-col p-4 bg-white rounded-sm max-w-[648px] w-full no-scrollbar"
              style={{ maxHeight: 800, overflowY: 'auto' }}
            >
              {loading && <div>Carregando comentários...</div>}
              {error && <div className="text-red-500">{error}</div>}
              {!loading && comments.length === 0 && <div className="px-2">Nenhum comentário ainda.</div>}
              {comments.map(comment => renderComment(comment))}
            </section>
          </main>
        </div>
      </div>
    </div>
  );
}

type NotificationType = "Campanhas" | "Avisos oficiais" | "Conexões" | "Interações"

export default function NotificacoesPage() {
  // Função para mapear status da API para status do frontend
  const mapApiStatusToFrontendStatus = (apiStatus: string): "Em análise" | "Aprovado" | "Rejeitado" | "Pendente" | "Em progresso" | "Cancelada" | "Finalizada" => {
    switch (apiStatus.toLowerCase()) {
      case 'active':
        return "Em análise";
      case 'approved':
        return "Aprovado";
      case 'rejected':
        return "Rejeitado";
      case 'pending':
        return "Pendente";
      case 'in_progress':
        return "Em progresso";
      case 'cancelled':
        return "Cancelada";
      case 'completed':
      case 'finished':
        return "Finalizada";
      default:
        return "Em análise";
    }
  };

  // Função para mapear status da campanha para o componente de badge correto
  const getCampaignStatusBadge = (status: string) => {
    // Primeiro mapear o status da API para o formato do frontend
    const mappedStatus = mapApiStatusToFrontendStatus(status);

    switch (mappedStatus) {
      case "Em análise":
        return <EmAnaliseBadge />;
      case "Aprovado":
        return <AprovadaBadge />;
      case "Rejeitado":
        return <RejeitadaBadge />;
      case "Pendente":
        return <PendenteBadge />;
      case "Em progresso":
        return <EmProgressoBadge />;
      case "Cancelada":
        return <CanceladaBadge />;
      case "Finalizada":
        return <FinalizadaBadge />;
      default:
        return <PendenteBadge />;
    }
  };
  const [activeTab, setActiveTab] = useState<NotificationType>("Campanhas")
  const [selectedNotification, setSelectedNotification] = useState<Notification | null>(null)
  const [showCommentsModal, setShowCommentsModal] = useState(false)
  const { notifications, loading, error } = useNotifications()

  // Usar conexões reais do backend
  const connections = notifications.connections || [];
  const pendingCount = connections.filter(conn => conn.connection_status === 'pending').length;

  // Usar interações reais do backend
  const interactions = notifications.interactions || [];
  const interactionsCount = interactions.length;

  // Funções para aceitar/rejeitar conexão usando API (exemplo básico)
  const handleConnect = async (id: string) => {
    try {
      await fetch(`/api/users/connections/${id}/accept`, { method: 'PUT' });
      // Ideal: atualizar lista de conexões após sucesso
    } catch (e) {
      console.error('Erro ao aceitar conexão', e);
    }
  };

  const handleReject = async (id: string) => {
    try {
      await fetch(`/api/users/connections/${id}/reject`, { method: 'PUT' });
      // Ideal: atualizar lista de conexões após sucesso
    } catch (e) {
      console.error('Erro ao rejeitar conexão', e);
    }
  };

  const handleLikeInteraction = (id: string) => {
    // Handle like functionality for interactions
    console.log(`Liked interaction ${id}`);
  };

  // Mapear os dados da API para o formato usado no componente
  const notificationsTabs: Record<NotificationType, Notification[]> = {
    Campanhas: notifications.campaigns,
    "Avisos oficiais": notifications.announcements,
    Conexões: notifications.connections,
    Interações: notifications.interactions,
  }

  const currentNotifications = notificationsTabs[activeTab] || []

  // Set first notification as selected when changing tabs or when data loads
  useEffect(() => {
    if (!selectedNotification && currentNotifications.length > 0) {
      setSelectedNotification(currentNotifications[0])
    }
  }, [selectedNotification, currentNotifications])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 text-[#161616]">
        <Sidebar variant="static" />
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
            <p className="mt-4 text-gray-600">Carregando notificações...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 text-[#161616]">
        <Sidebar variant="static" />
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <p className="text-red-600">Erro ao carregar notificações: {error}</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-4 px-4 py-2 bg-black text-white rounded"
            >
              Tentar novamente
            </button>
          </div>
        </div>
      </div>
    )
  }

  const handleTabChange = (tab: NotificationType) => {
    setActiveTab(tab)
    setSelectedNotification(notificationsTabs[tab]?.[0] || null)
  }

  return (
    <div className="min-h-screen bg-white text-[#161616]">
      <Sidebar variant="static" />
      <div className="flex">
        {/* Left Navigation - Fixo igual CommunityAdminPage */}
        <div className="fixed left-64 top-0 w-64 bg-white border-r border-[#e0e0e0] h-screen z-20 overflow-y-auto">
          {/* Header */}
          <div className="sticky top-0 p-6 border-[#e0e0e0] bg-white flex items-center gap-3">
            <ArrowLeft className="h-5 w-5 text-[#525252]" />
            <h1 className="text-lg font-regular">Notificações</h1>
          </div>
          {/* Navigation Tabs */}
          <nav className="py-4">
            {(Object.keys(notificationsTabs) as NotificationType[]).map((tab) => (
              <button
                key={tab}
                className={`w-full px-6 py-3 text-left hover:bg-[#f8f8f8] cursor-pointer ${activeTab === tab
                  ? "bg-[#f4f4f4] border-r-4 border-black text-[#161616]"
                  : "text-[#525252]"
                  }`}
                onClick={() => handleTabChange(tab)}
              >
                <span>{tab}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Middle Section - Campanhas with Figma layout */}
        {activeTab === "Campanhas" && (
          <div className="w-80 fixed my-4 top-0 bottom-0 left-[512px] bg-white border-r border-[#e0e0e0] overflow-y-auto z-10 no-scrollbar">
            <section className="flex flex-col max-w-[352px]">
              <header className="flex gap-2 items-center py-2.5 pr-2 pl-4 text-sm leading-none text-neutral-600">
                <h2 className="self-stretch text-neutral-600 w-[272px]">
                  Campanhas
                </h2>
                <button
                  className="object-contain shrink-0 self-stretch my-auto w-5 aspect-square"
                  aria-label="Action button 1"
                >
                  <Filter className="w-full h-full text-[#525252]" />
                </button>
                <button
                  className="object-contain shrink-0 self-stretch my-auto w-5 aspect-square"
                  aria-label="Action button 2"
                >
                  <SortDescending className="w-full h-full text-[#525252]" />
                </button>
              </header>

              <div className="self-center mt-6 w-full max-w-xs">
                {currentNotifications.map((notification, index) => (
                  <article
                    key={notification.id}
                    className={`flex flex-col justify-center px-6 py-4 w-full cursor-pointer hover:opacity-80 transition-opacity ${selectedNotification?.id === notification.id ? 'bg-zinc-200' : 'bg-white'
                      }`}
                    onClick={() => setSelectedNotification(notification)}
                  >
                    <div className="w-full">
                      <time className="text-xs leading-loose text-neutral-600">
                        {notification.date}
                      </time>
                      <div className="mt-2 w-full">
                        <div className="flex gap-10 justify-between items-start w-full">
                          <h3 className="text-base text-black">
                            {notification.title}
                          </h3>
                          <div className="flex gap-2 justify-center items-center text-xs leading-loose text-neutral-600">
                            <span className="self-stretch my-auto text-neutral-600">
                              {notification.stats?.accesses || '0'}
                            </span>
                            <Eye className="object-contain shrink-0 self-stretch my-auto w-4 aspect-square text-neutral-600" />
                          </div>
                        </div>
                        <p className="mt-1 text-xs leading-loose text-neutral-600">
                          Líder: {notification.author.name}
                        </p>
                        <p className="mt-1 text-xs leading-loose text-neutral-600">
                          Comunidade: {notification.community.name}
                        </p>
                        {notification.status && (
                          <div className="flex items-center mt-2">
                            {getCampaignStatusBadge(notification.status)}
                          </div>
                        )}
                      </div>
                    </div>
                  </article>
                ))}
              </div>
            </section>
          </div>
        )}

        {/* Middle Section - Avisos oficiais with Figma layout */}
        {activeTab === "Avisos oficiais" && (
          <div className="w-80 fixed my-4 top-0 bottom-0 left-[512px] bg-white border-r border-[#e0e0e0] overflow-y-auto z-10 no-scrollbar">
            <section className="flex flex-col max-w-[352px]">
              <header className="flex gap-2 items-center py-2.5 pr-2 pl-4 text-sm leading-none text-neutral-600">
                <h2 className="self-stretch text-neutral-600 w-[272px]">
                  Avisos oficiais
                </h2>
                <button
                  className="object-contain shrink-0 self-stretch my-auto w-5 aspect-square"
                  aria-label="Action button 1"
                >
                  <Filter className="w-full h-full text-[#525252]" />
                </button>
                <button
                  className="object-contain shrink-0 self-stretch my-auto w-5 aspect-square"
                  aria-label="Action button 2"
                >
                  <SortDescending className="w-full h-full text-[#525252]" />
                </button>
              </header>

              <div className="self-center mt-6 w-full max-w-xs">
                {currentNotifications.map((notification, index) => (
                  <article
                    key={notification.id}
                    className={`flex flex-col justify-center px-6 py-4 w-full cursor-pointer hover:opacity-80 transition-opacity ${selectedNotification?.id === notification.id ? 'bg-zinc-200' : 'bg-white'
                      }`}
                    onClick={() => setSelectedNotification(notification)}
                  >
                    <div className="w-full">
                      <time className="text-xs leading-loose text-neutral-600">
                        {notification.date}
                      </time>
                      <div className="mt-2 w-full">
                        <div className="flex gap-10 justify-between items-start w-full">
                          <h3 className="text-base text-black">
                            {notification.title}
                          </h3>
                          <div className="flex gap-2 justify-center items-center text-xs leading-loose text-neutral-600">
                            <span className="self-stretch my-auto whitespace-nowrap text-neutral-600">
                              {notification.stats?.accesses || '0'}
                            </span>
                            <Eye className="object-contain shrink-0 self-stretch my-auto w-4 aspect-square text-neutral-600" />
                          </div>
                        </div>
                        <p className="mt-1 text-xs leading-loose text-neutral-600">
                          Administrador: {notification.author.name}
                        </p>
                        <p className="mt-1 text-xs leading-loose text-neutral-600">
                          Comunidade: {notification.community.name}
                        </p>
                      </div>
                    </div>
                  </article>
                ))}
              </div>
            </section>
          </div>
        )}

        {/* Right Section - Detailed View for Campanhas */}
        {selectedNotification && activeTab === "Campanhas" && (
          <div className="flex-1 bg-gray-100 fixed top-0 right-0 bottom-0 left-[calc(512px+320px)] overflow-y-auto no-scrollbar">
            <div className="max-w-full">
              <div className="px-4 pt-4 pb-80 w-full bg-zinc-100 max-md:pb-24 max-md:max-w-full">
                <article className="mb-0 bg-white max-md:mb-2.5 max-md:max-w-full">
                  <header className="flex flex-col justify-center p-8 w-full bg-white rounded max-md:px-5 max-md:max-w-full">
                    <div className="w-full max-md:max-w-full">
                      <div className="flex justify-between items-start w-full max-md:max-w-full">
                        <div className="flex items-center min-w-60">
                          <img
                            src={selectedNotification.author.profile_picture || "/no-profile-pic.png"}
                            alt={`${selectedNotification.author.name} profile picture`}
                            className="object-contain shrink-0 self-stretch my-auto w-11 aspect-square"
                          />
                          <div className="self-stretch my-auto min-w-60 w-[342px]">
                            <div className="flex gap-2 items-center w-full h-[23px]">
                              <div className="flex overflow-hidden gap-2.5 justify-center items-center self-stretch px-3 my-auto">
                                <span className="self-stretch my-auto text-sm text-neutral-800">
                                  {selectedNotification.author.name}
                                </span>
                                <CheckmarkFilled
                                  className={`object-contain shrink-0 self-stretch my-auto aspect-square w-[18px] ${getCheckmarkColorClass(selectedNotification.author.role)}`}
                                  aria-label="Verificado"
                                />
                                <div className="self-stretch my-auto text-[10px] text-black">
                                  •
                                </div>
                                <span className={`flex gap-2.5 justify-center items-center self-stretch px-3 py-1 my-auto text-xs whitespace-nowrap rounded ${getRoleBadgeClasses(selectedNotification.author.role)}`}>
                                  {translateUserRole(selectedNotification.author.role || "member")}
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div className="mt-6 w-full text-sm text-neutral-800 max-md:max-w-full">
                        <div className="flex flex-wrap gap-4 items-center w-full leading-6 max-md:max-w-full">
                          <span className="self-stretch my-auto font-semibold text-neutral-800">
                            Título:{" "}
                          </span>
                          <span className="self-stretch my-auto text-neutral-800">
                            {selectedNotification.title}
                          </span>
                        </div>
                        <div className="mt-2 w-full max-md:max-w-full">
                          <h3 className="font-semibold leading-6 text-justify text-neutral-800">
                            Descrição:
                          </h3>
                          <p className="mt-2 leading-5 text-neutral-800 max-md:max-w-full whitespace-pre-line">
                            {selectedNotification.description}
                          </p>
                        </div>
                      </div>
                    </div>
                  </header>

                  {/* Image Section */}
                  {selectedNotification.image_url && (
                    <section className="px-8 pb-6 w-full max-md:px-5 max-md:max-w-full">
                      <img
                        src={selectedNotification.image_url || "/ProfilePic2.svg"}
                        alt="Content image"
                        className="w-full rounded"
                      />
                    </section>
                  )}

                  <section className="flex flex-col py-8 pr-4 pl-8 w-full max-md:pl-5 max-md:max-w-full">
                    <div className="w-full text-sm leading-none max-md:max-w-full">
                      <div className="flex flex-wrap gap-36 items-start w-full max-md:max-w-full">
                        <div className="flex flex-col items-start">
                          <div className="flex gap-2 items-center">
                            <span className="self-stretch my-auto font-medium text-neutral-800">
                              Data publicada:
                            </span>
                            <span className="self-stretch my-auto text-neutral-500">
                              {selectedNotification.stats?.published || selectedNotification.date}
                            </span>
                          </div>
                          <div className="flex gap-2 items-center self-stretch mt-4">
                            <span className="self-stretch my-auto font-medium text-neutral-800">
                              Número de acessos:
                            </span>
                            <span className="self-stretch my-auto text-neutral-500">
                              {selectedNotification.stats?.accesses ?? 0} acessos
                            </span>
                          </div>
                          <div className="flex gap-2 items-center mt-4">
                            <span className="self-stretch my-auto font-medium text-neutral-800">
                              Participantes:
                            </span>
                            <span className="self-stretch my-auto text-neutral-500">
                              {selectedNotification.stats?.participants ?? 0} pessoas
                            </span>
                          </div>
                        </div>
                        <div className="flex flex-col w-[198px]">
                          <div className="flex gap-2 items-center self-start">
                            <span className="self-stretch my-auto font-medium text-neutral-800">
                              Curtidas:
                            </span>
                            <span className="self-stretch my-auto text-neutral-500">
                              {selectedNotification.stats?.likes ?? 0} curtidas
                            </span>
                          </div>
                          <div className="flex gap-2 items-center mt-4 w-full">
                            <span className="self-stretch my-auto font-medium text-neutral-800">
                              Comentários:
                            </span>
                            <span className="self-stretch my-auto text-neutral-500">
                              {selectedNotification.stats?.comments ?? 0} comentários
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Status Section */}
                    <div className="flex gap-2 items-center self-start mt-10">
                      <span className="self-stretch my-auto text-sm font-medium leading-none text-neutral-800">
                        Status:
                      </span>
                      {getCampaignStatusBadge(selectedNotification.status || "pending")}
                    </div>

                    {/* Actions Section */}
                    {selectedNotification.actions && (
                      <div className="flex items-center gap-4 mt-10">
                        {selectedNotification.actions.map((action: string, index: number) => (
                          <button
                            key={index}
                            className="flex items-center gap-2 px-4 py-2 border border-[#e0e0e0] hover:bg-[#f8f8f8] rounded"
                          >
                            {action === "Promover" && <ArrowUp className="h-4 w-4" />}
                            {action === "Comentar" && <Forum className="h-4 w-4" />}
                            {action}
                          </button>
                        ))}
                      </div>
                    )}
                  </section>
                </article>
              </div>
            </div>
          </div>
        )}

        {/* Right Section - Detailed View for Avisos oficiais (layout de enquete) */}
        {selectedNotification && activeTab === "Avisos oficiais" && (
          <div className="flex-1 bg-gray-100 fixed top-0 right-0 bottom-0 left-[calc(512px+320px)] overflow-y-auto no-scrollbar">
            <div className="max-w-full">
              <div className="px-4 pt-4 pb-48 w-full bg-zinc-100 max-md:pb-24 max-md:max-w-full">
                <main className="bg-white max-w-full">
                  <article className="flex flex-col justify-center p-8 w-full bg-white rounded max-md:px-5 max-md:max-w-full">
                    <div className="w-full max-md:max-w-full">
                      <div className="flex justify-between items-start w-full max-md:max-w-full">
                        <header className="flex items-center min-w-60">
                          <img
                            src={selectedNotification.author.profile_picture || "/no-profile-pic.png"}
                            alt={`${selectedNotification.author.name} profile picture`}
                            className="object-contain shrink-0 self-stretch my-auto w-11 aspect-square rounded-[32px]"
                          />
                          <div className="self-stretch my-auto min-w-60 w-[342px]">
                            <div className="flex gap-2 items-center w-full h-[23px]">
                              <div className="flex overflow-hidden gap-2.5 justify-center items-center self-stretch px-3 my-auto">
                                <h2 className="self-stretch my-auto text-sm text-neutral-800">
                                  {selectedNotification.author.name}
                                </h2>
                                <CheckmarkFilled
                                  className={`object-contain shrink-0 self-stretch my-auto aspect-square w-[18px] ${getCheckmarkColorClass(selectedNotification.author.role)}`}
                                  aria-label="Verificado"
                                />
                                <div className="self-stretch my-auto text-[10px] text-black">
                                  •
                                </div>
                                <div className={`flex gap-2.5 justify-center items-center self-stretch px-3 py-1 my-auto text-xs whitespace-nowrap rounded ${getRoleBadgeClasses(selectedNotification.author.role)}`}>
                                  <span className="self-stretch my-auto">
                                    {translateUserRole(selectedNotification.author.role || "member")}
                                  </span>
                                </div>
                              </div>
                            </div>
                          </div>
                        </header>
                      </div>
                      <div className="mt-6 w-full text-sm text-neutral-800 max-md:max-w-full">
                        <div className="flex flex-wrap gap-4 items-center w-full max-md:max-w-full">
                          <h1 className="self-stretch my-auto font-semibold leading-6 text-neutral-800">
                            Título:
                          </h1>
                          <p className="self-stretch my-auto leading-8 text-neutral-800">
                            {selectedNotification.title}
                          </p>
                        </div>
                        <div className="mt-2 w-full max-md:max-w-full">
                          <h2 className="font-semibold leading-6 text-justify text-neutral-800">
                            Descrição:
                          </h2>
                          <p className="mt-2 leading-5 text-neutral-800 max-md:max-w-full whitespace-pre-line">
                            {selectedNotification.description}
                          </p>
                        </div>
                      </div>
                      {selectedNotification.image_url && (
                        <img
                          src={selectedNotification.image_url}
                          alt="Aviso oficial illustration"
                          className="object-contain mt-6 w-full rounded aspect-[2.43] max-md:max-w-full"
                        />
                      )}
                    </div>
                  </article>

                  <section className="flex flex-col justify-center py-8 pr-4 pl-8 w-full text-sm leading-none max-md:pl-5 max-md:max-w-full">
                    <div className="w-full max-w-[698px] max-md:max-w-full">
                      <div className="flex flex-wrap gap-10 items-start w-full max-md:max-w-full">
                        <div className="flex flex-col items-start">
                          <div className="flex gap-2 items-center">
                            <span className="self-stretch my-auto font-medium text-neutral-800">
                              Data publicada:
                            </span>
                            <span className="self-stretch my-auto text-neutral-500">
                              {selectedNotification.stats?.published || selectedNotification.date}
                            </span>
                          </div>
                          <div className="flex gap-2 items-center self-stretch mt-4">
                            <span className="self-stretch my-auto font-medium text-neutral-800">
                              Número de acessos:
                            </span>
                            <span className="self-stretch my-auto text-neutral-500">
                              {selectedNotification.stats?.accesses ?? 0} acessos
                            </span>
                          </div>
                        </div>
                        <div className="flex flex-col w-[198px]">
                          <div className="flex gap-2 items-center self-start">
                            <span className="self-stretch my-auto font-medium text-neutral-800">
                              Curtidas:
                            </span>
                            <span className="self-stretch my-auto text-neutral-500">
                              {selectedNotification.stats?.likes ?? 0} curtidas
                            </span>
                          </div>
                          <div className="flex gap-2 items-center mt-4 w-full">
                            <span className="self-stretch my-auto font-medium text-neutral-800">
                              Comentários:
                            </span>
                            <span className="self-stretch my-auto text-neutral-500">
                              {selectedNotification.stats?.comments ?? 0} comentários
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Botões de ação - Promover e Comentar */}
                    <div className="flex items-center gap-4 mt-10 max-w-[698px] max-md:max-w-full">
                      <button
                        onClick={() => {
                          // Ação de promover
                        }}
                        className="flex items-center gap-2 px-6 py-3 text-gray-600 hover:bg-gray-200 transition-colors cursor-pointer rounded"
                      >
                        <ArrowUp className="h-4 w-4" />
                        <span>Promover</span>
                      </button>
                      <button
                        onClick={() => {
                          setShowCommentsModal(true);
                        }}
                        className="flex items-center gap-2 px-6 py-3 text-gray-600 hover:bg-gray-200 transition-colors cursor-pointer rounded"
                      >
                        <Forum className="h-4 w-4" />
                        <span>Comentar</span>
                      </button>
                    </div>
                  </section>
                </main>
              </div>
            </div>
          </div>
        )}

        {/* Right Section - ConnectionsList Layout for Conexões */}
        {activeTab === "Conexões" && (
          <div className="flex-1 bg-white px-6 py-8 fixed top-6 right-0 bottom-0 left-[calc(300px+320px)] overflow-y-auto no-scrollbar">
            <div className="max-w-[680px]">
              {/* Header Section */}
              <header className="flex flex-wrap gap-10 justify-between items-center py-2.5 pr-6 pl-4 w-full max-md:pr-5 max-md:max-w-full">
                <nav className="flex gap-4 items-center self-stretch my-auto whitespace-nowrap min-w-60 w-[385px]">
                  <h1 className="self-stretch my-auto text-sm leading-none text-neutral-600">
                    Conexões
                  </h1>
                  <div className="self-stretch my-auto text-[10px] text-black font-semibold">
                    •
                  </div>
                  <div className="flex gap-4 items-center self-stretch my-auto">
                    <span className="self-stretch my-auto text-sm leading-none text-neutral-600">
                      Pendentes
                    </span>
                    <div className="flex gap-2.5 justify-center items-center self-stretch px-2 my-auto w-6 h-6 text-xs font-semibold leading-none text-gray-200 rounded-2xl bg-zinc-900">
                      <span className="self-stretch my-auto">
                        {pendingCount}
                      </span>
                    </div>
                  </div>
                </nav>
                <div className="flex gap-2 items-center self-stretch my-auto">
                  <button type="button" aria-label="Filtrar">
                    <Filter className="object-contain shrink-0 self-stretch my-auto w-5 aspect-square text-[#525252]" />
                  </button>
                  <button type="button" aria-label="Ordenar">
                    <SortDescending className="object-contain shrink-0 self-stretch my-auto w-5 aspect-square text-[#525252]" />
                  </button>
                </div>
              </header>

              {/* Connections List Section */}
              <section className="mt-6 w-full max-md:max-w-full">
                {connections.length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-16 text-neutral-500">
                    <span className="text-lg">Nenhuma conexão encontrada no momento.</span>
                  </div>
                ) : (
                  connections.map((connection) => (
                    <article
                      key={connection.id}
                      className={`flex flex-col justify-center px-6 py-4 w-full bg-white max-md:px-5 max-md:max-w-full ${connection.connection_status === 'pending' ? 'hover:bg-zinc-100 transition-colors' : ''}`}
                    >
                      <div className="w-full max-md:max-w-full">
                        <time className="text-xs leading-loose text-neutral-600 max-md:max-w-full">
                          {connection.created_at ? new Date(connection.created_at).toLocaleString('pt-BR') : ''}
                        </time>
                        <div className="mt-2 w-full max-md:max-w-full">
                          <div className="flex flex-wrap gap-6 items-start w-full max-md:max-w-full">
                            <p className="flex-1 shrink text-base text-black basis-8 max-md:max-w-full">
                              {connection.title}
                            </p>
                            {connection.connection_status === 'pending' && (
                              <>
                                <button
                                  onClick={() => handleConnect(connection.id)}
                                  className="flex gap-8 items-center px-4 py-2 text-sm leading-6 whitespace-nowrap bg-neutral-800 text-zinc-100 hover:bg-neutral-700 transition-colors"
                                >
                                  <span className="self-stretch my-auto text-zinc-100">
                                    Conectar-se
                                  </span>
                                </button>
                                <button
                                  onClick={() => handleReject(connection.id)}
                                  className="flex gap-8 items-center px-4 py-3 w-12 bg-neutral-200 hover:bg-neutral-300 transition-colors"
                                  aria-label="Rejeitar conexão"
                                >
                                  <Close className="object-contain self-stretch my-auto w-4 aspect-square" aria-label="Fechar" />
                                </button>
                              </>
                            )}
                          </div>
                          <p className="mt-1 text-xs leading-loose text-neutral-600 max-md:max-w-full">
                            @{connection.author?.username}
                          </p>
                          <p className="mt-1 text-xs leading-loose text-neutral-600 max-md:max-w-full">
                            Comunidade: {connection.community?.name}
                          </p>
                        </div>
                      </div>
                    </article>
                  ))
                )}
              </section>
            </div>
          </div>
        )}

        {/* Right Section - Interactions Layout */}
        {activeTab === "Interações" && (
          <div className="flex-1 bg-white px-6 py-8 fixed top-6 right-0 bottom-0 left-[calc(300px+320px)] overflow-y-auto no-scrollbar">
            <section className="max-w-[680px]">
              {/* Header Section */}
              <header className="flex flex-wrap gap-10 justify-between items-center py-2.5 pr-6 pl-4 w-full max-md:pr-5 max-md:max-w-full">
                <div className="flex gap-4 items-center self-stretch my-auto whitespace-nowrap">
                  <h1 className="self-stretch my-auto text-sm leading-none text-neutral-600">
                    Interações
                  </h1>
                  <div className="flex gap-2.5 justify-center items-center self-stretch px-2 my-auto w-6 h-6 text-xs font-semibold leading-none text-gray-200 rounded-2xl bg-zinc-900">
                    <span className="self-stretch my-auto">
                      {interactionsCount}
                    </span>
                  </div>
                </div>
                <nav className="flex gap-2 items-center self-stretch my-auto">
                  <button type="button" aria-label="Filtrar">
                    <Filter className="object-contain shrink-0 self-stretch my-auto w-5 aspect-square text-[#525252]" />
                  </button>
                  <button type="button" aria-label="Ordenar">
                    <SortDescending className="object-contain shrink-0 self-stretch my-auto w-5 aspect-square text-[#525252]" />
                  </button>
                </nav>
              </header>

              {/* Interactions List Section */}
              <main className="mt-6 w-full max-md:max-w-full">
                {interactions.length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-16 text-neutral-500">
                    <span className="text-lg">Nenhuma interação encontrada no momento.</span>
                  </div>
                ) : (
                  interactions.map((interaction) => (
                    <article
                      key={interaction.id}
                      className="flex flex-wrap gap-4 items-center px-6 py-4 w-full max-md:px-5 max-md:max-w-full"
                    >
                      <img
                        src={interaction.author.profile_picture || "/no-profile-pic.png"}
                        alt={`Avatar de ${interaction.author.name}`}
                        className="object-contain shrink-0 self-stretch my-auto w-11 aspect-square rounded-[32px]"
                      />
                      <div className="flex-1 shrink self-stretch my-auto text-xs basis-8 min-w-60 text-neutral-600 max-md:max-w-full">
                        <div className="w-full max-md:max-w-full">
                          <div className="flex gap-6 items-start w-full text-base text-black max-md:max-w-full">
                            <p className="flex-1 shrink basis-0 max-md:max-w-full">
                              {interaction.title}
                            </p>
                          </div>
                          <p className="mt-1 leading-loose text-neutral-600 max-md:max-w-full">
                            @{interaction.author.username}
                          </p>
                          <p className="mt-1 leading-loose text-neutral-600 max-md:max-w-full">
                            Comunidade: {interaction.community.name}
                          </p>
                        </div>
                        <time className="mt-2 leading-loose text-neutral-600 max-md:max-w-full">
                          {interaction.created_at ? new Date(interaction.created_at).toLocaleString('pt-BR') : interaction.date}
                        </time>
                      </div>
                      {interaction.interaction_type === 'comment' && (
                        <button
                          onClick={() => handleLikeInteraction(interaction.id)}
                          className="flex gap-8 items-center self-stretch px-4 py-2 my-auto text-sm leading-6 whitespace-nowrap bg-neutral-800 text-zinc-100 hover:bg-neutral-700 transition-colors"
                        >
                          <span className="self-stretch my-auto text-zinc-100">
                            Curtir
                          </span>
                        </button>
                      )}
                    </article>
                  ))
                )}
              </main>
            </section>
          </div>
        )}

        {/* Modal de comentários para avisos oficiais */}
        {selectedNotification && activeTab === "Avisos oficiais" && (
          <AnnouncementCommentsModal
            isOpen={showCommentsModal}
            onClose={() => setShowCommentsModal(false)}
            announcementId={selectedNotification.id}
            communityId={selectedNotification.community?.id || "default-community-id"}
          />
        )}
      </div>
    </div>
  )
}
