export interface APIResponse<T> {
  request_id?: string;
  data: T;
  meta?: Record<string, any>;
}

export interface PaginatedMeta {
  page: number;
  page_size: number;
  total?: number;
}

export interface PaginatedResponse<T> {
  request_id?: string;
  data: T[];
  meta: PaginatedMeta;
}

export interface ObservabilitySummary {
  total_requests: number;
  successful_requests: number;
  abstained_requests: number;
  failed_requests: number;
  average_latency_ms: number;
  p50_latency_ms: number;
  p95_latency_ms: number;
}

export interface RetrievedContextResponse {
  chunk_id: string;
  document_id: string;
  text: string;
  score: number;
  rank: number;
  retrieval_method: string;
  provenance?: {
    filename: string;
    page?: number;
    section?: string;
    chunk_index: number;
    source_location?: string;
  };
}

export interface Citation {
  token: string;
  document_id: string;
  chunk_id: string;
  text: string;
  filename?: string;
  page?: number;
  section?: string;
}

export interface GroundednessResult {
  score: number;
  supported_claims: number;
  total_claims: number;
}

export interface RAGQueryResponseData {
  answer: string;
  status: string;
  abstained: boolean;
  fallback_reason?: string;
  citations: Citation[];
  groundedness?: GroundednessResult;
}

export interface TraceSpan {
  span_id: string;
  parent_span_id?: string;
  stage: string;
  duration_ms: number;
  status: string;
}

export interface TraceError {
  error_id: string;
  span_id?: string;
  category: string;
  message: string;
}

export interface TokenUsage {
  input_tokens?: number;
  output_tokens?: number;
  total_tokens?: number;
}

export interface Trace {
  trace_id: string;
  request_id?: string;
  experiment_id?: string;
  start_time: string;
  end_time?: string;
  duration_ms: number;
  status: string;
  token_usage?: TokenUsage;
  spans?: TraceSpan[];
  errors?: TraceError[];
}
