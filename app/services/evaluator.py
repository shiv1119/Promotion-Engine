from app.models.schemas import Player
from app.storage.rule_store import rule_storage
import time
import random
from datetime import datetime
from typing import Optional, List

# In-memory evaluation metrics
metrics = {
    "total_evaluations": 0,
    "hits": 0,
    "misses": 0,
    "total_latency": 0.0,
}

# This is a helper function to check if current time falls within the given time window
def _check_time_window(time_window: dict) -> bool:
    try:
        now = datetime.utcnow()
        start = time_window.get("start")
        end = time_window.get("end")

        if start:
            start = datetime.fromisoformat(start)
            if now < start:
                return False

        if end:
            end = datetime.fromisoformat(end)
            if now > end:
                return False
        return True

    except Exception as e:
        print(f"[TimeWindowError] Invalid time window: {e}")
        return False


# This function evaluates conditions of a promotion rule
def match_rule(rule, player: Player) -> bool:
    try:
        c = rule.conditions

        if c.level and (player.level is None or player.level not in c.level):
            return False

        if c.spend_tier and c.spend_tier != player.spend_tier:
            return False

        if c.country and (player.country is None or player.country not in c.country):
            return False

        if c.days_since_last_purchase:
            if player.days_since_last_purchase is None:
                return False
            min_days = c.days_since_last_purchase.get("min", float("-inf"))
            max_days = c.days_since_last_purchase.get("max", float("inf"))
            if not (min_days <= player.days_since_last_purchase <= max_days):
                return False

        if c.ab_bucket and getattr(player, "ab_bucket", None) != c.ab_bucket:
            return False

        if c.time_window and not _check_time_window(c.time_window):
            return False
        
        return True

    except Exception as e:
        print(f"[MatchRuleError] Failed to match rule '{getattr(rule, 'id', 'unknown')}': {e}")
        return False


# This function evaluates all the given rules and returns the selected promotion for a player if any match on any of the satisfying conditions. Used weighted randomness if multiples promotions are matched.
def evaluate_rules(player: Player) -> Optional[dict]:
    try:
        start = time.time()
        matching_promotions = []

        for rule in rule_storage.get_rules():
            if match_rule(rule, player):
                matching_promotions.append(rule.promotion)

        promotion = None
        if matching_promotions:
            weights = [p.weight or 1.0 for p in matching_promotions]
            promotion = random.choices(matching_promotions, weights=weights, k=1)[0]

        latency = time.time() - start
        metrics["total_evaluations"] += 1
        metrics["total_latency"] += latency
        if promotion:
            metrics["hits"] += 1
        else:
            metrics["misses"] += 1

        return promotion

    except Exception as e:
        print(f"[EvaluateRulesError] Failed to evaluate rules for player {player}: {e}")
        return None

# This function calculates and returns aggregate metrics about rule evaluations.
def get_metrics() -> dict:
    try:
        avg_latency = (
            metrics["total_latency"] / metrics["total_evaluations"]
            if metrics["total_evaluations"] else 0
        )
        return {
            "total_evaluations": metrics["total_evaluations"],
            "hits": metrics["hits"],
            "misses": metrics["misses"],
            "avg_latency_ms": round(avg_latency * 1000, 2)
        }

    except Exception as e:
        print(f"[MetricsError] Failed to retrieve metrics: {e}")
        return {
            "total_evaluations": 0,
            "hits": 0,
            "misses": 0,
            "avg_latency_ms": 0.0
        }
