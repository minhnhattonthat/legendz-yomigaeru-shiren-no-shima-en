"""List scene entry candidates: every `00F2 <ptr>` (change-scene op, docs/re/script.md) in the script range, with the first
dialogue page reachable after the target and the count of references.

    python -X utf8 tools/scene_scan.py        # writes work/re/scenes.tsv
"""
import struct
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import jpcodec  # noqa: E402

SCRIPT_END = 0x8A000
TEXT = (0x1619D8, 0x184DCC)


def rom():
    line = (ROOT / "rom.sha1").read_text().splitlines()[-1].split("  ", 1)[1].strip()
    return (ROOT / line).read_bytes()


def pointer_hits(data, op):
    """Offsets of `op lo hi` where hi:lo is a ROM pointer into the script range (top nibble masked off)."""
    words = struct.unpack_from("<%dH" % (SCRIPT_END // 2), data)
    for i in range(len(words) - 2):
        if words[i] == op and words[i + 2] & 0x0FFF == 0x0800 | (words[i + 2] & 0xFF):
            p = (words[i + 2] << 16 | words[i + 1]) & 0x0FFFFFFF
            if 0x08000000 <= p < 0x08000000 + SCRIPT_END and not p & 1:
                yield i * 2, p - 0x08000000


def first_text(data, off, limit=0x600):
    """Decode the first `00DD`/`00BE` message after off: a cheap label for the scene."""
    for a in range(off, min(off + limit, SCRIPT_END), 2):
        w = struct.unpack_from("<H", data, a)[0]
        if w in (0xDD, 0xBE):
            p = (struct.unpack_from("<I", data, a + 4 if w == 0xDD else a + 2)[0] & 0x0FFFFFFF) - 0x08000000
            if TEXT[0] <= p < TEXT[1]:
                end = data.find(b"\xff\xff", p)
                return jpcodec.decode(data[p:min(end if end > 0 else p + 60, p + 60)]).replace("\n", "/")
    return ""


def place_name(data, off, limit=0x900):
    """Room label: the first `00E3 <id> 0000` (location card) after off, named by the table at 0x7EFFC4 (code at 0x080A3C0E)."""
    for a in range(off, min(off + limit, SCRIPT_END), 2):
        op, pid, zero = struct.unpack_from("<3H", data, a)
        if op == 0xE3 and zero == 0 and pid < 0x100:
            p = struct.unpack_from("<I", data, 0x7EFFC4 + pid * 4)[0]
            if 0x08188000 <= p < 0x08189000:
                raw = data[p - 0x08000000:p - 0x08000000 + 60]
                end = raw.find(b"\xff\xff")
                return "%02X %s" % (pid, jpcodec.decode(raw[:end & ~1 if end >= 0 else 60]))
    return ""


def main():
    data = rom()
    hits = list(pointer_hits(data, 0xF2))
    refs = Counter(t for _, t in hits)
    out = ["target\trefs\tfrom\tplace\tfirst_text"]
    for t, n in sorted(refs.items()):
        frm = next(f for f, x in hits if x == t)
        out.append("%06X\t%d\t%06X\t%s\t%s" % (t, n, frm, place_name(data, t), first_text(data, t)))
    dst = ROOT / "work/re/scenes.tsv"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(len(hits), "F2 hits,", len(refs), "targets ->", dst)


if __name__ == "__main__":
    main()
