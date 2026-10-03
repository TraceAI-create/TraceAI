import { useEffect, useMemo, useState } from 'react';
import { BookOpenText, ChevronRight, LoaderCircle, Scale, Search, ShieldAlert, X, type LucideIcon } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import PageHeader from '../components/PageHeader';
import { getPolicies } from '../services/policyService';
import type { Policy } from '../types/policy';

function humanize(value: string): string {
  return value
    .split(/[_\s-]+/)
    .filter(Boolean)
    .map((part) => part.charAt(0) + part.slice(1).toLowerCase())
    .join(' ');
}

function formatDate(value: string | null): string {
  if (!value) return '—';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return 'Invalid date';
  return new Intl.DateTimeFormat(undefined, { year: 'numeric', month: 'short', day: '2-digit' }).format(date);
}

function statusStyle(status: string): string {
  switch (status.toUpperCase()) {
    case 'ACTIVE': return 'border-emerald-400/20 bg-emerald-400/[0.08] text-emerald-300';
    case 'INACTIVE': return 'border-amber-400/20 bg-amber-400/[0.08] text-amber-300';
    case 'ARCHIVED': return 'border-slate-500/25 bg-slate-500/[0.08] text-slate-400';
    default: return 'border-slate-500/25 bg-slate-500/[0.08] text-slate-300';
  }
}

function StatusBadge({ status }: { status: string }) {
  return <span className={`inline-flex border px-2 py-1 text-[10px] font-medium leading-none ${statusStyle(status)}`}>{humanize(status)}</span>;
}

function LoadingState() {
  return <div role="status" className="flex items-center gap-3 border border-line bg-panel px-5 py-8 text-sm text-slate-400"><LoaderCircle size={17} className="animate-spin text-accent" />Loading development policies…</div>;
}

function EmptyState({ filtered }: { filtered: boolean }) {
  return (
    <div className="border border-line bg-panel px-5 py-12 text-center">
      <BookOpenText size={20} className="mx-auto text-slate-500" />
      <h2 className="mt-3 text-sm font-medium text-slate-200">{filtered ? 'No policies match your search' : 'No policies available'}</h2>
      <p className="mx-auto mt-1.5 max-w-md text-xs leading-5 text-muted">{filtered ? 'Try another search term or change the status or policy type filters.' : 'Policy records will appear here when available.'}</p>
    </div>
  );
}

function ErrorState({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div role="alert" className="flex flex-col gap-3 border border-rose-400/20 bg-rose-400/[0.04] px-5 py-6 sm:flex-row sm:items-center sm:justify-between">
      <div><h2 className="text-sm font-medium text-rose-200">Could not load policies</h2><p className="mt-1 text-xs text-slate-400">{message}</p></div>
      <button type="button" onClick={onRetry} className="w-fit border border-line px-3 py-2 text-xs text-slate-300 hover:border-slate-600 hover:text-white">Try again</button>
    </div>
  );
}

export default function PoliciesPage() {
  const navigate = useNavigate();
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    getPolicies()
      .then((items) => { if (active) setPolicies(items); })
      .catch((cause: unknown) => { if (active) setError(cause instanceof Error ? cause.message : 'An unexpected error occurred.'); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [reloadKey]);

  const statuses = useMemo(() => [...new Set(policies.map((policy) => policy.status))].sort(), [policies]);
  const policyTypes = useMemo(() => [...new Set(policies.map((policy) => policy.policy_type))].sort(), [policies]);
  const filteredPolicies = useMemo(() => {
    const query = search.trim().toLowerCase();
    return policies.filter((policy) => {
      const matchesSearch = !query || [policy.id, policy.name, policy.version, policy.description].some((value) => value.toLowerCase().includes(query));
      const matchesStatus = statusFilter === 'all' || policy.status === statusFilter;
      const matchesType = typeFilter === 'all' || policy.policy_type === typeFilter;
      return matchesSearch && matchesStatus && matchesType;
    });
  }, [policies, search, statusFilter, typeFilter]);
  const hasFilters = Boolean(search.trim()) || statusFilter !== 'all' || typeFilter !== 'all';

  const openPolicy = (policyId: string) => navigate(`/policies/${policyId}`);

  return (
    <>
      <PageHeader eyebrow="Audit / Governance" title="Policy Library" description="Review the governance policies used or evaluated during AI decisions, including their versions, rules, and evaluation history." />

      <div className="mb-4 flex flex-col gap-3 border border-line bg-panel p-4 xl:flex-row xl:items-center">
        <label className="relative min-w-0 flex-1">
          <span className="sr-only">Search policy ID, name, version, or description</span>
          <Search size={15} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search ID, name, version, or description" className="h-9 w-full border border-line bg-shell pl-9 pr-9 text-xs text-slate-200 outline-none placeholder:text-slate-600 focus:border-accent/50" />
          {search && <button type="button" onClick={() => setSearch('')} aria-label="Clear search" className="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-slate-500 hover:text-slate-200"><X size={14} /></button>}
        </label>
        <div className="flex flex-wrap gap-3">
          <label className="flex items-center gap-2 text-[11px] text-slate-500">
            <span>Status</span>
            <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)} className="h-9 min-w-32 border border-line bg-shell px-3 text-xs text-slate-300 outline-none focus:border-accent/50">
              <option value="all">All statuses</option>
              {statuses.map((status) => <option key={status} value={status}>{humanize(status)}</option>)}
            </select>
          </label>
          <label className="flex items-center gap-2 text-[11px] text-slate-500">
            <span>Type</span>
            <select value={typeFilter} onChange={(event) => setTypeFilter(event.target.value)} className="h-9 min-w-36 border border-line bg-shell px-3 text-xs text-slate-300 outline-none focus:border-accent/50">
              <option value="all">All types</option>
              {policyTypes.map((type) => <option key={type} value={type}>{humanize(type)}</option>)}
            </select>
          </label>
        </div>
      </div>

      <div className="mb-3 flex items-center justify-between gap-3 text-[11px] text-slate-500">
        <span>{loading ? 'Loading policies…' : `${filteredPolicies.length} ${filteredPolicies.length === 1 ? 'policy' : 'policies'}`}</span>
        <span className="inline-flex items-center gap-1.5 text-amber-300/80"><span className="h-1.5 w-1.5 rounded-full bg-amber-400" />Development mock data · not from the backend</span>
      </div>

      {loading ? <LoadingState /> : error ? <ErrorState message={error} onRetry={() => setReloadKey((key) => key + 1)} /> : filteredPolicies.length === 0 ? <EmptyState filtered={hasFilters} /> : (
        <>
          <div className="hidden overflow-x-auto border border-line bg-panel md:block">
            <table className="w-full min-w-[900px] border-collapse text-left">
              <thead className="border-b border-line bg-white/[0.015]">
                <tr className="text-[10px] font-medium uppercase tracking-wider text-slate-500">
                  <th scope="col" className="px-4 py-3">Policy</th><th scope="col" className="px-4 py-3">Version</th><th scope="col" className="px-4 py-3">Type</th><th scope="col" className="px-4 py-3">Status</th><th scope="col" className="px-4 py-3">Effective from</th><th scope="col" className="px-4 py-3">Updated</th><th scope="col" className="px-4 py-3">Rules</th><th scope="col" className="w-8 px-3 py-3"><span className="sr-only">Open policy</span></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line/70">
                {filteredPolicies.map((policy) => (
                  <tr key={policy.id} tabIndex={0} role="link" aria-label={`Open policy ${policy.name}`} onClick={() => openPolicy(policy.id)} onKeyDown={(event) => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); openPolicy(policy.id); } }} className="cursor-pointer text-xs text-slate-300 outline-none hover:bg-white/[0.025] focus-visible:bg-white/[0.035]">
                    <td className="max-w-[260px] px-4 py-3.5"><Link to={`/policies/${policy.id}`} onClick={(event) => event.stopPropagation()} className="block truncate font-medium text-slate-200 hover:text-blue-200">{policy.name}</Link><span className="mt-1 block truncate font-mono text-[9px] text-slate-600">{policy.id}</span></td>
                    <td className="px-4 py-3.5 font-mono text-[11px] text-slate-300">v{policy.version}</td>
                    <td className="px-4 py-3.5"><span className="inline-flex items-center gap-1.5 text-slate-400"><Scale size={12} />{humanize(policy.policy_type)}</span></td>
                    <td className="px-4 py-3.5"><StatusBadge status={policy.status} /></td>
                    <td className="whitespace-nowrap px-4 py-3.5 text-slate-400">{formatDate(policy.effective_from)}</td>
                    <td className="whitespace-nowrap px-4 py-3.5 text-slate-400">{formatDate(policy.updated_at)}</td>
                    <td className="px-4 py-3.5 font-mono tabular-nums text-slate-400">{policy.rules.length}</td>
                    <td className="px-3 py-3.5 text-slate-600"><ChevronRight size={15} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="space-y-2 md:hidden">
            {filteredPolicies.map((policy) => {
              const TypeIcon: LucideIcon = policy.policy_type === 'ACCOUNT_SAFETY' ? ShieldAlert : BookOpenText;
              return (
                <Link key={policy.id} to={`/policies/${policy.id}`} className="block border border-line bg-panel p-4 outline-none hover:border-slate-600 focus-visible:border-accent/50">
                  <div className="flex items-start justify-between gap-3"><div className="flex min-w-0 items-start gap-3"><span className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center border border-line bg-white/[0.02] text-slate-400"><TypeIcon size={15} /></span><span className="min-w-0"><span className="block text-xs font-medium text-slate-200">{policy.name}</span><span className="mt-1 block break-all font-mono text-[9px] text-slate-600">{policy.id}</span></span></div><StatusBadge status={policy.status} /></div>
                  <div className="mt-3 flex flex-wrap items-center justify-between gap-x-3 gap-y-2 border-t border-line pt-3 text-[10px] text-slate-500"><span className="font-mono text-slate-400">v{policy.version}</span><span>{humanize(policy.policy_type)}</span><span>{policy.rules.length} rules</span><span>Updated {formatDate(policy.updated_at)}</span></div>
                </Link>
              );
            })}
          </div>
        </>
      )}
    </>
  );
}
