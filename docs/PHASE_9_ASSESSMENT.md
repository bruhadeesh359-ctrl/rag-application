# Phase 9 Assessment

## Current Deployment Architecture
- **Frontend**: A React application built with Vite and TypeScript.
- **Backend**: A Python 3.12 FastAPI application handling ingestion, RAG orchestration (retrieval, generation), and observability.
- **Storage**:
  - SQLite (`./rag_observability.db`) for relational data (documents, chunks, traces, spans).
  - ChromaDB (`./chroma_db`) for vector storage.
  - BM25 index (in-memory or sparse storage).
- **Orchestration**: A simple `docker-compose.yml` defining the two services (`frontend`, `backend`), exposing ports `80` and `8000`, respectively.
- **Models**: Uses `sentence-transformers` for dense embeddings and reranking. Models are downloaded lazily on startup or first request.

## Existing Docker Configuration
- **Backend (`backend/Dockerfile`)**:
  - Uses `python:3.12-slim` base image.
  - Runs as the `root` user.
  - `requirements.txt` used for dependency management (without strict hashes or pinning for all packages).
  - Test files are currently baked into the image.
  - Exposes port 8000.
- **Frontend (`frontend/Dockerfile`)**:
  - Uses multi-stage build: `node:20-alpine` (build) -> `nginx:alpine` (serve).
  - Exposes port 80.
  - Standard `nginx` config is used which does not properly route traffic to `index.html` for client-side routing.
- **Missing Elements**: `.dockerignore` files are absent, which means local caches (`__pycache__`, `node_modules`, `.venv`) might be built into images depending on the context directory.

## Build and Runtime Processes
- **Frontend Build**: `npm ci && npm run build`, outputting static assets to `dist/`.
- **Frontend Runtime**: `nginx -g daemon off;`.
- **Backend Runtime**: `uvicorn app.main:app --host 0.0.0.0 --port 8000`.

## Required Environment Variables
- `GEMINI_API_KEY` (Backend): Required for LLM generation.
- `ENVIRONMENT` (Backend): Typically set to `production`.
- `CORS_ORIGINS` (Backend): Optional comma-separated list of allowed origins.
- `VITE_API_BASE_URL` (Frontend): Build-time and runtime variable pointing to the backend API URL.

## Persistent Storage Requirements
- `./rag_observability.db` (SQLite Database).
- `./chroma_db` (Chroma Vector Database).
- HuggingFace Models Cache (`~/.cache/huggingface` by default).

*Note: In `docker-compose.yml`, a volume `rag_data:/app/data` is mapped, but the backend stores databases in `./` instead of `/app/data/`. This is a mismatch causing persistent data loss on container restart.*

## Model Dependencies
- `all-MiniLM-L6-v2` (SentenceTransformer for dense embeddings).
- `cross-encoder/ms-marco-MiniLM-L-6-v2` (CrossEncoder for reranking).

## GPU Dependencies
- None required for standard operations (defaults to CPU).
- Can utilize CUDA if `device="cuda"` is specified, but CI and standard CD will rely on CPU.

## CI Requirements
- Automate linting (`npm run lint`), type checking (`tsc -b`), and building (`npm run build`) for the Frontend.
- Automate testing (`pytest`) for the Backend.
- Validate `docker build` reproducibility.

## CD Requirements
- Simple deployment pipeline (e.g., pushing to GitHub Container Registry `ghcr.io` or Docker Hub).
- Given the current setup, actual automated deployment requires specifying a cloud target. If one is not specified, CD will push to the registry and document deployment requirements.

## Security Risks
1. **Root Execution**: The backend container runs as `root`.
2. **Missing `.dockerignore`**: Accidental inclusion of secrets, large local databases, or `node_modules` into image layers.
3. **Model Download on Startup**: Slows startup, potentially causing readiness/liveness probe failures, and requires broad outbound internet access in production.
4. **Nginx Client-Side Routing**: The default nginx configuration lacks a fallback to `index.html` (e.g., `try_files $uri /index.html;`), breaking deep links.
5. **Lack of Proper Storage Mapping**: `SQLite` and `ChromaDB` default to the `/app` root directory rather than `/app/data`, making the `rag_data` volume mount useless.

## Deployment Blockers
- Path configurations for SQLite and ChromaDB must be mapped to a designated volume directory (e.g., `/app/data`).
- `nginx` configuration requires a custom `nginx.conf` for React Router.
- Missing non-root user in the backend Dockerfile.
- Missing `.dockerignore` files.
- Need a health check endpoint exposed in the FastAPI application (Phase 7 API might have one, needs verification).

## Recommended Implementation Plan
1. **Application Paths**: Update `backend/app/core/database.py` and `backend/app/services/vector_store.py` to support a `DATA_DIR` environment variable for storage, defaulting to `./data`.
2. **Docker Hardening**:
   - Create `.dockerignore` for both `frontend` and `backend`.
   - Update Backend `Dockerfile` to create an `appuser`, pre-download HuggingFace models during build (or map a cache volume), and use `HEALTHCHECK`.
   - Update Frontend `Dockerfile` to include a custom `nginx.conf` supporting SPA routing.
3. **CI/CD Pipelines**:
   - Update `.github/workflows/ci.yml` for complete unit test, linting, and docker build verification.
   - Create `.github/workflows/cd.yml` to publish to GHCR.
4. **Security**: Add `appuser` user configuration in the Dockerfile.
5. **Documentation**: Create `docs/PHASE_9.md`, `docs/DEPLOYMENT.md`, `docs/CI_CD.md`, and `docs/DEPLOYMENT_CHECKLIST.md`.
