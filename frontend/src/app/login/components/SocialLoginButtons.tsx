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
      <div className="fixed bottom-8 left-8 max-[770px]:hidden">
        <Image src="/space-escrita.svg" alt="Space escrita" width={150} height={150} className="w-32 h-auto max-sm:w-28" />
      </div>
    </>
  );
}