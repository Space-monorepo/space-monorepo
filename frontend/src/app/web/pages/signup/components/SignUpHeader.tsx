import Link from 'next/link';

export default function SignUpHeader() {
  return (
    <div className="space-y-2 text-center">
      <h1 className="text-2xl font-bold">Crie uma conta</h1>
      <p className="text-gray-500 text-sm">
        Já tem uma conta?{' '}
        <Link href="/login" className="text-gray-700 hover:underline">
          Entre
        </Link>
      </p>
    </div>
  );
}