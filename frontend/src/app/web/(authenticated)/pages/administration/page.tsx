"use client";

import Sidebar from "@/components/ui/sidebar";
import Link from "next/link";
import useCommunityActions from "@/app/api/src/hooks/community/useCommunityActions";
import {
  Search,
  OverflowMenuHorizontal,
  ArrowRight,
} from "@carbon/icons-react";

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
    <>
      <div className="min-h-screen bg-white text-[#161616] font-manrope">
        <Sidebar variant="static" />
        <div className="ml-64">
          <main className="flex flex-col gap-8 items-start pt-10 mx-auto my-0 w-full max-w-[1600px] max-md:gap-6 max-md:px-5 max-md:pt-8 max-md:max-w-[991px] max-sm:gap-5 max-sm:px-4 max-sm:pt-6 max-sm:max-w-screen-sm">
            <header className="flex flex-col gap-4 items-start w-full">
              <h1 className="text-xl leading-10 text-zinc-900 max-md:text-lg max-md:leading-9 max-sm:text-base max-sm:leading-8">
                Administração
              </h1>
              <div className="box-border flex gap-2.5 items-center px-3 py-2 w-full bg-white rounded border border-solid border-stone-300 max-md:px-3.5 max-md:py-2.5 max-sm:gap-2 max-sm:px-4 max-sm:py-3">
                <div>
                  <Search size={20} />
                </div>
                <span className="text-sm leading-6 text-neutral-500 max-sm:text-sm max-sm:leading-5">
                  Pesquisar
                </span>
              </div>
            </header>
            <section className="flex flex-col items-start w-full">
              {communities.length === 0 ? (
                <div className="text-center py-8 text-neutral-500 w-full">
                  Nenhuma comunidade encontrada
                </div>
              ) : (
                communities.map((community) => (
                  <article
                    key={community.id}
                    className="flex flex-col gap-4 items-start px-6 py-4 w-full bg-white max-md:gap-3.5 max-md:px-5 max-md:py-3.5 max-sm:gap-3 max-sm:px-4 max-sm:py-3"
                  >
                    <div className="flex justify-between items-start w-full max-sm:items-center">
                      <div className="w-12 h-12 rounded flex items-center justify-center text-xl bg-[#f4f4f4] border border-[#e0e0e0] max-sm:w-10 max-sm:h-10">
                        <span>🏢</span>
                      </div>
                      <button
                        type="button"
                        aria-label="Menu options"
                        className="p-1"
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
                      <Link href={`/administration/${community.id}`}>
                        <button
                          type="button"
                          aria-label="View community details"
                          className="p-1"
                        >
                          <ArrowRight size={20} />
                        </button>
                      </Link>
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
