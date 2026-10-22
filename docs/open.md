# Open: still to talk about

Questions and choices that wait for Nilio, gathered 19 October 2026 so nothing is forgotten. Each heading is a
name he can use ("open.md", "open: debug menu"). When a point is settled, write the decision into `plan.md`
(or `built.md`) and delete it here.

## Build order
What `plan.md` says now: weapons, then classes (in three parts, a pause after each), then the rest of the spell
effects, then round 6. Each starts only on Nilio's "ga".
- **Where do life skills go?** Their content is complete and approved (`plan.md`, "Life skills"), but they have no
  place in the order yet. Proposed: after the classes, because Smithing needs the new weapon kinds.

## Spell effects: what is left
Parts 1 and 2 are built (22 October 2026: each school its own hand and the storm's white frame). Still to decide:
the **weapon skills' effects** (a swing arc, arrows that fly, blood on Sever Artery, a `*` on a critical). A
proposal with GIFs is in the project files, `magie/wapeneffecten/voorstel.md`; it is built with the weapon skills.
Settled 22 October: the swing arc only on skills and criticals; blood both as a splash and a short red trail.

## Quick wins not taken
From the thread "Quick wins uit het plan"; items 1-5 were built, and market day and rest day on 22 October 2026.
Still not taken:
- **Five new weapons without skills first:** scimitar, flail, war hammer, cestus and tiger claws, each with its own
  rule. Medium, needs a `SAVE_VERSION` bump. Probably best left to the weapons round now that it comes first.

## Epic skills
Approved 22 October 2026 (`plan.md`, classes): epics from hidden teachers, a tier above the elites on key 6. Still
open: which epics there are (one or two per class), what each teacher asks first, and how many teachers per world.

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

## Dungeons (from the thread "Dungeons zoals ze nu zijn", 22 October 2026)
The design so far is in `docs/plan.md`, "Dungeons on their own land"; the files are in `/mnt/project-files/dungeons/`.
- **The fixed plan of each kind of place**, to work out with a mockup per kind when it is built: the temple, the abbey
  or monastery, the fort, the manor, the barrow, an ordinary goblin hole and the goblin village. The direction is in
  plan.md (an abbey always has a cloister, a refectory and cells; the goblin village is built like a settlement); the
  exact layout of each is still open.
- **The list of theme rooms and pieces** for K5 and the fixed plans: which special rooms exist, per kind of place and
  per part (entrance, arrival, middle, bottom). Nilio can also draw his own in the editor.
- **The editor's controls**, for a separate thread later. What we know so far:
  - **What it is:** its own program, "Avarenthia Editor", modelled on REXPaint; it comes with the test build ("Avarenthia (test)"), not with the players' download.
  - **Mouse and keyboard.** The mouse is welcome here, unlike in the game.
  - **Tools:** cell, line, rectangle, fill, copy and paste, undo and redo, change colour, zoom.
  - **Layers:** ground, things, creatures and triggers. Events in the trigger layer are picked from lists (when, if, then).
  - **Making and testing:** New → kind of place → part; Try puts the hero into the drawing at once; Save puts the file
    in "My pieces".
  - **Getting it into the game:** Nilio hands the file over and it goes into the repo; CI packs and seals it.
  - **Still to design:** the shortcut keys, how the palette looks, and where the layers and the Try button sit.

## Smaller loose ends
- **Northern lights:** still only weather; their gift (what they do for the player) was never settled.
- **The player as a ruler:** decided no (17 October 2026), but Nilio said he may come back to it.
- **Later, not planned:** crafts guilds, leadership, a house of your own (`plan.md`, At a glance).
- **The bard** stays parked (`docs/parked.md`), and so do the werewolf's and the vampire's curse.
- **Small bug, not fixed:** the help line in `ui.py` lists only 5 of the life skills.

Settled, no longer open: the visible weather border between regions (thread "Seizoenen in de wereld"; Nilio said
it is not needed) and the class system (approved 19 October 2026, "we kunnen later nog sleutelen").
