import { useEffect, useMemo, useState, type ReactNode } from 'react';
import {
  ArrowLeft,
  BrainCircuit,
  Check,
  ChevronDown,
  CircleDot,
  ClipboardList,
  Clock3,
  FileSearch,
  Fingerprint,
  LoaderCircle,
  Scale,
  ShieldCheck,
  Sparkles,
  Waypoints,
  type LucideIcon,
} from 'lucide-react';
import { Link, useParams } from 'react-router-dom';
import type { AuditEvent, DecisionDetail } from '../types/decisionDetail';
import type { Policy, PolicyEvaluation } from '../types/policy';
import { getDecisionDetail } from '../services/decisionDetailService';
import { getEvaluationsForDecision, getPolicyById } from '../services/policyService';

const eventPresentation: Record<string, { title: string; description: string; icon: LucideIcon }> = {
  INPUT_RECEIVED: {
    title: 'Input received',
    description: 'The initial request and decision inputs were recorded.',
    icon: ClipboardList,
  },
  CONTEXT_CAPTURED: {
    title: 'Context captured',
    description: 'Relevant context available to the agent was captured.',
    icon: Waypoints,
  },
  EVIDENCE_RETRIEVED: {
    title: 'Evidence retrieved',
    description: 'Supporting material was retrieved and associated with this decision.',
    icon: FileSearch,
  },
  POLICY_EVALUATED: {
    title: 'Policy evaluated',
    description: 'The decision payload was checked against a governance policy.',
    icon: Scale,
  },
  DECISION_MADE: {
    title: 'Decision made',
    description: 'The agent recorded its decision and rationale.',
    icon: BrainCircuit,
  },
  ACTION_EXECUTED: {
    title: 'Action executed',
    description: 'A workflow action was recorded for this decision.',
    icon: Sparkles,
  },
  OUTCOME_RECORDED: {
    title: 'Outcome recorded',
    description: 'The resulting state or next step was recorded.',
    icon: Check,
  },
};

function humanize(value: string): string {
  return value
    .split(/[_\s-]+/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1).toLowerCase())
    .join(' ');
}

function formatTimestamp(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return 'Invalid timestamp';
  return new Intl.DateTimeFormat(undefined, {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  }).format(date);
}

function statusStyle(status: string): string {
  const normalized = status.toLowerCase();
  if (normalized.startsWith('reviewed') || normalized === 'approved' || normalized === 'passed') {
    return 'border-emerald-400/20 bg-emerald-400/[0.08] text-emerald-300';
  }
  if (normalized.includes('reject') || normalized === 'failed') return 'border-rose-400/20 bg-rose-400/[0.08] text-rose-300';
  if (normalized.includes('challeng') || normalized === 'overridden') return 'border-amber-400/20 bg-amber-400/[0.08] text-amber-300';
  if (normalized === 'created' || normalized === 'running') {
    return 'border-sky-400/20 bg-sky-400/[0.08] text-sky-300';
  }
  return 'border-slate-500/25 bg-slate-500/[0.08] text-slate-300';
}

function StatusBadge({ status }: { status: string }) {
  return (
    <span className={`inline-flex border px-2 py-1 text-[10px] font-medium leading-none ${statusStyle(status)}`}>
      {humanize(status)}
    </span>
  );
}

function EventItem({ event, expanded, onToggle }: { event: AuditEvent; expanded: boolean; onToggle: () => void }) {
  const presentation = eventPresentation[event.event_type] ?? {
    title: humanize(event.event_type),
    description: 'An additional audit event was recorded.',
    icon: CircleDot,
  };
  const Icon = presentation.icon;
  const detailsId = `event-details-${event.id}`;

  return (
    <li className="relative pb-5 pl-10 last:pb-0">
      <span className="absolute -left-[17px] top-4 flex h-8 w-8 items-center justify-center border border-line bg-[#0b1017] text-slate-400">
        <Icon size={15} strokeWidth={1.7} />
      </span>
      <article className="border border-line bg-panel">
        <button
          type="button"
          aria-expanded={expanded}
          aria-controls={detailsId}
          onClick={onToggle}
          className="flex w-full items-start justify-between gap-4 px-4 py-3.5 text-left outline-none hover:bg-white/[0.02] focus-visible:ring-1 focus-visible:ring-inset focus-visible:ring-accent/50 sm:px-5"
        >
          <span className="min-w-0">
            <span className="flex flex-wrap items-center gap-x-2 gap-y-1">
              <span className="text-sm font-medium text-slate-200">{presentation.title}</span>
              <span className="font-mono text-[9px] uppercase tracking-wider text-slate-500">{event.event_type}</span>
            </span>
            <span className="mt-1.5 block text-xs leading-5 text-muted">{presentation.description}</span>
            <span className="mt-2.5 flex flex-wrap items-center gap-x-4 gap-y-1 text-[10px] text-slate-500">
              <span className="inline-flex items-center gap-1.5"><Clock3 size={11} />{formatTimestamp(event.timestamp)}</span>
              <span>Actor: <span className="font-mono text-slate-400">{event.actor}</span></span>
            </span>
          </span>
          <span className="flex shrink-0 items-center gap-2 pt-0.5">
            <span className="font-mono text-[10px] text-slate-500">#{event.sequence}</span>
            <ChevronDown size={15} className={`text-slate-500 transition-transform ${expanded ? 'rotate-180' : ''}`} />
          </span>
        </button>
        {expanded && (
          <div id={detailsId} className="border-t border-line px-4 py-4 sm:px-5">
            <div className="mb-2 flex items-center justify-between gap-3">
              <h3 className="text-[10px] font-medium uppercase tracking-wider text-slate-500">Event payload</h3>
              <span className="font-mono text-[9px] text-slate-600">JSON</span>
            </div>
            <pre className="max-h-80 overflow-auto border border-line bg-shell p-3 font-mono text-[10px] leading-5 text-slate-300 sm:text-[11px]">{JSON.stringify(event.payload, null, 2)}</pre>
            <div className="mt-3 grid gap-3 sm:grid-cols-2">
              <HashValue label="Event hash" value={event.hash} />
              <HashValue label="Previous hash" value={event.previous_hash} />
            </div>
          </div>
        )}
      </article>
    </li>
  );
}

function HashValue({ label, value }: { label: string; value: string | null }) {
  return (
    <div className="min-w-0">
      <p className="mb-1 text-[9px] uppercase tracking-wider text-slate-600">{label}</p>
      <p className="break-all font-mono text-[9px] leading-4 text-slate-500">{value ?? '—'}</p>
    </div>
  );
}

function SupportingPanel({ title, icon: Icon, children }: { title: string; icon: LucideIcon; children: ReactNode }) {
  return (
    <section className="border border-line bg-panel">
      <div className="flex items-center gap-2 border-b border-line px-4 py-3">
        <Icon size={14} className="text-slate-500" />
        <h2 className="text-xs font-medium text-slate-300">{title}</h2>
      </div>
      <div className="px-4 py-3.5">{children}</div>
    </section>
  );
}

function DecisionContent({ decision }: { decision: DecisionDetail }) {
  const [expandedEvents, setExpandedEvents] = useState<Set<string>>(() => new Set());
  const [policyEvaluations, setPolicyEvaluations] = useState<Array<{ evaluation: PolicyEvaluation; policy: Policy | null }>>([]);
  const [policyLoading, setPolicyLoading] = useState(true);
  const [policyError, setPolicyError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setPolicyLoading(true);
    setPolicyError(null);
    getEvaluationsForDecision(decision.id)
      .then((evaluations) => Promise.all(evaluations.map(async (evaluation) => ({
        evaluation,
        policy: await getPolicyById(evaluation.policy_id),
      }))))
      .then((items) => { if (active) setPolicyEvaluations(items); })
      .catch((cause: unknown) => { if (active) setPolicyError(cause instanceof Error ? cause.message : 'An unexpected error occurred.'); })
      .finally(() => { if (active) setPolicyLoading(false); });
    return () => { active = false; };
  }, [decision.id]);
  const orderedEvents = useMemo(
    () => [...decision.events].sort((a, b) => a.sequence - b.sequence),
    [decision.events],
  );

  const toggleEvent = (eventId: string) => {
    setExpandedEvents((current) => {
      const next = new Set(current);
      if (next.has(eventId)) next.delete(eventId);
      else next.add(eventId);
      return next;
    });
  };

  return (
    <>
      <div className="mb-6 flex flex-col justify-between gap-4 border-b border-line pb-6 sm:flex-row sm:items-start">
        <div className="min-w-0">
          <p className="mb-2 font-mono text-[10px] uppercase tracking-[0.16em] text-accent/80">Decision / Audit detail</p>
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-xl font-semibold tracking-tight text-slate-100 sm:text-2xl">Decision audit trail</h1>
            <StatusBadge status={decision.status} />
          </div>
          <p className="mt-2 break-all font-mono text-[11px] text-slate-500">{decision.id}</p>
        </div>
      </div>

      <section className="mb-6 border border-line bg-panel">
        <div className="grid grid-cols-2 divide-x divide-y divide-line sm:grid-cols-4 sm:divide-y-0">
          <MetadataItem label="Agent" value={decision.agent_id} />
          <MetadataItem label="Agent version" value={decision.agent_version} mono />
          <MetadataItem label="Created" value={formatTimestamp(decision.created_at)} />
          <MetadataItem label="Event count" value={String(decision.event_count)} mono />
        </div>
      </section>

      <section className="mb-7 border border-line bg-panel px-5 py-5 sm:px-6">
        <div className="mb-3 flex items-center gap-2">
          <BrainCircuit size={15} className="text-accent/80" />
          <h2 className="text-xs font-medium uppercase tracking-wider text-slate-400">Decision summary</h2>
        </div>
        <p className="text-sm leading-6 text-slate-200">{decision.decision_summary}</p>
        <div className="mt-4 flex flex-wrap gap-x-6 gap-y-2 border-t border-line pt-3 text-[11px] text-slate-500">
          <span>Agent <span className="ml-1 font-mono text-slate-300">{decision.agent_id}</span></span>
          <span>Status <span className="ml-1 text-slate-300">{humanize(decision.status)}</span></span>
          <span>Decision time <span className="ml-1 text-slate-300">{formatTimestamp(decision.created_at)}</span></span>
        </div>
      </section>

      <div className="grid items-start gap-6 xl:grid-cols-[minmax(0,1fr)_320px]">
        <section className="min-w-0">
          <div className="mb-4 flex items-end justify-between gap-3">
            <div>
              <p className="mb-1 font-mono text-[9px] uppercase tracking-[0.16em] text-accent/70">Ordered event record</p>
              <h2 className="text-base font-semibold text-slate-100">Audit timeline</h2>
            </div>
            <span className="text-[10px] text-slate-500">{orderedEvents.length} events</span>
          </div>
          {orderedEvents.length > 0 ? (
            <ol className="ml-4 border-l border-line">
              {orderedEvents.map((event) => (
                <EventItem
                  key={event.id}
                  event={event}
                  expanded={expandedEvents.has(event.id)}
                  onToggle={() => toggleEvent(event.id)}
                />
              ))}
            </ol>
          ) : (
            <div className="border border-line bg-panel px-5 py-8 text-sm text-muted">No audit events are available for this decision.</div>
          )}
        </section>

        <aside className="space-y-3">
          <SupportingPanel title="Evidence" icon={FileSearch}>
            {decision.evidence.length ? (
              <ul className="space-y-3">
                {decision.evidence.map((item) => (
                  <li key={item.id} className="min-w-0 border-b border-line/70 pb-3 last:border-0 last:pb-0">
                    <Link to={`/evidence/${item.id}`} className="block outline-none hover:text-blue-200 focus-visible:text-blue-200">
                      <p className="text-xs font-medium text-slate-300">{humanize(item.type)}</p>
                      <p className="mt-1 text-[10px] text-slate-500">Role: {humanize(item.role)}</p>
                      <p className="mt-1 break-all font-mono text-[9px] text-blue-300/70">{item.id}</p>
                    </Link>
                  </li>
                ))}
              </ul>
            ) : <p className="text-[11px] text-slate-500">No evidence linked in this development record.</p>}
            <p className="mt-3 border-t border-line pt-2.5 text-[10px] leading-4 text-slate-600">Evidence details will be connected in a future phase.</p>
          </SupportingPanel>

          <SupportingPanel title="Policy" icon={Scale}>
            {policyLoading ? <p className="text-[11px] text-slate-500">Loading policy evaluations…</p> : policyError ? (
              <p role="alert" className="text-[11px] text-rose-300">Could not load policy evaluations: {policyError}</p>
            ) : policyEvaluations.length ? (
              <ul className="space-y-3">
                {policyEvaluations.map(({ evaluation, policy }) => (
                  <li key={evaluation.id} className="border-b border-line/70 pb-3 last:border-0 last:pb-0">
                    <Link to={`/policies/${evaluation.policy_id}`} className="block outline-none hover:text-blue-200 focus-visible:text-blue-200">
                      <p className="text-xs font-medium text-slate-300">{policy?.name ?? 'Policy record unavailable'}</p>
                      <p className="mt-1 break-all font-mono text-[9px] text-blue-300/70">{evaluation.policy_id}</p>
                      <div className="mt-1 flex items-center justify-between gap-2 text-[10px] text-slate-500">
                        <span>Version {evaluation.policy_version}</span>
                        <StatusBadge status={evaluation.result} />
                      </div>
                      <p className="mt-2 text-[10px] leading-4 text-slate-400">{evaluation.summary}</p>
                    </Link>
                  </li>
                ))}
              </ul>
            ) : <p className="text-[11px] text-slate-500">No policy evaluation recorded.</p>}
          </SupportingPanel>

          <SupportingPanel title="Integrity" icon={Fingerprint}>
            <div className="flex items-center gap-2 text-xs text-slate-300">
              <ShieldCheck size={14} className="text-slate-400" />
              Integrity information available
            </div>
            <p className="mt-2 text-[10px] leading-4 text-slate-600">Displayed hash metadata is mock data. The frontend has not performed cryptographic verification.</p>
            <div className="mt-3 space-y-3 border-t border-line pt-3">
              <HashValue label="Root hash" value={decision.root_hash} />
              <p className="text-[10px] text-slate-500">Recorded events <span className="ml-1 font-mono text-slate-300">{decision.event_count}</span></p>
            </div>
          </SupportingPanel>

          <SupportingPanel title="Human review" icon={ClipboardList}>
            {decision.human_review ? (
              <>
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <StatusBadge status={decision.human_review.action} />
                  <span className="text-[10px] text-slate-500">{formatTimestamp(decision.human_review.created_at)}</span>
                </div>
                <p className="mt-2 text-[10px] text-slate-500">Reviewer <span className="font-mono text-slate-400">{decision.human_review.reviewer_id}</span></p>
                {decision.human_review.comments && <p className="mt-2 text-[11px] leading-5 text-slate-400">{decision.human_review.comments}</p>}
              </>
            ) : <p className="text-[11px] text-slate-500">No review recorded</p>}
          </SupportingPanel>
        </aside>
      </div>
    </>
  );
}

function MetadataItem({ label, value, mono = false }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="min-w-0 px-4 py-3.5 sm:px-5">
      <p className="text-[9px] uppercase tracking-wider text-slate-600">{label}</p>
      <p className={`mt-1.5 truncate text-xs text-slate-300 ${mono ? 'font-mono' : ''}`} title={value}>{value}</p>
    </div>
  );
}

function LoadingState() {
  return (
    <div role="status" className="flex items-center gap-3 border border-line bg-panel px-5 py-8 text-sm text-slate-400">
      <LoaderCircle size={17} className="animate-spin text-accent" /> Loading decision detail…
    </div>
  );
}

function ErrorState({ message }: { message: string }) {
  return (
    <div role="alert" className="border border-rose-400/20 bg-rose-400/[0.04] px-5 py-6">
      <h1 className="text-sm font-medium text-rose-200">Could not load decision</h1>
      <p className="mt-1 text-xs text-slate-400">{message}</p>
      <Link to="/decisions" className="mt-4 inline-flex items-center gap-2 text-xs text-slate-300 hover:text-white"><ArrowLeft size={13} /> Back to decisions</Link>
    </div>
  );
}

function NotFoundState() {
  return (
    <div className="border border-line bg-panel px-6 py-10 text-center">
      <CircleDot size={20} className="mx-auto text-slate-500" />
      <p className="mt-4 font-mono text-[10px] uppercase tracking-[0.16em] text-slate-500">404 / DECISION_NOT_FOUND</p>
      <h1 className="mt-2 text-lg font-semibold text-slate-100">Decision not found</h1>
      <p className="mx-auto mt-2 max-w-md text-xs leading-5 text-muted">This ID is not present in the current development detail records.</p>
      <Link to="/decisions" className="mt-5 inline-flex items-center gap-2 border border-line px-3 py-2 text-xs text-slate-300 hover:border-slate-600 hover:text-white">
        <ArrowLeft size={13} /> Back to decisions
      </Link>
    </div>
  );
}

export default function DecisionDetailPage() {
  const { decisionId = '' } = useParams<{ decisionId: string }>();
  const [decision, setDecision] = useState<DecisionDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    setDecision(null);

    getDecisionDetail(decisionId)
      .then((detail) => {
        if (active) setDecision(detail);
      })
      .catch((cause: unknown) => {
        if (active) setError(cause instanceof Error ? cause.message : 'An unexpected error occurred.');
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [decisionId]);

  return (
    <>
      <div className="mb-5 flex items-center justify-between gap-3">
        <Link to="/decisions" className="inline-flex items-center gap-2 text-xs text-slate-400 hover:text-slate-100">
          <ArrowLeft size={14} /> Back to decisions
        </Link>
        <span className="inline-flex items-center gap-1.5 text-[9px] uppercase tracking-wider text-amber-300/80">
          <span className="h-1.5 w-1.5 rounded-full bg-amber-400" /> Development mock data
        </span>
      </div>
      {loading ? <LoadingState /> : error ? <ErrorState message={error} /> : decision ? <DecisionContent key={decision.id} decision={decision} /> : <NotFoundState />}
    </>
  );
}
