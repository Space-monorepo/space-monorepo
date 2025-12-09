import { useState, useEffect, useCallback } from 'react'
import { fetchNotifications } from '../../services/notifications/notificationService'
import { NotificationsResponse } from '../../types/notifications/Notification'
import getTokenFromCookies from '../../controllers/getTokenFromCookies'
import { API_URL } from '@/config'

// Interface para o usuário completo
interface UserWithCommunities {
    id: string;
    name: string;
    username: string;
    profile_image_url: string;
    communities?: Array<{
        id?: string;
        _id?: string;
        name?: string;
    }>;
}

export const useNotifications = () => {
    const [notifications, setNotifications] = useState<NotificationsResponse>({
        campaigns: [],
        announcements: [],
        connections: [],
        interactions: []
    })
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    const loadNotifications = useCallback(async () => {
        try {
            setLoading(true)
            setError(null)

            const token = getTokenFromCookies()
            if (!token) {
                throw new Error('Token não encontrado')
            }

            // Buscar informações do usuário
            let communityId: string | undefined;
            try {
                const userResponse = await fetch(`${API_URL}/users/me`, {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });

                if (userResponse.ok) {
                    const user: UserWithCommunities = await userResponse.json();

                    // Buscar comunidades do usuário
                    const communitiesResponse = await fetch(`${API_URL}/communities/user/${user.id}/communities`, {
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/json'
                        }
                    });

                    if (communitiesResponse.ok) {
                        const communitiesData = await communitiesResponse.json();

                        // Pegar o ID da primeira comunidade
                        if (communitiesData.items && communitiesData.items.length > 0) {
                            communityId = communitiesData.items[0].id;
                        }
                    }
                }
            } catch (userError) {
                // Erro ao buscar informações do usuário
            }

            const data = await fetchNotifications(token, communityId)
            setNotifications(data)
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Erro desconhecido')
        } finally {
            setLoading(false)
        }
    }, [])

    useEffect(() => {
        loadNotifications()
    }, [loadNotifications])

    return {
        notifications,
        loading,
        error,
        refetch: loadNotifications
    }
}
