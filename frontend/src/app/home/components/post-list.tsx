"use client";

import React, { useState, useEffect } from "react";
import { toast } from "react-toastify";
import { useCampaignParticipation } from "@/app/api/src/hooks/post/useCampaignParticipation";
import Link from "next/link";
import {
  Bookmark,
  EllipsisVerticalIcon as OverflowMenuVertical,
  ArrowUp,
  Activity,
} from "lucide-react";
import { fetchPostsByCommunity } from "@/app/api/src/services/post/postService";
import getTokenFromCookies from "@/app/api/src/controllers/getTokenFromCookies";
import usePostActions from "@/app/api/src/hooks/post/usePostActions";
import { PostResponse, PostsListFeed } from "@/app/api/src/types/posts/Post";
import { translateUserRole } from "@/lib/roleTranslations";
import { translatePostType } from "@/lib/postTypeTranslations";
import { Forum, FaceSatisfied, TextBold, TextItalic, ListNumbered, ListBulleted } from "@carbon/icons-react";
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
}

function CommentsSection({ communityId, postId }: { communityId: string; postId: string }) {
  const { listComments, addComment, replyComment } = usePostActions();
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

  const renderComment = (comment: Comment, isChild = false) => (
    <article
      key={comment.id}
      className={`flex ${isChild ? 'ml-12' : ''} items-start self-stretch p-4 bg-white rounded-sm max-md:p-3 max-sm:p-2`}
    >
      <div className="flex flex-col gap-2 items-center">
        <img
          src={comment.user && (comment.user.profile_image_url || comment.user.profile_picture) ? (comment.user.profile_image_url || comment.user.profile_picture) : '/no-profile-pic.png'}
          alt={`${comment.user.name} avatar`}
          className="w-11 h-11 border border-solid border-stone-300 rounded-[32px] max-sm:w-9 max-sm:h-9"
        />
      </div>
      <div className="flex flex-col gap-2 items-start flex-[1_0_0]">
        <header className="flex gap-3 items-center self-stretch px-0 py-3">
          <div className="flex items-center">
            <div className="flex flex-col gap-2 items-start">
              <div className="flex gap-2 items-center self-stretch h-[23px]">
                <div className="flex gap-2.5 justify-center items-center px-3 py-0 max-sm:flex-wrap max-sm:gap-1.5 max-sm:px-2 max-sm:py-0">
                  <span className="text-sm text-neutral-800 max-md:text-sm max-sm:text-xs">
                    {comment.user.name}
                  </span>
                  {comment.user.role && (
                    <div className="flex gap-2.5 justify-center items-center px-3 py-1 rounded bg-neutral-800">
                      <span className="text-xs text-zinc-100 max-sm:text-xs">
                        {comment.user.role}
                      </span>
                    </div>
                  )}
                  <div className="flex flex-col gap-2.5 items-start">
                    <time className="text-xs font-semibold text-neutral-800 max-md:text-xs max-sm:text-xs">
                      {new Date(comment.created_at).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
                    </time>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </header>
        <div className="flex flex-col gap-2 items-start self-stretch px-3 py-0">
          <div className="flex gap-2.5 items-center self-stretch py-2 pr-3 pl-0">
            <p className="text-sm leading-5 flex-[1_0_0] text-neutral-800 max-md:text-sm max-md:leading-5 max-sm:text-xs max-sm:leading-4">
              {comment.content}
            </p>
          </div>
          <footer className="flex justify-between items-center self-stretch">
            <div className="flex gap-8 items-center h-5">
              {/* Aqui pode exibir likes, replies, etc. */}
            </div>
            <button
              className="flex gap-2 items-center"
              onClick={() => setReplyingTo(replyingTo === comment.id ? null : comment.id)}
            >
              <i className="ti ti-message-circle w-4 h-4 text-neutral-500 max-sm:w-3.5 max-sm:h-3.5" />
              <span className="text-xs font-medium leading-4 text-justify text-neutral-500 max-md:text-xs max-sm:text-xs">
                Responder
              </span>
            </button>
          </footer>
          {replyingTo === comment.id && (
            <div className="w-full mt-2">
              <textarea
                className="w-full p-2 border rounded text-sm"
                rows={2}
                placeholder="Digite sua resposta..."
                value={replyInput[comment.id] || ''}
                onChange={e => setReplyInput(prev => ({ ...prev, [comment.id]: e.target.value }))}
              />
              <button
                className="mt-1 px-3 py-1 bg-neutral-800 text-white rounded text-xs"
                onClick={() => handleReply(comment.id)}
              >
                Enviar resposta
              </button>
            </div>
          )}
        </div>
        {/* Renderizar respostas (filhos) recursivamente */}
        {((Array.isArray(comment.children) && comment.children.length > 0) || (Array.isArray(comment.replies) && comment.replies.length > 0)) && (
          <div className="w-full mt-2">
            {(comment.children && comment.children.length > 0
              ? comment.children
              : comment.replies || []
            ).map(child => renderComment(child, true))}
          </div>
        )}
      </div>
    </article>
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
              <div className="flex flex-row justify-end items-end w-full">
                <button
                  className="px-3 py-2 bg-neutral-800 text-white rounded-xs font-regular"
                  onClick={handleAddComment}
                >
                  Enviar
                </button>
              </div>
              {/* Barra de formatação com os mesmos ícones da campanha */}
              <div className="flex gap-4 items-start max-sm:gap-3 mt-2">
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
            </div>
            {/* <div className="self-stretch h-px bg-neutral-500" /> */}
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
        <section className="flex flex-col gap-2 items-start self-stretch">
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
            time: (() => {
              const date = new Date(item.created_at);
              date.setHours(date.getHours() - 3);
              return date.toLocaleTimeString("pt-BR", {
                hour: "2-digit",
                minute: "2-digit",
              });
            })(),
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
                            <img
                              src="https://api.builder.io/api/v1/image/assets/367ac41a58454bf7adac62a5f3afc83b/c57f1c8b88c7dbe0b50fb5cb6ba42204a5256630?placeholderIfAbsent=true"
                              alt="Verification"
                              className="object-contain shrink-0 self-stretch my-auto aspect-square w-[18px]"
                            />
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
