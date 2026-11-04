# Reverse-engineering notes

One file per subsystem (text engine, pointers, compression, font, graphics). Mark every finding with how far it is
proven, so a later session doesn't build on a guess:

- **verified** - and how: a decoded known string, a corrupt-and-boot test, a breakpoint hit on the drawing path, a
  passing roundtrip test. Name the test or savestate.
- **guess** - and why it seems likely (byte pattern, another game, an earlier patch's notes). Promote it to verified
  before code depends on it.

Addresses are for the dump in `rom.sha1` unless a note says otherwise.

| File | Covers | State |
|---|---|---|
| `text.md` | encoding, control codes, fonts, message path, pointers, script VM, text ranges | verified; open items listed at its end |
| `rom-map.md` | ROM map, LZ77, free space, Soul Doll adapter risk, prior work | verified except where marked |
| `graphics.md` | graphics-text survey and what it didn't cover | first pass; phase 2 and 5 add rows |
| `script.md` | script VM opcodes | verified for what's listed; operand table incomplete |
| `debug.md` | how warping works, RAM map | verified except where marked |
| `doll.md` | Soul Doll adapter: the gate, the read path, what a virtual doll must do | verified; release design open |
