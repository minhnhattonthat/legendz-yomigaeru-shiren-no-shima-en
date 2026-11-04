"""The English font: fonts/en_font.txt -> cells and widths for the two dialogue fonts and the sprite font, and the English encoder.

A code keeps its Japanese meaning where English has one (A-Z, digits, ! ? and so on: the game's own number and name code still works).
Lower case and the rest take the cells 00F1+, blank in the dialogue fonts and kanji only in the sprite font (docs/re/vwf.md).

    python -X utf8 tools/font_en.py       # self-test
"""
import re
import struct
from pathlib import Path

import jpcodec

ROOT = Path(__file__).resolve().parents[1]
CELLS = 0x160  # dialogue font size in codes; the sprite font has 0x140
GLYPH = 48
TOP = 2  # cell row of the capital's top
SPACE = 4  # px, the English space
TABULAR = 6  # px: digits, and code 0 that the game pads numbers with

CODES = {c: 0xA4 + i for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ")}
CODES.update({c: 0xC9 + i for i, c in enumerate("0123456789")})
CODES.update(zip("$,.-~…!?", (0xBE, 0xBF, 0xC0, 0xD8, 0xC2, 0xC3, 0xC4, 0xC5)))
CODES.update(zip("%+:'\"/()", (0xD6, 0xD7, 0xDC, 0xE9, 0xEA, 0xEB, 0xEF, 0xF0)))
CODES.update({c: 0xF1 + i for i, c in enumerate("abcdefghijklmnopqrstuvwxyz")})
CODES.update({c: 0x10B + i for i, c in enumerate(" ;&*=#[]<>_")})
# Japanese punctuation the game's own strings or code may still draw: same art as its English twin
TWINS = {0xC0: ".", 0xBF: ",", 0xC1: "-"}
_token = re.compile(r"\[[0-9A-F]{4}\]|<[a-z0-9]+>\n?|.", re.S)
CTRL = {"<end>": 0xFFFF, "<page>\n": 0xFFFE, "<page>": 0xFFFE, "<br>\n": 0xFFFD, "<br>": 0xFFFD}
PAIR_BASE = 0x400  # a word from here to FFBF is two letters: past every font's cells (0x160), below the controls
# the game's own symbols, kept at their code and 8 px cell: English has no twin for them
KEEP = {c: jpcodec.REV[c] for c in "●◎♪☺♥✓★◆♨✖♫🐰🐱《》¦•"}


def art():
    out = {" ": []}
    for line in (ROOT / "fonts" / "en_font.txt").read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("## "):
            ch, rows = line.split(" ", 1)
            out[ch] = rows.split("/")
    return out


ART = art()


def art_width(ch):
    return max(map(len, ART[ch]), default=0)


def glyphs():
    """{code: char} for every code the font replaces."""
    out = {code: ch for ch, code in CODES.items()}
    out.update(TWINS)
    return out


def cell(rows, fill, paint):
    """48 bytes, 4bpp, 8x12. paint(grid) writes colours in a 12x8 grid of fill."""
    grid = [[fill] * 8 for _ in range(12)]
    paint(grid, rows)
    return bytes(grid[y][x] | grid[y][x + 1] << 4 for y in range(12) for x in range(0, 8, 2))


def paint_shadow(grid, rows):
    """Font 1: colour 2 with a colour 6 shadow straight below, as the Japanese glyphs have."""
    for y, row in enumerate(rows):
        for x, c in enumerate(row):
            if c == "#":
                grid[TOP + y][x] = 2
    for y in range(11):
        for x in range(8):
            if grid[y][x] == 2 and grid[y + 1][x] != 2:
                grid[y + 1][x] = 6


def paint_outline(grid, rows):
    """Font 2: colour 2 inside a colour 1 outline, on 0."""
    pts = {(TOP + y, x + 1) for y, row in enumerate(rows) for x, c in enumerate(row) if c == "#"}
    for y, x in pts:
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            if 0 <= y + dy < 12 and 0 <= x + dx < 8:
                grid[y + dy][x + dx] = 1
    for y, x in pts:
        grid[y][x] = 2


def dialogue_fonts(rom):
    """Copies of both fonts with the English cells in, and the width table: 0x200 bytes a font, Japanese cells 8 wide."""
    out, widths = [], bytearray()
    for base, fill, paint, extra in ((0x42BB6C, 3, paint_shadow, 1), (0x42FD6C, 0, paint_outline, 1)):
        font = bytearray(rom[base:base + CELLS * GLYPH])
        w = bytearray([8] * 0x200)
        w[0] = TABULAR
        for code, ch in glyphs().items():
            font[code * GLYPH:(code + 1) * GLYPH] = cell(ART[ch], fill, paint)
            w[code] = TABULAR if ch.isdigit() else SPACE if ch == " " else min(8, art_width(ch) + extra)
        # 00F1-015F left over in font 1 are blank: keep them drawable as blanks 8 wide
        out.append(bytes(font))
        widths += w
    return out, bytes(widths)


def sprite_glyph(rom, english, code):
    """(16x16 grid of colours, advance). English: colour F inside a colour 1 outline, on 0 (transparent). A code with no English glyph
    shows its dialogue font cell, so stray kana stays readable."""
    grid = [[0] * 16 for _ in range(16)]
    if code in english:
        ch = english[code]
        pts = {(TOP + 1 + y, x + 1) for y, row in enumerate(ART[ch]) for x, c in enumerate(row) if c == "#"}
        for y, x in pts:
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    grid[y + dy][x + dx] = 1
        for y, x in pts:
            grid[y][x] = 0xF
        return grid, SPACE if ch == " " else art_width(ch) + 2
    g = rom[0x42BB6C + code * GLYPH:0x42BB6C + (code + 1) * GLYPH]
    colours = {2: 0xF, 6: 1}
    for y in range(12):
        for x in range(8):
            grid[y][x] = colours.get(g[y * 4 + x // 2] >> (4 * (x & 1)) & 15, 0)
    return grid, 8


def sprite_font(rom, pairs):
    """The one sprite font all 4 entries share (the palette stays each entry's): (frames, tiles with their size header, widths).
    A pair is a glyph of its own, its two letters side by side in the same 16x16 OBJ as the game's kanji, so the sprite code needs no change."""
    frames, tiles, widths = bytearray(), bytearray(), bytearray()
    english = glyphs()

    def add(grid, width):
        ids = len(tiles) // 32
        frames.extend(struct.pack("<HHHHI4H", 8, 8, 0, 0x4000, 0, ids, ids + 1, ids + 2, ids + 3))  # the original records' header
        for oy, ox in ((0, 0), (0, 8), (8, 0), (8, 8)):
            tiles.extend(grid[oy + y][ox + x] | grid[oy + y][ox + x + 1] << 4 for y in range(8) for x in range(0, 8, 2))
        widths.append(width)

    for code in range(0x140):
        add(*sprite_glyph(rom, english, code))
    blank = struct.pack("<HHHHI4H", 8, 8, 0, 0x4000, 0, 0, 0, 0, 0)
    frames += blank * (PAIR_BASE - 0x140)  # codes no string uses
    widths += bytes(PAIR_BASE - 0x140)
    for a, b in pairs:
        grid, w = sprite_glyph(rom, english, a)
        right, w2 = sprite_glyph(rom, english, b)
        for y in range(16):
            for x in range(16 - w):
                if right[y][x]:
                    grid[y][x + w] = right[y][x]
        add(grid, w + w2)
    return bytes(frames), struct.pack("<H", min(len(tiles), 0xFFFF)) + bytes(tiles), bytes(widths)


def tag_frames():
    """The speaker tag's 8 tall OBJs, one column of its buffer each: asm/vwf.s, vwf_tag. Same record as the tag font's own (0x1BD210)."""
    return b"".join(struct.pack("<HHHHI2H", 8, 4, 0x8000, 0, 0, 2 * k, 2 * k + 1) for k in range(8))


def pair_table(pairs):
    """Two codes for each pair word, in word order: asm/vwf.s, vwf_split."""
    return b"".join(struct.pack("<2H", a, b) for a, b in pairs)


def encode(text, pairs=None):
    """English text with <br>, <page>, <end> and [XXXX] words -> bytes. A character the font lacks raises KeyError.

    With pairs (a dict that grows, {(code, code): word}) two letters in a row share a word, code PAIR_BASE up. A string then takes half the
    words, which is what the game's fixed name slots and text buffers count (docs/re/vwf.md)."""
    out = []
    held = None
    for t in _token.findall(text):
        if pairs is not None and t in CODES:
            if held is None:
                held = CODES[t]
            else:
                out.append(pairs.setdefault((held, CODES[t]), PAIR_BASE + len(pairs)))
                held = None
            continue
        if held is not None:
            out.append(held)
            held = None
        if t in CTRL:
            out.append(CTRL[t])
        elif t.startswith("[") and len(t) == 6:
            out.append(int(t[1:5], 16))
        else:
            out.append(CODES[t] if t in CODES else KEEP[t])
    if held is not None:
        out.append(held)
    return struct.pack("<%dH" % len(out), *out)


def px_var(text, widths, var_px=48):
    """Dialogue-font width of a line with no controls; a [XXXX] variable counts var_px."""
    return sum(var_px if len(t) == 6 else widths[CODES[t]] for t in _token.findall(text))


if __name__ == "__main__":
    assert len(set(CODES.values())) == len(CODES)
    assert not [c for c in CODES if c not in ART and c != " "], [c for c in CODES if c not in ART and c != " "]
    assert not [c for c in ART if c not in CODES], [c for c in ART if c not in CODES]
    assert max(CODES.values()) < 0x140  # the sprite font's frame table ends there
    assert encode("Ab<br>\n[FFEE]<end>") == struct.pack("<5H", 0xA4, 0xF2, 0xFFFD, 0xFFEE, 0xFFFF)
    p = {}
    assert encode("Ab cA♪[FFEE]b<end>", p) == struct.pack("<7H", 0x400, 0x401, 0xA4, KEEP["♪"], 0xFFEE, 0xF2, 0xFFFF)
    assert list(p) == [(0xA4, 0xF2), (0x10B, 0xF3)]
    for ch in ART:
        assert all(len(r) == art_width(ch) for r in ART[ch]), ch
        assert len(ART[ch]) <= 9 and art_width(ch) <= 5, ch
    print("ok", len(CODES), "glyphs")
