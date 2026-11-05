# Legendz: Yomigaeru Shiren no Shima English translation

Unofficial English fan translation of **Legendz: Yomigaeru Shiren no Shima** (Game Boy Advance, Bandai, 2004): the
source text and tools that build the patch.

**Just want to play?** Download the patch from [Releases](../../releases) and follow its README. This repository holds
no game data you can play; you need your own dump of the Japanese game.

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
helps most.

## Translation status

| Part | Status |
|---|---|
| Dialogue, story, Soul Doll talk, Auto-Quest diary | Translated |
| Menus, items, skills, cards, battle and system messages | Translated |
| Title subtitle, menus and banners drawn as graphics | Translated (the stylised レジェンズ logo is kept: no official English logo) |
| Name entry | Translated |
| Credits roll | Translated |
| Soul Doll adapter | Not needed: the patch includes a virtual doll |

Known issues: see [Issues](../../issues).

## What's here

| Path | What it is |
|---|---|
| `script/` | Every text block: original Japanese and English. Translation fixes go here. |
| `glossary.md` | Binding names, terms and style rules. |
| `tools/` | Python build chain: extract, insert, lint, release. |
| `tests/` | pytest suite (ROM-dependent tests skip when the ROM is absent). |
| `docs/re/` | Reverse-engineering notes. |
| `docs/decisions.md`, `docs/status.md` | Rulings with their reasons; current progress and open bugs. |
| `docs/fonts.md` | Fonts used and their licences. |
| `AGENTS.md` | Instructions for coding agents (`CLAUDE.md` points to it). |
| `.claude/agents/` | Subagent types (translator, reviewer, visual QA, playtester) with only the tools each needs. |

## Build your own patched ROM

Needs Python 3.12+ and your own dump of the Japanese game.

```sh
git clone https://github.com/minhnhattonthat/legions-yomigaeru-shiren-no-shima-en
cd legions-yomigaeru-shiren-no-shima-en
# copy your dump to: rom/Legions - Yomigaeru Shiren no Shima (Japan).gba
#   (8,388,608 bytes, SHA-1 ff1e05a2fa70933dcf58a8be4f82fa289647c28a; the build refuses any other dump, see rom.sha1)
python -X utf8 build.py                                # -> build/legendz_en.gba
python -X utf8 tools/check.py                          # tests + text lint
python -X utf8 tools/release.py                        # every gate, then release/*.zip (patch + README)
```

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

## Licence

Tools and English translation: MIT. The original Japanese text in `script/` is Bandai's and is included only so
the translation can be checked against it. Legendz: Yomigaeru Shiren no Shima is (c) Wiz / Bandai; this project is not affiliated with them.
Do not share patched ROMs.

The translation was made with extensive AI assistance (Claude by Anthropic). Corrections are very welcome.
