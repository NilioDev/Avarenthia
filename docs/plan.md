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
| **Approved: spell effects** | Parts 1 and 2 built 19 and 22 October 2026 (the toolkit, status colours, Wild Shape colours, the option, each school's own hand, the storm's white frame; see `docs/built.md`). Left: the weapon skills' effects, with the weapon skills |
| **Next: round 6 (on hold)** | Livelier settlements, each people in its own rhythm; the half-orc and goblin quarters. Waits until Nilio says go |
| **Approved: dungeons on their own land** | Built places that stand outside (temple, abbey, tower, fort, manor) start on their own play map with land around them; upper floors and cellars by stairs; each kind its own plan, bigger levels, wider halls, one telling thing per room, a mood line in the messages. Caves stay underground. Underground kinds their own plan too; hand-drawn pieces in data files and an editor for Nilio; classic dungeons from a random maker (rooms of many shapes grow onto the level, main ways 3 wide, narrow ways 1 wide, every passage from room to room). The random maker, the theme rooms, rivers underground and the pieces format are built (24 October 2026), and so are the temples, towers, barrows, abbeys, forts, manors, goblin places and the underground kinds' plans; the editor waits until much later (`docs/open.md`) |
| **Approved: cities that grew** | Cities and the metropolis are no longer a grid: they grow like old European towns round a heart that fits the ruler (cathedral and great market, a burgh, or an emperor's walled palace), with winding streets, row houses that share their walls, the line of an old wall as a ring street, a wall with towers and a moat. Flat harbour towns get canal rings. Bigger: a metropolis 360x220, a city 240x140. Each other people builds its own way (dwarves plan, halflings ramble, orcs grow rings of huts). Not built yet |
| **Approved: old places on the land** | More points of interest born from the made history: old battlefields, deserted villages, broken bridges, memorials, quarries, wrecks, hermitages, leper colonies, marks of the peoples; overgrown Varnish cities found only by walking, with hidden dungeons beneath. Then newer places (logging camps, war camps, beacons, lighthouses...). The old places of part A are built (24 October 2026), the Varnish too (25 October 2026); archaeology and the rest are not |
| **Approved: the great evils as storyteller** | One ultimate evil, the Hollow King, the old shadow of the Varnish in the hidden Sky-Seat; under him three servants per world (one light, one middle, one heavy, from 24 kinds), each pushing the realms and powers with its own goal; a slow clock and a clock of his attention; one long quest with relics, the chains and the Sky-Seat's five floors. Replaces `evils.py`'s growth. Parts 1 and 2 built 29 October 2026 (`shadow.py`, `skyseat.py`, eight kinds). Not built: the other sixteen servants in rounds 31-32 |
| **Approved: trade as a way to play** | Fairer money (dear goods bend harder, routes tire), famous goods of a region with good and bad years, master makers, contraband, barter, monster goods, spoiling, far goods, war trade, market news, the great fair, League rank; your own caravan of up to 3 wagons with crew; travel with, trade with and race the NPC caravans. Part 1, the money fixes, built 29 October 2026; not built: rounds 22, 26, and the great fair with the feast days in 28 |
| **Approved: boss fights** | Bosses fight like a turn-based soulslike: great blows marked on the ground with a countdown, a rhythm drawn from a deck, phases at two thirds and one third, a spent moment after the heaviest blow, breaking casts, helpers with a job, twins, sealed arenas with one hard way out, roaming bosses. A move library from our own spells and weapon skills, and a maker of bosses for jobs ("kill the mage in the tower"). Parts A and B, the kit and the library with every fixed boss and the roaming bosses, built 29 October 2026; not built: the maker and the job bosses in 23 |
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
8. **The northern lights' gift** (M): needs the barrows. Built 24 October 2026 (see `docs/built.md`); its light-feast moves to the feast days (round 28).
9. **The Rift and the Ashen Deep** (L). Built 24 October 2026 (see `docs/built.md`). 10. ~~The editor~~: taken out of
   the build order (Nilio, 24 October 2026: "pas voor veel later"); it waits in `docs/open.md`, "Dungeon editor".
   A pause after 5, 7 and 9; merge after 9.
11. **Old places from the history** (L): battlefields, deserted villages, memorials, hermitages and the rest of part A.
    Built 24 October 2026 (see `docs/built.md`).
12. **The Varnish** (XL): their cities and places, the hidden dungeons, the lore, the books, the riddles. Built 25
    October 2026 (see `docs/built.md`).
13. **Classes part 4: the epics** (L). Built 29 October 2026 (see `docs/built.md`). 14. **Trade part 1:
    the money fixes** (S). Built 29 October 2026 (see `docs/built.md`). Pause after 12, merge after 14.
15. **Boss fights part A: the kit** (XL). Built 29 October 2026 (see `docs/built.md`). 16. **Part B** (XL): the
    move library, the other fixed bosses, roaming bosses. Built 29 October 2026 (see `docs/built.md`).
17. **The great evils, part 1: the frame** (XL). Built 29 October 2026 (see `docs/built.md`); Archaeology adds its
    source of weaknesses when it is built.
18. **Part 2: the quest and the Sky-Seat** (XL). Built 29 October 2026 (see `docs/built.md`). Pause after 15, 16 and
    17, merge after 18 (Nilio, 25 October 2026: the great evils come right after the
    epics, in parts).
19. **Life skills part 1** (XL): the curve, Herbalism into Foraging, Smithing and Tailoring, the materials by tier,
    alchemy, brewing. Built 30 October 2026 (see `docs/built.md`). 20. **Part 2** (XL): beast parts, crafted powers, Unmake,
    master tests, perks, hirelings' gear, named beasts' dens, catching alive, the great masters. Built 30 October 2026
    (see `docs/built.md`).
21. **Archaeology** (M): needs the old places and Smithing; also a source for the servants' weaknesses.
22. **Trade part 2: goods and ways** (L): named goods of a region with good and bad years, master makers, barter,
    monster goods, spoiling, need far away, far goods, contraband, war trade, market news, rank with the Merchant
    League; after the life skills, because it leans on brewing, Skinning, Smithing and the named beasts.
23. **Boss fights part C: the boss maker and the job bosses** (L): the 15 bases, traits, names and rumours, "A price
    on a head" and bosses for the other jobs; after the life skills, so that beasts drop materials of their body for
    the crafts. Pause after 19, 20, 21 and 22, merge after 23.
24. **Cities that grew, part 1** (XL): human cities, the metropolis, canal and fortress towns, test `city_rules`. The
    bridges are not yet perfect (open.md, "City streets and bridges"); that does not hold this round up.
25. **Part 2** (L): dwarf, halfling and orc towns, bridges on the open land. 26. **Trade part 3: caravans** (L): your
    own caravan (wagons, crew, the road, raids, stables in the grown cities) and the NPC caravans' new parts (travel
    along, trade on the road, League rivals, robbing has weight). 27. **Round 6** (L): it lives in the new city maps,
    and refugees from the great evils fill them. 28. **Feast days** (L), with the light-feast (northern villages keep the first night of the lights: news, cheaper beds, a blessing at their shrine; its spec stayed with the northern lights in `built.md`) and trade's great fair. Pause after 24, 26 and 27, merge after 28.
29. **Old places part B and the 44 places of the peoples and powers** (XL), with the caravanserai for the caravans.
    30. **Places 45-64 and the seasonal places** (L). Merge after 30.
31. **The great evils, part 3: the other sixteen servants** (XL), each with its lieutenants, weakness, relic and lair;
    late, because many of them live in what comes before (the Rat King in the grown cities, the Lindworm under the
    dwarves, the Wild Hunt and the Hag with the feast days). 32. **Part 4** (XL) if one round is not enough for
    sixteen: then eight and eight. Merge after the last.
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

## Spell effects (approved; parts 1 and 2 built)

**Part 1 built 19 October 2026 as a quick win, part 2 on 22 October** (see `docs/built.md`): the toolkit (bolts with
a tail, bursts, drain, rising crosses, the zigzag), status colours on creatures, Wild Shape's colours, monsters'
arrows and spells, the option full/short/off; each school its own hand (rings and waves, Meteor's shadow and slanting
fall, the corpse that greys and rises, Morrak's Bargain, walls one stone at a time) and the one white frame of Call
the Storm. **Left:** only the weapon skills' effects, built with the weapon skills (proposal in the project files,
`magie/wapeneffecten/voorstel.md`). The spec below is the whole plan.

Approved by Nilio on 17 October 2026 after two rounds of animated mockups (project files `magie/effecten/`, 17 GIFs,
made by `magie/effecten_mockups.py` and `effecten_mockups2.py`; every spell's effect in `magie/effecten.md` and
`magie/effecten_rest.md`). Today a spell flashes once for ~0.2 s (`engine.py` `flash`).

- **A small toolkit every school shares:** bolts that fly cell by cell with a fading tail; impacts that open out in
  three or four frames (`*` `+` `·`); particles flying back to you (life drain); rising `+` (heals); rings and
  waves; lasting colour on a creature (burning flickers orange, frozen has a pale blue ground, poisoned pulses
  green, weakened is dimmed); living tiles (burning ground, ice walls, roots, thorns, bone walls, Ball Lightning).
  Big spells draw light in for a frame before they strike.
- **Each school its own hand:** Meteor throws its shadow first and falls in at a slant; lightning is a white zigzag
  that fades to yellow and hops target to target; a corpse `%` greys and rises as `z`; Morrak's Bargain pulls your
  own life out in red first. Monsters' spells use the same effects, so you see what is coming.
- **Small areas.** Ordinary area spells (tome rank 0-30) have radius 1, a 3x3; big ones (42 and up) and the guilds'
  top techniques radius 2; never more than 3, and 3 only for the heaviest (Morrak's Bargain, Army of the Dead).
  Spells that pick targets (Chain Lightning, Call the Storm, Tempest) are not areas. Firebolt hits only its target;
  Grasping Roots and Entangle make a 3x3 of roots.
- **Wild Shape stays `@`.** You keep your sign and take the beast's colours (bear: orange-brown on dark brown, wolf:
  white on slate grey), so you never lose yourself on the map; the shape and its turns show with your buffs.
- **Calm:** no effect lasts longer than ~0.4 s, a key skips it, the game never waits for one; no screen shake, no
  flashing screen except one frame for a great lightning stroke; colours from the school (`DISC_COLOR`). An option:
  effects full, short or off.
- **In the code:** a small queue of effect frames in `anim.py`, drawn over the map in the existing draw loop and its
  timer (`GameScreen.moving`); `flash()` becomes a one-frame effect, so all that flashes today keeps working.
- **Weapon skills' effects** (proposal with GIFs in `magie/wapeneffecten/`; built with the weapon skills): steel and
  dust, no school colour; a swing arc only on skills and critical hits (an ordinary bump stays the short flash);
  blood on Sever Artery and claws, and a bleeding foe leaves a red trail `,` for a few turns (Nilio, 22 October).

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
- **Events in pieces**: the when / if / then rules are built in the pieces format (24 October 2026). The editor that would draw pieces waits, much later (`docs/open.md`).
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

## Cities that grew (approved 22 October 2026, not built)

Approved in the thread on grown cities: "dit ziet er goed uit", the American grid "werkt niet in een RPG-wereld".
The Dutch proposal, the mockups and the mockup generators (they use the real tiles and `look.py`) are in the project
files under `steden/` (`voorstel.md`, `mockup_steden.py`, `mockup_metropool.py`, `mockup_volken.py`).

**Human cities and the metropolis** replace the grid of `towns.gen_city`. The map grows in the order a town grew:
- **The heart** fits who rules the place: a cathedral (cross plan, towers, churchyard) on the great market; a
  king's or baron's burgh with its own moat, the market at its gate; an emperor's capital gets a walled palace,
  court behind court on one axis with the throne hall in the middle (the only straight thing in the city).
- **Main streets** wind from the market to the gates, one gate where each road of the world map comes in. Only the
  great ways run from the market to a gate; every other street starts at its gate or square and joins the first
  street it meets (no bundles of streets side by side).
- **Old walls** that are long gone are ring streets round the old core (the metropolis has two).
- **Lanes** branch off the streets and wander until they meet another street; some end blind. Dense in the old core,
  wider apart towards the wall.
- **Squares** where quarters grew round a well, a parish church or a small market.
- **Houses** stand in rows: each is a rectangle with its front and door on a street, sharing side walls with its
  neighbours; deep and narrow in the core, lower with bigger gardens further out. What is left behind them is yard,
  garden and alley. Every house stays inside the wall (checked in code).
- **The wall** with square towers and a broad moat; a gate with a tower each side; a lane runs along its inside.
- **A river** from the world map runs through, tamed as the Amstel was: long straight reaches joined by turns of
  45 degrees, one width all through the town, a stone quay wall along both banks (drawn thin and pale on the land
  side, like the bridge parapets) and a quay street behind it. A metropolis lies on a broad river.
- **Nothing is built over the water:** a great building (church, town hall, guild hall) only stands where its whole
  plot is dry land.
- **Bridges** were few and mattered (Nilio, 22 October 2026: "meer dan een stel houten planken"): only the great
  ways and the ring roads cross the river (a metropolis has two or three bridges), and only where they truly cross
  from bank to bank, never where a street runs along the water; other streets end at the quay. Each is a stone deck with a parapet each side and piers with
  cutwaters in the stream, and has its own kind: the market bridge has statues along its parapets (Charles
  Bridge); the rest stand on broad piers with lamps. No bridges with houses on them: they do not read on the map. A
  stone bridge has its own look, never the double line of a wall: a deck of grey flagstones, and thin pale parapets
  standing in the water, drawn as half blocks (▐ ▌ ▀ ▄, quarter blocks on a slant) on the side of the deck. Canal bridges are short, with a parapet and a lamp at each end.
  Wooden planks stay only for small streams in villages; drawbridges and harbour piers are stone too.
- **How a bridge is laid** (Nilio): first a quay street runs along both banks inside the walls. Then the bridges are
  laid, straight from quay to quay: one below the market and one where each ring road crosses (two or three in all).
  A bridge lies at 90 or 45 degrees to the river, the way its road runs (ASCII has only 8 directions).
  Only then comes the street plan, made round the bridges: a great way or ring road that crosses leaves its curve a
  little before the river, runs straight over the bridge in line with it and takes up its course on the far side (a
  straight piece in a ring is fine: ASCII has only 8 directions). Any other way ends at the quay, which leads on to
  the bridge, so no road stops at the water. Every gate has a stone bridge over the moat, like the other bridges (wood looks
  untidy on the map): straight or at 45 degrees, in line with the road that leaves the gate, from the gateway to the
  far bank where the road outside takes it up, with a tower on the wall at each side of the gateway. The moat is
  broad (about 5), so the whole bridge with its parapets fits over it.
- **Every way leads on** (Nilio): a bridge carries a great way or a ring road, so at both ends it runs on into the town;
  lanes seldom end blind; a check floods the streets from the market and joins any piece that does not reach it.
- **Light at night** as now: lamp posts along the great ways, on the squares and on the bridges, lit by the
  lamplighters at dusk; hearth glow from the houses; the lanes stay dark.
- **Guild halls** of the eleven guilds stand on the great market or a main street; the secret ones in an ordinary
  house down a lane. Inns by the gates, barracks by the wall, temples on squares, each on a plot of its size.
- **Townsfolk, the watch, lamplighters and the rest** (`people_city`) move into the new map; a metropolis has more.
- **Sizes:** metropolis 360x220 (now 196x110), city 240x140 (now 150x80). The screen shows 80x51.
- **Canal towns** (after old Amsterdam and Haarlem, Nilio 23 October 2026): no grid, but far more ordered than
  other towns, and plainly a harbour. Half rings of canals round the Dam, every reach straight and every turn
  45 degrees (a horseshoe: long sides, slanting corners, a long bottom). Three canals about 20 apart, so each block
  holds two rows of narrow deep canal houses with gardens between. A stone quay wall along all water, a quay street
  with trees on both sides of every canal. The Dam (the square where the river was dammed) with the town hall,
  the Damrak harbour arm up to it, two old town canals beside it; the great church in the old town on dry land.
  The river comes in tamed (straight reaches, one turn) and ends at the Dam. Great ways run from the Dam straight
  out across the rings, square to every canal, with a stone canal bridge (lamp at each end) at each crossing; a
  few long cross streets do the same; short cross streets join quay to quay inside a block. The harbour front: a
  quay wall and quay street along the water, warehouses on it, stone piers into the harbour with ships moored
  along them, ships at anchor further out. The land side has a bastioned wall and a broad moat; meadows with
  ditches outside. Mockups `grachten*.png`.
- **Fortress towns** (after Zutphen): a town in a border land or under a warlike ruler gets a bastioned wall:
  pointed bastions at its corners and along long sides, their faces at 45 degrees, behind a broad moat, a stone
  bridge at each gate.
- **Crafts guilds** (Later) would each get their own street (smiths, tanners by the water), as in real old towns.
- Villages, hamlets and towns keep their own maker.

**The other peoples** each build their own way (mockups shown 22 October 2026, Nilio said "doe maar"):
- **Dwarf cities:** built to a plan, the only straight city: the gate of the hold carved in the mountain face, below
  it terraces in rounded half rings like the rows of a theatre, a ledge and a street on each, rows of alike stone
  houses, the Great Stair on the axis with four lesser stairs, the forge square half way down (the great forge hall,
  the smiths' guild hall, the founder in stone), the cart line on the lowest terrace, a wall with square towers.
- **Halfling towns:** a hedge ring, no wall; paths that ramble; hills with homes dug into their south faces (round
  door, round windows); little houses with vegetable gardens; the green with the party tree and lanterns, the
  Keepsake Hall and the inn at its side; orchards and a pond.
- **Orc towns:** a palisade with sharpened stakes before it and watch platforms at the gates; the chief's longhouse
  in the middle with the fighting pit before it and totems round it; round huts of hide and timber in rings along
  mud paths, door to the path; fire pits, drying racks, middens, pens, the smith's open forge.
- The city under the Elder Tree, gnome hamlets, dwarf holds and villages, and the hostile camps stay as they are.

**Bridges in the open world, in each people's style** (Nilio, 22 October 2026): the same rules hold outside the
towns. Where a road crosses a river on a land map, the bridge is laid first, straight or at 45 degrees, and the road
runs over it in line. Who built it shows:
- **Humans:** stone arches with a flagstone deck and thin parapets; on lesser roads a timber trestle bridge; now
  and then an old stone bridge with a span fallen in (a ford nearby).
- **Dwarves:** dark granite, massive square piers, a low solid parapet, a brazier at each end; they also span chasms.
- **Elves:** a bridge grown of living roots and branches, leafy rails, glowmoss lanterns.
- **Halflings:** small humpbacked stone bridges over brooks, flower boxes on the parapets.
- **Gnomes:** a copper bascule bridge that lifts with a whirr of gears when a boat comes.
- **Orcs, goblins and other tribes:** logs lashed with rope, stakes at the ends; rope bridges over ravines.
- **Lizardfolk:** reed walkways on stilts across the swamp.

**City rules, checked by machine** (Nilio, 23 October 2026: "iedere keer komen we hier op terug"). Every rule Nilio
sets for towns becomes a check in code, run on many seeds before a mockup is shown, and in the build the same checks
become a test part `city_rules` (every kind of town, several seeds). A map that breaks a rule is a bug, not taste.
The checker for the mockups is `steden/controle.py` in the project files. The rules so far:
- A way that crosses the river has a bridge; a way with no bridge ends at the quay on both sides.
- No two streets run side by side with a thin strip between: the strip is paved into a little square.
- A paved square lies round every church and cathedral.
- Every bridge, straight or at 45 degrees, has a straight way in line with it at both ends (5 cells; 3 at a canal).
- Nothing is built over water: no house, hall or church on a river or canal.
- Every street inside the walls joins the rest; no loose pieces.
- No gate opens next to the river; every gate has a stone bridge over the moat and a straight road out of 12
  cells in line with it, then the old road joins its end. Where the land runs out at the map's edge, the gate
  moves along the wall; if there is no good place, that way has no gate.
- A bridge crosses the water, it never runs along it: at least 40 degrees off the way the water flows.
- How a crossing is made: the bridge first, then the straight road over it, then the joins to the street plan.

## Old places on the land (approved 23 October 2026, not built)

More points of interest, so the world looks old and lived in. Approved in the thread on points of interest: "we gaan
eerst A doen, alle ideeen klinken goed". Details and the full list (also the newer places, part B): project files
`poi/ideeen.md`. Each place is one world cell with its own play map (as the wonders and oases), and what matters is a
tile used with one key or a bump. Not the same as what exists: the fresh battlefields and plundered villages of
`living.py`, the hidden places of `hidden.py`, the planned temples, forts and barrows.
- Part A's old places (battlefields, deserted villages, broken bridges, memorials, quarries, wrecks, hermitages,
  leper colonies, the peoples' marks) are built (24 October 2026), and so are the Varnish: their cities, places,
  hidden dungeons, lore, books and riddles (25 October 2026); specs in `docs/built.md`. Still to build here:
- **Archaeology, a new life skill** (approved 23 October): dig spots on old places, a tile you see once you have the eye
  for it; the higher your rank, the more spots you see and the less you break; learnt only at places of your own height.
  It gives three things: (1) fragments of lore for the chronicle, belonging to five old riddles that grow as small
  chapters in The Old Days with their gaps named (how the Sky-Seat fell, who the Hollow King was, where the orcs came
  from, what lies in the vaults, why the dead were bound); a riddle made whole is a lead to a unique hidden place, and
  libraries, stones and rumours stay other ways to that knowledge; (2) pieces of star-iron and old things that a smith
  mends, a mended piece carrying an old power (Smithing's found powers), so finds stay rare and the smith's work counts;
  (3) a modest income: collectors and city libraries buy finds and old coins. Its place in the life skills order is
  still open. Already built with the Varnish (25 October 2026): the riddles and their pieces (`world.varnish['src']`
  says where each comes from; archaeology adds digging as one more source), the Varnish fragments and the curio
  'stariron' (a shard of star-iron, for the smith).
- **Where it goes in the build order:** see "The build order" at the top (rounds 11, 12, 21, 28, 29, 30).
- **Then part B** (also approved, after A): logging camp at the elven forest's edge, charcoal burners, peat cutters and
  salt pans, a realm's war camp, refugee camp, beacon hills, lighthouse, a baron's toll bridge, caravanserai,
  prospectors' camp after a Starfall, a lord's hunting lodge.
- **Places of today's peoples and powers** (all 44 approved 23 October; `poi/volken.md`), fixed in the wild:
  the realms (a boundary stone moved at night, a lone inn on a long road, a mill, a bridge chapel, lime kilns); the
  Church (a pilgrims' chapel up a rock, a tithe barn, a holy well, a plague cross); the Watch, companies, revolt and
  pretender (a blockhouse with wanted posters, a company's winter quarters, an outlaws' clearing, the pretender's
  hiding place); the witches (a cottage that heals and curses for a price that is not money, a hanging tree); raiders
  and riders (Fjordmen's boat-sheds, a jarl's ship-setting, a desert well, a pass cairn, a wreckers' false light to put
  out, cliff ladders, stone rows through the mist, star-path cairns); dwarves (an air shaft, a dwarf road through a
  mountain beside the pass, a grudge stone, a sealed door); elves (a watch tree, the burned grove, a grave tree);
  halflings (a hedge gate, a party field, pipeweed fields); gnomes (a bee garden, a lookout stump with a bell); orcs and
  the tribes (a duel ring, a warlord's cairn, a goblin midden, a rope bridge, a kobold lure, a gnoll bone yard,
  lizardfolk egg mounds); and for all (a shrine of a people long gone from there, a wayside market once a month).
- **More places** (45-64 approved 23 October; `poi/volken.md`): the land itself (a dragon's scorch, a lightning tree,
  a sunken boat in a clear lake, an old human mine, an avalanche field, flood lines on a village wall); people who live
  apart (a hedge wizard's tower, a charcoal family, a ferryman with a boat, a beekeeper's hill, a shepherd's bothy, an
  exiles' hamlet); where peoples meet (an old peace stone, a graveyard of all peoples, a trade bridge half human half
  dwarf, an orc farmstead); small secrets (a buried cache, a lovers' tree, a hidden still, the wrong milestone).
- **Seasonal places** (65-86 approved 23 October; `poi/volken.md`): spring (a salmon leap with bears, a flood lake with
  a family on a roof, a lambing fold, bird cliffs, a blossom orchard); summer (what the drought shows in a sunken lake,
  a tournament field, a harvest camp, a travelling fair that moves on); autumn (a rutting ground, a mushroom wood, a
  goose marsh, vineyard slopes, a pannage wood); winter (a frost fair on the river, an ice road over a lake, the
  herders' winter camp, a wolf winter, a snowed-in inn on a pass); old feasts that still work (on the longest night the
  standing dead turn to the Sky-Seat, on one spring day all wind towers whistle, Thessa's harvest stone).
- **Feast days** (approved 23 October, "klinkt goed"; `poi/feestdagen.md`), after real feasts from all over the world
  with names of our own. Not everywhere (Nilio): each feast belongs to a region, a people or a faith and is kept only
  there; Ruin Night (new year, the anniversary of the Ruin: lights out at midnight) and Hearthnight (the longest night)
  are kept by all humans. The name stands with the date; each feast shows in the town or on the land, gives one or two
  things to do with a key or a bump, and moves prices fairly. The handbook gets a table in its chapter on the year.
  The heartland and the west: the Masking (carnival: a Fool King, masks that hide who you are), the Lean Month, Greening
  Day, Blossom Eve, Last Sheaf, the Naming (speak a ghost's name and it lies down), Lantern Walk, Wanderer's Eve. The
  rest of the world: First-Footing, the Ship Burning, the Leaping, Colour Day, Wetting Day, the Thirst Month, Lantern
  River, Moonwatch, Marigold Days, Eight Lamps, Kite and Thunder, Sun Rope, the Rising, Walpurgis Hill. The realms (the
  Oath Day, the Day of the Fallen, the Fair of Skell) and the peoples (the Tapping and Founders' Quench of the dwarves,
  Starsong, the Long Table, First Frost, Night of Tusks, Swap Day, the Shine, the Hatching).
  - **Wanderer's Eve for the player:** on the night of 5 Longnight, in a heartland town with a temple or shrine of Skell,
    bump the hearth of the inn (or the tavern, or the temple's sleeping hall) and choose "Set your boot by the hearth"
    (EV.ask; without boots it is a sock); then sleep there that night. Other boots already stand by the hearth those days. In the morning the message line says what was in your boot, from your year since the last one: honest
    (no crime) a small thing, an apple, a few copper, or a rhyme that is a rumour of a place you did not know; devoted to
    Skell as well, a few days of his luck; stolen or wanted, a lump of coal (worth nothing, except one coal for a smith).
    Who does it, the game never says.

## The great evils as storyteller (approved 25 October 2026; parts 1 and 2 built 29 October 2026, not built: rounds 31-32)

The great evils become the world's storyteller, as in RimWorld: one shadow with a goal, and the world lives round it
whether the player joins in or not. Worked out with Nilio in the thread "Grote kwaden als verteller"; the Dutch
proposal with every servant: project files `kwaden/voorstel.md`. Replaces the growth with your level in `evils.py`;
its blight, hunters and whispers stay (the whispers go over the rule "no taunts" again).
- **The Hollow King** (from the riddles: made by the Varnish mages of star-iron, the winds and the bound dead) is the
  one ultimate evil, in every world. He sits in the piece of the Sky-Seat that never fell, a scar of the Varnish
  times that nobody remembers: bound winds keep it hidden in mist and storm; at sea you see a whirlpool and hear bells.
  His goal is to return. Only he is of the Varnish; the servants are of after them.
- **His land** is the coast facing the Sky-Seat (its place differs per world). As he wakes it turns his: blight, the
  bound dead, cults, empty fishing villages. Above it the sky darkens; the glow and the storm round the Sky-Seat grow
  with every broken seal, seen from the coast.
- **Three servants per world**, from 24 kinds, one of each weight, each in its own part of the world and on its own
  land (no Ifrit without desert, no Lindworm without dwarves); never two that want the same.
  - **Light**, awake from the start, only in its own land: Brood Mother, Wendigo, Ifrit, Nightmare (the Mare), Great
    Wolf, Gorgon, Wild Hunt, the Hag in the walking hut.
  - **Middle**, wakes halfway, a few baronies or a coast: Dragon, Drowned One, Rat King, Queen under the Hill (fey,
    not elven), Vampire Count, Keening Woman (banshee), Thunderbird, Lindworm.
  - **Heavy**, wakes late, a whole realm or more: Lich, Warlord, Fallen Mage, Sold King, False Prophet, Debt Lord,
    Giant King, Demon Prince.
  Each has the same set: one goal with one lever in the world, three lieutenants, one weakness, one relic. Only the
  reach differs, and everything grows from its own land, barony by barony. No people is wholly evil: some orc tribes
  refuse the Warlord, most glades fight the Queen under the Hill, part of the Church stays true.
- **The levers are the existing systems** (`realms.py`, `powers.py`, `seasons.py`, the economy, the news): a claim,
  a revolt, a war, hunger, debt, plague. At most one push per realm per month; the realms push back (an alliance, a
  levy, the Church's order). No doubled systems: the Warlord becomes the Gorvash, the Sold King is one of the kings
  who turns. New: a barony can be held by a servant, with its own colour on the realms layer.
- **Two clocks.** A slow one always runs (over years the servants grow a little, a village falls now and then, the
  news travels). The attention clock runs only when the player meddles (a lieutenant killed, a lair entered, a
  weakness learnt, a battle fought against him): hunters, faster plans, the next servant wakes sooner. It cools when
  you leave him alone and has a ceiling (each step up after a pause). Attention belongs to the world, not the player
  (in co-op he notices the group). Meddling pays: lieutenants' gear, standing with the realms, knowledge.
- **Only the player** can kill a servant or the Hollow King; the world can hold him back, never stop him. Named NPC
  heroes ride to the lairs: now and then they kill a lieutenant (heard through the news), never a servant; their grave
  becomes a place and their journal tells what they knew. Battles become places on the map (fight in them, or plunder
  them after). Refugees walk the roads, cities fill up, prices rise.
- **Lieutenants**: three per servant, drawn from a pool per kind, each with a place of its own in its servant's land
  (a fort, a camp, a tower). Not needed, but each one dead weakens its servant (fewer hunters, a weaker lair). One who
  survives you comes back scarred and promoted; he does not talk.
- **Weakness and relic**: one fixed weakness per kind, found from two or three sources (the riddles, libraries,
  Archaeology, a dying hero), with a real edge (the Lich's phylactery: leave it, and she comes back). The relic a slain
  servant leaves is a key with at most one small power (the loot rule holds); one can also be won elsewhere, harder.
- **The quest**, one heavy road as in The Lord of the Rings. The mist parts and the Sky-Seat comes on the world map
  when you know the truth or the first servant breaks a seal (each servant that reaches its goal breaks one). The
  relics let you through the mist. A long road through his land to the coast, no quick travel, a skipper who dares the
  whirlpool, your hirelings as the company. The Varnish chained the city down with star-iron chains to sea rocks and
  the cliff: you climb one (its own map: gusts, broken links, things that hang there), then the underside (breaking
  glass, wind that throws you off the edge, falls to the sea as in `towers.py`). The Sky-Seat is five floors of glass
  and bronze, from the under-city through the hall of the winds and the halls of the dead to the throne; a beacon on
  each floor. The last fight has three phases (the winds, the dead, himself); each relic you bring makes one lighter.
- **Dying there** (no point of no return): he keeps those who die in the Sky-Seat, so the priests' raising costs more
  and you wake on the mainland. Your body rises as your **shade** with your backpack (what you wear stays with you, as
  now): an echo, weaker than you, that does not heal; beat it for your things. What you opened stays open (mist,
  seals, chains), the slain stay dead, he sends a few new bound dead, a floor with its beacon lit stays calm. A shade
  rises only where the dead are bound: his land, a Lich's land, barrows, crypts, the Rift; a fallen hireling too.
- **If he wins**: the Long Night. The sky goes dark, his coast spreads, cities become strongholds, prices climb; he can
  still be beaten, only harder. You play on. **If you win**: one closing screen, then you play on in a world that
  heals: the blight lifts, the chronicle names you, the barons fight over the freed lands. No new ultimate evil. After
  a servant falls: a scramble for its baronies, its lair a ruin, your name in the chronicle.
- **Where it shows** (the UI rule): a journal tab "The Shadow" (what you know of him, the servants and lieutenants,
  kept on the player), a world-map layer (blight, lairs, hosts, seals), the line under the map in his land, a handbook
  chapter. No new key. `history.py` writes his first rising and fall so the chronicle and the lore agree.
- **Built in part 1** (round 17, `shadow.py`): the coast, the three weights, both clocks, the levers, held baronies,
  lieutenants, weaknesses, relics, heroes and their cairns, the Shadow tab and layer, for eight kinds (Brood Mother,
  Wendigo, Great Wolf, Dragon, Drowned One, Lich, Warlord, Fallen Mage). Left for part 2: the mist and the Sky-Seat
  on the map, the relics as keys, the road, the skipper, the climb, the five floors, the last fight, the shade, the
  Long Night and the healing world; `history.py`'s first rising. All built in part 2 (round 18, `skyseat.py`).
- **Left for rounds 31-32 besides the sixteen kinds**: a fallen hireling rising where the dead are bound, refugees on
  the roads, the barons' wars over freed lands as real wars (now news), the relic won elsewhere besides the Star-Iron
  Key.
- **Still to write while building**: the climb's map; the other sixteen kinds' pools, weaknesses and relics.

---

## Trade as a way to play (approved 25 October 2026, not built; rounds 14, 22, 26 and the great fair in 28)

Nilio (thread "Handelssysteem en waren doorlichten"): trade should be a full way to play the game, for players who
want to play it differently. Builds on `economy.py` (19 goods, stock-driven prices, NPC caravans in `wanderers.py`).

**Fixing the money first:** built 29 October 2026 (round 14, see `docs/built.md`).

**Small to great** (Nilio: begin small and grow). A trader climbs a ladder, each step paid for by the one before:
a peddler's pack (30) with cheap goods from village to village (grain, salt, ale, wool: a few silver a trip, but
safe and sure), small supply orders from a village's board; then a pack mule, then a cart; then wagons, crew and League
rank; at the top the dear goods, named goods, masterworks and far goods. The road is long (Nilio); where it ends (a trader's goal beyond the League title) is for later. Capital is the gate, nothing else: dear goods
cost too much to buy in bulk early, and small towns hold only a few of them. Neighbouring villages differ enough that
the first short trips always pay a little.

**Goods with a name.** Each world picks 12-15 famous goods of a region (`world.areas`), named after it: Amber Coast
Wine, Thornwood Mead, Highfells Wool, halfling pipe-weed, one dwarf hold's stout. Dearer than the plain good, best sold
far from home, made known by rumours and news ("the duke drinks only Amber Coast"). The maker has only a few each
season. Good and bad years: a hail summer spoils a region's harvest (dearer), a good year makes a sought-after vintage.
Every kind comes from several regions and peoples (the rule: never one people or one place).

**Master makers.** In some towns a master smith, weaver, brewer or goldsmith makes a few masterworks a season (a
dress sword, a tapestry, a silver cup). Trade goods, not gear: no loot. Brought to a baron, a temple or a rich town that
asks; sometimes as an order ("bring me an Ironhills cup before winter").

**More ways to trade.**
- Contraband: a realm or the church bans a good (black lotus, untaxed salt, stolen relics); the Watch searches you at a
  city gate; Cunning hides it; a fence or the pirate cove pays well.
- Barter with peoples without coin: kobolds want shiny things, orcs salt and arms, elves only barter; what they give is
  sold nowhere else.
- Monster goods: troll fat, dragon scale, spider silk, sold to alchemists in the cities (ties into Skinning and the
  named beasts).
- Spoiling: fish, fruit and milk go off on the way, like ice melts; speed or salt wins.
- Need far away: a snowed-in pass village or a besieged city pays three times as much, if you get there.
- Far goods: silk, incense, porcelain and dyes come only by the big merchant ship or the oasis caravans.
- War trade: arms to both sides pays a fortune; when it comes out, it costs standing.
- Market news: a traveller or innkeeper tells what is dear far away; news a few days old, so it may have changed.
- The great fair: once a year one city's fair wants everything (with the feast days).
- Merchant rank with the Merchant League (the faction exists): better prices and the best orders; at the top a title
  and a League caravan to escort.
Left out on purpose (they do not come across in a roguelike): a shop of your own, a bank, shares.

**Your own caravan.**
- Buy a wagon at a wagonmaker: up to 3 (more with League rank), ~150 cargo each, each needs a mule or an ox (the ox
  pulls more and walks slower). The wagons follow you on the world map as a string ♦♦♦. It lives on the player.
- Crew: a driver per wagon on a weekly wage, guards from the hirelings (`mercs.py`). A steady cost, so a money sink too.
- The road matters: slow, slower off the road; no snowed-in passes, stuck in spring mud, no high fords; a ferry costs
  per wagon. You choose your route.
- Upkeep: the beasts eat fodder (grain from the cargo); now and then a wheel breaks: bump the wagon, mend it with Tools.
- At night the wagons stand in a ring on the map; a round of drink (brewing) keeps the crew glad; night raids happen.
- Raids: bandits, raiders or desert riders ask a toll or attack: a small fight map where the wagons give cover (like
  the pirates' deck). A wagon that falls loses its cargo.
- Bump the lead wagon: make camp, leave the caravan in a stable or caravanserai, look at the cargo, pay the crew. You go
  into a dungeon without it; it waits.
- Your caravan gets a name and people talk of it.

**The NPC caravans** (they exist: a town with plenty sends up to 40 of a good to the town that lacks it most; bandits
and armies at war fall on them; a robbed one never arrives, so prices stay high there). New:
- Travel along: pay a caravan to walk with its guards. Safe and slow, for a beginner without a wagon.
- Trade on the road: bumping a caravan also offers buy or sell, at its home town's prices.
- Rivals: League caravans race you; if they arrive first your cargo is worth less. You see them on the road.
- Robbing has weight: prices rise in that town, towns send more guards along, the Watch looks for you.

UI: named goods stand by their own name in the market list; the caravan is a sign on the world map named by
`guide.py`; its choices are one `EV.ask`; each new key gets one first-time tip. The handbook's trade chapter grows with it.

## Boss fights (approved 26 October 2026; parts A and B built 29 October 2026, not built: round 23)

**Parts A and B:** built 29 October 2026 (rounds 15 and 16, see `docs/built.md`). Still to build here: part C, the
boss maker and the job bosses; the arenas dressed per place (tower top, temple nave and the rest), the ways out
other than the rotten wall, the one thing a place hides that eases its fight, floors above that foretell the boss,
and the place that wakes or falls in after a few bosses (these four were not in part B and wait for part C).

Bosses now are sacks of life that roll a die each turn (summon, nova, leap), and their worst moves come without the
warning that a common spider gives. Only the Lord of Cinders in the Rift has real mechanics. This replaces the boss
rules in `engine.mon_turn` with one system. Worked out with Nilio in the thread "Bazen spannender maken"; the Dutch
working-out with every move, base, boss and game it learnt from: project files `bazen/uitwerking.md`.
- **Ground rule**: it stays roguelike combat. Strategy is rewarded, chance stays (hit or miss, damage, which move,
  when the rhythm breaks, where helpers come). What is marked on the ground is always true: chance is in what comes,
  never a false warning. No facing (a glyph shows no direction), no bosses bigger than one tile, no taunts.
- **Marked blows**: a great blow is announced in the log and its tiles get a dark red background; blows that take 2-3
  turns show a counting number on each tile. The number's colour says what to do: red step out, purple can be broken,
  gold stand in it (or the whole room is struck). Shapes: line, cone, ring, cross, a circle on you, the room save
  behind cover, a wave that sweeps, a circle that follows you until the last turn. Every marked blow leaves at least
  one free tile you can reach in time (checked when it loads). Small blows come unmarked, as now.
- **Hard to dodge by overlap, not by one blow**: two threats at once (the safe tile lies in burning ground or the next
  ring), set-ups before the blow (web, slow, ice walls, a pull), interrupt-or-step-away choices, a room that shrinks
  each phase, ground that fills up with what blows leave (a soft clock instead of an enrage timer).
- **Rhythm from a deck** (Gloomhaven): each phase has a deck of 6-8 moves by beat kind (small, set-up, great,
  heaviest, move, summon, rest, and the room's own beat); one is drawn per beat, a shuffle card puts all back; great
  moves keep their place so the skeleton holds (say every fourth beat). About one in five the rhythm breaks. The player
  learns it himself: the bestiary never tells the next move; a line in `l` about its stance changes with the next beat.
- **Phases** at 66% and 33% (two phases at 50% for roaming and theme bosses): new deck, often a changed room, new
  helpers; one log line and a short shake. A blow stops at a threshold, except a critical hit while it is spent or
  staggered: it breaks through (gold line and flash, the skipped phase's room trick does not come, a chronicle line,
  a small job bonus); never two phases at once, never the last threshold of a great evil.
- **Spent and staggered**: after its heaviest blow it stands spent a turn (more damage, more crits). Breaking a blow or
  hitting its weakness fills three dots; full, it staggers two turns. **Breaking**: 2-3 turn blows break by a stunning
  or silencing skill (Shield Bash, Knock Out, Skull Crack, Throat Punch, Cheap Shot, Stunning Stone, Push Back,
  Counterspell, Garrote) or by a tenth of its life in damage while it loads.
- **Resolve and the action count** (D&D): it shrugs off the first two holds, sleeps, paralyses or charms (two ◆ in IN
  SIGHT); it gets one extra small move per ally beside you.
- **Helpers with a job**, on fixed beats: warder (half damage to the boss while it lives), mender, channeler (feeds the
  next heaviest blow), guard, swarm, bearer. Its great blows hit its own helpers too: push them into the red.
- **Twins**: six kinds (shared life; the survivor takes all; opposites; swap; bound together; master and beast).
- **Threat**: small moves follow the threat of `mercs.py`; great blows aim at the highest threat but strike everyone
  in the red; marks and curses follow threat too; threat resets each phase. Hirelings and pets play the fight like a
  player (step out of the red, handle a mark, break a cast, stand in gold, warder first), better as they rank up;
  the orders of `h` count. A marked blow never kills anyone from full life.
- **End bosses**: a veil of mist at the door asks once; then the room shuts until it falls, with one hard way out (a
  rotten wall, a drop to the level below, a chain to climb, a rare scroll). No resting inside. Fled from, it heals and
  prepares against what you did (burnt: resists fire; broken often: Unbroken), up to four times. Arenas fit the place
  (tower top with edges, temple nave, cave lake, crypt, fort yard, throne hall, forge, library, bridge, flooded
  cellar, glade, ship's deck) and change by phase (collapse, rising water, lights out, burning floor, falling
  ceiling, crumbling edge, webs, wind, rising dead, ice floor, thorns, fog). Ground effects combine (water and storm,
  oil and fire, poison and fire, ice and fire, web and fire). Some places hide one thing that eases the fight
  (holy water, the chain key); floors above foretell the boss. After a few bosses the place wakes or falls in as you
  leave.
- **Roaming bosses** walk a level with their band, are heard ("Heavy steps, somewhere east of you."), leave tracks,
  use the terrain, grow by killing other monsters; flee and they follow, up the stairs too, and do not heal while they
  hunt.
- **Move library**: ~100 moves by role, shape, element and counter, from our own spells, weapon skills and monster
  habits (what you can learn, they can do). Each fixed boss gets its own set (worked out for Snagtooth as the teaching
  boss, the Rat King, Grolm, the Lich, the four great evils, the Lord of Cinders, the theme bosses).
- **The boss maker** for jobs (not the Hollow King's servants, who use the same kit): 15 bases (mage per school,
  necromancer, cult leader, witch, wild druid, champion per weapon, band leader, assassin, hunter, great beast in the
  Dwarf Fortress way of body, stuff and attack, dead lord, golem, chief of a hostile people, pirate captain, fey lord),
  a draw in steps with rules (one set-up and blow pair, one weakness, weight by level, fits the arena, fairness check),
  traits (armoured, warded, regenerating, twinned, unbroken, vengeful, swift, mirrored, bloodbound, commanding,
  haunting, hoarder, grudge-bearer, waller, arcane sentry, vortex, watchful, anchored), a name, title, deed and one
  rumour of a move or the weakness. Jobs: a new "A price on a head", and bosses for nest, shrine, missing, boats,
  big one, deserter, relic; harder contracts pay more. Some fights are won another way (hold out, rescue, break it,
  escape); human bosses may yield (kill, let go, hand over).
- **Loot**: each fixed boss has three named items (a weapon, an armour piece, a jewel or focus); after it falls you
  choose one, the other two broke (grades by the loot rule). Beasts drop materials of their body or stuff at random,
  the same for every class.
- **Where it shows**: a boss bar at the top of IN SIGHT (name, bar with thresholds, phase, what it does, helpers with
  their job), the gold name across the map at the first blow and "FOE FELLED" at the end, new tiles named by `guide.py`,
  first-time tips for the red ground and the shut room. No new key. Handbook: a part "Bosses" in the fighting chapter.
- **Build in three parts**: A the kit (marks, deck, phases, spent, breaking, helpers, bar, arena) with Snagtooth, the
  Lich and the Dragon; B the whole library, the other fixed bosses, roaming bosses; C the maker and the job bosses.
  The great evils' servants then use it.

---

## Round 6: livelier settlements (on hold)

Approved on 16 October 2026 for the next round after round 5; on hold until Nilio says go (17 October 2026). Everything must show as a tile or work with a bump.
What exists: a day rhythm (work and home), day and night watch, drinkers, children, the lamplighter, hearth glow,
doors shut at night, dogs, cats and livestock, job barks, hints, news through people.

### Everywhere
1. **Work you can see.** (Sparks at the anvil and chimney smoke built 19 October 2026.) A woodpile that grows;
   fields change with the season (bare, green, gold, stubble).
2. **Weather in town.** (Rain emptying the streets and filling the inn built 19 October 2026.) Bare fields in winter.
3. **Market day and rest day.** Built 22 October 2026 (see `docs/built.md`). Left for round 6: travellers and extra
   stalls on market day.
4. **The town reacts to the world.** A raid nearby means more guards, fearful talk and shutters; a war won, a feast.
5. **Small happenings to bump into.** An inn brawl, a runaway pig, a funeral procession, a pickpocket. Small, no
   menu, a little reward.

### Each people in its own rhythm
- **Humans**: the temple bell and market day (built 22 October 2026).
- **Half-orcs and goblins in human cities**: a slum quarter where they live as second-class citizens (beggars,
  night trade), and shanty camps in the wild.
- **Halflings**: many meals a day, so always walking home or to the inn; lanterns in the hedges in the evening;
  round doors locked early.
- **Elves**: a night rhythm: quiet by day, singing and light in the trees by night; archers at the butts.
- **Gnomes**: shy; when a stranger comes near they dive into their root holes and come out later; mushroom picking
  at dawn.
- **Dwarves**: no day underground, so shifts: a shift bell, miners walking in groups, carts on the line, the ale hall
  full after the shift.
- **Hostile peoples**: orcs spar in pairs, goblins squabble over loot, the kobolds' hoard visibly grows, lizardfolk
  bask by day and are sluggish at night and in winter (a chance for the player).

---

## Parked
- **The bard** (the Lark's Company): see docs/parked.md. Not until Nilio says so.

## Later (not planned yet)
- The dungeon editor (much later, after all open blocks; Nilio, 24 October 2026): see `docs/open.md`, "Dungeon editor".
- Crafts guilds: smith and weaponsmith (mend and improve), herbalist, hunter-tanner (hides and trophies).
- Leadership: more hirelings, a group buff. A house of your own, with taxes.
- World ideas proposed with round 5 but not chosen: smoke over villages seen from afar, birds flushing from woods
  before an ambush, vultures over fights, the world growing (new hamlets, logging, regrowth), worn paths,
  lighthouses and watchtowers lit at night.
