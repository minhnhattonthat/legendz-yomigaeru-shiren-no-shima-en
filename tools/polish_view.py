"""The polish pass's worksheet: each unticked line of docs/polish.md with every id it names, its budget, Japanese and current English.

    python -X utf8 tools/polish_view.py [SECTION]   # e.g. b001; no SECTION = all
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import batches  # noqa: E402


def main():
    want = sys.argv[1] if len(sys.argv) > 1 else None
    blocks = batches.load_blocks()
    by_id = {e["id"]: e for b in blocks.values() for e in b}
    limit = {}
    for p in batches.TL.glob("b*.tsv"):
        if not p.stem.endswith(".out"):
            for line in p.read_text(encoding="utf-8").splitlines():
                f = line.split("\t")
                limit[f[0]] = f[2]
    section = None
    for n, line in enumerate((ROOT / "docs/polish.md").read_text(encoding="utf-8").splitlines(), 1):
        if line.startswith("## "):
            section = line[3:].split()[0]
        if not line.startswith("- [ ]") or (want and section != want):
            continue
        print("L%d %s" % (n, line[6:]))
        for i in dict.fromkeys(re.findall(r"\b[0-9A-F]{6}\b", line)):
            e = by_id.get(i)
            if e:
                print("   %s [%s] JP: %s\n          EN: %s" % (i, limit.get(i, "?"), e["jp"].replace("\n", ""), (e.get("en") or "").replace("\n", "")))
        print()


if __name__ == "__main__":
    main()
