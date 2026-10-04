import { mockDecisionDetails } from './decisionDetails';
import { mockDecisions } from './decisions';
import { mockEvidence } from './evidence';
import { mockIntegrity } from './integrity';
import { mockPolicies, mockPolicyEvaluations } from './policies';
import { mockReviews } from './reviews';
import type { AuditEvent } from '../types/decisionDetail';
import type { AuditReport } from '../types/auditReport';

// Consolidated fictional fixtures assembled from the existing frontend mock records.
const rejectedClaimId = 'bc2910f4-6a83-4f51-9e27-1d4a7c50b386';
const rejectedClaimEvents: AuditEvent[] = [
  {
    id: 'report-bc291-event-001',
    event_type: 'INPUT_RECEIVED',
    timestamp: '2025-02-17T17:16:53Z',
    sequence: 1,
    actor: 'claims-review-agent',
    payload: { claim_reference: 'CLM-DEMO-1982', requested_amount: 3180, currency: 'USD' },
    hash: 'a10c4e7b2d9f6035a10c4e7b2d9f6035a10c4e7b2d9f6035a10c4e7b2d9f6035',
    previous_hash: null,
  },
  {
    id: 'report-bc291-event-002',
    event_type: 'POLICY_EVALUATED',
    timestamp: '2025-02-17T17:17:04Z',
    sequence: 2,
    actor: 'policy-engine',
    payload: { policy_id: 'policy-demo-claims-2025-1', policy_version: '2025.1', result: 'FAILED', reason: 'Requested amount exceeded the automatic review threshold.' },
    hash: 'b21d5f8c3a0e7146b21d5f8c3a0e7146b21d5f8c3a0e7146b21d5f8c3a0e7146',
    previous_hash: 'a10c4e7b2d9f6035a10c4e7b2d9f6035a10c4e7b2d9f6035a10c4e7b2d9f6035',
  },
  {
    id: 'report-bc291-event-003',
    event_type: 'DECISION_MADE',
    timestamp: '2025-02-17T17:17:06Z',
    sequence: 3,
    actor: 'claims-review-agent',
    payload: { decision: 'reject_claim', rationale: 'The submitted claim exceeded the covered limit.' },
    hash: 'c32e6a9d4b1f8257c32e6a9d4b1f8257c32e6a9d4b1f8257c32e6a9d4b1f8257',
    previous_hash: 'b21d5f8c3a0e7146b21d5f8c3a0e7146b21d5f8c3a0e7146b21d5f8c3a0e7146',
  },
];

const detailEvents: Record<string, AuditEvent[]> = Object.fromEntries(
  Object.values(mockDecisionDetails).map((detail) => [detail.id, detail.events]),
);

export const mockAuditReports: Record<string, AuditReport> = Object.fromEntries(
  mockDecisions
    .filter((decision) => [
      'd3a6f291-7c4b-4d18-a21e-8b5d109a642f',
      'a1e9c462-5b37-49d0-8f24-3c6d72a519be',
      rejectedClaimId,
    ].includes(decision.id))
    .map((decision) => {
      const decisionId = decision.id;
      const evaluations = mockPolicyEvaluations.filter((item) => item.decision_id === decisionId);
      const linkedPolicies = evaluations.flatMap((evaluation) => {
        const policy = mockPolicies.find((item) => item.id === evaluation.policy_id);
        return policy ? [{ policy, evaluation }] : [];
      });
      const reviews = mockReviews
        .filter((item) => item.decision_id === decisionId)
        .slice()
        .sort((left, right) => right.created_at.localeCompare(left.created_at));
      const integrity = mockIntegrity.find((item) => item.decision_id === decisionId) ?? null;
      const events = (decisionId === rejectedClaimId
        ? rejectedClaimEvents
        : detailEvents[decisionId] ?? []).map((event) => {
          const integrityEvent = integrity?.events.find((item) => item.sequence === event.sequence);
          return integrityEvent
            ? { ...event, hash: integrityEvent.hash, previous_hash: integrityEvent.previous_hash }
            : event;
        });
      const evidence = mockEvidence.filter((item) => item.linked_decision_ids.includes(decisionId));
      const latestReview = reviews[0];
      const recordedDecisionOutcome = decision.status.toUpperCase();

      return [decisionId, {
        decision: { ...decision },
        executive_summary: decisionId === 'd3a6f291-7c4b-4d18-a21e-8b5d109a642f'
          ? 'The claims-review agent approved the equipment damage claim for human sign-off after the itemized repair invoice and active coverage policy passed the recorded checks.'
          : decisionId === rejectedClaimId
            ? 'The claims-review agent rejected the claim after the recorded request exceeded the applicable covered limit. A reviewer subsequently recorded a rejection.'
            : 'The support-triage agent routed the account-access request to account recovery. No human review is recorded in the available development fixtures.',
        events,
        evidence,
        policies: linkedPolicies,
        reviews,
        integrity: integrity ? { ...integrity, events: integrity.events.map((event) => ({ ...event })) } : null,
        final_outcome: {
          value: latestReview?.action === 'OVERRIDDEN' ? latestReview.action : recordedDecisionOutcome,
          source: latestReview?.action === 'OVERRIDDEN' ? 'HUMAN_OVERRIDE' as const : 'RECORDED_DECISION' as const,
          description: latestReview?.action === 'OVERRIDDEN'
            ? 'A human reviewer recorded an override after the original decision.'
            : 'Outcome shown from the recorded decision status; no additional business logic is inferred.',
        },
      } satisfies AuditReport];
    }),
);
