"use client"

import { useState } from "react"
import { ArrowLeft, Filter, SortDesc, Eye, X, ArrowUp, MessageSquare } from "lucide-react"
import Sidebar from "@/components/ui/sidebar"

type NotificationType = "Campanhas" | "Avisos oficiais" | "Conexões" | "Interações"

type Notification = {
  id: number
  type: string
  title: string
  author: string
  community: string
  date: string
  time: string
  status?: string
  description?: string
  stats?: {
    published: string
    accesses: number
    participants: number
    likes: number
    comments: number
  }
  image?: string
  actions?: string[]
}

export default function NotificacoesPage() {
  const [activeTab, setActiveTab] = useState<NotificationType>("Campanhas")
  const [selectedNotification, setSelectedNotification] = useState<Notification | null>(null)

  const notifications = {
    Campanhas: [
      {
        id: 1,
        type: "Campanha",
        title: "Revitalização da Sala de Biblioteca",
        author: "Rafael Lanza",
        community: "PUC - Campinas",
        date: "18/02/2025",
        time: "5 mil",
        status: "Em análise",
        description: `A sala de estudos da biblioteca da nossa unidade está precisando de uma atenção especial. Muitos alunos usam o espaço todos os dias, mas infelizmente ele vem apresentando problemas de estrutura, iluminação fraca e cadeiras danificadas. Estamos iniciando uma campanha para arrecadar fundos e voluntários com o objetivo de revitalizar esse espaço tão importante para nossa rotina acadêmica. A proposta inclui pequenas reformas, pintura, reorganização dos móveis e instalação de lâmpadas novas. Toda ajuda será bem-vinda – seja com contribuições financeiras ou com tempo e disposição para ajudar no mutirão.

Se você acredita na força da coletividade e no impacto de um ambiente de estudo digno, participe da campanha!`,
        stats: {
          published: "18/02/2025",
          accesses: 5000,
          participants: 245,
          likes: 678,
          comments: 72,
        },
      },
      {
        id: 2,
        type: "Campanha",
        title: "Título da Campanha",
        author: "Rafael Lanza",
        community: "PUC - Campinas",
        date: "18/02/2025",
        time: "5 mil",
        status: "Em análise",
      },
    ],
    "Avisos oficiais": [
      {
        id: 1,
        type: "Anúncio",
        title: "Anúncio oficial da comunidade",
        author: "Briann Oliveira",
        community: "PUC - Campinas",
        date: "18/02/2025",
        time: "5 mil",
        description: `Prezados membros,

Informamos que, a partir do dia 22 de abril, o sistema de chat da plataforma passará por uma manutenção programada para melhorias de performance e segurança. Durante o período de atualização, que ocorrerá entre 22h e 04h, as funcionalidades de envio de mensagens e notificações estarão temporariamente indisponíveis. A moderação seguirá funcionando normalmente, bem como o acesso ao feed e às campanhas. Recomendamos que, caso haja alguma comunicação importante a ser feita durante esse horário, ela seja agendada com antecedência. Pedimos a compreensão de todos, pois essas melhorias são essenciais para garantir uma experiência mais estável e segura para a comunidade. Em caso de dúvidas, entre em contato com o suporte pela aba "Ajuda". Agradecemos pela colaboração.

Atenciosamente,
Equipe de Administração da Comunidade`,
        image: "/ProfilePic2.svg?height=300&width=600&text=🛠️",
        stats: {
          published: "18/02/2025",
          accesses: 5000,
          participants: 0,
          likes: 678,
          comments: 72,
        },
        actions: ["Promover", "Comentar"],
      },
      {
        id: 2,
        type: "Anúncio",
        title: "Título do Anúncio",
        author: "Rafael Lanza",
        community: "Condomínio",
        date: "18/02/2025",
        time: "5 mil",
      },
    ],
    Conexões: [
      {
        id: 1,
        type: "Conexão",
        title: "Felipe Sousa deseja conectar-se com você",
        author: "@felipesousa",
        community: "PUC - Campinas",
        date: "3 horas atrás",
        time: "",
        actions: ["Conectar-se", "X"],
      },
      {
        id: 2,
        type: "Conexão",
        title: "Briann Gomes conectou-se com você",
        author: "@brianngomes",
        community: "Condomínio",
        date: "1 semana atrás",
        time: "",
      },
      {
        id: 3,
        type: "Conexão",
        title: "Gabriel Padreca deseja conectar-se com você",
        author: "@gabrielpadreca",
        community: "Apple Campinas",
        date: "2 semanas atrás",
        time: "",
        actions: ["Conectar-se", "X"],
      },
    ],
    Interações: [
      {
        id: 1,
        type: "Comentário",
        title: "Felipe Sousa comentou no seu post: Parabéns pela campanha!!",
        author: "@felipesousa",
        community: "PUC - Campinas",
        date: "3 horas atrás",
        time: "",
        actions: ["Curtir"],
      },
      {
        id: 2,
        type: "Curtida",
        title: "Rafael Lanza curtiu seu comentário: Esse debate é importante!",
        author: "@rafaellanza",
        community: "Condomínio",
        date: "3 horas atrás",
        time: "",
      },
      {
        id: 3,
        type: "Comentário",
        title: "Gabriel Padreca comentou no seu post: Tem toda razão, estou...",
        author: "@gabrielpadreca",
        community: "PUC - Campinas",
        date: "10 horas atrás",
        time: "",
        actions: ["Curtir"],
      },
      {
        id: 4,
        type: "Participação",
        title: "Briann Gomes está participando da sua campanha",
        author: "@brianngomes",
        community: "PUC - Campinas",
        date: "14 horas atrás",
        time: "",
      },
    ],
  }

  const currentNotifications = notifications[activeTab] || []

  // Set first notification as selected when changing tabs
  if (!selectedNotification && currentNotifications.length > 0) {
    setSelectedNotification(currentNotifications[0])
  }

  const handleTabChange = (tab: NotificationType) => {
    setActiveTab(tab)
    setSelectedNotification(notifications[tab]?.[0] || null)
  }

  const getConnectionCount = () => {
    return notifications.Conexões.filter((n) => n.actions?.includes("Conectar-se")).length
  }

  const getInteractionCount = () => {
    return notifications.Interações.length
  }

  return (
    <div className="min-h-screen bg-gray-100 text-[#161616]">
      <Sidebar variant="static"/>
      <div className="ml-64 flex">
        {/* Left Navigation */}
        <div className="w-64 border-r border-[#e0e0e0] bg-gray-100 min-h-screen">
          <div className="p-4 border-b border-[#e0e0e0] flex items-center gap-3">
            <ArrowLeft className="h-5 w-5 text-[#525252]" />
            <h1 className="text-xl font-medium">Notificações</h1>
          </div>

          <nav className="py-2">
            {(Object.keys(notifications) as NotificationType[]).map((tab) => (
              <button
                key={tab}
                className={`w-full px-6 py-3 text-left hover:bg-[#f8f8f8] ${
                  activeTab === tab ? "bg-[#f4f4f4] border-r-4 border-black" : ""
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
        <div className="w-[800px] border-r border-[#e0e0e0] bg-gray-100 min-h-screen">
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
                className={`p-4 border-b border-[#e0e0e0] cursor-pointer hover:bg-[#f8f8f8] ${
                  selectedNotification?.id === notification.id ? "bg-[#f4f4f4]" : ""
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
                            {notification.actions.map((action, index) => (
                              <button
                                key={index}
                                className={`px-3 py-1 text-xs ${
                                  action === "Conectar-se" || action === "Curtir"
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
                      <p className="text-xs text-[#525252]">{notification.author}</p>
                      <p className="text-xs text-[#525252]">Comunidade: {notification.community}</p>
                      <p className="text-xs text-[#525252] mt-1">{notification.date}</p>
                    </div>
                  </div>
                ) : (
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs text-[#525252]">{notification.date}</span>
                      <div className="flex items-center gap-1">
                        <Eye className="h-4 w-4 text-[#525252]" />
                        <span className="text-xs text-[#525252]">{notification.time}</span>
                      </div>
                    </div>
                    <h3 className="font-medium mb-1">{notification.title}</h3>
                    <p className="text-xs text-[#525252] mb-1">
                      {activeTab === "Avisos oficiais" ? "Administrador" : "Líder"}: {notification.author}
                    </p>
                    <p className="text-xs text-[#525252] mb-2">Comunidade: {notification.community}</p>
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
          <div className="flex-1 p-6">
            <div className="bg-white border border-[#e0e0e0] p-6">
              {/* Author info */}
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-full overflow-hidden">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img src="/ProfilePic1.svg" alt="User" className="w-full h-full object-cover" />
                </div>
                <div className="flex items-center gap-2">
                  <span className="font-medium">{selectedNotification.author}</span>
                  <div className="w-1 h-1 rounded-full bg-[#525252]"></div>
                  <span className="text-xs px-2 py-0.5 bg-[#393939] text-white">
                    {activeTab === "Avisos oficiais" ? "Administrador" : "Líder"}
                  </span>
                </div>
                <span className="text-xs text-[#525252] ml-auto">{selectedNotification.community}</span>
              </div>

              {/* Content title */}
              <div className="mb-4">
                <div className="text-sm text-[#525252] mb-1">Título:</div>
                <h2 className="text-lg font-medium">{selectedNotification.title}</h2>
              </div>

              {/* Content description */}
              <div className="mb-6">
                <div className="text-sm text-[#525252] mb-1">Descrição:</div>
                <p className="text-[#161616] whitespace-pre-line">{selectedNotification.description}</p>
              </div>

              {/* Image */}
              {selectedNotification.image && (
                <div className="mb-6">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img src={selectedNotification.image || "/ProfilePic2.svg"} alt="Content image" className="w-full" />
                </div>
              )}

              {/* Stats */}
              {selectedNotification.stats && (
                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div>
                    <div className="text-sm text-[#525252] mb-1">Data publicada:</div>
                    <div>{selectedNotification.stats.published}</div>
                  </div>
                  <div>
                    <div className="text-sm text-[#525252] mb-1">Curtidas:</div>
                    <div>{selectedNotification.stats.likes} curtidas</div>
                  </div>
                  <div>
                    <div className="text-sm text-[#525252] mb-1">Número de acessos:</div>
                    <div>{selectedNotification.stats.accesses.toLocaleString()} acessos</div>
                  </div>
                  <div>
                    <div className="text-sm text-[#525252] mb-1">Comentários:</div>
                    <div>{selectedNotification.stats.comments} comentários</div>
                  </div>
                  {selectedNotification.stats.participants > 0 && (
                    <div>
                      <div className="text-sm text-[#525252] mb-1">Participantes:</div>
                      <div>{selectedNotification.stats.participants} pessoas</div>
                    </div>
                  )}
                  {selectedNotification.status && (
                    <div>
                      <div className="text-sm text-[#525252] mb-1">Status:</div>
                      <div className="inline-block px-2 py-0.5 bg-[#fff8e1] text-[#b28600] rounded-full text-sm">
                        {selectedNotification.status}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Actions */}
              {selectedNotification.actions && (
                <div className="flex items-center gap-4">
                  {selectedNotification.actions.map((action, index) => (
                    <button
                      key={index}
                      className="flex items-center gap-2 px-4 py-2 border border-[#e0e0e0] hover:bg-[#f8f8f8]"
                    >
                      {action === "Promover" && <ArrowUp className="h-4 w-4" />}
                      {action === "Comentar" && <MessageSquare className="h-4 w-4" />}
                      {action}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
