"""Assemble a Thumb source file with keystone. @NAME@ in the source takes a hex value from `symbols`.

    python -X utf8 tools/asm_thumb.py asm/vwf.s      # prints the size
"""
import sys
from pathlib import Path

from keystone import KS_ARCH_ARM, KS_MODE_THUMB, Ks


def assemble(path, base, symbols=None):
    src = Path(path).read_text(encoding="utf-8")
    for k, v in (symbols or {}).items():
        src = src.replace("@%s@" % k, "0x%08X" % v)
    src = "\n".join(line.split("@")[0] for line in src.splitlines())  # keystone takes no @ comments
    return bytes(Ks(KS_ARCH_ARM, KS_MODE_THUMB).asm(src, base)[0])


if __name__ == "__main__":
    print(len(assemble(sys.argv[1], 0x08800000, {"WIDTHS": 0x08810000, "PAIRS": 0x08820000, "TAGFRAMES": 0x08830000})), "bytes")
