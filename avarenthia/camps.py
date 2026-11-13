"""Camps on the road (round 65): hosts, raiders and caravans stop for the night, and a camp is a place you walk into.

From dusk to dawn every host on the march, every war party and every caravan far from a caravanserai camps where it
stands; a host at the end of its march sits down before the enemy's seat as a siege camp for some days. On the world
map a camp shows by its people's signs round the wanderer; its own small map has tents you walk into (cloth walls, a
flap for a door), fires by night and cold pits by day, and each people camps its own way: a kingdom's host in rows
inside a ring of stakes, a dwarf hammer band in a square of stone and shields, an elven war-band in bowers under the
trees (seen from one cell away only), the Gorvash in a sprawl round one great fire, sea raiders behind their ships on
the strand, riders in round tents in a ring.

What you are to a camp (friend, stranger, foe) comes from who you are sworn to and what you did there; what you did
lives on the player (p.camp_rel). A friend trades with the quartermaster at war prices, is mended and healed, hears
the war's news and may sign on; a stranger gets as far as the quartermaster for a gift or a good word; a foe sneaks in
by night (noise and light count) to steal the orders, burn the stores or free the prisoners, each weakening the host
in its battle; seen, the whole camp wakes. A traders' camp trades at its town's prices, tells the road's news, lets
you ride along in safety and sleep by its fire; robbers sometimes come in the night.

The camps themselves are of the world (world.camps); blackened fire rings stay on the land for some weeks
(world.camp_rings)."""
import random

from . import data as D
from .worldgen import cheb

RING_DAYS = 21
NIGHT_FG = (255, 150, 60)
# each people's way: its signs on the world map (left, above, right of the camp) and words
STYLES = {
    'host': dict(name="a kingdom's host", signs=('Λ', '¶', 'Λ'), sentries=4),
    'siege': dict(name='a siege camp', signs=('Λ', 'Ψ', 'Λ'), sentries=5),
    'dwarf': dict(name='a dwarf hammer band', signs=('▓', '∩', '▓'), sentries=6),
    'elf': dict(name='an elven war-band', signs=('∩', None, '∩'), sentries=3),
    'gorvash': dict(name='the Gorvash', signs=('Λ', '¥', 'Λ'), sentries=2),
    'sea': dict(name='sea raiders on the strand', signs=('▬', 'o', '▬'), sentries=2),
    'riders': dict(name='riders', signs=('Ω', 'h', 'Ω'), sentries=2),
    'traders': dict(name="a traders' camp", signs=('Θ', None, 'Θ'), sentries=1),
}
CAMPERS = {'host', 'raid', 'caravan', 'warband'}
RAID_STYLE = {'sea': 'sea', 'island': 'sea', 'wreckers': 'sea', 'ice': 'sea', 'desert': 'riders', 'canyon': 'riders',
              'barbarian': 'riders', 'pass': 'dwarf', 'mist': 'elf'}
TROOPS = {'host': ['soldier', 'soldier', 'crossbow', 'knight'], 'siege': ['soldier', 'soldier', 'crossbow', 'knight'],
          'dwarf': ['soldier', 'soldier', 'knight'], 'elf': ['crossbow', 'crossbow', 'soldier'],
          'gorvash': ['orc', 'orc_spear', 'orc_berserker'], 'sea': ['sea_raider', 'sea_raider', 'berserker'],
          'riders': ['clan_rider', 'dune_rider', 'clan_warrior'], 'traders': ['bandit']}


def state(world):
    if not isinstance(getattr(world, 'camps', None), list):
        world.camps = []
    if not isinstance(getattr(world, 'camp_rings', None), dict):
        world.camp_rings = {}
    return world.camps


def rel_store(game):
    p = game.player
    if not isinstance(getattr(p, 'camp_rel', None), dict):
        p.camp_rel = {}
    return p.camp_rel


def hour(game):
    return (game.turn % D.DAY_LEN) * 24 / D.DAY_LEN


def camping(game):
    """From dusk to dawn the roads stop."""
    from .seasons import dusk, dawn
    t = hour(game)
    return t >= dusk(game.day) or t < dawn(game.day)


def get(game, cid):
    return next((c for c in state(game.world) if c['id'] == cid), None)


def of_wd(game, wd):
    return next((c for c in state(game.world) if c.get('wd') == wd.id), None)


def at(game, x, y):
    """A camp whose ground covers this world cell (the wanderer's cell and the cells round it)."""
    for c in state(game.world):
        if cheb(c['x'], c['y'], x, y) <= 1:
            return c
    return None


def resting(game, wd):
    """A wanderer that has made camp does not walk on."""
    return wd.kind in CAMPERS and of_wd(game, wd) is not None


# ------------------------------------------------------------------ who camps how
def style_for(game, wd):
    w = game.world
    if wd.kind == 'host':
        R = getattr(w, 'realm', None)
        try:
            kg = R.kingdoms[wd.kingdom]
            people = R.houses[R.lord(kg.king).house].people
        except Exception:
            people = 'human'
        return {'dwarf': 'dwarf', 'elf': 'elf'}.get(people, 'host')
    if wd.kind == 'raid':
        try:
            rd = w.powers['raiders'][wd.raider]
            return RAID_STYLE.get(rd['kind'], 'riders')
        except Exception:
            return 'riders'
    if wd.kind == 'warband':
        return 'gorvash' if getattr(wd, 'faction', None) == 'horde' else 'host'
    if wd.kind == 'caravan':
        return 'traders'
    return None


def wants_camp(game, wd):
    if wd.kind not in CAMPERS:
        return False
    if wd.kind == 'caravan':                       # by a caravanserai or a town it sleeps under a roof
        w = game.world
        if any(cheb(s.x, s.y, wd.x, wd.y) <= 3 for s in w.settlements):
            return False
        from . import landmarks as LM
        if any(LM.is_mark(st) and st.kind == 'caravanserai' and cheb(st.x, st.y, wd.x, wd.y) <= 4 for st in w.sites):
            return False
    if game.world.settlement_at(wd.x, wd.y):
        return False
    return True


def make(game, wd, style, siege=False):
    w = game.world
    cs = state(w)
    cid = getattr(w, 'camp_next', 0) + 1            # never the number of a camp gone before
    w.camp_next = cid
    c = dict(id=cid, wd=wd.id, kind=wd.kind, style='siege' if siege else style, people=style, x=wd.x, y=wd.y,
             day=game.day, name=_name(game, wd, style, siege), fg=tuple(wd.fg), kingdom=getattr(wd, 'kingdom', None),
             foe=getattr(wd, 'foe', None), hostile=bool(wd.hostile), map=f'camp:{cid}', done=[], alarm=False,
             siege=siege, origin=getattr(wd, 'origin', None))
    cs.append(c)
    return c


def _name(game, wd, style, siege):
    if siege:
        return f'{wd.name} before the walls'
    if style == 'traders':
        return 'A caravan camped by the road'
    return wd.name


def tick(game):
    """Dusk and dawn: hosts, war parties and caravans make camp, and break it again; the old fire rings fade."""
    w = game.world
    cs = state(w)
    alive = {wd.id: wd for wd in w.wanderers}
    night = camping(game)
    for c in cs[:]:
        wd = alive.get(c['wd'])
        if wd is None or (not night and not c['siege']) or (c['siege'] and not getattr(wd, 'siege_until', None)):
            if game.cur == c['map']:
                continue                            # it breaks round you when you leave
            cs.remove(c)
            game.maps.pop(c['map'], None)
            w.camp_rings[(c['x'], c['y'])] = game.day
    stamp = (game.day, int(hour(game)))
    if night and getattr(w, 'camp_stamp', None) != stamp:      # once an hour is enough to look who sits down
        w.camp_stamp = stamp
        have = {c['wd'] for c in cs}
        for wd in w.wanderers:
            if wd.id not in have and wants_camp(game, wd):
                st = style_for(game, wd)
                if st:
                    make(game, wd, st)
    for k in [k for k, d in w.camp_rings.items() if game.day - d > RING_DAYS]:
        del w.camp_rings[k]


def siege(game, wd):
    """A host at the end of its march sits down before the seat: True while the siege lasts."""
    if getattr(wd, 'siege_until', None) is None:
        wd.siege_until = game.day + random.randint(3, 5)
        c = of_wd(game, wd)
        if c:
            state(game.world).remove(c)
            game.maps.pop(c['map'], None)
        make(game, wd, style_for(game, wd) or 'host', siege=True)
        from . import realms as RL
        RL.news(game, f'{wd.name} sits down before the walls: a siege.', wd.x, wd.y)
        return True
    if game.day < wd.siege_until:
        return True
    c = of_wd(game, wd)
    if c and game.cur != c['map']:
        state(game.world).remove(c)
        game.maps.pop(c['map'], None)
    wd.siege_until = None
    return False


# ------------------------------------------------------------------ what you are to it
def rel(game, c):
    """'friend', 'stranger' or 'foe'."""
    mine = rel_store(game).get(str(c['id']))
    if mine:
        return mine
    if c['style'] == 'traders':
        return 'friend'
    p = game.player
    kn = getattr(p, 'knight', None) or {}
    if c['kingdom'] is not None:
        if kn.get('kid') == c['kingdom']:
            return 'friend'
        if kn.get('kid') == c['foe'] or c['hostile']:
            return 'foe'
        try:
            from . import realms as RL
            if RL.favour(game, c['kingdom']) >= RL.FEALTY_FAVOUR:
                return 'friend'
        except Exception:
            pass
        return 'stranger'
    return 'foe' if c['hostile'] else 'stranger'


def set_rel(game, c, r):
    rel_store(game)[str(c['id'])] = r


# ------------------------------------------------------------------ the world map
def signs(game):
    """(x, y, ch, fg) for every camp you can see, and the fire rings left behind."""
    out = []
    p = game.player
    om = game.maps['over']
    night = camping(game)
    px, py = (p.x, p.y) if game.cur == 'over' else game.over_pos
    for c in state(game.world):
        if not om.seen[c['y'] * om.w + c['x']]:
            continue
        st = STYLES[c['style']]
        if c['style'] == 'elf' or c['people'] == 'elf':
            if cheb(c['x'], c['y'], px, py) > 1:
                continue                             # the elves are seen from one cell away only
            out.append((c['x'] - 1, c['y'], '∩', (200, 220, 210)))
            out.append((c['x'] + 1, c['y'], '∩', (200, 220, 210)))
            continue
        left, up, right = st['signs']
        fg = c['fg']
        for dx, dy, ch in ((-1, 0, left), (0, -1, up), (1, 0, right)):
            x, y = c['x'] + dx, c['y'] + dy
            if ch and om.inb(x, y) and D.TILES[om.tile(x, y)].walk and not game.world.settlement_at(x, y):
                out.append((x, y, ch, fg if ch not in ('o', 'h') else (200, 180, 150)))
        if night:
            x, y = c['x'], c['y'] + 1
            if om.inb(x, y) and D.TILES[om.tile(x, y)].walk:
                out.append((x, y, '☼', NIGHT_FG))
    for (x, y), d in game.world.camp_rings.items():
        if om.seen[y * om.w + x] and not at(game, x, y):
            out.append((x, y, 'o', (96, 84, 72)))
    return out


def line(game):
    """The line under the map, by a camp: 'The host of Varn camps here tonight.'"""
    if game.cur != 'over':
        return None
    p = game.player
    c = at(game, p.x, p.y)
    if c is None:
        if (p.x, p.y) in game.world.camp_rings:
            return 'Blackened fire rings and trampled ground: a camp stood here.'
        return None
    if c['siege']:
        return f'{c["name"]}.'
    if c['style'] == 'traders':
        return 'A caravan camps here tonight.'
    return f'{c["name"]} camps here tonight.'


# ------------------------------------------------------------------ going in
def enter(game, c):
    from . import guide as GD
    p = game.player
    if game.cur == 'over':
        game.over_pos = (p.x, p.y)
    if c['map'] not in game.maps:
        game.maps[c['map']] = gen_map(game, c)
    game.cur = c['map']
    m = game.map
    p.x, p.y = m.entry
    r = rel(game, c)
    word = {'friend': 'They know you here.', 'stranger': 'A sentry watches you come.',
            'foe': 'You keep to the shadows.'}[r]
    if c['style'] == 'traders':
        word = 'The carters wave you to the fire.'
    game.msg(f'You come into {c["name"][0].lower() + c["name"][1:] if c["name"].startswith("A ") else c["name"]}. {word}', 'info')
    GD.tip(game, 'camp')
    game.compute_fov()
    game.request = ('save',)
    return 1


# ------------------------------------------------------------------ the camp's map
CW, CH = 64, 36


def gen_map(game, c):
    from .entities import GameMap
    st = c['people'] if c['style'] != 'siege' else c['people']
    siege = c['siege']
    om = game.maps['over']
    land = _ground(game, c['x'], c['y'])
    m = GameMap(c['map'], 'town', c['name'], CW, CH, land)
    m.camp, m.sid, m.hid, m.site, m.signs = c['id'], None, None, None, []
    m.radius = 60
    m.tents, m.cthings, m.tint = [], {}, {}
    rnd = random.Random(c['id'] * 131 + c['day'])
    cx, cy = CW // 2, CH // 2
    night = camping(game)
    foe = rel(game, c) == 'foe'
    m.entry = (1, cy)
    for x in range(0, 8):
        m.set(x, cy, D.PATH)
    if st == 'host' or c['style'] == 'siege' and st not in ('dwarf', 'elf'):
        _host(game, c, m, rnd, cx, cy, night, siege)
    elif st == 'dwarf':
        _dwarf(game, c, m, rnd, cx, cy, night)
    elif st == 'elf':
        _elf(game, c, m, rnd, cx, cy, night)
    elif st == 'gorvash':
        _gorvash(game, c, m, rnd, cx, cy, night)
    elif st == 'sea':
        _sea(game, c, m, rnd, cx, cy, night)
    elif st == 'riders':
        _riders(game, c, m, rnd, cx, cy, night)
    else:
        _traders(game, c, m, rnd, cx, cy, night)
    _folk(game, c, m, rnd, night, foe)
    m.lights = list(getattr(m, 'glows', []))
    for i in range(len(m.seen)):
        m.seen[i] = 1
    m._look = None
    return m


def _ground(game, x, y):
    from . import homes as HM
    land = HM.land_at(game, x, y)
    return {'long': D.SNOW, 'clay': D.SAND}.get(land, D.GRASS)


def _fire(m, x, y, night, big=False):
    m.set(x, y, D.FIREPIT if night else D.COLDPIT)
    if night:
        m.__dict__.setdefault('glows', []).append((x, y, (255, 150, 60), 6 if big else 4))
    m.cthings[(x, y)] = 'fire'


def tent(m, x, y, w, h, kind, fg, door='s', wall=None, floor=None):
    """A tent: cloth walls in the camp's colour, a flap for a door; its inside cells kept for the furniture."""
    wall = wall if wall is not None else D.CLOTH
    floor = floor if floor is not None else D.FLOOR
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            if not m.inb(xx, yy):
                continue
            edge = yy in (y, y + h - 1) or xx in (x, x + w - 1)
            m.set(xx, yy, wall if edge else floor)
            if edge and wall == D.CLOTH:
                m.tint[(xx, yy)] = ('▒', fg)
    dx, dy = {'s': (x + w // 2, y + h - 1), 'n': (x + w // 2, y), 'e': (x + w - 1, y + h // 2), 'w': (x, y + h // 2)}[door]
    if m.inb(dx, dy):
        m.set(dx, dy, D.ODOOR)
        m.tint.pop((dx, dy), None)
    inside = [(xx, yy) for yy in range(y + 1, y + h - 1) for xx in range(x + 1, x + w - 1)]
    m.tents.append(dict(kind=kind, box=(x, y, w, h), door=(dx, dy), inside=inside))
    return inside


def _put(m, cells, tile, thing=None):
    for c in cells:
        if m.inb(*c) and D.TILES[m.tile(*c)].walk and m.tile(*c) != D.ODOOR:
            m.set(c[0], c[1], tile)
            if thing:
                m.cthings[c] = thing
            return c
    return None


def _furnish(m, t, kind, rnd):
    """What stands in each kind of tent."""
    ins = t['inside']
    inner = [c for c in ins if c != (t['door'][0], t['door'][1] - 1) and c != (t['door'][0], t['door'][1] + 1)]
    if kind == 'soldiers':
        _put(m, inner[:1], D.BED)
        _put(m, inner[-1:], D.BED)
        _put(m, inner[len(inner) // 2:len(inner) // 2 + 1], D.BARREL)
    elif kind == 'marshal':
        _put(m, inner[len(inner) // 2:], D.TABLE, 'orders')
        _put(m, inner[:1], D.BED)
        _put(m, inner[-1:], D.CHEST, 'chest')
    elif kind == 'stores':
        for c in inner[::2]:
            _put(m, [c], D.CRATES, 'stores')
    elif kind == 'wounded':
        for c in inner[::3]:
            _put(m, [c], D.COT)
    elif kind == 'chapel':
        _put(m, inner[len(inner) // 2:], D.ALTAR)
        _put(m, inner[:1], D.BANNER)
    elif kind == 'smith':
        _put(m, inner[len(inner) // 2:], D.ANVIL)
    elif kind == 'bower':
        _put(m, inner[:1], D.BED)


def _pen(m, x, y, w, h):
    """The prisoners' pen: a fence with a gate you can open."""
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            if yy in (y, y + h - 1) or xx in (x, x + w - 1):
                m.set(xx, yy, D.FENCE)
    gate = (x + w // 2, y + h - 1)
    m.set(gate[0], gate[1], D.CAGE)
    m.cthings[gate] = 'pen'
    m.pen = [(xx, yy) for yy in range(y + 1, y + h - 1) for xx in range(x + 1, x + w - 1)]
    return gate


def _ring(m, x0, y0, x1, y1, tile, gate_w=True):
    for x in range(x0, x1 + 1):
        m.set(x, y0, tile)
        m.set(x, y1, tile)
    for y in range(y0, y1 + 1):
        m.set(x0, y, tile)
        m.set(x1, y, tile)
    cy = (y0 + y1) // 2
    m.set(x0, cy, D.PATH)
    m.gate = (x0, cy)


def _host(game, c, m, rnd, cx, cy, night, siege):
    fg = c['fg']
    _ring(m, 8, 3, CW - 6, CH - 4, D.PALISADE)
    rows = []
    for row_y in (6, 12, 21, 27):
        for x in range(13, CW - 14, 9):
            rows.append((x, row_y))
    kinds = ['marshal', 'stores', 'wounded', 'chapel', 'smith'] + ['soldiers'] * 20
    for (x, y), kind in zip(rows, kinds):
        w, h = (7, 5) if kind == 'marshal' else (6, 4)
        t = tent(m, x, y, w, h, kind, fg, 's' if y < cy else 'n')
        _furnish(m, m.tents[-1], kind, rnd)
        if kind == 'marshal':
            for gx in (m.tents[-1]['door'][0] - 1, m.tents[-1]['door'][0] + 1):
                gy = m.tents[-1]['door'][1] + (1 if y < cy else -1)
                m.set(gx, gy, D.BANNER) if gx == m.tents[-1]['door'][0] - 1 else None
    for i, (x, y) in enumerate(rows[5:]):                      # a fire for each pair of tents
        if i % 2 == 0:
            fy = y + (4 if y < cy else -1) + (1 if y < cy else -1)
            _fire(m, x + 7, fy if m.inb(x + 7, fy) else y, night)
    m.set(CW - 10, cy - 2, D.CART)                             # the quartermaster's wagons
    m.set(CW - 10, cy + 2, D.CART)
    m.quarter = (CW - 11, cy)
    _pen(m, CW - 16, cy - 2, 5, 5)
    for x in range(10, 16):                                    # the horse lines
        m.set(x, CH - 6, D.FENCE)
    if siege:
        for x in range(12, CW - 10, 10):
            m.set(x, 1, D.ENGINE)


def _dwarf(game, c, m, rnd, cx, cy, night):
    for y in (2, CH - 3):                                      # the ditch
        for x in range(6, CW - 3):
            m.set(x, y, D.WATER)
    for x in (6, CW - 4):
        for y in range(2, CH - 2):
            m.set(x, y, D.WATER)
    m.set(6, cy, D.PLANK)
    _ring(m, 8, 4, CW - 6, CH - 5, D.SHIELDWALL)
    fg = (150, 150, 160)
    kinds = ['marshal', 'stores', 'wounded', 'chapel'] + ['soldiers'] * 20
    i = 0
    for y in range(7, CH - 10, 6):
        for x in range(12, CW - 12, 8):
            if abs(x - cx) < 5 and abs(y - cy) < 4:
                continue
            k = kinds[i] if i < len(kinds) else 'soldiers'
            tent(m, x, y, 6, 4, k, fg, 's')
            _furnish(m, m.tents[-1], k, rnd)
            i += 1
    m.set(cx, cy, D.ANVIL)                                     # the field forge in the middle
    m.cthings[(cx, cy)] = 'forge'
    m.__dict__.setdefault('glows', []).append((cx, cy, (255, 140, 50), 5))
    for x, y in ((10, 6), (CW - 8, 6), (10, CH - 7), (CW - 8, CH - 7)):
        m.set(x, y, D.FIREPIT)                                 # braziers at the corners, day and night
        m.glows.append((x, y, (255, 150, 60), 3))
    m.quarter = (cx + 3, cy)
    m.set(cx + 4, cy - 1, D.CART)
    _pen(m, CW - 15, CH - 10, 5, 4)


def _elf(game, c, m, rnd, cx, cy, night):
    for y in range(CH):
        for x in range(CW):
            if rnd.random() < .22 and abs(x - cx) + abs(y - cy) > 4:
                m.set(x, y, D.TREE)
    for x in range(0, cx):
        m.set(x, cy, D.GRASS)
    kinds = ['marshal', 'wounded', 'stores'] + ['bower'] * 12
    spots = [(cx + rnd.randint(-24, 20), cy + rnd.randint(-13, 10)) for _ in range(60)]
    k = 0
    for x, y in spots:
        if k >= len(kinds) or not (2 < x < CW - 8 and 2 < y < CH - 6):
            continue
        if any(abs(x - t['box'][0]) < 8 and abs(y - t['box'][1]) < 6 for t in m.tents):
            continue
        tent(m, x, y, 5, 4, kinds[k], (110, 170, 110), 's', wall=D.CLOTH, floor=D.GRASS)
        for cc in [cc for cc, v in m.tint.items() if v[0] == '▒']:
            m.tint[cc] = ('♣', (110, 170, 110))                 # walls of woven leaves
        _furnish(m, m.tents[-1], 'bower' if kinds[k] == 'bower' else kinds[k], rnd)
        k += 1
    m.set(cx, cy, D.WATER)                                      # the moon-well
    m.cthings[(cx, cy)] = 'well'
    m.quarter = (cx + 2, cy)
    _pen(m, 4, 3, 5, 4)


def _gorvash(game, c, m, rnd, cx, cy, night):
    for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
        _fire(m, cx + dx, cy + dy, True, big=True)              # one great fire, day and night
    m.set(cx + 4, cy - 2, D.STATUE)                              # the skull pole
    m.tint[(cx + 4, cy - 2)] = ('¥', (220, 210, 190))
    for x in (cx - 4, cx + 6):
        m.set(x, cy + 3, D.DRUM)
    kinds = ['marshal', 'stores'] + ['soldiers'] * 16
    k = 0
    for _ in range(200):
        if k >= len(kinds):
            break
        a = rnd.random() * 6.28
        r = rnd.randint(8, 15)
        import math
        x, y = int(cx + math.cos(a) * r * 1.8), int(cy + math.sin(a) * r)
        if not (2 < x < CW - 8 and 2 < y < CH - 6) or any(abs(x - t['box'][0]) < 7 and abs(y - t['box'][1]) < 5 for t in m.tents):
            continue
        tent(m, x, y, 5, 4, kinds[k], (150, 110, 80), rnd.choice('nsew'))
        _furnish(m, m.tents[-1], kinds[k], rnd)
        k += 1
    for y in range(3, 8):                                        # the wolf pens
        m.set(CW - 9, y, D.FENCE)
        m.set(CW - 4, y, D.FENCE)
    for x in range(CW - 9, CW - 3):
        m.set(x, 3, D.FENCE)
        m.set(x, 7, D.FENCE)
    m.set(cx - 6, cy - 4, D.CAGE)
    m.cthings[(cx - 6, cy - 4)] = 'pen'
    m.pen = [(cx - 6, cy - 3)]
    m.quarter = (cx - 3, cy)


def _sea(game, c, m, rnd, cx, cy, night):
    for y in range(CH):
        for x in range(CW - 12, CW):
            m.set(x, y, D.WATER)
        for x in range(CW - 16, CW - 12):
            m.set(x, y, D.SAND)
    for i, y in enumerate(range(4, CH - 6, 8)):                  # the longships drawn up on the strand: the wall
        for x in range(CW - 22, CW - 11):
            for yy in (y, y + 3):
                m.set(x, yy, D.PLANK if x not in (CW - 22, CW - 12) else D.CLOTH)
            for yy in (y + 1, y + 2):
                m.set(x, yy, D.CLOTH if x in (CW - 22, CW - 12) else D.PLANK)
        for x in range(CW - 22, CW - 11):
            for yy in (y, y + 3):
                m.tint[(x, yy)] = ('▬', (140, 100, 60))
        tent(m, CW - 30, y, 6, 4, 'soldiers' if i else 'marshal', (180, 160, 120), 'w')     # a sail over the oars
        _furnish(m, m.tents[-1], 'soldiers' if i else 'marshal', rnd)
    _fire(m, cx - 6, cy, True, big=True)                          # the mead fire, the ring of shields round it
    for dx, dy in ((-3, 0), (3, 0), (0, -2), (0, 2), (-2, -1), (2, 1), (-2, 1), (2, -1)):
        m.set(cx - 6 + dx, cy + dy, D.BARREL)
        m.tint[(cx - 6 + dx, cy + dy)] = ('o', (170, 150, 110))
    m.set(cx - 2, cy + 5, D.CRATES)                              # the plunder heap
    m.cthings[(cx - 2, cy + 5)] = 'stores'
    _pen(m, 12, 4, 5, 5)
    m.quarter = (cx - 8, cy + 3)


def _riders(game, c, m, rnd, cx, cy, night):
    import math
    _fire(m, cx, cy, night, big=True)
    kinds = ['marshal', 'stores'] + ['soldiers'] * 8
    for i, k in enumerate(kinds):
        a = i / len(kinds) * 6.28
        x, y = int(cx + math.cos(a) * 16) - 2, int(cy + math.sin(a) * 9) - 2
        door = 'w' if math.cos(a) > .5 else 'e' if math.cos(a) < -.5 else ('n' if math.sin(a) > 0 else 's')
        tent(m, x, y, 5, 5, k, (200, 170, 120), door)
        m.set(x + 2, y + 2, D.FIREPIT if night else D.COLDPIT)  # the hearth in the middle
        _furnish(m, m.tents[-1], k, rnd)
    m.quarter = (cx + 3, cy)
    _pen(m, 3, 2, 5, 4)


def _traders(game, c, m, rnd, cx, cy, night):
    import math
    _fire(m, cx, cy, True)
    m.cthings[(cx, cy)] = 'traders_fire'
    for i in range(8):
        a = i / 8 * 6.28
        x, y = int(cx + math.cos(a) * 7), int(cy + math.sin(a) * 4)
        m.set(x, y, D.CART)
        m.tint[(x, y)] = ('Θ', (200, 170, 120))
    m.quarter = (cx + 2, cy)


def _folk(game, c, m, rnd, night, foe):
    """Who is in the camp: as folk you can talk to (friend, stranger) or as foes asleep in their tents (foe)."""
    from .entities import make_npc, make_monster
    from .towns import town_names
    names = town_names('dwarf' if c['people'] == 'dwarf' else 'human')
    fg = c['fg']
    lvl = max(3, game.world.danger_at(c['x'], c['y']) + 2)
    keys = [k for k in TROOPS.get(c['people'], TROOPS['host']) if k in D.MONSTERS] or ['soldier']
    if 'soldier' not in D.MONSTERS:
        keys = [k for k in keys if k in D.MONSTERS] or ['bandit']

    def free(cells):
        cs = [cc for cc in cells if m.inb(*cc) and D.TILES[m.tile(*cc)].walk and not m.mon_at(*cc)]
        return rnd.choice(cs) if cs else None

    def person(name, role, cells, sleep=False):
        spot = free(cells)
        if spot is None:
            return None
        if foe:
            mon = make_monster(game, rnd.choice(keys), spot[0], spot[1], lvl)
            mon.awake = not sleep
            mon.camp = c['id']
            m.mons.append(mon)
            return mon
        n = make_npc(game, name, role, fg if role != 'camp_trader' else '#e0c890', spot[0], spot[1], True)
        n.camp = c['id']
        m.mons.append(n)
        return n

    gate = getattr(m, 'gate', m.entry)
    ring = [(gate[0] + dx, gate[1] + dy) for dx in (1, 2) for dy in (-2, -1, 1, 2)]
    if c['style'] == 'traders':
        person(f'{names.pop()} the Caravan Master', 'camp_trader', [m.quarter])
        for _ in range(3):
            person('A carter', 'camp_soldier', [(m.quarter[0] + dx, m.quarter[1] + dy) for dx in range(-5, 5) for dy in range(-3, 4)])
        return
    for _ in range(STYLES[c['style']]['sentries']):
        s = person('A sentry', 'camp_sentry', ring)
        if s is not None and not foe:
            s.stay = True
    for t in m.tents:
        k = t['kind']
        if k == 'marshal':
            person({'gorvash': 'The warchief', 'sea': 'The jarl', 'riders': 'The khan', 'elf': 'The warden'}.get(
                c['people'], f'Marshal {names.pop()}'), 'camp_marshal', t['inside'])
            for d in ((-1, 0), (1, 0)):
                person('A guard', 'camp_sentry', [(t['door'][0] + d[0], t['door'][1] + d[1] + (1 if t['door'][1] < CH // 2 else -1))])
        elif k == 'wounded':
            person(f'{names.pop()} the Healer', 'camp_healer', t['inside'])
            for _ in range(2):
                person('A wounded man', 'camp_wounded', t['inside'], sleep=True)
        elif k == 'chapel':
            person('A priest of the host', 'camp_priest', t['inside'])
        elif k == 'smith':
            person(f'{names.pop()} the Smith', 'camp_smith', t['inside'])
        elif k in ('soldiers', 'bower'):
            if night:
                for _ in range(2):
                    person('A sleeping soldier', 'camp_soldier', t['inside'], sleep=True)
            elif rnd.random() < .4:
                person('A soldier', 'camp_soldier', t['inside'])
    if getattr(m, 'quarter', None) and not foe:
        person(f'{names.pop()} the Quartermaster', 'camp_quarter', [m.quarter])
    elif getattr(m, 'quarter', None):
        person('A guard', 'camp_sentry', [m.quarter])
    if not night:                                       # by day they are up and about
        for _ in range(5):
            person('A soldier', 'camp_soldier', [(x, y) for x in range(10, CW - 10) for y in range(4, CH - 5)])
    for cc in getattr(m, 'pen', [])[:3]:
        if not m.mon_at(*cc) and D.TILES[m.tile(*cc)].walk:
            n = make_npc(game, 'A captive', 'camp_captive', '#c0b8a8', cc[0], cc[1], True)
            n.camp = c['id']
            m.mons.append(n)


# ------------------------------------------------------------------ in the camp
def camp_of(game, m=None):
    m = m or game.map
    cid = getattr(m, 'camp', None)
    return get(game, cid) if cid is not None else None


def talk(game, npc):
    from . import events as EV
    from .money import fmt
    c = camp_of(game)
    if c is None:
        game.say(npc, '"Move along."')
        return
    r = rel(game, c)
    role = npc.role
    p = game.player
    if role == 'camp_trader':
        opts = [('Trade', 'trade'), ('Ask about the road', 'news'), ('Ride with them tomorrow', 'ride'),
                ('Sleep by their fire', 'sleep'), ('Nothing', 'leave')]
        EV.ask(game, 'camp_trader', npc.name, '"Sit, eat, be welcome. We are bound on at first light."', opts, cid=c['id'])
        return
    if role == 'camp_captive':
        game.say(npc, '"Get me out of here. The gate, the gate!"')
        return
    if role == 'camp_sentry' and r == 'stranger' and str(c['id']) not in p.camp_let:
        gift = 20 * 100
        opts = [(f'Give him a gift: {fmt(gift)}', 'gift' if p.gold >= gift else None)]
        if p.rep.get('crown', 0) >= 10:
            opts.append(('Give a good word: your name is known', 'word'))
        EV.ask(game, 'camp_sentry', 'A sentry', '"Halt. Who are you, and what do you want in this camp?"',
               opts + [('Go away', 'leave')], cid=c['id'], gift=gift)
        return
    if role in ('camp_soldier', 'camp_wounded', 'camp_sentry'):
        game.say(npc, random.choice(['"Cold night. They say we march at dawn."', '"Keep your hands where I see them."',
                                     '"The marshal is in the big tent."', '"My feet are worn to the bone."']))
        return
    if r == 'stranger' and role != 'camp_quarter':
        game.say(npc, '"I do not know you. The quartermaster may deal with you; I will not."')
        return
    if r == 'stranger' and str(c['id']) not in p.camp_let:
        game.say(npc, '"Who let you in? See the sentry first."')
        return
    if role == 'camp_quarter':
        return quarter(game, npc, c)
    if role == 'camp_smith':
        n, cost = game.repair_all(dry=True)
        if not n:
            game.say(npc, '"Your gear is sound."')
            return
        game.repair_all(discount=.2)
        return
    if role == 'camp_healer':
        gift = 15 * 100
        s = game.stats()
        if p.life >= s['max_life'] and not p.poison:
            game.say(npc, '"You are whole. Others need me more."')
            return
        if p.gold < gift:
            game.say(npc, '"A small gift for the wounded, and I will see to you."')
            return
        p.gold -= gift
        p.life, p.poison = s['max_life'], None
        game.msg(f'The healer binds your wounds for a small gift ({fmt(gift)}) to the wounded.', 'good')
        return
    if role == 'camp_priest':
        game.say(npc, '"May the gods hold your shield arm steady."')
        return
    if role == 'camp_marshal':
        opts = [('Ask how the war goes', 'news'), ('Sign on for the battle', 'sign'), ('Nothing', 'leave')]
        EV.ask(game, 'camp_marshal', npc.name, f'"{_war_word(game, c)}"', opts, cid=c['id'])
        return
    game.say(npc, '"Yes?"')


def _war_word(game, c):
    R = getattr(game.world, 'realm', None)
    try:
        war = next(w_ for w_ in R.wars if c['kingdom'] in (w_['a'], w_['b']))
        sc = war['score'] * (1 if war['a'] == c['kingdom'] else -1)
        foe = R.kingdoms[c['foe']].short if c['foe'] is not None else 'the enemy'
        how = 'goes well for us' if sc > 0 else 'goes against us' if sc < 0 else 'hangs in the balance'
        return f'The war with {foe} {how}. We march on at first light.'
    except Exception:
        return 'We march on at first light. Where, is not for you to know.'


def quarter(game, npc, c):
    """The quartermaster buys at war prices: food, arms, tools and timber dear."""
    from . import events as EV
    from .money import fmt
    p = game.player
    opts = []
    for g, q in sorted(p.cargo.items()):
        if q > 0 and g in D.GOODS:
            each = war_price(game, c, g)
            opts.append((f'Sell {q} {D.GOODS[g]["name"]}: {fmt(each * q)}', f'sell:{g}'))
    if not opts:
        game.say(npc, '"Bring me grain, ale, arms or timber, and I pay better than any market. A war eats everything."')
        return
    EV.ask(game, 'camp_quarter', npc.name, '"A war eats everything. What have you got?"', opts[:20] + [('Nothing', 'leave')],
           cid=c['id'])


WAR_GOODS = {'grain': 1.5, 'ale': 1.4, 'arms': 1.6, 'tools': 1.4, 'timber': 1.3, 'medicine': 1.6, 'fish': 1.3}


def war_price(game, c, g):
    from . import economy as ECO
    w = game.world
    s = min(w.settlements, key=lambda s_: cheb(s_.x, s_.y, c['x'], c['y']))
    return max(1, round(ECO.sell_price(s, g) * WAR_GOODS.get(g, 1.1)))


def r_quarter(game, choice, ctx):
    c = get(game, ctx['cid'])
    if not c or not choice or not choice.startswith('sell:'):
        return
    g = choice[5:]
    p = game.player
    q = p.cargo.get(g, 0)
    if not q:
        return
    pay = war_price(game, c, g) * q
    del p.cargo[g]
    p.cost_basis.pop(g, None) if isinstance(getattr(p, 'cost_basis', None), dict) else None
    p.gold += pay
    from . import tally as TY
    TY.add(game, 'earned_trade', pay)
    from .money import fmt
    game.msg(f'The quartermaster counts out {fmt(pay)} for your {D.GOODS[g]["name"].lower()}: war prices.', 'good')


def r_sentry(game, choice, ctx):
    c = get(game, ctx['cid'])
    p = game.player
    if not c:
        return
    if choice == 'gift' and p.gold >= ctx['gift']:
        p.gold -= ctx['gift']
        p.camp_let[str(c['id'])] = True
        game.msg('The sentry pockets the coin and nods you through: "The quartermaster. Nowhere else."', 'info')
    elif choice == 'word':
        p.camp_let[str(c['id'])] = True
        game.msg('The sentry has heard your name. "Go on, then. The quartermaster."', 'info')


def r_marshal(game, choice, ctx):
    c = get(game, ctx['cid'])
    if not c:
        return
    if choice == 'news':
        game.msg(_war_word(game, c), 'info')
    elif choice == 'sign':
        p = game.player
        kn = getattr(p, 'knight', None)
        R = getattr(game.world, 'realm', None)
        if not kn or kn.get('kid') != c['kingdom'] or R is None:
            game.msg('"We take only sworn men into the line. Swear to the king first."', 'info')
            return
        from . import realmjobs as RJ
        RJ.levy(game, R.kingdoms[c['kingdom']], R.kingdoms[c['foe']])
        game.msg('The marshal writes your name on the roll. Your place in the battle is in your journal.', 'good')


def r_trader(game, choice, ctx):
    c = get(game, ctx['cid'])
    if not c:
        return
    p = game.player
    if choice == 'trade':
        sid = c.get('origin')
        if sid is None:
            game.msg('They have sold out.', 'info')
            return
        game.request = ('market', sid)
        game.trading_at = sid
    elif choice == 'news':
        from . import news as NW
        told = NW.tell(game, far=True) if hasattr(NW, 'tell') else None
        if not told:
            game.msg('"The roads are quiet. Salt is dear in the north, they say."', 'info')
    elif choice == 'ride':
        p.buffs = [b for b in p.buffs if b[0] != 'safe_road'] + [['safe_road', 1, D.DAY_LEN * 2, 'A safe road']]
        game.msg('You ride with the caravan in the morning: no one troubles a road with so many wagons on it. (A safe road)', 'good')
    elif choice == 'sleep':
        sleep_by_fire(game, c)


def sleep_by_fire(game, c):
    """A night by the caravan's fire: safe, mostly. Sometimes robbers come."""
    from .entities import make_monster
    p = game.player
    s = game.stats()
    game.end_turn(D.DAY_LEN // 3, True)
    p.life, p.mana, p.stamina = s['max_life'], s['max_mana'], s['max_stamina']
    from . import trees as TT
    TT.rested(game)
    if random.random() < .3 and not rel_store(game).get(f'robbed{c["id"]}'):
        rel_store(game)[f'robbed{c["id"]}'] = 'yes'
        m = game.map
        lvl = max(2, game.world.danger_at(c['x'], c['y']) + 1)
        for i in range(3):
            x, y = 2 + i, CH // 2 - 1 + i
            mon = make_monster(game, 'bandit', x, y, lvl)
            mon.awake = True
            mon.robber = c['id']
            m.mons.append(mon)
        game.msg('Shouts in the dark: robbers on the wagons! The carters grab their cudgels.', 'bad')
        return
    game.msg('You sleep by the caravan\'s fire, among the snoring carters. A quiet night.', 'good')


def after_turn(game):
    """In a camp: a foe seen wakes the whole camp; robbers beaten, the trader remembers you."""
    m = game.map
    c = camp_of(game, m)
    if c is None:
        return
    if not c['alarm'] and rel(game, c) == 'foe':
        p = game.player
        if any(o.awake and not o.is_npc and getattr(o, 'camp', None) == c['id'] and game.visible(o.x, o.y)
               and cheb(o.x, o.y, p.x, p.y) <= 6 for o in m.mons):
            c['alarm'] = True
            for o in m.mons:
                if getattr(o, 'camp', None) == c['id'] and not o.is_npc:
                    o.awake = True
            game.msg('A horn sounds: the whole camp wakes!', 'bad')
    rob = [o for o in m.mons if getattr(o, 'robber', None) == c['id']]
    if rel_store(game).get(f'robbed{c["id"]}') == 'yes' and not any(o.hp > 0 for o in rob):
        rel_store(game)[f'robbed{c["id"]}'] = 'beaten'
        if c.get('origin') is not None:
            rel_store(game)[f'trader{c["origin"]}'] = game.day
            try:
                game.world.settlements[c['origin']].rep += 10          # its market's prices are kinder to you
            except (IndexError, AttributeError, TypeError):
                pass
        game.msg('The robbers are driven off. The caravan master grips your hand: "You will have my best price, '
                 'in my town, for as long as I live."', 'good')


def trader_friend(game, sid):
    """You beat off robbers from a caravan of this town: its market gives you a better price."""
    return f'trader{sid}' in rel_store(game)


# ------------------------------------------------------------------ as a foe, by night
def bump(game, x, y):
    """Walking into a thing of the camp: the orders, the stores, the pen, a fire, a chest, a tent's cloth."""
    m = game.map
    c = camp_of(game, m)
    if c is None:
        return None
    what = m.cthings.get((x, y))
    foe = rel(game, c) == 'foe'
    if what == 'traders_fire':
        sleep_by_fire(game, c)
        return 1
    if not foe:
        if what in ('orders', 'stores', 'pen', 'chest'):
            game.msg({'orders': 'The marshal\'s map and orders. Not for you to read.',
                      'stores': 'Crates of flour, salt pork, ale. The quartermaster keeps count.',
                      'pen': 'The prisoners\' pen. A guard watches it.',
                      'chest': 'The marshal\'s chest, locked.'}[what], 'info')
            return 0
        return None
    if what in c['done']:
        game.msg('Done already.', 'info')
        return 0
    if what == 'orders':
        return _deed(game, c, 'orders', 'You roll up the marshal\'s orders and slip them under your coat.', 2)
    if what == 'stores':
        for cc in [cc for cc, v in m.cthings.items() if v == 'stores']:
            m.set(cc[0], cc[1], D.BURNING)
        m.__dict__.setdefault('glows', []).append((x, y, (255, 120, 40), 6))
        from . import heard as HL
        HL.make(game, x, y, 6)
        return _deed(game, c, 'stores', 'The stores catch: flour, pork and ale go up in a roar of fire.', 3)
    if what == 'pen':
        for o in [o for o in m.mons if o.is_npc and o.role == 'camp_captive']:
            m.mons.remove(o)
        m.set(x, y, D.FENCE)
        return _deed(game, c, 'pen', 'You lift the bar of the pen. The captives slip away into the dark.', 1)
    if what == 'chest':
        from . import economy as ECO  # noqa: F401
        coin = random.randint(30, 120) * 100
        game.player.gold += coin
        from .money import fmt
        m.cthings.pop((x, y))
        return _deed(game, c, 'chest', f'The marshal\'s chest: {fmt(coin)} in pay for the host.', 1)
    if m.tile(x, y) == D.CLOTH:
        from . import events as EV
        EV.ask(game, 'camp_burn', 'A tent', 'The cloth is dry and the fire is near.',
               [('Set the tent burning', 'burn'), ('Leave it', 'leave')], cid=c['id'], at=(x, y))
        return 0
    return None


def r_burn(game, choice, ctx):
    if choice != 'burn':
        return
    c = get(game, ctx['cid'])
    m = game.map
    if not c:
        return
    x, y = ctx['at']
    t = next((t for t in m.tents if t['box'][0] <= x < t['box'][0] + t['box'][2] and t['box'][1] <= y < t['box'][1] + t['box'][3]), None)
    cells = [(x, y)] if t is None else [(xx, yy) for yy in range(t['box'][1], t['box'][1] + t['box'][3])
                                         for xx in range(t['box'][0], t['box'][0] + t['box'][2]) if m.tile(xx, yy) == D.CLOTH]
    for cc in cells:
        m.set(cc[0], cc[1], D.BURNING)
        m.tint.pop(cc, None)
    m.__dict__.setdefault('glows', []).append((x, y, (255, 120, 40), 5))
    from . import heard as HL
    HL.make(game, x, y, 6)
    _deed(game, c, f'tent{x},{y}', 'The tent goes up like straw.', 1)


def _deed(game, c, what, line, cut):
    """Something done against a host: it fights weaker in its battle."""
    c['done'].append(what)
    set_rel(game, c, 'foe')
    wd = next((x for x in game.world.wanderers if x.id == c['wd']), None)
    if wd is not None and getattr(wd, 'strength', 0):
        wd.strength = max(1, wd.strength - cut)
    game.msg(line + (' The host will be the weaker for it.' if wd is not None and c['kind'] in ('host', 'warband') else ''), 'good')
    from . import tally as TY
    TY.add(game, 'camp_deeds')
    return 1


def init():
    from . import events as EV
    EV.RESOLVERS.update({'camp_quarter': r_quarter, 'camp_sentry': r_sentry, 'camp_marshal': r_marshal,
                         'camp_trader': r_trader, 'camp_burn': r_burn})
