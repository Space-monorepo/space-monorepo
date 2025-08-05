"use client";

import { useEffect } from "react";
import { Loader2 } from "lucide-react";
import useRightSidebarData from "@/app/api/src/hooks/sidebar/useRightSidebarData";

export default function RightSidebar() {
  const { userCampaigns, loading, error, refreshCampaigns } =
    useRightSidebarData();

  useEffect(() => {
    refreshCampaigns();
  }, [refreshCampaigns]);

  const truncateText = (text: string, maxLength: number = 30) => {
    return text.length > maxLength
      ? text.substring(0, maxLength) + "..."
      : text;
  };

  return (
    <div className="w-72 border-l my-10 border-[#e0e0e0] bg-gray-100 p-4 hidden lg:block fixed right-0 top-16 bottom-0 overflow-y-auto z-[5]">
      <div className="space-y-6">
        {/* Minhas Campanhas */}
        <div>
          <h3 className="font-medium mb-3">Minhas Campanhas</h3>
          <div className="space-y-2">
            {loading.campaigns ? (
              <div className="flex items-center justify-center p-4">
                <Loader2 className="h-4 w-4 animate-spin text-[#525252]" />
                <span className="ml-2 text-sm text-[#525252]">
                  Carregando...
                </span>
              </div>
            ) : error.campaigns ? (
              <div className="p-3 bg-red-50 rounded text-center">
                <span className="text-sm text-red-600">
                  Erro ao carregar campanhas
                </span>
              </div>
            ) : userCampaigns.length > 0 ? (
              userCampaigns.map((campaign) => (
                <div
                  key={campaign.id}
                  className="p-3 bg-[#E0E0E0] rounded flex items-center gap-2 hover:bg-[#d0d0d0] transition-colors cursor-pointer"
                >
                  <div className="w-5 h-5 flex items-center justify-center">
                    <span className="text-md">📄</span>
                  </div>
                  <span className="text-sm" title={campaign.title}>
                    {truncateText(campaign.title)}
                  </span>
                </div>
              ))
            ) : (
              <div className="p-3 bg-[#f4f4f4] rounded text-center">
                <span className="text-sm text-[#525252]">
                  Você ainda não criou nenhuma campanha
                </span>
              </div>
            )}
          </div>
        </div>{" "}
        {/* Em discussão agora */}
        <div>
          <h3 className="font-medium mb-3">Em discussão agora</h3>
          <div className="space-y-2">
            <div className="p-3 bg-[#f4f4f4] rounded text-center">
              <span className="text-sm text-[#525252]">
                Não há discussões criadas no momento
              </span>
            </div>
          </div>
        </div>
        {/* Agenda Comunitária */}
        <div>
          <h3 className="font-medium mb-3">Agenda Comunitária</h3>
          <div className="space-y-2">
            <div className="p-3 bg-[#f4f4f4] rounded text-center">
              <span className="text-sm text-[#525252]">
                Não há eventos programados no momento
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
