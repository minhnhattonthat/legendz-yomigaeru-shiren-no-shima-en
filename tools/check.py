"""check.py: the one-command check (the pre-commit hook runs it). Runs every test in tests/; exit code gates the commit."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.exit(subprocess.call([sys.executable, "-X", "utf8", "-m", "unittest", "discover", "-q", "-s", "tests"], cwd=ROOT))
