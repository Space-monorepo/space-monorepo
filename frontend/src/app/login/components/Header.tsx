import Image from 'next/image';
import Link from 'next/link';

export default function Header() {
  return (
    <header className="flex flex-col gap-8 items-start w-full">
      <Image
        src="/space-escrita.svg"
        alt="Space"
        width={160}
        height={48}
        className="w-32 h-auto max-md:w-28 min-[770px]:hidden"
        priority
      />
      <div className="flex flex-col gap-2 w-full">
        <h1 className="text-3xl font-semibold text-zinc-900 max-sm:text-2xl">
          Entre com sua conta
        </h1>
        <p className="text-xs text-neutral-500">
          Não tem uma conta?{' '}
          <Link href="/signup" className="underline hover:text-neutral-700">Cadastre-se</Link>
        </p>
      </div>
    </header>
  );
}
