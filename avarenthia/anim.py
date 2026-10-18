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
          D.BURNING, D.BALL, D.HALLOWED, D.SPIRITTOTEM}
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
