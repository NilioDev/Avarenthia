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
| **To build** | **Bridges that join** (approved 14 November 2026, spec below); all of block 22 is built (13 November 2026) |
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
    60. **The Tests page grows** (M; built 13 November 2026, see `docs/built.md`).
61. **Block 22: the 10 November proposals** (Nilio, 13 November 2026: build all of the plan without waiting; the
    order chosen by Claude): 61. **A first sight of a town** (M; built 13 November 2026, see `docs/built.md`).
    62. **The land tells, and an inn in every town** (M; built 13 November 2026). 63. **Heard, lit and seen** (L; built 13 November 2026), before the camps,
    whose sneaking it needs. 64. **A roof of your own** (XL; built 13 November 2026). 65. **Camps on the road** (XL; built 13 November 2026). 66. **Wars that feel like
    wars** (XL; built 13 November 2026), with the field battle and magic in the wars.
No play build in between (Nilio, 2 November 2026): he plays when the last block, now 16, is built. After that: Multiplayer (parked).

---

---

## Bridges that join (approved 14 November 2026)

Nilio, thread "Bruggen in steden en dorpen ontwerpen": the bridges must join their roads; earlier tries were ragged.
The Dutch proposal with the mock-ups: project files `steden/bruggen-voorstel-2026-11-14.md`; a working trial on the
game's own city maker `steden/mockup_bruggen.py`, its pictures in `steden/bruggen/`. Replaces the painted bridges of
`citygrow` (`plan_bridge`, `stone_bridges`, `drawbridges`, `through_bridges`) and `towns.lay_bridges`.

- **The order.** Choose the crossings; lay the water straight there; set the bridge down as one piece; then the ways,
  from the bridgeheads; then the wall and its gates; then lanes and houses. In a village the river comes first (the
  land gives it), then the crossing, then the road, then the houses.
- **Straight water at a crossing.** A river or moat runs dead level or upright for the breadth of the bridge and 15
  cells each side, one width; its turns of 45 degrees lie between the bridges. In a village the river is drawn
  straight for the breadth of the bridge and a little more.
- **No bridge at 45 degrees inside a settlement.** On the open land they stay.
- **The bridge is a drawn piece**, never painted from a line: deck, a parapet each side its whole length, piers with
  cutwaters on both sides, a lamp on each corner (statues on the market bridge), and a bridgehead at each end where
  the quay street crosses the way square. Pieces live with the other drawn pieces (`pieces/*.des`), with a middle
  that repeats to the breadth of the water, so Nilio can redraw them in the Editor (as an option; the game ships
  its own).
- **One width.** A great way is 5 broad and so is its deck, from gate to market; a ring road 3 and its deck 3. The way
  runs straight and in line for 6 cells at each end (4 in a village).
- **Gates.** The wall may wander, but at every gate it runs straight (north, east, south or west) for some 27 cells,
  so the moat is straight there. Gate, a tower each side, the bridge over the moat and the forecourt are one piece. A
  road of the land that comes in aslant bends outside the town. A gate south of the river takes its way from the
  nearest bridge.
- **Canal towns** keep their plan; canal bridges only on the straight reaches, not on the slanting corners.
- **Villages and towns.** A timber bridge with a rail and a post on each corner, as broad as its road; stone in a
  town; a ford or one plank over a hamlet's brook. Ferries stay as they are. Each people's own style stays, as a piece.
- **The checker** (`city_rules`) gains the shape rules, each counted to 0: the deck is a clean rectangle; the parapet
  is whole and the same on both sides; both banks run straight at the bridge; the way is as broad as its deck and in
  line; no bridge at 45 degrees inside a settlement; every gate is one piece.
- Size: L. Saves: town maps are made anew, so a `SAVE_VERSION` step that remakes settlement maps.

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
- World ideas proposed with round 5 but not chosen: the world growing (new hamlets, logging, regrowth),
  lighthouses and watchtowers lit at night (smoke, birds, vultures and worn paths were built in round 62).
