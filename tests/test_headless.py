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

E.save_path = lambda: os.path.join(tempfile.gettempdir(), 'cursed_vale_test.dat')

TOKENS = ['up', 'down', 'left', 'right', 'y', 'u', 'b', 'n', 'np5', 'g', 'R', '1', '2', '3', 'q', 'w', 'p', 'x', 't',
          '>', '<', 'enter', 'i', 'c', 'd', 'esc', 'a', 'b', 'tab', 'H', 'L', 'D', '?', '4', 'down', 'enter', 'm', 'e',
          's', 'S', 'B', 'A']


def new_app(cls):
    app = ui.App(FakeCanvas(ui.W, ui.H))
    app.key('n')
    for ch in 'Test':
        app.key(ch)
    app.key('enter')
    app.key(str(D.CLASS_ORDER.index(cls) + 1))
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
        cls = D.CLASS_ORDER[gi % 3]
        app = new_app(cls)
        g = app.game
        g.player.vit = 400
        g.player.lvl = 8
        g.player.gold = 5000
        for s in D.SKILLS[cls]:
            g.player.skills[s.id] = 3
        dids = list(g.world.dungeons)
        for step in range(steps):
            if step % 150 == 0:
                app.screens = [ui.GameScreen(app)]
                did = dids[(step // 150) % len(dids)]
                g.enter_dungeon(did, random.randint(1, g.world.dungeons[did].depth), 'up')
            if step % 300 == 100:
                app.screens = [ui.GameScreen(app)]
                to_over(g, random.randrange(len(g.world.settlements)))
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
        for S in (ui.InventoryScreen, ui.CharacterScreen, ui.ShopScreen, ui.TravelScreen, ui.HelpScreen,
                  ui.DeathScreen, ui.WinScreen, ui.QuitScreen, ui.JournalScreen, ui.WorldMapScreen, ui.StablesScreen):
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
    g = E.Game('Trader', 'barbarian')
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


if __name__ == '__main__':
    random.seed(1)
    smoke()
    trade_and_jobs()
    if '--dump' in sys.argv:
        app = new_app('barbarian')
        app.render()
        sys.stdout.reconfigure(encoding='utf-8')
        print(app.cv.dump())
