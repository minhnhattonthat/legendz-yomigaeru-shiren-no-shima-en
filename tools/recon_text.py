"""Recon (phase 1): list text streams and what points at them; output under work/recon/. Pointers are read with the top nibble
masked (the script VM does `& 0x0FFFFFFF`). Promoted to the real extractor in phase 4."""
import collections
import os
import struct
import sys

from jpcodec import decode_words

ROM = "rom/Legions - Yomigaeru Shiren no Shima (Japan).gba"
OUT = "work/recon"


def streams(words, lo=0, hi=None, minlen=2):
    """Maximal runs of plausible text words ending in FFFE/FFFF; yield (byte_off, word_count)."""
    hi = hi or len(words)
    start = lo
    good = lambda w: w <= 0xF0 or (0xFFC0 <= w <= 0xFFFD)
    for i in range(lo, hi):
        w = words[i]
        if w in (0xFFFE, 0xFFFF):
            if i - start + 1 >= minlen:
                yield start * 2, i - start + 1
            start = i + 1
        elif not good(w):
            start = i + 1


def main():
    d = open(ROM, "rb").read()
    words = struct.unpack("<%dH" % (len(d) // 2), d)
    os.makedirs(OUT, exist_ok=True)
    msgs = list(streams(words))
    print("candidate streams", len(msgs))
    index = {o: n for o, n in msgs}
    refs = collections.defaultdict(list)
    for a in range(0, len(d) - 4, 2):
        v = words[a // 2] | words[a // 2 + 1] << 16
        if v & 0x0F000000 == 0x08000000:
            o = v & 0x00FFFFFF
            if o in index:
                refs[o].append((a, v >> 28))
    flags = collections.Counter(f for r in refs.values() for _, f in r)
    print("streams with a reference", len(refs), "refs", sum(len(r) for r in refs.values()), "flag nibbles", sorted(flags.items()))
    with open(OUT + "/streams.tsv", "w", encoding="utf-8", newline="\n") as f:
        for o, n in msgs:
            r = refs.get(o, [])
            txt = decode_words(words[o // 2:o // 2 + n]).replace("\n", "")
            f.write("%06X\t%d\t%s\t%s\n" % (o, n, ",".join("%06X" % a for a, _ in r[:6]), txt))
    # clusters of referenced text
    ref_sorted = sorted(refs)
    spans = []
    for o in ref_sorted:
        if spans and o - spans[-1][1] < 0x400:
            spans[-1][1] = o + index[o] * 2
            spans[-1][2] += 1
        else:
            spans.append([o, o + index[o] * 2, 1])
    with open(OUT + "/spans.txt", "w", encoding="utf-8", newline="\n") as f:
        for lo, hi, n in spans:
            f.write("%06X %06X %d\n" % (lo, hi, n))
    print("spans", len(spans), [(hex(a), hex(b), c) for a, b, c in spans if c >= 8])
    regions = collections.Counter()
    for r in refs.values():
        for a, _ in r:
            regions[a >> 16] += 1
    print("ref sites", sorted((hex(k << 16), v) for k, v in regions.items()))


if __name__ == "__main__":
    sys.exit(main())
