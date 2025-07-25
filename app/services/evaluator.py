from models.schemas import Player
from storage.rule_store import rule_storage
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


def _check_time_window(time_window: dict) -> bool:
    """
    Helper to check if current time is within the given time window.
    """
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
        # Fail-safe: if time format is wrong or invalid structure
        print(f"[TimeWindowError] Invalid time window: {e}")
        return False


def match_rule(rule, player: Player) -> bool:
    try:
        print(f"Evaluating rule: {rule.id}")
        c = rule.conditions

        if c.level and (player.level is None or player.level not in c.level):
            print(f"  Rule {rule.id} failed: level mismatch")
            return False

        if c.spend_tier and c.spend_tier != player.spend_tier:
            print(f"  Rule {rule.id} failed: spend_tier mismatch")
            return False

        if c.country and (player.country is None or player.country not in c.country):
            print(f"  Rule {rule.id} failed: country mismatch")
            return False

        if c.days_since_last_purchase:
            if player.days_since_last_purchase is None:
                print(f"  Rule {rule.id} failed: no days_since_last_purchase")
                return False
            min_days = c.days_since_last_purchase.get("min", float("-inf"))
            max_days = c.days_since_last_purchase.get("max", float("inf"))
            if not (min_days <= player.days_since_last_purchase <= max_days):
                print(f"  Rule {rule.id} failed: days_since_last_purchase out of range")
                return False

        if c.ab_bucket and getattr(player, "ab_bucket", None) != c.ab_bucket:
            print(f"  Rule {rule.id} failed: ab_bucket mismatch")
            return False

        if c.time_window and not _check_time_window(c.time_window):
            print(f"  Rule {rule.id} failed: time_window invalid")
            return False

        print(f"  Rule {rule.id} matched!")
        return True

    except Exception as e:
        print(f"[MatchRuleError] Failed to match rule '{getattr(rule, 'id', 'unknown')}': {e}")
        return False



def evaluate_rules(player: Player) -> Optional[dict]:
    """
    Evaluates all rules and returns the selected promotion for a player (if any).
    Uses weighted randomness if multiple promotions match.
    """
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


def get_metrics() -> dict:
    """
    Returns aggregate metrics about rule evaluations.
    """
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
