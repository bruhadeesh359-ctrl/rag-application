# CI/CD Workflows

This document explains the automation pipelines handled via GitHub Actions.

*Note: Git is version control. GitHub Actions performs CI/CD automation.*

## CI Pipeline (`.github/workflows/ci.yml`)
Triggered on `push` and `pull_request` against the `main` branch.

### Jobs
1. **backend-test**: 
   - Uses `python:3.12`.
   - Installs dependencies from `requirements.txt`.
   - Executes `pytest tests/` to validate the RAG ingestion, RRF, reranking, and generation logic.
2. **frontend-build**:
   - Uses `node:20`.
   - Runs `npm ci` for deterministic dependency installation.
   - Runs `npm run lint` (`oxlint`).
   - Runs `npm run build` (`tsc -b && vite build`) to ensure there are no TypeScript or build-time errors.
3. **docker-check**:
   - Runs `docker-compose build` to verify that both `frontend` and `backend` images can be built sequentially without syntax or dependency errors.

## CD Pipeline (`.github/workflows/cd.yml`)
Triggered on `push` to `main` and manual `workflow_dispatch`.

### Jobs
1. **build-and-push**:
   - Logs into GitHub Container Registry (`ghcr.io`) using the standard `GITHUB_TOKEN`.
   - Extracts metadata (tags/labels) generating both a `latest` and an immutable `<git-sha>` tag.
   - Builds and pushes the `backend` image.
   - Builds and pushes the `frontend` image.
2. **deploy**:
   - Currently, automated cloud deployment is **BLOCKED**.
   - Because no explicit cloud platform (e.g. AWS App Runner, Google Cloud Run) has been declared or provided credentials, the step will log deployment instructions and gracefully exit. 
   - **Do not enable heavy ML pipelines (QLoRA, DPO) on this CD branch.** Those tasks are reserved for a separated, scheduled, or manual pipeline on GPU hardware.
