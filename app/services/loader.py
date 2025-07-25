import os
import yaml
from models.schemas import Rule
from storage.rule_store import rule_storage
from typing import Optional


def load_rules_from_yaml(file_path: Optional[str] = None) -> None:
    """
    Loads promotion rules from a YAML file and stores them in the in-memory rule store.

    Args:
        file_path (str, optional): Path to the YAML file. Defaults to ../../rules.yaml.

    Raises:
        FileNotFoundError: If the YAML file doesn't exist.
        yaml.YAMLError: If the YAML content is invalid.
        ValueError: If rules cannot be parsed into the expected schema.
    """
    try:
        if not file_path:
            current_dir = os.path.dirname(__file__)
            file_path = os.path.abspath(os.path.join(current_dir, "../../rules.yaml"))

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Rules file not found at path: {file_path}")

        with open(file_path, "r") as f:
            try:
                rule_dicts = yaml.safe_load(f)
                if not isinstance(rule_dicts, list):
                    raise ValueError("YAML must contain a list of rules")

                rules = [Rule(**r) for r in rule_dicts]
                rule_storage.load_rules(rules)

            except yaml.YAMLError as ye:
                raise yaml.YAMLError(f"Invalid YAML format: {ye}")

            except Exception as e:
                raise ValueError(f"Failed to parse rules: {e}")

    except Exception as e:
        print(f"[LoadRulesError] {e}")
        raise  # re-raise to let FastAPI caller decide how to respond
