"use client"

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

export function AppearanceSection() {
  return (
    <section className="space-y-6 border-b border-gray-200 pb-12">
      <div className="space-y-2">
        <h2 className="text-xl font-semibold text-gray-900">Aparência</h2>
        <p className="text-gray-600">Customize como o Space aparece em seu dispositivo.</p>
      </div>
      
      <div className="flex justify-between items-start pt-4">
        <div className="space-y-2 flex-1 mr-8">
          <label className="text-sm font-medium text-gray-900">Tema</label>
          <p className="text-sm text-gray-500">Escolha o tema que melhor se adequa às suas preferências.</p>
        </div>
        <Select defaultValue="light">
          <SelectTrigger className="w-[200px] bg-white border border-gray-300">
            <SelectValue placeholder="Selecione o tema" />
          </SelectTrigger>
          <SelectContent className="bg-white border border-gray-300">
            <SelectItem value="light" className="hover:bg-gray-100">Claro</SelectItem>
            <SelectItem value="dark" className="hover:bg-gray-100">Escuro</SelectItem>
            <SelectItem value="system" className="hover:bg-gray-100">Sistema</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </section>
  )
}