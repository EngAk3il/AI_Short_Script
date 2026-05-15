"""Project paths (portable — no hardcoded user directories)."""
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA_DIR = BASE / "data"
STRATEGY_DATA_DIR = BASE / "strategy_data"
PATTERN_DIR = BASE / "creator_pattern"
PATTERNS_DIR = BASE / "patterns"
SCRIPTS_DIR = BASE / "scripts"
CREATORS_FILE = BASE / "creators.json"

SCRIPT_RULES = BASE / "SCRIPT_RULES.md"
SHORTS_FRAMEWORK = BASE / "SHORTS_MASTER_FRAMEWORK.md"
