"""Put English into a built ROM: engine patches, font, then every string, appended past the dump's end and repointed through its owners.
Every write goes through put(), logged for romdiff (references/pipeline.md, Checks). Marker mode writes `[id] filler` instead of `en`.
"""
import json
import re
import struct
from pathlib import Path

import font_en
import jpcodec
from asm_thumb import assemble

ROOT = Path(__file__).resolve().parents[1]
BASE = 0x800000  # first byte past the dump: docs/re/rom-map.md, Free space
CPU = 0x08000000
FONT_TABLE = 0x7F6654
SPRITE_TABLE = 0x7F2580
ENTRY = {"open": 0, "static": 2, "type": 4, "br": 6, "tag": 8}  # asm/vwf.s, its first lines
DIALOGUE_W = 20  # cells: the box's text column count, 0x11 in the original (docs/re/vwf.md)
FILLER = "The quick brown fox jumps over the lazy dog. "
# site, register of `movs rX, #0x11; strb rX, [rY, #7]`: every opener of the box at x = 9. 0x0B5F80 has the same bytes but isn't a text window.
# name in ENTRY, site, the whole span far_jump overwrites (8 bytes, 10 at a 2 mod 4 site), register
HOOKS = [("open", 0x0A5786, "68794b464343181c2979", 3), ("type", 0x0A5590, "1c4a207b01210140", 2), ("br", 0x0A5572, "04490448007808700449", 0),
         ("static", 0x0A594C, "6a892c690020297a", 2), ("tag", 0x0A311C, "f0b557464e464546", 3)]
PEN_RESET = 0x0A570E
BOX_WIDTH_SITES = [(0x08D2CA, 1), (0x0A9522, 0), (0x0B2B8A, 0), (0x0B9E7A, 0), (0x0C553A, 0), (0x0C815A, 0), (0x0C825C, 0), (0x0CF7D0, 0)]
SPRITE_BLOCKS = {"battle", "quips"}
TYPEWRITER = {"dialogue", "system", "link", "rental"}  # mostly the 2-row dialogue box; marker lines fill it
NAME_SLOTS = {"places", "legendz"}
# Name entry grid: its cursor picks a cell by index. 45BD*: table 0x7F7F30 draws 3, 7, 7 words of each by length, not to a terminator (phase 6), so spaces pad them to that count.
SINGLE_WORDS = {"441066", "4410A4", "4410E2", "441120", "44115E", "44119C", "45BDEA", "45BDF0", "45BDFE"}
# Not 『』: 45AA78's bracket pair frames an 8-cell name box drawn over cells 1-8, so English pads it to put 』 in cell 9 (debug_battle_record).
NON_TEXT = re.compile(r"(?:<end>|<page>\n?|<br>\n?|[　●¦：－％＇＂／\d]|\[FF[0-9A-F]{2}\])*")


class Rom:
    def __init__(self, data):
        self.orig = bytes(data)
        self.out = bytearray(data)
        self.log = []

    def put(self, off, data, by):
        self.log.append("%X %s %s %s" % (off, self.orig[off:off + len(data)].ljust(len(data), b"\xff").hex(), data.hex(), by))
        if off > len(self.out):
            self.out += b"\xff" * (off - len(self.out))
        self.out[off:off + len(data)] = data

    def append(self, data, by, align=2):
        off = (max(len(self.out), BASE) + align - 1) & ~(align - 1)
        self.put(off, data, by)
        return off


def far_jump(rom, site, target, reg, by):
    """`ldr reg, lit; bx reg; lit`, with the padding a 2 mod 4 site needs."""
    code = 0x4800 | reg << 8
    bx = 0x4700 | reg << 3
    if site & 2:
        data = struct.pack("<HHHI", code | 1, bx, 0xBF00, target | 1)
    else:
        data = struct.pack("<HHI", code, bx, target | 1)
    rom.put(site, data, by)


def expect(rom, site, hexbytes):
    """A fixed hook site must hold what the disassembly showed: a wrong dump fails here, not in game."""
    want = bytes.fromhex(hexbytes)
    if rom.orig[site:site + len(want)] != want:
        raise ValueError("site %06X holds %s, not %s" % (site, rom.orig[site:site + len(want)].hex(), hexbytes))


def engine(rom, pairs):
    """Fonts, width tables, VWF hooks (docs/re/vwf.md). pairs: what encode() built, so the strings get encoded first."""
    fonts, widths = font_en.dialogue_fonts(rom.orig)
    w_at = rom.append(widths, "widths")
    addrs = [rom.append(f, "font") for f in fonts]
    rom.put(FONT_TABLE, struct.pack("<2I", *(CPU + a for a in addrs)), "font table")
    pairs_at = rom.append(font_en.pair_table(pairs) or b"\0\0", "pairs")
    tag_at = rom.append(font_en.tag_frames(), "tag frames")
    code_at = (len(rom.out) + 3) & ~3
    code = assemble(ROOT / "asm" / "vwf.s", CPU + code_at, {"WIDTHS": CPU + w_at, "PAIRS": CPU + pairs_at - font_en.PAIR_BASE * 4, "TAGFRAMES": CPU + tag_at})
    rom.put(code_at, code, "vwf code")
    for name, site, old, reg in HOOKS:
        expect(rom, site, old)
        far_jump(rom, site, CPU + code_at + ENTRY[name], reg, "hook " + name)
    # `orrs r0, r4` with r4 = 0 -> `strh r4, [r7, #0xe]`: the open zeroes the window's pen
    expect(rom, PEN_RESET, "2043")
    rom.put(PEN_RESET, struct.pack("<H", 0x81FC), "pen reset")
    # the dialogue box's column count, in each of its openers: `movs rX, #0x11`
    for site, reg in BOX_WIDTH_SITES:
        expect(rom, site, "11%02X" % (0x20 | reg))
        rom.put(site, struct.pack("<H", 0x2000 | reg << 8 | DIALOGUE_W), "box width")
    frames, tiles, widths_s = font_en.sprite_font(rom.orig, pairs)
    f_at, t_at, w_at2 = rom.append(frames, "sprite frames"), rom.append(tiles, "sprite tiles"), rom.append(widths_s, "sprite widths")
    for n in range(4):
        at = SPRITE_TABLE + n * 16
        pal = struct.unpack_from("<I", rom.orig, at + 8)[0]
        rom.put(at, struct.pack("<4I", CPU + f_at, CPU + t_at, pal, CPU + w_at2), "sprite table")


def repoint(rom, entry, new):
    for o in entry["owners"]:
        parts = o.split(":")
        nib = int(parts[2], 16) if len(parts) > 2 else 0
        site = int(parts[1], 16)
        rom.put(site, struct.pack("<I", nib << 28 | CPU + new), "ptr " + entry["id"])


def non_text(entry):
    """Nothing to translate: a bead, blanks, a rule of colons, an empty slot, digits, variables alone. These stay as they are; a marker on the battle menu's bead drew "4T" there."""
    return NON_TEXT.fullmatch(entry["jp"]) is not None


def jp_lines(entry):
    """The string's lines without controls, and its terminator: <page> or <end>."""
    text = entry["jp"].replace("\n", "")
    term = "<page>" if text.endswith("<page>") else "<end>"
    return text[:-len(term)].split("<br>"), term


def cells(line):
    """A Japanese line's cell count, variables as words."""
    return len(jpcodec._token.findall(line))


def fill(prefix, target, widths, start=0):
    """prefix, then filler words cut to fit target px."""
    out = prefix
    w = font_en.px_var(prefix, widths)
    i = start
    while True:
        c = FILLER[i % len(FILLER)]
        if w + widths[font_en.CODES[c]] > target:
            return out.rstrip()
        out += c
        w += widths[font_en.CODES[c]]
        i += 1


def marker_id(entry, room, widths):
    """`[161C14]`, or fewer digits where the field is short. The field's px comes from the Japanese cells."""
    full = "[%s]" % entry["id"]
    if font_en.px_var(full, widths) <= room:
        return full
    for n in (4, 3, 2):
        short = entry["id"][-n:]
        if font_en.px_var(short, widths) <= room:
            return short
    return entry["id"][-1]


def marker_text(entry, block, widths):
    lines, term = jp_lines(entry)
    variables = [t for t in jpcodec._token.findall("".join(lines)) if t.startswith("[") and t[1:3] == "FF"][:2]  # enough to see them expand
    out = []
    if block in SPRITE_BLOCKS:
        # 21 OBJs a line, so 21 words, in a 32-word stack buffer (0x0A280C, 0x0A2850): variables can add 9 words each
        limit = 24 if variables else 40
        text = "[%s]" % entry["id"] + "".join(variables)
        text += FILLER[:max(0, limit - len(jpcodec._token.findall(text)))].rstrip()
        out = [text]
    else:
        box = DIALOGUE_W * 8 - 4 if block in TYPEWRITER else 0
        if box:
            lines = lines[:2]  # the box has 2 rows; the typewriter can't wrap, so a longer line would draw over other tiles
        for n, line in enumerate(lines):
            room = box or cells(line) * 8
            if block in NAME_SLOTS:
                # copied word by word into fixed save slots (default player name -> 0x02036AF8, 6 words, money right after it): as many words as the Japanese, 2 letters a word
                out.append((marker_id(entry, room, widths) + FILLER)[:max(1, cells(line) * 2)].rstrip() or entry["id"][-1])
            elif n and not line:
                out.append("")
            elif n == 0:
                lead = "●" if line.startswith("●") else ""  # a label's own bead: the menu's cursor sits on this cell, so words must start after it
                head = lead + marker_id(entry, room - 8 * len(lead), widths) + "".join(variables)
                out.append(fill(head, room, widths, 0))
            else:
                out.append(fill("", room, widths, 11 * n))
    return "<br>".join(out) + term


def strings():
    for p in sorted((ROOT / "script").glob("*.json")):
        if p.stem not in ("unreferenced", "credits"):
            yield p.stem, json.loads(p.read_text(encoding="utf-8"))


def credits_marker(entry):
    """The 8-bit credits: keep the controls, swap each run of glyphs for capitals of the same length. Lower case has no 8-bit code."""
    data = jpcodec.encode8(entry["jp"])
    out = bytearray()
    i, n = 0, 0
    while i < len(data):
        b = data[i]
        if b in (0xF1, 0xF2):
            out += data[i:i + 2]
            i += 2
        elif b >= 0xF1:
            out.append(b)
            i += 1
        else:
            word = "CREDITS%04d" % n
            n += 1
            j = i
            while j < len(data) and data[j] < 0xF1:
                j += 1
            run = (word * ((j - i) // len(word) + 1))[:j - i]
            out += bytes(font_en.CODES[c] for c in run)
            i = j
    return bytes(out)


def insert_marker(rom, overrides=None):
    """Every string as its marker; overrides {id: text} replace single markers (the width gate's test lines)."""
    _, widths = font_en.dialogue_fonts(rom.orig)
    count = 0
    pairs = {}
    encoded = []
    for block, entries in strings():
        for e in entries:
            text = (overrides or {}).get(e["id"])
            if not text and non_text(e):
                encoded.append((e, jpcodec.encode(e["jp"])))
                continue
            text = text or marker_text(e, block, widths)
            encoded.append((e, font_en.encode(text, None if e["id"] in SINGLE_WORDS else pairs)))
    engine(rom, pairs)
    for e, data in encoded:
        repoint(rom, e, rom.append(data, "text " + e["id"]))
        count += 1
    cred =json.loads((ROOT / "script" / "credits.json").read_text(encoding="utf-8"))
    for e in cred:
        repoint(rom, e, rom.append(credits_marker(e), "credits"))
    return count


# Menu layout records (pointer, tiles h16, x, y): a label's box is tiles/2 cells and the next label's tiles start where this one's end, so a table's sum
# stays the same. record, tiles in the dump, tiles in English: tools/layout.py lists them all.
LAYOUT = [(0x45ABB4, 14, 12), (0x45ABD4, 14, 16),  # Battles, Damage Taken
          (0x45AC44, 8, 10), (0x45AC5C, 8, 6),  # Support, Item
          (0x45AC64, 10, 8), (0x45AC7C, 12, 14),  # Effect, Normal Skill
          (0x45AC74, 4, 2), (0x45AC84, 8, 10)]  # the x sign, EX Skill
# Not grown: Main Role's value (0x45AC38, 8 tiles). At 10 it drew over the Main Role label's first tile (debug_battle_record), so サポート is `Assist`.


def layout(rom):
    for at, old, new in LAYOUT:
        expect(rom, at + 4, struct.pack("<H", old).hex())
        rom.put(at + 4, struct.pack("<H", new), "layout")


DOLL_ENTRY = {"test": 0, "read": 2, "write": 4, "tick": 6}  # asm/doll.s, its first lines
DOLL_HOOKS = [("test", 0x0BADA8, "00b50006054a0649"), ("read", 0x0E4948, "30b5104d2c88104b"), ("write", 0x0E488C, "30b5104d2c88104b"), ("tick", 0x0BADD4, "10b5041ce0883328")]


def doll(rom):
    """The virtual Soul Doll (D8, docs/re/doll.md). The debug tool's Lua hook stands aside when it sees these jumps."""
    at = (len(rom.out) + 3) & ~3
    rom.put(at, assemble(ROOT / "asm" / "doll.s", CPU + at), "doll code")
    for name, site, old in DOLL_HOOKS:
        expect(rom, site, old)
        far_jump(rom, site, CPU + at + DOLL_ENTRY[name], 3, "hook doll " + name)


def allowed():
    """Every span below BASE the build may write, built from the tables, not the log: (start, end) pairs. A write outside them is a stray."""
    spans = [(site, site + len(old) // 2) for _, site, old, _ in HOOKS] + [(site, site + len(old) // 2) for _, site, old in DOLL_HOOKS]
    spans += [(PEN_RESET, PEN_RESET + 2), (FONT_TABLE, FONT_TABLE + 8), (SPRITE_TABLE, SPRITE_TABLE + 64), (G2_PTR, G2_PTR + 4)]
    spans += [(p, p + 4) for v in MAP_LABELS.values() for p in v[1]] + [(m[1], m[1] + 4) for v in MAP_LABELS.values() for m in v[2]]
    spans += [(v[0], v[0] + 4) for v in BANNERS.values()] + [(s, s + len(old) // 2) for s, old, _ in CODE_KANA]
    spans += [(RIBBON[0], RIBBON[0] + 4)] + [(p, p + 4) for p in DATE_MARKS[1]] +[(v[0], v[0] + 4) for v in BLANK_SHEETS.values()] + [(FIELD_BANNERS + n * 16 + 12, FIELD_BANNERS + n * 16 + 16) for n in range(FIELD_COUNT)]
    spans += [(site, site + 2) for site, _ in BOX_WIDTH_SITES] + [(at + 4, at + 6) for at, _, _ in LAYOUT]
    entries = [e for _, es in strings() for e in es] + json.loads((ROOT / "script" / "credits.json").read_text(encoding="utf-8"))
    spans += [(int(o.split(":")[1], 16), int(o.split(":")[1], 16) + 4) for e in entries for o in e["owners"]]
    return sorted(set(spans))


# Graphics text (D5, docs/re/graphics.md). G2: the battle command sheet, LZ, 28x2 tiles 4bpp, BG palette 15 (2 white, 1 outline, 0 clear).
# Labels by top-row tile column: start, tiles, English. Tile 22 and 27 are the menu's orange corner marks and stay.
G2_SHEET, G2_PTR = 0x47FE24, 0x0D6728
G2_LABELS = [(0, 5, "Fight"), (5, 4, "Shift E"), (9, 4, "Items"), (13, 4, "Run"), (17, 5, "Talisdam"), (23, 4, "Give Up")]


def draw_text(px, pen, top, text, fill, edge, x0, x1):
    """English font art at (pen, top) on a pixel grid, outlined 1 px, kept inside columns x0..x1 and on clear (0) pixels only."""
    adv = [font_en.art_width(c) + 1 if c != " " else 2 for c in text]  # a 3 px word gap: `Give Up` fills its 4 tiles
    width = sum(adv) - 1 if text else 0
    if pen + width > x1 - 1 or pen - 1 < x0:
        raise ValueError("label %r is %d px from %d, room %d-%d" % (text, width, pen, x0, x1))
    ink = set()
    for c, a in zip(text, adv):
        for y, row in enumerate(font_en.ART[c]):
            ink.update((top + y, pen + x) for x, ch in enumerate(row) if ch == "#")
        pen += a
    rim = {(y + dy, x + dx) for y, x in ink for dy in (-1, 0, 1) for dx in (-1, 0, 1)} - ink
    if any(y < 0 or x < 0 or y >= len(px) or px[y][x] for y, x in ink | rim):
        raise ValueError("label %r lands on drawn pixels or off the grid" % text)
    for y, x in rim:
        px[y][x] = edge
    for y, x in ink:  # a list fill shades by row from the capital's top, its last colour on down
        px[y][x] = fill[min(y - top, len(fill) - 1)] if isinstance(fill, list) else fill


def draw_labels(tiles, cols, labels, fill=2, edge=1, top=4):
    """Redraw labels on a 2-row strip of 4bpp tiles (row 0 tiles, then row 1): the English font's art, 1 px outline. Returns new tile bytes."""
    w = cols * 8
    px = [[0] * w for _ in range(16)]
    for t in range(cols * 2):
        for y in range(8):
            for x in range(8):
                b = tiles[t * 32 + y * 4 + x // 2]
                px[(t // cols) * 8 + y][(t % cols) * 8 + x] = b >> 4 * (x & 1) & 15
    for start, n, text in labels:
        x0, x1 = start * 8, (start + n) * 8
        for y in range(16):
            px[y][x0:x1] = [0] * (x1 - x0)
        draw_text(px, x0 + 1, top, text, fill, edge, x0, x1)  # flush after the bead, as the kana sit
    out = bytearray(len(tiles))
    for t in range(cols * 2):
        for y in range(8):
            for x in range(0, 8, 2):
                r = px[(t // cols) * 8 + y]
                out[t * 32 + y * 4 + x // 2] = r[(t % cols) * 8 + x] | r[(t % cols) * 8 + x + 1] << 4
    return bytes(out)


# Labels drawn through a raw BG map (header `00 size24`, w, h, then u16 entries: tile index in its LZ sheet, h/v flip bits 10/11).
# The sheet's loader (0x8095710) hands out VRAM tiles in load order and keeps each sheet's base in RAM, so a sheet can grow:
# a label's new tiles go on its end and the map copies point at them. Each: sheet, its pointers, then maps: map, its pointer,
# style (background, fill: a colour or a shade a row, outline), labels as ((x, y, w, h) map cells, pen x, English[, top]) in map
# px. Every rect's fill and outline become the background first, then each English goes on, its capital's top at `top` or the
# rect's top + 4. Empty English: just cleared.
PLAIN = (0, 2, 1)
STAT_SHADE = (0, [0xA, 9, 8, 8, 7, 7, 6], 1)
MAP_LABELS = {
    "G3": (0x435CA0, [0x0D51B4], [(0x4379A0, 0x485498, PLAIN, [  # field menu (field_menu, field_menu_party)
        ((9, 5, 5, 2), 73, "Money"), ((8, 7, 6, 2), 65, "Soul Doll"), ((7, 9, 9, 2), 59, "Guest Legendz"),
        ((6, 11, 6, 2), 51, "Play Time"), ((5, 14, 7, 2), 43, "Auto-Quest"), ((8, 16, 3, 2), 66, "runs"),
        ((20, 7, 1, 2), 0, ""), ((18, 9, 2, 2), 0, "")])]),  # コ and 種 after the counts: the number alone reads
    "G15": (0x438E60, [0x0D5280], [  # doll care (menu_care): footer みがく, ドールいどう beside sprite icons; top bar `1/ 1コ`
        (0x43938A, 0x485518, PLAIN, [((5, 1, 4, 2), 41, "Polish"), ((13, 1, 7, 2), 105, "Switch Doll")]),
        (0x4392EC, 0x485508, (3, 2, 1), [((17, 2, 2, 1), 0, "")])]),
    # Talispod status (menu_talispod): ちから ぼうぎょ まりょく まぼうぎょ すばやさ, 12 px apart in a 40 px column (D9: M.Def)
    "G13": (0x45B004, [0x0BF77C, 0x0C1608], [(0x45B34E, 0x0BF988, STAT_SHADE, [((0, 0, 5, 8), 1, t, 4 + 12 * i) for i, t in enumerate(
        ["Power", "Defense", "Magic", "M.Def", "Speed"])])]),
}


def relabel_map(sheet, cells, w, labels, style):
    """Redraw labels through a map: returns the grown sheet and the new cells. Unchanged tiles keep their index."""
    bg, fill, edge = style
    clear = {edge, bg} | set(fill if isinstance(fill, list) else [fill])
    tiles = bytearray(sheet)
    index = {}
    for k in range(len(tiles) // 32 - 1, -1, -1):
        index[bytes(tiles[k * 32:k * 32 + 32])] = k
    cells = list(cells)
    h = len(cells) // w
    px = [[-1] * (w * 8) for _ in range(h * 8)]  # -1: transparent and staying so
    for n, e in enumerate(cells):
        t = tiles[(e & 0x3FF) * 32:(e & 0x3FF) * 32 + 32]
        for y in range(8):
            for x in range(8):
                ty, tx = (7 - y if e & 0x800 else y), (7 - x if e & 0x400 else x)
                v = t[ty * 4 + tx // 2] >> 4 * (tx & 1) & 15 if len(t) == 32 else 0
                px[n // w * 8 + y][n % w * 8 + x] = -1 if v == 0 and bg else v
    touched = set()
    for (cx, cy, cw, ch), *_ in labels:
        touched |= {(cx + i, cy + j) for i in range(cw) for j in range(ch)}
        for y in range(cy * 8, (cy + ch) * 8):
            for x in range(cx * 8, (cx + cw) * 8):
                if px[y][x] in clear:
                    px[y][x] = 0
    for (cx, cy, cw, ch), pen, text, *top in labels:
        if text:
            draw_text(px, pen, top[0] if top else cy * 8 + 4, text, fill, edge, cx * 8, (cx + cw) * 8)
    def val(y, x):
        v = px[y][x]
        return 0 if v < 0 else v or bg

    for i, j in sorted(touched):
        t = bytes(val(j * 8 + y, i * 8 + x) | val(j * 8 + y, i * 8 + x + 1) << 4 for y in range(8) for x in range(0, 8, 2))
        if t not in index:
            index[t] = len(tiles) // 32
            tiles += t
        cells[j * w + i] = index[t]
    return bytes(tiles), cells


# Japanese captions beside English art that already says it: (pointer, sheet: u16 byte size then tiles), sheet made clear.
BLANK_SHEETS = {"G12": (0x0A382C, 0x1ECC04)}  # 敵が出現!! over the battle start's ENEMY APPEARED
# Battlefield name banners (G16): 31 groups of 4 pointers (name frame, kanji frame, palette, tiles), gfx_frames.py. The kanji
# frame's tiles go clear in a copy of the tile data; the English name above it stays.
FIELD_BANNERS, FIELD_COUNT = 0x7F360C, 31


def frame_tiles(rom, at):
    """Tile indexes a sprite frame uses: u16 sprite list size, u16 tile list size, sprites, then u16 tile indexes."""
    end, size = struct.unpack_from("<HH", rom, at)
    return set(struct.unpack_from("<%dH" % (size // 2), rom, at + 4 + end))


# G5: the small number font's date marks 年 月 日 (tiles 30-32 of an LZ sheet, 5 loaders): 年 and 月 become `/`, 日 clear, so a
# date reads 2004/5/3. Rows of 8 colour digits.
SLASH = ["00000011", "00000121", "00001210", "00012100", "00121000", "01210000", "12100000", "11000000"]
DATE_MARKS = (0x1617E8, [0x0BEB80, 0x0BEF6C, 0x0BF788, 0x0C001C, 0x0C096C], {30: SLASH, 31: SLASH, 32: ["0" * 8] * 8})


# Kana the code puts in a string buffer itself: site, old, new Thumb. Code 0 is the game's blank number pad.
CODE_KANA = [(0x0C1792, "5b20", "0020")]  # Soul Doll List's count `1コ`: `movs r0, #0x5b` (コ) before the buffer's <end>


# Raw OBJ sheets drawn on a shaded banner: (pointer, sheet: u16 byte size then 4bpp tiles in rows of `cols`), cols, rows,
# fill, outline, the banner's text span in px, English (centred there). Kana pixels take the nearest banner colour in their row.
BANNERS = {
    "G14": (0x0CCC58, 0x43B678, 17, 2, 0xF, 2, (17, 124), "START: Confirm"),  # name entry footer スタートボタン：けっていへ
}


# G1: the title's subtitle scroll 甦る試練の島 (OBJ sheet, 14x4 tiles, 48 of them): the kanji are engraved dark strokes (colours
# 1-7) on a light ramp (8 9 B C D), so in the text rect dark pixels take colour C, then the English goes on in the darkest brown (D11).
RIBBON = (0x0CF118, 0x440688, 14, 4, (20, 5, 90, 15), 0xC, 1, "Trial Isle Reborn")


def redraw_ribbon(tiles, cols, rows, rect, light, fill, text):
    px = tile_px(tiles, cols, rows)
    x0, y0, x1, y1 = rect
    for y in range(y0, y1):
        px[y][x0:x1] = [light if 0 < v < 8 else v for v in px[y][x0:x1]]
    ink = [[0] * len(px[0]) for _ in px]
    width = sum(font_en.art_width(c) + 1 if c != " " else 2 for c in text) - 1
    draw_text(ink, (x0 + x1 - width) // 2, (y0 + y1 - 5) // 2, text, fill, 0xF, x0, x1)  # the scroll's middle sits low
    for y, row in enumerate(ink):
        for x, v in enumerate(row):
            if v == fill:
                px[y][x] = v
    return px_tiles(px, cols, len(tiles))


def tile_px(tiles, cols, rows):
    return [[tiles[((y // 8) * cols + x // 8) * 32 + (y % 8) * 4 + (x % 8) // 2] >> 4 * (x & 1) & 15 if ((y // 8) * cols + x // 8) * 32 < len(tiles) else 0
             for x in range(cols * 8)] for y in range(rows * 8)]


def px_tiles(px, cols, size):
    out = bytearray(size)
    for i in range(0, size * 2):
        t, p = divmod(i, 64)
        y, x = (t // cols) * 8 + p // 8, (t % cols) * 8 + p % 8
        out[i // 2] |= px[y][x] << 4 * (x & 1)
    return bytes(out)


def redraw_banner(tiles, cols, rows, fill, edge, span, text):
    px = tile_px(tiles, cols, rows)
    for row in px:
        keep = [x for x, v in enumerate(row) if v and v not in (fill, edge)]
        for x in range(span[0], span[1]):
            if row[x] in (fill, edge):
                row[x] = row[min(keep, key=lambda k: abs(k - x))]
    ink = [[0] * len(px[0]) for _ in px]
    width = sum(font_en.art_width(c) + 1 if c != " " else 2 for c in text) - 1
    draw_text(ink, (span[0] + span[1] - width) // 2, 2, text, fill, edge, span[0], span[1])
    for y, row in enumerate(ink):
        for x, v in enumerate(row):
            if v:
                if not px[y][x]:
                    raise ValueError("banner text %r leaves the banner at %d,%d" % (text, x, y))
                px[y][x] = v
    return px_tiles(px, cols, len(tiles))


def graphics(rom):
    """Tile-drawn Japanese replaced: a new LZ block past the dump, its pointer moved."""
    import lz77
    tiles = lz77.decompress(rom.orig, G2_SHEET)[0]
    data = lz77.compress(draw_labels(tiles, 28, G2_LABELS), 2)
    expect(rom, G2_PTR, struct.pack("<I", CPU + G2_SHEET).hex())
    rom.put(G2_PTR, struct.pack("<I", CPU + rom.append(data, "gfx G2", 4)), "gfx ptr G2")
    for name, (sheet, sheet_ptrs, maps) in MAP_LABELS.items():
        tiles = lz77.decompress(rom.orig, sheet)[0]
        for at, map_ptr, style, labels in maps:
            w, h = rom.orig[at + 4], rom.orig[at + 5]
            tiles, cells = relabel_map(tiles, struct.unpack_from("<%dH" % (w * h), rom.orig, at + 6), w, labels, style)
            expect(rom, map_ptr, struct.pack("<I", CPU + at).hex())
            new = rom.orig[at:at + 6] + struct.pack("<%dH" % len(cells), *cells)
            rom.put(map_ptr, struct.pack("<I", CPU + rom.append(new, "gfx map " + name, 4)), "gfx map ptr " + name)
        new = rom.append(lz77.compress(tiles, 2), "gfx " + name, 4)
        for p in sheet_ptrs:
            expect(rom, p, struct.pack("<I", CPU + sheet).hex())
            rom.put(p, struct.pack("<I", CPU + new), "gfx ptr " + name)
    sheet, ptrs, marks = DATE_MARKS
    tiles = bytearray(lz77.decompress(rom.orig, sheet)[0])
    for t, rows in marks.items():
        tiles[t * 32:t * 32 + 32] = bytes(int(r[x], 16) | int(r[x + 1], 16) << 4 for r in rows for x in range(0, 8, 2))
    new = rom.append(lz77.compress(bytes(tiles), 2), "gfx G5", 4)
    for p in ptrs:
        expect(rom, p, struct.pack("<I", CPU + sheet).hex())
        rom.put(p, struct.pack("<I", CPU + new), "gfx ptr G5")
    for site, old, new in CODE_KANA:
        expect(rom, site, old)
        rom.put(site, bytes.fromhex(new), "code kana")
    for name, (ptr, at) in BLANK_SHEETS.items():
        expect(rom, ptr, struct.pack("<I", CPU + at).hex())
        size = struct.unpack_from("<H", rom.orig, at)[0]
        rom.put(ptr, struct.pack("<I", CPU + rom.append(rom.orig[at:at + 2] + bytes(size), "gfx " + name, 4)), "gfx ptr " + name)
    for n in range(FIELD_COUNT):
        fa, fb, _, tiles = (struct.unpack_from("<I", rom.orig, FIELD_BANNERS + n * 16 + k * 4)[0] - CPU for k in range(4))
        kanji = frame_tiles(rom.orig, fb) - frame_tiles(rom.orig, fa)
        size = struct.unpack_from("<H", rom.orig, tiles)[0]
        data = bytearray(rom.orig[tiles:tiles + 2 + size])
        for t in kanji:
            data[2 + t * 32:2 + t * 32 + 32] = bytes(32)
        rom.put(FIELD_BANNERS + n * 16 + 12, struct.pack("<I", CPU + rom.append(bytes(data), "gfx G16 %d" % n, 4)), "gfx ptr G16")
    ptr, at, cols, rows, rect, light, fill, text = RIBBON
    size = struct.unpack_from("<H", rom.orig, at)[0]
    expect(rom, ptr, struct.pack("<I", CPU + at).hex())
    new = rom.orig[at:at + 2] + redraw_ribbon(rom.orig[at + 2:at + 2 + size], cols, rows, rect, light, fill, text)
    rom.put(ptr, struct.pack("<I", CPU + rom.append(new, "gfx G1", 4)), "gfx ptr G1")
    for name, (ptr, at, cols, rows, fill, edge, span, text) in BANNERS.items():
        size = struct.unpack_from("<H", rom.orig, at)[0]
        expect(rom, ptr, struct.pack("<I", CPU + at).hex())
        new = rom.orig[at:at + 2] + redraw_banner(rom.orig[at + 2:at + 2 + size], cols, rows, fill, edge, span, text)
        rom.put(ptr, struct.pack("<I", CPU + rom.append(new, "gfx " + name, 4)), "gfx ptr " + name)


def credits_en(text):
    """The 8-bit credits: controls as [XX], the blank 00, every glyph its font_en code (encode8's table has no punctuation in English's order, vwf.md).
    The roll draws the Japanese glyphs, not font_en's: no baseline dot or comma (C0 is 。, BF is 、), so batches.credits refuses `.` and `,`."""
    out = bytearray()
    for t in re.findall(r"\[[0-9A-F]{2}\]|[^\n]", text):
        code = int(t[1:3], 16) if t.startswith("[") else 0 if t == "　" else font_en.CODES[t]
        out.append(code)
    return bytes(out)


def insert_en(rom):
    """Every string's English. Non-text strings keep their bytes; a text string with no English stops the build."""
    pairs = {}
    encoded = []
    for block, entries in strings():
        for e in entries:
            if non_text(e):
                encoded.append((e, jpcodec.encode(e["jp"])))
            elif e["en"]:
                encoded.append((e, font_en.encode(e["en"], None if e["id"] in SINGLE_WORDS else pairs)))
            else:
                raise ValueError("no English: %s %s" % (block, e["id"]))
    engine(rom, pairs)
    layout(rom)
    doll(rom)
    graphics(rom)
    for e, data in encoded:
        repoint(rom, e, rom.append(data, "text " + e["id"]))
    for e in json.loads((ROOT / "script" / "credits.json").read_text(encoding="utf-8")):
        repoint(rom, e, rom.append(credits_en(e["en"]), "credits"))
    return len(encoded), len(pairs)
