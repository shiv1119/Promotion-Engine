from fastapi import APIRouter, HTTPException
from models.schemas import Player
from services.evaluator import evaluate_rules, get_metrics
from services.loader import load_rules_from_yaml
from typing import Dict

router = APIRouter()

from typing import Dict, Optional

@router.post("/promotion", response_model=Dict[str, Optional[dict]])  # Allow None
def get_promotion(player: Player):
    try:
        promotion = evaluate_rules(player)
        return {"promotion": promotion.model_dump() if promotion else None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reload", response_model=Dict[str, str])
def reload_rules():
    """
    Reload rules from the YAML file into memory.
    """
    try:
        load_rules_from_yaml()
        return {"status": "Rules reloaded successfully"}
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="rules.yaml file not found")
    
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Invalid rule format: {str(ve)}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error during reload: {str(e)}")


@router.get("/metrics", response_model=Dict[str, float])
def metrics():
    """
    Return rule evaluation performance metrics.
    """
    try:
        return get_metrics()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch metrics: {str(e)}")
