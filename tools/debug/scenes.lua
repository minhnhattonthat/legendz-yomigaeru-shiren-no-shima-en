-- Scene list for warp.lua. name -> {
--   target = script ROM offset (an 00F2 target, or a line inside one), entrance = [0x03006270], partner = true (Reborn's roster writes),
--   flags = {set}, clear = {clear}, mem = {{addr, value, size}}, doll = true (load virtual_doll.lua),
--   premash = press A for this many frames first, keys = {{frames after premash, "buttons"}}, frames = run length,
--   mash = press A every N frames after keys, every = frames between shots (default frames/12),
--   free = true (clear the flags that lock the field menu and Save), jump = {script line, frames after the warp} (move the room's task there),
--   stop_at_title = true (no warp: stay on the title menu and let keys drive it), save = true (writes the battery; regen.py runs it alone
--   and keeps work/saves/<name>.sav), sav = "name" (regen.py boots with that save), note }
-- Room offsets: tools/scene_scan.py (work/re/scenes.tsv). How the values were found: docs/re/debug.md.
local TOWN = 0x02F924
local F = 2600  -- the title menu is ready near frame 1500; a room is up about 500 frames later
-- Bag slots: id byte then count byte. Tools at 0x02036B18 (0x3B slots), the second tab at 0x02036B94 (0x40 slots, id is item-0x3E8): 0x080D9588.
local BAG = { { 0x02036B18, 0x0501 }, { 0x02036B1A, 0x0502 }, { 0x02036B1C, 0x0503 }, { 0x02036B1E, 0x0504 }, { 0x02036B94, 0x0501 }, { 0x02036B96, 0x0502 } }
return {
  -- Title screens: keys from the title menu, cursor on New Game (grid: continue, card / new game, doll init).
  title = { stop_at_title = true, frames = 1900, note = "title menu" },
  card_mode = { stop_at_title = true, keys = { { 30, "up" }, { 70, "right" }, { 110, "a" } }, frames = 2600, note = "title > カードモード" },
  doll_init = { stop_at_title = true, keys = { { 30, "right" }, { 70, "a" } }, frames = 2600, note = "title > ドールしょきか" },
  continue_empty = { stop_at_title = true, keys = { { 30, "up" }, { 110, "a" } }, frames = 3000, every = 100, note = "title > つづきから with no save" },
  continue_save = { sav = "menu_save", stop_at_title = true, keys = { { 30, "up" }, { 110, "a" }, { 600, "a" }, { 1000, "a" } }, frames = 4000, every = 100, note = "title > つづきから, loading menu_save's save" },
  new_game_overwrite = { sav = "menu_save", stop_at_title = true, keys = { { 30, "a" } }, frames = 3000, every = 100, note = "title > さいしょから with a save: the confirmation" },
  card_mode_in = { stop_at_title = true, keys = { { 30, "up" }, { 70, "right" }, { 110, "a" }, { 800, "a" }, { 1200, "a" }, { 1600, "a" }, { 2000, "right" }, { 2400, "a" } }, frames = 5000, every = 100, note = "title > カードモード, on inside" },
  doll_init_in = { stop_at_title = true, keys = { { 30, "right" }, { 70, "a" }, { 700, "a" }, { 1100, "a" }, { 1500, "a" } }, frames = 4000, every = 100, note = "title > ドールしょきか, on inside" },
  opening = { frames = 5000, target = 0x02483A, mash = 40, note = "new game's opening; stops before the player's name entry" },
  player_name = { frames = 16000, every = 300, target = 0x02483A, mash = 40, note = "new game's opening, mashed on to the player's name entry" },

  -- The doll gate, with and without the virtual doll.
  reborn_crystal = { target = 0x023C4E, frames = F, note = "Small Cave, crystal: the gate (docs/re/doll.md)" },
  reborn_nodoll = { target = 0x023C4E, frames = 7000, premash = 2800, mash = 40,
    keys = { { 0, "start" }, { 250, "a" }, { 550, "a" } }, note = "Small Cave, Reborn with no adapter: the failure lines" },
  reborn_doll = { target = 0x023C4E, doll = true, frames = 7000, premash = 2800, mash = 40,
    keys = { { 0, "start" }, { 250, "a" }, { 550, "a" } }, note = "Small Cave, Reborn with the virtual doll: Legendz appears, its name entry" },

  -- Field menu, from Small Cave (Start doesn't open it in the town room reached this way: see docs/re/debug.md).
  field_menu = { target = 0x023C4E, frames = 5000, premash = 2800, keys = { { 0, "start" } }, note = "field menu" },
  talispod = { target = 0x023C4E, frames = 5400, premash = 2800, keys = { { 0, "start" }, { 250, "a" } }, note = "field menu > Talispod" },
  field_menu_party = { target = TOWN, partner = true, free = true, frames = 3200, every = 150, premash = 1200, keys = { { 0, "start" } }, note = "field menu with a partner, in town" },
  menu_talispod = { target = TOWN, partner = true, free = true, frames = 4600, every = 100, premash = 1200, keys = { { 0, "start" }, { 300, "a" }, { 700, "a" }, { 1100, "a" } }, note = "field menu > Talispod with a partner, two levels in" },
  menu_status_scroll = { target = TOWN, partner = true, free = true, frames = 6000, every = 100, premash = 1200, keys = { { 0, "start" }, { 300, "a" }, { 700, "a" }, { 1100, "a" }, { 1500, "down" }, { 1800, "down" }, { 2100, "down" }, { 2400, "down" }, { 2700, "down" }, { 3000, "down" }, { 3300, "down" }, { 3600, "down" }, { 3900, "right" }, { 4300, "right" }, { 4700, "left" } }, note = "field menu > Talispod with a partner, then its status page's lower rows and next tabs" },
  menu_items = { target = TOWN, partner = true, free = true, mem = BAG, frames = 3800, every = 100, premash = 1200, keys = { { 0, "start" }, { 300, "down" }, { 400, "a" }, { 800, "right" }, { 1100, "right" }, { 1400, "right" } }, note = "field menu > items, with the bag seeded, through its tabs" },
  menu_save = { save = true, target = TOWN, partner = true, free = true, frames = 4600, every = 100, premash = 1200, keys = { { 0, "start" }, { 300, "down" }, { 400, "down" }, { 500, "a" }, { 800, "down" }, { 900, "a" }, { 1300, "a" }, { 1700, "a" } }, note = "field menu > save, confirmed" },
  menu_auto = { target = TOWN, partner = true, free = true, frames = 3800, every = 100, premash = 1200, keys = { { 0, "start" }, { 300, "up" }, { 500, "a" }, { 900, "a" } }, note = "field menu > オートぼうけん" },
  menu_care = { target = TOWN, partner = true, free = true, frames = 3800, every = 100, premash = 1200, keys = { { 0, "start" }, { 300, "down" }, { 400, "down" }, { 500, "down" }, { 600, "a" }, { 1000, "a" } }, note = "field menu > おていれ" },

  -- Battle: 00B5 sets the enemy, 0099 sets main mode 1, task 0 runs the battle (docs/re/script.md).
  battle = { target = 0x02B79E, partner = true, frames = 4200, keys = { { 1200, "a" } }, mash = 45, note = "battle set up by the Rental Shop's script" },
  battle_end = { target = 0x02B79E, partner = true, frames = 20000, every = 200, keys = { { 1200, "a" } }, mash = 45, note = "the same battle, mashed to its end" },
  battle_result = { target = 0x0241C8, partner = true, frames = 4300, every = 20, keys = { { 1200, "a" } }, mash = 45, note = "the first battle's last moments, densely shot" },
  battle_first = { target = 0x0241C8, partner = true, frames = 16000, every = 200, keys = { { 1200, "a" } }, mash = 45, note = "the first battle the story gives: won, for the result screens" },
  boss_fight = { target = 0x0577F4, partner = true, frames = 9000, every = 150, keys = { { 1200, "a" } }, mash = 45, note = "final boss's battle with a level 1 partner: for the loss path" },

  -- Shops: the keeper's script from its first line; mashing A takes the talk and opens the screen.
  shop_screen = { target = 0x029968, partner = true, frames = 4000, keys = { { 1100, "a" } }, mash = 60, note = "shop's buy screen" },
  shop_tabs = { target = 0x029968, partner = true, mem = BAG, frames = 4400, every = 100, keys = { { 700, "a" }, { 760, "a" }, { 820, "a" }, { 880, "a" }, { 1100, "a" }, { 1160, "a" }, { 1220, "a" }, { 1400, "right" }, { 1700, "right" }, { 2000, "right" }, { 2300, "left" } }, note = "shop's tabs, with something to sell" },
  rental_screen = { target = 0x02A092, partner = true, frames = 4000, keys = { { 1100, "a" } }, mash = 60, note = "rental shop's screen" },

  -- Story beats in order: a warp straight to the line, so the room's setup before it doesn't run (docs/re/debug.md, Known limits).
  story_stage2 = { target = 0x03194E, partner = true, frames = 5000, every = 150, keys = { { 1100, "a" } }, mash = 40, note = "stage 2 briefing call, then the stage" },
  story_stage1_clear = { target = TOWN, jump = { 0x031A02, 600 }, partner = true, frames = 5000, every = 150, keys = { { 1100, "a" } }, mash = 40, note = "town saved: end of stage 1" },
  story_stage3 = { target = 0x03DEAE, partner = true, frames = 5000, every = 150, keys = { { 1100, "a" } }, mash = 40, note = "stage 3 briefing call, then the stage" },
  story_rival = { target = 0x057250, partner = true, frames = 5000, every = 150, keys = { { 1100, "a" } }, mash = 40, note = "Nagisa at the lighthouse" },
  story_demon_king = { target = 0x052244, jump = { 0x052428, 600 }, partner = true, frames = 6000, every = 150, keys = { { 1100, "a" } }, mash = 40, note = "Live RPG cleared: the demon king escapes" },
  story_award = { target = 0x06ADAE, jump = { 0x06B2CC, 600 }, partner = true, frames = 6000, every = 150, keys = { { 1100, "a" } }, mash = 40, note = "award ceremony speech" },
  story_tournament = { target = 0x06F674, jump = { 0x06F8C4, 600 }, partner = true, frames = 5000, every = 150, keys = { { 1100, "a" } }, mash = 40, note = "Saga Tournament: round announcements" },
  story_final = { target = 0x06ADAE, jump = { 0x06B396, 600 }, partner = true, frames = 6000, every = 150, keys = { { 1100, "a" } }, mash = 40, note = "Saga Tournament final's introduction" },

  -- Ending: last cutscenes, mashed through (docs/re/script.md).
  ending_ship = { target = 0x02028A, partner = true, frames = 16000, every = 200, keys = { { 1100, "a" } }, mash = 30, note = "homeward ship: last story scene" },
  ending_end = { target = 0x020BA4, partner = true, frames = 17000, every = 200, keys = { { 1200, "a" } }, mash = 200, note = "from the ship's last line through the credits to the PASS screen" },

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
