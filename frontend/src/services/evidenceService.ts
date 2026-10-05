import { api } from './apiClient';
import type { Evidence } from '../types/evidence';

interface BackendEvidence {
  id: string;
  type: string;
  content_hash: string;
  storage_uri: string;
  metadata_json: Record<string, unknown>;
  created_at: string;
}

function toEvidence(e: BackendEvidence): Evidence {
  return {
    id: e.id,
    // Map backend `type` → frontend `evidence_type`
    evidence_type: e.type,
    title: e.metadata_json?.['title'] as string ?? e.type.replace(/_/g, ' '),
    source: e.metadata_json?.['source'] as string ?? 'TraceAI Evidence Store',
    source_reference: e.storage_uri,
    // Content is not returned in list — use content hash as placeholder
    content: e.content_hash,
    excerpt: null,
    created_at: e.created_at,
    retrieved_at: null,
    // Map backend `content_hash` → frontend `hash`
    hash: e.content_hash,
    metadata: e.metadata_json ?? {},
    linked_decision_ids: [],
    linked_decisions: [],
  };
}

export async function getEvidence(): Promise<Evidence[]> {
  const results = await api.get<BackendEvidence[]>('/evidence?limit=100');
  return results.map(toEvidence);
}

export async function getEvidenceById(evidenceId: string): Promise<Evidence | null> {
  try {
    const e = await api.get<BackendEvidence>(`/evidence/${evidenceId}`);
    return toEvidence(e);
  } catch {
    return null;
  }
}
