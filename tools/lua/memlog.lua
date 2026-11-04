-- Log every write to the watched ranges, with frame, PC and value. --var "MEMS={0x0203BD98,0x03006270}" (each watches 4 bytes).
for _, a in ipairs(MEMS or {}) do
  L.on_write(a, a + 3, function(addr, v)
    L.log(string.format("MEM f%d pc=%08X a=%08X v=%X", L.frame, L.pc(), addr, v))
  end)
end
