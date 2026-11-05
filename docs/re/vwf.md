# English text engine (phase 5)

Decision: **variable-width font in the game's own renderers, dialogue box widened from 17 to 20 cells, every string relocated past the dump.** No abbreviating. Source: `asm/vwf.s`, `tools/insert.py`, `tools/font_en.py`, `fonts/en_font.txt`. Tests: `tests/test_vwf.py` runs the assembly in Unicorn against a Python model of the screen.

## The renderers (verified by disassembly, the marker tour and the Unicorn test)

A text column is 2 stacked tiles, `0x40` bytes, 16 rows of one word. A glyph's 12 rows go in at the descriptor's top pad, so VRAM is laid out column after column and pen `x` of a line is `column x/8`, pixel `x%8`.

Descriptor (`d`): `+1` BG, `+2` top pad rows, `+3` flags (bit 0 font), `+4` x, `+5` y, `+6` map stride, `+7` **w, cells**, `+8` **h, rows of 2 tiles**, `+A` first tile, `+C` blank map entry, `+10` text, `+14` map.

| Renderer | Entry | Callers | English |
|---|---|---|---|
| Typewriter, one glyph a tick | `0x080A5614` opens the window, `0x080A54EC` ticks | 20 | hooked at the open's map fill `0x0A5786`, the glyph `0x0A5590`, the newline `0x0A5572` |
| Instant | `0x080A58D4` | 105 | hooked at `0x0A594C` |
| Fixed cells | `0x080A5CB0` | 10 | **not patched**: 2-digit numbers on a static map. Only draws digits |
| Sprite (OBJ) | `0x080A2850`, glyph `0x080A2734` | 4 | already proportional (width table), so new frames, tiles and widths; see Sprite font |
| Credits | `0x0D205C`'s literal | 1 | 8-bit codes: capitals only (below) |

Both patched renderers share `vwf_rows`: per row, measure to the line's end (`vwf_measure`, stops on a control word or past `w*8`), allocate `ceil(px/8)` columns, write the map, clear the tiles, then draw. A row uses tiles only as far as its text does, so **a window never takes more tiles than the original could at full w x h**.

The pen lives at `[window+0xE]`, unused by the game; the open zeroes it through a no-op it replaced (`orrs r0, r4` with r4 = 0 -> `strh r4, [r7, #0xe]`). `0x03004C40` stays the column under the pen; a cursor reads it (`0x080AFFC0`).

**The typewriter has no auto-wrap in English.** The open would wrap a too-long row, but the glyph code only moves its pen on `<br>`, so an overflowing line draws over the next line's tiles. The lint (phase 7) has to reject lines past the budget; the instant renderer wraps correctly.

## Font

`fonts/en_font.txt`, 89 glyphs, drawn for this project. Codes in `font_en.CODES`: English reuses a code that already means the character (A-Z `A4+`, digits `C9+`, `! ? . , ...`) so the game's own number and name code stays right. Lower case and the rest take `00F1+`, blank in the dialogue fonts.

- Font 1 (dialogue, story): colour 2 with a colour 6 shadow below, on colour 3. Advance = art + 1.
- Font 2 (menus, flag bit 0): colour 2 in a colour 1 outline on transparent 0. Advance = art + 1 with the outline 2 wider, so it writes only nonzero pixels and a neighbour's outline survives. The measured width gets 1 extra px so the last outline has a tile.
- Digits and code `0000` (what `0x080A5B38` pads numbers with) are all 6 px, so right-aligned numbers stay aligned. English space, a separate code, is 4 px.
- Kana cells stay as they were, 8 px: untranslated text is plain to see.

## Sprite font (verified: OAM dump, shot)

The battle's lines and the quips draw one 16x16 OBJ per word out of a **ring of 84 OBJ tiles**, 21 OBJs (`0x0203BDB8`, base `0x02024CF0`), and their slot lists hold 21 (`0x0A2172`). A longer line overwrites its own start. No sprite code is patched: a pair is a glyph of its own, its two letters side by side in the OBJ, so a line holds **21 words, 42 letters**. Frames, tiles and widths are written fresh and shared by the table's 4 entries, each keeping its palette (`font_en.sprite_font`). The tiles stay ROM pointers the OBJ loader copies from.

A line slides in, and mid-slide its letters look doubled: that's the game's animation, not a bug.

## Pairs: two letters a word (verified: Unicorn test, 8 tour scenes; the full tour was cut short, `status.md`)

The game's fixed limits count words: the name slots (6 for the player, 8 + terminator for a Legendz), report mode's copies (13, 9, 6, 5: `text.md`), the builder's 68-word buffer, the sprite ring. So **`font_en.encode` packs two letters in a row into one word**, code `0x400 + n`, numbered by the build (`pairs` in `insert.insert_marker`). That's a little over 300 for the marker text and a few thousand at most for the script: the word stays under `FFC0`, and the font tables only grow where a pair is looked up.

- `asm/vwf.s` splits a pair through the table (`vwf_split`) in the measure, row and typewriter code. A pair draws exactly as its letters do: `test_pairs_draw_exactly_like_their_letters`.
- The typewriter draws a word a tick, so English types at the speed of the Japanese, not half of it.
- **Kept as single words:** the name entry grid (`insert.SINGLE_WORDS`), because its cursor picks a cell by index.
- Anything else that reads text word by word needs to know: see the speaker tag below. Other `0x1BD210` users (`0x0AA92C`, `0x0D0A22`) draw numbers only.

## Speaker tag

`0x0A311C` has its own OBJ font (`0x1BD210`, 256 codes, stride 16, 8x16, fixed 8 px a word, 8 OBJ slots at `tag+0x12`): lower case is past its end, and a code there reads junk as a frame record, which blanks or corrupts the screen. It is **replaced** by `vwf_tag`: the name goes through the VWF into a 64x16 buffer on the stack, in font 2 (same colours as the tag font), and each column goes out as a tall OBJ through the game's own loader `0x08093FC4`, which copies at once. So a tag is proportional, **64 px**.

## Width gate

`tools/windows.py` writes `script/windows.tsv`: per string, px a row and rows, with source `measured` (drawn in the tour), `class` (a measured sibling) or `guess`. The table below holds on the final engine: all 75 scenes reached, and every box at every position has the same w and h as on the build before pairs, so **no box width comes from a word count**. `windows.py` must read a tour of the current build: it maps text addresses through `build/writes.txt`, which each marker build rewrites.

Two reads of the dump's own text are left, neither a word: `0x433F90` (`●`, a list's bead, code `0x0A9731`) and `0x440C8A` (8 blanks, an empty item name, `0x0A7919`).

**Non-text strings** (`insert.non_text`): a bead, blanks, a rule of colons, an empty slot, digits or variables alone. They keep their bytes in the marker and must stay out of translation: `188EA4` is the bead of the battle menu, and a marker there drew `4T` in place of it. Punctuation lines (`……`, `？？？`, `[FFEA]‼`) count as words.

**A label's leading `●` stays:** `●つづきから` and `●レンタル！` draw their own bead and the cursor sits on that cell, so English goes after it and the bead takes 8 px of the budget. Leading and trailing `　` pad a label to its box: English doesn't need them (`　　どうぐ　　` is a centred header, so centring it is the translator's call).

| Variant | Budget | Evidence |
|---|---|---|
| Dialogue box, with or without portrait | 156 px, 2 rows | ruler lines in the gate build; `T 0808D2DD`, `0x0A9547`, `0x0C80FF`, `0x0CF805`: 20x2 |
| One-row prompt, yes/no | 156 px, 1 row | `T 0x0C8273` 20x1 |
| Speaker tag | 64 px | `vwf_tag` |
| Battle line, location card | 240 px, and 21 words with variables expanded | sprite line |
| Item name | 64 px | `0x0A7919`, `0x0B7E5D` w=8; the count sits at 80 px |
| Item description | 88 px, 3 rows | `0x0A7A01`, `0x0B7F15` 11x3 |
| Legendz name | 64 px; 96 on its own status page | `0x0A58CF`, `0x0B98F9` w=8; `0x0C00EF` w=12 |
| Skill name | 80 px | `0x0BFCA5` w=10 |
| Field menu commands | 48-56 px | `0x0A58CF` w=6, 7 |
| Title menu | 48, 56, 56, 64 px, bead included | `0x0CF0AD` w=6, 7, 7, 8. Layout table `0x46B418`: pointer, x, y, w, 0. The left labels have 8 cells before the next one starts; raising w needs the tiles checked first (phase 7) |
| Name entry labels | 32-56 px | `0x0CC731`, `0x0CC75D` w=4; `0x0CC67F` w=7 |
| Save slot, shop and rental headers | 16-56 px | one-row `S` boxes at w=2-7 in `windows.tsv` |
| Quips | scrolling; 68-word buffer | **guess**: never on screen (`status.md`) |
| Card names, skill info, unreached labels | Japanese cells x 8 | **guess** |

An item, Legendz or skill name over its budget is engine work (`0x45AADC`-style layout tables hold x, y and w), not an abbreviation (D4).

## Longer than two lines: a second page

No text box holds more than 2 rows. A line that won't fit goes to another page **in the script**: replace its `00DD speaker ptr` (4 words) with `0005 ptr32` to appended bytecode `00DD speaker p1; 00DD speaker p2; 0005 back`. Same for `00BE ptr` and the other line ops. Consecutive `00DD`s already queue (`0x0808D148` returns 0 while a box is up). **Not built yet, and not proven in game: phase 7's job, for the lines that need it.** A line owned by op `0116` (4 pointers) or a table can't take this.

## Limits still to handle (phase 7)

- **Fixed save slots.** The default player name copies word by word into `0x02036AF8` (6 words), and money sits right after it: a 7-word marker corrupted money (`$` showed `A88E`). So `places` and `legendz` keep their Japanese word count, which pairs turn into twice the letters (`insert.NAME_SLOTS`). The lint has to hold each name to its Japanese word count; report mode (`text.md`) cuts at 13, 9, 6, 5 words.
- **A name the player types is one letter a word:** 6 letters in the slot, and a default name in pairs edits a pair at a time in name entry. Not seen in game yet.
- **Builder buffer** `0x02036890`: about 68 words, one page. Pairs put a full page near 40 words; variables add up to 13 each. Lint it on the page's worst case.
- **Sprite lines build on the stack:** `0x0A280C` and `0x0A2850` give it `0x40` bytes, 32 words. The ring's 21 words is the tighter limit; lint on it, variables expanded.
- **Menu labels from a layout table:** `0x45AADC` holds text, width, x and y per label (`0x0BF7DA`), so a longer English label needs that table's width raised, in phase 7.
- **Credits** are 8-bit codes up to `F0`, so capitals, digits and punctuation only: no lower case without a new font path.
