"""Tabulate the script VM's opcodes by running each handler (table 0x7F25E0) in Unicorn with its callees stubbed: which operand
bytes it reads and where it leaves the script PC, over a grid of operand fills and stub returns. Evidence for OPS in vmwalk.py
(docs/re/script.md); a path no fill reaches isn't seen, so vmwalk's cross-checks decide.

    python -X utf8 tools/vm_ops.py          # writes work/re/vm_ops.tsv
"""
import struct
import sys
from pathlib import Path

from unicorn import UC_ARCH_ARM, UC_HOOK_BLOCK, UC_HOOK_MEM_READ, UC_MODE_THUMB, Uc, UcError
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_SP

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from check_rom import check  # noqa: E402

TABLE, COUNT = 0x7F25E0, 0x12F  # 0x12F+ point at data
TASK, SPC, STOP = 0x03002780, 0x09000100, 0x0A000000
FILLS = (0, 1, 2, 3, 0x10, 0x8001, 0xFFFF, 0x1234)
STUBS = (0, 1, 2, 0xFFFFFFFF)


def rom():
    check()
    line = (ROOT / "rom.sha1").read_text().split("  ", 1)[1].strip()
    return (ROOT / line).read_bytes()


def machine(data):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    uc.mem_map(0x08000000, 0x800000)
    uc.mem_write(0x08000000, data)
    for base, size in ((0x02000000, 0x40000), (0x03000000, 0x8000), (0x04000000, 0x1000), (0x05000000, 0x1000), (0x06000000, 0x20000),
                       (0x07000000, 0x1000), (0x09000000, 0x1000), (STOP, 0x1000)):
        uc.mem_map(base, size)
    return uc


def run(uc, handler, fill, stub):
    """Return (operand offsets read, final PC delta or None if the run crashed or spun)."""
    start = handler & ~1
    reads = set()

    def on_block(uc, addr, size, _):
        if addr == STOP:
            uc.emu_stop()
        elif not start <= addr < start + 0x600:
            uc.reg_write(UC_ARM_REG_R0, stub)
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def on_read(uc, access, addr, size, value, _):
        if 0x09000000 <= addr < 0x09001000:
            reads.update(addr + i - SPC for i in range(size))

    uc.mem_write(0x09000000, struct.pack("<H", fill) * 0x800)
    uc.mem_write(0x02000000, b"\0" * 0x40000)
    uc.mem_write(0x03000000, b"\0" * 0x8000)
    uc.mem_write(TASK + 4, struct.pack("<I", SPC))
    uc.reg_write(UC_ARM_REG_R0, TASK)
    uc.reg_write(UC_ARM_REG_SP, 0x03007000)
    uc.reg_write(UC_ARM_REG_LR, STOP | 1)
    hooks = [uc.hook_add(UC_HOOK_BLOCK, on_block), uc.hook_add(UC_HOOK_MEM_READ, on_read)]
    try:
        uc.emu_start(handler | 1, STOP, count=4000)
        pc = struct.unpack("<I", uc.mem_read(TASK + 4, 4))[0]
        delta = pc - SPC
    except UcError:
        delta = None
    for h in hooks:
        uc.hook_del(h)
    return reads, delta


def analyse(data, op):
    handler = struct.unpack_from("<I", data, TABLE + op * 4)[0]
    uc = machine(data)
    reads, deltas = set(), {}
    for fill in FILLS:
        for stub in STUBS:
            r, d = run(uc, handler, fill, stub)
            reads |= r
            deltas.setdefault(d, (fill, stub))
    return handler, sorted(reads), deltas


def main():
    data = rom()
    out = ["op\thandler\tread_bytes\tdeltas"]
    for op in range(COUNT):
        handler, reads, deltas = analyse(data, op)
        out.append("%04X\t%08X\t%s\t%s" % (op, handler, max(reads) + 1 if reads else 0,
                                           " ".join(sorted("%s" % ("x" if d is None else d) for d in deltas))))
    dst = ROOT / "work/re/vm_ops.tsv"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text("\n".join(out) + "\n")
    print(dst)


if __name__ == "__main__":
    main()
