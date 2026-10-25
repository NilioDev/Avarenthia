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
| **Approved: the epics** | 22 epic skills from hidden teachers, two per class, on key 6 instead of the elite (classes part 4, round 13). The rest of the classes is built |
| **Approved: life skills** | Slow like an MMO but worth it: you learn only from work at your own height, better materials lie further out, crafted gear has chosen powers, masters can move a found power onto their own work (and may fail). Herbalism joins Foraging; new Smithing and Tailoring; named beasts give parts and keep dens (Monster Hunter's way). |
| **Next: round 6 (on hold)** | Livelier settlements, each people in its own rhythm; the half-orc and goblin quarters. Waits until Nilio says go |
| **Approved: dungeons on their own land** | Built places that stand outside (temple, abbey, tower, fort, manor) start on their own play map with land around them; upper floors and cellars by stairs; each kind its own plan, bigger levels, wider halls, one telling thing per room, a mood line in the messages. Caves stay underground. Underground kinds their own plan too; hand-drawn pieces in data files and an editor for Nilio; classic dungeons from a random maker (rooms of many shapes grow onto the level, main ways 3 wide, narrow ways 1 wide, every passage from room to room). The random maker, the theme rooms, rivers underground and the pieces format are built (24 October 2026), and so are the temples, towers, barrows, abbeys, forts, manors, goblin places and the underground kinds' plans; the editor is not |
| **Approved: cities that grew** | Cities and the metropolis are no longer a grid: they grow like old European towns round a heart that fits the ruler (cathedral and great market, a burgh, or an emperor's walled palace), with winding streets, row houses that share their walls, the line of an old wall as a ring street, a wall with towers and a moat. Flat harbour towns get canal rings. Bigger: a metropolis 360x220, a city 240x140. Each other people builds its own way (dwarves plan, halflings ramble, orcs grow rings of huts). Not built yet |
| **Approved: old places on the land** | More points of interest born from the made history: old battlefields, deserted villages, broken bridges, memorials, quarries, wrecks, hermitages, leper colonies, marks of the peoples; overgrown Varnish cities found only by walking, with hidden dungeons beneath. Then newer places (logging camps, war camps, beacons, lighthouses...). Not built yet |
| **Approved: the great evils as storyteller** | One ultimate evil, the Hollow King, the old shadow of the Varnish in the hidden Sky-Seat; under him three servants per world (one light, one middle, one heavy, from 24 kinds), each pushing the realms and powers with its own goal; a slow clock and a clock of his attention; one long quest with relics, the chains and the Sky-Seat's five floors. Replaces `evils.py`'s growth. Not built |
| **Parked** | The bard; the werewolf's and the vampire's curse (docs/parked.md) |
| **Later** | Crafts guilds, leadership, a house of your own |

**The build order** (settled with Nilio 23 October 2026, thread "Bouwvolgorde plan.md"; the Dutch proposal with the
reasons: project files `bouw/volgorde.md`). 23 rounds in 7 blocks. Sizes: S like market day, M like spell effects
part 2, L like herds and hunting, XL like the magic schools. No play builds in between (Nilio, 23 October 2026): he plays only when all 7 blocks are built, so the
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
8. **The northern lights' gift** (M): needs the barrows. Built 24 October 2026 (see `docs/built.md`); its light-feast moves to the feast days (round 20).
9. **The Rift and the Ashen Deep** (L). Built 24 October 2026 (see `docs/built.md`). 10. **The editor** (L; its controls are still to talk about, may come later).
   A pause after 5, 7 and 9; merge after 9 (the editor apart).
11. **Old places from the history** (L): battlefields, deserted villages, memorials, hermitages and the rest of part A.
12. **The Varnish** (XL): their cities and places, the hidden dungeons (need K5), the lore, the books, the riddles.
13. **Classes part 4: the epics** (L): their teachers live in hermitages, their deeds need barrows. Pause after 12,
    merge after 13.
14. **Life skills part 1** (XL): the curve, Herbalism into Foraging, Smithing and Tailoring, the materials by tier,
    alchemy, brewing (ore lies by depth in the new caves). 15. **Part 2** (XL): beast parts, crafted powers, Unmake,
    master tests, perks, hirelings' gear, named beasts' dens, catching alive, the great masters.
16. **Archaeology** (M): needs the old places and Smithing. Pause after 14 and 15, merge after 16.
17. **Cities that grew, part 1** (XL): human cities, the metropolis, canal and fortress towns, test `city_rules`. The
    bridges are not yet perfect (open.md, "City streets and bridges"); that does not hold this round up.
18. **Part 2** (L): dwarf, halfling and orc towns, bridges on the open land. 19. **Round 6** (L): it lives in the new
    city maps. 20. **Feast days** (L), with the light-feast (northern villages keep the first night of the lights: news, cheaper beds, a blessing at their shrine; its spec stayed with the northern lights in `built.md`). Pause after 17 and 19, merge after 20.
21. **Old places part B and the 44 places of the peoples and powers** (XL). 22. **Places 45-64 and the seasonal
    places** (L). Merge after 22.
After that: the great evils (see "The great evils as storyteller"; Nilio, 25 October 2026: after the epics, in
three parts: the frame with eight servants, the quest and the Sky-Seat, the other sixteen), then Multiplayer (parked).

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

## Classes part 4: the epics (approved, not built; round 13)

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

## Life skills: slow, and worth it (approved in part, not built)
Worked out with Nilio on 19 October 2026; details and tables in `/mnt/project-files/lifeskills/overzicht.md`.
Approved so far:
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
- **No grinding in one place** (19 October): the rank of a vein, herb, fish or beast follows the danger of the land
  (the danger layer) and the depth of a mine or dungeon, never one spot; each step has three or four options in
  different lands (Fishing 35: Great Sturgeon in broad rivers, Swordfish at deep sea, Ice Char in northern lakes, Deep
  Eel in underground lakes). The top finds (Moonfish, Star-iron, elven thread, dragon hide) are the crafts' own rares:
  scarce, one special property, never needed for a rank. Xp without gathering too: orders at your own height in every
  town, masterwork tries, mending for others.
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
- **An editor for Nilio** (and others he explains it to), modelled on REXPaint: mouse and keyboard (the one place the mouse is welcome), the real tileset and joined walls, tools for a cell, line, rectangle, fill, copy and paste, undo and redo, colours to change, layers (ground, things, creatures, triggers), zoom; it knows the game's tiles, so a wall stays a wall; saves to the pieces file; a key to play-test the piece at once. It is a tool, not part of the game: it is not in the players' download, only in the test build (see "Debug menu and a test build" in `docs/built.md`) and from the source with a flag. The game loads only the pieces that come with the build: CI packs them into one file with a checksum and the game ignores a changed pack. (A determined player can always change a local single-player game; this only keeps casual meddling out.)
- **Events in pieces**: the when / if / then rules are built in the pieces format (24 October 2026); the editor will offer them as lists in its trigger layer.
- **How Nilio works with it**: the editor is its own program ("Avarenthia Editor", own icon, not in the players' download). New → kind of place → part; draw with the mouse; events from lists; Try puts your hero in the drawing at once; Save puts the file in "My pieces". He hands the file to Claude ("voeg toe"), it goes into the repo, CI packs and seals it, and the next build has it.
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
- Still to settle (in `docs/open.md`, "Dungeons"): the editor's controls.

## Cities that grew (approved 22 October 2026, not built)

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

## Old places on the land (approved 23 October 2026, not built)

More points of interest, so the world looks old and lived in. Approved in the thread on points of interest: "we gaan
eerst A doen, alle ideeen klinken goed". Details and the full list (also the newer places, part B): project files
`poi/ideeen.md`. Each place is one world cell with its own play map (as the wonders and oases), and what matters is a
tile used with one key or a bump. Not the same as what exists: the fresh battlefields and plundered villages of
`living.py`, the hidden places of `hidden.py`, the planned temples, forts and barrows.
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
- **Archaeology, a new life skill** (approved 23 October): dig spots on old places, a tile you see once you have the eye
  for it; the higher your rank, the more spots you see and the less you break; learnt only at places of your own height.
  It gives three things: (1) fragments of lore for the chronicle, belonging to five old riddles that grow as small
  chapters in The Old Days with their gaps named (how the Sky-Seat fell, who the Hollow King was, where the orcs came
  from, what lies in the vaults, why the dead were bound); a riddle made whole is a lead to a unique hidden place, and
  libraries, stones and rumours stay other ways to that knowledge; (2) pieces of star-iron and old things that a smith
  mends, a mended piece carrying an old power (Smithing's found powers), so finds stay rare and the smith's work counts;
  (3) a modest income: collectors and city libraries buy finds and old coins. Its place in the life skills order is
  still open.
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
- **Where it goes in the build order:** see "The build order" at the top (rounds 11, 12, 16, 20, 21, 22).
- **Then part B** (also approved, after A): logging camp at the elven forest's edge, charcoal burners, peat cutters and
  salt pans, a realm's war camp, refugee camp, beacon hills, lighthouse, a baron's toll bridge, caravanserai,
  prospectors' camp after a Starfall, a lord's hunting lodge.
- **The Varnish places** (all approved 23 October; part C of `poi/ideeen.md`): the overgrown city round a sky well
  with a sunken Sky Court; the Northern Wall of the nine legions with its tower ruins; the wind tower that howls in a
  storm; the road of the bound dead (break a seal and the dead one rises); the star-iron forge by an old crater; the Gate
  of Leagues whose star map points to other gates; the sluice hall (open a sluice and a flooded hall runs dry); the fallen
  sky of black stones and glassy sand; the star house with an iron star floor under the dust; and as small extras a
  sunken harbour and old coins.
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

## The great evils as storyteller (approved 25 October 2026, not built; after the epics)

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
- **Still to write while building**: the lieutenants' pools, each kind's weakness and relic, the climb's map.

---

## Round 6: livelier settlements (on hold)

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

---

## Parked
- **The bard** (the Lark's Company): see docs/parked.md. Not until Nilio says so.

## Later (not planned yet)
- Crafts guilds: smith and weaponsmith (mend and improve), herbalist, hunter-tanner (hides and trophies).
- Leadership: more hirelings, a group buff. A house of your own, with taxes.
- World ideas proposed with round 5 but not chosen: smoke over villages seen from afar, birds flushing from woods
  before an ambush, vultures over fights, the world growing (new hamlets, logging, regrowth), worn paths,
  lighthouses and watchtowers lit at night.
