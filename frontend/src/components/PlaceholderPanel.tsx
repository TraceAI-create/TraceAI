import type { ReactNode } from 'react';
import { Construction } from 'lucide-react';

interface PlaceholderPanelProps {
  title: string;
  description: string;
  icon?: ReactNode;
}

export default function PlaceholderPanel({ title, description, icon }: PlaceholderPanelProps) {
  return (
    <section className="border border-line bg-panel px-5 py-6 sm:px-6">
      <div className="mb-4 flex h-9 w-9 items-center justify-center rounded-md border border-line bg-white/[0.02] text-slate-400">
        {icon ?? <Construction size={17} strokeWidth={1.7} />}
      </div>
      <h2 className="text-sm font-medium text-slate-200">{title}</h2>
      <p className="mt-1.5 max-w-2xl text-[13px] leading-5 text-muted">{description}</p>
    </section>
  );
}
