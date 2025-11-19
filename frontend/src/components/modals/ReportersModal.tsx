import React from "react";
import { createPortal } from "react-dom";

interface ReporterInfo {
    id: string;
    name: string;
    profile_picture?: string | null;
    role?: string;
}

interface ReportListItem {
    id: string;
    reporter: ReporterInfo;
    reason: string;
    description: string;
    created_at: string;
}

interface ReportersModalProps {
    isOpen: boolean;
    onClose: () => void;
    reporters: ReportListItem[];
    loading?: boolean;
}

const ReportersModal: React.FC<ReportersModalProps> = ({ isOpen, onClose, reporters, loading }) => {
    if (!isOpen || typeof window === 'undefined') return null;

    const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
        if (e.target === e.currentTarget) {
            onClose();
        }
    };

    const modalContent = (
        <div
            className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/10 backdrop-blur-sm"
            onClick={handleBackdropClick}
        >
            <div className="bg-white shadow-lg max-w-[420px] w-full p-6 relative">
                <button
                    className="absolute top-2 right-4 text-gray-500 hover:text-gray-700 text-2xl cursor-pointer"
                    onClick={onClose}
                >
                    &times;
                </button>
                <h2 className="text-lg font-bold mb-4 text-neutral-800">Usuários que reportaram</h2>
                {loading ? (
                    <div className="text-center text-neutral-500 py-8">Carregando...</div>
                ) : (
                    <div className="space-y-2 max-h-80 overflow-y-auto">
                        {reporters.length ? (
                            reporters.map((r) => (
                                <div key={r.id} className="flex items-center gap-3 py-2 border-b last:border-b-0">
                                    <img src={r.reporter.profile_picture || "/no-profile-pic.png"} className="w-8 h-8 rounded-full" />
                                    <div className="flex flex-col">
                                        <span className="font-medium text-neutral-800">{r.reporter.name}</span>
                                        <span className="text-xs text-gray-500">{r.reason}</span>
                                    </div>
                                </div>
                            ))
                        ) : (
                            <span className="text-xs text-gray-500">Nenhum reporte encontrado.</span>
                        )}
                    </div>
                )}
            </div>
        </div>
    );

    return createPortal(modalContent, document.body);
};

export default ReportersModal;
