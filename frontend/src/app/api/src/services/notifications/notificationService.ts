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

    return data.items.map((post: PostResponse) => ({
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

    return data.items.map((post: PostResponse) => ({
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
    // Por enquanto simulado - quando tiver endpoint real, implementar aqui
    return [
        {
            id: '1',
            type: 'Conexão',
            title: 'Felipe Sousa deseja conectar-se com você',
            author: {
                id: 'user1',
                name: 'Felipe Sousa',
                username: 'felipesousa',
                profile_picture: '/ProfilePic3.svg'
            },
            community: {
                id: 'comm1',
                name: 'PUC - Campinas'
            },
            date: '3 horas atrás',
            created_at: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
            updated_at: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
            time: '',
            connection_status: 'pending',
            actions: ['Conectar-se', 'X']
        }
    ]
}

// Buscar interações (simulado até ter endpoint real)
export const fetchInteractions = async (token: string): Promise<InteractionNotification[]> => {
    // Por enquanto simulado - quando tiver endpoint real, implementar aqui
    return [
        {
            id: '1',
            type: 'Comentário',
            title: 'Felipe Sousa comentou no seu post: Parabéns pela campanha!!',
            author: {
                id: 'user1',
                name: 'Felipe Sousa',
                username: 'felipesousa',
                profile_picture: '/ProfilePic3.svg'
            },
            community: {
                id: 'comm1',
                name: 'PUC - Campinas'
            },
            date: '3 horas atrás',
            created_at: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
            updated_at: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
            time: '',
            interaction_type: 'comment',
            post_id: 'post1',
            actions: ['Curtir']
        }
    ]
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
