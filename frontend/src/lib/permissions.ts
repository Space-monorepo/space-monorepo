// Sistema de permissões baseado nos papéis dos usuários do Space
export type UserRole = "admin" | "moderator" | "member";

export interface UserPermissions {
  // Comunidades
  canViewCommunities: boolean;
  canCreateCommunities: boolean;
  canEditCommunities: boolean;
  canDeleteCommunities: boolean;

  // Posts
  canViewPosts: boolean;
  canCreatePosts: boolean;
  canEditPosts: boolean;
  canDeletePosts: boolean;

  // Badges
  canViewBadges: boolean;
  canCreateBadges: boolean;
  canEditBadges: boolean;
  canDeleteBadges: boolean;

  // Sidebar
  canViewAdministrationTab: boolean;
  canViewModerationTab: boolean;
}

export function getPermissions(role: UserRole): UserPermissions {
  switch (role) {
    case "admin":
      return {
        canViewCommunities: true,
        canCreateCommunities: true,
        canEditCommunities: true,
        canDeleteCommunities: true,
        canViewPosts: true,
        canCreatePosts: true,
        canEditPosts: true,
        canDeletePosts: true,
        canViewBadges: true,
        canCreateBadges: true,
        canEditBadges: true,
        canDeleteBadges: true,
        canViewAdministrationTab: true,
        canViewModerationTab: true,
      };
    case "moderator":
      return {
        canViewCommunities: true,
        canCreateCommunities: false,
        canEditCommunities: true,
        canDeleteCommunities: false,
        canViewPosts: true,
        canCreatePosts: true,
        canEditPosts: true,
        canDeletePosts: true,
        canViewBadges: true,
        canCreateBadges: false,
        canEditBadges: true,
        canDeleteBadges: false,
        canViewAdministrationTab: false,
        canViewModerationTab: true,
      };
    case "member":
      return {
        canViewCommunities: true,
        canCreateCommunities: false,
        canEditCommunities: false,
        canDeleteCommunities: false,
        canViewPosts: true,
        canCreatePosts: true,
        canEditPosts: false,
        canDeletePosts: false,
        canViewBadges: true,
        canCreateBadges: false,
        canEditBadges: false,
        canDeleteBadges: false,
        canViewAdministrationTab: false,
        canViewModerationTab: false,
      };
    default:
      return {
        canViewCommunities: false,
        canCreateCommunities: false,
        canEditCommunities: false,
        canDeleteCommunities: false,
        canViewPosts: false,
        canCreatePosts: false,
        canEditPosts: false,
        canDeletePosts: false,
        canViewBadges: false,
        canCreateBadges: false,
        canEditBadges: false,
        canDeleteBadges: false,
        canViewAdministrationTab: false,
        canViewModerationTab: false,
      };
  }
}

export function hasPermission(
  role: UserRole,
  permission: keyof UserPermissions,
): boolean {
  const permissions = getPermissions(role);
  return permissions[permission];
}

export function canAccessRoute(role: UserRole, route: string): boolean {
  // Rotas públicas
  const publicRoutes = ["/home", "/login", "/signup", "/explore"];
  if (publicRoutes.some((r) => route.startsWith(r))) return true;

    if (route.startsWith("/communities")) return hasPermission(role, "canViewCommunities");
    if (route.startsWith("/posts")) return hasPermission(role, "canViewPosts");
    if (route.startsWith("/badges")) return hasPermission(role, "canViewBadges");

  return false;
}
