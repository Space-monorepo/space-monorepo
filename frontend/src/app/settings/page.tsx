"use client"

import { AppearanceSection } from "./components/AppearanceSection"
import { LanguageAndTimeSection } from "./components/LanguageAndTimeSection"
import { NotificationsSection } from "./components/NotificationsSection"
import { SettingsWrapper } from "./components/SettingsWrapper"
import { useCheckTokenValidity } from "@/app/api/src/controllers/authCheckToken"

export default function ConfiguracoesPage() {

  useCheckTokenValidity();
  return (
    <SettingsWrapper>
      <div className="space-y-12">
        <div className="space-y-2">
          <h1 className="text-3xl font-bold text-gray-900">Preferências</h1>
          <p className="text-gray-600">Gerencie suas configurações e preferências da plataforma.</p>
        </div>
        
        <div className="space-y-12">
          <AppearanceSection />
          <LanguageAndTimeSection />
          <NotificationsSection />
        </div>
      </div>
    </SettingsWrapper>
  )
}