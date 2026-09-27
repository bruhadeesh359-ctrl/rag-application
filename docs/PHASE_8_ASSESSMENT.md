# Phase 8 Assessment: Frontend Integration

## Current Frontend State
- A basic React + Vite + TypeScript application exists in `frontend/`.
- Tailwind CSS (v4) and `lucide-react` are installed.
- React Router is NOT currently installed (routing is faked via state in `App.tsx`).
- There are some mock pages: `Overview.tsx`, `Playground.tsx`, and `Traces.tsx`.
- *CRITICAL ISSUE*: `Overview.tsx` is completely populated with mock data (`mockMetricData`, `mockLatencyData`), which directly violates the hard requirements for Phase 8.
- Missing pages: Evaluation, Experiments, Documents.

## Backend API Surface (Phase 7)
The FastAPI backend is fully operational on `localhost:8000/api/v1` with the following endpoints:
- `GET /health` & `GET /system`
- `POST /ingest` (File upload for parsing/chunking)
- `POST /retrieve/bm25`, `/retrieve/dense`, `/retrieve/hybrid`
- `POST /rag/query` & `POST /rag/inspect`
- `GET /observability/traces`, `/traces/{trace_id}`, `/summary`
- `POST /evaluation/run`, `GET /evaluation/runs`, `GET /evaluation/runs/{experiment_id}`

## Implementation Risks
1. **Mock Data Removal**: All existing mock constants must be strictly purged. If the backend returns empty telemetry (e.g. `NOT_YET_MEASURED`), the UI must gracefully show "No Data Available" instead of breaking charts.
2. **Missing Routing**: We need to implement proper client-side routing (e.g. `react-router-dom`) so trace inspection and deep-linking works.
3. **Data Fetching & State**: We need a solid API client layer. We can implement a typed fetch wrapper to interface with backend models.

## API-to-Screen Mapping
| Screen | Route Path | Associated API Endpoint |
|---|---|---|
| Overview | `/overview` | `GET /observability/summary` |
| RAG Playground | `/rag` | `POST /rag/query`, `POST /rag/inspect` |
| Retrieval | `/retrieval` | `POST /retrieve/*` |
| Documents | `/documents` | `POST /ingest` |
| Evaluation | `/evaluation` | `POST /evaluation/run` |
| Experiments | `/experiments` | `GET /experiments`, `GET /experiments/{id}` |
| Traces | `/observability/traces` | `GET /observability/traces`, `GET /traces/{id}` |

## Responsive & Accessibility Requirements
- Use Tailwind classes for desktop-first responsiveness (`md:`, `lg:` breakpoints).
- Utilize semantic HTML elements (`<nav>`, `<main>`, `<aside>`).
- Implement proper loading spinners/skeletons while data is actively fetching.
