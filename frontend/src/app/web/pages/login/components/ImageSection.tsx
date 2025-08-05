import Image from 'next/image';

export default function ImageSection() {
  return (
    <div className="flex items-center justify-center w-full md:w-1/2 bg-white p-6">
      <div className="max-w-[400px] w-full">
        <Image src="/Planet.png" alt="Space" width={400} height={400} className="mx-auto" priority />
      </div>
    </div>
  );
}