"""Static graphics sweep (phase 1): render every LZ77 block and every raw region of the ROM as 4bpp tiles on numbered 1x pages, with
an index. Nothing is dropped silently: duplicates and non-tile blocks are listed in work/sweep/index.tsv with why.

    python -X utf8 tools/gfx_sweep.py [--zoom 1] [--page 1536] [--only HEX,HEX]
"""
import argparse
import hashlib
import os
import struct
import sys
import zlib

import lz77
from fontsheet import label, png

ROM = "rom/Legions - Yomigaeru Shiren no Shima (Japan).gba"
RAW_FROM = 0x100000  # below: code and scripts


def tile_rows(data, cols, zoom):
    """data as 4bpp tiles, `cols` tiles wide. Returns (w, h, rows)."""
    n = len(data) // 32
    th = (n + cols - 1) // cols
    w, h = cols * 8 * zoom, th * 8 * zoom
    rows = [[24] * w for _ in range(h)]
    for t in range(n):
        tx, ty = (t % cols) * 8 * zoom, (t // cols) * 8 * zoom
        for y in range(8):
            for x in range(8):
                b = data[t * 32 + y * 4 + x // 2]
                v = (b >> (4 * (x & 1))) & 15
                px = v * 17
                for zy in range(zoom):
                    r = rows[ty + y * zoom + zy]
                    for zx in range(zoom):
                        r[tx + x * zoom + zx] = px
    return w, h, rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zoom", type=int, default=1)
    ap.add_argument("--page", type=int, default=1536)
    ap.add_argument("--cols", type=int, default=32)
    ap.add_argument("--only", default="", help="comma list of hex offsets: render only these blocks")
    ap.add_argument("--out", default="work/sweep")
    a = ap.parse_args()
    d = open(ROM, "rb").read()
    os.makedirs(a.out, exist_ok=True)
    only = {int(x, 16) for x in a.only.split(",") if x}
    blocks = [(o, data, e) for o, data, e in lz77.scan(d)]
    # raw regions: gaps of >= 1 KB between LZ blocks above the code, skipping nothing else
    items = []
    seen = {}
    idx = open(a.out + "/index.tsv", "w", encoding="utf-8", newline="\n")
    last = RAW_FROM
    for o, data, e in blocks:
        if o >= RAW_FROM and o - last >= 0x400:
            items.append(("raw", last, d[last:o]))
        if o >= RAW_FROM:
            last = max(last, e)
        items.append(("lz", o, data))
    if len(d) - last >= 0x400:
        items.append(("raw", last, d[last:]))
    items.sort(key=lambda t: t[1])
    page, cx, cy, colw = 0, 0, 0, a.cols * 8 * a.zoom + 2
    canvas = [[48] * a.page for _ in range(a.page)]
    drawn = 0

    def flush():
        nonlocal page, canvas, cx, cy
        png("%s/page_%03d.png" % (a.out, page), a.page, a.page, canvas)
        page += 1
        canvas = [[48] * a.page for _ in range(a.page)]
        cx = cy = 0

    for kind, off, data in items:
        if only and off not in only:
            continue
        h = hashlib.sha1(data).hexdigest()
        if not only and h in seen:
            idx.write("%s\t%06X\t%d\tskip: duplicate of %06X\n" % (kind, off, len(data), seen[h]))
            continue
        seen[h] = off
        if len(data) < 32:
            idx.write("%s\t%06X\t%d\tskip: under one tile\n" % (kind, off, len(data)))
            continue
        # split long regions across several slices so a raw 1 MB region fits on pages
        maxbytes = (a.page - 8) // (8 * a.zoom) * a.cols * 32
        for s in range(0, len(data), maxbytes):
            chunk = data[s:s + maxbytes]
            w, th, rows = tile_rows(chunk, a.cols, a.zoom)
            if cy + th + 8 > a.page:
                cy, cx = 0, cx + colw
            if cx + colw > a.page:
                flush()
            label(canvas, cx + 1, cy + 1, "%06X" % (off + s))
            for y in range(th):
                canvas[cy + 7 + y][cx:cx + w] = rows[y]
            idx.write("%s\t%06X\t%d\tpage %03d at %d,%d\n" % (kind, off + s, len(chunk), page, cx, cy))
            cy += th + 8
            drawn += 1
    flush()
    idx.close()
    print("items", len(items), "drawn", drawn, "pages", page)


if __name__ == "__main__":
    sys.exit(main())
