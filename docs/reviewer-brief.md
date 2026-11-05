# Translation reviewer brief - Legendz: Yomigaeru Shiren no Shima (GBA)

You review one batch of a JP->English fan translation. Read-only: no edits, no git, no subagents.
Mechanical validity (ids, control codes, encodable characters, width, stub last lines) is already enforced by the
check tool - judge translation quality. Return the report as your final message; the controller saves it.

## Inputs (paths in your dispatch)
- Pairs file: every translated entry as `>> id | speaker | JP` then `EN` on the next line, with context lines (no `>>`) around them. Read ALL of it, in passes if large. ` / ` is a row break in the 2-row box, and the Japanese often splits one sentence across 2 consecutive ids: judge the pair, not the single string.
- `glossary.md` (rulings at the top), `docs/style-reference.md`, `docs/synopsis.md`.

## Judge
- Accuracy: mistranslation, omission, addition, wrong speaker or addressee, reversed meaning. Quote the JP and say what it means.
- Consistency: glossary names/terms exactly; honorific relationships stable within a scene; voice matches the style reference.
- Things players and users caught that reviewers missed: jokes/wordplay losing their punch; ordinal suffix after a variable ("1th"); abbreviated names or terms (unless the glossary rulings allow them); stock phrases that read awkwardly in English.
- Voice: each speaker against their row in the style reference. Speech quirks and register must come through, not be normalised into neutral prose. Mac ends lines ", y'know". Goblins ", gob". Blazedragon kin ", piko". Guardians archaic, no contractions.
- Variables: `[FFEE]` is the player's name, `[FFE5]`/`[FFEC]` a Legendz nickname, `[FFEF]` an item, `[FFC5]` a skill, `[FFED]`/`[FFF2]` another player, `[FFC4]` a number. They must read as such in English.
- Naturalness: would a fan-translation reader stumble?

## Don't flag
- Line length: the check tool enforces it. Any fix you suggest must be about as short as the line it replaces (2 rows of 30 characters a row at most).
- Trailing ~ and ♪: they are in the Japanese.
- Text in `.` or fixed labels: width is measured.
- "Rraaaah!! / Me ..." grammar: that doll's voice on purpose.

## Report
### Issues
#### Critical (meaning reversed, broken placeholder grammar, wrong speaker)
#### Important (clear mistranslation, glossary inconsistency, abbreviation, a character's voice flattened: quirk, register or emotional beat lost, joke dead)
#### Minor (style - these are deferred to one polish pass)
Each: `id - JP gist - problem - suggested EN`.
### Assessment
Approved | Needs fixes - one sentence why.
