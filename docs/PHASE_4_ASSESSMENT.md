# Phase 4 Assessment

## Current Architecture
The RAG pipeline correctly operates up through Phase 3:
1. **Documents** are chunked and embedded with strict `Provenance` metadata via `ChunkCreate` and `RetrievedChunk`.
2. **HybridRetriever** aggregates search results via `SparseRetriever` (BM25) and `DenseRetriever` (Vector).
3. **RRFFusion** mathematically scores ranks and blends candidates.
4. **CrossEncoderReranker** produces the final highly-accurate contextual set.

The models and logic for claim extraction and groundedness evaluation currently exist as placeholders in `app/schemas/domain.py` (`ExtractedClaim`, `GroundednessResult`, `GenerationResult`).

## Reusable Components
- `RetrievedChunk` which encapsulates text and exact chunk coordinates (document_id, chunk_index). This will be heavily relied upon by the `ContextBuilder`.
- `HybridRetriever`, whose output forms the basis of the LLM context.
- `app.core.config`, which provides a clean schema for injecting hyper-parameters without hard-coding models or thresholds.

## Phase 4 Implementation Plan
1. **LLM Provider Abstraction**:
   - Create `app/core/llm.py` with an abstract `LLMProvider` and a concrete `GeminiProvider`.
   - The provider must support fallback handling, timeout bounds, and retry logic.
   - Use `google-genai` or standard HTTP client with API keys loaded from `os.getenv("GEMINI_API_KEY")`.
2. **Context Builder**:
   - Create `app/services/context_builder.py`.
   - Take a list of `RetrievedChunk`s and map them to stable identifiers (e.g. `[S1]`, `[S2]`).
   - Emit a formatted string alongside a dictionary mapping `citation_id -> RetrievedChunk`.
3. **Prompt Definition**:
   - Build a robust `SystemPrompt` explicitly separating context from user instruction, demanding source identifiers `[Sx]` for claims, and explicitly commanding abstention if evidence is insufficient.
4. **Citation Validation**:
   - Create `CitationValidator` to parse LLM outputs, regex-match `[Sx]`, cross-reference with the `ContextBuilder` map, and reject fabricated references.
5. **Groundedness Analysis**:
   - Since Phase 4 requires strict tracking, we will use a naive deterministic extraction or a second LLM pass (LLM-as-a-judge) to measure supported vs unsupported claims. We will mark this as *LLM-assisted*.
6. **RAG Service API (`POST /api/rag/query`)**:
   - Tie everything together: Query -> HybridRetrieval -> Evidence Threshold check -> ContextBuilder -> GeminiProvider -> CitationValidator -> GroundednessAnalyzer -> Output.

## Configuration Additions
Extend `app/core/config.py` with:
- `GenerationCfg`: `provider`, `model`, `temperature`, `max_output_tokens`, `timeout_seconds`, `max_retries`.
- `EvidenceCfg`: `minimum_evidence_score`, `minimum_context_chunks`.

## Testing Strategy
- Unit tests for `ContextBuilder` (must preserve ordering, assign correct IDs).
- Unit tests for `CitationValidator` (catch missing, malformed, or fake citations).
- Unit tests mocking the `LLMProvider` to simulate Gemini network failures, timeouts, or hallucinated responses without actually making API requests.

## Risks & Fallbacks
- **Empty Retrieval**: Handled safely via Evidence thresholds.
- **Hallucinated Citations**: Blocked natively by `CitationValidator`.
- **API Token Limits**: We will truncate context up to the `final_top_k` provided by the reranker.
