"""Weather, drawn over the map.

Each effect is painted on top of the finished map view, cell by cell, from the time alone (no particles to
keep track of): a raindrop is wherever a hash of its falling position says there is one, so the picture moves
smoothly on its own clock, whatever the player does. Colours shift too: rain greys and darkens the land, snow
whitens it, fog swallows what is far away, heat bleaches everything and makes the air wobble.

Weather comes in families with grades: drizzle, rain, downpour and thunderstorm; light snow, snow and blizzard;
morning mist, fog and thick fog; warm and scorching; blowing dust, a sandstorm and a great sandstorm. Freezing
rain glazes the ground with ice, sleet turns it to slush, dew glitters in the morning; dry lightning strikes
without rain and sets the grass alight; a dust devil wanders over a plain; leaves fall in autumn and blossom
in spring; a burning village sends plumes of smoke over the land. Then there are the odd ones: hail, a sandstorm, drifting
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
    'warm': ('Warm', 'heat', 1), 'heat': ('Scorching heat', 'heat', 3),
    'dust': ('Blowing dust', 'sand', 1), 'sandstorm': ('Sandstorm', 'sand', 2), 'haboob': ('Great sandstorm', 'sand', 3),
    'freezing': ('Freezing rain', 'ice', 2), 'sleet': ('Sleet', 'sleet', 2), 'dew': ('Morning dew', 'dew', 1),
    'drystorm': ('Dry lightning', 'drystorm', 2), 'meteors': ('The Starfall', 'night', 1),
    'whirlwind': ('Whirlwind', 'whirl', 2), 'smoke': ('Smoke of a burning village', 'smoke', 2),
    'leaves': ('Falling leaves', 'leaves', 1), 'blossom': ('Spring blossom', 'leaves', 1),
    'ash': ('Falling ash', 'ash', 2), 'miasma': ('Miasma', 'miasma', 2), 'blood': ('Blood rain', 'rain', 2),
    'fireflies': ('Fireflies', 'night', 1), 'aurora': ('Northern lights', 'night', 2),
    'night': ('Clear', 'night', 0),
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


FRAME = {'ox': 0, 'oy': 0, 'wet': 0.0}      # set by the map drawing each frame: view offset and how wet it is
_RAIN_CACHE = {}


def frame(ox, oy, wet):
    FRAME['ox'], FRAME['oy'], FRAME['wet'] = ox, oy, wet
    if len(_RAIN_CACHE) > 30000:
        _RAIN_CACHE.clear()


def rain_cell(kind, ch, fg, bg, lx, ly, t, lightning=0.0):
    dark, curtains, slant, puddles = RAIN[kind]
    blood = kind == 'blood'
    mx, my = lx + FRAME['ox'], ly + FRAME['oy']          # puddles stay where they are on the land
    wet = FRAME['wet']
    key = (kind, mx, my, ch, fg, bg, round(wet * 10))
    pre = _RAIN_CACHE.get(key)
    if pre is None:                                       # the part that does not move: darker colours, puddles
        tone = (110, 40, 40) if blood else (70, 84, 110)
        fg0 = _mix(_mix(fg, _grey(fg), dark), tone, dark * .6)
        bg0 = _mix(_mix(bg, (24, 8, 8) if blood else (12, 16, 24), dark), _grey(bg), dark * .4)
        pool = 0.0
        if ch in GROUND and wet > .2:
            # small puddles in the hollows, growing the longer it rains and drying up after
            pool = _noise2(mx * .34, my * .46, 37) - (.9 - .14 * wet)
            if pool > 0:
                bg0 = _mix(bg0, (70, 14, 14) if blood else (30, 40, 58), min(1, pool * 12))
        pre = _RAIN_CACHE[key] = (fg0, bg0, pool > 0)
    fg, bg, in_pool = pre
    ground = ch in GROUND
    if in_pool:
        ring, life = _ripple(mx, my, t, 2.6)
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
    drift = _noise2((lx + FRAME['ox']) * .18, (ly + FRAME['oy']) * .25, 18)
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
    # the shadows of big clouds drift slowly over the land
    n = _noise2(lx * .05 - t * .045, ly * .08 - t * .012, 71) * .7 + _noise2(lx * .11 - t * .06, ly * .17, 72) * .3
    k = max(0.0, min(1.0, (n - .45) * 3.5))
    fg = _mix(fg, _mix(fg, (30, 40, 60), .45), k)
    bg = _mix(bg, _mix(bg, (4, 6, 12), .5), k)
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


SAND = {  # grade: how far you see, how thick the dust, colours (light, dark), streak density
    1: (16, .35, (226, 196, 140), (120, 90, 50), 41),
    2: (7, .7, (214, 170, 100), (110, 76, 36), 19),
    3: (3.5, 1.0, (170, 96, 52), (66, 32, 16), 9),
}


def sand_cell(kind, ch, fg, bg, lx, ly, t, dist):
    """Dust on the wind, from a haze to a wall of sand that swallows the sun."""
    grade = KINDS[kind][2]
    reach, thick, light, dark, gap = SAND[grade]
    speed = (1.6, 2.6, 3.4)[grade - 1]
    band = _noise2(lx * .12 - t * speed, ly * .5, 81) * .65 + _noise2(lx * .3 - t * speed * 1.5, ly * .9, 82) * .35
    k = (max(0.0, min(1.0, (dist - 2) / reach)) * .7 + band * .5) * thick
    fg = _mix(fg, light, min(1, k))
    bg = _mix(bg, _mix(dark, _mix(dark, light, .45), band), min(1, k * .95))
    ground = ch in GROUND
    if grade == 1:
        # dust runs low along the ground in thin snakes
        if ground and band > .62 and _h(lx, ly, 83) % 2:
            ch, fg = '~', _mix(bg, light, .45)
    elif (ground or ch in '♣♠↑∩n"') and band > (.55, .45)[grade - 2]:
        ch = '░' if band > (.72, .6)[grade - 2] else ('~' if _h(lx, ly, 83) % 3 else ' ')
        if grade == 3 and band > .78:
            ch = '▒'
        fg = _mix(bg, light, .4)
    u = lx - t * (18, 30, 44)[grade - 1]
    if _h(int(math.floor(u)), ly, 84) % gap == 0 and (ground or ch in '░~▒ '):
        ch, fg = '─', _mix(light, (255, 236, 190), .4)
    if grade == 3 and _h(int(math.floor(u * .7)), ly, 85) % 53 == 0:
        ch, fg = random_debris(lx, ly), (120, 90, 60)        # twigs and stones in the wind
    return ch, fg, bg


def random_debris(lx, ly):
    return ',`\\\''[_h(lx, ly, 86) % 4]


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


# ------------------------------------------------------------------ more kinds
def freezing_cell(ch, fg, bg, lx, ly, t, dist):
    """Freezing rain: a fine, cold rain that turns to ice where it lands. The ground lies glazed in
    patches that glint here and there; trees and grass take on a silver rime."""
    fg = _mix(_mix(fg, _grey(fg), .35), (150, 180, 210), .18)
    bg = _mix(bg, (16, 22, 32), .35)
    ground = ch in GROUND
    if ch in '♣♠↑"n∩':                         # rime on trees and tall grass
        fg = _mix(fg, (200, 220, 236), .35)
    ice = _noise2(lx * .22, ly * .3, 125) * .7 + _noise2(lx * .6, ly * .7, 126) * .3
    if ground and ice > .5:
        glass = min(1.0, (ice - .5) * 4)
        bg = _mix(bg, _mix((44, 60, 78), (70, 92, 116), (_h(lx, ly, 127) % 100) / 100), glass * .8)
        if ice > .58 and ch in '.,\'`"':
            ch = ' '                           # the glaze hides the ground beneath it
        # a glint: one cell catches the light for a moment, then another
        phase = t * .9 + (_h(lx, ly, 128) % 1000) / 1000 * 9
        if _h(lx, ly, 129 + int(phase)) % 23 == 0:
            k = math.sin((phase % 1) * math.pi)
            ch = '+' if k > .85 else '·'
            fg = _mix(bg, (235, 248, 255), .4 + .6 * k)
    # the rain itself: fine and sparse; where a drop lands it flashes and freezes into a crystal
    a = _streak(lx, ly, t, ((.7, 22, 2, 19, .22),), .1)
    if a > 0:
        bg = _mix(bg, (180, 205, 232), a * .12)
        if ground and a > .65:
            ch, fg = '|', _mix(bg, (200, 222, 244), .55)
        else:
            fg = _mix(fg, (200, 222, 244), a * .25)
    elif ground:
        phase = t * 2.4 + (_h(lx, ly, 130) % 100) / 100 * 5
        if _h(lx, ly, 131 + int(phase)) % 61 == 0:
            age = phase % 1
            ch = '*' if age < .25 else '∙' if age < .6 else '·'
            fg = _mix((255, 255, 255), (150, 180, 210), age)
    return ch, fg, bg


def sleet_cell(ch, fg, bg, lx, ly, t, dist):
    """Sleet: rain and wet snow at once, the ground turned to grey slush."""
    fg = _mix(_mix(fg, _grey(fg), .4), (120, 130, 150), .2)
    bg = _mix(bg, (18, 20, 26), .4)
    ground = ch in GROUND
    slush = _noise2(lx * .35, ly * .45, 121)
    if ground and slush > .55:
        bg = _mix(bg, (70, 74, 82), min(1, (slush - .55) * 3) * .5)       # grey slush in the ruts
        if _h(lx, ly, 122) % 4 == 0:
            ch, fg = ',', (130, 136, 146)
    a = _streak(lx, ly, t, ((1.0, 21, 3, 17, .25),), .2)
    if a > 0:
        bg = _mix(bg, (170, 190, 225), a * .2)
        if ground and a > .6:
            ch, fg = '|', _mix(bg, (170, 190, 225), .7)
    u = ly - t * 4
    sway = math.sin(t * 1.4 + u * .4) * 1.0
    if _h(int(round(lx + sway)), int(math.floor(u)), 123) % 37 == 0 and (ground or ch in ', '):
        ch, fg = '∙', (220, 226, 236)                                     # wet flakes, falling faster than snow
    return ch, fg, bg


def dew_cell(ch, fg, bg, lx, ly, t, dist):
    """Morning dew: the low sun is soft and pink, and the wet grass glitters."""
    fg = _mix(fg, (255, 214, 200), .15)
    bg = _mix(bg, (40, 30, 34), .15)
    if ch in GROUND or ch in '"\'':
        k = math.sin(t * 2.2 + (_h(lx, ly, 131) % 628) / 100)
        if _h(lx, ly, 132) % 9 == 0 and k > .75:
            ch = '∙' if k > .96 and _h(lx, ly, 134) % 3 == 0 else '·'
            fg = _mix((140, 190, 230), (240, 250, 255), (k - .75) / .25)
    low = max(0.0, _noise2(lx * .1 + t * .05, ly * .2, 133) - .5) * 1.2  # a little mist in the hollows
    bg = _mix(bg, (120, 110, 120), low)
    return ch, fg, bg


def drystorm_cell(ch, fg, bg, lx, ly, t, dist):
    """Dry lightning: a hot, heavy, dark sky without a drop of rain."""
    fg = _mix(fg, (200, 150, 110), .15)
    fg = _mix(fg, _grey(fg), .2)
    bg = _mix(bg, (30, 18, 24), .45)
    return ch, fg, bg


def _bolt_path(k, w, h):
    """The jagged path of strike k, from the top edge down to where it hits."""
    x = 4 + _h(k, 1, 141) % max(1, w - 8)
    end = h // 3 + _h(k, 2, 141) % max(1, h // 2)
    pts = []
    for y in range(end + 1):
        pts.append((x, y))
        r = _h(k, y, 142) % 5
        x += -1 if r == 0 else 1 if r == 1 else 0
    return pts


def drystorm_pass(cv, x0, y0, w, h, t):
    period = 2.4
    k = int(t / period)
    if _h(k, 3, 143) % 3 == 0:
        return
    dt = t - k * period - (_h(k, 4, 143) % 1000) / 1000 * 1.2
    if not (0 <= dt < .35):
        return
    k2 = 1 - dt / .35
    pts = _bolt_path(k, w, h)
    ex, ey = pts[-1]
    for y in range(h):                       # the strike lights the land around it
        for x in range(w):
            d = math.hypot(x - ex, (y - ey) * 1.2)
            light = max(0.0, 1 - d / 22) * k2
            if light > 0:
                ch, fg, bg = cv.get(x0 + x, y0 + y)
                cv.put(x0 + x, y0 + y, ch, _mix(fg, (255, 240, 255), light * .6), _mix(bg, (120, 100, 150), light * .5))
    if dt < .2:
        prev = pts[0][0]
        for x, y in pts:
            if 0 <= x < w and 0 <= y < h:
                glyph = '│' if x == prev else ('/' if x < prev else '\\')
                cv.put(x0 + x, y0 + y, glyph, (255, 255, 240), None)
            prev = x
    if 0 <= ex < w and 0 <= ey < h:          # and sets the grass alight
        cv.put(x0 + ex, y0 + ey, '☼', (255, 150 + int(80 * k2), 50), (90, 30, 10))


def falling_star(cv, x0, y0, w, h, t):
    """An ordinary clear night: now and then, rarely, a single star falls."""
    period = 47.0
    k = int(t / period)
    if _h(k, 7, 153) % 3:
        return
    dt = t - k * period - (_h(k, 8, 154) % 30)
    if not 0 <= dt <= .7:
        return
    sx = _h(k, 9, 155) % max(1, w)
    sy = _h(k, 10, 155) % max(1, h // 2)
    head = dt / .7 * 22
    for j in range(7):
        p = head - j * 1.2
        if p < 0:
            break
        x, y = int(sx + p), int(sy + p * .5)
        if 0 <= x < w and 0 <= y < h:
            ch, fg, bg = cv.get(x0 + x, y0 + y)
            fade = 1 - j / 7
            cv.put(x0 + x, y0 + y, '*' if j == 0 else ('─' if j < 3 else '·'), _mix((90, 110, 160), (255, 255, 230), fade), bg)


def meteors_pass(cv, x0, y0, w, h, t):
    """Shooting stars: now and then a streak of light crosses the night."""
    for lane in range(3):
        period = 2.6 + lane * .9
        k = int((t + lane * 1.3) / period)
        if _h(k, lane, 151) % 2:
            continue
        dt = (t + lane * 1.3) - k * period
        dur = .6
        if dt > dur:
            continue
        sx = _h(k, lane + 10, 152) % max(1, w)
        sy = _h(k, lane + 20, 152) % max(1, h // 2)
        head = dt / dur * 26
        for j in range(8):                   # the head and a fading tail, going down and to the right
            p = head - j * 1.2
            if p < 0:
                break
            x, y = int(sx + p), int(sy + p * .5)
            if 0 <= x < w and 0 <= y < h:
                ch, fg, bg = cv.get(x0 + x, y0 + y)
                fade = 1 - j / 8
                glyph = '*' if j == 0 else ('─' if j < 3 else '·')
                cv.put(x0 + x, y0 + y, glyph, _mix((90, 110, 160), (255, 255, 230), fade),
                       _mix(bg, (40, 50, 90), fade * .4))


def whirl_cell(ch, fg, bg, lx, ly, t, dist):
    """A dry, windy day: the dust devil itself is drawn in a pass of its own."""
    fg = _mix(fg, (230, 210, 160), .12)
    return ch, fg, bg


def whirlwind_pass(cv, x0, y0, w, h, t):
    """A dust devil wanders over the plain, spinning."""
    cx = w * .5 + math.sin(t * .35) * w * .3
    cy = h * .5 + math.sin(t * .23 + 1) * h * .25
    spin = '|/─\\'
    for y in range(h):
        for x in range(w):
            dx, dy = x - cx, (y - cy) * 1.3
            r = math.hypot(dx, dy)
            if r > 6:
                continue
            ch, fg, bg = cv.get(x0 + x, y0 + y)
            ang = math.atan2(dy, dx) + t * 7 - r * .6
            k = 1 - r / 6
            arm = math.sin(ang * 3) * .5 + .5
            bg = _mix(bg, (130, 100, 60), k * .45)
            if arm > .6 and r > .8:
                ch = spin[int((ang / math.pi * 2) % 4)]
                fg = _mix((180, 150, 100), (240, 220, 170), k)
            elif r <= .8:
                ch, fg = '@' if int(t * 8) % 2 else 'O', (210, 180, 120)
            else:
                fg = _mix(fg, (210, 180, 120), k * .5)
            cv.put(x0 + x, y0 + y, ch, fg, bg)


def smoke_cell(ch, fg, bg, lx, ly, t, dist):
    """A village burning: the light goes orange and dim, and soot drifts down."""
    fg = _mix(fg, (200, 130, 80), .15)
    bg = _mix(bg, (30, 16, 10), .35)
    return ch, fg, bg


def smoke_pass(cv, x0, y0, w, h, t):
    """Plumes of smoke rolling away on the wind from fires, with sparks and a red glow at their feet."""
    fires = [(w * .3, h * .65), (w * .55, h * .55), (w * .7, h * .75)]
    for y in range(h):
        for x in range(w):
            best = 0.0
            for i, (fx, fy) in enumerate(fires):
                dx, dy = x - fx, fy - y                 # the plume rises (up the screen) and leans downwind
                if dy < -2:
                    continue
                along = dy + max(0, dx) * .5
                lean = dx - dy * .9
                spread = 1.5 + along * .35
                wob = (_noise2(x * .2 + t * .8, y * .25 - t * 1.4, 160 + i) - .5) * 4
                k = max(0.0, 1 - abs(lean + wob) / spread) * max(0.0, 1 - along / 28)
                best = max(best, k)
            ch, fg, bg = cv.get(x0 + x, y0 + y)
            if best > 0:
                g = _noise2(x * .3 + t * .6, y * .3 - t, 165)
                smoke = _mix((26, 24, 24), (90, 84, 80), g)
                bg = _mix(bg, smoke, best * .8)
                fg = _mix(fg, smoke, best * .55)
                if best > .5 and ch in GROUND and g > .6:
                    ch, fg = '░', _mix(smoke, (120, 112, 106), .5)
            for i, (fx, fy) in enumerate(fires):
                d = math.hypot(x - fx, (y - fy) * 1.2)
                if d < 5:
                    glow = (1 - d / 5) * (.75 + .25 * math.sin(t * 9 + i * 2))
                    bg = _mix(bg, (150, 50, 14), glow * .6)
                    fg = _mix(fg, (255, 160, 70), glow * .5)
                if d < 1.2:
                    ch, fg = ('▲' if int(t * 6 + i) % 2 else '^'), (255, 170 + int(60 * math.sin(t * 11 + i)), 40)
            u = y + t * 5                              # sparks climbing
            if _h(int(x - u * .4), int(math.floor(u)), 166) % 89 == 0 and best > .3:
                ch, fg = '·', (255, 180, 80)
            cv.put(x0 + x, y0 + y, ch, fg, bg)


LEAVES = {'leaves': [(220, 120, 40), (200, 80, 30), (230, 180, 60), (160, 60, 30)],
          'blossom': [(255, 190, 215), (245, 160, 195), (255, 220, 235), (225, 140, 185)]}


def _petal_cell(kind, ch, fg, bg, lx, ly, t, dist):
    """Leaves in autumn or blossom in spring, drifting down and settling on the ground."""
    cols = LEAVES[kind]
    tint = (60, 30, 10) if kind == 'leaves' else (60, 30, 44)
    bg = _mix(bg, tint, .12 if kind == 'leaves' else .05)
    ground = ch in GROUND
    lie = _noise2(lx * .25, ly * .25, 171 if kind == 'leaves' else 172)
    if ground and lie > (.62 if kind == 'leaves' else .76) and _h(lx, ly, 178) % (1 if kind == 'leaves' else 5) == 0:
        ch, fg = (',' if _h(lx, ly, 173) % 2 else '.'), cols[_h(lx, ly, 174) % len(cols)]   # fallen ones
    for layer, speed in enumerate((2.0, 1.3)):
        u = ly - t * speed
        sway = math.sin(t * 1.1 + u * .5 + layer * 3) * 2.5 + t * (1.5 if kind == 'blossom' else .6)
        x = int(round(lx - sway))
        if _h(x, int(math.floor(u)), 175 + layer) % (29 if kind == 'leaves' else 53) == 0:
            if ground or ch in ',.':          # a petal shows on open ground; over water or a tree it is not drawn,
                ch = ('`' if math.sin(t * 4 + lx) > 0 else ',') if kind == 'leaves' else ('∙' if layer else '·')
                fg = cols[_h(x, int(u), 177) % len(cols)]       # so the water and the trees keep their own colour
            break
    return ch, fg, bg


def leaves_cell(ch, fg, bg, lx, ly, t, dist):
    return _petal_cell('leaves', ch, fg, bg, lx, ly, t, dist)


def blossom_cell(ch, fg, bg, lx, ly, t, dist):
    return _petal_cell('blossom', ch, fg, bg, lx, ly, t, dist)


def night_cell(ch, fg, bg, lx, ly, t, dist):
    return ch, fg, bg


EXTRA_CELLS = {'freezing': freezing_cell, 'sleet': sleet_cell, 'dew': dew_cell, 'drystorm': drystorm_cell,
               'whirlwind': whirl_cell, 'smoke': smoke_cell, 'leaves': leaves_cell, 'blossom': blossom_cell,
               'meteors': night_cell}
EXTRA_PASSES = {'drystorm': drystorm_pass, 'meteors': meteors_pass, 'whirlwind': whirlwind_pass, 'smoke': smoke_pass}


# ------------------------------------------------------------------ the painter
PASSES = {'fireflies': fireflies, 'night': falling_star, **EXTRA_PASSES}
NEEDS_CANVAS = {'heat'}                      # heat shimmer borrows the glyph of the cell next door


def cell(kind, ch, fg, bg, lx, ly, t, dist, lightning=0.0, w=80, h=50, neighbour=None):
    """Weather over one cell: (ch, fg, bg)."""
    fam = KINDS[kind][1]
    if fam == 'rain':
        return rain_cell(kind, ch, fg, bg, lx, ly, t, lightning)
    if fam == 'snow':
        return snow_cell(kind, ch, fg, bg, lx, ly, t, dist)
    if kind == 'hail':
        return hail_cell(ch, fg, bg, lx, ly, t)
    if fam in ('fog', 'miasma'):
        return fog_cell(kind, ch, fg, bg, lx, ly, t, dist)
    if kind == 'clouds':
        return cloud_cell(ch, fg, bg, lx, ly, t)
    if kind == 'wind':
        return wind_cell(ch, fg, bg, lx, ly, t)
    if fam == 'heat':
        return heat_cell(kind, ch, fg, bg, lx, ly, t, w, h, neighbour)
    if fam == 'sand':
        return sand_cell(kind, ch, fg, bg, lx, ly, t, dist)
    if kind in EXTRA_CELLS:
        return EXTRA_CELLS[kind](ch, fg, bg, lx, ly, t, dist)
    if kind == 'ash':
        return ash_cell(ch, fg, bg, lx, ly, t)
    if kind == 'aurora':
        return aurora_cell(ch, fg, bg, lx, ly, t)
    return ch, fg, bg


def sheltered_flash(fg, bg, lightning):
    return _mix(fg, (240, 244, 255), lightning * .3), _mix(bg, (150, 160, 200), lightning * .25)


def apply(cv, x0, y0, w, h, kind, t, centre=None, sheltered=None):
    """Paint weather over the rectangle (x0, y0, w, h) of a canvas. centre: the player's cell, for fog and snow.
    sheltered: cells (canvas x, y) under a roof, where no weather falls (only a lightning flash shows through)."""
    if kind == 'clear':
        return
    cx, cy = centre or (x0 + w // 2, y0 + h // 2)
    lightning = flash(t) if kind == 'storm' else 0.0
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            ch, fg, bg = cv.get(x, y)
            if sheltered and (x, y) in sheltered:
                if lightning:
                    fg, bg = sheltered_flash(fg, bg, lightning)
                    cv.put(x, y, ch, fg, bg)
                continue
            nb = cv.get(x + 1, y) if kind in NEEDS_CANVAS and x + 1 < x0 + w else None
            ch, fg, bg = cell(kind, ch, fg, bg, x - x0, y - y0, t, math.hypot(x - cx, y - cy), lightning, w, h, nb)
            cv.put(x, y, ch, fg, bg)
    passes(cv, x0, y0, w, h, kind, t)


def passes(cv, x0, y0, w, h, kind, t):
    """The parts drawn on top of everything: fireflies, lightning bolts, shooting stars, a dust devil, smoke."""
    if kind in PASSES:
        PASSES[kind](cv, x0, y0, w, h, t)


# ================================================================== the weather in the world
# Each region of the world has its own weather, which changes every few hours. What comes next depends on
# the region's climate (the cold north and the mountains, the hot dry south, the marshes, or the temperate
# middle) and on the season, and it changes by steps: drizzle grows into rain before it pours, a blizzard
# dies down to snow before the sky clears.

import random as _random

CLIMATE_WEIGHTS = {
    'temperate': {
        'spring': {'clear': 3, 'clouds': 3, 'drizzle': 2, 'rain': 2, 'downpour': .5, 'storm': .4, 'blossom': 1.5, 'warm': .5},
        'summer': {'clear': 4, 'warm': 3, 'heat': .8, 'clouds': 2, 'rain': 1, 'storm': 1, 'drystorm': .5, 'downpour': .4},
        'autumn': {'clear': 2, 'clouds': 3, 'wind': 2, 'leaves': 2, 'drizzle': 2, 'rain': 2, 'downpour': 1, 'fog': 1.5, 'storm': .5},
        'winter': {'clear': 2, 'clouds': 3, 'snow_light': 2, 'snow': 1.5, 'blizzard': .3, 'fog': 1, 'freezing': .7,
                   'sleet': 1, 'hail': .3},
    },
    'cold': {
        'spring': {'clear': 2, 'clouds': 3, 'snow_light': 2, 'sleet': 1.5, 'drizzle': 1, 'freezing': 1, 'fog': 1},
        'summer': {'clear': 3, 'clouds': 3, 'drizzle': 2, 'rain': 1.5, 'fog': 1, 'wind': 1},
        'autumn': {'clouds': 3, 'wind': 2, 'sleet': 2, 'snow_light': 2, 'fog': 1.5, 'rain': 1, 'clear': 1},
        'winter': {'snow_light': 2, 'snow': 3, 'blizzard': 1.5, 'clear': 1.5, 'clouds': 1, 'freezing': .8},
    },
    'arid': {
        'spring': {'clear': 4, 'warm': 3, 'dust': 2, 'sandstorm': .6, 'clouds': 1},
        'summer': {'clear': 3, 'heat': 4, 'warm': 1, 'dust': 2, 'sandstorm': 1, 'haboob': .4, 'drystorm': .8},
        'autumn': {'clear': 3, 'warm': 3, 'dust': 2, 'sandstorm': 1, 'haboob': .3, 'clouds': 1, 'drystorm': .4},
        'winter': {'clear': 4, 'warm': 2, 'clouds': 2, 'dust': 1, 'drizzle': .5},
    },
    'marsh': {
        'spring': {'mist': 2, 'fog': 2, 'drizzle': 3, 'rain': 2, 'clouds': 2, 'clear': 1},
        'summer': {'mist': 2, 'clear': 2, 'warm': 2, 'clouds': 2, 'rain': 2, 'storm': 1, 'fog': 1},
        'autumn': {'fog': 3, 'fog_thick': 1.5, 'mist': 2, 'drizzle': 2, 'rain': 2, 'clouds': 2},
        'winter': {'fog': 3, 'fog_thick': 1.5, 'freezing': 1, 'sleet': 1.5, 'clouds': 2, 'snow_light': 1},
    },
}
FAMILY_LADDER = {'rain': ['drizzle', 'rain', 'downpour', 'storm'], 'snow': ['snow_light', 'snow', 'blizzard'],
                 'fog': ['mist', 'fog', 'fog_thick'], 'sand': ['dust', 'sandstorm', 'haboob'], 'heat': ['warm', 'heat']}
MESSAGES = {
    'clear': 'The sky clears.', 'clouds': 'Clouds come in, and their shadows sail over the land.',
    'drizzle': 'A fine drizzle starts to fall.', 'rain': 'It is raining.', 'downpour': 'The rain comes down in sheets.',
    'storm': 'Thunder rolls overhead. A storm!', 'snow_light': 'A few snowflakes drift down.', 'snow': 'It is snowing.',
    'blizzard': 'A blizzard! The wind drives the snow sideways.', 'hail': 'Hail rattles down.',
    'mist': 'Mist rises from the ground.', 'fog': 'Fog closes in.', 'fog_thick': 'The fog is so thick you can barely see.',
    'wind': 'A strong wind picks up.', 'leaves': 'Leaves come down in the wind.', 'blossom': 'Blossom drifts on the breeze.',
    'warm': 'It is a warm day.', 'heat': 'The heat is scorching.', 'dust': 'The wind lifts the dust.',
    'sandstorm': 'A sandstorm!', 'haboob': 'A wall of sand swallows the sun!', 'freezing': 'Freezing rain glazes the ground.',
    'sleet': 'Sleet comes down, half rain, half snow.', 'drystorm': 'A dry storm: lightning, and not a drop of rain.',
    'ash': 'Ash is falling from the sky.', 'miasma': 'A sickly mist hangs over the land.', 'blood': 'The rain is red as blood.',
    'smoke': 'Smoke drifts over the land.',
}
# how the weather changes things: sight (cells less, or a cap), travel cost factor, ambush factor, food factor
EFFECTS = {
    'drizzle': (0, 1.0, 1.0, 1.0), 'rain': (-1, 1.1, 1.0, 1.0), 'downpour': (-2, 1.25, 1.2, 1.0), 'storm': (-3, 1.3, 1.2, 1.0),
    'snow_light': (-1, 1.1, 1.0, 1.15), 'snow': (-2, 1.35, 1.0, 1.3), 'blizzard': (('cap', 3), 2.0, 1.4, 1.6),
    'hail': (-1, 1.2, 1.0, 1.1), 'mist': (-1, 1.0, 1.2, 1.0), 'fog': (('cap', 5), 1.1, 1.6, 1.0),
    'fog_thick': (('cap', 3), 1.2, 2.0, 1.0), 'miasma': (('cap', 4), 1.2, 1.8, 1.0), 'heat': (0, 1.15, 1.0, 1.2),
    'dust': (-1, 1.05, 1.0, 1.0), 'sandstorm': (('cap', 4), 1.5, 1.5, 1.1), 'haboob': (('cap', 2), 2.0, 1.8, 1.2),
    'freezing': (-1, 1.3, 1.0, 1.3), 'sleet': (-1, 1.25, 1.0, 1.25), 'ash': (-1, 1.1, 1.2, 1.0), 'smoke': (-2, 1.0, 1.2, 1.0),
    'blood': (-1, 1.1, 1.3, 1.0), 'wind': (0, 1.05, 1.0, 1.0),
}
NIGHT_ONLY = {'fireflies', 'aurora', 'meteors', 'night'}
PANEL_ICON = {'clear': '☼', 'clouds': '≈', 'drizzle': '·', 'rain': '|', 'downpour': '|', 'storm': '!', 'snow_light': '*',
              'snow': '*', 'blizzard': '*', 'hail': 'o', 'mist': '░', 'fog': '░', 'fog_thick': '▒', 'wind': '~',
              'leaves': ',', 'blossom': '∙', 'warm': '☼', 'heat': '☼', 'dust': '~', 'sandstorm': '▒', 'haboob': '▓',
              'freezing': '|', 'sleet': '|', 'drystorm': '!', 'ash': '∙', 'miasma': '░', 'blood': '|', 'smoke': '░',
              'dew': '·', 'fireflies': '∙', 'aurora': '≈', 'meteors': '*'}


def climate(world, rid):
    """The climate of a region: cold, arid, marsh or temperate."""
    cache = getattr(world, 'climates', None)
    if cache is None:
        cache = world.climates = {}
    if rid in cache:
        return cache[rid]
    from .world import WORLD_H
    r = world.regions[rid]
    if getattr(r, 'climate', None):
        cache[rid] = r.climate
        return r.climate
    lat = r.cy / WORLD_H                          # the north is cold, the far south hot and dry
    biome = getattr(r, 'biome', 'grass')
    if lat < .26 or (biome == 'hills' and lat < .45):
        c = 'cold'
    elif biome == 'swamp':
        c = 'marsh'
    elif lat > .74:
        c = 'arid'
    else:
        c = 'temperate'
    cache[rid] = c
    return c


def _family(kind):
    for fam, ladder in FAMILY_LADDER.items():
        if kind in ladder:
            return fam
    return None


def _step(cur, target):
    """One step from the weather now towards the weather to come: grades change one at a time."""
    fc, ft = _family(cur), _family(target)
    if fc and fc == ft:
        lad = FAMILY_LADDER[fc]
        i, j = lad.index(cur), lad.index(target)
        return lad[i + (1 if j > i else -1 if j < i else 0)]
    if fc and lad_index(cur) > 0:
        lad = FAMILY_LADDER[fc]
        return lad[lad_index(cur) - 1]                  # die down before changing to something else
    if ft and lad_index(target) > 0:
        return FAMILY_LADDER[ft][0]                     # and start small
    return target


def lad_index(kind):
    fam = _family(kind)
    return FAMILY_LADDER[fam].index(kind) if fam else 0


def region_weather(game, rid):
    """The weather in a region now, moving it on if its time is up."""
    from . import calendar as CAL
    world = game.world
    ws = getattr(world, 'weather', None)
    if ws is None:
        ws = world.weather = {}
    st = ws.get(rid)
    turn = game.turn
    if st is None or turn - st[1] > 3000:
        st = ws[rid] = ['clear', turn, 'clear']
    steps = 0
    while st[1] <= turn and steps < 40:
        steps += 1
        day = 1 + st[1] // 300
        weights = CLIMATE_WEIGHTS[climate(world, rid)][CAL.season(day)]
        if st[0] == st[2]:                               # reached the goal: pick a new one
            kinds = list(weights)
            st[2] = _random.choices(kinds, [weights[k] for k in kinds])[0]
        st[0] = _step(st[0], st[2])
        if len(st) < 4:
            st.append(0.0)
        # how wet the ground is: it soaks up the rain, and dries again in fair weather
        grade = KINDS.get(st[0], ('', '', 0))[2]
        if _family(st[0]) == 'rain':
            st[3] = min(1.0, st[3] + .12 * grade)
        else:
            st[3] = max(0.0, st[3] - (.1 if _family(st[0]) in ('clear', 'heat', 'wind', 'clouds') else .04))
        st[1] += _random.randint(25, 70) if st[0] != st[2] else _random.randint(50, 150)
    return st[0]


def wetness(game):
    loc = where(game)
    if not loc:
        return 0.0
    region_weather(game, loc[0])
    st = game.world.weather.get(loc[0])
    return st[3] if st and len(st) > 3 else 0.0


def where(game):
    """(region id, overworld x, y) of the place you are in, or None underground."""
    m = game.map
    if m.kind == 'dungeon' or getattr(m, 'underground', False):
        return None
    if m.kind == 'over':
        x, y = game.player.x, game.player.y
    else:
        x, y = game.over_pos
    w = game.world
    om = game.maps['over']
    return w.region_of[y * om.w + x], x, y


def current(game):
    """The weather where you are (its base kind), 'clear' underground."""
    loc = where(game)
    if not loc:
        return 'clear'
    return region_weather(game, loc[0])


def foul(game):
    """Weather that sends townsfolk indoors: real rain, snow, hail, sleet or a sandstorm (a drizzle will not)."""
    k = current(game)
    _n, fam, power = KINDS.get(k, ('', 'clear', 0))
    return fam in ('hail', 'sleet', 'ice') or (fam in ('rain', 'snow', 'sand') and power >= 2)


def starfall(day):
    """The night of the Starfall, once a year: the 12th of Emberwane, when the sky rains stars."""
    from . import calendar as CAL
    _y, mo, d, _wd = CAL._split(day)
    return mo == 6 and d == 12


QUIET = {'clouds', 'night', 'dew'}
STILL = {'dew', 'mist', 'fog', 'fog_thick', 'clouds', 'warm', 'heat', 'aurora', 'fireflies'}   # slow things: 10 frames a second will do      # pretty, but not worth a word in the panel


def shown(game):
    """What to draw: the weather, an omen of a great evil nearby, or the quiet things of night and morning."""
    from . import towns as TW, calendar as CAL
    from . import evils as EVL
    loc = where(game)
    if not loc:
        return 'clear'
    rid, x, y = loc
    from . import rift as RF
    if RF.ash_at(game, x, y):
        return 'ash'                           # the land round a rift burns slowly to ash
    ev = EVL.taint_at(game, x, y)
    if ev:
        omen = {'scorch': 'ash', 'mire': 'miasma', 'blight': 'miasma', 'warpath': 'smoke'}.get(ev.d['taint'])
        if omen:
            return omen
    kind = region_weather(game, rid)
    from . import debug as DBG
    if DBG.ON and DBG.has(game, 'aurora'):
        return 'aurora'                        # the debug menu's northern lights: anywhere, at any hour
    if kind == 'clouds' and TW.is_night(game):
        kind = 'clear'                         # no cloud shadows without the sun
    if kind != 'clear':
        return kind
    h = TW.hour(game)
    season = CAL.season(game.day)
    cl = climate(game.world, rid)
    if TW.is_night(game):
        if cl == 'cold' and season in ('winter', 'autumn'):
            return 'aurora'
        if season == 'summer' and cl in ('temperate', 'marsh'):
            return 'fireflies'
        if starfall(game.day):
            return 'meteors'
        return 'night'
    if 5 <= h < 8 and season in ('spring', 'summer') and cl != 'arid':
        return 'dew'
    return 'clear'


def sight(game, r):
    """Your sight in this weather."""
    eff = EFFECTS.get(shown(game))
    if not eff:
        return r
    s = eff[0]
    if isinstance(s, tuple):
        return min(r, s[1])
    return max(2, r + s)


def travel_factor(game):
    eff = EFFECTS.get(current(game))
    return eff[1] if eff else 1.0


def ambush_factor(game):
    eff = EFFECTS.get(shown(game))
    return eff[2] if eff else 1.0


def food_factor(game):
    eff = EFFECTS.get(current(game))
    f = eff[3] if eff else 1.0
    p = game.player
    hot = current(game) in ('heat', 'sandstorm', 'haboob')
    if f > 1 and hot:
        if any(b[0] == 'cool' for b in p.buffs):
            return 1.0                               # a desert plate: the heat costs nothing
        if any(it.k == 'tool' and it.t == 'waterskin' for it in p.inv):
            return 1 + (f - 1) / 2
        return f
    if f > 1 and any(b[0] == 'warm' for b in p.buffs):
        return 1.0                                   # warmed through by a hot spring or a hot stew: the cold costs nothing
    return f


def notice(game):
    """Tell the player when the weather around them changes."""
    kind = shown(game)
    last = getattr(game, '_wx_seen', None)
    game._wx_seen = kind
    if last is None or kind == last or kind in NIGHT_ONLY or kind == 'dew' or last in NIGHT_ONLY and kind == 'clear':
        return
    if game.map.kind == 'dungeon' or kind == 'clear' and last == 'dew':
        return
    game.msg(MESSAGES.get(kind, ''), 'info') if MESSAGES.get(kind) else None


def strike(game):
    """In a thunderstorm, standing out in the open is a risk."""
    if current(game) != 'storm' or game.map.kind != 'over':
        return
    from . import data as D
    p = game.player
    if game.map.tile(p.x, p.y) in (D.GRASS, D.HILLS, D.SAND) and _random.random() < .006:
        dmg = 6 + p.lvl * 2
        p.life -= dmg
        game.msg(f'Lightning strikes the ground beside you! ({dmg} damage) Get off the open land.', 'bad')
        game.shake()
        if p.life <= 0:
            game.die('a bolt of lightning')
