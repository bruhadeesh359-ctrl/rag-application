import math
from typing import List

def recall_at_k(retrieved_chunk_ids: List[str], relevant_chunk_ids: List[str], k: int) -> float:
    """
    Measures if ANY relevant chunk is in the top K retrieved results.
    Returns 1.0 if yes, 0.0 if no.
    If there are no relevant chunks, returns 1.0 (since we retrieved correctly by finding nothing).
    """
    if not relevant_chunk_ids:
        # If there is no ground truth evidence (e.g. out of domain query), 
        # and we retrieved nothing, it's a success? 
        # Actually for standard Recall, if |relevant| == 0, it's undefined or 1.0. Let's return 1.0 for empty truth.
        return 1.0

    top_k = retrieved_chunk_ids[:k]
    for chunk_id in top_k:
        if chunk_id in relevant_chunk_ids:
            return 1.0
    return 0.0


def mrr(retrieved_chunk_ids: List[str], relevant_chunk_ids: List[str]) -> float:
    """
    Mean Reciprocal Rank.
    Finds the rank of the *first* relevant chunk. Returns 1 / rank.
    """
    if not relevant_chunk_ids:
        return 1.0
    
    for i, chunk_id in enumerate(retrieved_chunk_ids):
        if chunk_id in relevant_chunk_ids:
            return 1.0 / (i + 1)
    
    return 0.0


def ndcg_at_k(retrieved_chunk_ids: List[str], relevant_chunk_ids: List[str], k: int) -> float:
    """
    Normalized Discounted Cumulative Gain at K.
    Binary relevance: 1 if chunk in relevant_chunk_ids else 0.
    """
    if not relevant_chunk_ids:
        return 1.0

    dcg = 0.0
    top_k = retrieved_chunk_ids[:k]
    for i, chunk_id in enumerate(top_k):
        rel = 1 if chunk_id in relevant_chunk_ids else 0
        # Discount: log2(rank + 1). Rank is 1-indexed, so i + 2
        dcg += rel / math.log2(i + 2)
    
    # IDCG (Ideal DCG)
    # The ideal ranking places all relevant items at the top.
    idcg = 0.0
    ideal_k = min(k, len(relevant_chunk_ids))
    for i in range(ideal_k):
        idcg += 1 / math.log2(i + 2)
        
    if idcg == 0.0:
        return 0.0
        
    return dcg / idcg
