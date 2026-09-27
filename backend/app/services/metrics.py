import math
from typing import List

class RetrievalMetrics:
    @staticmethod
    def recall_at_k(retrieved_ids: List[str], relevant_ids: List[str], k: int) -> float:
        if not relevant_ids:
            return 0.0
        retrieved_k = retrieved_ids[:k]
        hits = sum(1 for rid in relevant_ids if rid in retrieved_k)
        return hits / len(relevant_ids)

    @staticmethod
    def mrr(retrieved_ids: List[str], relevant_ids: List[str]) -> float:
        for i, rid in enumerate(retrieved_ids):
            if rid in relevant_ids:
                return 1.0 / (i + 1)
        return 0.0

    @staticmethod
    def ndcg_at_k(retrieved_ids: List[str], relevant_ids: List[str], k: int) -> float:
        retrieved_k = retrieved_ids[:k]
        
        dcg = 0.0
        for i, rid in enumerate(retrieved_k):
            if rid in relevant_ids:
                # rel_i is 1 for binary relevance
                dcg += 1.0 / math.log2(i + 2) # i is 0-indexed
                
        idcg = 0.0
        for i in range(min(len(relevant_ids), k)):
            idcg += 1.0 / math.log2(i + 2)
            
        if idcg == 0.0:
            return 0.0
            
        return dcg / idcg
