"""Recursive walk of the script VM's bytecode: finds each instruction, so each text pointer has a decoded owner (docs/re/script.md).
Operand lengths come from vm_ops.py (handlers run in Unicorn), reconciled by hand. A linear sweep doesn't work: scripts hold data.

    python -X utf8 tools/vmwalk.py          # prints stats, writes work/re/walk.tsv
"""
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

COUNT = 0x12F
# operand bytes after the opcode, in opcode order
_LEN = [0, 2, 2, 4, 0, 4, 2, 2, 2, 2, 2, 4, 2, 2, 6, 2,  # 00
        2, 2, 2, 6, 4, 0, 6, 6, 6, 4, 4, 4, 6, 4, 0, 8,  # 10
        4, 8, 4, 8, 4, 2, 10, 2, 4, 4, 4, 6, 6, 2, 4, 2,  # 20
        0, 0, 0, 8, 4, 2, 2, 6, 4, 4, 4, 4, 12, 6, 10, 0,  # 30
        0, 2, 6, 4, 4, 6, 4, 4, 4, 4, 6, 4, 2, 0, 0, 0,  # 40
        20, 10, 6, 0, 4, 10, 4, 4, 4, 2, 2, 6, 10, 0, 0, 6,  # 50
        2, 2, 2, 0, 4, 6, 6, 4, 4, 8, 4, 4, 4, 4, 8, 2,  # 60
        4, 0, 2, 6, 6, 2, 0, 0, 4, 6, 4, 4, 2, 8, 4, 20,  # 70
        4, 0, 6, 6, 8, 6, 2, 16, 16, 8, 0, 0, 4, 2, 2, 6,  # 80
        4, 6, 2, 2, 4, 6, 0, 0, 4, 0, 0, 0, 0, 2, 2, 2,  # 90
        2, 4, 2, 12, 0, 2, 4, 0, 4, 4, 4, 0, 4, 4, 0, 6,  # A0
        6, 2, 2, 2, 2, 6, 2, 2, 2, 4, 6, 8, 2, 2, 4, 4,  # B0
        6, 2, 6, 0, 0, 4, 6, 6, 6, 6, 6, 8, 4, 8, 4, 4,  # C0
        6, 0, 0, 2, 8, 6, 2, 4, 2, 0, 4, 4, 4, 6, 4, 0,  # D0
        0, 0, 0, 4, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2,  # E0
        2, 6, 4, 4, 2, 2, 4, 0, 2, 2, 0, 4, 4, 0, 6, 2,  # F0
        2, 0, 6, 6, 4, 2, 4, 2, 2, 2, 2, 2, 2, 2, 4, 6,  # 100
        0, 8, 6, 8, 2, 6, 16, 0, 0, 2, 8, 2, 2, 6, 4, 2,  # 110
        14, 14, 0, 0, 0, 6, 4, 4, 14, 2, 2, 4, 2, 6, 2]  # 120
LEN = dict(enumerate(_LEN))
# op: (index of the count word, words before the list): the list's length is in the stream
VAR = {0x2D: (0, 1), 0x39: (1, 2), 0x47: (1, 2), 0xFE: (2, 3), 0xDA: (1, 2), 0xDB: (1, 2)}
# word 0 is `dist`: target = address after the opcode + 2 * dist (0x01 and 0x25 go backwards)
BRANCH = {0x02, 0x06, 0x0B, 0x0E, 0x13, 0x14, 0x1D, 0x2E, 0x2F, 0x38, 0x58, 0x64, 0x84, 0xB3, 0xB4, 0xCA, 0xCC, 0xCD, 0xDA, 0xDB, 0xF8, 0xF9,
          0xFB, 0x106, 0x10A, 0x10B, 0x10C, 0x10D, 0x10E, 0x114, 0x11A, 0x125, 0x12B, 0x12C}
BACK = {0x01, 0x25}
# ptr32 at word 0: another script to run, in this task or a new one
JUMP = {0x03, 0x05, 0x43, 0xF2}
SPAWN = {0x1A, 0x42, 0x56, 0x57, 0x7A, 0x8C, 0xF6}
NO_FALL = {0x01, 0x02, 0x04, 0x05, 0x06, 0x15, 0x1E, 0x25, 0x30, 0x43, 0xF2}
# ptr32 operands that name text, as (word index): read from each handler
TEXT_PTR = {0xBE: (0,), 0xBF: (0,), 0xDD: (1,), 0x33: (2,), 0xCB: (0, 2), 0x116: (0, 2, 4, 6), 0xF1: (1,), 0x120: (5,), 0x121: (5,)}
SCRIPT_END = 0x889A6  # the last ret; Thumb starts at 0x889A8


def u16(rom, off):
    return struct.unpack_from("<H", rom, off)[0]


def ptr_at(rom, off):
    return struct.unpack_from("<I", rom, off)[0]


def length(rom, off, op):
    """Operand bytes of the instruction at off."""
    if op in VAR:
        idx, before = VAR[op]
        return (before + u16(rom, off + 2 + idx * 2)) * 2
    return LEN[op]


def targets(rom, off, op):
    """Script addresses this instruction can pass control to, fall-through excluded."""
    out = []
    if op in BRANCH:
        out.append(off + 2 + 2 * u16(rom, off + 2))
    if op in BACK:
        out.append(off + 2 - 2 * u16(rom, off + 2))
    if op in JUMP or op in SPAWN:
        v = ptr_at(rom, off + 2) & 0x0FFFFFFF
        if 0x08000000 <= v < 0x08800000 and not v & 1:
            out.append(v - 0x08000000)
    return out


def walk_from(rom, seeds, known=None):
    """Follow control flow from seeds. Returns (instructions {off: op}, ok). ok is False if a path hit a bad opcode."""
    known = known or {}
    seen, todo, ok = {}, list(seeds), True
    while todo:
        off = todo.pop()
        while True:
            if off in seen or off in known:
                break
            if not (0 <= off < SCRIPT_END) or off & 1:
                ok = False
                break
            op = u16(rom, off)
            if op == 0 or op >= COUNT:
                ok = False
                break
            seen[off] = op
            todo.extend(targets(rom, off, op))
            if op in NO_FALL:
                break
            off += 2 + length(rom, off, op)
    return seen, ok


def literal_seeds(rom):
    """Script addresses named by code literals and data tables, with where each came from."""
    out = defaultdict(list)
    for a in range(0x8A000, len(rom) - 3, 4):
        v = ptr_at(rom, a)
        if 0x080001E0 <= v < 0x08000000 + SCRIPT_END and not v & 1:
            out[v - 0x08000000].append(a)
    return out


def walk(rom):
    """Walk from task 0's start; then from literal seeds, keeping a seed's walk only if it stays clean."""
    known, ok = walk_from(rom, [0x1E0])
    rejected = []
    seeds = literal_seeds(rom)
    for s in sorted(seeds):
        if s in known:
            continue
        got, ok = walk_from(rom, [s], known)
        if ok:
            known.update(got)
        else:
            rejected.append(s)
    # code nothing above names (dead rooms, entries reached through RAM): after padding or a data table, the first word that
    # starts a clean walk. Data can pass as code here, which is harmless: extract.py only takes a pointer that hits a string start
    while True:
        grown = False
        for a, b in gaps(coverage(rom, known)):
            for s in range(a, b, 2):
                got, ok = walk_from(rom, [s], known)
                if ok and got:
                    known.update(got)
                    grown = True
                    break
        if not grown:
            return known, rejected, seeds


def coverage(rom, instrs):
    cov = bytearray(SCRIPT_END)
    for off, op in instrs.items():
        n = 2 + length(rom, off, op)
        cov[off:off + n] = b"\1" * n
    return cov


def gaps(cov):
    """(start, end) of each unwalked run from 0x1E0 up."""
    out, o = [], 0x1E0
    while o < SCRIPT_END:
        if cov[o]:
            o += 2
            continue
        s = o
        while o < SCRIPT_END and not cov[o]:
            o += 2
        out.append((s, o))
    return out


def text_refs(rom, instrs):
    """(site offset, word index, op, nibble, target offset) for each TEXT_PTR operand in the walked instructions."""
    out = []
    for off, op in sorted(instrs.items()):
        for i in TEXT_PTR.get(op, ()):
            site = off + 2 + 2 * i
            v = ptr_at(rom, site)
            if 0x08000000 <= v & 0x0FFFFFFF < 0x08800000:
                out.append((site, i, op, v >> 28, (v & 0x0FFFFFFF) - 0x08000000))
    return out


def main():
    from vm_ops import rom as load
    rom = load()
    instrs, rejected, seeds = walk(rom)
    print("instructions", len(instrs), "bytes", sum(2 + length(rom, o, p) for o, p in instrs.items()))
    print("literal seeds", len(seeds), "rejected", len(rejected), ["%X" % s for s in rejected[:40]])
    print("text refs", len(text_refs(rom, instrs)))
    ops = Counter(instrs.values())
    print("never walked", ["%X" % i for i in range(1, COUNT) if i not in ops])
    # any pointer into 0x08xxxxxx in a walked operand, by op and word index
    stats = Counter()
    for off, op in instrs.items():
        n = length(rom, off, op) // 2
        for i in range(n - 1):
            v = ptr_at(rom, off + 2 + 2 * i) & 0x0FFFFFFF
            if 0x08000000 <= v < 0x08800000 and not v & 1:
                stats[(op, i, (v - 0x08000000) >> 20)] += 1
    print("pointer operands (op, word, MB):", sorted(((("%02X" % a), b, c), n) for (a, b, c), n in stats.items()))
    dst = ROOT / "work/re/walk.tsv"
    dst.parent.mkdir(parents=True, exist_ok=True)
    with dst.open("w", newline="\n") as f:
        for off, op in sorted(instrs.items()):
            f.write("%06X\t%04X\t%s\n" % (off, op, " ".join("%04X" % u16(rom, off + 2 + 2 * i) for i in range(length(rom, off, op) // 2))))
    print(dst)


if __name__ == "__main__":
    main()
