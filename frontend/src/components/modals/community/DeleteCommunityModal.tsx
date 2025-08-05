"use client";

import { X, AlertTriangle } from "lucide-react";
import { Community } from "@/app/api/src/types/community/Community";

interface DeleteCommunityModalProps {
  community: Community;
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (communityId: string) => Promise<void>;
  isLoading?: boolean;
}

export default function DeleteCommunityModal({
  community,
  isOpen,
  onClose,
  onConfirm,
  isLoading = false,
}: DeleteCommunityModalProps) {
  const handleConfirm = async () => {
    try {
      await onConfirm(community.id);
      onClose();
    } catch (error) {
      console.error("Erro ao excluir comunidade:", error);
    }
  };

  if (!isOpen) return null;
  return (
    <div className="fixed inset-0 bg-white/20 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-white p-6 w-full max-w-md mx-4 shadow-2xl">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
              <AlertTriangle className="h-5 w-5 text-red-600" />
            </div>
            <h2 className="text-xl font-medium">Excluir Comunidade</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 text-[#525252] hover:text-[#161616]"
            disabled={isLoading}
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="mb-6">
          <p className="text-[#525252] mb-4">
            Tem certeza que deseja excluir a comunidade{" "}
            <span className="font-medium text-[#161616]">{community.name}</span>
            ?
          </p>
          <div className="bg-red-50 border border-red-200 p-3 rounded">
            <p className="text-red-800 text-sm">
              <strong>Atenção:</strong> Esta ação não pode ser desfeita. Todos
              os dados da comunidade, incluindo posts, membros e configurações
              serão permanentemente excluídos.
            </p>
          </div>
        </div>

        <div className="flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-[#525252] border border-[#e0e0e0] hover:bg-[#f8f8f8] disabled:opacity-50"
            disabled={isLoading}
          >
            Cancelar
          </button>
          <button
            onClick={handleConfirm}
            className="px-4 py-2 bg-red-600 text-white hover:bg-red-700 disabled:opacity-50"
            disabled={isLoading}
          >
            {isLoading ? "Excluindo..." : "Excluir Comunidade"}
          </button>
        </div>
      </div>
    </div>
  );
}
