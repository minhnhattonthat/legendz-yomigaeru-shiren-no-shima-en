"""check.py: the one-command check (the pre-commit hook runs it). Every test in tests/, then the text lint; either failing exits non-zero, which gates the commit."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
codes = [subprocess.call([sys.executable, "-X", "utf8", "-m", "unittest", "discover", "-q", "-s", "tests"], cwd=ROOT),
         subprocess.call([sys.executable, "-X", "utf8", "tools/batches.py", "lint"], cwd=ROOT)]
sys.exit(max(codes))
