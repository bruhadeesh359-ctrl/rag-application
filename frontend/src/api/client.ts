import type { 
    APIResponse, 
    PaginatedResponse, 
    ObservabilitySummary, 
    RAGQueryResponseData,
    Trace,
    RetrievedContextResponse
} from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

class APIClient {
    private async fetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
        const url = `${API_BASE_URL}${endpoint}`;
        const defaultHeaders = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };

        const config = {
            ...options,
            headers: {
                ...defaultHeaders,
                ...options?.headers,
            },
        };

        // If body is FormData, remove Content-Type so browser can set boundary
        if (options?.body instanceof FormData) {
            delete (config.headers as Record<string, string>)['Content-Type'];
        }

        const response = await fetch(url, config);
        
        if (!response.ok) {
            let errorMsg = response.statusText;
            try {
                const errorData = await response.json();
                errorMsg = errorData.error?.message || errorData.detail || errorMsg;
            } catch (e) {}
            throw new Error(errorMsg);
        }

        return response.json();
    }

    // Health
    async getHealth(): Promise<APIResponse<{status: string, service: string}>> {
        return this.fetch('/health');
    }

    async getSystem(): Promise<APIResponse<any>> {
        return this.fetch('/system');
    }

    // Observability
    async getObservabilitySummary(): Promise<APIResponse<ObservabilitySummary>> {
        return this.fetch('/observability/summary');
    }

    async getTraces(page = 1, pageSize = 50): Promise<PaginatedResponse<Trace>> {
        return this.fetch(`/observability/traces?page=${page}&page_size=${pageSize}`);
    }

    async getTrace(traceId: string): Promise<APIResponse<Trace>> {
        return this.fetch(`/observability/traces/${traceId}`);
    }

    // RAG
    async queryRAG(query: string, includeDebug = true): Promise<APIResponse<RAGQueryResponseData>> {
        return this.fetch('/rag/query', {
            method: 'POST',
            body: JSON.stringify({ query, include_debug: includeDebug, top_k: 10 })
        });
    }

    async inspectRAG(query: string): Promise<APIResponse<{query: string, contexts: RetrievedContextResponse[]}>> {
        return this.fetch('/rag/inspect', {
            method: 'POST',
            body: JSON.stringify({ query, top_k: 20 })
        });
    }

    // Ingestion
    async ingestDocument(file: File): Promise<APIResponse<{document_id: string, chunk_count: number}>> {
        const formData = new FormData();
        formData.append('file', file);
        
        return this.fetch('/ingest', {
            method: 'POST',
            body: formData
        });
    }

    // Experiments
    async listExperiments(): Promise<APIResponse<string[]>> {
        return this.fetch('/experiments');
    }

    async getExperiment(experimentId: string): Promise<APIResponse<any>> {
        return this.fetch(`/experiments/${experimentId}`);
    }
}

export const apiClient = new APIClient();
