"""Headless tests: drive the real UI and engine with key tokens on a fake canvas.
Run from the project folder:  python tests/test_headless.py
"""
import os
import random
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cursed_vale import engine as E, data as D, ui  # noqa: E402
from cursed_vale.canvas import FakeCanvas  # noqa: E402

E.save_path = lambda: os.path.join(tempfile.gettempdir(), 'cursed_vale_test.dat')

TOKENS = ['up', 'down', 'left', 'right', 'y', 'u', 'b', 'n', 'np5', 'g', 'R', '1', '2', '3', 'q', 'w', 'p', 'x', 't',
          '>', '<', 'enter', 'i', 'c', 'd', 'esc', 'a', 'b', 'tab', 'H', 'L', 'D', '?', '4', 'down', 'enter']


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


def smoke(games=12, steps=1500):
    for gi in range(games):
        cls = D.CLASS_ORDER[gi % 3]
        app = new_app(cls)
        g = app.game
        g.player.vit = 400
        g.player.lvl = 8
        for s in D.SKILLS[cls]:
            g.player.skills[s.id] = 3
        for step in range(steps):
            if step % 150 == 0:
                app.screens = [ui.GameScreen(app)]
                did = D.DUNGEON_ORDER[(step // 150) % 3]
                g.enter_dungeon(did, random.randint(1, D.DUNGEONS[did]['depth']), 'up')
            if step % 400 == 200:
                app.screens = [ui.GameScreen(app)]
                g.cur = 'over'
                g.player.x, g.player.y = g.town_pos[0], g.town_pos[1] + 1
                g.compute_fov()
            g.player.mana = 999
            app.key(random.choice(TOKENS), random.random() < .1)
            app.render()
            if not app.running:
                app.running = True
            if g.dead or isinstance(app.top, ui.WinScreen):
                break
        # every screen must render
        for S in (ui.InventoryScreen, ui.CharacterScreen, ui.ShopScreen, ui.TravelScreen, ui.HelpScreen,
                  ui.DeathScreen, ui.WinScreen, ui.QuitScreen):
            app.screens = [ui.GameScreen(app), S(app)]
            app.render()
        E.save_game(g)
        assert E.load_game() is not None or g.dead
    print('smoke ok')


if __name__ == '__main__':
    random.seed(1)
    smoke()
    app = new_app('barbarian')
    app.hover = (35, 14)
    app.render()
    print(app.cv.dump())
