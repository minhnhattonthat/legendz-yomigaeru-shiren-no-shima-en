-- Log each text stream pointer the window structs at 0x03004C50+ walk (first pointer of each new message), with bytes.
-- --var WIN=0x03004C50 --var COUNT=4 --var STEP=0x?? (stride from RE notes)
local base = WIN or 0x03004C50
local last = {}
L.on_frame(function(n)
  for i = 0, (COUNT or 4) - 1 do
    local w = base + i * (STEP or 0x14)
    local p = emu.read32(w + 8, emu.memType.gbaMemory)
    if p ~= last[i] then
      if last[i] == nil or p < last[i] or p > last[i] + 256 then
        local t = {}
        for k = 0, 39 do t[#t + 1] = string.format("%04X", emu.read16(p + k * 2, emu.memType.gbaMemory)) end
        L.log(string.format("f%d win%d ptr=%08X %s", n, i, p, table.concat(t, " ")))
      end
      last[i] = p
    end
  end
end)
