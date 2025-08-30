"use client";
import * as React from "react";

// Interface para o componente base StatusBadge
interface StatusBadgeProps {
    children: React.ReactNode;
    className?: string;
}

// Componente base StatusBadge
function StatusBadge({ children, className = "" }: StatusBadgeProps) {
    return (
        <div className={`flex gap-1.5 justify-center items-center px-2 py-1 whitespace-nowrap rounded-xs text-xs ${className}`}>
            <span className="self-stretch my-auto">
                {children}
            </span>
        </div>
    );
}

export function LeveBadge() {
    return (
        <StatusBadge className="bg-green-900/10 text-green-950">
            Leve
        </StatusBadge>
    );
}

export function ModeradaBadge() {
    return (
        <StatusBadge className="bg-yellow-800/10 text-yellow-700 mt-4">
            Moderada
        </StatusBadge>
    );
}

export function CriticaBadge() {
    return (
        <StatusBadge className="bg-red-700/10 text-red-900 mt-4">
            Crítica
        </StatusBadge>
    );
}

export function PendenteBadge() {
    return (
        <StatusBadge className="bg-zinc-100 text-neutral-900 mt-4">
            <img
                src="https://api.builder.io/api/v1/image/assets/2c92ea9fbec34a758f970e8cafff5cb1/2efb89be383c3d2b1892a33a44a365ae6b569917?placeholderIfAbsent=true"
                alt=""
                className="object-contain shrink-0 self-stretch my-auto w-4 aspect-square mr-1"
            />
            Pendente
        </StatusBadge>
    );
}

export function EmApuracaoBadge() {
    return (
        <StatusBadge className="bg-zinc-100 text-neutral-800 mt-4">
            <img
                src="https://api.builder.io/api/v1/image/assets/2c92ea9fbec34a758f970e8cafff5cb1/f120d585c27b43e6290c996678692721d61ba205?placeholderIfAbsent=true"
                alt=""
                className="object-contain shrink-0 self-stretch my-auto w-4 aspect-square mr-1"
            />
            Em apuração
        </StatusBadge>
    );
}

export function ResolvidaBadge() {
    return (
        <StatusBadge className="bg-zinc-100 text-neutral-800 mt-4 mb-0">
            <img
                src="https://api.builder.io/api/v1/image/assets/2c92ea9fbec34a758f970e8cafff5cb1/a45823c370b0390f0ec1fdb6cb1a1259f169e95c?placeholderIfAbsent=true"
                alt=""
                className="object-contain shrink-0 self-stretch my-auto w-4 aspect-square mr-1"
            />
            Resolvida
        </StatusBadge>
    );
}

// Componente que exibe todos os badges (para demonstração)
export function StatusBadgeDenuncia() {
    return (
        <main className="flex flex-col items-center px-14 pt-32 w-full bg-white pb-[495px] max-w-[279px]">
            <LeveBadge />
            <div className="mt-4">
                <ModeradaBadge />
            </div>
            <div className="mt-4">
                <CriticaBadge />
            </div>
            <div className="mt-4">
                <PendenteBadge />
            </div>
            <div className="mt-4">
                <EmApuracaoBadge />
            </div>
            <div className="mt-4 mb-0">
                <ResolvidaBadge />
            </div>
        </main>
    );
}

// Exportação do componente base para uso externo se necessário
export { StatusBadge };
