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
        g.player.gold = 5000
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
    g.player.gold = 400
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
            print(f'  job ok: {mi.kind:8} {mi.title} ({mi.reward}g)')
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
    p.gold = 2000
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
        print(f'  traveller job ok: {sub:6} {mi.title} ({mi.reward}g)')
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
    assert sorted(i.base for i in p.inv if i.k == 'gear') == ['quilted', 'shortbow', 'shortsword']
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
    p.gold = 5000
    g.enter_town(0)
    temple = next((o for o in g.map.mons if o.role == 'healer'), None)
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
    p.lvl = 20
    EVL.update(g)
    to_over(g, 0)
    for _ in range(40):
        EVL.daily(g)
    hunts = [w for w in g.world.wanderers if w.kind == 'hunt']
    print('at level 20:', [(e.name, EVL.stage(e)) for e in g.world.evils], 'tainted cells', tainted(), 'hunters', len(hunts))
    assert hunts and tainted() > 300
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


def main():
    random.seed(int(os.environ.get('TEST_SEED', '1')))
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
