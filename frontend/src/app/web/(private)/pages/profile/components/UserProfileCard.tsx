import FilePicker from "@/components/ui/FilePicker";
import { User } from "../[username]/page";
import { Button } from "@/components/ui/button";
import ReputationBar from "./ReputationBar";
import UserInfo from "./UserInfo";
import Achievements from "./Achievements";

interface Props {
  user: User | null;
  isOwnProfile: boolean;
  onImageChange: (newImageUrl: string) => void;
}

export default function UserProfileCard({ user, isOwnProfile, onImageChange }: Props) {
  return (
    <div className="w-80 p-4">
      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        <FilePicker
          currentImageUrl={user?.profile_image_url || ""}
          onImageChange={onImageChange}
          isOwnProfile={isOwnProfile}
        />
        <div className="p-4">
          <UserInfo user={user} />

          {!isOwnProfile && (
            <Button className="w-full mt-3 bg-black text-white hover:bg-black/90">
              Conectar-se
            </Button>
          )}

          <ReputationBar reputationLevel={user?.reputation_level} />
          <div className="mt-4 border-t pt-4">
            <h3 className="font-medium text-sm mb-2">Popularidade</h3>
            <div className="text-3xl font-bold">{user?.popularity || 0}</div>
          </div>

          <Achievements />
        </div>
      </div>
    </div>
  );
}
