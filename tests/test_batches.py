"""The batch check's rules that aren't plain arithmetic."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import batches  # noqa: E402


class Honorifics(unittest.TestCase):
    def test_needs_the_suffix_after_a_name(self):
        self.assertEqual(batches.honorific_problems("カンナちゃん　ですわよん♪", "It's cute little Kanna"), ["ちゃん: no -chan"])
        self.assertEqual(batches.honorific_problems("カンナちゃん　ですわよん♪", "Kanna-chan here"), [])

    def test_player_variable_and_stretch(self):
        self.assertEqual(batches.honorific_problems("[FFEE]ちゃんが", "You, [FFEE]"), ["ちゃん: no -chan"])
        self.assertEqual(batches.honorific_problems("シュウくんだぁ", "It's Shu-kuuun"), [])

    def test_only_after_a_name(self):
        self.assertEqual(batches.honorific_problems("さんざんだよ　ちゃんと　しなさい", "What a mess. Behave."), [])


class Overs(unittest.TestCase):
    def test_a_line_past_a_guess_is_listed(self):
        en = "Thunder Tower Thunder Tower<end>"
        blocks = {b: [] for b in batches.ORDER}
        blocks["adventure"] = [{"id": "X", "jp": "カミナリ<end>", "en": en, "owners": []}]
        out = batches.overs(blocks, {"X": (16, 1, "guess")}, batches.widths())
        self.assertEqual([o[0] for o in out], ["X"])


if __name__ == "__main__":
    unittest.main()
