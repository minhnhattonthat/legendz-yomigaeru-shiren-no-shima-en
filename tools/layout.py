"""Menu layout tables in 0x45AADC-0x45AE30 and 0x46B280+: records of (pointer, tiles h16, x, y); a label's box is tiles/2 cells. Prints each label's English width against its box.

    python -X utf8 tools/layout.py [start end]
"""
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import batches  # noqa: E402
import insert  # noqa: E402

CPU = 0x08000000


def rows(rom, start, end):
    """(table offset, pointer, tiles, x, y) where a word points into ROM text. Records sit at either 4-byte alignment (0x45AE18 is 4 mod 8)."""
    for at in range(start, end, 4):
        p, t, x, y = struct.unpack_from("<IHBB", rom, at)
        if CPU <= p < CPU + len(rom):
            yield at, p - CPU, t, x, y


def main():
    rom = next((ROOT / "rom").glob("*.gba")).read_bytes()
    a = sys.argv[1:]
    start, end = (int(a[0], 16), int(a[1], 16)) if a else (0x45AADC, 0x45AE30)
    by_id = {e["id"]: e for b in batches.load_blocks().values() for e in b}
    w = batches.widths()
    grown = {at: new for at, _, new in insert.LAYOUT}
    for at, p, t, x, y in rows(rom, start, end):
        t = grown.get(at, t)
        e = by_id.get("%06X" % p)
        en = batches.show(e["en"]) if e and e["en"] else "-"
        px = batches.row_px(en, w, False) + 1 if en != "-" else 0
        print("%06X -> %06X tiles %2d x %2d y %2d box %3d px %3d %s %s" % (at, p, t, x, y, t * 4, px, "OVER" if px > t * 4 and en != "-" else "    ", en))


if __name__ == "__main__":
    main()
