"""Weather, drawn over the map: rain, thunderstorms, snow, fog and scorching heat.

Each effect is painted on top of the finished map view, cell by cell, from the time alone (no particles to
keep track of): a raindrop is wherever a hash of its falling position says there is one, so the picture
moves smoothly on its own clock, whatever the player does. Colours shift too: rain greys and darkens the
land, snow whitens it, fog swallows what is far away, heat bleaches everything and makes the air wobble."""
import math

from .look import _h

KINDS = ['clear', 'rain', 'storm', 'snow', 'fog', 'heat']
NAMES = {'clear': 'Clear', 'rain': 'Rain', 'storm': 'Thunderstorm', 'snow': 'Snow', 'fog': 'Fog', 'heat': 'Scorching heat'}


def _mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return (round(a[0] + (b[0] - a[0]) * t), round(a[1] + (b[1] - a[1]) * t), round(a[2] + (b[2] - a[2]) * t))


def _grey(c):
    v = (c[0] * 3 + c[1] * 4 + c[2] * 3) // 10
    return (v, v, v)


def _noise2(x, y, s=0):
    """Smooth 2-d value noise in 0..1."""
    xi, yi = math.floor(x), math.floor(y)
    fx, fy = x - xi, y - yi
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a = _h(xi, yi, s) / 65535
    b = _h(xi + 1, yi, s) / 65535
    c = _h(xi, yi + 1, s) / 65535
    d = _h(xi + 1, yi + 1, s) / 65535
    return (a + (b - a) * fx) + ((c + (d - c) * fx) - (a + (b - a) * fx)) * fy


def flash(t, seed=0):
    """Lightning: how bright the sky is right now (0 most of the time)."""
    period = 3.1
    k = int(t / period)
    if _h(k, 7, seed) % 3 == 0:                # not every period has a strike
        return 0.0
    when = (_h(k, 8, seed) % 1000) / 1000 * (period - .6)
    dt = t - k * period - when
    if 0 <= dt < .08 or .16 <= dt < .22:       # a strike flickers twice
        return 1.0
    if .08 <= dt < .5:
        return .25 * (1 - (dt - .08) / .42)
    return 0.0


def apply(cv, x0, y0, w, h, kind, t, strength=1.0, centre=None):
    """Paint weather over the rectangle (x0, y0, w, h) of a canvas. centre: the player's cell, for fog."""
    if kind == 'clear':
        return
    cx, cy = centre or (x0 + w // 2, y0 + h // 2)
    lightning = flash(t) if kind == 'storm' else 0.0
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            ch, fg, bg = cv.get(x, y)
            lx, ly = x - x0, y - y0
            if kind in ('rain', 'storm'):
                heavy = kind == 'storm'
                # the land goes grey and dark under the clouds, and wet things gleam
                fg = _mix(_mix(fg, _grey(fg), .35), (60, 74, 96), .18 if not heavy else .3)
                bg = _mix(_mix(bg, (14, 18, 26), .35 if not heavy else .5), _grey(bg), .2)
                if lightning:
                    fg = _mix(fg, (240, 244, 255), lightning * .75)
                    bg = _mix(bg, (150, 160, 200), lightning * .8)
                # falling streaks: each column of rain slides down and a little to the side
                speed = 26 if heavy else 18
                slant = .45 if heavy else .25
                u = ly - t * speed
                col = lx + u * slant
                cell = (_h(int(math.floor(col)), int(math.floor(u / 3)), 41) % (9 if heavy else 15))
                if cell == 0:
                    ch, fg = ('/' if slant > .3 else '│') if (int(u) % 3) else '\'', _mix((150, 170, 210), fg, .2)
                elif cell == 1 and heavy:
                    ch, fg = '/', (110, 128, 170)
                elif (_h(lx, ly, int(t * 7)) % (60 if heavy else 110)) == 0:
                    ch, fg = ('°' if _h(lx, ly, 3) % 2 else '·'), (170, 190, 230)     # a splash
            elif kind == 'snow':
                # everything whitens; open ground lies under a blanket of snow, in drifts
                drift = _noise2(lx * .18, ly * .25, 18)
                fg = _mix(fg, (220, 228, 240), .3)
                bg = _mix(bg, _mix((52, 58, 72), (110, 118, 134), drift), .55)
                if ch in '.,\'`"' and drift > .45:
                    ch = ' '                    # the grass is buried
                # flakes fall slowly and sway; near ones are big and bright, far ones small and dim
                for layer, (speed, gap, glyph, bright) in enumerate(((3.2, 61, '*', 1.0), (2.0, 43, '∙', .85), (1.2, 31, '·', .65))):
                    u = ly - t * speed
                    sway = math.sin(t * .9 + u * .35 + layer) * 1.4
                    col = lx + sway
                    if _h(int(round(col)), int(math.floor(u)), 51 + layer) % gap == 0:
                        ch, fg = glyph, _mix((150, 160, 180), (255, 255, 255), bright)
                        break
            elif kind == 'fog':
                # the further from you, the more the fog swallows; it drifts in slow banks
                d = math.hypot((x - cx), (y - cy) * 1.0)
                bank = _noise2(lx * .09 + t * .12, ly * .14, 61) * .6 + _noise2(lx * .21 - t * .07, ly * .3, 62) * .4
                thick = max(0.0, min(1.0, (d - 3) / 9)) * .75 + bank * .45
                fogc = _mix((96, 102, 108), (140, 146, 150), bank)
                fg = _mix(fg, fogc, min(1, thick * 1.1))
                bg = _mix(bg, _mix((44, 48, 52), (70, 74, 78), bank), min(1, thick))
                if thick > .85:
                    ch = '░' if bank > .62 and _h(lx, ly, 63) % 3 == 0 else ' '
                    fg = _mix(bg, (150, 156, 160), .35)
            elif kind == 'heat':
                # bleached, warm, overexposed; the air above the ground shimmers
                fg = _mix(fg, (255, 232, 170), .3)
                fg = _mix(fg, _grey(fg), .25)
                bg = _mix(bg, (70, 52, 26), .3)
                wob = math.sin(t * 6 + ly * 1.7) + math.sin(t * 3.3 - ly * .9 + lx * .05)
                if wob > 1.45 and lx + 1 < w:      # this row of air bends: show the neighbour's glyph
                    nch, nfg, _nbg = cv.get(x + 1, y)
                    ch, fg = nch, _mix(nfg, (255, 236, 180), .35)
                glare = max(0.0, 1 - math.hypot(lx - w * .7, (ly - h * .2) * 1.6) / (w * .7))
                fg = _mix(fg, (255, 250, 230), glare * .35)
                bg = _mix(bg, (120, 96, 50), glare * .3)
                if _h(int(lx + t * 6), ly, 71) % 97 == 0:          # dust drifting on a hot wind
                    ch, fg = '·', (220, 190, 130)
            cv.put(x, y, ch, fg, bg)
