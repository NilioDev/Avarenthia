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
| **Approved: herds, hunting and the crafts** | Herds that stay off the map until you are close, hunting on its own small map, skinning, cooking from what you find (64 dishes, learned by trying or hearing), tanning and leatherworking. Not built yet |
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

## Herds, hunting and the crafts (approved, not built)

Approved on 17 October 2026 in the thread on herd animals. Mockups and the script that drew them are in the project
files under `kuddes/` (`kuddes_mockups.py`, seed 6; `voorstel.md` is the Dutch version of this section). Today there
are no prey animals: beasts drop Raw Meat 35% of the time, there is no cooking, leather armour is only loot or shop
stock. Planned as one new module (`hunting.py`); new tiles (hoof tracks, stretching frame); `SAVE_VERSION` goes up.

**The world map must not fill up with animals.**
- Game is a number per stretch of country (`world.areas`): how many herds graze there. It is not drawn.
- In normal sight you see only hoof tracks `:` where a herd passed; they fade in a day or two, like tracks in the snow.
- The herd itself (one `q`) shows only within 4-5 cells (a little further on open land and with a higher Hunting,
  less in woods). Walk away and it is gone: it is never remembered on the map.
- Only 2-4 great herds per world really travel, with the seasons: reindeer, wisent and wildebeest go north and up to
  the high meadows in summer, south and down to the valleys in winter. Wolves and gnolls follow them. This is the
  "herds moving south" left open in round 5.
- Hunting a herd sends it on and lowers the game there for a while.

**The animals** (real animals only). All hoofed animals are `q` (like the bear and the boar now), each with its own
colour; the leader of a herd is a `Q`. Small game (hares, grouse) never shows on the world map: only on the hunting
map or through foraging.

| Land | Animals (colour) | Behaviour |
|---|---|---|
| Forest, old forest, birch wood | red deer (red-brown), wild boar, hare | the boar charges if you come too close |
| Taiga, marsh | elk (dark brown) | kicks back |
| Tundra | reindeer (grey-white), travels | flees far |
| Steppe, grassland | aurochs/wisent (black), travels; wild horses (light brown) | the bull charges |
| Mountains, alpine meadow | ibex (grey), wild goats | flees into the rocks |
| Savanna, desert edge | gazelle (sand), wildebeest (slate grey), travels | fast, skittish |
| Cold north | fox, ermine (small game, fine fur) | |

**Hunting** happens on its own small map. Walk into the herd on the world map: a hunting ground like an encounter
map now (`gen_wild`). The herd grazes; the leader watches. The wind is in the log (and one arrow at the edge): with
the wind in your face they do not smell you; tall grass and trees hide you. No sneak key: the closer and the more
open, the sooner they see you. Bow (Tab to aim) or spear; a hit animal runs on a few steps, a blood trail `·` leads to
where it falls `%`. The rest flee off the map.

**Skinning** (its own life skill). Walk into the carcass with a knife or dagger: cuts of meat (named by animal:
venison, boar, aurochs...), a hide, sometimes antlers, horn or tusks. Hide quality by rank: torn, rough, good, fine.
It works on the existing beasts too: wolf pelt, bear fur, crocodile hide. No loot piñata: a beast has a hide, not a
sword.

**Tanning takes time; this is how the game shows it.**
1. A fresh hide rots after two days; its name says how long it has left (*Fresh Wildebeest Hide (1 day)*).
2. In the field: walk into a stretching frame `╬` (a tool you carry, like the tent) with salt in your pack: an hour of
   scraping and salting, then it is a *Salted Hide*, which does not rot. Salt is cheap in every village, or scoop it
   from the salt flats.
3. Then either the **tanner** in a village or town (you pay, and the leather is ready for you after 3 days: you must
   come back), or **yourself** with oak bark (bought, or foraged in woods): the salted hide tans in your pack and
   counts down (*Tanning Hide (4 days)*) and becomes leather after 5 days. Cheap, but you carry the weight.
4. **Leatherworking** (life skill) at a workbench in town (the tanner's or saddler's): leather armour, boots, gloves,
   a quiver, a waterskin, mending a tent. Plain good work, no magic; higher rank, better stats.
- Money: plain hides sell for little; fine fur (fox, ermine, bear) sells much better in cities and the cold north,
  which is trade. The tanner, salt and the workbench cost coin.

**Hunting** (life skill): reading tracks (how fresh, which animal), seeing herds from further off, being noticed later.

**Cooking** (life skill): no fixed recipes.
- You start knowing only Roast Meat and Grilled Fish. Rank never gives recipes: it means fewer burnt dishes, more
  portions from one pot, stronger and longer buffs, and at a high rank tasting what is in someone else's simple or
  hearty dish (then you know it).
- Walk into a fire (camp fire, fire pit, an inn's hearth): the dishes you know and have everything for, and at the
  bottom **Try something new**: pick up to three things from your pack, one short choice at a time ("That's all").
  - A match teaches the dish: *"You have made something good: Hunter's Stew. You will remember how."*
  - One thing short gives a hint: *"Not bad. It wants something sharp."* (onion), *"... something sweet."* (honey,
    apples), *"... something green."* (a herb).
  - Nothing right gives Camp Mush: edible, half the food; the ingredients are gone.
  - An unknown plant may go in; you find out what it was when you eat it. Deathcap in the stew is deathcap in you.
- **Hearing it from others is rare, and only simple local dishes.** About one inn in five has a keeper who shares a
  recipe: his simple local dish, with what grows and lives there. Herders, hunters and fishers on the road share one
  now and then. The peoples have their own kitchens, shared only with friends, and only the plain dishes.
- **Luxury dishes are never taught.** You find them in the pot yourself, or in a very rare cookbook (a few per world:
  an old ruin, a rich merchant's chest, a castle kitchen); each book teaches one luxury dish.
- What you know is kept with your knowledge (like plants), not in a separate menu.
- Drying and smoking: walk into a drying rack with meat or fish; after a night it is Dried Meat or Smoked Fish. Salt
  makes it keep longer.
- Money: a hot meal at the inn stays easier; cooking yourself is cheaper and better on the road. Luxury dishes are
  trade: a city cook pays well for them.
- Each dish is one line (name, ingredients, where, who, effect), so more are easy to add.

**Local ingredients** (new, per land): found by foraging (F), hunting, fishing, or sold in the villages there. Like
the plants now, each world gives them its own look until you know them. Also new: salt, eggs, milk, butter.

| Land | Plants and fruit | Animals and catch |
|---|---|---|
| Forest, old forest | wild thyme, beechnuts, ceps | venison, boar, hare |
| Birch wood | birch sap, wild strawberries | hare, black grouse |
| Taiga | juniper berries, spruce tips | elk, snow hare |
| Tundra | crowberries, lichen | reindeer, ptarmigan |
| Moor | heather honey, bilberries | black grouse, heath sheep |
| Mountains, alpine meadow | gentian, wild garlic | ibex, goat's milk |
| Grassland, steppe | wild carrot, mustard seed | aurochs, wild horse, quail |
| Savanna | baobab fruit, wild millet | gazelle, wildebeest, guinea fowl |
| Desert, oasis | dates, figs, cactus fruit | desert hare, goat's milk (camps) |
| Mesa, canyon | wild sage, pine nuts | bighorn sheep |
| Marsh, floodplain | watercress, calamus root | eel, frog legs, duck |
| Mangrove, coast | samphire, coconut (by palms), seaweed | crab, mussels, oysters |
| Jungle | wild pepper, vanilla, mango | forest hog, parrot eggs |
| Karst | cave mushrooms | blind cavefish (exists) |

**The dishes.** Who teaches it: **I** innkeeper, **T** travellers, herders, hunters or fishers, **P** a people,
**S** only by trying, **B** a rare book. 29 simple, 25 hearty, 10 luxury = 64.

Simple (local dishes; innkeepers and travellers teach only these):

| Dish | Ingredients | Where | Who | Effect |
|---|---|---|---|---|
| Roast Meat | meat | everywhere | everyone knows it | no stomach ache |
| Grilled Fish | fish | everywhere | everyone knows it | |
| Mushroom Skewer | chanterelles | forest | S | |
| Barley Porridge | barley + milk | farmland | I T | lasts long |
| Berry Porridge | barley + berries | | S | |
| Baked Apples | apples + honey | orchards | I | |
| Fish Soup | fish + wild onion | river, lake | T (fishers) | |
| Omelette | eggs + wild onion | farmland | I | |
| Cheese Toast | bread + cheese | | I | |
| Thyme Rabbit | hare + wild thyme | forest | T (hunters) | |
| Birch Water | birch sap | birch wood | I | a little healing |
| Elk Broth | elk + spruce tips | taiga | I | warm in winter |
| Reindeer Jerky | reindeer + salt (on the rack) | tundra | T (herders) | keeps very long |
| Crowberry Mash | crowberries + lichen | tundra | T | |
| Heather Honey Cake | heather honey + barley | moor | I | |
| Goat Milk Curd | goat's milk | mountains | T (herders) | |
| Wild Garlic Bread | wild garlic + bread | alpine meadow | I | less often ill |
| Steppe Kebab | aurochs + wild carrot | steppe | T | |
| Millet Cakes | wild millet + honey | savanna | I | keeps well |
| Date Porridge | dates + barley | oasis | I | |
| Fig Paste | figs + honey | desert | T | keeps well |
| Sage Mutton | bighorn + wild sage | mesa | I | |
| Eel in Ale | eel + ale | marsh | I | |
| Fried Frog Legs | frog legs + watercress | marsh | T | |
| Steamed Mussels | mussels + samphire | coast | I | |
| Crab Boil | crab + seaweed | coast, mangrove | T (fishers) | |
| Coconut Fish | fish + coconut | mangrove | I | |
| Mango Pork | forest hog + mango | jungle | I | |
| Cave Mushroom Fry | cave mushrooms + salt | karst, dwarves | T | |

Hearty (mostly by trying):

| Dish | Ingredients | Who | Effect |
|---|---|---|---|
| Hunter's Stew | meat + wild onion + chanterelles | S | much food, warm in winter |
| Forest Fry | chanterelles + wild onion + hazelnuts | S | filling, no meat |
| Venison Pie | venison + bread + bilberries | S | |
| Boar Ribs | boar + honey + salt | S | |
| Aurochs Steak | aurochs + salt + mustard seed | S | strength (+damage) for a while |
| Herb Broth | yarrow + wild onion | S, monasteries | faster healing |
| Fever Tea | feverfew + honey | S, monasteries | less often ill, cures stomach ache |
| Yarrow Tea | yarrow + honey | S | a little healing |
| Moon Soup | moonpetal + fish | S | mana comes back faster |
| Trail Cakes | hazelnuts + honey + barley | S | light and keeps: a home-made travel ration |
| Shepherd's Supper | goat cheese + bread + wild onion | S | |
| Desert Plate | dates + goat cheese + figs | S | no heat exhaustion for a day |
| Juniper Elk | elk + juniper + salt | S | warm in winter, longer |
| Grouse in Heather | black grouse + heather honey + thyme | S | |
| Ibex Stew | ibex + gentian + wild garlic | S | less trouble from cold and height |
| Gazelle Skewers | gazelle + wild millet + baobab fruit | S | faster on the world map for a day |
| Pepper Crab | crab + wild pepper | S | |
| Pine Nut Bread | pine nuts + barley + sage | S | keeps very long |
| Mulled Wine | wine + honey + apples | S | warm in winter |
| Nut Loaf | hazelnuts + barley + honey | P (halflings) | |
| Second Breakfast | eggs + bread + cheese | P (halflings) | much food |
| Deep Bread | barley + cave mushrooms + salt | P (dwarves) | keeps very long |
| Mead Stew | meat + mead + wild onion | P (dwarves) | warm, poison resistance |
| Rootcake | calamus root + hazelnuts + honey | P (gnomes) | |
| Starlight Broth | moonpetal + yarrow + wild strawberries | P (elves) | mana and healing |

Luxury (only by trying, or a rare book; they sell well in cities):

| Dish | Ingredients | Effect |
|---|---|---|
| Kingsfoil Stew | kingsfoil + meat + wild onion | strong healing |
| Feast of the Hunt | meat + ceps + wine | for you, your hireling and your beast |
| Oysters in Wine | oysters + wine + samphire | mana and luck (better finds) for a day |
| Golden Carp Supper | golden carp + butter + wild thyme | everything a little better for a day |
| Vanilla Cream | vanilla + goat's milk + honey | the hireling's spirits up; a week less wages |
| Spiced Haunch | venison + wild pepper + juniper | +damage and warm, long |
| Oasis Pilaf | wild millet + dates + pine nuts | no hunger for two days |
| Cep Omelette | eggs + ceps + butter | faster healing and mana |
| Wyrm-egg Custard | a drake egg (very rare) + milk + honey | fire resistance for a day |
| Elder Tree Nectar | sap of the Elder Tree (elven city) + wild strawberries + honey | full healing, once a week |

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
