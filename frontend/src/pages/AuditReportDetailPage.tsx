import { useEffect, useState, type ReactNode } from 'react';
import { ArrowLeft, ChevronDown, Clock3, FileSearch, Fingerprint, LoaderCircle, Scale, ShieldCheck } from 'lucide-react';
import { Link, useParams } from 'react-router-dom';
import PageHeader from '../components/PageHeader';
import { getAuditReport } from '../services/auditReportService';
import type { AuditReport } from '../types/auditReport';

function formatDate(value: string | null): string {
  if (!value) return '—';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? '—' : new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'medium' }).format(date);
}

function readable(value: string): string {
  return value.replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function badgeClass(value: string): string {
  const status = value.toLowerCase();
  if (status.includes('reject') || status.includes('failed') || status.includes('warning')) return 'border-rose-400/20 bg-rose-400/[0.08] text-rose-300';
  if (status.includes('approve') || status.includes('passed') || status.includes('intact')) return 'border-emerald-400/20 bg-emerald-400/[0.08] text-emerald-300';
  return 'border-slate-500/25 bg-slate-500/[0.08] text-slate-300';
}

function Badge({ value }: { value: string }) {
  return <span className={`inline-flex border px-2 py-1 font-mono text-[9px] uppercase tracking-wider ${badgeClass(value)}`}>{readable(value)}</span>;
}

function Section({ title, icon: Icon, children }: { title: string; icon: typeof FileSearch; children: ReactNode }) {
  return <section className="border border-line bg-panel"><div className="flex items-center gap-2 border-b border-line px-4 py-3"><Icon size={14} className="text-slate-500" /><h2 className="text-xs font-medium text-slate-200">{title}</h2></div><div className="p-4">{children}</div></section>;
}

function truncateHash(value: string | null): string {
  if (!value) return '—';
  return value.length > 24 ? `${value.slice(0, 12)}…${value.slice(-8)}` : value;
}

function ReportBody({ report }: { report: AuditReport }) {
  const decision = report.decision;
  return (
    <>
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <Link to="/audit-reports" className="inline-flex items-center gap-2 text-xs text-slate-400 hover:text-slate-100"><ArrowLeft size={14} />Back to audit reports</Link>
        <span className="inline-flex items-center gap-1.5 text-[9px] uppercase tracking-wider text-amber-300/80"><span className="h-1.5 w-1.5 rounded-full bg-amber-400" />Development mock report</span>
      </div>
      <PageHeader eyebrow="Consolidated decision record" title="Audit Report" description="Investigator-oriented view of the recorded decision lifecycle and associated audit data." action={<Link to={`/decisions/${decision.id}`} className="inline-flex h-9 items-center gap-2 border border-line px-3 text-xs text-slate-300 hover:border-slate-600 hover:text-white">Decision detail <ArrowLeft size={13} className="rotate-180" /></Link>} />

      <section className="mb-5 border border-line bg-panel">
        <div className="flex flex-wrap items-start justify-between gap-4 border-b border-line px-4 py-4 sm:px-5">
          <div className="min-w-0"><p className="text-sm font-medium text-slate-100">{decision.agent_id}</p><p className="mt-1 break-all font-mono text-[10px] text-slate-500">{decision.id}</p><p className="mt-1 text-[10px] text-slate-600">Agent version {decision.agent_version}</p></div>
          <div className="flex flex-wrap items-center gap-2"><Badge value={decision.status} />{report.final_outcome && <Badge value={report.final_outcome.value} />}</div>
        </div>
        <dl className="grid grid-cols-2 divide-x divide-y divide-line sm:grid-cols-4 sm:divide-y-0"><div className="p-4"><dt className="text-[9px] uppercase tracking-wider text-slate-600">Created</dt><dd className="mt-1.5 text-[11px] text-slate-300">{formatDate(decision.created_at)}</dd></div><div className="p-4"><dt className="text-[9px] uppercase tracking-wider text-slate-600">Events</dt><dd className="mt-1.5 font-mono text-xs text-slate-300">{decision.event_count}</dd></div><div className="p-4"><dt className="text-[9px] uppercase tracking-wider text-slate-600">Evidence records</dt><dd className="mt-1.5 font-mono text-xs text-slate-300">{report.evidence.length}</dd></div><div className="p-4"><dt className="text-[9px] uppercase tracking-wider text-slate-600">Policy evaluations</dt><dd className="mt-1.5 font-mono text-xs text-slate-300">{report.policies.filter((item) => item.evaluation).length}</dd></div></dl>
      </section>

      <section className="mb-5 border border-line bg-panel px-4 py-4 sm:px-5"><h2 className="mb-2 text-[10px] font-medium uppercase tracking-wider text-slate-500">Executive summary</h2><p className="text-sm leading-6 text-slate-200">{report.executive_summary}</p></section>

      {report.final_outcome && <section className="mb-6 border border-accent/20 bg-accent/[0.035] px-4 py-4 sm:px-5"><div className="flex items-start gap-3"><ShieldCheck size={16} className="mt-0.5 shrink-0 text-accent" /><div><p className="text-[9px] uppercase tracking-wider text-slate-500">Final recorded outcome · {readable(report.final_outcome.source)}</p><p className="mt-1 text-lg font-semibold text-slate-100">{readable(report.final_outcome.value)}</p><p className="mt-1 text-[11px] leading-5 text-slate-400">{report.final_outcome.description}</p></div></div></section>}

      <div className="grid items-start gap-5 xl:grid-cols-[minmax(0,1.35fr)_minmax(300px,0.85fr)]">
        <Section title="Decision lifecycle" icon={Clock3}>
          {report.events.length ? <ol className="ml-2 border-l border-line">{report.events.slice().sort((a, b) => a.sequence - b.sequence).map((event) => <li key={event.id} className="relative pb-4 pl-5 last:pb-0"><span className="absolute -left-[4px] top-1.5 h-2 w-2 rounded-full border border-accent/50 bg-panel" /><details className="group"><summary className="flex cursor-pointer list-none flex-wrap items-start justify-between gap-2 outline-none"><span><span className="font-mono text-[9px] text-slate-600">#{event.sequence}</span><span className="ml-2 text-xs font-medium text-slate-200">{readable(event.event_type)}</span><span className="mt-1 block text-[10px] text-slate-500">{formatDate(event.timestamp)} · {event.actor}</span></span><ChevronDown size={13} className="mt-1 text-slate-600 transition-transform group-open:rotate-180" /></summary><pre className="mt-3 max-h-72 overflow-auto border border-line bg-shell p-3 font-mono text-[10px] leading-5 text-slate-400">{JSON.stringify(event.payload, null, 2)}</pre></details></li>)}</ol> : <p className="text-[11px] text-slate-500">No detailed event timeline is available in this development report.</p>}
        </Section>

        <div className="space-y-5">
          <Section title="Evidence" icon={FileSearch}>
            {report.evidence.length ? <ul className="space-y-3">{report.evidence.map((item) => <li key={item.id} className="border-b border-line pb-3 last:border-0 last:pb-0"><Link to={`/evidence/${item.id}`} className="text-xs font-medium text-blue-200/90 hover:text-blue-100">{item.title}</Link><p className="mt-1 break-all font-mono text-[9px] text-slate-600">{item.id}</p><p className="mt-1 text-[10px] text-slate-400">{readable(item.evidence_type)} · {item.source}</p><p className="mt-1 text-[9px] text-slate-600">Relationship: linked to this decision{item.hash && <> · hash <span className="font-mono" title={item.hash}>{truncateHash(item.hash)}</span></>}</p></li>)}</ul> : <p className="text-[11px] text-slate-500">No evidence is linked in the available report fixtures.</p>}
          </Section>

          <Section title="Policies" icon={Scale}>
            {report.policies.length ? <ul className="space-y-4">{report.policies.map(({ policy, evaluation }) => <li key={policy.id} className="border-b border-line pb-4 last:border-0 last:pb-0"><Link to={`/policies/${policy.id}`} className="text-xs font-medium text-blue-200/90 hover:text-blue-100">{policy.name}</Link><p className="mt-1 break-all font-mono text-[9px] text-slate-600">{policy.id}</p><p className="mt-1 text-[10px] text-slate-500">Version {evaluation?.policy_version ?? policy.version} · <Badge value={policy.status} /></p>{evaluation ? <div className="mt-2"><div className="flex flex-wrap items-center gap-2"><Badge value={evaluation.result} /><span className="text-[9px] text-slate-600">Evaluated {formatDate(evaluation.evaluated_at)}</span></div><p className="mt-2 text-[10px] leading-4 text-slate-400">{evaluation.summary}</p></div> : <p className="mt-2 text-[10px] text-slate-500">No evaluation recorded.</p>}</li>)}</ul> : <p className="text-[11px] text-slate-500">No policy records are associated with this report.</p>}
          </Section>

          <Section title="Human review" icon={ShieldCheck}>
            {report.reviews.length ? <ol className="space-y-3">{report.reviews.map((review) => <li key={review.id} className="border-b border-line pb-3 last:border-0 last:pb-0"><div className="flex flex-wrap items-center justify-between gap-2"><Badge value={review.action} /><span className="text-[9px] text-slate-600">{formatDate(review.created_at)}</span></div><p className="mt-2 text-[10px] text-slate-500">Reviewer <span className="font-mono text-slate-300">{review.reviewer}</span></p><p className="mt-1 text-[10px] leading-4 text-slate-400">{review.comment ?? 'No comment recorded.'}</p></li>)}</ol> : <p className="text-[11px] text-slate-500">No human review recorded.</p>}
          </Section>

          <Section title="Integrity" icon={Fingerprint}>
            <p className="mb-3 border border-amber-400/15 bg-amber-400/[0.035] px-3 py-2 text-[9px] leading-4 text-amber-200/80">Development fixture information. The frontend does not independently perform cryptographic verification.</p>
            {report.integrity ? <><div className="mb-3 flex items-center justify-between gap-2"><span className="text-[10px] text-slate-500">Chain status</span><Badge value={report.integrity.chain_status} /></div><dl className="grid grid-cols-2 gap-3"><div><dt className="text-[9px] uppercase tracking-wider text-slate-600">Event count</dt><dd className="mt-1 font-mono text-xs text-slate-300">{report.integrity.event_count}</dd></div><div><dt className="text-[9px] uppercase tracking-wider text-slate-600">Events hashed</dt><dd className="mt-1 font-mono text-xs text-slate-300">{report.integrity.events_hashed}</dd></div><div><dt className="text-[9px] uppercase tracking-wider text-slate-600">Algorithm</dt><dd className="mt-1 font-mono text-[10px] text-slate-400">{report.integrity.hash_algorithm ?? '—'}</dd></div><div><dt className="text-[9px] uppercase tracking-wider text-slate-600">Verification status</dt><dd className="mt-1"><Badge value={report.integrity.verification_status} /></dd></div></dl><div className="mt-3"><p className="text-[9px] uppercase tracking-wider text-slate-600">Root hash</p><p className="mt-1 break-all font-mono text-[9px] text-slate-400" title={report.integrity.root_hash ?? undefined}>{report.integrity.root_hash ?? '—'}</p></div></> : <p className="text-[11px] text-slate-500">Integrity information is unavailable for this decision in the current fixtures.</p>}
          </Section>
        </div>
      </div>
    </>
  );
}

export default function AuditReportDetailPage() {
  const { decisionId = '' } = useParams<{ decisionId: string }>();
  const [report, setReport] = useState<AuditReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    getAuditReport(decisionId).then((item) => { if (active) setReport(item); })
      .catch((cause: unknown) => { if (active) setError(cause instanceof Error ? cause.message : 'Could not load this audit report.'); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [decisionId]);

  if (loading) return <div role="status" className="flex items-center gap-3 border border-line bg-panel px-5 py-8 text-sm text-slate-400"><LoaderCircle size={16} className="animate-spin text-accent" />Loading audit report…</div>;
  if (error) return <div role="alert" className="border border-rose-400/20 bg-panel px-5 py-6"><p className="text-sm text-rose-300">Could not load audit report</p><p className="mt-1 text-xs text-slate-500">{error}</p><Link to="/audit-reports" className="mt-4 inline-flex items-center gap-2 text-xs text-slate-300"><ArrowLeft size={13} />Back to reports</Link></div>;
  if (!report) return <div className="border border-line bg-panel px-6 py-10 text-center"><p className="font-mono text-[10px] uppercase tracking-wider text-slate-500">404 / REPORT_NOT_FOUND</p><h1 className="mt-2 text-lg font-semibold text-slate-100">Audit report not found</h1><p className="mt-2 text-xs text-slate-500">No report is available for this decision in the current development fixtures.</p><Link to="/audit-reports" className="mt-5 inline-flex items-center gap-2 border border-line px-3 py-2 text-xs text-slate-300 hover:text-white"><ArrowLeft size={13} />Back to audit reports</Link></div>;
  return <ReportBody report={report} />;
}
