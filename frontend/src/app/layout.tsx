import type React from "react";
import type { Metadata } from "next";
import "./globals.css";
import { ToastContainer } from "react-toastify";
import { Manrope } from "next/font/google";

const manrope = Manrope({
  subsets: ["latin"],
  weight: ["200", "300", "400", "500","600", "700", "800"],
  variable: "--font-manrope",
  display: "auto",
});

export const metadata: Metadata = {
  title: "Space",
  description: "Sua plataforma social",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR" className={manrope.variable}>
      <body className="font-manrope">
        {children}
        <ToastContainer
          position="top-right"
          autoClose={3000}
          hideProgressBar={false}
          newestOnTop={false}
          closeOnClick
          rtl={false}
          pauseOnFocusLoss
          draggable
          pauseOnHover
        />
      </body>
    </html>
  );
}
