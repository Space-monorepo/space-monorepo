import { UserRole, getPermissions } from "@/lib/permissions";

export function getSidebarPermissions(user: any) {
    // Suporte para user ser null/undefined
    let role: UserRole = "member";
    
    // Primeiro, verifica se tem member_role direto no usuário
    if (user?.member_role) {
        const r = user.member_role.toLowerCase();
        if (r.includes("admin")) role = "admin";
        else if (r.includes("moderator")) role = "moderator";
        else role = "member";
    }
    
    // Se não encontrou role direto, verifica nas comunidades do usuário
    // O role mais alto encontrado nas comunidades determina as permissões
    if (user?.communities && Array.isArray(user.communities)) {
        for (const community of user.communities) {
            if (community.role) {
                const communityRole = community.role.toLowerCase();
                // Admin tem prioridade sobre tudo
                if (communityRole === "admin") {
                    role = "admin";
                    break; // Admin é o mais alto, pode parar
                }
                // Moderador tem prioridade sobre member
                if (communityRole === "moderator" && role !== "admin") {
                    role = "moderator";
                }
            }
        }
    }
    
    // Se ainda não encontrou, mas tem hasAdminOrModeratorRole, verifica
    // Se tem hasAdminOrModeratorRole mas não encontrou role específico,
    // assume moderador (mais conservador) ou tenta determinar melhor
    if (role === "member" && user?.hasAdminOrModeratorRole === true) {
        // Se tem hasAdminOrModeratorRole mas não encontrou role específico,
        // verifica se tem alguma comunidade com role definido
        // Por padrão, se tem hasAdminOrModeratorRole, assume moderador
        // (pois admin seria detectado acima)
        role = "moderator";
    }
    
    const permissions = getPermissions(role);
    return permissions;
}
