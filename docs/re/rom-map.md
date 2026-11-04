# ROM map, compression, free space

Dump: Legendz: Yomigaeru Shiren no Shima, serial AGB-BLJJ-JPN, header title `LEGENDZSHIMA`, code `BLJJ`, maker `B2` (Bandai), developer Bec, 2004. 8,388,608 bytes. The local file is named "Legions" (an old scene mislabel); the game is レジェンズ 甦る試練の島.
CRC32 `33950228`, MD5 `9c7546d2fd1399614b035ead1d66aa8d`, SHA-1 `ff1e05a2fa70933dcf58a8be4f82fa289647c28a`. Not compared with No-Intro's listing (no offline copy).

| Range | Content | State |
|---|---|---|
| `0x000000-0x0000C0` | header | verified |
| `0x0000C0-0x0001DF` | startup code (guess: not disassembled) | guess |
| `0x0001E0-~0x08A000` | script bytecode (16-bit words with embedded pointers; `script.md`) | start verified by trace; end is a guess from pointer density |
| `~0x08A000-0x0E7877` | code; script VM at `0x08B000`, text engine at `0x0A2000-0x0A6000` | named routines verified by disassembly and hooks |
| `0x0E7878-0x1619D7` | graphics, mostly raw | verified by sweep |
| `0x1619D8-0x1895C0` | text (see `text.md`) | verified |
| `0x18AC3C-0x42BB6B` | graphics, LZ blocks, portraits, monster sprites | verified by sweep |
| `0x42BB6C-~0x430000` | fonts: font 1 at `0x42BB6C`, font 2 at `0x42FD6C` | starts verified; font 2's end is a guess |
| `0x430000-0x47FFFF` | UI graphics and text tables; credits text at `0x46F75C` (8-bit, `text.md`, Credits) | verified by sweep |
| `0x488000-0x6FFFFF` | isometric map tile blocks | verified by sweep |
| `0x700000-0x7EFFFF` | further graphics; LZ blocks to `0x7584F0`, tables after | partly verified |
| `0x7EFD1C` | `FLASH512_V131` save library marker | verified |
| `0x7F0000-0x7FFFFF` | pointer tables, script handlers (`0x7F25E0`), font pointers (`0x7F6654`), LZ blocks at `0x7F934C+` | verified for the tables named in `text.md` |

Save type: FLASH 64 KB (`FLASH512_V131`). Not EEPROM, so ROM growth doesn't affect saves.

## Compression (verified)

BIOS LZ77 type 0x10. `tools/lz77.py` decompresses and compresses; `lz77.scan` finds 2,159 well-formed blocks, 3.68 MB packed to 7.15 MB, 1,988 unique. Test: decompress(compress(x, min_disp=2)) == x on all 1,988 unique blocks, VRAM-safe (62 s, run once; `test_identity.py` keeps a sample). The original compressor isn't reproduced: 30 of 90 sampled blocks match with `min_disp=2`, 0 with 1, and the originals pass up some matches ours takes, so ours comes out smaller. So **rewrite only blocks the patch changes**, and keep pointers to the rest. 1,873 of the 2,159 blocks never use displacement 1 (VRAM-safe); recompress with `min_disp=2`. No text sits in LZ blocks: none decode to SJIS and the first dialogue line was not in any block. Thumb `svc 0x11` and `svc 0x12` each occur once in the code range; `0x13`/`0x14` hits may be data, so Huffman and RLE are unconfirmed but no block has needed them yet.

## Free space (verified that none exists inside the 8 MiB)

No run of 0x00 or 0xFF of 4 KB or more anywhere in the ROM. The patch appends past the end: **`0x800000` up (CPU `0x08800000`)**, up to 16 MiB for a BPS patch. The script VM's `& 0x0FFFFFFF` mask and Thumb literals accept those addresses. Text strings stay 2-aligned. Vacated Japanese text can be reused once its pointers are all rewritten.

## Soul Doll adapter (partly verified: this is a risk to players and QA)

- The retail game shipped with a Soul Doll and an adapter. The code drives cart GPIO `0x080000C4-C8` (`0x0E3F80-0x0E4700`) and link port RCNT `0x04000134` (literals at `0x0E47F0`, `0x0E4A2C`, `0x0E4C18`). Mesen emulates neither device.
- The title menu has ドールしょきか. The story uses "Reborn": `0x162396` `ドールをセットして、Aボタンをおしてね / リボーーーーン`, `0x17EE30` `アナタの ソウルドールを はやく これで リボーンしてみて！`.
- A forum post (gbatemp thread for dump 1596) says the game won't progress until the doll is plugged in. **Verified in phase 2: it is a hard gate**, and a virtual doll passes it. See `doll.md`.

## Prior work

No English or other fan patch found (2026-11-05 web search). Cheat codes exist on wazap.jp (`所持金999999` as an encrypted PAR code); no plain RAM addresses found. Sequel: Legendz: Sign of Nekurom (GBA) takes a password from this game's ending, so **the ending password display must stay byte-exact**.
