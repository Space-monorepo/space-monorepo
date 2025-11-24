"use client";

import React, { useState, useEffect, useCallback, useRef } from "react";
import { toast } from "react-toastify";
import { useCampaignParticipation } from "@/app/api/src/hooks/post/useCampaignParticipation";
import Link from "next/link";
import {
  Bookmark,
  EllipsisVerticalIcon as OverflowMenuVertical,
  Activity,
} from "lucide-react";
import { fetchPostsByCommunity } from "@/app/api/src/services/post/postService";
import { voteOnPoll } from "@/app/api/src/services/post/postService";
import getTokenFromCookies from "@/app/api/src/controllers/getTokenFromCookies";
import { fetchUserCampaigns } from "@/app/api/src/services/post/fetchUserCampaigns";
import usePostActions from "@/app/api/src/hooks/post/usePostActions";
import { PostResponse, PostsListFeed } from "@/app/api/src/types/posts/Post";
import { translateUserRole } from "@/lib/roleTranslations";
import { translatePostType } from "@/lib/postTypeTranslations";
import { Forum, FaceSatisfied, TextBold, TextItalic, ListNumbered, ListBulleted, CheckmarkFilled, OverflowMenuHorizontal, ArrowUp } from "@carbon/icons-react";
import useReportPost from "@/app/api/src/hooks/post/useReportPost";
import { getRelativeTime } from "@/lib/relativeTime";
import { API_URL } from "@/config";
import getRoleBadgeClasses from "@/components/badges/users/RoleBadgesClasses";
import getCheckmarkColorClass from "@/components/badges/users/CheckmarkColorClasses";
import PostPreviewModal from "@/components/modals/PostPreviewModal";
import { confirmComplaint } from "@/app/api/src/services/post/postService";

// CommentsSection como componente interno
interface Comment {
  id: string;
  user?: {
    name?: string;
    profile_picture?: string;
    profile_image_url?: string;
    member_role?: string;
  };
  member?: {
    name?: string;
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

function CommentsSection({ communityId, postId }: { communityId: string; postId: string }) {
  const { listComments, addComment, replyComment, likeComment, unlikeComment } = usePostActions();
  const [likedComments, setLikedComments] = React.useState<{ [key: string]: boolean }>({});
  const [comments, setComments] = React.useState<Comment[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [commentInput, setCommentInput] = React.useState('');
  const [replyingTo, setReplyingTo] = React.useState<string | null>(null);
  const [replyInput, setReplyInput] = React.useState<{ [key: string]: string }>({});

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
      const data = await listComments(communityId, postId);
      const items = data.items || [];
      setComments(buildCommentsTree(items));
      // Atualiza o estado de likes dos comentários (simples, só para UX, não busca likes do usuário)
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

  React.useEffect(() => {
    fetchComments();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [communityId, postId]);

  const handleAddComment = async () => {
    if (!commentInput.trim()) return;
    try {
      await addComment(communityId, postId, commentInput);
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
      await replyComment(communityId, postId, parentId, content);
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
        return { ...comment, likes_count: Math.max(0, (comment.likes_count || 0) + increment) };
      }
      // Atualiza filhos e replies recursivamente
      let children = comment.children ? updateCommentLikes(comment.children, commentId, increment) : undefined;
      let replies = comment.replies ? updateCommentLikes(comment.replies, commentId, increment) : undefined;
      return { ...comment, children, replies };
    });
  }

  // Like/Unlike comentário (agora atualiza recursivamente)
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

  const renderComment = (comment: Comment, isChild = false) => {
    // API retorna 'member' em vez de 'user'
    const userObj = comment.member || comment.user;

    // Nome do usuário
    const displayName = userObj?.name ||
      (userObj as any)?.username ||
      (userObj as any)?.full_name ||
      'Usuário';

    // Role do membro
    const memberRole = userObj?.member_role ||
      (userObj as any)?.role;

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
  };

  // Função para contar todos os comentários recursivamente
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

  const totalComments = countAllComments(comments);

  return (
    <>
      <main className="flex flex-col shrink-0 gap-8 items-start p-4 bg-white rounded border-solid border-[0.5px] border-stone-300 h-[907px] w-[680px] max-md:p-3 max-md:w-full max-md:max-w-[680px] max-sm:gap-6 max-sm:p-2 max-sm:w-full">
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
    </>
  );
}

type PostDisplay = PostResponse & {
  author: string;
  avatar: string;
  role: string;
  location: string;
  type: string;
  time: string;
  image: string;
  likes: number;
  comments: number;
  shares: number;
  liked: boolean;
  username?: string;
  alreadyParticipating?: boolean;
  userVotedOptionId?: string; // id da opção que o usuário votou
  confirmations_count?: number;
};

export default function PostList() {
  const [allPosts, setAllPosts] = useState<PostDisplay[]>([]);
  const [newPosts, setNewPosts] = useState<PostDisplay[]>([]); // Para armazenar posts novos detectados
  const [showNewPostsBanner, setShowNewPostsBanner] = useState(false);
  // Estado para menu de opções do post (custom, sem MUI)
  const [openMenuPostId, setOpenMenuPostId] = useState<string | null>(null);
  const { reportPost } = useReportPost();
  const [displayedPosts, setDisplayedPosts] = useState<PostDisplay[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [showNoCommunitiesMessage, setShowNoCommunitiesMessage] = useState(false);
  const [openCommentsPostId, setOpenCommentsPostId] = useState<string | null>(null);
  const [hasMorePosts, setHasMorePosts] = useState(true);
  const [currentPage, setCurrentPage] = useState(0);
  const postsPerPage = 3;
  const observerRef = useRef<IntersectionObserver | null>(null);
  const loadingRef = useRef<HTMLDivElement>(null);

  const {
    likePost,
    unlikePost,
    addComment,
    sharePost,
  } = usePostActions();

  const { participating, loading: loadingParticipation, checkParticipation, participate } = useCampaignParticipation();

  const [isPostPreviewOpen, setIsPostPreviewOpen] = useState(false);
  const [postPreviewData, setPostPreviewData] = useState<any>(null);


  // Função para buscar posts do backend (usada tanto para inicial quanto para atualização)
  const fetchPosts = async () => {
    const token = getTokenFromCookies();
    if (!token) {
      setError(new Error("Usuário não autenticado."));
      setLoading(false);
      return [];
    }
    try {
      const communityId = "default-community-id";
      const feedData: PostsListFeed = await fetchPostsByCommunity(token, communityId);
      const userCampaigns = await fetchUserCampaigns();
      const userCampaignPostIds = userCampaigns.map((c: any) => c.post?.id).filter(Boolean);
      const currentUserId = token ? JSON.parse(atob(token.split('.')[1])).sub : null;
      const fetchedPosts = feedData.items.map((item: PostResponse): PostDisplay => {
        let alreadyParticipating = false;
        if (translatePostType(item.type_post) === 'Campanha') {
          alreadyParticipating = item.user.id === currentUserId || userCampaignPostIds.includes(item.id);
        }
        // Detecta se o usuário já votou na enquete
        let userVotedOptionId: string | undefined = undefined;
        if (item.poll_options && Array.isArray(item.poll_options)) {
          const votedOption = item.poll_options.find((opt: any) => Array.isArray(opt.votes) && opt.votes.some((v: any) => v.user_id === currentUserId));
          if (votedOption) userVotedOptionId = votedOption.id;
        }
        return {
          ...item,
          author: item.user.name,
          username: item.user.username || item.user.id,
          avatar: item.user.profile_picture || "/no-profile-pic.png",
          role: translateUserRole(item.user.role),
          location: item.community.name,
          type: translatePostType(item.type_post),
          time: getRelativeTime(item.created_at),
          image: item.image_url || "",
          likes: item.likes_count,
          comments: item.comments_count,
          shares: item.report_count,
          liked: false,
          alreadyParticipating,
          userVotedOptionId,
          confirmations_count: translatePostType(item.type_post) === 'Denúncia' && typeof (item as any).confirmations_count === 'number' ? (item as any).confirmations_count : 0,
        };
      });
      return fetchedPosts;
    } catch (err) {
      setError(err as Error);
      console.error("Erro ao buscar posts:", err);
      return [];
    }
  };

  // Carrega posts iniciais
  const loadInitialPosts = async () => {
    setLoading(true);
    const fetchedPosts = await fetchPosts();
    setAllPosts(fetchedPosts);
    setDisplayedPosts(fetchedPosts.slice(0, postsPerPage));
    setCurrentPage(1);
    if (fetchedPosts.length <= postsPerPage) setHasMorePosts(false);
    if (fetchedPosts.length === 0) setShowNoCommunitiesMessage(true);
    setLoading(false);
  };

  // Atualização periódica: busca novos posts a cada 5s
  useEffect(() => {
    const interval = setInterval(async () => {
      const fetchedPosts = await fetchPosts();
      if (fetchedPosts.length > 0 && allPosts.length > 0) {
        // Verifica se há posts novos (comparando IDs)
        const currentIds = new Set(allPosts.map(p => p.id));
        const onlyNew = fetchedPosts.filter(p => !currentIds.has(p.id));
        if (onlyNew.length > 0) {
          setNewPosts(onlyNew);
          setShowNewPostsBanner(true);
        }
      }
    }, 5000);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [allPosts]);

  // Função para carregar mais posts (scroll infinito)
  const loadMorePosts = useCallback(async () => {
    if (loadingMore || !hasMorePosts) return;
    setLoadingMore(true);
    await new Promise(resolve => setTimeout(resolve, 500));
    const startIndex = currentPage * postsPerPage;
    const endIndex = startIndex + postsPerPage;
    const morePosts = allPosts.slice(startIndex, endIndex);
    if (morePosts.length > 0) {
      setDisplayedPosts(prev => [...prev, ...morePosts]);
      setCurrentPage(prev => prev + 1);
      if (endIndex >= allPosts.length) setHasMorePosts(false);
    } else {
      setHasMorePosts(false);
    }
    setLoadingMore(false);
  }, [loadingMore, hasMorePosts, currentPage, allPosts]);

  // Configurar Intersection Observer para scroll infinito
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMorePosts && !loadingMore) {
          loadMorePosts();
        }
      },
      { threshold: 0.1 }
    );

    if (loadingRef.current) {
      observer.observe(loadingRef.current);
    }

    observerRef.current = observer;

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [loadMorePosts, hasMorePosts, loadingMore]);

  useEffect(() => {
    loadInitialPosts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleLike = async (post: PostDisplay) => {
    const communityId = post.community?.id || "default-community-id";
    try {
      if (!post.liked) {
        await likePost(communityId, post.id);
        setDisplayedPosts(posts => posts.map((p) =>
          p.id === post.id ? { ...p, likes: p.likes + 1, liked: true } : p
        ));
      } else {
        await unlikePost(communityId, post.id);
        setDisplayedPosts(posts => posts.map((p) =>
          p.id === post.id ? { ...p, likes: Math.max(0, p.likes - 1), liked: false } : p
        ));
      }
    } catch (err) {
      // Tratar erro se necessário
    }
  };

  const handleComment = (post: PostDisplay) => {
    setOpenCommentsPostId((prev) => (prev === post.id ? null : post.id));
  };

  const handleShare = async (post: PostDisplay) => {
    const communityId = post.community?.id || "default-community-id";
    await sharePost(communityId, post.id);
    // Quando implementar no backend, incremente shares
    // setDisplayedPosts(posts => posts.map((p) =>
    //   p.id === post.id ? { ...p, shares: p.shares + 1 } : p
    // ));
  };

  // Confirmar problema em denúncia
  const handleConfirmComplaint = async (post: PostDisplay) => {
    try {
      const token = getTokenFromCookies();
      await confirmComplaint(post.community?.id || "default-community-id", post.id, token ?? undefined);
      setDisplayedPosts((prev: PostDisplay[]) => prev.map((p: PostDisplay) => p.id === post.id ? { ...p, confirmations_count: (p.confirmations_count ?? 0) + 1 } : p));
      toast.success('Confirmação registrada!');
    } catch (err) {
      toast.error('Erro ao confirmar problema');
    }
  };

  // Votar em opção da enquete
  const handleVotePoll = async (post: PostDisplay, optionId: string) => {
    const token = getTokenFromCookies();
    const communityId = post.community?.id || 'default-community-id';

    // Se clicar na opção que já votou, retira o voto
    if (post.userVotedOptionId === optionId) {
      await handleUnvotePoll(post);
      return;
    }

    // Aplicação otimista: atualiza imediatamente as contagens locais para animação
    const previousAllPosts = allPosts.slice();
    const previousDisplayed = displayedPosts.slice();
    const optimisticOptions = Array.isArray(post.poll_options) ? post.poll_options.map((o: any) => ({ ...o })) : [];
    const prevVoted = post.userVotedOptionId;
    if (optimisticOptions.length > 0) {
      // Se usuário já tinha votado em outra opção, decrementa essa opção
      if (prevVoted && prevVoted !== optionId) {
        const prevOpt = optimisticOptions.find((o: any) => o.id === prevVoted);
        if (prevOpt) prevOpt.votes_count = Math.max(0, (prevOpt.votes_count || 0) - 1);
      }
      // Incrementa a opção clicada
      const clicked = optimisticOptions.find((o: any) => o.id === optionId);
      if (clicked) clicked.votes_count = (clicked.votes_count || 0) + 1;
    }

    // Atualiza estados localmente para mostrar animação/contagem imediatamente
    setAllPosts(prev => prev.map(p => p.id === post.id ? { ...p, poll_options: optimisticOptions, userVotedOptionId: optionId } as any : p));
    setDisplayedPosts(prev => prev.map(p => p.id === post.id ? { ...p, poll_options: optimisticOptions, userVotedOptionId: optionId } as any : p));
    if (postPreviewData && postPreviewData.id === post.id) {
      setPostPreviewData((prev: any) => ({ ...prev, poll_options: optimisticOptions, userVotedOptionId: optionId }));
    }

    try {
      const response = await voteOnPoll(communityId, optionId, token ?? undefined);
      if (response?.alreadyVoted) {
        toast.info('Você já votou nessa opção!');
        // backend diz que já votou, reverte otimista para o estado anterior
        setAllPosts(previousAllPosts);
        setDisplayedPosts(previousDisplayed);
        return;
      }
      // Atualiza contagem de votos usando os dados mais recentes do backend
      const updatedOptions = response?.post?.poll_options ?? response?.options ?? [];
      const updatedQuestion = response?.question ?? response?.post?.poll_question ?? post.poll_question;

      // Se o backend retornar opções, atualiza contagens mas preserva a ordem
      // das opções otimistas (optimisticOptions) para evitar reordenações visuais.
      let finalOptions: any[] = optimisticOptions.slice();
      if (Array.isArray(updatedOptions) && updatedOptions.length > 0) {
        if (optimisticOptions.length > 0) {
          const updatedMap: { [key: string]: any } = {};
          updatedOptions.forEach((o: any) => { updatedMap[o.id] = o; });
          // Mantém a ordem das opções otimistas, substituindo dados por aqueles retornados
          finalOptions = optimisticOptions.map((o: any) => updatedMap[o.id] ?? o);
          // Se backend trouxe novas opções que não existiam antes, anexá-las ao final
          updatedOptions.forEach((o: any) => {
            if (!finalOptions.some((f: any) => f.id === o.id)) finalOptions.push(o);
          });
        } else {
          finalOptions = updatedOptions.slice();
        }
      }

      let userVotedOptionId: string | undefined = undefined;
      if (finalOptions && Array.isArray(finalOptions)) {
        const currentUserId = token ? JSON.parse(atob(token.split('.')[1])).sub : null;
        const votedOption = finalOptions.find((opt: any) => Array.isArray(opt.votes) && opt.votes.some((v: any) => v.user_id === currentUserId));
        if (votedOption) userVotedOptionId = votedOption.id;
      }

      // Se ainda não encontrou o voto, assume que votou na opção clicada
      if (!userVotedOptionId && finalOptions) {
        userVotedOptionId = optionId;
      }

      setAllPosts(prev => prev.map(p => p.id === post.id ? { ...p, poll_options: finalOptions, poll_question: updatedQuestion, userVotedOptionId } as any : p));
      setDisplayedPosts(prev => prev.map(p => p.id === post.id ? { ...p, poll_options: finalOptions, poll_question: updatedQuestion, userVotedOptionId } as any : p));
      if (postPreviewData && postPreviewData.id === post.id) {
        setPostPreviewData((prev: any) => ({ ...prev, poll_options: finalOptions, poll_question: updatedQuestion, userVotedOptionId }));
      }
      // Recarrega posts do backend para garantir consistência (quando backend não retorna opções atualizadas)
      try {
        const refreshed = await fetchPosts();
        // Ao recarregar, preservamos a ordem das opções da enquete que acabamos de
        // calcular (`finalOptions`) para evitar reordenação visual causada pelo backend.
        const merged = refreshed.map((p: any) => {
          if (p.id === post.id) {
            return { ...p, poll_options: finalOptions, poll_question: updatedQuestion, userVotedOptionId };
          }
          return p;
        });
        setAllPosts(merged);
        // mantém a mesma quantidade de posts exibidos atualmente
        const shownCount = Math.max(displayedPosts.length, postsPerPage);
        setDisplayedPosts(merged.slice(0, shownCount));
        setHasMorePosts(!(merged.length <= shownCount));
      } catch (err) {
        // se falhar no refresh, continuamos com o estado otimista já aplicado
        console.warn('Falha ao recarregar posts após voto:', err);
      }
      toast.success('Voto contabilizado');
    } catch (err: any) {
      console.error('Erro ao votar na enquete', err);
      // Reverte otimista em caso de erro
      setAllPosts(previousAllPosts);
      setDisplayedPosts(previousDisplayed);
      if (postPreviewData && postPreviewData.id === post.id) {
        setPostPreviewData((prev: any) => ({ ...prev, poll_options: post.poll_options, userVotedOptionId: post.userVotedOptionId }));
      }
      toast.error(err?.message || 'Erro ao votar na enquete');
    }
  };

  // Função para retirar o voto
  const handleUnvotePoll = async (post: PostDisplay) => {
    if (!post.userVotedOptionId) return;
    const token = getTokenFromCookies();
    const communityId = post.community?.id || 'default-community-id';
    // Otimista: decrementa imediatamente a opção votada localmente
    const previousAllPostsUn = allPosts.slice();
    const previousDisplayedUn = displayedPosts.slice();
    const optimisticOptionsUn = Array.isArray(post.poll_options) ? post.poll_options.map((o: any) => ({ ...o })) : [];
    const votedId = post.userVotedOptionId;
    if (optimisticOptionsUn.length > 0 && votedId) {
      const opt = optimisticOptionsUn.find((o: any) => o.id === votedId);
      if (opt) opt.votes_count = Math.max(0, (opt.votes_count || 0) - 1);
    }
    setAllPosts(prev => prev.map(p => p.id === post.id ? { ...p, poll_options: optimisticOptionsUn, userVotedOptionId: undefined } as any : p));
    setDisplayedPosts(prev => prev.map(p => p.id === post.id ? { ...p, poll_options: optimisticOptionsUn, userVotedOptionId: undefined } as any : p));
    if (postPreviewData && postPreviewData.id === post.id) {
      setPostPreviewData((prev: any) => ({ ...prev, poll_options: optimisticOptionsUn, userVotedOptionId: undefined }));
    }

    try {
      // Para retirar o voto, basta chamar voteOnPoll novamente na opção votada, e o backend deve tratar como unvote
      const response = await voteOnPoll(communityId, post.userVotedOptionId, token ?? undefined);
      // Atualiza contagem de votos usando os dados mais recentes do backend
      const updatedOptions = response?.post?.poll_options ?? response?.options ?? [];
      const updatedQuestion = response?.question ?? response?.post?.poll_question ?? post.poll_question;

      // Preserva ordem das opções otimistas (optimisticOptionsUn) como em handleVotePoll
      let finalOptions: any[] = optimisticOptionsUn.slice();
      if (Array.isArray(updatedOptions) && updatedOptions.length > 0) {
        if (optimisticOptionsUn.length > 0) {
          const updatedMap: { [key: string]: any } = {};
          updatedOptions.forEach((o: any) => { updatedMap[o.id] = o; });
          finalOptions = optimisticOptionsUn.map((o: any) => updatedMap[o.id] ?? o);
          updatedOptions.forEach((o: any) => {
            if (!finalOptions.some((f: any) => f.id === o.id)) finalOptions.push(o);
          });
        } else {
          finalOptions = updatedOptions.slice();
        }
      }

      setAllPosts(prev => prev.map(p => p.id === post.id ? { ...p, poll_options: finalOptions, poll_question: updatedQuestion, userVotedOptionId: undefined } as any : p));
      setDisplayedPosts(prev => prev.map(p => p.id === post.id ? { ...p, poll_options: finalOptions, poll_question: updatedQuestion, userVotedOptionId: undefined } as any : p));
      if (postPreviewData && postPreviewData.id === post.id) {
        setPostPreviewData((prev: any) => ({ ...prev, poll_options: finalOptions, poll_question: updatedQuestion, userVotedOptionId: undefined }));
      }
      // Recarrega posts do backend para garantir consistência após remover voto
      try {
        const refreshed = await fetchPosts();
        // Preserva a ordem das opções já calculada em `finalOptions` ao mesclar
        const merged = refreshed.map((p: any) => {
          if (p.id === post.id) {
            return { ...p, poll_options: finalOptions, poll_question: updatedQuestion, userVotedOptionId: undefined };
          }
          return p;
        });
        setAllPosts(merged);
        const shownCount = Math.max(displayedPosts.length, postsPerPage);
        setDisplayedPosts(merged.slice(0, shownCount));
        setHasMorePosts(!(merged.length <= shownCount));
      } catch (err) {
        console.warn('Falha ao recarregar posts após remover voto:', err);
      }
      toast.success('Voto removido');
    } catch (err: any) {
      console.error('Erro ao remover voto', err);
      // Reverte otimista em caso de erro
      setAllPosts(previousAllPostsUn);
      setDisplayedPosts(previousDisplayedUn);
      if (postPreviewData && postPreviewData.id === post.id) {
        setPostPreviewData((prev: any) => ({ ...prev, poll_options: post.poll_options, userVotedOptionId: post.userVotedOptionId }));
      }
      toast.error(err?.message || 'Erro ao remover voto');
    }
  };

  // Participar da campanha
  const handleParticipateCampaign = async (post: PostDisplay) => {
    try {
      await participate(post.community?.id || "default-community-id", post.id);
      setDisplayedPosts((prev) => prev.map((p) => p.id === post.id ? { ...p, alreadyParticipating: true } : p));
      toast.success('Você agora faz parte da campanha!');
    } catch (err) {
      toast.error('Erro ao participar da campanha');
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col justify-center items-center h-full w-full pr-72 mt-62 text-center">
        Carregando posts...
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col justify-center items-center h-full w-full pr-72 mt-62 text-center text-red-500">
        Erro ao carregar posts: {error.message}
      </div>
    );
  }

  if (showNoCommunitiesMessage) {
    return (
      <div className="flex flex-col justify-center items-center h-full w-full pr-72 mt-62 text-center">
        <p className="mb-4 text-lg">
          Você ainda não participa de nenhuma comunidade.
        </p>
        <p className="mb-4">
          Peça para um administrador convidá-lo para a comunidade.
        </p>
        <Link href="/notifications" legacyBehavior>
          <a className="px-4 py-2 bg-black text-white hover:bg-gray-800">
            Ver notificações
          </a>
        </Link>
      </div>
    );
  }

  return (
    <div className="flex-1 p-4 overflow-auto pr-72 flex justify-center">
      <main className="overflow-hidden max-w-[680px] w-full space-y-6">
        {/* Banner de novos posts fixo na tela */}
        {showNewPostsBanner && newPosts.length > 0 && (
          <div
            style={{
              position: 'fixed',
              top: 70,
              left: '50%',
              transform: 'translateX(-50%)',
              zIndex: 0,
              minWidth: 220,
              maxWidth: 360,
            }}
            className="flex justify-center animate-fade-in"
          >
            <button
              className="px-4 py-2 bg-black text-white rounded-xl shadow-lg hover:bg-gray-900 transition-colors border-gray-200 cursor-pointer"
              onClick={() => {
                setAllPosts(prev => [...newPosts, ...prev]);
                setDisplayedPosts(prev => [...newPosts, ...prev]);
                setShowNewPostsBanner(false);
                setNewPosts([]);
              }}
            >
              {newPosts.length === 1 ? '1 publicado' : `${newPosts.length} publicados`}
            </button>
          </div>
        )}
        {displayedPosts.map((post) => (
          <React.Fragment key={post.id}>
            <article
              className="flex flex-col justify-center px-6 py-4 w-full bg-white rounded border-solid shadow-sm border-[0.5px] border-stone-300 max-md:px-5 max-md:max-w-full"
            >
              <div className="w-full max-w-[632px] max-md:max-w-full">
                <div className="w-full max-md:max-w-full">
                  <header className="flex flex-wrap gap-10 justify-between items-start w-full max-md:max-w-full">
                    <div className="flex items-start min-w-60">
                      <div className="w-11 h-11 rounded-[32px] overflow-hidden shrink-0 flex items-center justify-center bg-neutral-200">
                        <img
                          src={post.avatar || "/placeholder.svg"}
                          alt={`${post.author} avatar`}
                          className="object-cover w-full h-full"
                        />
                      </div>
                      <div className="flex flex-col min-w-60 w-[342px]">
                        <div className="flex gap-2 items-center w-full h-[23px]">
                          <div className="flex overflow-hidden gap-2.5 justify-center items-center self-stretch px-3 my-auto">
                            <Link
                              href={`/profile/${post.username || post.user.id}`}
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
                              {post.type}
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
                        <Bookmark
                          className={`h-4 w-4 text-gray-500`}
                        />
                      </button>
                      <div className="relative">
                        <button
                          className="p-1 hover:bg-gray-100 rounded-full cursor-pointer transition-colors"
                          onClick={(e) => {
                            e.stopPropagation();
                            setOpenMenuPostId(openMenuPostId === post.id ? null : post.id);
                          }}
                          aria-label="Mais opções"
                        >
                          <OverflowMenuVertical className="h-4 w-4 text-gray-500" />
                        </button>
                        {openMenuPostId === post.id && (
                          <div
                            className="absolute right-0 z-20 mt-2 w-40 bg-white border border-gray-200 rounded shadow-lg animate-fade-in"
                            tabIndex={-1}
                            onBlur={() => setOpenMenuPostId(null)}
                          >
                            <button
                              className="w-full text-left px-4 py-2 text-sm cursor-pointer text-red-600 hover:bg-gray-100 rounded"
                              onClick={async (e) => {
                                e.stopPropagation();
                                setOpenMenuPostId(null);
                                try {
                                  await reportPost(post.community?.id || 'default-community-id', post.id);
                                } catch { }
                              }}
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
                        className="flex gap-2.5 items-center text-xl font-bold leading-relaxed min-w-60 px-0 w-0 flex-1 cursor-pointer"
                        style={{ wordBreak: 'break-word' }}
                        onClick={() => {
                          setPostPreviewData({
                            id: post.id,
                            title: post.title,
                            content: post.content,
                            author: post.author,
                            avatar: post.avatar,
                            role: post.role,
                            location: post.location,
                            type: post.type,
                            time: post.time,
                            imageUrl: post.image,
                            likes: post.likes,
                            comments: post.comments,
                            shares: post.shares,
                            community: post.community,
                            liked: post.liked,
                            alreadyParticipating: post.alreadyParticipating,
                            userVotedOptionId: post.userVotedOptionId,
                            confirmations_count: post.confirmations_count,
                            status_complaint: (post as any).status_complaint,
                            level_complaint: (post as any).level_complaint,
                            tags: (post as any).tags,
                            username: post.username,
                            user: {
                              id: post.user.id,
                              profile_picture: post.user.profile_picture
                            },
                            poll_question: post.poll_question,
                            poll_options: post.poll_options
                          });
                          setIsPostPreviewOpen(true);
                        }}
                      >
                        <h2
                          className="text-neutral-800 px-0 font-georgia font-bold break-words w-full max-w-full"
                          style={{ fontFamily: 'Georgia, serif', fontWeight: 'bold', wordBreak: 'break-word', overflowWrap: 'break-word', whiteSpace: 'pre-line' }}
                        >
                          {post.title}
                        </h2>
                      </div>
                      <div className="flex gap-2 items-center px-3 py-1 my-auto text-sm leading-none text-justify whitespace-nowrap rounded-sm flex-shrink-0">
                        <div className="self-stretch my-auto text-neutral-800">
                          {post.likes + post.comments + post.shares}
                        </div>
                        <Activity className="h-4 w-4 text-gray-500" />
                      </div>
                    </div>

                    {post.content && (
                      <div
                        className="mt-4 text-sm leading-5 text-justify text-neutral-800 max-md:max-w-full whitespace-pre-line font-regular break-words w-full max-w-full cursor-pointer"
                        style={{ wordBreak: 'break-word', overflowWrap: 'break-word', whiteSpace: 'pre-line' }}
                        onClick={() => {
                          setPostPreviewData({
                            id: post.id,
                            title: post.title,
                            content: post.content,
                            author: post.author,
                            avatar: post.avatar,
                            role: post.role,
                            location: post.location,
                            type: post.type,
                            time: post.time,
                            imageUrl: post.image,
                            likes: post.likes,
                            comments: post.comments,
                            shares: post.shares,
                            community: post.community,
                            liked: post.liked,
                            alreadyParticipating: post.alreadyParticipating,
                            userVotedOptionId: post.userVotedOptionId,
                            confirmations_count: post.confirmations_count,
                            status_complaint: (post as any).status_complaint,
                            level_complaint: (post as any).level_complaint,
                            tags: (post as any).tags,
                            username: post.username,
                            user: {
                              id: post.user.id,
                              profile_picture: post.user.profile_picture
                            },
                            poll_question: post.poll_question,
                            poll_options: post.poll_options
                          });
                          setIsPostPreviewOpen(true);
                        }}
                      >
                        {post.content}
                      </div>
                    )}

                    {post.image && (
                      <img
                        src={post.image}
                        alt="Post content"
                        className="object-contain mt-4 w-full rounded aspect-[2.26] max-md:max-w-full"
                      />
                    )}

                    {/* Opções de Enquete */}
                    {post.type === 'Enquete' && Array.isArray(post.poll_options) && post.poll_options.length > 0 && (
                      <div className="mt-6 w-full">
                        {post.poll_question && (
                          <h3 className="text-base font-semibold text-neutral-800 mb-6">
                            {post.poll_question}
                          </h3>
                        )}
                        {(() => {
                          const totalVotes = Array.isArray(post.poll_options) ? post.poll_options.reduce((sum, opt) => sum + opt.votes_count, 0) : 0;
                          return (post.poll_options ?? []).map((option) => {
                            const percent = totalVotes > 0 ? Math.round((option.votes_count / totalVotes) * 100) : 0;
                            const isUserVote = post.userVotedOptionId === option.id;
                            return (
                              <div
                                key={`${option.id}-${option.votes_count}`}
                                className={`mb-4 cursor-pointer hover:opacity-80 transition-opacity`}
                              >
                                <button
                                  className={`w-full text-left bg-transparent border-none outline-none p-0 m-0 cursor-pointer`}
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleVotePoll(post, option.id);
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
                                        style={{ width: `${percent}%`, minWidth: '8px', transition: 'width 300ms ease' }}
                                      />
                                    </div>
                                  </div>
                                </button>
                              </div>
                            );
                          });
                        })()}
                      </div>
                    )}

                    {/* Botão Participar da Campanha */}
                    {post.type === 'Campanha' && (
                      <button
                        className={`mt-4 w-full py-2 px-4 text-left font-regular transition-colors cursor-pointer ${post.alreadyParticipating || participating[post.id] ? 'bg-neutral-200 text-neutral-700 cursor-not-allowed' : 'bg-neutral-900 text-white hover:bg-neutral-800'}`}
                        onClick={(e) => {
                          e.stopPropagation();
                          if (!post.alreadyParticipating && !participating[post.id]) handleParticipateCampaign(post);
                        }}
                        disabled={post.alreadyParticipating || participating[post.id]}
                      >
                        {post.alreadyParticipating || participating[post.id] ? 'Já participa da campanha' : 'Participar da Campanha'}
                      </button>
                    )}

                    {/* Botão Confirmar problema para Denúncia */}
                    {post.type === 'Denúncia' && (
                      <button
                        className={`mt-4 w-full py-2 px-4 text-left font-regular transition-colors ${(post.confirmations_count ?? 0) > 0 ? 'bg-neutral-200 text-neutral-700 cursor-not-allowed' : 'bg-neutral-900 text-white hover:bg-neutral-800'}`}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleConfirmComplaint(post);
                        }}
                        disabled={(post.confirmations_count ?? 0) > 0}
                      >
                        {(post.confirmations_count ?? 0) > 0 ? (
                          'Problema confirmado'
                        ) : (
                          'Confirmar problema'
                        )}
                      </button>
                    )}
                  </div>
                </div>

                <div className="flex justify-between items-center mt-10 w-full text-xs font-medium leading-none text-neutral-500 max-md:max-w-full">
                  <div className="flex overflow-hidden gap-8 items-center self-stretch my-auto min-h-5 w-[214px]">
                    <button
                      className="flex overflow-hidden gap-2 items-center self-stretch my-auto text-justify whitespace-nowrap cursor-pointer"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleLike(post);
                      }}
                      title="Curtir"
                    >
                      <ArrowUp className="h-4 w-4 text-gray-500" />
                      <div className="self-stretch my-auto text-neutral-500">
                        {post.likes}
                      </div>
                    </button>
                    <button
                      className={`flex overflow-hidden gap-2 items-center self-stretch my-auto text-justify whitespace-nowrap transition-colors px-3 py-1 cursor-pointer ${openCommentsPostId === post.id ? 'bg-neutral-200' : ''}`}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleComment(post);
                      }}
                      title="Comentar"
                    >
                      <Forum className={`h-4 w-4 ${openCommentsPostId === post.id ? 'text-black-300' : 'text-gray-500'}`} />
                      <div className={`self-stretch my-auto ${openCommentsPostId === post.id ? 'text-black-600' : 'text-neutral-500'}`}>
                        {post.comments}
                      </div>
                    </button>
                    <button
                      className="flex overflow-hidden gap-2 items-center self-stretch my-auto text-teal-700"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleShare(post);
                      }}
                      title="Compartilhar"
                    >
                      <Activity className="h-4 w-4 text-teal-700" />
                      <div className="self-stretch my-auto">
                        {post.shares}
                      </div>
                    </button>
                  </div>
                </div>
              </div>
            </article>
            {openCommentsPostId === post.id && (
              <div className="flex justify-center w-full -mt-6">
                <CommentsSection communityId={post.community?.id || "default-community-id"} postId={post.id} />
              </div>
            )}
          </React.Fragment>
        ))}

        {/* Loading indicator para scroll infinito */}
        {hasMorePosts && (
          <div
            ref={loadingRef}
            className="flex justify-center items-center py-8"
          >
            {loadingMore ? (
              <div className="flex items-center gap-2 text-neutral-500">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-neutral-500"></div>
                <span>Carregando mais posts...</span>
              </div>
            ) : (
              <div className="h-8"></div> // Espaçador invisível para trigger do observer
            )}
          </div>
        )}

        {/* Mensagem quando não há mais posts
        {!hasMorePosts && displayedPosts.length > 0 && (
          <div className="flex justify-center items-center py-8 text-neutral-500">
            <span>Você chegou ao final dos posts</span>
          </div>
        )} */}
        <PostPreviewModal
          post={postPreviewData}
          isOpen={isPostPreviewOpen}
          onClose={() => setIsPostPreviewOpen(false)}
        />
      </main>
    </div>
  );
}
