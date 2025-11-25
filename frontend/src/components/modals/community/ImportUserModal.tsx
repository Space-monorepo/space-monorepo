"use client";
import * as React from "react";
import { toast } from "react-toastify";

interface ImportUserModalProps {
    isOpen: boolean;
    onClose: () => void;
    onImport: () => void;
    loading: boolean;
    emailValue: string;
    onEmailChange: (value: string) => void;
}

const ImportUserModal: React.FC<ImportUserModalProps> = ({
    isOpen,
    onClose,
    onImport,
    loading,
    emailValue,
    onEmailChange,
}) => {
    if (!isOpen) return null;

    const handleEmailSubmit = () => {
        if (!emailValue.trim()) {
            toast.error("Por favor, digite um email válido");
            return;
        }
        onImport();
    };

    const handleClose = () => {
        if (loading) return;
        onClose();
    };

    return (
        <div className="fixed inset-0 flex items-center justify-center bg-[#858585]/80 backdrop-blur-sm z-50">
            <article className="flex relative flex-col items-start shadow-sm bg-zinc-100 border-stone-300 h-[320px] min-w-[640px] max-md:max-w-screen-sm max-md:w-[90%] max-sm:mx-auto max-sm:my-5 max-sm:h-auto max-sm:w-[95%]">
                <header className="flex relative justify-between items-start self-stretch p-4 max-sm:p-3">
                    <h1 className="relative text-xl leading-8 text-neutral-800">
                        Adicionar usuário
                    </h1>
                    <button
                        onClick={handleClose}
                        disabled={loading}
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

                <main className="flex relative flex-col gap-6 items-stretch self-stretch px-4 pt-0 pb-4 flex-grow">
                    <section className="flex relative flex-col gap-2 items-start self-stretch">
                        <label className="relative self-stretch text-sm leading-6 text-neutral-800">
                            E-mail do usuário
                        </label>
                        <div className="flex relative gap-8 items-center self-stretch px-4 py-2 border-b border-solid bg-neutral-200 border-b-neutral-500">
                            <input
                                type="email"
                                value={emailValue}
                                onChange={(e) => onEmailChange(e.target.value)}
                                placeholder="Digite o e-mail do usuário"
                                className="relative text-sm leading-6 text-neutral-500 bg-transparent border-none outline-none flex-1 placeholder:text-neutral-500"
                                aria-label="E-mail do usuário"
                                disabled={loading}
                            />
                        </div>
                        <p className="relative text-xs text-neutral-500 min-w-[496px] max-md:w-full max-md:max-w-[496px] max-sm:w-full">
                            Informe o e-mail do usuário que deseja adicionar à comunidade. O usuário receberá uma notificação sobre o convite.
                        </p>
                    </section>
                </main>

                <footer className="flex w-full h-16 text-sm leading-6 whitespace-nowrap">
                    <button
                        onClick={handleClose}
                        type="button"
                        className="w-1/2 h-full flex cursor-pointer items-center justify-start p-4 bg-neutral-200 text-neutral-800 focus:outline-none focus:ring-2 focus:ring-neutral-400 border-r border-neutral-300 disabled:opacity-50"
                        aria-label="Cancelar"
                        disabled={loading}
                    >
                        Cancelar
                    </button>
                    <button
                        onClick={handleEmailSubmit}
                        type="button"
                        className="w-1/2 h-full cursor-pointer flex items-center justify-start p-4 bg-neutral-800 text-zinc-100 disabled:bg-neutral-400 focus:outline-none focus:ring-2 focus:ring-zinc-400"
                        aria-label="Adicionar usuário"
                        disabled={loading}
                    >
                        {loading ? "Adicionando..." : "Adicionar"}
                    </button>
                </footer>
            </article>
        </div>
    );
};

export default ImportUserModal;
