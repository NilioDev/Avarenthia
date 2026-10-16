# Avarenthia: notes for Claude

ASCII open-world RPG in Python + python-tcod by Nilio (GitHub NilioDev, repo NilioDev/Cursed-Vale).
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

## Code map (biggest files first)
- `avarenthia/ui.py` all screens; `engine.py` game rules; `towns.py` settlement maps; `weather.py`; `world.py`;
  `terrain.py` (climate, rivers, wonders); `heightmap.py` (the shape of the land: Azgaar-like templates); `data.py` tiles, monsters, items; `missions.py` jobs; `jobs.py` the many job kinds (round 4); `guilds.py`; `mercs.py` hirelings and threat;
  `news.py` news through people; `harbour.py`; `hidden.py` old ways; `lifeskills.py` fishing etc.
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
