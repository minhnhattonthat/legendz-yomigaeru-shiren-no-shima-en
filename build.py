"""build.py: split the ROM into pieces (text, pointer tables, LZ blocks, raw), rebuild each one, join them -> build/legendz_en.gba.
There is no archive to unpack: the ROM's pieces are the ranges in docs/re/text.md and rom-map.md. With no edits the output is
byte-identical to the dump (tests/test_identity.py)."""
import hashlib
import struct
import sys
from collections import namedtuple
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
import check_rom
import jpcodec
import lz77

OUT = ROOT / "build" / "legendz_en.gba"
Piece = namedtuple("Piece", "start end kind value")

# start, end: docs/re/text.md, Text ranges
TEXT = [(0x1619D8, 0x184DCC), (0x1857D8, 0x187A5C), (0x188070, 0x188EA8), (0x188F00, 0x1895B8), (0x23C3D4, 0x23D110),
        (0x2A7714, 0x2A9EC2), (0x2AB4E0, 0x2AB97C), (0x2ABE2C, 0x2AC100), (0x2AFEE0, 0x2B0ADE), (0x434BF8, 0x434E40),
        (0x440C9C, 0x448836), (0x44F4B8, 0x450016), (0x45A602, 0x45B002), (0x45BBCE, 0x466CF0), (0x47BD3C, 0x47BF5E)]
# start, count. shortcut: only the plain 4-byte tables; struct tables and script pointers need phase 4's owner walk (text.md)
POINTERS = [(0x7EFF18, 235), (0x7F330C, 190), (0x7F66CC, 875), (0x7F75E8, 89), (0x7F7F48, 23)]


def split(rom):
    """Cover the whole ROM with contiguous pieces. Text and pointer tables win over any LZ scan hit that overlaps them."""
    pieces = [Piece(a, b, "text", jpcodec.decode(rom[a:b])) for a, b in TEXT]
    for a, n in POINTERS:
        words = struct.unpack_from("<%dI" % n, rom, a)
        # the top nibble can hold flags (the VM masks it off); keep it apart from the address
        pieces.append(Piece(a, a + 4 * n, "ptr", [(w >> 28, w & 0x0FFFFFFF) for w in words]))
    named = list(pieces)
    for off, data, end in lz77.scan(rom):
        if not any(off < p.end and end > p.start for p in named):
            pieces.append(Piece(off, end, "lz", data))
    out = []
    at = 0
    for p in sorted(pieces):
        if at < p.start:
            out.append(Piece(at, p.start, "raw", rom[at:p.start]))
        out.append(p)
        at = p.end
    if at < len(rom):
        out.append(Piece(at, len(rom), "raw", rom[at:]))
    return out


def rebuild(rom, p):
    if p.kind == "text":
        return jpcodec.encode(p.value)
    if p.kind == "ptr":
        return b"".join(struct.pack("<I", nib << 28 | addr) for nib, addr in p.value)
    if p.kind == "lz":
        # our compressor doesn't reproduce the original bytes, so an unchanged block keeps them
        if lz77.decompress(rom, p.start)[0] == p.value:
            return rom[p.start:p.end]
        return lz77.compress(p.value, 2)  # min_disp 2: 1,873 of 2,159 blocks are VRAM-safe, so assume the target may be VRAM
    return p.value


def join(rom, pieces):
    out = bytearray()
    for p in pieces:
        new = rebuild(rom, p)
        if len(new) != p.end - p.start:  # later pieces would shift; relocation comes with insertion
            sys.exit("%s piece at 0x%06X changed size: %d -> %d" % (p.kind, p.start, p.end - p.start, len(new)))
        out += new
    return bytes(out)


def build(rom):
    return join(rom, split(rom))


def main():
    check_rom.check()
    rom = next((ROOT / "rom").glob("*.gba")).read_bytes()
    new = build(rom)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_bytes(new)
    print("%s %d bytes sha1 %s" % (OUT.relative_to(ROOT), len(new), hashlib.sha1(new).hexdigest()))
    print("identical to the dump" if new == rom else "differs from the dump")


if __name__ == "__main__":
    main()
