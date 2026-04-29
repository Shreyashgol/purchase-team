"""Purchase Order application package."""

from pathlib import Path
import sys


repo_root = Path(__file__).resolve().parents[2]
repo_root_str = str(repo_root)
if repo_root_str not in sys.path:
    sys.path.insert(0, repo_root_str)

from shared.env import load_agent_env

load_agent_env(__file__)
