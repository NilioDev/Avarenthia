"""Record the weather effects as animated GIFs (for checking the look without playing).

Usage: python tools/weather_demo.py OUT_DIR
Writes weather_catalog.gif (every kind side by side) and one larger GIF per kind."""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from PIL import Image, ImageDraw  # noqa: E402

from cursed_vale import ui, engine as E, weather as WX  # noqa: E402
from cursed_vale.canvas import FakeCanvas  # noqa: E402
from cursed_vale.glyphs import TILE_W, TILE_H  # noqa: E402
from tools.screenshot import save  # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
T = [0.0]
ui.time.monotonic = lambda: T[0]

# kind -> scene it is shown on
CATALOG = [
    ('drizzle', 'village'), ('rain', 'village'), ('downpour', 'village'), ('storm', 'village'),
    ('snow_light', 'land'), ('snow', 'land'), ('blizzard', 'land'), ('hail', 'village'),
    ('mist', 'land'), ('fog', 'land'), ('fog_thick', 'land'), ('miasma', 'land'),
    ('clouds', 'land'), ('wind', 'land'), ('warm', 'land'), ('heat', 'land'),
    ('sandstorm', 'land'), ('ash', 'land'), ('blood', 'village'), ('fireflies', 'night'),
]
EXTRA = [('aurora', 'night')]


def scene(where):
    """A rendered map view to put weather on: (canvas, player cell in view)."""
    random.seed(4)
    app = ui.App(FakeCanvas(ui.W, ui.H))
    g = E.Game('Aldric', False, seed=None, race='human', gender='male')
    app.start_game(g)
    g.request = None
    g.turn = 130 if where != 'night' else 270
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
    if where != 'night':
        g.vis = bytearray([1]) * len(m.t)
    for i in range(len(m.seen)):
        m.seen[i] = 1
    app.screens = [ui.GameScreen(app)]
    app.render()
    ox, oy = app.top.origin
    return app.cv, (g.player.x - ox, g.player.y - oy)


def cut(base, px, py, w, h):
    """A w x h piece of a canvas around (px, py), as a canvas of its own."""
    x0 = max(0, min(ui.MAP_W - w, px - w // 2))
    y0 = max(0, min(ui.MAP_H - h, py - h // 2))
    cv = FakeCanvas(w, h)
    for y in range(h):
        for x in range(w):
            ch, fg, bg = base.get(x0 + x, y0 + y)
            cv.put(x, y, ch, fg, bg)
    return cv, (px - x0, py - y0)


def frame(piece, kind, t):
    cv0, centre = piece
    cv = FakeCanvas(cv0.w, cv0.h)
    cv.ch, cv.fg, cv.bg = list(cv0.ch), list(cv0.fg), list(cv0.bg)
    WX.apply(cv, 0, 0, cv.w, cv.h, kind, t, centre=centre)
    tmp = os.path.join(OUT, '_p.png')
    save(cv, tmp)
    return Image.open(tmp).convert('RGB')


def catalog(scenes, frames=30, dt=.12, pw=34, ph=22, cols=4):
    pieces = {k: cut(scenes[s][0], *scenes[s][1], pw, ph) for k, s in CATALOG}
    rows = (len(CATALOG) + cols - 1) // cols
    cw, chh = pw * TILE_W, ph * TILE_H
    gap, label = 6, 14
    imgs = []
    for f in range(frames):
        t = 50 + f * dt
        sheet = Image.new('RGB', (cols * (cw + gap) + gap, rows * (chh + gap + label) + gap), (12, 10, 9))
        d = ImageDraw.Draw(sheet)
        for i, (kind, _s) in enumerate(CATALOG):
            x = gap + (i % cols) * (cw + gap)
            y = gap + (i // cols) * (chh + gap + label)
            d.text((x + 2, y), WX.NAMES[kind], fill=(236, 200, 130))
            sheet.paste(frame(pieces[kind], kind, t), (x, y + label))
        imgs.append(sheet.convert('P', palette=Image.ADAPTIVE, colors=255))
    path = os.path.join(OUT, 'weather_catalog.gif')
    imgs[0].save(path, save_all=True, append_images=imgs[1:], duration=int(dt * 1000), loop=0)
    return path


def single(scenes, kind, where, frames=36, dt=.1):
    piece = cut(scenes[where][0], *scenes[where][1], 64, 40)
    imgs = []
    for f in range(frames):
        im = frame(piece, kind, 50 + f * dt)
        im = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
        imgs.append(im.convert('P', palette=Image.ADAPTIVE, colors=255))
    path = os.path.join(OUT, f'weather_{kind}.gif')
    imgs[0].save(path, save_all=True, append_images=imgs[1:], duration=int(dt * 1000), loop=0)
    return path


if __name__ == '__main__':
    scenes = {w: scene(w) for w in ('village', 'land', 'night')}
    print(catalog(scenes))
    for kind, where in (('blizzard', 'land'), ('sandstorm', 'land'), ('ash', 'land'), ('aurora', 'night'),
                        ('fireflies', 'night'), ('wind', 'land'), ('clouds', 'land'), ('hail', 'village')):
        print(single(scenes, kind, where))
    os.remove(os.path.join(OUT, '_p.png'))
