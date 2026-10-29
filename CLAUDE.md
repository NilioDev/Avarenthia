# Avarenthia: notes for Claude

ASCII open-world RPG in Python + python-tcod by Nilio (GitHub NilioDev, repo NilioDev/Avarenthia, formerly Cursed-Vale).
The plan for the next rounds of work is in `docs/plan.md`; read it before building. What is already built is in
`docs/built.md` (summaries and the specs of built rounds): read only the section a round touches, never the whole file.
Questions still to discuss with Nilio are in `docs/open.md`; when he says "open.md" or names one of its headings, read it.
What each new thing needs to be testable in the test build (debug menu) is in `docs/testing.md`: when a new proposal is
approved, add its lines there in the same commit (Nilio, 23 Oct 2026).

## Keeping plan.md short (Nilio, 18 Oct 2026)
`docs/plan.md` holds only what is still to build. When a round is built, move its spec section and its At a glance
row from `plan.md` to `docs/built.md` in the same commit (summary in built.md's Built list, spec as
"## <name> (built <date>; the spec)"). A new approved proposal goes into `plan.md` as a short spec; long detail stays
in the project files and is linked.

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
  `k5.py` the maker of classic dungeon levels (Brogue-like); `pieces.py` the drawn pieces (`pieces/*.des`, format in
  `pieces/README.txt`, packed and sealed by `tools/pack_pieces.py` in CI); `themes.py` theme rooms, their telling things
  and the mood lines of rooms; `underground.py` rivers of water and fire, swimming; `oldplaces.py` old places from the history (battlefields, deserted villages, broken bridges, memorials, quarries, wrecks, hermitages, leper colonies, the peoples' marks); `aurora.py` the northern lights' gift (rune stones, cheaper Frost/Storm, barrow spirits, the glow); `rift.py` the Rift and the Ashen Deep;
  `varnish.py` the Varnish: ruined cities in the zones, their places, the Northern Wall, league stones, the hidden deeps
  and their bosses, pages and bound books, the five riddles (state on `world.varnish` and `p.varnish`); `varnishtexts.py`
  their texts (fragments, 27 books, riddles);
  `epics.py` the epics on key 6 (classes part 4): the 22, their teachers' huts, deeds and hooks (state on `p.epic`);
  `places.py` temples, towers and barrows of every people on their own land (who may go how far, stairs, the hidden
  bottom); `towers.py` tower plans and floors, the haze below, the lookout, edges and falls; `temples.py` each
  people's temple; `barrows.py` each people's barrow and the bier;
  `halls.py` each people's abbey, fort and manor (the floor above: style 'upper'; who holds a fort; telling things);
  `delves.py` the underground kinds' own plans (rooms by use, folk where they belong, the goblin hole's watch and
  snares); `gobvillage.py` the goblin village behind the ravine and its deep halls;
  `arts.py` the arts of Cunning and Arcane (first blow, snares, runes, gates, dispel); `spellmap.py` what spells leave on the ground (burning ground, ice walls, roots...) and corpses;
  `weapons.py` the weapons' own rules (reach, crossbows, two weapons, fists, `armoured`); `bestiary.py` what
  you know of each creature kind (on the player); `classes.py` who you become (classes, pair names, the bar); `weaponskills.py` keys 1-2 per weapon kind and the
  family rules; `trees.py` the class trees (knots as data, `tuned` + hooks) and the 66 rules (`RULES`); `guide.py` the look legend, Signs and first-time tips; `debug.py` + `debug_ui.py` the debug menu (F12, test build
  and `--debug` only; not in the handbook); `anim.py` small tile animations (the screen redraws on a timer only while one is in view: `GameScreen.moving`).
- World size: `world.WORLD_W/H` = 480 x 270. Counts made for the old 320 x 180 world go through `world.scaled(n)`.
- Choice dialogs: `EV.ask(game, key, title, text, options, **ctx)` + `EV.RESOLVERS[key] = fn(game, choice, ctx)`.
- UI requests: `game.request = ('shop', ...)` etc., handled in `App.after_action`.
- Buffs: `p.buffs = [[kind, value, turns, label]]`. Money in copper (100c = 1s, 100s = 1g).
- Bump `SAVE_VERSION` in engine.py whenever saved data changes shape.

## Multiplayer later (Nilio, 22 Oct 2026)
Real multiplayer may come (see "Multiplayer" in `docs/open.md`). So: whatever belongs to the player (gear, money,
jobs, what they know, what they were told, where they are) lives on the player, never loose on the game or world.

## Tests and CI
- `python tests/test_headless.py` (no tcod needed). Parts: `TEST_ONLY=part1,part2`, seed: `TEST_SEED=n`.
  Run seeds one after another (they share a save file). A full seed takes ~23 minutes (`smoke` ~9 of them);
  almost every part spends ~17 s making a fresh world.
- How much to test (Nilio, 18 Oct 2026; saves his usage limit):
  - After each round: only that round's own part (`TEST_ONLY=<part>`), plus `text_fits` when text changed.
  - Once, at the end of a build, before merging to `main`: seeds 1-3, then `smoke`, then the bot.
  - CI runs the whole suite (seed 1 with `smoke`) on every push: read its result, don't run it again locally.
- `python tests/bot.py 2` lets a bot play.
- The wiki (Nilio, 25 Oct 2026): `python tools/wiki/build_wiki.py` writes `wiki/avarenthia-wiki.html` from the code and
  docs (lore, great evils, monsters, skills, classes, items, the handbook, plan.md); CI builds it on every push as the
  artifact "Avarenthia wiki". A new data table worth reading gets a few lines there.
- `text_fits` fails when a sentence is cut short with "…": wrap text, don't truncate it.
- Push to `main`; GitHub Actions runs the tests and builds Windows/macOS/Linux executables.
- Screenshots for checking: `tools/screenshot.save(canvas, path, scale)` with `canvas.FakeCanvas`.
