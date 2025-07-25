from typing import List
from threading import Lock
from app.models.schemas import Rule

class RuleStorage:
    def __init__(self):
        self._rules: List[Rule] = []
        self._lock = Lock()

    # This method loads the rules and sort the values based on priority. It replaces any sorted value
    def load_rules(self, rule_list: List[Rule]):
        if not isinstance(rule_list, list) or not all(isinstance(r, Rule) for r in rule_list):
            raise ValueError("Input must be a list of Rule instances.")

        try:
            with self._lock:
                self._rules = sorted(rule_list, key=lambda r: r.priority)
        except Exception as e:
            print(f"[RuleStorageError] Failed to load rules: {e}")
            raise

    # This method returns a shallow copy of the rules
    def get_rules(self) -> List[Rule]:
        try:
            with self._lock:
                return self._rules.copy()
        except Exception as e:
            print(f"[RuleStorageError] Failed to retrieve rules: {e}")
            raise

rule_storage = RuleStorage()
