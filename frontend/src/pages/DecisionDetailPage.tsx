import { useParams } from 'react-router-dom';
import { GitBranch } from 'lucide-react';
import PageHeader from '../components/PageHeader';
import PlaceholderPanel from '../components/PlaceholderPanel';

export default function DecisionDetailPage() {
  const { decisionId } = useParams<{ decisionId: string }>();
  return (
    <>
      <PageHeader eyebrow="Decisions / Detail" title="Decision audit trail" description="Follow the recorded execution from input and context through evidence, reasoning, actions, outcome, and integrity." />
      <div className="mb-5 border border-line bg-panel px-4 py-3">
        <p className="text-[10px] uppercase tracking-wider text-slate-500">Decision identifier</p>
        <p className="mt-1 break-all font-mono text-xs text-slate-300">{decisionId}</p>
      </div>
      <PlaceholderPanel title="Audit timeline" description="Decision details and event timeline will load here after connecting the existing FastAPI endpoints." icon={<GitBranch size={17} />} />
    </>
  );
}
