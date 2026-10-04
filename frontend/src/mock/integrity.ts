import { mockDecisionDetails } from './decisionDetails';
import type { IntegrityEvent, IntegrityInfo } from '../types/integrity';

// These are fictional audit-system fixtures. The frontend does not calculate these hashes.
const claimDetail = mockDecisionDetails['d3a6f291-7c4b-4d18-a21e-8b5d109a642f'];
const claimEvents: IntegrityEvent[] = claimDetail.events.map((event) => ({
  event_id: event.id,
  sequence: event.sequence,
  event_type: event.event_type,
  hash: event.hash,
  previous_hash: event.previous_hash,
}));

const rejectedClaimEvents: IntegrityEvent[] = [
  { event_id: 'integrity-claim-reject-001', sequence: 1, event_type: 'INPUT_RECEIVED', hash: 'a10c4e7b2d9f6035a10c4e7b2d9f6035a10c4e7b2d9f6035a10c4e7b2d9f6035', previous_hash: null },
  { event_id: 'integrity-claim-reject-002', sequence: 2, event_type: 'EVIDENCE_RETRIEVED', hash: 'b21d5f8c3a0e7146b21d5f8c3a0e7146b21d5f8c3a0e7146b21d5f8c3a0e7146', previous_hash: 'a10c4e7b2d9f6035a10c4e7b2d9f6035a10c4e7b2d9f6035a10c4e7b2d9f6035' },
  { event_id: 'integrity-claim-reject-003', sequence: 3, event_type: 'POLICY_EVALUATED', hash: 'c32e6a9d4b1f8257c32e6a9d4b1f8257c32e6a9d4b1f8257c32e6a9d4b1f8257', previous_hash: 'b21d5f8c3a0e7146b21d5f8c3a0e7146b21d5f8c3a0e7146b21d5f8c3a0e7146' },
  { event_id: 'integrity-claim-reject-004', sequence: 4, event_type: 'HUMAN_REVIEW_REJECTED', hash: 'd43f7b0e5c2a9368d43f7b0e5c2a9368d43f7b0e5c2a9368d43f7b0e5c2a9368', previous_hash: 'c32e6a9d4b1f8257c32e6a9d4b1f8257c32e6a9d4b1f8257c32e6a9d4b1f8257' },
];

const riskEvents: IntegrityEvent[] = [
  { event_id: 'integrity-risk-001', sequence: 1, event_type: 'DECISION_CREATED', hash: 'e54a8c1f6d3b0479e54a8c1f6d3b0479e54a8c1f6d3b0479e54a8c1f6d3b0479', previous_hash: null },
  { event_id: 'integrity-risk-002', sequence: 2, event_type: 'POLICY_EVALUATION', hash: 'f65b9d2a7e4c1580f65b9d2a7e4c1580f65b9d2a7e4c1580f65b9d2a7e4c1580', previous_hash: 'e54a8c1f6d3b0479e54a8c1f6d3b0479e54a8c1f6d3b0479e54a8c1f6d3b0479' },
  { event_id: 'integrity-risk-003', sequence: 3, event_type: 'DECISION_MADE', hash: '076cad3b8f5e2691076cad3b8f5e2691076cad3b8f5e2691076cad3b8f5e2691', previous_hash: 'f65b9d2a7e4c1580f65b9d2a7e4c1580f65b9d2a7e4c1580f65b9d2a7e4c1580' },
];

const refundEvents: IntegrityEvent[] = [
  { event_id: 'integrity-refund-001', sequence: 1, event_type: 'DECISION_CREATED', hash: '187dbe4c9a603f52187dbe4c9a603f52187dbe4c9a603f52187dbe4c9a603f52', previous_hash: null },
  { event_id: 'integrity-refund-002', sequence: 2, event_type: 'POLICY_EVALUATION', hash: '298ecf5dab714063298ecf5dab714063298ecf5dab714063298ecf5dab714063', previous_hash: '187dbe4c9a603f52187dbe4c9a603f52187dbe4c9a603f52187dbe4c9a603f52' },
  { event_id: 'integrity-refund-003', sequence: 3, event_type: 'DECISION_MADE', hash: '3a9fd06ebc8251743a9fd06ebc8251743a9fd06ebc8251743a9fd06ebc825174', previous_hash: '298ecf5dab714063298ecf5dab714063298ecf5dab714063298ecf5dab714063' },
  { event_id: 'integrity-refund-004', sequence: 4, event_type: 'HUMAN_REVIEW_REQUESTED', hash: '4ba0e17fcd9362854ba0e17fcd9362854ba0e17fcd9362854ba0e17fcd936285', previous_hash: '3a9fd06ebc8251743a9fd06ebc8251743a9fd06ebc8251743a9fd06ebc825174' },
];

export const mockIntegrity: IntegrityInfo[] = [
  {
    decision_id: claimDetail.id,
    root_hash: claimDetail.root_hash,
    event_count: claimDetail.event_count,
    events_hashed: claimEvents.length,
    hash_algorithm: 'SHA-256',
    chain_status: 'CHAIN_INTACT',
    verification_status: 'VERIFICATION_AVAILABLE',
    last_verified_at: null,
    events: claimEvents,
  },
  {
    decision_id: 'bc2910f4-6a83-4f51-9e27-1d4a7c50b386',
    root_hash: rejectedClaimEvents[rejectedClaimEvents.length - 1].hash,
    event_count: 18,
    events_hashed: rejectedClaimEvents.length,
    hash_algorithm: 'SHA-256',
    chain_status: 'CHAIN_WARNING',
    verification_status: 'NOT_VERIFIED',
    last_verified_at: null,
    events: rejectedClaimEvents,
  },
  {
    decision_id: '7f4b2c91-08d3-4a65-b917-52e1f0c83d46',
    root_hash: riskEvents[riskEvents.length - 1].hash,
    event_count: 21,
    events_hashed: riskEvents.length,
    hash_algorithm: 'SHA-256',
    chain_status: 'CHAIN_WARNING',
    verification_status: 'NOT_VERIFIED',
    last_verified_at: null,
    events: riskEvents,
  },
  {
    decision_id: 'ef06b1d8-3a72-45c9-bf14-6d2e8a50c731',
    root_hash: refundEvents[refundEvents.length - 1].hash,
    event_count: 4,
    events_hashed: refundEvents.length,
    hash_algorithm: 'SHA-256',
    chain_status: 'CHAIN_INTACT',
    verification_status: 'NOT_VERIFIED',
    last_verified_at: null,
    events: refundEvents,
  },
];
