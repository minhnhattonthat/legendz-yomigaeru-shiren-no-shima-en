import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import build
import lz77

ROM = next((ROOT / "rom").glob("*.gba")).read_bytes()
PIECES = build.split(ROM)


class Identity(unittest.TestCase):
    def test_rebuild_is_byte_identical(self):
        self.assertTrue(build.join(ROM, PIECES) == ROM)  # ROM itself is pinned to rom.sha1 by test_rom.py

    def test_pieces_cover_the_rom_with_no_gap_or_overlap(self):
        at = 0
        for p in PIECES:
            self.assertEqual(p.start, at)
            self.assertGreater(p.end, p.start)
            at = p.end
        self.assertEqual(at, len(ROM))

    def test_every_kind_is_really_rebuilt(self):
        kinds = Counter(p.kind for p in PIECES)
        self.assertEqual(kinds["text"], len(build.TEXT))
        self.assertEqual(kinds["ptr"], len(build.POINTERS))
        self.assertGreater(kinds["lz"], 2000)

    def test_pointer_writer_keeps_the_flag_nibble(self):
        p = build.Piece(0, 4, "ptr", [(2, 0x08182EA4)])
        self.assertEqual(build.rebuild(b"", p), bytes.fromhex("a42e1828"))

    def test_changed_block_is_recompressed_vram_safe(self):
        p = next(p for p in PIECES if p.kind == "lz")
        changed = bytes(b ^ 1 for b in p.value)
        new = build.rebuild(ROM, p._replace(value=changed))
        self.assertEqual(lz77.decompress(new, vram_safe=True)[0], changed)


class RealBlocks(unittest.TestCase):
    def test_recompressed_blocks_decompress_to_the_same_data(self):  # the whole ROM: see rom-map.md
        blocks = [p for p in PIECES if p.kind == "lz"]
        for p in blocks[::100]:
            self.assertEqual(lz77.decompress(lz77.compress(p.value, 2), vram_safe=True)[0], p.value, hex(p.start))


if __name__ == "__main__":
    unittest.main()
