"""Render a raw 8x12 4bpp font (48 bytes a glyph) into a labelled zoomed PNG: fontsheet.py ROM BASE_HEX OUT.png [--from N --count N]."""
import argparse
import sys
import zlib
import struct


def png(path, w, h, rows):
    raw = b"".join(b"\0" + bytes(r) for r in rows)
    def chunk(t, d):
        c = struct.pack(">I", len(d)) + t + d
        return c + struct.pack(">I", zlib.crc32(t + d))
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 0, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def glyph(d, off):
    """12 rows of 8 values."""
    return [[(d[off + y * 4 + x // 2] >> (4 * (x & 1))) & 15 for x in range(8)] for y in range(12)]


DIGITS = {c: v for c, v in zip("0123456789ABCDEF", [
    "111101101101111", "010110010010111", "111001111100111", "111001111001111", "101101111001001", "111100111001111",
    "111100111101111", "111001001001001", "111101111101111", "111101111001111", "010101111101101", "110101110101110",
    "011100100100011", "110101101101110", "111100110100111", "111100110100100"])}


def label(canvas, x, y, text):
    for i, c in enumerate(text):
        bits = DIGITS[c]
        for r in range(5):
            for k in range(3):
                if bits[r * 3 + k] == "1":
                    canvas[y + r][x + i * 4 + k] = 255


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rom")
    ap.add_argument("base", type=lambda s: int(s, 16) & 0x1FFFFFF)
    ap.add_argument("out")
    ap.add_argument("--from", dest="start", type=int, default=0)
    ap.add_argument("--count", type=int, default=256)
    ap.add_argument("--cols", type=int, default=16)
    ap.add_argument("--zoom", type=int, default=3)
    a = ap.parse_args()
    d = open(a.rom, "rb").read()
    cw, ch = 8 * a.zoom + 14, 12 * a.zoom + 8
    rows = (a.count + a.cols - 1) // a.cols
    W, H = cw * a.cols, ch * rows
    canvas = [[32] * W for _ in range(H)]
    for n in range(a.count):
        code = a.start + n
        cx, cy = (n % a.cols) * cw, (n // a.cols) * ch
        label(canvas, cx + 1, cy + 1, "%03X" % code)
        g = glyph(d, a.base + code * 48)
        for y in range(12):
            for x in range(8):
                v = 255 - g[y][x] * 17 if g[y][x] else 96
                v = 0 if g[y][x] == 3 else (255 if g[y][x] in (6,) else v)
                for zy in range(a.zoom):
                    for zx in range(a.zoom):
                        canvas[cy + 7 + y * a.zoom + zy][cx + 1 + x * a.zoom + zx] = v
    png(a.out, W, H, canvas)
    print(a.out, W, H)


if __name__ == "__main__":
    sys.exit(main())
