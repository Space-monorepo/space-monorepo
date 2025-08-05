"use client"

import Sidebar from "@/components/ui/sidebar"

export function SettingsWrapper({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-100 flex">
      <Sidebar />

      <main className="flex-1 p-8 pl-32 transition-all duration-300 ease-in-out">
        <div className="bg-white rounded-lg shadow-sm min-h-[calc(100vh-4rem)] p-6">
          <div className="max-w-3xl mx-auto space-y-8">
            {children}
          </div>
        </div>
      </main>
    </div>
  )
}