"""Rank LZ blocks by how much they look like lettering: tiles with few colours and thin strokes, then print them for gfx_sweep --only.
Heuristic only: complements the 1x pages and the emulator tour, it does not replace them."""
import sys

import lz77

ROM = "rom/Legions - Yomigaeru Shiren no Shima (Japan).gba"


def score(data):
    n = len(data) // 32
    if n < 2:
        return 0, 0
    hits = solid = 0
    for t in range(n):
        tile = data[t * 32:t * 32 + 32]
        if not any(tile):
            continue
        px = [(tile[y * 4 + x // 2] >> (4 * (x & 1))) & 15 for y in range(8) for x in range(8)]
        cols = set(px)
        if len(cols) > 4:
            continue
        fg = sum(1 for p in px if p != px[0])
        # transitions along rows: strokes alternate more than flat areas, less than dither
        tr = sum(px[y * 8 + x] != px[y * 8 + x + 1] for y in range(8) for x in range(7))
        if 8 <= fg <= 36 and 6 <= tr <= 24:
            hits += 1
        solid += 1
    return hits / n, solid / n


def main():
    d = open(ROM, "rb").read()
    rows = []
    seen = set()
    for off, data, end in lz77.scan(d):
        if data in seen:
            continue
        seen.add(data)
        s, f = score(data)
        rows.append((s, f, off, len(data)))
    rows.sort(reverse=True)
    top = [r for r in rows if r[0] >= float(sys.argv[1] if len(sys.argv) > 1 else 0.25) and r[3] >= 64]
    print("blocks", len(rows), "over threshold", len(top))
    print(",".join("%X" % r[2] for r in top))
    for r in top[:40]:
        print("%06X %6d %.2f %.2f" % (r[2], r[3], r[0], r[1]))


if __name__ == "__main__":
    main()
