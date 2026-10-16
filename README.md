# Avarenthia
### *Tales of Fortune, Fame and Folly*

An ASCII open-world RPG in Python, built on [python-tcod](https://python-tcod.readthedocs.io/) (libtcod).
A game by **Nilio**.

You wake in a temple outside Thornfield with no memory and no name worth mentioning. Around you lies a random
open world: fast combat, trade between hamlets and cities, factions at war, jobs on the notice boards, caravans,
patrols, bandits and travellers moving visibly across the land, weather rolling in from the hills, and great evils
growing quietly in the background while you are busy elsewhere.

## The world

**Avarenthia, 1172 After the Ruin.** Once the Varnish Empire ruled everything from the Sky-Seat; then came the Ruin,
and what is left are broken roads, old ruins and young kingdoms quarrelling over the pieces. The history, the gods and
the peoples are told by the people you meet, a little at a time, and in the help pages.

**One continent, a frozen north, islands out at sea.** Every world is made the way Dwarf Fortress makes its
worlds: mountains rise in long chains, wet winds blow in from the western sea and drop their rain where the land
climbs, so the land behind a range lies dry; the climate runs from the polar ice and pack ice of the north through
tundra, taiga and the temperate woods and grasslands to savanna, desert and jungle in the far south. Rain gathers
into real river systems with tributaries and lakes. The overworld is drawn in the calm style of the DF world map:
black ground and one clear glyph per biome (`♣` broadleaf, `♠` pine, `↑` taiga, `"` grass, `n` hills, `▲`
mountains, `~` desert, `·` tundra, `═║` rivers). Roads are joined ochre lines: the great roads between the cities
double (`═║╔`), the others single (`─│┌`), with bridges (`╪`) where they cross a river.

**Wonders.** Each world has its rare sights, one of each at most and always where they belong: Starfall Crater, the
Elder Tree, the Sundering, the White Waste, the Sea of Sand, the Steaming Fields, the Glass Hills, the Stone Wood, the
Black Mire, the Glimmering, the Fjords, the Ashen Scar, the Burning Isle, the Wyrm's Bones in the desert, and far out
in the warm southern sea the Sky-Seat: a shard of the fallen Varnish capital still hanging in the air over a
maelstrom, ringed by drowned towers and by a coral atoll that the currents have torn open on one side. It lies so far
out that nobody on land can see it, not even from a watchtower; the sailors in the harbours talk about it. People talk about them; the first
time you see one, you will know.

**You learn the world by travelling.** At the start you know nothing but where Thornfield lies; you see only what is
around you. In the open you see about four tiles, further from hills, little in forest and marsh, and half as far at
night. Signposts (`┬`) tell you where the roads go, and rumours tell you where a place lies, but the road and the land
in between only appear on your map once you have walked them. From the top of a watchtower you see about ten tiles
around, but not past mountains.

**Travel.** Once you have been somewhere you can travel there again, from the world map: `m`, then Tab (or
Shift+Tab) picks one of the places you have been, the map shows the way there and how long it takes, and Enter sets
out. You walk to the nearest road, follow the roads and cross the last stretch over open land, step by step, while
time, hunger and the weather go on. An enemy in sight, a traveller on the road, an event, hunger or wounds stop you,
and so does any key. In a town, `m` first shows the plan of the town, with every building lettered and named; Tab
goes on to the realm.

**The old ways.** Under the moss lie the paths of the Varnish Empire, hidden until you find them, and even then you
only know what you have seen. Walk onto one and you see the stretch in sight; the rest you walk. A rumour tells you
only where one starts; an old map from a ruin or a chart from the Cartographers' Society shows a stretch of it, never
where it ends; from a watchtower you see as much as you can see; a milestone only points. They show as a faint,
broken grey-green line. They are faster than open land and slower than a road, and nobody patrols them.
Some are shortcuts (passes over the mountains, causeways through the marsh); some lead to hidden things (Varnish
waystations where you can rest safely, forgotten graveyards, a smugglers' den, lost ruins, and sealed vaults that open
only to the old word); and some lead over a pass into a hidden valley, where a forgotten hamlet lives as it did when
the Empire fell: a handful of huts on old terraces, goats, no inn and no market, people who speak the old way and
trade but do not sell, and an elder who knows more than the books. Milestones along the ways point to the other
secrets: the paths are what is left of one network.

**News travels on foot.** What happens in the world is not shouted at you: it is told in the inns, a few days late,
by those whose business it is. The innkeeper has the local gossip (and small jobs on the board); the factor of the
Merchants' Guild has trade work and talk of prices on the roads near here; the captain of the garrison knows where
the trouble is and pays bounties; a travelling merchant tells you what sold where when he came through; travellers and
sailors bring word from far away. News moves about twenty-five leagues a day, so what you hear of a far place is old,
and may no longer be true.

**Listen to people.** Everyone has something to say, and an attentive player picks up hints: an overgrown shrine past
the old mill, a ruin two days east, herbs that grow by the lake, a war going badly in the north, prices rising in the
capital, strange lights in the marsh. Some of it is idle talk; some of it points to hidden places, and some of it
tells you how the world is faring. The last few things you heard are kept in your journal under *Heard on the road*.

**Settlements come in five sizes**: hamlet, village, town, city and metropolis.
A hamlet is a few houses along the road where the farmer sells from his kitchen; a village has a green, a town a paved
market square with a fountain; cities and the metropolis are walled with gates. The roads inside a settlement run
exactly as on the world map: if a village sits at the end of a road, the road ends there too, and you enter by the road
you came on. Along the roads lie farms (where you are often welcome at the table) and the odd lonely roadside inn.
Outside the villages stand temples, monasteries and watchtowers, and the ruins of them, with a way down.
Every building has a hanging sign by its door (`¡` inn, `¥` outfitter, `†` temple...) and every inn its own name; walk
close and the name shows outside the building. Settlements on the coast have a **harbour** that fits their size: a
short jetty and boats drawn up on the beach in a hamlet; two jetties, a boathouse and drying racks in a village; a
stone quay at the head of a cove with three piers and a warehouse in a town; a straight quay with a deep berth, a big
ship, a crane, a fish market under awnings, a customs house and a harbour wall with a beacon in a city; two basins, a
lighthouse, a shipyard and ships everywhere in the metropolis. In a fjord there is no beach: a ledge on the rock, a
tiny jetty, or nothing. There is no sailing yet.

**Dwarven holds.** In the mountains lie underground dwarven cities (`▼`) with halls, forges, a throne room and stairs
down to the Deep Roads, old dwarven tunnels now full of goblins and worse.

**Sleeping out.** Rest in the open and you make camp: with a fire the beasts keep off, but robbers see it from
afar; without one, it is the other way round. A night out can bring wolves, robbers, a thief at your pack or a cold
wet night without sleep; a tent helps, a hireling keeps watch, and a Varnish waystation is safe. A bed at an inn costs
coin and leaves you *well rested*.

**Weather.** Every region has its own climate that changes with the seasons and moves in steps: drizzle turns to rain
turns to a downpour. Over thirty kinds of weather, from mist, fog and snow to blizzards, sandstorms, haboobs, freezing
rain, hail, falling leaves and blossom. The north and the mountains are cold, the south hot and dry, marshes misty.
Rain, snow, fog and dust limit your sight; snow and storms slow you down; cold and heat make you hungry; fire sputters
in the rain, and lightning strikes open ground. Ash rain, miasma and smoke betray a great evil nearby. Under a roof you
stay dry. Rain leaves puddles that grow while it pours and dry up after. On a clear night a star falls now and then;
once a year, on the night of the 12th of Emberwane, the sky rains them: the Starfall.

**Light and dark.** Torches, campfires, crystals and glowing mushrooms flicker and pulse. Towns have street lamps: at
dusk the lamplighter makes his round and lights them one by one, and at dawn he puts them out again. At night you see
the lit streets from afar; the rest is dark.

**The calendar.** Twelve months of thirty days (Deepfrost to Longnight) and a seven-day week; the story begins on
Stonesday, the 3rd of Seedwake, 1172 AR.

## Your hero

When you start a new game you choose your people (human, elf, dwarf, halfling, gnome, half-orc or goblin), your gender
and your name; Tab gives you a random name that suits your people. Each people has its own attributes, strengths and
weaknesses, and other peoples and factions treat you differently: other prices, another starting reputation.

You start with nothing: kobolds took your sword and shield to the Hollow Den. Until you get them back you fight with
your fists. Their chief Snagtooth also keeps your first spellbook. You are nobody; what you become is up to you.

Choose **hardcore** (death is final) or **softcore**: the priests of the nearest temple raise you, for a fee from your
purse; your pack and cargo lie by your body until you fetch them, and you are weak for a day or two. If your purse
cannot pay the temple, your tale ends there, and with it your one save. Enter a **seed** to play the same world again.

### No classes

You become what you do. Fourteen disciplines (sword, axe and mace, dagger, bow, fire, ice, storm, healing, shadow,
warcraft, unarmed, nature, necromancy and beastcraft) grow by use. Skills (seventy of them) are learnt from **books** (`≡`): from monsters, deep in ruins, at standing
stones, from pedlars and sometimes at a city outfitter. Harder books ask for a higher discipline. You carry six skills
at a time and swap them in a town or castle. Weapon skills only work with the matching weapon in hand.

### Gear, in the manner of Diablo II

Ten slots: helm, amulet, armour, weapon, off-hand (a shield, or a grimoire for those who fight with magic), gloves,
belt, boots and two rings. Two-handed weapons (great swords and axes, mauls, staves and bows) leave the off-hand empty.
Every base item comes in three grades, **normal**, **exceptional** and **elite**, and asks for Strength or Dexterity.
The level of the place where it drops sets the item level, and with it the grade and the strength of its powers: a
wide pool of prefixes and suffixes in tiers with ranges, from enhanced damage and life to fire, cold, lightning and
poison resistance, added elemental damage, `+` to a discipline, light radius, damage against the undead, thorns,
life and mana after each kill and magic find. **Uniques** roll their powers within a range (the range is shown; a
perfect one has them all at the top) and come only from those who would carry them. Small **sets** of two to four
pieces, bound to a people or a place (the grave goods of a Varnish general, the harness of the Crown's border wardens),
give a bonus for two pieces and another for the whole set. How many things drop has not changed: beasts carry no
swords. No sockets, gems or runewords, and no weapon swap.

**Resistances.** Fire, cold, lightning and poison, at most 75%. Salamanders in the deserts, ice witches in the frozen
north, storm spirits on the hills and coasts and bog lurkers in the marshes attack with their element, and every kind
of monster resists some elements and fears others: you learn which by fighting them.

Magic items are rare and **unidentified** when found; their powers only work after an outfitter or priest identifies
them. Some are **cursed**: once worn, they will not come off until a priest lifts the curse.

### Guilds

Fight for at most **two** combat guilds; rivals will not have you both. The Circle of Magi, the Iron Company, the
Order of Dawn and the Wardens of the Wild keep halls in the cities and lodges in the woods. Two are secret: the
Thieves' Guild is found through rumours and chalk marks, or it finds you after a crime or two, and the Hollow Coven,
who serve Morrak and take a price in life, is found only through those who already know. The guilds of the crafts
(Alembic and Barrel, the Cartographers' Society, the Brotherhood of the Net) take anyone, and speed up the crafts they
keep. Each guild has five ranks, earned with its own jobs; only a guild master teaches the advanced techniques, to
those of high enough rank and discipline, and those who serve two guilds can learn a technique of both. The work of
the secret guilds has a dark side, and the world notices. Your standing fades slowly if you do nothing for a guild,
but never below your rank; the secret guilds let you fall. Leaving costs you your rank, and a secret guild sends
someone after you.

Five more combat guilds: **the Green Moot** (druids of Thessa, in groves in the forest villages: Entangle, Spirit
Totem, Wild Shape), **the Hallowed Chapter** (Solmara's healers in the great temples: Mass Mend, Hallowed Ground,
Rite of Return to raise your hireling in the field; its members pay less to have the fallen raised), **the Quiet
Ossuary** (half secret, found through the old graveyards on the Varnish ways: Raise Dead, Bone Armour, Corpse Burst;
its grave-robbing work costs you standing with the faithful when it comes out), **the Order of the Still Hand**
(monks in the hill monasteries, who fight better without heavy armour: Hundred Hands, Stone Stance, Pressure Point,
Wind Step) and **the Houndwardens' Lodge** (beastmasters in the hill villages: Tame, Call of the Pack, Pack Fury).
New two-guild techniques: Wildheart (Moot and Wardens), Lichcraft (Ossuary and Coven), Mendicant's Fist (Still Hand
and Dawn) and War-Handler (Houndwardens and Iron Company).

Membership costs nothing, and what you learn you keep if you leave. But members buy from the guild's
**quartermaster** at a discount that grows with their rank, sleep in the hall for little or nothing, have their gear
mended for less, and the higher their rank, the better paid the guild's work (and now and then there is a piece of
gear on top).

Each guild also has work of its own, and better work from the third rank: the Wardens a bad harvest and the missing,
then legendary beasts and hunts with a rival hunter after the same prey (race them, hunt together and split the
bounty, or make sure they never get there); the Iron Company escorts and stolen cargo, then deserters and raids; the
Order of Dawn desecrated shrines, then relics of the gods; the Magi the deep places mapped, then the Starfall; the
Cartographers surveys, then the old ways walked to their end and the deep places; the Brotherhood of the Net the big
one (a legendary fish that bites only in rain, at night or in one season, landed with the fishing game), then what
took the boats; Alembic and Barrel herbs, then the sick well; the Thieves smuggling past the gate, then debts
collected their way; the Hollow Coven a shrine to foul, then a relic to steal.

### Hirelings

In the barracks of the cities the Iron Company lets out sellswords by the day, and now and then one sits in an inn
between contracts. A **defender** (shield and sword: steps in front of you and takes blows meant for you, bashes with
his shield), a **warrior** (a two-handed weapon), an **archer** (never shoots through you), a **healer** or a
**mage**. A hireling costs a fee to sign, a daily wage and his food from your pack; short him either and his mood
sours, and in the end he walks. He carries four pieces of gear (weapon, armour, helm, shield) that wear like yours
and that you can swap for better from your pack, and he grows with you. `h` gives orders: follow, defend me, attack my
target, hold position, or stay out of it. He follows you down stairs and through towns, swaps places with you in a
corridor, drinks his own potions and never touches a neutral. Badly hurt, he may run, and come back when it is over.

Who the monsters go for is never shown, but it is not random: each remembers who hurt it lately and who healed whom,
who stands in its way, who looks soft (light armour, low on life), and how clever it is. A beast goes for the nearest
throat; a clever foe goes for the healer; an archer picks the weakest it can see; and none of them turns lightly on
whoever is hitting it hardest. In hardcore a fallen hireling is dead, and his gear lies with his body. In softcore a
temple raises him for a fee; when you fall, he falls with you.

A beastmaster can **tame** a wolf, bear, panther or hawk in the wild (easier when it is hurt) and keep it as well as
a hireling. A beast follows the same orders and rules, has no gear and takes no wage, but eats meat from your pack
once a day; go without and it goes back to the wild. Raised dead and called wolves are **thralls**: they fight at your
side for a while, then fall away.

### Life skills

Like in Project Gorgon, life skills grow by doing them: **fishing**, **foraging**, **herbalism**, **alchemy** and
**brewing**. Buy a fishing pole and fish by any water (`a`): fishing opens a window of its own, with the water, the
bank, you, the rod and the float. Wait for the bite (ripples are not bites) and strike in time; then reel in, keeping
the fish in the green with the arrows while the line holds. The better you get, the more kinds bite, the wider the
green and the longer the line holds; a master angler can take the quick way. Forage in the
wild for food and herbs. Plants you do not know look different in every world: taste them at your own risk, some are
deadly. A herb monk tells you what you found. Brew potions from herbs, and ale, berry wine and mead at an inn or in a
monastery cellar.

### Hunger

You use up food. Eat bread, rations, fish or meat, or have a hot meal at an inn (a bowl of stew, or a meal with a bed).
On a full stomach you last about a week; after a day or two you get hungry, then weak, then faint.

### Gods

A small pantheon: Solmara (light and mercy), Valdric (law, protector of the crown), Thessa (the wild), Durnak (forge
and stone, god of the dwarves), Skell (luck, roads, trade and thieves) and Morrak (death and hunger). In a temple you
can devote yourself to its god. Prayer, offerings and deeds your god likes earn favour, and with it blessings. But
factions that worship a rival god trust you less, and priests of a hostile god will not help you.

## Coin, trade and jobs

- **Coin is rare, and it goes.** Jobs pay modestly; trade is where the money is made. Coin goes on beds and meals,
  on mending your gear (it wears with use and breaks when worn out; outfitters mend it, a repair kit patches it up on
  the road), on a hireling's wage and on the temple.
- 100 copper is 1 silver, 100 silver is 1 gold. Beasts carry no money, people a little, traders a lot.
  Most coin is found in chests (`■`) in dungeons and ruins. Drops are realistic: beasts do not carry swords.
- Every place makes certain goods (`+`, cheap) and wants others (`!`, dear). Buy low and sell elsewhere. Prices react
  to what you and the caravans buy and sell, and recover slowly. News (famine, feast, mine disaster, fire, war,
  plague) shifts prices for a few days.
- You carry 30 units of cargo; a mule (+60) and a cart (+160) are sold by the stablemaster.
- The inn's notice board has courier jobs, freight runs, bounties, escorts, dungeon delves and WANTED posters for named
  enemies (see *Named enemies*). A blinking yellow `!`
  above someone means work; a `?` means you can hand something in.
- **More work, and who gives it.** The innkeeper and the elder of a village need a nest of ants or spiders cleared,
  boars or worse driven off the fields, someone found who went into the woods and did not come back (follow the
  tracks: alive, hurt, or too late), a captive cut out of the webs or taken back from an orc camp, the village
  defended on the day the raiders come (be there, or it burns), the sick well put right, winter supplies brought to a
  hamlet at the end of a long road (in autumn), and someone escorted who walks along with you and can die. The towns
  keep four festivals a year: be there on the day and try the contests. The factor of the Merchants' Guild has rush
  orders for towns hit by bad news, debts to collect (pay it yourself, lean on the debtor, or let it go) and cargo the
  bandits took (bring it back, or keep it). The captain and the castellan want deserters brought back (or let go home),
  enemy fortresses spied on, villages defended. The temple sends you on a pilgrimage to a far shrine, after a relic in a
  ruined temple, or to take a shrine back from the dead. And when you are wanted, you can swear at the gate it was
  someone else, and go and prove it on the one who works the same roads.
- **Choices leave marks**: on your standing in a town, with a faction, with your god and your guild, on your record with
  the law, and on your hireling's loyalty. A sellsword who has been with you a while may tell you about an old debt.
- **The Starfall.** On the night of the 12th of Emberwane the sky rains stars, and one of them comes down whole. Follow
  the scorched earth to it: star-iron for whoever is first, and others are looking too.
- **Thornfield** has a pond with an old fisherman. Talk to him for your first pole and your first job: catch a fish.

## Factions, war and crime

The factions are different in every world: an empire, merchants, forest folk, outlaws and a cult, often joined by
dwarf clans and orc tribes, each with its own people, name, colour and enemies. They hold castles (`Ω`) and forts
(`╬`). Small armies march visibly across the map; a successful siege takes the castle and its region, villages and all.
You can storm hostile castles yourself: kill the commander and hand the castle to an ally. Your standing with each
faction sets prices, which gates open and who attacks you.

You can rob travellers and caravans. Every settlement remembers what happens nearby: let your name sink too far and
you are wanted, in five levels (the village watch, the sheriff, the lord's soldiers, knights and finally an army).
Wanted posters go up on the boards, and guards stop you at the gate: pay the fine, three days in the stocks, or run.
People forget, slowly.

## The wild

- On the roads you are fairly safe. The further you stray, the more dangerous it gets: bigger packs, stronger
  monsters, more champions. At night the dead walk.
- **Enemies have habits**: cowards flee when hurt, packs surround you, archers keep their distance, spiders lie in wait
  unseen, wolves howl the pack awake, orcs fly into a rage, cultists heal their friends, ogres and trolls charge you
  (after a warning).
- **Every kind asks something different of you.** Web weavers shoot silk that holds you, trapdoor spiders burst out
  of the ground and seize you, jumping spiders pounce, phase spiders flicker out of the world, swarms shrug off blades
  but burn, bombardier beetles spray acid, rust beetles eat your gear, locusts eat your food, needlewings latch on and
  drink, crawlers paralyse, ticks bring disease. Goblins, kobolds, orcs, hobgoblins, gnolls, lizardfolk, viperkin and the
  peoples below come in bands with classes: archers, bombers, shamans who plant totems, warlocks who curse, trappers
  who lay snares, legionaries who fight in line, and a chief whose death may break the band. Dangerous moves are
  announced a turn ahead (a lifted abdomen, a lit fuse, gathering shadows): step aside.
- **And every other corner of the land has its own**: ghouls whose claws numb, ghasts that stink, skeleton warriors
  behind shields, barrow draugr who step out of the rock, banshees whose wail fills you with fear, shades and wights
  that drain your strength, vampire spawn; bears that hug, boars and rhinos that charge, panthers that stalk, snow apes,
  mammoths and sabretooths in the north, frogs whose tongue drags you in, constrictors, winter wolves that breathe frost;
  oozes that eat metal or split, rot flowers whose pollen sends you to sleep, shriekers that wake the whole level;
  crabfolk, brinefolk and sea hags on the coast; animated armour and bronze guardians in the Varnish vaults, gargoyles
  that stand as statues and mimics that wait as chests; Morrak's imps, which go unseen; pixies and dryads that charm
  you so you cannot strike them; wyverns, drakes, basilisks whose gaze stiffens you, manticores; and the things of the
  deep, under names of our own: skullsippers that drink your mana, babbling gibberflesh, stonemaws, gloomwings,
  rustgnawers, gloomdiggers, burrowbacks.
- **States**: held, paralysed (never twice in a row), asleep, slowed, confused, afraid, blinded, diseased (no natural
  healing), cursed (less damage and healing), weakened (less damage) and charmed show under your globes. Priests, antidotes and Purify lift them.
- **New places**: an ant nest, a spider lair, a goblin warren (with its king), a snake ruin, an old barrow (the Ghast
  Lord), the Gloam (where the Staring Dark waits) and a drowned grotto (the Deep Mother), each with its lord at the bottom, and
  orc war camps (green `∆`) out in the hills.
- Hidden places: ruins (`Π`), shrines (`†`), bandit camps (`∆`), standing stones (`Ψ`) and abandoned wagons (`¤`);
  along the old ways Varnish waystations (`Σ`), milestones (`╥`), sealed vaults (`Φ`), graveyards (`┼`) and a
  smugglers' den (`δ`), which you only find by walking right up to them or by following their path.
- On the road anything can happen: wounded travellers, pedlars, Black Hand toll roads, storms, will-o'-wisps.
  Travellers (`☺`) sometimes have a job for you and wait for you afterwards at an inn.
- **Fog of war**: in the open you see about 4 tiles, further from hills, much less in forest and marsh, and half as far
  at night. Land you saw earlier is shown grey: what happens there now, you do not see.
- The bestiary remembers the monsters you have met. Every kill teaches you more: more damage against that kind, and
  they hit you less often. For the new kinds it tells three layers: how they look (each one is its own, female or
  male), what they do (after 3 kills), and their weakness and home (after 10).

### Named enemies

The wild has its own villains: an orc chief who burned a mill, an old she-wolf who takes the sheep every winter, a
spider that webbed a whole wood. Each has a name and an epithet, a rank (notable, notorious, or rarely legendary, with a
lair of its own), traits you learn as you see them (venomous, thorny, blinking, shielded, a war cry...), a following,
a habit (territorial, roaming, raiding villages, waiting on one road, only out at night), looks, a past, a weakness
you can hear about, and a trophy.

- **No marker.** A WANTED poster, a captain or a guild gives a hatched search area on the map: where it was last seen,
  growing as the report ages. Walking inside it you find signs (tracks, a torn deer, a burnt cart, webs) that tell
  direction and age and shrink the area. Foraging and the Wardens help; rain washes tracks away, snow shows them.
- **Close enough, you meet**: you catch it unawares, or it catches you. Its name shows once you have seen it.
- Kill first, find the poster later: the trophy is paid for wherever there is a bounty on it.
- Left alone they grow: a trait, more followers, a higher bounty. Beaten badly they flee and come back scarred,
  knowing your name. If one kills you, it keeps a piece of your gear until you take it back.
- The big ones have lieutenants: kill them, and one of them carries the map to where the boss hides.

## Controls

Avarenthia is played with the keyboard alone, and with as few keys as possible, so that one day it can be played on a
controller or a phone.

| Key | Action |
|---|---|
| arrows, numpad | walk; walking into a monster attacks it |
| Shift + direction | run |
| **Enter** (or Space) | **do the obvious thing here**: take the stairs, enter a place, pick up, talk to someone nearby, read a signpost, open a chest, fish |
| **Tab** / Shift+Tab | **pick a target**, as in WoW: the next or previous enemy in sight, nearest first; it is marked on the map and shown in the panel |
| `1` - `6` | your six skills, at your target (or the nearest enemy) |
| `f` | shoot your bow at your target |
| `Q` / `W` | health or mana potion |
| `I` | inventory |
| `m` | world map (in a town: the town plan, Tab for the realm); Tab picks a place to travel to, Enter sets out |
| `t` | talk to whoever is near |
| `h` | your hireling: orders and gear |
| `?` | help |
| **Esc** | let go of your target; otherwise **the menu**: everything else, grouped as Hero, World, Actions and Game (save and quit is under Game) |

Every menu item shows its own shortcut on the right (`t` talk, `E` eat, `F` forage, `C` life skills, `x` explore,
and so on). The foot of the side panel shows what you can do where you stand, with its key (`Enter go in`,
`t talk`, `a fish`, `E eat`, `F forage`, `R rest`), so you learn the shortcuts the moment they are useful. A capital
letter means: with Shift.

## Install and run

You need Python 3.10 or newer.

```bash
python -m venv .venv
# Windows:      .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

The game opens a window of 110 × 60 square cells in the IBM CGA 8×8 font, at the largest sharp scale that fits your
screen (2× on a 1080p screen). F11 or Alt+Enter toggles full screen. Your hero is saved in `savegame.dat` next to
`main.py`; when you die in hardcore, it is deleted.

### Windows with Smart App Control

Smart App Control blocks the `.exe` because it is not digitally signed. Play through Python instead:

1. Install Python 3.10 or newer from [python.org](https://www.python.org/downloads/) and tick "Add python.exe to PATH".
2. Download the source (on GitHub: *Code → Download ZIP*) and unpack it.
3. Double-click `start_windows.bat`. The first time it installs what it needs (about a minute); after that the game
   starts straight away.

If Windows also blocks the `.bat`, open a terminal in the folder and type:

```
py -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python main.py
```

### Building a single executable

An executable has to be built on the operating system it will run on.

- **Windows:** double-click `build_windows.bat`; after a few minutes `dist\Avarenthia.exe` is ready.
- **macOS / Linux:** `bash build.sh`, then `dist/Avarenthia` is ready.
- **Through GitHub:** the workflow in `.github/workflows/build.yml` builds Windows, macOS and Linux versions on every
  push. Download them under *Actions*, at the latest run, under *Artifacts*.

Windows SmartScreen may warn because the file is not signed; choose *More info* and *Run anyway*.

## Project structure

```
main.py                    window, tileset, keyboard (everything tcod-specific)
avarenthia/ui.py           all screens and drawing, independent of tcod
avarenthia/canvas.py       thin layer over the tcod console
avarenthia/logo.py         the title emblem, baked from assets/logo.png by tools/make_logo.py
avarenthia/engine.py       game rules: movement, combat, skills, exploring, saving
avarenthia/data.py         tiles, skills, items, affixes, monsters, dungeons
avarenthia/entities.py     Item, Monster, Player, GameMap; loot and monsters
avarenthia/ai.py           monster habits and traits
avarenthia/creatures.py    the families of round one: spiders, insects, goblinoids, the peoples below (pure data)
avarenthia/menagerie.py    round two: the dead, beasts of every land, oozes, plants, the sea, constructs, fey, the deep
avarenthia/behave.py       what those kinds do (web, grab, swarm, totems...), and your states (held, cursed...)
avarenthia/named.py        named enemies, their fame and grudges, and hunting them
avarenthia/world.py        the realm: regions, roads, settlement sizes and services
avarenthia/terrain.py      the shape of the world: continent, islands, climate, biomes, rivers, wonders
avarenthia/worldgen.py     wilderness, dungeons (rooms and caves), shops
avarenthia/towns.py        hamlets, villages, towns, cities and the metropolis
avarenthia/sites.py        farms, roadside inns, temples, monasteries, watchtowers
avarenthia/deephold.py     dwarven holds and the Deep Roads
avarenthia/weather.py      climates, seasons and every weather effect
avarenthia/lore.py         history, gods and peoples; what people say; rumours and hints
avarenthia/gods.py         the pantheon, devotion, favour and blessings
avarenthia/events.py       ruins and other places, road events, travellers
avarenthia/evils.py        what happens in the background (spoilers!)
avarenthia/war.py          armies and sieges
avarenthia/factions.py     factions, made anew for every world
avarenthia/races.py        peoples, their relations and names
avarenthia/crime.py        crime, standing per settlement, bounty hunters
avarenthia/itemdata.py     slots, base items in three grades, affixes, uniques, sets and loot tables
avarenthia/guilds.py       the guilds: ranks, jobs, techniques, the secret ones
avarenthia/hidden.py       the old Varnish ways, the places they lead to and the hidden valleys
avarenthia/harbour.py      harbours in the coastal settlements, by size
avarenthia/mercs.py        hirelings: hiring, orders, morale, and whom the monsters go for
avarenthia/news.py         news that travels on foot, and the people who tell it
avarenthia/economy.py      goods and prices
avarenthia/money.py        copper, silver and gold
avarenthia/missions.py     jobs and quest marks
avarenthia/jobs.py         village, trade, war, faith and exploring jobs, the calendar's, and the weight of choices
avarenthia/lifeskills.py   fishing and the other life skills
avarenthia/foraging.py     plants, foraging and herbalism
avarenthia/brewing.py      alchemy and brewing
avarenthia/hunger.py       food and hunger
avarenthia/calendar.py     months, weeks and seasons
avarenthia/look.py         how the land looks (height, moisture, climate)
avarenthia/dress.py        dungeon dressing and light
avarenthia/fov.py          field of view through libtcod (symmetric shadowcasting)
assets/glyphs.png          tileset made from the IBM CGA 8×8 font (Px437, every glyph)
assets/fonts/              the font and its licence
tools/                     tileset and logo makers, screenshots, weather demo
tests/                     headless test and a bot that plays the game
```

## Tests

```bash
python tests/test_headless.py   # plays with random keys and draws every screen
TEST_ONLY=wonders,wilds python tests/test_headless.py   # only some parts of it
python tests/bot.py 4           # a bot plays through the dungeons
```

The tests run without a window and without tcod.

To rebuild the tileset:

```bash
pip install pillow
python tools/make_tileset.py path/to/font.ttf
```

## Credits

Design and direction: **Nilio**.

The font is Px437 IBM CGA from The Ultimate Oldschool PC Font Pack by VileR
(https://int10h.org/oldschool-pc-fonts/), CC BY-SA 4.0; see `assets/fonts/LICENSE-Px437.txt`. Every glyph of the font
is in the tileset (`avarenthia/glyphs.py`).
