"""Record the weather effects as animated GIFs (for checking the look without playing).

Usage: python tools/weather_demo.py OUT_DIR
Writes weather_catalog.gif (every kind side by side) and one larger GIF per kind."""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from PIL import Image, ImageDraw  # noqa: E402

from avarenthia import ui, engine as E, weather as WX  # noqa: E402
from avarenthia.canvas import FakeCanvas  # noqa: E402
from avarenthia.glyphs import TILE_W, TILE_H  # noqa: E402
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
CATALOG2 = [
    ('dust', 'land'), ('sandstorm', 'land'), ('haboob', 'land'), ('drystorm', 'land'),
    ('freezing', 'village'), ('sleet', 'village'), ('dew', 'land'), ('whirlwind', 'land'),
    ('leaves', 'land'), ('blossom', 'village'), ('smoke', 'village'), ('meteors', 'night'),
]


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
    from avarenthia import data as D
    roofed = {D.FLOOR, D.PLANK, D.BED, D.TABLE, D.BARREL, D.ALTAR, D.ANVIL}
    shelter = set()
    if m.kind == 'town':
        for vy in range(ui.MAP_H):
            for vx in range(ui.MAP_W):
                if m.inb(vx + ox, vy + oy) and m.tile(vx + ox, vy + oy) in roofed:
                    shelter.add((vx, vy))
    return app.cv, (g.player.x - ox, g.player.y - oy), shelter


def cut(base, px, py, shelter, w, h):
    """A w x h piece of a canvas around (px, py), as a canvas of its own."""
    x0 = max(0, min(ui.MAP_W - w, px - w // 2))
    y0 = max(0, min(ui.MAP_H - h, py - h // 2))
    cv = FakeCanvas(w, h)
    for y in range(h):
        for x in range(w):
            ch, fg, bg = base.get(x0 + x, y0 + y)
            cv.put(x, y, ch, fg, bg)
    return cv, (px - x0, py - y0), {(x - x0, y - y0) for x, y in shelter}


def frame(piece, kind, t):
    cv0, centre, shelter = piece
    cv = FakeCanvas(cv0.w, cv0.h)
    cv.ch, cv.fg, cv.bg = list(cv0.ch), list(cv0.fg), list(cv0.bg)
    WX.apply(cv, 0, 0, cv.w, cv.h, kind, t, centre=centre, sheltered=shelter)
    tmp = os.path.join(OUT, '_p.png')
    save(cv, tmp)
    return Image.open(tmp).convert('RGB')


def catalog(scenes, frames=30, dt=.12, pw=34, ph=22, cols=4, items=None, name='weather_catalog'):
    items = items or CATALOG
    pieces = {k: cut(scenes[s][0], *scenes[s][1], scenes[s][2], pw, ph) for k, s in items}
    rows = (len(items) + cols - 1) // cols
    cw, chh = pw * TILE_W, ph * TILE_H
    gap, label = 6, 14
    imgs = []
    for f in range(frames):
        t = 50 + f * dt
        sheet = Image.new('RGB', (cols * (cw + gap) + gap, rows * (chh + gap + label) + gap), (12, 10, 9))
        d = ImageDraw.Draw(sheet)
        for i, (kind, _s) in enumerate(items):
            x = gap + (i % cols) * (cw + gap)
            y = gap + (i // cols) * (chh + gap + label)
            d.text((x + 2, y), WX.NAMES[kind], fill=(236, 200, 130))
            sheet.paste(frame(pieces[kind], kind, t), (x, y + label))
        imgs.append(sheet.convert('P', palette=Image.ADAPTIVE, colors=255))
    path = os.path.join(OUT, f'{name}.gif')
    imgs[0].save(path, save_all=True, append_images=imgs[1:], duration=int(dt * 1000), loop=0)
    return path


def single(scenes, kind, where, frames=36, dt=.1):
    piece = cut(scenes[where][0], *scenes[where][1], scenes[where][2], 64, 40)
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
    what = sys.argv[2] if len(sys.argv) > 2 else 'all'
    if what in ('all', '1'):
        print(catalog(scenes))
    if what in ('all', '2'):
        print(catalog(scenes, frames=40, items=CATALOG2, name='weather_catalog2'))
    singles = (('blizzard', 'land'), ('sandstorm', 'land'), ('ash', 'land'), ('aurora', 'night'),
               ('fireflies', 'night'), ('wind', 'land'), ('clouds', 'land'), ('hail', 'village'))
    if what in ('all', '2'):
        singles = (('haboob', 'land'), ('drystorm', 'land'), ('smoke', 'village'), ('whirlwind', 'land'),
                   ('meteors', 'night'), ('freezing', 'village'))
    for kind, where in singles:
        print(single(scenes, kind, where))
    os.remove(os.path.join(OUT, '_p.png'))
