"""Render the sprite font (battle top line, table 0x7F2580: frames, tiles, palette, widths; docs/re/text.md) with code labels.

    python -X utf8 tools/spritefont.py OUT.png [--entry N] [--from HEX] [--to HEX] [--zoom N]
"""
import argparse
import struct
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
TABLE = 0x7F2580


def load(rom, entry=0):
    """(frames offset, tile bytes, palette RGB list, widths offset)."""
    frames, tiles, pal, widths = (v - 0x08000000 for v in struct.unpack_from("<4I", rom, TABLE + entry * 16))
    # a halfword byte count (0x9740 = 1,210 tiles), then the raw tiles; checked against a VRAM dump in battle
    size = struct.unpack_from("<H", rom, tiles)[0]
    data = rom[tiles + 2:tiles + 2 + size]
    # pal + 2: the loader skips one word
    colours = struct.unpack_from("<16H", rom, pal + 2)
    rgb = [((c & 31) * 8, (c >> 5 & 31) * 8, (c >> 10 & 31) * 8) for c in colours]
    return frames, data, rgb, widths


def glyph(rom, font, code):
    """A 16x16 list of palette indexes."""
    frames, data, _, _ = font
    ids = struct.unpack_from("<4H", rom, frames + code * 20 + 12)
    out = [[0] * 16 for _ in range(16)]
    for n, t in enumerate(ids):
        ox, oy = (n % 2) * 8, (n // 2) * 8
        for y in range(8):
            row = data[t * 32 + y * 4:t * 32 + y * 4 + 4]
            for x in range(8):
                out[oy + y][ox + x] = (row[x // 2] >> (4 * (x & 1))) & 15 if row else 0
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--entry", type=int, default=0)
    ap.add_argument("--from", dest="start", type=lambda s: int(s, 16), default=0)
    ap.add_argument("--to", type=lambda s: int(s, 16), default=0x13D)
    ap.add_argument("--zoom", type=int, default=2)
    ap.add_argument("--cols", type=int, default=16)
    a = ap.parse_args()
    rom = next((ROOT / "rom").glob("*.gba")).read_bytes()
    font = load(rom, a.entry)
    z = a.zoom
    cw, ch = 16 * z + 6, 16 * z + 12
    n = a.to - a.start
    im = Image.new("RGB", (cw * a.cols, ch * ((n + a.cols - 1) // a.cols)), (60, 60, 90))
    dr = ImageDraw.Draw(im)
    for i in range(n):
        code = a.start + i
        cx, cy = (i % a.cols) * cw, (i // a.cols) * ch
        dr.text((cx + 1, cy), "%03X" % code, fill=(255, 255, 0))
        for y, row in enumerate(glyph(rom, font, code)):
            for x, v in enumerate(row):
                if v:
                    dr.rectangle((cx + 1 + x * z, cy + 11 + y * z, cx + x * z + z, cy + 10 + y * z + z), fill=font[2][v])
    im.save(a.out)
    print(a.out, im.size)


if __name__ == "__main__":
    main()
