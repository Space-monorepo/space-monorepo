"use client";

import React, { useState, useEffect, useCallback, useRef } from "react";
import { toast } from "react-toastify";
import { useCampaignParticipation } from "@/app/api/src/hooks/post/useCampaignParticipation";
import Link from "next/link";
import {
  EllipsisVerticalIcon as OverflowMenuVertical,
  Activity,
  Loader2,
} from "lucide-react";
import {
  fetchPostsByCommunity,
  voteOnPoll,
  unvoteOnPoll,
} from "@/app/api/src/services/post/postService";
import getTokenFromCookies from "@/app/api/src/controllers/getTokenFromCookies";
import { fetchUserCampaigns } from "@/app/api/src/services/post/fetchUserCampaigns";
import { fetchUserCommunities } from "@/app/api/src/services/community/communityService";
import usePostActions from "@/app/api/src/hooks/post/usePostActions";
import { PostResponse, PostsListFeed } from "@/app/api/src/types/posts/Post";
import { translateUserRole } from "@/lib/roleTranslations";
import { translatePostType } from "@/lib/postTypeTranslations";
import {
  Forum,
  FaceSatisfied,
  TextBold,
  TextItalic,
  ListNumbered,
  ListBulleted,
  CheckmarkFilled,
  OverflowMenuHorizontal,
  ArrowUp,
} from "@carbon/icons-react";
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

function CommentsSection({
  communityId,
  postId,
  refreshSignal,
}: {
  communityId: string;
  postId: string;
  refreshSignal?: number;
}) {
  const {
    listComments,
    addComment,
    replyComment,
    likeComment,
    unlikeComment,
    reportMember,
  } = usePostActions();
  const [likedComments, setLikedComments] = React.useState<{
    [key: string]: boolean;
  }>({});
  const [comments, setComments] = React.useState<Comment[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [commentInput, setCommentInput] = React.useState("");
  const [replyingTo, setReplyingTo] = React.useState<string | null>(null);
  const [replyInput, setReplyInput] = React.useState<{ [key: string]: string }>(
    {},
  );
  const [commentMenuOpen, setCommentMenuOpen] = React.useState<string | null>(
    null,
  );

  function buildCommentsTree(flatComments: Comment[]): Comment[] {
    const commentsMap: { [key: string]: Comment & { children: Comment[] } } =
      {};
    const roots: (Comment & { children: Comment[] })[] = [];
    flatComments.forEach((comment) => {
      commentsMap[comment.id] = { ...comment, children: [] };
    });
    flatComments.forEach((comment) => {
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
      setError("Erro ao carregar comentários");
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    fetchComments();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [communityId, postId]);

  React.useEffect(() => {
    setCommentMenuOpen(null);
  }, [communityId, postId]);

  // Quando o sinal de refresh mudar (vindo do polling global), refazemos os comentários
  React.useEffect(() => {
    if (typeof refreshSignal !== "undefined") {
      fetchComments();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [refreshSignal]);

  const handleAddComment = async () => {
    if (!commentInput.trim()) return;
    try {
      await addComment(communityId, postId, commentInput);
      setCommentInput("");
      fetchComments();
    } catch (err) {
      setError("Erro ao comentar");
    }
  };

  const handleReply = async (parentId: string) => {
    const content = replyInput[parentId];
    if (!content?.trim()) return;
    try {
      await replyComment(communityId, postId, parentId, content);
      setReplyInput((prev) => ({ ...prev, [parentId]: "" }));
      setReplyingTo(null);
      fetchComments();
    } catch (err) {
      setError("Erro ao responder comentário");
    }
  };

  // Atualiza likes recursivamente na árvore de comentários
  function updateCommentLikes(
    comments: Comment[],
    commentId: string,
    increment: number,
  ): Comment[] {
    return comments.map((comment) => {
      if (comment.id === commentId) {
        return {
          ...comment,
          likes_count: Math.max(0, (comment.likes_count || 0) + increment),
        };
      }
      // Atualiza filhos e replies recursivamente
      let children = comment.children
        ? updateCommentLikes(comment.children, commentId, increment)
        : undefined;
      let replies = comment.replies
        ? updateCommentLikes(comment.replies, commentId, increment)
        : undefined;
      return { ...comment, children, replies };
    });
  }

  // Like/Unlike comentário (agora atualiza recursivamente)
  const handleLikeComment = async (comment: Comment) => {
    try {
      if (!likedComments[comment.id]) {
        await likeComment(communityId, comment.id);
        setComments((prev) => updateCommentLikes(prev, comment.id, 1));
        setLikedComments((prev) => ({ ...prev, [comment.id]: true }));
      } else {
        await unlikeComment(communityId, comment.id);
        setComments((prev) => updateCommentLikes(prev, comment.id, -1));
        setLikedComments((prev) => ({ ...prev, [comment.id]: false }));
      }
    } catch (err) {
      setError("Erro ao curtir/descurtir comentário");
    }
  };

  const handleReportMember = async (comment: Comment) => {
    const reportedMemberId =
      ((comment.member as any)?.id) ?? ((comment.user as any)?.id) ?? null;
    if (!reportedMemberId) {
      toast.error("Não foi possível identificar o membro deste comentário.");
      return;
    }
    try {
      await reportMember(
        communityId,
        reportedMemberId,
        "other",
        `Comentário reportado: ${comment.content}`.slice(0, 140),
      );
      toast.success("Denúncia enviada.");
    } catch (err) {
      console.error(err);
      toast.error("Erro ao reportar o membro.");
    } finally {
      setCommentMenuOpen(null);
    }
  };

  const renderComment = (comment: Comment, isChild = false) => {
    // API retorna 'member' em vez de 'user'
    const userObj = comment.member || comment.user;

    // Nome do usuário
    const displayName =
      userObj?.name ||
      (userObj as any)?.username ||
      (userObj as any)?.full_name ||
      "Usuário";

    // Role do membro
    const memberRole = userObj?.member_role || (userObj as any)?.role;

    return (
      <div
        key={comment.id}
        className={`${isChild ? "flex flex-wrap items-start self-end mt-6 w-full max-w-[592px]" : "flex flex-wrap justify-between w-full max-[899px]:max-w-full"}`}
      >
        <div className="flex flex-col items-center w-11">
          <img
            src={
              userObj?.profile_image_url ||
              userObj?.profile_picture ||
              "/no-profile-pic.png"
            }
            alt={`${displayName} avatar`}
            className={`object-contain w-11 aspect-square ${isChild ? "rounded-[32px]" : ""}`}
          />
          {!isChild &&
            ((Array.isArray(comment.children) && comment.children.length > 0) ||
              (Array.isArray(comment.replies) &&
                comment.replies.length > 0)) && (
              <div className="flex mt-2 w-px bg-zinc-300 min-h-[78px]" />
            )}
        </div>
        <div className="flex-1 shrink basis-0 min-w-0 max-[899px]:max-w-full min-[900px]:min-w-60">
          <div className="flex flex-wrap gap-3 items-center py-3 w-full max-[899px]:max-w-full">
            <div
              className={`flex items-center self-stretch my-auto text-neutral-800 min-w-0 w-full min-[900px]:min-w-60 ${isChild ? "min-[900px]:w-[360px]" : "min-[900px]:w-[380px]"}`}
            >
              <div
                className={`self-stretch my-auto min-w-0 w-full min-[900px]:min-w-60 ${isChild ? "min-[900px]:w-[360px]" : "min-[900px]:w-[380px]"}`}
              >
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
                      <div
                        className={`flex gap-2.5 justify-center items-center self-stretch px-3 py-1 my-auto text-xs whitespace-nowrap rounded ${getRoleBadgeClasses(memberRole)}`}
                      >
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
            <div className="flex gap-4 items-center self-stretch my-auto w-5 min-h-5 relative">
              <button
                className="p-1 hover:bg-gray-100 rounded-full transition-colors"
                onClick={(e) => {
                  e.stopPropagation();
                  setCommentMenuOpen(
                    commentMenuOpen === comment.id ? null : comment.id,
                  );
                }}
                aria-label="Opções do comentário"
              >
                <OverflowMenuHorizontal className="h-4 w-4 text-gray-500" />
              </button>
              {commentMenuOpen === comment.id && (
                <div className="absolute right-0 top-6 z-20 mt-1 w-44 bg-white border border-gray-200 rounded shadow-lg">
                  <button
                    className="w-full text-left px-4 py-2 text-sm cursor-pointer text-red-600 hover:bg-gray-100"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleReportMember(comment);
                    }}
                  >
                    Reportar membro
                  </button>
                </div>
              )}
            </div>
          </div>
          <div className="px-3 mt-2 w-full max-[899px]:max-w-full">
            <div
              className={`flex ${isChild ? "overflow-hidden " : ""}gap-2.5 items-center w-full text-sm leading-5 text-neutral-800 max-[899px]:max-w-full`}
            >
              <div className="flex-1 shrink self-stretch my-auto basis-0 text-neutral-800 max-[899px]:max-w-full">
                {comment.content}
              </div>
            </div>
            <div
              className={`flex justify-between items-center mt-4 w-full text-xs font-medium leading-none text-justify ${isChild ? "whitespace-nowrap " : ""}text-neutral-500 max-[899px]:max-w-full`}
            >
              <div className="flex overflow-hidden gap-8 items-center self-stretch my-auto min-h-5">
                <div
                  className={`flex overflow-hidden gap-2 items-center self-stretch my-auto ${isChild ? "" : "whitespace-nowrap"}`}
                >
                  <ArrowUp
                    className="object-contain shrink-0 self-stretch my-auto w-3 aspect-square cursor-pointer hover:opacity-70 transition-opacity text-neutral-500"
                    onClick={() => handleLikeComment(comment)}
                    aria-label="Curtir"
                  />
                  <div
                    className={`self-stretch my-auto ${likedComments[comment.id] ? "text-neutral-600" : "text-neutral-500"}`}
                  >
                    {comment.likes_count ?? 0}
                  </div>
                </div>
                <div className="flex overflow-hidden gap-2 items-center self-stretch my-auto">
                  <img
                    src="https://api.builder.io/api/v1/image/assets/367ac41a58454bf7adac62a5f3afc83b/76fc42bedb22beda24433b506515bdee6ba7cab0?placeholderIfAbsent=true"
                    className="object-contain shrink-0 self-stretch my-auto w-4 aspect-square cursor-pointer hover:opacity-70 transition-opacity"
                    onClick={() =>
                      setReplyingTo(
                        replyingTo === comment.id ? null : comment.id,
                      )
                    }
                    alt="Reply"
                  />
                  <div
                    className="self-stretch my-auto text-neutral-500 cursor-pointer hover:text-neutral-700 transition-colors"
                    onClick={() =>
                      setReplyingTo(
                        replyingTo === comment.id ? null : comment.id,
                      )
                    }
                  >
                    {isChild
                      ? "Responder"
                      : `Responder${(Array.isArray(comment.children) && comment.children.length > 0) || (Array.isArray(comment.replies) && comment.replies.length > 0) ? ` (${(comment.children?.length || 0) + (comment.replies?.length || 0)})` : ""}`}
                  </div>
                </div>
              </div>
            </div>
            {replyingTo === comment.id && (
              <div className="flex flex-col gap-2 items-start self-stretch w-full mt-4">
                <div className="flex flex-col items-start self-stretch w-full">
                  <div className="flex flex-col justify-between items-start self-stretch p-4 bg-gray-100 h-[160px] rounded-xs w-full">
                    <textarea
                      className="w-full h-full bg-transparent text-sm leading-6 text-neutral-600 max-[539px]:text-sm resize-none border-none outline-none placeholder:text-neutral-600"
                      rows={2}
                      placeholder="Digite sua resposta..."
                      value={replyInput[comment.id] || ""}
                      onChange={(e) =>
                        setReplyInput((prev) => ({
                          ...prev,
                          [comment.id]: e.target.value,
                        }))
                      }
                      onKeyDown={(e) => {
                        if (e.key === "Enter" && !e.shiftKey) {
                          e.preventDefault();
                          handleReply(comment.id);
                        }
                      }}
                    />
                    <div className="flex flex-row justify-between items-end w-full mt-2">
                      <div className="flex gap-4 items-center max-[539px]:gap-3">
                        <button type="button" aria-label="Adicionar emoji">
                          <FaceSatisfied
                            size={20}
                            className="toolbar-icon text-neutral-500"
                          />
                        </button>
                        <button type="button" aria-label="Negrito">
                          <TextBold
                            size={20}
                            className="toolbar-icon text-neutral-500"
                          />
                        </button>
                        <button type="button" aria-label="Itálico">
                          <TextItalic
                            size={20}
                            className="toolbar-icon text-neutral-500"
                          />
                        </button>
                        <button type="button" aria-label="Lista numerada">
                          <ListNumbered
                            size={20}
                            className="toolbar-icon text-neutral-500"
                          />
                        </button>
                        <button type="button" aria-label="Lista com marcadores">
                          <ListBulleted
                            size={20}
                            className="toolbar-icon text-neutral-500"
                          />
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
          <div className="flex flex-wrap items-start self-end mt-6 w-full max-w-[592px]">
            {comment.children.map((child) => renderComment(child, true))}
          </div>
        )}
        {/* Renderizar replies recursivamente */}
        {Array.isArray(comment.replies) && comment.replies.length > 0 && (
          <div className="flex flex-wrap items-start self-end mb-6 w-full max-w-[592px] min-[900px]:pl-12">
            {comment.replies.map((child) => renderComment(child, true))}
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
      <main className="flex flex-col shrink-0 gap-8 items-start w-full max-w-[680px] p-4 bg-white rounded border-solid border-[0.5px] border-stone-300 max-[899px]:p-3 max-[539px]:gap-6 max-[539px]:p-2">
        {/* Comment Input Section */}
        <div className="flex flex-col gap-2 items-start self-stretch">
          <div className="flex flex-col items-start self-stretch">
            <div className="flex flex-col justify-between items-start self-stretch p-4 bg-gray-100 h-[160px] rounded-xs">
              <textarea
                id="comment-textarea"
                value={commentInput}
                onChange={(e) => setCommentInput(e.target.value)}
                placeholder="Adicione um comentário"
                className="w-full h-full bg-transparent text-sm leading-6 text-neutral-600 max-[539px]:text-sm resize-none border-none outline-none placeholder:text-neutral-600"
                rows={2}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleAddComment();
                  }
                }}
              />
              <div className="flex flex-row justify-between items-end w-full mt-2">
                <div className="flex gap-4 items-center max-[539px]:gap-3">
                  <button type="button" aria-label="Adicionar emoji">
                    <FaceSatisfied
                      size={20}
                      className="toolbar-icon text-neutral-500"
                    />
                  </button>
                  <button type="button" aria-label="Negrito">
                    <TextBold
                      size={20}
                      className="toolbar-icon text-neutral-500"
                    />
                  </button>
                  <button type="button" aria-label="Itálico">
                    <TextItalic
                      size={20}
                      className="toolbar-icon text-neutral-500"
                    />
                  </button>
                  <button type="button" aria-label="Lista numerada">
                    <ListNumbered
                      size={20}
                      className="toolbar-icon text-neutral-500"
                    />
                  </button>
                  <button type="button" aria-label="Lista com marcadores">
                    <ListBulleted
                      size={20}
                      className="toolbar-icon text-neutral-500"
                    />
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
        <header className="flex gap-4 items-center self-stretch px-2 py-0 max-[899px]:gap-3 max-[899px]:px-3 max-[899px]:py-0 max-[539px]:flex-wrap max-[539px]:gap-2 max-[539px]:px-2 max-[539px]:py-0">
          <h2 className="text-base leading-6 text-neutral-800 max-[539px]:text-sm">
            Comentários
          </h2>
          <div className="flex flex-col gap-2.5 justify-center items-center px-2 py-1 rounded-xs bg-neutral-800">
            <span className="self-stretch text-base leading-6 text-zinc-100 max-[539px]:text-sm">
              {totalComments}
            </span>
          </div>
        </header>

        {/* Comments List */}
        <section
          className="flex flex-col p-4 bg-white rounded-sm max-w-[648px] w-full no-scrollbar"
          style={{ maxHeight: 800, overflowY: "auto" }}
        >
          {loading && <div>Carregando comentários...</div>}
          {error && <div className="text-red-500">{error}</div>}
          {!loading && comments.length === 0 && (
            <div className="px-2">Nenhum comentário ainda.</div>
          )}
          {comments.map((comment) => renderComment(comment))}
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
  const [showNoCommunitiesMessage, setShowNoCommunitiesMessage] =
    useState(false);
  const [hasCommunities, setHasCommunities] = useState<boolean | null>(null);
  const [isFeedEmpty, setIsFeedEmpty] = useState(false);
  const [openCommentsPostId, setOpenCommentsPostId] = useState<string | null>(
    null,
  );
  const [hasMorePosts, setHasMorePosts] = useState(true);
  const [currentPage, setCurrentPage] = useState(0);
  const [currentUserId, setCurrentUserId] = useState<string | null>(null);
  const [pullDistance, setPullDistance] = useState(0);
  const [isRefreshingFeed, setIsRefreshingFeed] = useState(false);
  const postsPerPage = 3;
  const observerRef = useRef<IntersectionObserver | null>(null);
  const loadingRef = useRef<HTMLDivElement>(null);
  const pullStartYRef = useRef<number | null>(null);

  const { likePost, unlikePost, addComment, sharePost } = usePostActions();

  const {
    participating,
    loading: loadingParticipation,
    checkParticipation,
    participate,
  } = useCampaignParticipation();

  const [isPostPreviewOpen, setIsPostPreviewOpen] = useState(false);
  const [postPreviewData, setPostPreviewData] = useState<any>(null);

  // Adicionar estado para rastrear confirmações de problemas
  const [confirmedProblems, setConfirmedProblems] = useState<{
    [key: string]: boolean;
  }>({});
  // Estado para bloquear requisições de voto por post (previne votos duplicados)
  const [votingPosts, setVotingPosts] = useState<{ [key: string]: boolean }>(
    {},
  );
  // Sinal para forçar refresh dos comentários por post (incremental)
  const [commentsRefreshSignal, setCommentsRefreshSignal] = useState<{
    [key: string]: number;
  }>({});
  // Refs para evitar recriar o intervalo de polling quando estados mudam
  const allPostsRef = useRef<PostDisplay[]>(allPosts);
  const votingPostsRef = useRef<{ [key: string]: boolean }>(votingPosts);
  const displayedPostsRef = useRef<PostDisplay[]>(displayedPosts);
  const pullDistanceRef = useRef(0);

  // Sincroniza refs com os estados correspondentes
  useEffect(() => {
    allPostsRef.current = allPosts;
  }, [allPosts]);

  useEffect(() => {
    votingPostsRef.current = votingPosts;
  }, [votingPosts]);

  useEffect(() => {
    displayedPostsRef.current = displayedPosts;
  }, [displayedPosts]);

  useEffect(() => {
    pullDistanceRef.current = pullDistance;
  }, [pullDistance]);

  useEffect(() => {
    const verifyUserCommunities = async () => {
      const token = getTokenFromCookies();
      if (!token) {
        setHasCommunities(null);
        setShowNoCommunitiesMessage(false);
        return;
      }
      try {
        const decodedUserId = JSON.parse(atob(token.split(".")[1])).sub;
        const response = await fetchUserCommunities(token, decodedUserId);
        const participates = (response?.items?.length ?? 0) > 0;
        setHasCommunities(participates);
        setShowNoCommunitiesMessage(!participates);
      } catch (err) {
        console.error("Erro ao verificar comunidades do usuário:", err);
        setHasCommunities(null);
        setShowNoCommunitiesMessage(false);
      }
    };
    verifyUserCommunities();
  }, []);

  // Função para buscar posts do backend (usada tanto para inicial quanto para atualização)
  const fetchPosts = useCallback(async () => {
    const token = getTokenFromCookies();
    if (!token) {
      setError(new Error("Usuário não autenticado."));
      setLoading(false);
      return [];
    }
    try {
      const decodedUserId = JSON.parse(atob(token.split(".")[1])).sub;
      setCurrentUserId((prev) => prev ?? decodedUserId);
      // Busca o feed do usuário (não precisa de communityId específico)
      const response = await fetch(`${API_URL}/posts/feed?limit=9999`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("Erro ao carregar posts");
      }

      const feedData: PostsListFeed = await response.json();
      const userCampaigns = await fetchUserCampaigns();
      const userCampaignPostIds = userCampaigns
        .map((c: any) => c.post?.id)
        .filter(Boolean);
      const currentUserId = token
        ? JSON.parse(atob(token.split(".")[1])).sub
        : null;
      const fetchedPosts = feedData.items.map(
        (item: PostResponse): PostDisplay => {
          let alreadyParticipating = false;
          if (translatePostType(item.type_post) === "Campanha") {
            alreadyParticipating =
              item.user.id === currentUserId ||
              userCampaignPostIds.includes(item.id);
          }
          // Detecta se o usuário já votou na enquete
          let userVotedOptionId: string | undefined = undefined;
          if (item.poll_options && Array.isArray(item.poll_options)) {
            const votedOption = item.poll_options.find(
              (opt: any) =>
                Array.isArray(opt.votes) &&
                opt.votes.some((v: any) => v.user_id === currentUserId),
            );
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
            confirmations_count:
              translatePostType(item.type_post) === "Denúncia" &&
                typeof (item as any).confirmations_count === "number"
                ? (item as any).confirmations_count
                : 0,
          };
        },
      );
      return fetchedPosts;
    } catch (err) {
      setError(err as Error);
      console.error("Erro ao buscar posts:", err);
      return [];
    }
  }, []);

  // Carrega posts iniciais
  const loadInitialPosts = useCallback(async () => {
    setLoading(true);
    const fetchedPosts = await fetchPosts();
    setAllPosts(fetchedPosts);
    setDisplayedPosts(fetchedPosts.slice(0, postsPerPage));
    setCurrentPage(1);
    setHasMorePosts(fetchedPosts.length > postsPerPage);
    setIsFeedEmpty(fetchedPosts.length === 0);
    setLoading(false);
  }, [fetchPosts, postsPerPage]);

  // Polling global otimizado: cria apenas UM intervalo e usa refs para acessar estados mais recentes
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const fetched = await fetchPosts();
        if (!fetched || fetched.length === 0) return;

        const prevAllSnapshot = allPostsRef.current;
        const fetchedMap = new Map(fetched.map((post) => [post.id, post]));

        const updatedExisting = prevAllSnapshot.map((existingPost) => {
          const backendPost = fetchedMap.get(existingPost.id);
          if (!backendPost) {
            return existingPost;
          }

          if (
            (backendPost as any).comments_count !== undefined &&
            (backendPost as any).comments_count !== existingPost.comments
          ) {
            setCommentsRefreshSignal((prev) => ({
              ...prev,
              [existingPost.id]: (prev[existingPost.id] || 0) + 1,
            }));
          }

          fetchedMap.delete(existingPost.id);

          if (votingPostsRef.current[existingPost.id]) {
            return existingPost;
          }

          return mergePostFromBackend(existingPost, backendPost);
        });

        const newPostsFromBackend = Array.from(fetchedMap.values());
        const merged =
          newPostsFromBackend.length > 0
            ? [...newPostsFromBackend, ...updatedExisting]
            : updatedExisting;

        setAllPosts(merged);
        setIsFeedEmpty(merged.length === 0);

        const shownCount = Math.max(
          displayedPostsRef.current.length,
          postsPerPage,
        );
        setDisplayedPosts(merged.slice(0, shownCount));

        setHasMorePosts(!(fetched.length <= shownCount));
      } catch (err) {
        console.warn("Polling failed:", err);
      }
    }, 5000);

    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Função para carregar mais posts (scroll infinito)
  const handleManualRefresh = useCallback(async () => {
    setIsRefreshingFeed(true);
    await loadInitialPosts();
    setIsRefreshingFeed(false);
    setPullDistance(0);
  }, [loadInitialPosts]);

  const loadMorePosts = useCallback(async () => {
    if (loadingMore || !hasMorePosts) return;
    setLoadingMore(true);
    await new Promise((resolve) => setTimeout(resolve, 500));
    const startIndex = currentPage * postsPerPage;
    const endIndex = startIndex + postsPerPage;
    const morePosts = allPosts.slice(startIndex, endIndex);
    if (morePosts.length > 0) {
      setDisplayedPosts((prev) => [...prev, ...morePosts]);
      setCurrentPage((prev) => prev + 1);
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
      { threshold: 0.1 },
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
  }, [loadInitialPosts]);

  useEffect(() => {
    const handleTouchStart = (event: TouchEvent) => {
      if (window.scrollY <= 0) {
        pullStartYRef.current = event.touches[0].clientY;
      } else {
        pullStartYRef.current = null;
      }
    };

    const handleTouchMove = (event: TouchEvent) => {
      if (pullStartYRef.current === null) return;
      const distance = event.touches[0].clientY - pullStartYRef.current;
      if (distance > 0) {
        setPullDistance(distance);
      } else {
        setPullDistance(0);
      }
    };

    const handleTouchEnd = () => {
      if (pullStartYRef.current === null) return;
      if (
        pullDistanceRef.current > 70 &&
        !isRefreshingFeed &&
        !loading
      ) {
        handleManualRefresh();
      } else {
        setPullDistance(0);
      }
      pullStartYRef.current = null;
    };

    window.addEventListener("touchstart", handleTouchStart, { passive: true });
    window.addEventListener("touchmove", handleTouchMove, { passive: true });
    window.addEventListener("touchend", handleTouchEnd);

    return () => {
      window.removeEventListener("touchstart", handleTouchStart);
      window.removeEventListener("touchmove", handleTouchMove);
      window.removeEventListener("touchend", handleTouchEnd);
    };
  }, [handleManualRefresh, isRefreshingFeed, loading]);

  const handleLike = async (post: PostDisplay) => {
    const communityId = post.community?.id;
    if (!communityId) return;

    try {
      if (!post.liked) {
        await likePost(communityId, post.id);
        setDisplayedPosts((posts) =>
          posts.map((p) =>
            p.id === post.id ? { ...p, likes: p.likes + 1, liked: true } : p,
          ),
        );
      } else {
        await unlikePost(communityId, post.id);
        setDisplayedPosts((posts) =>
          posts.map((p) =>
            p.id === post.id
              ? { ...p, likes: Math.max(0, p.likes - 1), liked: false }
              : p,
          ),
        );
      }
    } catch (err) {
      // Tratar erro se necessário
    }
  };

  const handleComment = (post: PostDisplay) => {
    setOpenCommentsPostId((prev) => (prev === post.id ? null : post.id));
  };

  const handleShare = async (post: PostDisplay) => {
    const communityId = post.community?.id;
    if (!communityId) return;

    await sharePost(communityId, post.id);
    // Quando implementar no backend, incremente shares
    // setDisplayedPosts(posts => posts.map((p) =>
    //   p.id === post.id ? { ...p, shares: p.shares + 1 } : p
    // ));
  };

  // Função para verificar se o problema já foi confirmado pelo usuário
  const checkProblemConfirmation = async (
    postId: string,
    communityId: string,
  ) => {
    try {
      const token = getTokenFromCookies();
      const response = await fetch(
        `${API_URL}/communities/${communityId}/complaints/${postId}`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        },
      );
      if (!response.ok) {
        return false;
      }
      const data = await response.json();
      // Verifica se o usuário atual está na lista de confirmações
      const currentUserId = token
        ? JSON.parse(atob(token.split(".")[1])).sub
        : null;
      return (
        data.confirmations?.some((c: any) => c.user_id === currentUserId) ??
        false
      );
    } catch (err) {
      console.error("Erro ao verificar confirmação do problema:", err);
      return false;
    }
  };

  // Confirmar problema em denúncia
  const handleConfirmComplaint = async (post: PostDisplay) => {
    try {
      const token = getTokenFromCookies();
      const communityId = post.community?.id;

      if (!communityId) {
        toast.error("ID da comunidade não encontrado");
        return;
      }

      if (post.user?.id && post.user.id === currentUserId) {
        toast.info("Você não pode confirmar um problema que criou.");
        return;
      }

      if (!confirmedProblems[post.id]) {
        await confirmComplaint(communityId, post.id, token ?? undefined);
        setConfirmedProblems((prev) => ({ ...prev, [post.id]: true }));
        setDisplayedPosts((prev: PostDisplay[]) =>
          prev.map((p: PostDisplay) =>
            p.id === post.id
              ? { ...p, confirmations_count: (p.confirmations_count ?? 0) + 1 }
              : p,
          ),
        );
        setAllPosts((prev: PostDisplay[]) =>
          prev.map((p: PostDisplay) =>
            p.id === post.id
              ? { ...p, confirmations_count: (p.confirmations_count ?? 0) + 1 }
              : p,
          ),
        );
        toast.success("Confirmação registrada!");
      } else {
        toast.info("Você já confirmou este problema.");
      }
    } catch (err) {
      toast.error("Erro ao confirmar problema");
    }
  };

  // Atualizar o estado inicial ao carregar os posts
  useEffect(() => {
    const fetchConfirmedProblems = async () => {
      const confirmedMap: { [key: string]: boolean } = {};
      for (const post of allPosts) {
        if (
          post.community?.id &&
          translatePostType(post.type_post) === "Denúncia"
        ) {
          confirmedMap[post.id] = await checkProblemConfirmation(
            post.id,
            post.community.id,
          );
        }
      }
      setConfirmedProblems(confirmedMap);
    };

    if (allPosts.length > 0) {
      fetchConfirmedProblems();
    }
  }, [allPosts]);

  // Função auxiliar para atualizar o estado do post com novas opções de enquete
  const updatePollState = (
    postId: string,
    newOptions: any[],
    newUserVotedOptionId: string | undefined,
    pollQuestion?: string,
  ) => {
    const updatePost = (p: PostDisplay) => {
      if (p.id !== postId) return p;
      return {
        ...p,
        poll_options: newOptions,
        userVotedOptionId: newUserVotedOptionId,
        ...(pollQuestion && { poll_question: pollQuestion }),
      } as PostDisplay;
    };

    setAllPosts((prev) => prev.map(updatePost));
    setDisplayedPosts((prev) => prev.map(updatePost));
    if (postPreviewData && postPreviewData.id === postId) {
      setPostPreviewData((prev: any) => ({
        ...prev,
        poll_options: newOptions,
        userVotedOptionId: newUserVotedOptionId,
        ...(pollQuestion && { poll_question: pollQuestion }),
      }));
    }
  };

  // Mescla os dados do backend mantendo a ordem local e os campos derivados
  const mergePostFromBackend = (
    localPost: PostDisplay,
    backendPost: PostDisplay,
  ): PostDisplay => {
    let mergedPollOptions = localPost.poll_options;
    const backendPollOptions = (backendPost as any).poll_options;

    if (Array.isArray(backendPollOptions) && backendPollOptions.length > 0) {
      if (
        Array.isArray(localPost.poll_options) &&
        localPost.poll_options.length > 0
      ) {
        const optionsMap: { [key: string]: any } = {};
        backendPollOptions.forEach((option: any) => {
          optionsMap[option.id] = option;
        });

        mergedPollOptions = localPost.poll_options.map(
          (option: any) => optionsMap[option.id] ?? option,
        );

        backendPollOptions.forEach((option: any) => {
          if (!mergedPollOptions!.some((existing: any) => existing.id === option.id)) {
            mergedPollOptions!.push(option);
          }
        });
      } else {
        mergedPollOptions = backendPollOptions;
      }
    }

    return {
      ...localPost,
      ...backendPost,
      likes: (backendPost as any).likes_count ?? localPost.likes,
      comments: (backendPost as any).comments_count ?? localPost.comments,
      shares: (backendPost as any).report_count ?? localPost.shares,
      poll_options: mergedPollOptions,
      poll_question: backendPost.poll_question ?? localPost.poll_question,
      userVotedOptionId:
        backendPost.userVotedOptionId ?? localPost.userVotedOptionId,
      confirmations_count:
        (backendPost as any).confirmations_count ?? localPost.confirmations_count,
    };
  };

  // Função auxiliar para mesclar opções do backend preservando a ordem local
  const mergeOptionsPreservingOrder = (
    localOptions: any[],
    backendOptions: any[],
  ): any[] => {
    if (!Array.isArray(backendOptions) || backendOptions.length === 0) {
      return localOptions;
    }
    if (!Array.isArray(localOptions) || localOptions.length === 0) {
      return backendOptions;
    }

    const backendMap: { [key: string]: any } = {};
    backendOptions.forEach((o) => {
      backendMap[o.id] = o;
    });

    // Mantém a ordem das opções locais, apenas atualizando os dados do backend
    const merged = localOptions.map((o) => backendMap[o.id] ?? o);

    // Adiciona novas opções que possam ter sido criadas
    backendOptions.forEach((o) => {
      if (!merged.some((m) => m.id === o.id)) {
        merged.push(o);
      }
    });

    return merged;
  };

  // Função para retirar o voto
  const handleUnvotePoll = async (post: PostDisplay) => {
    if (!post.userVotedOptionId) return;
    const token = getTokenFromCookies();
    const communityId = post.community?.id;
    if (!communityId) return;

    // Salva estado anterior para rollback em caso de erro
    const previousOptions = post.poll_options ?? [];
    const previousVotedId = post.userVotedOptionId;

    // Atualização otimista imediata
    const optimisticOptions = Array.isArray(post.poll_options)
      ? post.poll_options.map((o: any) => {
        if (o.id === post.userVotedOptionId) {
          return { ...o, votes_count: Math.max(0, (o.votes_count || 0) - 1) };
        }
        return { ...o };
      })
      : [];

    updatePollState(post.id, optimisticOptions, undefined);

    try {
      await unvoteOnPoll(
        communityId,
        post.userVotedOptionId,
        token ?? undefined,
      );

      // Mantém as opções otimistas já atualizadas (voto já foi decrementado)
      toast.success("Voto removido");
    } catch (err: any) {
      console.error("Erro ao remover voto", err);
      // Rollback
      updatePollState(post.id, previousOptions, previousVotedId);
      toast.error(err?.message || "Erro ao remover voto");
    }
  };

  // Participar da campanha
  const handleParticipateCampaign = async (post: PostDisplay) => {
    const communityId = post.community?.id;
    if (!communityId) {
      toast.error("ID da comunidade não encontrado");
      return;
    }

    try {
      await participate(communityId, post.id);
      setDisplayedPosts((prev) =>
        prev.map((p) =>
          p.id === post.id ? { ...p, alreadyParticipating: true } : p,
        ),
      );
      setAllPosts((prev) =>
        prev.map((p) =>
          p.id === post.id ? { ...p, alreadyParticipating: true } : p,
        ),
      );
      toast.success("Você agora faz parte da campanha!");
    } catch (err) {
      toast.error("Erro ao participar da campanha");
    }
  };

  // Função para votar em uma enquete (suporta troca de voto e remover voto clicando na mesma opção)
  const handleVotePoll = async (post: PostDisplay, optionId: string) => {
    const communityId = post.community?.id;
    if (!communityId) return;
    const token = getTokenFromCookies();

    // Se já estamos processando um voto para este post, ignore
    if (votingPosts[post.id]) return;

    // Se o usuário clicou na mesma opção que já votou -> trata como remover voto
    if (post.userVotedOptionId === optionId) {
      await handleUnvotePoll(post);
      return;
    }

    // Salva estado anterior para rollback em caso de erro
    const previousOptions = post.poll_options ?? [];
    const previousVotedId = post.userVotedOptionId;

    // Atualização otimista imediata - decrementa voto anterior e incrementa novo
    const optimisticOptions = Array.isArray(post.poll_options)
      ? post.poll_options.map((o: any) => {
        let newVotesCount = o.votes_count || 0;

        // Decrementa o voto anterior (se existir)
        if (previousVotedId && o.id === previousVotedId) {
          newVotesCount = Math.max(0, newVotesCount - 1);
        }

        // Incrementa o novo voto
        if (o.id === optionId) {
          newVotesCount = newVotesCount + 1;
        }

        return { ...o, votes_count: newVotesCount };
      })
      : [];

    // Aplica atualização otimista imediatamente
    updatePollState(post.id, optimisticOptions, optionId);
    setVotingPosts((prev) => ({ ...prev, [post.id]: true }));

    try {
      const response = await voteOnPoll(
        communityId,
        optionId,
        token ?? undefined,
      );

      // Mescla resposta do backend preservando ordem local
      const backendOptions =
        response?.post?.poll_options ?? response?.options ?? [];
      const finalOptions = mergeOptionsPreservingOrder(
        optimisticOptions,
        backendOptions,
      );

      updatePollState(
        post.id,
        finalOptions,
        optionId,
        response?.post?.poll_question,
      );
      toast.success("Voto registrado");
    } catch (err: any) {
      console.error("Erro ao votar na enquete:", err);
      // Rollback para estado anterior
      updatePollState(post.id, previousOptions, previousVotedId);
      toast.error(err?.message || "Erro ao registrar o voto.");
    } finally {
      setVotingPosts((prev) => ({ ...prev, [post.id]: false }));
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col justify-center items-center h-full w-full px-4 mt-62 text-center">
        Carregando posts...
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col justify-center items-center h-full w-full px-4 mt-62 text-center text-red-500">
        Erro ao carregar posts: {error.message}
      </div>
    );
  }

  if (showNoCommunitiesMessage) {
    return (
      <div className="flex flex-col justify-center items-center w-full px-4 text-center gap-3 min-h-[calc(100vh-12rem)]">
        <p className="text-lg font-medium">
          Você ainda não participa de nenhuma comunidade.
        </p>
        <p>
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

  if (!loading && !error && isFeedEmpty && !showNoCommunitiesMessage) {
    return (
      <div className="flex flex-col justify-center items-center w-full px-4 text-center text-neutral-700 gap-2 min-h-[calc(100vh-12rem)]">
        <p className="text-lg font-medium">
          Não há publicações aparente...
        </p>
        <p className="text-sm">
          Atualize a página para carregar novas publicações.
        </p>
      </div>
    );
  }

  return (
    <div className="flex-1 p-4 min-[900px]:p-6 flex justify-center">
      <main className="post-content overflow-hidden max-w-[680px] w-full space-y-6">
        {(pullDistance > 0 || isRefreshingFeed) && (
          <div
            className="flex justify-center items-center text-xs text-neutral-600 transition-all duration-200"
            style={{
              height: Math.min(80, pullDistance || (isRefreshingFeed ? 60 : 0)),
              opacity:
                pullDistance > 0
                  ? Math.min(1, pullDistance / 70)
                  : isRefreshingFeed
                    ? 1
                    : 0,
            }}
          >
            {isRefreshingFeed ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Atualizando feed...
              </>
            ) : pullDistance > 70 ? (
              "Solte para atualizar"
            ) : (
              "Puxe para atualizar"
            )}
          </div>
        )}
        {/* Banner de novos posts fixo na tela */}
        {showNewPostsBanner && newPosts.length > 0 && (
          <div
            style={{
              position: "fixed",
              top: 70,
              left: "50%",
              transform: "translateX(-50%)",
              zIndex: 0,
              minWidth: 220,
              maxWidth: 360,
            }}
            className="flex justify-center animate-fade-in"
          >
            <button
              className="px-4 py-2 bg-black text-white rounded-xl shadow-lg hover:bg-gray-900 transition-colors border-gray-200 cursor-pointer"
              onClick={() => {
                setAllPosts((prev) => [...newPosts, ...prev]);
                setDisplayedPosts((prev) => [...newPosts, ...prev]);
                setShowNewPostsBanner(false);
                setNewPosts([]);
              }}
            >
              {newPosts.length === 1
                ? "1 publicado"
                : `${newPosts.length} publicados`}
            </button>
          </div>
        )}
        {displayedPosts.map((post) => (
          <React.Fragment key={post.id}>
            <article className="flex flex-col justify-center px-6 py-4 w-full bg-white rounded border-solid shadow-sm border-[0.5px] border-stone-300 max-md:px-5 max-md:max-w-full">
              <div className="w-full max-w-[632px] max-md:max-w-full">
                <div className="w-full max-md:max-w-full">
                  <header className="flex items-start justify-between gap-4 w-full max-md:max-w-full">
                    <div className="flex flex-1 min-w-0 items-start max-[480px]:items-center">
                      <div className="w-11 h-11 rounded-[32px] overflow-hidden shrink-0 flex items-center justify-center bg-neutral-200 max-[480px]:w-9 max-[480px]:h-9">
                        <img
                          src={post.avatar || "/placeholder.svg"}
                          alt={`${post.author} avatar`}
                          className="object-cover w-full h-full"
                        />
                      </div>
                      <div className="ml-3 flex flex-col min-w-0 max-[480px]:ml-2">
                        <div className="flex gap-2 items-center w-full h-[23px] max-[480px]:h-auto max-[480px]:flex-wrap">
                          <div className="flex overflow-hidden gap-2.5 justify-center items-center self-stretch px-3 my-auto max-[480px]:px-1.5 max-[480px]:gap-1.5 max-[480px]:flex-nowrap max-[480px]:min-w-0">
                            <Link
                              href={`/profile/${post.username || post.user.id}`}
                              className="self-stretch my-auto text-sm text-neutral-800 hover:text-blue-600 whitespace-nowrap transition-colors hover:underline max-[480px]:text-xs max-[480px]:truncate max-[480px]:max-w-[160px]"
                            >
                              {post.author}
                            </Link>
                            <CheckmarkFilled
                              className={`object-contain shrink-0 self-stretch my-auto aspect-square w-[18px] ${getCheckmarkColorClass(post.role)} max-[480px]:w-[14px]`}
                              aria-label="Verificado"
                            />
                            <div className="self-stretch my-auto text-[10px] font-semibold max-[480px]:hidden">
                              •
                            </div>
                            <div
                              className={`flex gap-2.5 justify-center items-center self-stretch px-3 py-1 my-auto text-xs whitespace-nowrap rounded ${getRoleBadgeClasses(post.role)} max-[480px]:hidden`}
                            >
                              <div className="self-stretch my-auto">
                                {post.role}
                              </div>
                            </div>
                          </div>
                          <div className="self-stretch my-auto text-xs leading-none text-justify whitespace-nowrap text-neutral-800 max-[480px]:hidden">
                            {post.location}
                          </div>
                        </div>
                        <div className="hidden max-[480px]:flex items-center gap-2 px-1.5 text-xs text-neutral-800 mt-1">
                          <div
                            className={`flex gap-2 justify-center items-center px-2 py-0.5 text-[10px] whitespace-nowrap rounded ${getRoleBadgeClasses(post.role)}`}
                          >
                            <span>{post.role}</span>
                          </div>
                          <div className="text-[11px] text-neutral-600">
                            {post.location}
                          </div>
                        </div>
                        <div className="self-start px-3 mt-2 text-[10px] font-semibold tracking-normal whitespace-nowrap text-neutral-500">
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
                    <div className="flex gap-2 items-center flex-shrink-0">
                      <div className="relative">
                        <button
                          className="p-1 hover:bg-gray-100 rounded-full cursor-pointer transition-colors"
                          onClick={(e) => {
                            e.stopPropagation();
                            setOpenMenuPostId(
                              openMenuPostId === post.id ? null : post.id,
                            );
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
                                  const communityId = post.community?.id;
                                  if (!communityId) {
                                    toast.error(
                                      "ID da comunidade não encontrado",
                                    );
                                    return;
                                  }
                                  await reportPost(communityId, post.id);
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
                        style={{ wordBreak: "break-word" }}
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
                              profile_picture: post.user.profile_picture,
                            },
                            poll_question: post.poll_question,
                            poll_options: post.poll_options,
                          });
                          setIsPostPreviewOpen(true);
                        }}
                      >
                        <h2
                          className="text-neutral-800 px-0 font-georgia font-bold break-words w-full max-w-full"
                          style={{
                            fontFamily: "Georgia, serif",
                            fontWeight: "bold",
                            wordBreak: "break-word",
                            overflowWrap: "break-word",
                            whiteSpace: "pre-line",
                          }}
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
                        style={{
                          wordBreak: "break-word",
                          overflowWrap: "break-word",
                          whiteSpace: "pre-line",
                        }}
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
                              profile_picture: post.user.profile_picture,
                            },
                            poll_question: post.poll_question,
                            poll_options: post.poll_options,
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
                    {post.type === "Enquete" &&
                      Array.isArray(post.poll_options) &&
                      post.poll_options.length > 0 && (
                        <div className="mt-6 w-full">
                          {post.poll_question && (
                            <h3 className="text-base font-semibold text-neutral-800 mb-6">
                              {post.poll_question}
                            </h3>
                          )}
                          {(() => {
                            const totalVotes = Array.isArray(post.poll_options)
                              ? post.poll_options.reduce(
                                (sum, opt) => sum + opt.votes_count,
                                0,
                              )
                              : 0;
                            return (post.poll_options ?? []).map((option) => {
                              const percent =
                                totalVotes > 0
                                  ? Math.round(
                                    (option.votes_count / totalVotes) * 100,
                                  )
                                  : 0;
                              const isUserVote =
                                post.userVotedOptionId === option.id;
                              return (
                                <div
                                  key={`${option.id}-${option.votes_count}`}
                                  className={`mb-4 cursor-pointer hover:opacity-80 transition-opacity`}
                                >
                                  <button
                                    className={`w-full text-left bg-transparent border-none outline-none p-0 m-0 ${votingPosts[post.id] ? "cursor-not-allowed opacity-70" : "cursor-pointer"}`}
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      if (!votingPosts[post.id])
                                        handleVotePoll(post, option.id);
                                    }}
                                    disabled={votingPosts[post.id]}
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
                                        {option.votes_count}{" "}
                                        {option.votes_count === 1
                                          ? "voto"
                                          : "votos"}
                                      </span>
                                    </div>
                                    <div className="mt-2 w-full rounded-sm">
                                      <div className="flex flex-col items-start rounded-sm border border-solid border-stone-300">
                                        <div
                                          className="flex shrink-0 h-2 rounded-sm bg-neutral-800"
                                          style={{
                                            width: `${percent}%`,
                                            minWidth: "8px",
                                            transition: "width 300ms ease",
                                          }}
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
                    {post.type === "Campanha" && (
                      <button
                        className={`mt-4 w-full py-2 px-4 text-left font-regular transition-colors cursor-pointer ${post.alreadyParticipating || participating[post.id] ? "bg-neutral-200 text-neutral-700 cursor-not-allowed" : "bg-neutral-900 text-white hover:bg-neutral-800"}`}
                        onClick={(e) => {
                          e.stopPropagation();
                          if (
                            !post.alreadyParticipating &&
                            !participating[post.id]
                          )
                            handleParticipateCampaign(post);
                        }}
                        disabled={
                          post.alreadyParticipating || participating[post.id]
                        }
                      >
                        {post.alreadyParticipating || participating[post.id]
                          ? "Já participa da campanha"
                          : "Participar da Campanha"}
                      </button>
                    )}

                    {/* Botão Confirmar problema para Denúncia */}
                    {post.type === "Denúncia" && (
                      <button
                        className={`mt-4 w-full py-2 px-4 text-left font-regular transition-colors ${(post.confirmations_count ?? 0) > 0 ? "bg-neutral-200 text-neutral-700 cursor-not-allowed" : "bg-neutral-900 text-white hover:bg-neutral-800"}`}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleConfirmComplaint(post);
                        }}
                        disabled={(post.confirmations_count ?? 0) > 0}
                      >
                        {(post.confirmations_count ?? 0) > 0
                          ? "Problema confirmado"
                          : "Confirmar problema"}
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
                      className={`flex overflow-hidden gap-2 items-center self-stretch my-auto text-justify whitespace-nowrap transition-colors px-3 py-1 cursor-pointer ${openCommentsPostId === post.id ? "bg-neutral-200" : ""}`}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleComment(post);
                      }}
                      title="Comentar"
                    >
                      <Forum
                        className={`h-4 w-4 ${openCommentsPostId === post.id ? "text-black-300" : "text-gray-500"}`}
                      />
                      <div
                        className={`self-stretch my-auto ${openCommentsPostId === post.id ? "text-black-600" : "text-neutral-500"}`}
                      >
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
                      <div className="self-stretch my-auto">{post.shares}</div>
                    </button>
                  </div>
                </div>
              </div>
            </article>
            {openCommentsPostId === post.id && (
              <div className="flex justify-center w-full -mt-6">
                {post.community?.id && (
                  <CommentsSection
                    communityId={post.community.id}
                    postId={post.id}
                    refreshSignal={commentsRefreshSignal[post.id]}
                  />
                )}
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
