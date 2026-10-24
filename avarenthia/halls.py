"""Abbeys, forts and manors of every people (round 7), each on its own land (places.land).

An abbey (100 x 60) is where the devout of a people live, learn and keep lore; a fort (100 x 60) is built to hold
ground, and its way in is its one telling thing; a manor (80 x 50) is the house of someone who matters, and its
telling thing says who lives there. Each people builds its own, under its own name (`docs/plan.md`, approved 22
October 2026). Upper floors are levels of their own over the air (style 'upper': `site.up`, drawn by upper_map);
a fort's tower follows the tower rules (towers.py). Cellars, cells and deeper halls lie below (`site.below`).

Who may come how far in depends on your name with that people, as with temples (places.tier). A fort may also be
taken by bandits, abandoned, or a ruin (`site.state`)."""
import math
import random

from . import data as D
from .data import FLOOR, WALL, DOOR, PATH, UP, DOWN, PLANK, AIR
from .entities import GameMap, make_monster
from .worldgen import cheb
from . import places as PL
from . import temples as TP

SIZE = {'monastery': (100, 60), 'fort': (100, 60), 'manor': (80, 50)}
NOUN = {'monastery': 'abbey', 'fort': 'fort', 'manor': 'manor'}
KIND_NAME = {
    'monastery': {'human': 'Abbey', 'elf': 'Starhaven', 'dwarf': 'Rune Hall', 'halfling': 'Harvest House',
                  'gnome': 'Lantern House', 'orc': 'Spirit Lodge', 'goblin': 'Scroll Warren', 'kobold': 'Gleam House',
                  'gnoll': 'Bone Kraal', 'lizard': 'Hatchery'},
    'fort': {'human': 'Keep', 'elf': 'Thornwatch', 'dwarf': 'Gatehold', 'halfling': 'Hedge Post', 'gnome': 'Hidden Hill',
             'orc': 'Stockade', 'goblin': 'Scrap Fort', 'kobold': 'Trap Gate', 'gnoll': 'War Boma', 'lizard': 'Stilt Bastion'},
    'manor': {'human': 'Manor', 'elf': 'Bower', 'dwarf': 'Clan House', 'halfling': 'Hill Hall', 'gnome': 'Cap House',
              'orc': 'Longhouse', 'goblin': 'Counting House', 'kobold': 'Hoard Burrow', 'gnoll': 'Great Tent',
              'lizard': 'Sun House'},
}
NAMES = {
    'monastery': {'elf': ['The Starhaven', 'The Haven of Stars', 'The White Garden'],
                  'dwarf': ['The Rune Hall', 'The Hall of Carved Lore', 'The Stone Book'],
                  'halfling': ['The Harvest House', 'The House of Plenty', 'The Long Table'],
                  'gnome': ['The Lantern House', 'The House of Lenses', 'The Lit Hollow'],
                  'orc': ['The Spirit Lodge', 'The Lodge of Drums', 'The Smoke Lodge'],
                  'goblin': ['The Scroll Warren', 'The Warren of Stolen Words', 'The Ink Hole'],
                  'kobold': ['The Gleam House', 'The Polishing Hall', 'The House of Shine'],
                  'gnoll': ['The Bone Kraal', 'The Kraal of the Moon', 'The Howling Kraal'],
                  'lizard': ['The Hatchery', 'The Warm Mud', 'The House of Eggs']},
    'fort': {'human': ['Keep', 'Castle', 'Hold'],
             'elf': ['The Thornwatch', 'The Briar Ward', 'The Thorn Ring'],
             'dwarf': ['The Gatehold', 'The Gorge Gate', 'The Iron Gate'],
             'halfling': ['The Hedge Post', 'The Bell Hedge', 'The Watch Hedge'],
             'gnome': ['The Hidden Hill', 'The Empty Hill', 'The Hill That Is Not'],
             'orc': ['The Stockade', 'The Stake Fort', 'The Red Stockade'],
             'goblin': ['The Scrap Fort', 'The Junk Ring', 'The Cart Fort'],
             'kobold': ['The Trap Gate', 'The Tunnel of Teeth', 'The Snare Gate'],
             'gnoll': ['The War Boma', 'The Thorn Boma', 'The Ring of Spears'],
             'lizard': ['The Stilt Bastion', 'The Reed Fort', 'The Water Fort']},
    'manor': {'human': ['Manor', 'Hall', 'House', 'Court'],
              'elf': ['The Bower', 'The Moon Bower', 'The House of Four Trees'],
              'dwarf': ['The Clan House', 'The Carved Door', 'The Hearth House'],
              'halfling': ['The Hill Hall', 'The Green Hill', 'The Round Door'],
              'gnome': ['The Cap House', 'The Mushroom House', 'The Red Cap'],
              'orc': ['The Longhouse', "The Chief's Hall", 'The Skull House'],
              'goblin': ['The Counting House', "The Boss's House", 'The Ledger Hole'],
              'kobold': ['The Hoard Burrow', 'The Coin Bed', 'The Shiny Hole'],
              'gnoll': ['The Great Tent', "The Packlord's Tent", 'The Hide Hall'],
              'lizard': ['The Sun House', "The Elder's House", 'The Stilt House']},
}
OWNER = {'human': ['Lord {n}', 'Lady {n}'], 'elf': ['{n} of the Bower'], 'dwarf': ['Clanlord {n}'],
         'halfling': ['{n} of the Hill'], 'gnome': ['Master {n}'], 'orc': ['Chief {n}'], 'goblin': ['Boss {n}'],
         'kobold': ['Hoardmaster {n}'], 'gnoll': ['Packlord {n}'], 'lizard': ['Elder {n}']}
# what lies below: (tag, name, levels)
BELOW = {
    'monastery': {'human': ('crypt', 'The Cellars of {n}'), 'elf': ('cave', 'The Root Halls under {n}'),
                  'dwarf': ('crypt', 'The Deep Archive of {n}'), 'halfling': ('cave', 'The Pantry Cellars of {n}'),
                  'gnome': ('cave', 'The Deep Workshop of {n}'), 'orc': ('lair_orc', 'The Spirit Cave'),
                  'goblin': ('warren', 'The Vault of Secrets'), 'kobold': ('den', 'The Deep Hoard'),
                  'gnoll': ('burrow', 'The Bone Tunnels'), 'lizard': ('swamp', 'The Drowned Halls under {n}')},
    'fort': {'human': ('dungeon', 'The Dungeon of {n}'), 'elf': ('cave', 'The Root Cellars of {n}'),
             'dwarf': ('dungeon', 'The Halls under {n}'), 'halfling': ('cave', 'The Root Cellar of {n}'),
             'gnome': ('cave', 'The Deep Burrows of {n}'), 'orc': ('lair_orc', 'The Pits under {n}'),
             'goblin': ('warren', 'The Tunnels under {n}'), 'kobold': ('den', 'The Warrens behind {n}'),
             'gnoll': ('burrow', 'The Dug Den'), 'lizard': ('swamp', 'The Flooded Cellars of {n}')},
    'manor': {'human': ('dungeon', 'The Wine Cellar of {n}'), 'elf': ('cave', 'The Root Cellar of {n}'),
              'dwarf': ('crypt', 'The Clan Vault'), 'halfling': ('cave', 'The Deep Pantry'),
              'gnome': ('cave', 'The Root Workshop'), 'orc': ('den', 'The Store Pit'),
              'goblin': ('warren', "The Smugglers' Tunnel"), 'kobold': ('den', 'The Deep Hoard'),
              'gnoll': ('burrow', 'The Den below'), 'lizard': ('swamp', 'The Mud Cellar')},
}
BUILT = {'human', 'dwarf'}                  # stone halls below; the rest dig, or the water did
GARRISON = {'human': ('A soldier', '#c8c4b4'), 'elf': ('An elven warden', '#d0e8c8'), 'dwarf': ('A dwarf guard', '#d8b890'),
            'halfling': ('A hedge-warden', '#c8d090'), 'gnome': ('A gnome watcher', '#e0cc80')}
CAPTAIN = {'human': 'Castellan {n}', 'elf': 'Captain {n} of the Thorns', 'dwarf': 'Gatewarden {n}',
           'halfling': 'Bellwarden {n}', 'gnome': 'Watchmaster {n}'}
HEAD = {'human': 'Abbot {n}', 'elf': '{n}, Keeper of the Stars', 'dwarf': 'Runemaster {n}', 'halfling': 'Mother {n}',
        'gnome': '{n} the Lamplighter'}


def title(site):
    return KIND_NAME[site.kind][PL.people_of(site)]


# ------------------------------------------------------------------ on the world map
def setup(game, world, site):
    """What lies above and below: an abbey's or manor's upper floor, the cellars or dungeon below; who holds a fort."""
    from .world import Dungeon
    pe = PL.people_of(site)
    danger = world.region_at(site.x, site.y).danger
    base = max(1, danger * 2 - 1)
    if site.kind == 'fort' and not hasattr(site, 'state'):
        r = random.random()
        site.state = 'whole' if pe in PL.HOSTILE or r < .6 else 'taken' if r < .75 else 'abandoned' if r < .88 else 'ruin'
    site.state = getattr(site, 'state', 'whole')
    if site.state == 'taken':
        site.holder = 'bandits'
    if site.kind == 'manor':
        site.owner = random.choice(OWNER[pe]).format(n=PL.a_name(pe))
    if site.kind in ('monastery', 'manor') and (pe in ('human', 'elf', 'gnome') or site.kind == 'monastery' and pe == 'halfling'):
        did = f'hu{site.id}'
        dg = Dungeon(did, site.name, 1, base, 'upper', 'tower', None, None, site.x, site.y, True)
        dg.site, dg.rise, dg.upper = site.id, True, True
        world.dungeons[did] = dg
        site.floors = did
    tag, name = BELOW[site.kind][pe]
    n = {'monastery': random.randint(1, 2), 'fort': random.randint(3, 5), 'manor': 1}[site.kind]
    did = f'hb{site.id}'
    dg = Dungeon(did, name.format(n=PL.the(site.name)), n, base, 'rooms', tag, None,
                 D.hexrgb(PL.WALLS.get(tag, '#7e869c')), site.x, site.y, False)
    dg.site, dg.size = site.id, 'small' if site.kind == 'manor' else 'middle'
    rough = pe not in BUILT
    dg.styles = ['rooms'] * n if not rough else ['cave'] * n
    world.dungeons[did] = dg
    site.below = did


def describe(game, site):
    pe = PL.people_of(site)
    st = getattr(site, 'state', 'whole')
    if site.kind == 'monastery':
        return (f'A {title(site).lower()} of the {PL.PLURAL[pe]}: a place apart where their devout live, learn and keep '
                'lore.' + (' Monks, a herb garden, a warm meal for travellers.' if pe == 'human' else ''))
    if site.kind == 'fort':
        if st == 'taken':
            return f'A {title(site).lower()} of the {PL.PLURAL[pe]}, held by bandits now.'
        if st == 'abandoned':
            return f'A {title(site).lower()} of the {PL.PLURAL[pe]}. Nobody holds it any more.'
        if st == 'ruin':
            return f'The broken walls of a {title(site).lower()} of the {PL.PLURAL[pe]}.'
        return f'A {title(site).lower()} of the {PL.PLURAL[pe]}, built to hold this ground.'
    return f'The {title(site).lower()} of {getattr(site, "owner", "someone who matters")}.'


def on_enter(game, site, m):
    t = PL.tier(game, site)
    pe = PL.people_of(site)
    st = getattr(site, 'state', 'whole')
    if st == 'taken':
        game.msg(f'Bandits hold {PL.the(site.name)} now. Someone shouts on the wall.', 'bad')
    elif st == 'abandoned':
        game.msg('Nobody holds this place any more. The gate stands open, and the wind goes through it.', 'info')
    elif st == 'ruin':
        game.msg('Only broken walls are left standing.', 'info')
    elif t < 0:
        game.msg(f'This is a place of the {PL.PLURAL[pe]}, and they do not suffer strangers in it.', 'bad')
    elif t == 0:
        game.msg(f'Your name is not good with the {PL.PLURAL[pe]}. You will not get far in.', 'bad')


# ------------------------------------------------------------------ the map
def site_map(game, site):
    pe = PL.people_of(site)
    W, H = SIZE[site.kind]
    m = PL.land(game, site, W, H)
    cx, cy = m.centre
    mx, my = (40, 24) if W == 100 else (32, 20)
    cx = max(mx, min(W - mx + 6, cx))
    cy = max(my, min(H - my, cy))
    m.centre = (cx, cy)
    m.things, m.says, m.bar = {}, {}, {}
    m.hall = site.kind
    friendly = PL.tier(game, site) >= 0 and getattr(site, 'state', 'whole') == 'whole'
    door = PLANS[site.kind][pe](game, site, m, cx, cy, friendly)
    st = getattr(site, 'state', 'whole')
    if st in ('abandoned', 'ruin'):
        empty(game, site, m, st)
    elif st == 'taken':
        held(game, site, m)
    TP.weather(m)
    if getattr(m, 'peeps', False):
        rim = [(x, y) for y in range(m.h) for x in range(m.w) if m.tile(x, y) == D.ROCK and
               any(m.inb(x + a, y + b) and D.TILES[m.tile(x + a, y + b)].walk for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))
               and cheb(x, y, *door) > 2]
        for x, y in rim[::9]:
            m.set(x, y, D.SLIT)
    PL.finish(m, door)
    m.made_tier = PL.tier(game, site)
    m.place = site.kind
    if st != 'whole':
        m.bar = {}
    return m


# ------------------------------------------------------------------ building blocks
def fill(m, x0, y0, x1, y1, t):
    for y in range(max(0, y0), min(m.h, y1 + 1)):
        for x in range(max(0, x0), min(m.w, x1 + 1)):
            m.set(x, y, t)


def wood(m, cx, cy, rx, ry, p):
    """Old wood round a place, thinning out towards its edge."""
    for y in range(max(0, cy - ry), min(m.h, cy + ry + 1)):
        for x in range(max(0, cx - rx), min(m.w, cx + rx + 1)):
            r = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            if m.tile(x, y) != D.WATER and random.random() < p * min(1, 2.2 * (1 - r)):
                m.set(x, y, D.TREE)


def rock(m, x0, y0, x1, y1):
    TP.rock(m, max(0, x0), max(0, y0), min(m.w - 1, x1), min(m.h - 1, y1))


def tell(m, x, y, action, text=None, tile=None):
    """A telling thing at (x, y): bump it (or step on it) for `action` (themes.ACTIONS)."""
    if tile is not None:
        m.set(x, y, tile)
    m.things[(x, y)] = (action, f'h{x},{y}')
    if text:
        m.says[(x, y)] = text


def say(m, x, y, text, tile=None):
    tell(m, x, y, 'h_say', text, tile)


def ring(m, cells, t):
    for x, y in TP.ring_of(cells):
        m.set(x, y, t)


def head(game, site, m, x, y, role='healer'):
    pe = PL.people_of(site)
    return TP.npc(game, m, HEAD.get(pe, 'Brother {n}').format(n=PL.a_name(pe)), role, '#f4f0e6', x, y)


def garrison(game, site, m, cells, n, cap_at=None):
    """The fort's own people, or its foes' (hostile peoples, and a fort taken by others)."""
    pe = PL.people_of(site)
    if pe in PL.HOSTILE:
        return TP.foes(game, site, m, cells, n, chief_at=cap_at)
    if getattr(site, 'state', 'whole') != 'whole':
        return []
    who, fg = GARRISON[pe]
    if cap_at:
        TP.npc(game, m, CAPTAIN[pe].format(n=PL.a_name(pe)), 'guard', '#e8e0c0', cap_at[0], cap_at[1])
    cs = [c for c in cells if D.TILES[m.tile(*c)].walk and not m.mon_at(*c)]
    random.shuffle(cs)
    for c in cs[:n]:
        TP.npc(game, m, who, 'guard', fg, c[0], c[1], stay=False)
    return cs


def tower_at(game, site, m, cx, cy, style, storeys, toward, mark=None):
    """A tower set into a fort, drawn here; its floors follow the tower rules. Returns its door."""
    from . import towers as TOW
    if getattr(site, 'state', 'whole') == 'ruin':
        storeys = 0
    if not getattr(site, 'tw', None) or (site.tw['cx'], site.tw['cy']) != (cx, cy):
        site.tw = TOW.plan(site, cx, cy, style, max(2, storeys), seed=site.id * 41 + 5)
        site.tw['folk'] = PL.people_of(site)
        if mark:
            site.tw['mark'] = mark
    tw = site.tw
    cells = TOW.footprint(tw)
    rim = TOW.rim_of(cells)
    st = TOW.STYLE[style]
    for x, y in cells:
        m.set(x, y, st['wall'] if (x, y) in rim else st['floor'])
    inner = cells - rim
    door = min((c for c in rim if any((c[0] + a, c[1] + b) in inner for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))),
               key=lambda c: cheb(c[0], c[1], *toward))
    m.set(*door, DOOR)
    if storeys:
        up = tw['stairs'][0]
        if cheb(up[0], up[1], *door) <= 1 and len(tw['stairs']) > 1:
            tw['stairs'].reverse()
            up = tw['stairs'][0]
        m.set(*up, UP)
        m.bar[up] = 2
    return door


def upper(site, m, stair, line, wall=WALL, floor=FLOOR, boxes=(), ovals=(), doors=(), bridges=(), put=(), tells=(),
          folk=None):
    """The floor above, kept on the site and drawn by upper_map; its stair up on this map."""
    if not getattr(site, 'floors', None):
        return
    m.set(*stair, UP)
    m.bar[stair] = 2
    site.up = dict(stair=stair, line=line, wall=wall, floor=floor, boxes=list(boxes), ovals=list(ovals), doors=list(doors),
                   bridges=list(bridges), put=list(put), tells=list(tells), folk=folk)


def down(m, x, y, need=2):
    m.set(x, y, DOWN)
    m.bar[(x, y)] = need


# ------------------------------------------------------------------ the floor above
def upper_map(game, dg, depth):
    """The floor over an abbey or a manor: its rooms over the air, the land faded below."""
    site = game.world.sites[dg.site]
    gm = game.maps[site.map_key]
    up = getattr(site, 'up', None) or dict(stair=gm.entry, line='', wall=WALL, floor=FLOOR, boxes=[], ovals=[], doors=[],
                                           bridges=[], put=[], tells=[], folk=None)
    m = GameMap(f'{dg.id}:{depth}', 'dungeon', site.name, gm.w, gm.h, AIR)
    m.did, m.depth, m.level, m.wall_fg = dg.id, depth, dg.base + depth, getattr(gm, 'wall_fg', None)
    m.radius, m.sky, m.built = 30, site.id, True
    m.below = site.map_key
    m.lights, m.deco, m.mons, m.items = [], bytearray(m.w * m.h), [], []
    m.ladders, m.dtag = False, 'tower'
    m.things, m.says = {}, {}
    m.mood_line, m.upper = up['line'], True
    cells = set()
    for x0, y0, x1, y1 in up['boxes']:
        TP.box(m, x0, y0, x1, y1, up['wall'], up['floor'])
        cells |= {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}
    for cx, cy, rx, ry in up['ovals']:
        TP.rounded(m, cx, cy, rx, ry, up['wall'], up['floor'])
        cells |= set(TP.oval(cx, cy, rx, ry))
    for a, b in up['bridges']:
        from .tribes import line
        for x, y in line(a, b):
            m.set(x, y, D.BRIDGE if m.tile(x, y) == AIR else up['floor'])
    for c in up['doors']:
        m.set(c[0], c[1], DOOR)
    for x, y in cells:                                  # windows: a look out, now and then
        if m.tile(x, y) == up['wall'] and (x * 5 + y * 11) % 7 == 0 and \
                sum(1 for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)) if m.tile(x + a, y + b) == AIR) == 1 and \
                sum(1 for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)) if m.tile(x + a, y + b) == up['wall']) == 2:
            m.set(x, y, D.SLIT)
    for x, y, t in up['put']:
        m.set(x, y, t)
    for x, y, action, text in up['tells']:
        tell(m, x, y, action, text)
    m.set(up['stair'][0], up['stair'][1], DOWN)
    xs = [x for x, _ in cells] or [m.w // 2]
    ys = [y for _, y in cells] or [m.h // 2]
    m.sky_centre = ((min(xs) + max(xs)) // 2, (min(ys) + max(ys)) // 2)
    for i, t in enumerate(m.t):
        if t == AIR:
            m.seen[i] = 1
    free = [c for c in cells if m.tile(*c) == up['floor'] and cheb(c[0], c[1], *up['stair']) > 2]
    if up['folk'] and PL.friendly(game, site):
        job, fg, n = up['folk']
        TP.folk(game, m, site, free, n, job, fg)
    elif PL.people_of(site) in PL.HOSTILE and not PL.friendly(game, site) and free:
        TP.foes(game, site, m, free, 2)
    return m


def on_level(game, m, dg):
    if getattr(m, 'mood_line', None):
        game.msg(m.mood_line, 'info')


# ------------------------------------------------------------------ taken, abandoned, fallen
def held(game, site, m):
    """Bandits in a fort that was someone else's: on the walls and in the yard, their chief in the best room."""
    from . import towers as TOW
    lvl = game.world.dungeons[site.below].base + 1
    free = [(x, y) for y in range(m.h) for x in range(m.w) if m.tile(x, y) in (FLOOR, PLANK, PATH)
            and not m.mon_at(x, y) and cheb(x, y, *m.centre) <= 24]
    random.shuffle(free)
    for k, c in enumerate(free[:6]):
        key = TOW.CHIEF['bandits'] if k == 0 else random.choice(TOW.FOES['bandits'])
        if key not in D.MONSTERS:
            key = 'bandit'
        m.mons.append(make_monster(game, key, c[0], c[1], lvl + (1 if k == 0 else 0), 1 if k == 0 else 0))


def empty(game, site, m, st):
    """Nobody holds it: the folk are gone, a beast or two has moved in; a ruin's walls are broken."""
    m.mons = []
    m.bar = {}
    walls = {WALL, D.PALISADE, D.HIDE, D.REEDS, D.THORNS, D.HEDGE, D.FENCE, D.EARTH}
    for i, t in enumerate(m.t):
        if t == DOOR:
            m.t[i] = D.ODOOR if st == 'abandoned' else FLOOR
        elif st == 'ruin' and t in walls:
            r = random.random()
            if r < .22:
                m.t[i] = D.RUBBLE
            elif r < .4:
                m.t[i] = m.ground
            elif r < .5 and t == WALL:
                m.t[i] = D.IVY
        elif st == 'ruin' and t in (D.BED, D.TABLE, D.SHELVES, D.BARREL, D.PEW, D.HIGHSEAT, D.RACK, D.FURS):
            m.t[i] = D.RUBBLE if random.random() < .5 else FLOOR
    m.things, m.says = {}, {}
    lvl = game.world.dungeons[site.below].base
    beasts = [k for k in ('wolf', 'boar', 'giant_spider', 'bear') if k in D.MONSTERS] or ['wolf']
    free = [(x, y) for y in range(m.h) for x in range(m.w) if m.tile(x, y) in (FLOOR, PLANK, m.ground)
            and cheb(x, y, *m.centre) <= 16 and not m.mon_at(x, y)]
    for c in random.sample(free, min(len(free), random.randint(1, 3))):
        m.mons.append(make_monster(game, random.choice(beasts), c[0], c[1], lvl))
    m.lights, m.glows = [], []


# ==================================================================== abbeys
def abbey_human(game, site, m, cx, cy, friendly):
    PL.clear(m, cx - 32, cy - 19, cx + 30, cy + 19)
    TP.box(m, cx - 30, cy - 18, cx + 28, cy + 18, WALL, m.ground)              # the precinct wall
    gate = (cx - 30, cy + 4)
    m.set(*gate, PATH)
    TP.box(m, cx - 14, cy - 16, cx + 20, cy - 8)                               # the church, north
    for x in range(cx - 11, cx + 14, 3):
        m.set(x, cy - 14, D.PILLAR)
        m.set(x, cy - 10, D.PILLAR)
    for x in range(cx - 10, cx + 12, 2):
        if (x - cx) % 3:
            for y in (cy - 13, cy - 11):
                m.set(x, y, D.PEW)
    altar = (cx + 18, cy - 12)
    m.set(*altar, D.ALTAR)
    m.set(cx + 19, cy - 14, D.STATUE)
    m.set(cx + 19, cy - 10, D.STATUE)
    TP.box(m, cx - 11, cy - 8, cx + 11, cy + 8)                                # the cloister round the garth
    fill(m, cx - 8, cy - 5, cx + 8, cy + 5, D.GRASS)
    for x in range(cx - 8, cx + 9, 2):
        for y in (cy - 5, cy + 5):
            m.set(x, y, D.PILLAR)
    for y in range(cy - 3, cy + 4, 2):
        for x in (cx - 8, cx + 8):
            m.set(x, y, D.PILLAR)
    m.set(cx, cy, D.WELL)
    for x, y in ((cx - 4, cy - 2), (cx + 4, cy + 2), (cx - 4, cy + 2), (cx + 4, cy - 2)):
        m.set(x, y, D.FIELD)
    m.set(cx, cy - 8, DOOR)
    TP.box(m, cx - 22, cy - 8, cx - 11, cy)                                    # the chapter house
    TP.box(m, cx - 22, cy, cx - 11, cy + 8)                                    # the parlour, with the way in
    for x in range(cx - 20, cx - 12, 2):
        m.set(x, cy - 6, D.PEW)
        m.set(x, cy - 2, D.PEW)
    m.set(cx - 17, cy - 4, D.TABLE)
    door = (cx - 22, cy + 4)
    m.set(*door, DOOR)
    m.set(cx - 11, cy + 4, DOOR)
    m.set(cx - 11, cy - 4, DOOR)
    TP.box(m, cx - 11, cy + 8, cx + 6, cy + 16)                               # the refectory and the kitchen
    TP.box(m, cx + 6, cy + 8, cx + 14, cy + 16)
    m.set(cx - 2, cy + 8, DOOR)
    m.set(cx + 6, cy + 12, DOOR)
    for x in range(cx - 8, cx + 4):
        m.set(x, cy + 12, D.TABLE)
    m.set(cx + 12, cy + 10, D.HEARTH)
    m.set(cx + 8, cy + 14, D.BARREL)
    m.set(cx + 9, cy + 14, D.BARREL)
    down(m, cx + 12, cy + 14)
    TP.box(m, cx + 11, cy - 8, cx + 22, cy + 8)                               # the infirmary
    m.set(cx + 11, cy, DOOR)
    for y in range(cy - 6, cy + 7, 2):
        m.set(cx + 20, y, D.BED)
    m.set(cx + 14, cy - 6, D.SHELVES)
    for y in range(cy - 15, cy - 8):                                          # the herb garden and the orchard
        for x in range(cx - 28, cx - 16):
            if (x + y) % 2 == 0:
                m.set(x, y, D.FIELD)
    for x in range(cx + 24, cx + 28, 2):
        for y in range(cy - 15, cy + 16, 3):
            m.set(x, y, D.TREE)
    for x in range(cx - 28, cx - 14, 3):
        m.set(x, cy + 13, D.GRAVE)
    upper(site, m, (cx - 20, cy - 6), 'The dormitory and the scriptorium. Pens scratch; somebody snores.',
          boxes=[(cx - 22, cy - 8, cx - 11, cy + 8), (cx - 22, cy + 8, cx + 22, cy + 12), (cx + 11, cy - 8, cx + 22, cy + 8)],
          doors=[(cx - 16, cy + 8), (cx + 16, cy + 8)],
          put=[(cx - 13, y, D.BED) for y in range(cy - 6, cy + 7, 2)] + [(cx + 14, y, D.TABLE) for y in range(cy - 5, cy + 6, 3)]
          + [(cx + 21, y, D.SHELVES) for y in range(cy - 6, cy + 7, 2)],
          tells=[(cx + 21, y, 'h_lore', None) for y in range(cy - 6, cy + 7, 2)],
          folk=('scribe', '#b0a080', 2))
    if friendly:
        head(game, site, m, cx + 16, cy - 12)
        TP.npc(game, m, f'Brother {PL.a_name("human")} the Herbalist', 'herbalist', '#90d070', cx - 22, cy - 12)
        TP.npc(game, m, f'Brother {PL.a_name("human")} the Cellarer', 'inn', '#e0a060', cx + 9, cy + 11)
        TP.folk(game, m, site, [(x, y) for x in range(cx - 10, cx + 11) for y in (cy - 7, cy + 7)], 4, 'monk', '#b0a080')
    m.bar[gate] = 1
    m.signs.append((cx - 8, cy - 17, 'ABBEY'))
    PL.lit(m, [(cx + 17, cy - 12), (cx + 12, cy + 11), (cx - 17, cy - 3)])
    m.altar = altar
    return gate


def abbey_elf(game, site, m, cx, cy, friendly):
    wood(m, cx, cy, 44, 26, .9)
    for x, y in TP.oval(cx, cy, 25, 15):
        if m.inb(x, y):
            m.set(x, y, D.GRASS)
    PL.trail(m, (cx - 44, cy), (cx - 24, cy), D.WHITE)
    trunks = []
    for k in range(8):                                                        # the ring of great trees
        a = k / 8 * math.tau + .2
        tx, ty = round(cx + math.cos(a) * 19), round(cy + math.sin(a) * 11)
        trunks.append((tx, ty))
        fill(m, tx - 1, ty - 1, tx + 1, ty + 1, D.TRUNK)
    for x, y in TP.oval(cx, cy, 7, 4):                                        # the star garden of white stone
        m.set(x, y, D.WHITE if (x + y) % 3 else D.FIELD)
    for k in range(7):
        a = k / 7 * math.tau
        m.set(round(cx + math.cos(a) * 6), round(cy + math.sin(a) * 3.5), D.STONE)
    px, py = cx - 1, cy
    for x, y in TP.oval(px, py, 2, 1):                                        # the still pool
        tell(m, x, y, 'h_pool', tile=D.WATER)
    # the archive: a hollow trunk full of song-scrolls, and the way down through its roots
    ax, ay = cx + 13, cy + 7
    TP.rounded(m, ax, ay, 4, 3, D.TRUNK, PLANK)
    m.set(ax - 4, ay, D.ODOOR)
    for x in (ax - 1, ax + 1, ax + 2):
        tell(m, x, ay - 2, 'h_lore', tile=D.SHELVES)
    down(m, ax + 2, ay + 1)
    # the sleeping halls in the crowns: up through another hollow trunk
    hx, hy = cx - 13, cy - 7
    TP.rounded(m, hx, hy, 3, 2, D.TRUNK, PLANK)
    m.set(hx, hy + 2, D.ODOOR)
    upper(site, m, (hx + 1, hy), 'The sleeping halls in the crowns. Leaves whisper all round you.', wall=D.HEDGE,
          floor=PLANK, ovals=[(hx, hy, 6, 4), (cx + 2, cy - 9, 7, 4), (cx + 14, cy - 4, 5, 3)],
          bridges=[((hx + 6, hy), (cx - 5, cy - 9)), ((cx + 9, cy - 8), (cx + 10, cy - 5))],
          put=[(hx - 3, hy - 1, D.BED), (hx - 3, hy + 1, D.BED), (cx, cy - 11, D.BED), (cx + 4, cy - 11, D.BED),
               (cx + 2, cy - 7, D.BED), (cx + 17, cy - 4, D.BED)],
          folk=('sleeper', '#e0e8d0', 2))
    if friendly:
        head(game, site, m, cx + 2, cy + 2)
        TP.npc(game, m, f'{PL.a_name("elf")} the Herb-Warden', 'herbalist', '#90d080', cx - 6, cy + 6)
        TP.folk(game, m, site, TP.oval(cx, cy, 14, 8), 3, 'singer', '#e0e8d0')
    m.bar[(ax - 4, ay)] = 1
    m.wall_fg = (222, 234, 216)
    m.glows = [(x, y, (190, 230, 255), 3) for x, y in ((cx, cy), (ax, ay), trunks[2], trunks[6])]
    m.lights = list(m.glows)
    return (cx - 24, cy)


def abbey_dwarf(game, site, m, cx, cy, friendly):
    rock(m, cx - 24, cy - 22, cx + 38, cy + 22)
    PL.clear(m, cx - 36, cy - 6, cx - 23, cy + 6)
    TP.box(m, cx - 22, cy - 7, cx + 12, cy + 7)                               # the hall of rune stones
    door = (cx - 22, cy)
    m.set(*door, DOOR)
    for x in range(cx - 18, cx + 10, 4):
        for y in (cy - 4, cy + 4):
            tell(m, x, y, 'h_lore', tile=D.STONE)
    for x in range(cx - 16, cx + 10, 4):
        m.set(x, cy - 1, D.PILLAR)
        m.set(x, cy + 1, D.PILLAR)
    TP.box(m, cx + 12, cy - 6, cx + 24, cy + 6)                               # the forge chapel
    m.set(cx + 12, cy, DOOR)
    altar = (cx + 22, cy)
    m.set(*altar, D.ALTAR)
    m.set(cx + 20, cy - 3, D.ANVIL)
    m.set(cx + 20, cy + 3, D.FIREPIT)
    TP.box(m, cx - 14, cy - 17, cx + 4, cy - 7)                               # the brewery
    m.set(cx - 5, cy - 7, DOOR)
    for x in range(cx - 12, cx + 3, 2):
        m.set(x, cy - 15, D.BARREL)
    m.set(cx - 12, cy - 10, D.HEARTH)
    for k in range(5):                                                        # the brothers' cells
        x0 = cx - 18 + k * 6
        TP.box(m, x0, cy + 7, x0 + 6, cy + 12)
        m.set(x0 + 3, cy + 7, DOOR)
        m.set(x0 + 2, cy + 10, D.BED)
    TP.box(m, cx + 24, cy - 4, cx + 34, cy + 4)                               # the store hall, and the stair down
    m.set(cx + 24, cy, DOOR)
    for y in (cy - 2, cy + 2):
        m.set(cx + 27, y, D.BARREL)
        m.set(cx + 29, y, D.BARREL)
    down(m, cx + 32, cy)
    m.wall_fg = (176, 150, 120)
    if friendly:
        head(game, site, m, cx + 18, cy)
        TP.folk(game, m, site, [(x, y) for x in range(cx - 18, cx + 10) for y in (cy - 2, cy + 2)], 3, 'runecarver', '#d8b890')
    m.bar[door] = 1
    PL.lit(m, [(cx + 20, cy + 2), (cx - 21, cy + 1), (cx - 11, cy - 10)])
    m.altar = altar
    return (cx - 36, cy)


def abbey_halfling(game, site, m, cx, cy, friendly):
    PL.clear(m, cx - 28, cy - 18, cx + 28, cy + 18)
    hedge = TP.oval(cx, cy, 25, 16)
    ring(m, hedge, D.HEDGE)
    gate = (cx - 25, cy)
    m.set(*gate, PATH)
    TP.rounded(m, cx, cy, 11, 6, WALL, PLANK)                                 # the round hall with the long table
    m.round_doors = True
    m.set(cx - 11, cy, DOOR)
    for x in range(cx - 7, cx + 8):
        tell(m, x, cy, 'h_meal', tile=D.TABLE)
    m.set(cx + 9, cy - 2, D.HEARTH)
    for x in range(cx - 7, cx + 8, 2):
        m.set(x, cy - 1, D.PEW)
        m.set(x, cy + 1, D.PEW)
    down(m, cx + 8, cy + 3)
    TP.rounded(m, cx - 11, cy - 10, 4, 3, WALL, PLANK)                       # the bakery
    m.set(cx - 11, cy - 7, DOOR)
    m.set(cx - 12, cy - 11, D.HEARTH)
    TP.rounded(m, cx + 11, cy - 10, 4, 3, WALL, PLANK)                       # the brewhouse
    m.set(cx + 11, cy - 7, DOOR)
    for x in (cx + 9, cx + 11, cx + 13):
        m.set(x, cy - 11, D.BARREL)
    for y in range(cy + 8, cy + 14):                                          # vegetable gardens
        for x in range(cx - 18, cx - 2):
            if y % 2 == 0 and ((x - cx) / 25.5) ** 2 + ((y - cy) / 16.5) ** 2 < .85:
                m.set(x, y, D.FIELD)
    for x in range(cx + 4, cx + 20, 3):                                       # the orchard and the beehives
        for y in range(cy + 8, cy + 14, 3):
            if ((x - cx) / 25.5) ** 2 + ((y - cy) / 16.5) ** 2 < .85:
                m.set(x, y, D.TREE)
    for x in (cx + 16, cx + 18, cx + 20):
        say(m, x, cy - 3, 'A beehive, humming. The bees are busy and do not care about you.', D.HIVE)
    upper(site, m, (cx - 8, cy - 3), 'The loft under the thatch: beds in rows, and jars hung from every beam.',
          floor=PLANK, ovals=[(cx, cy, 11, 6)], put=[(x, cy - 2, D.BED) for x in range(cx - 6, cx + 7, 3)] +
          [(x, cy + 2, D.BED) for x in range(cx - 6, cx + 7, 3)], folk=('sleeper', '#c8d090', 1))
    if friendly:
        head(game, site, m, cx + 6, cy - 3)
        TP.npc(game, m, f'{PL.a_name("halfling")} the Herb-Grower', 'herbalist', '#90d070', cx - 10, cy + 10)
        TP.folk(game, m, site, [(x, y) for x in range(cx - 18, cx - 4) for y in range(cy + 8, cy + 13)], 2, 'gardener',
                '#c8d090')
    m.bar[gate] = 1
    PL.lit(m, [(cx + 8, cy - 2), (cx - 12, cy - 10)])
    return gate


def abbey_gnome(game, site, m, cx, cy, friendly):
    wood(m, cx, cy, 36, 24, .7)
    rock(m, cx - 24, cy - 18, cx + 28, cy + 18)
    PL.clear(m, cx - 34, cy - 1, cx - 23, cy + 1)
    for x, y in TP.oval(cx, cy - 15, 18, 2):
        if m.inb(x, y) and m.tile(x, y) == D.ROCK and random.random() < .45:
            m.set(x, y, D.ROOT)
    rooms = {'dome': (cx, cy, 8, 5), 'library': (cx - 15, cy - 7, 5, 3), 'alchemy': (cx + 15, cy - 7, 5, 3),
             'nooks': (cx - 15, cy + 8, 5, 3), 'work': (cx + 16, cy + 8, 5, 3), 'hall': (cx - 16, cy, 4, 2)}
    for rx_, ry_, a, b in rooms.values():
        TP.rounded(m, rx_, ry_, a, b, D.EARTH, FLOOR)
    from .tribes import line
    for a, b in (('hall', 'dome'), ('dome', 'library'), ('dome', 'alchemy'), ('dome', 'nooks'), ('dome', 'work')):
        for x, y in line(rooms[a][:2], rooms[b][:2]):
            if m.tile(x, y) in (D.EARTH, D.ROCK, D.ROOT):
                m.set(x, y, FLOOR)
    door = (cx - 23, cy)
    for x in range(cx - 23, cx - 19):
        m.set(x, cy, FLOOR)
    m.set(*door, DOOR)
    tell(m, cx, cy, 'h_lens', tile=D.LENS)                                    # the star dome and its lens
    for k in range(8):
        a = k / 8 * math.tau
        m.set(round(cx + math.cos(a) * 6), round(cy + math.sin(a) * 3.5), D.CRYSTAL)
    lx, ly = rooms['library'][:2]
    for x in (lx - 3, lx - 1, lx + 1, lx + 3):
        tell(m, x, ly - 2, 'h_lore', tile=D.SHELVES)
    ax_, ay_ = rooms['alchemy'][:2]
    m.set(ax_ + 2, ay_ - 1, D.ALCHEMY)
    m.set(ax_ - 2, ay_ - 1, D.SHELVES)
    nx, ny = rooms['nooks'][:2]
    for x in (nx - 3, nx, nx + 3):
        m.set(x, ny + 1, D.BED)
    wx, wy = rooms['work'][:2]
    m.set(wx + 2, wy, D.GEARS)
    m.set(wx - 2, wy + 1, D.BENCH)
    down(m, wx + 3, wy + 1)
    if friendly:
        head(game, site, m, cx + 3, cy + 2)
        TP.npc(game, m, f'{PL.a_name("gnome")} the Potion-Maker', 'herbalist', '#90d070', ax_, ay_)
        TP.folk(game, m, site, TP.oval(cx, cy, 6, 3), 2, 'stargazer', '#e0cc80')
    m.bar[door] = 1
    m.glows = [(cx, cy, (120, 230, 255), 6), (lx, ly, (120, 230, 255), 3), (wx, wy, (255, 190, 110), 3)]
    m.lights = list(m.glows)
    return (cx - 34, cy)


def abbey_orc(game, site, m, cx, cy, friendly):
    from .tribes import round_hut
    PL.clear(m, cx - 30, cy - 19, cx + 30, cy + 19)
    ring(m, TP.oval(cx, cy, 27, 16), D.PALISADE)
    gate = (cx - 27, cy)
    m.set(*gate, PATH)
    m.set(cx, cy, D.SPIRITTOTEM)                                              # the spirit pole in the ring of trial stones
    for k in range(9):
        a = k / 9 * math.tau
        m.set(round(cx + math.cos(a) * 6), round(cy + math.sin(a) * 4), D.STONE)
    for x, y in ((cx - 3, cy - 7), (cx + 3, cy - 7), (cx, cy + 7)):
        m.set(x, y, D.DRUM)
    round_hut(m, cx - 14, cy - 9, 4, 3, D.HIDE, FLOOR)                       # the sweat lodge
    m.set(cx - 14, cy - 6, DOOR)
    say(m, cx - 14, cy - 9, 'Hot stones in a pit. Pour water on them and the lodge fills with steam: here the young '
        'sweat out their fear before the trials.', D.FIREPIT)
    round_hut(m, cx + 14, cy - 9, 6, 3, D.HIDE, FLOOR)                       # the young warriors' hut
    m.set(cx + 14, cy - 6, DOOR)
    for x in range(cx + 10, cx + 19, 2):
        m.set(x, cy - 10, D.FURS)
    shaman = round_hut(m, cx - 13, cy + 9, 4, 3, D.HIDE, FLOOR)              # the shaman's hut, the spirit cave below
    m.set(cx - 13, cy + 6, DOOR)
    m.set(cx - 14, cy + 10, D.ALTAR)
    down(m, cx - 11, cy + 10)
    for x in range(cx + 9, cx + 20, 3):
        m.set(x, cy + 10, D.RACK)
    TP.foes(game, site, m, [(x, y) for x, y in TP.oval(cx, cy, 14, 9) if cheb(x, y, cx, cy) > 6], 6,
            chief_at=(cx - 12, cy + 9) if shaman else None)
    PL.lit(m, [(cx - 14, cy - 8), (cx, cy + 1)])
    return gate


def abbey_goblin(game, site, m, cx, cy, friendly):
    cells, mouth, far = TP.nook(game, site, m, cx, cy, friendly, [D.SHELVES, D.SHELVES, D.MIDDEN, D.SHELVES, D.SHELVES],
                                D.IDOL)
    near = sorted((c for c in cells if m.tile(*c) == FLOOR), key=lambda c: cheb(c[0], c[1], *far))
    mid = [c for c in cells if m.tile(*c) == FLOOR and 4 <= cheb(c[0], c[1], *far) <= 9]
    if mid:
        tell(m, *random.choice(mid), 'h_dungeonmap', tile=D.MAPTABLE)
    pit = [c for c in cells if m.tile(*c) == FLOOR and c[0] < cx and cheb(c[0], c[1], *mouth) > 6]
    if pit:
        say(m, *random.choice(pit), 'The ink pit: soot, oil and something worse, stirred black. Quills stand in it.',
            D.DARKWATER)
    for c in near[2:9:2]:
        if m.tile(*c) == FLOOR:
            m.set(c[0], c[1], D.SHELVES)
    TP.foes(game, site, m, list(cells), 5, chief_at=(far[0] - 1, far[1]))
    PL.lit(m, [(far[0] - 1, far[1] + 1)])
    return mouth


def abbey_kobold(game, site, m, cx, cy, friendly):
    rock(m, cx - 22, cy - 18, cx + 30, cy + 18)
    PL.clear(m, cx - 34, cy - 1, cx - 21, cy + 1)
    for x in range(cx - 21, cx - 12):
        m.set(x, cy, FLOOR)
    TP.box(m, cx - 13, cy - 5, cx + 5, cy + 5)                                # the mirror hall
    for x in range(cx - 11, cx + 4, 2):
        tell(m, x, cy - 5, 'h_mirror', tile=D.MIRROR)
        tell(m, x, cy + 5, 'h_mirror', tile=D.MIRROR)
    m.set(cx - 13, cy, DOOR)
    TP.box(m, cx + 5, cy - 9, cx + 22, cy + 9)                               # the sorting hall
    m.set(cx + 5, cy, DOOR)
    for y in range(cy - 6, cy + 7, 3):
        m.set(cx + 10, y, D.TABLE)
        m.set(cx + 14, y, D.GLITTER)
    m.set(cx + 18, cy - 6, D.ANVIL)
    m.set(cx + 18, cy + 6, D.BENCH)
    down(m, cx + 20, cy)
    TP.foes(game, site, m, [(x, y) for x in range(cx - 12, cx + 21) for y in range(cy - 8, cy + 9)], 6,
            chief_at=(cx + 19, cy - 2))
    m.glows = [(cx - 4, cy, (255, 210, 120), 5), (cx + 14, cy, (255, 210, 120), 4)]
    m.lights = list(m.glows)
    return (cx - 34, cy)


def abbey_gnoll(game, site, m, cx, cy, friendly):
    from .tribes import round_hut
    PL.clear(m, cx - 28, cy - 18, cx + 28, cy + 18)
    ring(m, TP.oval(cx, cy, 25, 15), D.THORNS)
    gate = (cx - 25, cy)
    m.set(*gate, PATH)
    fill(m, cx - 2, cy - 2, cx + 2, cy + 1, D.BAREROCK)                     # the howl rock and its moon stone
    m.set(cx - 2, cy - 2, D.STONE)
    m.set(cx + 2, cy - 2, D.STONE)
    say(m, cx, cy - 1, 'The moon stone: pale, cold, pitted like the moon itself. The bone-callers howl to it.', D.CRYSTAL)
    round_hut(m, cx - 14, cy - 8, 4, 3, D.HIDE, FLOOR)                       # the bone-caller's hut
    m.set(cx - 14, cy - 5, DOOR)
    m.set(cx - 15, cy - 9, D.FURS)
    down(m, cx - 12, cy - 8)
    for x in range(cx + 8, cx + 18, 3):                                      # hide racks
        m.set(x, cy - 9, D.FRAME)
    for x, y in TP.oval(cx + 13, cy + 8, 3, 2):                              # the bone heap and the carrion pit
        m.set(x, y, D.BONES if x < cx + 13 else D.BLOODPIT)
    TP.foes(game, site, m, [(x, y) for x, y in TP.oval(cx, cy, 15, 9) if cheb(x, y, cx, cy) > 4], 5,
            chief_at=(cx - 13, cy - 7))
    TP.beasts(game, site, m, [(x, y) for x, y in TP.oval(cx, cy, 20, 12) if cheb(x, y, cx, cy) > 14], 2)
    PL.lit(m, [(cx, cy + 2)])
    return gate


def abbey_lizard(game, site, m, cx, cy, friendly):
    from .tribes import round_hut
    swamp(m, cx, cy, 30, 20)
    fill(m, cx - 3, cy - 2, cx + 3, cy + 2, D.SWAMP)                        # the sacred eggs in the warm mud
    for x, y in ((cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)):
        say(m, x, y, 'The sacred eggs, warm in the mud. A priest would kill you for touching one.', D.EGGS)
    huts = [(cx - 12, cy - 9), (cx + 12, cy - 9), (cx - 12, cy + 9), (cx + 12, cy + 9), (cx + 20, cy)]
    for hx, hy in huts:                                                       # reed huts on stilts
        round_hut(m, hx, hy, 3, 2, D.REEDS, PLANK)
    from .tribes import line
    for a in [(cx - 30, cy)] + huts:
        for x, y in line(a, (cx, cy)):
            if m.tile(x, y) in (D.SHALLOW, D.WATER, D.SWAMP, D.GRASS) and cheb(x, y, cx, cy) > 3:
                m.set(x, y, PLANK)
    for hx, hy in huts:
        for dx in (-3, 3):
            if m.tile(hx + dx, hy) == D.REEDS:
                m.set(hx + dx, hy, DOOR)
    say(m, cx + 21, cy - 1, 'The sun stone: a flat stone, warm as a hearth. The priests lie on it at noon and dream.', D.STONE)
    down(m, cx - 12, cy + 10)
    m.set(cx - 13, cy + 9, D.ALTAR)
    TP.foes(game, site, m, [(x, y) for y in range(cy - 12, cy + 13) for x in range(cx - 22, cx + 23)
                            if m.tile(x, y) == PLANK], 5, chief_at=(cx - 11, cy + 9))
    TP.beasts(game, site, m, [(x, y) for y in range(cy - 16, cy + 17) for x in range(cx - 26, cx + 27)
                              if m.tile(x, y) == D.SHALLOW and cheb(x, y, cx, cy) > 8], 2)
    PL.lit(m, [(cx, cy + 3)])
    return (cx - 30, cy)


def swamp(m, cx, cy, rx, ry, deep=False):
    for y in range(max(0, cy - ry - 2), min(m.h, cy + ry + 3)):
        for x in range(max(0, cx - rx - 4), min(m.w, cx + rx + 4)):
            r = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            if r < 1:
                m.set(x, y, D.WATER if deep and r < .8 else D.SHALLOW if random.random() < .55 else D.SWAMP)


# ==================================================================== forts
def fort_human(game, site, m, cx, cy, friendly):
    x0, y0, x1, y1 = cx - 22, cy - 14, cx + 20, cy + 14
    PL.clear(m, x0 - 6, y0 - 4, x1 + 4, y1 + 4)
    TP.box(m, x0 - 3, y0 - 3, x1 + 3, y1 + 3, D.WATER, m.ground)             # the moat
    TP.box(m, x0 - 2, y0 - 2, x1 + 2, y1 + 2, m.ground, m.ground)
    TP.box(m, x0, y0, x1, y1)                                                 # the curtain wall
    for x in range(x0 - 3, x0 + 1):                                          # the drawbridge
        m.set(x, cy, D.BRIDGE)
    TP.box(m, x0, cy - 3, x0 + 5, cy + 3)                                    # the gatehouse
    for x in range(x0, x0 + 6):
        m.set(x, cy, FLOOR)
    m.portcullis = [(x0 + 1, cy)]
    m.set(x0, cy, DOOR)
    m.set(x0 + 5, cy, FLOOR)
    for x, y in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):                    # the corner towers
        if (x, y) != (x1, y0):
            TP.box(m, x - 3, y - 3, x + 3, y + 3)
            m.set(x + (1 if x == x0 else -1), y + (3 if y == y0 else -3), DOOR)
    tdoor = tower_at(game, site, m, x1, y0, 'corner', random.randint(2, 3), (x1 - 5, y0 + 5))
    m.set(*tdoor, DOOR)
    m.set(cx - 6, cy - 4, D.WELL)                                            # the yard
    TP.box(m, x0 + 4, y0, x0 + 16, y0 + 8)                                   # the barracks
    m.set(x0 + 10, y0 + 8, DOOR)
    for x in range(x0 + 6, x0 + 15, 2):
        m.set(x, y0 + 2, D.BED)
    TP.box(m, x0 + 4, y1 - 8, x0 + 16, y1)                                   # the stable
    m.set(x0 + 10, y1 - 8, DOOR)
    for x in range(x0 + 7, x0 + 15, 3):
        for y in range(y1 - 6, y1 - 1):
            m.set(x, y, D.FENCE)
    TP.box(m, x0 + 16, y1 - 8, x0 + 24, y1)                                  # the armoury
    m.set(x0 + 20, y1 - 8, DOOR)
    for x in range(x0 + 18, x0 + 23, 2):
        say(m, x, y1 - 2, 'Racks of spears and crossbows, oiled and counted. The armourer knows every one.', D.RACK)
    TP.box(m, x1 - 14, cy - 7, x1, cy + 7)                                   # the lord's keep
    m.set(x1 - 14, cy, DOOR)
    m.set(x1 - 3, cy, D.HIGHSEAT)
    for x in range(x1 - 11, x1 - 4, 2):
        m.set(x, cy - 3, D.TABLE)
    m.set(x1 - 12, cy + 5, D.SHELVES)
    down(m, x1 - 2, cy + 5)
    postern = (x1, cy + 10)                                                  # the postern, out over the moat
    m.set(*postern, DOOR)
    for x in range(x1 + 1, x1 + 4):
        m.set(x, cy + 10, D.SHALLOW if x == x1 + 3 else m.ground)
    garrison(game, site, m, [(x, y) for x in range(x0 + 6, x1 - 15) for y in range(cy - 6, cy + 7)], 4,
             cap_at=(x1 - 4, cy + 1) if friendly else None)
    m.bar[(x0, cy)] = 1
    m.bar[(x1 - 14, cy)] = 2
    m.wall_fg = (186, 182, 172)
    m.signs.append((x0 - 4, y0 - 5, 'KEEP'))
    PL.lit(m, [(x0 + 2, cy - 1), (x1 - 4, cy - 1), (cx - 6, cy - 3)])
    return (x0 - 4, cy)


def fort_elf(game, site, m, cx, cy, friendly):
    wood(m, cx, cy, 44, 26, .85)
    inside = TP.oval(cx, cy, 22, 13)
    for x, y in inside:
        if m.inb(x, y):
            m.set(x, y, D.GRASS)
    edge = set(TP.ring_of(inside))
    for x, y in inside:                                                       # the ring of thorn, two thick
        if (x, y) in edge or any((x + a, y + b) in edge for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            m.set(x, y, D.THORNS)
    gate = (cx - 22, cy)
    shut = getattr(site, 'state', 'whole') == 'whole' and PL.tier(game, site) < 1
    for x in range(cx - 22, cx - 19):                                         # the gate of woven living branches
        m.set(x, cy, D.WOVEN if shut else D.WHITE)
        if shut:
            tell(m, x, cy, 'h_woven')
    PL.trail(m, (cx - 44, cy), (cx - 23, cy), D.WHITE)
    for k, (tx, ty) in enumerate(((cx - 10, cy - 6), (cx + 10, cy - 6), (cx - 10, cy + 6), (cx + 12, cy + 5))):
        if k == 1:
            continue
        fill(m, tx - 1, ty - 1, tx + 1, ty + 1, D.TRUNK)                     # guard trees
    tdoor = tower_at(game, site, m, cx + 10, cy - 6, 'elftree', random.randint(2, 3), (cx, cy))
    m.set(*tdoor, D.ODOOR)
    say(m, cx, cy, "The captain's stone: names cut in it, one under another. Every captain of the watch, and the last "
        'line still fresh.', D.STONE)
    fill(m, cx + 2, cy + 7, cx + 6, cy + 9, D.ROOT)                          # the hatch to the root cellars
    for x in range(cx + 2, cx + 7):
        m.set(x, cy + 8, D.GRASS)
    down(m, cx + 4, cy + 8)
    garrison(game, site, m, [(x, y) for x, y in inside if m.tile(x, y) == D.GRASS and cheb(x, y, cx, cy) > 3], 4,
             cap_at=(cx + 1, cy + 1) if friendly else None)
    m.wall_fg = (222, 234, 216)
    m.glows = [(cx, cy, (190, 230, 255), 3)]
    m.lights = list(m.glows)
    return gate


def fort_dwarf(game, site, m, cx, cy, friendly):
    rock(m, cx - 18, 0, cx + 30, m.h - 1)
    for y in range(cy - 3, cy + 4):                                           # the gorge, and the road through it
        for x in range(max(0, cx - 18), min(m.w, cx + 31)):
            m.set(x, y, PATH if abs(y - cy) <= 1 else m.ground)
    wx = cx + 2
    for y in range(cy - 4, cy + 5):                                           # the wall across the gorge
        for x in (wx, wx + 1, wx + 2):
            m.set(x, y, WALL)
    for y in range(cy - 1, cy + 2):
        m.set(wx, y, DOOR)
        m.set(wx + 1, y, FLOOR)
        m.set(wx + 2, y, FLOOR)
    m.portcullis = [(wx + 1, y) for y in range(cy - 1, cy + 2)]
    for x in range(cx - 10, wx):                                              # murder holes over the road
        if x % 3 == 0:
            tell(m, x, cy, 'h_murder')
    for x in range(cx - 12, wx, 4):                                           # bolt throwers in the cliffs
        for y in (cy - 4, cy + 4):
            say(m, x, y, 'A bolt thrower in a niche in the cliff, aimed down at the road.', D.BOLTS)
    TP.box(m, wx + 4, cy - 14, wx + 20, cy - 4)                              # the barracks
    m.set(wx + 10, cy - 4, DOOR)
    for x in range(wx + 6, wx + 19, 2):
        m.set(x, cy - 12, D.BED)
    TP.box(m, wx + 4, cy + 4, wx + 16, cy + 12)                              # the forge
    m.set(wx + 10, cy + 4, DOOR)
    m.set(wx + 8, cy + 9, D.ANVIL)
    m.set(wx + 12, cy + 9, D.FIREPIT)
    TP.box(m, wx + 16, cy + 4, wx + 26, cy + 12)                             # the stair hall, down to the halls
    m.set(wx + 21, cy + 4, DOOR)
    down(m, wx + 23, cy + 9)
    tdoor = tower_at(game, site, m, wx + 8, cy - 20, 'corner', random.randint(2, 3), (wx + 8, cy - 14))
    for y in range(tdoor[1] + 1, cy - 13):                                   # the stair up to the battlements
        m.set(tdoor[0], y, FLOOR)
    m.set(tdoor[0], cy - 14, DOOR)
    for x in range(wx - 2, wx + 4):                                          # the postern: a narrow way round, in the rock
        m.set(x, cy - 6, FLOOR)
    m.set(wx - 2, cy - 5, FLOOR)
    m.set(wx - 2, cy - 4, DOOR)
    m.set(wx + 3, cy - 5, FLOOR)
    m.set(wx + 3, cy - 4, FLOOR)
    garrison(game, site, m, [(x, y) for x in range(wx + 3, wx + 26) for y in range(cy - 2, cy + 3)], 4,
             cap_at=(wx + 5, cy) if friendly else None)
    for y in range(cy - 1, cy + 2):
        m.bar[(wx, y)] = 1
    m.wall_fg = (156, 136, 112)
    PL.lit(m, [(wx - 1, cy - 2), (wx - 1, cy + 2), (wx + 12, cy + 8)])
    return (max(1, cx - 18), cy)


def fort_halfling(game, site, m, cx, cy, friendly):
    PL.clear(m, cx - 20, cy - 13, cx + 20, cy + 13)
    inside = TP.oval(cx, cy, 16, 10)
    edge = set(TP.ring_of(inside))
    for x, y in inside:
        if (x, y) in edge or any((x + a, y + b) in edge for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            m.set(x, y, D.HEDGE)
    gate = (cx - 16, cy)
    for x in range(cx - 16, cx - 13):
        m.set(x, cy, PATH)
    TP.rounded(m, cx, cy, 6, 4, WALL, PLANK)                                  # the watch house
    m.round_doors = True
    m.set(cx - 6, cy, DOOR)
    m.set(cx + 2, cy - 2, D.TABLE)
    m.set(cx + 3, cy + 2, D.BED)
    down(m, cx - 2, cy + 2)
    m.set(cx - 9, cy - 4, D.BELL)                                            # the bell to raise the hamlets
    tdoor = tower_at(game, site, m, cx + 10, cy, 'loft', 2, (cx + 10, cy + 5))
    m.set(*tdoor, DOOR)
    garrison(game, site, m, [(x, y) for x, y in inside if m.tile(x, y) in (m.ground, PLANK)], 2,
             cap_at=(cx + 1, cy) if friendly else None)
    PL.lit(m, [(cx, cy - 1)])
    return gate


def fort_gnome(game, site, m, cx, cy, friendly):
    rock(m, cx - 20, cy - 15, cx + 24, cy + 15)
    hid = PL.tier(game, site) < 1
    rooms = [(cx, cy, 6, 4), (cx - 11, cy - 6, 4, 2), (cx + 12, cy - 6, 4, 3), (cx + 12, cy + 7, 4, 2), (cx - 10, cy + 7, 4, 2)]
    for a, b, c, d in rooms:
        TP.rounded(m, a, b, c, d, D.EARTH, FLOOR)
    from .tribes import line
    for r in rooms[1:]:
        for x, y in line(rooms[0][:2], r[:2]):
            if m.tile(x, y) in (D.EARTH, D.ROCK):
                m.set(x, y, FLOOR)
    tunnel = [(x, cy) for x in range(cx - 20, cx - 5)]
    for x, y in tunnel:
        m.set(x, y, FLOOR)
    door = (cx - 20, cy)
    m.set(*door, D.SECRET if hid else DOOR)                                   # the hill looks empty from outside
    say(m, cx, cy - 1, 'The illusion crystal. Look into it and you see the hill from outside: grass, a rabbit, '
        'nothing else at all.', D.CRYSTAL)
    if hid and getattr(site, 'state', 'whole') == 'whole':                   # traps on every way in
        from .behave import traps
        tr = traps(m)
        for x, y in tunnel[2::3]:
            tr[(x, y)] = 3
    m.peeps = True                                                            # peep holes all round (site_map)
    m.set(cx + 13, cy - 7, D.BED)
    m.set(cx + 11, cy - 7, D.BED)
    m.set(cx - 12, cy - 6, D.GEARS)
    down(m, cx + 13, cy + 7)
    garrison(game, site, m, [c for r in rooms for c in TP.oval(r[0], r[1], r[2] - 1, r[3] - 1)], 3,
             cap_at=(cx + 2, cy + 1) if friendly else None)
    m.glows = [(cx, cy - 1, (120, 230, 255), 5)]
    m.lights = list(m.glows)
    return door


def fort_orc(game, site, m, cx, cy, friendly):
    from .tribes import round_hut
    PL.clear(m, cx - 30, cy - 19, cx + 30, cy + 19)
    TP.box(m, cx - 26, cy - 16, cx + 26, cy + 16, D.STAKES, m.ground)        # the ditch of stakes
    TP.box(m, cx - 24, cy - 14, cx + 24, cy + 14, D.PALISADE, m.ground)
    for x in range(cx - 27, cx - 23):
        m.set(x, cy, PATH)
    gate = (cx - 26, cy)
    tdoor = tower_at(game, site, m, cx - 21, cy - 4, 'loft', random.randint(2, 3), (cx - 18, cy), mark=D.DRUM)
    m.set(*tdoor, DOOR)
    fill(m, cx - 23, cy + 3, cx - 19, cy + 5, D.PALISADE)                    # the other gate tower
    TP.box(m, cx + 4, cy - 12, cx + 22, cy - 4, D.HIDE, FLOOR)               # the warlord's hall
    m.set(cx + 13, cy - 4, DOOR)
    say(m, cx + 20, cy - 8, "The warlord's seat: a heap of shields with a skull on each, and a great one on top.",
        D.HIGHSEAT)
    m.set(cx + 9, cy - 8, D.FIREPIT)
    for y in range(cy - 2, cy + 6, 3):                                       # sleeping rows
        for x in range(cx - 14, cx - 2, 2):
            m.set(x, y, D.FURS)
    for x in range(cx + 2, cx + 8):
        m.set(x, cy + 3, D.RACK)
    for x in range(cx + 10, cx + 21):                                        # the warg pen
        for y in (cy + 5, cy + 12):
            m.set(x, y, D.FENCE)
    for y in range(cy + 5, cy + 13):
        for x in (cx + 10, cx + 20):
            m.set(x, y, D.FENCE)
    round_hut(m, cx - 12, cy + 10, 3, 2, D.HIDE, FLOOR)                      # the pits below
    m.set(cx - 12, cy + 8, DOOR)
    down(m, cx - 11, cy + 10)
    TP.foes(game, site, m, [(x, y) for y in range(cy - 12, cy + 12) for x in range(cx - 18, cx + 22)
                            if m.tile(x, y) == m.ground], 7, chief_at=(cx + 19, cy - 8))
    TP.beasts(game, site, m, [(x, y) for x in range(cx + 11, cx + 20) for y in range(cy + 6, cy + 12)], 2)
    PL.lit(m, [(cx + 9, cy - 7), (cx - 20, cy)])
    return gate


def fort_goblin(game, site, m, cx, cy, friendly):
    PL.clear(m, cx - 24, cy - 16, cx + 24, cy + 16)
    wall = TP.oval(cx, cy, 20, 12)
    for k, (x, y) in enumerate(TP.ring_of(wall)):                            # a ring of scrap, carts and planks
        m.set(x, y, (D.CART, D.PALISADE, D.RUBBLE, D.PALISADE)[(x * 3 + y) % 4])
    gate = (cx - 20, cy)
    m.set(*gate, PATH)
    from .behave import traps
    tr, kinds = traps(m), m.__dict__.setdefault('trap_kind', {})
    if not PL.friendly(game, site):                                           # spiked pits at the gate
        for c in ((cx - 18, cy), (cx - 17, cy - 1), (cx - 16, cy + 1)):
            tr[c] = 5
            kinds[c] = 'pit'
    tdoor = tower_at(game, site, m, cx + 2, cy - 7, 'loft', 2, (cx, cy), mark=D.GONG)
    m.set(*tdoor, DOOR)
    for x, y in ((cx - 10, cy - 8), (cx - 10, cy + 8), (cx + 12, cy + 9)):  # catapults of junk
        say(m, x, y, 'A catapult of junk: a cart wheel, a bent spar and a basket of stones. It might even work.', D.BOLTS)
    for x in range(cx - 6, cx + 6, 2):
        m.set(x, cy + 6, D.MIDDEN)
    m.set(cx + 12, cy, D.FIREPIT)
    fill(m, cx + 14, cy - 2, cx + 16, cy + 2, D.RUBBLE)
    down(m, cx + 15, cy)
    m.set(cx + 14, cy, FLOOR)
    TP.foes(game, site, m, [(x, y) for x, y in wall if m.tile(x, y) == m.ground and cheb(x, y, cx, cy) > 2], 7,
            chief_at=(cx + 11, cy + 1))
    PL.lit(m, [(cx + 12, cy + 1)])
    return gate


def fort_kobold(game, site, m, cx, cy, friendly):
    rock(m, cx - 26, cy - 18, cx + 30, cy + 18)
    PL.clear(m, cx - 34, cy - 1, cx - 25, cy + 1)
    tunnel = [(x, cy) for x in range(cx - 25, cx + 12)]
    for x, y in tunnel:
        m.set(x, y, FLOOR)
    from .behave import traps
    tr, kinds = traps(m), m.__dict__.setdefault('trap_kind', {})
    hostile = not PL.friendly(game, site)
    for k, (x, y) in enumerate(tunnel[3::4]):                                 # a trap every few steps
        if hostile:
            tr[(x, y)] = 3 + k % 3
            if k % 3 == 1:
                kinds[(x, y)] = 'plate'
            elif k % 3 == 2:
                kinds[(x, y)] = 'wire'
    for x in range(cx - 20, cx + 10, 6):                                      # spy holes from side tunnels
        for dy in (-1, 1):
            m.set(x, cy + dy, D.SLIT)
            m.set(x, cy + 2 * dy, FLOOR)
            m.set(x + 1, cy + 2 * dy, FLOOR)
            m.set(x + 2, cy + 2 * dy, FLOOR)
    if hostile:
        tell(m, cx + 4, cy, 'h_ceiling')                                      # the ceiling ready to drop
    cells = TP._cave(m, cx + 18, cy, 150)
    for x in range(cx + 11, cx + 19):
        m.set(x, cy, FLOOR)
    far = max(cells, key=lambda c: c[0])
    m.set(*far, D.GLITTER)
    left = [c for c in cells if m.tile(*c) == FLOOR and cheb(c[0], c[1], *far) > 4]
    if left:
        down(m, *min(left, key=lambda c: c[1]))
    TP.foes(game, site, m, list(cells) + tunnel[-6:], 6, chief_at=(far[0] - 1, far[1]))
    m.glows = [(far[0] - 1, far[1], (255, 210, 120), 3)]
    m.lights = list(m.glows)
    return (cx - 34, cy)


def fort_gnoll(game, site, m, cx, cy, friendly):
    PL.clear(m, cx - 28, cy - 18, cx + 28, cy + 18)
    outer, inner = TP.oval(cx, cy, 24, 14), TP.oval(cx, cy, 15, 9)
    ring(m, outer, D.THORNS)
    ring(m, inner, D.THORNS)
    gate = (cx - 24, cy)
    m.set(*gate, PATH)
    m.set(cx, cy + 9, PATH)                                                   # the inner gate on the far side
    m.set(cx, cy - 9, D.THORNS)
    tdoor = tower_at(game, site, m, cx - 14, cy - 10, 'loft', 2, (cx - 14, cy - 4), mark=D.HORN)
    m.set(*tdoor, DOOR)
    for x, y in TP.oval(cx + 3, cy - 1, 2, 1):                                # the packlord's bones
        m.set(x, y, D.BONES)
    say(m, cx + 3, cy - 1, "The packlord's seat: a heap of bones with a great skull on top, and the best bones for "
        'himself.', D.HIGHSEAT)
    for x in range(cx - 8, cx - 2, 2):
        m.set(x, cy + 3, D.FURS)
    fill(m, cx + 6, cy + 3, cx + 8, cy + 5, D.BAREROCK)
    down(m, cx + 7, cy + 4)
    TP.foes(game, site, m, [(x, y) for x, y in inner if m.tile(x, y) == m.ground and cheb(x, y, cx, cy) > 3], 6,
            chief_at=(cx + 2, cy))
    TP.beasts(game, site, m, [(x, y) for x, y in outer if m.tile(x, y) == m.ground and (x, y) not in set(inner)], 3)
    PL.lit(m, [(cx, cy + 1)])
    return gate


def fort_lizard(game, site, m, cx, cy, friendly):
    swamp(m, cx, cy, 34, 20, deep=True)
    TP.box(m, cx - 9, cy - 7, cx + 9, cy + 7, D.REEDS, PLANK)                 # the reed fort on stilts
    TP.box(m, cx - 2, cy - 7, cx + 9, cy, D.REEDS, PLANK)
    m.set(cx - 9, cy, DOOR)
    m.set(cx + 2, cy, DOOR)
    walk = [(x, cy) for x in range(cx - 34, cx - 9)]                         # one plank walkway
    for x, y in walk:
        if m.inb(x, y) and m.tile(x, y) in (D.WATER, D.SHALLOW, D.SWAMP, m.ground):
            m.set(x, y, PLANK)
    m.walkway = [c for c in walk if m.inb(*c) and m.tile(*c) == PLANK and cheb(c[0], c[1], cx, cy) > 12]
    for x, y in ((cx - 9, cy - 7), (cx + 9, cy - 7), (cx - 9, cy + 7), (cx + 9, cy + 7)):
        m.set(x, y, D.STILT)
    for x in range(cx - 7, cx - 2, 2):
        m.set(x, cy + 5, D.FURS)
    m.set(cx + 6, cy - 4, D.FIREPIT)
    down(m, cx + 7, cy + 5)
    TP.foes(game, site, m, [(x, y) for y in range(cy - 6, cy + 7) for x in range(cx - 8, cx + 9)
                            if m.tile(x, y) == PLANK], 6, chief_at=(cx + 5, cy - 3))
    TP.beasts(game, site, m, [(x, y) for y in range(cy - 16, cy + 17) for x in range(cx - 30, cx + 31)
                              if m.tile(x, y) == D.SHALLOW and cheb(x, y, cx, cy) > 10], 2)
    PL.lit(m, [(cx + 6, cy - 3)])
    return (cx - 34, cy)


# ==================================================================== manors
def manor_human(game, site, m, cx, cy, friendly):
    PL.clear(m, cx - 26, cy - 15, cx + 24, cy + 15)
    TP.box(m, cx - 22, cy - 13, cx + 22, cy + 13, WALL, m.ground)             # the garden wall
    gate = (cx - 22, cy)
    m.set(*gate, PATH)
    for x in range(cx - 21, cx - 12):                                         # the lane to the door
        m.set(x, cy, PATH)
    TP.box(m, cx - 12, cy - 7, cx + 4, cy + 7)                                # the great hall
    door = (cx - 12, cy)
    m.set(*door, DOOR)
    tell(m, cx + 3, cy - 6, 'h_portrait')                                     # the portrait over the hearth
    m.set(cx + 3, cy - 6, WALL)
    m.set(cx + 3, cy - 5, D.HEARTH)
    m.set(cx - 6, cy + 4, D.TABLE)
    TP.box(m, cx + 4, cy - 7, cx + 14, cy)                                    # the dining room
    m.set(cx + 4, cy - 3, DOOR)
    for x in range(cx + 6, cx + 13):
        m.set(x, cy - 4, D.TABLE)
    TP.box(m, cx + 4, cy, cx + 14, cy + 7)                                    # the kitchen and the store
    m.set(cx + 4, cy + 3, DOOR)
    m.set(cx + 12, cy + 2, D.HEARTH)
    m.set(cx + 8, cy + 5, D.BARREL)
    m.set(cx + 9, cy + 5, D.BARREL)
    m.set(cx + 14, cy + 4, DOOR)                                              # the back door, to the well
    m.set(cx + 18, cy + 4, D.WELL)
    for y in range(cy + 6, cy + 12):
        for x in range(cx + 15, cx + 21):
            if y % 2 == 0:
                m.set(x, y, D.FIELD)
    TP.box(m, cx - 12, cy + 7, cx - 2, cy + 11)                               # the chapel
    m.set(cx - 7, cy + 7, DOOR)
    m.set(cx - 4, cy + 10, D.ALTAR)
    m.set(cx - 9, cy + 10, D.PEW)
    for x in range(cx - 18, cx - 13, 2):
        for y in range(cy - 11, cy - 3, 3):
            m.set(x, y, D.TREE)
    down(m, cx + 13, cy + 6)
    upper(site, m, (cx - 10, cy - 5), 'The bedrooms and the study. The floorboards creak; a clock ticks somewhere.',
          boxes=[(cx - 12, cy - 7, cx - 2, cy + 7), (cx - 2, cy - 7, cx + 14, cy), (cx - 2, cy, cx + 14, cy + 7)],
          doors=[(cx - 2, cy - 3), (cx - 2, cy + 3)],
          put=[(cx + 12, cy - 5, D.BED), (cx + 12, cy + 5, D.BED), (cx - 9, cy + 4, D.SHELVES), (cx - 7, cy + 4, D.SHELVES)],
          tells=[(cx - 5, cy + 1, 'h_letters', None)], folk=('maid', '#c8c0b0', 1))
    owner(game, site, m, cx, cy + 2, friendly)
    if friendly:
        TP.folk(game, m, site, [(x, y) for x in range(cx + 6, cx + 13) for y in (cy + 2, cy + 5)], 2, 'servant', '#c8c0b0')
    m.bar[door] = 1
    PL.lit(m, [(cx + 3, cy - 4), (cx + 11, cy + 2)])
    return gate


def manor_elf(game, site, m, cx, cy, friendly):
    wood(m, cx, cy, 36, 24, .85)
    for x, y in TP.oval(cx, cy, 16, 10):
        if m.inb(x, y):
            m.set(x, y, D.GRASS)
    PL.trail(m, (cx - 34, cy), (cx - 16, cy), D.WHITE)
    trunks = [(cx - 8, cy - 5), (cx + 8, cy - 5), (cx - 8, cy + 5), (cx + 8, cy + 5)]
    for tx, ty in trunks:
        fill(m, tx - 1, ty - 1, tx + 1, ty + 1, D.TRUNK)
    for x, y in TP.oval(cx, cy, 4, 2):                                        # the moon garden
        m.set(x, y, D.WHITE if (x + y) % 2 else D.FIELD)
    m.set(cx, cy, D.FOUNTAIN)
    m.moonwell = (cx, cy)
    tx, ty = trunks[0]
    m.set(tx + 1, ty, D.ODOOR)
    m.set(tx, ty, PLANK)
    hatch = (trunks[3][0], trunks[3][1])
    m.set(trunks[3][0] - 1, trunks[3][1], D.ODOOR)
    m.set(*hatch, PLANK)
    down(m, *hatch)
    m.set(tx, ty, PLANK)
    upper(site, m, (tx, ty), 'Rooms of living wood among the leaves, joined by bridges. The house sways a little.',
          wall=D.HEDGE, floor=PLANK, ovals=[(tx, ty, 4, 3), (cx + 9, cy - 6, 4, 3), (cx - 9, cy + 6, 4, 3), (cx + 9, cy + 6, 4, 3)],
          bridges=[((tx + 4, ty), (cx + 5, cy - 6)), ((tx, ty + 3), (cx - 9, cy + 3)), ((cx + 9, cy - 3), (cx + 9, cy + 3))],
          put=[(cx + 11, cy - 7, D.SHELVES), (cx - 11, cy + 6, D.BED), (cx + 11, cy + 6, D.PEW), (cx + 7, cy + 6, D.PEW)],
          tells=[(cx + 7, cy - 7, 'h_letters', None)], folk=('singer', '#e0e8d0', 1))
    owner(game, site, m, cx + 3, cy + 1, friendly)
    m.wall_fg = (222, 234, 216)
    m.glows = [(cx, cy, (190, 230, 255), 3)]
    m.lights = list(m.glows)
    return (cx - 16, cy)


def manor_dwarf(game, site, m, cx, cy, friendly):
    rock(m, cx - 16, cy - 16, cx + 28, cy + 16)
    PL.clear(m, cx - 30, cy - 4, cx - 15, cy + 4)
    TP.box(m, cx - 14, cy - 6, cx + 6, cy + 6)                                # the hearth hall
    door = (cx - 14, cy)
    m.set(*door, DOOR)
    say(m, cx - 15, cy - 1, 'A carved door: the clan\'s marks, an axe, a hammer and a mountain, cut deep in oak and iron.',
        D.STATUE)
    m.set(cx - 15, cy + 1, D.STATUE)
    m.set(cx - 3, cy, D.HEARTH)
    for x in range(cx - 12, cx + 5, 3):                                       # the ancestor wall
        tell(m, x, cy - 5, 'h_portrait', tile=D.STATUE)
    for x in range(cx - 10, cx + 3, 2):
        m.set(x, cy + 3, D.TABLE)
    TP.box(m, cx + 6, cy - 10, cx + 18, cy - 2)                              # the brew room
    m.set(cx + 6, cy - 4, DOOR)
    for x in range(cx + 8, cx + 17, 2):
        m.set(x, cy - 8, D.BARREL)
    TP.box(m, cx + 6, cy + 2, cx + 14, cy + 9)                               # the treasury, behind bars
    m.set(cx + 6, cy + 4, D.BARS)
    m.set(cx + 11, cy + 6, D.CHEST)
    TP.box(m, cx + 14, cy - 2, cx + 24, cy + 9)                              # sleeping rooms, and the vault below
    m.set(cx + 14, cy, DOOR)
    for y in (cy + 2, cy + 5):
        m.set(cx + 22, y, D.BED)
    down(m, cx + 17, cy + 7)
    TP.box(m, cx + 6, cy - 2, cx + 14, cy + 2)
    m.set(cx + 6, cy, DOOR)
    m.set(cx + 14, cy, DOOR)
    owner(game, site, m, cx - 2, cy + 1, friendly)
    m.wall_fg = (176, 150, 120)
    PL.lit(m, [(cx - 3, cy + 1), (cx + 10, cy - 7)])
    return (cx - 30, cy)


def manor_halfling(game, site, m, cx, cy, friendly):
    PL.clear(m, cx - 26, cy - 16, cx + 24, cy + 16)
    hill = TP.oval(cx + 2, cy, 18, 11)
    for x, y in hill:
        m.set(x, y, D.ROCK)
    rooms = [(cx - 4, cy, 6, 3), (cx + 9, cy - 5, 4, 2), (cx + 9, cy + 5, 4, 2), (cx - 4, cy - 7, 4, 2), (cx - 4, cy + 7, 4, 2)]
    for a, b, c, d in rooms:
        TP.rounded(m, a, b, c, d, D.EARTH, PLANK)
    from .tribes import line
    for r in rooms[1:]:
        for x, y in line(rooms[0][:2], r[:2]):
            if m.tile(x, y) in (D.EARTH, D.ROCK):
                m.set(x, y, PLANK)
    m.round_doors = True
    for x in range(cx - 16, cx - 9):
        m.set(x, cy, PLANK)
    door = (cx - 16, cy)
    m.set(*door, DOOR)
    m.set(cx - 7, cy - 2, D.HEARTH)                                           # the parlour, its portrait over the hearth
    tell(m, cx - 6, cy - 3, 'h_portrait', tile=D.EARTH)
    for x in (cx - 2, cx):
        m.set(x, cy + 1, D.PEW)
    px, py = rooms[1][:2]                                                     # pantries full of jars
    for x in range(px - 3, px + 4, 2):
        m.set(x, py - 1, D.SHELVES)
    m.set(px + 2, py + 1, D.BARREL)
    sx, sy = rooms[3][:2]
    tell(m, sx + 2, sy, 'h_letters', tile=D.TABLE)
    m.set(sx - 2, sy - 1, D.SHELVES)
    bx, by = rooms[4][:2]
    m.set(bx - 2, by, D.BED)
    m.set(bx + 2, by, D.BED)
    qx, qy = rooms[2][:2]
    down(m, qx + 2, qy)
    for y in range(cy - 13, cy + 14):                                         # flower gardens
        for x in range(cx - 24, cx - 16):
            if (x + y) % 3 == 0:
                m.set(x, y, D.FIELD)
    owner(game, site, m, cx - 3, cy + 1, friendly)
    PL.lit(m, [(cx - 7, cy - 1)])
    return (cx - 24, cy)


def manor_gnome(game, site, m, cx, cy, friendly):
    wood(m, cx, cy, 32, 20, .6)
    PL.clear(m, cx - 14, cy - 10, cx + 14, cy + 10)
    for k in range(18):                                                      # the little mushrooms round about
        a = random.random() * math.tau
        r = random.uniform(8, 12)
        m.set(round(cx + math.cos(a) * r), round(cy + math.sin(a) * r * .7), D.SHROOM)
    TP.rounded(m, cx, cy, 5, 4, D.TRUNK, FLOOR)                              # the stem: the workshop
    door = (cx - 5, cy)
    m.set(*door, DOOR)
    m.set(cx + 2, cy - 2, D.GEARS)
    m.set(cx + 3, cy + 1, D.BENCH)
    down(m, cx - 2, cy + 2)
    upper(site, m, (cx + 1, cy + 2), 'The cap of the great mushroom. The walls are soft and smell of rain.',
          wall=D.SHROOM, floor=PLANK, ovals=[(cx, cy, 12, 7)], boxes=[],
          put=[(cx - 8, cy - 2, D.BED), (cx + 8, cy - 3, D.ALCHEMY), (cx + 9, cy + 2, D.SHELVES)] +
          [(cx - 3, y, D.EARTH) for y in range(cy - 6, cy - 1)] + [(cx + 4, y, D.EARTH) for y in range(cy + 3, cy + 7)],
          tells=[(cx - 6, cy + 3, 'h_letters', None)], folk=('apprentice', '#e0cc80', 1))
    owner(game, site, m, cx - 1, cy - 1, friendly)
    PL.lit(m, [(cx + 2, cy - 1)])
    return (cx - 14, cy)


def manor_orc(game, site, m, cx, cy, friendly):
    PL.clear(m, cx - 26, cy - 14, cx + 26, cy + 14)
    TP.box(m, cx - 20, cy - 4, cx + 20, cy + 4, D.HIDE, FLOOR)               # the long hall
    door = (cx - 20, cy)
    m.set(*door, DOOR)
    say(m, cx - 22, cy - 2, 'A skull pole at the door: the chief\'s kills, the newest on top.', D.TOTEM)
    for x in range(cx - 14, cx + 14, 6):                                      # fires down the middle
        m.set(x, cy, D.FIREPIT)
    for x in range(cx - 18, cx + 16, 2):                                      # sleeping benches along the walls
        m.set(x, cy - 3, D.FURS)
        m.set(x, cy + 3, D.FURS)
    tell(m, cx + 18, cy, 'h_portrait', tile=D.HIGHSEAT)                      # the chief's seat
    for x in range(cx - 8, cx + 8):                                           # the warg yard
        for y in (cy + 7, cy + 12):
            m.set(x, y, D.FENCE)
    for y in range(cy + 7, cy + 13):
        for x in (cx - 8, cx + 7):
            m.set(x, y, D.FENCE)
    fill(m, cx + 12, cy - 9, cx + 14, cy - 7, D.BAREROCK)
    down(m, cx + 13, cy - 8)
    TP.foes(game, site, m, [(x, y) for x in range(cx - 18, cx + 17) for y in (cy - 2, cy - 1, cy + 1, cy + 2)], 5,
            chief_at=(cx + 17, cy))
    TP.beasts(game, site, m, [(x, y) for x in range(cx - 7, cx + 7) for y in range(cy + 8, cy + 12)], 2)
    PL.lit(m, [(cx - 14, cy + 1), (cx + 10, cy + 1)])
    return (cx - 26, cy)


def manor_goblin(game, site, m, cx, cy, friendly):
    rock(m, cx - 16, cy - 15, cx + 26, cy + 15)
    PL.clear(m, cx - 30, cy - 1, cx - 15, cy + 1)
    for x in range(cx - 16, cx - 9):
        m.set(x, cy, FLOOR)
    TP.box(m, cx - 10, cy - 5, cx + 4, cy + 5)                                # the counting room
    m.set(cx - 10, cy, DOOR)
    for x in range(cx - 7, cx + 3, 3):
        tell(m, x, cy - 2, 'h_letters', tile=D.TABLE)
    tell(m, cx, cy + 3, 'h_portrait', tile=D.HIGHSEAT)
    TP.box(m, cx + 4, cy - 9, cx + 16, cy - 1)                                # the strongroom
    m.set(cx + 4, cy - 3, D.BARS)
    m.set(cx + 13, cy - 6, D.CHEST)
    m.set(cx + 10, cy - 6, D.GLITTER)
    TP.box(m, cx + 4, cy + 1, cx + 18, cy + 9)                                # the store of stolen goods
    m.set(cx + 4, cy + 3, DOOR)
    for x in range(cx + 6, cx + 17, 2):
        m.set(x, cy + 7, D.BARREL if x % 4 else D.MIDDEN)
    down(m, cx + 16, cy + 3)
    TP.foes(game, site, m, [(x, y) for x in range(cx - 9, cx + 17) for y in range(cy - 4, cy + 8)], 5, chief_at=(cx + 1, cy + 3))
    PL.lit(m, [(cx - 3, cy - 1)])
    return (cx - 30, cy)


def manor_kobold(game, site, m, cx, cy, friendly):
    cells, mouth, far = TP.nook(game, site, m, cx, cy, friendly, [D.GEMS, D.GLITTER, D.MIRROR, D.BENCH, D.GLITTER], D.GLITTER)
    tell(m, far[0], far[1], 'h_portrait', tile=D.GLITTER)
    for c in sorted(cells, key=lambda c: -c[1])[:3]:
        if m.tile(*c) == FLOOR:
            m.set(c[0], c[1], D.GEMS)
    TP.foes(game, site, m, list(cells), 5, chief_at=(far[0] - 1, far[1]))
    m.glows = [(far[0] - 1, far[1], (255, 210, 120), 4)]
    m.lights = list(m.glows)
    return mouth


def manor_gnoll(game, site, m, cx, cy, friendly):
    from .tribes import round_hut
    PL.clear(m, cx - 24, cy - 15, cx + 24, cy + 15)
    ring(m, TP.oval(cx, cy, 20, 12), D.THORNS)
    gate = (cx - 20, cy)
    m.set(*gate, PATH)
    round_hut(m, cx + 2, cy, 10, 6, D.HIDE, FLOOR)                           # the great tent
    m.set(cx - 8, cy, DOOR)
    tell(m, cx + 9, cy, 'h_portrait', tile=D.HIGHSEAT)
    for x, y in ((cx + 9, cy - 1), (cx + 9, cy + 1), (cx + 10, cy)):
        m.set(x, y, D.BONES)
    say(m, cx + 4, cy - 4, "The packlord's share of the kill: a haunch, a head, a heap of ribs. Nobody else touches it.",
        D.BLOODPIT)
    m.set(cx - 2, cy + 3, D.FURS)
    down(m, cx + 5, cy + 4)
    TP.foes(game, site, m, [(x, y) for x, y in TP.oval(cx + 2, cy, 8, 4)], 4, chief_at=(cx + 8, cy))
    TP.beasts(game, site, m, [(x, y) for x in range(cx - 16, cx - 9) for y in range(cy - 3, cy + 4)], 2)
    PL.lit(m, [(cx, cy + 1)])
    return gate


def manor_lizard(game, site, m, cx, cy, friendly):
    from .tribes import round_hut
    swamp(m, cx, cy, 26, 16)
    round_hut(m, cx, cy, 7, 4, D.REEDS, PLANK)                               # the elder's house on stilts
    m.set(cx - 7, cy, DOOR)
    m.set(cx + 7, cy - 1, D.WINDOW)
    m.set(cx + 7, cy, D.WINDOW)
    tell(m, cx + 5, cy, 'h_portrait', tile=D.EGGS)                           # the egg of the line
    m.set(cx - 3, cy - 2, D.FURS)
    down(m, cx + 2, cy + 3)
    for x in range(cx - 26, cx - 7):
        if m.tile(x, cy) in (D.SHALLOW, D.SWAMP, D.WATER, m.ground):
            m.set(x, cy, PLANK)
    for x in range(cx + 9, cx + 15):                                         # the fish pen
        for y in (cy + 5, cy + 9):
            m.set(x, y, D.FISHTRAP if x % 2 else D.STILT)
    TP.foes(game, site, m, [(x, y) for x, y in TP.oval(cx, cy, 5, 2)], 3, chief_at=(cx + 4, cy - 1))
    TP.beasts(game, site, m, [(x, y) for y in range(cy - 12, cy + 13) for x in range(cx - 20, cx + 21)
                              if m.tile(x, y) == D.SHALLOW and cheb(x, y, cx, cy) > 9], 1)
    PL.lit(m, [(cx - 2, cy)])
    return (cx - 26, cy)


def owner(game, site, m, x, y, friendly):
    """The one who lives here, at home (when they are friends of yours: the hostile peoples' chiefs fight)."""
    pe = PL.people_of(site)
    if friendly and pe not in PL.HOSTILE:
        TP.npc(game, m, site.owner, 'villager', '#f0e0b0', x, y)


PLANS = {
    'monastery': {'human': abbey_human, 'elf': abbey_elf, 'dwarf': abbey_dwarf, 'halfling': abbey_halfling,
                  'gnome': abbey_gnome, 'orc': abbey_orc, 'goblin': abbey_goblin, 'kobold': abbey_kobold,
                  'gnoll': abbey_gnoll, 'lizard': abbey_lizard},
    'fort': {'human': fort_human, 'elf': fort_elf, 'dwarf': fort_dwarf, 'halfling': fort_halfling, 'gnome': fort_gnome,
             'orc': fort_orc, 'goblin': fort_goblin, 'kobold': fort_kobold, 'gnoll': fort_gnoll, 'lizard': fort_lizard},
    'manor': {'human': manor_human, 'elf': manor_elf, 'dwarf': manor_dwarf, 'halfling': manor_halfling,
              'gnome': manor_gnome, 'orc': manor_orc, 'goblin': manor_goblin, 'kobold': manor_kobold,
              'gnoll': manor_gnoll, 'lizard': manor_lizard},
}


# ==================================================================== while you are there
def on_step(game):
    """Each step on a hall's map: its traps, the telling things you step on, and the alarm."""
    from . import behave as BH
    from . import themes as TH
    m, p = game.map, game.player
    BH.stepped(game)
    if game.dead:
        return
    BH.spot_traps(game)
    t = m.things.get((p.x, p.y))
    if t and D.TILES[m.tile(p.x, p.y)].walk:
        TH.ACTIONS[t[0]](game, p.x, p.y, t[1], TH.state(m, t[1]))
    alarm(game)


def alarm(game):
    """A foe that sees you raises the alarm: the portcullis drops, the plank walkway is pulled in."""
    m, p = game.map, game.player
    if getattr(m, 'alarmed', False) or not (getattr(m, 'portcullis', None) or getattr(m, 'walkway', None)):
        return
    seen = [o for o in m.mons if not o.is_npc and o.hp > 0 and cheb(o.x, o.y, p.x, p.y) <= 9 and game.visible(o.x, o.y)]
    if not seen:
        return
    m.alarmed = True
    for o in m.mons:
        if not o.is_npc:
            o.awake = True
    if getattr(m, 'portcullis', None):
        if (p.x, p.y) in m.portcullis:
            return
        for x, y in m.portcullis:
            m.set(x, y, D.BARS)
        game.msg('A shout, a rattle of chains, and the portcullis crashes down! The gate is shut. There may be a '
                 'postern somewhere.', 'bad')
    elif getattr(m, 'walkway', None):
        for x, y in m.walkway:
            if (x, y) != (p.x, p.y):
                m.set(x, y, D.SHALLOW)
        game.msg('They see you coming and pull in the plank walkway. You will have to wade.', 'bad')


def _once(game, st, key, text):
    from .themes import _once as once
    return once(game, st, key, text)


def a_say(game, x, y, rid, st):
    game.msg(game.map.says.get((x, y), 'Nothing of note.'), 'info')
    return 0


def a_lore(game, x, y, rid, st):
    """Lore kept on shelves or carved in stone: a page of the world's history, once per place."""
    from . import history as HI
    m = game.map
    key = f'lore{m.key}'
    done = game.player.__dict__.setdefault('hall_read', set())
    if key in done:
        game.msg('You have read what is kept here. The rest is prayers, accounts and old songs.', 'info')
        return 0
    done.add(key)
    evs = HI.events(game.world)
    if evs:
        e = random.choice(evs)
        HI.learn(game, e, 'read', m.name)
        game.msg(f'You read a while. One account catches your eye: {e["text"]}', 'gold')
    else:
        game.msg('You read a while: prayers, accounts and old songs.', 'info')
    return 10


def _unknown_sites(game, near=80):
    om = game.maps['over']
    ox, oy = game.world_pos()
    return [q for q in game.world.sites if not om.seen[q.y * om.w + q.x] and cheb(q.x, q.y, ox, oy) < near]


def a_reveal(game, x, y, rid, st):
    """A still pool or a lens: a far place shows itself, one a visit."""
    from .engine import dir_name
    p = game.player
    seen = p.__dict__.setdefault('hall_looked', {})
    key = game.map.key
    if seen.get(key) == game.day:
        game.msg('You look again, but see only yourself now. Come back another day.', 'info')
        return 0
    seen[key] = game.day
    cands = _unknown_sites(game)
    what = 'Stars, and your own face among them.' if game.map.hall == 'monastery' and PL.people_of(
        game.world.sites[game.map.site]) == 'elf' else 'Only sky.'
    if not cands:
        game.msg(f'You look a long while. {what}', 'info')
        return 2
    ox, oy = game.world_pos()
    q = min(cands, key=lambda c: cheb(c.x, c.y, ox, oy) + random.randint(0, 12))
    game.reveal_place(q.x, q.y)
    game.msg(f'You look a long while. Then a place shows itself, far to the {dir_name(q.x - ox, q.y - oy)}: '
             f'{q.name}. It is marked on your map.', 'good')
    return 2


def a_dungeonmap(game, x, y, rid, st):
    """The goblins' map room: where a way down lies that you do not know yet."""
    from .engine import dir_name
    if _once(game, st, 'read', 'You know this map now: every scribble on it.'):
        return 0
    om = game.maps['over']
    ox, oy = game.world_pos()
    cands = [d for d in game.world.dungeons.values() if getattr(d, 'site', None) is None and om.inb(d.x, d.y)
             and not om.seen[d.y * om.w + d.x] and cheb(d.x, d.y, ox, oy) < 90]
    if not cands:
        game.msg('A map of stolen roads and caravan routes. Nothing on it you did not know.', 'info')
        return 3
    d = min(cands, key=lambda c: cheb(c.x, c.y, ox, oy))
    game.reveal_place(d.x, d.y)
    game.msg(f'A map of stolen roads, and a skull drawn far to the {dir_name(d.x - ox, d.y - oy)}: {d.name}. '
             'It is marked on your map.', 'good')
    return 3


def a_meal(game, x, y, rid, st):
    """The long table of a halfling house: a meal for a friend, once a day."""
    from . import hunger as HU
    p = game.player
    site = game.world.sites[game.map.site]
    if not PL.friendly(game, site):
        game.msg('The long table, laid for many. Nobody asks you to sit.', 'info')
        return 0
    if getattr(p, 'hall_meal', -1) == game.day:
        game.msg('You have eaten here today. Another plate would be greedy, even here.', 'info')
        return 0
    p.hall_meal = game.day
    p.food = min(HU.MAX, p.food + 600)
    game.msg('They sit you down at the long table: bread, cheese, a pie and a mug of ale. You eat your fill.', 'good')
    return 20


def a_mirror(game, x, y, rid, st):
    game.msg('A polished mirror. In it you see yourself, and behind you a kobold polishing another mirror.', 'info')
    return 0


def a_woven(game, x, y, rid, st):
    game.msg('A gate of living branches woven tight. It opens for friends of the elves, and you are not one yet.', 'info')
    return 0


def a_murder(game, x, y, rid, st):
    """The murder holes over the dwarves' road: a word, the first time you walk under them."""
    seen = game.map.__dict__.setdefault('murder_seen', [False])
    if seen[0]:
        return 0
    seen[0] = True
    game.msg('You walk under the murder holes. Something moves up there in the dark.', 'info')
    return 0


def a_ceiling(game, x, y, rid, st):
    """The kobolds' last trick: the roof of the tunnel comes down behind you."""
    if st.get('down'):
        return 0
    st['down'] = True
    m = game.map
    for dx in (-2, -1):
        if m.tile(x + dx, y) == FLOOR:
            m.set(x + dx, y, D.RUBBLE)
    game.flash([(x - 1, y), (x - 2, y)], (180, 160, 120), ':', .3)
    game.msg('Something gives with a crack, and the roof comes down behind you! Stones rain on your back.', 'bad')
    game.hurt(4 + m.__dict__.get('level', 2), 'a falling ceiling')
    return 0


def a_portrait(game, x, y, rid, st):
    """Who lives here: the portrait, the ancestor wall, the seat."""
    site = game.world.sites[game.map.site]
    pe = PL.people_of(site)
    who = getattr(site, 'owner', 'someone')
    text = {'human': f'The portrait over the hearth: {who}, painted younger and kinder than life.',
            'elf': f'Carved in the living wood: {who}, with a harp.',
            'dwarf': f'The ancestor wall: the faces of the clan in stone, the last of them {who}.',
            'halfling': f'A portrait over the hearth: {who}, round and pleased, with a pipe.',
            'gnome': f'A drawing pinned to the wall: {who}, in goggles, beside a machine.',
            'orc': f"{who}'s seat. Skulls on the arms, and a hide over the back.",
            'goblin': f"{who}'s seat behind the counting table, with a cushion stolen from a lord.",
            'kobold': f"{who}'s bed: a heap of coins, still warm.",
            'gnoll': f"{who}'s seat of bones, gnawed smooth.",
            'lizard': f'The egg of the line, kept warm in a basket: {who}\'s heir, not yet hatched.'}[pe]
    game.msg(text, 'info')
    return 0


def a_letters(game, x, y, rid, st):
    """Letters and ledgers on the desk: a lead to something, once a day."""
    p = game.player
    if getattr(p, 'hall_letters', None) == (game.map.key, game.day):
        game.msg('You have read the letters. The rest are bills.', 'info')
        return 0
    p.hall_letters = (game.map.key, game.day)
    line = game.rumor()
    game.msg(f'Among the letters and ledgers, one is worth reading. {line}' if line else
             'Letters and ledgers: bills, a dull poem, a recipe for pie.', 'info')
    return 5


def a_lens(game, x, y, rid, st):
    return a_reveal(game, x, y, rid, st)


def a_pool(game, x, y, rid, st):
    return a_reveal(game, x, y, rid, st)


from . import themes as _TH                             # noqa: E402
_TH.ACTIONS.update({'h_say': a_say, 'h_lore': a_lore, 'h_pool': a_pool, 'h_lens': a_lens, 'h_dungeonmap': a_dungeonmap,
                    'h_meal': a_meal, 'h_mirror': a_mirror, 'h_woven': a_woven, 'h_murder': a_murder,
                    'h_ceiling': a_ceiling, 'h_portrait': a_portrait, 'h_letters': a_letters})
