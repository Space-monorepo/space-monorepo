
import React from "react";
import { createPortal } from "react-dom";
import { UserReport } from "@/app/moderation/page";

interface UserReportPreviewModalProps {
    report: UserReport;
    onClose: () => void;
}

const UserReportPreviewModal: React.FC<UserReportPreviewModalProps> = ({ report, onClose }) => {
    if (typeof window === "undefined" || !report) return null;

    const modalContent = (
        <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/10 backdrop-blur-sm" onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}>
            <div className="bg-white shadow-lg max-w-[680px] w-full p-8 relative rounded-lg">
                <button
                    className="absolute top-2 right-4 text-gray-500 hover:text-gray-700 text-2xl cursor-pointer"
                    onClick={onClose}
                >
                    &times;
                </button>
                <article>
                    <div className="w-full max-w-[632px] max-md:max-w-full">
                        <div className="w-full max-md:max-w-full">
                            <header className="flex flex-wrap gap-10 justify-between items-start w-full max-md:max-w-full">
                                <div className="flex items-start min-w-60">
                                    <div className="w-11 h-11 rounded-[32px] overflow-hidden shrink-0 flex items-center justify-center bg-neutral-200">
                                        <img
                                            src={report.reportedUser.profile_picture || "/no-profile-pic.png"}
                                            alt={`${report.reportedUser.name} avatar`}
                                            className="object-cover w-full h-full"
                                        />
                                    </div>
                                    <div className="flex flex-col min-w-60 w-[342px]">
                                        <div className="flex gap-2 items-center w-full h-[23px]">
                                            <div className="flex overflow-hidden gap-2.5 justify-center items-center self-stretch px-3 my-auto">
                                                <span className="self-stretch my-auto text-sm text-neutral-800">
                                                    {report.reportedUser.name}
                                                </span>
                                                <div className="self-stretch my-auto text-[10px] font-semibold">•</div>
                                                <div className="flex gap-2.5 justify-center items-center self-stretch px-3 py-1 my-auto text-xs whitespace-nowrap rounded bg-neutral-800 text-zinc-100">
                                                    <div className="self-stretch my-auto">
                                                        {report.reportedUser.role}
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </header>

                            <div className="mt-6 w-full text-neutral-800 max-md:max-w-full">
                                <div className="flex flex-row justify-between items-center w-full max-md:max-w-full">
                                    <div className="flex gap-2.5 items-center text-xl font-bold leading-relaxed min-w-60 px-0 w-0 flex-1" style={{ wordBreak: 'break-word' }}>
                                        <h2 className="text-neutral-800 px-0 font-georgia font-bold break-words w-full max-w-full" style={{ fontFamily: 'Georgia, serif', fontWeight: 'bold', wordBreak: 'break-word', overflowWrap: 'break-word', whiteSpace: 'pre-line' }}>
                                            Usuário Reportado
                                        </h2>
                                    </div>
                                </div>

                                <div className="mt-4 text-sm leading-5 text-justify text-neutral-800 max-md:max-w-full whitespace-pre-line font-regular break-words w-full max-w-full" style={{ wordBreak: 'break-word', overflowWrap: 'break-word', whiteSpace: 'pre-line' }}>
                                    <div><span className="font-medium">Motivo:</span> {report.reason}</div>
                                    <div><span className="font-medium">Descrição:</span> {report.description}</div>
                                </div>

                                <div className="mt-4 w-full">
                                    <div className="flex flex-wrap gap-2">
                                        <span className="px-3 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded-full">Status: {report.status}</span>
                                        <span className="px-3 py-1 text-xs font-medium bg-red-100 text-red-800 rounded-full">Severidade: {report.severity}</span>
                                        <span className="px-3 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">Categoria: {report.category}</span>
                                        <span className="px-3 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">Confirmações: {report.confirmations}</span>
                                        <span className="px-3 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded-full">Data: {report.date}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </article>
            </div>
        </div>
    );

    return createPortal(modalContent, document.body);
};

export default UserReportPreviewModal;
