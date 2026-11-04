"""Decode the game's 16-bit text stream with the original font's code order (see docs/re/text.md). Stream words: font index, or
FFxx control. Unknown words decode as [XXXX] so a dump roundtrips."""
import re
import struct

HIRA = "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんがぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽぁぃぅぇぉっゃゅょゎ"
KATA = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲンヴガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポァィゥェォッャュョヮ"
LATIN = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
SYMS = "$、。ー～…！？‼「」0123456789・●◎％＋－♪『』：☺♥✓★◆♨✖♫🐰🐱《》＇＂／¦\"•（）"

TABLE = {0: "　"}
for i, c in enumerate(HIRA):
    TABLE[1 + i] = c
for i, c in enumerate(KATA):
    TABLE[0x52 + i] = c
for i, c in enumerate(LATIN):
    TABLE[0xA4 + i] = c
for i, c in enumerate(SYMS):
    TABLE[0xBE + i] = c
CTRL = {0xFFFF: "<end>", 0xFFFE: "<page>\n", 0xFFFD: "<br>\n", 0xFFFB: "<flag4>"}
REV = {v: k for k, v in TABLE.items()}
REV.update({v: k for k, v in CTRL.items()})
_token = re.compile(r"\[[0-9A-F]{4}\]|<[a-z0-9]+>\n?|.", re.S)


def decode_words(words):
    return "".join(CTRL.get(w) or TABLE.get(w) or "[%04X]" % w for w in words)


def decode(data):
    return decode_words(struct.unpack("<%dH" % (len(data) // 2), data))


def encode(text):
    out = []
    for t in _token.findall(text):
        if t.startswith("[") and len(t) == 6:
            out.append(int(t[1:5], 16))
        else:
            out.append(REV[t])
    return struct.pack("<%dH" % len(out), *out)


def is_kana(w):
    return 1 <= w <= 0xA3


if __name__ == "__main__":
    assert len(HIRA) == 0x51 and len(KATA) == 0x52, (len(HIRA), len(KATA))
    assert len(set(TABLE.values())) == len(TABLE), "duplicate glyph value"
    assert TABLE[0xC3] == "…" and TABLE[0xC4] == "！" and TABLE[0xC1] == "ー" and TABLE[0xEF] == "（" and TABLE[0xF0] == "）", (TABLE[0xC3], TABLE[0xC4], TABLE[0xC1], TABLE[0xEF], TABLE[0xF0])
    s = struct.pack("<8H", 1, 0xC3, 0xFFFD, 0x1234, 0xA4, 0xFFFE, 0, 0xFFFF)
    assert encode(decode(s)) == s, decode(s)
    print("ok", decode(s).replace("\n", "|"))
