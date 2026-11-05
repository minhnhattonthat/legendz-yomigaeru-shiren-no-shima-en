# Glossary - Legendz: Yomigaeru Shiren no Shima

Binding for every translator and reviewer. Agents propose additions in reports; only the controller edits this file. `tools/batches.py lint` enforces the tables: a katakana term in the Japanese must show its EN form, and an Avoid word fails.

## Rulings (asked of the user once; options and reasons in docs/decisions.md)
- Honorifics: kept, hyphenated (Johannes-san). Name order: Western (given name first).
- Romanisation source: official English names where they exist, else an earlier fan patch (none found), else Hepburn without macrons.
- Credits: English.
- Register / flavour: a light kids' anime register, playful and quick: contractions, tildes and ♪ where the Japanese has them. Sound effects: asterisks in dialogue (*Slump*...); no sound effect text in battle lines.
- Abbreviations: full names and terms everywhere, prefer engine changes over shortening. The game's own short forms (CBドラゴン, Gスコーピオン) stay short: C.B.Dragon, G.Scorpion.
- Series name: Legendz (レジェンズ), the spelling in the game's header and copyright line.

## Style rules
- Punctuation map: 「」 -> "...", 『』 -> '...', ・・・ and ： in doll text -> ..., ！？ -> !?, ‼ -> !!, ⁉ -> !?, … -> ... (three dots, the font's … is for the name grid).
- Voices: docs/style-reference.md. Story: docs/synopsis.md.
- ゾクセイ/ぞくせい is "element" everywhere ("Fire element", "Earth type" only where English wants it), to match Shift Element and Element Power.
- ぼうけん: "adventure" in the story's Live RPG, "quest" in Auto-Quest: spot lists, the partner's diary lines, doll prompts.
- A sprite line is at most 21 words (pairs of letters count as one): tools/batches.py checks it.
- The 8 tablets are one sentence in order: "The crag above / the giant dragon's / very heart, / when it shakes the land, / the waters barring / your way shall vanish, / and a new labyrinth / shall reveal its form."

## Characters
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| シュウ | Shu | | official: Shuzo "Shu" Matsutani. Halca-sensei's pupil, the anime's lead | |
| メグ | Meg | | official: Meg Sprinkle | |
| マック | Mac | | official: Mike "Mac" McField; ends lines "y'know" | |
| ディーノ | Dino | | official: Dino Sparks. Girls call him Dino-sama | |
| ハルカ | Halca | | official: Halca Hepburn; "Halca-sensei" | Haruka |
| サスケ | Sasuke | | official: Sasuke Matsutani, Shu's dad | |
| シロン | Shiron | | official; "Gaga" speech with a parenthesised gloss | |
| ランシーン | Ranshiin | | official | |
| アリサ | Arisa | | rival, heir of the Saga's heroes | |
| ヒカル | Hikaru | | refers to herself by name; "Hikaru-chan" | |
| リュウイチロウ | Ryuichiro | | Saga Commander; "Ryuichiro-san", "-sama" from girls | |
| レイジロウ | Reijiro | | Saga Commander | |
| ジョニー | Johnny | | Evil Saga Commander; "Johnny the Gale" | |
| アンディー | Andy | | Evil Saga Commander; "HEY♪", "OH~", "YOU" | |
| ナギサ | Nagisa | | Saga Commander | |
| カンナ | Kanna | | Saga Commander | |
| キリコ | Kiriko | | Saga Commander | |
| そうむ | - | | Soumu, BB's aide (the job title used as a name) | |
| グリフィン | Griffin | | Lord of Wind; speaks formally | |
| ティアマット | Tiamat | | | |
| ヘキサドラゴン | Hexadragon | | the player's partner; ボク, cheerful, thinks of food | Hexa Dragon |
| プリンセス | Princess | | Live RPG role | |
| だいまおう | - | | Demon King, Live RPG role | |

## Places
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| レジェンズパーク | Legendz Park | | | |
| レジェンズタウン | Legendz Town | | "Town" alone in dialogue | |
| ダークテンプル | Dark Temple | | | |
| りゅうのつばさ | - | | Dragon's Wing; りゅうのせなか Dragon's Back; つばさのしま Isle of Wings; シレンのしま Isle of Trials | |

## Items / skills / terms
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| ソウルドール | Soul Doll | | "doll" alone in dialogue is fine (ドール) | |
| タリスポッド | Talispod | | | |
| タリスダム | Talisdam | | ダム alone: "Dam" | |
| ダムパーツ | Dam Part | | the 3 pieces that build the Talisdam | |
| リボーン | Reborn | | verb and noun: "try to reborn your Soul Doll" | |
| サーガ | Saga | | a Legendz's human partner | |
| サーガコマンド | Saga Commander | | あくのサーガコマンド: Evil Saga Commander | |
| サーガバトル | Saga Battle | | | |
| サーガ・トーナメント | Saga Tournament | | | |
| シフトエレメント | Shift Element | | シフトE on screen: "Shift E" | |
| エレメントパワー | Element Power | | | |
| エレメントコア | Element Core | | | |
| レンタルドール | Rental Doll | | | |
| レンタルショップ | Rental Shop | | | |
| パスチェック | - | | "pass check", checked at INFO | |
| もんしょう | - | | "Crest", "Crest of Fire/Earth/Wind/Water/Light/Dark" | |
| しれん | - | | "Trial"; さいしゅうしれん "final trial" | |
| せきばん | - | | "tablet" | |
| かくしイベント | - | | "hidden event" | |
| オートぼうけん | - | | "Auto-Quest"; ぼうけんスポット "Quest Spot" | |
| ライブRPG | Live RPG | | | |
| マヒ | - | | "Paralysis Cure", "Paralysis" (label), "is paralyzed", "paralysis wore off" | Numb |
| こんらん | - | | "Confuse Cure" (64 px item slot; Confusion Cure is 66), "Confusion" (label), "is confused", "inflicts confusion" | Daze |
| せきか | - | | "Petrify Cure", "Petrify" (label), "is petrified", "is no longer petrified" | |
| ぞくせい | - | | Fire, Earth, Wind, Water, Light, Dark; むぞくせい Null | |
| しゃちょう | - | | "Boss", DWC's president, every line | Mr. President |
| ぶちょう | - | | "Chief", BB's title | |
| オサ | - | | オサさま "Elder" | |

## Decisions from earlier batches
- b024 Quest Spot names: free-form short names, 64 px at most: see `script/adventure.json`.
- b024 name entry grid: lower case in the kana columns, upper case in the Latin column; digits and symbols stay put. One word a cell (`insert.SINGLE_WORDS`).
- b019 `45BDEA`, `45BDF0`, `45BDFE`: drawn by length (table `0x7F7F30`), so padded with spaces to exactly 3, 7 and 7 words.
- b024 `440CF8` いくつ？ -> Qty? (32 px measured).
- b016 ライブRPG `Live RPG`: one word order, never "RPG Live".
- Phase 7 fit: やめる is `Back` (24 px box on the auto-quest menu, `Cancel` is 28), ●やめる `●Back` (32 px rental menu). サポート as the Main Role value is `Assist` (32 px box): growing the box to fit `Support` drew over the Main Role label (seen in `debug_battle_record`). The skill term サポート stays `Support` elsewhere.
- Flagged abbreviation (D9): まぼうぎょ is `M.Def` in the 64 px slots only (`M.Def Up`, `M.Def Focus`, `M.Def Tonic`: `Magic Def Tonic` is 69 px). Everywhere with room: `Magic Defense`.
- Review: ぼうぎょUP is `Defense Up` (the stat, as in the item text); ～ぼうぎょ resists and とっか/マスター are `Guard` (Earth Guard, Guard Focus, Guard Master).
- グランドデスサイズ `GrandDeathscythe` (80 px; with the space it's 83, the slot is measured), Gデスサイズ `G.Deathscythe`. Nothing cut, no abbreviation beyond the game's own G.
- Phase 7 rephrasings where a label's box is measured and can't grow: ミチのレジェンズ `Unknown` (name fields, w=8 everywhere), ほけつ `Bench` (w=4), いまのじかん `Time now`, いくつもたせる？ `How many?`, ぼうけんする `Set out`.
- Review: American spelling (favorite). Capitalised terms: Saga Battle, Rental Doll. ドラゴンのもよう is a dragon `design`, not a crest (Crest is もんしょう). カムバックアンドリ・ボーン: `Come back and Reborn!`.
- Names used in the script: エレメンタルレギオン Elemental Legion, りゅうじんのいずみ Dragon Fountain, たいまのひせき Banish Stone, ヴォルケーノキングドラゴン Volcano King Dragon.
