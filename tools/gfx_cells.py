"""Which block tile sits in each screen cell: read a gfx_trace dump's BG map and look each cell's tile up in an LZ block.
Finds the tiles a tile-drawn label uses, to redraw them (insert.graphics).

    python -X utf8 tools/gfx_cells.py work/qa/trace/SCENE BG X Y W H --block 435CA0

Cells are 8x8 screen tiles, scroll taken as 0 (the dump can't read the write-only scroll registers).
Prints a grid: block tile index (hex) with h/v flip marks, `.` for tile 0 or a tile not in the block, `pN` palette per row.
"""
import argparse
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("trace")
    ap.add_argument("bg", type=int)
    ap.add_argument("x", type=int)
    ap.add_argument("y", type=int)
    ap.add_argument("w", type=int)
    ap.add_argument("h", type=int)
    ap.add_argument("--block", required=True, help="LZ block offset, hex, from work/lzblocks/")
    ap.add_argument("--pixels", action="store_true", help="also print the rect's pixels as colour indexes")
    a = ap.parse_args()
    d = Path(a.trace)
    vram = next(d.glob("ppu_*.vram.bin")).read_bytes()
    io = next(d.glob("ppu_*.io.bin")).read_bytes()
    cnt = struct.unpack_from("<H", io, 8 + 2 * a.bg)[0]
    char, screen = (cnt >> 2 & 3) * 0x4000, (cnt >> 8 & 31) * 0x800
    block = (ROOT / "work/lzblocks" / ("%s.bin" % a.block.upper())).read_bytes()
    where = {}
    for k in range(len(block) // 32 - 1, -1, -1):
        where[block[k * 32:k * 32 + 32]] = k
    for y in range(a.y, a.y + a.h):
        row, pals = [], set()
        for x in range(a.x, a.x + a.w):
            e = struct.unpack_from("<H", vram, screen + ((y & 31) * 32 + (x & 31)) * 2)[0]
            t = e & 0x3FF
            k = where.get(vram[char + t * 32:char + t * 32 + 32])
            pals.add(e >> 12)
            row.append("  .  " if k is None or t == 0 else "%3X%s%s" % (k, "h" if e & 0x400 else " ", "v" if e & 0x800 else " "))
        print("%2d %s  p%s" % (y, "".join(row), ",".join(map(str, sorted(pals)))))
    if a.pixels:  # the rect's colour indexes, one hex digit a pixel
        for y in range(a.y * 8, (a.y + a.h) * 8):
            line = ""
            for x in range(a.x * 8, (a.x + a.w) * 8):
                e = struct.unpack_from("<H", vram, screen + ((y // 8 & 31) * 32 + (x // 8 & 31)) * 2)[0]
                ty, tx = (7 - y % 8 if e & 0x800 else y % 8), (7 - x % 8 if e & 0x400 else x % 8)
                line += "%X" % (vram[char + (e & 0x3FF) * 32 + ty * 4 + tx // 2] >> 4 * (tx & 1) & 15)
            print(line)


if __name__ == "__main__":
    sys.exit(main())
