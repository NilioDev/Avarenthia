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
| **Approved: spell effects** | Part 1 built 19 October 2026 (the shared toolkit, status colours, Wild Shape colours, the option; see `docs/built.md`). Left: each school its own hand, the weapon skills' effects |
| **Approved: classes** | Two classes instead of a free mix: you start blank, the first tome you read wakes your first class, a second comes late (rank 20); 11 classes (the nine schools, Cunning, Arcane), a name and one rule for each pair (55) or a pure rule; a small tree of passives per class (3 branches of 6); the bar becomes 2 weapon skills, 3 class skills, 1 elite from a guild. Not built yet |
| **Approved: weapons** | 26 weapon kinds in six disciplines (new: Spears and Staves with reach; flail, war hammer, scimitar, crossbows, sling, throwing knives, cestus, claws); shield skills in Warcraft; two weapons at once. Not built yet |
| **Next: round 6 (on hold)** | Livelier settlements, each people in its own rhythm; the half-orc and goblin quarters. Waits until Nilio says go |
| **Parked** | The bard (docs/parked.md) |
| **Later** | Crafts guilds, leadership, a house of your own |

**Left of the big build (paused 18 October 2026 after the magic schools, at Nilio's word):** in this order,
weapons, then classes (approved 19 October 2026; they need the weapon kinds, and they change the skill list), then
spell effects (so the new skills get theirs too), then round 6 (Nilio's go for the whole plan covers the old three;
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

## Spell effects (approved; part 1 built)

**Built 19 October 2026 as a quick win** (see `docs/built.md`): the toolkit (bolts with a tail, bursts, drain,
rising crosses, the zigzag), status colours on creatures, Wild Shape's colours, monsters' arrows and spells, the
option full/short/off. **Left:** each school its own hand (Meteor's shadow and slanting fall, the corpse that greys
and rises, Morrak's Bargain pulling your own life out first, rings and waves), the one white frame of a great
lightning stroke, and the weapon skills' effects. The spec below is the whole plan.

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
- **Still open:** effects for the weapon skills (a swing arc, arrows that fly, blood on Sever Artery, a `*` on a
  critical), to be worked out with the weapon skills.

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

## Round 6: livelier settlements (on hold)

Approved on 16 October 2026 for the next round after round 5; on hold until Nilio says go (17 October 2026). Everything must show as a tile or work with a bump.
What exists: a day rhythm (work and home), day and night watch, drinkers, children, the lamplighter, hearth glow,
doors shut at night, dogs, cats and livestock, job barks, hints, news through people.

### Everywhere
1. **Work you can see.** (Sparks at the anvil and chimney smoke built 19 October 2026.) A woodpile that grows;
   fields change with the season (bare, green, gold, stubble).
2. **Weather in town.** (Rain emptying the streets and filling the inn built 19 October 2026.) Bare fields in winter.
3. **Market day and rest day.** One market day a week (extra stalls, travellers, better selling prices); on the rest
   day the temple is full and the shops are shut (`calendar.weekday()` is still unused).
4. **The town reacts to the world.** A raid nearby means more guards, fearful talk and shutters; a war won, a feast.
5. **Small happenings to bump into.** An inn brawl, a runaway pig, a funeral procession, a pickpocket. Small, no
   menu, a little reward.

### Each people in its own rhythm
- **Humans**: the temple bell and market day.
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
