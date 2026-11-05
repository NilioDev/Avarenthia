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
| **Approved: dungeons on their own land** | Built places that stand outside (temple, abbey, tower, fort, manor) start on their own play map with land around them; upper floors and cellars by stairs; each kind its own plan, bigger levels, wider halls, one telling thing per room, a mood line in the messages. Caves stay underground. Underground kinds their own plan too; hand-drawn pieces in data files and an editor for Nilio; classic dungeons from a random maker (rooms of many shapes grow onto the level, main ways 3 wide, narrow ways 1 wide, every passage from room to room). The random maker, the theme rooms, rivers underground and the pieces format are built (24 October 2026), and so are the temples, towers, barrows, abbeys, forts, manors, goblin places and the underground kinds' plans; the editor is built too (rounds 33-36, 31 October to 1 November 2026; see `docs/built.md`) |
| **Approved: more makers** | 21 new makers for dungeons and places (a fallen dwarf hold, real mines, sewers, catacombs, a castle dungeon, a maze, ice caves, lava tubes, tide caves, a fungal deep, drowned villages, bandit hideouts, a fey hill, a giant's steading, wyrm bones and more), plus 14 states (lived in, fallen, held, flooded, besieged, sealed and more, shifting while you play) and levels breaking into other kinds. Rounds 50-52 |
| **Approved: folk in need** | Ordinary people in every settlement, on the road and in camps ask for help with a need drawn from the world as it is (the wolves on the map, a raid in the news, the winter, their trade and people); a quest of 1-4 steps with a twist one time in three, useful rewards and favours, standing, people who remember you, 120 hand-written seeds. Rounds 46-47 |
| **Approved: marked creatures** | One list of 20 affixes for champions, uniques and named enemies (the 16 traits, Brutal, and new Warded, Ember-hearted, Grave-bound); a champion has one, a unique two or three; each fits its kind, place and season and has an answer the player already owns; rarer than now; loot unchanged. Rounds 45 |
| **Approved: crafts guilds** | Four new guilds so every life skill has one (smiths and miners, tanners and trappers, tailors, cooks and innkeepers), halls among three peoples each; a free guild bench, the master's test in the hall, the guild mark, the master's board, one guild secret at Master, a guild day with a contest, their own streets; guild jobs of seven kinds. Rounds 48-49 |
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
45. **Block 13: creatures and folk.** 45. **Marked creatures** (L). 46. **Folk in need, part 1** (XL): the maker, needs
    from the world, the grammar, rewards, who remembers you. 47. **Part 2** (L): twists, favours, the 120 seeds.
    Merge after 47.
48. **Block 14: the crafts guilds** (added 5 November 2026; after folk in need, whose maker makes the guild jobs).
    48. **Crafts guilds** (XL): the four new guilds and their halls, ranks, the guild bench, the master's test in the
    hall, the guild mark, the master's board, the secrets, the guild day, their streets. 49. **Guild jobs** (L): the
    seven kinds, the quarrel over the water and its consequences, the founder's heirlooms. Merge after 49.
50. **Block 15: more makers.** 50. **Part 1** (XL): the fallen dwarf hold, real mines, sewers, catacombs, the castle
    dungeon, the maze, ice caves. 51. **Part 2** (XL): lava tubes, tide caves and the other makers. 52. **Part 3** (L):
    the 14 states and levels breaking into other kinds. Merge after 52.
53. **Block 16: loose ends.** 53. **Boss fights: what is left** (L). 54. **Dungeons: what is left** (M): the entrance
    part of the fixed plans, each people flavouring a theme room. Merge after 54.
No play build in between (Nilio, 2 November 2026): he plays when the last block, now 16, is built. After that: Multiplayer (parked).

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

## More makers (approved 1 November 2026, not built)

Thread "Overzicht van alle generatoren". Dutch list: project files `generatoren/voorstel.md`. Each maker is its own
plan (like `delves.py`): you can tell from the map what the place is; what matters is a tile you see and bump.
1. **A fallen dwarf hold**: the hold maker (`deephold.py`) in ruin, three layers (the city, the workshops, the mines),
   the chasm bridge fallen, the forges cold; the cause comes from the history (a thing from the deep, goblins moved
   in, a plague, a flood) and the chronicle tells it.
2. **Real mines**: shafts and galleries that follow ore veins, cart rails, lifts, pit props, cave-ins and flooded deep
   levels; for human, kobold and abandoned mines. The Lost Mine becomes one.
3. **Sewers under cities**, following the streets above: channels with ledges, grates up to the street, a thieves' den.
4. **Catacombs or an ossuary** under city temples: a grid of niche passages, a bone chapel.
5. **A castle dungeon**: cells, a guard room, a torture room; prisoners to free.
6. **A maze** with a folklore dweller (the minotaur) at its heart.
7. **Ice caves** in a glacier: slick ice you slide over, the frozen dead.
8. **Lava tubes** under volcanoes: long round tunnels, crusts.
9. **A tide or smugglers' cave** on the coast: at high tide the low part floods (the hour counts).
10. **A fungal deep**: a wood of great mushrooms and spore clouds.
11. **An abandoned halfling hill home or a burnt elven glade**, a small place on the land.
12. **A drowned village** under a lake, reached only in a dry summer.
13. **A bandit hideout** in a quarry or a ruined keep: people with watch rounds and an alarm bell (rung, it wakes all).
14. **A fey hill**: a hall under the hill where time runs otherwise; outside a week has passed.
15. **A giant's steading** in the mountains: everything too big, under tables, crawl under doors.
16. **Wyrm bones**: the skeleton of an old dragon half in the ground, ribs for passages, the skull the last room.
17. **A sinkhole shaft**: levels round one open pit; look down, jump, or go down on a rope.
18. **Cellars under towns**: small cellars under houses and inns, for jobs.
19. **A geode**: a crystal cave that breaks the light into colours, rare stones.
20. **Termite mounds** on the savanna: climbed up from inside.
21. **A graveyard of family vaults**: many small vaults on one map.
Over all of them: **states** and **break-ins** (a level that gives onto another kind: a mine into a Varnish deep, a
sewer into the catacombs). The states: lived in; fallen; held by another people or by monsters; overgrown; flooded
(the low half under water, swim or find another way); just burnt (smouldering, hot floor, part fallen in); frozen
(winter or a curse, ice floors, frozen dwellers); stricken (doors nailed shut, stay too long and you may sicken);
haunted (still by day, the dead rise at night); besieged (an army of a war in `realms.py` before it, defenders inside;
help, smuggle in or betray); being plundered (the plunderers still at it); settled again (refugees or new settlers in
an old ruin, `townlife.py`); sealed (never opened since the fall: the best finds, the worst guards); already emptied
(grave robbers or a rival of `living.py` came first: their tracks, their snares, maybe still them).
**States shift while you play**: a besieged place falls if you stay away too long, a plundered one is overgrown later.
To settle when building: the order, which get their own boss and loot, the handbook lines.

---

## Marked creatures (approved 1 November 2026, not built)
Monsters grow more varied through one list of affixes, not through more kinds (there are 272). The full table with who,
where and the answer for each: project files `monsters/affixen.md`.
- **One list, 20 affixes.** The 16 traits of the named enemies (`named.TRAITS`); *Extra Strong* becomes **Brutal**
  (hits half again as hard), *Fire Enchanted* goes into Fire-blooded, *Fast* into Swift. Three new: **Warded** (resists
  one school of magic, the look line says which), **Ember-hearted** (burning ground 3 x 3 where it dies), **Grave-bound**
  (undead only: rises once more unless the body is burnt or hallowed). Also new: fire or acid stops Regenerating for 3 turns.
- **Who has how many.** A champion (blue) has 1 affix, from level 15 sometimes 2. A unique (gold) has 2 or 3 and a name in
  the named enemies' style ("Old Greytooth"); the Diablo names (`D.UNIQUE_NAME`, "Gorefang the Wicked") go. A named
  enemy keeps its own growing but draws its traits from this list.
- **It must fit.** Each affix belongs to certain kinds (Multishot only archers, Splitting never a people, Warcry only
  leaders); place, region and season make one likelier (Frost-touched in winter and the north, Fire-blooded on fire
  levels). Frost-touched and Fire-blooded never together.
- **Rarer.** Of the packs in dungeons about 8% champions and 3% uniques (now 12% and 7%); a little fewer in the wild.
- **Seen on one tile.** The colour stays blue or gold; in IN SIGHT the affixes stand on their own line under the name
  ("venomous, swift"); the look line `l` gives the sentence (`TRAIT_TEXT`). One first-time tip in `guide.TIPS`.
- **Every affix has an answer** the player already owns (Shielded: the flail or many small blows; Stone Skin: the war
  hammer; Thorny: a bow or reach; Splitting: fire). Dispel strips the magic ones, now also Warded, Ember-hearted and Blink.
- **Loot unchanged:** only those who use gear drop gear. A skinned unique may give a part tied to its affix (about
  25%, as named enemies do now, `beastparts.TRAIT_POWER`); champions nothing extra. The bestiary does not change.
- Handbook: two or three sentences in the fighting chapter. Test part `affixes`. Bump `SAVE_VERSION`.

## Folk in need (approved 1 November 2026, not built)
Quests the world makes itself, beside the boards. The Dutch proposal with examples: project files `quests/voorstel.md`
(thread "Leukere quests laten genereren").
- **Who.** 0 to 2 ordinary people with a need in each settlement, and on the road, by herds, in hermitages, as captives
  in a den, among hostile peoples when your standing allows. They wear the `!` and `?` that already mark people with
  work (`missions.py`); passing near, they say their need in the log; a bump talks (one choice window). Look names them
  ("Maud, the miller's wife, worried"). One first-time tip; no new key. Taken needs go in the Jobs tab and layer.
- **Need from the world.** Every need hangs on something real in this world, never made up for the quest: a monster
  group, nest, named enemy or roaming boss on the map; the news (raid, plague, famine, fire, war, an evil's mark);
  season and weather (a shut pass, drought, harvest, ice); caravans and goods; realms (a levy, a baron's grab); old
  places, Varnish ruins, barrows; the giver's trade (smith, fisher, innkeeper, priest...); the giver's people, each its
  own list (halfling, dwarf, elf, gnome, half-orc, human, and kobold, goblin, lizardfolk); feast days. No need depends
  on one people or place.
- **The grammar** (after Doran and Parberry's study of RPG quests): a motive (safety, health, family, knowledge,
  property, tools, honour, peace, skill, feast), an approach, and 1-4 steps from verbs the game has: go, talk, follow
  tracks (the named enemies' search area), find, bring, kill, drive off, guard or escort, make (a life skill), use a
  thing at a place, keep watch a night, spy, catch alive. Mostly 1-2 steps; sometimes a journey of 3-4.
- **Twists,** about one in three, picked at making and found on the spot (a rumour may hint): 18 kinds (the beast
  guards its young; it was driven out by something worse; the thief is a hungry child; the missing one will not come
  back; the giver lies; a rival; already sold; cursed; too late; the wrong one accused; a bewitched kin; the weather
  turns; two people want the opposite; a hidden place; a captive in the den; the beast is sick; the giver in danger
  while you are away). At most one choice, 2-4 options. The board jobs get these twists now and then too.
- **Rewards.** Small coin (the money balance). Standing always: in the giver's town, with the giver's people if
  another, with a temple, guild or the law where it fits; a twist's choice can also cost standing (`jobs.effects`).
  Beside it one thing fitting the giver: a service (a free repair or sharpening, a bed, healing, a crossing), a
  rumour that leads somewhere real (a hidden place, a herb, an epic teacher, a boss's weakness), a recipe or a
  bestiary step, something the giver owns (only what such a person has: the loot rule), access, or a follower later.
- **Favours.** About eight kinds, each a thing in the pack ("the ferryman's token", "Hob's carved whistle"). No key: it
  shows as an extra option in a window that exists already (the ferry, the city gate while wanted, the lord, a guide
  over a pass) and is gone after one use. On the player.
- **Remembered.** Who you helped lives on the player (`p.folk`): they greet you, now and then give a small thing or a
  rumour; sometimes a follow-up days or weeks later (up to three parts). Needs run out after some days: folk solve it
  themselves or it goes wrong, and the news says which; left alone, the world shows it (the goat gone, the well foul,
  the mill still, a grave with a name you know). Givers can die.
- **Seeds.** 120 hand-written small stories beside the maker (like the Varnish books): fixed lines, 2-4 steps, one
  twist with a choice drawn from a few, and a rule where it may fall ("The bell that rings at night": a human village
  with a chapel). Each world gets 20 to 25 of them.
- Code: `folkquests.py` (maker, steps) and `folkdata.py` (lists, twists, seeds); hooks in `townlife.py`, `events.py`,
  `news.py`, `missions.py` (Mission kind 'folk' with steps). Handbook: Jobs and money, Towns and people. The wiki gets
  the seeds' titles. Test part `folk`. Bump `SAVE_VERSION`. Size XL in two parts: A the maker, sources, steps, rewards,
  standing, favours and UI; B the twists (also on the boards), who remembers you, follow-ups and consequences, seeds.

## Crafts guilds (approved 2 November 2026, not built)
Every life skill gets a guild that keeps it. The Dutch proposal: the doc "Ambachtsgildes: voorstellen" (thread
"Ambachtsgildes voorstellen"). Rounds 48-49 of the build order. The rule "no new guilds" was about classes and elites;
the crafts guilds give no fighting power.
- **Four new guilds** beside Alembic and Barrel, the Cartographers and the Brotherhood of the Net (`guilds.py`, kind
  'life'): **The Hammer and Tongs** (mining, smithing; halls in human cities, dwarf holds, which already have a
  smiths' guild hall, and half-orc towns), **The Tanners' and Trappers' Lodge** (hunting, skinning, leatherworking;
  human cities by the water, halfling and half-orc towns), **The Needle and Loom** (tailoring; human cities, the
  elven city under the Elder Tree, gnome hamlets), **The Lantern and Ladle** (cooking, brewing beside Alembic; every
  inn with a sign, halfling hill homes). Archaeology joins the Cartographers; foraging counts for Alembic and Barrel
  too (the herbalist). Every guild has halls among at least three peoples. Anyone may join all of them.
- **Ranks** come from guild jobs as now, and each also asks a rank in the craft (about 10/20/30/40). An entry fee at
  each promotion (about 50c, 2s, 8s, 25s) instead of dues.
- **The guild bench.** The hall has the guild's own anvil, workbench or hearth; members use it free, others pay the
  usual 30c/20c. A bump and the window that exists now.
- **The master's test in the hall.** The tests at 25 and 40 can also be taken from the guild master; the far town's
  job stays, so the guild is a second source.
- **The guild mark.** From Journeyman what you make carries the mark in its name ("Iron spear, Hammer and Tongs
  mark"): merchants pay about 15% more, and the hall always buys your work.
- **The master's board** in the hall: better paid orders than the town board, one at a time, hung on the world
  (spears for the watch before a raid, a named beast's hide, a wedding cloak for a baron's house, a feast-day meal).
- **One guild secret at Master,** at the guild bench: Hammer and Tongs *re-temper* (roll a crafted power's values
  once more, may come out worse); the Lodge *mounting* (a named beast's head becomes a trophy to sell or give a lord
  for standing); Needle and Loom *livery* (clothes in a house's or people's colours: some standing in their land,
  the @ wears the colour); Lantern and Ladle *a table for the house* (cook for the whole inn: good moods and two more
  rumours).
- **The guild day** (`feasts.py`): stalls on the square and a contest for your best piece, judged by tier, powers
  and masterwork with a roll; the prize a rare material and your name in the news.
- **Their streets** (`citygrow.py`): the smiths' street with sparks (`anim.py`), the tanners by the water downstream
  with racks and pits, weavers and dyers with looms and vats; the inns of the Lantern and Ladle a small mark on their
  sign. Small happenings in `townlife.py`: tanners and dyers quarrel over the water, a smith wants a strong arm for a
  day, a journeyman on his wander year walks along to the next town.
- **Guild jobs** (approved 5 November 2026), made by the folk-in-need maker (`folkquests.py`) from steps the game has,
  hung on the world, rewarded with guild rank, materials or a pattern (a new thing to make) and little coin:
  1. **Fetch the stuff:** ore from a deep cave, a named beast's hide, Fey Silk; the higher your rank, the more
     dangerous the land.
  2. **Work for the world:** spears for the watch before a raid, winter cloaks before the snow, food for an army at
     war, a wedding cloak for a baron's house; made or bought.
  3. **The journeyman's wander year:** take a journeyman to a hall in another town, sometimes of another people;
     standing with both.
  4. **The false mark:** someone sells goods with a forged guild mark; track the forger in the poor quarter, then
     turn him in to the Watch or take a share.
  5. **The quarrel over the water** (tanners and dyers): take a side or mediate. The loser thinks less of you and
     shuts its bench and board to you for a season (and guild standing is your rank, so a rank can fall); the
     winner gives a favour (a thing in the pack, as with folk in need); mediating needs rank in both crafts, wins a
     little with both or, failed, costs a little with both. The town shows it: the losing tanners' racks stand
     empty for a season, or the losing dyers' vats stay dry.
  6. **The fallen mine:** kobolds or something from below in the guild's mine; clear it and members may dig there.
  7. **The founder's heirloom,** one great job per guild at Master, in three parts: Hammer and Tongs a broken Varnish
     sword in three pieces at three places; the Lodge the beast that killed its founder; Needle and Loom a realm's
     banner; Lantern and Ladle the king's meal at the Fair. The reward: the guild secret and a piece of your own.
  Consequences go through `jobs.effects` (town, people, guild, crime) and the folk-in-need memory (`p.folk`).
- Left out: a guild monopoly, dues, licences. UI: the guilds tab of the journal, the halls in the town legend
  (`guide.py`); no new key. Handbook: Guilds and Crafts. Test part `craftguilds`. Bump `SAVE_VERSION`.

## Dungeons on their own land (approved 22 October 2026, not built)
Today every dungeon level is 84 x 50 and made by one of two makers (rooms strung west to east, or a cellular cave); the kinds differ only in dressing, monsters and depth. Overview, 15 example levels and mockups: `/mnt/project-files/dungeons/` (`uitleg.md`, `mockups/`). Inspired by laughingpanjandrum's ASCII maps (Tomb of King Oraine, Church of the Ailing Flower).
- **Built places start outside** (built for temples, towers and barrows, 24 October 2026; see `docs/built.md`). A place that stands on the land (temple, abbey or monastery, tower, fort, manor, and other buildings on the world map) starts on its own play map with land around it, matching the world-map terrain: you walk in from the edge, through a gate or a door. An upper floor (a tower, a bell loft) and cellars or a crypt are their own levels, reached by stairs. Caves, dens, nests and mines still start straight underground. Mockup C.
- **Each kind its own plan.** A temple has a nave with pews and pillars, a transept, chapels and an altar; an abbey a cloister round a garden, a refectory and cells; a tomb a procession hall and burial galleries. You can tell from the map what the place is. Mockups A and C.
- **Bigger and roomier**, for fights with hirelings and spells: levels up to 120 x 70 (sizes per kind below), halls two or three wide. Ties in with Nilio's later wish for bigger play maps (the map view now shows 80 x 51).
- **Built walls are thin joined lines** (as town houses already draw them), one wall between neighbouring rooms, never a double one; caves keep their raw rock.
- **Mixed levels** when a job or the story asks: a built tomb that breaks into a cave (mockup B). Caves may be bigger too, with several great halls.
- **One telling thing per room** (a pool, a row of statues, an altar, a sarcophagus), always a tile used with one key or a bump.
- **A mood line**: the first time you step into a room, the messages say what it is ("The nave. Rotten pews face a cracked altar.").
- **Hand-drawn pieces** (the way of Dungeon Crawl Stone Soup): the format is built (24 October 2026; `pieces/README.txt`, `pieces.py`, see "The K5 maker" in `docs/built.md`). Left for the fixed plans: a kind's plan laid out first and its rooms filled with fitting pieces; unique places once per world.
- **Events in pieces**: the when / if / then rules are built in the pieces format (24 October 2026). The editor that draws pieces: "The Avarenthia Editor" below.
- **The random maker for classic dungeons (K5)** is built (24 October 2026, see "The K5 maker" in `docs/built.md`); the fixed plans set their theme rooms in their own spots.
- **Settled 22 October.**
  - **Which places start outside:** the temple, abbey or monastery, tower, fort, manor and barrow. Caves, dens, nests and mines start straight underground.
  - **Which maker:** classic dungeons and ruins use the K5 maker, with theme rooms set into them. The other kinds get a fixed plan of their own; an abbey, for example, always has a cloister, a refectory and cells.
  - **Goblin places come in two kinds.** The big delve with a market hall, a forge, family halls and the chief's hall is a goblin village and gets built like a settlement. An ordinary goblin hole gets its own, smaller plan in the same spirit.
  - **Below a temple or a fort** lie 3 to 5 levels of crypt or dungeon; the number varies.
  - **Stairs** may come out anywhere on the next level.
  - **Sizes, in three steps.** The map view already follows the hero on maps bigger than the screen. Sizes can be tuned later.
    - **Small, one screen, 80 x 50:** the manor, the barrow, an ordinary goblin hole and a beast's den.
    - **Middle, 100 x 60:** the temple, the abbey, the fort, and the levels below them.
    - **Large, 120 x 70:** classic dungeons, caves and the goblin village.
    - **Now and then very large, 150 x 90:** a special place, such as the bottom level or one of Nilio's unique places.
- **Theme rooms** are built for K5 (24 October 2026, see "The K5 maker" in `docs/built.md`): 38 drawn pieces in `pieces/theme.des`, with the arrival and bottom rooms. Still to come with the fixed plans: the entrance part, and each people flavouring a room (a dwarf shrine with a forge altar, a goblin library of stolen books).

## Boss fights: what is left (approved 26 October 2026)

The kit, the library and the boss maker are built (`docs/built.md`, "Boss fights"). Not built yet, for a later
round: arenas dressed per place (tower top, temple nave and the rest) and the ways out other than the rotten wall;
the place that wakes or falls in after a few bosses; fights won another way (hold out, rescue, break it, escape);
bosses for the big one (a fish) and the relic job.

---

## Parked
- **Multiplayer**: see docs/parked.md.
- **The bard** (the Lark's Company): see docs/parked.md. Not until Nilio says so.

## Later (not planned yet)
- Leadership: more hirelings, a group buff. A house of your own, with taxes.
- World ideas proposed with round 5 but not chosen: smoke over villages seen from afar, birds flushing from woods
  before an ambush, vultures over fights, the world growing (new hamlets, logging, regrowth), worn paths,
  lighthouses and watchtowers lit at night.
