"use client";

import Image from "next/image";
import Link from "next/link";
import { useState } from "react";
import { ChatLaunch, Events, Notification, Settings, Logout, Security, User, Home } from "@carbon/icons-react";
import { usePathname } from "next/navigation";
import { useCheckTokenValidity } from "@/app/api/src/controllers/authCheckToken";
import { Button } from "./button";
import { toast } from "react-toastify";
import Cookies from "js-cookie";
import { cn } from "@/lib/utils";
import { getSidebarPermissions } from "@/lib/sidebarPermissions";
import { useUnreadNotificationsCount } from "@/app/api/src/hooks/notifications/useUnreadNotificationsCount";

type SidebarProps = {
  variant?: "hover" | "static";
};

export default function Sidebar({ variant = "hover" }: SidebarProps) {
  const [isHovered, setIsHovered] = useState(false);
  const pathname = usePathname();
  const { user, loading } = useCheckTokenValidity();

  const sidebarPermissions = getSidebarPermissions(user);

  // Verifica se o usuário é admin ou moderador em alguma comunidade (para compatibilidade)
  const isAdminOrModerator = user?.hasAdminOrModeratorRole === true;

  const isOpen = variant === "static" || isHovered;

  const { unreadCount, loading: unreadLoading } = useUnreadNotificationsCount(20000);

  const handleLogout = () => {
    try {
      Cookies.remove("token", { path: "/" });
      toast.success("Você deslogou!", { autoClose: 3000 });
      setTimeout(() => {
        window.location.href = "/login";
      }, 500);
    } catch (error) {
      toast.error("Erro ao sair. Por favor, tente novamente.");
      console.error("Logout error:", error);
    }
  };

  const isActive = (path: string) => pathname === path;

  return (
    <>
      <aside
        className={cn(
          "bg-gray-100 text-gray-900 flex flex-col h-screen border-r fixed border-gray-200 transition-all duration-300 ease-in-out",
          "hidden min-[900px]:flex", // some quando o card ficaria <500px (sidebar 256px + gap 24px + card 500px + paddings ~120px)
          isOpen ? "w-64" : "w-26"
        )}
        onMouseEnter={() => variant === "hover" && setIsHovered(true)}
        onMouseLeave={() => variant === "hover" && setIsHovered(false)}
      >
        {/* Logo */}
        <div className="p-9 flex items-center gap-3 border-gray-200">
          <Link href="/home" className="flex items-center space-x-2">
            <Image src="/Vector.svg" alt="Space Logo" width={24} height={24} />
            <Image
              src="/space-escrita.svg"
              alt="Space-escrita"
              width={60}
              height={40}
              className={cn(
                "transition-opacity duration-200",
                isOpen
                  ? "opacity-100 pointer-events-auto"
                  : "opacity-0 pointer-events-none"
              )}
            />
          </Link>
        </div>

        {/* Navegação principal */}
        <div className="mt-8 px-6 flex-1 flex flex-col overflow-y-auto">
          <div
            className={cn(
              "text-xs font-medium text-zinc-500 mb-4 transition-opacity duration-200",
              isOpen
                ? "opacity-100 pointer-events-auto"
                : "opacity-0 pointer-events-none"
            )}
          >
            MENU
          </div>

          <nav className="space-y-4 flex-1 flex flex-col">
            <div className="space-y-4">
              <SidebarItem
                icon={<Events size={20} />}
                label="Comunidades"
                href="/communities"
                active={isActive("/communities")}
                isOpen={isOpen}
              />
              <SidebarItem
                icon={<Notification size={20} />}
                label="Notificações"
                href="/notifications"
                active={isActive("/notifications")}
                isOpen={isOpen}
                badgeCount={unreadLoading ? undefined : unreadCount}
              />
              <SidebarItem
                icon={<ChatLaunch size={20} />}
                label="Mensagens"
                href="/messages"
                active={isActive("/messages")}
                isOpen={isOpen}
              />
              {/* Mostra Moderação apenas se tiver permissão */}
              {sidebarPermissions.canViewModerationTab && (
                <SidebarItem
                  icon={<Security size={20} />}
                  label="Moderação"
                  href="/moderation"
                  active={isActive("/moderation")}
                  isOpen={isOpen}
                />
              )}
              {/* Mostra Administrador apenas se tiver permissão (só admin) */}
              {sidebarPermissions.canViewAdministrationTab && (
                <SidebarItem
                  icon={<User size={20} />}
                  label="Administrador"
                  href="/administration"
                  active={isActive("/administration")}
                  isOpen={isOpen}
                />
              )}
            </div>
            <div className="mt-auto">
              <SidebarItem
                icon={<Settings size={20} />}
                label="Configurações"
                href="/settings"
                active={isActive("/settings")}
                isOpen={isOpen}
              />
            </div>
          </nav>
        </div>



        {/* Perfil e logout */}
        <div className="p-7 py-4 border-gray-200">
          <div className="flex items-center justify-between overflow-hidden">
            <Link
              href={user?.username ? `/profile/${user.username}` : "/profile"}
              className="flex items-center gap-3 overflow-hidden"
            >
              <div
                className={cn(
                  "rounded-full bg-zinc-200 overflow-hidden transition-all duration-300",
                  isOpen ? "w-8 h-8" : "w-10 h-8"
                )}
              >
                {loading ? (
                  <div className="w-full h-full animate-pulse bg-gray-300" />
                ) : user?.profile_image_url ? (
                  <Image
                    src={user.profile_image_url}
                    alt="Foto de perfil"
                    width={48}
                    height={48}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <Image
                    src="/no-profile-pic.png"
                    alt="Sem foto de perfil"
                    width={48}
                    height={48}
                    className="w-full h-full object-cover"
                  />
                )}
              </div>

              <div
                className={cn(
                  "flex flex-col whitespace-nowrap overflow-hidden transition-all duration-200",
                  isOpen
                    ? "opacity-100 visible ml-2"
                    : "opacity-0 invisible w-0 ml-0"
                )}
              >
                <span className="text-sm font-medium truncate">{user?.name}</span>
                <span className="text-xs text-gray-500 truncate">
                  @{user?.username}
                </span>
              </div>
            </Link>

            {isOpen && (
              <Button
                variant="ghost"
                className="p-1 ml-2 text-zinc-600 hover:text-red-500 cursor-pointer"
                onClick={handleLogout}
              >
                <Logout size={18} />
              </Button>
            )}
          </div>
        </div>
      </aside>
      <MobileBottomNav
        pathname={pathname}
        sidebarPermissions={sidebarPermissions}
        unreadCount={unreadLoading ? undefined : unreadCount}
      />
    </>
  );
}

type SidebarItemProps = {
  icon: React.ReactNode;
  label: string;
  href: string;
  active: boolean;
  isOpen: boolean;
  badgeCount?: number;
};

function SidebarItem({ icon, label, href, active, isOpen, badgeCount }: SidebarItemProps) {
  return (
    <Link
      href={href}
      className={cn(
        "flex items-center px-3 py-2 rounded-md transition-colors",
        active ? "bg-gray-100 text-black" : "text-zinc-700 hover:bg-gray-100"
      )}
    >
      <div className="relative">
        <div className="w-5 h-5 flex items-center justify-center">{icon}</div>
        {badgeCount !== undefined ? (
          badgeCount && badgeCount > 0 ? (
            <span className="absolute -top-2 -right-3 inline-flex items-center justify-center px-1.5 py-0.5 text-[10px] font-semibold leading-none text-white bg-black rounded-full">
              {badgeCount > 99 ? "99+" : badgeCount}
            </span>
          ) : null
        ) : (
          // placeholder para evitar "layout shift" enquanto carrega
          <span aria-hidden className="absolute -top-2 -right-3 inline-block w-6 h-4" />
        )}
      </div>
      <span
        className={cn(
          "ml-3 text-sm transition-opacity duration-200",
          isOpen ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none"
        )}
      >
        {label}
      </span>
    </Link>
  );
}

type MobileBottomNavProps = {
  pathname: string;
  sidebarPermissions: ReturnType<typeof getSidebarPermissions>;
  unreadCount?: number;
};

function MobileBottomNav({ pathname, sidebarPermissions, unreadCount }: MobileBottomNavProps) {
  const baseLinks = [
    {
      label: "Home",
      href: "/home",
      icon: (
        <Image
          src="/Vector.svg"
          alt="Space logo"
          width={18}
          height={18}
        />
      ),
    },
    { label: "Comunidades", href: "/communities", icon: <Events size={18} /> },
    { label: "Notificações", href: "/notifications", icon: <Notification size={18} /> },
    { label: "Mensagens", href: "/messages", icon: <ChatLaunch size={18} /> },
    { label: "Configurações", href: "/settings", icon: <Settings size={18} /> },
  ];

  const adminLinks = [];
  if (sidebarPermissions.canViewModerationTab) {
    adminLinks.push({ label: "Moderação", href: "/moderation", icon: <Security size={18} />, hideOnCompact: true });
  }
  if (sidebarPermissions.canViewAdministrationTab) {
    adminLinks.push({ label: "Admin", href: "/administration", icon: <User size={18} />, hideOnCompact: true });
  }

  const links = [...baseLinks.slice(0, 4), ...adminLinks, baseLinks[4]];

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-40 bg-white border-t border-gray-200 shadow-lg min-[900px]:hidden">
      <div className="flex items-center justify-between px-4 py-2 gap-1 max-[426px]:gap-2">
        {links.map((link) => {
          const isActive = pathname === link.href;
          const hideOnCompact = (link as any).hideOnCompact;
          return (
            <Link
              key={link.href}
              href={link.href}
              className={cn(
                "flex flex-col items-center justify-center gap-1 text-[11px] text-neutral-500 flex-1 py-1 min-w-[48px]",
                isActive && "text-neutral-900 font-medium",
                hideOnCompact && "max-[426px]:hidden"
              )}
            >
              <span
                className={cn(
                  "relative flex items-center justify-center w-9 h-9 rounded-full transition-colors",
                  isActive ? "bg-neutral-100 text-neutral-900" : "text-neutral-500"
                )}
              >
                {link.icon}
                {link.href === "/notifications" && (
                  unreadCount !== undefined ? (
                    unreadCount > 0 ? (
                      <span className="absolute -top-2 -right-2 inline-flex items-center justify-center px-1.5 py-0.5 text-[10px] font-semibold leading-none text-white bg-red-500 rounded-full">
                        {unreadCount > 99 ? "99+" : unreadCount}
                      </span>
                    ) : null
                  ) : (
                    <span aria-hidden className="absolute -top-2 -right-2 inline-block w-6 h-4" />
                  )
                )}
              </span>
              <span className="max-[426px]:hidden">{link.label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
