export type NotificationType = "campaigns" | "announcements" | "connections" | "interactions"

export interface NotificationAuthor {
    id: string
    name: string
    username: string
    profile_picture?: string | null
    role?: string
}

export interface NotificationCommunity {
    id: string
    name: string
}

export interface NotificationStats {
    published: string
    accesses: number
    participants: number
    likes: number
    comments: number
}

export interface BaseNotification {
    id: string
    type: string
    title: string
    author: NotificationAuthor
    community: NotificationCommunity
    date: string
    created_at: string
    updated_at: string
    time?: string // Para compatibilidade com o componente existente
    actions?: string[]
    status?: string
    description?: string
    stats?: NotificationStats
    image_url?: string
}

export interface CampaignNotification extends BaseNotification {
    // Específico para campanhas
}

export interface AnnouncementNotification extends BaseNotification {
    // Específico para anúncios
}

export interface ConnectionNotification extends BaseNotification {
    connection_status: 'pending' | 'accepted' | 'rejected'
}

export interface InteractionNotification extends BaseNotification {
    interaction_type: 'comment' | 'like' | 'participation'
    post_id?: string
    comment_id?: string
}

export type Notification = CampaignNotification | AnnouncementNotification | ConnectionNotification | InteractionNotification

export interface NotificationsResponse {
    campaigns: CampaignNotification[]
    announcements: AnnouncementNotification[]
    connections: ConnectionNotification[]
    interactions: InteractionNotification[]
}
