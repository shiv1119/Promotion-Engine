from typing import List
from threading import Lock
from models.schemas import Rule

class RuleStorage:
    def __init__(self):
        self._rules: List[Rule] = []
        self._lock = Lock()

    def load_rules(self, rule_list: List[Rule]):
        """
        Load and sort rules based on priority. Replaces any previously stored rules.

        Args:
            rule_list (List[Rule]): A list of Rule objects.

        Raises:
            ValueError: If input is not a list of Rule instances.
        """
        if not isinstance(rule_list, list) or not all(isinstance(r, Rule) for r in rule_list):
            raise ValueError("Input must be a list of Rule instances.")

        try:
            with self._lock:
                self._rules = sorted(rule_list, key=lambda r: r.priority)
        except Exception as e:
            print(f"[RuleStorageError] Failed to load rules: {e}")
            raise

    def get_rules(self) -> List[Rule]:
        """
        Returns a shallow copy of the rules.

        Returns:
            List[Rule]: The stored rules.
        """
        try:
            with self._lock:
                return self._rules.copy()
        except Exception as e:
            print(f"[RuleStorageError] Failed to retrieve rules: {e}")
            raise

# Singleton instance
rule_storage = RuleStorage()
