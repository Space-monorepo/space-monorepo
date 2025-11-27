/* eslint-disable @next/next/no-img-element */
/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import { useParams } from "next/navigation";
import { useEffect, useState, useCallback } from "react";
import { toast } from "react-toastify";
import { loadUserProfile } from "@/app/api/src/controllers/userController";
import { updateProfile } from "@/app/api/src/controllers/updateUserController";
import { useCheckTokenValidity } from "@/app/api/src/controllers/authCheckToken";
import getTokenFromCookies from "@/app/api/src/controllers/getTokenFromCookies";
import { useBypassAuth } from "@/app/api/src/hooks/useBypassAuth";
import useUserPosts from "@/app/api/src/hooks/post/useUserPosts";
import usePostActions from "@/app/api/src/hooks/post/usePostActions";
import { useCampaignParticipation } from "@/app/api/src/hooks/post/useCampaignParticipation";
import useReportPost from "@/app/api/src/hooks/post/useReportPost";
import { confirmComplaint } from "@/app/api/src/services/post/postService";
import { translatePostType } from "@/lib/postTypeTranslations";
import { translateUserRole } from "@/lib/roleTranslations";
import { getRelativeTime } from "@/lib/relativeTime";
import getRoleBadgeClasses from "@/components/badges/users/RoleBadgesClasses";
import getCheckmarkColorClass from "@/components/badges/users/CheckmarkColorClasses";
import { Loader2, Activity, Award } from "lucide-react";
import { CheckmarkFilled, Forum, OverflowMenuHorizontal, ArrowUp } from "@carbon/icons-react";
import FilePicker from "@/components/ui/FilePicker";
import Sidebar from "@/components/ui/sidebar";
import EditProfileModal from "../components/EditProfileModal";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { getConnectionStatus, requestConnection, deleteConnection } from "@/app/api/src/services/connection/connectionService";
import { API_URL } from "@/config";

// --- Interfaces ---
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

// --- Configuração dos Níveis de Reputação ---
const levels = [
  { label: "Sob observação", min: 0, max: 2500 },
  { label: "Ajudante", min: 2501, max: 5000 },
  { label: "Colaborador", min: 5001, max: 7500 },
  { label: "Líder", min: 7501, max: 10000 },
];

const isUuid = (value: string) =>
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(value);

export default function ProfilePage() {
  const params = useParams();
  const urlParamId = (params?.username ?? "") as string;

  const bypass = useBypassAuth();
  const { loading, user: authUser } = useCheckTokenValidity();

  const [user, setUser] = useState<User | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [currentUserId, setCurrentUserId] = useState<string | null>(null);

  // Estados para Reputação
  const [averageReputation, setAverageReputation] = useState<number>(0);
  const [communitiesCount, setCommunitiesCount] = useState<number>(0);

  const [badges, setBadges] = useState<any[]>([]);
  const [totalPopularity, setTotalPopularity] = useState<number>(0);

  const {
    userPosts,
    loading: postsLoading,
    fetchUserPosts,
  } = useUserPosts();

  // Estado para posts com likes
  const [postsWithLikes, setPostsWithLikes] = useState<Map<string, boolean>>(new Map());
  const [openMenuPostId, setOpenMenuPostId] = useState<string | null>(null);
  const [openCommentsPostId, setOpenCommentsPostId] = useState<string | null>(null);
  const [confirmedProblems, setConfirmedProblems] = useState<{ [key: string]: boolean }>({});

  // Estados para Conexão
  const [connectionStatus, setConnectionStatus] = useState<any>(null);
  const [loadingConnection, setLoadingConnection] = useState(false);
  const [showDisconnectModal, setShowDisconnectModal] = useState(false);

  // Hooks para ações com posts
  const { likePost, unlikePost } = usePostActions();
  const { participate, checkParticipation, participating: campaignParticipation } = useCampaignParticipation();
  const { reportPost } = useReportPost();

  const router = useRouter();

  // Helper para saber qual nível está ativo
  const getCurrentLevel = (points: number) => {
    return levels.find(l => points >= l.min && points <= l.max) || levels[0];
  };

  // 1. Carrega o perfil baseado no ID da URL
  useEffect(() => {
    if (bypass) return;

    const loadUserData = async () => {
      const token = getTokenFromCookies();

      try {
        let myId = (authUser as any)?.id;

        if (!myId) {
          try {
            const tokenString = token ?? "";
            const myProfile = await loadUserProfile(tokenString);
            myId = (myProfile as any).id;
            setCurrentUserId(myId);
          } catch (e) {
            console.error("Erro ao obter ID do usuário logado", e);
          }
        } else {
          setCurrentUserId(myId);
        }

        // Usar API_URL configurado
        console.log(`🔎 Buscando perfil pelo ID: ${urlParamId} na API ${API_URL}`);

        // Prepare headers, include Authorization only if token exists
        const headers: any = {
          'Content-Type': 'application/json',
        };
        if (token) {
          headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(`${API_URL}/users/user/${urlParamId}`, {
          method: 'GET',
          headers,
        });

        if (response.ok) {
          const profileData = await response.json();
          setUser(profileData);
          await fetchUserPosts(profileData);
        } else {
          console.error(`❌ Usuário não encontrado (ID: ${urlParamId}). Status: ${response.status}`);
          if (myId && urlParamId === myId) {
            const tokenString = token ?? "";
            const fallbackData = await loadUserProfile(tokenString);
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

  // 2. Calcula a Média de Reputação
  useEffect(() => {
    const loadCommunityData = async () => {
      if (!user?.id) return;

      const token = getTokenFromCookies();
      const headers: any = {
        'Content-Type': 'application/json'
      };
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      try {
        // 1. Buscar as comunidades que o usuário participa
        const communitiesResponse = await fetch(
          `${API_URL}/communities/user/${user.id}/communities?offset=0&limit=100`,
          { headers }
        );

        if (!communitiesResponse.ok) {
          console.error(`Erro ao buscar comunidades: ${communitiesResponse.status}`);
          setCommunitiesCount(0);
          setAverageReputation(0);
          setTotalPopularity(0);
          setBadges([]);
          return;
        }

        const communitiesData = await communitiesResponse.json();
        const communities = Array.isArray(communitiesData) ? communitiesData : (communitiesData.items || []);

        setCommunitiesCount(communities.length);

        if (communities.length > 0) {
          // 2. Para cada comunidade, buscar os membros para encontrar o membro do usuário
          const membershipPromises = communities.map((community: any) =>
            fetch(`${API_URL}/communities/${community.id}/members?offset=0&limit=100`, { headers })
              .then(res => res.ok ? res.json() : null)
              .catch(() => null)
          );

          const membershipsResults = await Promise.all(membershipPromises);

          // 3. Filtrar apenas os memberships do usuário atual
          const myMemberships: any[] = [];
          membershipsResults.forEach((result) => {
            if (result?.items) {
              const userMember = result.items.find((m: any) => m.user?.id === user.id);
              if (userMember) {
                myMemberships.push(userMember);
              }
            }
          });

          if (myMemberships.length > 0) {
            // 4. Calcular Reputação Média
            const sumReputation = myMemberships.reduce((acc: number, item: any) => acc + (item.reputation || 0), 0);
            setAverageReputation(Math.floor(sumReputation / myMemberships.length));

            // 5. Calcular Popularidade Total
            const sumPopularity = myMemberships.reduce((acc: number, item: any) => acc + (item.popularity || 0), 0);
            setTotalPopularity(sumPopularity);

            // 6. Buscar Badges para cada membership
            const badgePromises = myMemberships.map((member: any) =>
              fetch(`${API_URL}/badges/member/${member.id}`, { headers })
                .then(res => res.ok ? res.json() : [])
                .catch(() => [])
            );

            const badgeResults = await Promise.all(badgePromises);
            const allBadges = badgeResults.flat();
            setBadges(allBadges);
          } else {
            setAverageReputation(0);
            setTotalPopularity(0);
            setBadges([]);
          }
        }
      } catch (error) {
        console.error("Erro ao carregar dados de comunidade:", error);
        setAverageReputation(0);
        setTotalPopularity(0);
        setBadges([]);
      }
    };

    loadCommunityData();
  }, [user?.id]);

  useEffect(() => {
    if (!currentUserId || !urlParamId) return;

    const shouldRedirectToId =
      !isUuid(urlParamId) &&
      (
        urlParamId === "[username]" ||
        urlParamId === "%5Busername%5D" ||
        urlParamId === "space" ||
        urlParamId === (authUser as any)?.username
      );

    if (shouldRedirectToId) {
      router.replace(`/profile/${currentUserId}`);
    }
  }, [currentUserId, urlParamId, authUser, router]);

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

  const handleLikePost = useCallback(async (post: any) => {
    const communityId = post.community?.id;
    if (!communityId) return;

    try {
      const isLiked = postsWithLikes.get(post.id) || false;
      if (!isLiked) {
        await likePost(communityId, post.id);
        setPostsWithLikes(prev => new Map(prev).set(post.id, true));
      } else {
        await unlikePost(communityId, post.id);
        setPostsWithLikes(prev => new Map(prev).set(post.id, false));
      }
    } catch (err) {
      console.error('Erro ao curtir/descurtir post:', err);
    }
  }, [postsWithLikes, likePost, unlikePost]);

  const handleComment = (postId: string) => {
    setOpenCommentsPostId((prev) => (prev === postId ? null : postId));
  };

  const checkProblemConfirmation = useCallback(async (postId: string, communityId: string) => {
    try {
      const token = getTokenFromCookies();
      if (!token) {
        return false;
      }

      const response = await fetch(`${API_URL}/communities/${communityId}/complaints/${postId}`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        return false;
      }

      const data = await response.json();
      const currentUserId = JSON.parse(atob(token.split('.')[1])).sub;
      return data.confirmations?.some((confirmation: any) => confirmation.user_id === currentUserId) ?? false;
    } catch (error) {
      console.error('Erro ao verificar confirmação do problema:', error);
      return false;
    }
  }, []);

  const handleConfirmComplaint = useCallback(async (post: any) => {
    try {
      const token = getTokenFromCookies();
      const communityId = post.community?.id;

      if (!communityId) {
        toast.error('ID da comunidade não encontrado');
        return;
      }

      if (post.user?.id && post.user.id === currentUserId) {
        toast.info('Você não pode confirmar um problema que criou.');
        return;
      }

      if (!confirmedProblems[post.id]) {
        await confirmComplaint(communityId, post.id, token ?? undefined);
        setConfirmedProblems((prev) => ({ ...prev, [post.id]: true }));
        toast.success('Confirmação registrada!');
      } else {
        toast.info('Você já confirmou este problema.');
      }
    } catch {
      toast.error('Erro ao confirmar problema');
    }
  }, [confirmedProblems, currentUserId]);

  const handleParticipate = useCallback(async (post: any) => {
    const communityId = post.community?.id;
    if (!communityId) {
      toast.error('ID da comunidade não encontrado');
      return;
    }

    if (post.user?.id && post.user.id === currentUserId) {
      toast.info('Você não pode participar da própria campanha.');
      return;
    }

    if (campaignParticipation[post.id]) {
      toast.info('Você já participa desta campanha.');
      return;
    }

    try {
      await participate(communityId, post.id);
      toast.success('Você agora faz parte da campanha!');
    } catch {
      toast.error('Erro ao participar da campanha');
    }
  }, [participate, campaignParticipation, currentUserId]);

  useEffect(() => {
    let isCancelled = false;

    const initializePostStates = async () => {
      const confirmedMap: Record<string, boolean> = {};

      for (const post of userPosts) {
        const communityId = post.community?.id;
        if (!communityId) continue;

        const postType = translatePostType(post.type_post || '');

        if (postType === 'Denúncia') {
          confirmedMap[post.id] = await checkProblemConfirmation(post.id, communityId);
        }

        if (postType === 'Campanha') {
          await checkParticipation(communityId, post.id);
        }
      }

      if (!isCancelled) {
        setConfirmedProblems(confirmedMap);
      }
    };

    if (userPosts.length > 0) {
      initializePostStates();
    } else {
      setConfirmedProblems({});
    }

    return () => {
      isCancelled = true;
    };
  }, [userPosts, checkProblemConfirmation, checkParticipation]);

  // 3. Carrega status de conexão com o usuário visitado
  useEffect(() => {
    if (bypass || !user?.id || !currentUserId || currentUserId === user.id) {
      // Se é o próprio perfil, não carregar conexão
      setConnectionStatus(null);
      return;
    }

    const loadConnectionStatus = async () => {
      const token = getTokenFromCookies();
      if (!token) return;

      setLoadingConnection(true);
      try {
        const status = await getConnectionStatus(token, user.id || '');
        setConnectionStatus(status);
      } catch (error) {
        console.error('Erro ao carregar status de conexão:', error);
        setConnectionStatus(null);
      } finally {
        setLoadingConnection(false);
      }
    };

    loadConnectionStatus();
  }, [user?.id, currentUserId, bypass]);

  // Helper para definir se é próprio perfil
  const isOwnProfile = currentUserId && user?.id && currentUserId === user.id;

  // Handler para enviar pedido de conexão
  const handleSendConnectionRequest = async () => {
    const token = getTokenFromCookies();
    if (!token || !user?.id) {
      toast.error('Erro: Usuário não encontrado');
      return;
    }

    setLoadingConnection(true);
    try {
      await requestConnection(token, user.id);
      setConnectionStatus({ status: 'pending', addressee_id: user.id });
      toast.success('Pedido de conexão enviado!');
    } catch (error: any) {
      toast.error(error.message || 'Erro ao enviar pedido de conexão');
    } finally {
      setLoadingConnection(false);
    }
  };

  // Handler para enviar mensagem - Navega para página de mensagens com userId e userName
  const handleSendMessage = () => {
    if (!user?.id) return;
    // Passa userId e userName como parâmetros para a página de mensagens
    const params = new URLSearchParams({
      userId: user.id,
      userName: user.name || user.username,
    });
    router.push(`/messages?${params.toString()}`);
  };

  // Handler para desconectar
  const handleDisconnect = async () => {
    const token = getTokenFromCookies();
    if (!token || !connectionStatus?.id) {
      toast.error('Erro: Conexão não encontrada');
      return;
    }

    setLoadingConnection(true);
    try {
      await deleteConnection(token, connectionStatus.id);
      setConnectionStatus(null);
      setShowDisconnectModal(false);
      toast.success('Conexão encerrada');
    } catch (error: any) {
      toast.error(error.message || 'Erro ao encerrar conexão');
    } finally {
      setLoadingConnection(false);
    }
  };

  if (loading && !bypass) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen text-center px-4">
        <Loader2 className="h-10 w-10 animate-spin text-black mb-4" />
        <h1 className="text-xl font-semibold text-gray-800">Processando...</h1>
      </div>
    );
  }

  return (
    <div className="flex bg-zinc-100 min-h-screen">
      <Sidebar variant="static" />

      <main className="flex-1 ml-0 min-[900px]:ml-64 overflow-hidden">
        <header className="pt-8 w-full bg-white border border-solid border-stone-300 max-md:pt-4">
          <div className="flex p-4 max-md:flex-col">
            <div className="max-md:ml-0 max-md:w-full">
              <div className="object-contain grow shrink-0 max-w-full aspect-[0.98] w-[180px] max-md:mt-6">
                {isOwnProfile ? (
                  <FilePicker
                    currentImageUrl={user?.profile_image_url || "/no-profile-pic.png"}
                    onImageChange={handleImageChange}
                    isOwnProfile={true}
                  />
                ) : (
                  <div className="w-full h-full rounded-full overflow-hidden border border-gray-200 bg-gray-100">
                    <img
                      src={user?.profile_image_url || "/no-profile-pic.png"}
                      alt={user?.name || "Foto de perfil"}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        const target = e.target as HTMLImageElement;
                        target.src = "/no-profile-pic.png";
                      }}
                    />
                  </div>
                )}
              </div>
            </div>
            <div className="w-full max-md:ml-0 max-md:w-full">
              <div className="flex flex-wrap gap-10 justify-between items-start p-4 mt-28 w-full max-md:mt-10 max-md:max-w-full">
                <div className="leading-none whitespace-nowrap w-[62px]">
                  <h1 className="text-2xl text-zinc-900">
                    {user?.name || "Carregando..."}
                  </h1>
                  <p className="text-xs text-neutral-500">
                    @{user?.name ? user.name.toLowerCase().replace(/\s+/g, "") : "..."}
                  </p>
                </div>
                <div>
                  {isOwnProfile ? (
                    <button
                      onClick={() => setIsEditModalOpen(true)}
                      className="gap-2.5 self-stretch cursor-pointer py-2 pr-16 pl-4 text-base rounded-sm bg-neutral-200 text-neutral-800 hover:bg-neutral-300 transition-colors max-md:pr-5"
                    >
                      Editar perfil
                    </button>
                  ) : (
                    <div className="flex gap-2">
                      {connectionStatus?.status === 'accepted' ? (
                        <>
                          <button
                            onClick={handleSendMessage}
                            disabled={loadingConnection}
                            className="px-4 py-2 bg-neutral-800 text-white hover:bg-neutral-700 transition-colors rounded-sm disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            {loadingConnection ? 'Carregando...' : 'Enviar mensagem'}
                          </button>
                          <button
                            onClick={() => setShowDisconnectModal(true)}
                            disabled={loadingConnection}
                            className="gap-2.5 self-stretch py-2 pr-16 pl-4 text-base rounded-sm bg-neutral-200 text-neutral-800 hover:bg-neutral-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed max-md:pr-5"
                          >
                            Conectado
                          </button>
                        </>
                      ) : connectionStatus?.status === 'pending' ? (
                        <button
                          disabled={true}
                          className="px-4 py-2 bg-neutral-200 text-neutral-800 rounded-sm cursor-not-allowed"
                        >
                          Pedido enviado
                        </button>
                      ) : (
                        <button
                          onClick={handleSendConnectionRequest}
                          disabled={loadingConnection}
                          className="px-4 py-2 bg-neutral-800 text-white hover:bg-neutral-700 transition-colors rounded-sm disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {loadingConnection ? 'Enviando...' : 'Conectar-se'}
                        </button>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </header>

        <div className="mt-4 max-md:max-w-full">
          <div className="flex gap-5 max-md:flex-col">

            {/* Coluna Esquerda */}
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
                    <h3 className="text-base font-medium leading-none text-zinc-900 max-md:max-w-full mb-4">
                      Reputação
                      <span className="ml-2 text-xs font-normal text-gray-500">
                        ({communitiesCount} comunidades)
                      </span>
                    </h3>

                    <div className="w-full relative px-1 mb-6">
                      <div className="w-full h-3 rounded-full bg-gradient-to-r from-gray-200 via-emerald-400 to-emerald-900 shadow-inner" />

                      <div
                        className="absolute top-3 transition-all duration-1000 ease-out flex flex-col items-center"
                        style={{
                          left: `calc(${Math.min((averageReputation / 10000) * 100, 100)}% - 6px)`
                        }}
                      >
                        <div className="w-0 h-0 border-l-[6px] border-l-transparent border-r-[6px] border-r-transparent border-b-[8px] border-b-black mt-1" />
                      </div>

                      <div className="flex justify-between mt-4 text-xs text-neutral-500 w-full">
                        {levels.map((level, index) => {
                          const isActive = getCurrentLevel(averageReputation).label === level.label;
                          return (
                            <span
                              key={index}
                              className={`${isActive ? "text-black font-bold" : "text-gray-400"} text-center flex-1`}
                            >
                              {level.label}
                            </span>
                          );
                        })}
                      </div>
                    </div>
                  </div>

                  <div className="flex flex-col pr-20 mt-8 w-full whitespace-nowrap rounded-none text-zinc-900 max-md:pr-5 max-md:mt-10 max-md:max-w-full">
                    <h4 className="self-start text-xs font-medium leading-none">Popularidade</h4>
                    <p className="self-center mt-6 text-3xl text-center">
                      {totalPopularity.toLocaleString()}
                    </p>
                  </div>
                  <div className="flex flex-col mt-16 w-full text-xs leading-none whitespace-nowrap max-md:mt-10 max-md:max-w-full">
                    <h3 className="self-start font-medium text-zinc-900">
                      Conquistas ({badges.length})
                    </h3>

                    {badges.length > 0 ? (
                      <div className="flex flex-wrap gap-4 justify-start items-start mt-4 w-full text-neutral-500">
                        {badges.map((badge, index) => (
                          <div key={badge.id || index} className="flex gap-2 items-center bg-gray-100 p-2 rounded-md" title={badge.description}>
                            <div className="object-contain w-6 h-6">
                              {/* Verifica se a badge tem imagem, senão usa ícone padrão */}
                              {badge.image_url ? (
                                <img src={badge.image_url} alt={badge.name} className="w-full h-full object-contain" />
                              ) : (
                                <Award className="h-5 w-5 text-amber-500" />
                              )}
                            </div>
                            <span className="text-neutral-700 font-medium">{badge.name}</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="mt-4 text-gray-400 italic">Nenhuma conquista ainda.</p>
                    )}
                  </div>
                </section>
              </div>
            </div>

        <div className="ml-5 flex-1 max-w-3xl w-full max-md:ml-0 max-md:w-full">
          <div className="flex flex-col items-center self-stretch my-auto w-full max-w-3xl mx-auto pr-6 max-md:mt-10 max-md:max-w-full max-md:pr-0">
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
              <div className="w-full max-w-2xl space-y-6 mx-auto pr-4 max-md:pr-0">
                    {userPosts.map((post) => {
                      const isPostLiked = postsWithLikes.get(post.id) || false;
                      const roleClass = getRoleBadgeClasses(post.user?.role || '');
                      const checkmarkClass = getCheckmarkColorClass(post.user?.role || '');
                      const postType = translatePostType(post.type_post || '');
                      const postTime = getRelativeTime(post.created_at);
                      const isParticipating = !!campaignParticipation[post.id];
                      const hasConfirmedProblem = !!confirmedProblems[post.id];

                      // Debug para enquetes
                      if (postType === 'Enquete') {
                        console.log(`📊 [PROFILE POLL DEBUG] Post "${post.title}":`, {
                          type: postType,
                          poll_question: post.poll_question,
                          poll_options_count: Array.isArray(post.poll_options) ? post.poll_options.length : 0,
                          poll_options: post.poll_options
                        });
                      }

                      return (
                        <article
                          key={post.id}
                          className="flex flex-col justify-center px-6 py-4 w-full bg-white rounded border-solid shadow-sm border-[0.5px] border-stone-300"
                        >
                          <div className="w-full">
                            <div className="w-full">
                              <header className="flex flex-wrap gap-10 justify-between items-start w-full">
                                <div className="flex items-start min-w-60">
                                  <div className="w-11 h-11 rounded-[32px] overflow-hidden shrink-0 flex items-center justify-center bg-neutral-200">
                                    <img
                                      src={(post.user as any)?.profile_image_url || (post.user as any)?.profile_picture || "/no-profile-pic.png"}
                                      alt={`${post.user?.name} avatar`}
                                      className="object-cover w-full h-full"
                                    />
                                  </div>
                                  <div className="flex flex-col min-w-60 w-[342px]">
                                    <div className="flex gap-2 items-center w-full h-[23px]">
                                      <div className="flex overflow-hidden gap-2.5 justify-center items-center self-stretch px-3 my-auto">
                                        <Link
                                          href={`/profile/${post.user?.id || post.user?.username}`}
                                          className="self-stretch my-auto text-sm text-neutral-800 hover:text-blue-600 whitespace-nowrap transition-colors hover:underline"
                                        >
                                          {post.user?.name}
                                        </Link>
                                        <CheckmarkFilled
                                          className={`object-contain shrink-0 self-stretch my-auto aspect-square w-[18px] ${checkmarkClass}`}
                                          aria-label="Verificado"
                                        />
                                        <div className="self-stretch my-auto text-[10px] font-semibold">
                                          •
                                        </div>
                                        <div className={`flex gap-2.5 justify-center items-center self-stretch px-3 py-1 my-auto text-xs whitespace-nowrap rounded ${roleClass}`}>
                                          <div className="self-stretch my-auto">
                                            {translateUserRole(post.user?.role || '')}
                                          </div>
                                        </div>
                                      </div>
                                      <div className="self-stretch my-auto text-xs leading-none text-justify whitespace-nowrap text-neutral-800">
                                        {post.community?.name}
                                      </div>
                                    </div>
                                    <div className="self-start px-3 mt-2 text-xs font-semibold tracking-normal whitespace-nowrap text-neutral-500">
                                      <div className="flex items-center gap-1">
                                        <div className="self-stretch my-auto text-neutral-500">
                                          {postType}
                                        </div>
                                        <div className="self-stretch my-auto text-[10px] text-neutral-500">
                                          •
                                        </div>
                                        <div className="self-stretch my-auto text-neutral-500">
                                          {postTime}
                                        </div>
                                      </div>
                                    </div>
                                  </div>
                                </div>
                                <div className="flex gap-4 items-center">
                                  <div className="relative">
                                    <button
                                      className="p-1 hover:bg-gray-100 rounded-full cursor-pointer transition-colors"
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        setOpenMenuPostId(openMenuPostId === post.id ? null : post.id);
                                      }}
                                      aria-label="Mais opções"
                                    >
                                      <OverflowMenuHorizontal className="h-4 w-4 text-gray-500" />
                                    </button>
                                    {openMenuPostId === post.id && (
                                      <div
                                        className="absolute right-0 z-20 mt-2 w-40 bg-white border border-gray-200 rounded shadow-lg"
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
                                                toast.error('ID da comunidade não encontrado');
                                                return;
                                              }
                                              await reportPost(communityId, post.id);
                                            } catch (error) {
                                              console.error(error);
                                            }
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
                                      {(post.likes_count || 0) + (post.comments_count || 0) + (post.report_count || 0)}
                                    </div>
                                    <Activity className="h-4 w-4 text-gray-500" />
                                  </div>
                                </div>

                                {post.content && (
                                  <div
                                    className="mt-4 text-sm leading-5 text-justify text-neutral-800 max-md:max-w-full whitespace-pre-line font-regular break-words w-full max-w-full cursor-pointer"
                                    style={{ wordBreak: 'break-word', overflowWrap: 'break-word', whiteSpace: 'pre-line' }}
                                  >
                                    {post.content}
                                  </div>
                                )}

                                {post.image_url && (
                                  <img
                                    src={post.image_url}
                                    alt="Post content"
                                    className="object-contain mt-4 w-full rounded aspect-[2.26] max-md:max-w-full"
                                  />
                                )}

                                {/* Opções de Enquete */}
                                {postType === 'Enquete' && (post.poll_question || (Array.isArray(post.poll_options) && post.poll_options.length > 0)) && (
                                  <div className="mt-6 w-full">
                                    {post.poll_question && (
                                      <h3 className="text-base font-semibold text-neutral-800 mb-6">
                                        {post.poll_question}
                                      </h3>
                                    )}
                                    {Array.isArray(post.poll_options) && post.poll_options.length > 0 && (
                                      <>
                                        {(() => {
                                          const totalVotes = post.poll_options.reduce((sum, opt) => sum + (opt.votes_count || 0), 0);
                                          return post.poll_options.map((option) => {
                                            const percent = totalVotes > 0 ? Math.round(((option.votes_count || 0) / totalVotes) * 100) : 0;
                                            return (
                                              <div
                                                key={`${option.id}-${option.votes_count}`}
                                                className="mb-4 cursor-pointer hover:opacity-80 transition-opacity"
                                              >
                                                <button
                                                  className="w-full text-left bg-transparent border-none outline-none p-0 m-0 cursor-pointer"
                                                  onClick={(e) => {
                                                    e.stopPropagation();
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
                                                      {option.votes_count || 0} {(option.votes_count || 0) === 1 ? 'voto' : 'votos'}
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
                                      </>
                                    )}
                                  </div>
                                )}

                                {/* Botão Participar da Campanha */}
                                {postType === 'Campanha' && (
                                  <button
                                    className={`mt-4 w-full py-2 px-4 text-left font-regular transition-colors ${isParticipating ? 'bg-neutral-200 text-neutral-700 cursor-not-allowed' : 'cursor-pointer bg-neutral-900 text-white hover:bg-neutral-800'}`}
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      if (!isParticipating) {
                                        handleParticipate(post);
                                      }
                                    }}
                                    disabled={isParticipating}
                                  >
                                    {isParticipating ? 'Já participa da campanha' : 'Participar da Campanha'}
                                  </button>
                                )}

                                {/* Botão Confirmar problema para Denúncia */}
                                {postType === 'Denúncia' && (
                                  <button
                                    className={`mt-4 w-full py-2 px-4 text-left font-regular transition-colors ${hasConfirmedProblem ? 'bg-neutral-200 text-neutral-700 cursor-not-allowed' : 'bg-neutral-900 text-white hover:bg-neutral-800'}`}
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      if (!hasConfirmedProblem) {
                                        handleConfirmComplaint(post);
                                      }
                                    }}
                                    disabled={hasConfirmedProblem}
                                  >
                                    {hasConfirmedProblem ? 'Problema confirmado' : 'Confirmar problema'}
                                  </button>
                                )}
                              </div>
                            </div>

                            <div className="flex justify-between items-center mt-10 w-full text-xs font-medium leading-none text-neutral-500 max-md:max-w-full">
                              <div className="flex overflow-hidden gap-8 items-center self-stretch my-auto min-h-5 w-[214px]">
                                <button
                                  className="flex overflow-hidden gap-2 items-center self-stretch my-auto text-justify whitespace-nowrap cursor-pointer hover:text-neutral-700 transition-colors"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleLikePost(post);
                                  }}
                                  title="Curtir"
                                >
                                  <ArrowUp className={`h-4 w-4 ${isPostLiked ? 'text-red-500' : 'text-gray-500'}`} />
                                  <div className={isPostLiked ? 'text-red-500' : 'text-neutral-500'}>
                                    {post.likes_count || 0}
                                  </div>
                                </button>
                                <button
                                  className={`flex overflow-hidden gap-2 items-center self-stretch my-auto text-justify whitespace-nowrap transition-colors px-3 py-1 cursor-pointer ${openCommentsPostId === post.id ? 'bg-neutral-200' : ''}`}
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleComment(post.id);
                                  }}
                                  title="Comentar"
                                >
                                  <Forum className={`h-4 w-4 ${openCommentsPostId === post.id ? 'text-black' : 'text-gray-500'}`} />
                                  <div className={openCommentsPostId === post.id ? 'text-black' : 'text-neutral-500'}>
                                    {post.comments_count || 0}
                                  </div>
                                </button>
                                <button
                                  className="flex overflow-hidden gap-2 items-center self-stretch my-auto text-teal-700 cursor-pointer hover:text-teal-600 transition-colors"
                                  title="Compartilhar"
                                >
                                  <Activity className="h-4 w-4 text-teal-700" />
                                  <div>
                                    {post.report_count || 0}
                                  </div>
                                </button>
                              </div>
                            </div>
                          </div>
                        </article>
                      );
                    })}
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

      {/* Modal de Desconexão */}
      {showDisconnectModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg p-6 max-w-sm">
            <div className="flex items-center gap-3 mb-4">
              <h2 className="text-lg font-semibold text-neutral-900">Encerrar conexão</h2>
            </div>
            <p className="text-neutral-600 mb-6">
              Você tem certeza que deseja encerrar a conexão com {user?.name}? Isso impedirá que você envie mensagens.
            </p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowDisconnectModal(false)}
                disabled={loadingConnection}
                className="px-4 py-2 bg-neutral-200 text-neutral-800 hover:bg-neutral-300 transition-colors rounded-sm disabled:opacity-50"
              >
                Cancelar
              </button>
              <button
                onClick={handleDisconnect}
                disabled={loadingConnection}
                className="px-4 py-2 bg-red-600 text-white hover:bg-red-700 transition-colors rounded-sm disabled:opacity-50"
              >
                {loadingConnection ? 'Encerrando...' : 'Encerrar conexão'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
