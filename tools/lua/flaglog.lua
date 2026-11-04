-- Log each story flag number the game's own code asks about, once per caller: frame, flag, return address.
-- Tells you which flags a menu or a room tests. Run beside warp.lua. Flag code: docs/re/debug.md.
local seen = {}
local function hook(pc)
  L.on_exec(pc, pc, function()
    local s = emu.getState()
    local key = pc .. ":" .. s["cpu.r0"] .. ":" .. s["cpu.r14"]
    if not seen[key] then
      seen[key] = true
      L.log(string.format("FLAG f%d fn %08X flag %03X lr %08X", L.frame, pc, s["cpu.r0"], s["cpu.r14"]))
    end
  end)
end
hook(0x080933B8)
hook(0x08093348)
