import { ArrowRight, GitBranch, ShieldCheck } from 'lucide-react';
import { Link } from 'react-router-dom';
import PageHeader from '../components/PageHeader';
import PlaceholderPanel from '../components/PlaceholderPanel';

export default function DashboardPage() {
  return (
    <>
      <PageHeader
        eyebrow="Overview / Dashboard"
        title="Decision audit workspace"
        description="A focused view for understanding how an AI agent reached an outcome—from its original input through the evidence and audit trail."
      />
      <div className="mb-6 grid gap-4 lg:grid-cols-3">
        <PlaceholderPanel
          title="Decision activity"
          description="Decision volume and lifecycle summaries will appear here when backend integration is added."
          icon={<GitBranch size={17} strokeWidth={1.7} />}
        />
        <PlaceholderPanel
          title="Integrity status"
          description="Tamper-evidence verification summaries will be available here. No live backend status is shown yet."
          icon={<ShieldCheck size={17} strokeWidth={1.7} />}
        />
        <PlaceholderPanel
          title="Audit workflow"
          description="Inspect a decision to follow its recorded events, linked evidence, and human review."
          icon={<ArrowRight size={17} strokeWidth={1.7} />}
        />
      </div>
      <div className="border border-line bg-panel px-5 py-5 sm:px-6">
        <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
          <div>
            <h2 className="text-sm font-medium text-slate-200">Start with decisions</h2>
            <p className="mt-1 text-[13px] text-muted">The decision register will provide the entry point to each audit trail.</p>
          </div>
          <Link to="/decisions" className="inline-flex w-fit items-center gap-2 border border-line px-3 py-2 text-xs font-medium text-slate-300 hover:border-slate-600 hover:text-white">
            Browse decisions <ArrowRight size={14} />
          </Link>
        </div>
      </div>
    </>
  );
}
