"use client"

import { useState, useEffect } from "react"
import { ArrowLeft, Filter, SortDesc, Eye, X, ArrowUp, MessageSquare } from "lucide-react"
import Sidebar from "@/components/ui/sidebar"
import { useNotifications } from "@/app/api/src/hooks/notifications/useNotifications"
import { Notification } from "@/app/api/src/types/notifications/Notification"

type NotificationType = "Campanhas" | "Avisos oficiais" | "Conexões" | "Interações"

export default function NotificacoesPage() {
  const [activeTab, setActiveTab] = useState<NotificationType>("Campanhas")
  const [selectedNotification, setSelectedNotification] = useState<Notification | null>(null)
  const { notifications, loading, error } = useNotifications()

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

  const getConnectionCount = () => {
    return notificationsTabs.Conexões.filter((n) => n.actions?.includes("Conectar-se")).length
  }

  const getInteractionCount = () => {
    return notificationsTabs.Interações.length
  }

  return (
    <div className="min-h-screen bg-gray-100 text-[#161616]">
      <Sidebar variant="static" />
      <div className="flex">
        {/* Left Navigation - Fixo igual CommunityAdminPage */}
        <div className="fixed left-64 top-0 w-64 bg-white border-r border-[#e0e0e0] h-screen z-20 overflow-y-auto">
          {/* Header */}
          <div className="sticky top-0 p-6 border-b border-[#e0e0e0] bg-white flex items-center gap-3">
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
                <div className="flex items-center justify-between">
                  <span>{tab}</span>
                  {tab === "Conexões" && getConnectionCount() > 0 && (
                    <span className="bg-black text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                      {getConnectionCount()}
                    </span>
                  )}
                  {tab === "Interações" && getInteractionCount() > 0 && (
                    <span className="bg-black text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                      {getInteractionCount()}
                    </span>
                  )}
                </div>
              </button>
            ))}
          </nav>
        </div>

        {/* Middle Section - Notifications List */}
        <div className="w-80 fixed top-0 bottom-0 left-[512px] bg-white border-r border-[#e0e0e0] overflow-y-auto z-10 no-scrollbar">
          {/* Header */}
          <div className="p-4 border-b border-[#e0e0e0] flex items-center justify-between">
            <h2 className="font-medium">{activeTab}</h2>
            <div className="flex gap-2">
              <button className="p-1 hover:bg-[#f4f4f4]">
                <Filter className="h-4 w-4 text-[#525252]" />
              </button>
              <button className="p-1 hover:bg-[#f4f4f4]">
                <SortDesc className="h-4 w-4 text-[#525252]" />
              </button>
            </div>
          </div>

          {/* Special header for Conexões */}
          {activeTab === "Conexões" && (
            <div className="p-4 border-b border-[#e0e0e0] flex gap-4">
              <button className="text-sm">Conexões</button>
              <button className="text-sm flex items-center gap-1">
                Pendentes
                <span className="bg-[#161616] text-white text-xs rounded-full w-4 h-4 flex items-center justify-center">
                  {getConnectionCount()}
                </span>
              </button>
            </div>
          )}

          {/* Special header for Interações */}
          {activeTab === "Interações" && (
            <div className="p-4 border-b border-[#e0e0e0] flex gap-4">
              <button className="text-sm flex items-center gap-1">
                Interações
                <span className="bg-[#161616] text-white text-xs rounded-full w-4 h-4 flex items-center justify-center">
                  {getInteractionCount()}
                </span>
              </button>
            </div>
          )}

          {/* Notifications List */}
          <div className="overflow-auto">
            {currentNotifications.map((notification) => (
              <div
                key={notification.id}
                className={`p-4 border-b border-[#e0e0e0] cursor-pointer hover:bg-[#f8f8f8] ${selectedNotification?.id === notification.id ? "bg-[#f4f4f4]" : ""
                  }`}
                onClick={() => setSelectedNotification(notification)}
              >
                {activeTab === "Conexões" || activeTab === "Interações" ? (
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full overflow-hidden flex-shrink-0">
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img
                        src="/ProfilePic3.svg?height=40&width=40"
                        alt="User"
                        className="w-full h-full object-cover"
                      />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-1">
                        <p className="font-medium text-sm">{notification.title}</p>
                        {notification.actions && (
                          <div className="flex gap-2">
                            {notification.actions.map((action: string, index: number) => (
                              <button
                                key={index}
                                className={`px-3 py-1 text-xs ${action === "Conectar-se" || action === "Curtir"
                                  ? "bg-[#161616] text-white"
                                  : "bg-[#f4f4f4] hover:bg-[#e0e0e0]"
                                  }`}
                              >
                                {action === "X" ? <X className="h-3 w-3" /> : action}
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                      <p className="text-xs text-[#525252]">{notification.author.name}</p>
                      <p className="text-xs text-[#525252]">Comunidade: {notification.community.name}</p>
                      <p className="text-xs text-[#525252] mt-1">{notification.date}</p>
                    </div>
                  </div>
                ) : (
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
                      <span className="text-xs px-2 py-0.5 bg-[#fff8e1] text-[#b28600] rounded-full">
                        {notification.status}
                      </span>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Right Section - Detailed View */}
        {selectedNotification && (activeTab === "Campanhas" || activeTab === "Avisos oficiais") && (
          <div className="flex-1 bg-gray-100 px-6 py-8 fixed top-0 right-0 bottom-0 left-[calc(512px+320px)] overflow-y-auto no-scrollbar">
            <div className="max-w-full">
              <div className="px-4 pt-4 pb-80 w-full bg-zinc-100 max-md:pb-24 max-md:max-w-full">
                <article className="mb-0 bg-white max-md:mb-2.5 max-md:max-w-full">
                  <header className="flex flex-col justify-center p-8 w-full bg-white rounded max-md:px-5 max-md:max-w-full">
                    <div className="w-full max-md:max-w-full">
                      <div className="flex justify-between items-start w-full max-md:max-w-full">
                        <div className="flex items-center min-w-60">
                          <img
                            src="/ProfilePic1.svg"
                            alt="User"
                            className="object-contain shrink-0 self-stretch my-auto w-11 aspect-square"
                          />
                          <div className="self-stretch my-auto min-w-60 w-[342px]">
                            <div className="flex gap-2 items-center w-full h-[23px]">
                              <div className="flex overflow-hidden gap-2.5 justify-center items-center self-stretch px-3 my-auto">
                                <span className="self-stretch my-auto text-sm text-neutral-800">
                                  {selectedNotification.author.name}
                                </span>
                                <span className="flex gap-2.5 justify-center items-center self-stretch px-3 py-1 my-auto text-xs whitespace-nowrap rounded bg-neutral-800 text-white">
                                  {activeTab === "Avisos oficiais" ? "Administrador" : "Líder"}
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                        <span className="text-xs text-neutral-500">{selectedNotification.community.name}</span>
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
                    {selectedNotification.stats && (
                      <div className="w-full text-sm leading-none max-md:max-w-full">
                        <div className="flex flex-wrap gap-36 items-start w-full max-md:max-w-full">
                          <div className="flex flex-col items-start">
                            <div className="flex gap-2 items-center">
                              <span className="self-stretch my-auto font-medium text-neutral-800">
                                Data publicada:
                              </span>
                              <span className="self-stretch my-auto text-neutral-500">
                                {selectedNotification.stats.published}
                              </span>
                            </div>
                            <div className="flex gap-2 items-center self-stretch mt-4">
                              <span className="self-stretch my-auto font-medium text-neutral-800">
                                Número de acessos:
                              </span>
                              <span className="self-stretch my-auto text-neutral-500">
                                {selectedNotification.stats.accesses.toLocaleString()} acessos
                              </span>
                            </div>
                            {selectedNotification.stats.participants > 0 && (
                              <div className="flex gap-2 items-center mt-4">
                                <span className="self-stretch my-auto font-medium text-neutral-800">
                                  Participantes:
                                </span>
                                <span className="self-stretch my-auto text-neutral-500">
                                  {selectedNotification.stats.participants} pessoas
                                </span>
                              </div>
                            )}
                          </div>
                          <div className="flex flex-col w-[198px]">
                            <div className="flex gap-2 items-center self-start">
                              <span className="self-stretch my-auto font-medium text-neutral-800">
                                Curtidas:
                              </span>
                              <span className="self-stretch my-auto text-neutral-500">
                                {selectedNotification.stats.likes} curtidas
                              </span>
                            </div>
                            <div className="flex gap-2 items-center mt-4 w-full">
                              <span className="self-stretch my-auto font-medium text-neutral-800">
                                Comentários:
                              </span>
                              <span className="self-stretch my-auto text-neutral-500">
                                {selectedNotification.stats.comments} comentários
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Status Section */}
                    {selectedNotification.status && (
                      <div className="flex gap-2 items-center self-start mt-10">
                        <span className="self-stretch my-auto text-sm font-medium leading-none text-neutral-800">
                          Status:
                        </span>
                        <div className="inline-block px-2 py-0.5 bg-[#fff8e1] text-[#b28600] rounded-full text-sm">
                          {selectedNotification.status}
                        </div>
                      </div>
                    )}

                    {/* Actions Section */}
                    {selectedNotification.actions && (
                      <div className="flex items-center gap-4 mt-10">
                        {selectedNotification.actions.map((action: string, index: number) => (
                          <button
                            key={index}
                            className="flex items-center gap-2 px-4 py-2 border border-[#e0e0e0] hover:bg-[#f8f8f8] rounded"
                          >
                            {action === "Promover" && <ArrowUp className="h-4 w-4" />}
                            {action === "Comentar" && <MessageSquare className="h-4 w-4" />}
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
      </div>
    </div>
  )
}
