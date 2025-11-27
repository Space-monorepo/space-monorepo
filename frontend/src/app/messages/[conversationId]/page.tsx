"use client"

import MessagesScreen from "../MessagesScreen"

type ConversationPageProps = {
  params: {
    conversationId: string
  }
}

export default function ConversationPage({ params }: ConversationPageProps) {
  return (
    <MessagesScreen
      initialConversationId={params.conversationId}
      viewMode="chatOnly"
    />
  )
}
