"""Weather, drawn over the map.

Each effect is painted on top of the finished map view, cell by cell, from the time alone (no particles to
keep track of): a raindrop is wherever a hash of its falling position says there is one, so the picture moves
smoothly on its own clock, whatever the player does. Colours shift too: rain greys and darkens the land, snow
whitens it, fog swallows what is far away, heat bleaches everything and makes the air wobble.

Weather comes in families with grades: drizzle, rain, downpour and thunderstorm; light snow, snow and blizzard;
morning mist, fog and thick fog; warm and scorching. Then there are the odd ones: hail, a sandstorm, drifting
cloud shadows, an autumn wind, and the ones that mean trouble: falling ash near a dragon, a sickly miasma over
the marshes, blood rain. On clear summer nights there are fireflies, and in the far north the northern lights.

Every effect leaves what is on the map readable: it tints and veils, and only draws its own glyphs on open
ground, never over people, walls or items."""
import math

from .look import _h

# kind: (name, family, grade 1-3)
KINDS = {
    'clear': ('Clear', 'clear', 0),
    'drizzle': ('Drizzle', 'rain', 1), 'rain': ('Rain', 'rain', 2), 'downpour': ('Downpour', 'rain', 3),
    'storm': ('Thunderstorm', 'rain', 3),
    'snow_light': ('Light snow', 'snow', 1), 'snow': ('Snow', 'snow', 2), 'blizzard': ('Blizzard', 'snow', 3),
    'hail': ('Hail', 'hail', 2),
    'mist': ('Morning mist', 'fog', 1), 'fog': ('Fog', 'fog', 2), 'fog_thick': ('Thick fog', 'fog', 3),
    'clouds': ('Cloud shadows', 'clouds', 1), 'wind': ('Autumn wind', 'wind', 2),
    'warm': ('Warm', 'heat', 1), 'heat': ('Scorching heat', 'heat', 3), 'sandstorm': ('Sandstorm', 'sand', 3),
    'ash': ('Falling ash', 'ash', 2), 'miasma': ('Miasma', 'miasma', 2), 'blood': ('Blood rain', 'rain', 2),
    'fireflies': ('Fireflies', 'night', 1), 'aurora': ('Northern lights', 'night', 2),
}
NAMES = {k: v[0] for k, v in KINDS.items()}
GROUND = set(' .,\'`"·∙')          # cells with nothing in them but the ground: weather may draw here


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
    top = a + (b - a) * fx
    return top + ((c + (d - c) * fx) - top) * fy


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


def _streak(lx, ly, t, curtains, slant):
    """How bright a falling streak is on this cell (0..1). curtains: (strength, speed, tail, period, chance)."""
    a = 0.0
    for sd, (strength, speed, tail, period, chance) in enumerate(curtains):
        lane = round(lx - ly * slant + sd * 7)
        off = (_h(lane, sd, 41) % 1000) / 1000 * period
        pos = t * speed + off - ly
        k = math.floor(pos / period)
        if (_h(lane, k, 42 + sd) % 100) >= chance * 100:
            continue
        d = pos - k * period
        if d < tail:
            a = max(a, (1 - d / tail) * strength)
    return a


def _ripple(lx, ly, t, rate):
    """A ring spreading on a puddle where a drop landed: one of · ∙ o ○ as it grows and fades, or None."""
    phase = t * rate + (_h(lx, ly, 33) % 100) / 100 * 7
    slot = int(phase)
    if _h(lx, ly, 34 + slot) % 9:
        return None, 0.0
    age = phase - slot
    return '·∙o○'[min(3, int(age * 4))], 1 - age


# ------------------------------------------------------------------ rain
RAIN = {  # grade: darkening, curtains, slant, puddles
    'drizzle': (.12, ((.7, 20, 2, 19, .22),), .12, False),
    'rain': (.3, ((1.0, 22, 3, 17, .3), (.6, 17, 2, 13, .18)), .2, False),
    'downpour': (.42, ((1.0, 28, 4, 14, .45), (.7, 22, 3, 11, .35)), .3, True),
    'storm': (.48, ((1.0, 30, 3, 15, .42), (.75, 23, 2, 12, .3)), .45, True),
    'blood': (.35, ((1.0, 20, 3, 17, .32), (.6, 16, 2, 13, .2)), .18, True),
}


def rain_cell(kind, ch, fg, bg, lx, ly, t, lightning=0.0):
    dark, curtains, slant, puddles = RAIN[kind]
    blood = kind == 'blood'
    tone = (110, 40, 40) if blood else (70, 84, 110)
    fg = _mix(_mix(fg, _grey(fg), dark), tone, dark * .6)
    bg = _mix(_mix(bg, (24, 8, 8) if blood else (12, 16, 24), dark), _grey(bg), dark * .4)
    ground = ch in GROUND
    if puddles and ground:
        pool = _noise2(lx * .16, ly * .22, 37)
        if pool > .66:
            bg = _mix(bg, (70, 14, 14) if blood else (30, 40, 58), min(1, (pool - .66) * 5))
            ring, life = _ripple(lx, ly, t, 2.6)
            if ring:
                ch, fg = ring, _mix(bg, (230, 90, 90) if blood else (170, 190, 225), .3 + .6 * life)
    a = _streak(lx, ly, t, curtains, slant)
    if a > 0:
        rc = (220, 70, 70) if blood else (170, 192, 232)
        bg = _mix(bg, rc, a * .22)
        if ground and a > .6:
            ch = '/' if slant > .35 else '|'
            fg = _mix(bg, rc, .35 + a * .5)
        else:
            fg = _mix(fg, rc, a * .3)
    if lightning:
        fg = _mix(fg, (240, 244, 255), lightning * .7)
        bg = _mix(bg, (150, 160, 200), lightning * .75)
    return ch, fg, bg


# ------------------------------------------------------------------ snow and hail
def snow_cell(kind, ch, fg, bg, lx, ly, t, dist):
    grade = KINDS[kind][2]
    drift = _noise2(lx * .18, ly * .25, 18)
    ground = ch in GROUND
    lying = drift > (.62, .4, .25)[grade - 1]               # where the snow lies, in drifts
    fg = _mix(fg, (220, 228, 240), .12 + .1 * grade)
    bg = _mix(bg, (30, 34, 44), .3)
    if lying and (ground or ch in '♣♠↑∩n"^▲'):
        depth = min(1.0, (drift - (.62, .4, .25)[grade - 1]) * 4)
        bg = _mix(bg, _mix((120, 126, 140), (196, 202, 214), depth), (.55, .75, .9)[grade - 1])
        if ground:
            ch = ' '                            # the grass is buried
        else:
            fg = _mix(fg, (60, 70, 80), .5)     # trees and hills stand dark against the snow
    if kind == 'blizzard':
        # wind-driven: the snow flies sideways and the world turns white past a few steps
        white = max(0.0, min(1.0, (dist - 2.5) / 6)) * .85 + _noise2(lx * .2 + t * 1.5, ly * .4, 19) * .25
        fg = _mix(fg, (214, 220, 230), white)
        bg = _mix(bg, (150, 156, 168), white * .9)
        u = lx - t * 34
        lane = ly + round(math.sin(u * .2 + ly) * .6)
        k = _h(int(math.floor(u / 2)), lane, 52) % 7
        if k == 0:
            ch, fg = ('─' if _h(lane, int(u), 53) % 2 else '-'), (240, 244, 250)
        elif k == 1 and ground:
            ch, fg = '·', (230, 236, 246)
        return ch, fg, bg
    layers = ((3.2, 61, '*', 1.0), (2.0, 43, '∙', .85), (1.2, 31, '·', .65))
    for layer, (speed, gap, glyph, bright) in enumerate(layers[3 - grade:] if grade < 3 else layers):
        gap = round(gap * (1.8 if grade == 1 else 1))
        u = ly - t * speed
        sway = math.sin(t * .9 + u * .35 + layer) * 1.4
        if _h(int(round(lx + sway)), int(math.floor(u)), 51 + layer) % gap == 0:
            if ch == ' ' or ground or glyph != '*':
                ch = glyph
            fg = _mix((200, 206, 220), (255, 255, 255), bright)
            if lying:
                fg = _mix((80, 90, 110), (40, 48, 64), bright)    # dark flakes against white snow
            break
    return ch, fg, bg


def hail_cell(ch, fg, bg, lx, ly, t):
    fg = _mix(_mix(fg, _grey(fg), .4), (120, 130, 150), .2)
    bg = _mix(bg, (18, 20, 26), .4)
    ground = ch in GROUND
    a = _streak(lx, ly, t, ((1.0, 40, 2, 11, .35),), .08)
    if a > .5:
        if ground:
            ch = '∙'
        fg = (236, 240, 250)
    elif ground and _h(lx, ly, int(t * 9)) % 23 == 0:
        ch, fg = ('o' if _h(lx, ly, int(t * 9) + 1) % 3 else '°'), (220, 228, 240)     # a stone bouncing
    elif ground and _noise2(lx * .3, ly * .3, 56) > .72:
        ch, fg = '·', (200, 206, 216)                                                   # hailstones lying
    return ch, fg, bg


# ------------------------------------------------------------------ fog, mist and miasma
def fog_cell(kind, ch, fg, bg, lx, ly, t, dist):
    grade = KINDS[kind][2] if kind != 'miasma' else 2
    bank = _noise2(lx * .09 + t * .12, ly * .14, 61) * .6 + _noise2(lx * .21 - t * .07, ly * .3, 62) * .4
    if kind == 'mist':
        # morning mist lies in low wisps; you see far, but the land is veiled in patches
        k = max(0.0, bank - .35) * 2.2
        fg = _mix(fg, (190, 194, 196), min(1, k * .7))
        bg = _mix(bg, (110, 114, 118), min(1, k * .75))
        if k > .75 and ch in GROUND:
            ch, fg = '░', _mix(bg, (200, 204, 206), .3)
        return ch, fg, bg
    reach = (0, 9, 5)[grade - 1] if kind != 'miasma' else 7
    thick = max(0.0, min(1.0, (dist - 2.5) / reach)) * (.75 if grade == 2 else .95) + bank * .45
    if kind == 'miasma':
        fogc, deep = _mix((90, 110, 50), (140, 160, 70), bank), _mix((30, 40, 18), (52, 64, 26), bank)
    else:
        fogc, deep = _mix((96, 102, 108), (140, 146, 150), bank), _mix((44, 48, 52), (70, 74, 78), bank)
    fg = _mix(fg, fogc, min(1, thick * 1.1))
    bg = _mix(bg, deep, min(1, thick))
    if thick > .85 and ch in GROUND | set('♣♠↑∩n^▲~≈'):
        ch = '░' if bank > .62 and _h(lx, ly, 63) % 3 == 0 else ' '
        fg = _mix(bg, fogc, .35)
    if kind == 'miasma' and ch in GROUND:      # bubbles rising from the bog
        phase = t * 1.5 + (_h(lx, ly, 64) % 100) / 100 * 5
        if _h(lx, ly, 65 + int(phase)) % 37 == 0:
            ch, fg = '°o·'[min(2, int((phase % 1) * 3))], (190, 210, 90)
    return ch, fg, bg


# ------------------------------------------------------------------ clouds and wind
def cloud_cell(ch, fg, bg, lx, ly, t):
    # the shadows of big clouds sail over the land
    n = _noise2(lx * .05 - t * .35, ly * .08 - t * .1, 71) * .7 + _noise2(lx * .11 - t * .5, ly * .17, 72) * .3
    k = max(0.0, min(1.0, (n - .42) * 5))
    fg = _mix(fg, _mix(fg, (30, 40, 60), .7), k)
    bg = _mix(bg, _mix(bg, (4, 6, 12), .75), k)
    if k < .05:                                    # and where the sun breaks through, the land glows
        fg = _mix(fg, (255, 240, 200), .18)
    return ch, fg, bg


LEAF = [(220, 120, 40), (200, 80, 30), (230, 180, 60), (160, 60, 30)]


def wind_cell(ch, fg, bg, lx, ly, t):
    # gusts run through the grass and the trees as waves of light
    gust = math.sin(lx * .25 - t * 5 + math.sin(ly * .3) * 2) * .5 + .5
    if ch in GROUND or ch in '♣♠↑"n∩':
        fg = _mix(fg, (230, 226, 170), gust ** 2 * .55)
        bg = _mix(bg, (40, 36, 20), gust ** 2 * .3)
    if ch in GROUND and gust > .8 and ch in '\'"`,':
        ch = '`' if ch in '\'"' else ','
    # leaves tumbling along on the wind
    u = lx - t * 18
    row = ly + round(math.sin(u * .3 + ly * 1.3 + t * 3) * .8)
    if _h(int(math.floor(u)), row, 74) % 19 == 0 and ch in GROUND | set('♣♠↑n∩'):
        ch = ',' if _h(int(u), row, 75) % 2 else '`'
        fg = LEAF[_h(row, int(u // 7), 76) % len(LEAF)]
    return ch, fg, bg


# ------------------------------------------------------------------ heat and sand
def heat_cell(kind, ch, fg, bg, lx, ly, t, w, h, neighbour):
    s = .45 if kind == 'warm' else 1.0
    fg = _mix(fg, (255, 232, 170), .3 * s)
    fg = _mix(fg, _grey(fg), .25 * s)
    bg = _mix(bg, (70, 52, 26), .3 * s)
    if kind == 'heat':
        wob = math.sin(t * 6 + ly * 1.7) + math.sin(t * 3.3 - ly * .9 + lx * .05)
        if wob > 1.45 and neighbour:            # this row of air bends: show the neighbour's glyph
            ch, fg = neighbour[0], _mix(neighbour[1], (255, 236, 180), .35)
        if _h(int(lx + t * 6), ly, 77) % 97 == 0:
            ch, fg = '·', (220, 190, 130)
    glare = max(0.0, 1 - math.hypot(lx - w * .7, (ly - h * .2) * 1.6) / (w * .7))
    fg = _mix(fg, (255, 250, 230), glare * .35 * s)
    bg = _mix(bg, (120, 96, 50), glare * .3 * s)
    return ch, fg, bg


def sand_cell(ch, fg, bg, lx, ly, t, dist):
    # walls of dust race across the land; you see a few steps, then only ochre
    band = _noise2(lx * .12 - t * 2.6, ly * .5, 81) * .65 + _noise2(lx * .3 - t * 4, ly * .9, 82) * .35
    k = max(0.0, min(1.0, (dist - 2) / 7)) * .7 + band * .5
    fg = _mix(fg, (214, 170, 100), min(1, k))
    bg = _mix(bg, _mix((90, 62, 28), (150, 110, 56), band), min(1, k * .95))
    if ch in GROUND | set('♣♠↑∩n"') and band > .55:
        ch = '░' if band > .72 else ('~' if _h(lx, ly, 83) % 3 else ' ')
        fg = _mix(bg, (236, 200, 140), .4)
    u = lx - t * 30
    if _h(int(math.floor(u)), ly, 84) % 19 == 0 and ch in GROUND | set('░~'):
        ch, fg = '─', (240, 210, 150)
    return ch, fg, bg


# ------------------------------------------------------------------ omens
def ash_cell(ch, fg, bg, lx, ly, t):
    fg = _mix(_mix(fg, _grey(fg), .45), (120, 70, 50), .2)
    bg = _mix(bg, (30, 14, 10), .45)
    ground = ch in GROUND
    if ground and _noise2(lx * .2, ly * .2, 91) > .55:
        ch, fg = '.', (110, 104, 100)          # a grey film over everything
    for layer, (speed, gap, glyph, col) in enumerate(((1.4, 17, '∙', (190, 184, 180)), (.9, 13, '·', (140, 134, 130)))):
        u = ly - t * speed
        sway = math.sin(t * .6 + u * .25 + layer * 2) * 2
        if _h(int(round(lx + sway)), int(math.floor(u)), 92 + layer) % gap == 0:
            if ground or ch == '.':
                ch = glyph
            fg = col
            return ch, fg, bg
    u = ly + t * 2.2                            # embers rise, glowing
    sway = math.sin(t * 1.3 + u * .4) * 1.5
    if _h(int(round(lx + sway)), int(math.floor(u)), 94) % 97 == 0:
        glow = .5 + .5 * math.sin(t * 9 + lx)
        ch, fg = ('*' if glow > .6 else '·'), _mix((200, 60, 20), (255, 200, 80), glow)
    return ch, fg, bg


# ------------------------------------------------------------------ night
def firefly_cell(ch, fg, bg, lx, ly, t):
    return ch, fg, bg                           # the flies are drawn in a pass of their own


def fireflies(cv, x0, y0, w, h, t, n=None):
    n = n or w * h // 35
    for k in range(n):
        bx = (_h(k, 1, 101) % 1000) / 1000 * w
        by = (_h(k, 2, 101) % 1000) / 1000 * h
        x = int(bx + math.sin(t * .4 + k) * 3 + math.sin(t * 1.1 + k * 2) * 1)
        y = int(by + math.cos(t * .33 + k * 1.7) * 2)
        glow = math.sin(t * (1.5 + (k % 5) * .3) + k * 2.1)
        if glow < .2 or not (0 <= x < w and 0 <= y < h):
            continue
        ch, fg, bg = cv.get(x0 + x, y0 + y)
        col = _mix((90, 120, 30), (230, 255, 120), glow)
        cv.put(x0 + x, y0 + y, '·' if glow < .7 else '∙' if ch not in GROUND else '*', col, _mix(bg, (60, 80, 20), glow * .4))
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if 0 <= x + dx < w and 0 <= y + dy < h:
                c2, f2, b2 = cv.get(x0 + x + dx, y0 + y + dy)
                cv.put(x0 + x + dx, y0 + y + dy, c2, _mix(f2, col, glow * .25), _mix(b2, (50, 70, 18), glow * .25))


def aurora_cell(ch, fg, bg, lx, ly, t):
    # curtains of green and violet light ripple across the sky, and the land below catches it
    wave = ly * .5 + math.sin(lx * .08 + t * .5) * 4 + math.sin(lx * .19 - t * .8) * 2
    band = math.sin(wave * .7 + t * .3) * .5 + .5
    bright = band ** 3 * (0.6 + 0.4 * math.sin(lx * .3 - t * 1.7))
    col = _mix((60, 230, 140), (160, 90, 230), _noise2(lx * .05 + t * .1, ly * .1, 111))
    fg = _mix(fg, col, bright * .35)
    bg = _mix(bg, _mix((4, 14, 18), col, .5), bright * .35)
    return ch, fg, bg


# ------------------------------------------------------------------ the painter
def apply(cv, x0, y0, w, h, kind, t, centre=None):
    """Paint weather over the rectangle (x0, y0, w, h) of a canvas. centre: the player's cell, for fog and snow."""
    if kind == 'clear':
        return
    cx, cy = centre or (x0 + w // 2, y0 + h // 2)
    lightning = flash(t) if kind == 'storm' else 0.0
    fam = KINDS[kind][1]
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            ch, fg, bg = cv.get(x, y)
            lx, ly = x - x0, y - y0
            dist = math.hypot(x - cx, y - cy)
            if fam == 'rain':
                ch, fg, bg = rain_cell(kind, ch, fg, bg, lx, ly, t, lightning)
            elif fam == 'snow':
                ch, fg, bg = snow_cell(kind, ch, fg, bg, lx, ly, t, dist)
            elif kind == 'hail':
                ch, fg, bg = hail_cell(ch, fg, bg, lx, ly, t)
            elif fam in ('fog', 'miasma'):
                ch, fg, bg = fog_cell(kind, ch, fg, bg, lx, ly, t, dist)
            elif kind == 'clouds':
                ch, fg, bg = cloud_cell(ch, fg, bg, lx, ly, t)
            elif kind == 'wind':
                ch, fg, bg = wind_cell(ch, fg, bg, lx, ly, t)
            elif fam == 'heat':
                nb = cv.get(x + 1, y) if lx + 1 < w else None
                ch, fg, bg = heat_cell(kind, ch, fg, bg, lx, ly, t, w, h, nb)
            elif kind == 'sandstorm':
                ch, fg, bg = sand_cell(ch, fg, bg, lx, ly, t, dist)
            elif kind == 'ash':
                ch, fg, bg = ash_cell(ch, fg, bg, lx, ly, t)
            elif kind == 'aurora':
                ch, fg, bg = aurora_cell(ch, fg, bg, lx, ly, t)
            else:
                continue
            cv.put(x, y, ch, fg, bg)
    if kind == 'fireflies':
        fireflies(cv, x0, y0, w, h, t)
