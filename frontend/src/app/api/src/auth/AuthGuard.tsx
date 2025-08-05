import { ReactNode } from "react";
import { useAuth } from "./useAuth";
import { Loader } from "@/components/ui/loader";

export const AuthGuard = ({ children }: { children: ReactNode }) => {
  const { user, loading } = useAuth();

  if (loading) return <Loader/>;
  if (!user) return null;

  return <>{children}</>;
};