import type { AuditEvent } from './decisionDetail';
import type { Decision } from './decision';
import type { Evidence } from './evidence';
import type { IntegrityInfo } from './integrity';
import type { Policy, PolicyEvaluation } from './policy';
import type { ReviewAction } from './review';

export interface AuditReportPolicy {
  policy: Policy;
  evaluation: PolicyEvaluation | null;
}

export interface AuditReportOutcome {
  value: string;
  source: 'RECORDED_DECISION' | 'HUMAN_OVERRIDE' | 'RECORDED_RESULT';
  description: string;
}

export interface AuditReport {
  decision: Decision;
  executive_summary: string;
  events: AuditEvent[];
  evidence: Evidence[];
  policies: AuditReportPolicy[];
  reviews: ReviewAction[];
  integrity: IntegrityInfo | null;
  final_outcome: AuditReportOutcome | null;
}
