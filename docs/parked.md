# Parked: to be researched further before building

Taken out of docs/plan.md on 16 October 2026 at Nilio's request. Do not build these until he says so.

The jobs that were parked here went back into docs/plan.md as round 4 on 16 October 2026.

### The bard (round 4 of the old plan)
| **The Lark's Company** (Skell) | bard | new: Song | Inspire (you and your hireling fight better), Dirge (enemies near are weaker), Discord (one enemy confused); no taunt | great inns of the cities; perform for coin, hear more news from further, better prices | none |
- Two-guild technique: Lark's + Thieves: Silver Tongue (deceive, distract).

### The werewolf's and the vampire's curse (parked 22 October 2026)
From going through Project Gorgon's skills. A curse that befalls you instead of a skill you choose: bitten, you
change at full moon by night (`nature.moon`), the folk flee and the Watch attacks; the temple can lift it early, or
you learn to steer it. Nilio has thought about both himself and wants them much later, when the game stands more.
Details: project files `gorgon/voorstel.md`.

### Multiplayer (parked 22 October 2026; moved here from open.md 2 November 2026)
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
