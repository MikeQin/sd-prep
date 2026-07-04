export interface ScoreOut {
  talk_listen_ratio: number;
  objection_raised: boolean;
  objection_handled_well: boolean;
  pricing_discussed: boolean;
  next_step_committed: boolean;
  sentiment_score: number;
  overall_score: number;
  flags: string[];
}

export interface CallSummary {
  id: string;
  rep_id: string;
  customer_name: string;
  vertical: string;
  date: string;
  overall_score: number;
}

export interface CallDetail extends Omit<CallSummary, "overall_score"> {
  duration_seconds: number;
  turns: { speaker: string; start: number; end: number; text: string }[];
  score: ScoreOut;
}

export interface RepSummary {
  id: string;
  name: string;
  vertical: string;
  call_count: number;
  average_score: number;
}

export interface RepDetail {
  id: string;
  name: string;
  vertical: string;
  calls: CallSummary[];
}
