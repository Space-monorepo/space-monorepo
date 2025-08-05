"use client";

import { useState } from "react";
import { X } from "lucide-react";
import {
  Community,
  UpdateCommunity,
} from "@/app/api/src/types/community/Community";

interface EditCommunityModalProps {
  community: Community;
  isOpen: boolean;
  onClose: () => void;
  onSave: (
    communityId: string,
    updateData: Partial<UpdateCommunity>
  ) => Promise<void>;
  isLoading?: boolean;
}

const communityTypes = [
  { value: "university", label: "Universidade" },
  { value: "neighborhood", label: "Bairro" },
  { value: "company", label: "Empresa" },
  { value: "government", label: "Governo" },
  { value: "healthcare", label: "Saúde" },
  { value: "religious", label: "Religioso" },
  { value: "commercial", label: "Comercial" },
  { value: "club", label: "Clube" },
];

export default function EditCommunityModal({
  community,
  isOpen,
  onClose,
  onSave,
  isLoading = false,
}: EditCommunityModalProps) {
  const [formData, setFormData] = useState({
    name: community.name,
    description: community.description || "",
    type_community: community.type_community,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = "Nome é obrigatório";
    }

    if (!formData.type_community) {
      newErrors.type_community = "Tipo da comunidade é obrigatório";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    try {
      await onSave(community.id, {
        name: formData.name.trim(),
        description: formData.description.trim(),
        type_community: formData.type_community,
      });
      onClose();
    } catch (error) {
      console.error("Erro ao salvar comunidade:", error);
    }
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Limpar erro do campo quando o usuário começar a digitar
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: "" }));
    }
  };
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-white/20 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-white p-6 w-full max-w-md mx-4 shadow-2xl">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-medium">Editar Comunidade</h2>
          <button
            onClick={onClose}
            className="p-1 text-[#525252] hover:text-[#161616]"
            disabled={isLoading}
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Nome da Comunidade */}
          <div>
            <label
              htmlFor="name"
              className="block text-sm font-medium text-[#161616] mb-1"
            >
              Nome da Comunidade *
            </label>
            <input
              id="name"
              type="text"
              value={formData.name}
              onChange={(e) => handleInputChange("name", e.target.value)}
              className={`w-full px-3 py-2 border focus:outline-none focus:border-[#0f62fe] ${
                errors.name ? "border-red-500" : "border-[#e0e0e0]"
              }`}
              placeholder="Digite o nome da comunidade"
              disabled={isLoading}
            />
            {errors.name && (
              <p className="text-red-500 text-xs mt-1">{errors.name}</p>
            )}
          </div>

          {/* Tipo da Comunidade */}
          <div>
            <label
              htmlFor="type_community"
              className="block text-sm font-medium text-[#161616] mb-1"
            >
              Tipo da Comunidade *
            </label>
            <select
              id="type_community"
              value={formData.type_community}
              onChange={(e) =>
                handleInputChange("type_community", e.target.value)
              }
              className={`w-full px-3 py-2 border focus:outline-none focus:border-[#0f62fe] ${
                errors.type_community ? "border-red-500" : "border-[#e0e0e0]"
              }`}
              disabled={isLoading}
            >
              <option value="">Selecione um tipo</option>
              {communityTypes.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
            {errors.type_community && (
              <p className="text-red-500 text-xs mt-1">
                {errors.type_community}
              </p>
            )}
          </div>

          {/* Descrição */}
          <div>
            <label
              htmlFor="description"
              className="block text-sm font-medium text-[#161616] mb-1"
            >
              Descrição
            </label>
            <textarea
              id="description"
              value={formData.description}
              onChange={(e) => handleInputChange("description", e.target.value)}
              rows={4}
              className="w-full px-3 py-2 border border-[#e0e0e0] focus:outline-none focus:border-[#0f62fe] resize-none"
              placeholder="Digite uma descrição para a comunidade"
              disabled={isLoading}
            />
          </div>

          {/* Botões */}
          <div className="flex justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-[#525252] border border-[#e0e0e0] hover:bg-[#f8f8f8] disabled:opacity-50"
              disabled={isLoading}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-black text-white hover:bg-gray-900 disabled:opacity-50"
              disabled={isLoading}
            >
              {isLoading ? "Salvando..." : "Salvar"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
