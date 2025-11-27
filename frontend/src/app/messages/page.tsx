"use client"

import { useState, useEffect, useCallback, useRef, useMemo, Suspense } from "react"
import Link from "next/link"
import { useSearchParams } from "next/navigation"
import { Search, Paperclip, Smile, Loader2 } from "lucide-react"
import Sidebar from "@/components/ui/sidebar"
import useChatConversations from "@/app/api/src/hooks/chat/useChatConversations"
import useChatMessages from "@/app/api/src/hooks/chat/useChatMessages"
import useConnectionsList from "@/app/api/src/hooks/connection/useConnectionsList"
import { Conversation, createConversation } from "@/app/api/src/services/chat/chatService"
import { Message } from "@/app/api/src/services/chat/chatService"
import { ConnectionNotification } from "@/app/api/src/types/notifications/Notification"
import { toast } from "react-toastify"
import { WS_URL } from "@/config"
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

type ChatListItem =
  | {
    kind: "conversation"
    key: string
    name: string
    email?: string
    avatar?: string | null
    preview: string
    timestamp?: string
    unreadCount: number
    conversation: Conversation
  }
  | {
    kind: "connection"
    key: string
    name: string
    email?: string
    avatar?: string | null
    preview: string
    timestamp?: string
    connection: ConnectionNotification
  }


function MensagensPageContent() {
  const searchParams = useSearchParams()
  const {
    conversations,
    loading: conversationsLoading,
    error: conversationsError,
    selectedConversation,
    setSelectedConversation,
    selectConversation,
    refreshConversations,
    updateConversationPreview,
  } = useChatConversations()

  const {
    messages,
    loading: messagesLoading,
    error: messagesError,
    loadMessages,
    sendMessage: sendMessageService,
    markAsRead,
    addMessageOptimistic,
    replaceMessage,
    upsertMessage,
    removeMessageById,
  } = useChatMessages()

  const {
    connections: userConnections,
    loading: connectionsLoading,
    error: connectionsError,
  } = useConnectionsList()

  const [searchTerm, setSearchTerm] = useState("")
  const [newMessage, setNewMessage] = useState("")
  const [currentUserId, setCurrentUserId] = useState<string | null>(null)
  const [isSending, setIsSending] = useState(false)
  const [isWsConnected, setIsWsConnected] = useState(false)
  const [typingUsers, setTypingUsers] = useState<Record<string, string>>({})

  // Estado para nova conversa (quando vem do perfil)
  const [newConversationUser, setNewConversationUser] = useState<{
    id: string;
    name: string;
  } | null>(null)

  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const reconnectAttemptsRef = useRef(0)
  const isUnmountedRef = useRef(false)
  const pendingMessagesRef = useRef<Record<string, { conversationId: string }>>({})
  const pendingJoinAttemptsRef = useRef<
    Record<string, { attempts: number; lastAttempt: number }>
  >({})
  const joinConversationRoomRef = useRef<
    ((conversationId: string, force?: boolean) => Promise<void>) | null
  >(null)
  const conversationsPollingRef = useRef<NodeJS.Timeout | null>(null)
  const typingTimeoutsRef = useRef<Record<string, NodeJS.Timeout>>({})
  const stopTypingTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const lastTypingEventRef = useRef<number>(0)
  const selectedConversationIdRef = useRef<string | null>(null)
  const currentUserIdRef = useRef<string | null>(null)
  const joinedConversationsRef = useRef<Set<string>>(new Set())
  const previousConversationIdRef = useRef<string | null>(null)
  const messagesContainerRef = useRef<HTMLDivElement | null>(null)

  const baseWsUrl = useMemo(() => {
    if (!WS_URL) return ""
    return WS_URL.endsWith("/") ? WS_URL.slice(0, -1) : WS_URL
  }, [])

  const typingIndicatorText = useMemo(() => {
    const names = Object.values(typingUsers)
    if (!names.length) return ""
    const uniqueNames = [...new Set(names)]
    const label = uniqueNames.join(", ")
    return `${label} está digitando...`
  }, [typingUsers])

  const acceptedConnections = useMemo(
    () => userConnections.filter((conn) => conn.connection_status === "accepted"),
    [userConnections]
  )

  const conversationParticipantIds = useMemo(() => {
    const ids = new Set<string>()
    conversations.forEach((conversation) => {
      if (conversation?.participant?.id) {
        ids.add(conversation.participant.id)
      }
    })
    return ids
  }, [conversations])

  const availableConnections = useMemo(
    () =>
      acceptedConnections.filter(
        (connection) => !conversationParticipantIds.has(connection.author.id)
      ),
    [acceptedConnections, conversationParticipantIds]
  )

  const chatListItems = useMemo<ChatListItem[]>(() => {
    const formattedConversations: ChatListItem[] = conversations.map(
      (conversation) => ({
        kind: "conversation",
        key: conversation.id,
        name: conversation.participant?.name || "Usuário",
        email: conversation.participant?.email,
        avatar:
          conversation.participant?.profile_image_url ||
          conversation.participant?.profile_picture,
        preview: conversation.last_message || "Inicie uma conversa",
        timestamp: conversation.last_message_timestamp || conversation.created_at,
        unreadCount: conversation.unread_count || 0,
        conversation,
      })
    )

    const formattedConnections: ChatListItem[] = availableConnections.map(
      (connection) => ({
        kind: "connection",
        key: `connection-${connection.author.id}`,
        name: connection.author.name || connection.author.username,
        email: connection.author.username,
        avatar: connection.author.profile_picture,
        preview: "Conexão aceita. Clique para iniciar uma conversa.",
        timestamp: connection.updated_at || connection.created_at,
        connection,
      })
    )

    const combined = [...formattedConversations, ...formattedConnections]

    return combined.sort((a, b) => {
      const dateA = a.timestamp ? new Date(a.timestamp).getTime() : 0
      const dateB = b.timestamp ? new Date(b.timestamp).getTime() : 0
      return dateB - dateA
    })
  }, [availableConnections, conversations])

  const scrollMessagesToBottom = useCallback(() => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight
    }
  }, [])

  const normalizeIncomingMessage = useCallback(
    (message: Partial<Message> & { [key: string]: any }): Message => ({
      id: message.id as string,
      conversation_id: message.conversation_id as string,
      sender_id: message.sender_id as string,
      content: message.content || "",
      created_at: message.created_at as string,
      is_read: Boolean(message.is_read),
      reply_to_message_id: message.reply_to_message_id as string | undefined,
      attachments: message.attachments || [],
    }),
    []
  )

  const clearTypingUser = useCallback((userId: string) => {
    if (typingTimeoutsRef.current[userId]) {
      clearTimeout(typingTimeoutsRef.current[userId])
      delete typingTimeoutsRef.current[userId]
    }

    setTypingUsers((prev) => {
      if (!prev[userId]) return prev
      const updated = { ...prev }
      delete updated[userId]
      return updated
    })
  }, [])

  const resetTypingIndicators = useCallback(() => {
    Object.values(typingTimeoutsRef.current).forEach((timeout) => {
      clearTimeout(timeout)
    })
    typingTimeoutsRef.current = {}
    setTypingUsers({})
  }, [])

  const sendChatEvent = useCallback(
    (event: Record<string, unknown>, requiresAck: boolean = false) => {
      if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
        throw new Error("Conexão WebSocket não disponível")
      }

      const payload: Record<string, unknown> = {
        ...event,
        timestamp: Date.now(),
      }

      if (requiresAck) {
        payload.request_id =
          typeof crypto !== "undefined" && typeof crypto.randomUUID === "function"
            ? crypto.randomUUID()
            : `${Date.now()}-${Math.random()}`
      }

      wsRef.current.send(JSON.stringify(payload))
      return typeof payload.request_id === "string" ? payload.request_id : undefined
    },
    []
  )


  const handleIncomingMessage = useCallback(
    async (rawData: string) => {
      try {
        const payload = JSON.parse(rawData)

        if (payload.type === "ping") {
          try {
            sendChatEvent({ type: "pong", timestamp: Date.now() })
          } catch (error) {
            console.error("Erro ao responder ping do chat:", error)
          }
          return
        }

        if (payload.type === "conversation_joined") {
          const conversationId = payload.conversation_id ? String(payload.conversation_id) : null
          if (conversationId) {
            joinedConversationsRef.current.add(conversationId)
            delete pendingJoinAttemptsRef.current[conversationId]
          }
          return
        }

        if (payload.type === "conversation_left") {
          const conversationId = payload.conversation_id ? String(payload.conversation_id) : null
          if (conversationId) {
            joinedConversationsRef.current.delete(conversationId)
            delete pendingJoinAttemptsRef.current[conversationId]
          }
          return
        }

        if (payload.type === "message_received") {
          const incoming = normalizeIncomingMessage(payload.message || {})
          const conversationId = payload.conversation_id
            ? String(payload.conversation_id)
            : null
          if (!conversationId) {
            return
          }
          if (!joinedConversationsRef.current.has(conversationId) && joinConversationRoomRef.current) {
            joinConversationRoomRef.current(conversationId).catch((error) =>
              console.error("Erro ao tentar ingressar após receber mensagem:", error)
            )
          }
          const isCurrentConversation = selectedConversationIdRef.current === conversationId

          if (incoming.sender_id) {
            clearTypingUser(incoming.sender_id)
          }

          if (isCurrentConversation) {
            upsertMessage(incoming)
            await markAsRead(conversationId)
            updateConversationPreview(conversationId, {
              lastMessage: incoming.content || "",
              lastMessageTimestamp: incoming.created_at,
              unreadCount: 0,
            })
          } else {
            const updated = updateConversationPreview(conversationId, {
              lastMessage: incoming.content || "",
              lastMessageTimestamp: incoming.created_at,
              unreadDelta: 1,
            })

            if (!updated) {
              await refreshConversations()
            }
          }

          return
        }

        if (payload.type === "user_typing") {
          const typingUserId = String(payload.user_id || "")
          if (
            payload.conversation_id === selectedConversationIdRef.current &&
            typingUserId &&
            typingUserId !== currentUserIdRef.current
          ) {
            setTypingUsers((prev) => ({
              ...prev,
              [typingUserId]: payload.user_name || "Usuário",
            }))

            if (typingTimeoutsRef.current[typingUserId]) {
              clearTimeout(typingTimeoutsRef.current[typingUserId])
            }

            typingTimeoutsRef.current[typingUserId] = setTimeout(() => {
              clearTypingUser(typingUserId)
            }, 4000)
          }
          return
        }

        if (payload.type === "user_stopped_typing" && payload.user_id) {
          clearTypingUser(String(payload.user_id))
          return
        }

        if (payload.type === "chat_error") {
          toast.error(payload.error_message || "Erro no chat")
          return
        }

        if (payload.type === "permission_error") {
          toast.error(payload.error_message || "Você não tem permissão para essa ação.")
          return
        }

        if (typeof payload.success === "boolean" && payload.request_id) {
          const pending = pendingMessagesRef.current[payload.request_id]

          if (pending) {
            if (payload.success && payload.data) {
              const confirmedMessage = normalizeIncomingMessage(payload.data)
              replaceMessage(payload.request_id, confirmedMessage)
              updateConversationPreview(pending.conversationId, {
                lastMessage: confirmedMessage.content || "",
                lastMessageTimestamp: confirmedMessage.created_at,
                unreadCount:
                  selectedConversationIdRef.current === pending.conversationId ? 0 : undefined,
              })
            } else {
              removeMessageById(payload.request_id)
              toast.error(payload.message || "Erro ao enviar mensagem")
            }

            delete pendingMessagesRef.current[payload.request_id]
          }
        }
      } catch (error) {
        console.error("Erro ao processar mensagem do WebSocket:", error)
      }
    },
    [
      clearTypingUser,
      markAsRead,
      normalizeIncomingMessage,
      refreshConversations,
      removeMessageById,
      replaceMessage,
      sendChatEvent,
      updateConversationPreview,
      upsertMessage,
    ]
  )

  const connectWebSocket = useCallback(() => {
    if (wsRef.current || !baseWsUrl) {
      return
    }

    const token = getTokenFromCookies()
    if (!token) {
      return
    }

    try {
      const socket = new WebSocket(`${baseWsUrl}/chat/ws?token=${token}`)
      wsRef.current = socket

      socket.onopen = () => {
        setIsWsConnected(true)
        reconnectAttemptsRef.current = 0
      }

      socket.onmessage = (event) => {
        handleIncomingMessage(event.data)
      }

      socket.onerror = (event) => {
        console.error("Erro no WebSocket do chat:", event)
        socket.close()
      }

      socket.onclose = () => {
        setIsWsConnected(false)
        wsRef.current = null
        joinedConversationsRef.current.clear()

        if (isUnmountedRef.current) {
          return
        }

        const attempts = reconnectAttemptsRef.current + 1
        reconnectAttemptsRef.current = attempts
        const delay = Math.min(10000, 2000 * attempts)

        reconnectTimeoutRef.current = setTimeout(() => {
          reconnectTimeoutRef.current = null
          connectWebSocket()
        }, delay)
      }
    } catch (error) {
      console.error("Não foi possível conectar ao WebSocket do chat:", error)
    }
  }, [baseWsUrl, handleIncomingMessage])

  const waitForWebSocketReady = useCallback(async (timeoutMs: number = 5000) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      return true
    }

    const start = Date.now()
    return new Promise<boolean>((resolve) => {
      const checkReady = () => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          resolve(true)
          return
        }

        if (Date.now() - start >= timeoutMs) {
          resolve(false)
          return
        }

        setTimeout(checkReady, 150)
      }

      checkReady()
    })
  }, [])

  const ensureWebSocketReady = useCallback(async () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      return true
    }

    connectWebSocket()
    return waitForWebSocketReady()
  }, [connectWebSocket, waitForWebSocketReady])

  const joinConversationRoom = useCallback(
    async (conversationId: string, force = false) => {
      if (!conversationId) {
        return
      }

      if (!force && joinedConversationsRef.current.has(conversationId)) {
        return
      }

      const now = Date.now()
      const pending = pendingJoinAttemptsRef.current[conversationId]
      if (!force && pending && now - pending.lastAttempt < 1500) {
        return
      }

      pendingJoinAttemptsRef.current[conversationId] = {
        attempts: (pending?.attempts || 0) + 1,
        lastAttempt: now,
      }

      const ready = await ensureWebSocketReady()
      if (!ready || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
        console.warn("Não foi possível participar da conversa em tempo real:", conversationId)
        return
      }

      try {
        sendChatEvent({
          type: "join_conversation",
          conversation_id: conversationId,
        })
      } catch (error) {
        console.error("Erro ao conectar na conversa:", error)
      }
    },
    [ensureWebSocketReady, sendChatEvent]
  )

  useEffect(() => {
    joinConversationRoomRef.current = joinConversationRoom
  }, [joinConversationRoom])

  const sendStopTyping = useCallback(
    (conversationId?: string) => {
      const conversationToUse = conversationId || selectedConversationIdRef.current
      if (!conversationToUse) {
        return
      }

      if (stopTypingTimeoutRef.current) {
        clearTimeout(stopTypingTimeoutRef.current)
        stopTypingTimeoutRef.current = null
      }

      try {
        sendChatEvent({ type: "stop_typing", conversation_id: conversationToUse })
      } catch (error) {
        console.error("Erro ao enviar evento stop_typing:", error)
      }
    },
    [sendChatEvent]
  )

  const notifyTyping = useCallback(() => {
    if (!selectedConversation?.id || !isWsConnected) {
      return
    }

    const conversationId = selectedConversation.id
    const now = Date.now()

    if (now - lastTypingEventRef.current > 1500) {
      try {
        sendChatEvent({ type: "typing", conversation_id: conversationId })
        lastTypingEventRef.current = now
      } catch (error) {
        console.error("Erro ao enviar evento typing:", error)
      }
    }

    if (stopTypingTimeoutRef.current) {
      clearTimeout(stopTypingTimeoutRef.current)
    }

    stopTypingTimeoutRef.current = setTimeout(() => {
      if (selectedConversationIdRef.current === conversationId) {
        sendStopTyping(conversationId)
      }
    }, 2500)
  }, [isWsConnected, selectedConversation?.id, sendChatEvent, sendStopTyping])

  const sendMessageRealtime = useCallback(
    async (conversationId: string, rawContent: string) => {
      const trimmed = rawContent.trim()
      if (!trimmed) return

      const userId = currentUserIdRef.current
      if (!userId) {
        throw new Error("Usuário não identificado. Recarregue a página e tente novamente.")
      }

      const wsReady = await ensureWebSocketReady()
      if (!wsReady) {
        toast.warning("Conexão em tempo real indisponível. Tentando enviar via API...")
        await sendMessageService(conversationId, trimmed)
        updateConversationPreview(conversationId, {
          lastMessage: trimmed,
          lastMessageTimestamp: new Date().toISOString(),
          unreadCount: selectedConversationIdRef.current === conversationId ? 0 : undefined,
        })
        return
      }

      const requestId = sendChatEvent(
        {
          type: "send_message",
          conversation_id: conversationId,
          content: trimmed,
        },
        true
      )

      if (!requestId) {
        throw new Error("Não foi possível iniciar o envio em tempo real.")
      }

      pendingMessagesRef.current[requestId] = { conversationId }

      const optimisticMessage: Message = {
        id: requestId,
        conversation_id: conversationId,
        sender_id: userId,
        content: trimmed,
        created_at: new Date().toISOString(),
        is_read: true,
      }

      addMessageOptimistic(optimisticMessage)
      updateConversationPreview(conversationId, {
        lastMessage: trimmed,
        lastMessageTimestamp: optimisticMessage.created_at,
        unreadCount: 0,
      })
    },
    [
      addMessageOptimistic,
      ensureWebSocketReady,
      sendChatEvent,
      sendMessageService,
      updateConversationPreview,
    ]
  )

  useEffect(() => {
    selectedConversationIdRef.current = selectedConversation?.id || null
  }, [selectedConversation?.id])

  useEffect(() => {
    currentUserIdRef.current = currentUserId
  }, [currentUserId])

  useEffect(() => {
    resetTypingIndicators()
  }, [resetTypingIndicators, selectedConversation?.id])

  useEffect(() => {
    if (!baseWsUrl) return
    connectWebSocket()

    return () => {
      isUnmountedRef.current = true
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (stopTypingTimeoutRef.current) {
        clearTimeout(stopTypingTimeoutRef.current)
        stopTypingTimeoutRef.current = null
      }
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        joinedConversationsRef.current.forEach((conversationId) => {
          try {
            sendChatEvent({
              type: "leave_conversation",
              conversation_id: conversationId,
            })
          } catch (error) {
            // ignore
            console.error("Erro ao sair da conversa:", error)
          }
        })
      }
      joinedConversationsRef.current.clear()
      pendingJoinAttemptsRef.current = {}
      wsRef.current?.close()
    }
  }, [baseWsUrl, connectWebSocket])

  useEffect(() => {
    if (selectedConversation?.id) {
      updateConversationPreview(selectedConversation.id, { unreadCount: 0 })
    }
  }, [selectedConversation?.id, updateConversationPreview])

  useEffect(() => {
    const previousConversationId = previousConversationIdRef.current
    const currentConversationId = selectedConversation?.id || null

    if (
      previousConversationId &&
      previousConversationId !== currentConversationId
    ) {
      sendStopTyping(previousConversationId)
    }

    previousConversationIdRef.current = currentConversationId
  }, [selectedConversation?.id, sendStopTyping])

  // Filtrar conversas e conexões por termo de pesquisa
  const filteredChatItems = useMemo(() => {
    if (!searchTerm.trim()) {
      return chatListItems
    }

    const term = searchTerm.toLowerCase()
    return chatListItems.filter((item) => {
      const nameMatch = item.name?.toLowerCase().includes(term)
      const emailMatch = item.email?.toLowerCase().includes(term)
      return nameMatch || emailMatch
    })
  }, [chatListItems, searchTerm])

  const handleSelectConversation = useCallback(
    async (conversation: Conversation) => {
      if (!conversation?.id) return
      setSelectedConversation(conversation)
      setNewConversationUser(null)
      updateConversationPreview(conversation.id, { unreadCount: 0 })
      joinConversationRoom(conversation.id, true).catch((error) =>
        console.error("Erro ao ingressar na conversa selecionada:", error)
      )
      try {
        await selectConversation(conversation.id)
      } catch (error) {
        toast.error("Erro ao carregar conversa")
        console.error(error)
      }
    },
    [joinConversationRoom, selectConversation, updateConversationPreview]
  )

  const handleSelectConnection = useCallback(
    (connection: ConnectionNotification) => {
      const existingConversation = conversations.find(
        (conversation) => conversation.participant?.id === connection.author.id
      )

      if (existingConversation) {
        handleSelectConversation(existingConversation)
        return
      }

      setSelectedConversation(null)
      setNewConversationUser({
        id: connection.author.id,
        name: connection.author.name || connection.author.username,
      })
    },
    [conversations, handleSelectConversation]
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
      updateConversationPreview(selectedConversation.id, { unreadCount: 0 })
    }
  }, [selectedConversation?.id, loadMessages, markAsRead, updateConversationPreview])

  useEffect(() => {
    scrollMessagesToBottom()
  }, [messages, messagesLoading, selectedConversation?.id, scrollMessagesToBottom])

  useEffect(() => {
    const POLLING_INTERVAL_MS = 15000

    const runPolling = async () => {
      try {
        await refreshConversations()
      } catch (error) {
        console.error("Erro ao atualizar conversas automaticamente:", error)
      }
    }

    conversationsPollingRef.current = setInterval(runPolling, POLLING_INTERVAL_MS)

    return () => {
      if (conversationsPollingRef.current) {
        clearInterval(conversationsPollingRef.current)
        conversationsPollingRef.current = null
      }
    }
  }, [refreshConversations])

  useEffect(() => {
    if (!isWsConnected) {
      joinedConversationsRef.current.clear()
      pendingJoinAttemptsRef.current = {}
      return
    }

    conversations.forEach((conversation) => {
      if (conversation?.id) {
        joinConversationRoom(conversation.id).catch((error) => {
          console.error("Erro ao ingressar na conversa:", conversation.id, error)
        })
      }
    })
  }, [conversations, isWsConnected, joinConversationRoom])

  useEffect(() => {
    if (!isWsConnected) {
      return
    }

    const retryInterval = setInterval(() => {
      Object.keys(pendingJoinAttemptsRef.current).forEach((conversationId) => {
        if (joinedConversationsRef.current.has(conversationId)) {
          delete pendingJoinAttemptsRef.current[conversationId]
          return
        }

        const info = pendingJoinAttemptsRef.current[conversationId]
        const now = Date.now()
        if (!info || now - info.lastAttempt > 4000) {
          joinConversationRoom(conversationId, true).catch((error) => {
            console.error(
              "Erro ao tentar novamente ingressar na conversa:",
              conversationId,
              error
            )
          })
        }
      })
    }, 4000)

    return () => clearInterval(retryInterval)
  }, [isWsConnected, joinConversationRoom])

  useEffect(() => {
    const existingIds = new Set(
      conversations.map((conversation) => conversation.id).filter(Boolean) as string[]
    )

    joinedConversationsRef.current.forEach((conversationId) => {
      if (!existingIds.has(conversationId)) {
        joinedConversationsRef.current.delete(conversationId)
        delete pendingJoinAttemptsRef.current[conversationId]
      }
    })
  }, [conversations])

  const handleSendMessage = async () => {
    if (!newMessage.trim() || isSending) return

    if (!selectedConversation && newConversationUser) {
      await handleSendFirstMessage()
      return
    }

    if (!selectedConversation) return

    setIsSending(true)

    try {
      await sendMessageRealtime(selectedConversation.id, newMessage)
      setNewMessage("")
      sendStopTyping(selectedConversation.id)
    } catch (error) {
      console.error("Erro ao enviar mensagem:", error)
      toast.error((error as Error).message || "Erro ao enviar mensagem")
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

      const firstMessageContent = newMessage
      selectedConversationIdRef.current = conversationToUse.id
      await sendMessageRealtime(conversationToUse.id, firstMessageContent)
      setNewConversationUser(null)
      setNewMessage("")
      setSelectedConversation(conversationToUse)
      await loadMessages(conversationToUse.id)
      await refreshConversations()
      sendStopTyping(conversationToUse.id)

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
            {conversationsLoading || connectionsLoading ? (
              <div className="p-4 text-center text-[#525252] flex items-center justify-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                Carregando conversas e conexões...
              </div>
            ) : conversationsError || connectionsError ? (
              <div className="p-4 text-center text-red-500">
                Erro ao carregar lista:{" "}
                {(conversationsError || connectionsError)?.message || "Tente novamente"}
              </div>
            ) : filteredChatItems.length === 0 ? (
              <div className="p-4 text-center text-[#525252]">
                {searchTerm ? "Nenhum resultado encontrado" : "Nenhuma conexão disponível"}
              </div>
            ) : (
              filteredChatItems.map((item) => {
                const isConversationSelected =
                  item.kind === "conversation" &&
                  selectedConversation?.id === item.conversation.id
                const isConnectionSelected =
                  item.kind === "connection" &&
                  !selectedConversation &&
                  newConversationUser?.id === item.connection.author.id

                const isSelected = isConversationSelected || isConnectionSelected
                const avatarSrc =
                  item.avatar && item.avatar.length > 0 ? item.avatar : "/no-profile-pic.png"

                return (
                  <div
                    key={item.key}
                    className={`p-4 border-b border-[#e0e0e0] cursor-pointer hover:bg-[#f8f8f8] flex ${isSelected ? "bg-[#f4f4f4]" : ""
                      }`}
                    onClick={() =>
                      item.kind === "conversation"
                        ? handleSelectConversation(item.conversation)
                        : handleSelectConnection(item.connection)
                    }
                  >
                    <div className="w-10 h-10 rounded-full overflow-hidden flex-shrink-0 mr-3 bg-gray-200">
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img src={avatarSrc} alt={item.name} className="w-full h-full object-cover" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-1">
                        <h3 className="font-medium truncate">{item.name}</h3>
                        {item.timestamp && (
                          <span className="text-xs text-[#525252] flex-shrink-0 ml-2">
                            {formatTime(item.timestamp)}
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-[#525252] truncate">{item.preview}</p>
                      {item.kind === "connection" && (
                        <span className="inline-block mt-1 text-[11px] uppercase tracking-wide text-[#161616]">
                          Conexão
                        </span>
                      )}
                    </div>
                    {item.kind === "conversation" && item.unreadCount > 0 && (
                      <div className="ml-2 flex-shrink-0 self-center">
                        <span className="flex items-center justify-center w-5 h-5 bg-black text-white text-xs rounded-full">
                          {item.unreadCount}
                        </span>
                      </div>
                    )}
                  </div>
                )
              })
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
                  {typingIndicatorText && (
                    <p className="text-xs text-green-600 mt-1">{typingIndicatorText}</p>
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
                      className={`flex ${message.sender_id === currentUserId ? "justify-end" : "justify-start"
                        }`}
                    >
                      <div
                        className={`max-w-[70%] p-3 rounded ${message.sender_id === currentUserId
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
                    onChange={(e) => {
                      setNewMessage(e.target.value)
                      notifyTyping()
                    }}
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
                  disabled={isSending || !newMessage.trim() || !currentUserId}
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

export default function MensagensPage() {
  return (
    <Suspense fallback={<div>Carregando...</div>}>
      <MensagensPageContent />
    </Suspense>
  )
}
