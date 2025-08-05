import { Search } from "lucide-react"
import { useState } from "react"
import ModalResponsibility from "@/components/modals/responsabilty/ModalResponsabilty"

export default function Header() {
  const [isModalOpen, setIsModalOpen] = useState(false)

  const handleOpenModal = () => {
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
  }

  return (
    <header className="flex items-center font-manrope justify-between p-4 bg-gray-100 border-b border-[#e0e0e0] h-16 fixed top-0 left-[16rem] right-0 z-10">
      <div className="w-full max-w-xl ml-86">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[#525252] h-4 w-4" />
          <input
            type="text"
            placeholder="Pesquisar"
            className="w-[675px] pl-10 pr-4 py-2 border border-[#e0e0e0] focus:outline-none focus:border-[#0f62fe]"
          />
        </div>
      </div>
      <button
        onClick={handleOpenModal}
        className="flex items-center gap-2 px-4 py-2 bg-gray-900 text-white hover:bg-black text-[14px] m-30 cursor-pointer transition-colors"
      >
        Criar publicação
      </button>
      {isModalOpen && <ModalResponsibility onClose={handleCloseModal} />}
    </header>
  )
}
