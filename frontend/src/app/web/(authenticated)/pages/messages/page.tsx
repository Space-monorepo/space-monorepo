"use client"

import { useState } from "react"
import { Search, Paperclip, Smile } from "lucide-react"
import Sidebar from "@/components/ui/sidebar"

type Message = {
  id: number
  content: string
  sender: "user" | "contact"
  timestamp: string
}

type Conversation = {
  id: number
  name: string
  avatar: string
  lastMessage: string
  time: string
  unread: number
  email?: string
  messages?: Message[]
}

export default function MensagensPage() {
  const [conversations, setConversations] = useState<Conversation[]>([
    {
      id: 1,
      name: "Nome do Usuário",
      avatar: "/ProfilePic2.svg",
      lastMessage:
        "Lorem ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining...",
      time: "11:24",
      unread: 5,
      email: "emaildousuario@gmail.com",
      messages: [
        {
          id: 1,
          content: "Olá, colega! Consegue comparecer amanhã na campanha?",
          sender: "contact",
          timestamp: "11:20",
        },
        {
          id: 2,
          content: "Fala companheiro, consigo sim, claro!",
          sender: "user",
          timestamp: "11:24",
        },
      ],
    },
    {
      id: 2,
      name: "Nome do Usuário",
      avatar: "/ProfilePic3.svg",
      lastMessage:
        "At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident, similique sunt in culpa qui officia deserunt mollitia animi...",
      time: "11:24",
      unread: 2,
      email: "emaildousuario@gmail.com",
    },
    {
      id: 3,
      name: "Nome do Usuário",
      avatar: "/ProfilePic4.svg",
      lastMessage:
        "It has survived not only five centuries, but also the leap into electronic typesetting, remaining...",
      time: "11:24",
      unread: 1,
      email: "emaildousuario@gmail.com",
    },
    {
      id: 4,
      name: "Nome do Usuário",
      avatar: "/ProfilePic5.svg",
      lastMessage: "It has survived not only five centuries",
      time: "11:24",
      unread: 0,
      email: "emaildousuario@gmail.com",
    },
    {
      id: 5,
      name: "Nome do Usuário",
      avatar: "/ProfilePic6.svg",
      lastMessage:
        "There are many variations of passages of Lorem Ipsum available, but the majority have suffered alteration in some form, by injected humour, or randomised words which don't look even slightly believable.",
      time: "11:24",
      unread: 0,
      email: "emaildousuario@gmail.com",
    },
    {
      id: 6,
      name: "Nome do Usuário",
      avatar: "ProfilePic1.svg",
      lastMessage:
        "It has survived not only five centuries, but also the leap into electronic typesetting, remaining...",
      time: "11:24",
      unread: 0,
      email: "emaildousuario@gmail.com",
    },
  ])

  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(conversations[0])
  const [newMessage, setNewMessage] = useState("")

  const handleSendMessage = () => {
    if (!newMessage.trim() || !selectedConversation) return

    const updatedConversations = conversations.map((conv) => {
      if (conv.id === selectedConversation.id) {
        const updatedMessages = [
          ...(conv.messages || []),
          {
            id: Date.now(),
            content: newMessage,
            sender: "user",
            timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          } as const,
        ]

        return {
          ...conv,
          messages: updatedMessages,
          lastMessage: newMessage,
        }
      }
      return conv
    })

    setConversations(updatedConversations)
    setSelectedConversation(updatedConversations.find((c) => c.id === selectedConversation.id) || null)
    setNewMessage("")
  }

  return (
    <div className="min-h-screen bg-[#f4f4f4] text-[#161616]">
      <Sidebar variant="static"/>
      <div className="ml-64 flex h-screen">
        {/* Conversations List */}
        <div className="w-[500px] border-r border-[#e0e0e0] bg-white overflow-hidden flex flex-col">
          {/* Header */}
          <div className="p-4 border-b border-[#e0e0e0] flex items-center justify-between">
            <div>
              <h1 className="text-xl font-medium">Mensagens</h1>
              <p className="text-sm text-[#525252]">25 não lidas</p>
            </div>
            <div className="w-48">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[#525252] h-4 w-4" />
                <input
                  type="text"
                  placeholder="Pesquisar"
                  className="w-full pl-10 pr-4 py-2 border border-[#e0e0e0] focus:outline-none focus:border-black"
                />
              </div>
            </div>
          </div>

          {/* Conversations */}
          <div className="overflow-auto flex-1">
            {conversations.map((conversation) => (
              <div
                key={conversation.id}
                className={`p-4 border-b border-[#e0e0e0] cursor-pointer hover:bg-[#f8f8f8] flex ${
                  selectedConversation?.id === conversation.id ? "bg-[#f4f4f4]" : ""
                }`}
                onClick={() => setSelectedConversation(conversation)}
              >
                <div className="w-10 h-10 rounded-full overflow-hidden flex-shrink-0 mr-3">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={conversation.avatar || "/ProfilePic2.svg"}
                    alt={conversation.name}
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <h3 className="font-medium truncate">{conversation.name}</h3>
                    <span className="text-xs text-[#525252] flex-shrink-0 ml-2">{conversation.time}</span>
                  </div>
                  <p className="text-sm text-[#525252] truncate">{conversation.lastMessage}</p>
                </div>
                {conversation.unread > 0 && (
                  <div className="ml-2 flex-shrink-0 self-center">
                    <span className="flex items-center justify-center w-5 h-5 bg-black text-white text-xs rounded-full">
                      {conversation.unread}
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Chat Area */}
        {selectedConversation ? (
          <div className="flex-1 flex flex-col">
            {/* Chat Header */}
            <div className="p-4 border-b border-[#e0e0e0] bg-white">
              <div className="flex items-center">
                <div className="w-10 h-10 rounded-full overflow-hidden mr-3">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={selectedConversation.avatar || "/ProfilePic2.svg"}
                    alt={selectedConversation.name}
                    className="w-full h-full object-cover"
                  />
                </div>
                <div>
                  <h3 className="font-medium">{selectedConversation.name}</h3>
                  {selectedConversation.email && <p className="text-sm text-[#525252]">{selectedConversation.email}</p>}
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 p-4 overflow-auto bg-[#f4f4f4]">
              {selectedConversation.messages ? (
                <div className="space-y-4">
                  {selectedConversation.messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"}`}
                    >
                      <div
                        className={`max-w-[70%] p-3 ${
                          message.sender === "user" ? "bg-black text-white" : "bg-white border-l-4 border-[#e0e0e0]"
                        }`}
                      >
                        <p>{message.content}</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="h-full flex items-center justify-center text-[#525252]">
                  <p>Inicie uma conversa</p>
                </div>
              )}
            </div>

            {/* Message Input */}
            <div className="p-4 border-t border-[#e0e0e0] bg-white">
              <div className="flex items-center">
                <div className="flex-1 relative">
                  <input
                    type="text"
                    placeholder="Digite sua mensagem..."
                    className="w-full pl-4 pr-20 py-3 border border-[#e0e0e0] focus:outline-none focus:border-black"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        handleSendMessage()
                      }
                    }}
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
                  className="ml-2 px-4 py-3 bg-[#161616] text-white hover:bg-[#262626] flex items-center"
                  onClick={handleSendMessage}
                >
                  Enviar
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
