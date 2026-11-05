# Decisions

The user's rulings on scope, style and trade-offs, newest last. Read before asking the user anything; if a later
decision replaces one, mark the old one "replaced by D<n>" instead of deleting it. Binding term spellings live in
`glossary.md`; this file holds the why.

| # | Date | Question | Options offered | Decision and reason |
|---|---|---|---|---|
| D1 | 2026-11-05 | Honorifics and name order | keep (-san), drop; JP or Western order | Keep honorifics; Western name order (given name first). Owner's standing answer for one-shot runs. |
| D2 | 2026-11-05 | Romanization source for names | official art, earlier patch, Hepburn | Official English names where they exist, else an earlier fan patch, else Hepburn without macrons. Owner's standing answer. No earlier fan patch was found (see `docs/re/README.md`). |
| D3 | 2026-11-05 | Credits | stay Japanese, translate | English. Owner's standing answer. |
| D4 | 2026-11-05 | Abbreviations | engine work first (default), abbreviate | Skill default: full names and terms, engine work first; abbreviate only as a flagged last resort. |
| D5 | 2026-11-05 | Graphics text left in Japanese | none (default), list | Translate all of it (titles, menus, banners, cards); keep the original Japanese logo only if it has no official English version. Owner's standing answer. |
| D6 | 2026-11-05 | Specs and plans | need approval, pre-approved | Pre-approved; keep going through checkpoints. Owner's standing answer. |
| D7 | 2026-11-05 | Existing saves, memory cards, savestates | user supplies, none | None provided; build the debug tool as usual. Owner's standing answer. |
| D8 | 2026-11-05 | Soul Doll adapter gate | leave the gate, virtual doll in the patch | Virtual doll, per the default in `status.md` ("if phase 2 finds it blocks progress, the patch includes a virtual doll"), which the owner's pre-approval covers. Phase 2 verified the gate is hard (`docs/re/doll.md`). Which dolls to offer is still open. |
| D9 | 2026-11-05 | `M.Def` in the 64 px item and status slots (D4's flagged last resort) | grow the item list, abbreviate | Agent's default under the pre-approved run, owner may overrule. Abbreviate: the list draws 8 rows of w=8 at tile base+6, step 0x10, and the description starts at base+0xAE, so w=10 would need the description and count tiles moved in two renderers (`0x0A7860`, `0x0B7DF4`) and each shop screen. `Magic Defense Up` is 77 px, `Tonic` 89, `Focus` 91: only `Up` would fit even then. |
| D10 | 2026-11-05 | Emulator tours on this shared machine | full parallel, `--jobs 2` with a free-memory floor | `--jobs 2`, stopping under 4 GB free (`regen.py --min-free`), owner approved: other work shares the machine. Moved here from `status.md` (phase 7 review). |
| D11 | 2026-11-05 | Title screen: the stylised レジェンズ logo and its subtitle scroll 甦る試練の島 | redraw the logo, keep it; subtitle `Isle of Trials Reborn`, `Trial Isle Reborn`, `Isle of Trials` | Agent's default under the pre-approved run, owner may overrule. Logo kept: D5 keeps the original logo when there is no official English one, and none was found; "Legendz" is in the copyright line. Subtitle `Trial Isle Reborn`: the scroll's flat middle holds about 70 px, `Isle of Trials Reborn` is 84 px in the English font; 甦る (revived) is kept as "Reborn", the game's own word for calling up a Legend. Other graphics captions that repeat English art beside them (`敵が出現!!` over ENEMY APPEARED, the battlefield kanji under their English names) are cleared, not redrawn. |
