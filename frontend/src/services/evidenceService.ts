import { mockEvidence } from '../mock/evidence';
import { mockDecisions } from '../mock/decisions';
import type { Evidence, LinkedDecision } from '../types/evidence';

function withLinkedDecisions(evidence: Evidence): Evidence {
  const linkedDecisions: LinkedDecision[] = evidence.linked_decision_ids.flatMap((id) => {
    const decision = mockDecisions.find((item) => item.id === id);
    return decision
      ? [{
          id: decision.id,
          agent_id: decision.agent_id,
          status: decision.status,
          created_at: decision.created_at,
        }]
      : [];
  });

  return {
    ...evidence,
    metadata: { ...evidence.metadata },
    linked_decision_ids: [...evidence.linked_decision_ids],
    linked_decisions: linkedDecisions,
  };
}

/**
 * Evidence data boundary for the explorer and detail view.
 * Replace these mock implementations with GET /api/v1/evidence and
 * GET /api/v1/evidence/{evidence_id} when backend integration is ready.
 */
export async function getEvidence(): Promise<Evidence[]> {
  return Promise.resolve(mockEvidence.map(withLinkedDecisions));
}

export async function getEvidenceById(evidenceId: string): Promise<Evidence | null> {
  const evidence = mockEvidence.find((item) => item.id === evidenceId);
  return Promise.resolve(evidence ? withLinkedDecisions(evidence) : null);
}
