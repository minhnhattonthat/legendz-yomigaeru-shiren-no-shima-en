"""Leftover Japanese on the built ROM: jp_left.py over every pointer slot the build wrote (build/writes.txt), with the project's 16-bit table.

    python -X utf8 tools/jp_check.py [build/legendz_en.gba]

Writes work/jp_le16.tbl and build/slots.txt. Strings that stay on purpose (insert.non_text) hold no kana. Exit 1 if any Japanese is left.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import jpcodec  # noqa: E402
from skill import SKILL  # noqa: E402


def main():
    rom = sys.argv[1] if len(sys.argv) > 1 else "build/legendz_en.gba"
    tbl = ROOT / "work/jp_le16.tbl"
    tbl.write_text("".join("%04X=%s\n" % (c, t) for c, t in jpcodec.TABLE.items() if 1 <= c <= 0xA3), encoding="utf-8", newline="\n")
    slots = ROOT / "build/slots.txt"
    rows = [line.split(" ")[0] for line in (ROOT / "build/writes.txt").read_text(encoding="utf-8").splitlines() if line.split(" ")[3] == "ptr"]
    slots.write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
    sys.exit(subprocess.call([sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts/jp_left.py"), rom, "--tbl", str(tbl), "--le16", "--slots", str(slots)], cwd=ROOT))


if __name__ == "__main__":
    main()
