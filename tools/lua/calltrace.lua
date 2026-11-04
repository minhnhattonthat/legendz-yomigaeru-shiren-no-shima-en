-- Log each distinct (pc-range hit, lr) in LO..HI: who enters this code. --var LO=0x080E3F00 --var HI=0x080E4CFF [--var MAX=200]
local seen, n = {}, 0
L.on_exec(LO, HI, function()
  if n >= (MAX or 200) then return end
  local s = emu.getState()
  local lr = s["cpu.r14"]
  if lr >= LO and lr <= HI then return end  -- internal calls
  local pc = L.pc()
  local k = pc .. ":" .. lr
  if seen[k] then return end
  seen[k] = true
  n = n + 1
  L.log(string.format("CALL f%d pc=%08X lr=%08X r0=%08X r1=%08X", L.frame, pc, lr, s["cpu.r0"], s["cpu.r1"]))
end)
