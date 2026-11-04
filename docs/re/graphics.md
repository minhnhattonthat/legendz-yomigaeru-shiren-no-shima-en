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
| G8 | Field menu frame: `Emblem` and `Command` lettering (likely G3's blocks) | scene `field_menu` | not traced | seen on screen; English already, check nothing else in the frame is tile-drawn |
| G9 | Card mode screen: dark logo and lettering; `A:START`, `A:STOP`, `CARD LEVEL` English | scenes `card_mode`, `card_mode_in` | not traced | logo not read at full size |
| G10 | Credits staff roll: kana names and job titles on black beside map stills (`うつ えいじ`, `ウィズ`) | scene `ending_end` | not traced. Not in the font's encoding: `たかはし`, `さとう`, `ウィズ`, `せんでん` give no hit, so tiles, or text in another encoding | seen on screen, every shot |
| G11 | Last credits screen: `きかく・せいさく`, `せんでん・はんばい`, `かぶしきがいしゃバンダイ`, `ビデオゲームカンパニー`, `PASS: 0B7B` | scene `ending_end`, final frame | not traced; `PASS:` isn't ASCII in ROM either | seen on screen. What the password is for, and whether its digits vary: not known. Kept as a number either way |
| G12 | Battle start banner: `敵が出現!!`, `ENEMY APPEARED` | scene `boss_fight`, a dense sheet near frame 1200 | not traced | seen once at small size; it lasts under 150 frames, so the regenerated shots miss it: use a denser `every` |
| G13 | Status screen labels on the Talispod page: `Lv.`, `EX.`, `NEXT`, `S.E.`, `HP.`, ちから, ぼうぎょ, まりょく, まぼうぎょ, すばやさ (probably G4) | scene `menu_talispod` | `0x45B004` is the guess | seen at 2x; a VRAM check closes it |

## Text-engine screens, not graphics (listed so nobody hunts for tiles)

Same font: speaker tags (シュウ, ハルカ), dialogue, the location card, name entry grid and `スタートボタン：けってい`. Name entry needs an English grid and an English default name in phase 5; a kana-only name would otherwise show as Japanese in every later box. The title menu (つづきから, カードモード, さいしょから, ドールしょきか) looks like the same font: not confirmed by a hook.

## Coverage: what this survey did and didn't check

- **Static sweep:** all 2,364 items rendered: 2,024 drawn on 15 pages at 1x in `work/sweep/`, 171 duplicates and 172 tiny blocks listed in `index.tsv`. Regenerate with `python -X utf8 tools/gfx_sweep.py`.
- **Read closely:** 2 full pages at 1x, plus 2x sheets of 159 blocks picked by a lettering score (`gfx_score.py`) and non-map position. At 1x, 4bpp tiles in greyscale without their palettes are hard to read, and tiles ordered for 1D sprites come out scrambled.
- **Not read closely:** the other 13 pages, including most of `0x488000-0x6FFFFF` (isometric map blocks, which only showed `EXIT`) and raw regions. Linear formats were not rendered. Treat this list as a floor.
- **Live tour:** title, title menu, ドールしょきか screen, name entry, the opening ship and first outdoor scene; phase 2 added field menu and its five commands (items through three tabs, save, おていれ, auto-adventure's intro), Talispod status, card mode's reel game, Reborn, both name entries, shop and rental screens, battle to a win and a loss, the story beats in `scenes.lua`, credits, 35 rooms. **Not reached:** random encounters, auto-adventure past its intro, the shop's sell tab (Right moved nothing with a seeded bag, so it may not exist; the arrows at the top are drawn either way). No chapter card was seen in any `story_*` run, but those runs jump past each room's own entry, so that isn't proof there are none.
- The room `LEGENDZ TOWN` / `レジェンズタウン` location card comes from the text table at `0x7EFFC4`, not tiles.

Phase 5's marker tour must add anything still Japanese. A row can only close once a VRAM dump and `vramfind.py` confirm its source.
