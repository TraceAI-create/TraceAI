import { Fingerprint } from 'lucide-react';
import PageHeader from '../components/PageHeader';
import PlaceholderPanel from '../components/PlaceholderPanel';

export default function AuditReportsPage() {
  return <><PageHeader title="Audit reports" description="Generate and inspect a consolidated report of decision events, evidence, replay results, reviews, and cryptographic verification." /><PlaceholderPanel title="Report center" description="JSON and Markdown audit report retrieval will be added when the frontend is connected to the backend." icon={<Fingerprint size={17} />} /></>;
}
