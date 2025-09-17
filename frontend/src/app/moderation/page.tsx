
"use client";
import React, { useState, useEffect, useRef } from "react";
import { ArrowLeft, Filter, Eye, Heart, MessageSquare } from "lucide-react";
import Link from "next/link";
import { toast } from "react-toastify";
import Sidebar from "@/components/ui/sidebar";
import { CheckmarkFilled, Search } from "@carbon/icons-react";
import getCheckmarkColorClass from "@/components/badges/users/CheckmarkColorClasses";
import getRoleBadgeClasses from "@/components/badges/users/RoleBadgesClasses";
import ApproveCampaignModal from "@/components/modals/community/ApproveCampaignModal";
import RejectCampaignModal from "@/components/modals/community/RejectCampaignModal";
import { useCampaignAdminActions } from "@/app/api/src/hooks/post/useCampaignAdminActions";
import { useAuth } from "@/app/api/src/auth/useAuth";
import useCommunityById from "@/app/api/src/hooks/community/useCommunityById";
import useCommunityUserActions from "@/app/api/src/hooks/community/useCommunityUserActions";
import useCommunityPosts from "@/app/api/src/hooks/post/useCommunityPosts";
import useCampaignDetails from "@/app/api/src/hooks/post/useCampaignDetails";
import useModerationReports from "@/app/api/src/hooks/moderation/useModerationReports";
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
import ModalAnnouncement from "@/components/modals/posts/ModalAnnouncement";
import RejectComplaintModal from "@/components/modals/community/RejectComplaintModal";
import ApproveComplaintModal from "@/components/modals/community/ApproveComplaintModal";
import ImportUserModal from "@/components/modals/community/ImportUserModal";
import { ChevronSort, Email, FilterEdit } from "@carbon/icons-react";
import useCommunityActions from "@/app/api/src/hooks/community/useCommunityActions";
import { useRouter } from "next/navigation";

// Tipo para dropdown de comunidades
type CommunityOption = { id: string; name: string };

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
    id: string;
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

type UserReport = {
    id: string;
    reportedUser: UserInfo;
    reporter: UserInfo;
    reason: string;
    description: string;
    date: string;
    status: "Em análise" | "Resolvido" | "Arquivado";
    severity: "Crítica" | "Moderada" | "Leve";
    confirmations: number;
    category: string;
};

type PostReport = {
    id: string;
    reportedPost: {
        id: string;
        title: string;
        content: string;
        author: UserInfo;
        image?: string;
        likes: number;
        comments: number;
        date: string;
    };
    reporter: UserInfo;
    reason: string;
    description: string;
    date: string;
    status: "Em análise" | "Resolvido" | "Arquivado";
    severity: "Crítica" | "Moderada" | "Leve";
    confirmations: number;
    category: string;
};

type CommentReport = {
    id: string;
    reportedComment: {
        id: string;
        content: string;
        author: UserInfo;
        date: string;
        postTitle: string;
        likes: number;
    };
    reporter: UserInfo;
    reason: string;
    description: string;
    date: string;
    status: "Em análise" | "Resolvido" | "Arquivado";
    severity: "Crítica" | "Moderada" | "Leve";
    confirmations: number;
    category: string;
};

type Announcement = {
    id: string;
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

type Poll = {
    id: string;
    title: string;
    author: string;
    user: UserInfo;
    date: string;
    status: "Ativa" | "Encerrada" | "Rascunho";
    votes?: number;
    description?: string;
    options?: string[];
    likes?: number;
    comments?: number;
};

export default function ModerationPage() {
    // --- Dropdown de comunidades ---
    const { communities: userCommunities, loading: loadingCommunities } = useCommunityActions();
    const [communityDropdownOpen, setCommunityDropdownOpen] = useState(false);
    const [selectedCommunity, setSelectedCommunity] = useState<CommunityOption | null>(null);
    const router = useRouter();

    // Handler para selecionar comunidade
    const handleSelectCommunity = (community: CommunityOption) => {
        setSelectedCommunity(community);
        setCommunityDropdownOpen(false);
        // Não altera a URL, só troca o estado local
        fetchCommunity(community.id);
    };

    const { user } = useAuth();

    // Hook para buscar dados da comunidade específica
    const {
        community,
        loading: communityLoading,
        error: communityError,
        fetchCommunity,
    } = useCommunityById();

    // Hook para gerenciar usuários da comunidade
    const {
        isLoading: isUserActionLoading,
        members,
        pagination,
        loadMembers,
        addModeratorByEmail,
        removeUserById,
        importUsers,
    } = useCommunityUserActions({
        onSuccess: () => {
            setNewModeratorEmail("");
            setExcludeUserEmail("");
            setEmailsToImport("");
        },
        onError: (error) => {
            toast.error("Erro ao realizar ação: " + error.message);
        },
    });

    // Hook para buscar posts da comunidade (campanhas, denúncias, anúncios, enquetes)
    const {
        campaigns: apiCampaigns,
        reports: apiReports,
        announcements: apiAnnouncements,
        polls: apiPolls,
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

    // Hook para dados de moderação (reportes reais)
    const {
        reportedUsers,
        reportedPosts,
        reportedComments,
        loading: moderationLoading,
        error: moderationError,
        fetchReportedUsers,
        fetchReportedPosts,
        fetchReportedComments,
        suspendUser,
        removePost,
        removeComment,
        tolerateReport,
    } = useModerationReports();

    // Estados existentes
    const [activeTab, setActiveTab] = useState("Reportes");
    const [reportesActiveTab, setReportesActiveTab] = useState("usuarios"); // usuarios, publicacoes, comentarios
    const [selectedCampaign, setSelectedCampaign] = useState<Campaign | null>(null);
    const [selectedReport, setSelectedReport] = useState<Report | null>(null);
    const [selectedUserReport, setSelectedUserReport] = useState<UserReport | null>(null);
    const [selectedPostReport, setSelectedPostReport] = useState<PostReport | null>(null);
    const [selectedCommentReport, setSelectedCommentReport] = useState<CommentReport | null>(null);
    const [selectedAnnouncement, setSelectedAnnouncement] = useState<Announcement | null>(null);
    const [selectedPoll, setSelectedPoll] = useState<Poll | null>(null);
    const [isApproveModalOpen, setIsApproveModalOpen] = useState(false);
    const [isRejectModalOpen, setIsRejectModalOpen] = useState(false);
    const [isAnnouncementModalOpen, setIsAnnouncementModalOpen] = useState(false);
    const [newModeratorEmail, setNewModeratorEmail] = useState("");
    const [excludeUserEmail, setExcludeUserEmail] = useState("");
    const [emailsToImport, setEmailsToImport] = useState("");
    const [isImportUserModalOpen, setIsImportUserModalOpen] = useState(false);
    const [hasLoadedMembers, setHasLoadedMembers] = useState(false);
    const loadMembersRef = useRef(loadMembers);

    // Estados para a aba Comunidades
    const [dropdown1Value, setDropdown1Value] = useState('Opção 1');
    const [dropdown1Open, setDropdown1Open] = useState(false);
    const [dropdown2Value, setDropdown2Value] = useState('Opção 2');
    const [dropdown2Open, setDropdown2Open] = useState(false);
    const [toggleChecked, setToggleChecked] = useState(false);

    // Carregar a primeira comunidade automaticamente ao carregar o componente
    useEffect(() => {
        if (userCommunities.length > 0 && !selectedCommunity) {
            setSelectedCommunity(userCommunities[0]);
        }
    }, [userCommunities, selectedCommunity]);

    // Sempre que selectedCommunity mudar, buscar dados da comunidade, posts e membros
    useEffect(() => {
        if (selectedCommunity) {
            fetchCommunity(selectedCommunity.id);
            fetchCommunityPosts(selectedCommunity.id);
            // Buscar dados de moderação
            fetchReportedUsers(selectedCommunity.id);
            fetchReportedPosts(selectedCommunity.id);
            fetchReportedComments(selectedCommunity.id);
            // loadMembersRef.current(selectedCommunity.id);
        }
    }, [selectedCommunity?.id, fetchReportedUsers, fetchReportedPosts, fetchReportedComments]);

    // Atualizar a ref quando loadMembers mudar
    useEffect(() => {
        loadMembersRef.current = loadMembers;
    }, [loadMembers]);

    const tabs = ["Reportes", "Denúncias", "Enquetes", "Anúncios"];

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
        participants: 0,
        date: new Date(post.created_at).toLocaleDateString("pt-BR"),
        status: mapApiStatusToFrontendStatus(post.status),
        description: post.content,
        accesses: 0,
        likes: post.likes_count || 0,
        comments: post.comments_count || 0,
        image: post.image_url || undefined,
    });

    // Converter dados da API de moderação para os tipos do componente
    const convertApiUserToUserReport = (apiUser: any): UserReport => ({
        id: apiUser.id,
        reportedUser: {
            id: apiUser.id,
            name: apiUser.name,
            profile_picture: apiUser.profile_picture,
            role: apiUser.role || "member",
        },
        reporter: {
            id: "system",
            name: "Sistema",
            profile_picture: "/system-avatar.png",
            role: "admin",
        },
        reason: apiUser.suspension_reason || "Violação das diretrizes da comunidade",
        description: `Usuário reportado por comportamento inadequado. Status atual: ${apiUser.status}`,
        date: new Date(apiUser.created_at).toLocaleDateString("pt-BR"),
        status: apiUser.status === "suspended" ? "Resolvido" : "Em análise",
        severity: apiUser.report_count > 10 ? "Crítica" : apiUser.report_count > 5 ? "Moderada" : "Leve",
        confirmations: apiUser.report_count || 0,
        category: "Comportamento",
    });

    const convertApiPostToPostReport = (apiPost: any): PostReport => ({
        id: apiPost.id,
        reportedPost: {
            id: apiPost.id,
            title: apiPost.title,
            content: apiPost.content,
            author: {
                id: apiPost.user.id,
                name: apiPost.user.name,
                profile_picture: apiPost.user.profile_picture,
                role: apiPost.user.role || "member",
            },
            image: apiPost.image_url,
            likes: apiPost.likes_count || 0,
            comments: apiPost.comments_count || 0,
            date: new Date(apiPost.created_at).toLocaleDateString("pt-BR"),
        },
        reporter: {
            id: "community",
            name: "Comunidade",
            profile_picture: "/community-avatar.png",
            role: "member",
        },
        reason: "Conteúdo inapropriado",
        description: "Publicação foi reportada pela comunidade por violar as diretrizes de conteúdo.",
        date: new Date(apiPost.created_at).toLocaleDateString("pt-BR"),
        status: "Em análise",
        severity: apiPost.report_count > 15 ? "Crítica" : apiPost.report_count > 8 ? "Moderada" : "Leve",
        confirmations: apiPost.report_count || 0,
        category: "Conteúdo",
    });

    const convertApiCommentToCommentReport = (apiComment: any): CommentReport => ({
        id: apiComment.id,
        reportedComment: {
            id: apiComment.id,
            content: apiComment.content,
            author: {
                id: apiComment.user.id,
                name: apiComment.user.name,
                profile_picture: apiComment.user.profile_picture,
                role: apiComment.user.role || "member",
            },
            date: new Date(apiComment.created_at).toLocaleDateString("pt-BR"),
            postTitle: apiComment.post?.title || "Post não encontrado",
            likes: apiComment.likes_count || 0,
        },
        reporter: {
            id: "community",
            name: "Comunidade",
            profile_picture: "/community-avatar.png",
            role: "member",
        },
        reason: "Linguagem inadequada",
        description: "Comentário foi reportado pela comunidade por conter linguagem inadequada ou ofensiva.",
        date: new Date(apiComment.created_at).toLocaleDateString("pt-BR"),
        status: "Em análise",
        severity: apiComment.report_count > 5 ? "Crítica" : apiComment.report_count > 2 ? "Moderada" : "Leve",
        confirmations: apiComment.report_count || 0,
        category: "Comportamento",
    });

    const convertPostToReport = (post: PostResponse): Report => ({
        id: post.id,
        title: post.title,
        reporter: post.user.name,
        user: {
            id: post.user.id,
            name: post.user.name,
            profile_picture: post.user.profile_picture,
            role: post.user.role,
        },
        reported: "Usuário Denunciado",
        date: new Date(post.created_at).toLocaleDateString("pt-BR"),
        status: post.status === "active" ? "Em análise" : "Resolvido",
        description: post.content,
        category: "Comportamento",
        severity: "Moderada" as const,
        confirmations: post.report_count || 0,
        image: post.image_url || undefined,
        likes: post.likes_count || 0,
        comments: post.comments_count || 0,
        accesses: 0,
    });

    const convertPostToAnnouncement = (post: PostResponse): Announcement => ({
        id: post.id,
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
        likes: post.likes_count ?? 0,
        comments: post.comments_count ?? 0,
        description: post.content,
        image: post.image_url || undefined,
    });

    const convertPostToPoll = (post: PostResponse): Poll => ({
        id: post.id,
        title: post.title,
        author: post.user.name,
        user: {
            id: post.user.id,
            name: post.user.name,
            profile_picture: post.user.profile_picture,
            role: post.user.role,
        },
        date: new Date(post.created_at).toLocaleDateString("pt-BR"),
        status: post.status === "active" ? "Ativa" : "Encerrada",
        votes: post.likes_count || 0, // usando likes_count como proxy para votes por enquanto
        description: post.content,
        options: [], // TODO: adicionar opções da enquete quando disponível na API
        likes: post.likes_count ?? 0,
        comments: post.comments_count ?? 0,
    });


    // Dados reais da API convertidos para os formatos esperados
    const campaigns: Campaign[] = (apiCampaigns || []).map(convertPostToCampaign);
    const reports: Report[] = (apiReports || []).map(convertPostToReport);
    const announcements: Announcement[] = (apiAnnouncements || []).map(convertPostToAnnouncement);
    const polls: Poll[] = (apiPolls || []).map(convertPostToPoll);

    // Dados reais de moderação convertidos dos dados da API
    const userReports: UserReport[] = (reportedUsers || []).map(convertApiUserToUserReport);
    const postReports: PostReport[] = (reportedPosts || []).map(convertApiPostToPostReport);
    const commentReports: CommentReport[] = (reportedComments || []).map(convertApiCommentToCommentReport);

    // Set default selected items when changing tabs
    const handleTabChange = (tab: string) => {
        setActiveTab(tab);
        setSelectedCampaign(null);
        setSelectedReport(null);
        setSelectedUserReport(null);
        setSelectedPostReport(null);
        setSelectedCommentReport(null);
        setSelectedAnnouncement(null);
        setSelectedPoll(null);
        clearDetails();

        if (tab === "Reportes") {
            // Reset para primeira tab de reportes e selecionar primeiro item
            setReportesActiveTab("usuarios");
            if (userReports.length > 0) {
                setSelectedUserReport(userReports[0]);
            }
        } else if (tab === "Denúncias" && reports.length > 0) {
            setSelectedReport(reports[0]);
        } else if (tab === "Enquetes" && polls.length > 0) {
            setSelectedPoll(polls[0]);
        } else if (tab === "Anúncios" && announcements.length > 0) {
            setSelectedAnnouncement(announcements[0]);
        }
    };

    // Função para mudar tabs dentro dos reportes
    const handleReportesTabChange = (reportTab: string) => {
        setReportesActiveTab(reportTab);
        // Limpar seleções anteriores
        setSelectedUserReport(null);
        setSelectedPostReport(null);
        setSelectedCommentReport(null);

        // Selecionar primeiro item da nova tab
        if (reportTab === "usuarios" && userReports.length > 0) {
            setSelectedUserReport(userReports[0]);
        } else if (reportTab === "publicacoes" && postReports.length > 0) {
            setSelectedPostReport(postReports[0]);
        } else if (reportTab === "comentarios" && commentReports.length > 0) {
            setSelectedCommentReport(commentReports[0]);
        }
    };

    const handleCampaignSelection = async (campaign: Campaign) => {
        setSelectedCampaign(campaign);
    };

    // Hook para aprovar/rejeitar campanha
    const { approveCampaign, rejectCampaign, loading: adminActionLoading } = useCampaignAdminActions();

    // Handler para aprovação real
    const handleApproveCampaign = async (subject: string, message: string) => {
        if (!selectedCampaign) return;
        try {
            // Implementar lógica de aprovação para moderação
            setSelectedCampaign({ ...selectedCampaign, status: "Aprovado" });
            toast.success("Campanha aprovada com sucesso!");
        } catch (error: any) {
            toast.error(error?.message || "Erro ao aprovar campanha");
        } finally {
            setIsApproveModalOpen(false);
        }
    };

    // Handler para rejeição real
    const handleRejectCampaign = async (subject: string, reason: string) => {
        if (!selectedCampaign) return;
        try {
            // Implementar lógica de rejeição para moderação
            setSelectedCampaign({ ...selectedCampaign, status: "Rejeitado" });
            toast.success("Campanha rejeitada com sucesso!");
        } catch (error: any) {
            toast.error(error?.message || "Erro ao rejeitar campanha");
        } finally {
            setIsRejectModalOpen(false);
        }
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
        // Implementar lógica de adicionar moderador
        toast.success("Moderador adicionado com sucesso!");
    };

    const handleRemoveUser = async () => {
        if (!excludeUserEmail.trim()) {
            toast.error("Por favor, digite um email válido");
            return;
        }
        // Implementar lógica de remover usuário
        toast.success("Usuário removido com sucesso!");
    };

    const handleImportUsers = async () => {
        if (!emailsToImport.trim()) {
            toast.error("Por favor, digite o email para importar");
            return;
        }
        // Implementar lógica de importar usuários
        toast.success("Usuário importado com sucesso!");
        setEmailsToImport("");
        setIsImportUserModalOpen(false);
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

    // Handlers reais para ações de moderação
    const handleActuallyTolerate = async (subject: string, reason: string) => {
        if (!selectedCommunity) return;

        try {
            let type: 'user' | 'post' | 'comment' = 'user';
            let id = '';

            if (selectedUserReport) {
                type = 'user';
                id = selectedUserReport.reportedUser.id;
            } else if (selectedPostReport) {
                type = 'post';
                id = selectedPostReport.reportedPost.id;
            } else if (selectedCommentReport) {
                type = 'comment';
                id = selectedCommentReport.reportedComment.id;
            }

            await tolerateReport(selectedCommunity.id, type, id);
            toast.success("Reporte tolerado com sucesso!");

            // Limpar seleções
            setSelectedUserReport(null);
            setSelectedPostReport(null);
            setSelectedCommentReport(null);
        } catch (error: any) {
            toast.error(error.message || "Erro ao tolerar reporte");
        } finally {
            setIsDissolveModalOpen(false);
        }
    };

    const handleActuallyResolve = async (subject: string, message: string) => {
        if (!selectedCommunity) return;

        try {
            if (selectedUserReport) {
                await suspendUser(selectedCommunity.id, selectedUserReport.reportedUser.id);
                toast.success("Usuário suspenso com sucesso!");
            } else if (selectedPostReport) {
                await removePost(selectedCommunity.id, selectedPostReport.reportedPost.id);
                toast.success("Publicação removida com sucesso!");
            } else if (selectedCommentReport) {
                await removeComment(selectedCommunity.id, selectedCommentReport.reportedComment.id);
                toast.success("Comentário removido com sucesso!");
            }

            // Limpar seleções
            setSelectedUserReport(null);
            setSelectedPostReport(null);
            setSelectedCommentReport(null);
        } catch (error: any) {
            toast.error(error.message || "Erro ao resolver reporte");
        } finally {
            setIsResolveModalOpen(false);
        }
    };

    // Componentes inline para a aba Comunidades
    const SectionHeader = ({ title }: { title: string }) => (
        <header className="w-full text-xl leading-none text-black max-md:max-w-full">
            <h2 className="max-md:max-w-full">{title}</h2>
            <div className="flex mt-4 w-full bg-stone-300 min-h-px max-md:max-w-full" />
        </header>
    );

    const ConfigurationItem = ({
        description,
        value,
        children
    }: {
        description: string;
        value?: string;
        children?: React.ReactNode;
    }) => (
        <div className="flex flex-wrap gap-10 justify-between items-center mt-2 w-full max-md:max-w-full">
            <div className="self-stretch my-auto text-xs leading-none text-justify text-neutral-500 max-md:max-w-full">
                {description}
            </div>
            {value && (
                <div className="self-stretch my-auto text-sm leading-none text-center text-neutral-800 w-[60px]">
                    {value}
                </div>
            )}
            {children}
        </div>
    );

    const DropdownSelect = ({
        options,
        value,
        onChange,
        isOpen,
        onToggle,
        variant = 'primary'
    }: {
        options: string[];
        value: string;
        onChange: (value: string) => void;
        isOpen: boolean;
        onToggle: () => void;
        variant?: 'primary' | 'secondary';
    }) => {
        const textColorClass = variant === 'primary' ? 'text-neutral-800' : 'text-neutral-500';

        return (
            <div className="relative">
                <button
                    className={`flex gap-2.5 justify-center items-center self-stretch p-2.5 my-auto text-sm leading-none text-justify ${textColorClass}`}
                    onClick={onToggle}
                    aria-expanded={isOpen}
                    aria-haspopup="listbox"
                >
                    <span className="self-stretch my-auto">{value}</span>
                </button>

                {isOpen && (
                    <div className="absolute top-full left-0 mt-1 bg-white border border-gray-200 rounded shadow-lg z-10 min-w-full">
                        <ul role="listbox" className="py-1">
                            {options.map((option, index) => (
                                <li key={index}>
                                    <button
                                        className={`w-full px-3 py-2 text-left text-sm hover:bg-gray-100 ${textColorClass}`}
                                        onClick={() => {
                                            onChange(option);
                                            onToggle();
                                        }}
                                        role="option"
                                        aria-selected={value === option}
                                    >
                                        {option}
                                    </button>
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>
        );
    };

    const ToggleSwitch = ({
        checked,
        onChange
    }: {
        checked: boolean;
        onChange: (checked: boolean) => void;
    }) => (
        <button
            className="flex gap-2.5 items-center self-stretch px-1.5 py-1 my-auto w-12 rounded-2xl border border-solid bg-neutral-800 border-zinc-900"
            onClick={() => onChange(!checked)}
            role="switch"
            aria-checked={checked}
            aria-label="Toggle switch"
        >
            <div
                className={`flex self-stretch my-auto w-4 h-4 rounded-full min-h-4 transition-all duration-200 ${checked ? 'bg-white ml-auto' : 'bg-gray-200'
                    }`}
            />
        </button>
    );

    return (
        <div className="min-h-screen bg-gray-100 text-[#161616]">
            <Sidebar variant="static" />
            <div className="flex">
                {/* Left Navigation - Fixed */}
                <div className="fixed left-64 top-1 w-64 bg-white border-r border-[#e0e0e0] h-screen z-20 overflow-y-auto">
                    {/* Header */}
                    <div className="sticky top-0 p-6 border-[#e0e0e0] bg-white">
                        <div className="flex items-center gap-3 mb-4">
                            <Link href="/administration" className="p-1 hover:bg-[#e5e5e5]">
                                <ArrowLeft className="h-5 w-5 text-[#525252]" />
                            </Link>
                            <div className="flex items-center gap-2 relative">
                                <h1 className="text-lg font-medium">
                                    {selectedCommunity?.name || community?.name || "Comunidade"}
                                </h1>
                                <button
                                    className="ml-2 p-1 rounded hover:bg-[#f4f4f4] flex items-center"
                                    onClick={() => setCommunityDropdownOpen((open) => !open)}
                                    aria-haspopup="listbox"
                                    aria-expanded={communityDropdownOpen}
                                >
                                    <svg width="18" height="18" fill="none" viewBox="0 0 24 24"><path d="M7 10l5 5 5-5" stroke="#525252" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>
                                </button>
                                {communityDropdownOpen && (
                                    <div className="absolute left-0 top-full mt-2 bg-white border border-gray-200 rounded shadow-lg z-30 min-w-[180px]">
                                        <ul role="listbox">
                                            {userCommunities.map((c) => (
                                                <li key={c.id}>
                                                    <button
                                                        className="w-full px-3 py-2 text-left text-sm hover:bg-gray-100 text-gray-800"
                                                        onClick={() => handleSelectCommunity(c)}
                                                        role="option"
                                                        aria-selected={selectedCommunity?.id === c.id}
                                                    >
                                                        {c.name}
                                                    </button>
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
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
                    {/* Middle Section - Content List */}
                    <div className="w-80 fixed top-0 bottom-0 left-[512px] bg-white border-r border-[#e0e0e0] overflow-y-auto z-10 no-scrollbar">
                        {/* Header with filters */}
                        <div className="sticky top-0 p-4 border-[#e0e0e0] flex items-center gap-2 bg-white z-20">
                            <button className="p-2 hover:bg-[#f4f4f4]">
                                <FilterEdit className="h-4 w-4 text-[#525252]" />
                            </button>
                            <button className="p-2 hover:bg-[#f4f4f4]">
                                <ChevronSort className="h-4 w-4 text-[#525252]" />
                            </button>
                            {activeTab === "Anúncios" && (
                                <button
                                    className="ml-auto cursor-pointer px-3 min-w-[138px] min-h-[56px] py-1.5 bg-[#161616] text-white text-sm hover:bg-[#262626] flex items-center gap-10"
                                    onClick={() => setIsAnnouncementModalOpen(true)}
                                >
                                    Anunciar
                                    <Email className="h-4 w-4" />
                                </button>
                            )}
                        </div>

                        {/* Content List */}
                        <div className="h-full overflow-y-auto pb-20 no-scrollbar">

                            {/* Quando estiver em Reportes, mostrar apenas as abas internas (Usuários, Publicações, Comentários) */}
                            {activeTab === "Reportes" && (
                                <div className="space-y-0 mt-10">
                                    <button
                                        className={`w-full px-6 py-4 text-left border-[#e0e0e0] hover:bg-[#f8f8f8] cursor-pointer ${reportesActiveTab === "usuarios"
                                            ? "bg-[#f4f4f4] text-[#161616] font-medium"
                                            : "text-[#525252]"
                                            }`}
                                        onClick={() => handleReportesTabChange("usuarios")}
                                    >
                                        Usuários
                                    </button>
                                    <button
                                        className={`w-full px-6 py-4 text-left border-[#e0e0e0] hover:bg-[#f8f8f8] cursor-pointer ${reportesActiveTab === "publicacoes"
                                            ? "bg-[#f4f4f4] text-[#161616] font-medium"
                                            : "text-[#525252]"
                                            }`}
                                        onClick={() => handleReportesTabChange("publicacoes")}
                                    >
                                        Publicações
                                    </button>
                                    <button
                                        className={`w-full px-6 py-4 text-left border-[#e0e0e0] hover:bg-[#f8f8f8] cursor-pointer ${reportesActiveTab === "comentarios"
                                            ? "bg-[#f4f4f4] text-[#161616] font-medium"
                                            : "text-[#525252]"
                                            }`}
                                        onClick={() => handleReportesTabChange("comentarios")}
                                    >
                                        Comentários
                                    </button>
                                </div>
                            )}

                            {/* Exibir listas apenas nas abas Denúncias, Enquetes e Anúncios */}
                            {activeTab === "Denúncias" &&
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
                                            {getSeverityBadge(report.severity)}
                                            <div className="flex items-center gap-1">
                                                <span className="text-xs text-[#525252]">{report.accesses || 0}</span>
                                                <Eye className="h-3 w-3 text-[#525252]" />
                                            </div>
                                        </div>
                                    </div>
                                ))}

                            {/* Polls List */}
                            {activeTab === "Enquetes" &&
                                polls.map((poll) => (
                                    <div
                                        key={poll.id}
                                        className={`p-4 border-b border-[#e0e0e0] cursor-pointer hover:bg-[#f8f8f8] ${selectedPoll?.id === poll.id
                                            ? "bg-[#f4f4f4]"
                                            : ""
                                            }`}
                                        onClick={() => setSelectedPoll(poll)}
                                    >
                                        <div className="mb-2">
                                            <h3 className="font-medium text-sm mb-1">
                                                {poll.title}
                                            </h3>
                                            <p className="text-xs text-[#525252] mb-1">
                                                Autor: {poll.author}
                                            </p>
                                            <p className="text-xs text-[#525252] mb-2">
                                                {poll.votes} votos
                                            </p>
                                            <p className="text-xs text-[#525252] mb-2">
                                                {poll.date}
                                            </p>
                                        </div>
                                        <div className="flex items-center justify-between">
                                            <span className={`px-2 py-1 rounded text-xs ${poll.status === "Ativa"
                                                ? "bg-green-100 text-green-800"
                                                : poll.status === "Encerrada"
                                                    ? "bg-gray-100 text-gray-800"
                                                    : "bg-yellow-100 text-yellow-800"
                                                }`}>
                                                {poll.status}
                                            </span>
                                            <div className="flex items-center gap-1">
                                                <span className="text-xs text-[#525252]">{poll.votes || 0}</span>
                                                <Eye className="h-3 w-3 text-[#525252]" />
                                            </div>
                                        </div>
                                    </div>
                                ))}

                            {/* Announcements List */}
                            {activeTab === "Anúncios" &&
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
                                            <h3 className="font-medium text-sm mb-1">
                                                {announcement.title}
                                            </h3>
                                            <p className="text-xs text-[#525252] mb-1">
                                                Autor: {announcement.author}
                                            </p>
                                            <p className="text-xs text-[#525252] mb-2">
                                                {announcement.views} visualizações
                                            </p>
                                            <p className="text-xs text-[#525252] mb-2">
                                                {announcement.date}
                                            </p>
                                        </div>
                                        <div className="flex items-center justify-between">
                                            <span className={`px-2 py-1 rounded text-xs ${announcement.status === "Publicado"
                                                ? "bg-green-100 text-green-800"
                                                : "bg-gray-100 text-gray-800"
                                                }`}>
                                                {announcement.status}
                                            </span>
                                            <div className="flex items-center gap-1">
                                                <span className="text-xs text-[#525252]">{announcement.views || 0}</span>
                                                <Eye className="h-3 w-3 text-[#525252]" />
                                            </div>
                                        </div>
                                    </div>
                                ))}

                            {/* Reports List */}
                            {activeTab === "Denúncias" &&
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
                                            {getSeverityBadge(report.severity)}
                                            <div className="flex items-center gap-1">
                                                <span className="text-xs text-[#525252]">{report.accesses || 0}</span>
                                                <Eye className="h-3 w-3 text-[#525252]" />
                                            </div>
                                        </div>
                                    </div>
                                ))}

                            {/* Polls List */}
                            {activeTab === "Enquetes" &&
                                polls.map((poll) => (
                                    <div
                                        key={poll.id}
                                        className={`p-4 border-b border-[#e0e0e0] cursor-pointer hover:bg-[#f8f8f8] ${selectedPoll?.id === poll.id
                                            ? "bg-[#f4f4f4]"
                                            : ""
                                            }`}
                                        onClick={() => setSelectedPoll(poll)}
                                    >
                                        <div className="mb-2">
                                            <h3 className="font-medium text-sm mb-1">
                                                {poll.title}
                                            </h3>
                                            <p className="text-xs text-[#525252] mb-1">
                                                Autor: {poll.author}
                                            </p>
                                            <p className="text-xs text-[#525252] mb-2">
                                                {poll.votes} votos
                                            </p>
                                            <p className="text-xs text-[#525252] mb-2">
                                                {poll.date}
                                            </p>
                                        </div>
                                        <div className="flex items-center justify-between">
                                            <span className={`px-2 py-1 rounded text-xs ${poll.status === "Ativa"
                                                ? "bg-green-100 text-green-800"
                                                : poll.status === "Encerrada"
                                                    ? "bg-gray-100 text-gray-800"
                                                    : "bg-yellow-100 text-yellow-800"
                                                }`}>
                                                {poll.status}
                                            </span>
                                            <div className="flex items-center gap-1">
                                                <span className="text-xs text-[#525252]">{poll.votes || 0}</span>
                                                <Eye className="h-3 w-3 text-[#525252]" />
                                            </div>
                                        </div>
                                    </div>
                                ))}

                            {/* Announcements List */}
                            {activeTab === "Anúncios" &&
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
                                            <h3 className="font-medium text-sm mb-1">
                                                {announcement.title}
                                            </h3>
                                            <p className="text-xs text-[#525252] mb-1">
                                                Autor: {announcement.author}
                                            </p>
                                            <p className="text-xs text-[#525252] mb-2">
                                                {announcement.views} visualizações
                                            </p>
                                            <p className="text-xs text-[#525252] mb-2">
                                                {announcement.date}
                                            </p>
                                        </div>
                                        <div className="flex items-center justify-between">
                                            <span className={`px-2 py-1 rounded text-xs ${announcement.status === "Publicado"
                                                ? "bg-green-100 text-green-800"
                                                : "bg-gray-100 text-gray-800"
                                                }`}>
                                                {announcement.status}
                                            </span>
                                            <div className="flex items-center gap-1">
                                                <span className="text-xs text-[#525252]">{announcement.views || 0}</span>
                                                <Eye className="h-3 w-3 text-[#525252]" />
                                            </div>
                                        </div>
                                    </div>
                                ))}
                        </div>
                    </div>

                    {/* Right Section - Details Panel */}
                    <div className="ml-80">
                        {/* Lista de Denúncias */}
                        {activeTab === "Denúncias" && !selectedReport && (
                            <div className="max-w-full">
                                <div className="px-4 pt-4 pb-80 w-full bg-zinc-100 max-md:pb-24 max-md:max-w-full">
                                    <div className="space-y-4">
                                        {reports.map((report) => (
                                            <article key={report.id} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                                                <div className="p-6">
                                                    <div className="flex items-start gap-4 mb-4">
                                                        <div className="w-12 h-12 rounded-full bg-gray-200 flex-shrink-0 overflow-hidden">
                                                            {report.user.profile_picture && (
                                                                <img
                                                                    src={report.user.profile_picture}
                                                                    alt={report.user.name}
                                                                    className="w-full h-full object-cover"
                                                                />
                                                            )}
                                                        </div>
                                                        <div className="flex-1">
                                                            <div className="flex items-center gap-2 mb-1">
                                                                <h3 className="font-semibold text-lg text-gray-900">
                                                                    {report.title}
                                                                </h3>
                                                                {getSeverityBadge(report.severity)}
                                                            </div>
                                                            <p className="text-sm text-gray-600 mb-2">
                                                                Denunciante: {report.reporter}
                                                            </p>
                                                            <p className="text-sm text-gray-500">
                                                                {report.confirmations} confirmações • {report.date}
                                                            </p>
                                                        </div>
                                                    </div>
                                                    <p className="text-gray-700 mb-4">
                                                        {report.description}
                                                    </p>
                                                    <div className="flex gap-2">
                                                        <button
                                                            onClick={() => setSelectedReport(report)}
                                                            className="px-4 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
                                                        >
                                                            Ver detalhes
                                                        </button>
                                                    </div>
                                                </div>
                                            </article>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Lista de Enquetes */}
                        {activeTab === "Enquetes" && !selectedPoll && (
                            <div className="max-w-full">
                                <div className="px-4 pt-4 pb-80 w-full bg-zinc-100 max-md:pb-24 max-md:max-w-full">
                                    <div className="space-y-4">
                                        {polls.map((poll) => (
                                            <article key={poll.id} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                                                <div className="p-6">
                                                    <div className="flex items-start gap-4 mb-4">
                                                        <div className="w-12 h-12 rounded-full bg-gray-200 flex-shrink-0 overflow-hidden">
                                                            {poll.user.profile_picture && (
                                                                <img
                                                                    src={poll.user.profile_picture}
                                                                    alt={poll.user.name}
                                                                    className="w-full h-full object-cover"
                                                                />
                                                            )}
                                                        </div>
                                                        <div className="flex-1">
                                                            <div className="flex items-center gap-2 mb-1">
                                                                <h3 className="font-semibold text-lg text-gray-900">
                                                                    {poll.title}
                                                                </h3>
                                                                <span className={`text-xs px-2 py-1 rounded ${poll.status === "Ativa"
                                                                    ? "bg-green-100 text-green-600"
                                                                    : "bg-gray-100 text-gray-600"}`}>
                                                                    {poll.status}
                                                                </span>
                                                            </div>
                                                            <p className="text-sm text-gray-600 mb-2">
                                                                Autor: {poll.author}
                                                            </p>
                                                            <p className="text-sm text-gray-500">
                                                                {poll.votes} votos • {poll.date}
                                                            </p>
                                                        </div>
                                                    </div>
                                                    <p className="text-gray-700 mb-4">
                                                        {poll.description}
                                                    </p>
                                                    <div className="flex gap-2">
                                                        <button
                                                            onClick={() => setSelectedPoll(poll)}
                                                            className="px-4 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
                                                        >
                                                            Ver detalhes
                                                        </button>
                                                    </div>
                                                </div>
                                            </article>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Lista de Anúncios */}
                        {activeTab === "Anúncios" && !selectedAnnouncement && (
                            <div className="max-w-full">
                                <div className="px-4 pt-4 pb-80 w-full bg-zinc-100 max-md:pb-24 max-md:max-w-full">
                                    <div className="space-y-4">
                                        {announcements.map((announcement) => (
                                            <article key={announcement.id} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                                                <div className="p-6">
                                                    <div className="flex items-start gap-4 mb-4">
                                                        <div className="w-12 h-12 rounded-full bg-gray-200 flex-shrink-0 overflow-hidden">
                                                            {announcement.user.profile_picture && (
                                                                <img
                                                                    src={announcement.user.profile_picture}
                                                                    alt={announcement.user.name}
                                                                    className="w-full h-full object-cover"
                                                                />
                                                            )}
                                                        </div>
                                                        <div className="flex-1">
                                                            <div className="flex items-center gap-2 mb-1">
                                                                <h3 className="font-semibold text-lg text-gray-900">
                                                                    {announcement.title}
                                                                </h3>
                                                                <span className={`text-xs px-2 py-1 rounded ${announcement.status === "Publicado"
                                                                    ? "bg-green-100 text-green-600"
                                                                    : "bg-gray-100 text-gray-600"}`}>
                                                                    {announcement.status}
                                                                </span>
                                                            </div>
                                                            <p className="text-sm text-gray-600 mb-2">
                                                                Autor: {announcement.author}
                                                            </p>
                                                            <p className="text-sm text-gray-500">
                                                                {announcement.views} visualizações • {announcement.date}
                                                            </p>
                                                        </div>
                                                    </div>
                                                    <p className="text-gray-700 mb-4">
                                                        {announcement.description}
                                                    </p>
                                                    <div className="flex gap-2">
                                                        <button
                                                            onClick={() => setSelectedAnnouncement(announcement)}
                                                            className="px-4 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
                                                        >
                                                            Ver detalhes
                                                        </button>
                                                    </div>
                                                </div>
                                            </article>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        )}
                        {/* Report Details - Usuários */}
                        {activeTab === "Reportes" && reportesActiveTab === "usuarios" && selectedUserReport && (
                            <div className="max-w-full">
                                <div className="px-4 pt-4 pb-80 w-full bg-zinc-100 max-md:pb-24 max-md:max-w-full">
                                    <article className="mb-0 bg-white max-md:mb-2.5 max-md:max-w-full">
                                        <header className="flex flex-col justify-center p-8 w-full bg-white rounded max-md:px-5 max-md:max-w-full">
                                            <div className="w-full max-md:max-w-full">
                                                <div className="flex justify-between items-start w-full max-md:max-w-full">
                                                    <div className="flex items-center min-w-60">
                                                        <img
                                                            src={selectedUserReport.reportedUser.profile_picture || "/no-profile-pic.png"}
                                                            alt={`${selectedUserReport.reportedUser.name} profile picture`}
                                                            className="object-contain shrink-0 self-stretch my-auto w-11 aspect-square"
                                                        />
                                                        <div className="self-stretch my-auto min-w-60 w-[342px]">
                                                            <div className="flex gap-2 items-center w-full h-[23px]">
                                                                <div className="flex overflow-hidden gap-2.5 justify-center items-center self-stretch px-3 my-auto">
                                                                    <span className="self-stretch my-auto text-sm text-neutral-800">
                                                                        {selectedUserReport.reportedUser.name}
                                                                    </span>
                                                                    <CheckmarkFilled
                                                                        className={`object-contain shrink-0 self-stretch my-auto aspect-square w-[18px] ${getCheckmarkColorClass(selectedUserReport.reportedUser.role)}`}
                                                                        aria-label="Verificado"
                                                                    />
                                                                    <span className={`flex gap-2.5 justify-center items-center self-stretch px-3 py-1 my-auto text-xs whitespace-nowrap rounded ${getRoleBadgeClasses(selectedUserReport.reportedUser.role)}`}>
                                                                        {translateUserRole(selectedUserReport.reportedUser.role || "member")}
                                                                    </span>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                    <div className="flex flex-col items-end gap-2">
                                                        {getSeverityBadge(selectedUserReport.severity)}
                                                        <span className="text-xs text-[#525252]">
                                                            {selectedUserReport.confirmations} reportes
                                                        </span>
                                                    </div>
                                                </div>
                                                <div className="mt-6 w-full text-sm text-neutral-800 max-md:max-w-full">
                                                    <div className="flex flex-wrap gap-4 items-center w-full leading-6 max-md:max-w-full">
                                                        <span className="self-stretch my-auto font-semibold text-neutral-800">
                                                            Motivo do reporte:
                                                        </span>
                                                        <span className="self-stretch my-auto text-neutral-800">
                                                            {selectedUserReport.reason}
                                                        </span>
                                                    </div>
                                                    <div className="mt-4 flex flex-wrap gap-4 items-center w-full leading-6 max-md:max-w-full">
                                                        <span className="self-stretch my-auto font-semibold text-neutral-800">
                                                            Reportado por:
                                                        </span>
                                                        <div className="flex items-center gap-2">
                                                            <img
                                                                src={selectedUserReport.reporter.profile_picture || "/no-profile-pic.png"}
                                                                alt={selectedUserReport.reporter.name}
                                                                className="w-6 h-6 rounded-full object-cover"
                                                            />
                                                            <span className="self-stretch my-auto text-neutral-800">
                                                                {selectedUserReport.reporter.name}
                                                            </span>
                                                        </div>
                                                    </div>
                                                    <div className="mt-4 w-full max-md:max-w-full">
                                                        <h3 className="font-semibold leading-6 text-justify text-neutral-800">
                                                            Descrição do reporte:
                                                        </h3>
                                                        <p className="mt-2 leading-5 text-neutral-800 max-md:max-w-full">
                                                            {selectedUserReport.description}
                                                        </p>
                                                    </div>
                                                    <div className="mt-4 flex gap-4 items-center">
                                                        <span className="font-semibold text-neutral-800">Data:</span>
                                                        <span className="text-neutral-800">{selectedUserReport.date}</span>
                                                    </div>
                                                    <div className="mt-2 flex gap-4 items-center">
                                                        <span className="font-semibold text-neutral-800">Categoria:</span>
                                                        <span className="text-neutral-800">{selectedUserReport.category}</span>
                                                    </div>
                                                </div>
                                            </div>
                                        </header>
                                        <section className="flex flex-col py-8 pr-4 pl-8 w-full max-md:pl-5 max-md:max-w-full">
                                            <div className="flex flex-wrap gap-2 justify-between items-center w-full text-sm leading-6 whitespace-nowrap max-w-[698px] max-md:max-w-full">
                                                <button
                                                    onClick={handleDissolveReport}
                                                    className="flex gap-8 cursor-pointer items-center self-stretch pt-4 pr-16 pb-6 pl-4 my-auto bg-zinc-100 min-w-60 text-neutral-800 w-[345px] max-md:pr-5 hover:bg-zinc-200 transition-colors"
                                                >
                                                    <span className="self-stretch my-auto text-neutral-800">
                                                        Tolerar
                                                    </span>
                                                </button>
                                                <button
                                                    onClick={handleResolveReport}
                                                    className="flex gap-8 cursor-pointer items-center self-stretch pt-4 pr-16 pb-6 pl-4 my-auto bg-neutral-800 min-w-60 text-zinc-100 w-[345px] max-md:pr-5 hover:bg-neutral-700 transition-colors"
                                                >
                                                    <span className="self-stretch my-auto text-zinc-100">
                                                        Suspender
                                                    </span>
                                                </button>
                                            </div>
                                        </section>
                                    </article>
                                </div>
                            </div>
                        )}

                        {/* Report Details - Publicações */}
                        {activeTab === "Reportes" && reportesActiveTab === "publicacoes" && selectedPostReport && (
                            <div className="max-w-full">
                                <div className="px-4 pt-4 pb-80 w-full bg-zinc-100 max-md:pb-24 max-md:max-w-full">
                                    <article className="mb-0 bg-white max-md:mb-2.5 max-md:max-w-full">
                                        <header className="flex flex-col justify-center p-8 w-full bg-white rounded max-md:px-5 max-md:max-w-full">
                                            <div className="w-full max-md:max-w-full">
                                                <div className="flex justify-between items-start w-full max-md:max-w-full">
                                                    <div className="flex items-center min-w-60">
                                                        <img
                                                            src={selectedPostReport.reportedPost.author.profile_picture || "/no-profile-pic.png"}
                                                            alt={`${selectedPostReport.reportedPost.author.name} profile picture`}
                                                            className="object-contain shrink-0 self-stretch my-auto w-11 aspect-square"
                                                        />
                                                        <div className="self-stretch my-auto min-w-60 w-[342px]">
                                                            <div className="flex gap-2 items-center w-full h-[23px]">
                                                                <div className="flex overflow-hidden gap-2.5 justify-center items-center self-stretch px-3 my-auto">
                                                                    <span className="self-stretch my-auto text-sm text-neutral-800">
                                                                        {selectedPostReport.reportedPost.author.name}
                                                                    </span>
                                                                    <CheckmarkFilled
                                                                        className={`object-contain shrink-0 self-stretch my-auto aspect-square w-[18px] ${getCheckmarkColorClass(selectedPostReport.reportedPost.author.role)}`}
                                                                        aria-label="Verificado"
                                                                    />
                                                                    <span className={`flex gap-2.5 justify-center items-center self-stretch px-3 py-1 my-auto text-xs whitespace-nowrap rounded ${getRoleBadgeClasses(selectedPostReport.reportedPost.author.role)}`}>
                                                                        {translateUserRole(selectedPostReport.reportedPost.author.role || "member")}
                                                                    </span>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                    <div className="flex flex-col items-end gap-2">
                                                        {getSeverityBadge(selectedPostReport.severity)}
                                                        <span className="text-xs text-[#525252]">
                                                            {selectedPostReport.confirmations} reportes
                                                        </span>
                                                    </div>
                                                </div>
                                                <div className="mt-6 w-full text-sm text-neutral-800 max-md:max-w-full">
                                                    <div className="flex flex-wrap gap-4 items-center w-full leading-6 max-md:max-w-full">
                                                        <span className="self-stretch my-auto font-semibold text-neutral-800">
                                                            Título da publicação:
                                                        </span>
                                                        <span className="self-stretch my-auto text-neutral-800">
                                                            {selectedPostReport.reportedPost.title}
                                                        </span>
                                                    </div>
                                                    <div className="mt-4 w-full max-md:max-w-full">
                                                        <h3 className="font-semibold leading-6 text-justify text-neutral-800">
                                                            Conteúdo da publicação:
                                                        </h3>
                                                        <p className="mt-2 leading-5 text-neutral-800 max-md:max-w-full">
                                                            {selectedPostReport.reportedPost.content}
                                                        </p>
                                                        {selectedPostReport.reportedPost.image && (
                                                            <img
                                                                src={selectedPostReport.reportedPost.image}
                                                                alt="Imagem da publicação"
                                                                className="mt-4 max-w-full h-auto rounded"
                                                            />
                                                        )}
                                                    </div>
                                                    <div className="mt-4 flex flex-wrap gap-4 items-center w-full leading-6 max-md:max-w-full">
                                                        <span className="self-stretch my-auto font-semibold text-neutral-800">
                                                            Motivo do reporte:
                                                        </span>
                                                        <span className="self-stretch my-auto text-neutral-800">
                                                            {selectedPostReport.reason}
                                                        </span>
                                                    </div>
                                                    <div className="mt-4 flex flex-wrap gap-4 items-center w-full leading-6 max-md:max-w-full">
                                                        <span className="self-stretch my-auto font-semibold text-neutral-800">
                                                            Reportado por:
                                                        </span>
                                                        <div className="flex items-center gap-2">
                                                            <img
                                                                src={selectedPostReport.reporter.profile_picture || "/no-profile-pic.png"}
                                                                alt={selectedPostReport.reporter.name}
                                                                className="w-6 h-6 rounded-full object-cover"
                                                            />
                                                            <span className="self-stretch my-auto text-neutral-800">
                                                                {selectedPostReport.reporter.name}
                                                            </span>
                                                        </div>
                                                    </div>
                                                    <div className="mt-4 w-full max-md:max-w-full">
                                                        <h3 className="font-semibold leading-6 text-justify text-neutral-800">
                                                            Descrição do reporte:
                                                        </h3>
                                                        <p className="mt-2 leading-5 text-neutral-800 max-md:max-w-full">
                                                            {selectedPostReport.description}
                                                        </p>
                                                    </div>
                                                    <div className="mt-4 flex gap-4 items-center">
                                                        <span className="font-semibold text-neutral-800">Data do post:</span>
                                                        <span className="text-neutral-800">{selectedPostReport.reportedPost.date}</span>
                                                    </div>
                                                    <div className="mt-2 flex gap-4 items-center">
                                                        <span className="font-semibold text-neutral-800">Data do reporte:</span>
                                                        <span className="text-neutral-800">{selectedPostReport.date}</span>
                                                    </div>
                                                    <div className="mt-2 flex gap-4 items-center">
                                                        <span className="font-semibold text-neutral-800">Categoria:</span>
                                                        <span className="text-neutral-800">{selectedPostReport.category}</span>
                                                    </div>
                                                    <div className="mt-4 flex gap-6 items-center">
                                                        <div className="flex items-center gap-1">
                                                            <Heart className="h-4 w-4 text-[#525252]" />
                                                            <span className="text-sm text-[#525252]">{selectedPostReport.reportedPost.likes}</span>
                                                        </div>
                                                        <div className="flex items-center gap-1">
                                                            <MessageSquare className="h-4 w-4 text-[#525252]" />
                                                            <span className="text-sm text-[#525252]">{selectedPostReport.reportedPost.comments}</span>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </header>
                                        <section className="flex flex-col py-8 pr-4 pl-8 w-full max-md:pl-5 max-md:max-w-full">
                                            <div className="flex flex-wrap gap-2 justify-between items-center w-full text-sm leading-6 whitespace-nowrap max-w-[698px] max-md:max-w-full">
                                                <button
                                                    onClick={handleDissolveReport}
                                                    className="flex gap-8 cursor-pointer items-center self-stretch pt-4 pr-16 pb-6 pl-4 my-auto bg-zinc-100 min-w-60 text-neutral-800 w-[345px] max-md:pr-5 hover:bg-zinc-200 transition-colors"
                                                >
                                                    <span className="self-stretch my-auto text-neutral-800">
                                                        Tolerar
                                                    </span>
                                                </button>
                                                <button
                                                    onClick={handleResolveReport}
                                                    className="flex gap-8 cursor-pointer items-center self-stretch pt-4 pr-16 pb-6 pl-4 my-auto bg-neutral-800 min-w-60 text-zinc-100 w-[345px] max-md:pr-5 hover:bg-neutral-700 transition-colors"
                                                >
                                                    <span className="self-stretch my-auto text-zinc-100">
                                                        Remover Publicação
                                                    </span>
                                                </button>
                                            </div>
                                        </section>
                                    </article>
                                </div>
                            </div>
                        )}

                        {/* Report Details - Comentários */}
                        {activeTab === "Reportes" && reportesActiveTab === "comentarios" && selectedCommentReport && (
                            <div className="max-w-full">
                                <div className="px-4 pt-4 pb-80 w-full bg-zinc-100 max-md:pb-24 max-md:max-w-full">
                                    <article className="mb-0 bg-white max-md:mb-2.5 max-md:max-w-full">
                                        <header className="flex flex-col justify-center p-8 w-full bg-white rounded max-md:px-5 max-md:max-w-full">
                                            <div className="w-full max-md:max-w-full">
                                                <div className="flex justify-between items-start w-full max-md:max-w-full">
                                                    <div className="flex items-center min-w-60">
                                                        <img
                                                            src={selectedCommentReport.reportedComment.author.profile_picture || "/no-profile-pic.png"}
                                                            alt={`${selectedCommentReport.reportedComment.author.name} profile picture`}
                                                            className="object-contain shrink-0 self-stretch my-auto w-11 aspect-square"
                                                        />
                                                        <div className="self-stretch my-auto min-w-60 w-[342px]">
                                                            <div className="flex gap-2 items-center w-full h-[23px]">
                                                                <div className="flex overflow-hidden gap-2.5 justify-center items-center self-stretch px-3 my-auto">
                                                                    <span className="self-stretch my-auto text-sm text-neutral-800">
                                                                        {selectedCommentReport.reportedComment.author.name}
                                                                    </span>
                                                                    <CheckmarkFilled
                                                                        className={`object-contain shrink-0 self-stretch my-auto aspect-square w-[18px] ${getCheckmarkColorClass(selectedCommentReport.reportedComment.author.role)}`}
                                                                        aria-label="Verificado"
                                                                    />
                                                                    <span className={`flex gap-2.5 justify-center items-center self-stretch px-3 py-1 my-auto text-xs whitespace-nowrap rounded ${getRoleBadgeClasses(selectedCommentReport.reportedComment.author.role)}`}>
                                                                        {translateUserRole(selectedCommentReport.reportedComment.author.role || "member")}
                                                                    </span>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                    <div className="flex flex-col items-end gap-2">
                                                        {getSeverityBadge(selectedCommentReport.severity)}
                                                        <span className="text-xs text-[#525252]">
                                                            {selectedCommentReport.confirmations} reportes
                                                        </span>
                                                    </div>
                                                </div>
                                                <div className="mt-6 w-full text-sm text-neutral-800 max-md:max-w-full">
                                                    <div className="flex flex-wrap gap-4 items-center w-full leading-6 max-md:max-w-full">
                                                        <span className="self-stretch my-auto font-semibold text-neutral-800">
                                                            Publicação relacionada:
                                                        </span>
                                                        <span className="self-stretch my-auto text-neutral-800">
                                                            {selectedCommentReport.reportedComment.postTitle}
                                                        </span>
                                                    </div>
                                                    <div className="mt-4 w-full max-md:max-w-full">
                                                        <h3 className="font-semibold leading-6 text-justify text-neutral-800">
                                                            Comentário reportado:
                                                        </h3>
                                                        <div className="mt-2 p-4 bg-gray-50 rounded border-l-4 border-gray-300">
                                                            <p className="leading-5 text-neutral-800 max-md:max-w-full">
                                                                "{selectedCommentReport.reportedComment.content}"
                                                            </p>
                                                            <div className="mt-2 flex items-center gap-4 text-xs text-gray-500">
                                                                <span>Data: {selectedCommentReport.reportedComment.date}</span>
                                                                <div className="flex items-center gap-1">
                                                                    <Heart className="h-3 w-3" />
                                                                    <span>{selectedCommentReport.reportedComment.likes}</span>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                    <div className="mt-4 flex flex-wrap gap-4 items-center w-full leading-6 max-md:max-w-full">
                                                        <span className="self-stretch my-auto font-semibold text-neutral-800">
                                                            Motivo do reporte:
                                                        </span>
                                                        <span className="self-stretch my-auto text-neutral-800">
                                                            {selectedCommentReport.reason}
                                                        </span>
                                                    </div>
                                                    <div className="mt-4 flex flex-wrap gap-4 items-center w-full leading-6 max-md:max-w-full">
                                                        <span className="self-stretch my-auto font-semibold text-neutral-800">
                                                            Reportado por:
                                                        </span>
                                                        <div className="flex items-center gap-2">
                                                            <img
                                                                src={selectedCommentReport.reporter.profile_picture || "/no-profile-pic.png"}
                                                                alt={selectedCommentReport.reporter.name}
                                                                className="w-6 h-6 rounded-full object-cover"
                                                            />
                                                            <span className="self-stretch my-auto text-neutral-800">
                                                                {selectedCommentReport.reporter.name}
                                                            </span>
                                                        </div>
                                                    </div>
                                                    <div className="mt-4 w-full max-md:max-w-full">
                                                        <h3 className="font-semibold leading-6 text-justify text-neutral-800">
                                                            Descrição do reporte:
                                                        </h3>
                                                        <p className="mt-2 leading-5 text-neutral-800 max-md:max-w-full">
                                                            {selectedCommentReport.description}
                                                        </p>
                                                    </div>
                                                    <div className="mt-4 flex gap-4 items-center">
                                                        <span className="font-semibold text-neutral-800">Data do reporte:</span>
                                                        <span className="text-neutral-800">{selectedCommentReport.date}</span>
                                                    </div>
                                                    <div className="mt-2 flex gap-4 items-center">
                                                        <span className="font-semibold text-neutral-800">Categoria:</span>
                                                        <span className="text-neutral-800">{selectedCommentReport.category}</span>
                                                    </div>
                                                </div>
                                            </div>
                                        </header>
                                        <section className="flex flex-col py-8 pr-4 pl-8 w-full max-md:pl-5 max-md:max-w-full">
                                            <div className="flex flex-wrap gap-2 justify-between items-center w-full text-sm leading-6 whitespace-nowrap max-w-[698px] max-md:max-w-full">
                                                <button
                                                    onClick={handleDissolveReport}
                                                    className="flex gap-8 cursor-pointer items-center self-stretch pt-4 pr-16 pb-6 pl-4 my-auto bg-zinc-100 min-w-60 text-neutral-800 w-[345px] max-md:pr-5 hover:bg-zinc-200 transition-colors"
                                                >
                                                    <span className="self-stretch my-auto text-neutral-800">
                                                        Tolerar
                                                    </span>
                                                </button>
                                                <button
                                                    onClick={handleResolveReport}
                                                    className="flex gap-8 cursor-pointer items-center self-stretch pt-4 pr-16 pb-6 pl-4 my-auto bg-neutral-800 min-w-60 text-zinc-100 w-[345px] max-md:pr-5 hover:bg-neutral-700 transition-colors"
                                                >
                                                    <span className="self-stretch my-auto text-zinc-100">
                                                        Remover Comentário
                                                    </span>
                                                </button>
                                            </div>
                                        </section>
                                    </article>
                                </div>
                            </div>
                        )}

                        {/* Report Details */}
                        {activeTab === "Denúncias" && selectedReport && (
                            <div className="max-w-full">
                                <div className="px-4 pt-4 pb-80 w-full bg-zinc-100 max-md:pb-24 max-md:max-w-full">
                                    <article className="mb-0 bg-white max-md:mb-2.5 max-md:max-w-full">
                                        <header className="flex flex-col justify-center p-8 w-full bg-white rounded max-md:px-5 max-md:max-w-full">
                                            <div className="w-full max-md:max-w-full">
                                                <div className="flex justify-between items-start w-full max-md:max-w-full">
                                                    <div className="flex items-center min-w-60">
                                                        <img
                                                            src={selectedReport.user.profile_picture || "/no-profile-pic.png"}
                                                            alt={`${selectedReport.user.name} profile picture`}
                                                            className="object-contain shrink-0 self-stretch my-auto w-11 aspect-square"
                                                        />
                                                        <div className="self-stretch my-auto min-w-60 w-[342px]">
                                                            <div className="flex gap-2 items-center w-full h-[23px]">
                                                                <div className="flex overflow-hidden gap-2.5 justify-center items-center self-stretch px-3 my-auto">
                                                                    <span className="self-stretch my-auto text-sm text-neutral-800">
                                                                        {selectedReport.reporter}
                                                                    </span>
                                                                    <CheckmarkFilled
                                                                        className={`object-contain shrink-0 self-stretch my-auto aspect-square w-[18px] ${getCheckmarkColorClass(selectedReport.user.role)}`}
                                                                        aria-label="Verificado"
                                                                    />
                                                                    <span className={`flex gap-2.5 justify-center items-center self-stretch px-3 py-1 my-auto text-xs whitespace-nowrap rounded ${getRoleBadgeClasses(selectedReport.user.role)}`}>
                                                                        {translateUserRole(selectedReport.user.role || "member")}
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
                                                            {selectedReport.title}
                                                        </span>
                                                    </div>
                                                    <div className="mt-2 w-full max-md:max-w-full">
                                                        <h3 className="font-semibold leading-6 text-justify text-neutral-800">
                                                            Descrição:
                                                        </h3>
                                                        <p className="mt-2 leading-5 text-neutral-800 max-md:max-w-full">
                                                            {selectedReport.description}
                                                        </p>
                                                    </div>
                                                </div>
                                            </div>
                                        </header>
                                        <section className="flex flex-col py-8 pr-4 pl-8 w-full max-md:pl-5 max-md:max-w-full">
                                            <div className="flex flex-wrap gap-2 justify-between items-center w-full text-sm leading-6 whitespace-nowrap max-w-[698px] max-md:max-w-full">
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
                                        </section>
                                    </article>
                                </div>
                            </div>
                        )}

                        {/* Poll Details */}
                        {activeTab === "Enquetes" && selectedPoll && (
                            <div className="max-w-full">
                                <div className="px-4 pt-4 pb-80 w-full bg-zinc-100 max-md:pb-24 max-md:max-w-full">
                                    <article className="mb-0 bg-white max-md:mb-2.5 max-md:max-w-full">
                                        <header className="flex flex-col justify-center p-8 w-full bg-white rounded max-md:px-5 max-md:max-w-full">
                                            <div className="w-full max-md:max-w-full">
                                                <div className="flex justify-between items-start w-full max-md:max-w-full">
                                                    <div className="flex items-center min-w-60">
                                                        <img
                                                            src={selectedPoll.user.profile_picture || "/no-profile-pic.png"}
                                                            alt={`${selectedPoll.user.name} profile picture`}
                                                            className="object-contain shrink-0 self-stretch my-auto w-11 aspect-square"
                                                        />
                                                        <div className="self-stretch my-auto min-w-60 w-[342px]">
                                                            <div className="flex gap-2 items-center w-full h-[23px]">
                                                                <div className="flex overflow-hidden gap-2.5 justify-center items-center self-stretch px-3 my-auto">
                                                                    <span className="self-stretch my-auto text-sm text-neutral-800">
                                                                        {selectedPoll.author}
                                                                    </span>
                                                                    <CheckmarkFilled
                                                                        className={`object-contain shrink-0 self-stretch my-auto aspect-square w-[18px] ${getCheckmarkColorClass(selectedPoll.user.role)}`}
                                                                        aria-label="Verificado"
                                                                    />
                                                                    <span className={`flex gap-2.5 justify-center items-center self-stretch px-3 py-1 my-auto text-xs whitespace-nowrap rounded ${getRoleBadgeClasses(selectedPoll.user.role)}`}>
                                                                        {translateUserRole(selectedPoll.user.role || "member")}
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
                                                            {selectedPoll.title}
                                                        </span>
                                                    </div>
                                                    <div className="mt-2 w-full max-md:max-w-full">
                                                        <h3 className="font-semibold leading-6 text-justify text-neutral-800">
                                                            Descrição:
                                                        </h3>
                                                        <p className="mt-2 leading-5 text-neutral-800 max-md:max-w-full">
                                                            {selectedPoll.description}
                                                        </p>
                                                    </div>
                                                    {selectedPoll.options && selectedPoll.options.length > 0 && (
                                                        <div className="mt-4 w-full max-md:max-w-full">
                                                            <h3 className="font-semibold leading-6 text-justify text-neutral-800">
                                                                Opções:
                                                            </h3>
                                                            <ul className="mt-2 leading-5 text-neutral-800 max-md:max-w-full">
                                                                {selectedPoll.options.map((option, index) => (
                                                                    <li key={index} className="py-1">• {option}</li>
                                                                ))}
                                                            </ul>
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        </header>
                                        <section className="flex flex-col py-8 pr-4 pl-8 w-full max-md:pl-5 max-md:max-w-full">
                                            <div className="flex flex-wrap gap-2 justify-between items-center w-full text-sm leading-6 whitespace-nowrap max-w-[698px] max-md:max-w-full">
                                                <button
                                                    onClick={() => {
                                                        toast.success("Enquete encerrada com sucesso!");
                                                    }}
                                                    className="flex gap-8 cursor-pointer items-center self-stretch pt-4 pr-16 pb-6 pl-4 my-auto bg-zinc-100 min-w-60 text-neutral-800 w-[345px] max-md:pr-5 hover:bg-zinc-200 transition-colors"
                                                >
                                                    <span className="self-stretch my-auto text-neutral-800">
                                                        Encerrar
                                                    </span>
                                                </button>
                                                <button
                                                    onClick={() => {
                                                        toast.success("Enquete aprovada com sucesso!");
                                                    }}
                                                    className="flex gap-8 cursor-pointer items-center self-stretch pt-4 pr-16 pb-6 pl-4 my-auto bg-neutral-800 min-w-60 text-zinc-100 w-[345px] max-md:pr-5 hover:bg-neutral-700 transition-colors"
                                                >
                                                    <span className="self-stretch my-auto text-zinc-100">
                                                        Aprovar
                                                    </span>
                                                </button>
                                            </div>
                                        </section>
                                    </article>
                                </div>
                            </div>
                        )}

                        {/* Announcement Details */}
                        {activeTab === "Anúncios" && selectedAnnouncement && (
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
                                                            className="object-contain shrink-0 self-stretch my-auto w-11 aspect-square"
                                                        />
                                                        <div className="self-stretch my-auto min-w-60 w-[342px]">
                                                            <div className="flex gap-2 items-center w-full h-[23px]">
                                                                <div className="flex overflow-hidden gap-2.5 justify-center items-center self-stretch px-3 my-auto">
                                                                    <span className="self-stretch my-auto text-sm text-neutral-800">
                                                                        {selectedAnnouncement.author}
                                                                    </span>
                                                                    <CheckmarkFilled
                                                                        className={`object-contain shrink-0 self-stretch my-auto aspect-square w-[18px] ${getCheckmarkColorClass(selectedAnnouncement.user.role)}`}
                                                                        aria-label="Verificado"
                                                                    />
                                                                    <span className={`flex gap-2.5 justify-center items-center self-stretch px-3 py-1 my-auto text-xs whitespace-nowrap rounded ${getRoleBadgeClasses(selectedAnnouncement.user.role)}`}>
                                                                        {translateUserRole(selectedAnnouncement.user.role || "member")}
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
                                                            {selectedAnnouncement.title}
                                                        </span>
                                                    </div>
                                                    <div className="mt-2 w-full max-md:max-w-full">
                                                        <h3 className="font-semibold leading-6 text-justify text-neutral-800">
                                                            Descrição:
                                                        </h3>
                                                        <p className="mt-2 leading-5 text-neutral-800 max-md:max-w-full">
                                                            {selectedAnnouncement.description}
                                                        </p>
                                                    </div>
                                                </div>
                                            </div>
                                        </header>
                                        <section className="flex flex-col py-8 pr-4 pl-8 w-full max-md:pl-5 max-md:max-w-full">
                                            <div className="flex flex-wrap gap-2 justify-between items-center w-full text-sm leading-6 whitespace-nowrap max-w-[698px] max-md:max-w-full">
                                                <button
                                                    onClick={() => {
                                                        toast.success("Anúncio despublicado com sucesso!");
                                                    }}
                                                    className="flex gap-8 cursor-pointer items-center self-stretch pt-4 pr-16 pb-6 pl-4 my-auto bg-zinc-100 min-w-60 text-neutral-800 w-[345px] max-md:pr-5 hover:bg-zinc-200 transition-colors"
                                                >
                                                    <span className="self-stretch my-auto text-neutral-800">
                                                        Despublicar
                                                    </span>
                                                </button>
                                                <button
                                                    onClick={() => {
                                                        toast.success("Anúncio publicado com sucesso!");
                                                    }}
                                                    className="flex gap-8 cursor-pointer items-center self-stretch pt-4 pr-16 pb-6 pl-4 my-auto bg-neutral-800 min-w-60 text-zinc-100 w-[345px] max-md:pr-5 hover:bg-neutral-700 transition-colors"
                                                >
                                                    <span className="self-stretch my-auto text-zinc-100">
                                                        Publicar
                                                    </span>
                                                </button>
                                            </div>
                                        </section>
                                    </article>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Modals */}
            {isAnnouncementModalOpen && (
                <ModalAnnouncement
                    onClose={() => setIsAnnouncementModalOpen(false)}
                    communityId={selectedCommunity?.id || ""}
                />
            )}

            {isImportUserModalOpen && (
                <ImportUserModal
                    isOpen={isImportUserModalOpen}
                    onClose={() => setIsImportUserModalOpen(false)}
                    onImport={handleImportUsers}
                    loading={isUserActionLoading}
                    emailValue={emailsToImport}
                    onEmailChange={setEmailsToImport}
                />
            )}

            {isDissolveModalOpen && (
                <RejectComplaintModal
                    isOpen={isDissolveModalOpen}
                    onClose={() => setIsDissolveModalOpen(false)}
                    onReject={handleActuallyTolerate}
                    complaintTitle={
                        selectedUserReport?.reportedUser.name ||
                        selectedPostReport?.reportedPost.title ||
                        selectedCommentReport?.reportedComment.author.name ||
                        selectedReport?.title ||
                        "Item"
                    }
                />
            )}

            {isResolveModalOpen && (
                <ApproveComplaintModal
                    isOpen={isResolveModalOpen}
                    onClose={() => setIsResolveModalOpen(false)}
                    onApprove={handleActuallyResolve}
                    complaintTitle={
                        selectedUserReport?.reportedUser.name ||
                        selectedPostReport?.reportedPost.title ||
                        selectedCommentReport?.reportedComment.author.name ||
                        selectedReport?.title ||
                        "Item"
                    }
                />
            )}

        </div>
    );
}
