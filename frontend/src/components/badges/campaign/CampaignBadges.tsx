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

// Badges individuais
export function PendenteBadge() {
  return (
    <StatusBadge className="bg-[#041794]/10 text-[#000D63]">
      Pendente
    </StatusBadge>
  );
}

export function EmAnaliseBadge() {
  return (
    <StatusBadge className="bg-[#814B00]/10 text-[#9A5A00]">
      Em análise
    </StatusBadge>
  );
}

export function AprovadaBadge() {
  return (
    <StatusBadge className="bg-[#056800]/10 text-[#034500]">
      Aprovada
    </StatusBadge>
  );
}

export function RejeitadaBadge() {
  return (
    <StatusBadge className="bg-[#AE0A0A]/10 text-[#870000]">
      Rejeitada
    </StatusBadge>
  );
}

export function EmProgressoBadge() {
  return (
    <StatusBadge className="bg-[#041794]/10 text-[#000D63]">
      Em progresso
    </StatusBadge>
  );
}

export function CanceladaBadge() {
  return (
    <StatusBadge className="bg-[#AE0A0A]/10 text-[#870000]">
      Cancelada
    </StatusBadge>
  );
}

export function FinalizadaBadge() {
  return (
    <StatusBadge className="bg-gray-100 text-gray-900">
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
