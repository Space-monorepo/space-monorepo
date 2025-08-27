"use client"

import Sidebar from "@/components/ui/sidebar"
import RightSidebar from "@/components/ui/Rightsidebar"
import Header from "@/components/ui/header"
import PostList from "./components/post-list"
import { useCheckTokenValidity } from "@/app/api/src/controllers/authCheckToken"

export default function Home() {

  useCheckTokenValidity();

  return (
    <div className="min-h-screen bg-gray-100 text-[#161616] scrollbar-hide overflow-hidden">
      <Sidebar variant="static" />
      <div className="ml-64 scrollbar-hide overflow-auto h-screen">
        <Header />
        <main className="flex flex-1 pt-16 scrollbar-hide overflow-auto">
          <PostList />
          <RightSidebar />
        </main>
      </div>
    </div>
  )
}