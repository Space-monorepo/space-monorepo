import { Button } from '@/components/ui/button';

export default function SocialLoginButtons() {
  return (
    <div className="grid grid-cols-2 gap-4">
      <Button variant="outline" className="w-full">Google</Button>
      <Button variant="outline" className="w-full">Outlook</Button>
    </div>
  );
}