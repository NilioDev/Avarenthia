# Built: what is in the game

Moved out of `docs/plan.md` so the plan stays short. Read a section here only when a round touches it. The full
specs of rounds 1-4 are in the git history of `docs/plan.md` (before 16 October 2026, 23:00).

## At a glance

| Status | What |
|---|---|
| **Built** | Rounds 1-5 (monsters and behaviours, named enemies, five guilds, the jobs, seasons and sailing); world shapes; the peoples' own lands; hostile camps; dwarf holds and mines; the bigger world with nine new biomes; small animations on the maps |
| **Built: nature and wonders** | Waterfalls, cascades, great falls and rapids; hot springs, the tidal causeway, the Frozen Stair; the Drifting Isles, the Starwater, the Thunder Anvil and eleven more wonders, each a site with its own saved map; trolls turn to stone in the sun |
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
| **Built: the Varnish (25 Oct)** | Ruined Varnish cities found only by walking their zones, the Sky Court and a hidden deep below with a guardian of its own; the Northern Wall and its towers, wind towers, the road of the standing dead, a star-iron forge, Gates of Leagues, a sluice hall, the fallen sky, star houses, a sunken harbour; league stones; the chapter The Varnish, eight books in pieces bound by a scribe, and five riddles in The Old Days that point to five deep places |
| **Built: old places from the history (24 Oct)** | The made history lies on the land: old battlefields where the dead walk on the battle's night, villages emptied by plague, war or a dragon, broken bridges of the old Empire, stones of names, the fallen emperor, gallows hills, quarries, wrecks at low tide, hermits, leper colonies; and the peoples' small marks |
| **Built: the Rift and the Ashen Deep (24 Oct)** | A rift opens now and then as a world event (or under a deep dungeon's bottom), the land round it burns to ash, fiends raid at night; three to five levels of basalt, fire, chains, vents, bone fields and cages; seven new creatures; the Lord of Cinders before the burning gate; break it and the rift closes |
| **Built: the northern lights' gift (24 Oct)** | Under the lights rune stones glow and show an old way, Frost and Storm cost less, the spirits of the northern barrows rise and give errands, and wake angry if you dig in or rob them; the ghostly glow blue-green, fiends red. The light-feast comes with the feast days |
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
  page). Test `varnish`. SAVE_VERSION 43. Not as asked: no archaeology yet (round 16), so the pieces come from stones,
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
  Test `aurora`. SAVE_VERSION 40. Not as asked: the light-feast moved to the feast days (round 20, as the build
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
