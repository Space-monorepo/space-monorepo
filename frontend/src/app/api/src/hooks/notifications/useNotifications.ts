import { useState, useEffect, useCallback } from 'react'
import { fetchNotifications } from '../../services/notifications/notificationService'
import { NotificationsResponse } from '../../types/notifications/Notification'
import getTokenFromCookies from '../../controllers/getTokenFromCookies'

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

            const data = await fetchNotifications(token)
            setNotifications(data)
        } catch (err) {
            console.error('Erro ao carregar notificações:', err)
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
