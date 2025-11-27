"use client";

import { useState } from "react";
import { Attachment, FaceActivated, TextBold, TextItalic, Close } from "@carbon/icons-react";
import { toast } from "react-toastify";

interface User {
  username: string;
  name: string;
  email: string;
  created_at: string;
  bio?: string;
  reputation_level?: string;
  popularity?: number;
  profile_image_url?: string;
}

interface EditProfileModalProps {
  isOpen: boolean;
  onClose: () => void;
  user: User;
  onSave: (name: string, bio: string) => void;
}

export default function EditProfileModal({
  isOpen,
  onClose,
  user,
  onSave,
}: EditProfileModalProps) {
  const [name, setName] = useState(user.name);
  const [bio, setBio] = useState(user.bio || "");
  const [isLoading, setIsLoading] = useState(false); const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validação básica
    if (!name.trim()) {
      toast.error("O nome é obrigatório");
      return;
    }

    if (name.trim().length < 2) {
      toast.error("O nome deve ter pelo menos 2 caracteres");
      return;
    }

    setIsLoading(true);

    try {
      await onSave(name.trim(), bio.trim());
      toast.success("Perfil atualizado com sucesso!");
      onClose();
    } catch (error) {
      console.error("Erro ao salvar perfil:", error);
      const errorMessage = error instanceof Error ? error.message : "Erro ao atualizar perfil. Tente novamente.";
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="border-solid shadow-sm bg-zinc-100 border-stone-300 max-w-[926px] w-full">
        <header className="flex flex-wrap gap-10 justify-between items-start p-4 w-full text-xl leading-relaxed text-neutral-800 max-md:max-w-full">
          <h2 className="text-neutral-800">Editar Perfil</h2>
          <button
            onClick={onClose}
            className="shrink-0 w-5 aspect-square hover:opacity-70 transition-opacity"
            aria-label="Fechar"
            disabled={isLoading}
          >
            <Close className="w-full h-full text-neutral-800" />
          </button>
        </header>

        <div className="flex flex-col justify-center px-4 pb-12 w-full max-md:max-w-full">
          <section className="w-full text-sm text-neutral-800 max-md:max-w-full mb-4">
            <p className="text-neutral-800 mb-2">Você está editando seu perfil. As informações atualizadas ficarão visíveis no seu perfil público.</p>
            <p className="text-neutral-600 text-sm">Atualize o Nome e Biografia abaixo.</p>
          </section>

          <form onSubmit={handleSubmit} className="w-full max-w-full space-y-4">
            <div className="flex flex-col">
              <label htmlFor="name" className="block text-sm font-medium text-neutral-700 mb-1">Nome</label>
              <div className="mt-2 w-full text-neutral-500">
                <div className="flex gap-8 items-center px-4 py-2 w-full bg-neutral-200">
                  <input type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="Escreva o Nome" className="flex-1 bg-transparent text-neutral-500 outline-none placeholder-neutral-500" />
                </div>
              </div>
            </div>

            <div className="mt-8 w-full text-sm leading-6 max-md:max-w-full">
              <label className="text-sm font-medium text-neutral-700 mb-1">Biografia</label>
              <div className="mt-4 w-full">
                <div className="flex flex-col justify-between p-4 w-full rounded-sm bg-neutral-200 min-h-[236px]">
                  <textarea value={bio} onChange={(e) => setBio(e.target.value)} placeholder="Conte um pouco sobre você..." className="flex-1 bg-transparent text-sm leading-6 text-neutral-600 outline-none resize-none" rows={8} />
                  <div className="flex gap-4 items-start self-start mt-4">
                    <button className="w-5 h-5" aria-label="Anexar arquivo">
                      <Attachment className="w-full h-full" />
                    </button>
                    <button className="w-5 h-5" aria-label="Emoji">
                      <FaceActivated className="w-full h-full" />
                    </button>
                    <button className="w-5 h-5" aria-label="Negrito">
                      <TextBold className="w-full h-full" />
                    </button>
                    <button className="w-5 h-5" aria-label="Itálico">
                      <TextItalic className="w-full h-full" />
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <footer className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 px-4 py-2 text-sm cursor-pointer text-neutral-800 bg-neutral-200 hover:bg-neutral-300 rounded-md transition-colors"
                disabled={isLoading}
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="flex-1 px-4 py-2 cursor-pointer bg-neutral-800 text-white hover:bg-neutral-700 rounded-md transition-colors"
                disabled={isLoading}
              >
                Salvar
              </button>
            </footer>
          </form>
        </div>
      </div>
    </div>
  );
}
