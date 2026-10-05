import { api } from './apiClient';
import type { Decision } from '../types/decision';

interface BackendDecision {
  id: string;
  agent_id: string;
  agent_version: string;
  status: string;
  created_at: string;
  root_hash: string | null;
  event_count: number;
}

function toDecision(d: BackendDecision): Decision {
  return {
    id: d.id,
    agent_id: d.agent_id,
    agent_version: d.agent_version,
    status: d.status,
    created_at: d.created_at,
    root_hash: d.root_hash,
    event_count: d.event_count ?? 0,
  };
}

export async function getDecisions(): Promise<Decision[]> {
  const results = await api.get<BackendDecision[]>('/decisions?limit=100');
  return results.map(toDecision);
}
