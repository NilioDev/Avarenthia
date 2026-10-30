"""The peoples in their own lands. The halflings keep a green country of hills and hedges, where they dig their
homes into the hillsides or build round-doored houses. The elves live in glades hidden deep in the woods, which
nobody can find on a map until they have walked into one, and in one great city under the Elder Tree."""
import math
import random

from . import data as D
from .data import GRASS, TREE, PATH, FOREST, WATER, PLANK, DOOR, TABLE, ALTAR, STATUE, FIELD, STALL, ROOT, FLOOR, BED, BARREL
from .entities import GameMap, make_npc
from .worldgen import cheb

LAND_NAMES = ['The Barleydowns', 'The Clover Hills', 'The Green Downs', 'The Honeyfolds', 'The Hollow Hills',
              'The Tumbledowns', 'The Apple Country']
LIVING = (150, 180, 110)          # walls of living wood and woven branches
ELF_FG = '#aae6aa'
LANTERN = (140, 200, 255)


def oval(cx, cy, rx, ry):
    return {(x, y) for y in range(int(cy - ry) - 1, int(cy + ry) + 2) for x in range(int(cx - rx) - 1, int(cx + rx) + 2)
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1}


# ------------------------------------------------------------------ the world
def elder_spot(m, world, reach_set, taken):
    """Where the elven city stands: in the old forest at the foot of the Elder Tree."""
    tree = next(((x, y) for n, x, y in getattr(world, 'wonders', ()) if n == 'The Elder Tree'), None)
    if not tree:
        return None
    w = m.w
    cells = [(tree[0] + dx, tree[1] + dy) for dy in range(-6, 7) for dx in range(-6, 7) if 2 <= max(abs(dx), abs(dy))]
    cells = [(x, y) for x, y in cells if m.inb(x, y) and y * w + x in reach_set and m.tile(x, y) in (FOREST, GRASS)
             and y * w + x not in world.wonder_cells and all(cheb(x, y, a, b) >= 6 for a, b in taken)]
    if not cells:
        return None
    return min(cells, key=lambda c: (cheb(c[0], c[1], *tree), c))


def settle_peoples(m, world):
    """Give the halflings their country, and the elves their city."""
    regs = world.regions
    homes = {}
    for s in world.settlements:
        if not s.is_city and s.kind != 'deephold' and not getattr(s, 'dwarven', False):
            homes[s.region] = homes.get(s.region, 0) + 1
    cities = {s.region for s in world.settlements if s.is_city}
    bad = ('cult', 'horde', 'blackhand', 'clan')

    def fits(r, strict):
        if r.id == 0 or r.faction in bad or homes.get(r.id, 0) < 2:
            return False
        return not strict or (getattr(r, 'climate', 'temperate') == 'temperate' and r.biome in ('grass', 'hills'))
    cand = [r for r in regs if fits(r, True)] or [r for r in regs if fits(r, False)]
    cand.sort(key=lambda r: (r.id in cities, r.danger > 5, -homes[r.id], r.id))
    land = cand[:1]
    near = sorted((r for r in regs if fits(r, False) and r not in land and r.id not in cities),
                  key=lambda r: (r not in cand, math.hypot(r.cx - land[0].cx, r.cy - land[0].cy)) if land else 0)
    for r in near:                               # and up to two of its neighbours, so it is a country of its own
        if len(land) < 3 and land and min(math.hypot(r.cx - q.cx, r.cy - q.cy) for q in land) < 52:
            land.append(r)
    used = {r.name for r in regs}
    names = [n for n in LAND_NAMES if n not in used]
    random.shuffle(names)
    for r in land:
        r.people = 'halfling'
        if names:
            r.name = names.pop()
    world.halfling_land = [r.id for r in land]
    for s in world.settlements:
        if getattr(s, 'elder', False):
            s.race = 'elf'
            if 'circle' in D.FACTIONS:
                s.faction = 'circle'
        elif s.region in world.halfling_land and not s.is_city and s.kind != 'deephold' and s.id != 0 \
                and not getattr(s, 'dwarven', False):
            s.race = 'halfling'                  # named in names.py, like every place
        elif s.race in ('halfling', 'elf') and not getattr(s, 'dwarven', False):
            s.race = 'human'                     # elves and halflings live in their own lands now


def place_glades(game, m, world, reach_set, n=4):
    """The hidden glades of the elves: deep in the woods, far from any road. Not on the map until found."""
    from .sites import Site
    w = m.w
    taken = [(s.x, s.y) for s in world.settlements] + [(q.x, q.y) for q in world.sites] + \
            [(d.x, d.y) for d in world.dungeons.values()] + [(h.x, h.y) for h in world.holds]
    cands = [(i % w, i // w) for i in reach_set if m.t[i] == FOREST and world.road_dist[i] >= 3
             and 4 <= i % w < w - 4 and 4 <= i // w < m.h - 4 and i not in world.wonder_cells]
    random.shuffle(cands)
    from . import names as NM
    for wood, road in ((36, 6), (28, 4), (20, 3)):       # deep in the wood and far from roads if the land allows
        for x, y in cands:
            if n <= 0:
                return
            if world.road_dist[y * w + x] < road or any(cheb(x, y, a, b) < 12 for a, b in taken):
                continue
            if sum(1 for dy in range(-3, 4) for dx in range(-3, 4) if m.tile(x + dx, y + dy) == FOREST) < wood:
                continue
            st = Site(len(world.sites), 'glade', x, y, NM.make(world, 'elf', 'glade', NM.land_at(m, x, y)))
            st.hidden, st.found = True, False
            st.faction = world.region_at(x, y).faction
            world.sites.append(st)
            taken.append((x, y))
            n -= 1


def unfound(site):
    return getattr(site, 'hidden', False) and not getattr(site, 'found', True)


def discover(game, site, how=''):
    site.found = True
    om = game.maps['over']
    om.seen[site.y * om.w + site.x] = 1
    if how is not None:
        from .varnish import WHAT
        from .epics import WHAT as EP_WHAT
        what = {'gnomes': 'a gnome hamlet', 'cove': 'a pirate cove', **WHAT, **EP_WHAT}.get(site.kind, 'an elven glade')
        game.msg((how + ' ' if how else '') + f'You have found {site.name}, {what}. It is on your map now.', 'unique')


def on_step(game):
    """Walking in the deep woods: come close enough to a glade and you see its lanterns between the trees.
    Elves hear the singing from further off."""
    from .varnish import is_varnish
    from .landmarks import is_mark
    p = game.player
    for st in getattr(game.world, 'sites', ()):
        if unfound(st) and not is_varnish(st) and st.kind not in ('teacher', 'den', 'master', 'lostshop') and not is_mark(st):
            d = cheb(st.x, st.y, p.x, p.y)
            gnomes = st.kind == 'gnomes'
            if d <= 1:
                discover(game, st, 'Under the roots of a great tree you see a little round window, lit.' if gnomes else
                         'Between the trees you see lanterns, and a clearing beyond.')
            elif d <= 3 and getattr(p, 'race', '') == ('gnome' if gnomes else 'elf'):
                discover(game, st, 'You smell woodsmoke and baking, the way it smells at home.' if gnomes else
                         'Somewhere in the trees, someone is singing in your own tongue.')


# ------------------------------------------------------------------ halfling homes
def ring(m):
    """The hedge round a halfling town: centre and radii. The houses stand inside it, the fields outside."""
    return m.w / 2, m.h / 2, m.w / 2 - 20, m.h / 2 - 15


def in_ring(m, x, y, margin=2):
    cx, cy, rx, ry = ring(m)
    return ((x - cx) / (rx - margin)) ** 2 + ((y - cy) / (ry - margin)) ** 2 < 1


def outside_ring(m, x0, y0, w, h, margin=2):
    cx, cy, rx, ry = ring(m)
    edge = [(x, y) for x in range(x0, x0 + w + 1) for y in (y0, y0 + h)] + \
           [(x, y) for y in range(y0, y0 + h + 1) for x in (x0, x0 + w)]
    return all(((x - cx) / (rx + margin)) ** 2 + ((y - cy) / (ry + margin)) ** 2 > 1 for x, y in edge)


def dig_hills(game, m, plots, near_road, tier):
    """Grassy hills beside the roads, each with two homes dug into its south face: a round door and round windows in
    the slope, a hall behind them, and rooms that run back into the hill. Returns the homes as plots."""
    from .towns import Plot, carve_path, road_cells
    roads = road_cells(m)
    out = []
    n_hills = {'hamlet': 1, 'village': 2, 'town': 3}.get(tier, 2)

    def fits(cx, cy, rx, ry, reach):
        box = Plot(cx - rx - 1, cy - ry - 1, 2 * rx + 3, 2 * ry + 3, 'hill')
        if box.x < 3 or box.y < 3 or box.x + box.w > m.w - 3 or box.y + box.h > m.h - 3:
            return None
        if any(box.overlaps(o, 2) for o in plots):
            return None
        if tier == 'town' and not all(in_ring(m, x, y) for x, y in ((box.x, box.y), (box.x + box.w, box.y),
                                                                     (box.x, box.y + box.h), (box.x + box.w, box.y + box.h))):
            return None
        if min(cheb(x, y, cx, cy + ry + 2) for x, y in near_road) > reach:
            return None                          # the doors look out on a road, not on the woods
        if any(m.tile(x, y) not in (GRASS, TREE) for y in range(box.y, box.y + box.h) for x in range(box.x, box.x + box.w)):
            return None
        return box

    for k in range(n_hills + 1):
        found = None
        if k < n_hills:
            for _try in range(600):
                rx, ry = random.randint(13, 14), random.randint(6, 7)
                rc = random.choice(near_road)
                cx, cy = rc[0] + random.randint(-22, 22), rc[1] + random.randint(-ry - 14, 4)
                box = fits(cx, cy, rx, ry, 12)
                if box:
                    found = (cx, cy, rx, ry, box)
                    break
        elif not out:                            # none would fit by the roads: look everywhere, nearest road first
            rx, ry = 13, 6
            spots = [(cx, cy) for cy in range(ry + 5, m.h - ry - 5) for cx in range(rx + 5, m.w - rx - 5)]
            spots.sort(key=lambda c: min(cheb(x, y, c[0], c[1] + ry + 2) for x, y in near_road[::3]))
            for cx, cy in spots:
                box = fits(cx, cy, rx, ry, 40)
                if box:
                    found = (cx, cy, rx, ry, box)
                    break
        if found:
            cx, cy, rx, ry, box = found
            cells = oval(cx, cy, rx, ry)
            plots.append(box)
            for x, y in cells:
                m.set(x, y, D.SLOPE)
            for sx in (cx - 5, cx + 5):
                pl = _smial(m, cells, sx)
                if pl:
                    out.append(pl)
                    door_x, rim = pl.door[0], max(y for x, y in cells if x == pl.door[0])
                    for y in range(pl.door[1] + 1, rim + 2):
                        m.set(door_x, y, PATH)
                    tgt = min(roads, key=lambda c: cheb(c[0], c[1], door_x, rim + 1))
                    carve_path(m, (door_x, rim + 2), tgt)
    return out


def _smial(m, cells, x):
    """A home dug into a hill at column x: the hall along the slope, two rooms behind it."""
    from .towns import Plot
    rim = max((y for cx, y in cells if cx == x), default=None)
    if rim is None:
        return None
    hy = rim - 2                                  # the hall's floor
    dug = [(xx, yy) for yy in range(hy - 5, hy + 2) for xx in range(x - 4, x + 5)]
    if any(c not in cells for c in dug):
        return None
    floor = set((xx, hy) for xx in range(x - 3, x + 4))
    floor |= {(xx, yy) for yy in range(hy - 4, hy - 1) for xx in list(range(x - 3, x)) + list(range(x + 1, x + 4))}
    floor |= {(x - 2, hy - 1), (x + 2, hy - 1)}   # the doorways from the hall into the rooms
    for c in dug:
        m.set(c[0], c[1], PLANK if c in floor else D.EARTH)
    m.set(x, hy + 1, DOOR)
    pl = Plot(x - 4, hy - 5, 9, 7, 'home')
    pl.annex = None
    pl.inside = sorted(floor)
    pl.door = (x, hy + 1)
    pl.smial = True
    return pl


def hedges(m, tier):
    """Hedges instead of fences; round a town, a hedge instead of a wall, with gaps where the roads go through."""
    for i, t in enumerate(m.t):
        if t == D.FENCE:
            m.t[i] = D.HEDGE
    if tier != 'town':
        return
    cx, cy, rx, ry = ring(m)
    for x, y in oval(cx, cy, rx, ry) - oval(cx, cy, rx - 1.1, ry - 1.1):
        if m.inb(x, y) and m.tile(x, y) in (GRASS, TREE, FIELD, D.HEDGE):
            m.set(x, y, D.HEDGE)


# ------------------------------------------------------------------ the elven glades
def glade_map(game, site):
    """A clearing deep in the wood, reached by one hidden path: a long hall, round houses of living wood,
    a healer, an herb garden and a moon pool ringed with standing stones. Lanterns hang in the trees."""
    from .towns import (Plot, build_house, place_door, carve_path, furnish, add_sign, lay_road, meander, townsfolk,
                        hearths, town_names, free_inside)
    W, H = 96, 60
    m = GameMap(site.map_key, 'town', site.name, W, H, TREE)
    m.radius, m.sid, m.hid, m.signs = 60, None, None, []
    m.site, m.glade, m.wall_fg = site.id, True, LIVING
    cx, cy, RX, RY = 52, 29, 34, 19
    for y in range(H):
        for x in range(W):
            if ((x - cx) / RX) ** 2 + ((y - cy) / RY) ** 2 < 1 - random.random() * .08:
                m.set(x, y, GRASS)
    ey = random.randint(40, 52)
    lay_road(m, meander((0, ey), (cx - RX + 5, cy + 5), 4, 2, True), 1)
    m.entry = (0, ey)
    hall = Plot(cx - 13, cy - 12, 27, 8, 'inn')
    hall.annex = None
    build_house(m, hall)
    place_door(m, hall, cx, cy)
    furnish(m, hall)
    add_sign(m, hall, 'THE LONG HALL')
    plots = [Plot(hall.x - 1, hall.y - 1, hall.w + 2, hall.h + 3, 'hall'), Plot(cx - 10, cy + 4, 21, 10, 'pool')]
    # the moon pool and its ring of stones
    for x, y in oval(cx, cy + 9, 5, 2):
        m.set(x, y, WATER)
    for k in range(8):
        a = k / 8 * math.tau
        m.set(round(cx + math.cos(a) * 8.5), round(cy + 9 + math.sin(a) * 3.6), STATUE)
    homes = []
    healer = None
    for k in ['temple'] + ['home'] * 5:
        for _ in range(300):
            pw, ph = (11, 6) if k == 'temple' else (random.randint(7, 9), random.randint(5, 6))
            pl = Plot(random.randint(cx - RX + 3, cx + RX - pw - 3), random.randint(cy - RY + 3, cy + RY - ph - 3), pw, ph, k)
            pl.annex = None
            corners = [(pl.x - 1, pl.y - 1), (pl.x + pw, pl.y - 1), (pl.x - 1, pl.y + ph), (pl.x + pw, pl.y + ph)]
            if any(((x - cx) / RX) ** 2 + ((y - cy) / RY) ** 2 > .9 for x, y in corners):
                continue
            if any(pl.overlaps(o, 2) for o in plots):
                continue
            if any(m.tile(x, y) not in (GRASS, TREE) for y in range(pl.y - 1, pl.y + ph + 1) for x in range(pl.x - 1, pl.x + pw + 1)):
                continue
            build_house(m, pl)
            out = place_door(m, pl, cx, cy + 3)
            carve_path(m, out, (cx, cy + 2))
            furnish(m, pl)
            plots.append(pl)
            if k == 'temple':
                healer = pl
            else:
                homes.append(pl)
            break
    # the herb garden beside the healer's house
    garden = None
    for gx, gy in ((healer.x, healer.y + healer.h + 1), (healer.x, healer.y - 4), (healer.x - 4, healer.y),
                   (healer.x + healer.w + 1, healer.y)) if healer else ():
        gw, gh = (healer.w, 3) if gx == healer.x else (3, healer.h)
        cells = [(x, y) for y in range(gy, gy + gh) for x in range(gx, gx + gw)]
        if all(m.inb(*c) and m.tile(*c) in (GRASS, TREE) for c in cells):
            for x, y in cells:
                m.set(x, y, FIELD if (y - gy if gh == 3 else x - gx) % 2 == 0 else GRASS)
            garden = cells
            break
    # the people
    names = town_names('elf')
    spots = [c for c in free_inside(m, hall) if c[1] == hall.y + 2] or free_inside(m, hall)
    m.mons.append(make_npc(game, f'{names.pop()} the Hallkeeper', 'roadinn', '#e0c080', spots[0][0], spots[0][1], True))
    if healer:
        sp = free_inside(m, healer)
        if sp:
            m.mons.append(make_npc(game, f'{names.pop()} the Healer', 'healer', '#f4f0e6', sp[0][0], sp[0][1], True))
    if garden:
        c = garden[len(garden) // 2]
        m.set(c[0], c[1], GRASS)
        m.mons.append(make_npc(game, f'{names.pop()} the Herb-Warden', 'herbalist', '#90d080', c[0], c[1], True))
    m.mons.append(make_npc(game, f'{names.pop()}, Elder of the Glade', 'glade_elder', '#e0f0c0', cx, cy + 5, True))
    lawn = [(x, y) for y in range(cy - RY + 4, cy + RY - 3) for x in range(cx - RX + 5, cx + RX - 4)
            if m.tile(x, y) == GRASS and ((x - cx) / RX) ** 2 + ((y - cy) / RY) ** 2 < .7]
    for pl in homes:
        beds = [c for c in pl.inside if m.tile(*c) in (D.FLOOR, PLANK)]
        for _ in range(random.randint(1, 2)):
            job = random.choice(['archer', 'singer', 'weaver', 'woodwarden', 'child', 'any'])
            work = random.choice(free_inside(m, hall) or lawn) if job == 'singer' else random.choice(lawn)
            townsfolk(game, m, beds, work, names, job, fg=ELF_FG)
    # firelight in the hall, lanterns hung in the trees round the clearing
    hearths(m, [hall] + ([healer] if healer else []))
    edge = [(x, y) for y in range(H) for x in range(W) if m.tile(x, y) == TREE and any(
        m.inb(x + dx, y + dy) and m.tile(x + dx, y + dy) == GRASS for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    random.shuffle(edge)
    lit = []
    for x, y in edge:
        if len(lit) >= 14:
            break
        if all(cheb(x, y, a, b) > 7 for a, b in lit):
            lit.append((x, y))
    m.glows = list(m.glows) + [(x, y, LANTERN, 4) for x, y in lit]
    m.lights = list(m.glows)
    m.portal_pos = (cx + 2, cy + 2)
    m.centre = (cx, cy + 2)
    for i in range(len(m.seen)):
        m.seen[i] = 1
    return m


def glade_talk(game, npc):
    from .events import ask
    from .races import relation
    site = game.world.sites[game.map.site]
    f = game.flags
    first = not f.get(f'glade{site.id}')
    f[f'glade{site.id}'] = True
    cold = relation('elf', game.player.race) < 0
    if first and cold:
        text = ('The elder does not rise. "You found the way in. That does not happen by chance, so we will not turn you '
                'away. Rest if you must. Then go, and forget the path."')
    elif first:
        text = ('The elder looks up from the water and smiles. "You found the way in. Then you were meant to. '
                f'Be welcome in {site.name}. Few of your kind have sat by this pool."')
    else:
        text = '"Back again. The wood remembers your step now. What would you know?"'
    opts = [('Ask about the Elder Tree', 'tree')]
    if not cold:
        opts.append(('Ask whether there are other glades', 'glades'))
        from . import tradegoods as TG
        opts += TG.barter_opts(game, 'glade')
    opts.append(('Take your leave', 'bye'))
    ask(game, 'glade', npc.name, text, opts, site=site.id)


def r_glade(game, choice, ctx):
    from .engine import dir_name
    site = game.world.sites[ctx['site']]
    if choice and choice.startswith('barter:'):
        from . import tradegoods as TG
        TG.barter(game, choice[7:])
        return
    if choice == 'tree':
        city = next((s for s in game.world.settlements if getattr(s, 'elder', False)), None)
        if city:
            game.reveal_place(city.x, city.y)
            text = (f'"There is one tree older than all the others, to the {dir_name(city.x - site.x, city.y - site.y)}. '
                    f'Under its crown lies {city.name}, the oldest city of our people. The way is on your map now. '
                    f'Tell them {site.name} sent you."')
        else:
            text = '"The Elder Tree? It fell, long before your grandfathers. We keep its seeds, and wait."'
        game.request = ('dialog', 'The elder', text)
        return
    if choice == 'glades':
        left = [q for q in game.world.sites if q.kind == 'glade' and unfound(q)]
        if not left:
            game.request = ('dialog', 'The elder', '"You have found every one of us there is. Few can say that."')
            return
        other = min(left, key=lambda q: cheb(q.x, q.y, site.x, site.y))
        discover(game, other, None)
        game.request = ('dialog', 'The elder', f'"There is another, to the {dir_name(other.x - site.x, other.y - site.y)}: '
                                               f'{other.name}. Walk softly when you come near, and they will show you the way."')


# ------------------------------------------------------------------ the city under the Elder Tree
def gen_elder_city(game, s):
    """The elven city in the roots of the Elder Tree: the hall of the elven lord inside the hollow trunk, roots as thick
    as walls running out through the city, two rings of paths, and houses of living wood between the roots."""
    from .towns import (Plot, house_plot, plot_box, build_house, place_door, carve_path, furnish, add_sign, SIGN,
                        lay_road, meander, road_dirs, edge_point, river_course, carve_river, people_city, town_names,
                        place_lamps)
    from . import guilds as GU
    W, H = 140, 90
    m = GameMap(s.map_key, 'town', s.name, W, H, TREE)
    m.radius, m.sid, m.hid, m.signs = 60, s.id, None, []
    m.wall_fg = LIVING
    cx, cy = W // 2, H // 2 - 2
    RX, RY = 64, 41
    inside = lambda x, y, k=1.0: ((x - cx) / RX) ** 2 + ((y - cy) / RY) ** 2 < k
    for y in range(H):
        for x in range(W):
            if inside(x, y, 1 - random.random() * .06):
                m.set(x, y, TREE if random.random() < .012 else GRASS)
    harbour = None
    if getattr(s, 'harbour', False):             # by the sea: quays below the trees
        from . import harbour as HB
        harbour = HB.carve(m, s)
    # the hollow trunk
    TX, TY = 13, 7
    trunk = oval(cx, cy, TX, TY)
    for x, y in trunk:
        edge = any((x + dx, y + dy) not in trunk for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        m.set(x, y, D.ROOT if edge else PLANK)
    door = (cx, max(y for x, y in trunk if x == cx))
    m.set(*door, DOOR)
    # the leaf market just south of the trunk
    px, py = cx, cy + 18
    for y in range(py - 2, py + 3):
        for x in range(px - 10, px + 11):
            m.set(x, y, PATH)
    stall_spots = [(x, py - 1) for x in range(px - 8, px + 9, 4)] + [(x, py + 2) for x in range(px - 6, px + 7, 4)]
    for c in stall_spots:
        m.set(c[0], c[1], STALL)
    # the ways in, one for each road on the world map
    m.exits = []
    for dx, dy, other in (road_dirs(game, s) or [(-1, 0, None)]):
        a = math.atan2(dy, dx)
        start = (round(cx + math.cos(a) * 47), round(cy + math.sin(a) * 28))
        ex, ey = edge_point(m, cx, cy, dx, dy)
        lay_road(m, meander(start, (ex, ey), 6, 1, abs(ex - start[0]) >= abs(ey - start[1])), 2)
        m.exits.append((ex, ey, other))
    course = river_course(game, s, m, 14)
    if course:
        carve_river(m, course, 2.6, keep=(D.ROOT, PLANK, DOOR))
    # the hall of the tree
    hall = Plot(cx - TX, cy - TY, 2 * TX + 1, 2 * TY + 1, 'elder')
    hall.annex = None
    hall.inside = sorted(c for c in trunk if m.tile(*c) == PLANK)
    hall.door = door
    for dx in range(-8, 9, 4):
        for y in (cy - 2, cy + 2):
            m.set(cx + dx, y, TABLE)
    m.set(cx - 10, cy, ALTAR)
    m.set(cx + 10, cy, STATUE)
    add_sign(m, hall, 'ELDER')
    # houses of living wood between the roots
    kinds = ['temple', 'inn', 'shop', 'barracks', 'stables', 'inn']
    kinds += ['guild:' + k for k in GU.halls_in(game, s.id) if k != 'anglers'] + ['home'] * 42
    plots = [Plot(cx - TX - 2, cy - TY - 2, 2 * TX + 5, 2 * TY + 5, 'trunk'), Plot(px - 11, py - 3, 23, 7, 'market')]
    if harbour:
        plots.append(harbour)
    plots.append(Plot(cx - 2, cy + TY, 5, 18 - TY, 'way'))
    RINGS = ((24, 13), (47, 28))
    on_ring = lambda x, y: any(abs((((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2) ** .5 - 1) < 1.6 / ry for rx, ry in RINGS)
    buildings = []
    for k in kinds:
        for _ in range(300 if k == 'home' else 1500):
            x0, y0 = random.randint(cx - RX + 3, cx + RX - 14), random.randint(cy - RY + 3, cy + RY - 10)
            gk = k[6:] if k.startswith('guild:') else None
            if gk:
                secret = GU.GUILDS[gk]['secret']
                pl = house_plot('home' if secret else 'inn', x0, y0)
                pl.kind, pl.guild = ('home' if secret else 'keep'), gk
            else:
                pl = house_plot('inn' if k == 'barracks' else k, x0, y0)
                pl.kind = k
            pl.annex = None
            pl.w, pl.h = min(pl.w, 12), min(pl.h, 7)       # lodges are low and long, to fit between the roots
            bx = plot_box(pl)
            ring = [(x, y) for y in range(bx.y - 1, bx.y + bx.h + 1) for x in range(bx.x - 1, bx.x + bx.w + 1)]
            if any(not m.inb(*c) or not inside(c[0], c[1], .92) or m.tile(*c) not in (GRASS, TREE) or on_ring(*c)
                   for c in ring):
                continue
            if any(bx.overlaps(o, 1) for o in plots):
                continue
            plots.append(bx)
            buildings.append(pl)
            break
    # the roots, running out through the city round the houses that stand against them
    taken = {(x, y) for o in plots[2:] for y in range(o.y - 1, o.y + o.h + 1) for x in range(o.x - 1, o.x + o.w + 1)}
    near = lambda o: {(x, y) for y in range(o.y - 1, o.y + o.h + 1) for x in range(o.x - 1, o.x + o.w + 1)}
    below = set().union(*[near(o) for o in plots[2:] if o.kind in ('way', 'stables') or o is harbour])
    for k in range(9):
        a = k / 9 * math.tau + .35
        for t in range(9, 36):
            x = round(cx + math.cos(a) * t * 1.7 + math.sin(t / 3 + k) * 1.2)
            y = round(cy + math.sin(a) * t * .95)
            for c in ((x, y), (x + 1, y), (x, y + 1)) if t < 18 else ((x, y), (x + 1, y)) if t < 28 else ((x, y),):
                if m.inb(*c) and c not in trunk and c not in below and m.tile(*c) in (GRASS, TREE):
                    m.set(c[0], c[1], D.ROOT)
    # two rings of paths, through gaps in the roots; the way from the trunk door to the market
    for rx, ry in RINGS:
        for j in range(720):
            a = j / 720 * math.tau
            x, y = round(cx + math.cos(a) * rx), round(cy + math.sin(a) * ry)
            for c in ((x, y), (x, y + 1)):
                if m.inb(*c) and m.tile(*c) in (GRASS, TREE, D.ROOT) and c not in below:
                    m.set(c[0], c[1], PATH)
    for y in range(door[1] + 1, cy + 16):
        for x in (cx - 1, cx, cx + 1):
            m.set(x, y, PATH)
    # ladders up from the roots: one at the four quarters of each ring, and the stair in the hall
    ladders = [(cx, cy + 4)]
    for rx, ry in RINGS:
        for a in (0, math.pi / 2, math.pi, 3 * math.pi / 2):
            x, y = round(cx + math.cos(a) * rx), round(cy + math.sin(a) * ry)
            if m.tile(x, y) == PATH and not any(cheb(x, y, ex, ey) < 4 for ex, ey, _o in m.exits):
                ladders.append((x, y))
    for x, y in ladders:
        m.set(x, y, D.UP)
    paths = [(x, y) for y in range(H) for x in range(W) if m.tile(x, y) == PATH]
    lamps = []
    for j, (x, y) in enumerate(paths):
        if j % 11 == 0:
            lamps += [(x + 1, y), (x, y - 1)]
    place_lamps(m, lamps)
    # down here only the stables (horses do not climb) and the market; everything else is up in the crown
    names = town_names('elf')
    down = [pl for pl in buildings if pl.kind == 'stables']
    up = [pl for pl in buildings if pl.kind != 'stables']
    for pl in down:
        build_house(m, pl)
        tgt = min(paths, key=lambda c: cheb(c[0], c[1], pl.x + pl.w // 2, pl.y + pl.h // 2))
        carve_path(m, place_door(m, pl, tgt[0], tgt[1]), tgt)
        furnish(m, pl)
        add_sign(m, pl, SIGN[pl.kind])
    from .towns import staff, hearths, name_buildings, townsfolk, TITLE
    for pl in [hall] + down:
        staff(game, m, pl, pl.kind, names, s)
    nm, col = TITLE['market']
    for c in stall_spots[:2]:
        m.mons.append(make_npc(game, nm.format(n=names.pop()), 'market', col, c[0], c[1] - 1, True))
    gfg = D.FACTIONS[s.faction]['fg']
    for i in range(4):
        post = random.choice([(ex, ey) for ex, ey, _o in m.exits] + [(px, py + 3)])
        post = min(paths, key=lambda c: cheb(c[0], c[1], *post))
        g = townsfolk(game, m, hall.inside, post, ['An elven warden'], 'guard', fg=gfg, role='guard')
        g.name, g.night_watch = 'An elven warden', i < 2
    hearths(m, [hall] + down)
    if harbour:
        from . import harbour as HB
        HB.furnish(game, m, s, names)
    name_buildings(game, m, s)
    for o in m.mons:
        if o.role == 'elder':
            o.name = o.name.replace('Elder ', '') + ', Lord of the Tree'
    for b in getattr(m, 'buildings', []):
        if b['kind'] == 'elder':
            b['name'], b['what'] = 'The Hall of the Tree', 'hall of the elven lord'
    m.tree = s.id
    from .hunger import make_food           # a cup of the Tree's own sap, set out where the roots meet the hall
    sap = make_food(game, 'elder_sap')
    sap.x, sap.y = next(((x, y) for r in range(2, 12) for y in range(py + 4 - r, py + 5 + r) for x in range(px - r, px + r + 1)
                         if m.inb(x, y) and D.TILES[m.tile(x, y)].walk and not m.mon_at(x, y)), (px, py + 4))
    sap.dropped = True
    m.items.append(sap)
    m.portal_pos = (px + 2, py + 1)
    m.centre = (px, py + 4)
    m.entry = m.exits[0][:2]
    for i in range(len(m.seen)):
        m.seen[i] = 1
    game.maps[crown_key(s)] = gen_crown(game, s, m, up, trunk, RINGS, ladders, taken, names)
    return m


def crown_key(s):
    return s.map_key + ':crown'


def gen_crown(game, s, ground, buildings, trunk, rings, ladders, taken, names):
    """The crown of the Elder Tree, right above the city: decks on the great boughs, walkways round the tree, and the
    houses of the elves among the leaves. The same ground plan as below, so every ladder comes out right above itself."""
    from .towns import build_house, place_door, furnish, add_sign, SIGN, people_city
    from . import guilds as GU
    W, H = ground.w, ground.h
    m = GameMap(crown_key(s), 'town', f'{s.name}, in the crown', W, H, TREE)
    m.radius, m.sid, m.hid, m.signs = 60, s.id, None, []
    m.wall_fg, m.tree, m.crown = LIVING, s.id, True
    cx, cy = W // 2, H // 2 - 2
    for c in trunk:                               # the top of the trunk: the moot, where the boughs meet
        m.set(c[0], c[1], PLANK)
    for k in range(9):                            # the great boughs, over the roots
        a = k / 9 * math.tau + .35
        for t in range(9, 38):
            x = round(cx + math.cos(a) * t * 1.7 + math.sin(t / 3 + k) * 1.2)
            y = round(cy + math.sin(a) * t * .95)
            for c in ((x, y), (x + 1, y)):
                if m.inb(*c) and c not in taken:
                    m.set(c[0], c[1], PLANK)
    for rx, ry in rings:                          # walkways round the tree, over the paths
        for j in range(720):
            a = j / 720 * math.tau
            x, y = round(cx + math.cos(a) * rx), round(cy + math.sin(a) * ry)
            for c in ((x, y), (x, y + 1)):
                if m.inb(*c) and c not in taken:
                    m.set(c[0], c[1], PLANK)
    for x, y in ladders:
        m.set(x, y, D.DOWN)
    walk = [(x, y) for y in range(H) for x in range(W) if m.tile(x, y) == PLANK]
    for pl in buildings:                          # each house on its own deck, with a plank way to the nearest walk
        for y in range(pl.y - 1, pl.y + pl.h + 1):
            for x in range(pl.x - 1, pl.x + pl.w + 1):
                m.set(x, y, PLANK)
        build_house(m, pl)
        tgt = min(walk, key=lambda c: cheb(c[0], c[1], pl.x + pl.w // 2, pl.y + pl.h // 2))
        x, y = place_door(m, pl, tgt[0], tgt[1])
        while (x, y) != tgt and m.inb(x, y):
            if m.tile(x, y) == TREE:
                m.set(x, y, PLANK)
            if x != tgt[0] and (y == tgt[1] or abs(x - tgt[0]) >= abs(y - tgt[1])):
                x += 1 if tgt[0] > x else -1
            else:
                y += 1 if tgt[1] > y else -1
        furnish(m, pl)
        if getattr(pl, 'guild', None):
            if GU.GUILDS[pl.guild]['sign']:
                add_sign(m, pl, GU.GUILDS[pl.guild]['name'])
        elif pl.kind in SIGN:
            add_sign(m, pl, SIGN[pl.kind])
    walk = [(x, y) for y in range(H) for x in range(W) if m.tile(x, y) == PLANK]
    people_city(game, m, s, buildings, names, cx, cy, [], walk, 8, guard_name='An elven warden', harbour=False)
    lit = []
    for x, y in walk:
        if all(cheb(x, y, a, b) > 8 for a, b in lit):
            lit.append((x, y))
    m.glows = list(getattr(m, 'glows', [])) + [(x, y, LANTERN, 4) for x, y in lit]
    m.lights = list(m.glows)
    m.exits, m.entry = list(ground.exits), (cx, cy + 4)
    m.portal_pos, m.centre = ground.portal_pos, ground.centre
    for i in range(len(m.seen)):
        m.seen[i] = 1
    return m


def climb(game, up):
    """Up a ladder into the crown of the Elder Tree, or back down to the roots."""
    s = game.world.settlements[game.map.tree]
    if up and crown_key(s) not in game.maps:     # an old save, or the crown lost: grow it again
        game.maps.pop(s.map_key, None)
        game.enter_town(s.id)
    key = crown_key(s) if up else s.map_key
    p = game.player
    game.cur = key
    if game.map.tile(p.x, p.y) not in (D.UP, D.DOWN):
        st = [(x, y) for y in range(game.map.h) for x in range(game.map.w) if game.map.tile(x, y) in (D.UP, D.DOWN)]
        p.x, p.y = min(st, key=lambda c: cheb(c[0], c[1], p.x, p.y))
    from .towns import sync_lamps
    sync_lamps(game, game.map)
    game.msg('You climb up into the crown of the Elder Tree. Walkways run from bough to bough among the leaves.'
             if up else 'You climb back down among the roots.', 'info')
    game.compute_fov()
    game.request = ('save',)


# ------------------------------------------------------------------ the gnome hamlets
HERB_PRICE, SHROOM_PRICE, BEAST_FEE = 120, 60, 300


def place_gnomes(game, m, world, reach_set, n=3):
    """The gnome hamlets: a handful of homes under the roots of great trees, deep in the old forests, far from the
    roads of the big folk. Like the glades, nobody finds them on a map before they have walked into one."""
    from .sites import Site
    w = m.w
    names = getattr(m, 'biome_names', [])
    deep = names.index('deep_forest') if 'deep_forest' in names else None
    if deep is None:
        return
    taken = [(s.x, s.y) for s in world.settlements] + [(q.x, q.y) for q in world.sites] + \
            [(d.x, d.y) for d in world.dungeons.values()] + [(h.x, h.y) for h in world.holds]
    cands = [(i % w, i // w) for i in reach_set if m.biome[i] == deep and m.t[i] == FOREST and world.road_dist[i] >= 3
             and 4 <= i % w < w - 4 and 4 <= i // w < m.h - 4 and i not in world.wonder_cells]
    random.shuffle(cands)
    from . import names as NM
    for x, y in cands:
        if n <= 0:
            return
        if any(cheb(x, y, a, b) < 8 for a, b in taken):
            continue
        if sum(1 for dy in range(-2, 3) for dx in range(-2, 3) if m.inb(x + dx, y + dy) and m.biome[(y + dy) * w + x + dx] == deep) < 16:
            continue
        st = Site(len(world.sites), 'gnomes', x, y, NM.make(world, 'gnome', 'hamlet', NM.land_at(m, x, y)))
        st.hidden, st.found = True, False
        world.sites.append(st)
        taken.append((x, y))
        n -= 1


def great_tree(m, cx, cy, rx, ry, room, door, windows, big=False):
    """A great old tree: its trunk, roots running out from it, and a home dug in among the roots. room is (x, y, w, h)
    of the floor; the root mound round it is its wall. Returns the floor cells."""
    for k in range(7):
        a = k / 9 * math.tau + random.uniform(-.2, .2)
        for j in range(random.randint(rx + 3, rx + 6)):
            x, y = round(cx + math.cos(a) * j * 1.6), round(cy + math.sin(a) * j * .8)
            if m.inb(x, y):
                m.set(x, y, ROOT)
    x0, y0, w, h = room
    for y in range(y0 - 1, y0 + h + 1):
        for x in range(x0 - 1, x0 + w + 1):
            m.set(x, y, ROOT)
    for x, y in oval(cx, cy, rx, ry):
        m.set(x, y, D.TRUNK)
    floor = [(x, y) for y in range(y0, y0 + h) for x in range(x0, x0 + w)]
    for x, y in floor:
        m.set(x, y, FLOOR)
    m.set(door[0], door[1], DOOR if big else D.SMALLDOOR)
    for x, y in windows:
        m.set(x, y, D.WINDOW)
        m.glows.append((x, y, (255, 200, 110), 3))
    return floor


def gnome_map(game, site):
    """A mossy clearing deep in the wood, ringed by great trees with homes dug in under their roots. Only a deer track
    leads in. The doors are too small for big folk; only the elder's guest room has a wide door."""
    from .towns import town_names
    W, H = 100, 56
    m = GameMap(site.map_key, 'town', site.name, W, H, GRASS)
    m.radius, m.sid, m.hid, m.signs = 60, None, None, []
    m.site, m.wall_fg = site.id, LIVING
    m.lights, m.glows = [], []
    for i in range(len(m.t)):
        m.t[i] = TREE if random.random() < .42 else GRASS
    for x, y in oval(50, 30, 30, 15):
        m.set(x, y, GRASS)
    # the elder's tree: the guest room is dug wide enough for big folk
    hall = great_tree(m, 50, 13, 5, 3, (42, 18, 16, 5), (50, 23), [(46, 23), (54, 23)], big=True)
    for dx, dy, t in ((1, 1, BED), (1, 3, BED), (5, 2, TABLE), (8, 1, FIELD), (9, 1, FIELD), (10, 1, FIELD),
                      (13, 1, D.FURS), (14, 3, D.FURS), (11, 3, D.FIREPIT)):
        m.set(42 + dx, 18 + dy, t)
    m.lights.append((53, 21, (255, 150, 70), 4))
    m.signs.append((42, 6, "THE ELDER'S TREE"))
    names = town_names('gnome')
    m.mons.append(make_npc(game, f'{names.pop()}, elder of {site.name}', 'gnome_elder', '#e0d0f0', 49, 20, True, race='gnome'))
    hurt = make_npc(game, 'A hurt deer', 'livestock', '#be8c5a', 55, 21, True, ch='d')
    m.mons.append(hurt)
    # the homes: small rooms among the roots
    homes = []
    for cx, cy, side in ((20, 18, 'left'), (79, 17, 'right'), (22, 42, 'left'), (77, 43, 'right'), (50, 47, 'up')):
        if side == 'up':
            room, door, wins = (cx - 3, cy - 5, 6, 2), (cx, cy - 2), [(cx - 3, cy - 2), (cx + 3, cy - 2)]
        elif side == 'left':
            room, door, wins = (cx + 4, cy - 1, 5, 2), (cx + 6, cy + 2), [(cx + 4, cy + 2), (cx + 8, cy + 2)]
        else:
            room, door, wins = (cx - 8, cy - 1, 5, 2), (cx - 6, cy + 2), [(cx - 8, cy + 2), (cx - 4, cy + 2)]
        fl = great_tree(m, cx, cy, 3, 2, room, door, wins)
        x0, y0 = room[0], room[1]
        for dx, dy, t in ((0, 0, BED), (2, 0, TABLE), (4, 0, BARREL)):
            m.set(x0 + dx, y0 + dy, t)
        homes.append(fl)
    # the spring, the woodpile, the vegetable plots, the ring of mushrooms
    for x, y in oval(66, 32, 3, 1):
        m.set(x, y, WATER)
    for gx, gy in ((34, 36), (56, 38)):
        for y in range(gy, gy + 3):
            for x in range(gx, gx + 7):
                m.set(x, y, FIELD)
        for x in range(gx - 1, gx + 8):
            m.set(x, gy - 1, D.FENCE)
            m.set(x, gy + 3, D.FENCE)
        for y in range(gy, gy + 3):
            m.set(gx - 1, y, D.FENCE)
            m.set(gx + 7, y, D.FENCE)
    for k in range(10):
        a = k / 10 * math.tau
        m.set(round(46 + 4 * math.cos(a)), round(30 + 2 * math.sin(a)), D.SHROOM)
    # only a deer track leads in
    ey = 34
    for a, b in (((0, ey), (40, 31)), ((50, 24), (50, 28)), ((26, 20), (44, 29)), ((73, 19), (54, 29)),
                 ((28, 44), (40, 34)), ((71, 45), (62, 34)), ((50, 45), (50, 33))):
        n = max(abs(b[0] - a[0]), abs(b[1] - a[1]))
        for k in range(n + 1):
            x, y = round(a[0] + (b[0] - a[0]) * k / n), round(a[1] + (b[1] - a[1]) * k / n)
            if m.tile(x, y) in (GRASS, TREE):
                m.set(x, y, PATH)
    m.entry = (0, ey)
    # the gnomes, and the beasts of the wood that walk in and out without fear
    for x, y in ((48, 30), (66, 30), (33, 31), (55, 26), (25, 21), (74, 22), (51, 44)):
        n = make_npc(game, names.pop(), 'villager', '#c8aae6', x, y, False, race='gnome')
        n.job = 'any'
        m.mons.append(n)
    for (nm, ch, fg), (x, y) in zip([('A rabbit', 'r', '#beaa8c'), ('A deer', 'd', '#be8c5a'), ('A fox', 'f', '#dc783c'),
                                     ('A badger', 'b', '#aaaaaa')] * 2, ((38, 34), (70, 28), (14, 30), (84, 38), (60, 42),
                                                                         (30, 26), (8, 12), (90, 10))):
        if m.tile(x, y) in (GRASS, PATH) and not m.mon_at(x, y):
            m.mons.append(make_npc(game, nm, 'livestock', fg, x, y, False, ch=ch))
    m.centre = (50, 30)
    m.portal_pos = (50, 30)
    m.lights = list(m.lights) + list(m.glows)
    return m


def gnome_talk(game, npc):
    from .events import ask
    from . import mercs as MC
    from .money import fmt
    site = game.world.sites[game.map.site]
    f = game.flags
    first = not f.get(f'gnomes{site.id}')
    f[f'gnomes{site.id}'] = True
    if first:
        text = ('The elder peers up at you over a pair of spectacles. "A big one! Mind your head on the roots. '
                'Well, you found us, so the wood must think you are all right. Sit, sit."')
    else:
        text = '"Back again, big one? The kettle is on. What can an old gnome do for you?"'
    beast = MC.get(game, 'beast')
    opts = []
    if beast:
        opts.append((f'Ask the elder to see to {beast.name} ({fmt(BEAST_FEE)})', 'beast'))
    opts += [(f'Buy a bundle of healing herbs ({fmt(HERB_PRICE)})', 'herbs'),
             (f'Buy a basket of good mushrooms ({fmt(SHROOM_PRICE)})', 'shrooms'),
             ('Ask to learn the ways of the wood', 'teach'), ('Take your leave', 'bye')]
    ask(game, 'gnomes', npc.name, text, opts, site=site.id)


def r_gnomes(game, choice, ctx):
    from . import mercs as MC, foraging as FG
    from .money import fmt
    p = game.player
    if choice == 'beast':
        mc = MC.get(game, 'beast')
        if not mc:
            return
        if p.gold < BEAST_FEE:
            game.msg(f'The elder asks {fmt(BEAST_FEE)} for the herbs it takes.', 'bad')
            return
        if mc.state == 'fallen':
            p.gold -= BEAST_FEE
            MC.raise_up(game, mc, free=True)
            return
        p.gold -= BEAST_FEE
        mc.hp = MC.stats(game, mc)['max_hp']
        mc.frail = 0
        game.msg(f'The elder rubs salve into {mc.name}\'s hurts and hums to {mc.him()}. {mc.name} is whole again.', 'good')
    elif choice in ('herbs', 'shrooms'):
        price = HERB_PRICE if choice == 'herbs' else SHROOM_PRICE
        if p.gold < price:
            game.msg(f'That costs {fmt(price)}.', 'bad')
            return
        got = [('yarrow', 2), ('moonpetal', 1), ('feverfew', 1)] if choice == 'herbs' else [('chanterelle', 3)]
        for k, n in got:
            if not game.add_to_inv(FG.make_plant(game, k, n)):
                game.msg('Your bag is full.', 'bad')
                return
            p.known_plants.add(k)
        p.gold -= price
        game.msg('The elder wraps them in a dock leaf and tells you what each one is.', 'gold')
    elif choice == 'teach':
        from .entities import make_tome
        tm = make_tome(game, min(8, p.lvl), 'nature')
        price = tm.value() // 2
        if tm.t in p.known:
            game.request = ('dialog', 'The elder', '"You know what I know already. Go and walk in the wood; it teaches better than I do."')
            return
        if p.gold < price:
            game.request = ('dialog', 'The elder', f'"I could teach you {tm.name[8:]}. It would cost you {fmt(price)} in '
                                                   f'candles and ink. Come back when you have it."')
            return
        if not game.add_to_inv(tm):
            game.msg('Your bag is full.', 'bad')
            return
        p.gold -= price
        game.request = ('dialog', 'The elder', f'"Here, I wrote it down for you, big one: {tm.name[8:]}. Read it slowly." '
                                               f'(You pay {fmt(price)} for the {tm.name}.)')


def register():
    from . import events as EV
    EV.RESOLVERS['glade'] = r_glade
    EV.RESOLVERS['gnomes'] = r_gnomes


register()
