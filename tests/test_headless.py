"""Headless tests: drive the real UI and engine with key tokens on a fake canvas.
Run from the project folder:  python tests/test_headless.py [--dump]
"""
import os
import random
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cursed_vale import engine as E, data as D, ui, economy as ECO, missions as MS, wanderers as WA  # noqa: E402
from cursed_vale.canvas import FakeCanvas  # noqa: E402
from cursed_vale.worldgen import cheb  # noqa: E402

E.save_path = lambda: os.path.join(tempfile.gettempdir(), 'cursed_vale_test.dat')

TOKENS = ['up', 'down', 'left', 'right', 'y', 'u', 'b', 'n', 'np5', 'g', 'R', '1', '2', '3', 'q', 'w', 'p', 'x', 't',
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
    return app


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
        from cursed_vale import skills as SK
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
            if mi.kind in kinds_done:
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
    p.gold = 123
    n_bag = len(g.backpack())
    g.die('a test')
    assert not g.dead and p.gold == 0 and len(g.corpses) == 1
    key, cid = g.corpses[0]
    corpse = next(i for i in g.maps[key].items if i.id == cid)
    g.enter_dungeon('rat', 1, 'up')
    p.x, p.y = corpse.x, corpse.y
    g.auto_pickup()
    assert p.gold == 123 and len(g.backpack()) == n_bag and not g.corpses
    print('softcore corpse run ok')
    # disciplines grow by use
    r0 = p.disc['fire'][0]
    for _ in range(40):
        from cursed_vale import skills as SK
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
    from cursed_vale import events as EV
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
    road = [w.danger_at(x, y) for (x, y) in random.sample([(i % 200, i // 200) for i in range(len(g.maps['over'].t))
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
    from cursed_vale.entities import make_monster
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
    from cursed_vale.entities import make_tome, random_gear, make_gear, add_curse
    from cursed_vale import skills as SK, evils as EVL
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
    g.unequip('ring')
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
    g.unequip('ring')
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
    from cursed_vale import races as RC, evils as EVL, lifeskills as LS
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
    from cursed_vale import crime as CR, events as EV
    from cursed_vale.money import fmt
    random.seed(17)
    assert fmt(0) == '0c' and fmt(12345) == '1g 23s 45c' and fmt(205) == '2s 5c', fmt(12345)
    app = new_app('soft', 2024)
    g = app.game
    p = g.player
    p.vit, p.str, p.lvl = 300, 90, 10
    p.life = g.stats()['max_life']
    # coins are rare: kill a pack of wolves, no coins; bandits sometimes
    g.enter_dungeon('rat', 1, 'up')
    from cursed_vale.entities import make_monster
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
    from cursed_vale import hunger as HU, crime as CR
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
    from cursed_vale import foraging as FG, lifeskills as LS, sites as ST
    from cursed_vale.entities import make_monster
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
    from cursed_vale import calendar as CAL, gods as GD, brewing as BR, hunger as HU, lifeskills as LS
    from cursed_vale import describe as DS, worldgen as WG
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
    from cursed_vale import towns as TWN
    s0 = g.world.settlements[0]
    assert len({e[2] for e in m.exits}) == len(TWN.road_dirs(g, s0)), (m.exits, TWN.road_dirs(g, s0))
    for ex, ey, _o in m.exits:
        assert ex in (0, m.w - 1) or ey in (0, m.h - 1), 'exits are on the edge of the map'
        assert (ex, ey) in seen, 'every road out leads to the middle of town'
    assert m.w >= ui.MAP_W and m.h >= ui.MAP_H, 'villages fill the screen'
    # street lamps and the lamplighter who lights them at dusk
    from cursed_vale import towns as TW, dress as DR
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
    # the Tab menu opens other screens by their hotkey
    app.screens = [ui.GameScreen(app)]
    app.key('tab')
    assert isinstance(app.top, ui.MenuScreen)
    app.render()
    app.key('i')
    assert isinstance(app.top, ui.InventoryScreen), app.top
    app.key('esc')
    app.key('tab')
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
    from cursed_vale import weather as WX, ai as AI, missions as MS2
    from cursed_vale.entities import make_monster
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


def main():
    random.seed(int(os.environ.get('TEST_SEED', '1')))
    world_life()
    thornfield_and_faith()
    countryside()
    start_and_survival()
    crime_and_coin()
    world_and_people()
    items_skills_curse()
    smoke()
    trade_and_jobs()
    factions_and_death()
    wilds()


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
