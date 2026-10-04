import { mockAuditReports } from '../mock/auditReports';
import type { AuditReport } from '../types/auditReport';

/**
 * Audit report data boundary. Replace this fixture lookup with
 * GET /api/v1/decisions/{decision_id}/audit-report during API integration.
 */
export async function getAuditReport(decisionId: string): Promise<AuditReport | null> {
  const report = mockAuditReports[decisionId];
  return Promise.resolve(report ? {
    ...report,
    decision: { ...report.decision },
    events: report.events.map((event) => ({ ...event, payload: { ...event.payload } })),
    evidence: report.evidence.map((item) => ({ ...item, metadata: { ...item.metadata } })),
    policies: report.policies.map(({ policy, evaluation }) => ({
      policy: { ...policy, rules: policy.rules.map((rule) => ({ ...rule })) },
      evaluation: evaluation ? { ...evaluation, conditions: evaluation.conditions.map((condition) => ({ ...condition })) } : null,
    })),
    reviews: report.reviews.map((review) => ({ ...review })),
    integrity: report.integrity ? { ...report.integrity, events: report.integrity.events.map((event) => ({ ...event })) } : null,
    final_outcome: report.final_outcome ? { ...report.final_outcome } : null,
  } : null);
}

export async function getAuditReports(): Promise<AuditReport[]> {
  const reports = await Promise.all(Object.keys(mockAuditReports).map((decisionId) => getAuditReport(decisionId)));
  return reports.filter((report): report is AuditReport => report !== null);
}
