"""extract.py: dump the game's text to script/<block>.json with each string's decoded owners (docs/re/text.md).

Owners: script VM operands (vmwalk.py), Thumb literal words, and words in the named table regions. Everything else in a text
range is accounted for in script/unreferenced.json. Re-running keeps en/status/notes by id, and lists any id whose jp changed.

    python -X utf8 tools/extract.py
"""
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import jpcodec  # noqa: E402
import vmwalk  # noqa: E402

OUT = ROOT / "script"
# name, start, end: docs/re/text.md, Text ranges
BLOCKS = [("dialogue", 0x1619D8, 0x184DCC), ("items", 0x1857D8, 0x187A5C), ("places", 0x188070, 0x188EA8), ("names_old", 0x188F00, 0x1895B8),
          ("battle", 0x23C3D4, 0x23D110), ("skills", 0x2A7714, 0x2A9EC2), ("skills2", 0x2AB4E0, 0x2AB97C), ("skills3", 0x2ABE2C, 0x2AC100),
          ("legendz", 0x2AFEE0, 0x2B0ADE), ("rental", 0x434BF8, 0x434E40), ("adventure", 0x440C9C, 0x441882), ("quips", 0x441882, 0x448836),
          ("cards", 0x44F4B8, 0x450016), ("menus", 0x45A602, 0x45B002), ("system", 0x45BBCE, 0x466CF0), ("link", 0x47BD3C, 0x47BF5E)]
# drawn with sprite font 0 (kanji cells) or 1 (its own symbol order): text.md, Sprite font
SPRITE_LAYOUT = {"quips"}
# 4-aligned pointer words live here; tables are mixed with other fields, so a word counts only if it hits a text-like string
TABLE_REGIONS = [(0x187A5C, 0x188070), (0x188EA8, 0x188F00), (0x1895B8, 0x18AC3C), (0x23C000, 0x23D800), (0x2A7000, 0x2B2000), (0x430000, 0x480000),
                 (0x7EF000, 0x800000)]
CODE = (0x889A8, 0xE7878)
# a table or literal hit in the middle of a string counts only here: a few real pointers skip a leading pair of words; the other
# 34 mid-string hits, printed by main(), are data that happens to look like an address. Read by hand (text.md)
MID_OK = {0x188074, 0x2AB4E4, 0x2ABE30, 0x434BFC, 0x45AE30, 0x45BBD0, 0x45BDF0, 0x45BDFE, 0x47BD40}
# stretches of the text ranges that hold tables or palettes, not strings: text.md, Not text
DATA_RUNS = [(0x45A606, 0x45A696), (0x45AABC, 0x45AE30), (0x47BF20, 0x47BF5E)]
CREDITS = (0x46F75C, 0x46FF53)  # through its FF
CREDITS_OWNERS = ["lit:0D205C"]
SPEAKERS, SPEAKERS2, TAGS, LEGENDZ = 0x184DF6, 0x184F34, 0x7F020C, 0x2B0AE0


def u16(rom, off):
    return struct.unpack_from("<H", rom, off)[0]


def good(w):
    return w <= 0x15F or 0xFFC4 <= w <= 0xFFFF


def string_at(rom, off, limit=800):
    """End offset (past the terminator) of the text-like string at off, or None."""
    for n in range(limit):
        w = u16(rom, off + n * 2)
        if w >= 0xFFFE:
            return off + n * 2 + 2
        if not good(w):
            return None
    return None


def block_of(off):
    for name, a, b in BLOCKS:
        if a <= off < b:
            return name
    return None


def starts_string(rom, off):
    """True if off follows a terminator or opens a block."""
    return any(off == a for _, a, _ in BLOCKS) or u16(rom, off - 2) >= 0xFFFE


def literal_words(rom):
    """Offsets of words read by a Thumb `ldr rX, [pc, #imm]` in the code range. Halfwords in data can pass as an ldr too, so a hit
    still has to name a string start."""
    out = set()
    for a in range(CODE[0], CODE[1], 2):
        w = u16(rom, a)
        if w >> 11 == 0b01001:
            out.add(((a + 4) & ~3) + (w & 0xFF) * 4)
    return out


def owners(rom):
    """{target offset: [owner strings]}, and the list of rejected mid-string hits."""
    found, rejected = {}, []

    def add(t, owner):
        found.setdefault(t, []).append(owner)

    instrs, _, _ = vmwalk.walk(rom)
    for site, _, op, nib, t in vmwalk.text_refs(rom, instrs):
        if block_of(t) and not t & 1:
            add(t, "op%02X:%06X%s" % (op, site, ":%X" % nib if nib else ""))

    def word(site, kind):
        v = struct.unpack_from("<I", rom, site)[0]
        t = (v & 0x0FFFFFFF) - 0x08000000
        if t & 1 or not block_of(t) or string_at(rom, t) is None:
            return
        if starts_string(rom, t) or t in MID_OK:
            add(t, "%s:%06X%s" % (kind, site, ":%X" % (v >> 28) if v >> 28 else ""))
        else:
            rejected.append((site, kind, t))

    for site in sorted(literal_words(rom)):
        word(site, "lit")
    for lo, hi in TABLE_REGIONS:
        for site in range(lo & ~3, hi - 3, 4):
            word(site, "tab")
    return found, rejected, instrs


def speakers(rom, instrs):
    """{text target: set of speaker names} from the portrait op's speaker operand, via the game's speaker tables and tag table."""
    def name(ptr):
        t = (ptr & 0x0FFFFFFF) - 0x08000000
        if not 0 <= t < len(rom) or t & 1:
            return None
        end = string_at(rom, t, 40)
        return jpcodec.decode(rom[t:end - 2]) if end else None

    table = {}
    for base, tags, stride in ((SPEAKERS, TAGS, 4), (SPEAKERS2, LEGENDZ, 8)):
        a, last = base, -1
        while a < 0x1857D8:  # ids ascend; the table stops where they don't
            who, _, actor = struct.unpack_from("<3h", rom, a)
            a += 6
            if who <= last or actor < 0:
                break
            last = who
            table[who] = name(struct.unpack_from("<I", rom, tags + actor * stride)[0])
    out = {}
    for off, op in instrs.items():
        if op == 0xDD:
            who = u16(rom, off + 2)
            t = (vmwalk.ptr_at(rom, off + 4) & 0x0FFFFFFF) - 0x08000000
            out.setdefault(t, set()).add(table.get(who) or "#%04X" % who)
        elif op == 0xBE or op == 0xCB:  # no speaker operand: the player's own lines
            t = (vmwalk.ptr_at(rom, off + 2) & 0x0FFFFFFF) - 0x08000000
            out.setdefault(t, set()).add("プレイヤー")
    return out


def entries(rom):
    """Returns (entries by block, unreferenced runs). Every word of every block ends up in one or the other: test_extract.py."""
    found, rejected, instrs = owners(rom)
    who = speakers(rom, instrs)
    blocks = {name: [] for name, _, _ in BLOCKS}
    claimed = {}
    for t in sorted(found):
        end = string_at(rom, t)
        if end is None:
            sys.exit("owned string at %06X isn't text: %s" % (t, found[t]))
        name = block_of(t)
        sprite = name in SPRITE_LAYOUT
        e = {"id": "%06X" % t, "end": "%06X" % end, "owners": found[t],
             "jp": jpcodec.decode(rom[t:end], jpcodec.SPRITE if sprite else jpcodec.TABLE), "en": "", "status": "", "notes": ""}
        if t in who:
            e["speaker"] = sorted(who[t])
        if sprite:
            e["font"] = "sprite1"
        blocks[name].append(e)
        for o in range(t, end, 2):
            claimed[o] = t
    # what's left in each block: padding, dead strings, data runs
    rest = []
    for name, a, b in BLOCKS:
        o = a
        while o < b:
            if o in claimed:
                o += 2
                continue
            data = next((r for r in DATA_RUNS if r[0] <= o < r[1]), None)
            if data:
                rest.append({"at": "%06X" % o, "end": "%06X" % min(data[1], b), "kind": "data", "block": name})
                o = min(data[1], b)
                continue
            # up to the next claimed word or terminator
            e = o
            while e < b and e not in claimed and u16(rom, e) < 0xFFFE:
                e += 2
            if e < b and e not in claimed:
                e += 2  # its terminator
            words = struct.unpack("<%dH" % ((e - o) // 2), rom[o:e])
            kind = "pad" if all(w == 0xFFFF for w in words) else "dead"
            rest.append({"at": "%06X" % o, "end": "%06X" % e, "kind": kind, "block": name, "jp": jpcodec.decode(rom[o:e])})
            o = e
    # merge padding runs
    merged = []
    for r in rest:
        if merged and r["kind"] == "pad" and merged[-1]["kind"] == "pad" and merged[-1]["end"] == r["at"]:
            merged[-1]["end"] = r["end"]
            merged[-1]["jp"] += r["jp"]
        else:
            merged.append(r)
    return blocks, merged, rejected


def credits(rom):
    a, b = CREDITS
    return [{"id": "%06X" % a, "end": "%06X" % b, "owners": CREDITS_OWNERS, "jp": jpcodec.decode8(rom[a:b]), "en": "", "status": "", "notes": "", "font": "8bit"}]


def merge(path, new):
    """Write new, keeping en/status/notes from an existing file by id. Returns the ids whose jp changed."""
    changed = []
    if path.exists():
        old = {e["id"]: e for e in json.loads(path.read_text(encoding="utf-8"))}
        for e in new:
            o = old.get(e["id"])
            if o:
                for k in ("en", "status", "notes"):
                    e[k] = o.get(k, "")
                if o["jp"] != e["jp"]:
                    changed.append(e["id"])
    path.write_text(json.dumps(new, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    return changed


def main():
    from vm_ops import rom as load
    rom = load()
    blocks, rest, rejected = entries(rom)
    OUT.mkdir(exist_ok=True)
    changed = []
    total = 0
    for name, es in blocks.items():
        if es:
            changed += merge(OUT / (name + ".json"), es)
            total += len(es)
        print("%-10s %5d strings" % (name, len(es)))
    changed += merge(OUT / "credits.json", credits(rom))
    (OUT / "unreferenced.json").write_text(json.dumps(rest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    kinds = {}
    for r in rest:
        kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
    print("total", total, "unreferenced", kinds, "rejected mid-string hits", len(rejected))
    for site, kind, t in rejected:
        print("  rejected %s %06X -> %06X %s" % (kind, site, t, jpcodec.decode(rom[t:t + 24]).replace("\n", "/")))
    if changed:
        print("jp changed, re-queue these translations:", changed)


if __name__ == "__main__":
    main()
