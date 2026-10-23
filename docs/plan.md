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
| **Built** | Everything up to the magic schools: see `docs/built.md` (summaries and the specs of built rounds) |
| **Approved: spell effects** | Parts 1 and 2 built 19 and 22 October 2026 (the toolkit, status colours, Wild Shape colours, the option, each school's own hand, the storm's white frame; see `docs/built.md`). Left: the weapon skills' effects, with the weapon skills |
| **Approved: classes** | Two classes instead of a free mix: you start blank, the first tome you read wakes your first class, a second comes late (rank 20); 11 classes (the nine schools, Cunning, Arcane), a name and one rule for each pair (55) or a pure rule; a small tree of passives per class (3 branches of 6); the bar becomes 2 weapon skills, 3 class skills, 1 elite from a guild (or one of 22 epics from hidden teachers, two per class). Not built yet |
| **Approved: weapons** | 26 weapon kinds in six disciplines (new: Spears and Staves with reach; flail, war hammer, scimitar, crossbows, sling, throwing knives, cestus, claws); shield skills in Warcraft; two weapons at once. Not built yet |
| **Approved: life skills** | Slow like an MMO but worth it: you learn only from work at your own height, better materials lie further out, crafted gear has chosen powers, masters can move a found power onto their own work (and may fail). Herbalism joins Foraging; new Smithing and Tailoring; named beasts give parts and keep dens (Monster Hunter's way). |
| **Next: round 6 (on hold)** | Livelier settlements, each people in its own rhythm; the half-orc and goblin quarters. Waits until Nilio says go |
| **Approved: dungeons on their own land** | Built places that stand outside (temple, abbey, tower, fort, manor) start on their own play map with land around them; upper floors and cellars by stairs; each kind its own plan, bigger levels, wider halls, one telling thing per room, a mood line in the messages. Caves stay underground. Underground kinds their own plan too; hand-drawn pieces in data files and an editor for Nilio; classic dungeons from a random maker (rooms of many shapes grow onto the level, main ways 3 wide, narrow ways 1 wide, every passage from room to room). Not built yet |
| **Approved: debug menu and a test build** | Every CI build makes two downloads: the normal game for players and "Avarenthia (test)" with the debug menu (F12) and the dungeon editor. Snapshots, a bug-report key, teleport, god mode and more. Not built yet |
| **Approved: the bestiary grows** | What you know of a creature kind grows by killing and skinning it; the look line and its bestiary page show more in three steps. No new skill. Not built yet |
| **Approved: the northern lights' gift** | Under the northern lights old rune stones glow and point to hidden places, Frost and Storm cost less mana, the spirits of northern barrows give a job (wake them by digging and they turn on you), and northern villages hold a light-feast. Ghostly creatures get a wan blue-green glow, fiends a faint red fire glow. Not built yet |
| **Approved: cities that grew** | Cities and the metropolis are no longer a grid: they grow like old European towns round a heart that fits the ruler (cathedral and great market, a burgh, or an emperor's walled palace), with winding streets, row houses that share their walls, the line of an old wall as a ring street, a wall with towers and a moat. Flat harbour towns get canal rings. Bigger: a metropolis 360x220, a city 240x140. Each other people builds its own way (dwarves plan, halflings ramble, orcs grow rings of huts). Not built yet |
| **Approved: old places on the land** | More points of interest born from the made history: old battlefields, deserted villages, broken bridges, memorials, quarries, wrecks, hermitages, leper colonies, marks of the peoples; overgrown Varnish cities found only by walking, with hidden dungeons beneath. Then newer places (logging camps, war camps, beacons, lighthouses...). Not built yet |
| **Parked** | The bard; the werewolf's and the vampire's curse (docs/parked.md) |
| **Later** | Crafts guilds, leadership, a house of your own |

**Left of the big build (paused 18 October 2026 after the magic schools, at Nilio's word):** in this order,
weapons with their skills' effects (spell effects parts 1 and 2 are built), then classes (approved 19 October 2026;
they need the weapon kinds, and they change the skill list; new skills get their effects as they are built), then
round 6 (Nilio's go for the whole plan covers the old three;
classes wait for his go). Their specs are below; nothing of them is built yet.

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

## Classes, trees and the bar (approved, not built)

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

## The bestiary grows (approved, not built)
Approved 22 October 2026 (from going through Project Gorgon's skills). No new skill: the bestiary that exists gets
deeper. What you know of a creature kind grows each time you kill or skin one. Three steps, each shown in the look
line (`l`) and on its bestiary page: first its weakness and resistances, then what it carries, then its weak spot
(a better chance of a critical hit against that kind). Reading about a creature in a library may give the first step.
Saved per hero: bump `SAVE_VERSION`; the handbook says it in a sentence or two.

## The northern lights' gift (approved 22 October 2026, not built)
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

## Weapons: more kinds, few disciplines (approved, not built)

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
- **Built places start outside.** A place that stands on the land (temple, abbey or monastery, tower, fort, manor, and other buildings on the world map) starts on its own play map with land around it, matching the world-map terrain: you walk in from the edge, through a gate or a door. An upper floor (a tower, a bell loft) and cellars or a crypt are their own levels, reached by stairs. Caves, dens, nests and mines still start straight underground. Mockup C.
- **Each kind its own plan.** A temple has a nave with pews and pillars, a transept, chapels and an altar; an abbey a cloister round a garden, a refectory and cells; a tomb a procession hall and burial galleries. You can tell from the map what the place is. Mockups A and C.
- **Bigger and roomier**, for fights with hirelings and spells: levels up to 120 x 70 (sizes per kind below), halls two or three wide. Ties in with Nilio's later wish for bigger play maps (the map view now shows 80 x 51).
- **Built walls are thin joined lines** (as town houses already draw them), one wall between neighbouring rooms, never a double one; caves keep their raw rock.
- **Mixed levels** when a job or the story asks: a built tomb that breaks into a cave (mockup B). Caves may be bigger too, with several great halls.
- **One telling thing per room** (a pool, a row of statues, an altar, a sarcophagus), always a tile used with one key or a bump.
- **A mood line**: the first time you step into a room, the messages say what it is ("The nave. Rotten pews face a cracked altar.").
- **Underground kinds get their own plan too** (`ondergronds.md`): whoever made the place decides its shape (water, beasts, ants, goblins, dwarves, people); rooms by use (a goblin delve has a market hall, forge, family halls, cells, the chief's hall); tunnels at least 3 wide, main ones 4, well connected with a loop; inhabitants placed where they belong, fewer than now; two ways down where it fits. Goblins are a clever people: their delve is cut into the back wall of their ravine, not a cave. Cells have bars only as their front, between stone walls. Bridges no longer use ═ (the built wall). Mockups E2 and F.
- **Hand-drawn pieces ("vaults", the way of Dungeon Crawl Stone Soup, `dcss.md`)**: small ASCII maps in data files with substitutions for variety, tagged by kind of place and by part (entrance, arrival, middle, bottom); the plan of a kind is laid out first and its rooms filled with fitting pieces. A piece may have a trigger with a message line (bars drop, the dead rise). Nilio can also draw unique places that appear once per world.
- **An editor for Nilio** (and others he explains it to), modelled on REXPaint: mouse and keyboard (the one place the mouse is welcome), the real tileset and joined walls, tools for a cell, line, rectangle, fill, copy and paste, undo and redo, colours to change, layers (ground, things, creatures, triggers), zoom; it knows the game's tiles, so a wall stays a wall; saves to the pieces file; a key to play-test the piece at once. It is a tool, not part of the game: it is not in the players' download, only in the test build (see "Debug menu and a test build") and from the source with a flag. The game loads only the pieces that come with the build: CI packs them into one file with a checksum and the game ignores a changed pack. (A determined player can always change a local single-player game; this only keeps casual meddling out.)
- **Events in pieces**: simple when → if → then rules, picked from lists in the editor's trigger layer (no typing, no real script language). When: step on, open, take, kill, enter a room, night falls. If: day or night, a job or item, people or standing, a chance. Then: a message line, a choice (EV.ask), a door or bars open or shut, creatures appear or wake, something caves in or floods, a job moves on.
- **How Nilio works with it**: the editor is its own program ("Avarenthia Editor", own icon, not in the players' download). New → kind of place → part; draw with the mouse; events from lists; Try puts your hero in the drawing at once; Save puts the file in "My pieces". He hands the file to Claude ("voeg toe"), it goes into the repo, CI packs and seals it, and the next build has it.
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
- **Theme rooms (approved 22 October)**: a room with one telling thing you use with a key or a bump. K5 keeps rooms with a single entrance for them; every fixed plan has its own spots for them. Each is a drawn piece with switches for variety, in its own shape (a nave with an apse, an L, an octagon, round, a cross, a gallery with bays, a half moon, a cave), turned and mirrored; Nilio can draw more in the editor. More ideas are always welcome. Details: project files `dungeons/themakamers.md`; mockups `R_theme_rooms.png`, `R2_theme_rooms_shapes.png`.
  - **Four parts per place, each its own list:** the entrance (a gate, a fallen-in way, a guard post with a gong, a stair hall); the arrival, never straight into a fight (the stair room, a dead adventurers' camp with a letter that becomes a rumour, a quiet chapel); the middle; the bottom (the boss's throne or lair, the treasure room, the hidden ancient bottom).
  - **Something to do:** shrine (pray for a blessing, or a curse if defiled); library (search for a tome, a map or lore, `history.py`); fountain (one drink, a random effect); abandoned forge (repair); alchemy lab (brew); fungus garden (forage; some puff spores); larder or kitchen (food, a fire to cook); wishing well (throw a coin for luck, gold for more); training hall (straw dummies, a little weapon practice, once); map room (read it and the level shows); wine cellar.
  - **Something to find:** locked vault (its key elsewhere on the level, often with a guard); choice vault (take one find, the rest sink away); hidden room behind a secret door; flooded hall (an island; swim, heavy gear sinks you, or freeze a way); armoury (only the gear of who lived there, mostly rusted: no loot piñata); fallen adventurer (one piece of kit and a letter).
  - **Something to fight:** pillared hall for a horde (pillars to break it up, a door to hold); summoning circle (step in by choice for a wave, a reward at the end); statue hall (one statue is not); ossuary (the bones get up at the bier); nest (webs or eggs: burn or wake); guard post with a gong at a choke point (silence the guard and the level sleeps); prison block (barred cell fronts between stone walls; a captive or something better left locked); mirror room (your double steps out); menagerie (a lever opens the cages, on whoever is near); echo hall (a fight here wakes the level).
  - **Something of the place:** chasm with a rope bridge and a collapsing floor (the edge rule: shove foes down); fallen-in room (clear the rubble, something behind); trap corridor (plates seen when searching); lava or fire rift (deep only); a cave breaking through; overgrown garden under a light shaft (herbs); sanctuary (wards no monster crosses: one safe rest); old arch of the old ways (`hidden.py`, with its word it takes you elsewhere); gnome clockwork room (gears open and shut the ways); bandits' gaming den (dice; catch them cheating).
  - **Each people flavours a room:** a dwarf shrine has a forge altar, a goblin library heaps of stolen books.
  - **Rules:** 2 or 3 theme rooms per level at most, never the same twice on one level, a mood line on first entry, and no light to carry: mushrooms and crystals give the light.
- **Goblin places (approved 22 October)**:
  - **An ordinary goblin hole** (small, 80 x 50; mockup `E3_goblin_hole.png`): a hole in a slope with a lookout and the alarm gong by the way in (silence the watch and the hole sleeps on); rough passages braced with beams; tripwires and a covered pit; a sleeping den with straw, a cook den, a loot corner with what they took from the road, the leader's nook; a narrow back way out where they flee. Short and sharp: one level, sometimes two.
  - **The goblin village** (large, 120 x 70, built like a settlement; mockup `E2b_goblin_village.png`): cut into the back wall of their ravine, the ravine as the square, a gate with the goblin tower; a main gallery 4 wide; the market hall with pillars, the forge, family halls with hearths, the cell block (barred fronts between stone walls), wolf pens (a keepers' aisle with room to stand, pens cut into the rock, a barred front with a door on each), a shrine, the chief's hall at the back with the treasury, a loop round the back. Two levels: the village, and the mine and deep halls below. Traders, children and non-fighters who flee; the warn-then-rouse rule of `tribes.py`; captives for a rescue job. The chief's throne decides whether the village goes with you or against you.
- **Rock you can see (Nilio, 22 October)**: underground, the solid rock beyond the walls is not plain black but shows a quiet texture, as in the mockups: a sparse speckle (#) in a dim earth colour, darker than the walls so it never reads as a wall or as floor. Fixed per cell (the same each time you look), and it shows only round what you have seen. Each kind of ground its own tint: grey stone, brown earth, dark basalt deep down; now and then a glint of ore in a mine. On the world above, built places keep their land round them instead.
- **Rivers underground (Nilio, 22 October)**: a river, of water or of fire, always runs through: it comes in at one edge of the level and leaves at another. Between caves it flows through the rock in a channel of its own, with rock for banks, so only the river passes there; it never just stops. It flows visibly: light runs downstream along it, as the rivers on the world map already do; fire pulses as molten metal does. Crossing takes a bridge, a ford or a crust of cooled rock, which makes a good choke point.
  - **Water:** you can swim it. Heavy armour and a heavy pack pull you under, so swimming in them asks first and warns. Monsters that cannot swim stay on the bank; some swim after you.
  - **Fire:** stepping in asks first (as at an edge) and burns you badly; there is no swimming in it. A shove or a knockback sends a foe into it, where it burns.
- **The Rift and the Ashen Deep (approved 22 October)**: a hell-like place. Mockups `H_ashen_deep.png` and `H2_ashen_deep_river.png` (the river running through).
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
- Still to settle (in `docs/open.md`, "Dungeons"): the editor's controls.

## Debug menu and a test build (approved 22 October 2026, not built)

A tool for testing, not part of the game. Details: project files `debug/voorstel.md`.
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
  chronicle; keep it or sell it once, well, to a library. About 12-15 books, each world picks some six, the pages lie
  where they fit. No new key. Stories and titles: project files `poi/varnish-boeken.md` (Letters from the Ninth, The
  Wind in the Jar, Twelve, and more to write). Books of the dirty side too (Twelve, a runaway slave; a mother's petitions
  for her bound son; a dealer in the dead; a banned play); the stories may cross (a soldier in one is in another).
- **Then part B** (also approved, after A): logging camp at the elven forest's edge, charcoal burners, peat cutters and
  salt pans, a realm's war camp, refugee camp, beacon hills, lighthouse, a baron's toll bridge, caravanserai,
  prospectors' camp after a Starfall, a lord's hunting lodge.
- Still to settle (in `docs/open.md`, "Points of interest"): which Varnish places (proposal v2, part C of `poi/ideeen.md`).

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
