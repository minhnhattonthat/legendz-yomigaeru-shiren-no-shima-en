"""asm/doll.s's name converters in Unicorn: the doll image keeps a name a byte a letter (issue #1)."""
import struct
import sys
import unittest
from pathlib import Path

from unicorn import UC_ARCH_ARM, UC_MODE_THUMB, Uc
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_SP

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import font_en
import insert
from asm_thumb import assemble

CODE, PAIRS, STOP, WORDS, BYTES = 0x08800000, 0x08500000, 0x08900000, 0x02000000, 0x02001000


def run(entry, src, dst, count, pairs):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    uc.mem_map(0x08000000, 0x1000000)
    uc.mem_map(0x02000000, 0x10000)
    uc.mem_map(0x03000000, 0x8000)
    uc.mem_write(CODE, assemble(ROOT / "asm" / "doll.s", CODE, {"PAIRS": PAIRS - font_en.PAIR_BASE * 4}))
    uc.mem_write(PAIRS, font_en.pair_table(pairs) or b"\0\0")
    uc.mem_write(STOP, struct.pack("<H", 0xE7FE))
    return uc, entry, src, dst, count


def call(uc, entry, r0, r1, count):
    for reg, v in ((UC_ARM_REG_R0, r0), (UC_ARM_REG_R1, r1), (UC_ARM_REG_R2, count), (UC_ARM_REG_SP, 0x03007F00), (UC_ARM_REG_LR, STOP | 1)):
        uc.reg_write(reg, v)
    uc.emu_start((CODE + insert.DOLL_ENTRY[entry]) | 1, STOP, count=2000)


class Names(unittest.TestCase):
    def roundtrip(self, text, pairs=None, slot=8):
        data = font_en.encode(text + "<end>", pairs)
        words = list(struct.unpack("<%dH" % (len(data) // 2), data))
        uc, *_ = run("pack", WORDS, BYTES, slot, pairs or {})
        uc.mem_write(WORDS, struct.pack("<%dH" % (slot + 1), *(words + [0xFFFF] * slot)[:slot + 1]))
        call(uc, "pack", WORDS, BYTES, slot)
        packed = bytes(uc.mem_read(BYTES, slot))
        call(uc, "unpack", BYTES, WORDS + 0x100, slot)
        back = list(struct.unpack("<%dH" % slot, uc.mem_read(WORDS + 0x100, slot * 2)))
        return packed, back

    def test_every_letter_survives(self):
        for text in ("Alex", "Hexadra", "Bob o p", "xyz;&*=", "[]<>_ab"):
            packed, back = self.roundtrip(text)
            self.assertEqual(back[:len(text)], [font_en.CODES[c] for c in text], text)
            self.assertNotIn(0xFF, packed[:len(text)], text)  # 0xFF ends a name: o must not be it
            self.assertEqual(back[len(text)], 0xFFFF, text)

    def test_pairs_go_in_as_letters_and_stop_at_the_slot(self):
        pairs = {}
        packed, back = self.roundtrip("Hexadragon", pairs)
        self.assertTrue(pairs)
        self.assertEqual(back, [font_en.CODES[c] for c in "Hexadrag"])

    def test_v1_0_dolls_read_back(self):
        """v1.0 kept the low byte: x 0x108 as 0x08, r as 0x02. Those still read as their letters."""
        uc, *_ = run("unpack", BYTES, WORDS, 5, {})
        uc.mem_write(BYTES, bytes((0xA4, 0xFC, 0xF5, 0x08, 0xFF)))
        call(uc, "unpack", BYTES, WORDS, 5)
        self.assertEqual(list(struct.unpack("<5H", uc.mem_read(WORDS, 10))), [font_en.CODES[c] for c in "Alex"] + [0xFFFF])


if __name__ == "__main__":
    unittest.main()
