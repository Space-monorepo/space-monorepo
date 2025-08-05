import { ReactNode } from "react";
import { AuthProvider } from "@/app/api/src/auth/AuthContext";

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <AuthProvider>
      {children}
    </AuthProvider>
  );
}