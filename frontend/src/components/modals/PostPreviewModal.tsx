import React from "react";
import { createPortal } from "react-dom";
import Link from "next/link";
import { Activity, EllipsisVerticalIcon as OverflowMenuVertical } from "lucide-react";
import { CheckmarkFilled, ArrowUp, Forum } from "@carbon/icons-react";
import { FaceSatisfied, TextBold, TextItalic, ListNumbered, ListBulleted } from "@carbon/icons-react";
import getRoleBadgeClasses from "@/components/badges/users/RoleBadgesClasses";
import getCheckmarkColorClass from "@/components/badges/users/CheckmarkColorClasses";
import { translateUserRole } from "@/lib/roleTranslations";
import { translatePostType } from "@/lib/postTypeTranslations";
import { getRelativeTime } from "@/lib/relativeTime";
import { voteOnPoll } from "@/app/api/src/services/post/postService";
import { confirmComplaint } from "@/app/api/src/services/post/postService";
import getTokenFromCookies from "@/app/api/src/controllers/getTokenFromCookies";
import usePostActions from "@/app/api/src/hooks/post/usePostActions";
import useReportPost from "@/app/api/src/hooks/post/useReportPost";
import { useCampaignParticipation } from "@/app/api/src/hooks/post/useCampaignParticipation";
import { toast } from "react-toastify";

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
        userVotedOptionId?: string;
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
    // Confirmação de denúncia
    const handleConfirmComplaint = async (e: React.MouseEvent) => {
        e.stopPropagation();
        if (!localPost) return;
        try {
            const token = getTokenFromCookies();
            await confirmComplaint(localPost.community?.id || "default-community-id", localPost.id, token ?? undefined);
            setLocalPost(prev => prev ? { ...prev, confirmations_count: (prev.confirmations_count ?? 0) + 1 } : prev);
            toast.success('Confirmação registrada!');
        } catch (err) {
            toast.error('Erro ao confirmar problema');
        }
    };
    const [openMenu, setOpenMenu] = React.useState(false);
    const [localPost, setLocalPost] = React.useState(post);
    const { likePost, unlikePost, listComments, addComment, sharePost, replyComment, likeComment, unlikeComment } = usePostActions();
    const { reportPost } = useReportPost();
    const { participate } = useCampaignParticipation();

    // Comments state for modal
    const [showComments, setShowComments] = React.useState(false);
    const [comments, setComments] = React.useState<any[]>([]);
    const [commentInput, setCommentInput] = React.useState("");
    const [loadingComments, setLoadingComments] = React.useState(false);
    const [commentsError, setCommentsError] = React.useState<string | null>(null);
    const [likedComments, setLikedComments] = React.useState<{ [key: string]: boolean }>({});
    const [replyingTo, setReplyingTo] = React.useState<string | null>(null);
    const [replyInput, setReplyInput] = React.useState<{ [key: string]: string }>({});

    // Sincronizar localPost com prop post
    React.useEffect(() => {
        setLocalPost(post);
    }, [post]);

    React.useEffect(() => {
    }, [post]);
    // Busca comentários do post
    const fetchComments = async () => {
        if (!localPost) return;
        setLoadingComments(true);
        setCommentsError(null);
        try {
            const communityId = localPost.community?.id || 'default-community-id';
            const token = getTokenFromCookies();
            if (!token) {
                toast.error('Usuário não autenticado (cookie ausente)');
            }
            const data = await listComments(communityId, localPost.id);
            const items = data?.items || [];

            setComments(buildCommentsTree(items));
            const likedMap: { [key: string]: boolean } = {};
            items.forEach((c: any) => { likedMap[c.id] = false; });
            setLikedComments(likedMap);
        } catch (err) {
            setCommentsError('Erro ao carregar comentários');
        } finally {
            setLoadingComments(false);
        }
    };

    function buildCommentsTree(flatComments: any[]): any[] {
        const commentsMap: { [key: string]: any & { children: any[] } } = {};
        const roots: (any & { children: any[] })[] = [];
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

    // Atualiza likes recursivamente na árvore de comentários
    function updateCommentLikes(commentsArr: any[], commentId: string, increment: number): any[] {
        return commentsArr.map(comment => {
            if (comment.id === commentId) {
                return { ...comment, likes_count: Math.max(0, (comment.likes_count || 0) + increment) };
            }
            const children = comment.children ? updateCommentLikes(comment.children, commentId, increment) : undefined;
            const replies = comment.replies ? updateCommentLikes(comment.replies, commentId, increment) : undefined;
            return { ...comment, children, replies };
        });
    }

    const handleLikeComment = async (comment: any) => {
        try {
            const communityId = localPost?.community?.id || 'default-community-id';
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
            setCommentsError('Erro ao curtir/descurtir comentário');
        }
    };

    const handleReply = async (parentId: string) => {
        const content = replyInput[parentId];
        if (!content?.trim() || !localPost) return;
        try {
            const communityId = localPost.community?.id || 'default-community-id';
            await replyComment(communityId, localPost.id, parentId, content.trim());
            setReplyInput(prev => ({ ...prev, [parentId]: '' }));
            setReplyingTo(null);
            fetchComments();
        } catch (err) {
            setCommentsError('Erro ao responder comentário');
        }
    };

    const handleAddComment = async () => {
        if (!localPost || !commentInput.trim()) return;
        try {
            const communityId = localPost.community?.id || 'default-community-id';
            const token = getTokenFromCookies();

            if (!token) {
                toast.error('Usuário não autenticado (cookie ausente)');
                return;
            }
            await addComment(communityId, localPost.id, commentInput.trim());
            setCommentInput('');
            fetchComments();
            setLocalPost(prev => prev ? { ...prev, comments: (prev.comments ?? 0) + 1 } : prev);
            toast.success('Comentário adicionado');
        } catch (err) {
            console.error('Erro ao adicionar comentário', err);
            toast.error('Erro ao adicionar comentário');
        }
    };

    if (!isOpen || !localPost || typeof window === 'undefined') return null;

    const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
        if (e.target === e.currentTarget) {
            onClose();
        }
    };

    const handleLike = async (e: React.MouseEvent) => {
        e.stopPropagation();
        if (!localPost) return;
        try {
            const communityId = localPost.community?.id || 'default-community-id';
            const token = getTokenFromCookies();

            if (!token) {
                toast.error('Usuário não autenticado (cookie ausente)');
                return;
            }
            if (!localPost.liked) {
                await likePost(communityId, localPost.id);
                setLocalPost(prev => prev ? { ...prev, likes: (prev.likes ?? 0) + 1, liked: true } : prev);
            } else {
                await unlikePost(communityId, localPost.id);
                setLocalPost(prev => prev ? { ...prev, likes: Math.max(0, (prev.likes ?? 1) - 1), liked: false } : prev);
            }
        } catch (err) {
            console.error('Erro like/unlike:', err);
            toast.error('Erro ao atualizar like');
        }
    };

    const handleComment = (e: React.MouseEvent) => {
        e.stopPropagation();
        setShowComments(prev => {
            const next = !prev;
            if (next) fetchComments();
            return next;
        });
    };

    const handleShare = async (e: React.MouseEvent) => {
        e.stopPropagation();
        if (!localPost) return;
        try {
            const communityId = localPost.community?.id || 'default-community-id';
            const token = getTokenFromCookies();

            if (!token) {
                toast.error('Usuário não autenticado (cookie ausente)');
                return;
            }
            await sharePost(communityId, localPost.id);
            setLocalPost(prev => prev ? { ...prev, shares: (prev.shares ?? 0) + 1 } : prev);
            toast.success('Post compartilhado');
        } catch (err) {
            console.error('Erro ao compartilhar:', err);
            toast.error('Erro ao compartilhar');
        }
    };

    const handleParticipateCampaign = async (e: React.MouseEvent) => {
        e.stopPropagation();
        if (!localPost) return;
        try {
            const communityId = localPost.community?.id || 'default-community-id';
            const token = getTokenFromCookies();

            if (!token) {
                toast.error('Usuário não autenticado (cookie ausente)');
                return;
            }
            await participate(communityId, localPost.id);
            setLocalPost(prev => prev ? { ...prev, alreadyParticipating: true } : prev);
            toast.success('Você agora faz parte da campanha!');
        } catch (err) {
            console.error('Erro participar campanha:', err);
            toast.error('Erro ao participar da campanha');
        }
    };

    const handleVotePoll = async (optionId: string) => {
        if (!localPost) return;
        const token = getTokenFromCookies();
        const communityId = localPost.community?.id || 'default-community-id';
        try {
            const response = await voteOnPoll(communityId, optionId, token ?? undefined);

            // A resposta do backend pode conter os dados em response.post.poll_options ou em response.options
            const updatedOptions = response?.post?.poll_options ?? response?.options ?? [];
            const updatedQuestion = response?.question ?? response?.post?.poll_question ?? localPost.poll_question;

            // Tenta inferir a opção votada pelo usuário a partir das opções retornadas
            const currentUserId = token ? JSON.parse(atob(token.split('.')[1])).sub : null;
            let userVotedOptionId: string | undefined = undefined;
            if (Array.isArray(updatedOptions) && currentUserId) {
                const votedOpt = updatedOptions.find((opt: any) => Array.isArray(opt.votes) && opt.votes.some((v: any) => v.user_id === currentUserId));
                if (votedOpt) userVotedOptionId = votedOpt.id;
            }

            // Fallback: se backend não retornou opções, mantém/ajusta baseado no estado anterior
            if (!userVotedOptionId) {
                if (localPost.userVotedOptionId === optionId) userVotedOptionId = undefined; // remover voto
                else userVotedOptionId = optionId; // assume que votou na opção clicada
            }

            // Atualiza estado local do modal
            setLocalPost(prev => prev ? { ...prev, poll_options: (Array.isArray(updatedOptions) && updatedOptions.length > 0) ? updatedOptions : prev.poll_options, poll_question: updatedQuestion, userVotedOptionId } : prev);

            toast.success('Voto contabilizado');
        } catch (err: any) {
            console.error('Erro ao votar na enquete', err);
            toast.error(err?.message || 'Erro ao votar na enquete');
        }
    };

    const handleReportPost = async (e: React.MouseEvent) => {
        e.stopPropagation();
        setOpenMenu(false);
        try {
            if (!localPost) return;
            await reportPost(localPost.community?.id || 'default-community-id', localPost.id);
            toast.success('Post denunciado!');
        } catch {
            // Tratamento de erro silencioso
        }
    };

    const renderComment = (comment: any, isChild = false) => {
        // API retorna 'member' em vez de 'user'
        const userObj = comment.member || comment.user;

        // Nome do usuário
        const displayName = userObj?.name ||
            userObj?.username ||
            userObj?.full_name ||
            comment.author ||
            'Usuário';

        // Role do membro
        const memberRole = userObj?.member_role ||
            userObj?.role ||
            comment.member_role;

        return (
            <div key={comment.id} className={`${isChild ? 'flex flex-wrap items-start self-end mt-6 max-w-full w-[592px]' : 'flex flex-wrap justify-between w-full max-md:max-w-full'}`}>
                <div className="flex flex-col items-center w-11">
                    <img
                        src={userObj?.profile_image_url || userObj?.profile_picture || '/no-profile-pic.png'}
                        alt={`${displayName} avatar`}
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
                                            {displayName}
                                        </div>
                                        <CheckmarkFilled
                                            className={`object-contain shrink-0 self-stretch my-auto aspect-square w-[18px] ${getCheckmarkColorClass(memberRole)}`}
                                            aria-label="Verificado"
                                        />
                                        <div className="self-stretch my-auto text-[10px] text-black font-semibold">
                                            •
                                        </div>
                                        {memberRole && (
                                            <div className={`flex gap-2.5 justify-center items-center self-stretch px-3 py-1 my-auto text-xs whitespace-nowrap rounded ${getRoleBadgeClasses(memberRole)}`}>
                                                <div className="self-stretch my-auto">
                                                    {translateUserRole(memberRole)}
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
                                        {comment.likes_count || 0} {comment.likes_count === 1 ? 'curtida' : 'curtidas'}
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
                                        Responder
                                    </div>
                                </div>
                            </div>
                        </div>
                        {replyingTo === comment.id && (
                            <div className="flex flex-col gap-2 items-start self-stretch w-full mt-4">
                                <div className="flex flex-col items-start self-stretch w-full">
                                    <div className="flex flex-col justify-between items-start self-stretch p-4 bg-gray-100 h-[160px] rounded-xs">
                                        <textarea
                                            value={replyInput[comment.id] || ''}
                                            onChange={e => setReplyInput(prev => ({ ...prev, [comment.id]: e.target.value }))}
                                            placeholder="Responda..."
                                            className="w-full h-full bg-transparent text-sm leading-6 text-neutral-600 max-sm:text-sm resize-none border-none outline-none placeholder:text-neutral-600"
                                            rows={2}
                                            onKeyDown={e => {
                                                if (e.key === 'Enter' && !e.shiftKey) {
                                                    e.preventDefault();
                                                    handleReply(comment.id);
                                                }
                                            }}
                                        />
                                        <div className="flex flex-row justify-between items-end w-full mt-2">
                                            <div className="flex gap-4 items-center max-sm:gap-3">
                                                <FaceSatisfied className="object-contain shrink-0 self-stretch my-auto w-5 aspect-square cursor-pointer hover:opacity-70 transition-opacity" />
                                                <TextBold className="object-contain shrink-0 self-stretch my-auto w-5 aspect-square cursor-pointer hover:opacity-70 transition-opacity" />
                                                <TextItalic className="object-contain shrink-0 self-stretch my-auto w-5 aspect-square cursor-pointer hover:opacity-70 transition-opacity" />
                                                <ListNumbered className="object-contain shrink-0 self-stretch my-auto w-5 aspect-square cursor-pointer hover:opacity-70 transition-opacity" />
                                                <ListBulleted className="object-contain shrink-0 self-stretch my-auto w-5 aspect-square cursor-pointer hover:opacity-70 transition-opacity" />
                                            </div>
                                            <div className="flex flex-row items-end">
                                                <button
                                                    className="px-3 py-1 bg-black text-white rounded disabled:opacity-50 hover:bg-gray-800 transition-colors"
                                                    onClick={() => handleReply(comment.id)}
                                                    disabled={!replyInput[comment.id] || !replyInput[comment.id].trim()}
                                                >
                                                    Responder
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
                        {comment.children.map((child: any) => renderComment(child, true))}
                    </div>
                )}
                {/* Renderizar replies recursivamente */}
                {Array.isArray(comment.replies) && comment.replies.length > 0 && (
                    <div className="flex flex-wrap items-start self-end mt-6 max-w-full w-[592px] pl-12">
                        {comment.replies.map((child: any) => renderComment(child, true))}
                    </div>
                )}
            </div>
        );
    };

    if (!localPost) return null;

    const modalContent = (
        <div
            className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/10 backdrop-blur-sm"
            onClick={handleBackdropClick}
        >
            <div className="bg-white shadow-lg max-w-[680px] w-full px-6 py-4 relative max-h-[90vh] overflow-y-auto no-scrollbar">
                <article>
                    <div className="w-full max-w-[632px] max-md:max-w-full">
                        <div className="w-full max-md:max-w-full">
                            <header className="flex flex-wrap gap-10 justify-between items-start w-full max-md:max-w-full">
                                <div className="flex items-start min-w-60">
                                    <div className="w-11 h-11 rounded-[32px] overflow-hidden shrink-0 flex items-center justify-center bg-neutral-200">
                                        <img
                                            src={localPost.user && (localPost.user.profile_image_url || localPost.user.profile_picture)
                                                ? (localPost.user.profile_image_url || localPost.user.profile_picture)
                                                : localPost.avatar || "/placeholder.svg"}
                                            alt={`${localPost.author} avatar`}
                                            className="object-cover w-full h-full"
                                        />
                                    </div>
                                    <div className="flex flex-col min-w-60 w-[342px]">
                                        <div className="flex gap-2 items-center w-full h-[23px]">
                                            <div className="flex overflow-hidden gap-2.5 justify-center items-center self-stretch px-3 my-auto">
                                                <Link
                                                    href={`/profile/${localPost.username || localPost.user?.id}`}
                                                    className="self-stretch my-auto text-sm text-neutral-800 hover:text-blue-600 whitespace-nowrap transition-colors hover:underline"
                                                >
                                                    {localPost.author}
                                                </Link>
                                                <CheckmarkFilled
                                                    className={`object-contain shrink-0 self-stretch my-auto aspect-square w-[18px] ${getCheckmarkColorClass(localPost.role)}`}
                                                    aria-label="Verificado"
                                                />
                                                <div className="self-stretch my-auto text-[10px] font-semibold">
                                                    •
                                                </div>
                                                <div className={`flex gap-2.5 justify-center items-center self-stretch px-3 py-1 my-auto text-xs whitespace-nowrap rounded ${getRoleBadgeClasses(localPost.role)}`}>
                                                    <div className="self-stretch my-auto">
                                                        {translateUserRole(localPost.role || "")}
                                                    </div>
                                                </div>
                                            </div>
                                            <div className="self-stretch my-auto text-xs leading-none text-justify whitespace-nowrap text-neutral-800">
                                                {localPost.location}
                                            </div>
                                        </div>
                                        <div className="self-start px-3 mt-2 text-[10px] font-semibold tracking-normal whitespace-nowrap text-neutral-500">
                                            <div className="flex items-center gap-1">
                                                <div className="self-stretch my-auto text-neutral-500">
                                                    {localPost.type || "Tipo não informado"}
                                                </div>
                                                <div className="self-stretch my-auto text-[10px] text-neutral-500">
                                                    •
                                                </div>
                                                <div className="self-stretch my-auto text-neutral-500">
                                                    {localPost.time}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div className="flex gap-2 items-center">
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
                                    <button
                                        className="p-1 hover:bg-gray-100 rounded-full transition-colors text-gray-500 text-xl leading-none"
                                        onClick={onClose}
                                        aria-label="Fechar pré-visualização"
                                        title="Fechar"
                                    >
                                        &times;
                                    </button>
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
                                            {localPost.title}
                                        </h2>
                                    </div>
                                    <div className="flex gap-2 items-center px-3 py-1 my-auto text-sm leading-none text-justify whitespace-nowrap rounded-sm flex-shrink-0">
                                        <div className="self-stretch my-auto text-neutral-800">{(localPost.likes ?? 0) + (localPost.comments ?? 0) + (localPost.shares ?? 0)}</div>
                                        <Activity className="h-4 w-4 text-gray-500" />
                                    </div>
                                </div>

                                {localPost.content && (
                                    <div
                                        className="mt-4 text-sm leading-5 text-justify text-neutral-800 max-md:max-w-full whitespace-pre-line font-regular break-words w-full max-w-full"
                                        style={{ wordBreak: 'break-word', overflowWrap: 'break-word', whiteSpace: 'pre-line' }}
                                    >
                                        {localPost.content}
                                    </div>
                                )}

                                {localPost.imageUrl && (
                                    <img
                                        src={localPost.imageUrl}
                                        alt="Post content"
                                        className="object-contain mt-4 w-full rounded aspect-[2.26] max-md:max-w-full"
                                    />
                                )}

                                {/* Botão Participar da Campanha */}
                                {localPost.type === 'Campanha' && (
                                    <button
                                        className={`mt-4 w-full py-2 px-4 text-left font-regular transition-colors ${localPost.alreadyParticipating ? 'bg-neutral-200 text-neutral-700 cursor-not-allowed' : 'bg-neutral-900 text-white hover:bg-neutral-800'}`}
                                        onClick={handleParticipateCampaign}
                                        disabled={localPost.alreadyParticipating}
                                    >
                                        {localPost.alreadyParticipating ? 'Já participa da campanha' : 'Participar da Campanha'}
                                    </button>
                                )}

                                {/* Botão Confirmar problema para Denúncia */}
                                {localPost.type === 'Denúncia' && (
                                    <button
                                        className={`mt-4 w-full py-2 px-4 text-left font-regular transition-colors ${localPost.confirmations_count && localPost.confirmations_count > 0 ? 'bg-neutral-200 text-neutral-700 cursor-not-allowed' : 'bg-neutral-900 text-white hover:bg-neutral-800'}`}
                                        onClick={handleConfirmComplaint}
                                        disabled={Boolean(localPost.confirmations_count)}
                                    >
                                        {localPost.confirmations_count && localPost.confirmations_count > 0 ? 'Problema confirmado' : 'Confirmar problema'}
                                    </button>
                                )}

                                {/* Opções de Enquete */}
                                {localPost.type === 'Enquete' && Array.isArray(localPost.poll_options) && localPost.poll_options.length > 0 && (
                                    <div className="mt-6 w-full">
                                        {localPost.poll_question && (
                                            <h3 className="text-base font-semibold text-neutral-800 mb-6">
                                                {localPost.poll_question}
                                            </h3>
                                        )}
                                        {(localPost.poll_options ?? []).map((option) => {
                                            const totalVotes = Array.isArray(localPost.poll_options) ? localPost.poll_options.reduce((sum, opt) => sum + (opt.votes_count || 0), 0) : 0;
                                            const percent = totalVotes > 0 ? Math.round((option.votes_count / totalVotes) * 100) : 0;
                                            const isUserVote = (localPost as any).userVotedOptionId === option.id;
                                            return (
                                                <div
                                                    key={option.id}
                                                    className={`mb-4 cursor-pointer hover:opacity-80 transition-opacity`}
                                                >
                                                    <button
                                                        className={`w-full text-left bg-transparent border-none outline-none p-0 m-0 cursor-pointer`}
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            handleVotePoll(option.id);
                                                        }}
                                                    >
                                                        <div className="flex flex-wrap gap-10 justify-between items-center w-full text-xs leading-none">
                                                            <div className="flex gap-2 items-center self-stretch my-auto">
                                                                <span className="self-stretch my-auto text-neutral-800 font-medium">
                                                                    {percent}%
                                                                </span>
                                                                <span className="self-stretch my-auto text-neutral-900">
                                                                    {option.answer}
                                                                </span>
                                                            </div>
                                                            <span className="self-stretch my-auto text-neutral-500">
                                                                {option.votes_count} {option.votes_count === 1 ? 'voto' : 'votos'}
                                                            </span>
                                                        </div>
                                                        <div className="mt-2 w-full rounded-sm">
                                                            <div className="flex flex-col items-start rounded-sm border border-solid border-stone-300">
                                                                <div
                                                                    className="flex shrink-0 h-2 rounded-sm bg-neutral-800"
                                                                    style={{ width: `${percent}%`, minWidth: '8px' }}
                                                                />
                                                            </div>
                                                        </div>
                                                    </button>
                                                </div>
                                            );
                                        })}
                                    </div>
                                )}

                                {/* Seção da Denúncia */}
                                {/* {localPost.type === 'Denúncia' && (
                                    <div className="mt-6 w-full p-4 bg-red-50 rounded-lg border border-red-200">
                                        <div className="flex items-center gap-2 mb-3">
                                            <div className="w-2 h-2 rounded-full bg-red-500"></div>
                                            <span className="text-sm font-medium text-red-700">Denúncia em andamento</span>
                                        </div>
                                        <div className="grid grid-cols-2 gap-4 text-sm">
                                            <div>
                                                <span className="text-neutral-600">Status:</span>
                                                <span className="ml-2 text-neutral-800 font-medium">
                                                    {localPost.status_complaint === 'pending' && 'Pendente'}
                                                    {localPost.status_complaint === 'under_investigation' && 'Sob investigação'}
                                                    {localPost.status_complaint === 'resolved' && 'Resolvida'}
                                                    {!localPost.status_complaint && 'Pendente'}
                                                </span>
                                            </div>
                                            <div>
                                                <span className="text-neutral-600">Nível:</span>
                                                <span className={`ml-2 font-medium ${localPost.level_complaint === 'high' ? 'text-red-600' :
                                                    localPost.level_complaint === 'medium' ? 'text-yellow-600' :
                                                        'text-green-600'
                                                    }`}>
                                                    {localPost.level_complaint === 'high' && 'Alto'}
                                                    {localPost.level_complaint === 'medium' && 'Médio'}
                                                    {localPost.level_complaint === 'low' && 'Baixo'}
                                                    {!localPost.level_complaint && 'Baixo'}
                                                </span>
                                            </div>
                                        </div>
                                        <div className="mt-3 text-sm">
                                            <span className="text-neutral-600">Confirmações:</span>
                                            <span className="ml-2 text-neutral-800 font-medium">
                                                {localPost.confirmations_count ?? 0}
                                            </span>
                                        </div>
                                    </div>
                                )} */}

                                {/* Seção do Anúncio - Tags */}
                                {localPost.type === 'Anúncio' && localPost.tags && localPost.tags.length > 0 && (
                                    <div className="mt-4 w-full">
                                        <div className="flex flex-wrap gap-2">
                                            {localPost.tags.map((tag, index) => (
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
                                        {localPost.likes ?? 0}
                                    </div>
                                </button>
                                <button
                                    className="flex overflow-hidden gap-2 items-center self-stretch my-auto text-justify whitespace-nowrap transition-colors px-3 py-1"
                                    onClick={handleComment}
                                    title="Comentar"
                                >
                                    <Forum className="h-4 w-4 text-gray-500" />
                                    <div className="self-stretch my-auto text-neutral-500">
                                        {localPost.comments ?? 0}
                                    </div>
                                </button>
                                <button
                                    className="flex overflow-hidden gap-2 items-center self-stretch my-auto text-teal-700"
                                    onClick={handleShare}
                                    title="Compartilhar"
                                >
                                    <Activity className="h-4 w-4 text-teal-700" />
                                    <div className="self-stretch my-auto">
                                        {localPost.shares ?? 0}
                                    </div>
                                </button>
                            </div>
                        </div>
                    </div>

                    {showComments && (
                        <main className="flex flex-col shrink-0 gap-8 items-start p-4 bg-white w-full mt-6 max-md:p-3 max-sm:gap-6 max-sm:p-2">
                            {/* Comment Input Section */}
                            <div className="flex flex-col gap-2 items-start self-stretch">
                                <div className="flex flex-col items-start self-stretch">
                                    <div className="flex flex-col justify-between items-start self-stretch p-4 bg-gray-100 h-[160px] rounded-xs">
                                        <textarea
                                            id="comment-textarea-modal"
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
                                                    disabled={!commentInput.trim()}
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
                                        {comments.length}
                                    </span>
                                </div>
                            </header>

                            {/* Comments List */}
                            <section
                                className="flex flex-col p-4 bg-white rounded-sm w-full no-scrollbar"
                                style={{ maxHeight: 500, overflowY: 'auto' }}
                            >
                                {loadingComments && <div>Carregando comentários...</div>}
                                {commentsError && <div className="text-red-500">{commentsError}</div>}
                                {!loadingComments && comments.length === 0 && <div className="px-2">Nenhum comentário ainda.</div>}
                                {!loadingComments && comments.map((c: any) => renderComment(c))}
                            </section>
                        </main>
                    )}
                </article>
            </div>
        </div>
    );

    return createPortal(modalContent, document.body);
};

export default PostPreviewModal;
