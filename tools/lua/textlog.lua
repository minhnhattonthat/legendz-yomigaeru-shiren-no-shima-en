-- Log every text draw once per (caller, text): kind, caller, the box's x y w h, font bit, top pad, text pointer. tools/windows.py reads these logs.
-- Kinds: T typewriter 0x080A5614, S instant 0x080A58D4, F fixed cells 0x080A5CB0, P sprite line 0x080A2850.
local seen = {}
local function log(kind, lr, text, x, y, w, h, flags, pad, tile)
  local k = kind .. lr .. ":" .. text
  if seen[k] then return end
  seen[k] = true
  local words = ""
  if text < 0x08000000 then -- built in RAM: the ROM string can't be looked up later
    for i = 0, 7 do words = words .. string.format(" %04X", emu.read16(text + i * 2, emu.memType.gbaMemory)) end
  end
  L.log(string.format("TEXT %s lr=%08X text=%08X x=%d y=%d w=%d h=%d flags=%02X pad=%d f=%d%s%s", kind, lr, text, x, y, w, h, flags, pad, L.frame, words, tile and string.format(" tile=%d", tile) or ""))
end
local function box(kind, addr)
  L.on_exec(addr, addr, function()
    local s = emu.getState()
    local d = s["cpu.r0"]
    local m = emu.memType.gbaMemory
    log(kind, s["cpu.r14"], emu.read32(d + 0x10, m, false), emu.read(d + 4, m), emu.read(d + 5, m), emu.read(d + 7, m), emu.read(d + 8, m), emu.read(d + 3, m), emu.read(d + 2, m), emu.read16(d + 0xA, m))
  end)
end
box("T", 0x080A5614)
box("S", 0x080A58D4)
box("F", 0x080A5CB0)
L.on_exec(0x080A2850, 0x080A2850, function()
  local s = emu.getState()
  log("P", s["cpu.r14"], s["cpu.r2"], s["cpu.r0"], s["cpu.r1"], 0, 0, 0, 0)
end)
-- The message builder's source: what a box shows comes from RAM, so this is where a dialogue line's own pointer shows.
L.on_exec(0x080A2AF0, 0x080A2AF0, function()
  local s = emu.getState()
  log("B", s["cpu.r14"], s["cpu.r0"] & 0x0FFFFFFF, 0, 0, 0, 0, 0, 0)
end)
