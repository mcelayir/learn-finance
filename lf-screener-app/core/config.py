import os
import yaml
from dotenv import load_dotenv
from typing import Any, Dict

load_dotenv()

def load_config(path: str = "config.yaml") -> Dict[str, Any]:
    with open(path, "r") as f:
        cfg = yaml.safe_load(f)
    # environment fallbacks
    cfg["tv_username"] = os.getenv("TV_USERNAME")
    cfg["tv_password"] = os.getenv("TV_PASSWORD")
    return cfg
