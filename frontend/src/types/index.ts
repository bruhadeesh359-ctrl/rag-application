export interface TraceMetric {
  parsing_ms?: number;
  chunking_ms?: number;
  embedding_ms?: number;
  bm25_ms?: number;
  dense_retrieval_ms?: number;
  rrf_ms?: number;
  reranking_ms?: number;
  context_build_ms?: number;
  llm_ms?: number;
  validation_ms?: number;
  total_ms: number;
}

export interface Trace {
  trace_id: string;
  query_id: string;
  experiment_id?: string;
  start_time: string;
  end_time?: string;
  status: 'running' | 'success' | 'error';
  metrics: TraceMetric;
  input_tokens?: number;
  output_tokens?: number;
  total_tokens?: number;
  estimated_cost?: number;
  error_category?: string;
  error_message?: string;
}

export interface Chunk {
  chunk_id: string;
  document_id: string;
  text: string;
  score?: number;
  rank?: number;
  retrieval_method?: string;
  provenance: {
    document_id: string;
    filename: string;
    page?: number;
    section?: string;
    chunk_index: number;
    source_location?: string;
  };
}
