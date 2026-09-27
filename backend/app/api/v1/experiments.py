from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
import os
import json

from app.schemas.api import APIResponse

router = APIRouter(prefix="/experiments", tags=["experiments"])

@router.get("", response_model=APIResponse[List[str]])
async def list_experiments():
    base_dir = "evaluation/results"
    if not os.path.exists(base_dir):
        return APIResponse(data=[])
        
    experiments = []
    for d in os.listdir(base_dir):
        if os.path.isdir(os.path.join(base_dir, d)):
            experiments.append(d)
            
    return APIResponse(data=experiments)

@router.get("/{experiment_id}", response_model=APIResponse[Dict[str, Any]])
async def get_experiment(experiment_id: str):
    # Retrieve metadata from the evaluation output directory
    base_dir = "evaluation/results"
    exp_dir = os.path.join(base_dir, experiment_id)
    if not os.path.exists(exp_dir):
        raise HTTPException(status_code=404, detail="Experiment not found")
        
    cfg_path = os.path.join(exp_dir, "config.json")
    if os.path.exists(cfg_path):
        with open(cfg_path, "r") as f:
            config = json.load(f)
            return APIResponse(data=config)
            
    return APIResponse(data={"experiment_id": experiment_id, "status": "UNKNOWN"})
