"""Decode the game's 16-bit text stream with the original font's code order (see docs/re/text.md). Stream words: font index, or
FFxx control. Unknown words decode as [XXXX] so a dump roundtrips."""
import re
import struct

HIRA = "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんがぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽぁぃぅぇぉっゃゅょゎ"
KATA = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲンヴガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポァィゥェォッャュョヮ"
LATIN = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
SYMS = "$、。ー～…！？‼「」0123456789・●◎％＋－♪『』：☺♥✓★◆♨✖♫🐰🐱《》＇＂／¦\"•（）"
# 00F1-013C: kanji cells of the battle sprite font (tools/spritefont.py), read off its sheet. Blank in the dialogue font.
KANJI = "出現回復自爆属性効果大悪眠覚解混乱治毒受抜石化打撃技封印魔法全状態異常瀕死敵逃倒達減新入手変火風水土光闇力防御至高恵率命中素早攻特無道具使動勝利追加行段"
# sprite font 1 and up (quips, text.md) order their symbols differently from BE up
SPRITE_SYMS = "0123456789、。ー～…！？‼⁉$「」・○％＋－♪★"

TABLE = {0: "　"}
for i, c in enumerate(HIRA):
    TABLE[1 + i] = c
for i, c in enumerate(KATA):
    TABLE[0x52 + i] = c
for i, c in enumerate(LATIN):
    TABLE[0xA4 + i] = c
SPRITE = dict(TABLE)
for i, c in enumerate(SYMS):
    TABLE[0xBE + i] = c
for i, c in enumerate(SPRITE_SYMS):
    SPRITE[0xBE + i] = c
assert len(KANJI) == 0x13D - 0xF1
TABLE.update(zip(range(0xF1, 0x13D), KANJI))
CTRL = {0xFFFF: "<end>", 0xFFFE: "<page>\n", 0xFFFD: "<br>\n", 0xFFFB: "<flag4>"}
REV = {v: k for k, v in TABLE.items()}
REV.update({v: k for k, v in CTRL.items()})
SPRITE_REV = {v: k for k, v in SPRITE.items()}
SPRITE_REV.update({v: k for k, v in CTRL.items()})
_token = re.compile(r"\[[0-9A-F]{4}\]|<[a-z0-9]+>\n?|.", re.S)


def decode_words(words, table=TABLE):
    return "".join(CTRL.get(w) or table.get(w) or "[%04X]" % w for w in words)


def decode(data, table=TABLE):
    return decode_words(struct.unpack("<%dH" % (len(data) // 2), data), table)


def encode(text, rev=REV):
    out = []
    for t in _token.findall(text):
        if t.startswith("[") and len(t) == 6:
            out.append(int(t[1:5], 16))
        else:
            out.append(rev[t])
    return struct.pack("<%dH" % len(out), *out)


def decode8(data):
    """Credits: one byte a glyph, F1 x colour, F2 x picture, F3 next page, FD newline, FF end (text.md). Unknown bytes: [XX]."""
    return "".join((TABLE.get(b) if b < 0xF1 else None) or ("[FD]\n" if b == 0xFD else "[%02X]" % b) for b in data)


def encode8(text):
    return bytes(int(t[1:3], 16) if t.startswith("[") else REV[t] for t in re.findall(r"\[[0-9A-F]{2}\]|[^\n]", text))


def is_kana(w):
    return 1 <= w <= 0xA3


if __name__ == "__main__":
    assert len(HIRA) == 0x51 and len(KATA) == 0x52, (len(HIRA), len(KATA))
    assert len(set(TABLE.values())) == len(TABLE), "duplicate glyph value"
    assert TABLE[0xC3] == "…" and TABLE[0xC4] == "！" and TABLE[0xC1] == "ー" and TABLE[0xEF] == "（" and TABLE[0xF0] == "）", (TABLE[0xC3], TABLE[0xC4], TABLE[0xC1], TABLE[0xEF], TABLE[0xF0])
    s = struct.pack("<8H", 1, 0xC3, 0xFFFD, 0x1234, 0xA4, 0xFFFE, 0, 0xFFFF)
    assert encode(decode(s)) == s, decode(s)
    print("ok", decode(s).replace("\n", "|"))
