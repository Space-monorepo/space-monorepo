"use client";
import React, { useState, useEffect, useRef } from "react";
import Cookies from "js-cookie";
import { API_URL } from "@/config";
import { useReportersList, ReportListItem } from "@/app/api/src/hooks/moderation/useReportersList";
import ReportersModal from "@/components/modals/ReportersModal";
import UserReportPreviewModal from "@/components/modals/UserReportPreviewModal";
import PostReportPreviewModal from "@/components/modals/PostReportPreviewModal";
import CommentReportPreviewModal from "@/components/modals/CommentReportPreviewModal";
import { ArrowLeft, Filter, Heart, MessageSquare } from "lucide-react";
import { View } from "@carbon/icons-react";
import Link from "next/link";
import { toast } from "react-toastify";
import { useModerationActions } from "@/app/api/src/hooks/moderation/useModerationActions";
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
import ModalPoll from "@/components/modals/posts/ModalPoll";
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
    // Data de entrada/associação na comunidade
    joined_date?: string;
    // Reputação pode ser um número (pontos) ou uma string (Nível)
    reputation?: number | string;
    // Popularidade como número de visualizações ou um valor numérico qualquer
    popularity?: number;
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

export type UserReport = {
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

export type PostReport = {
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

export type CommentReport = {
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
    options?: { id: string; answer: string; votes_count: number }[];
    likes?: number;
    comments?: number;
};

export default function ModerationPage() {
    // --- Estados para exibir lista de reportes ---
    // Modal states
    const [userReportersOpen, setUserReportersOpen] = useState<string | null>(null);
    const [postReportersOpen, setPostReportersOpen] = useState<string | null>(null);
    const [commentReportersOpen, setCommentReportersOpen] = useState<string | null>(null);

    // Estados para modais de preview de reportes
    const [isUserReportPreviewOpen, setIsUserReportPreviewOpen] = useState(false);
    const [isPostReportPreviewOpen, setIsPostReportPreviewOpen] = useState(false);
    const [isCommentReportPreviewOpen, setIsCommentReportPreviewOpen] = useState(false);
    const [previewUserReport, setPreviewUserReport] = useState<UserReport | null>(null);
    const [previewPostReport, setPreviewPostReport] = useState<PostReport | null>(null);
    const [previewCommentReport, setPreviewCommentReport] = useState<CommentReport | null>(null);

    // Hooks para buscar reportes
    const userReportersHook = useReportersList();
    const postReportersHook = useReportersList();
    const commentReportersHook = useReportersList();

    // --- Handlers para buscar e abrir lista de reportes ---
    const handleShowUserReporters = async (report: UserReport) => {
        if (!selectedCommunity) return;
        if (userReportersOpen === report.id) {
            setUserReportersOpen(null);
            return;
        }
        setUserReportersOpen(report.id);
        userReportersHook.fetchReporters("user", selectedCommunity.id, report.reportedUser.id);
    };

    const handleShowPostReporters = async (report: PostReport) => {
        if (!selectedCommunity) return;
        if (postReportersOpen === report.id) {
            setPostReportersOpen(null);
            return;
        }
        setPostReportersOpen(report.id);
        postReportersHook.fetchReporters("post", selectedCommunity.id, report.reportedPost.id);
    };

    const handleShowCommentReporters = async (report: CommentReport) => {
        if (!selectedCommunity) return;
        if (commentReportersOpen === report.id) {
            setCommentReportersOpen(null);
            return;
        }
        setCommentReportersOpen(report.id);
        commentReportersHook.fetchReporters("comment", selectedCommunity.id, report.reportedComment.id);
    };
    // ===================================
    // INÍCIO: TRECHO DE USUÁRIOS REPORTADOS
    // ===================================
    const renderUserReportsList = () => (
        <div className="max-w-full">
            <div className="px-4 pt-4 pb-80 w-full bg-zinc-100 max-md:pb-24 max-md:max-w-full">
                {userReports.map((report, index) => (
                    <article key={report.id} className={`mb-0 bg-white max-md:mb-2.5 max-md:max-w-full ${index > 0 ? "mt-4" : ""}`}>
                        <header className="flex flex-col justify-center p-8 w-full bg-white rounded max-md:px-5 max-md:max-w-full">
                            <div className="w-full max-md:max-w-full">
                                <div className="flex justify-between items-start w-full max-md:max-w-full">
                                    <div className="flex items-center min-w-60">
                                        <img
                                            src={report.reportedUser.profile_picture || "/no-profile-pic.png"}
                                            alt={`${report.reportedUser.name} profile picture`}
                                            className="object-contain shrink-0 self-stretch my-auto w-11 aspect-square"
                                        />
                                        <div className="self-stretch my-auto min-w-60 w-[342px]">
                                            <div className="flex gap-2 items-center w-full h-[23px]">
                                                <div className="flex overflow-hidden gap-2.5 justify-center items-center self-stretch px-3 my-auto">
                                                    <span className="self-stretch my-auto text-sm text-neutral-800">
                                                        {report.reportedUser.name}
                                                    </span>
                                                    <CheckmarkFilled
                                                        className={`object-contain shrink-0 self-stretch my-auto aspect-square w-[18px] ${getCheckmarkColorClass(report.reportedUser.role)}`}
                                                        aria-label="Verificado"
                                                    />
                                                    <div className="self-stretch my-auto text-[10px] text-black">
                                                        •
                                                    </div>
                                                    <span className={`flex gap-2.5 justify-center items-center self-stretch px-3 py-1 my-auto text-xs whitespace-nowrap rounded ${getRoleBadgeClasses(report.reportedUser.role)}`}>
                                                        {translateUserRole(report.reportedUser.role || "member")}
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-4">
                                        <div className="self-stretch my-auto text-sm text-neutral-500">
                                            {((voteCounts[report.id]?.tolerate || 0) + (voteCounts[report.id]?.suspend || 0))}/{VOTE_THRESHOLD} votos
                                        </div>
                                        {getSeverityBadge(report.severity)}
                                    </div>
                                </div>
                                <div className="mt-6 w-full text-sm text-neutral-800 max-md:max-w-full">
                                    <div className="flex flex-wrap gap-4 items-center w-full leading-6 max-md:max-w-full">
                                        <span className="self-stretch my-auto font-semibold text-neutral-800">
                                            Motivo:
                                        </span>
                                        <span className="self-stretch my-auto text-neutral-800">
                                            {report.reason}
                                        </span>
                                    </div>
                                    <div className="mt-4 w-full flex flex-col items-start gap-2">
                                        <button
                                            className="text-yellow-600 font-medium text-sm hover:text-yellow-700 transition-colors cursor-pointer"
                                            onClick={() => {
                                                setPreviewUserReport(report);
                                                setIsUserReportPreviewOpen(true);
                                            }}
                                        >
                                            Investigar usuário
                                        </button>
                                        <button
                                            className="text-yellow-600 font-medium text-sm hover:text-yellow-700 transition-colors cursor-pointer"
                                            onClick={() => handleShowUserReporters(report)}
                                        >
                                            Ver reportes
                                        </button>
                                        <ReportersModal
                                            isOpen={userReportersOpen === report.id}
                                            onClose={() => setUserReportersOpen(null)}
                                            reporters={userReportersHook.reporters}
                                            loading={userReportersHook.loading}
                                        />
                                    </div>
                                </div>
                            </div>
                        </header>
                        <section className="py-8 pr-4 pl-8 w-full text-sm max-md:pl-5 max-md:max-w-full">
                            <div className="w-full leading-none max-md:max-w-full">
                                <div className="flex flex-wrap gap-36 items-start w-full max-md:max-w-full">
                                    <div className="flex flex-col">
                                        <div className="flex gap-2 items-center">
                                            <span className="self-stretch my-auto font-medium text-neutral-800">
                                                Número de reportes:
                                            </span>
                                            <span className="self-stretch my-auto text-neutral-500">
                                                {report.confirmations} reportes
                                            </span>
                                        </div>
                                        <div className="flex gap-2 items-center self-start mt-4">
                                            <span className="self-stretch my-auto font-medium text-neutral-800">
                                                Data de entrada:
                                            </span>
                                            <time className="self-stretch my-auto text-neutral-500">
                                                {report.reportedUser.joined_date
                                                    ? new Date(report.reportedUser.joined_date).toLocaleDateString("pt-BR")
                                                    : (report.date || "-")}
                                            </time>
                                        </div>
                                    </div>
                                    <div className="flex flex-col grow shrink w-[182px]">
                                        <div className="flex gap-2 items-center self-start">
                                            <span className="self-stretch my-auto font-medium text-neutral-800">
                                                Reputação:
                                            </span>
                                            <span className="self-stretch my-auto text-neutral-500">
                                                {typeof report.reportedUser.reputation !== "undefined" && report.reportedUser.reputation !== null
                                                    ? report.reportedUser.reputation
                                                    : (report.status === "Resolvido" ? "Suspenso" : "Sob Observação")}
                                            </span>
                                        </div>
                                        <div className="flex gap-2 items-center mt-4 w-full">
                                            <span className="self-stretch my-auto font-medium text-neutral-800">
                                                Popularidade:
                                            </span>
                                            <span className="self-stretch my-auto text-neutral-500">
                                                {typeof report.reportedUser.popularity !== "undefined" && report.reportedUser.popularity !== null
                                                    ? `${report.reportedUser.popularity} visualizações`
                                                    : `0 visualizações`}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="flex flex-wrap gap-2 justify-between items-center mt-10 w-full text-sm leading-6 whitespace-nowrap max-w-[698px] max-md:max-w-full">
                                <button
                                    onClick={async () => {
                                        setSelectedUserReport(report);
                                        await handleActuallyTolerate(report);
                                    }}
                                    className="flex gap-8 cursor-pointer items-center self-stretch pt-4 pr-16 pb-6 pl-4 my-auto bg-zinc-100 min-w-60 text-neutral-800 w-[345px] max-md:pr-5 hover:bg-zinc-200 transition-colors"
                                >
                                    <span className="self-stretch my-auto text-neutral-800">
                                        Tolerar
                                    </span>
                                </button>
                                <button
                                    onClick={async () => {
                                        setSelectedUserReport(report);
                                        await handleActuallyResolve(report);
                                    }}
                                    className="flex gap-8 cursor-pointer items-center self-stretch pt-4 pr-16 pb-6 pl-4 my-auto bg-neutral-800 min-w-60 text-zinc-100 w-[345px] max-md:pr-5 hover:bg-neutral-700 transition-colors"
                                >
                                    <span className="self-stretch my-auto text-zinc-100">
                                        Suspender
                                    </span>
                                </button>
                            </div>
                        </section>
                    </article>
                ))}
            </div>
        </div>
    );
    // ===================================
    // FIM: TRECHO DE USUÁRIOS REPORTADOS
    // ===================================

    // ===================================
    // INÍCIO: TRECHO DE PUBLICAÇÕES REPORTADAS
    // ===================================
    const renderPostReportsList = () => (
        <div className="max-w-full">
            <div className="px-4 pt-4 pb-80 w-full bg-zinc-100 max-md:pb-24 max-md:max-w-full">
                {postReports.map((report, index) => (
                    <article key={report.id} className={`mb-0 bg-white max-md:mb-2.5 max-md:max-w-full ${index > 0 ? "mt-4" : ""}`}>
                        <header className="flex flex-col justify-center p-8 w-full bg-white rounded max-md:px-5 max-md:max-w-full">
                            <div className="w-full max-md:max-w-full">
                                <div className="flex justify-between items-start w-full max-md:max-w-full">
                                    <div className="flex items-center min-w-60">
                                        <img
                                            src={report.reportedPost.author.profile_picture || "/no-profile-pic.png"}
                                            alt={`${report.reportedPost.author.name} profile picture`}
                                            className="object-contain shrink-0 self-stretch my-auto w-11 aspect-square"
                                        />
                                        <div className="self-stretch my-auto min-w-60 w-[342px]">
                                            <div className="flex gap-2 items-center w-full h-[23px]">
                                                <div className="flex overflow-hidden gap-2.5 justify-center items-center self-stretch px-3 my-auto">
                                                    <span className="self-stretch my-auto text-sm text-neutral-800">
                                                        {report.reportedPost.author.name}
                                                    </span>
                                                    <CheckmarkFilled
                                                        className={`object-contain shrink-0 self-stretch my-auto aspect-square w-[18px] ${getCheckmarkColorClass(report.reportedPost.author.role)}`}
                                                        aria-label="Verificado"
                                                    />
                                                    <div className="self-stretch my-auto text-[10px] text-black">
                                                        •
                                                    </div>
                                                    <span className={`flex gap-2.5 justify-center items-center self-stretch px-3 py-1 my-auto text-xs whitespace-nowrap rounded ${getRoleBadgeClasses(report.reportedPost.author.role)}`}>
                                                        {translateUserRole(report.reportedPost.author.role || "member")}
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-4">
                                        <div className="self-stretch my-auto text-sm text-neutral-500">
                                            {((voteCounts[report.id]?.tolerate || 0) + (voteCounts[report.id]?.suspend || 0))}/{VOTE_THRESHOLD} votos
                                        </div>
                                        {getSeverityBadge(report.severity)}
                                    </div>
                                </div>
                                <div className="mt-6 w-full text-sm text-neutral-800 max-md:max-w-full">
                                    <div className="flex flex-wrap gap-4 items-center w-full leading-6 max-md:max-w-full">
                                        <span className="self-stretch my-auto font-semibold text-neutral-800">
                                            Título:
                                        </span>
                                        <span className="self-stretch my-auto text-neutral-800">
                                            {report.reportedPost.title}
                                        </span>
                                    </div>
                                    <div className="flex flex-wrap gap-4 items-center w-full leading-6 mt-4 max-md:max-w-full">
                                        <span className="self-stretch my-auto font-semibold text-neutral-800">
                                            Descrição:
                                        </span>
                                        <span className="self-stretch my-auto text-neutral-800">
                                            {report.reportedPost.content}
                                        </span>
                                    </div>
                                    <div className="mt-4 w-full flex flex-col items-start gap-2">
                                        <button
                                            className="text-yellow-600 font-medium text-sm hover:text-yellow-700 transition-colors cursor-pointer"
                                            onClick={() => {
                                                setPreviewPostReport(report);
                                                setIsPostReportPreviewOpen(true);
                                            }}
                                        >
                                            Investigar publicação
                                        </button>
                                        <button
                                            className="text-yellow-600 font-medium text-sm hover:text-yellow-700 transition-colors cursor-pointer"
                                            onClick={() => handleShowPostReporters(report)}
                                        >
                                            Ver reportes
                                        </button>
                                        <ReportersModal
                                            isOpen={postReportersOpen === report.id}
                                            onClose={() => setPostReportersOpen(null)}
                                            reporters={postReportersHook.reporters}
                                            loading={postReportersHook.loading}
                                        />
                                    </div>
                                </div>
                            </div>
                        </header>
                        <section className="py-8 pr-4 pl-8 w-full text-sm max-md:pl-5 max-md:max-w-full">
                            <div className="w-full leading-none max-md:max-w-full">
                                <div className="flex flex-wrap gap-36 items-start w-full max-md:max-w-full">
                                    <div className="flex flex-col">
                                        <div className="flex gap-2 items-center">
                                            <span className="self-stretch my-auto font-medium text-neutral-800">
                                                Número de reportes:
                                            </span>
                                            <span className="self-stretch my-auto text-neutral-500">
                                                {report.confirmations} reportes
                                            </span>
                                        </div>
                                        <div className="flex gap-2 items-center self-start mt-4">
                                            <span className="self-stretch my-auto font-medium text-neutral-800">
                                                Data publicada:
                                            </span>
                                            <time className="self-stretch my-auto text-neutral-500">
                                                {report.reportedPost.date}
                                            </time>
                                        </div>
                                    </div>
                                    <div className="flex flex-col grow shrink w-[182px]">
                                        <div className="flex gap-2 items-center self-start">
                                            <span className="self-stretch my-auto font-medium text-neutral-800">
                                                Curtidas:
                                            </span>
                                            <span className="self-stretch my-auto text-neutral-500">
                                                {report.reportedPost.likes}
                                            </span>
                                        </div>
                                        <div className="flex gap-2 items-center mt-4 w-full">
                                            <span className="self-stretch my-auto font-medium text-neutral-800">
                                                Comentários:
                                            </span>
                                            <span className="self-stretch my-auto text-neutral-500">
                                                {report.reportedPost.comments}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="flex flex-wrap gap-2 justify-between items-center mt-10 w-full text-sm leading-6 whitespace-nowrap max-w-[698px] max-md:max-w-full">
                                <button
                                    onClick={async () => {
                                        setSelectedPostReport(report);
                                        await handleActuallyTolerate(report);
                                    }}
                                    className="flex gap-8 cursor-pointer items-center self-stretch pt-4 pr-16 pb-6 pl-4 my-auto bg-zinc-100 min-w-60 text-neutral-800 w-[345px] max-md:pr-5 hover:bg-zinc-200 transition-colors"
                                >
                                    <span className="self-stretch my-auto text-neutral-800">
                                        Tolerar
                                    </span>
                                </button>
                                <button
                                    onClick={async () => {
                                        setSelectedPostReport(report);
                                        await handleActuallyResolve(report);
                                    }}
                                    className="flex gap-8 cursor-pointer items-center self-stretch pt-4 pr-16 pb-6 pl-4 my-auto bg-neutral-800 min-w-60 text-zinc-100 w-[345px] max-md:pr-5 hover:bg-neutral-700 transition-colors"
                                >
                                    <span className="self-stretch my-auto text-zinc-100">
                                        Suspender
                                    </span>
                                </button>
                            </div>
                        </section>
                    </article>
                ))}
            </div>
        </div>
    );
    // ===================================
    // FIM: TRECHO DE PUBLICAÇÕES REPORTADAS
    // ===================================

    // ===================================
    // INÍCIO: TRECHO DE COMENTÁRIOS REPORTADOS
    // ===================================
    const renderCommentReportsList = () => (
        <div className="max-w-full">
            <div className="px-4 pt-4 pb-80 w-full bg-zinc-100 max-md:pb-24 max-md:max-w-full">
                {commentReports.map((report, index) => (
                    <article key={report.id} className={`mb-0 bg-white max-md:mb-2.5 max-md:max-w-full ${index > 0 ? "mt-4" : ""}`}>
                        <header className="flex flex-col justify-center p-8 w-full bg-white rounded max-md:px-5 max-md:max-w-full">
                            <div className="w-full max-md:max-w-full">
                                <div className="flex justify-between items-start w-full max-md:max-w-full">
                                    <div className="flex items-center min-w-60">
                                        <img
                                            src={report.reportedComment.author.profile_picture || "/no-profile-pic.png"}
                                            alt={`${report.reportedComment.author.name} profile picture`}
                                            className="object-contain shrink-0 self-stretch my-auto w-11 aspect-square"
                                        />
                                        <div className="self-stretch my-auto min-w-60 w-[342px]">
                                            <div className="flex gap-2 items-center w-full h-[23px]">
                                                <div className="flex overflow-hidden gap-2.5 justify-center items-center self-stretch px-3 my-auto">
                                                    <span className="self-stretch my-auto text-sm text-neutral-800">
                                                        {report.reportedComment.author.name}
                                                    </span>
                                                    <CheckmarkFilled
                                                        className={`object-contain shrink-0 self-stretch my-auto aspect-square w-[18px] ${getCheckmarkColorClass(report.reportedComment.author.role)}`}
                                                        aria-label="Verificado"
                                                    />
                                                    <div className="self-stretch my-auto text-[10px] text-black">
                                                        •
                                                    </div>
                                                    <span className={`flex gap-2.5 justify-center items-center self-stretch px-3 py-1 my-auto text-xs whitespace-nowrap rounded ${getRoleBadgeClasses(report.reportedComment.author.role)}`}>
                                                        {translateUserRole(report.reportedComment.author.role || "member")}
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-4">
                                        <div className="self-stretch my-auto text-sm text-neutral-500">
                                            {((voteCounts[report.id]?.tolerate || 0) + (voteCounts[report.id]?.suspend || 0))}/{VOTE_THRESHOLD} votos
                                        </div>
                                        {getSeverityBadge(report.severity)}
                                    </div>
                                </div>
                                <div className="mt-6 w-full text-sm text-neutral-800 max-md:max-w-full">
                                    <div className="flex flex-col gap-2 w-full max-md:max-w-full">
                                        <span className="font-semibold text-neutral-800">
                                            Comentário:
                                        </span>
                                        <span className="text-neutral-800 leading-6">
                                            {report.reportedComment.content}
                                        </span>
                                    </div>
                                    <div className="mt-4 w-full flex flex-col items-start gap-2">
                                        <button
                                            className="text-yellow-600 font-medium text-sm hover:text-yellow-700 transition-colors cursor-pointer"
                                            onClick={() => {
                                                setPreviewCommentReport(report);
                                                setIsCommentReportPreviewOpen(true);
                                            }}
                                        >
                                            Investigar comentário
                                        </button>
                                        <button
                                            className="text-yellow-600 font-medium text-sm hover:text-yellow-700 transition-colors cursor-pointer"
                                            onClick={() => handleShowCommentReporters(report)}
                                        >
                                            Ver reportes
                                        </button>
                                        <ReportersModal
                                            isOpen={commentReportersOpen === report.id}
                                            onClose={() => setCommentReportersOpen(null)}
                                            reporters={commentReportersHook.reporters}
                                            loading={commentReportersHook.loading}
                                        />
                                    </div>
                                </div>
                            </div>
                        </header>
                        <section className="py-8 pr-4 pl-8 w-full text-sm max-md:pl-5 max-md:max-w-full">
                            <div className="w-full leading-none max-md:max-w-full">
                                <div className="flex flex-wrap gap-36 items-start w-full max-md:max-w-full">
                                    <div className="flex flex-col">
                                        <div className="flex gap-2 items-center">
                                            <span className="self-stretch my-auto font-medium text-neutral-800">
                                                Número de reportes:
                                            </span>
                                            <span className="self-stretch my-auto text-neutral-500">
                                                {report.confirmations} reportes
                                            </span>
                                        </div>
                                        <div className="flex gap-2 items-center self-start mt-4">
                                            <span className="self-stretch my-auto font-medium text-neutral-800">
                                                Data publicada:
                                            </span>
                                            <time className="self-stretch my-auto text-neutral-500">
                                                {report.reportedComment.date}
                                            </time>
                                        </div>
                                    </div>
                                    <div className="flex flex-col grow shrink w-[182px]">
                                        <div className="flex gap-2 items-center self-start">
                                            <span className="self-stretch my-auto font-medium text-neutral-800">
                                                Curtidas:
                                            </span>
                                            <span className="self-stretch my-auto text-neutral-500">
                                                {report.reportedComment.likes}
                                            </span>
                                        </div>
                                        <div className="flex gap-2 items-center mt-4 w-full">
                                            <span className="self-stretch my-auto font-medium text-neutral-800">
                                                Categoria:
                                            </span>
                                            <span className="self-stretch my-auto text-neutral-500">
                                                {report.category}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="flex flex-wrap gap-2 justify-between items-center mt-10 w-full text-sm leading-6 whitespace-nowrap max-w-[698px] max-md:max-w-full">
                                <button
                                    onClick={async () => {
                                        setSelectedCommentReport(report);
                                        await handleActuallyTolerate(report);
                                    }}
                                    className="flex gap-8 cursor-pointer items-center self-stretch pt-4 pr-16 pb-6 pl-4 my-auto bg-zinc-100 min-w-60 text-neutral-800 w-[345px] max-md:pr-5 hover:bg-zinc-200 transition-colors"
                                >
                                    <span className="self-stretch my-auto text-neutral-800">
                                        Tolerar
                                    </span>
                                </button>
                                <button
                                    onClick={async () => {
                                        setSelectedCommentReport(report);
                                        await handleActuallyResolve(report);
                                    }}
                                    className="flex gap-8 cursor-pointer items-center self-stretch pt-4 pr-16 pb-6 pl-4 my-auto bg-neutral-800 min-w-60 text-zinc-100 w-[345px] max-md:pr-5 hover:bg-neutral-700 transition-colors"
                                >
                                    <span className="self-stretch my-auto text-zinc-100">
                                        Suspender
                                    </span>
                                </button>
                            </div>
                        </section>
                    </article>
                ))}
            </div>
        </div>
    );
    // ===================================
    // FIM: TRECHO DE COMENTÁRIOS REPORTADOS
    // ===================================

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
    const [currentUserMemberId, setCurrentUserMemberId] = useState<string | null>(null);

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

    // Buscar o member_id do usuário logado na comunidade selecionada
    useEffect(() => {
        const fetchUserMemberId = async () => {
            if (!selectedCommunity || !user) return;

            try {
                const token = Cookies.get('token');
                if (!token) return;

                const response = await fetch(`${API_URL}/communities/${selectedCommunity.id}/members?user_id=${user.id}`, {
                    headers: { Authorization: `Bearer ${token}` }
                });

                if (response.ok) {
                    const data = await response.json();
                    const userMember = data.items?.find((m: any) => m.user?.id === user.id || m.user_id === user.id);
                    if (userMember) {
                        setCurrentUserMemberId(userMember.id);
                    }
                }
            } catch (error) {
                console.error('Erro ao buscar member_id do usuário:', error);
            }
        };

        fetchUserMemberId();
    }, [selectedCommunity?.id, user?.id]);

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
    const convertApiUserToUserReport = (apiUser: any): UserReport => {
        // A API de membros da comunidade retorna um objeto CommunityMemberResponse
        // com campos no nível superior (reputation, popularity, entered_in) e um
        // sub-objeto `user` com dados do usuário. Precisamos mesclar essas fontes.
        const member = apiUser || {};
        const userObj = member.user || {};
        // profile_picture pode vir como profile_picture ou profile_image_url
        const profilePicture = userObj.profile_picture || userObj.profile_image_url || userObj.profile_image || "/no-profile-pic.png";
        // joined/entered date pode estar em member.entered_in ou em user.joined_date/created_at
        const joinedDate = member.entered_in || userObj.joined_date || userObj.created_at || member.created_at || undefined;
        // reputação e popularidade podem existir tanto no nível do membro quanto no user
        const reputationValue = typeof member.reputation !== 'undefined' ? member.reputation : (userObj.reputation ?? userObj.reputation_level ?? undefined);
        const popularityValue = typeof member.popularity !== 'undefined' ? member.popularity : (userObj.popularity ?? userObj.views_count ?? userObj.views ?? undefined);

        return {
            id: apiUser.id,
            reportedUser: {
                id: userObj.id || member.id,
                name: userObj.name || userObj.username || member.name || "Usuário desconhecido",
                profile_picture: profilePicture,
                role: userObj.role || member.role || "member",
                joined_date: joinedDate,
                reputation: reputationValue,
                popularity: popularityValue,
            },
            reporter: {
                id: (apiUser.reporter && apiUser.reporter.id) || "system",
                name: (apiUser.reporter && (apiUser.reporter.name || apiUser.reporter.username)) || "Sistema",
                profile_picture: (apiUser.reporter && (apiUser.reporter.profile_picture || apiUser.reporter.profile_image_url)) || "/system-avatar.png",
                role: (apiUser.reporter && apiUser.reporter.role) || "admin",
                joined_date: apiUser.reporter && (apiUser.reporter.joined_date || apiUser.reporter.created_at),
                reputation: apiUser.reporter && (apiUser.reporter.reputation ?? apiUser.reporter.reputation_level),
                popularity: apiUser.reporter && (apiUser.reporter.popularity ?? apiUser.reporter.views_count ?? apiUser.reporter.views),
            },
            reason: apiUser.suspension_reason || apiUser.reason || "Violação das diretrizes da comunidade",
            description: apiUser.description || `Usuário reportado por comportamento inadequado. Status atual: ${apiUser.status}`,
            date: new Date(apiUser.created_at || apiUser.date).toLocaleDateString("pt-BR"),
            status: apiUser.status === "suspended" ? "Resolvido" : "Em análise",
            severity: apiUser.level_complaint || "Leve",
            confirmations: apiUser.report_count || 0,
            category: apiUser.category || "Comportamento",
        };
    };

    const convertApiPostToPostReport = (apiPost: any): PostReport => ({
        id: apiPost.id,
        reportedPost: {
            id: apiPost.id,
            title: apiPost.title,
            content: apiPost.content,
            author: {
                id: apiPost.user?.id || 'unknown',
                name: apiPost.user?.name || apiPost.user?.username || 'Usuário desconhecido',
                profile_picture: apiPost.user?.profile_picture,
                role: apiPost.user?.role || "member",
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
        severity: apiPost.level_complaint || "Leve",
        confirmations: apiPost.report_count || 0,
        category: "Conteúdo",
    });

    const convertApiCommentToCommentReport = (apiComment: any): CommentReport => ({
        id: apiComment.id,
        reportedComment: {
            id: apiComment.id,
            content: apiComment.content,
            // Normalizar possíveis formatos onde o autor pode vir
            // (member, user, author, created_by, creator, owner, user_info)
            author: (() => {
                const authorObj = apiComment.member || apiComment.user || apiComment.author || apiComment.created_by || apiComment.creator || apiComment.owner || apiComment.user_info || {};
                const id = authorObj.id || authorObj.user_id || authorObj.uuid || 'unknown';
                const name = authorObj.name || authorObj.full_name || authorObj.display_name || authorObj.username || authorObj.user_name || 'Usuário desconhecido';
                const profile_picture = authorObj.profile_picture || authorObj.profile_image_url || authorObj.profile_image || authorObj.avatar_url || authorObj.avatar || undefined;
                const role = authorObj.role || authorObj.user_role || authorObj.member_role || 'member';
                return { id, name, profile_picture, role };
            })(),
            date: new Date(apiComment.created_at || apiComment.createdAt || apiComment.date || Date.now()).toLocaleDateString("pt-BR"),
            postTitle: apiComment.post?.title || apiComment.post?.name || apiComment.postTitle || "Post não encontrado",
            likes: apiComment.likes_count || apiComment.likes || 0,
        },
        // Mapear reporter real quando disponível. A API pode fornecer o reporter
        // diretamente ou dentro de um array de reports. Usar fallbacks amigáveis.
        reporter: {
            id: apiComment.reporter?.id || apiComment.reported_by?.id || apiComment.reports?.[0]?.reporter?.id || apiComment.reports?.[0]?.user?.id || "community",
            name: apiComment.reporter?.name || apiComment.reported_by?.name || apiComment.reports?.[0]?.reporter?.name || apiComment.reports?.[0]?.user?.name || "Comunidade",
            profile_picture: apiComment.reporter?.profile_picture || apiComment.reported_by?.profile_picture || apiComment.reports?.[0]?.reporter?.profile_picture || apiComment.reports?.[0]?.user?.profile_picture || "/community-avatar.png",
            role: apiComment.reporter?.role || apiComment.reported_by?.role || apiComment.reports?.[0]?.reporter?.role || apiComment.reports?.[0]?.user?.role || "member",
        },
        reason: apiComment.reason || apiComment.report_reason || apiComment.reports?.[0]?.reason || apiComment.reports?.[0]?.report_reason || "Linguagem inadequada",
        description: apiComment.description || apiComment.report_description || apiComment.reports?.[0]?.description || `Comentário reportado (id: ${apiComment.id})`,
        date: new Date(apiComment.created_at).toLocaleDateString("pt-BR"),
        // status pode vir da API; mapear para os valores do frontend quando possível
        status: apiComment.status === 'resolved' || apiComment.status === 'suspended' ? 'Resolvido' : 'Em análise',
        severity: apiComment.level_complaint || apiComment.severity || "Leve",
        confirmations: apiComment.report_count || (apiComment.reports && apiComment.reports.length) || 0,
        category: apiComment.category || apiComment.type || "Comportamento",
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
        severity: ["Crítica", "Moderada", "Leve"].includes(post.level_complaint as string)
            ? (post.level_complaint as "Crítica" | "Moderada" | "Leve")
            : "Leve",
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
        options: Array.isArray(post.poll_options) ? post.poll_options.map(opt => ({
            id: opt.id,
            answer: opt.answer,
            votes_count: opt.votes_count
        })) : [],
        likes: post.likes_count ?? 0,
        comments: post.comments_count ?? 0,
    });


    // Dados reais da API convertidos para os formatos esperados
    const campaigns: Campaign[] = (apiCampaigns || []).map(convertPostToCampaign);
    const reports: Report[] = (apiReports || []).map(convertPostToReport);
    const announcements: Announcement[] = (apiAnnouncements || []).map(convertPostToAnnouncement);
    const polls: Poll[] = (apiPolls || []).map(convertPostToPoll);

    // Dados reais de moderação convertidos dos dados da API
    const userReports: UserReport[] = (reportedUsers || []).map((apiUser): UserReport => {
        return {
            id: apiUser.report_id || apiUser.id, // Usar report_id se disponível, senão fallback para o id do membro
            reportedUser: {
                id: apiUser.id,
                name: apiUser.name || "Usuário desconhecido",
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
            severity: "Leve",
            confirmations: apiUser.report_count || 0,
            category: "Comportamento",
        };
    });

    const postReports: PostReport[] = (reportedPosts || []).map((apiPost): PostReport => {
        return {
            id: apiPost.report_id || apiPost.id, // Usar report_id se disponível
            reportedPost: {
                id: apiPost.id,
                title: apiPost.title,
                content: apiPost.content,
                author: {
                    id: apiPost.user?.id || 'unknown',
                    name: apiPost.user?.name || 'Usuário desconhecido',
                    profile_picture: apiPost.user?.profile_picture,
                    role: apiPost.user?.role || "member",
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
            severity: "Leve",
            confirmations: apiPost.report_count || 0,
            category: "Conteúdo",
        };
    });

    const commentReports: CommentReport[] = (reportedComments || []).map((apiComment): CommentReport => {
        return {
            id: apiComment.report_id || apiComment.id, // Usar report_id se disponível
            reportedComment: {
                id: apiComment.id,
                content: apiComment.content,
                author: {
                    id: apiComment.user?.id || 'unknown',
                    name: apiComment.user?.name || 'Usuário desconhecido',
                    profile_picture: apiComment.user?.profile_picture,
                    role: apiComment.user?.role || 'member',
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
            description: `Comentário reportado (id: ${apiComment.id})`,
            date: new Date(apiComment.created_at).toLocaleDateString("pt-BR"),
            status: "Em análise",
            severity: "Leve",
            confirmations: apiComment.report_count || 0,
            category: "Comportamento",
        };
    });

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
            // Reset para primeira tab de reportes sem selecionar automaticamente
            setReportesActiveTab("usuarios");
            // Não seleciona automaticamente para mostrar a lista
        } else if (tab === "Denúncias" && reports.length > 0) {
            setSelectedReport(reports[0]);
        } else if (tab === "Enquetes" && polls.length > 0) {
            setSelectedPoll(polls[0]);
        } else if (tab === "Anúncios" && announcements.length > 0) {
            setSelectedAnnouncement(announcements[0]);
        }
    };

    // Não seleciona automaticamente nenhum item para permitir exibir a lista
    // useEffect(() => {
    //     if (
    //         activeTab === "Reportes" &&
    //         reportesActiveTab === "usuarios" &&
    //         userReports.length > 0 &&
    //         !selectedUserReport
    //     ) {
    //         setSelectedUserReport(userReports[0]);
    //     }
    // }, [activeTab, reportesActiveTab, userReports, selectedUserReport]);

    // Função para mudar tabs dentro dos reportes
    const handleReportesTabChange = (reportTab: string) => {
        setReportesActiveTab(reportTab);
        // Limpar seleções anteriores para mostrar a lista
        setSelectedUserReport(null);
        setSelectedPostReport(null);
        setSelectedCommentReport(null);

        // Não selecionar automaticamente o primeiro item para exibir a lista
        // if (reportTab === "usuarios" && userReports.length > 0) {
        //     setSelectedUserReport(userReports[0]);
        // } else if (reportTab === "publicacoes" && postReports.length > 0) {
        //     setSelectedPostReport(postReports[0]);
        // } else if (reportTab === "comentarios" && commentReports.length > 0) {
        //     setSelectedCommentReport(commentReports[0]);
        // }
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
    // Estado para modal de enquete
    const [isPollModalOpen, setIsPollModalOpen] = useState(false);

    // Handlers para ações de denúncia
    const handleDissolveReport = () => {
        setIsDissolveModalOpen(true);
    };

    const handleResolveReport = () => {
        setIsResolveModalOpen(true);
    };

    // Handlers reais para ações de moderação
    const { moderateReport } = useModerationActions();
    // Contador de votos locais por reporte (chave = report.id)
    // Alinha com o backend (REPORT_VOTES_THRESHOLD = 2)
    const VOTE_THRESHOLD = 2;
    const [voteCounts, setVoteCounts] = useState<Record<string, { tolerate: number; suspend: number }>>({});
    const handleActuallyTolerate = async (report: UserReport | PostReport | CommentReport) => {
        if (!selectedCommunity || !user || !currentUserMemberId) {
            if (!currentUserMemberId) {
                toast.error("Você precisa ser membro da comunidade para moderar");
            }
            return;
        }

        const reportId = report.id;

        if (!reportId) {
            toast.error("ID do reporte não encontrado");
            return;
        }

        try {
            const result: any = await moderateReport(selectedCommunity.id, reportId, {
                report_id: reportId,
                moderator_id: currentUserMemberId,
                vote: 'tolerate',
            });

            // Se o backend retornou uma action, a decisão foi tomada e executada
            if (result && result.action) {
                toast.success(result.message || 'Ação automática executada');
                // limpar contadores locais para este report
                setVoteCounts(prev => {
                    const copy = { ...prev };
                    delete copy[reportId];
                    return copy;
                });
                if (selectedCommunity) {
                    fetchReportedUsers(selectedCommunity.id);
                    fetchReportedPosts(selectedCommunity.id);
                    fetchReportedComments(selectedCommunity.id);
                }
            } else {
                // apenas registro do voto
                setVoteCounts(prev => {
                    const prevCounts = prev[reportId] || { tolerate: 0, suspend: 0 };
                    return { ...prev, [reportId]: { ...prevCounts, tolerate: prevCounts.tolerate + 1 } };
                });
                toast.success("Voto registrado");
            }

            setSelectedUserReport(null);
            setSelectedPostReport(null);
            setSelectedCommentReport(null);
        } catch (error: any) {
            toast.error(error.message || "Erro ao tolerar reporte");
        }
    };

    const handleActuallyResolve = async (report: UserReport | PostReport | CommentReport) => {
        if (!selectedCommunity || !user || !currentUserMemberId) {
            if (!currentUserMemberId) {
                toast.error("Você precisa ser membro da comunidade para moderar");
            }
            return;
        }

        const reportId = report.id;

        if (!reportId) {
            toast.error("ID do reporte não encontrado");
            return;
        }

        try {
            const result: any = await moderateReport(selectedCommunity.id, reportId, {
                report_id: reportId,
                moderator_id: currentUserMemberId,
                vote: 'suspend',
            });

            if (result && result.action) {
                toast.success(result.message || 'Ação automática executada');
                setVoteCounts(prev => {
                    const copy = { ...prev };
                    delete copy[reportId];
                    return copy;
                });
                if (selectedCommunity) {
                    fetchReportedUsers(selectedCommunity.id);
                    fetchReportedPosts(selectedCommunity.id);
                    fetchReportedComments(selectedCommunity.id);
                }
            } else {
                setVoteCounts(prev => {
                    const prevCounts = prev[reportId] || { tolerate: 0, suspend: 0 };
                    return { ...prev, [reportId]: { ...prevCounts, suspend: prevCounts.suspend + 1 } };
                });
                toast.success("Voto registrado");
            }

            setSelectedUserReport(null);
            setSelectedPostReport(null);
            setSelectedCommentReport(null);
        } catch (error: any) {
            toast.error(error.message || "Erro ao suspender reporte");
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
                            {activeTab !== "Reportes" && (
                                <>
                                    <button className="p-2 hover:bg-[#f4f4f4]">
                                        <FilterEdit className="h-4 w-4 text-[#525252]" />
                                    </button>
                                    <button className="p-2 hover:bg-[#f4f4f4]">
                                        <ChevronSort className="h-4 w-4 text-[#525252]" />
                                    </button>
                                </>
                            )}
                            {activeTab === "Anúncios" && (
                                <button
                                    className="ml-auto cursor-pointer px-3 min-w-[138px] min-h-[56px] py-1.5 bg-[#161616] text-white text-sm hover:bg-[#262626] flex items-center gap-10"
                                    onClick={() => setIsAnnouncementModalOpen(true)}
                                >
                                    Anunciar
                                    <Email className="h-4 w-4" />
                                </button>
                            )}
                            {activeTab === "Enquetes" && (
                                <button
                                    className="ml-auto cursor-pointer px-3 min-w-[138px] min-h-[56px] py-1.5 bg-[#161616] text-white text-sm hover:bg-[#262626] flex items-center gap-10"
                                    onClick={() => setIsPollModalOpen(true)}
                                >
                                    Criar enquete
                                    <Email className="h-4 w-4" />
                                </button>
                            )}
                        </div>

                        {/* Content List */}
                        <div className="h-full overflow-y-auto pb-20 no-scrollbar">

                            {/* Quando estiver em Reportes, mostrar apenas as abas internas (Usuários, Publicações, Comentários) */}
                            {activeTab === "Reportes" && (
                                <div className="space-y-0 mt-20">
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
                                                <View className="h-4 w-4 text-[#161616]" />
                                            </div>
                                        </div>
                                    </div>
                                ))}

                            {/* Polls List */}
                            {activeTab === "Enquetes" && (
                                <div className="flex flex-col mt-4">
                                    {polls.map((poll) => (
                                        <div
                                            key={poll.id}
                                            className={`w-full p-4 cursor-pointer transition-colors rounded-md border border-transparent ${selectedPoll?.id === poll.id ? 'bg-zinc-100' : 'bg-white hover:bg-zinc-50'}`}
                                            onClick={() => setSelectedPoll(poll)}
                                        >
                                            <div className="flex justify-between items-center">
                                                <span className="text-[12px] font-normal text-neutral-500">{poll.date}</span>
                                                <span className="flex items-center gap-1 text-[12px] font-normal text-neutral-500">
                                                    {poll.votes ? `${poll.votes.toLocaleString('pt-BR')} mil` : '0'}
                                                    <View className="h-4 w-4 text-[#161616]" />
                                                </span>
                                            </div>
                                            <div className="mt-1 text-[16px] font-normal text-black">{poll.title}</div>
                                            <div className="mt-1 text-[12px] font-normal text-neutral-500">
                                                Moderador: {poll.author}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}

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
                                                <View className="h-4 w-4 text-[#161616]" />
                                            </div>
                                        </div>
                                    </div>
                                ))}
                        </div>
                    </div>

                    {/* Right Section - Details Panel */}
                    <div className="ml-80">
                        {/* Lista de Denúncias*/}
                        {activeTab === "Denúncias" && selectedReport && (
                            <div className="max-w-full">
                                <div className="px-4 pt-4 pb-48 w-full bg-zinc-100 max-md:pb-24 max-md:max-w-full">
                                    <article className="bg-white max-md:max-w-full">
                                        <header className="flex flex-col justify-center p-8 w-full bg-white rounded max-md:px-5 max-md:max-w-full">
                                            <div className="w-full max-md:max-w-full">
                                                <div className="flex justify-between items-start w-full max-md:max-w-full">
                                                    <div className="flex items-center min-w-60">
                                                        <img
                                                            src={selectedReport.user.profile_picture || "/no-profile-pic.png"}
                                                            alt={`${selectedReport.user.name} avatar`}
                                                            className="object-contain shrink-0 self-stretch my-auto w-11 aspect-square"
                                                        />
                                                        <div className="self-stretch my-auto min-w-60 w-[342px]">
                                                            <div className="flex gap-2 items-center w-full h-[23px]">
                                                                <div className="flex overflow-hidden gap-2.5 justify-center items-center self-stretch px-3 my-auto">
                                                                    <h2 className="self-stretch my-auto text-sm text-neutral-800">
                                                                        {selectedReport.reporter}
                                                                    </h2>
                                                                    <CheckmarkFilled
                                                                        className={`object-contain shrink-0 self-stretch my-auto aspect-square w-[18px] ${getCheckmarkColorClass(selectedReport.user.role)}`}
                                                                        aria-label="Verificado"
                                                                    />
                                                                    <div className="self-stretch my-auto text-[10px] text-black">
                                                                        •
                                                                    </div>
                                                                    <span className={`flex gap-2.5 justify-center items-center self-stretch px-3 py-1 my-auto text-xs whitespace-nowrap rounded ${getRoleBadgeClasses(selectedReport.user.role)}`}>
                                                                        {translateUserRole(selectedReport.user.role || "member")}
                                                                    </span>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                                <div className="mt-6 w-full text-sm leading-6 max-md:max-w-full">
                                                    <div className="flex flex-wrap gap-4 items-center w-full text-neutral-800 max-md:max-w-full">
                                                        <span className="self-stretch my-auto font-semibold text-neutral-800">
                                                            Motivo:
                                                        </span>
                                                        <span className="self-stretch my-auto text-neutral-800">
                                                            {selectedReport.category}
                                                        </span>
                                                    </div>
                                                    <div className="mt-2 w-full max-md:max-w-full">
                                                        <span className="self-stretch my-auto text-neutral-800 leading-6">
                                                            {selectedReport.description || "Investigar denúncia"}
                                                        </span>
                                                    </div>
                                                </div>
                                            </div>
                                        </header>

                                        <section className="py-8 pr-4 pl-8 w-full text-sm max-md:pl-5 max-md:max-w-full">
                                            <div className="w-full leading-none max-md:max-w-full">
                                                <div className="flex flex-wrap gap-36 items-start w-full max-md:max-w-full">
                                                    <div className="flex flex-col">
                                                        <div className="flex gap-2 items-center">
                                                            <span className="self-stretch my-auto font-medium text-neutral-800">
                                                                Número de reportes:
                                                            </span>
                                                            <span className="self-stretch my-auto text-neutral-500">
                                                                {selectedReport.confirmations} reportes
                                                            </span>
                                                        </div>
                                                        <div className="flex gap-2 items-center self-start mt-4">
                                                            <span className="self-stretch my-auto font-medium text-neutral-800">
                                                                Data de entrada:
                                                            </span>
                                                            <span className="self-stretch my-auto text-neutral-500">
                                                                {selectedReport.date}
                                                            </span>
                                                        </div>
                                                    </div>
                                                    <div className="flex flex-col grow shrink w-[182px]">
                                                        <div className="flex gap-2 items-center self-start">
                                                            <span className="self-stretch my-auto font-medium text-neutral-800">
                                                                Status:
                                                            </span>
                                                            <span className="self-stretch my-auto text-neutral-500">
                                                                {selectedReport.status}
                                                            </span>
                                                        </div>
                                                        <div className="flex gap-2 items-center mt-4 w-full">
                                                            <span className="self-stretch my-auto font-medium text-neutral-800">
                                                                Popularidade:
                                                            </span>
                                                            <span className="self-stretch my-auto text-neutral-500">
                                                                {selectedReport.accesses || 0} visualizações
                                                            </span>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>

                                            <footer className="flex flex-wrap gap-2 justify-between items-center mt-10 w-full leading-6 whitespace-nowrap max-w-[698px] max-md:max-w-full">
                                                <button
                                                    onClick={() => {
                                                        setSelectedReport(selectedReport);
                                                        handleDissolveReport();
                                                    }}
                                                    className="flex gap-8 items-center self-stretch pt-4 pr-16 pb-6 pl-4 my-auto bg-zinc-100 min-w-60 text-neutral-800 w-[345px] max-md:pr-5 hover:bg-zinc-200 transition-colors"
                                                >
                                                    <span className="self-stretch my-auto">
                                                        Dissolver
                                                    </span>
                                                </button>
                                                <button
                                                    onClick={() => {
                                                        setSelectedReport(selectedReport);
                                                        handleResolveReport();
                                                    }}
                                                    className="flex gap-8 items-center self-stretch pt-4 pr-16 pb-6 pl-4 my-auto bg-neutral-800 min-w-60 text-zinc-100 w-[345px] max-md:pr-5 hover:bg-neutral-700 transition-colors"
                                                >
                                                    <span className="self-stretch my-auto text-zinc-100">
                                                        Resolver
                                                    </span>
                                                </button>
                                            </footer>
                                        </section>
                                    </article>
                                </div>
                            </div>
                        )}

                        {/* Lista de Enquetes: exibe apenas a enquete selecionada */}
                        {activeTab === "Enquetes" && selectedPoll && (
                            <div className="max-w-full">
                                <div className="px-4 pt-4 pb-48 w-full bg-zinc-100 max-md:pb-24 max-md:max-w-full">
                                    <main className="bg-white max-w-full">
                                        <article className="flex flex-col justify-center p-8 w-full bg-white rounded max-md:px-5 max-md:max-w-full">
                                            <div className="w-full max-md:max-w-full">
                                                <div className="flex justify-between items-start w-full max-md:max-w-full">
                                                    <header className="flex items-center min-w-60">
                                                        <img
                                                            src={selectedPoll.user.profile_picture || "/no-profile-pic.png"}
                                                            alt={`${selectedPoll.user.name} profile picture`}
                                                            className="object-contain shrink-0 self-stretch my-auto w-11 aspect-square rounded-[32px]"
                                                        />
                                                        <div className="self-stretch my-auto min-w-60 w-[342px]">
                                                            <div className="flex gap-2 items-center w-full h-[23px]">
                                                                <div className="flex overflow-hidden gap-2.5 justify-center items-center self-stretch px-3 my-auto">
                                                                    <h2 className="self-stretch my-auto text-sm text-neutral-800">
                                                                        {selectedPoll.author}
                                                                    </h2>
                                                                    <CheckmarkFilled
                                                                        className={`object-contain shrink-0 self-stretch my-auto aspect-square w-[18px] ${getCheckmarkColorClass(selectedPoll.user.role)}`}
                                                                        aria-label="Verificado"
                                                                    />
                                                                    <div className="self-stretch my-auto text-[10px] text-black">
                                                                        •
                                                                    </div>
                                                                    <div className={`flex gap-2.5 justify-center items-center self-stretch px-3 py-1 my-auto text-xs whitespace-nowrap rounded ${getRoleBadgeClasses(selectedPoll.user.role)}`}>
                                                                        <span className="self-stretch my-auto">
                                                                            {translateUserRole(selectedPoll.user.role || "member")}
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
                                                            {selectedPoll.title}
                                                        </p>
                                                    </div>
                                                    <div className="mt-2 w-full max-md:max-w-full">
                                                        <h2 className="font-semibold leading-6 text-justify text-neutral-800">
                                                            Descrição:
                                                        </h2>
                                                        <p className="mt-2 leading-5 text-neutral-800 max-md:max-w-full">
                                                            {selectedPoll.description || "Enquete criada para coletar opiniões da comunidade sobre temas importantes e decisões que afetam todos os membros."}
                                                        </p>
                                                    </div>
                                                </div>
                                                <img
                                                    src="https://api.builder.io/api/v1/image/assets/367ac41a58454bf7adac62a5f3afc83b/506828c0ec32c591f29f197ff573cb0d9d6761c1?placeholderIfAbsent=true"
                                                    alt="Poll illustration"
                                                    className="object-contain mt-6 w-full rounded aspect-[2.43] max-md:max-w-full"
                                                />
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
                                                                {selectedPoll.date}
                                                            </span>
                                                        </div>
                                                        <div className="flex gap-2 items-center self-stretch mt-4">
                                                            <span className="self-stretch my-auto font-medium text-neutral-800">
                                                                Número de acessos:
                                                            </span>
                                                            <span className="self-stretch my-auto text-neutral-500">
                                                                {Math.floor((selectedPoll.votes || 0) * 2.5)} acessos
                                                            </span>
                                                        </div>
                                                        <div className="flex gap-2 items-center mt-4">
                                                            <span className="self-stretch my-auto font-medium text-neutral-800">
                                                                Total de votos:
                                                            </span>
                                                            <span className="self-stretch my-auto text-neutral-500">
                                                                {selectedPoll.votes} votos
                                                            </span>
                                                        </div>
                                                    </div>
                                                    <div className="flex flex-col w-[198px]">
                                                        <div className="flex gap-2 items-center self-start">
                                                            <span className="self-stretch my-auto font-medium text-neutral-800">
                                                                Curtidas:
                                                            </span>
                                                            <span className="self-stretch my-auto text-neutral-500">
                                                                {selectedPoll.likes} curtidas
                                                            </span>
                                                        </div>
                                                        <div className="flex gap-2 items-center mt-4 w-full">
                                                            <span className="self-stretch my-auto font-medium text-neutral-800">
                                                                Comentários:
                                                            </span>
                                                            <span className="self-stretch my-auto text-neutral-500">
                                                                {selectedPoll.comments} comentários
                                                            </span>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </section>

                                        <section className="flex flex-col justify-center p-8 w-full max-md:px-5 max-md:max-w-full">
                                            <div className="w-full max-md:max-w-full">
                                                <h3 className="text-sm font-semibold leading-none text-neutral-800 max-md:max-w-full">
                                                    Opções da enquete
                                                </h3>
                                                <div className="mt-6 w-full max-md:max-w-full">
                                                    {selectedPoll.options && selectedPoll.options.length > 0 ? (
                                                        selectedPoll.options.map(option => {
                                                            const totalVotes = selectedPoll.options!.reduce((sum, opt) => sum + opt.votes_count, 0);
                                                            const percent = totalVotes > 0 ? Math.round((option.votes_count / totalVotes) * 100) : 0;
                                                            return (
                                                                <div key={option.id} className="mb-4">
                                                                    <div className="flex flex-wrap gap-10 justify-between items-center w-full text-xs leading-none max-md:max-w-full">
                                                                        <div className="flex gap-2 items-center self-stretch my-auto">
                                                                            <span className="self-stretch my-auto text-neutral-800">
                                                                                {percent}%
                                                                            </span>
                                                                            <span className="self-stretch my-auto text-neutral-900">
                                                                                {option.answer}
                                                                            </span>
                                                                        </div>
                                                                        <span className="self-stretch my-auto text-neutral-500">
                                                                            {option.votes_count} votos
                                                                        </span>
                                                                    </div>
                                                                    <div className="mt-2 w-full rounded-sm max-md:max-w-full">
                                                                        <div className="flex flex-col items-start rounded-sm border border-solid border-stone-300 max-md:pr-5 max-md:max-w-full">
                                                                            <div className="flex shrink-0 h-2 rounded-sm bg-neutral-800" style={{ width: `${percent}%`, minWidth: '8px' }} />
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                            );
                                                        })
                                                    ) : (
                                                        <div className="text-neutral-500">Nenhuma opção cadastrada.</div>
                                                    )}
                                                </div>

                                                {/* Botões do footer da enquete */}
                                                {/*
                                                <footer className="flex flex-wrap gap-2 justify-between items-center mt-10 w-full text-sm leading-6 whitespace-nowrap max-w-[698px] max-md:max-w-full">
                                                    <button
                                                        onClick={() => {
                                                            toast.success("Enquete encerrada com sucesso!");
                                                        }}
                                                        className="flex gap-8 items-center self-stretch pt-4 pr-16 pb-6 pl-4 my-auto bg-zinc-100 min-w-60 text-neutral-800 w-[345px] max-md:pr-5 hover:bg-zinc-200 transition-colors"
                                                    >
                                                        <span className="self-stretch my-auto">
                                                            Encerrar
                                                        </span>
                                                    </button>
                                                    <button
                                                        onClick={() => {
                                                            toast.success("Enquete aprovada com sucesso!");
                                                        }}
                                                        className="flex gap-8 items-center self-stretch pt-4 pr-16 pb-6 pl-4 my-auto bg-neutral-800 min-w-60 text-zinc-100 w-[345px] max-md:pr-5 hover:bg-neutral-700 transition-colors"
                                                    >
                                                        <span className="self-stretch my-auto text-zinc-100">
                                                            Aprovar
                                                        </span>
                                                    </button>
                                                </footer>
                                                */}
                                            </div>
                                        </section>
                                    </main>
                                </div>
                            </div>
                        )}

                        {/* Lista de Anúncios */}
                        {activeTab === "Anúncios" && selectedAnnouncement && (
                            <div className="max-w-full">
                                <div className="px-4 pt-4 pb-48 w-full bg-zinc-100 max-md:pb-24 max-md:max-w-full">
                                    <article className="bg-white max-md:max-w-full">
                                        <header className="flex flex-col justify-center p-8 w-full bg-white rounded max-md:px-5 max-md:max-w-full">
                                            <div className="w-full max-md:max-w-full">
                                                <div className="flex justify-between items-start w-full max-md:max-w-full">
                                                    <div className="flex items-center min-w-60">
                                                        <img
                                                            src={selectedAnnouncement.user.profile_picture || "/no-profile-pic.png"}
                                                            alt={`${selectedAnnouncement.user.name} avatar`}
                                                            className="object-contain shrink-0 self-stretch my-auto w-11 aspect-square"
                                                        />
                                                        <div className="self-stretch my-auto min-w-60 w-[342px]">
                                                            <div className="flex gap-2 items-center w-full h-[23px]">
                                                                <div className="flex overflow-hidden gap-2.5 justify-center items-center self-stretch px-3 my-auto">
                                                                    <h2 className="self-stretch my-auto text-sm text-neutral-800">
                                                                        {selectedAnnouncement.author}
                                                                    </h2>
                                                                    <CheckmarkFilled
                                                                        className={`object-contain shrink-0 self-stretch my-auto aspect-square w-[18px] ${getCheckmarkColorClass(selectedAnnouncement.user.role)}`}
                                                                        aria-label="Verificado"
                                                                    />
                                                                    <div className="self-stretch my-auto text-[10px] text-black">
                                                                        •
                                                                    </div>
                                                                    <span className={`flex gap-2.5 justify-center items-center self-stretch px-3 py-1 my-auto text-xs whitespace-nowrap rounded ${getRoleBadgeClasses(selectedAnnouncement.user.role)}`}>
                                                                        {translateUserRole(selectedAnnouncement.user.role || "member")}
                                                                    </span>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                                <div className="mt-6 w-full text-sm leading-6 max-md:max-w-full">
                                                    <div className="flex flex-wrap gap-4 items-center w-full text-neutral-800 max-md:max-w-full">
                                                        <span className="self-stretch my-auto font-semibold text-neutral-800">
                                                            Título:
                                                        </span>
                                                        <span className="self-stretch my-auto text-neutral-800">
                                                            {selectedAnnouncement.title}
                                                        </span>
                                                    </div>
                                                    <div className="mt-2 w-full font-medium text-yellow-600 max-md:max-w-full">
                                                        <p>Anúncio {selectedAnnouncement.status.toLowerCase()}</p>
                                                    </div>
                                                </div>
                                            </div>
                                        </header>

                                        <section className="py-8 pr-4 pl-8 w-full text-sm max-md:pl-5 max-md:max-w-full">
                                            <div className="w-full leading-none max-md:max-w-full">
                                                <div className="flex flex-wrap gap-20 items-start w-full max-md:max-w-full">
                                                    <div className="flex flex-col">
                                                        <div className="flex gap-2 items-center">
                                                            <span className="self-stretch my-auto font-medium text-neutral-800">
                                                                Número de visualizações:
                                                            </span>
                                                            <span className="self-stretch my-auto text-neutral-500">
                                                                {selectedAnnouncement.views} visualizações
                                                            </span>
                                                        </div>
                                                        <div className="flex gap-2 items-center self-start mt-4">
                                                            <span className="self-stretch my-auto font-medium text-neutral-800">
                                                                Data de criação:
                                                            </span>
                                                            <span className="self-stretch my-auto text-neutral-500">
                                                                {selectedAnnouncement.date}
                                                            </span>
                                                        </div>
                                                    </div>
                                                    <div className="flex flex-col grow shrink w-[182px]">
                                                        <div className="flex gap-2 items-center self-start">
                                                            <span className="self-stretch my-auto font-medium text-neutral-800">
                                                                Status:
                                                            </span>
                                                            <span className="self-stretch my-auto text-neutral-500">
                                                                {selectedAnnouncement.status}
                                                            </span>
                                                        </div>
                                                        <div className="flex gap-2 items-center mt-4 w-full">
                                                            <span className="self-stretch my-auto font-medium text-neutral-800">
                                                                Interações:
                                                            </span>
                                                            <span className="self-stretch my-auto text-neutral-500">
                                                                {(selectedAnnouncement.likes || 0) + (selectedAnnouncement.comments || 0)} interações
                                                            </span>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>

                                            <footer className="flex flex-wrap gap-2 justify-between items-center mt-10 w-full leading-6 whitespace-nowrap max-w-[698px] max-md:max-w-full">
                                                <button
                                                    onClick={() => {
                                                        toast.success("Anúncio despublicado com sucesso!");
                                                    }}
                                                    className="flex gap-8 items-center self-stretch pt-4 pr-16 pb-6 pl-4 my-auto bg-zinc-100 min-w-60 text-neutral-800 w-[345px] max-md:pr-5 hover:bg-zinc-200 transition-colors"
                                                >
                                                    <span className="self-stretch my-auto">
                                                        Despublicar
                                                    </span>
                                                </button>
                                                <button
                                                    onClick={() => {
                                                        toast.success("Anúncio publicado com sucesso!");
                                                    }}
                                                    className="flex gap-8 items-center self-stretch pt-4 pr-16 pb-6 pl-4 my-auto bg-neutral-800 min-w-60 text-zinc-100 w-[345px] max-md:pr-5 hover:bg-neutral-700 transition-colors"
                                                >
                                                    <span className="self-stretch my-auto text-zinc-100">
                                                        Publicar
                                                    </span>
                                                </button>
                                            </footer>
                                        </section>
                                    </article>
                                </div>
                            </div>
                        )}

                        {/* Reportes - Usuários: lista direta com ações */}
                        {activeTab === "Reportes" && reportesActiveTab === "usuarios" && renderUserReportsList()}

                        {/* Reportes - Publicações: lista direta com ações */}
                        {activeTab === "Reportes" && reportesActiveTab === "publicacoes" && renderPostReportsList()}

                        {/* Reportes - Comentários: lista direta com ações */}
                        {activeTab === "Reportes" && reportesActiveTab === "comentarios" && renderCommentReportsList()}
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
            {isPollModalOpen && (
                <ModalPoll
                    onClose={() => setIsPollModalOpen(false)}
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

            {/* Modal de preview de usuário reportado */}
            {isUserReportPreviewOpen && previewUserReport && (
                <UserReportPreviewModal
                    report={previewUserReport}
                    onClose={() => {
                        setIsUserReportPreviewOpen(false);
                        setPreviewUserReport(null);
                    }}
                />
            )}
            {/* Modal de preview de publicação reportada */}
            {isPostReportPreviewOpen && previewPostReport && (
                <PostReportPreviewModal
                    report={previewPostReport}
                    onClose={() => {
                        setIsPostReportPreviewOpen(false);
                        setPreviewPostReport(null);
                    }}
                />
            )}
            {/* Modal de preview de comentário reportado */}
            {isCommentReportPreviewOpen && previewCommentReport && (
                <CommentReportPreviewModal
                    report={previewCommentReport}
                    onClose={() => {
                        setIsCommentReportPreviewOpen(false);
                        setPreviewCommentReport(null);
                    }}
                />
            )}

        </div>
    );
}

// Componente para buscar e exibir detalhes reais do reporte de usuário da API
function UserReportDetails({ reportId, onTolerate, onSuspend }: {
    reportId: string;
    onTolerate: () => void;
    onSuspend: () => void;
}) {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [report, setReport] = useState<any>(null);

    useEffect(() => {
        async function fetchReport() {
            try {
                setLoading(true);
                setError(null);
                const response = await fetch(`/api/reports/users/${reportId}`);
                if (!response.ok) {
                    throw new Error("Erro ao buscar reporte");
                }
                const data = await response.json();
                setReport(data);
            } catch (err: any) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        }

        fetchReport();
    }, [reportId]);

    if (loading) {
        return (
            <div className="max-w-full">
                <div className="px-4 pt-4 pb-80 w-full bg-zinc-100 max-md:pb-24 max-md:max-w-full">
                    <div className="p-8 text-center">Carregando...</div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="max-w-full">
                <div className="px-4 pt-4 pb-80 w-full bg-zinc-100 max-md:pb-24 max-md:max-w-full">
                    <div className="p-8 text-center text-red-500">Erro: {error}</div>
                </div>
            </div>
        );
    }

    if (!report) return null;

    return (
        <div className="w-full">
            <div className="pt-4 pb-80 w-full bg-zinc-100 max-md:pb-24 max-md:max-w-full">
                <article className="bg-white w-full">
                    <header className="flex flex-col justify-center p-8 w-full bg-white rounded max-md:px-5 max-md:max-w-full">
                        <div className="w-full max-md:max-w-full">
                            <div className="flex justify-between items-start w-full max-md:max-w-full">
                                <div className="flex items-center min-w-60">
                                    <img
                                        src={report.reportedUser?.profile_picture || "/no-profile-pic.png"}
                                        alt={`${report.reportedUser?.name} avatar`}
                                        className="object-contain shrink-0 self-stretch my-auto w-11 aspect-square"
                                    />
                                    <div className="self-stretch my-auto min-w-60 w-[342px]">
                                        <div className="flex gap-2 items-center w-full h-[23px]">
                                            <div className="flex overflow-hidden gap-2.5 justify-center items-center self-stretch px-3 my-auto">
                                                <h2 className="self-stretch my-auto text-sm text-neutral-800">
                                                    {report.reportedUser?.name}
                                                </h2>
                                                <img
                                                    src="https://api.builder.io/api/v1/image/assets/2c92ea9fbec34a758f970e8cafff5cb1/0915c1f8d702c90f4deafed21adc581f37a91002?placeholderIfAbsent=true"
                                                    alt="Role indicator"
                                                    className="object-contain shrink-0 self-stretch my-auto aspect-square w-[18px]"
                                                />
                                                <span className="flex gap-2.5 justify-center items-center self-stretch px-3 py-1 my-auto text-xs whitespace-nowrap rounded bg-neutral-800 text-zinc-100">
                                                    {translateUserRole(report.reportedUser?.role || "member")}
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="mt-6 w-full text-sm leading-6 max-md:max-w-full">
                                <div className="flex flex-wrap gap-4 items-center w-full text-neutral-800 max-md:max-w-full">
                                    <span className="self-stretch my-auto font-semibold text-neutral-800">
                                        Motivo:
                                    </span>
                                    <span className="self-stretch my-auto text-neutral-800">
                                        {report.reason}
                                    </span>
                                </div>
                                <div className="mt-2 w-full font-medium text-yellow-600 max-md:max-w-full">
                                    <p>Investigar usuário</p>
                                </div>
                            </div>
                        </div>
                    </header>
                    <section className="py-8 pr-4 pl-8 w-full text-sm max-md:pl-5 max-md:max-w-full">
                        <div className="w-full leading-none max-md:max-w-full">
                            <div className="flex flex-wrap gap-36 items-start w-full max-md:max-w-full">
                                <div className="flex flex-col">
                                    <div className="flex gap-2 items-center">
                                        <span className="self-stretch my-auto font-medium text-neutral-800">
                                            Número de reportes:
                                        </span>
                                        <span className="self-stretch my-auto text-neutral-500">
                                            {report.confirmations} reportes
                                        </span>
                                    </div>
                                    <div className="flex gap-2 items-center self-start mt-4">
                                        <span className="self-stretch my-auto font-medium text-neutral-800">
                                            Data de entrada:
                                        </span>
                                        <time className="self-stretch my-auto text-neutral-500">
                                            {report.reportedUser?.joined_date
                                                ? new Date(report.reportedUser.joined_date).toLocaleDateString("pt-BR")
                                                : (report.date || "-")}
                                        </time>
                                    </div>
                                </div>
                                <div className="flex flex-col grow shrink w-[182px]">
                                    <div className="flex gap-2 items-center self-start">
                                        <span className="self-stretch my-auto font-medium text-neutral-800">
                                            Reputação:
                                        </span>
                                        <span className="self-stretch my-auto text-neutral-500">
                                            {typeof report.reportedUser?.reputation !== "undefined" && report.reportedUser?.reputation !== null
                                                ? report.reportedUser.reputation
                                                : (report.status === "Resolvido" ? "Suspenso" : "Sob Observação")}
                                        </span>
                                    </div>
                                    <div className="flex gap-2 items-center mt-4 w-full">
                                        <span className="self-stretch my-auto font-medium text-neutral-800">
                                            Popularidade:
                                        </span>
                                        <span className="self-stretch my-auto text-neutral-500">
                                            {typeof report.reportedUser?.popularity !== "undefined" && report.reportedUser?.popularity !== null
                                                ? `${report.reportedUser.popularity} visualizações`
                                                : `0 visualizações`}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="flex flex-wrap gap-2 justify-between items-center mt-10 w-full leading-6 whitespace-nowrap max-w-[698px] max-md:max-w-full">
                            <button
                                onClick={onTolerate}
                                className="flex gap-8 items-center self-stretch pt-4 pr-16 pb-6 pl-4 my-auto bg-zinc-100 min-w-60 text-neutral-800 w-[345px] max-md:pr-5 hover:bg-zinc-200 transition-colors"
                            >
                                <span className="self-stretch my-auto text-neutral-800">
                                    Tolerar
                                </span>
                            </button>
                            <button
                                onClick={onSuspend}
                                className="flex gap-8 items-center self-stretch pt-4 pr-16 pb-6 pl-4 my-auto bg-neutral-800 min-w-60 text-zinc-100 w-[345px] max-md:pr-5 hover:bg-neutral-700 transition-colors"
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
    );
}
