-- Scene list for warp.lua. name -> {
--   target = script ROM offset (an 00F2 target, or a line inside one), entrance = [0x03006270], partner = true (Reborn's roster writes),
--   flags = {set}, clear = {clear}, mem = {{addr, value, size}}, doll = true (load virtual_doll.lua),
--   premash = press A for this many frames first, keys = {{frames after premash, "buttons"}}, frames = run length,
--   mash = press A every N frames after keys,
--   stop_at_title = true (no warp: stay on the title menu and let keys drive it), note }
-- Room offsets: tools/scene_scan.py (work/re/scenes.tsv). How the values were found: docs/re/debug.md.
local TOWN = 0x02F924
local F = 2600  -- the title menu is ready near frame 1500; a room is up about 500 frames later
return {
  -- Title screens: keys from the title menu, cursor on New Game (grid: continue, card / new game, doll init).
  title = { stop_at_title = true, frames = 1900, note = "title menu" },
  card_mode = { stop_at_title = true, keys = { { 30, "up" }, { 70, "right" }, { 110, "a" } }, frames = 2600, note = "title > カードモード" },
  doll_init = { stop_at_title = true, keys = { { 30, "right" }, { 70, "a" } }, frames = 2600, note = "title > ドールしょきか" },
  opening = { frames = 5000, target = 0x02483A, mash = 40, note = "new game's opening; stops before the player's name entry" },

  -- The doll gate, with and without the virtual doll.
  reborn_crystal = { target = 0x023C4E, frames = F, note = "Small Cave, crystal: the gate (docs/re/doll.md)" },
  reborn_nodoll = { target = 0x023C4E, frames = 7000, premash = 2800, mash = 40,
    keys = { { 0, "start" }, { 250, "a" }, { 550, "a" } }, note = "Small Cave, Reborn with no adapter: the failure lines" },
  reborn_doll = { target = 0x023C4E, doll = true, frames = 7000, premash = 2800, mash = 40,
    keys = { { 0, "start" }, { 250, "a" }, { 550, "a" } }, note = "Small Cave, Reborn with the virtual doll: Legendz appears, its name entry" },

  -- Field menu, from Small Cave (Start doesn't open it in the town room reached this way: see docs/re/debug.md).
  field_menu = { target = 0x023C4E, frames = 5000, premash = 2800, keys = { { 0, "start" } }, note = "field menu" },
  talispod = { target = 0x023C4E, frames = 5400, premash = 2800, keys = { { 0, "start" }, { 250, "a" } }, note = "field menu > Talispod" },

  -- Rooms, in rough story order.
  dwc_camp = { target = 0x0238B2, partner = true, frames = F, note = "DWC Camp" },
  valley_of_dawn = { target = 0x023AA4, partner = true, frames = F, note = "Valley of Dawn" },
  town = { target = TOWN, partner = true, frames = F, note = "Legendz Town" },
  rental_shop = { target = 0x02AB92, partner = true, frames = F, note = "Rental Shop" },
  goblin_den = { target = 0x02D014, partner = true, frames = F, note = "Goblin's Den" },
  blue_cave = { target = 0x02DDEC, partner = true, frames = F, note = "Blue Cave" },
  silver_cave = { target = 0x02E2F4, partner = true, frames = F, note = "White Silver Cave" },
  red_cave = { target = 0x02EA98, partner = true, frames = F, note = "Red Heat Cave" },
  island_camp = { target = 0x031DF0, partner = true, frames = F, note = "Island Camp" },
  north_camp = { target = 0x032A92, partner = true, frames = F, note = "North Camp" },
  hotel = { target = 0x0337BC, partner = true, frames = F, note = "Hotel" },
  dark_temple = { target = 0x03446A, partner = true, frames = F, note = "Dark Temple" },
  dragon_fountain = { target = 0x034E9E, partner = true, frames = F, note = "Dragon Fountain" },
  devil_cave = { target = 0x037F10, partner = true, frames = F, note = "Devil's Cave" },
  grey_cave = { target = 0x03B1FE, partner = true, frames = F, note = "Grey Cave" },
  trial_water = { target = 0x03E066, partner = true, frames = F, note = "Trial of Aqua" },
  old_cave = { target = 0x03FBE4, partner = true, frames = F, note = "こていのどうくつ" },
  dwarf_shop = { target = 0x041570, partner = true, frames = F, note = "Dwarf's Shop" },
  ship = { target = 0x0446D6, partner = true, frames = F, note = "Inside the Ship" },
  trial_wind = { target = 0x046244, partner = true, frames = F, note = "Trial of Wind" },
  west_camp = { target = 0x046E88, partner = true, frames = F, note = "West Camp" },
  mermaid = { target = 0x04A25E, partner = true, frames = F, note = "Mermaid's House" },
  trial_fire = { target = 0x04CC78, partner = true, frames = F, note = "Trial of Fire" },
  lighthouse = { target = 0x04D204, partner = true, frames = F, note = "Lighthouse" },
  office = { target = 0x04F9C8, partner = true, frames = F, note = "Office" },
  hospice = { target = 0x0525CA, partner = true, frames = F, note = "Hospice" },
  trial_earth = { target = 0x060ED0, partner = true, frames = F, note = "Trial of Earth" },
  south_camp = { target = 0x0660BA, partner = true, frames = F, note = "South Camp" },
  shop = { target = 0x066692, partner = true, frames = F, note = "Shop" },
  expensive_shop = { target = 0x066A16, partner = true, frames = F, note = "Expensive Shop" },
  snow_mountain = { target = 0x071E66, partner = true, frames = F, note = "Snow Mountain" },
  training_room = { target = 0x0795DC, partner = true, frames = F, note = "Training Room" },
  under_lake = { target = 0x07B58A, partner = true, frames = F, note = "Under the Lake" },
  basement_lab = { target = 0x07BD96, partner = true, frames = F, note = "Basement Lab" },
  dragon_spring = { target = 0x07C778, partner = true, frames = F, note = "りゅうじんのいずみ" },
  abyss = { target = 0x07CF6C, partner = true, frames = F, note = "Cave of Abyss" },
}
