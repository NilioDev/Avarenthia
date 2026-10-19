# Open: still to talk about

Questions and choices that wait for Nilio, gathered 19 October 2026 so nothing is forgotten. Each heading is a
name he can use ("open.md", "open: debug menu"). When a point is settled, write the decision into `plan.md`
(or `built.md`) and delete it here.

## Build order
What `plan.md` says now: weapons, then classes (in three parts, a pause after each), then the rest of the spell
effects, then round 6. Each starts only on Nilio's "ga".
- **Where do life skills go?** Their content is complete and approved (`plan.md`, "Life skills"), but they have no
  place in the order yet. Proposed: after the classes, because Smithing needs the new weapon kinds.

## Life skills: masters who unmake for coin
Masters at rank 40 can Unmake a found power onto their own crafted gear, with a chance to fail. Open: may masters
in the world (NPCs) do this for the player for coin? Proposed: no, so the rares stay what players hunt and the
craft stays the player's own. (Thread "Life skills sparren".)

## Debug menu
Proposal in project files `debug/voorstel.md` (a `--debug` flag and F12, its own `debug.sav`, snapshots, a
bug-report key that writes screenshot, seed, place, log and save). Nothing built. Two questions:
- Only with `--debug`, or also in the built executables, for example with a `debug.txt` next to the .exe?
- Keep it out of the handbook (it is not a rule of the game)? Proposed: yes.
(Thread "Debugmenu voor testen".)

## Spell effects: what is left
Part 1 is built (toolkit, status colours, Wild Shape colours, monsters' arrows and spells, the full/short/off
option). Still to do, not to decide: each school its own hand (Meteor's shadow and slanting fall, the corpse that
greys and rises, Morrak's Bargain pulling your own life out first, rings and waves) and the one white frame of a
great lightning stroke. Still to work out: the **weapon skills' effects** (a swing arc, arrows that fly, blood on
Sever Artery, a `*` on a critical), together with the weapon skills.

## Quick wins not taken
From the thread "Quick wins uit het plan"; items 1-5 were built, these two were not:
- **Market day and rest day** (round 6, item 3): one market day a week with extra stalls and better prices; on the
  rest day the temple is full and the shops are shut. Small to medium; `calendar.weekday()` is still unused. Build
  it early on its own, or wait for round 6?
- **Five new weapons without skills first:** scimitar, flail, war hammer, cestus and tiger claws, each with its own
  rule. Medium, needs a `SAVE_VERSION` bump. Probably best left to the weapons round now that it comes first.

## Project Gorgon skills
Nilio wants to go through the skills on https://wiki.projectgorgon.com/wiki/Skills together and see whether
anything there suits our game (ideas only, never their text or names). Not looked at yet.

## Multiplayer
Nilio wants to look into multiplayer later: whether it can work in this game at all, and in what form. Not looked
at yet.

## Smaller loose ends
- **Northern lights:** still only weather; their gift (what they do for the player) was never settled.
- **The player as a ruler:** decided no (17 October 2026), but Nilio said he may come back to it.
- **Later, not planned:** crafts guilds, leadership, a house of your own (`plan.md`, At a glance).
- **The bard** stays parked (`docs/parked.md`).
- **Small bug, not fixed:** the help line in `ui.py` lists only 5 of the life skills.

Settled, no longer open: the visible weather border between regions (thread "Seizoenen in de wereld"; Nilio said
it is not needed) and the class system (approved 19 October 2026, "we kunnen later nog sleutelen").
