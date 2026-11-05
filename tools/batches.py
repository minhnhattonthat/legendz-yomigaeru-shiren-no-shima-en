"""Translation batches: script/*.json -> work/tl/bNNN.tsv -> checked work/tl/bNNN.out.tsv -> back into script/*.json (references/translation.md).

    python -X utf8 tools/batches.py split              # refuses to run if work/tl has batches
    python -X utf8 tools/batches.py check b001 [b002]  # 0 errors prints OK; exit 1 otherwise
    python -X utf8 tools/batches.py merge b001 [b002]  # refuses a batch that fails check
    python -X utf8 tools/batches.py status             # per block: translated, left; multi-page lines for phase 7
    python -X utf8 tools/batches.py lint               # check every merged string (run after glossary changes)
    python -X utf8 tools/batches.py fit "text / text" [--px 156]

Input line: id, speaker, limit (156x2 = px x rows), flags (* = op 0116, one of 4 personality lines), Japanese. ` / ` is a row break, ` // ` a new page (phase 7 builds
those: vwf.md, Longer than two lines). Output line: id, English. The terminator comes from the Japanese. Identical Japanese is one entry, written to every copy.
"""
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import font_en  # noqa: E402
import insert  # noqa: E402
import jpcodec  # noqa: E402

TL = ROOT / "work" / "tl"
# translated order: names and terms first, so the story batches can use them
ORDER = ["legendz", "places", "items", "skills", "skills2", "skills3", "cards", "menus", "rental", "link", "dialogue", "system", "battle", "adventure", "quips"]
BATCH_CHARS = 5000
SPRITE_WORDS = 21  # the OBJ ring: vwf.md, Sprite font
BUILDER_WORDS = 68  # 0x02036890: vwf.md, Limits
# (px, words) a variable expands to, at worst: docs/re/text.md, Variables
VARS = {}
for codes, px, words in (
    (("FFC4",), 30, 5), (("FFC5", "FFEA", "FFC7", "FFC8", "FFC9", "FFCA"), 80, 9), (("FFC6", "FFE3", "FFE5", "FFEB", "FFEC", "FFF0", "FFF1", "FFF2"), 64, 9),
    (("FFD9", "FFE2"), 40, 5), (("FFE1", "FFE8", "FFE9"), 18, 3), (("FFE7", "FFEF", "FFED"), 64, 9), (("FFEE",), 36, 6),
):
    VARS.update(dict.fromkeys(codes, (px, words)))
DEFAULT_VAR = (12, 2)  # the 2-digit record fields
YES_NO = " /          Yes    No"  # はい at 40 px, いいえ at 72 px in the Japanese row: 4 px spaces put them where the cursor goes (seen in QA, phase 8)
VAR = re.compile(r"\[(FF[0-9A-F]{2})\]")
ORDINAL = re.compile(r"\[FF[0-9A-F]{2}\](st|nd|rd|th)\b")
ARTICLE = re.compile(r"\b(a|an|A|An) \[FF[0-9A-F]{2}\]")


_widths = None


def widths():
    global _widths
    if _widths is None:
        _widths = font_en.dialogue_fonts(next((ROOT / "rom").glob("*.gba")).read_bytes())[1]
    return _widths


def load_blocks():
    return {b: json.loads((ROOT / "script" / (b + ".json")).read_text(encoding="utf-8")) for b in ORDER}


def budgets():
    out = {}
    for line in (ROOT / "script/windows.tsv").read_text(encoding="utf-8").splitlines()[1:]:
        i, px, rows, source, _ = line.split("\t")
        out[i] = int(px), int(rows), source
    # boxes English needs wider than the Japanese had: phase 7 raises them in the engine (D4). id, px, where.
    for line in (ROOT / "script/widen.tsv").read_text(encoding="utf-8").splitlines():
        i, px, _ = line.split("\t", 2)
        out[i] = int(px), out[i][1], "widen"
    return out


def show(jp):
    """The JSON's form -> one line: ' / ' row, ' // ' page, no terminator."""
    t = jp.replace("<br>\n", " / ").replace("<br>", " / ").replace("<page>\n", " // ").replace("<page>", " // ").replace("<end>", "")
    return t[:-4] if t.endswith(" // ") else t


def terminator(jp):
    return "<page>\n" if jp.endswith("<page>\n") else "<page>" if jp.endswith("<page>") else "<end>"


def store(en, jp):
    """One output line -> the JSON's form, same control text the extractor writes."""
    return en.replace(" // ", "<page>\n").replace(" / ", "<br>\n") + terminator(jp)


def groups(blocks):
    """{jp: [(block, entry)]}, in ORDER, without strings that aren't text."""
    out = {}
    for b in ORDER:
        for e in blocks[b]:
            if not insert.non_text(e):
                out.setdefault(e["jp"], []).append((b, e))
    return out


def limit(copies, bud):
    """(px, rows, known): the tightest box among a string's copies, guesses only if there's nothing else. A Japanese layout with more rows than a class's has that many."""
    rows_of = [bud[e["id"]] for _, e in copies]
    if any(r[2] == "widen" for r in rows_of):
        rows_of = [r for r in rows_of if r[2] == "widen"]  # one row in widen.tsv speaks for every copy of the string
    known = [r for r in rows_of if r[2] != "guess"]
    use = known or rows_of
    rows = min(r[1] for r in use)
    if not any(r[2] == "measured" for r in use):
        rows = max(rows, show(copies[0][1]["jp"]).count(" / ") + 1)
    return min(r[0] for r in use), rows, bool(known)


def split():
    TL.mkdir(parents=True, exist_ok=True)
    if list(TL.glob("b*.tsv")):
        raise SystemExit("work/tl already has batches: refusing to overwrite")
    bud = budgets()
    n, size, cur, last = 1, 0, [], None

    def flush():
        nonlocal n, size, cur
        if cur:
            (TL / ("b%03d.tsv" % n)).write_text("\n".join(cur) + "\n", encoding="utf-8", newline="\n")
            n, size, cur = n + 1, 0, []

    for jp, copies in groups(load_blocks()).items():
        b, e = copies[0]
        if size > BATCH_CHARS or (last and last != b and size > BATCH_CHARS / 3):
            flush()
        last = b
        px, rows, _ = limit(copies, bud)
        speaker = ",".join(e.get("speaker") or []) if isinstance(e.get("speaker"), list) else ""
        flags = "*" if any(o.startswith("op116") for o in e["owners"]) else ""
        cur.append("\t".join((e["id"], speaker, "%dx%d" % (px, rows), flags, show(jp))))
        size += len(show(jp))
    flush()
    print("batches:", n - 1)


def words(text):
    """Words after pairing, with each variable's worst case."""
    pairs = {}
    data = font_en.encode(re.sub(VAR, "", text), pairs)
    return len(data) // 2 + sum(VARS.get(v, DEFAULT_VAR)[1] for v in VAR.findall(text))


def row_px(row, w, sprite):
    px = 0
    for t in font_en._token.findall(row):
        if len(t) == 6:
            px += VARS.get(t[1:5], DEFAULT_VAR)[0]
        elif t in font_en.KEEP:
            px += 8
        elif sprite:
            px += font_en.SPACE if t == " " else font_en.art_width(t) + 2
        else:
            px += w[font_en.CODES[t]]
    return px


def wrap(en, px, w, sprite):
    """Author sentences, generate rows: a page with no ` / ` of its own wraps greedily at spaces to px. The typewriter can't wrap by itself (vwf.md)."""
    pages = []
    for page in en.split(" // "):
        if " / " not in page and row_px(page, w, sprite) > px:
            rows, cur = [], ""
            for word in page.split(" "):
                if cur and row_px(cur + " " + word, w, sprite) > px:
                    rows.append(cur)
                    cur = word
                else:
                    cur = cur + " " + word if cur else word
            page = " / ".join(rows + [cur])
        pages.append(page)
    return " // ".join(pages)


def problems(en, copies, bud, w):
    """Everything wrong with one English line for these copies, as strings."""
    jp = copies[0][1]["jp"]
    out = []
    if not en.strip():
        return ["empty"]
    bad = [c for c in font_en._token.findall(en.replace(" // ", "").replace(" / ", "")) if len(c) != 6 and c not in font_en.CODES and c not in font_en.KEEP]
    if bad:
        return ["unencodable %r" % "".join(bad)]
    if sorted(VAR.findall(jp)) != sorted(VAR.findall(en)):
        out.append("variables differ: %s vs %s" % (sorted(VAR.findall(jp)), sorted(VAR.findall(en))))
    if ORDINAL.search(en) or ARTICLE.search(en):
        out.append("suffix or article on a variable")
    if jp.startswith("●") != en.startswith("●"):
        out.append("label bead")
    if "  " in en and "　　" not in jp and not re.search(r"(^|\n)　", jp) and copies[0][1]["id"] not in insert.SINGLE_WORDS:  # a Japanese row that starts on a blank is a choice row, spaced on purpose; the name grid's blanks are cells
        out.append("double space")
    px, rows, known = limit(copies, bud)
    blocks = {b for b, _ in copies}
    sprite = bool(blocks & insert.SPRITE_BLOCKS)
    if rows > 1:
        en = wrap(en, px, w, sprite)
    for page in en.split(" // "):
        rs = page.split(" / ")
        if len(rs) > rows and known:
            out.append("%d rows, budget %d" % (len(rs), rows))
        for r in rs:
            if row_px(r, w, sprite) > px and known:  # over a guess means measure it, not shorten it: vwf.md, Width gate
                out.append("%dpx > %dpx: %s" % (row_px(r, w, sprite), px, r))
        n = words(page.replace(" / ", "<br>"))
        if sprite and "battle" in blocks and n > SPRITE_WORDS:
            out.append("%d words, sprite ring holds %d" % (n, SPRITE_WORDS))
        elif n > BUILDER_WORDS:
            out.append("%d words, builder buffer holds %d" % (n, BUILDER_WORDS))
    if " // " in en and not any(o.split(":")[0] in ("opDD", "opBE", "op33") for _, e in copies for o in e["owners"]):
        out.append("a second page needs a script line op: this one can't take it")
    if blocks & insert.NAME_SLOTS:
        # a Legendz or spot name's slot is 8 words + terminator (report mode, FFE7); a speaker's is the enemy name (JP up to 7), so 6 is safe for every tag: vwf.md, Limits
        cap = max(len(jpcodec._token.findall(jp.replace("<end>", "").replace("<page>\n", ""))), 6 if "places" in blocks and int(copies[0][1]["id"], 16) >= 0x188C56 else 8)
        if words(en) > cap:
            out.append("%d words, name slot holds %d" % (words(en), cap))
    return out + glossary_problems(jp, en)


def glossary():
    """(jp, en, [avoid]) from glossary.md's tables. A row with a bare `-` in the EN column is advice, not enforced."""
    rows = []
    for line in (ROOT / "glossary.md").read_text(encoding="utf-8").splitlines():
        p = [c.strip() for c in line.split("|")]
        if len(p) >= 7 and p[1] not in ("JP", "---") and p[2]:
            rows.append((p[1], p[2], [a.strip() for a in p[5].split(",") if a.strip()]))
    return rows


GLOSSARY = None


def glossary_problems(jp, en):
    global GLOSSARY
    if GLOSSARY is None:
        GLOSSARY = glossary()
    out = []
    for term, want, avoid in GLOSSARY:
        for a in avoid:
            if re.search(r"\b%s\b" % re.escape(a), en):
                out.append("avoid %r, use %r" % (a, want))
        # whole katakana runs only: ミン inside タイミング must not count
        if re.fullmatch(r"[ァ-ヶー・]+", term) and want != "-" and re.search(r"(?<![ァ-ヶー])%s(?![ァ-ヶー])" % term, jp) and want.lower() not in en.lower():
            out.append("%s should be %r" % (term, want))
    return out


def read_out(batch):
    out = {}
    for n, line in enumerate((TL / (batch + ".out.tsv")).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        if "\t" not in line:
            raise SystemExit("%s.out.tsv line %d: no tab" % (batch, n))
        i, en = line.split("\t", 1)
        if i in out:
            raise SystemExit("%s.out.tsv: %s twice" % (batch, i))
        out[i] = pads(en.replace("{yn}", YES_NO))
    return out


def pads(en):
    """{@N}: spaces up to N px on this row, for choice rows whose cursor stops sit at the Japanese columns."""
    w = widths()
    rows = en.split(" / ")
    for n, row in enumerate(rows):
        while "{@" in row:
            head, tail = row.split("{@", 1)
            at, tail = tail.split("}", 1)
            row = head + " " * max(1, (int(at) - row_px(head, w, False) + 3) // 4) + tail
        rows[n] = row
    return " / ".join(rows)


def check(batch, blocks=None, bud=None, w=None):
    blocks, bud, w = blocks or load_blocks(), bud or budgets(), w or widths()
    want = [line.split("\t")[0] for line in (TL / (batch + ".tsv")).read_text(encoding="utf-8").splitlines()]
    out = read_out(batch)
    errs = ["missing " + i for i in want if i not in out] + ["extra " + i for i in out if i not in want]
    by_id = {copies[0][1]["id"]: copies for copies in groups(blocks).values()}
    for i, en in out.items():
        if i in by_id:
            errs += ["%s: %s" % (i, p) for p in problems(en, by_id[i], bud, w)]
    return errs


def merge(batch, blocks):
    by_id = {copies[0][1]["id"]: copies for copies in groups(blocks).values()}
    bud, w = budgets(), widths()
    for i, en in read_out(batch).items():
        px, rows, _ = limit(by_id[i], bud)
        if rows > 1:
            en = wrap(en, px, w, bool({b for b, _ in by_id[i]} & insert.SPRITE_BLOCKS))
        for _, e in by_id[i]:
            e["en"], e["status"] = store(en, e["jp"]), "tl"


def save(blocks):
    for b, entries in blocks.items():
        (ROOT / "script" / (b + ".json")).write_text(json.dumps(entries, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")


def status(blocks):
    for b, entries in blocks.items():
        text = [e for e in entries if not insert.non_text(e)]
        print("%-10s %4d of %4d" % (b, sum(1 for e in text if e["en"]), len(text)))
    long = [e["id"] for es in blocks.values() for e in es if e["en"].count("<page>") > e["jp"].count("<page>")]
    print("second pages for phase 7:", len(long), " ".join(long))


def lint(blocks, bud, w):
    errs = []
    for jp, copies in groups(blocks).items():
        en = copies[0][1]["en"]
        if en:
            errs += ["%s: %s" % (copies[0][1]["id"], p) for p in problems(show(en), copies, bud, w)]
    return errs


def main():
    a = sys.argv[1:]
    if not a:
        raise SystemExit(__doc__)
    if a[0] == "split":
        split()
    elif a[0] == "fit":
        w = widths()
        px = int(a[a.index("--px") + 1]) if "--px" in a else 156
        for r in a[1].split(" / "):
            print(row_px(r, w, False), "/", px, r)
    elif a[0] in ("check", "merge"):
        blocks, bud, w = load_blocks(), budgets(), widths()
        bad = 0
        for b in a[1:]:
            errs = check(b, blocks, bud, w)
            for e in errs:
                print(b, e)
            bad += len(errs)
            if not errs and a[0] == "merge":
                merge(b, blocks)
        if a[0] == "merge" and not bad:
            save(blocks)
        print("OK" if not bad else "%d errors" % bad)
        sys.exit(1 if bad else 0)
    elif a[0] == "status":
        status(load_blocks())
    elif a[0] == "lint":
        errs = lint(load_blocks(), budgets(), widths())
        print("\n".join(errs) or "OK")
        sys.exit(1 if errs else 0)
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
