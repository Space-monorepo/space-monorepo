import { useEffect, useState } from "react"

export default function useMediaQuery(query: string) {
  const [matches, setMatches] = useState<boolean>(() => {
    if (typeof window === "undefined") {
      return false
    }
    return window.matchMedia(query).matches
  })

  useEffect(() => {
    if (typeof window === "undefined") return

    const mediaQueryList = window.matchMedia(query)
    const handler = () => setMatches(mediaQueryList.matches)

    handler()

    mediaQueryList.addEventListener("change", handler)
    return () => mediaQueryList.removeEventListener("change", handler)
  }, [query])

  return matches
}

