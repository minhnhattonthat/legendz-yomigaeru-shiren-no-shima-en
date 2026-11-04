import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import lz77


class Lz77(unittest.TestCase):
    def test_roundtrip(self):
        blob = bytes(range(64)) * 20 + b"abcabcabc" * 50 + b"\x00" * 300
        for min_disp in (1, 2):
            packed = lz77.compress(blob, min_disp)
            got, end = lz77.decompress(packed)
            self.assertEqual(got, blob)
            self.assertEqual(end, len(packed))

    def test_vram_safe_has_no_disp1(self):
        lz77.decompress(lz77.compress(b"\x00" * 100, 2), vram_safe=True)  # raises on disp 1

    def test_rejects_garbage(self):
        with self.assertRaises(ValueError):
            lz77.decompress(b"\x11\x00\x00\x00")
        with self.assertRaises(ValueError):
            lz77.decompress(b"\x10\x40\x00\x00\xff\x00\x00")  # back-reference before start


if __name__ == "__main__":
    unittest.main()
