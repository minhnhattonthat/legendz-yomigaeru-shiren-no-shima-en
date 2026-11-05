# Text engine

Addresses are ROM offsets for the dump in `rom.sha1`; CPU address = `0x08000000 + offset`. Reproduce the lists with `python -X utf8 tools/recon_text.py` (writes `work/recon/streams.tsv`, `spans.txt`).

## Encoding (verified)

16-bit little-endian words, one per character, raw in ROM (not Shift-JIS, not compressed). A word is a font cell index. `tools/jpcodec.py` holds the table.

**How verified:** read the first dialogue box in Mesen (`…あおいそら ながれるくも！ / そしてこの ひろいうなばら！`), found the same words at `0x180F1C`, and decoded `レジェンズタウン`, `LEGENDZ TOWN`, `ソウルドール` with the same table.

| Words | Glyphs |
|---|---|
| 0000 | fullwidth space |
| 0001-0051 | hiragana, gojuon order: あ..ん (0001-002E), voiced, semi-voiced, small kana, ゎ |
| 0052-00A3 | katakana in the same order, plus ヴ at 0080 |
| 00A4-00BD | A-Z (capitals only, no lowercase in the ROM font) |
| 00BE-00C8 | `$ 、 。 ー ～ … ！ ？ ‼ 「 」` |
| 00C9-00D2 | 0-9 |
| 00D3-00F0 | `・`, icons, `％ ＋ － ♪ 『 』 ：`, `（`=00EF, `）`=00F0 |
| 00F1-013C | kanji, in the battle sprite font only; blank in font 1 (see Sprite font) |
| 013D-015F | not used by any string |
| FFC4-FFF5 | inline variables expanded by the message builder (see Variables) |
| FFFB | sets window flag 4 (reader `0x080A5568`). No string uses it |
| FFFD | newline (reader `0x080A5572`) |
| FFFE | end of page: sets flags 8 and 0x40 (`0x080A5548`). Most pages have their own script pointer; some follow on with none, see Open 3 |
| FFFF | end of string: sets flag 0x40 (`0x080A5550`) |

`FFFC` has no case in the reader and no string, owned or dead, holds it: the 52 hits from the scan were non-text.

No kanji cell exists in the main font: dialogue is all kana. This is why the table is exact rather than a template-matched guess.

## Sprite font (verified)

Battle's top line and the auto-adventure quips aren't drawn with the fonts below: they go through the builder, then `0x080A2734`, into OBJ tiles.

- Table `0x7F2580`: 4 entries of 16 bytes (frame pointer, tiles, palette, widths). Tiles are LZ or raw after a 2-byte byte count. Tile order is column-major, 2 wide. `tools/spritefont.py OUT.png [--entry N] [--from HEX] [--to HEX]` draws a sheet; entry 0 matched VRAM dump `work/qa/bw7/ppu_002371` tile for tile.
- Entry 0 holds the kanji `00F1-013C`, read off the sheet (`jpcodec.KANJI`). Two near-twins: `0105` is 抜 (`毒が抜けた`), `010A` is 技 (`新しい技をひらめいた`).
- Entry 1's symbols differ from `00BE` up (`jpcodec.SPRITE_SYMS`): digits first, so what the dialogue table calls digits are punctuation here (`あ2ん…`, `カンジかな4` in the old decode). `script/quips.json` decodes with it and carries `"font": "sprite1"`.
- Quip path, static: `0x080B4BAC` indexes table `0x7F69F8`, builds into `0x02036890`, stores it in window `0x03005370`; the same module's `0x080B4A08` draws through `0x080A2734`. **Not seen on screen**: the `auto_spot` warp stuck on the adapter prompt. The proof so far is that the lines read correctly (`うそー‼`, `10バイ`, `なんちゃって★`); visual QA should still look.

## Variables (verified for the routing, meanings read from the text)

Builder `0x080A2AF0`: jump table `0x080A2B30`, indexed by word `- 0xFFC4`, 50 entries. It stops at `FFFE`/`FFFF`, so it builds one page. When `[0x0203BD98]` is 5, the visiting-doll report, most cases call `0x080B0604` (table `0x080B0628`, word `- 0xFFC6`) and take their value from the visiting doll's record at `0x03005B90`, not the player's.

| Word | Inserts | Source |
|---|---|---|
| FFC4 | money or EXP amount, 1-5 digits | `0x02003C74`, `0x080A5B38` |
| FFC5, FFEA | skill name | `0x080DB6BC(id)+4` |
| FFC6, FFE3 | Legendz species (report) | `0x082B0AE4`, 9 words |
| FFC7-FFCA | the doll's 4 skill names (report) | `0x082AA0AC` |
| FFD0-FFD7 | hours, minutes: story, auto-adventure, link, total | record, 2 digits each |
| FFD8, FFDA | rental partners; girls or boys among them | record, 2 digits |
| FFD9, FFE2 | owner names: best friend, most-fought | record, 5 words |
| FFDB-FFDD | doll kinds, dolls owned, skills learned | record, 2 digits |
| FFDE-FFE0 | link battles, wins, losses | record, 2 digits |
| FFE1 | team's top level | record, 3 digits |
| FFE5 | partner Legendz name | `0x080DA834`, `0x082B0AE0` |
| FFE7 | spot name | table, 9 words in report mode |
| FFE8 | spot count (report) | `0x0201DFA4`, 1-3 digits; report 2 |
| FFE9 | MP or HP amount | `0x0201DFA4`, 1-3 digits; report 2 |
| FFEB | the enemy's Legendz | `0x02036918`, `0x0201DFF0`, `0x082B0AE0` |
| FFEC | the player's Legendz (`いけ‼[FFEC]‼`) | `0x0203B564`, `0x0201E830`, `0x082B0AE0` |
| FFED | the enemy's name (`はヨワそうだぞ`); the doll's owner in the report | `0x020038B0`; report 5 words |
| FFEE | player name | `0x02036AF8`; report 6 words |
| FFEF | item name | `0x080D941C(id)`; report 9 words |
| FFF0-FFF2 | report: the doll's nickname, a mistaken name (the joke at `45E7A8`), the owner | `0x080B0604`; other modes: pointers at `0x02024CD0`, word `- 0xFFF0` |

No string uses FFCB-FFCF, FFE4, FFE6 or FFF3-FFF5. Meanings marked report are read from the report lines, not from a live visit.

**For insertion:** report mode copies a fixed number of words, not up to `FFFF` (`cmp r4, #8` at `0x080B0784`, and similar): 13 for FFF0, 9 for most names, 6 for the player, 5 for owners. Longer English names get cut there, and a shorter one must still hold its `FFFF` inside the count: check in phase 7.

## Extract (verified)

`tools/extract.py` writes `script/<block>.json`, one entry per string: `id` (ROM offset), `end` (past its terminator), `owners`, `jp`, `en`, `status`, `notes`, and `speaker` and `font` where known. Re-running keeps `en`, `status`, `notes` by id, and prints any id whose `jp` changed.

Owners, decoded rather than matched by a scan: script operands from `tools/vmwalk.py` (`opXX:site[:nibble]`), Thumb literal words (`lit:site`), and words in the named table regions (`tab:site`). `tools/vm_ops.py` gets each opcode's length by running its handler in Unicorn; the walker reaches 85,853 instructions over 303 handlers, and every PC seen in 715 traced ones. **5,922 strings, 114k characters.** `speaker` comes from the portrait op's operand via `0x184DF6`/`0x184F34`.

`tests/test_extract.py` asserts: each string re-encodes to its ROM bytes; each owner holds its pointer; every word of each block is a string, padding, dead or marked data; the files match the extractor; no unknown code in owned text.

**Op `0116` holds 4 pointers, one per partner personality** (`[FFC5]をおぼえたよ／たぞ／たわ／たぜ`): translate all four to match.

## Credits (verified)

`0x46F75C-0x46FF53`, one string, reached by the literal at `0x0D205C`, in `script/credits.json`. **One byte per glyph**, same codes as the table for `00-F0`, which is why the 16-bit search found nothing. `F1 x` colour, `F2 x` picture, `F3` next page, `FD` newline, `FF` end. `jpcodec.decode8`/`encode8`. It opens with a staff comment (`スタッフロールぶんめんはここからスタート`) that isn't drawn: guess, from where the roll starts on screen. The roll draws the Japanese glyph shapes, not the English font copies (an 8-bit draw path not traced; patching font 1 at `0x42BB6C` changed nothing on screen, and no tile of its `A` sits aligned in ROM or the LZ blocks): `C0` is 。, `BF` is 、, `DC` is ‥ and `EC` the colon, so `jpcodec`'s `：` at `DC` is a misnomer (D12).

## Not text

- `script/unreferenced.json` lists every leftover word of the blocks: `pad`, `data`, `dead`.
- `data`: `0x45A606-0x45A696`, `0x45AABC-0x45AE30`, `0x47BF20-0x47BF5E` (palettes and tables). `0x0AFFB8` and `0x0D34B0`'s literals into `0x47BF52` are these.
- 29 table or literal hits landing mid-string are rejected and printed by `extract.py`: words in graphics or data that look like an address, plus `0x0C53FC`'s `48177004`, a repeated constant whose neighbours aren't addresses. Nine real pointers skip a leading pair of words (`MID_OK`).
- **393 dead runs, not translated:** 195 dialogue, 123 `names_old`, the rest system, menus and places. No pointer-shaped word anywhere in the ROM names them at any 2-aligned offset, apart from 4 chance hits in graphics and code (`0x43FA7E`, `0x6060E0`, `0x0B8444`, `0x789552`). No literal base plus `adds` immediate reaches them (`pipeline.md` asks). Reads of `names_old` over `menu_talispod`, `battle` and `menu_items`: 0. What they are: `けつばん` and `まつびメッセージ` placeholders, the debug labels at `0x45BC18+`, `わざダミー`, a cut desert survival event (`0x16FD3E+`), and the personalities cut from 8 to 4 (`0x182600+`, between the live lines of op `0116`). **The marker build is the real check**: a computed pointer would show as Japanese there.

## Fonts (verified)

- Table at `0x7F6654`: font 1 `0x42BB6C` (normal), font 2 `0x42FD6C`, picked by bit 0 of the window flag byte (`[win+0xC]`). `code*48` bytes per glyph: 8x12, 4bpp, fixed width. Source: `0x080A5590`, confirmed by the read at `0x42DFFC` for code `00C3`.
- A glyph lands in VRAM as two stacked BG tiles (`0x8000` chr base in the dialogue screen, BG0, map `0xE000`, tiles `0x054`+ with palette F). Copy loop: `0x080A55B0`.
- Dialogue box width is 14 cells on line 1 and 17 on line 2 because the box is a parallelogram: measured from one screen only. Phase 5's width gate measures it properly.

## Message path (verified on the first dialogue)

1. Script opcode `00DD <arg> <ptr>` (handler `0x0808D464`) takes a 2-aligned pointer.
2. The builder (`0x080A2BC0` jump table, copy loops around `0x080A2F20`-`0x080A30EE`) copies words to EWRAM `0x02036890`, expanding variables on the way: player name, Legendz names (via `0x080B0604`), numbers.
3. Window struct `0x03004C50`: `[+8]` text pointer, `[+4]` VRAM destination, `[+0xC]` flags. Reader `0x080A5510` (`ldrh`, then `FFFB`/`FFFD`/`FFFE`/`FFFF`). Per-window globals at `0x03004C40`-`0x03004C48`.

**The EWRAM buffer is probably 68 words:** the next global the builder reads is at `0x02036918` (guess from that address; not checked for other users). The longest Japanese string is 58 words (a quip, `0x44293C`), so English in this buffer has almost no room to grow. Check before English lengths go in.

## Pointers (verified for scripts, partly guess for tables)

- Script pointers: 32-bit, **2-aligned**, stored as two halfwords after the opcode. `0x0808D498` masks with `0x0FFFFFFF`, so **the top nibble can hold flags** (`0x28182EA4` seen after opcode `00BE`, `0x18xxxxxx` too). Keep the nibble when repointing. Meaning of the flags: guess, not yet decoded.
- A whole-ROM scan with the nibble masked gives 5,986 referenced strings, 8,983 references, in: scripts (roughly `0x10000`-`0x8A000`), tables `0x187A60`+, `0x2AA0A8`+, `0x2ABB98`+, `0x2B0AE0`+, `0x450018`+, `0x45AADC`+, `0x467BD0`+, `0x47BFA0`+, `0x7F0020`+, `0x7F3370`+, `0x7F6A10`+, `0x7F74CC`+. Thumb literal pools also point at strings (`0x0B993C`, `0x0B9FA8`, `0x0D3868`, `0x0AFFB8`, ...).
- Plain tables of consecutive 4-byte pointers into text (phase 3 scan, runs of 20+; the starts above are mid-table for these): `0x7EFF18` x235, `0x7F330C` x190, `0x7F66CC` x875, `0x7F75E8` x89, `0x7F7F48` x23. `build.py` round-trips these. The others above (`0x187A60`, `0x2AA0A8`, `0x2ABB98`, `0x2AC11C`, `0x2B0AE0`, `0x450018`, `0x45AADC`, `0x467BD0`, `0x47BFA0`) have non-pointer words after their first entries: struct tables or code data, stride not yet decoded. `0x0C53FC` x8 uses nibble 4; `0x2AA284`, `0x2AB490` mix nibbles 0 and 2.
- **That scan is a recon sweep, not a repoint list.** Stray hits exist in graphics regions (single refs in `0x3Bxxxx`, `0x5Dxxxx`, `0x6Fxxxx`). The extractor must decode the owner of each pointer: walk the script VM (below) and the named tables. Do not patch every matching word.

## Script VM (partly verified)

- Handlers: 317-entry table at `0x7F25E0`; dispatcher `0x0808B326` (`ldrh` opcode, `bl` to handler, repeat while it returns 1). Task struct stride `0x98`, base `0x03002780`, script PC at `[+4]`.
- Stream of 16-bit words: scripts live roughly in `0x10000`-`0x8A000` (guess from pointer density; the VM's own code starts by `0x8B000`). Argument counts per opcode are not yet tabulated: phase 4 derives them from the handlers (how far each one advances `[r4+4]`). Opcode `00DD` length is 4 words.
- SJIS debug strings near `0x485664` and `0x76FBDC` (`子スクリプトがあふれました`, `移動バッファオーバーフロー`) are error messages, not player text: exclude them.

## Text ranges (coverage test: `tests/test_extract.py`)

| Range | Content | Pointers from |
|---|---|---|
| `0x1619D8-0x184DCC` | story dialogue, about 2,800 pages, 72k words | scripts |
| `0x1857D8-0x187A5C` | item names and descriptions; `0x1857D8` starts with a debug line | table `0x187A60` |
| `0x188070-0x188EA8` | place names, character names, some English labels | table `0x7F0020` |
| `0x188F00-0x1895B8` | Legendz names, dead (see Not text) | none |
| `0x23C36A-0x23D110` | battle messages (kanji, sprite font); the first 7 were found by the marker tour | table `0x7F32F0` |
| `0x2A7714-0x2A9EC2` | skill names (with `みせってい` placeholders) | table `0x2AA0A8` |
| `0x2AB4E0-0x2AB97C`, `0x2ABE2C-0x2AC100` | skill names and `せつめいぶん` placeholder descriptions | `0x2ABB98`, `0x2AC11C` |
| `0x2AFEE0-0x2B0ADE` | Legendz names | `0x2B0AE0` |
| `0x434BF8-0x434E40` | rental doll lines | `0x7F74CC`, code |
| `0x440C9C-0x448836` | partner quips, place names | `0x7F6A10`+ |
| `0x44F4B8-0x450016` | card and skill names | `0x450018` |
| `0x45A602-0x45B002` | menu labels (includes `わざダミー` placeholders) | `0x45AADC`, `0x7F7604`+ |
| `0x45BBCE-0x466CF0` | system and NPC dialogue, including Soul Doll instructions | `0x467BD0`+ |
| `0x47BD3C-0x47BF5E` | link cable messages | `0x47BFA0`, code |

About 124k words of referenced text in total. Non-text that decodes as text: `0x1EAC0A`-`0x1EC9E0` and `0x76E49A` (guess: coordinate data, from the number patterns), short noise across the graphics region: exclude them. `0x7F0000+` holds tables.

## Open

Phase 1's five are closed: battle codes are kanji (Sprite font), quip digits are the sprite layout (Sprite font), the unreferenced pages are dead (Not text), variables are listed (Variables), credits found (Credits). Left: quips on screen; the buffer size.
