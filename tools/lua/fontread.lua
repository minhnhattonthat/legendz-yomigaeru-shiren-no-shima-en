-- Log each distinct PC reading the font range, with r0-r7/lr. --var LO=0x... --var HI=0x... [--var MAX=40]
local lo, hi, max = LO or 0x0842A000, HI or 0x08430000, MAX or 40
local seen, n = {}, 0
L.on_read(lo, hi, function(addr)
  local pc = L.pc()
  if seen[pc] or n >= max then return end
  seen[pc] = true
  n = n + 1
  local s = emu.getState()
  local t = {}
  for i = 0, 14 do t[#t + 1] = string.format("r%d=%08X", i, s["cpu.r" .. i] or s["gba.cpu.r" .. i] or 0) end
  L.log(string.format("f%d pc=%08X addr=%08X %s", L.frame, pc, addr, table.concat(t, " ")))
end)
