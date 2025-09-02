"use client";

import React, { useState, useEffect, useRef } from "react";
import { ArrowLeft, Filter, Eye } from "lucide-react";
import Link from "next/link";
import { toast } from "react-toastify";
import Sidebar from "@/components/ui/sidebar";
import ApproveCampaignModal from "@/components/modals/community/ApproveCampaignModal";
import RejectCampaignModal from "@/components/modals/community/RejectCampaignModal";
import { useAuth } from "@/app/api/src/auth/useAuth";
import useCommunityById from "@/app/api/src/hooks/community/useCommunityById";
import useCommunityUserActions from "@/app/api/src/hooks/community/useCommunityUserActions";
import useCommunityPosts from "@/app/api/src/hooks/post/useCommunityPosts";
import useCampaignDetails from "@/app/api/src/hooks/post/useCampaignDetails";
import { PostResponse } from "@/app/api/src/types/posts/Post";
import { translateUserRole } from "@/lib/roleTranslations";
import {
  PendenteBadge,
  EmAnaliseBadge,
  AprovadaBadge,
  RejeitadaBadge,
  EmProgressoBadge,
  CanceladaBadge,
  FinalizadaBadge
} from "@/components/badges/campaign/CampaignBadges";
import { LeveBadge, ModeradaBadge, CriticaBadge } from "@/components/badges/complaints/ComplaintsBadges";
import RejectComplaintModal from "@/components/modals/community/RejectComplaintModal";
import ApproveComplaintModal from "@/components/modals/community/ApproveComplaintModal";
import { ChevronSort, Email } from "@carbon/icons-react";

type UserInfo = {
  id: string;
  name: string;
  profile_picture?: string | null;
  role?: string;
};

type Campaign = {
  id: string;
  title: string;
  leader: string;
  user: UserInfo;
  participants: number;
  date: string;
  status: "Em análise" | "Aprovado" | "Rejeitado" | "Pendente" | "Em progresso" | "Cancelada" | "Finalizada";
  description?: string;
  accesses?: number;
  likes?: number;
  comments?: number;
  image?: string;
};

type Report = {
  id: number;
  title: string;
  reporter: string;
  user: UserInfo;
  reported: string;
  date: string;
  status: "Em análise" | "Resolvido" | "Arquivado";
  description?: string;
  category: string;
  severity: "Crítica" | "Moderada" | "Leve";
  confirmations: number;
  image?: string;
  likes?: number;
  comments?: number;
  accesses?: number;
};

type Announcement = {
  id: number;
  title: string;
  author: string;
  user: UserInfo;
  date: string;
  status: "Rascunho" | "Publicado" | "Agendado";
  views?: number;
  description?: string;
  image?: string;
  likes?: number;
  comments?: number;
};

export default function CommunityAdminPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { user } = useAuth();
  const { id } = React.use(params);
  // Hook para buscar dados da comunidade específica
  const {
    community,
    loading: communityLoading,
    error: communityError,
    fetchCommunity,
  } = useCommunityById(); // Hook para gerenciar usuários da comunidade
  const {
    isLoading: isUserActionLoading,
    members,
    pagination,
    loadMembers,
    addModeratorByEmail,
    removeUserById,
    // updateUserRole, // COMENTADO TEMPORARIAMENTE
    importUsers,
  } = useCommunityUserActions({
    onSuccess: () => {
      // Limpar os campos após sucesso
      setNewModeratorEmail("");
      setExcludeUserEmail("");
      setEmailsToImport("");
      // O toast já é exibido no hook, mas podemos adicionar lógica extra aqui se necessário
    },
    onError: (error) => {
      toast.error("Erro ao realizar ação: " + error.message);
      // O toast de erro já é exibido no hook
    },
  });

  // Hook para buscar posts da comunidade (campanhas, denúncias, anúncios)
  const {
    campaigns: apiCampaigns,
    reports: apiReports,
    announcements: apiAnnouncements,
    loading: postsLoading,
    error: postsError,
    fetchCommunityPosts,
  } = useCommunityPosts();

  // Hook para buscar detalhes específicos de campanhas
  const {
    campaignDetails,
    loading: campaignDetailsLoading,
    error: campaignDetailsError,
    fetchCampaignDetailsById,
    clearDetails,
  } = useCampaignDetails();

  // Estados existentes
  const [activeTab, setActiveTab] = useState("Campanhas");
  const [selectedCampaign, setSelectedCampaign] = useState<Campaign | null>(
    null
  );
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);
  const [selectedAnnouncement, setSelectedAnnouncement] =
    useState<Announcement | null>(null);
  const [isApproveModalOpen, setIsApproveModalOpen] = useState(false);
  const [isRejectModalOpen, setIsRejectModalOpen] = useState(false);
  const [newModeratorEmail, setNewModeratorEmail] = useState("");
  const [excludeUserEmail, setExcludeUserEmail] = useState("");
  // Estados para importação em lote
  const [emailsToImport, setEmailsToImport] = useState("");
  const [hasLoadedMembers, setHasLoadedMembers] = useState(false);
  const loadMembersRef = useRef(loadMembers);

  // Buscar dados da comunidade quando o componente monta ou o ID muda
  useEffect(() => {
    if (id) {
      fetchCommunity(id);
      fetchCommunityPosts(id);
    }
  }, [id, fetchCommunity, fetchCommunityPosts]); // Carregar membros quando a aba de usuários for ativa
  useEffect(() => {
    if (id && activeTab === "Usuários" && !hasLoadedMembers) {
      loadMembersRef.current(id);
      setHasLoadedMembers(true);
    }
  }, [id, activeTab, hasLoadedMembers]); // Sem dependência de loadMembers

  // Atualizar ref quando loadMembers mudar
  useEffect(() => {
    loadMembersRef.current = loadMembers;
  }, [loadMembers]);
  const tabs = ["Campanhas", "Denúncias", "Usuários", "Anúncios"];

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

  // Funções auxiliares para converter dados da API para o formato do componente
  const convertPostToCampaign = (post: PostResponse): Campaign => ({
    id: post.id,
    title: post.title,
    leader: post.user.name,
    user: {
      id: post.user.id,
      name: post.user.name,
      profile_picture: post.user.profile_picture,
      role: post.user.role,
    },
    participants: 0, // Zerar participantes temporariamente
    date: new Date(post.created_at).toLocaleDateString("pt-BR"),
    status: mapApiStatusToFrontendStatus(post.status),
    description: post.content,
    accesses: 0,
    likes: post.likes_count || 0,
    comments: post.comments_count || 0,
    image: post.image_url || undefined,
  });

  const convertPostToReport = (post: PostResponse): Report => ({
    id: parseInt(post.id) || 0,
    title: post.title,
    reporter: post.user.name,
    user: {
      id: post.user.id,
      name: post.user.name,
      profile_picture: post.user.profile_picture,
      role: post.user.role,
    },
    reported: "Usuário Denunciado", // Placeholder - ajustar conforme API
    date: new Date(post.created_at).toLocaleDateString("pt-BR"),
    status: post.status === "active" ? "Em análise" : "Resolvido",
    description: post.content,
    category: "Comportamento", // Placeholder - ajustar conforme API
    severity: "Moderada" as const, // Placeholder - ajustar conforme API
    confirmations: post.report_count || 0,
    image: post.image_url || undefined,
    likes: post.likes_count || 0,
    comments: post.comments_count || 0,
    accesses: 0,
  });

  const convertPostToAnnouncement = (post: PostResponse): Announcement => ({
    id: parseInt(post.id) || 0,
    title: post.title,
    author: post.user.name,
    user: {
      id: post.user.id,
      name: post.user.name,
      profile_picture: post.user.profile_picture,
      role: post.user.role,
    },
    date: new Date(post.created_at).toLocaleDateString("pt-BR"),
    status: post.status === "active" ? "Publicado" : "Rascunho",
    views: 0, // Não existe campo de views no backend, manter 0 ou ajustar se backend mudar
    likes: post.likes_count ?? 0,
    comments: post.comments_count ?? 0,
    description: post.content,
    image: post.image_url || undefined,
  });
  // Converter dados da API para o formato esperado pelos componentes
  const campaigns: Campaign[] = apiCampaigns.map(convertPostToCampaign);
  const reports: Report[] = apiReports.map(convertPostToReport);
  const announcements: Announcement[] = apiAnnouncements.map(
    convertPostToAnnouncement
  );

  // Mostrar toast de erro se houver problema ao carregar posts
  useEffect(() => {
    if (postsError) {
      toast.error("Erro ao carregar dados da comunidade. Tente novamente.");
    }
  }, [postsError]);

  // Set default selected items when changing tabs
  const handleTabChange = (tab: string) => {
    setActiveTab(tab);

    // Reset all selected items
    setSelectedCampaign(null);
    setSelectedReport(null);
    setSelectedAnnouncement(null);
    clearDetails(); // Limpar detalhes da campanha

    // Set the first item of the active tab as selected
    if (tab === "Campanhas" && campaigns.length > 0) {
      setSelectedCampaign(campaigns[0]);
    } else if (tab === "Denúncias" && reports.length > 0) {
      setSelectedReport(reports[0]);
    } else if (tab === "Anúncios" && announcements.length > 0) {
      setSelectedAnnouncement(announcements[0]);
    }
  };

  // Função para buscar detalhes da campanha quando selecionada
  const handleCampaignSelection = async (campaign: Campaign) => {
    setSelectedCampaign(campaign);
    if (id) {
      try {
        await fetchCampaignDetailsById(id, campaign.id);
      } catch (error) {
        toast.error("Erro ao carregar detalhes da campanha");
      }
    }
  };

  // Initialize default selected items if none are selected
  if (activeTab === "Campanhas" && !selectedCampaign && campaigns.length > 0) {
    const firstCampaign = campaigns[0];
    setSelectedCampaign(firstCampaign);
    // Buscar detalhes da primeira campanha automaticamente
    if (id) {
      fetchCampaignDetailsById(id, firstCampaign.id).catch(error => {
        toast.error("Erro ao carregar detalhes da campanha");
      });
    }
  } else if (
    activeTab === "Denúncias" &&
    !selectedReport &&
    reports.length > 0
  ) {
    setSelectedReport(reports[0]);
  } else if (
    activeTab === "Anúncios" &&
    !selectedAnnouncement &&
    announcements.length > 0
  ) {
    setSelectedAnnouncement(announcements[0]);
  }
  const handleApproveCampaign = (subject: string, message: string) => {
    console.log("Approving campaign with:", {
      subject,
      message,
      communityId: id,
    });
    if (selectedCampaign) {
      const updatedCampaign = {
        ...selectedCampaign,
        status: "Aprovado" as const,
      };
      setSelectedCampaign(updatedCampaign);
    }
    setIsApproveModalOpen(false);
  };

  const handleRejectCampaign = (subject: string, reason: string) => {
    console.log("Rejecting campaign with:", {
      subject,
      reason,
      communityId: id,
    });
    if (selectedCampaign) {
      const updatedCampaign = {
        ...selectedCampaign,
        status: "Rejeitado" as const,
      };
      setSelectedCampaign(updatedCampaign);
    }
    setIsRejectModalOpen(false);
  };
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "Crítica":
        return "bg-[#fff1f1] text-[#da1e28]";
      case "Moderada":
        return "bg-[#fff8e1] text-[#b28600]";
      case "Leve":
        return "bg-[#defbe6] text-[#0e6027]";
      default:
        return "bg-[#f4f4f4] text-[#525252]";
    }
  };

  // Função para mapear status da campanha para o componente de badge correto
  const getCampaignStatusBadge = (status: string) => {
    switch (status) {
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
  // Handlers para gerenciamento de usuários
  const handleAddModerator = async () => {
    if (!newModeratorEmail.trim()) {
      toast.error("Por favor, digite um email válido");
      return;
    }

    if (!id) {
      toast.error("ID da comunidade não encontrado");
      return;
    }

    await addModeratorByEmail(id, newModeratorEmail, "moderator");
  };

  const handleRemoveUser = async () => {
    if (!excludeUserEmail.trim()) {
      toast.error("Por favor, digite um email válido");
      return;
    }

    if (!id) {
      toast.error("ID da comunidade não encontrado");
      return;
    }

    // Encontrar o membro pelo email
    const memberToRemove = members.find(
      (member) =>
        member.user.email.toLowerCase() ===
        excludeUserEmail.trim().toLowerCase()
    );

    if (!memberToRemove) {
      toast.error("Usuário não encontrado na comunidade");
      return;
    } // Confirmação antes de excluir
    const confirmRemoval = window.confirm(
      `Tem certeza que deseja excluir o usuário "${memberToRemove.user.name}" (${memberToRemove.user.email})? Esta ação é permanente e não pode ser desfeita.`
    );
    if (confirmRemoval) {
      await removeUserById(id, id, memberToRemove.user_id);
    }
  };

  const handleImportUsers = async () => {
    if (!emailsToImport.trim()) {
      toast.error("Por favor, digite os emails para importar");
      return;
    }

    if (!id) {
      toast.error("ID da comunidade não encontrado");
      return;
    }

    const emails = emailsToImport
      .split(/[,\n]/)
      .map((e) => e.trim())
      .filter((e) => e);

    if (emails.length === 0) {
      toast.error("Nenhum email válido encontrado");
      return;
    }
    await importUsers(id, emails);
    setEmailsToImport("");
  };

  // Função para mapear severidade para o badge correto
  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case "Leve":
        return <LeveBadge />;
      case "Moderada":
        return <ModeradaBadge />;
      case "Crítica":
        return <CriticaBadge />;
      default:
        return <LeveBadge />;
    }
  };

  // Estados para modais de denúncia
  const [isDissolveModalOpen, setIsDissolveModalOpen] = useState(false);
  const [isResolveModalOpen, setIsResolveModalOpen] = useState(false);

  // Handlers para ações de denúncia
  const handleDissolveReport = () => {
    setIsDissolveModalOpen(true);
  };

  const handleResolveReport = () => {
    setIsResolveModalOpen(true);
  };

  return (
    <div className="min-h-screen bg-gray-100 text-[#161616]">
      <Sidebar variant="static" />
      <div className="flex">
        {/* Left Navigation - Fixed */}
        <div className="fixed left-64 top-1 w-64 bg-white border-r border-[#e0e0e0] h-screen z-20 overflow-y-auto">
          {/* Header */}
          <div className="sticky top-0 p-6 border-b border-[#e0e0e0] bg-white">
            <div className="flex items-center gap-3 mb-4">
              <Link href="/administration" className="p-1 hover:bg-[#e5e5e5]">
                <ArrowLeft className="h-5 w-5 text-[#525252]" />
              </Link>
              <div>
                {community ? (
                  <h1 className="text-lg font-medium">{community.name}</h1>
                ) : (
                  <>
                    <h1 className="text-lg font-medium">Título da</h1>
                    <h1 className="text-lg font-medium">Comunidade</h1>
                  </>
                )}
                {communityLoading && (
                  <p className="text-sm text-[#525252]">Carregando...</p>
                )}
                {communityError && (
                  <p className="text-sm text-red-500">Erro ao carregar</p>
                )}
              </div>
            </div>
          </div>
          {/* Navigation Tabs */}
          <nav className="py-4">
            {tabs.map((tab) => (
              <button
                key={tab}
                className={`w-full px-6 py-3 text-left hover:bg-[#f8f8f8] cursor-pointer ${activeTab === tab
                  ? "bg-[#f4f4f4] border-r-4 border-black text-[#161616]"
                  : "text-[#525252]"
                  }`}
                onClick={() => handleTabChange(tab)}
              >
                {tab}
              </button>
            ))}
          </nav>
        </div>
        {/* Main Content Area */}
        <div className="ml-[512px] flex-1">
          {/* Middle Section - Content List (only for Campanhas, Denúncias, Anúncios) */}
          {activeTab !== "Usuários" && (
            <div className="w-80 fixed top-0 bottom-0 left-[512px] bg-white border-r border-[#e0e0e0] overflow-y-auto z-10 no-scrollbar">
              {/* Header with filters */}
              <div className="sticky top-0 p-4 border-b border-[#e0e0e0] flex items-center gap-2 bg-white z-20">
                <button className="p-2 hover:bg-[#f4f4f4]">
                  //TODO: colocar icone do carbon do filter
                  <Filter className="h-4 w-4 text-[#525252]" />
                </button>
                <button className="p-2 hover:bg-[#f4f4f4]">
                  <ChevronSort className="h-4 w-4 text-[#525252]" />
                </button>
                {activeTab === "Anúncios" && (
                  <button className="ml-auto px-3 min-w-[138px] min-h-[56px] py-1.5 bg-[#161616] text-white text-sm hover:bg-[#262626] flex items-center gap-10">
                    Anunciar
                    <Email className="h-4 w-4" />
                  </button>
                )}
              </div>
              {/* Content List */}
              <div className="h-full overflow-y-auto pb-20">
                {/* Loading State */}
                {postsLoading && (
                  <div className="p-4 text-center">
                    <div className="flex items-center justify-center">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#161616]"></div>
                    </div>
                    <p className="text-sm text-[#525252] mt-2">
                      Carregando dados...
                    </p>
                  </div>
                )}
                {/* Error State */}
                {postsError && !postsLoading && (
                  <div className="p-4 text-center">
                    <p className="text-sm text-red-500 mb-2">
                      Erro ao carregar dados
                    </p>
                    <button
                      onClick={() => id && fetchCommunityPosts(id)}
                      className="text-sm text-[#161616] hover:underline"
                    >
                      Tentar novamente
                    </button>
                  </div>
                )}
                {/* Empty State */}
                {!postsLoading && !postsError && (
                  <>
                    {activeTab === "Campanhas" && campaigns.length === 0 && (
                      <div className="p-4 text-center">
                        <p className="text-sm text-[#525252]">
                          Nenhuma campanha encontrada
                        </p>
                      </div>
                    )}

                    {activeTab === "Denúncias" && reports.length === 0 && (
                      <div className="p-4 text-center">
                        <p className="text-sm text-[#525252]">
                          Nenhuma denúncia encontrada
                        </p>
                      </div>
                    )}

                    {activeTab === "Anúncios" && announcements.length === 0 && (
                      <div className="p-4 text-center">
                        <p className="text-sm text-[#525252]">
                          Nenhum anúncio encontrado
                        </p>
                      </div>
                    )}
                  </>
                )}
                {/* Campaigns List */}
                {activeTab === "Campanhas" &&
                  !postsLoading &&
                  campaigns.length > 0 &&
                  campaigns.map((campaign) => (
                    <div
                      key={campaign.id}
                      className={`p-4 border-b border-[#e0e0e0] cursor-pointer hover:bg-[#f8f8f8] ${selectedCampaign?.id === campaign.id
                        ? "bg-[#f4f4f4]"
                        : ""
                        }`}
                      onClick={() => handleCampaignSelection(campaign)}
                    >
                      <div className="mb-2">
                        <h3 className="font-medium text-sm mb-1">
                          {campaign.title}
                        </h3>
                        <p className="text-xs text-[#525252] mb-1">
                          Líder: {campaign.leader}
                        </p>
                        <p className="text-xs text-[#525252] mb-2">
                          {campaign.participants.toLocaleString()} participantes
                        </p>
                        <p className="text-xs text-[#525252] mb-2">
                          {campaign.date}
                        </p>
                      </div>
                      <div className="flex items-center justify-between">
                        {getCampaignStatusBadge(campaign.status)}
                        <div className="flex items-center gap-1">
                          <span className="text-xs text-[#525252]">0</span>
                          <Eye className="h-3 w-3 text-[#525252]" />
                        </div>
                      </div>
                    </div>
                  ))}{" "}
                {/* Reports List */}
                {activeTab === "Denúncias" &&
                  !postsLoading &&
                  reports.length > 0 &&
                  reports.map((report) => (
                    <div
                      key={report.id}
                      className={`p-4 border-b border-[#e0e0e0] cursor-pointer hover:bg-[#f8f8f8] ${selectedReport?.id === report.id ? "bg-[#f4f4f4]" : ""
                        }`}
                      onClick={() => setSelectedReport(report)}
                    >
                      <div className="mb-2">
                        <h3 className="font-medium text-sm mb-1">
                          {report.title}
                        </h3>
                        <p className="text-xs text-[#525252] mb-1">
                          Denunciante: {report.reporter}
                        </p>
                        <p className="text-xs text-[#525252] mb-2">
                          {report.confirmations} confirmações
                        </p>
                        <p className="text-xs text-[#525252] mb-2">
                          {report.date}
                        </p>
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="mr-2">{getSeverityBadge(report.severity)}</div>
                        <div className="flex items-center gap-1">
                          <span className="text-xs text-[#525252]">0</span>
                          <Eye className="h-3 w-3 text-[#525252]" />
                        </div>
                      </div>
                    </div>
                  ))}{" "}
                {/* Announcements List */}
                {activeTab === "Anúncios" &&
                  !postsLoading &&
                  announcements.length > 0 &&
                  announcements.map((announcement) => (
                    <div
                      key={announcement.id}
                      className={`p-4 border-b border-[#e0e0e0] cursor-pointer hover:bg-[#f8f8f8] ${selectedAnnouncement?.id === announcement.id
                        ? "bg-[#f4f4f4]"
                        : ""
                        }`}
                      onClick={() => setSelectedAnnouncement(announcement)}
                    >
                      <div className="mb-2">
                        <p className="text-xs text-[#525252] mb-1">
                          {announcement.date}
                        </p>
                        <h3 className="font-medium text-sm mb-1">
                          {announcement.title}
                        </h3>
                        <p className="text-xs text-[#525252] mb-2">
                          Administrador: {announcement.author}
                        </p>{" "}
                      </div>
                      <div className="flex items-center gap-1">
                        <span className="text-xs text-[#525252]">{announcement.views || 0}</span>
                        <Eye className="h-3 w-3 text-[#525252]" />
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          )}
          {/* Right Section - Details */}
          <div className="flex-1 bg-gray-100 px-6 py-8 fixed top-0 right-0 bottom-0 left-[calc(512px+320px)] overflow-y-auto no-scrollbar">
            {/* Loading State for Details */}
            {postsLoading && activeTab !== "Usuários" && (
              <div className="bg-white p-6 text-center">
                <div className="flex items-center justify-center mb-4">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#161616]"></div>
                </div>
                <p className="text-sm text-[#525252]">Carregando detalhes...</p>
              </div>
            )}
            {/* No Selection State */}
            {!postsLoading && activeTab !== "Usuários" && (
              <>
                {activeTab === "Campanhas" &&
                  !selectedCampaign &&
                  campaigns.length > 0 && (
                    <div className="bg-white p-6 text-center">
                      <p className="text-sm text-[#525252]">
                        Selecione uma campanha para ver os detalhes
                      </p>
                    </div>
                  )}

                {activeTab === "Denúncias" &&
                  !selectedReport &&
                  reports.length > 0 && (
                    <div className="bg-white p-6 text-center">
                      <p className="text-sm text-[#525252]">
                        Selecione uma denúncia para ver os detalhes
                      </p>
                    </div>
                  )}

                {activeTab === "Anúncios" &&
                  !selectedAnnouncement &&
                  announcements.length > 0 && (
                    <div className="bg-white p-6 text-center">
                      <p className="text-sm text-[#525252]">
                        Selecione um anúncio para ver os detalhes
                      </p>
                    </div>
                  )}
              </>
            )}{" "}
            {/* Campaign Details - Updated with Figma Layout */}
            {activeTab === "Campanhas" && selectedCampaign && !postsLoading && (
              <div className="max-w-full">
                <div className="px-4 pt-4 pb-80 w-full bg-zinc-100 max-md:pb-24 max-md:max-w-full">
                  <article className="mb-0 bg-white max-md:mb-2.5 max-md:max-w-full">
                    <header className="flex flex-col justify-center p-8 w-full bg-white rounded max-md:px-5 max-md:max-w-full">
                      <div className="w-full max-md:max-w-full">
                        <div className="flex justify-between items-start w-full max-md:max-w-full">
                          <div className="flex items-center min-w-60">
                            <img
                              src={selectedCampaign.user.profile_picture || "/no-profile-pic.png"}
                              alt={`${selectedCampaign.user.name} profile picture`}
                              className="object-contain shrink-0 self-stretch my-auto w-11 aspect-square"
                            />
                            <div className="self-stretch my-auto min-w-60 w-[342px]">
                              <div className="flex gap-2 items-center w-full h-[23px]">
                                <div className="flex overflow-hidden gap-2.5 justify-center items-center self-stretch px-3 my-auto">
                                  <span className="self-stretch my-auto text-sm text-neutral-800">
                                    {selectedCampaign.leader}
                                  </span>
                                  <img
                                    src="https://api.builder.io/api/v1/image/assets/2c92ea9fbec34a758f970e8cafff5cb1/0915c1f8d702c90f4deafed21adc581f37a91002?placeholderIfAbsent=true"
                                    alt="Verification badge"
                                    className="object-contain shrink-0 self-stretch my-auto aspect-square w-[18px]"
                                  />
                                  <div className="flex gap-2.5 justify-center items-center self-stretch px-3 py-1 my-auto text-xs whitespace-nowrap rounded bg-neutral-800 text-zinc-100">
                                    <span className="self-stretch my-auto text-zinc-100">
                                      {translateUserRole(selectedCampaign.user.role || "leader")}
                                    </span>
                                  </div>
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
                              {selectedCampaign.title}
                            </span>
                          </div>
                          <div className="mt-2 w-full max-md:max-w-full">
                            <h3 className="font-semibold leading-6 text-justify text-neutral-800">
                              Descrição:
                            </h3>
                            <p className="mt-2 leading-5 text-neutral-800 max-md:max-w-full">
                              {selectedCampaign.description}
                            </p>
                          </div>
                        </div>
                      </div>
                    </header>
                    <section className="flex flex-col py-8 pr-4 pl-8 w-full max-md:pl-5 max-md:max-w-full">
                      <div className="w-full text-sm leading-none max-md:max-w-full">
                        <div className="flex flex-wrap gap-36 items-start w-full max-md:max-w-full">
                          <div className="flex flex-col items-start">
                            <div className="flex gap-2 items-center">
                              <span className="self-stretch my-auto font-medium text-neutral-800">
                                Data publicada:
                              </span>
                              <span className="self-stretch my-auto text-neutral-500">
                                {selectedCampaign.date}
                              </span>
                            </div>
                            <div className="flex gap-2 items-center self-stretch mt-4">
                              <span className="self-stretch my-auto font-medium text-neutral-800">
                                Número de acessos:
                              </span>
                              <span className="self-stretch my-auto text-neutral-500">
                                {campaignDetails?.views_count || selectedCampaign.accesses || 0} acessos
                              </span>
                            </div>
                            <div className="flex gap-2 items-center mt-4">
                              <span className="self-stretch my-auto font-medium text-neutral-800">
                                Participantes:
                              </span>
                              <span className="self-stretch my-auto text-neutral-500">
                                {campaignDetails?.participants_count || selectedCampaign.participants || 0} pessoas
                              </span>
                            </div>
                          </div>
                          <div className="flex flex-col w-[198px]">
                            <div className="flex gap-2 items-center self-start">
                              <span className="self-stretch my-auto font-medium text-neutral-800">
                                Curtidas:
                              </span>
                              <span className="self-stretch my-auto text-neutral-500">
                                {campaignDetails?.likes_count || selectedCampaign.likes || 0} curtidas
                              </span>
                            </div>
                            <div className="flex gap-2 items-center mt-4 w-full">
                              <span className="self-stretch my-auto font-medium text-neutral-800">
                                Comentários:
                              </span>
                              <span className="self-stretch my-auto text-neutral-500">
                                {campaignDetails?.comments_count || selectedCampaign.comments || 0} comentários
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div className="flex gap-2 items-center self-start mt-10">
                        <span className="self-stretch my-auto text-sm font-medium leading-none text-neutral-800">
                          Status:
                        </span>
                        {campaignDetailsLoading ? (
                          <div className="flex items-center gap-2">
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-neutral-800"></div>
                            <span className="text-sm text-neutral-500">Carregando...</span>
                          </div>
                        ) : (
                          getCampaignStatusBadge(selectedCampaign.status)
                        )}
                      </div>
                      {selectedCampaign.status === "Em análise" && (
                        <div className="flex flex-wrap gap-2 justify-between items-center mt-10 w-full text-sm leading-6 whitespace-nowrap max-w-[698px] max-md:max-w-full">
                          <button
                            onClick={() => setIsRejectModalOpen(true)}
                            className="flex gap-8 cursor-pointer items-center self-stretch pt-4 pr-16 pb-6 pl-4 my-auto bg-zinc-100 min-w-60 text-neutral-800 w-[345px] max-md:pr-5 hover:bg-zinc-200 transition-colors"
                          >
                            <span className="self-stretch my-auto text-neutral-800">
                              Rejeitar
                            </span>
                          </button>
                          <button
                            onClick={() => setIsApproveModalOpen(true)}
                            className="flex gap-8 cursor-pointer items-center self-stretch pt-4 pr-16 pb-6 pl-4 my-auto bg-neutral-800 min-w-60 text-zinc-100 w-[345px] max-md:pr-5 hover:bg-neutral-700 transition-colors"
                          >
                            <span className="self-stretch my-auto text-zinc-100">
                              Aprovar
                            </span>
                          </button>
                        </div>
                      )}
                    </section>
                  </article>
                </div>
              </div>
            )}
            {/* Report Details - Updated with Figma Layout */}
            {activeTab === "Denúncias" && selectedReport && !postsLoading && (
              <div className="max-w-full">
                <div className="px-4 pt-4 pb-72 w-full bg-zinc-100 max-md:pb-24 max-md:max-w-full">
                  <article className="mb-0 bg-white max-md:mb-2.5 max-md:max-w-full">
                    <div className="flex flex-col justify-center p-8 w-full bg-white rounded max-md:px-5 max-md:max-w-full">
                      <div className="w-full max-md:max-w-full">
                        <div className="flex justify-between items-start w-full max-md:max-w-full">
                          <div className="flex items-center min-w-60">
                            <img
                              src={selectedReport.user.profile_picture || "/no-profile-pic.png"}
                              className="object-contain shrink-0 self-stretch my-auto w-11 aspect-square"
                              alt={`${selectedReport.user.name} avatar`}
                            />
                            <div className="self-stretch my-auto min-w-60 w-[342px]">
                              <div className="flex gap-2 items-center w-full h-[23px]">
                                <div className="flex overflow-hidden gap-2.5 justify-center items-center self-stretch px-3 my-auto">
                                  <span className="self-stretch my-auto text-sm text-neutral-800">
                                    {selectedReport.user.name}
                                  </span>
                                  <img
                                    src="https://api.builder.io/api/v1/image/assets/2c92ea9fbec34a758f970e8cafff5cb1/0915c1f8d702c90f4deafed21adc581f37a91002?placeholderIfAbsent=true"
                                    className="object-contain shrink-0 self-stretch my-auto aspect-square w-[18px]"
                                    alt="Verified"
                                  />
                                  <div className="flex gap-2.5 justify-center items-center self-stretch px-3 py-1 my-auto text-xs whitespace-nowrap rounded bg-neutral-800 text-zinc-100">
                                    <span className="self-stretch my-auto text-zinc-100">
                                      {translateUserRole(selectedReport.user.role || "member")}
                                    </span>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                        <div className="flex flex-col mt-6 w-full max-md:max-w-full">
                          <div className="flex gap-2 items-center self-start whitespace-nowrap">
                            <span className="self-stretch my-auto text-sm font-semibold leading-none text-neutral-800">
                              Nível:
                            </span>
                            <div className="flex gap-2.5 items-start self-stretch my-auto">
                              {getSeverityBadge(selectedReport.severity)}
                            </div>
                          </div>
                          <div className="flex flex-wrap gap-4 items-center mt-2 w-full text-sm text-neutral-800 max-md:max-w-full">
                            <h2 className="self-stretch my-auto font-semibold leading-6 text-neutral-800">
                              Título:
                            </h2>
                            <p className="self-stretch my-auto leading-8 text-neutral-800">
                              {selectedReport.title}
                            </p>
                          </div>
                          <div className="mt-2 w-full text-sm text-neutral-800 max-md:max-w-full">
                            <h3 className="font-semibold leading-6 text-justify text-neutral-800">
                              Descrição:
                            </h3>
                            <p className="mt-2 leading-5 text-neutral-800 max-md:max-w-full">
                              {selectedReport.description || "Descrição não disponível."}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="flex flex-col py-8 pr-4 pl-8 w-full max-md:pl-5 max-md:max-w-full">
                      <section className="w-full text-sm leading-none max-md:max-w-full">
                        <div className="flex flex-wrap gap-36 items-start w-full max-md:max-w-full">
                          <div className="flex flex-col items-start">
                            <div className="flex gap-2 items-center">
                              <span className="self-stretch my-auto font-medium text-neutral-800">
                                Data publicada:
                              </span>
                              <span className="self-stretch my-auto text-neutral-500">
                                {selectedReport.date}
                              </span>
                            </div>
                            <div className="flex gap-2 items-center self-stretch mt-4">
                              <span className="self-stretch my-auto font-medium text-neutral-800">
                                Número de acessos:
                              </span>
                              <span className="self-stretch my-auto text-neutral-500">
                                {selectedReport.accesses || 0} acessos
                              </span>
                            </div>
                            <div className="flex gap-2 items-center mt-4">
                              <span className="self-stretch my-auto font-medium text-neutral-800">
                                Confirmações:
                              </span>
                              <span className="self-stretch my-auto text-neutral-500">
                                {selectedReport.confirmations} pessoas
                              </span>
                            </div>
                          </div>
                          <div className="flex flex-col w-[198px]">
                            <div className="flex gap-2 items-center self-start">
                              <span className="self-stretch my-auto font-medium text-neutral-800">
                                Curtidas:
                              </span>
                              <span className="self-stretch my-auto text-neutral-500">
                                {selectedReport.likes || 0} curtidas
                              </span>
                            </div>
                            <div className="flex gap-2 items-center mt-4 w-full">
                              <span className="self-stretch my-auto font-medium text-neutral-800">
                                Comentários:
                              </span>
                              <span className="self-stretch my-auto text-neutral-500">
                                {selectedReport.comments || 0} comentários
                              </span>
                            </div>
                          </div>
                        </div>
                      </section>
                      <div className="flex gap-2 items-center self-start mt-10 text-neutral-800">
                        <span className="self-stretch my-auto text-sm font-medium leading-none text-neutral-800">
                          Status:
                        </span>
                        <div className="flex gap-2.5 justify-center items-center self-stretch px-3 py-2 my-auto text-xs leading-none rounded-sm bg-zinc-100">
                          <img
                            src="https://api.builder.io/api/v1/image/assets/2c92ea9fbec34a758f970e8cafff5cb1/8c1af7523fbdfb5b8097ae5cb54b499951078f51?placeholderIfAbsent=true"
                            className="object-contain shrink-0 self-stretch my-auto w-4 aspect-square"
                            alt=""
                          />
                          <span className="self-stretch my-auto text-neutral-800">
                            {selectedReport.status}
                          </span>
                        </div>
                      </div>
                      <div className="flex flex-wrap gap-2 justify-between items-center mt-10 w-full text-sm leading-6 whitespace-nowrap max-w-[698px] max-md:max-w-full">
                        <button
                          onClick={handleDissolveReport}
                          className="flex gap-8 cursor-pointer items-center self-stretch pt-4 pr-16 pb-6 pl-4 my-auto bg-zinc-100 min-w-60 text-neutral-800 w-[345px] max-md:pr-5 hover:bg-zinc-200 transition-colors"
                        >
                          <span className="self-stretch my-auto text-neutral-800">
                            Dissolver
                          </span>
                        </button>
                        <button
                          onClick={handleResolveReport}
                          className="flex gap-8 cursor-pointer items-center self-stretch pt-4 pr-16 pb-6 pl-4 my-auto bg-neutral-800 min-w-60 text-zinc-100 w-[345px] max-md:pr-5 hover:bg-neutral-700 transition-colors"
                        >
                          <span className="self-stretch my-auto text-zinc-100">
                            Resolver
                          </span>
                        </button>
                      </div>
                    </div>
                  </article>
                </div>
              </div>
            )}
            {/* Users Management */}
            {activeTab === "Usuários" && (
              <div className="bg-white fixed top-0 right-0 bottom-0 left-[512px] overflow-y-auto">
                <main className="flex flex-col gap-12 items-start px-6 py-6 w-full max-w-[894px]">
                  {/* Header Section */}
                  <header className="flex flex-col gap-1 items-start w-full">
                    <div className="flex gap-2.5 justify-center items-center w-full">
                      <p className="text-xs font-medium flex-[1_0_0] text-neutral-500">
                        Usuários
                      </p>
                    </div>
                    <div className="flex gap-2.5 justify-center items-center w-full">
                      <h1 className="text-xl text-black flex-[1_0_0]">
                        Gerenciamento de Usuários
                      </h1>
                    </div>
                  </header>

                  {/* Import Database Section */}
                  <section className="flex flex-col gap-4 items-start px-0 py-12 w-full border-b border-solid border-b-stone-300">
                    <div className="flex flex-col gap-2 items-start w-full">
                      <h2 className="w-full text-sm font-semibold leading-6 text-neutral-800">
                        Importar base de dados de usuários
                      </h2>
                      <p className="text-sm text-neutral-500">
                        Tamanho máximo do arquivo é 2MB. Tipos de arquivos suportados são .jpg e .png.
                      </p>
                    </div>
                    <button
                      className="flex gap-8 items-center py-3 pr-16 pl-4 cursor-pointer bg-neutral-800 hover:bg-neutral-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      onClick={handleImportUsers}
                      disabled={isUserActionLoading}
                    >
                      <span className="text-sm leading-6 text-zinc-100">
                        {isUserActionLoading ? "Importando..." : "Importar base"}
                      </span>
                    </button>
                  </section>

                  {/* Add Moderator Section */}
                  <section className="flex gap-10 items-start px-0 py-12 w-full border-b border-solid border-b-stone-300">
                    <div className="flex flex-col flex-1 gap-2 items-start">
                      <h2 className="w-full text-sm leading-6 text-neutral-800">
                        Adicionar moderador
                      </h2>
                      <div className="flex gap-8 items-center px-4 py-2 w-full border-b border-solid bg-zinc-100 border-b-neutral-500">
                        <input
                          type="email"
                          value={newModeratorEmail}
                          onChange={(e) => setNewModeratorEmail(e.target.value)}
                          placeholder="Digite o email do usuário"
                          className="text-sm leading-6 text-neutral-500 bg-transparent border-none outline-none w-full placeholder:text-neutral-500"
                          disabled={isUserActionLoading}
                        />
                      </div>
                      <p className="mt-2 text-xs leading-4 text-neutral-500">
                        Ao clicar em adicionar o usuário terá seu papel da comunidade alterado para moderador.
                      </p>
                    </div>
                    <button
                      className="flex gap-2 items-center mt-8 px-4 py-2 cursor-pointer bg-neutral-800 hover:bg-neutral-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      onClick={handleAddModerator}
                      disabled={isUserActionLoading}
                    >
                      <span className="text-sm leading-6 text-zinc-100">
                        {isUserActionLoading ? "Adicionando..." : "Adicionar"}
                      </span>
                      <div>
                        <div
                          dangerouslySetInnerHTML={{
                            __html:
                              "<svg width=\"16\" height=\"17\" viewBox=\"0 0 16 17\" fill=\"none\" xmlns=\"http://www.w3.org/2000/svg\" class=\"add-icon\"> <path d=\"M8.5 8V4.5H7.5V8H4V9H7.5V12.5H8.5V9H12V8H8.5Z\" fill=\"#F4F4F4\"></path> </svg>",
                          }}
                        />
                      </div>
                    </button>
                  </section>

                  {/* Delete User Section */}
                  <section className="flex gap-10 items-start px-0 py-12 w-full border-b border-solid border-b-stone-300">
                    <div className="flex flex-col flex-1 gap-2 items-start">
                      <h2 className="w-full text-sm leading-6 text-neutral-800">
                        Excluir usuário
                      </h2>
                      <div className="flex gap-8 items-center px-4 py-2 w-full border-b border-solid bg-zinc-100 border-b-neutral-500">
                        <input
                          type="email"
                          value={excludeUserEmail}
                          onChange={(e) => setExcludeUserEmail(e.target.value)}
                          placeholder="Digite o email do usuário"
                          className="text-sm leading-6 text-neutral-500 bg-transparent border-none outline-none w-full placeholder:text-neutral-500"
                          disabled={isUserActionLoading}
                        />
                      </div>
                      <p className="mt-2 text-xs text-neutral-500">
                        A exclusão é permanente, então certifique-se de digitar o e-mail corretamente.
                      </p>
                    </div>
                    <button
                      className="flex gap-2 items-center mt-8 px-4 py-2 bg-red-600 cursor-pointer hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      onClick={handleRemoveUser}
                      disabled={isUserActionLoading}
                    >
                      <span className="text-sm leading-6 text-zinc-100">
                        {isUserActionLoading ? "Excluindo..." : "Excluir"}
                      </span>
                      <div>
                        <div
                          dangerouslySetInnerHTML={{
                            __html:
                              "<svg width=\"16\" height=\"17\" viewBox=\"0 0 16 17\" fill=\"none\" xmlns=\"http://www.w3.org/2000/svg\" class=\"close-icon\"> <path d=\"M12 4.86675L11.3 4.16675L8 7.46675L4.7 4.16675L4 4.86675L7.3 8.16675L4 11.4667L4.7 12.1667L8 8.86675L11.3 12.1667L12 11.4667L8.7 8.16675L12 4.86675Z\" fill=\"#F4F4F4\"></path> </svg>",
                          }}
                        />
                      </div>
                    </button>
                  </section>
                </main>
              </div>
            )}
            {/* Announcement Details - Updated with Figma Layout */}
            {activeTab === "Anúncios" && selectedAnnouncement && !postsLoading && (
              <div className="max-w-full">
                <div className="px-4 pt-4 pb-80 w-full bg-zinc-100 max-md:pb-24 max-md:max-w-full">
                  <article className="mb-0 bg-white max-md:mb-2.5 max-md:max-w-full">
                    <header className="flex flex-col justify-center p-8 w-full bg-white rounded max-md:px-5 max-md:max-w-full">
                      <div className="w-full max-md:max-w-full">
                        <div className="flex justify-between items-start w-full max-md:max-w-full">
                          <div className="flex items-center min-w-60">
                            <img
                              src={selectedAnnouncement.user.profile_picture || "/no-profile-pic.png"}
                              alt={`${selectedAnnouncement.user.name} profile picture`}
                              className="object-contain shrink-0 self-stretch my-auto w-11 aspect-square rounded-[32px]"
                            />
                            <div className="self-stretch my-auto min-w-60 w-[342px]">
                              <div className="flex gap-2 items-center w-full h-[23px]">
                                <div className="flex overflow-hidden gap-2.5 justify-center items-center self-stretch px-3 my-auto min-w-60">
                                  <h2 className="self-stretch my-auto text-sm text-neutral-800">
                                    {selectedAnnouncement.author}
                                  </h2>
                                  <img
                                    src="https://api.builder.io/api/v1/image/assets/2c92ea9fbec34a758f970e8cafff5cb1/053d988ba4cfa8562519f55304901c8878c52e86?placeholderIfAbsent=true"
                                    alt="Verification badge"
                                    className="object-contain shrink-0 self-stretch my-auto aspect-square w-[18px]"
                                  />
                                  <span className="flex gap-2.5 justify-center items-center self-stretch px-3 py-1 my-auto text-xs whitespace-nowrap rounded bg-yellow-600 bg-opacity-40 text-yellow-950">
                                    {translateUserRole(selectedAnnouncement.user.role || "admin")}
                                  </span>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                        <section className="mt-6 w-full text-sm text-neutral-800 max-md:max-w-full">
                          <div className="flex flex-wrap gap-4 items-center w-full max-md:max-w-full">
                            <h3 className="self-stretch my-auto font-semibold leading-6 text-neutral-800">
                              Título:{" "}
                            </h3>
                            <p className="self-stretch my-auto leading-8 text-neutral-800">
                              {selectedAnnouncement.title}
                            </p>
                          </div>
                          <div className="mt-2 w-full max-md:max-w-full">
                            <h3 className="font-semibold leading-6 text-justify text-neutral-800">
                              Descrição:
                            </h3>
                            <div className="mt-2 leading-5 text-neutral-800 max-md:max-w-full">
                              {selectedAnnouncement.description ? (
                                selectedAnnouncement.description.split('\n').map((paragraph, index) => (
                                  <React.Fragment key={index}>
                                    {paragraph}
                                    {index < selectedAnnouncement.description!.split('\n').length - 1 && <br />}
                                  </React.Fragment>
                                ))
                              ) : (
                                "Descrição não disponível."
                              )}
                            </div>
                          </div>
                        </section>
                        {selectedAnnouncement.image && (
                          <img
                            src={selectedAnnouncement.image}
                            alt="Announcement illustration"
                            className="object-contain mt-6 w-full rounded aspect-[2.43] max-md:max-w-full"
                          />
                        )}
                      </div>
                    </header>
                    <footer className="flex flex-col justify-center py-8 pr-4 pl-8 w-full text-sm leading-none max-md:pl-5 max-md:max-w-full">
                      <div className="w-full max-w-[698px] max-md:max-w-full">
                        <div className="flex flex-wrap gap-10 items-start w-full max-md:max-w-full">
                          <div className="flex flex-col">
                            <div className="flex gap-2 items-center self-start">
                              <span className="self-stretch my-auto font-medium text-neutral-800">
                                Data publicada:
                              </span>
                              <span className="self-stretch my-auto text-neutral-500">
                                {selectedAnnouncement.date}
                              </span>
                            </div>
                            <div className="flex gap-2 items-center mt-4">
                              <span className="self-stretch my-auto font-medium text-neutral-800">
                                Número de acessos:
                              </span>
                              <span className="self-stretch my-auto text-neutral-500">
                                {selectedAnnouncement.views || 0} acessos
                              </span>
                            </div>
                          </div>
                          <div className="flex flex-col w-[198px]">
                            <div className="flex gap-2 items-center self-start">
                              <span className="self-stretch my-auto font-medium text-neutral-800">
                                Curtidas:
                              </span>
                              <span className="self-stretch my-auto text-neutral-500">
                                {selectedAnnouncement.likes || 0} curtidas
                              </span>
                            </div>
                            <div className="flex gap-2 items-center mt-4 w-full">
                              <span className="self-stretch my-auto font-medium text-neutral-800">
                                Comentários:
                              </span>
                              <span className="self-stretch my-auto text-neutral-500">
                                {selectedAnnouncement.comments || 0} comentários
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </footer>
                  </article>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Modals */}
      <ApproveCampaignModal
        isOpen={isApproveModalOpen}
        onClose={() => setIsApproveModalOpen(false)}
        onApprove={handleApproveCampaign}
        campaignTitle={selectedCampaign?.title || ""}
      />

      <RejectCampaignModal
        isOpen={isRejectModalOpen}
        onClose={() => setIsRejectModalOpen(false)}
        onReject={handleRejectCampaign}
        campaignTitle={selectedCampaign?.title || ""}
      />

      {/* Modais de denúncia */}
      <RejectComplaintModal
        isOpen={isDissolveModalOpen}
        onClose={() => setIsDissolveModalOpen(false)}
        onReject={(subject, reason) => {
          setIsDissolveModalOpen(false);
        }}
        complaintTitle={selectedReport?.title || ""}
      />

      <ApproveComplaintModal
        isOpen={isResolveModalOpen}
        onClose={() => setIsResolveModalOpen(false)}
        onApprove={(subject, message) => {
          setIsResolveModalOpen(false);
        }}
        complaintTitle={selectedReport?.title || ""}
      />
    </div>
  );
}
