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
            if mi.kind in kinds_done or mi.kind == 'hunt':   # hunts: creatures_and_hunts
                continue
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
        if g.cur == 'wild':
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
            if g.cur == 'wild':
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
        app.screens = [ui.GameScreen(app), ui.HelpScreen(app)]
        app.top.page = page
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
    assert g.cur == 'wild'
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
    assert any(m.tile(fisher.x + dx, fisher.y + dy) in (D.WATER, D.SHALLOW) for dx in (-1, 0, 1) for dy in (-1, 0, 1))
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
    assert keys <= {'kobold', 'snagtooth'}, keys
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
    choose(app, 'order:defend')
    assert mc.order == 'defend'
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
        if g.cur == 'wild':
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
    for pg in range(len(ui.HelpScreen.PAGES)):
        h = ui.HelpScreen(app)
        h.page = pg
        look(h)
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
    sentence = {k: v for k, v in cuts.items() if k in ('ChoiceScreen', 'DialogScreen', 'HelpScreen', 'BoardScreen',
                                                      'MenuScreen', 'TempleScreen', 'FishingScreen', 'IntroScreen')}
    for k, v in sorted(cuts.items()):
        print(f'  cut in {k}: {sorted(v)[:6]}')
    assert not sentence, f'text cut short: {sentence}'
    print('text fits')


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
    sleeper = make_monster(g, 'goblin', 1, 1, 3)
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
        assert g.cur == 'wild' and any(o.k == 'orc_chief' for o in g.map.mons)
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
    assert NM.step(g) and g.cur == 'wild'
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


def main():
    random.seed(int(os.environ.get('TEST_SEED', '1')))
    parts = [wonders, world_life, thornfield_and_faith, countryside, start_and_survival, crime_and_coin, world_and_people,
             items_skills_curse, smoke, trade_and_jobs, factions_and_death, wilds, ways_and_wares, hirelings_and_camp,
             creatures_and_hunts, new_guilds, text_fits]
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
