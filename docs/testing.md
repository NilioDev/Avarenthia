# Testing: what each new thing needs

What Nilio wants to be able to try in the test build ("Avarenthia (test)", F12 debug menu, see "Debug menu and a test
build" in `plan.md`) for each new thing, so he does not have to play for weeks to reach it. Not built; how to make it easy
is still to settle. When a round is built, its lines stay here as long as they are useful for testing.
Each line: **what** - what to check - what the debug menu should offer.

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

## Old places on the land (approved 23 October 2026)

### Part A: the old, lived-in world
- **Old battlefield** - born from a history event; the chronicle names it; digging a mound gives rust, very rarely a named
  weapon; the dead walk on the battle's day at night. Debug: teleport to it; set the date to its day; force a find.
- **Deserted village** - the cause from history; who lives there now (bandits, hermit, ghost); a plundered village turns into
  one after a year. Debug: teleport; force a plundered village to fall empty now.
- **Broken bridge** - piers, the ford beside it, part of the old ways. Debug: teleport.
- **Memorials** - the stone with names adds a chronicle fact; the fallen statue; the gallows hill with the Watch's sentences.
  Debug: teleport by kind.
- **Old quarry** - half-cut blocks, unfinished statue, flooded ones (swim, fish), stone, a fossil now and then. Debug: teleport.
- **Shipwreck** - only at low tide; searched once; the wreckers may have been first. Debug: teleport; set the tide.
- **Hermitage** - the hermit, and the hidden teachers of the epic skills living there. Debug: teleport; reveal all teachers.
- **Leper colony** - the bell, the temple jobs. Debug: teleport; make the job.
- **Marks of the peoples** - boundary stones, moonstones, skull poles, kobold scratches; read or follow. Debug: teleport by kind.
- **Varnish ruins in the wild** - never on the map before you walk there; found by walking the zones; they match the land
  (forest, sand, marsh, ice). Debug: list them; teleport; reveal on the map.
- **Hidden dungeons** - no rumour, map or job names them; the way in only on the spot (stone with the letters, well, hollow
  floor, lever). Debug: list them with their way in; teleport to the entrance; give the Varnish letters.

### The Varnish places
- **Overgrown city** (sky well, Sky Court), **Northern Wall** (tower ruins), **wind tower** (howls in a storm), **road of the
  bound dead** (break a seal, the dead rises), **star-iron forge**, **Gate of Leagues** (its star map points on), **sluice
  hall** (open a sluice, a hall runs dry), **the fallen sky**, **star house**, sunken harbour, old coins. League stones count
  down towards a ruin. Debug: teleport by kind; choose the weather (storm); spawn star-iron and coins.

### Archaeology (a life skill)
- Dig spots seen by rank; breaking less at higher rank; learnt only at places of your own height. Debug: set the rank;
  show all dig spots on the map.
- Gives lore fragments (the five riddles), star-iron pieces a smith mends into an old power, a modest income from collectors
  and libraries. Debug: give a fragment or a piece by name; show a riddle's state.

### The Varnish' own lore and books
- **Fragments** in the chronicle chapter The Varnish, under their headings (Gods, Daily life, Law and measure, Songs and
  books, Voices, The last days, and the dirty side). Debug: give any fragment by name; give all; open the chronicle there.
- **Books bound from fragments** - 27 books, about eight picked per world, at least one per thread; from the second page the
  chronicle shows "2 of 6" with the gaps; a library scribe binds a whole set and finds the hidden page; the book sells once.
  Debug: list this world's books and where each page lies; give a whole set; give one page; teleport to a page.
- What some books add: the recipe Fig Bread; the ferryman who ferries you free; one apple a year from the tree on the
  Sky-Seat; an old way revealed at once; places put on the map. Debug: check each after binding.

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

### The five riddles
- Each riddle in the chronicle with its gaps named; whole at about six of eight fragments; false ones get "Not so" later;
  the answer and the lead to its hidden place; all five give The Ruin, as it was. Debug: give fragments of a riddle one by
  one; make a riddle whole; teleport to its hidden place.
