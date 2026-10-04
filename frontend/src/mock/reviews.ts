import type { ReviewAction } from '../types/review';

// Fictional review history for local development; these actions are not backend records.
export const mockReviews: ReviewAction[] = [
  {
    id: 'review-demo-claims-001',
    decision_id: 'd3a6f291-7c4b-4d18-a21e-8b5d109a642f',
    reviewer: 'reviewer-demo-17',
    action: 'REQUESTED_REVIEW',
    comment: 'Please confirm the repair invoice is itemized and within the active coverage limit.',
    created_at: '2025-02-18T14:48:12Z',
  },
  {
    id: 'review-demo-claims-002',
    decision_id: 'd3a6f291-7c4b-4d18-a21e-8b5d109a642f',
    reviewer: 'reviewer-demo-17',
    action: 'APPROVED',
    comment: 'Supporting documentation reviewed; the claim is within the policy limit.',
    created_at: '2025-02-18T15:04:32Z',
  },
  {
    id: 'review-demo-claims-003',
    decision_id: 'bc2910f4-6a83-4f51-9e27-1d4a7c50b386',
    reviewer: 'reviewer-demo-04',
    action: 'REJECTED',
    comment: 'The submitted amount exceeds the covered limit and no exception evidence was supplied.',
    created_at: '2025-02-17T17:28:10Z',
  },
  {
    id: 'review-demo-risk-004',
    decision_id: 'c7b31e09-2d64-4a85-93f1-0b6e8d42a517',
    reviewer: 'reviewer-demo-02',
    action: 'OVERRIDDEN',
    comment: 'Manual review required because the evidence conflicted with the active policy.',
    created_at: '2025-02-16T10:41:55Z',
  },
  {
    id: 'review-demo-policy-005',
    decision_id: '52d8a6c3-1f94-4b07-ae36-8c5d2f719b40',
    reviewer: 'reviewer-demo-11',
    action: 'REQUESTED_REVIEW',
    comment: 'Please inspect the policy violation details before closing this risk assessment.',
    created_at: '2025-02-17T16:02:34Z',
  },
  {
    id: 'review-demo-support-006',
    decision_id: 'ef06b1d8-3a72-45c9-bf14-6d2e8a50c731',
    reviewer: 'reviewer-demo-08',
    action: 'REJECTED',
    comment: 'The supporting verification signals do not meet the required account-safety threshold.',
    created_at: '2025-02-17T09:51:08Z',
  },
];
