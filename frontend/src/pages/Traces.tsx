import { useEffect, useState } from 'react';
import { CheckCircle2, AlertCircle, Activity, Database, Zap, Bot, ChevronLeft } from 'lucide-react';
import { apiClient } from '../api/client';
import type { Trace, TraceSpan } from '../api/types';

function FileTextIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><line x1="10" y1="9" x2="8" y2="9"/></svg>
  )
}

export default function Traces() {
  const [traces, setTraces] = useState<Trace[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [selectedTraceId, setSelectedTraceId] = useState<string | null>(null);
  const [traceDetails, setTraceDetails] = useState<Trace | null>(null);
  const [loadingDetails, setLoadingDetails] = useState(false);

  const fetchTraces = async () => {
    try {
      setLoading(true);
      const res = await apiClient.getTraces(1, 50);
      setTraces(res.data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch traces');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTraces();
  }, []);

  const loadTrace = async (id: string) => {
    setSelectedTraceId(id);
    try {
      setLoadingDetails(true);
      const res = await apiClient.getTrace(id);
      setTraceDetails(res.data);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoadingDetails(false);
    }
  };

  const getStageIcon = (stage: string) => {
    const s = stage.toLowerCase();
    if (s.includes('retrieve') || s.includes('bm25') || s.includes('dense')) return <Database size={16}/>;
    if (s.includes('rrf') || s.includes('fusion')) return <Zap size={16}/>;
    if (s.includes('rerank')) return <Activity size={16}/>;
    if (s.includes('llm') || s.includes('generate')) return <Bot size={16}/>;
    if (s.includes('context')) return <FileTextIcon />;
    return <Activity size={16}/>;
  };

  const getStageColor = (stage: string) => {
    const s = stage.toLowerCase();
    if (s.includes('retrieve')) return 'text-blue-400';
    if (s.includes('llm')) return 'text-emerald-400';
    if (s.includes('rerank')) return 'text-purple-400';
    return 'text-gray-400';
  };

  if (selectedTraceId) {
    if (loadingDetails) {
      return <div className="p-8 flex justify-center"><Activity className="animate-spin text-gray-500 w-8 h-8"/></div>;
    }

    if (!traceDetails) {
      return (
        <div className="p-8">
          <button onClick={() => setSelectedTraceId(null)} className="flex items-center text-blue-400 mb-4 hover:underline">
            <ChevronLeft size={16} /> Back
          </button>
          <div className="text-red-500">Failed to load trace details.</div>
        </div>
      );
    }

    return (
      <div className="p-8 max-w-5xl mx-auto">
        <button onClick={() => setSelectedTraceId(null)} className="flex items-center text-blue-400 mb-6 hover:underline">
          <ChevronLeft size={16} /> Back to Traces
        </button>

        <h2 className="text-2xl font-semibold text-white tracking-tight mb-8">Trace Inspection</h2>

        <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg overflow-hidden">
          {/* Header */}
          <div className="p-5 border-b border-[var(--color-border)] flex justify-between items-start bg-[#1c1f26]">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <span className="font-mono text-sm text-[var(--color-primary)] bg-[var(--color-primary)]/10 px-2 py-0.5 rounded">
                  {traceDetails.trace_id}
                </span>
                {traceDetails.status === 'success' ? (
                  <span className="text-xs font-medium text-[var(--color-success)] bg-[var(--color-success)]/10 px-2 py-0.5 rounded flex items-center gap-1">
                    <CheckCircle2 size={12}/> SUCCESS
                  </span>
                ) : (
                  <span className="text-xs font-medium text-red-500 bg-red-500/10 px-2 py-0.5 rounded flex items-center gap-1">
                    <AlertCircle size={12}/> {traceDetails.status.toUpperCase()}
                  </span>
                )}
              </div>
              <h3 className="text-lg text-white font-medium">Trace {traceDetails.trace_id.split('_').pop()}</h3>
              <p className="text-xs text-gray-400 mt-1">{new Date(traceDetails.start_time).toLocaleString()}</p>
            </div>
            <div className="text-right">
              <div className="text-sm text-[var(--color-text-muted)] mb-1">Total Latency</div>
              <div className="text-2xl font-semibold text-white flex items-baseline gap-1 justify-end">
                {traceDetails.duration_ms?.toFixed(0) || 0}<span className="text-sm font-normal text-[var(--color-text-muted)]">ms</span>
              </div>
            </div>
          </div>

          {/* Timeline */}
          <div className="p-6">
            <h4 className="text-sm font-semibold text-[var(--color-text-muted)] uppercase tracking-wider mb-6">Execution Pipeline</h4>
            
            <div className="space-y-4">
              {traceDetails.spans?.length === 0 && <p className="text-gray-500">No spans recorded.</p>}
              {traceDetails.spans?.map((stage: TraceSpan, i: number) => {
                const totalMs = traceDetails.duration_ms || 1;
                const width = Math.max(2, ((stage.duration_ms || 0) / totalMs) * 100);
                const colorClass = getStageColor(stage.stage);
                
                return (
                  <div key={stage.span_id || i} className="flex items-center gap-4">
                    <div className={`w-8 h-8 rounded-full bg-[#1c1f26] border border-[#2d3139] flex items-center justify-center shrink-0 ${colorClass}`}>
                      {getStageIcon(stage.stage)}
                    </div>
                    
                    <div className="flex-1">
                      <div className="flex justify-between text-sm mb-1.5">
                        <span className="text-[var(--color-text-main)] font-medium">{stage.stage} {stage.status !== 'success' && <span className="text-red-500">({stage.status})</span>}</span>
                        <span className="text-[var(--color-text-muted)] font-mono">{(stage.duration_ms || 0).toFixed(0)}ms</span>
                      </div>
                      
                      <div className="h-1.5 bg-[#1c1f26] rounded-full overflow-hidden flex w-full">
                        <div 
                          className={`h-full bg-current ${colorClass}`} 
                          style={{ width: `${width}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
          
          {/* Token Usage */}
          {traceDetails.token_usage && (
            <div className="p-5 border-t border-[var(--color-border)] bg-[#1c1f26] flex gap-8 text-sm">
              <div>
                <span className="text-[var(--color-text-muted)] mr-2">Input Tokens:</span>
                <span className="text-white font-mono">{traceDetails.token_usage?.input_tokens || 'N/A'}</span>
              </div>
              <div>
                <span className="text-[var(--color-text-muted)] mr-2">Output Tokens:</span>
                <span className="text-white font-mono">{traceDetails.token_usage?.output_tokens || 'N/A'}</span>
              </div>
              <div>
                <span className="text-[var(--color-text-muted)] mr-2">Total Tokens:</span>
                <span className="text-white font-mono">{traceDetails.token_usage?.total_tokens || 'N/A'}</span>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  // List View
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <div>
        <h2 className="text-2xl font-semibold text-white tracking-tight">Traces</h2>
        <p className="text-[var(--color-text-muted)] text-sm mt-1">Review end-to-end telemetry and execution spans.</p>
      </div>

      <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg">
        {loading ? (
          <div className="p-8 flex justify-center text-gray-500"><Activity className="animate-spin mr-2"/> Loading traces...</div>
        ) : error ? (
          <div className="p-8 text-red-500">{error}</div>
        ) : traces.length === 0 ? (
          <div className="p-8 text-center text-gray-500">No traces found. Run some RAG queries first.</div>
        ) : (
          <table className="w-full text-left text-sm">
            <thead className="bg-[#1c1f26] text-gray-400 border-b border-[var(--color-border)]">
              <tr>
                <th className="px-4 py-3 font-medium">Trace ID</th>
                <th className="px-4 py-3 font-medium">Time</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Duration (ms)</th>
                <th className="px-4 py-3 font-medium"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--color-border)]">
              {traces.map(trace => (
                <tr key={trace.trace_id} className="hover:bg-[#1c1f26]/50 transition-colors">
                  <td className="px-4 py-3 font-mono text-[var(--color-primary)]">{trace.trace_id}</td>
                  <td className="px-4 py-3 text-gray-300">{new Date(trace.start_time).toLocaleString()}</td>
                  <td className="px-4 py-3">
                    {trace.status === 'success' ? (
                      <span className="text-[var(--color-success)] flex items-center gap-1"><CheckCircle2 size={14}/> Success</span>
                    ) : (
                      <span className="text-red-500 flex items-center gap-1"><AlertCircle size={14}/> Error</span>
                    )}
                  </td>
                  <td className="px-4 py-3 font-mono text-gray-300">{trace.duration_ms?.toFixed(0)}</td>
                  <td className="px-4 py-3 text-right">
                    <button onClick={() => loadTrace(trace.trace_id)} className="text-blue-400 hover:underline text-xs">
                      Inspect
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
