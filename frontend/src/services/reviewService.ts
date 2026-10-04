import { mockReviews } from '../mock/reviews';
import type { ReviewAction, ReviewActionKind } from '../types/review';

let generatedReviewNumber = 1;

function copyReview(review: ReviewAction): ReviewAction {
  return { ...review };
}

export async function getReviewsForDecision(decisionId: string): Promise<ReviewAction[]> {
  return Promise.resolve(
    mockReviews
      .filter((review) => review.decision_id === decisionId)
      .sort((a, b) => b.created_at.localeCompare(a.created_at))
      .map(copyReview),
  );
}

export async function getReviewById(reviewId: string): Promise<ReviewAction | null> {
  const review = mockReviews.find((item) => item.id === reviewId);
  return Promise.resolve(review ? copyReview(review) : null);
}

/** Adds an in-memory development review; it is not persisted to the backend. */
export async function submitMockReview(input: {
  decision_id: string;
  action: ReviewActionKind;
  comment: string | null;
}): Promise<ReviewAction> {
  if (!input.decision_id) throw new Error('A decision is required for a review.');
  if ((input.action === 'REJECTED' || input.action === 'OVERRIDDEN') && !input.comment?.trim()) {
    throw new Error('A comment is required for a rejected or overridden review.');
  }

  const review: ReviewAction = {
    id: `review-dev-${Date.now()}-${generatedReviewNumber++}`,
    decision_id: input.decision_id,
    reviewer: 'auditor-local',
    action: input.action,
    comment: input.comment?.trim() || null,
    created_at: new Date().toISOString(),
  };
  mockReviews.push(review);
  return copyReview(review);
}
