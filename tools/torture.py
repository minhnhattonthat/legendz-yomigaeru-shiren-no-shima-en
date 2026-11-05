"""Width gate's glyph torture build: every glyph of font_en.CODES, with double spaces, on lines three scenes show, one per font. Read the shots against the printed lines.

    python -X utf8 tools/torture.py                                 # build/legendz_torture.gba; leaves build/writes.txt alone
    emu.py build/legendz_torture.gba --out work/qa/torture/opening --script tools/debug/warp.lua --var "SCENE='opening'" --frames 5000 --shot-every 120 --sheet
    (same for menu_items and battle)
"""
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import build
import check_rom
import font_en

GROUPS = ["ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz", "0123456789", "$,.-~…!?%+:'\"/()", ";&*=#[]<>_"]
ALL = "  ".join(GROUPS)
# ids from the marker tour's logs (writes.txt), in the order each scene draws them
FONT1_OPENING = ["180F1C", "180F58", "180F8E", "180FAE", "180FE6", "181020", "181062", "1810A4", "1810E6"]
FONT2_ITEMS = [("18581C", 64, 1), ("18582E", 88, 3), ("18585A", 64, 1), ("185898", 64, 1), ("1858D4", 64, 1), ("186F1A", 64, 1), ("186F28", 88, 3), ("186F4C", 64, 1)]
SPRITE_BATTLE = ["23C36A", "23C3F6", "23C5A8", "23C5D6", "23C78E", "23C872", "23C87C", "23CED2"]


def fill(text, px, rows, width, letters):
    """Take as much of text as fits rows rows of px, breaking anywhere: (lines joined by <br>, the rest)."""
    out = []
    for _ in range(rows):
        at, used = 0, 0
        while at < min(len(text), letters) and used + width(text[at]) <= px:
            used += width(text[at])
            at += 1
        out.append(text[:at])
        text = text[at:]
    return "<br>\n".join(out), text


def lines(widths):
    """{id: text}. Each font's lines wrap the alphabet's text around until every id has a full box."""
    dialogue = lambda c: widths[font_en.CODES[c]]  # measured per pixel of the game's own table
    menu = lambda c: widths[0x200 + font_en.CODES[c]] + 1
    sprite = lambda c: font_en.SPACE if c == " " else font_en.art_width(c) + 2
    out = {}
    for group, width, letters in (([(i, 156, 2) for i in FONT1_OPENING], dialogue, 999), (FONT2_ITEMS, menu, 999), ([(i, 240, 1) for i in SPRITE_BATTLE], sprite, 42)):  # 42: the sprite ring's 21 words
        text = ALL * 3
        covered = ""
        for i, px, rows in group:
            line, text = fill(text, px, rows, width, letters)
            if line.strip("<br>\n"):  # an emptied line keeps its plain marker
                out[i] = line + "<end>"
            covered += line
        assert set(ALL) <= set(covered), "%s misses %s" % (group[0][0], set(ALL) - set(covered))
    return out


def main():
    check_rom.check()
    rom = next((ROOT / "rom").glob("*.gba")).read_bytes()
    _, widths = font_en.dialogue_fonts(rom)
    qa = lines(widths)
    r = build.marker(rom, qa)
    path = ROOT / "build/legendz_torture.gba"
    path.write_bytes(r.out)
    for i, t in qa.items():
        print(i, t.replace("<br>\n", " | "))
    print(path.name, "%d bytes sha1 %s" % (len(r.out), hashlib.sha1(r.out).hexdigest()))


if __name__ == "__main__":
    main()
