from fastapi import APIRouter, HTTPException
from app.models.schemas import Player
from app.services.evaluator import evaluate_rules, get_metrics
from app.services.loader import load_rules_from_yaml
from typing import Dict

router = APIRouter()

from typing import Dict, Optional

# This routes takes optional inputs from player's profile (like their level, country, spend tier, etc.) and and checks all promotion rules to see if the player qualifies for a promotion.
@router.post("/promotion", response_model=Dict[str, Optional[dict]])
def get_promotion(player: Player):
    try:
        promotion = evaluate_rules(player)
        return {"promotion": promotion.model_dump() if promotion else None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# This routes reloads promotion rules from yaml into memory
@router.post("/reload", response_model=Dict[str, str])
def reload_rules():
    try:
        load_rules_from_yaml()
        return {"status": "Rules reloaded successfully"}
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="rules.yaml file not found")
    
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Rules format are invalid. Try formatting it: {str(ve)}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error during reload: {str(e)}")

# This is going to return rules evaluation performance metrics
@router.get("/metrics", response_model=Dict[str, float])
def metrics():
    try:
        return get_metrics()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load metrics: {str(e)}")
