"use client";

import { useState } from "react";
import { Paperclip, Smile, Bold, Italic, X } from "lucide-react";

type RejectCampaignModalProps = {
  isOpen: boolean;
  onClose: () => void;
  onReject: (subject: string, reason: string) => void;
  campaignTitle: string;
  campaignAuthor: string;
};

export default function RejectCampaignModal({
  isOpen,
  onClose,
  onReject,
}: RejectCampaignModalProps) {
  const [subject, setSubject] = useState("");
  const [reason, setReason] = useState("");

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white w-full max-w-2xl">
        <div className="flex justify-between items-center p-4 border-b border-[#e0e0e0]">
          <h2 className="text-xl font-medium">Rejeitar campanha</h2>
          <button onClick={onClose} className="p-1 hover:bg-[#f4f4f4]">
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="p-6">
          <p className="mb-4">
            Você está prestes a rejeitar esta campanha. Essa ação a deixará
            invisível para a comunidade e será registrada no histórico.
          </p>
          <p className="mb-6">
            Para manter o processo transparente, explique brevemente o motivo da
            rejeição. Seu feedback ajuda o autor a entender o que precisa ser
            ajustado — e mantém a confiança de todos no sistema.
          </p>

          <div className="mb-4">
            <label className="block mb-2 text-sm">Assunto</label>
            <input
              type="text"
              placeholder="Escreva o Assunto"
              className="w-full p-3 border border-[#e0e0e0] focus:outline-none focus:border-[#0f62fe]"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
            />
          </div>

          <div className="mb-4">
            <label className="block mb-2 text-sm">Motivo</label>
            <div className="border border-[#e0e0e0]">
              <textarea
                placeholder="Escreva aqui..."
                className="w-full p-3 min-h-[200px] focus:outline-none"
                value={reason}
                onChange={(e) => setReason(e.target.value)}
              />
              <div className="border-t border-[#e0e0e0] p-2 flex gap-2">
                <button className="p-1 text-[#525252] hover:bg-[#f4f4f4]">
                  <Paperclip className="h-5 w-5" />
                </button>
                <button className="p-1 text-[#525252] hover:bg-[#f4f4f4]">
                  <Smile className="h-5 w-5" />
                </button>
                <button className="p-1 text-[#525252] hover:bg-[#f4f4f4]">
                  <Bold className="h-5 w-5" />
                </button>
                <button className="p-1 text-[#525252] hover:bg-[#f4f4f4]">
                  <Italic className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>

          <div className="flex justify-between items-center mt-6 border-t border-[#e0e0e0] pt-4">
            <div>
              <p className="text-sm text-[#525252]">De</p>
              <div className="flex items-center gap-2 mt-1">
                <div className="w-6 h-6 rounded-full overflow-hidden">
                  {/*  eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src="/ProfilePic1.svg"
                    alt="User"
                    className="w-full h-full object-cover"
                  />
                </div>
                <span>Briann Gomes</span>
              </div>
            </div>
            <div>
              <p className="text-sm text-[#525252]">Para</p>
              <p className="mt-1">Todos os participantes da campanha</p>
            </div>
          </div>
        </div>

        <div className="flex border-t border-[#e0e0e0]">
          <button
            onClick={onClose}
            className="flex-1 p-4 text-center hover:bg-[#f4f4f4] transition-colors"
          >
            Cancelar
          </button>
          <button
            onClick={() => onReject(subject, reason)}
            className="flex-1 p-4 text-center bg-[#da1e28] text-white hover:bg-[#bc1a22] transition-colors"
          >
            Rejeitar e relatar
          </button>
        </div>
      </div>
    </div>
  );
}
