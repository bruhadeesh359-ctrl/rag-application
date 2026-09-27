from typing import List, Dict, Any
from evaluation.schemas import GenerationMetrics

def compute_generation_metrics(generation_results: List[Dict[str, Any]]) -> GenerationMetrics:
    """
    Computes aggregated generation metrics from a list of RAGService output validation blocks.
    Each result in `generation_results` should look like the "validation" block from RAGService:
    {
        "citations_valid": True,
        "citation_details": {
            "is_valid": True,
            "citations_found": [...],
            "invalid_citations": [...]
        },
        "groundedness": {
            "is_grounded": True,
            "supported_claims": [...],
            "unsupported_claims": [...]
        }
    }
    """
    if not generation_results:
        return GenerationMetrics()

    total_claims = 0
    total_supported_claims = 0
    total_unsupported_claims = 0
    total_citations_expected = 0
    total_valid_citations = 0
    abstained_count = 0
    
    for result in generation_results:
        # Check abstention
        if result.get("abstained", False):
            abstained_count += 1
            continue
            
        validation = result.get("validation", {})
        groundedness = validation.get("groundedness", {})
        
        sup_claims = groundedness.get("supported_claims", [])
        unsup_claims = groundedness.get("unsupported_claims", [])
        
        total_supported_claims += len(sup_claims)
        total_unsupported_claims += len(unsup_claims)
        total_claims += len(sup_claims) + len(unsup_claims)

        citation_details = validation.get("citation_details", {})
        valid_cites = citation_details.get("citations_found", [])
        invalid_cites = citation_details.get("invalid_citations", [])
        
        total_valid_citations += len(valid_cites)
        total_citations_expected += len(valid_cites) + len(invalid_cites)

    # Compute rates
    total_evaluated = len(generation_results)
    abstention_rate = abstained_count / total_evaluated if total_evaluated > 0 else 0.0
    
    groundedness_rate = total_supported_claims / total_claims if total_claims > 0 else 1.0
    unsupported_claim_rate = total_unsupported_claims / total_claims if total_claims > 0 else 0.0
    
    citation_coverage = total_valid_citations / total_citations_expected if total_citations_expected > 0 else 1.0
    # If no citations were expected/found but claims existed, it's a structural coverage miss.
    if total_citations_expected == 0 and total_claims > 0:
        citation_coverage = 0.0

    return GenerationMetrics(
        groundedness=groundedness_rate,
        unsupported_claim_rate=unsupported_claim_rate,
        citation_coverage=citation_coverage,
        abstention_rate=abstention_rate
    )
