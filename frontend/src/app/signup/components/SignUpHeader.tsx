import Link from 'next/link';

export default function SignUpHeader() {
  return (
    <header className="max-w-full w-[231px]">
      <h1 className="text-3xl font-semibold text-zinc-900">
        Crie uma conta
      </h1>
      <p className="mt-1 text-xs text-neutral-500">
        Já tem uma conta?{' '}
        <Link href="/login" className="hover:underline">
          Entre
        </Link>
      </p>
    </header>
  );
}
