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
| **Approved: walking the land (zones)** | Every world cell can be entered as its own stretch of land; walk off the edge into the next one. The world map stays for travel; towns, sites and holds keep their own maps. Not built yet |
| **Approved: herds, hunting and the crafts** | Herds that stay off the map until you are close, hunting on its own small map, skinning, cooking from what you find (64 dishes, learned by trying or hearing), tanning and leatherworking. Not built yet |
| **Approved: realms, lords and wars** | An emperor, kings, barons and lesser houses with seats on the map; wars that start and end; dwarves, elves and orcs (the Gorvash) each with their own engine; sea raiders, barbarians, desert riders, ice raiders, pass clans, wreckers, canyon riders, mist folk, island voyagers, the church, the Border Watch, mercenaries, peasant revolts, a pretender, witch circles; a realms layer on the world map with organic borders. Not built yet |
| **Built: keeping it clear** | Journal tabs, map layers, IN SIGHT, the status line, the look legend, the company screen, round globes, tips. Every new round follows *The UI rule* below |
| **Approved: stamina for martial skills** | Weapon and martial skills cost stamina, spells cost mana; Warcraft becomes martial (and Charge gets fixed); a third orb on the panel, LIFE, STAMINA and MANA always in sight. Not built yet |
| **Approved: magic schools** | Each school one role and one rule on the map (fire burns, frost walls, storm through water, shadow costs life, necromancy uses corpses, nature makes root and thorn tiles, beastcraft works through the beast); eight tome skills per school; guild techniques adjusted; Packmaster lets you keep two beasts. Not built yet |
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
- **Keeping it clear** (`guide.py`, `ui.py`, 17 October 2026). The line under the map: where you are, danger as
  five blocks, the job you follow. The panel: Money with the potions and cargo; the combat numbers moved to the
  character sheet (c); IN SIGHT lists every enemy in view with a bar and what it is doing (who it goes for stays
  hidden). Round life and mana globes (quarter-block glyphs added to the tileset). The journal in tabs: Jobs (Enter
  follows one: an arrow on the world map's edge, the goal lit), Road, Standing, Lore (every sign you have seen, made
  from the data), Log (500 lines, repeats counted "(x3)", important lines marked ►). Map layers 1-5: Land, Danger,
  Factions, Jobs, Trade (L: next; F still Factions). Look (o) lists what every sign in view means; Enter on a
  creature opens its bestiary page. The company screen (h): hireling and beast side by side, 1-5 orders for one or
  both, gear by slot. A tip in the log the first time something is useful, once per hero.

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

**Hunting** happens on its own small map (with the zones, see *Walking the land*, the zone itself is the hunting ground). Walk into the herd on the world map: a hunting ground like an encounter
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

## Walking the land: zones (approved, not built)

Approved on 17 October 2026 in the thread on seamless walking ("option B", the Caves of Qud model). The Dutch
proposal with the measurements, a sketch script and pictures are in the project files under `naadloos/`
(`voorstel.md`, `zones_mockup.py`, `zones_overview.png`, `zone_corner.png`, seed 7).

**How it plays:**
- The world map stays the way to travel, at today's speed.
- `>` anywhere in open country puts you in that cell's **zone**: a play map of 80x51 tiles (one screen).
- Walk off a zone's edge and you are in the neighbouring zone, not back on the world map. `<` anywhere in open
  country takes you back up to the world map.
- Towns, villages, sites, holds and dungeons keep their own maps. Walk into their zone's middle (or bump the gate)
  and you are in; leave by any edge and you come out into the zone on that side.
- An ambush on the world map is fought in the zone of that cell, not on a loose battle map; after the fight you
  can walk on. Fleeing off the edge still works (you land in the next zone, the foes stay behind).
- Wanderers live on the world map as now and appear in a zone when you are in their cell.

**Why the world map stays:** a grass step on the world map costs 10 turns, a zone is 80 steps across. Crossing the
world through zones would be ~38,000 steps (~128 days). Zones are for looking around, hunting, finding a waterfall;
the world map is for distance.

**How a zone is made:**
- Every tile is a pure function of (world seed, global tile x, y): the world cell and its neighbours are blended
  from cell centre to cell centre, roughened with noise, so forest frays into hills and grass with no seam at a zone
  edge.
- Rivers and roads run from a cell's middle to a point on the edge it shares with the next river or road cell;
  that point comes from a hash of the edge, so both neighbours draw it the same, whenever they are made. A river
  that starts on the world map starts at a spring in its zone. Roads over rivers get bridges.
- Dungeon mouths, shrines, battlefields, shielings and other one-cell things stand in the middle of their zone.
- Settlement maps get a strip along their edges that blends into the zones around them (their roads and rivers
  already follow the world map).
- On screen the 3x3 zones around you are stitched into one map, so the view, sight and chasing monsters run on
  across the edges. Cross an edge and the window shifts: the zone that drops off is put away, the new one is made
  (7-12 ms each in the sketch, with numpy).
- Monsters in zones you are not near stand still.

**Saving:**
- An untouched zone is never saved: it is made again from the seed.
- A visited zone keeps only what changed: items, corpses, dug or cut tiles, dead monsters, and what you have seen
  (as bits). About 0.5-1 KB per zone; a long life of 2000 zones adds 1-2 MB.
- With it (or before it, it stands alone): pack the save with zlib and keep the world map's tiles as bytes. Seed 7
  today: 2.1 MB raw (0.9 MB of it the world map), 0.34 MB packed.
- `SAVE_VERSION` goes up.

**Seasons** are drawn over a zone (snow, ice, leaf colour, mud), never baked into its tiles, or a saved zone stays
in the season you first saw it.

**How the other plans fit:**
- Nature and wonders: each stays a site with its own map, entered from its zone; a river you follow leads to its
  waterfall, and a drifting isle's shadow can fall on the zones under it.
- Herds and hunting: the hunting ground is the zone itself, not a separate small map; a herd on the world map has its
  animals walking in its zone, and a wounded animal can flee into the next zone.
- Place names: unchanged; the area's name shows on the bottom line as now.
- Round 6: no clash, settlements keep their own maps.

**Build:** one new module (`zones.py`: make, stitch, save only changes), changes in `try_move`, `leave_to_over`,
`start_encounter`, save/load and the season drawing; every check of the map kind `'wild'` or `'over'` must know the
zone. About the size of round 5. Tests: zone edges match from both sides, a saved zone comes back the same, an
ambush in a zone, walking from a town edge into a zone and back.

---

## Realms, lords and wars (approved, not built)

Approved on 17 October 2026 in the thread on the kingdoms. Mockups of the realms map and the sketch script are in
the project files under `rijken/` (`realms_overview.png`, `realms_closeup.png`, `realms_mock.py`, seed 3).

**What exists today:** `factions.py` makes crown, league, circle, outlaws, sometimes dwarf clans and an orc horde,
and the cult, with enemy lists fixed when the world is made; `war.py` sends warbands to enemy holds, sieges flip
regions. Wars never start or end, there is no diplomacy. This round replaces that with people who rule.

**The human empire:**
- One **emperor** in the great city; under him 3-5 **kings**; under each king the **barons**, one per region, seated
  in its castle or fort; under each baron 2-3 **lesser houses** (knightly families).
- Every lord is a named person: age, one or two traits (ambitious, greedy, pious, craven, honest), an heir, loyalty
  to his liege. Every house has a name, arms and colours (banners, guards' tabards).
- **Lesser houses have a seat** in their barony, by the village they hold and fitting the land (a hill, a river
  bend, a forest edge): one world tile with its own small map. A poor house has a fortified farm with a palisade,
  a middling one a stone tower house, a rich one a walled manor with hall, chapel and stables, everything inside
  its wall. Inside: the head of the house, the heir, a few guards and servants. A house that rises gets a bigger
  seat; one that becomes baron moves to the castle; a fallen house leaves a burnt or empty ruin to explore.
- In the cities, rich **merchant families** buy influence with coin instead of swords (the league's place).
- **In the background, once a month per court, a small event**, heard through the news: a lord dies (a disputed
  succession means two claimants and a civil war; with no heir the lesser houses press their claims); an ambitious
  baron rebels or claims his neighbour's land; a marriage binds two houses, an insult or murder breaks it; the
  emperor calls his vassals against an outside foe. **Wars end too**: peace, a region changing hands, tribute, a
  hostage.
- **The player never rules** and gets no land. He is a piece in their game: swear fealty and become a knight,
  carry letters, back a claimant, save or kill an heir, open a gate in a revolt, guard a wedding. Lesser houses
  give most of the small work. Money stays modest: lords pay little (greedy ones less), a war levy makes bread and
  arms dear, treason pays well and makes enemies.
- Dwarves and elves also live in human cities under a king, but most of them live in their own lands.

**The other peoples, each with its own engine (outside the empire):**
- **Dwarves: the grudge book.** Each hold keeps a book of wrongs (an unpaid debt, a slain dwarf, a broken pact).
  A full book means a feud or war that only ends when the debt is paid in gold or blood. Iron for grain makes
  pacts with the empire. The player can settle a grudge: collect a debt, return a lost heirloom, hand over a
  killer.
- **Elves: the forest's edge.** They conquer nothing and defend their wood. Imperial logging pushes the forest edge
  back, visible on the map (clear-cuts, stumps); too far and they close the wood and attack woodcutters and
  travellers. The elders under the Elder Tree think in centuries: a promise or an insult counts for generations.
  The player can mediate, chase the woodcutters off, or open a road through the wood for the empire.
- **Orcs and goblins: strength.** Loose tribes with random names from their totem or founder (The Split Tusk, The
  Red Hand) that fight each other; every chief has a strength that grows with each victory. When one is strong
  enough he unites them into **the Gorvash** (an orc word, "all spears"): a real invasion out of the badlands
  ("The Gorvash of Urzag Skullsplitter marches"), the emperor calls his vassals. The warlord dies and it splits
  into feuding tribes again. Goblins serve under the orcs; during a march the half-orcs and goblins in the cities
  are distrusted. The player can kill a rising warlord, challenge him to single combat, or sell them arms. The
  name "Horde" goes (`factions.py`).
- Kobolds, gnolls (follow the drought) and lizardfolk stay local, no realm.

**Outlaw peoples who raid and can win a barony (humans with another law; trade, guest right and pacts possible):**
- **Northern sea raiders** (their own name in game, e.g. the Fjordmen of Skarsvik): longhouses on the fjords, a
  jarl and a mead hall; under his roof guest right holds. In spring their longships are seen at sea, land at coast
  villages, plunder and take captives, and sail home in autumn. A strong jarl can take a coastal barony and stay:
  a jarldom on the map, and the king must fight or accept him as vassal. The player can warn a village of sails on
  the horizon, ransom captives, or sail along for a share (the realm frowns).
- **Hill and steppe barbarians**: tribes with a chieftain (riders on the steppe, clans in the highlands), honour
  and blood feud. They raid in winter and in hunger (after a dry summer or a hard winter). Barons hire them
  against a neighbour, cheap and unreliable. They can take a border barony, which after some years becomes theirs.
- **Desert riders** (desert, dunes, oases): fast riders on camels and horses who hold the oases and the caravan
  roads. They take a toll or rob a caravan; in the dry season they ride north under cover of a sandstorm; a strong
  leader can take a southern barony. Guest right holds in the tent; fine traders in salt, spice and horses.
- **Ice raiders** (tundra, taiga): reindeer herders with sledges, peaceful in summer. In winter, when rivers and
  lakes freeze, they ride south over the ice and raid (the frozen water of round 5 becomes a real danger); the
  spring thaw ends their raids.
- **Pass clans** (alpine, mountains): mountain folk who guard the passes and take a toll. They hire out as guides
  or close a pass to an army, and now and then loose an avalanche on those who will not pay; a king who wants to
  cross the mountains must deal with them (ties in with the passes that close in winter).
- **Wreckers** (coast, moor): coast villages that lure ships onto the rocks with false lights in a storm and strip
  the wreck; the lights are seen at night. They never attack a barony, but grow rich and buy a baron.
- **Canyon riders** (mesa, canyon): fortified villages high in the cliff walls; they strike caravans from the
  canyons (fits the ambush effect those biomes already have).
- **Mist folk** (moor, marsh): raid only in the moor's morning mist and vanish into it again. Little is known of
  them; tales say they know the marshes like no one else.
- **Island voyagers** (atolls, lagoons): sea nomads in outriggers who steer by the stars and hold the reefs and the
  pearls. Good to trade with, bloody in revenge on whoever plunders their reefs.
- The names above are only labels: every one of these peoples gets a made name in its own sound.
- The outlaws (robber knights) stay criminals inside the realm, and a baron can hire them against his neighbour.

**More powers:**
- **The Church**: a king needs the high priest's blessing to be lawful; the church can ban a rebel baron; a holy
  order with its own keep hunts necromancers and witches. The player can get a claim blessed or bribe a priest.
- **The Border Watch**: a knightly order on a line of forts along the northern border against barbarians and
  raiders. They take anyone, convicts and disowned sons too; a baron can exile a rival there. When the watch
  weakens, the raids reach further in.
- **Mercenary companies**: named companies with a banner and a camp on the map, fighting for whoever pays most;
  they can change sides mid-war, and a strong captain may take a town for himself.
- **Peasant revolt**: high taxes, war levies and hunger raise the villages under a leader of their own. They win a
  free commune or are put down (gallows along the road). The player chooses the peasants or the lord.
- **The exiled pretender**: a driven-out heir holds court in exile (over the sea, in a hidden camp, with the
  dwarves), gathers followers and waits for his moment; this starts succession wars by itself.
- **Witch circles**: small hidden circles on the moors and in the marshes that sell herbs, curses and foretellings;
  hunted by the church, secretly visited by barons.

**Not everything in every world** (like `factions.py` today, dwarves 75%, horde 65%): each world draws its own mix,
so every power stays special and every new game feels different.
- **Always there, the backbone:** the empire with kings, barons and lesser houses; the church; dwarves; elves; the
  orc tribes; the outlaws; the cult.
- **Raiding peoples: two or three per world**, and only where their biome is big enough (no ice raiders without
  tundra, no island voyagers without atolls).
- **Small powers grow out of what happens** instead of being there from the start: a peasant revolt only after
  hunger and heavy levies; a pretender only when someone loses a succession war; the Border Watch only with a
  raiding people in the north; mercenary companies when there is war; witch circles where there is moor or marsh.

**Jobs for and against them** (through `jobs.py`, with `effects` on reputation: one side gains, the other loses;
jobs for these powers pay modestly, betrayal pays more; each played on the spot, on foot, with one key):
- Sea raiders: warn a village and set a watch on the beach / sail along and plunder a church for a share.
- Barbarians: bring a hostage back from the highlands / negotiate hired troops for a baron.
- Desert riders: bring a caravan safely through the dunes / betray a caravan to the riders.
- Ice raiders: break the river ice before they come / guide their sledges over the ice.
- Pass clans: show an army a hidden pass / help loose the avalanche.
- Wreckers: put out the false lights on a storm night / help strip a wreck and keep quiet.
- Canyon riders: scout their cliff village for a baron / kill the baron's spy in the canyon.
- Mist folk: find a child who vanished in the mist / take an envoy through the marshes to them.
- Island voyagers: return a stolen pearl / plunder a reef for a merchant.
- Church: track down a witch / warn a witch that they are coming.
- Border Watch: bring supplies to a fort / let a convict escape before he arrives.
- Mercenaries: deliver their pay / bribe a captain to change sides.
- Peasants: catch the leader of the revolt / smuggle arms to the peasants.
- The pretender: carry a letter to his followers / betray his hiding place.

**The realms map:** a new layer on the world map (key 4, after Factions; see *The UI rule*). Each realm washes the
land in its colour, with a bright border where two realms meet and a faint one between baronies; the realm's name
in the middle, ♦ a king's seat, · a baron's; town names hidden in this layer. **Borders are organic**: every seat
grows over the land, and crossing a river or ridge costs a lot, so borders follow rivers and ridges, with a little
noise; each people grows best over its own ground (elves in the wood, dwarves in the mountains, orcs in the
badlands, sea raiders on the fjord coasts); land nobody reaches stays wild without colour.

**Names are made, not picked from a short list** (with the place-name maker): a land name from syllables plus a
form that fits (Kingdom, Realm, Crown, March of, Principality); the empire its own (The Aldic Empire, The Empire of
the Seven Crowns); a barony after its chief place or its land (Barony of Caer Dunmor, The Wolfgate March); houses a
family name with arms and a motto; dwarves, elves, orcs and raiders in their own sound.

---

## Stamina for martial skills (approved, not built)

Approved by Nilio on 17 October 2026. Today every skill costs mana, also Power Strike or Assassinate, and
Warcraft counts as magic. Fighting skills get their own resource: stamina.

- **Two pools.** Weapon skills (Unarmed, Swordsmanship, Axes and Maces, Daggers, Archery) and the martial skills
  cost stamina; spells (Fire, Frost, Storm, Restoration, Shadow, Nature, Necromancy, Beastcraft) cost mana.
  A character who fights and casts has both and must choose where the points go.
- **Warcraft becomes martial**, a third kind beside weapon and magic (`skills.py` DISCIPLINES): it works with any
  weapon in hand, costs stamina and grows on Strength, not Energy. Charge becomes a true weapon strike (today it is
  counted as a spell with 0 base damage, so it only hits for about Energy/5: a bug to fix in the same round).
  Guild techniques follow their discipline: the Iron Company's are martial, Spellblade too.
- **Where it comes from.** Maximum stamina from Strength and Vitality (mana stays on Energy). Stamina comes back
  quickly on any turn you do not attack, slower in heavy armour, and not at all while starving. No new keys.
- **Not rage.** A pool that fills by hitting starts every fight empty; that fits a careful roguelike badly.
- **UI.** Three orbs side by side on the panel, always all three in sight: LIFE, STAMINA, MANA. The panel is 27 cells
  wide, so three 9-wide orbs fit exactly once the small ornament between them goes; rows 12-13 get three labels and
  three numbers. Stamina gets its own colour (bronze or sand; green is poison, gold is XP). The UI round with the
  round globes has landed on main, so the third orb builds on its `orb()` drawing.
- **Save data** changes shape (a stamina value on the player): bump `SAVE_VERSION`.
- Full list of schools, skills and guild techniques as they stand: project files `magie/scholen.md`.

## Magic schools with a character of their own (approved, not built)

Approved by Nilio on 17 October 2026, together with stamina above. Today almost every school runs bolt, curse or
buff, area, bigger area. Each school gets one role and one rule of its own that shows on the map, and **eight tome
skills instead of five**, at ranks **0, 5, 12, 20, 30, 42, 55, 70** (today `UNLOCKS` = 0/8/20/35/55). The bar stays
at six, so more skills means real choices. 72 tome skills instead of 45: each tome turns up a little more rarely.
Full tables with what each skill does: project files `magie/voorstel_scholen.md` (the list as it stands today:
`magie/scholen.md`).

| School | Role | Its own rule | The eight tome skills |
|---|---|---|---|
| Fire | strongest on one target, burning, also areas | burning enemies take more fire damage; fire leaves burning ground (dry summer grass can start a steppe fire) | Firebolt, Immolate, Searing Brand, Fireball, Ring of Fire, Pyre, Meteor, Heart of the Sun |
| Frost | defence and slowing | ice on the map: ice walls block a corridor until they melt; frost on water makes ice to walk on | Frost Shard, Frost Armor, Ice Wall, Frost Nova, Ice Lance, Glacial Ward, Blizzard, Ice Tomb |
| Storm | crowds | water conducts: wet enemies and those in water take more and pass the arc further | Spark, Static Field, Gust, Chain Lightning, Thunderclap, Ball Lightning, Call the Storm, Tempest |
| Restoration | keep you and your company whole | every restoration spell that hurts does double to the undead | Mend, Ward, Renewal, Purify, Turn Undead, Sanctuary, Divine Light, Martyr's Grace |
| Shadow | curses, and the price | Morrak always collects: from rank 30 shadow spells cost life as well as mana; the only school that steals life | Life Drain, Curse of Weakness, Mark of Doom, Shadow Bolt, Dread, Plague, Soul Harvest, Morrak's Bargain |
| Necromancy | the dead fight for you | corpses are the resource: the fallen leave a corpse on the map, the stronger spells use one up; no more life stealing | Grave Touch, Bone Spear, Bone Shield, Raise Skeleton, Grave Mist, Bone Prison, Withering, Army of the Dead |
| Nature | the ground | roots and thorns become tiles; 25% stronger in forest and grass, 25% weaker in desert, on ice and underground | Thorn Lash, Barkskin, Grasping Roots, Bramble Patch, Healing Rain, Swarm, Wrath of the Oak, Awaken the Wood |
| Beastcraft | everything through your beast | without a beast most skills do nothing; Tame moves from the Houndwardens to the tomes (rank 5) | Feral Howl, Tame, Sic 'Em, Lick the Wounds, Call a Wolf, Bond of Blood, Alpha Roar, Spirit of the Pack |
| Warcraft (martial, stamina) | shouts and stances | works with any weapon in hand | War Cry, Battle Rage, Brace, Second Wind, Iron Skin, Rally, Charge, Unbroken |

**Guild techniques** stay, with their guild and skill ranks and prices; only those that now repeat a tome skill or
no longer fit their school change:
- Quiet Ossuary: Raise Dead raises the corpse as itself, with its own attacks; Bone Golem replaces Bone Armour
  (uses three corpses, stays until it falls). Corpse Burst stays.
- Green Moot: Entangle leaves root tiles (r2) instead of a stun; Spirit Totem becomes a totem tile that heals your
  company beside it while it stands. Wild Shape stays.
- Hallowed Chapter: Hallowed Ground makes hallowed tiles (r4) the undead cannot enter, instead of a stun.
- Hollow Coven: Pact of Blood and Morrak's Hand cost life as well.
- Houndwardens: Pack Fury drops to guild rank 1; new at rank 4, **Packmaster**: keep two tamed beasts instead of one.
- Iron Company, Wardens, Thieves, Still Hand: unchanged, now paid in stamina.
- The eight two-guild techniques stay; those mixing martial and magic cost both (Spellblade and Crusade stamina and
  mana; Lichcraft mana and life).

**On the map and in the UI.** New signs, each a tile named in the data so the look legend and Signs know them:
burning ground, ice wall, root tiles, thorn tiles, bone walls, corpses, hallowed ground, the totem, Ball Lightning.
A tile under a spell in a fight shows in IN SIGHT like any other danger. No new keys: skills stay on the bar (1-6)
and are chosen in town (Z). Two beasts (Packmaster) take the beast's place in the company screen (h).
**Save data** changes (known skills, second beast, corpses): bump `SAVE_VERSION`.

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
