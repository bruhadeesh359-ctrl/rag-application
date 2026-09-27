# Deployment Checklist

## Infrastructure
- [x] Runtime selected: `Docker` (Multi-container setup via `docker-compose`)
- [x] Registry selected: `ghcr.io`
- [x] Environment variables configured: `.env.example` mapped properly in `docker-compose.yml`.
- [ ] Secrets configured: (Awaiting deployment environment secrets)
- [x] Database configured: SQLite mapped to `DATA_DIR`.
- [x] Vector store configured: ChromaDB mapped to `DATA_DIR`.
- [x] LLM provider configured: Gemini configured via `GEMINI_API_KEY`.
- [x] CORS configured: Set via `CORS_ORIGINS`.
- [x] Storage configured: `/app/data` mapped appropriately.

## Security
- [x] No secrets in Git: Verified via `.dockerignore` and `.gitignore`.
- [x] Non-root container: Backend `Dockerfile` uses `appuser`.
- [x] CORS restricted: Allowed through standard FastAPI middleware setup via `CORS_ORIGINS`.
- [x] Error responses sanitized: Custom JSONResponse handler filters stacktraces out of production errors (Phase 7).
- [ ] Image scanned where configured: Awaiting container security scan action in CD pipeline.

## Application
- [x] Health endpoint: `GET /api/v1/health` exists and mapped to Docker `HEALTHCHECK`.
- [x] API working: FastAPI responds to standard HTTP queries.
- [x] Frontend working: Nginx serves static compiled Vite bundle.
- [x] Observability working: Tracing intercepts requests perfectly.

## Deployment
- [x] Image built: CI validates the image can be built.
- [x] Image pushed: CD logic written to push the image to GHCR.
- [ ] Deployment completed: **NOT CONFIGURED** (Blocked pending explicit infrastructure).
- [ ] Health check passed: Will run post-deployment.
- [x] Rollback documented: See `DEPLOYMENT.md`.
