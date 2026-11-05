"""Render a raw BG map from the ROM (header `00 size24`, w, h, u16 entries) with its LZ tile sheet, greyscale by colour index.

    python -X utf8 tools/gfx_map.py MAP_HEX SHEET_HEX OUT.png [--zoom 3] [--rom R]

Reads a map before it's on screen: which labels a menu variant draws (insert.MAP_LABELS).
"""
import argparse
import struct
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import lz77  # noqa: E402

ROM = ROOT / "rom/Legions - Yomigaeru Shiren no Shima (Japan).gba"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("map")
    ap.add_argument("sheet")
    ap.add_argument("out")
    ap.add_argument("--zoom", type=int, default=3)
    ap.add_argument("--rom")
    a = ap.parse_args()
    data = Path(a.rom or ROM).read_bytes()
    at, sheet = int(a.map, 16), lz77.decompress(data, int(a.sheet, 16))[0]
    w, h = data[at + 4], data[at + 5]
    cells = struct.unpack_from("<%dH" % (w * h), data, at + 6)
    im = Image.new("L", (w * 8, h * 8))
    for i, e in enumerate(cells):
        t = (e & 0x3FF) * 32
        for y in range(8):
            for x in range(8):
                ty, tx = (7 - y if e & 0x800 else y), (7 - x if e & 0x400 else x)
                v = sheet[t + ty * 4 + tx // 2] >> 4 * (tx & 1) & 15 if t + 32 <= len(sheet) else 0
                im.putpixel(((i % w) * 8 + x, (i // w) * 8 + y), v * 17)
    im.resize((w * 8 * a.zoom, h * 8 * a.zoom), Image.NEAREST).save(a.out)


if __name__ == "__main__":
    main()
