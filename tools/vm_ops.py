"""Tabulate the script VM's opcodes from the handler table at 0x7F25E0: handler address, how far each exit advances the
script PC, and whether it writes a pointer into the PC (a jump). Static guess; work/qa traces confirm it (docs/re/script.md).

    python -X utf8 tools/vm_ops.py          # writes work/re/vm_ops.tsv
"""
import re
import struct
import sys
from pathlib import Path

import capstone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from check_rom import check  # noqa: E402

TABLE, COUNT = 0x7F25E0, 317


def rom():
    check()
    line = (ROOT / "rom.sha1").read_text().split("  ", 1)[1].strip()
    return (ROOT / line).read_bytes()


def handler_ops(data, addr):
    """Walk the handler's straight code; return (advances, jump, calls). Stops at the last return past the furthest branch."""
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    md.skipdata = True
    off = (addr & ~1) - 0x08000000
    adv, calls = set(), []
    jump = False
    far = addr & ~1
    last_imm = {}
    for ins in md.disasm(data[off:off + 800], addr & ~1):
        m = ins.mnemonic
        a = ins.op_str
        im = re.match(r"(r\d), #(0x[0-9a-f]+|\d+)$", a)
        if m == "adds" and im:
            last_imm[im[1]] = int(im[2], 0)
        im3 = re.match(r"(r\d), (r\d), #(0x[0-9a-f]+|\d+)$", a)
        if m == "adds" and im3:
            last_imm[im3[1]] = int(im3[3], 0)
        s = re.match(r"(r\d), \[r\d+, #4\]$", a)
        if m == "str" and s:
            if s[1] in last_imm:
                adv.add(last_imm[s[1]])
            else:
                jump = True
        if m == "bl":
            calls.append(int(a.lstrip("#"), 16))
        b = re.match(r"#(0x[0-9a-f]+)$", a)
        if m.startswith("b") and m not in ("bl", "bx") and b:
            far = max(far, int(b[1], 16))
        if (m == "pop" and "pc" in a) or m == "bx":
            if ins.address >= far:
                break
    return adv, jump, calls


def main():
    data = rom()
    out = ["op\thandler\tadvance\tjump\tcalls"]
    for i in range(COUNT):
        h = struct.unpack_from("<I", data, TABLE + i * 4)[0]
        adv, jump, calls = handler_ops(data, h)
        out.append("%04X\t%08X\t%s\t%s\t%s" % (i, h, ",".join(str(x) for x in sorted(adv)), "J" if jump else "",
                                               " ".join("%07X" % c for c in calls[:6])))
    dst = ROOT / "work/re/vm_ops.tsv"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text("\n".join(out) + "\n")
    print(dst)


if __name__ == "__main__":
    main()
