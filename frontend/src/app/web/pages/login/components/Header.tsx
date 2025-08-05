import Link from 'next/link';

export default function Header() {
  return (
    <div className="space-y-2 text-center">
      <h1 className="text-2xl font-bold">Entre com sua conta</h1>
      <p className="text-gray-500 text-sm">
        Não tem uma conta?{' '}
        <Link href="/signup" className="text-gray-700 hover:underline">
          Cadastre-se
        </Link>
      </p>
    </div>
  );
}