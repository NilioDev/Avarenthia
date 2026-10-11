"""Record the weather effects as animated GIFs (for checking the look without playing).

Usage: python tools/weather_demo.py OUT_DIR"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from PIL import Image  # noqa: E402

from cursed_vale import ui, engine as E, weather as WX  # noqa: E402
from cursed_vale.canvas import FakeCanvas  # noqa: E402
from tools.screenshot import save  # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
T = [0.0]
ui.time.monotonic = lambda: T[0]


def record(app, kind, name, frames=36, dt=.1):
    imgs = []
    g = app.game
    for k in range(frames):
        T[0] = 50 + k * dt
        app.render()
        p = g.player
        ox, oy = app.top.origin
        WX.apply(app.cv, 0, 0, ui.MAP_W, ui.MAP_H, kind, T[0], centre=(p.x - ox, p.y - oy))
        app.cv.text(2, 1, f' {WX.NAMES[kind]} ', (255, 236, 190), (20, 16, 12))
        tmp = os.path.join(OUT, '_frame.png')
        save(app.cv, tmp)
        im = Image.open(tmp).convert('RGB').crop((0, 0, ui.MAP_W * 8, ui.MAP_H * 8))
        im = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
        imgs.append(im.convert('P', palette=Image.ADAPTIVE, colors=255))
    path = os.path.join(OUT, f'weather_{name}.gif')
    imgs[0].save(path, save_all=True, append_images=imgs[1:], duration=int(dt * 1000), loop=0)
    os.remove(tmp)
    return path


def scene(where):
    random.seed(4)
    app = ui.App(FakeCanvas(ui.W, ui.H))
    g = E.Game('Aldric', False, seed=None, race='human', gender='male')
    app.start_game(g)
    g.request = None
    g.turn = 130                       # late morning
    if where == 'village':
        g.enter_town(0)
        g.request = None
        m = g.map
        g.player.x, g.player.y = m.w // 2 - 10, m.h // 2
    else:
        s = g.world.settlements[0]
        g.cur = 'over'
        g.player.x, g.player.y = s.x + 3, s.y + 2
        g.over_pos = (s.x, s.y)
    g.pending = None
    g.compute_fov()
    m = g.map
    g.vis = bytearray([1]) * len(m.t)
    for i in range(len(m.seen)):
        m.seen[i] = 1
    app.screens = [ui.GameScreen(app)]
    app.render()
    return app


if __name__ == '__main__':
    village, land = scene('village'), scene('over')
    for kind, app in (('rain', village), ('storm', village), ('snow', land), ('fog', land), ('heat', land)):
        print(record(app, kind, kind))
