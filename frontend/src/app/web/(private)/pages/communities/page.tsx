"use client"

import Sidebar from "@/components/ui/sidebar"
import { Input } from "@/components/ui/input"
import { Search, MapPin, Users, Activity, MoreHorizontal, Snowflake } from "lucide-react"

const communities = [
  {
    id: 1,
    title: "Título da Comunidade",
    location: "Paulinia, São Paulo",
    category: "Educação",
    description:
      "Lorem ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged.",
    members: 1450,
    activity: 120,
    status: "hot",
    statusValue: 12,
    image: "/placeholder.svg?height=120&width=120",
    color: "teal",
  },
  {
    id: 2,
    title: "Título da Comunidade",
    location: "Paulinia, São Paulo",
    category: "Jogos",
    description:
      "Lorem ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged.",
    members: 289,
    activity: 10,
    status: "hot",
    statusValue: 14,
    image: "/placeholder.svg?height=120&width=120",
    color: "red",
  },
  {
    id: 3,
    title: "Título da Comunidade",
    location: "Paulinia, São Paulo",
    category: "Arte",
    description:
      "Lorem ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged.",
    members: 102,
    activity: 0,
    status: "cold",
    statusValue: 0,
    image: "/placeholder.svg?height=120&width=120",
    color: "gray",
  },
  {
    id: 4,
    title: "Título da Comunidade",
    location: "Campinas, São Paulo",
    category: "Educação",
    description:
      "Lorem ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged.",
    members: 350,
    activity: 89,
    status: "new",
    statusValue: 5,
    image: "/placeholder.svg?height=120&width=120",
    color: "blue",
  },
]

export default function CommunitiesPage() {
  return (
    <div className="min-h-screen bg-gray-100 flex">
      <Sidebar />

      <main className="flex-1 p-4">
        <div className="max-w-5xl mx-auto">
          {/* Header */}
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-2xl font-bold">Minhas comunidades</h1>
            <div className="relative w-96">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input placeholder="Pesquisar" className="pl-9 h-10 pr-4" />
            </div>
          </div>

          {/* Communities List */}
          <div className="space-y-4">
            {communities.map((community) => (
              <div key={community.id} className="bg-white rounded-lg shadow-sm p-4">
                <div className="flex">
                  {/* Community Image */}
                  <div
                    className={`w-32 h-32 rounded-lg overflow-hidden flex-shrink-0 mr-4 ${
                      community.color === "teal"
                        ? "bg-teal-500"
                        : community.color === "red"
                          ? "bg-red-500"
                          : community.color === "gray"
                            ? "bg-gray-800"
                            : "bg-blue-200"
                    }`}
                  >
                    {community.id === 1 && (
                      <svg viewBox="0 0 200 200" className="w-full h-full p-2">
                        <path
                          d="M100,30 C120,10 150,20 160,40 C170,60 160,90 140,100 C160,110 170,140 160,160 C150,180 120,190 100,170 C80,190 50,180 40,160 C30,140 40,110 60,100 C40,90 30,60 40,40 C50,20 80,10 100,30 Z"
                          fill="#D97706"
                        />
                        <circle cx="80" cy="80" r="10" fill="#000" />
                        <circle cx="120" cy="80" r="10" fill="#000" />
                        <path d="M70,120 Q100,150 130,120" stroke="#000" strokeWidth="5" fill="none" />
                      </svg>
                    )}
                    {community.id === 2 && (
                      <svg viewBox="0 0 200 200" className="w-full h-full p-4">
                        <rect x="40" y="40" width="120" height="120" rx="10" fill="#FCD34D" />
                        <rect x="60" y="60" width="80" height="60" rx="5" fill="#000" />
                        <rect x="70" y="130" width="20" height="20" rx="3" fill="#000" />
                        <rect x="110" y="130" width="20" height="20" rx="3" fill="#000" />
                        <circle cx="140" cy="70" r="5" fill="#EF4444" />
                        <circle cx="140" cy="90" r="5" fill="#3B82F6" />
                      </svg>
                    )}
                    {community.id === 3 && (
                      <svg viewBox="0 0 200 200" className="w-full h-full p-4">
                        <rect x="60" y="40" width="20" height="120" rx="2" fill="#EF4444" />
                        <rect x="90" y="60" width="20" height="100" rx="2" fill="#3B82F6" />
                        <rect x="120" y="80" width="20" height="80" rx="2" fill="#10B981" />
                        <circle cx="70" cy="30" r="10" fill="#FCD34D" />
                        <circle cx="100" cy="50" r="10" fill="#8B5CF6" />
                        <circle cx="130" cy="70" r="10" fill="#EC4899" />
                      </svg>
                    )}
                    {community.id === 4 && (
                      <svg viewBox="0 0 200 200" className="w-full h-full">
                        <rect x="40" y="100" width="120" height="60" fill="#EF4444" />
                        <rect x="60" y="80" width="80" height="20" fill="#EF4444" />
                        <rect x="90" y="50" width="20" height="30" fill="#78716C" />
                        <circle cx="50" cy="170" r="10" fill="#78716C" />
                        <circle cx="150" cy="170" r="10" fill="#78716C" />
                        <path d="M0,170 Q50,120 100,170 Q150,120 200,170" fill="#4ADE80" />
                        <path d="M30,170 Q50,140 70,170" fill="#4ADE80" />
                        <path d="M130,170 Q150,140 170,170" fill="#4ADE80" />
                        <circle cx="40" cy="130" r="5" fill="#FFFFFF" />
                        <circle cx="60" cy="130" r="5" fill="#FFFFFF" />
                      </svg>
                    )}
                  </div>

                  {/* Community Info */}
                  <div className="flex-1">
                    <div className="flex justify-between items-start">
                      <div>
                        <h2 className="text-xl font-semibold">{community.title}</h2>
                        <div className="flex items-center text-sm text-gray-500 mt-1">
                          <MapPin className="w-4 h-4 mr-1" />
                          <span>{community.location}</span>
                          <span className="mx-2">|</span>
                          <span>{community.category}</span>
                        </div>
                      </div>

                      {/* Status Indicator */}
                      <div>
                        {community.status === "hot" && (
                          <div className="flex items-center text-red-500">
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              width="20"
                              height="20"
                              viewBox="0 0 24 24"
                              fill="currentColor"
                            >
                              <path d="M12 2C10.35 2 9 3.35 9 5V9C9 10.3 9.84 11.4 11 11.82V22H13V11.82C14.16 11.4 15 10.3 15 9V5C15 3.35 13.65 2 12 2Z" />
                            </svg>
                            <span className="ml-1 font-medium">{community.statusValue}</span>
                          </div>
                        )}
                        {community.status === "cold" && (
                          <div className="flex items-center text-blue-500">
                            <Snowflake className="w-5 h-5" />
                          </div>
                        )}
                        {community.status === "new" && (
                          <div className="flex items-center">
                            <span className="bg-gray-200 text-gray-800 rounded-full w-6 h-6 flex items-center justify-center text-xs font-medium">
                              {community.statusValue}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>

                    <p className="text-gray-600 text-sm mt-2 line-clamp-2">{community.description}</p>

                    {/* Community Stats */}
                    <div className="flex justify-between items-center mt-4">
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <div className="flex items-center">
                          <Users className="w-4 h-4 mr-1" />
                          <span>{community.members}</span>
                        </div>
                        <div className="flex items-center">
                          <Activity className="w-4 h-4 mr-1" />
                          <span>{community.activity === 0 ? "Sem interações" : community.activity}</span>
                        </div>
                      </div>
                      <button className="text-gray-400 hover:text-gray-600">
                        <MoreHorizontal className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}

