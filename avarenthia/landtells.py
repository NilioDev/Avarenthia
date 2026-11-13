"""The land tells: each sign has one meaning, seen before you meet the thing (round 62).

- Smoke from afar: light smoke climbs over a village or town on the world map and drifts with the day's wind; over
  one that burns or was plundered it is dark, with a small red fire that flickers.
- Birds flushing: a few birds burst up from a wood a few steps before an ambush there, with a log line; Cunning
  sees them sooner.
- Vultures: three circle slowly over a field after a fight, a dead giant or a battlefield.
- Worn paths: where you and the caravans walk often, the grass becomes a path; it grows over when no one comes.
- Villages rebuilt: a settlement struck by a raid, a war, a dragon, a great evil or a fire is rebuilt over weeks,
  seen on its map: burnt roofs first, then fresh timber, then whole again.

All of it is worked out from what is there (the day, the world's lists); the moving signs are drawn by the clock and
never saved. The world keeps `w.vultures` and `w.wear`; what belongs to the player (an ambush waiting) lives on the
player."""
import math
import random

from . import data as D
from .canvas import mix, scale
from .look import _h

SMOKE = (196, 192, 184)
DARK = (70, 62, 58)
FIRE = (236, 92, 30)
BIRD = (186, 180, 168)
VULTURE = (150, 128, 112)
WORN = (150, 132, 96)
WOOD = (8,)                                    # world-map tiles that are woods (birds rise from them)
WEAR_PATH = 10.0                               # steps on a cell before the grass shows a path
WEAR_FADE = .35                                # what a day takes off (a path grows over in about a month)
VULTURE_DAYS = 2
PLUMES = {'hamlet': 1, 'village': 1, 'town': 2, 'city': 3, 'metropolis': 4, 'deephold': 0}
HARM_WORDS = {'raid': 'raiders', 'war': 'the war', 'dragon': 'a dragon', 'evil': 'a great evil', 'fire': 'a fire',
              'rift': 'the things out of the rift', 'plunder': 'soldiers'}


# ------------------------------------------------------------------ villages struck and rebuilt
def harm(game, s, kind='plunder', days=None):
    """A settlement struck: it burns, and is rebuilt over weeks (burnt roofs, fresh timber, whole)."""
    from .living import PLUNDER_DAYS
    s.plundered = game.day + (days or PLUNDER_DAYS)
    s.harm = kind
    s.harm_day = game.day


def stage(game, s):
    """None (whole), 'burnt' or 'timber': how far its rebuilding has come."""
    until = getattr(s, 'plundered', 0)
    if until <= game.day:
        return None
    start = getattr(s, 'harm_day', None)
    if start is None:
        from .living import PLUNDER_DAYS
        start = until - PLUNDER_DAYS
    frac = (game.day - start) / max(1, until - start)
    return 'burnt' if frac < .45 else 'timber'


def burning(game, s):
    """Still burning: the first days after it was struck."""
    st = getattr(s, 'harm_day', None)
    return stage(game, s) == 'burnt' and st is not None and game.day - st <= 2


# ------------------------------------------------------------------ smoke from afar
def wind(game):
    """The day's wind: -1 (to the west) or 1 (to the east), by the weather's wind if it blows."""
    return 1 if _h(game.day, 3, 11) % 2 else -1


def smoke(game, s, t, night):
    """The puffs over one settlement now: [(x, y, sign, colour)]. Light smoke by day and evening; dark smoke and a red
    fire over one that burns or was plundered not long ago (seen by night too)."""
    st = stage(game, s)
    n = PLUMES.get(s.kind, 1)
    if not n:
        return []
    dark = st == 'burnt'
    if night and not dark:
        return []
    drift = wind(game)
    out = []
    for p in range(n if not dark else max(2, n)):
        cx = s.x + (p - (n - 1) // 2) * (1 if p % 2 else -1) * (p > 0)
        for j in range(4):
            k = (t * .25 + j / 4 + _h(s.x + p, s.y, 9) / 65536) % 1.0
            col = scale(DARK if dark else SMOKE, (1 - .6 * k))
            out.append((cx + round(k * k * 2 * drift), s.y - 1 - int(k * 4),
                        '§' if k < .3 else '°' if k < .6 else '·', col))
    if dark:
        f = .6 + .4 * math.sin(t * 9 + s.x)
        out.append((s.x + (1 if _h(s.x, s.y, 4) % 2 else -1), s.y, '*', scale(FIRE, .7 + .3 * f)))
    return out


# ------------------------------------------------------------------ birds before an ambush
def woods_near(game, x, y, r=3):
    om = game.maps['over']
    out = []
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if (dx or dy) and om.inb(x + dx, y + dy) and om.t[(y + dy) * om.w + x + dx] in WOOD:
                out.append((x + dx, y + dy))
    return out


def warning(game):
    """How many steps of warning the birds give: more with Cunning."""
    c = game.player.disc.get('cunning', [0])[0]
    return 2 + (1 if c >= 20 else 0) + (1 if c >= 40 else 0)


def flush(game, lvl, keys, elite, terrain):
    """An ambush rolled by a wood: birds burst up first, and it falls on you a few steps later. True when the birds
    went up (the ambush waits on the player), False when there is no wood to warn you."""
    p = game.player
    trees = woods_near(game, p.x, p.y)
    if not trees:
        return False
    bx, by = random.choice(trees)
    p.ambush = dict(n=warning(game), lvl=lvl, keys=keys, elite=elite, terrain=terrain, at=(bx, by))
    from . import engine as E
    way = E.dir_name(bx - p.x, by - p.y)
    game.msg(f'Birds burst from the trees to the {way}.', 'bad')
    game.events.append(('birds', bx, by, 1 if bx >= p.x else -1))
    return True


def step(game):
    """On the world map: an ambush the birds told of comes nearer. True when it falls on you now."""
    p = game.player
    a = getattr(p, 'ambush', None)
    if not a:
        return False
    a['n'] -= 1
    if a['n'] > 0:
        return False
    p.ambush = None
    game.start_encounter(None, a['terrain'], a['lvl'], a['keys'], a['elite'])
    return True


def calm(game):
    """You left the world map (a town, a place): whatever waited in the wood lets you go."""
    if getattr(game.player, 'ambush', None):
        game.player.ambush = None


def birds(ev, age):
    """The birds bursting from a wood now: [(x, y, sign)] for age seconds after."""
    _k, bx, by, drift = ev
    out = []
    for j in range(4):
        a = age * (5 + j)
        x = bx + round(drift * a * .6 + (j - 1.5) * a * .4)
        y = by - int(a * (1.5 + j * .3))
        out.append((x, y, '^' if int(age * 12 + j) % 2 else 'v'))
    return out


# ------------------------------------------------------------------ vultures
def vultures(game, x, y, days=VULTURE_DAYS):
    """Something lies dead here: three vultures circle over it for a while."""
    w = game.world
    vs = [v for v in getattr(w, 'vultures', []) if v[2] >= game.day and max(abs(v[0] - x), abs(v[1] - y)) > 1]
    vs.append((x, y, game.day + days))
    w.vultures = vs[-12:]


def vulture_cells(game, t):
    """The circling birds now: [(x, y)]; over the fresh fights and the battlefields."""
    w = game.world
    spots = [(v[0], v[1]) for v in getattr(w, 'vultures', []) if v[2] >= game.day]
    from .living import BATTLE_DAYS
    spots += [(b['x'], b['y']) for b in getattr(w, 'battles', []) if game.day - b['day'] < min(BATTLE_DAYS, 8)]
    out = []
    for x, y in spots:
        for j in range(3):
            a = t * .7 + j * 2.094 + _h(x, y, 2) / 9000
            out.append((x + round(math.cos(a) * 1.6), y - 1 + round(math.sin(a) * .9)))
    return out


# ------------------------------------------------------------------ worn paths
def wear(game, x, y, n=1.0):
    """A step on the land off the road: the grass wears."""
    om = game.maps['over']
    i = y * om.w + x
    if om.t[i] != D.GRASS:
        return
    w = game.world
    if not hasattr(w, 'wear') or w.wear is None:
        w.wear = {}
    w.wear[i] = min(40.0, w.wear.get(i, 0.0) + n)


def daily(game):
    """Each day the grass grows back a little; the vultures fly off."""
    w = game.world
    wr = getattr(w, 'wear', None)
    if wr:
        for i in list(wr):
            v = wr[i] - WEAR_FADE
            if v <= 0:
                del wr[i]
            else:
                wr[i] = v
    if getattr(w, 'vultures', None):
        w.vultures = [v for v in w.vultures if v[2] >= game.day]


def worn(game, i):
    return getattr(game.world, 'wear', {}).get(i, 0) >= WEAR_PATH


def caravans_wear(game):
    """The caravans on the land wear the grass where they pass (called each day)."""
    for wd in getattr(game.world, 'wanderers', []):
        if wd.kind in ('caravan', 'merchant', 'pilgrims', 'herd') or getattr(wd, 'caravan', False):
            wear(game, wd.x, wd.y, 2.0)


# ------------------------------------------------------------------ drawing on the world map
def draw_over(screen, cv, ox, oy, map_w, map_h):
    """Smoke, vultures and worn paths on the world map (GameScreen.draw_overworld_extras)."""
    import time
    from . import towns as TW
    g = screen.game
    p = g.player
    om = g.map
    t = time.monotonic()
    night = TW.is_night(g)
    moving = False

    def put(x, y, ch, col):
        vx, vy = x - ox, y - oy
        if 0 <= vx < map_w and 0 <= vy < map_h and (x, y) != (p.x, p.y) and om.inb(x, y):
            cv.put(vx, vy, ch, col)
    wr = getattr(g.world, 'wear', None)
    if wr:
        for i, v in wr.items():
            if v >= WEAR_PATH and om.seen[i]:
                x, y = i % om.w, i // om.w
                if 0 <= x - ox < map_w and 0 <= y - oy < map_h and om.t[i] == D.GRASS:
                    put(x, y, '·', scale(WORN, .55 if not g.vis[i] else 1))
    for s in g.world.settlements:
        if not g.known_settlement(s) or abs(s.x - p.x) > map_w or abs(s.y - p.y) > map_h:
            continue
        for x, y, ch, col in smoke(g, s, t, night):
            if g.world.settlement_at(x, y) is None:
                put(x, y, ch, col)
                moving = True
    if not night:
        for x, y in vulture_cells(g, t):
            if om.inb(x, y) and om.seen[y * om.w + x]:
                put(x, y, 'ˇ', VULTURE)
                moving = True
    return moving


def town_look(game, s, m):
    """On the settlement's own map: burnt roofs while it is 'burnt', fresh timber while it is 'timber', whole after.
    Kept on m.burnt_cells / m.burnt_stage (living.on_enter_town lays the burnt ones)."""
    st = stage(game, s)
    cells = getattr(m, 'burnt_cells', None)
    if not cells or st != 'timber' or getattr(m, 'burnt_stage', None) == 'timber':
        return
    over = m.over
    for i in cells:
        x, y = i % m.w, i // m.w
        t = m.t[i]
        if t == D.WALL:
            over[i] = ('#', (214, 170, 104), (52, 36, 20))           # fresh timber on the old stones
        elif _h(x, y, 73) % 3 == 0:
            over[i] = ('=', (190, 150, 92), (40, 30, 18))             # planks and beams lying ready
        else:
            over.pop(i, None)
    m.burnt_stage = 'timber'
    m._look = None


def view_signs(g):
    """What the land tells in view on the world map, for the look legend: [((sign, colour), name)]."""
    import time
    from . import towns as TW
    out = []
    t = time.monotonic()
    night = TW.is_night(g)
    p = g.player
    near = [s for s in g.world.settlements if g.known_settlement(s) and max(abs(s.x - p.x), abs(s.y - p.y)) <= 30]
    if any(stage(g, s) == 'burnt' for s in near):
        out.append((('§', DARK), 'Dark smoke: a place that burns, or burnt not long ago'))
    if not night and any(stage(g, s) != 'burnt' and PLUMES.get(s.kind, 1) for s in near):
        out.append((('§', SMOKE), 'Smoke over a village or town'))
    if not night and any(g.visible(x, y) for x, y in vulture_cells(g, t) if g.map.inb(x, y)):
        out.append((('ˇ', VULTURE), 'Vultures: something lies dead there'))
    om = g.map
    if any(g.vis[i] for i in getattr(g.world, 'wear', {}) if worn(g, i) and i < len(g.vis)):
        out.append((('·', WORN), 'A worn path through the grass'))
    return out
