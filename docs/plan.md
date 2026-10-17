# The plan: where we stand

Kept up to date after every round. Built work is summarised here; the full specs of rounds 1-4 are in the git
history of this file (before 16 October 2026, 23:00). After each round: tests (seeds 1-3, smoke), push (CI builds),
a short Dutch report. Nilio plays afterwards and sends feedback.

Inspiration: Shadowdark (core book, Western Reaches, Cursed Scrolls 1-6), D&D, Pathfinder, Diablo, Final Fantasy,
WoW. Take the ideas, never the text, stat blocks or invented names.

## At a glance

| Status | What |
|---|---|
| **Built** | Rounds 1-5 (monsters and behaviours, named enemies, five guilds, the jobs, seasons and sailing); world shapes; the peoples' own lands; hostile camps; dwarf holds and mines; the bigger world with nine new biomes; small animations on the maps |
| **Approved: nature and wonders** | Waterfalls, cascades, great falls and rapids; hot springs, the tidal causeway; the Drifting Isles, the Starwater, the Thunder Anvil and fourteen more wonders, each a site with its own saved map. Not built yet |
| **Approved: place names** | A name maker per people for villages, towns, cities, holds, glades, hamlets and the hostile camps; human names by region; names that fit the land. Not built yet |
| **Next: round 6 (on hold)** | Livelier settlements, each people in its own rhythm; the half-orc and goblin quarters. Waits until Nilio says go |
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
- **Round 5: seasons, seasonal goods, a livelier world, sailing** (`seasons.py`, `economy.py`, `living.py`,
  `sailing.py`). Snow that comes and goes with a snow line (slow off the road), frozen lakes and rivers to walk on,
  thin ice in the thaw and fords running high with meltwater, passes snowed shut, leaves turning and bare woods
  (+1 sight), berries and mushrooms to pick in autumn, tracks in the snow, wolves near the roads and bears asleep in
  winter, mud on the roads in spring, streams running dry late in summer, grass fires, herders down from the high
  meadows in winter, Midsummer fires on the hills, short winter days. Apples and cider, wine, honey, wool and ice
  (it melts in your cargo), cheap at harvest and dear out of season. Battlefields with the dead to search,
  plundered villages that are rebuilt, a rival party of adventurers, ferries, crossroads shrines (give or steal),
  ships and a pirate ship at sea. Skippers hire out a fishing boat, coaster or merchant ship by harbour size;
  pirates board some voyages (fight on deck or give up the cargo; an armed escort keeps them off); a hidden pirate
  cove with a fence, a tavern and the captain. Not built: herds moving south (there are no herd animals yet).
- **Animations** (`anim.py`). Fires and forges flicker by day too, water glints, rivers run towards the sea, molten
  iron breathes, ore, gems and rare items catch the light, rings where fish rise (fishing is better there), wisps
  over the marsh at night, tainted land breathes, the portal and altar candles pulse, the lighthouse beam turns,
  hostile camps glow on the world map at night. The screen only redraws on a timer while one is in view.

---

## Place names (approved, not built)

Approved on 17 October 2026. Today almost every place name comes from a short fixed list: 22 city names for the
18 cities a world needs, so every game shows nearly the same cities; human villages are 24 x 14 parts for 85
villages (Ashford, Ashwick and Ashmere in one world); the hostile camps have 6 names each for 4-5 camps; elven glades
have 8 names for the 9 a world wants, so one glade is quietly lost. Halfling and dwarf villages already build names
from parts.

**One name maker** (`names.py`): for each people a small grammar of parts and patterns, with a small chance of a
fixed, hand-made name. Picked at random per world, never twice in one world (`world` keeps the used names). Names
are fixed when the world is made, so saves need nothing new. Every list that now caps how many places are made
(glades, gnome hamlets, camps, holds) stops capping.

**Names fit the land.** The maker looks at where the place lies: by a river -ford, -bridge, -wade; on the coast
-haven, -mouth, Port; in hills and mountains Dun-, -crag, -fell; in wood and marsh -wood, -holt, -fen, -mere. An
ending that does not fit the spot is not used (no -ford without a river).

**Humans by region.** The human lands get three ways of speaking, by where they lie on the map:
- **The north**: Norse-sounding (Thorby, Kettlethorpe, Ravensgarth, Skelwick).
- **The west**: Celtic-sounding (Caer Lewyn, Penmorrow, Trevellan, Llanfarren).
- **The heartland**: old English (Ashford, Market Hollin, Bramley Cross).
Cities take grander forms (Port Varen, Highmarch, Kingsbridge); villages plainer ones.

**The other peoples:**
- **Halflings**: the parts they have now, plus forms like "Puddle-under-Hill" and "Little Tumbling".
- **Elves**: flowing syllables for the cities (Ael-, Ith-, Syl- with -vael, -thiel, -ond); glades in plain English
  (Moonwater Glade, Starfall Hollow).
- **Dwarves**: hard syllables for the holds (Khaz, Karak, Dun, Zirak with -dum, -grund, -thar); miners' words for the
  villages (Flintcleft, Anvilbrow).
- **Gnomes**: cosy compounds (Moss, Toad, Acorn with -hame, -dell, -bottom).
- **Orcs (war camps)**: after the totem or the tribe (The Split Tusk Camp, Camp of the Red Hand).
- **Goblins (ravines)**: crude and plain (Ratgut Gully, Snot Gulch, The Grubcrack).
- **Kobolds**: shiny and small (Shinydig, Tinklehole, Glimmerburrow).
- **Gnolls**: after the pack (The Bone-Laugh Pack, Red Grass Camp).
- **Lizardfolk**: hissing syllables (Sslathaar, Ix-Hessa, Ossk Vael).
- Later, with round 6: names for the half-orc and goblin quarters in the cities and their shanty camps.

---

## Nature and wonders (approved, not built)

Approved on 17 October 2026 in the thread on natural phenomena. Mockups (GIFs in the game's own tiles) and the
script that drew them are in the project files under `natuur/` (`natuur_mockups.py`).

**Rules for all of them:**
- On the world map each one is **one cell**, like a village. The full look lives on its own play map.
- Each one is a **site** (`world.sites`). Its play map is made on the first visit (`gen_site_map`) and kept in
  `game.maps`, so it is saved, the same way oases and shielings work. Tides and night events come from the clock.
- **Random per world:** which wonders a world has, where they lie, and how their maps are laid out (from the world
  seed plus the site position); names are built from parts. Only a few great wonders have a fixed name, and each
  appears once per world at most.
- Each one must give the player something to do: a visible tile, used with one key or a bump.
- **Water must move:** rivers and pools flow everywhere (frames of about 190 ms). Falling water is made of strands,
  each with its own speed, thickness and gaps, never one pattern scrolling across the full width. Foam boils
  irregularly. Where falling water lands there are rings and splash.
- **Placement:** rivers rarely run straight out of mountain cells (`terrain.py`), so the waterfall placer looks for
  the steps where a river leaves hills or mountains. Expect only a few per world.

**Water:**
- **Waterfall**: a cave behind the falls, better fishing in the pool, mist drifting off. One great named waterfall
  per world.
- **Cascade**: falls in many low steps down a hillside (like Pongour).
- **Great falls**: a wide horseshoe curtain with rising spray (like Niagara or Victoria).
- **Rapids**: white water with boulders. Stepping stones are the crossing; falling in sweeps you downstream.
- **Hot spring**: bathe to heal; warms you in winter.
- **Tidal causeway**: a path of poles to an islet, passable only at low tide.
- **Frozen Stair**: in winter a waterfall freezes. Climb the ice to a ledge where something was left behind.

**Fantasy wonders:**
- **Drifting Isles**: rocks hanging over a vale. Super rare, and can appear in any ordinary biome (forest, desert,
  savanna and so on); the vale and the isle tops take that biome's look. The isles are drawn in full; the one the
  player walks under turns into its shadow only, like a roof vanishing. Not every isle has a fall. Falling water
  drains away: pool, brook, small lake, then a river off the map. A chain to climb up to an isle-top map.
- **Starwater**: a lake that shows the stars by day. A stair under it leads to its twin lake far away.
- **Thunder Anvil**: lightning strikes an iron spike on a hill; a weapon left there is blessed.
- **Hollow Hill**: at full moon a door opens in a green hill, with music inside. The fair folk sell strange things
  and take no coin.
- **The Unwintering**: a patch of spring in the middle of the snow, with herbs that grow nowhere else.
- **Undying Flame**: fire burning out of bare rock. What a smith works in it holds an edge.
- **Drowned Bell**: in a storm a bell rings under a lake. Only then can you swim down to the drowned chapel.
- **Star Well**: an old well with stars in it by day. Throw in a coin and wish; the wish is not always the one
  you meant.
- **Singing Stones**: a ring of stones that hums at dusk. Sleep in the middle and dream of a hidden place.
- **Northern lights**: green and violet light over the snow on winter nights in the far north. What it gives the
  player is still to be settled.
- **Starfall**: now and then a star falls at night and leaves a new crater with star-iron for the smith. Whoever
  gets there first gets it.
- **Wisp Fen**: blue lights over a marsh at night. Following them leads to old treasure or into the mire.
- **Singing Sands**: dunes that hum underfoot. Where the hum is loudest, a buried ruin can be dug out.
- **Glowing Bay**: on summer nights the waves break in blue light, and the fish bite better.
- **Green Well (cenote)**: a clear pool in a hole in the jungle floor. Climb down a rope and dive for old
  offerings.
- **Stone Wood**: a petrified forest. The trees cannot be cut; amber lies in the grit and sometimes a fossil to
  sell.

**For the monsters:** trolls caught in sunlight turn to stone.

**Dropped:** the Twin Kings, the Troll's Bridge, the mirage and the whirlpool.

**Shown but not yet decided:** stone arch over a river (a free crossing), lookout crag (shows the map around it),
fairy ring, ice cave at a glacier's edge, quicksand, bird cliffs (eggs in spring), and a use for the wonders that
are only for looking at today (geysers, tar pits, crystal hills, glowing mushrooms).

---

## Round 6: livelier settlements (on hold)

Approved on 16 October 2026 for the next round after round 5; on hold until Nilio says go (17 October 2026). Everything must show as a tile or work with a bump.
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
