from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import os
import json
import asyncio

from app.schemas.api import APIResponse
from pydantic import BaseModel

router = APIRouter(prefix="/evaluation", tags=["evaluation"])

class RunEvalRequest(BaseModel):
    dataset_path: str
    experiment_id: str
    retriever: str # "bm25", "dense", "hybrid_rrf", "hybrid_rerank"

@router.post("/run", response_model=APIResponse[Dict[str, Any]])
async def run_evaluation(request: RunEvalRequest):
    # Run the CLI as a subprocess to keep isolation.
    cmd = [
        "python", "-m", "evaluation.run_eval",
        "--dataset", request.dataset_path,
        "--experiment", request.experiment_id,
        "--retriever", request.retriever
    ]
    
    # Fire and forget
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    return APIResponse(
        data={"message": "Evaluation job started.", "experiment_id": request.experiment_id}
    )

@router.get("/runs", response_model=APIResponse[List[str]])
async def list_experiments():
    base_dir = "evaluation/results"
    if not os.path.exists(base_dir):
        return APIResponse(data=[])
        
    experiments = []
    for d in os.listdir(base_dir):
        if os.path.isdir(os.path.join(base_dir, d)):
            experiments.append(d)
            
    return APIResponse(data=experiments)

@router.get("/runs/{experiment_id}", response_model=APIResponse[Dict[str, Any]])
async def get_experiment(experiment_id: str):
    base_dir = "evaluation/results"
    exp_dir = os.path.join(base_dir, experiment_id)
    if not os.path.exists(exp_dir):
        # We must return an explicit NOT_YET_MEASURED if it hasn't run.
        return APIResponse(data={"status": "NOT_YET_MEASURED", "message": "Evaluation has not been run or completed."})
        
    result = {"status": "MEASURED"}
    
    cfg_path = os.path.join(exp_dir, "config.json")
    if os.path.exists(cfg_path):
        with open(cfg_path, "r") as f:
            result["config"] = json.load(f)
            
    ret_path = os.path.join(exp_dir, "retrieval_metrics.json")
    if os.path.exists(ret_path):
        with open(ret_path, "r") as f:
            result["retrieval_metrics"] = json.load(f)
            
    gen_path = os.path.join(exp_dir, "generation_metrics.json")
    if os.path.exists(gen_path):
        with open(gen_path, "r") as f:
            result["generation_metrics"] = json.load(f)
            
    lat_path = os.path.join(exp_dir, "latency_metrics.json")
    if os.path.exists(lat_path):
        with open(lat_path, "r") as f:
            result["latency_metrics"] = json.load(f)
            
    return APIResponse(data=result)
