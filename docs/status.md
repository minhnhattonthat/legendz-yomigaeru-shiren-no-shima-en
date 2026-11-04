# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2. Debug tool next. Last build: none yet (2026-11-05).
- **Done:** Step 0 (repo, MesenCE 2.2.1 + BIOS, smoke on the original, guard hook, commit gate). Phase 1 recon: encoding, fonts, message path, pointer format, text ranges, LZ77, free space (`docs/re/text.md`, `rom-map.md`), first graphics survey (`graphics.md`).
- **Next:** phase 2: `tools/debug/` warp to any scene from cold boot: find map id, story flags, party RAM. First questions to answer: does the Soul Doll "Reborn" scene (`0x17EE30`) block progress without the adapter, and where is the field menu? Then add survey rows for every screen the live tour missed. Text that phase 4 must close: `text.md` § Open.
- **Open bugs:** none.
- **Not verified:** GUI keyboard input in `tools/mesen/` (Step 0 asks for it; `settings.json` holds no GBA key map yet, and sending keys to a window on the owner's desktop was skipped; if blank, Settings > Input > reset defaults). Graphics survey is a floor: 13 of 15 1x sweep pages not read closely, see `graphics.md`.
- **Waiting on the user:** non-blocking: the retail game needs a Soul Doll adapter that emulators and most players lack. Default: if phase 2 finds it blocks progress, the patch includes a virtual doll.
- **Gotchas for the skill:** `fetch_emu.py mesen` failed with `CERTIFICATE_VERIFY_FAILED` on the release-asset CDN under this machine's Python (the API call and BIOS fetch worked); curl with verification on fetched the same URL (belongs in `references/setup.md`). The MesenCE 2.2.1 zip holds only `Mesen.exe`.
