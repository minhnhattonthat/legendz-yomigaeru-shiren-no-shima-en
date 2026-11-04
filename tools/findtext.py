"""Find a line of game text, and the script ops that point at it. Native calls are tallied with --natives.

    python -X utf8 tools/findtext.py いらっしゃいませ [CONTEXT_BYTES]     # text hits, each pointer, and a disassembly after it
    python -X utf8 tools/findtext.py --natives                            # op 0019 targets by number of call sites
    python -X utf8 tools/findtext.py --lines 20000 20C20                  # script lines and scene changes in a hex range
"""
import collections
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import jpcodec  # noqa: E402
from vm_ops import rom  # noqa: E402
from vmdis import dis, text_at  # noqa: E402

SCRIPT_END = 0x0A0000  # shortcut: bytecode range from rom-map.md; widen if a script is found past it


def hits(data, needle):
    p = data.find(needle)
    while p >= 0:
        if p % 2 == 0:
            yield p
        p = data.find(needle, p + 1)


def natives(data):
    tally = collections.Counter()
    for off in range(0x1E0, SCRIPT_END, 2):
        op, lo, hi = struct.unpack_from("<3H", data, off)
        if op == 0x19 and hi in range(0x0800, 0x0817) and lo & 1:
            tally[(hi << 16 | lo) & ~1] += 1
    for addr, n in tally.most_common():
        print("%08X %d" % (addr, n))


def lines(data, lo, hi):
    """Every 00DD/0033/00BE line and 00F2 scene change in a script range, whatever the disassembler thinks of the bytes between."""
    for off in range(lo, hi, 2):
        op = struct.unpack_from("<H", data, off)[0]
        if op == 0xF2:
            at = 2
        elif op == 0xBE:
            at = 2
        elif op in (0xDD, 0x33):
            at = 4
        else:
            continue
        p = struct.unpack_from("<I", data, off + at)[0] & 0x0FFFFFFF
        if 0x08000000 <= p < 0x08800000 and p % 2 == 0:
            print("%06X %04X %s" % (off, op, "-> %06X" % (p - 0x08000000) if op == 0xF2 else text_at(data, p - 0x08000000)))


def main():
    data = rom()
    if sys.argv[1] == "--natives":
        return natives(data)
    if sys.argv[1] == "--lines":
        return lines(data, int(sys.argv[2], 16), int(sys.argv[3], 16))
    needle = jpcodec.encode(sys.argv[1])
    context = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    for p in hits(data, needle):
        print("TEXT %06X %s" % (p, text_at(data, p)))
        ptr = struct.pack("<I", 0x08000000 + p)
        for ref in hits(data, ptr):
            print("  ref %06X" % ref)
            if ref < SCRIPT_END:
                dis(data, ref - 4 if data[ref - 4] == 0xDD else ref - 2, context)


if __name__ == "__main__":
    main()
