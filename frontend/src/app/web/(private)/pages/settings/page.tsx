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
      <h1 className="text-2xl font-bold">Preferências</h1>
      <AppearanceSection />
      <LanguageAndTimeSection />
      <NotificationsSection />
    </SettingsWrapper>
  )
}