from datetime import datetime
from typing import Optional, List, Dict, Union
from pydantic import BaseModel

#This schemas describes that  who should receive a promotion by defining a set of conditions that the player must meet
class RuleCondition(BaseModel):
    level: Optional[List[int]] = None
    spend_tier: Optional[str] = None
    country: Optional[List[str]] = None
    days_since_last_purchase: Optional[Dict[str, int]] = None
    ab_bucket: Optional[str] = None  
    time_window: Optional[Dict[str, str]] = None 

#This schema describes what will be reward if a player qualifies
class Promotion(BaseModel):
    type: str
    value: Optional[Union[int, float]] = None
    item: Optional[str] = None
    weight: Optional[float] = 1.0 

# This schema represents a full promotion rule: both the condition and the reward.
class Rule(BaseModel):
    id: str
    priority: int
    conditions: RuleCondition
    promotion: Promotion

# This schema represents a player profile who is checking if they are eligible for any promotion.
class Player(BaseModel):
    level: Optional[int] = None
    spend_tier: Optional[str] = None
    country: Optional[str] = None 
    days_since_last_purchase: Optional[int] = None
    ab_bucket: Optional[str] = None
