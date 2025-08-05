"use client";

import { useState, useEffect, useRef } from "react";
import { ArrowLeft, Filter, SortDesc, Eye, Plus, X } from "lucide-react";
import Link from "next/link";
import { toast } from "react-toastify";
import Sidebar from "@/components/ui/sidebar";
import ApproveCampaignModal from "@/components/modals/community/ApproveCampaignModal";
import RejectCampaignModal from "@/components/modals/community/RejectCampaignModal";
import useCommunityById from "@/app/api/src/hooks/community/useCommunityById";
import useCommunityUserActions from "@/app/api/src/hooks/community/useCommunityUserActions";
import useCommunityPosts from "@/app/api/src/hooks/post/useCommunityPosts";
import { PostResponse } from "@/app/api/src/types/posts/Post";
import { translateUserRole } from "@/lib/roleTranslations";

type UserInfo = {
  id: string;
  name: string;
  profile_picture?: string | null;
  role?: string;
};

type Campaign = {
  id: number;
  title: string;
  leader: string;
  user: UserInfo;
  participants: number;
  date: string;
  status: "Em análise" | "Aprovado" | "Rejeitado";
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
};

export default function CommunityAdminPage({
  params,
}: {
  params: { id: string };
}) {
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
      setSingleUserEmail("");
      setEmailsToImport("");
      // O toast já é exibido no hook, mas podemos adicionar lógica extra aqui se necessário
    },
    onError: (error) => {
      console.error("Erro na ação do usuário:", error);
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
  // Estado para adicionar usuário individual
  const [singleUserEmail, setSingleUserEmail] = useState("");
  const [hasLoadedMembers, setHasLoadedMembers] = useState(false);
  const loadMembersRef = useRef(loadMembers);

  // Buscar dados da comunidade quando o componente monta ou o ID muda
  useEffect(() => {
    if (params.id) {
      console.log("ID da comunidade:", params.id); // Aqui você tem acesso ao ID
      fetchCommunity(params.id);
      fetchCommunityPosts(params.id);
    }
  }, [params.id, fetchCommunity, fetchCommunityPosts]); // Carregar membros quando a aba de usuários for ativa
  useEffect(() => {
    if (params.id && activeTab === "Usuários" && !hasLoadedMembers) {
      loadMembersRef.current(params.id);
      setHasLoadedMembers(true);
    }
  }, [params.id, activeTab, hasLoadedMembers]); // Sem dependência de loadMembers

  // Atualizar ref quando loadMembers mudar
  useEffect(() => {
    loadMembersRef.current = loadMembers;
  }, [loadMembers]);
  const tabs = ["Campanhas", "Denúncias", "Usuários", "Anúncios"];
  // Funções auxiliares para converter dados da API para o formato do componente
  const convertPostToCampaign = (post: PostResponse): Campaign => ({
    id: parseInt(post.id) || 0,
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
    status: post.status === "active" ? "Em análise" : "Aprovado",
    description: post.content,
    accesses: 0,
    likes: 0,
    comments: 0,
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
    views: 0,
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

    // Set the first item of the active tab as selected
    if (tab === "Campanhas" && campaigns.length > 0) {
      setSelectedCampaign(campaigns[0]);
    } else if (tab === "Denúncias" && reports.length > 0) {
      setSelectedReport(reports[0]);
    } else if (tab === "Anúncios" && announcements.length > 0) {
      setSelectedAnnouncement(announcements[0]);
    }
  };

  // Initialize default selected items if none are selected
  if (activeTab === "Campanhas" && !selectedCampaign && campaigns.length > 0) {
    setSelectedCampaign(campaigns[0]);
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
      communityId: params.id,
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
      communityId: params.id,
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
  // Handlers para gerenciamento de usuários
  const handleAddModerator = async () => {
    if (!newModeratorEmail.trim()) {
      toast.error("Por favor, digite um email válido");
      return;
    }

    if (!params.id) {
      toast.error("ID da comunidade não encontrado");
      return;
    }

    await addModeratorByEmail(params.id, newModeratorEmail, "moderator");
  };

  const handleRemoveUser = async () => {
    if (!excludeUserEmail.trim()) {
      toast.error("Por favor, digite um email válido");
      return;
    }

    if (!params.id) {
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
      await removeUserById(params.id, params.id, memberToRemove.user_id);
    }
  };

  const handleImportUsers = async () => {
    if (!emailsToImport.trim()) {
      toast.error("Por favor, digite os emails para importar");
      return;
    }

    if (!params.id) {
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
    await importUsers(params.id, emails);
    setEmailsToImport("");
  };

  const handleAddSingleUser = async () => {
    if (!singleUserEmail.trim()) {
      toast.error("Por favor, digite um email válido");
      return;
    }

    if (!params.id) {
      toast.error("ID da comunidade não encontrado");
      return;
    }

    // Validar formato de email básico
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(singleUserEmail.trim())) {
      toast.error("Por favor, digite um email válido");
      return;
    }

    await importUsers(params.id, [singleUserEmail.trim()]);
    setSingleUserEmail("");
  };

  return (
    <div className="min-h-screen bg-gray-100 text-[#161616]">
      <Sidebar variant="static" />
      <div className="ml-64 flex">
        {/* Left Navigation */}
        <div className="w-64 bg-white border-r border-[#e0e0e0] min-h-screen">
          {/* Header */}{" "}
          <div className="p-6 border-b border-[#e0e0e0]">
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
                className={`w-full px-6 py-3 text-left hover:bg-[#f8f8f8] ${
                  activeTab === tab
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
        {/* Middle Section - Content List (only for Campanhas, Denúncias, Anúncios) */}
        {activeTab !== "Usuários" && (
          <div className="w-80 bg-white border-r border-[#e0e0e0] min-h-screen">
            {/* Header with filters */}
            <div className="p-4 border-b border-[#e0e0e0] flex items-center gap-2">
              <button className="p-2 hover:bg-[#f4f4f4]">
                <Filter className="h-4 w-4 text-[#525252]" />
              </button>
              <button className="p-2 hover:bg-[#f4f4f4]">
                <SortDesc className="h-4 w-4 text-[#525252]" />
              </button>
              {activeTab === "Anúncios" && (
                <button className="ml-auto px-3 py-1.5 bg-[#161616] text-white text-sm hover:bg-[#262626] flex items-center gap-1">
                  Anunciar
                  <Plus className="h-4 w-4" />
                </button>
              )}
            </div>{" "}
            {/* Content List */}
            <div className="overflow-auto">
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
                    onClick={() => params.id && fetchCommunityPosts(params.id)}
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
                    className={`p-4 border-b border-[#e0e0e0] cursor-pointer hover:bg-[#f8f8f8] ${
                      selectedCampaign?.id === campaign.id ? "bg-[#f4f4f4]" : ""
                    }`}
                    onClick={() => setSelectedCampaign(campaign)}
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
                      <span
                        className={`text-xs px-2 py-1 ${
                          campaign.status === "Em análise"
                            ? "bg-[#fff8e1] text-[#b28600]"
                            : campaign.status === "Aprovado"
                            ? "bg-[#defbe6] text-[#0e6027]"
                            : "bg-[#fff1f1] text-[#da1e28]"
                        }`}
                      >
                        {campaign.status}
                      </span>
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
                    className={`p-4 border-b border-[#e0e0e0] cursor-pointer hover:bg-[#f8f8f8] ${
                      selectedReport?.id === report.id ? "bg-[#f4f4f4]" : ""
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
                      <span
                        className={`text-xs px-2 py-1 ${getSeverityColor(
                          report.severity
                        )}`}
                      >
                        {report.severity}
                      </span>
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
                    className={`p-4 border-b border-[#e0e0e0] cursor-pointer hover:bg-[#f8f8f8] ${
                      selectedAnnouncement?.id === announcement.id
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
                      <span className="text-xs text-[#525252]">0</span>
                      <Eye className="h-3 w-3 text-[#525252]" />
                    </div>
                  </div>
                ))}
            </div>
          </div>
        )}{" "}
        {/* Right Section - Details */}
        <div className="flex-1 bg-gray-100 p-6">
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
          {/* Campaign Details */}
          {activeTab === "Campanhas" && selectedCampaign && !postsLoading && (
            <div className="bg-white p-6">
              {/* Author info */}
              <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 rounded-full overflow-hidden">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={
                      selectedCampaign.user.profile_picture ||
                      "/no-profile-pic.png"
                    }
                    alt={selectedCampaign.user.name}
                    className="w-full h-full object-cover"
                  />
                </div>{" "}
                <div className="flex items-center gap-2">
                  <span className="font-medium">{selectedCampaign.leader}</span>
                  <div className="w-1 h-1 rounded-full bg-[#525252]"></div>
                  <span className="text-xs px-2 py-1 bg-[#393939] text-white">
                    {translateUserRole(selectedCampaign.user.role || "leader")}
                  </span>
                </div>
              </div>

              {/* Campaign content */}
              <div className="space-y-4 mb-8">
                <div>
                  <p className="text-sm text-[#525252] mb-1">Título:</p>
                  <h2 className="text-lg font-medium">
                    {selectedCampaign.title}
                  </h2>
                </div>{" "}
                <div>
                  <p className="text-sm text-[#525252] mb-1">Descrição:</p>
                  <p className="text-[#161616] whitespace-pre-line leading-relaxed">
                    {selectedCampaign.description}
                  </p>
                </div>
                {selectedCampaign.image && (
                  <div>
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={selectedCampaign.image || "/placeholder.svg"}
                      alt="Campaign"
                      className="w-full max-w-md"
                    />
                  </div>
                )}
              </div>

              {/* Stats */}
              <div className="grid grid-cols-2 gap-x-8 gap-y-4 mb-8">
                <div>
                  <p className="text-sm text-[#525252]">Data publicada:</p>
                  <p className="font-medium">{selectedCampaign.date}</p>
                </div>{" "}
                <div>
                  <p className="text-sm text-[#525252]">Curtidas:</p>
                  <p className="font-medium">0 curtidas</p>
                </div>
                <div>
                  <p className="text-sm text-[#525252]">Número de acessos:</p>
                  <p className="font-medium">0 acessos</p>
                </div>
                <div>
                  <p className="text-sm text-[#525252]">Comentários:</p>
                  <p className="font-medium">0 comentários</p>
                </div>
                <div>
                  <p className="text-sm text-[#525252]">Participantes:</p>
                  <p className="font-medium">
                    {selectedCampaign.participants} pessoas
                  </p>
                </div>
                <div>
                  <p className="text-sm text-[#525252]">Status:</p>
                  <span
                    className={`inline-block px-2 py-1 text-sm ${
                      selectedCampaign.status === "Em análise"
                        ? "bg-[#fff8e1] text-[#b28600]"
                        : selectedCampaign.status === "Aprovado"
                        ? "bg-[#defbe6] text-[#0e6027]"
                        : "bg-[#fff1f1] text-[#da1e28]"
                    }`}
                  >
                    {selectedCampaign.status}
                  </span>
                </div>
              </div>

              {/* Action buttons */}
              {selectedCampaign.status === "Em análise" && (
                <div className="flex gap-4">
                  <button
                    className="flex-1 py-3 px-4 border border-[#e0e0e0] hover:bg-[#f8f8f8] transition-colors"
                    onClick={() => setIsRejectModalOpen(true)}
                  >
                    Rejeitar
                  </button>
                  <button
                    className="flex-1 py-3 px-4 bg-[#161616] text-white hover:bg-[#262626] transition-colors"
                    onClick={() => setIsApproveModalOpen(true)}
                  >
                    Aprovar
                  </button>
                </div>
              )}
            </div>
          )}
          {/* Report Details */}
          {activeTab === "Denúncias" && selectedReport && (
            <div className="bg-white p-6">
              {/* Report header */}{" "}
              <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 rounded-full overflow-hidden">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={
                      selectedReport.user.profile_picture ||
                      "/no-profile-pic.png"
                    }
                    alt={selectedReport.user.name}
                    className="w-full h-full object-cover"
                  />
                </div>{" "}
                <div className="flex items-center gap-2">
                  <span className="font-medium">
                    {selectedReport.user.name}
                  </span>
                  <div className="w-1 h-1 rounded-full bg-[#525252]"></div>
                  <span className="text-xs px-2 py-1 bg-[#393939] text-white">
                    {selectedReport.user.role || "Membro"}
                  </span>
                </div>
              </div>
              {/* Report content */}
              <div className="space-y-4 mb-8">
                <div>
                  <p className="text-sm text-[#525252] mb-1">Nível:</p>
                  <span
                    className={`px-2 py-1 text-sm ${getSeverityColor(
                      selectedReport.severity
                    )}`}
                  >
                    {selectedReport.severity}
                  </span>
                </div>{" "}
                <div>
                  <p className="text-sm text-[#525252] mb-1">Título:</p>
                  <h2 className="text-lg font-medium">
                    {selectedReport.title}
                  </h2>
                </div>{" "}
                <div>
                  <p className="text-sm text-[#525252] mb-1">Descrição:</p>
                  <p className="text-[#161616] whitespace-pre-line leading-relaxed">
                    {selectedReport.description}
                  </p>
                </div>
                {selectedReport.image && (
                  <div>
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={selectedReport.image || "/placeholder.svg"}
                      alt="Report"
                      className="w-full max-w-md"
                    />
                  </div>
                )}
              </div>
              {/* Stats */}
              <div className="grid grid-cols-2 gap-x-8 gap-y-4 mb-8">
                <div>
                  <p className="text-sm text-[#525252]">Data publicada:</p>
                  <p className="font-medium">{selectedReport.date}</p>{" "}
                </div>{" "}
                <div>
                  <p className="text-sm text-[#525252]">Curtidas:</p>
                  <p className="font-medium">0 curtidas</p>
                </div>
                <div>
                  <p className="text-sm text-[#525252]">Número de acessos:</p>
                  <p className="font-medium">0 acessos</p>
                </div>
                <div>
                  <p className="text-sm text-[#525252]">Comentários:</p>
                  <p className="font-medium">0 comentários</p>
                </div>
                <div>
                  <p className="text-sm text-[#525252]">Confirmações:</p>
                  <p className="font-medium">
                    {selectedReport.confirmations} pessoas
                  </p>
                </div>
                <div>
                  <p className="text-sm text-[#525252]">Status:</p>
                  <span className="inline-flex items-center gap-1 px-2 py-1 text-sm bg-[#fff8e1] text-[#b28600]">
                    <div className="w-2 h-2 rounded-full bg-[#b28600]"></div>
                    Em apuração
                  </span>
                </div>
              </div>
              {/* Action buttons */}
              <div className="flex gap-4">
                <button className="flex-1 py-3 px-4 border border-[#e0e0e0] hover:bg-[#f8f8f8] transition-colors">
                  Dissolver
                </button>
                <button className="flex-1 py-3 px-4 bg-[#161616] text-white hover:bg-[#262626] transition-colors">
                  Resolver
                </button>
              </div>
            </div>
          )}{" "}
          {/* Users Management */}
          {activeTab === "Usuários" && (
            <div className="bg-white p-6">
              <div className="mb-6">
                <p className="text-sm text-[#525252] mb-2">Usuários</p>
                <h1 className="text-2xl font-medium">
                  Gerenciamento de Usuários
                </h1>
              </div>

              <div className="space-y-8">
                {" "}
                {/* Lista de membros */}
                {members.length > 0 && (
                  <div>
                    <h3 className="font-medium mb-4">Membros da Comunidade</h3>

                    {/* Estatísticas da comunidade - COMENTADO TEMPORARIAMENTE */}
                    {/* <div className="grid grid-cols-4 gap-4 mb-4 p-4 bg-gray-50 border border-[#e0e0e0] rounded">
                      <div className="text-center">
                        <p className="text-sm text-[#525252]">
                          Total de Membros
                        </p>
                        <p className="text-lg font-medium">{members.length}</p>
                      </div>
                      <div className="text-center">
                        <p className="text-sm text-[#525252]">Membros Ativos</p>
                        <p className="text-lg font-medium text-green-600">
                          {
                            members.filter(
                              (m) => m.status_participation === "active"
                            ).length
                          }
                        </p>
                      </div>
                      <div className="text-center">
                        <p className="text-sm text-[#525252]">
                          Administradores
                        </p>
                        <p className="text-lg font-medium text-blue-600">
                          {members.filter((m) => m.role === "admin").length}
                        </p>
                      </div>
                      <div className="text-center">
                        <p className="text-sm text-[#525252]">Moderadores</p>
                        <p className="text-lg font-medium text-purple-600">
                          {members.filter((m) => m.role === "moderator").length}
                        </p>
                      </div>
                    </div> */}

                    <div className="space-y-2 max-h-60 overflow-y-auto border border-[#e0e0e0] p-4">
                      {members.map((member) => (
                        <div
                          key={member.user_id}
                          className="flex items-center justify-between p-2 hover:bg-[#f8f8f8]"
                        >
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full overflow-hidden">
                              {/* eslint-disable-next-line @next/next/no-img-element */}
                              <img
                                src={
                                  member.user.profile_image_url ||
                                  "/no-profile-pic.png"
                                }
                                alt={member.user.name}
                                className="w-full h-full object-cover"
                              />
                            </div>
                            <div>
                              <p className="font-medium text-sm">
                                {member.user.name}
                              </p>
                              <p className="text-xs text-[#525252]">
                                {member.user.email}
                              </p>
                              <div className="flex items-center gap-2 mt-1">
                                <span
                                  className={`text-xs px-2 py-0.5 rounded-full ${
                                    member.status_participation === "active"
                                      ? "bg-green-100 text-green-800"
                                      : member.status_participation ===
                                        "suspended"
                                      ? "bg-yellow-100 text-yellow-800"
                                      : "bg-red-100 text-red-800"
                                  }`}
                                >
                                  {member.status_participation === "active"
                                    ? "Ativo"
                                    : member.status_participation ===
                                      "suspended"
                                    ? "Suspenso"
                                    : "Banido"}
                                </span>
                                <span className="text-xs text-[#525252]">
                                  Rep: {member.reputation}
                                </span>
                                <span className="text-xs text-[#525252]">
                                  Desde:{" "}
                                  {new Date(
                                    member.entered_in
                                  ).toLocaleDateString("pt-BR")}
                                </span>
                              </div>
                            </div>
                          </div>
                          {/* Seletores de função e botão de remover - COMENTADO TEMPORARIAMENTE */}
                          {/* <div className="flex items-center gap-2">
                            <select
                              value={member.role}
                              onChange={(e) => {
                                console.log("DEBUG: member object:", member);
                                // Corrigido: params.id (id da comunidade), params.id (communityId), member.user_id (memberId)
                                updateUserRole(
                                  params.id,
                                  params.id,
                                  member.user_id,
                                  e.target.value as "admin" | "moderator" | "member"
                                );
                              }}
                              disabled={isUserActionLoading}
                              className="text-xs px-2 py-1 border border-[#e0e0e0]"
                            >
                              <option value="member">Membro</option>
                              <option value="moderator">Moderador</option>
                              <option value="admin">Admin</option>
                            </select>
                            <button
                              onClick={() => {
                                console.log("DEBUG: member object:", member);
                                const confirm = window.confirm(
                                  `Remover ${member.user.name}?`
                                );
                                if (confirm)
                                  removeUserById(params.id, params.id, member.user_id);
                              }}
                              disabled={isUserActionLoading}
                              className="text-xs px-2 py-1 bg-red-500 text-white hover:bg-red-600"
                            >
                              Remover
                            </button>
                          </div> */}
                        </div>
                      ))}
                    </div>
                    {pagination && (
                      <p className="text-xs text-[#525252] mt-2">
                        {pagination.items.length} de {pagination.total} membros
                      </p>
                    )}
                  </div>
                )}
                {/* Add single user */}
                <div>
                  <h3 className="font-medium mb-2">Adicionar usuário</h3>
                  <p className="text-sm text-[#525252] mb-4">
                    Digite o email do usuário que deseja adicionar à comunidade.
                  </p>
                  <div className="flex gap-2 mb-2">
                    <input
                      type="email"
                      placeholder="Digite o email do usuário"
                      className="flex-1 px-3 py-2 border border-[#e0e0e0] focus:outline-none focus:border-[#0f62fe]"
                      value={singleUserEmail}
                      onChange={(e) => setSingleUserEmail(e.target.value)}
                    />
                    <button
                      className="px-4 py-2 bg-[#161616] text-white hover:bg-[#262626] transition-colors flex items-center gap-1 disabled:opacity-50 disabled:cursor-not-allowed"
                      onClick={handleAddSingleUser}
                      disabled={isUserActionLoading}
                    >
                      {isUserActionLoading ? "Adicionando..." : "Adicionar"}
                      <Plus className="h-4 w-4" />
                    </button>
                  </div>
                  <p className="text-sm text-[#525252]">
                    O usuário será adicionado com o papel de membro na
                    comunidade.
                  </p>
                </div>
                <hr className="border-[#e0e0e0]" />
                {/* Import users */}
                <div>
                  <h3 className="font-medium mb-2">
                    Importar base de dados de usuários
                  </h3>
                  <p className="text-sm text-[#525252] mb-4">
                    Digite os emails separados por vírgula ou quebra de linha.
                  </p>
                  <textarea
                    placeholder="email1@example.com, email2@example.com"
                    className="w-full px-3 py-2 border border-[#e0e0e0] mb-2 h-24"
                    value={emailsToImport}
                    onChange={(e) => setEmailsToImport(e.target.value)}
                  />
                  <button
                    className="px-4 py-2 bg-[#161616] text-white hover:bg-[#262626] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    onClick={handleImportUsers}
                    disabled={isUserActionLoading}
                  >
                    {isUserActionLoading
                      ? "Importando..."
                      : "Importar usuários"}
                  </button>
                </div>
                <hr className="border-[#e0e0e0]" />
                {/* Add moderator */}
                <div>
                  <h3 className="font-medium mb-2">Adicionar moderador</h3>
                  <div className="flex gap-2 mb-2">
                    <input
                      type="email"
                      placeholder="Digite o email do usuário"
                      className="flex-1 px-3 py-2 border border-[#e0e0e0] focus:outline-none focus:border-[#0f62fe]"
                      value={newModeratorEmail}
                      onChange={(e) => setNewModeratorEmail(e.target.value)}
                    />{" "}
                    <button
                      className="px-4 py-2 bg-[#161616] text-white hover:bg-[#262626] transition-colors flex items-center gap-1 disabled:opacity-50 disabled:cursor-not-allowed"
                      onClick={handleAddModerator}
                      disabled={isUserActionLoading}
                    >
                      {isUserActionLoading ? "Adicionando..." : "Adicionar"}
                      <Plus className="h-4 w-4" />
                    </button>
                  </div>
                  <p className="text-sm text-[#525252]">
                    Ao clicar em adicionar o usuário terá seu papel da
                    comunidade alterado para moderador.
                  </p>
                </div>
                <hr className="border-[#e0e0e0]" />
                {/* Exclude user */}
                <div>
                  <h3 className="font-medium mb-2">Excluir usuário</h3>
                  <div className="flex gap-2 mb-2">
                    <input
                      type="email"
                      placeholder="Digite o email do usuário"
                      className="flex-1 px-3 py-2 border border-[#e0e0e0] focus:outline-none focus:border-[#0f62fe]"
                      value={excludeUserEmail}
                      onChange={(e) => setExcludeUserEmail(e.target.value)}
                    />{" "}
                    <button
                      className="px-4 py-2 bg-[#da1e28] text-white hover:bg-[#bc1a22] transition-colors flex items-center gap-1 disabled:opacity-50 disabled:cursor-not-allowed"
                      onClick={handleRemoveUser}
                      disabled={isUserActionLoading}
                    >
                      {isUserActionLoading ? "Excluindo..." : "Excluir"}
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                  <p className="text-sm text-[#525252]">
                    A exclusão é permanente, então certifique-se de digitar o
                    e-mail corretamente.
                  </p>
                </div>
              </div>
            </div>
          )}
          {/* Announcement Details */}
          {activeTab === "Anúncios" && selectedAnnouncement && (
            <div className="bg-white p-6">
              {/* Author info */}
              <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 rounded-full overflow-hidden">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={
                      selectedAnnouncement.user.profile_picture ||
                      "/no-profile-pic.png"
                    }
                    alt={selectedAnnouncement.user.name}
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="flex items-center gap-2">
                  <span className="font-medium">
                    {selectedAnnouncement.author}
                  </span>
                  <div className="w-1 h-1 rounded-full bg-[#525252]"></div>
                  <span className="text-xs px-2 py-1 bg-black text-white">
                    {selectedAnnouncement.user.role}
                  </span>
                </div>
              </div>

              {/* Announcement content */}
              <div className="space-y-4 mb-8">
                {" "}
                <div>
                  <p className="text-sm text-[#525252] mb-1">Título:</p>
                  <h2 className="text-lg font-medium">
                    {selectedAnnouncement.title}
                  </h2>
                </div>
                <div>
                  <p className="text-sm text-[#525252] mb-1">Descrição:</p>
                  <p className="text-[#161616] whitespace-pre-line leading-relaxed mb-4">
                    {selectedAnnouncement.description}
                  </p>
                  <p className="text-[#161616] mb-4">Atenciosamente,</p>
                  <p className="text-[#161616]">
                    Equipe de Administração da Comunidade
                  </p>
                </div>
                {selectedAnnouncement.image && (
                  <div>
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={selectedAnnouncement.image || "/placeholder.svg"}
                      alt="Announcement"
                      className="w-full max-w-md"
                    />
                  </div>
                )}
              </div>

              {/* Stats */}
              <div className="grid grid-cols-2 gap-x-8 gap-y-4">
                <div>
                  <p className="text-sm text-[#525252]">Data publicada:</p>
                  <p className="font-medium">{selectedAnnouncement.date}</p>
                </div>{" "}
                <div>
                  <p className="text-sm text-[#525252]">Curtidas:</p>
                  <p className="font-medium">0 curtidas</p>
                </div>
                <div>
                  <p className="text-sm text-[#525252]">Número de acessos:</p>
                  <p className="font-medium">0 acessos</p>
                </div>
                <div>
                  <p className="text-sm text-[#525252]">Comentários:</p>
                  <p className="font-medium">0 comentários</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Modals */}
      <ApproveCampaignModal
        isOpen={isApproveModalOpen}
        onClose={() => setIsApproveModalOpen(false)}
        onApprove={handleApproveCampaign}
        campaignTitle={selectedCampaign?.title || ""}
        campaignAuthor={selectedCampaign?.leader || ""}
      />

      <RejectCampaignModal
        isOpen={isRejectModalOpen}
        onClose={() => setIsRejectModalOpen(false)}
        onReject={handleRejectCampaign}
        campaignTitle={selectedCampaign?.title || ""}
        campaignAuthor={selectedCampaign?.leader || ""}
      />
    </div>
  );
}
