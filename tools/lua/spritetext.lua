-- Log each glyph the sprite text renderer (0x080A2734, battle top line) is given; dump the PPU once, a little after a code >=
-- 0x100 (a kanji cell) first appears, to compare the on-screen glyph with tools/spritefont.py.
local mem = emu.memType.gbaMemory
local dump_at
L.on_exec(0x080A2734, 0x080A2734, function()
  local s = emu.getState()
  local code = emu.read16(s["cpu.r0"], mem)
  L.log(string.format("f%d glyph %04X", L.frame, code))
  if code >= 0x100 and code < 0x140 and not dump_at then dump_at = L.frame + (DELAY or 30) end
end)
L.on_frame(function(f)
  if f == dump_at then L.dump_ppu(string.format("ppu_%06d", f)) end
end)
