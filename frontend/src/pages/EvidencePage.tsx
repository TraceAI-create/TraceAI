import { Archive } from 'lucide-react';
import PageHeader from '../components/PageHeader';
import PlaceholderPanel from '../components/PlaceholderPanel';

export default function EvidencePage() {
  return <><PageHeader title="Evidence" description="Review evidence artifacts and how they support recorded AI decisions." /><PlaceholderPanel title="Evidence inventory" description="Evidence metadata, content hashes, and decision links will be shown here once API integration is added." icon={<Archive size={17} />} /></>;
}
