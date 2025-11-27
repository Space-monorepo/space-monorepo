import React, { useState } from "react";
import { REPORT_REASONS, ReportReason } from "./reportReasons";

interface ReportReasonModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: { reason: ReportReason; description: string }) => void;
  type: "member_report" | "post_report" | "comment_report";
}

export const ReportReasonModal: React.FC<ReportReasonModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  type,
}) => {
  const [reason, setReason] = useState<ReportReason>("other");
  const [description, setDescription] = useState("");

  if (!isOpen) return null;

  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!reason) return;
    onSubmit({ reason, description });
    setReason("other");
    setDescription("");
  };

  const typeLabel =
    type === "member_report"
      ? "membro"
      : type === "post_report"
      ? "post"
      : "comentário";

  return (
    <div
      className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/20 backdrop-blur-sm"
      onClick={handleBackdropClick}
    >
      <div className="bg-white shadow-lg max-w-[400px] w-full rounded border border-stone-300 relative p-6">
        <button
          className="absolute top-2 right-4 text-gray-500 hover:text-gray-700 text-2xl cursor-pointer"
          onClick={onClose}
          aria-label="Fechar"
        >
          &times;
        </button>
        <h2 className="text-lg font-bold mb-4 text-neutral-800">
          Reportar {typeLabel}
        </h2>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1">
              Motivo do reporte
            </label>
            <select
              className="w-full border border-neutral-300 rounded px-3 py-2 text-sm"
              value={reason}
              onChange={(e) => setReason(e.target.value as ReportReason)}
              required
            >
              {REPORT_REASONS.map((r) => (
                <option key={r.value} value={r.value}>
                  {r.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1">
              Descrição (opcional)
            </label>
            <textarea
              className="w-full border border-neutral-300 rounded px-3 py-2 text-sm resize-none"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Descreva o motivo do reporte"
              rows={3}
            />
          </div>
          <div className="flex justify-end gap-2 mt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded bg-neutral-200 text-neutral-800 hover:bg-neutral-300 transition"
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="px-4 py-2 rounded bg-red-600 text-white hover:bg-red-700 transition"
            >
              Enviar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ReportReasonModal;
