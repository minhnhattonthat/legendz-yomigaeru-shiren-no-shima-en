"""Story-pass input (references/translation.md, Review): the dialogue block cut into chapters in story order, from docs/synopsis.md's ranges.

    python -X utf8 tools/chapters.py [OUT_DIR]   # default work/qa/story/chapters; one `NN_name.txt` a chapter, `>> id | speaker | JP` / `EN`

A chapter over PART lines is split into parts so one reviewer can read it whole. Lines outside every range go to `99_other`.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import batches  # noqa: E402

# (name, [(first, end)...]) in story order; end exclusive. From docs/synopsis.md, Story.
CHAPTERS = [
    ("01_ship", [(0x180F1C, 0x182188), (0x17F6D8, 0x17FAD8)]),
    ("02_hidden_event", [(0x17E912, 0x17F696)]),
    ("03_live_rpg", [(0x17FF58, 0x180B0C), (0x1619DC, 0x1642B0)]),
    ("04_stages", [(0x1642B0, 0x1747D0)]),
    ("05_tournament", [(0x174850, 0x17AC36)]),
    ("06_tiamat", [(0x17AF9C, 0x17E912)]),
    ("07_ending", [(0x182F5E, 0x184898)]),
]
PART = 400


def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "work/qa/story/chapters")
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.txt"):
        old.unlink()
    lines = batches.load_blocks()["dialogue"]
    used = set()

    def row(e):
        speaker = ",".join(e.get("speaker") or []) if isinstance(e.get("speaker"), list) else ""
        return ">> %s | %s | %s\n   %s" % (e["id"], speaker, batches.show(e["jp"]), batches.show(e["en"]))

    def write(name, picked):
        size = -(-len(picked) // max(1, -(-len(picked) // PART)))  # even parts of at most PART
        parts = [picked[i:i + size] for i in range(0, len(picked), size)] or [[]]
        for n, part in enumerate(parts, 1):
            stem = name if len(parts) == 1 else "%s_%d" % (name, n)
            (out / (stem + ".txt")).write_text("\n".join(row(e) for e in part) + "\n", encoding="utf-8", newline="\n")
            print(stem, len(part))

    for name, spans in CHAPTERS:
        picked = [e for a, z in spans for e in lines if a <= int(e["id"], 16) < z]
        used.update(e["id"] for e in picked)
        write(name, picked)
    write("99_other", [e for e in lines if e["id"] not in used])


if __name__ == "__main__":
    main()
