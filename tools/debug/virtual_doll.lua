-- Virtual Soul Doll for the emulator: answers the adapter read path so Reborn runs the game's own code. docs/re/doll.md.
-- --var DOLL=0x2C picks the doll byte (table at ROM 0x466E74; 0x2C = species 0 Hexadragon).
-- A read loads this doll's image: a blank one (decrypts to zeros, so its checksum fails and the game treats it as new), unless the game
-- wrote one back earlier in this run.
local MEM = emu.memType.gbaMemory
local STATUS = 0x03006D48  -- adapter status: 0x01 busy, 0x02 present, 0x20 transfer running, 0x8000 no reply
local KEY = 0xA8262CDB     -- image dwords are xored with this (0x080C3F00)
local doll = DOLL or 0x2C
local pending
local image = {}           -- what the game wrote back, per buffer offset

-- 0x080BADA8 is the one status test the game logic uses. The link IRQ keeps setting 0x8000 (no reply); show present and no error.
L.on_exec(0x080BADA8, 0x080BADA8, function()
  emu.write16(STATUS, emu.read16(STATUS, MEM) & ~0x8000 | 2, MEM)
end)

-- Transfer start (buffer, then two sizes; state machine 0x080BADD4 passes 0x80/0x380 or 0x380/0).
L.on_exec(0x080E4948, 0x080E4948, function()
  local s = emu.getState()
  pending = { kind = "read", buf = s["cpu.r0"], a = s["cpu.r1"], b = s["cpu.r2"] }
end)
L.on_exec(0x080E488C, 0x080E488C, function()
  local s = emu.getState()
  pending = { kind = "write", buf = s["cpu.r0"], a = s["cpu.r1"], b = s["cpu.r2"] }
end)

L.on_frame(function()
  if not pending then return end
  local p = pending
  p.wait = (p.wait or 8) - 1  -- the Reborn task must see the busy bit (0x080C8490) before it clears
  if p.wait > 0 then return end
  pending = nil
  local size = math.max(p.a, p.b)
  if p.kind == "read" then
    for off = 0, size - 4, 4 do
      local v = image[off]
      if v == nil then v = (size == 0x380) and 0 or KEY end
      emu.write32(p.buf + off, v, MEM)
    end
    if size == 0x380 then emu.write(p.buf + 0x302, doll, MEM) end
  else
    for off = 0, size - 4, 4 do image[off] = emu.read32(p.buf + off, MEM) end
  end
  emu.write16(STATUS, emu.read16(STATUS, MEM) & ~0x21 | 2, MEM)
  L.log(string.format("DOLL %s buf=%08X sizes %X %X f%d", p.kind, p.buf, p.a, p.b, L.frame))
end)
