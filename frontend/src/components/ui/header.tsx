import { useState, useEffect } from "react"
import ModalResponsibility from "@/components/modals/responsabilty/ModalResponsabilty"
import { SearchBar } from "@/components/ui/search-bar"
import { API_URL } from "@/config"
import getTokenFromCookies from "@/app/api/src/controllers/getTokenFromCookies"

export default function Header() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [searchValue, setSearchValue] = useState("")
  const [searchResults, setSearchResults] = useState([])

  const handleOpenModal = () => {
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
  }

  useEffect(() => {
    const fetchResults = async () => {
      if (searchValue.length >= 3) {
        const token = getTokenFromCookies();
        const headers: HeadersInit = {};
        if (token) headers["Authorization"] = `Bearer ${token}`;
        try {
          const res = await fetch(`${API_URL}/search?q=${encodeURIComponent(searchValue)}`, {
            headers,
          })
          if (res.ok) {
            const data = await res.json()
            setSearchResults(data)
          } else {
            setSearchResults([])
          }
        } catch (err) {
          setSearchResults([])
        }
      } else {
        setSearchResults([])
      }
    }
    fetchResults()
  }, [searchValue])

  return (
    <header
      className="flex items-center font-manrope justify-between p-4 bg-gray-100 border-b border-[#e0e0e0] h-16 fixed top-0 left-[16rem] right-0 z-10
        max-lg:left-0 max-lg:w-full max-lg:px-2 max-md:flex-col max-md:h-auto max-md:gap-2"
    >
      <div className="w-full max-w-xl ml-86 max-lg:ml-0 flex-1 relative z-30">
        <SearchBar
          value={searchValue}
          onChange={setSearchValue}
          placeholder="Pesquisar"
        />
        {searchValue.length >= 3 && (
          <div className="absolute left-0 top-full w-full bg-white shadow-lg rounded border border-gray-200 mt-2 z-30">
            {searchResults.length > 0 ? (
              <ul className="divide-y divide-gray-100 max-h-80 overflow-y-auto">
                {searchResults.map((result: any) => (
                  <li key={result.id} className="flex items-center gap-3 p-3 hover:bg-gray-50 cursor-pointer transition-colors">
                    {result.type === "user" ? (
                      <>
                        {result.profile_image_url ? (
                          <img src={result.profile_image_url} alt={result.name} className="w-8 h-8 rounded-full object-cover border" />
                        ) : (
                          <div className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center text-gray-600 font-bold">👤</div>
                        )}
                        <div className="flex flex-col">
                          <span className="font-medium text-gray-900">{result.name}</span>
                          <span className="text-xs text-gray-500">Usuário</span>
                        </div>
                      </>
                    ) : (
                      <>
                        <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold">📝</div>
                        <div className="flex flex-col">
                          <span className="font-medium text-gray-900">{result.title}</span>
                          <span className="text-xs text-gray-500">Post</span>
                        </div>
                      </>
                    )}
                  </li>
                ))}
              </ul>
            ) : (
              <div className="p-4 text-center text-gray-500">Nenhum resultado encontrado</div>
            )}
          </div>
        )}
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
