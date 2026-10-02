import {
  Activity,
  Archive,
  FileSearch,
  Fingerprint,
  Layers3,
  Scale,
  type LucideIcon,
} from 'lucide-react';

export interface NavigationItem {
  label: string;
  to: string;
  icon: LucideIcon;
  end?: boolean;
}

export interface NavigationGroup {
  label: string;
  items: NavigationItem[];
}

export const navigationGroups: NavigationGroup[] = [
  {
    label: 'Overview',
    items: [
      { label: 'Dashboard', to: '/dashboard', icon: Activity, end: true },
      { label: 'Decisions', to: '/decisions', icon: Layers3 },
    ],
  },
  {
    label: 'Audit',
    items: [
      { label: 'Evidence', to: '/evidence', icon: Archive },
      { label: 'Policies', to: '/policies', icon: Scale },
      { label: 'Replay', to: '/replay', icon: FileSearch },
    ],
  },
  {
    label: 'System',
    items: [{ label: 'Audit Reports', to: '/audit-reports', icon: Fingerprint }],
  },
];
