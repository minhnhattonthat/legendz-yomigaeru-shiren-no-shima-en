# Polish list

Minor findings from the phase 6 review (`work/qa/review/bNNN.md`, read-only reviewers), deferred to one polish pass. Each: `id - JP gist - problem - suggested EN`. Check width with `batches.py fit`, edit `work/tl/bNNN.out.tsv`, merge. Some suggestions may already be fixed by the Important round or a sweep (`pico`, `Saga Battle`, `Rental Doll`, American spelling, `dragon design`): skip those.

## b001

- [x] 2AFF48 / 2B00DA - Bドラゴンバーサクモード / Wドラゴンバーサクモード (B./W. Dragon Berserk Mode) - "Mode" dropped, so the EN is a shortened name the JP doesn't have (glossary ruling: full terms). Likely a width call. Keep it only if the full form doesn't fit - "B.Dragon Berserk Mode" / "W.Dragon Berserk Mode". - **waived: B.Dragon Berserk Mode is 101 px in a 96 px slot**
- [x] 2AFFC6 / 2AFFDA - ウィルオーウィスプ / Wウィスプ (Will-o'-the-wisp) - "Willowisp" is a respelling, and the short form Wウィスプ (W.Wisp) gets the same full EN name. Not wrong, but the short and full names are no longer distinct. Consider "Will-o'-Wisp" if the apostrophe encodes, and "W.Wisp" for 2AFFDA. - **fixed: Will-o'-Wisp / W.Wisp**
- [x] 2B0180 / 2B02A8 - クラウドG / ファイアG - expanded to the full "Cloud Giant" / "Fire Giant", while the other G-forms stay short (G.Scorpion, G.Beetle, G.Crab). This breaks the glossary rule that the game's short forms stay short. The expansion reads better, so keep it, but it is inconsistent - alternatively "Cloud G." / "Fire G.". - **waived: the full names read better and fit**
- [x] 1885BC - りゅうじんのいずみ (Dragon God's Spring) - "Fountain" implies a man-made structure, and 神 (god) is lost. Suggested EN: "Dragon Spring" / "DRAGON SPRING". - **waived: DRAGON FOUNTAIN is the game's own English label (1885D0, D2)**
- [x] 18846A - はくぎんのふうけつ (Platinum Wind Cave) - 風穴 (wind cave) is lost; "White Silver Cave" is loose. Suggested EN: "Platinum Wind Cave" if it fits (the shorter fallback is "Silver Wind Cave"). - **waived: WHITE SILVER CAVE is the game's own English label (18847E, D2)**
- [x] 1886EA - まじゅうのもり (Forest of Magical Beasts) - "Beast Forest" is fine. 魔 (demonic) is dropped; "Monster Forest" would be a bit closer. - **waived: BEAST FOREST is the game's own English label (1886FA, D2)**
- [x] 1882A2 - せんない (inside the ship) - "Aboard Ship" is fine. It differs from the on-screen "INSIDE THE SHIP" in wording only, so not worth changing. - **waived: reviewer's own call, not worth changing**

## b002

- [x] 187872 - しゅぎょうにっき, にがてなツチぞくせい - "its weak Earth type" is awkward, and glossary says "element" - "Diary of days training / with its Saga in its weak / Earth element." - **already fixed (element)**
- [x] 185F7C - むぞくせいに へんか - "Null" alone is cryptic - "Turns the battlefield / elementless." if it fits. - **fixed**
- [x] 185CDE - ふういんじょうたい - "Cures all seals." loses "state" - "Cures all sealed states." - **fixed**
- [x] 185D5E and 1859DE - セットされたレジェンズ - "all set Legendz" reads like "all set" (ready) - "all Legendz in the party" if it fits. - **fixed: in the party / party Legendz**
- [x] 186792 - なぞのクリスタル / なぞのアイテム - "Odd Crystal" vs "A mystery item" are inconsistent - "Mystery Crystal". - **waived: Mystery Crystal is 69 px in 64**
- [x] 186664 - サービスチケット - "Sale Ticket" suggests a sale, but it halves prices - "Discount Ticket". - **waived: Discount Ticket is 68 px in 64**
- [x] 187436 - くものようにかるく ここちよさがにんきの いっぴん - いっぴん is "item/piece", and "gem" reads as jewellery for a shawl - "A popular item, light / as a cloud and so comfy." - **fixed**
- [x] 1873E6 - りゅうおうのつかいで とびかうレジェンズ - drops "Legendz" and "flying" - "Flying Legendz who serve the Dragon King carry it to beat the heat." Shorten to fit. - **fixed**
- [x] 187736 - いがいにひとみしりな - drops いがいに ("unexpectedly") - "Turns an oddly shy / Legendz cool." - **fixed**
- [x] 1875B6 - うみでサーフィンに - drops "at sea" - "They say it's used to surf / the sea more than skate..." - **fixed**
- [x] 1879B4 - けいたいせんぷうき - drops "portable" - "High-tech portable / fan." - **fixed**
- [x] 18781E - カレといっしょの ランチボックス - "him" has no antecedent - "Lunchbox for two, / packed with boiled eggs." - **fixed**
- [x] 187698 - ひみつのバンダナ - "Hush Bandana" changes ひみつ ("secret") for no reason - "Secret Bandana". - **fixed: Spy Bandana (Secret Bandana is 69 px in 64)**
- [x] 1879FE - みてい - "TBD" is an abbreviation - "Undecided" if it fits. - **fixed**
- [x] 186864 - カゼのけっしょう - "wind crystal" in lowercase while the item is "Wind Crystal" - "A Talisdam fitted / with a Wind Crystal." - **fixed**
- [x] 187A06 - げきからドリンク - げき ("extremely") is lost - "Fiery Drink" or "Hot Drink". - **fixed: Fiery Drink**

## b003

- [x] 2A9D08 - ヴォルクバイパー (second spelling of ヴォルクヴァイパー at 2A9CF4) - EN "Volk Bipar" reads as a typo next to "Volk Viper" - "Volk Viper", or "Volk Vyper" if the JP spelling difference must show. - **fixed: Volk Viper**
- [x] 2A7F80 - しばりじょうたいに ならない - "Prevents bind" is clipped - "Prevents binding" - **fixed**
- [x] 2A96C4 / 2A9704 - ムぞくせい (Null element) - "Null skill" drops the element term, though "Fire/Earth skill" follows the same pattern throughout. Consistent, so optional - "Doubles Null-elem. power" only if the element wording matters; otherwise leave it. - **waived: consistent with the Fire/Earth skill pattern**
- [x] 2A85F0 - ピコフレム - "Pico Flem" where the glossary tag for Blazedragon kin is "piko". Only a skill name, so optional - "Piko Flem" - **fixed: Flem is now Flam across the family; Pico kept, the glossary has no piko tag**

## b004

- [x] 45A806 - 『スタート¦にっきみる』 - the 『』 rule maps to '...', but the EN uses "..." - 'Start: Read Diary' - **fixed**
- [x] 44F756 - ウインライトニング - "Win Lightning" reads as a typo for Wind (cf. ウインドダッシュ -> Wind Dash) - "Wind Lightning" - **fixed**
- [x] 44FDF6 - すいしんがん - "Water Gun" looks like a guess, since the JP is not みずでっぽう - re-check the intended word (水神眼 or similar) - **waived: no context names the word; Water Gun kept**
- [x] 44FE24 - かぜのわすれもの (the wind's forgotten thing) - "Keepsake" adds a different sense (形見) - "Wind's Lost Item" - **fixed**
- [x] 44FB08 - さすらいのようじんぼうジスト (wandering bodyguard) - "Guard" loses ようじんぼう - "Wandering Bodyguard Zist" - **fixed**
- [x] 44FB26 - ものしりねこミッチー (knowledgeable cat) - "Know-It-All" is pejorative - "Wise Cat Mitchy" - **fixed**
- [x] 44FC2A - ひねくれものガルゴ (cranky or contrary person) - "Crooked" suggests dishonest - "Cranky Gargo" - **fixed**
- [x] 44FB08 area (したっぱとうぞくロード, 44FAF0) - したっぱ (underling thief) - "Low Thief Lord" is awkward - "Petty Thief Lord" - **fixed**
- [x] 44FC82 - しんかいのてんまケルビル (deep-sea heavenly demon) - "Abyss Imp" loses "deep sea" - "Deep-Sea Imp Kerbil" - **fixed**
- [x] 45A8C0 - ひんしかいすう (times fainted) - "Near-Deaths" is odd for a stat label - "Times KO'd" - **fixed**
- [x] 45A928 - とくい (strong at) - "Good" is vague - "Strong" - **waived: Strong is 29 px in 24**
- [x] 45AE9C / 45AEDA - やま / れいほう (mountain / sacred peak) - Peak/Summit are near-synonyms and lose the distinction - "Mountain" / "Holy Peak" - **waived: Mountain does not fit 16 px**
- [x] 45AE6C - まかい (demon realm) - "Demon" is truncated and unbalanced against "Heaven" - "Netherworld" - **waived: Netherworld does not fit 24 px**
- [x] 45AE30 - むぞくせい (no element) - "Null" - "Neutral" or "No Element", per the element ruling - **waived: glossary rules むぞくせい Null**
- [x] 45AF5E / 45AF6E - マヒ / こんらん - "Numb" / "Daze" are non-standard status names - "Paralysis" / "Confusion" if width allows **fixed: phase 6 review**
- [x] 44FD96 - えいえんりゅうさ (eternal quicksand) - "Eternal Sands" drops the flowing quality - "Eternal Quicksand" - **fixed**

## b005

- [x] 434DE0 - ‼ ending - "?!!" is not a mapped form (‼ -> !!, ⁉ -> !?) - "You rent me?!" - **fixed**
- [x] 1626A2 / 1626E2 - ゾクセイ - "Earth type" / "Wind type"; the glossary prefers "element" everywhere - "Goblins are Earth element!" / "My Legendz is Wind element, so..." if it fits. - **already fixed**
- [x] 163AD8 - レンタルドール - "rental doll" is lower case, but the glossary and 434BFC use "Rental Doll" - "I wanna try a Rental Doll already!" - **already fixed**
- [x] 162D90 - みなみのこじまへにげた - "southern" dropped, though 162C0C and 162D14 say "small southern island" - "Everyone, please chase the goblins who fled south!" - **fixed**
- [x] 1627AA - そうよね…　ゲームなんだから - "He's right..." adds a referent the JP lacks. The girl is agreeing with herself - "Right... It's a game. / I shouldn't be scared." - **fixed**
- [x] 1639A6 - オレばっか　ねらってきやがって - "all came after me" loses "only me" - "They only ever go after me..." - **fixed**
- [x] 161D6A - すごいおとだったね - "awful noise" adds a negative tone - "What a loud noise." - **fixed**
- [x] 1634E8 - つぎからは　がんばってくれ - "Try harder" sounds scolding for a friendly staffer - "Do your best from here on!" - **fixed**
- [x] 163302 - "my Legendz's Power" is awkward - "...my Legendz got stronger!" if it fits. - **fixed**

## b006

- [x] 165912 - Meg "もー　どうしてアンタたちは / いつも　そうなのよ！" - "Geez" is Shu's word; Meg's device is "Honestly" - "Honestly, why are you two always like this!" - **fixed**
- [x] 164B5E / 164B98 - clerk "だいじなショップの / にもつをー　ゴブリンにー…", then Player "…とられたから" - the pair reads awkwardly: "package was... by a goblin..." then "...stolen" - "the shop's important / package got... a goblin...", keeping "...stolen" on the next line. - **fixed: ...stole it on the player's line**
- [x] 1642E6 - "Legendz here do / Reborn properly" - clunky - "the Legendz here Reborn just fine..." - **fixed**
- [x] 165E76 - がきだいしょう "あのさー" - "Y'know" is Mac's tic, and a random kid takes it up - "Hey, what's that Talisdam the / guy just talked about?" - **fixed**
- [x] 1654D2 - Croc "オレさまの　オヤツ" - the "Oresama" swagger is flattened to "my snack"; a tone nit, optional - "you're my snack, y'know, / 'cause I'm great!" or leave as is. - **waived: optional tone nit**
- [x] 164E86 - "もってきて　くれたら　おれいを / するから　よろしくたのむよ" - "so please!" is stilted - "I'll reward you for them, so / I'm counting on you!" - **fixed**
- [x] 165228 - Mermaid "アラララッ！？" - the stretched-vowel voice is lost - "Ohhh my!?" **fixed: phase 6 review**
- [x] 16588A - Player "ワニくん" - "Mr. Croc" is the worker's ダンナ; the player's くん is friendlier - "Croc, is it okay if I look at the / door in back?" - **waived: D1 keeps honorifics**

## b007

- [x] 166B9C - BB: きいてのとおりよ means "just as you heard (the order)". "You heard her!" assumes Soumu's gender and sounds like it refers to a person. Suggest "You heard the orders!" - **fixed**
- [x] 166DA8 - てんいん: "こうたいのうりこさん" is one replacement saleswoman. "Salespeople" is plural, but 166E24 says "she". Suggest "The replacement saleswoman came, / what a reliiief." - **fixed**
- [x] 167816 - Player: "これもイベントなんだよね！" ends "right!" where it is a tag question. Suggest "...this is an event too, right?" - **fixed**
- [x] 167C3C - さぎょういん: "That oughtn't be" is stiff for a rough-talking worker. Suggest "That shouldn't happen, but..." - **fixed**
- [x] 168882 - Wyvern/Mermaid: "す・て・き・♪" is spelled out syllable by syllable, as 168946's "キ・モ・チ・" is, but "dree-ee-eeamy" breaks the syllable beat. Suggest "Darling, you're so dre-e-amy♪", or drop the stretch and write "Darling, you're so dream-y♪". - **fixed**
- [x] 168C88 - つっこみガール: the JP says "DMC", and the EN normalises it to "DWC". This is fine if intended. Check whether it is a JP typo or a deliberate rival-company gag. - **fixed: DMC kept, a rival company's spy copying the park, not DWC**
- [x] 1687BE - Werewolf: "Sorry to keep you, honey♪" lacks "waiting". Suggest "Sorry I'm late, honey♪ Is that / nasty wall bugging you again?" - **fixed**
- [x] 168C0C - おじょうさま: "あこがれちゃいます" means she is swooning or envious. "I just dream of it" is odd. Suggest "It just makes me swoon♪" - **fixed**

## b008

- [x] 16985A, 16A242 - パークのイベント - lowercase "park event", but the synopsis and glossary treat Legendz Park as a proper noun - "Is this really a Park event?" - **fixed: Park event**
- [x] 16B9AE - おかししている (shop clerk) - "looooaning" reads oddly; the stretch lands on the wrong sound - "Umm, we're only loaaaning that out / as a rental doll, though..." - **fixed**
- [x] 1698FE-169AB8 - the mermaid's run of lines (のよ, カレったら, ダーリン) - flirty and girlish but fairly flat; there is no stretched-vowel or "Oh my~" device, as the style reference's Mermaid and flirt rows call for - optional, e.g. 1698FE "Listen to this! He's soooo awful!" **fixed: phase 6 review**
- [x] 16A0B6 - ぶじ みとめられた (Arisa) - "safely" is dropped; the line is fine otherwise - optional "The Wind Messenger accepted you, safe and sound." - **waived: optional**

## b009

- [x] Many ids - サーガバトル - the glossary term is "Saga Battle", but the batch uses lowercase "Saga battle" throughout (16BD02, 16BE1C, 16BF2A, 16D808, 16DB26, 16DB66, 16E096). The lowercase form is internally consistent, so decide once. Same for "rental doll" versus "Rental Doll". - **already fixed: Saga Battle capitalised throughout**
- [x] 16C254 - シュウ, イイヤツだな - "really good guy" is wrong when the player is a girl. Suggest "really a great person, [FFEE]♪". **fixed: phase 6 review**
- [x] 16D6B4 - シニカルボーイ, かたしてもらうよん - "clean you out" suggests taking money. Suggest "wipe you out". - **fixed**
- [x] 16DFEA - the tablet fragment 「な めいきゅう その」 is partial (letters missing), but the EN is a complete line from the glossary sentence. If the game deliberately shows a partial reading, the gap is lost. Suggest "and a new labyrin..." or "...a new laby..." if it fits. - **waived: every tablet quote gives its glossary chunk whole; kept consistent**
- [x] 16CA3C - 「ホントはいいやつゴブ」 - "actually a nice one" is slightly stiff. Suggest "actually a good human, gob". - **fixed**
- [x] 16DEF6, 16DF30 - おじょうさま - the refined register (〜のよね, 〜かしら) comes out neutral. Suggest "Cure All is handy, but rather pricey, isn't it...". **fixed: phase 6 review**

## b010

- [x] 16E2C4 - Johnny's "そうだろう！" - "Ain't it!" on its own is cryptic - "Cool, ain't it! Be sure and / remember the name!" - **fixed**
- [x] 16E6B0 - Arisa's "めざわりだわ" - "You disgust me" is too strong; the JP means "you're an eyesore/in my way" - "You're in my way!!" - **fixed**
- [x] 16E8D4 - Arisa's "でなおして" - this is "come back again later", not "start over" - "I have to go regroup, so..." - **fixed**
- [x] 16EBDA - Player's "キミは もしかして…" - "もしかして" (could it be you) is lost - "Could you be...?" - **fixed**
- [x] 16F03A - 14A0's "かんりにんです" - a contraction in a formal servant's voice that otherwise has none ("I have been awaiting") - "I am the caretaker of this cave. I will / now tell you about..." **fixed: phase 6 review**
- [x] 16F0B6, 16F0F8 - 14A0's "しかくのあるもの" - "the right" reads oddly; しかく means qualification - "Only those qualified can walk on the water here." / "if one without qualification enters" - **fixed**
- [x] 16F2E4 - 1522's "シシツはありそうだわ" - "it seems to have the makings" has an unclear "it" - "this one seems to have the makings." - **fixed**
- [x] 16F320 - 1522's "みせてもらうとしましょ…？" - "shall you...?" is ungrammatical - "Now then, let's see your strength as a / Saga, shall we...?" **fixed: phase 6 review**
- [x] 16F396 - Chimera's "いざ しょうぶっ！" - "Have at thee!" breaks the style reference, which avoids "thou/thee" - "Have at you!" - **fixed**
- [x] 16F3E4 - 14A0's "あのかたの ちをひかれる おかた" - "that one's blood" is clumsy - "Just what I'd expect of one who carries / that person's blood..." - **fixed**
- [x] 16FA8E - Player's "ドラゴンのもよう" - もよう is a pattern or design, and "crest" collides with the glossary term Crest (もんしょう) - "This door has a dragon design on / it..." - **already fixed**
- [x] 170896 - Kanna's "カンナちゃん ですわよん" - "cute little Kanna" adds words and drops -chan; the glossary keeps honorifics - "Kanna-chan here♪" **fixed: phase 6 review**
- [x] 16EF66 - Clerk's "けんじゃのおみせへー" - the stretched vowel is lost, though the next line keeps it ("elsewheeere") - "Welcoooome to the Sage's Shop." **fixed: phase 6 review**

## b011

- [x] 172816 - ドワーフ "コケーーーーーッ！！", an angry squawk (the player answers "やっぱりおこった"). "Cock-a-doooodle" is a rooster crow, not an angry waking-up shriek - "Bwaaawk!!" or "Cluuuuck!!" - **fixed**
- [x] 171A74 - おじょうさま "でしたわ", ladylike ending lost - "...talking even more strangely than usual, I must say." **fixed: phase 6 review**
- [x] 1721F6 - おじょうさま "さっそくですけど… ワタシとショウブいたしませんか！" - "shall we have a match!" is an awkward question ending in "!", and the "with me" is lost - "Pardon me, but... would you care to match with me!" - **fixed**
- [x] 1710A0 - キリコ "いっきに…って アララ！？" - "wipe you all..." is awkward and アララ is flattened - "I'll finish you off in one... eep!?" **fixed: phase 6 review**
- [x] 171F98 - おにいさん "たにのおくに すすめるな！" (we can go deeper into the valley) - "open up the valley" is vague - "All right, this hammer smashes the rock, so we can go deeper into the valley!" - **fixed**
- [x] 172642 - "すごそうなの" (looks formidable) - "looks amazing" is off in a scary-sleeping-monster context - "Whoa... There it is, and it looks tough..." - **fixed**
- [x] 172AE0 - ツチのはどう (Earth's pulse/energy) - "Earth's waves" reads like ocean waves - "Earth's energy" - **fixed**
- [x] 170CAC - おっと…いけない！ (Oops, almost forgot!) - "That's right!" loses the "forgot" sense - "Oops... Almost forgot! One more Saga / Commander is..." - **fixed**
- [x] 1713CE - 「サーガのチ」のチカラ (the power of Saga blood) - "Saga blood" drops チカラ - "Is that the power of "Saga blood" too...?" **fixed: phase 6 review**
- [x] 171940/17197C - つっこみガール "デレデレしてたの～！" (was totally goo-goo) - the excited tilde and the split sentence are muddled by the ellipsis on row 2 - "...He was all dopey about it~!" / "It was kinda gross to watch." - **fixed**
- [x] 1713CE, 171490, 171412 etc. - sage #1464 uses contractions ("aren't", "I'll", "I'd") while ワシ/おヌシ/〜だぞ is an elderly archaic voice. Consider one pass of de-contracting if it fits, e.g. "Quick on the uptake, are you not." **fixed: phase 6 review**
- [x] 172C46 and 172C8C - #1414 sage "まちかねたぞ… みごとにはばたいてみせよ！" is archaic (〜せよ), but the EN has "I've" - "I have waited long, Saga chick..." if it fits. **fixed: phase 6 review**

## b012

- [x] 1732E4/173368 chain, 173390/1733CC - 1733CC "…むかったらしい！" - らしい hedge (apparently) lost; the Cool Doll fragment dangles as its own box - "...the Dragon Fountain, apparently, / to summon..." (optional) - **fixed**
- [x] 173882 - ナギサ "でもザンネンね～ ここでいちばんさいしょに まけてしまうんだもの" - subject ambiguous in JP; "You're the very first to lose here" is a guess, check whether this is pre-battle taunt (OK) or her own loss line (then "I'm the first to lose here!") - **waived: a pre-battle taunt; the EN reading holds**
- [x] 173844 - "あなたがいちばんノリよ" - "most fun yet" misses "you've got the best vibe/groove so far" - "You've got the best groove yet♪" - **fixed**
- [x] 1739C6 - アンディー "なんてこったーい" - style ref gives "Good grief"; "What a bummer" is fine but drops the stock line - "OH~ Good grief♪" **fixed: phase 6 review**
- [x] 17374C/173784 - バカンスレディ - "cheer hard" then "cheer my hardest for him" repeats; "for him" is filler - "To have Dino-sama avenge me, / I've got to cheer my hardest!" - **fixed**
- [x] 174066/1740A8 - かの りゅうおう (singular, "that famed Dragon King") - rendered plural "Dragon Kings" - "...to rival even the / legendary Dragon King!!" - **fixed**
- [x] 174354 - "このいりぐちの おくから" - "from deep past this entrance" awkward - "from deep inside this entrance...!" - **fixed**
- [x] 174CB6 - "「しかくしゃ」" (one qualified) - '"One with the right"' reads awkward - '"The Qualified One" has appeared...' - **fixed**
- [x] 1750CE - ドラゴンのもよう (pattern/design) - "dragon crest" clashes with the Crest (もんしょう) term - "dragon emblem" - **already fixed (design)**
- [x] 175112 - ホノオのはどう (surge of flame) - "Flame's waves" odd - "I can feel a surge of flame / coming from here..." - **fixed**
- [x] 1747B2 - "オモイシルガイイ" (learn it well) - "YOU WILL KNOW IT" is weak - "LEARN IT WELL" - **fixed**
- [x] 17482A - #14BE "セッカク… ガンバッタノニ" (all that effort, and yet) - "after all that" regret reduced - "ME... PRACTICED LINES... / WORKED SO HARD..." - **fixed**
- [x] 17595E - おねえさん "INFOでよばれたみんな" - "Is everyone called at INFO here?" reads passive/odd - "Okaaay! Is everybody INFO / called here yet?" - **fixed**
- [x] 175916 - Princess "INFOのおにいさん" - "INFO guy" too casual for her わたくし register - "the young man at INFO" - **fixed**
- [x] Glossary suggestion: add エレメンタルレギオン = Elemental Legion, りゅうじんのいずみ = Dragon Fountain, たいまのひせき = Banish Stone, ヴォルケーノキングドラゴン = Volcano King Dragon. - **already in glossary.md (line 100)**

## b013

- [x] 176436 - Arisa: これはワタシの… リソウをかなえてくれる レジェンズよ - "my... Legendz that makes my ideal come true" misreads the pause. ワタシの modifies リソウ, so "my" is doubled. Suggested EN: "This is the Legendz that will... / make my ideal come true..." - **fixed**
- [x] 1768BE - Arisa: だれにも まけない… [FFEE]にも まけない - "Power to lose to no one" is clunky and adds "Power". Suggested EN: "I won't lose to anyone... / Not even to [FFEE]..." - **fixed**
- [x] 1767A4 - Tiamat: なにものにも まけぬ きょうだいなチカラ - "Power that loses to nothing" is a literal stock phrase that reads oddly. Suggested EN: "Seek my power... Power that / nothing can defeat..." - **fixed**
- [x] 1766C4/176704 - Tiamat: なるのだぞ？ - "you know?" is too casual for the villain. Suggested EN: "...someone nobody needs, mark my words." - **fixed**
- [x] 176A44 - Tiamat: そのセイギのココロ - "That just heart" is awkward. Suggested EN: "That heart of justice is a bother." - **fixed**
- [x] 1776F4 - Johnny's catchphrase リ・ボーン - "Re-Born" departs from the glossary's "Reborn". Fine if the stylization is deliberate; otherwise "Come back and Reborn!" - **waived: Johnny's catchphrase, the JP splits it リ・ボーン; the hyphen keeps the stylization**
- [x] 1774BC - Player: ど～りで なまえも にてるとおもった - "No wonder" is lost. Suggested EN: "I see...! No wonder your names are so alike." - **fixed**
- [x] 176BA8 - いいよなー ひょうしょうしきに でれるやつは - "Lucky for those who get to be in the ceremony" has the wrong sense. Suggested EN: "Must be nice for those who get to / go to the ceremony..." **fixed: phase 6 review**
- [x] 178148 - かいぞうして - "remodeling bugs and plants" is odd. Suggested EN: "DWC is modifying bugs and plants..." - **fixed**
- [x] 175CB4 - DWC Boss: いまから…けっしょうせんを おこないたいと おもいます - "...Final...!" drops "hold". Suggested EN: "...hold the Final...!" - **fixed**
- [x] 175D8C/175DC6 - "Who will win..." / "Which Saga will it be!?" repeat each other. Suggested EN: "...Which Saga will take the title / of this memorable 1st Tournament!?" - **fixed: The winner of... / which Saga will it be**
- [x] 1771B0 - Shiron's gloss とっとといくぞ - "Let's get moving." is too mild for the rude gloss. Suggested EN: "(Hey! Move it, we're going!)" - **fixed**
- [x] 176C5E - おしゃれガール: いけてたんだけどなぁ - the regret "but" is lost. Suggested EN: "I'd gotten pretty far, though..." - **fixed**
- [x] 175EB2 - "the counter right of the hotel" is awkward. Suggested EN: "The clerk at the counter to the right of..." - **fixed**

## b014

- [x] 178B56 - Shu panics: "your opponent's that one, over there" (deflecting to the player) - "your opponent's them!" is confusing, and the "them" dodges the boy/girl split - "Wah wah wah, your opponent's / [FFEE]! Over there...!" - **fixed: over there! Over there, no pronoun**
- [x] 17A7CC/17A810 - Player asks why this Saga Battle has them fight the Saga Commanders, not ordinary kids - "Saga battle" breaks the glossary's "Saga Battle", and the "is it not against... but against... that I fight?" syntax is clumsy - "...Why, in this Saga Battle, am I / fighting you Saga Commanders?" plus a short "...not ordinary kids?" tail. - **fixed**
- [x] 178148 - DWC "かいぞう" (modifies) bugs and plants - "remodeling" is a building term - "modifying bugs and plants". - **fixed**
- [x] 179846 - Hexadragon chose you as the heir - "as its heir" suggests the heir is Hexadragon's - "chose you as the Hero's heir..." (if it fits). - **fixed**
- [x] 1792FC - Dino "ちょっと いいかい？" - "Got a moment?" is clipped and casual against his polite, full-sentence style - "Do you have a moment?" - **fixed**
- [x] 17903A - Ryuichiro, courtly - "Anyway, you all leave here right away too" is blunt, and the "too" is awkward - "Anyway, all of you must leave at once, too." - **fixed**
- [x] 17A858 - Ryuichiro - "You've got good instincts" is contracted and casual for the courtly voice - "You have fine instincts..." **fixed: phase 6 review**
- [x] 178916 - Player: "ここには もう いかないほうが" - "I'd better not go there anymore" may read oddly after a scene change - "Maybe I shouldn't come here anymore..." - **fixed**
- [x] 178B8E - Meg: "ワルいけど よろしく！" - "you take this!" is vague - "Sorry, but it's up to you!" - **fixed**
- [x] 178A50 - Hikaru "シュウくんだぁ" - the drawn-out vowel is lost, so the line is flatter than her style row - "It's Shuu-kun! Why are you here?" **fixed: phase 6 review**
- [x] 1798C8/1798FC - Arisa: "to steal Hexadragon... that was my aim..." - fragmented, and "aim" lands oddly - "So I... wanted to steal Hexadragon... / That's why I got close to you..." - **fixed**
- [x] 1795FC/17962A - Player relays Dino's guess ("ないか だって" = "he said maybe you...") - the hedge is dropped, so it reads as a flat claim - "...and maybe got close to me to keep an eye on me..." - **fixed**

## b015

- [x] 17C30A - guardian: たっしゃでな - "Fare thee well" brings in "thee" (the style reference avoids "thou") - "I am in your debt... Fare well!". - **fixed**
- [x] 17C00A/17C04C - Thunderbird: サーガの こうけいしゃとして みとめよう - "heirs to our Saga" adds "our" and reads oddly - "We recognize you as the Saga's / heirs, here and now...". - **fixed**
- [x] 17AAB4 - Hikaru: キタイして ソンしちゃった - "What a waste of hoping" is awkward - "I got my hopes up for nothing...". - **fixed**
- [x] 17ACCA - Arisa: はやくようじを すませて - はやく ("quickly") is dropped - "Please, hurry up and finish what / you have to do, then come back.". - **fixed**
- [x] 17B4E2 - Griffin: よくきたな - "at last" is added, which implies he was impatient - "You have come... All that / remains is to test your power...". - **fixed**
- [x] 17B262/17B2A2 - Griffin: "heroes of old" adds "of old", which is not in the Japanese. The line is acceptable but could be "as the heir of the Saga's heroes...". - **fixed**
- [x] 17CC30 - アニキ rendered "bro" - fine, but "boss" would fit the thug voice better if there is room. - **waived: bro reads fine for アニキ**

## b016

- [x] 17DE54 - それでは どうぞ ごゆっくり おやすみ くださいませ - "Very good." isn't in the JP and sounds stiff - "Then please enjoy / a nice, long rest." - **fixed**
- [x] 17DFF0 - とうてんじまんの ゴージャスな しょうひん - "shop's pride, gorgeous goods" reads awkward - "Please have a look at our / shop's gorgeous, prized goods." - **fixed**
- [x] 17EF9A - タリスポッドコマンドを えらぶと - "command" dropped from Talispod command - "Next, choose the Talispod command / and the Reborn command will" - **fixed**
- [x] 17D13E - いくのを みたのよ！ - "I saw it!" repeats "I saw that dragon" from 17D102 - "go in here! / Aww, I want to chase it, but..." (or "I saw it go in!") - **fixed**
- [x] 17F5E2 - まんぞくしてたら ダメよ - "don't get satisfied with this little" is clumsy - "don't get satisfied with so little." - **fixed**
- [x] 17F3BA - ヘキサドラゴンは アナタが パートナーなんだから - "partner of this Hexadragon" is stiff - "H-hey, you're Hexadragon's / partner, so you have to" - **fixed**
- [x] 17E50A - なんだか ドキドキしてきた - "getting me excited" loses the heartbeat - "My heart's pounding...!" - **fixed**
- [x] 17F7CC - ...いろいろ たのみこんでな - "favours" is British spelling; the rest of the script is American - "favors" - **already fixed**
- [x] 17CF88 - うん ありがとう - "Right, thank you" is slightly off for a kid - "Yeah, thank you...!" - **fixed**
- [x] 17D55A..17D61E - Ryuichiro's lines are plain, not "courtly" per the style row. The JP is plain too (んだ, だよ), so this is just a note. No fix needed. - **waived: reviewer's note, no fix needed**

## b017

- [x] 1801DA - DWC Boss: わがDWCの Legendz Park - "our / DWC's" stacks two possessives and reads clumsy - "Ahem, everyone! Welcome to / DWC's very own Legendz Park!" - **fixed**
- [x] 181062 - Meg: きいてるほうがうんざりする (fed up) - "sickening" is too strong - "...Anyway! I'm sick of hearing / it, so give it a rest." - **fixed**
- [x] 181482 - Shu: べつにさわいでないじゃんなぁ - ", y'know" is Mac's tic, and this line sits right beside Mac's; the style reference says Shu uses it sparingly. It blurs the two voices - "We're not being noisy, geez." - **fixed**
- [x] 181796 - Mac: ボクは… - "Me..." reads like the brute doll's dropped pronoun; Mac says "I" - "I... like kind ones, y'know..." **fixed: phase 6 review**
- [x] 18127A - Halca: そんざいじたいがでんせつ - "are legend itself" is slightly off - "Legendz, true to their name, / are legends in themselves!" - **fixed**
- [x] 180AA4 - Sports Girl: ナチュラルなボケかまさない (don't make a dumb remark so naturally) - "Don't play dumb" misses that the remark was unintentional - "Hey, you! / Don't say that so casually!" (or "Quit deadpanning like that!") **fixed: phase 6 review**
- [x] 180672 - Princess: ストーリーをかんたんにおはなしする - "tell you the story simply" is stiff - "Hello, everyone! I'll give you / a quick rundown of the story," - **fixed**
- [x] 180E9A / 180EDA - Clerk: かいてんのおしらせ (opening notice) - "there'll be an opening notice" is stiff - "there'll be an announcement / when we open. Look forward to it!" - **fixed**
- [x] 17F926 - Dad: ちょうレアがつく - "a Legendz that counts as super rare" is clunky - "That one's a Legendz so rare / it's called 'super rare'!" - **fixed**
- [x] 181DD4 - Shu: いっくぜー - "I'm going to be the first one off" is flat for Shu's swagger - "I'm gonna be the first one off!!" - **fixed**
- [x] 1805CE (unmarked, context only) - Girl host: しゃちょう is "Mr. President" here but "Boss" in 18015A and 1801A0. Make it "Thank you very much, Boss!" **fixed: phase 6 review**

## b018

- [x] 182106 - Player: "クールなカンジが ちょっとカッコいいかも" - "cool, in a cool way" is a clumsy repeat - "So that's Arisa. She's got a cool / vibe that's kind of neat♪" - **fixed**
- [x] 1838E6 / 183926 - Arisa: "…こうけいしゃに なれないワタシなんか" - "A me who can't become heir" is stiff, and the row break lands mid-phrase - "But I didn't want to admit it... Without / being the Saga heroes' heir, I have no reason to exist..." (re-split 1838E6 and 183926 as needed) - **fixed: re-split**
- [x] 18444C - Shiron: "（まったくだぜ！）" - the rude, cocky gloss is flattened to "Exactly!" - "Gagagaga (You said it!)" **fixed: phase 6 review**
- [x] 182658 - cool doll: "フッ…" - the style reference uses "Heh..." for this cool doll, not "Hmph." - "Heh. Inside was... I see. / It seems to be [FFEF]." - **fixed**
- [x] 1827A0 - old-man doll: "こんかいのえもの" - "This time's prize" reads oddly - "This time's catch was [FFEF], it seems." - **fixed**
- [x] 1836A0 - Player: "ティアマットが…　きえていく…" - "Tiamat's... vanishing..." can read as a possessive - "Tiamat... is vanishing... / Arisa! Don't go!!" - **fixed**
- [x] 183BFC - Player: "へいきだよ！" - "That's fine!" is flat for a reassurance - "I don't mind!" - **fixed**
- [x] 184664 - Meg: "そうよね～" - "For sure~" is a bit off - "Tell me about it~" - **fixed**
- [x] 184184 - Griffin: "ワレらが シレンのしまと ともに…" - the subject "We" is lost, so it reads as if Arisa sleeps with the island - "Sleep for now... as we shall, / together with the Isle of Trials..." - **fixed**
- [x] 182D54 - flirt doll: "こんなに わるいわね～♪" - "So much, how kind~♪" misses the "sorry, this is too much" tease - "So much? Oh, you shouldn't~♪" - **fixed**

## b019

- [x] 45D2D6 - ヨロシクね (here "take care of me") - "so hi there!!" is a stock phrase misused and reads oddly - "I'll do my best, so be nice to me!!" - **fixed**
- [x] 45D292 - なにがおきるか　たのしみだなぁ♪ - the excitement ("can't wait") is flattened to "I wonder what'll happen", and "How many years since I've seen outside~" is clumsy - "Been years since I saw outside~ / Can't wait to see what happens♪" - **fixed**
- [x] 45D810 - ボクえらい？ - "Am I good?" - "Aren't I great?" - **fixed**
- [x] 45DDF2 - ほかのコばかり - "other girls" assumes a gender and means the player's other Legendz - "You only call the other ones!" - **fixed**
- [x] 45C028 - キャーーーッ ステキ！！ - style-reference Halca gushes "Kyaa" - "Kyaa, how wonderful!!" - **fixed: Kyaaa**
- [x] 45D690 - よろしくたのむよ！ - "So, if you please!" is stiff - "Let's get along, then!" - **fixed**
- [x] 45CF54 - これでも　いそがしい - "Forgive me, but I am busy" drops これでも ("even so") - "Forgive me, but I am busier than I look." - **fixed**
- [x] 45D01C - ワタシは…りゅうのおう　サーガのみちを　あゆむものよ - "...you who walk the Saga's way" reads as apposition to "I". It is a vocative - "Walker of the Saga's way, I am the dragon king ruling Water..." - **fixed**
- [x] 184D84, 184D90, 184DBE - まひむこう / こんらんむこう / せきかむこう - "No Paralyze" and "No Confuse" are verb forms, and "No Petrify" is also a verb - "No Paralysis" / "No Confusion" if they fit. - **fixed: No Paralysis / No Confusion / No Petrifying**
- [x] 184BEC - しこうのぼうぎょ - "Best Guard" - "Supreme Guard" if it fits. - **waived: Supreme Guard is 65 px in 64**

## b020

- [x] 45FC4C, 45FD06 - "tho" is a casual abbreviation (the brief says to avoid abbreviations) - "though", if the width allows - **fixed**
- [x] 45E718 - ‼‼ is 4 bangs, EN has "!!!" - "Me, [FFEC]!!!!" - **fixed**
- [x] 45ECBE - "[FFC5]ていどなら" is dismissive ("a move as basic as [FFC5]"), but EN "[FFC5]?" is flat - "Heh... A move like [FFC5]? / I can pick that up in an instant." - **fixed: Just [FFC5]? (A move like overflows with a long skill name)**
- [x] 45F066 - "キモチはうれしいけど" = "I'm glad for the thought, but..." - "it's the thought that counts" adds an idiom and sounds sarcastic - "Mmm, I appreciate the thought, but..." - **fixed**
- [x] 45E5FC - "こんかいも せわになるぜ" - "I'm in your care again" is stiff - "Thanks for having me again." - **fixed**
- [x] 45E00C - "So I'll read it, listen close!" is a comma splice, and から is causal - "Okay, I'll read it, so listen close!" - **fixed**
- [x] 45F62A - "[FFC5]を おそわったよ" - "I was taught [FFC5]!!" is stiff for the cheerful doll - "I got taught [FFC5]!!" - **fixed**
- [x] 45F7C2 - "ボクの ぼうけん みてくれる？" - "Will you look at my quest?" reads oddly - "Wanna hear how my quest went?" - **fixed**
- [x] 460432 - ねぶそく = lack of sleep - "I haven't been sleeping lately" - "I haven't been getting / enough sleep lately~" - **fixed**
- [x] 460600 - "I like it pretty well" is stilted - "I kinda like it, though♪" - **fixed**
- [x] 45F26C, 45F2AA, 45F2EA, 45F324, 45F35C, 45F398, 45F3D4, 45F402, 45F43C, 45F476 - quoted option terms: "Finds" here vs the menu label 4602DE "Find Focus", and "shorter 'Time'" is awkward - use "Find" in both places, or "less 'Time'" if the width allows - **fixed: Find, less Time**
- [x] 45FD44, 45FD82, 45FDC4 - あいしょうムシ - "Ignoring affinity" is vague next to the glossary's element terms - "Ignoring matchups" - **fixed**
- [x] 45F95E - the "just / fine" row break is awkward - "I memorized the message / properly, so don't worry♪" - **fixed**

## b021

- [x] 461A6A - brute: オレの パンチは つよいぞ - "My punch is strong!" is neutral, where the other brute lines use "Me" or drop words - "Me punch strong! / Wanna take one?" **fixed: phase 6 review**
- [x] 460A56 - "[FFEE]って たんじゅんだね" - "You're so easy" reads as gullible or loose; the sense is "simple-minded" - "You're so simple, [FFEE]♪" - **fixed**
- [x] 460DBE - "かんじの おおいのは ニガテ" - "tho" is a casual abbreviation - "Too much kanji's not for me, though..." if it fits. - **fixed**
- [x] 461338 - "カワイイだけの オンナだとは" - "a girl who's cute" is clumsy - "Don't think I'm just a / cute girl!" - **fixed**
- [x] 461690 - "どう？ どう？" - "How? How?" is stilted - "Well? Well?" or "What d'you think?" - **fixed**
- [x] 461FC4 - "あたし なかなかやるでしょ♪" - "Not bad, am I" is a broken tag question - "Not bad, huh♪" or "Pretty good, right♪" - **fixed**
- [x] 461ED0, 461F50 - "こんど ちょうせん" - "some time" - "sometime". - **fixed**
- [x] 4623AE - "はっけんすうについては [FFEE]のほうが すすんでる" - "In spots found, [FFEE], you seem to be ahead." is awkward - "As for spots found, you / seem ahead, [FFEE]." - **fixed**
- [x] 462688, 4626B8, 4626EC, 462722, 4627F8, 462828, 46285C, 462892, 46295A, 46298C, 4629C2, 4629F8, 462ACC, 462AFE, 462B34, 462B6C - じかん/ふん - "hr"/"min" are abbreviations, and the glossary ruling asks for full words - "hours"/"minutes" wherever the width gate allows. Not a defect if it can't fit. - **fixed: hours / minutes in all 16**
- [x] 462C54 - "ドールのかしかり" - "swapped dolls" loses the lend/borrow sense - "lent and borrowed dolls with [FFD8] people" if it fits. - **fixed**

## b022

- [x] 463232 - "Lots of friends! You're sloppy/pathetic!" (だらしない) - "You weak" changes the meaning to weak - "Lots of friends! / You pathetic!!" **fixed: phase 6 review**
- [x] 4647B2 - "found as many as [FFE8] spots" - the emphatic も is lost - "They've found as many as / [FFE8] Quest Spots!" - **fixed**
- [x] 4647E6 - "so I'll secretly tell you [FFE7]" - [FFE7] is a spot name and "tell you [FFE7]" reads bare - "So I'll secretly tell you / about [FFE7]♪" - **fixed**
- [x] 46304A - "Despite appearances, they have friends! Fight on!" - "More friends than they look!" is awkward - "Friends, despite their looks! / Fight on, [FFEE]-chan!" - **fixed**
- [x] 4646C4 - "Me don't get it, but it looks amazing" - "they seem great" is ambiguous (the skills are meant) - "Me not really get it, / but looks awesome!!" - **fixed**
- [x] 463498 - "Let's teach them lots!" (ようね, inclusive) - "You should" drops the "let's" feel used in 462CC8 - "Are they kind of laid-back? / Let's teach them lots!" - **fixed**
- [x] 4641A4 - "Probably [FFE3] or so!" (とか) - "or so" lost, so it reads as a firm answer - "Me think [FFE3] or so!" - **fixed**
- [x] 4632CE and 46330A - "Huh? Girl/boy friends?" - "Girl friends" can read as girlfriends, and the bare "[FFDA]!" is clipped - "Huh? Girls? Hmm, [FFDA] / of them! Probably!" - **fixed**
- [x] 465580 - "Well, you figured it'd be about that much, right?" - "is that what you expected? Right?" stacks two questions - "Well, about what you figured, / huh? Right, [FFEE]?" - **fixed**
- [x] 463956, 463ABA, 463C22 and 463D80 - the team's combined max level for the 3 set in the Dam - "top level total for the 3 set in the Dam" is clumsy and repeated across the batch - "Combined max level of the 3 / set in the Dam: [FFE1]!" - **fixed**

## b023

- [x] 4665E2, 466622, 466650 - Flirt doll (あのひとったら, わ): the lines are neutral and carry none of the flirt voice ("Oh my~", "Tee-hee") - suggest "Oh my~, that person has a doll you / don't have, [FFEE]-chan!" in 4665E2. **fixed: phase 6 review**
- [x] 466850 - ヘキサドラゴンが いないんだよ - "There's no Hexadragon!!" could be read as the doll not existing - suggest "They don't even have a Hexadragon!! / Can you believe it!?" - **fixed: They don't have a Hexadragon (even overflows)**
- [x] 4667EE - おぼえさせてるワザ - "skills" is dropped - suggest "These are the skills they've / taught their Hexadragon!" - **fixed**
- [x] 23D098 - ひらめいたみたい / おぼえなきゃ - "New skill! / Reborn to learn it!" drops the speaker's "looks like / I've got to" - suggest "Got a new skill idea! / I'll Reborn to learn it!" - **waived: the sprite ring holds 21 words, the longer line needs 24; reworded within it**
- [x] 23C658, 23C66E - 攻撃手段がない - "has no attack!" - suggest "can't attack!" - **fixed**
- [x] 23C9B2, 23CF9A - 石化が解けた - "is no longer stone!" doesn't match "is petrified" elsewhere - suggest "is no longer petrified!" **fixed: phase 6 review**
- [x] 23CA5E - 瀕死から回復 - 瀕死 is "near death", and "revived" implies a KO - suggest "pulled through!" - **fixed**
- [x] 23CD1E, 23CD7A vs 23CCD2 - 防御 is rendered "Guard" in Focus and Master but "Defense" in Up and in the stat lines - pick one. - **fixed: Defense throughout**
- [x] 23CA72 - 敵レジェンズ "The enemy Legendz" vs "Foe" elsewhere - suggest "Foe fled!" if it fits. - **waived: the full term reads better and fits**
- [x] 466598, 466682 - fine in meaning; "some time" is a filler, optional trim. - **fixed**

## b024

- [x] 4412CA - ぼうけんちゅう あと ふん = "on quest, X min left" - あと (remaining) is dropped, so the number reads as elapsed time - "On quest: In   min" or "On quest:   min left", if width allows. **fixed: phase 6 review**
- [x] 44171A - やみのしんでん - "Temple of Dark" breaks the pattern of its siblings "Light Temple", "White Temple", "Black Temple" - "Dark Shrine" or "Shadow Temple". Not "Dark Temple", which is a glossary place. - **already fixed**
- [x] 4413C0 - やまのふうけつ - "Peak Wind Hole" is clumsy (ふうけつ = wind cave) - "Windy Hollow" or "Wind Cave Peak". - **already fixed**
- [x] 441270 - …くらい = "about / or so" after the clock time - "...ish" is slangy but works. Optionally "About...". - **waived: ...ish reads fine in a 32 px slot**
- [x] 440E42 - おていれ (care / upkeep) - "Polish" is a guess and may mislead - "Care" or "Groom". Check what the screen does. - **fixed: Care (the doll care screen)**
- [x] 44199E - 'Someone has already cleared this place, so in that way, it's safe' - "in that way" is stiff - "so at least it's safe♪". - **fixed**
- [x] 441D2A - ...ておもったらやっぱりだよ！ ("I thought so, and sure enough!") - "...And I knew it!" is a little flat - "...Called it! Here I go~!!". - **fixed**
- [x] 442502 - 'Not for the battle, in another way...' is awkward (meaning: not because of the fight, but for another reason) - "Not the battle, but, uh, for other reasons...". - **fixed**
- [x] 44293C - それならでてこないでほしいよね ("then it shouldn't show up at all") - "Then I wish it wouldn't show up!" is OK; "Then don't show up in the first place!" has more bite. - **fixed**
- [x] 4429D8 - ゴクゴクのんじゃった ("I gulped it down") - "I drank up / big gulps♪" is ungrammatical across the row break - "I gulped / it all down♪". - **fixed**
- [x] 442562 - ぞくせいのチカラ - lowercase "element power" looks like the glossary term Element Power. It is probably intended as the generic sense. If not, capitalise or reword: "any element energy". - **waived: the generic sense is meant, lowercase on purpose**
- [x] 4423E4 - おまたせ！ - "Sorry to keep you!" is slightly apologetic - "Thanks for waiting!". - **fixed**

## b025

- [x] 4432BA - けいけんぶそくだったのかも (past tense: "maybe I lacked experience") - "need more experience" shifts the tense. - `Maybe I lacked experience...` - **fixed**
- [x] 4436AE - レベルはすこしゆうりだな - "favour" is British; the rest of the script is American. - `The level's a little in my favor... / No problem.` - **already fixed**
- [x] 443644 - レベルはともかく - "The level aside" reads stiffly. - `Level aside, / affinity's / on my side.` - **fixed**
- [x] 443A06 - どうどうとしてごリッパだね - "Bold as brass" is idiomatic but leans negative. The JP is a cocky compliment. - `Yo! / Standing tall, I like it! Care for / a match?` - **fixed**
- [x] 443C16 - ニクイね - "How cool" is a bit flat for the cool doll's sly "you're smooth". - `...How smooth♪` - **fixed**
- [x] 445236 - なんでここ⁉ / キャンセルできないのかしら - かしら marks a question, so "!" ends it wrongly. - `Can't I cancel this?!` - **fixed**
- [x] 4452EC - あたしがはじめてクリアする - "be first" is missing the article. - `I'll be the first to clear this place~` - **fixed**
- [x] 443F88 - ようやくおわりにできそうだぜ - "finish" has no object. - `Looks like I can finally wrap this up.` - **fixed**
- [x] 445098, 4450D4, 445142, 4451BE - flirt doll (あたし, わ endings) - Only the "Tee-hee" lines carry the flirt voice. The rest read as neutral. Optional: add "Oh my~" or "Hee~" to a few. **fixed: phase 6 review**

## b026

- [x] 445B8C - "To make this me nervous, you're pretty good!" - "little me" is an addition - "To make / me / nervous, / you're pretty good!" - **fixed: me, of all people**
- [x] 445C20 - きゃ～！いまのウソで～す！ - "I take that back" loses the panicked "that was a lie!" - "Kyaa! That was a lie! / I'm sorry!" - **fixed**
- [x] 445D78 - わりとカワイイボウヤだこと - "What a fairly cute boy" reads stiff - "What a rather cute little boy" - **fixed**
- [x] 445EE0 - ノコノコとでてきちゃった - "came right out" loses ノコノコ (blithely, heedlessly) - "you came strolling right out" - **fixed**
- [x] 445F64 - キホンのとおりならそろそろ - "If the basics hold" is awkward - "If it goes by the basics, then / right about here..." - **fixed**
- [x] 44650A - リフレッシュできたみたい - "Seems I feel refreshed!" is clumsy - "Looks like I'm refreshed!" - **fixed**
- [x] 446988 - インチキよ - "It's a cheat!" doesn't read like English - "You cheated!" - **fixed**
- [x] 446CB8 - トクなのか？そうかよかった - "Oh, greeeat!!" reads as sarcasm, but the JP is sincere relief - "Oh, good!!" - **fixed**
- [x] 446E1E - きのせいか？ - "Or just me?" is ambiguous; it means "or am I imagining it?" - "Or me imagine?" - **fixed**
- [x] 446E8C - オレいじめられてるか？ - "You bullying me?" adds an addressee; JP is "am I being bullied?" - "Me being bullied?" - **fixed**
- [x] 4471C8 - ふんふん - "Hmph hmph!!" sounds disdainful, but it is excited snorting - "*Snort snort*!!" - **fixed: Snort snort (no asterisks inside a line)**
- [x] 44837C - こんなのあさメシまえ‼そういえばあさメシまだ？ - "piece of cake" breaks the breakfast link to the next sentence - "Easy as pre-breakfast!! Speaking of, breakfast yet?" - **fixed**

## b027

- [x] 448480 - なんとかオレのかち！どうしてかオレにもわからない "Somehow I won, and I don't know why myself" - "Why?" reads as the doll asking a question rather than saying it doesn't know why. Suggest "Somehow me won! / Dunno why. / Me don't / know either..." - **fixed**
- [x] 448758 - クリアできなかったけど…それがしんぱいだぞ "Couldn't clear it, but will they feed me... that worries me" - It is a comma splice, and "That's what worries me" is too fluent for the brute. Suggest "Ugh... / Me couldn't / clear it, / will dinner come... / Me worry about that..." - **fixed**
- [x] 448714 - たべほうだい "all you can eat" - The break "all you can / eat!!" is clumsy. Suggest "Me cleared it, so dinner is / all-you-can-eat!!" if the width allows. - **fixed**
- [x] 448594 - "who cares!" is a little dismissive for がんばったからまあいいか "I tried hard, so it's fine". Suggest "...so it's all good!" Optional. - **fixed**

## bfix

- [x] 184766 - カゼのヌシさん - "Lord of Wind-san" is a stumble because the honorific sits on a title phrase, and "they saved her" gives Griffin a plural subject - "Didn't Lord of Wind-san say he saved her?" - **fixed**
- [x] 45F916, 45F93A - おきにいり as the item - lowercase "a favorite" while the menus (440CAC, 440EAE) say "Favorites" - "a Favorite". - **fixed**
- [x] 17A7CC, 17A810 - "is it not against ordinary kids... but against you Saga Commanders that I fight?" - stiff and tangled across the two ids - "Why, in this Saga Battle, am I not facing ordinary kids... but you Saga Commanders?" - **already fixed in this pass (L179)**

## phase 6 review, Minor (H:\translation\.harness\reviews, e0c8728)

- [x] stub rows - 27 dialogue pages end on a stub row of 3 letters or fewer (`16258E 163AA0 16414E 165D36 1678C6 168474 1684A4 16A3E8 16A482 16BEFA 16CAF0 16EB00 16EC2C 16EF2E 16F592 16FCB0 170FCC 171CDE 173784 173844 175654 1763CC 17668C 177656 178586 17A24A`, `165228` fixed): rebalance, add the check to `problems()`, or correct `docs/reviewer-brief.md`'s claim. - **already fixed: phase 7's balanced wrap rewrapped these and lint fails a short last row**
- [x] 16C3E8, 1772DE, 17A556 - Mac's tic: `16C3E8` lacks it, the other two have it mid-string. Drop "y'know" from Shu's row in `style-reference.md`. - **waived: 16C3E8's Japanese has no なんだな, so no tic; the style reference keeps Shu's sparing y'know, which the polish pass removed where it sat beside Mac (181482)**
- [x] 168636, 168664, 17D06A - オサさま: "Elder" twice, "Chief" in `17D06A` (Chief is BB's title). Use Elder. - **fixed**
- [x] 46F75C - credits have had no reviewer: レジェンズせいさくいいんかい lost "Production"; DIV./DEV. could take a second row. - **fixed: LEGENDZ / PRODUCTION / COMMITTEE in a blank row; DIVISION already whole**
- [x] glossary - the game's own English labels changed with no record: TRIAL OF AQUA -> WATER, HOSPICE -> LODGE, EXPENSIVE SHOP -> LUXURY SHOP, MERMAID'S HOUSE -> HOME, EVIL DRAGON'S RELIC -> RUINS. D2 prefers official names: record why, or restore. - **recorded in glossary.md, Style rules**
- [x] decisions - the skipped pilot isn't in `docs/decisions.md`. - **recorded as D13**
- [x] 2A85F0 and family - "Flem" reads as phlegm: Flemm or Flam. - **fixed with L39**
- [x] 47BDFE - "Cancelled" -> "Canceled". Grey Cave stays: the game's own label says GREY. - **fixed**

## phase 7 review

- [x] battle record page (`debug_battle_record`) - number values sit 2 px left in the 5-cell boxes (Damage Dealt, Damage Taken) of the 4-cell ones: the game pads numbers with code 0, 6 px in English, 8 in Japanese, so right edges differ by box size. Fix in the renderer (right-align digit runs) or leave; JP has them in one column. - **waived: a 2 px offset on a debug-only page; the game pads with code 0**

## Phase 8 visual QA

- [x] 18127A - レジェンズは そのなのとおり そんざいじたいが でんせつなのよ (Legendz, as the name says, are legends by their very existence) - "are legend itself" is ungrammatical - "Legendz, true to their name,<br>are legends just by existing!" - **fixed**
- [x] 184596 / 1845C6 (fixed in phase 8 with Dino's 1844A4 / 1844DE, split mid-phrase) - one sentence over two pages; the second ends on the lone word "island~♪" - reflow: "Look, look♪ I picked up<br>so much Legendz research<page>" / "material on that<br>island~♪" or similar, widths via `batches.py fit`.
- [x] room captions - 5 rooms' top banners are the JP ROM's own English art and differ from our subtitles: ISLAND OF WINGS/Isle of Wings, BLUE CAVE/Blue Water Cave, UNDER THE LAKE/Lakebed Cave, DARKNESS TOWER/Dark Tower, EVIL DRAGON'S RUINS/Evil Dragon Ruins. Align the subtitles (and glossary) to the banners, or keep and note why. - **waived: kept and recorded, D14 and glossary.md**
