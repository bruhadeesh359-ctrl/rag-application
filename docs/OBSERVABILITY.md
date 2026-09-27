# Deep AI Observability & Error Taxonomy

The RAG Observability Lab implements a highly detailed OpenTelemetry-style tracing framework (Phase 6) that wraps every query execution, tracking latency, token usage, and logical errors.

## 1. Trace Architecture

Each RAG request initializes a `Trace` with a globally unique UUID. The trace contains multiple `Span`s that measure the execution of individual pipeline steps.

- **Trace IDs:** UUIDv4 generated at the request boundary.
- **Span IDs:** UUIDv4 generated for each distinct step (e.g., `retrieval_pipeline`, `llm_generation`).
- **Parent-Child Relationships:** Spans like `base_retrieval` are children of `retrieval_pipeline`, allowing the frontend to construct hierarchical flame graphs of execution time.

## 2. Telemetry Collected

- **Latency:** Timestamps (`start_time`, `end_time`) accurately measure pipeline bottlenecks down to the millisecond.
- **Tokens & Cost:** `input_tokens`, `output_tokens`, and `total_tokens` are extracted from the LLM provider response to enable cost monitoring.
- **Retrieval:** Tracks how many chunks were fetched, and which method (dense vs sparse vs hybrid) dominated the top-k results.
- **Citations:** Tracks `citations_valid` true/false.
- **Groundedness:** Logs the ratio of `supported_claims` / `total_claims`.

*Note: Telemetry does NOT log raw PII or excessive document contents in the span metadata, though queries are logged for evaluation purposes.*

## 3. Error Taxonomy

The system defines strict error categories rather than throwing raw Exceptions to the user.

| Error Category | Meaning | Likely Cause | User-Facing Behavior |
|---|---|---|---|
| `INSUFFICIENT_EVIDENCE` | Retrieval failed to find highly relevant context. | Query is out of distribution for the document corpus. | "I couldn't find enough evidence..." |
| `LLM_GENERATION_ERROR` | Provider API threw an exception. | Timeout, rate limit, or authentication failure. | Fallback message triggered. |
| `CITATION_ERROR` | LLM generated invalid or hallucinated citations. | LLM ignored system prompt instructions. | `status="unsafe_citations"` |
| `GROUNDEDNESS_ERROR` | LLM generated claims not entailed by evidence. | Hallucination. | `status="unsupported_claims"` |
| `VECTOR_STORE_ERROR` | Connection to ChromaDB failed. | Missing persistent volume or corrupted index. | Internal Server Error (500) |
| `RERANKER_ERROR` | Cross-encoder model failed to execute. | Out of Memory (OOM) or corrupted weights. | Internal Server Error (500) |

## 4. Trace Persistence

Traces are asynchronously written to the SQLite database `rag_observability.db` via `app.core.tracer.tracer.storage`. The frontend fetches these via `GET /api/v1/observability/traces` to render the Trace Explorer.
