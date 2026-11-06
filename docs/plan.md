# The plan: where we stand

Only what is still to build. When a round is built, its spec and summary move to `docs/built.md` in the same
commit (see CLAUDE.md), so this file stays short. After each round: that round's own test part
(plus `text_fits` when text changed), push (CI runs the whole suite and builds), a short Dutch report. The full run
(seeds 1-3, smoke, bot) happens once, at the end of a build, before merging to main. Nilio plays afterwards and sends feedback.

Inspiration: Shadowdark (core book, Western Reaches, Cursed Scrolls 1-6), D&D, Pathfinder, Diablo, Final Fantasy,
WoW. Take the ideas, never the text, stat blocks or invented names.

## At a glance

| Status | What |
|---|---|
| **Built** | Everything up to the magic schools, the debug menu, the weapons and the classes: see `docs/built.md` (summaries and the specs of built rounds) |
| **To build** | The bar of seven keys, with the balance measure first (round 57; approved 6 November 2026) |
| **To build** | The Counted Sky in the game and books for every people (round 58; approved 6 November 2026) |
| **Parked** | Multiplayer; the bard; the werewolf's and the vampire's curse (docs/parked.md) |
| **Later** | Leadership, a house of your own |

**The build order** (settled with Nilio 23 October 2026, thread "Bouwvolgorde plan.md"; the Dutch proposal with the
reasons: project files `bouw/volgorde.md`). 32 rounds in 9 blocks (the great evils and trade added 25 October 2026, the boss fights 26 October). Sizes: S like market day, M like spell effects
part 2, L like herds and hunting, XL like the magic schools. No play builds in between (Nilio, 23 October 2026): he plays only when all blocks are built, through the last round, now 32 (Nilio, 25 October 2026: the play build only at the end), so the
"pauses" below are only clean points to stop at when his usage limit runs low. The full test run and the merge to
`main` come at the end of each block; CI keeps testing every push. Each block starts on Nilio's "ga".
0. **Debug menu and test build** (M). Built 23 October 2026 (see `docs/built.md`).
1. **Weapons** with the bestiary that grows (L). Built 23 October 2026 (see `docs/built.md`).
2. **Classes part 1** (XL): blank start, the classes, the bar, two skills per weapon kind with their effects.
   Built 23 October 2026 (see `docs/built.md`).
3. **Classes part 2** (L): the trees. Built 23 October 2026 (see `docs/built.md`). 4. **Classes part 3** (XL): pair and pure rules, Cunning and Arcane, guild
   elites, the balance test. Built 23 October 2026 (see `docs/built.md`). A pause after 2, 3 and 4; merge after 4. The epics wait for round 13.
5. **The K5 maker** (XL): sizes, rock texture, rivers underground, mood lines, the pieces format, theme rooms. Built 24 October 2026 (see `docs/built.md`).
6. **Places on their own land, part 1** (XL): temples, towers (floors, lookout, ruins, edges and falls), barrows. Built 24 October 2026 (see `docs/built.md`).
7. **Part 2** (XL): abbeys, forts, manors, the goblin hole and goblin village, the underground kinds' plans. Built 24 October 2026 (see `docs/built.md`).
8. **The northern lights' gift** (M): needs the barrows. Built 24 October 2026 (see `docs/built.md`); its light-feast built with the feast days (round 28).
9. **The Rift and the Ashen Deep** (L). Built 24 October 2026 (see `docs/built.md`). 10. ~~The editor~~: taken out of
   the build order on 24 October 2026; back as rounds 33-36 (31 October 2026, "The Avarenthia Editor").
   A pause after 5, 7 and 9; merge after 9.
11. **Old places from the history** (L): battlefields, deserted villages, memorials, hermitages and the rest of part A.
    Built 24 October 2026 (see `docs/built.md`).
12. **The Varnish** (XL): their cities and places, the hidden dungeons, the lore, the books, the riddles. Built 25
    October 2026 (see `docs/built.md`).
13. **Classes part 4: the epics** (L). Built 29 October 2026 (see `docs/built.md`). 14. **Trade part 1:
    the money fixes** (S). Built 29 October 2026 (see `docs/built.md`). Pause after 12, merge after 14.
15. **Boss fights part A: the kit** (XL). Built 29 October 2026 (see `docs/built.md`). 16. **Part B** (XL): the
    move library, the other fixed bosses, roaming bosses. Built 29 October 2026 (see `docs/built.md`).
17. **The great evils, part 1: the frame** (XL). Built 29 October 2026 (see `docs/built.md`); Archaeology added its
    source of weaknesses on 30 October 2026.
18. **Part 2: the quest and the Sky-Seat** (XL). Built 29 October 2026 (see `docs/built.md`). Pause after 15, 16 and
    17, merge after 18 (Nilio, 25 October 2026: the great evils come right after the
    epics, in parts).
19. **Life skills part 1** (XL): the curve, Herbalism into Foraging, Smithing and Tailoring, the materials by tier,
    alchemy, brewing. Built 30 October 2026 (see `docs/built.md`). 20. **Part 2** (XL): beast parts, crafted powers, Unmake,
    master tests, perks, hirelings' gear, named beasts' dens, catching alive, the great masters. Built 30 October 2026
    (see `docs/built.md`).
21. **Archaeology** (M). Built 30 October 2026 (see `docs/built.md`).
22. **Trade part 2: goods and ways** (L). Built 30 October 2026 (see `docs/built.md`).
23. **Boss fights part C** (L). Built 30 October 2026 (see `docs/built.md`). Pause after 19, 20, 21 and 22, merge
    after 23.
24. **Cities that grew, part 1** (XL). Built 30 October 2026 (see `docs/built.md`).
25. **Part 2** (L). Built 30 October 2026 (see `docs/built.md`). 26. **Trade part 3: caravans** (L). Built 30
    October 2026 (see `docs/built.md`). 27. **Round 6** (L). Built 30 October 2026 (see
    `docs/built.md`). 28. **Feast days** (L). Built 30 October 2026 (see `docs/built.md`). Pause after 24, 26 and 27, merge after 28.
29. **Old places part B and the 44 places of the peoples and powers** (XL), with the caravanserai for the caravans.
    Built 30 October 2026 (see `docs/built.md`). 30. **Places 45-64 and the seasonal places** (L). Built 30 October
    2026 (see `docs/built.md`). Merge after 30.
31. **The great evils, part 3: the other sixteen servants** (XL). Built 31 October 2026 with part 4 in one round
    (see `docs/built.md`). Merge after it.
32b. **The Avarenthia Editor** (approved 31 October 2026, thread "Editor voor speciale kamers ontwerpen"; Nilio's
    "ga" the same evening). 33. **Round A** (XL): the PxPlus tileset, the editor's screen, drawing and saving rooms,
    the check. Built 31 October 2026 (`avarenthia/editor/`, `editor.py`, test part `editor`). 34. **Round B1** (XL): events with switches, counters and wires, variety, creatures and lists,
    dressing, own tiles and things, Ctrl+R, Try. Built 31 October 2026 (`dressing.py`, `owntiles.py`,
    `editor/layers.py`, `maker.py`, `trying.py`; test parts `editor` and `pieces`). Pause after it. 35. **Round B2** (XL): more doors (`'`, `DOORS:`), then puzzle things 1-26 in the
    game. Built 31 October 2026 (`puzzles.py`, `pieces/puzzles.des` with 15 example rooms, the editor's PUZZLE THINGS;
    test part `puzzles`). 36. **Round C** (XL): whole places, puzzle things 27-44. Built 1 November 2026
    (`drawnplaces.py`, `places/saint-odo.des`, `editor/placemode.py`; test parts `puzzles`, `drawn_places`, `editor`).
    Merged after 36 (see `docs/built.md`).
37. **Block 10: playing and reporting made cheap** (settled 2 November 2026, thread "Testen in de testbuild makkelijk
    maken"; the Dutch proposal: project files `bouw/volgorde-2.md`). 37. **The test menu** (L). 38. **Saves that last**
    (M). 39. **The money check** (M). Built 5 November 2026 (see `docs/built.md`).
40. **Block 11: the start of the game.** 40. **The first tome, a letter for the city, the baron's word** (L; built 5 November 2026).
    41. **What you met** (M; built 5 November 2026). 42. **The belt and the tally** (L; built 5 November 2026). Merge after 42.
43. **Block 12: a finer look, not busier.** 43. **Items 1, 2, 5, 6, 7** (M; built 5 November 2026). 44. **Item 3, then item 4** (M; built 5 November 2026). Merge
    after 44.
45. **Block 13: creatures and folk.** 45. **Marked creatures** (L; built 5 November 2026). 46. **Folk in need, part 1** (XL; built 5 November 2026): the maker, needs
    from the world, the grammar, rewards, who remembers you. 47. **Part 2** (L; built 5 November 2026): twists, favours, the 120 seeds.
    Merge after 47.
48. **Block 14: the crafts guilds** (added 5 November 2026; after folk in need, whose maker makes the guild jobs).
    48. **Crafts guilds** (XL; built 5 November 2026): the four new guilds and their halls, ranks, the guild bench, the master's test in the
    hall, the guild mark, the master's board, the secrets, the guild day, their streets. 49. **Guild jobs** (L; built 5 November 2026): the
    seven kinds, the quarrel over the water and its consequences, the founder's heirlooms. Merge after 49.
50. **Block 15: more makers.** 50. **Part 1** (XL; built 5 November 2026): the fallen dwarf hold, real mines, sewers, catacombs, the castle
    dungeon, the maze, ice caves. 51. **Part 2** (XL; built 5 November 2026): lava tubes, tide caves and the other makers. 52. **Part 3** (L; built 5 November 2026):
    the 14 states and levels breaking into other kinds. Merge after 52.
53. **Block 16: loose ends.** 53. **Boss fights: what is left** (L; built 5 November 2026). 54. **Dungeons: what is left**
    (M; built 5 November 2026): the entrance part of the fixed plans, each people flavouring a theme room. Merge after 54.
    All 54 rounds are built (see `docs/built.md`).
55. **Block 17: the makers in the editor** (approved 5 November 2026, thread "Generatoren in de editor gebruiken").
    55. **Makers in the editor** (XL; built 5 November 2026, see `docs/built.md`), with the maker area.
    56. **A window that fits** (M; built 5 November 2026, see `docs/built.md`).
57. **Block 18: the bar of seven keys** (approved 6 November 2026, thread "Skillsysteem met 6 toetsen beoordelen").
    57a. **The balance measure** (M) first, so the numbers are set before the bar changes. 57b. **The bar of seven
    keys** (L): see "The bar of seven keys" below. Merge after 57b.
58. **Block 19: The Counted Sky and the peoples' books** (approved 6 November 2026, thread "Lore uit The Counted Sky
    en volksboeken"). 58a. **The Varnish lore made even** (M, mostly text). 58b. **The peoples' books** (L).
    58c. **The story on the land** (M). See "The Counted Sky in the game" below. Merge after 58c.
No play build in between (Nilio, 2 November 2026): he plays when the last block, now 16, is built. After that: Multiplayer (parked).

---

## The bar of seven keys (approved 6 November 2026; not built)

Approved by Nilio on 6 November 2026 (thread "Skillsysteem met 6 toetsen beoordelen"). Why: with three class keys
everyone takes damage and the helping skills (Tame, Gate, Purify, Mend) never reach the bar; the bar changes only in
a town, so deep in a dungeon most known skills are dead; and an epic on key 6 costs the elite, then leaves key 6
empty until the next rest, while camping anywhere makes "once per rest" cheap.

- **The bar:** **1-2** the weapon's two skills (as now), **3-6 four class skills, at most one of them an elite**
  (the elite takes a class key, so it costs an ordinary skill, as in Guild Wars), **7 the epic**. Key 7 and its
  group show only once you have learnt an epic; one first-time tip in `guide.TIPS` teaches it. In a shape, 1-2 are
  the beast's attacks and 3-7 rest unless Untamed (as now). Weapon rules colour class skills on 3-6 as they did on 3-5.
- **The epic charges by fighting** instead of once per rest. The ♦ on key 7 fills with blows given and taken (as a
  share of your life) and foes brought down (by their threat); foes far below your level (about 5 levels) give
  nothing, so rats cannot be farmed. Full after about one hard fight or a few ordinary ones; it stays full until
  used and keeps between rests and saves; resting does not fill it. It starts empty when learnt and empties when the
  teacher swaps it. Shown on the bar only: the ♦ goes from dull to bright gold as it fills (no number, no new screen).
  **Phoenix** stays once per day and does not charge. How fast each epic fills is set per epic from the balance
  measure (Time Stop and Army of the Dead may want a slower fill).
- **Changing the bar after any rest:** [z] lets you change the bar in a town (as now) and also right after a rest,
  an inn's bed or your camp, before you walk on, the same moment as spending tree points. Never with a foe in sight,
  because no one rests then.
- **Casting from the book:** any skill you know that is not on the bar can be used from the [z] list: 3 turns
  instead of 1, its usual cost and cooldown, broken off like rummaging in the pack (a new foe in sight or a blow;
  the turns are gone, nothing is cast). Not for elites, the epic or weapon skills: those work only from the bar.
  So the bar is the fight, and the helping skills are still there when there is time.
- **The balance measure** (round 57a, built first): `python tests/balance.py [seed]` beside `tests/money.py`. The
  bot builds of the `balance` part, each fought with today's bar (3 + elite) and the new one (4 with an elite, and 4
  without), at levels 10, 20 and 30, with and without an epic: waves won, turns, damage taken, how often the epic
  fills per level of a dungeon, and each of the 22 epics' share of the damage or the saved life. It prints a table so
  the charge numbers and any epic that is too strong can be set before 57b; its bands become asserts in the
  `balance` part (new bar no more than about 15% faster than the old one; an epic about once per hard fight).
- **Handbook:** "Who you become" (the bar's three groups become 1-2, 3-6 with one elite, 7 the epic; charging; the
  bar after a rest; casting from the book), "Epics" (charges instead of once per rest; Phoenix once per day), "All the
  keys" ([1-7]), "Resting" (changing the bar). The build report quotes the lines.
- **Save data:** the bar gets seven places, an elite on old key 6 moves to class key 6 (the 4th), an epic to key 7;
  `p.epic` gets its charge. Bump `SAVE_VERSION`, a step in `saves.MIGRATIONS` (not breaking).
- **Tests:** `balance` (the new bar and charging), `classes` and `epics` (the slots, elite limit, key 7, the
  charge), `lasting_saves` (the move), `text_fits`; testing.md "The bar of seven keys".

---

## The Counted Sky in the game (approved 6 November 2026; not built)

Approved by Nilio on 6 November 2026 (thread "Lore uit The Counted Sky en volksboeken"). The story of the Varnish,
"The Counted Sky", in Nilio's own writing (project files `lore/The_Counted_Sky-Niels-2026-11-06.pdf`; older text
`lore/varnish-origin.md`), is the source: its tone is the reference for every new text. The Dutch proposal with the
sample pages: the Claude Doc "Voorstel: The Counted Sky in het spel, en boeken voor alle volken".

- **The whole story shows step by step** (Nilio, 6 November 2026), never as one book to find: each people tells its
  own "Before the Founding" in its books, so the prologue comes from them; each Varnish riddle made whole opens one or
  two chapters of The Counted Sky as whole text in the chronicle (a heading "The Counted Sky" in The Varnish); the
  end (chapters IX and X and the last line, one light coming back in the north) only after the Hollow King is beaten,
  as the book the Circle of Magi writes out for you.
- **One source for the story:** the story goes into the repo as `docs/lore/the-counted-sky.md`; every text taken
  from it carries the chapter it comes from, so a later change to a chapter shows which fragments and pages to go
  over. The chronicle reads such texts from the source by key, so old saves show a changed sentence too.
- **A review document at the end** (Nilio, 6 November 2026): once 58a and 58b are built, a document like his PDF
  with everything that went into the game: the story, all Varnish fragments and books, every people's books and
  their "Before the Founding", the voices; Nilio reads it through and sends changes, which then go into the source
  and the game.

- **58a. The Varnish lore made even** with the story: the heart was Vael, the small moon, after the nine stars of her
  Crown (riddle "How the Sky-Seat fell", A Teller's Count: nine gone in a ring round Vael, the scorch pointing at the
  Sky-Seat; its hidden line names Master Vane and his pupil Ilo); `hidden.py` "four hundred years" becomes twelve
  hundred; the Varnish Gladius and Pilum get names of their own; "Morrak always collects" among the Morrak lines.
  About forty new fragments from the story (a new heading "Before the Founding": the question to the iron, Ilthrix
  Who Was a Star, the giants, the wyrms, the fey, men out of the western sea; and Orveth, Ennis, Taur and the pits,
  the fortieth master, the eye on the prow, the skipping rhyme). Four new Varnish books: The Ninth Day of Taur
  (widened), Orveth's Notes (a piece of the King's riddle), The Fortieth Master (points to the Wyrm's Bones and the
  altar stone), Ennis, On Curves (four pages his own; the hidden line, in his hand on page five: "Stop.").
- **58b. The peoples' books**, on the Varnish books' frame (pages where they fit, gathered, bound, a hidden line that
  does something), four or five books per people in the data and one or two per people in a world, five to seven
  pages each. Each people writes its own way: dwarves in ledger leaves, elves in rings, halflings in recipes and
  almanacs, gnomes in workshop notebooks, kobolds on slates, goblins in a swap ledger, orcs in a young script of
  their own, the north in kept names; gnolls and lizardfolk do not write (carved bones, moon-stones, a verse heard
  at full moon). **Reading goes through the people:** you read their pages if your hero is of that people, if a
  hireling of that people is with you (one line in the log), or when one of them reads it to you in their place;
  halflings and goblins write in common letters. **That people binds them:** the Grudge Book's keeper, the
  loremaster under the Elder Tree, the mayor in the Keepsake Hall, a gnome house. The chronicle's Peoples chapter gets
  a heading per people. A bound book does something of that people: one of their hidden places on the map, a recipe,
  a feast you may now join, a favour, or a piece of a Varnish riddle seen from their side. Each people tells its own
  "Before the Founding", so the prologue comes in pieces that contradict each other. The books (sample pages in the
  proposal): dwarves The Account of Bardin Coalhand, The Hold That Delved Too Deep, The Sparks Owed, The Night the
  Gates Opened; elves The First Pact, The Rings of the Tree, The Nine Names (lies in a star house), Starsong;
  halflings The Long Table Book, Pellam's Ledger, The Almanac of Not Jutting, Second Breakfast; gnomes The Stake
  Moved Four Paces, What the Oaks Said, The Count Kept Private, The First Winter; kobolds The Shine Tally, She Who Saw
  the Sky, The Bridge Spikes; goblins The Honest Day Book, What We Heard Under the Collegium, Sold Twice; gnolls The
  Last Verse; lizardfolk The Long Bone, Pressed Into the Peat; orcs When We Came Up; the north The Names Kept, The
  Torches on the Snow; **the fey** one book, The First Pact from their side ("to the letter, never the spirit"). What
  you have lives on the player.
- **Each people's own voice** in everyday talk, as in the story: the elves first (sure of themselves to the point of
  annoying, a smile from above, never a taunt: "The price is fair. I know, because I set it."; asked about the stars
  in the north they change the subject), then dwarves curt and book-keeping, halflings hospitable and sly, gnomes
  absent and curious. In greetings, rumours, traders, the glade elder, the loremaster (`lore.RACE_LORE` and the
  peoples' barks).
- **58c. The story on the land**, each a tile you step on or bump, with one outcome: (1) **Bardin Coalhand**, bound in
  a bridge abutment in one Varnish ruin per world, carried to a dwarf hold and laid flat: the grudge stays open, but
  every hold knows your name. (2) **The altar stone** a mile from the Wyrm's Bones: bread and oil in spring calm the
  desert round the bones that year; binding or plundering the bones lights something in the sockets (a warning and a
  heavy curse, no fight). (3) **Ferro**, the bound clerk in a deserted granary, who tells the measure people needed to
  live. (4) **Tam's tally** on his wall tower, to day 3,651 and "Count me": [e] counts him (Your deeds). (5) **The
  dark ring** on a star house's iron floor: nine lead plugs round an empty hole; who beats the King sees one light
  come back in the north on the closing screen, and a silver dot on that floor afterwards. (6) **Aerith** chained in
  the Hall of the Winds: breaking her chain (the storm on that floor first grows worse) lightens the first phase of
  the last fight, like a relic. (7) **The goblins knew**: a goblin boss, well paid, tells of the drains under the
  mud-city: a second, narrower way up in the Under-City. (8) **The north** has mostly forgotten its past but has a
  clear culture of its own: they call you by your name once you have said it, a guest is fed before questions, they
  still steer by the stars; only the Varnish books show why. (9) **The Northern Wall on the world map**: a broken
  grey line in the towers' colour on the stretches you have seen (all of it after the lantern), gaps where it fell,
  so it reads as old and not as a border.
- **Handbook:** "The Varnish" (the peoples' books beside theirs; reading through a people or a hireling; binding by
  that people), the Peoples chapter, the Wall's line in the world-map signs (`guide.py`). The build report quotes the
  lines.
- **Save data:** the peoples' pages, read and bound books on the player; new world places (Bardin, the granary, the
  altar stone). Bump `SAVE_VERSION`, a step in `saves.MIGRATIONS` (not breaking).
- **Tests:** `varnish` (the made-even texts, the four new books), a new part `folkbooks` (pages placed, reading by
  people/hireling, binding, effects), `text_fits`, `lasting_saves`; testing.md "The Counted Sky in the game". The
  wiki gets the peoples' books.

---

## The UI rule for every new round

Everything new finds its place in what is there; no new screen per system, no new letter keys in play:
- **A list or a record** (realms, lords and houses, dishes, herds, wonders) goes in a tab of the journal (e).
- **Something spread over the land** (realms and borders, herds, seasons) goes in a layer of the world map (m),
  with its own legend line. The realms layer becomes key 4, after Factions.
- **Something about where you stand** (the realm or baron, the wind when hunting, the zone) goes on the line under
  the map. **Something in a fight** goes in IN SIGHT.
- **A new sign** is named by the data (tile names, `guide.py`), so the look legend and the journal's Signs know it.
- **A new key** is taught by one tip in `guide.TIPS` the first time it is useful, not by text on the screen.

---

## The look rule (Nilio, 31 October 2026)

Prettier means using what is on the screen better, never adding to it:
- **Three layers of brightness.** Ground and rock stay dim, built things and walls in the middle, and only what lives
  or can be used is bright: creatures, items, doors, stairs, places.
- **An accent colour has one meaning.** Gold is something for you (money, jobs, places, what matters in the log), red
  is danger; the orbs' red, ochre and blue belong to life, stamina and mana. The ground does not borrow them.
- **Movement is scarce.** Only what really moves (fire, water, spell effects); no blinking or glinting as decoration.

---

---

## Parked
- **Multiplayer**: see docs/parked.md.
- **The bard** (the Lark's Company): see docs/parked.md. Not until Nilio says so.

## Later (not planned yet)
- Leadership: more hirelings, a group buff. A house of your own, with taxes.
- World ideas proposed with round 5 but not chosen: smoke over villages seen from afar, birds flushing from woods
  before an ambush, vultures over fights, the world growing (new hamlets, logging, regrowth), worn paths,
  lighthouses and watchtowers lit at night.
