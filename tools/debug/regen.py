"""Run every scene in tools/debug/scenes.lua from a cold boot, keep a shot and a savestate of each, and write one proof sheet per page.
Exit 1 if any scene didn't log REACHED or its final frame is blank.

    python -X utf8 tools/debug/regen.py [--rom build/legendz_en.gba] [--only a,b] [--jobs 4]

Output: work/qa/scenes/<name>/ (run), work/states/<name>.mss, work/qa/scenes/proof*.png, work/qa/scenes/report.tsv.
"""
import argparse
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402

ROM = next(l for l in (ROOT / "rom.sha1").read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")).split("  ", 1)[1]


def scenes():
    """name -> frames, from scenes.lua's own text (Lua is not available here)."""
    text = (ROOT / "tools/debug/scenes.lua").read_text(encoding="utf-8")
    default = int(re.search(r"^local F = (\d+)", text, re.M)[1])
    out = {}
    for name, body in re.findall(r"^  (\w+) = \{(.*)$", text, re.M):
        m = re.search(r"frames = (\w+)", body)
        out[name] = default if not m or m[1] == "F" else int(m[1])
    return out


def run(rom, name, frames):
    out = ROOT / "work/qa/scenes" / name
    state = ROOT / "work/states" / (name + ".mss")
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts/emu.py"), rom, "--out", str(out), "--script", "tools/debug/warp.lua",
           "--var", "SCENE='%s'" % name, "--frames", str(frames), "--shot-every", str(max(frames // 12, 60)), "--state-out", str(state),
           "--sheet", "--timeout", "280"]
    with open(ROOT / "work/qa/scenes" / (name + ".log"), "w", encoding="utf-8") as f:
        code = subprocess.call(cmd, cwd=ROOT, stdout=f, stderr=subprocess.STDOUT)
    log = (out / "log.txt").read_text(encoding="utf-8", errors="replace") if (out / "log.txt").exists() else ""
    reached = "REACHED " + name in log
    final = out / "final.png"
    sys.path.insert(0, str(Path(SKILL) / "scripts"))
    import sheet
    blank = not final.exists() or sheet.is_blank(sheet.read_png(str(final)))
    return name, code, reached, blank


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rom", default=ROM)
    ap.add_argument("--only", default="")
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    (ROOT / "work/qa/scenes").mkdir(parents=True, exist_ok=True)
    table = scenes()
    if a.only:
        table = {k: table[k] for k in a.only.split(",")}
    with ThreadPoolExecutor(a.jobs) as pool:
        results = list(pool.map(lambda kv: run(a.rom, kv[0], kv[1]), table.items()))
    rows, bad = ["name\texit\treached\tblank"], 0
    for name, code, reached, blank in results:
        rows.append("%s\t%d\t%s\t%s" % (name, code, reached, blank))
        ok = code == 0 and reached and not blank
        bad += not ok
        print(("ok  " if ok else "FAIL"), name, "exit", code, "reached", reached, "blank", blank)
    (ROOT / "work/qa/scenes/report.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    finals = [str(ROOT / "work/qa/scenes" / n / "final.png") for n in table]
    subprocess.call([sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts/sheet.py"), *finals, "--out", str(ROOT / "work/qa/scenes/proof.png")], cwd=ROOT)
    print(len(results) - bad, "of", len(results), "ok")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
