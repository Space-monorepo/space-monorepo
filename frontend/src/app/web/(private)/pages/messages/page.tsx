"use client"

import { useState, useEffect, useRef } from "react"
import Sidebar from "@/components/ui/sidebar"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Search, Paperclip, MoreHorizontal } from "lucide-react"
import Image from "next/image"

// Types
type Message = {
  id: number
  text: string
  sender: string
  timestamp: string
}

type Conversation = {
  id: number
  name: string
  avatar: string
  lastMessage: string
  time: string
  unread: number
  messages: Message[]
}


const initialConversations: Conversation[] = [
  {
    id: 1,
    name: "Nome do Usuário",
    avatar: "/https://t.ctcdn.com.br/GR014wWXkOpIOo0kpxSfSRnk_Jk=/959x539/smart/i598772.jpeg",
    lastMessage:
      "Lorem ipsum has been the industry's standard dummy text ever since the 1500s.",
    time: "11:24",
    unread: 5,
    messages: [],
  },
]

const socketUrl = "ws://localhost:8000/ws/chat" //TODO: Mudar para o endereço do WebSocket que está no backend

export default function MensagensPage() {
  const [conversations, setConversations] = useState<Conversation[]>(initialConversations)
  const [activeConversation, setActiveConversation] = useState<Conversation | null>(
    initialConversations[0] || null
  )
  const [message, setMessage] = useState("")
  const [socket, setSocket] = useState<WebSocket | null>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const filteredConversations = conversations.filter(
    (conv) =>
      conv.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      conv.lastMessage.toLowerCase().includes(searchQuery.toLowerCase())
  )

  useEffect(() => {
    const ws = new WebSocket(socketUrl)

    ws.onopen = () => {
      console.log("Conectado ao WebSocket")
    }

    ws.onmessage = (event) => {
      const receivedMessage = JSON.parse(event.data)
      handleIncomingMessage(receivedMessage)
    }

    ws.onclose = () => {
      console.log("Desconectado do WebSocket")
    }

    setSocket(ws)

    return () => {
      ws.close()
    }
  }, [])

  const handleIncomingMessage = (message: Message) => {
    if (!activeConversation) return

    const updatedConversations = conversations.map((conv) => {
      if (conv.id === activeConversation.id) {
        return {
          ...conv,
          messages: [...conv.messages, message],
          lastMessage: message.text,
          time: "Agora",
          unread: conv.unread + 1,
        }
      }
      return conv
    })
    setConversations(updatedConversations)

    const updatedActiveConversation = updatedConversations.find(
      (conv) => conv.id === activeConversation.id
    )
    if (updatedActiveConversation) {
      setActiveConversation(updatedActiveConversation)
    }
  }

  const handleSendMessage = () => {
    if (!message.trim() || !socket || socket.readyState !== WebSocket.OPEN || !activeConversation) return

    const newMessage: Message = {
      id: activeConversation.messages.length,
      text: message,
      sender: "user",
      timestamp: new Date().toISOString(),
    }

    socket.send(JSON.stringify(newMessage))

    const updatedConversations = conversations.map((conv) => {
      if (conv.id === activeConversation.id) {
        return {
          ...conv,
          messages: [...conv.messages, newMessage],
          lastMessage: message,
          time: "Agora",
          unread: 0,
        }
      }
      return conv
    })
    setConversations(updatedConversations)

    const updatedActiveConversation = updatedConversations.find(
      (conv) => conv.id === activeConversation.id
    )
    if (updatedActiveConversation) {
      setActiveConversation(updatedActiveConversation)
    }

    setMessage("")
  }

  const handleConversationClick = (conv: Conversation) => {
    const updatedConversations = conversations.map((c) => {
      if (c.id === conv.id) {
        return { ...c, unread: 0 }
      }
      return c
    })

    setConversations(updatedConversations)
    setActiveConversation(conv)
  }

  return (
    <div className="min-h-screen bg-gray-100 flex">
      <Sidebar />

      <div className="flex-1 flex">
        {/* Conversations List */}
        <div className="w-96 border-r bg-white">
          <div className="p-4 border-b flex justify-between items-center">
            <div>
              <h1 className="text-xl font-bold">Mensagens</h1>
              <p className="text-sm text-gray-500">
                {conversations.reduce((total, conv) => total + conv.unread, 0)} não lidas
              </p>
            </div>
            <div className="relative w-64">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                placeholder="Pesquisar"
                className="pl-9 h-9"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>

          <div className="overflow-y-auto h-[calc(100vh-8rem)]">
            {filteredConversations.map((conv) => (
              <div
                key={conv.id}
                className={`p-4 border-b hover:bg-gray-50 cursor-pointer ${
                  activeConversation?.id === conv.id ? "bg-gray-50" : ""
                }`}
                onClick={() => handleConversationClick(conv)}
              >
                <div className="flex gap-3">
                  <div className="flex-shrink-0">
                    <Image
                      src={conv.avatar || "/placeholder.svg"}
                      alt={`Avatar de ${conv.name}`}
                      width={40}
                      height={40}
                      className="rounded-full"
                    />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex justify-between items-start">
                      <h3 className="font-medium truncate">{conv.name}</h3>
                      <span className="text-xs text-gray-500 whitespace-nowrap ml-2">{conv.time}</span>
                    </div>
                    <p className="text-sm text-gray-600 line-clamp-2">{conv.lastMessage}</p>
                  </div>
                  {conv.unread > 0 && (
                    <div className="flex-shrink-0 self-center">
                      <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-black text-white text-xs">
                        {conv.unread}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Chat Window */}
        <div className="flex-1 flex flex-col bg-white">
          {/* Chat Header */}
          {activeConversation && (
            <div className="p-4 border-b flex justify-between items-center">
              <div className="flex items-center gap-3">
                <Image
                  src={activeConversation.avatar || "/placeholder.svg"}
                  alt={`Avatar de ${activeConversation.name}`}
                  width={40}
                  height={40}
                  className="rounded-full"
                />
                <div>
                  <h2 className="font-medium">{activeConversation.name}</h2>
                  <p className="text-xs text-gray-500">emaildousuario@gmail.com</p>
                </div>
              </div>
              <Button variant="ghost" size="icon">
                <MoreHorizontal className="w-5 h-5" />
              </Button>
            </div>
          )}

          {/* Messages Area */}
          <div className="flex-1 p-4 overflow-y-auto">
            <div className="space-y-4">
              {activeConversation?.messages.map((msg) => (
                <div key={msg.id} className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}>
                  <div
                    className={`max-w-[70%] rounded-lg p-3 ${
                      msg.sender === "user" ? "bg-black text-white" : "bg-gray-100 text-gray-800"
                    }`}
                  >
                    <p>{msg.text}</p>
                    <div className={`text-xs mt-1 ${msg.sender === "user" ? "text-gray-300" : "text-gray-500"}`}>
                      {new Date(msg.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                    </div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* Message Input */}
          <div className="p-4 border-t">
            <div className="flex items-end gap-2">
              <div className="flex-1 border rounded-lg overflow-hidden">
                <textarea
                  placeholder="Digite sua mensagem..."
                  className="w-full p-3 resize-none focus:outline-none min-h-[80px]"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault()
                      handleSendMessage()
                    }
                  }}
                />
                <div className="flex justify-between items-center p-2 bg-gray-50">
                  <Button variant="ghost" size="icon" className="text-gray-500">
                    <Paperclip className="w-5 h-5" />
                  </Button>
                  <div className="flex gap-2">
                    <Button variant="outline" onClick={() => setMessage("")}>
                      Descartar
                    </Button>
                    <Button className="bg-black text-white hover:bg-black/90" onClick={handleSendMessage}>
                      Enviar
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
