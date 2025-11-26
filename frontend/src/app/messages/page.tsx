"use client"

import { useState, useEffect } from "react"
import { Search, Paperclip, Smile, Loader2 } from "lucide-react"
import Sidebar from "@/components/ui/sidebar"
import useChatConversations from "@/app/api/src/hooks/chat/useChatConversations"
import useChatMessages from "@/app/api/src/hooks/chat/useChatMessages"
import useConnectionActions from "@/app/api/src/hooks/connection/useConnectionActions"
import { Conversation } from "@/app/api/src/services/chat/chatService"
import { Message } from "@/app/api/src/services/chat/chatService"
import { toast } from "react-toastify"
import getTokenFromCookies from "@/app/api/src/controllers/getTokenFromCookies"
import { loadUserProfile } from "@/app/api/src/controllers/userController"

export default function MensagensPage() {
  const {
    conversations,
    loading: conversationsLoading,
    error: conversationsError,
    selectedConversation,
    setSelectedConversation,
    selectConversation,
    createNewConversation,
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

  // Carregar mensagens quando conversa é selecionada
  useEffect(() => {
    if (selectedConversation?.id) {
      loadMessages(selectedConversation.id)
      markAsRead(selectedConversation.id)
    }
  }, [selectedConversation?.id, loadMessages, markAsRead])

  // Filtrar conversas por termo de pesquisa
  const filteredConversations = conversations.filter((conv) =>
    conv.participant.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    conv.participant.email.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const handleSelectConversation = async (conversation: Conversation) => {
    setSelectedConversation(conversation)
    try {
      await selectConversation(conversation.id)
    } catch (error) {
      toast.error("Erro ao carregar conversa")
      console.error(error)
    }
  }

  const handleSendMessage = async () => {
    if (!newMessage.trim() || !selectedConversation || isSending) return

    setIsSending(true)

    try {
      // Criar objeto de mensagem otimista
      const optimisticMessage: Message = {
        id: Date.now().toString(),
        content: newMessage,
        sender_id: currentUserId || "",
        conversation_id: selectedConversation.id,
        created_at: new Date().toISOString(),
        is_read: true,
      }

      // Adicionar mensagem localmente para feedback imediato
      // Fazer requisição para enviar
      await sendMessageService(selectedConversation.id, newMessage)
      setNewMessage("")
      toast.success("Mensagem enviada!")
    } catch (error) {
      console.error("Erro ao enviar mensagem:", error)
      toast.error("Erro ao enviar mensagem")
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
                          {new Date(conversation.last_message_timestamp).toLocaleTimeString(
                            [],
                            { hour: "2-digit", minute: "2-digit" }
                          )}
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
        {selectedConversation ? (
          <div className="flex-1 flex flex-col">
            {/* Chat Header */}
            <div className="p-4 border-b border-[#e0e0e0] bg-white">
              <div className="flex items-center">
                <div className="w-10 h-10 rounded-full overflow-hidden mr-3 bg-gray-200">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={
                      selectedConversation.participant.profile_image_url ||
                      selectedConversation.participant.profile_picture ||
                      "/no-profile-pic.png"
                    }
                    alt={selectedConversation.participant.name}
                    className="w-full h-full object-cover"
                  />
                </div>
                <div>
                  <h3 className="font-medium">{selectedConversation.participant.name}</h3>
                  {selectedConversation.participant.email && (
                    <p className="text-sm text-[#525252]">
                      {selectedConversation.participant.email}
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 p-4 overflow-auto bg-[#f4f4f4]">
              {messagesLoading ? (
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
                          {new Date(message.created_at).toLocaleTimeString([], {
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
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
