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
    spans += [(PEN_RESET, PEN_RESET + 2), (FONT_TABLE, FONT_TABLE + 8), (SPRITE_TABLE, SPRITE_TABLE + 64)]
    spans += [(site, site + 2) for site, _ in BOX_WIDTH_SITES] + [(at + 4, at + 6) for at, _, _ in LAYOUT]
    entries = [e for _, es in strings() for e in es] + json.loads((ROOT / "script" / "credits.json").read_text(encoding="utf-8"))
    spans += [(int(o.split(":")[1], 16), int(o.split(":")[1], 16) + 4) for e in entries for o in e["owners"]]
    return sorted(set(spans))


def credits_en(text):
    """The 8-bit credits: controls as [XX], the blank 00, every glyph its font_en code (encode8's table has no punctuation in English's order, vwf.md)."""
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
    for e, data in encoded:
        repoint(rom, e, rom.append(data, "text " + e["id"]))
    for e in json.loads((ROOT / "script" / "credits.json").read_text(encoding="utf-8")):
        repoint(rom, e, rom.append(credits_en(e["en"]), "credits"))
    return len(encoded), len(pairs)
