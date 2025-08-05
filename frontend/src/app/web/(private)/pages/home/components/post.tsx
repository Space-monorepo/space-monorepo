import { Bookmark, MoreHorizontal, TrendingUp, MessageSquare, ArrowUpRight } from "lucide-react";
import { Badge } from "@/components/ui/badge";

function PostImage({ imageType }: { imageType: "flag" | "megaphone" | "people" | "warning" | null }) {
  switch (imageType) {
    case "flag":
      return (
        <svg viewBox="0 0 100 100" className="w-16 h-16">
          <line x1="30" y1="20" x2="30" y2="80" stroke="#555" strokeWidth="3" />
          <polygon points="30,20 70,30 70,50 30,40" fill="#3B82F6" />
        </svg>
      );
    case "megaphone":
      return (
        <svg viewBox="0 0 100 100" className="w-16 h-16">
          <path d="M30,40 L50,25 L50,75 L30,60 Z" fill="#EF4444" />
          <rect x="20" y="40" width="15" height="20" fill="#EF4444" />
          <path
            d="M50,35 C70,35 75,20 80,20 M50,65 C70,65 75,80 80,80"
            stroke="#EF4444"
            strokeWidth="3"
            fill="none"
          />
        </svg>
      );
    case "people":
      return (
        <svg viewBox="0 0 100 100" className="w-16 h-16">
          <rect x="20" y="50" width="60" height="30" fill="#D1D5DB" />
          <circle cx="30" cy="40" r="10" fill="#D1D5DB" />
          <circle cx="50" cy="40" r="10" fill="#D1D5DB" />
          <circle cx="70" cy="40" r="10" fill="#D1D5DB" />
        </svg>
      );
    case "warning":
      return (
        <svg viewBox="0 0 100 100" className="w-16 h-16">
          <polygon points="50,20 80,80 20,80" fill="#FBBF24" stroke="#EF4444" strokeWidth="2" />
          <text x="50" y="65" fontSize="30" textAnchor="middle" fill="#EF4444">
            !
          </text>
        </svg>
      );
    default:
      return null;
  }
}

interface PostProps {
  title: string;
  content: string;
  upvotes: number;
  comments: number;
  location: string;
  tag: string;
  tagColor: string;
  views: number;
  imageType: "flag" | "megaphone" | "people" | "warning" | null;
}

export default function Post({ title, content, upvotes, comments, location, tag, tagColor, views, imageType }: PostProps) {
  return (
    <div className="bg-white rounded-lg shadow-sm p-4">
      <div className="flex gap-4">
        <div className="w-20 h-20 bg-gray-50 flex items-center justify-center rounded-md flex-shrink-0">
          <PostImage imageType={imageType} />
        </div>

        <div className="flex-1">
          <div className="flex justify-between items-start">
            <h2 className="text-xl font-semibold">{title}</h2>
            <div className="flex items-center gap-2">
              <button className="text-gray-400 hover:text-gray-600">
                <Bookmark className="w-5 h-5" />
              </button>
              <button className="text-gray-400 hover:text-gray-600">
                <MoreHorizontal className="w-5 h-5" />
              </button>
            </div>
          </div>

          <p className="text-gray-600 mt-2 text-sm">{content}</p>

          <div className="flex items-center justify-between mt-4">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1 text-gray-500">
                <TrendingUp className="w-4 h-4" />
                <span>{upvotes}</span>
              </div>
              <div className="flex items-center gap-1 text-gray-500">
                <MessageSquare className="w-4 h-4" />
                <span>{comments === 0 ? "Sem interações" : comments}</span>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-500">{location}</span>
              <Badge className={`bg-${tagColor}-100 text-${tagColor}-800 hover:bg-${tagColor}-100`}>
                {tag}
              </Badge>
              <div className="flex items-center gap-1 text-gray-500">
                <span>{views}</span>
                <ArrowUpRight className="w-4 h-4" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}