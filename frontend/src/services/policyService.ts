import { api } from './apiClient';
import type { Policy, PolicyEvaluation } from '../types/policy';

interface BackendRule {
  field: string;
  operator: string;
  value: unknown;
  action: string;
  message?: string;
}

interface BackendPolicy {
  id: string;
  name: string;
  version: string;
  status?: string;
  description?: string | null;
  content_hash?: string;
  storage_uri?: string | null;
  rules: Record<string, unknown> | BackendRule[];
  effective_from?: string;
  effective_to?: string | null;
  created_at: string;
  updated_at?: string;
}

function toPolicy(p: BackendPolicy): Policy {
  // Backend stores rules as a JSON blob; normalize to array for the frontend
  const rawRules = Array.isArray(p.rules)
    ? p.rules
    : (p.rules?.['rules'] as BackendRule[] | undefined) ?? [];

  const now = new Date().toISOString();
  const effectiveFrom = p.effective_from || p.created_at || now;
  const isExpired = p.effective_to ? new Date(p.effective_to) < new Date() : false;
  const computedStatus = p.status || (isExpired ? 'inactive' : 'active');

  return {
    id: p.id,
    name: p.name,
    version: p.version,
    status: computedStatus,
    description: p.description ?? '',
    policy_type: 'governance',
    effective_from: effectiveFrom,
    effective_to: p.effective_to ?? null,
    created_at: p.created_at || now,
    updated_at: p.updated_at ?? p.created_at ?? now,
    rules: rawRules.map((r, i) => ({
      id: `${p.id}-rule-${i}`,
      name: r.message ?? `Rule ${i + 1}`,
      description: `${r.field} ${r.operator} ${JSON.stringify(r.value)}`,
      condition: `${r.field} ${r.operator} ${JSON.stringify(r.value)}`,
      action: r.action ?? 'block',
    })),
  };
}

export async function getPolicies(): Promise<Policy[]> {
  const results = await api.get<BackendPolicy[]>('/policies?active_only=false');
  return results.map(toPolicy);
}

export async function getPolicyById(policyId: string): Promise<Policy | null> {
  try {
    const p = await api.get<BackendPolicy>(`/policies/${policyId}`);
    return toPolicy(p);
  } catch {
    return null;
  }
}

export async function getPolicyEvaluations(_policyId: string): Promise<PolicyEvaluation[]> {
  // Policy evaluations are recorded as POLICY_EVALUATION audit events on decisions.
  // Full evaluation history requires querying per-decision; return empty for now.
  return [];
}

export async function getEvaluationsForDecision(_decisionId: string): Promise<PolicyEvaluation[]> {
  return [];
}
