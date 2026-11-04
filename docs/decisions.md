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
