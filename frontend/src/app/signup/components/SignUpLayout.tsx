import Image from 'next/image';

export default function SignUpLayout({ children }: { children: React.ReactNode }) {
  return (
    <main className="flex min-h-screen bg-white overflow-x-hidden">
      {/* Imagem lateral esquerda */}
      <div className="hidden md:flex w-1/2 items-center justify-center">
        <Image
          src="/Planet.png"
          alt="Logo espaço"
          width={400}
          height={400}
          className="object-contain"
          priority
          draggable={false}
        />
      </div>
      <div className="flex-1 flex items-center justify-center bg-white">
        <section className="flex flex-col gap-28 items-start w-full max-w-[480px] px-4">
          {children}
        </section>
      </div>
    </main>
  );
}
