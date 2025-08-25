"use client";
import * as React from "react";
import { Incomplete, CircleDash, CheckmarkFilled, FaceSatisfied, TextBold, TextItalic, ListNumbered, ListBulleted } from "@carbon/icons-react";
import { useState, useRef } from "react";
import usePostActions from "@/app/api/src/hooks/post/usePostActions";
import { toast } from "react-toastify";

interface StepIndicatorProps {
  active: boolean;
  completed: boolean;
  stepNumber: number;
  label: string;
}

const StepIndicator: React.FC<StepIndicatorProps> = ({
  active,
  completed,
  stepNumber,
  label,
}) => {
  return (
    <div className="flex relative flex-col gap-2.5 items-start w-full max-md:w-full max-md:max-w-full max-sm:w-full">
      <div className={`relative self-stretch h-0.5 ${active || completed ? 'bg-neutral-800' : 'bg-stone-300'}`} />
      <div className="flex relative gap-2 items-center w-full max-md:w-full max-md:max-w-full max-sm:w-full">
        <div className="relative shrink-0 w-4 h-4 flex items-center justify-center">
          {completed ? (
            <CheckmarkFilled size={16} className="text-black" />
          ) : active ? (
            <Incomplete size={16} className="text-black" />
          ) : (
            <CircleDash size={16} className="text-black" />
          )}
        </div>
        <p className="relative text-xs leading-4 text-black">
          {stepNumber}. {label}
        </p>
      </div>
    </div>
  );
};

const StepProgress: React.FC<{ currentStep: number }> = ({ currentStep }) => {
  return (
    <section className="flex relative items-center w-full self-stretch px-0 py-4 max-sm:p-3">
      <StepIndicator
        active={currentStep === 1}
        completed={currentStep > 1}
        stepNumber={1}
        label="Definir o título"
      />
      <StepIndicator
        active={currentStep === 2}
        completed={false}
        stepNumber={2}
        label="Escrever a denúncia"
      />
    </section>
  );
};


interface ComplaintFormData {
  title: string;
  content: string;
  files: File[];
  community_id: string;
}

const InputField: React.FC<{
  title: string;
  onTitleChange: (value: string) => void;
}> = ({ title, onTitleChange }) => {
  return (
    <section className="flex relative flex-col gap-2 items-start self-stretch">
      <label className="relative self-stretch text-sm leading-6 text-neutral-800">
        Título da denúncia
      </label>
      <div className="flex relative gap-8 items-center self-stretch px-4 py-2 border-b border-solid bg-neutral-200 border-b-neutral-500">
        <input
          type="text"
          value={title}
          onChange={(e) => onTitleChange(e.target.value)}
          placeholder="Escreva o título da denúncia"
          className="relative text-sm leading-6 text-neutral-500 bg-transparent border-none outline-none flex-1 placeholder:text-neutral-500"
          aria-label="Título da denúncia"
        />
      </div>
      <p className="relative text-xs text-neutral-500 w-[496px] max-md:w-full max-md:max-w-[496px] max-sm:w-full">
        Este será o título exibido nas notificações para todos os participantes da denúncia. Certifique-se de escolher uma frase clara e direta.
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
    <>
      {/* Editor de Denúncia */}
      <section className="flex flex-col gap-2 items-start self-stretch">
        <label htmlFor="complaint-text" className="self-stretch text-sm leading-6 text-neutral-800 max-sm:text-sm">
          Descrição da denúncia
        </label>
        <div className="flex flex-col items-start self-stretch">
          <div className="flex flex-col justify-between items-start self-stretch p-4 rounded-sm bg-neutral-200 h-[174px]">
            <textarea
              id="complaint-text"
              value={content}
              onChange={(e) => onContentChange(e.target.value)}
              placeholder="Descreva o motivo da denúncia"
              className="w-full h-full bg-transparent text-sm leading-6 text-neutral-600 max-sm:text-sm resize-none border-none outline-none placeholder:text-neutral-600"
            />
            {/* Barra de formatação */}
            <div className="flex gap-4 items-start max-sm:gap-3">
              <button type="button" aria-label="Adicionar emoji">
                <FaceSatisfied size={20} className="toolbar-icon text-neutral-500" />
              </button>
              <button type="button" aria-label="Negrito">
                <TextBold size={20} className="toolbar-icon text-neutral-500" />
              </button>
              <button type="button" aria-label="Itálico">
                <TextItalic size={20} className="toolbar-icon text-neutral-500" />
              </button>
              <button type="button" aria-label="Lista numerada">
                <ListNumbered size={20} className="toolbar-icon text-neutral-500" />
              </button>
              <button type="button" aria-label="Lista com marcadores">
                <ListBulleted size={20} className="toolbar-icon text-neutral-500" />
              </button>
            </div>
          </div>
          <div className="self-stretch h-px bg-neutral-500" />
        </div>
      </section>

      {/* Upload de Arquivos */}
      <section className="flex flex-col gap-4 items-start self-stretch">
        <div className="flex flex-col gap-2 items-start self-stretch">
          <h3 className="self-stretch text-sm font-semibold leading-6 text-neutral-800 max-sm:text-sm">
            Carregar arquivos
          </h3>
          <p className="text-sm text-neutral-500 w-[497px] max-md:w-full max-sm:w-full max-sm:text-sm">
            Tamanho máximo do arquivo é 2MB. Tipos de arquivos suportados são .jpg e .png.
          </p>
        </div>
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileInput}
          className="hidden"
          multiple
        />
        <div
          className="flex gap-8 items-start self-stretch p-4 h-24 border border-dashed border-neutral-500 cursor-pointer hover:bg-neutral-50 transition-colors"
          onClick={handleFileSelect}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          role="button"
          tabIndex={0}
          aria-label="Upload files"
        >
          <p className="text-sm leading-5 text-neutral-500 w-[230px] max-md:w-full max-sm:w-full max-sm:text-sm">
            Arraste and solte os arquivos aqui ou clique para carregar
          </p>
        </div>
        {files.length > 0 && (
          <div className="mt-4 w-full">
            <h4 className="text-neutral-800 font-medium mb-2 text-sm">
              Arquivos selecionados:
            </h4>
            <ul className="space-y-1">
              {files.map((file, index) => (
                <li
                  key={index}
                  className="flex items-center justify-between bg-neutral-100 p-2 rounded text-sm"
                >
                  <span>{file.name}</span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onFilesChange(files.filter((_, i) => i !== index));
                    }}
                    className="text-red-500 hover:text-red-700 text-xs"
                  >
                    Remover
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}
      </section>
    </>
  );
};

const NavigationButtons: React.FC<{
  onBack: () => void;
  onNext: () => void;
  currentStep: number;
  isLoading?: boolean;
}> = ({ onBack, onNext, currentStep, isLoading }) => {
  return (
    <footer className="flex w-full h-16 text-sm leading-6 whitespace-nowrap mt-auto">
      <button
        onClick={onBack}
        type="button"
        className="w-1/2 h-full flex cursor-pointer items-center justify-start p-4 bg-neutral-200 text-neutral-800 focus:outline-none focus:ring-2 focus:ring-neutral-400 border-r border-neutral-300 disabled:opacity-50"
        aria-label="Voltar para a etapa anterior"
        disabled={currentStep === 1 || isLoading}
      >
        Voltar
      </button>
      <button
        onClick={onNext}
        type="button"
        className="w-1/2 h-full cursor-pointer flex items-center justify-start p-4 bg-neutral-800 text-zinc-100 disabled:bg-neutral-400 focus:outline-none focus:ring-2 focus:ring-zinc-400"
        aria-label="Avançar para a próxima etapa"
        disabled={isLoading}
      >
        {isLoading
          ? "Enviando..."
          : currentStep === 1
            ? "Seguinte"
            : "Concluir"}
      </button>
    </footer>
  );
};


export const ModalComplaint: React.FC<{
  onClose?: () => void;
  communityId: string;
}> = ({ onClose, communityId }) => {
  const [currentStep, setCurrentStep] = useState<number>(1);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [complaintData, setComplaintData] = useState<ComplaintFormData>({
    title: "",
    content: "",
    files: [],
    community_id: communityId,
  });

  const { createComplaint } = usePostActions({
    onSuccess: () => {
      setIsLoading(false);
      onClose?.();
      toast.success("Denúncia criada com sucesso!");
    },
    onError: (error: unknown) => {
      setIsLoading(false);
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
      if (!complaintData.title.trim()) {
        toast.warn("Por favor, insira um título para a denúncia.");
        return;
      }
      setCurrentStep(2);
    } else {
      if (!complaintData.content.trim()) {
        toast.warn("Por favor, insira o conteúdo da denúncia.");
        return;
      }
      setIsLoading(true);
      try {
        await createComplaint(complaintData);
      } catch {
        setIsLoading(false);
      }
    }
  };

  const handleBack = () => {
    if (isLoading) return;
    setCurrentStep(1);
  };

  const handleClose = () => {
    if (isLoading) return;
    onClose?.();
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-[#858585]/80 backdrop-blur-xd z-50">
      <article className={`flex relative flex-col items-start mx-auto my-0 shadow-sm bg-zinc-100 border-stone-300 ${currentStep === 2 ? 'h-[673px] w-[926px]' : 'h-[372px] w-[640px]'} max-md:max-w-screen-sm max-md:w-[90%] max-sm:mx-auto max-sm:my-5 max-sm:h-auto max-sm:w-[95%]`}>
        <header className="flex relative justify-between items-start self-stretch p-4 max-sm:p-3">
          <h1 className="relative text-xl leading-8 text-neutral-800">
            Criar denúncia
          </h1>
          <button
            onClick={handleClose}
            disabled={isLoading}
            className="cursor-pointer disabled:opacity-50"
          >
            <div
              dangerouslySetInnerHTML={{
                __html:
                  '<svg id="621:4115" layer-name="close" data-component-name="close" width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" class="close-icon"> <path d="M5.33317 15.8333L4.1665 14.6666L8.83317 9.99996L4.1665 5.33329L5.33317 4.16663L9.99984 8.83329L14.6665 4.16663L15.8332 5.33329L11.1665 9.99996L15.8332 14.6666L14.6665 15.8333L9.99984 11.1666L5.33317 15.8333Z" fill="#161616"></path> </svg>',
              }}
            />
          </button>
        </header>

        <main className="flex relative flex-col gap-6 items-stretch self-stretch px-4 pt-0 pb-12">
          <StepProgress currentStep={currentStep} />
          {currentStep === 1 ? (
            <InputField
              title={complaintData.title}
              onTitleChange={(title) =>
                setComplaintData({ ...complaintData, title })
              }
            />
          ) : (
            <WritePost
              content={complaintData.content}
              files={complaintData.files}
              onContentChange={(content) =>
                setComplaintData({ ...complaintData, content })
              }
              onFilesChange={(files) =>
                setComplaintData({ ...complaintData, files: files as File[] })
              }
            />
          )}
        </main>

        <NavigationButtons
          onBack={handleBack}
          onNext={handleNext}
          currentStep={currentStep}
          isLoading={isLoading}
        />
      </article>
    </div>
  );
};

export default ModalComplaint;
