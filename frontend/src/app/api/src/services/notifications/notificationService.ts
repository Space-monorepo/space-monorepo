import { API_URL } from '@/config'
import { PostsListFeed, PostResponse } from '@/app/api/src/types/posts/Post'
import { NotificationsResponse, CampaignNotification, AnnouncementNotification, ConnectionNotification, InteractionNotification } from '@/app/api/src/types/notifications/Notification'

// Buscar campanhas (posts do tipo campaign)
export const fetchCampaigns = async (token: string, communityId: string): Promise<CampaignNotification[]> => {
    const url = `${API_URL}/notifications?type=CAMPAIGN${communityId ? `&community_id=${communityId}` : ''}`;

    const response = await fetch(url, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Erro ao carregar campanhas: ${response.status} ${response.statusText}`);
    }

    const notifications = await response.json()

    if (!Array.isArray(notifications)) {
        return [];
    }

    return notifications.map((n: any) => {
        const d = n.data || {}
        const campaign = d.campaign || d.campaign_data || {}
        const post = d.post || campaign.post || null

        if (!post) return null

        const user = post.user || d.actor || { id: '', name: 'Usuário', username: '' }
        const community = post.community || { id: d.community_id || '', name: d.community_name || '' }

        return {
            id: post.id,
            type: 'Campanha',
            title: post.title,
            author: {
                id: user.id,
                name: user.name,
                username: user.username || '',
                profile_picture: user.profile_picture,
                role: user.role
            },
            community: {
                id: community.id,
                name: community.name
            },
            date: new Date(post.created_at).toLocaleDateString('pt-BR'),
            created_at: post.created_at,
            updated_at: post.updated_at,
            time: `${(post.likes_count || 0) + (post.comments_count || 0)}`,
            description: post.content,
            status: campaign.status_campaign || d.status_campaign || campaign.status || 'unknown',
            stats: {
                published: new Date(post.created_at).toLocaleDateString('pt-BR'),
                accesses: (post as any).accesses ?? 0,
                participants: campaign.current_participants ?? d.current_participants ?? 0,
                likes: post.likes_count ?? 0,
                comments: post.comments_count ?? 0
            },
            image_url: post.image_url || undefined,
            target_participants: campaign.target_participants ?? d.target_participants ?? 0,
            current_participants: campaign.current_participants ?? d.current_participants ?? 0
        }
    }).filter(Boolean) as CampaignNotification[];
}

// Buscar avisos oficiais (posts do tipo announcement)
export const fetchAnnouncements = async (token: string, communityId?: string): Promise<AnnouncementNotification[]> => {
    if (!communityId) {
        return [];
    }

    const url = `${API_URL}/notifications?type=OFFICIAL_NOTICE&community_id=${communityId}`

    const response = await fetch(url, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })

    if (!response.ok) {
        throw new Error('Erro ao carregar avisos oficiais')
    }

    const notifications = await response.json()

    if (!Array.isArray(notifications)) return []

    return notifications
        .map((n: any) => {
            const d = n.data || {}
            const post = d.post || d.announcement || null
            if (!post) return null

            // sometimes the notification may signal the type, prefer explicit announcement posts
            const typePost = post.type_post || d.type_post || n.type || ''
            if (typePost && typePost.toLowerCase() !== 'announcement' && typePost.toLowerCase() !== 'official_notice') return null

            const user = post.user || d.actor || { id: '', name: 'Usuário', username: '' }
            const community = post.community || { id: d.community_id || '', name: d.community_name || '' }

            return {
                id: post.id,
                type: 'Anúncio',
                title: post.title,
                author: {
                    id: user.id,
                    name: user.name,
                    username: user.username || '',
                    profile_picture: user.profile_picture,
                    role: user.role
                },
                community: {
                    id: community.id,
                    name: community.name
                },
                date: new Date(post.created_at).toLocaleDateString('pt-BR'),
                created_at: post.created_at,
                updated_at: post.updated_at,
                time: `${(post.likes_count || 0) + (post.comments_count || 0)}`,
                description: post.content,
                image_url: post.image_url || undefined,
                stats: {
                    published: new Date(post.created_at).toLocaleDateString('pt-BR'),
                    accesses: (post as any).accesses ?? 0,
                    participants: (post as any).participants ?? 0,
                    likes: post.likes_count ?? 0,
                    comments: post.comments_count ?? 0
                },
                actions: ['Promover', 'Comentar']
            }
        })
        .filter(Boolean) as AnnouncementNotification[]
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

        const actorStatusMap: { [actorId: string]: ConnectionNotification } = {}

        const connectionNotifications = await Promise.all(notifications.map(async (n: any) => {
            const d = n.data || {}

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
                    }
                }
            } catch (err) {
                if (d.connection_type === 'request_received') {
                    actualStatus = 'pending'
                } else if (d.connection_type === 'request_accepted') {
                    actualStatus = 'accepted'
                } else if (d.connection_type === 'request_rejected') {
                    actualStatus = 'rejected'
                }
            }

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

        connectionNotifications.forEach(conn => {
            const actorId = conn.author.id
            if (!actorStatusMap[actorId] || new Date(conn.created_at) > new Date(actorStatusMap[actorId].created_at)) {
                actorStatusMap[actorId] = conn
            }
        })

        return Object.values(actorStatusMap)
    } catch (error) {
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

            const interactionType = d.interaction_type || 'comment'

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
        return []
    }
}

// Buscar todas as notificações
export const fetchNotifications = async (token: string, communityId?: string): Promise<NotificationsResponse> => {
    try {
        const campaignsPromise = communityId ? fetchCampaigns(token, communityId) : Promise.resolve([]);

        const [campaigns, announcements, connections, interactions] = await Promise.all([
            campaignsPromise,
            fetchAnnouncements(token, communityId),
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
        throw error
    }
}
