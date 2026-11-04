# Graphics-text survey

Offsets are LZ block starts unless marked raw. Each row needs English in a zoomed cold-boot shot, or "kept Japanese" per decision D5. Tools: `tools/gfx_sweep.py`, `tools/gfx_score.py`.

## Tile-drawn Japanese

| # | Element | Where seen | Source | State |
|---|---|---|---|---|
| G1 | Title logo レジェンズ with subtitle 甦る試練の島 | title screen | not traced; `0x0E7878` is the title block (holds "the world map" and other English labels) | seen on screen. Logo policy per D5: "Legendz" is an official spelling, in the copyright line (`© WiZ.LEGENDZ PARTNERS`) and header; no official English logo art found. Default: redraw in English |
| G2 | Bold kana label sheet (カ, ナ, ヒ... in dim grey tiles) | sweep | `0x47FE24` (1,792 bytes) | which screens use it: not traced |
| G3 | Menu frames with kana lettering and `Emblem`, `Command` English lettering | sweep | `0x435CA0` (14,176 bytes), `0x438E60` (2,688) | lettering confirmed in the zoom; words not read (dim palette). Screens not traced |
| G4 | Status labels: `NEXT`, `Lv`, `EX`, `S.E`, `HP` plus kana such as ちから | sweep | `0x45B004` (1,440) | seen in the zoom. Screen not traced |
| G5 | Date digits and 年月日 | sweep | `0x1617E8` (1,088) | seen in the zoom. Screen: not traced (guess: save slot) |
| G6 | HP/MP/EXP bars | sweep | `0x43A8E4`, `0x47F848` | English already; no change unless lettering conflicts |
| G7 | `EXIT` signs on maps | sweep | `0x4B8CFC` | English already |

## Text-engine screens, not graphics (listed so nobody hunts for tiles)

Same font: speaker tags (シュウ, ハルカ), dialogue, the location card, name entry grid and `スタートボタン：けってい`. Name entry needs an English grid and an English default name in phase 5; a kana-only name would otherwise show as Japanese in every later box. The title menu (つづきから, カードモード, さいしょから, ドールしょきか) looks like the same font: not confirmed by a hook.

## Coverage: what this survey did and didn't check

- **Static sweep:** all 2,364 items rendered: 2,024 drawn on 15 pages at 1x in `work/sweep/`, 171 duplicates and 172 tiny blocks listed in `index.tsv`. Regenerate with `python -X utf8 tools/gfx_sweep.py`.
- **Read closely:** 2 full pages at 1x, plus 2x sheets of 159 blocks picked by a lettering score (`gfx_score.py`) and non-map position. At 1x, 4bpp tiles in greyscale without their palettes are hard to read, and tiles ordered for 1D sprites come out scrambled.
- **Not read closely:** the other 13 pages, including most of `0x488000-0x6FFFFF` (isometric map blocks, which only showed `EXIT`) and raw regions. Linear formats were not rendered. Treat this list as a floor.
- **Live tour:** title, title menu, ドールしょきか screen, name entry, the opening ship and first outdoor scene. **Not reached:** field menu, battle, shop, card mode, doll screens, chapter cards, game over, ending, credits. Start and Select did nothing in the scene reached.

**Phase 2 must:** warp to each unreached screen and add rows. Phase 5's marker tour must add anything still Japanese. A row can only close once a VRAM dump and `vramfind.py` confirm its source.
