import Image from 'next/image';

export default function AlternativeSignUpMethods() {
  return (
    <section className="mt-8 w-full">
      <div className="flex gap-9 items-center w-full text-xs leading-none text-neutral-500">
        <div className="flex shrink-0 self-stretch my-auto h-px bg-stone-300 w-[152px]" />
        <span className="grow shrink self-stretch text-neutral-500 w-[83px]">
          Ou se registre com
        </span>
        <div className="flex shrink-0 self-stretch my-auto h-px bg-stone-300 w-[152px]" />
      </div>

      <div className="flex gap-8 items-center mt-8 w-full text-sm leading-6 whitespace-nowrap text-neutral-800">
        <button className="flex gap-2.5 items-center py-2 pr-16 pl-4 w-56 border border-solid border-neutral-500 hover:bg-gray-50 transition-colors">
          <span className="self-stretch my-auto text-neutral-800">Google</span>
        </button>
        <button className="flex gap-2.5 items-center py-2 pr-16 pl-4 w-56 border border-solid border-neutral-500 hover:bg-gray-50 transition-colors">
          <span className="self-stretch my-auto text-neutral-800">Outlook</span>
        </button>
      </div>

      <Image
        src="/space-escrita.svg"
        alt="Space escrita"
        width={150}
        height={150}
        className="fixed bottom-8 left-8 p-4 text-sm text-gray-500"
      />
    </section>
  );
}
