import React from "react";
import { createPortal } from "react-dom";
import Link from "next/link";
import { Bookmark, Activity, EllipsisVerticalIcon as OverflowMenuVertical } from "lucide-react";
import { CheckmarkFilled, ArrowUp, Forum } from "@carbon/icons-react";
import getRoleBadgeClasses from "@/components/badges/users/RoleBadgesClasses";
import getCheckmarkColorClass from "@/components/badges/users/CheckmarkColorClasses";
import { translatePostType } from "@/lib/postTypeTranslations";

interface PollOption {
    id: string;
    answer: string;
    votes_count: number;
}

interface PostPreviewModalProps {
    post: {
        id: string;
        title: string;
        content: string;
        author?: string;
        avatar?: string;
        role?: string;
        location?: string;
        type?: string;
        time?: string;
        imageUrl?: string;
        likes?: number;
        comments?: number;
        shares?: number;
        username?: string;
        user?: { id?: string; profile_picture?: string; profile_image_url?: string };
        liked?: boolean;
        alreadyParticipating?: boolean;
        community?: { id: string };
        // Props específicas para enquetes
        poll_question?: string;
        poll_options?: PollOption[];
        // Props específicas para denúncias
        confirmations_count?: number;
        status_complaint?: string;
        level_complaint?: string;
        // Props específicas para anúncios
        tags?: string[];
    } | null;
    isOpen: boolean;
    onClose: () => void;
}

const PostPreviewModal: React.FC<PostPreviewModalProps> = ({ post, isOpen, onClose }) => {
    const [openMenu, setOpenMenu] = React.useState(false);

    if (!isOpen || !post || typeof window === 'undefined') return null;

    const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
        if (e.target === e.currentTarget) {
            onClose();
        }
    };

    const handleLike = (e: React.MouseEvent) => {
        e.stopPropagation();
        // Implementar lógica de like aqui se necessário
    };

    const handleComment = (e: React.MouseEvent) => {
        e.stopPropagation();
        // Implementar lógica de comentário aqui se necessário
    };

    const handleShare = (e: React.MouseEvent) => {
        e.stopPropagation();
        // Implementar lógica de compartilhamento aqui se necessário
    };

    const handleParticipateCampaign = (e: React.MouseEvent) => {
        e.stopPropagation();
        // Implementar lógica de participação em campanha aqui se necessário
    };

    const handleVotePoll = (optionId: string) => {
        // Implementar lógica de votação em enquete aqui se necessário
        // await voteOnPoll(post.community?.id || 'default-community-id', optionId);
    };

    const handleReportPost = async (e: React.MouseEvent) => {
        e.stopPropagation();
        setOpenMenu(false);
        try {
            // Implementar lógica de denúncia aqui se necessário
            // await reportPost(post.community?.id || 'default-community-id', post.id);
        } catch {
            // Tratamento de erro silencioso
        }
    };

    const modalContent = (
        <div
            className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/10 backdrop-blur-sm"
            onClick={handleBackdropClick}
        >
            <div className="bg-white shadow-lg max-w-[680px] w-full p-8 relative">
                <button
                    className="absolute top-2 right-4 text-gray-500 hover:text-gray-700 text-2xl cursor-pointer"
                    onClick={onClose}
                >
                    &times;
                </button>
                <article>
                    <div className="w-full max-w-[632px] max-md:max-w-full">
                        <div className="w-full max-md:max-w-full">
                            <header className="flex flex-wrap gap-10 justify-between items-start w-full max-md:max-w-full">
                                <div className="flex items-start min-w-60">
                                    <div className="w-11 h-11 rounded-[32px] overflow-hidden shrink-0 flex items-center justify-center bg-neutral-200">
                                        <img
                                            src={post.user && (post.user.profile_image_url || post.user.profile_picture)
                                                ? (post.user.profile_image_url || post.user.profile_picture)
                                                : post.avatar || "/placeholder.svg"}
                                            alt={`${post.author} avatar`}
                                            className="object-cover w-full h-full"
                                        />
                                    </div>
                                    <div className="flex flex-col min-w-60 w-[342px]">
                                        <div className="flex gap-2 items-center w-full h-[23px]">
                                            <div className="flex overflow-hidden gap-2.5 justify-center items-center self-stretch px-3 my-auto">
                                                <Link
                                                    href={`/profile/${post.username || post.user?.id}`}
                                                    className="self-stretch my-auto text-sm text-neutral-800 hover:text-blue-600 whitespace-nowrap transition-colors hover:underline"
                                                >
                                                    {post.author}
                                                </Link>
                                                <CheckmarkFilled
                                                    className={`object-contain shrink-0 self-stretch my-auto aspect-square w-[18px] ${getCheckmarkColorClass(post.role)}`}
                                                    aria-label="Verificado"
                                                />
                                                <div className="self-stretch my-auto text-[10px] font-semibold">
                                                    •
                                                </div>
                                                <div className={`flex gap-2.5 justify-center items-center self-stretch px-3 py-1 my-auto text-xs whitespace-nowrap rounded ${getRoleBadgeClasses(post.role)}`}>
                                                    <div className="self-stretch my-auto">
                                                        {post.role}
                                                    </div>
                                                </div>
                                            </div>
                                            <div className="self-stretch my-auto text-xs leading-none text-justify whitespace-nowrap text-neutral-800">
                                                {post.location}
                                            </div>
                                        </div>
                                        <div className="self-start px-3 mt-2 text-xs font-semibold tracking-normal whitespace-nowrap text-neutral-500">
                                            <div className="flex items-center gap-1">
                                                <div className="self-stretch my-auto text-neutral-500">
                                                    {post.type || "Tipo não informado"}
                                                </div>
                                                <div className="self-stretch my-auto text-[10px] text-neutral-500">
                                                    •
                                                </div>
                                                <div className="self-stretch my-auto text-neutral-500">
                                                    {post.time}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div className="flex gap-4 items-center">
                                    <button
                                        className="p-1 hover:bg-gray-100 rounded-full transition-colors"
                                        title="Salvar nos favoritos"
                                    >
                                        <Bookmark className={`h-4 w-4 text-gray-500`} />
                                    </button>
                                    <div className="relative">
                                        <button
                                            className="p-1 hover:bg-gray-100 rounded-full transition-colors"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                setOpenMenu(openMenu ? false : true);
                                            }}
                                            aria-label="Mais opções"
                                            title="Mais opções"
                                        >
                                            <OverflowMenuVertical className="h-4 w-4 text-gray-500" />
                                        </button>
                                        {openMenu && (
                                            <div
                                                className="absolute right-0 z-20 mt-2 w-40 bg-white border border-gray-200 rounded shadow-lg animate-fade-in"
                                                tabIndex={-1}
                                                onBlur={() => setOpenMenu(false)}
                                            >
                                                <button
                                                    className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100 rounded"
                                                    onClick={handleReportPost}
                                                >
                                                    Reportar post
                                                </button>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </header>

                            <div className="mt-6 w-full text-neutral-800 max-md:max-w-full">
                                <div className="flex flex-row justify-between items-center w-full max-md:max-w-full">
                                    <div
                                        className="flex gap-2.5 items-center text-xl font-bold leading-relaxed min-w-60 px-0 w-0 flex-1"
                                        style={{ wordBreak: 'break-word' }}
                                    >
                                        <h2
                                            className="text-neutral-800 px-0 font-georgia font-bold break-words w-full max-w-full"
                                            style={{ fontFamily: 'Georgia, serif', fontWeight: 'bold', wordBreak: 'break-word', overflowWrap: 'break-word', whiteSpace: 'pre-line' }}
                                        >
                                            {post.title}
                                        </h2>
                                    </div>
                                    <div className="flex gap-2 items-center px-3 py-1 my-auto text-sm leading-none text-justify whitespace-nowrap rounded-sm flex-shrink-0">
                                        <div className="self-stretch my-auto text-neutral-800">{(post.likes ?? 0) + (post.comments ?? 0) + (post.shares ?? 0)}</div>
                                        <Activity className="h-4 w-4 text-gray-500" />
                                    </div>
                                </div>

                                {post.content && (
                                    <div
                                        className="mt-4 text-sm leading-5 text-justify text-neutral-800 max-md:max-w-full whitespace-pre-line font-regular break-words w-full max-w-full"
                                        style={{ wordBreak: 'break-word', overflowWrap: 'break-word', whiteSpace: 'pre-line' }}
                                    >
                                        {post.content}
                                    </div>
                                )}

                                {post.imageUrl && (
                                    <img
                                        src={post.imageUrl}
                                        alt="Post content"
                                        className="object-contain mt-4 w-full rounded aspect-[2.26] max-md:max-w-full"
                                    />
                                )}

                                {/* Botão Participar da Campanha */}
                                {post.type === 'Campanha' && (
                                    <button
                                        className={`mt-4 w-full py-2 px-4 text-left font-regular transition-colors ${post.alreadyParticipating ? 'bg-neutral-200 text-neutral-700 cursor-not-allowed' : 'bg-neutral-900 text-white hover:bg-neutral-800'}`}
                                        onClick={handleParticipateCampaign}
                                        disabled={post.alreadyParticipating}
                                    >
                                        {post.alreadyParticipating ? 'Já participa da campanha' : 'Participar da Campanha'}
                                    </button>
                                )}

                                {/* Seção da Enquete */}
                                {post.type === 'Enquete' && post.poll_question && post.poll_options && (
                                    <div className="mt-6 w-full">
                                        <div className="text-lg font-medium text-neutral-800 mb-4">
                                            {post.poll_question}
                                        </div>
                                        <div className="space-y-3">
                                            {post.poll_options.map((option) => {
                                                const totalVotes = post.poll_options!.reduce((sum: number, opt: PollOption) => sum + opt.votes_count, 0);
                                                const percentage = totalVotes > 0 ? Math.round((option.votes_count / totalVotes) * 100) : 0;

                                                return (
                                                    <div key={option.id} className="relative">
                                                        <button
                                                            className="w-full p-3 text-left border border-gray-200 rounded-lg hover:border-gray-300 transition-colors bg-white"
                                                            onClick={() => handleVotePoll(option.id)}
                                                        >
                                                            <div className="flex justify-between items-center">
                                                                <span className="text-sm text-neutral-800">{option.answer}</span>
                                                                <span className="text-xs text-neutral-500 ml-2">
                                                                    {percentage}% ({option.votes_count} votos)
                                                                </span>
                                                            </div>
                                                            <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                                                                <div
                                                                    className="bg-neutral-800 h-2 rounded-full transition-all duration-300"
                                                                    style={{ width: `${percentage}%` }}
                                                                />
                                                            </div>
                                                        </button>
                                                    </div>
                                                );
                                            })}
                                        </div>
                                        <div className="mt-4 text-xs text-neutral-500">
                                            Total de votos: {post.poll_options.reduce((sum: number, opt: PollOption) => sum + opt.votes_count, 0)}
                                        </div>
                                    </div>
                                )}

                                {/* Seção da Denúncia */}
                                {post.type === 'Denúncia' && (
                                    <div className="mt-6 w-full p-4 bg-red-50 rounded-lg border border-red-200">
                                        <div className="flex items-center gap-2 mb-3">
                                            <div className="w-2 h-2 rounded-full bg-red-500"></div>
                                            <span className="text-sm font-medium text-red-700">Denúncia em andamento</span>
                                        </div>
                                        <div className="grid grid-cols-2 gap-4 text-sm">
                                            <div>
                                                <span className="text-neutral-600">Status:</span>
                                                <span className="ml-2 text-neutral-800 font-medium">
                                                    {post.status_complaint === 'pending' && 'Pendente'}
                                                    {post.status_complaint === 'under_investigation' && 'Sob investigação'}
                                                    {post.status_complaint === 'resolved' && 'Resolvida'}
                                                    {!post.status_complaint && 'Pendente'}
                                                </span>
                                            </div>
                                            <div>
                                                <span className="text-neutral-600">Nível:</span>
                                                <span className={`ml-2 font-medium ${post.level_complaint === 'high' ? 'text-red-600' :
                                                    post.level_complaint === 'medium' ? 'text-yellow-600' :
                                                        'text-green-600'
                                                    }`}>
                                                    {post.level_complaint === 'high' && 'Alto'}
                                                    {post.level_complaint === 'medium' && 'Médio'}
                                                    {post.level_complaint === 'low' && 'Baixo'}
                                                    {!post.level_complaint && 'Baixo'}
                                                </span>
                                            </div>
                                        </div>
                                        <div className="mt-3 text-sm">
                                            <span className="text-neutral-600">Confirmações:</span>
                                            <span className="ml-2 text-neutral-800 font-medium">
                                                {post.confirmations_count ?? 0}
                                            </span>
                                        </div>
                                    </div>
                                )}

                                {/* Seção do Anúncio - Tags */}
                                {post.type === 'Anúncio' && post.tags && post.tags.length > 0 && (
                                    <div className="mt-4 w-full">
                                        <div className="flex flex-wrap gap-2">
                                            {post.tags.map((tag, index) => (
                                                <span
                                                    key={index}
                                                    className="px-3 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full"
                                                >
                                                    #{tag}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="flex justify-between items-center mt-10 w-full text-xs font-medium leading-none text-neutral-500 max-md:max-w-full">
                            <div className="flex overflow-hidden gap-8 items-center self-stretch my-auto min-h-5 w-[214px]">
                                <button
                                    className="flex overflow-hidden gap-2 items-center self-stretch my-auto text-justify whitespace-nowrap"
                                    onClick={handleLike}
                                    title="Curtir"
                                >
                                    <ArrowUp className="h-4 w-4 text-gray-500" />
                                    <div className="self-stretch my-auto text-neutral-500">
                                        {post.likes ?? 0}
                                    </div>
                                </button>
                                <button
                                    className="flex overflow-hidden gap-2 items-center self-stretch my-auto text-justify whitespace-nowrap transition-colors px-3 py-1"
                                    onClick={handleComment}
                                    title="Comentar"
                                >
                                    <Forum className="h-4 w-4 text-gray-500" />
                                    <div className="self-stretch my-auto text-neutral-500">
                                        {post.comments ?? 0}
                                    </div>
                                </button>
                                <button
                                    className="flex overflow-hidden gap-2 items-center self-stretch my-auto text-teal-700"
                                    onClick={handleShare}
                                    title="Compartilhar"
                                >
                                    <Activity className="h-4 w-4 text-teal-700" />
                                    <div className="self-stretch my-auto">
                                        {post.shares ?? 0}
                                    </div>
                                </button>
                            </div>
                        </div>
                    </div>
                </article>
            </div>
        </div>
    );

    return createPortal(modalContent, document.body);
};

export default PostPreviewModal;
