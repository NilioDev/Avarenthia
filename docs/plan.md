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
| **To build** | Round 60: the Tests page grows (approved 6 November 2026); a roof of your own (approved 6 November 2026, rounds not yet ordered) |
| **Parked** | Multiplayer; the bard; the werewolf's and the vampire's curse (docs/parked.md) |
| **Later** | Leadership |

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
    keys** (L). Both built 6 November 2026 (see `docs/built.md`).
58. **Block 19: The Counted Sky and the peoples' books** (approved 6 November 2026, thread "Lore uit The Counted Sky
    en volksboeken"). 58a. **The Varnish lore made even** (M, mostly text). 58b. **The peoples' books** (L).
    58c. **The story on the land** (M). All three built 6 November 2026 (see `docs/built.md`).
59. **Block 20: games at the inn** (approved 6 November 2026, thread "Thematische minigames bedenken"; the Dutch
    proposal: project files `minigames/voorstel.md`). 59a. **Bones** (S/M). 59b. **Vigil** (M/L). 59c. **The Count** (S).
    All three built 6 November 2026 (see `docs/built.md`).
60. **Block 21: the Tests page grows** (approved 6 November 2026, thread "Testchecklist in debugmenu uitbreiden").
    60. **The Tests page grows** (M), spec below.
No play build in between (Nilio, 2 November 2026): he plays when the last block, now 16, is built. After that: Multiplayer (parked).

---

---

## The Tests page grows (approved 6 November 2026, not built)

Thread "Testchecklist in debugmenu uitbreiden". F12, T (the Tests page, built in round 37) is the checklist Nilio
works through; three things make it fit a game this big. Test build and `--debug` only, not in the handbook.
- **The older rounds get lines.** Rounds 1-5 (monsters, named enemies, guilds, jobs, seasons, sailing), weapons and
  the bestiary, the magic schools and spell effects, stamina, realms and wars, walking the land (zones), herds and
  hunting, nature and wonders, place names, ferries, keeping it clear, the handbook and the chronicle, the Varnish,
  the great evils: about 50 new lines in `docs/testing.md`, each with its recipe in `debug_tests.py` (test part
  `debug_tests` as now). A recipe that needs a debug action we lack gets it in the same round.
- **A tick lasts.** A ✓ or ✗ stays across builds. A line opens again only when its thing changed: each heading in
  `testing.md` may carry a line `Changed: <date>` (Claude sets it when a later round touches that thing); a tick
  older than that date shows dim and counts as open. `u` shows the open lines (never ticked, ✗, or changed since).
- **An overview per round.** Each heading shows its count, "3/5 ✓ 1 ✗". The first words of a ✗'s note stand after
  its line. `x` shows only the ✗ lines with their whole notes, by heading.

## A roof of your own (approved 6 November 2026, not built)

Thread "Housing-systeem ontwerpen"; the Dutch proposal with mock screens: project files `huizen/voorstel.md`. A gold
sink: one system, "a home", a small map of your own with a fixed plan (walls, doors) and a floor you furnish. All on
`p.homes` (multiplayer rule). Prices are first guesses for the `money` check (level 10 keeps up to ~80s a day).
- **A town house.** In hamlets, towns, cities and the metropolis of every people, one to a few for sale, a `$` on
  the door; bump it, one choice (`EV.ask`), 4g (hamlet) to 40g (metropolis), cheaper in the poor quarter. Each
  people's own kind (a hill home, a room in the rock, a house in a tree), taken from the settlement's own map, so the
  settlement rules hold. Hearth tax each season, paid when you come in or left in a chest by the door; a year unpaid
  and the town sells it (half back, less the debt; your things wait at the town hall).
- **Building anywhere.** A builder's stake from a carpenter (2g); on the world map an open tile (no road, no
  settlement, not by a hostile camp). Stages, each coin, trade goods (timber, stone) and days of building while you
  are away: camp, hut 5g, cabin 12g, stone house 25g, holdfast 30g (a palisade round it, so the settlement rule
  holds), keep 60g (a small stone tower-keep: the castle you build yourself). The look follows the land (log cabin
  in woods, stone in hills, sod on the steppe, stilts in the marsh, clay in the desert, a longhouse in the north).
- **The risk.** Each week away a roll by the region's threat (`mercs.py`), the distance to road and town and your
  defences: theft from one chest, a broken piece (`%`, paid to mend), squatters (bandits, a beast, goblins: a small
  fight in your own home), fire in a drought, a flood by a river, snow on a northern roof, a roused tribe or a great
  evil. Told through the news ("A drover says smoke rose over the cabin by the Grey Fen."). Defences: a lock, the
  palisade, a dog, a caretaker hireling on a wage, snares (Cunning), a rune on the door (Arcane); never zero in the wild.
- **A seat.** The empty seat of a fallen lesser house (`:`) or an empty fort, bought from the baron when you are
  his knight or well known to his house (120-300g), then restored in stages like building. Owned, never ruled
  (Nilio, 6 November 2026: ruling is another game): no villagers, no dues, no host, no land round it. The baron may
  call on it in a war (a realm job); if he loses, the new lord may claim it or sell it back to you. It gives room for
  all your hirelings, a stable for your wagons, a trophy hall and a watch that mostly beats off raids; a steward and
  guards cost a daily wage.
- **Furnishing.** In your own home one first-time tip teaches the furnish key (to pick from the free keys when
  built): a cursor on the floor and what you own beside it; place, pick up, move. Every piece works with a bump or is
  decoration: bed (rest, tree points, "well rested"), chest and strongbox (storage, 10 or 20 things), weapon rack and
  armour stand (swap a set at once), bookshelf (your books and pages, read again), hearth (cooking, warmth),
  workbench, anvil, loom (the guild bench at home at enough rank), shrine (a small blessing once a day), herb bed
  (herbs grow over days), kennel and stable (your beast, your wagons), trophies, rugs, tapestries, plants, lamps.
  Comfort, one to three stars, from variety, a matching style and trophies, makes "well rested" last longer; a
  neighbour or a house-warming remarks on it. Each people sells its own style (human oak, dwarf stone, elven wood,
  halfling snug, orc hide), a set of one style is a star more; dyes from Needle and Loom colour a piece; rare pieces
  from the Fair of Skell, tombs, or a boss's unchosen named things. Furniture is delivered (a few days, a small fee)
  or carried.
- **Where it shows.** `⌂` in your colour in the Places layer; a journal tab Homes (each home, its state, its chests);
  the line under the map ("Your cabin. All quiet when you left."); a handbook chapter "A Roof of Your Own".
- **Not:** ruling, fast travel home, renting out (a source of coin), free wall building tile by tile.
- **First choices, Nilio may change them:** a home is never lost outright to the weekly roll (a stage back at worst;
  only a great evil may burn it to the stake); more than one home is allowed, each with its own upkeep.

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
- Leadership: more hirelings, a group buff.
- World ideas proposed with round 5 but not chosen: smoke over villages seen from afar, birds flushing from woods
  before an ambush, vultures over fights, the world growing (new hamlets, logging, regrowth), worn paths,
  lighthouses and watchtowers lit at night.
