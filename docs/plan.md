# The plan: rounds 1 to 3

Agreed with Nilio on 15 October 2026; the other jobs and the bard parked on 16 October (docs/parked.md).
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

## Later (not in these rounds)
- Crafts guilds: smith and weaponsmith (mend and improve), herbalist, hunter-tanner (hides and trophies).
- Leadership: more hirelings, a group buff. A house of your own, with taxes. Sailing.
