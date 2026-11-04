"""regen.py reads scenes.lua as text; a scene its regex misses is silently never run."""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools/debug"))
import regen  # noqa: E402


class Scenes(unittest.TestCase):
    def test_parses_every_entry_and_its_options(self):
        text = (ROOT / "tools/debug/scenes.lua").read_text(encoding="utf-8")
        table = regen.scenes()
        self.assertEqual(len(table), len(re.findall(r"^\s+\w+ = \{.*note = ", text, re.M)))
        self.assertEqual(table["menu_save"][2], True)
        self.assertEqual(table["continue_save"][3], "menu_save")
        self.assertEqual(table["battle_result"][:2], (4300, 20))
        self.assertEqual(table["town"][:2], (2600, 216))

    def test_a_save_reader_names_a_save_writer(self):
        table = regen.scenes()
        for name, (_, _, _, sav) in table.items():
            if sav:
                self.assertTrue(table[sav][2], name)


if __name__ == "__main__":
    unittest.main()
