"use client";

import { useState, useEffect } from "react";
import Link from "next/link"; // Adicionar importação do Link
import {
  Bookmark,
  EllipsisVerticalIcon as OverflowMenuVertical,
  ArrowUp,
  MessageSquare,
  Activity,
} from "lucide-react";
import { fetchPostsByCommunity } from "@/app/api/src/services/post/postService";
import getTokenFromCookies from "@/app/api/src/controllers/getTokenFromCookies";
import { PostResponse, PostsListFeed } from "@/app/api/src/types/posts/Post";
import { translateUserRole } from "@/lib/roleTranslations";
import { translatePostType } from "@/lib/postTypeTranslations";

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
  bookmarked: boolean;
  username?: string; // Adicionando username para o link do perfil
};

export default function PostList() {
  const [posts, setPosts] = useState<PostDisplay[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [showNoCommunitiesMessage, setShowNoCommunitiesMessage] =
    useState(false); // Novo estado

  useEffect(() => {
    const loadPosts = async () => {
      const token = getTokenFromCookies();
      if (!token) {
        setError(new Error("Usuário não autenticado."));
        setLoading(false);
        return;
      }

      try {
        const communityId = "default-community-id"; // SUBSTITUA PELO ID DA COMUNIDADE REAL
        const feedData: PostsListFeed = await fetchPostsByCommunity(
          token,
          communityId
        );        const fetchedPosts = feedData.items.map(
          (item: PostResponse): PostDisplay => ({
            ...item,
            author: item.user.name,
            username: item.user.username || item.user.id, // Usar username se disponível, senão usar ID
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
            //TODO: ajustar para pegar os opçoes de enquete
            image: item.image_url || "/publication-image.jpg",
            likes: item.likes_count,
            comments: item.comments_count,
            shares: item.report_count, // Ajuste se necessário
            bookmarked: false, // Gerenciar localmente ou obter do backend
          })
        );
        setPosts(fetchedPosts);
        if (fetchedPosts.length === 0) {
          setShowNoCommunitiesMessage(true); // Mostrar mensagem se não houver posts
        }
      } catch (err) {
        setError(err as Error);
        console.error("Erro ao buscar posts:", err);
      } finally {
        setLoading(false);
      }
    };

    loadPosts();
  }, []);

  const toggleBookmark = (id: string) => {
    setPosts(
      posts.map((post) =>
        post.id === id ? { ...post, bookmarked: !post.bookmarked } : post
      )
    );
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
        {" "}
        {/* Adicionado w-full */}
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
      <div className="w-full max-w-2xl space-y-4">
        {posts.map((post) => (
          <div
            key={post.id}
            className="bg-white rounded-md border border-[#e0e0e0] overflow-hidden"
          >
            <div className="p-4">
              {/* Post Header */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full overflow-hidden">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={post.avatar || "/placeholder.svg"} // Usar post.avatar
                      alt={post.author} // Usar post.author
                      className="w-full h-full object-cover"
                    />
                  </div>{" "}
                  <div>
                    {" "}                    <div className="flex items-center gap-2">
                      <Link
                        href={`/profile/${post.username || post.user.id}`}
                        className="font-medium text-[#161616] hover:text-[#0f62fe] cursor-pointer transition-colors hover:underline"
                      >
                        {post.author}
                      </Link>{" "}
                      {/* Nome do usuário clicável */}
                      <div className="w-1.5 h-1.5 rounded-full bg-[#525252]"></div>
                      <span className="text-xs px-2 py-0.5 bg-[#393939] text-white rounded">
                        {post.role}
                      </span>{" "}
                      {/* Usar post.role */}
                    </div>
                    <div className="flex items-center text-xs text-[#525252]">
                      <span>{post.type}</span> {/* Usar post.type */}
                      <span className="mx-1">•</span>
                      <span>{post.time}</span> {/* Usar post.time */}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-[#525252]">
                    {post.location}
                  </span>{" "}
                  {/* Usar post.location */}
                  <button
                    onClick={() => toggleBookmark(post.id)}
                    className="p-1 hover:bg-[#f4f4f4] rounded-full"
                  >
                    <Bookmark
                      className={`h-5 w-5 ${
                        post.bookmarked
                          ? "fill-[#0f62fe] text-[#0f62fe]"
                          : "text-[#525252]"
                      }`} // Usar post.bookmarked
                    />
                  </button>
                  <button className="p-1 hover:bg-[#f4f4f4] rounded-full">
                    <OverflowMenuVertical className="h-5 w-5 text-[#525252]" />
                  </button>
                </div>
              </div>

              {/* Post Content */}
              <div className="mt-4">
                <h2 className="text-xl font-medium mb-2">{post.title}</h2>
                <p className="text-[#161616] whitespace-pre-line">
                  {post.content}
                </p>
                {post.image && ( // Usar post.image
                  <div className="mt-4">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={post.image || "/placeholder.svg"}
                      alt="Post image"
                      className="w-full rounded"
                    />{" "}
                    {/* Usar post.image */}
                  </div>
                )}
              </div>

              {/* Post Actions */}
              <div className="flex items-center gap-6 mt-4 text-[#525252]">
                <div className="flex items-center gap-1">
                  <ArrowUp className="h-4 w-4" />
                  <span className="text-sm">{post.likes}</span>{" "}
                  {/* Usar post.likes */}
                </div>
                <div className="flex items-center gap-1">
                  <MessageSquare className="h-4 w-4" />
                  <span className="text-sm">{post.comments}</span>{" "}
                  {/* Usar post.comments */}
                </div>
                <div className="flex items-center gap-1">
                  <Activity className="h-4 w-4" />
                  <span className="text-sm">{post.shares}</span>{" "}
                  {/* Usar post.shares */}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
