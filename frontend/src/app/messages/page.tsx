"use client"

import { useState, useEffect, useCallback, useRef } from "react"
import Link from "next/link"
import { useSearchParams } from "next/navigation"
import { Search, Paperclip, Smile, Loader2 } from "lucide-react"
import Sidebar from "@/components/ui/sidebar"
import useChatConversations from "@/app/api/src/hooks/chat/useChatConversations"
import useChatMessages from "@/app/api/src/hooks/chat/useChatMessages"
import useConnectionActions from "@/app/api/src/hooks/connection/useConnectionActions"
import { Conversation, createConversation, sendMessage as sendMessageApi } from "@/app/api/src/services/chat/chatService"
import { Message } from "@/app/api/src/services/chat/chatService"
import { toast } from "react-toastify"
import getTokenFromCookies from "@/app/api/src/controllers/getTokenFromCookies"
import { loadUserProfile } from "@/app/api/src/controllers/userController"

const formatTime = (dateString?: string) => {
  if (!dateString) return ""

  const buildDate = (value: string) => {
    const trimmed = value.trim()
    if (!trimmed) return null

    const hasTimezoneInfo = /([zZ]|[+-]\d{2}:?\d{2})$/.test(trimmed)
    const normalized = hasTimezoneInfo ? trimmed : `${trimmed}Z`

    const parsed = new Date(normalized)
    if (!Number.isNaN(parsed.getTime())) {
      return parsed
    }

    // Último recurso: tentar parsear valor original
    const fallback = new Date(trimmed)
    return Number.isNaN(fallback.getTime()) ? null : fallback
  }

  try {
    const date = buildDate(dateString)
    if (!date) return ""

    return date.toLocaleTimeString("pt-BR", {
      hour: "2-digit",
      minute: "2-digit",
    })
  } catch {
    return ""
  }
}

export default function MensagensPage() {
  const searchParams = useSearchParams()
  const {
    conversations,
    loading: conversationsLoading,
    error: conversationsError,
    selectedConversation,
    setSelectedConversation,
    selectConversation,
    refreshConversations,
  } = useChatConversations()

  const {
    messages,
    loading: messagesLoading,
    error: messagesError,
    loadMessages,
    sendMessage: sendMessageService,
    markAsRead,
  } = useChatMessages()

  const { checkConnectionStatus, isConnected } = useConnectionActions()

  const [searchTerm, setSearchTerm] = useState("")
  const [newMessage, setNewMessage] = useState("")
  const [currentUserId, setCurrentUserId] = useState<string | null>(null)
  const [isSending, setIsSending] = useState(false)
  
  // Estado para nova conversa (quando vem do perfil)
  const [newConversationUser, setNewConversationUser] = useState<{
    id: string;
    name: string;
  } | null>(null)

  const messagesContainerRef = useRef<HTMLDivElement | null>(null)

  const scrollMessagesToBottom = useCallback(() => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight
    }
  }, [])

  // Filtrar conversas por termo de pesquisa
  const filteredConversations = conversations.filter((conv) => {
    if (!conv?.participant) return false
    const nameMatch = conv.participant.name
      ?.toLowerCase()
      .includes(searchTerm.toLowerCase())
    const emailMatch = conv.participant.email
      ?.toLowerCase()
      .includes(searchTerm.toLowerCase())
    return nameMatch || emailMatch
  })

  const handleSelectConversation = useCallback(
    async (conversation: Conversation) => {
      if (!conversation?.id) return
      setSelectedConversation(conversation)
      try {
        await selectConversation(conversation.id)
      } catch (error) {
        toast.error("Erro ao carregar conversa")
        console.error(error)
      }
    },
    [selectConversation]
  )

  // Carregar ID do usuário atual
  useEffect(() => {
    const loadCurrentUser = async () => {
      try {
        const token = getTokenFromCookies()
        if (token) {
          const user = await loadUserProfile(token)
          setCurrentUserId(user.id as string)
        }
      } catch (error) {
        console.error("Erro ao carregar usuário atual:", error)
      }
    }

    loadCurrentUser()
  }, [])

  // Processar parâmetros da URL (userId para nova conversa ou conversationId para existente)
  useEffect(() => {
    if (searchParams && !conversationsLoading) {
      const userId = searchParams.get("userId")
      const userName = searchParams.get("userName")
      const conversationId = searchParams.get("conversationId")

      // Se temos userId, verificar se já existe conversa com esse usuário
      if (userId && userName) {
          const existingConversation = conversations.find(
            (c) => c?.participant?.id === userId
          )
        
        if (existingConversation) {
          // Já existe conversa, seleciona ela
          handleSelectConversation(existingConversation)
          setNewConversationUser(null)
        } else {
          // Não existe conversa, mostra painel para iniciar nova conversa
          setNewConversationUser({ id: userId, name: userName })
          setSelectedConversation(null)
        }
      } else if (conversationId && conversations.length > 0 && !selectedConversation) {
        // Se temos conversationId, seleciona a conversa
        const conversation = conversations.find((c) => c?.id === conversationId)
        if (conversation) {
          handleSelectConversation(conversation)
        }
      }
    }
  }, [searchParams, conversations, conversationsLoading, handleSelectConversation, selectedConversation, setSelectedConversation])

  // Carregar mensagens quando conversa é selecionada
  useEffect(() => {
    if (selectedConversation?.id) {
      loadMessages(selectedConversation.id)
      markAsRead(selectedConversation.id)
    }
  }, [selectedConversation?.id, loadMessages, markAsRead])

  useEffect(() => {
    scrollMessagesToBottom()
  }, [messages, messagesLoading, selectedConversation?.id, scrollMessagesToBottom])

  const handleSendMessage = async () => {
    if (!newMessage.trim() || isSending) return
    
    // Se não tem conversa selecionada mas tem usuário para nova conversa
    if (!selectedConversation && newConversationUser) {
      await handleSendFirstMessage()
      return
    }

    if (!selectedConversation) return

    setIsSending(true)

    try {
      await sendMessageService(selectedConversation.id, newMessage)
      setNewMessage("")
      // Recarrega as mensagens para mostrar a nova
      loadMessages(selectedConversation.id)
    } catch (error) {
      console.error("Erro ao enviar mensagem:", error)
      toast.error("Erro ao enviar mensagem")
    } finally {
      setIsSending(false)
    }
  }

  // Enviar primeira mensagem (cria conversa e envia)
  const handleSendFirstMessage = async () => {
    if (!newMessage.trim() || !newConversationUser || isSending) return

    setIsSending(true)

    try {
      const token = getTokenFromCookies()
      if (!token) {
        toast.error("Token não encontrado")
        return
      }

      let conversationToUse: Conversation | null = null

      // Tentar criar a conversa
      try {
        conversationToUse = await createConversation(token, newConversationUser.id)
      } catch (createError: any) {
        const errorMessage = createError.message || ""

        // Se a conversa já existe, buscar nas conversas existentes
        if (errorMessage.includes("already exists")) {
          const { fetchConversations } = await import("@/app/api/src/services/chat/chatService")
          const response = await fetchConversations(token)
          const existingConv = response.items.find(
            (c) => c?.participant?.id === newConversationUser.id
          )
          
          if (existingConv) {
            conversationToUse = existingConv
          } else {
            throw new Error("Não foi possível encontrar a conversa existente")
          }
        } 
        // Se os usuários não estão conectados
        else if (errorMessage.includes("not connected") || errorMessage.includes("Users must be connected")) {
          toast.error("Você precisa estar conectado com este usuário para iniciar uma conversa. Envie um pedido de conexão primeiro.")
          return
        } 
        else {
          throw createError
        }
      }

      if (!conversationToUse) {
        throw new Error("Não foi possível criar ou encontrar a conversa")
      }
      
      // Enviar a mensagem
      await sendMessageApi(token, conversationToUse.id, newMessage)
      
      // Limpar estado de nova conversa
      setNewConversationUser(null)
      setNewMessage("")
      
      // Selecionar a conversa e carregar mensagens
      setSelectedConversation(conversationToUse)
      await loadMessages(conversationToUse.id)
      await refreshConversations()
      
      toast.success("Mensagem enviada!")
    } catch (error: any) {
      console.error("Erro ao enviar primeira mensagem:", error)
      toast.error(error.message || "Erro ao enviar mensagem")
    } finally {
      setIsSending(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="min-h-screen bg-[#f4f4f4] text-[#161616]">
      <Sidebar variant="static" />
      <div className="flex h-screen ml-0 min-[900px]:ml-64">
        {/* Conversations List */}
        <div className="w-[500px] border-r border-[#e0e0e0] bg-white overflow-hidden flex flex-col">
          {/* Header */}
          <div className="p-4 border-b border-[#e0e0e0] flex items-center justify-between">
            <div>
              <h1 className="text-xl font-medium">Mensagens</h1>
              <p className="text-sm text-[#525252]">
                {conversations.filter((c) => (c.unread_count || 0) > 0).length} não lidas
              </p>
            </div>
            <div className="w-48">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[#525252] h-4 w-4" />
                <input
                  type="text"
                  placeholder="Pesquisar"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-[#e0e0e0] focus:outline-none focus:border-black"
                />
              </div>
            </div>
          </div>

          {/* Conversations */}
          <div className="overflow-auto flex-1">
            {conversationsLoading ? (
              <div className="p-4 text-center text-[#525252] flex items-center justify-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                Carregando conversas...
              </div>
            ) : conversationsError ? (
              <div className="p-4 text-center text-red-500">
                Erro ao carregar conversas: {conversationsError.message}
              </div>
            ) : filteredConversations.length === 0 ? (
              <div className="p-4 text-center text-[#525252]">
                {searchTerm ? "Nenhuma conversa encontrada" : "Nenhuma conversa ainda"}
              </div>
            ) : (
              filteredConversations.map((conversation) => (
                <div
                  key={conversation.id}
                  className={`p-4 border-b border-[#e0e0e0] cursor-pointer hover:bg-[#f8f8f8] flex ${
                    selectedConversation?.id === conversation.id ? "bg-[#f4f4f4]" : ""
                  }`}
                  onClick={() => handleSelectConversation(conversation)}
                >
                  <div className="w-10 h-10 rounded-full overflow-hidden flex-shrink-0 mr-3 bg-gray-200">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={
                        conversation.participant.profile_image_url ||
                        conversation.participant.profile_picture ||
                        "/no-profile-pic.png"
                      }
                      alt={conversation.participant.name}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <h3 className="font-medium truncate">
                        {conversation.participant.name}
                      </h3>
                      {conversation.last_message_timestamp && (
                        <span className="text-xs text-[#525252] flex-shrink-0 ml-2">
                          {formatTime(conversation.last_message_timestamp)}
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-[#525252] truncate">
                      {conversation.last_message || "Inicie uma conversa"}
                    </p>
                  </div>
                  {(conversation.unread_count || 0) > 0 && (
                    <div className="ml-2 flex-shrink-0 self-center">
                      <span className="flex items-center justify-center w-5 h-5 bg-black text-white text-xs rounded-full">
                        {conversation.unread_count}
                      </span>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>

        {/* Chat Area */}
        {selectedConversation || newConversationUser ? (
          <div className="flex-1 flex flex-col">
            {/* Chat Header */}
            <div className="p-4 border-b border-[#e0e0e0] bg-white">
              <div className="flex items-center">
                <div className="w-10 h-10 rounded-full overflow-hidden mr-3 bg-gray-200">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={
                      selectedConversation?.participant?.profile_image_url ||
                      selectedConversation?.participant?.profile_picture ||
                      "/no-profile-pic.png"
                    }
                    alt={selectedConversation?.participant?.name || newConversationUser?.name || ""}
                    className="w-full h-full object-cover"
                  />
                </div>
                <div>
                  {selectedConversation?.participant?.id ? (
                    <Link
                      href={`/profile/${selectedConversation.participant.id}`}
                      className="font-medium text-[#161616] hover:underline"
                    >
                      {selectedConversation.participant.name}
                    </Link>
                  ) : (
                    <h3 className="font-medium">
                      {selectedConversation?.participant?.name || newConversationUser?.name}
                    </h3>
                  )}
                  {selectedConversation?.participant?.email && (
                    <p className="text-sm text-[#525252]">
                      {selectedConversation.participant.email}
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 p-4 overflow-auto bg-[#f4f4f4]" ref={messagesContainerRef}>
              {newConversationUser ? (
                <div className="h-full flex items-center justify-center text-[#525252]">
                  <p>Envie uma mensagem para iniciar a conversa com {newConversationUser.name}</p>
                </div>
              ) : messagesLoading ? (
                <div className="h-full flex items-center justify-center">
                  <div className="flex items-center gap-2 text-[#525252]">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Carregando mensagens...
                  </div>
                </div>
              ) : messages.length === 0 ? (
                <div className="h-full flex items-center justify-center text-[#525252]">
                  <p>Inicie uma conversa</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${
                        message.sender_id === currentUserId ? "justify-end" : "justify-start"
                      }`}
                    >
                      <div
                        className={`max-w-[70%] p-3 rounded ${
                          message.sender_id === currentUserId
                            ? "bg-black text-white"
                            : "bg-white border-l-4 border-[#e0e0e0]"
                        }`}
                      >
                        <p className="break-words">{message.content}</p>
                        <span className="text-xs opacity-70 mt-1 block">
                          {formatTime(message.created_at)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Message Input */}
            <div className="p-4 border-t border-[#e0e0e0] bg-white">
              <div className="flex items-center">
                <div className="flex-1 relative">
                  <textarea
                    placeholder="Digite sua mensagem..."
                    className="w-full pl-4 pr-20 py-3 border border-[#e0e0e0] focus:outline-none focus:border-black resize-none"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyDown={handleKeyDown}
                    rows={1}
                  />
                  <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex items-center gap-2">
                    <button className="p-1 text-[#525252] hover:text-[#161616]">
                      <Paperclip className="h-5 w-5" />
                    </button>
                    <button className="p-1 text-[#525252] hover:text-[#161616]">
                      <Smile className="h-5 w-5" />
                    </button>
                  </div>
                </div>
                <button
                  className="ml-2 px-4 py-3 bg-[#161616] text-white hover:bg-[#262626] flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
                  onClick={handleSendMessage}
                  disabled={isSending || !newMessage.trim()}
                >
                  {isSending ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin mr-2" />
                      Enviando...
                    </>
                  ) : (
                    "Enviar"
                  )}
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center bg-[#f4f4f4] text-[#525252]">
            <p>Selecione uma conversa para começar</p>
          </div>
        )}
      </div>
    </div>
  )
}
