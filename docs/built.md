# Built: what is in the game

Moved out of `docs/plan.md` so the plan stays short. Read a section here only when a round touches it. The full
specs of rounds 1-4 are in the git history of `docs/plan.md` (before 16 October 2026, 23:00).

## At a glance

| Status | What |
|---|---|
| **Built** | Rounds 1-5 (monsters and behaviours, named enemies, five guilds, the jobs, seasons and sailing); world shapes; the peoples' own lands; hostile camps; dwarf holds and mines; the bigger world with nine new biomes; small animations on the maps |
| **Built: nature and wonders** | Waterfalls, cascades, great falls and rapids; hot springs, the tidal causeway, the Frozen Stair; the Drifting Isles, the Starwater, the Thunder Anvil and eleven more wonders, each a site with its own saved map; trolls turn to stone in the sun |
| **Built: trade as a way to play** | Fairer money (dear goods bend harder, routes tire), famous goods of a region with good and bad years, master makers, contraband, barter, monster goods, spoiling, far goods, war trade, market news, the great fair, League rank; your own caravan of up to 3 wagons with crew; travel with, trade with and race the NPC caravans. Part 1, the money fixes, built 29 October 2026; parts 2 and 3, goods and ways and the caravans, and the great fair with the feast days, built 30 October 2026 |
| **Built: feast days (30 Oct)** | Thirty-five feasts, each kept only by its land, people or faith (Ruin Night and Hearthnight by all humans); the name under the map, the square dressed, someone to walk into, fair price changes; the Masking's mask, Wanderer's Eve's boot, the Light-Feast in the north; the Fair of Skell, a week a year in each human city |
| **Built: round 6, livelier settlements** | Woodpiles and fields through the year, market-day travellers, the town's mood (fear, feast), small happenings, each people's rhythm, the poor quarter and shanty camps, refugees of the great evils (round 27, 30 October 2026) |
| **Built: ferries in villages** | Where a lane crosses a broad or wild river in a village: a ferry with a ferryman instead of a bridge; a main road over a broad river always gets a bridge |
| **Built: place names** | A name maker per people for villages, towns, cities, holds, glades, hamlets and the hostile camps; human names by region; names that fit the land |
| **Built: walking the land (zones)** | `>` in open country goes down into the zone of that world cell; walk off the edge into the next one, `<` goes back up. Ambushes are fought there; towns, sites and holds keep their own maps and are entered from the middle of their zone. The save is packed |
| **Built: herds, hunting and the crafts** | Herds that stay off the map until you are close, hunting in the herd's zone, skinning, cooking from what you find (64 dishes, learned by trying or hearing), tanning and leatherworking |
| **Built: realms, lords and wars** | An emperor, kings, barons and lesser houses with seats on the map; court events every month; wars that start and end, hosts on the march; dwarves (the grudge book), elves (the wood's edge) and the orc tribes (the Gorvash); two or three raiding peoples per world; the church and its holy order, the Border Watch, mercenary companies, peasant revolts, a pretender, witch circles; 39 kinds of realm job; knighthood; a Realms layer on the map with organic borders |
| **Built: keeping it clear** | Journal tabs, map layers, IN SIGHT, the status line, the look legend, the company screen, round globes, tips. Every new round follows *The UI rule* below |
| **Built: the handbook** | `?` opens The Adventurer's Handbook instead of the old help: contents on the left, the page on the right, opened at the page that fits where you are; lists built from the data |
| **Built: the chronicle** | A second book like the handbook: what your hero knows of this world, each fact marked heard, read or seen; rumours can prove false; books, stones and records lead to places on the map. Libraries with scribes, the dwarves' Grudge Book, the elves' loremaster; a made history of the last two hundred years. Opens with Enter on the journal's Lore tab |
| **Built: stamina for martial skills** | Weapon and martial skills cost stamina, spells cost mana; Warcraft is martial (and Charge is a true weapon strike); a third orb on the panel, LIFE, STAMINA and MANA always in sight |
| **Built: quick wins (19 Oct)** | Spell effects part 1 (bolts, bursts, drain, heals, lightning; full/short/off), burning, poison and frost shown on creatures, Wild Shape in the beast's colours; chimney smoke, sparks at the anvil, rain empties the streets |
| **Built: spell effects part 2 (22 Oct)** | Each school its own hand: rings and waves (ice, `!`, a howl as `( )`, wind `~`, gold), Meteor's shadow and slanting fall, the dead grey and rise, Morrak's Bargain red then purple, walls one stone at a time, fire leaping in Pyre; one white frame of the sky for Call the Storm; areas hit the square but open out round, with a harmless cloud beyond the sides |
| **Built: magic schools** | Each school one role and one rule on the map (fire burns, frost walls, storm through water, shadow costs life, necromancy uses corpses, nature makes root and thorn tiles, beastcraft works through the beast); eight tome skills per school and Warcraft (72); guild techniques adjusted; Packmaster lets you keep two beasts |
| **Built: debug menu and test build (23 Oct)** | Two downloads from every CI build, the game and "Avarenthia (test)"; F12 opens the debug menu there (or `--debug` from the source): snapshots, a bug report, the world, the player and the rest; its own `debug.sav` |
| **Built: temples, towers and barrows (24 Oct)** | Every people's temple, tower and barrow on its own land; tower floors with the land below in a haze and a lookout on top; edges and falls; a deep place below each temple, some over something older; wardens by standing; the bier wakes its king |
| **Built: boss fights part C (30 Oct)** | The boss maker: 15 bases, decks drawn by rules from the library, up to two of 18 traits, a name, title, deed and rumour; "A price on a head"; bosses at the end of nest, shrine, boats, missing and deserter jobs; a boss of the people may yield; beasts leave parts; floors above a fixed boss foretell it, and its floor hides the thing that eases the fight |
| **Built: trade part 2, goods and ways (30 Oct)** | Named goods of a region (12-15 per world) with good and bad years and three or four master works; far goods by sea and the south; barter with kobolds, orcs and elves; beast parts to a city's alchemists; spoiling; need far away; black lotus and the Watch at the gates; war trade; market news at the inn; rank with the Merchant League |
| **Built: archaeology (30 Oct)** | A twelfth life skill: dig spots at old places and Varnish ruins, seen by rank and dug with a trowel; you learn only at places of your own height; lore and riddle pieces, a source of the servants' weaknesses, old pieces a smith mends into gear with an old power (Varnish work wants star-iron), finds a city library buys |
| **Built: life skills part 2 (30 Oct)** | Every beast gives parts, and a part is the power a maker chooses (two from rank 40), better from stronger beasts; parts broken off big beasts; named beasts give parts of their own nature and keep a den; catching one alive for a lord, a cage in his yard; Unmake from rank 40; a master's test at 25 and 40; orders on the boards; perks at 30, 40 and 50; the three great masters and their test; mending for your hireling and the town; boots for the road, a bedroll, barding |
| **Built: life skills part 1 (30 Oct)** | Slow crafts that teach only work at your height (grey, green, yellow, orange), the first time double; Herbalism in Foraging; 51 herbs with two properties each and alchemy without recipes (draughts, oils, a sleeping flask, the Starlight Elixir, tinctures); ten drinks, learnt per people, dearer far away, a barrel, a round, a gift; fish, ore, cloth, leather and game by tier; Smithing at the anvil and Tailoring at the bench, the material sets the grade and a property, the work crude, fine or masterwork |
| **Built: the great evils parts 3 and 4, the other sixteen servants (31 Oct)** | The Ifrit, the Nightmare, the Gorgon, the Wild Hunt and the Hag in her walking hut; the Rat King, the Queen under the Hill, the Vampire Count, the Keening Woman, the Thunderbird and the Lindworm; the Sold King, the False Prophet, the Debt Lord, the Giant King and the Demon Prince: each its land, mark, lever, lieutenants, weakness, relic, lair folk and boss deck. A hireling's shade where the dead are bound; refugees on the roads; real wars over freed lands; the Cinder Key from the Ashen Deep |
| **Built: the great evils part 2, the quest and the Sky-Seat (29 Oct)** | Mist over the Sky-Seat until you know the truth or a seal breaks; relics as keys (and the Star-Iron Key for all five riddles); no travelling by road through his coast; one skipper who dares the whirlpool; the star-iron chain with gusts, handholds and broken links, the glass underside; five floors with beacons; the Hollow King in three phases, one lighter per relic; your shade where the dead are bound, a double fee in his city; the Long Night; the end and a healing world |
| **Built: the great evils part 1, the frame (29 Oct)** | The Hollow King's coast facing the Sky-Seat; three servants per world, one light, one middle, one heavy, from eight kinds (three new: the Wendigo, the Great Wolf, the Fallen Mage), on their own slow clock and his attention clock; levers on the realms (war, tribute, webs, the Gorvash, floods, hunger, wolves, swayed barons), held baronies, the realms pushing back; seals; lieutenants in forts, camps and towers; a weakness from two sources; relics; heroes who ride out and their cairns; the Shadow tab and map layer [7] |
| **Built: boss fights part B, the library (29 Oct)** | A library of about 130 moves from our own spells, weapon skills and beasts; kits for the Rat King, Grolm, the Brood Mother, the Warlord, the Drowned King, the Lord of Cinders, eight theme bosses and nine Varnish guardians, each with its room and tricks; stances and images; roaming bosses that walk a level with their band and follow you up and down the stair; three named things per fixed boss, take one |
| **Built: boss fights part A, the kit (29 Oct)** | Great blows marked red on the ground with a count, purple ones you can break; a rhythm from a deck per phase; phases at two thirds and one third that stop a blow; spent after the heaviest blow, three dots to a stagger, resolve; helpers with a job; twins; a boss bar in IN SIGHT; the end-boss room behind a veil that shuts until it falls, one rotten wall out; Snagtooth, the Lich and the Dragon |
| **Built: the money fixes (29 Oct)** | A dear good moves its market further and bends the price harder, a town holds only a few dear goods, stock comes back over weeks, and the same good sold to the same town fetches less until the market forgets |
| **Built: odd corners and the seasons' places (30 Oct)** | A dragon's scorch, a lightning oak, a sunken boat, an old mine of men, an avalanche cart, flood marks; a hedge wizard, colliers, a ferryman, a beekeeper, a bothy, exiles; a peace stone, a graveyard of all peoples, a two-halves bridge, an orc farm; a robber's cache and the wrong milestone, a lovers' tree, a still; 22 places of spring, summer, autumn and winter; the Standing Night and the Loosing |
| **Built: places of today (30 Oct)** | Part B and the 44 places of the peoples and powers, each a site with its own small map: logging camps, burners, peat, salt, lime kilns, beacon chains that burn in a war, lighthouses, toll bridges, caravanserais that keep robbers off your wagons, prospectors after the Starfall, hunting lodges; the realms', the Church's, the Watch's, the witches', the raiders' and every people's own places; the moot stones' market once a month |
| **Built: the epics (29 Oct)** | 22 epics, two per class, on key 6 in the elite's place, once per rest and free (Phoenix once a day); two hidden teachers of every class in their huts far apart, heard of from rank 35, teaching from 40 after a deed of their own |
| **Built: the Varnish (25 Oct)** | Ruined Varnish cities found only by walking their zones, the Sky Court and a hidden deep below with a guardian of its own; the Northern Wall and its towers, wind towers, the road of the standing dead, a star-iron forge, Gates of Leagues, a sluice hall, the fallen sky, star houses, a sunken harbour; league stones; the chapter The Varnish, eight books in pieces bound by a scribe, and five riddles in The Old Days that point to five deep places |
| **Built: old places from the history (24 Oct)** | The made history lies on the land: old battlefields where the dead walk on the battle's night, villages emptied by plague, war or a dragon, broken bridges of the old Empire, stones of names, the fallen emperor, gallows hills, quarries, wrecks at low tide, hermits, leper colonies; and the peoples' small marks |
| **Built: the Rift and the Ashen Deep (24 Oct)** | A rift opens now and then as a world event (or under a deep dungeon's bottom), the land round it burns to ash, fiends raid at night; three to five levels of basalt, fire, chains, vents, bone fields and cages; seven new creatures; the Lord of Cinders before the burning gate; break it and the rift closes |
| **Built: the northern lights' gift (24 Oct)** | Under the lights rune stones glow and show an old way, Frost and Storm cost less, the spirits of the northern barrows rise and give errands, and wake angry if you dig in or rob them; the ghostly glow blue-green, fiends red. The light-feast built with the feast days (30 Oct) |
| **Built: abbeys, forts, manors and the underground kinds (24 Oct)** | Every people's abbey, fort and manor on its own land with floors above and cellars below; forts held, taken, empty or ruined, with their own ways in; caves, nests, dens and crypts shaped by whoever made them; the goblin hole and the goblin village |
| **Built: the K5 maker (24 Oct)** | Classic dungeons grow from rooms of many shapes; 38 theme rooms drawn as pieces, each with one telling thing; rivers of water and fire underground; rock you can see; a mood line per room |
| **Built: classes part 2, the trees (23 Oct)** | A tree per class, 3 branches of 6 passive knots, a point per 5 ranks, spent where you rested, a temple takes them back; the imbues; Nature's three shapes |
| **Built: classes part 1 (23 Oct)** | A blank start, the first and second class, 55 pair names; the bar is 2 weapon skills, 3 class skills, 1 elite; two skills for every weapon kind, each family with a rule for class skills |
| **Built: weapons and the bestiary (23 Oct)** | 12 new weapon kinds (26 in all) in six disciplines, each with its own rule; reach, thrown spears and knives, crossbows that load; two weapons at once; Shield Bash and Block; monsters fight with one weapon of their own; the bestiary grows in three steps by killing and skinning |

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
- **Fixes from play, 17 October 2026.** Magic made special: found gear is magic about 1 in 30 and rare about 1 in
  125; dungeon floors, chests, elites, bosses, shops and road loot give far less. Named items come in every grade
  (early ones plain magic, middle ones rare, the great ones unique), each power within its level's tier; Snagtooth's
  Pick is now a small magic club. The peddler mostly sells plain gear and can be robbed (he and his sellsword fight,
  or he runs with the pack). Choices you cannot afford show greyed out. Village bridges are one straight deck from
  bank to bank. Orchards are fenced. The fisherman goes home at night. Calmer spring blossom that leaves water and
  trees alone. A town's name no longer covers you on the world map.
- **The handbook** (`handbook.py`, `ui.BookScreen`, 17 October 2026). `?` opens The Adventurer's Handbook: 18
  chapters on the left (the chosen one shows its sections), the page on the right with keys as gold keycaps and signs
  in their own colours, a real piece of the map in a fight or a town, tips in the margin. Opens at First steps for a
  new hero, at Fighting in a fight, at Towns and people in a town, at Travel and sailing on deck; else at the page
  read last. Peoples, gods, the year, rarity, Signs and All the keys come from the data. The book screen is shared
  with the chronicle to come.
- **The chronicle, part 1** (`chronicle.py`, `ui.ChronicleScreen`). The journal's Lore tab is its contents (chapters
  with counts, a dot where something is new); Enter opens the book at that chapter. Facts marked heard ·, read ≡ or
  seen ☼, with who, where and the day; a red "Not so" line when one proves false; gaps named without the answer.
  Heard: the old days, gods, peoples, places and wonders people tell of. Seen: great sights, the dungeons you go down
  into, battlefields you walk, Your deeds (named enemies and great evils brought down, also on the death screen).
  Read: inscribed stones Θ on the first level of some worked dungeons (Varnish ones unreadable until the letters are
  learnt; once read they show where an old way starts) and six old books in the deepest levels (one may name a
  dungeon and mark it). Enter on a page shows its place on the world map. Creatures opens the bestiary.
- **Ferries in villages** (`ferries.py`, `towns.river_kind`). The world map's river decides the village river: a
  stream (short river) gets a narrow bed, a broad one (long river) a wide bed; wild when it comes out of hills or
  mountains close by. Where a lane crosses a broad or wild river: a rope ─ over the water, a raft ▬ at one end, a
  landing on each bank and the ferryman's hut by one of them. Bump the raft, the rope or the ferryman by day: 3c
  (8c when the river is in spate), and you step off on the far bank; the raft stays on that side. At night he is
  home and the raft is tied up. The two busiest roads always keep their bridges, stone ones in towns.
- **Place names** (`names.py`). One name maker for every people, a name never twice in one world
  (`world.used_names`) and never three places on the same stem. Names fit the land (`names.land_at`): river words
  only by a river, coast words only by the sea, hill, wood and marsh words likewise. Humans by region: the north
  Norse (Kettlehowe, Wathmouth), the west Celtic (Penmaris, Caer Morrow, Rhydfynnon), the heartland old English
  (Market Kingshill, Foxbridge, Great Bexchurch); cities grander (Port Hollis, Stoneminster, Konungsgarth). Halflings
  (Hobble-under-Hill, Little Puddling), elf cities and glades, dwarf holds and miners' villages, gnome hamlets, and
  each hostile camp kind its own way. A small chance of a hand-made name. Glades, gnome hamlets, camps, holds and
  cities are no longer capped by a list. The handbook's Towns chapter has a Names section.
- **Nature and wonders** (`nature.py`). One world-map cell each, a site with its own saved play map made from the
  world seed and its place. Falls at the steps where a river leaves the hills (about four a world, one with a great
  name): waterfall with a hollow and a chest behind the curtain, cascade and great falls with a lookout cairn that
  maps the land around, the Frozen Stair in the cold (climb the ice in winter to a ledge with a chest). Rapids with
  stepping stones (a slip sweeps you downstream), hot springs (heal half once a day, warm: the cold costs no extra
  food), a tidal causeway to an islet chapel (two tides a day; the sea covers it at high tide). Wonders, each at most
  once: the Drifting Isles (isles drawn over the vale, the one above you only a shadow; water off one isle runs pool,
  brook, lake, river; a chain up to an isle top with a chest), the Starwater and its twin (a stair under the lake
  between them), the Thunder Anvil (a weapon left at the spike gets lightning damage in a storm), the Hollow Hill (at
  full moon by night: trade a thing you carry for a fey thing, or dance away a day), the Unwintering (Everbloom), the
  Undying Flame (a weapon tempered once: +10% damage, more durability), the Drowned Bell (dive in a storm: the
  chapel's offerings, and something follows you up), the Star Well (a silver coin and one of four wishes a day, three
  in ten twisted), the Singing Stones (rest in the ring at dusk or night: dream of a hidden place, once a week), the
  Wisp Fen (follow five lights at night: a chest or the mire), the Singing Sands (the hum grows louder towards a
  buried chest), the Glowing Bay (summer nights: waves glow, fish bite), the Green Well (rope down, three dives for
  offerings), the Stone Wood (amber and fossils to sell). Falling water in strands of their own speed, boiling foam,
  drifting spray, flowing water on the site maps. Now and then a star falls on an ordinary night (the Starfall's
  machinery). Trolls in daylight turn to stone. Not built: the northern lights stay weather (what they give is not
  settled); the "shown but not decided" list stays open.
- **Walking the land: zones** (`zones.py`). Every world cell is a zone of 80x51 tiles, made from (seed, global x, y)
  with numpy: the cell and its neighbours blended centre to centre and roughened (trees, rocks, slopes, pools; the
  ground from the biome: sand, snowfields, grit, bare rock, bog), so nothing seams at an edge. Rivers and roads run
  from the cell's middle to a hashed point on the shared edge; every river stretch has a ford, roads get bridges, a
  river starts at a spring. Towns (with fields round them), keeps, sites, dungeon mouths (in a hill), places found in
  the wild and crossroads shrines stand in the middle of their zone; hidden glades and unfound places stay hidden.
  The 3x3 zones around you are one map (`maps['zone']`, kind `wild`); crossing into the next cell moves the window.
  A zone you leave keeps only what changed (`game.zones`: tiles, items, what you have seen as packed bits); an
  untouched one is made again. Ambushes from the world map (and camp attacks, job and legend fights) are fought in
  the zone of their cell; foes carry `enc`, cross into the next zone with none beside you and they stay behind.
  Hostile bands that walk into your cell fall on you there; caravans, travellers, patrols and rivals stand in their
  zone and talk when bumped. Leaving a town, site or hold by its edge, or climbing out of a dungeon, puts you in the
  zone on that side. Snow, ice and autumn leaves are drawn over a zone from its world cell, never baked in. The save
  is packed with zlib (seed 7: about 0.38 MB). Not built: the settlement maps' blending strip along their edges, and
  a drifting isle's shadow on the zones under it.
- **Herds, hunting and the crafts** (`hunting.py`, `cooking.py`, `prey.py`). Game is a number per stretch of country
  (`world.game_stock`, by area), never drawn. Herds (one `q`) come and go within a few cells of you and are seen only
  within 4-6 cells (open land and Hunting 10 further, woods less); they leave hoof tracks `:` that fade in two days
  and can be read (age, animal, way). Two to four great herds (reindeer, aurochs, wildebeest) travel north in spring
  and summer and south in autumn and winter, wolves or gnolls behind them. Walking into a herd opens its zone as the
  hunting ground: the herd some 14 tiles off, its leader a `Q`, a few hares or grouse about; the wind in the log and
  one arrow at the edge it comes from; sight (less behind trees and rocks, less with Hunting) and smell (downwind of
  you). A hit animal bolts, bleeds and falls after 3-6 steps; the herd flees off the map; bulls and boars charge, elk
  kick, ibex vanish into the rocks. Prey and the skinnable beasts leave a carcass: Enter skins it (knife or dagger:
  cuts named by the animal, a hide torn/rough/good/fine by Skinning, antlers, horn, tusks, claws, fangs, ivory,
  sometimes a drake egg; without a knife only raw meat). Fresh hides rot in two days (the name counts down); the
  stretching frame `╬` (carried, set up in the land) salts them; a tanner in every village and town (frame and
  workbench `╤` in the stables or the outfitter's) tans for a fee, ready in three days, or oak bark tans a salted hide
  in your pack in five. The workbench makes leather armour, gloves, boots, a belt and a waterskin (heat costs half).
  Fine fur sells for more in cities and the cold north. Cooking: 64 dishes in one table, Roast Meat and Grilled Fish
  known; walk into a hearth (every inn), a fire pit, or cook when making camp; Try something new (up to three things)
  teaches, hints at what is missing, or gives Camp Mush; rank means fewer burnt dishes, more portions, stronger and
  longer effects, and from 15 tasting the inn's stew. One inn in five shares its local dish, travellers and herders
  now and then theirs, the peoples theirs with friends, four cookbooks per world in chests (luxury dishes). Drying
  racks make Dried Meat and Smoked Fish. Local herbs and fruit per land (their own look per world) are found by
  foraging there, with small game snared now and then; village outfitters sell one local thing and farm food; salt,
  a skinning knife and the frame are supplies. Four new life skills: Hunting, Skinning, Cooking, Leatherworking.
  Changed: Nut Loaf is hazelnuts, barley and butter, as the plan gave it Trail Cakes' three things. Not built: the
  quiver (there are no arrows to carry) and mending a tent (tents do not wear).
- **Realms, lords and wars** (`realms.py`, `powers.py`, `seats.py`, `realmjobs.py`, `outlanders.py`). The regions
  now grow over the land from their centres, so every border follows rivers and ridges. The crown faction becomes the
  empire with a made name; 3-5 kingdoms (seats as far apart as the land allows, a made land name and form), a barony
  per crown region (Barony of X, or a March on the border), houses with arms, colours and a motto, every lord with an
  age, traits, loyalty and an heir. Lesser houses get a seat beside their village: fortified farm `╓`, tower house
  `╥`, walled manor `╦` (empty `:` when the house falls), each with its own map, its people inside the wall. Barons
  and kings sit in the finest house of their town (the house gets their name) or in their castle's keep; merchant
  families in the cities. Once a month each court may have an event (deaths and successions, regents, civil wars,
  rebel barons, claims, marriages, insults and murders, levies, taxes, the emperor's summons), heard through the
  news and kept in the chronicle; one telling in four is wrong and gets corrected. Wars end in peace, a barony
  changing hands, tribute or a hostage; hosts `K` march between the seats and burn villages on the way. Fealty to a
  baron, king or the emperor (Friendly with the empire and enough favour with that realm): Sir or Dame, the levy as
  a job, struck from the roll after two missed levies. The other powers (`powers.py`): a grudge book per dwarf hold
  (feuds, settled by jobs), the elves' wood edge (clear-cuts on the map, the wood closed and more dangerous), named
  orc tribes that fight until one warlord makes a Gorvash (the faction is renamed while it marches; half-orcs and
  goblins pay more and are watched in other peoples' towns), two or three raiding peoples per world by biome, each
  with a hall `Æ` (guest right), its own months, raids by land or sea (`R` on the map), captives, warned villages,
  and a barony taken by a strong chief; the church's holy order `╪` (bans a rebel), the Border Watch `╫` (only with
  northern raiders), mercenary companies `¶` (change sides, bribable), peasant risings `‼` (free commune or gallows),
  a pretender in exile `º`, hidden witch circles `○`. 19 new fighters in `outlanders.py`. 39 kinds of realm job
  (`realmjobs.py`) from lords, village boards, raider chiefs, the prior, witches, the Watch, mercenaries, rebels,
  the pretender, the grudge keeper and the elves' loremaster, each played on the spot with one key, some with a
  fight. Map layer 4 Realms (layers now 1-6): realm colours, bright borders between realms, faint ones between
  baronies, `♦` kings' seats, `·` barons' seats, realm names instead of town names. Changed: the regions do not
  grow faster over each people's own ground (only rivers and ridges steer them).
- **The chronicle, part 2** (`history.py`). World making writes 30-60 events of the last ~200 years (the founding of
  the empire, dynasties, kingdoms joining, wars with their field, raiders' first raids, an old Gorvash, marriages,
  fallen houses whose seats are today's ruins, founded towns, plagues and hard winters, the holy order, the Watch,
  the dwarves' oldest grudge, the elves shutting their wood), each tied to a place. The old folk tell them as hints,
  one in four wrong; reading puts it right. City libraries (a home becomes the library, shelves `≡`, a scribe):
  The old days, The realms, A lord or house, This city (3s and a few hours each), Varnish letters (8s and a day),
  free for the Circle of Magi; they buy old books. The Grudge Book's keeper beside a dwarf king's High Seat and a
  loremaster in the elven city. Records mark the ruins of fallen houses on the map; walking past an old battlefield
  shows the bones. New chapters The Realms and Lords and houses; seen beats read, read beats heard.
- **Stamina** (`skills.pool`, `engine.stats`, `ui.draw_panel`). The weapon disciplines and Warcraft (now kind
  'martial': any weapon, its spell damage grows on Strength) cost stamina; the spells mana; guild techniques follow
  their discipline (Iron Company and Spellblade martial). Maximum stamina 10 + Strength + Vitality + 2 a level. It
  comes back 1 + max/20 a turn on every turn you do not strike or use a martial skill, every other turn in chain or
  plate, not at all while starving (food under 100). Charge is a weapon strike (200% + rank) instead of a 0-damage
  spell. The panel shows three globes side by side (the ornament went); the skill bar shows `st` or `mp`. Gnomes'
  cheaper skills apply to mana only.
- **Magic schools** (`skills.py`, `spellmap.py`). Eight tome skills for each school and Warcraft at ranks 0, 5, 12,
  20, 30, 42, 55, 70 (the weapon disciplines keep five at 0, 8, 20, 35, 55): 72 instead of 45, each tome a little
  rarer. The rules: burning foes take a quarter more fire (Searing Brand and Heart of the Sun double), Ring of Fire,
  Meteor and Inferno leave burning ground, which can start a grass fire on a dry summer plain; Ice Wall, frost on
  water as ice to walk on, Blizzard's snowdrifts that slow, Glacial Ward, Ice Tomb; a wet foe (in water, or out in
  the rain) takes a quarter more lightning and the arc jumps once more and further; Gust, Ball Lightning that rolls on
  by itself, Tempest; every hurting restoration spell does at least double to the undead, Ward, Turn Undead, Martyr's
  Grace; shadow from rank 30 costs life (Dread, Plague that leaps on death, Soul Harvest, Morrak's Bargain at a
  quarter of your life) and is the only school that steals life; corpses `%` lie where the fallen fell (the last
  twelve) and Bone Shield, Raise Skeleton, Grave Mist, Bone Golem and Army of the Dead use them, Bone Prison walls a
  foe in; Grasping Roots and Bramble Patch as tiles, Swarm, Awaken the Wood, nature a quarter stronger in forest and
  grass and weaker in desert, on ice and underground; Tame is a tome (rank 5), Sic 'Em, Bond of Blood, Spirit of the
  Pack, most beastcraft needs the beast beside you; Warcraft Brace, Rally, Unbroken. Guilds: Bone Golem replaces Bone
  Armour, Entangle leaves roots, Spirit Totem is a tile, Hallowed Ground makes tiles the undead cannot enter, Pact of
  Blood and Morrak's Hand cost life, Pack Fury at guild rank 1, Packmaster at 4 (two beasts, both on the company
  screen and the panel), Spellblade and Crusade cost stamina and mana, Lichcraft mana and life. Ten new tiles
  (burning ground, ice wall, spell ice, grasping roots, bramble patch, bone wall, hallowed ground, spirit totem, ball
  lightning, snowdrift); a foe standing in one says so under IN SIGHT. Areas already follow the spell-effects rule
  (radius 1 up to rank 30, 2 from 42, 3 only for Morrak's Bargain and Army of the Dead). Changed: Hallowed Ground has
  radius 3 instead of 4 (the effects rule allows no more than 3); Mark of Doom (was Mark of Death) moved to shadow.
- **Loading screen** (`ui.IntroScreen`). The world is made in the background after character creation; the
  opening text from the temple shows meanwhile, with a bar naming each step. Enter begins once the world is ready.
- **Quick wins: spell effects part 1 and a livelier town** (19 October 2026; `anim.py`, `game.fx`). From the
  approved spell-effects plan: the shared toolkit (`bolt` with a fading tail, arrows pointing the way they fly;
  `burst` opening out `*` `+` `·`, with a frame of light drawn in first for radius 2 and up; `drain`, red motes
  flying back after the blow; `rise`, crosses of light off whoever is healed; `zap`, a white zigzag fading to the
  school's colour, hopping foe to foe), used by bolts, splashes, areas, chain and storm, curses, heals and wards, and
  by monsters' and hirelings' arrows and spells and monster novas. Never longer than ~0.45 s with the impact, a key
  skips it, the game never waits. Main menu: Spell effects full / short (twice as fast) / off (the old one-frame
  flash), kept in `settings.txt` beside the save. Lasting colour on a creature: burning flickers orange, poisoned
  pulses green, frozen stands on pale blue, weakened is dimmed; your `@` too for burning and poison. Wild Shape keeps
  your `@` in the beast's colours (bear orange-brown on dark brown, wolf white on slate). From round 6: smoke from
  one chimney per wooden house (most hearths lit, all in winter, from dawn to midnight, the day's wind leaning every
  plume one way) and sparks at the anvil by day; rain, snow, hail, sleet and sandstorms (not a drizzle) send
  townsfolk whose place is outdoors home or to the inn (guards and the lamplighter stay out). No save change.
- **Spell effects part 2: each school its own hand** (22 October 2026; `anim.py`, `skills._ring`, `_rise_dead`).
  New effect kinds: `wave` (a ring running out from a point, or in towards it, with a fainter ring behind; the sign
  from the school: Frost Nova `*`, Ring of Fire and Inferno `^`, Turn Undead, Dawnbreak and Hallowed Ground `o`,
  Dread and Withering `∙`, War Cry and Thunderclap `!`, Wrath of the Oak `♣`, Entangle `"`, Feral Howl, Alpha Roar
  and a monster's wail a sound wave bending round as `( )`, Gust wind `~`); `meteor` (a shadow `░` on the ground,
  then it falls in at a slant from the upper left, then the crater burst, no gathering frame); `raise` (the corpse
  `%` greys, then stands up as its own sign: Raise Skeleton, Raise Dead, Army of the Dead one after another, and Bone
  Golem, whose other corpses crawl to the first as `%`); `trail` (cells one after another: Ice Wall and Bone Prison
  going up stone by stone, dust `·` behind Charge, the leaps and Sic 'Em); Pyre's fire leaps `^` to each neighbour;
  Morrak's Bargain sends your life out red and then all falls in, purple; `sky` (Call the Storm: the map washes
  white for one frame, ~0.07 s, before the strikes; not with effects off). Areas of radius 1 and more look round (Nilio's
  wish the same day, purely the look: what is hit stays the square, as far every way): `anim._round` runs a front
  of signs out by real distance, the ground glows `░` behind it and dims, the corners are drawn softer, and a faint
  cloud `░ ·` beyond the sides rounds it off and harms nobody (Meteor's is brown dust); a howl, a gust and a war
  cry keep only their front. Morrak's Bargain: a short red wave, then the purple one. All stay within ~0.5 s.
  No save change.
- **Market day and rest day** (22 October 2026; `towns.day_kind`, round 6 item 3). Only in human towns. Your first
  day is now a Moonsday, so the week runs Moonsday to Restday. Starsday is market day: from 8 to 17 two in three
  townsfolk stand in the open near a trader's stall, goods sell for a tenth more (still under the buying price) and
  outfitters pay 30% of an item's worth instead of 25%. Restday: the bell rings at 8, the townsfolk sit in the temple
  from 8 to 12, and outfitters, traders and stablemasters are shut by day (the inn and the temple stay open). The
  line under the map shows "· market day" or "· rest day"; a message at 8 says which. Rain still sends people
  indoors. No save change.
- **Fix, 22 October 2026:** the menu line for Life skills (`C`) named only 5 of the 10; it now names all, and
  `text_fits` checks that every life skill is in it.
- **Debug menu and a test build** (23 October 2026; `debug.py` the rules, `debug_ui.py` the screens; test part
  `debug_menu`). CI builds the game and "Avarenthia (test)" (a `TESTBUILD` file packed in turns the menu on; the
  players' build has no way in); from the source `--debug` or `AVARENTHIA_DEBUG=1`. F12 opens an overlay: three
  snapshot slots, a bug report (a folder under `bug-reports/` with what you wrote, the seed, the place, the turn,
  the last 200 log lines and keys, the screen as text and picture, and the save), the whole map, teleport by kind or
  name (towns, dungeons, sites, holds, places, wonders, named beasts, great evils), time on (hours to a season, or
  to a month), the weather, spawn by name, kill all in sight, god mode, full health, coin, levels, skill ranks
  (weapons, schools, life skills), any item by name and grade, identify all, jobs (make one of a kind, finish or
  fail), events (ships, pirates, raiders, rivals, a warband), standing, a hireling, sight off, a creature's state on
  look, and where you are, the turn and the seed in the line under the map. The main menu gets a quick start. A
  debug run saves to `debug.sav`. Not in the handbook. Not built of the proposal: the bot playing from inside the game.

- **Weapons and the bestiary** (23 October 2026; `weapons.py` the weapons' own rules, `bestiary.py` what you know of
  each kind). Scimitar, flail, war hammer, spear, halberd, scythe, throwing knives, light and heavy crossbow, sling
  (weapons) and cestus and tiger claws (gloves), each in three grades; the staff moved to the new Spears and Staves;
  Archery is now Bows and Crossbows. Reach two tiles in a straight line, also past a friend (bump the friend); [f]
  throws a spear or a knife, shoots, winds a crossbow, or strikes with reach. Monster tag `armoured`
  (`weapons.ARMOURED` and constructs): weapons do 25% less, a hammer 25% more, a bolt goes through. Two weapons: a
  light one goes in the off-hand beside a one-handed weapon, half damage, its affixes count half. Shield Bash and
  Block are Iron Company techniques (Warcraft, need a shield). Monsters carry one weapon (`mon.wield`) and drop only
  that one. The bestiary lives on the player (`p.bestiary`: first seen, slain, skinned); steps at 3, 10 and 25:
  weakness and resistances, what it carries, a weak spot (+10% critical chance); a library scribe teaches step one.
  Spears and Staves has no tome skills yet: its two skills per weapon kind come with classes part 1. Test `weapons`.

- **Classes part 1: the blank start, the classes and the bar** (23 October 2026; `classes.py`, `weaponskills.py`).
  You start blank; the first class tome you read asks, then wakes your class (`p.classes`); at rank 20 one tome of
  another school may become the second class and names the pair (55 names, pure names for one class). Only tomes of
  your classes can be read. The weapon tome skills are gone (Burning Arrow too): every weapon kind (29 kits, fists
  included) brings two skills on keys 1-2, the second from discipline rank 10, with their swing, spin, crit and
  blood effects (`anim.py`). Keys 3-5 class skills, 6 one elite (any guild technique for now). Each weapon family's
  rule on class skills (`weaponskills.RULE`: swords cool down, axes push, staves 15% cheaper spells, spears reach 2,
  daggers crit beside you, bows place areas further, shields last longer, unarmed every 3rd blow returns
  stamina/mana). Handbook chapter "Who you become". Tip `class`. SAVE_VERSION 34. Test `classes`.

- **Classes part 2: the trees** (23 October 2026; `trees.py`, `ui.TreeScreen`). Nine trees (Cunning and Arcane come
  with part 3), 3 branches x 6 knots, all passive, from `klassen/uitwerking.md`; each knot is data
  (kind, argument, amount per point) read where the game does that thing: `trees.tuned` makes the cast copy of a
  skill (cooldown, cost, durations, buffs, radius, jumps, range, push, summons, healing, life price, damage), the
  rest are small hooks (stats, weapon and spell damage by the foe's state, softer blows, kills, the turn, the
  beast, thralls). Points: one per 5 ranks in the school (`p.tree`), spent only where you rested (an inn's bed or
  your camp, until you move: `p.rest_spot`), [z] then Tab; a temple takes them all back for 2s a point (and the
  shapes a knot taught). Imbue (first knot of each school's weapon branch): a spell of the school sets the weapon
  going for 10 turns, ~1 blow in 3, no mana back meanwhile. Shapeshifter teaches Wolf, Bear and Hawk Shape
  (`weaponskills.TREE_SKILL_LIST`); in a shape keys 1-2 are its attacks, 3-6 rest unless Untamed. Knots of the
  proposal that needed systems we lack were made simpler (listed in the round's report,
  /mnt/project-files/bouw/ronde3-bomen.md). Debug: "Rested here". Tip `tree`. SAVE_VERSION 35. Test `trees`.
- **Classes part 3: the rules, Cunning and Arcane, the elites** (23 October 2026; `arts.py` the two new schools'
  arts, `trees.RULES`). Cunning (martial, stamina) and Arcane (magic, mana) with 8 tomes each (Garrote and Smoke Bomb
  moved in; the Thieves now teach Cheap Shot and Blinding Powder) and their trees (Stealth, Poison, Traps; Runes,
  Space, Time). New ground tiles: snare ^, caltrops ÷, rune Φ, gate Ω, smoke ▒ (spell tiles, `arts.mon_moved`).
  Cunning's rule: the first blow on a foe that does not see you lands twice (Rogue three times); sneaking is seen
  far less. All 66 rules (11 pure, 55 pairs) are data (`trees.RULES`: text + effects, read as knots by `trees.mine`),
  shown on the tree page. Elites: guild techniques of rank 4+ and the two-guild combos go on key 6; a lesser
  technique of your own school on 3-5; a weapon guild's on key 1 or 2 while you hold its weapon (`p.wswap`); a master
  will not teach a lesser technique of a school that is not yours. SAVE_VERSION 36. Tests `pairs` (every rule in a
  fight) and `balance`: Pyromancer, Warrior, Firebrand, Reaver and Rogue, each in the gear such a one wears, four
  waves on three worlds, each must win 11 of 12. Tuned so (24 October 2026, Nilio: the Rogue stands level with the
  rest): dagger 2-7 (was 1-5), Envenom 10 + 0.6 a rank for 20 turns, Shadowstep back in 6 turns, Iron Skin 30% +
  0.4 a rank for 12 turns. Over eight worlds: Pyromancer, Firebrand, Reaver 32 of 32, Rogue 31, Warrior 30.
  Tuned again at the end of block 2 (24 October 2026; the new dungeons made the Warrior and the Rogue fall on some
  worlds): Iron Skin 40% + 0.4 a rank for 16 turns, back in 20; Envenom also weakens the foe while the poison lasts;
  Shadowstep gives +60 defense for 4 turns. The test now fights on six worlds and each build must win 22 of 24 waves.
  Over ten worlds: Warrior 40 of 40, Rogue 38, Reaver 39, Firebrand 40.
- **The K5 maker** (24 October 2026; `k5.py`, `pieces.py`, `themes.py`, `underground.py`, `pieces/`). Classic dungeon
  levels grow the way of Brogue: rooms of 15 shapes slid onto the level, main ways 3 wide, narrow ways 1 wide, every
  passage from room to room, loops only where the way round is long, lakes, a check (0 bad doors, 0 double walls).
  Sizes: small 80 x 50 (the den), large 120 x 70 (the rest). The rock beyond the walls shows a quiet speckle by
  ground (stone, earth, basalt; ore glints in a mine). The first time you step into a room, the log names it.
  Drawn pieces in `pieces/*.des` (format in `pieces/README.txt`: substitutions, turning and mirroring, telling things,
  when / if / then events), packed and sealed by CI (`tools/pack_pieces.py`); a changed pack is ignored. 38 theme
  rooms, 2 or 3 per level behind a single entrance (a door, an arch, a hidden door or a vault with its key on the
  level), never twice on a level; two arrival rooms by the stairs up, three bottom rooms for the boss. On about
  45% of large levels a river runs from edge to edge, of fire from depth 3 (a third of them): bridges, fords and
  crusts keep every part reachable; you swim water (heavy armour or a heavy pack asks, then hurts), swimmers follow,
  fire asks and burns, a shove sends a foe into the fire or over a chasm's edge. Debug: "Theme room or river" (z).
  Test `k5`. Not as asked: the alchemy bench gives potions that are still good (real brewing comes with the life
  skills); released menagerie beasts fight a nearer monster once, then hunt you; the gaming den's cheats are
  caught by watching, then they fight; the arch with its word takes you up to the land, not along an old way.
- **Places on their own land, part 1** (24 October 2026; `places.py`, `towers.py`, `temples.py`, `barrows.py`).
  Temples, towers and barrows of every people stand on their own stretch of land, cut from the zone round them; you
  walk in from the west edge. A temple for each of the ten peoples (the old temples keep their place and become
  human), towers for humans, elves, dwarves, orcs, goblins, kobolds, gnolls and lizardfolk, half-fallen towers and
  ruins held by bandits, a beast or something in the cellar, and a barrow for each people (two human). The world map
  draws them π, ¡ and ∩ in the people's colour. Tower floors are their own levels, the same size as the land, with
  the land below faded in a haze, the tower's shadow by the hour, birds and cloud; a slit shows out on lower floors;
  the top marks the land round about (10 to 14 by height, 4 more on a hill, halved in fog, rain or snow, only lights
  by night). Edges ask before you step off; a knockback throws you over, a shove sends a foe over; a fall hurts by
  floors. Below each temple a deep place of 3 to 5 levels in its people's style; about a third were built over
  something older: a tale (a rumour) tells which, and the loose flagstone on the last level lifts into a ring of
  standing stones with the Old Warden. Who may go how far is set by standing: wardens stop strangers, pushing past
  is a crime. Barrows of 80 x 50, each people's own twist (the goblins' false tomb and hidden door, the kobolds'
  floor that gives way, the lizardfolk pool); take from the bier and its king rises. A human temple may have a bell
  tower and the elves' eldest tree a stair to its crown, both by the tower rules. Debug: Teleport lists every place
  by people and state; "Hear the tale of an older place" (T). Test `places`. SAVE_VERSION 38. Not as asked: the
  hidden bottom is always under a loose flagstone (no walled-up way yet), found by a rumour, not yet by a job. In a
  hostile tower the watch on top sees you come and the floors wake.
- **Trade part 1: the money fixes** (29 October 2026; `economy.py`). One of a good moves a market's stock by
  `step(g)` = (base / 12) ** .5, at least 1 (grain 1, cloth 1.6, gems 3.2), so a town holds `units()` of it; the
  price follows the stock to the power `bend(g)`, .55 for cheap goods up to .75 for gems. Stock comes back 5% of
  the way a day (was 15%). A route tires: what you sold a town of a good (`p.tired`, in stock) lowers its price
  for you, 1 / (1 + tired / 180), and the market forgets 5% of it a day. Best route in the world with 30 cargo,
  first trip / again a month later: grain 2.6g / 1.7g, cloth 7.8g / 2.9g, spice 11.7g / 2.5g, gems 10.3g (was
  32.8g) / a loss. Test `money_fixes`. SAVE_VERSION 45.
- **Classes part 4: the epics** (29 October 2026; `epics.py`). 22 skills of mode 'epic' (`EP.EPICS`, in
  `SK.SKILLS`), two per class (`BY_LINE`); `classes.fits` lets key 6 take an elite or an epic of your classes. No cost
  (`cost_of` 0); once per rest (`p.epic['spent']`, reset in `TT.rested` through `EP.rested`), Phoenix once a day
  (`phoenix_day`, checked in `engine.die`). All that is yours lives on the player (`p.epic`: spent, learnt per class,
  deeds, teachers heard of, the barrow king, Phoenix's flames, who fell last for Return). The teachers: sites of kind
  'teacher' placed last (`EP.place`, dice of their own), two per class far apart and of other peoples where the land
  allows (gaps of 100-300 cells on seed 11), hidden until a rumour (`lore.hint_teacher` from rank 35); a hut map of
  its own (`site_map`, kind 'town'), a talk with role 'teacher'. Each season a teacher may die (4%); when both are
  gone a pupil comes after a season. The deeds are jobs of kind 'epic' (`JB.LABEL`): the ember (over_step at the
  nearest burnt land), the winter night (sit_out), the bell in a storm (`m.bell`, bumped), five undead laid, the
  temple relic (a crime), the crowned wight on a barrow level (`on_level`), the seed at another wonder (a season),
  a notorious beast's trophy (`NM.make`), the duel (the champion yields at 20%; no hireling, no drink), a new Varnish
  page, the baron's strongbox unseen (`_watched`). Hooks: damage_mon (`on_damage`, `duel_blow`), hurt, mon_shoot,
  die, kill, monsters_act (Time Stop, the duel), end_turn (flames, after_mons, daily), drink, try_move (`EP.bump`,
  no melee in Time Stop), fire, BH.give/push (Unstoppable), arts (Eclipse, Shadow Dance), mercs (One Blood, Return,
  the barrow king follows). New fx kinds 'line' and 'inward'; the world grey under Time Stop; the oak's colours and
  Lich Form's pale @. Oak Shape is a fourth shape kit (`WS.KIT['oak']`: Slam and Root). Debug: "Epics: rank 40,
  teachers, deeds" (E). Test `epics`. SAVE_VERSION 44. Not as asked: Earthshaker is called Worldshaker (a maul's
  weapon skill already has the name); Call of the Old Ones brings a cave bear, a winter wolf or a giant hawk (the
  kinds the game has); the relic comes from a temple's altar.
- **The Varnish** (25 October 2026; `varnish.py`, texts in `varnishtexts.py`). Placed last of all the world
  (`VN.place`, with dice of its own so the rest of the world comes out as before), all in `world.varnish`: `ruin` (cell to city), `wall` (the Northern Wall's cells), `books` (8 of 27,
  one per thread at least), `pages` ((book, n) to ('site', id), ('dungeon', did), ('poi', id) or ('library', None)),
  `src` (each riddle piece's source in this world: what is not here falls back to the library) and `deep`. Hidden
  sites (`folk.unfound`): four cities (`vcity`, 3 x 3 cells, land overgrown, sand, marsh or ice, painted into the zones
  by `VN.paint` from `zones.make`: streets, columns, roofless houses, a gate of star-iron, a name stone), found by
  walking among the ruins (`zone_step`, `over_step`); named only by a name stone read with the letters (`site.vname`).
  The city map: the Sky Court round the sky well, and one way down per city (`site.way`: a stone that says where to
  press, a well that draws air, a hollow flagstone, a lever behind a statue); below a deep of 2-3 levels (style
  rooms, tag vault, size middle, `dg.vn`) with a boss from four (iron sentinel, bound gale, standing legate, hollow
  echo), each once per world, a lump of star-iron and a stone at the bottom; up from level 1 is back on the court.
  Places (each its own small map, `m.vn`, telling things in `m.vthings`): 5-7 wall towers with the wall painted
  between them (one has a lantern: light it at night and the whole wall goes on your map), wind towers (a look-out;
  they howl in a storm), roads of the standing dead (read a seal, or break it and a bound dead steps down), a
  star-iron forge by Starfall Crater when there is one, Gates of Leagues (the star map shows the nearest city and the
  other gates), a sluice hall (open the sluice: the hall runs dry, old coins and a piece), the fallen sky, star
  houses (your feet sweep the dust off a star floor; most of it swept gives a piece) and a sunken harbour. The five
  deep places (`vdeep`: the Anchor by the coast nearest the Sky-Seat, the Hollow Throne beside a city, the Pits of the
  East, the Last Vault, the Standing Hall beside a road of the dead), each with a deep of 3 levels and its own boss
  (chained star, shard of the Hollow King, first of the uncounted, keeper of names, bound magister); found by walking
  or by its riddle made whole. League stones IV-I (POI 'leaguestone') toward each city, each showing the next once
  you have the letters, I showing the city. New tiles 188-211; ten creatures in `menagerie.py` (bound dead and the
  nine bosses). Pages are items 'vpage' that go into `p.varnish['pages']` on pickup and are read with the letters
  (learning them reads what you carry); the chronicle's new chapter The Varnish groups by heading (the fragments'
  subjects, Loose pages, Pages that belong together with "n of N" and the missing ones by number, Bound books); The
  Old Days shows the riddles under their titles with their gap, the answer after six true pieces, false pieces red,
  and The Ruin, as it was after all five. The scribe: The Varnish (3s, two fragments, a riddle piece, a page kept in
  a library), Bind (5s, an hour: item 'vbook', its hidden page and its effect: a place, a riddle piece, an old way, a
  lie shown up, the wall's lantern, the ferrymen's tally that crosses free) and selling a bound book once for 20s.
  Rumours (`lore.hint_varnish`) bring riddle pieces and Voices. Debug V (letters and every Varnish place) and P (every
  page). Test `varnish`. SAVE_VERSION 43. Not as asked: no archaeology yet (round 21), so the pieces come from stones,
  places, pages, libraries and rumours; "mine" pages lie in the cities' deeps; the Anchor stands on the nearest coast,
  not under the Sky-Seat itself.
- **Old places from the history** (24 October 2026; `oldplaces.py`). Placed after the history is made
  (`OP.place` after `RL.generate`). Ten site kinds, each one world cell with a small play map (`m.old` = kind) and
  telling tiles you bump (new tiles 176-187: mound, dug mound, spear point, half-cut block, ship's timbers, sea chest,
  wet sand, pier, gallows, stone head, stone of names, bell on a post): old battlefield × beside a battle's village
  (`e['doy']` its day; mounds give rust 60%, an old coin 12%, once per field 4% a magic blade named for the battle;
  the cairn names battle and date, a chronicle fact; on that day at night skeletons, skeleton warriors and a wight
  rise); deserted village ⌂ with a history event of its own (kind 'deserted': plague, war or dragon; bandits, a
  hermit, a ghost by night or nobody); broken bridge ╧ by a river (the pier shows the nearest old way); stone of
  names ┴; the fallen emperor ß (from the 'empire' event); gallows hill Γ at road crossings near towns (shows your
  wanted notice); old quarry □ (40% flooded; a block holds a fossil 18%); shipwreck ▬ (wet sand only at low tide; the
  chest once, 55% the wreckers came first); hermitage ╓ (the hermit tells a history hint once a week); leper colony
  ± outside human cities (food at the gate, a blessing; the temple job 'alms' carries bread there). Marks as secret
  POIs: dwarf boundary stones ┬, moonstone lines · toward glades and the elder city (each reveals the next), orc skull
  poles ⁿ (reveal the camp), kobold scratches « that reveal their hoard * (coin and a trinket, once). A library
  record of a deserted village or battle marks the place (`history.lead` takes ('site', id)). Curios rust, old coin,
  trinket. Debug flags B (the blade in the next mound) and W (the dead walk every night). Test `old_places`.
  SAVE_VERSION 42. Not as asked: a plundered village of today does not yet fall empty after a year; the hermitages'
  epic teachers come with round 13; a flooded quarry has no fishing of its own yet (the water is ordinary water).
- **The Rift and the Ashen Deep** (24 October 2026; `rift.py`). A world event (`world.rift`): from day 40 a 10% chance
  a month when no rift is open (again a year after one closed and healed). It tears open on the land (a glowing `>`
  on the world map, `D.ENTR`) or, three times in ten, under the bottom of a dungeon four or more levels deep (a crack
  `>` on its bottom level; `dg.under`, `rift_below`). The ash round it grows a cell a month up to 9 and shrinks again
  after it closes (`ash_cells`, the 'ash' omen); at night fiends raid a village within 30 now and then (plundered,
  news, the taken). The Deep: 3 to 5 levels of 120 x 70 cave (the bottom 150 x 90), basalt, ash underfoot, red
  light from the fire (`m.ambient`), a river of fire on every level with bridges of chains (`underground.add_river`
  takes fire, bridge and swallow now), brimstone vents that puff every 5 to 9 turns (stamina and a little harm),
  bone fields that raise ashwalkers, cages with the taken (bump to free) and a gaoler that runs for the gong. No rest
  down there. Creatures: cinderling (horde, dies into burning ground), chain warden (hooks and drags you, over the
  fire if it can), ashwalker (blinding ash when struck up close), brimstone toad (sulphur costs stamina), slag brute
  (burns who strikes it; frost makes it brittle, then double damage), gaoler, and the Lord of Cinders (named per
  rift, heals from the gate while its four fire bowls burn, calls three hellhounds at half, drops only its own gear);
  imp, hellhound, hollow spawn and hungering shade live there too. The burning gate takes three blows (burning you
  while the lord lives) and closes the rift. Debug R opens one near you. Test `rift`. SAVE_VERSION 41. Not as asked:
  the iron hall is only on the bottom level (the court of the Lord of Cinders); no fiend raid walks the world map,
  the raids come as news and a plundered village.
- **The northern lights' gift** (24 October 2026; `aurora.py`). While the lights are in the sky (weather 'aurora',
  or the debug toggle N): rune stones ╨ (a few per world, in the cold lands, `hidden.py`) are found only then, glow
  on the map and, bumped, point to a hidden way's end and show its first stretch; a milestone shows the other way's
  first stretch too. Frost and Storm cost a quarter less mana (`skills.cost_of`). At every northern barrow (at least
  two per world: human barrows are added in the cold lands when too few stand there) a spirit rises as an NPC `G`
  with a quest mark; talking once gives an errand (`spirit` job: set an old grave right, bring back a lost sword from
  a dungeon, or kill the grave robbers), handed in back at the barrow, by day or night. Going down while it watches
  asks first; going down anyway, or taking from a northern bier, wakes the dead (`site.wrath`): every dead below
  awake and angry, and the spirit rises hostile on later nights until it is killed. Glow: blue-green round ghost,
  wraith, banshee, shade, wight and the spirit (brighter and restless when angry, a wisp below), red round fiends.
  Test `aurora`. SAVE_VERSION 40. Not as asked: the light-feast moved to the feast days (round 28, as the build
  order says).
- **Places on their own land, part 2** (24 October 2026; `halls.py`, `delves.py`, `gobvillage.py`). Every people
  has an abbey (Θ; the old human monasteries keep their place), a fort (╩) and a manor (Å), each its own plan as
  the spec says, on its own land: 100 x 60 for abbeys and forts, 80 x 50 for manors. Floors above for the human
  abbey (dormitory and scriptorium), the elves' crowns, the halfling loft, the human manor, the elven bower and the
  gnome cap house (style 'upper', the land faded below); a fort's tower follows the tower rules (two new small
  styles, 'corner' and 'loft'). Below: cellars, archives and dungeons of 1 to 5 levels. A fort is held by its people,
  or taken by bandits, abandoned to beasts or a ruin. Telling things through `m.things`: lore on shelves and rune
  stones (history), a still pool or lens shows a far place, the goblins' map room marks a dungeon, the halfling long
  table feeds a friend once a day, letters give a rumour, a portrait or seat says who lives there; the keep's
  portcullis drops on alarm (a postern at the back), the lizardfolk pull in their walkway, the kobold trap gate and
  its falling ceiling, the gnomes' hidden door and peep holes, the elves' woven gate for friends only, the dwarves'
  murder holes and bolt throwers. The underground kinds (den, warren, cave, ant nest, spider lair, grotto, gloam,
  dragon and spider lairs, burrow, swamp, crypt) lay out rooms by use with their folk where they belong; the goblin
  hole has a watch that strikes the gong, tripwires, a covered pit and a back way out. The goblin ravine ends in a
  carved gate to the goblin village (120 x 70) with the deep halls below; its chief's high seat holds the village.
  Test `halls`. SAVE_VERSION 39. Not as asked: no drawn pieces set into the fixed plans yet; the halfling abbey and
  the elven bower got floors above that the spec did not ask for; the Hedge Post's bell wakes foes but raises no
  hamlets yet.
- **Boss fights part A: the kit** (29 October 2026; `bosses.py`). A boss with a kit (`BS.KITS`: snagtooth, lich,
  dragon) keeps its fight in `mon.bs` and a loading blow in `mon.cast`; `BS.turn` runs before every other boss rule
  in `mon_turn` (the old die-roll summon, nova and leap are gone; other bosses' nova and leap are now announced a
  turn ahead, `_plain`). Moves (`BS.MOVES`): shapes line, cone, ring, cross, circle on you, room save behind cover,
  wave and a circle that follows; `need()` counts the steps to a safe cell (BFS) and the load is at least that, so a
  marked blow always leaves a way out (`check_fair`, 150 turns per boss in the test). The deck: per phase a skeleton
  of beat roles (small, set-up, great, heaviest, summon, room), cards drawn from piles that reshuffle; one beat in
  five breaks the rhythm. Phases at .66 and .33 (Snagtooth one at .5) stop a blow in `blow()`; a crit while spent
  or staggered breaks through (never two at once). Spent a turn after the heaviest blow; breaking a blow or its
  weakness fills three dots, full staggers two turns; ♦ resolve takes the first two stuns. Helpers carry `o.job`
  (warder halves damage to the boss, mender, guard, channeler). Twins (`BS.TWINS`, `mon.twin`): opposites, shared
  life, a survivor who grows, master and servant. Kills go through `BS.spare` (a threshold holds; a lich shard
  raises her a quarter healed after 3 turns) and `BS.felled`. The arena (`m.arena`, `BS.on_level` on a last level,
  else a dug blob): the boss's room behind a veil (tile VEIL, asks once), shut (SEALED) at the first blow, one ROTTEN
  wall that gives after five bumps; leaving means fleeing: the boss heals and gets ready (a resistance, unbroken, a
  helper, its second phase; four at most). No rest and no portal while shut. The Lich: four shards (SHARD, DARKSHARD)
  and pillars as cover, lichcraft halves weapons not silvered, fire or holy, lights out (sight 3). The Dragon: drakes
  with a channeler, takes wing out of reach and dives, the burning floor dance, Inferno breaks a pillar (FALLEN) and
  leaves it spent. The company steps out of the red (`ally_turn`) and hits the boss once more per ally beside you.
  Shown: red and purple ground with the count (`marks`), the boss bar on top of IN SIGHT (phase, ♦, dots, ticks at
  the thresholds, what it does), the gold name across the map and FOE FELLED, a stance line in `l`; tips 'red' and
  'shut'. Lich life 7 to 4.5 and Dragon 8.5 to 5 (the kit makes them longer). Tiles 212-217. Debug: Bosses (K):
  spawn, phase, shut/open, fairness, helpers, spent, flee, twins, flag 'rhythm'. Test `bosses`. SAVE_VERSION 46. Not
  as asked: the three named items per boss come with part B, for every fixed boss at once.
- **Boss fights part B: the library** (29 October 2026; `bossmoves.py`, `bosses.py`). `BM.LIBRARY` (merged into
  `BS.MOVES`, 131 moves besides the calls) by school: weapons, fire, ice, storm, shadow, the dead, nature and beasts,
  holy light, arcane and cunning, and the bosses' own; role R is a stance. New shapes in `cells_for`: arc, wide,
  cross (round you or through the room), ringat, strips, scatter, wave (cover stops it), ring with a hole, circle of
  one tile, room with a `safe` (stones of light, ledges and chains; `shelter()`, shown gold, MARK_GOLD), self (a
  spell on itself, broken like any other; `BM.on_self`: mend, army of the dead, stop time, the knot). Kinds without
  ground in `BM.do`: curse, guard (riposte, shield wall: a flail or war hammer gets past, glacial ward, holy shield
  of three blows, pyre, sanctuary, counterspell; 12 turns before the same again), cry, icewall, bramble, runes,
  blink, smoke, step, burrow/drop (aloft, then a following circle), eggs, holes, prop, mirror (images of 1 life,
  `image_of`), harvest, martyr, gust, tunnel, shed (a skin left as decoy). States on you in `BM.on_you` (the new
  status 'hexed': no skills); pull, gather, drain, chain, crater, roots, webs in `BM.hit_more` and `BM.after`.
  Kits (`BS.KITS`, 31): the Rat King (rat holes you stop up by walking in; the water rises at a third; the knot
  splits into three kings, `knot`, the last one is the real death), Grolm (pit props; kicking one drops marked
  stones; the falling roof, never beside a standing prop), the Brood Mother (webs on the floor hold you, eggs hatch
  unless trodden, drop from above, cocoon heals her), the Warlord (his band, a banner bearer whose banner stays until
  hacked down, then the duel: the guard watches until you strike from afar or your company steps in; enrage), the
  Drowned King (`flood()`: water bands from the low side, shallow then deep; every change raises it, each chain in
  the wall broken in two blows lowers it; the deep calls spares ledges and chains), the Lord of Cinders (his hall is
  the arena, `hall()`; the burning gate is his warder while a bowl burns; its healing stops at the thresholds),
  eight theme bosses at the bottom of their nests (`on_level` arms the dungeon's boss: Spider Matriarch, Ant Queen,
  Goblin King who hides behind his goblins, Viperkin Coilguard, Ghast Lord, the Staring Dark, the Deep Mother, the
  Wasp Queen; two phases at one half), the nine Varnish guardians (two phases; wind, fog, enrage as room tricks).
  Room tricks per phase in `_phase`: water, ceiling, collapse, webs, wind, fog, enrage, banner, duel. One of each
  helper job at a time (mender, warder, channeler, bearer); a mender heals a fortieth every fourth turn. Blows that
  went round `blow` (a hireling's) still take it past a threshold (`crossed`). Roaming bosses (`ROAMERS` by place
  tag: troll, ogre, orc warchief, hobgoblin captain, gnoll packlord, ghast lord): `place_roamer` halfway down a place
  of three levels or more that is not small, half the time, with a band; `patrol` walks a path from hall to hall and
  leaves tracks (decoration TRACKS), `heard` gives a line with its direction every 25-45 turns, `hunting` (seen or
  within 5 in the last 300 turns; lost, it heals and goes to a stair); `leaving`/`arrive` in `enter_dungeon` bring it
  after you up or down the stair. Loot: three named things per fixed boss (`D.UNIQUES` with `boss`, 18 new), a
  choice `boss_loot` when it falls; you take one. Life of the Rat King 6 to 4, Grolm 6 to 4.5, Brood Mother 6.5 to
  4.5, Warlord 7.5 to 5, Drowned King 7 to 5. Tiles 218-225 (rat hole, pit prop, web on the floor, clutch of eggs,
  stone of light, chain in the wall, stone ledge, war banner). Debug: Bosses (K) sets down any kit boss or a roaming
  one ten steps off. Test `boss_moves`. SAVE_VERSION 47. Not built from the spec (left for part C): arenas dressed per place (tower
  top, temple nave...), ways out other than the rotten wall, the thing a place hides that eases its fight, floors
  above that foretell the boss, the place that wakes or falls in; the other fixed bosses' named sets come with the
  great evils' servants.
- **The great evils part 1: the frame** (29 October 2026; `shadow.py`, `evils.py`). `world.shadow`: the Hollow King's
  coast (`land`, the land cells within 36 of the coast cell nearest the Sky-Seat; his as far as `land_r`, which grows
  with `wake`), `wake`, `seals`, `torn` (the mist may part: part 2), `night` (three seals: part 2), the attention
  clock (`att` 0-5, `pts`; a step needs 3 points and 10 days since the last, cools a step every 15 days after 20 days
  left alone; `meddle()`), `held` baronies (realm key `('evil', i)`), `heroes`. `p.shadow`: weakness clues per
  servant, lieutenants known, cairns read, `king`. Servants: `EVL.choose` draws one heavy, one middle, one light;
  `place_lairs` puts them far from home, from each other and from his coast, a light or middle kind giving way when
  its land is missing. New kinds: the Wendigo (cold woods), the Great Wolf (plains), the Fallen Mage (sways barons),
  each a boss with a kit; the call `call_wolves`. Strength from `power()` (its weight, its goal, his attention, dead
  lieutenants), never from your level; the mark's reach by weight (14, 26, 42). The slow clock: a light one awake
  from the start, middle at day 100-140, heavy at 250-330 (sooner with his attention); the goal fills by weight and
  breaks a seal at 100. Levers once a month, one push per realm (`LEVERS`), then `_push_back` (levy, the Church's
  order, a held barony freed). Lieutenants: three per servant from a pool of four or five, sites kind 'lt' (fort,
  camp, tower) near the lair; killed: papers (a clue), favour with the kingdom, a weaker servant; survived and hurt:
  scarred, its place made anew stronger. Weakness: two of library (scribe subject "The dark powers"), riddles (a
  Varnish riddle made whole; the king riddle also gives `king`), a hero's journal (cairn, sites kind 'hgrave', tile
  HCAIRN), a lieutenant's papers; the edge in the lair (`on_level`): fire half again, blows a quarter harder, no calls,
  no rising water, a quarter weaker, or the Lich's jar (tile JAR beside her; whole, she rises 40 days later). Relic:
  item kind 'relic' with one small power while carried (`SH.stats`). Heroes: one rides out at a time, kills a
  lieutenant a third of the time, mostly dies (a cairn). The world no longer ends when all three fall (the Hollow King
  does that, part 2). His coast: ambushes of the bound dead, villages struck by the dead. UI: journal tab Shadow, map
  layer Shadow on [7], the line under the map, chronicle chapter The Shadow, tip 'shadow'. Debug: The shadow (S).
  Tiles 226-227. Test `shadow`. SAVE_VERSION 48. Not built from the spec (part 2): the battles as places for the
  servants' wars beyond what the realms already leave, refugees on the roads, the sky darkening over his land.
- **The great evils part 2: the quest and the Sky-Seat** (29 October 2026; `skyseat.py`). At the making of the world
  the Sky-Seat's cells go under a mist overlay (`seat_over` keeps what was there) and it leaves `world.wonders`;
  `check()` tears the mist when you know the truth (`p.shadow['king']`, the riddle of the Hollow King) or a seal broke
  (`torn`). Keys: items kind 'relic' (each fallen servant's, or the Star-Iron Key when all five riddles are whole).
  `travel_iter` refuses a route through his coast; on his coast his hunters come as if his attention were 2. The
  skipper on the harbour nearest his coast offers "Out past the mist" (20 silver, a relic, two days; no company).
  The chain (`chain_map`, key `skyseat:chain`, `m.chain`): the sea rocks and the boat (RAFT, back to the harbour),
  a star-iron chain three links wide in the air, handholds (`D.CHAIN`), broken links and cracked glass that give way
  on the second turn you stand on them, gusts sung a turn before (`turn()`), the fall into the sea (`fall()`, by the
  height), the glass underside and the stair up. Five floors (dungeon 'skyseat', tag 'skyseat'): `FLOORS` names, a
  beacon on each (walk into it: `beacons`; from the rocks a rope of light up to the highest lit floor), the throne
  and the Hollow King (boss 'hollow_king', kit of three phases: the winds, the dead, himself; `kit_over` drops a
  phase's heaviest blow and its trick per relic carried; a third more life in the Long Night). Dying there: the
  fee doubles, your body rises as your shade (`shade()`, a 'shade' with your pack in `my_body`; also in barrows,
  crypts and the Rift), bound dead come back on the unlit floors; no town portal in his city. The Long Night at
  three seals (`night_falls`): his coast to 54, the world map darker, prices a fifth up (`ECO.NIGHT`), the cities
  shut their gates (news). The end (`won()`): his coast and the marks fade, the clocks stop, held baronies freed,
  the chronicle and Your deeds, the closing screen (WinScreen). `history.py`: the first fall of the Hollow King in
  1 AR. Tiles 228-234. Debug: The shadow (S), the Sky-Seat column. Test `skyseat`. SAVE_VERSION 49. Not built from the
  spec: a fallen hireling rising as well; the relic won elsewhere besides the Star-Iron Key; the barons' fight over
  freed lands is news, not a war (left for rounds 31-32).
- **Fixes from the full run, 29 October 2026 (block 4).** Hunters on the world map go round a lake or a ridge
  (`wanderers.hunt_round`) instead of waiting behind it; a totem heals a boss only a fortieth, not past its phase;
  a tower door in a thick bit of wall gets a short passage; the eldest tree of an elven temple gets a white path from
  its door to the moonwell; a ladder is never set on the one below it (an orc fort's tower lost its way down); a roaming boss's stair check survives a level already gone; the Sky-Seat's chain map has
  its own flag (`skychain`). The balance test draws anew (`world * 7 + 1`): the Rogue stands near the edge, and on
  some draws it lost a few of its 24 waves, before the great evils as well.
- **Round 19: life skills part 1** (30 October 2026; `lifeskills.py`, `foraging.py`, `alchemy.py`, `brewing.py`,
  `crafts.py`). The curve `20 + 4r + .35r²` (`need_for`); `gain(..., at=, what=)`: work far below your rank teaches
  nothing (grey, 10 under), little (green, 5 under), most at or above (yellow, orange), the first make or catch double
  (`p.life_firsts`); `colour_of` colours the craft lists. Foes five or ten levels under you teach a discipline less
  (`skills.gain(..., foe)`). Tiers A-E and the top (`TIER_RANK`, `TIER_DANGER`, `place_danger`): what lies where
  follows the danger of the land and the depth; above your rank "too hard for you yet" (`too_hard`). Herbalism is
  gone into Foraging. 51 herbs (`foraging.HERBS`: tier, two of 17 properties, where: lands, biomes, night, winter,
  cave, deep, cursed, wonder); `draw_herb`, `herb_here`; properties known per herb in `p.herb_props` (taste the
  first, Foraging 15 the second, a brew both; `props_known` shows `?`). Alchemy without recipes (`alchemy.py`): two or
  three herbs, what they share; three on one stronger; oils (Venom, Flame, Silver: `oil_venom`, `fire_dmg`, `undead`
  buffs), the sleeping flask (`hold`), Starmoss doubles, alone the Starlight Elixir (`p.starlight`, +5 life once);
  spirits as the base: a tincture, twice as long. Items 'draught'. The `[P]` screen: herbs with letters, Enter brews,
  Tab to brewing. Brewing: ten drinks (`RECIPES`; `p.drinks`, learnt by tasting or from an innkeeper of that people
  or climate, royal mead at 45 by yourself), `it.origin` and `far_value`, a barrel for the cart from 30, a round for the
  company at a fire (`round_for_company`, morale +15), a people's own drink as a gift at their inn (rep, a place told),
  strong spirits warm and give courage, the third cup makes you tipsy (`tipsy`). Fish by tier (`FISH` with tier and
  where: night, storm, north, south, mountain, broad, deep, deepest, forest, star), fresh and salt apart; a fish too
  strong snaps the line; fish hooks, the net (`net`), bandages (`bandage`). Smithing at the anvil (`crafts.anvil`):
  ore veins hold a metal by land and depth (`vein`, kept in `m.veins`; iron on the cart, the rest items 'mat'
  `ore_<metal>`), smelting into `bar_<metal>`, forging every metal weapon, mail, plate, helms, shields, gloves,
  belts, boots and tools (`SMITH`), mending for a bar, honing (`honed`). Tailoring and Leatherworking at the bench
  (`crafts.bench`): cloth `cloth_<cloth>` from outfitters by land (`shop_cloth`), spiders (`on_kill`), mammoths, the
  wisp fens at night (`fey_silk`); leather by its beast (`hunting.LEATHER_OF`); new bases Robe, Hood, Wraps, Soft
  Shoes; warm or cool (`it.feel`, `feel_count` in `weather.food_factor`). Grade by the material's tier, its property
  (`props`), quality crude, fine, masterwork (`quality`). Herds above your Hunting tier are too wary for you yet
  (`GAME_TIER`); parts tear below it in Skinning. Handbook chapter Crafts. Test `crafts`. SAVE_VERSION 50.
  Not built from the spec: the road goods of Leatherworking, Lockpicks, the master perks, orders and mending for others
  (left for round 20); gifts go to the innkeeper of a people, not to a king or a guard.
- **Round 20: life skills part 2** (30 October 2026; `beastparts.py`, `mastery.py`, `crafts.py`). Parts by their
  beast (`Item('part', '<part>:<beast>')`, `beastparts.PART`, the ladder `STEP` by the beast's tier: wolf fangs +5,
  winter wolf +10, sabretooth +15); spiders and beetles leave chitin (`on_kill`); scales and frost scales on snakes,
  crocodiles and drakes. Making asks for a part after the material (`crafts.ask_part`, `r_craft_part`; two from rank
  40); `fits` keeps fangs on weapons, helms, gloves and rings, claws on weapons and gloves, the rest on armour,
  antlers and feathers anywhere. A critical blow on a big beast below half its life breaks a part off, once
  (`on_blow`). Named beasts (beast and crawler kinds) give one or two `npart` items with a trait's power of found gear
  (`TRAIT_POWER`, by rank), whole only with a knife and Skinning 15/30/45 (`named_parts`); a piece made of one bears
  the beast's name. Dens: a hidden site 'den' near the home of every named beast but the legends (`make_den`, the
  sign δ), found by walking up to it (`on_step`), Hunting 50 on its track (`reveal`); a small map of the land's kind
  (hollow tree, thicket, cave, wallow, ledge, burrow, webbed hollow) with bones and now and then a shed part; the
  beast is home when it fled there or one day in three (`home`); `den_gone` on its death or capture (`site.gone`,
  `site_at` skips it). Catching alive: the lord's realm job 'catch' (`realmjobs.make_catch`); a sleeping flask marks
  `slept`, below a quarter of its life a rope binds it (`try_bind`, in `melee`); waking first makes it furious
  (`wake`); a cage in the lord's seat yard (`world.cages`, `sync_cages`, `at_cage`); a dead beast fails the job.
  Unmake (`crafts.found_pieces`, `own_pieces`, `unmake_chance`: 40 at rank 40 rising 3 a rank, cap 80, a strong power
  15 less; two thirds of the value, all of it at 50; the found piece lost either way, one failure in four breaks or
  curses yours; `it.moved`). Mending at the bench for leather and cloth, your hireling's gear at both
  (`worn(game, craft)`), mending on the road from rank 30 by using a bar, bolt or leather, mending for the townsfolk
  once a day (`mend_others`). Road goods: marsh, sand, snow and mountain boots (`ROAD`, `road_boots`, a quarter off
  a world-map step), bedroll and tent (a better night in the open), light and mail barding (`it.bard`, `mc.barding`).
  Master's tests (`mastery.held` in `lifeskills.gain`, `need_test`, `wants`, `hand_in`; a 'mastertest' job in a far
  town; `p.life_tests`). Orders on the boards (`make_order`, kind 'order', your best craft at your tier). Perks at 30,
  40 and 50 for every skill (in `LIFE`; ice fishing, storm bites, two fish; rare herbs twice, no poison by mistake,
  herbs in passing; veins through a wall, cave-in warning, one more ore; tracks last, stalking close, dens on the
  track; trophies, no tearing, fine hides; a feast for the company, dishes keep, effects last; two brews, oils last,
  never fail; drinks sell better, the inn buys yours; road mending, two parts, masterwork and full Unmake). The great
  masters (`mastery.ensure`: a smith, a leatherworker and a tailor far from the roads, each with a lost workshop;
  rumours at inns and tanners; the test in three parts in `p.masters`; one Unmake a visit for 3 gold at 50%).
  Handbook: Hunting and cooking (parts, named beasts), Crafts (powers, mending, Unmake, masters). Test `masters`.
  SAVE_VERSION 51. Not built: Lockpicks (there are no locks yet) and the quiver (bows use no arrows): both wait for
  what they need.

- **Round 21: archaeology** (30 October 2026; `archaeology.py`). A twelfth life skill (`LIFE['archaeology']`, last
  in `LIFE_ORDER`; perks 3, 8, 15, 20, 25, 30, 40, 50; the master's test asks for an old piece of tier C, then D).
  Dig spots (`spots`, `m.digs`, the tile `D.DIGSPOT`, the sign ÷): a few on every old place and Varnish place (`KINDS`,
  eight in a city), each as hard as the land's tier (+5 at the Varnish, + 0-9); you see a spot up to 3 ranks above
  you (6 from rank 8, all at 50; `show`), and only with a trowel or some rank. Walking into one with a trowel (sold
  with the supplies and forged at the anvil) or a pick (more breaks) digs it (`dig`): the break chance falls with
  rank over the spot (`brk`), and a spot far below you teaches nothing. Dug spots stay dug on the site (`site.dug`).
  Finds (`find`): lore (a Varnish riddle piece from the 'library', 'place:<kind>' or, with the letters, 'stone'
  sources; on a battlefield or in a deserted village its history event), from rank 20 a servant's weakness (source
  'dig' in `shadow.SOURCES`), old pieces (`Item('oldpiece')`, mended at the anvil by Smithing of their tier into
  magic gear named "of the Old Days" or "Varnish ...", the Varnish ones for a shard of star-iron too), star-iron
  shards at the Varnish, and finds by tier (`FINDS`: potsherd, old coin, seal, figure, gold torc) that a city library
  buys at half again their value (`scribe_opts`). Debug: the flag "Old finds" keeps finds whole; Give item (trowel,
  old pieces). Handbook: Your hero (life skills list), Crafts (Archaeology), the Varnish forge line, Weaknesses.
  Test `archaeology`. SAVE_VERSION 52.

- **Round 22: trade part 2, goods and ways** (30 October 2026; `tradegoods.py`). Extra goods beyond the nineteen
  (`D.GOODS` keys not in `GOOD_ORDER`, put in by `install` after making or loading a world): 12-15 named goods per
  world (`NAMED`: good, name after the area or town, where it can be made, how much dearer, spoils), one maker town
  each; three or four master works (`MASTER`: cup, tapestry, dress sword, brooch); far goods (`FAR`: silk, incense,
  porcelain, dyes, stocked only in harbour cities and the far south); barter goods (`BARTERED`, `BARTER`: kobolds give
  glowcaps for gems, orcs hides for salt, elves moonsilk for salt); contraband (`CONTRA`: black lotus, stocked in swamp
  towns). An extra good has its own reference stock (`ref` = three of it): a few at the maker, almost none elsewhere,
  so it is cheap at home and dear far off, plus up to 40% more by the road from home (`factor`). Each new year a
  named good has a plain, bad (x1.4, less made) or famous year (x1.25, more made; `years`, news). Every day
  (`daily`): spoiling of fruit, fish and perishable named goods (5% a day in summer, 1.5% in winter, less with salt
  in the cargo); now and then a need (`world.trade['need']`): a cold or hill village snowed in in winter wants grain,
  a city of a realm at war under siege wants medicine, at three times the price with none to buy. Arms cost 1.6 times
  in a realm at war; selling them to both sides (`p.arms_to`) comes out one time in three: favour -15 with both
  crowns, League -5. Markets will not deal in lotus (`refuse`, except buying it in a swamp town); the Watch searches
  at the gate of towns and cities (`at_gate`, 30%, half for Cunning): lotus taken, a fine, a crime; the cove's fence
  pays twice its base (`cove_sell`). A city's herbalist buys beast parts at twice their worth (`alchemist`). An inn
  now and then has a carter's prices from a far town, a few days old, put into the market list (`inn_news`). League
  rank by profit (`p.league_profit`; Associate 5g, Member 25g, Master Trader 100g, Merchant Prince 300g): 2% better
  prices a step (`ECO.league`), better paid factor's work, a League caravan to guard at the top; the factor tells
  your standing. Cities ask for a master work on their boards (job 'masterwork'). Market list: extra goods that are
  here, in your cargo or needed (`rows`), marked * or ×, a note on the selected good; the screen is 110 wide.
  Handbook: Jobs and money, Trade. Test `trade_goods`. SAVE_VERSION 53. Not built here: the great fair (with the
  feast days) and the ladder's small supply orders (with the caravans).
- **Round 23: boss fights part C, the boss maker** (30 October 2026; `bossmaker.py`). Fifteen bases (`BASES`: mage
  of fire, cold or storm (`SCHOOLS`), necromancer, cult leader, witch, druid, champion, band leader, assassin, hunter,
  great beast of a body and a stuff (`BODIES`, `STUFF`), dead lord, golem, chief of a hostile people, pirate captain,
  fey lord), each with pools per role from the move library. `draw` builds the kit by rules: two small moves, one
  set-up and great pair, the heaviest blow only from level 8, three phases (.66, .33) from level 10 and else two
  (.5), a summons trick when it has helpers, no move that needs a roof out in the open (`ROOF`), one weakness, up to
  two traits (`TRAITS`: those with a card add it, `TRAIT_CARD`; armoured counts for the war hammer and raises its
  defence, warded adds 30 to its resistances but its weakness, unbroken has resolve 4, regenerating heals 2% a turn
  unless it burns, twinned brings its Shadow, linked 'survivor', grudge has more life, hoarder leaves coin), a name
  (men and women by the gender drawn), a title, a deed and one rumour (its weakness or a great blow). `apply` puts
  it on a monster (`mon.kit_over`, `mon.bs`, `mon.maker`, life x3.5 and a tenth a level). Jobs: 'head' ("A price on
  a head", town and city boards and the captain; pays by level and traits; won like a bounty), and `wrap` gives the
  nest, shrine, boats, missing and deserter jobs a boss and its rumour (`m.data['bspec']`, put on the leader in
  `jobs.fight`). A boss of the people that would die at its last threshold yields three times in five (`yields`):
  kill, let go, or hand over (the reward a quarter more). A beast leaves parts of its body (`felled`), a chronicle
  line names the deed. Fixed bosses: the floor above foretells it (`FORETELL`), its own floor hides the thing it
  cannot abide (`BOON`, an item 'boon'); carried into the fight it fills two dots (`boon_edge`). Handbook: Fighting,
  Bosses. Test `boss_maker`. SAVE_VERSION 54. Not built (still in `docs/plan.md`): arenas dressed per place, other
  ways out, the place that wakes or falls in, fights won another way, bosses for the big one and the relic.
- **Round 24: cities that grew, part 1** (30 October 2026; `citygrow.py`). `towns.gen_city` now asks
  `citygrow.make`: the city is grown in its own frame (sea to the north, river west to east) by `grow` and turned to
  face the world (`_to`, `_dir_in`). `plan` chooses the maker (metropolis 360x220; a harbour city off the hills a
  canal city, else a grown city, 240x140), the heart from the realms (`ruler`: the emperor's palace, a king's or
  baron's burgh, else the cathedral; a metropolis never a burgh) and a bastioned wall for a grown city in a march.
  Six winding main streets from the market; a world road takes the nearest (within .6 rad) and gets its gate and
  road out, the rest end at the lane inside the wall; roads from nearly the same side are spread apart (`spread`).
  Lanes are tried by the map's size, then a pass of blind lanes into the far yards; scraps of street cut off go back
  to garden (`crumbs`). Houses (`c.houses`) become the buildings (`_buildings`): guild halls by the market, the
  secret ones far down a lane, inns by the gates, shops by the market, stables and barracks by the gates, a temple
  if no church, the burgh or palace is `m.seat` (realms furnishes it first); townsfolk live in at most 58 homes (110
  in a metropolis). Bridges, quay walls and gate bridges have their own look (`m.over`, drawn by `look.py` on
  streets of non-world maps). `rules(c)` counts each city rule. Handbook: Towns, Cities. Test `city_rules` (eight
  kinds on three draws, and every human city of a world: gates and market walkable). SAVE_VERSION 55.
- **Round 25: cities that grew, part 2** (30 October 2026; `folktowns.py`). `maker_for` sends a dwarf city or
  metropolis, a halfling town and a half-orc town to their own maker, built in its own frame by `citygrow.grow`
  and peopled the same way (`WATCH`: the shirriffs, the chief's guard; `HOUSES`: what a town has by its services).
  Dwarf city: the mountain on the side of the high ground (`citygrow.mountain_side`), the sea before it; the gate
  of the hold is the lord's hall (`m.seat`), terraces with ledges, the Great Stair and four lesser stairs of stone
  steps (tile STEPS; `_steps_join` cuts steps to cut-off terrace ends, the rest goes back to rock), the forge square
  with stalls, the forge hall and the smiths' guild hall, the cart line, one gate below; roads out along the foot
  of the mountain (`_side_way`). Halfling town: the hedge ring, the green with the party tree and lanterns, the
  Keepsake Hall and inn on the green (great buildings, furnished), hill homes dug in, row cottages with vegetable
  patches, orchards, a pond. Half-orc town: palisade and stakes, the chief's longhouse (`m.seat`), the fighting pit,
  three mud rings, longhouses for inn and trader, round huts with doors to the path, pens, the open forge. Half-orcs
  now have towns: `settle_orcs` gives the towns furthest from Thornfield (`scaled(2)`) to them, with names of their
  own (`names.orc_town`); dwarf cities get dwarven names. Bridges on the land (`dress_bridges`, from `zones.make`):
  each road crossing is laid straight or at 45 degrees from bank to bank, the road in line at both ends, in the style
  of `people_at` (nearest people's place): human stone with parapets, a timber trestle, sometimes a fallen span;
  dwarf granite with braziers; elven roots, leafy rails, glowmoss lanterns; halfling flower boxes; gnome copper;
  logs and stakes of the tribes; lizardfolk reeds. Tiles 236-249. `rules(c, folk=True)` keeps their own rules.
  Handbook: The peoples, Their own lands; The land, Walking the land. Test `city_rules` grows. SAVE_VERSION 56.
  Not built: the gnome bascule lifting for boats (it is only drawn); chasm bridges.
- **The Rogue a little stronger** (30 October 2026, Nilio's wish after block 4). The pure Rogue's rule (`trees.RULES`)
  also gives 20% more weapon damage to a poisoned foe (`wvs` 'poisoned'), so Envenom feeds it. The balance test: the
  Rogue went from 22 to 24 of 24 waves, on the test's draw and on another.
- **Round 26: trade part 3, caravans** (30 October 2026; `caravan.py`). Once you own the mule cart the stables
  sell wagons (keys c and d: a mule, 150 cargo, or an ox, 210 and slower), three at most, four from League rank 6,
  each with a driver at 15s a week (`p.caravan`). With you they add their cargo space and follow on the world map as
  a string of ♦; off the road they cost 1.6 times the step, a broken wheel now and then, spring mud, a ford or a
  swamp stops them; the beasts eat a grain a wagon a day (hungry: slower); unpaid two weeks, the drivers stop. Into a
  town they go to the stables (a fee a night, key e takes them out), at a dungeon or site they wait outside and join
  you when you come back. Raids on the road (richer load, worse land: more often; a watch of hirelings: less) ask a
  toll (`EV.ask` 'wagon_raid') or fight on the land map among the wagons; robbers strike at the wagons too, a wagon
  knocked over loses a share of the load, fleeing loses one. On the land the wagons stand behind you by day and in
  a ring at night; walking into one (`EV.ask` 'wagon'): mend a wheel (tools from the cargo, or half a day), pay the
  crew, make camp (a round of ale, wine or mead), leave the caravan, take it on. A camp with wagons draws more
  robbers. A ferry costs 25 more a wagon. The NPC caravans: walk along for a fare (a quick journey to where it goes),
  trade on the road at its home town's prices, a League caravan races you when you buy 20 or more of a good,
  robbing one puts more guards on the next from its town and makes the good dearer where it went. Handbook: Trade,
  Your own wagons. Tip 'wagon'. Debug events: wagons, a raid, a League racer. Test `caravans`. SAVE_VERSION 57.
  Not as the spec: the wagons are sold at the stables, not a wagonmaker; walking along is one quick journey; trade on
  the road uses the home town's market; people do not yet talk of your caravan by name (the news round).
- **Fixes at the end of block 6** (30 October 2026). The human bridge parapet was drawn with a sign the tileset
  lacks (a crash at such a bridge); two bug reports in one second now get folders of their own; the creatures test
  puts the shrieker in sight. A harbour town no longer loses a road whose way out fell inside the harbour: the road
  now leaves the map beside it (`towns.dry_exits`, an old fault: 8 of 81 harbour towns in three worlds).
  The crown's towns are human even when the crown was first drawn as dwarves or elves (`world.py`; the realm
  makes it the human empire later), so Thornfield never keeps dwarf shifts; a rival hunting with you finds room
  near you when you are hemmed in.
- **Rounds 31-32: the great evils parts 3 and 4, the other sixteen servants** (31 October 2026, one round;
  `servants.py`, hooked into `evils.py`, `shadow.py`, `data.py`, `bosses.py`, `look.py`, `townlife.py`). The 24 kinds
  are whole: light the Ifrit (desert, wells and caravans), the Nightmare (no rest in the open), the Gorgon (villages
  turned to stone), the Wild Hunt (travellers gone on the night roads), the Hag (sour milk; her hut walks a little each
  month, `walk`); middle the Rat King (plague in a city, its lair just outside one), the Queen under the Hill (the
  wood takes villages), the Vampire Count (marries into a barony and holds it), the Keening Woman (a lord dies,
  `realms.die`), the Thunderbird (burnt fields, ships lost), the Lindworm (a dwarf hold's deep galleries fall in; its
  lair over the holds); heavy the Sold King (a king takes the black banner and makes war, `start_war`), the False
  Prophet (villages follow him, the Church splits), the Debt Lord (a kingdom's burden grows, a barony pledged), the
  Giant King (winter stays, the ice raiders ride), the Demon Prince (cults in the cities, the Church burns them).
  Each: names, mark (`look.TAINT`, signs, a line on the look), four lieutenants (three drawn), a weakness (fire or
  frost half again, blows a quarter harder, no calls, a quarter weaker), a relic with one small power (new words:
  sight, armour, better finds), lair folk by tag, a boss with resistances, lore and a deck of three phases.
  `place_lairs` knows 'desert' (the dry biomes), 'city' (4-9 from a city, away from home) and 'dwarf' (4-12 from a
  dwarf hold); a light or middle kind without its land gives way, as before. The loose ends of parts 1 and 2: a
  hireling who falls where the dead are bound rises as his shade (`skyseat.merc_shade`; no raising while it walks,
  `mercs.bound`, a month at most; in hardcore it holds his body); a village struck by a servant sends a band of
  refugees on the road to the nearest town (`townlife.road_refugees`, at most 6 scaled, talk as in the towns); a
  fallen servant's held baronies start a real war between their kingdom and a neighbour (`shadow.freed_war`, also at
  the end); the Cinder Key, a relic from the Ashen Deep's broken gate (`skyseat.cinder_key`, once). Debug: The shadow
  (S): every lair on your map; 8, 9, 0 swap the heavy, middle or light servant for the next kind of its weight
  (`debug.swap_servant`). Test `servants`. SAVE_VERSION 61.
  Not as the spec: the new bosses have no named sets of three (as the eight of part 1); the Rat King's lair stands
  outside a city, not under its streets; the Giant King, being heavy, keeps his lair when a world has no cold land.
- **Round 30: more places and the places of the seasons** (30 October 2026; `yearplaces.py`). 40 kinds on
  landmarks' frame (their sign, words and play in landmarks' tables; only where they lie in `yearplaces.PLACE`, placed
  after round 29's). The land: dragon's scorch (the dragon's name and fate in the chronicle, a scale in half the
  worlds), lightning oak (storm wood every 60 days; a thunderstorm strikes you, `STEP`), sunken boat (three dives),
  old mine of men (a load of ore or a copper every 30 days; a beast inside), avalanche cart (spring once a year),
  flood wall (years in the chronicle, a brass marker). People apart: hedge wizard (scrolls and potions, Varnish lore
  monthly, a scroll for frog legs), charcoal family (a lead every 14 days), ferryman (8c over the river), beekeeper
  (honey, a load for 40c), bothy (sleep, heal, once a day), exiles' hamlet (a tale, a stall). Peoples meeting: peace
  stone (a kill there costs both sides 2), mixed graveyard (epitaphs, a small blessing monthly), trade bridge (free
  crossing), orc farm (cheese). Secrets: robber's cache (hidden; the wrong milestone shows it), lovers' tree (Varnish
  names, carve your own), hidden still (spirits, warn him). Seasons: salmon leap (spring and autumn, bears), flood
  lake (rescue the family once a spring), lambing fold, bird cliffs (eggs, a fall), orchard, the drought's drowned
  village (only in a dry summer, one in three: the mill's rule), tournament (one bout a day in summer, 3s and crown
  favour), harvest camp (Goldfield and Harvestmoon), travelling fair (summer only, one of its stops each week:
  `daily`), rutting glade, mushroom wood, goose marsh, vineyard (the new wine at the end of Leaffall), pannage wood,
  frost fair (Longnight and Deepfrost; the ice cracks late), ice road (winter, thin near the thaw), herders' winter
  camp (furs, where the ice raiders rode), wolf winter (a hard winter, one in two: 40c a pelt), snowed-in inn (a thief
  among the guests, or not), Thessa's harvest stone. The Standing Night (21 Longnight, by night near the road of the
  bound dead: they turn to the Sky-Seat) and the Loosing (14 Seedwake, inside a wind tower: a Varnish fragment) are
  days, not places (`old_feasts`). Handbook: The land, Odd corners and Places of the seasons. Test `year_places`.
  SAVE_VERSION 60.
  Not as the spec: the old mine's beast is a bear, bats or wolves, not a dungeon; the hedge wizard wants frog legs
  only (no wind in a pot); the cache shows by its milestone, not by a map from a robbers' den; the frost fair keeps
  every deep winter, not one in ten; the tournament's knight is an ordinary fight in a ring of fence, not a joust.
- **Round 29: old places part B and the places of the peoples and powers** (30 October 2026; `landmarks.py`, the
  frame for round 30 in `yearplaces.py`). 56 kinds of site (`KINDS`, `LOOK`), placed after the shanty camps by
  `place` with dice of its own (`Lay`: free cells with a shrinking gap, cells by a road, near a people's land or a
  raiders' seat); a few come and go each day (`daily`): a realm's war camp while a war lasts (`realm_camps`), a
  refugee camp by a plundered village for 40 days (`refugee_camps`), a prospectors' camp near the Starfall for 30
  (`prospectors`). Each has a small map of its own (`site_map`, `BUILD`), with telling things (tile MARK, `m.tells`,
  named by `thing_name`), keepers (role 'landmark') and one choice dialog (`EV.ask` 'lm'). What they do: the burners,
  peat cutters and lime burners buy food and ale cargo at x1.35; salt by the load at the pans; a beacon is a lookout
  and burns at night in a war or with raiders within 25 (`lit`, `glyph`); the lighthouse's cut wick; the toll
  bridge (pay or dodge, a crime); the caravanserai (stew, bed, news, a caravan master's goods, no raids within 2:
  `caravan.raid_chance`); the hunting lodge (poaching is a crime, `on_kill`); the boundary stone moved at night; the
  mill (still in one summer in three); the Church's tithe barn opened in a revolt; holy well; witch's healing for
  luck or hair; the star cairns' star-path (a voyage a day shorter, `sailing.sail`); dwarf roads in pairs; the duel
  ring (`duel_won`); the rope bridge; the moot stones' market on the 15th. Marks of what you did on `p.marks`.
  Handbook: The land, Places of today. Test `landmarks`. SAVE_VERSION 59.
  Not as the spec: the pretender's hiding place was already built as the powers' 'exile' site; the jobs these places
  could give are choices at the place itself; the burners buy food rather than sell charcoal; the refugee camp
  empties and does not become a hamlet; the pass cairn gives a blessing for the road, not cheaper guides; the
  star-path shortens a voyage by a day.
- **Round 28: feast days, the light-feast and the great fair** (30 October 2026; `feasts.py`). `FEASTS` holds 35
  feasts, each with its dates, who keeps it (`keeps`: all humans, the heartland, west or north by `names.dialect`,
  the fjords, northern villages, river towns, ports, the great city, the steppe, savanna, desert, jungle and canyons
  by the biome, and the peoples in their towns and sites: `keeps_site`), what you see, its decoration, its prices
  (`economy.FEAST`, set every day by `daily`) and one or two things to do. On a feast day the name stands on the line
  under the map, the square is dressed (`m.over`), a figure stands in it (role 'feast'; `EV.ask` 'feast'), the folk
  gather there from five until late, and a first-time tip 'feast' says to walk in. The things to do, once a year
  each (`p.feasts`): a blessing (a buff for a few days), a vigil until the lights come back, a free meal, a rumour, a
  few coppers, leaping the fire, an egg in the hedge, the Masking's mask (`masked`: `crime.at_gate` lets you in where
  you are wanted), honey for the gnomes (welcome after First Frost), the boot of Wanderer's Eve (in the morning an
  apple and coppers or a rhyme that is a rumour; coal if you are wanted; Skell's luck for his faithful), the way to a
  hidden glade at Starsong, a gem at the Shine, the amnesty of the Oath Day. The Light-Feast is kept on 1 Leaffall in
  northern villages (a blessing against the cold). The Fair of Skell (`FAIR`, `fair_week`): a week a year in each
  human city, the same week every year: travelling traders all week, a tenth more for what you sell
  (`economy.fair_day`), pickpockets likely. Handbook: The year, Feast days (with the table, `table_rows`); Trade (the
  fair). Test `feasts`. SAVE_VERSION 58.
  Not as the spec: the Light-Feast keeps a fixed date (the first dark night of Leaffall), not the first night the lights
  are really seen; the feasts' effects on the dead (stronger on the Naming, a ghost led off by the lanterns) and on the
  tribes (no attack in the Leaping week, the Night of Tusks' duels) are only in what you see and the blessings; the
  Lean Month's priests do not mind what you eat; no beds dearer or free at the temple on Hearthnight.
- **Round 27: round 6, livelier settlements** (30 October 2026; `townlife.py`). Dressed once per map (`dress`):
  woodpiles against the houses (tile WOODPILE, only where blocking keeps the way round joined: `_ring_ok`), archery
  butts and two archers in an elven glade or city (BUTTS), the poor quarter of a grown human city (the homes
  furthest from the heart: half-orcs and goblins, patched walls and mud lanes in `m.over`, beggars and a night
  trader, role 'slum'). Each day you come in (`on_enter`): the town's mood (`mood`: 'fear' with a hostile band
  within 14, a war, raid or siege event, or a great evil's mark near; 'feast' for a week after its king won a war,
  `realms.end_war` sets `won_day`), with guards called up at the gates, doors shut and half the folk at home, or
  tables in the square; refugees (`refugees`) from each awake servant whose land lies within 40 beyond its reach,
  in cities and towns, who take a silver (Solmara likes it) or tell their tale and where a lieutenant keeps (marked
  on your map, once a refugee); one small happening (`happening`: a brawl at the inn, a runaway pig, a funeral to
  the temple, a pickpocket), each solved with a bump for a small reward. Every turn (`tick`, `target` from
  `towns._target`): halfling meals (seven a day) and hedge lanterns, doors shut at seven; elves quiet by day and
  singing at night, lights in the trees; gnomes dive into their holes (until you are friends with the elder) and
  pick mushrooms at dawn; dwarves by the shift bell at 6, 14 and 22, the ale hall after a shift; orcs spar, goblins
  squabble; the kobolds' hoard grows a little every three days; lizardfolk bask by day and, roused at night or in
  winter, are slow. Market day brings two to four travelling traders with a stall (`market_day`). The look
  (`look`, from the map drawing): fields by the season and its half, woodpiles by the year. Shanty camps
  (`place_shanties`, a site 'shanty' by each human city, with dice of its own; `shanty_map`). Handbook: Towns (the
  woodpiles and fields, A town that lives, The week); The peoples (each people's day). Test `town_life`.
  SAVE_VERSION 58. Not built: the shutters on the houses are doors that shut (no new tile); the carts on the dwarves'
  line move as before; the hoard grows in glitter, not in coin you could take.

## Spell effects (built 19-23 October 2026; the spec)

**Part 1 built 19 October 2026 as a quick win, part 2 on 22 October** (see `docs/built.md`): the toolkit (bolts with
a tail, bursts, drain, rising crosses, the zigzag), status colours on creatures, Wild Shape's colours, monsters'
arrows and spells, the option full/short/off; each school its own hand (rings and waves, Meteor's shadow and slanting
fall, the corpse that greys and rises, Morrak's Bargain, walls one stone at a time) and the one white frame of Call
the Storm. The weapon skills' effects came with the weapon skills (23 October 2026: the swing arc on skills and critical
hits, blood on the cut, a bleeding foe's trail; proposal in the project files, `magie/wapeneffecten/voorstel.md`). The spec below is the whole plan.

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

## The great evils as storyteller (built 29-31 October 2026; the spec)

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

## More places and the places of the seasons (built 30 October 2026; the spec)

From "Old places on the land" in `plan.md` (approved 23 October 2026; `poi/volken.md` 45-86):
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

## Old places part B and the places of the peoples and powers (built 30 October 2026; the spec)

The section "Old places on the land" (approved 23 October 2026, all built by 30 October 2026): More points of interest, so the world looks old and lived in. Approved in the thread on points of interest: "we gaan
eerst A doen, alle ideeen klinken goed". Details and the full list (also the newer places, part B): project files
`poi/ideeen.md`. Each place is one world cell with its own play map (as the wonders and oases), and what matters is a
tile used with one key or a bump. Not the same as what exists: the fresh battlefields and plundered villages of
`living.py`, the hidden places of `hidden.py`, the planned temples, forts and barrows.

From "Old places on the land" in `plan.md` (approved 23 October 2026; `poi/ideeen.md` part B, `poi/volken.md` 1-44):
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

## Feast days, the light-feast and the great fair (built 30 October 2026; the spec)

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

### Trade as a way to play (approved 25 October 2026; built in rounds 14, 22, 26 and 28)

Nilio (thread "Handelssysteem en waren doorlichten"): trade should be a full way to play the game, for players who
want to play it differently. Builds on `economy.py` (19 goods, stock-driven prices, NPC caravans in `wanderers.py`).

**Fixing the money first:** built 29 October 2026 (round 14, see `docs/built.md`).

**Small to great** (Nilio: begin small and grow). A trader climbs a ladder, each step paid for by the one before:
a peddler's pack (30) with cheap goods from village to village (grain, salt, ale, wool: a few silver a trip, but
safe and sure), small supply orders from a village's board; then a pack mule, then a cart; then wagons, crew and League
rank; at the top the dear goods, named goods, masterworks and far goods. The road is long (Nilio); where it ends (a trader's goal beyond the League title) is for later. Capital is the gate, nothing else: dear goods
cost too much to buy in bulk early, and small towns hold only a few of them. Neighbouring villages differ enough that
the first short trips always pay a little.

**Goods and ways:** built 30 October 2026 (round 22, see `docs/built.md`): named goods, master makers, far goods,
barter, monster goods, spoiling, need far away, contraband, war trade, market news, rank with the Merchant League. Still
here for later: the great fair (with the feast days, round 28).

**Your own caravan and the NPC caravans:** built 30 October 2026 (round 26, see `docs/built.md`).

UI: named goods stand by their own name in the market list; the caravan is a sign on the world map named by
`guide.py`; its choices are one `EV.ask`; each new key gets one first-time tip. The handbook's trade chapter grows with it.

## Round 6: livelier settlements (built 30 October 2026 as round 27; the spec)

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

## Trade part 3: caravans (built 30 October 2026; the spec)

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

## Cities that grew, part 2 (built 30 October 2026; the spec)


The human cities, the metropolis, canal and fortress towns and the machine-checked city rules are built (see
`docs/built.md`, "Cities that grew, part 1"). Left for round 25: the other peoples' towns and the bridges on the
open land. The mockups are in the project files under `steden/` (`mockup_volken.py`). The city rules of part 1
hold here too and the test part `city_rules` grows to check these towns.

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

## Cities that grew, part 1 (built 30 October 2026; the spec)


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

## Boss fights (approved 26 October 2026; built 29-30 October 2026; the spec)

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

## Trade part 2: goods and ways (built 30 October 2026; the spec)
From "Trade as a way to play" (approved 25 October 2026; the caravans and the great fair are still in `docs/plan.md`):

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

## Archaeology (built 30 October 2026; the spec)
From "Old places on the land" (approved 23 October 2026):
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

## Life skills part 2 (built 30 October 2026; the spec)
Worked out with Nilio on 19 October 2026; details and tables in `/mnt/project-files/lifeskills/overzicht.md`. Part 1
(the curve, the herbs and alchemy, brewing, Smithing and Tailoring, the materials by tier) is built: see `docs/built.md`.
Left from part 1 for round 20: the road goods of Leatherworking (marsh, mountain, snow and sand boots that make travel
over that land quicker; tent and bedroll; barding for your beast; a quiver), Lockpicks from the anvil (once there is a
lock to pick), the master perks at 30, 40 and 50, and xp without gathering (orders at your own height in every town,
mending for others).
- **Crafted gear:** quality (crude, fine, masterwork); a base material (hide, metal or cloth: the grade and its own
  property) plus one beast part of the maker's choice, which gives the power; two parts from rank 40.
- **Every beast gives parts, from the first wolf on** (Monster Hunter's way, 19 October): fangs (to hit), claws
  (damage), horn and tusks (armour), antlers (stamina), feathers (lighter), chitin (poison resistance), scales (fire or
  cold resistance), ivory (life). The same part from a stronger beast gives more (wolf fangs +5, winter wolf +10,
  sabretooth +15), so better gear means hunting stronger beasts; old parts are sold. Big beasts (bear, aurochs,
  mammoth, drake) can have a part broken off too. Below the beast's tier in Skinning, parts tear more often.
- **Special powers** (+ranks in a school, leech, life or mana on a kill, crits, all resistances, thorns, less damage,
  Strength or Dexterity) exist only on found gear and on the parts of named beasts, so rares stay what players hunt
  for.
- **Unmake** (rank 40 in the craft, at its own bench): one power of an identified found piece moves onto a piece you
  made; the found piece is destroyed; one moved power per piece, at about two thirds of its value (full at 50). Uniques
  and sets cannot be unmade. It can always fail: about 40% success at rank 40, 55% at 45, 70% at 50, never above 80%;
  a strong power costs 15%. A failure loses the found piece; one failure in four also wears your own piece to broken or
  curses it. The chance shows before you confirm.
- **Master tests at 25 and 40:** one job from a master somewhere in the world before the skill goes on.
- **Perks up to 50** (19 October): every skill gets master perks at 30, 40 and 50 (Fishing 30: ice fishing through a
  hole in winter; Mining 30: you see a vein through one wall; the crafts at 30: mend on the road with a kit, at 40 two
  chosen powers and Unmake, at 50 masterwork more often and Unmake at full value). The full list is in
  `/mnt/project-files/lifeskills/content.md`.
- **Gear for your hirelings:** crafted gear can be handed to hirelings (weapon, armour, helm, shield), and you mend
  theirs with your craft: the thrifty way to fit out a company.
- **Hunting the named beasts, Monster Hunter's way** (19 October; builds on `named.py`):
  - **Parts:** beside its trophy a named beast gives one or two materials (pelt, horn, scale, venom gland) that carry
    one of its traits (Frost-touched: cold resistance; Venomous: poison resistance or a venom oil; Stone Skin: more
    armour; Swift: lighter). A piece made of them bears the beast's name ("Old Greyback's Hide Armor"): the crafts'
    rares. No set bonuses (they would clash with the class trees).
  - **Breaking a part:** a critical hit while it is below half its life breaks off a horn or tail: one more material.
  - **Skinning counts:** taking the parts off whole needs rank 15 (notable), 30 (notorious), 45 (legendary).
  - **A den of its own:** every named beast gets a den when it is made, near its home, of the land's kind: a hollow
    tree or thorn thicket in a wood, a cave in the hills, a mud wallow in a marsh, a ledge high in the mountains. A
    real den, not a dungeon: one small map with bones, the leavings of its prey, now and then a shed scale. One sign on
    the world map, shown only once you have found it; `>` goes in. Out of its den it roams the world and the play maps
    as now; beaten, it flees there, leaving a blood trail.
  - **The den goes with the beast:** when it dies its den is gone; a new beast brings a new den. So the number of
    dens never grows past the number of named beasts (the cap that is there now: about 9, rising to 18).
  - **Legendary beasts** keep a place of their own: the deepest level of a dungeon, a dragon's nest, or old ruins.
  - **Catching one alive** (a job kind: a baron wants the beast alive): below a quarter of its life, throw a sleeping
    draught (Alchemy); it sleeps a few turns; bump it with a rope to bind it; men with a cart come for it. If it wakes
    first it is furious. More coin, no parts. No zoo to build: the baron keeps it in a cage in his seat's yard
    (one cage tile per beast you brought), so you see your catches when you visit.
- **The great masters** (22 October): one master per craft in the whole world (a smith, a leatherworker, a
  tailor), far from the roads. They unmake for a hero who lacks the craft, but only after a real quest: first find
  them (no marker; rumours, a book in a library, an old craftsman who knew them), then their test in three parts:
  bring a top find of their craft (Star-iron, the parts of a named beast or a dragon, Fey Silk), bring the part of a
  notorious or legendary named beast, and win back what they lost (an old forge, a workshop or a hall overrun by
  whatever lives there now). After that they work for you: one Unmake per visit, for a high price (gold, not silver),
  at a 50% chance (less than a master player at rank 50), with the same bad failure. Your own craft stays the better
  road.

## Life skills part 1 (built 30 October 2026; the spec)
Worked out with Nilio on 19 October 2026; details and tables in `/mnt/project-files/lifeskills/overzicht.md` and
`content.md`.
- **Slow, like an MMO, without grinding.** Work far below your rank teaches nothing, close below it little, at or above
  it most; the colour of a name in the craft list shows which (grey, green, yellow, orange). The first time you make
  or catch something counts double. Steeper curve: `20 + 4r + 0.35r²` (rank 10 in about an hour, 25 in 12-15 hours of
  play, 50 in 60+ hours: one skill per hero).
- **The same rule for the disciplines** (weapons and schools): foes far below you teach little. Their pace stays
  (rank 100 in about 30 hours of play); a life skill is the long road beside the fighting.
- **Herbalism joins Foraging** (its perks move along). **New: Smithing** (an anvil; ore becomes bars; mend your own
  metal gear for ore and time; weapons and metal armour) **and Tailoring** (cloth: light, mana and resistance, warm or
  cool). With Leatherworking every kind of armour is made by someone.
- **Each craft its own field, beyond armour** (19 October): Smithing is the fight (metal armour, every metal weapon,
  tools: pick, skinning knife, lockpicks, fish hooks; honing a blade at the anvil, a short buff). Leatherworking is the
  road (leather armour; marsh, mountain, snow and sand boots that make travel over that land quicker; waterskin, tent
  and bedroll; barding for your beast; a quiver once arrows exist). Tailoring is the weather (cloth pieces, each warm
  or cool: Quilted Armor, Robe, Cap, Hood, Sash, Wraps, Soft Shoes; bandages, rope, a fishing net). New cloth bases
  come in three grades like the rest. Lists in `/mnt/project-files/lifeskills/content.md`.
- **Alchemy without fixed recipes** (19 October), like cooking: every herb has two properties; pick two or three herbs
  at `[P]` and what they share becomes the draught; three sharing one property make it stronger; nothing shared, a
  ruined brew. Strength = the herbs' tier and your rank. A shared Venom, Flame or Silver makes a blade oil (a short
  buff), a shared Sleep a flask to throw. You learn a herb's first property by tasting it, its second at Foraging 15
  when you pick it, both from a brew that works; unknown ones show as `?`. 17 properties (Heal, Mana, Stamina, Regen,
  Cure, Staunch, Ward Fire, Ward Cold, Ward Poison, Sight, Calm, Swift, Strength, Sleep, Venom, Flame, Silver) and 49
  herbs, most of them real (Nettle, Valerian, Arnica, Comfrey, Mandrake, Myrrh...), cooking herbs among them, spread
  so that almost every property grows in every tier. Top: Starmoss (doubles a brew; alone, the Starlight Elixir: +5
  life for good, once per hero). The list: `/mnt/project-files/lifeskills/content.md`.
- **Brewing, the craft of trade and company** (19 October): ten drinks (Ale, Berry Wine, Mead; Halfling Cider, Dwarf
  Stout, Gnome Cordial, Elven Wine, Juniper Spirits, Spiced Spirits, Royal Mead), learnt per people by tasting or from
  an innkeeper. A drink sells best far from where it comes from; from rank 30 a barrel, trade goods for a caravan. "A
  round for the company" at an inn or a campfire raises the hirelings' morale. A drink of their own people as a gift
  (the dwarf king, an elven guard, the kobolds) earns better prices, a rumour or a job. Strong spirits as the base of a
  draught make a tincture that lasts twice as long. Strong drink warms and gives courage; too much spoils your aim.
- **Fishing by tier** (19 October), fresh and salt water apart: A fresh Minnow (no longer at sea), Perch, Carp, Trout,
  Eel, Pike, Cavefish; A salt Herring, Mackerel, Sprat, Flounder, Cod. B Salmon, Bluefin, Catfish (marsh), Grayling
  (mountain streams). C Great Sturgeon (broad rivers; its roe is caviar), Swordfish (deep sea; its sword is a part: to
  hit), Ice Char (northern lakes, through a hole in winter), Deep Eel (underground lakes). D Ghost Pike (forest lakes,
  at night), Sailfish (warm seas; its fin: lighter), Blind Whitefish (caves, level 4 and down). E Thunderfin (at sea,
  in storms only; its scale: lightning resistance), Abyss Eel (deepest caves; its skin makes leather with poison
  resistance), Elder Sturgeon (the greatest rivers). Top: Golden Carp, Moonfish (starwater at night; doubles a dish),
  the legendary fish. The fishing net (Tailoring) takes small fish from shallow water without a cast.
- **Mining and Smithing by tier** (19 October): ore veins lie in every deep cave system (cave dungeons, karst
  sinkholes, the deeper levels of old mines), the tier rising with depth; the dwarves' mines are one place among
  them (digging there unasked stays a crime), so a bad name with the dwarves never shuts you out. A Iron (no
  property). B Silver Ore (hills far from the road, caves from level 2; strong against the dead), Bog Iron (cut from
  a marsh; cheap, wears faster). C Deepiron (caves and mines from level 4; wears slower), Bloodstone (canyons and
  mesas; some life), Frostvein (high mountains; cold resistance). D Blackiron (dangerous hills, orc country; more
  armour), Moonsilver (karst caves; lighter), Sunstone (desert; fire resistance). E Adamant (the deepest tunnels of
  any system; much armour), Wyrmstone (by drakes' lairs; fire and cold resistance). Top: Star-iron (the fallen star
  only; light and strong, with one special power). Gems as now, from Mining 10. Grade: A-B normal, C-D exceptional,
  E elite.
- **Tailoring by tier** (19 October; warm or cool is the maker's choice, the cloth adds its own property). A Linen
  (farm villages; cool; also bandages), Wool (herders; warm), Hemp (river farms; strong; rope and nets). B Felt (wool
  felted at a fulling mill; warm, sturdy), Cotton (southern farms; cool), Mohair (goat herders on alpine meadows; warm,
  light). C Spider Silk (spider caves; light, some mana), Highland Wool (far mountain herders; very warm), Sandsilk
  (oasis caravans; cool, fire resistance). D Shadowsilk (deep spider nests; foes see you later), Mammoth Wool (from a
  mammoth you hunted; cold resistance), Seasilk (giant shells on far coasts; lightning resistance). E Queen's Silk (a
  spider queen; much mana), Emberthread (fire beetles in volcanic land; strong fire resistance). Top: Fey Silk (light,
  one special power), never tied to one people: gathered at night by fairy rings and wisp marshes (wonders, several
  per world), from a legendary spider's den, or as an elven gift after a job.
- **Hunting, Skinning and Leatherworking by tier** (19 October; the game is all there already). A hare, grouse, deer,
  goat, sheep, wild boar (plain leather). B elk, reindeer, ibex, gazelle (sturdy leather), wolf (warm fur), snake
  (poison resistance). C aurochs, wild horse (sturdy), bear, winter wolf (warm), panther (lighter), crocodile (more
  armour). D cave bear, snow ape (very warm), sabretooth (lighter), mammoth, rhino (wears slower, much armour). E
  drake (fire resistance), frost drake (cold), swamp drake (poison). Top: the parts of named beasts and of dragons. A
  herd above your tier is "too wary for you yet": you cannot get close.
- **Every rank opens something:** veins, herbs, fish and game have a rank; below it they are "too hard for you yet".
  Grades follow the rank (exceptional from about 20-25, elite from about 40-45), with the matching material.
- **No grinding in one place** (19 October): the rank of a vein, herb, fish or beast follows the danger of the land
  (the danger layer) and the depth of a mine or dungeon, never one spot; each step has three or four options in
  different lands (Fishing 35: Great Sturgeon in broad rivers, Swordfish at deep sea, Ice Char in northern lakes, Deep
  Eel in underground lakes). The top finds (Moonfish, Star-iron, elven thread, dragon hide) are the crafts' own rares:
  scarce, one special property, never needed for a rank. Xp without gathering too: orders at your own height in every
  town, masterwork tries, mending for others.

## Trade part 1: the money fixes (built 29 October 2026; the spec)

From "Trade as a way to play" in `docs/plan.md` (approved 25 October 2026; the rest of it is still to build).

**Fixing the money first.** Today 30 gems from the hills to a city earn ~23 gold, while a job pays ~12 silver and grain
earns ~1.5 gold a trip; and stock springs back 15% a day, so two towns become a money machine. So: the price bends
harder the dearer the good (selling ten gems moves the price more than ten sacks of grain), stock comes back more slowly,
and each route tires (the same good to the same town fetches less until the market forgets). Weigh it against wages,
beds, repairs and the temple: trade pays well, never endlessly.

## Classes part 4: the epics (built 29 October 2026; the spec)

The rest of the classes spec is built (see `docs/built.md`, "Classes, trees and the bar").

- **Epic skills from hidden teachers** (approved 22 October 2026, from going through Project Gorgon's skills; the
  epics themselves settled the same day in thread "Epic skills", project files `klassen/epics/`: `voorstel.md`,
  mockups `epics.gif`). A tier above the elites, in the same slot: key 6 holds one elite or one epic, never both,
  so an epic costs you your elite. An epic is drawn in gold with its own sign ♦ (the elite keeps ☼).
  - **Two epics per class (22).** A teacher teaches the two epics of their class; you pick one and may swap at a
    later visit. With two classes you may learn from the teachers of both.
  - **Price:** an epic works **once per rest** (an inn, your camp), no mana or stamina on top; Phoenix once per day.
  - **Teachers:** a hermit, an old hunter, a witch, a retired master. **Two per class, 22 a world**, each in another
    part of the world and never both with the same people. You hear of them only through a rumour (`news.py`: an
    innkeeper, a traveller, a book), never as a sign on the map before you have heard, and only of the teachers of
    your classes, from class rank about 35; they teach at class rank about 40. When a teacher dies (war, plunder)
    the other remains; if both are dead, a pupil turns up elsewhere after a season, so no one is ever locked out.
  - **A deed first,** a job of their own in the jobs tab. Fire: an ash hermit in a burnt valley, bring a glowing
    ember from the heart of a fire mountain or fire wonder. Frost: a rime witch at a mountain pass, live through a
    winter night outside her hut without fire. Storm: a hermit on a lightning-split peak, ring the old bell on the
    top in a thunderstorm. Restoration: an old saint at a crossroads shrine, lay five restless dead to rest. Shadow:
    a witch (`powers.py`), steal a relic from a church. Necromancy: an old gravedigger, half dead himself, bring a
    crown or sword out of a barrow where a wight lies. Nature: an old druid at a wonder, plant a seed at another
    wonder and come back when it comes up (a season). Beastcraft: an old hunter, track and kill the beast of a
    rumour and bring its hide. Warcraft: an old champion of one of the realms' wars, win a duel against him (no
    hireling, no drink). Arcane: a magus in exile in a tower, bring a lost page from a library (`history.py`).
    Cunning: an old master thief "retired", steal something unseen from a baron's seat (`seats.py`).
  - **The epics:**
    - Fire: **Sunfall** (a small sun hangs a turn over a spot and falls, r2; the ground burns 3 turns) and
      **Phoenix** (while it is ready on key 6, a death blow burns you up instead: you rise with 20% life, foes
      within r2 catch fire, and you carry **4 flames** that never go out by themselves; each flame burns you a
      little each turn; each turn standing in water and each Health or Rejuvenation Potion takes one flame off,
      in any mix; who does nothing burns to death; shown as "Burning 3" with your states).
    - Frost: **Long Winter** (the ground r3 round you freezes for 10 turns: who stands in it slows, who is slowed
      freezes) and **Glass Heart** (one foe frozen 6 turns; a blow on it shatters it, heavy damage r1).
    - Storm: **Skyfather's Spear** (one stroke from the sky along a line of 10 tiles; wet foes stunned) and **Eye
      of the Tempest** (8 turns: arrows miss you, a spark leaps each turn to every foe within r3).
    - Restoration: **Miracle** (you and your company wholly healed, every ailment gone) and **Return** (your fallen
      hireling or beast gets up, if it fell in the last 20 turns).
    - Shadow: **The Unmaking** (costs life; a foe under 30% dies at once, otherwise loses half of what it has, a
      boss a quarter) and **Eclipse** (6 turns every foe in sight sees only 1 tile; you are unseen).
    - Necromancy: **Lich Form** (10 turns undead: spells cost no life, no poison or cold, your touch steals life;
      your `@` turns pale) and **Barrow King** (a barrow king rises from the ground, no corpse needed, and follows
      you until you rest).
    - Nature: **Wrath of the Wild** (everything within r3 grows shut: roots and thorns hold every foe, the land
      stays green) and **Oak Shape** (a fourth shape: a walking oak, slow, much life, keys 1-2 Slam and Root).
    - Beastcraft: **Call of the Old Ones** (a great beast of this land comes for 20 turns: cave bear, dire wolf,
      great eagle) and **One Blood** (10 turns your beast cannot die and you share its life).
    - Warcraft: **Earthshaker** (strike the ground: r2 stunned and knocked down, armoured foes too) and
      **Unstoppable** (8 turns no push, stun or slow; every kill fills your stamina).
    - Arcane: **Time Stop** (3 turns only you move: foes stand still, arrows hang in the air, the world goes grey;
      you cannot harm anyone in it, only walk, drink, heal or buff yourself, lay runes and traps: a way out and a
      way to get ready, not a killing key) and **Unweave** (everything magic within r3 is gone: buffs on foes,
      spell tiles, called creatures).
    - Cunning: **Death Mark** (unseen, your next blow kills an ordinary foe outright; a boss takes it four times)
      and **Shadow Dance** (5 turns every blow counts as an unseen first strike).
  - **Effects:** the same hand as the spells (star front, ░ glow, radius at most 3, at most ~0.4 s). Three looks
    only epics have: **a line** across the land (Skyfather's Spear, white then yellow), **drawn inwards** onto one
    foe (The Unmaking: your life out in red, then dark motes close in) and **the world grey** (Time Stop: only you
    keep your colour). Six are drawn in `klassen/epics/epics.gif`; the rest follow the same hand.
  - **The handbook:** a few sentences in "Who you become": what an epic is, that it takes key 6 from the elite, how
    you find a teacher, once per rest; Phoenix's flames in "Fighting".

## The Varnish (built 25 October 2026; the spec)
From "Old places on the land" (approved 23 October 2026; archaeology and part B stay in `docs/plan.md`).
- **Varnish ruins in the wild** (Nilio's addition): old Varnish cities, overgrown by forest, half under the sand in a
  desert, sunk in a marsh, frozen in the tundra. They have no name and no sign on the world map beforehand; you find
  them only by walking the land (the zones), and what you saw goes on your map. A city spans several zones: columns
  between the trees, a forum full of bushes, a gate without a wall, stones with Varnish letters that say its name.
- **Hidden dungeons** hang under such ruins: no rumour names them, no map shows them, no job asks for them. You find
  the way in only on the spot (a stone you read with the Varnish letters, a well that draws air, a floor that sounds
  hollow, a lever behind a statue). Its own boss and a treasure room, kept modest; unique to each world.
- **The Varnish get a face of their own** (approved 23 October; not a copy of Rome): iron, stars and measuring. Their
  black iron is star-iron (as in a Starfall crater): it never rusts and still shines in every ruin. They built to the
  stars (a city lies round a round sky well) and measured everything in leagues; league stones count down towards a
  ruin. They buried their dead standing, bound to the stone. This fits what `lore.py` and the stones already say (the
  Sky-Seat, the winds and the dead bound, the Hollow King, the northern wall of nine legions, the sealed vaults).
- **The Varnish' own lore** (approved 23 October, "de toon is goed, mag alle kanten op gaan"): loose fragments of the
  empire itself, not about today's world: its gods (today's gods are their worn-down remains: Skell was Eskelion,
  Measurer of Roads), emperors, mages, daily life, food, feasts, trades, soldiers, law, love, songs, books and plays,
  and its last days. They count years "from the Founding" (FF); the empire lasted 1400 years. Found as archaeology
  finds, on stones, in city library books, now and then as a rumour; the chronicle gets a chapter The Varnish with
  headings. A few longer works (the Song of the Nine Walls, the Book of Leagues) lie in pieces across the world, one per
  find; a whole work sells once and well to a city library, and its last line may point to a hidden place. Dry humour
  is welcome. The empire was not kind: the dirty side (slaves, "the uncounted", the dead bound for debt, conquest)
  shows too, with what people thought of it, for and against, from many mouths (Nilio: "de menselijke kant"). The texts: project files `poi/varnish-lore.md` (more may come).
- **Books bound from fragments** (approved 23 October): a book is a set of 5-8 fragments spread over the world
  (letters, sherds, diary pages), each readable on its own. From the second one the chronicle sees they belong together
  ("2 of 6", the gaps named, never where). With a whole set, a scribe in a city library binds it in order (talk, one
  option, a few silver and an hour) and finds what only the whole shows: a hidden last page with the end of the story,
  sometimes a lead to a hidden place or a piece of a riddle. The book is then a thing in your pack and its story in the
  chronicle; keep it or sell it once, well, to a library. 27 books written out (more may come); each world picks about eight at random, at least one from each
  thread (Tam and his mother, the winds, the fall, the uncounted, the bound dead, the emperors), and the pages lie where
  they fit. Stories cross between books, each still whole on its own. No new key. Stories and titles: project files `poi/varnish-boeken.md` (all 27 with their hidden
  pages and what they add to the chronicle or the map). Books of the dirty side too (Twelve, a runaway slave; a mother's petitions
  for her bound son; a dealer in the dead; a banned play); the stories may cross (a soldier in one is in another).
- **The five riddles written** (23 October; project files `poi/raadsels.md`): eight fragments each, some false (a red
  "Not so" later); a riddle is whole with about six; then the chronicle writes the answer and points to a unique hidden
  place (the Anchor, the Hollow Throne, the Pits of the East, the Last Vault, the Standing Hall). All five whole give a last
  paragraph, The Ruin, as it was. The answer, never told outright: the mages made the Hollow King of star-iron, every
  bound wind and the bound dead; they made the first orcs of the uncounted to feed the work; the last star they pulled
  down was the Ruin; the vaults hold the names and what they could not destroy. The great evils (`evils.py`) are of after the
  Varnish and stay out of these riddles (Nilio).
- **The Varnish places** (all approved 23 October; part C of `poi/ideeen.md`): the overgrown city round a sky well
  with a sunken Sky Court; the Northern Wall of the nine legions with its tower ruins; the wind tower that howls in a
  storm; the road of the bound dead (break a seal and the dead one rises); the star-iron forge by an old crater; the Gate
  of Leagues whose star map points to other gates; the sluice hall (open a sluice and a flooded hall runs dry); the fallen
  sky of black stones and glassy sand; the star house with an iron star floor under the dust; and as small extras a
  sunken harbour and old coins.

## Old places from the history (built 24 October 2026; the spec)
Part A of "Old places on the land" (approved 23 October 2026; the rest of that section stays in `docs/plan.md`).
- **Born from the history.** Each old place comes from an event `history.py` already writes: the battle of 120 years
  ago lies somewhere as an old battlefield, a plague left a deserted village. The chronicle says why it lies there, a
  library book can point to it, and the place proves or disproves what you heard.
- **Old battlefield:** grassy mounds, rusted spear points, a cairn for the fallen. Digging a mound gives rust mostly,
  very rarely an old weapon with a name from the chronicle. On the battle's day the dead walk the field at night.
- **Deserted village:** left after a plague, a war or a dragon. Roofless houses, a well, an overgrown field, a burnt
  chapel; now and then bandits, a hermit or a ghost live there. A plundered village of today that never recovers can
  become one after a year.
- **Broken bridge** of the old Empire: piers in the river, the deck gone, a ford beside it. Part of the old ways.
- **Memorials:** a stone with names (reading it adds a chronicle fact), a fallen statue of an old king with its head
  beside it, a gallows hill at a crossroads where the Watch hangs its sentences.
- **Old quarry:** half-cut blocks, a giant statue never finished; sometimes flooded (swim, fish). Stone, now and then a fossil.
- **Shipwreck:** a hull on the beach or a reef, reached at low tide; searched once, and often the wreckers came first.
- **Hermitage:** a hermit's hut on a rock or in a wood. The hidden teachers of the epic skills live in such places.
- **Leper colony:** a hamlet outside a city with a bell; temple jobs bring food there.
- **Marks of the peoples:** small signs of whose land it was: dwarf boundary stones with runes, elven moonstones along
  a path, orc skull poles, kobold scratches pointing at something shiny. Read or follow; never a key resource.

## The Rift and the Ashen Deep (built 24 October 2026; the spec)
a hell-like place. Mockups `H_ashen_deep.png` and `H2_ashen_deep_river.png` (the river running through).
  - **How it comes:** a rift opens in the world as a world event, like the raiders and revolts of `powers.py`. It is a scar on the world map, and the land round it slowly burns to ash. At night fiends raid the villages nearby, and the news goes round through people. Now and then the bottom of a very deep dungeon breaks into it instead.
  - **Below the rift:** 3 to 5 levels of black basalt, faintly warm, ash underfoot (large, 120 x 70; the bottom may be 150 x 90). A river of fire runs through each level, with a bridge of chains over it. Vents of brimstone puff choking smoke every few turns. There are fields of bones where the dead rise, cages hung on chains with the taken (a rescue), and a hall of black iron where a fiend lord keeps court.
  - **At the bottom stands the burning gate,** the anchor of the rift. Break it and the rift closes; the land heals slowly.
  - **Rules:** the heat lets you rest nowhere there; fire resistance and frost matter; the fire gives the light, so you carry none.
  - **Monsters:** the fiend family already in the game (imp, hellhound, hollow spawn, hungering shade), and these new ones (approved 22 October), each with one clear trick:
    - **Cinderling:** a small glowing ember thing that comes in swarms, the horde of the Deep; it dies into burning ground, so do not fight in its ashes.
    - **Chain Warden:** keeps the bridges; it throws a hooked chain and drags you to it, past the fire if it can.
    - **Ashwalker:** a dead one from the bone fields wrapped in ash; hit it and a cloud of ash puffs up that blinds for a moment.
    - **Brimstone Toad:** sits by the vents and spits sulphur that chokes: it costs stamina.
    - **Slag Brute:** big, slow and glowing hot: whoever hits it up close is burnt; frost makes it brittle, and then every blow does double.
    - **Gaoler:** keeps the cages; when it sees you it runs for the gong to wake the level.
    - **The Lord of Cinders,** the boss: each rift has one, with its own name from a list. While the burning gate stands it heals from it; put out the fire bowls round the gate first. At half strength it calls its hellhounds. It drops only its own gear.

## The northern lights' gift (built 24 October 2026; the spec)
Today the northern lights are only weather (`weather.py` 'aurora': cold lands, autumn and winter nights). Now they
give four things, only while they are in the sky:
- **What only the light shows:** some old rune stones and marks of the old ways (`hidden.py`) are plain rock by day.
  Under the lights they glow and point the way to a hidden place.
- **Magic in the air:** Frost and Storm spells cost less mana under the lights.
- **The barrow spirits:** at a barrow in the north a spirit rises under the lights. Talk to it once: it gives a
  random job that leads somewhere (an old grave, a lost sword, a deed undone). Do not dig into or rob its barrow:
  the dead wake, their glow turns brighter and restless, and they attack.
- **The light-feast:** northern villages celebrate the first night of the lights: news, cheaper beds, a blessing at
  their shrine.
- **The glow (look):** a spirit is a pale `G` that flickers half there, with a wan blue-green glow on the tiles round
  it and a faint wisp below; angry, the glow grows brighter and restless. The same glow goes on other ghostly
  creatures (ghost, wraith and their kin), and fiends (the Rift's) get a faint red fire glow. Mockup: project files
  `noorderlicht/spirit.gif` (`mockup_spirit.py`).
- **Handbook:** a few sentences in the world chapter on the northern lights and the barrow spirits.

## The K5 maker (built 24 October 2026; the spec)
- **The random maker for classic dungeons (K5, approved 22 October)**: the way of Brogue, in our style. The theme rooms come from the pieces; the rest stays random. Mockups `K5_ways_seed1-4`, script `mockups/mockup_brogue_v5.py`, notes `brogue.md` and `inspiratie.md`.
  - **Growing rooms.** Rooms grow onto the level one at a time. Each new room is slid along until its door meets a wall of what is already dug, and it is placed close to the middle, so the level stays compact.
  - **Many shapes, all mixed.** Plain, cut corners, round, L, T, cross, two rooms laid over each other, Z, chunky, a pillar hall, a rotunda round a stone core, a room with a room inside it, a pillared gallery, alcoves and a cave. Shapes are turned and mirrored. A shuffled deck makes every shape come up before one repeats.
  - **Rooms are big, for hordes.** About 11 to 18 wide, and halls 20 to 30.
  - **Two widths of passage.** A main way is 3 wide. It joins the rooms, it may be an L or a T, and it carries the route between the stairs; the big halls always get one. A narrow way is 1 wide and short, 3 to 10 cells. It leads to a side room, or cuts straight through the rock between two rooms as a shortcut. It is a choke point where a horde comes one by one.
  - **Every passage runs from room to room.** A passage attaches only to a room, never to another passage, so there is never a door between two passages. An arm that no room joined is filled in again, and a passage piece that reaches only one room is taken out whole.
  - **Loops** are cut only where walking round would take more than 30 steps.
  - **Lakes** go only where all the floor stays reachable, with shallow water round the deep.
  - **Doors and theme rooms.** About 60% of doorways get a door; the rest stay open arches. Rooms behind a single entrance are kept for theme rooms.
  - **A mood per level**, the way of DCSS and ToME: mixed, halls and passages, or close-packed.
  - **A check after making.** A door may sit only in a straight wall, and there are no double walls; for this the inner corner of an L or T, or the corner where a narrow way meets a wall, does not count. A bad door is removed. The mockups always show 0 bad doors and 0 double walls.
- **Theme rooms (approved 22 October)**: a room with one telling thing you use with a key or a bump. K5 keeps rooms with a single entrance for them; every fixed plan has its own spots for them. Each is a drawn piece with switches for variety, in its own shape (a nave with an apse, an L, an octagon, round, a cross, a gallery with bays, a half moon, a cave), turned and mirrored; Nilio can draw more in the editor. More ideas are always welcome. Details: project files `dungeons/themakamers.md`; mockups `R_theme_rooms.png`, `R2_theme_rooms_shapes.png`.
  - **Four parts per place, each its own list:** the entrance (a gate, a fallen-in way, a guard post with a gong, a stair hall); the arrival, never straight into a fight (the stair room, a dead adventurers' camp with a letter that becomes a rumour, a quiet chapel); the middle; the bottom (the boss's throne or lair, the treasure room, the hidden ancient bottom).
  - **Something to do:** shrine (pray for a blessing, or a curse if defiled); library (search for a tome, a map or lore, `history.py`); fountain (one drink, a random effect); abandoned forge (repair); alchemy lab (brew); fungus garden (forage; some puff spores); larder or kitchen (food, a fire to cook); wishing well (throw a coin for luck, gold for more); training hall (straw dummies, a little weapon practice, once); map room (read it and the level shows); wine cellar.
  - **Something to find:** locked vault (its key elsewhere on the level, often with a guard); choice vault (take one find, the rest sink away); hidden room behind a secret door; flooded hall (an island; swim, heavy gear sinks you, or freeze a way); armoury (only the gear of who lived there, mostly rusted: no loot piñata); fallen adventurer (one piece of kit and a letter).
  - **Something to fight:** pillared hall for a horde (pillars to break it up, a door to hold); summoning circle (step in by choice for a wave, a reward at the end); statue hall (one statue is not); ossuary (the bones get up at the bier); nest (webs or eggs: burn or wake); guard post with a gong at a choke point (silence the guard and the level sleeps); prison block (barred cell fronts between stone walls; a captive or something better left locked); mirror room (your double steps out); menagerie (a lever opens the cages, on whoever is near); echo hall (a fight here wakes the level).
  - **Something of the place:** chasm with a rope bridge and a collapsing floor (the edge rule: shove foes down); fallen-in room (clear the rubble, something behind); trap corridor (plates seen when searching); lava or fire rift (deep only); a cave breaking through; overgrown garden under a light shaft (herbs); sanctuary (wards no monster crosses: one safe rest); old arch of the old ways (`hidden.py`, with its word it takes you elsewhere); gnome clockwork room (gears open and shut the ways); bandits' gaming den (dice; catch them cheating).
  - **Each people flavours a room:** a dwarf shrine has a forge altar, a goblin library heaps of stolen books.
  - **Rules:** 2 or 3 theme rooms per level at most, never the same twice on one level, a mood line on first entry, and no light to carry: mushrooms and crystals give the light.
- **Rock you can see (Nilio, 22 October)**: underground, the solid rock beyond the walls is not plain black but shows a quiet texture, as in the mockups: a sparse speckle (#) in a dim earth colour, darker than the walls so it never reads as a wall or as floor. Fixed per cell (the same each time you look), and it shows only round what you have seen. Each kind of ground its own tint: grey stone, brown earth, dark basalt deep down; now and then a glint of ore in a mine. On the world above, built places keep their land round them instead.
- **Rivers underground (Nilio, 22 October)**: a river, of water or of fire, always runs through: it comes in at one edge of the level and leaves at another. Between caves it flows through the rock in a channel of its own, with rock for banks, so only the river passes there; it never just stops. It flows visibly: light runs downstream along it, as the rivers on the world map already do; fire pulses as molten metal does. Crossing takes a bridge, a ford or a crust of cooled rock, which makes a good choke point.
  - **Water:** you can swim it. Heavy armour and a heavy pack pull you under, so swimming in them asks first and warns. Monsters that cannot swim stay on the bank; some swim after you.
  - **Fire:** stepping in asks first (as at an edge) and burns you badly; there is no swimming in it. A shove or a knockback sends a foe into it, where it burns.
- **Hand-drawn pieces ("vaults", the way of Dungeon Crawl Stone Soup, `dcss.md`)**: small ASCII maps in data files with substitutions for variety, tagged by kind of place and by part (entrance, arrival, middle, bottom); the plan of a kind is laid out first and its rooms filled with fitting pieces. A piece may have a trigger with a message line (bars drop, the dead rise). Nilio can also draw unique places that appear once per world.
- **Events in pieces**: simple when → if → then rules, picked from lists in the editor's trigger layer (no typing, no real script language). When: step on, open, take, kill, enter a room, night falls. If: day or night, a job or item, people or standing, a chance. Then: a message line, a choice (EV.ask), a door or bars open or shut, creatures appear or wake, something caves in or floods, a job moves on.

## Weapons: more kinds, few disciplines (built 23 October 2026; the spec)

Approved by Nilio on 17 October 2026 (project files `magie/wapens.md`). Today: 16 weapon kinds in three grades
(48 weapons), four disciplines and Unarmed; shields exist (buckler, round, kite, tower; the grimoire also takes that
hand) but have no skills. New weapons join the discipline they fit; only **Spears and Staves** is new. Each new
weapon has one rule you notice in a fight. Everything comes in the three grades.

| Discipline | Weapons (new in bold) | The new ones' rule |
|---|---|---|
| Unarmed | empty hands, **cestus**, **tiger claws** | cestus hits harder and still counts as unarmed (monks); claws bleed |
| Swordsmanship | short sword, long sword, bastard sword, rune blade, greatsword, **scimitar** | quick and light (desert riders) |
| Axes and Maces | club, mace, war axe, great axe, maul, **flail**, **war hammer** | a shield does not stop a flail; a war hammer is strong against heavy armour (dwarves) |
| **Spears and Staves** | staff and war staff (moved here), **spear**, **halberd**, **scythe** | **reach**: strike an enemy 2 tiles away in a straight line, also past a friend; a spear can be thrown; a scythe hits the arc in front of you |
| Daggers | dagger, **throwing knives** | thrown with the bow's key, picked up again |
| Bows and Crossbows | short bow, long bow, war bow, **light crossbow**, **heavy crossbow**, **sling** | crossbows shoot and load in turn ("loaded" shows), go through armour, need little Dexterity; a sling is cheap and its stones lie everywhere (halflings) |

26 weapon kinds (78 weapons), six weapon disciplines. A mage with a staff no longer trains axe fighting.
- **The five new melee weapons in detail** (approved 22 October 2026; names, numbers and looks in project files
  `magie/vijf-wapens.md`; their two skills each are in the classes plan):
  - **Scimitar** (Swords; one hand, may go in the second hand; Scimitar, Shamshir, Talwar): cut in passing: if you
    stepped last turn, your first blow does +50% ("You cut in passing."). Needs little Strength.
  - **Flail** (Axes and Maces; one hand; Flail, Knout, Scourge): a shield, Shield Wall or formation does not help
    against it, both ways (an orc's flail goes over your Block too). Price: -10 to hit.
  - **War hammer** (Axes and Maces; one hand; War Hammer, Battle Hammer, Rune Hammer): new monster tag `armoured`
    (dwarf clans, knights and skeleton warriors in mail, golems, beetles, crabs) takes 25% less from weapons; a war
    hammer ignores that and does +25% on top. An enemy hammer wears your armour faster. Half-Sword, Crush, Iron Fist,
    Sunder and Armour Breaker use the same tag.
  - **Cestus** (Unarmed; worn in the gloves slot; Cestus, Spiked Cestus, Ironbound Cestus): with the weapon hand
    empty you fight unarmed with its damage and a little armour, so the second hand stays free (a grimoire fits).
    A critical hit stuns for 1 turn.
  - **Tiger claws** (Unarmed; gloves slot; Tiger Claws, Bagh Nakh, Wyrm Claws): one blow in four starts bleeding,
    stacking to 3. No blood, no bleeding: skeletons, golems, oozes and ghosts.
  - Carried by desert riders (scimitars), orcs and goblins (flails), dwarves (hammers); the Still Hand sells cestus
    and claws, gnoll pack leaders carry claws. Looks: a short arc on a cut in passing, a grey `]` flash when a flail
    passes a shield, a grey spark `*` when a hammer hits an armoured foe, stun stars on a cestus crit, blood on claws.
- **Shields** get no discipline: shield skills go into Warcraft (martial, stamina), beside the Iron Company's Shield
  Wall: Shield Bash (push one tile, short stun) and Block (the first blow of a turn is caught). Without a shield in
  hand they do not work.
- **Two weapons.** A light one-handed weapon (dagger, short sword, scimitar, club) can go in the second hand, the
  shield slot. One bump is two blows: the main hand as usual, the second for about half. The price: no shield, no
  block, no shield skills. Skills use the main hand, which decides the discipline that grows. Affixes of both count;
  mind the balance when building (the second hand counting half). On screen two short swings; the character screen
  shows the weapon as "off hand".
- **Who carries what** (only those who use gear drop gear): dwarves hammers and crossbows, halflings slings, elves
  long bows, desert riders scimitars, orcs and goblins spears and flails, the Border Watch halberds, necromancers
  scythes.
- **No wands**: the grimoire is already the magic second hand.
- **Next:** replaced by the classes plan above: two skills per weapon kind and one rule per discipline, then their effects.
- **Save data** changes (new bases, off-hand weapon): bump `SAVE_VERSION`.


## Classes, trees and the bar (built 23 October 2026; the spec)

Approved by Nilio on 19 October 2026 (thread "klasses en skills"; project files `klassen/`: the full list of names
and pair rules in `klasses.md`, mockups `fire_tree.png` and `bar_near.png`). Today all fourteen disciplines stay
open, 72 tome skills and eleven guilds mix freely, and a careful player ends up in one line anyway. Combat itself
stays as it is.

- **Start blank.** You wake in the temple with no class, only your weapon and its skills. The **first tome you
  read** wakes a memory and is your **first class** (one warning before you read: "This will wake a memory").
  From then on you read only tomes of your class; others you sell or keep.
- **A second class, late.** At **rank 20** (settled) in your first class you may read one tome of a second school; it becomes
  your second class and you learn the **name of your pair** (Fire + Shadow is a Hexblade). Who never takes a
  second stays **pure** (Pyromancer, Rimecaller, Stormcaller, Cleric, Warlock, Necromancer, Druid, Beastmaster,
  Warrior, Rogue, Arcanist).
- **Eleven classes:** the nine schools, plus **Cunning** (Thieves' Guild; stealth, poison, traps; the first blow on
  one who does not see you comes twice) and **Arcane** (Circle of Magi; Blink, Gate, Slow, Haste, Dispel,
  Counterspell, runes laid as tiles; the lowest damage; can take away or move what a spell left on the map). Each
  gets eight tomes like the schools.
- **One rule per pair** (55) and one **pure rule** per class (11): a fight rule that ties the two school rules
  together, given with the name (Hexblade: a foe both burning and cursed gives you life back from the burn). The
  name is also how people and the chronicle speak of you. Full list: `klassen/klasses.md`.
- **A tree per class:** three branches of six knots, some with 2-3 steps, a strong last knot (☼) at the end of each.
  A knot opens when the one above it has a point. Only **passives**: the actives still come from tomes, so the bar
  does not grow. One point per 5 ranks in that school (about 14 at rank 70): never everything. Points are spent
  only at rest (an inn, your camp); a temple takes them all back for coin. One screen, arrows and Enter, Tab to the
  other class. Examples: Fire has Pyromancer, Flameblade (your weapon burns: the spellsword's imbue, weaker than the
  spell, ~1 blow in 3, no mana coming back while it burns) and Kindler; Nature's third branch is **Shapeshifter**
  (wolf, bear, hawk: in a shape keys 1-2 become the beast's two attacks, your `@` takes its colours).
- **The bar stays six keys** in three groups under SKILLS, each with a small header: **1-2 your weapon's two skills**
  (they change with the weapon in hand, stamina), **3-5 three class skills** (chosen at rest as today, a dot in the
  school's colour), **6 one elite** (gold ☼; only one elite on the bar). The pair's name stands right of SKILLS.
- **Weapons:** each weapon kind gives two skills (a staff: Push Back and Focus; a bow: Aimed Shot and Volley) and
  each discipline **one rule that colours your class skills** (staff: spells cost less; sword: a blow takes a turn
  off your class cooldowns; axe and mace: damaging skills sometimes push; dagger: class skills crit more on a foe
  beside you; bow: areas placed further; spear: skills on a foe beside you reach 2 tiles; a shield lengthens
  defensive skills, a grimoire gives mana). Weapon rules never stack with an imbue blow. This replaces "eight tome
  skills per weapon discipline" in the weapons plan; weapons get no tree.
- **Guilds stay** (no new ones). Their techniques (three per guild at guild rank 1, 2, 4, plus eight for those who
  serve two guilds) no longer mix freely on the bar (settled 19 October 2026):
  - **Guild rank 4 is the guild's elite** (Inferno, Last Stand, Dawnbreak, Corpse Burst, Wind Step...); the
    two-guild techniques are elites too, only for who serves both (Spellblade for a spellsword: the imbue holds
    while mana lasts, each blow costs some, no other spells meanwhile). One elite on key 6. An elite may ask for a
    knot in a tree.
  - **Guild rank 1 and 2 become ordinary skills of their school** for keys 3-5, usable only when that school is one
    of your classes (Mage Armor is Frost).
  - **The weapon guilds** (Wardens: the bow; Still Hand: empty hands) teach weapon skills that may replace one of
    that weapon's two.
  - Anyone may join any guild and do its jobs and rise; a master with nothing for your classes says so.
  - Garrote and Smoke Bomb move to the Cunning school; Wild Shape moves to the Nature tree and the Green Moot's elite
    becomes a stronger shape (Elder Bear).
- **Pure is deeper, a pair is wider:** growing by use, one school reaches ranks 55 and 70 sooner; so a pure class
  gets only its pure rule, no extra elite.
- **Worked out** (approved 19 October 2026, numbers to be tuned by the balance test): the eight tomes of Cunning and
  Arcane, the Thieves' two new techniques (Cheap Shot, Blinding Powder), one rule per weapon family (unarmed: every
  third blow gives some mana or stamina; staves: spells 15% cheaper) and two skills for each of the 26 weapon kinds
  (the second at discipline rank 10; Burning Arrow goes), and the knots of all eleven trees (each school's "blade"
  branch opens with its imbue): project files `klassen/uitwerking.md`.
- **Balance test:** a new headless part where the bot fights the same set of monsters as a pure caster, a pure
  warrior, a spellsword and weapon plus class, and reports turns and damage taken; they should win about as fast,
  with a different risk.
- **The handbook:** a new chapter **"Who you become"** after "Your hero", written so a new player understands it
  without help: the blank start and the first tome, the second class at rank 20 and the pair's name, pure classes,
  the tree (points, rest, the temple), the bar's three groups, weapon skills and weapon rules, elites and guilds.
  "Fighting", "Your hero", "Guilds" and "All the keys" change with it. The build report quotes all of it.
- **Save data** changes (classes, tree points, new skills): bump `SAVE_VERSION`. Too big for one round: build in
  parts (classes and the bar, then trees, then the pair rules, Cunning and Arcane).

## The bestiary grows (built 23 October 2026; the spec)
Approved 22 October 2026 (from going through Project Gorgon's skills). No new skill: the bestiary that exists gets
deeper. What you know of a creature kind grows each time you kill or skin one. Three steps, each shown in the look
line (`l`) and on its bestiary page: first its weakness and resistances, then what it carries, then its weak spot
(a better chance of a critical hit against that kind). Reading about a creature in a library may give the first step.
Saved per hero: bump `SAVE_VERSION`; the handbook says it in a sentence or two.

## Debug menu and a test build (built 23 October 2026; the spec)

A tool for testing, not part of the game. Details: project files `debug/voorstel.md`. What each new thing needs to be
testable is listed in `docs/testing.md`.
- **Two downloads from every CI build.** The normal game for players, with no debug menu and no editor; and
  "Avarenthia (test)", with the debug menu switched on and the dungeon editor beside it, so Nilio can play it and share
  it with other testers. From the source, `--debug` turns the menu on as well. The normal download has no way to turn it on.
- **F12 opens it**, an overlay in the game's own look (letters to pick, Esc back). A debug run saves to its own
  `debug.sav`, so the one real save stays clean.
- **What is in it**, in this order of building: (1) three snapshot slots to save and load a moment again and again,
  and a bug-report key that writes a folder with a screenshot, the seed, the place, the turn, the last 200 log lines,
  the last keys pressed and the save; (2) the world: show the whole map, teleport to any place by kind or name, days or
  season ahead, choose the weather, spawn a creature by name, kill all in sight; the player: god mode, full health,
  coin, XP, skill ranks, give any item by name, identify all; (3) the rest: finish or make jobs, force events
  (pirates, a raid, a rival), set standing, add a hireling; sight off, a creature's AI state on look, coordinates and
  turn in the status line; pick the seed and skip the character making.
- **Not in the handbook**: it is a tool, not a rule of the game. The F12 screen shows its own keys.

## Ferries in villages (built 18 October 2026; the spec)

Niels, 17 October 2026: a village river is not always crossed by a bridge; it depends on how broad and wild the
river is and how big the road is.

- **Small river or stream:** a bridge, as now (one straight deck from bank to bank).
- **Broad or fast river, small road or lane:** a ferry instead. A flat raft (`▬` planks) on a rope across the water, a
  landing on each bank, a ferryman's hut on one side. Bump the ferryman (or step onto the raft): a few copper, and
  you are on the other bank; at night he is home and the raft is tied up. Farm fields across the water stay reachable.
- **Broad river, main road** (one of the two busiest roads into the place): always a bridge, stone in towns, because
  that fits the world.
- How broad and wild comes from the river on the world map (its size where it passes the place, and mountains or
  rapids upstream). The world-map ferries (`living.py`) stay as they are.
- UI: the raft and the ferryman are signs named in `guide.py`; no new key.

## The handbook (built 17 October 2026; the spec)

Approved by Nilio on 17 Oct 2026. The old `HelpScreen` (seven pages of key lines, partly stale) becomes **The
Adventurer's Handbook**. Mockups and every text: `/mnt/project-files/handleiding/` (`voorstel.md`, `teksten.md`,
`handbook_mockup.py`).

- **Where it shows:** `?` (and Esc, Game, Help) opens it as a modal. Contents on the left (18 chapters; the chosen one
  opens to show its sections), the page on the right: short plain sentences, gold headings, keys in `[ ]`, signs in
  their own colours, now and then a real piece of the map, a tip in the margin.
- **How it is controlled:** up and down pick a chapter, right (or Enter) goes into the page and up and down scroll it,
  left goes back, Esc closes. No new keys in play.
- **It opens where it fits:** in a fight at Fighting, in a town at Towns and people, at sea at Travel and sailing,
  for a new hero at First steps; while the game runs it remembers the page you read last (not saved).
- **Chapters:** First steps, Moving and looking, Fighting, Your hero, Gear, Towns and people, Jobs and money, The
  land, Weather and seasons, Travel and sailing, Camp food and rest, Your company, Guilds, Gods, Wild peoples, Death,
  Signs, All the keys.
- **From the data, so it cannot go stale:** peoples, gods, months, rarity colours, money, Signs (`guide.signs`) and All
  the keys (from `MenuScreen.GROUPS`). The texts live in their own file, `avarenthia/handbook.py`.
- **Tests:** every menu key appears in All the keys; every text fits (wrap, never cut).
- **Keys and signs look different:** a key is always written in square brackets in the text, `[e]`, and drawn as a
  gold keycap on a dark patch; a map sign never has brackets and stands free in its own colour ("tomes, the sign ≡").
- **The year is exact:** a table of the four seasons with their three months each (winter Longnight to Thawmoon,
  spring Seedwake to Blossomreign, summer Highsun to Goldfield, autumn Harvestmoon to Mistwane), from `calendar.py`.
- **Standing rule (in CLAUDE.md):** every change to the game updates the handbook in the same commit, and the build
  report quotes the new or changed handbook lines so Nilio can read them.

## The chronicle: what your hero knows (built 17-18 October 2026; the spec)

Approved by Nilio on 17 October 2026. Proposal and mockups: `/mnt/project-files/kennis/` (`voorstel.md`,
`1_chronicle_war.png`, `2_chronicle_old_days.png`, `chronicle_mockup.py`).

- **Two books, one screen.** The handbook (`?`) says how the game works and is the same for every hero. The chronicle
  (*Aldra's Chronicle*) says what this hero knows of this world. It uses the handbook's book screen: chapters with
  counts on the left, the page on the right.
- **Where:** the journal `e`, tab Lore, becomes its contents; Enter opens the book (as Enter opens the bestiary now).
  No new key. Enter on a page shows its place on the world map (a battlefield, a tomb, a seat), like following a job.
- **Chapters:** The Old Days, The Realms, Lords and houses, Peoples, Gods, Places, Wonders, Your deeds, Creatures (the
  bestiary), Signs.
- **Every fact has a source**, with a sign before it: `·` heard (may be wrong or old), `≡` read (a book or a stone),
  `☼` seen (you were there); under it, small: from whom, where, which day.
- **Rumours can prove false.** When you later see or read better, a red line goes under the old one ("Not so: you saw
  King Oswin ride through Kelmarch on day 30"). Heard news comes through `news.py` as it does now: late, sometimes wrong.
- **Gaps are named** without giving the answer: "Who leads Hale's army, you have not heard. The scribes of Hale would
  know." A dot marks what you have not read yet; one gold log line: "Your chronicle grows: The War of the Ford."
- **Where knowledge comes from:** talk (the `lore.py` lines and the news, now kept as heard); what you see yourself
  (battlefields, lords you meet, a town that falls, named enemies you kill: Your deeds, also for the death screen);
  inscribed stones in ruins (bump one: a line of the old days; Varnish letters must be learnt in a library first,
  until then "Old letters you cannot read"); rare old books in dungeons (a few per world; read them, or sell them to
  a library for some coin); libraries.
- **Libraries:** only in cities, plus the dwarves' own (the Grudge Book of a hold) and the elves' (the hall of songs
  under the Elder Tree). A building with shelves and a scribe; bump the scribe for a choice: The old days, The realms,
  A lord or house, This city, Varnish letters. Costs a few hours and a few silver per subject, a day for something
  big; members of the mages' guild read for free. A library is true but slow: the past and its own realm are right,
  far news is old or missing.
- **Why it matters in play:** leads (a book names a tomb, a lost battlefield or an old road of the Empire, and the
  place goes on your map); Varnish letters open the stones, which point to the old ways (`hidden.py`); when a job
  asks you to take a side, you see what you know of that lord; a dwarf whose grudge you know talks differently to you.
- **History up to now:** the myth in `lore.py` stays the start. Making the world also works out a short history of the
  last ~200 years, 30-60 events (kings, marriages, wars, fallen houses, founded towns), each tied to a place on the map
  (battlefields from `living.py`, ruins, seats). After the start the realms engine writes on.
- **Cut:** the realms layer does not show borders "as you know them"; it shows the borders as they are.
- **Order:** 1. the handbook (it builds the book screen). 2. Chronicle part 1, small: the book in the Lore tab,
  sources, heard and seen facts, Your deeds, the old myth, stones and old books; works without kingdoms.
  3. Chronicle part 2, with the realms round: the made history, libraries, false rumours of lords and wars, leads.
- **Save:** a list of facts (id, source, day, true or proven false). Bump `SAVE_VERSION`.

## Place names (built 18 October 2026; the spec)

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

## Nature and wonders (built 18 October 2026; the spec)

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

## Herds, hunting and the crafts (built 18 October 2026; the spec)

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

## Walking the land: zones (built 18 October 2026; the spec)

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

## Realms, lords and wars (built 18 October 2026; the spec)

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

## Stamina for martial skills (built 18 October 2026; the spec)

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

## Magic schools with a character of their own (built 18 October 2026; the spec)

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

## Places on their own land, part 2 (built 24 October 2026; the spec)
- **Underground kinds get their own plan too** (`ondergronds.md`): whoever made the place decides its shape (water, beasts, ants, goblins, dwarves, people); rooms by use (a goblin delve has a market hall, forge, family halls, cells, the chief's hall); tunnels at least 3 wide, main ones 4, well connected with a loop; inhabitants placed where they belong, fewer than now; two ways down where it fits. Goblins are a clever people: their delve is cut into the back wall of their ravine, not a cave. Cells have bars only as their front, between stone walls. Bridges no longer use ═ (the built wall). Mockups E2 and F.
- **Abbeys (approved 22 October)**: a middle place, 100 x 60, on its own land: a place apart where the devout live, learn and keep lore. Each people has its own, under its own name, with levels up (<) and down (>). Mockup `AP_abbeys_peoples.png` (style sketch).
  - **Human, the Abbey:** a church on the north side, a cloister walk round a garth with a well, a chapter house, refectory, kitchen and infirmary. Up: the dormitory and the scriptorium with books (ties to the libraries of `history.py`). Down: the wine cellar and the bone house.
  - **Elf, the Starhaven:** a ring of great trees round a star garden of white stone; sleeping halls in the crowns; a still pool that mirrors the stars; an archive of song-scrolls in a hollow trunk.
  - **Dwarf, the Rune Hall:** a hall of rune stones where the lore is carved, a forge chapel, a brewery, the brothers' cells; store halls and the deep archive below.
  - **Halfling, the Harvest House:** a round hall with the long table, a bakery and a brewhouse, vegetable gardens, an orchard and beehives inside a hedge; pantry cellars below.
  - **Gnome, the Lantern House:** round rooms under the roots, lit by crystals: a star dome with a lens, a library, an alchemy room, sleeping nooks; the deep workshop below.
  - **Orc, the Spirit Lodge:** where shamans train the young: a sweat lodge, the young warriors' hut, a ring of trial stones round the spirit pole, drums; the spirit cave below.
  - **Goblin, the Scroll Warren:** a cave of stolen books and scrolls in heaps round a junk idol, a map room, an ink pit, reading nooks; the vault of secrets below.
  - **Kobold, the Gleam House:** a mirror hall and a sorting hall where coins, gems and metal are sorted and polished; the deep hoard below.
  - **Gnoll, the Bone Kraal:** where bone-callers learn: the howl rock with its moon stone, the bone-caller's hut, hide racks, a bone heap, a carrion pit; the bone tunnels below.
  - **Lizardfolk, the Hatchery:** reed huts on stilts joined by walkways round the sacred eggs in warm mud; the priests' hut and the sun stone; the drowned halls below.
  - **Friendly or not** by standing, as with temples and towers.
- **Forts (approved 22 October)**: a middle place, 100 x 60 (a border fort large), built to hold ground. Each people has its own, under its own name; its way in is its one telling thing. Below lie 3 to 5 levels of cells, stores or older dungeon. Mockup `FP_forts_peoples.png` (style sketch). Only the goblin hole and the goblin village get no version per people; they are goblin kinds already.
  - **Human, the Keep:** a moat and a drawbridge, a gatehouse with a portcullis that drops on alarm, four corner towers (tower rules; shoot over the wall from the wall walk), a yard with a well, barracks, stable, armoury and the lord's keep. Below: the dungeon, a place for rescue jobs.
  - **Elf, the Thornwatch:** a ring of thorn grown as a wall, a gate of woven living branches, guard trees with archers' platforms, the captain's stone; root cellars below.
  - **Dwarf, the Gatehold:** a wall across a gorge with the gate in the rock, murder holes over the road, bolt throwers in the cliff, barracks and a forge; the battlements up, the halls down.
  - **Halfling, the Hedge Post:** a small watch house in a thick hedge, a bell to raise the hamlets, a lookout loft; the root cellar.
  - **Gnome, the Hidden Hill:** a hill that looks empty through an illusion crystal; peep holes all round, traps on every way in; the deep burrows below.
  - **Orc, the Stockade:** a palisade behind a ditch of stakes, gate towers, the warlord's seat, sleeping rows, a weapon heap, a warg pen; the pits below.
  - **Goblin, the Scrap Fort:** a ring of scrap, carts and planks, a gong tower, catapults of junk, spiked pits at the gate; tunnels below.
  - **Kobold, the Trap Gate:** one long tunnel in, trapped every few steps, spy holes from side tunnels, a ceiling ready to drop; the warrens below.
  - **Gnoll, the War Boma:** two rings of thorn, lookout platforms on poles, the packlord's bones, hyenas inside; the dug den below.
  - **Lizardfolk, the Stilt Bastion:** a reed fort on stilts in deep water, reached by one plank walkway they pull in when warned; the flooded cellars below.
  - **Who holds it:** its own people (access by standing), or it is taken, abandoned or a ruin.
- **Manors (approved 22 October)**: a small place, 80 x 50: the house of someone who matters. Each people has its own, under its own name. Letters and ledgers in it can point to a job; the one telling thing says who lives there. Mockup `MP_manors_peoples.png` (style sketch); the human one is mockup D.
  - **Human, the Manor:** the great hall with the portrait over the hearth, kitchen and store with a back door to the well and the kitchen garden, a chapel, a dining room, a garden wall and a lane to the road. Up: bedrooms and the study. Down: the wine cellar, sometimes with a secret way out.
  - **Elf, the Bower:** a house grown round four trunks, rooms of living wood joined by bridges (the hall of songs, the study, the bedroom), a moon garden on the ground; the root cellar.
  - **Dwarf, the Clan House:** behind a carved door, the hearth hall with the ancestor wall, a brew room, the treasury, sleeping rooms; the clan vault below.
  - **Halfling, the Hill Hall:** a big home dug into a green hill behind a round door: the parlour, pantries full of jars, a study, bedrooms, flower gardens; the deep pantry.
  - **Gnome, the Cap House:** a house in a giant mushroom with a stair up its stem: a workshop, a study, a potion room, a bedroom; the root workshop.
  - **Orc, the Longhouse:** the chief's long hall, fires down the middle, sleeping benches along the walls, the chief's seat at the end, a skull pole at the door, a warg yard; the store pit.
  - **Goblin, the Counting House:** a trader-boss's house in the rock: the counting room with ledgers, a locked strongroom, a store of stolen goods; the smugglers' tunnel.
  - **Kobold, the Hoard Burrow:** the hoardmaster sleeps on his coin; side holes for gems, a mirror, a polishing bench; the deep hoard.
  - **Gnoll, the Great Tent:** the packlord's great tent of hides in a thorn ring, his seat of bones, his share of the kill, hyenas at the door; the den below.
  - **Lizardfolk, the Sun House:** the elder's house on stilts with a window to the sun, an egg of the line, a fish pen; the mud cellar.
- **Goblin places (approved 22 October)**:
  - **An ordinary goblin hole** (small, 80 x 50; mockup `E3_goblin_hole.png`): a hole in a slope with a lookout and the alarm gong by the way in (silence the watch and the hole sleeps on); rough passages braced with beams; tripwires and a covered pit; a sleeping den with straw, a cook den, a loot corner with what they took from the road, the leader's nook; a narrow back way out where they flee. Short and sharp: one level, sometimes two.
  - **The goblin village** (large, 120 x 70, built like a settlement; mockup `E2b_goblin_village.png`): cut into the back wall of their ravine, the ravine as the square, a gate with the goblin tower; a main gallery 4 wide; the market hall with pillars, the forge, family halls with hearths, the cell block (barred fronts between stone walls), wolf pens (a keepers' aisle with room to stand, pens cut into the rock, a barred front with a door on each), a shrine, the chief's hall at the back with the treasury, a loop round the back. Two levels: the village, and the mine and deep halls below. Traders, children and non-fighters who flee; the warn-then-rouse rule of `tribes.py`; captives for a rescue job. The chief's throne decides whether the village goes with you or against you.

## Places on their own land, part 1 (built 24 October 2026; the spec)
- **Towers (approved 22 October)**: slender and high. Mockups `T_tower.png`, `T_towers_peoples.png` and `T_towers_peoples2.png`.
  - **Floors.** Every floor is the same small footprint, about 15 across, and has 3 to 6 storeys. A floor may be split into rooms. Each floor has its own use: a guard room, a store, the keeper's room. There is no room for hordes, only for a few strong foes, and the stair is the choke point.
  - **Stairs.** A stair or ladder comes out at the same spot it left from below. The next one up lies elsewhere on that floor; in a stone tower it is a quarter turn further along the wall, like a spiral stair.
  - **Below.** A cellar or dungeon may lie underneath, reached through a hatch.
  - **The top is a lookout.** Standing there marks the land around on the world map, the way the great falls' cairn does. The radius grows with the tower's height: about 10 for a low tower and 14 for a high one, with 4 more on a hill. Fog or rain halves it. At night you see only lights: villages, campfires and ships. In a manned tower, a watch at the top sees you coming from afar and raises the alarm sooner.
  - **Up high you see it.** Mockup `T_tower_height.png`.
    - Round the top platform, the ground map below is drawn faded in a blue-grey haze; the higher the tower, the paler.
    - The tower casts its shadow across the land.
    - Birds (v) wheel below you, and now and then a wisp of cloud (░) drifts past, using the small animations.
    - Lower floors show the same through an arrow slit when you stand next to one.
    - A message line: "The wind tugs at your cloak. The land lies small below."
    - The land shown is the real map below, so it matches where you walk out again.
  - **Not every tower is hostile.** Human, elf and dwarf towers are manned by their own people.
    - Whether you may climb up depends on your standing with that people or its lord. With good standing, the keeper lets you up to the lookout.
    - Otherwise the guard on the stair turns you away, and forcing your way up is a crime.
    - The towers of the hostile peoples you fight your way up.
  - **Fallen towers and ruins.** Mockup `T_tower_ruins.png`.
    - **Half fallen:** one side came down. Its stones lie in a heap round the foot of the tower, and a few fell in through the roof. Higher up, half of each floor is gone, and you stand at a broken edge.
    - **What you see below** is always the real level underneath, faded in the haze: through a gap or over an edge you see the ground floor with its rubble.
    - **A true ruin:** only a stump of wall stands, with ivy on it, and rubble and grass inside. The stair ends at a last broken ledge, and the cellar hatch still leads down.
    - **Who lives there:** no people keeps a fallen tower, but bandits, a nesting beast or something in the cellar may.
    - **Edges and falls** (the same for a hole in a floor, as in a goblin tower): stepping off first asks, with a warning of how far down it is; you never fall by one careless key. A monster that knocks you back can throw you over the edge, though, and the same works the other way: a shove or a knockback of yours sends a foe over the edge and down. A fall hurts by the number of floors, and you land at the same spot on the level below.
  - **Each people builds its own tower:**
    - **Human:** grey stone, round, with rooms behind doors. On top, battlements and a brazier.
    - **Elf:** white stone in thin lines, built round a living trunk that the stair winds about. The top is open to the stars, with a crown of leaves.
    - **Dwarf:** hewn blocks, square with cut corners, and runes in the wall; a forge and a store. On top, a bolt thrower and a beacon.
    - **Orc:** rough logs, square, with ladders instead of stairs, and skulls. On top, a hide roof and a war drum.
    - **Goblin:** crooked, of scrap and planks, with holes in the floor that drop you to the floor below. On top, a crow's nest with a gong.
    - **Kobold:** a narrow spire of piled stone with shiny bits set in the walls, ladders, and a hoard room. On top, a polished shield that flashes a warning.
    - **Gnoll:** poles and hides lashed together, taken down when the pack moves on, with bones lying about. On top, an open platform and a bone horn.
    - **Lizardfolk:** woven reeds on stilts over the swamp, with an egg nest. On top, a smoke fire that signals over the reeds.
    - **Halflings and gnomes** build no towers.
- **Temples (approved 22 October)**: a middle place, 100 x 60, on its own land. Mockups `C_temple_on_its_land.png`, `TF_1`-`TF_4` (every level of a human temple), `TP_temples_peoples.png` (style sketch) and `TP_full_elf.png`, `TP_full_orc.png`, `TP_full_gnoll.png` (true size).
  - **Below every temple** lies its own deep place, 3 to 5 levels: older and rougher the deeper you go.
  - **The bell tower is a chance.** Not every human temple has one; when it does, it follows the tower rules and its top is a lookout.
  - **The ancient bottom is a chance too, and hidden.** Some temples were built over something older (a cave, a ring of standing stones, what guards it). The way in is walled up or under a loose flagstone; a job or a rumour leads you to it, in the spirit of the old ways (`hidden.py`).
  - **Each people its own temple:**
    - **Human:** a nave with pews and pillars, a transept with chapels, the altar; maybe a bell tower. Below: the priests' crypt, then old catacombs.
    - **Elf:** no walls and no roof: glades in the old wood, the living trees as walls, linked by paths of white stone. The great glade holds the moonwell; round it the hall of songs, the healers' grove, the grove of the fallen; the eldest tree has a stair up to a lookout in its crown. Below: the root halls.
    - **Dwarf:** the hall of the forefathers cut in the rock, ancestors in stone, a forge altar. Below: the tombs of the forefathers.
    - **Halfling:** a round hearth chapel with a harvest altar, a garden inside a hedge.
    - **Gnome:** a hollow under the roots, a ring of glowing mushrooms round a crystal.
    - **Orc:** a palisade ring open to the sky, the ring of blood with the skull pole and blood pit in the middle; the warchief's long hall, the shaman's hut, a trophy hut, a cage of captives, a warg pen. Below: the cave of the war god, cells at the top, a blood altar at the bottom.
    - **Goblin:** a cave nook with an idol made of junk and heaps of offerings.
    - **Kobold:** a shrine to shine: a hoard of coins, a polished mirror, candles.
    - **Gnoll:** a camp on the plain in a hedge of thorn bush, a ring of bone poles round an altar of skulls, a moon stone; hide tents, a feeding pit, a hyena pen. Below: the burrows, down to the bone pit of the bone-caller.
    - **Lizardfolk:** a stepped mound in the swamp, stairs on four sides, the egg altar on top.
  - **Friendly or not** by standing, as with towers: how far in you may walk depends on your name with that people.
- **Barrows (approved 22 October)**: a small place, 80 x 50: the grave of someone great. Each people has its own, under its own name. Narrow and low: fights in passages, not hordes. The bier is the telling thing: take from it and the dead wake (an event). Sometimes an older grave lies below. Mockup `BP_barrows_peoples.png` (style sketch).
  - **Human, the Barrow:** a mound in a ring of standing stones, its stone door half sunk; inside a long passage lined with stones, an antechamber of grave goods, side rooms of bone niches, the hill king on his bier.
  - **Elf, the Root Tomb:** under a dead great tree the elves lie in cradles of root; a sapling grows from the eldest's breast; starlight lamps.
  - **Dwarf, the Sealed Vault:** behind a sealed door of runes, a hall of stone kings with rune traps, treasure rooms, the lord in his armour.
  - **Halfling, the Resting Hill:** a family tomb in a small hill behind a round door, flowers laid every year; quiet, seldom anything worse than a grieving ghost.
  - **Gnome, the Crystal Crypt:** the dead sealed in crystal round the great inventor, the book of their works, clever traps on the way in.
  - **Orc, the Bone Cairn:** a warlord under a cairn of piled stones, his slain wargs and weapons round him, skull poles on the way in.
  - **Goblin, the Trapped Tomb:** a zigzag way with a trap at every turn, to a boss buried with what he stole; a false tomb and a real one.
  - **Kobold, the Hoard Tomb:** the old hoardmaster buried in his coin; take some and the loose floor gives way into the old shaft.
  - **Gnoll, the Bone Hill:** a hill of the bones of every kill heaped over a great packlord; the bone-callers wake what lies below.
  - **Lizardfolk, the Drowned Tomb:** stone coffins sunk in a sacred pool round an island with a stone egg; wade or dive; the drowned halls below.
