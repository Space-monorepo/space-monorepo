import { Search } from "@carbon/icons-react";

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

export function SearchBar({
  value,
  onChange,
  placeholder = "Pesquisar",
}: SearchBarProps) {
  return (
    <div
      className="box-border flex w-full items-center gap-2.5 rounded-md border border-solid border-stone-300 bg-white px-3 py-2 max-[899px]:gap-2 max-[899px]:px-2 max-[899px]:py-2"
    >
      <div>
        <Search size={20} />
      </div>
      <input
        type="text"
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full text-sm leading-6 text-neutral-800 outline-none placeholder:text-neutral-500"
      />
    </div>
  );
}
