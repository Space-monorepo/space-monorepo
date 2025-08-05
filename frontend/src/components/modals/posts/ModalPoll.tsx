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
      <StepIndicator
        active={currentStep === 3}
        icon="https://cdn.builder.io/api/v1/image/assets/TEMP/placeholder-icon-poll-options?apiKey=c82d577402ec4a68b3d9eb6968f38275" // Placeholder icon, replace with actual
        label="Definir opções da enquete"
      />
    </nav>
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
    <section className="mt-6 w-full text-sm leading-6 text-neutral-500 max-md:max-w-full">
      <label className="block text-neutral-800 max-md:max-w-full">
        Título da enquete
      </label>
      <input
        type="text"
        value={title}
        onChange={(e) => onTitleChange(e.target.value)}
        placeholder="Escreva o título da enquete"
        className="gap-8 self-stretch px-4 py-2 mt-2 w-full bg-neutral-200 text-neutral-500 max-md:max-w-full"
        aria-label="Título da campanha"
      />
      <p className="mt-2 text-xs text-neutral-500 max-md:max-w-full">
        Este será o título exibido nas notificações para todos os participantes
        da enquete. Certifique-se de escolher uma frase clara e direta.
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
      <label className="block text-neutral-800">Conteúdo do enquete</label>
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
    <section className="mt-6 w-full text-sm text-neutral-500">
      <label className="block text-neutral-800">Pergunta da enquete</label>
      <input
        type="text"
        value={question}
        onChange={(e) => onQuestionChange(e.target.value)}
        placeholder="Qual sua pergunta?"
        className="w-full px-4 py-2 mt-2 bg-neutral-200 text-neutral-700"
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
          <button className="text-red-500" onClick={() => removeOption(i)}>
            Remover
          </button>
        </div>
      ))}
      <button
        className="mt-4 px-4 py-2 bg-neutral-800 text-white rounded hover:bg-neutral-900"
        onClick={addOption}
      >
        Adicionar opção
      </button>
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
        {currentStep === 3 ? "Concluir" : "Seguinte"}
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
  const [pollData, setPollData] = useState<PollData>({
    community_id: communityId,
    title: "",
    content: "",
    files: [],
    status: status,
    pollQuestion: "",
    pollOptions: ["", ""], // Initial two options for the poll
  });
  const { createPoll } = usePostActions({
    onSuccess: () => {
      onClose?.();
      toast.success("Enquete criada com sucesso!");
    },
    onError: (error: unknown) => {
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
        alert("Por favor, insira um título para a enquete");
        return;
      }
      setCurrentStep(2);
    } else if (currentStep === 2) {
      if (!pollData.content.trim()) {
        alert("Por favor, insira o conteúdo da publicação");
        return;
      }
      setCurrentStep(3);
    } else {
      if (!pollData.pollQuestion.trim()) {
        alert("Por favor, insira a pergunta da enquete");
        return;
      }
      if (pollData.pollOptions.some((opt) => !opt.trim())) {
        alert("Por favor, preencha todas as opções da enquete");
        return;
      }
      try {
        await createPoll({
          ...pollData, // Contém title, content, files, community_id, pollQuestion, pollOptions
          // pollQuestion já está em pollData, não precisa ser passado separadamente se estiver lá
          options: pollData.pollOptions, // Passar as opções como string[]
          endDate: "", // Defina um valor apropriado se necessário
        });
      } catch {
        // O erro já será tratado pelo hook
      }
    }
  };

  const handleBack = () => {
    console.log("handleBack clicked");
    setCurrentStep((prev) => (prev > 1 ? prev - 1 : 1));
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-[#858585]/80 backdrop-blur-xd z-50">
      <article
        className={`${
          currentStep === 2 ? "w-[926px] h-[673px]" : "max-w-screen-sm w-full"
        } border border-solid shadow-lg bg-zinc-100 border-[color:var(--gray-300,#C6C6C6)] relative z-[51] flex flex-col`}
      >
        <header className="flex overflow-hidden flex-wrap items-start p-4 w-full text-xl leading-relaxed text-neutral-800 max-md:max-w-full">
          <h1 className="text-neutral-800">Criar enquete</h1>
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
        />
      </article>
    </div>
  );
}

export default ModalPoll;
