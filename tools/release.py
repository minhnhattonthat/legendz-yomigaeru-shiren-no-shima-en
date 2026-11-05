"""release.py: build, gate and package the English patch (references/pipeline.md, Release). Stops at the first failure.

    python -X utf8 tools/release.py [--version 1.0] [--force]

Steps: build -> tests + lint (tools/check.py) -> smoke -> jp_check (leftover Japanese) -> qa_gate check on every
work/qa/**/manifest.tsv -> no unticked line in docs/polish.md -> debug tool off -> BPS patch (bps.py re-applies it) ->
apply to the clean dump and compare -> release/<NAME>_v<version>.zip holding the patch and README.txt.
The playable image stays in build/legendz_en.gba. An existing version's files need --force. Publishing is the owner's call.
"""
import argparse
import hashlib
import subprocess
import sys
import tempfile
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402

PY = [sys.executable, "-X", "utf8"]
NAME = "Legendz_Yomigaeru_Shiren_no_Shima_EN"
BUILT = ROOT / "build/legendz_en.gba"
README = ROOT / "tools/release_readme.txt"


def orig():
    return ROOT / (ROOT / "rom.sha1").read_text(encoding="utf-8").split("\n")[-2].split("  ", 1)[1]


def run(step, cmd):
    print("==", step, flush=True)
    if subprocess.call(cmd, cwd=ROOT):
        raise SystemExit("release stopped: %s failed" % step)


def hashes(data):
    return {"size": len(data), "crc32": "%08X" % (zlib.crc32(data) & 0xFFFFFFFF), "md5": hashlib.md5(data).hexdigest(), "sha1": hashlib.sha1(data).hexdigest()}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default="1.0")
    ap.add_argument("--force", action="store_true", help="overwrite this version's patch and zip")
    a = ap.parse_args()
    out = ROOT / "release"
    bps, zpath = out / ("%s_v%s.bps" % (NAME, a.version)), out / ("%s_v%s.zip" % (NAME, a.version))
    if (bps.exists() or zpath.exists()) and not a.force:
        raise SystemExit("%s already exists: pass --force to overwrite it" % zpath.name)

    run("build", PY + ["build.py"])
    run("tests and lint", PY + ["tools/check.py"])
    run("smoke", PY + [str(Path(SKILL) / "scripts/emu.py"), str(BUILT), "--out", "work/qa/release_smoke", "--route", "tools/routes/boot.txt", "--smoke"])
    run("leftover Japanese", PY + ["tools/jp_check.py", str(BUILT)])
    manifests = sorted((ROOT / "work/qa").rglob("manifest.tsv"))
    if not manifests:
        raise SystemExit("release stopped: no work/qa/**/manifest.tsv")
    for m in manifests:
        run("qa gate %s" % m.relative_to(ROOT), PY + [str(Path(SKILL) / "scripts/qa_gate.py"), "check", str(m), str(m.parent / "verdicts")])
    print("== polish list")
    left = [line for line in (ROOT / "docs/polish.md").read_text(encoding="utf-8").splitlines() if line.startswith("- [ ]")]
    if left:
        raise SystemExit("release stopped: %d unticked lines in docs/polish.md" % len(left))
    print("== debug tool off")
    # The debug tool is Lua the emulator runs (tools/debug/), never written into the ROM, and the build above ran with no
    # --marker/--qa flag. What's left to check: no write is a debug one.
    tags = {line.split(" ")[3] for line in (ROOT / "build/writes.txt").read_text(encoding="utf-8").splitlines() if line}
    if any("debug" in t or "marker" in t or "qa" == t for t in tags):
        raise SystemExit("release stopped: debug or marker writes in build/writes.txt: %s" % sorted(tags))

    src, built = orig().read_bytes(), BUILT.read_bytes()
    out.mkdir(exist_ok=True)
    run("patch", PY + ["tools/bps.py", "make", str(orig()), str(BUILT), str(bps)])
    with tempfile.TemporaryDirectory() as tmp:
        again = Path(tmp) / "again.gba"
        run("apply to the clean dump", PY + ["tools/bps.py", "apply", str(orig()), str(bps), str(again)])
        if again.read_bytes() != built:
            raise SystemExit("release stopped: the patched dump differs from build/legendz_en.gba")
    o, p = hashes(src), hashes(built)
    text = README.read_text(encoding="utf-8").format(version=a.version, patch=bps.name, **{"o_" + k: v for k, v in o.items()}, **{"p_" + k: v for k, v in p.items()})
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(bps, bps.name)
        z.writestr("README.txt", text.replace("\n", "\r\n"))
    print("%s: %s + README.txt\npatched sha1 %s crc32 %s; patch sha1 %s" % (zpath.relative_to(ROOT), bps.name, p["sha1"], p["crc32"], hashlib.sha1(bps.read_bytes()).hexdigest()))


if __name__ == "__main__":
    main()
