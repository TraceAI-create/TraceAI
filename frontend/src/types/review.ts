export type ReviewActionKind = 'APPROVED' | 'REJECTED' | 'OVERRIDDEN' | 'REQUESTED_REVIEW';

export interface ReviewAction {
  id: string;
  decision_id: string;
  reviewer: string;
  action: string;
  comment: string | null;
  created_at: string;
}
