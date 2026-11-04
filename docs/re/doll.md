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

## What a blank doll does (verified)

`tools/debug/virtual_doll.lua` answers the path above: present bit on, no-reply bit off, buffers filled, status cleared 8 frames after the start (the task at `0x080C8490` must see busy first). The image decrypts to zeros, the checksum fails and the game treats it as a new doll, so the game's own Reborn runs: the Legendz appears, its name entry opens, the story continues. Test: `work/qa/d1/sheet.png`, doll byte `0x2C`.

**What Reborn changes in the save struct `0x02036A30`** (diff across the scene, `work/qa/d0` vs `d3`): `+0x1F2` doll byte, `+0x265` skill bits, `+0x280` roster record 0 (0xA4 bytes each, 96 slots; slot in use: `+0x288` nonzero, `0x080DA708`), `+0x403C`-`+0x40A7` (guess: a second copy of the live partner, the bytes look alike), and flags.

## For the release (phase 5)

The Lua hook is a debug tool, not the patch. The patch must do the same in ROM:
- Short-circuit `0x080E4948` and `0x080E488C` (fill or keep the buffer, finish at once) and keep `0x03006D48` showing present.
- Persist what the game writes to the doll: a real doll stores its Legendz, so a doll image lost at power-off would lose that Legendz's progress. Where it goes: not decided; flash has room to check (`FLASH512_V131`, 64 KB).
- Doll choice: a player has no doll to pick. Default: one Hexadragon (byte `0x2C`), the story's partner (`0x17F154`). Other dolls unlock species the game treats as optional; open whether to offer a list (non-blocking, status.md).
- ドールしょきか (title menu) must not offer to wipe what the player can't re-read. Check it once the patch works.
