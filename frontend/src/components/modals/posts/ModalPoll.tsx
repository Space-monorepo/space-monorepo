"use client";
import * as React from "react";

import { useState, useRef } from "react";
import usePostActions from "@/app/api/src/hooks/post/usePostActions";
import { toast } from "react-toastify";
import { Incomplete, CircleDash, CheckmarkFilled, Close } from "@carbon/icons-react";


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
        completed={currentStep > 2}
        stepNumber={2}
        label="Escrever a publicação"
      />
      <StepIndicator
        active={currentStep === 3}
        completed={false}
        stepNumber={3}
        label="Definir opções da enquete"
      />
    </section>
  );
};

interface PollData {
  title: string;
  content: string;
  files: File[];
  status?: string;
  community_id: string;
  pollQuestion: string;
  pollOptions: string[];
}

const InputField: React.FC<{
  title: string;
  onTitleChange: (value: string) => void;
}> = ({ title, onTitleChange }) => {
  return (
    <section className="flex relative flex-col gap-2 items-start self-stretch">
      <label className="relative self-stretch text-sm leading-6 text-neutral-800">
        Título da enquete
      </label>
      <div className="flex relative gap-8 items-center self-stretch px-4 py-2 border-b border-solid bg-neutral-200 border-b-neutral-500">
        <input
          type="text"
          value={title}
          onChange={(e) => onTitleChange(e.target.value)}
          placeholder="Escreva o título da enquete"
          className="relative text-sm leading-6 text-neutral-500 bg-transparent border-none outline-none flex-1 placeholder:text-neutral-500"
          aria-label="Título da enquete"
        />
      </div>
      <p className="relative text-xs text-neutral-500 w-[496px] max-md:w-full max-md:max-w-[496px] max-sm:w-full">
        Este será o título exibido nas notificações para todos os participantes da enquete. Certifique-se de escolher uma frase clara e direta.
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
    <section className="flex relative flex-col gap-2 items-start self-stretch">
      <label className="relative self-stretch text-sm leading-6 text-neutral-800">
        Publicação
      </label>
      <div className="flex relative gap-8 items-start self-stretch px-4 py-2 border-b border-solid bg-neutral-200 border-b-neutral-500">
        <textarea
          value={content}
          onChange={(e) => onContentChange(e.target.value)}
          placeholder="Escreva a publicação"
          className="relative text-sm leading-6 text-neutral-500 bg-transparent border-none outline-none flex-1 h-32 resize-none placeholder:text-neutral-500"
          aria-label="Escreva a publicação"
        />
      </div>
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
        className="mt-4 p-6 border-2 border-dashed border-neutral-300 text-center cursor-pointer hover:bg-neutral-50 transition-colors w-full"
      >
        <p className="text-sm text-neutral-500">Arraste e solte arquivos aqui ou clique para selecionar</p>
        {files.length > 0 && (
          <div className="mt-4">
            <h3 className="text-neutral-800 font-medium mb-2 text-sm">
              Arquivos selecionados:
            </h3>
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
      </div>
    </section>
  );
};

const PollOptions: React.FC<{
  question: string;
  options: string[];
  onQuestionChange: (val: string) => void;
  onOptionsChange: (opts: string[]) => void;
}> = ({ question, options, onQuestionChange, onOptionsChange }) => {
  const updateOption = (index: number, value: string) => {
    const updated = [...options];
    updated[index] = value;
    onOptionsChange(updated);
  };

  const addOption = () => onOptionsChange([...options, ""]);

  const removeOption = (index: number) => {
    const updated = options.filter((_, i) => i !== index);
    onOptionsChange(updated);
  };

  return (
    <section className="mt-2 w-full text-sm text-neutral-500">
      <label className="block text-neutral-800">Pergunta da enquete</label>
      <input
        type="text"
        value={question}
        onChange={(e) => onQuestionChange(e.target.value)}
        placeholder="Escreva a pergunta da enquete"
        className="w-full px-4 py-2 mt-2 bg-neutral-200 text-neutral-700 border-b"
      />
      <label className="block mt-4 text-neutral-800">Opções</label>
      {options.map((opt, i) => (
        <div key={i} className="flex items-center mt-2 gap-2">
          <input
            type="text"
            value={opt}
            onChange={(e) => updateOption(i, e.target.value)}
            placeholder={`Opção ${i + 1}`}
            className="w-full px-4 py-2 bg-neutral-200 text-neutral-700"
          />
          {/* Só mostra o botão Remover se não for as duas primeiras opções */}
          {i > 1 && (
            <button className="text-red-500" onClick={() => removeOption(i)}>
              Remover
            </button>
          )}
        </div>
      ))}
      <div
        className="mt-2 flex items-center px-3 py-2 border-2 border-dashed border-neutral-300 text-neutral-500 cursor-pointer hover:bg-neutral-50 transition-colors w-full"
        style={{ minHeight: '48px' }}
        onClick={addOption}
      >
        <span className="text-xl mr-2 select-none">+</span>
        <span className="text-sm select-none">Adicionar outra opção</span>
      </div>
    </section>
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
          : currentStep < 3
            ? "Seguinte"
            : "Concluir"}
      </button>
    </footer>
  );
};

interface ModalPollProps {
  onClose: () => void;
  communityId: string;
}

// Adicionar a prop onClose à interface

export function ModalPoll({ onClose, communityId }: ModalPollProps) {
  const [status] = useState<string>("active");
  const [currentStep, setCurrentStep] = useState<number>(1);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [pollData, setPollData] = useState<PollData>({
    community_id: communityId,
    title: "",
    content: "",
    files: [],
    status: status,
    pollQuestion: "",
    pollOptions: ["", ""],
  });
  const { createPoll } = usePostActions({
    onSuccess: () => {
      setIsLoading(false);
      onClose?.();
      toast.success("Enquete criada com sucesso!");
    },
    onError: (error: unknown) => {
      setIsLoading(false);
      const message =
        typeof error === "object" && error !== null && "message" in error
          ? (error as { message?: string }).message
          : "Erro desconhecido";
      console.error("Erro ao criar enquete:", message);
      toast.error(
        message === "Network Error"
          ? "Erro de rede. Verifique sua conexão com a internet."
          : message
      );
    },
  });

  const handleNext = async () => {
    if (currentStep === 1) {
      if (!pollData.title.trim()) {
        toast.warn("Por favor, insira um título para a enquete.");
        return;
      }
      setCurrentStep(2);
    } else if (currentStep === 2) {
      if (!pollData.content.trim()) {
        toast.warn("Por favor, insira o conteúdo da publicação.");
        return;
      }
      setCurrentStep(3);
    } else {
      if (!pollData.pollQuestion.trim()) {
        toast.warn("Por favor, insira a pergunta da enquete.");
        return;
      }
      if (pollData.pollOptions.some((opt) => !opt.trim())) {
        toast.warn("Por favor, preencha todas as opções da enquete.");
        return;
      }
      setIsLoading(true);
      try {
        await createPoll({
          ...pollData,
          options: pollData.pollOptions,
          endDate: "",
        });
      } catch {
        setIsLoading(false);
      }
    }
  };

  const handleBack = () => {
    if (isLoading) return;
    setCurrentStep((prev) => (prev > 1 ? prev - 1 : 1));
  };

  const handleClose = () => {
    if (isLoading) return;
    onClose?.();
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-[#858585]/80 backdrop-blur-xd z-50">
      <article className={`flex relative flex-col items-start mx-auto my-0 shadow-sm bg-zinc-100 border-stone-300 
        ${currentStep === 1 ? 'min-w-[640px] min-h-[372px]' : ''}
        ${currentStep === 2 ? 'min-w-[926px] min-h-[673px]' : ''}
        ${currentStep === 3 ? 'min-w-[640px] min-h-[524px]' : ''}
        max-md:max-w-screen-sm max-md:w-[90%] max-sm:mx-auto max-sm:my-5 max-sm:h-auto max-sm:w-[95%]`}>
        <header className="flex relative justify-between items-start self-stretch p-4 max-sm:p-3">
          <h1 className="relative text-xl leading-8 text-neutral-800">
            Criar enquete
          </h1>
          <button
            onClick={handleClose}
            disabled={isLoading}
            className="cursor-pointer disabled:opacity-50"
            aria-label="Fechar modal"
          >
            <Close size={20} className="text-neutral-800" />
          </button>
        </header>

        <main className="flex relative flex-col gap-6 items-stretch self-stretch px-4 pt-0 pb-12">
          <StepProgress currentStep={currentStep} />
          {currentStep === 1 ? (
            <InputField
              title={pollData.title}
              onTitleChange={(title) => setPollData({ ...pollData, title })}
            />
          ) : currentStep === 2 ? (
            <WritePost
              content={pollData.content}
              files={pollData.files}
              onContentChange={(content) =>
                setPollData({ ...pollData, content })
              }
              onFilesChange={(files) => setPollData({ ...pollData, files })}
            />
          ) : (
            <PollOptions
              question={pollData.pollQuestion}
              options={pollData.pollOptions}
              onQuestionChange={(pollQuestion) =>
                setPollData({ ...pollData, pollQuestion })
              }
              onOptionsChange={(pollOptions) =>
                setPollData({ ...pollData, pollOptions })
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
}

export default ModalPoll;
