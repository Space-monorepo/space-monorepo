import { Button } from "@/components/ui/button";

interface TabButtonProps {
  label: string;
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

function TabButton({ label, activeTab, setActiveTab }: TabButtonProps) {
  const isActive = activeTab === label.toLowerCase();
  return (
    <button
      className={`text-lg ${isActive ? "font-semibold" : "text-gray-500"}`}
      onClick={() => setActiveTab(label.toLowerCase())}
    >
      {label}
    </button>
  );
}

interface HeaderProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  openModal: () => void;
}

export default function Header({ activeTab, setActiveTab, openModal }: HeaderProps) {
  return (
    <div className="flex justify-between items-center mb-6">
      <div className="flex space-x-6">
        <TabButton label="Geral" activeTab={activeTab} setActiveTab={setActiveTab} />
        <TabButton label="Em alta" activeTab={activeTab} setActiveTab={setActiveTab} />
      </div>
      <div className="flex items-center gap-4">
        <button className="text-gray-500">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect width="18" height="18" x="3" y="3" rx="2" />
            <path d="M7 7h.01" />
            <path d="M17 7h.01" />
            <path d="M7 17h.01" />
            <path d="M17 17h.01" />
          </svg>
        </button>
        <Button className="bg-black hover:bg-black/90 text-white" onClick={openModal}>
          Criar publicação
        </Button>
      </div>
    </div>
  );
}