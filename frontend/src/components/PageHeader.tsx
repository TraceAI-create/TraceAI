import type { ReactNode } from 'react';

interface PageHeaderProps {
  eyebrow?: string;
  title: string;
  description: string;
  action?: ReactNode;
}

export default function PageHeader({ eyebrow = 'TraceAI workspace', title, description, action }: PageHeaderProps) {
  return (
    <div className="mb-8 flex flex-col justify-between gap-4 border-b border-line pb-6 sm:flex-row sm:items-end">
      <div>
        <p className="mb-2 font-mono text-[10px] uppercase tracking-[0.16em] text-accent/80">{eyebrow}</p>
        <h1 className="text-2xl font-semibold tracking-tight text-slate-100">{title}</h1>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">{description}</p>
      </div>
      {action}
    </div>
  );
}
