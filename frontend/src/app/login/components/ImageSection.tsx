import Image from 'next/image';

export default function ImageSection() {
  return (
    <div className="flex items-center justify-center w-full h-full">
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
  );
}