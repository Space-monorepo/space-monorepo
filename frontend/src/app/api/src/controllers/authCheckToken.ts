import { useEffect, useState } from "react";
import Cookies from "js-cookie";
import { useRouter } from "next/navigation";
import { API_URL } from "@/config";
import { useBypassAuth } from "../hooks/useBypassAuth";

export const useCheckTokenValidity = () => {
  const [user, setUser] = useState<{
    name: string;
    username: string;
    profile_image_url: string;
    member_role?: string;
    communities?: Array<{ id: string; name: string; role?: string; }>;
    hasAdminOrModeratorRole?: boolean;
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const bypass = useBypassAuth();

  useEffect(() => {
    if (bypass) {
      setLoading(false);
      return;
    }

    const token = Cookies.get("token");

    if (!token) {
      router.push("/login");
      return;
    }

    const verifyToken = async () => {
      try {
        const response = await fetch(`${API_URL}/users/me`, {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const data = await response.json();

          // Buscar as comunidades do usuário com suas associações (incluindo role)
          let communities: Array<{ id: string; name: string; role?: string; }> = [];
          let hasAdminOrModeratorRole = false;

          try {
            const communitiesResponse = await fetch(`${API_URL}/communities/user/${data.id}/communities`, {
              method: "GET",
              headers: {
                Authorization: `Bearer ${token}`,
              },
            });

            if (communitiesResponse.ok) {
              const communitiesData = await communitiesResponse.json();

              // Para cada comunidade, buscar o papel do usuário
              for (const community of communitiesData.items || []) {
                try {
                  const membersResponse = await fetch(`${API_URL}/communities/${community.id}/members?user_id=${data.id}`, {
                    method: "GET",
                    headers: {
                      Authorization: `Bearer ${token}`,
                    },
                  });

                  let userRole = 'member'; // padrão
                  if (membersResponse.ok) {
                    const membersData = await membersResponse.json();
                    const userMember = membersData.items?.find((member: any) => member.user.id === data.id);
                    if (userMember) {
                      userRole = userMember.role;
                    }
                  }

                  communities.push({
                    id: community.id,
                    name: community.name,
                    role: userRole
                  });

                  // Verificar se tem papel de admin ou moderador
                  if (userRole === 'admin' || userRole === 'moderator') {
                    hasAdminOrModeratorRole = true;
                  }
                } catch (error) {
                  console.error(`Erro ao buscar papel do usuário na comunidade ${community.id}:`, error);
                  communities.push({
                    id: community.id,
                    name: community.name,
                    role: 'member'
                  });
                }
              }
            }
          } catch (error) {
            console.error("Erro ao buscar comunidades do usuário:", error);
          }

          setUser({
            name: data.name,
            username: data.username,
            profile_image_url: data.profile_image_url,
            member_role: data.member_role || data.role || undefined,
            communities: communities,
            hasAdminOrModeratorRole: hasAdminOrModeratorRole
          });
        } else {
          Cookies.remove("token");
          if (typeof window !== "undefined") {
            localStorage.removeItem("space_responsibility_accepted");
          }
          router.push("/login");
        }
      } catch (error) {
        console.error("Erro ao validar token:", error);
        Cookies.remove("token");
        if (typeof window !== "undefined") {
          localStorage.removeItem("space_responsibility_accepted");
        }
        router.push("/login");
      } finally {
        setLoading(false);
      }
    };

    verifyToken();
  }, [router, bypass]);

  return { user, loading };
};