"use client";

interface SimpleFilePickerProps {
  onChange: (files: File[]) => void;
  accept?: string;
  multiple?: boolean;
}

const SimpleFilePicker: React.FC<SimpleFilePickerProps> = ({
  onChange,
  accept,
  multiple = false,
}) => {
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      onChange(Array.from(event.target.files));
    }
  };

  return (
    <input 
      type="file" 
      onChange={handleFileChange} 
      accept={accept} 
      multiple={multiple} 
      className="w-full text-sm text-gray-500
        file:mr-4 file:py-2 file:px-4
        file:rounded-full file:border-0
        file:text-sm file:font-semibold
        file:bg-violet-50 file:text-violet-700
        hover:file:bg-violet-100"
    />
  );
};

export default SimpleFilePicker;
