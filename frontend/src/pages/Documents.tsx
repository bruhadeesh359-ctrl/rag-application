import React, { useState } from 'react';
import { UploadCloud, FileText, CheckCircle2, AlertCircle } from 'lucide-react';
import { apiClient } from '../api/client';

export default function Documents() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<{ document_id: string, chunk_count: number } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setResult(null);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    
    try {
      setUploading(true);
      setError(null);
      const res = await apiClient.ingestDocument(file);
      setResult(res.data);
    } catch (err: any) {
      setError(err.message || 'Failed to upload document');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-8">
      <div>
        <h2 className="text-2xl font-semibold text-white tracking-tight">Document Knowledge Base</h2>
        <p className="text-[var(--color-text-muted)] text-sm mt-1">Upload and manage documents in the RAG system.</p>
      </div>

      <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-6">
        <h3 className="text-lg font-medium text-white mb-4">Ingest New Document</h3>
        
        <div className="border-2 border-dashed border-[var(--color-border)] rounded-lg p-8 flex flex-col items-center justify-center text-center">
          <UploadCloud className="w-12 h-12 text-[var(--color-text-muted)] mb-4" />
          <p className="text-sm text-white font-medium mb-1">Select a file to upload</p>
          <p className="text-xs text-[var(--color-text-muted)] mb-4">Supports PDF, TXT, MD</p>
          
          <input 
            type="file" 
            id="file-upload" 
            className="hidden" 
            accept=".pdf,.txt,.md"
            onChange={handleFileChange}
          />
          <label 
            htmlFor="file-upload" 
            className="cursor-pointer bg-[var(--color-border)] hover:bg-[#3d424d] text-white px-4 py-2 rounded-md text-sm transition-colors"
          >
            Browse Files
          </label>
        </div>

        {file && (
          <div className="mt-4 flex items-center justify-between bg-[#1e222a] p-3 rounded-md border border-[var(--color-border)]">
            <div className="flex items-center gap-3">
              <FileText className="text-[var(--color-primary)] w-5 h-5" />
              <div className="text-sm">
                <p className="text-white font-medium">{file.name}</p>
                <p className="text-[var(--color-text-muted)] text-xs">{(file.size / 1024).toFixed(1)} KB</p>
              </div>
            </div>
            <button
              onClick={handleUpload}
              disabled={uploading}
              className="bg-[var(--color-primary)] hover:bg-blue-600 disabled:opacity-50 text-white px-4 py-1.5 rounded-md text-sm transition-colors"
            >
              {uploading ? 'Ingesting...' : 'Ingest Document'}
            </button>
          </div>
        )}

        {error && (
          <div className="mt-4 bg-red-900/20 border border-red-900/50 text-red-500 text-sm p-3 rounded-md flex items-start gap-2">
            <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
            <p>{error}</p>
          </div>
        )}

        {result && (
          <div className="mt-4 bg-green-900/20 border border-green-900/50 text-green-500 text-sm p-3 rounded-md flex items-start gap-2">
            <CheckCircle2 className="w-4 h-4 mt-0.5 shrink-0" />
            <div>
              <p className="font-medium">Document ingested successfully!</p>
              <p className="text-green-500/70 text-xs mt-1">
                ID: {result.document_id} &bull; Chunks generated: {result.chunk_count}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
