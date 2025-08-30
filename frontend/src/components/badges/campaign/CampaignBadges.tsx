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
    <div className={`flex gap-2.5 justify-center items-center px-3 py-2 whitespace-nowrap rounded-sm ${className}`}>
      <span className="self-stretch my-auto">
        {children}
      </span>
    </div>
  );
}

// Badges individuais
export function PendenteBadge() {
  return (
    <StatusBadge className="bg-blue-900 bg-opacity-10 text-blue-950">
      Pendente
    </StatusBadge>
  );
}

export function EmAnaliseBadge() {
  return (
    <StatusBadge className="text-yellow-700 bg-yellow-800 bg-opacity-10">
      Em análise
    </StatusBadge>
  );
}

export function AprovadaBadge() {
  return (
    <StatusBadge className="bg-green-900 bg-opacity-10 text-green-950">
      Aprovada
    </StatusBadge>
  );
}

export function RejeitadaBadge() {
  return (
    <StatusBadge className="text-red-900 bg-red-700 bg-opacity-10">
      Rejeitada
    </StatusBadge>
  );
}

export function EmProgressoBadge() {
  return (
    <StatusBadge className="bg-blue-900 bg-opacity-10 text-blue-950">
      Em progresso
    </StatusBadge>
  );
}

export function CanceladaBadge() {
  return (
    <StatusBadge className="text-red-900 bg-red-700 bg-opacity-10">
      Cancelada
    </StatusBadge>
  );
}

export function FinalizadaBadge() {
  return (
    <StatusBadge className="bg-zinc-100 text-neutral-800">
      Finalizada
    </StatusBadge>
  );
}

// Componente que exibe todos os badges (para demonstração)
export function StatusBadgeCampaign() {
  return (
    <main className="flex flex-col items-center px-14 pt-32 w-full bg-white pb-[522px]">
      <PendenteBadge />
      
      <div className="mt-14">
        <EmAnaliseBadge />
      </div>

      <div className="mt-14">
        <AprovadaBadge />
      </div>

      <div className="mt-14">
        <RejeitadaBadge />
      </div>

      <div className="mt-14">
        <EmProgressoBadge />
      </div>

      <div className="mt-14">
        <CanceladaBadge />
      </div>

      <div className="mt-14 mb-0">
        <FinalizadaBadge />
      </div>
    </main>
  );
}

// Exportação do componente base para uso externo se necessário
export { StatusBadge };
