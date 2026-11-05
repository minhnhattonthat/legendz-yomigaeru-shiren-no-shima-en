"""Width gate: write script/windows.tsv, one budget per string (px a row, rows, source), and list any string the marker tour still read from the dump's own text.

measured = the string itself drawn in the tour, by tools/lua/textlog.lua. class = its class has a measured sibling (docs/re/vwf.md, Width gate). guess = neither: the lint
treats a LONG line against a guess as "measure it", not "shorten it".

    python -X utf8 tools/debug/regen.py --rom build/legendz_marker.gba --out work/qa/marker --lua tools/lua/textlog.lua
    python -X utf8 tools/windows.py [work/qa/marker]
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 0x800000
LINE = re.compile(r"TEXT (\w) lr=(\w+) text=(\w+) x=(\d+) y=(\d+) w=(\d+) h=(\d+) flags=(\w+) pad=(\d+)")
BOX, BOX_ROWS = 156, 2  # the dialogue box: 20 cells less the right edge the ruler line showed
TAG = 64  # a speaker tag: 8 tall OBJs (asm/vwf.s, vwf_tag)
LINE_PX = 240  # one sprite line: the screen, and at most 21 words
TICKER = 800  # a quip scrolls: the limit is the 68-word builder buffer, 2 letters a word
ITEMS = 0x187A5C  # records of name, description, value
# Boxes read from the code that draws them, for strings the marker tour missed or a block's class gets wrong.
FROM_CODE = {
    "440D3A": (88, 3, "class", "auto-quest spot info, 11x3 (0x0B1DCC): values draw over cells 4-5, 9-10; 5-6, 8-9; 5-10"),
    "440DAE": (88, 2, "class", "auto-quest spot too high, 11x2 (0x0B1F04)"),
    "440D32": (24, 1, "class", "auto-quest cancel, w=3 (0x0B15E6)"),
    "45AA92": (40, 1, "class", "main role value, w=5 (table 0x45ABF8, record 8, grown in insert.LAYOUT)"),
    "45AA9C": (40, 1, "class", "main role value, w=5 (table 0x45ABF8, record 8, grown in insert.LAYOUT)"),
    "434C0C": (48, 1, "class", "rental menu, w=6 (0x0B9F60)"),
    "434C1A": (32, 1, "class", "rental menu, w=4 (0x0B9F84)"),
}


def table_field(e, base, stride):
    return next(((int(o.split(":")[1], 16) - base) % stride for o in e["owners"] if o.startswith("tab:")), None)


def owner(e, *prefixes):
    return any(o.startswith(p) for o in e["owners"] for p in prefixes)


def by_class(block, e):
    """(px, rows, source, where) for a string the tour didn't reach."""
    if e["id"] in FROM_CODE:
        return FROM_CODE[e["id"]]
    if block in ("dialogue", "system", "link", "rental"):
        if owner(e, "tab:7F020C", "tab:7EF", "tab:7F7") and block == "dialogue" and "<br>" not in e["jp"] and len(e["jp"]) < 14:
            return 64, 1, "class", "status labels, w=8 (0x0BFCA5)"
        return BOX, BOX_ROWS, "class", "dialogue box"
    if block == "items":
        return (64, 1, "class", "item list, w=8 (0x0A7919, 0x0B7E5D)") if table_field(e, ITEMS, 12) == 0 else (88, 3, "class", "item info, 11x3 (0x0A7A01, 0x0B7F15)")
    if block == "legendz":
        return 64, 1, "class", "name fields, w=8 (0x0A58CF, 0x0B98F9)"
    if block in ("skills", "skills2", "skills3"):
        # records of 0x1C from 0x2AA0A8 (and on, same stride): long name, short name, description; the Japanese descriptions wrap at 10 cells
        if table_field(e, 0x2AA0A8, 0x1C) == 8:
            return 80, 2, "guess", "skill info: 10 cells a row in the Japanese"
        return 80, 1, "class", "skill list, w=10 (0x0BFCA5)"
    if block == "places":
        # 0x7EFFC4's table holds both: locations and their English subtitles first, speaker names from the player's own tag on
        return (TAG, 1, "class", "speaker tag") if int(e["id"], 16) >= 0x188C56 else (LINE_PX, 1, "class", "location card, sprite line")
    if block == "battle":
        return LINE_PX, 1, "class", "battle line, sprite"
    if block == "quips":
        return TICKER, 1, "guess", "quip ticker: never seen on screen (status.md)"
    if block == "cards":
        return 112, 1, "class", "card name, w=14 (0x0BD742; never on screen)"
    if block == "menus" and owner(e, "tab:7F75", "tab:7F76"):
        return 64, 1, "class", "status rows x=5, w=8 (table 0x45ACA8, read through 0x0BFAB0)"
    if block == "adventure" and owner(e, "tab:434") and owner(e, "tab:7F6"):
        return 64, 1, "class", "spot list, w=8 (0x0B1C90, table 0x0B1D10)"
    return 8 * max(1, len(e["jp"]) - 5), 1, "guess", "menu label, not reached: its Japanese cells"


def measures(qa):
    """{dump offset of the string: [(kind, caller, w, h)]}, {dump offset read from the dump's text: [(kind, caller, scene)]}, boxes seen."""
    at = {}
    for line in (ROOT / "build/writes.txt").read_text(encoding="utf-8").splitlines():
        p = line.split(" ")
        if len(p) >= 5 and p[3] == "text":
            at[int(p[0], 16)] = p[4]
    seen, stale, boxes = {}, {}, {}
    for log in qa.glob("*/log.txt"):
        for m in LINE.finditer(log.read_text(encoding="utf-8", errors="replace")):
            kind, lr, text, _, _, w, h, flags, _ = m.groups()
            off = int(text, 16) - 0x08000000
            if kind == "F":
                continue  # fixed cells: digits only, no budget
            if 0 <= off < BASE:
                stale.setdefault(off, set()).add((kind, lr, log.parent.name))
            elif off in at:
                seen.setdefault(at[off], set()).add((kind, lr, int(w), int(h)))
            if kind != "B":
                boxes.setdefault((kind, lr, int(w), int(h), int(flags, 16) & 1), set()).add(log.parent.name)
    return seen, stale, boxes


def budget(seen):
    """The string's smallest box among those seen: pipeline.md, Width gate."""
    fits = []
    for kind, lr, w, h in seen:
        if kind == "B":  # the builder: 0x0808D2AF is the dialogue box's, 0x08098xxx battle's sprite lines
            fits.append((BOX, BOX_ROWS, lr) if lr == "0808D2AF" else (LINE_PX, 1, lr) if lr.startswith("08098") else None)
        elif kind == "P":
            fits.append((LINE_PX, 1, lr))
        elif kind == "T":
            fits.append((w * 8 - 4, h, lr))
        else:
            fits.append((w * 8, h, lr))
    fits = [f for f in fits if f]
    return min(fits, key=lambda f: f[0] * f[1]) if fits else None


def main():
    qa = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "work/qa/marker"
    seen, stale, boxes = measures(qa)
    out = ["id\tpx\trows\tsource\twhere"]
    count = {}
    for p in sorted((ROOT / "script").glob("*.json")):
        if p.stem in ("unreferenced", "credits"):
            continue
        for e in json.loads(p.read_text(encoding="utf-8")):
            got = budget(seen.get(e["id"], ()))
            px, rows, source, where = (got[0], got[1], "measured", got[2]) if got else by_class(p.stem, e)
            out.append("%s\t%d\t%d\t%s\t%s" % (e["id"], px, rows, source, where))
            count[source] = count.get(source, 0) + 1
    (ROOT / "script/windows.tsv").write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    print("windows.tsv:", len(out) - 1, "strings", count)
    print("distinct boxes:")
    for (kind, lr, w, h, font), scenes in sorted(boxes.items()):
        print("  %s %s w=%d h=%d font=%d  %s" % (kind, lr, w, h, font, ",".join(sorted(scenes)[:3])))
    if stale:
        print("STILL READ FROM THE DUMP'S TEXT (%d):" % len(stale))
        for off, where in sorted(stale.items()):
            print("  %06X %s" % (off, sorted(where)[:2]))
    else:
        print("nothing read from the dump's text")


if __name__ == "__main__":
    main()
