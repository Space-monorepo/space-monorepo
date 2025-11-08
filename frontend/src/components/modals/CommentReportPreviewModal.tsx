
import React from "react";
import { createPortal } from "react-dom";
import { CommentReport } from "@/app/moderation/page";
import { CheckmarkFilled } from "@carbon/icons-react";
import getRoleBadgeClasses from "@/components/badges/users/RoleBadgesClasses";
import getCheckmarkColorClass from "@/components/badges/users/CheckmarkColorClasses";
import { translateUserRole } from "@/lib/roleTranslations";

interface CommentReportPreviewModalProps {
    report: CommentReport;
    onClose: () => void;
}

const CommentReportPreviewModal: React.FC<CommentReportPreviewModalProps> = ({ report, onClose }) => {
    if (typeof window === "undefined" || !report) return null;

    const modalContent = (
        <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/10 backdrop-blur-sm" onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}>
            <div className="bg-white shadow-lg max-w-[680px] w-full p-8 relative">
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
                                            src={report.reportedComment.author.profile_picture || "/no-profile-pic.png"}
                                            alt={`${report.reportedComment.author.name} avatar`}
                                            className="object-cover w-full h-full"
                                        />
                                    </div>
                                    <div className="flex flex-col min-w-60 w-[342px]">
                                        <div className="flex gap-2 items-center w-full h-[23px]">
                                            <div className="flex overflow-hidden gap-2.5 justify-center items-center self-stretch px-3 my-auto">
                                                <span className="self-stretch my-auto text-sm text-neutral-800">
                                                    {report.reportedComment.author.name}
                                                </span>
                                                <CheckmarkFilled
                                                    className={`object-contain shrink-0 self-stretch my-auto aspect-square w-[18px] ${getCheckmarkColorClass(report.reportedComment.author.role)}`}
                                                    aria-label="Verificado"
                                                />
                                                <div className="self-stretch my-auto text-[10px] font-semibold">
                                                    •
                                                </div>
                                                <div className={`flex gap-2.5 justify-center items-center self-stretch px-3 py-1 my-auto text-xs whitespace-nowrap rounded ${getRoleBadgeClasses(report.reportedComment.author.role)}`}> 
                                                    <div className="self-stretch my-auto">
                                                        {translateUserRole(report.reportedComment.author.role || "")}
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="self-start px-3 mt-2 text-xs font-semibold tracking-normal whitespace-nowrap text-neutral-500">
                                            <div className="flex items-center gap-1">
                                                <div className="self-stretch my-auto text-neutral-500">
                                                    Post: {report.reportedComment.postTitle}
                                                </div>
                                                <div className="self-stretch my-auto text-[10px] text-neutral-500">
                                                    •
                                                </div>
                                                <div className="self-stretch my-auto text-neutral-500">
                                                    {report.reportedComment.date}
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
                                            Comentário Reportado
                                        </h2>
                                    </div>
                                    <div className="flex gap-2 items-center px-3 py-1 my-auto text-sm leading-none text-justify whitespace-nowrap rounded-sm flex-shrink-0">
                                        <div className="self-stretch my-auto text-neutral-800">{report.reportedComment.likes}</div>
                                        <span className="h-4 w-4 text-gray-500">👍</span>
                                    </div>
                                </div>

                                {report.reportedComment.content && (
                                    <div className="mt-4 text-sm leading-5 text-justify text-neutral-800 max-md:max-w-full whitespace-pre-line font-regular break-words w-full max-w-full" style={{ wordBreak: 'break-word', overflowWrap: 'break-word', whiteSpace: 'pre-line' }}>
                                        {report.reportedComment.content}
                                    </div>
                                )}

                                <div className="mt-4 w-full">
                                    <div className="flex flex-wrap gap-2">
                                        <span className="px-3 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded-full">Status: {report.status}</span>
                                        <span className="px-3 py-1 text-xs font-medium bg-red-100 text-red-800 rounded-full">Severidade: {report.severity}</span>
                                        <span className="px-3 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">Categoria: {report.category}</span>
                                        <span className="px-3 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">Confirmações: {report.confirmations}</span>
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

export default CommentReportPreviewModal;
