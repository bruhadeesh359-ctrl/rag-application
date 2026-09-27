# Deployment Architecture & Configuration

This document outlines the operational configurations for deploying the RAG Observability Lab.

## Architecture

```mermaid
graph TD
    User([User]) --> |HTTP 80| Nginx[Frontend Nginx Container]
    Nginx --> |API Calls| FastAPI[Backend FastAPI Container]
    
    subgraph Storage Volume [/app/data]
        SQLite[(SQLite DB)]
        ChromaDB[(Chroma Vector Store)]
        HFCache[HF Models Cache]
    end
    
    FastAPI --> SQLite
    FastAPI --> ChromaDB
    FastAPI --> HFCache
    
    FastAPI -.-> |HTTPS| Gemini[Google Gemini API]
```

## Configuration Matrix

| Component | Local | CI | Production |
|-----------|-------|----|------------|
| **FastAPI** | ✓ | ✓ | ✓ |
| **React** | ✓ | ✓ | ✓ |
| **Gemini** | optional | mocked | configured |
| **SQLite** | ✓ (`./data`) | test in-memory | Persistent Volume |
| **Vector DB** | ✓ (`./data`) | test in-memory | Persistent Volume |
| **GPU** | optional | no | depends on host |
| **QLoRA** | separate | no | separate ML pipeline |
| **DPO** | separate | no | separate ML pipeline |

## Essential Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GEMINI_API_KEY` | Key for Google's Gemini Models | Yes (for Generation) | - |
| `ENVIRONMENT` | Target environment | No | `development` |
| `CORS_ORIGINS` | Comma-separated allowed origins | No | `*` |
| `DATA_DIR` | Backend persistent storage directory | No | `.` |
| `HF_HOME` | HuggingFace cache directory | No | `~/.cache/huggingface` |
| `VITE_API_BASE_URL` | Frontend API base URL | No | `/api/v1` |

## Storage Considerations
Because containers are ephemeral, **all SQLite metadata and ChromaDB vector indices will be lost if not mounted externally.**

We use a `DATA_DIR` environment variable defaulting to `/app/data` inside Docker. This directory must be mapped to a persistent volume (e.g., Docker Volume, AWS EBS, GCP Persistent Disk) across container restarts.

## Model Cache
The dense embedding (`all-MiniLM-L6-v2`) and reranking (`ms-marco-MiniLM-L-6-v2`) models download upon the first query. We map `HF_HOME` to the persistent `DATA_DIR` (`/app/data/.cache`) to prevent models from re-downloading on every container deployment, ensuring faster startup times and less network egress.

## Rollback Strategy
If a new image tag fails the health checks or breaks functionality:
1. Re-deploy the previously known-good container image (`ghcr.io/repository/backend:<previous-sha>`).
2. There are no automated database migrations configured in the system (yet), so database schemas remain backward compatible with prior `Phase 7` schemas.
