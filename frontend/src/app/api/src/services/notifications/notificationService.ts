import { API_URL } from '@/config'
import { PostsListFeed, PostResponse } from '@/app/api/src/types/posts/Post'
import { NotificationsResponse, CampaignNotification, AnnouncementNotification, ConnectionNotification, InteractionNotification } from '@/app/api/src/types/notifications/Notification'

// Helper function to fetch post details with proper typing
const fetchPostDetails = async (token: string, communityId: string, postId: string): Promise<PostResponse | null> => {
    try {
        // Skip fetch if communityId or postId is empty
        if (!communityId || !postId) {
            return null
        }

        const response = await fetch(`${API_URL}/posts/${communityId}/post/${postId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
        })

        if (!response.ok) {
            console.warn(`Failed to fetch post details for post ${postId}: ${response.status}`)
            return null
        }

        return await response.json() as PostResponse
    } catch (error) {
        console.warn(`Error fetching post details for post ${postId}:`, error)
        return null
    }
}

// Buscar campanhas usando a rota de notificações
export const fetchCampaigns = async (token: string): Promise<CampaignNotification[]> => {
    try {
        const response = await fetch(`${API_URL}/notifications?type=CAMPAIGN`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
        })

        if (!response.ok) {
            throw new Error('Erro ao carregar campanhas')
        }

        const notifications = await response.json()

        // Fetch post details for each campaign notification to get real-time stats
        const campaignNotifications = await Promise.all(notifications.map(async (n: any) => {
            const d = n.data || {}

            const campaignTitle = d.campaign_title || 'Campanha'
            const communityName = d.community_name || 'Comunidade'
            const campaignStatusType = d.campaign_status_type || 'default'
            const postId = d.post_id
            const notificationCommunityId = d.community_id

            let status = 'pending'
            if (campaignStatusType === 'approved') status = 'approved'
            else if (campaignStatusType === 'rejected') status = 'rejected'
            else if (campaignStatusType === 'canceled') status = 'canceled'
            else if (campaignStatusType === 'in_progress') status = 'in_progress'
            else if (campaignStatusType === 'finished') status = 'finished'
            else if (campaignStatusType === 'target_reached') status = 'under_review'

            // Default stats from notification data (fallback)
            let stats = {
                published: new Date(n.created_at).toLocaleDateString('pt-BR'),
                accesses: 0,
                participants: d.current_participants || 0,
                likes: 0,
                comments: 0
            }

            let postDetails: PostResponse | null = null
            let imageUrl = d.image_url || undefined
            let description = n.message || d.feedback_content || ''
            let authorData = {
                id: d.actor_id || '',
                name: d.actor_name || 'Usuário',
                username: d.actor_username || 'user',
                profile_picture: d.actor_picture || null,
                role: d.actor_role || 'member'
            }

            // If we have post_id and community_id, fetch actual post details
            if (postId && notificationCommunityId) {
                postDetails = await fetchPostDetails(token, notificationCommunityId, postId)
                if (postDetails) {
                    // Tenta obter views_count ou accesses, se não existir no tipo, usa any para evitar erro de TS imediato
                    const views = (postDetails as any).views_count || (postDetails as any).accesses || 0;

                    stats = {
                        published: new Date(postDetails.created_at).toLocaleDateString('pt-BR'),
                        accesses: views, 
                        // Usa nullish coalescing (??) para garantir que 0 seja um valor válido
                        participants: postDetails.current_participants ?? d.current_participants ?? 0,
                        likes: postDetails.likes_count || 0,
                        comments: postDetails.comments_count || 0
                    }
                    imageUrl = postDetails.image_url || imageUrl
                    description = postDetails.content || description

                    if (postDetails.user) {
                        authorData = {
                            id: postDetails.user.id || authorData.id,
                            name: postDetails.user.name || authorData.name,
                            username: postDetails.user.username || authorData.username,
                            profile_picture: postDetails.user.profile_picture || authorData.profile_picture,
                            role: postDetails.user.role || authorData.role
                        }
                    }
                }
            }

            return {
                id: n.id,
                type: 'Campanha',
                title: campaignTitle,
                author: authorData,
                community: {
                    id: notificationCommunityId || '',
                    name: communityName
                },
                date: new Date(n.created_at).toLocaleDateString('pt-BR'),
                created_at: n.created_at,
                updated_at: n.created_at,
                time: '0',
                description: description,
                status: status,
                stats: stats,
                image_url: imageUrl,
                target_participants: d.target_participants || 0,
                // Prioriza o dado atualizado do post, senão usa o da notificação
                current_participants: postDetails?.current_participants ?? d.current_participants ?? 0,
                post_id: postId
            } as CampaignNotification
        }))

        return campaignNotifications
    } catch (error) {
        return []
    }
}

// Buscar avisos oficiais usando a rota de notificações
export const fetchAnnouncements = async (token: string, communityId?: string): Promise<AnnouncementNotification[]> => {
    try {
        const response = await fetch(`${API_URL}/notifications?type=OFFICIAL_NOTICE`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
        })

        if (!response.ok) {
            throw new Error('Erro ao carregar avisos oficiais')
        }

        const notifications = await response.json()

        // Fetch post details for each announcement notification to get real-time stats
        const announcementNotifications = await Promise.all(notifications.map(async (n: any) => {
            const d = n.data || {}

            const noticeTitle = d.notice_title || 'Aviso'
            const noticeContent = d.notice_content || n.message || ''
            const postId = d.post_id
            const notificationCommunityId = d.community_id || communityId

            // Default stats
            let stats = {
                published: new Date(n.created_at).toLocaleDateString('pt-BR'),
                accesses: 0,
                participants: 0,
                likes: 0,
                comments: 0
            }

            let imageUrl = d.image_url || undefined
            let description = noticeContent
            let authorData = {
                id: d.actor_id || '',
                name: d.actor_name || 'Administração',
                username: d.actor_username || 'admin',
                profile_picture: d.actor_picture || null,
                role: d.actor_role || 'admin'
            }

            // If we have post_id and community_id, fetch actual post details
            if (postId && notificationCommunityId) {
                const postDetails = await fetchPostDetails(token, notificationCommunityId, postId)
                if (postDetails) {
                    const views = (postDetails as any).views_count || (postDetails as any).accesses || 0;
                    
                    stats = {
                        published: new Date(postDetails.created_at).toLocaleDateString('pt-BR'),
                        accesses: views,
                        participants: 0,
                        likes: postDetails.likes_count || 0,
                        comments: postDetails.comments_count || 0
                    }
                    imageUrl = postDetails.image_url || imageUrl
                    description = postDetails.content || description

                    if (postDetails.user) {
                        authorData = {
                            id: postDetails.user.id || authorData.id,
                            name: postDetails.user.name || authorData.name,
                            username: postDetails.user.username || authorData.username,
                            profile_picture: postDetails.user.profile_picture || authorData.profile_picture,
                            role: postDetails.user.role || authorData.role
                        }
                    }
                }
            }

            return {
                id: n.id,
                type: 'Anúncio',
                title: noticeTitle,
                author: authorData,
                community: {
                    id: notificationCommunityId || '',
                    name: d.community_name || ''
                },
                date: new Date(n.created_at).toLocaleDateString('pt-BR'),
                created_at: n.created_at,
                updated_at: n.created_at,
                time: '0',
                description: description,
                image_url: imageUrl,
                stats: stats,
                actions: ['Promover', 'Comentar'],
                post_id: postId
            } as AnnouncementNotification
        }))

        return announcementNotifications
    } catch (error) {
        return []
    }
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
        // Fetch all notification types - campaign and announcement data includes post_id and community_id
        const [campaigns, announcements, connections, interactions] = await Promise.all([
            fetchCampaigns(token),
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