import { UserRole, getPermissions } from "@/lib/permissions";

export function getSidebarPermissions(user: any) {
    // Suporte para user ser null/undefined
    // member_role pode vir como "admin", "moderator", "member" ou undefined
    let role: UserRole = "member";
    if (user?.member_role) {
        const r = user.member_role.toLowerCase();
        if (r.includes("admin")) role = "admin";
        else if (r.includes("moderator")) role = "moderator";
        else role = "member";
    }
    const permissions = getPermissions(role);
    return permissions;
}
