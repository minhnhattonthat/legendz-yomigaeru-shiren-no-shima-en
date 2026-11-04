import json
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import extract
import jpcodec
import vmwalk

ROM = next((ROOT / "rom").glob("*.gba")).read_bytes()
FILES = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in (ROOT / "script").glob("*.json")}
REST = FILES.pop("unreferenced")
CREDITS = FILES.pop("credits")
ALL = [e for es in FILES.values() for e in es]


class Extract(unittest.TestCase):
    def test_every_string_reencodes_to_its_bytes(self):
        for e in ALL:
            a, b = int(e["id"], 16), int(e["end"], 16)
            rev = jpcodec.SPRITE_REV if e.get("font") == "sprite1" else jpcodec.REV
            self.assertEqual(jpcodec.encode(e["jp"], rev), ROM[a:b], e["id"])

    def test_credits_reencode(self):
        for e in CREDITS:
            self.assertEqual(jpcodec.encode8(e["jp"]), ROM[int(e["id"], 16):int(e["end"], 16)])

    def test_each_owner_holds_the_pointer(self):
        for e in ALL:
            self.assertTrue(e["owners"], e["id"])
            for o in e["owners"]:
                parts = o.split(":")
                nib = int(parts[2], 16) if len(parts) > 2 else 0
                v = struct.unpack_from("<I", ROM, int(parts[1], 16))[0]
                self.assertEqual(v, nib << 28 | 0x08000000 + int(e["id"], 16), o)

    def test_text_ranges_are_fully_covered(self):
        cover = {}
        for e in ALL:
            for o in range(int(e["id"], 16), int(e["end"], 16), 2):
                cover[o] = "string"
        for r in REST:
            for o in range(int(r["at"], 16), int(r["end"], 16), 2):
                self.assertNotIn(o, cover, r["at"])
                cover[o] = r["kind"]
        missing = [o for _, a, b in extract.BLOCKS for o in range(a, b, 2) if o not in cover]
        self.assertEqual(missing[:5], [])

    def test_leftovers_are_what_they_claim(self):
        ranges = extract.DATA_RUNS
        for r in REST:
            a, b = int(r["at"], 16), int(r["end"], 16)
            words = struct.unpack("<%dH" % ((b - a) // 2), ROM[a:b])
            if r["kind"] == "pad":
                self.assertEqual(set(words), {0xFFFF}, r["at"])
            elif r["kind"] == "data":
                self.assertTrue(any(x <= a and b <= y for x, y in ranges), r["at"])
            else:
                self.assertEqual(r["kind"], "dead")

    def test_files_match_the_extractor(self):
        blocks, rest, _ = extract.entries(ROM)
        for name, es in blocks.items():
            self.assertEqual([(e["id"], e["jp"], e["owners"]) for e in es],
                             [(e["id"], e["jp"], e["owners"]) for e in FILES.get(name, [])], name)
        self.assertEqual(rest, REST)

    def test_no_unknown_codes_in_owned_text(self):
        unknown = [e["id"] for e in ALL if "[0" in e["jp"] or "[1" in e["jp"]]
        self.assertEqual(unknown, [])


class Layouts(unittest.TestCase):
    def test_battle_kanji(self):
        # read in Mesen as ああああの攻撃!! (work/qa/bw); tools/spritefont.py matched the VRAM dump tile for tile
        self.assertEqual(jpcodec.decode(struct.pack("<2H", 0x130, 0x109)), "攻撃")
        self.assertEqual(jpcodec.decode(struct.pack("<2H", 0x100, 0x101)), "混乱")

    def test_quip_layout_makes_the_digits_read_as_punctuation(self):
        quips = " ".join(e["jp"] for e in FILES["quips"])
        for line in ("うそー‼", "10バイ", "なんちゃって★"):
            self.assertIn(line, quips)

    def test_credits_names(self):
        self.assertIn("わたなべ　けんじ", CREDITS[0]["jp"])
        self.assertIn("ビデオゲームカンパニー", CREDITS[0]["jp"])


class Walk(unittest.TestCase):
    def test_known_instructions(self):
        instrs, _, _ = vmwalk.walk(ROM)
        # from vmtrace.lua runs (all 715 traced PCs were in the walk when this was written)
        for off, op in ((0x1E0, 0x05), (0x1E6, 0x4A), (0x1EE, 0x8C), (0x1F4, 0xC1), (0x4F6, 0x5D)):
            self.assertEqual(instrs.get(off), op, hex(off))
        self.assertGreater(len(instrs), 85000)

    def test_operand_table_length(self):
        self.assertEqual(len(vmwalk.LEN), vmwalk.COUNT)


if __name__ == "__main__":
    unittest.main()
