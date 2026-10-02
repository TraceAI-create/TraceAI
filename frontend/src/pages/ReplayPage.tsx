import { FileSearch } from 'lucide-react';
import PageHeader from '../components/PageHeader';
import PlaceholderPanel from '../components/PlaceholderPanel';

export default function ReplayPage() {
  return <><PageHeader title="Replay" description="Compare a recorded decision with a deterministic replay or a what-if simulation." /><PlaceholderPanel title="Replay comparison" description="Replay controls, event differences, and similarity details will be available after backend integration." icon={<FileSearch size={17} />} /></>;
}
