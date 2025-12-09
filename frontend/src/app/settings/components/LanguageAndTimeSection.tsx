"use client"

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

export function LanguageAndTimeSection() {
  return (
    <section className="space-y-8 border-b border-gray-200 pb-12">
      <div className="space-y-2">
        <h2 className="text-xl font-semibold text-gray-900">Linguagem e Hora</h2>
        <p className="text-gray-600">Configure idioma e fuso horário para sua experiência personalizada.</p>
      </div>

      <div className="space-y-8">
        <div className="flex justify-between items-start">
          <div className="space-y-2 flex-1 mr-8">
            <label className="text-sm font-medium text-gray-900">Linguagem</label>
            <p className="text-sm text-gray-500">Altere a linguagem utilizada na interface do usuário.</p>
          </div>
          <Select defaultValue="pt-BR">
            <SelectTrigger className="w-[200px] bg-white border border-gray-300">
              <SelectValue placeholder="Selecione o idioma" />
            </SelectTrigger>
            <SelectContent className="bg-white border border-gray-300">
              <SelectItem value="pt-BR" className="hover:bg-gray-100">Português - Brasil</SelectItem>
              <SelectItem value="en-US" className="hover:bg-gray-100">English - US</SelectItem>
              <SelectItem value="es" className="hover:bg-gray-100">Español</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="flex justify-between items-start">
          <div className="space-y-2 flex-1 mr-8">
            <label className="text-sm font-medium text-gray-900">Fuso horário</label>
            <p className="text-sm text-gray-500">Configuração atual de fuso horário para exibição de datas e horários.</p>
          </div>
          <Select defaultValue="SP">
            <SelectTrigger className="w-[200px] bg-white border border-gray-300">
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