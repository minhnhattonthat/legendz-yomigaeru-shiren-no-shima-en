-- Log where the message builder (0x080A2AF0) writes when its source holds a code >= 0x100 (kanji cells), then who reads that
-- buffer: finds the renderer of battle text. Hooks the builder's entry and return; r0 = source, r1 = dest.
local mem = emu.memType.gbaMemory
local armed, seen = {}, {}
L.on_exec(0x080A2AF0, 0x080A2AF0, function()
  local s = emu.getState()
  local src, dst = s["cpu.r0"], s["cpu.r1"]
  if src < 0x08000000 then return end
  local t, kanji = {}, false
  for i = 0, 15 do
    local w = emu.read16(src + i * 2, mem)
    t[#t + 1] = string.format("%04X", w)
    if w >= 0x100 and w < 0x140 then kanji = true end
    if w >= 0xFFFE then break end
  end
  L.log(string.format("f%d build src=%08X dst=%08X %s %s", L.frame, src, dst, kanji and "KANJI" or "", table.concat(t, " ")))
  if not armed[dst] then
    armed[dst] = true
    L.on_read(dst, dst + 0x40, function(addr)
      local pc = L.pc()
      if seen[pc] then return end
      seen[pc] = true
      local st = emu.getState()
      L.log(string.format("f%d read pc=%08X addr=%08X lr=%08X", L.frame, pc, addr, st["cpu.r14"] or 0))
    end)
  end
end)
