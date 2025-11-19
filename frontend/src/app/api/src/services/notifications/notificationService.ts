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

// Buscar conexões reais (via notificações de tipo CONNECTION)
export const fetchConnections = async (token: string): Promise<ConnectionNotification[]> => {
    try {
        const response = await fetch(`${API_URL}/notifications?type=CONNECTION`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        })

        if (!response.ok) {
            throw new Error('Erro ao carregar conexões')
        }

        const notifications = await response.json()

        console.log('Notificações de conexão recebidas:', notifications);

        // Criar um mapa para armazenar o status mais recente de cada ator
        const actorStatusMap: { [actorId: string]: ConnectionNotification } = {}

        const connectionNotifications = await Promise.all(notifications.map(async (n: any) => {
            const d = n.data || {}
            console.log('Processando notificação:', n.id, 'connection_type:', d.connection_type);

            // Para cada notificação, buscar o status atual da conexão
            let actualStatus: 'pending' | 'accepted' | 'rejected' = 'pending'

            try {
                const statusResponse = await fetch(`${API_URL}/users/connections/status/${d.actor_id}`, {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });

                if (statusResponse.ok) {
                    const connectionData = await statusResponse.json();
                    if (connectionData && connectionData.status) {
                        actualStatus = connectionData.status;
                        console.log(`Status real para ${d.actor_id}:`, actualStatus);
                    }
                }
            } catch (err) {
                console.warn('Erro ao buscar status da conexão:', err);
                // Fallback para o connection_type da notificação
                if (d.connection_type === 'request_received') {
                    actualStatus = 'pending'
                } else if (d.connection_type === 'request_accepted') {
                    actualStatus = 'accepted'
                } else if (d.connection_type === 'request_rejected') {
                    actualStatus = 'rejected'
                }
            }

            // Gerar título apropriado baseado no status real
            let title = 'Nova conexão'
            if (actualStatus === 'pending') {
                title = `Convite para se conectar com ${d.actor_name || 'alguém'}`
            } else if (actualStatus === 'accepted') {
                title = `Conexão aceita com ${d.actor_name || 'alguém'}`
            } else if (actualStatus === 'rejected') {
                title = `Conexão rejeitada com ${d.actor_name || 'alguém'}`
            }

            return {
                id: n.id,
                type: 'connections',
                title,
                author: {
                    id: d.actor_id || '',
                    name: d.actor_name || 'Usuário',
                    username: d.actor_username || 'user',
                    profile_picture: d.actor_picture || null,
                    role: d.actor_role || 'member'
                },
                community: {
                    id: d.community_id || '',
                    name: d.community_name || ''
                },
                date: new Date(n.created_at).toLocaleDateString('pt-BR'),
                created_at: n.created_at,
                updated_at: n.created_at,
                connection_status: actualStatus,
                stats: {
                    published: new Date(n.created_at).toLocaleDateString('pt-BR'),
                    accesses: 0,
                    participants: 0,
                    likes: 0,
                    comments: 0
                }
            } as ConnectionNotification
        }))

        // Filtrar para manter apenas a notificação mais recente por ator
        connectionNotifications.forEach(conn => {
            const actorId = conn.author.id
            if (!actorStatusMap[actorId] || new Date(conn.created_at) > new Date(actorStatusMap[actorId].created_at)) {
                actorStatusMap[actorId] = conn
            }
        })

        return Object.values(actorStatusMap)
    } catch (error) {
        console.error('Erro ao buscar conexões:', error)
        return []
    }
}

// Buscar interações reais (via notificações de tipo INTERACTION)
export const fetchInteractions = async (token: string): Promise<InteractionNotification[]> => {
    try {
        const response = await fetch(`${API_URL}/notifications?type=INTERACTION`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        })

        if (!response.ok) {
            throw new Error('Erro ao carregar interações')
        }

        const notifications = await response.json()

        return notifications.map((n: any) => {
            const d = n.data || {}

            // Determinar tipo de interação
            const interactionType = d.interaction_type || 'comment'

            // Gerar título apropriado
            let title = 'Nova interação'
            const postTitle = d.post_title || 'sua publicação'
            const commentContent = d.comment_content || ''

            if (interactionType === 'comment') {
                title = `Comentário em ${postTitle}`
                if (commentContent) {
                    title = `Comentou em ${postTitle}: "${commentContent.substring(0, 30)}..."`
                }
            } else if (interactionType === 'like') {
                title = `Nova curtida em ${postTitle}`
            } else if (interactionType === 'comment_like') {
                title = `Curtiu seu comentário${commentContent ? `: "${commentContent.substring(0, 30)}..."` : ''}`
            }

            return {
                id: n.id,
                type: 'interactions',
                title,
                author: {
                    id: d.actor_id || '',
                    name: d.actor_name || 'Usuário',
                    username: d.actor_username || 'user',
                    profile_picture: d.actor_picture || null,
                    role: d.actor_role || 'member'
                },
                community: {
                    id: d.community_id || '',
                    name: d.community_name || ''
                },
                date: new Date(n.created_at).toLocaleDateString('pt-BR'),
                created_at: n.created_at,
                updated_at: n.created_at,
                interaction_type: interactionType,
                post_id: d.post_id,
                comment_id: d.comment_id,
                stats: {
                    published: new Date(n.created_at).toLocaleDateString('pt-BR'),
                    accesses: 0,
                    participants: 0,
                    likes: 0,
                    comments: 0
                }
            } as InteractionNotification
        })
    } catch (error) {
        console.error('Erro ao buscar interações:', error)
        return []
    }
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
