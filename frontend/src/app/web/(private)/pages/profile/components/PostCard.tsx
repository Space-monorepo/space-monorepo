import { TrendingUp, MessageSquare, Clock, BookmarkIcon, MoreHorizontal, Flag } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface PostCardProps {
  title: string;
  description: string;
  likes: number;
  comments: number;
  timeAgo: string;
}

export default function PostCard({ title, description, likes, comments, timeAgo }: PostCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-sm p-4">
      <div className="flex justify-between items-start mb-4">
        <h2 className="text-lg font-semibold">{title}</h2>
        <div className="flex items-center gap-1">
          <button className="text-gray-400 hover:text-gray-600">
            <BookmarkIcon className="w-5 h-5" />
          </button>
          <button className="text-gray-400 hover:text-gray-600">
            <MoreHorizontal className="w-5 h-5" />
          </button>
        </div>
      </div>

      <div className="flex gap-4 mb-4">
        <div className="w-20 h-20 bg-gray-100 flex items-center justify-center rounded">
          <Flag className="w-8 h-8 text-gray-400" />
        </div>
        <div className="flex-1">
          <p className="text-sm text-gray-600">{description}</p>
        </div>
      </div>

      <div className="flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1">
            <TrendingUp className="w-4 h-4" />
            <span>{likes}</span>
          </div>
          <div className="flex items-center gap-1">
            <MessageSquare className="w-4 h-4" />
            <span>{comments}</span>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span>PUC - Campinas</span>
          <Badge variant="outline" className="bg-blue-50 text-blue-600 border-blue-200">
            Campanha
          </Badge>
          <div className="flex items-center gap-1">
            <Clock className="w-3 h-3" />
            <span>{timeAgo}</span>
          </div>
        </div>
      </div>
    </div>
  );
}