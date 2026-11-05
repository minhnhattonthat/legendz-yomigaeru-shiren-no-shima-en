"""Print strings by id, or every string whose English or Japanese matches a regex.

    python -X utf8 tools/show.py 1885BC 1885D0      # id: JP / EN
    python -X utf8 tools/show.py -e "Dragon Fountain"  # every string whose English matches
    python -X utf8 tools/show.py -j "りゅうじん"        # every string whose Japanese matches
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import batches  # noqa: E402


def main():
    a = sys.argv[1:]
    blocks = batches.load_blocks()
    rows = [(b, e) for b in batches.ORDER for e in blocks[b]]
    if a and a[0] in ("-e", "-j"):
        rx, key = re.compile(a[1]), ("en" if a[0] == "-e" else "jp")
        pick = [(b, e) for b, e in rows if rx.search((e.get(key) or "").replace("\n", ""))]
    else:
        ids = set(a)
        pick = [(b, e) for b, e in rows if e["id"] in ids]
    for b, e in pick:
        print("%s %s  JP: %s\n%s EN: %s" % (b, e["id"], e["jp"].replace("\n", ""), " " * (len(b) + 8), (e.get("en") or "").replace("\n", "")))


if __name__ == "__main__":
    main()
