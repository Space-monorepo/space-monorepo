"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
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
  username?: string;
};

export default function PostList() {
  const [posts, setPosts] = useState<PostDisplay[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [showNoCommunitiesMessage, setShowNoCommunitiesMessage] = useState(false);

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

        const fetchedPosts = feedData.items.map(
          (item: PostResponse): PostDisplay => ({
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
            bookmarked: false,
          })
        );
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
          <article
            key={post.id}
            className="flex flex-col justify-center px-6 py-4 w-full bg-white rounded border-solid shadow-sm border-[0.5px] border-stone-300 max-md:px-5 max-md:max-w-full"
          >
            <div className="w-full max-w-[632px] max-md:max-w-full">
              <div className="w-full max-md:max-w-full">
                <header className="flex flex-wrap gap-10 justify-between items-start w-full max-md:max-w-full">
                  <div className="flex items-start min-w-60">
                    <img
                      src={post.avatar || "/placeholder.svg"}
                      alt={`${post.author} avatar`}
                      className="object-contain shrink-0 w-11 aspect-square rounded-[32px]"
                    />
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
                      onClick={() => toggleBookmark(post.id)}
                      className="p-1 hover:bg-gray-100 rounded-full transition-colors"
                    >
                      <Bookmark
                        className={`h-4 w-4 ${post.bookmarked
                          ? "fill-blue-600 text-blue-600"
                          : "text-gray-500"
                          }`}
                      />
                    </button>
                    <button className="p-1 hover:bg-gray-100 rounded-full transition-colors">
                      <OverflowMenuVertical className="h-4 w-4 text-gray-500" />
                    </button>
                  </div>
                </header>

                <div className="mt-6 w-full text-neutral-800 max-md:max-w-full">
                  <div className="flex flex-wrap gap-10 justify-between items-center w-full max-md:max-w-full">
                    <div className="flex gap-2.5 justify-center items-center self-stretch my-auto text-xl font-bold leading-relaxed min-w-60">
                      <h2 className="self-stretch my-auto text-neutral-800">
                        {post.title}
                      </h2>
                    </div>
                    <div className="flex gap-2 items-center self-stretch px-3 py-1 my-auto text-sm leading-none text-justify whitespace-nowrap rounded-sm">
                      <div className="self-stretch my-auto text-neutral-800">
                        {post.likes + post.comments + post.shares}
                      </div>
                      <Activity className="h-4 w-4 text-gray-500" />
                    </div>
                  </div>

                  {post.content && (
                    <div className="mt-4 text-sm leading-5 text-justify text-neutral-800 max-md:max-w-full whitespace-pre-line">
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
                </div>
              </div>

              <div className="flex justify-between items-center mt-10 w-full text-xs font-medium leading-none text-neutral-500 max-md:max-w-full">
                <div className="flex overflow-hidden gap-8 items-center self-stretch my-auto min-h-5 w-[214px]">
                  <div className="flex overflow-hidden gap-2 items-center self-stretch my-auto text-justify whitespace-nowrap">
                    <ArrowUp className="h-4 w-4 text-gray-500" />
                    <div className="self-stretch my-auto text-neutral-500">
                      {post.likes}
                    </div>
                  </div>
                  <div className="flex overflow-hidden gap-2 items-center self-stretch my-auto text-justify whitespace-nowrap">
                    <MessageSquare className="h-4 w-4 text-gray-500" />
                    <div className="self-stretch my-auto text-neutral-500">
                      {post.comments}
                    </div>
                  </div>
                  <div className="flex overflow-hidden gap-2 items-center self-stretch my-auto text-teal-700">
                    <Activity className="h-4 w-4 text-teal-700" />
                    <div className="self-stretch my-auto">
                      {post.shares}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </article>
        ))}
      </main>
    </div>
  );
}
