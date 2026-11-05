"""Run asm/vwf.s in Unicorn against a Python model of the screen it should draw, and check the font and the marker text."""
import json
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from unicorn import UC_ARCH_ARM, UC_MODE_THUMB, Uc
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_R0, UC_ARM_REG_R3, UC_ARM_REG_R5, UC_ARM_REG_R6, UC_ARM_REG_R7, UC_ARM_REG_R8, UC_ARM_REG_R12, UC_ARM_REG_SP

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import font_en
import insert
import jpcodec
from asm_thumb import assemble

CODE, FONTS, WIDTHS, TEXT, VRAM, MAP, STACK, STOP = 0x08800000, 0x08700000, 0x08600000, 0x02000000, 0x06000000, 0x02010000, 0x03008000, 0x08900000
PAIRS = 0x08500000
FONT_TABLE = 0x087F6000 + 0x654
ROM = next((ROOT / "rom").glob("*.gba")).read_bytes()


def machine(pairs=None):
    fonts, widths = font_en.dialogue_fonts(ROM)
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for base, size in ((0x08000000, 0x1000000), (0x02000000, 0x40000), (0x03000000, 0x8000 + 0x1000), (0x06000000, 0x18000)):
        uc.mem_map(base, size)
    uc.mem_write(FONTS, fonts[0] + fonts[1])
    uc.mem_write(WIDTHS, widths)
    uc.mem_write(FONT_TABLE, struct.pack("<2I", FONTS, FONTS + len(fonts[0])))
    code = assemble(ROOT / "asm" / "vwf.s", CODE, {"WIDTHS": WIDTHS, "PAIRS": PAIRS - font_en.PAIR_BASE * 4, "TAGFRAMES": PAIRS + 0x10000})
    uc.mem_write(CODE, code)
    uc.mem_write(PAIRS, font_en.pair_table(pairs or {}) or b"\0\0")
    uc.mem_write(0x080A5A64, struct.pack("<H", 0xE7FE))  # the renderer's epilogue: a stop point
    return uc, fonts, widths


def draw_model(text, fonts, widths, font=0, pad=2, fill=3):
    """Pixel rows of one text row, in Python: {(x, y): colour} over a filled background."""
    out = {}
    pen = 0
    for code in text:
        g = fonts[font][code * 48:(code + 1) * 48]
        for y in range(12):
            for x in range(widths[font * 0x200 + code]):
                out[(pen + x, y + pad)] = g[y * 4 + x // 2] >> (4 * (x & 1)) & 15
        pen += widths[font * 0x200 + code]
    return out, pen


class Static(unittest.TestCase):
    def run_static(self, uc, text, w, h, pad=2, stride=30):
        d = bytes([0, 0, pad, 0, 3, 1, stride, w, h, 0]) + struct.pack("<HH", 0x1234, 0xF000) + b"\0\0" + struct.pack("<II", TEXT, MAP)
        uc.mem_write(TEXT, text)
        uc.mem_write(TEXT + 0x1000, d)
        uc.mem_write(VRAM, b"\xAA" * 0x2000)
        uc.mem_write(MAP, b"\xEE" * 0x1000)
        uc.reg_write(UC_ARM_REG_R3, VRAM)
        uc.reg_write(UC_ARM_REG_R12, MAP)
        uc.reg_write(UC_ARM_REG_R5, TEXT + 0x1000)
        uc.reg_write(UC_ARM_REG_R6, 0x33333333)
        uc.reg_write(UC_ARM_REG_R7, stride)
        uc.reg_write(UC_ARM_REG_R8, 0xF0AA)
        uc.reg_write(UC_ARM_REG_SP, STACK)
        uc.emu_start((CODE + insert.ENTRY["static"]) | 1, 0x080A5A64)
        self.assertEqual(uc.reg_read(UC_ARM_REG_SP), STACK)

    def test_rows_match_the_model(self):
        uc, fonts, widths = machine()
        line1 = struct.unpack("<9H", font_en.encode("Hello, Wi"))
        line2 = struct.unpack("<6H", font_en.encode("[qmb].") )
        text = struct.pack("<%dH" % (len(line1) + len(line2) + 2), *line1, 0xFFFD, *line2, 0xFFFF)
        self.run_static(uc, text, 10, 3)
        vram = bytes(uc.mem_read(VRAM, 0x2000))
        at = 0
        for line in (line1, line2):
            model, px = draw_model(line, fonts, widths)
            cols = (px + 7) // 8
            for x in range(cols * 8):
                for y in range(16):
                    word = struct.unpack_from("<I", vram, at + (x // 8) * 0x40 + y * 4)[0]
                    got = word >> (4 * (x % 8)) & 15
                    self.assertEqual(got, model.get((x, y), 3), (x, y, line[:2]))
            at += cols * 0x40
        self.assertEqual(vram[at:at + 4], b"\xAA" * 4, "wrote past the columns it laid out")
        # the map: sequential tile pairs for what's used, blank for the rest, 2 rows a line
        m = bytes(uc.mem_read(MAP, 0x400))
        def cell(row, col):
            return struct.unpack_from("<H", m, (row * 30 + col) * 2)[0]  # the entry gets the map pointer already at x, y
        cols1 = (draw_model(line1, fonts, widths)[1] + 7) // 8
        self.assertEqual([cell(0, c) for c in range(cols1)], [0x1234 + 2 * c for c in range(cols1)])
        self.assertEqual([cell(1, c) for c in range(cols1)], [0x1235 + 2 * c for c in range(cols1)])
        self.assertEqual(cell(0, cols1), 0xF0AA)
        self.assertEqual(cell(2, 0), 0x1234 + 2 * cols1)
        self.assertEqual(cell(4, 0), 0xF0AA)  # the third row: text ended

    def test_pairs_draw_exactly_like_their_letters(self):
        text = "Hexadragon, the Wind!<br>Odd line.<br>[FFEE]"
        pairs = {}
        packed = font_en.encode(text + "<end>", pairs)
        plain = font_en.encode(text + "<end>")
        self.assertLess(len(packed), len(plain) * 2 // 3)
        shots = []
        for t in (plain, packed):
            uc, _, _ = machine(pairs)
            self.run_static(uc, t, 20, 3)
            shots.append((bytes(uc.mem_read(VRAM, 0x2000)), bytes(uc.mem_read(MAP, 0x800))))
        self.assertEqual(shots[0], shots[1])

    def test_outlined_font_keeps_the_neighbours_outline(self):
        uc, fonts, widths = machine()
        codes = struct.unpack("<4H", font_en.encode("HHHH"))
        d3 = 1  # font 2's flag
        d = bytes([0, 0, 2, d3, 3, 1, 30, 10, 1, 0]) + struct.pack("<HH", 0x1234, 0xF000) + b"\0\0" + struct.pack("<II", TEXT, MAP)
        uc.mem_write(TEXT, struct.pack("<5H", *codes, 0xFFFF))
        uc.mem_write(TEXT + 0x1000, d)
        uc.mem_write(VRAM, b"\xAA" * 0x400)
        for reg, v in ((UC_ARM_REG_R3, VRAM), (UC_ARM_REG_R12, MAP), (UC_ARM_REG_R5, TEXT + 0x1000), (UC_ARM_REG_R6, 0), (UC_ARM_REG_R7, 30), (UC_ARM_REG_R8, 0), (UC_ARM_REG_SP, STACK)):
            uc.reg_write(reg, v)
        uc.emu_start((CODE + insert.ENTRY["static"]) | 1, 0x080A5A64)
        vram = bytes(uc.mem_read(VRAM, 0x200))
        # the model: nonzero pixels of each cell, advancing by the width table
        model = {}
        pen = 0
        for code in codes:
            g = fonts[1][code * 48:(code + 1) * 48]
            for y in range(12):
                for x in range(8):
                    v = g[y * 4 + x // 2] >> (4 * (x & 1)) & 15
                    if v:
                        model[(pen + x, y + 2)] = v
            pen += widths[0x200 + code]
        for (x, y), v in model.items():
            word = struct.unpack_from("<I", vram, (x // 8) * 0x40 + y * 4)[0]
            self.assertEqual(word >> (4 * (x % 8)) & 15, v, (x, y))
        # the last outline column gets a tile of its own: measured px + 1
        self.assertEqual(struct.unpack_from("<H", bytes(uc.mem_read(MAP, 10)), ((pen + 8) // 8 - 1) * 2)[0], 0x1234 + 2 * ((pen + 8) // 8 - 1))

    def test_auto_wrap_keeps_every_glyph(self):
        uc, _, _ = machine()
        text = font_en.encode("MMMMMMMMMMMMMMMM<end>")  # 16 x 6 px in rows of 2 cells: 2 per row
        self.run_static(uc, text, 2, 8)
        m = bytes(uc.mem_read(MAP, 0x800))
        used = sum(struct.unpack_from("<H", m, (r * 2 * 30 + c) * 2)[0] != 0xF0AA for r in range(8) for c in range(2))
        self.assertEqual(used, 8 * 2)


class MarkerBuild(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import build
        cls.r = build.marker(ROM)

    def test_romdiff_accepts_every_write(self):
        with tempfile.TemporaryDirectory() as d:
            new, log = Path(d) / "new.gba", Path(d) / "writes.txt"
            orig = Path(d) / "orig.gba"
            orig.write_bytes(ROM)
            new.write_bytes(self.r.out)
            log.write_text("\n".join(self.r.log) + "\n", encoding="utf-8")
            res = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "tools/romdiff.py"), str(orig), str(new), "--writes", str(log)], capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, res.stdout[-800:] + res.stderr[-800:])

    def test_every_write_is_in_an_allowed_span(self):
        # romdiff counts any logged write as covered, so the allowed list is checked here: a write to flag bytes or graphics fails
        import bisect
        spans = insert.allowed()
        starts = [a for a, _ in spans]
        for line in self.r.log:
            p = line.split(" ")
            at, end = int(p[0], 16), int(p[0], 16) + len(p[1]) // 2
            if at >= insert.BASE:
                continue
            i = bisect.bisect_right(starts, at) - 1
            self.assertTrue(i >= 0 and spans[i][0] <= at and end <= spans[i][1], "stray write %s" % line[:60])

    def test_every_owner_points_at_its_new_string(self):
        placed = {}
        for line in self.r.log:
            p = line.split(" ")
            if p[3] == "text":
                placed[p[4]] = int(p[0], 16)
        n = 0
        for _, entries in insert.strings():
            for e in entries:
                for o in e["owners"]:
                    parts = o.split(":")
                    nib = int(parts[2], 16) if len(parts) > 2 else 0
                    word = struct.unpack_from("<I", self.r.out, int(parts[1], 16))[0]
                    self.assertEqual(word, nib << 28 | 0x08000000 + placed[e["id"]], o)
                    n += 1
        self.assertGreater(n, 8000)  # every table wrote all its entries, not just some

    def test_dump_untouched_below_the_writes(self):
        self.assertEqual(self.r.out[:0xC0], ROM[:0xC0])  # header and its checksum

    def test_no_site_was_written_twice(self):
        sites = [int(line.split(" ")[0], 16) for line in self.r.log]
        self.assertEqual(len(sites), len(set(sites)))

    def test_no_branch_lands_inside_a_hook(self):
        spans = []
        for line in self.r.log:
            p = line.split(" ")
            if p[3] == "hook":
                spans.append((int(p[0], 16), int(p[0], 16) + len(p[2]) // 2))
        self.assertGreaterEqual(len(spans), 5)
        for a, b in spans:
            for at in range(a - 0x1000 & ~1, b + 0x1000, 2):
                if a <= at < b:
                    continue
                op = struct.unpack_from("<H", ROM, at)[0]
                if op >> 12 == 0xD and op >> 8 & 15 < 14:  # Bcc
                    to = at + 4 + ((op & 0xFF ^ 0x80) - 0x80) * 2
                elif op >> 11 == 0x1C:  # B
                    to = at + 4 + ((op & 0x7FF ^ 0x400) - 0x400) * 2
                elif op >> 11 == 0x1E:  # BL, in two halves
                    low = struct.unpack_from("<H", ROM, at + 2)[0]
                    if low >> 11 != 0x1F:
                        continue
                    to = at + 4 + ((op & 0x7FF ^ 0x400) - 0x400 << 12) + (low & 0x7FF) * 2
                else:
                    continue
                self.assertFalse(a < to < b, "%06X branches to %06X, inside the hook at %06X" % (at, to, a))


class EnglishBuild(MarkerBuild):
    """The same ROM checks as the marker's, on the real script, and what only English has."""

    @classmethod
    def setUpClass(cls):
        import build
        cls.r = build.english(ROM)

    def _at(self, e):
        return (struct.unpack_from("<I", self.r.out, int(e["owners"][0].split(":")[1], 16))[0] & 0x0FFFFFFF) - 0x08000000

    def _string(self, e):
        return self.r.out[self._at(e):self.r.out.index(b"\xff\xff", self._at(e)) + 2]

    def test_g2_sheet_is_english_and_keeps_its_marks(self):
        import lz77
        at = struct.unpack_from("<I", self.r.out, insert.G2_PTR)[0] - 0x08000000
        new, old = lz77.decompress(self.r.out, at)[0], lz77.decompress(ROM, insert.G2_SHEET)[0]
        self.assertEqual(len(new), len(old))
        for t in (22, 27, 22 + 28, 27 + 28):  # the orange corner marks
            self.assertEqual(new[t * 32:t * 32 + 32], old[t * 32:t * 32 + 32])
        self.assertNotEqual(new[:5 * 32], old[:5 * 32])

    def test_relabelled_maps_only_grow_their_sheet_and_change_label_cells(self):
        import lz77
        for name, (sheet, ptrs, maps) in insert.MAP_LABELS.items():
            old = lz77.decompress(ROM, sheet)[0]
            for p in ptrs:
                new = lz77.decompress(self.r.out, struct.unpack_from("<I", self.r.out, p)[0] - 0x08000000)[0]
                self.assertEqual(new[:len(old)], old, name)  # other maps on this sheet keep their tiles
                self.assertGreater(len(new), len(old), name)
            for at, map_ptr, _, labels in maps:
                w, h = ROM[at + 4], ROM[at + 5]
                was = struct.unpack_from("<%dH" % (w * h), ROM, at + 6)
                now = struct.unpack_from("<%dH" % (w * h), self.r.out, struct.unpack_from("<I", self.r.out, map_ptr)[0] - 0x08000000 + 6)
                rects = {(cx + i, cy + j) for (cx, cy, cw, ch), *_ in labels for i in range(cw) for j in range(ch)}
                changed = {(n % w, n // w) for n in range(w * h) if was[n] != now[n]}
                self.assertTrue(changed and changed <= rects, name)

    def test_banner_keeps_its_size_and_changes(self):
        for name, (ptr, at, *_rest) in insert.BANNERS.items():
            size = struct.unpack_from("<H", ROM, at)[0]
            new = struct.unpack_from("<I", self.r.out, ptr)[0] - 0x08000000
            self.assertEqual(self.r.out[new:new + 2], ROM[at:at + 2], name)
            self.assertNotEqual(self.r.out[new + 2:new + 2 + size], ROM[at + 2:at + 2 + size], name)

    def test_field_banners_lose_only_their_kanji_frame(self):
        for n in range(insert.FIELD_COUNT):
            fa, fb, _, old = (struct.unpack_from("<I", ROM, insert.FIELD_BANNERS + n * 16 + k * 4)[0] - 0x08000000 for k in range(4))
            new = struct.unpack_from("<I", self.r.out, insert.FIELD_BANNERS + n * 16 + 12)[0] - 0x08000000
            for t in insert.frame_tiles(ROM, fa):
                self.assertEqual(self.r.out[new + 2 + t * 32:new + 34 + t * 32], ROM[old + 2 + t * 32:old + 34 + t * 32], n)
            for t in insert.frame_tiles(ROM, fb) - insert.frame_tiles(ROM, fa):
                self.assertFalse(any(self.r.out[new + 2 + t * 32:new + 34 + t * 32]), n)

    def test_every_string_has_english_or_keeps_its_bytes(self):
        for _, entries in insert.strings():
            for e in entries:
                if insert.non_text(e):
                    data = jpcodec.encode(e["jp"])
                    self.assertEqual(self.r.out[self._at(e):self._at(e) + len(data)], data, e["id"])
                else:
                    self.assertTrue(e["en"], e["id"])
                    self.assertNotRegex(e["en"], "[぀-ヿ一-鿿]", e["id"])

    def test_single_word_strings_stay_single(self):
        entries = {e["id"]: e for _, es in insert.strings() for e in es}
        for id, words in (("45BDEA", 3), ("45BDF0", 7), ("45BDFE", 7)):  # drawn by length, table 0x7F7F30
            self.assertEqual(len(self._string(entries[id])) // 2 - 1, words, id)
        grid = self._string(entries["441066"])
        self.assertEqual(len(grid) // 2 - 1, len(entries["441066"]["en"].replace("<end>", "")))  # a cell a word

    def test_credits_in_the_8_bit_codes(self):
        e = json.loads((ROOT / "script/credits.json").read_text(encoding="utf-8"))[0]
        data = insert.credits_en(e["en"])
        self.assertEqual(data[-1], 0xFF)
        self.assertLessEqual(max(b for b in data if b < 0xF1), 0xF0)
        self.assertEqual(data[:3], bytes((0xA4 + ord("S") - ord("A"), 0xA4 + ord("T") - ord("A"), 0xA4)))
        word = struct.unpack_from("<I", self.r.out, 0x0D205C)[0]
        self.assertEqual(self.r.out[word - 0x08000000:word - 0x08000000 + len(data)], data)

    def test_layout_tables_keep_their_sums(self):
        by = {}
        for at, old, new in insert.LAYOUT:
            table = 0x45ABB4 if at < 0x45AC00 else 0x45AC44
            by[table] = by.get(table, 0) + new - old
        self.assertEqual(set(by.values()), {0})


class Font(unittest.TestCase):
    def test_widths_fit_a_cell(self):
        _, widths = font_en.dialogue_fonts(ROM)
        self.assertLessEqual(max(widths), 8)
        self.assertEqual(widths[font_en.CODES["1"]], widths[0])  # digits and the padding code stay tabular

    def test_kana_is_untouched(self):
        fonts, widths = font_en.dialogue_fonts(ROM)
        self.assertEqual(fonts[0][48:96], ROM[0x42BB6C + 48:0x42BB6C + 96])
        self.assertEqual(widths[1], 8)

    def test_every_marker_encodes(self):
        _, widths = font_en.dialogue_fonts(ROM)
        for block, entries in insert.strings():
            for e in entries:
                t = insert.marker_text(e, block, widths)
                font_en.encode(t)
                if block in insert.TYPEWRITER:
                    self.assertLessEqual(t.count("<br>"), 1, e["id"])
                    for line in t.replace("<page>", "").replace("<end>", "").split("<br>"):
                        self.assertLessEqual(font_en.px_var(line, widths), insert.DIALOGUE_W * 8, e["id"])

    def test_non_text_stays_and_words_dont(self):
        entries = {e["id"]: (b, e) for b, es in insert.strings() for e in es}
        for id in ("188EA4", "45AA42", "23C82E", "4642B0", "1865A0"):  # bead, rule of colons, empty slot, variables alone, dash
            self.assertTrue(insert.non_text(entries[id][1]), id)
        for id in ("17D524", "188C9E", "23CED2", "44128A"):  # ……, ？？？ and [FFEA]‼ read as words; a label behind a bead
            self.assertFalse(insert.non_text(entries[id][1]), id)
        _, widths = font_en.dialogue_fonts(ROM)
        block, e = entries["44128A"]
        self.assertTrue(insert.marker_text(e, block, widths).startswith("●"))  # the title menu's cursor sits on this cell

    def test_every_jump_site_stays_in_range(self):
        r = insert.Rom(ROM)
        insert.engine(r, {})
        table = struct.unpack_from("<2I", r.out, insert.FONT_TABLE)
        self.assertTrue(all(a >= 0x08800000 for a in table))

    def test_colon_keeps_the_games_two_dot_leader(self):
        # DC is ‥ (the field menu's locked rows draw it by code); EC is the Japanese font's own colon, which the credits draw
        self.assertNotIn(0xDC, font_en.glyphs())
        self.assertEqual(font_en.CODES[":"], 0xEC)
        self.assertEqual(insert.credits_en("ART:"), bytes([0xA4, 0xB5, 0xB7, 0xEC]))

    def test_credits_have_no_period_or_comma(self):
        # the roll draws the Japanese glyphs: 。 and 、 at the English codes
        en = json.loads((ROOT / "script" / "credits.json").read_text(encoding="utf-8"))[0]["en"]
        self.assertFalse(set(".,") & set(en.replace("[", "").replace("]", "")))


if __name__ == "__main__":
    unittest.main()
