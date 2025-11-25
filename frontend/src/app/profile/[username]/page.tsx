/* eslint-disable @next/next/no-img-element */
/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { loadUserProfile } from "@/app/api/src/controllers/userController";
import { updateProfile } from "@/app/api/src/controllers/updateUserController";
import { useCheckTokenValidity } from "@/app/api/src/controllers/authCheckToken";
import getTokenFromCookies from "@/app/api/src/controllers/getTokenFromCookies";
import { useBypassAuth } from "@/app/api/src/hooks/useBypassAuth";
import useUserPosts from "@/app/api/src/hooks/post/useUserPosts";
import {
  Loader2,
  MessageSquare,
  BookmarkIcon,
  MoreHorizontal,
  ArrowUp,
  Activity,
  Users,
  FileText,
  Heart,
  Award,
} from "lucide-react";
import FilePicker from "@/components/ui/FilePicker";
import Sidebar from "@/components/ui/sidebar";
import EditProfileModal from "../components/EditProfileModal";

export interface User {
  id?: string;
  username: string;
  name: string;
  email: string;
  created_at: string;
  bio?: string;
  reputation_level?: string;
  popularity?: number;
  profile_image_url?: string;
}

export default function ProfilePage() {
  const params = useParams();
  const urlParamId = params.username as string;

  const bypass = useBypassAuth();
  const { loading, user: authUser } = useCheckTokenValidity();
  const [user, setUser] = useState<User | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [currentUserId, setCurrentUserId] = useState<string | null>(null);

  const {
    userPosts,
    loading: postsLoading,
    fetchUserPosts,
  } = useUserPosts();

  // 1. Carrega o perfil baseado no ID da URL
  useEffect(() => {
    if (bypass) return;

    const loadUserData = async () => {
      const token = getTokenFromCookies();
      if (!token) return;

      try {
        // CORREÇÃO AQUI: Usamos 'as any' para o TypeScript não reclamar que falta o ID na tipagem original
        let myId = (authUser as any)?.id;

        if (!myId) {
          try {
            // Se não veio no authUser, buscamos via /me (que retorna o objeto completo do controller)
            const myProfile = await loadUserProfile(token);
            // O controller retorna 'any' ou o tipo correto, então aqui costuma funcionar, 
            // mas garantimos com 'as any' caso o controller também não tenha tipagem estrita
            myId = (myProfile as any).id;
            setCurrentUserId(myId);
          } catch (e) {
            console.error("Erro ao obter ID do usuário logado", e);
          }
        } else {
          setCurrentUserId(myId);
        }

        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        console.log(`🔎 Buscando perfil pelo ID: ${urlParamId}`);

        // Rota oficial do backend para buscar por ID
        const response = await fetch(`${apiUrl}/users/user/${urlParamId}`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (response.ok) {
          const profileData = await response.json();

          // Define o usuário da página
          setUser(profileData);

          // Busca os posts desse usuário específico
          await fetchUserPosts(profileData);
        } else {
          console.error(`❌ Usuário não encontrado (ID: ${urlParamId}). Status: ${response.status}`);

          // Se falhar e for o "meu" ID, tenta carregar via loadUserProfile como fallback
          if (myId && urlParamId === myId) {
            const fallbackData = await loadUserProfile(token);
            setUser(fallbackData);
            await fetchUserPosts(fallbackData);
          }
        }

      } catch (err) {
        console.error("Erro ao carregar perfil:", err);
      }
    };

    if (urlParamId) {
      loadUserData();
    }
  }, [bypass, urlParamId, fetchUserPosts, authUser]);

  // 2. Verifica se é o próprio perfil comparando IDs
  const isOwnProfile = currentUserId && user?.id && currentUserId === user.id;

  // 3. Redirecionamento automático se a URL estiver inválida
  useEffect(() => {
    if (currentUserId) {
      // Se não tem ID na URL ou é placeholder, redireciona para o ID do logado
      if (!urlParamId || urlParamId === "[username]" || urlParamId === "%5Busername%5D" || urlParamId === "space") {
        console.log("Redirecionando para URL baseada em ID...");
        window.location.href = `/profile/${currentUserId}`;
      }
    }
  }, [currentUserId, urlParamId]);

  const handleImageChange = (newImageUrl: string) => {
    setUser((prev) =>
      prev ? { ...prev, profile_image_url: newImageUrl } : null
    );
  };

  const handleSaveProfile = async (name: string, bio: string) => {
    const token = getTokenFromCookies();
    if (!token) throw new Error("Token não encontrado");

    try {
      const response = await updateProfile(token, name, bio);
      setUser((prev) =>
        prev ? {
          ...prev,
          name: response.name || name,
          bio: response.bio || bio
        } : null
      );
      return response;
    } catch (error) {
      console.error("Erro ao salvar perfil:", error);
      throw error;
    }
  };

  const reputationLevels = ["Sob observação", "Ajudante", "Colaborador", "Líder"];
  const achievements = [
    { icon: <Users className="h-5 w-5" />, name: "Líder" },
    { icon: <FileText className="h-5 w-5" />, name: "Ativo" },
    { icon: <Heart className="h-5 w-5" />, name: "Amigável" },
    { icon: <Award className="h-5 w-5" />, name: "Efetivo" },
  ];

  const getReputationPercentage = (level?: string) => {
    const index = reputationLevels.indexOf(level || "Sob observação");
    const percentage = ((index + 1) / reputationLevels.length) * 100;
    return percentage;
  };

  const traduzirTipoPost = (tipo?: string) => {
    switch (tipo) {
      case "complaint": return "Denúncia";
      case "poll": return "Enquete";
      case "campaign": return "Campanha";
      case "announcement": return "Anúncio";
      default:
        if (!tipo) return "Publicação";
        return tipo.charAt(0).toUpperCase() + tipo.slice(1);
    }
  };

  if (loading && !bypass) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen text-center px-4">
        <Loader2 className="h-10 w-10 animate-spin text-black mb-4" />
        <h1 className="text-xl font-semibold text-gray-800">Processando...</h1>
        <p className="text-gray-500 mt-2">Você será redirecionado em instantes.</p>
      </div>
    );
  }

  return (
    <div className="flex bg-zinc-100 min-h-screen">
      <Sidebar variant="static" />

      <main className="flex-1 ml-66 max-md:ml-0 overflow-hidden">
        <header className="pt-8 w-full bg-white border border-solid border-stone-300 max-md:pt-4">
          <div className="flex p-4 max-md:flex-col">
            <div className="max-md:ml-0 max-md:w-full">
              <div className="object-contain grow shrink-0 max-w-full aspect-[0.98] w-[180px] max-md:mt-6">
                <FilePicker
                  currentImageUrl={user?.profile_image_url || "/images/default-avatar.png"}
                  onImageChange={handleImageChange}
                  isOwnProfile={!!isOwnProfile}
                />
              </div>
            </div>
            <div className="w-full max-md:ml-0 max-md:w-full">
              <div className="flex flex-wrap gap-10 justify-between items-start p-4 mt-28 w-full max-md:mt-10 max-md:max-w-full">
                <div className="leading-none whitespace-nowrap w-[62px]">
                  <h1 className="text-2xl text-zinc-900">
                    {user?.name || "Carregando..."}
                  </h1>
                  <p className="text-xs text-neutral-500">
                    @{user?.username ? user.username.toLowerCase().replace(/\s+/g, "") : "..."}
                  </p>
                </div>
                <div>
                  {isOwnProfile ? (
                    <button
                      onClick={() => setIsEditModalOpen(true)}
                      className="gap-2.5 self-stretch py-2 pr-16 pl-4 text-base rounded-sm bg-neutral-200 text-neutral-800 hover:bg-neutral-300 transition-colors max-md:pr-5"
                    >
                      Editar perfil
                    </button>
                  ) : (
                    <div className="flex gap-2">
                      <button className="px-4 py-2 bg-neutral-800 text-white hover:bg-neutral-700 transition-colors rounded-sm">
                        Enviar mensagem
                      </button>
                      <button className="gap-2.5 self-stretch py-2 pr-16 pl-4 text-base rounded-sm bg-neutral-200 text-neutral-800 max-md:pr-5">
                        Conectar
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </header>

        <div className="mt-4 max-md:max-w-full">
          <div className="flex gap-5 max-md:flex-col">

            <div className="w-[41%] max-md:ml-0 max-md:w-full">
              <div className="grow max-md:mt-5 max-md:max-w-full">
                <section className="p-4 w-full text-sm bg-white rounded-sm max-md:max-w-full">
                  <div className="max-w-full leading-none w-[300px]">
                    <div className="flex overflow-hidden gap-2 items-center py-2 w-full whitespace-nowrap">
                      <span className="self-stretch my-auto font-medium text-neutral-800">Email:</span>
                      <a href={`mailto:${user?.email}`} className="self-stretch my-auto underline text-neutral-600">
                        {user?.email || "..."}
                      </a>
                    </div>
                    <div className="flex overflow-hidden gap-2 items-center py-2 w-full">
                      <span className="self-stretch my-auto font-medium text-neutral-800">Entrou em:</span>
                      <time className="self-stretch my-auto text-neutral-600">
                        {user ? new Date(user.created_at).toLocaleDateString() : "..."}
                      </time>
                    </div>
                  </div>
                  <div className="mt-4 w-full max-md:max-w-full">
                    <h3 className="font-medium leading-none text-neutral-800 max-md:max-w-full">Biografia:</h3>
                    <p className="mt-2 leading-5 text-justify text-neutral-600 max-md:max-w-full">
                      {user?.bio || "Esse usuário ainda não escreveu uma bio."}
                    </p>
                  </div>
                </section>

                <section className="overflow-hidden p-4 mt-4 w-full bg-white rounded-sm max-md:max-w-full">
                  <div className="w-full max-md:max-w-full">
                    <h3 className="text-xs font-medium leading-none text-zinc-900 max-md:max-w-full">Reputação</h3>
                    <div className="mt-4 w-full text-xs leading-relaxed text-neutral-500 max-md:max-w-full">
                      <div className="flex w-full rounded-sm border border-gray-200 border-solid min-h-2 max-md:max-w-full">
                        <div
                          className="h-full bg-blue-500 rounded-sm"
                          style={{ width: `${getReputationPercentage(user?.reputation_level)}%` }}
                        />
                      </div>
                      <div className="flex flex-col mt-2 w-full max-md:max-w-full">
                        <div className="flex gap-10 justify-center items-center w-full max-md:max-w-full">
                          {reputationLevels.map((level, index) => (
                            <span
                              key={index}
                              className={`self-stretch my-auto ${level === user?.reputation_level ? "text-blue-600 font-medium" : "text-neutral-500"}`}
                            >
                              {level}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="flex flex-col pr-20 mt-16 w-full whitespace-nowrap rounded-none text-zinc-900 max-md:pr-5 max-md:mt-10 max-md:max-w-full">
                    <h4 className="self-start text-xs font-medium leading-none">Popularidade</h4>
                    <p className="self-center mt-6 text-3xl text-center">
                      {user?.popularity?.toLocaleString() || "0"}
                    </p>
                  </div>
                  <div className="flex flex-col mt-16 w-full text-xs leading-none whitespace-nowrap max-md:mt-10 max-md:max-w-full">
                    <h3 className="self-start font-medium text-zinc-900">Conquistas</h3>
                    <div className="flex flex-wrap gap-4 justify-between items-start mt-4 w-full text-neutral-500 max-md:max-w-full">
                      {achievements.map((achievement, index) => (
                        <div key={index} className="flex gap-4 items-center text-center">
                          <div className="object-contain shrink-0 self-stretch my-auto w-6 aspect-square">
                            {achievement.icon}
                          </div>
                          <span className="self-stretch my-auto text-neutral-500">{achievement.name}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </section>
              </div>
            </div>

            <div className="ml-5 w-[59%] max-md:ml-0 max-md:w-full">
              <div className="flex flex-col items-center self-stretch my-auto w-full max-md:mt-10 max-md:max-w-full">
                {postsLoading.posts ? (
                  <div className="flex items-center justify-center py-8">
                    <Loader2 className="h-6 w-6 animate-spin text-gray-500 mr-2" />
                    <span className="text-gray-500">Carregando publicações...</span>
                  </div>
                ) : userPosts.length === 0 ? (
                  <>
                    <p className="text-base text-neutral-500">
                      {isOwnProfile ? "Você ainda não possui nenhuma publicação..." : "Este usuário ainda não possui publicações..."}
                    </p>
                    {isOwnProfile && (
                      <div className="flex gap-8 items-center mt-4 max-w-full text-sm leading-none text-zinc-100 ">
                        <button className="gap-2.5 self-stretch py-2 pr-16 pl-3.5 my-auto rounded-sm bg-neutral-800 text-zinc-100 smax-md:pr-5">
                          Criar publicação
                        </button>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="w-full space-y-4">
                    {userPosts.map((post) => (
                      <article key={post.id} className="bg-white border border-neutral-300 rounded-sm">
                        <div className="p-4 border-b border-neutral-200">
                          <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center gap-3">
                              <div className="w-10 h-10 rounded-full overflow-hidden">
                                <img
                                  src={user?.profile_image_url || "/images/default-avatar.png"}
                                  alt={user?.name || "Perfil"}
                                  className="w-full h-full object-cover"
                                />
                              </div>
                              <div>
                                <div className="flex items-center gap-2">
                                  <span className="font-medium">{user?.name || "Usuário"}</span>
                                  <div className="w-1.5 h-1.5 rounded-full bg-neutral-500"></div>
                                  <span className="text-xs px-2 py-0.5 bg-neutral-800 text-white rounded">
                                    {user?.reputation_level || "Sob observação"}
                                  </span>
                                </div>
                                <div className="flex items-center text-xs text-neutral-500">
                                  <span>{traduzirTipoPost(post.type_post)}</span>
                                  <span className="mx-1">•</span>
                                  <span>{new Date(post.created_at).toLocaleDateString("pt-BR")}</span>
                                </div>
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              <span className="text-xs text-neutral-500">{post.community.name}</span>
                              <button className="p-1 hover:bg-neutral-100 rounded">
                                <BookmarkIcon className="h-5 w-5 text-neutral-500" />
                              </button>
                              <button className="p-1 hover:bg-neutral-100 rounded">
                                <MoreHorizontal className="h-5 w-5 text-neutral-500" />
                              </button>
                            </div>
                          </div>

                          <h2 className="text-xl font-medium mb-2">{post.title}</h2>
                          <p className="text-neutral-800 mb-4">{post.content}</p>

                          {post.image_url && (
                            <div className="mb-4">
                              <img src={post.image_url} alt="Imagem da publicação" className="w-full rounded-md max-h-96 object-cover" />
                            </div>
                          )}

                          <div className="flex items-center gap-6 text-neutral-500">
                            <div className="flex items-center gap-1">
                              <ArrowUp className="h-4 w-4" />
                              <span className="text-sm">{post.likes_count}</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <MessageSquare className="h-4 w-4" />
                              <span className="text-sm">{post.comments_count}</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <Activity className="h-4 w-4" />
                              <span className="text-sm">{post.report_count}</span>
                            </div>
                          </div>
                        </div>
                        {!isOwnProfile && (
                          <div className="p-4 bg-neutral-100">
                            <button className="w-full py-2 bg-neutral-800 text-white hover:bg-neutral-700 transition-colors rounded-sm">
                              Confirmar problema
                            </button>
                          </div>
                        )}
                      </article>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>

      {user && (
        <EditProfileModal
          isOpen={isEditModalOpen}
          onClose={() => setIsEditModalOpen(false)}
          user={user}
          onSave={handleSaveProfile}
        />
      )}
    </div>
  );
}