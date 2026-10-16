# The plan: where we stand

Kept up to date after every round. Built work is summarised here; the full specs of rounds 1-4 are in the git
history of this file (before 16 October 2026, 23:00). After each round: tests (seeds 1-3, smoke), push (CI builds),
a short Dutch report. Nilio plays afterwards and sends feedback.

Inspiration: Shadowdark (core book, Western Reaches, Cursed Scrolls 1-6), D&D, Pathfinder, Diablo, Final Fantasy,
WoW. Take the ideas, never the text, stat blocks or invented names.

## At a glance

| Status | What |
|---|---|
| **Built** | Rounds 1-4 (monsters and behaviours, named enemies, five guilds, the jobs); world shapes; the peoples' own lands; hostile camps; dwarf holds and mines; the bigger world with nine new biomes |
| **Next: round 5** | Seasons on the world map, seasonal goods, a livelier world, sailing |
| **Then: round 6** | Livelier settlements, each people in its own rhythm; the half-orc and goblin quarters |
| **Parked** | The bard (docs/parked.md) |
| **Later** | Crafts guilds, leadership, a house of your own |

---

## Built

- **Round 1: behaviours, spiders, insects, humanoids with classes, named enemies** (`creatures.py`, `behave.py`,
  `named.py`). Grab, web, paralyse, swarm, acid, burrow, leap, formation, totem, curse, darkness and the rest;
  spider and insect families; goblin, kobold, orc, hobgoblin, gnoll, lizardfolk and underground classes in groups
  with leaders; three-layer descriptions and gender; named enemies with ranks, traits, fame, grudges and search areas
  with signs instead of a marker. Changed later: kobolds became folklore miners; the Kobold Dragon Priest is gone.
- **Round 2: the other monsters and aberrations** (`menagerie.py`). Undead, beasts by biome, oozes and plants, water
  folk, constructs, Morrak's spawn, fey, dragons and legend beasts, aberrations under our own names, family bosses.
- **Round 3: five combat guilds** (`guilds.py`, `mercs.py`). The Green Moot, the Hallowed Chapter, the Quiet Ossuary,
  the Order of the Still Hand, the Houndwardens' Lodge; disciplines Nature, Necromancy, Beastcraft; a tamed beast
  beside the hireling; two-guild techniques.
- **Round 4: the jobs** (`jobs.py`). 27 kinds: village work, the round-2 jobs, trade, war and crime, faith,
  exploring, the calendar (the Starfall, festivals), a sellsword's debt; givers by guild rank; village elders.
- **World shapes** (`heightmap.py`). Azgaar-like continent templates; the Sky-Seat stays; few islands.
- **The peoples' own lands** (`folk.py`, `deephold.py`). Halfling country with hill homes and hedges; hidden elven
  glades and the city under the Elder Tree; gnome hamlets under great roots; dwarf holds, villages, mines, digging
  and the cart line.
- **Hostile peoples' camps** (`tribes.py`). Orc and goblin war camp, goblin ravine, kobold caves, gnoll camp,
  lizardfolk stilt village: guards warn first, non-fighters flee, captives, the kobold toll.
- **The bigger world** (`lands.py`, `terrain.py`). 480 x 270; moor, old forest, birch wood, alpine meadow,
  floodplain, mangrove, mesa and canyon, oasis, karst with sinkholes, each with one effect; big patches broken up;
  named stretches of country; oasis camps and herders' huts; small wonders may appear twice.

---

## Round 5: seasons, a livelier world, sailing

Overworld only; the seasons inside settlements (fields, market day, rest day) belong to the livelier-settlements
round. The calendar stays as it is: 30-day months, 90-day seasons. What exists already: weather by climate and
season, blossom and falling leaves, aurora and fireflies, floodplains slow in spring, the autumn winter-supplies job.
What is missing is that the map itself changes. Everything below must show on the map or work with a bump.

### The land through the year
1. **Snow cover.** In winter the ground of the cold north and the mountains turns white; the snow line creeps south
   and downhill as winter deepens and draws back in spring. Off the road you walk slower; roads stay open.
2. **Frozen water.** Northern rivers and lakes freeze: you can walk across, a short cut. Fishing goes through a hole
   in the ice (bump it with your pole). With the thaw the ice breaks and the fords are impassable for a while.
3. **Passes snowed shut.** In winter a mountain pass becomes a tile of deep snow you cannot get through; villagers
   below warn you.
4. **Leaf colour.** Broadleaf forest turns gold and red in autumn and stands bare and grey in winter; conifers stay
   green. In bare forest you see one tile further.
5. **Wildlife.** Bears sleep in winter, wolves come closer to the roads, herds move south in autumn; berries and
   mushrooms to pick with a bump in autumn only.
6. **Short winter days.** Dusk comes earlier in winter, so you travel more in the dark.
7. **Pack ice.** The sea ice grows south in winter and closes the northernmost harbours.
8. **Tracks in snow.** Beasts and monsters leave tracks on snow tiles; follow a wolf back to its den.
9. **Thin ice.** Early in spring the ice cracks first (a warning), and gives way if you go on.
10. **Mud season.** With the thaw, dirt roads are slow in spring.
11. **Drought.** Late in summer small streams and pools dry up into dry beds; oases shrink.
12. **Grass fire.** In dry grass a fire can break out in summer and spread visibly over the tiles; burnt land grows
    back in spring.
13. **Herders move.** The herders' huts on the high meadows are lived in only in summer; in winter the flocks are
    down by the villages.
14. **Midsummer fires.** On Midsummer night fires burn on the hilltops, seen from far away (like the Starfall, one
    fixed night a year).

### Goods by season
Each good is cheap where and when it is harvested, dear elsewhere and out of season. Small margins: trade pays,
but it is no gold mine.
- **Grain**: cheapest after the harvest (Harvestmoon), dearest in late winter.
- **Fruit and cider**: autumn, the temperate middle.
- **Wine**: harvested in autumn in the warm south; it keeps, so you can hold it until it is dear.
- **Honey**: summer, heath and meadows.
- **Wool**: spring shearing in the hills and high meadows.
- **Ice**: cut in the north in winter; carry it south in summer, but it melts in your cargo on the way.
- **Furs**: dear in autumn, cheap in summer.

### A livelier world
- **Battlefields and ruins** (18). Factions clash on the map: a battle leaves a battlefield, and a plundered village
  lies in ruins for a while before it is rebuilt.
- **Rival adventurers** (21). A rival party roams the land and sometimes clears a dungeon before you get there;
  sometimes you find their camp, sometimes their bodies.
- **Ferries** (22). On broad rivers a ferry with a ferryman: bump him, pay a few copper, cross.
- **Crossroads shrine** (24). Travellers leave offerings: add one yourself, or steal them, with consequences.
- **Ships at sea** (25). Ships sail visibly between the harbours on the world map, pirate ships among them.

### Sailing (hire only, no ship of your own)
The harbours already have boats and ships by size (harbour.py); now they sail.
- **Hire a passage**: bump a skipper on the quay and pick a destination from a list. Days pass on the voyage, as on
  the dwarves' cart line, and your cargo comes along.
- **Three kinds of ship, by harbour size**:
  - **Fishing boat**: any harbour, hamlets too; cheap, short hops along the coast, little cargo.
  - **Coaster**: from villages to villages and up; further, more cargo.
  - **Merchant ship**: only between cities and metropolises with a deep berth; most cargo, the longest routes.
  So a remote hamlet means changing to a fishing boat.
- **Seasons at sea**: fewer sailings and more storms in winter; pack ice closes the northern harbours.
- **Pirates**: on some routes your ship can be boarded. That is a real fight on deck (a deck map, with your hireling
  and the crew), or you give up your cargo. An armed ship or an escort costs more, and almost nobody attacks it.
- **Pirate coves**: one or two in the whole world, well hidden in a fjord, the mangroves or on a reef islet. Found
  through rumours, a captured pirate with a chart, or by following a pirate ship at sea. Inside: a fence who buys
  stolen goods and sells contraband without questions, a tavern, and the pirate captain. Trade there, or root it out.

---

## Round 6: livelier settlements

Approved on 16 October 2026 for the next round after round 5. Everything must show as a tile or work with a bump.
What exists: a day rhythm (work and home), day and night watch, drinkers, children, the lamplighter, hearth glow,
doors shut at night, dogs, cats and livestock, job barks, hints, news through people.

### Everywhere
1. **Work you can see.** Sparks at the smith, smoke from the baker's chimney, a woodpile that grows; fields change
   with the season (bare, green, gold, stubble).
2. **Weather in town.** Rain empties the streets and fills the inn; bare fields in winter.
3. **Market day and rest day.** One market day a week (extra stalls, travellers, better selling prices); on the rest
   day the temple is full and the shops are shut (`calendar.weekday()` is still unused).
4. **The town reacts to the world.** A raid nearby means more guards, fearful talk and shutters; a war won, a feast.
5. **Small happenings to bump into.** An inn brawl, a runaway pig, a funeral procession, a pickpocket. Small, no
   menu, a little reward.

### Each people in its own rhythm
- **Humans**: the temple bell and market day.
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
- Crafts guilds: smith and weaponsmith (mend and improve), herbalist, hunter-tanner (hides and trophies).
- Leadership: more hirelings, a group buff. A house of your own, with taxes.
- World ideas proposed with round 5 but not chosen: smoke over villages seen from afar, birds flushing from woods
  before an ambush, vultures over fights, the world growing (new hamlets, logging, regrowth), worn paths,
  lighthouses and watchtowers lit at night.
