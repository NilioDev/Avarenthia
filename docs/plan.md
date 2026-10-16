# The plan: rounds 1 to 5

Agreed with Nilio on 15 October 2026; the other jobs and the bard parked on 16 October (docs/parked.md); the jobs
brought back as round 4 the same day, at his request. The bard stays parked. Round 5 (seasons, a livelier world, sailing) agreed on 16 October.
Build the rounds in order; after each round: tests (seeds 1-3, smoke),
push (CI builds), a short Dutch report. Then go on with the next round. He plays afterwards and sends feedback.

Inspiration: Shadowdark (core book, Western Reaches, Cursed Scrolls 1-6), D&D, Pathfinder, Diablo, Final Fantasy,
WoW. Take the ideas, never the text, stat blocks or invented names.

---

## Round 1: behaviours, spiders, insects, humanoids with classes, named enemies

### New behaviours (building blocks for monsters)
Every new monster has one or two of these, so each asks something different of the player. Dangerous moves are
always announced a turn ahead (as the charge is now).
- **grab / web**: you are held (cannot move) until you break free (a strength roll each turn); bites on you hit.
  Web is a ranged shot that holds.
- **paralyse**: at most 1-2 turns, then a few turns of immunity.
- **swarm**: one cell, many hit points, half damage from weapons, double from fire and area spells.
- **acid / metal-eater**: damages the durability of your gear (armour on a hit, weapon when you hit it).
- **burrow / ambush**: hidden under the ground until you come close.
- **leap**, **knockback**, **phase** (only hittable while solid, flickers in and out).
- **formation**: stronger (defence, accuracy) next to an ally of its kind.
- **totem**: a shaman plants a totem that heals or hastes its group; break the totem.
- **curse**: weaker damage or healing for a while.
- **darkness**: a spell cloud; inside it you see almost nothing for a few turns (a status, not light management).
- **sunblind**: creatures from below fight worse outside by day.
- **greedy**: steals something shiny and runs; chase it.
- **spawn / split**: bursts into smaller ones when it dies.
- **leader**: a buff on its group; when it falls the group may break and run.
- **disease**: no natural regeneration until cured or it passes.
- **eats food**: locusts eat food from your pack.
- New statuses for the player: held, paralysed, slowed, confused, afraid, blinded (darkness), diseased, cursed.

### Families in round 1
Keep one letter per family (`s` spiders...), colour per kind; female/male per individual where it fits.
- **Spiders**: Wolf Spider (fast, hunts, no web), Trapdoor Spider (burrow, grab), Web Weaver (shoots web, keeps
  distance), Jumping Spider (leap), Spider Swarm, Phase Spider, Frost Spider (slows), Ember Spider (in the dragon's
  scorched lair), Brood Spider (bursts into spiderlings), Webkin (spiderfolk: web and venom), Spider Matriarch (boss,
  always female).
- **Insects and crawlers**: Giant Ant Worker (swarm) / Soldier (acid bite) / Queen (spawns, boss; ant nest dungeon);
  Fire Beetle (glows, purely to look at), Bombardier Beetle (acid cloud), Horn Beetle (knockback), Rust Beetle (eats
  gear); Bloodwasp and a Wasp Queen; Giant Mantis (unseen until it strikes); Giant Centipede and Cave Crawler
  (paralyse); Centipede Swarm; Sand Scorpion and Giant Scorpion (grab and sting); Locust Swarm (eats your food);
  Needlewing (drinks blood, latches on); Tunnel Borer (burrows, spits acid on armour); Mire Leech; Blood Tick (disease);
  Dustwing Moth (dust: everyone near loses some life).
- **Humanoids with classes** (groups with a leader):
  - Goblin: Sneak (backstab), Archer (exists), Bomber (thrown fire pot, area), Shaman (stink bomb, climbs), Wolf Rider,
    Boss.
  - Kobold: Slinger, Trapper (lays traps in corridors), Sorcerer (calls a spider swarm), Dragon Priest, Chief.
  - Orc: Brute (exists), Berserker (rage), Spearthrower, Shaman (totems: bloodlust, healing), Warlock (curse, shadow
    fire), Warlord (exists); Deep Orc (underground, sunblind).
  - Hobgoblin: Legionary (formation), Archer, Captain (also usable as faction troops).
  - Gnoll: Hunter, Packlord, Bone-caller (calls hyenas); Hyena.
  - Lizardfolk: Warrior, Spearthrower, Swamp Shaman; crocodiles with them.
  - Underground: Grey Dwarf (enlarge, invisibility), Shade Elf (sleep darts), Shade Priestess (darkness), Weaver-born
    (half spider, half shade elf), Sporeling (mushroom folk, spore cloud).
  - Viperkin in desert ruins: warrior, sorcerer, a giant snake-torsoed one.
- **New dungeons**: ant nest, spider lair, goblin warren, orc camp (overworld site with a wild map), snake ruin.
- Place every monster by biome, depth, dungeon type or evil lair. No new loot rules: only gear users drop gear;
  beasts give meat and hides at most.

### Descriptions and gender
- Three layers, unlocked with bestiary knowledge: (1) what you see (always, per individual, gendered: "A hunched orc
  woman draped in finger bones, a smouldering totem on her back."), (2) what they do (after a few kills), (3) weakness
  and where they live (more knowledge).
- Gender per individual for humanoids, beasts and many monsters: pronouns in messages ("lights her fuse"), the
  description, the names of leaders. Fixed where it adds colour: matriarchs and queens, sea hags, banshees female;
  mammoth herds led by an old cow. Oozes, constructs, swarms, skeletons and true aberrations stay "it".

### Named enemies
- Built from: name (fits people and gender) and epithet ("the Widow of Blackmere", "Old Snagjaw"); family, class,
  gender; rank: **notable** (one trait), **notorious** (2-3 traits and a following), **legendary** (rare, own lair,
  own loot); traits from a long Diablo-like list (Venomous, Frost-touched, Fire-blooded, Stone Skin, Thorny, Vampiric,
  Regenerating, Swift, Blink, Summoner, Splitting, Multishot, Berserk at low life, Shielded, Cursing, Warcry aura...);
  following by type (orc shaman with brutes and an archer; alpha wolf with pack; matriarch with brood; necromancer with
  dead; aberrations and big beasts alone); behaviour (territorial, roaming, raider of caravans and villages: makes news
  and moves prices, ambusher on one road, nocturnal); one or two looks (broken tusk, brand scar, bone armour); a past
  ("burned the mill at Ashwick"); a weakness you can hear about ("hates fire"); a trophy (head, ear, fang); loot only
  what it uses, always something special for legendary ones; **fame**: left alone too long it grows (a trait or more
  followers) and its bounty rises.
- Also met at random in the world, without a job. Kill first, find the poster later: the trophy can be handed in
  wherever there is a bounty on it.
- **Fleeing and grudges**: a named enemy losing badly flees to its lair to heal, leaving a fresh blood trail. It comes
  back with a scar and a new epithet ("the Scarred"), knows your name, calls it out, and sometimes comes for you on the
  road. If it kills you (softcore) it grows ("Slayer of ...") and keeps a piece of your gear; kill it to get it back.

### Hunting them (no live marker)
- The job gives a **search area** on the world map (hatched), not a dot: "last seen near the Blackmere, three days
  ago". Small for territorial ones, larger for roamers, and it grows as the report ages (news travels slowly). New
  rumours from captains and travellers shrink it again.
- Walking inside the area you sometimes find **signs** (tracks, a torn deer, a burnt cart, shed scales, webs in the
  trees). Each sign shrinks and moves the area and tells direction and freshness ("heading north-east, a day old").
  Foraging rank (or a Tracking skill) and the Wardens help. Rain washes tracks away, fresh snow shows them; nocturnal
  ones are found by night.
- Close enough: an encounter (you surprise it, or an ambusher surprises you). Its name shows in the panel only once
  you see it. In a dungeon the job names the level; signs on the way (blood trail, fresh webs, gnawed bones); marked
  only once seen.
- Journal: name, description, past, last seen, traits you have seen, reward. Rewards stay modest (coin, standing in
  the town, guild standing, the trophy, sometimes a special piece).
- Givers: the captain (raiders, orcs, beasts near villages), "WANTED" posters on the boards, and the guilds, each on
  its own prey; higher guild rank, more dangerous and better paid hunts: Wardens (beasts), Order of Dawn (undead,
  Morrak's spawn), Iron Company (warlords and gangs), Magi (aberrations and sorcerers), Thieves (rival gang bosses),
  Coven (paladins). Chains as in an MMO: first his lieutenants, then where the boss hides.

---

## Round 2: the other monsters and aberrations

- **Undead**: Ghoul (paralyses) and a Ghast leader, Skeleton Warrior with shield, Skeleton Mage, Barrow Draugr (walks
  through walls), Banshee (fear wail), Mummy (disease, desert), Shade (drains strength), Wight, Vampire Spawn.
- **Beasts by biome**: bears, Boar (charge), Panther (stalks), Snow Ape and Mammoth (north), Sabretooth, Worg, Winter
  Wolf (frost breath), Giant Frog (tongue pulls you in), Crocodile, Constrictor (grab), Cobra, Vulture, Giant Badger,
  Rhino, Giant Crab, Clawbeak (owl-headed bear), Shimmercat (shifting image).
- **Oozes and plants**: Grey Ooze (eats metal), Black Pudding (splits), Glass Jelly (see-through, engulfs), Rot Flower
  (sleep pollen, does not move), Violet Creeper, Shrieker (a mushroom that screams everything awake), Strangling Vine.
- **Water and coast**: Crabfolk, Brinefolk (sea devils), Merrow, Sea Hag, Giant Octopus (grabs from the quay).
- **Constructs**: Animated Armour, Varnish Guardian (in the vaults), Gargoyle (a statue until you are close), Mimic (a
  chest), Clay Golem.
- **Morrak's spawn** (Hollow Coven): Imp (invisible), Hollow Spawn (stench), Hellhound, Hungering Shade.
- **Fey and wood**: Pixie (charms), Dryad, Will-o'-Wisp, Weald Hag, Scarecrow.
- **Dragons and legend beasts**: Wyvern (venom tail), Swamp Drake, Frost Drake, Basilisk (stiffens you), Cockatrice,
  Manticore (spikes at range), Chimera.
- **Aberrations (own names)**: Skullsipper (brain eater), Gibberflesh (babbling mass, confusion), Stonemaw (a
  stalagmite that bites), Gloomwing (a cloak in the dark that makes illusions), The Staring Dark (many eyes; rare,
  boss), Rustgnawer (eats metal), Midden Maw (lives in filth, disease), Gloomdigger (burrows, its gaze dazes), Pincer
  Horror, Burrowback (swims through the ground), The Deep Mother (ancient fish telepath; boss), Starspawn.
- **Bosses per family**: Spider Matriarch, Ant Queen, Goblin King, Kobold Dragon Priest, Gnoll Packlord, Ghast Lord...

---

## Round 3: five new combat guilds

The limit of two combat guilds stays. Crafts guilds (smith, herbalist, tanner) come later, not now.

| Guild | Archetype | Discipline | Techniques | Halls | Rivals |
|---|---|---|---|---|---|
| **The Green Moot** (Thessa) | druid and shaman | new: Nature | Entangle (roots hold), Spirit Totem (heals you and your hireling), Wild Shape (bear or wolf for a while) | groves in forest villages, by the standing stones | Coven, Ossuary |
| **The Hallowed Chapter** (Solmara) | priest and healer, no sword | Healing | Mass Mend, Sanctuary (enemies cannot attack for a few turns), Rite of Return (raise your hireling in the field) | great temples in the cities; cheaper healing and raising | Coven, Ossuary |
| **The Quiet Ossuary** (half secret) | necromancer | new: Necromancy | Raise Dead (a slain enemy fights for you a while), Bone Armour, Corpse Burst | found through old graveyards along the Varnish ways; tolerated by the dwarves (Durnak is god of the dead), hunted by the Crown and the Dawn; grave-robbing jobs, standing lost when it comes out | Dawn, Chapter, Moot |
| **The Order of the Still Hand** | monk | Unarmed | Flurry, Stone Stance (less damage, slower), Pressure Point (one enemy stunned a turn), Wind Step (a few cells at once); stronger without heavy armour | the monasteries | none |
| **The Houndwardens' Lodge** | beastmaster | new: Beastcraft | Tame (a wolf, bear, panther or hawk in the wild), Call of the Pack, Pack Fury | hunting lodges in hill villages, beside the Wardens | none |

- The tamed beast follows the hireling rules (orders on `h`, threat, death and raising); it eats meat, no wage.
  A beastmaster may have a beast **and** a hireling. (Leadership, for more, comes later.)
- Two-guild techniques: Moot + Wardens: Wildheart (hunt in beast shape); Ossuary + Coven: Lichcraft (dark, costs
  life); Still Hand + Dawn: Mendicant (holy fists);
  Houndwardens + Iron: War-handler (war dogs).
- Each new discipline needs about five to eight skills from tomes besides the three master techniques.

---

## Round 4: the jobs (back from docs/parked.md)

### Village work, and the frame for choices
- **Clear a nest** (spider or ant nest; village elder / innkeeper), **Defend** (a raid is coming to a village),
  **Rescue a captive** (from an orc camp or a web), **Find the missing** (tracks, as with hunting; alive, wounded or
  dead), **Rival hunter** (another bounty hunter after the same prey: be faster, work together, or cross him).
- A frame for choices with consequences on: standing in a town, standing with a faction, a god's favour, guild rank,
  crime, a hireling's loyalty.
- Built: every village and hamlet has an elder with work (Berend stays Thornfield's own).

### Jobs that went with round 2
- The sick well (find what poisons a village well), Desecrated shrine, What took the boats (a harbour loses
  boats: sea hag, octopus or brinefolk), The big one (Brotherhood of the Net: a legendary fish, in one season or
  weather, with the fishing game), Map the deep (explore a dungeon to its bottom for a scholar).

### Jobs of trade, faith, crime and the calendar
- Trade: **Rush order** (a town hit by news needs medicine fast), **Debt collector** (pay it yourself, threaten, or let
  it go), **Recover stolen cargo** (from a bandit camp), **Smuggle past the gate** (Thieves).
- War and crime: **Spy** (look around an enemy fortress unrecognised), **Deserter** (hand him in: faction up, his
  village down; let him go: the reverse), **Clear your name** (find the real culprit instead of paying the fine).
- Faith: **Pilgrimage** (an offering to a far shrine), **Relic of the god** (from a ruined rival temple).
- Exploring: **Survey** (Cartographers: a place not yet on their map), **Lost way** (walk an old way to its end).
- Village: **Bad harvest** (boars, crows or worse), **Winter supplies** (autumn only: wood, meat or grain to a remote
  hamlet), **Escort a person** (a pilgrim or merchant who walks along and can die).
- Calendar: **The Starfall** (on the night of the Starfall a star lands somewhere; star-iron for whoever is first, and
  others are looking too), **The festival** (light-hearted; standing as the reward). Festivals: the Seedwake Fair,
  Midsummer, Harvest Home, the Longnight Vigil.
- Company: **A sellsword's debt** (help your hireling with an old debt: more loyalty).
- Givers: village elder and innkeeper (village jobs, standing in the village), captain, factor of the Merchants' Guild,
  temple, and the guilds by rank:

| Guild | Low rank | High rank |
|---|---|---|
| Wardens | bad harvest, find the missing | legendary beast hunts, rival hunter |
| Iron Company | escort, recover cargo | deserter, defend, warlord hunts |
| Order of Dawn | desecrated shrine | relic of the god, ghast lords and Morrak's spawn |
| Magi | map the deep | aberration hunts, the Starfall (star-iron) |
| Cartographers | survey | lost way, maps of the deep |
| Brotherhood of the Net | the big one | what took the boats |
| Alembic and Barrel | gather for the alchemist | the sick well (find the cause) |
| Thieves' Guild | smuggle past the gate | debt collector (their way), rival gang bosses |
| Hollow Coven | desecrate a shrine | steal a relic of the god, paladins |

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

## Later (not in these rounds)
- Crafts guilds: smith and weaponsmith (mend and improve), herbalist, hunter-tanner (hides and trophies).
- Leadership: more hirelings, a group buff. A house of your own, with taxes.
