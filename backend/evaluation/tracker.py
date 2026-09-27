import os
import json
from datetime import datetime
from typing import Dict, Any
from evaluation.schemas import ExperimentResult

class ExperimentTracker:
    def __init__(self, base_dir: str = "evaluation/results"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def save_experiment(self, result: ExperimentResult) -> str:
        """
        Saves the experiment to evaluation/results/<experiment_id>/
        """
        exp_id = result.config.experiment_id
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Ensure unique directory if experiment run multiple times
        exp_dir = os.path.join(self.base_dir, f"{exp_id}_{timestamp_str}")
        os.makedirs(exp_dir, exist_ok=True)

        # Separate files to avoid massive JSON blobs
        
        # 1. Config
        with open(os.path.join(exp_dir, "config.json"), "w") as f:
            f.write(result.config.model_dump_json(indent=2))
            
        # 2. Retrieval Metrics
        if result.retrieval_metrics:
            with open(os.path.join(exp_dir, "retrieval_metrics.json"), "w") as f:
                f.write(result.retrieval_metrics.model_dump_json(indent=2))
                
        # 3. Generation Metrics
        if result.generation_metrics:
            with open(os.path.join(exp_dir, "generation_metrics.json"), "w") as f:
                f.write(result.generation_metrics.model_dump_json(indent=2))
                
        # 4. Latency
        if result.latency_metrics:
            with open(os.path.join(exp_dir, "latency_metrics.json"), "w") as f:
                f.write(result.latency_metrics.model_dump_json(indent=2))
                
        # 5. Errors
        if result.errors:
            with open(os.path.join(exp_dir, "errors.json"), "w") as f:
                json.dump(result.errors, f, indent=2)

        return exp_dir
