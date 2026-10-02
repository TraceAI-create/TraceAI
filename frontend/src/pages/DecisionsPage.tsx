import { Layers3 } from 'lucide-react';
import PageHeader from '../components/PageHeader';
import PlaceholderPanel from '../components/PlaceholderPanel';

export default function DecisionsPage() {
  return (
    <>
      <PageHeader title="Decisions" description="Browse recorded AI decision sessions and open an audit trail to inspect its inputs, events, evidence, and reviews." />
      <PlaceholderPanel title="Decision register" description="No backend data is connected in this foundation step. The decision list, filtering, and pagination will be implemented with API integration." icon={<Layers3 size={17} />} />
    </>
  );
}
