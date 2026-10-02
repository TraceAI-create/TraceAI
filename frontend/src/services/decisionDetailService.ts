import { mockDecisionDetails } from '../mock/decisionDetails';
import type { DecisionDetail } from '../types/decisionDetail';

/**
 * Decision detail data boundary for the audit view.
 * Replace this mock implementation with GET /api/v1/decisions/{decision_id} later.
 */
export async function getDecisionDetail(decisionId: string): Promise<DecisionDetail | null> {
  return Promise.resolve(mockDecisionDetails[decisionId] ?? null);
}
