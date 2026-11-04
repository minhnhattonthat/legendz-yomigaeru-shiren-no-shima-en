# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2. Debug tool in progress: warp works, scene list incomplete. Last build: none yet (2026-11-05).
- **Done:** Step 0. Phase 1 recon (`docs/re/text.md`, `rom-map.md`, `graphics.md`). Phase 2 so far: `tools/debug/warp.lua` reaches any room from a cold boot through the real title menu; 45 scenes pass `tools/debug/regen.py` (proof sheets read: title screens, Small Cave, Reborn with and without the doll, field menu, Talispod, 35 rooms). Soul Doll question answered: **hard gate; a blank virtual doll passes it through the game's own code** (`docs/re/doll.md`, decision D8).
- **Next, phase 2, what the scene list still lacks** (its done-when needs every menu, shop, battle type, chapter, ending and the credits):
  - **Battle:** guess: `00B5 .. 00B1 .. 00B2 .. 0099 .. 00B3` is the setup, e.g. at `0x02B79E` (read `script.md`, try a warp there). Also game over: `ふぅ～ ヒドイめにあった` lines follow a loss in many rooms.
  - **Field menu's other commands** with a partner, item, status, save screens. Start does nothing in `town` reached by warp (`debug.md`, Known limits): find out why, or use another room.
  - **Shop, Expensive Shop and Rental screens:** the rooms load (`shop`, `expensive_shop`, `rental_shop`), the shop UI hasn't been opened. Text `いらっしゃいませ` near `0x294BA`.
  - **Player name entry:** `opening` stops before it. **Auto-adventure.** **Card mode inside.**
  - **Story beats, in order, need flags:** stage 2 briefing near `0x31952`, stage 3 `0x3DEB2`, stage 4 desert `0x46...`, final boss `0x5242C-0x57xxx`, award ceremony `0x6B2D0-0x6B480`, Saga Tournament `0x6B4C2-0x6FA44`. Rooms test flags with `000B`; read each room's head to find which.
  - **Ending and credits:** not found. No credits text in the font's ranges. Candidates: ops `0120`-`0124`, `00F7`, and the `0005 01E0 0800` returns to title at `0x1D44C`-`0x1E1A2` and `0x2ADAA`-`0x2B5AE`.
  - Then add `graphics.md` rows for each new screen, and put `regen.py` in `AGENTS.md` (done) if its options change.
- **Open bugs:** none in the game. Tool: `town` Start, above.
- **Not verified:** GUI keyboard input in `tools/mesen/` (Step 0 asks for it; `settings.json` holds no GBA key map yet, and sending keys to a window on the owner's desktop was skipped; if blank, Settings > Input > reset defaults). Graphics survey is a floor: 13 of 15 1x sweep pages not read closely, see `graphics.md`. That a battle runs correctly with the copied partner. Which species the blank doll gave: the story text says Hexadragon, not read off a status screen.
- **Waiting on the user:** non-blocking: which Soul Dolls the patch should offer. Default: one Hexadragon, the story's partner. Other species are then reachable only through rentals (`doll.md`, For the release).
- **Gotchas for the skill:** `fetch_emu.py mesen` failed with `CERTIFICATE_VERIFY_FAILED` on the release-asset CDN under this machine's Python (the API call and BIOS fetch worked); curl with verification on fetched the same URL (belongs in `references/setup.md`). The MesenCE 2.2.1 zip holds only `Mesen.exe`. Exec hooks over a wide range slow Mesen enough to hit the timeout (`calltrace.lua` over `0x080E3F00-0x080E4CFF`: exit 124 where the same run takes under a minute without it): belongs in `emulator-qa.md`. A title's mode variable can read "menu" well before the menu takes input; test the cursor moving, not the mode (`emulator-qa.md`, Debug tool).
