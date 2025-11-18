
import React from "react";
import { createPortal } from "react-dom";
import { CommentReport } from "@/app/moderation/page";
import { CheckmarkFilled, ArrowUp } from "@carbon/icons-react";
import getRoleBadgeClasses from "@/components/badges/users/RoleBadgesClasses";
import getCheckmarkColorClass from "@/components/badges/users/CheckmarkColorClasses";
import { translateUserRole } from "@/lib/roleTranslations";
import { getRelativeTime } from "@/lib/relativeTime";

interface CommentReportPreviewModalProps {
    report: CommentReport;
    onClose: () => void;
}

const CommentReportPreviewModal: React.FC<CommentReportPreviewModalProps> = ({ report, onClose }) => {
    if (typeof window === "undefined" || !report) return null;

    // Usar os dados que já temos do report
    const userObj = report.reportedComment.author;
    const displayName = userObj?.name || 'Usuário';
    const memberRole = (userObj as any)?.member_role || (userObj as any)?.role;
    const profilePicture = (userObj as any)?.profile_picture || (userObj as any)?.profile_image_url || '/no-profile-pic.png';
    const content = report.reportedComment.content;
    const createdAt = report.reportedComment.date;
    const likesCount = report.reportedComment.likes;

    const modalContent = (
        <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/10 backdrop-blur-sm" onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}>
            <div className="bg-white shadow-lg max-w-[680px] w-full rounded border-solid border-[0.5px] border-stone-300 relative max-h-[90vh] overflow-y-auto">
                <button
                    className="absolute top-2 right-4 text-gray-500 hover:text-gray-700 text-2xl cursor-pointer z-10"
                    onClick={onClose}
                >
                    &times;
                </button>
                {/* Comments List Container igual ao PostList */}
                <section className="flex flex-col p-4 bg-white rounded-sm max-w-[648px] w-full">
                    {/* Layout do comentário igual ao PostList */}
                    <div className="flex flex-wrap justify-between w-full max-md:max-w-full">
                        <div className="flex flex-col items-center w-11">
                            <img
                                src={profilePicture}
                                alt={`${displayName} avatar`}
                                className="object-contain w-11 aspect-square"
                            />
                        </div>
                        <div className="flex-1 shrink basis-0 min-w-60 max-md:max-w-full">
                            <div className="flex flex-wrap gap-3 items-center py-3 w-full max-md:max-w-full">
                                <div className="flex items-center self-stretch my-auto min-w-60 text-neutral-800 w-[380px]">
                                    <div className="self-stretch my-auto min-w-60 w-[380px]">
                                        <div className="flex gap-2 items-center w-full h-[23px]">
                                            <div className="flex overflow-hidden gap-2.5 justify-center items-center self-stretch px-3 my-auto">
                                                <div className="self-stretch my-auto whitespace-nowrap text-sm text-neutral-800">
                                                    {displayName}
                                                </div>
                                                <CheckmarkFilled
                                                    className={`object-contain shrink-0 self-stretch my-auto aspect-square w-[18px] ${getCheckmarkColorClass(memberRole)}`}
                                                    aria-label="Verificado"
                                                />
                                                <div className="self-stretch my-auto text-[10px] text-black font-semibold">
                                                    •
                                                </div>
                                                {memberRole && (
                                                    <div className={`flex gap-2.5 justify-center items-center self-stretch px-3 py-1 my-auto text-xs whitespace-nowrap rounded ${getRoleBadgeClasses(memberRole)}`}>
                                                        <div className="self-stretch my-auto">
                                                            {translateUserRole(memberRole)}
                                                        </div>
                                                    </div>
                                                )}
                                                <div className="self-stretch my-auto text-[10px] text-black">
                                                    •
                                                </div>
                                                <div className="self-stretch my-auto text-[10px] whitespace-nowrap font-semibold">
                                                    <div className="text-neutral-800">
                                                        {getRelativeTime(createdAt)}
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div className="flex gap-4 items-center self-stretch my-auto w-5 min-h-5">
                                    {/* Menu de opções pode ser implementado aqui se necessário */}
                                </div>
                            </div>
                            <div className="px-3 mt-2 w-full max-md:max-w-full">
                                <div className="flex gap-2.5 items-center w-full text-sm leading-5 text-neutral-800 max-md:max-w-full">
                                    <div className="flex-1 shrink self-stretch my-auto basis-0 text-neutral-800 max-md:max-w-full">
                                        {content}
                                    </div>
                                </div>
                                <div className="flex justify-between items-center mt-4 w-full text-xs font-medium leading-none text-justify text-neutral-500 max-md:max-w-full">
                                    <div className="flex overflow-hidden gap-8 items-center self-stretch my-auto min-h-5">
                                        <div className="flex overflow-hidden gap-2 items-center self-stretch my-auto whitespace-nowrap">
                                            <ArrowUp
                                                className="object-contain shrink-0 self-stretch my-auto w-3 aspect-square text-neutral-500"
                                                aria-label="Curtir"
                                            />
                                            <div className="self-stretch my-auto text-neutral-500">
                                                {likesCount}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>
            </div>
        </div>
    );

    return createPortal(modalContent, document.body);
};

export default CommentReportPreviewModal;
