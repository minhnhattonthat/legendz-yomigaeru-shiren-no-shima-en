# Legendz: Yomigaeru Shiren no Shima (GBA) English translation

The repo slug says "legions" (mislabelled dump name); the game is レジェンズ 甦る試練の島, header `LEGENDZSHIMA`/`BLJJ`.

Skill: translate-retro-game; `python tools/skill.py` prints its folder. Read its SKILL.md before ROM, text or QA work. `"$(python tools/skill.py)"` works in bash and PowerShell; never paste a `plugins/cache/<hash>` path.
Fresh clone: `git config core.hooksPath tools/hooks`; `fetch_emu.py mesen` and `fetch_emu.py gba-bios`.

## Commands (run from repo root)
- Build:    `python -X utf8 build.py` -> build/legendz_en.gba (phase 3+; checks the dump against `rom.sha1` first)
- Check:    `python -X utf8 tools/check.py` (tests + lint; the pre-commit hook runs this)
- Smoke:    `python -X utf8 "$(python tools/skill.py)/scripts/emu.py" build/legendz_en.gba --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Warp:     `python -X utf8 "$(python tools/skill.py)/scripts/emu.py" build/legendz_en.gba --out work/qa/warp --script tools/debug/warp.lua --var "SCENE='<name>'" --frames 900 --sheet` (phase 2+; scenes: `tools/debug/scenes.lua`; never ask the user to play to a scene)
- All scenes: `python -X utf8 tools/debug/regen.py [--only a,b] [--rom R]` (every scene from a cold boot; states in `work/states/`, proof sheets in `work/qa/scenes/`; read the sheets, `REACHED` only proves the warp fired)
- Release:  `python -X utf8 tools/release.py` (phase 9; patch + verify; never publish without the user)
- Clean:    `python -X utf8 tools/clean.py` (published projects: lists rebuildable/downloadable files; `--yes` deletes)

## Paths
- Original ROM: `rom/Legions - Yomigaeru Shiren no Shima (Japan).gba` (gitignored; SHA-1 in `rom.sha1`, checked by `tools/check_rom.py`). Emulator: this repo's own copy in `tools/mesen/` (MesenCE 2.2.1, https://github.com/nesdev-org/MesenCE/releases/download/2.2.1/Mesen_2.2.1_Windows.zip; gitignored; BIOS in `tools/mesen/Firmware/`; settings in `tools/emu-config/`). Savestates: `work/states/`.
- Text: `script/` (JSON, phase 4+). Tables: `tbl/`. Glossary: `glossary.md`. RE notes index: `docs/re/README.md`. Fonts and their licences: `docs/fonts.md`.

## Rulings
- Edit source files (.py .lua .asm .tbl .json) only with the file-edit tool; scripts here read and analyse, never `.replace()` and write back.
- Subagents: dispatch the `.claude/agents/` types (translator, reviewer, visual-qa, playtester), never general-purpose: their short tool list cuts each agent's start-up context from ~43k to ~9k tokens.
- The user's decisions, with the options and reasons: `docs/decisions.md`. Read it before asking the user anything; add each new ruling there the same session.
- Player bug reports: GitHub issues (`gh issue list --label bug`). Copy the attached save into `work/states/`, reproduce in the emulator, fix, commit with `Fixes #N`, and update `docs/status.md`.
- Text is 16-bit font indexes, raw in ROM, not Shift-JIS: `jp_left.py --sjis` sees only debug strings. See `docs/re/text.md`.

## Status
`docs/status.md`: done, next, open bugs. Update it at the end of every session.
