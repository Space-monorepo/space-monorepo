"use client";

import { Search, MoreHorizontal, ArrowRight } from "lucide-react";
import Sidebar from "@/components/ui/sidebar";
import Link from "next/link";
import useCommunityActions from "@/app/api/src/hooks/community/useCommunityActions";

export default function AdministrationPage() {
  const { communities, loading, error } = useCommunityActions();

  if (loading) {
    return (
      <div className="min-h-screen bg-white text-[#161616]">
        <Sidebar variant="static" />
        <div className="ml-64">
          <main className="p-8">
            <h1 className="text-2xl font-medium mb-6">Administração</h1>
            <div className="flex items-center justify-center h-64">
              <div className="text-[#525252]">Carregando comunidades...</div>
            </div>
          </main>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-white text-[#161616]">
        <Sidebar variant="static" />
        <div className="ml-64">
          <main className="p-8">
            <h1 className="text-2xl font-medium mb-6">Administração</h1>
            <div className="flex items-center justify-center h-64">
              <div className="text-red-500">
                Erro ao carregar comunidades: {error.message}
              </div>
            </div>
          </main>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white text-[#161616]">
      <Sidebar variant="static" />
      <div className="ml-64">
        <main className="p-8">
          <h1 className="text-2xl font-medium mb-6">Administração</h1>{" "}
          {/* Search Bar */}
          <div className="mb-8 max-w-3xl">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[#525252] h-4 w-4" />
              <input
                type="text"
                placeholder="Pesquisar"
                className="w-full pl-10 pr-4 py-2 border border-[#e0e0e0] rounded focus:outline-none focus:border-[#0f62fe]"
              />
            </div>
          </div>
          {/* Communities List */}
          <div className="space-y-2 max-w-3xl">
            {communities.length === 0 ? (
              <div className="text-center py-8 text-[#525252]">
                Nenhuma comunidade encontrada
              </div>
            ) : (
              communities.map((community) => (
                <div
                  key={community.id}
                  className="bg-white hover:bg-[#f8f8f8] rounded-md p-4 flex items-center justify-between group"
                >
                  <div className="flex items-center gap-4">
                    <div
                      className={`w-12 h-12 rounded flex items-center justify-center text-xl bg-[#f4f4f4] border border-[#e0e0e0]`}
                    >
                      <span>🏢</span>
                    </div>
                    <div>
                      <h3 className="font-medium text-lg">{community.name}</h3>
                      <p className="text-sm text-[#525252]">
                        {community.type_community
                          ? `Tipo: ${community.type_community}`
                          : "Tipo não especificado"}
                        {community.memberCount &&
                          ` • ${community.memberCount} membros`}
                      </p>
                      {community.description && (
                        <p className="text-sm text-[#525252] mt-1 line-clamp-2">
                          {community.description}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <button className="p-2 rounded-full hover:bg-[#e5e5e5] opacity-0 group-hover:opacity-100 transition-opacity">
                      <MoreHorizontal className="h-5 w-5 text-[#525252]" />
                    </button>
                    <button className="p-2 rounded-full hover:bg-[#e5e5e5]">
                      <Link href={`/administration/${community.id}`}>
                        <ArrowRight className="h-5 w-5 text-[#525252]" />
                      </Link>
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
