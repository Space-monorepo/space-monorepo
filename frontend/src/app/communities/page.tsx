"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import {
  Search,
  Lock,
  Clock,
  MoreHorizontal,
  ArrowRight,
  Users,
  Shield,
  UserCheck,
  TrendingUp,
  Edit,
  Trash2,
} from "lucide-react";
import Sidebar from "@/components/ui/sidebar";
import useCommunityActions from "@/app/api/src/hooks/community/useCommunityActions";
import useCommunityUserActions from "@/app/api/src/hooks/community/useCommunityUserActions";
import { Community } from "@/app/api/src/types/community/Community";
import { translateCommunityType } from "@/lib/communityTypeTranslations";
import { translateUserRole } from "@/lib/roleTranslations";
import EditCommunityModal from "@/components/modals/community/EditCommunityModal";
import DeleteCommunityModal from "@/components/modals/community/DeleteCommunityModal";
import { toast } from "react-toastify";

export default function ComunidadesPage() {
  const { communities, loading, error, updateCommunity, deleteCommunity } =
    useCommunityActions();
  const [selectedCommunity, setSelectedCommunity] = useState<Community | null>(
    null
  );
  const [activeTab, setActiveTab] = useState("Sobre");
  const [searchTerm, setSearchTerm] = useState("");
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  // Hook para gerenciar membros da comunidade selecionada
  const {
    members,
    pagination,
    loadMembers,
    isLoading: membersLoading,
  } = useCommunityUserActions();

  // Seleciona a primeira comunidade quando as comunidades são carregadas
  useEffect(() => {
    if (communities.length > 0 && !selectedCommunity) {
      setSelectedCommunity(communities[0]);
    }
  }, [communities, selectedCommunity]);

  // Carrega membros quando uma comunidade é selecionada
  useEffect(() => {
    if (selectedCommunity?.id) {
      loadMembers(selectedCommunity.id, { limit: 50 });
    }
  }, [selectedCommunity?.id, loadMembers]);

  // Funções para manipular os modais
  const handleUpdateCommunity = async (
    communityId: string,
    updateData: Partial<Community>
  ) => {
    setActionLoading(true);
    try {
      await updateCommunity(communityId, updateData);

      // Atualizar a comunidade selecionada se for a mesma
      if (selectedCommunity?.id === communityId) {
        setSelectedCommunity((prev) =>
          prev ? { ...prev, ...updateData } : null
        );
      }

      toast.success("Comunidade atualizada com sucesso!");
    } catch (error) {
      console.error("Erro ao atualizar comunidade:", error);
      toast.error("Erro ao atualizar comunidade");
      throw error;
    } finally {
      setActionLoading(false);
    }
  };

  const handleDeleteCommunity = async (communityId: string) => {
    setActionLoading(true);
    try {
      await deleteCommunity(communityId);

      // Se a comunidade excluída era a selecionada, limpar seleção
      if (selectedCommunity?.id === communityId) {
        setSelectedCommunity(null);
      }

      toast.success("Comunidade excluída com sucesso!");
    } catch (error) {
      console.error("Erro ao excluir comunidade:", error);
      toast.error("Erro ao excluir comunidade");
      throw error;
    } finally {
      setActionLoading(false);
    }
  };

  // Filtrar comunidades baseado no termo de pesquisa
  const filteredCommunities = communities.filter(
    (community) =>
      community.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      community.type_community
        .toLowerCase()
        .includes(searchTerm.toLowerCase()) ||
      translateCommunityType(community.type_community)
        .toLowerCase()
        .includes(searchTerm.toLowerCase()) ||
      (community.description &&
        community.description.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  // Limpa a seleção se a comunidade selecionada não estiver na lista filtrada
  useEffect(() => {
    if (
      selectedCommunity &&
      filteredCommunities.length > 0 &&
      !filteredCommunities.find((c) => c.id === selectedCommunity.id)
    ) {
      setSelectedCommunity(filteredCommunities[0]);
    } else if (filteredCommunities.length === 0 && searchTerm) {
      setSelectedCommunity(null);
    }
  }, [filteredCommunities, selectedCommunity, searchTerm]);

  // Função auxiliar para converter ano da data de criação
  const getCreationYear = (dateString?: string) => {
    if (!dateString) return new Date().getFullYear();
    return new Date(dateString).getFullYear();
  };

  // Função auxiliar para gerar um ícone baseado no tipo de comunidade
  const getCommunityIcon = (type: string) => {
    const icons = {
      university: "🎓",
      neighborhood: "🏘️",
      company: "🏢",
      government: "🏛️",
      healthcare: "🏥",
      religious: "⛪",
      commercial: "🏪",
      club: "🎯",
    };
    return icons[type as keyof typeof icons] || "🌟";
  };

  // Função auxiliar para gerar cor baseada no tipo
  const getCommunityColor = (type: string) => {
    const colors = {
      university: "#3b82f6",
      neighborhood: "#10b981",
      company: "#f59e0b",
      government: "#ef4444",
      healthcare: "#06b6d4",
      religious: "#8b5cf6",
      commercial: "#f97316",
      club: "#ec4899",
    };
    return colors[type as keyof typeof colors] || "#6b7280";
  };

  // Função para obter estatísticas dos membros
  const getMemberStats = () => {
    if (!members || members.length === 0) {
      return { admins: 0, moderators: 0, totalMembers: 0, activeMembers: 0 };
    }

    const admins = members.filter((member) => member.role === "admin").length;
    const moderators = members.filter(
      (member) => member.role === "moderator"
    ).length;
    const activeMembers = members.filter(
      (member) => member.status_participation === "active"
    ).length;

    return {
      admins,
      moderators,
      totalMembers: pagination?.total || members.length,
      activeMembers,
    };
  };

  return (
    <div className="min-h-screen bg-[#f4f4f4] text-[#161616]">
      <Sidebar variant="static" />
      <div className="flex h-screen ml-0 min-[900px]:ml-64">
        {/* Communities List */}
        <div className="w-[500px] border-r border-[#e0e0e0] bg-white overflow-hidden flex flex-col">
          {/* Header */}
          <div className="p-4 border-b border-[#e0e0e0]">
            <h1 className="text-xl font-medium mb-4">Minhas comunidades</h1>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[#525252] h-4 w-4" />
              <input
                type="text"
                placeholder="Pesquisar"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-[#e0e0e0] focus:outline-none focus:border-[#0f62fe]"
              />
            </div>
          </div>

          {/* Communities */}
          <div className="overflow-auto flex-1">
            {loading ? (
              <div className="p-4 text-center text-[#525252]">
                Carregando comunidades...
              </div>
            ) : error ? (
              <div className="p-4 text-center text-red-500">
                Erro ao carregar comunidades: {error.message}
              </div>
            ) : filteredCommunities.length === 0 ? (
              <div className="p-4 text-center text-[#525252]">
                {searchTerm
                  ? "Nenhuma comunidade encontrada para a pesquisa"
                  : "Nenhuma comunidade encontrada"}
              </div>
            ) : (
              filteredCommunities.map((community) => (
                <div
                  key={community.id}
                  className={`p-4 border-b border-[#e0e0e0] cursor-pointer hover:bg-[#f8f8f8] ${
                    selectedCommunity?.id === community.id ? "bg-[#f4f4f4]" : ""
                  }`}
                  onClick={() => setSelectedCommunity(community)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-10 h-10 flex items-center justify-center text-xl rounded`}
                        style={{
                          backgroundColor: getCommunityColor(
                            community.type_community
                          ),
                          color: "#ffffff",
                        }}
                      >
                        <span>
                          {getCommunityIcon(community.type_community)}
                        </span>
                      </div>
                      <div>
                        <h3 className="font-medium">{community.name}</h3>
                        <p className="text-xs text-[#525252]">
                          Tipo:{" "}
                          {translateCommunityType(community.type_community)}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center">
                      <button
                        className="p-1 text-[#525252] hover:text-[#161616] mr-1"
                        onClick={(e) => {
                          e.stopPropagation();
                          setIsEditModalOpen(true);
                        }}
                        title="Editar comunidade"
                      >
                        <Edit className="h-4 w-4" />
                      </button>
                      <button
                        className="p-1 text-[#525252] hover:text-red-600 mr-1"
                        onClick={(e) => {
                          e.stopPropagation();
                          setIsDeleteModalOpen(true);
                        }}
                        title="Excluir comunidade"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                      <button className="p-1 text-[#525252] hover:text-[#161616]">
                        <MoreHorizontal className="h-5 w-5" />
                      </button>
                      <button className="p-1 text-[#525252] hover:text-[#161616]">
                        <ArrowRight className="h-5 w-5" />
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Community Details */}
        {selectedCommunity && (
          <div className="flex-1 overflow-auto">
            <div className="p-6">
              <div className="mb-4">
                <h1 className="text-2xl font-medium mb-2">
                  {selectedCommunity.name}
                </h1>
                <div className="flex items-center text-sm text-[#525252]">
                  <Lock className="h-4 w-4 mr-1" />
                  <span>
                    Comunidade{" "}
                    {translateCommunityType(selectedCommunity.type_community)} ·{" "}
                    {getMemberStats().totalMembers} membros
                  </span>
                </div>
              </div>

              {/* Community Stats */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                <div className="bg-white border border-[#e0e0e0] p-4 rounded">
                  <div className="flex items-center gap-2 mb-2">
                    <Users className="h-4 w-4 text-blue-600" />
                    <span className="text-sm text-[#525252]">
                      Total de Membros
                    </span>
                  </div>
                  <span className="text-xl font-medium text-blue-600">
                    {membersLoading ? "..." : getMemberStats().totalMembers}
                  </span>
                </div>

                <div className="bg-white border border-[#e0e0e0] p-4 rounded">
                  <div className="flex items-center gap-2 mb-2">
                    <UserCheck className="h-4 w-4 text-green-600" />
                    <span className="text-sm text-[#525252]">
                      Membros Ativos
                    </span>
                  </div>
                  <span className="text-xl font-medium text-green-600">
                    {membersLoading ? "..." : getMemberStats().activeMembers}
                  </span>
                </div>

                <div className="bg-white border border-[#e0e0e0] p-4 rounded">
                  <div className="flex items-center gap-2 mb-2">
                    <Shield className="h-4 w-4 text-purple-600" />
                    <span className="text-sm text-[#525252]">Moderadores</span>
                  </div>
                  <span className="text-xl font-medium text-purple-600">
                    {membersLoading ? "..." : getMemberStats().moderators}
                  </span>
                </div>

                <div className="bg-white border border-[#e0e0e0] p-4 rounded">
                  <div className="flex items-center gap-2 mb-2">
                    <TrendingUp className="h-4 w-4 text-orange-600" />
                    <span className="text-sm text-[#525252]">
                      Administradores
                    </span>
                  </div>
                  <span className="text-xl font-medium text-orange-600">
                    {membersLoading ? "..." : getMemberStats().admins}
                  </span>
                </div>
              </div>

              {/* Tabs */}
              <div className="border-b border-[#e0e0e0] mb-6">
                <div className="flex">
                  {[
                    "Sobre",
                    "Membros",
                    "Moderadores",
                    "Discussão",
                    "Avaliações",
                  ].map((tab) => (
                    <button
                      key={tab}
                      className={`px-4 py-3 text-sm font-medium ${
                        activeTab === tab
                          ? "text-[#0f62fe] border-b-2 border-[#0f62fe]"
                          : "text-[#525252] hover:text-[#161616]"
                      }`}
                      onClick={() => setActiveTab(tab)}
                    >
                      {tab}
                    </button>
                  ))}
                </div>
              </div>

              {/* Tab Content */}
              <div className="mb-6">
                {activeTab === "Sobre" && (
                  <div>
                    <div className="border border-[#e0e0e0] bg-white mb-4">
                      <div className="p-4 border-b border-[#e0e0e0]">
                        <h3 className="font-medium">Sobre</h3>
                      </div>
                      <div className="p-4">
                        <p className="text-[#161616] whitespace-pre-line">
                          {selectedCommunity.description ||
                            "Nenhuma descrição disponível."}
                        </p>
                      </div>
                    </div>

                    <div className="border border-[#e0e0e0] bg-white">
                      <div className="p-4 flex items-center gap-3">
                        <div className="w-8 h-8 flex items-center justify-center border border-[#e0e0e0]">
                          <Clock className="h-4 w-4 text-[#525252]" />
                        </div>
                        <div>
                          <h3 className="font-medium">História</h3>
                          <p className="text-sm text-[#525252]">
                            Criado em{" "}
                            {getCreationYear(selectedCommunity.createdAt)}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === "Membros" && (
                  <div className="border border-[#e0e0e0] bg-white">
                    <div className="p-4 border-b border-[#e0e0e0]">
                      <h3 className="font-medium">Membros da Comunidade</h3>
                      <p className="text-sm text-[#525252] mt-1">
                        {pagination?.total || members.length} membros no total
                      </p>
                    </div>
                    <div className="p-4">
                      {membersLoading ? (
                        <div className="text-center py-8">
                          <div className="text-[#525252]">
                            Carregando membros...
                          </div>
                        </div>
                      ) : members.length === 0 ? (
                        <div className="text-center py-8">
                          <div className="text-[#525252]">
                            Nenhum membro encontrado
                          </div>
                        </div>
                      ) : (
                        <div className="space-y-3 max-h-96 overflow-y-auto">
                          {members.slice(0, 20).map((member) => (
                            <div
                              key={member.user_id}
                              className="flex items-center justify-between p-3 border border-[#e0e0e0] rounded"
                            >
                              <div className="flex items-center gap-3">
                                <div className="w-10 h-10 rounded-full overflow-hidden bg-[#f4f4f4] flex items-center justify-center">
                                  {member.user.profile_image_url ? (
                                    <Image
                                      src={member.user.profile_image_url}
                                      alt={member.user.name}
                                      width={40}
                                      height={40}
                                      className="w-full h-full object-cover"
                                    />
                                  ) : (
                                    <span className="text-lg font-medium text-[#525252]">
                                      {member.user.name.charAt(0).toUpperCase()}
                                    </span>
                                  )}
                                </div>
                                <div>
                                  <h4 className="font-medium">
                                    {member.user.name}
                                  </h4>
                                  <div className="flex items-center gap-2 text-xs text-[#525252]">
                                    <span
                                      className={`px-2 py-1 rounded text-xs ${
                                        member.role === "admin"
                                          ? "bg-orange-100 text-orange-800"
                                          : member.role === "moderator"
                                          ? "bg-purple-100 text-purple-800"
                                          : "bg-blue-100 text-blue-800"
                                      }`}
                                    >
                                      {translateUserRole(member.role)}
                                    </span>
                                    <span
                                      className={`px-2 py-1 rounded text-xs ${
                                        member.status_participation === "active"
                                          ? "bg-green-100 text-green-800"
                                          : member.status_participation ===
                                            "suspended"
                                          ? "bg-yellow-100 text-yellow-800"
                                          : "bg-red-100 text-red-800"
                                      }`}
                                    >
                                      {member.status_participation === "active"
                                        ? "Ativo"
                                        : member.status_participation ===
                                          "suspended"
                                        ? "Suspenso"
                                        : "Banido"}
                                    </span>
                                  </div>
                                </div>
                              </div>
                              <div className="text-right">
                                <div className="text-xs text-[#525252]">
                                  Reputação: {member.reputation}
                                </div>
                                <div className="text-xs text-[#525252]">
                                  Desde:{" "}
                                  {new Date(
                                    member.entered_in
                                  ).toLocaleDateString("pt-BR")}
                                </div>
                              </div>
                            </div>
                          ))}
                          {members.length > 20 && (
                            <div className="text-center mt-4">
                              <span className="text-sm text-[#525252]">
                                Mostrando 20 de {members.length} membros
                              </span>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {activeTab === "Moderadores" && (
                  <div className="border border-[#e0e0e0] bg-white">
                    <div className="p-4 border-b border-[#e0e0e0]">
                      <h3 className="font-medium">
                        Moderadores e Administradores
                      </h3>
                      <p className="text-sm text-[#525252] mt-1">
                        {getMemberStats().moderators + getMemberStats().admins}{" "}
                        moderadores/administradores
                      </p>
                    </div>
                    <div className="p-4">
                      {membersLoading ? (
                        <div className="text-center py-8">
                          <div className="text-[#525252]">
                            Carregando moderadores...
                          </div>
                        </div>
                      ) : (
                        <div className="space-y-3">
                          {members
                            .filter(
                              (member) =>
                                member.role === "admin" ||
                                member.role === "moderator"
                            )
                            .map((member) => (
                              <div
                                key={member.user_id}
                                className="flex items-center justify-between p-3 border border-[#e0e0e0] rounded"
                              >
                                <div className="flex items-center gap-3">
                                  <div className="w-10 h-10 rounded-full overflow-hidden bg-[#f4f4f4] flex items-center justify-center">
                                    {member.user.profile_image_url ? (
                                      <Image
                                        src={member.user.profile_image_url}
                                        alt={member.user.name}
                                        width={40}
                                        height={40}
                                        className="w-full h-full object-cover"
                                      />
                                    ) : (
                                      <span className="text-lg font-medium text-[#525252]">
                                        {member.user.name
                                          .charAt(0)
                                          .toUpperCase()}
                                      </span>
                                    )}
                                  </div>
                                  <div>
                                    <h4 className="font-medium">
                                      {member.user.name}
                                    </h4>
                                    <div className="flex items-center gap-2 text-xs">
                                      <span
                                        className={`px-2 py-1 rounded text-xs ${
                                          member.role === "admin"
                                            ? "bg-orange-100 text-orange-800"
                                            : "bg-purple-100 text-purple-800"
                                        }`}
                                      >
                                        {translateUserRole(member.role)}
                                      </span>
                                      <span className="text-[#525252]">
                                        Reputação: {member.reputation}
                                      </span>
                                    </div>
                                  </div>
                                </div>
                                <div className="text-right text-xs text-[#525252]">
                                  <div>
                                    Desde:{" "}
                                    {new Date(
                                      member.entered_in
                                    ).toLocaleDateString("pt-BR")}
                                  </div>
                                </div>
                              </div>
                            ))}
                          {members.filter(
                            (member) =>
                              member.role === "admin" ||
                              member.role === "moderator"
                          ).length === 0 && (
                            <div className="text-center py-8">
                              <div className="text-[#525252]">
                                Nenhum moderador encontrado
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {activeTab === "Discussão" && (
                  <div className="border border-[#e0e0e0] bg-white p-4">
                    <p className="text-[#525252]">
                      Discussões da comunidade aparecerão aqui.
                    </p>
                  </div>
                )}

                {activeTab === "Avaliações" && (
                  <div className="border border-[#e0e0e0] bg-white p-4">
                    <p className="text-[#525252]">
                      Avaliações da comunidade aparecerão aqui.
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Modals */}
      {selectedCommunity && (
        <>
          <EditCommunityModal
            community={selectedCommunity}
            isOpen={isEditModalOpen}
            onClose={() => setIsEditModalOpen(false)}
            onSave={handleUpdateCommunity}
            isLoading={actionLoading}
          />

          <DeleteCommunityModal
            community={selectedCommunity}
            isOpen={isDeleteModalOpen}
            onClose={() => setIsDeleteModalOpen(false)}
            onConfirm={handleDeleteCommunity}
            isLoading={actionLoading}
          />
        </>
      )}
    </div>
  );
}
