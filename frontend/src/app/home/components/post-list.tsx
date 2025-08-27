"use client";

import React, { useState, useEffect } from "react";
import { toast } from "react-toastify";
import { useCampaignParticipation } from "@/app/api/src/hooks/post/useCampaignParticipation";
import Link from "next/link";
import {
  Bookmark,
  EllipsisVerticalIcon as OverflowMenuVertical,
  Activity,
} from "lucide-react";
import { fetchPostsByCommunity } from "@/app/api/src/services/post/postService";
import getTokenFromCookies from "@/app/api/src/controllers/getTokenFromCookies";
import usePostActions from "@/app/api/src/hooks/post/usePostActions";
import { PostResponse, PostsListFeed } from "@/app/api/src/types/posts/Post";
import { translateUserRole } from "@/lib/roleTranslations";
import { translatePostType } from "@/lib/postTypeTranslations";
import { Forum, FaceSatisfied, TextBold, TextItalic, ListNumbered, ListBulleted, CheckmarkFilled, OverflowMenuHorizontal, ArrowUp } from "@carbon/icons-react";
import { getRelativeTime } from "@/lib/relativeTime";
import { API_URL } from "@/config";

// CommentsSection como componente interno
interface Comment {
  id: string;
  user: {
    name: string;
    profile_picture?: string;
    profile_image_url?: string;
    role?: string;
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

  const getRoleBadgeClasses = (role?: string) => {
    if (!role) return '';
    if (role.toLowerCase().includes('admin')) {
      return 'bg-yellow-600 bg-opacity-40 text-yellow-950';
    }
    if (role.toLowerCase().includes('líder') || role.toLowerCase().includes('leader')) {
      return 'bg-neutral-800 text-zinc-100';
    }
    return 'bg-neutral-800 text-zinc-100';
  };

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
      <div className="flex-1 shrink my-auto basis-0 min-w-60 max-md:max-w-full">
        <div className="flex flex-wrap gap-3 items-center py-3 w-full max-md:max-w-full">
          <div className={`flex items-center self-stretch my-auto min-w-60 text-neutral-800 ${isChild ? 'w-[360px]' : 'w-[301px]'}`}>
            <div className={`self-stretch my-auto min-w-60 ${isChild ? 'w-[360px]' : 'w-[301px]'}`}>
              <div className="flex gap-2 items-center w-full h-[23px]">
                <div className="flex overflow-hidden gap-2.5 justify-center items-center self-stretch px-3 my-auto">
                  <div className="self-stretch my-auto text-sm text-neutral-800">
                    {comment.user.name}
                  </div>
                  <CheckmarkFilled className="object-contain shrink-0 self-stretch my-auto aspect-square w-[18px] text-black" aria-label="Verificado" />
                  {comment.user.role && (
                    <div className={`flex gap-2.5 justify-center items-center self-stretch px-3 py-1 my-auto text-xs whitespace-nowrap rounded ${getRoleBadgeClasses(comment.user.role)}`}>
                      <div className="self-stretch my-auto">
                        {comment.user.role}
                      </div>
                    </div>
                  )}
                  <div className="self-stretch my-auto text-xs font-semibold">
                    <div className="text-neutral-800">
                      {getRelativeTime(comment.created_at)}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="flex gap-4 items-center self-stretch my-auto w-5 min-h-5">
            <OverflowMenuHorizontal className="object-contain self-stretch my-auto w-5 aspect-square cursor-pointer hover:opacity-70 transition-opacity text-neutral-500" aria-label="Menu" />
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
                <div className={`self-stretch my-auto ${likedComments[comment.id] ? 'text-blue-600' : 'text-neutral-500'}`}>
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
        <div className="flex flex-wrap items-start self-end mt-6 max-w-full w-[592px]">
          {comment.replies.map(child => renderComment(child, true))}
        </div>
      )}
    </div>
  );

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
              {comments.length}
            </span>
          </div>
        </header>

        {/* Comments List */}
        <section
          className="flex flex-col p-4 bg-white rounded-sm max-w-[648px] w-full"
          style={{ maxHeight: 600, overflowY: 'auto' }}
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
};

export default function PostList() {
  const [posts, setPosts] = useState<PostDisplay[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [showNoCommunitiesMessage, setShowNoCommunitiesMessage] = useState(false);
  const [openCommentsPostId, setOpenCommentsPostId] = useState<string | null>(null);

  const {
    likePost,
    unlikePost,
    addComment,
    sharePost,
  } = usePostActions();

  const { participating, loading: loadingParticipation, checkParticipation, participate } = useCampaignParticipation();

  useEffect(() => {
    const loadPosts = async () => {
      const token = getTokenFromCookies();
      if (!token) {
        setError(new Error("Usuário não autenticado."));
        setLoading(false);
        return;
      }

      try {
        const communityId = "default-community-id";
        const feedData: PostsListFeed = await fetchPostsByCommunity(
          token,
          communityId
        );

        // Checar participação em paralelo usando hook
        const fetchedPosts = await Promise.all(feedData.items.map(async (item: PostResponse): Promise<PostDisplay> => {
          let alreadyParticipating = false;
          if (translatePostType(item.type_post) === 'Campanha') {
            alreadyParticipating = await checkParticipation(item.community.id, item.id);
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
            image: item.image_url || "/publication-image.jpg",
            likes: item.likes_count,
            comments: item.comments_count,
            shares: item.report_count,
            liked: false,
            alreadyParticipating,
          };
        }));
        setPosts(fetchedPosts);
        if (fetchedPosts.length === 0) {
          setShowNoCommunitiesMessage(true);
        }
      } catch (err) {
        setError(err as Error);
        console.error("Erro ao buscar posts:", err);
      } finally {
        setLoading(false);
      }
    };

    loadPosts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleLike = async (post: PostDisplay) => {
    const communityId = post.community?.id || "default-community-id";
    try {
      if (!post.liked) {
        await likePost(communityId, post.id);
        setPosts(posts.map((p) =>
          p.id === post.id ? { ...p, likes: p.likes + 1, liked: true } : p
        ));
      } else {
        await unlikePost(communityId, post.id);
        setPosts(posts.map((p) =>
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
    // setPosts(posts.map((p) =>
    //   p.id === post.id ? { ...p, shares: p.shares + 1 } : p
    // ));
  };

  // Participar da campanha
  const handleParticipateCampaign = async (post: PostDisplay) => {
    try {
      await participate(post.community?.id || "default-community-id", post.id);
      setPosts((prev) => prev.map((p) => p.id === post.id ? { ...p, alreadyParticipating: true } : p));
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
      <div className="flex justify-center items-center h-full text-red-500">
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
        {posts.map((post) => (
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
                              className="self-stretch my-auto text-sm text-neutral-800 hover:text-blue-600 transition-colors hover:underline"
                            >
                              {post.author}
                            </Link>
                            <CheckmarkFilled className="object-contain shrink-0 self-stretch my-auto aspect-square w-[18px] text-black" aria-label="Verificado" />
                            <div className="flex gap-2.5 justify-center items-center self-stretch px-3 py-1 my-auto text-xs text-white whitespace-nowrap rounded bg-neutral-800">
                              <div className="self-stretch my-auto">
                                {post.role}
                              </div>
                            </div>
                          </div>
                          <div className="self-stretch my-auto text-xs leading-none text-justify text-neutral-800">
                            {post.location}
                          </div>
                        </div>
                        <div className="self-start px-3 mt-2 text-xs font-semibold tracking-normal whitespace-nowrap text-neutral-500">
                          <div className="flex items-center gap-1">
                            <div className="self-stretch my-auto text-neutral-500">
                              {post.type}
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
                      // Aqui você pode adicionar lógica de bookmark real se desejar
                      >
                        <Bookmark
                          className={`h-4 w-4 text-gray-500`}
                        />
                      </button>
                      <button className="p-1 hover:bg-gray-100 rounded-full transition-colors">
                        <OverflowMenuVertical className="h-4 w-4 text-gray-500" />
                      </button>
                    </div>
                  </header>

                  <div className="mt-6 w-full text-neutral-800 max-md:max-w-full">
                    <div className="flex flex-row justify-between items-center w-full max-md:max-w-full">
                      <div className="flex gap-2.5 items-center text-xl font-bold leading-relaxed min-w-60 px-0 w-0 flex-1" style={{ wordBreak: 'break-word' }}>
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
                        className="mt-4 text-sm leading-5 text-justify text-neutral-800 max-md:max-w-full whitespace-pre-line font-regular break-words w-full max-w-full"
                        style={{ wordBreak: 'break-word', overflowWrap: 'break-word', whiteSpace: 'pre-line' }}
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

                    {/* Botão Participar da Campanha */}
                    {post.type === 'Campanha' && (
                      <button
                        className={`mt-4 w-full py-2 px-4 text-left font-regular transition-colors ${participating[post.id] ? 'bg-neutral-200 text-neutral-700 cursor-not-allowed' : 'bg-neutral-900 text-white hover:bg-neutral-800'}`}
                        onClick={() => !participating[post.id] && handleParticipateCampaign(post)}
                        disabled={participating[post.id]}
                      >
                        {participating[post.id] ? 'Já participa da campanha' : 'Participar da Campanha'}
                      </button>
                    )}
                  </div>
                </div>

                <div className="flex justify-between items-center mt-10 w-full text-xs font-medium leading-none text-neutral-500 max-md:max-w-full">
                  <div className="flex overflow-hidden gap-8 items-center self-stretch my-auto min-h-5 w-[214px]">
                    <button
                      className="flex overflow-hidden gap-2 items-center self-stretch my-auto text-justify whitespace-nowrap"
                      onClick={() => handleLike(post)}
                      title="Curtir"
                    >
                      <ArrowUp className="h-4 w-4 text-gray-500" />
                      <div className="self-stretch my-auto text-neutral-500">
                        {post.likes}
                      </div>
                    </button>
                    <button
                      className={`flex overflow-hidden gap-2 items-center self-stretch my-auto text-justify whitespace-nowrap transition-colors px-3 py-1 ${openCommentsPostId === post.id ? 'bg-neutral-200' : ''}`}
                      onClick={() => handleComment(post)}
                      title="Comentar"
                    >
                      <Forum className={`h-4 w-4 ${openCommentsPostId === post.id ? 'text-black-300' : 'text-gray-500'}`} />
                      <div className={`self-stretch my-auto ${openCommentsPostId === post.id ? 'text-black-600' : 'text-neutral-500'}`}>
                        {post.comments}
                      </div>
                    </button>
                    <button
                      className="flex overflow-hidden gap-2 items-center self-stretch my-auto text-teal-700"
                      onClick={() => handleShare(post)}
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
      </main>
    </div>
  );
}
