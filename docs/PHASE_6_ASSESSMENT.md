# Phase 6 Observability Assessment

## Current Observability Capabilities (Phases 1-5)
1. **TraceManager**: Currently exists in `backend/app/core/tracer.py` and provides a very basic `start_trace`, `record_stage`, and `end_trace` capability. It records metrics (duration) and basic error status within a single flat `trace_context` dictionary.
2. **ExperimentTracker**: Exists in `backend/evaluation/tracker.py` and handles storing offline evaluation experiments (e.g. `retrieval_metrics.json`, `generation_metrics.json`, `config.json`).
3. **Endpoints**: `app/api/endpoints.py` has a `/retrieval/stats` route providing simple count metrics (number of vectors, chunks, indexed chunks).
4. **Errors**: `tracer.py` has an `ErrorTaxonomy` with string constants, but it is not utilized in a structured `Error` object format.

## Missing Instrumentation
1. **Span Hierarchy**: The current `TraceManager` does not natively support parent/child nested spans (e.g., Request -> Retrieval -> RRF -> Context -> LLM).
2. **Structured Spans**: We need a dedicated Span model that includes start/end times, parent_span_id, span_id, status, etc.
3. **Token & Cost Telemetry**: Token usage is currently not extracted properly into the trace. Cost calculation is missing.
4. **Structured Error Taxonomy**: Errors are just recorded as simple strings. We need a rigorous schema representing error_id, trace_id, category, severity, message, timestamp, and component.
5. **Observability Manager Layer**: A more comprehensive `ObservabilityManager` is needed to handle emitting structured events without leaking data.
6. **Data Privacy / Redaction**: Currently no clear enforcement on redacting sensitive keys or PII from telemetry before it hits storage.
7. **Trace Storage**: Currently `TraceManager.end_trace` has a placeholder `pass` for SQL persistence.
8. **Observability APIs**: We need `/api/observability/traces`, `/api/observability/metrics`, and `/api/observability/summary` for external visibility.

## Proposed Tracing Architecture
We will implement an event-driven observability core using Python's `contextvars` or explicit parameter passing for trace context. 

### Core Components
- **ObservabilityManager**: The main interface for services to begin traces, start spans, and record events.
- **TraceManager**: Manages the lifecycle of a `Trace` and its child `Spans`.
- **MetricsCollector**: Aggregates latency percentiles, error rates, and token counts.
- **EventLogger**: Handles logging structured JSON events and enforcing privacy controls (safe vs sensitive fields).
- **SQLiteStorage Extension**: Extend our existing storage to persist `traces`, `spans`, and `errors`.

### Event Schema
We will create a structured Pydantic schema in `app/schemas/observability.py`:
- `Trace`: trace_id, request_id, experiment_id, start_time, end_time, duration_ms, status.
- `Span`: span_id, trace_id, parent_span_id, name, start_time, end_time, duration_ms, status, attributes.
- `ErrorEvent`: error_id, trace_id, span_id, category, severity, message, timestamp, retryable, component.

### Error Taxonomy
We will extend `ErrorTaxonomy` to include the standard required categories (e.g. `LLM_RATE_LIMIT`, `VECTOR_STORE_ERROR`) and severities (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).

### Implementation Strategy
1. Introduce the `observability.py` schemas.
2. Upgrade `TraceManager` to support `start_span(name, parent_id)`.
3. Wrap existing `RAGService`, `HybridRetriever`, `EmbeddingService`, and `LLMProvider` calls in these spans.
4. Add SQL models and storage logic to `SQLiteStorage` for traces, spans, and errors.
5. Build the Observability REST APIs.
6. Add unit tests verifying telemetry and trace nesting.
