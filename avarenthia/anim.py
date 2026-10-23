"""Small things that move on the map, worked out from the clock and never saved: fires that flicker by day, water
that glints, rivers that run towards the sea, molten iron that breathes, ore and gems that catch the light, rings
where fish are rising, will-o'-wisps over the marsh at night, the slow breath of tainted land, the portal and the
altar candles, and the beam of a harbour lighthouse. The screen only redraws on a timer while one of them is in view."""
import math

from . import data as D
from .canvas import mix, scale
from .look import _h

WATERS = (D.WATER, D.SHALLOW, D.RIVER)
MOVING = {D.FIREPIT, D.MOLTEN, D.ALTAR, D.WATER, D.SHALLOW, D.RIVER, D.ORE, D.GEMS, D.GLITTER, D.SWAMP,
          D.BURNING, D.BALL, D.HALLOWED, D.SPIRITTOTEM, D.ANVIL}
RISE_EVERY = 25           # about one water cell in this many along a shore has fish rising, a new set each day


def _bump(s, w):
    """0 -> 1 -> 0 while s runs through 0..w, else 0."""
    return math.sin(math.pi * s / w) if 0 <= s < w else 0.0


def _phase(t, x, y, speed, salt):
    return (t * speed + _h(x, y, salt) / 65536) % 1.0


def flame(t, x, y):
    """How bright a flame is now, about .7 to 1: the same restless wobble for everyone looking at it."""
    a = math.sin(t * 7.3 + x * 1.7 + y * 3.1) * .5 + math.sin(t * 13.1 + x * .9) * .3 + math.sin(t * 3.1 + y) * .2
    return .85 + .15 * a


def sparkle(fg, t, x, y, salt=91):
    """Now and then a glint of light on something hard and bright. (fg, True) while it shines."""
    g = _bump(_phase(t, x, y, .11, salt), .05)
    return (mix(fg, (255, 255, 240), g * .85), True) if g > 0 else (fg, False)


def rising(m, x, y, day):
    """Are fish rising at this water cell today? Only near a shore, where a line can reach them."""
    if not m.inb(x, y) or m.t[y * m.w + x] not in WATERS or _h(x, y, day * 7 + 3) % RISE_EVERY:
        return False
    return any(m.inb(x + dx, y + dy) and m.t[(y + dy) * m.w + x + dx] not in WATERS
               and D.TILES[m.t[(y + dy) * m.w + x + dx]].walk for dy in (-1, 0, 1) for dx in (-1, 0, 1))


def rising_near(game, x, y):
    """Fish rising within a step of (x, y), on the map you are on."""
    m = game.map
    day = game.turn // D.DAY_LEN
    return any(rising(m, x + dx, y + dy, day) for dy in (-1, 0, 1) for dx in (-1, 0, 1))


def flow(m):
    """How far each river cell of the world map lies from the lake or sea it runs into, cached on the map."""
    f = getattr(m, '_flow', None)
    if f is not None:
        return f
    f = {}
    if m.kind == 'over':
        front = []
        for i, t in enumerate(m.t):
            if t == D.RIVER:
                x, y = i % m.w, i // m.w
                if any(m.inb(x + dx, y + dy) and m.t[(y + dy) * m.w + x + dx] == D.WATER
                       for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    f[i] = 0
                    front.append(i)
        while front:
            nxt = []
            for i in front:
                x, y = i % m.w, i // m.w
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)):
                    if m.inb(x + dx, y + dy):
                        j = (y + dy) * m.w + x + dx
                        if j not in f and m.t[j] == D.RIVER:
                            f[j] = f[i] + 1
                            nxt.append(j)
            front = nxt
    m._flow = f
    return f


def cell(m, i, x, y, look, t, night, day):
    """The look of cell i at time t, or None when it does not move now."""
    ch, fg, bg = look
    tt = m.t[i]
    if tt == D.BURNING:                                     # burning ground: low flames that lick and flicker
        f = flame(t * 1.3, x, y)
        return ('^' if f > .82 else '*' if f > .74 else ','), mix(scale(fg, f), (255, 220, 120), max(0.0, f - .9) * 3), \
            scale(bg, .7 + .4 * (f - .7))
    if tt == D.BALL:                                        # ball lightning crackles
        k = .5 + .5 * math.sin(t * 17 + x * 3.1)
        return ('¤' if k > .3 else '○'), mix(fg, (255, 255, 255), k * .6), mix(bg, (120, 120, 30), k * .5)
    if tt in (D.HALLOWED, D.SPIRITTOTEM):                   # a soft light that breathes
        k = .5 + .5 * math.sin(t * 1.6 + (x + y) * .4)
        return ch, mix(fg, (255, 255, 255), k * .3), scale(bg, .85 + .25 * k)
    if tt == D.ANVIL:                                       # the smith at work: now and then a shower of sparks
        if night:
            return None
        g = _bump(_phase(t, x, y, .45, 33), .1)
        if g > 0:
            return ('*' if g > .5 else '∙'), mix(fg, (255, 226, 120), g), mix(bg, (150, 70, 20), g * .7)
        return ch, fg, bg
    if tt == D.FIREPIT:
        f = flame(t, x, y)
        return ch, mix(scale(fg, f), (255, 220, 120), max(0.0, f - .9) * 3), scale(bg, .8 + .3 * (f - .7))
    if tt == D.MOLTEN:
        k = .5 + .5 * math.sin(t * 1.1 - x * .35 + y * .2)
        return ch, mix(fg, (255, 214, 120), k * .7), mix(bg, (170, 72, 14), k * .6)
    if tt == D.ALTAR:
        return ch, scale(fg, flame(t * .7, x, y) * 1.05), bg
    if tt in (D.ORE, D.GEMS, D.GLITTER):
        fg, on = sparkle(fg, t, x, y)
        return ch, fg, bg
    if tt == D.SWAMP:
        if not night:
            return None
        g = _bump(_phase(t, x, y, .05, 77), .06)            # a wisp of pale light comes and goes
        if g <= 0:
            return ch, fg, bg
        return ('∙' if g > .4 else ch), mix(fg, (150, 235, 190), g), mix(bg, (30, 60, 46), g * .5)
    # water
    if rising(m, x, y, day):
        s = _phase(t, x, y, .42, 13)                         # rings spread and fade, then a pause
        ring = '·' if s < .15 else 'o' if s < .3 else 'O' if s < .45 else None
        if ring:
            return ring, mix(fg, (200, 225, 245), .6 - s), bg
        return ch, fg, bg
    if tt == D.RIVER and m.kind == 'over':
        d = flow(m).get(i)
        if d is not None:
            g = _bump((d / 9 + t * .5) % 1.0, .18)          # light runs down the river towards the sea
            return ch, mix(fg, (190, 222, 255), g * .5), bg
    g = _bump(_phase(t, x, y, .07, 51), .03)
    if g > 0:
        return '~', mix(fg, (214, 232, 255), g * .8), bg
    return ch, fg, bg


def portal(t):
    return mix((90, 176, 255), (196, 232, 255), .5 + .5 * math.sin(t * 2.2))


def beacon(m, x, y, look, t):
    """The turning beam of a lighthouse at night falling on cell (x, y)."""
    bx, by = m.beacon
    dx, dy = x - bx, y - by
    dist = math.hypot(dx, dy)
    if not 1 <= dist <= 16:
        return look
    diff = abs((math.atan2(dy, dx) - t * .8 + math.pi) % (2 * math.pi) - math.pi)
    k = max(0.0, 1 - diff / .16) * (1 - dist / 17)
    if k <= 0:
        return look
    ch, fg, bg = look
    return ch, mix(fg, (255, 240, 200), k * .5), mix(bg, (150, 130, 80), k * .6)


def camp_glow(t, x, y):
    """The fires of a hostile camp seen from the world map at night: a dull red that breathes."""
    return mix((40, 34, 26), (120, 36, 14), .55 + .3 * flame(t * .4, x, y) - .25)


# ------------------------------------------------------------------ spell effects
# A small set of moving pictures that every school shares: bolts that fly with a fading tail, impacts that open out,
# life flowing back, rising light, lightning that zigzags. Never longer than about .4 s; a key skips them and the game
# never waits for one. game.fx(kind, **kw) queues one; the GameScreen draws it over the map.
# Each school has its own hand on top: rings and waves, Meteor's shadow and slanting fall, the dead that grey and
# rise, walls that go up one stone at a time, and one white frame of the sky for a great lightning stroke.
FX_MODES = ('full', 'short', 'off')
STEP = .02                # a bolt flies one cell in this long
BOLT_MAX = .12
BURST_FRAME = .05
WAVE_FRAME = .06          # kept for timing a second wave after a first
ROUND_STEP = .03          # an area opens out by real distance: one tile further in this long (it looks round)
FRONT = .04               # each sign of the front (* + ·) shows this long, then the ground glows ░ and dims
ROUND_DUR = .22
SWING_TICK, SWING_LIT = .045, .12     # a weapon's swing arc: one sign after another, each lit a moment
SPIN_TICK = .03
CRIT_TIME, BLOOD_TIME = .26, .3
STEEL_DIM, GOLD_CRIT, BLOOD_RED = (150, 152, 160), (255, 214, 90), (200, 30, 30)
CLOUD_DUR = .22           # the faint cloud beyond the square's sides: only a look, it harms nobody
DUST = (150, 140, 130)
NO_GLOW = ('sound', '~', '!')     # a howl, a gust, a war cry: only the front, no glow, no cloud
SKY_TIME = .07            # the white frame of a great lightning stroke
METEOR_SHADOW, METEOR_FALL = .08, .1
RAISE_TIME = .36
TRAIL_STEP = .03


def _line_char(dx, dy):
    """The sign of a flying arrow or a stroke of lightning, by its direction."""
    if dx == 0:
        return '|'
    if dy == 0:
        return '-'
    return '\\' if (dx > 0) == (dy > 0) else '/'


def bolt_time(n):
    return min(BOLT_MAX, STEP * max(1, n))


def fx_life(kind, kw):
    """How long (delay included) an effect of this kind stays on the screen."""
    d = kw.get('delay', 0.0)
    if kind == 'bolt':
        return d + bolt_time(len(kw['cells'])) + .06
    if kind in ('burst', 'wave') and kw.get('r', 1) >= 1:
        r = kw.get('r', 1)
        g = BURST_FRAME if kind == 'burst' and kw.get('gather') else 0
        return d + g + max(ROUND_STEP * r * 1.415 + kw.get('dur', ROUND_DUR), ROUND_STEP * r + CLOUD_DUR)
    if kind == 'burst':
        return d + BURST_FRAME * (kw.get('r', 1) + 3 + (1 if kw.get('gather') else 0))
    if kind == 'zap':
        return d + .24
    if kind == 'sky':
        return d + SKY_TIME
    if kind == 'meteor':
        return d + METEOR_SHADOW + METEOR_FALL
    if kind == 'raise':
        return d + RAISE_TIME
    if kind == 'trail':
        return d + TRAIL_STEP * len(kw['cells']) + kw.get('linger', .14)
    if kind == 'swing':
        return d + SWING_TICK * (5 if kw.get('wide') else 3) + SWING_LIT
    if kind == 'spin':
        return d + SPIN_TICK * 8 + SWING_LIT
    if kind == 'crit':
        return d + CRIT_TIME
    if kind == 'blood':
        return d + BLOOD_TIME
    return d + kw.get('dur', .28 if kind == 'drain' else .4)


def fx_fallback(kind, kw):
    """With effects off: the plain flash of old, (cells, colour, sign), or None."""
    col = kw.get('col', (255, 255, 255))
    if kind in ('bolt', 'zap'):
        return kw['cells'], col, kw.get('ch', '*')
    if kind in ('burst', 'wave'):
        x, y, r = kw['x'], kw['y'], kw.get('r', 1)
        return ([(x + dx, y + dy) for dy in range(-r, r + 1) for dx in range(-r, r + 1)
                 if not ((kw.get('hollow') or kind == 'wave') and dx == dy == 0)], col, kw.get('ch', '*'))
    if kind == 'trail':
        return kw['cells'], col, kw.get('ch', '*')
    if kind == 'raise':
        return [(kw['x'], kw['y'])], col, kw.get('ch', 'z')
    return None                 # the sky's white frame and Meteor's shadow have no flash of old


def _wave_sign(sign, dx, dy):
    """The sign of a wave at this offset: a sound wave bends round as ( ), wind runs as ~, the rest keep theirs."""
    if sign == 'sound':
        if abs(dx) >= abs(dy):
            return '(' if dx < 0 else ')'
        return '-'
    return sign


def _round(x, y, r, col, age, signs='*+·', hollow=False, sign=None, glow=True, cloud=True, dust=False, dur=ROUND_DUR):
    """An area of radius r (what is hit is the whole square, the same range every way) drawn so it looks round: a
    front of signs runs out by real distance, the ground behind it glows ░ and dims, the corners are drawn softer,
    and a faint cloud beyond the sides rounds it off (a Meteor's is brown dust)."""
    out = []
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if hollow and dx == dy == 0:
                continue
            d = math.sqrt(dx * dx + dy * dy)
            q = age - d * ROUND_STEP
            if not 0 <= q < dur:
                continue
            soft = d > r + .5
            st = int(q / FRONT)
            if st < len(signs):
                c = mix(col, (255, 250, 220), .5) if st == 0 else _fade(col, 1 - st * .3)
                ch = _wave_sign(sign, dx, dy) if st == 0 and sign else signs[st]
                out.append((x + dx, y + dy, ch, scale(c, .72) if soft else c, None))
            elif glow:
                k = (q - FRONT * len(signs)) / max(.01, dur - FRONT * len(signs))
                out.append((x + dx, y + dy, '░', mix(col, (14, 12, 12), min(.95, .3 + .55 * k + (.15 if soft else 0))), None))
    if cloud and r >= 1:
        a = age - ROUND_STEP * r
        if 0 <= a < CLOUD_DUR:
            k = a / CLOUD_DUR
            base = mix((200, 120, 80), DUST, .3) if dust else mix(col, DUST, .5)
            rr = r * 1.415 + .7
            for dy in range(-r - 2, r + 3):
                for dx in range(-r - 2, r + 3):
                    if max(abs(dx), abs(dy)) <= r or dx * dx + dy * dy > rr * rr:
                        continue
                    if k > .6 and ((x + dx) * 73856093 ^ (y + dy) * 19349663) % 5 == 0:
                        continue                # a few puffs thin out first: a ragged edge
                    out.append((x + dx, y + dy, '░' if k < .55 else '·', mix(base, (14, 12, 12), .35 + .55 * k), None))
    return out


def slant(x, y, n=4):
    """Where a Meteor falls from: a slanting line down onto (x, y) from the upper left, ending on it."""
    return [(x - k, y - k) for k in range(n, -1, -1)]


def sky_on(kw, age):
    """Whether the sky's white frame is lit at this age."""
    a = age - kw.get('delay', 0.0)
    return 0 <= a < SKY_TIME


def _fade(col, k):
    """A dimmer shade, never so dark that it reads as a black mark on lit ground."""
    return scale(col, .45 + .55 * max(0.0, min(1.0, k)))


def fx_cells(kind, kw, age):
    """The cells an effect lights at this age: [(x, y, sign, colour, background or None)]."""
    age -= kw.get('delay', 0.0)
    if age < 0:
        return []
    col = kw.get('col', (255, 255, 255))
    out = []
    if kind == 'bolt':
        cells = kw['cells']
        if not cells:
            return out
        n = len(cells)
        head = int(age / bolt_time(n) * n)
        ch = kw.get('ch', '*')
        if ch in '-|/\\':                       # arrows and stones point the way they fly
            sx, sy = kw.get('src', cells[0])
            ex, ey = cells[-1]
            ch = _line_char((ex > sx) - (ex < sx), (ey > sy) - (ey < sy))
        for k in range(4):                      # the head and a tail of three, fading
            i = head - k
            if 0 <= i < n:
                out.append((*cells[i], ch if k == 0 else '·' if k == 1 else '∙',
                            mix(col, (255, 255, 240), .35) if k == 0 else _fade(col, 1 - k * .28), None))
        return out
    if kind == 'burst':
        x, y, r = kw['x'], kw['y'], kw.get('r', 1)
        f = int(age / BURST_FRAME)
        if kw.get('gather'):                    # a big spell draws the light in for a frame first
            if f == 0:
                rr = r + 1
                return [(x + dx, y + dy, '·', _fade(col, .55), None) for dy in range(-rr, rr + 1)
                        for dx in range(-rr, rr + 1) if max(abs(dx), abs(dy)) == rr]
            f -= 1
        signs = kw.get('signs', '*+·')
        if r >= 1:
            return _round(x, y, r, col, age - (BURST_FRAME if kw.get('gather') else 0), signs, kw.get('hollow'),
                          dust=kw.get('dust'), dur=kw.get('dur', ROUND_DUR))
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                d = max(abs(dx), abs(dy))
                if kw.get('hollow') and d == 0:
                    continue
                s = f - d
                if 0 <= s < len(signs):
                    hot = mix(col, (255, 250, 220), .5) if s == 0 else _fade(col, 1 - s * .3)
                    out.append((x + dx, y + dy, signs[s], hot, None))
        return out
    if kind == 'drain':                         # motes of life flying from the foe back to you
        cells = kw['cells']
        n = len(cells)
        if not n:
            return out
        dur = kw.get('dur', .28)
        for j in range(3):
            k = (age - j * .06) / max(.01, dur - .12)
            if 0 <= k < 1:
                i = min(n - 1, int(k * n))
                out.append((*cells[i], '∙' if j else '•', _fade(col, 1 - j * .25), None))
        return out
    if kind == 'rise':                          # small crosses of light rising off whoever is healed
        x, y = kw['x'], kw['y']
        dur = kw.get('dur', .4)
        for j, dx in enumerate((0, -1, 1)):
            k = (age - j * .07) / (dur - .14)
            if 0 <= k < 1:
                out.append((x + dx, y - 1 - int(k * 2), '+', _fade(col, 1 - k * .7), None))
        return out
    if kind == 'zap':                           # a white zigzag that fades to yellow
        cells = kw['cells']
        k = age / .24
        if k >= 1:
            return out
        c = mix((255, 255, 255), col, k)
        for i, (cx, cy) in enumerate(cells):
            out.append((cx, cy, '/' if i % 2 == 0 else '\\', c, None))
        return out
    if kind == 'wave':                          # a ring running out from (x, y): the school's sign as its front
        x, y, r = kw['x'], kw['y'], kw.get('r', 1)
        sign = kw.get('sign', '*')
        quiet = sign in NO_GLOW
        signs = '*+·' if sign == '*' else (sign if sign != 'sound' else '(') + '·'
        return _round(x, y, r, col, age, signs, True, sign=sign if sign == 'sound' else None, glow=not quiet,
                      cloud=not quiet, dur=kw.get('dur', ROUND_DUR))
    if kind == 'meteor':                        # its shadow on the ground first, then it falls in at a slant
        x, y, r = kw['x'], kw['y'], kw.get('r', 1)
        shade = (52, 46, 44)
        k = min(1.0, age / METEOR_SHADOW)
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if dx == dy == 0 or k > .5:
                    out.append((x + dx, y + dy, '░', shade if dx == dy == 0 else mix(shade, (24, 22, 20), .4), None))
        fall = age - METEOR_SHADOW
        if fall >= 0:
            cells = slant(x, y)
            head = min(len(cells) - 1, int(fall / METEOR_FALL * len(cells)))
            for j in range(3):
                i = head - j
                if 0 <= i < len(cells):
                    out.append((*cells[i], '*' if j == 0 else '·',
                                mix(col, (255, 250, 220), .5) if j == 0 else _fade(col, 1 - j * .3), None))
        return out
    if kind == 'raise':                         # a corpse greys, then gets up as what it now is
        x, y = kw['x'], kw['y']
        k = age / RAISE_TIME
        if k >= 1:
            return out
        corpse, grave = kw.get('from_col', (150, 60, 50)), (150, 170, 140)
        if k < .55:
            return [(x, y, '%', mix(corpse, grave, k / .55), None)]
        return [(x, y, kw.get('ch', 'z'), mix((235, 245, 225), col, (k - .55) / .45), None)]
    if kind == 'trail':                         # one cell after another: a wall going up, dust behind a run
        cells = kw['cells']
        ch = kw.get('ch', '*')
        linger = kw.get('linger', .14)
        for i, c in enumerate(cells):
            a = age - i * TRAIL_STEP
            if 0 <= a < linger:
                q = a / linger
                out.append((*c, ch, mix((255, 255, 245), col, min(1.0, q * 2.5)) if kw.get('build') else
                            _fade(col, 1 - q), None))
        return out
    if kind == 'swing':                         # \ | / along the side of the foe, white fading to steel
        return _swing(kw, age)
    if kind == 'spin':                          # the blade once round you
        x, y = kw['x'], kw['y']
        for i, (dx, dy) in enumerate(((1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1))):
            a = age - i * SPIN_TICK
            if 0 <= a < SWING_LIT:
                out.append((x + dx, y + dy, _line_char(dx, dy), mix((255, 255, 250), STEEL_DIM, a / SWING_LIT), None))
        return out
    if kind == 'crit':                          # a white star that turns gold and fades
        k = age / CRIT_TIME
        if k < 1:
            out.append((kw['x'], kw['y'], '*', mix((255, 255, 255), GOLD_CRIT, min(1.0, k * 2)) if k < .6
                        else _fade(GOLD_CRIT, 1 - (k - .6) / .4), None))
        return out
    if kind == 'blood':                         # a red * on the cut, then drops fly back and darken
        x, y = kw['x'], kw['y']
        sx, sy = kw.get('src', (x - 1, y))
        dx, dy = (x > sx) - (x < sx), (y > sy) - (y < sy)
        k = age / BLOOD_TIME
        if k >= 1:
            return out
        if k < .3:
            out.append((x, y, '*', BLOOD_RED, None))
        for j, (ox, oy) in enumerate(((dx, dy), (dx - dy, dy + dx), (dx + dy, dy - dx))):
            ox, oy = max(-1, min(1, ox)), max(-1, min(1, oy))
            n = 1 + int(k * 1.8)                    # one tile out, then two
            if (ox or oy) and k > .1:
                out.append((x + ox * n, y + oy * n, ',' if j == 0 else '·', _fade(BLOOD_RED, 1 - k), None))
        return out
    return out


def _swing(kw, age):
    """The cells of a swing arc: the foe's tile and its neighbours on your side, swept in turn."""
    out = []
    sx, sy = kw.get('src', (0, 0))
    seen = set()
    for tx, ty in kw.get('cells', ()):
        dx, dy = (tx > sx) - (tx < sx), (ty > sy) - (ty < sy)
        dirs = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
        if (dx, dy) not in dirs:
            continue
        i = dirs.index((dx, dy))
        half = 2 if kw.get('wide') else 1
        far = max(abs(tx - sx), abs(ty - sy))
        for n, k in enumerate(range(-half, half + 1)):
            ex, ey = dirs[(i + k) % 8]
            c = (sx + ex * far, sy + ey * far)
            if c in seen:
                continue
            seen.add(c)
            a = age - n * SWING_TICK
            if 0 <= a < SWING_LIT:
                out.append((c[0], c[1], _line_char(ex, ey), mix((255, 255, 250), STEEL_DIM, a / SWING_LIT), None))
    return out


# ------------------------------------------------------------------ how a creature looks under a spell
BURN_COL, POISON_COL, ICE_BG = (255, 150, 50), (130, 230, 110), (54, 86, 112)
SHAPES = {'bear': ((214, 140, 76), (62, 38, 22)), 'wolf': ((236, 236, 240), (66, 76, 90)),
          'hawk': ((230, 200, 140), (48, 58, 80))}


def status_look(fg, bg, t, x, y, burn=False, poison=False, frozen=False, weak=False):
    """fg, bg and whether it moves: burning flickers orange, frozen stands on pale blue, poisoned pulses green,
    weakened is dimmed."""
    moving = False
    if frozen:
        fg, bg = (214, 236, 255), ICE_BG
    if weak:
        fg = scale(fg, .62)
    if poison:
        k = .5 + .5 * math.sin(t * 4.2 + x)
        fg, moving = mix(fg, POISON_COL, .35 + .45 * k), True
    if burn:
        f = flame(t * 1.4, x, y)
        fg, moving = mix(fg, BURN_COL, .35 + (f - .7) * 2.2), True
    return fg, bg, moving


def shape_of(p):
    """The beast you have become, if any ('bear', 'wolf'), from your buffs."""
    for b in p.buffs:
        if b[0] == 'dmg' and str(b[3]).endswith(' shape'):
            return b[3][:-6].lower()
    return None


def player_look(p, bg, t):
    """Your @: in a beast's shape it takes the beast's colours, and shows burning and poison like any creature."""
    fg = (255, 246, 220)
    sh = shape_of(p)
    if sh:
        fg, bg = SHAPES.get(sh, ((200, 170, 120), bg))
    return status_look(fg, bg, t, p.x, p.y, burn=bool(p.burn), poison=bool(p.poison))


# ------------------------------------------------------------------ smoke from the chimneys
_CHIMNEYS = {}
SMOKE = (204, 200, 190)


def chimneys(m):
    """One chimney on the roof wall of each wooden house (a top wall with planks under it), worked out once."""
    key = (m.key, m.w, m.h)
    if key in _CHIMNEYS:
        return _CHIMNEYS[key]
    out = []
    t, w = m.t, m.w
    for y in range(1, m.h - 1):
        run = []
        for x in range(m.w + 1):
            ok = x < m.w and t[y * w + x] == D.WALL and t[(y + 1) * w + x] == D.PLANK and \
                D.TILES[t[(y - 1) * w + x]].walk
            if ok:
                run.append(x)
                continue
            if len(run) >= 4:
                out.append((run[0] + 1 + _h(run[0], y, 5) % (len(run) - 2), y))
            run = []
    _CHIMNEYS[key] = out
    return out


def smoke(cx, cy, t, day, winter, late):
    """The puffs rising from one chimney now: [(x, y, sign, colour)]; most hearths are lit, all of them in winter."""
    if not winter and _h(cx, cy, day) % 10 >= 8:
        return []
    drift = 1 if _h(day, 3, 11) % 2 else -1          # the day's wind leans every plume the same way
    out = []
    for j in range(4):
        k = (t * .3 + j / 4 + _h(cx, cy, 9) / 65536) % 1.0
        col = scale(SMOKE, (1 - .65 * k) * (.55 if late else 1))
        out.append((cx + round(k * k * 2 * drift), cy - 1 - int(k * 4), '°' if k < .3 else 'o' if k < .6 else '·', col))
    return out
