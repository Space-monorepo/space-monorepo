'use client'

import Sidebar from "@/components/ui/sidebar";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { loadUserProfile } from "@/app/api/src/controllers/userController";
import { useCheckTokenValidity } from "@/app/api/src/controllers/authCheckToken";
import getTokenFromCookies from "@/app/api/src/controllers/getTokenFromCookies";
import UserProfileCard from "../components/UserProfileCard";
import PostList from "../components/PostList";

export interface User {
  username: string;
  name: string;
  email: string;
  created_at: string;
  bio?: string;
  reputation_level?: string;
  popularity?: number;
  profile_image_url?: string;
}

export default function ProfilePage() {
  const params = useParams();
  const username = params.username as string;

  const [user, setUser] = useState<User | null>(null);
  useCheckTokenValidity();

  useEffect(() => {
    const loadUser = async () => {
      const token = getTokenFromCookies();
      if (!token) return console.warn("Token não encontrado nos cookies.");
      try {
        const data = await loadUserProfile(token);
        setUser(data);
      } catch (err) {
        console.error("Erro ao carregar o perfil:", err);
      }
    };
    loadUser();
  }, []);

  const isOwnProfile = user?.username === username;

  const handleImageChange = (newImageUrl: string) => {
    setUser((prev) => prev ? { ...prev, profile_image_url: newImageUrl } : prev);
  };

  return (
    <div className="min-h-screen bg-gray-100 flex">
      <Sidebar />
      <main className="flex-1">
        <div className="max-w-6xl mx-auto flex">
          <UserProfileCard user={user} isOwnProfile={isOwnProfile} onImageChange={handleImageChange} />
          <div className="flex-1 p-4">
            <PostList />
          </div>
        </div>
      </main>
    </div>
  );
}
