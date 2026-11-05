"""Graphics text or font text? Dump a scene's VRAM on the original ROM and look its tiles up in the LZ blocks.
A tile found nowhere is drawn at run time: if the script doesn't hold its words, the extractor missed them.

    python -X utf8 tools/gfx_trace.py SCENE [SCENE..] [--at FRAME]

Output: work/qa/trace/<scene>/ppu_*.vram.bin, then vramfind.py's runs per scene. Blocks go to work/lzblocks/ (docs/re/graphics.md).
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools/debug"))
import lz77
import regen
from skill import SKILL

BLOCKS = ROOT / "work/lzblocks"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scenes", nargs="+")
    ap.add_argument("--at", type=int, help="frame to dump; default the scene's last")
    a = ap.parse_args()
    rom = str(ROOT / regen.ROM)
    if not any(BLOCKS.glob("*.bin")):
        BLOCKS.mkdir(parents=True, exist_ok=True)
        for off, data, _ in lz77.scan(Path(rom).read_bytes()):
            (BLOCKS / ("%06X.bin" % off)).write_bytes(data)
    table = regen.scenes()
    for name in a.scenes:
        frames = a.at + 10 if a.at else table[name][0]
        out = ROOT / "work/qa/trace" / name
        cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts/emu.py"), rom, "--out", str(out), "--script", "tools/debug/warp.lua",
               "--var", "SCENE='%s'" % name, "--script", str(Path(SKILL) / "scripts/lua/probes/ppudump.lua"), "--frames", str(frames), "--timeout", "560"]
        if a.at:
            cmd += ["--var", "DUMP_AT=%d" % a.at]
        if table[name][3]:
            cmd += ["--sav", str(ROOT / "work/saves" / (table[name][3] + ".sav"))]
        subprocess.check_call(cmd, cwd=ROOT, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        vram = next(out.glob("ppu_*.vram.bin"))
        print("==", name, vram.name, flush=True)
        subprocess.call([sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts/vramfind.py"), str(vram), str(BLOCKS), "--fmt", "gba4"], cwd=ROOT, stdin=subprocess.DEVNULL)


if __name__ == "__main__":
    main()
