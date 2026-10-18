# Avarenthia: notes for Claude

ASCII open-world RPG in Python + python-tcod by Nilio (GitHub NilioDev, repo NilioDev/Avarenthia, formerly Cursed-Vale).
The plan for the next rounds of work is in `docs/plan.md`; read it before building.

## Working with Nilio
- Talk to him in **Dutch**. Everything in the game and the README is **English**.
- When he says "bouw/genereer/pas nog niets aan": discuss only, change nothing.
- He is the only tester: he plays a build, then sends feedback. Keep reports short; no step-by-step recaps.
- Standing taste: keyboard only, few hotkeys (no vi-keys: `h` is the hireling); calm Dwarf Fortress-like look;
  roguelike seriousness; no loot piñatas (only those who use gear drop gear); weigh the money balance in everything
  (jobs pay modestly, trade pays, coin goes on beds, repairs, wages, the temple). No taunts. One save only.
- No light-as-a-resource: the player never carries or manages a torch.
- Monster names: myth and folklore names are fine; names invented by RPG publishers (beholder, mind flayer, owlbear,
  displacer beast, Shadowdark's own creatures...) get our own names.

## The UI rule (Nilio, 17 Oct 2026)
Every new version must fit the layout, see "The UI rule" in `docs/plan.md`: lists go in a journal tab, things on the
land in a world-map layer (keys 1-6, L), where-you-stand in the line under the map, fights in IN SIGHT; signs are
named by the data (`guide.py`); a new key is taught by one first-time tip (`guide.TIPS`), never by screen text.
Keys are learnt by playing: don't add hints like "c: your numbers" to the screen.

## The handbook rule (Nilio, 17 Oct 2026)
`?` opens The Adventurer's Handbook (`avarenthia/handbook.py`, drawn by `ui.BookScreen`). Every change to the game updates the handbook in the same commit: a new
or changed system gets its sentences in the right chapter, a removed one loses them. In the build report, quote the
new or changed handbook lines (Nilio reads them there). Style: plain short English; a key is always in square brackets,
`[e]`, `[Shift+Tab]` (drawn as a gold keycap); a map sign is never in brackets but stands free in its own colour, with
"the sign" before it where needed ("tomes, the sign ≡"); no parentheses around keys or signs.

## Code map (biggest files first)
- `avarenthia/ui.py` all screens; `engine.py` game rules; `towns.py` settlement maps; `weather.py`; `world.py`;
  `terrain.py` (climate, rivers, wonders); `heightmap.py` (the shape of the land: Azgaar-like templates); `data.py` tiles, monsters, items; `missions.py` jobs; `jobs.py` the many job kinds (round 4); `guilds.py`; `mercs.py` hirelings and threat;
  `news.py` news through people; `harbour.py`; `hidden.py` old ways; `lifeskills.py` fishing etc.
  `folk.py` the peoples' own lands (halfling country and hill homes, hidden elven glades, the city under the Elder Tree,
  gnome hamlets); `tribes.py` hostile peoples' camps (warn, then rouse; captives; kobold toll); `deephold.py` dwarf holds,
  villages, mines (`dress_mine`), digging (`mining` life skill) and the cart line.
  `lands.py` the finer grain of the land: newer biomes and their effects (sight, ambush, cost, packs, foraging),
  named stretches of country (`world.areas`), oasis camps and herders' huts.
  `seasons.py` the year on the world map (snow, ice, passes, leaves, fires; dusk/dawn by season); `living.py` battlefields,
  plundered villages, rivals, ferries, crossroads shrines, ships; `sailing.py` skippers, voyages, pirates, the cove;
  `realms.py` the empire, kings, barons, houses and wars; `powers.py` the other powers (grudges, the wood, the Gorvash,
  raiders, church, Watch, companies, revolts, pretender, witches); `seats.py` their places' maps; `realmjobs.py` the
  'realm' jobs; `history.py` the made history and the libraries;
  `spellmap.py` what spells leave on the ground (burning ground, ice walls, roots...) and corpses;
  `guide.py` the look legend, Signs and first-time tips; `anim.py` small tile animations (the screen redraws on a timer only while one is in view: `GameScreen.moving`).
- World size: `world.WORLD_W/H` = 480 x 270. Counts made for the old 320 x 180 world go through `world.scaled(n)`.
- Choice dialogs: `EV.ask(game, key, title, text, options, **ctx)` + `EV.RESOLVERS[key] = fn(game, choice, ctx)`.
- UI requests: `game.request = ('shop', ...)` etc., handled in `App.after_action`.
- Buffs: `p.buffs = [[kind, value, turns, label]]`. Money in copper (100c = 1s, 100s = 1g).
- Bump `SAVE_VERSION` in engine.py whenever saved data changes shape.

## Tests and CI
- `python tests/test_headless.py` (no tcod needed). Parts: `TEST_ONLY=part1,part2`, seed: `TEST_SEED=n`.
  Run seeds one after another (they share a save file); `smoke` takes ~5 minutes, run it on its own.
- `python tests/bot.py 2` lets a bot play.
- `text_fits` fails when a sentence is cut short with "…": wrap text, don't truncate it.
- Push to `main`; GitHub Actions runs the tests and builds Windows/macOS/Linux executables.
- Screenshots for checking: `tools/screenshot.save(canvas, path, scale)` with `canvas.FakeCanvas`.
