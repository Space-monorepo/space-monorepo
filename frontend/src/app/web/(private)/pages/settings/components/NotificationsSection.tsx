"use client"

import { Switch } from "@/components/ui/switch"

export function NotificationsSection() {
  return (
    <section className="space-y-6">
      <h2 className="text-lg font-semibold">Notificações</h2>

      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <label className="text-sm font-medium">Notificações em dispositivos móveis</label>
            <p className="text-sm text-gray-500">Ative para receber notificações no seu dispositivo móvel</p>
          </div>
          <Switch className="data-[state=checked]:bg-black" />
        </div>

        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <label className="text-sm font-medium">Notificações por email</label>
            <p className="text-sm text-gray-500">Ative para receber notificações por email.</p>
          </div>
          <Switch className="data-[state=checked]:bg-black" />
        </div>
      </div>
    </section>
  )
}