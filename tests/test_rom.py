import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import check_rom


class RomPin(unittest.TestCase):
    def test_dump_matches_pin(self):
        check_rom.check()  # sys.exit on a missing or wrong dump


if __name__ == "__main__":
    unittest.main()
