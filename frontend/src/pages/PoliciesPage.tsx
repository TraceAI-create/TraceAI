import { Scale } from 'lucide-react';
import PageHeader from '../components/PageHeader';
import PlaceholderPanel from '../components/PlaceholderPanel';

export default function PoliciesPage() {
  return <><PageHeader title="Policies" description="Inspect governance policy definitions, effective periods, and recorded evaluation outcomes." /><PlaceholderPanel title="Policy library" description="The policy list and evaluation workflow will be connected to the backend in a later step." icon={<Scale size={17} />} /></>;
}
