
"use client"

import { Close, CheckmarkFilled, Forum, ArrowUp } from "@carbon/icons-react";

import { useState, useEffect } from "react"
import { ArrowLeft, Filter, SortDesc, Eye } from "lucide-react"
import Sidebar from "@/components/ui/sidebar"
import { useNotifications } from "@/app/api/src/hooks/notifications/useNotifications"
import { Notification } from "@/app/api/src/types/notifications/Notification"
import getCheckmarkColorClass from "@/components/badges/users/CheckmarkColorClasses";
import getRoleBadgeClasses from "@/components/badges/users/RoleBadgesClasses";
import { translateUserRole } from "@/lib/roleTranslations";
import {
  PendenteBadge,
  EmAnaliseBadge,
  AprovadaBadge,
  RejeitadaBadge,
  EmProgressoBadge,
  CanceladaBadge,
  FinalizadaBadge
} from "@/components/badges/campaign/CampaignBadges";

type NotificationType = "Campanhas" | "Avisos oficiais" | "Conexões" | "Interações"

export default function NotificacoesPage() {
  // Função para mapear status da API para status do frontend
  const mapApiStatusToFrontendStatus = (apiStatus: string): "Em análise" | "Aprovado" | "Rejeitado" | "Pendente" | "Em progresso" | "Cancelada" | "Finalizada" => {
    switch (apiStatus.toLowerCase()) {
      case 'active':
        return "Em análise";
      case 'approved':
        return "Aprovado";
      case 'rejected':
        return "Rejeitado";
      case 'pending':
        return "Pendente";
      case 'in_progress':
        return "Em progresso";
      case 'cancelled':
        return "Cancelada";
      case 'completed':
      case 'finished':
        return "Finalizada";
      default:
        return "Em análise";
    }
  };

  // Função para mapear status da campanha para o componente de badge correto
  const getCampaignStatusBadge = (status: string) => {
    // Primeiro mapear o status da API para o formato do frontend
    const mappedStatus = mapApiStatusToFrontendStatus(status);

    switch (mappedStatus) {
      case "Em análise":
        return <EmAnaliseBadge />;
      case "Aprovado":
        return <AprovadaBadge />;
      case "Rejeitado":
        return <RejeitadaBadge />;
      case "Pendente":
        return <PendenteBadge />;
      case "Em progresso":
        return <EmProgressoBadge />;
      case "Cancelada":
        return <CanceladaBadge />;
      case "Finalizada":
        return <FinalizadaBadge />;
      default:
        return <PendenteBadge />;
    }
  };
  const [activeTab, setActiveTab] = useState<NotificationType>("Campanhas")
  const [selectedNotification, setSelectedNotification] = useState<Notification | null>(null)
  const { notifications, loading, error } = useNotifications()

  // State for connections functionality
  const [connections, setConnections] = useState([
    {
      id: "1",
      timestamp: "3 horas atrás",
      message: "Felipe Sousa deseja conectar-se com você",
      username: "@felipesousa",
      community: "Comunidade: PUC-Campinas",
      isPending: true
    },
    {
      id: "2",
      timestamp: "1 semana atrás",
      message: "Briann Gomes conectou-se com você",
      username: "@brianngomes",
      community: "Comunidade: Condomínio",
      isPending: false
    },
    {
      id: "3",
      timestamp: "2 semanas atrás",
      message: "Gabriel Padreca deseja conectar-se com você",
      username: "@gabrielpadreca",
      community: "Comunidade: Apple Campinas",
      isPending: true
    },
    {
      id: "4",
      timestamp: "2 semanas atrás",
      message: "Guilherme Sousa conectou-se com você",
      username: "@guilhermesousa",
      community: "Comunidade: PUC-Campinas",
      isPending: false
    }
  ])

  const pendingCount = connections.filter(conn => conn.isPending).length

  const handleConnect = (id: string) => {
    setConnections(prev =>
      prev.map(conn =>
        conn.id === id
          ? { ...conn, isPending: false, message: conn.message.replace("deseja conectar-se com você", "conectou-se com você") }
          : conn
      )
    );
  };

  const handleReject = (id: string) => {
    setConnections(prev => prev.filter(conn => conn.id !== id));
  };

  // Mapear os dados da API para o formato usado no componente
  const notificationsTabs: Record<NotificationType, Notification[]> = {
    Campanhas: notifications.campaigns,
    "Avisos oficiais": notifications.announcements,
    Conexões: notifications.connections,
    Interações: notifications.interactions,
  }

  const currentNotifications = notificationsTabs[activeTab] || []

  // Set first notification as selected when changing tabs or when data loads
  useEffect(() => {
    if (!selectedNotification && currentNotifications.length > 0) {
      setSelectedNotification(currentNotifications[0])
    }
  }, [selectedNotification, currentNotifications])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 text-[#161616]">
        <Sidebar variant="static" />
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
            <p className="mt-4 text-gray-600">Carregando notificações...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 text-[#161616]">
        <Sidebar variant="static" />
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <p className="text-red-600">Erro ao carregar notificações: {error}</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-4 px-4 py-2 bg-black text-white rounded"
            >
              Tentar novamente
            </button>
          </div>
        </div>
      </div>
    )
  }

  const handleTabChange = (tab: NotificationType) => {
    setActiveTab(tab)
    setSelectedNotification(notificationsTabs[tab]?.[0] || null)
  }

  return (
    <div className="min-h-screen bg-white text-[#161616]">
      <Sidebar variant="static" />
      <div className="flex">
        {/* Left Navigation - Fixo igual CommunityAdminPage */}
        <div className="fixed left-64 top-0 w-64 bg-white border-r border-[#e0e0e0] h-screen z-20 overflow-y-auto">
          {/* Header */}
          <div className="sticky top-0 p-6 border-[#e0e0e0] bg-white flex items-center gap-3">
            <ArrowLeft className="h-5 w-5 text-[#525252]" />
            <h1 className="text-lg font-medium">Notificações</h1>
          </div>
          {/* Navigation Tabs */}
          <nav className="py-4">
            {(Object.keys(notificationsTabs) as NotificationType[]).map((tab) => (
              <button
                key={tab}
                className={`w-full px-6 py-3 text-left hover:bg-[#f8f8f8] cursor-pointer ${activeTab === tab
                  ? "bg-[#f4f4f4] border-r-4 border-black text-[#161616]"
                  : "text-[#525252]"
                  }`}
                onClick={() => handleTabChange(tab)}
              >
                <span>{tab}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Middle Section - Notifications List (removido para Conexões) */}
        {activeTab !== "Conexões" && (
          <div className="w-80 fixed top-0 bottom-0 left-[512px] bg-white border-r border-[#e0e0e0] overflow-y-auto z-10 no-scrollbar">
            {/* Header */}
            <div className="p-4 my-2 text-gray-600 text-[14px] flex items-center justify-between">
              <h2 className="font-regular">{activeTab}</h2>
              <div className="flex gap-2">
                <button className="p-1 hover:bg-[#f4f4f4]">
                  <Filter className="h-4 w-4 text-[#525252]" />
                </button>
                <button className="p-1 hover:bg-[#f4f4f4]">
                  <SortDesc className="h-4 w-4 text-[#525252]" />
                </button>
              </div>
            </div>

            {/* Special header for Interações */}
            {activeTab === "Interações" && (
              <div className="p-4 border-b border-[#e0e0e0] flex gap-4">
                <button className="text-sm">
                  Interações
                </button>
              </div>
            )}

            {/* Notifications List */}
            <div className="overflow-auto">
              {currentNotifications.map((notification) => (
                <div
                  key={notification.id}
                  className={`p-4 border-b border-[#e0e0e0] cursor-pointer hover:bg-[#f8f8f8] ${selectedNotification?.id === notification.id ? "bg-[#f4f4f4]" : ""}`}
                  onClick={() => setSelectedNotification(notification)}
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs text-[#525252]">{notification.date}</span>
                      <div className="flex items-center gap-1">
                        <Eye className="h-4 w-4 text-[#525252]" />
                        <span className="text-xs text-[#525252]">{notification.time || notification.stats?.accesses || '0'}</span>
                      </div>
                    </div>
                    <h3 className="font-medium mb-1">{notification.title}</h3>
                    <p className="text-xs text-[#525252] mb-1">
                      {activeTab === "Avisos oficiais" ? "Administrador" : "Líder"}: {notification.author.name}
                    </p>
                    <p className="text-xs text-[#525252] mb-2">Comunidade: {notification.community.name}</p>
                    {notification.status && (
                      <div className="flex items-center">
                        {getCampaignStatusBadge(notification.status)}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Right Section - Detailed View for Campanhas */}
        {selectedNotification && activeTab === "Campanhas" && (
          <div className="flex-1 bg-gray-100 fixed top-0 right-0 bottom-0 left-[calc(512px+320px)] overflow-y-auto no-scrollbar">
            <div className="max-w-full">
              <div className="px-4 pt-4 pb-80 w-full bg-zinc-100 max-md:pb-24 max-md:max-w-full">
                <article className="mb-0 bg-white max-md:mb-2.5 max-md:max-w-full">
                  <header className="flex flex-col justify-center p-8 w-full bg-white rounded max-md:px-5 max-md:max-w-full">
                    <div className="w-full max-md:max-w-full">
                      <div className="flex justify-between items-start w-full max-md:max-w-full">
                        <div className="flex items-center min-w-60">
                          <img
                            src={selectedNotification.author.profile_picture || "/no-profile-pic.png"}
                            alt={`${selectedNotification.author.name} profile picture`}
                            className="object-contain shrink-0 self-stretch my-auto w-11 aspect-square"
                          />
                          <div className="self-stretch my-auto min-w-60 w-[342px]">
                            <div className="flex gap-2 items-center w-full h-[23px]">
                              <div className="flex overflow-hidden gap-2.5 justify-center items-center self-stretch px-3 my-auto">
                                <span className="self-stretch my-auto text-sm text-neutral-800">
                                  {selectedNotification.author.name}
                                </span>
                                <CheckmarkFilled
                                  className={`object-contain shrink-0 self-stretch my-auto aspect-square w-[18px] ${getCheckmarkColorClass(selectedNotification.author.role)}`}
                                  aria-label="Verificado"
                                />
                                <div className="self-stretch my-auto text-[10px] text-black">
                                  •
                                </div>
                                <span className={`flex gap-2.5 justify-center items-center self-stretch px-3 py-1 my-auto text-xs whitespace-nowrap rounded ${getRoleBadgeClasses(selectedNotification.author.role)}`}>
                                  {translateUserRole(selectedNotification.author.role || "member")}
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div className="mt-6 w-full text-sm text-neutral-800 max-md:max-w-full">
                        <div className="flex flex-wrap gap-4 items-center w-full leading-6 max-md:max-w-full">
                          <span className="self-stretch my-auto font-semibold text-neutral-800">
                            Título:{" "}
                          </span>
                          <span className="self-stretch my-auto text-neutral-800">
                            {selectedNotification.title}
                          </span>
                        </div>
                        <div className="mt-2 w-full max-md:max-w-full">
                          <h3 className="font-semibold leading-6 text-justify text-neutral-800">
                            Descrição:
                          </h3>
                          <p className="mt-2 leading-5 text-neutral-800 max-md:max-w-full whitespace-pre-line">
                            {selectedNotification.description}
                          </p>
                        </div>
                      </div>
                    </div>
                  </header>

                  {/* Image Section */}
                  {selectedNotification.image_url && (
                    <section className="px-8 pb-6 w-full max-md:px-5 max-md:max-w-full">
                      <img
                        src={selectedNotification.image_url || "/ProfilePic2.svg"}
                        alt="Content image"
                        className="w-full rounded"
                      />
                    </section>
                  )}

                  <section className="flex flex-col py-8 pr-4 pl-8 w-full max-md:pl-5 max-md:max-w-full">
                    <div className="w-full text-sm leading-none max-md:max-w-full">
                      <div className="flex flex-wrap gap-36 items-start w-full max-md:max-w-full">
                        <div className="flex flex-col items-start">
                          <div className="flex gap-2 items-center">
                            <span className="self-stretch my-auto font-medium text-neutral-800">
                              Data publicada:
                            </span>
                            <span className="self-stretch my-auto text-neutral-500">
                              {selectedNotification.stats?.published || selectedNotification.date}
                            </span>
                          </div>
                          <div className="flex gap-2 items-center self-stretch mt-4">
                            <span className="self-stretch my-auto font-medium text-neutral-800">
                              Número de acessos:
                            </span>
                            <span className="self-stretch my-auto text-neutral-500">
                              {selectedNotification.stats?.accesses ?? 0} acessos
                            </span>
                          </div>
                          <div className="flex gap-2 items-center mt-4">
                            <span className="self-stretch my-auto font-medium text-neutral-800">
                              Participantes:
                            </span>
                            <span className="self-stretch my-auto text-neutral-500">
                              {selectedNotification.stats?.participants ?? 0} pessoas
                            </span>
                          </div>
                        </div>
                        <div className="flex flex-col w-[198px]">
                          <div className="flex gap-2 items-center self-start">
                            <span className="self-stretch my-auto font-medium text-neutral-800">
                              Curtidas:
                            </span>
                            <span className="self-stretch my-auto text-neutral-500">
                              {selectedNotification.stats?.likes ?? 0} curtidas
                            </span>
                          </div>
                          <div className="flex gap-2 items-center mt-4 w-full">
                            <span className="self-stretch my-auto font-medium text-neutral-800">
                              Comentários:
                            </span>
                            <span className="self-stretch my-auto text-neutral-500">
                              {selectedNotification.stats?.comments ?? 0} comentários
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Status Section */}
                    <div className="flex gap-2 items-center self-start mt-10">
                      <span className="self-stretch my-auto text-sm font-medium leading-none text-neutral-800">
                        Status:
                      </span>
                      {getCampaignStatusBadge(selectedNotification.status || "pending")}
                    </div>

                    {/* Actions Section */}
                    {selectedNotification.actions && (
                      <div className="flex items-center gap-4 mt-10">
                        {selectedNotification.actions.map((action: string, index: number) => (
                          <button
                            key={index}
                            className="flex items-center gap-2 px-4 py-2 border border-[#e0e0e0] hover:bg-[#f8f8f8] rounded"
                          >
                            {action === "Promover" && <ArrowUp className="h-4 w-4" />}
                            {action === "Comentar" && <Forum className="h-4 w-4" />}
                            {action}
                          </button>
                        ))}
                      </div>
                    )}
                  </section>
                </article>
              </div>
            </div>
          </div>
        )}

        {/* Right Section - Detailed View for Avisos oficiais (layout de enquete) */}
        {selectedNotification && activeTab === "Avisos oficiais" && (
          <div className="flex-1 bg-gray-100 fixed top-0 right-0 bottom-0 left-[calc(512px+320px)] overflow-y-auto no-scrollbar">
            <div className="max-w-full">
              <div className="px-4 pt-4 pb-48 w-full bg-zinc-100 max-md:pb-24 max-md:max-w-full">
                <main className="bg-white max-w-full">
                  <article className="flex flex-col justify-center p-8 w-full bg-white rounded max-md:px-5 max-md:max-w-full">
                    <div className="w-full max-md:max-w-full">
                      <div className="flex justify-between items-start w-full max-md:max-w-full">
                        <header className="flex items-center min-w-60">
                          <img
                            src={selectedNotification.author.profile_picture || "/no-profile-pic.png"}
                            alt={`${selectedNotification.author.name} profile picture`}
                            className="object-contain shrink-0 self-stretch my-auto w-11 aspect-square rounded-[32px]"
                          />
                          <div className="self-stretch my-auto min-w-60 w-[342px]">
                            <div className="flex gap-2 items-center w-full h-[23px]">
                              <div className="flex overflow-hidden gap-2.5 justify-center items-center self-stretch px-3 my-auto">
                                <h2 className="self-stretch my-auto text-sm text-neutral-800">
                                  {selectedNotification.author.name}
                                </h2>
                                <CheckmarkFilled
                                  className={`object-contain shrink-0 self-stretch my-auto aspect-square w-[18px] ${getCheckmarkColorClass(selectedNotification.author.role)}`}
                                  aria-label="Verificado"
                                />
                                <div className="self-stretch my-auto text-[10px] text-black">
                                  •
                                </div>
                                <div className={`flex gap-2.5 justify-center items-center self-stretch px-3 py-1 my-auto text-xs whitespace-nowrap rounded ${getRoleBadgeClasses(selectedNotification.author.role)}`}>
                                  <span className="self-stretch my-auto">
                                    {translateUserRole(selectedNotification.author.role || "member")}
                                  </span>
                                </div>
                              </div>
                            </div>
                          </div>
                        </header>
                      </div>
                      <div className="mt-6 w-full text-sm text-neutral-800 max-md:max-w-full">
                        <div className="flex flex-wrap gap-4 items-center w-full max-md:max-w-full">
                          <h1 className="self-stretch my-auto font-semibold leading-6 text-neutral-800">
                            Título:
                          </h1>
                          <p className="self-stretch my-auto leading-8 text-neutral-800">
                            {selectedNotification.title}
                          </p>
                        </div>
                        <div className="mt-2 w-full max-md:max-w-full">
                          <h2 className="font-semibold leading-6 text-justify text-neutral-800">
                            Descrição:
                          </h2>
                          <p className="mt-2 leading-5 text-neutral-800 max-md:max-w-full whitespace-pre-line">
                            {selectedNotification.description}
                          </p>
                        </div>
                      </div>
                      {selectedNotification.image_url && (
                        <img
                          src={selectedNotification.image_url}
                          alt="Aviso oficial illustration"
                          className="object-contain mt-6 w-full rounded aspect-[2.43] max-md:max-w-full"
                        />
                      )}
                    </div>
                  </article>

                  <section className="flex flex-col justify-center py-8 pr-4 pl-8 w-full text-sm leading-none max-md:pl-5 max-md:max-w-full">
                    <div className="w-full max-w-[698px] max-md:max-w-full">
                      <div className="flex flex-wrap gap-10 items-start w-full max-md:max-w-full">
                        <div className="flex flex-col items-start">
                          <div className="flex gap-2 items-center">
                            <span className="self-stretch my-auto font-medium text-neutral-800">
                              Data publicada:
                            </span>
                            <span className="self-stretch my-auto text-neutral-500">
                              {selectedNotification.stats?.published || selectedNotification.date}
                            </span>
                          </div>
                          <div className="flex gap-2 items-center self-stretch mt-4">
                            <span className="self-stretch my-auto font-medium text-neutral-800">
                              Número de acessos:
                            </span>
                            <span className="self-stretch my-auto text-neutral-500">
                              {selectedNotification.stats?.accesses ?? 0} acessos
                            </span>
                          </div>
                        </div>
                        <div className="flex flex-col w-[198px]">
                          <div className="flex gap-2 items-center self-start">
                            <span className="self-stretch my-auto font-medium text-neutral-800">
                              Curtidas:
                            </span>
                            <span className="self-stretch my-auto text-neutral-500">
                              {selectedNotification.stats?.likes ?? 0} curtidas
                            </span>
                          </div>
                          <div className="flex gap-2 items-center mt-4 w-full">
                            <span className="self-stretch my-auto font-medium text-neutral-800">
                              Comentários:
                            </span>
                            <span className="self-stretch my-auto text-neutral-500">
                              {selectedNotification.stats?.comments ?? 0} comentários
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Botões de ação - Promover e Comentar */}
                    <div className="flex items-center gap-4 mt-10 max-w-[698px] max-md:max-w-full">
                      <button
                        onClick={() => {
                          // Ação de promover
                        }}
                        className="flex items-center gap-2 px-6 py-3 text-gray-600 hover:bg-gray-200 transition-colors cursor-pointer rounded"
                      >
                        <ArrowUp className="h-4 w-4" />
                        <span>Promover</span>
                      </button>
                      <button
                        onClick={() => {
                          // Ação de comentar
                        }}
                        className="flex items-center gap-2 px-6 py-3 text-gray-600 hover:bg-gray-200 transition-colors cursor-pointer rounded"
                      >
                        <Forum className="h-4 w-4" />
                        <span>Comentar</span>
                      </button>
                    </div>
                  </section>
                </main>
              </div>
            </div>
          </div>
        )}

        {/* Right Section - ConnectionsList Layout for Conexões */}
        {activeTab === "Conexões" && (
          <div className="flex-1 bg-white px-6 py-8 fixed top-6 right-0 bottom-0 left-[calc(300px+320px)] overflow-y-auto no-scrollbar">
            <div className="max-w-[680px]">
              {/* Header Section */}
              <header className="flex flex-wrap gap-10 justify-between items-center py-2.5 pr-6 pl-4 w-full max-md:pr-5 max-md:max-w-full">
                <nav className="flex gap-4 items-center self-stretch my-auto whitespace-nowrap min-w-60 w-[385px]">
                  <h1 className="self-stretch my-auto text-sm leading-none text-neutral-600">
                    Conexões
                  </h1>
                  <div className="self-stretch my-auto text-[10px] text-black font-semibold">
                    •
                  </div>
                  <div className="flex gap-4 items-center self-stretch my-auto">
                    <span className="self-stretch my-auto text-sm leading-none text-neutral-600">
                      Pendentes
                    </span>
                    <div className="flex gap-2.5 justify-center items-center self-stretch px-2 my-auto w-6 h-6 text-xs font-semibold leading-none text-gray-200 rounded-2xl bg-zinc-900">
                      <span className="self-stretch my-auto">
                        {pendingCount}
                      </span>
                    </div>
                  </div>
                </nav>
                <div className="flex gap-2 items-center self-stretch my-auto">
                  <button type="button" aria-label="Action 1">
                    <img
                      src="https://api.builder.io/api/v1/image/assets/367ac41a58454bf7adac62a5f3afc83b/074681a549e783096b458262f6c0fe30416fe3b1?placeholderIfAbsent=true"
                      className="object-contain shrink-0 self-stretch my-auto w-5 aspect-square"
                      alt=""
                    />
                  </button>
                  <button type="button" aria-label="Action 2">
                    <img
                      src="https://api.builder.io/api/v1/image/assets/367ac41a58454bf7adac62a5f3afc83b/8fab779e10432bd198f30df3d0e10f8370547d71?placeholderIfAbsent=true"
                      className="object-contain shrink-0 self-stretch my-auto w-5 aspect-square"
                      alt=""
                    />
                  </button>
                </div>
              </header>

              {/* Connections List Section */}
              <section className="mt-6 w-full max-md:max-w-full">
                {connections.map((connection) => {
                  return (
                    <article
                      key={connection.id}
                      className={`flex flex-col justify-center px-6 py-4 w-full bg-white max-md:px-5 max-md:max-w-full ${connection.isPending ? 'hover:bg-zinc-100 transition-colors' : ''}`}
                    >
                      <div className="w-full max-md:max-w-full">
                        <time className="text-xs leading-loose text-neutral-600 max-md:max-w-full">
                          {connection.timestamp}
                        </time>
                        <div className="mt-2 w-full max-md:max-w-full">
                          <div className="flex flex-wrap gap-6 items-start w-full max-md:max-w-full">
                            <p className="flex-1 shrink text-base text-black basis-8 max-md:max-w-full">
                              {connection.message}
                            </p>
                            {connection.isPending && (
                              <>
                                <button
                                  onClick={() => handleConnect(connection.id)}
                                  className="flex gap-8 items-center px-4 py-2 text-sm leading-6 whitespace-nowrap bg-neutral-800 text-zinc-100 hover:bg-neutral-700 transition-colors"
                                >
                                  <span className="self-stretch my-auto text-zinc-100">
                                    Conectar-se
                                  </span>
                                </button>
                                <button
                                  onClick={() => handleReject(connection.id)}
                                  className="flex gap-8 items-center px-4 py-3 w-12 bg-neutral-200 hover:bg-neutral-300 transition-colors"
                                  aria-label="Rejeitar conexão"
                                >
                                  <Close className="object-contain self-stretch my-auto w-4 aspect-square" aria-label="Fechar" />
                                </button>
                              </>
                            )}
                          </div>
                          <p className="mt-1 text-xs leading-loose text-neutral-600 max-md:max-w-full">
                            {connection.username}
                          </p>
                          <p className="mt-1 text-xs leading-loose text-neutral-600 max-md:max-w-full">
                            {connection.community}
                          </p>
                        </div>
                      </div>
                    </article>
                  );
                })}
              </section>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
