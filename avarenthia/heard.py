"""Heard, lit and seen (round 63): noise, what you hear, noticing as a sum, light that lives, the last-seen marks.

- Noise. What you do makes noise: walking 1, a fight 4-6, a spell by its school, a door kicked in 8; heavy armour
  +1 to +3. It runs along the halls and through doors (doors swallow some), never through rock. A foe that hears it
  and does not see you comes to look where it was; it does not wake the whole place at once.
- Seen, not heard: a loud noise draws one pale ring of ◦ that runs out through the halls (an effect, `('ring', ...)`).
  A foe that heard you and comes to look has ? before its name in IN SIGHT. The line under the map says how loud you
  are now: Quiet, Soft, Loud.
- What you hear: a foe moving out of sight leaves a dim silver-blue sign about where it was (its letter when you know
  its kind, else ?), with a log line now and then; it fades after a few turns. Better Cunning hears further.
- Noticing is a sum: the light on your tile, the distance, your armour and sneak, the foe's kind.
- Light that lives: what burns gives light while it burns (burning ground, a fire spell for a turn, lightning over a
  room, lava, a burning house); a torch put out darkens a room; shadows fall as the light's own sight falls.
- Last seen: a foe that walks out of sight leaves a dim mark of its letter where you saw it last, until you look there.

What is on the map (`m.heard`, `m.last_seen`, `m.flares`) is the map's; how loud you were lives on the player."""
import random
from collections import deque

from . import data as D

HEARD = (150, 170, 210)              # dim silver-blue: the colour of "heard"
RING = (176, 192, 226)
WORDS = ((1, 'Quiet'), (3, 'Soft'), (99, 'Loud'))
SCHOOL = {'fire': 6, 'storm': 7, 'frost': 4, 'shadow': 1, 'nature': 3, 'arcane': 3, 'necromancy': 3,
          'restoration': 2, 'warcraft': 5, 'beastcraft': 4, 'cunning': 1, 'unarmed': 4, 'swords': 5, 'axes': 5,
          'spears': 5, 'daggers': 3, 'archery': 3}
DOOR_COST = 3                       # a closed door swallows this much of a noise
HEAR_FADE = 6                       # turns a heard sign stays
LOOK_TURNS = 14                     # how long a foe that heard you looks before it gives up
MAX_CELLS = 900


def _walk(m, i):
    t = m.t[i]
    return D.TILES[t].walk or D.TILES[t].door


def spread(m, x, y, r):
    """{(x, y): distance} along the halls and through doors from a noise, never through rock."""
    if not m.inb(x, y):
        return {}
    out = {(x, y): 0}
    q = deque([(x, y, 0)])
    while q and len(out) < MAX_CELLS:
        cx, cy, d = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
            nx, ny = cx + dx, cy + dy
            if not m.inb(nx, ny) or (nx, ny) in out:
                continue
            i = ny * m.w + nx
            if not _walk(m, i):
                continue
            nd = d + 1 + (DOOR_COST if m.t[i] == D.DOOR else 0)
            if nd > r:
                continue
            out[(nx, ny)] = nd
            q.append((nx, ny, nd))
    return out


def armour_noise(game):
    """+0 to +3 for what you wear: leather is quiet, chain clinks, plate clanks."""
    it = game.eq_item('armor')
    if not it:
        return 0
    fam = D.BASES[it.base].get('family', it.base)
    return {'platemail': 3, 'chainmail': 2}.get(fam, 0)


def hears_well(mon):
    """Bosses, wardens and beasts hear further."""
    from .creatures import BEASTS
    d = mon.tpl
    return d.get('boss') or d.get('chief') or mon.k in BEASTS or 'warden' in mon.k or 'sentry' in mon.k


def make(game, x, y, level, what='noise'):
    """A noise at (x, y). Foes that do not see you and are within its reach come to look; a loud one draws the ring."""
    m = game.map
    if m.kind == 'over' or level <= 0:
        return
    p = game.player
    if (x, y) == (p.x, p.y):
        last = getattr(p, 'loud', None)
        p.loud = (max(level, last[0]) if last and last[1] == game.turn else level, game.turn)
    r = level * 2
    field = spread(m, x, y, r + 4)
    for mon in m.mons:
        if mon.is_npc or getattr(mon, 'ally', False) or mon.hp <= 0:
            continue
        d = field.get((mon.x, mon.y))
        if d is None or d > r + (4 if hears_well(mon) else 0):
            continue
        mon.heard_you = game.turn
        if mon.awake:
            continue
        if getattr(mon, 'lurk', False) or mon.tpl.get('slow') and random.random() < .5:
            continue
        if not game.visible(mon.x, mon.y):
            mon.look_at = (x, y)
            mon.look_until = game.turn + LOOK_TURNS
            fields = getattr(m, 'noise_fields', None)
            if fields is None or not isinstance(fields, dict):
                m.noise_fields = fields = {}
            fields[(x, y)] = field
            while len(fields) > 4:
                fields.pop(next(iter(fields)))
    if level >= 4:
        ring = [(cx, cy, d) for (cx, cy), d in field.items() if d <= r and m.seen[cy * m.w + cx]]
        if ring:
            game.events.append(('ring', r, ring[:600]))
    from . import guide as GDE
    if level >= 4 and any(getattr(o, 'look_at', None) == (x, y) for o in m.mons):
        GDE.tip(game, 'heard')


def loudness(game):
    """'Quiet', 'Soft' or 'Loud': how loud you were this turn and the one before."""
    p = game.player
    last = getattr(p, 'loud', None)
    lvl = last[0] if last and game.turn - last[1] <= 1 else 0
    return next(w for top, w in WORDS if lvl <= top)


# ------------------------------------------------------------------ what you do
def walked(game):
    make(game, game.player.x, game.player.y, 1 + armour_noise(game), 'walk')


def fought(game, ranged=False):
    make(game, game.player.x, game.player.y, (4 if ranged else 5) + armour_noise(game) // 2, 'fight')


def spell(game, line):
    make(game, game.player.x, game.player.y, SCHOOL.get(line, 3), 'spell')
    if line == 'fire':
        flare(game, game.player.x, game.player.y, 5, (255, 150, 60), 1)
    elif line == 'storm':
        flare(game, game.player.x, game.player.y, 12, (200, 210, 255), 1)
        if random.random() < .5:
            put_out(game, game.player.x, game.player.y, 4, 'The gust of your storm puts out a torch.')


def door(game, x, y, kicked=False):
    make(game, x, y, 8 if kicked else 2, 'door')


# ------------------------------------------------------------------ foes that come to look
def look_turn(game, mon):
    """An unaware foe that heard you walks to where the noise was. True when it used its turn."""
    la = getattr(mon, 'look_at', None)
    if la is None:
        return False
    if game.turn > getattr(mon, 'look_until', 0) or (mon.x, mon.y) == la:
        if game.turn > getattr(mon, 'look_until', 0) or random.random() < .3:
            mon.look_at = None                       # nothing there: it gives up
        return True
    m = game.map
    field = (getattr(m, 'noise_fields', None) or {}).get(la)
    best = None
    here = field.get((mon.x, mon.y), 99) if field else None
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
        nx, ny = mon.x + dx, mon.y + dy
        if not m.inb(nx, ny) or game.occupied(m, nx, ny):
            continue
        t = m.tile(nx, ny)
        if not (D.TILES[t].walk or t == D.DOOR):
            continue
        if field is not None:
            d = field.get((nx, ny))
            if d is None or d >= here:
                continue
        else:
            d = max(abs(nx - la[0]), abs(ny - la[1]))
            if d >= max(abs(mon.x - la[0]), abs(mon.y - la[1])):
                continue
        if best is None or d < best[0]:
            best = (d, nx, ny)
    if best is None:
        mon.look_at = None
        return True
    if m.tile(best[1], best[2]) == D.DOOR:
        m.set(best[1], best[2], D.ODOOR)
        return True
    mon.x, mon.y = best[1], best[2]
    return True


def coming(mon):
    """It heard you and comes to look (IN SIGHT puts ? before its name)."""
    return not mon.awake and getattr(mon, 'look_at', None) is not None


# ------------------------------------------------------------------ noticing as a sum
def light_on(game, x, y):
    """0 (dark) to about 1.5 (bright): the light falling on a cell from the map's lights and what burns now."""
    m = game.map
    if m.kind in ('over',):
        return 1.0
    from . import towns as TW
    if m.kind in ('town', 'wild') and not getattr(m, 'underground', False):
        return .4 if TW.is_night(game) else 1.2
    if getattr(m, 'sky', None) is not None:
        return 1.0
    from . import dress as DR
    i = y * m.w + x
    c = DR.light_map(m)[i]
    amb = getattr(m, 'ambient', .3)
    base = amb if not isinstance(amb, tuple) else sum(amb) / 3
    k = max(0.0, sum(c) / 3 - base)
    for fx, fy, r, _col, _until in live_flares(game):
        dd = max(abs(fx - x), abs(fy - y))
        if dd <= r:
            k += (1 - dd / (r + 1)) * .9
    for dy in (-2, -1, 0, 1, 2):
        for dx in (-2, -1, 0, 1, 2):
            if m.inb(x + dx, y + dy) and m.tile(x + dx, y + dy) in BURNS:
                k += .25
    return min(1.5, k)


def notice(game, mon, base):
    """The sum: base (the old chance) by the light on your tile, the distance, your armour, the foe's kind and
    whether it heard you. The undead see by no light."""
    from .affixes import undead
    p = game.player
    d = max(abs(mon.x - p.x), abs(mon.y - p.y))
    if undead(mon.k):
        light = 1.0
    else:
        light = .45 + .55 * min(1.0, light_on(game, p.x, p.y))
    far = 1.0 if d <= 2 else max(.35, 1 - (d - 2) * .08)
    arm = 1 + .08 * armour_noise(game)
    kind = 1.25 if hears_well(mon) else 1.0
    heard = 1.4 if getattr(mon, 'heard_you', -99) >= game.turn - 3 else 1.0
    return min(.95, base * light * far * arm * kind * heard)


# ------------------------------------------------------------------ light that lives
BURNS = set()


def _burns():
    for name in ('BURNING', 'LAVA', 'MOLTEN', 'FIREPIT', 'FIREBOWL', 'FIREGATE', 'HEARTH'):
        if hasattr(D, name):
            BURNS.add(getattr(D, name))


_burns()


def flare(game, x, y, r, col, turns=1):
    """A light that lives for a while: a fire spell's flash, lightning over a room, a burning house."""
    m = game.map
    fl = [f for f in (getattr(m, 'flares', None) or []) if f[4] >= game.turn]
    fl.append((x, y, r, col, game.turn + turns))
    m.flares = fl[-8:]


def live_flares(game):
    return [f for f in (getattr(game.map, 'flares', None) or []) if f[4] >= game.turn]


def glows(game):
    """(x, y, colour, r) of the living light now, for the screen: flares, and what burns in view."""
    out = [(f[0], f[1], f[3], f[2]) for f in live_flares(game)]
    return out


def put_out(game, x, y, r=1, why=''):
    """A torch or lamp put out (a foe, wind, water): the room goes darker."""
    m = game.map
    lights = getattr(m, 'lights', None)
    if not lights:
        return False
    keep = [li for li in lights if max(abs(li[0] - x), abs(li[1] - y)) > r]
    if len(keep) == len(lights):
        return False
    m.lights = keep
    m._light = None
    if why and game.visible(x, y):
        game.msg(why, 'info')
    return True


def foes_put_out(game):
    """Things of the dark put out the torches near them, now and then."""
    m = game.map
    for o in m.mons:
        if not o.is_npc and 'darkness' in o.tpl.get('beh', ()) and o.awake and random.random() < .08:
            put_out(game, o.x, o.y, 2, f'{o.the()[0].upper() + o.the()[1:]} snuffs out a light.')


# ------------------------------------------------------------------ what you hear, and the last seen
def hear_range(game):
    c = game.player.disc.get('cunning', [0])[0]
    return 7 + c // 10


def know(game, k):
    from . import bestiary as BE
    return BE.step(game, k) >= 2 or game.player.disc.get('cunning', [0])[0] >= 30


def sound_word(mon):
    from .affixes import undead
    from .creatures import BEASTS
    d = mon.tpl
    if undead(mon.k):
        return 'Something scrapes'
    if mon.k in ('ogre', 'troll') or d.get('boss') or mon.maxhp >= 80:
        return 'Heavy feet'
    if mon.k in BEASTS:
        return 'Claws on stone'
    return 'Footsteps'


def after_turn(game):
    """After the foes moved: what you hear of them out of sight, the last-seen marks, the heard signs fading."""
    m = game.map
    if m.kind == 'over' or getattr(m, 'mons', None) is None:
        return
    from . import engine as E
    p = game.player
    turn = game.turn
    heard = getattr(m, 'heard', None)
    if heard is None or not isinstance(heard, dict):
        m.heard = heard = {}
    for k in [k for k, v in heard.items() if turn - v[2] > HEAR_FADE or game.visible(*k)]:
        del heard[k]
    last = getattr(m, 'last_seen', None)
    if last is None or not isinstance(last, dict):
        m.last_seen = last = {}
    seen_now = getattr(m, '_seen_foes', None) or {}
    now = {}
    rng = hear_range(game)
    said = getattr(p, 'heard_said', 0)
    for o in m.mons:
        if o.is_npc or getattr(o, 'ally', False) or o.hp <= 0 or getattr(o, 'lurk', False):
            continue
        if game.visible(o.x, o.y):
            now[o.id] = (o.x, o.y, o.ch, o.fg)
            last.pop(o.id, None)
            continue
        if o.id in seen_now:                             # it walked out of sight: a dim mark where it was
            x, y, ch, fg = seen_now[o.id]
            last[o.id] = [x, y, ch, coming(o), False]
        moving = o.awake or coming(o)
        d = max(abs(o.x - p.x), abs(o.y - p.y))
        if moving and d <= rng and random.random() < .6:
            jx, jy = o.x + random.randint(-1, 1), o.y + random.randint(-1, 1)
            if m.inb(jx, jy) and not game.visible(jx, jy):
                heard[(jx, jy)] = ('?' if not know(game, o.k) else o.ch, HEARD, turn)
                if turn - said > 12 and d <= rng - 1:
                    p.heard_said = said = turn
                    way = E.dir_name(o.x - p.x, o.y - p.y)
                    game.msg(f'{sound_word(o)}, to the {way}.', 'info')
    m._seen_foes = now
    alive = {o.id for o in m.mons}
    for k in list(last):
        v = last[k]
        if k not in alive:
            del last[k]
        elif not game.visible(v[0], v[1]):
            v[4] = True                                  # out of view now: the next look there takes it away
        elif v[4]:
            del last[k]
    foes_put_out(game)


def marks(game):
    """[(x, y, sign, colour)] to draw dim on the map: heard sounds and last-seen letters, out of sight."""
    m = game.map
    out = []
    for (x, y), (ch, col, _t) in (getattr(m, 'heard', None) or {}).items():
        out.append((x, y, ch, col))
    for _k, v in (getattr(m, 'last_seen', None) or {}).items():
        x, y, ch, came = v[0], v[1], v[2], v[3]
        out.append((x, y, ch, (110, 110, 120)))
        if came and m.inb(x + 1, y):
            out.append((x + 1, y, '?', HEARD))
    return out
