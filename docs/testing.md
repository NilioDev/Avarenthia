# Testing: what each new thing needs

What Nilio wants to be able to try in the test build ("Avarenthia (test)", F12 debug menu, see "Debug menu and a test
build" in `plan.md`) for each new thing, so he does not have to play for weeks to reach it. The Tests page in F12 (T) shows every line of a built thing and sets
it up with one key; its setup is a recipe in `avarenthia/debug_tests.py`, keyed by the heading and the line's name
(the bold words, or the first words). A new line needs a recipe there once its thing is built (test part
`debug_tests`); a heading of a thing not built yet stands in `debug_tests.NOT_BUILT`. When a round is built, its lines stay here as long as they are useful for testing.
Each line: **what** - what to check - what the debug menu should offer.

A tick (✓ or ✗) lasts across builds. When a later round changes a thing, Claude puts a line `Changed: <date>` under
its heading (e.g. `Changed: 13 November 2026`); a tick older than that date shows dim and counts as open again. On the
page, `u` shows the open lines (never ticked, ✗, or changed since), `x` only the ✗ lines with their whole notes, and
each heading shows its count, "3/5 ✓ 1 ✗".

## Classes (built 23 October 2026)

- **First class** - read a class tome while blank: the question, the name, the tip, the chronicle line. Debug: give a
  tome of any school (Give item).
- **Second class** - at rank 20 a tome of another school asks; the pair name shows beside SKILLS. Debug: set the
  rank of your class to 20 (Ranks), give a tome of another school.
- **Trees** - points per 5 ranks, spending only where you rested, every knot, the imbues, the shapes, the temple
  taking points back. Debug: set the school's rank (Ranks), "Rested here", give coin.
- **Weapon skills** - every weapon kind's two skills on keys 1-2, the second at rank 10, with their effects. Debug:
  give the weapon, set its discipline to 10.
- **Cunning and Arcane** - their 8 tomes each, the tiles they lay (snare, caltrops, rune, gate, smoke), the first
  blow on a foe that does not see you, sneaking. Debug: give their tomes, set the rank (Ranks), spawn a sleeping foe.
- **Pair and pure rules** - each of the 66 names' rule, shown on the tree page. Debug: give two tomes, rank 20.
- **Elites and weapon-guild skills** - a guild master's techniques on key 6, a lesser one of your school on 3-5, a
  weapon guild's on 1 or 2 with its weapon in hand; a master refusing a technique you could not use. Debug: Guild
  rank (q), Coin.
- **Epics** (built 29 October 2026) - each of the 22 on key 6, once per rest, ready/spent on the panel; Phoenix
  instead of a death, its flames and how they go out; the teachers' huts, a rumour from rank 35, each deed to its
  end, the swap. Debug: "Epics: rank 40, teachers, deeds" (E), Teleport to the hut, "Rested here", Weather (a storm
  for the bell), Time (a winter night).


## Cities that grew, part 1 (built 30 October 2026)

- **The heart** - a cathedral city, a king's or baron's burgh, the emperor's palace in the great city, each on its
  market. Debug: Teleport (kind city, metropolis).
- **Streets, lanes, rows, the wall** - main streets winding to the gates, a gate where each road comes in, the ring
  street, blind lanes, houses in rows inside the wall, the moat with a stone bridge at each gate. Debug: Teleport to
  a city, Reveal map.
- **The river and its bridges** - quay walls, only the great ways and the ring street cross, statues on the market
  bridge. Debug: Teleport to a city on a river.
- **Canal and fortress towns** - a flat harbour city in canal rings round the Dam; a city in a march with bastions.
  Debug: Teleport to a harbour city, to a city in a march.
- **Who lives where** - guild halls by the market, the secret ones down a lane, inns by the gates, the watch by the
  wall; the lamplighters at dusk. Debug: Teleport, Time (dusk).

## Cities that grew, part 2 (built 30 October 2026)

- **Dwarf cities** - the terraces under the gate of the hold, the Great Stair and its steps, the forge square, the
  cart line, the lord in the hall of the gate. Debug: Teleport (a dwarf city, kind city or metropolis).
- **Halfling towns** - the hedge ring, the green with the party tree, the Keepsake Hall, hill homes, the pond.
  Debug: Teleport to a halfling town.
- **Half-orc towns** - palisade and stakes, the chief's longhouse and the pit, rings of huts. Debug: Teleport (the
  outer towns).
- **Bridges on the land** - each people's look where a road crosses a river; a human bridge with a fallen span and
  its ford. Debug: Teleport near a river crossing, then [>] into the land.

## Feast days (built 30 October 2026)

- **Each feast where it is kept** - the name under the map, the square dressed, the figure, its one or two things
  to do, the folk in the square at evening, the prices. Debug: Time (to the feast's date), Teleport to a town that
  keeps it (the handbook's table says who).
- **The mask, the boot, the Light-Feast** - wanted in a town, enter it masked in the Masking; the boot on
  Wanderer's Eve and the morning after; a northern village on 1 Leaffall. Debug: Time, Teleport, standing.
- **The Fair of Skell** - a human city's own week: travellers all week, better selling, pickpockets. Debug: Time
  (days ahead) until the fair is in a city.

## Round 6: livelier settlements (built 30 October 2026)

- **Work you can see** - woodpiles by the houses and the fields through the year. Debug: Teleport to a village or
  city, Time (month).
- **Market day** - travelling traders with stalls in the square, gone at five. Debug: Time (to a Starsday, 9).
- **The mood** - fear (guards at the gates, doors shut) and the feast after a war won. Debug: Force an event (a war
  party of the raiders), then Teleport to the town near it.
- **Happenings** - the brawl, the pig, the funeral, the pickpocket. Debug: Force an event, "Something happens in
  this town".
- **Each people's day** - halfling meals and hedge lanterns, elves at night and the archers at the butts, shy gnomes,
  the dwarves' shift bell, orcs sparring, goblins squabbling, the kobolds' hoard, slow lizardfolk at night.
  Debug: Teleport, Time.
- **The poor quarter and shanty camps** - beggars, the night trader buying black lotus. Debug: Teleport to a human
  city; Force an event, "Five black lotus in your cargo"; Time (night).
- **Refugees** - in the cities near a waking servant: a silver, their tale, a lieutenant marked. Debug: the Shadow
  menu (wake a servant).

## Trade part 3: caravans (built 30 October 2026)

- **Your wagons** - buying a wagon with a mule or an ox at the stables (needs the cart), the string of ♦ on the map,
  the stables in town, waiting outside a dungeon. Debug: Force an event, "Three wagons of your own join you"; coin.
- **The road** - slower off the road, no fords or swamps, the beasts eating grain, a broken wheel, spring mud, the
  wages. Debug: Time (days ahead, spring).
- **Raids and the land** - the toll or the fight among the wagons, the ring at night, walking into the lead wagon
  (mend, pay, camp, leave, take). Debug: "Robbers fall on your wagons" on the world map, then [>].
- **The NPC caravans** - walking along, trading on the road, the League racer, robbing one. Debug: "A League
  caravan races you" in a town.

## Boss fights part C: the boss maker (built 30 October 2026)

- **Job bosses** - "A price on a head" on a town board or from the captain, the rumour in the job, the fight with
  its rhythm, phases and traits (a twin, wounds that close); a nest, shrine, boats, missing or deserter job ends in
  a boss. Debug: Jobs (make one), Teleport, Level.
- **The end of it** - a man or woman who yields (kill, let go, hand over), a beast's parts, the chronicle line.
- **Fixed bosses** - the line on the floor above, the thing on the boss's floor, carried into the fight. Debug:
  Teleport to a dungeon with a boss, its depth.


## Trade part 2: goods and ways (built 30 October 2026)

- **Named goods and master works** - the market list's * goods at their maker and far away, the note at the foot,
  a bad or famous year (news at the new year), a city's board asking for a master work. Debug: Gold, Teleport to a
  town, Time (to the new year).
- **Far goods, barter, monster goods** - silk in a harbour city; barter at a kobold or orc trader and with an elven
  elder; beast parts sold to a city herbalist. Debug: Teleport, Give item (parts), Gold.
- **Spoiling, need, war, contraband** - fruit going off with and without salt; a snowed-in village or a besieged
  city; arms dear in a war and sold to both sides; black lotus from a swamp town, the Watch at a gate (try with a
  Cunning hero), the cove's fence. Debug: Time (winter), Teleport, the Realms section (a war).
- **News and the League** - a carter at the inn, the factor's "Your standing with the League", better prices with
  rank. Debug: Gold.


## Archaeology (built 30 October 2026)

- **Dig spots** - at an old battlefield, a deserted village or a Varnish place: no spot without a trowel or rank,
  more spots as the rank grows, all of them at 50; dug spots stay dug when you come back. Debug: Give item (Digger's
  Trowel), Ranks (Archaeology), Teleport to an old place or a Varnish place.
- **What the earth gives** - breaking a find (try a pick), a riddle piece at the Varnish, the battle or the village
  in the chronicle, a servant's weakness from rank 20, old pieces, star-iron, coins and finds; a city library buying
  them. Debug: the flag "Old finds" (nothing breaks), Ranks, the Shadow section (a known servant).
- **Mending old pieces** - at an anvil, Smithing of the piece's tier, a shard of star-iron for Varnish work.
  Debug: Give item (old pieces, a shard of star-iron), Ranks (Smithing).


## Life skills part 2 (built 30 October 2026)

- **Parts and powers** - skinning parts of every beast, the ladder (wolf, winter wolf, sabretooth fangs), chitin from
  spiders, a part broken off a bear below half life by a critical blow; choosing a part when you make a piece, two
  from rank 40, which parts fit which pieces. Debug: Give item (parts, leather, bars), Ranks, Spawn (a bear).
- **Named beasts** - their own parts at Skinning 15/30/45 and the piece named after them; the den, found by walking
  up to it or at Hunting 50 on a track, the beast at home after it fled; the den gone when it dies. Debug: Give item
  (named parts), Ranks (Skinning, Hunting), the named enemies in the World section, Teleport.
- **Catching alive** - a lord's "alive" job, a sleeping flask, a rope, the furious waking, the cage in his yard.
  Debug: Give item (rope, herbs for a flask), Ranks (Alchemy), Teleport to the seat.
- **Unmake and mending** - Unmake at 40, 45 and 50 (the chance, the two thirds, a failure), mending yours and your
  hireling's at the anvil and the bench, on the road from 30, for the townsfolk. Debug: Give item (magic gear),
  Ranks.
- **Masters** - the test at 25 and 40 and its job, an order on a board, every perk at 30, 40 and 50 (ice fishing in
  winter, a storm, veins through a wall, a cave-in, a feast); the three great masters heard of at an inn or a tanner,
  their three-part test, the won-back workshop, Unmake for gold once a visit. Debug: Ranks (a rank set past 25 or 40
  counts the test as passed), Give item (Fey Silk, star-iron, drake leather), Time (winter), Weather (a storm).
- **The road** - marsh, sand, snow and mountain boots on their land, a bedroll at camp, barding on your beast.
  Debug: Give item (leather), Ranks (Leatherworking), Teleport to a marsh or desert.

## Life skills part 1 (built 30 October 2026)

- **The curve and the colours** - a craft list's names in grey, green, yellow and orange; grey work teaching nothing,
  the first make or catch double; a rat teaching a sword little at level 20. Debug: Ranks (life skills and
  disciplines), Give item.
- **Herbs and alchemy** - the herbs of each land and tier, "too hard for you yet", tasting for the first property,
  the second at Foraging 15, `?` in the [P] list; two or three herbs, a ruined brew, three on one property, an oil on
  the blade, a sleeping flask thrown, Starmoss alone (once only), a tincture on spirits. Debug: Give item (plants,
  the spirits), Ranks (Foraging, Alchemy), Teleport to a land, Time (night, winter).
- **Brewing** - the ten drinks with their ranks, tasting one to learn it, an innkeeper of that people telling it, a
  barrel at 30, a round for the company at a fire, the gift at a people's inn, tipsy after three cups, a drink sold
  far away. Debug: Give item (food: the drinks, honey, barley, apples), Ranks (Brewing), Teleport.
- **Fish by tier** - fresh and salt fish apart, a big fish snapping the line, grayling, sturgeon, ice char, the
  thunderfin in a storm, the net, the hooks. Debug: Ranks (Fishing), Teleport, Weather (a storm), Time (night).
- **Smithing and Tailoring** - veins of each metal by land and depth, smelting, forging every piece and tool, the
  grade and property per material, crude/fine/masterwork, mending and honing; cloth from the outfitters, spiders, a
  mammoth, Fey Silk at night by the wisps; warm or cool pieces in the cold and the heat; leather by its beast; a herd
  too wary for you yet. Debug: Give item (ore, bars, cloth, leather), Ranks, Teleport, Spawn (spiders).

## The K5 maker (built 24 October 2026)

- **Theme rooms** - each of the 43 rooms, its mood line, its telling thing (pray, search, drink, the vault and its key,
  the plinths, the circle's waves, the gong guard, cells, the mirror, the lever, the arch, the falling floor...).
  Debug: "Theme room or river" (z) makes a level round the room you pick and puts you at its door.
- **Arrival and bottom rooms** - the dead camp and the chapel by the stairs up, the throne, treasury and lair with
  the boss. Debug: the same list (z).
- **Rivers underground** - water: swimming, the question with heavy armour or pack, swimmers that follow; fire: the
  question, the burn, shoving a foe in; the crossings. Debug: "a river of water" or "a river of fire" (z).
- **Rock you can see, mood lines of plain rooms, sizes** - walk any classic dungeon. Debug: Teleport to a dungeon.
- **Rooms of a people** (built 5 November 2026) - the dwarf shrine, goblin library, orc war shrine, elven bower and
  halfling pantry, met in a dungeon near that people. Debug: the recipe makes a level round the next one (Enter again).
- **The way in** (built 5 November 2026) - a goblin totem, a crypt's mourners, web over a spider's cave, the line it
  says. Debug: the recipe stands you on the first level of the next kind (Enter again).

## Places on their own land, part 1 (built 24 October 2026)

- **Temples of every people** - the walk in, the warden who stops a stranger, pushing past (a crime), the altar, each
  people's telling things (bell, gong, moonwell, idol, blood pit...), the deep place below. Debug: Teleport (temple
  and its people); Standing (f) to be a friend or a stranger.
- **The older bottom** - the tale, the loose flagstone on the last level, the ring of stones and the Old Warden.
  Debug: "Hear the tale of an older place" (O), then Teleport to a temple marked "older below".
- **Towers** - every people's floors, the stair a quarter turn on, the haze and shadow below, a slit on lower floors
  (never in a corner), rain and snow falling round every floor and on the open top, the lookout on top by day and by
  night, in fog. Debug: Teleport (tower and its people), Time, Weather.
- **Fallen towers, edges and falls** - half fallen and ruin, the question at an edge, a fall by floors, a foe thrown
  over by a shove. Debug: Teleport (tower, half or ruin); Spawn a creature beside an edge.
- **Barrows** - each people's barrow, its twist (false tomb, hidden door, the kobolds' floor, the pool), the bier and
  its king. Debug: Teleport (barrow and its people).

## Places on their own land, part 2 (built 24 October 2026)

- **Abbeys, forts and manors of every people** - the walk in, how far a stranger gets, the floor above where there
  is one, the cellars below, each telling thing (shelves, rune stones, the pool and the lens, the goblins' map room,
  the long table, letters, the portrait or seat). Debug: Teleport (abbey, fort or manor and its people); Standing (f).
- **Who holds a fort** - its people, bandits, nobody, a ruin; the portcullis that drops when the bandits see you, the
  postern; the lizardfolk's walkway pulled in. Debug: "Change who holds this fort" (F) on the fort's land.
- **The ways in** - the kobolds' trapped tunnel and falling ceiling, the gnomes' hidden door, the elves' woven gate
  (stranger only), the dwarves' murder holes. Debug: Standing (f) to be a stranger, then Teleport.
- **Underground kinds** - every kind's rooms and folk, the goblin hole's watch and gong, tripwires and the covered
  pit, the back way out; smashing a nest's eggs. Debug: Teleport (dungeon), Spawn.
- **The goblin village** - the carved gate at the end of the ravine, the village, the deep halls, the chief's high
  seat, rousing in sync. Debug: Teleport (ravine).

## The northern lights' gift (built 24 October 2026)

- **Rune stones and milestones** - a rune stone unseen by day, found under the lights, glowing on the map; bumped, its
  arrow and the first stretch of the way it shows; a milestone's extra line. Debug: "Northern lights in the sky" (A),
  Teleport near one (cold lands).
- **Frost and Storm** - a quarter cheaper under the lights. Debug: A, give a Frost tome, Ranks.
- **Barrow spirits** - the spirit rising and fading with the lights, its mark, its errand (grave, sword, grave
  robbers) and the hand-in at the barrow; the question at the way down; going down or robbing the bier, the angry
  dead and the hostile spirit. Debug: A, Teleport to a barrow in the north.
- **The glow** - blue-green round ghosts and their kin, red round fiends. Debug: A, Spawn a ghost or an imp.

## The Rift and the Ashen Deep (built 24 October 2026)

- **The rift on the land** - the glowing entrance, the ash spreading month by month, the omen, the raids as news and
  a plundered village; closed, the ash going back. Debug: "Open a rift near you" (R), Time (months on).
- **Under a deep dungeon** - the crack at the bottom of a dungeon four levels deep or more, down and back up.
  Debug: R until it opens under one, or Teleport to that dungeon's bottom.
- **The levels** - the river of fire and its chains, vents and their smoke, bone fields rising, cages and the gaoler
  running for the gong, no rest. Debug: Teleport (dungeon: The Ashen Deep).
- **The creatures** - each trick: swarm and burning ground, the hooked chain over the fire, blinding ash, sulphur,
  the slag brute's burn and brittleness. Debug: Spawn.
- **The Lord of Cinders and the gate** - healing while the bowls burn, the hounds at half strength, the gate's three
  blows, the rift closing. Debug: Teleport to the bottom, God mode.

## Old places on the land (approved 23 October 2026)

### Part A: the old, lived-in world (built 24 October 2026)
- **Old battlefield** - born from a history event; the cairn names it; digging a mound gives rust, very rarely a named
  weapon; the dead walk on the battle's day at night. Debug: Teleport (kind oldfield); Time, to night; W: the dead walk
  every night; B: the next mound gives the blade.
- **Deserted village** - the cause from history; who lives there now (bandits, hermit, ghost by night). Debug: Teleport.
- **Broken bridge** - piers, the ford beside it, the pier shows the old way. Debug: Teleport.
- **Memorials** - the stone with names adds a chronicle fact; the fallen statue; the gallows hill with the Watch's sentences.
  Debug: Teleport by kind.
- **Old quarry** - half-cut blocks, unfinished statue, flooded ones, a fossil now and then. Debug: Teleport.
- **Shipwreck** - only at low tide; searched once; the wreckers may have been first. Debug: Teleport; Time to move the tide.
- **Hermitage** - the hermit's hint once a week. Debug: Teleport.
- **Leper colony** - the bell, food at the gate, the temple job "Alms for the lepers". Debug: Teleport; Jobs to make the job.
- **Marks of the peoples** - boundary stones, moonstones, skull poles, kobold scratches and their hoard. Debug: Teleport
  (poi kinds).

### The Varnish (built 25 October 2026)
- **Varnish ruins in the wild** - never on the map before you walk there; found by walking among the columns in their
  zones; they match the land (overgrown, sand, marsh, ice); a name stone read with the letters names the city. Debug:
  Teleport (kind vcity); V gives the letters and puts every Varnish place on the map.
- **Hidden dungeons** - no rumour, map or job names them; the way in only on the spot (a stone with the letters, a well
  that draws air, a hollow flagstone, a lever behind a statue); a boss of its own at the bottom, each once per world, and
  back up onto the Sky Court. Debug: Teleport to the city; V for the letters.
- **The Varnish places** - wall towers (the lantern on one, lit at night, shows the whole wall), wind tower (look-out;
  howls in a storm: Weather), road of the standing dead (read a seal; break one and a bound dead steps down), star-iron
  forge (shards of star-iron), Gate of Leagues (its star map shows the nearest city and the other gates), sluice hall
  (open the sluice: it runs dry, old coins), the fallen sky, star house (sweep the dust by walking), sunken harbour.
  League stones IV to I toward a city. Debug: Teleport by kind; Time for the night; Weather for a storm.

### Archaeology (a life skill)
- Dig spots seen by rank; breaking less at higher rank; learnt only at places of your own height. Debug: set the rank;
  show all dig spots on the map.
- Gives lore fragments (the five riddles), star-iron pieces a smith mends into an old power, a modest income from collectors
  and libraries. Debug: give a fragment or a piece by name; show a riddle's state.

### The Varnish' own lore and books (built 25 October 2026)
- **Fragments** in the chronicle chapter The Varnish, under their headings: from stones read with the letters, the
  scribe's option The Varnish, now and then a rumour. Debug: V for the letters, then read stones; open the chronicle.
- **Books bound from pages** - eight of the 27 per world, at least one per thread; a page goes in with your papers and is
  read with the letters; from the second page "n of N" with the missing ones; the scribe binds a whole set (Bind) and
  finds the hidden page; the bound book reads from the bag and sells once. Debug: P gives every page of this world.
- What some books add: the recipe Fig Bread; the ferrymen's tally (ferries free); the apple tree at the Anchor (one apple
  a year); an old way; places on the map; a riddle piece; a lie shown up. Debug: P, then bind each at a library.

### Part B: newer places
- Logging camp, charcoal burners, peat cutters, salt pans, a realm's war camp (only in a war), refugee camp (after a
  plunder, becomes a hamlet or goes), beacon hills (lit in a war or a raid), lighthouse, toll bridge, caravanserai,
  prospectors' camp (after a Starfall), a lord's hunting lodge (poaching). Debug: teleport by kind; start a war or a raid;
  force a Starfall.

### Places of today's peoples and powers (1-44)
- Realms, Church, the Watch, companies, revolt and pretender, witches, raiders and riders, dwarves, elves, halflings, gnomes,
  orcs and the tribes, and for all (see `plan.md`). Debug: teleport by kind; set standing with a people or power (the dwarf
  road, the watch tree, the duel ring all depend on it).

### More places (45-64)
- The land itself, people who live apart, where peoples meet, small secrets (see `plan.md`). Debug: teleport by kind.

### Seasonal places (65-86)
- Each only in its season: salmon leap, flood lake, lambing fold, bird cliffs, blossom orchard; what the drought shows,
  tournament field, harvest camp, travelling fair; rutting ground, mushroom wood, goose marsh, vineyard, pannage wood; frost
  fair, ice road, herders' winter camp, wolf winter, snowed-in inn; the standing dead on the longest night, the wind towers
  on the day of the Loosing, Thessa's harvest stone. Debug: set the season and the day; force a drought; force a hard winter.

### Feast days
- Each feast only in its own region, people or faith; the name with the date; one or two things to do; prices move.
  Debug: set the date to any feast; teleport to a town that keeps it; list which towns keep which feasts.
- **Wanderer's Eve** - bump the inn's hearth on 5 Longnight, set your boot, sleep; the morning gift follows your year
  (honest: a small thing or a rhyme that is a rumour; Skell's devoted: his luck; crime: a lump of coal). Debug: set the
  date; set or clear your crime record for the year; set your god.
- **The Masking** - a mask hides who you are (also when wanted). **The Naming** - a ghost's name lays it down. **Thirst
  Month** - oases must take you in. Debug: give a mask; spawn a named ghost; set wanted.

### The five riddles (built 25 October 2026)
- Each riddle in The Old Days under its title, with its gap; whole at six true pieces of eight; false ones get "Not so"
  then; the answer and the lead to its deep place with its own boss; all five give The Ruin, as it was. Debug: V and P,
  then the stones, the places and the library; Teleport to the deep places (kind vdeep).

## The great evils as storyteller (approved 25 October 2026)

- **The servants** - each of the 24 kinds: its land, its lever on the realms and powers, its lieutenants, its weakness
  and relic, waking by weight. Debug: pick the world's three servants; wake one now; set its power.
- **The two clocks** - the slow growth, the attention rising when you meddle and cooling when you stop, the ceiling.
  Debug: show and set the attention; let a year pass.
- **The realms** - a servant's push, the realms pushing back, a barony held by a servant. Debug: force a push now.

Built in part 1 (29 October 2026): The shadow (S) in the debug menu: his attention one step up or back to nothing;
name, wake every servant; break a seal; know every weakness; every lieutenant on your map; a hero rides out now; a
month goes by for the servants. Teleport lists the lieutenants' places and his coast. Look at the Shadow tab (e),
the Shadow layer [7] and the Realms layer for held baronies. Test part `shadow`.

Built in part 2 (29 October 2026): The shadow (S), column THE SKY-SEAT: tear the mist, give a relic, to the foot of
the chain, to the underside, to the first and third floor, to the throne, let him win (three seals), kill him (the
end). Climb the chain and wait for a gust beside and away from a handhold; stand on a broken link; light a beacon;
die on a floor and beat your shade; ask the skipper nearest his coast with and without a relic. Test part `skyseat`.

Built in part 3 (31 October 2026, rounds 31-32): the other sixteen kinds (`servants.py`). The shadow (S): every lair
on your map; heavy, middle, light one: the next kind (8, 9, 0 swap a servant for the next of its weight, in the same
lair). For each kind: its mark on the land and the line under the map; a month goes by (its lever: news, a struck
village, a held barony); its lieutenants' places; its lair and boss (the deck's three phases); its weakness known
(know every weakness) and the edge in the fight; its relic and what it gives. Camp in the Nightmare's land (no rest);
watch the Hag's hut move after a month. A struck village sends refugees on the road (walk into them). Let a hireling
fall in a barrow or crypt: the shade, no raising until it is beaten. Kill a servant that holds a barony: a real war
over the freed lands. Break the Rift's burning gate: the Cinder Key. Test part `servants`.

- **The quest** - the mist parting, the relics, the road, the chain climb, the five floors, the beacons, the last
  fight's three phases. Debug: break a seal; give a relic; teleport to the chain, to each floor, to the throne.
- **Dying there** - the dearer raising, the shade with your backpack, what stays open. Debug: kill the player there;
  spawn your shade.
- **The ends** - the Long Night, the closing screen and the healing world. Debug: let him win; kill him.

## Trade as a way to play (approved 25 October 2026)

- **The money** (built 29 October 2026) - prices bending by how dear a good is, stock coming back slowly, a route
  tiring: sell one good twice in one town and see the price drop. Debug: Coin, Time (let days pass).
- **Goods with a name** - each named good, its region, the rumour, good and bad years. Debug: list the world's named
  goods; teleport to a maker; set the year good or bad.
- **Master makers** - a masterwork bought and brought to who asks, an order. Debug: give a masterwork; teleport to a master.
- **The other ways** - contraband and the gate search, barter with kobolds, orcs and elves, monster goods, spoiling, a
  far town in need, far goods, war trade, market news, the great fair, League rank. Debug: give each good; start a ban,
  a siege or the fair now; set League standing.
- **Your caravan** - buying wagons and beasts, the crew and wages, the string on the map, passes, mud, fords, ferries,
  fodder, a broken wheel, the night ring, a raid on the fight map, leaving it in a stable. Debug: give wagons and crew;
  spawn a raid on it; break a wheel.
- **The NPC caravans** - travelling along, trading on the road, League rivals arriving first, what robbing brings.
  Debug: spawn a caravan beside you; send a League caravan to a town.

## Boss fights (approved 26 October 2026; part A built 29 October 2026)

Built in part A: F12, Bosses (K) sets down Snagtooth, the Lich or the Dragon, sets its phase, shows the rhythm, shuts
or opens its room, runs the fairness check, kills its helpers, makes it spent or staggered, flees once more, and adds a
twin of the next kind. Test part `bosses`.
Built in part B: Bosses (K), "Any boss with a kit..." sets down any of the 31 (the fixed bosses, the theme bosses,
the Varnish guardians), each in a room of its own with its tricks; "A roaming boss..." sets one down ten steps off,
out of sight, to listen for it, follow its tracks and take it up or down the stair. Killing a fixed boss offers its
three things. Test part `boss_moves`.


- **A fixed boss** - each phase, its deck, its room tricks, its three items to choose from. Debug: place any fixed boss;
  set its phase (1-3).
- **A made boss** - the maker's draw from a base, element, level and seed; its name, rumour, deck and arena. Debug:
  make a boss (base, element, level, seed) and place it, or open its job.
- **The rhythm** - draws, the shuffle card, the rhythm breaking. Debug: "Show rhythm" writes its deck and next beat
  under IN SIGHT (test build only).
- **Marks and fairness** - every shape, the number's colours, a free tile for each blow. Debug: "Fairness check" runs
  every move of the boss in this room and names the ones that fail.
- **Spent, staggered, breaking, Resolve, breaking through a phase** - Debug: "Spent now", "Stagger now", give the
  stunning skills.
- **Helpers and twins** - each job, each twin kind. Debug: place a helper with a job; kill helpers.
- **The arena** - the mist, the shut room, the way out, coming back after fleeing. Debug: shut or open the arena;
  "Flee test" (as if you fled once more).
- **Roaming bosses** - sounds, tracks, following up the stairs. Debug: place a roaming boss on the level.
- **Arenas by place and ways out** (built 5 November 2026) - a nave with pillars, tombs with statues, a forge's pool,
  a cave's lake, a glade, a lord's hall; the rope up and the hole down. Debug: the boss floor of the next place (Enter
  again), shut the arena.
- **The place answers** (built 5 November 2026) - out of a place whose master fell: it falls in for good, or wakes
  with worse in it. Debug: the boss floor, kill the boss (god mode), go up and out.
- **Won another way** (built 5 November 2026) - hold out (boats), cut the captive free (missing), break the black
  altar (shrine); half of those fights. Debug: a job of each kind (Enter again for the next).
- **The big one and the relic** (built 5 November 2026) - the big one fights before it comes in; a lost relic has a
  keeper. Debug: the big one's job with a rod; a relic job.
- **Hirelings in a boss fight** - stepping out, handling marks, breaking. Debug: give a hireling of each kind and rank.

## Places of today (built 30 October 2026)

- **Each place** - its small map, every telling thing answers a bump, every keeper talks. Debug: Teleport (the
  place's kind is in the list).
- **Toll bridge, serai, beacons** - pay or dodge the toll; no robbers near a serai with your wagons; beacons burn at
  night in a war. Debug: Teleport, Force an event ("Two realms go to war"), Time (night).
- **Coming and going** - a realm's war camp in a war, refugees by a plundered village, prospectors after the
  Starfall. Debug: Force an event ("Two realms go to war", "A star falls"), and plunder a village with a raid.

## Odd corners and the seasons' places (built 30 October 2026)

- **Each place** - its map, its telling things and keepers, in every season. Debug: Teleport, Time (months ahead).
- **Part of the year** - the drought's village in a dry summer, the fair moving each week of summer, the frost fair
  in deep winter, the wolf den in a hard winter. Debug: Time (months, weeks), Teleport.
- **The cache** - bump the wrong milestone, the robber's stone appears on the map. Debug: Teleport to the milestone.
- **The Standing Night, the Loosing** - 21 Longnight by night beside the road of the bound dead; 14 Seedwake inside
  a wind tower. Debug: Time, Teleport.

## The Avarenthia Editor (approved 31 October 2026)

- **The editor itself** - draws, saves, checks, Try. Nothing needed in the debug menu: it is its own program in the
  test download; Try opens the game with the debug menu on.
- **Puzzle things** - each of the 44 answers a bump or a step, resets with its lever, keeps its state when you come
  back. Debug: Teleport to an example puzzle room (one of each), "Reset this room".
- **Creatures from lists, dressing in the game** - a room filled anew. Debug: Theme room or river (a fresh level
  round the piece), or F5 Try in the editor.
- **Switches, counters, timers, "back as drawn"** - a lever works bars, a timer shuts them, the room goes back.
  Debug: F5 Try in the editor on a room with them.
- **Own tiles and things** - made with Ctrl+T, they show in the game with their own sign and look line. Debug: F5 Try.
- **More doors** - a room with `'` doors opens a different one or two in every world and the level runs through it.
  Debug: Theme room or river (several times), Reveal map; F5 Try in the editor.
- **Whole places** - each lies in the world (kind "drawn"), every floor reached by its stairs onto the twin stair,
  its people talk, its rumour at the inn and its line in a library book mark it on the map. Debug: Teleport (kind
  drawn in the list), Reveal map; in the editor F5 Try on a whole place (you stand at its west edge).
- **Whole places in the editor** - Ctrl+N "A whole place", floors with PgUp / PgDn and + up / + down, In the world,
  people and finds on the Creatures layer, a room at 40 x 30 made a whole place, saved to my places.des.
- **Makers in the editor** - Ctrl+G, pick a maker, R for another, Enter; take a part by dragging a frame; check the
  floors of a temple or a dungeon come as tabs. Maker area: select a rectangle in a whole place, Ctrl+G, then F5 Try
  and see it filled and joined to the rest.

## A finer look, not busier (approved 31 October 2026, built 5 November 2026)

- **Remembered land and roads** - the world map out of sight in its own dull colours, roads calmer than towns. Debug:
  reveal the map (Teleport far, or a reveal-map option).
- **Each level's tint** - a den, an ice cave, a fire level, a drowned level, a crypt each remember in their own tint;
  a mine with a fire or ice level below. Debug: Teleport to each kind, reveal the level.
- **Fade-in** - stairs, gates and entrances, with effects full, short and off. Debug: none needed.
- **Names and panel** - a name next to a sign and at the edge of the view; a target at full and low life; a long
  name in IN SIGHT. Debug: Teleport, spawn a champion with a long name.
- **Names in the log** - a fight, a find, a drink: creature and item names in their map colour, the rest of the
  line unchanged; a wrapped line keeps the colour. Debug: spawn a foe, Give item.


## The belt and the tally (approved 1 November 2026, built 5 November 2026)

- **Potion grades** - each grade of health and mana, what it restores, where it is sold. Debug: give potions of any
  grade (Give item), Teleport to a village, a town, a city.
- **The belt** - pockets by belt worn (none, sash, belt, a "+1 pocket" belt), Shift+1-5, Q and W picking the smallest
  grade that will do, refilling once no foe is in sight, the tip. Debug: give belts and potions, spawn a foe.
- **Drinking from the pack** - three turns, broken off by a foe coming in sight or a blow. Debug: spawn a foe
  out of sight, empty the belt.
- **The tally** - from the menu at any time, after the win, at death; every number counting. Debug: F12 [Y] fills
  the tally with plausible numbers and opens it; the Tests page also opens the death and win screens.


## More makers (approved 1 November 2026, built 5 November 2026)

- **Each new maker** - every kind can be reached and seen whole. Debug: the recipe takes you into the next kind each
  time (Enter again), Reveal map.
- **States and break-ins** - one place in each of the 14 states and a level that breaks into another kind. Debug: the
  recipe sets the next state each time (Enter again); the 15th is the bottom of a place with a cracked wall.
- **States shifting** - a besieged place falling, a plundered one growing over. Debug: the recipe besieges a place and
  lets 22 days pass (Time); set a place's state with the recipe above.
- **Time and season places** - the tide cave at high and low tide, the drowned village in a dry summer, the fey
  hill's lost week. Debug: set the hour and the season (Time), the recipe stands you at each place's door.


## Marked creatures (approved 1 November 2026, built 5 November 2026)

- **Each affix** - a champion and a unique with each of the 20 affixes; what it does and its answer (Dispel, fire on
  Regenerating, burning or hallowing a Grave-bound body). Debug: spawn a champion or unique with an affix of choice.
- **Fit and rarity** - affixes match kind, place and season; never Frost-touched with Fire-blooded; about 8% champions
  and 3% uniques. Debug: Teleport to a fire level and a winter map, Reveal map.
- **Seen and told** - the affix line in IN SIGHT, the look line, the first-time tip, a unique's new name. Debug: spawn
  a unique, reset tips.

## Playing it (approved 1 November 2026, built 5 November 2026)

- **A note for Claude** - the zip beside the save with the note (as long as you like, wrapped as you type), the screen
  and the save; loading that save stands you where the note was written. Debug: it is itself a debug menu line.
- **Saves that last** - a save from the build before loads, with new fields filled; a breaking step gives the one
  line on the main menu; a save that cannot be written says so in red. Debug: none needed; keep an old build's save.
- **The money check** - `python tests/money.py` prints the three tables; the part `money` stays in its bands.
- **What you met** - meeting a system the first time adds it with the day; F12 shows met and never met; the note's
  zip holds the list. Debug: it is itself a debug menu line.
- **The first tome** - Snagtooth's hoard with three tomes of three schools; a village shop's tome now and then; the
  shelf in the temple where you wake; `tests/money.py --opening` prints the day of the first tome. Debug: Teleport to
  the Hollow Den, spawn Snagtooth, give coin.
- **The Eleven Ways** - the lectern in the start temple with all eleven classes; a guild hall selling its school's
  first tome only while you are blank. Debug: Teleport to a guild hall, give coin.
- **A letter for the city** - Berend's letter and loads after Snagtooth; selling them in the city; the merchant's
  lines; the good taken home and sold; the bookseller and the stamp. Debug: set Snagtooth slain (story flags),
  Teleport to the city.
- **The baron's word** - the messenger in the letter's city, the sealed word, the lord's seat, the realms layer opening,
  the first realm job, the war version. Debug: set the letter done (story flags), Teleport to the city, start a war.

## Folk in need (approved 1 November 2026, built 5 November 2026)
- **Folk with a need** - the `!` on them, the log line when near, the window, the Jobs tab; each source making its
  need (a monster group, news, season, caravan, realm, old place, trade, people); a need running out and its sign in
  the world. Debug: "Folk: make a need here" (by source and kind), Time (skip days), Teleport.
- **Twists and seeds** - each of the 18 twists, also on a board job; each seed where it may fall; a follow-up. Debug:
  make a need with a chosen twist or seed; "Folk: next part now".
- **Rewards and favours** - standing in town and with the people, each reward kind, each favour showing in its window
  (ferry, gate while wanted, lord, guide). Debug: give a favour (Give item), set wanted (crime).

## The test menu (built 5 November 2026)

- **Tests page** - every built line of this file shown, each set up by its key, ✓ and ✗ kept after a restart and
  after a new build. Debug: F12, [T].
- **Note for Claude and ✗** - the zip beside the save with note.txt, screen.png and the save; loading that save
  stands where you stood. Debug: F12, [N]; a ✗ on any test.

## Crafts guilds (approved 2 November 2026, built 5 November 2026)
- **The four new guilds** - each guild's halls among three peoples; joining; a rank asking the craft's rank and the
  entry fee. Debug: Teleport to a hall, set a life skill rank, give coin.
- **Bench, test and mark** - the guild bench free for members and paid for others; the master's test in the hall; the
  mark in an item's name and its better price. Debug: set guild rank, give materials (Give item).
- **Board, secrets, day** - the master's board orders; each of the four secrets; the guild day's stalls and contest.
  Debug: set guild rank to Master, Events "Today is this town's guild day".
- **Streets and happenings** - the smiths', tanners' and weavers' streets in a city; the quarrel over the water, the
  strong arm, the journeyman. Debug: Teleport to a city, "Town: make a happening".
- **Guild jobs** - each of the seven kinds from a guild master; the quarrel's three ways (side, side, mediate) with
  the bench and board shut for a season, the favour, the empty racks or dry vats; the fallen mine opening; each
  heirloom's three parts. Debug: set guild rank, the master's "Guild work of the hall".

## A window that fits (approved 5 November 2026)
- **Sizes and Zoom** - the game at several window sizes (more map, panel and log the same), every full screen
  centred; Zoom Auto and 1x-4x on the title screen. Debug: a "Window size" choice that sets the cells (110 x 60,
  120 x 67, 160 x 90, super wide with margin).
- **The margin** - the random old-map stretch, a new one on a new zone or day, still in between. Debug: "Margin: new
  stretch now".

## The bar of seven keys (approved 6 November 2026)
- **Four class keys** - 3-6 hold four class skills, at most one elite among them (a second elite refused with a
  line); an old save's elite moved to key 6 and its epic to 7. Debug: give tomes, Guild rank (q) to 4.
- **The epic on key 7** - key 7 shows only once an epic is learnt; the tip; the ♦ filling dull to bright gold by
  fighting, nothing from foes far below you, kept over a rest; Phoenix once per day. Debug: "Epics: rank 40, teachers,
  deeds" (E), which also fills the charge; spawn foes of your level and far below.
- **The bar after a rest** - [z] changes the bar after an inn's bed or your camp, not before walking on elsewhere.
  Debug: "Rested here", Teleport out of town.
- **Casting from the book** - a known skill off the bar from the [z] list: 3 turns, its cost, broken off by a new
  foe or a blow; elites, the epic and weapon skills refused. Debug: give tomes, spawn a foe out of sight.
- **The balance measure** - `python tests/balance.py` prints the table; old bar against new, with and without an
  epic. Debug: none (a tool).

## The Counted Sky in the game (approved 6 November 2026)
- **The made-even lore** - the fall riddle names Vael and her Crown; the new fragments under "Before the Founding";
  the four new Varnish books. Debug: "Varnish: all pages and the letters", a library to bind.
- **The peoples' books** - pages of each people where they fit; read as one of that people, with a hireling of
  that people, or read aloud in their place; bound by that people; each book's effect; the Peoples headings.
  Debug: "Folk books, story places", Race at start, hire a hireling of any people, Teleport to a hold, glade, hall.
- **The peoples' voices** - elves' greetings, traders and rumours in their tone, then the others. Debug: Teleport to
  the elven city, a glade.
- **Bardin, the altar stone, Ferro, Tam's tally** - each place, its one outcome: Bardin carried to a dwarf hall and
  laid flat; bread and oil at the stone in spring calm the sand round the bones that year; Ferro tells the measure,
  his seal broken he rests; Tam counted. Debug: "Folk books, story places", Teleport to each.
- **The dark ring, Aerith, the goblin drains** - the star floor before and after the King; breaking Aerith's chain
  and the lighter first phase; the drain way up. Debug: "Folk books, story places" (knows the drains), "Sky-Seat: open
  the mist", Teleport to a star house (sweep it).
- **The Wall on the world map** - the broken line on seen stretches, all of it after the lantern. Debug: Reveal map.
- **The court under the hill** (a secret) - the barrow and its mushroom ring look ordinary; the door only at night
  under a full moon after walking widdershins round it inside the ring; the court's movement, trails, flowers, signs
  that change, the mirror pool, the "?" date, the gold words of a bargain, the honey wine, a season gone outside.
  Debug: "Fey: hill, night, door" (three presses: to the hill, a full-moon night, the door).

## Games at the inn (approved and built 6 November 2026)

- **Bones** - the gaming table in an inn of each people, its name and twist, throw/set aside/stop, the skull, the
  limit per night, seeing and using a loaded bone with Cunning, being caught and not served. Debug: Teleport to an inn
  of each people, Time (evening), Coin, set Cunning's rank (Ranks).
- **Vigil** - a game against each kind of player, the three strengths, the Iron and the Watch, Vael to an edge, the
  boards of the peoples, the masters told by rumour and the title. Debug: Teleport to an inn, an abbey, a master.
- **The Count** - draw or stop, the three suits, Water face down till the end, the dealer, the limit per night,
  counting with Cunning and being shown the door. Debug: Teleport to an inn, Time (evening), Coin, Ranks.

## The older rounds (lines added 13 November 2026)

What was built before the Tests page, so it can be checked from F12 too.

### Rounds 1-5: the first world

- **Monsters of each kind** - goblins, orcs, undead, beasts and spiders each fight their own way; IN SIGHT names
  them. Debug: Spawn (goblin, orc, skeleton, wolf, spider) in a dungeon.
- **Named enemies** - a named foe with its title and its drop. Debug: Teleport to a lieutenant.
- **Guilds** - the guild masters, ranks, their jobs and their skills. Debug: Teleport to a city, Guild rank (q), Coin.
- **Jobs** - taking a job from a board, following it, its end and pay. Debug: Jobs (a bounty, a courier).
- **Seasons on the world map** - snow, ice on the rivers, passes shut, leaves, fires in a drought. Debug: Time
  (month 1, 7, 10).
- **Sailing** - a skipper in a harbour, a voyage, pirates on the way, the cove. Debug: Teleport to a harbour city,
  Force an event (pirates).

### Weapons and the bestiary

- **Each weapon kind** - reach, crossbows, two weapons, fists, the armoured rule. Debug: Give item (spear,
  crossbow, two daggers), Spawn.
- **The bestiary grows** - three steps of knowing a kind, what each step shows in look and IN SIGHT. Debug: Spawn
  a wolf, kill it a few times.

### Magic

- **The schools** - each school's tomes, its spells on the bar, mana. Debug: Give a tome of each school, Ranks.
- **Spell effects on the ground** - burning ground, ice walls, roots, corpses for necromancy. Debug: Fire, Frost,
  Nature and Necromancy tomes, Spawn.
- **Stamina** - running, heavy blows and armour spending it, resting giving it back. Debug: Give heavy armour.

### Realms and the land

- **Realms and wars** - kingdoms, barons, houses, a war and its end, the Realms layer [4]. Debug: Force an event
  (realm war), Time (months on).
- **Walking the land** - the zones under the world map, [>] into the land and out at the edge. Debug: Teleport to
  the world map, a road over a river.
- **Herds and hunting** - herds on the land, the wind, the hunt, skinning. Debug: Ranks (hunting, skinning), Time.
- **Nature and wonders** - each wonder on the land and what it gives. Debug: Teleport to a wonder.
- **Place names** - names of the stretches of land on the line under the map. Debug: Teleport to the world map.
- **Ferries** - the ferryman's hut, the fare, the crossing. Debug: Teleport to a ferry hut.
- **Keeping it clear** - the look legend, the journal's Signs, the first-time tips. Debug: reset the tips.
- **The handbook and the chronicle** - [?] and every chapter, the journal's chronicle. Debug: none needed.

### Life on the road

- **Hirelings** - hiring one, the wage, their gear, threat, leaving. Debug: Add a hireling (each kind), Coin.
- **Hunger and cooking** - getting hungry, a meal at a fire, dishes and their buffs. Debug: Ranks (cooking), Time.
- **Fishing** - a rod by the water, the fish by season and weather. Debug: Give a rod, Teleport to a village.
- **Crime and the Watch** - stealing, being seen, the bounty, the gaol or a fine. Debug: Teleport to a town.
- **The temple and the gods** - prayer, blessings, healing, the price of a curse lifted. Debug: Teleport to a
  temple, Coin.
- **Weather** - each kind of weather and what it does to sight, fire and travel. Debug: Weather (rain, storm, fog,
  snow).
- **Day and night** - dusk and dawn by season, night sight, sleeping at an inn. Debug: Time (hour 21, hour 5).
- **Death and the chronicle** - dying, the tally, the chronicle of your life. Debug: Fill the tally and open it.
- **Trade at a market** - buying low and selling high, the stock and the price going back. Debug: Coin, Teleport
  to a city.
- **Herbs and potions at a shop** - the healer, potions by grade, selling herbs. Debug: Coin, Give a plant.
- **Factions** - standing with the Crown, the League, the Circle, the Black Hand and the Cult, and what it opens.
  Debug: Standing (each faction).
- **Hostile camps of the tribes** - the warning, the rousing, captives, the kobold toll. Debug: Teleport to an orc
  camp, a kobold warren.
- **Dwarf holds and mines** - the hold's gate, digging with mining, the cart line. Debug: Teleport to a dwarf
  hold, Ranks (mining).
- **The peoples' lands** - halfling hills, elven glades, the city under the Elder Tree, gnome hamlets. Debug:
  Teleport to a glade, gnome hamlet.
- **Old ways** - hidden roads and their entrances. Debug: Show the whole map.
- **The harbour** - ships coming in, the harbour master, goods by sea. Debug: Teleport to a harbour city.
- **News through people** - rumours at the inn, news walking from town to town. Debug: Force an event (raid),
  Time (days on).
- **Libraries and the made history** - the libraries' books, the history of the world in the chronicle. Debug:
  Teleport to a city.
- **The underground rivers** - swimming, water and fire rivers in a dungeon. Debug: Theme room or river.
- **The Sky-Seat** - the mist, the skipper, the chain climb, the five floors. Debug: The shadow (reveal, chain).
- **Ships on the land's waters** - ships and pirates passing, the battlefields and rivals of living.py. Debug: Force
  an event (ship, rivals).
- **Arts of Cunning and Arcane** - snares, runes, gates, dispel, the first blow. Debug: Ranks (cunning, arcane),
  their tomes, Spawn a sleeping foe.

### The Varnish and the great evils

- **The Varnish on the land** - its ruined cities, the Northern Wall, league stones. Debug: Varnish letters and
  places, Teleport to a Varnish city.
- **The great evils** - a servant awake, its marks on the land, its lair, the Hollow King's coast. Debug: The shadow
  (name, wake, lairs).

## A roof of your own (approved 6 November 2026, built 13 November 2026)

- **A town house** - the `$` door in a settlement of each people, buying it, each people's kind of home, the hearth
  tax each season, the town selling it after a year unpaid. Debug: Teleport to a town of each people, Coin, Time
  (a season on, a year on).
- **Building anywhere** - the builder's stake, placing it on the world map, each stage from camp to keep with its
  goods and days, the look by the land. Debug: Coin, give timber and stone, Time (days on), Teleport to each biome.
- **The risk** - each outcome of the weekly roll (theft, a broken piece, squatters, fire, flood, snow, a great
  evil), the news line, each defence lowering it. Debug: "Home: roll now" with a chosen outcome, set region threat.
- **A seat** - buying an empty seat or fort from the baron as his knight, restoring it, the steward and guards'
  wages, the baron's call in a war, losing it to a new lord. Debug: make you a knight, Coin, start a war, end it.
- **Furnishing** - the first-time tip, placing, picking up and moving, every piece's bump, Comfort's stars and
  "well rested", the peoples' styles and a full set, dyes, delivery. Debug: give furniture of each style, Coin.

## Heard, lit and seen (approved 10 November 2026, built 13 November 2026)

- **Noise** - walking, running, a fight, each school's spells, a kicked door, heavy armour; the ring of `◦` along
  halls and not through rock; Quiet/Soft/Loud under the map; a foe coming to look with `?` in IN SIGHT. Debug: spawn
  a foe behind a wall, Gear (heavy and light armour), Ranks (Cunning).
- **What you hear** - the dim letter or `?` in the dark, the log line, fading, Cunning hearing further. Debug: spawn
  a known and an unknown kind out of sight, Bestiary (know a kind).
- **Noticing** - in the dark and in torchlight, near and far, with sneak, a boss and a beast. Debug: Teleport to a
  dungeon and a hostile camp at night, Time.
- **Light that lives** - burning ground, a fire spell, lightning, lava, a burning house lighting the room; a torch
  put out; a shadow behind a pillar. Debug: give fire spells, start a raid on a village.
- **Last seen** - the dim mark where a foe left your sight, gone when you look there again.

## The land tells, and an inn in every town (approved 10 November 2026, built 13 November 2026)

- **Signs on the land** - smoke over a village from afar (and dark with a fire over a burning one), birds before an
  ambush, vultures over a fight, a worn path growing and growing over. Debug: Teleport near a village, start a raid,
  force an ambush, Time (days).
- **Villages rebuilt** - a raided, plundered, burnt settlement through its stages back to whole. Debug: start a raid,
  Time (weeks on).
- **An inn in every town** - each city style and each people's town has an inn with a bed and a gaming table.
  Debug: Teleport to a city of each style.

## A first sight of a town (approved 10 November 2026, built 13 November 2026)

- **The skyline card** - the first time in a hamlet, village, town, city and metropolis of every people; drawn from
  its own map (wall, towers, spire, keep, roofs), by day, at night with lit windows, in winter; once only, again from
  the journal's Places; a burnt settlement. Debug: Teleport to a settlement of each people and size, Time.

## Camps on the road (approved 10 November 2026)

- **A host's camp** - by night on the march and as a siege camp; the signs on the world map and the line under it;
  the camp's map with a campfire for each pair of tents by night and cold fire pits by day; as a friend, a stranger
  and a foe (sneaking in, the orders, the stores, the prisoners); the fire rings left behind. Debug: start a war,
  make you a knight, Time (dusk, dawn).
- **A traders' camp** - by the road at night, trading, the road's news, travelling with them, a night raid.
  Debug: Teleport near a road with a caravan, Time (dusk).
- **Each people's camp** - a kingdom's host, a siege camp, a dwarf hammer band, an elven war-band (seen only from one
  cell), the Gorvash, sea raiders on the strand, riders; their signs on the world map by night and their own maps.
  Debug: "Make a camp here" by people, Time (dusk).
- **Inside the tents** - every tent of every people walked into; the marshal's orders, the stores, the wounded, the
  chapel, the prisoners; sleepers waking at a noise; a chest taken; a tent set burning. Debug: "Make a camp here",
  Time (night).

## Wars that feel like wars (approved 10 November 2026)

- **The forces** - the king's host and the barons' hosts on both sides, the defender marching out, a battle where two
  hosts meet; raiders, foragers, messengers and scouts between them; no more than about eight signs per war.
  Debug: start a war, Time (days on), the Realms layer [4].
- **The front and the seasons** - burnt border villages, refugees, prices; hosts home in winter; levies going home,
  hosts shrinking, deserters turning robber. Debug: start a war, Time (months on), set the season.
- **A siege** - stores running down, smuggling food in, the postern, a sally, the breach and the storm.
  Debug: "Start a siege at the nearest seat", Time.
- **Ransom and the peace** - take a lord in battle and sell him back; the war's score; the peace by tribute, hostage
  or land. Debug: start a war, "Give the war a score".
- **The fantasy** - the battle mage or priest, the holy banner, the dead rising on a field in the Lich's land, a dwarf
  hammer band for hire, the Gorvash falling on a worn border.
- **Each people's way** - dwarves besieging and going home, elves' ambushes in the wood, the Gorvash growing, sea
  raiders from the sea, riders' deep raids. Debug: start a war or a raid of each people.
- **Your part** - catch a raid, carry a message, smuggle into a siege, sneak into a camp, stand in a field battle.
- **The field battle** - the battlefield zone with both lines and the moving front; the arrows, the clash, the rout;
  each of the captain's tasks done and failed; the outcome on a knife's edge and lopsided; walking off the edge (your
  lord remembers); the rout with riders after you; the news of what you did. Debug: "Start a field battle here",
  set the hosts' strength.
- **Magic in the wars** - a big host's mage and priest, each school on the front (fire, frost wall, storm in rain,
  roots, the dead rising), taking out the mage; each people's own (rune-smiths, druids, shamans, the storm-caller,
  the wind-singer); a host using necromancy and the Church's answer; a mage player's task; the mage's tent.
  Debug: "Start a field battle here" by people, the weather.

