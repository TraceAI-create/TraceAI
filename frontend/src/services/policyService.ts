import { mockPolicies, mockPolicyEvaluations } from '../mock/policies';
import type { Policy, PolicyEvaluation } from '../types/policy';

function copyPolicy(policy: Policy): Policy {
  return { ...policy, rules: policy.rules.map((rule) => ({ ...rule })) };
}

function copyEvaluation(evaluation: PolicyEvaluation): PolicyEvaluation {
  return { ...evaluation, conditions: evaluation.conditions.map((condition) => ({ ...condition })) };
}

/**
 * Policy and evaluation data boundary for the frontend.
 * Replace these mock implementations with FastAPI requests when API access is ready.
 */
export async function getPolicies(): Promise<Policy[]> {
  return Promise.resolve(mockPolicies.map(copyPolicy));
}

export async function getPolicyById(policyId: string): Promise<Policy | null> {
  const policy = mockPolicies.find((item) => item.id === policyId);
  return Promise.resolve(policy ? copyPolicy(policy) : null);
}

export async function getPolicyEvaluations(policyId: string): Promise<PolicyEvaluation[]> {
  return Promise.resolve(
    mockPolicyEvaluations
      .filter((evaluation) => evaluation.policy_id === policyId)
      .map(copyEvaluation),
  );
}

export async function getEvaluationsForDecision(decisionId: string): Promise<PolicyEvaluation[]> {
  return Promise.resolve(
    mockPolicyEvaluations
      .filter((evaluation) => evaluation.decision_id === decisionId)
      .map(copyEvaluation),
  );
}
