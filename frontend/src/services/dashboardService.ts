import { getDecisions } from './decisionService';
import { getEvidence } from './evidenceService';
import { getEvaluationsForDecision } from './policyService';
import { getReviewsForDecision } from './reviewService';
import { getIntegrityForDecision } from './integrityService';
import type { Decision } from '../types/decision';

export interface DashboardData {
  decisions: Decision[];
  evidenceCount: number;
  policyEvaluationCount: number;
  decisionsWithReviewHistory: number;
  decisionsWithoutReviewHistory: number;
  integrityAvailableCount: number;
  intactChainCount: number;
  warningChainCount: number;
  integrityUnavailableCount: number;
}

/** Aggregates existing mock-backed services; no dashboard-specific fixtures are introduced. */
export async function getDashboardData(): Promise<DashboardData> {
  const [decisions, evidence] = await Promise.all([getDecisions(), getEvidence()]);
  const perDecision = await Promise.all(decisions.map(async (decision) => {
    const [evaluations, reviews, integrity] = await Promise.all([
      getEvaluationsForDecision(decision.id),
      getReviewsForDecision(decision.id),
      getIntegrityForDecision(decision.id),
    ]);
    return { evaluations, hasReviews: reviews.length > 0, integrity };
  }));

  const integrityRecords = perDecision.flatMap((item) => item.integrity ? [item.integrity] : []);
  return {
    decisions: decisions.slice().sort((left, right) => right.created_at.localeCompare(left.created_at)),
    evidenceCount: evidence.length,
    policyEvaluationCount: perDecision.reduce((sum, item) => sum + item.evaluations.length, 0),
    decisionsWithReviewHistory: perDecision.filter((item) => item.hasReviews).length,
    decisionsWithoutReviewHistory: perDecision.filter((item) => !item.hasReviews).length,
    integrityAvailableCount: integrityRecords.length,
    intactChainCount: integrityRecords.filter((item) => item.chain_status === 'CHAIN_INTACT').length,
    warningChainCount: integrityRecords.filter((item) => item.chain_status === 'CHAIN_WARNING').length,
    integrityUnavailableCount: decisions.length - integrityRecords.length,
  };
}
