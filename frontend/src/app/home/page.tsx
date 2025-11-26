"use client"

import Sidebar from "@/components/ui/sidebar"
import RightSidebar from "@/components/ui/Rightsidebar"
import Header from "@/components/ui/header"
import PostList from "./components/PostList"
import { useCheckTokenValidity } from "@/app/api/src/controllers/authCheckToken"

export default function Home() {
  useCheckTokenValidity();

  return (
    <div className="min-h-screen bg-gray-100 text-[#161616]">
      <Sidebar variant="static" />
      <div className="ml-0 min-[900px]:ml-64 min-h-screen">
        <Header />
        <main className="pt-24 pb-10 px-4 min-[900px]:px-6 lg:px-10">
          <div className="flex w-full gap-6 min-[1360px]:gap-10 mx-auto max-w-6xl min-[1360px]:mx-0 min-[1360px]:max-w-none">
            <section className="flex-1 min-w-0">
              <PostList />
            </section>
            <aside className="hidden min-[1360px]:flex w-[320px] shrink-0 ml-auto">
              <RightSidebar />
            </aside>
          </div>
        </main>
      </div>
    </div>
  )
}
