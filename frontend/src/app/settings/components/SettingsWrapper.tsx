"use client";

import Sidebar from "@/components/ui/sidebar";

export function SettingsWrapper({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-100 flex overflow-hidden">
      <Sidebar variant="static" />{" "}
      <main 
        className="flex-1 pl-0 min-[900px]:pl-64 transition-all duration-300 ease-in-out h-screen overflow-y-scroll" 
        style={{
          scrollbarWidth: 'none',
          msOverflowStyle: 'none'
        }}>
        <div className="bg-white shadow-sm p-12 py-16 w-full min-h-full">
          {children}
        </div>
      </main>
    </div>
  );
}
