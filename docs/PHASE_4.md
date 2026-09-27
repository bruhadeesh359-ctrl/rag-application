# Phase 4: LLM Generation, Context Control & Validation

## Overview
Phase 4 implements the generation half of the RAG pipeline. It safely passes the verified retrieval context from Phase 3 to a generative LLM (Gemini 2.5 Flash), extracts claims, and strictly validates the outputs for groundedness and citation integrity.

## Architecture

1. **LLM Abstraction (`app/core/llm.py`)**:
   - `LLMProvider` interface isolates the core logic from specific SDK implementations.
   - `GeminiProvider` utilizes `google-genai` and environment variables. Secrets are strictly forbidden from being committed or logged.
   
2. **Context Builder (`app/services/context_builder.py`)**:
   - Receives final `RetrievedChunk` instances from Phase 3.
   - Assigns stable citation identifiers `[S1]`, `[S2]`.
   - Protects against context overflow via deterministic truncation.
   - Preserves `Provenance` by rendering it directly alongside the chunk text.

3. **RAG Service (`app/services/rag_service.py`)**:
   - The central orchestrator for `POST /api/rag/query`.
   - Checks **Evidence Thresholds** before hitting the LLM. If the retrieval scores are too low (e.g., `< 0.01`), the pipeline safely short-circuits and abstains to prevent forced hallucination.
   - Constructs the system prompt explicitly telling the LLM that retrieved evidence is untrusted data, mitigating **Prompt Injection**.

4. **Citation Validator (`app/services/citation_validator.py`)**:
   - Parses LLM output deterministically using Regex.
   - Ensures the LLM did not hallucinate citation IDs (e.g., inventing `[S99]`).
   - Maps citations back to the underlying `chunk_id`s.

5. **Groundedness Analyzer (`app/services/groundedness.py`)**:
   - Utilizes a secondary *LLM-Assisted* check (LLM-as-a-judge).
   - Forces the LLM to output structured JSON.
   - Breaks the generated answer down into distinct claims, marking them as `supported` or `unsupported` strictly based on the provided text context.

## Telemetry & Cost Safety
- Telemetry captures exact millisecond execution for retrieval, generation, and validation.
- Missing telemetry (like exact token usage or cost, if unavailable in the provider's async response) is marked as "Unavailable" rather than fabricated. Fake metrics destroy observability lab credibility.

## Fallback Behavior
The system abstains and returns a graceful fallback in the following scenarios:
1. **Insufficient Evidence**: The top chunk scored below `minimum_evidence_score`.
2. **LLM Timeouts**: The LLM provider timed out after `max_retries`.
3. **Provider Failures**: 5xx HTTP errors or rate limits from Gemini.

## API Usage

### RAG Query
```powershell
curl -X POST http://localhost:8000/api/rag/query `
  -H "Content-Type: application/json" `
  -d '{"query": "revenue increase"}'
```

**Response includes:**
- `answer`: The safe generated text.
- `status`: One of `grounded`, `unsafe_citations`, `unsupported_claims`, `abstained`.
- `citations`: List of valid source IDs used.
- `validation`: Embedded results of Groundedness and Citation Validation logic.
- `timings`: Millisecond breakdowns.
