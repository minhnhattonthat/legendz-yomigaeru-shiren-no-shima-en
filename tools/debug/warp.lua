-- Warp to a named scene from a cold boot. Scene data: scenes.lua. Mechanism and addresses: docs/re/debug.md.
--   emu.py ROM --out DIR --script tools/debug/warp.lua --var "SCENE='name'" --frames 900 --sheet
-- Drives the title by RAM, never by frame count: press Start until the title menu's mode, write New Game's mode, then swap
-- the target of the new game's first change-scene op. Logs REACHED when the game has entered the scene's room script.
local MEM = emu.memType.gbaMemory
local MODE, ENTRANCE = 0x0203BD98, 0x03006270
local NEWGAME_SCENE = 0x0802483A
local FLAGS = 0x02036A30
local SCENES = dofile("../debug/scenes.lua")  -- Mesen runs from tools/mesen
local scene = assert(SCENES[SCENE], "unknown SCENE " .. tostring(SCENE))
if scene.doll then dofile("../debug/virtual_doll.lua") end

local function setflag(n) local a = FLAGS + (n >> 3); emu.write(a, emu.read(a, MEM) | (1 << (n & 7)), MEM) end
local function clrflag(n) local a = FLAGS + (n >> 3); emu.write(a, emu.read(a, MEM) & ~(1 << (n & 7)) & 0xFF, MEM) end

local function apply(entry)
  if entry.partner then
    for _, run in ipairs(dofile("../debug/partner.lua")) do
      local hex = run[2]
      for i = 0, #hex // 2 - 1 do emu.write(run[1] + i, tonumber(hex:sub(i * 2 + 1, i * 2 + 2), 16), MEM) end
    end
    setflag(0x15F)  -- Small Cave's "has Reborn" gate (docs/re/doll.md)
  end
  for _, n in ipairs(entry.flags or {}) do setflag(n) end
  for _, n in ipairs(entry.clear or {}) do clrflag(n) end
  for _, w in ipairs(entry.mem or {}) do
    if w[3] == 4 then emu.write32(w[1], w[2], MEM) elseif w[3] == 1 then emu.write(w[1], w[2], MEM) else emu.write16(w[1], w[2], MEM) end
  end
end

local start_keys  -- set when the scene is reached; keys count from there

-- The handler of 00F2 has just stored its pointer in the task PC. Swap it for the scene's script.
local warped = false
L.on_exec(0x0808B8B8, 0x0808B8B8, function()
  if warped or scene.stop_at_title then return end
  local s = emu.getState()
  if (s["cpu.r0"] & 0x0FFFFFFF) ~= NEWGAME_SCENE then return end
  warped = true
  apply(scene)
  emu.write32(s["cpu.r2"] + 4, scene.target | 0x08000000, MEM)
  emu.write32(ENTRANCE, scene.entrance or 0, MEM)
  L.log(string.format("REACHED %s f%d script %08X entrance %d", SCENE, L.frame, scene.target | 0x08000000, scene.entrance or 0))
  start_keys = L.frame
end)

local booted, pressed = false, -999
local chosen, triedDown
local nextkey = 1
local CURSOR = 0x030004D4  -- title menu: 0 continue, 1 card mode, 2 new game, 3 doll init
L.on_frame(function(n)
  if not booted then
    local mode = emu.read32(MODE, MEM)
    if chosen and mode ~= 0xB then
      -- Only New Game writes 8 (0x080CEB0A). Any other pick means the cursor wasn't where this route assumes.
      if mode ~= 8 then error("title menu picked mode " .. mode .. ", not New Game") end
      booted = true
    elseif mode == 0xB then
      -- Use the real menu: poking the mode skips its cleanup and leaves the title's ribbon sprite on screen for the whole run.
      -- Mode 0x0B is the title screen waiting for Start as well as the menu. Down only moves the cursor once the menu is open,
      -- so alternate: Down, and if the cursor didn't move, Start. Frame counts here only space the presses.
      if n - pressed > 60 then
        pressed = n
        if emu.read(CURSOR, MEM) ~= 2 then
          triedDown = not triedDown
          L.press(triedDown and "down" or "start", 6)
        elseif scene.stop_at_title then
          booted = true
          L.log(string.format("REACHED %s f%d title menu", SCENE, n))
          start_keys = n
        else
          L.press("a", 6)
          chosen = n
        end
      end
    elseif mode == 0x11 and n - pressed > 30 then
      L.press("start", 4)
      pressed = n
    end
    return
  end
  if not start_keys then return end
  -- A room's setup draws its map and actors; only then move the room's task (1) to a line deep in its script.
  if scene.jump and n - start_keys == scene.jump[2] then
    emu.write32(0x03002780 + 0x98 + 4, scene.jump[1] | 0x08000000, MEM)
    L.log(string.format("JUMP %08X f%d", scene.jump[1] | 0x08000000, n))
  end
  -- run = {frames, ram addr, hex}: VM bytecode no room holds (a native call to dead code), written to unused RAM; the room's task jumps to it
  if scene.run and n - start_keys == scene.run[1] then
    local at, hex = scene.run[2], scene.run[3]
    for i = 0, #hex // 2 - 1 do
      assert(emu.read(at + i, MEM) == 0, string.format("run: RAM %08X in use", at + i))
      emu.write(at + i, tonumber(hex:sub(i * 2 + 1, i * 2 + 2), 16), MEM)
    end
    emu.write32(0x03002780 + 0x98 + 4, at, MEM)
    L.log(string.format("RUN %08X f%d", at, n))
  end
  local pre = scene.premash or 0
  if n - start_keys < pre then
    if n % 40 == 0 then L.press("a", 6) end  -- click through the room's opening lines
    return
  end
  -- The top loop opens the field menu on Start only with flags 0 and 9 clear (script 0x240); a warped room never clears them.
  -- Save refuses with flag 6 or 8 set (0x080A69F8).
  if scene.free then clrflag(0); clrflag(9); clrflag(6); clrflag(8) end
  local keys = scene.keys or {}
  local k = keys[nextkey]
  if k and n - start_keys - pre >= k[1] then
    L.press(k[2], 6)
    L.log(string.format("KEY %s f%d", k[2], n))
    nextkey = nextkey + 1
  elseif not k and scene.mash and n % scene.mash == 0 then
    L.press("a", 6)
  end
end)
