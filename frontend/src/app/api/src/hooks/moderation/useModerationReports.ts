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
    id: string; // Este é o ID do membro, não do reporte
    report_id?: string; // ID do primeiro reporte associado (para votação)
    name: string;
    profile_picture?: string;
    role?: string;
    status: string;
    report_count: number;
    created_at: string;
    suspension_reason?: string;
}

export interface ReportedPost {
    id: string; // Este é o ID do post, não do reporte
    report_id?: string; // ID do primeiro reporte associado (para votação)
    title: string;
    content: string;
    status: string;
    report_count: number;
    likes_count: number;
    comments_count: number;
    created_at: string;
    image_url?: string;
    type_post?: string;
    poll_options?: Array<{ id: string; answer: string; votes_count: number }>;
    poll_question?: string;
    status_complaint?: string;
    level_complaint?: string;
    user: {
        id: string;
        name: string;
        profile_picture?: string;
        role?: string;
    };
}

export interface ReportedComment {
    id: string; // Este é o ID do comentário, não do reporte
    report_id?: string; // ID do primeiro reporte associado (para votação)
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

            // Buscar lista de brief reports (resumo dos membros reportados)
            const briefResponse = await axios.get(
                `${API_URL}/moderation/${communityId}/list-all-member-brief-reports`,
                {
                    headers: { Authorization: `Bearer ${token}` }
                }
            );

            const briefReports = briefResponse.data?.items || [];

            // Para cada membro reportado, buscar os detalhes dos reportes para obter o report_id
            const usersWithReportIds = await Promise.all(
                briefReports.map(async (brief: any) => {
                    try {
                        // Buscar reportes detalhados para este membro
                        const detailsResponse = await axios.get(
                            `${API_URL}/moderation/${communityId}/list-all-member-reports/${brief.member.id}`,
                            {
                                headers: { Authorization: `Bearer ${token}` },
                                params: { limit: 1 } // Pegar apenas o primeiro reporte
                            }
                        );

                        const firstReport = detailsResponse.data?.items?.[0];

                        return {
                            id: brief.member.id,
                            report_id: firstReport?.id, // ID do reporte para votação
                            name: brief.member.name,
                            profile_picture: brief.member.profile_picture,
                            role: brief.member.role,
                            status: 'reported',
                            report_count: brief.reports_count,
                            created_at: brief.member_entry_date,
                            suspension_reason: brief.reason,
                        };
                    } catch (err) {
                        console.warn(`Erro ao buscar reportes para membro ${brief.member.id}:`, err);
                        return {
                            id: brief.member.id,
                            name: brief.member.name,
                            profile_picture: brief.member.profile_picture,
                            role: brief.member.role,
                            status: 'reported',
                            report_count: brief.reports_count,
                            created_at: brief.member_entry_date,
                            suspension_reason: brief.reason,
                        };
                    }
                })
            );

            setReportedUsers(usersWithReportIds);
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

            // Buscar lista de brief reports (resumo dos posts reportados)
            const briefResponse = await axios.get(
                `${API_URL}/moderation/${communityId}/list-all-post-brief-reports`,
                {
                    headers: { Authorization: `Bearer ${token}` }
                }
            );

            const briefReports = briefResponse.data?.items || [];

            // Para cada post reportado, buscar os detalhes dos reportes para obter o report_id
            const postsWithReportIds = await Promise.all(
                briefReports.map(async (brief: any) => {
                    try {
                        // Buscar reportes detalhados para este post
                        const detailsResponse = await axios.get(
                            `${API_URL}/moderation/${communityId}/list-all-post-reports/${brief.post_id}`,
                            {
                                headers: { Authorization: `Bearer ${token}` },
                                params: { limit: 1 } // Pegar apenas o primeiro reporte
                            }
                        );

                        const firstReport = detailsResponse.data?.items?.[0];

                        return {
                            id: brief.post_id,
                            report_id: firstReport?.id, // ID do reporte para votação
                            title: brief.title,
                            content: brief.content,
                            status: 'reported',
                            report_count: brief.report_count,
                            likes_count: brief.likes_count,
                            comments_count: brief.comments_count,
                            created_at: brief.published_at,
                            image_url: brief.image_url,
                            user: {
                                id: brief.member.id,
                                name: brief.member.name,
                                profile_picture: brief.member.profile_picture,
                                role: brief.member.role,
                            },
                        };
                    } catch (err) {
                        console.warn(`Erro ao buscar reportes para post ${brief.post_id}:`, err);
                        return {
                            id: brief.post_id,
                            title: brief.title,
                            content: brief.content,
                            status: 'reported',
                            report_count: brief.report_count,
                            likes_count: brief.likes_count,
                            comments_count: brief.comments_count,
                            created_at: brief.published_at,
                            image_url: brief.image_url,
                            user: {
                                id: brief.member.id,
                                name: brief.member.name,
                                profile_picture: brief.member.profile_picture,
                                role: brief.member.role,
                            },
                        };
                    }
                })
            );

            setReportedPosts(postsWithReportIds);
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

            // Buscar lista de brief reports (resumo dos comentários reportados)
            const briefResponse = await axios.get(
                `${API_URL}/moderation/${communityId}/list-all-comment-brief-reports`,
                {
                    headers: { Authorization: `Bearer ${token}` }
                }
            );

            const briefReports = briefResponse.data?.items || [];

            // Para cada comentário reportado, buscar os detalhes dos reportes para obter o report_id
            const commentsWithReportIds = await Promise.all(
                briefReports.map(async (brief: any) => {
                    try {
                        // Buscar reportes detalhados para este comentário
                        const detailsResponse = await axios.get(
                            `${API_URL}/moderation/${communityId}/list-all-comment-reports/${brief.comment_id}`,
                            {
                                headers: { Authorization: `Bearer ${token}` },
                                params: { limit: 1 } // Pegar apenas o primeiro reporte
                            }
                        );

                        const firstReport = detailsResponse.data?.items?.[0];

                        return {
                            id: brief.comment_id,
                            report_id: firstReport?.id, // ID do reporte para votação
                            content: brief.content,
                            status: 'reported',
                            report_count: brief.report_count,
                            likes_count: brief.likes_count,
                            created_at: brief.commented_at,
                            parent_id: brief.parent_id,
                            user: {
                                id: brief.member.id,
                                name: brief.member.name,
                                profile_picture: brief.member.profile_picture,
                                role: brief.member.role,
                            },
                            post: {
                                id: brief.post_id,
                                title: brief.post_title,
                            },
                        };
                    } catch (err) {
                        console.warn(`Erro ao buscar reportes para comentário ${brief.comment_id}:`, err);
                        return {
                            id: brief.comment_id,
                            content: brief.content,
                            status: 'reported',
                            report_count: brief.report_count,
                            likes_count: brief.likes_count,
                            created_at: brief.commented_at,
                            parent_id: brief.parent_id,
                            user: {
                                id: brief.member.id,
                                name: brief.member.name,
                                profile_picture: brief.member.profile_picture,
                                role: brief.member.role,
                            },
                            post: {
                                id: brief.post_id,
                                title: brief.post_title,
                            },
                        };
                    }
                })
            );

            setReportedComments(commentsWithReportIds);
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