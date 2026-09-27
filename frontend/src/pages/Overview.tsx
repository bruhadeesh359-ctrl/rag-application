import React, { useEffect, useState } from 'react';
import { Target, AlertCircle, Clock, CheckCircle2, Activity } from 'lucide-react';
import { apiClient } from '../api/client';
import type { ObservabilitySummary } from '../api/types';

export default function Overview() {
  const [summary, setSummary] = useState<ObservabilitySummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        setLoading(true);
        const res = await apiClient.getObservabilitySummary();
        if (res.data && 'status' in res.data && res.data.status === 'NOT_YET_MEASURED') {
          // If no data yet
          setSummary({
            total_requests: 0,
            successful_requests: 0,
            abstained_requests: 0,
            failed_requests: 0,
            average_latency_ms: 0,
            p50_latency_ms: 0,
            p95_latency_ms: 0
          });
        } else {
          setSummary(res.data as ObservabilitySummary);
        }
      } catch (err: any) {
        setError(err.message || "Failed to load summary");
      } finally {
        setLoading(false);
      }
    };

    fetchSummary();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full text-[var(--color-text-muted)]">
        <Activity className="animate-spin w-8 h-8 mr-2" />
        <span>Loading telemetry...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full text-red-500 flex-col">
        <AlertCircle className="w-10 h-10 mb-4" />
        <h3 className="text-lg font-medium">Failed to load overview</h3>
        <p className="text-sm mt-2">{error}</p>
      </div>
    );
  }

  const failureRate = summary?.total_requests 
    ? ((summary.failed_requests / summary.total_requests) * 100).toFixed(1) + '%' 
    : 'N/A';

  const avgLatency = summary?.average_latency_ms
    ? (summary.average_latency_ms / 1000).toFixed(2) + 's'
    : 'N/A';

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-2xl font-semibold text-white tracking-tight">System Overview</h2>
          <p className="text-[var(--color-text-muted)] text-sm mt-1">Real-time metrics and evaluation results across the RAG pipeline.</p>
        </div>
        <div className="text-sm font-mono text-[var(--color-text-muted)] bg-[var(--color-surface)] px-3 py-1.5 rounded-md border border-[var(--color-border)] flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-green-500 inline-block"></span>
          Live Environment
        </div>
      </div>

      {/* Top Stats */}
      <div className="grid grid-cols-4 gap-4">
        <StatCard title="Total Requests" value={summary?.total_requests.toString() || "0"} icon={<Target size={16}/>} />
        <StatCard title="Average Latency" value={avgLatency} icon={<Clock size={16}/>} />
        <StatCard title="Successful" value={summary?.successful_requests.toString() || "0"} icon={<CheckCircle2 size={16}/>} />
        <StatCard title="Failure Rate" value={failureRate} icon={<AlertCircle size={16}/>} />
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Placeholder for real charts - purged mock data per rules */}
        <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-5 flex flex-col items-center justify-center h-64">
           <Activity className="w-12 h-12 text-[var(--color-border)] mb-4" />
           <p className="text-[var(--color-text-muted)]">NOT YET MEASURED</p>
           <p className="text-xs text-[#555] mt-2">Evaluation dataset chart requires historical run data.</p>
        </div>

        <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-5 flex flex-col items-center justify-center h-64">
           <Clock className="w-12 h-12 text-[var(--color-border)] mb-4" />
           <p className="text-[var(--color-text-muted)]">INSUFFICIENT DATA</p>
           <p className="text-xs text-[#555] mt-2">Latency distribution requires more trace samples.</p>
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, icon }: { title: string, value: string, icon: React.ReactNode }) {
  return (
    <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4 flex flex-col justify-between">
      <div className="flex items-center justify-between text-[var(--color-text-muted)] mb-2">
        <span className="text-xs font-medium uppercase tracking-wider">{title}</span>
        {icon}
      </div>
      <div className="flex items-baseline gap-2 mt-2">
        <span className="text-2xl font-semibold text-white">{value}</span>
      </div>
    </div>
  );
}
