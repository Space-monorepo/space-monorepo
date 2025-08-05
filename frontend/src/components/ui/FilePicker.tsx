"use client";

import { useRef, useState } from "react";
import { Upload, Loader2 } from "lucide-react";
import axios from "axios";
import getTokenFromCookies from "@/app/api/src/controllers/getTokenFromCookies";
import { cloudinary_link, API_URL } from "@/config";

const uploadToCloudinary = async (file: File): Promise<string | null> => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append(
    "upload_preset",
    process.env.NEXT_PUBLIC_CLOUDINARY_UPLOAD_PRESET || ""
  );

  const cloudName = process.env.NEXT_PUBLIC_CLOUDINARY_CLOUD_NAME;
  if (!cloudName) {
    console.error("Cloudinary Cloud Name não está configurado.");
    return null;
  }

  try {
    const response = await fetch(`${cloudinary_link}`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) throw new Error("Erro ao enviar para o Cloudinary");

    const data = await response.json();
    return data.secure_url;
  } catch (error) {
    console.error("Erro no upload para Cloudinary:", error);
    return null;
  }
};

interface FilePickerProps {
  currentImageUrl?: string;
  onImageChange: (newImageUrl: string) => void;
  isOwnProfile: boolean;
}

const FilePicker = ({
  currentImageUrl,
  onImageChange,
  isOwnProfile,
}: FilePickerProps) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [loading, setLoading] = useState(false);

  // Debug para verificar o isOwnProfile
  console.log("FilePicker - isOwnProfile:", isOwnProfile);
  console.log("FilePicker - currentImageUrl:", currentImageUrl);

  const triggerFileInput = () => {
    if (isOwnProfile && fileInputRef.current && !loading) {
      fileInputRef.current.value = "";
      fileInputRef.current.click();
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading(true);

    try {
      const imageUrl = await uploadToCloudinary(file);
      if (!imageUrl) throw new Error("Erro ao obter URL da imagem");

      const token = getTokenFromCookies();
      if (!token) throw new Error("Token não encontrado");

      const response = await axios.patch(
        `${API_URL}/users/me`,
        { profile_image_url: imageUrl },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      if (response.data.profile_image_url) {
        onImageChange(response.data.profile_image_url);
      }
    } catch (error) {
      console.error("Erro no processo de upload:", error);
    } finally {
      setLoading(false);
    }
  };
  return (
    <div className="relative group h-full">
      <div
        onClick={triggerFileInput}
        className={`w-full h-full bg-gray-100 overflow-hidden rounded-lg
          ${
            isOwnProfile ? "cursor-pointer hover:bg-gray-200" : "cursor-default"
          }
          relative flex items-center justify-center transition`}
      >
        {currentImageUrl ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={currentImageUrl}
            alt="Foto de perfil"
            className="absolute inset-0 w-full h-full object-cover rounded-lg"
          />
        ) : (
          <div className="text-gray-400 text-center p-4">
            {isOwnProfile ? "Clique para adicionar foto" : "Sem foto de perfil"}
          </div>
        )}{" "}
        {/* Overlay de animação - apenas para próprio perfil */}
        {isOwnProfile && !loading && (
          <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-black bg-opacity-30 rounded-lg">
            <Upload className="text-white w-8 h-8" />
          </div>
        )}
        {/* Overlay de loading separado */}
        {isOwnProfile && loading && (
          <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-40 rounded-lg">
            <Loader2 className="animate-spin text-white w-8 h-8" />
          </div>
        )}
      </div>

      {/* Input de arquivo oculto - apenas para próprio perfil */}
      {isOwnProfile && (
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept="image/*"
          className="absolute opacity-0 w-full h-full top-0 left-0 cursor-pointer"
          tabIndex={-1}
        />
      )}
    </div>
  );
};

export default FilePicker;
