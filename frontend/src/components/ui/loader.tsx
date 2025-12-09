import { Loader2 } from "lucide-react";

export const Loader = () => {
  return (
      <div className="flex flex-col items-center justify-center min-h-screen text-center px-4">
      <Loader2 className="h-10 w-10 animate-spin text-blue-600 mb-4" />
      <h1 className="text-xl font-semibold text-gray-800">Carregando...</h1>
      <p className="text-gray-500 mt-2">Você será redirecionado em instantes.</p>
    </div>
  );
};
