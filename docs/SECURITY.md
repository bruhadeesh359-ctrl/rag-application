# Security Profile & Threat Model

This document outlines the security controls, known limitations, and threat models for the RAG Observability Lab.

**Note: The system is NOT "fully secure" or "zero-vulnerability". It is an engineering sandbox that lacks production-grade identity and access management (IAM).**

## 1. Security Controls Implemented

- **Secret Management:** Secrets (`GEMINI_API_KEY`) are managed exclusively via `.env` variables injected into the Docker container. No secrets are baked into the Docker image, and `.env` files are aggressively `.gitignore`'d and `.dockerignore`'d.
- **Frontend Protections:** The React frontend makes API calls without possessing LLM API keys directly. The backend acts as a secure proxy.
- **Container Hardening:** The backend Dockerfile creates and executes under the `appuser` user rather than `root`.
- **CORS:** FastAPI enforces Cross-Origin Resource Sharing (CORS) limits strictly via the `CORS_ORIGINS` environment variable.
- **Error Sanitization:** FastAPIs exception handlers intercept raw exceptions and return sanitized JSON responses to prevent leaking internal stack traces or SQL schemas.

## 2. Threat Model

| Threat | Impact | Mitigation | Remaining Limitation |
|---|---|---|---|
| **Prompt Injection** | LLM ignores system instructions (e.g., reveals secrets). | Extracted chunks are treated strictly as DATA in the prompt template. `GroundednessAnalyzer` double-checks claims. | Advanced jailbreaks inside uploaded PDFs may still bypass LLM-assisted checks. |
| **Path Traversal** | Attacker downloads arbitrary server files. | FastAPI endpoints do not accept raw file paths for querying. | Uploaded documents must be rigorously scanned by external infrastructure (WAF) before ingestion. |
| **API Abuse / DoS** | Exhaustion of LLM quota and budget. | N/A (Currently). | **No rate limiting or authentication is implemented.** This must be deployed behind an API Gateway (e.g., Kong, AWS API Gateway) in production. |
| **Secret Leakage** | Exposure of Gemini API Key. | Environment variables. | If the host machine is compromised, the environment variables are exposed. |

## 3. Known Security Limitations

- **No Authentication:** There is currently no user login, JWT validation, or RBAC (Role-Based Access Control) to limit who can upload documents or query the API.
- **No Document Segregation:** All uploaded documents fall into a single multi-tenant vector space. Users can query and retrieve information from documents uploaded by other users.
- **Vulnerability Scanning:** Dependency scanning (e.g., Snyk, Dependabot) and container image scanning (e.g., Trivy) are not yet integrated into the CI/CD pipeline.
