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
| 00F1-015F | blank cells in font 1 (see Open) |
| FFC6-FFF2 | inline variables expanded by the message builder (see below) |
| FFFB | sets window flag 4 (reader `0x080A5568`; effect not yet known) |
| FFFD | newline (reader `0x080A5572`) |
| FFFE | end of page: sets flags 8 and 0x40 (`0x080A5548`). Most pages have their own script pointer; some follow on with none, see Open 3 |
| FFFF | end of string: sets flag 0x40 (`0x080A5550`) |

`FFFC` has no case in the reader. The 52 `FFFC` hits from the scan may be non-text; check them in phase 4.

No kanji cell exists in the main font: dialogue is all kana. This is why the table is exact rather than a template-matched guess.

## Fonts (verified)

- Table at `0x7F6654`: font 1 `0x42BB6C` (normal), font 2 `0x42FD6C`, picked by bit 0 of the window flag byte (`[win+0xC]`). `code*48` bytes per glyph: 8x12, 4bpp, fixed width. Source: `0x080A5590`, confirmed by the read at `0x42DFFC` for code `00C3`.
- A glyph lands in VRAM as two stacked BG tiles (`0x8000` chr base in the dialogue screen, BG0, map `0xE000`, tiles `0x054`+ with palette F). Copy loop: `0x080A55B0`.
- Dialogue box width is 14 cells on line 1 and 17 on line 2 because the box is a parallelogram: measured from one screen only. Phase 5's width gate measures it properly.

## Message path (verified on the first dialogue)

1. Script opcode `00DD <arg> <ptr>` (handler `0x0808D464`) takes a 2-aligned pointer.
2. The builder (`0x080A2BC0` jump table, copy loops around `0x080A2F20`-`0x080A30EE`) copies words to EWRAM `0x02036890`, expanding variables on the way: player name, Legendz names (via `0x080B0604`), numbers.
3. Window struct `0x03004C50`: `[+8]` text pointer, `[+4]` VRAM destination, `[+0xC]` flags. Reader `0x080A5510` (`ldrh`, then `FFFB`/`FFFD`/`FFFE`/`FFFF`). Per-window globals at `0x03004C40`-`0x03004C48`.

The EWRAM buffer's size is not yet known: **check it before English lengths go in** (it is sized for Japanese).

## Pointers (verified for scripts, partly guess for tables)

- Script pointers: 32-bit, **2-aligned**, stored as two halfwords after the opcode. `0x0808D498` masks with `0x0FFFFFFF`, so **the top nibble can hold flags** (`0x28182EA4` seen after opcode `00BE`, `0x18xxxxxx` too). Keep the nibble when repointing. Meaning of the flags: guess, not yet decoded.
- A whole-ROM scan with the nibble masked gives 5,986 referenced strings, 8,983 references, in: scripts (roughly `0x10000`-`0x8A000`), tables `0x187A60`+, `0x2AA0A8`+, `0x2ABB98`+, `0x2B0AE0`+, `0x450018`+, `0x45AADC`+, `0x467BD0`+, `0x47BFA0`+, `0x7F0020`+, `0x7F3370`+, `0x7F6A10`+, `0x7F74CC`+. Thumb literal pools also point at strings (`0x0B993C`, `0x0B9FA8`, `0x0D3868`, `0x0AFFB8`, ...).
- **That scan is a recon sweep, not a repoint list.** Stray hits exist in graphics regions (single refs in `0x3Bxxxx`, `0x5Dxxxx`, `0x6Fxxxx`). The extractor must decode the owner of each pointer: walk the script VM (below) and the named tables. Do not patch every matching word.

## Script VM (partly verified)

- Handlers: 317-entry table at `0x7F25E0`; dispatcher `0x0808B326` (`ldrh` opcode, `bl` to handler, repeat while it returns 1). Task struct stride `0x98`, base `0x03002780`, script PC at `[+4]`.
- Stream of 16-bit words: scripts live roughly in `0x10000`-`0x8A000` (guess from pointer density; the VM's own code starts by `0x8B000`). Argument counts per opcode are not yet tabulated: phase 4 derives them from the handlers (how far each one advances `[r4+4]`). Opcode `00DD` length is 4 words.
- SJIS debug strings near `0x485664` and `0x76FBDC` (`子スクリプトがあふれました`, `移動バッファオーバーフロー`) are error messages, not player text: exclude them.

## Text ranges (verified as decoding to sensible text; coverage test comes in phase 4)

| Range | Content | Pointers from |
|---|---|---|
| `0x1619D8-0x184DCC` | story dialogue, about 2,800 pages, 72k words | scripts |
| `0x1857D8-0x187A5C` | item names and descriptions; `0x1857D8` starts with a debug line | table `0x187A60` |
| `0x188070-0x188EA8` | place names, character names, some English labels | table `0x7F0020` |
| `0x188F00-0x1895B8` | Legendz names, currently unreferenced by the scan | find the owner in phase 4 |
| `0x23C3D4-0x23D110` | battle messages (uses codes `0100-013C`, see Open) | table `0x7F3370` |
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

## Open (phase 4 must close these)

1. **Codes `0100-013C` in battle text** (`は[0106][0107]している‼`, 57 distinct, all in `0x23C3D4+`): blank in font 1, so another font or renderer draws them; possibly kanji. Hook the battle message draw, read those cells and extend the table.
2. **Digits inside quips** at `0x440C9C+` (`あ2ん…`, `カンジかな4`): they don't read as digits. Guess: this block's renderer maps them to punctuation or emotes. Check on screen before translating.
3. **190 unreferenced dialogue pages**: reached by computed pointers, or dead text. The coverage test decides.
4. **FFC6-FFF2**: list each variable and what it inserts (the jump table at `0x080B0628` and `0x080A2BC0`).
