from datetime import datetime
from typing import Optional, List, Dict, Union
from pydantic import BaseModel

class RuleCondition(BaseModel):
    level: Optional[List[int]] = None
    spend_tier: Optional[str] = None
    country: Optional[List[str]] = None
    days_since_last_purchase: Optional[Dict[str, int]] = None
    ab_bucket: Optional[str] = None  # NEW
    time_window: Optional[Dict[str, str]] = None  # start_time, end_time as ISO

class Promotion(BaseModel):
    type: str
    value: Optional[Union[int, float]] = None
    item: Optional[str] = None
    weight: Optional[float] = 1.0  # NEW

class Rule(BaseModel):
    id: str
    priority: int
    conditions: RuleCondition
    promotion: Promotion


class Player(BaseModel):
    level: Optional[int] = None
    spend_tier: Optional[str] = None
    country: Optional[str] = None 
    days_since_last_purchase: Optional[int] = None
    ab_bucket: Optional[str] = None
