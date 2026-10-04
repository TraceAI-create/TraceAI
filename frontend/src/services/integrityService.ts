import { mockIntegrity } from '../mock/integrity';
import type { IntegrityInfo } from '../types/integrity';

/** Returns fixture data only; no cryptographic verification is performed here. */
export async function getIntegrityForDecision(decisionId: string): Promise<IntegrityInfo | null> {
  const integrity = mockIntegrity.find((item) => item.decision_id === decisionId);
  return Promise.resolve(integrity ? { ...integrity, events: integrity.events.map((event) => ({ ...event })) } : null);
}
