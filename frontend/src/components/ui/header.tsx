
import { useState } from "react"
import ModalResponsibility from "@/components/modals/responsabilty/ModalResponsabilty"
import { SearchBar } from "@/components/ui/search-bar"

export default function Header() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [searchValue, setSearchValue] = useState("")

  const handleOpenModal = () => {
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
  }

  return (
    <header className="flex items-center font-manrope justify-between p-4 bg-gray-100 border-b border-[#e0e0e0] h-16 fixed top-0 left-[16rem] right-0 z-10">
      <div className="w-full max-w-xl ml-86">
        <SearchBar
          value={searchValue}
          onChange={setSearchValue}
          placeholder="Pesquisar"
        />
      </div>
      <button
        onClick={handleOpenModal}
        className="flex items-center gap-2 bg-gray-900 text-white text-[14px] m-30 cursor-pointer transition-colors w-[180px] h-[36px] justify-start p-4"
      >
        Criar publicação
      </button>
      {isModalOpen && <ModalResponsibility onClose={handleCloseModal} />}
    </header>
  )
}
