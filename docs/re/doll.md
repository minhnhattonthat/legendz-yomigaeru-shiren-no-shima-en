# Soul Doll adapter

## The gate (verified)

Small Cave (scene `0x023C4E`) is a hard gate without the adapter. Its exit checks flag `0x15F` (`0x023DB2`-`0x023DE6`: if unset, `ちょっと！ ここまできて どこいくつもりなの？` and you stay). The player can only get a Legendz here through field menu > タリスポッド > リボーン, which reads a physical doll. Verified in Mesen on the original ROM, no adapter: the read fails, Haruka says the cable or doll came out (`0x45BEF8`), and the loop repeats. **So a virtual doll must ship in the release** (status.md default, decision D8).

## Read path (verified by hooks unless marked)

| What | Where |
|---|---|
| Adapter driver: GPIO `0x080000C4-C8`, link port RCNT, timer IRQ | `0x0E3F80-0x0E4D9x` |
| Status word: `0x01` busy, `0x02` present, `0x20` transfer, `0x8000` no reply (the IRQ at `0x080E4D98` sets it) | `0x03006D48` |
| Status test used by game logic, mask table `0x434E78` (1, 2, 0x10, 0x20, 0x8000) | `0x080BADA8` |
| Doll task, states: 0x0A idle, 0x14 read 0x80 bytes, 0x1E read 0x380 bytes, 0x28/0x32 write | `0x080BADD4`, table `0x080BADF0` |
| Transfer start (buffer, length, doll offset) | `0x080E4948` read, `0x080E488C` write |
| Reborn screen: reads image, reads header, decrypts, classifies | `0x080C7A7E`-`0x080C7B02` |
| Header buffer, 0x380 bytes. `+0x302` is the doll's type byte | `0x0201C420` |
| Image buffer, 0x80 bytes (doll offset 0x380), dwords xored with `0xA8262CDB`, `+0x7E` checksum: byte sum of the first 0x7C, xored with `0x4832` (`0x080C3EB0`) | `0x02036920` |
| Current doll: `+1` result code, `+2` type byte, `+3` species | `0x0203B360` |
| Doll byte to species, 0x3B pairs. `0x2C` is species 0 Hexadragon, `0xFF` is the fallback | ROM `0x466E74` |
| Species `0x21`-`0x25`, 5 entries: `0x080C3330` returns 1 for these, which gives result code 3 | ROM `0x466E60` |

Result code from `0x080C326C`: the return values are read from code, what each means is a **guess** from the texts in table `0x467BD0` (same-doll limit, "only one Hexadragon", on-adventure and so on): 0 same doll again, 2/7 new doll, 3 unsupported, 4 roster full (count above `0x5F`), 6 a mode check.

**Code 7 (verified, issue #1):** the image's checksum holds (a doll with data) and the roster is empty (`0x080DA708` = 0), i.e. a used doll on a new save. The story's first Reborn then loops on `いまセットした ソウルドールは ヘキサドラゴン じゃないわよ？` / `いまは ヘキサドラゴンを リボーンするのよ！` (`45C968`, `45C9A8`). The game's own rule: title > ドールしょきか writes a fresh image (0x80 bytes through `doll_write`), and the next new game's Reborn gets code 2. The patch's doll persists in flash, so a player restarting must reset it first (README says so). Repro: a save that is blank (0xFF) but for flash sector 15 holding a used image, then scene `reborn_crystal`'s Reborn (`emu.py --sav`).

## Names in the image (verified, issue #1)

The image keeps names a byte a letter: owner `+0x18` (5), nickname `+0x31` (8), four more 5-byte names at `+0x39`-`+0x48`, 16 bytes at `+0x41`. `0x080C3438` packs words to bytes (low byte), `0x080C3400` unpacks (0xFF ends a name, `FFFF`). English `o` is `0xFF` and `p`-`z`, space and the rest are `0x100`+, so v1.0 dolls showed `x` as く and `r` as り, and an `o` cut the name. `asm/doll.s` replaces both: `0x101`-`0x115` keep their low byte (v1.0 dolls read back right), `o` is `0x16`, `p` `0x17`, a pair word goes in as its two letters. Test: `tests/test_doll.py`; in game, scene `doll_init_full` with a used doll's save shows the names.

## What a blank doll does (verified)

`tools/debug/virtual_doll.lua` answers the path above: present bit on, no-reply bit off, buffers filled, status cleared 8 frames after the start (the task at `0x080C8490` must see busy first). The image decrypts to zeros, the checksum fails and the game treats it as a new doll, so the game's own Reborn runs: the Legendz appears, its name entry opens, the story continues. Test: `work/qa/d1/sheet.png`, doll byte `0x2C`.

**What Reborn changes in the save struct `0x02036A30`** (diff across the scene, `work/qa/d0` vs `d3`): `+0x1F2` doll byte, `+0x265` skill bits, `+0x280` roster record 0 (0xA4 bytes each, 96 slots; slot in use: `+0x288` nonzero, `0x080DA708`), `+0x403C`-`+0x40A7` (guess: a second copy of the live partner, the bytes look alike), and flags.

## For the release (phase 5)

The Lua hook is a debug tool, not the patch. The patch must do the same in ROM:
- Short-circuit `0x080E4948` and `0x080E488C` (fill or keep the buffer, finish at once) and keep `0x03006D48` showing present.
- Persist what the game writes to the doll: a real doll stores its Legendz, so a doll image lost at power-off would lose that Legendz's progress. Where it goes: not decided; flash has room to check (`FLASH512_V131`, 64 KB).
- Doll choice: a player has no doll to pick. Default: one Hexadragon (byte `0x2C`), the story's partner (`0x17F154`). Other dolls unlock species the game treats as optional; open whether to offer a list (non-blocking, status.md).
- ドールしょきか (title menu) must not offer to wipe what the player can't re-read. Check it once the patch works.
