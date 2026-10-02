import { NavLink, Outlet } from 'react-router-dom';
import { ShieldCheck } from 'lucide-react';
import { navigationGroups } from '../routes/navigation';

export default function AppLayout() {
  return (
    <div className="min-h-screen bg-shell text-slate-200">
      <aside className="fixed inset-y-0 left-0 z-20 hidden w-60 flex-col border-r border-line bg-[#0b1017] md:flex">
        <div className="flex h-16 items-center gap-3 border-b border-line px-5">
          <div className="flex h-8 w-8 items-center justify-center rounded-md border border-accent/25 bg-accent/10 text-accent">
            <ShieldCheck size={18} strokeWidth={1.8} />
          </div>
          <div>
            <p className="text-sm font-semibold tracking-wide text-slate-100">TraceAI</p>
            <p className="text-[10px] uppercase tracking-[0.16em] text-muted">Decision audit</p>
          </div>
        </div>

        <nav aria-label="Main navigation" className="flex-1 space-y-7 px-3 py-6">
          {navigationGroups.map((group) => (
            <section key={group.label}>
              <h2 className="mb-2 px-3 text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-500">
                {group.label}
              </h2>
              <div className="space-y-1">
                {group.items.map(({ label, to, icon: Icon, end }) => (
                  <NavLink
                    key={to}
                    to={to}
                    end={end}
                    className={({ isActive }) =>
                      `flex h-9 items-center gap-3 rounded-md px-3 text-[13px] transition-colors ${
                        isActive
                          ? 'bg-accent/10 text-blue-200 ring-1 ring-inset ring-accent/15'
                          : 'text-slate-400 hover:bg-white/[0.04] hover:text-slate-200'
                      }`
                    }
                  >
                    <Icon size={16} strokeWidth={1.8} />
                    {label}
                  </NavLink>
                ))}
              </div>
            </section>
          ))}
        </nav>

        <div className="border-t border-line px-5 py-4">
          <div className="flex items-center gap-2 text-[11px] text-slate-500">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
            Audit workspace
          </div>
        </div>
      </aside>

      <div className="md:pl-60">
        <header className="sticky top-0 z-10 flex h-16 items-center justify-between border-b border-line bg-shell/95 px-5 backdrop-blur-sm sm:px-8">
          <div className="md:hidden">
            <span className="text-sm font-semibold text-slate-100">TraceAI</span>
          </div>
          <div className="hidden text-xs text-slate-500 md:block">AI decision traceability and audit</div>
          <div className="flex items-center gap-3">
            <span className="rounded border border-line px-2 py-1 font-mono text-[10px] text-slate-500">LOCAL</span>
            <span className="flex h-7 w-7 items-center justify-center rounded-full border border-line bg-panel text-[10px] font-medium text-slate-300">AU</span>
          </div>
        </header>
        <main className="mx-auto w-full max-w-[1440px] px-5 py-8 sm:px-8 lg:px-10">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
