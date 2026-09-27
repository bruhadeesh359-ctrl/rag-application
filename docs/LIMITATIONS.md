# Known Limitations

A technically honest project is stronger than an exaggerated project. The following are the explicit technical limitations of the current RAG Observability Lab architecture.

## 1. Storage & Scaling
- **SQLite / Local Storage:** The backend utilizes a local SQLite database (`aiosqlite`) and a local ChromaDB instance stored in a mounted Docker volume (`/app/data`). While adequate for thousands of documents, this will not scale horizontally across multiple stateless containers. Production usage requiring high concurrency should swap SQLite for PostgreSQL and local ChromaDB for a managed vector database (e.g., Pinecone, Qdrant).
- **Synchronous Bottlenecks:** The embedding and cross-encoder reranking models run synchronously on CPU (or single GPU) within the FastAPI event loop, which may block concurrency under heavy load.

## 2. Evaluation
- **Synthetic Data Dependence:** Groundedness evaluation utilizes an LLM-as-a-judge mechanism. While prompt-engineered to be strict, LLMs are fundamentally prone to sycophancy and occasional hallucination, making the Groundedness metric an approximation, not absolute ground truth.
- **Dataset Size:** The offline evaluation datasets do not yet represent tens of thousands of varied query profiles, limiting the statistical significance of Recall@K and MRR benchmarking.

## 3. Infrastructure & Deployment
- **Cloud Deployment:** While `ghcr.io` CI/CD pushes are active, automated deployment to a scalable cloud orchestrator (Kubernetes, AWS ECS) is blocked pending explicit infrastructure definitions.
- **Authentication:** The API lacks OAuth2/JWT authentication and multi-tenant data segregation.

## 4. Prompt Injection
- **Mitigated, Not Solved:** Treating chunks as `DATA` rather than instructions mitigates indirect prompt injections. However, extremely sophisticated adversarial payloads embedded in uploaded PDFs could still theoretically manipulate the generative LLM. No absolute claim of "zero prompt injection" is made.
