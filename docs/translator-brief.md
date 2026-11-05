# Translator brief - Legendz: Yomigaeru Shiren no Shima (GBA, 2004)

You translate part of the Japanese script of this Legendz RPG into English for a fan patch. It's a light kids' anime story set in a Live RPG theme park, played as a boy or a girl.
Work only on the batches or lines named in your dispatch, one at a time in the order given, each to a passing check before the next. Do all translation yourself; do not dispatch subagents.

## Read first
1. `docs/style-reference.md` - character voices and paired examples. Match this voice.
2. `glossary.md` - binding names and terms, rulings at the top, and the Decisions list.
3. `docs/synopsis.md` - plot, who is who and the late reveals. Don't give a reveal away early.

## Input: `work/tl/<batch>.tsv`
`id<TAB>speaker<TAB>limit<TAB>flags<TAB>Japanese`. Limit is `156x2`: px a row x rows. `*` marks op 0116, one of 4 personality lines. ` / ` is a row break, ` // ` a new page, which only a script-line string can take (the check says so). Lines are in story order: use neighbours. A sentence is often split over 2 ids: make the pieces read in sequence.

## Output: `work/tl/<batch>.out.tsv`, written with your file-write tool (not a shell heredoc)
`id<TAB>English`, every input id once, same order. The font's characters only (`tools/font_en.py`, `CODES`, `KEEP`): straight quotes, `...`, and the game's own ♪ ★ ●. No tabs, no Japanese or fullwidth characters, no `\uXXXX`. A page with no ` / ` of its own wraps at spaces by itself. `{@N}` pads with spaces to N px on the row; `{yn}` is the yes/no row.

Single fixes after a batch is merged: a file of `id<TAB>English` lines, then `python -X utf8 tools/batches.py fix FILE`. Any copy's id works.

## Validate
`python -X utf8 tools/batches.py check <batch>`, then fix every reported id until it prints OK. `python -X utf8 tools/batches.py fit "row / row" --px 156` measures a row before you write it.

## Style
- Faithful: keep the information and order of ideas; adapt idiom, not meaning. Don't add details the Japanese doesn't state; don't summarise or skip. Adapt wordplay so the joke still lands (no translator notes).
- Keep the speaker audible: every voice's Japanese markers and English devices are in the style reference's table. A line any speaker could have said is a mistake.
- Names and terms exactly as in the glossary. Abbreviations: never to fit (D4). If a line can't fit without losing meaning, keep the meaning and report it as `LONG: id`; the engine gets changed first.
- Honorifics kept and hyphenated, Western name order (D1). Punctuation: 「」 -> "...", 『』 -> '...', ・・・ -> ..., ！？ -> !?, ‼ -> !!.
- Variables and control codes: copy every one exactly. No suffix glued to a variable (write "No. [n]", not "[n]th"), no a/an right before one.
- American spelling.

## Mistakes the reviews caught (don't repeat them)
- **The player can be a girl (`18187C`).** いいヤツ, へんなヤツ and おまえ are neutral: "You best pal ever♪", "You weird one", never "guy". Same for a linked player whose gender is unknown: "That one", "they".
- **A flattened voice is Important, not Minor:** the mermaid's stretched vowels ("soooo", "Pleeease"), the refined girl's "rather", "I must say", the sage's and guardians' no contractions ("I shall", "you have"), Ryuichiro's courtly "You have fine instincts", the flirt doll's "Oh my~", "Tee-hee★", Hikaru's "Shu-kuuun", the brute doll's "Me punch strong!".
- **Honorifics stay on names:** カンナちゃん is "Kanna-chan", not "cute little Kanna". `check` enforces this.
- **Keep the small words that carry sense:** あと is time left ("left:", not elapsed), いいよなー is "must be nice", だらしない is pathetic, not weak.
- **One name for one thing across screens:** しゃちょう is Boss everywhere, マヒ paralysis, こんらん confuse/confusion, せきか petrify. The same screen can show the item and the status.
- **Mac's ", y'know" ends the line.** It's his, so other speakers don't borrow it.
- **Tag questions and stock phrases:** "shall we...?", never "shall you...?". Read a line aloud.

## Consistency
Never edit `glossary.md`. For a recurring name or term not in it, pick a form, use it consistently, and report it.

## Report (reply with only this)
Files written and entry count; then any lines: `NEW TERM: jp -> en`, `UNSURE: id - note`, `LONG: id - note`.
