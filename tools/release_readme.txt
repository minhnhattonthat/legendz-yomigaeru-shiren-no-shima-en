Legendz: Yomigaeru Shiren no Shima - English translation v{version}
Game Boy Advance (Bandai, 2004). Unofficial fan translation.

WHAT YOU NEED
- Your own dump of the Japanese cartridge (internal header LEGENDZSHIMA, game code BLJJ). Some sets file it under the
  wrong name "Legions - Yomigaeru Shiren no Shima (Japan)"; the hashes below are what count.
    Size   {o_size} bytes
    CRC32  {o_crc32}
    MD5    {o_md5}
    SHA-1  {o_sha1}
- A BPS patcher: Flips, or RomPatcher.js (https://www.marcrobledo.com/RomPatcher.js/) in a browser.

HOW TO PATCH
Apply {patch} to the Japanese ROM. The result should be:
    Size   {p_size} bytes
    CRC32  {p_crc32}
    SHA-1  {p_sha1}

PLAYING
- Tested in MesenCE 2.2.1. Any accurate GBA emulator or a flash cart should work.
- Start from a fresh boot. Savestates made on the Japanese ROM carry the old code and text: don't load them.
- No Soul Doll adapter needed. The original game needs a Soul Doll on the adapter to start the story; this patch
  includes a virtual doll, so the game passes that check on its own: it reads as a new doll, the game's own Reborn
  runs and you name your partner.

TRANSLATION STATUS
- Story dialogue, NPCs, Soul Doll talk, Auto-Quest diary: English.
- Menus, items, skills, cards, battle messages, system messages: English.
- Graphics with text (title subtitle, menus drawn as pictures, battle banners, name entry): English. The stylised
  レジェンズ logo is kept, as there is no official English logo for this game.
- Credits roll: English.
- Names follow the official English Legendz anime where one exists (Shu, Meg, Mac, Dino...). Honorifics (-san,
  -kun, -sama) are kept.

KNOWN ISSUES
- Five room names differ slightly from the English art the original game already shows above them (for example
  "Isle of Wings" under ISLAND OF WINGS). Deliberate: the names follow the Japanese.
- The credits roll uses the game's own font, so it has no periods or commas.
- Report anything else (untranslated text, typos, text running out of a box, crashes) at
  https://github.com/minhnhattonthat/legendz-yomigaeru-shiren-no-shima-en/issues - a savestate helps most.

CREDITS
Translation, tools and patch: minhnhattonthat. Made with extensive AI assistance (Claude by Anthropic);
corrections are very welcome.
Legendz is (c) Wiz / Bandai. This project is not affiliated with them. Do not ask for or share patched ROMs.
