"use client";

import Sidebar from "@/components/ui/sidebar";
import Link from "next/link";
import useCommunityActions from "@/app/api/src/hooks/community/useCommunityActions";
import { OverflowMenuHorizontal, ArrowRight } from "@carbon/icons-react";
import Image from "next/image";
import { useState } from "react";
import { SearchBar } from "@/components/ui/search-bar";

export default function AdministrationPage() {
  const { communities, loading, error } = useCommunityActions();
  const [searchQuery, setSearchQuery] = useState("");

  if (loading) {
    return (
      <div className="min-h-screen bg-white text-[#161616]">
        <Sidebar variant="static" />
        <div className="ml-0 min-[900px]:ml-64 max-md:pl-4 max-md:pr-4">
          <main className="p-8 max-md:p-4 max-sm:p-3">
            <h1 className="text-2xl font-medium mb-6 max-md:text-xl max-sm:text-lg">Administração</h1>
            <div className="flex items-center justify-center h-64">
              <div className="text-[#525252] text-center">Carregando comunidades...</div>
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
        <div className="ml-0 min-[900px]:ml-64 max-md:pl-4 max-md:pr-4">
          <main className="p-8 max-md:p-4 max-sm:p-3">
            <h1 className="text-2xl font-medium mb-6 max-md:text-xl max-sm:text-lg">Administração</h1>
            <div className="flex items-center justify-center h-64">
              <div className="text-red-500 text-center max-w-md">
                Erro ao carregar comunidades: {error.message}
              </div>
            </div>
          </main>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="min-h-screen bg-white text-[#161616] font-manrope no-scrollbar">
        <Sidebar variant="static" />
        <div className="ml-0 min-[900px]:ml-64 no-scrollbar">
          <main className="flex flex-col gap-8 items-start pt-10 mx-auto my-0 w-full max-w-[1600px] px-6 max-md:gap-6 max-md:px-5 max-md:pt-8 max-md:max-w-[991px] max-sm:gap-5 max-sm:px-4 max-sm:pt-6 max-sm:max-w-screen-sm no-scrollbar">
            <header className="flex flex-col gap-4 items-start w-full">
              <h1 className="text-xl leading-10 text-zinc-900 max-md:text-lg max-md:leading-9 max-sm:text-base max-sm:leading-8">
                Administração
              </h1>
              <div className="w-full [&>div]:!w-full [&>div]:!max-w-none max-md:[&>div]:!px-3 max-sm:[&>div]:!px-2">
                <SearchBar value={searchQuery} onChange={setSearchQuery} />
              </div>
            </header>
            <section className="flex flex-col items-start w-full">
              {communities.filter(
                (community) =>
                  community.name
                    .toLowerCase()
                    .includes(searchQuery.toLowerCase()) ||
                  (community.description || "")
                    .toLowerCase()
                    .includes(searchQuery.toLowerCase())
              ).length === 0 ? (
                <div className="text-center py-8 text-neutral-500 w-full">
                  Nenhuma comunidade encontrada
                </div>
              ) : (
                communities
                  .filter(
                    (community) =>
                      community.name
                        .toLowerCase()
                        .includes(searchQuery.toLowerCase()) ||
                      (community.description || "")
                        .toLowerCase()
                        .includes(searchQuery.toLowerCase())
                  )
                  .map((community) => (
                    <article
                      key={community.id}
                      role="button"
                      tabIndex={0}
                      onClick={() => window.location.href = `/administration/${community.id}`}
                      onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') { window.location.href = `/administration/${community.id}`; } }}
                      className="flex flex-col gap-4 items-start px-6 py-4 w-full bg-white max-md:gap-3.5 max-md:px-5 max-md:py-3.5 max-sm:gap-3 max-sm:px-4 max-sm:py-3 text-left cursor-pointer outline-none"
                    >
                      <div className="flex justify-between items-start w-full max-sm:items-center">
                        <div className="w-12 h-12 flex items-center justify-center max-sm:w-10 max-sm:h-10">
                          <Image
                            src={`/icons/community/${[
                              "Coffee.png",
                              "Lantern.png",
                              "Myrobot.png",
                              "Reindeer.png",
                            ][Math.floor(Math.random() * 4)]
                              }`}
                            alt="Community icon"
                            width={52}
                            height={52}
                            className="object-contain"
                          />
                        </div>
                        <button
                          type="button"
                          aria-label="Menu options"
                          className="p-1 cursor-pointer hover:bg-gray-200 rounded-full transition max-sm:hidden"
                          onClick={e => { e.stopPropagation(); /* menu logic aqui */ }}
                        >
                          <OverflowMenuHorizontal size={20} />
                        </button>
                      </div>
                      <div className="flex justify-between items-center w-full">
                        <div className="flex flex-col flex-1 gap-2 items-start">
                          <h2 className="text-xl font-medium leading-8 text-neutral-800 max-md:text-lg max-md:leading-7 max-sm:text-base max-sm:leading-6">
                            {community.name}
                          </h2>
                          <div className="flex gap-1 items-center max-sm:gap-1">
                            <span className="text-xs text-neutral-500 max-sm:text-xs">
                              Fundador
                            </span>
                            <span className="text-xs text-neutral-500 max-sm:text-xs">
                              {community.type_community ||
                                "Tipo não especificado"}
                            </span>
                          </div>
                          {community.description && (
                            <p className="text-xs text-neutral-500 mt-1 line-clamp-2">
                              {community.description}
                            </p>
                          )}
                          {community.memberCount && (
                            <p className="text-xs text-neutral-500">
                              {community.memberCount} membros
                            </p>
                          )}
                        </div>
                        <span className="p-1 rounded-full transition">
                          <ArrowRight size={20} />
                        </span>
                      </div>
                    </article>
                  ))
              )}
            </section>
          </main>
        </div>
      </div>
    </>
  );
}
