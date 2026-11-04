# Script VM

Handlers: table `0x7F25E0`, 317 entries (`0x12F`+ point at data, so 303 are real). Dispatcher `0x0808B326`. `tools/vm_ops.py` tabulates each handler; `tools/vmdis.py ADDR [COUNT]` disassembles linearly. `tools/lua/vmtrace.lua` logs each script PC the first time it runs: use it to test a guess.

Bytecode starts at **`0x1E0`**, not `0x10000`: task 0 starts there, and the title flow sits at `0x1E0`-`0x600`.

## Opcodes (operands in words after the opcode)

**Read from the handler's code:**

| Op | Operands | Meaning |
|---|---|---|
| 0001 | n | back up n words and yield a frame |
| 0002 | n | forward n words and yield |
| 0005 | ptr32 | jump |
| 0007 | n | wait n frames |
| 0009 / 000A | flag | set / clear story flag |
| 0019 | ptr32 | native Thumb call |
| 004A | addr32, value | store a word at a RAM address (top nibble masked off) |
| 0084 | dist, addr32, value | if the test fails, skip dist words (target = op + 2 + 2*dist). Top nibble of addr picks the test: 0 eq, 1 lt, 2 gt, 3 le, 4 ge, 5 ne |
| 00F2 | ptr32 | change scene: store the pointer in `[0x03005E40+0x3C]`, run the flag calls for 9 and 10 |
| 00FE | a, b, n, then n words | variable length: 3 + n words |
| 0108 | skill | store the skill id at `0x0201C394`, set its bit at `0x02036C95` |

**Read from the handler, phase 2:** 0014 `dist, mask`: skip `dist` words unless a key in `mask` is down (top nibble of mask picks which key word; the top loop uses `1008`, Start). 00DA `dist, n, then n words`: skip unless every flag matches (low 15 bits flag number, top bit the wanted value). 009D `var` opens the shop screen, 009E `var` the rental screen: seen working.

**Places:** `0x600`-`0x1C00` battle flow (mode 1). `0x020BA4`-`0x020C16` the end of the game, verified by `ending_end`: warped there, the credits play and stop on a `PASS:` screen. Which op starts them is a guess (native `0x080D1EDC`, then `0129 002F`), and so is mode 4 returning to the title: A presses never left the `PASS:` screen. Battle setup: `00B5 a, b, c`, `00B1`, `00B2`, `0099`, `00B3`: 79 hits; operands' meaning is a guess, and `00B5`'s `0010 00CD 0010` and `8000 00CE 0010` both run. `tools/findtext.py --natives` and `--lines LO HI` list natives and lines by offset.

**Seen working in a trace, meaning inferred:** 0003 call, 0004 return, 0006 skip, 000B `dist, flag` flag test, 0015 end task, 002E branch on the last choice, 008C spawn a task (top nibble: slot), 00C1 wait for child tasks, 00DD `speaker, ptr32` line with portrait, 00BE `ptr32` player's line.

**Guess, not tested:** 000F music, 0010 sound, 0020 set task variable, 0033 line with no portrait, 003C place an actor, 004D/004E and 005D/005E fades, 004F close the box, 0106 branch on a roster count, 0116 prize line (one of four pointers), the top nibble of 00BE as an expression.

## Limits

`vmdis.py` reads linearly: a table of data after a return desynchronises it, and it prints `????`. `OVERRIDES` covers what has been read by hand. Phase 4 must finish the operand table from every handler, because the extractor has to own each pointer.
