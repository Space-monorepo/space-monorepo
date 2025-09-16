import { useState, useCallback } from 'react';
// Utilitário para garantir que status seja sempre string separada por vírgulas
function statusToParam(status: string | string[]): string {
    if (Array.isArray(status)) return status.join(',');
    return status;
}
import axios from 'axios';
import { API_URL } from '@/config';
import getTokenFromCookies from '@/app/api/src/controllers/getTokenFromCookies';

// Tipos para dados reportados da API
export interface ReportedUser {
    id: string;
    name: string;
    profile_picture?: string;
    role?: string;
    status: string;
    report_count: number;
    created_at: string;
    suspension_reason?: string;
}

export interface ReportedPost {
    id: string;
    title: string;
    content: string;
    status: string;
    report_count: number;
    likes_count: number;
    comments_count: number;
    created_at: string;
    image_url?: string;
    user: {
        id: string;
        name: string;
        profile_picture?: string;
        role?: string;
    };
}

export interface ReportedComment {
    id: string;
    content: string;
    status: string;
    report_count: number;
    likes_count: number;
    created_at: string;
    parent_id?: string;
    user: {
        id: string;
        name: string;
        profile_picture?: string;
        role?: string;
    };
    post: {
        id: string;
        title: string;
    };
}

const useModerationReports = () => {
    const [reportedUsers, setReportedUsers] = useState<ReportedUser[]>([]);
    const [reportedPosts, setReportedPosts] = useState<ReportedPost[]>([]);
    const [reportedComments, setReportedComments] = useState<ReportedComment[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Buscar usuários reportados
    const fetchReportedUsers = useCallback(async (communityId: string) => {
        setLoading(true);
        setError(null);
        try {
            const token = getTokenFromCookies();
            if (!token) throw new Error("Token não encontrado");

            // Como não há endpoint específico para usuários reportados, vamos buscar membros da comunidade
            // e filtrar por aqueles que têm status suspenso ou reportado
            const response = await axios.get(
                `${API_URL}/communities/${communityId}/members`,
                {
                    headers: { Authorization: `Bearer ${token}` },
                    params: { status: ['suspended', 'reported'] }
                }
            );

            setReportedUsers(response.data?.items || []);
        } catch (err: any) {
            console.error('Erro ao buscar usuários reportados:', err);
            setError(err.response?.data?.message || 'Erro ao carregar usuários reportados');
            setReportedUsers([]);
        } finally {
            setLoading(false);
        }
    }, []);

    // Buscar posts reportados
    const fetchReportedPosts = useCallback(async (communityId: string) => {
        setLoading(true);
        setError(null);
        try {
            const token = getTokenFromCookies();
            if (!token) throw new Error("Token não encontrado");

            const response = await axios.get(
                `${API_URL}/posts/${communityId}/community/list-posts`,
                {
                    headers: { Authorization: `Bearer ${token}` },
                    params: { status: ['reported'] }
                }
            );

            setReportedPosts(response.data?.items || []);
        } catch (err: any) {
            console.error('Erro ao buscar posts reportados:', err);
            setError(err.response?.data?.message || 'Erro ao carregar posts reportados');
            setReportedPosts([]);
        } finally {
            setLoading(false);
        }
    }, []);

    // Buscar comentários reportados
    const fetchReportedComments = useCallback(async (communityId: string) => {
        setLoading(true);
        setError(null);
        try {
            const token = getTokenFromCookies();
            if (!token) throw new Error("Token não encontrado");

            // Primeiro, buscar todos os posts da comunidade
            const postsResponse = await axios.get(
                `${API_URL}/posts/${communityId}/community/list-posts`,
                {
                    headers: { Authorization: `Bearer ${token}` }
                }
            );

            const posts = postsResponse.data?.items || [];
            let allReportedComments: ReportedComment[] = [];

            // Para cada post, buscar comentários reportados
            for (const post of posts) {
                try {
                    const commentsResponse = await axios.get(
                        `${API_URL}/comments/${communityId}/post/${post.id}/list-comments`,
                        {
                            headers: { Authorization: `Bearer ${token}` },
                            params: { status: ['reported'] }
                        }
                    );

                    const reportedCommentsForPost = (commentsResponse.data?.items || []).map((comment: any) => ({
                        ...comment,
                        post: {
                            id: post.id,
                            title: post.title
                        }
                    }));

                    allReportedComments = [...allReportedComments, ...reportedCommentsForPost];
                } catch (commentErr) {
                    console.warn(`Erro ao buscar comentários do post ${post.id}:`, commentErr);
                }
            }

            setReportedComments(allReportedComments);
        } catch (err: any) {
            console.error('Erro ao buscar comentários reportados:', err);
            setError(err.response?.data?.message || 'Erro ao carregar comentários reportados');
            setReportedComments([]);
        } finally {
            setLoading(false);
        }
    }, []);

    // Suspender usuário
    const suspendUser = useCallback(async (communityId: string, userId: string) => {
        try {
            const token = getTokenFromCookies();
            if (!token) throw new Error("Token não encontrado");

            await axios.patch(
                `${API_URL}/communities/${communityId}/suspend-user/${userId}`,
                {},
                { headers: { Authorization: `Bearer ${token}` } }
            );

            // Recarregar usuários reportados
            fetchReportedUsers(communityId);
        } catch (err: any) {
            console.error('Erro ao suspender usuário:', err);
            throw new Error(err.response?.data?.message || 'Erro ao suspender usuário');
        }
    }, [fetchReportedUsers]);

    // Remover post
    const removePost = useCallback(async (communityId: string, postId: string) => {
        try {
            const token = getTokenFromCookies();
            if (!token) throw new Error("Token não encontrado");

            await axios.delete(
                `${API_URL}/posts/${communityId}/post/${postId}`,
                { headers: { Authorization: `Bearer ${token}` } }
            );

            // Recarregar posts reportados
            fetchReportedPosts(communityId);
        } catch (err: any) {
            console.error('Erro ao remover post:', err);
            throw new Error(err.response?.data?.message || 'Erro ao remover post');
        }
    }, [fetchReportedPosts]);

    // Remover comentário
    const removeComment = useCallback(async (communityId: string, commentId: string) => {
        try {
            const token = getTokenFromCookies();
            if (!token) throw new Error("Token não encontrado");

            await axios.delete(
                `${API_URL}/comments/${communityId}/comment/${commentId}`,
                { headers: { Authorization: `Bearer ${token}` } }
            );

            // Recarregar comentários reportados
            fetchReportedComments(communityId);
        } catch (err: any) {
            console.error('Erro ao remover comentário:', err);
            throw new Error(err.response?.data?.message || 'Erro ao remover comentário');
        }
    }, [fetchReportedComments]);

    // Tolerar (marcar como resolvido) - para qualquer tipo de conteúdo
    const tolerateReport = useCallback(async (communityId: string, type: 'user' | 'post' | 'comment', id: string) => {
        try {
            const token = getTokenFromCookies();
            if (!token) throw new Error("Token não encontrado");

            let endpoint = '';
            switch (type) {
                case 'user':
                    endpoint = `${API_URL}/communities/${communityId}/unsuspend-user/${id}`;
                    break;
                case 'post':
                    endpoint = `${API_URL}/posts/${communityId}/post/${id}/unreport`;
                    break;
                case 'comment':
                    endpoint = `${API_URL}/comments/${communityId}/comment/${id}/unreport`;
                    break;
            }

            await axios.patch(endpoint, {}, { headers: { Authorization: `Bearer ${token}` } });

            // Recarregar dados apropriados
            switch (type) {
                case 'user':
                    fetchReportedUsers(communityId);
                    break;
                case 'post':
                    fetchReportedPosts(communityId);
                    break;
                case 'comment':
                    fetchReportedComments(communityId);
                    break;
            }
        } catch (err: any) {
            console.error('Erro ao tolerar reporte:', err);
            throw new Error(err.response?.data?.message || 'Erro ao tolerar reporte');
        }
    }, [fetchReportedUsers, fetchReportedPosts, fetchReportedComments]);

    return {
        reportedUsers,
        reportedPosts,
        reportedComments,
        loading,
        error,
        fetchReportedUsers,
        fetchReportedPosts,
        fetchReportedComments,
        suspendUser,
        removePost,
        removeComment,
        tolerateReport,
    };
};

export default useModerationReports;