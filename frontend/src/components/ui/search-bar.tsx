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
    <div className="box-border flex gap-2.5 items-center px-3 py-2 w-[675px] bg-white border border-solid border-stone-300 max-md:px-3.5 max-md:py-2.5 max-sm:gap-2 max-sm:px-4 max-sm:py-3">
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
