"use client";

import { Dialog } from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { useState, useEffect } from "react";
import { Close } from "@carbon/icons-react";
import { ModalCampaign } from "../posts/ModalCampaign";
import Cookies from "js-cookie";
import { useAuth } from "@/app/api/src/auth/useAuth";
import { ModalComplaint } from "../posts/ModalComplaint";
import { ModalPoll } from "../posts/ModalPoll";
import { ModalAnnouncement } from "../posts/ModalAnnouncement";
import useCommunityActions from "@/app/api/src/hooks/community/useCommunityActions";

interface ModalCreatePublicationProps {
  isOpen: boolean;
  onClose: () => void;
}

type PublicationType = "campaign" | "complaint" | "poll" | "announcement";

export function ModalCreatePublication({
  isOpen,
  onClose,
}: ModalCreatePublicationProps) {
  const { user } = useAuth();
  const authToken = Cookies.get("token");
  const [selectedCommunity, setSelectedCommunity] = useState("");
  const [publicationType, setPublicationType] = useState<PublicationType | "">(
    ""
  );
  const [showNextModal, setShowNextModal] = useState(false);

  const {
    communities: fetchedCommunities,
    loading: communitiesLoading,
    error: communitiesError,
    fetchCommunities,
  } = useCommunityActions();

  useEffect(() => {
    fetchCommunities();
  }, [fetchCommunities]);

  const publicationTypes = [
    { value: "campaign", label: "Campanha" },
    { value: "complaint", label: "Denúncia" },
    { value: "poll", label: "Enquete" },
    { value: "announcement", label: "Anúncio" },
  ];

  const handleCreate = () => {
    if (selectedCommunity && publicationType) {
      setShowNextModal(true);
    }
  };

  const handleClose = () => {
    setSelectedCommunity("");
    setPublicationType("");
    setShowNextModal(false);
    onClose();
  };

  if (showNextModal) {
    switch (publicationType) {
      case "campaign":
        return (
          <ModalCampaign
            onClose={handleClose}
            communityId={selectedCommunity}
            userId={user?.username || ""}
            authToken={authToken || ""}
          />
        );
      case "complaint":
        return (
          <ModalComplaint
            onClose={handleClose}
            communityId={selectedCommunity}
          />
        );
      case "poll":
        return (
          <ModalPoll onClose={handleClose} communityId={selectedCommunity} />
        );
      case "announcement":
        return (
          <ModalAnnouncement
            onClose={handleClose}
            communityId={selectedCommunity}
          />
        );
      default:
        return null;
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <div className="fixed inset-0 bg-[#858585]/80 backdrop-blur-xd flex items-center justify-center">
        <main className="w-[640px] h-[344px] shadow-sm bg-zinc-100 border-stone-300 flex flex-col">
          <header className="flex flex-wrap gap-10 justify-between items-start p-4 w-full text-xl text-neutral-800 max-md:max-w-full">
            <h1 className="text-neutral-800">Criar publicação</h1>
            <button
              onClick={handleClose}
              className="focus:outline-none focus:ring-2 focus:ring-neutral-400"
              aria-label="Fechar"
            >
              <Close size={20} className="object-contain shrink-0 w-5 aspect-square" />
            </button>
          </header>

          <section className="px-4 pb-6 w-full max-md:max-w-full">
            <label className="text-xs text-neutral-500 max-md:max-w-full">
              Selecione a comunidade
            </label>
            <div className="mt-2 w-full text-sm leading-6 whitespace-nowrap text-neutral-800 max-md:max-w-full">
              <Select
                value={selectedCommunity}
                onValueChange={setSelectedCommunity}
                disabled={communitiesLoading}
              >
                <SelectTrigger className="flex flex-wrap gap-10 justify-between rounded-none items-center px-4 py-3 w-full bg-neutral-200 border-0 hover:bg-neutral-200 focus:bg-neutral-200 focus:ring-0 focus:ring-offset-0 max-md:max-w-full">
                  <SelectValue placeholder="Selecione uma comunidade" />
                </SelectTrigger>
                <SelectContent className="bg-white border border-neutral-300 shadow-lg">
                  {communitiesError && (
                    <SelectItem
                      value="error-loading"
                      disabled
                      className="flex flex-wrap gap-10 justify-between rounded-none items-center px-4 py-3 w-full bg-neutral-200 border-0 text-red-500"
                    >
                      Erro ao carregar comunidades. Tente novamente.
                    </SelectItem>
                  )}
                  {!communitiesLoading &&
                    !communitiesError &&
                    fetchedCommunities.length === 0 && (
                      <SelectItem value="no-communities" disabled className="flex flex-wrap gap-10 justify-between rounded-none items-center px-4 py-3 w-full bg-neutral-200">
                        Nenhuma comunidade encontrada.
                      </SelectItem>
                    )}
                  {fetchedCommunities.map((community) => (
                    <SelectItem
                      className="flex flex-wrap gap-10 justify-between rounded-none items-center px-6 py-3 w-full text-black hover:bg-neutral-300 focus:bg-neutral-100 cursor-pointer"
                      key={community.id}
                      value={community.id}
                    >
                      {community.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <div className="flex w-full bg-neutral-400 min-h-px max-md:max-w-full" />
            </div>
          </section>

          <section className="px-4 pb-12 w-full max-md:max-w-full">
            <label className="text-xs text-neutral-500 max-md:max-w-full">
              Selecione o tipo da publicação
            </label>
            <div className="mt-2 w-full text-sm leading-6 whitespace-nowrap text-neutral-800 max-md:max-w-full">
              <Select
                value={publicationType}
                onValueChange={(value) =>
                  setPublicationType(value as PublicationType)
                }
              >
                <SelectTrigger className="flex flex-wrap gap-10 rounded-none justify-between items-center px-4 py-3 w-full bg-neutral-200 border-0 hover:bg-neutral-200 focus:bg-neutral-200 focus:ring-0 focus:ring-offset-0 max-md:max-w-full">
                  <SelectValue placeholder="Selecione um tipo" />

                </SelectTrigger>
                <SelectContent className="bg-white border border-neutral-300 shadow-lg">
                  {publicationTypes.map((type) => (
                    <SelectItem
                      className="flex flex-wrap gap-10 justify-between rounded-none items-center px-6 py-3 w-full border-0 text-black hover:bg-neutral-300 focus:bg-neutral-100 cursor-pointer"
                      key={type.value}
                      value={type.value}
                    >
                      {type.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <div className="flex w-full bg-neutral-400 min-h-px max-md:max-w-full" />
            </div>
          </section>

          <footer className="flex w-full h-16 text-sm leading-6 whitespace-nowrap mt-auto">
            <button
              onClick={handleClose}
              className="w-1/2 h-full flex items-center justify-start p-4 bg-neutral-200 text-neutral-800 focus:outline-none focus:ring-2 focus:ring-neutral-400 border-r border-neutral-300 cursor-pointer"
            >
              Cancelar
            </button>
            <button
              onClick={handleCreate}
              disabled={!selectedCommunity || !publicationType}
              className="w-1/2 h-full flex items-center justify-start p-4 bg-neutral-800 text-zinc-100 disabled:bg-neutral-400 focus:outline-none focus:ring-2 focus:ring-zinc-400 cursor-pointer"
            >
              Criar
            </button>
          </footer>
        </main>
      </div>
    </Dialog>
  );
}
