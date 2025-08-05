import { Calendar, Mail } from "lucide-react";
import { User } from "../[username]/page";

export default function UserInfo({ user }: { user: User | null }) {
  return (
    <>
      <h1 className="text-xl font-bold">{user?.name || "Carregando..."}</h1>
      <p className="text-gray-500 text-sm">@{user?.username || "..."}</p>

      <div className="mt-4 space-y-2 text-sm text-gray-500">
        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4" />
          <span>
            {user ? `Desde ${new Date(user.created_at).toLocaleDateString()}` : "..."}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <Mail className="w-4 h-4" />
          <span>{user?.email || "..."}</span>
        </div>
      </div>

      <div className="mt-4 border-t pt-4">
        <h3 className="font-medium text-sm mb-2">Bio</h3>
        <p className="text-sm text-gray-600">
          {user?.bio || "Esse usuário ainda não escreveu uma bio."}
        </p>
      </div>
    </>
  );
}
