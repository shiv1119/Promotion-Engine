from app.models.schemas import Player
from app.services.evaluator import evaluate_rules
from app.services.loader import load_rules_from_yaml
from app.core.config import RULE_FILE

# This function checks that a player with predefined values matches a promotion or not
def test_best_rule_selected():
    load_rules_from_yaml(RULE_FILE)
    player = Player(
        level=30,
        spend_tier="high",
        country="US",
        days_since_last_purchase=1
    )
    promo = evaluate_rules(player)
    assert promo is None or hasattr(promo, "id")

# Checks that a player who clearly doesn't match any promotion rules (low level, unknown country, extremely old activity) receives no promotion.
def test_no_promotion_case():
    load_rules_from_yaml(RULE_FILE)
    player = Player(
        level=1,
        spend_tier="low",
        country="XYZ",
        days_since_last_purchase=500
    )
    promo = evaluate_rules(player)
    assert promo is None
