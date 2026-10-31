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
| **Approved: dungeons on their own land** | Built places that stand outside (temple, abbey, tower, fort, manor) start on their own play map with land around them; upper floors and cellars by stairs; each kind its own plan, bigger levels, wider halls, one telling thing per room, a mood line in the messages. Caves stay underground. Underground kinds their own plan too; hand-drawn pieces in data files and an editor for Nilio; classic dungeons from a random maker (rooms of many shapes grow onto the level, main ways 3 wide, narrow ways 1 wide, every passage from room to room). The random maker, the theme rooms, rivers underground and the pieces format are built (24 October 2026), and so are the temples, towers, barrows, abbeys, forts, manors, goblin places and the underground kinds' plans; the editor is approved and in the build order (rounds 33-36, "The Avarenthia Editor" below) |
| **Approved: the Avarenthia Editor (31 Oct)** | Nilio's own program in the test build to draw rooms, whole places, tiles and things; events with switches, counters and wires; Zelda-like puzzles in the game; creatures drawn, of the place or from his own lists; dressing a room; the PxPlus tileset. Rounds 33-36 |
| **Parked** | The bard; the werewolf's and the vampire's curse (docs/parked.md) |
| **Later** | Crafts guilds, leadership, a house of your own |

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
    test part `puzzles`). 36. **Round C** (XL): whole places, puzzle things 27-44. Merge after 36.
After that: Multiplayer (parked).

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

## The Avarenthia Editor (approved 31 October 2026, not built)

Nilio's own program for drawing the special rooms, whole places, tiles and things of the game. Proposal in Dutch with
eight mockups in the project files, `editor/` (`voorstel.md`, `puzzels.md`, `1_` to `8_*.png`, `mockup_editor.py`,
the fonts in `editor/font/`). It edits the pieces format that is already built (`pieces/README.txt`, `pieces.py`).

- **What it is.** Its own program, "Avarenthia Editor": `python main.py --editor` from the source, and a third
  PyInstaller build that goes only into the "Avarenthia (test)" download. Not in the players' download, not in the
  handbook. Code in `avarenthia/editor/` (`model.py`, `write.py`, `tools.py`, `screen.py`, `panels.py`).
- **The screen** (mockup 1): the game's window and tiles. Left: Tools (Draw, Line, Rectangle, Fill, Select, Variety)
  and the Palette in groups (Ground, Water and fire, Things, Telling things, Puzzle things, My tiles, My things,
  More = every tile of the game). Middle: the drawing with a ruler, zoom 1-4; the rock wall round a room is drawn for
  you. Right: the piece (name, part, places it suits, from level, how often, way in, shape, size, mood lines), the
  layers (Ground, Things, Creatures, Events; Tab), and "Will the game take it?". Bottom line: cursor, tile, tool,
  layer, zoom, size, saved.
- **Controls.** The mouse first: left draws, right picks the tile under it (in Creatures and Events: takes away),
  wheel zooms, middle mouse or Space-drag moves the view. Keys: D L R F S V for the tools, Tab, Ctrl+Z / Ctrl+Y,
  Ctrl+C / X / V, Delete, Ctrl+N / O / S, Ctrl+R (a few drawings as the game makes them: turned, mirrored, variety
  picked), Ctrl+T (a new tile or thing), Ctrl+D (dress), F5 (Try), PgUp / PgDn (floors), Esc.
- **No free colours** per cell: a tile carries its colour and meaning. Instead **own tiles** (name, look line,
  "is like" floor / wall / water / shallow / chasm / fire, a sign from the tileset or an own 8 x 8 sign, two colours,
  see-through, a preview lit and remembered) and **own things** (sign, colours, stands on, blocks the way and/or
  sight, look line; when you bump / step / look; "it does" from lists or one of the game's existing do's).
  A new kind of doing is not made in the editor: Nilio describes it, Claude builds it, it joins the list. Own tiles
  take fixed places after the game's own, by name; a removed one stays as an empty place so saves do not break.
- **The tileset** becomes PxPlus IBM CGA (same maker VileR, same licence CC BY-SA): 781 signs plus our hand-drawn
  ones, thick only. The lever becomes ⌐ / ¬. The editor warns when an own tile uses a letter a creature has.
- **Size.** Set in the Size field or by dragging the corner handles, up to **40 x 30** for a room; the limit shows in
  Ctrl+N and Size, and dragging stops there with the line "40 x 30 is the most for a room; bigger: make it a whole
  place" and a button that turns it into one.
- **Creatures three ways**, mixed in one room: drawn (this one, here, always); `?` one of the place (by kind and
  level, as now); `1`-`9` from Nilio's own lists (`LIST: war band = orc:6 orc_shaman:1 ogre:1 troll:1`; only kinds
  that may live in the place are drawn, else back to `?`); plus "and more", 0-n extra where there is room.
  Format: `CREATURE: <key> | ? | list:<name> at x,y`, `LIST:`, `MORE:`.
- **Dressing (Ctrl+D).** Sets (war camp, hall, ruin, library, own sets) and how full; rules, not scatter (tables in
  twos, furs round the fire, shelves on walls, barrels in corners, never on the way from the door to a way out or a
  telling thing; the rules of `dress.py`). Both ways: now, in the editor (laid light green, R rolls again, then edit
  by hand), or in the game (a room or area marked with a set, dressed anew in every world).
- **Variety**: paint cells with a group (1, 2...) and weights per group ("statue 1 : floor 3"), the `SUBST` lines.
- **Events** (mockup 2): marks drawn in gold on the Events layer; WHEN / AT / IF / THEN rows, every field a list,
  only a line of text is typed. **Switches** (on/off or one of a few), **counters**, **wires** (click a thing, then
  what it works on; a line is drawn), timers, "back as drawn". The game keeps each place's state.
- **The check** runs live, in plain words, red cells and a click jumps there; Save only when all is green.
- **Try (F5)** opens the game in test mode on one K5 level with the piece in it, the hero at its way in; Esc or
  death goes back. If a level cannot run without a world, Try makes one small test world once and keeps it.
- **Saving**: `My pieces.des`, `my tiles.des`, `my places.des` beside the editor; the editor rewrites only the block
  of the piece it edits. Nilio hands the files over ("voeg toe"), they go into `pieces/`, CI packs and seals them.
- **Puzzles** (`puzzels.md`, mockup 7): 1-19 puzzle things (pressure plate, stone block, lever, crystal switch with
  red and blue blocks, brazier, mirror and sun disc, bells in order, gate of bars, cracked wall, crumbling floor,
  slick ice, spikes on a rhythm, two portals, plinth, keyhole with the place's own key, sluice, arrow trap, riddle
  stone); 20-26 dungeon things (sarcophagus, offering bowl, cell with a prisoner, scrying pool, chained book, idol
  with gem eyes, rope down / ladder up); 27-44 more (mirror statues, the statue that comes when unseen, a raft on a
  stream, wind in a passage, shifting walls, blocks into a chasm or through a hole, an oil barrel against a cracked
  wall, runes in order, a light floor, a scale, spells as a key, two plates at once with the hireling, sneaking
  past, the key on a creature, three shards of a seal, a timed run, day and night or ebb). Rules: never stuck (a
  lever that resets every block room; the editor tries that every plate can be reached), the way on never hangs on
  a puzzle unless a whole place sets it on purpose, hints only in the world (walls, books, rumours), a spell as key
  always has another way too (one source is never the only one). Creatures and hirelings press plates too.
  New module `puzzles.py`, state per place on the map; example rooms in `pieces/` so puzzles come without Nilio's
  drawings too.
- **More doors** (Nilio, 31 October 2026, "ga"): `+` stays the way in that is always used (it may be left out);
  the sign `'` is a door that may be used, as many as drawn. `DOORS: 1-2` (1, 1-2, 2-3 or all) says how many the
  generator opens; K5 joins the rest of the level at those, the others become wall, so a room differs per world and
  can be a way through. The check: each door in a straight wall, at least one `+` or `'`; with two doors or more the
  way from door to door may not hang on anything that can shut (bars, a lever, a puzzle): a puzzle room is set to
  1 door. Built first in B2.
- **Whole places** (mockup 6): a map drawn whole, one of a kind; sizes 60 x 34, 80 x 50, 100 x 60, 120 x 70; floors as
  tabs, stairs find their twin; room slots `?` where the game sets a theme room each world; people who live there;
  a find of the place or one fixed item; a boss from the boss maker. "In the world": name, sign, terrain, whose
  land, zone, how many (one per world, or in some worlds), near a road, level; found on the map, by a rumour, a job,
  a line in an old book, or only by a job; the land around as drawn or fitted. `PLACE` blocks with `FLOOR` maps and
  `WORLD` lines in `places/*.des`; `drawnplaces.py` on the frame of `landmarks.py` (a fixed cell per seed, never on
  another site or road), rumours by `news.py`, jobs by `jobs.py`. Example place: Saint Odo's Rest.
- **Rounds.** A: tileset, screen, palette, tools, Ground and Things, undo, copy and paste, zoom, size, the check,
  new / open / save, writing the format; test part `editor` (every piece of `theme.des` read, written, read again and
  equal; the tools; the check; a screenshot). B1: events with switches, counters and wires, variety, creatures and
  lists, dressing, own tiles and things, Ctrl+R, Try; test parts `editor` and `pieces`. B2: puzzle things 1-26 in the
  game and example rooms; test part `puzzles` (a small solver solves each example room, the lever resets it).
  C: whole places, puzzle things 27-44; test part `drawn_places` (Saint Odo's Rest lies in the world, every floor is
  reached, its rumour goes round).

## Boss fights: what is left (approved 26 October 2026)

The kit, the library and the boss maker are built (`docs/built.md`, "Boss fights"). Not built yet, for a later
round: arenas dressed per place (tower top, temple nave and the rest) and the ways out other than the rotten wall;
the place that wakes or falls in after a few bosses; fights won another way (hold out, rescue, break it, escape);
bosses for the big one (a fish) and the relic job.

---

## Parked
- **The bard** (the Lark's Company): see docs/parked.md. Not until Nilio says so.

## Later (not planned yet)
- Crafts guilds: smith and weaponsmith (mend and improve), herbalist, hunter-tanner (hides and trophies).
- Leadership: more hirelings, a group buff. A house of your own, with taxes.
- World ideas proposed with round 5 but not chosen: smoke over villages seen from afar, birds flushing from woods
  before an ambush, vultures over fights, the world growing (new hamlets, logging, regrowth), worn paths,
  lighthouses and watchtowers lit at night.
