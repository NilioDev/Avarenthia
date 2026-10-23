# Open: still to talk about

Questions and choices that wait for Nilio, gathered 19 October 2026 so nothing is forgotten. Each heading is a
name he can use ("open.md", "open: debug menu"). When a point is settled, write the decision into `plan.md`
(or `built.md`) and delete it here.

## Build order
What `plan.md` says now: weapons (with the weapon skills' effects), then classes (in three parts, a pause after
each), then round 6. Each starts only on Nilio's "ga".
- **Where do life skills go?** Their content is complete and approved (`plan.md`, "Life skills"), but they have no
  place in the order yet. Proposed: after the classes, because Smithing needs the new weapon kinds.

## Multiplayer (parked, not urgent)
Parked on 22 October 2026: we come back to this later; nothing to decide now. Talked through on 22 October 2026 (thread "Multiplayer"). Nilio wants real online multiplayer: every player runs
their own copy of the game (own screen, menus, handbook, settings), not a remote terminal window.
- Shape: the host owns the world (monsters, jobs, shop stock, the clock are decided only there). A joining player
  makes the same world from the seed, so the big map never goes over the line; after that the host sends only what
  changes, and the player's game sends actions ("walk east", "buy sword"). No separate server; over the internet
  through something like Tailscale. Not lockstep (every copy reckoning everything itself): one difference in the
  dice and the worlds drift apart.
- Rules still to settle: the clock waits for every player; world-map travel, resting and sleeping together; shops
  and choice windows must not freeze the others; death, sharing loot, jobs for two, the one save (kept by the host).
- Cost: preparation (several players in one world, screens apart from the rules) 3 to 4 big rounds, the network 2
  more. Bigger than the class build. Advice: after classes and life skills.
- Rule from now on (in CLAUDE.md): what belongs to the player lives on the player.
- Old code left as it is for now: about 30 things that belong to the player live on the game (where you are: `cur`, `over_pos`; the log, jobs,
  bestiary, kills, death, the hireling, crimes, open choices, "already told" flags), used in some 500 places.

## Dungeon editor controls (parked, not urgent)
Parked on 22 October 2026, for a separate thread later. What we know so far:
- **What it is:** its own program, "Avarenthia Editor", modelled on REXPaint; it comes with the test build ("Avarenthia (test)"), not with the players' download.
- **Mouse and keyboard.** The mouse is welcome here, unlike in the game.
- **Tools:** cell, line, rectangle, fill, copy and paste, undo and redo, change colour, zoom.
- **Layers:** ground, things, creatures and triggers. Events in the trigger layer are picked from lists (when, if, then).
- **Making and testing:** New → kind of place → part; Try puts the hero into the drawing at once; Save puts the file
  in "My pieces".
- **Getting it into the game:** Nilio hands the file over and it goes into the repo; CI packs and seals it.
- **Still to design:** the shortcut keys, how the palette looks, and where the layers and the Try button sit.

## City streets and bridges (parked, later)
Parked on 23 October 2026: "nog steeds niet lekker, lossen we later op". What we have stays as it is (plan.md,
"Cities that grew" and its City rules; mockups and the checker `steden/controle.py` in the project files; all 30
test maps keep the rules). Still not right to Nilio's eye:
- Where a way meets a bridge it does not yet flow: the street plan bends onto the bridge rather than growing from it.
- Gate bridges over the moat look cramped, above all at 45 degrees on a slanting moat.
- Next time: say first what looks wrong in each picture, make that a rule in the checker, then fix.

## Testing the new things
- How to make the lines in `docs/testing.md` easy to test (Nilio, 23 October: "kijken we later hoe we dat makkelijk kunnen doen").

## The great evils (later)
- Go through the great evils together (`evils.py`: the Lich, the Dragon, the Brood Mother, the Warlord, the Drowned One;
  one to three per world). They are of after the Varnish (Nilio, 23 October 2026). Nothing decided yet.

## Smaller loose ends
- **Later, not planned:** crafts guilds, leadership, a house of your own (`plan.md`, At a glance).
- **Parked for later** (`docs/parked.md`): the bard, the werewolf's and the vampire's curse.

Settled, no longer open: the northern lights' gift (in `plan.md` since 22 October 2026), the player as a ruler
(stays no; taken off this list 22 October 2026), the menu line that listed only 5 life skills (fixed 22 October
2026), the visible weather border between regions (thread "Seizoenen in de wereld"; Nilio said it is not needed) and
the class system (approved 19 October 2026, "we kunnen later nog sleutelen").
