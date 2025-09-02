"use client";

import { useState } from "react";
import { Attachment, FaceActivated, TextBold, TextItalic, Close } from "@carbon/icons-react";

type RejectCampaignModalProps = {
  isOpen: boolean;
  onClose: () => void;
  onReject: (subject: string, reason: string) => void;
  campaignTitle: string;
  campaignAuthor: string;
};

export default function RejectCampaignModal({
  isOpen,
  onClose,
  onReject,
}: RejectCampaignModalProps) {
  const [subject, setSubject] = useState("");
  const [reason, setReason] = useState("");

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm bg-opacity-50 flex items-center justify-center z-50">
      <div className="border-solid shadow-sm bg-zinc-100 border-stone-300 max-w-[926px] w-full">
        {/* Header */}
        <header className="flex flex-wrap gap-10 justify-between items-start p-4 w-full text-xl leading-relaxed text-neutral-800 max-md:max-w-full">
          <h1 className="text-neutral-800">
            Rejeitar campanha
          </h1>
          <button
            onClick={onClose}
            className="shrink-0 w-5 aspect-square hover:opacity-70 transition-opacity"
            aria-label="Fechar"
          >
            <Close className="w-full h-full text-neutral-800" />
          </button>
        </header>

        <div className="flex flex-col justify-center px-4 pb-12 w-full max-md:max-w-full">
          {/* Description Section */}
          <section className="w-full text-sm text-neutral-800 max-md:max-w-full">
            <div className="w-full max-md:max-w-full">
              <p className="text-neutral-800 max-md:max-w-full">
                Você está prestes a rejeitar esta campanha. Essa ação a deixará
                invisível para a comunidade e será registrada no histórico.
              </p>
              <p className="mt-5 text-neutral-800 max-md:max-w-full">
                Para manter o processo transparente, explique brevemente o motivo da
                rejeição. Seu feedback ajuda o autor a entender o que precisa ser
                ajustado — e mantém a confiança de todos no sistema.
              </p>
            </div>
          </section>

          {/* Subject Input */}
          <div className="mt-8 w-full text-sm leading-6 max-md:max-w-full">
            <div className="flex gap-6 items-start w-full max-md:max-w-full">
              <div className="flex-1 shrink w-full basis-0 min-w-60 max-md:max-w-full">
                <div className="w-full max-md:max-w-full">
                  <label className="text-neutral-800 max-md:max-w-full">
                    Assunto
                  </label>
                  <div className="mt-2 w-full text-neutral-500 max-md:max-w-full">
                    <div className="flex gap-8 items-center px-4 py-2 w-full bg-neutral-200 max-md:max-w-full">
                      <input
                        type="text"
                        value={subject}
                        onChange={(e) => setSubject(e.target.value)}
                        placeholder="Escreva o Assunto"
                        className="flex-1 bg-transparent text-neutral-500 outline-none placeholder-neutral-500"
                      />
                    </div>
                    <div className="flex w-full bg-neutral-500 min-h-px max-md:max-w-full" />
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Reason Textarea */}
          <div className="mt-8 w-full max-md:max-w-full">
            <div className="w-full max-md:max-w-full">
              <label className="text-sm leading-6 text-neutral-800 max-md:max-w-full">
                Motivo
              </label>
              <div className="mt-4 w-full max-md:max-w-full">
                <div className="flex flex-col justify-between p-4 w-full rounded-sm bg-neutral-200 min-h-[236px] max-md:max-w-full">
                  <textarea
                    value={reason}
                    onChange={(e) => setReason(e.target.value)}
                    placeholder="Escreva aqui..."
                    className="flex-1 bg-transparent text-sm leading-6 text-neutral-600 outline-none placeholder-neutral-600 resize-none"
                    rows={8}
                  />
                  <div className="flex gap-4 items-start self-start mt-4">
                    <button className="w-5 aspect-square text-neutral-600 hover:text-neutral-800 transition-colors" aria-label="Anexar arquivo">
                      <Attachment className="w-full h-full" />
                    </button>
                    <button className="w-5 aspect-square text-neutral-600 hover:text-neutral-800 transition-colors" aria-label="Emoji">
                      <FaceActivated className="w-full h-full" />
                    </button>
                    <button className="w-5 aspect-square text-neutral-600 hover:text-neutral-800 transition-colors" aria-label="Negrito">
                      <TextBold className="w-full h-full" />
                    </button>
                    <button className="w-5 aspect-square text-neutral-600 hover:text-neutral-800 transition-colors" aria-label="Itálico">
                      <TextItalic className="w-full h-full" />
                    </button>
                  </div>
                </div>
                <div className="flex w-full bg-neutral-500 min-h-px max-md:max-w-full" />
              </div>
            </div>

            {/* Participant Info */}
            <div className="flex flex-wrap gap-6 items-start mt-6 w-full text-sm leading-6 max-md:max-w-full">
              <div className="flex-1 shrink basis-0 min-w-60 max-md:max-w-full">
                <p className="text-neutral-500 max-md:max-w-full">
                  De
                </p>
                <div className="flex gap-2 justify-center items-center mt-2 w-full font-medium rounded-lg text-neutral-800 max-md:max-w-full">
                  <div className="w-6 h-6 rounded-2xl overflow-hidden">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src="/ProfilePic1.svg"
                      alt="Briann Gomes"
                      className="object-contain w-full h-full"
                    />
                  </div>
                  <span className="flex-1 shrink self-stretch my-auto basis-0 text-neutral-800">
                    Briann Gomes
                  </span>
                </div>
              </div>
              <div className="flex-1 shrink basis-0 min-w-60 max-md:max-w-full">
                <p className="text-neutral-500 max-md:max-w-full">
                  Para
                </p>
                <div className="flex gap-2 justify-center items-center mt-2 w-full font-medium rounded-lg text-neutral-800 max-md:max-w-full">
                  <span className="flex-1 shrink self-stretch my-auto basis-0 text-neutral-800 max-md:max-w-full">
                    Todos os participantes da campanha
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <footer className="flex flex-wrap items-center w-full text-sm leading-6 whitespace-nowrap max-md:max-w-full">
          <button
            onClick={onClose}
            className="flex gap-8 items-center self-stretch pt-4 pr-16 pb-6 pl-4 my-auto bg-neutral-200 min-w-60 text-neutral-800 w-[462px] max-md:pr-5 max-md:max-w-full hover:bg-neutral-300 transition-colors"
          >
            <span className="self-stretch my-auto text-neutral-800">
              Cancelar
            </span>
          </button>
          <button
            onClick={() => onReject(subject, reason)}
            className="flex flex-1 shrink gap-8 items-center self-stretch pt-4 pr-16 pb-6 pl-4 basis-0 bg-red-700 min-w-60 text-zinc-100 max-md:pr-5 max-md:max-w-full hover:bg-red-800 transition-colors"
          >
            <span className="self-stretch my-auto text-zinc-100">
              Rejeitar e relatar
            </span>
          </button>
        </footer>
      </div>
    </div>
  );
}
