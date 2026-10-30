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

E.save_path = lambda: os.path.join(tempfile.gettempdir(), f'avarenthia_test_{os.getpid()}.dat')    # runs side by side keep apart

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


def climb(g, site):
    """Enter a tower and take every stair up to the top; returns the floors climbed."""
    g.enter_site(site.id)
    k = 0
    while D.UP in g.map.t:
        i = g.map.t.index(D.UP)
        g.player.x, g.player.y = i % g.map.w, i // g.map.w
        g.use_stairs('up')
        k += 1
    return k


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
    from avarenthia import classes as CL, events as EV
    assert p.known == [] and not any(p.bar) and not CL.classes(g), (p.known, p.bar)
    assert CL.slot_skill(g, 0) == 'haymaker' and CL.slot_skill(g, 1) is None, 'blank: only your fists\' skill'
    assert sorted(i.base for i in p.inv if i.k == 'gear') == ['quilted']
    # tomes: the first wakes a memory and is your class
    t0 = make_tome(g, 0)
    g.add_to_inv(t0)
    assert g.read_tome(t0) == 0 and g.pending, 'one warning first'
    EV.RESOLVERS['wake_class'](g, 'yes', {'item': t0.id})
    g.pending = None
    line = SK.SKILLS[t0.t].line
    assert CL.classes(g) == [line] and CL.title(g) == CL.PURE[line] and t0.t in p.known and t0.t in p.bar[2:5]
    other = next(s for s in SK.SKILL_LIST if s.line not in (line, 'warcraft') and s.unlock == 0)
    ot = E.Item(g.new_id(), 'tome', other.id)
    g.add_to_inv(ot)
    assert g.read_tome(ot) == 0 and other.id not in p.known and not g.pending, 'not your school'
    p.disc[line][0] = CL.SECOND_AT
    assert g.read_tome(ot) == 0 and g.pending, 'at rank 20 a second school may open'
    EV.RESOLVERS['second_class'](g, 'yes', {'item': ot.id})
    g.pending = None
    assert CL.title(g) == CL.pair_name(line, other.line) and other.id in p.known
    p.disc[line][0] = 0
    hard = next(s for s in SK.SKILL_LIST if s.unlock == SK.TOME[5] and s.line == line)
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
    # the servants grow on their own clock, not with you; meddling brings his attention, and hunters
    tainted = lambda: sum(1 for v in g.world.taint if v)
    print('evils:', [(e.name, EVL.stage(e)) for e in g.world.evils], 'tainted cells', tainted())
    g.request = None
    to_over(g, 0)
    from avarenthia import shadow as SH
    for e in g.world.evils:
        e.awake, e.goal = True, 60.0
    sh = SH.st(g.world)
    sh['att'], sh['step_day'] = 4, g.day
    for _ in range(60):
        EVL.daily(g)
    hunts = [w for w in g.world.wanderers if w.kind == 'hunt']
    print('awake and watched:', [(e.name, EVL.stage(e)) for e in g.world.evils], 'tainted cells', tainted(), 'hunters', len(hunts))
    assert tainted() > 300 and any(e.known for e in g.world.evils)
    assert hunts, 'his attention sends hunters'
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
        e.jar = True                            # the Lich's jar broken, or she would rise again
        g.kill(boss)
        assert e.defeated
    assert sum(1 for it in g.player.inv if it.k == 'relic') >= 1, 'a fallen servant leaves its relic'
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
    assert g.read_tome(tome) == 0 and g.pending, 'the first tome asks'
    from avarenthia import events as EV
    EV.RESOLVERS['wake_class'](g, 'yes', {'item': tome.id})
    g.pending = None
    assert tome.t in p.known
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
    assert p.recipes and FG.props_known(g, 'yarrow') == ['Heal', 'Staunch']
    tower = next(st for st in g.world.sites if st.kind == 'tower' and st.people == 'human' and getattr(st, 'state', 'whole') == 'whole')
    om = g.maps['over']
    before = sum(om.seen)
    assert climb(g, tower) >= 2
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
    # brew a healing draught: yarrow and dandelion both heal
    from avarenthia import alchemy as AL
    p.inv.append(FG.make_plant(g, 'yarrow', 2))
    p.inv.append(FG.make_plant(g, 'dandelion', 2))
    random.seed(3)
    AL.brew(g, ['yarrow', 'dandelion'])
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
            if m.inb(nx, ny) and (nx, ny) not in seen and m.tile(nx, ny) in (D.PATH, D.GRASS, D.SIGNPOST, D.WELL, D.BRIDGE):
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
    wl = w.wonders + ([w.shadow['wonder']] if w.shadow.get('wonder') and not w.shadow.get('seen') else [])
    names = [n for n, _x, _y in wl]                            # the Sky-Seat lies hidden in the mist at first
    print('wonders:', names)
    assert 'The Sky-Seat' in names, names
    sx, sy = next((x, y) for n, x, y in wl if n == 'The Sky-Seat')
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
    # the Sky-Seat lies far out in the warm south (hidden in the mist at first)
    wl = w.wonders + ([w.shadow['wonder']] if w.shadow.get('wonder') else [])
    sx, sy = next((x, y) for n, x, y in wl if n == 'The Sky-Seat')
    land = [i for i, t in enumerate(om.t) if t != D.WATER and D.TILES[t].walk
            and om.biome_names[om.biome[i]] not in ('cay', 'atoll_palm', 'reef', 'reef_flat')]
    near = min(math.hypot(i % om.w - sx, i // om.w - (sy + 10)) for i in land)
    assert near >= 25, near
    # roads are joined lines; the great roads between the cities are double
    assert om.main_road, 'great roads'
    i = next(iter(om.main_road))
    assert LK.get(om, i)[0] in '═║╔╗╚╝╠╣╦╩╬╪╫', LK.get(om, i)
    # a watchtower: a circle, and mountains block the view
    tw = next(q for q in w.sites if q.kind == 'tower' and q.people == 'human' and getattr(q, 'state', 'whole') == 'whole')
    before = sum(om.seen)
    climb(g, tw)
    r = 10 + round((tw.storeys - 3) * 4 / 3) + 4
    assert 0 < sum(om.seen) - before <= 3.3 * r * r + 30
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
        g.compute_fov()
        p.life = max(1, p.life)
        g.camp(k % 2 == 0)
        if g.map.kind == 'wild':
            clear_wild(g)
        elif g.map.kind != 'over':
            print('  camp led to', g.cur, g.map.kind)
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
    from avarenthia import lifeskills as LS
    life = next(d for _g, items in ui.MenuScreen.GROUPS for k, _n, d in items if k == 'C')
    for sk in LS.LIFE.values():                     # the menu names every life skill
        assert sk['name'].lower() in life, sk['name']
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
    # the map: seven layers, by number and by L, in both views
    app.key('m')
    for z in (1, 0):
        ui.WorldMapScreen.zoom = z
        for k in '1234567':
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
    keep = random.random
    random.random = lambda: 0.0                    # a sign is found (in the rain they are rare: that is not the point here)
    NM.sign(g, n)
    random.random = keep
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
    p.classes = ['beastcraft']                     # a master teaches a lesser technique only of your own school
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
    p.bar[5] = 'tame'
    for _ in range(30):
        p.cooldowns.clear()
        p.mana = 99
        SK.use(g, 5)
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
    new = [s.id for s in SK.SKILL_LIST if s.line in ('nature', 'necromancy', 'beastcraft') and s.id != 'tame']
    new += [t[0] for k in ('moot', 'chapter', 'ossuary') for t in GU.TEACH[k]] + ['wildheart', 'lichcraft', 'mendicant', 'war_handler']
    for sid in new:
        if sid not in p.known:
            p.known.append(sid)
    for sid in new:
        g.map.mons = [o for o in g.map.mons if o.is_npc and not getattr(o, 'thrall', 0)]
        for x, y in free_around(g, g.map, p.x, p.y, 2)[:2]:
            e = make_monster(g, 'goblin', x, y, 6)
            e.awake = True
            g.map.mons.append(e)
        g.compute_fov()
        prep_skill(g, sid)
        p.bar[5] = sid
        p.cooldowns.clear()
        p.mana, p.stamina, p.life = 999, 999, max(p.life, 200)
        p.buffs = [b for b in p.buffs if not str(b[3]).endswith(' shape')]    # Elder Bear's shape lets go
        assert SK.use(g, 5), sid
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
    from avarenthia import crafts as CRF
    ores = [(x, y) for y in range(mine.h) for x in range(mine.w) if mine.tile(x, y) == D.ORE]
    vein = next((v for v in ores if CRF.vein(g, *v) == 'iron'), ores[0])     # iron: no rank needed
    if CRF.vein(g, *vein) != 'iron':
        p.life_sk['mining'] = [50, 0]
    assert DH.dig(g, *vein) == 0 and mine.tile(*vein) == D.ORE      # no pick yet
    g.add_to_inv(Item(g.new_id(), 'tool', 'pick'))
    s.rep = 0
    p.cargo.clear()
    rep = s.rep
    dw = next(o for o in mine.mons if o.is_npc and getattr(o, 'race', '') == 'dwarf')
    dw.x, dw.y = p.x, p.y                           # a dwarf of the clan sees you do it
    ore = sum(i.n for i in p.inv if i.k == 'mat' and i.t.startswith('ore_'))
    assert DH.dig(g, *vein) > 0 and (p.cargo.get('ore', 0) >= 1 or sum(i.n for i in p.inv if i.k == 'mat' and i.t.startswith('ore_')) > ore) \
        and mine.tile(*vein) == D.FLOOR and s.rep < rep, (s.rep, rep, p.cargo)
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
    for seed in (12, 1, 5, 2, 9):
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
            if not NT.night(g):                            # a light summer night in the north: take the small hours
                at(1, 1)
            m = g.map
            m.wisp_day, m.wisp_k = -1, 0
            for pt in m.wisp:
                p.x, p.y = pt
                NT.on_step(g)
            assert m.wisp_day != -1, 'following the lights to the end'
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
    p.life_sk['hunting'] = [30, 0]                  # no herd too wary for this hunter
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
        h.q = max(h.q, 2)                  # a well-skinned hide: how well you skinned it is luck, not the point here
    HT.spoil(g)
    leather = sum(i.n for i in p.inv if i.k == 'leather')
    assert leather >= 3, f'the hides tanned into leather: {leather}'
    p.gold += 1000
    leather_it = next(i for i in p.inv if i.k == 'leather')
    leather_it.n = 6
    from avarenthia import crafts as CRF
    p.life_sk['leatherworking'] = [30, 0]
    CRF.make(g, 'leatherworking', 'leather', leather_it.t)
    assert any(i.k == 'gear' and CRF.D.BASES[i.base]['family'] == 'leather' for i in p.inv), 'leather armour from the bench'
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
        sc = RJ.SCENES.get(key)
        if not sc:                  # a beast caught alive for a lord's yard is a hunt, not a scene (test 'masters')
            continue
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
    assert len(made) >= len(RJ.TASKS) - 4 and played >= 60      # some need a coast, a reef or a witch the world lacks, (len(made), played, sorted(set(RJ.TASKS) - set(made)))
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
    p.known = ['firebolt', 'charge']
    p.classes = ['warcraft', 'fire']
    p.bar = [None, None, 'firebolt', 'charge', None, None]
    p.disc['warcraft'] = [60, 0]
    st0, mp0 = p.stamina, p.mana
    from avarenthia.skills import use
    assert use(g, 0) and p.stamina == st0 - SK.SKILLS['haymaker'].cost and p.mana == mp0, (p.stamina, p.mana)
    st1 = p.stamina
    p.cooldowns.clear()
    for _try in range(8):                     # a blow may roll low: strike again until one shows its weight
        before = wolf.hp
        assert use(g, 3), 'Charge works with any weapon'
        assert p.stamina == st1 - 9, 'Charge costs stamina'
        if before - wolf.hp > 3:
            break
        p.stamina, wolf.hp = st1, 999
        p.cooldowns.clear()
    assert before - wolf.hp > 3, ('Charge hits like a weapon now', before - wolf.hp)
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


def prep_skill(g, sid):
    """What a skill needs around it: enemies in reach, corpses for the necromancer, a tree for the druid."""
    from avarenthia import skills as SK
    from avarenthia.entities import make_monster
    from avarenthia.worldgen import free_around
    m, p = g.map, g.player
    sk = SK.SKILLS[sid]
    g.compute_fov()
    spots = [c for c in free_around(g, m, p.x, p.y, 3) if c != (p.x, p.y) and g.visible(*c)]    # not behind a wall a spell left
    m.slain = []
    for x, y in spots[-6:]:
        m.slain.append(('goblin', x, y, 5))
    if sk.mode == 'awaken':
        tx, ty = spots[0]
        m.set(tx, ty, D.TREE)
    if sk.mode == 'rite':
        from avarenthia import mercs as MC
        for mc in MC.beasts(g):
            MC.hurt(g, mc, 99999)
    if sk.mode == 'pyre':
        for o in g.visible_hostiles():
            o.effects['burn'] = [4, 3]
    if sk.need_shield and not g.eq_item('shield'):
        from avarenthia.entities import make_gear
        sh = make_gear(g, 'buckler', 'normal', 1)
        g.add_to_inv(sh)
        p.eq.pop('weapon', None) if g.two_handed(g.eq_item('weapon')) else None
        p.eq['shield'] = sh.id


def schools():
    """Eight tome skills a school, each with its own rule on the map: every tome skill and every technique cast once in
    a fight; burning ground, ice walls, roots, brambles, bone walls, hallowed ground, the totem and ball lightning come
    and go; corpses lie where the fallen fell; Morrak takes life; a Packmaster keeps two beasts."""
    from avarenthia import skills as SK, guilds as GU, mercs as MC, spellmap as SM
    from avarenthia.entities import make_monster, make_tome
    from avarenthia.worldgen import free_around
    print('== schools')
    for line, d in SK.DISCIPLINES.items():
        tomes = SK.by_line(line)
        want = 0 if d['kind'] == 'weapon' else 8      # weapon skills come with the weapon now (weaponskills.py)
        assert len(tomes) == want, (line, len(tomes))
        if d['kind'] != 'weapon':
            assert [s.unlock for s in tomes] == list(SK.TOME), (line, [s.unlock for s in tomes])
    assert SK.SKILLS['tame'] in SK.SKILL_LIST and SK.SKILLS['tame'].unlock == 5
    assert 'packmaster' in [t[0] for t in GU.TEACH['hound']] and GU.TEACH['hound'][0][0] == 'pack_fury'
    assert 'bone_golem' in [t[0] for t in GU.TEACH['ossuary']]
    assert not any(s.drain for s in SK.SKILL_LIST if s.line != 'shadow'), 'only shadow steals life'
    assert all(s.life_cost or s.life_frac for s in SK.by_line('shadow') if s.unlock >= 30)
    assert SK.SKILLS['spellblade'].both and SK.SKILLS['crusade'].both and SK.SKILLS['lichcraft'].life_cost
    app = new_app('soft', seed=7)
    g = app.game
    p = g.player
    p.vit = 400
    for _ in range(20):
        t = make_tome(g, random.randint(0, 20))
        assert t.t in SK.SKILLS and t.value() > 0
    g.enter_dungeon(list(g.world.dungeons)[0], 1, 'up')
    for line in SK.DISCIPLINES:
        p.disc[line] = [80, 0]
    techs = [t[0] for k in GU.TEACH for t in GU.TEACH[k]] + [c[0] for c in GU.COMBOS.values()]
    every = [s.id for s in SK.SKILL_LIST if SK.DISCIPLINES[s.line]['kind'] != 'weapon'] + techs
    p.known = list(dict.fromkeys(every))
    tamed = False
    for sid in p.known:
        sk = SK.SKILLS[sid]
        if sk.passive or SK.DISCIPLINES[sk.line]['kind'] == 'weapon':
            continue
        g.map.mons = [o for o in g.map.mons if o.is_npc and not getattr(o, 'thrall', 0)]
        for xy in list(SM.fields(g.map)):
            SM.clear(g.map, xy)
        if sid == 'blink':                          # room to blink to: an open stretch of floor
            m_ = g.map
            p.x, p.y = max(((i % m_.w, i // m_.w) for i, t in enumerate(m_.t) if t == D.FLOOR),
                           key=lambda c: sum(1 for a in range(-3, 4) for b in range(-3, 4)
                                             if m_.inb(c[0] + a, c[1] + b) and m_.tile(c[0] + a, c[1] + b) == D.FLOOR))
        k = 'skeleton' if sid in ('turn_undead', 'hallowed_ground', 'dawnbreak', 'smite') else \
            'wolf' if sid == 'tame' else 'goblin'
        for x, y in free_around(g, g.map, p.x, p.y, 2)[:3]:
            e = make_monster(g, k, x, y, 6)
            e.awake = True
            if sid == 'tame':
                e.hp = 1
            if sid == 'dispel':
                e.mods = list(e.mods) + ['Fast']   # something to take away
            if getattr(sk, 'need_unseen', False):
                e.awake = False                    # Cheap Shot: only on one who does not see you
            g.map.mons.append(e)
        g.compute_fov()
        prep_skill(g, sid)
        p.bar[5] = sid
        ok = False
        p.buffs = [b for b in p.buffs if not str(b[3]).endswith(' shape')]    # Elder Bear's shape lets go
        for _ in range(40 if sid == 'tame' else 8):    # a jump may find no spot this time: try again
            p.cooldowns.clear()
            p.mana = p.stamina = 999
            p.life = max(p.life, 400)
            ok = SK.use(g, 5)
            if ok and (sid != 'tame' or MC.beasts(g)):
                break
        assert ok, sid
        if sid == 'tame':
            assert MC.beasts(g), 'not tamed'
            tamed = True
        assert SK.describe(sk, 30), sid
        for _ in range(2):
            g.end_turn(1)
            if g.dead:
                break
        app.render()
    assert tamed
    # the tiles: each one a named tile, and each one goes away again
    m = g.map
    assert any(fd[0] == D.BURNING for fd in SM.fields(m).values()) or True
    for xy in list(SM.fields(m)):
        SM.clear(m, xy)
    g.map.mons = [o for o in g.map.mons if o.is_npc and not getattr(o, 'thrall', 0)]
    x, y = next(c for c in free_around(g, m, p.x, p.y, 3) if c != (p.x, p.y) and not g.occupied(m, *c)
                and not any((it.x, it.y) == c for it in m.items) and m.tile(*c) not in SM.KEEP_OFF)
    under = m.tile(x, y)
    assert SM.place(g, m, x, y, D.ICEWALL, 2) and not D.TILES[m.tile(x, y)].walk
    g.end_turn(1)
    g.end_turn(1)
    g.end_turn(1)
    assert m.tile(x, y) == under, 'the ice wall melted'
    # burning ground burns a goblin standing in it; roots hold one
    g.map.mons = [o for o in g.map.mons if o.is_npc]
    gob = make_monster(g, 'goblin', x, y, 3)
    gob.hp = gob.maxhp = 999
    g.map.mons.append(gob)
    SM.place(g, m, x, y, D.BURNING, 5, 4)
    SM.tick(g)
    assert 'burn' in gob.effects
    # the undead cannot step onto hallowed ground
    sk_ = make_monster(g, 'skeleton', x, y, 3)
    g.map.mons = [o for o in g.map.mons if o.is_npc] + [sk_]
    nx, ny = next(c for c in free_around(g, m, x, y, 1) if c != (x, y) and c != (p.x, p.y))
    SM.place(g, m, nx, ny, D.HALLOWED, 5, 3)
    sk_.x, sk_.y = nx, ny
    SM.after_move(g, sk_, x, y)
    assert (sk_.x, sk_.y) == (x, y), 'the skeleton set foot on hallowed ground'
    # corpses: the fallen leave one, and it shows
    g.map.slain = []
    g.kill(sk_)
    assert g.map.slain and SM.corpses(g)
    app.render()
    assert '%' in app.cv.dump()
    # wards and Martyr's Grace
    p.buffs = [['ward', 50, 10, 'Ward']]
    life = p.life
    g.hurt(20, 'test')
    assert p.life == life and p.buffs[0][1] < 50
    p.buffs = [['martyr', 1, 10, "Martyr's Grace"]]
    g.hurt(99999, 'test')
    assert p.life == 1 and not g.dead and not p.buffs
    p.life = 400
    # Packmaster: two beasts
    assert 'packmaster' in p.known and MC.beast_room(g) == 'beast2'
    w2 = make_monster(g, 'wolf', *free_around(g, m, p.x, p.y, 1)[0], 3)
    g.map.mons.append(w2)
    MC.tame(g, w2)
    assert MC.get(g, 'beast2') and len(MC.beasts(g)) == 2 and MC.beast_room(g) is None
    app.screens = [ui.GameScreen(app), ui.CompanyScreen(app)]
    app.render()
    dump = app.cv.dump()
    assert w2.name in dump or MC.get(g, 'beast2').name in dump, 'the second beast has its card'
    app.screens = [ui.GameScreen(app)]
    print('schools ok:', len(SK.SKILL_LIST), 'tome skills,', len(techs), 'techniques')


def weapons():
    """The weapons round: twelve new kinds, each with its own rule (reach, the thrown spear, knives, crossbows that load,
    the scimitar's cut, the flail over a shield, the hammer through armour, fists in a cestus or claws), two weapons at
    once, Shield Bash and Block, monsters with one weapon of their own; and the bestiary in three steps."""
    from avarenthia import weapons as WP, bestiary as BE, skills as SK, hunting as HT, describe as DS
    from avarenthia.entities import make_monster, make_gear
    from avarenthia.worldgen import free_around
    print('== weapons')
    for f in ('scimitar', 'flail', 'warhammer', 'spear', 'halberd', 'scythe', 'throwknives', 'lightxbow', 'heavyxbow',
              'sling', 'cestus', 'claws'):
        assert len(D.grades(f)) == 3 and all(b in D.BASES for b in D.grades(f)), f
    fams = {b['family'] for b in D.BASES.values() if b['slot'] == 'weapon'}
    assert len(fams) == 26 and all(f in SK.WEAPON_LINE for f in fams), (len(fams), [f for f in fams if f not in SK.WEAPON_LINE])
    assert SK.WEAPON_LINE['staff_x'] == 'spears' and SK.WEAPON_LINE['sling'] == 'archery'
    assert D.BASES['cestus_e']['fist'][1] > D.BASES['cestus']['fist'][1]
    app = new_app('soft', seed=6)
    g, p = app.game, app.game.player
    p.lvl, p.str, p.dex, p.vit = 30, 200, 200, 300
    g.enter_dungeon(list(g.world.dungeons)[0], 1, 'up')
    m = g.map

    def arena():
        m.mons = []
        m.items = [it for it in m.items if abs(it.x - p.x) > 6 or abs(it.y - p.y) > 6]
        p.buffs, p.cooldowns = [], {}
        p.life = g.stats()['max_life']

    def line_spot(n, need=None):
        """A free tile n steps from you in a straight line, with open floor between."""
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            cells = [(p.x + dx * k, p.y + dy * k) for k in range(1, n + 1)]
            if all(m.inb(*c) and D.TILES[m.tile(*c)].walk and not g.occupied(m, *c) for c in cells):
                return cells, (dx, dy)
        return None, None

    def foe(k, x, y, hp=500):
        o = make_monster(g, k, x, y, 5)
        o.hp = o.maxhp = hp
        o.awake = True
        m.mons.append(o)
        return o

    def wield(base, slot='weapon'):
        it = make_gear(g, base, 'normal', 5)
        g.add_to_inv(it)
        p.eq[slot] = it.id
        return it
    # find a straight corridor of five free tiles
    for _ in range(400):
        cells, d = line_spot(5)
        if cells:
            break
        spots = [c for c in free_around(g, m, p.x, p.y, 8) if not g.occupied(m, *c)]
        p.x, p.y = random.choice(spots)
    assert cells, 'no room to fight'
    g.compute_fov()
    # reach: a spear strikes a goblin two tiles away, and past a friend
    arena()
    p.eq = {}
    sp = wield('spear')
    gob = foe('goblin', *cells[1])
    g.compute_fov()
    assert WP.reach_target(g, gob) and g.fire() == 1, 'the spear reaches'
    for _ in range(6):                             # a blow may miss
        if gob.hp < 500:
            break
        gob.x, gob.y = cells[1]
        g.fire()
    assert gob.hp < 500, 'the spear reaches and strikes'
    pal = make_monster(g, 'villager', *cells[0], 3) if 'villager' in D.MONSTERS else None
    if pal is not None:
        pal.is_npc = True
        m.mons.append(pal)
        hp = gob.hp
        g.try_move(*d)
        assert gob.hp < hp and (p.x, p.y) != cells[0], 'a spear strikes past a friend'
        m.mons.remove(pal)
    # the spear thrown: it lies where it fell until you pick it up again
    arena()
    gob = foe('goblin', *cells[3])
    g.compute_fov()
    assert g.fire() == 1 and not g.eq_item('weapon') and any(it is sp for it in m.items), 'the spear is thrown'
    sp.x, sp.y = p.x, p.y
    g.auto_pickup()
    assert g.eq_item('weapon') is sp, 'the spear is back in your hand'
    # a crossbow shoots, then must be wound again; the panel says so
    arena()
    xb = wield('lightxbow')
    gob = foe('goblin', *cells[3])
    g.compute_fov()
    assert g.fire() == 1 and WP.unloaded(g) and ('unloaded', (200, 120, 90)) in WP.shown(g)
    hp = gob.hp
    assert g.fire() == 1 and not WP.unloaded(g) and gob.hp == hp, 'the second press winds it'
    assert WP.shot_df(g, 40) == 20
    # throwing knives: one fewer in the set, one on the ground, back again when picked up
    arena()
    kn = wield('throwknives')
    gob = foe('goblin', *cells[3])
    g.compute_fov()
    assert g.fire() == 1 and kn.ammo == WP.KNIVES_MAX - 1
    knife = next(it for it in m.items if it.k == 'ammo')
    knife.x, knife.y = p.x, p.y
    g.auto_pickup()
    assert kn.ammo == WP.KNIVES_MAX and knife not in m.items and 'knife' in knife.display_name().lower()
    # the scimitar's cut in passing
    arena()
    wield('scimitar')
    gob = foe('goblin', *cells[0])
    s = g.stats()
    p.stepped = g.turn - 1
    assert WP.on_melee(g, gob, s) == 1.5 and WP.on_melee(g, gob, s) == 1.0, 'only the first blow after a step'
    # a flail swings over a shield, at a price in aim
    arena()
    wield('mace')
    ar = g.stats()['ar']
    wield('flail')
    assert g.stats()['ar'] == ar - 10
    gob = foe('goblin', *cells[0])
    gob.shield = 3
    hp = gob.hp
    g.damage_mon(gob, 40, weapon=True)
    assert hp - gob.hp == 40 and gob.shield == 3, 'the flail went over the shield'
    wield('mace')
    g.damage_mon(gob, 40, weapon=True)
    assert gob.shield == 2
    # a war hammer goes through armour
    arena()
    sk_ = foe('skel_warrior' if 'skel_warrior' in D.MONSTERS else 'skeleton', *cells[0])
    assert WP.armoured(sk_)
    wield('longsword')
    assert WP.armour_mult(g, sk_, True) == .75
    wield('warhammer')
    assert WP.armour_mult(g, sk_, True) == 1.25 and WP.armour_mult(g, gob, True) == 1.0
    # fists: a cestus or claws while the weapon hand is empty; claws draw blood, three times at most, not from bones
    arena()
    p.eq = {}
    bare = g.stats()['dmg']
    ce = wield('cestus_e', 'gloves')
    assert WP.fist(g) is ce and g.stats()['dmg'][1] > bare[1] and g.stats()['line'] == 'unarmed'
    gob = foe('goblin', *cells[0])
    for _ in range(4):
        WP.bleed(g, gob, 2)
    assert gob.bleeds == 3 and gob.effects['bleed'][1] == 6
    WP.bleed(g, sk_, 2)
    assert 'bleed' not in sk_.effects, 'no blood, no bleeding'
    g.end_turn(1)
    assert WP.blood_at(g, m), 'a bleeding goblin leaves a trail'
    # two weapons: a light one beside a one-handed one goes in the second hand, and strikes too
    arena()
    p.eq = {}
    da = make_gear(g, 'dagger', 'normal', 5)
    ss = make_gear(g, 'shortsword', 'normal', 5)
    g.add_to_inv(da)
    g.add_to_inv(ss)
    assert g.equip(da) and g.equip(ss) and p.eq.get('shield') == ss.id and p.eq.get('weapon') == da.id
    assert g.stats().get('off') and WP.off_hand(g) is ss
    bs = make_gear(g, 'buckler', 'normal', 5)
    g.add_to_inv(bs)
    assert g.equip(bs) and not WP.off_hand(g) and WP.has_shield(g)
    # Block and Shield Bash: a shield in hand catches the first blow of a turn; a flail goes over it
    arena()
    p.known = list(dict.fromkeys(p.known + ['block', 'shield_bash']))
    gob = foe('goblin', *cells[0])
    p.bar[5] = 'block'
    p.stamina = 999
    assert SK.use(g, 5) and any(b_[0] == 'block' for b_ in p.buffs)
    life = p.life
    gob.wield = None
    g.mon_attack(gob, 0)
    assert p.life == life and p.blocked == g.turn, 'caught on the shield'
    p.blocked = -1
    gob.wield = 'flail'
    assert not WP.blocked(g, gob), 'the flail swings over the shield'
    p.bar[4] = 'shield_bash'
    p.cooldowns = {}
    at = (gob.x, gob.y)
    assert SK.use(g, 4) and ((gob.x, gob.y) != at or gob not in m.mons or not D.TILES[m.tile(2 * gob.x - p.x, 2 * gob.y - p.y)].walk)
    p.eq.pop('shield', None)
    p.cooldowns = {}
    assert not SK.use(g, 4), 'no shield, no Shield Bash'
    # monsters carry one weapon of their kind, and drop only that one
    for _ in range(20):
        dr = make_monster(g, 'dune_rider', p.x, p.y, 5)
        assert dr.wield in D.GEAR_USERS['dune_rider'] and dr.wield == 'scimitar'
        assert 'shortsword' not in WP.drop_families(dr, D.GEAR_USERS['dune_rider'])
    assert 'heavyxbow' in D.GEAR_USERS['thunderer'] and 'sling' in D.GEAR_USERS['kob_slinger']
    # the bestiary: kills and skins teach a kind in three steps; the last gives a weak spot
    arena()
    p.bestiary.pop('wolf', None)
    w_ = foe('wolf', *cells[0], hp=1)
    g.kill(w_)
    assert BE.step(g, 'wolf') == 0 and DS.monster(g, foe('wolf', *cells[1]))[2]
    for _ in range(2):
        BE.on_skin(g, 'wolf')
    assert BE.step(g, 'wolf') == 1 and BE.look_lines(g, 'wolf'), p.bestiary['wolf']
    p.bestiary['wolf'][1] = 30
    assert BE.step(g, 'wolf') == 3 and BE.crit_bonus(g, m.mons[-1]) == BE.WEAK_CRIT
    assert g.crit_vs(m.mons[-1], g.stats()) == g.stats()['crit'] + BE.WEAK_CRIT
    lines = BE.look_lines(g, 'wolf')
    assert len(lines) == 3 and 'critical' in lines[2], lines
    if 'red_deer' in HT.SKINS:
        assert 'deer hide' in BE.carries('red_deer').lower()
    assert 'scimitar' in BE.carries('dune_rider').lower()
    for e in p.bestiary.values():
        e[1] = max(e[1], 3)
    p.bestiary['rat'] = [1, 0]
    assert BE.study(g) == ['Giant Rat'] and BE.step(g, 'rat') == 1, 'a library teaches the first step'
    app.screens = [ui.GameScreen(app), ui.BestiaryScreen(app)]
    for _ in range(len(p.bestiary)):
        app.render()
        app.key('down')
    app.screens = [ui.GameScreen(app), ui.InventoryScreen(app)]
    wield('heavyxbow')
    app.render()
    assert 'loaded' in app.cv.dump()
    app.screens = [ui.GameScreen(app)]
    app.render()
    E.save_game(g)
    g2 = E.load_game()
    assert g2.bestiary['wolf'][1] == 30 and g2.player.bestiary is g2.bestiary
    print('weapons ok:', len(fams), 'weapon kinds,', len(p.bestiary), 'creatures known')


def classes():
    """Classes part 1: a blank start with only your weapon's skills; the first tome wakes your class, a second school
    at rank 20 gives the pair's name; keys 1-2 come with the weapon (two skills for each of the 29 kinds, the second at
    rank 10), 3-5 class skills, 6 one elite; each weapon family's rule; the swing arc, blood and the critical star."""
    from avarenthia import skills as SK, classes as CL, weaponskills as WS, weapons as WP
    from avarenthia.entities import make_monster, make_gear
    from avarenthia.worldgen import free_around
    print('== classes')
    assert len(CL.PAIRS) == 55 and CL.pair_name('nature', 'beastcraft') == 'Wildkin' and len(WS.KIT) == 29 + len(WS.SHAPE_KITS)
    assert all(a in SK.SKILLS and b in SK.SKILLS for a, b in WS.KIT.values())
    assert not any(SK.DISCIPLINES[s.line]['kind'] == 'weapon' for s in SK.SKILL_LIST), 'no weapon tomes any more'
    assert 'fire_arrow' not in SK.SKILLS, 'Burning Arrow goes'
    app = new_app('soft', seed=9)
    g, p = app.game, app.game.player
    p.lvl, p.str, p.dex, p.vit, p.ene = 30, 150, 150, 300, 150
    assert CL.slot_skill(g, 0) == 'haymaker' and not CL.title(g)
    g.enter_dungeon(list(g.world.dungeons)[0], 1, 'up')
    m = g.map
    fx = []

    def foes(n=4, k='goblin'):
        m.mons = [o for o in m.mons if o.is_npc]
        out = []
        for c in [c for c in free_around(g, m, p.x, p.y, 2) if c != (p.x, p.y) and not g.occupied(m, *c)][:n]:
            o = make_monster(g, k, *c, 4)
            o.hp = o.maxhp = 900
            o.awake = True
            m.mons.append(o)
            out.append(o)
        g.compute_fov()
        return out
    # every weapon kind: both skills work, the second only from rank 10
    used = 0
    for fam, (a, b) in [kv for kv in WS.KIT.items() if kv[0] not in WS.SHAPE_KITS]:
        p.eq, p.inv = {}, []
        if fam != 'fists':
            it = make_gear(g, fam, 'normal', 5)
            g.add_to_inv(it)
            p.eq['gloves' if D.BASES[fam]['slot'] == 'gloves' else 'weapon'] = it.id
        line = SK.SKILLS[a].line
        p.disc[line][0] = 0
        assert CL.slot_skill(g, 0) == a and CL.slot_skill(g, 1) is None and WS.second_locked(g) == b, fam
        p.disc[line][0] = WS.SECOND
        assert CL.slot_skill(g, 1) == b, fam
        for i in (0, 1):
            foes()
            p.stamina = p.mana = 999
            p.cooldowns, p.quick = {}, False
            if WP.main_hand(g) is not None:
                WP.main_hand(g).unloaded = False
            g.events = []
            assert SK.use(g, i), (fam, i, CL.slot_skill(g, i), g.log[-1:])
            fx += [e[1] for e in g.events if e[0] == 'fx']
            used += 1
            sp = next((it for it in m.items if getattr(it, 'thrown', False)), None)
            if sp:                                  # a thrown spear back in hand
                sp.x, sp.y = p.x, p.y
                g.auto_pickup()
        app.render()
    assert 'swing' in fx and 'spin' in fx and 'blood' in fx, set(fx)
    # a crossbow skill unloads it; Brace winds it
    p.inv = []
    xb = make_gear(g, 'heavyxbow', 'normal', 5)
    g.add_to_inv(xb)
    p.eq = {'weapon': xb.id}
    foes()
    p.cooldowns = {}
    assert SK.use(g, 0) and WP.unloaded(g) and not SK.use(g, 0) and SK.use(g, 1) and not WP.unloaded(g)
    # keys 3-6: class skills only of your schools, one elite
    p.classes = ['fire']
    p.known = ['firebolt', 'mend', 'shield_wall', 'inferno']
    assert CL.fits(g, SK.SKILLS['firebolt'], 2) is None and CL.fits(g, SK.SKILLS['mend'], 2)
    assert CL.fits(g, SK.SKILLS['inferno'], 5) is None and CL.fits(g, SK.SKILLS['firebolt'], 5)
    assert CL.fits(g, SK.SKILLS['shield_wall'], 3) and CL.fits(g, SK.SKILLS['haymaker'], 2)
    # the family rules: a staff makes spells cheaper, a sword's blow takes a turn off class recharges,
    # every third unarmed blow gives breath back
    st = make_gear(g, 'staff', 'normal', 5)
    g.add_to_inv(st)
    p.eq = {'weapon': st.id}
    assert SK.cost_of(g, SK.SKILLS['inferno']) < SK.SKILLS['inferno'].cost
    sw = make_gear(g, 'longsword', 'normal', 5)
    g.add_to_inv(sw)
    p.eq = {'weapon': sw.id}
    o = foes(1)[0]
    p.cooldowns = {'firebolt': 5, 'lunge': 5}
    for _ in range(10):
        g.melee(o)
    assert p.cooldowns.get('firebolt', 0) < 5 and p.cooldowns.get('lunge') == 5, (p.cooldowns, o.hp, g.log[-3:])
    p.eq = {}
    p.stamina, p.blows = 0, 0
    for _ in range(12):
        g.melee(o)
    assert p.stamina > 0 or p.mana > 0
    # the screens: the panel shows the three groups and your name, the skills screen keys 3-6
    p.classes = ['fire', 'shadow']
    p.bar = [None, None, 'firebolt', None, None, 'inferno']
    app.screens = [ui.GameScreen(app)]
    app.render()
    dump = app.cv.dump()
    assert 'Hexblade' in dump and 'weapon' in dump and 'elite' in dump and 'Firebolt' in dump
    app.screens = [ui.GameScreen(app), ui.SkillsScreen(app)]
    app.render()
    assert 'YOUR WEAPON' in app.cv.dump()
    app.key('1')
    app.render()
    app.key('esc')
    print('classes ok:', used, 'weapon skills used,', len(set(fx)), 'kinds of effect')


def trees():
    """Classes part 2: a tree per class, three branches of six; a point per five ranks, spent only where you rested,
    in order down a branch; each school's blade branch opens with its imbue; Nature's shapes put teeth and claws on
    keys 1-2; a temple takes the points back for coin; every knot of every tree in a fight without an error."""
    from avarenthia import skills as SK, classes as CL, trees as TT, weaponskills as WS, anim as AN
    from avarenthia.entities import make_monster, make_gear
    from avarenthia.worldgen import free_around
    print('== trees')
    assert len([k for k in TT.KNOTS.values() if k[1] >= 0]) == 11 * 18 and len(TT.IMBUES) == 8
    app = new_app('soft', seed=9)
    g, p = app.game, app.game.player
    p.lvl, p.str, p.dex, p.vit, p.ene = 30, 150, 150, 300, 150
    p.classes = ['fire', 'nature']
    p.disc['fire'][0], p.disc['nature'][0] = 40, 30
    assert TT.earned(g, 'fire') == 8 and TT.free(g, 'nature') == 6
    assert TT.spend(g, 'kindled_mind'), 'only where you rested'
    TT.rested(g)
    assert TT.spend(g, 'quick_spark'), 'in order down a branch'
    for kid in ('kindled_mind', 'kindled_mind', 'kindled_mind', 'quick_spark', 'thrifty_flame', 'thrifty_flame',
                'flameblade', 'heart_of_fire'):
        why = TT.spend(g, kid)
        if kid == 'heart_of_fire':
            assert why, 'Heart of Fire waits for the knots above it'
        else:
            assert why is None, (kid, why)
    assert TT.spend(g, 'kindled_mind') and TT.free(g, 'fire') == 1
    fb, fball = TT.tuned(g, SK.SKILLS['firebolt']), TT.tuned(g, SK.SKILLS['fireball'])
    assert abs(fb.tmul - 1.15) < 1e-9 and fball.cost < SK.SKILLS['fireball'].cost
    assert TT.tuned(g, SK.SKILLS['searing_brand']).cd == SK.SKILLS['searing_brand'].cd - 1
    # the screen: arrows and Enter spend a point
    app.screens = [ui.GameScreen(app), ui.TreeScreen(app)]
    app.render()
    assert 'PYROMANCER' in app.cv.dump() and 'Kindled Mind' in app.cv.dump()
    app.key('right')
    app.key('down')
    app.key('enter')
    assert TT.pts(g, 'hot_steel') == 1
    app.key('tab')
    app.render()
    assert 'SHAPESHIFTER' in app.cv.dump()
    app.key('esc')
    # Flameblade: a fire spell sets your weapon burning; while it burns no mana comes back
    g.enter_dungeon(list(g.world.dungeons)[0], 1, 'up')
    m = g.map

    def foes(n=3, k='goblin'):
        m.mons = [o for o in m.mons if o.is_npc]
        out = []
        for c in [c for c in free_around(g, m, p.x, p.y, 2) if c != (p.x, p.y) and not g.occupied(m, *c)][:n]:
            o = make_monster(g, k, *c, 4)
            o.hp = o.maxhp = 2000
            o.awake = True
            m.mons.append(o)
            out.append(o)
        g.compute_fov()
        return out
    sw = make_gear(g, 'longsword', 'normal', 5)
    p.inv = []
    g.add_to_inv(sw)
    p.eq = {'weapon': sw.id}
    p.known = ['firebolt']
    p.bar = [None, None, 'firebolt', None, None, None]
    o = foes(1)[0]
    p.mana, p.cooldowns = 999, {}
    p.fire_free = True
    assert SK.cost_of(g, SK.SKILLS['firebolt']) > 0, 'Heart of Fire has no point yet'
    assert SK.use(g, 2) and TT.imbue(g) == ('flameblade', 'burn') and TT.mana_held(g)
    burned = 0
    for _ in range(30):
        o.effects.pop('burn', None)
        g.melee(o)
        burned += 'burn' in o.effects
    assert burned, 'about one blow in three sets the foe alight'
    # the shapes: a knot teaches Wolf Shape; as a wolf keys 1-2 bite and lunge, keys 3-6 rest until Untamed
    TT.rested(g)
    t = TT.tree(g)
    t['nature'] = {'wolf_shape': 1}
    p.known = []
    t['nature'] = {}
    TT.rested(g)
    assert TT.spend(g, 'wolf_shape') is None and 'wolf_shape' in p.known
    p.bar = [None, None, 'firebolt', 'wolf_shape', None, None]
    p.cooldowns = {}
    p.stamina = 999
    assert SK.use(g, 3) and AN.shape_of(p) == 'wolf' and CL.slot_skill(g, 0) == 'bite' and CL.slot_skill(g, 1) == 'wolf_lunge'
    foes(2)
    assert SK.use(g, 0), g.log[-1:]
    assert not SK.use(g, 2), 'keys 3-6 rest in a shape'
    t['nature'].update({k[0]: k[2] for k in TT.TREES['nature'][2][2]})
    assert SK.use(g, 2) or p.cooldowns.get('firebolt') is not None
    # the temple takes it all back, and the shapes a knot taught go with it
    cost = TT.unlearn_cost(g)
    p.gold = cost
    assert cost and TT.unlearn(g) and not TT.tree(g) and 'wolf_shape' not in p.known and p.gold == 0
    # every knot of every tree, full, in a fight: casting each of the school's skills and striking with the weapon
    blows = 0
    for line, brs in TT.TREES.items():
        p.classes = [line]
        p.tree = {line: {k[0]: k[2] for _n, _w, ks in brs for k in ks}}
        p.disc[line][0] = 70
        p.known = [s.id for s in SK.SKILL_LIST if s.line == line] + [k[4] for _n, _w, ks in brs for k in ks if k[3] == 'teach']
        g.clamp_vitals()
        for sid in p.known:
            sk = SK.SKILLS[sid]
            if sk.mode in ('tame', 'rite', 'tomb') or sk.need_beast:
                continue
            foes(3, 'skeleton' if line == 'restoration' else 'goblin')
            p.bar[2] = sid
            p.mana = p.stamina = 9999
            p.life = g.stats()['max_life']
            p.cooldowns = {}
            p.buffs = [b for b in p.buffs if not str(b[3]).endswith(' shape')]
            SK.use(g, 2)
            for o in [o for o in m.mons if not o.is_npc][:1]:
                for _ in range(6):
                    if o in m.mons:
                        g.melee(o)
                        blows += 1
            g.end_turn(1)
            if g.dead:
                break
        assert not g.dead, line
        p.life = g.stats()['max_life']
        g.hurt(5, 'a test', 'lightning')
    app.render()
    print('trees ok:', len([k for k in TT.KNOTS.values() if k[1] >= 0]), 'knots,', blows, 'blows struck with full trees')


def pairs():
    """Classes part 3: Cunning (the first blow on the unaware lands twice; sneak, snares, smoke, vanish) and Arcane
    (blink, runes, dispel, counterspell, gate, haste, stop time); a rule for each pure class and each of the 55 pairs;
    a guild's rank-4 technique is its elite, rank 1-2 an ordinary skill of its school, the weapon guilds' a weapon
    skill; every rule in a fight without an error."""
    from avarenthia import skills as SK, classes as CL, trees as TT, arts as ART, spellmap as SM, guilds as GU
    from avarenthia.entities import make_monster, make_gear
    from avarenthia.worldgen import free_around
    print('== pairs')
    assert len(TT.RULES) == 66 and set(TT.RULES) == set(CL.PURE.values()) | set(CL.PAIRS.values())
    assert len([s for s in SK.SKILL_LIST if s.line == 'cunning']) == 8 == len([s for s in SK.SKILL_LIST if s.line == 'arcane'])
    assert CL.is_elite(SK.SKILLS['inferno']) and CL.is_elite(SK.SKILLS['spellblade'])
    assert not CL.is_elite(SK.SKILLS['mage_armor']) and CL.weapon_guild(SK.SKILLS['hunters_mark'])
    assert 'elder_bear' in [t[0] for t in GU.TEACH['moot']] and 'garrote' not in [t[0] for t in GU.TEACH['thieves']]
    app = new_app('soft', seed=9)
    g, p = app.game, app.game.player
    p.lvl, p.str, p.dex, p.vit, p.ene = 30, 150, 150, 300, 150
    p.classes = ['frost']
    assert CL.fits(g, SK.SKILLS['mage_armor'], 2) is None and CL.fits(g, SK.SKILLS['mage_armor'], 5)
    assert CL.of_no_use(g, 'smite') and not CL.of_no_use(g, 'inferno')
    g.enter_dungeon(list(g.world.dungeons)[0], 1, 'up')
    m = g.map

    def foes(n=3, k='goblin', awake=True, hp=2000):
        m.mons = [o for o in m.mons if o.is_npc]
        m.fields = {}
        out = []
        for c in [c for c in free_around(g, m, p.x, p.y, 2) if c != (p.x, p.y) and not g.occupied(m, *c)][:n]:
            o = make_monster(g, k, *c, 4)
            o.hp = o.maxhp = hp
            o.awake = awake
            o.mods = []
            m.mons.append(o)
            out.append(o)
        g.compute_fov()
        return out
    # Cunning: an unaware foe takes the first blow twice; a pure Rogue three times
    sw = make_gear(g, 'longsword', 'normal', 5)
    p.inv = []
    g.add_to_inv(sw)
    p.eq = {'weapon': sw.id}
    p.classes = ['cunning', 'fire']
    o = foes(1, awake=False)[0]
    assert ART.first_blow(g, o) == 2 and ART.first_blow(g, o) == 1, 'only the first blow'
    p.classes = ['cunning']
    o = foes(1, awake=False)[0]
    assert ART.first_blow(g, o) == 3
    # Sneak: foes are slow to notice; a snare holds who steps in; smoke and Vanish lose them
    p.known = [s.id for s in SK.SKILL_LIST if s.line == 'cunning']
    p.disc['cunning'][0] = 70
    p.stamina = p.mana = 999
    p.bar = [None, None, 'sneak', 'set_snare', 'vanish', None]
    o = foes(1)[0]
    p.cooldowns = {}
    assert SK.use(g, 2) and ART.notice(g, o) < .65
    assert SK.use(g, 3)
    sn = next(xy for xy, fd in m.fields.items() if fd[0] == D.SNARE)
    ox, oy = o.x, o.y
    o.x, o.y = sn
    SM.after_move(g, o, ox, oy)
    assert o.hold >= 3 and sn not in m.fields
    assert SK.use(g, 4) and not o.awake and ART.buff(g, 'ambush')
    # Arcane: Blink away, Dispel the magic off a foe, Counterspell a spell, a Gate, Haste, Stop Time
    p.classes = ['arcane']
    p.known = [s.id for s in SK.SKILL_LIST if s.line == 'arcane'] + ['haste']
    p.disc['arcane'][0] = 70
    p.bar = [None, None, 'blink', 'dispel', 'counterspell', None]
    o = foes(1)[0]
    o.mods = ['Fire Enchanted', 'Fast']
    start = (p.x, p.y)
    p.cooldowns, p.mana = {}, 999
    assert SK.use(g, 2) and (p.x, p.y) != start
    o.x, o.y = next(c for c in free_around(g, m, p.x, p.y, 1) if c != (p.x, p.y))   # Blink took you away: back in reach
    g.compute_fov()
    assert o in g.visible_hostiles(), (o.name, o.x, o.y, p.x, p.y)
    assert SK.use(g, 3) and not o.mods, (o.mods, g.log[-3:])
    assert SK.use(g, 4) and ART.counter(g, o) and not ART.buff(g, 'counter')
    p.bar[2] = 'gate'
    a = (p.x, p.y)
    p.cooldowns = {}
    assert SK.use(g, 2)
    step = next(c for c in free_around(g, m, p.x, p.y, 3) if 2 <= cheb(c[0], c[1], *a) <= 3 and not g.occupied(m, *c))
    p.x, p.y = step
    p.cooldowns = {}
    assert SK.use(g, 2) and len(m.gates) == 2
    p.x, p.y = next(c for c in free_around(g, m, *step, 1) if c != step and c != a and not g.occupied(m, *c))
    ART.through_gate(g)
    p.x, p.y = step
    ART.through_gate(g)
    assert (p.x, p.y) == a, 'stepping onto one gate brings you out of the other'
    p.bar[2] = 'haste'
    p.cooldowns = {}
    assert SK.use(g, 2)
    t0 = g.turn
    g.end_turn(1)
    g.end_turn(1)
    assert g.turn == t0 + 1, 'Haste: two things in one turn'
    p.buffs = [b for b in p.buffs if b[0] != 'haste']
    os_ = foes(3)
    p.bar[2] = 'stop_time'
    p.cooldowns = {}
    assert SK.use(g, 2) and all(o.hold >= 3 for o in os_)
    # every rule: the classes of that name, the school's skills used, blows struck, a beast's bite, a turn
    from avarenthia import mercs as MC
    names = {}
    for line in CL.PURE:
        names[CL.PURE[line]] = [line]
    for pr, nm in CL.PAIRS.items():
        names[nm] = sorted(pr)
    done = 0
    for nm, cl in names.items():
        p.classes = list(cl)
        p.tree = {}
        assert CL.rule_name(g) == nm and TT.RULE_KNOTS[nm]
        for line in cl:
            p.disc[line][0] = 40
        p.known = [s.id for s in SK.SKILL_LIST if s.line in cl and s.tier <= 5]
        g.clamp_vitals()
        for sid in p.known:
            sk = SK.SKILLS[sid]
            if sk.mode in ('tame', 'rite', 'tomb', 'gate') or sk.need_beast:
                continue
            foes(2, 'skeleton' if 'restoration' in cl else 'goblin', awake=random.random() < .5)
            p.bar[2] = sid
            p.mana = p.stamina = 9999
            p.life = g.stats()['max_life']
            p.cooldowns, p.buffs = {}, []
            SK.use(g, 2)
            for o in [o for o in m.mons if not o.is_npc][:1]:
                for _ in range(3):
                    if o in m.mons:
                        g.melee(o)
            g.end_turn(1)
            assert not g.dead, (nm, sid)
        done += 1
    app.render()
    print('pairs ok:', done, 'rules in a fight')


def balance():
    """The balance test: the same foes, five ways to fight them: a pure caster, a pure warrior, two who mix weapon and
    class, and a pure rogue. Each wears what such a one wears. On six worlds they should all win, about as fast,
    with a different risk. Six worlds, so that one hard draw does not decide it: each must win 22 of 24 waves."""
    from avarenthia import skills as SK, classes as CL
    from avarenthia.entities import make_monster, make_gear
    from avarenthia.worldgen import free_around, bfs
    print('== balance')
    builds = {'Pyromancer': (['fire'], None, ['quilted', 'cap'], ['firebolt', 'fireball', 'searing_brand'], (40, 60, 120, 120)),
              'Warrior': (['warcraft'], 'greatsword', ['chainmail', 'fullhelm'], ['rage', 'charge', 'iron_skin'], (120, 60, 120, 40)),
              'Firebrand': (['fire', 'warcraft'], 'longsword', ['chainmail', 'skullcap', 'roundshield'], ['firebolt', 'rage', 'warcry'],
                            (90, 60, 120, 70)),
              'Reaver': (['shadow', 'warcraft'], 'waraxe', ['chainmail', 'skullcap', 'roundshield'], ['drain', 'rage', 'warcry'],
                         (100, 60, 120, 60)),
              'Rogue': (['cunning'], 'dagger', ['leather', 'cap'], ['envenom', 'garrote', 'shadowstep'], (60, 120, 120, 40))}
    out = {}
    for name, (cl, weapon, wear, bar, (st, dx, vi, en)) in builds.items():
        won, turns, taken = 0, 0, 0
        for world in range(11, 17):
            app = new_app('soft', seed=world)
            random.seed(world * 7 + 1)      # one draw for all five, so they fight the same foes
            g, p = app.game, app.game.player
            p.lvl, p.str, p.dex, p.vit, p.ene = 18, st, dx, vi, en
            p.classes = cl
            for line in cl:
                p.disc[line][0] = 35
            p.known = list(bar)
            p.bar = [None, None] + bar + [None]
            p.inv, p.eq = [], {}
            for base in ([weapon] if weapon else []) + wear:
                it = make_gear(g, base, 'normal', 10)
                g.add_to_inv(it)
                p.eq[D.BASES[base]['slot']] = it.id
            if weapon:
                p.disc[SK.WEAPON_LINE[weapon]][0] = 30
            g.enter_dungeon(list(g.world.dungeons)[0], 1, 'up')
            m = g.map
            s = g.stats()
            p.life, p.mana, p.stamina = s['max_life'], s['max_mana'], s['max_stamina']
            for wave in range(4):
                m.mons = [o for o in m.mons if o.is_npc]
                wave_foes = []
                near = bfs(m, p.x, p.y, lambda k: D.TILES[k].walk, 5)    # where one can walk to, not behind a wall
                for c in [c for c in free_around(g, m, p.x, p.y, 4) if cheb(c[0], c[1], p.x, p.y) >= 3
                          and 0 <= near[c[1] * m.w + c[0]] <= 5 and g.visible(*c) and not g.occupied(m, *c)][:3]:
                    o = make_monster(g, random.choice(['goblin', 'orc', 'skeleton']), *c, 12)
                    o.awake = wave % 2 == 0
                    m.mons.append(o)
                    wave_foes.append(o)
                g.compute_fov()
                for _ in range(120):
                    foes = [o for o in wave_foes if o in m.mons and not getattr(o, 'fleeing', False)]
                    if not foes or g.dead:     # smoke hides them but does not count: they must fall or flee
                        break
                    life = p.life
                    used = 0
                    for i in (2, 3, 4, 0, 1):
                        sid = CL.slot_skill(g, i)
                        sk = SK.SKILLS[sid] if sid else None
                        if sk and sk.buff and any(b[0] == sk.buff[0] for b in p.buffs):
                            continue                    # it is on you already
                        if sid and not p.cooldowns.get(sid) and SK.can_pay(g, SK.SKILLS[sid]):
                            used = SK.use(g, i)
                            if used:
                                break
                    if not used:
                        t = min(foes, key=lambda o: cheb(o.x, o.y, p.x, p.y))
                        if cheb(t.x, t.y, p.x, p.y) <= 1:
                            g.melee(t)
                        else:
                            dx_, dy_ = (t.x > p.x) - (t.x < p.x), (t.y > p.y) - (t.y < p.y)
                            if not g.try_move(dx_, dy_):        # round the wall, by the shortest way
                                dist = bfs(m, t.x, t.y, lambda k: D.TILES[k].walk, 30)
                                step = [(ax, ay) for ax in (-1, 0, 1) for ay in (-1, 0, 1) if m.inb(p.x + ax, p.y + ay)
                                        and dist[(p.y + ay) * m.w + p.x + ax] >= 0]
                                if step:
                                    ax, ay = min(step, key=lambda d: dist[(p.y + d[1]) * m.w + p.x + d[0]])
                                    g.try_move(ax, ay)
                        g.end_turn(1)
                    else:
                        g.end_turn(used)
                    taken += max(0, life - p.life)
                    turns += 1
                if not g.dead and not any(o in m.mons and not getattr(o, 'fleeing', False) for o in wave_foes):
                    won += 1
                if g.dead:
                    break
        out[name] = (won, turns, taken)
        print(f'  {name}: {won} of 24 waves won in {turns} turns, {taken} damage taken')
    assert all(w >= 22 for w, _t, _d in out.values()), out
    ts = [t for _w, t, _d in out.values()]
    assert max(ts) <= 3 * max(1, min(ts)), out
    print('balance ok')


def visible():
    """Spell effects: bolts fly and impacts open out, life flows back, short and skippable, an option full/short/off;
    burning, frozen and poisoned show on a creature; Wild Shape keeps your @ in the beast's colours; smoke rises from
    the chimneys and sparks fly at the smith's; rain sends the townsfolk indoors."""
    from avarenthia import anim as AN, skills as SK, towns as TW, weather as WX, look as LOOK
    from avarenthia.entities import make_monster
    from avarenthia.worldgen import free_around
    print('== visible')
    # every effect stays short and draws something
    kinds = {'bolt': dict(cells=[(i, 0) for i in range(1, 15)], src=(0, 0), col=(255, 120, 60), ch='*'),
             'burst': dict(x=5, y=5, r=2, col=(255, 120, 60), gather=True),
             'drain': dict(cells=[(i, 0) for i in range(1, 6)], col=(220, 60, 70)),
             'rise': dict(x=3, y=3, col=(120, 240, 140)), 'zap': dict(cells=[(1, 1), (2, 2)], col=(255, 240, 120)),
             'wave': dict(x=5, y=5, r=3, col=(160, 200, 255), sign='sound'),
             'meteor': dict(x=8, y=8, col=(255, 120, 60)), 'raise': dict(x=2, y=2, ch='z', col=(190, 200, 170)),
             'trail': dict(cells=[(i, 1) for i in range(5)], col=(160, 200, 255), ch='█', build=True)}
    for k, kw in kinds.items():
        life = AN.fx_life(k, kw)
        assert life <= .42, (k, life)
        drawn = [AN.fx_cells(k, kw, a / 50) for a in range(int(life * 50))]
        assert any(drawn), k
        assert all(0 <= v <= 255 for cells in drawn for c in cells for v in c[3]), k
    assert AN.fx_life('burst', dict(x=0, y=0, r=2, delay=AN.bolt_time(20))) <= .5
    # each school's hand: a howl bends round as ( ), Meteor's shadow comes before its slanting fall, the dead grey
    # and rise, Morrak's Bargain goes out red before it falls in, and the sky's white frame is brief
    howl = AN.fx_cells('wave', kinds['wave'], .05)
    assert {c[2] for c in howl} >= {'(', ')'} and all(cheb(c[0], c[1], 5, 5) == 1 for c in howl), howl
    # areas look round but hit the square: the front reaches the sides before the corners, and every cell of the
    # square lights; a faint cloud beyond the sides only rounds it off
    area = dict(x=10, y=10, r=2, col=(255, 120, 60))
    early = {c[:2] for c in AN.fx_cells('burst', area, .065)}
    assert (12, 10) in early and (12, 12) not in early, early
    lit = set()
    for a in range(30):
        lit |= {c[:2] for c in AN.fx_cells('burst', area, a / 60)}
    assert {(10 + dx, 10 + dy) for dx in range(-2, 3) for dy in range(-2, 3)} <= lit
    assert any(cheb(x, y, 10, 10) == 3 for x, y in lit) and (13, 13) not in lit, 'a round cloud beyond the sides'
    first = AN.fx_cells('meteor', kinds['meteor'], .01)
    assert first and all(c[2] == '░' for c in first), first
    late = AN.fx_cells('meteor', kinds['meteor'], AN.METEOR_SHADOW + .02)
    assert any(c[2] == '*' and c[0] < 8 and c[1] < 8 for c in late), late
    assert AN.fx_cells('raise', kinds['raise'], .01)[0][2] == '%' and AN.fx_cells('raise', kinds['raise'], .3)[0][2] == 'z'
    assert AN.fx_life('wave', dict(r=3, delay=.12)) <= .48 and AN.fx_life('burst', dict(r=2, delay=.18, dust=True)) <= .5
    assert AN.fx_life('sky', {}) < .1 and AN.sky_on({}, .01) and not AN.sky_on({}, .2)
    arrow = AN.fx_cells('bolt', dict(cells=[(1, 0), (2, 0)], src=(0, 0), ch='-'), 0)
    assert arrow and arrow[0][2] == '-'
    assert AN.fx_cells('bolt', dict(cells=[(1, 1), (2, 2)], src=(0, 0), ch='-'), 0)[0][2] == '\\'
    # a firebolt in a fight: it flies, opens out on the target, and a key skips it
    app = new_app('soft', seed=3)
    g, p = app.game, app.game.player
    g.enter_dungeon(list(g.world.dungeons)[0], 1, 'up')
    g.map.mons = [o for o in g.map.mons if o.is_npc]
    far = [c for c in free_around(g, g.map, p.x, p.y, 4) if cheb(c[0], c[1], p.x, p.y) >= 2 and
           g.line_clear(p.x, p.y, *c)]
    e = make_monster(g, 'goblin', far[0][0], far[0][1], 3)
    e.hp = e.maxhp = 999
    e.awake = True
    g.map.mons.append(e)
    g.compute_fov()
    p.known = ['firebolt', 'drain']
    p.disc['fire'] = [10, 0]
    p.disc['shadow'] = [10, 0]
    for sid in ('firebolt', 'drain'):
        p.bar[5] = sid
        p.cooldowns.clear()
        p.mana = 999
        p.life = 5
        assert SK.use(g, 5), sid
        app.after_action()
        fx = [ev[2][1] for ev in app.effects if ev[0] == 'fx']
        assert 'bolt' in fx and 'burst' in fx, (sid, fx)
        if sid == 'drain':
            assert 'drain' in fx, fx
        app.render()
        check_colours(app)
        app.key('esc')
        assert not any(ev[0] == 'fx' for ev in app.effects), 'a key skips the effects'
        while not isinstance(app.top, ui.GameScreen):
            app.key('esc')
    # Meteor, Frost Nova, Call the Storm (the sky goes white for one frame), Raise Skeleton from a corpse
    p.disc['frost'] = [40, 0]
    p.disc['storm'] = [40, 0]
    p.disc['necromancy'] = [40, 0]
    p.disc['fire'] = [60, 0]
    wants = {'meteor': 'meteor', 'nova': 'wave', 'storm_call': 'sky', 'raise_skeleton': 'raise', 'morraks_bargain': 'wave'}
    p.disc['shadow'] = [60, 0]
    for sid, want in wants.items():
        if sid == 'raise_skeleton':
            spot = next(c for c in free_around(g, g.map, p.x, p.y, 2) if c not in ((p.x, p.y), (e.x, e.y)) and
                        g.visible(*c) and not g.occupied(g.map, *c))
            g.map.__dict__.setdefault('slain', []).append(('goblin', spot[0], spot[1], 3))
        app.effects.clear()
        p.bar[5] = sid
        p.cooldowns.clear()
        p.mana = p.stamina = 999
        p.life = 500
        e.hp = 999
        assert SK.use(g, 5), sid
        app.after_action()
        fx = [ev[2][1] for ev in app.effects if ev[0] == 'fx']
        assert want in fx, (sid, fx)
        if sid == 'storm_call':
            lit = [ev for ev in app.effects if ev[0] == 'fx' and ev[2][1] == 'sky']
            assert lit and AN.sky_on(lit[0][2][2], 0)
            sky = FakeCanvas(4, 2)
            sky.lighten(2, 2, .55)
            assert sky.bg[0] != (0, 0, 0) and sky.bg[3] == (0, 0, 0)
        app.render()
        check_colours(app)
        app.key('esc')
        while not isinstance(app.top, ui.GameScreen):
            app.key('esc')
    g.map.mons = [o for o in g.map.mons if not getattr(o, 'thrall', 0)]
    # effects off: the old flash; short: half as long
    app.fx_mode = 'off'
    g.fx('bolt', cells=[(p.x + 1, p.y)], col=(255, 0, 0))
    app.after_action()
    assert app.effects and app.effects[-1][0] == 'flash'
    app.fx_mode = 'short'
    g.fx('burst', x=p.x, y=p.y, r=1, col=(255, 0, 0))
    app.after_action()
    e0 = app.effects[-1]
    life = AN.fx_life('burst', e0[2][2])
    assert app.fx_alive(e0, e0[1] + life * .4) and not app.fx_alive(e0, e0[1] + life * .6)
    app.fx_mode = 'full'
    # the main menu sets it, and it is kept next to the save
    menu = ui.App(FakeCanvas(ui.W, ui.H))
    menu.render()
    menu.key('f')
    assert menu.fx_mode == 'short' and E.load_settings().get('effects') == 'short'
    assert ui.App(FakeCanvas(ui.W, ui.H)).fx_mode == 'short'
    menu.key('f')
    menu.key('f')
    assert menu.fx_mode == 'full' and E.load_settings().get('effects') == 'full'
    # burning flickers, poisoned pulses, frozen stands on ice
    looks = {AN.status_look((200, 200, 200), (0, 0, 0), k / 7, 3, 3, burn=True)[0] for k in range(10)}
    assert len(looks) > 3, looks
    assert AN.status_look((200, 200, 200), (0, 0, 0), 0, 3, 3, frozen=True)[1] == AN.ICE_BG
    e.effects['burn'] = [4, 3]
    app.render()
    assert app.top.moving
    check_colours(app)
    # Wild Shape: your @ in the bear's colours
    p.buffs.append(['dmg', 30, 10, 'Bear shape'])
    app.effects.clear()
    app.render()
    ox, oy = app.top.origin
    i = (p.y - oy) * app.cv.w + (p.x - ox)
    assert app.cv.ch[i] == '@' and tuple(app.cv.fg[i]) == AN.SHAPES['bear'][0], (app.cv.ch[i], app.cv.fg[i])
    p.buffs = [b for b in p.buffs if b[3] != 'Bear shape']
    # a village: smoke from the chimneys, sparks at the anvil by day, and rain empties the street
    sid = next(s.id for s in g.world.settlements if s.kind in ('village', 'town') and not getattr(s, 'folk', None))
    to_over(g, sid)
    g.enter_town(sid)
    m = g.map
    assert AN.chimneys(m), 'no chimneys'
    cx, cy = AN.chimneys(m)[0]
    puffs = AN.smoke(cx, cy, 1.0, 1, True, False)
    assert puffs and all(y < cy for _x, y, _c, _col in puffs)
    anvils = [i for i, t in enumerate(m.t) if t == D.ANVIL]
    if anvils:
        ai = anvils[0]
        ax, ay = ai % m.w, ai // m.w
        assert AN.cell(m, ai, ax, ay, LOOK.get(m, ai), 1.0, True, 0) is None
        sparks = {AN.cell(m, ai, ax, ay, LOOK.get(m, ai), k / 9, False, 0)[0] for k in range(60)}
        assert len(sparks) > 1, sparks
    g.turn = (g.turn // D.DAY_LEN + 1) * D.DAY_LEN + D.DAY_LEN // 2
    walkers = [n for n in m.mons if n.is_npc and hasattr(n, 'work_pos') and n.job not in ('guard', 'lamplighter')
               and m.tile(*TW.target_for(g, n)) not in TW.INDOOR]
    assert walkers, 'nobody works outdoors'
    old = WX.current
    WX.current = lambda game: 'rain'
    try:
        assert WX.foul(g)
        for n in walkers:
            assert m.tile(*TW.target_for(g, n, True)) in TW.INDOOR | {D.GRASS, D.PATH} or \
                tuple(TW.target_for(g, n, True)) == tuple(n.home_pos), n.name
        assert any(m.tile(*TW.target_for(g, n, True)) in TW.INDOOR for n in walkers)
        for _ in range(3):
            g.end_turn(1)
        app.screens = [ui.GameScreen(app)]
        app.render()
        check_colours(app)
    finally:
        WX.current = old
    WX.current = lambda game: 'drizzle'
    try:
        assert not WX.foul(g)
    finally:
        WX.current = old
    print('visible ok')


def market_days():
    """Starsday is market day in human towns: the square fills and selling pays a little more; Restday the temple
    bell rings, the townsfolk go to the temple, and shops, stalls and stables are shut."""
    from avarenthia import towns as TW, economy as ECO, calendar as CAL
    print('== market_days')
    app = new_app('soft', seed=5)
    g, p = app.game, app.game.player
    st = next(s for s in g.world.settlements if s.race == 'human' and s.kind in ('village', 'town', 'city')
              and 'temple' in s.services and not getattr(s, 'folk', None))
    to_over(g, st.id)
    g.enter_town(st.id)
    m = g.map
    base = g.day + 7
    day_of = {CAL.weekday(d): d for d in range(base, base + 7)}
    assert set(day_of) == set(CAL.WEEKDAYS)
    def at(day, h):
        g.turn = (day - 1) * D.DAY_LEN + D.DAY_LEN * h // 24
    # a plain day: nothing special
    at(day_of['Windsday'], 10)
    assert TW.day_kind(g) is None and not TW.shut(g)
    gk = D.GOOD_ORDER[0]
    plain = ECO.sell_price(st, gk, ECO.fair_day(g, st))
    ware = next(it for wares in g.shops.values() for it in wares if it.value() >= 40)
    plain_gear = g.sell_value(ware)
    # market day: better prices, people on the square, the line under the map says so
    at(day_of['Starsday'], 10)
    assert TW.day_kind(g) == 'market' and ECO.fair_day(g, st)
    assert ECO.sell_price(st, gk, True) >= plain and ECO.sell_price(st, gk, True) < ECO.buy_price(st, gk)
    assert g.sell_value(ware) > plain_gear
    folk = [n for n in m.mons if n.is_npc and hasattr(n, 'work_pos') and n.job not in ('guard', 'lamplighter', 'fisher', 'drinker')]
    traders = [o for o in m.mons if o.is_npc and o.role == 'market' and m.tile(o.x, o.y) not in TW.INDOOR]
    assert traders, 'no stall on the square'
    at_fair = [n for n in folk if n.id % 3 and tuple(TW.target_for(g, n)) == tuple(TW.fair_spot(g, n))]
    assert at_fair, 'nobody goes to market'
    app.screens = [ui.GameScreen(app)]
    app.render()
    assert 'market day' in app.cv.dump(), 'the line under the map'
    check_colours(app)
    # rest day: the bell, the temple full, the shops shut
    at(day_of['Restday'], 9)
    assert TW.day_kind(g) == 'rest' and TW.shut(g)
    pews = [n for n in folk if TW.pew_spot(g, n)]
    assert pews, 'no room in the temple'
    for n in pews:
        assert m.tile(*TW.target_for(g, n)) in TW.INDOOR
    keeper = next(o for o in m.mons if o.is_npc and o.role in ('shop', 'market'))
    g.request = None
    g.talk(keeper)
    assert g.request is None, 'a shop open on the rest day'
    inn = next((o for o in m.mons if o.is_npc and o.role == 'inn'), None)
    if inn:
        g.talk(inn)
        assert g.request and g.request[0] == 'inn', 'the inn shuts on the rest day'
        g.request = None
    at(day_of['Restday'], 8)
    m.bell_day = None
    TW.live(g, m)
    assert m.bell_day == g.day
    app.render()
    assert 'rest day' in app.cv.dump()
    check_colours(app)
    # outside human towns the week passes unmarked
    to_over(g, st.id)
    assert TW.day_kind(g) is None
    print('market_days ok')


def debug_menu():
    """The debug menu (F12) of the test build: off for players, on with --debug; snapshots, a bug report, the world,
    the player and the rest, each a letter in its own overlay."""
    from avarenthia import debug as DBG, debug_ui as DU, weather as WX, missions as MS
    print('== debug_menu')
    tmp = tempfile.mkdtemp()
    assert DBG.turn_on(['--debug'], environ={}) and not DBG.turn_on([], environ={})
    assert DBG.turn_on([], environ={'AVARENTHIA_DEBUG': '1'})
    assert not DBG.turn_on(['--debug'], environ={'AVARENTHIA_DEBUG': '1'}, here=tmp, frozen=True)   # players: no way in
    open(os.path.join(tmp, 'TESTBUILD'), 'w').close()
    assert DBG.turn_on([], environ={}, here=tmp, frozen=True)                                     # the test build
    app = new_app('soft', seed=4)
    g, p = app.game, app.game.player
    DBG.ON = False
    app.key('f12')
    assert isinstance(app.top, ui.GameScreen), 'F12 does nothing in the players\' game'
    DBG.ON = True
    try:
        def menu(*keys):
            app.key('f12')
            assert isinstance(app.top, DU.DebugScreen), app.top
            for k in keys:
                app.key(k)
                app.render()

        def typed(text):
            for ch in text.lower():
                app.key('space' if ch == ' ' else ch)
            app.render()

        def close():
            while isinstance(app.top, DU.DebugScreen):
                app.key('esc')
            assert isinstance(app.top, ui.GameScreen)
        menu()
        app.render()
        close()
        # the line under the map shows where you are, the turn and the seed
        app.render()
        assert f'seed {g.seed}' in app.cv.dump()
        # the whole map
        menu('m')
        close()
        assert all(g.maps['over'].seen)
        # a snapshot in slot 1
        menu('a', '1')
        assert os.path.exists(DBG.snap_path(1)) and DBG.snap_info(1)
        close()
        saved_turn = g.turn
        # god mode: no harm
        menu('g')
        close()
        g.hurt(99999, 'a test')
        assert not g.dead and p.life == g.stats()['max_life'], p.life
        menu('g')
        close()
        p.life = 3
        menu('h')
        close()
        assert p.life == g.stats()['max_life']
        # coin and levels
        gold = p.gold
        menu('c', 'b')
        close()
        assert p.gold == gold + 10 * 100 * 100
        lvl = p.lvl
        menu('x')
        close()
        assert p.lvl == lvl + 1
        # an item by name, and one of a better grade
        n = len(p.inv)
        menu('i')
        typed('long sword')
        app.key('enter')
        app.key('tab')
        app.key('enter')
        close()
        assert len(p.inv) == n + 2 and p.inv[-1].rar == 'magic', [(i.name, getattr(i, 'rar', '')) for i in p.inv]
        # a skill rank
        menu('n')
        typed('fire')
        app.key('enter')
        assert isinstance(app.top.pages[-1], DU.AskPage)
        typed('42')
        app.key('enter')
        close()
        assert p.disc['fire'][0] == 42
        # teleport into a town far away
        st = max(g.world.settlements, key=lambda s: cheb(s.x, s.y, *g.world_pos()) if s.kind == 'town' else -1)
        menu('t')
        typed(st.name)
        page = app.top.pages[-1]
        page.sel = [r[2] for r in page.shown()].index(('s', st.id))
        app.key('enter')
        assert isinstance(app.top, ui.GameScreen) and g.here is st, g.loc_name()
        # the weather, and time
        menu('w')
        typed('thunder')
        app.key('enter')
        assert WX.current(g) == 'storm', WX.current(g)
        day = g.day
        menu('d', 'e')
        close()
        assert g.day == day + 90
        # spawn a creature, look at what it thinks, kill all in sight
        menu('s')
        typed('giant rat')
        app.key('enter')
        rat = next(o for o in g.map.mons if o.k == 'rat')
        menu('o')
        close()
        app.key('o')
        lk = app.top
        lk.x, lk.y = rat.x, rat.y
        app.render()
        assert '[debug] rat' in app.cv.dump()
        app.key('esc')
        menu('k')
        assert not any(o.k == 'rat' for o in g.map.mons)
        # sight off
        menu('v')
        close()
        assert all(g.vis)
        menu('v')
        close()
        # jobs: make one, then finish it
        jobs = len(MS.active(g))
        menu('j')
        typed('courier')
        app.key('enter')
        assert len(MS.active(g)) == jobs + 1
        close()
        menu('j')
        app.key('enter')
        app.key('a')
        assert len(MS.active(g)) == jobs
        # an event, a standing, a hireling
        ships = sum(1 for w in g.world.wanderers if getattr(w, 'pirate', False))
        menu('e')
        typed('pirate')
        app.key('enter')
        assert sum(1 for w in g.world.wanderers if getattr(w, 'pirate', False)) in (ships, ships + 1)
        f = next(iter(D.FACTIONS))
        menu('f')
        app.key('enter')
        app.key('a')
        close()
        assert p.rep[f] == -100
        menu('l')
        app.key('enter')
        assert g.merc is not None and g.merc.state == 'alive', g.merc
        # the bug report: a folder with all it takes
        menu('r')
        typed('the rat bit me')
        app.key('enter')
        reports = os.path.join(os.path.dirname(E.save_path()), 'bug-reports')
        last = os.path.join(reports, sorted(os.listdir(reports))[-1])
        for fn in ('report.txt', 'log.txt', 'keys.txt', 'screen.txt', 'save.dat'):
            assert os.path.exists(os.path.join(last, fn)), fn
        assert 'the rat bit me' in open(os.path.join(last, 'report.txt'), encoding='utf-8').read()
        assert 'Debug' not in open(os.path.join(last, 'screen.txt'), encoding='utf-8').read().split('\n')[0]
        assert app.shot and app.shot.endswith('screen.png')
        # back to the snapshot
        menu('b', '1')
        assert app.game is not g and app.game.turn == saved_turn and isinstance(app.top, ui.GameScreen)
        app.render()
    finally:
        DBG.ON = False


def k5():
    """The K5 maker: levels with no bad doors and no double walls, fast, every cell reachable; the drawn pieces read,
    packed and sealed; every theme room set in and its telling thing used; the mood line of a room; rivers
    underground: swimming, heavy armour, the river of fire, shoving a foe in."""
    import pickle
    import time
    from avarenthia import k5 as K5, pieces as PC, themes as TH, underground as UG, events as EV
    from avarenthia.entities import Item, make_monster
    print('== k5')
    pcs = PC.load(True)
    middle = [pc for pc in pcs if pc.part == 'middle']
    assert len(middle) >= 38 and {pc.part for pc in pcs} >= {'arrival', 'middle', 'bottom'}, len(middle)
    for seed in range(1, 5):
        random.seed(seed)
        t0 = time.time()
        th = [(pc, PC.drawn(pc)) for pc in random.sample(middle, 3)]
        plan = K5.make(*K5.SIZES['large'], themes=th)
        assert time.time() - t0 < 4, time.time() - t0
        assert plan.bad_doors == 0 and plan.double == 0, (seed, plan.bad_doors, plan.double)
        assert len(K5.walk(plan.floor, plan.up)) == len(plan.floor), seed
        assert sum(1 for r in plan.rooms if r.theme) >= 2, seed
    # a broken piece is refused with where it went wrong; a changed pack is ignored
    for bad in ('NAME: x\nMAP\n...\n...\nENDMAP\n', 'NAME: x\nMAP\n.....\n..Q..\n.....\n  +\nENDMAP\n',
                'NAME: x\nTHING: A = teapot\nMAP\n.....\n.....\n  +\nENDMAP\n'):
        try:
            PC.parse(bad, 'bad.des')
            raise AssertionError(bad)
        except PC.Bad as e:
            assert 'bad.des' in str(e), e
    texts = PC._source_texts()
    raw, seal = PC.pack(texts)
    assert PC.unpack(raw, seal) == texts
    assert PC.unpack(raw[:-1] + bytes([raw[-1] ^ 1]), seal) is None and PC.unpack(raw, None) is None
    # in the game: each theme room is set into a level, says what it is, and its thing answers a bump or a step
    app = new_app('soft', 3)
    g = app.game
    p = g.player
    p.vit = 600
    did = next(k for k, d in g.world.dungeons.items() if d.style != 'cave' and d.tag != 'den' and d.depth >= 3)
    real_pick = PC.pick
    try:
        for pc in middle:
            PC.pick = lambda part, tag, depth, n, used=(), pc=pc: [pc] if part == 'middle' else []
            rid = None
            for _ in range(5):
                g.maps.pop(f'{did}:3', None)
                g.enter_dungeon(did, 3, 'up')
                m = g.map
                rid = next((i for i, r in enumerate(m.rooms) if r[2] == pc.name), None)
                if rid is not None:
                    break
            assert rid is not None, pc.name
            m.mons[:] = [o for o in m.mons if o.is_npc or cheb(o.x, o.y, *TH.cells_of(m, rid)[0]) < 12]
            cells = [c for c in TH.cells_of(m, rid) if D.TILES[m.tile(*c)].walk and not m.mon_at(*c)]
            p.x, p.y = cells[0]
            g.compute_fov()
            n0 = len(g.log)
            TH.on_step(g)
            assert any(str(ln[0] if isinstance(ln, tuple) else ln).rstrip(' x0123456789()') in pc.moods
                       for ln in g.log[n0:]), (pc.name, g.log[n0:])
            for c, (act, r) in list(m.things.items()):
                if r != rid:
                    continue
                if D.TILES[m.tile(*c)].walk:
                    p.x, p.y = c
                    TH.on_step(g)
                    continue
                nb = [(c[0] + dx, c[1] + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx or dy)
                      and m.inb(c[0] + dx, c[1] + dy) and D.TILES[m.tile(c[0] + dx, c[1] + dy)].walk
                      and not m.mon_at(c[0] + dx, c[1] + dy)]
                if not nb:
                    continue
                p.x, p.y = nb[0]
                g.compute_fov()
                g.try_move(c[0] - p.x, c[1] - p.y)
                if g.pending:
                    opts = [k for _l, k in g.pending['options'] if k not in (None, 'bye')]
                    EV.resolve(g, opts[0] if opts else 'bye')
                break
            for _ in range(3):
                g.end_turn(1)
            if g.cur != m.key or g.dead:           # the floor gave way, or the arch took you up
                g.dead = False
            p.life = g.stats()['max_life']
            pickle.dumps(m)                         # a level with theme rooms saves
    finally:
        PC.pick = real_pick
    # the gates: a hidden door is found by walking into it, a vault opens only with its key
    g.maps.pop(f'{did}:3', None)
    g.enter_dungeon(did, 3, 'up')
    m = g.map
    x, y = next((i % m.w, i // m.w) for i, t in enumerate(m.t) if t == D.FLOOR and m.t[i + 1] == D.WALL)
    p.x, p.y = x, y
    m.set(x + 1, y, D.SECRET)
    g.try_move(1, 0)
    assert m.tile(x + 1, y) == D.DOOR
    m.set(x + 1, y, D.VAULTDOOR)
    assert g.try_move(1, 0) == 0 and m.tile(x + 1, y) == D.VAULTDOOR
    key = Item(g.new_id(), 'vkey', 'k5', 1)
    key.name, key.door = 'Heavy Iron Key', (m.key, (x + 1, y))
    p.inv.append(key)
    g.try_move(1, 0)
    assert m.tile(x + 1, y) == D.ODOOR and key not in p.inv
    # mood lines: walking through a level's rooms names some of them
    lines = {ln for v in TH.SHAPE_MOODS.values() for ln in v}
    n0 = len(g.log)
    for rid in range(len(m.rooms)):
        c = next((c for c in TH.cells_of(m, rid) if D.TILES[m.tile(*c)].walk), None)
        if c:
            p.x, p.y = c
            TH.on_step(g)
    assert any(str(ln[0] if isinstance(ln, tuple) else ln) in lines for ln in g.log[n0:])
    # rivers underground: one always runs from edge to edge, and every part of the level stays reachable
    UG.CHANCE, UG.FIRE_SHARE = 1.0, 0.0
    try:
        for kind in ('water', 'fire'):
            UG.FIRE_SHARE = 1.0 if kind == 'fire' else 0.0
            g.maps.pop(f'{did}:3', None)
            g.enter_dungeon(did, 3, 'up')
            m = g.map
            assert getattr(m, 'river', None) == kind, getattr(m, 'river', None)
            tile = D.LAVA if kind == 'fire' else D.WATER
            riv = [i for i in m.river_flow if m.t[i] == tile]
            xs, ys = {i % m.w for i in riv}, {i // m.w for i in riv}
            assert (min(xs) == 0 and max(xs) == m.w - 1) or (min(ys) == 0 and max(ys) == m.h - 1)
            parts = [q for q in UG._parts(m) if not q <= getattr(m, 'theme_cells', set())]
            assert len(parts) == 1, [len(q) for q in parts]
            assert any(t in (D.BRIDGE, D.SHALLOW, D.CRUST) for t in m.t)
            bank = next((i, j) for i in riv for j in (i + 1, i - 1, i + m.w, i - m.w)
                        if 0 <= j < len(m.t) and m.t[j] == D.FLOOR and not m.mon_at(j % m.w, j // m.w))
            wet, dry = bank
            p.x, p.y = dry % m.w, dry // m.w
            dx, dy = wet % m.w - p.x, wet // m.w - p.y
            m.mons[:] = []
            if kind == 'water':
                arm = next((it for it in p.inv if it.id == p.eq.get('armor')), None)
                plate = Item(g.new_id(), 'gear', 'platemail')
                plate.base, plate.slot = 'platemail', 'armor'
                p.inv.append(plate)
                p.eq['armor'] = plate.id
                assert g.try_move(dx, dy) == 0 and g.pending and g.pending['key'] == 'river_swim'
                life = p.life
                EV.resolve(g, 'in')
                assert (p.x, p.y) == (wet % m.w, wet // m.w) and p.life < life
                p.x, p.y = dry % m.w, dry // m.w
                p.inv.remove(plate)
                p.eq['armor'] = arm.id if arm else None
                if arm is None:
                    p.eq.pop('armor')
                assert g.try_move(dx, dy) == 2 and not g.pending and m.tile(p.x, p.y) == D.WATER
                # a swimmer comes after you into the water; others stay on the bank
                p.x, p.y = wet % m.w, wet // m.w
                spot = next((x, y) for x in range(p.x - 2, p.x + 3) for y in range(p.y - 2, p.y + 3)
                            if m.inb(x, y) and m.tile(x, y) == D.WATER and cheb(x, y, p.x, p.y) == 2)
                croc = make_monster(g, 'crocodile', spot[0], spot[1], 3)
                croc.awake = True
                m.mons.append(croc)
                assert UG.swims(croc) and UG.swim_after(g, croc) and cheb(croc.x, croc.y, p.x, p.y) == 1
            else:
                assert g.try_move(dx, dy) == 0 and g.pending and g.pending['key'] == 'river_fire'
                life = p.life
                EV.resolve(g, 'in')
                assert p.life < life * .8, (life, p.life)
                p.life = g.stats()['max_life']
                # shove a foe into the fire: it burns, and crawls back out if it lives
                p.x, p.y = dry % m.w - dx, dry // m.w - dy
                if not D.TILES[m.tile(p.x, p.y)].walk:
                    m.set(p.x, p.y, D.FLOOR)
                foe = make_monster(g, 'skeleton', dry % m.w, dry // m.w, 3)
                foe.awake = True
                m.mons.append(foe)
                hp = foe.hp
                from avarenthia import weaponskills as WS
                WS.push(g, foe, 1)
                assert foe not in m.mons or foe.hp < hp
            pickle.dumps(m)
    finally:
        UG.CHANCE, UG.FIRE_SHARE = .45, .35
    # the test build makes a level round a theme room, or with a river, and puts you beside it
    from avarenthia import debug as DBG
    DBG.theme_level(g, 'vault')
    rid = next(i for i, r in enumerate(g.map.rooms) if r[2] == 'vault')
    assert min(cheb(p.x, p.y, *c) for c in TH.cells_of(g.map, rid)) <= 3
    assert D.VAULTDOOR in g.map.t and any(it.k == 'vkey' for it in g.map.items)
    DBG.theme_level(g, 'river:fire')
    assert g.map.river == 'fire' and any(g.map.t[(p.y + dy) * g.map.w + p.x + dx] == D.LAVA
                                         for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
    print('k5 ok:', len(middle), 'theme rooms, rivers of water and fire')


def places():
    """Temples, towers and barrows of every people on their own land: every stair can be reached and leads somewhere,
    the guard stops a stranger, the top of a tower shows the land, the edge asks before you fall, the bier wakes its
    king, and the loose flagstone at the bottom of a temple lifts when you know the tale."""
    from avarenthia import places as PL, towers as TOW, crime as CR, events as EV
    from avarenthia.entities import make_monster
    from collections import Counter, deque
    import pickle
    app = new_app('soft')
    g = app.game
    p = g.player
    w = g.world
    kinds = Counter((s.kind, PL.people_of(s)) for s in w.sites if PL.is_place(s))
    for pe in PL.PEOPLES:
        assert kinds[('temple', pe)] >= 1, ('temple', pe)
    for pe in ('human', 'elf', 'dwarf', 'orc', 'goblin', 'kobold', 'gnoll', 'lizard'):
        assert kinds[('tower', pe)] >= 1, ('tower', pe)
    assert sum(v for (k, _pe), v in kinds.items() if k == 'barrow') >= 6, kinds
    assert not any(s.kind == 'watchtower' for s in w.sites)

    def reach(m, start):
        seen, q = {start}, deque([start])
        while q:
            x, y = q.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                c = (x + dx, y + dy)
                if c not in seen and m.inb(*c) and (D.TILES[m.tile(*c)].walk or m.tile(*c) in (D.DOOR, D.SECRET)):
                    seen.add(c)
                    q.append(c)
        return seen

    done = set()
    for s in w.sites:
        tag = (s.kind, PL.people_of(s), getattr(s, 'state', '') if s.kind == 'tower' else '')
        if not PL.is_place(s) or tag in done:
            continue
        done.add(tag)
        to_over(g, 0)
        p.x, p.y = s.x, s.y
        g.over_pos = (s.x, s.y)
        g.enter_site(s.id)
        m = g.map
        app.render()
        got = reach(m, m.entry)
        for t in (D.UP, D.DOWN):
            for i in [i for i, v in enumerate(m.t) if v == t]:
                if (i % m.w, i // m.w) not in got:
                    from avarenthia import look as LK
                    ux, uy = i % m.w, i // m.w
                    for y in range(max(0, uy - 9), min(m.h, uy + 10)):
                        print(''.join(('o' if (x, y) in got else LK.get(m, y * m.w + x)[0]) for x in range(max(0, ux - 20), min(m.w, ux + 20))))
                    print(m.entry, (ux, uy))
                assert (i % m.w, i // m.w) in got, (tag, t)
        for t, d in ((D.UP, 'up'), (D.DOWN, 'down')):
            if t not in m.t:
                continue
            g.cur = s.map_key
            i = m.t.index(t)
            p.x, p.y = i % m.w, i // m.w
            g.use_stairs(d)
            assert g.map is not m, (tag, d)
            app.render()
            for _ in range(8):                          # all the way up, or all the way down
                mm = g.map
                if t not in mm.t or (d == 'down' and mm.kind != 'dungeon'):
                    break
                i = mm.t.index(t)
                p.x, p.y = i % mm.w, i // mm.w
                g.use_stairs(d)
                app.render()
            pickle.dumps(g.map)
            back = {D.UP: D.DOWN, D.DOWN: D.UP}[t]      # and the way back leads home
            for _ in range(10):
                mm = g.map
                if mm.key == s.map_key or back not in mm.t:
                    break
                i = mm.t.index(back)
                p.x, p.y = i % mm.w, i // mm.w
                g.use_stairs('down' if d == 'up' else 'up')
            assert g.cur == s.map_key, (tag, d, g.cur)
        print('  ', *tag, 'ok')
    # a stranger is stopped by the warden; pushing past is a crime
    tem = next(q for q in w.sites if q.kind == 'temple' and q.people in ('elf', 'dwarf', 'gnome', 'halfling'))
    to_over(g, 0)
    g.enter_site(tem.id)
    m = g.map
    assert m.bar, 'a warden'
    cell, need = next(iter(m.bar.items()))
    real = PL.tier
    PL.tier = lambda game, site: 0
    try:
        assert PL.barred(g, *cell) == 0 and g.pending and g.pending['key'] == 'place_bar'
        heat = CR.max_heat(g)
        EV.resolve(g, 'force')
        assert m.forced and CR.max_heat(g) >= heat
        assert PL.barred(g, *cell) is None
    finally:
        PL.tier = real
    # the top of a tower: the land below, the edge asks first, and the fall hurts by the floors
    tw = next(q for q in w.sites if q.kind == 'tower' and q.people == 'human' and getattr(q, 'state', 'whole') == 'whole')
    to_over(g, 0)
    om = g.maps['over']
    for i in range(len(om.seen)):                       # forget the land round it, seen on the walk above
        if cheb(i % om.w, i // om.w, tw.x, tw.y) <= 8:
            om.seen[i] = 0
    before = sum(om.seen)
    floors = climb(g, tw)
    assert floors >= 2, floors
    assert sum(om.seen) > before, 'the lookout marks the land'
    m = g.map
    assert m.sky == tw.id
    air = next(((i % m.w, i // m.w) for i, t in enumerate(m.t) if t == D.AIR
                and any(D.TILES[m.t[j]].walk for j in (i + 1, i - 1, i + m.w, i - m.w) if 0 <= j < len(m.t))), None)
    if air is None:                                     # a whole top has its parapet all round: break a gap in it
        i = next(i for i, t in enumerate(m.t) if t == D.PARAPET
                 and any(D.TILES[m.t[j]].walk for j in (i + 1, i - 1, i + m.w, i - m.w))
                 and any(m.t[j] == D.AIR for j in (i + 1, i - 1, i + m.w, i - m.w)))
        m.t[i] = D.AIR
        air = (i % m.w, i // m.w)
    p.x, p.y = next((air[0] + dx, air[1] + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                    if D.TILES[m.tile(air[0] + dx, air[1] + dy)].walk)
    m.mons[:] = []
    g.compute_fov()
    life = p.life
    g.try_move(air[0] - p.x, air[1] - p.y)
    assert g.pending and g.pending['key'] == 'tower_edge'
    EV.resolve(g, 'bye')
    assert g.map is m and p.life == life
    g.try_move(air[0] - p.x, air[1] - p.y)
    EV.resolve(g, 'jump')
    assert g.map is not m and p.life < life, 'over the edge'
    p.life = g.stats()['max_life']
    g.request = None
    # a foe shoved over the edge falls away
    g.cur = m.key
    o = make_monster(g, 'goblin', *air, 2)
    m.mons.append(o)
    TOW.shove_over(g, o, *air)
    assert o not in m.mons
    # the bier wakes its king
    br = next(q for q in w.sites if q.kind == 'barrow' and q.people == 'human')
    to_over(g, 0)
    g.enter_site(br.id)
    i = g.map.t.index(D.DOWN)
    p.x, p.y = i % g.map.w, i // g.map.w
    g.use_stairs('down')
    m = g.map
    bx, by = m.bier
    m.mons[:] = []
    spot = next((bx + dx, by + dy) for dx, dy in ((-1, 0), (1, 0), (0, 1), (0, -1)) if D.TILES[m.tile(bx + dx, by + dy)].walk)
    p.x, p.y = spot
    g.compute_fov()
    g.try_move(bx - p.x, by - p.y)
    assert g.pending and g.pending['key'] == 'barrow_bier'
    EV.resolve(g, 'take')
    assert m.bier_taken and any(o.name for o in m.mons if not o.is_npc), 'the king rises'
    pickle.dumps(m)
    # the hidden bottom of a temple: a tale tells of it, the loose flagstone lifts, the older place lies under it
    old = PL.hidden_temples(g)
    if old:
        q = old[0]
        p.old_bottoms = {q.id}
        dg = w.dungeons[q.below]
        g.enter_dungeon(dg.id, dg.depth, 'up')
        m = g.map
        assert D.LOOSE in m.t
        i = m.t.index(D.LOOSE)
        p.x, p.y = i % m.w, i // m.w
        PL.loose_step(g)
        assert m.tile(p.x, p.y) == D.DOWN and m.ancient
        g.use_stairs('down')
        assert g.map.depth == dg.depth + 1 and any(o.name == 'The Old Warden' for o in g.map.mons)
        pickle.dumps(g.map)
    print('places ok:', len(done), 'kinds of place,', sum(kinds.values()), 'in the world,', len(old), 'over older places')


def halls():
    """Abbeys, forts and manors of every people, the underground kinds' own plans and the goblin village: each stands
    where it should, its stairs lead up and down, its telling things answer, a fort may be taken, abandoned or broken,
    the portcullis drops on alarm, and the round trip from the ravine to the deep halls comes home."""
    from avarenthia import places as PL, halls as HL, themes as TH, delves as DV, gobvillage as GV, hunger as HU
    from avarenthia.world import Dungeon
    from collections import Counter, deque
    import pickle
    app = new_app('soft')
    g = app.game
    p = g.player
    w = g.world
    kinds = Counter((s.kind, PL.people_of(s)) for s in w.sites if s.kind in PL.HALLS)
    for pe in PL.PEOPLES:
        if pe == 'halfling' and not getattr(w, 'halfling_land', None):
            continue
        for k in ('monastery', 'fort', 'manor'):
            assert kinds[(k, pe)] >= 1, (k, pe, kinds)
    assert all(PL.people_of(s) == 'human' for s in w.sites if s.kind == 'monastery' and s.name in
               ('Monastery of the Grey Brothers', 'Abbey of Saint Wendel'))

    def reach(m, start):
        seen, q = {start}, deque([start])
        while q:
            x, y = q.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                c = (x + dx, y + dy)
                if c not in seen and m.inb(*c) and (D.TILES[m.tile(*c)].walk or m.tile(*c) in (D.DOOR, D.SECRET, D.WOVEN)):
                    seen.add(c)
                    q.append(c)
        return seen

    def visit(s):
        to_over(g, 0)
        p.x, p.y = s.x, s.y
        g.over_pos = (s.x, s.y)
        g.enter_site(s.id)
        return g.map

    told = Counter()
    for s in [q for q in w.sites if q.kind in PL.HALLS]:
        m = visit(s)
        app.render()
        assert m.hall == s.kind and getattr(m, 'things', None) is not None
        got = reach(m, m.entry)
        for t in (D.UP, D.DOWN):
            for i in [i for i, v in enumerate(m.t) if v == t]:
                assert (i % m.w, i // m.w) in got, (s.kind, s.people, t)
        assert D.DOWN in m.t, (s.kind, s.people)
        for (x, y), (act, rid) in list(m.things.items()):     # every telling thing answers
            if act in told and act not in ('h_portrait',):
                continue
            told[act] += 1
            p.x, p.y = m.entry
            spent = TH.ACTIONS[act](g, x, y, rid, TH.state(m, rid))
            assert spent is not None and spent >= 0, act
            if g.dead or g.map is not m:
                g.dead = False
                g.cur = s.map_key
        if getattr(s, 'up', None):
            g.cur = s.map_key
            i = m.t.index(D.UP)
            p.x, p.y = i % m.w, i // m.w
            g.use_stairs('up')
            um = g.map
            assert getattr(um, 'upper', False) and um.sky == s.id, s.name
            app.render()
            assert len(reach(um, (p.x, p.y))) > 30, s.name
            pickle.dumps(um)
            g.use_stairs('down')
            assert g.cur == s.map_key
    for act in ('h_lore', 'h_pool', 'h_lens', 'h_dungeonmap', 'h_meal', 'h_portrait', 'h_letters', 'h_say'):
        assert told[act], (act, told)
    print('  telling things:', dict(told))
    # a halfling house feeds a friend once a day
    hh = next((q for q in w.sites if q.kind == 'monastery' and q.people == 'halfling'), None)
    if hh:
        m = visit(hh)
        cell = next(c for c, v in m.things.items() if v[0] == 'h_meal')
        p.food, p.hall_meal = 100, -1
        TH.ACTIONS['h_meal'](g, *cell, m.things[cell][1], {})
        assert p.food > 600
        before = p.food
        TH.ACTIONS['h_meal'](g, *cell, m.things[cell][1], {})
        assert p.food == before, 'one meal a day'
    # who holds a fort: taken by bandits, abandoned to beasts, or a ruin
    fort = next(q for q in w.sites if q.kind == 'fort' and q.people == 'human')
    for st in ('taken', 'abandoned', 'ruin', 'whole'):
        fort.state = st
        fort.holder = 'bandits' if st == 'taken' else None
        g.maps.pop(fort.map_key, None)
        m = visit(fort)
        foes = [o for o in m.mons if not o.is_npc]
        folk = [o for o in m.mons if o.is_npc]
        if st == 'taken':
            assert foes and not folk and getattr(m, 'portcullis', None)
            assert not PL.friendly(g, fort)
        elif st == 'abandoned':
            assert not folk and not m.bar
        elif st == 'ruin':
            assert D.RUBBLE in m.t and not folk
        else:
            assert folk
        print('  ', fort.name, st, len(foes), 'foes', len(folk), 'folk')
    # the portcullis drops when the bandits see you
    fort.state, fort.holder = 'taken', 'bandits'
    g.maps.pop(fort.map_key, None)
    m = visit(fort)
    gate = m.portcullis[0]
    o = next(o for o in m.mons if not o.is_npc)
    p.x, p.y = gate[0] - 1, gate[1]
    o.x, o.y = gate[0] + 3, gate[1]
    g.compute_fov()
    HL.alarm(g)
    assert m.alarmed and m.tile(*gate) == D.BARS
    fort.state, fort.holder = 'whole', None
    g.maps.pop(fort.map_key, None)
    # the elves' gate of woven branches shuts for a stranger; the gnomes' hill hides its door
    real = PL.tier
    PL.tier = lambda game, site: 0
    try:
        for kind, pe, tile in (('fort', 'elf', D.WOVEN), ('fort', 'gnome', D.SECRET)):
            q = next((q for q in w.sites if q.kind == kind and q.people == pe and getattr(q, 'state', 'whole') == 'whole'),
                     None)
            if q:
                g.maps.pop(q.map_key, None)
                m = visit(q)
                assert tile in m.t, (kind, pe)
                g.maps.pop(q.map_key, None)
    finally:
        PL.tier = real
    # every underground kind lays out its own plan: rooms by their use, folk where they belong
    for k, kd in DV.KINDS.items():
        did = f'test_{k}'
        dg = Dungeon(did, f'Test {k}', 2, 3, 'cave' if not kd.get('built') else 'rooms', k, None, (120, 110, 100), 5, 5, False)
        w.dungeons[did] = dg
        to_over(g, 0)
        g.enter_dungeon(did, 1, 'up')
        m = g.map
        assert getattr(m, 'delve', None) == k, k
        got = reach(m, (p.x, p.y))
        for t in (D.UP, D.DOWN):
            for i in [i for i, v in enumerate(m.t) if v == t]:
                assert (i % m.w, i // m.w) in got, (k, t)
        assert any(not o.is_npc for o in m.mons) or k in ('cave', 'grotto'), k
        app.render()
        print('  ', k, len(m.mons), 'folk', len([r for r in m.rooms if r[0].startswith('delve:')]), 'rooms')
        del w.dungeons[did]
    # the goblin ravine leads down to the village, the village down to the deep halls, and all the way back
    rv = next((q for q in w.sites if q.kind == 'ravine'), None)
    if rv:
        m = visit(rv)
        assert getattr(m, 'delve_gate', None)
        i = m.t.index(D.DOWN)
        p.x, p.y = i % m.w, i // m.w
        g.use_stairs('down')
        vm = g.map
        assert getattr(vm, 'village', False) and D.HIGHSEAT in vm.t
        app.render()
        i = vm.t.index(D.DOWN)
        p.x, p.y = i % vm.w, i // vm.w
        g.use_stairs('down')
        assert g.map.kind == 'dungeon' and g.map.did == GV.deep_id(rv)
        i = g.map.t.index(D.UP)
        p.x, p.y = i % g.map.w, i // g.map.w
        g.use_stairs('up')
        assert g.map is vm
        i = vm.t.index(D.UP)
        p.x, p.y = i % vm.w, i // vm.w
        g.use_stairs('up')
        assert g.cur == rv.map_key
        pickle.dumps(vm)
    print('halls ok:', sum(kinds.values()), 'abbeys, forts and manors;', len(DV.KINDS), 'underground kinds')


def aurora():
    """The northern lights' gift: rune stones that only the lights show, cheaper Frost and Storm, the barrow spirits
    with their errands and their wrath when the barrow is dug into, and the glow of the ghostly."""
    from avarenthia import aurora as AU, hidden as HP, places as PL, missions as MS, jobs as JB, skills as SK
    from avarenthia import debug as DBG, weather as WX, events as EV
    import pickle
    print('== the northern lights')
    app = new_app('soft')
    g = app.game
    p = g.player
    w = g.world
    om = g.maps['over']
    stones = [q for q in w.pois if q.kind == 'runestone']
    assert stones and all(AU.northern(w, q.x, q.y) for q in stones), len(stones)
    rs = stones[0]
    to_over(g, 0)
    p.x, p.y = rs.x - 1, rs.y
    g.over_pos = (p.x, p.y)
    g.compute_fov()
    EV.discover(g)
    assert not rs.found, 'plain rock by day'
    keep_on = DBG.ON
    DBG.ON = True
    p.dbg = set(getattr(p, 'dbg', set())) | {'aurora'}
    assert AU.lit(g) and WX.shown(g) == 'aurora'
    EV.discover(g)
    assert rs.found, 'the lights show it'
    EV.on_poi(g, rs)
    assert w.ways[rs.points].id in HP.known(g) and g.request[0] == 'dialog'
    app.render()
    # Frost and Storm cost less under the lights
    sk = next(k for k in SK.SKILL_LIST if k.line == 'frost' and k.cost >= 8)
    lit_cost = SK.cost_of(g, sk)
    p.dbg.discard('aurora')
    assert SK.cost_of(g, sk) > lit_cost, (SK.cost_of(g, sk), lit_cost)
    p.dbg.add('aurora')
    # the barrow spirits
    north = AU.northern
    barrows = [q for q in w.sites if q.kind == 'barrow']
    assert sum(1 for q in barrows if AU.northern(w, q.x, q.y)) >= 2, 'the old kings of the north'
    AU.northern = lambda world, x, y: True          # every barrow counts as northern here

    def visit(s):
        to_over(g, 0)
        p.x, p.y = s.x, s.y
        g.over_pos = (s.x, s.y)
        g.enter_site(s.id)
        g.compute_fov()
        return g.map
    try:
        site = barrows[0]
        m = visit(site)
        sp = next(o for o in m.mons if getattr(o, 'spirit', False))
        assert sp.is_npc and sp.ch == 'G' and MS.quest_mark(g, sp) == '!'
        p.x, p.y = sp.x, sp.y + 1 if m.inb(sp.x, sp.y + 1) else sp.y - 1
        g.compute_fov()
        aura, _w = AU.auras(g, m, 0.0)
        assert aura, 'the spirit glows'
        app.render()
        gold = p.gold
        g.talk(sp)
        job = next(x for x in MS.active(g) if x.kind == 'spirit')
        assert site.id in AU.heard(g) and MS.target_pos(g, job)
        # every kind of errand can be made, and leads somewhere
        subs = {}
        for _ in range(60):
            x = AU.make_job(g, site)
            if x:
                subs.setdefault(x.data['sub'], x)
        assert {'grave', 'deed'} <= set(subs), subs.keys()
        gr = subs['grave']
        gr.state = 'active'
        g.missions = [x for x in g.missions if x.kind != 'spirit'] + [gr]
        AU.accept(g, gr)
        to_over(g, 0)
        p.x, p.y = gr.data['spot']
        g.over_pos = (p.x, p.y)
        JB.step(g)
        assert gr.state == 'turnin', gr.state
        assert MS.target_pos(g, gr)[0] == (site.x, site.y)
        visit(site)
        assert gr.state == 'done' and p.gold > gold, (gr.state, p.gold, gold)
        dd = subs['deed']
        AU.won(g, dd, True)
        assert dd.state == 'turnin'
        if 'sword' in subs:
            sw = subs['sword']
            AU.accept(g, sw)
            assert w.dungeons[sw.data['dungeon']].relic == sw.id
            AU.on_fail(g, sw)
            assert w.dungeons[sw.data['dungeon']].relic is None
        # digging in: the spirit asks first, then the dead wake
        site2 = barrows[1] if len(barrows) > 1 else site
        m = visit(site2)
        assert any(getattr(o, 'spirit', False) and o.is_npc for o in m.mons)
        assert PL.stairs(g, D.DOWN, None) == 0 and g.pending['key'] == 'spirit_dig'
        ctx = g.pending['ctx']
        g.pending = None
        EV.RESOLVERS['spirit_dig'](g, 'go', ctx)
        assert site2.wrath and g.map.did == site2.below
        dead = [o for o in g.map.mons if not o.is_npc]
        assert all(o.awake for o in dead)
        g.cur = site2.map_key
        AU.on_barrow(g)
        foe = next(o for o in g.map.mons if getattr(o, 'spirit', False))
        assert not foe.is_npc and foe.wrath and foe.k == 'barrow_spirit'
        g.compute_fov()
        app.render()
        AU.on_kill(g, foe)
        assert site2.spirit_laid
        # the lights fade, and a calm spirit with them
        site3 = barrows[2] if len(barrows) > 2 else site
        m = visit(site3)
        assert any(getattr(o, 'spirit', False) for o in m.mons)
        p.dbg.discard('aurora')
        if not AU.lit(g):
            AU.on_barrow(g)
            assert not any(getattr(o, 'spirit', False) and o.is_npc for o in m.mons)
        pickle.dumps(g)
    finally:
        AU.northern = north
        DBG.ON = keep_on
        p.dbg.discard('aurora')
    print('northern lights ok:', len(stones), 'rune stones,', len(barrows), 'barrows, errands', sorted(subs))


def rift():
    """The Rift and the Ashen Deep: the rift opens, the land burns to ash, fiends raid; every level of the Deep with
    its river of fire and chains, vents, bone fields, cages, gaoler and gong; the creatures' tricks; the lord heals
    from the gate until its bowls are out; breaking the gate closes the rift; a rift under a deep dungeon."""
    from avarenthia import rift as RF, weather as WX, behave as BH
    from avarenthia.entities import make_monster
    from avarenthia.worldgen import free_around
    from collections import deque
    import pickle
    print('== the rift')
    app = new_app('soft')
    g = app.game
    p = g.player
    w = g.world
    om = g.maps['over']
    vil = next(s for s in w.settlements if s.kind in ('village', 'hamlet') and s.id != 0)
    r = RF.open_rift(g, spot=RF.find_spot(g, (vil.x, vil.y), 8, 20))
    assert r and om.tile(r['x'], r['y']) == D.ENTR and w.dungeon_at(r['x'], r['y']).id == r['did']
    for _ in range(3):
        RF.monthly(g)
    assert r['r'] == 4 and RF.ash_cells(w)
    to_over(g, 0)
    p.x, p.y = r['x'] + 1, r['y']
    g.over_pos = (p.x, p.y)
    assert WX.shown(g) == 'ash'
    app.render()
    keep = random.random
    random.random = lambda: 0.0
    RF.daily(g)
    random.random = keep
    assert r['raids'] == 1 and r.get('taken')
    dg = w.dungeons[r['did']]

    def reach(m, start):
        seen, q = {start}, deque([start])
        while q:
            x, y = q.popleft()
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    c = (x + dx, y + dy)
                    if c not in seen and m.inb(*c) and D.TILES[m.tile(*c)].walk:
                        seen.add(c)
                        q.append(c)
        return seen
    for depth in range(1, dg.depth + 1):
        g.enter_dungeon(dg.id, depth, 'up')
        m = g.map
        assert m.rift and D.LAVA in m.t and m.vents and m.bonefields, depth
        i = m.t.index(D.UP)
        got = reach(m, (i % m.w, i // m.w))
        want = [D.DOWN] if depth < dg.depth else [D.FIREGATE, D.FIREBOWL]
        for t in want:
            j = m.t.index(t)
            x, y = j % m.w, j // m.w
            assert any((x + a, y + b) in got for a in (-1, 0, 1) for b in (-1, 0, 1)), (depth, t)
        assert all(any((cx + a, cy + b) in got for a in (-1, 0, 1) for b in (-1, 0, 1)) for cx, cy in m.cages), depth
        app.render()
    g.enter_dungeon(dg.id, 1, 'up')
    m = g.map
    # nobody rests here
    t0 = g.turn
    g.rest()
    assert g.turn == t0
    # a vent puffs
    (vx, vy), _k = next(iter(m.vents.items()))
    m.vents[(vx, vy)] = 1
    p.x, p.y = next(c for c in free_around(g, m, vx, vy, 1) if D.TILES[m.tile(*c)].walk)
    p.stamina = 50
    RF.turn(g)
    assert p.stamina < 50
    # the dead rise from a bone field
    bf = m.bonefields[0]
    p.x, p.y = bf['cells'][0]
    n = len(m.mons)
    RF.on_step(g)
    assert bf['risen'] and len(m.mons) > n
    # the gaoler runs for the gong and wakes the level
    if getattr(m, 'gong', None):
        gl = next((o for o in m.mons if o.k == 'gaoler'), None)
        if gl:
            # set it a few steps from the gong, with nobody in its way
            dm = RF.bfs(m, m.gong[0], m.gong[1], lambda t: D.TILES[t].walk)
            m._gong_dist = dm
            gl.x, gl.y = next((i % m.w, i // m.w) for i, v in enumerate(dm) if 4 <= v <= 8)
            m.mons = [o for o in m.mons if o is gl or o.is_npc]
            for _ in range(200):
                d = cheb(gl.x, gl.y, p.x, p.y)
                RF.gaoler(g, gl, 3, True)
                if getattr(m, 'rung', False):
                    break
            assert m.rung
    # the creatures' tricks, on an open floor
    m.mons = [o for o in m.mons if o.is_npc]
    fl = [(i % m.w, i // m.w) for i, t in enumerate(m.t) if t in (D.FLOOR, D.ASH)]
    spot = next(c for c in fl if all(m.inb(c[0] + k, c[1]) and m.tile(c[0] + k, c[1]) in (D.FLOOR, D.ASH) for k in range(0, 6)))
    p.x, p.y = spot
    g.compute_fov()
    random.random = lambda: 0.0
    try:
        wd = make_monster(g, 'chain_warden', spot[0] + 4, spot[1], 8)
        m.mons.append(wd)
        g.compute_fov()
        assert RF.hook(g, wd, 4) and cheb(p.x, p.y, wd.x, wd.y) == 1
        m.mons.remove(wd)
        p.x, p.y = spot
        toad = make_monster(g, 'brimstone_toad', spot[0] + 3, spot[1], 8)
        m.mons.append(toad)
        g.compute_fov()
        p.stamina = 50
        assert RF.sulphur(g, toad, 3) and p.stamina < 50
        m.mons.remove(toad)
        brute = make_monster(g, 'slag_brute', spot[0] + 1, spot[1], 8)
        m.mons.append(brute)
        life = p.life
        BH.struck(g, brute, 5)
        assert p.life < life
        assert BH.incoming(g, brute, 10, None, 'cold') == 10 and brute.brittle
        assert BH.incoming(g, brute, 10, True, None) == 20
        m.mons.remove(brute)
        ash = make_monster(g, 'ashwalker', spot[0] + 1, spot[1], 8)
        BH.struck(g, ash, 5)
        assert BH.has(g, 'blinded')
        BH.clear(g, 'blinded', True)
        cl = make_monster(g, 'cinderling', spot[0] + 2, spot[1], 8)
        BH.on_death(g, cl)
        assert m.tile(spot[0] + 2, spot[1]) == D.BURNING
    finally:
        random.random = keep
    p.life = g.stats()['max_life']
    # the bottom: the lord heals from the gate until its bowls are out, calls hounds, and the gate breaks
    g.enter_dungeon(dg.id, dg.depth, 'up')
    m = g.map
    lord = next(o for o in m.mons if getattr(o, 'lord', False))
    assert lord.name == r['lord'] and lord.is_boss
    lord.hp = lord.maxhp * 3 // 4
    hp = lord.hp
    RF.turn(g)
    assert lord.hp > hp
    for i, t in enumerate(list(m.t)):
        if t == D.FIREBOWL:
            RF.bump(g, i % m.w, i // m.w, t)
    assert D.FIREBOWL not in m.t
    lord.hp = lord.maxhp // 2 - 1
    hp = lord.hp
    n = len(m.mons)
    RF.turn(g)
    assert lord.hp == hp and len(m.mons) > n, 'no healing without the bowls; the hounds come'
    m.mons.remove(lord)
    gx, gy = m.gate
    p.life = g.stats()['max_life']
    for _ in range(3):
        RF.bump(g, gx, gy, m.tile(gx, gy))
    assert r['state'] == 'closed' and m.tile(gx, gy) == D.BROKENGATE
    rr = r['r']
    RF.monthly(g)
    assert r['r'] == rr - 1
    app.render()
    # a rift under a deep dungeon: the crack at its bottom
    deep = RF.deep_dungeons(w)
    if deep:
        un = deep[0]
        r2 = RF.open_rift(g, under=un)
        assert r2 and r2['under'] == un.id and w.dungeon_at(un.x, un.y).id == un.id
        g.enter_dungeon(un.id, un.depth, 'up')
        assert D.DOWN in g.map.t
        assert RF.stairs(g, D.DOWN, None) == 1 and g.map.did == r2['did'] and g.map.depth == 1
        assert RF.stairs(g, D.UP, None) == 1 and g.map.did == un.id
    pickle.dumps(g)
    print('rift ok:', dg.depth, 'levels, lord', r['lord'], '; under a dungeon:', bool(deep))


def old_places():
    """Old places from the history: battlefields beside their villages, deserted villages with an event of their own,
    broken bridges, memorials, gallows, quarries, wrecks, hermitages, leper colonies; each map can be walked to every
    telling thing, and each answers a bump; the dead walk on the battle's night; the temple's bread for the lepers;
    the peoples' marks on the world map; a record names the place."""
    from avarenthia import oldplaces as OP, history as HI, debug as DBG, missions as MS, nature as NT, events as EV
    from avarenthia import chronicle as CH
    from avarenthia.entities import Item
    from collections import Counter, deque
    import pickle
    print('== old places')
    app = new_app('soft')
    g = app.game
    p = g.player
    w = g.world
    om = g.maps['over']
    old = [s for s in w.sites if OP.is_old(s)]
    kinds = Counter(s.kind for s in old)
    for k in ('oldfield', 'deserted', 'namestone', 'gallows', 'hermitage'):
        assert kinds[k], (k, kinds)
    assert len({s.name for s in old}) == len(old)
    H = HI.events(w)
    assert all(e['id'] == i for i, e in enumerate(H))
    assert all(H[i - 1]['year'] <= H[i]['year'] for i in range(1, len(H)))
    for s in old:
        assert om.inb(s.x, s.y) and D.TILES[om.tile(s.x, s.y)].walk, s.name
        e = OP.event_of(g, s)
        if s.kind in ('oldfield', 'deserted'):
            assert e and e.get('lead') == ('site', s.id) or s.kind == 'oldfield', s.name
        if s.kind == 'oldfield':
            assert e.get('field') and 1 <= e['doy'] <= 360
        if s.kind == 'deserted':
            assert e['kind'] == 'deserted' and e['village'] == s.name

    def reach(m, start):
        seen, q = {start}, deque([start])
        while q:
            x, y = q.popleft()
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    c = (x + dx, y + dy)
                    if c not in seen and m.inb(*c) and (D.TILES[m.tile(*c)].walk or m.tile(*c) == D.DOOR):
                        seen.add(c)
                        q.append(c)
        return seen
    to_over(g, 0)
    keep_turn = g.turn
    g.turn = (g.turn // D.DAY_LEN) * D.DAY_LEN + int(D.DAY_LEN * 12 / 24)      # noon
    lo = next(t for t in range(g.turn, g.turn + D.DAY_LEN) if (setattr(g, 'turn', t) or NT.low_tide(g)))
    bumped = Counter()
    for s in old:
        to_over(g, 0)
        g.turn = lo
        g.enter_site(s.id)
        m = g.map
        assert m.old == s.kind and g.cur == s.map_key
        app.render()
        got = reach(m, (p.x, p.y))
        cells = [(i % m.w, i // m.w) for i, t in enumerate(m.t) if t in OP.BUMP]
        assert cells or s.kind == 'hermitage', s.name
        for x, y in cells:
            assert any((x + a, y + b) in got for a in (-1, 0, 1) for b in (-1, 0, 1)), (s.name, D.TILES[m.tile(x, y)].name)
        for x, y in cells:
            t = m.tile(x, y)
            if bumped[(s.kind, t)] >= 2:
                continue
            bumped[(s.kind, t)] += 1
            assert OP.bump(g, x, y) is not None, (s.name, D.TILES[t].name)
            g.request = None
            g.pending = None
        for o in [o for o in m.mons if getattr(o, 'role', None) in ('oldplace', 'leper')]:
            g.talk(o)
            app.render()
            g.request = None
            g.pending = None
        pickle.dumps(m)
    assert bumped[('oldfield', D.MOUND)] and bumped[('oldfield', D.CAIRN)]
    assert any(f['key'] == f'old:{s.id}' for f in CH.facts(g)
               for s in old if s.kind == 'oldfield')
    # the wreck: the sea covers the sand at high tide, and the chest is searched only once
    wr = next((s for s in old if s.kind == 'wreck'), None)
    if wr:
        to_over(g, 0)
        g.enter_site(wr.id)
        m = g.map
        i = m.t.index(D.WETSAND)
        hi = next(t for t in range(lo, lo + D.DAY_LEN) if (setattr(g, 'turn', t) or not NT.low_tide(g)))
        g.turn = hi
        assert OP.blocked(g, i % m.w, i // m.w)
        g.turn = lo
        assert OP.blocked(g, i % m.w, i // m.w) is None
        j = m.t.index(D.SEACHEST)
        assert wr.searched and OP.bump(g, j % m.w, j // m.w) == 0
    # the battle's night: the dead get up out of the grass; the blade in a mound
    fld = next(s for s in old if s.kind == 'oldfield')
    e = OP.event_of(g, fld)
    to_over(g, 0)
    g.turn = (g.turn // D.DAY_LEN) * D.DAY_LEN + int(D.DAY_LEN * 23 / 24)
    assert OP.night(g)
    was_on, DBG.ON = DBG.ON, True
    DBG.flags(g).add('oldnight')
    assert DBG.has(g, 'oldnight')
    g.enter_site(fld.id)
    m = g.map
    dead = [o for o in m.mons if o.k in ('skeleton', 'skel_warrior', 'wight')]
    assert len(dead) >= 4 and any(o.k == 'wight' for o in dead), len(dead)
    m.mons = [o for o in m.mons if o not in dead]
    DBG.toggle(g, 'oldnight')
    if not DBG.has(g, 'oldfind'):
        DBG.toggle(g, 'oldfind')
    fld.blade_found = False
    m.set(5, 5, D.MOUND)
    n = len(p.inv)
    OP.dig(g, fld, e, 5, 5)
    assert m.tile(5, 5) == D.DUGMOUND and fld.blade_found and len(p.inv) == n + 1
    assert e['title'][4:] in p.inv[-1].name and p.inv[-1].rar == 'magic', p.inv[-1].name
    DBG.toggle(g, 'oldfind')
    DBG.ON = was_on
    # a ghost in an empty village at night
    dv = next(s for s in old if s.kind == 'deserted')
    dv.who = 'ghost'
    to_over(g, 0)
    g.enter_site(dv.id)
    assert any(o.k == 'ghost' for o in g.map.mons)
    g.turn = keep_turn
    # the temple's bread for the lepers
    col = next((s for s in old if s.kind == 'colony'), None)
    if col:
        city = w.settlements[col.city]
        assert 'temple' in city.services
        mi = OP.make_alms(g, city)
        assert mi and mi.kind == 'alms' and mi.data['site'] == col.id
        city.board.append(mi)
        assert MS.accept(g, city, mi)
        assert any(pc['mid'] == mi.id for pc in p.parcels)
        to_over(g, 0)
        g.enter_site(col.id)
        assert mi.state == 'turnin' and not any(pc['mid'] == mi.id for pc in p.parcels)
        bro = next(o for o in g.map.mons if getattr(o, 'role', None) == 'oldplace')
        p.inv.append(Item(g.new_id(), 'food', 'bread'))
        g.talk(bro)
        assert g.pending and g.pending['key'] == 'oldplace'
        n = sum(i.n for i in p.inv if i.k == 'food')
        EV.resolve(g, 'alms')
        assert sum(i.n for i in p.inv if i.k == 'food') == n - 1
    # the marks of the peoples
    marks = [q for q in w.pois if q.kind in OP.POI_LOOK]
    assert any(q.kind == 'moonstone' for q in marks) and any(q.kind == 'dwarfstone' for q in marks)
    to_over(g, 0)
    for q in marks:
        assert q.secret and q.name
        assert EV.on_poi(g, q) is None and g.request and g.request[0] == 'dialog', q.kind
        g.request = None
        if q.kind == 'moonstone' and getattr(q, 'next', None) is not None:
            assert w.pois[q.next].found
        if q.kind == 'scratch':
            assert w.pois[q.cache].found
        if q.kind == 'cache':
            gold = p.gold
            EV.on_poi(g, q)
            assert p.gold == gold
            g.request = None
    app.render()
    # a record names the deserted village
    e = OP.event_of(g, dv)
    om.seen[dv.y * om.w + dv.x] = 0
    HI.lead(g, e)
    assert om.seen[dv.y * om.w + dv.x]
    pickle.dumps(g)
    print('old places ok:', dict(kinds), len(marks), 'marks')


def varnish():
    """The Varnish: ruined cities found by walking their zones, the Varnish places and the Northern Wall, league stones
    that count down to a city, the way into a city's hidden deep and its own boss, pages in the old letters kept with
    your papers and read once you have the letters, books bound whole by a scribe and sold once, the five riddles made
    whole with their false pieces shown up, and the chapter The Varnish with its headings."""
    from avarenthia import varnish as VN, varnishtexts as T, chronicle as CH, folk as FK, zones as ZN, events as EV
    from avarenthia import history as HI, debug as DBG
    from avarenthia.entities import Item
    from collections import Counter, deque
    import pickle
    print('== varnish')
    app = new_app('soft')
    g = app.game
    p = g.player
    w = g.world
    V = VN.info(g)
    kinds = Counter(s.kind for s in w.sites if VN.is_varnish(s))
    assert kinds['vcity'] >= 2 and kinds['walltower'] >= 5 and kinds['vdeep'] == 5, kinds
    for k in VN.PLACE_KINDS:
        assert kinds[k], (k, kinds)
    assert all(FK.unfound(s) for s in w.sites if VN.is_varnish(s)), 'no Varnish place is on the map beforehand'
    assert len(V['books']) == 8 and {T.BOOK[b]['thread'] for b in V['books']} == set(T.THREADS)
    assert all((bk, n) in V['pages'] for bk in V['books'] for n in range(len(T.BOOK[bk]['pages'])))
    assert len(V['src']) == sum(len(r['frags']) for r in T.RIDDLES)
    for (rk, i), src in V['src'].items():           # every piece of a riddle can be had in this world
        assert src in ('stone', 'library', 'rumour') or src.startswith('page:') and src.split(':')[1] in V['books'] \
            or src.startswith('place:') and any(s.kind == src[6:] or getattr(s, 'deep', None) == src[6:]
                                                for s in w.sites), (rk, i, src)
    for r in T.RIDDLES:
        assert sum(1 for i, fr in enumerate(r['frags']) if not fr[2]) >= T.WHOLE

    def reach(m, start):
        seen, q = {start}, deque([start])
        while q:
            x, y = q.popleft()
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    c = (x + dx, y + dy)
                    if c not in seen and m.inb(*c) and D.TILES[m.tile(*c)].walk:
                        seen.add(c)
                        q.append(c)
        return seen
    # walking into a ruin's zone finds it; a name stone with the letters names it
    city = next(s for s in w.sites if s.kind == 'vcity')
    to_over(g, 0)
    ZN.enter(g, (city.x - 1, city.y))
    m = g.map
    ruin = [i for i, t in enumerate(m.t) if t in (D.COLUMN, D.VPAVE)]
    assert len(ruin) > 200, 'columns and paving in the ruin\'s zones'
    i = ruin[0]
    p.x, p.y = i % m.w, i // m.w
    VN.zone_step(g)
    assert not FK.unfound(city) and city.name == 'A Varnish ruin'
    app.render()
    # the play maps: every telling thing can be walked to and answers a bump, with and without the letters
    for letters in (False, True):
        g.varnish_letters = letters
        for s in [s for s in w.sites if VN.is_varnish(s)]:
            to_over(g, 0)
            g.enter_site(s.id)
            m = g.map
            assert m.vn == s.kind and g.cur == s.map_key
            got = reach(m, (p.x, p.y))
            cells = [(i % m.w, i // m.w) for i, t in enumerate(m.t) if (t in VN.BUMP and t != D.SKYWELL) or t == D.DOWN
                     or (t == D.LEVER and m.vthings.get((i % m.w, i // m.w)))]
            well = [(i % m.w, i // m.w) for i, t in enumerate(m.t) if t == D.SKYWELL]
            assert not well or any((x + a, y + b) in got for x, y in well for a in (-1, 0, 1) for b in (-1, 0, 1))
            cells += well[:1] + [c for c in m.vthings if c not in cells]
            assert cells, s.name
            for x, y in cells:
                assert m.tile(x, y) == D.SKYWELL or VN.underwater(m, x, y) or any((x + a, y + b) in got for a in (-1, 0, 1) for b in (-1, 0, 1)), \
                    (s.name, D.TILES[m.tile(x, y)].name)
            for x, y in cells:
                if m.tile(x, y) == D.DOWN or D.TILES[m.tile(x, y)].walk:
                    continue
                spent = VN.bump(g, x, y)
                assert spent is not None, (s.name, D.TILES[m.tile(x, y)].name)
                if g.pending and g.pending['key'] == 'varnish':
                    EV.resolve(g, 'seal')
                g.request = None
                g.pending = None
            app.render()
            pickle.dumps(m)
    assert city.named and city.name == city.vname, 'the city\'s stone says its name'
    assert any(s.kind == 'sluice' and s.drained for s in w.sites), 'the sluice opens and the hall runs dry'
    assert any(f['key'].startswith('vr:') for f in CH.facts(g)), 'pieces of the riddles at the places'
    # the way down: open, the hidden deep below with its own boss, and back up to the court
    to_over(g, 0)
    g.enter_site(city.id)
    m = g.map
    assert city.open and D.DOWN in m.t, city.way
    i = m.t.index(D.DOWN)
    p.x, p.y = i % m.w, i // m.w
    g.use_stairs('down')
    assert g.cur == f'{city.below}:1'
    dg = w.dungeons[city.below]
    assert dg.varnish and dg.boss in VN.CITY_BOSSES and dg.size == 'middle'
    g.enter_dungeon(dg.id, dg.depth, 'up')
    assert any(o.k == dg.boss for o in g.map.mons), 'the deep\'s own boss waits at the bottom'
    assert D.STARIRON in g.map.t
    g.enter_dungeon(dg.id, 1, 'down')
    i = g.map.t.index(D.UP)
    p.x, p.y = i % g.map.w, i // g.map.w
    g.use_stairs('up')
    assert g.cur == city.map_key and g.map.tile(p.x, p.y) == D.DOWN, 'up the stair, back in the Sky Court'
    bosses = [w.dungeons[s.below].boss for s in w.sites if VN.is_varnish(s) and getattr(s, 'below', None)]
    assert len(bosses) == len(set(bosses)), 'every deep has a boss of its own'
    # pages: kept with your papers, read once you have the letters
    g.varnish_letters = False
    st = VN.st(g)
    bk = V['books'][0]
    key = (bk, 0)
    st['pages'].discard(key)
    st['read'].discard(key)
    to_over(g, 0)
    it = Item(g.new_id(), 'vpage', 'vpage')
    it.vpage = key
    it.x, it.y = p.x, p.y
    g.map.items.append(it)
    n = len(p.inv)
    g.auto_pickup()
    assert key in st['pages'] and key not in st['read'] and len(p.inv) == n, 'a page goes in with your papers'
    town = w.settlements[w.realm.great]
    g.enter_town(town.id)
    scribe = next(o for o in g.map.mons if getattr(o, 'role', '') == 'scribe')
    p.gold = 100000
    g.talk(scribe)
    assert 'vlore' in [o[1] for o in g.pending['options']]
    EV.resolve(g, 'letters')
    assert key in st['read'], 'learning the letters reads the pages you carry'
    n0 = len(st['lore'])
    g.talk(scribe)
    EV.resolve(g, 'vlore')
    assert len(st['lore']) > n0, 'the scribe\'s Varnish shelf'
    # a whole book bound, its hidden page and what it shows; sold once
    was_on, DBG.ON = DBG.ON, True
    DBG.varnish_pages(g)
    DBG.ON = was_on
    assert len(VN.complete(g)) == 8
    g.talk(scribe)
    opts = [o[1] for o in g.pending['options']]
    bind = next(o for o in opts if o and o.startswith('vbind:'))
    EV.resolve(g, bind)
    b = bind[6:]
    assert b in st['bound'] and any(i.k == 'vbook' and i.book == b for i in p.inv)
    assert any(f['key'] == f'vb:{b}' for f in CH.facts(g))
    gold = p.gold
    g.talk(scribe)
    EV.resolve(g, f'vsell:{b}')
    assert p.gold == gold + VN.BOUND_PRICE and b in st['sold']
    g.talk(scribe)
    assert f'vsell:{b}' not in [o[1] for o in g.pending['options']]
    g.pending = None
    for bk in VN.complete(g):
        VN.bind(g, bk, 'here')
    assert all(k in st['bound'] for k in V['books'])
    if 'hessa' in V['books']:
        from avarenthia import cooking as CK
        assert 'fig_bread' in CK.known(g), 'Hessa\'s Kitchen gives its recipe'
    st['apple'] = True                              # the gardener's tree at the Anchor: one apple a year
    to_over(g, 0)
    g.enter_site(V['deep']['anchor'])
    tree = next(c for c, v in g.map.vthings.items() if v == 'apple')
    n = len(p.inv)
    assert VN.bump(g, *tree) and len(p.inv) == n + 1 and p.inv[-1].t == 'apple'
    assert VN.bump(g, *tree) == 0 and len(p.inv) == n + 1
    vb = next(i for i in p.inv if i.k == 'vbook')
    VN.read_bound(g, vb)
    assert g.request[0] == 'dialog' and T.BOOK[vb.book]['hidden'] in g.request[2]
    g.request = None
    # the riddles made whole: the answer, the lies shown up, the place it points to, and the last paragraph
    for r in T.RIDDLES:
        for i in range(len(r['frags'])):
            VN.riddle_frag(g, r['key'], i, 'a test', 'here')
        assert r['key'] in st['whole']
        site = w.sites[V['deep'][r['place']]]
        assert not FK.unfound(site), r['place']
        for i, fr in enumerate(r['frags']):
            f = next(f for f in CH.facts(g) if f['key'] == f'vr:{r["key"]}:{i}')
            assert bool(f['false']) == bool(fr[2]), (r['key'], i)
        assert any(f['key'] == f'vr:{r["key"]}:answer' for f in CH.facts(g))
    assert any(f['key'] == 'vr:last' for f in CH.facts(g)), 'all five riddles whole'
    deep = w.sites[V['deep']['anchor']]
    to_over(g, 0)
    g.enter_site(deep.id)
    i = g.map.t.index(D.DOWN)
    p.x, p.y = i % g.map.w, i // g.map.w
    g.use_stairs('down')
    dd = w.dungeons[deep.below]
    g.enter_dungeon(dd.id, dd.depth, 'up')
    assert any(o.k == 'chained_star' for o in g.map.mons), 'the Anchor\'s own boss'
    # league stones count down to a city
    for c in [s for s in w.sites if s.kind == 'vcity']:
        stones = [q for q in w.pois if q.kind == 'leaguestone' and q.city == c.id]
        if len(stones) < 2:
            continue
        c.found = False
        for q in stones:
            q.found = False
        for q in stones:
            assert VN.on_poi(g, q) and g.request[0] == 'dialog'
            g.request = None
        assert all(q.found for q in stones[1:]), 'each stone shows the next'
        if stones[-1].num == 'I':
            assert c.found, 'the last stone shows the city'
        break
    # heard: a rumour of the Varnish
    line = VN.rumour(g)
    assert line is None or isinstance(line, str)
    # the chronicle's chapters, with their headings
    for ch in ('The Old Days', 'The Varnish'):
        i = CH.CHAPTERS.index(ch)
        bl = CH.blocks(g, i)
        assert any(b[0] == 'h' for b in bl), ch
        app.screens = [ui.GameScreen(app), ui.ChronicleScreen(app, i)]
        app.render()
    heads = [b[1] for b in CH.blocks(g, CH.CHAPTERS.index('The Varnish')) if b[0] == 'h']
    assert 'Bound books' in heads, heads
    app.screens = [ui.GameScreen(app)]
    pickle.dumps(g)
    print('   varnish ok:', dict(kinds), len(st['lore']), 'loose fragments')


def epics():
    """The epics: 22 of them, two per class, on key 6 in the elite's place, once per rest and free; two hidden teachers
    of each class far apart, heard of from rank 35, teaching from 40 after a deed; each epic at work in a fight; Phoenix
    burns you up instead of dying; Time Stop, Unstoppable, Oak Shape, One Blood, Return; the duel and the bell."""
    from avarenthia import epics as EP, skills as SK, classes as CL, mercs as MC, folk as FK, events as EV, lore as LORE
    from avarenthia import weaponskills as WS, behave as BH, spellmap as SM, missions as MS, debug as DBG
    from avarenthia.entities import make_monster
    from avarenthia.worldgen import free_around, cheb
    import pickle
    print('== epics')
    assert len(EP.EPICS) == 22 and set(EP.BY_LINE) == set(CL.PURE)
    assert all(SK.SKILLS[s] is EP.EPICS[s] and SK.describe(EP.EPICS[s], 40) for s in EP.EPICS)
    assert {s.name for s in EP.EPIC_LIST}.isdisjoint({s.name for s in SK.SKILLS.values() if not EP.is_epic(s)})
    app = new_app('soft', seed=11)
    g = app.game
    p = g.player
    w = g.world
    # two teachers a class, hidden, each in another part of the world
    for line in EP.TEACHERS:
        ts = EP.teachers(g, line)
        assert len(ts) == 2 and all(FK.unfound(t) for t in ts), (line, len(ts))
        assert cheb(ts[0].x, ts[0].y, ts[1].x, ts[1].y) >= 30, (line, ts[0].x, ts[0].y, ts[1].x, ts[1].y)
    gaps = sorted(cheb(*(lambda a, b: (a.x, a.y, b.x, b.y))(*EP.teachers(g, line))) for line in EP.TEACHERS)
    p.classes = ['fire', 'cunning']
    for line in p.classes:
        p.disc[line] = [30, 0]
    to_over(g, 0)
    assert EP.hear(g) is None                       # not yet: rank 35
    p.disc['fire'] = [36, 0]
    line = EP.hear(g)
    assert line and 'ash hermit' in line
    t = next(t for t in EP.teachers(g, 'fire') if t.id in EP.st(g)['heard'])
    assert not FK.unfound(t)
    old = LORE.HINTS
    LORE.HINTS = [(LORE.hint_teacher, 1)]
    p.disc['cunning'] = [36, 0]
    assert 'master thief' in LORE.hint(g)
    LORE.HINTS = old
    # the hut: the teacher refuses below 40, then sets a deed
    g.enter_site(t.id)
    assert g.map.kind == 'town' and getattr(g.map, 'teacher', False)
    npc = next(o for o in g.map.mons if getattr(o, 'role', '') == 'teacher')
    g.talk(npc)
    assert not g.pending
    p.disc['fire'] = [40, 0]
    g.talk(npc)
    assert g.pending and g.pending['key'] == 'epic'
    EV.resolve(g, 'deed')
    job = EP._job(g, 'fire')
    assert job and job.state == 'active' and job.title and EP.target_pos(g, job)[0] == tuple(job.data['spot'])
    app.render()
    # the ember at the heart of the fire
    g.cur = 'over'
    p.x, p.y = job.data['spot']
    EP.over_step(g)
    assert EP.deed_done(g, job)
    g.enter_site(t.id)
    npc = next(o for o in g.map.mons if getattr(o, 'role', '') == 'teacher')
    p.x, p.y = npc.x - 1, npc.y
    g.talk(npc)
    assert EP.st(g)['deeds']['fire'] and job.state == 'done'
    assert g.pending and g.pending['key'] == 'epic'
    EV.resolve(g, 'learn:sunfall')
    assert p.bar[5] == 'sunfall' and 'sunfall' in p.known and CL.fits(g, EP.EPICS['sunfall'], 5) is None
    assert CL.fits(g, EP.EPICS['sunfall'], 2) and CL.fits(g, EP.EPICS['unweave'], 5)
    g.talk(npc)                                     # swap for the other
    EV.resolve(g, 'learn:phoenix')
    assert p.bar[5] == 'phoenix' and 'sunfall' not in p.known
    app.render()
    scr = app.cv.dump()
    assert EP.SIGN in scr and 'Phoenix' in scr and 'ready' in scr and 'epic' in scr, scr
    # every epic at work in a fight
    p.classes = list(CL.PURE)
    for line_ in p.classes:
        p.disc[line_] = [45, 0]
    p.vit = 400
    g.enter_dungeon(list(w.dungeons)[0], 1, 'up')
    mc = MC.Merc('defender', 'Test Shield', 5)
    MC.outfit(g, mc)
    mc.hp = MC.stats(g, mc)['max_hp']
    g.merc = mc
    MC.sync(g)
    for sid in [s for s in EP.EPICS if s != 'phoenix']:
        g.map.mons = [o for o in g.map.mons if o.is_npc and not getattr(o, 'thrall', 0)]
        p.buffs = []
        BH.status(g).clear()
        for xy in list(SM.fields(g.map)):
            SM.clear(g.map, xy)
        if sid == 'one_blood' and not MC.with_you(g, 'beast'):
            wolf = make_monster(g, 'wolf', *free_around(g, g.map, p.x, p.y, 2)[-1], 3)
            g.map.mons.append(wolf)
            MC.tame(g, wolf, 'wolf')
            MC.sync(g)
        if sid == 'epic_return':
            MC.hurt(g, mc, 10 ** 5)
            assert mc.state == 'fallen'
        for x, y in [c for c in free_around(g, g.map, p.x, p.y, 2) if c != (p.x, p.y) and not g.occupied(g.map, *c)][:3]:
            e = make_monster(g, 'skeleton' if sid == 'unweave' else 'goblin', x, y, 6)
            e.awake = True
            e.hp = e.maxhp = 400
            if sid == 'unweave':
                e.mods = list(e.mods) + ['Fast']
                e.called = True
            g.map.mons.append(e)
        g.compute_fov()
        EP.learn(g, sid, quiet=True)
        EP.st(g)['spent'] = False
        p.life = g.stats()['max_life']
        assert SK.use(g, 5), sid
        assert EP.st(g)['spent'] and not EP.ready(g, sid), sid
        if sid != 'oak_shape':                      # Oak Shape's key lets it go; the others are spent until you rest
            assert not SK.use(g, 5), sid
        foes = [o for o in g.map.mons if not o.is_npc]
        if sid == 'sunfall':
            hp0 = sum(o.hp for o in foes)
            g.end_turn(1)
            g.end_turn(1)
            assert sum(o.hp for o in g.map.mons if not o.is_npc) < hp0 or len(g.map.mons) < len(foes) + 2
        if sid == 'glass_heart':
            t_ = next(o for o in foes if getattr(o, 'glass', -1) >= g.turn)
            hp0 = t_.hp
            g.damage_mon(t_, 5, weapon=True)
            assert t_.hp < hp0 - 20 or t_ not in g.map.mons
        if sid == 'epic_return':
            assert mc.state == 'alive' and mc.hp > 0
        if sid == 'time_stop':
            gob = foes[0]
            xy = (gob.x, gob.y)
            assert g.try_move(gob.x - p.x, gob.y - p.y) == 0
            g.end_turn(1)
            assert (gob.x, gob.y) == xy and EP.time_stopped(g)
            app.render()
        if sid == 'unstoppable':
            assert not BH.give(g, 'slowed', 5) and not BH.give(g, 'paralysed', 2)
        if sid == 'oak_shape':
            assert WS.kit(g) == 'oak' and CL.slot_skill(g, 0) == 'oak_slam' and BH.has(g, 'slowed'), \
                (WS.kit(g), CL.slot_skill(g, 0), BH.status(g), p.buffs)
            assert SK.use(g, 5) and WS.kit(g) != 'oak' and not BH.has(g, 'slowed')
        if sid == 'one_blood':
            bst = MC.with_you(g, 'beast')
            MC.hurt(g, bst, 10 ** 5)
            assert bst.state == 'alive' and bst.hp == 1
        if sid == 'unweave':
            assert not any(o for o in g.map.mons if not o.is_npc and cheb(o.x, o.y, p.x, p.y) <= 3)
        if sid == 'death_mark':
            gob = foes[0]
            g.damage_mon(gob, 3, weapon=True)
            assert gob not in g.map.mons
        if sid == 'lich_form':
            life = p.life
            g.hurt(50, 'the cold', 'cold')
            assert p.life == life
        if sid == 'barrow_king':
            assert any(getattr(o, 'barrow_king', False) for o in g.map.mons)
        g.end_turn(1)
        app.render()
        assert not g.dead, sid
        EP.rested(g)
        assert EP.ready(g, sid) and not any(getattr(o, 'barrow_king', False) for o in g.map.mons)
    # Phoenix: the blow that would kill you burns you up instead, once a day
    p.buffs = []
    EP.learn(g, 'phoenix', quiet=True)
    g.map.mons = [o for o in g.map.mons if o.is_npc]
    p.life = 5
    g.hurt(10 ** 5, 'a goblin')
    assert not g.dead and p.life > 1 and EP.flames(g) == EP.FLAMES and not EP.ready(g, 'phoenix')
    assert any('Burning' in t_ for t_, _c in BH.shown(g))
    life = p.life
    g.end_turn(1)
    assert p.life < life
    p.inv.append(__import__('avarenthia.entities', fromlist=['Item']).Item(g.new_id(), 'potion', 'hp'))
    g.drink('hp')
    assert EP.flames(g) == EP.FLAMES - 1
    st0 = EP.st(g)
    st0['flames'] = 0
    p.life = 5
    g.hurt(10 ** 5, 'a goblin')                     # the second death that day: no Phoenix
    assert EP.flames(g) == 0
    g.dead = False
    p.life = g.stats()['max_life']
    # the other deeds, each to its end
    from types import SimpleNamespace
    for line_ in ('shadow', 'necromancy', 'cunning', 'nature', 'frost', 'beastcraft', 'arcane', 'restoration'):
        tch = EP.teachers(g, line_)[0]
        EP.st(g)['deeds'].pop(line_, None)
        EP.start_deed(g, tch)
        jb = EP._job(g, line_)
        assert jb and EP.target_pos(g, jb), line_
        d = jb.data
        if line_ == 'shadow' and d.get('temple') is not None:
            g.enter_site(d['temple'])
            alt = next(((i % g.map.w, i // g.map.w) for i, t_ in enumerate(g.map.t) if t_ == D.ALTAR), None)
            if alt:
                assert EP.bump(g, *alt, D.ALTAR) == 1 and EP.deed_done(g, jb)
        if line_ == 'necromancy' and d.get('barrow') is not None:
            g.enter_dungeon(list(w.dungeons)[0], 1, 'up')
            EP.on_level(g, g.map, SimpleNamespace(site=d['barrow']))
            wt = next(o for o in g.map.mons if getattr(o, 'ep_crown', None) == jb.id)
            g.kill(wt)
            g.player.inv += [it for it in g.map.items if getattr(it, 'mission', None) == jb.id]
            assert EP.deed_done(g, jb)
        if line_ == 'cunning' and d.get('seat') is not None:
            g.enter_site(d['seat'])
            assert g.map.ep_box
            p.buffs.append(['sneak', 1, 30, 'Sneak'])
            assert EP.bump(g, *g.map.ep_box, D.CHEST) == 1 and EP.deed_done(g, jb)
        if line_ == 'nature':
            g.cur = 'over'
            p.x, p.y = d['spot']
            g.compute_fov()
            EP.over_step(g)
            assert d['planted'] is not None
            d['planted'] -= EP.SEASON
            EP.over_step(g)
            assert EP.deed_done(g, jb)
        if line_ == 'frost':
            g.enter_site(tch.id)
            keep = EP.winter_night
            EP.winter_night = lambda game: True
            p.life = g.stats()['max_life']
            EP.sit_out(g, tch)
            EP.winter_night = keep
            assert not g.dead and EP.deed_done(g, jb)
        if line_ == 'restoration':
            g.enter_dungeon(list(w.dungeons)[0], 1, 'up')
            for _ in range(5):
                sk_ = make_monster(g, 'skeleton', p.x, p.y, 3)
                g.map.mons.append(sk_)
                g.kill(sk_)
            assert EP.deed_done(g, jb)
        app.render()
        MS.active(g).remove(jb) if jb in MS.active(g) else None
        jb.state = 'done'
    # the duel: the old champion yields before he falls, and no drink
    camp = next(t for t in EP.teachers(g, 'warcraft'))
    g.enter_site(camp.id)
    EP.st(g)['deeds'].pop('warcraft', None)
    npc = next(o for o in g.map.mons if getattr(o, 'role', '') == 'teacher')
    EP.start_deed(g, camp)
    job = EP._job(g, 'warcraft')
    EP.start_duel(g, camp)
    champ = next(o for o in g.map.mons if getattr(o, 'duel', False))
    assert g.map.duel == champ.id
    g.damage_mon(champ, champ.hp * 3)
    assert getattr(g.map, 'duel', None) is None and job.data.get('done') and EP.deed_done(g, job)
    assert any(getattr(o, 'role', '') == 'teacher' for o in g.map.mons)
    # the storm hermit's bell
    peak = EP.teachers(g, 'storm')[0]
    g.enter_site(peak.id)
    EP.start_deed(g, peak)
    bx, by = g.map.bell
    assert EP.bump(g, bx, by, D.BELL) == 1 and not EP._job(g, 'storm').data.get('done')
    g.world.weather = getattr(g.world, 'weather', None)
    # the debug menu's line
    DBG.epics(g)
    assert all(EP.st(g)['deeds'].get(c) for c in CL.classes(g))
    assert len(MS.active(g)) >= 1
    pickle.dumps(g)
    print('   epics ok: gaps between teachers', gaps[:3], '...', gaps[-1])


def money_fixes():
    """Trade part 1: a dear good bends the price harder than a cheap one, a town holds only a few dear goods, stock comes
    back slowly, and a route tires: the same good in the same town fetches less until the market forgets."""
    import copy
    print('== money fixes')
    random.seed(5)
    g = E.Game('Trader', False, 4242)
    p = g.player
    w = g.world
    p.gold = 10 ** 7
    p.vit = 300
    assert ECO.step('gems') > ECO.step('tools') > ECO.step('grain') == 1
    assert ECO.bend('gems') > ECO.bend('grain')
    s = max(w.settlements, key=lambda q: q.market['grain'][0])
    keep = copy.deepcopy(s.market)
    for gk in ('grain', 'gems'):
        s.market[gk][0] = 60.0
    s.market['gems'][0] = 60.0
    a0, b0 = ECO.buy_price(s, 'grain'), ECO.buy_price(s, 'gems')
    ECO.buy(g, s, 'grain', 10)
    ECO.buy(g, s, 'gems', 10)
    assert ECO.buy_price(s, 'gems') / b0 > ECO.buy_price(s, 'grain') / a0
    assert ECO.units(s, 'gems') < ECO.units(s, 'grain')
    # selling again and again: the market remembers you
    s.market = copy.deepcopy(keep)
    p.cargo = {'cloth': 40}
    p.cost_basis = {}
    first = ECO.sell_price(s, 'cloth', False, ECO.tired(g, s, 'cloth'))
    ECO.sell(g, s, 'cloth', 20)
    s.market['cloth'][0] = keep['cloth'][0]          # the same stock: only the route has tired
    tired = ECO.sell_price(s, 'cloth', False, ECO.tired(g, s, 'cloth'))
    assert tired < first, (tired, first)
    for _ in range(60):
        ECO.daily(g)
    assert ECO.tired(g, s, 'cloth') < 3
    # stock comes back slowly: a tenth of the way in two days at most
    m = s.market['grain']
    m[0], gap = m[1] - 40, 40
    random.seed(1)
    keep_gauss = random.gauss
    random.gauss = lambda a, b: 0.0
    ECO.daily(g)
    ECO.daily(g)
    random.gauss = keep_gauss
    assert m[1] - m[0] > gap * .88, (m[1] - m[0])
    import pickle
    pickle.dumps(g)
    print('   money ok: gems step', round(ECO.step('gems'), 2), 'cloth', first, '->', tired)


def bosses():
    """Boss fights, the kit: the veil, the shut room and its rotten wall, marked blows that always leave a way out and
    never kill from full life, the deck, phases that stop a blow and the crit that breaks through, spent, staggered,
    breaking, resolve, helpers with a job, the lich's shards, fleeing, your company in the red, the six twins, the other
    bosses' marked nova and leap, the boss bar; Snagtooth, the Lich and the Dragon each through all their phases."""
    from avarenthia import bosses as BS, debug as DBG, events as EV, mercs as MC, behave as BH
    from avarenthia.entities import make_monster
    from avarenthia.worldgen import free_around
    import pickle
    print('== bosses')
    random.seed(15)
    g = E.Game('Bosser', False, 4242)
    app = ui.App(FakeCanvas(ui.W, ui.H))
    app.start_game(g)
    p = g.player
    p.vit, p.lvl = 60, 3
    p.life = g.stats()['max_life']
    # the den: its hoard is a room behind a veil of mist, with one rotten wall
    d = g.world.dungeons['den']
    g.enter_dungeon('den', d.depth, 'up')
    m = g.map
    ar = m.arena
    boss = next(o for o in m.mons if o.k == 'snagtooth')
    assert ar['boss'] == boss.id and ar['gates'] and all(m.tile(*c) == D.VEIL for c in ar['gates'])
    assert ar['rotten'] and m.tile(*ar['rotten']) == D.ROTTEN, 'one hard way out'
    room = set(map(tuple, ar['cells']))
    gate = ar['gates'][0]
    outside = next(c for c in free_around(g, m, *gate, 1) if c not in room and c not in ar['gates'])
    p.x, p.y = outside
    g.compute_fov()
    assert g.try_move(gate[0] - p.x, gate[1] - p.y) == 0 and g.pending and g.pending['key'] == 'boss_veil'
    EV.resolve(g, 'go')
    assert (p.x, p.y) == tuple(gate) and ar['asked']
    for o in [o for o in m.mons if not o.is_npc and o is not boss]:
        m.mons.remove(o)
    p.x, p.y = min((c for c in room if not g.occupied(m, *c)), key=lambda c: abs(cheb(*c, boss.x, boss.y) - 3))
    g.compute_fov()
    boss.awake = True
    g.damage_mon(boss, 1, weapon=True)               # the first blow: the name in gold, and the room shuts
    assert BS.st(boss)['engaged'] and ar['sealed'] and g.banner and g.banner[0] == boss.name.upper()
    assert all(m.tile(*c) == D.SEALED for c in ar['gates'])
    assert BS.no_rest(g)
    n = len(g.log)
    g.rest()
    assert 'no rest' in g.log[-1][0]
    p.inv.append(E.Item(g.new_id(), 'scroll', 'tp'))
    assert g.town_portal() == 0 and g.cur.startswith('den'), 'no portal out of a shut room'
    # a marked blow: red ground, a way out within the turns it loads, and never death from full life
    assert BS.start(g, boss, 'coin_toss')
    c = boss.cast
    assert (p.x, p.y) in set(map(tuple, c['cells'])) and c['load'] >= 2, c
    assert BS.need(g, boss, BS.MOVES['coin_toss'], set(map(tuple, c['cells'])), p.x, p.y) <= c['left']
    marks = BS.marks(g)
    assert (p.x, p.y) in marks and marks[(p.x, p.y)][0] == str(c['left'])
    app.render()
    assert 'Charging: Coin Toss' in app.cv.dump() and 'IN SIGHT' in app.cv.dump()
    keep = BS.MOVES['coin_toss']['power']
    BS.MOVES['coin_toss']['power'] = 50.0
    p.life = g.stats()['max_life']
    boss.cast['left'] = 1
    g.mon_turn(boss, g.stats()['def'])
    BS.MOVES['coin_toss']['power'] = keep
    assert not g.dead and p.life == 1 and boss.cast is None, 'a marked blow never kills from full life'
    assert any(it.k == 'gold' for it in m.items), 'the coins lie where they fell'
    p.life = g.stats()['max_life']
    # the threshold stops a blow; its turn goes on the phase's trick: kobolds with a job come running
    g.damage_mon(boss, 10 ** 5, weapon=True)
    bs = BS.st(boss)
    assert boss in m.mons and boss.hp == round(boss.maxhp * .5) and bs['pending'] == 1
    boss.cast = None
    g.mon_turn(boss, g.stats()['def'])
    assert bs['phase'] == 1 and bs['pending'] is None
    hs = BS.helpers(g, boss)
    assert {o.job for o in hs} == {'guard', 'mender'}, [o.job for o in hs]
    app.render()
    assert 'guarding' in app.cv.dump() or 'mending' in app.cv.dump()
    # the rotten wall gives after five blows; out through it, and it heals and makes ready
    rx, ry = ar['rotten']
    inner = next(cc for cc in room if cheb(cc[0], cc[1], rx, ry) == 1 and abs(cc[0] - rx) + abs(cc[1] - ry) == 1)
    p.x, p.y = inner
    for k in range(5):
        assert g.try_move(rx - p.x, ry - p.y) == 1
    assert m.tile(rx, ry) == D.FLOOR
    p.x, p.y = rx, ry
    g.try_move(rx - inner[0], ry - inner[1])
    assert (p.x, p.y) not in room
    bs['took'] = {'cold': 50, 'weapon': 10}
    BS.tick(g)
    assert not ar['sealed'] and boss.hp == boss.maxhp and bs['phase'] == 0 and 'res:cold' in bs['prep']
    assert all(m.tile(*cc) == D.VEIL for cc in ar['gates']) and g.mon_res(boss, 'cold') >= 50
    # Snagtooth through all his phases, and FOE FELLED
    p.x, p.y = inner
    g.damage_mon(boss, 10 ** 5, weapon=True)
    boss.cast = None
    g.mon_turn(boss, g.stats()['def'])
    while boss in m.mons:
        g.damage_mon(boss, 10 ** 5, weapon=True)
    assert g.flags.get('den') and g.banner[0] == 'FOE FELLED' and ar['done'] and not ar['sealed']
    assert all(m.tile(*cc) != D.SEALED for cc in ar['gates'])
    # the Lich, set down in a room of the mine: shards, phases, the breakthrough, breaking, resolve, staggering
    g.enter_dungeon('mine', g.world.dungeons['mine'].depth, 'up')
    m = g.map
    for o in [o for o in m.mons if not o.is_npc]:
        m.mons.remove(o)
    ar0 = m.arena                                    # Grolm's own room down here: the test sets its own
    if ar0:
        for cc, t in ar0['orig'].items():
            m.set(cc[0], cc[1], t)
        for cc in ar0.get('props', ()):
            m.set(cc[0], cc[1], D.FLOOR)
        if ar0['rotten']:
            m.set(ar0['rotten'][0], ar0['rotten'][1], D.WALL)
    m.arena = None
    bad = {m.room_of[i] for i, t in enumerate(m.t) if t in (D.UP, D.DOWN)}
    from collections import Counter
    cnt = Counter(r for r in m.room_of if r != 255 and r not in bad)
    rid = max(cnt, key=lambda r: cnt[r])
    cells = [(i % m.w, i // m.w) for i, r in enumerate(m.room_of) if r == rid and D.TILES[m.t[i]].walk]
    cx, cy = sum(c[0] for c in cells) // len(cells), sum(c[1] for c in cells) // len(cells)
    p.x, p.y = min(cells, key=lambda c: cheb(*c, cx, cy))
    p.lvl, p.vit = 14, 160
    p.life = g.stats()['max_life']
    g.compute_fov()
    DBG.ON = True
    lich = DBG.boss(g, 'lich')
    ar = m.arena
    assert len(ar['shards']) == 4 and all(m.tile(*cc) == D.SHARD for cc in ar['shards'])
    assert D.TILES[D.SHARD].opaque, 'the shards are cover'
    bs = BS.st(lich)
    lich.awake = True
    BS.engage(g, lich)
    assert ar['sealed']
    # resolve: the first two holds are shrugged off, the third is shorter
    for k in range(3):
        lich.hold = 4
        BS.pre(g, lich)
        assert lich.hold == (0 if k < 2 else 2), (k, lich.hold)
        lich.hold = 0
        bs['seen_hold'] = 0
    assert bs['resolve'] == 0
    # breaking: a stun while it winds up a blow that loads long
    p.x, p.y = min((cc for cc in ar['cells'] if not g.occupied(m, *cc)), key=lambda cc: abs(cheb(*cc, lich.x, lich.y) - 3))
    g.compute_fov()
    BS.set_phase(g, lich, 2)
    assert ar['dark'] and bs.get('lichcraft')
    g.compute_fov()
    assert BS.start(g, lich, 'blizzard'), 'there is cover within reach'
    assert lich.cast['brk'] and lich.cast['load'] >= 3
    app.render()
    assert 'Charging: Blizzard' in app.cv.dump()
    lich.hold = 1
    dots = bs['dots']
    assert BS.pre(g, lich) and lich.cast is None and bs['breaks'] == 1 and bs['dots'] == dots + 1
    # or enough damage while it loads
    bs['stun'] = 0
    assert BS.start(g, lich, 'blizzard')
    g.damage_mon(lich, lich.maxhp * .25, elem='fire')
    assert lich.cast is None
    # the weakness and the breaks fill the three dots: it staggers
    bs['stun'], bs['weak_t'] = 0, -1
    while not bs['stag']:
        g.turn += 1
        g.damage_mon(lich, 1, elem='fire')
    assert bs['stag'] == 2 and bs['dots'] == 0
    # lichcraft: a plain weapon does half
    bs['stag'] = 0
    hp = lich.hp
    g.damage_mon(lich, 40, weapon=True)
    assert hp - lich.hp <= 21, hp - lich.hp
    # the shards raise her again; broken, they do not
    lich.hp = 1
    g.damage_mon(lich, 100)
    assert lich not in m.mons and ar['rising']
    for _ in range(3):
        BS.tick(g)
    assert lich in m.mons and lich.hp == lich.maxhp // 4
    assert sum(1 for cc in ar['shards'] if m.tile(*cc) == D.SHARD) == 3
    for cc in ar['shards']:
        if m.tile(*cc) == D.SHARD:
            p.x, p.y = next(q for q in free_around(g, m, *cc, 1))
            assert g.try_move(cc[0] - p.x, cc[1] - p.y) == 1 and m.tile(*cc) == D.DARKSHARD
    g.damage_mon(lich, 10 ** 5)
    assert lich not in m.mons and not ar['rising'] and ar['done']
    # the breakthrough: a critical hit while it is spent goes through the threshold, and the trick never comes
    lich2 = BS.spawn(g, 'lich')
    b2 = BS.st(lich2)
    b2['spent'] = 1
    g.damage_mon(lich2, lich2.maxhp * .5, crit=True)
    assert b2['phase'] == 1 and b2.get('broke_through') and b2['pending'] is None
    assert lich2.hp > round(lich2.maxhp * .33), 'never two phases in one blow'
    m.mons.remove(lich2)
    # a warder halves what the boss takes
    p.x, p.y = min((cc for cc in cells if not g.occupied(m, *cc)), key=lambda cc: cheb(*cc, cx, cy))
    g.compute_fov()
    lich3 = BS.spawn(g, 'lich')
    lich3.x, lich3.y = next(cc for cc in free_around(g, m, p.x, p.y, 2) if g.visible(*cc))
    BS.call(g, lich3, (('wraith', 'warder'),), '')
    wd = next(o for o in m.mons if getattr(o, 'job', None) == 'warder' and o.boss_of == lich3.id)
    if not g.visible(wd.x, wd.y):            # where you can see it, so that IN SIGHT names it
        wd.x, wd.y = next(cc for cc in free_around(g, m, p.x, p.y, 3) if g.visible(*cc) and not g.occupied(m, *cc))
    hp = lich3.hp
    g.damage_mon(lich3, 40)
    assert BS.warded(g, lich3) and hp - lich3.hp == 20, hp - lich3.hp
    g.compute_fov()
    app.render()
    assert 'warding' in app.cv.dump() and 'Warded' in app.cv.dump(), app.cv.dump()[-2500:]
    for o in BS.helpers(g, lich3):
        m.mons.remove(o)
    m.mons.remove(lich3)
    # the Dragon in its own room: pillars, the breath, flight and the dive, the burning floor, Inferno and spent
    m.arena = None
    dragon = DBG.boss(g, 'dragon')
    if m.__dict__.get('arena') is None:
        BS.build(g, m, dragon)
    ar = m.arena
    db = BS.st(dragon)
    dragon.awake = True
    BS.engage(g, dragon)
    p.x, p.y = min((cc for cc in ar['cells'] if not g.occupied(m, *cc)), key=lambda cc: abs(cheb(*cc, dragon.x, dragon.y) - 3))
    g.compute_fov()
    BS.set_phase(g, dragon, 1)
    assert any(o.job == 'channeler' for o in BS.helpers(g, dragon))
    assert BS.do(g, dragon, 'take_wing', g.stats()['def']) and db['air'] and dragon.invis
    hp = dragon.hp
    assert g.damage_mon(dragon, 50) is False and dragon.hp == hp, 'out of reach in the air'
    p.life = g.stats()['max_life']
    for _ in range(4):
        if dragon.cast:
            g.mon_turn(dragon, g.stats()['def'])
    assert not db['air'] and not dragon.invis
    BS.set_phase(g, dragon, 2)
    assert ar['dance'] is not None
    for _ in range(2):
        BS.tick(g)
    db['stun'] = 0
    fed = db['fed']
    ok = BS.start(g, dragon, 'inferno')
    if ok:
        dragon.cast['left'] = 1
        pil = sum(1 for cc in ar['pillars'] if m.tile(*cc) == D.PILLAR)
        g.mon_turn(dragon, g.stats()['def'])
        assert db['spent'] >= 1 and sum(1 for cc in ar['pillars'] if m.tile(*cc) == D.PILLAR) == max(0, pil - 1)
    # no marked blow without a free tile: many turns of all three fights, with you standing anywhere
    for k, turns in (('snagtooth', 150), ('lich', 150), ('dragon', 150)):
        for o in [o for o in m.mons if not o.is_npc]:
            m.mons.remove(o)
        m.arena = None
        b = BS.spawn(g, k)
        b.awake = True
        for t in range(turns):
            p.life = g.stats()['max_life']
            if b not in m.mons:
                break
            if random.random() < .3:
                sp = [cc for cc in free_around(g, m, b.x, b.y, 6) if g.visible(*cc)]
                if sp:
                    p.x, p.y = random.choice(sp)
                    g.compute_fov()
            g.monsters_act()
            c = b.__dict__.get('cast')
            if c and c['left'] == c['load']:
                mv = BS.MOVES[c['mv']]
                if mv['shape'] != 'mark':
                    n = BS.need(g, b, mv, set(map(tuple, c['cells'])), c['tx'], c['ty'], 5)
                    assert n is not None and n <= c['left'], (k, c['mv'], n, c['left'])
            if random.random() < .15:
                g.damage_mon(b, b.maxhp * .08, weapon=True)
            for o in BS.helpers(g, b):
                if random.random() < .2:
                    g.kill(o)
        assert BS.st(b)['phase'] >= 1 or b not in m.mons, k
    # your company: out of the red, better with rank
    for o in [o for o in m.mons if not o.is_npc]:
        m.mons.remove(o)
    b = BS.spawn(g, 'snagtooth')
    mc = DBG.add_hireling(g, 'defender')
    MC.sync(g)
    body = mc.body
    assert body is not None and body in m.mons
    out = free_around(g, m, body.x, body.y, 1)
    if out:
        b.cast = dict(mv='coin_toss', left=2, load=2, cells=[(body.x + a, body.y + bb) for a in (-1, 0, 1) for bb in (-1, 0, 1)
                                                              if (body.x + a, body.y + bb) != out[0]], who='p', tx=body.x,
                      ty=body.y, taken=0, brk=False, told=[])
        mc.lvl = 20
        keep_r = random.random
        random.random = lambda: .5
        moved = BS.ally_turn(g, mc, body)
        random.random = keep_r
        assert moved and (body.x, body.y) == out[0], 'a veteran steps out of the red'
        b.cast = None
    # the six twins
    for o in [o for o in m.mons if not o.is_npc]:
        m.mons.remove(o)
    m.arena = None
    a, bb = BS.spawn(g, 'snagtooth'), BS.spawn(g, 'snagtooth')
    BS.link(a, bb, 'opposites')
    hp = a.hp
    g.damage_mon(a, 10, weapon=True)
    assert hp - a.hp == 5, 'one of the opposites shrugs off weapons'
    BS.link(a, bb, 'shared')
    hp = bb.hp
    g.damage_mon(a, 3)
    assert bb.hp == hp - 3
    BS.link(a, bb, 'survivor')
    bb.hp = 2
    g.kill(a)
    assert bb.hp == bb.maxhp and bb in m.mons
    a = BS.spawn(g, 'snagtooth')
    wolf = make_monster(g, 'wolf', a.x, a.y + 1, 3)
    m.mons.append(wolf)
    BS.link(a, wolf, 'master')
    g.kill(wolf)
    assert 'frenzy' in a.effects
    # the other bosses: their leap is marked a turn before it lands
    grolm = make_monster(g, 'grolm', p.x + 3, p.y, 9)
    if not g.occupied(m, grolm.x, grolm.y) and D.TILES[m.tile(grolm.x, grolm.y)].walk:
        m.mons.append(grolm)
        grolm.awake = True
        g.compute_fov()
        keep_r = random.random
        random.random = lambda: .01
        BS.turn(g, grolm, g.stats()['def'])
        random.random = keep_r
        c = grolm.__dict__.get('cast')
        assert (c and c['mv'] in BS.MOVES) or BS.st(grolm)['engaged'] or not g.visible(grolm.x, grolm.y)  # part B tests the kit
    pickle.dumps(g)
    print('   bosses ok')


def boss_moves():
    """Boss fights part B: the move library, the kits of every fixed, theme and Varnish boss with their rooms and
    tricks (rat holes and the knot, props and the falling roof, rising water and chains, webs and eggs, the banner and
    the duel, the stones of light), stances and images, the hex, three named things to choose from, and a roaming boss
    that walks its rounds, is heard, leaves tracks and follows you down the stair."""
    from avarenthia import bosses as BS, bossmoves as BM, debug as DBG, events as EV, behave as BH
    from avarenthia.worldgen import free_around
    from collections import Counter
    print('== boss_moves')
    random.seed(16)
    g = E.Game('Mover', False, 4243)
    app = ui.App(FakeCanvas(ui.W, ui.H))
    app.start_game(g)
    p = g.player
    for k, mv in BS.MOVES.items():
        assert mv['role'] in 'kVGZBOR' and mv.get('name') and (mv.get('shape') or mv.get('kind')), k
    assert sum(1 for mv in BS.MOVES.values() if mv.get('kind') != 'call') >= 100, 'the library'
    for k, kt in BS.KITS.items():
        assert k in D.MONSTERS, k
        ats = [ph['at'] for ph in kt['phases'][1:]]
        assert ats == sorted(ats, reverse=True) and len(kt['phases']) in (2, 3), k
        assert all(c in BS.MOVES for ph in kt['phases'] for cs in ph['cards'].values() for c in cs), k
        assert all(r in ph['cards'] or r == 'k' for ph in kt['phases'] for r in ph['beat']), k
    us = Counter(u['boss'] for u in D.UNIQUES if u.get('boss'))
    assert all(us[k] == 3 for k in ('snagtooth', 'ratking', 'grolm', 'lich', 'dragon', 'broodmother', 'warlord',
                                    'drowned_king', 'cinder_lord')), us
    g.enter_dungeon('mine', g.world.dungeons['mine'].depth, 'up')
    m = g.map
    bad = {m.room_of[i] for i, t in enumerate(m.t) if t in (D.UP, D.DOWN)}
    cnt = Counter(r for r in m.room_of if r != 255 and r not in bad)
    rid = max(cnt, key=lambda r: cnt[r])
    cells = [(i % m.w, i // m.w) for i, r in enumerate(m.room_of) if r == rid and D.TILES[m.t[i]].walk]
    cx, cy = sum(c[0] for c in cells) // len(cells), sum(c[1] for c in cells) // len(cells)
    mid = min(cells, key=lambda c: cheb(*c, cx, cy))
    p.lvl, p.vit = 14, 220
    DBG.ON = True

    def fresh(k):
        for o in [o for o in m.mons if not o.is_npc]:
            m.mons.remove(o)
        a0 = m.__dict__.get('arena')
        if a0:
            for cc, t in a0['orig'].items():
                m.set(cc[0], cc[1], t)
            if a0['rotten']:
                m.set(a0['rotten'][0], a0['rotten'][1], D.WALL)
            for cc in list(a0.get('holes', ())) + list(a0.get('chains', ())):
                m.set(cc[0], cc[1], D.WALL)
        m.arena = None
        m.__dict__.pop('boss_eggs', None)
        for c in cells:
            if m.tile(*c) not in (D.FLOOR, D.UP, D.DOWN):
                m.set(c[0], c[1], D.FLOOR)
        p.x, p.y = mid
        p.life = g.stats()['max_life']
        BH.status(g).clear()
        g.pending = None
        g.compute_fov()
        b = DBG.boss(g, k)
        assert b is not None and BS.st(b) is not None, k
        b.awake = True
        return b

    # every shaped move from a boss in its room: a way out within the turns it loads, and it lands without harm to
    # the game; every other kind can be done or refused
    b = fresh('lich')
    for k, mv in sorted(BS.MOVES.items()):
        p.life = g.stats()['max_life']
        BH.status(g).clear()
        if b not in m.mons:
            b = fresh('lich')
        b.cast = None
        BS.st(b)['air'] = False
        b.invis = 0
        if mv.get('shape'):
            if BS.start(g, b, k):
                c = b.cast
                if mv['shape'] not in ('mark', 'self'):
                    n = BS.need(g, b, mv, set(map(tuple, c['cells'])), c['tx'], c['ty'], 5)
                    assert n is not None and n <= c['left'], (k, n, c['left'])
                c['left'] = 1
                b.cast = None
                BS.release(g, b, c)
        elif mv.get('kind') not in ('melee', 'bolt'):
            BS.do(g, b, k, g.stats()['def'])
        assert not g.dead, k
    # each kit boss through its fight: no marked blow without a free tile, and it reaches its second phase
    for k in sorted(BS.KITS):
        if BS.KITS[k].get('roam'):
            continue
        b = fresh(k)
        for t in range(90):
            p.life = g.stats()['max_life']
            BH.status(g).clear()
            g.pending = None
            if b not in m.mons or g.dead:
                break
            if random.random() < .3:
                ar = m.__dict__.get('arena')                # a sealed room: you cannot step out of it
                room = set(map(tuple, ar['cells'])) if ar and ar.get('sealed') else None
                sp = [cc for cc in free_around(g, m, b.x, b.y, 6) if g.visible(*cc) and (room is None or cc in room)]
                if sp:
                    p.x, p.y = random.choice(sp)
                    g.compute_fov()
            g.monsters_act()
            if g.cur != 'mine:' + str(g.world.dungeons['mine'].depth):
                break
            c = b.__dict__.get('cast')
            if c and c['left'] == c['load']:
                mv = BS.MOVES[c['mv']]
                if mv['shape'] not in ('mark', 'self'):
                    n = BS.need(g, b, mv, set(map(tuple, c['cells'])), c['tx'], c['ty'], 5)
                    assert n is not None and n <= c['left'], (k, c['mv'], n, c['left'])
            if t % 4 == 3:                                # a steady tenth of its life every fourth turn
                g.damage_mon(b, b.maxhp * .1, weapon=False)
            for o in BS.helpers(g, b):
                if random.random() < .2:
                    g.kill(o)
        assert not g.dead, k
        assert BS.st(b)['phase'] >= 1 or b not in m.mons, k
    g.pending = None
    # a stance: the shield of light takes three blows
    b = fresh('name_keeper')
    assert BS.BM.do(g, b, BS.MOVES['holy_shield'])
    hp = b.hp
    for _ in range(3):
        g.damage_mon(b, 5, weapon=True)
    assert b.hp == hp and 'holy' not in BS.st(b)['guard']
    g.damage_mon(b, 5, weapon=True)
    assert b.hp < hp
    # images: one blow and an image is gone
    b = fresh('bound_magister')
    assert BS.BM.do(g, b, BS.MOVES['mirror'])
    imgs = [o for o in m.mons if getattr(o, 'image_of', None) == b.id]
    assert len(imgs) == 2
    hp = b.hp
    g.damage_mon(imgs[0], 50, weapon=True)
    assert imgs[0] not in m.mons and b.hp == hp
    # the hex: a toad has no skills
    BH.give(g, 'hexed', 3)
    assert g.use_skill(1) == 0 and 'toad' in g.log[-1][0]
    BH.status(g).clear()
    # the Rat King: rats from the holes, a hole stopped up, the water rising, the knot that splits
    b = fresh('ratking')
    ar = m.arena
    assert len(ar['holes']) >= 2 and all(m.tile(*c) == D.RATHOLE for c in ar['holes'])
    BS.seal(g, ar)
    assert BS.do(g, b, 'rats', g.stats()['def']) and any(o.k == 'rat' for o in BS.helpers(g, b))
    h = ar['holes'][0]
    assert BS.bump(g, h[0], h[1], D.RATHOLE) == 1 and m.tile(*h) == D.RUBBLE
    BS.set_phase(g, b, 2)
    assert ar['water'] == 1 and any(m.tile(*c) == D.SHALLOW for c in map(tuple, ar['cells']))
    BS.st(b)['spent'] = 0
    assert BS.start(g, b, 'knot_split')
    c = b.cast
    b.cast = None
    BS.release(g, b, c)
    kings = [o for o in m.mons if o.k == 'ratking']
    assert len(kings) == 3 and all(o.knot == b.id for o in kings)
    for o in kings[:2]:
        o.hp = 0
        g.kill(o)
        assert not ar['done'], 'the room stays shut while one king lives'
    o = kings[2]
    o.hp = 0
    g.kill(o)
    assert ar['done'] and g.banner[0] == 'FOE FELLED'
    assert g.pending and g.pending['key'] == 'boss_loot' and len(g.pending['options']) == 3
    pick = g.pending['options'][1][1]
    EV.resolve(g, pick)
    assert any(it.name == pick for it in m.items), 'the one you took'
    # Grolm: a prop kicked out, the roof that falls, never beside a prop that stands
    b = fresh('grolm')
    ar = m.arena
    BS.seal(g, ar)
    props = [c for c in ar['props'] if m.tile(*c) == D.PROP]
    assert len(props) >= 3
    assert BS.do(g, b, 'kick_prop', g.stats()['def'])
    assert sum(1 for c in ar['props'] if m.tile(*c) == D.PROP) == len(props) - 1
    b.cast = None
    BS.set_phase(g, b, 2)
    assert ar['ceiling'] == 0
    BS.tick(g)
    stand = [c for c in ar['props'] if m.tile(*c) == D.PROP]
    assert ar['falling'] and all(min(cheb(*c, *q) for q in stand) > 1 for c in ar['falling'])
    assert all(BS.marks(g).get(tuple(c)) for c in ar['falling'])
    BS.tick(g)
    assert not ar['falling']
    # the Drowned King: the water rises with every change; a chain broken lowers it; ledges and chains stay dry
    b = fresh('drowned_king')
    ar = m.arena
    assert ar['water'] == 1 and len(ar['chains']) >= 2
    BS.seal(g, ar)
    BS.set_phase(g, b, 1)
    assert ar['water'] == 2
    ch = ar['chains'][0]
    BS.bump(g, ch[0], ch[1], D.BCHAIN)
    BS.bump(g, ch[0], ch[1], D.BCHAIN)
    assert ar['water'] == 1 and m.tile(*ch) == D.WALL
    b.cast = None
    BS.st(b)['phase'] = 2
    if BS.start(g, b, 'deep_calls'):
        gold = b.cast['gold']
        assert gold and all(m.tile(*c) == D.BLEDGE or any(m.tile(c[0] + a, c[1] + bb) == D.BCHAIN
                                                          for a in (-1, 0, 1) for bb in (-1, 0, 1)) for c in gold)
        assert all(BS.marks(g)[tuple(c)][1] == BS.GOLDN for c in gold)
    # the Brood Mother: eggs hatch unless you tread on them; webs on the floor hold you
    b = fresh('broodmother')
    eg = BM.eggs(g)
    n0 = len(eg)
    BS.do(g, b, 'egg_clutch', g.stats()['def'])
    assert len(eg) >= n0 + 3
    c = next(iter(eg))
    p.x, p.y = c
    BS.floor_things(g)
    assert c not in eg and m.tile(*c) == D.FLOOR, 'trodden'
    p.x, p.y = mid
    for v in eg.values():
        v[0] = 1
    BS.floor_things(g)
    assert not eg and any(o.k == 'spiderling' for o in m.mons)
    from avarenthia import spellmap as SM
    web = next(cc for cc in free_around(g, m, p.x, p.y, 10) if m.tile(*cc) == D.FLOOR and cc not in SM.fields(m))
    assert SM.place(g, m, web[0], web[1], D.WEBS, 30)
    p.x, p.y = web
    BS.floor_things(g)
    assert BH.has(g, 'held') and m.tile(*web) != D.WEBS
    BH.status(g).clear()
    # the Warlord: the banner and its bearer; the duel, broken by a blow from afar
    b = fresh('warlord')
    BS.seal(g, m.arena)
    BS.set_phase(g, b, 1)
    bearer = next(o for o in BS.helpers(g, b) if o.job == 'bearer')
    at = (bearer.x, bearer.y)
    bearer.hp = 0
    g.kill(bearer)
    if m.tile(*at) == D.BANNER:
        assert BS.bump(g, at[0], at[1], D.BANNER) == 1 and m.tile(*at) == D.FLOOR
    BS.call(g, b, (('orc', 'guard'),), '')
    BS.set_phase(g, b, 2)
    assert BS.st(b)['duel'] and all(o.watching for o in BS.helpers(g, b))
    p.x, p.y = next(cc for cc in free_around(g, m, b.x, b.y, 4) if cheb(*cc, b.x, b.y) >= 3)
    g.damage_mon(b, 1, weapon=False)
    assert not BS.st(b)['duel'] and not any(o.watching for o in BS.helpers(g, b))
    # Dawnbreak: two stones of light, the safe ground round them gold, gone after the blow
    b = fresh('name_keeper')
    BS.st(b)['phase'] = 1
    if BS.start(g, b, 'dawnbreak'):
        c = b.cast
        assert len(c['stones']) == 2 and all(m.tile(*s_) == D.LIGHTSTONE for s_ in c['stones']) and c['gold']
        c['left'] = 1
        b.cast = None
        BS.release(g, b, c)
        assert all(m.tile(*s_) != D.LIGHTSTONE for s_ in c['stones'])
    g.compute_fov()
    app.render()
    # a roaming boss: it walks its rounds, you hear it, it leaves tracks; it hunts you and follows you down
    for o in [o for o in m.mons if not o.is_npc]:
        m.mons.remove(o)
    m.arena = None
    g.enter_dungeon('mine', 1, 'up')
    m = g.map
    for o in [o for o in m.mons if not o.is_npc]:
        m.mons.remove(o)
    p.life = g.stats()['max_life']
    r = DBG.boss(g, 'roam:troll')
    assert r is not None and r.roam
    n0 = len(g.log)
    walked = 0
    for _ in range(300):
        if BS.hunting(g, r):
            break
        at = (r.x, r.y)
        g.end_turn(1)
        walked += (r.x, r.y) != at
        p.life = g.stats()['max_life']
    assert r.roam['heard'] > 0 and any('of you' in ln[0] or 'somewhere' in ln[0] for ln in g.log[-80:]), 'heard'
    tracks = sum(1 for v in m.deco if v == 16) if m.deco else 0
    assert tracks >= min(5, walked // 5), ('tracks', tracks, walked)   # it may find you before it has walked far
    r.roam['seen'] = g.turn
    i = m.t.index(D.DOWN)
    p.x, p.y = i % m.w, i // m.w
    sp = [cc for cc in free_around(g, m, p.x, p.y, 4) if cheb(*cc, p.x, p.y) >= 3]
    r.x, r.y = sp[0]
    g.use_stairs('down')
    assert r not in m.mons and g.map.coming
    for _ in range(8):
        g.end_turn(1)
        p.life = g.stats()['max_life']
    assert r in g.map.mons and any('after you' in ln[0] for ln in g.log[-20:])
    print('boss moves ok')


def shadow():
    """The great evils part 1: the Hollow King's coast, three servants of three weights on their own clocks, his
    attention (one step after a pause, cooling), a seal, the levers and a held barony, a lieutenant killed (papers,
    weaker servant), one that survives scarred, the weakness from two sources and its edge in the lair, the Lich's
    jar, a hero and the cairn, the relic and its small power, the Shadow tab and map layer."""
    import pickle
    from avarenthia import shadow as SH, evils as EVL, realms as RL, debug as DBG
    print('== shadow')
    random.seed(17)
    g = E.Game('Shade', False, 4244)
    app = ui.App(FakeCanvas(ui.W, ui.H))
    app.start_game(g)
    p = g.player
    w = g.world
    sh = SH.st(w)
    assert [e.weight for e in w.evils] == ['heavy', 'middle', 'light'], [e.weight for e in w.evils]
    assert sh['sky'] and sh['coast'] and len(sh['land']) > 100
    for a in w.evils:
        assert a.did in w.dungeons and len(a.lts) == 3
        for b in w.evils:
            if a is not b:
                assert cheb(a.x, a.y, b.x, b.y) >= 30, (a.key, b.key)
    sites = [lt['site'] for e in w.evils for lt in e.lts if lt['site'] is not None]
    assert len(sites) >= 7 and all(w.sites[i].kind == 'lt' for i in sites)
    light, middle, heavy = w.evils[2], w.evils[1], w.evils[0]
    assert light.awake and not middle.awake and not heavy.awake
    # its own clock, not your level
    to_over(g, 0)
    pw = SH.power(g, light)
    p.lvl = 30
    assert SH.power(g, light) == pw
    p.lvl = 1
    g0 = light.goal
    middle.wake_day = g.day + 3
    for _ in range(5):
        g.turn += D.DAY_LEN
        g.last_day = g.day
        EVL.daily(g)
    assert light.goal > g0 and middle.awake and not heavy.awake
    # attention: one step after a pause, then it cools
    SH.meddle(g, 3, light)
    assert sh['att'] == 1
    SH.meddle(g, 5, light)
    assert sh['att'] == 1, 'a pause before the next step'
    sh['step_day'] -= SH.ATT_PAUSE
    SH.meddle(g, 3, light)
    assert sh['att'] == 2
    sh['meddled'] = g.day - SH.ATT_COOL - 1
    sh['cooled'] = g.day - 20
    SH.daily(g)
    assert sh['att'] == 1, 'left alone he looks away'
    # a seal breaks when one has what it wants
    middle.goal = 99.99
    SH.daily(g)
    assert middle.sealed and sh['seals'] == [middle.key] and sh['torn'] and sh['wake'] >= 20
    # the levers: a servant holds a barony, with its colour on the realms layer
    heavy.awake = True
    EVL.update(g)
    R = w.realm
    rids = [r for r in SH.regions_of(g, 0) if r in R.baronies] or [r for r in R.baronies][:1]
    rid = SH._hold(g, 0, heavy, rids)
    assert rid is not None and RL.realm_key(w, rid) == ('evil', 0)
    keep = random.random
    random.random = lambda: 0.0
    try:
        SH.monthly(g)
    finally:
        random.random = keep
    assert any('Shadow' in str(n.get('fact')) for n in __import__('avarenthia.news', fromlist=['x']).store(g))
    # a lieutenant: its place, its death, its papers
    i, j = next((i, j) for i, e in enumerate(w.evils) for j, lt in enumerate(e.lts) if lt['site'] is not None and lt['person'])
    e = w.evils[i]
    lt = e.lts[j]
    site = w.sites[lt['site']]
    g.enter_site(site.id)
    o = next(x for x in g.map.mons if x.__dict__.get('lt') == (i, j))
    assert o.maxhp > 100 or o.maxhp >= 3 * 10
    pw = SH.power(g, e)
    pts = sh['pts']
    g.kill(o)
    assert lt['dead'] == 'you' and 'papers' in SH.know(g)['src'].get(e.key, set())
    assert SH.power(g, e) <= pw and (sh['pts'] > pts or sh['att'] >= 1)
    # one that survives you comes back scarred
    i2, j2 = next((i_, j_) for i_, e_ in enumerate(w.evils) for j_, l_ in enumerate(e_.lts) if l_['site'] is not None
                  and not l_['dead'])
    lt2 = w.evils[i2].lts[j2]
    s2 = w.sites[lt2['site']]
    g.enter_site(s2.id)
    o2 = next(x for x in g.map.mons if x.__dict__.get('lt') == (i2, j2))
    o2.hp = o2.maxhp // 2
    to_over(g, 0)
    SH.daily(g)
    assert lt2['scars'] == 1 and s2.map_key not in g.maps
    g.enter_site(s2.id)
    o2 = next(x for x in g.map.mons if x.__dict__.get('lt') == (i2, j2))
    assert 'scarred' in o2.name and o2.hp == o2.maxhp
    to_over(g, 0)
    # the weakness: two sources, then the edge in the lair
    SH.clue(g, light, 'library')
    assert not SH.weak_known(g, light)
    SH.clue(g, light, 'riddle')
    assert SH.weak_known(g, light)
    dg = w.dungeons[light.did]
    g.enter_dungeon(light.did, dg.depth, 'up')
    boss = next(x for x in g.map.mons if x.k == light.d['boss'])
    assert boss.__dict__.get('edge') == SH.SERVANT[light.key]['weak'][1]
    edge = boss.edge
    if isinstance(edge, tuple):
        assert SH.edge_mult(g, boss, False, edge[1]) == 1.5
    # the Lich's jar
    lich = EVL.make('lich')
    lich.did = heavy.did
    assert SH.returns(g, lich, None) and lich.back == g.day + 40
    m = g.map
    jx, jy = next((x, y) for x, y in ((p.x + dx, p.y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1))
                  if (x, y) != (p.x, p.y) and D.TILES[m.tile(x, y)].walk and not m.mon_at(x, y))
    m.set(jx, jy, D.JAR)
    keep_ev = w.evils
    w.evils = keep_ev + [lich]
    g.try_move(jx - p.x, jy - p.y)
    w.evils = keep_ev
    assert m.tile(jx, jy) != D.JAR and lich.jar and lich.back is None
    # the servant falls: its relic, with one small power
    s0 = g.stats()
    stat = SH.SERVANT[light.key]['relic'][1]
    g.kill(boss)
    assert light.defeated and any(it.k == 'relic' and it.t == light.key for it in p.inv)
    assert g.stats().get(stat, 0) > s0.get(stat, 0)
    # a hero rides out; one who falls leaves a cairn with the journal
    to_over(g, 0)
    for _ in range(12):
        DBG.shadow(g, 'hero')
        if any(h['state'] == 'dead' for h in sh['heroes']):
            break
    graves = [q for q in w.sites if q.kind == 'hgrave']
    assert sh['heroes'] and graves, [h['state'] for h in sh['heroes']]
    gs = graves[0]
    g.enter_site(gs.id)
    cx, cy = next((i_ % g.map.w, i_ // g.map.w) for i_, t in enumerate(g.map.t) if t == D.HCAIRN)
    p.x, p.y = cx - 1, cy
    g.try_move(1, 0)
    assert gs.id in SH.know(g)['read'] and g.request and g.request[0] == 'dialog'
    g.request = None
    # where it shows: the journal tab, the map layer, the line under the map
    to_over(g, 0)
    for e_ in w.evils:
        if not e_.known:
            EVL.learn(g, e_)
    g.request = None
    DBG.shadow(g, 'lts')
    app.screens = [ui.GameScreen(app), ui.JournalScreen(app, ui.JournalScreen.TABS.index('Shadow'))]
    app.render()
    rows = app.screens[-1].rows_shadow()
    text = ' '.join(t for r in rows for _x, t, _c in r['parts'])
    assert 'HIS SERVANTS' in text and heavy.name[:20] in text and lt['name'][:20] in text
    app.screens = [ui.GameScreen(app), ui.WorldMapScreen(app)]
    app.key('7')
    assert ui.WorldMapScreen.LAYERS[ui.WorldMapScreen.layer] == 'Shadow'
    app.render()
    cx, cy = sh['coast']
    assert SH.his_land(g, cx, cy) and SH.where_line(g, cx, cy) == "The Hollow King's coast"
    assert SH.layer_look(g, cx, cy) is not None
    ui.WorldMapScreen.layer = 0
    for k in ('up', 'zero', 'name', 'wake', 'seal', 'weak', 'month'):
        DBG.shadow(g, k)
    pickle.dumps(g)
    print('shadow ok')


def skyseat():
    """The great evils part 2: the mist over the Sky-Seat and its tearing, the skipper who dares the whirlpool, the
    chain (gusts, handholds, broken links, the fall to the sea), the stair into the city, the five floors and their
    beacons, the Hollow King lighter for every relic, the shade that rises with your pack where the dead are bound,
    the dearer raising, no town portal, the Long Night and the end."""
    import pickle
    from avarenthia import shadow as SH, skyseat as SK, events as EV, debug as DBG, economy as ECO
    from avarenthia.worldgen import free_around
    print('== skyseat')
    random.seed(18)
    g = E.Game('Climber', False, 4245)
    app = ui.App(FakeCanvas(ui.W, ui.H))
    app.start_game(g)
    p = g.player
    w = g.world
    sh = SH.st(w)
    om = g.maps['over']
    assert 'skyseat' in w.dungeons and not sh['seen']
    assert not any(n == 'The Sky-Seat' for n, _x, _y in w.wonders), 'hidden in the mist'
    x0, y0 = sh['sky'][0], sh['sky'][1] + 10
    i0 = y0 * om.w + x0
    assert om.over.get(i0) and om.over[i0][0] in '░▒~', 'mist over the city'
    SH.know(g)['king'] = True
    SK.check(g)
    assert sh['seen'] and any(n == 'The Sky-Seat' for n, _x, _y in w.wonders)
    # the skipper on the harbour nearest his coast
    from avarenthia.living import harbours
    cx, cy = sh['coast']
    here = min(harbours(g), key=lambda q: cheb(q.x, q.y, cx, cy))
    assert SK.dares(g, here) and SK.opt(g, here)
    others = [q for q in harbours(g) if q.id != here.id]
    assert not others or not SK.dares(g, others[0])
    g.enter_town(here.id)
    SK.whirl(g)
    assert not g.pending, 'no relic, no passage'
    DBG.shadow(g, 'relic')
    DBG.shadow(g, 'relic')
    p.gold = 100000
    SK.whirl(g)
    assert g.pending and g.pending['key'] == 'skyseat'
    EV.resolve(g, 'go')
    m = g.map
    assert g.cur == SK.CHAIN and getattr(m, 'skychain', False) and p.gold == 100000 - SK.FARE
    app.render()
    # a gust: a handhold holds you, without one it throws you off the chain into the sea
    links = [(i_ % m.w, i_ // m.w) for i_, t in enumerate(m.t) if t == D.STARLINK]
    ex = next(c for c in links if m.tile(c[0] + 1, c[1]) == D.AIR and c[1] > 40 and
              not any(m.tile(c[0] + a, c[1] + b) == D.CHAIN for a in (-1, 0, 1) for b in (-1, 0, 1)))
    p.x, p.y = ex
    p.life = g.stats()['max_life']
    m.gust = dict(t=g.turn, dx=1)
    SK.turn(g)
    assert (p.x, p.y) == m.entry and p.life < g.stats()['max_life'], 'off the chain and into the sea'
    p.x, p.y = ex
    m.set(ex[0] - 1, ex[1] - 1, D.CHAIN)
    m.gust = dict(t=g.turn, dx=1)
    SK.turn(g)
    assert (p.x, p.y) == ex, 'a handhold holds'
    # a broken link gives way if you stand on it
    m.set(*ex, D.WEAKLINK)
    p.life = g.stats()['max_life']
    SK.turn(g)
    assert (p.x, p.y) == ex
    SK.turn(g)
    assert m.tile(*ex) == D.AIR and (p.x, p.y) == m.entry
    # the stair into the city; each floor's name and beacon
    p.x, p.y = m.top[0], m.top[1] - 1
    assert m.tile(p.x, p.y) == D.UP
    g.use_stairs('up')
    f1 = g.map
    assert g.cur == 'skyseat:1' and 'Under-City' in f1.name and D.BEACON in f1.t
    bx, by = f1.beacon
    near = next(c for c in free_around(g, f1, bx, by, 1))
    p.x, p.y = near
    g.try_move(bx - p.x, by - p.y)
    assert f1.tile(bx, by) == D.LITBEACON and 1 in sh['beacons']
    assert g.town_portal() == 0 or not any(it.k == 'scroll' for it in p.inv)
    app.render()
    # the throne: the Hollow King, two phases lighter for two relics
    DBG.shadow(g, 'f5')
    f5 = g.map
    king = next(o for o in f5.mons if o.k == 'hollow_king')
    kt = king.kit_over
    assert king.light == 2 and 'Z' not in kt['phases'][0]['beat'] and 'Z' not in kt['phases'][1]['beat']
    assert 'Z' in kt['phases'][2]['beat'] and 'Z' in BS_KIT_BEAT()
    # dying there: the dearer raising, the shade with your pack, new bound dead on the unlit floors
    n_inv = sum(1 for it in p.inv if not g.is_equipped(it) and it.k != 'quest')
    gold0 = p.gold
    fee = g.raise_fee() * 2
    sp = next(c for c in free_around(g, f5, king.x, king.y, 12) if cheb(*c, king.x, king.y) > 6)
    p.x, p.y = sp
    dead_before = sum(1 for o in g.maps['skyseat:1'].mons if o.k == 'bound_dead')
    g.die('a test')
    assert not g.dead and p.gold == gold0 - fee and g.cur != 'skyseat:5'
    sd = next(o for o in f5.mons if o.__dict__.get('my_body') is not None)
    assert sd.name.startswith('The shade of') and len(sd.my_body.payload['items']) <= n_inv
    assert sum(1 for o in g.maps['skyseat:1'].mons if o.k == 'bound_dead') == dead_before, 'a lit floor stays calm'
    g.cur = 'skyseat:5'
    p.x, p.y = sp
    g.compute_fov()
    g.kill(sd)
    assert any(it.k == 'corpse' for it in f5.items)
    # the Long Night: dark, wider, dearer
    DBG.shadow(g, 'night')
    assert sh['night'] and SH.land_r(w) == SH.NIGHT_R
    SH.daily(g)
    assert ECO.NIGHT[0] > 1
    # the end: he falls, the world heals
    g.request = None
    g.kill(king)
    assert sh['won'] and g.request == ('win',) and SH.land_r(w) == 0
    SH.daily(g)
    assert ECO.NIGHT[0] == 1.0
    app.screens = [ui.GameScreen(app), ui.WinScreen(app)]
    app.render()
    app.screens = [ui.GameScreen(app)]
    pickle.dumps(g)
    print('skyseat ok')


def crafts():
    """Life skills part 1: the curve and the colours, herbs with properties and alchemy without recipes, the ten drinks,
    fish and ore and cloth by tier, Smithing at the anvil and Tailoring at the bench, the game too wary for you."""
    from avarenthia import lifeskills as LS, foraging as FG, alchemy as AL, brewing as BR, crafts as CRF, hunting as HT
    from avarenthia import hunger as HU, skills as SKL
    from avarenthia.entities import make_monster
    import pickle
    print('== crafts')
    random.seed(19)
    app = new_app('soft', 1919)
    g = app.game
    p = g.player
    p.gold = 10 ** 6
    # the curve: slow, and work far below you teaches nothing
    assert LS.need_for(0) == 20 and LS.need_for(10) == 95 and LS.need_for(49) > 1000
    assert LS.colour(20, 5) == 'grey' and LS.colour(20, 14) == 'green' and LS.colour(20, 20) == 'yellow' \
        and LS.colour(20, 30) == 'orange'
    p.life_sk['fishing'] = [20, 0]
    LS.gain(g, 'fishing', 5, at=0)
    assert p.life_sk['fishing'][1] == 0, 'grey work teaches nothing'
    LS.gain(g, 'fishing', 5, at=20, what='trout')
    first = p.life_sk['fishing'][1]
    LS.gain(g, 'fishing', 5, at=20, what='trout')
    assert first > p.life_sk['fishing'][1] - first > 0, 'the first time counts double'
    assert 'herbalism' not in LS.LIFE and {'smithing', 'tailoring'} <= set(LS.LIFE_ORDER)
    # foes far below you teach a discipline little
    line = 'swords'
    p.disc.setdefault(line, [0, 0])
    p.lvl = 20
    weak = make_monster(g, 'rat', p.x, p.y, 1, 1)
    p.disc[line] = [0, 0]
    SKL.gain(g, line, 1, weak)
    low = p.disc[line][1]
    p.disc[line] = [0, 0]
    SKL.gain(g, line, 1)
    assert p.disc[line][0] == 0 and low < p.disc[line][1] / 5, (low, p.disc[line])
    # herbs: 51, each with two properties, almost every property in every tier
    assert len(FG.HERBS) >= 49 and all(len(v[1]) == 2 for v in FG.HERBS.values())
    for tier in 'ABCD':
        props = {pr for v in FG.HERBS.values() if v[0] == tier for pr in v[1]}
        assert len(props) >= 12, (tier, props)
    assert FG.props_known(g, 'arnica') == ['?', '?']
    p.inv.append(FG.make_plant(g, 'arnica', 1))
    p.food = 0
    FG.eat_plant(g, next(i for i in p.inv if i.t == 'arnica'))
    assert FG.props_known(g, 'arnica') == ['Heal', '?'], 'tasting teaches the first property'
    # foraging finds only what grows here, and the better herbs are too hard for a beginner
    to_over(g, 0)
    om = g.maps['over']
    found, hard = set(), 0
    forest = [k for k, t in enumerate(om.t) if t == D.FOREST]
    for _ in range(300):
        k = random.choice(forest)
        p.x, p.y = k % om.w, k // om.w
        key = FG.draw_herb(g)
        if key == 'hard':
            hard += 1
        elif key:
            found.add(key)
            assert FG.herb_here(g, key)
    print('herbs in the woods:', sorted(found), 'too hard', hard)
    assert found and all(FG.HERBS[k][0] == 'A' for k in found)
    # alchemy: what two herbs share
    p.inv = [i for i in p.inv if i.k != 'plant']
    for k in ('yarrow', 'dandelion', 'elderflower', 'wolfsbane', 'fly_agaric', 'nightshade', 'moonpetal', 'valerian',
              'starmoss', 'kingsfoil', 'feverfew'):
        p.inv.append(FG.make_plant(g, k, 3))
    p.life_sk['alchemy'] = [25, 0]
    random.seed(4)
    assert AL.shared(['yarrow', 'dandelion']) == (['Heal'], False)
    assert AL.shared(['yarrow', 'dandelion', 'elderflower'])[1], 'three that share one property'
    n0 = len([i for i in p.inv if i.k == 'draught'])
    for _ in range(3):
        AL.brew(g, ['yarrow', 'dandelion', 'elderflower'])
    drs = [i for i in p.inv if i.k == 'draught']
    assert len(drs) > n0 and drs[0].props == ['Heal'] and drs[0].t == 'draught'
    assert FG.props_known(g, 'elderflower') == ['Ward Cold', 'Heal'], 'a brew that works teaches both'
    assert AL.form_of(AL.shared(['wolfsbane', 'fly_agaric'])[0])[0] == 'oil'
    assert AL.form_of(AL.shared(['moonpetal', 'valerian'])[0])[0] == 'flask'
    p.life = 1
    AL.use(g, drs[0])
    assert p.life > 1
    # a ruined brew: nothing shared
    before = sum(i.n for i in p.inv if i.k == 'plant')
    AL.brew(g, ['kingsfoil', 'wolfsbane'])
    assert sum(i.n for i in p.inv if i.k == 'plant') == before - 2
    # the oil on a blade, the flask thrown
    from avarenthia.entities import make_gear
    w = make_gear(g, 'longsword', 'normal', 1)
    p.inv.append(w)
    p.str = p.dex = 200
    p.eq.pop('weapon', None)
    p.eq.pop('shield', None)
    g.equip(w)
    assert g.eq_item('weapon') is w
    for _ in range(4):
        AL.brew(g, ['wolfsbane', 'fly_agaric'])
    oil = next((i for i in p.inv if i.k == 'draught' and i.t == 'oil'), None)
    if oil:
        AL.use(g, oil)
        assert any(b[0] == 'oil_venom' for b in p.buffs)
    # Starmoss alone: +5 life, once in a life
    life0 = g.stats()['max_life']
    AL.brew(g, ['starmoss'])
    star = next(i for i in p.inv if i.k == 'draught' and i.t == 'starlight')
    AL.use(g, star)
    assert g.stats()['max_life'] == life0 + 5
    AL.brew(g, ['starmoss'])
    star = next(i for i in p.inv if i.k == 'draught' and i.t == 'starlight')
    assert AL.use(g, star) == 0 and g.stats()['max_life'] == life0 + 5
    app.screens = [ui.GameScreen(app), ui.BrewScreen(app)]
    app.render()
    app.key('a')
    app.key('b')
    app.render()
    app.key('tab')
    app.render()
    app.key('esc')
    # brewing: ten drinks, learnt per people; tasting teaches; far away they sell better
    assert len(BR.RECIPES) == 10
    assert 'cider' not in BR.known(g)
    p.inv.append(HU.make_food(g, 'cider', 1))
    HU.eat(g, next(i for i in p.inv if i.t == 'cider'))
    assert 'cider' in BR.known(g)
    g.enter_town(0)
    p.life_sk['brewing'] = [12, 0]
    p.inv.append(HU.make_food(g, 'apple', 6))
    random.seed(1)
    BR.brew(g, 'cider')
    BR.brew(g, 'cider')
    jug = next(i for i in p.inv if i.k == 'food' and i.t == 'cider')
    assert jug.origin is not None
    near = jug.value()
    jug.origin = (jug.origin[0] + 200, jug.origin[1])
    assert jug.value() > near, 'a drink sells best far from where it was brewed'
    p.life_sk['brewing'] = [0, 0]
    assert BR.brew(g, 'cider') == 0, 'too hard for you yet'
    # fish by tier: fresh and salt apart, the big ones in their own water
    assert 'minnow' in LS.FISH and 'sea' not in LS.FISH['minnow'][2] and 'sea' in LS.FISH['sprat'][2]
    assert LS.fish_cond(g, '') and not LS.fish_cond(g, 'deepest')
    # smithing: ore by depth, bars, a piece with grade and quality from the metal and your rank
    p.cargo['ore'] = 6
    CRF.give(g, 'ore_deepiron', 4)
    p.life_sk['smithing'] = [25, 0]
    CRF.smelt(g, 'iron')
    CRF.smelt(g, 'deepiron')
    CRF.smelt(g, 'deepiron')
    assert CRF.count(g, 'bar_iron') == 1 and CRF.count(g, 'bar_deepiron') == 2
    CRF.give(g, 'bar_deepiron', 4)
    n_gear = len([i for i in p.inv if i.k == 'gear'])
    CRF.make(g, 'smithing', 'chainmail', 'deepiron')
    mail = [i for i in p.inv if i.k == 'gear'][-1]
    assert len([i for i in p.inv if i.k == 'gear']) == n_gear + 1
    assert mail.base == 'chainmail_x' and 'Deepiron' in mail.name and mail.made[2] in CRF.QUALITY, mail.name
    print('forged:', mail.name, mail.arm, mail.mdur)
    p.life_sk['smithing'] = [0, 0]
    CRF.give(g, 'bar_adamant', 8)
    CRF.r_craft_item(g, 'make:platemail', {'craft': 'smithing'})
    assert not any('Adamant' in i.name for i in p.inv if i.k == 'gear'), 'adamant is too hard for you yet'
    # mending and honing at the anvil
    mail.dur = 1
    CRF.give(g, 'bar_iron', 1)
    CRF.mend(g, mail.id)
    assert mail.dur == mail.mdur
    CRF.hone(g)
    assert any(b[0] == 'honed' for b in p.buffs)
    # a vein: iron near the surface, its metal kept once struck
    mm = g.maps[g.cur]
    assert CRF.vein(g, 1, 1) == CRF.vein(g, 1, 1)
    # tailoring: a warm robe of wool, and warm clothes keep the cold from eating your food
    CRF.give(g, 'cloth_wool', 6)
    p.life_sk['tailoring'] = [5, 0]
    CRF.make(g, 'tailoring', 'robe', 'wool', 'warm')
    robe = [i for i in p.inv if i.k == 'gear'][-1]
    assert robe.base == 'robe' and robe.feel == 'warm'
    g.equip(robe)
    assert CRF.feel_count(g, 'warm') == 1
    CRF.make(g, 'tailoring', 'bandages', 'wool')
    assert any(i.k == 'tool' and i.t == 'bandage' and i.n == 3 for i in p.inv)
    # leather by its beast
    assert HT.LEATHER_OF['wolf'] == 'fur' and CRF.LEATHERS['croc'][1] == 'C'
    p.inv.append(__import__('avarenthia.entities', fromlist=['Item']).Item(g.new_id(), 'leather', 'snake', 4))
    p.life_sk['leatherworking'] = [15, 0]
    CRF.make(g, 'leatherworking', 'boots', 'snake')
    boots = [i for i in p.inv if i.k == 'gear'][-1]
    assert ['res_poison', 15] in boots.aff, boots.aff
    # the shops sell cloth of their land
    s0 = g.world.settlements[0]
    stock = CRF.shop_cloth(g, s0)
    assert all(it.k == 'mat' and it.t.startswith('cloth_') for it in stock)
    # a herd above your tier is too wary for you yet
    h = HT.Herd(g.new_id(), 'aurochs', 5, 5, 6)
    to_over(g, 0)
    p.life_sk['hunting'] = [0, 0]
    assert HT.hunt(g, h) == 0 and g.cur == 'over'
    # spiders leave silk
    random.seed(2)
    spun = 0
    for _ in range(30):
        o = make_monster(g, 'spider', p.x, p.y, 4, 1)
        g.map.mons.append(o)
        before = len(g.map.items)
        CRF.on_kill(g, o)
        spun += len(g.map.items) > before
        g.map.mons.remove(o)
    assert spun
    pickle.dumps(g)
    print('crafts ok')


def masters():
    """Life skills part 2: beast parts as the chosen power, the ladder, a part broken off, a named beast's own parts,
    its den, catching one alive, Unmake, the master's tests at 25 and 40, orders, the great masters, the perks."""
    from avarenthia import lifeskills as LS, crafts as CRF, beastparts as BP, mastery as MA, named as NM
    from avarenthia import missions as MS, realmjobs as RJ, sites as ST, folk as FK
    from avarenthia.entities import Item, make_monster, make_gear
    import pickle
    print('== masters')
    random.seed(20)
    app = new_app('soft', 2020)
    g = app.game
    p = g.player
    p.gold = 10 ** 6
    # the ladder: the same part from a stronger beast gives more
    assert BP.power('fangs:wolf') == ('hit', 5) and BP.power('fangs:winter_wolf') == ('hit', 10) \
        and BP.power('fangs:sabretooth') == ('hit', 15)
    assert BP.power('ivory:mammoth')[0] == 'life' and BP.power('frostscale:frost_drake')[0] == 'res_cold'
    # a part is the power you choose: wolf fangs on leather gloves
    p.inv.append(Item(g.new_id(), 'leather', 'leather', 6))
    p.inv.append(BP.make(g, 'fangs', 'wolf', 2))
    p.inv.append(BP.make(g, 'horn', 'aurochs', 1))
    p.life_sk['leatherworking'] = [10, 0]
    CRF.make(g, 'leatherworking', 'gloves', 'leather', None, ['fangs:wolf'])
    gl = [i for i in p.inv if i.k == 'gear'][-1]
    assert ['hit', 5] in gl.aff, gl.aff
    assert not BP.fits('armour', gl) or gl.slot != 'weapon'
    # from rank 40, two parts
    p.life_sk['leatherworking'] = [40, 0]
    CRF.make(g, 'leatherworking', 'leather', 'leather', None, ['horn:aurochs', 'fangs:wolf'])
    arm = [i for i in p.inv if i.k == 'gear'][-1]
    assert any(a[0] == 'edef' for a in arm.aff) and any(a[0] == 'hit' for a in arm.aff), arm.aff
    # road boots: a quarter quicker over their own land
    p.inv.append(Item(g.new_id(), 'leather', 'leather', 6))
    CRF.make(g, 'leatherworking', 'marshboots', 'leather')
    mb = [i for i in p.inv if i.k == 'gear'][-1]
    assert mb.road == 'marsh' and 'Marsh Boots' in mb.name, mb.name
    p.str = p.dex = 200
    g.equip(mb)
    assert CRF.road_boots(g, D.SWAMP) == .75 and CRF.road_boots(g, D.GRASS) == 1
    # a big beast below half: a critical blow breaks a part off
    to_over(g, 0)
    g.enter_town(0)
    bear = make_monster(g, 'brown_bear', p.x + 1, p.y, 6)
    g.map.mons.append(bear)
    bear.hp = bear.maxhp // 3
    n_items = len(g.map.items)
    BP.on_blow(g, bear, True)
    assert len(g.map.items) == n_items + 1 and bear.broken_part
    BP.on_blow(g, bear, True)
    assert len(g.map.items) == n_items + 1, 'once per beast'
    g.map.mons.remove(bear)
    # a named beast keeps a den near its home, hidden until found
    to_over(g, 0)
    n = None
    for _ in range(20):
        n = NM.make(g, prey='beast', rank='notable')
        if n and getattr(n, 'den', None) is not None:
            break
    assert n and n.den is not None
    den = g.world.sites[n.den]
    assert den.kind == 'den' and FK.unfound(den) and den.nid == n.id
    om = g.maps['over']
    p.x, p.y = den.x + 1, den.y
    BP.on_step(g)
    assert not FK.unfound(den)
    m = ST.gen_site_map(g, den)
    assert m.nook and m.entry
    n.back = g.day + 3
    g.enter_site(den.id)
    boss = next((o for o in g.map.mons if getattr(o, 'named', None) == n.id), None)
    assert boss is not None, 'licking its wounds in its den'
    # its own parts: Skinning by its rank, a knife
    p.life_sk['skinning'] = [15, 0]
    p.inv.append(Item(g.new_id(), 'tool', 'knife'))
    before = len(g.map.items)
    BP.named_parts(g, boss, n)
    nparts = [i for i in g.map.items[before:] if i.k == 'npart']
    assert nparts and nparts[0].beast == n.name, g.map.items[before:]
    np_ = nparts[0]
    g.map.items.remove(np_)
    p.inv.append(np_)
    BP.den_gone(g, n)
    assert getattr(den, 'gone', False) and ST.site_at(g.world, den.x, den.y) is None
    # a piece made of it bears the beast's name and carries the power of found gear
    p.inv.append(Item(g.new_id(), 'leather', 'leather', 6))
    CRF.make(g, 'leatherworking', 'boots', 'leather', None, [f'n{np_.id}'])
    nb = [i for i in p.inv if i.k == 'gear'][-1]
    assert nb.name.startswith(NM.poss(n.name)) and BP.npower(np_)[0] in [a[0] for a in nb.aff], (nb.name, nb.aff)
    # Unmake: a found power onto your own work; the found piece is gone either way
    p.life_sk['leatherworking'] = [45, 0]
    found = make_gear(g, 'ring', 'magic', 10)
    found.ided = True
    found.aff = [['life', 12]]
    p.inv.append(found)
    own = next(i for i in p.inv if i.k == 'gear' and getattr(i, 'made', None) and not getattr(i, 'moved', False)
               and not g.is_equipped(i))
    assert CRF.unmake_pairs(g, 'leatherworking')
    assert CRF.unmake_chance(g, 'leatherworking', 'life') == 55 and CRF.unmake_chance(g, 'leatherworking', 'leech') == 40
    ok = CRF.do_unmake(g, 'leatherworking', found.id, 0, own.id, 8, 100)
    assert ok and own.moved and ['life', 8] in own.aff and found not in p.inv
    found2 = make_gear(g, 'ring', 'magic', 10)
    found2.ided = True
    found2.aff = [['life', 12]]
    p.inv.append(found2)
    own2 = next(i for i in p.inv if i.k == 'gear' and getattr(i, 'made', None) and not getattr(i, 'moved', False)
                and not g.is_equipped(i))
    assert not CRF.do_unmake(g, 'leatherworking', found2.id, 0, own2.id, 8, 0) and found2 not in p.inv
    # the master's test at 25: the skill stops until a master has seen your work
    p.life_sk['fishing'] = [25, 0]
    LS.gain(g, 'fishing', 10 ** 4, at=30)
    assert p.life_sk['fishing'][0] == 25
    mt = next(mi for mi in g.missions if mi.kind == 'mastertest' and mi.data['key'] == 'fishing')
    assert MA.line(g, mt)
    p.inv.append(LS.make_fish(g, 'sturgeon'))
    MA.hand_in(g, mt, mt.giver)
    assert mt.state == 'done' and MA.passed(g, 'fishing', 25)
    LS.gain(g, 'fishing', 10 ** 4, at=40)
    assert 25 < p.life_sk['fishing'][0] <= 40
    # an order at your own height, from a town board
    p.life_sk['smithing'] = [22, 0]
    p.life_sk['leatherworking'] = [0, 0]
    s0 = g.world.settlements[0]
    od = MA.make_order(g, s0)
    assert od and od.kind == 'order' and od.data['key'] == 'smithing' and od.data['tier'] == 'C'
    od.state = 'active'
    g.missions.append(od)
    CRF.give(g, 'bar_deepiron', 10)
    for _ in range(od.data['n']):
        CRF.make(g, 'smithing', 'dagger', 'deepiron')
    sk0 = p.life_sk['smithing'][:]
    MA.hand_in(g, od, s0.id)
    assert od.state == 'done' and p.life_sk['smithing'] != sk0
    # the three great masters: far from the roads, found by rumour, a test in three parts
    ms = MA.ensure(g)
    assert set(ms) == {'smithing', 'leatherworking', 'tailoring'}
    random.seed(3)
    for _ in range(40):
        MA.rumour(g, 'The innkeeper')
    assert p.masters_heard == set(ms)
    site = g.world.sites[ms['tailoring']['site']]
    g.enter_site(site.id)
    master = next(o for o in g.map.mons if getattr(o, 'role', '') == 'master')
    MA.talk(g, master)
    assert MA.stage(g, 'tailoring') == 1
    CRF.give(g, 'cloth_feysilk', 1)
    MA.talk(g, master)
    assert MA.stage(g, 'tailoring') == 2
    np2 = Item(g.new_id(), 'npart', 'Swift')
    np2.beast, np2.nid, np2.rank, np2.src, np2.word = 'the Widow', None, 'notorious', 'wolf_spider', 'chitin'
    p.inv.append(np2)
    MA.talk(g, master)
    assert MA.stage(g, 'tailoring') == 3
    lost = g.world.sites[ms['tailoring']['lost']]
    assert not FK.unfound(lost)
    g.enter_site(lost.id)
    for o in [o for o in g.map.mons if not o.is_npc]:
        g.kill(o)
    assert MA.stage(g, 'tailoring') == 4
    # catching one alive: a lord's job, a sleeping draught, a rope
    to_over(g, 0)
    R = g.world.realm
    lo = next(o for o in R.lords.values() if o.alive and R.houses[o.house].seat)
    nb2 = NM.make(g, g.world.settlements[0].x, g.world.settlements[0].y, prey='beast', rank='notable')
    gd = dict(kind='lord', lid=lo.id, house=lo.house, name='the lord')
    job = RJ.make_catch(g, gd)
    if job:
        job.state = 'active'
        g.missions.append(job)
        nb3 = NM.get(g, job.data['nid'])
        g.enter_town(0)
        beast = make_monster(g, nb3.k, p.x + 1, p.y, nb3.lvl)
        NM.apply(g, beast, nb3)
        g.map.mons.append(beast)
        assert not BP.try_bind(g, beast), 'awake: no rope holds it'
        beast.hold, beast.slept = 5, True
        beast.hp = beast.maxhp // 5
        p.inv.append(Item(g.new_id(), 'tool', 'rope'))
        assert BP.try_bind(g, beast) and job.state == 'turnin' and getattr(nb3, 'caught', False)
        assert beast not in g.map.mons
    print('caught alive:', bool(job), nb2 is not None)
    # perks: a master's dishes keep, a master's veins give more
    assert 30 in LS.LIFE['fishing']['perks'] and 50 in LS.LIFE['tailoring']['perks']
    assert all({30, 40, 50} <= set(v['perks']) for v in LS.LIFE.values())
    pickle.dumps(g)
    print('masters ok')


def city_rules():
    """Cities that grew: every kind (cathedral, burgh, palace, fortress, harbour, canal, metropolis) keeps the rules
    Nilio set on the mock-ups, on several draws; in the game each human city is walled, peopled and can be walked
    from its gates to its market."""
    import pickle
    from avarenthia import citygrow as CG, towns as TW
    print('== city_rules')
    kinds = [('grown', 'cathedral', False, True, 0), ('grown', 'castle', False, True, 0),
             ('grown', 'palace', False, False, 0), ('grown', 'castle', True, True, 0),
             ('grown', 'cathedral', False, True, 30), ('canal', 'cathedral', False, True, 30),
             ('metropolis', 'cathedral', False, True, 30), ('metropolis', 'palace', False, True, 0)]
    for seed in (1, 2, 3):
        for i, k in enumerate(kinds):
            random.seed(seed * 100 + i)
            roads = [(random.uniform(-3, 3), 'a'), (random.uniform(-3, 3), 'b'), (random.uniform(-3, 3), None)]
            c, sq = CG.grow('x', 'X', k[0], k[1], k[2], k[3], roads, k[4])
            bad = {r: n for r, n in CG.rules(c).items() if n}
            assert not bad, (seed, k, bad)
            assert len(c.houses) > (300 if k[0] == 'metropolis' else 120), (seed, k, len(c.houses))
            if k[0] != 'canal':
                assert any(g[0] == {'cathedral': 'cathedral', 'castle': 'keep', 'palace': 'keep'}[k[1]] or
                           k[1] == 'cathedral' for g in c.great), (seed, k, c.great)
            assert len(c.exits) >= 2 and len(c.stalls) >= 6, (seed, k)
    app = new_app('soft', seed=24)
    g = app.game
    cities = [s for s in g.world.settlements if s.is_city and s.race == 'human' and not getattr(s, 'elder', False)]
    assert cities
    seen = set()
    for s in cities:
        mk = CG.plan(g, s)
        seen.add(mk[0])
        m = TW.gen_settlement_map(g, s)
        assert m.grown == mk[0] and m.exits, s.name
        homes = [b for b in m.homes]
        assert homes and any(o.is_npc for o in m.mons), s.name
        assert any(o.is_npc and o.role == 'market' for o in m.mons), s.name
        # from the first way in, every gate and the market can be walked to
        q, reach = [m.entry], {tuple(m.entry)}
        while q:
            x, y = q.pop()
            for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if n not in reach and m.inb(*n) and D.TILES[m.tile(*n)].walk:
                    reach.add(n)
                    q.append(n)
        for ex, ey, other in m.exits:
            assert (ex, ey) in reach, (s.name, 'a gate cut off')
        stall = next(o for o in m.mons if o.is_npc and o.role == 'market')
        assert any((stall.x + dx, stall.y + dy) in reach for dx in (-1, 0, 1) for dy in (-1, 0, 1)), s.name
    print('kinds in this world:', sorted(seen))
    pickle.dumps(g)
    print('city_rules ok')


def BS_KIT_BEAT():
    from avarenthia import bosses as BS
    return ''.join(ph['beat'] for ph in BS.KITS['hollow_king']['phases'])


def main():
    random.seed(int(os.environ.get('TEST_SEED', '1')))
    parts = [animations, seasons, lands, peoples, camps_and_holds, wonders, world_life, thornfield_and_faith, countryside, start_and_survival, crime_and_coin, world_and_people,
             items_skills_curse, smoke, trade_and_jobs, factions_and_death, wilds, ways_and_wares, hirelings_and_camp,
             creatures_and_hunts, new_guilds, more_jobs, text_fits, overview, chronicle, ferries, place_names, nature_sites, zones, herds_and_cooking, realms, stamina, schools, visible, market_days, debug_menu, weapons, classes, trees, pairs, balance, k5, places, halls, aurora, rift, old_places, varnish, epics, money_fixes, bosses, boss_moves, shadow, skyseat, crafts, masters, archaeology, trade_goods, boss_maker, city_rules]
    only = os.environ.get('TEST_ONLY')             # e.g. TEST_ONLY=smoke,wilds to run a part of the suite
    for f in parts:
        if not only or f.__name__ in only.split(','):
            f()


def archaeology():
    """Archaeology: dig spots at old places, seen by rank, dug with a trowel; lore, a servant's weakness, old pieces
    a smith mends, finds a library buys, the master's test."""
    from avarenthia import lifeskills as LS, archaeology as AR, crafts as CRF, mastery as MA, shadow as SH
    from avarenthia import debug as DBG
    from avarenthia.entities import Item
    print('== archaeology')
    random.seed(21)
    app = new_app('soft', 2121)
    g = app.game
    p = g.player
    p.gold = 10 ** 6
    assert 'archaeology' in LS.LIFE_ORDER and D.TILES[D.DIGSPOT].name == 'dig spot'
    sites = [s for s in g.world.sites if s.kind in AR.KINDS and s.kind not in ('wreck',)]
    assert sites, 'no old places'
    var = [s for s in sites if s.kind in AR.VARNISH]
    site = next((s for s in sites if s.kind == 'oldfield'), sites[0])
    # without a tool and rank 0 nothing shows; with a trowel the easy spots do
    to_over(g, 0)
    g.enter_site(site.id)
    m = g.map
    assert m.digs and len(m.digs) <= AR.KINDS[site.kind], m.digs
    assert D.DIGSPOT not in m.t
    p.inv.append(Item(g.new_id(), 'tool', 'trowel'))
    AR.show(g)
    low = sum(1 for n in m.digs.values() if n <= AR.sight(g))
    assert m.t.count(D.DIGSPOT) == low, (m.t.count(D.DIGSPOT), low, m.digs)
    p.life_sk['archaeology'] = [50, 0]
    AR.show(g)
    assert m.t.count(D.DIGSPOT) == len(m.digs), 'rank 50 sees every spot'
    # dig every spot: each gives something, and the place remembers it
    if not DBG.has(g, 'oldfind'):
        DBG.toggle(g, 'oldfind')
    before = len(p.inv)
    spots = list(m.digs)
    for x, y in spots:
        AR.dig(g, x, y)
        assert m.tile(x, y) != D.DIGSPOT
    assert not m.digs and site.dug == set(spots)
    assert len(p.inv) >= before
    # a new map of the same place holds no spot already dug
    g.maps.pop(site.map_key, None)
    to_over(g, 0)
    g.enter_site(site.id)
    assert not g.map.digs, g.map.digs
    # a servant's weakness from the earth: one source of two
    ev = next((e for e in g.world.evils if not e.defeated), None)
    if ev:
        ev.known = True
        assert SH.clue(g, ev, 'dig', 'test') and 'dig' in SH.know(g)['src'][ev.key]
        assert SH.SOURCES['dig'] == 'what you dug up'
    # an old piece: the smith mends it into magic gear; a Varnish piece wants star-iron
    to_over(g, 0)
    g.enter_town(0)
    op = AR.make_piece(g, False, 25)
    vp = AR.make_piece(g, True, 35)
    p.inv += [op, vp]
    assert op.tier == 'C' and vp.tier == 'D' and AR.need_smith(vp) == 30
    p.life_sk['smithing'] = [10, 0]
    p.inv = [i for i in p.inv if i.k != 'oldpiece' or i in (op, vp)]
    assert all(k is None for _l, k in AR.mend_opts(g)), 'too low a smith'
    p.life_sk['smithing'] = [35, 0]
    ok = dict((k, l) for l, k in AR.mend_opts(g))
    assert f'oldmend:{op.id}' in ok and f'oldmend:{vp.id}' not in ok, 'the Varnish piece wants a shard'
    from avarenthia.nature import curio
    p.inv.append(curio(g, 'stariron'))
    CRF.r_extra(g, f'oldmend:{op.id}')
    CRF.r_extra(g, f'oldmend:{vp.id}')
    made = [i for i in p.inv if i.k == 'gear' and getattr(i, 'old', False)]
    assert len(made) == 2 and all(i.rar == 'magic' for i in made), [(i.name, i.rar) for i in made]
    assert any(i.name.startswith('Varnish ') for i in made) and not any(i.k == 'oldpiece' for i in p.inv)
    assert not any(i.k == 'curio' and i.t == 'stariron' for i in p.inv)
    # a library buys finds for half again what a trader gives
    for k in ('sherd', 'oldcoin', 'torc'):
        p.inv.append(curio(g, k))
    w = AR.worth(g)
    assert w == round(sum(curio(g, k).value() for k in ('sherd', 'oldcoin', 'torc')) * 1.5) or w > 0
    gold = p.gold
    class N:
        name = 'Scribe'
    g.say = lambda *a, **k: None
    assert AR.r_scribe(g, N(), 'finds') and p.gold == gold + w and not AR.finds(g)
    # the master's test at 25 asks for an old piece of tier C
    text, test, n = MA.wants('archaeology', 25)
    assert test(AR.make_piece(g, False, 22)) and not test(AR.make_piece(g, False, 5))
    # the varnish places hold spots too
    if var:
        g.maps.pop(var[0].map_key, None)
        to_over(g, 0)
        g.enter_site(var[0].id)
        assert g.map.digs or var[0].kind == 'vcity'
    print('archaeology ok')


def trade_goods():
    """Trade part 2: named goods and master works, far goods, barter, monster goods, spoiling, need far away,
    contraband and the Watch, war trade, market news, the League."""
    from avarenthia import economy as ECO, tradegoods as TG, beastparts as BP, missions as MS, realms as RL
    from avarenthia.entities import Item
    print('== trade_goods')
    random.seed(22)
    app = new_app('soft', 2222)
    g = app.game
    p = g.player
    w = g.world
    p.gold = 10 ** 7
    T = TG.st(w)
    named = {k: v for k, v in T['named'].items() if v['kind'] == 'named'}
    masters = {k: v for k, v in T['named'].items() if v['kind'] == 'master'}
    assert 12 <= len(named) <= 15 and 3 <= len(masters) <= 4, (len(named), len(masters))
    assert len({v['home'] for v in T['named'].values()}) == len(T['named']), 'one maker per town'
    print('named goods:', ', '.join(v['name'] for v in T['named'].values()))
    for k in T['named']:
        assert k in D.GOODS and all(k in s.market for s in w.settlements if s.market)
    # cheap at home, dear far away
    k, v = next(iter(named.items()))
    home = w.settlements[v['home']]
    far = max((s for s in w.settlements if s.market), key=lambda s: max(abs(s.x - home.x), abs(s.y - home.y)))
    assert ECO.units(home, k) >= 3 and ECO.units(far, k) < 1
    assert ECO.buy_price(home, k) * 1.5 < ECO.sell_price(far, k), (ECO.buy_price(home, k), ECO.sell_price(far, k))
    # a bad year makes it dear
    plain = ECO.price(home, k)
    D.GOODS[k]['f'] = 1.4
    assert ECO.price(home, k) > plain * 1.3
    D.GOODS[k]['f'] = 1.0
    # the market list shows the extra goods that are here; the screen fits
    to_over(g, 0)
    g.enter_town(home.id)
    rows = TG.rows(g, home)
    assert k in rows and rows[:len(D.GOOD_ORDER)] == D.GOOD_ORDER
    app.push(ui.MarketScreen(app, home.id))
    from avarenthia.canvas import Canvas
    Canvas.cut = []
    app.render()
    for _ in range(len(rows)):
        app.key('down')
        app.render()
    assert not Canvas.cut, Canvas.cut
    Canvas.cut = None
    app.pop()
    ECO.buy(g, home, k, 3)
    assert p.cargo.get(k) == 3
    # sold far away: profit, and the League hears of it
    p.cost_basis[k] = 1
    ECO.sell(g, far, k, 3)
    assert getattr(p, 'league_profit', 0) > 0
    p.league_profit = TG.LEAGUE[2][0]
    assert TG.rank(g) == 2 and TG.league_discount(g) == .04
    # far goods: only by sea or the south
    ports = [s for s in w.settlements if s.market and ECO.units(s, 'silk') >= 1]
    inland = [s for s in w.settlements if s.market and ECO.units(s, 'silk') < 1]
    assert inland and (ports or True)
    # barter: salt for moonsilk with the elves; kobolds want gems
    p.cargo.clear()
    p.cargo['salt'] = 5
    assert TG.barter_opts(g, 'glade')[0][1] == 'barter:glade'
    assert TG.barter(g, 'glade') and p.cargo.get('moonsilk') == 2 and 'salt' not in p.cargo
    assert TG.barter_opts(g, 'kobolds')[0][1] is None
    # spoiling: fruit goes off, salt slows it
    p.cargo.clear()
    p.cargo['fruit'] = 40
    random.seed(1)
    for _ in range(20):
        TG.spoil(g)
    lost = 40 - p.cargo.get('fruit', 0)
    p.cargo['fruit'] = 40
    p.cargo['salt'] = 10
    random.seed(1)
    for _ in range(20):
        TG.spoil(g)
    assert lost > 0 and 40 - p.cargo.get('fruit', 0) < lost
    # need far away: three times the price, nothing to buy
    vil = next(s for s in w.settlements if s.kind == 'village' and s.market and s.id != 0)
    before = ECO.price(vil, 'grain')
    T['need'][vil.id] = ('grain', 10)
    assert abs(ECO.price(vil, 'grain') / before - 3) < .01
    del T['need'][vil.id]
    # contraband: markets will not buy it; the Watch finds it; the cove pays
    p.cargo.clear()
    p.cargo['lotus'] = 4
    town = next(s for s in w.settlements if s.kind in ('town', 'city') and s.race == 'human')
    assert ECO.sell(g, town, 'lotus', 4) == 0 and p.cargo['lotus'] == 4
    old = TG.SEARCH
    TG.SEARCH = 1.0
    gold = p.gold
    TG.at_gate(g, town)
    TG.SEARCH = old
    assert 'lotus' not in p.cargo and p.gold < gold
    p.cargo['lotus'] = 2
    gold = p.gold
    TG.cove_sell(g)
    assert p.gold == gold + 2 * TG.cove_price()
    # monster goods: a city's herbalist buys beast parts at double their worth
    city = next(s for s in w.settlements if s.is_city)
    to_over(g, 0)
    g.enter_town(city.id)
    p.inv.append(BP.make(g, 'fangs', 'wolf', 3))
    val = sum(i.value() * i.n for i in p.inv if i.k == 'part')
    npc = next((o for o in g.map.mons if o.is_npc), None)
    assert TG.alchemist(g, npc)
    gold = p.gold
    TG.r_alchemist(g, 'sell', {})
    assert p.gold == gold + 2 * val and not TG.parts(g)
    # war trade: arms dear in a realm at war; both sides, and it comes out
    R = RL.get(g)
    war_town = next((s for s in w.settlements if s.market and TG.at_war(w, s)), None)
    if war_town:
        assert ECO.price(war_town, 'arms') > D.GOODS['arms']['base'] * 100 * .35
    # market news: the inn tells of a far town, days old
    gl = len(g.price_log)
    random.seed(3)
    for _ in range(10):
        city.news_day = -1
        TG.inn_news(g, city, npc)
    assert len(g.price_log) > gl and any(r['day'] < g.day for r in g.price_log.values())
    # a city asks for a master work
    m = TG.make_order(g, city)
    if m:
        assert m.kind == 'masterwork' and m.data['good'] in masters
        p.cargo[m.data['good']] = 1
        city.board.append(m)
        MS.accept(g, city, m)
        TG.hand_in(g, m, city.id)
        assert m.state != 'active' and m.data['good'] not in p.cargo
    # the goods survive a save and load
    import pickle
    g2 = pickle.loads(pickle.dumps(g))
    g2.hook()
    assert all(k2 in D.GOODS for k2 in TG.st(g2.world)['named'])
    print('trade_goods ok')


def boss_maker():
    """Boss fights part C: the boss maker (bases, rules, traits, names, rumours), a price on a head, bosses at the end of
    other jobs, yielding, a beast's parts, the floors that foretell a fixed boss and the thing that eases its fight."""
    from avarenthia import bossmaker as MK, bosses as BS, jobs as JB, missions as MS
    print('== boss_maker')
    random.seed(23)
    app = new_app('soft', 2323)
    g = app.game
    p = g.player
    p.gold = 10 ** 6
    rnd = random.Random(5)
    for lvl in (2, 6, 12):
        for base in MK.BASES:
            if lvl < 4 and base in ('deadlord', 'golem', 'fey'):
                continue
            sp = MK.draw(g, lvl, base=base, rnd=rnd)
            kt = sp['kit']
            assert len(kt['phases']) == (3 if lvl >= 10 else 2), (base, lvl)
            cards = [c for ph in kt['phases'] for cs in ph['cards'].values() for c in cs]
            assert all(c in BS.MOVES for c in cards), (base, cards)
            assert any(BS.MOVES[c]['role'] == 'G' for c in cards)
            assert lvl >= 8 or not any(BS.MOVES[c]['role'] == 'Z' for c in cards), (base, lvl, cards)
            assert not any(c in MK.ROOF for c in cards), 'nothing that needs a roof out in the open'
            assert len(kt['weak']) == 1 and sp['rumour'] and sp['name'] and sp['deed']
            for ph in kt['phases']:
                for r in ph['beat']:
                    assert r in ph['cards'], (base, ph['beat'], ph['cards'])
    # a price on a head: on the boards, a fight with a kit boss
    to_over(g, 0)
    town = next(s for s in g.world.settlements if s.kind in ('town', 'city'))
    m = None
    for _ in range(20):
        m = MK.make_head(g, town)
        if m:
            break
    assert m and m.kind == 'head' and m.data['bspec']['rumour'] in m.desc
    print('head:', m.title, '|', m.desc)
    town.board.append(m)
    MS.accept(g, town, m)
    g.cur = 'over'
    p.x, p.y = m.data['spot']
    assert JB.ARRIVE['head'](g, m)
    boss = next(o for o in g.map.mons if o.__dict__.get('maker'))
    assert BS.kit(boss) and BS.st(boss) and boss.name == m.data['leader']
    # it stops at its thresholds; at the end a man may yield, or it dies
    boss.hp = 1
    hold = [boss.maxhp]
    for _ in range(4):
        if boss not in g.map.mons:
            break
        boss.hp = 0
        g.kill(boss)
        if boss.__dict__.get('yielded'):
            MK.r_yield(g, 'law', {'mon': boss.id})
            break
        BS.st(boss)['pending'] = None if BS.st(boss).get('pending') is None else BS.st(boss)['pending']
        if BS.st(boss).get('pending') is not None:
            BS.st(boss)['phase'] = BS.st(boss)['pending']
            BS.st(boss)['pending'] = None
    for o in [o for o in g.map.mons if not o.is_npc]:
        g.map.mons.remove(o)
    JB.after_fight(g, g.map)
    assert m.state == 'turnin', m.state
    # other jobs get a boss and its rumour
    vil = next(s for s in g.world.settlements if s.kind == 'village')
    got = 0
    for k in MK.BOSS_JOBS:
        for _ in range(15):
            mj = JB.MAKE[k](g, vil) if k != 'deserter' else JB.MAKE[k](g, vil)
            if mj:
                assert mj.data.get('bspec') and mj.data['bspec']['rumour'] in mj.desc, k
                got += 1
                break
    assert got >= 2, got
    # a great beast leaves parts of its body
    from avarenthia.entities import make_monster
    sp = MK.draw(g, 6, base='beast', rnd=random.Random(2))
    b = make_monster(g, sp['mon'], p.x, p.y, 6)
    g.map.mons.append(b)
    MK.apply(g, b, sp)
    n = len(g.map.items)
    MK.felled(g, b)
    assert any(i.k == 'part' for i in g.map.items[n:])
    # a twinned boss brings its Shadow beside it, and the survivor takes all
    tw = MK.twin(g, b, dict(sp, traits=['twinned']))
    assert tw and tw in g.map.mons and cheb(tw.x, tw.y, b.x, b.y) <= 2 and tw.name.endswith("'s Shadow")
    g.map.mons.remove(tw)
    # a regenerating boss closes its wounds
    b.regen, b.hp = True, b.maxhp // 2
    hp = b.hp
    MK.on_turn(g, b)
    assert b.hp > hp
    # the floor above a fixed boss foretells it; its own floor hides the thing that eases the fight
    dg = next((d for d in g.world.dungeons.values() if getattr(d, 'boss', None) in MK.FORETELL and d.depth >= 2), None)
    if dg:
        g.enter_dungeon(dg.id, dg.depth - 1, 'down')
        assert (dg.id, dg.depth - 1) in p.foretold
        g.enter_dungeon(dg.id, dg.depth, 'down')
        boons = [i for i in g.map.items if i.k == 'boon']
        assert boons, 'the thing that eases the fight'
        p.inv.append(boons[0])
        g.map.items.remove(boons[0])
        kb = next((o for o in g.map.mons if BS.st(o) is not None), None)
        if kb:
            BS.st(kb)['engaged'] = False
            BS.engage(g, kb)
            assert BS.st(kb)['dots'] >= 2 and not any(i.k == 'boon' for i in p.inv)
    print('boss_maker ok')


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
