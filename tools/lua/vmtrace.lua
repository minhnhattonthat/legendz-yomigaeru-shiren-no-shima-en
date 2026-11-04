-- Log each script VM opcode the first time its PC runs: frame, task index, script PC, opcode and the next words.
-- Hook is the dispatcher's ldrh (docs/re/text.md). --var MAX=20000 caps the lines; --var ONLY=0x3C logs one opcode;
-- --var ALL=1 logs every fetch, wait loops included.
local max, n, seen = MAX or 20000, 0, {}
local rd = emu.read16
L.on_exec(0x0808B32A, 0x0808B32A, function()
  if n >= max then return end
  local s = emu.getState()
  local p, task = s["cpu.r1"], (s["cpu.r4"] - 0x03002780) // 0x98
  local op = rd(p, emu.memType.gbaMemory)
  if ONLY and op ~= ONLY then return end
  if not ALL then
    if seen[p] then return end
    seen[p] = true
  end
  n = n + 1
  local t = {}
  for i = 1, 6 do t[i] = string.format("%04X", rd(p + i * 2, emu.memType.gbaMemory)) end
  L.log(string.format("VM f%d t%d %08X op=%04X %s", L.frame, task, p, op, table.concat(t, " ")))
end)
