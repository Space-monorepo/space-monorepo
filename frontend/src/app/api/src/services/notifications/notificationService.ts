import { API_URL } from '@/config'
import { PostsListFeed, PostResponse } from '@/app/api/src/types/posts/Post'
import { NotificationsResponse, CampaignNotification, AnnouncementNotification, ConnectionNotification, InteractionNotification } from '@/app/api/src/types/notifications/Notification'

// Buscar campanhas (posts do tipo campaign)
export const fetchCampaigns = async (token: string): Promise<CampaignNotification[]> => {
    const response = await fetch(`${API_URL}/posts/feed?type=campaign`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
    })

    if (!response.ok) {
        throw new Error('Erro ao carregar campanhas')
    }

    const data: PostsListFeed = await response.json()

    // Garantir que retornamos apenas posts do tipo "campaign" (por precaução caso o endpoint retorne itens mistos)
    return data.items
        .filter((post: PostResponse) => post.type_post === 'campaign')
        .map((post: PostResponse) => ({
            id: post.id,
            type: 'Campanha',
            title: post.title,
            author: {
                id: post.user.id,
                name: post.user.name,
                username: post.user.username || '',
                profile_picture: post.user.profile_picture,
                role: post.user.role // Adiciona a role do backend
            },
            community: {
                id: post.community.id,
                name: post.community.name
            },
            date: new Date(post.created_at).toLocaleDateString('pt-BR'),
            created_at: post.created_at,
            updated_at: post.updated_at,
            time: `${post.likes_count + post.comments_count}`,
            description: post.content,
            status: post.status === 'active' ? 'Ativa' : post.status === 'reported' ? 'Em análise' : 'Suspensa',
            stats: {
                published: new Date(post.created_at).toLocaleDateString('pt-BR'),
                accesses: (post as any).accesses ?? 0, // Usar campo real se existir
                participants: (post as any).participants ?? 0, // Usar campo real se existir
                likes: post.likes_count,
                comments: post.comments_count
            },
            image_url: post.image_url || undefined
        }))
}

// Buscar avisos oficiais (posts do tipo announcement)
export const fetchAnnouncements = async (token: string): Promise<AnnouncementNotification[]> => {
    const response = await fetch(`${API_URL}/posts/feed?type=announcement`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
    })

    if (!response.ok) {
        throw new Error('Erro ao carregar avisos oficiais')
    }

    const data: PostsListFeed = await response.json()

    // Garantir que retornamos apenas posts do tipo "announcement"
    return data.items
        .filter((post: PostResponse) => post.type_post === 'announcement')
        .map((post: PostResponse) => ({
            id: post.id,
            type: 'Anúncio',
            title: post.title,
            author: {
                id: post.user.id,
                name: post.user.name,
                username: post.user.username || '',
                profile_picture: post.user.profile_picture,
                role: post.user.role // Adiciona a role do backend
            },
            community: {
                id: post.community.id,
                name: post.community.name
            },
            date: new Date(post.created_at).toLocaleDateString('pt-BR'),
            created_at: post.created_at,
            updated_at: post.updated_at,
            time: `${post.likes_count + post.comments_count}`,
            description: post.content,
            image_url: post.image_url || undefined,
            stats: {
                published: new Date(post.created_at).toLocaleDateString('pt-BR'),
                accesses: (post as any).accesses ?? 0,
                participants: (post as any).participants ?? 0,
                likes: post.likes_count,
                comments: post.comments_count
            },
            actions: ['Promover', 'Comentar']
        }))
}

// Buscar conexões (simulado até ter endpoint real)
export const fetchConnections = async (token: string): Promise<ConnectionNotification[]> => {
    // Quando a API real estiver pronta, implemente aqui a chamada fetch para o backend
    return [];
}

// Buscar interações (simulado até ter endpoint real)
export const fetchInteractions = async (token: string): Promise<InteractionNotification[]> => {
    // Quando a API real estiver pronta, implemente aqui a chamada fetch para o backend
    return [];
}

// Buscar todas as notificações
export const fetchNotifications = async (token: string): Promise<NotificationsResponse> => {
    try {
        const [campaigns, announcements, connections, interactions] = await Promise.all([
            fetchCampaigns(token),
            fetchAnnouncements(token),
            fetchConnections(token),
            fetchInteractions(token)
        ])

        return {
            campaigns,
            announcements,
            connections,
            interactions
        }
    } catch (error) {
        console.error('Erro ao buscar notificações:', error)
        throw error
    }
}
