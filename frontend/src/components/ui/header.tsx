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
    <header className="fixed top-0 left-0 right-0 min-[900px]:left-64 z-20 border-b border-[#e0e0e0] bg-gray-100">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-3 px-4 py-3 font-manrope min-[900px]:px-6 lg:px-10 min-[900px]:h-16 min-[900px]:flex-row min-[900px]:items-center min-[900px]:gap-4 min-[900px]:py-0">
        <div className="relative z-0 flex-1 min-w-0 transition-all duration-200 min-[900px]:min-w-[260px]">
          <SearchBar
            value={searchValue}
            onChange={setSearchValue}
            placeholder="Pesquisar"
          />
          {searchValue.length >= 3 && (
            <div className="absolute left-0 top-full z-30 mt-2 w-full rounded border border-gray-200 bg-white shadow-lg">
              {searchResults.length > 0 ? (
                <ul className="max-h-80 divide-y divide-gray-100 overflow-y-auto">
                  {searchResults.map((result: any) => (
                    <li key={result.id} className="flex cursor-pointer items-center gap-3 p-3 transition-colors hover:bg-gray-50">
                      {result.type === "user" ? (
                        <>
                          {result.profile_image_url ? (
                            <img src={result.profile_image_url} alt={result.name} className="h-8 w-8 rounded-full border object-cover" />
                          ) : (
                            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-300 text-gray-600 font-bold">👤</div>
                          )}
                          <div className="flex flex-col">
                            <span className="font-medium text-gray-900">{result.name}</span>
                            <span className="text-xs text-gray-500">Usuário</span>
                          </div>
                        </>
                      ) : (
                        <>
                          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 text-blue-600 font-bold">📝</div>
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
          className="flex h-10 w-full items-center justify-center gap-2 whitespace-nowrap rounded bg-[#161616] px-4 text-sm font-medium text-white transition-colors hover:bg-black cursor-pointer min-[900px]:w-auto min-[900px]:min-w-[164px] min-[900px]:flex-shrink-0"
        >
          Criar publicação
        </button>
      </div>
      {isModalOpen && <ModalResponsibility onClose={handleCloseModal} />}
    </header>
  )
}
