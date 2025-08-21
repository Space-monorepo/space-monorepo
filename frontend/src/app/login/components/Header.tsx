import Link from 'next/link';

export default function Header() {
  return (
    <header className="flex flex-col gap-1 items-start w-full">
      <h1 className="w-full text-3xl font-semibold text-zinc-900 max-sm:text-3xl">
        <div className="text-3xl font-bold text-zinc-900 max-sm:text-3xl">
          Entre com sua conta
        </div>
      </h1>
      <p className="w-full text-xs text-neutral-500">
        Não tem uma conta?{' '}
        <Link href="/signup" className="underline hover:text-neutral-700">Cadastre-se</Link>
      </p>
    </header>
  );
}