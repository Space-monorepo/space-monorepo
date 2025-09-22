
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
    <header
      className="flex items-center font-manrope justify-between p-4 bg-gray-100 border-b border-[#e0e0e0] h-16 fixed top-0 left-[16rem] right-0 z-10
        max-lg:left-0 max-lg:w-full max-lg:px-2 max-md:flex-col max-md:h-auto max-md:gap-2"
    >
      <div className="w-full max-w-xl ml-86 max-lg:ml-0 flex-1">
        <SearchBar
          value={searchValue}
          onChange={setSearchValue}
          placeholder="Pesquisar"
        />
      </div>
      <button
        onClick={handleOpenModal}
        className="flex items-center gap-2 bg-gray-900 text-white text-[14px] m-30 cursor-pointer transition-colors w-[180px] h-[36px] justify-start p-4
          max-md:w-full max-md:justify-center max-md:mt-2"
      >
        Criar publicação
      </button>
      {isModalOpen && <ModalResponsibility onClose={handleCloseModal} />}
    </header>
  )
}
