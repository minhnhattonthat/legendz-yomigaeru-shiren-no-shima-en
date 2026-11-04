-- Dump EWRAM+IWRAM to OUT/ram.bin at the last frame of the run (FRAMES). --var AT=N dumps at frame N instead.
local at = AT or FRAMES or 0
L.on_frame(function(n)
  if n == at then L.dump_ram(OUT .. (DUMP_NAME or "ram.bin")) end
end)
