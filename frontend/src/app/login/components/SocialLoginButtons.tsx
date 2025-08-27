import { Button } from '@/components/ui/button';
import Image from 'next/image';

export default function SocialLoginButtons() {
  return (
    <>
      <div className="flex gap-8 items-center w-full max-sm:flex-col max-sm:gap-4">
        <Button variant="outline" className="box-border flex gap-2.5 items-center px-4 py-2 w-56 bg-white border border-solid border-neutral-500 max-sm:w-full rounded-none">
          Google
        </Button>
        <Button variant="outline" className="box-border flex gap-2.5 items-center px-4 py-2 w-56 bg-white border border-solid border-neutral-500 max-sm:w-full rounded-none">
          Outlook
        </Button>
      </div>
      <Image src="/space-escrita.svg" alt="Space escrita" width={150} height={150} className="fixed bottom-8 left-8 p-4 text-sm text-gray-500" />
    </>
  );
}