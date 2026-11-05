"""Render the sprite frames of a 4-pointer object table (frame A, frame B, palette, tiles): battlefield name banners (G16).

    python -X utf8 tools/gfx_frames.py TABLE_HEX COUNT OUT.png [--rom R]

Frame: u16 byte size of its sprite list, u16 byte size of its tile list, then 8-byte sprites (attr0, attr1, u16 slot, u16 0)
from offset 4, then the tile list: u16 tile index a slot into the tile data (u16 byte size, 4bpp tiles). One row per group:
its index, frame A, frame B. docs/re/graphics.md, G16.
"""
import argparse
import struct
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom/Legions - Yomigaeru Shiren no Shima (Japan).gba"
SIZES = {(0, 0): (8, 8), (0, 1): (16, 16), (0, 2): (32, 32), (0, 3): (64, 64), (1, 0): (16, 8), (1, 1): (32, 8), (1, 2): (32, 16),
         (1, 3): (64, 32), (2, 0): (8, 16), (2, 1): (8, 32), (2, 2): (16, 32), (2, 3): (32, 64)}


def sprites(rom, at):
    """[(x, y, w, h, [tile index per 8x8, row-major])] of the frame at `at`."""
    end, size = struct.unpack_from("<HH", rom, at)
    slots = struct.unpack_from("<%dH" % (size // 2), rom, at + 4 + end)
    out = []
    for o in range(at + 4, at + 4 + end, 8):
        a0, a1, slot = struct.unpack_from("<HHH", rom, o)
        w, h = SIZES[(a0 >> 14, a1 >> 14)]
        x, y = a1 & 0x1FF, a0 & 0xFF
        x, y = x - 512 if x >= 256 else x, y - 256 if y >= 128 else y
        out.append((x, y, w, h, list(slots[slot:slot + w * h // 64])))
    return out


def group(rom, table, n):
    return [struct.unpack_from("<I", rom, table + n * 16 + k * 4)[0] - 0x08000000 for k in range(4)]


def draw(rom, frame, pal, tiles, im, ox, oy):
    colours = [struct.unpack_from("<H", rom, pal + 2 + c * 2)[0] for c in range(16)]
    for x, y, w, h, idx in sprites(rom, frame):
        for k, t in enumerate(idx):
            tx, ty = x + (k % (w // 8)) * 8, y + (k // (w // 8)) * 8
            for py in range(8):
                for px in range(8):
                    v = rom[tiles + 2 + t * 32 + py * 4 + px // 2] >> 4 * (px & 1) & 15
                    if v:
                        c = colours[v]
                        im.putpixel((ox + tx + px, oy + ty + py), ((c & 31) << 3, (c >> 5 & 31) << 3, (c >> 10 & 31) << 3))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("table")
    ap.add_argument("count", type=int)
    ap.add_argument("out")
    ap.add_argument("--rom")
    a = ap.parse_args()
    rom = Path(a.rom or ROM).read_bytes()
    table = int(a.table, 16)
    im = Image.new("RGB", (40 + 2 * 140, a.count * 52), (40, 40, 60))
    d = ImageDraw.Draw(im)
    for n in range(a.count):
        fa, fb, pal, tiles = group(rom, table, n)
        d.text((2, n * 52 + 2), str(n), fill=(255, 255, 0))
        try:
            draw(rom, fa, pal, tiles, im, 40, n * 52 + 2)
            draw(rom, fb, pal, tiles, im, 180, n * 52 + 2)
        except (IndexError, KeyError, struct.error):
            d.text((40, n * 52 + 20), "not a frame", fill=(255, 0, 0))
    im = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
    im.save(a.out)


if __name__ == "__main__":
    main()
