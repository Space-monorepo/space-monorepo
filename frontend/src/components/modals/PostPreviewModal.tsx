import React from "react";
import { createPortal } from "react-dom";
import Link from "next/link";
import { Bookmark, Activity } from "lucide-react";
import { CheckmarkFilled } from "@carbon/icons-react";
import getRoleBadgeClasses from "@/components/badges/users/RoleBadgesClasses";
import getCheckmarkColorClass from "@/components/badges/users/CheckmarkColorClasses";
import { translatePostType } from "@/lib/postTypeTranslations";

interface PostPreviewModalProps {
    post: {
        id: string;
        title: string;
        content: string;
        author?: string;
        avatar?: string;
        role?: string;
        location?: string;
        type?: string;
        time?: string;
        imageUrl?: string;
        likes?: number;
        comments?: number;
        shares?: number;
        username?: string;
        user?: { id?: string; profile_picture?: string; profile_image_url?: string };
    } | null;
    isOpen: boolean;
    onClose: () => void;
}

const PostPreviewModal: React.FC<PostPreviewModalProps> = ({ post, isOpen, onClose }) => {
    if (!isOpen || !post || typeof window === 'undefined') return null;

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
            <div className="bg-white shadow-lg max-w-[680px] w-full p-8 relative">
                <button
                    className="absolute top-2 right-4 text-gray-500 hover:text-gray-700 text-2xl cursor-pointer"
                    onClick={onClose}
                >
                    &times;
                </button>
                <div className="w-full max-w-[632px] mx-auto">
                    <header className="flex flex-wrap gap-10 justify-between items-start w-full">
                        <div className="flex items-start min-w-60">
                            <div className="w-11 h-11 rounded-[32px] overflow-hidden shrink-0 flex items-center justify-center bg-neutral-200">
                                <img
                                    src={post.user && (post.user.profile_image_url || post.user.profile_picture)
                                        ? (post.user.profile_image_url || post.user.profile_picture)
                                        : post.avatar || "/placeholder.svg"}
                                    alt={`${post.author} avatar`}
                                    className="object-cover w-full h-full"
                                />
                            </div>
                            <div className="flex flex-col min-w-60 w-[342px]">
                                <div className="flex gap-2 items-center w-full h-[23px]">
                                    <div className="flex overflow-hidden gap-2.5 justify-center items-center self-stretch px-3 my-auto">
                                        <Link
                                            href={`/profile/${post.username || post.user?.id}`}
                                            className="self-stretch my-auto text-sm text-neutral-800 hover:text-blue-600 whitespace-nowrap transition-colors hover:underline"
                                        >
                                            {post.author}
                                        </Link>
                                        <CheckmarkFilled
                                            className={`object-contain shrink-0 self-stretch my-auto aspect-square w-[18px] ${getCheckmarkColorClass(post.role)}`}
                                            aria-label="Verificado"
                                        />
                                        <div className="self-stretch my-auto text-[10px] font-semibold">•</div>
                                        <div className={`flex gap-2.5 justify-center items-center self-stretch px-3 py-1 my-auto text-xs whitespace-nowrap rounded ${getRoleBadgeClasses(post.role)}`}>
                                            <div className="self-stretch my-auto">{post.role}</div>
                                        </div>
                                    </div>
                                    <div className="self-stretch my-auto text-xs leading-none text-justify whitespace-nowrap text-neutral-800">
                                        {post.location}
                                    </div>
                                </div>
                                <div className="self-start px-3 mt-2 text-xs font-semibold tracking-normal whitespace-nowrap text-neutral-500">
                                    <div className="flex items-center gap-1">
                                        <div className="self-stretch my-auto text-neutral-500">{post.type ? translatePostType(post.type) : "Tipo não informado"}</div>
                                        <div className="self-stretch my-auto text-[10px] text-neutral-500">•</div>
                                        <div className="self-stretch my-auto text-neutral-500">{post.time}</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="flex gap-4 items-center">
                            <button className="p-1 hover:bg-gray-100 rounded-full transition-colors" title="Salvar nos favoritos">
                                <Bookmark className={`h-4 w-4 text-gray-500`} />
                            </button>
                            <div className="flex gap-2 items-center px-3 py-1 my-auto text-sm leading-none text-justify whitespace-nowrap rounded-sm flex-shrink-0">
                                <div className="self-stretch my-auto text-neutral-800">{(post.likes ?? 0) + (post.comments ?? 0) + (post.shares ?? 0)}</div>
                                <Activity className="h-4 w-4 text-gray-500" />
                            </div>
                        </div>
                    </header>
                    <div className="mt-6 w-full text-neutral-800">
                        <div className="flex flex-row justify-between items-center w-full">
                            <div className="flex gap-2.5 items-center text-xl font-bold leading-relaxed min-w-60 px-0 w-0 flex-1" style={{ wordBreak: 'break-word' }}>
                                <h2
                                    className="text-neutral-800 px-0 font-georgia font-bold break-words w-full max-w-full"
                                    style={{ fontFamily: 'Georgia, serif', fontWeight: 'bold', wordBreak: 'break-word', overflowWrap: 'break-word', whiteSpace: 'pre-line' }}
                                >
                                    {post.title}
                                </h2>
                            </div>
                            <div className="flex gap-2 items-center px-3 py-1 my-auto text-sm leading-none text-justify whitespace-nowrap rounded-sm flex-shrink-0">
                                <div className="self-stretch my-auto text-neutral-800">{(post.likes ?? 0) + (post.comments ?? 0) + (post.shares ?? 0)}</div>
                                <Activity className="h-4 w-4 text-gray-500" />
                            </div>
                        </div>
                        {post.content && (
                            <div
                                className="mt-4 text-sm leading-5 text-justify text-neutral-800 whitespace-pre-line font-regular break-words w-full max-w-full"
                                style={{ wordBreak: 'break-word', overflowWrap: 'break-word', whiteSpace: 'pre-line' }}
                            >
                                {post.content}
                            </div>
                        )}
                        {post.imageUrl && (
                            <img
                                src={post.imageUrl}
                                alt="Post content"
                                className="object-contain mt-4 w-full rounded aspect-[2.26]"
                            />
                        )}
                    </div>
                </div>
            </div>
        </div>
    );

    return createPortal(modalContent, document.body);
};

export default PostPreviewModal;
