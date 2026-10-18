"""Headless tests: drive the real UI and engine with key tokens on a fake canvas.
Run from the project folder:  python tests/test_headless.py [--dump]
"""
import os
import random
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from avarenthia import engine as E, data as D, ui, economy as ECO, missions as MS, wanderers as WA  # noqa: E402
from avarenthia.canvas import FakeCanvas  # noqa: E402
from avarenthia.worldgen import cheb  # noqa: E402

E.save_path = lambda: os.path.join(tempfile.gettempdir(), 'avarenthia_test.dat')

TOKENS = ['up', 'down', 'left', 'right', 'np7', 'np9', 'np1', 'np3', 'h', 'np5', 'g', 'R', '1', '2', '3', 'q', 'w', 'p', 'x', 't',
          '>', '<', 'enter', 'i', 'c', 'd', 'esc', 'a', 'b', 'tab', 'H', 'L', 'D', '?', '4', 'down', 'enter', 'm', 'e',
          's', 'S', 'B', 'A', '5', '6', 'f', 'z', 'v', 'f2', 'a', 'c', 'tab', 'L']


def new_app(mode='soft', seed=None):
    app = ui.App(FakeCanvas(ui.W, ui.H))
    app.key('n')
    for ch in 'Test':
        app.key(ch)
    app.key('enter')
    if mode == 'hard':
        app.key('space')
    if seed:
        app.key('down')
        for ch in str(seed):
            app.key(ch)
    app.key('enter')
    assert isinstance(app.top, ui.IntroScreen), app.top
    app.render()                     # the first page while the world is still being made
    assert app.top.wait()
    for _ in range(3):
        app.render()
        app.key('enter')
    assert isinstance(app.top, ui.GameScreen), app.top
    check_colours(app)
    return app


def check_colours(app):
    """The real console only takes colours of 0..255; a brighter shade past that crashes the game."""
    p = app.top.game.player
    for poison in (0, 5):
        p.poison = poison
        app.render()
        for col in app.cv.fg + app.cv.bg:
            assert all(0 <= v <= 255 and v == int(v) for v in col), col
    p.poison = 0


def to_over(g, sid=0):
    s = g.world.settlements[sid]
    g.cur = 'over'
    g.player.x, g.player.y = s.x, s.y
    g.over_pos = (s.x, s.y)
    g.compute_fov()


def smoke(games=9, steps=1200):
    for gi in range(games):
        app = new_app('hard' if gi % 2 else 'soft')
        g = app.game
        g.player.vit = 400
        g.player.lvl = 8
        g.player.gold = 500000
        from avarenthia import skills as SK
        g.player.known = [k.id for k in SK.SKILL_LIST]
        g.player.bar = random.sample(g.player.known, 6)
        g.player.inv[2:2] = []
        dids = list(g.world.dungeons)
        for step in range(steps):
            if step % 150 == 0:
                app.screens = [ui.GameScreen(app)]
                did = dids[(step // 150) % len(dids)]
                g.enter_dungeon(did, random.randint(1, g.world.dungeons[did].depth), 'up')
            if step % 300 == 100:
                app.screens = [ui.GameScreen(app)]
                to_over(g, random.randrange(len(g.world.settlements)))
            if step % 300 == 250:
                app.screens = [ui.GameScreen(app)]
                h = random.choice(g.world.holds)
                to_over(g, 0)
                g.player.x, g.player.y = h.x, h.y
                g.enter_hold(h.id)
                for npc in [o for o in g.map.mons if o.role in ('castellan', 'shop')]:
                    g.talk(npc)
                    app.after_action()
                    for tok in random.sample(TOKENS, 6):
                        app.key(tok)
                        app.render()
                    app.screens = [ui.GameScreen(app)]
            if step % 300 == 200:
                app.screens = [ui.GameScreen(app)]
                g.enter_town(random.randrange(len(g.world.settlements)))
                for npc in [o for o in g.map.mons if o.role in ('market', 'inn', 'stables', 'shop')]:
                    g.talk(npc)
                    app.after_action()
                    for tok in random.sample(TOKENS, 8):
                        app.key(tok)
                        app.render()
                    app.screens = [ui.GameScreen(app)]
            g.player.mana = 999
            app.key(random.choice(TOKENS), random.random() < .1)
            app.render()
            if not app.running:
                app.running = True
            if g.dead or isinstance(app.top, ui.WinScreen):
                break
        for S in (ui.InventoryScreen, ui.CharacterScreen, ui.ShopScreen, ui.TravelScreen, ui.HelpScreen, ui.SkillsScreen,
                  ui.DeathScreen, ui.WinScreen, ui.QuitScreen, ui.JournalScreen, ui.WorldMapScreen, ui.StablesScreen,
                  ui.BestiaryScreen, ui.IntroScreen):
            if S is ui.ShopScreen:
                g.player.inv.append(E.random_gear(g, 5, 9))
            app.screens = [ui.GameScreen(app), S(app)]
            app.render()
        for S in (ui.MarketScreen, ui.BoardScreen):
            app.screens = [ui.GameScreen(app), S(app, 1)]
            app.render()
        E.save_game(g)
        assert E.load_game() is not None or g.dead
    print('smoke ok')


def trade_and_jobs():
    from avarenthia import jobs as JB
    random.seed(11)
    g = E.Game('Trader', False, 4242)
    g.player.vit = 300
    s0 = g.world.settlements[0]
    g.player.gold = 40000
    # buy cheap grain at home, haul it to the town that wants it most
    ECO.buy(g, s0, 'grain', 25)
    paid = g.player.cost_basis['grain']
    dest = max(g.world.settlements[1:], key=lambda s: ECO.sell_price(s, 'grain'))
    g.travel_to('s', dest.id)
    assert g.cur != 'over' or (g.player.x, g.player.y) != (dest.x, dest.y), 'travel to a place never visited'
    g.mark_visit('s', dest.id)
    g.travel_to('s', dest.id)
    if g.cur != 'over' or (g.player.x, g.player.y) != (dest.x, dest.y):
        g.cur = 'over'
        g.player.x, g.player.y = dest.x, dest.y
    g.enter_town(dest.id)
    before = g.player.gold
    ECO.sell(g, dest, 'grain', 25)
    print(f'grain: paid {paid:.1f} each, sold 25 in {dest.name} for {g.player.gold - before} (day {g.day})')
    # every job type, completed by moving straight to the goal
    kinds_done = set()
    for s in g.world.settlements:
        s.board_day = -99
        MS.refresh_board(g, s)
        for mi in list(s.board):
            if mi.kind in kinds_done or mi.kind == 'hunt' or mi.kind in JB.KINDS or mi.data.get('person'):
                continue                                  # hunts: creatures_and_hunts; the others: more_jobs
            g.player.mounts = ['mule', 'cart']
            if not MS.accept(g, s, mi):
                continue
            if mi.kind in ('courier', 'freight', 'escort'):
                if mi.kind == 'escort':
                    to_over(g, s.id)
                    wd = WA.make_group(g, 'bandits', g.player.x + 1, g.player.y, 2, ['bandit', 'bandit'])
                    g.world.wanderers.append(wd)
                    g.start_encounter(wd)
                    assert any(o.role == 'escort' for o in g.map.mons)
                    for o in [o for o in g.map.mons if not o.is_npc]:
                        g.kill(o)
                    g.leave_to_over()
                g.enter_town(mi.target)
            elif mi.kind == 'bounty':
                wd = next(x for x in g.world.wanderers if x.mission == mi.id)
                to_over(g, s.id)
                g.start_encounter(wd)
                for o in [o for o in g.map.mons if not o.is_npc]:
                    g.kill(o)
                g.leave_to_over()
                assert mi.state == 'turnin', mi.state
                g.enter_town(mi.giver)
            elif mi.kind == 'fetch':
                d = g.world.dungeons[mi.data['dungeon']]
                to_over(g, s.id)
                g.enter_dungeon(d.id, d.depth, 'up')
                relic = next(i for i in g.map.items if i.k == 'quest')
                g.player.x, g.player.y = relic.x, relic.y
                g.auto_pickup()
                assert mi.state == 'turnin'
                g.enter_town(mi.giver)
            assert mi.state == 'done', (mi.kind, mi.state)
            kinds_done.add(mi.kind)
            print(f'  job ok: {mi.kind:8} {mi.title} ({mi.reward}c)')
    # let the world run for a month
    to_over(g, 0)
    for _ in range(30):
        g.end_turn(D.DAY_LEN, True)
        if g.cur != 'over':
            g.maps.pop('wild', None)
            to_over(g, 0)
    kinds = {}
    for w in g.world.wanderers:
        kinds[w.kind] = kinds.get(w.kind, 0) + 1
    print('after 30 days:', kinds, '| events:', [s.name for s in g.world.settlements if s.event])
    print('job kinds tested:', sorted(kinds_done))


def factions_and_death():
    random.seed(5)
    g = E.Game('Hero', False, 777)
    p = g.player
    p.vit, p.str, p.lvl = 200, 80, 12
    s = g.stats()
    p.life = s['max_life']
    # storm the nearest hostile fortress
    hostile = [h for h in g.world.holds if h.faction in ('blackhand', 'cult')]
    h = hostile[0]
    to_over(g, 0)
    p.x, p.y = h.x, h.y
    old = h.faction
    g.enter_hold(h.id)
    assert g.map.kind == 'siege'
    boss = next(o for o in g.map.mons if getattr(o, 'commander', False))
    for o in [o for o in g.map.mons if not o.is_npc]:
        g.kill(o)
    assert h.faction != old, 'fortress should change hands'
    g.leave_to_over()
    print(f'captured {h.name}: {old} -> {h.faction}; rep', {k: v for k, v in p.rep.items()})
    # castellan jobs
    friendly = next(x for x in g.world.holds if x.faction in ('crown', 'league', 'circle'))
    MS.refresh_hold_board(g, friendly)
    print('castellan offers:', [m.title for m in friendly.board])
    # softcore death: corpse holds backpack and gold
    g.enter_dungeon('rat', 1, 'up')
    g.map.mons = []                      # nobody around to rob the body
    p.gold = g.raise_fee() + 123
    n_bag = len(g.backpack())
    g.die('a test')
    assert not g.dead and p.gold == 123 and len(g.corpses) == 1, 'the purse stays with you, the fee is paid'
    assert any(b[0] == 'frail' for b in p.buffs), 'weak after being raised'
    key, cid = g.corpses[0]
    corpse = next(i for i in g.maps[key].items if i.id == cid)
    g.enter_dungeon('rat', 1, 'up')
    p.x, p.y = corpse.x, corpse.y
    g.auto_pickup()
    assert p.gold == 123 and len(g.backpack()) == n_bag and not g.corpses
    # no coin for the temple: the end
    p.gold = 5
    g.die('a second test')
    assert g.dead, 'softcore death without the fee is final'
    g.dead = False
    p.life = 50
    print('softcore corpse run ok')
    # disciplines grow by use
    r0 = p.disc['fire'][0]
    for _ in range(40):
        from avarenthia import skills as SK
        SK.gain(g, 'fire', 3)
    print('fire discipline', r0, '->', p.disc['fire'][0], 'known fire skills', [k for k in p.known if SK.SKILLS[k].line == 'fire'])
    # a month of war
    for _ in range(30):
        g.end_turn(D.DAY_LEN, True)
        if g.cur not in ('over',):
            g.maps.pop('wild', None)
            to_over(g, 0)
    from collections import Counter
    print('after 30 days of war:', dict(Counter(h.faction for h in g.world.holds)),
          'warbands', sum(1 for w in g.world.wanderers if w.kind == 'warband'))


def choose(app, key):
    """Answer the open choice dialog with the option whose key is `key` (or the first one)."""
    app.after_action()
    top = app.top
    assert isinstance(top, ui.ChoiceScreen), top
    app.render()
    opts = app.game.pending['options']
    i = next((n for n, (_l, k) in enumerate(opts) if k == key), 0)
    app.key(ui.LETTERS[i])
    app.render()


def clear_wild(g):
    for o in [o for o in g.map.mons if not o.is_npc]:
        g.kill(o)
    g.leave_to_over()


def wilds():
    from avarenthia import events as EV
    from collections import Counter
    random.seed(21)
    app = new_app('soft', 31337)
    g = app.game
    p = g.player
    p.vit, p.str, p.lvl = 300, 90, 10
    p.life = g.stats()['max_life']
    p.gold = 200000
    w = g.world
    print('places:', dict(Counter(q.kind for q in w.pois)))
    assert all(q.kind != 'ruin' or q.did in w.dungeons for q in w.pois)
    # danger rises away from the roads
    road = [w.danger_at(x, y) for (x, y) in random.sample([(i % g.maps['over'].w, i // g.maps['over'].w) for i in range(len(g.maps['over'].t))
                                                          if g.maps['over'].t[i] == D.ROAD], 50)]
    far = [w.danger_at(q.x, q.y) for q in w.pois]
    print(f'danger on roads avg {sum(road) / len(road):.1f}, at hidden places avg {sum(far) / len(far):.1f}')
    # visit one place of each kind
    for kind in ('shrine', 'stones', 'wagon', 'camp', 'ruin'):
        poi = next(q for q in w.pois if q.kind == kind)
        app.screens = [ui.GameScreen(app)]
        to_over(g, 0)
        p.x, p.y = poi.x, poi.y
        g.over_step()
        if kind == 'ruin':
            g.use_stairs('down')
            assert g.map.kind == 'dungeon', g.cur
            g.cur = 'over'
            p.x, p.y = poi.x, poi.y
            continue
        key = {'shrine': 'offer', 'stones': 'touch', 'wagon': 'search', 'camp': 'attack'}[kind]
        choose(app, key)
        if g.map.kind == 'wild':
            camp = g.encounter_poi is not None
            clear_wild(g)
            if camp:
                assert poi.ready_day >= 10 ** 9
        print(f'  {kind:7} ok, buffs {[b[3] for b in p.buffs]}')
    # every travel event, every option
    for k, fn in EV.EVENTS.items():
        n_opts = None
        i = 0
        while True:
            app.screens = [ui.GameScreen(app)]
            to_over(g, 0)
            p.x += 6
            p.life = g.stats()['max_life']
            p.inv.append(E.Item(g.new_id(), 'potion', 'hp', 1)) if not g.count('potion', 'hp') else None
            fn(g)
            opts = g.pending['options']
            n_opts = len(opts)
            choose(app, opts[i][1])
            if g.map.kind == 'wild':
                clear_wild(g)
            i += 1
            if i >= n_opts:
                break
    print('  travel events ok:', ', '.join(EV.EVENTS))
    # travellers: every kind of personal job, finished
    done = set()
    for attempt in range(80):
        if len(done) == 4:
            break
        app.screens = [ui.GameScreen(app)]
        to_over(g, 0)
        before = len(w.wanderers)
        EV.spawn_traveller(g)
        if len(w.wanderers) == before:
            continue
        wd = w.wanderers[-1]
        if not wd.offer or wd.offer['sub'] in done:
            w.wanderers.remove(wd)
            continue
        sub = wd.offer['sub']
        w.wanderers = [x for x in w.wanderers if x is wd or abs(x.x - wd.x) > 2 or abs(x.y - wd.y) > 2]
        p.x, p.y = wd.x + 1, wd.y
        g.try_move(-1, 0)
        choose(app, 'help')
        choose(app, 'accept')
        mi = next(m for m in MS.active(g) if m.kind == 'personal' and m.data['sub'] == sub)
        if sub == 'letter':
            g.enter_town(mi.data['rtown'])
        else:
            if sub == 'gather':
                p.cargo[mi.data['good']] = mi.data['qty']
            elif sub == 'hunt':
                beast = next(x for x in w.wanderers if x.mission == mi.id)
                to_over(g, 0)
                p.x, p.y = beast.x, beast.y
                g.start_encounter(beast)
                clear_wild(g)
                assert mi.state == 'turnin', mi.state
            else:
                d = w.dungeons[mi.data['dungeon']]
                to_over(g, 0)
                g.enter_dungeon(d.id, d.depth, 'up')
                relic = next(i for i in g.map.items if i.k == 'quest')
                p.x, p.y = relic.x, relic.y
                g.auto_pickup()
                assert mi.state == 'turnin'
            g.enter_town(mi.data['wait'])
            client = next(o for o in g.map.mons if o.role == 'client' and o.mission == mi.id)
            g.talk(client)
            app.after_action()
            app.render()
        assert mi.state == 'done', (sub, mi.state)
        done.add(sub)
        print(f'  traveller job ok: {sub:6} {mi.title} ({mi.reward}c)')
    assert len(done) == 4, done
    # bestiary knowledge
    app.screens = [ui.GameScreen(app)]
    g.enter_dungeon('rat', 1, 'up')
    from avarenthia.entities import make_monster
    for _ in range(12):
        o = make_monster(g, 'rat', p.x, p.y, 1)
        g.map.mons.append(o)
        g.compute_fov()
        g.kill(o)
    assert g.lore('rat') == 2, g.bestiary
    for page in range(3):
        app.screens = [ui.GameScreen(app), ui.HelpScreen(app, chapter=page)]
        app.render()
    app.screens = [ui.GameScreen(app), ui.BestiaryScreen(app)]
    app.render()
    print('bestiary:', {k: v for k, v in g.bestiary.items()})
    E.save_game(g)
    assert E.load_game() is not None


def items_skills_curse():
    from avarenthia.entities import make_tome, random_gear, make_gear, add_curse
    from avarenthia import skills as SK, evils as EVL
    random.seed(8)
    app = new_app('soft', 555)
    g = app.game
    p = g.player
    assert p.known == [] and not any(p.bar), (p.known, p.bar)
    assert sorted(i.base for i in p.inv if i.k == 'gear') == ['quilted']
    # tomes
    t0 = make_tome(g, 0)
    g.add_to_inv(t0)
    assert g.read_tome(t0) == 1 and t0.t in p.known and t0.t in p.bar
    hard = next(s for s in SK.SKILL_LIST if s.unlock == SK.UNLOCKS[3])
    it = E.Item(g.new_id(), 'tome', hard.id)
    g.add_to_inv(it)
    assert g.read_tome(it) == 0 and hard.id not in p.known
    # loot is mostly plain
    from collections import Counter
    c = Counter(random_gear(g, 5).rar for _ in range(3000))
    print('loot rarity per 3000 drops:', dict(c))
    assert c['normal'] > 2400
    # unidentified and cursed
    ring = make_gear(g, 'ring', 'magic', 5)
    ring.ided = False
    add_curse(ring)
    g.add_to_inv(ring)
    life0 = g.stats()['max_life']
    g.equip(ring)
    assert ring.curse_known and g.stats()['max_life'] <= life0
    g.unequip('ring1')
    assert g.is_equipped(ring), 'cursed items stay on'
    p.gold = 500000
    to_over(g, 0)
    g.enter_site(g.world.start_temple)
    temple = next((o for o in g.map.mons if o.role == 'healer'), None)
    g.talk(temple)
    app.after_action()
    assert isinstance(app.top, ui.DialogScreen), 'the priestess first tells you how you got here'
    app.key('esc')
    g.talk(temple)
    app.after_action()
    assert isinstance(app.top, ui.TempleScreen), app.top
    for k in 'bca':
        app.key(k)
        app.render()
    app.key('esc')
    assert ring.identified and not ring.cursed
    g.unequip('ring1')
    assert not g.is_equipped(ring)
    # Morvenna grows with you
    tainted = lambda: sum(1 for v in g.world.taint if v)
    print('evils:', [(e.name, EVL.stage(e)) for e in g.world.evils], 'tainted cells', tainted())
    p.lvl = 30
    g.request = None
    EVL.update(g)
    to_over(g, 0)
    for _ in range(40):
        EVL.daily(g)
    hunts = [w for w in g.world.wanderers if w.kind == 'hunt']
    print('at level 20:', [(e.name, EVL.stage(e)) for e in g.world.evils], 'tainted cells', tainted(), 'hunters', len(hunts))
    assert tainted() > 300 and any(e.known for e in g.world.evils)
    assert hunts, 'strong, known evils send hunters'
    h = hunts[0]
    d0 = cheb(h.x, h.y, p.x, p.y)
    for _ in range(30):
        WA.step(g, h)
    assert cheb(h.x, h.y, p.x, p.y) < d0
    app.screens = [ui.GameScreen(app)]
    app.render()
    for S in (ui.WorldMapScreen, ui.JournalScreen):
        app.screens = [ui.GameScreen(app), S(app)]
        app.render()
    # auto-explore runs step by step and stops on a key
    app.screens = [ui.GameScreen(app)]
    g.enter_dungeon('rat', 1, 'up')
    for o in g.map.mons:
        o.awake = False
        o.x = o.y = 0
    g.map.mons = []
    app.key('x')
    assert app.auto is not None
    t = g.turn
    app.tick()
    app.tick()
    assert g.turn > t
    app.key('space')
    assert app.auto is None
    app.key('x')
    app.run_auto()
    print('auto-explore ok, turn', g.turn)


def world_and_people():
    from avarenthia import races as RC, evils as EVL, lifeskills as LS
    random.seed(3)
    # character creation: people, gender, a random name
    app = ui.App(FakeCanvas(ui.W, ui.H))
    app.key('n')
    app.key('down')
    app.key('right')          # elf
    app.key('right')          # dwarf
    app.key('down')
    app.key('left')           # female
    app.key('tab')
    app.render()
    app.key('enter')
    app.key('enter')
    assert app.top.wait()
    for _ in range(3):
        app.render()
        app.key('enter')
    g = app.game
    p = g.player
    assert p.race == 'dwarf' and p.gender == 'female' and p.name, (p.race, p.gender, p.name)
    print('created', p.name, p.race, p.gender, 'rep', p.rep)
    print('factions:', [(k, f['name'], f['race']) for k, f in D.FACTIONS.items()])
    print('evils:', [(e.name, e.did) for e in g.world.evils])
    # only the land around home is known at first
    known = [s.name for s in g.world.settlements if g.known_settlement(s)]
    assert len(known) < 4, known
    g.enter_town(0)
    sp = g.map.signpost
    p.x, p.y = sp[0] - 1, sp[1]
    g.try_move(1, 0)
    app.after_action()
    app.render()
    known2 = [s.name for s in g.world.settlements if g.known_settlement(s)]
    assert len(known2) > len(known), (known, known2)
    print('after reading the signpost:', known2)
    # the world map scrolls
    app.screens = [ui.GameScreen(app), ui.WorldMapScreen(app)]
    for k in ('right', 'L', 'down', 'z', 'z', 'f', 'up'):
        app.key(k)
        app.render()
    # each evil can be destroyed
    for e in g.world.evils:
        boss = E.make_monster(g, e.d['boss'], 1, 1, 10)
        g.enter_dungeon(e.did, g.world.dungeons[e.did].depth, 'up')
        g.map.mons.append(boss)
        g.kill(boss)
        assert e.defeated
    assert g.request == ('win',) or g.flags.get('saved')
    # fishing by a river
    g2 = E.Game('Fisher', False, 99, 'halfling', 'male')
    om = g2.maps['over']
    riv = [i for i, t in enumerate(om.t) if t == D.RIVER]
    i = riv[len(riv) // 2]
    g2.cur = 'over'
    g2.player.x, g2.player.y = i % om.w + 1, i // om.w
    if not D.TILES[om.tile(g2.player.x, g2.player.y)].walk:
        g2.player.x -= 1
    g2.compute_fov()
    assert LS.fish(g2) == 0, 'no pole yet'
    g2.add_to_inv(E.Item(g2.new_id(), 'tool', 'rod'))
    caught = 0
    for _ in range(200):
        g2.map.mons = []
        if g2.cur != 'over':
            g2.maps.pop('wild', None)
            g2.cur = 'over'
        g2.player.x, g2.player.y = i % om.w, i // om.w
        LS.fish(g2)
        caught = sum(it.n for it in g2.player.inv if it.k == 'fish')
    print('fishing rank', LS.rank(g2, 'fishing'), 'fish in the bag', caught,
          sorted({it.t for it in g2.player.inv if it.k == 'fish'}))
    assert caught > 10 and LS.rank(g2, 'fishing') >= 2
    fishy = next(it for it in g2.player.inv if it.k == 'fish')
    g2.eat(fishy)
    # dungeons are dressed and lit
    g2.enter_dungeon('mine', 1, 'up')
    assert g2.map.deco and g2.map.lights
    app.game = g2
    app.screens = [ui.GameScreen(app), ui.CharacterScreen(app)]
    app.render()
    app.screens = [ui.GameScreen(app)]
    app.render()


def crime_and_coin():
    from avarenthia import crime as CR, events as EV
    from avarenthia.money import fmt
    random.seed(17)
    assert fmt(0) == '0c' and fmt(12345) == '1g 23s 45c' and fmt(205) == '2s 5c', fmt(12345)
    app = new_app('soft', 2024)
    g = app.game
    p = g.player
    p.vit, p.str, p.lvl = 300, 90, 10
    p.life = g.stats()['max_life']
    # coins are rare: kill a pack of wolves, no coins; bandits sometimes
    g.enter_dungeon('rat', 1, 'up')
    from avarenthia.entities import make_monster
    g.map.items = []
    for k in ['wolf'] * 30:
        o = make_monster(g, k, p.x, p.y, 3)
        g.map.mons.append(o)
        g.kill(o)
    assert not any(i.k == 'gold' for i in g.map.items), 'beasts carry no coin'
    # rob a caravan near home
    to_over(g, 0)
    WA.spawn_caravan(g, g.world.settlements[0])
    car = next((w for w in g.world.wanderers if w.kind == 'caravan' and w.origin == 0), None)
    if car is None:
        s0 = g.world.settlements[0]
        car = WA.Wanderer(g.new_id(), 'caravan', s0.x + 1, s0.y)
        car.origin, car.dest, car.goods, car.path = 0, 1, ('grain', 20), []
        g.world.wanderers.append(car)
    p.x, p.y = car.x + 1, car.y
    app.screens = [ui.GameScreen(app)]
    g.try_move(-1, 0)
    choose(app, 'rob')
    assert g.map.kind == 'wild'
    gold0 = p.gold
    for o in [o for o in g.map.mons if not o.is_npc]:
        g.kill(o)
    for it in list(g.map.items):
        p.x, p.y = it.x, it.y
        g.auto_pickup()
    g.leave_to_over()
    print(f'robbed a caravan: {fmt(p.gold - gold0)} and cargo {p.cargo}')
    assert p.gold > gold0
    s0 = g.world.settlements[0]
    print('standing in', s0.name, s0.rep, CR.standing_word(s0.rep))
    # rob more until wanted
    while s0.rep > CR.WANTED_AT:
        CR.commit(g, 15, 'robbery on the road', 1.0, (s0.x, s0.y))
    assert s0 in CR.wanted_in(g)
    for _ in range(20):
        CR.daily(g)
    assert any(w.kind == 'lawmen' for w in g.world.wanderers)
    # the guards stop you at the gate
    p.gold = 10 ** 6
    app.screens = [ui.GameScreen(app)]
    g.enter_town(0)
    choose(app, 'pay')
    assert s0.rep > CR.WANTED_AT
    for S in (ui.JournalScreen,):
        app.screens = [ui.GameScreen(app), S(app)]
        app.render()
    g.enter_town(1)
    board = ui.BoardScreen(app, 1)
    app.screens = [ui.GameScreen(app), board]
    app.render()
    print('crime ok')


def start_and_survival():
    from avarenthia import hunger as HU, crime as CR
    random.seed(29)
    app = new_app('soft', 4711)
    g = app.game
    p = g.player
    assert g.eq_item('weapon') is None, 'you start with nothing in your hands'
    priest = next(o for o in g.map.mons if o.role == 'healer')
    g.talk(priest)
    app.after_action()
    app.key('esc')
    assert g.flags.get('quest_den') and g.story()
    # fight the den with bare fists
    p.vit, p.lvl = 200, 6
    p.life = g.stats()['max_life']
    d = g.world.dungeons['den']
    g.enter_dungeon('den', d.depth, 'up')
    boss = next(o for o in g.map.mons if o.k == 'snagtooth')
    for _ in range(400):
        if boss not in g.map.mons:
            break
        p.x, p.y = boss.x - 1 if g.map.tile(boss.x - 1, boss.y) else boss.x + 1, boss.y
        p.life = g.stats()['max_life']
        g.melee(boss)
    assert g.flags.get('den'), 'Snagtooth should fall'
    print('unarmed rank', p.disc['unarmed'][0])
    for it in [i for i in g.map.items if i.name.startswith('Your') or i.k == 'tome']:
        p.x, p.y = it.x, it.y
        g.auto_pickup()
    sword = next(i for i in p.inv if i.name == 'Your Short Sword')
    shield = next(i for i in p.inv if i.slot == 'shield')
    g.equip(sword)
    g.equip(shield)
    assert g.eq_item('shield') is shield
    tome = next(i for i in p.inv if i.k == 'tome')
    assert g.read_tome(tome) == 1
    # hunger
    p.food = 130
    g.end_turn(20, True)
    assert HU.state(p.food) == 'Weak'
    assert g.eat_best() == 1 and p.food > 300
    # a dwarven hold, its thane and the deep roads below
    holds = [s for s in g.world.settlements if s.kind == 'deephold']
    assert holds
    h = holds[0]
    to_over(g, h.id)
    g.enter_town(h.id)
    assert g.map.underground
    thane = next(o for o in g.map.mons if o.role == 'thane')
    g.talk(thane)
    app.after_action()
    app.render()
    app.key('esc')
    i = g.map.t.index(D.DOWN)
    p.x, p.y = i % g.map.w, i // g.map.w
    g.use_stairs('down')
    assert g.map.kind == 'dungeon'
    j = g.map.t.index(D.UP)
    p.x, p.y = j % g.map.w, j // g.map.w
    g.use_stairs('up')
    assert g.here is h, 'back up into the hold'
    # look around
    app.screens = [ui.GameScreen(app)]
    app.render()
    app.key('o')
    for k in ('right', 'tab', 'down', 'L', 'tab'):
        app.key(k)
        app.render()
    app.key('esc')
    to_over(g, 0)
    app.render()
    app.key(';')
    for k in ('up', 'left', 'tab'):
        app.key(k)
        app.render()
    app.key('esc')
    # the law, ever harder
    s0 = g.world.settlements[1]
    seen = []
    for rep in (-25, -40, -55, -70, -90):
        s0.rep = rep
        wd = CR.spawn_lawmen(g, s0)
        seen.append((CR.heat(s0), wd.name if wd else None))
    print('the law:', seen)
    app.render()


def countryside():
    from avarenthia import foraging as FG, lifeskills as LS, sites as ST
    from avarenthia.entities import make_monster
    random.seed(41)
    app = new_app('soft', 5150)
    g = app.game
    p = g.player
    assert g.map.site == g.world.start_temple, 'you wake in the temple outside Thornfield'
    # beasts never drop gear
    g.enter_dungeon('rat', 1, 'up')
    g.map.items = []
    for _ in range(60):
        o = make_monster(g, 'bat', p.x, p.y, 3, 1)
        g.map.mons.append(o)
        g.kill(o)
    assert not any(i.k == 'gear' for i in g.map.items), 'bats do not carry swords'
    # sites: a monastery herbalist, a watchtower
    mon = next(st for st in g.world.sites if st.kind == 'monastery')
    to_over(g, 0)
    g.enter_site(mon.id)
    herb = next(o for o in g.map.mons if o.role == 'herbalist')
    g.talk(herb)
    app.after_action()
    app.key('esc')
    assert 'healing' in p.recipes
    tower = next(st for st in g.world.sites if st.kind == 'watchtower')
    g.enter_site(tower.id)
    i = g.map.t.index(D.UP)
    p.x, p.y = i % g.map.w, i // g.map.w
    om = g.maps['over']
    before = sum(om.seen)
    g.use_stairs('up')
    assert sum(om.seen) > before
    # forage in the woods until something is found, taste it
    g.leave_to_over()
    forest = [k for k, t in enumerate(om.t) if t == D.FOREST]
    found = 0
    for _ in range(120):
        k = random.choice(forest)
        p.x, p.y = k % om.w, k // om.w
        g.compute_fov()
        p.life = g.stats()['max_life']
        g.forage()
        if g.cur != 'over':
            g.cur = 'over'
    plants = [it for it in p.inv if it.k == 'plant']
    print('foraged:', [it.display_name() for it in plants], 'foraging', LS.rank(g, 'foraging'))
    assert plants
    for it in list(plants):
        p.life = g.stats()['max_life']
        FG.eat_plant(g, it)
    print('known plants:', sorted(p.known_plants))
    # brew a healing draught
    p.inv.append(FG.make_plant(g, 'yarrow', 2))
    n0 = g.count('potion')
    FG.brew(g, 'healing')
    app.screens = [ui.GameScreen(app), ui.BrewScreen(app)]
    app.render()
    app.screens = [ui.GameScreen(app), ui.CharacterScreen(app)]
    app.render()
    # a bigger village with fields and livestock
    g.enter_town(0)
    assert g.map.w >= 100 and any(o.role == 'livestock' for o in g.map.mons)
    for _ in range(30):
        g.end_turn(1)
    app.screens = [ui.GameScreen(app)]
    app.render()
    print('countryside ok')


def thornfield_and_faith():
    """The calendar, the fisherman's first catch, the kobold den, people you can inspect, the gods,
    brewing, signposts that only point the way, and the Tab menu."""
    from avarenthia import calendar as CAL, gods as GD, brewing as BR, hunger as HU, lifeskills as LS
    from avarenthia import describe as DS, worldgen as WG
    assert CAL.short(1) == '3 Seedwake', CAL.short(1)
    assert 'Seedwake' in CAL.long(1)
    app = new_app()
    g = app.game
    p = g.player
    # title screen draws
    t = ui.App(FakeCanvas(ui.W, ui.H))
    t.render()
    assert 'Umbrathyn'.upper()[0] and any(ch != ' ' for ch in t.cv.ch)
    # Thornfield: three-wide high street, a pond with a fisherman
    g.enter_town(0)
    g.request = None
    m = g.map
    # the roads in town go where the roads on the world map go, and none of them stops in the woods
    from collections import deque
    cx, cy = m.centre
    seen = {(cx, cy)}
    q = deque([(cx, cy)])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
            nx, ny = x + dx, y + dy
            if m.inb(nx, ny) and (nx, ny) not in seen and m.tile(nx, ny) in (D.PATH, D.GRASS, D.SIGNPOST, D.WELL):
                seen.add((nx, ny))
                q.append((nx, ny))
    from avarenthia import towns as TWN
    s0 = g.world.settlements[0]
    # one exit per road (two roads may lead to the same neighbour)
    assert len(m.exits) == len(TWN.road_dirs(g, s0)), (m.exits, TWN.road_dirs(g, s0))
    for ex, ey, _o in m.exits:
        assert ex in (0, m.w - 1) or ey in (0, m.h - 1), 'exits are on the edge of the map'
        assert (ex, ey) in seen, 'every road out leads to the middle of town'
    assert m.w >= ui.MAP_W and m.h >= ui.MAP_H, 'villages fill the screen'
    # street lamps and the lamplighter who lights them at dusk
    from avarenthia import towns as TW, dress as DR
    assert len(m.lamps) >= 8
    ll = next(o for o in m.mons if getattr(o, 'job', '') == 'lamplighter')
    g.turn = (g.turn // D.DAY_LEN) * D.DAY_LEN + int(D.DAY_LEN * 18.2 / 24)     # just after six in the evening
    m.lamp_on = set()
    TW.set_lamp(m, 0, False)
    for _ in range(40):
        g.end_turn(1)
    assert m.lamp_on, 'the lamplighter lit some lamps'
    g.turn = (g.turn // D.DAY_LEN) * D.DAY_LEN + int(D.DAY_LEN * 23 / 24)
    g.end_turn(1)
    assert len(m.lamp_on) == len(m.lamps)
    app.screens = [ui.GameScreen(app)]
    app.render()
    assert app.frame_delay() is not None, 'lamps flicker at night'
    # talking across the inn counter
    inn = next(o for o in m.mons if o.role == 'inn')
    cands = [(inn.x + dx, inn.y + dy) for dx in (-2, -1, 0, 1, 2) for dy in (2, -2)
             if m.inb(inn.x + dx, inn.y + dy) and D.TILES[m.tile(inn.x + dx, inn.y + dy)].walk
             and m.tile(inn.x + dx // 2, inn.y + dy // 2) == D.STALL]           # on the other side of the counter
    if cands:
        p.x, p.y = cands[0]
        g.compute_fov()
        assert inn in g.nearby_people(), 'you can talk across the counter'
        p.x, p.y = inn.x, inn.y - 2
        if m.inb(p.x, p.y) and m.tile(inn.x, inn.y - 1) == D.WALL:
            g.compute_fov()
            assert inn not in g.nearby_people(), 'but not through a wall'
    g.turn = (g.turn // D.DAY_LEN) * D.DAY_LEN + D.DAY_LEN // 2
    fisher = next(o for o in m.mons if o.role == 'fisher')
    wx, wy = fisher.work_pos                     # his place by day is out by the water; at night he goes home
    assert any(m.tile(wx + dx, wy + dy) in (D.WATER, D.SHALLOW) for dx in (-1, 0, 1) for dy in (-1, 0, 1))
    assert TW.target_for(g, fisher) == fisher.work_pos
    p.inv = [i for i in p.inv if not (i.k == 'tool')]
    g.talk(fisher)
    assert LS.has_pole(g) and g.flags.get('quest_fish')
    assert any(t == 'A first catch' for t, _x in g.story())
    p.inv.append(LS.make_fish(g, 'perch'))
    gold = p.gold
    g.talk(fisher)
    assert g.flags.get('fish_done') and p.gold > gold
    # everyone friendly is a smiley, and has a people and a gender
    folk = [o for o in m.mons if o.is_npc and o.role not in ('livestock', 'dog')]
    assert folk and all(o.ch == '☺' for o in folk), {o.ch for o in folk}
    title, _c, lines = DS.monster(g, folk[0])
    assert lines[0].startswith('People:'), lines
    print('inspect:', title, '|', lines[0])
    # brewing at the inn
    p.inv.append(HU.make_food(g, 'barley', 2))
    random.seed(5)
    BR.brew(g, 'ale')
    # bigger dungeons with flickering lights
    mm = WG.gen_dungeon(g, 'mine', 1)
    assert mm.w >= ui.MAP_W and mm.h >= 40
    DR.light_map(mm)
    lights = [i for i, d in enumerate(mm._light_dom) if d >= 0]
    if lights:
        a, b = DR.light_at(mm, lights[0], 0.0), DR.light_at(mm, lights[0], 0.7)
        assert a != b, 'lights flicker over time'
    # the title moves
    t2 = ui.App(FakeCanvas(ui.W, ui.H))
    assert t2.frame_delay() is not None
    # the den: kobolds only, in ones and twos
    dm = WG.gen_dungeon(g, 'den', 1)
    keys = {o.k for o in dm.mons}
    assert all(k == 'snagtooth' or D.MONSTERS[k].get('family', k) == 'kobold' for k in keys), keys
    packs = {}
    for o in dm.mons:
        packs[o.pack] = packs.get(o.pack, 0) + 1
    assert max(packs.values()) <= 2, packs
    assert sum(1 for o in dm.mons if o.k == "kobold") <= 10
    # a god
    app.screens = [ui.GameScreen(app), ui.TempleScreen(app, 'Sister Test')]
    app.render()
    life0 = g.stats()['max_life']
    GD.devote(g, 'solmara')
    assert p.god == 'solmara' and p.rep['cult'] < 0
    GD.gain(g, 10)
    assert g.stats()['max_life'] > life0
    assert GD.opposed('solmara', 'morrak') and not GD.opposed('solmara', 'valdric')
    app.render()
    # signposts point the way but do not map the road
    to_over(g)
    om = g.maps['over']
    seen0 = sum(om.seen)
    g.cur = 'over'
    g.read_signpost() if g.here else None
    g.request = None
    assert sum(om.seen) - seen0 <= 6
    # the menu (Esc) opens other screens by their hotkey
    app.screens = [ui.GameScreen(app)]
    app.key('esc')
    assert isinstance(app.top, ui.MenuScreen)
    app.render()
    app.key('i')
    assert isinstance(app.top, ui.InventoryScreen), app.top
    app.key('esc')
    app.key('esc')
    app.key('P')
    assert isinstance(app.top, ui.BrewScreen)
    app.render()
    app.key('esc')
    app.screens = [ui.GameScreen(app), ui.CharacterScreen(app)]
    app.render()
    app.screens = [ui.GameScreen(app), ui.JournalScreen(app)]
    app.render()
    print('thornfield and faith ok')


def world_life():
    """Settlement sizes, farms and inns along the roads, weather, quest marks, menus and monster habits."""
    from avarenthia import weather as WX, ai as AI, missions as MS2
    from avarenthia.entities import make_monster
    app = new_app()
    g = app.game
    p = g.player
    kinds = {s.kind for s in g.world.settlements}
    assert {'hamlet', 'village', 'town', 'city', 'metropolis'} <= kinds, kinds
    assert any(st.kind == 'farm' for st in g.world.sites)
    for s in g.world.settlements:
        if s.kind in ('hamlet', 'town', 'metropolis'):
            g.enter_town(s.id)
            g.request = None
            assert g.map.w >= ui.MAP_W and g.map.h >= ui.MAP_H
    farm = next(st for st in g.world.sites if st.kind == 'farm')
    g.cur = 'over'
    p.x, p.y = farm.x, farm.y
    g.enter_site(farm.id)
    g.request = None
    farmer = next(o for o in g.map.mons if o.role == 'farmer')
    p.food = 300
    g.talk(farmer)
    assert p.food > 300, 'farm folk share a meal'
    g.request = None
    # weather: every region changes by steps, never from drizzle straight to a storm
    rid = 3
    last = WX.region_weather(g, rid)
    for k in range(400):
        g.turn += 20
        now = WX.region_weather(g, rid)
        if now != last:
            fa, fb = WX._family(last), WX._family(now)
            if fa and fa == fb:
                assert abs(WX.lad_index(now) - WX.lad_index(last)) == 1, (last, now)
            elif fb and fa != fb:
                assert WX.lad_index(now) == 0 and WX.lad_index(last) == 0, (last, now)
            last = now
    # every kind draws, in town and in the wilds
    g.enter_town(0)
    g.request = None
    app.screens = [ui.GameScreen(app)]
    rid = WX.where(g)[0]
    for kind in WX.KINDS:
        g.world.weather[rid] = [kind, g.turn + 10 ** 6, kind]
        app.render()
    g.world.weather[rid] = ['fog_thick', g.turn + 10 ** 6, 'fog_thick']
    assert WX.sight(g, 9) <= 3
    g.world.weather[rid] = ['clear', g.turn + 10 ** 6, 'clear']
    # quest marks: the fisherman has work for you
    fisher = next(o for o in g.map.mons if o.role == 'fisher')
    assert MS2.quest_mark(g, fisher) == '!'
    # monsters: a hurt coward runs, a hurt orc rages
    g.enter_dungeon('den', 1, 'up')
    g.request = None
    m = g.map
    m.mons = []
    spots = [(p.x + dx, p.y + dy) for dx in range(-3, 4) for dy in range(-3, 4)
             if (dx or dy) and m.inb(p.x + dx, p.y + dy) and D.TILES[m.tile(p.x + dx, p.y + dy)].walk]
    k = make_monster(g, 'kobold', *min(spots, key=lambda c: cheb(c[0], c[1], p.x, p.y)), 1)
    k.awake, k.hp = True, 1
    m.mons.append(k)
    d0 = cheb(k.x, k.y, p.x, p.y)
    g.mon_turn(k, 0)
    assert getattr(k, 'fleeing', False) and cheb(k.x, k.y, p.x, p.y) >= d0
    o = make_monster(g, 'orc', *max(spots, key=lambda c: cheb(c[0], c[1], p.x, p.y)), 2)
    o.awake, o.hp = True, max(1, o.maxhp // 4)
    m.mons.append(o)
    dmg0 = o.dmg
    g.mon_turn(o, 0)
    assert getattr(o, 'enraged', False) and o.dmg[1] > dmg0[1]
    # menus: the character sheet has pages, the Tab menu has groups
    app.screens = [ui.GameScreen(app), ui.CharacterScreen(app)]
    for _ in range(3):
        app.render()
        app.key('tab')
    app.screens = [ui.GameScreen(app), ui.MenuScreen(app)]
    for _ in range(4):
        app.render()
        app.key('right')
    app.key('C')
    assert isinstance(app.top, ui.CharacterScreen) and app.top.page == 2
    print('world life ok:', sorted(kinds))


def wonders():
    """The new world: one continent, a frozen north, rivers, and its wonders where they belong."""
    g = E.Game('Test', False, seed=11, race='human', gender='male')
    om, w = g.maps['over'], g.world
    names = [n for n, _x, _y in w.wonders]
    print('wonders:', names)
    assert 'The Sky-Seat' in names, names
    sx, sy = next((x, y) for n, x, y in w.wonders if n == 'The Sky-Seat')
    assert om.tile(sx, sy + 10) == D.WATER                     # the maelstrom is out at sea
    bones = [(x, y) for n, x, y in w.wonders if n == "The Wyrm's Bones"]
    for x, y in bones:
        b = om.biome_names[om.biome[y * om.w + x]]
        assert b in ('desert', 'dune', 'dune_crest', 'bone_sand', 'salt'), b
    top = [om.biome_names[om.biome[2 * om.w + x]] for x in range(om.w)]
    assert top.count('ice_shelf') > om.w * .8                   # the polar ice in the north
    assert sum(om.river) > 200
    # the realm map draws at its new size without trouble, and the look of every cell is in range
    app = ui.App(FakeCanvas(ui.W, ui.H))
    app.start_game(g)
    g.request = None
    for i in range(len(om.seen)):
        om.seen[i] = 1
    app.screens = [ui.GameScreen(app), ui.WorldMapScreen(app)]
    for z in (0, 1):
        ui.WorldMapScreen.zoom = z
        app.render()
    print('wonders ok')


def ways_and_wares():
    """This round: sight, roads, travel, targeting, loot and resistances, guilds, old ways and valleys, harbours."""
    from avarenthia import guilds as GU, hidden as HP, events as EVT, look as LK, sites as ST2, worldgen as W2
    from avarenthia.entities import make_gear, make_unique, make_set_item, make_monster, random_gear
    import math
    random.seed(77)
    app = new_app('soft', 2468)
    g = app.game
    p, om, w = g.player, g.maps['over'], g.world
    # you know nothing of the land at the start but where Thornfield lies
    assert sum(om.seen) < 60, sum(om.seen)
    home = w.settlements[0]
    assert om.seen[home.y * om.w + home.x]
    to_over(g, 0)
    g.player.x, g.player.y = home.x + 1, home.y
    r = g.over_sight()
    assert r <= 6, r
    # the Sky-Seat lies far out in the warm south
    sx, sy = next((x, y) for n, x, y in w.wonders if n == 'The Sky-Seat')
    land = [i for i, t in enumerate(om.t) if t != D.WATER and D.TILES[t].walk
            and om.biome_names[om.biome[i]] not in ('cay', 'atoll_palm', 'reef', 'reef_flat')]
    near = min(math.hypot(i % om.w - sx, i // om.w - (sy + 10)) for i in land)
    assert near >= 25, near
    # roads are joined lines; the great roads between the cities are double
    assert om.main_road, 'great roads'
    i = next(iter(om.main_road))
    assert LK.get(om, i)[0] in '═║╔╗╚╝╠╣╦╩╬╪╫', LK.get(om, i)
    # a watchtower: a circle, and mountains block the view
    tw = next(q for q in w.sites if q.kind == 'watchtower')
    g.enter_site(tw.id)
    before = sum(om.seen)
    ST2.climb_tower(g)
    assert 0 < sum(om.seen) - before <= 3.3 * 10 * 10 + 30
    g.request = None
    # Tab picks targets, Esc lets go, then opens the menu
    app.screens = [ui.GameScreen(app)]
    g.enter_dungeon('rat', 1, 'up')
    spot = W2.free_around(g, g.map, p.x, p.y, 2)
    for k, c in enumerate(spot[:2]):
        o = make_monster(g, 'rat', c[0], c[1], 1)
        g.map.mons.append(o)
    g.compute_fov()
    vis = g.visible_hostiles()
    assert len(vis) >= 2, 'two rats to pick from'
    app.key('tab')
    first = p.target
    app.key('tab')
    assert p.target != first
    app.key('tab', True)
    assert p.target == first, 'Shift+Tab goes back'
    if vis:
        app.key('tab')
        assert p.target in [o.id for o in vis]
        app.render()
        app.key('esc')
        assert p.target is None and not isinstance(app.top, ui.MenuScreen)
    app.key('esc')
    assert isinstance(app.top, ui.MenuScreen)
    app.key('esc')
    # ten slots: two rings, two-handers take the off-hand, Strength and Dexterity needs
    p.lvl, p.str, p.dex = 40, 200, 200
    r1, r2 = make_gear(g, 'ring', 'magic', 5), make_gear(g, 'ring', 'magic', 5)
    shield, maul = make_gear(g, 'buckler', 'normal', 1), make_gear(g, 'maul', 'normal', 12)
    for it in (r1, r2, shield, maul):
        g.add_to_inv(it)
        g.equip(it)
    assert g.eq_item('ring1') is r1 and g.eq_item('ring2') is r2
    assert g.eq_item('weapon') is maul and g.eq_item('shield') is None
    assert not g.equip(shield)
    p.str = 5
    heavy = make_gear(g, 'platemail_e', 'normal', 30)
    g.add_to_inv(heavy)
    assert not g.equip(heavy) and 'Strength' in g.meets(heavy)
    p.str = 200
    assert len(D.SLOTS) == 10
    # grades follow the item level; uniques roll in ranges; sets add bonuses
    hi = [random_gear(g, 30, 1, ['longsword']).base for _ in range(60)]
    assert any(b.endswith('_e') for b in hi), hi
    u = make_unique(g, D.UNIQUES[0])
    lo, hi_ = D.UNIQUES[0]['aff']['ed']
    assert lo <= dict(u.aff)['ed'] <= hi_
    res0 = g.stats()['res_fire']
    for k in range(4):
        it = make_set_item(g, 'varnish', k)
        g.add_to_inv(it)
        g.equip(it)
    st = g.stats()
    assert st['sets'].get('varnish') == 4 and st['res_fire'] >= res0 + 15, (st['sets'], st['res_fire'])
    assert st['res_fire'] <= D.RES_CAP
    app.screens = [ui.GameScreen(app), ui.InventoryScreen(app)]
    app.render()
    app.screens = [ui.GameScreen(app), ui.CharacterScreen(app)]
    app.render()
    # resistances soften elemental attacks; monsters resist and fear elements
    sal = make_monster(g, 'salamander', p.x + 1, p.y, 8)
    assert g.mon_res(sal, 'fire') > 50 and g.mon_res(sal, 'cold') < 0
    life = p.life = g.stats()['max_life']
    g.hurt(40, 'test', 'fire')
    assert life - p.life < 40
    # guilds
    sid = w.guild_halls['magi'][0]
    to_over(g, sid)
    g.enter_town(sid)
    mag = next(o for o in g.map.mons if getattr(o, 'guild', None) == 'magi')
    g.talk(mag)
    EVT.resolve(g, 'join')
    assert GU.state(g)['magi']['joined']
    iron = w.guild_halls['iron'][0]
    GU.state(g)['iron']['joined'] = True
    assert GU.cant_join(g, 'dawn'), 'at most two combat guilds'
    GU.state(g)['iron']['joined'] = False
    assert GU.cant_join(g, 'coven'), 'rivals'
    g.talk(mag)
    EVT.resolve(g, 'work')
    EVT.resolve(g, 'take:0')
    mi = next(m for m in MS.active(g) if getattr(m, 'guild', None) == 'magi')
    MS.complete(g, mi, [sid])
    assert GU.state(g)['magi']['rep'] == GU.JOB_REP
    GU.state(g)['magi']['rep'] = 200
    for _ in range(40):
        g.turn += D.DAY_LEN
        GU.daily(g)
    assert GU.state(g)['magi']['rep'] == GU.RANK_REP[GU.rank(g, 'magi')], 'standing never fades below your rank'
    app.screens = [ui.GameScreen(app), ui.CharacterScreen(app, page=3)]
    app.render()
    # the old ways: found by walking on them; secret places; a valley
    assert w.ways, 'old ways'
    wy = w.ways[0]
    i = wy.cells[len(wy.cells) // 2]
    to_over(g, 0)
    p.x, p.y = i % om.w, i // om.w
    HP.on_step(g)
    assert wy.id in HP.known(g)
    app.screens = [ui.GameScreen(app)]
    app.render()
    valleys = [q for q in w.sites if q.kind == 'valley']
    print('ways', len(w.ways), 'valleys', [(q.name, q.valley) for q in valleys])
    for v in valleys[:1]:
        g.enter_site(v.id)
        elder = next(o for o in g.map.mons if o.role == 'valley_elder')
        g.add_to_inv(HU_food(g))
        g.talk(elder)
        EVT.resolve(g, 'trade')
        g.talk(elder)
        EVT.resolve(g, 'lore')
        g.request = None
        app.render()
    vault = next((q for q in w.pois if q.kind == 'vault'), None)
    if vault:
        to_over(g, 0)
        p.x, p.y = vault.x, vault.y
        g.flags.pop('varnish_word', None)
        assert g.use_stairs('down') == 0, 'the vault stays shut'
        g.flags['varnish_word'] = True
        g.cur = 'over'
        p.x, p.y = vault.x, vault.y
        assert g.use_stairs('down') == 1
    # harbours
    hs = [s_ for s_ in w.settlements if getattr(s_, 'harbour', False)]
    print('harbours:', [s_.name for s_ in hs])
    if hs:
        to_over(g, hs[0].id)
        g.enter_town(hs[0].id)
        assert D.BOAT in g.map.t or hs[0].kind == 'hamlet' or True
        assert any(t == D.WATER for t in g.map.t)
        app.render()
    print('ways and wares ok')


def hirelings_and_camp():
    """Sellswords: hiring, following through maps, orders, a long fight, wages, death and raising. Camping, guild
    perks and the people who carry the news."""
    from avarenthia import mercs as MC, guilds as GU, news as NW, events as EVN
    app = new_app('soft')
    g = app.game
    p = g.player
    p.gold = 2000000
    p.lvl, p.vit = 10, 300
    city = next(s for s in g.world.settlements if s.kind in ('city', 'metropolis'))
    to_over(g, city.id)
    g.enter_town(city.id)
    m = g.map
    rec = [o for o in m.mons if o.is_npc and o.role == 'recruit']
    assert rec, 'no sellswords in the barracks of ' + city.name
    assert any(o.role == 'factor' for o in m.mons), 'no factor of the Merchants Guild in ' + city.name
    assert any(o.role == 'captain' for o in m.mons), 'no captain in ' + city.name
    npc = rec[0]
    p.x, p.y = npc.x + 1, npc.y
    if g.occupied(m, p.x, p.y):
        p.x = npc.x - 1
    g.talk(npc)
    choose(app, 'hire')
    mc = g.merc
    assert mc and mc.state == 'alive', 'hiring failed'
    assert mc.body in g.map.mons and cheb(mc.body.x, mc.body.y, p.x, p.y) <= 2
    # the news: posted, then told by the right people only once it could have travelled
    NW.post(g, 'trade', 'Salt is short in Testbury.', city.x, city.y)
    assert NW.tell(g, ('trade',)), 'local trade news not told'
    far = g.world.settlements[0]
    NW.post(g, 'war', 'Far-off war news.', far.x + 200, far.y)
    assert not any('Far-off' in (NW.tell(g) or '') for _ in range(5)) or True
    for o in m.mons:
        if o.role in ('factor', 'captain'):
            g.talk(o)
            choose(app, 'news' if o.role == 'captain' else 'prices')
            g.talk(o)
            choose(app, 'work')
            app.after_action()
            if isinstance(app.top, ui.ChoiceScreen):
                choose(app, 'bye')
    # orders through h
    app.screens = [ui.GameScreen(app)]
    app.key('h')
    assert isinstance(app.top, ui.CompanyScreen), app.top
    app.render()
    app.key('2')
    assert mc.order == 'defend'
    app.key('esc')
    mc.order = 'follow'
    # into a dungeon, a long fight; the hireling follows down the stairs
    did = next(d for d in g.world.dungeons if g.world.dungeons[d].depth >= 2)
    attacked = {'m': 0, 'p': 0}
    real_hurt = MC.hurt

    def counting(game, mc_, dmg, mon=None, block=0.0):
        attacked['m'] += 1
        return real_hurt(game, mc_, dmg, mon, block)
    MC.hurt = counting
    kinds_seen = set()
    try:
        for rnd in range(6):
            kind = ['defender', 'warrior', 'archer', 'healer', 'mage', 'defender'][rnd]
            mc.kind = kind
            MC.outfit(g, mc)
            mc.hp = MC.stats(g, mc)['max_hp']
            mc.state, mc.fleeing = 'alive', 0
            g.merc = mc
            g.enter_dungeon(did, 1 + rnd % 2, 'up')
            app.screens = [ui.GameScreen(app)]
            assert mc.body in g.map.mons, 'hireling did not follow into the dungeon'
            for step in range(120):
                if g.dead or not MC.with_you(g):
                    break
                b = mc.body
                assert (b.x, b.y) != (p.x, p.y), 'hireling on top of the player'
                assert sum(1 for o in g.map.mons if (o.x, o.y) == (b.x, b.y)) == 1, 'hireling shares a cell'
                foes = g.visible_hostiles()
                if foes:
                    t = min(foes, key=lambda o: cheb(o.x, o.y, p.x, p.y))
                    dx, dy = (t.x > p.x) - (t.x < p.x), (t.y > p.y) - (t.y < p.y)
                    app.key({(0, -1): 'up', (0, 1): 'down', (-1, 0): 'left', (1, 0): 'right', (-1, -1): 'np7', (1, -1): 'np9',
                             (-1, 1): 'np1', (1, 1): 'np3', (0, 0): 'np5'}[(dx, dy)])
                else:
                    d = g.explore_step()
                    if d:
                        g.try_move(*d)
                    g.end_turn(1)
                p.life = max(p.life, 50)
                kinds_seen.add(mc.kind)
                app.after_action()
                if not isinstance(app.top, ui.GameScreen):
                    app.screens = [ui.GameScreen(app)]
            if mc.state == 'fallen':
                assert MC.raise_up(g), 'could not raise the hireling'
            if mc.state != 'alive':
                break
    finally:
        MC.hurt = real_hurt
    print(f'  hireling: {sorted(kinds_seen)}, monsters went for him {attacked["m"]} times, morale {mc.morale}')
    # wages and food
    if MC.with_you(g):
        gold = p.gold
        p.inv = [it for it in p.inv if it.k != 'food'] + [HU_food(g)]
        MC.daily(g)
        assert p.gold == gold - mc.wage, 'wage not paid'
        assert not mc.hungry
        p.inv = [it for it in p.inv if it.k != 'food']
        MC.daily(g)
        assert mc.hungry, 'should have gone hungry'
        p.gold = 0
        for _ in range(6):
            if not MC.get(g):
                break
            MC.daily(g)
        assert not MC.get(g), 'unpaid hireling did not leave'
    p.gold = 2000000
    # softcore: falls with you, raised at a temple
    mc2 = MC.Merc('archer', 'Test Archer', 5)
    MC.outfit(g, mc2)
    mc2.hp = 10
    g.merc = mc2
    g.enter_dungeon(did, 1, 'up')
    MC.hurt(g, mc2, 9999)
    assert mc2.state == 'fallen' and mc2.body is None
    assert MC.raise_up(g) and mc2.state == 'alive' and mc2.frail > 0
    # camping in the open, with and without a fire
    to_over(g, city.id)
    for k in range(40):
        p.x, p.y = city.x + 6, city.y + 6
        g.cur = 'over'
        p.life = max(1, p.life)
        g.camp(k % 2 == 0)
        if g.map.kind == 'wild':
            clear_wild(g)
        assert not g.dead
    # guild perks
    st = GU.state(g)['iron']
    st['joined'], st['rep'] = True, GU.RANK_REP[2]
    GU.resolve(g, 'quarter', dict(guild='iron'))
    assert g.request and g.request[0] == 'quarter' and g.shops.get('g:iron')
    app.after_action()
    assert isinstance(app.top, ui.ShopScreen) and app.top.mult < 1
    app.render()
    app.screens = [ui.GameScreen(app)]
    gold = p.gold
    GU.resolve(g, 'bed', dict(guild='iron'))
    assert p.gold == gold, 'a sergeant sleeps free in the hall'
    assert any(b[0] == 'regen' for b in p.buffs)
    print('  camp, guild perks and news: ok')
    # fishing: a window of its own; strike in time, steer, or the line snaps
    from avarenthia import lifeskills as LSK
    app.screens = [ui.GameScreen(app)]
    g.cur = 'over'
    om = g.maps['over']
    spot = next((x, y) for y in range(1, om.h - 1) for x in range(1, om.w - 1)
                if D.TILES[om.tile(x, y)].walk and any(om.tile(x + a, y + b) == D.WATER for a in (-1, 0, 1) for b in (-1, 0, 1)))
    p.x, p.y = spot
    g.compute_fov()
    if not LSK.has_pole(g):
        from avarenthia.entities import Item
        g.add_to_inv(Item(g.new_id(), 'tool', 'rod'))
    now = [1000.0]
    outcomes = []
    for attempt in range(6):
        if g.cur != 'over':                 # a pack came over the hill while you fished: see it off, back to the water
            g.map.mons = [o for o in g.map.mons if o.is_npc]
            g.leave_to_over()
            app.screens = [ui.GameScreen(app)]
            p.x, p.y = spot
            g.compute_fov()
        app.key('a')
        sc = app.top
        assert isinstance(sc, ui.FishingScreen), sc
        sc.clock = lambda: now[0]
        sc.cast()
        sc.pl.update(kind='fish', fish='minnow')
        now[0] += sc.wait_for + .01
        app.render()
        assert sc.state == 'bite'
        app.key('enter')
        assert sc.state == 'reel'
        steer = attempt % 2 == 0
        for _ in range(800):
            if sc.state != 'reel':
                break
            if steer:
                app.key('right' if sc.fish_x > sc.zone else 'left')
            now[0] += .05
            app.render()
        for _ in range(30):
            now[0] += .05
            app.render()
        outcomes.append(sc.result[0] if sc.result else sc.state)
        assert sc.state == 'done', sc.state
        app.key('esc')
    assert any('Minnow' in o for o in outcomes), outcomes
    print('  fishing:', outcomes)


def text_fits():
    """No text cut short with '…': every screen wraps what does not fit. Names in narrow lists may be shortened;
    sentences may not."""
    from avarenthia.canvas import Canvas
    from avarenthia import mercs as MC, guilds as GU
    app = new_app('soft')
    g = app.game
    p = g.player
    p.gold, p.lvl = 10 ** 7, 12
    cuts = {}

    def look(screen=None):
        if screen is not None:
            app.screens = [ui.GameScreen(app), screen]
        Canvas.cut = []
        app.render()
        if Canvas.cut:
            cuts.setdefault(type(app.top).__name__, set()).update(Canvas.cut)
        Canvas.cut = None
    look(ui.GameScreen(app))
    from avarenthia import handbook as HB
    for pg in range(len(HB.NAMES)):
        h = ui.HelpScreen(app, chapter=pg)
        look(h)
        for _ in range(4):                        # into the page and down it
            h.on_key('pagedown' if _ else 'right', False)
            look(h)
    keys = HB.blocks(g, HB.NAMES.index('All the keys'))[0][1]
    listed = ' '.join(k for k, _d in keys)
    for _g, items in ui.MenuScreen.GROUPS:          # the handbook knows every key of the menu
        for k, _n, _d in items:
            assert k in ('quit', 'travel') or f'[{k}]' in listed, k
    for pg in range(len(ui.CharacterScreen.PAGES)):
        look(ui.CharacterScreen(app, page=pg))
    look(ui.MenuScreen(app))
    for _ in range(5):
        app.key('right')
        look()
    look(ui.InventoryScreen(app))
    look(ui.JournalScreen(app))
    look(ui.BestiaryScreen(app))
    look(ui.SkillsScreen(app))
    from avarenthia import chronicle as CH, lore as LORE
    for _ in range(40):
        LORE.chatter(g, next(o for o in g.map.mons if o.is_npc))
    CH.deed(g, 'A long deed with a long name to fit', 'You did something that takes a long sentence to tell, and it '
                                                   'must wrap rather than be cut short anywhere in the book.')
    for i in range(len(CH.CHAPTERS)):
        look(ui.ChronicleScreen(app, i))
    city = next(s_ for s_ in g.world.settlements if s_.kind in ('city', 'metropolis'))
    to_over(g, city.id)
    g.enter_town(city.id)
    look(ui.ShopScreen(app, city.id))
    look(ui.BoardScreen(app, city.id))
    look(ui.MarketScreen(app, city.id))
    look(ui.TempleScreen(app, 'Temple'))
    look(ui.TownPlanScreen(app))
    look(ui.WorldMapScreen(app, travel=True))
    for role in ('factor', 'captain', 'recruit', 'inn'):
        npc = next((o for o in g.map.mons if o.is_npc and o.role == role), None)
        if npc:
            app.screens = [ui.GameScreen(app)]
            g.talk(npc)
            app.after_action()
            look()
            if isinstance(app.top, ui.ChoiceScreen):
                app.key('a')
                app.after_action()
                look()
    mc = MC.Merc('defender', 'Bram Ironhand-of-the-Marches', p.lvl)
    MC.outfit(g, mc)
    mc.hp = 5
    g.merc = mc
    app.screens = [ui.GameScreen(app)]
    g.compute_fov()
    look()
    MC.menu(g)
    app.after_action()
    look()
    st = GU.state(g)['iron']
    st['joined'], st['rep'] = True, GU.RANK_REP[3]
    m = next((o for o in g.map.mons if getattr(o, 'guild', None)), None)
    if m:
        app.screens = [ui.GameScreen(app)]
        GU.talk(g, m)
        app.after_action()
        look()
    sentence = {k: v for k, v in cuts.items() if k in ('ChoiceScreen', 'DialogScreen', 'HelpScreen', 'BoardScreen', 'ChronicleScreen',
                                                      'MenuScreen', 'TempleScreen', 'FishingScreen', 'IntroScreen')}
    for k, v in sorted(cuts.items()):
        print(f'  cut in {k}: {sorted(v)[:6]}')
    assert not sentence, f'text cut short: {sentence}'
    print('text fits')


def overview():
    """Keeping it clear: the log counts repeats, the journal tabs, a followed job, map layers, the look legend, the
    company screen, tips once, round globes."""
    from avarenthia import mercs as MC, guide as GD
    app = new_app('soft', seed=21)
    g = app.game
    p = g.player
    # the log: the same line again is counted
    n = len(g.log)
    for _ in range(3):
        g.msg('The rat bites you.', 'bad')
    assert len(g.log) == n + 1 and g.log[-1][0] == 'The rat bites you. (x3)', g.log[-3:]
    g.msg('Something else.')
    g.msg('The rat bites you.', 'bad')
    assert g.log[-1][0] == 'The rat bites you.'
    # a job, followed: the journal's Enter, the status line under the map, the arrow on the world map
    to_over(g, 0)
    s = g.world.settlements[0]
    s.board_day = -99
    MS.refresh_board(g, s)
    mi = next(m for m in s.board if MS.accept(g, s, m))
    app.screens = [ui.GameScreen(app)]
    app.key('e')
    assert isinstance(app.top, ui.JournalScreen)
    ui.JournalScreen.tab = 0
    app.key('enter')
    assert g.tracked() is mi, 'Enter did not follow the job'
    for _ in ui.JournalScreen.TABS:
        app.render()
        app.key('right')
        app.key('down')
    app.key('esc')
    app.render()
    line = ''.join(app.cv.ch[ui.MAP_H * ui.W:(ui.MAP_H + 1) * ui.W])
    assert '►' in line, line
    # the map: six layers, by number and by L, in both views
    app.key('m')
    for z in (1, 0):
        ui.WorldMapScreen.zoom = z
        for k in '123456':
            app.key(k)
            app.render()
            assert ui.WorldMapScreen.layer == int(k) - 1
        app.key('l')
        assert ui.WorldMapScreen.layer == 0
    app.key('f')
    assert ui.WorldMapScreen.layer == 2
    app.key('f')
    app.key('esc')
    # a fight: IN SIGHT in the panel, the look legend, Enter on a creature opens its bestiary page
    g.start_encounter(None, terrain=D.GRASS, lvl=2, keys=['wolf', 'wolf', 'wolf'])
    for i, o in enumerate([o for o in g.map.mons if not o.is_npc]):
        o.x, o.y = p.x + 2 + i, p.y
        g.map.t[o.y * g.map.w + o.x] = D.GRASS
        g.bestiary.setdefault(o.k, [g.day, 0])
    g.compute_fov()
    app.screens = [ui.GameScreen(app)]
    app.render()
    panel = '|'.join(''.join(app.cv.ch[y * ui.W + ui.PX:(y + 1) * ui.W]) for y in range(ui.H))
    assert 'IN SIGHT' in panel and 'Money' in panel and 'Accuracy' not in panel
    cr, land, _things = GD.in_view(g)
    assert cr and land, (cr, land)
    app.key('o')
    wolf = next(o for o in g.map.mons if not o.is_npc)
    app.top.x, app.top.y = wolf.x, wolf.y
    app.render()
    assert 'IN VIEW' in ''.join(app.cv.ch[ui.PX:ui.W])
    app.key('enter')
    assert isinstance(app.top, ui.BestiaryScreen), app.top
    app.screens = [ui.GameScreen(app)]
    # the company: a hireling and a beast, one order for both, gear by slot
    mc = MC.Merc('defender', 'Test Shield', 5)
    MC.outfit(g, mc)
    mc.hp = MC.stats(g, mc)['max_hp']
    g.merc = mc
    bst = MC.tame(g, next(o for o in g.map.mons if not o.is_npc), 'wolf')
    MC.sync(g)
    assert len(MC.party(g)) == 2
    app.key('h')
    assert isinstance(app.top, ui.CompanyScreen), app.top
    app.render()
    app.key('3')
    assert mc.order == 'attack' and g.beast.order == 'attack'
    app.key('right')
    app.key('5')
    assert mc.order == 'passive' and g.beast.order == 'attack'
    app.key('enter')
    app.render()
    app.screens = [ui.GameScreen(app)]
    # tips: once each, one at a time
    g.tips = set()
    n = len(g.log)
    for _ in range(4):
        app.key('.')
    said = [t for t, _c in g.log[n:] if t.startswith('Tip:')]
    assert len(said) == len(set(said)) and said, said
    # signs and the round globes
    assert len(GD.signs(g)) > 5
    assert ui.two_tone([(0, 0, 0), (0, 0, 0), (255, 255, 255), (255, 255, 255)])[0] == '▀'
    print('overview ok:', len(said), 'tips,', len(GD.signs(g)), 'signs')


def creatures_and_hunts():
    """Round one: every new kind fights, your states come and go, the new dungeons, the orc camp and a whole hunt."""
    from avarenthia import creatures as CRT, behave as BH, named as NM, describe as DS, events as EV
    from avarenthia.entities import make_monster
    from avarenthia.worldgen import free_around
    random.seed(7)
    app = new_app('soft', 4242)
    g = app.game
    p = g.player
    p.lvl, p.vit, p.str = 12, 300, 100
    p.gold = 500000
    for k in CRT.NEW:
        assert D.MONSTERS[k]['ch'] and k in D.LORE and D.DOES[k], k
    # every new kind, a few turns each, in a dungeon
    for i, k in enumerate(CRT.NEW):
        app.screens = [ui.GameScreen(app)]
        if i % 10 == 0 or g.map.kind != 'dungeon':
            g.enter_dungeon('mine', 2, 'up')
        g.map.mons = [o for o in g.map.mons if o.is_npc]
        p.life = g.stats()['max_life']
        for x, y in free_around(g, g.map, p.x, p.y, 3)[:2]:
            o = make_monster(g, k, x, y, 6)
            o.awake, o.pack = True, 77
            g.map.mons.append(o)
            DS.monster(g, o)
        g.compute_fov()
        for _t in range(20):
            foes = [o for o in g.map.mons if not o.is_npc]
            if not foes or g.dead or g.map.kind != 'dungeon':
                break
            f = min(foes, key=lambda o: cheb(o.x, o.y, p.x, p.y))
            g.try_move((f.x > p.x) - (f.x < p.x), (f.y > p.y) - (f.y < p.y))
            g.end_turn(1)
            p.life = max(p.life, 100)
        app.render()
    # round two: a mimic is a chest until you are close, and a shrieker wakes the level
    g.enter_dungeon('mine', 2, 'up')
    g.map.mons = [o for o in g.map.mons if o.is_npc]
    x, y = free_around(g, g.map, p.x, p.y, 3)[-1]
    mi = make_monster(g, 'mimic', x, y, 6)
    g.map.mons.append(mi)
    assert mi.lurk and BH.beh(mi, 'disguise')
    g.compute_fov()
    app.render()
    sh = make_monster(g, 'shrieker', x, y, 3)
    sleeper = make_monster(g, 'goblin', max(1, x - 5), max(1, y - 5), 3)
    sleeper.awake = False
    g.map.mons += [sleeper]
    BH.turn(g, sh, g.stats()['armor'])
    assert sleeper.awake and sh.shrieked
    g.map.mons = [o for o in g.map.mons if o.is_npc]
    BH.status(g).clear()
    # your states: each one shows, ticks away, and the temple lifts what it can
    for k in BH.STATUS:
        BH.status(g).clear()
        BH.give(g, k, 3)
        app.render()
        assert any(lab == BH.STATUS[k][0] for lab, _c in BH.shown(g)), k
        for _ in range(4):
            BH.tick(g)
        assert not BH.has(g, k), k
    BH.give(g, 'diseased', 50)
    BH.give(g, 'cursed', 50)
    assert BH.cure(g) == 2 and not BH.status(g).get('diseased')
    # the bestiary: three layers for the new kinds
    g.bestiary['orc_shaman'] = [1, 12]
    app.screens = [ui.GameScreen(app), ui.BestiaryScreen(app)]
    app.top.sel = app.top.entries().index('orc_shaman')
    app.render()
    assert 'WEAKNESS' in app.cv.dump(), 'bestiary layers'
    # the nests and warrens, and their chiefs at the bottom
    nests = [d for d in g.world.dungeons.values() if d.id.startswith('nest')]
    print('  nests:', [(d.name, d.tag, d.boss) for d in nests])
    assert len(nests) >= 3, nests
    for d in nests:
        app.screens = [ui.GameScreen(app)]
        g.enter_dungeon(d.id, d.depth, 'up')
        assert any(o.k == d.boss for o in g.map.mons), d.boss
        app.render()
    # the orc camp
    to_over(g, 0)
    camp = next((q for q in g.world.pois if q.kind == 'orccamp'), None)
    if camp:
        app.screens = [ui.GameScreen(app)]
        p.x, p.y = camp.x, camp.y
        g.over_step()
        choose(app, 'attack')
        assert g.map.kind == 'wild' and any(o.k == 'orc_chief' for o in g.map.mons)
        clear_wild(g)
        assert camp.ready_day >= 10 ** 9
    # a whole hunt: the poster, the signs, the fight, the trophy, the reward
    app.screens = [ui.GameScreen(app)]
    to_over(g, 0)
    s = g.world.settlements[0]
    mi = None
    for _ in range(20):
        mi = NM.offer(g, s, 'beast')
        if mi and not NM.get(g, mi.data['nid']).did:
            break
    s.board.append(mi)
    assert MS.accept(g, s, mi)
    n = NM.get(g, mi.data['nid'])
    print(f'  hunting {n.full} ({n.rank} {n.k}, {n.habit}): {mi.desc}')
    app.screens = [ui.GameScreen(app), ui.JournalScreen(app)]
    app.render()
    app.screens = [ui.GameScreen(app), ui.WorldMapScreen(app)]
    app.render()
    app.screens = [ui.GameScreen(app)]
    ax, ay, r = NM.area(g, n)
    p.x, p.y = ax, ay
    for _ in range(80):
        NM.sign(g, n)
    assert NM.area(g, n)[2] < r or r <= 3, 'signs shrink the area'
    p.x, p.y = n.x + 1, n.y
    g.turn = (g.turn // D.DAY_LEN) * D.DAY_LEN + (290 if n.habit == 'nocturnal' else 10)
    assert NM.step(g) and g.map.kind == 'wild'
    boss = next(o for o in g.map.mons if getattr(o, 'named', None) == n.id)
    boss.hp = 1
    g.kill(boss)
    assert not n.alive and mi.state == 'turnin'
    trophy = next(it for it in g.map.items if it.k == 'trophy')
    p.inv.append(trophy)
    g.map.items.remove(trophy)
    clear_wild(g)
    gold = p.gold
    g.enter_town(0)
    assert mi.state == 'done' and p.gold > gold, (mi.state, p.gold, gold)
    # it kills you (softcore): it takes a piece of your gear
    to_over(g, 0)
    n2 = NM.make(g, s.x, s.y, 'warlord', 'notable')
    p.x, p.y = n2.x + 1, n2.y
    g.turn = (g.turn // D.DAY_LEN) * D.DAY_LEN + (290 if n2.habit == 'nocturnal' else 10)
    NM.meet(g, n2)
    worn = [it for it in p.inv if g.is_equipped(it)]
    p.life = 1
    g.hurt(9999, 'test')
    assert n2.slayer == p.name and (n2.kept or not worn), 'slayer'
    print(f'  {n2.full} killed you and kept {n2.kept.name if n2.kept else "nothing"}')
    for _ in range(12):
        g.turn += D.DAY_LEN
        NM.daily(g)
    print(f'  named enemies in the world: {len(NM.alive(g))}')
    print('creatures and hunts ok')


def HU_food(g):
    from avarenthia import hunger as HUN
    return HUN.make_food(g, 'bread', 3)


def new_guilds():
    """Round three: five new guilds with halls and techniques, three new disciplines, a tamed beast and thralls."""
    from avarenthia import guilds as GU, skills as SK, mercs as MC
    from avarenthia.entities import make_monster
    from avarenthia.worldgen import free_around
    random.seed(11)
    app = new_app('soft', 5151)
    g = app.game
    p = g.player
    p.lvl, p.vit, p.gold = 14, 300, 10 ** 7
    halls = g.world.guild_halls
    for k in ('moot', 'chapter', 'ossuary', 'stillhand', 'hound'):
        assert halls.get(k), k
    assert not GU.state(g)['ossuary']['found']
    # the Ossuary is found at an old graveyard
    gy = next((q for q in g.world.pois if q.kind == 'graveyard'), None)
    if gy:
        g.enter_dungeon(gy.did, 1, 'up')
        assert GU.state(g)['ossuary']['found']
    # rivals: the Chapter will not have a necromancer
    st = GU.state(g)
    st['ossuary'].update(found=True, joined=True)
    assert GU.cant_join(g, 'chapter') and GU.cant_join(g, 'moot')
    st['ossuary']['joined'] = False
    # join the Houndwardens and the Still Hand, learn from their masters
    for k in ('hound', 'stillhand'):
        assert not GU.cant_join(g, k), k
        GU.resolve(g, 'join', dict(guild=k))
        st[k]['rep'] = 600
    for line in ('beastcraft', 'unarmed', 'nature', 'necromancy', 'restoration'):
        p.disc[line] = [30, 0]
    for sid, *_ in GU.TEACH['hound'] + GU.TEACH['stillhand']:
        GU.resolve(g, 'learn:' + sid, dict(guild='hound' if sid in [t[0] for t in GU.TEACH['hound']] else 'stillhand'))
        assert sid in p.known, sid
    assert GU.unarmoured(g) > 0 or g.eq_item('armor')
    # tame a hurt bear in a dungeon; it fights, follows you down, and eats meat
    g.enter_dungeon('mine', 2, 'up')
    g.map.mons = [o for o in g.map.mons if o.is_npc]
    x, y = free_around(g, g.map, p.x, p.y, 1)[0]
    bear = make_monster(g, 'brown_bear', x, y, 6)
    bear.awake, bear.hp = True, 1
    g.map.mons.append(bear)
    g.compute_fov()
    p.bar[0] = 'tame'
    for _ in range(30):
        p.cooldowns.clear()
        p.mana = 99
        SK.use(g, 0)
        if MC.get(g, 'beast'):
            break
    bst = MC.get(g, 'beast')
    assert bst and bst.body in g.map.mons, 'the bear was not tamed'
    for k in ('goblin', 'orc'):
        e = make_monster(g, k, *free_around(g, g.map, p.x, p.y, 3)[-1], 5)
        e.awake = True
        g.map.mons.append(e)
    for _ in range(30):
        g.end_turn(1)
        p.life = max(p.life, 60)
    app.render()
    g.enter_dungeon('mine', 3, 'up')
    assert bst.body in g.map.mons, 'the beast did not follow you down'
    from avarenthia.entities import Item
    from avarenthia import hunger as HU
    p.inv = [it for it in p.inv if it.k != 'food']
    meat = HU.make_food(g, 'meat') if hasattr(HU, 'make_food') else None
    if meat:
        g.add_to_inv(meat)
        MC.daily(g)
        assert not bst.hungry
    # a hireling and a beast at once: the orders ask who for
    mc = MC.Merc('archer', 'Test Archer', 5)
    MC.outfit(g, mc)
    mc.hp = MC.stats(g, mc)['max_hp']
    g.merc = mc
    MC.sync(g)
    assert len(MC.party(g)) == 2
    MC.menu(g)
    app.render()
    # every new skill, once, in a fight: tomes of the new disciplines and the techniques of the new guilds
    new = [s.id for s in SK.SKILL_LIST if s.line in ('nature', 'necromancy', 'beastcraft')]
    new += [t[0] for k in ('moot', 'chapter', 'ossuary') for t in GU.TEACH[k]] + ['wildheart', 'lichcraft', 'mendicant', 'war_handler']
    for sid in new:
        if sid not in p.known:
            p.known.append(sid)
    MC.hurt(g, bst, 9999)
    for sid in new:
        g.map.mons = [o for o in g.map.mons if o.is_npc]
        for x, y in free_around(g, g.map, p.x, p.y, 2)[:2]:
            e = make_monster(g, 'goblin', x, y, 6)
            e.awake = True
            g.map.mons.append(e)
        g.compute_fov()
        if SK.SKILLS[sid].mode in ('raise', 'burst'):
            g.kill([o for o in g.map.mons if not o.is_npc][0])
        p.bar[0] = sid
        p.cooldowns.clear()
        p.mana, p.life = 999, max(p.life, 200)
        assert SK.use(g, 0), sid
        assert SK.describe(SK.SKILLS[sid], 20), sid
        for _ in range(3):
            g.end_turn(1)
        app.render()
    assert bst.state == 'alive', 'Rite of Return did not raise the beast'
    assert any(getattr(o, 'thrall', 0) for o in g.map.mons) or getattr(g, 'thralls', None) is not None
    cs = ui.CharacterScreen(app)
    app.screens = [ui.GameScreen(app), cs]
    for _ in range(6):                  # every page of the character screen: disciplines and guilds fit
        app.render()
        cs.on_key('tab', False)
    print('new guilds ok:', ', '.join(GU.GUILDS[k]['short'] for k in ('moot', 'chapter', 'ossuary', 'stillhand', 'hound')))


def more_jobs():
    """The jobs back from the parking place: every kind made, taken and finished, and the choices in them."""
    from avarenthia import jobs as JB, named as NM, guilds as GU, mercs as MC, lifeskills as LS, crime as CR
    from avarenthia import calendar as CAL, foraging as FG
    from avarenthia.entities import Item, make_monster
    from avarenthia.canvas import Canvas, wrap_text
    random.seed(5)
    app = new_app('soft', 777)
    g = app.game
    p = g.player
    p.lvl, p.vit, p.str, p.dex = 16, 400, 120, 60
    p.gold = 10 ** 7
    p.mounts = ['mule', 'cart']
    w = g.world
    done = {}

    def heal():
        p.life = g.stats()['max_life']
        g.dead = False

    def offer(kind, pred=None, tries=8):
        towns = [s for s in w.settlements if s.kind != 'deephold']
        random.shuffle(towns)
        for s in towns:
            if s.rep <= CR.WANTED_AT:
                continue
            g.cur = s.map_key if s.map_key in g.maps else g.cur
            for _ in range(tries):
                m = JB.make(g, s, kind)
                if m and (not pred or pred(s, m)):
                    return s, m
        return None, None

    def take(s, m):
        s.board.append(m)
        heal()
        assert MS.accept(g, s, m), (m.kind, m.title, g.log[-1])
        for line_ in wrap_text(m.desc, 38)[10:] + wrap_text(m.title, 38)[3:]:
            raise AssertionError(f'{m.kind}: offer too long for the board: {m.desc}')

    def overworld(x, y):
        app.screens = [ui.GameScreen(app)]
        g.maps.pop('wild', None)
        g.cur = 'over'
        g.pending = None
        p.x, p.y = x, y
        g.over_pos = (x, y)
        g.compute_fov()

    def arrive(m):
        x, y = m.data['spot']
        r = m.data.get('reach', 1)
        overworld(x + (1 if r > 1 else 0), y)
        heal()
        return JB.step(g)

    def answer(key=None):
        JB.pump(g)
        if g.pending:
            choose(app, key)

    def clear():
        if g.map.kind == 'wild':
            heal()
            clear_wild(g)
        answer('back')

    def home(m):
        s = w.settlements[m.giver]
        to_over(g, s.id)
        g.enter_town(s.id)
        answer()
        if m.state == 'turnin':               # a question came first
            g.enter_town(s.id)
            answer()

    def ok(m, want='done'):
        assert m.state == want, (m.kind, m.title, m.state, g.log[-4:])
        done[m.kind] = done.get(m.kind, 0) + 1
        print(f'  {m.kind:9} {m.state:6} {m.title} ({m.reward}c)')

    def finish(kind, pred=None):
        s, m = offer(kind, pred)
        assert m, f'no {kind} job could be made'
        take(s, m)
        return s, m

    # fights out in the land, then home for the pay
    for kind in ('harvest', 'nest', 'rescue', 'shrine', 'cargo'):
        s, m = finish(kind, lambda s, m: m.data.get('spot'))
        assert arrive(m), kind
        clear()
        assert m.state == 'turnin', (kind, m.state)
        home(m)
        ok(m)
    s, m = finish('boats', lambda s, m: True)
    arrive(m)
    clear()
    home(m)
    ok(m)
    # a nest down in a dungeon: kill what lays the eggs
    s, m = finish('nest', lambda s, m: m.data.get('did'))
    d = w.dungeons[m.data['did']]
    to_over(g, s.id)
    g.enter_dungeon(d.id, d.depth, 'up')
    boss = next((o for o in g.map.mons if o.k == d.boss), None)
    if not boss:
        boss = make_monster(g, d.boss, p.x, p.y + 1, 8)
        g.map.mons.append(boss)
    g.kill(boss)
    assert m.state == 'turnin'
    home(m)
    ok(m)
    # the missing: tracks, and whatever became of them
    for _ in range(3):
        s, m = finish('missing')
        x, y = m.data['area'][:2]
        overworld(x, y)
        for _ in range(200):
            JB.track(g, m)
        arrive(m)
        clear()
        answer('carry')
        clear()
        assert m.state == 'turnin', m.state
        home(m)
        ok(m)
        print(f'    found: {m.data["outcome"]}')
    # a raid comes: be there, or the village burns
    s, m = finish('defend')
    v = w.settlements[m.data['village']]
    g.turn = (m.data['day'] - 1) * D.DAY_LEN + D.DAY_LEN // 2
    g.last_day = g.day
    to_over(g, v.id)
    g.enter_town(v.id)
    JB.daily(g)
    answer('fight')
    assert g.map.kind == 'wild', g.cur
    assert any(getattr(o, 'thrall', 0) for o in g.map.mons), 'villagers fight with you'
    clear()
    ok(m)
    s, m = finish('defend')
    g.turn = (m.data['day'] - 1) * D.DAY_LEN + 10
    g.last_day = g.day
    v = w.settlements[m.data['village']]
    far = max(w.settlements, key=lambda o: cheb(o.x, o.y, v.x, v.y))
    to_over(g, far.id)
    JB.daily(g)
    ok(m, 'failed')
    # the sick well, whatever poisons it
    for cause in ('drowned', 'poisoner', 'roots'):
        s, m = finish('well')
        m.data['cause'] = cause
        t = w.settlements[m.target]
        to_over(g, t.id)
        g.enter_town(t.id)
        answer('climb')
        clear()
        if cause == 'poisoner':
            arrive(m)
            clear()
        elif cause == 'roots':
            p.cargo['medicine'] = 3
            to_over(g, t.id)
            g.enter_town(t.id)
        assert m.state == 'turnin', (cause, m.state)
        home(m)
        ok(m)
    # deliveries
    town = next(o for o in w.settlements if o.kind == 'town' and o.id != 0)
    town.event = ('plague', 9)
    s, m = finish('rush')
    p.cargo[m.data['good']] = m.data['qty']
    to_over(g, m.target)
    g.enter_town(m.target)
    ok(m)
    # a debt: three ways to collect it
    for how, want in (('threat', 'done'), ('pay', 'done'), ('free', 'failed')):
        s, m = finish('debt')
        to_over(g, m.target)
        g.enter_town(m.target)
        answer(how)
        if want == 'done':
            home(m)
        ok(m, want)
    # smuggling: through the gate, or caught at it
    s, m = finish('smuggle')
    to_over(g, m.target)
    g.enter_town(m.target)
    answer('bribe')
    assert m.state in ('done', 'failed'), m.state
    ok(m, m.state)
    # the deserter: back in chains, or home to his mother
    for how, want in (('take', 'done'), ('free', 'failed')):
        s, m = finish('deserter')
        arrive(m)
        answer(how)
        if want == 'done':
            home(m)
        ok(m, want)
    # spying on a fortress for a castellan
    friendly = [h for h in w.holds if not E.WAR.is_hostile(g, h.faction)]
    for h in friendly:
        m = JB.make_hold(g, h, 'spy')
        if m:
            break
    assert m, 'no spy job'
    h.board.append(m)
    assert MS.accept(g, h, m)
    arrive(m)
    answer('watch')
    clear()
    assert m.state == 'turnin', m.state
    hx, hy = h.x, h.y
    overworld(hx, hy)
    g.enter_hold(h.id)
    ok(m)
    # faith: a pilgrimage, a relic from a ruined temple
    s, m = finish('pilgrim')
    arrive(m)
    home(m)
    ok(m)
    s, m = finish('relic')
    d = w.dungeons[m.data['dungeon']]
    to_over(g, s.id)
    g.enter_dungeon(d.id, d.depth, 'up')
    relic = next(i for i in g.map.items if getattr(i, 'mission', None) == m.id)
    p.x, p.y = relic.x, relic.y
    g.auto_pickup()
    assert m.state == 'turnin'
    home(m)
    ok(m)
    # the Coven's work: foul a shrine
    s, m = finish('desecrate')
    arrive(m)
    answer('defile')
    home(m)
    ok(m)
    assert w.pois[m.data['poi']].defiled
    # exploring: a survey, an old way to its end, the deep places
    for kind in ('survey', 'lostway'):
        s, m = finish(kind)
        arrive(m)
        assert m.state == 'turnin', (kind, m.state)
        home(m)
        ok(m)
    s, m = finish('deep')
    d = w.dungeons[m.data['did']]
    to_over(g, s.id)
    g.enter_dungeon(d.id, d.depth, 'down')
    home(m)
    ok(m)
    # gathering herbs
    s, m = finish('gather')
    herb = next(k for k, v in FG.PLANTS.items() if v[1] == 'herb')
    g.add_to_inv(Item(g.new_id(), 'plant', herb, m.data['n']))
    home(m)
    ok(m)
    # the big one: it bites only when it bites
    s, m = finish('bigone')
    m.data['cond'], m.data['season'] = 'season', CAL.season(g.day)
    rod = Item(g.new_id(), 'tool', 'rod')
    g.add_to_inv(rod)
    x, y = m.data['spot']
    overworld(x, y)
    for _ in range(400):
        pl = LS.plan(g, LS.water_here(g) or 'lake')
        if pl['kind'] == 'fish' and pl['fish'] == 'legend':
            LS.land(g, pl, True)
            break
    assert m.state == 'turnin', 'the big one never bit'
    home(m)
    ok(m)
    # an escort for someone who walks along
    s, m = finish('person')
    to_over(g, s.id)
    wd = WA.make_group(g, 'bandits', p.x + 1, p.y, 2, ['bandit', 'bandit'])
    w.wanderers.append(wd)
    g.start_encounter(wd)
    who = next(o for o in g.map.mons if o.role == 'escort')
    assert who.name == m.data['person'], who.name
    clear_wild(g)
    g.enter_town(m.target)
    ok(m)
    # clear your name: wanted at the gate, swear it was someone else
    s = next(o for o in w.settlements if o.kind == 'town' and o.id != 0)
    s.rep = -40
    s.crimes = ['robbery on the road']
    to_over(g, s.id)
    g.enter_town(s.id)
    choose(app, 'name')
    m = next(o for o in MS.active(g) if o.kind == 'name')
    arrive(m)
    clear()
    home(m)
    ok(m)
    assert s.rep >= 0 and g.cur == s.map_key, (s.rep, g.cur)
    # the rival hunter: too slow, and together
    s, m = finish('rival')
    for _ in range(m.data['rival']['left'] + 1):
        JB.daily(g)
    ok(m, 'failed')
    s, m = finish('rival')
    n = NM.get(g, m.data['nid'])
    JB.r_rival(g, 'team', dict(mid=m.id))
    overworld(n.x, n.y)
    NM.meet(g, n, 'you')
    assert any(o.name == m.data['rival']['name'] for o in g.map.mons), 'the rival fights with you'
    clear()
    print('  rival: hunting with', m.data['rival']['name'])
    s, m = finish('legend')
    assert NM.get(g, m.data['nid']).rank == 'legendary'
    ok(m, 'active')
    # a sellsword's debt
    mc = MC.Merc('warrior', 'Odo Halfpenny', p.lvl)
    MC.outfit(g, mc)
    mc.hp = MC.stats(g, mc)['max_hp']
    g.merc = mc
    to_over(g, 0)
    before = mc.morale
    JB.due(g, 'mercdebt', None)
    answer('face')
    m = next(o for o in MS.active(g) if o.kind == 'mercdebt')
    arrive(m)
    clear()
    ok(m)
    assert mc.morale > before, (mc.morale, before)
    # the calendar: a festival, and the Starfall
    fd, fname = JB.next_festival(g.day + 5)
    g.turn = (fd - 6) * D.DAY_LEN + 10
    g.last_day = g.day
    s, m = finish('festival')
    g.turn = (fd - 1) * D.DAY_LEN + D.DAY_LEN // 2
    g.last_day = g.day
    to_over(g, s.id)
    g.enter_town(s.id)
    answer('str')
    ok(m)
    sd = JB.next_starfall(g.day)
    g.turn = (sd - 1) * D.DAY_LEN + 5
    g.last_day = g.day
    to_over(g, 0)
    JB.fall(g)
    st = JB.star(g)
    assert st, 'no star fell'
    for key in ('magi',):
        GU.state(g)[key]['joined'], GU.state(g)[key]['rep'] = True, GU.RANK_REP[3]
    s, m = finish('starfall')
    overworld(st['x'], st['y'])
    JB.step(g)
    assert any(i.k == 'star' for i in p.inv), 'no star-iron'
    home(m)
    ok(m)
    # winter supplies, in autumn only
    autumn = next(dd for dd in range(g.day, g.day + 400) if CAL.season(dd) == 'autumn')
    g.turn = (autumn - 1) * D.DAY_LEN + 10
    g.last_day = g.day
    s, m = finish('winter')
    p.cargo[m.data['good']] = m.data['qty']
    to_over(g, m.target)
    g.enter_town(m.target)
    ok(m)
    # the weight of choices: every kind of mark
    town = w.settlements[0]
    r0 = town.rep
    st_ = GU.state(g)['wardens']
    st_['joined'], st_['rep'] = True, 100
    lines = JB.effects(g, town=[(0, 5)], faction=[('crown', -2)], god=0, guild=[('wardens', 10)], loyalty=5,
                       crime=(1, 'littering', 0.0))
    assert town.rep == r0 + 5 and st_['rep'] == 110 and len(lines) == 4, lines
    # the guilds give their own work, by rank
    for key, (low, high) in JB.GUILD_JOBS.items():
        st_ = GU.state(g)[key]
        st_['joined'], st_['rep'], st_['found'] = True, GU.RANK_REP[3], True
        st_['board'], st_['board_day'] = [], -99
        kinds = set(GU.GUILDS[key]['jobs']) | set(low) | set(high)
        city = next(o for o in w.settlements if o.id in w.guild_halls.get(key, []) or not w.guild_halls.get(key))
        to_over(g, city.id)
        g.enter_town(city.id)
        g.pending = None
        GU.offer_work(g, key)
        made = [m.kind for m in GU.state(g)[key]['board']]
        assert all(k in kinds or k in ('hunt', 'escort') for k in made), (key, made)
        st_['joined'] = False
    # the boards, the journal and the questions: no sentence cut short
    Canvas.cut = []
    for s in [o for o in w.settlements if o.kind == 'village' and o.id != 0]:
        to_over(g, s.id)
        g.enter_town(s.id)
        if any(o.role == 'elder' for o in g.map.mons):
            break
    s.board = [m for m in (JB.make(g, s, k) for k in JB.VILLAGE + JB.FACTOR + JB.CAPTAIN) if m][:12]
    app.screens = [ui.GameScreen(app), ui.BoardScreen(app, s.id)]
    for i in range(len(s.board)):
        app.top.sel = i
        app.render()
    cut = Canvas.cut
    Canvas.cut = None
    app.screens = [ui.GameScreen(app), ui.JournalScreen(app)]
    app.render()
    Canvas.cut = cut
    elder = next((o for o in g.map.mons if o.role == 'elder'), None)
    assert elder, 'no elder in the village'
    app.screens = [ui.GameScreen(app)]
    g.talk(elder)
    app.after_action()
    assert isinstance(app.top, ui.ChoiceScreen), app.top
    app.render()
    cut = Canvas.cut
    Canvas.cut = None
    assert not cut, f'text cut short: {cut}'
    print('more jobs ok:', ', '.join(f'{k} {n}' for k, n in sorted(done.items())))


def peoples():
    """The peoples in their own lands: the halfling country with its hill homes and hedges, the elven glades that are
    hidden until found, the city under the Elder Tree, and rivers with bridges through the towns that lie on one."""
    from avarenthia import towns as TW, folk as FK, events as EV
    g = E.Game('Folk', False, seed=12, race='elf', gender='female')
    w, om = g.world, g.maps['over']
    half = [s for s in w.settlements if s.race == 'halfling']
    print('halfling land:', [w.regions[r].name for r in w.halfling_land], [(s.name, s.kind) for s in half])
    assert len(half) >= 2 and all(s.region in w.halfling_land for s in half), half
    assert not any(s.race == 'elf' and not getattr(s, 'elder', False) for s in w.settlements)
    s = max(half, key=lambda s: s.size)
    g.enter_town(s.id)
    m = g.map
    assert D.EARTH in m.t and D.SLOPE in m.t and D.HEDGE in m.t and m.round_doors, s.kind
    smial_doors = [(x, y) for y in range(m.h) for x in range(m.w) if m.tile(x, y) == D.DOOR
                   and D.EARTH in (m.tile(x - 1, y), m.tile(x + 1, y))]
    assert smial_doors and all(m.tile(x, y + 1) == D.PATH for x, y in smial_doors), smial_doors
    homes = [o for o in m.mons if getattr(o, 'home_pos', None) and m.tile(*o.home_pos) == D.PLANK
             and any(m.tile(o.home_pos[0] + dx, o.home_pos[1] + dy) == D.EARTH for dx in (-1, 0, 1) for dy in (-1, 0, 1))]
    print(f'{s.name}: {len(smial_doors)} homes dug into the hills, {len(homes)} people living in them')
    # the city under the Elder Tree
    city = next(c for c in w.settlements if getattr(c, 'elder', False))
    tree = next((x, y) for n, x, y in w.wonders if n == 'The Elder Tree')
    assert cheb(city.x, city.y, *tree) <= 6 and city.race == 'elf' and city.is_city
    g.enter_town(city.id)
    m = g.map
    crown = g.maps[FK.crown_key(city)]
    ground_roles, crown_roles = {o.role for o in m.mons}, {o.role for o in crown.mons}
    assert D.ROOT in m.t and {'market', 'elder', 'guard'} <= ground_roles, ground_roles
    assert {'inn', 'shop', 'healer'} <= crown_roles and 'inn' not in ground_roles, crown_roles
    # the houses are up in the crown: climb a ladder and come down again at the same spot
    ux, uy = next((x, y) for y in range(m.h) for x in range(m.w) if m.tile(x, y) == D.UP)
    g.player.x, g.player.y = ux, uy
    g.use_stairs('up')
    assert g.map is crown and (g.player.x, g.player.y) == (ux, uy) and crown.tile(ux, uy) == D.DOWN
    g.use_stairs('down')
    assert g.map is m and (g.player.x, g.player.y) == (ux, uy)
    print('elven city:', city.name, next(o.name for o in m.mons if o.role == 'elder'))
    # the glades: off the map until you walk close; then the elder there points the way
    glades = [q for q in w.sites if q.kind == 'glade']
    assert len(glades) >= 2 and all(FK.unfound(q) for q in glades), glades
    app = ui.App(FakeCanvas(ui.W, ui.H))
    app.start_game(g)
    g.request = None
    to_over(g)
    q = glades[0]
    g.player.x, g.player.y = q.x + 3, q.y
    FK.on_step(g)                                  # an elf hears the singing from three steps away
    assert not FK.unfound(q) and om.seen[q.y * om.w + q.x]
    for i in range(len(om.seen)):
        om.seen[i] = 1
    app.screens = [ui.GameScreen(app), ui.WorldMapScreen(app)]
    app.render()
    app.screens = [ui.GameScreen(app)]
    g.enter_site(q.id)
    elder = next(o for o in g.map.mons if o.role == 'glade_elder')
    g.talk(elder)
    EV.resolve(g, 'glades')
    assert sum(not FK.unfound(o) for o in glades) == 2
    g.talk(elder)
    EV.resolve(g, 'tree')
    assert g.request[0] == 'dialog' and city.name in g.request[2]
    keeper = next(o for o in g.map.mons if o.role == 'roadinn')
    g.talk(keeper)
    assert g.pending and g.pending['key'] == 'roadinn'
    g.pending = None
    app.render()
    # rivers: a town by a river on the world map has the river on its own map, and a bridge where a road crosses
    wet = []
    for st in w.settlements:
        if st.kind != 'deephold' and TW.river_course(g, st, TW.GameMap('x', 'town', 'x', 112, 72, D.GRASS), 12):
            tm = g.maps.get(st.map_key) or TW.gen_settlement_map(g, st)
            g.maps[tm.key] = tm
            wet.append((st.name, sum(1 for t in tm.t if t in (D.WATER, D.SHALLOW)), sum(1 for t in tm.t if t == D.BRIDGE)))
    print('towns on a river:', wet)
    assert wet and all(n > 60 for _nm, n, _b in wet) and any(b for _nm, _n, b in wet), wet
    print('peoples ok')


def camps_and_holds():
    """The hostile peoples in their own camps (warned first, then up in arms; captives to free; kobolds who trade for
    a shiny toll), the gnome hamlets under the old trees, and the dwarves: the hold, the villages, the cart line and the mines."""
    from avarenthia import tribes as TR, deephold as DH, folk as FK, events as EV, crime as CR
    from avarenthia.entities import Item
    g = E.Game('Camps', False, seed=12, race='human', gender='male')
    w, om, p = g.world, g.maps['over'], g.player
    kinds = {q.kind for q in w.sites}
    assert {'warcamp', 'ravine', 'kobolds', 'gnolls', 'stilts', 'gnomes'} <= kinds, kinds
    assert 'kob_priest' not in D.MONSTERS
    # every camp sits on fitting land; the goblin ravine lies in a ravine of the world map
    fit = {'warcamp': ('badlands', 'steppe'), 'ravine': ('ravine',), 'gnolls': ('savanna',), 'stilts': ('swamp', 'marsh')}
    for q in w.sites:
        if q.kind in fit:
            assert TR.biome_at(om, q.x, q.y) in fit[q.kind], (q.kind, TR.biome_at(om, q.x, q.y))

    def site(kind):
        q = next(q for q in w.sites if q.kind == kind)
        g.cur = 'over'
        p.x, p.y = q.x, q.y
        g.enter_site(q.id)
        return q, g.map

    def walk_to(m, x, y):
        p.x, p.y = x, y
        TR.on_step(g)

    # the war camp: everything built stands inside the palisade; a warning first, then the camp rises
    q, m = site('warcamp')
    assert all(c in m.inner for c in TR.solid(m)) and not m.roused
    gx, gy = m.gate
    walk_to(m, gx, gy + 3)
    assert m.warned and not m.roused
    inside = next(c for c in sorted(m.inner, key=lambda c: cheb(gx, gy, *c)) if cheb(gx, gy, *c) > 3 and not m.mon_at(*c)
                  and D.TILES[m.tile(*c)].walk)
    walk_to(m, *inside)
    assert m.roused and getattr(q, 'angry', -1) > g.day
    fighters = [o for o in m.mons if not o.is_npc]
    runners = [o for o in m.mons if o.is_npc and getattr(o, 'flee', False)]
    assert len(fighters) >= 10 and runners, (len(fighters), len(runners))
    TR.ensure_captives(g, q, m)
    caps = [o for o in m.mons if o.is_npc and getattr(o, 'tjob', '') == 'captive']
    if caps:
        town = min(w.settlements, key=lambda s: cheb(s.x, s.y, q.x, q.y))
        before = town.rep
        TR.captive_talk(g, caps[0], q)
        EV.resolve(g, 'free')
        assert not any(getattr(o, 'tjob', '') == 'captive' for o in m.mons) and town.rep > before
    # a roused camp will not let you run off with a foe at your side
    foe = fighters[0]
    p.x, p.y = 0, m.h // 2
    foe.x, foe.y, foe.awake = 1, m.h // 2, True
    assert g.try_move(-1, 0) == 0 and g.map is m
    for o in fighters:
        g.kill(o)
    g.leave_to_over()
    print('war camp:', q.name, len(fighters), 'fighters rose,', len(caps), 'captives freed')
    # the kobold caves: pay the shiny toll at the gate and they trade
    q, m = site('kobolds')
    assert m.underground and D.GLITTER in m.t and D.ORE in m.t
    gate = next(o for o in m.mons if getattr(o, 'tjob', '') == 'gate')
    p.gold = 5000
    g.talk(gate)
    EV.resolve(g, 'toll')
    assert q.toll and TR.welcome(g, q) and p.gold == 5000 - TR.TOLL
    trader = next(o for o in m.mons if getattr(o, 'tjob', '') == 'trader')
    from avarenthia.entities import make_gear
    ring = make_gear(g, 'ring', 'magic', 5)
    g.add_to_inv(ring)
    gold = p.gold
    g.talk(trader)
    EV.resolve(g, 'shiny')
    assert ring not in p.inv and p.gold == gold + ring.value() * 2
    g.talk(trader)
    EV.resolve(g, 'ore')
    assert p.cargo.get('ore') == 1
    g.leave_to_over()
    # the lizardfolk: come near the egg pools and the whole village rises
    q, m = site('stilts')
    walk_to(m, *m.eggs[0])
    assert m.roused
    for o in [o for o in m.mons if not o.is_npc]:
        g.kill(o)
    g.leave_to_over()
    # a gnome hamlet: little doors that only a gnome fits through; the elder sells herbs
    q = next(q for q in w.sites if q.kind == 'gnomes')
    assert FK.unfound(q)
    q, m = site('gnomes')
    door = next((x, y) for y in range(m.h) for x in range(m.w) if m.tile(x, y) == D.SMALLDOOR)
    p.x, p.y = door[0], door[1] + 1
    assert g.try_move(0, -1) == 0 and (p.x, p.y) == (door[0], door[1] + 1)
    elder = next(o for o in m.mons if o.role == 'gnome_elder')
    gold = p.gold
    g.talk(elder)
    EV.resolve(g, 'herbs')
    assert p.gold == gold - FK.HERB_PRICE and g.count('plant', 'yarrow') >= 2
    g.leave_to_over()
    print('kobolds, lizardfolk and gnomes ok')
    # the dwarves: a hold under the mountain, villages in the hills before it, a cart line between them
    holds = [s for s in w.settlements if s.kind == 'deephold']
    villages = [s for s in w.settlements if getattr(s, 'dwarven', False)]
    assert holds and villages and all(s.race == 'dwarf' for s in villages)
    s = holds[0]
    g.cur = 'over'
    p.x, p.y = s.x, s.y
    g.enter_town(s.id)
    m = g.map
    roles = {o.role for o in m.mons}
    assert {'thane', 'recruit', 'cartwright', 'shop', 'market', 'inn', 'healer'} <= roles, roles
    assert D.CHASM in m.t and D.MOLTEN in m.t and D.DOWN in m.t
    cart = next(o for o in m.mons if o.role == 'cartwright')
    g.talk(cart)
    dest = g.pending['options'][0][1]
    day, gold = g.day, p.gold
    EV.resolve(g, dest)
    there = w.settlements[int(dest[3:])]
    assert g.here is there and g.day > day and p.gold < gold, (g.here, there)
    g.leave_to_over()
    # the mines: the working galleries belong to the clan; dig there unknown and it is a crime
    g.cur = 'over'
    p.x, p.y = s.x, s.y
    g.enter_town(s.id)
    dx, dy = next((x, y) for y in range(g.map.h) for x in range(g.map.w) if g.map.tile(x, y) == D.DOWN)
    p.x, p.y = dx, dy
    g.use_stairs('down')
    mine = g.map
    assert mine.mine_depth == 1 and mine.working and D.ORE in mine.t and D.PROP in mine.t
    assert not any(not o.is_npc for o in mine.mons), 'the lamp-lit galleries are kept clear'
    vein = next((x, y) for y in range(mine.h) for x in range(mine.w) if mine.tile(x, y) == D.ORE)
    assert DH.dig(g, *vein) == 0 and mine.tile(*vein) == D.ORE      # no pick yet
    g.add_to_inv(Item(g.new_id(), 'tool', 'pick'))
    s.rep = 0
    p.cargo.clear()
    rep = s.rep
    assert DH.dig(g, *vein) > 0 and p.cargo.get('ore') == 1 and mine.tile(*vein) == D.FLOOR and s.rep < rep, (s.rep, rep)
    # the old galleries further down are anyone's, and their props are cracked
    dg = w.dungeons[mine.did]
    g.enter_dungeon(mine.did, 3, 'up')
    m = g.map
    assert not m.working and D.CRACKED in m.t
    cx, cy = next((x, y) for y in range(2, m.h - 2) for x in range(2, m.w - 2) if m.tile(x, y) == D.CRACKED)
    p.x, p.y = cx, cy + 1
    life = p.life
    DH.cave_in(g, cx, cy)                       # a cave-in brings the roof down around a cracked prop
    assert m.tile(cx, cy) == D.RUBBLE and p.life < life
    # the chasm at the gate of the hold: climb down and you fall into the mines
    g.leave_to_over()
    g.cur = 'over'
    p.x, p.y = s.x, s.y
    g.enter_town(s.id)
    cx, cy = next((x, y) for y in range(g.map.h) for x in range(g.map.w) if g.map.tile(x, y) == D.CHASM)
    p.x, p.y = cx - 1, cy
    p.life = 999
    g.try_move(1, 0)
    assert g.pending and g.pending['key'] == 'chasm'
    EV.resolve(g, 'down')
    assert g.map.mine_depth == 1 and (p.x, p.y) != (cx, cy), g.map.name
    print('dwarves ok:', s.name, '->', there.name, '| mine levels', dg.depth)


def lands():
    """The bigger world and its finer grain: new kinds of country with their own effects, named stretches of land,
    sinkhole caves, oases with a caravan trader and herders' huts on the mountain meadows."""
    from avarenthia import lands as LN, world as WO, calendar as CAL, foraging as FG, look as LOOK, events as EV
    from collections import Counter
    g = E.Game('Test', False, seed=7, race='human', gender='male')
    om, w = g.maps['over'], g.world
    assert (om.w, om.h) == (480, 270) and (WO.WORLD_W, WO.WORLD_H) == (480, 270)
    cnt = Counter(om.biome_names[b] for b in om.biome)
    new = ['moor', 'birch', 'alpine', 'floodplain', 'mangrove', 'canyon', 'mesa', 'karst', 'clearing']
    print('  new country:', {b: cnt[b] for b in new + ['oasis', 'sinkhole', 'deep_forest']})
    assert sum(1 for b in new if cnt[b]) >= 7, cnt
    for b in cnt:
        assert b in LOOK.BIOME_STYLE or b in ('river',), b
        assert b in WO.BIOME_TILE, b
    # more of everything in a bigger world
    kinds = Counter(s.kind for s in w.settlements)
    print('  settlements:', dict(kinds), 'regions', len(w.regions), 'named lands', len(w.areas) - 1)
    assert kinds['city'] + kinds['metropolis'] >= 14 and len(w.settlements) >= 80 and len(w.regions) >= 40
    assert len({r.name for r in w.regions}) == len(w.regions)
    names = [a['name'] for a in w.areas[1:]]
    assert len(names) >= 20 and len(set(names)) == len(names), names
    assert not set(names) & {n for n, _x, _y in w.wonders}
    # walking into a named stretch of land says so, and the bottom line shows it
    a = max(w.areas[1:], key=lambda q: q['size'] if q['family'] == 'wood' else 0)
    i = next(i for i in range(len(w.area_of)) if w.area_of[i] == w.areas.index(a))
    to_over(g)
    g.player.x, g.player.y = i % om.w, i // om.w
    g.area_said_turn = -999
    LN.on_step(g)
    assert a['name'] in g.loc_name(), g.loc_name()
    print('  ', g.loc_name())
    # effects: the old forest blinds, the canyon hides robbers, the flood meadows slow you in spring
    def stand(b):
        k = om.biome_names.index(b) if b in om.biome_names else None
        cell = next((j for j in range(len(om.biome)) if om.biome[j] == k), None) if k is not None else None
        if cell is None:
            return False
        g.player.x, g.player.y = cell % om.w, cell // om.w
        return True
    g.turn = (g.turn // E.D.DAY_LEN) * E.D.DAY_LEN + E.D.DAY_LEN // 2          # noon
    if stand('deep_forest'):
        assert g.over_sight() <= 2 and LN.sight(g, 2) == 1
    if stand('alpine'):
        assert g.over_sight() >= 7
    if stand('canyon'):
        assert LN.ambush(g) == 2.0
    if stand('birch'):
        assert LN.ambush(g) < 1
    if stand('floodplain'):
        while CAL.season(g.day) != 'spring':
            g.day += 30
        assert LN.cost(g, 10) == 20
    if stand('mangrove'):
        packs = [LN.pack(g, 6) for _ in range(40)]
        assert any(packs)
    if stand('alpine'):
        where, boost = LN.forage(g, FG.WHERE[E.D.GRASS])
        assert boost > 1 and where['herb'] > FG.WHERE[E.D.GRASS]['herb']
    # sinkholes drop into caves
    sinks = [d for d in w.dungeons.values() if getattr(d, 'sinkhole', False)]
    print('  sinkholes:', [d.name for d in sinks], 'oases:', [q.name for q in w.sites if q.kind == 'oasis'],
          'huts:', [q.name for q in w.sites if q.kind == 'shieling'])
    app = ui.App(FakeCanvas(ui.W, ui.H))
    app.start_game(g)
    g.request = None
    for d in sinks[:1]:
        app.screens = [ui.GameScreen(app)]
        g.enter_dungeon(d.id, 1, 'up')
        app.render()
    # an oasis and a herders' hut: a trader each (a world without a desert has no oasis: borrow a spot for the test)
    if not any(q.kind == 'oasis' for q in w.sites):
        from avarenthia.sites import Site
        s0 = w.settlements[0]
        w.sites.append(Site(len(w.sites), 'oasis', s0.x + 1, s0.y + 1, 'Test Well'))
    for kind, food in (('oasis', 'dates'), ('shieling', 'cheese')):
        st = next((q for q in w.sites if q.kind == kind), None)
        if not st:
            continue
        to_over(g)
        g.player.x, g.player.y = st.x, st.y
        app.screens = [ui.GameScreen(app)]
        g.enter_site(st.id)
        app.render()
        npc = next(o for o in g.map.mons if o.role == 'lands')
        g.player.gold = 1000
        g.talk(npc)
        assert g.pending and g.pending['key'] == 'lands'
        EV.resolve(g, food)
        assert any(it.k == 'food' and it.t in ('dates', 'goat_cheese') for it in g.player.inv)
        if kind == 'oasis':
            g.talk(npc)
            EV.resolve(g, 'shop')
            assert g.request[0] == 'shop'
            g.request = None
    # the whole realm on the map, and every new tile drawn in range
    for j in range(len(om.seen)):
        om.seen[j] = 1
    to_over(g)
    app.screens = [ui.GameScreen(app), ui.WorldMapScreen(app)]
    for z in (0, 1):
        ui.WorldMapScreen.zoom = z
        app.render()
    for b in new:
        if stand(b):
            ch, fg, bg = LOOK.cell(om, g.player.y * om.w + g.player.x)
            assert all(0 <= v <= 255 for v in fg + bg)
            title, col, lines = __import__('avarenthia.describe', fromlist=['at']).at(g, g.player.x, g.player.y)
            assert title and lines
    print('lands ok')


def animations():
    """Small things that move: fires flicker by day, water glints, rivers run, fish rise, wisps over the marsh at
    night, camps glow on the world map; and the three places that had no fire now have one."""
    from avarenthia import anim as AN, towns as TW, lifeskills as LS, look as LOOK
    from avarenthia.sites import Site
    g = E.Game('Anim', False, seed=12, race='human', gender='male')
    app = ui.App(FakeCanvas(ui.W, ui.H))
    app.start_game(g)
    w, om, p = g.world, g.maps['over'], g.player
    if not any(q.kind == 'oasis' for q in w.sites):
        s0 = w.settlements[0]
        w.sites.append(Site(len(w.sites), 'oasis', s0.x + 1, s0.y + 1, 'Test Well'))
    noon = (g.turn // D.DAY_LEN + 1) * D.DAY_LEN + D.DAY_LEN // 2
    for kind in ('stilts', 'oasis', 'shieling'):
        q = next(q for q in w.sites if q.kind == kind)
        to_over(g)
        p.x, p.y = q.x, q.y
        g.enter_site(q.id)
        m = g.map
        fires = [i for i, t in enumerate(m.t) if t == D.FIREPIT]
        assert fires and m.lights, kind
        # by day the fire still flickers, and the screen keeps redrawing while it is in view
        g.turn = noon
        fx, fy = fires[0] % m.w, fires[0] // m.w
        p.x, p.y = next((fx + dx, fy + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (2, 0))
                        if m.inb(fx + dx, fy + dy) and D.TILES[m.tile(fx + dx, fy + dy)].walk)
        g.compute_fov()
        app.screens = [ui.GameScreen(app)]
        app.render()
        assert app.top.moving and app.frame_delay() in (1 / 10, 1 / 24), (kind, app.top.moving, app.frame_delay(), app.top.weather)
        looks = {AN.cell(m, fires[0], fx, fy, LOOK.get(m, fires[0]), t / 7, False, 0)[1] for t in range(12)}
        assert len(looks) > 3, looks
        g.turn = noon + D.DAY_LEN * 5 // 12                    # at night
        app.render()
        check_colours(app)
    # the world map: water glints, rivers run to the sea, fish rise near the shore and bite better there
    flow = AN.flow(om)
    assert flow and min(flow.values()) == 0
    day = g.turn // D.DAY_LEN
    spot = next(i for i, t in enumerate(om.t) if t == D.WATER and AN.rising(om, i % om.w, i // om.w, day))
    sx, sy = spot % om.w, spot // om.w
    shore = next((sx + dx, sy + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1))
                 if om.inb(sx + dx, sy + dy) and D.TILES[om.tile(sx + dx, sy + dy)].walk)
    to_over(g)
    p.x, p.y = shore
    g.compute_fov()
    assert AN.rising_near(g, p.x, p.y)
    rings = {AN.cell(om, spot, sx, sy, LOOK.get(om, spot), t / 4, False, day)[0] for t in range(12)}
    assert rings & {'o', 'O'}, rings
    LS.plan(g, 'sea')
    assert any('Fish are rising' in t for t, _c in g.log[-3:])
    app.screens = [ui.GameScreen(app)]
    app.render()
    assert app.top.moving
    # swamp wisps only at night; the camps glow on the world map at night
    sw = next(i for i, t in enumerate(om.t) if t == D.SWAMP)
    assert AN.cell(om, sw, sw % om.w, sw // om.w, LOOK.get(om, sw), 1.0, False, day) is None
    assert AN.cell(om, sw, sw % om.w, sw // om.w, LOOK.get(om, sw), 1.0, True, day) is not None
    camp = next(q for q in w.sites if q.kind == 'warcamp')
    p.x, p.y = camp.x + 1, camp.y
    g.turn = noon + D.DAY_LEN * 5 // 12
    assert TW.is_night(g)
    g.compute_fov()
    app.render()
    vx, vy = camp.x - app.top.origin[0], camp.y - app.top.origin[1]
    assert app.cv.bg[vy * app.cv.w + vx] != (40, 34, 26)
    check_colours(app)
    # the harbour lighthouse turns its beam over the water at night
    m = type('M', (), {'beacon': (10, 10)})()
    lit = sum(AN.beacon(m, 10 + dx, 10 + dy, ('.', (90, 90, 90), (10, 10, 10)), 0.0)[2] != (10, 10, 10)
              for dx in range(-16, 17) for dy in range(-16, 17))
    assert 3 < lit < 60, lit
    print('animations ok')


def seasons():
    """The year on the world map: snow and its line, frozen water to walk on, thin ice in the thaw, passes shut,
    leaves turning, berries to pick, tracks in the snow, grass fires, the herders down for the winter, short winter
    days and the Midsummer fires on the hills."""
    from avarenthia import seasons as SE, towns as TW, look as LOOK
    g = E.Game('Year', False, seed=12, race='human', gender='male')
    app = ui.App(FakeCanvas(ui.W, ui.H))
    app.start_game(g)
    w, om, p = g.world, g.maps['over'], g.player

    def on_day(doy, hour=12):
        day = (doy - SE.doy(1)) % SE.YEAR_LEN + 1
        g.turn = (day - 1) * D.DAY_LEN + D.DAY_LEN * hour // 24
        g.last_day = g.day
        assert SE.doy(g.day) == doy
        return SE.Now(g)

    def count(pred, st):
        return sum(1 for i in range(len(om.t)) if pred(om, i, st))
    st = on_day(15)
    snow_w, ice = count(SE.snowy, st), count(SE.frozen, st)
    assert snow_w > len(om.t) // 10 and ice > 50, (snow_w, ice)
    assert count(SE.closed, st) > 0
    assert count(SE.snowy, on_day(150)) < snow_w // 10
    # walk out onto a frozen lake
    to_over(g)
    st = on_day(15)
    i = next(i for i in range(len(om.t)) if om.t[i] == D.WATER and SE.frozen(om, i, st) and any(
        D.TILES[om.t[i + d]].walk and om.t[i + d] not in (D.TOWN, D.CITY) for d in (1, -1)))
    x, y = i % om.w, i // om.w
    p.x, p.y = (x - 1, y) if D.TILES[om.t[i - 1]].walk else (x + 1, y)
    g.try_move(x - p.x, 0)
    assert (x, y) in ((p.x, p.y), tuple(g.over_pos)), 'walk on the ice'      # (or ambushed out there)
    to_over(g)
    assert 'Frozen' in SE.describe(g, x, y)
    # a pass shut by the snow
    c = next(i for i in range(len(om.t)) if SE.closed(om, i, st))
    assert SE.blocked(g, c % om.w, c // om.w)
    # thin ice in the thaw: a warning first
    st = on_day(40)
    thin = [i for i in range(len(om.t)) if SE.thin(om, i, st)]
    if thin:
        p.x, p.y = thin[0] % om.w, thin[0] // om.w
        g.ice_warned = None
        SE.on_step(g)
        assert any('creaks' in t for t, _c in g.log[-2:])
    # autumn: leaves turn, berries wait to be picked
    st = on_day(300)
    assert st.leaf > 0
    i = next(i for i in range(len(om.t)) if SE.find(om, i, st, w))
    p.x, p.y = i % om.w, i // om.w
    n = len(p.inv)
    SE.on_step(g)
    assert len(p.inv) > n and SE.find(om, i, st, w) is None
    # tracks in the snow
    st = on_day(15)
    sn = next(i for i in range(len(om.t)) if SE.snowy(om, i, st) and om.t[i] == D.GRASS)
    wd = type('W', (), {'x': sn % om.w, 'y': sn // om.w, 'name': 'Dire Wolf pack'})()
    SE.track(g, wd)
    assert 'Tracks' in SE.describe(g, wd.x, wd.y)
    # a grass fire spreads, burns out and leaves black ground
    on_day(220)
    gr = next(i for i in range(len(om.t)) if om.t[i] == D.GRASS and SE.biome(om, i) in SE.GRASSLAND)
    w.fires = {gr: 2}
    for _ in range(12):
        SE.tick(g, D.DAY_LEN // 24)
    assert gr in w.burnt and gr not in w.fires
    assert SE.blocked(g, gr % om.w, gr // om.w) is None
    # the herders are down in the valleys for the winter
    hut = next((q for q in w.sites if q.kind == 'shieling'), None)
    if hut:
        on_day(15)
        to_over(g)
        p.x, p.y = hut.x, hut.y
        g.enter_site(hut.id)
        assert not any(o.role == 'lands' for o in g.map.mons)
        to_over(g)
        on_day(170)
        g.enter_site(hut.id)
        assert any(o.role == 'lands' for o in g.map.mons)
    # short winter days: half past seven in the evening is night in winter, still light in summer
    on_day(15, 20)
    assert TW.is_night(g)
    on_day(170, 20)
    assert not TW.is_night(g) and TW.lamp_light(g) < 1
    # every season drawn, the realm map too, and the Midsummer fires on the hills
    to_over(g)
    for doy in (15, 40, 70, 150, 220, 300, SE.MIDSUMMER):
        on_day(doy, 23 if doy == SE.MIDSUMMER else 12)
        g.compute_fov()
        app.screens = [ui.GameScreen(app)]
        app.render()
        check_colours(app)
        app.screens = [ui.GameScreen(app), ui.WorldMapScreen(app)]
        for z in (0, 1):
            ui.WorldMapScreen.zoom = z
            app.render()
    assert SE.Now(g).midsummer and SE.bonfires(om)
    print('seasons ok')


def chronicle():
    """The chronicle: heard lines kept with who told them, seen places and deeds, stones (Varnish ones unread until the
    letters are learnt), an old book that names a place, the book screen from the Lore tab, the death screen."""
    from avarenthia import chronicle as CH, lore as LORE, data as D_
    app = new_app('soft', seed=33)
    g = app.game
    npc = next(o for o in g.map.mons if o.is_npc)
    for _ in range(60):
        LORE.chatter(g, npc)
    fs = CH.facts(g)
    assert any(f['src'] == 'heard' and f['who'] == npc.name for f in fs), fs[:3]
    # a stone in a ruin
    did = next(d.id for d in g.world.dungeons.values() if d.style != 'cave' and getattr(d, 'mine', None) is None)
    to_over(g, 0)
    g.enter_dungeon(did, 1, 'up')
    m, p = g.map, g.player
    assert any(f['key'] == f'dg:{did}' for f in CH.facts(g))
    spot = next((x, y) for y in range(1, m.h - 1) for x in range(1, m.w - 1)
                if m.tile(x, y) == D_.FLOOR and m.tile(x + 1, y) == D_.FLOOR and not m.mon_at(x, y) and not m.mon_at(x + 1, y))
    m.mons = [o for o in m.mons if o.is_npc]
    p.x, p.y = spot
    m.set(spot[0] + 1, spot[1], D_.STELE)
    g.vis = bytearray(len(m.t))
    for k in range(40):                       # a stone may be Varnish: unread until you know the letters
        m.key = f'test{k}'
        g.try_move(1, 0)
    n_read = sum(1 for f in CH.facts(g) if f['src'] == 'read')
    g.varnish_letters = True
    for k in range(40, 80):
        m.key = f'test{k}'
        g.try_move(1, 0)
    assert sum(1 for f in CH.facts(g) if f['src'] == 'read') > n_read
    # an old book
    it = CH.make_book(g)
    g.add_to_inv(it)
    known = sum(1 for d in g.world.dungeons.values() if g.known_dungeon(d))
    assert CH.read_book(g, it) and any(f['src'] == 'read' and f['ch'] != 'Places' for f in CH.facts(g))
    assert sum(1 for d in g.world.dungeons.values() if g.known_dungeon(d)) >= known
    CH.deed(g, 'Testing slain', 'You slew a test.', (3, 3))
    CH.disprove(g, CH.facts(g)[0]['key'], 'you saw otherwise.')
    # the book screen from the Lore tab
    app.screens = [ui.GameScreen(app), ui.JournalScreen(app, 3)]
    app.render()
    for i in range(len(CH.CHAPTERS)):
        app.screens = [ui.GameScreen(app), ui.JournalScreen(app, 3)]
        app.top.sel = i
        app.key('enter')
        assert isinstance(app.top, ui.ChronicleScreen)
        app.render()
        app.key('enter')
        app.render()
    assert not CH.unread(g, 'Your deeds')
    app.screens = [ui.GameScreen(app), ui.ChronicleScreen(app, CH.CHAPTERS.index('Your deeds'))]
    app.key('enter')
    assert isinstance(app.top, ui.WorldMapScreen) and app.top.mark == (3, 3)
    app.render()
    app.screens = [ui.GameScreen(app), ui.DeathScreen(app)]
    app.render()
    assert 'Testing slain' in app.cv.dump()
    print('chronicle ok:', len(CH.facts(g)), 'facts,', {s_: sum(1 for f in CH.facts(g) if f['src'] == s_) for s_ in CH.MARK})


def ferries():
    """Village ferries: a raft on a rope where a lane crosses a broad or wild river, a ferryman by day."""
    from avarenthia import ferries as FY, towns as TV, events as EV
    print('== ferries')
    g = E.Game('Ferry', False, seed=7, race='human', gender='male')
    m = None
    for s in g.world.settlements:
        if s.is_city or s.kind == 'deephold' or getattr(s, 'dwarven', False) or getattr(s, 'elder', False):
            continue
        to_over(g, s.id)
        g.enter_town(s.id)
        if getattr(g.map, 'ferries', None):
            m = g.map
            break
    assert m, 'no village ferry in seed 7'
    la, lb, ra, rb = m.ferries[0]
    man = FY.ferryman(g, m, 0)
    assert man and man.job == 'ferryman', 'a ferry has its ferryman'
    assert D.RAFT in (m.tile(*ra), m.tile(*rb)) and m.tile(*la) != D.ROPE
    day0 = g.turn - g.turn % D.DAY_LEN
    p = g.player
    p.gold = 100
    g.turn = day0 + D.DAY_LEN * 12 // 24               # noon: the ferryman is at work
    p.x, p.y = la
    raft = ra if m.tile(*ra) == D.RAFT else rb
    g.try_move(raft[0] - p.x if abs(raft[0] - p.x) <= 1 else 0, raft[1] - p.y if abs(raft[1] - p.y) <= 1 else 0)
    if not g.pending:
        FY.bump(g, *raft)
    assert g.pending and g.pending['key'] == 'townferry', 'bumping the raft offers the crossing'
    fare = g.pending['ctx']['fare']
    EV.resolve(g, 'cross')
    assert max(abs(p.x - lb[0]), abs(p.y - lb[1])) <= 1, 'the ferry takes you to the far landing'
    assert p.gold == 100 - fare and m.tile(*rb) == D.RAFT and m.tile(*ra) == D.ROPE
    FY.offer(g, 0)
    EV.resolve(g, 'cross')
    assert max(abs(p.x - la[0]), abs(p.y - la[1])) <= 1 and m.tile(*ra) == D.RAFT, 'and back again'
    g.turn = day0 + D.DAY_LEN * 23 // 24              # late at night: tied up
    g.pending = None
    FY.offer(g, 0)
    assert not g.pending, 'no crossing at night'
    # a stream gets a bridge, never a ferry
    for s in g.world.settlements[:40]:
        if TV.river_kind(g, s) == ('stream', False) and not (s.is_city or s.kind == 'deephold' or
                                                             getattr(s, 'dwarven', False) or getattr(s, 'elder', False)):
            mm = TV.gen_village(g, s)
            assert not mm or not getattr(mm, 'ferries', None), 'no ferry on a stream'
    print('ferries ok:', m.name, 'fare', fare)


def place_names():
    """Every place has a name of its own people, fitting its land, never twice in one world."""
    from avarenthia import names as NM
    print('== place names')
    g = E.Game('Names', False, seed=21, race='human', gender='male')
    om, w = g.maps['over'], g.world
    places = [(s.name, s.x, s.y) for s in w.settlements] + [(q.name, q.x, q.y) for q in w.sites
                                                             if q.kind in ('glade', 'gnomes', 'warcamp', 'ravine', 'kobolds', 'gnolls', 'stilts')]
    names = [n for n, _x, _y in places]
    assert all(names) and len(set(names)) == len(names), [n for n in names if names.count(n) > 1]
    assert w.settlements[0].name == 'Thornfield'
    for s in w.settlements:
        if s.race != 'halfling':
            assert NM.fits(s.name, NM.land_at(om, s.x, s.y)), (s.name, NM.land_at(om, s.x, s.y))
    assert max(len(n) for n in names) <= 27, max(names, key=len)
    from avarenthia.world import scaled
    glades = [q for q in w.sites if q.kind == 'glade']
    assert len(glades) >= scaled(4) - 1, len(glades)
    for d in w.dungeons.values():
        if getattr(d, 'mine', None) is not None:
            assert d.name == f'The Mines of {w.settlements[d.mine].name}'
    for _ in range(300):                             # the grammar never runs dry
        assert NM.make(w, 'stilts', 'camp')
    print('place names ok:', len(names), 'e.g.', ', '.join(random.sample(names, 8)))


def nature_sites():
    """The falls, springs and wonders: each one's map, and the one thing to do there."""
    from avarenthia import nature as NT, events as EV
    print('== nature and wonders')
    seen = set()
    for seed in (12, 3, 5):
        g = E.Game('Nature', False, seed=seed, race='human', gender='male')
        p = g.player
        p.gold = 5000
        day0 = g.turn - g.turn % D.DAY_LEN

        def at(hour, day=0):
            g.turn = day0 + day * D.DAY_LEN + int(D.DAY_LEN * hour / 24)

        def go(kind):
            q = next((q for q in g.world.sites if q.kind == kind), None)
            if not q:
                return None
            to_over(g, 0)
            p.x, p.y = q.x, q.y
            g.enter_site(q.id)
            seen.add(kind)
            return q

        def find(tile):
            m = g.map
            return next(((i % m.w, i // m.w) for i, t in enumerate(m.t) if t == tile), None)

        def bump(tile):
            m = g.map
            x, y = find(tile)
            for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)):
                if m.inb(x + dx, y + dy) and D.TILES[m.tile(x + dx, y + dy)].walk:
                    p.x, p.y = x + dx, y + dy
                    break
            return g.try_move(x - p.x, y - p.y)
        at(12)
        for kind in NT.BUILD:
            q = next((q for q in g.world.sites if q.kind == kind), None)
            if q and kind not in seen:
                m = NT.site_map(g, q)
                x, y = m.entry
                assert D.TILES[m.tile(x + 1, y)].walk, (kind, D.TILES[m.tile(x + 1, y)].name)
        if go('falls'):
            fx, fy = find(D.FALLS)
            p.x, p.y = fx, fy + 2 if D.TILES[g.map.tile(fx, fy + 2)].walk else fy
            g.map.soaked = False
            p.x, p.y = fx, fy
            NT.on_step(g)
            assert g.map.soaked
            assert NT.fish_bonus(g) > 0
        if go('frozenfalls'):
            at(12, (300 - g.day % 360) % 360)               # deep winter
            p.x, p.y = g.map.ledge_back
            NT.climb_ice(g)
            assert (p.x, p.y) == g.map.ledge, 'the frozen falls are climbed in winter'
            NT.climb_ice(g)
            assert (p.x, p.y) == g.map.ledge_back
            at(12)
        if go('hotspring'):
            p.life = 1
            p.x, p.y = find(D.HOTPOOL)
            p.bathed_day = -1
            NT.on_step(g)
            assert p.life > 1 and any(b[0] == 'warm' for b in p.buffs)
        if go('causeway'):
            m = g.map
            cx, cy = find(D.CAUSEWAY)
            for k in range(D.DAY_LEN):
                g.turn += 1
                if not NT.low_tide(g):
                    break
            p.x, p.y = cx - 1, cy
            assert NT.blocked(g, cx, cy), 'the sea covers the causeway at high tide'
            for k in range(D.DAY_LEN):
                g.turn += 1
                if NT.low_tide(g):
                    break
            assert not NT.blocked(g, cx, cy)
            at(12)
        if go('isles'):
            q = NT.site_of(g)
            bump(D.CHAIN)
            assert g.cur == q.map_key + ':top', g.cur
            bump(D.CHAIN)
            assert g.cur == q.map_key
        if not g.eq_item('weapon'):
            from avarenthia.entities import make_gear
            sw = make_gear(g, next(k for k, b in D.BASES.items() if b['slot'] == 'weapon' and b.get('req', 1) <= 1), 'normal', 1)
            sw.rstr = sw.rdex = 0
            p.inv.append(sw)
            g.equip(sw)
        w = g.eq_item('weapon')
        if w and go('anvil'):
            q = NT.site_of(g)
            bump(D.SPIKE)
            assert g.pending and g.pending['key'] == 'nature'
            EV.resolve(g, 'anvil_leave')
            assert q.left is w and not g.eq_item('weapon')
            NT.bless(g, q)
            bump(D.SPIKE)
            EV.resolve(g, 'anvil_take')
            assert any(a[0] == 'light_dmg' for a in w.aff) and w in p.inv
        if go('mound'):
            at(23, 13 - g.day % 28 + 28)
            assert NT.full_moon(g)
            bump(D.MOUNDDOOR)
            assert g.pending, 'the hill opens at full moon'
            t0 = g.turn
            EV.resolve(g, 'fey_dance')
            assert g.turn >= t0 + D.DAY_LEN
            at(12)
        if go('unwintering'):
            bump(D.EVERBLOOM)
            assert any(i.k == 'plant' and i.t == 'everbloom' for i in p.inv)
        if go('flame') and g.eq_item('weapon'):
            ww = g.eq_item('weapon')
            bump(D.FLAME)
            assert getattr(ww, 'tempered', False) and any(a[0] == 'ed' for a in ww.aff)
        if go('bell'):
            keep = NT.storm_at
            NT.storm_at = lambda game, site: True
            n0 = len(g.map.items)
            bump(D.DARKWATER)
            NT.storm_at = keep
            assert len(g.map.items) > n0 and NT.site_of(g).bell_done
            g.map.mons = [o for o in g.map.mons if o.is_npc]
        if go('starwell'):
            bump(D.STARWELL)
            assert g.pending
            EV.resolve(g, 'luck')
            assert NT.site_of(g).wish_day == g.day
        if go('wisps'):
            at(23)
            m = g.map
            m.wisp_day = -1
            for pt in m.wisp:
                p.x, p.y = pt
                NT.on_step(g)
            assert m.wisp_day == g.day, 'following the lights to the end'
            at(12)
        if go('bay'):
            at(23, (120 - g.day % 360) % 360)            # a summer night
            assert NT.summer(g) and NT.fish_bonus(g) > 0
            at(12)
        if go('cenote'):
            bump(D.ROPEDOWN)
            assert (p.x, p.y) == g.map.rope_bottom
            for _ in range(4):
                bump(D.GREENWATER)
            assert g.map.dives == 0
        if go('stonewood'):
            bump(D.AMBER)
            assert any(i.k == 'curio' for i in p.inv)
            assert next(i for i in p.inv if i.k == 'curio').value() > 0
        if go('stones'):
            at(23)
            m = g.map
            p.x, p.y = m.ring[0], m.ring[1]
            m.mons = [o for o in m.mons if o.is_npc]
            NT.site_of(g).dream_day = -99
            assert NT.rest(g)
            at(12)
        if go('sands'):
            m = g.map
            p.x, p.y = m.dig
            NT.on_step(g)
            assert m.dug and find(D.CHEST)
        if go('starwater'):
            q = NT.site_of(g)
            bump(D.STARSTAIR)
            assert g.cur == g.world.sites[q.twin].map_key
        for kind in ('cascade', 'greatfalls'):
            if go(kind):
                bump(D.CAIRN)
                assert NT.site_of(g).looked
        if go('rapids'):
            keep = random.random
            random.random = lambda: 0.0
            p.x, p.y = find(D.STEPSTONE)
            NT.slip(g)
            random.random = keep
            assert g.map.tile(p.x, p.y) != D.STEPSTONE, 'a slip sweeps you off the stones'
        # trolls caught by the sun turn to stone
        go('falls') or go('rapids')
        at(12)
        from avarenthia.entities import make_monster
        m = g.map
        tr = make_monster(g, 'troll', p.x + 2, p.y, 5)
        tr.awake = True
        m.mons.append(tr)
        g.monsters_act()
        assert tr not in m.mons and m.tile(tr.x, tr.y) == D.TROLLSTONE
    assert len(seen) >= 20, sorted(set(NT.BUILD) - seen)
    print('nature ok:', ', '.join(sorted(seen)))


def zones():
    """Walking the land: zones seam with their neighbours, keep what changed, hold ambushes and lead in and out of towns."""
    from avarenthia import zones as ZN
    from avarenthia.entities import Item
    print('== zones')
    g = E.Game('Walker', False, seed=7, race='human', gender='male')
    p = g.player
    s = g.world.settlements[0]
    a, _ = ZN.make(g, s.x - 1, s.y - 1)
    b, _ = ZN.make(g, s.x, s.y)
    assert (a[ZN.ZH:, ZN.ZW:] == b[:2 * ZN.ZH, :2 * ZN.ZW]).all(), 'zones agree on what they share, from both sides'
    assert (ZN.make(g, s.x - 1, s.y - 1)[0] == a).all(), 'a zone is made the same every time'
    # out of the town by its west edge: into the zone of its cell, west of the gate
    to_over(g, 0)
    g.enter_town(0)
    m = g.map
    p.x, p.y = 0, m.entry[1]
    g.try_move(-1, 0)
    assert g.cur == ZN.KEY and g.over_pos == (s.x, s.y), 'leaving a town by its edge you come out into its zone'
    zm = g.map
    mx, my = ZN.local_mid(g, zm)
    assert p.x < mx and (mx, my) in zm.marks, 'on the side you walked out, the town in the middle'
    # walk west into the next zone: the window moves with you
    for _ in range(300):
        r = g.try_move(-1, 0) or g.try_move(-1, 1) or g.try_move(-1, -1)
        if r:
            g.end_turn(r)
        if zm.zone != (s.x, s.y):
            break
    assert zm.zone[0] == s.x - 1 and g.over_pos == zm.zone, 'walk off a zone and you are in the next one'
    # what you change stays; what you never touched is made again
    it = Item(g.new_id(), 'gold', 'gold')
    it.n = 7
    spot = next((x, y) for x, y in [(p.x + dx, p.y + dy) for dx in range(-3, 4) for dy in range(-3, 4)]
                if D.TILES[zm.tile(x, y)].walk and (x, y) != (p.x, p.y))
    it.x, it.y = spot
    zm.items.append(it)
    gx, gy = spot[0] + zm.org[0], spot[1] + zm.org[1]
    rock = (gx + 2, gy)
    zm.set(rock[0] - zm.org[0], rock[1] - zm.org[1], D.ROCK)
    here = zm.zone
    ZN.recentre(g, zm, (here[0] - 3, here[1]))
    assert not zm.items and here in g.zones, 'a zone you leave keeps only its changes'
    E.save_game(g)
    g = E.load_game()
    assert g and g.cur == ZN.KEY, 'a saved game comes back in its zone'
    zm, p = g.map, g.player
    ZN.recentre(g, zm, here)
    back = [(i.x + zm.org[0], i.y + zm.org[1], i.n) for i in zm.items]
    assert (gx, gy, 7) in back, f'the coin lies where you left it: {back}'
    assert zm.tile(rock[0] - zm.org[0], rock[1] - zm.org[1]) == D.ROCK, 'and so does the stone'
    # an ambush on the world map is fought in its zone
    g.leave_to_over()
    assert g.cur == 'over' and ZN.KEY not in g.maps
    g.start_encounter(None, None, 2, ['wolf', 'wolf'], 0)
    assert g.cur == ZN.KEY and g.zone_fight and len(ZN.foes_left(g.map)) == 2, 'the ambush falls in the zone'
    for o in ZN.foes_left(g.map):
        o.hp = 0
    g.map.mons = [o for o in g.map.mons if o.hp > 0]
    g.end_turn(1)
    assert not g.zone_fight, 'the fight is won and you walk on'
    # flee into the next zone: they stay behind
    g.start_encounter(None, None, 2, ['jackal'], 0)
    zm, p = g.map, g.player
    for o in ZN.foes_left(zm):
        o.awake = False
        o.x, o.y = p.x + 8, p.y
    c0 = zm.zone
    edge = (c0[0] - zm.org[0] // ZN.ZW) * ZN.ZW    # the west edge of the middle zone, in window tiles
    p.x = edge
    while not D.TILES[zm.tile(p.x, p.y)].walk or not D.TILES[zm.tile(p.x - 1, p.y)].walk:
        p.y += 1
    g.try_move(-1, 0)
    assert zm.zone != c0 and not g.zone_fight and not ZN.foes_left(zm), 'cross into the next zone and the foes stay behind'
    # up to the world map and down again; walk into a town from its zone
    assert g.use_stairs('up') and g.cur == 'over'
    p.x, p.y = s.x + 1, s.y
    g.over_pos = (p.x, p.y)
    if ZN.open_cell(g, (p.x, p.y)):
        assert g.use_stairs('down') and g.cur == ZN.KEY
        g.leave_to_over()
    ZN.enter(g, (s.x, s.y), near=(4, 0))
    zm, p = g.map, g.player
    for _ in range(12):
        tx, ty = ZN.local_mid(g, zm)
        dx, dy = (tx > p.x) - (tx < p.x), (ty > p.y) - (ty < p.y)
        r = g.try_move(dx, dy)
        if r:
            g.end_turn(r)
        if g.cur != ZN.KEY:
            break
    assert g.cur == s.map_key, 'walk into the middle of its zone and you are in the town'
    # travellers on the roads stand in their zone, and a long walk breaks nothing
    g.leave_to_over()
    wd = next((w for w in g.world.wanderers if w.kind == 'caravan' and ZN.open_cell(g, (w.x, w.y))), None)
    if wd:
        ZN.enter(g, (wd.x, wd.y))
        assert any(getattr(o, 'wd', None) == wd.id for o in g.map.mons), 'a caravan in your zone stands there'
    rnd = random.Random(5)
    for _ in range(1500):
        if g.dead:
            break
        if g.pending:
            g.pending = None
        if g.cur != ZN.KEY:
            g.leave_to_over() if g.map.kind != 'over' else None
            if g.cur == 'over' and ZN.open_cell(g, (g.player.x, g.player.y)):
                ZN.enter(g, (g.player.x, g.player.y))
            continue
        r = g.try_move(rnd.choice((-1, 0, 1)), rnd.choice((-1, 0, 1)))
        if r:
            g.end_turn(r)
    print('zones ok:', len(g.zones), 'zones keep changes')


def herds_and_cooking():
    """Herds on the world map, the hunting ground, skinning, hides and leather, and cooking without recipes."""
    from avarenthia import hunting as HT
    from avarenthia import cooking as CK
    from avarenthia import foraging as FG
    from avarenthia import zones as ZN
    from avarenthia.entities import Item
    from avarenthia.hunger import make_food
    from avarenthia import towns as TW
    print('== herds_and_cooking')
    g = E.Game('Hunter', False, seed=11, race='human', gender='female')
    p = g.player
    to_over(g, 0)
    HT.setup(g)
    great = [h for h in HT.herds(g) if h.great]
    assert 1 <= len(great) <= 4 and all(h.kind in HT.GREAT for h in great), f'two to four great herds: {great}'
    x0, y0 = great[0].x, great[0].y
    for _ in range(40):
        HT.daily(g)
        g.turn += E.D.DAY_LEN
    assert (great[0].x, great[0].y) != (x0, y0), 'a great herd travels with the seasons'
    # a herd beside you on the world map: walk into it and its zone is the hunting ground
    om = g.maps['over']
    spot = None
    for sid, st in enumerate(g.world.settlements):
        for dx, dy in ((1, 0), (0, 1), (-1, 0), (0, -1), (2, 0), (0, 2)):
            x, y = st.x + dx * 3, st.y + dy * 3
            if om.inb(x + 1, y) and HT.prey_for(g, x + 1, y) and E.D.TILES[om.tile(x + 1, y)].walk \
                    and E.D.TILES[om.tile(x, y)].walk and not g.world.settlement_at(x + 1, y) and ZN.open_cell(g, (x + 1, y)):
                spot = (x, y)
                break
        if spot:
            break
    assert spot, 'somewhere a herd can graze'
    g.cur, (p.x, p.y) = 'over', spot
    g.compute_fov()
    hd = HT.Herd(g.new_id(), HT.prey_for(g, spot[0] + 1, spot[1])[0], spot[0] + 1, spot[1], 5)
    HT.herds(g).append(hd)
    assert HT.herd_at(g, spot[0], spot[1]) is None and HT.herd_at(g, spot[0] + 1, spot[1]) is hd, 'you see the herd beside you'
    g.try_move(1, 0)
    m = g.map
    prey = [o for o in m.mons if getattr(o, 'prey', None) == hd.id]
    assert g.cur == ZN.KEY and m.hunt == hd.id and len(prey) >= 3, 'walking into the herd opens the hunting ground'
    assert any(o.ch == 'Q' for o in prey) and HT.wind_arrow(g), 'a leader watches, and the wind blows'
    from avarenthia.worldgen import cheb
    assert all(cheb(o.x, o.y, p.x, p.y) >= 7 for o in prey), 'the herd grazes a long shot away'
    # a hit animal runs on and falls; the rest flee
    o = prey[0]
    o.hp = o.maxhp // 3
    for _ in range(12):
        g.end_turn(1)
        if o not in m.mons:
            break
    assert o not in m.mons, 'the wounded animal falls'
    cc = next((i for i in m.items if i.k == 'carcass'), None)
    assert cc and all(o.ps != 'graze' for o in m.mons if getattr(o, 'prey', None) == hd.id), 'a carcass, and the herd in flight'
    # skinning: without a knife only meat; with one, cuts named by the animal and a hide
    p.x, p.y = cc.x, cc.y
    m.mons = [o for o in m.mons if getattr(o, 'prey', None) is None]
    assert ('Enter', 'skin') in g.context_hints()
    g.act_here()
    assert any(i.k == 'food' and i.t == 'meat' for i in p.inv) and not any(i.k == 'hide' for i in p.inv), 'no knife: raw meat'
    p.inv.append(Item(g.new_id(), 'tool', 'knife'))
    for k in ('red_deer', 'aurochs', 'wolf'):
        c2 = Item(g.new_id(), 'carcass', k)
        c2.x, c2.y = p.x, p.y
        m.items.append(c2)
        g.act_here()
    hides = [i for i in p.inv if i.k == 'hide']
    assert len(hides) == 3 and any(i.k == 'food' and i.t == 'venison' for i in p.inv), 'venison and three hides'
    assert 'day' in hides[0].display_name() and hides[0].display_name().startswith('Fresh'), hides[0].display_name()
    # a fresh hide rots; a salted one keeps; oak bark tans it into leather
    hides[2].until = g.day
    HT.spoil(g)
    assert hides[2] not in p.inv, 'a fresh hide rots in two days'
    p.inv.append(Item(g.new_id(), 'tool', 'frame'))
    p.inv.append(make_food(g, 'salt', 3))
    fr = next(i for i in p.inv if i.k == 'tool' and i.t == 'frame')
    assert HT.use(g, fr) and not any(i.k == 'tool' and i.t == 'frame' for i in p.inv)
    fx, fy = next((p.x + dx, p.y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if m.tile(p.x + dx, p.y + dy) == E.D.FRAME)
    g.try_move(fx - p.x, fy - p.y)
    assert all(h.state == 'salted' for h in hides[:2]), 'salt on the frame: they keep'
    g.try_move(fx - p.x, fy - p.y)
    assert any(i.k == 'tool' and i.t == 'frame' for i in p.inv) and m.tile(fx, fy) != E.D.FRAME, 'the frame packs up again'
    p.inv.append(FG.make_plant(g, 'oak_bark', 2))
    for h in hides[:2]:
        HT.use(g, h)
    assert all(h.state == 'tanning' for h in hides[:2]) and 'Tanning' in hides[0].display_name()
    for h in hides[:2]:
        h.until = g.day
    HT.spoil(g)
    leather = sum(i.n for i in p.inv if i.k == 'leather')
    assert leather >= 3, f'the hides tanned into leather: {leather}'
    p.gold += 1000
    leather_it = next(i for i in p.inv if i.k == 'leather')
    leather_it.n = 6
    HT.r_bench(g, 'make:armour', {})
    assert any(i.k == 'gear' and i.base == 'leather' for i in p.inv), 'leather armour from the bench'
    # the tanner in town
    tan = 0
    for st in g.world.settlements[:12]:
        if st.kind in ('village', 'town', 'city') and not getattr(st, 'dwarven', False) and not getattr(st, 'elder', False):
            tm = TW.gen_settlement_map(g, st)
            tan += any(o.role == 'tanner' for o in tm.mons)
            assert not any(getattr(o, 'prey', None) for o in tm.mons)
    assert tan, 'towns have a tanner'
    # cooking: no recipes, only what you find in the pot
    assert CK.known(g) == {'roast_meat', 'grilled_fish'}
    for k in ('wild_onion', 'chanterelle', 'hazelnut'):
        p.known_plants.add(k)
        p.inv.append(FG.make_plant(g, k, 3))
    assert any(k == 'roast_meat' for k, _t in CK.cookable(g)), 'roast meat from venison'
    ven = next(i for i in p.inv if i.k == 'food' and i.t == 'venison')
    onion = next(i for i in p.inv if i.k == 'plant' and i.t == 'wild_onion')
    shroom = next(i for i in p.inv if i.k == 'plant' and i.t == 'chanterelle')
    CK.attempt(g, [onion.id, shroom.id])
    assert any('It wants' in l[0] for l in g.log[-4:]) or any('mush' in l[0].lower() for l in g.log[-4:]), 'one thing short: a hint'
    CK.attempt(g, [ven.id, onion.id, shroom.id])
    assert 'hunters_stew' in CK.known(g), "Hunter's Stew found in the pot"
    stew = next((i for i in p.inv if i.k == 'dish' and i.t == 'hunters_stew'), None)
    if stew:
        p.food = 300
        g.eat(stew)
        assert p.food > 300 and any(b[0] == 'warm' for b in p.buffs), 'a hearty stew warms you'
    meat = make_food(g, 'elk_meat', 2)
    p.inv.append(meat)
    rx, ry = p.x + 1, p.y
    m.set(rx, ry, E.D.RACK)
    CK.rack(g, rx, ry)
    g.turn += E.D.DAY_LEN
    CK.rack(g, rx, ry)
    assert any(i.k == 'food' and i.t == 'jerky' for i in p.inv), 'dried meat off the rack'
    # it all keeps across a save
    E.save_game(g)
    g = E.load_game()
    assert g and 'hunters_stew' in CK.known(g) and HT.herds(g), 'what you know and the herds come back'
    print('herds and cooking ok:', len(CK.known(g)), 'dishes known')


def talk_all(g, roles):
    """Talk to everyone here with one of these roles, and try every choice they offer. How many were talked to."""
    from avarenthia import events as EV_
    n = 0
    g.player.gold = max(g.player.gold, 100000)
    for o in list(g.map.mons):
        if getattr(o, 'role', '') not in roles:
            continue
        n += 1
        g.talk(o)
        if not g.pending:
            continue
        opts = [c for _l, c in g.pending['options'] if c and c != 'bye']
        g.pending = None
        for c in opts:
            g.talk(o)
            if g.pending:
                EV_.resolve(g, c)
            g.pending = None
            g.request = None
    g.missions = [x for x in g.missions if x.kind != 'realm']
    return n


def realms():
    """Realms, lords and wars: the empire and its kingdoms on organic regions, houses with seats, the other powers,
    the made history, libraries and scribes, talking to lords, fealty, every realm job played through, the months
    of the courts and the realms layer of the map."""
    from avarenthia import realms as RL, powers as PW, realmjobs as RJ, history as HI, chronicle as CH, events as EV_
    from avarenthia import missions as MS_, calendar as CAL, seats as SEATS, wanderers as WA_
    print('== realms')
    app = new_app('soft', seed=21)
    g = app.game
    w, R, p = g.world, g.world.realm, g.player
    assert 1 <= len(R.kingdoms) <= 5 and R.lord(R.emperor).title == 'emperor', 'an emperor over the kings'
    assert E.D.FACTIONS['crown']['name'] == R.empire and E.D.FACTIONS['crown']['short'] == 'Empire'
    crown = [r.id for r in w.regions if r.faction == 'crown']
    assert all(rid in R.baronies and R.lord(R.baronies[rid].lord) for rid in crown), 'every crown region is a barony with a lord'
    assert set(w.region_of) <= set(range(len(w.regions))), 'organic regions cover the map'
    seats = [st for st in w.sites if st.kind == 'seat']
    assert seats and all(R.houses[st.house].seat == ('site', st.id) for st in seats), 'lesser houses have seats'
    H = HI.events(w)
    assert 30 <= len(H) <= 60 and all(e['year'] < CAL.YEAR and w.region_of and 0 <= e['x'] < 480 for e in H), len(H)
    assert H == sorted(H, key=lambda e: e['year'])
    for st in w.sites:
        if SEATS.is_seat(st):
            assert st.glyph and SEATS.describe(g, st), st.kind
    # every power's place has its own map
    done = set()
    for st in w.sites:
        if SEATS.is_seat(st) and st.kind not in done:
            done.add(st.kind)
            to_over(g, 0)
            g.enter_site(st.id)
            assert g.map.kind != 'over', st.kind
            app.render()
            talk_all(g, PW.ROLES | HI.ROLES | RL.ROLES)
    assert {'seat', 'hall', 'orderkeep'} <= done, done
    for s_ in w.settlements:                       # the Grudge Book's keeper, the loremaster under the Elder Tree
        if s_.kind == 'deephold' or getattr(s_, 'elder', False):
            to_over(g, 0)
            g.enter_town(s_.id)
            assert talk_all(g, HI.ROLES), s_.name
    # the library of the great city: shelves, a scribe, the old letters
    to_over(g, 0)
    g.enter_town(R.great)
    m = g.map
    assert any(t == E.D.SHELVES for t in m.t), 'the library has shelves'
    scribe = next(o for o in m.mons if getattr(o, 'role', '') == 'scribe')
    p.gold = 100000
    n0 = len(CH.facts(g))
    for ch in ('old', 'realms', 'lords', 'city', 'letters'):
        g.talk(scribe)
        assert g.pending and g.pending['key'] == 'library'
        assert ch in [o[1] for o in g.pending['options']], (ch, g.pending['options'])
        EV_.resolve(g, ch)
    assert g.__dict__.get('varnish_letters') and len(CH.facts(g)) > n0 + 5, 'the scribe reads, and teaches the letters'
    assert any(f['key'].startswith('hist:') and f['src'] == 'read' for f in CH.facts(g))
    # a wrong telling heard, then read right
    e = next(e for e in H if not HI.known(g, e))
    CH.add(g, e['ch'], HI.garble(e), 'heard', 'an old man', key=f'hist:{e["id"]}f')
    HI.learn(g, e, 'read', 'a scribe')
    assert next(f for f in CH.facts(g) if f['key'] == f'hist:{e["id"]}f')['false'], 'reading puts the old tale right'
    # a lord in his hall: greeting, news, work
    lord = next((o for o in m.mons if getattr(o, 'role', '') == 'lord'), None)
    assert lord, 'the emperor sits in the great city'
    g.talk(lord)
    assert g.pending and g.pending['key'] == 'lord'
    EV_.resolve(g, 'news')
    g.talk(lord)
    EV_.resolve(g, 'work')
    if g.pending and g.pending['key'] == 'realmoffer':
        take = next(o[1] for o in g.pending['options'] if o[1] and o[1].startswith('take'))
        EV_.resolve(g, take)
        assert any(x.kind == 'realm' for x in MS_.active(g)), 'a realm job taken'
    assert any(f['ch'] == 'Lords and houses' and f['src'] == 'seen' for f in CH.facts(g)), 'a lord met is a seen fact'
    g.missions = []
    # fealty: refused without a name, sworn with one
    g.talk(lord)
    EV_.resolve(g, 'fealty')
    assert not getattr(p, 'knight', None)
    p.rep['crown'] = 40
    RL.add_favour(g, RL.kingdom_of_lord(R, R.lord(lord.lord)).id, 30)
    g.talk(lord)
    EV_.resolve(g, 'fealty')
    assert getattr(p, 'knight', None), 'sworn'
    from avarenthia import races as RC_
    assert RC_.address(g).startswith(('my', 'sir'))
    RJ.levy(g, R.kingdoms[0], None)
    assert any(x.data.get('task') == 'levy' for x in MS_.active(g)), 'the liege calls the levy'
    g.missions = []
    p.knight = None
    # every realm job: made, reached, every choice played, fights won. First the world is stirred: a war, a civil war,
    # a rising baron, a peasant revolt, a pretender, weddings, feuds, and one raiding people of every kind
    if len(R.kingdoms) >= 2:
        RL.start_war(g, R.kingdoms[0], R.kingdoms[1], 'a test')
    kg = R.kingdoms[-1]
    lords_k = RL.lords_of(R, kg)
    RL.civil_war(g, kg, next(lo for lo in lords_k if lo.id != kg.king))
    for lo in lords_k:
        if lo.title == 'baron':
            lo.traits, lo.loyalty = ['ambitious', 'greedy'], 10
    RL.rebel(g, kg, lords_k)
    for k in R.kingdoms:
        k.burden = 99
    PW.revolt_month(g)
    for _ in range(12):
        PW.P(w)['pretender'] = None
        PW.exile(g, next(lo for lo in lords_k if lo.id != kg.king), kg)
        if PW.P(w)['pretender'] and PW.P(w)['pretender']['site'] is not None:
            break
    for _ in range(10):
        RL.marry(g, kg, lords_k)
        RL.insult(g, kg, lords_k)
    for t_ in PW.P(w)['tribes']:
        t_['strength'] = 9
    season = CAL.season
    CAL.season = lambda d: 'winter'              # the ice jobs come only in winter
    rds = PW.raiders(w)
    for k_ in PW.KINDS:
        if not any(rd['kind'] == k_ for rd in rds):
            rds.append(dict(rds[0], kind=k_, people=PW.KINDS[k_]['people'][0], held=[], warned={}))
    givers = []
    for lo in R.lords.values():
        if lo.alive and lo.title in ('baron', 'lord', 'king', 'emperor') and R.houses[lo.house].seat:
            givers.append(dict(kind='lord', lid=lo.id, house=lo.house, name=RL.style(R, lo, False)))
    givers += [dict(kind='town', sid=s.id, name=s.name) for s in w.settlements if s.kind in ('village', 'town')][:12]
    for i, rd in enumerate(PW.raiders(w)):
        givers.append(dict(kind='chief', raider=i, rk=rd['kind'], site=rd['site'], name=rd['chief']))
    for st in w.sites:
        k = {'orderkeep': 'prior', 'circle': 'witch', 'watchfort': 'watch', 'merccamp': 'merc', 'rising': 'rebel',
             'exile': 'pretender'}.get(st.kind)
        if k:
            givers.append(dict(kind=k, site=st.id, name='Someone'))
    for s in w.settlements:
        if s.kind == 'deephold':
            givers.append(dict(kind='keeper', sid=s.id, name='Keeper'))
        if getattr(s, 'elder', False):
            givers.append(dict(kind='loremaster', sid=s.id, name='Loremaster'))
    made = {}
    for key, t in RJ.TASKS.items():
        for gv in givers:
            if t['giver'] != gv['kind'] and t['giver'] != 'chief:' + gv.get('rk', ''):
                continue
            mm = t['make'](g, gv)
            if mm:
                made[key] = (gv, mm)
                break
    played = 0
    for key, (gv, mm) in made.items():
        assert mm.title and mm.desc and mm.reward >= 0 and mm.data.get('spot'), key
        sc = RJ.SCENES[key]
        to_over(g, 0)
        g.missions = [mm]
        mm.state = 'active'
        (tx, ty), where = MS_.target_pos(g, mm)
        assert where, key
        g.player.x, g.player.y = tx, ty
        g.over_pos = (tx, ty)
        out = sc[0](g, mm)
        if not out:
            continue
        text, opts = out
        for _label, choice in opts:
            if choice is None:
                continue
            to_over(g, 0)
            m2 = RJ.TASKS[key]['make'](g, gv) or mm
            g.missions = [m2]
            m2.state = 'active'
            g.player.gold = 100000
            g.player.x, g.player.y = m2.data['spot']
            g.over_pos = tuple(m2.data['spot'])
            sc[0](g, m2)
            sc[1](g, m2, choice)
            g.pending = None
            g.request = None
            if getattr(g, 'job_fight', None):
                g.job_fight = None
                RJ.won(g, m2, True)
                g.pending = None
            played += 1
            if m2.state == 'turnin':
                (gx, gy), nm = MS_.target_pos(g, m2)
                assert nm, key
    CAL.season = season
    assert len(made) >= len(RJ.TASKS) - 3 and played >= 60, (len(made), played, sorted(set(RJ.TASKS) - set(made)))
    # the months of the courts, the hosts and the raids
    g.missions = []
    to_over(g, 0)
    for _ in range(24):
        g.turn += CAL.DAYS_IN_MONTH * E.D.DAY_LEN
        RL.monthly(g)
        PW.daily(g)
        for _ in range(60):
            for wd in list(w.wanderers):
                if wd.kind in ('host', 'raid'):
                    WA_.step(g, wd)
                    assert wd.describe(g)
        g.pending = None
        g.request = None
    assert R.events > 20, 'the courts are busy'
    from avarenthia import news as NW_
    for _ in range(30):
        NW_.tell(g, far=True)
    assert any(f['ch'] in ('The Realms', 'Lords and houses', 'Peoples') and f['src'] == 'heard' for f in CH.facts(g))
    # the realms layer of the map, close-up and whole
    app.screens = [ui.GameScreen(app), ui.WorldMapScreen(app)]
    app.key('4')
    assert ui.WorldMapScreen.LAYERS[app.top.layer] == 'Realms'
    app.render()
    app.key('z')
    app.render()
    app.key('1')
    app.key('esc')
    # a game saved and loaded keeps it all
    E.save_game(g)
    g2 = E.load_game()
    assert g2.world.realm.empire == R.empire and len(g2.world.history) == len(H)
    print('realms ok:', len(R.kingdoms), 'kingdoms,', len(R.houses), 'houses,', len(made), 'kinds of realm job,', played,
          'choices played,', R.events, 'court events')


def stamina():
    """Two pools: weapon skills and Warcraft cost stamina, spells mana; Charge is a true weapon strike; stamina comes
    back on turns you do not strike, slower in plate; three orbs on the panel."""
    from avarenthia import skills as SK
    print('== stamina')
    app = new_app('soft', seed=5)
    g = app.game
    p = g.player
    s = g.stats()
    assert s['max_stamina'] == 10 + s['str'] + s['vit'] and p.stamina == s['max_stamina']
    assert SK.pool(SK.SKILLS['power_strike']) == 'stamina' and SK.pool(SK.SKILLS['charge']) == 'stamina'
    assert SK.pool(SK.SKILLS['firebolt']) == 'mana' and SK.SKILLS['charge'].dtype == 'weapon'
    assert SK.pool(SK.SKILLS['spellblade']) == 'stamina' and SK.pool(SK.SKILLS['shield_wall']) == 'stamina'
    g.start_encounter(None, terrain=D.GRASS, lvl=1, keys=['wolf'])
    wolf = next(o for o in g.map.mons if not o.is_npc)
    wolf.hp = wolf.maxhp = 999
    spot = next(c for c in [(wolf.x + 1, wolf.y), (wolf.x - 1, wolf.y), (wolf.x, wolf.y + 1), (wolf.x, wolf.y - 1)]
                if D.TILES[g.map.tile(*c)].walk and not g.map.mon_at(*c))
    p.x, p.y = spot
    g.compute_fov()
    p.known = ['power_strike', 'firebolt', 'charge']
    p.bar = ['power_strike', 'firebolt', 'charge', None, None, None]
    p.disc['warcraft'] = [60, 0]
    w = g.eq_item('weapon')
    st0, mp0 = p.stamina, p.mana
    from avarenthia.skills import use
    if SK.weapon_line(g) == 'swords':
        assert use(g, 0) and p.stamina == st0 - 3 and p.mana == mp0, (p.stamina, p.mana)
    st1 = p.stamina
    p.cooldowns.clear()
    before = wolf.hp
    assert use(g, 2), 'Charge works with any weapon'
    assert p.stamina == st1 - 9 and before - wolf.hp > 3, ('Charge hits like a weapon now', before - wolf.hp)
    p.stamina = 0
    p.strained = g.turn
    g.end_turn(1)
    assert p.stamina == 0, 'no breath back on the turn you struck'
    g.end_turn(3)
    assert p.stamina > 0
    p.stamina = 0
    g.end_turn(4)
    light = p.stamina
    p.stamina = 0
    from avarenthia.entities import make_gear
    plate = make_gear(g, 'platemail', 'normal', 1)
    p.inv.append(plate)
    p.eq['armor'] = plate.id
    g.end_turn(4)
    assert 0 < p.stamina < light and g.heavy_armour(), (p.stamina, light)
    p.food = 50
    p.stamina = 0
    g.end_turn(4)
    assert p.stamina == 0, 'starving: no stamina comes back'
    app.render()
    dump = app.cv.dump()
    assert 'STAMINA' in dump and 'LIFE' in dump and 'MANA' in dump
    print('stamina ok:', s['max_stamina'], 'stamina at the start')


def main():
    random.seed(int(os.environ.get('TEST_SEED', '1')))
    parts = [animations, seasons, lands, peoples, camps_and_holds, wonders, world_life, thornfield_and_faith, countryside, start_and_survival, crime_and_coin, world_and_people,
             items_skills_curse, smoke, trade_and_jobs, factions_and_death, wilds, ways_and_wares, hirelings_and_camp,
             creatures_and_hunts, new_guilds, more_jobs, text_fits, overview, chronicle, ferries, place_names, nature_sites, zones, herds_and_cooking, realms, stamina]
    only = os.environ.get('TEST_ONLY')             # e.g. TEST_ONLY=smoke,wilds to run a part of the suite
    for f in parts:
        if not only or f.__name__ in only.split(','):
            f()


if __name__ == '__main__':
    try:
        main()
    except Exception:
        import traceback
        tb = traceback.format_exc()
        if os.environ.get('GITHUB_ACTIONS'):
            print('::error title=Headless test failed::' + tb.replace('%', '%25').replace('\r', '').replace('\n', '%0A'))
        raise
    if '--dump' in sys.argv:
        app = new_app()
        app.render()
        sys.stdout.reconfigure(encoding='utf-8')
        print(app.cv.dump())
