import { NextResponse, type NextRequest } from "next/server";

// Rotas públicas e seus comportamentos quando o usuário está autenticado
const publicRoutes = [
    { path: '/', whenAuthenticated: '/next' },
    { path: '/login', whenAuthenticated: '/redirect' },
    { path: '/signup', whenAuthenticated: '/redirect' },
    { path: '/settings', whenAuthenticated: '/next' },
    { path: '/home', whenAuthenticated: '/next' },
    { path: '/profile', whenAuthenticated: '/next' },
] as const;

// Rota para redirecionamento quando o usuário não está autenticado
const REDIRECT_WHEN_NOT_AUTHENTICATED_ROUTE = '/login';

export function middleware(request: NextRequest) {
    const path = request.nextUrl.pathname;
    const authToken = request.cookies.get('token')?.value; // Acessa o valor do cookie 'token'

    console.log('Middleware executado para a rota:', path);
    console.log('Token de autenticação:', authToken);

    // Verifica se a rota atual é pública
    const isPublicRoute = publicRoutes.some(route => path.startsWith(route.path));
    console.log('É uma rota pública?', isPublicRoute);

    // Se o usuário não estiver autenticado e a rota não for pública, redireciona para o login
    if (!authToken && !isPublicRoute) {
        console.log('Usuário não autenticado tentando acessar rota privada. Redirecionando para login...');
        const redirectUrl = request.nextUrl.clone();
        redirectUrl.pathname = REDIRECT_WHEN_NOT_AUTHENTICATED_ROUTE;
        return NextResponse.redirect(redirectUrl);
    }

    // Se o usuário estiver autenticado e tentar acessar uma rota pública que redireciona quando autenticado
    if (authToken && isPublicRoute) {
        const publicRoute = publicRoutes.find(route => path.startsWith(route.path));
        if (publicRoute && publicRoute.whenAuthenticated === '/redirect') {
            console.log('Usuário autenticado tentando acessar rota pública com redirecionamento. Redirecionando para home...');
            const redirectUrl = request.nextUrl.clone();
            redirectUrl.pathname = '/';
            return NextResponse.redirect(redirectUrl);
        }
    }

    // Se o usuário estiver autenticado e a rota não for pública, permite o acesso
    if (authToken && !isPublicRoute) {
        console.log('Usuário autenticado acessando rota privada. Permitindo acesso...');
        // Aqui você pode adicionar a lógica para verificar se o JWT está expirado
        // e aplicar uma estratégia de refresh token, se necessário
    }

    // Permite o acesso para rotas públicas ou rotas privadas com autenticação válida
    console.log('Acesso permitido para a rota:', path);
    return NextResponse.next();
}

export const config = {
    matcher: [
        /*
         * Match all request paths except for the ones starting with:
         * - api (API routes)
         * - _next/static (static files)
         * - _next/image (image optimization files)
         * - favicon.ico, sitemap.xml, robots.txt (metadata files)
         */
        '/((?!api|_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt|.*\\.(?:ico|png|jpg|jpeg|svg|gif|webp)$).*)',
    ],
};