# Phase 7: Production FastAPI Backend Integration

## Overview
Phase 7 restructures the monolithic RAG application into a scalable, production-grade FastAPI application. It introduces robust dependency injection, modular routing, standardized API contracts, and middleware-level observability hooks.

## Architectural Decisions

### 1. Modular Routing (`app/api/v1`)
The previous implementation grouped completely disjoint domains (Retrieval, RAG, Evaluation, Observability) into `endpoints.py`. In Phase 7, we decentralized the routing logic into specific API domain files (e.g., `rag.py`, `retrieval.py`, `ingestion.py`, `health.py`). This allows teams to scale and own different parts of the API independently.

### 2. Dependency Injection (`app/api/dependencies.py`)
Previously, expensive models (e.g., HuggingFace embedding models, cross-encoders) were loaded at module scope in the router, causing:
- Slow API startup times.
- Memory bloating during testing.
- Hard coupling between routes and implementations.

Phase 7 introduces FastAPI `Depends()` coupled with `lru_cache` singletons for all services. This implements **lazy loading**: models are instantiated exactly once upon the first request that needs them, greatly accelerating initial boot and enabling easy test mocking.

### 3. Strict API Contracts (`app/schemas/api.py`)
To prevent internal data structure leakage, all endpoints now return a standardized `APIResponse[T]` wrapper. This enforces consistent fields for generic UI integrations:
- `request_id`: For correlated trace tracing.
- `data`: The primary payload.
- `meta`: Auxiliary data (e.g., debug info, timings, pagination).

### 4. Middleware Trace Injection (`app/core/middleware.py`)
Added a `RequestIDMiddleware` that injects an `X-Request-ID` into every incoming request using `contextvars`. This ID is natively picked up by the `TraceManager` implemented in Phase 6, ensuring end-to-end lineage from the HTTP request down to the lowest SQLite SQL trace execution.
