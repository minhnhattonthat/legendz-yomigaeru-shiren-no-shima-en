"""Every string a tour drew against the box it drew in: tools/lua/textlog.lua's logs, the build's write log, the script's English.

    python -X utf8 tools/overflow.py work/qa/en1 [build/tour1.writes.txt]

Prints each string whose English doesn't fit, each string in overs.tsv the tour reached and its real box, and how many strings the tour drew. Exit 1 on an overflow.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import batches  # noqa: E402

LINE = re.compile(r"TEXT (\w) lr=(\w+) text=(\w+) x=(\d+) y=(\d+) w=(\d+) h=(\d+) flags=(\w+) pad=(\d+)")


def main():
    qa = Path(sys.argv[1])
    writes = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "build/writes.txt"
    at = {}
    for line in writes.read_text(encoding="utf-8").splitlines():
        p = line.split(" ")
        if len(p) >= 5 and p[3] == "text":
            at[int(p[0], 16) + 0x08000000] = p[4]
    by_id = {e["id"]: e for b in batches.load_blocks().values() for e in b}
    w = batches.widths()
    overs = {line.split("\t")[0] for line in (ROOT / "script/overs.tsv").read_text(encoding="utf-8").splitlines()}
    drawn, over, seen_over = set(), {}, {}
    for log in qa.glob("*/log.txt"):
        for m in LINE.finditer(log.read_text(encoding="utf-8", errors="replace")):
            kind, lr, text, x, y, cells, rows, flags, _ = m.groups()
            i = at.get(int(text, 16))
            if not i or kind in "BF":
                continue
            drawn.add(i)
            e = by_id[i]
            en = batches.show(e["en"]) if e["en"] else ""
            if kind == "P":
                box, h, font2 = batches.row_px, 1, 0
                continue  # sprite lines: lint holds them to 240 px and 21 words
            h, font2 = int(rows), int(flags, 16) & 1
            box = int(cells) * 8 - (4 if kind == "T" else 0)
            if i in overs:
                seen_over.setdefault(i, set()).add((lr, int(cells), h, log.parent.name))
            for page in en.split(" // "):
                rs = page.split(" / ")
                wide = max((batches.row_px(r, w, False) + font2 for r in rs), default=0)
                if wide > box or len(rs) > h:
                    over.setdefault(i, set()).add("%dpx x%d in %dpx x%d lr=%s %s: %s" % (wide, len(rs), box, h, lr, log.parent.name, page))
    for i, why in sorted(over.items()):
        print("OVER", i, sorted(why)[0])
    for i, boxes in sorted(seen_over.items()):
        print("reached", i, sorted(boxes)[:2])
    print("%d strings drawn, %d over, %d of %d overs.tsv reached" % (len(drawn), len(over), len(seen_over), len(overs)))
    sys.exit(1 if over else 0)


if __name__ == "__main__":
    main()
