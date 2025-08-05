"use client"

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

export function LanguageAndTimeSection() {
  return (
    <section className="space-y-6 border-b pb-6">
      <h2 className="text-lg font-semibold">Linguagem e Hora</h2>

      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div className="space-y-1">
            <label className="text-sm font-medium">Linguagem</label>
            <p className="text-sm text-gray-500">Altere a linguagem utilizada na interface do usuário.</p>
          </div>
          <Select defaultValue="pt-BR">
            <SelectTrigger className="w-[180px] bg-white border border-gray-300">
              <SelectValue placeholder="Selecione o idioma" />
            </SelectTrigger>
            <SelectContent className="bg-white border border-gray-300">
              <SelectItem value="pt-BR" className="hover:bg-gray-100">Português - Brasil</SelectItem>
              <SelectItem value="en-US" className="hover:bg-gray-100">English - US</SelectItem>
              <SelectItem value="es" className="hover:bg-gray-100">Español</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="flex justify-between items-center">
          <div className="space-y-1">
            <label className="text-sm font-medium">Fuso horário</label>
            <p className="text-sm text-gray-500">Configuração atual de fuso horário.</p>
          </div>
          <Select defaultValue="SP">
            <SelectTrigger className="w-[180px] bg-white border border-gray-300">
              <SelectValue placeholder="Selecione o fuso" />
            </SelectTrigger>
            <SelectContent className="bg-white border border-gray-300">
              <SelectItem value="SP" className="hover:bg-gray-100">(GMT - 3:00) - São Paulo</SelectItem>
              <SelectItem value="NY" className="hover:bg-gray-100">(GMT - 4:00) - New York</SelectItem>
              <SelectItem value="LDN" className="hover:bg-gray-100">(GMT + 0:00) - London</SelectItem>
              <SelectItem value="TKY" className="hover:bg-gray-100">(GMT + 9:00) - Tokyo</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
    </section>
  )
}