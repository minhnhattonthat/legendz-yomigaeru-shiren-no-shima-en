"""Tick lines of docs/polish.md from a file of `L<line><TAB>note` (line numbers as `polish_view.py` prints them).

    python -X utf8 tools/polish_tick.py work/polish/ticks1.tsv

Each named line goes from `- [ ]` to `- [x]` with ` - <note>` appended (`fixed`, `waived: reason`, ...).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLISH = ROOT / "docs/polish.md"


def main():
    lines = POLISH.read_text(encoding="utf-8").split("\n")
    for row in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines():
        if not row.strip():
            continue
        tag, note = row.split("\t", 1)
        n = int(tag.lstrip("L")) - 1
        if not lines[n].startswith("- [ ]"):
            raise SystemExit("line %d is not an unticked item: %s" % (n + 1, lines[n][:60]))
        lines[n] = "- [x]" + lines[n][5:] + " - **" + note + "**"
    POLISH.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print("%d left" % sum(line.startswith("- [ ]") for line in lines))


if __name__ == "__main__":
    main()
