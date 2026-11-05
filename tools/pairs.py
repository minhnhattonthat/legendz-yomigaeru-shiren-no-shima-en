"""Reviewer input: one pairs file per batch (references/translation.md, Review), read from script/*.json.

    python -X utf8 tools/pairs.py OUT_DIR b015 b016 ...   # OUT_DIR/b015.txt: `>> id | speaker | JP` / `EN`, in script order, with 2 lines of context either side
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import batches  # noqa: E402


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    blocks = batches.load_blocks()
    by_id = {}
    for block in batches.ORDER:
        for n, e in enumerate(blocks[block]):
            by_id[e["id"]] = (block, n)
    for batch in sys.argv[2:]:
        ids = [line.split("\t")[0] for line in (batches.TL / (batch + ".tsv")).read_text(encoding="utf-8").splitlines()]
        rows = []
        for block in batches.ORDER:
            mine = {by_id[i][1] for i in ids if by_id[i][0] == block}
            near = sorted(k for n in mine for k in range(n - 2, n + 3) if 0 <= k < len(blocks[block]))
            for k in dict.fromkeys(near):
                e = blocks[block][k]
                speaker = ",".join(e.get("speaker") or []) if isinstance(e.get("speaker"), list) else ""
                rows.append("%s %s | %s | %s\n   %s" % (">>" if k in mine else "  ", e["id"], speaker, batches.show(e["jp"]), batches.show(e["en"])))
        (out / (batch + ".txt")).write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
        print(batch, len(ids))


if __name__ == "__main__":
    main()
