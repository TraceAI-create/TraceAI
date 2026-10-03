import { mockDecisionDetails } from '../mock/decisionDetails';
import { mockDecisions } from '../mock/decisions';
import { mockReplayRuns } from '../mock/replays';
import type { ReplayCondition, ReplayDifference, ReplayRun } from '../types/replay';

let generatedReplayNumber = 1;

function copyReplay(run: ReplayRun): ReplayRun {
  return {
    ...run,
    conditions: run.conditions.map((condition) => ({ ...condition })),
    differences: run.differences.map((difference) => ({ ...difference })),
  };
}

function getOriginalResult(decisionId: string): string {
  const decision = mockDecisions.find((item) => item.id === decisionId);
  if (!decision) throw new Error('Decision not found in development fixtures.');

  const normalizedStatus = decision.status.toLowerCase();
  if (normalizedStatus.includes('approved')) return 'APPROVED';
  if (normalizedStatus.includes('rejected') || normalizedStatus === 'rejected') return 'REJECTED';
  if (normalizedStatus.includes('challenged') || normalizedStatus.includes('policy_violated')) return 'REVIEW_REQUIRED';

  const detail = mockDecisionDetails[decisionId];
  const decisionEvent = detail?.events.find((event) => event.event_type === 'DECISION_MADE');
  const outcome = decisionEvent?.payload.decision;
  if (typeof outcome === 'string' && outcome.toLowerCase().includes('approve')) return 'APPROVED';
  if (typeof outcome === 'string' && outcome.toLowerCase().includes('reject')) return 'REJECTED';
  return 'ESCALATED';
}

function makeReplayId(): string {
  const id = `replay-dev-${Date.now()}-${generatedReplayNumber}`;
  generatedReplayNumber += 1;
  return id;
}

function toDifference(condition: ReplayCondition): ReplayDifference {
  const significanceByName: Record<string, string> = {
    'Requested amount': 'The requested amount was changed for this what-if scenario.',
    'Days since incident': 'The elapsed time was changed for this what-if scenario.',
    'Prior claims': 'The prior-claim count was changed for this what-if scenario.',
    'Prior refund count': 'The prior-refund count was changed for this what-if scenario.',
    'Account verified': 'The identity verification state was changed for this what-if scenario.',
    'Customer risk': 'The customer risk value was changed for this what-if scenario.',
    'Policy version': 'The policy version was changed for this what-if scenario.',
  };
  return {
    field: condition.name,
    original_value: condition.original_value,
    replay_value: condition.replay_value,
    significance: significanceByName[condition.name] ?? 'This condition was changed in the mock what-if input.',
  };
}

function whatIfOutcome(decisionId: string, conditions: ReplayCondition[], originalResult: string): { result: string; explanation: string } {
  const changedValues = new Map(
    conditions
      .filter((condition) => condition.changed)
      .map((condition) => [condition.name.toLowerCase(), condition.replay_value.trim().toLowerCase()]),
  );

  if (decisionId === 'd3a6f291-7c4b-4d18-a21e-8b5d109a642f') {
    const amount = changedValues.get('requested amount');
    if (amount) {
      const numericAmount = Number(amount.replace(/[^0-9.]/g, ''));
      if (Number.isFinite(numericAmount) && numericAmount > 2500) {
        return { result: 'REVIEW_REQUIRED', explanation: 'The changed amount exceeds the mock claims threshold of $2,500 USD and requires human review.' };
      }
    }
    const days = changedValues.get('days since incident');
    if (days) {
      const numericDays = Number(days.replace(/[^0-9.]/g, ''));
      if (Number.isFinite(numericDays) && numericDays > 30) {
        return { result: 'REJECTED', explanation: 'The changed incident date is outside the mock 30-day reporting window.' };
      }
    }
    const priorClaims = changedValues.get('prior claims') ?? changedValues.get('prior refund count');
    if (priorClaims && Number(priorClaims) > 0) {
      return { result: 'REVIEW_REQUIRED', explanation: 'The changed prior-claim count triggers the mock duplicate/history review safeguard.' };
    }
  }

  if (decisionId === 'a1e9c462-5b37-49d0-8f24-3c6d72a519be' && changedValues.get('account verified') === 'false') {
    return { result: 'REVIEW_REQUIRED', explanation: 'The mock identity policy requires verification before account-sensitive routing.' };
  }

  if (decisionId === '7f4b2c91-08d3-4a65-b917-52e1f0c83d46') {
    const risk = changedValues.get('customer risk');
    if (risk && Number(risk) > 0.78) {
      return { result: 'REJECTED', explanation: 'The changed risk value exceeds the mock 0.78 risk threshold.' };
    }
  }

  return { result: originalResult, explanation: 'The changed conditions do not cross a modeled outcome threshold in this mock scenario.' };
}

export async function getReplayRuns(): Promise<ReplayRun[]> {
  return Promise.resolve(mockReplayRuns.map(copyReplay));
}

export async function getReplayRunsForDecision(decisionId: string): Promise<ReplayRun[]> {
  return Promise.resolve(
    mockReplayRuns
      .filter((run) => run.decision_id === decisionId)
      .sort((a, b) => b.created_at.localeCompare(a.created_at))
      .map(copyReplay),
  );
}

export async function getReplayById(replayId: string): Promise<ReplayRun | null> {
  const replay = mockReplayRuns.find((run) => run.id === replayId);
  return Promise.resolve(replay ? copyReplay(replay) : null);
}

export async function createDeterministicReplay(decisionId: string): Promise<ReplayRun> {
  const decision = mockDecisions.find((item) => item.id === decisionId);
  if (!decision) throw new Error('Decision not found in development fixtures.');

  const existing = mockReplayRuns.find((run) => run.decision_id === decisionId && run.mode === 'DETERMINISTIC');
  if (existing) return copyReplay(existing);

  const originalResult = getOriginalResult(decisionId);
  const detail = mockDecisionDetails[decisionId];
  const conditions: ReplayCondition[] = detail
    ? detail.events
        .filter((event) => event.event_type === 'CONTEXT_CAPTURED' || event.event_type === 'INPUT_RECEIVED')
        .flatMap((event) => Object.entries(event.payload).map(([name, value]) => ({
          name,
          original_value: typeof value === 'string' ? value : JSON.stringify(value),
          replay_value: typeof value === 'string' ? value : JSON.stringify(value),
          changed: false,
        })))
    : [];
  const now = new Date().toISOString();
  const run: ReplayRun = {
    id: makeReplayId(),
    decision_id: decisionId,
    mode: 'DETERMINISTIC',
    status: 'COMPLETED',
    created_at: now,
    completed_at: now,
    original_result: originalResult,
    replay_result: originalResult,
    summary: 'The recorded decision information is unchanged in this deterministic mock replay. No AI model was executed.',
    differences: [],
    conditions,
  };
  mockReplayRuns.push(run);
  return copyReplay(run);
}

export async function createWhatIfReplay(decisionId: string, inputConditions: ReplayCondition[]): Promise<ReplayRun> {
  if (!mockDecisions.some((decision) => decision.id === decisionId)) {
    throw new Error('Decision not found in development fixtures.');
  }

  const conditions = inputConditions.map((condition) => ({
    ...condition,
    changed: condition.original_value !== condition.replay_value,
  }));
  const originalResult = getOriginalResult(decisionId);
  const outcome = whatIfOutcome(decisionId, conditions, originalResult);
  const differences = conditions.filter((condition) => condition.changed).map(toDifference);

  if (outcome.result !== originalResult) {
    differences.push({
      field: 'Outcome',
      original_value: originalResult,
      replay_value: outcome.result,
      significance: outcome.explanation,
    });
  }

  const now = new Date().toISOString();
  const run: ReplayRun = {
    id: makeReplayId(),
    decision_id: decisionId,
    mode: 'WHAT_IF',
    status: 'COMPLETED',
    created_at: now,
    completed_at: now,
    original_result: originalResult,
    replay_result: outcome.result,
    summary: outcome.explanation,
    differences,
    conditions,
  };
  mockReplayRuns.push(run);
  return copyReplay(run);
}
