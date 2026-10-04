export interface IntegrityEvent {
  event_id: string;
  sequence: number;
  event_type: string;
  hash: string;
  previous_hash: string | null;
}

export interface IntegrityInfo {
  decision_id: string;
  root_hash: string | null;
  event_count: number;
  events_hashed: number;
  hash_algorithm: string | null;
  chain_status: string;
  verification_status: string;
  last_verified_at: string | null;
  events: IntegrityEvent[];
}
