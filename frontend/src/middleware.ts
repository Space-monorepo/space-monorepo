import { NextResponse, type NextRequest } from "next/server";
import {
  PUBLIC_ROUTES,
  REDIRECT_WHEN_AUTHENTICATED,
  REDIRECT_WHEN_NOT_AUTHENTICATED,
} from "@/lib/authRoutes";

function isPublicRoute(pathname: string): boolean {
  return PUBLIC_ROUTES.includes(pathname);
}

// 🔓 Apenas retorna o valor da variável de ambiente
function isBypassEnabled(): boolean {
  return process.env.BYPASS_AUTH === "0";
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const authToken = request.cookies.get("token")?.value;

  const bypass = isBypassEnabled();
  const isPublic = isPublicRoute(pathname);
  const isAuthenticated = Boolean(authToken);

  if (bypass) {
    return NextResponse.next();
  }

  if (!isAuthenticated && !isPublic) {
    const redirectUrl = request.nextUrl.clone();
    redirectUrl.pathname = REDIRECT_WHEN_NOT_AUTHENTICATED;
    redirectUrl.searchParams.set("session", "expired");
    return NextResponse.redirect(redirectUrl);
  }

  if (isAuthenticated && isPublic) {
    const redirectUrl = request.nextUrl.clone();
    redirectUrl.pathname = REDIRECT_WHEN_AUTHENTICATED;
    return NextResponse.redirect(redirectUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    '/((?!api|_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt|.*\\.(?:ico|png|jpg|jpeg|svg|gif|webp)$).*)',
  ],
};
