import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import jpcodec

ROM = next((ROOT / "rom").glob("*.gba"))


class JpCodec(unittest.TestCase):
    def test_table_is_one_to_one(self):
        self.assertEqual(len(set(jpcodec.TABLE.values())), len(jpcodec.TABLE))

    def test_known_strings_from_rom(self):
        rom = ROM.read_bytes()
        # read in Mesen from the first dialogue box of a new game
        first = jpcodec.decode(rom[0x180F1C:0x180F1C + 60])
        self.assertEqual(first, "…あおいそら　ながれるくも！<br>\nそしてこの　ひろいうなばら！<page>\n")

    def test_roundtrip_unknown_words(self):
        raw = struct.pack("<6H", 1, 0x106, 0xFFE3, 0xFFFD, 0xA4, 0xFFFF)
        self.assertEqual(jpcodec.encode(jpcodec.decode(raw)), raw)


if __name__ == "__main__":
    unittest.main()
