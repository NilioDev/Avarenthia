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

