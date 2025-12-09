"use client"

import { Switch } from "@/components/ui/switch"

export function NotificationsSection() {
  return (
    <section className="space-y-8">
      <div className="space-y-2">
        <h2 className="text-xl font-semibold text-gray-900">Notificações</h2>
        <p className="text-gray-600">Gerencie como e quando você recebe notificações da plataforma.</p>
      </div>

      <div className="space-y-8">
        <div className="flex items-start justify-between">
          <div className="space-y-2 flex-1 mr-8">
            <label className="text-sm font-medium text-gray-900">Notificações por email</label>
            <p className="text-sm text-gray-500">Ative para receber notificações importantes por email sobre atividades da sua conta.</p>
          </div>
          <Switch className="data-[state=checked]:bg-black mt-1" />
        </div>
      </div>
    </section>
  )
}