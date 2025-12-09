
import React from "react";
import { translateUserRole } from "@/lib/roleTranslations";
import getRoleBadgeClasses from "@/components/badges/users/RoleBadgesClasses";
import getCheckmarkColorClass from "@/components/badges/users/CheckmarkColorClasses";
import { createPortal } from "react-dom";
import { UserReport } from "@/app/moderation/page";
import { CheckmarkFilled, OverflowMenuVertical } from "@carbon/icons-react";
import { Bookmark } from "lucide-react";
import Link from "next/link";

interface UserReportPreviewModalProps {
    report: UserReport;
    onClose: () => void;
}

// Helper: capitaliza a primeira letra de uma string (seguindo UX solicitado)
function capitalizeFirst(s?: string) {
    if (!s || typeof s !== 'string') return '';
    return s.charAt(0).toUpperCase() + s.slice(1);
}

const UserReportPreviewModal: React.FC<UserReportPreviewModalProps> = ({ report, onClose }) => {
    if (typeof window === "undefined" || !report) return null;

    const user = report.reportedUser;

    const modalContent = (
        <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/10 backdrop-blur-sm" onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}>
            <div className="bg-white shadow-lg max-w-[680px] w-full p-4 relative max-h-[90vh] overflow-y-auto">
                <button
                    className="absolute top-2 right-4 text-gray-500 hover:text-gray-700 text-2xl cursor-pointer z-10"
                    onClick={onClose}
                >
                    &times;
                </button>
                <article className="flex flex-col justify-center px-6 py-4 w-full bg-white max-md:px-5 max-md:max-w-full">
                    <div className="w-full max-w-[632px] max-md:max-w-full">
                        <div className="w-full max-md:max-w-full">
                            <header className="flex flex-wrap gap-10 justify-between items-start w-full max-md:max-w-full">
                                <div className="flex items-start min-w-60">
                                    <div className="w-11 h-11 rounded-[32px] overflow-hidden shrink-0 flex items-center justify-center bg-neutral-200">
                                        <img
                                            src={user.profile_picture || "/no-profile-pic.png"}
                                            alt={`${user.name} avatar`}
                                            className="object-cover w-full h-full"
                                        />
                                    </div>
                                    <div className="flex flex-col min-w-60 w-[342px]">
                                        <div className="flex gap-2 items-center w-full h-[23px]">
                                            <div className="flex overflow-hidden gap-2.5 justify-center items-center self-stretch px-3 my-auto">
                                                <Link
                                                    href={`/profile/${user.id}`}
                                                    className="self-stretch my-auto text-sm text-neutral-800 hover:text-blue-600 whitespace-nowrap transition-colors hover:underline"
                                                >
                                                    {user.name}
                                                </Link>
                                                <CheckmarkFilled
                                                    className={`object-contain shrink-0 self-stretch my-auto aspect-square w-[18px] ${getCheckmarkColorClass(translateUserRole(user.role || ""))}`}
                                                    aria-label="Verificado"
                                                />
                                                <div className="self-stretch my-auto text-[10px] font-semibold">
                                                    •
                                                </div>
                                                <div className={`flex gap-2.5 justify-center items-center self-stretch px-3 py-1 my-auto text-xs whitespace-nowrap rounded ${getRoleBadgeClasses(translateUserRole(user.role || ""))}`}>
                                                    <div className="self-stretch my-auto">
                                                        {translateUserRole(user.role || "")}
                                                    </div>
                                                </div>
                                            </div>
                                            <div className="self-stretch my-auto text-xs leading-none text-justify whitespace-nowrap text-neutral-800">
                                                Comunidade
                                            </div>
                                        </div>
                                        <div className="self-start px-3 mt-2 text-xs font-semibold tracking-normal whitespace-nowrap text-neutral-500">
                                            <div className="flex items-center gap-1">
                                                <div className="self-stretch my-auto text-neutral-500">
                                                    Usuário Reportado
                                                </div>
                                                <div className="self-stretch my-auto text-[10px] text-neutral-500">
                                                    •
                                                </div>
                                                <div className="self-stretch my-auto text-neutral-500">
                                                    {report.date}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div className="flex gap-4 items-center">
                                    <button
                                        className="p-1 hover:bg-gray-100 rounded-full transition-colors"
                                        title="Salvar nos favoritos"
                                    >
                                        <Bookmark className={`h-4 w-4 text-gray-500`} />
                                    </button>
                                    <div className="relative">
                                        <button
                                            className="p-1 hover:bg-gray-100 rounded-full cursor-pointer transition-colors"
                                            aria-label="Mais opções"
                                        >
                                            <OverflowMenuVertical className="h-4 w-4 text-gray-500" />
                                        </button>
                                    </div>
                                </div>
                            </header>

                            <div className="mt-6 w-full text-neutral-800 max-md:max-w-full">
                                <div className="flex flex-row justify-between items-center w-full max-md:max-w-full">
                                    <div className="flex gap-2.5 items-center text-xl font-bold leading-relaxed min-w-60 px-0 w-0 flex-1" style={{ wordBreak: 'break-word' }}>
                                        <h2 className="text-neutral-800 px-0 font-georgia font-bold break-words w-full max-w-full" style={{ fontFamily: 'Georgia, serif', fontWeight: 'bold', wordBreak: 'break-word', overflowWrap: 'break-word', whiteSpace: 'pre-line' }}>
                                            {capitalizeFirst(report.reason)}
                                        </h2>
                                    </div>
                                </div>

                                <div className="mt-4 text-sm leading-5 text-justify text-neutral-800 max-md:max-w-full whitespace-pre-line font-regular break-words w-full max-w-full" style={{ wordBreak: 'break-word', overflowWrap: 'break-word', whiteSpace: 'pre-line' }}>
                                    {report.description}
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
