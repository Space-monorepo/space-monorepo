"use client"

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

export function AppearanceSection() {
  return (
    <section className="space-y-4 border-b pb-6">
      <h2 className="text-lg font-semibold">Aparência</h2>
      <p className="text-sm text-gray-500">Customize como o Space aparece em seu dispositivo.</p>
      <div className="flex justify-between items-center">
        <div className="space-y-1">
          <label className="text-sm font-medium">Tema</label>
        </div>
        <Select defaultValue="light">
          <SelectTrigger className="w-[180px] bg-white border border-gray-300">
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