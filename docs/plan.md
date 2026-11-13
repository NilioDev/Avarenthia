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
| **To build** | A roof of your own (approved 6 November 2026); camps on the road, wars that feel like wars (approved 10 November 2026); the order: block 22 below |
| **Parked** | Multiplayer; the bard; the werewolf's and the vampire's curse (docs/parked.md) |
| **Later** | Leadership |

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
   the build order on 24 October 2026; back as rounds 33-36 (31 October 2026, "The Avarenthia Editor").
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
    Built 30 October 2026 (see `docs/built.md`). 30. **Places 45-64 and the seasonal places** (L). Built 30 October
    2026 (see `docs/built.md`). Merge after 30.
31. **The great evils, part 3: the other sixteen servants** (XL). Built 31 October 2026 with part 4 in one round
    (see `docs/built.md`). Merge after it.
32b. **The Avarenthia Editor** (approved 31 October 2026, thread "Editor voor speciale kamers ontwerpen"; Nilio's
    "ga" the same evening). 33. **Round A** (XL): the PxPlus tileset, the editor's screen, drawing and saving rooms,
    the check. Built 31 October 2026 (`avarenthia/editor/`, `editor.py`, test part `editor`). 34. **Round B1** (XL): events with switches, counters and wires, variety, creatures and lists,
    dressing, own tiles and things, Ctrl+R, Try. Built 31 October 2026 (`dressing.py`, `owntiles.py`,
    `editor/layers.py`, `maker.py`, `trying.py`; test parts `editor` and `pieces`). Pause after it. 35. **Round B2** (XL): more doors (`'`, `DOORS:`), then puzzle things 1-26 in the
    game. Built 31 October 2026 (`puzzles.py`, `pieces/puzzles.des` with 15 example rooms, the editor's PUZZLE THINGS;
    test part `puzzles`). 36. **Round C** (XL): whole places, puzzle things 27-44. Built 1 November 2026
    (`drawnplaces.py`, `places/saint-odo.des`, `editor/placemode.py`; test parts `puzzles`, `drawn_places`, `editor`).
    Merged after 36 (see `docs/built.md`).
37. **Block 10: playing and reporting made cheap** (settled 2 November 2026, thread "Testen in de testbuild makkelijk
    maken"; the Dutch proposal: project files `bouw/volgorde-2.md`). 37. **The test menu** (L). 38. **Saves that last**
    (M). 39. **The money check** (M). Built 5 November 2026 (see `docs/built.md`).
40. **Block 11: the start of the game.** 40. **The first tome, a letter for the city, the baron's word** (L; built 5 November 2026).
    41. **What you met** (M; built 5 November 2026). 42. **The belt and the tally** (L; built 5 November 2026). Merge after 42.
43. **Block 12: a finer look, not busier.** 43. **Items 1, 2, 5, 6, 7** (M; built 5 November 2026). 44. **Item 3, then item 4** (M; built 5 November 2026). Merge
    after 44.
45. **Block 13: creatures and folk.** 45. **Marked creatures** (L; built 5 November 2026). 46. **Folk in need, part 1** (XL; built 5 November 2026): the maker, needs
    from the world, the grammar, rewards, who remembers you. 47. **Part 2** (L; built 5 November 2026): twists, favours, the 120 seeds.
    Merge after 47.
48. **Block 14: the crafts guilds** (added 5 November 2026; after folk in need, whose maker makes the guild jobs).
    48. **Crafts guilds** (XL; built 5 November 2026): the four new guilds and their halls, ranks, the guild bench, the master's test in the
    hall, the guild mark, the master's board, the secrets, the guild day, their streets. 49. **Guild jobs** (L; built 5 November 2026): the
    seven kinds, the quarrel over the water and its consequences, the founder's heirlooms. Merge after 49.
50. **Block 15: more makers.** 50. **Part 1** (XL; built 5 November 2026): the fallen dwarf hold, real mines, sewers, catacombs, the castle
    dungeon, the maze, ice caves. 51. **Part 2** (XL; built 5 November 2026): lava tubes, tide caves and the other makers. 52. **Part 3** (L; built 5 November 2026):
    the 14 states and levels breaking into other kinds. Merge after 52.
53. **Block 16: loose ends.** 53. **Boss fights: what is left** (L; built 5 November 2026). 54. **Dungeons: what is left**
    (M; built 5 November 2026): the entrance part of the fixed plans, each people flavouring a theme room. Merge after 54.
    All 54 rounds are built (see `docs/built.md`).
55. **Block 17: the makers in the editor** (approved 5 November 2026, thread "Generatoren in de editor gebruiken").
    55. **Makers in the editor** (XL; built 5 November 2026, see `docs/built.md`), with the maker area.
    56. **A window that fits** (M; built 5 November 2026, see `docs/built.md`).
57. **Block 18: the bar of seven keys** (approved 6 November 2026, thread "Skillsysteem met 6 toetsen beoordelen").
    57a. **The balance measure** (M) first, so the numbers are set before the bar changes. 57b. **The bar of seven
    keys** (L). Both built 6 November 2026 (see `docs/built.md`).
58. **Block 19: The Counted Sky and the peoples' books** (approved 6 November 2026, thread "Lore uit The Counted Sky
    en volksboeken"). 58a. **The Varnish lore made even** (M, mostly text). 58b. **The peoples' books** (L).
    58c. **The story on the land** (M). All three built 6 November 2026 (see `docs/built.md`).
59. **Block 20: games at the inn** (approved 6 November 2026, thread "Thematische minigames bedenken"; the Dutch
    proposal: project files `minigames/voorstel.md`). 59a. **Bones** (S/M). 59b. **Vigil** (M/L). 59c. **The Count** (S).
    All three built 6 November 2026 (see `docs/built.md`).
60. **Block 21: the Tests page grows** (approved 6 November 2026, thread "Testchecklist in debugmenu uitbreiden").
    60. **The Tests page grows** (M; built 13 November 2026, see `docs/built.md`).
61. **Block 22: the 10 November proposals** (Nilio, 13 November 2026: build all of the plan without waiting; the
    order chosen by Claude): 61. **A first sight of a town** (M; built 13 November 2026, see `docs/built.md`).
    62. **The land tells, and an inn in every town** (M; built 13 November 2026). 63. **Heard, lit and seen** (L; built 13 November 2026), before the camps,
    whose sneaking it needs. 64. **A roof of your own** (XL). 65. **Camps on the road** (XL). 66. **Wars that feel like
    wars** (XL), with the field battle and magic in the wars.
No play build in between (Nilio, 2 November 2026): he plays when the last block, now 16, is built. After that: Multiplayer (parked).

---

---

## A roof of your own (approved 6 November 2026, not built)

Thread "Housing-systeem ontwerpen"; the Dutch proposal with mock screens: project files `huizen/voorstel.md`. A gold
sink: one system, "a home", a small map of your own with a fixed plan (walls, doors) and a floor you furnish. All on
`p.homes` (multiplayer rule). Prices are first guesses for the `money` check (level 10 keeps up to ~80s a day).
- **A town house.** In hamlets, towns, cities and the metropolis of every people, one to a few for sale, a `$` on
  the door; bump it, one choice (`EV.ask`), 4g (hamlet) to 40g (metropolis), cheaper in the poor quarter. Each
  people's own kind (a hill home, a room in the rock, a house in a tree), taken from the settlement's own map, so the
  settlement rules hold. Hearth tax each season, paid when you come in or left in a chest by the door; a year unpaid
  and the town sells it (half back, less the debt; your things wait at the town hall).
- **Building anywhere.** A builder's stake from a carpenter (2g); on the world map an open tile (no road, no
  settlement, not by a hostile camp). Stages, each coin, trade goods (timber, stone) and days of building while you
  are away: camp, hut 5g, cabin 12g, stone house 25g, holdfast 30g (a palisade round it, so the settlement rule
  holds), keep 60g (a small stone tower-keep: the castle you build yourself). The look follows the land (log cabin
  in woods, stone in hills, sod on the steppe, stilts in the marsh, clay in the desert, a longhouse in the north).
- **The risk.** Each week away a roll by the region's threat (`mercs.py`), the distance to road and town and your
  defences: theft from one chest, a broken piece (`%`, paid to mend), squatters (bandits, a beast, goblins: a small
  fight in your own home), fire in a drought, a flood by a river, snow on a northern roof, a roused tribe or a great
  evil. Told through the news ("A drover says smoke rose over the cabin by the Grey Fen."). Defences: a lock, the
  palisade, a dog, a caretaker hireling on a wage, snares (Cunning), a rune on the door (Arcane); never zero in the wild.
- **A seat.** The empty seat of a fallen lesser house (`:`) or an empty fort, bought from the baron when you are
  his knight or well known to his house (120-300g), then restored in stages like building. Owned, never ruled
  (Nilio, 6 November 2026: ruling is another game): no villagers, no dues, no host, no land round it. The baron may
  call on it in a war (a realm job); if he loses, the new lord may claim it or sell it back to you. It gives room for
  all your hirelings, a stable for your wagons, a trophy hall and a watch that mostly beats off raids; a steward and
  guards cost a daily wage.
- **Furnishing.** In your own home one first-time tip teaches the furnish key (to pick from the free keys when
  built): a cursor on the floor and what you own beside it; place, pick up, move. Every piece works with a bump or is
  decoration: bed (rest, tree points, "well rested"), chest and strongbox (storage, 10 or 20 things), weapon rack and
  armour stand (swap a set at once), bookshelf (your books and pages, read again), hearth (cooking, warmth),
  workbench, anvil, loom (the guild bench at home at enough rank), shrine (a small blessing once a day), herb bed
  (herbs grow over days), kennel and stable (your beast, your wagons), trophies, rugs, tapestries, plants, lamps.
  Comfort, one to three stars, from variety, a matching style and trophies, makes "well rested" last longer; a
  neighbour or a house-warming remarks on it. Each people sells its own style (human oak, dwarf stone, elven wood,
  halfling snug, orc hide), a set of one style is a star more; dyes from Needle and Loom colour a piece; rare pieces
  from the Fair of Skell, tombs, or a boss's unchosen named things. Furniture is delivered (a few days, a small fee)
  or carried.
- **Where it shows.** `⌂` in your colour in the Places layer; a journal tab Homes (each home, its state, its chests);
  the line under the map ("Your cabin. All quiet when you left."); a handbook chapter "A Roof of Your Own".
- **Not:** ruling, fast travel home, renting out (a source of coin), free wall building tile by tile.
- **First choices, Nilio may change them:** a home is never lost outright to the weekly roll (a stage back at worst;
  only a great evil may burn it to the stake); more than one home is allowed, each with its own upkeep.

## Camps on the road (approved 10 November 2026, not built)

The Dutch proposal and mock screens: project files `nextlevel/kampen.md`, `kamp_*.png`. Hosts and caravans already
walk the world map (`realms.march`, the wanderers); now they stop, and a camp is a place you can walk into.
- **A host's camp.** A host on the march camps from dusk to dawn; at the end of its march it becomes a siege camp
  before the seat for as long as the siege lasts. World map: a few tents `Λ` in the kingdom's colour, the banner `¶`
  and a fire; the line under the map ("The host of Varn camps here tonight."); the Realms layer. Its own small map:
  a ring of stakes, rows of tents `Λ`, in the evening a campfire `☼` for each pair of tents with a warm glow on the
  ground (a cold fire pit `o` by day), the marshal's tent and banner, the quartermaster's wagons, a smith, the
  wounded, horse lines, sentries at the gate.
  - As a friend (the king's knight, or well known to his house): sell to the quartermaster (war prices, as war
    trade), mend at the smith, be healed for a small gift, hear the war's news, sign on for the battle (the realm job
    there is, modest pay). As a stranger: a sentry stops you; a small gift or a good word lets you to the
    quartermaster only. As a foe: sneak in by night (noise and light count): steal the orders, burn the stores or
    free prisoners, each weakening that host in its battle; seen, the whole camp wakes.
  - Gone by morning; blackened fire rings and trampled ground stay a few weeks.
- **A traders' camp.** A caravan that cannot reach a caravanserai camps by the road at night: wagons `Θ` in a ring
  round a fire. Trade at a fair price (far goods from its town), hear the road's news (safe ways, where prices are
  high), travel with them next day (the escort job there is), sleep safer by their fire. Robbers sometimes come in
  the night: help and the trader remembers you (a better price).
- Later, the same frame: pilgrims to a feast, herders to the summer pastures, a lord's hunting camp.
- What you are to a camp lives on the player. Handbook: the realms and the trade chapters. Test part `camps`.
- **Each people camps its own way** (mock: project files `nextlevel/legers/kampen_per_volk.png` and
  `kampen_wereldkaart.png`, made by `legers_mock.py`). World map by night and the camp's own map:
  - *A kingdom's host*: as above; a priest's tent `†` and, in a big host, a battle mage; siege engines `Ψ` in a siege
    camp. On the world map tents `Λ` in rows with a fire between each pair and the banner; a siege camp's tents close
    round the seat, with an engine `Ψ` beside them.
  - *A dwarf hammer band*: a square of stacked stone and shields `▓` with a ditch round it, low tents `∩` in a tight
    grid, braziers `¤` at the corners and one field forge in the middle, ale, war carts, ponies; no open fires and a
    watch that never sleeps: the hardest camp to sneak into. World map: `∩` inside `▓` with the forge's glow.
  - *An elven war-band*: no ring, no rows, no fires: bowers `∩` in moonlit clearings under the trees, sentries up in
    them, the warden and a moon-well. World map: nothing at all; from one cell away a pale `∩` under the trees.
  - *The Gorvash*: a sprawl with no ring, hide tents `Λ` every way round one great fire, the skull pole `¥`, war drums
    (seen, as in "Heard, lit and seen"), wolf pens and cages of captives; easy to walk into, many awake round the fire.
    World map: scattered `Λ` round a big fire and the pole.
  - *Sea raiders*: the longships drawn up on the strand are the wall, a ring of shields `o` round the mead fire, the
    jarl, the plunder heap and captives; gone with the tide at dawn. World map: ships `▬` on the strand and a fire.
  - *Riders* (steppe and desert riders, canyon riders, the clans on horse): round tents `Ω` in a ring round the fire,
    the herd outside, riders circling; no wall, gone at dawn. World map: `Ω` in a ring and the herd `h`.
  - The smaller raiding peoples (ice raiders, pass clans, wreckers, mist folk, island voyagers) camp in the frame of
    the nearest of these (sledges for ships, a stone hall's ring for a shield ring), dressed in their own colour.
- **You walk into the tents** (mock: `nextlevel/legers/kamp_tenten.png`, `tenten_per_volk.png`, made by
  `tenten_mock.py`). Every tent is a small room on the camp's own map, with cloth walls in the realm's colour and a
  flap `'` for a door; no new screen. Soldiers' tents: two bedrolls, packs, sleepers by night. The marshal's
  pavilion: the map table `π` with the orders on it, his chest, his bed, the banner at the flap with two guards. The
  stores (crates, ale, flour), the wounded on cots with a healer, the chapel (priest, holy banner), the prisoners'
  pen with a guard. Each people's own: the dwarves' stone-weighted hide with bunks in two tiers and a brazier; the
  riders' round tent with rugs, the hearth in the middle and the chest across from the door; the Gorvash's hides on
  poles with furs, bones and the loot sack; the elves' roof of woven leaves with no walls; the sea raiders' sail
  stretched from a ship's side over the oars. By night a lamp or the hearth lights a tent from within; sleepers wake
  at a noise; a chest, the orders or a prisoner can be taken; a tent can be set burning.

## Wars that feel like wars (approved 10 November 2026, not built)

The Dutch proposal: project files `nextlevel/legers/legers.md`. Today a war sends one host `K` at a time to one seat
and one roll settles it (`realms.war_month`, `march`, `arrive`). A war should feel like a war, but the sums behind it
stay small: the player is one adventurer, and what counts is what they see on the map and can touch.
- **More forces, both sides.** Each side has two to four: the king's host (marshal, banner, a priest, in a big one a
  battle mage) and smaller hosts of the border barons in their own houses' colours. The defender marches out too:
  where two hosts meet on the world map, the battle is there, in the field. Between them small parties: raiders `k`
  burning border villages, foragers, messengers and scouts; each can be caught or helped. At most about eight war
  signs per war on the map at once.
- **A front.** The border baronies are where the war is: camps, battlefields, burnt villages (the land tells: black
  smoke), refugees on the roads. Further off the war shows only in prices and news.
- **Raids and sieges, few battles.** Most of a war is raiding (to shame the other lord) and sieges; a battle in the
  field is rare and therefore big. A siege lasts days to weeks: the seat's stores run down, food can be smuggled in,
  the garrison sallies, the engines make a breach, and then the storm.
- **Seasons.** Hosts march from spring to the harvest; in winter they go home and the war is quiet (the seasons that
  are there already). Raiders keep their own months (`powers.KINDS`).
- **Levies go home.** A baron's men serve for a while, then go home to the harvest unless the king pays sellswords
  (the mercenary companies that are there). Hunger and sickness thin a host that sits too long in one place or eats
  a land bare. A host shrinks with every fight and must go home to fill up, or melts away into deserters, who become
  robbers on the roads. So a war is a matter of wearing down, not one roll.
- **Ransom.** A knight or lord taken in battle is worth coin: catch one, or buy or free one, as a realm job.
- **The peace.** As in Crusader Kings: taken seats, won battles and captured lords make the war's score; whoever has
  enough forces the peace (the tribute, hostage or land in `end_war`).
- **The fantasy in it.** A battle mage or priest with the king's host: take him out and the host weighs much less. A
  holy banner or relic goes with a host: steal it or save it. The great evils feed on war (their levers on the realms
  are there); on a battlefield in the Lich's land the dead rise by night. Other peoples take part: dwarves hire out a
  hammer band, and the Gorvash smell weakness and fall on a worn-out border.
- **Each people wars its own way**, and camps its own way (above, in Camps on the road):
  - *Kingdoms*: levies and knights, raids and sieges, ransom, the peace treaty.
  - *Dwarves*: slow; never raid, never march far from the hills; the best at sieges (they dig under walls); a debt in
    the grudge book is paid in full and then they go home.
  - *Elves*: never besiege and never hold land; ambush in the wood and on its edge, then vanish; they fight only for
    the wood (its edge, a felled grove).
  - *The Gorvash*: one great march that grows as it wins (beaten tribes join) and burns everything; when the warlord
    dies it falls apart into tribes again.
  - *Sea raiders*: strike the coast in their months from the sea, burn and leave by ship; no sieges.
  - *Riders*: fast raids deep into the land, never a siege, gone before a host can come; their herds are their wealth.
- **For the player**: catch or guard a raiding party; carry a message through the front; smuggle food into a besieged
  seat or open its postern; sneak into a camp by night (orders, stores, prisoners, the banner, the mage); take a lord
  for ransom; stand in the line in a field battle as one man in the press (your corner of the fight: hold the flank,
  save the banner, cut down a captain; see The field battle below). Pay
  stays modest; war raises prices (war trade), and what is taken from the field goes through the fence that is there.
- The war's state lives on the world (`R.wars`); what you did in it (signed on, known to a camp, a captive you hold)
  on the player. The Realms layer [4] shows the hosts, camps, sieges and the front. Handbook: the realms chapter
  (war, sieges, ransom, the peoples' ways of war). Test part `wars`.
- **The field battle** (approved 13 November 2026). At most one per war, so it stays a big moment. Its own zone
  map: two lines across the whole width, you in one corner of yours. Real soldiers fight only near you; further off
  the battle is a shifting front line of signs, so it looks big and stays light. Three phases of a few hundred turns
  each: the arrows, the clash, the rout of the side that breaks. At the start your captain gives you one task: hold
  the flank, save the banner, cut down their captain or take out their mage; or you just fight. The outcome stays
  honest: the hosts' strength decides, and your task weighs at most about 15%: a strong host mostly wins anyway, and
  a task done well only saves a battle on a knife's edge. The news tells what you did, also when your side lost.
  Getting out: you can always walk off the map's edge, but your lord remembers you left; if your side breaks, the
  rout begins and riders chase you to the edge. Death is as everywhere in the game.
- **Magic in the wars** (approved 13 November 2026). Rare and dear, but plain to see when it is there. A big host has
  one or two mages at most, behind the line with a bodyguard; a small host none. A priest blesses and heals, never
  strikes. On the battlefield each school does what its map rule does: fire sets a stretch of the front burning,
  frost draws an ice wall across a flank, storm strikes in rain or by water, nature lays roots and thorns, necromancy
  raises the day's dead. A mage counts in his host's strength; take him out and that is gone (the task "take out
  their mage"). Each people its own: kingdoms a court mage from a tower or guild, and the Church's priests; dwarves
  no mages but rune-smiths (runes on shields and gates make their sieges and camps tougher still); elves the Circle's
  druids (roots, thorns, mist in the wood); the Gorvash shamans (curses, the drums); sea raiders a storm-caller who
  gives their ships the wind; riders a wind-singer or a beast-master. Necromancy is forbidden: who uses it in a war
  stirs the Church and the great evils. If you are a mage, your captain gives you a mage's task (meet their mage, or
  break the front), pay a little higher, and their archers look for you first. In the camp the mage has a tent of
  his own with books and reagents: something to steal, kept modest (the loot rule).

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

## The look rule (Nilio, 31 October 2026)

Prettier means using what is on the screen better, never adding to it:
- **Three layers of brightness.** Ground and rock stay dim, built things and walls in the middle, and only what lives
  or can be used is bright: creatures, items, doors, stairs, places.
- **An accent colour has one meaning.** Gold is something for you (money, jobs, places, what matters in the log), red
  is danger; the orbs' red, ochre and blue belong to life, stamina and mana. The ground does not borrow them.
- **Movement is scarce.** Only what really moves (fire, water, spell effects); no blinking or glinting as decoration.

---

---

## Parked
- **Multiplayer**: see docs/parked.md.
- **The bard** (the Lark's Company): see docs/parked.md. Not until Nilio says so.

## Later (not planned yet)
- Leadership: more hirelings, a group buff.
- World ideas proposed with round 5 but not chosen: the world growing (new hamlets, logging, regrowth),
  lighthouses and watchtowers lit at night (smoke, birds, vultures and worn paths were built in round 62).
