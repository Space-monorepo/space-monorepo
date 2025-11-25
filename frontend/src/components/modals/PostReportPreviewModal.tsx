
import React from "react";
import { translateUserRole } from "@/lib/roleTranslations";
import { translatePostType } from "@/lib/postTypeTranslations";
import getRoleBadgeClasses from "@/components/badges/users/RoleBadgesClasses";
import getCheckmarkColorClass from "@/components/badges/users/CheckmarkColorClasses";
import { createPortal } from "react-dom";
import { PostReport } from "@/app/moderation/page";
import { CheckmarkFilled, OverflowMenuVertical } from "@carbon/icons-react";
import { Bookmark, Activity } from "lucide-react";
import { ArrowUp, Forum } from "@carbon/icons-react";
import Link from "next/link";

interface PostReportPreviewModalProps {
    report: PostReport;
    onClose: () => void;
}

const PostReportPreviewModal: React.FC<PostReportPreviewModalProps> = ({ report, onClose }) => {
    if (typeof window === "undefined" || !report) return null;

    const post = report.reportedPost;
    const author = post.author;
    const postType = post.type_post ? translatePostType(post.type_post) : "Post";

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
                                            src={author.profile_picture || "/no-profile-pic.png"}
                                            alt={`${author.name} avatar`}
                                            className="object-cover w-full h-full"
                                        />
                                    </div>
                                    <div className="flex flex-col min-w-60 w-[342px]">
                                        <div className="flex gap-2 items-center w-full h-[23px]">
                                            <div className="flex overflow-hidden gap-2.5 justify-center items-center self-stretch px-3 my-auto">
                                                <Link
                                                    href={`/profile/${author.id}`}
                                                    className="self-stretch my-auto text-sm text-neutral-800 hover:text-blue-600 whitespace-nowrap transition-colors hover:underline"
                                                >
                                                    {author.name}
                                                </Link>
                                                <CheckmarkFilled
                                                    className={`object-contain shrink-0 self-stretch my-auto aspect-square w-[18px] ${getCheckmarkColorClass(translateUserRole(author.role || ""))}`}
                                                    aria-label="Verificado"
                                                />
                                                <div className="self-stretch my-auto text-[10px] font-semibold">
                                                    •
                                                </div>
                                                <div className={`flex gap-2.5 justify-center items-center self-stretch px-3 py-1 my-auto text-xs whitespace-nowrap rounded ${getRoleBadgeClasses(translateUserRole(author.role || ""))}`}>
                                                    <div className="self-stretch my-auto">
                                                        {translateUserRole(author.role || "")}
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
                                                    {postType}
                                                </div>
                                                <div className="self-stretch my-auto text-[10px] text-neutral-500">
                                                    •
                                                </div>
                                                <div className="self-stretch my-auto text-neutral-500">
                                                    {post.date}
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
                                            {post.title}
                                        </h2>
                                    </div>
                                    <div className="flex gap-2 items-center px-3 py-1 my-auto text-sm leading-none text-justify whitespace-nowrap rounded-sm flex-shrink-0">
                                        <div className="self-stretch my-auto text-neutral-800">
                                            {post.likes + post.comments}
                                        </div>
                                        <Activity className="h-4 w-4 text-gray-500" />
                                    </div>
                                </div>

                                {post.content && (
                                    <div className="mt-4 text-sm leading-5 text-justify text-neutral-800 max-md:max-w-full whitespace-pre-line font-regular break-words w-full max-w-full" style={{ wordBreak: 'break-word', overflowWrap: 'break-word', whiteSpace: 'pre-line' }}>
                                        {post.content}
                                    </div>
                                )}

                                {post.image && (
                                    <img
                                        src={post.image}
                                        alt="Post content"
                                        className="object-contain mt-4 w-full rounded aspect-[2.26] max-md:max-w-full"
                                    />
                                )}

                                {/* Opções de Enquete */}
                                {postType === 'Enquete' && Array.isArray(post.poll_options) && post.poll_options.length > 0 && (
                                    <div className="mt-6 w-full">
                                        {post.poll_question && (
                                            <h3 className="text-base font-semibold text-neutral-800 mb-6">
                                                {post.poll_question}
                                            </h3>
                                        )}
                                        {post.poll_options.map((option) => {
                                            const totalVotes = post.poll_options!.reduce((sum, opt) => sum + opt.votes_count, 0);
                                            const percent = totalVotes > 0 ? Math.round((option.votes_count / totalVotes) * 100) : 0;
                                            return (
                                                <div key={option.id} className="mb-4">
                                                    <div className="flex flex-wrap gap-10 justify-between items-center w-full text-xs leading-none">
                                                        <div className="flex gap-2 items-center self-stretch my-auto">
                                                            <span className="self-stretch my-auto text-neutral-800 font-medium">
                                                                {percent}%
                                                            </span>
                                                            <span className="self-stretch my-auto text-neutral-900">
                                                                {option.answer}
                                                            </span>
                                                        </div>
                                                        <span className="self-stretch my-auto text-neutral-500">
                                                            {option.votes_count} {option.votes_count === 1 ? 'voto' : 'votos'}
                                                        </span>
                                                    </div>
                                                    <div className="mt-2 w-full rounded-sm">
                                                        <div className="flex flex-col items-start rounded-sm border border-solid border-stone-300">
                                                            <div
                                                                className="flex shrink-0 h-2 rounded-sm bg-neutral-800"
                                                                style={{ width: `${percent}%`, minWidth: '8px' }}
                                                            />
                                                        </div>
                                                    </div>
                                                </div>
                                            );
                                        })}
                                    </div>
                                )}

                                {/* Botão Participar da Campanha (desabilitado no preview) */}
                                {postType === 'Campanha' && (
                                    <button
                                        className="mt-4 w-full py-2 px-4 text-left font-regular bg-neutral-200 text-neutral-700 cursor-not-allowed"
                                        disabled
                                    >
                                        Participar da Campanha
                                    </button>
                                )}

                                {/* Botão Confirmar problema para Denúncia (desabilitado no preview) */}
                                {postType === 'Denúncia' && (
                                    <button
                                        className="mt-4 w-full py-2 px-4 text-left font-regular bg-neutral-200 text-neutral-700 cursor-not-allowed"
                                        disabled
                                    >
                                        Confirmar problema
                                    </button>
                                )}
                            </div>
                        </div>

                        <div className="flex justify-between items-center mt-10 w-full text-xs font-medium leading-none text-neutral-500 max-md:max-w-full">
                            <div className="flex overflow-hidden gap-8 items-center self-stretch my-auto min-h-5 w-[214px]">
                                <button className="flex overflow-hidden gap-2 items-center self-stretch my-auto text-justify whitespace-nowrap cursor-pointer" title="Curtir">
                                    <ArrowUp className="h-4 w-4 text-gray-500" />
                                    <div className="self-stretch my-auto text-neutral-500">
                                        {post.likes}
                                    </div>
                                </button>
                                <button className="flex overflow-hidden gap-2 items-center self-stretch my-auto text-justify whitespace-nowrap transition-colors px-3 py-1 cursor-pointer" title="Comentar">
                                    <Forum className="h-4 w-4 text-gray-500" />
                                    <div className="self-stretch my-auto text-neutral-500">
                                        {post.comments}
                                    </div>
                                </button>
                                <button className="flex overflow-hidden gap-2 items-center self-stretch my-auto text-teal-700" title="Compartilhar">
                                    <Activity className="h-4 w-4 text-teal-700" />
                                    <div className="self-stretch my-auto">
                                        0
                                    </div>
                                </button>
                            </div>
                        </div>
                    </div>
                </article>
            </div>
        </div>
    );

    return createPortal(modalContent, document.body);
};

export default PostReportPreviewModal;
