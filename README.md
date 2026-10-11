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

**You learn the world by travelling.** At the start you only know the country around Thornfield. Signposts (`┬`)
tell you where the roads go, and rumours tell you where a place lies, but the road and the land in between only appear
on your map once you have walked them.

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

**Dwarven holds.** In the mountains lie underground dwarven cities (`▼`) with halls, forges, a throne room and stairs
down to the Deep Roads, old dwarven tunnels now full of goblins and worse.

**Weather.** Every region has its own climate that changes with the seasons and moves in steps: drizzle turns to rain
turns to a downpour. Over thirty kinds of weather, from mist, fog and snow to blizzards, sandstorms, haboobs, freezing
rain, hail, falling leaves and blossom. The north and the mountains are cold, the south hot and dry, marshes misty.
Rain, snow, fog and dust limit your sight; snow and storms slow you down; cold and heat make you hungry; fire sputters
in the rain, and lightning strikes open ground. Ash rain, miasma and smoke betray a great evil nearby. Under a roof you
stay dry.

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

Choose **hardcore** (death is final) or **softcore** (you wake in the nearest temple, but your pack, cargo and gold
lie by your corpse until you fetch them). Enter a **seed** to play the same world again.

### No classes

You become what you do. Ten disciplines (sword, axe and mace, dagger, bow, fire, ice, storm, healing, shadow and
unarmed) grow by use. Skills (fifty of them) are learnt from **books** (`≡`): from monsters, deep in ruins, at standing
stones, from pedlars and sometimes at a city outfitter. Harder books ask for a higher discipline. You carry six skills
at a time and swap them in a town or castle. Weapon skills only work with the matching weapon in hand.

Magic items are rare and **unidentified** when found; their powers only work after an outfitter or priest identifies
them. Some are **cursed**: once worn, they will not come off until a priest lifts the curse.

### Life skills

Like in Project Gorgon, life skills grow by doing them: **fishing**, **foraging**, **herbalism**, **alchemy** and
**brewing**. Buy a fishing pole and fish by any water; the better you get, the more kinds of fish bite. Forage in the
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

- **Coin is rare.** 100 copper is 1 silver, 100 silver is 1 gold. Beasts carry no money, people a little, traders a lot.
  Most coin is found in chests (`■`) in dungeons and ruins. Drops are realistic: beasts do not carry swords.
- Every place makes certain goods (`+`, cheap) and wants others (`!`, dear). Buy low and sell elsewhere. Prices react
  to what you and the caravans buy and sell, and recover slowly. News (famine, feast, mine disaster, fire, war,
  plague) shifts prices for a few days.
- You carry 30 units of cargo; a mule (+60) and a cart (+160) are sold by the stablemaster.
- The inn's notice board has courier jobs, freight runs, bounties, escorts and dungeon delves. A blinking yellow `!`
  above someone means work; a `?` means you can hand something in.
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
- Hidden places: ruins (`Π`), shrines (`†`), bandit camps (`∆`), standing stones (`Ψ`) and abandoned wagons (`¤`).
- On the road anything can happen: wounded travellers, pedlars, Black Hand toll roads, storms, will-o'-wisps.
  Travellers (`☺`) sometimes have a job for you and wait for you afterwards at an inn.
- **Fog of war**: in the open you see about 8 tiles, further from hills, much less in forest and marsh, and half as far
  at night. Land you saw earlier is shown grey: what happens there now, you do not see.
- The bestiary remembers the monsters you have met. Every kill teaches you more: more damage against that kind, and
  they hit you less often.

## Controls

Avarenthia is played with the keyboard alone, and with as few keys as possible, so that one day it can be played on a
controller or a phone.

| Key | Action |
|---|---|
| arrows, numpad, `hjklyubn` | walk; walking into a monster attacks it |
| Shift + direction | run |
| **Enter** (or Space) | **do the obvious thing here**: take the stairs, enter a place, pick up, talk to someone nearby, read a signpost, open a chest, fish |
| **Tab** | **the menu**: everything else, grouped as Hero, World, Actions and Game |
| `1` - `6` | your six skills, aimed at the nearest enemy |
| `Q` / `W` | health or mana potion |
| `I` | inventory |
| `M` | world map |
| `?` | help |
| Esc | save and quit |

Every menu item shows its own shortcut on the right (`T` talk, `E` eat, `F` forage, `C` life skills, `X` explore,
and so on). You never need them, but once you know them they are faster.

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
avarenthia/titleart.py     the animated title screen
avarenthia/engine.py       game rules: movement, combat, skills, exploring, saving
avarenthia/data.py         tiles, skills, items, affixes, monsters, dungeons
avarenthia/entities.py     Item, Monster, Player, GameMap; loot and monsters
avarenthia/ai.py           monster habits and traits
avarenthia/world.py        the realm: regions, roads, settlement sizes and services
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
avarenthia/economy.py      goods and prices
avarenthia/money.py        copper, silver and gold
avarenthia/missions.py     jobs and quest marks
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
tools/                     tileset maker, screenshots, weather demo
tests/                     headless test and a bot that plays the game
```

## Tests

```bash
python tests/test_headless.py   # plays with random keys and draws every screen
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
