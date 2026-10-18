"""The seats of the lesser houses and the places of the other powers, each a world tile with its own small map.

A poor house has a fortified farm in a palisade, a middling one a stone tower house inside a low wall, a rich one a
walled manor with hall, chapel and stables, everything inside its wall. Inside: the head of the house, the heir, a
few guards in the house's colours and servants. A fallen house leaves a burnt or empty ruin.
The raiders' halls (guest right holds under the chief's roof), the holy order's keep, the forts of the Border Watch,
a mercenary camp, a witch's circle on the moor, a peasants' camp and the pretender's hidden court."""
import random

from . import data as D
from .data import GRASS, FLOOR, WALL, DOOR, PATH, TREE, ALTAR, BED, TABLE, FIELD, WELL, ROCK, PLANK, BARREL
from .entities import GameMap, make_npc, make_monster
from .worldgen import cheb

LOOK = {'hall': ('Æ', (214, 176, 120)), 'orderkeep': ('╪', (240, 236, 216)), 'watchfort': ('╫', (160, 168, 186)),
        'merccamp': ('¶', (226, 184, 90)), 'circle': ('○', (176, 146, 210)), 'rising': ('‼', (210, 178, 110)),
        'exile': ('º', (220, 200, 150)), 'seat': ('╥', (220, 200, 150))}
SEAT_GLYPH = {'farm': '╓', 'tower': '╥', 'manor': '╦'}
KINDS = set(LOOK)


def glyph(site):
    if site.kind == 'seat':
        if getattr(site, 'fallen', False):
            return ':', (150, 140, 126)
        return SEAT_GLYPH.get(getattr(site, 'style', 'tower'), '╥'), house_fg(site)
    if getattr(site, 'empty', False) or getattr(site, 'burnt', False):
        return LOOK[site.kind][0], (120, 112, 100)
    return LOOK[site.kind]


def house_fg(site):
    from . import foraging as FG
    game = FG.GAME
    R = getattr(game.world, 'realm', None) if game else None
    if R is None or getattr(site, 'house', None) is None:
        return LOOK['seat'][1]
    return R.houses[site.house].arms[1]


def is_seat(site):
    return site is not None and site.kind in KINDS


def describe(game, site):
    """A line for the look command and the place line under the map."""
    R = game.world.realm
    if site.kind == 'seat':
        h = R.houses[site.house]
        if getattr(site, 'fallen', False):
            return f'{site.name}, the {"burnt" if getattr(site, "burnt", False) else "empty"} seat of the fallen House {h.name}.'
        what = {'farm': 'fortified farm', 'tower': 'tower house', 'manor': 'walled manor'}[site.style]
        return f'{site.name}, the {what} of House {h.name}.'
    if site.kind == 'hall':
        from . import powers as PW
        rd = PW.raiders(game.world)[site.raider]
        return f'{site.name}: {rd["name"]}.'
    return site.name + '.'


# ------------------------------------------------------------------ helpers
def _new(site, w, h, fill=GRASS):
    m = GameMap(site.map_key, 'town', site.name, w, h, fill)
    m.radius, m.sid, m.hid, m.signs = 60, None, None, []
    m.site = site.id
    m.lights = []
    return m


def rect(m, x0, y0, x1, y1, wall=WALL, floor=FLOOR):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            m.set(x, y, wall if y in (y0, y1) or x in (x0, x1) else floor)
    return [(x, y) for y in range(y0 + 1, y1) for x in range(x0 + 1, x1)]


def ring(m, x0, y0, x1, y1, wall):
    for x in range(x0, x1 + 1):
        m.set(x, y0, wall)
        m.set(x, y1, wall)
    for y in range(y0, y1 + 1):
        m.set(x0, y, wall)
        m.set(x1, y, wall)


def door(m, x, y, t=DOOR):
    m.set(x, y, t)


def free(m, cells):
    return [c for c in cells if D.TILES[m.tile(*c)].walk and not m.mon_at(*c)]


def folk(game, m, cells, names, job, fg='#a8aab4', role='villager', n=1, ch='☺'):
    from .towns import townsfolk
    out = []
    cs = free(m, cells)
    random.shuffle(cs)
    for c in cs[:n]:
        out.append(townsfolk(game, m, [c], c, names, job, fg=fg, role=role, ch=ch))
    return out


def finish(m, entry):
    from .towns import embed
    m.entry = entry
    for i in range(len(m.seen)):
        m.seen[i] = 1
    return embed(m, 96, 62)


def ruin(m, x0, y0, x1, y1, burnt):
    """What is left when a house falls: broken walls, ash, the doors gone."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            t = m.tile(x, y)
            if t in (WALL, ROCK, D.PALISADE) and random.random() < .35:
                m.set(x, y, D.RUBBLE if random.random() < .6 else GRASS)
            elif t in (DOOR, D.ODOOR):
                m.set(x, y, FLOOR)
            elif t in (FLOOR, PLANK) and burnt and random.random() < .6:
                m.set(x, y, D.GRIT)
            elif t in (BED, TABLE, BARREL) and random.random() < .7:
                m.set(x, y, D.GRIT if burnt else FLOOR)


# ------------------------------------------------------------------ the seats of the lesser houses
def gen_map(game, site):
    fn = {'seat': seat_map, 'hall': hall_map, 'orderkeep': keep_map, 'watchfort': fort_map, 'merccamp': camp_map,
          'circle': circle_map, 'rising': rising_map, 'exile': exile_map}[site.kind]
    return fn(game, site)


def seat_map(game, site):
    R = game.world.realm
    h = R.houses[site.house]
    style = site.style
    fallen = getattr(site, 'fallen', False)
    W, H = (40, 21) if style == 'farm' else (46, 23) if style == 'tower' else (56, 25)
    m = _new(site, W, H)
    m.level = 3
    sy = H // 2
    for x in range(0, 4):
        m.set(x, sy, PATH)
    x0, y0, x1, y1 = 4, 1, W - 3, H - 2
    wall = D.PALISADE if style == 'farm' else ROCK if style == 'tower' else WALL
    ring(m, x0, y0, x1, y1, wall)
    door(m, x0, sy, D.ODOOR)
    for x in range(x0 + 1, x1):
        m.set(x, sy, PATH)
    rooms = {}
    if style == 'farm':
        rooms['hall'] = rect(m, x1 - 13, sy - 4, x1 - 2, sy + 3, WALL, PLANK)
        door(m, x1 - 13, sy)
        rooms['barn'] = rect(m, x0 + 3, y0 + 2, x0 + 12, y0 + 6, WALL, FLOOR)
        door(m, x0 + 7, y0 + 6)
        for x in range(x0 + 3, x0 + 14):
            for y in range(sy + 3, y1 - 1):
                m.set(x, y, FIELD)
        m.set(x1 - 17, sy - 3, WELL)
    elif style == 'tower':
        rooms['hall'] = rect(m, x1 - 12, sy - 5, x1 - 3, sy + 4, ROCK, FLOOR)
        door(m, x1 - 12, sy)
        rooms['barn'] = rect(m, x0 + 3, y0 + 2, x0 + 12, y0 + 6, WALL, PLANK)
        door(m, x0 + 7, y0 + 6)
        rooms['kitchen'] = rect(m, x0 + 3, y1 - 6, x0 + 11, y1 - 2, WALL, PLANK)
        door(m, x0 + 7, y1 - 6)
        m.set(x1 - 16, sy + 3, WELL)
    else:
        rooms['hall'] = rect(m, x1 - 18, sy - 5, x1 - 2, sy + 4, WALL, PLANK)
        door(m, x1 - 18, sy)
        rooms['chapel'] = rect(m, x0 + 15, y0 + 1, x0 + 24, y0 + 6, WALL, FLOOR)
        door(m, x0 + 19, y0 + 6)
        m.set(x0 + 19, y0 + 2, ALTAR)
        rooms['barn'] = rect(m, x0 + 2, y0 + 1, x0 + 12, y0 + 6, WALL, FLOOR)
        door(m, x0 + 7, y0 + 6)
        rooms['kitchen'] = rect(m, x0 + 2, y1 - 6, x0 + 11, y1 - 1, WALL, PLANK)
        door(m, x0 + 6, y1 - 6)
        for x in range(x0 + 14, x0 + 26):
            for y in range(sy + 3, y1 - 1):
                m.set(x, y, FIELD if (x + y) % 3 else GRASS)
        m.set(x0 + 28, sy - 3, D.FOUNTAIN)
    hall = rooms['hall']
    hx = max(c[0] for c in hall)
    for c in hall:
        if c[0] == hx and c[1] == sy:
            m.set(c[0], c[1], D.HIGHSEAT)
        elif c[0] in (hx - 3, hx - 5) and abs(c[1] - sy) == 1:
            m.set(c[0], c[1], TABLE)
    beds = [c for c in hall if c[1] == min(cc[1] for cc in hall) and c[0] < hx - 1][:3]
    for c in beds:
        m.set(c[0], c[1], BED)
    if 'kitchen' in rooms:
        for c in rooms['kitchen'][:2]:
            m.set(c[0], c[1], BARREL)
        k = rooms['kitchen'][len(rooms['kitchen']) // 2]
        m.set(k[0], k[1], D.HEARTH)
    if fallen:
        ruin(m, x0, y0, x1, y1, getattr(site, 'burnt', False))
        spot = random.choice(free(m, hall) or [(x1 - 4, sy)])
        m.set(spot[0], spot[1], D.CHEST)
        lvl = game.world.danger_at(site.x, site.y) + 2
        m.level = lvl
        r = random.random()
        keys = ['bandit', 'bandit', 'brigand'] if r < .4 else ['wolf', 'wolf'] if r < .7 else []
        cs = free(m, [(x, y) for y in range(y0 + 1, y1) for x in range(x0 + 1, x1)])
        random.shuffle(cs)
        for k, c in zip(keys, cs):
            m.mons.append(make_monster(game, k, c[0], c[1], lvl))
        m.signs.append((x1 - 10, y0, 'RUIN'))
        return finish(m, (0, sy))
    # the people of the house
    from . import realms as RL
    head = R.lord(h.head)
    cells = free(m, hall)
    if head and head.alive and cells:
        hs = min(cells, key=lambda c: cheb(c[0], c[1], hx - 1, sy))
        RL.place_lord(game, m, head, hs)
        heir = R.lord(head.heir)
        if heir and heir.alive:
            c2 = free(m, hall)
            if c2:
                RL.place_lord(game, m, heir, random.choice(c2), 'heir')
    names = []
    from .towns import town_names
    names = town_names('human')
    guards = 2 + h.wealth
    gfg = h.arms[1]
    cs = free(m, [(x, y) for y in range(y0 + 1, y1) for x in range(x0 + 1, x0 + 6)] + [(x1 - 14, sy - 1), (x1 - 14, sy + 1)])
    random.shuffle(cs)
    from .towns import townsfolk
    for c in cs[:guards]:
        g = townsfolk(game, m, [c], c, [f'A guard of House {h.name}'], 'guard', fg=gfg, role='guard')
        g.house = h.id
    folk(game, m, rooms.get('kitchen', rooms['barn']), names, 'servant', '#c8b8a0', n=1 + h.wealth)
    if 'chapel' in rooms:
        cs = free(m, rooms['chapel'])
        if cs:
            m.mons.append(make_npc(game, f'Father {names.pop() if names else "Anselm"}', 'healer', '#f4f0e6', cs[0][0], cs[0][1], True))
    for c in free(m, rooms['barn'])[:2]:
        a = make_npc(game, random.choice(['A horse', 'A cow']), 'livestock', '#c8a070', c[0], c[1], False, ch='h' if random.random() < .5 else 'C')
        m.mons.append(a)
    m.signs.append((x1 - 12, y0, f'HOUSE {h.name.upper()}'))
    return finish(m, (0, sy))


# ------------------------------------------------------------------ the raiders' halls
def hall_map(game, site):
    from . import powers as PW
    rd = PW.raiders(game.world)[site.raider]
    k = rd['kind']
    t = PW.KINDS[k]
    W, H = 60, 27
    m = _new(site, W, H, D.SAND if k in ('desert', 'canyon', 'island') else GRASS)
    m.level = 4
    sy = H // 2
    x0, y0, x1, y1 = 4, 1, W - 3, H - 2
    for x in range(0, x0 + 1):
        m.set(x, sy, PATH)
    if k == 'canyon':
        ring(m, x0, y0, x1, y1, D.CLIFF)
    elif k not in ('desert', 'island'):
        ring(m, x0, y0, x1, y1, D.PALISADE)
    m.set(x0, sy, PATH)
    for x in range(x0 + 1, x1):
        m.set(x, sy, PATH)
    wall = D.HIDE if k in ('desert', 'ice', 'mist', 'island') else WALL
    hall = rect(m, x1 - 22, sy - 4, x1 - 2, sy + 4, wall, PLANK)
    door(m, x1 - 22, sy)
    for x in range(x1 - 19, x1 - 4, 3):
        m.set(x, sy, D.FIREPIT)
    m.set(x1 - 3, sy, D.HIGHSEAT)
    for x in range(x1 - 20, x1 - 4, 2):
        for y in (sy - 2, sy + 2):
            m.set(x, y, TABLE)
    huts = []
    for k2 in range(4):
        hx = x0 + 3 + k2 * 8
        for hy in (y0 + 2, y1 - 6):
            if hx + 6 < x1 - 24:
                huts += rect(m, hx, hy, hx + 6, hy + 4, wall, FLOOR)
                door(m, hx + 3, hy + 4 if hy < sy else hy)
    names = [PW.made(t.get('chief', PW.CHIEF_DEFAULT)) for _ in range(12)]
    cells = free(m, hall)
    ch = min(cells, key=lambda c: cheb(c[0], c[1], x1 - 4, sy))
    chief = make_npc(game, PW.chief_style(rd), 'chief', '#f0d890', ch[0], ch[1], True, gender=rd['chief_g'])
    chief.raider = site.raider
    m.mons.append(chief)
    troop = D.MONSTERS[t['troops'][0]]
    folk(game, m, hall, names, 'warrior', troop['fg'], n=3)
    folk(game, m, huts, names, None, '#c0a888', n=5)
    m.signs.append((x1 - 14, sy - 5, t['hall'].upper()))
    m.guest = True
    return finish(m, (0, sy))


# ------------------------------------------------------------------ the other powers
def keep_map(game, site):
    from . import powers as PW
    od = PW.P(game.world)['church'].get('order') or {}
    W, H = 50, 23
    m = _new(site, W, H)
    m.level = 5
    sy = H // 2
    x0, y0, x1, y1 = 3, 1, W - 3, H - 2
    for x in range(0, x0 + 1):
        m.set(x, sy, PATH)
    ring(m, x0, y0, x1, y1, ROCK)
    door(m, x0, sy, D.ODOOR)
    for x in range(x0 + 1, x1):
        m.set(x, sy, PATH)
    chapel = rect(m, x1 - 14, sy - 5, x1 - 2, sy + 4, ROCK, FLOOR)
    door(m, x1 - 14, sy)
    m.set(x1 - 3, sy, ALTAR)
    barracks = rect(m, x0 + 3, y0 + 2, x0 + 14, y0 + 6, WALL, PLANK)
    door(m, x0 + 8, y0 + 6)
    for c in barracks[:5]:
        m.set(c[0], c[1], BED)
    cs = free(m, chapel)
    p = min(cs, key=lambda c: cheb(c[0], c[1], x1 - 4, sy))
    pr = make_npc(game, f'Prior {od.get("prior", "Anselm")}', 'prior', '#f4f0e6', p[0], p[1], True, gender=od.get('prior_g'))
    m.mons.append(pr)
    for c in free(m, barracks + [(x, y) for x in range(x0 + 4, x1 - 16) for y in (sy - 1, sy + 1)])[:4]:
        from .towns import townsfolk
        g = townsfolk(game, m, [c], c, ['A knight of the Order'], 'guard', fg='#f0ecd8', role='guard', ch='K')
    m.signs.append((x1 - 12, sy - 6, 'CHAPTER HOUSE'))
    return finish(m, (0, sy))


def fort_map(game, site):
    from . import powers as PW
    wt = PW.P(game.world).get('watch') or {}
    W, H = 42, 19
    m = _new(site, W, H)
    m.level = 4
    sy = H // 2
    x0, y0, x1, y1 = 3, 1, W - 3, H - 2
    for x in range(0, x0 + 1):
        m.set(x, sy, PATH)
    ring(m, x0, y0, x1, y1, D.PALISADE)
    door(m, x0, sy, D.ODOOR)
    tower = rect(m, x1 - 10, sy - 4, x1 - 2, sy + 4, ROCK, FLOOR)
    door(m, x1 - 10, sy)
    for x in range(x0 + 1, x1 - 10):
        m.set(x, sy, PATH)
    barracks = rect(m, x0 + 3, y0 + 1, x0 + 14, y0 + 5, WALL, PLANK)
    door(m, x0 + 8, y0 + 5)
    for c in barracks[:6]:
        m.set(c[0], c[1], BED)
    cs = free(m, tower)
    c = cs[0]
    m.mons.append(make_npc(game, f'Commander {wt.get("commander", "Hale")}', 'watch_captain', '#c8ccd8', c[0], c[1], True,
                           gender=wt.get('commander_g')))
    from .towns import townsfolk
    n = max(1, min(5, wt.get('strength', 6) // 2))
    for c in free(m, barracks + [(x, y) for x in range(x0 + 2, x1 - 11) for y in (sy - 2, sy + 2)])[:n]:
        townsfolk(game, m, [c], c, ['A soldier of the Watch'], 'guard', fg='#9098a8', role='guard')
    m.signs.append((x1 - 9, sy - 5, 'THE WATCH'))
    return finish(m, (0, sy))


def camp_map(game, site):
    from . import powers as PW
    c = PW.P(game.world)['companies'][site.company]
    W, H = 46, 21
    m = _new(site, W, H)
    m.level = 4
    sy = H // 2
    for x in range(0, W - 4):
        m.set(x, sy, PATH)
    tents = []
    for k in range(5):
        tx = 6 + k * 7
        for ty in (2, H - 7):
            tents += rect(m, tx, ty, tx + 4, ty + 3, D.HIDE, FLOOR)
            door(m, tx + 2, ty + 3 if ty < sy else ty, D.ODOOR)
    m.set(W - 10, sy - 2, D.FIREPIT)
    if getattr(site, 'empty', False) or c['gone']:
        m.set(W - 10, sy - 2, D.GRIT)
        return finish(m, (0, sy))
    cs = free(m, [(W - 8, sy + 1), (W - 7, sy - 1), (W - 9, sy + 2)])
    if cs:
        cap = make_npc(game, f'Captain {c["captain"]}', 'merc_captain', '#e8c888', cs[0][0], cs[0][1], True, gender=c['captain_g'])
        cap.company = site.company
        m.mons.append(cap)
    from .towns import townsfolk
    for cc in free(m, tents)[:5]:
        townsfolk(game, m, [cc], cc, [f'A sellsword of {c["name"].replace("The ", "the ")}'], 'guard', fg=c['fg'], role='guard')
    return finish(m, (0, sy))


def circle_map(game, site):
    W, H = 40, 21
    m = _new(site, W, H)
    sy = H // 2
    cx, cy = 22, sy
    for x in range(0, cx - 6):
        m.set(x, sy, PATH if random.random() < .7 else GRASS)
    import math
    for a in range(9):
        x, y = cx + round(6 * math.cos(a * 2 * math.pi / 9)), cy + round(4 * math.sin(a * 2 * math.pi / 9))
        m.set(x, y, D.CAIRN)
    hut = rect(m, cx + 8, cy - 3, cx + 13, cy + 2, D.HIDE, FLOOR)
    door(m, cx + 8, cy)
    for i in range(len(m.t)):
        if m.t[i] == GRASS and random.random() < .08:
            m.t[i] = D.SWAMP
    if getattr(site, 'burnt', False):
        ruin(m, cx + 8, cy - 3, cx + 13, cy + 2, True)
        m.set(cx, cy, D.GRIT)
        return finish(m, (0, sy))
    m.set(cx, cy, D.FIREPIT)
    c = free(m, hut)[0]
    w = make_npc(game, f'{getattr(site, "witch", "Old Morwen")} the Witch', 'witch', '#b8a0d8', c[0], c[1], True,
                 gender=getattr(site, 'witch_g', 'female'))
    m.mons.append(w)
    return finish(m, (0, sy))


def rising_map(game, site):
    from . import powers as PW
    rv = PW.P(game.world).get('revolt')
    W, H = 44, 21
    m = _new(site, W, H)
    sy = H // 2
    for x in range(0, W - 6):
        m.set(x, sy, PATH)
    lean = []
    for k in range(4):
        x = 8 + k * 8
        for y in (3, H - 6):
            lean += rect(m, x, y, x + 4, y + 2, D.HIDE, FLOOR)
            door(m, x + 2, y + 2 if y < sy else y, D.ODOOR)
    m.set(W - 12, sy - 2, D.FIREPIT)
    if getattr(site, 'empty', False) or not rv or rv['site'] != site.id:
        m.set(W - 12, sy - 2, D.GRIT)
        return finish(m, (0, sy))
    c = free(m, [(W - 10, sy - 1), (W - 11, sy + 1)])[0]
    m.mons.append(make_npc(game, rv['leader'], 'rebel_leader', '#d8c090', c[0], c[1], True, gender=rv['leader_g']))
    from .towns import town_names
    folk(game, m, lean, town_names('human'), 'rebel', '#b8a070', n=6)
    return finish(m, (0, sy))


def exile_map(game, site):
    from . import powers as PW
    from . import realms as RL
    pt = PW.P(game.world).get('pretender')
    W, H = 40, 21
    m = _new(site, W, H)
    sy = H // 2
    for i in range(len(m.t)):
        if random.random() < .18:
            m.t[i] = TREE
    for x in range(0, W - 5):
        m.set(x, sy, PATH)
    tent = rect(m, W - 14, sy - 3, W - 5, sy + 3, D.HIDE, FLOOR)
    door(m, W - 14, sy, D.ODOOR)
    m.set(W - 6, sy, D.HIGHSEAT)
    if getattr(site, 'empty', False) or not pt or pt.get('site') != site.id:
        return finish(m, (0, sy))
    R = game.world.realm
    lo = R.lord(pt['lid'])
    c = free(m, tent)
    if lo and c:
        npc = RL.place_lord(game, m, lo, min(c, key=lambda q: cheb(q[0], q[1], W - 7, sy)), 'pretender')
        npc.name = f'{lo.first} {R.houses[lo.house].name}, the rightful heir'
    from .towns import townsfolk
    for cc in free(m, [(x, y) for x in range(W - 20, W - 15) for y in (sy - 2, sy + 2)])[:3]:
        townsfolk(game, m, [cc], cc, ['A loyal knight'], 'guard', fg='#d0c8a0', role='guard', ch='K')
    return finish(m, (0, sy))
