import { useState } from 'react';
import { Send, AlertTriangle, FileText, CheckCircle2 } from 'lucide-react';
import { apiClient } from '../api/client';
import type { RAGQueryResponseData, RetrievedContextResponse } from '../api/types';

export default function Playground() {
  const [query, setQuery] = useState('');
  const [isQuerying, setIsQuerying] = useState(false);
  const [result, setResult] = useState<RAGQueryResponseData | null>(null);
  const [inspection, setInspection] = useState<RetrievedContextResponse[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleQuery = async () => {
    setIsQuerying(true);
    setError(null);
    setResult(null);
    setInspection(null);
    try {
      // Fire both queries (this mimics what the UI wants to show)
      const [res, inspectRes] = await Promise.all([
        apiClient.queryRAG(query),
        apiClient.inspectRAG(query)
      ]);
      setResult(res.data);
      setInspection(inspectRes.data.contexts);
    } catch (err: any) {
      setError(err.message || 'Failed to query RAG service');
    } finally {
      setIsQuerying(false);
    }
  };

  const renderTextWithCitations = (text: string) => {
    // Basic citation replacing [S1] with bold tags, this can be improved
    const parts = text.split(/(\[S\d+\])/g);
    return parts.map((part, i) => {
      if (part.match(/\[S\d+\]/)) {
        return <span key={i} className="text-[var(--color-primary)] font-bold cursor-pointer hover:underline" title="See evidence">{part}</span>;
      }
      return <span key={i}>{part}</span>;
    });
  };

  return (
    <div className="flex h-full">
      {/* Left pane: Query & Answer */}
      <div className="w-1/2 p-6 border-r border-[var(--color-border)] flex flex-col h-full overflow-y-auto">
        <h2 className="text-xl font-semibold mb-6">RAG Playground</h2>
        
        <div className="relative mb-8">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask a question..."
            className="w-full bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4 pb-12 text-white focus:outline-none focus:border-[var(--color-primary)] resize-none"
            rows={4}
          />
          <button 
            onClick={handleQuery}
            disabled={!query.trim() || isQuerying}
            className="absolute bottom-3 right-3 bg-[var(--color-primary)] hover:bg-blue-600 text-white p-2 rounded-md transition-colors disabled:opacity-50"
          >
            <Send size={18} />
          </button>
        </div>

        {isQuerying && (
          <div className="flex-1 flex items-center justify-center text-[var(--color-text-muted)] animate-pulse">
            Generating response & validating citations...
          </div>
        )}

        {error && !isQuerying && (
          <div className="bg-red-900/20 border border-red-900/50 rounded-lg p-4 flex items-start gap-3">
            <AlertTriangle className="text-red-500 mt-1 shrink-0" size={20} />
            <div>
              <h4 className="text-red-500 font-medium">Error Occurred</h4>
              <p className="text-red-200/70 text-sm mt-1">{error}</p>
            </div>
          </div>
        )}

        {result && !isQuerying && (
          <div className="animate-in fade-in duration-300">
            {result.abstained ? (
              <div className="bg-amber-900/20 border border-amber-900/50 rounded-lg p-4 flex items-start gap-3">
                <AlertTriangle className="text-amber-500 mt-1 shrink-0" size={20} />
                <div>
                  <h4 className="text-amber-500 font-medium">Insufficient Evidence</h4>
                  <p className="text-amber-200/70 text-sm mt-1">{result.fallback_reason || result.answer}</p>
                </div>
              </div>
            ) : (
              <div>
                <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-5 mb-6">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-xs font-semibold text-[var(--color-text-muted)] uppercase tracking-wider">
                      Generated Answer
                    </h3>
                    {result.groundedness && result.groundedness.score > 0.8 && (
                      <span className="bg-[var(--color-success)]/10 text-[var(--color-success)] px-2 py-0.5 rounded text-[10px] flex items-center gap-1">
                        <CheckCircle2 size={10} /> Grounded ({(result.groundedness.score * 100).toFixed(0)}%)
                      </span>
                    )}
                  </div>
                  <p className="text-[var(--color-text-main)] leading-relaxed whitespace-pre-wrap">
                    {renderTextWithCitations(result.answer)}
                  </p>
                </div>

                <div className="space-y-3">
                  <h3 className="text-xs font-semibold text-[var(--color-text-muted)] uppercase tracking-wider mb-2">Retrieved Evidence</h3>
                  {result.citations.length === 0 && (
                    <p className="text-sm text-[var(--color-text-muted)]">No citations provided by the model.</p>
                  )}
                  {result.citations.map((cite, i) => (
                    <div key={i} className="bg-[#1e222a] border border-[#2d3139] p-3 rounded-md text-sm">
                      <div className="flex items-center gap-2 mb-2 text-xs text-[var(--color-primary)] font-mono">
                        <FileText size={14} />
                        {cite.token} - {cite.filename || cite.document_id}
                        {cite.page && <span> (Page {cite.page})</span>}
                      </div>
                      <p className="text-[var(--color-text-muted)] italic">"{cite.text}"</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Right pane: Inspector */}
      <div className="w-1/2 p-6 bg-[#0a0b0e] h-full overflow-y-auto">
        <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
          Retrieval Inspector
        </h2>
        
        {!inspection ? (
          <div className="text-sm text-[var(--color-text-muted)] flex items-center justify-center h-64 border border-dashed border-[var(--color-border)] rounded-lg">
            Run a query to inspect the retrieval pipeline
          </div>
        ) : (
          <div className="space-y-4">
            {inspection.length === 0 && (
              <p className="text-sm text-[var(--color-text-muted)]">No contexts retrieved.</p>
            )}
            {inspection.map((ctx, idx) => (
              <InspectorCard 
                key={ctx.chunk_id} 
                title={`Context ${idx + 1} (${ctx.retrieval_method})`} 
                score={ctx.score.toFixed(3)} 
                rank={ctx.rank.toString()} 
                filename={ctx.provenance?.filename}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function InspectorCard({ title, score, rank, filename }: { title: string, score: string, rank: string, filename?: string }) {
  return (
    <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4">
      <div className="flex justify-between items-center mb-3">
        <h3 className="text-sm font-medium text-white">{title}</h3>
      </div>
      <div className="flex gap-4 text-sm font-mono mb-2">
        <div>
          <span className="text-[var(--color-text-muted)] mr-2">Rank</span>
          <span className="text-white">#{rank}</span>
        </div>
        <div>
          <span className="text-[var(--color-text-muted)] mr-2">Score</span>
          <span className="text-[var(--color-success)]">{score}</span>
        </div>
      </div>
      {filename && (
        <div className="text-xs text-[var(--color-text-muted)]">
          Source: {filename}
        </div>
      )}
    </div>
  );
}
