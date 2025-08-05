import Image from 'next/image';

export default function SignUpLayout({ children }: { children: React.ReactNode }) {
  return (
    <main className="flex min-h-screen flex-col md:flex-row">
      <div className="flex items-center justify-center w-full md:w-1/2 bg-white p-6">
        <div className="max-w-[400px] w-full">
          <Image src="/Planet.png" alt="Space" width={400} height={400} className="mx-auto" priority />
        </div>
      </div>

      <div className="flex items-center justify-center w-full md:w-1/2 bg-gray-100 p-6">
        <div className="max-w-[400px] w-full space-y-8">
          {children}
        </div>
      </div>
    </main>
  );
}