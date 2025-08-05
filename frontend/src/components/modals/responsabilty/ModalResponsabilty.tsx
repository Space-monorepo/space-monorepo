"use client";
import * as React from "react";
import { ModalCreatePublication } from "../createPublication/ModalCreatePublication";

const ModalResponsibility: React.FC<{ onClose?: () => void }> = ({
  onClose,
}) => {
  const [showCampaignModal, setShowCampaignModal] = React.useState(false);

  const handleCancel = () => {
    console.log("Cancelar clicado");
    if (onClose) onClose();
  };

  const handleAgree = () => {
    console.log("Concordar clicado");
    setShowCampaignModal(true);
  };

  return (
    <>
      {!showCampaignModal && (
        <div className="fixed inset-0 flex items-center justify-center bg-[#858585]/80 backdrop-blur-xd z-50">
          <article className="flex flex-col gap-12 items-center pt-8 shadow-sm bg-neutral-800 w-[640px] max-md:w-[90%] max-sm:w-[95%]">
            <div className="flex flex-col gap-5 items-start w-[577px] max-md:w-[90%] max-sm:w-[95%]">
              <header className="flex flex-col gap-4 items-start w-full">
                <h1 className="w-full text-xl font-bold leading-normal text-neutral-200">
                  Publicar é um ato de responsabilidade.
                </h1>
                <p className="w-full text-sm leading-normal text-zinc-100">
                  Antes de criar sua publicação, lembre-se de que o que você
                  compartilha aqui impacta diretamente a experiência da
                  comunidade e também a sua própria reputação como membro.
                </p>
              </header>

              <section className="w-full text-sm leading-normal text-zinc-100">
                <p>
                  Cada tipo de publicação — seja uma campanha, denúncia, anúncio
                  ou enquete — carrega consigo um propósito. Ao utilizar esses
                  espaços com clareza, respeito e intenção positiva, você
                  fortalece a comunidade e sua imagem dentro dela.
                </p>
                <p className="mt-4">
                  No entanto, o uso inadequado pode gerar consequências.
                  Publicações que violem as diretrizes ou causem desconforto
                  podem ser denunciadas por outros membros. Ao atingir um número
                  limite de denúncias, a moderação será acionada. Isso pode
                  levar à suspensão temporária ou remoção da sua publicação, e,
                  em casos mais sérios, à suspensão ou banimento da conta.
                </p>
                <p className="mt-4">
                  <strong className="font-bold">
                    Nossa recomendação é simples:{" "}
                  </strong>
                  compartilhe com consciência, pense no coletivo e use sua voz
                  para construir, somar e inspirar.
                </p>
                <p className="mt-4">
                  O espaço é seu. A responsabilidade também.
                </p>
                <footer className="mt-4">
                  <p>
                    Atenciosamente,
                    <br />
                    Equipe Space.
                  </p>
                </footer>
              </section>
            </div>{" "}
            <footer className="flex w-full">
              <button
                onClick={handleCancel}
                className="text-left flex-1 py-4 px-4 text-sm leading-6 cursor-pointer bg-neutral-200 text-neutral-800"
              >
                Cancelar
              </button>
              <button
                onClick={handleAgree}
                className="text-left flex-1 py-4 px-4 text-sm leading-6 cursor-pointer bg-neutral-800 text-zinc-100"
              >
                Concordar e seguir
              </button>
            </footer>
          </article>
        </div>
      )}
      {showCampaignModal && (
        <ModalCreatePublication
          isOpen={showCampaignModal}
          onClose={() => {
            setShowCampaignModal(false); // Esconde o ModalCampaign
            if (onClose) {
              onClose(); // Agora fecha o ModalResponsibility (se o pai forneceu onClose)
            }
          }}
        />
      )}
    </>
  );
};

export default ModalResponsibility;
