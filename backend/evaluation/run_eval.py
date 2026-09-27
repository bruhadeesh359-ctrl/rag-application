import argparse
import asyncio
import os
from evaluation.evaluator import Evaluator
from evaluation.schemas import ExperimentConfig
from evaluation.tracker import ExperimentTracker

from app.services.retrievers import SparseRetriever, DenseRetriever
from app.services.vector_store import ChromaVectorStorage
from app.services.sparse_index import BM25SparseIndex
from app.services.sqlite_storage import SQLiteStorage
from app.services.embeddings import EmbeddingService
from app.services.hybrid_retriever import HybridRetriever
from app.services.fusion import RRFFusion
from app.services.reranker import CrossEncoderReranker

from app.core.database import async_session, init_db

async def main():
    parser = argparse.ArgumentParser(description="RAG Observability Lab - Evaluation CLI")
    parser.add_argument("--dataset", type=str, required=True, help="Path to evaluation dataset (.jsonl)")
    parser.add_argument("--experiment", type=str, required=True, help="Experiment ID (e.g., bm25_baseline)")
    parser.add_argument("--retriever", type=str, choices=["bm25", "dense", "hybrid_rrf", "hybrid_rerank"], required=True)
    args = parser.parse_args()

    print(f"Starting Evaluation: {args.experiment} using {args.retriever}")
    
    await init_db()
    
    async with async_session() as session:
        relational_storage = SQLiteStorage(session)
        vector_storage = ChromaVectorStorage()
        sparse_index = BM25SparseIndex()
        embedding_service = EmbeddingService()
    
        dense = DenseRetriever(vector_storage, embedding_service, relational_storage)
        bm25 = SparseRetriever(sparse_index, relational_storage)
        
        retriever = None
        if args.retriever == "bm25":
            retriever = bm25
        elif args.retriever == "dense":
            retriever = dense
        elif args.retriever == "hybrid_rrf":
            fusion = RRFFusion()
            retriever = HybridRetriever(sparse_retriever=bm25, dense_retriever=dense, fusion_service=fusion)
        elif args.retriever == "hybrid_rerank":
            fusion = RRFFusion()
            reranker = CrossEncoderReranker()
            retriever = HybridRetriever(sparse_retriever=bm25, dense_retriever=dense, fusion_service=fusion, reranker_service=reranker)

        evaluator = Evaluator(retriever=retriever)
        config = ExperimentConfig(
            experiment_id=args.experiment,
            dataset_version=args.dataset,
            retriever_type=args.retriever,
            llm_model="none"
        )
        
        print("Running evaluation...")
        result = await evaluator.run_retrieval_evaluation(args.dataset, config)
        
        print("Saving results...")
        tracker = ExperimentTracker()
        out_dir = tracker.save_experiment(result)
        
        print(f"Evaluation complete! Results saved to {out_dir}")
        if result.retrieval_metrics:
            print(f"Recall@5: {result.retrieval_metrics.recall_at_5:.4f}")
            print(f"MRR: {result.retrieval_metrics.mrr:.4f}")
            print(f"NDCG@5: {result.retrieval_metrics.ndcg_at_5:.4f}")

if __name__ == "__main__":
    asyncio.run(main())
