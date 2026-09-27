# RAG Observability Lab

A production-grade Retrieval-Augmented Generation (RAG) engineering and observability platform. 

This is not a simple "upload PDF and chat" application. It is a comprehensive framework for instrumenting, tracking, and evaluating every single stage of a complex RAG pipeline.

## Features

- **Strict Provenance Tracking**: Metadata follows every chunk from parsing to generation.
- **Hybrid Retrieval**: Combines BM25 (sparse) and Vector Search (dense) using Reciprocal Rank Fusion (RRF).
- **Cross-Encoder Reranking**: Re-scores candidate sets for maximal accuracy.
- **Deep Observability**: Traces latency (P50/P95/P99) at every micro-stage (parsing, chunking, embedding, retrieval, fusion, reranking, generation).
- **Formal Evaluation**: Deterministic metric tracking (Recall@K, MRR, NDCG) and separated retrieval vs generation evaluation.
- **Groundedness Verification**: Extracts and validates claims against retrieved evidence to detect hallucinations.
- **Strict Fallbacks**: Intercepts queries with insufficient evidence before they reach the LLM to prevent hallucination.

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for a detailed breakdown of the storage abstractions and pipeline.

## Getting Started

### Prerequisites
- Python 3.12+
- Node.js 20+
- Docker & Docker Compose
- API Key (e.g., Gemini) for LLM generation

### Local Setup

1. **Backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

2. **Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### Docker Setup

```bash
docker-compose up --build
```

## Security

This system implements robust boundaries between `System Instructions`, `User Queries`, and `Untrusted Context` to mitigate Prompt Injection attacks.

## Documentation

- [Architecture & Design](docs/ARCHITECTURE.md)
- [Observability Strategy](docs/OBSERVABILITY.md)
- [Interview Preparation](docs/INTERVIEW_PREP.md)
