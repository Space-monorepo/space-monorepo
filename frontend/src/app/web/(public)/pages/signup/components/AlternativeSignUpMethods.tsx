import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import Image from 'next/image';

export default function AlternativeSignUpMethods() {
  return (
    <>
      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <Separator className="w-full" />
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-gray-100 px-2 text-gray-500">Ou se registre com</span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <Button variant="outline" className="w-full">
          Google
        </Button>
        <Button variant="outline" className="w-full">
          Outlook
        </Button>
      </div>

      <Image src="/space-escrita.svg" alt="Space escrita" width={150} height={150} className="fixed bottom-8 left-8 p-4 text-sm text-gray-500" />
    </>
  );
}