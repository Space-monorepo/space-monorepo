"use client";

import Image from "next/image";
import Link from "next/link";
import { useState } from "react";
import { ChatLaunch, Events, Notification, Settings, Logout, Security } from "@carbon/icons-react";
import { usePathname } from "next/navigation";
import { useCheckTokenValidity } from "@/app/api/src/controllers/authCheckToken";
import { Button } from "./button";
import { toast } from "react-toastify";
import Cookies from "js-cookie";
import { cn } from "@/lib/utils";

type SidebarProps = {
  variant?: "hover" | "static";
};

export default function Sidebar({ variant = "hover" }: SidebarProps) {
  const [isHovered, setIsHovered] = useState(false);
  const pathname = usePathname();
  const { user, loading } = useCheckTokenValidity();

  const isOpen = variant === "static" || isHovered;

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
    <aside
      className={cn(
        "bg-gray-50 text-gray-900 flex flex-col h-screen border-r border-gray-200 transition-all duration-300 ease-in-out",
        isOpen ? "w-64" : "w-26"
      )}
      onMouseEnter={() => variant === "hover" && setIsHovered(true)}
      onMouseLeave={() => variant === "hover" && setIsHovered(false)}
    >
      {/* Logo */}
      <div className="p-9 flex items-center gap-3 border-b border-gray-200">
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
      <div className="mt-8 px-6 flex-1">
        <div
          className={cn(
            "text-xs font-medium text-zinc-500 mb-4 transition-opacity duration-200",
            isOpen
              ? "opacity-100 pointer-events-auto"
              : "opacity-0 pointer-events-none"
          )}
        >
          GENERAL
        </div>

        <nav className="space-y-4">
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
          />
          <SidebarItem
            icon={<ChatLaunch size={20} />}
            label="Mensagens"
            href="/messages"
            active={isActive("/messages")}
            isOpen={isOpen}
          />
          <SidebarItem
            icon={<Security size={20} />}
            label="Moderação"
            href="/moderation"
            active={isActive("/moderation")}
            isOpen={isOpen}
          />
        </nav>
      </div>

      {/* Configurações */}
      <div className="px-6 mb-4 border-gray-200">
        <SidebarItem
          icon={<Settings size={20} />}
          label="Configurações"
          href="/settings"
          active={isActive("/settings")}
          isOpen={isOpen}
        />
      </div>

      {/* Perfil e logout */}
      <div className="p-7 py-4 border-gray-200">
        <div className="flex items-center justify-between overflow-hidden">
          <Link
            href="/profile"
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
  );
}

type SidebarItemProps = {
  icon: React.ReactNode;
  label: string;
  href: string;
  active: boolean;
  isOpen: boolean;
};

function SidebarItem({ icon, label, href, active, isOpen }: SidebarItemProps) {
  return (
    <Link
      href={href}
      className={cn(
        "flex items-center px-3 py-2 rounded-md transition-colors",
        active ? "bg-gray-100 text-zinc-900" : "text-zinc-700 hover:bg-gray-100"
      )}
    >
      <div className="w-5 h-5 flex items-center justify-center">{icon}</div>
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
