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
| **Approved: dungeons on their own land** | Built places that stand outside (temple, abbey, tower, fort, manor) start on their own play map with land around them; upper floors and cellars by stairs; each kind its own plan, bigger levels, wider halls, one telling thing per room, a mood line in the messages. Caves stay underground. Underground kinds their own plan too; hand-drawn pieces in data files and an editor for Nilio; classic dungeons from a random maker (rooms of many shapes grow onto the level, main ways 3 wide, narrow ways 1 wide, every passage from room to room). The random maker, the theme rooms, rivers underground and the pieces format are built (24 October 2026), and so are the temples, towers, barrows, abbeys, forts, manors, goblin places and the underground kinds' plans; the editor waits until much later (`docs/open.md`) |
| **Approved: old places on the land** | More points of interest born from the made history: old battlefields, deserted villages, broken bridges, memorials, quarries, wrecks, hermitages, leper colonies, marks of the peoples; overgrown Varnish cities found only by walking, with hidden dungeons beneath. Then newer places (logging camps, war camps, beacons, lighthouses...). The old places of part A are built (24 October 2026), the Varnish too (25 October 2026), archaeology too (30 October 2026); the rest is not |
| **Approved: the great evils as storyteller** | One ultimate evil, the Hollow King, the old shadow of the Varnish in the hidden Sky-Seat; under him three servants per world (one light, one middle, one heavy, from 24 kinds), each pushing the realms and powers with its own goal; a slow clock and a clock of his attention; one long quest with relics, the chains and the Sky-Seat's five floors. Replaces `evils.py`'s growth. Parts 1 and 2 built 29 October 2026 (`shadow.py`, `skyseat.py`, eight kinds). Not built: the other sixteen servants in rounds 31-32 |
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

## Old places on the land (approved 23 October 2026, not built)

More points of interest, so the world looks old and lived in. Approved in the thread on points of interest: "we gaan
eerst A doen, alle ideeen klinken goed". Details and the full list (also the newer places, part B): project files
`poi/ideeen.md`. Each place is one world cell with its own play map (as the wonders and oases), and what matters is a
tile used with one key or a bump. Not the same as what exists: the fresh battlefields and plundered villages of
`living.py`, the hidden places of `hidden.py`, the planned temples, forts and barrows.
- Part A's old places (battlefields, deserted villages, broken bridges, memorials, quarries, wrecks, hermitages,
  leper colonies, the peoples' marks) are built (24 October 2026), and so are the Varnish: their cities, places,
  hidden dungeons, lore, books and riddles (25 October 2026), and archaeology (30 October 2026); specs in
  `docs/built.md`. Still to build here:
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

## Boss fights: what is left (approved 26 October 2026)

The kit, the library and the boss maker are built (`docs/built.md`, "Boss fights"). Not built yet, for a later
round: arenas dressed per place (tower top, temple nave and the rest) and the ways out other than the rotten wall;
the place that wakes or falls in after a few bosses; fights won another way (hold out, rescue, break it, escape);
bosses for the big one (a fish) and the relic job.

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
