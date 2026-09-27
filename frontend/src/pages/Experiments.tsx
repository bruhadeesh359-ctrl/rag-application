import { useEffect, useState } from 'react';
import { FlaskConical, Activity } from 'lucide-react';
import { apiClient } from '../api/client';

export default function Experiments() {
  const [experiments, setExperiments] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchExperiments = async () => {
      try {
        setLoading(true);
        const res = await apiClient.listExperiments();
        setExperiments(res.data);
      } catch (err: any) {
        setError(err.message || 'Failed to list experiments');
      } finally {
        setLoading(false);
      }
    };
    fetchExperiments();
  }, []);

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <div>
        <h2 className="text-2xl font-semibold text-white tracking-tight flex items-center gap-2">
          <FlaskConical className="text-purple-400" />
          Evaluation Experiments
        </h2>
        <p className="text-[var(--color-text-muted)] text-sm mt-1">Review historical evaluation runs.</p>
      </div>

      <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg">
        {loading ? (
          <div className="p-8 flex justify-center text-gray-500"><Activity className="animate-spin mr-2"/> Loading...</div>
        ) : error ? (
          <div className="p-8 text-red-500">{error}</div>
        ) : experiments.length === 0 ? (
          <div className="p-8 text-center text-gray-500">No experiments found.</div>
        ) : (
          <div className="divide-y divide-[var(--color-border)]">
            {experiments.map((exp, idx) => (
              <div key={idx} className="p-4 flex items-center justify-between hover:bg-[#1c1f26] transition-colors">
                <span className="font-mono text-sm text-[var(--color-primary)]">{exp}</span>
                <span className="text-xs text-gray-500">Click to view details (Coming soon)</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
