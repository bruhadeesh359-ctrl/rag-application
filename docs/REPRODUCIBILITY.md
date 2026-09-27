# Reproducibility Guide

The primary metric of a strong engineering project is whether it can be completely reproduced by a new developer on a fresh machine.

## 1. System Requirements
- **Docker & Docker Compose** (Recommended for identical environment matching)
- **Node.js 20+** (If building frontend locally)
- **Python 3.12+** (If running backend locally)
- **API Key:** `GEMINI_API_KEY` with access to Google's Gemini models.

## 2. Docker Reproduction (Preferred)

To start the complete platform securely and deterministically:

1. Clone the repository.
2. Copy the environment template:
   ```bash
   cp .env.example .env
   ```
3. Inject your LLM provider key into `.env`.
4. Build and start the cluster:
   ```bash
   docker-compose up --build
   ```

**What happens?**
- The backend image downloads the `all-MiniLM-L6-v2` and `ms-marco-MiniLM-L-6-v2` models on the first run and persists them to the `/app/data/.cache` volume.
- The `rag_observability.db` (SQLite) and ChromaDB are initialized inside `/app/data/`.
- The Vite frontend is compiled and served statically on Port 80.

## 3. Local Development Reproduction

If you need to reproduce the backend manually for debugging or tests:

```bash
# 1. Setup Backend
cd backend
python -m venv venv
# Activate the venv (source venv/bin/activate on Linux, venv\Scripts\Activate on Windows)
pip install -r requirements.txt
export DATA_DIR=./data
export PYTHONPATH=.

# 2. Run Tests
pytest tests/

# 3. Start Backend
uvicorn app.main:app --reload --port 8000
```

```bash
# 1. Setup Frontend
cd frontend
npm ci
npm run build

# 2. Run Linter
npm run lint

# 3. Start Frontend (Dev)
npm run dev
```

## 4. Hardware Assumptions
- **CPU:** Standard deployment assumes CPU execution for the dense embedder and cross-encoder. It is entirely functional on modern CPUs but will exhibit higher latency (~100-300ms for reranking).
- **GPU (CUDA):** If a local GPU is detected, `sentence_transformers` will automatically utilize it for hardware acceleration, significantly improving reranker latency. This is supported but not strictly required.
