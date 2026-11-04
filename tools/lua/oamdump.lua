-- Log the visible OAM entries at frame AT (--var AT=2700): index, x, y, shape/size bits, tile, palette.
local at = AT or 1000
L.on_frame(function(n)
  if n ~= at then return end
  local m = emu.memType.gbaSpriteRam
  for i = 0, 127 do
    local a0 = emu.read16(i * 8, m, false)
    local a1 = emu.read16(i * 8 + 2, m, false)
    local a2 = emu.read16(i * 8 + 4, m, false)
    if a0 & 0x0300 ~= 0x0200 then
      L.log(string.format("OAM %3d x=%3d y=%3d shape=%d size=%d tile=%3d pal=%d prio=%d", i, a1 & 0x1FF, a0 & 0xFF, a0 >> 14, a1 >> 14, a2 & 0x3FF, a2 >> 12, a2 >> 10 & 3))
    end
  end
  L.shot("oam.png")
end)
