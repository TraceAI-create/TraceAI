import { mockDecisions } from '../mock/decisions';
import type { Decision } from '../types/decision';

/**
 * Decision data boundary for the register.
 * Replace this mock implementation with GET /api/v1/decisions when API access is ready.
 */
export async function getDecisions(): Promise<Decision[]> {
  return Promise.resolve(mockDecisions.map((decision) => ({ ...decision })));
}
