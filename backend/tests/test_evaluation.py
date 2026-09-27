import pytest
from evaluation.metrics.retrieval import recall_at_k, mrr, ndcg_at_k

def test_recall_at_k():
    retrieved = ["c1", "c2", "c3", "c4"]
    relevant = ["c3"]
    
    # c3 is at index 2 (rank 3)
    assert recall_at_k(retrieved, relevant, 1) == 0.0
    assert recall_at_k(retrieved, relevant, 2) == 0.0
    assert recall_at_k(retrieved, relevant, 3) == 1.0
    assert recall_at_k(retrieved, relevant, 5) == 1.0

def test_mrr():
    retrieved = ["c1", "c2", "c3", "c4"]
    assert mrr(retrieved, ["c1"]) == 1.0       # Rank 1
    assert mrr(retrieved, ["c2"]) == 0.5       # Rank 2
    assert mrr(retrieved, ["c3"]) == 1.0 / 3   # Rank 3
    assert mrr(retrieved, ["c5"]) == 0.0       # Not found

def test_ndcg_at_k():
    retrieved = ["c1", "c2", "c3", "c4"]
    # All retrieved are relevant, so DCG = IDCG = 1.0
    assert ndcg_at_k(retrieved, ["c1", "c2", "c3"], 3) == 1.0
    
    # Only c2 is relevant
    # DCG = 1 / log2(1 + 2) = 1 / log2(3) = 0.6309
    # IDCG = 1 / log2(2) = 1.0
    # NDCG = 0.6309
    assert abs(ndcg_at_k(retrieved, ["c2"], 3) - 0.6309) < 0.01

    # Empty retrieved array but we have relevant targets
    assert ndcg_at_k([], ["c1"], 3) == 0.0
