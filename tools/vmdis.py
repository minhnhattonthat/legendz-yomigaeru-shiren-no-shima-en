"""Disassemble script VM bytecode linearly. Operand lengths come from vm_ops.py's handler walk plus OVERRIDES checked by hand
or against vmtrace.lua logs. Messages print decoded. Phase 4's extractor should grow out of this.

    python -X utf8 tools/vmdis.py 0x2483A [COUNT]     # hex ROM offset or 08xxxxxx address, instructions (default 60)
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import jpcodec  # noqa: E402
from vm_ops import COUNT, TABLE, handler_ops, rom  # noqa: E402

# Operand bytes (after the opcode word) where the handler walk is ambiguous.
OVERRIDES = {0x01: 2, 0x02: 2, 0x03: 4, 0x04: 0, 0x05: 4, 0x06: 2, 0x13: 6, 0x14: 4, 0x15: 0, 0x25: 2, 0x40: 0, 0x84: 8,
             0xC1: 2, 0xC2: 6, 0xCA: 6, 0xCC: 4, 0xCD: 8, 0xDD: 6, 0xF2: 4, 0x2E: 4, 0x33: 8, 0x8C: 4, 0x3C: 12, 0x4A: 6}
NAMES = {0x01: "yield_back", 0x02: "yield_fwd", 0x03: "call", 0x04: "ret", 0x05: "jump", 0x06: "skip", 0x07: "wait", 0x09: "set_flag",
         0x0A: "clear_flag", 0x0B: "if_flag", 0x15: "end_task", 0x19: "native", 0x4A: "set_mem", 0x84: "if_mem", 0x8C: "spawn",
         0xBE: "msg_be", 0xDD: "msg", 0xF2: "change_scene"}
PTR_AT = {0x03: 0, 0x05: 0, 0x19: 0, 0x8C: 0, 0xF2: 0, 0xBE: 0, 0xDD: 2}


def lengths(data):
    out = {}
    for i in range(COUNT):
        h = struct.unpack_from("<I", data, TABLE + i * 4)[0]
        adv, jump, _ = handler_ops(data, h)
        out[i] = OVERRIDES.get(i, max(adv) if adv else 0)
    return out


def text_at(data, p):
    end = p
    while end < p + 80 and struct.unpack_from("<H", data, end)[0] not in (0xFFFF, 0xFFFE):
        end += 2
    return jpcodec.decode(data[p:end]).replace("\n", "/")


def dis(data, off, count):
    ln = lengths(data)
    for _ in range(count):
        op = struct.unpack_from("<H", data, off)[0]
        if op >= COUNT:
            print("%06X  ???? %04X" % (off, op))
            return
        n = ln[op]
        if op == 0xFE:  # choice box: 3 words, then that many option words
            n = 6 + struct.unpack_from("<H", data, off + 6)[0] * 2
        words =struct.unpack_from("<%dH" % (n // 2), data, off + 2)
        note = ""
        if op in PTR_AT:
            i = PTR_AT[op] // 2
            p = ((words[i + 1] << 16 | words[i]) & 0x0FFFFFFF) if len(words) > i + 1 else 0
            note = " -> %07X" % p
            if op in (0xDD, 0xBE) and 0x08000000 <= p < 0x08800000:
                note += "  " + text_at(data, p - 0x08000000)
        print("%06X  %04X %-12s %s%s" % (off, op, NAMES.get(op, ""), " ".join("%04X" % w for w in words), note))
        off += 2 + n


if __name__ == "__main__":
    a = int(sys.argv[1], 16) & 0x7FFFFF
    dis(rom(), a, int(sys.argv[2]) if len(sys.argv) > 2 else 60)
