"""Zoom a screen shot or BG map render and draw the 8x8 tile grid with column/row numbers, to read cell coordinates for gfx_cells.py.

    python -X utf8 tools/gfx_grid.py IN.png OUT.png [--zoom 4] [--crop x,y,w,h]   (crop in source pixels, tile-aligned keeps the numbers right)
"""
import argparse

from PIL import Image, ImageDraw


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--zoom", type=int, default=4)
    ap.add_argument("--crop")
    a = ap.parse_args()
    im = Image.open(a.src).convert("RGB")
    ox = oy = 0
    if a.crop:
        x, y, w, h = map(int, a.crop.split(","))
        im, ox, oy = im.crop((x, y, x + w, y + h)), x // 8, y // 8
    z = a.zoom
    im = im.resize((im.width * z, im.height * z), Image.NEAREST)
    d = ImageDraw.Draw(im)
    for x in range(0, im.width, 8 * z):
        d.line([(x, 0), (x, im.height)], fill=(255, 0, 0))
        d.text((x + 2, 0), str(ox + x // (8 * z)), fill=(0, 255, 0))
    for y in range(0, im.height, 8 * z):
        d.line([(0, y), (im.width, y)], fill=(255, 0, 0))
        d.text((0, y + 10), str(oy + y // (8 * z)), fill=(0, 255, 255))
    im.save(a.out)


if __name__ == "__main__":
    main()
