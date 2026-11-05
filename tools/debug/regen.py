"""Run every scene in tools/debug/scenes.lua from a cold boot, keep a shot and a savestate of each, and write one proof sheet per page.
Exit 1 if any scene didn't log REACHED or its final frame is blank.

    python -X utf8 tools/debug/regen.py [--rom build/legendz_en.gba] [--only a,b] [--jobs 4]

Output: work/qa/scenes/<name>/ (run), work/states/<name>.mss, work/qa/scenes/proof*.png, work/qa/scenes/report.tsv,
work/saves/<name>.sav (what a `save = true` scene wrote; a `sav = "name"` scene boots with it).
"""
import argparse
import ctypes
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402

SAVE_FIXTURES = ROOT / "work/saves"
DEFAULT_QA = ROOT / "work/qa/scenes"
QA = DEFAULT_QA
EXTRA_LUA = []
TIMEOUT = 280
RESUME = False
MIN_FREE = 0.0  # GB: under this a running scene stops, and runs again once there is 1 GB more
MEMORY_WAIT = 3 * 3600
ROM_NAME = ""

ROM = next(l for l in (ROOT / "rom.sha1").read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")).split("  ", 1)[1]


def scenes():
    """name -> (frames, shot spacing), from scenes.lua's own text (Lua is not available here)."""
    text = (ROOT / "tools/debug/scenes.lua").read_text(encoding="utf-8")
    default = int(re.search(r"^local F = (\d+)", text, re.M)[1])
    out = {}
    for name, body in re.findall(r"^  (\w+) = \{(.*)$", text, re.M):
        m = re.search(r"frames = (\w+)", body)
        frames = default if not m or m[1] == "F" else int(m[1])
        every = re.search(r"every = (\d+)", body)
        sav = re.search(r'sav = "(\w+)"', body)
        out[name] = (frames, int(every[1]) if every else max(frames // 12, 60), "save = true" in body, sav[1] if sav else None)
    return out


def free_gb():
    class Status(ctypes.Structure):
        _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong), ("total", ctypes.c_ulonglong), ("avail", ctypes.c_ulonglong),
                    ("pagefile", ctypes.c_ulonglong), ("availfile", ctypes.c_ulonglong), ("virt", ctypes.c_ulonglong), ("availvirt", ctypes.c_ulonglong), ("ext", ctypes.c_ulonglong)]
    s = Status()
    s.length = ctypes.sizeof(s)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(s))
    return s.avail / 2**30


def wait_for_memory(gb):
    """Hold the next scene until the machine has room; give up rather than wait all day."""
    deadline = time.time() + MEMORY_WAIT
    while free_gb() < gb:
        if time.time() > deadline:
            sys.exit("under %.1f GB free for %d s: stopped; rerun with --resume" % (gb, MEMORY_WAIT))
        time.sleep(30)


def run(rom, name, frames, every, saves=False, sav=None):
    out = QA / name
    state = (ROOT / "work/states" if QA == DEFAULT_QA else QA) / (name + ".mss")
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts/emu.py"), rom, "--out", str(out), "--script", "tools/debug/warp.lua",
           "--var", "SCENE='%s'" % name, "--frames", str(frames), "--shot-every", str(every), "--state-out", str(state),
           "--sheet", "--timeout", str(TIMEOUT)]
    if sav:
        cmd += ["--sav", str(SAVE_FIXTURES / (sav + ".sav"))]
    for lua in EXTRA_LUA:
        cmd += ["--script", lua]
    if RESUME and finished(name):
        return result(name, 0)
    while True:
        wait_for_memory(MIN_FREE + 1)
        with open(QA / (name + ".log"), "w", encoding="utf-8") as f:
            proc = subprocess.Popen(cmd, cwd=ROOT, stdout=f, stderr=subprocess.STDOUT)
            while proc.poll() is None and free_gb() >= MIN_FREE:
                time.sleep(5)
            if proc.poll() is not None:
                return result(name, proc.returncode)
            print("low memory: %.1f GB free, stopping %s to run it again" % (free_gb(), name), flush=True)
            subprocess.call(["taskkill", "/PID", str(proc.pid), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            proc.wait()
        if saves:  # the stopped run may have left its save, and a cold boot must not see one
            (ROOT / "tools/mesen/Saves" / (Path(ROM_NAME).stem + ".sav")).unlink(missing_ok=True)


def finished(name):
    """A scene an earlier, stopped run already got through."""
    log = QA / name / "log.txt"
    return (QA / name / "final.png").exists() and log.exists() and "REACHED " + name in log.read_text(encoding="utf-8", errors="replace")


def result(name, code):
    out = QA / name
    log = (out / "log.txt").read_text(encoding="utf-8", errors="replace") if (out / "log.txt").exists() else ""
    reached = "REACHED " + name in log
    final = out / "final.png"
    sys.path.insert(0, str(Path(SKILL) / "scripts"))
    import sheet
    blank = not final.exists() or sheet.is_blank(sheet.read_png(str(final)))
    return name, code, reached, blank


def main():
    global QA, TIMEOUT, RESUME, MIN_FREE, ROM_NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--rom", default=ROM)
    ap.add_argument("--only", default="")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--out", default=str(DEFAULT_QA), help="output folder; away from the default, states go there too")
    ap.add_argument("--lua", action="append", default=[], help="extra --script for every run, e.g. tools/lua/textlog.lua")
    ap.add_argument("--timeout", type=int, default=TIMEOUT, help="seconds per scene; exec hooks (--lua) slow the long scenes past the default")
    ap.add_argument("--resume", action="store_true", help="skip scenes this output folder already finished")
    ap.add_argument("--min-free", type=float, default=0.0, help="GB of free memory: under it a scene stops and reruns when there's room (the machine may be shared)")
    a = ap.parse_args()
    QA = Path(a.out).resolve()
    TIMEOUT = a.timeout
    RESUME, MIN_FREE, ROM_NAME = a.resume, a.min_free, a.rom
    EXTRA_LUA.extend(a.lua)
    QA.mkdir(parents=True, exist_ok=True)
    table = scenes()
    if a.only:
        table = {k: table[k] for k in a.only.split(",")}
    # Every run on one ROM name shares this emulator's battery file: a save left there makes New Game ask to overwrite, and the warp never fires.
    SAVE_FIXTURES.mkdir(parents=True, exist_ok=True)
    battery = ROOT / "tools/mesen/Saves" / (Path(a.rom).stem + ".sav")
    aside = SAVE_FIXTURES / "before_regen.sav"
    if battery.exists():
        shutil.move(battery, aside)
    try:
        plain = [(k, v) for k, v in table.items() if not v[2] and not v[3]]
        with ThreadPoolExecutor(a.jobs) as pool:
            results = list(pool.map(lambda kv: run(a.rom, kv[0], *kv[1]), plain))
        for name, v in table.items():  # save writers, then their readers: one at a time, never beside the runs above
            if v[2]:
                results.append(run(a.rom, name, *v))
                if battery.exists():
                    shutil.move(battery, SAVE_FIXTURES / (name + ".sav"))
        results += [run(a.rom, name, *v) for name, v in table.items() if v[3]]
    finally:
        battery.unlink(missing_ok=True)
        if aside.exists():
            shutil.move(aside, battery)
    rows, bad = ["name\texit\treached\tblank"], 0
    for name, code, reached, blank in results:
        rows.append("%s\t%d\t%s\t%s" % (name, code, reached, blank))
        ok = code == 0 and reached and not blank
        bad += not ok
        print(("ok  " if ok else "FAIL"), name, "exit", code, "reached", reached, "blank", blank)
    (QA / "report.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    finals = [str(QA / n / "final.png") for n in table]
    subprocess.call([sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts/sheet.py"), *finals, "--out", str(QA / ("proof_only.png" if a.only else "proof.png"))], cwd=ROOT)
    print(len(results) - bad, "of", len(results), "ok")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
