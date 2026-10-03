export interface PolicyRule {
  id: string;
  name: string;
  description: string;
  condition: string;
  action: string;
}

export interface Policy {
  id: string;
  name: string;
  version: string;
  status: string;
  description: string;
  policy_type: string;
  effective_from: string | null;
  effective_to: string | null;
  created_at: string;
  updated_at: string;
  rules: PolicyRule[];
}

export interface EvaluationCondition {
  name: string;
  expected: string;
  actual: string;
  result: string;
}

export interface PolicyEvaluation {
  id: string;
  policy_id: string;
  policy_version: string;
  decision_id: string;
  evaluated_at: string;
  result: string;
  summary: string;
  conditions: EvaluationCondition[];
}
