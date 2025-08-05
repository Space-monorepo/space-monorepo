"use client";
import * as React from "react";
import { useState, useRef } from "react";
import usePostActions from "@/app/api/src/hooks/post/usePostActions";
import { toast } from "react-toastify";

interface StepIndicatorProps {
  active: boolean;
  icon: string;
  label: string;
}

const StepIndicator: React.FC<StepIndicatorProps> = ({
  active,
  icon,
  label,
}) => {
  return (
    <div className="grow shrink self-stretch my-auto min-w-60 w-[243px]">
      <div
        className={`flex w-full ${
          active ? "bg-neutral-800" : "bg-stone-300"
        } min-h-0.5`}
      />
      <div className="flex gap-2 items-center mt-2.5 w-72 max-w-full">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={icon}
          alt=""
          className="object-contain shrink-0 self-stretch my-auto w-4 aspect-square"
        />
        <span className="self-stretch my-auto">{label}</span>
      </div>
    </div>
  );
};

const StepProgress: React.FC<{ currentStep: number }> = ({ currentStep }) => {
  return (
    <nav className="flex flex-wrap items-center py-4 w-full text-xs leading-none text-black max-md:max-w-full">
      <StepIndicator
        active={currentStep === 1}
        icon="https://cdn.builder.io/api/v1/image/assets/TEMP/1ef80c9a750193eba71404b8d050d883e7ab8686?placeholderIfAbsent=true&apiKey=c82d577402ec4a68b3d9eb6968f38275"
        label="Definir o título"
      />
      <StepIndicator
        active={currentStep === 2}
        icon="https://cdn.builder.io/api/v1/image/assets/TEMP/7dce8eec7e4883fda51019d4aaaf8f1a6fcc0a29?placeholderIfAbsent=true&apiKey=c82d577402ec4a68b3d9eb6968f38275"
        label="Escrever a publicação"
      />
    </nav>
  );
};

interface CampaignData {
  title: string;
  content: string;
  files: File[];
  community_id: string; // Adicionar community_id
}

const InputField: React.FC<{
  title: string;
  onTitleChange: (value: string) => void;
}> = ({ title, onTitleChange }) => {
  return (
    <section className="mt-6 w-full text-sm leading-6 text-neutral-500 max-md:max-w-full">
      <label className="block text-neutral-800 max-md:max-w-full">
        Título da denúncia
      </label>
      <input
        type="text"
        value={title}
        onChange={(e) => onTitleChange(e.target.value)}
        placeholder="Escreva o título da denúncia"
        className="gap-8 self-stretch px-4 py-2 mt-2 w-full bg-neutral-200 text-neutral-500 max-md:max-w-full"
        aria-label="Título da campanha"
      />
      <p className="mt-2 text-xs text-neutral-500 max-md:max-w-full">
        Este será o título exibido nas notificações para todos os participantes
        da denúncia. Certifique-se de escolher uma frase clara e direta.
      </p>
    </section>
  );
};

const WritePost: React.FC<{
  content: string;
  files: File[];
  onContentChange: (value: string) => void;
  onFilesChange: (files: File[]) => void;
}> = ({ content, files, onContentChange, onFilesChange }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const droppedFiles = Array.from(e.dataTransfer.files);
    onFilesChange([...files, ...droppedFiles]);
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  const handleFileSelect = () => {
    fileInputRef.current?.click();
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      onFilesChange([...files, ...selectedFiles]);
    }
  };

  return (
    <section className="mt-6 w-full text-sm leading-6 text-neutral-500">
      <label className="block text-neutral-800">Conteúdo da denúncia</label>
      <textarea
        value={content}
        onChange={(e) => onContentChange(e.target.value)}
        placeholder="Escreva o conteúdo da sua publicação"
        className="gap-8 self-stretch px-4 py-2 mt-2 w-full h-32 bg-neutral-200 text-neutral-500 resize-none"
        aria-label="Conteúdo da publicação"
      />
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileInput}
        className="hidden"
        multiple
      />
      <div
        onClick={handleFileSelect}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        className="mt-4 p-6 border-2 border-dashed border-neutral-300 rounded-lg text-center cursor-pointer hover:bg-neutral-50 transition-colors"
      >
        <p>Arraste e solte arquivos aqui ou clique para selecionar</p>
        {files.length > 0 && (
          <div className="mt-4">
            <h3 className="text-neutral-800 font-medium mb-2">
              Arquivos selecionados:
            </h3>
            <ul className="space-y-1">
              {files.map((file, index) => (
                <li
                  key={index}
                  className="flex items-center justify-between bg-neutral-100 p-2 rounded"
                >
                  <span>{file.name}</span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onFilesChange(files.filter((_, i) => i !== index));
                    }}
                    className="text-red-500 hover:text-red-700"
                  >
                    Remover
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </section>
  );
};

const NavigationButtons: React.FC<{
  onBack: () => void;
  onNext: () => void;
  currentStep: number;
}> = ({ onBack, onNext, currentStep }) => {
  return (
    <footer className="flex items-center w-full text-sm leading-6 whitespace-nowrap max-md:max-w-full mt-auto">
      <button
        onClick={onBack}
        type="button"
        className="flex-1 pt-4 pr-16 pb-6 pl-4 bg-neutral-200 text-neutral-800 max-md:pr-5 hover:bg-neutral-300 transition-colors"
        aria-label="Voltar para a etapa anterior"
        disabled={currentStep === 1}
        style={{ opacity: currentStep === 1 ? 0.5 : 1 }}
      >
        Voltar
      </button>
      <button
        onClick={onNext}
        type="button"
        className="flex-1 pt-4 pr-16 pb-6 pl-4 bg-neutral-800 text-zinc-100 max-md:pr-5 hover:bg-neutral-900 transition-colors"
        aria-label="Avançar para a próxima etapa"
      >
        {currentStep === 1 ? "Seguinte" : "Concluir"}
      </button>
    </footer>
  );
};

// Adicionar a prop onClose à interface
export const ModalComplaint: React.FC<{
  onClose?: () => void;
  communityId: string;
}> = ({
  onClose,
  communityId, // Receber communityId
}) => {
  const [currentStep, setCurrentStep] = useState<number>(1);
  const [campaignData, setCampaignData] = useState<CampaignData>({
    title: "",
    content: "",
    files: [],
    community_id: communityId, // Usar communityId aqui
  });
  const { createComplaint } = usePostActions({
    // Alterado de createCampaign para createComplaint
    onSuccess: () => {
      onClose?.();
      toast.success("Denúncia criada com sucesso!");
    },
    onError: (error: unknown) => {
      const message =
        typeof error === "object" && error !== null && "message" in error
          ? (error as { message?: string }).message
          : "Erro desconhecido";
      console.error("Erro ao criar denúncia:", message);
      toast.error(
        message === "Network Error"
          ? "Erro de rede. Verifique sua conexão com a internet."
          : message
      );
    },
  });

  const handleNext = async () => {
    if (currentStep === 1) {
      if (!campaignData.title.trim()) {
        alert("Por favor, insira um título para a campanha");
        return;
      }
      setCurrentStep(2);
    } else {
      if (!campaignData.content.trim()) {
        alert("Por favor, insira o conteúdo da publicação");
        return;
      }
      try {
        await createComplaint(campaignData); // Alterado de createCampaign para createComplaint
      } catch {
        // O erro já será tratado pelo hook
      }
    }
  };

  const handleBack = () => {
    console.log("handleBack clicked");
    setCurrentStep(1);
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-[#858585]/80 backdrop-blur-xd z-50">
      <article
        className={`${
          currentStep === 2 ? "w-[926px] h-[673px]" : "max-w-screen-sm w-full"
        } border border-solid shadow-lg bg-zinc-100 border-[color:var(--gray-300,#C6C6C6)] relative z-[51] flex flex-col`}
      >
        <header className="flex overflow-hidden flex-wrap items-start p-4 w-full text-xl leading-relaxed text-neutral-800 max-md:max-w-full">
          <h1 className="text-neutral-800">Criar denúncia</h1>
          <button
            onClick={onClose}
            className="absolute top-2 right-2 text-2xl font-bold text-neutral-800 hover:text-neutral-600"
          >
            &times;
          </button>
        </header>
        <main className="px-4 flex-1 flex flex-col w-full max-md:max-w-full">
          <StepProgress currentStep={currentStep} />
          {currentStep === 1 ? (
            <InputField
              title={campaignData.title}
              onTitleChange={(title) =>
                setCampaignData({ ...campaignData, title })
              }
            />
          ) : (
            <WritePost
              content={campaignData.content}
              files={campaignData.files}
              onContentChange={(content) =>
                setCampaignData({ ...campaignData, content })
              }
              onFilesChange={(files) =>
                setCampaignData({ ...campaignData, files })
              }
            />
          )}
        </main>
        <NavigationButtons
          onBack={handleBack}
          onNext={handleNext}
          currentStep={currentStep}
        />
      </article>
    </div>
  );
};

export default ModalComplaint;
