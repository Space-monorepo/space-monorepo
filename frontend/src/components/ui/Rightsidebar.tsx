"use client";

import { useEffect, useState } from "react";
import { Loader2 } from "lucide-react";
import useRightSidebarData from "@/app/api/src/hooks/sidebar/useRightSidebarData";
import PostPreviewModal from "@/components/modals/PostPreviewModal";
import { translatePostType } from "@/lib/postTypeTranslations";
import { translateUserRole } from "@/lib/roleTranslations";
import { getRelativeTime } from "@/lib/relativeTime";

export default function RightSidebar() {

  const { userCampaigns, loading, error, refreshCampaigns } = useRightSidebarData();
  const [isPostPreviewOpen, setIsPostPreviewOpen] = useState(false);
  const [postPreviewData, setPostPreviewData] = useState<any>(null);

  // Campanhas em engajamento: ordena por soma de likes + comentários e pega as top 3
  const trendingCampaigns = [...userCampaigns]
    .sort((a, b) => (b.likes_count + b.comments_count) - (a.likes_count + a.comments_count))
    .slice(0, 3)
    .filter(c => (c.likes_count + c.comments_count) > 0);

  useEffect(() => {
    refreshCampaigns();
  }, [refreshCampaigns]);

  const truncateText = (text: string, maxLength: number = 30) => {
    return text.length > maxLength
      ? text.substring(0, maxLength) + "..."
      : text;
  };

  return (
    <nav className="flex flex-col shrink-0 gap-10 items-start pt-10 pr-0 pb-0 pl-5 border border-solid border-t-0 bg-zinc-100 border-stone-300 h-[927px] w-[330px] max-md:gap-8 max-md:px-4 max-md:py-8 max-md:w-full max-md:h-auto max-md:max-w-[330px] max-sm:gap-5 max-sm:px-2.5 max-sm:py-5 max-sm:w-full max-sm:border-b max-sm:border-solid max-sm:border-t-0 max-sm:border-[none] max-sm:border-y-stone-300 lg:block fixed right-0 top-16 bottom-0 overflow-y-auto z-[5]">
      <section className="flex relative flex-col items-start w-[180px] max-md:w-full mb-8">
        <header className="flex relative gap-2 items-center self-stretch px-0 py-3 max-sm:px-0 max-sm:py-2 mb-2">
          <h2 className="text-sm font-bold text-neutral-800 max-sm:text-sm">
            Minhas Campanhas
          </h2>
        </header>
        <div className="flex relative flex-col gap-1 items-start self-stretch max-md:w-full">
          {loading.campaigns ? (
            <div className="flex items-center justify-center p-4 self-stretch">
              <Loader2 className="h-4 w-4 animate-spin text-neutral-800" />
              <span className="ml-2 text-xs text-neutral-800">
                Carregando...
              </span>
            </div>
          ) : error.campaigns ? (
            <div className="flex relative gap-2 items-center self-stretch p-3 rounded-sm bg-red-100 max-md:w-full max-sm:p-2.5">
              <div className="relative text-xs text-red-600 w-[139px] max-sm:text-xs">
                <p className="text-xs text-red-600">Erro ao carregar campanhas</p>
              </div>
            </div>
          ) : userCampaigns.length > 0 ? (
            userCampaigns.map((campaign, index) => (
              <article key={campaign.id} className="flex relative flex-col gap-1 items-start self-stretch max-md:w-full">
                <div
                  className="flex relative gap-2 items-center self-stretch p-3 rounded-sm bg-neutral-200 hover:bg-neutral-300 transition-colors cursor-pointer max-md:w-full max-sm:p-2.5"
                  onClick={() => {
                    setPostPreviewData({
                      id: campaign.id,
                      title: campaign.title,
                      content: campaign.content,
                      author: campaign.user.name,
                      avatar: campaign.user.profile_picture || "/no-profile-pic.png",
                      role: translateUserRole(campaign.user.role),
                      location: campaign.community.name,
                      type: translatePostType(campaign.type_post),
                      time: getRelativeTime(campaign.created_at),
                      imageUrl: campaign.image_url,
                      likes: campaign.likes_count,
                      comments: campaign.comments_count,
                      shares: campaign.report_count,
                      username: campaign.user.username || campaign.user.id,
                      user: {
                        id: campaign.user.id,
                        profile_picture: campaign.user.profile_picture
                      }
                    });
                    setIsPostPreviewOpen(true);
                  }}
                >
                  <div>
                    <div
                      dangerouslySetInnerHTML={{
                        __html:
                          "<svg layer-name=\"bookmark\" data-component-name=\"bookmark\" width=\"16\" height=\"16\" viewBox=\"0 0 16 16\" fill=\"none\" xmlns=\"http://www.w3.org/2000/svg\" class=\"bookmark-icon\" style=\"width: 16px; height: 16px; position: relative\"> <path d=\"M3.33325 14V3.33333C3.33325 2.96667 3.46381 2.65278 3.72492 2.39167C3.98603 2.13056 4.29992 2 4.66659 2H11.3333C11.6999 2 12.0138 2.13056 12.2749 2.39167C12.536 2.65278 12.6666 2.96667 12.6666 3.33333V14L7.99992 12L3.33325 14ZM4.66659 11.9667L7.99992 10.5333L11.3333 11.9667V3.33333H4.66659V11.9667Z\" fill=\"#262626\"></path> </svg>",
                      }}
                    />
                  </div>
                  <div className="relative text-xs text-neutral-800 w-[139px] max-sm:text-xs" title={campaign.title}>
                    <p className="text-xs text-neutral-800">{truncateText(campaign.title)}</p>
                  </div>
                </div>
                <div className="relative h-1 w-[180px] max-md:w-full">
                  <div className="absolute top-0 left-0 shrink-0 h-1 bg-neutral-200 w-[180px] max-md:w-full" />
                  <div
                    className="absolute top-0 left-0 shrink-0 h-1 bg-neutral-800"
                    style={{ width: `${Math.min(93 + (index * 28), 149)}px` }}
                  />
                </div>
              </article>
            ))
          ) : (
            <div className="flex relative gap-2 items-center self-stretch p-3 rounded-sm bg-neutral-200 max-md:w-full max-sm:p-2.5">
              <div className="relative text-xs text-neutral-800 w-[139px] max-sm:text-xs">
                <p className="text-xs text-neutral-800">Você ainda não criou nenhuma campanha</p>
              </div>
            </div>
          )}
        </div>
      </section>

      <section className="flex relative flex-col items-start self-stretch mb-8">
        <header className="flex relative gap-2 items-center self-stretch px-0 py-3 max-sm:px-0 max-sm:py-2 mb-2">
          <h2 className="text-sm font-bold text-neutral-800 max-sm:text-sm">
            Em discussão agora
          </h2>
        </header>
        {trendingCampaigns.length > 0 ? (
          trendingCampaigns.map((campaign) => (
            <article key={campaign.id} className="flex relative gap-2 items-center self-stretch px-0 py-2 max-sm:px-0 max-sm:py-1.5">
              <div>
                <div
                  dangerouslySetInnerHTML={{
                    __html:
                      "<svg layer-name=\"Trending up\" data-component-name=\"Trending up\" data-variant-name=\"Size=24\" width=\"16\" height=\"16\" viewBox=\"0 0 16 16\" fill=\"none\" xmlns=\"http://www.w3.org/2000/svg\" class=\"trending-icon\" style=\"width: 16px; height: 16px; position: relative\"> <g clip-path=\"url(#clip0_545_4615)\"> <path d=\"M15.3334 4L9.00008 10.3333L5.66675 7L0.666748 12M15.3334 4H11.3334M15.3334 4V8\" stroke=\"#262626\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"></path> </g> <defs> <clipPath id=\"clip0_545_4615\"> <rect width=\"16\" height=\"16\" fill=\"white\"></rect> </clipPath> </defs> </svg>",
                  }}
                />
              </div>
              <div className="relative text-xs text-neutral-800" title={campaign.title}>
                <p className="text-xs text-neutral-800 max-sm:text-xs font-semibold">{truncateText(campaign.title)}</p>
              </div>
            </article>
          ))
        ) : (
          <article className="flex relative gap-2 items-center self-stretch px-0 py-2 max-sm:px-0 max-sm:py-1.5">
            <div>
              <div
                dangerouslySetInnerHTML={{
                  __html:
                    "<svg layer-name=\"Trending up\" data-component-name=\"Trending up\" data-variant-name=\"Size=24\" width=\"16\" height=\"16\" viewBox=\"0 0 16 16\" fill=\"none\" xmlns=\"http://www.w3.org/2000/svg\" class=\"trending-icon\" style=\"width: 16px; height: 16px; position: relative\"> <g clip-path=\"url(#clip0_545_4615)\"> <path d=\"M15.3334 4L9.00008 10.3333L5.66675 7L0.666748 12M15.3334 4H11.3334M15.3334 4V8\" stroke=\"#262626\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"></path> </g> <defs> <clipPath id=\"clip0_545_4615\"> <rect width=\"16\" height=\"16\" fill=\"white\"></rect> </clipPath> </defs> </svg>",
                }}
              />
            </div>
            <div className="relative text-xs text-neutral-800">
              <p className="text-xs text-neutral-800 max-sm:text-xs">Não há discussões criadas no momento</p>
            </div>
          </article>
        )}
      </section>

      <section className="flex relative flex-col items-start self-stretch mb-8">
        <header className="flex relative gap-2 items-center self-stretch px-0 py-3 max-sm:px-0 max-sm:py-2 mb-2">
          <h2 className="text-sm font-bold text-neutral-800 max-sm:text-sm">
            Agenda Comunitária
          </h2>
        </header>
        <article className="flex relative gap-2 items-center self-stretch px-0 py-2 max-sm:px-0 max-sm:py-1.5">
          <div>
            <div
              dangerouslySetInnerHTML={{
                __html:
                  "<svg layer-name=\"today\" data-component-name=\"today\" width=\"16\" height=\"16\" viewBox=\"0 0 16 16\" fill=\"none\" xmlns=\"http://www.w3.org/2000/svg\" class=\"calendar-icon\" style=\"width: 16px; height: 16px; position: relative\"> <path d=\"M6 10.9999C5.53333 10.9999 5.13889 10.8388 4.81667 10.5166C4.49444 10.1944 4.33333 9.79992 4.33333 9.33325C4.33333 8.86659 4.49444 8.47214 4.81667 8.14992C5.13889 7.8277 5.53333 7.66659 6 7.66659C6.46667 7.66659 6.86111 7.8277 7.18333 8.14992C7.50556 8.47214 7.66667 8.86659 7.66667 9.33325C7.66667 9.79992 7.50556 10.1944 7.18333 10.5166C6.86111 10.8388 6.46667 10.9999 6 10.9999ZM3.33333 14.6666C2.96667 14.6666 2.65278 14.536 2.39167 14.2749C2.13056 14.0138 2 13.6999 2 13.3333V3.99992C2 3.63325 2.13056 3.31936 2.39167 3.05825C2.65278 2.79714 2.96667 2.66659 3.33333 2.66659H4V1.33325H5.33333V2.66659H10.6667V1.33325H12V2.66659H12.6667C13.0333 2.66659 13.3472 2.79714 13.6083 3.05825C13.8694 3.31936 14 3.63325 14 3.99992V13.3333C14 13.6999 13.8694 14.0138 13.6083 14.2749C13.3472 14.536 13.0333 14.6666 12.6667 14.6666H3.33333ZM3.33333 13.3333H12.6667V6.66659H3.33333V13.3333Z\" fill=\"#1D1B20\"></path> </svg>",
              }}
            />
          </div>
          <div className="relative text-xs text-neutral-800 w-[139px] max-sm:text-xs">
            <p className="text-xs text-neutral-800">Não há eventos programados no momento</p>
          </div>
        </article>
      </section>

      {/* Modal de visualização do post */}
      <PostPreviewModal
        post={postPreviewData}
        isOpen={isPostPreviewOpen}
        onClose={() => setIsPostPreviewOpen(false)}
      />
    </nav>
  );
}
