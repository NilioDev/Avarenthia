"""The old ways. Before the roads of the kingdoms there was the road network of the Varnish Empire; what is left
of it are overgrown paths that nobody walks: passes over the mountains, causeways through the marshes, and tracks
that lead to places the world has forgotten. They are hidden until you find them, by walking on one, from rumours,
from old maps found in ruins or bought from the Cartographers, or from the top of a watchtower. They are faster
than the open land but slower than a road, and nobody patrols them.

Three kinds: shortcuts between towns; paths to hidden things (waystations, sealed vaults, forgotten graveyards,
a smugglers' den, lost ruins), and the passes into hidden valleys walled in by mountains, where a forgotten
hamlet lives as it did when the Empire fell. Milestones along the ways carry Varnish inscriptions that point
to the other secrets: the paths are what is left of one network."""
import math
import random

from . import data as D
from .data import GRASS, FOREST, HILLS, SWAMP, SAND, MOUNTAIN, RIVER, ROAD, TOWN, CITY, WATER
from .worldgen import cheb
from .world import scaled

WAY_FG = (112, 132, 100)
WAY_COST = 8                      # road 6, grass 10, forest 14
SECRET_KINDS = ('waystation', 'vault', 'graveyard', 'smugglers', 'lostruin', 'milestone')
POI_LOOK = {'waystation': ('Σ', (200, 196, 170)), 'vault': ('Φ', (150, 200, 190)), 'graveyard': ('┼', (170, 170, 180)),
            'smugglers': ('δ', (190, 150, 110)), 'lostruin': ('Π', (150, 170, 140)), 'milestone': ('╥', (150, 160, 130))}
VARNISH = ['Aes', 'Varn', 'Ithil', 'Oros', 'Caelum', 'Vess', 'Taur', 'Mor', 'Ennis', 'Halun', 'Serrat', 'Domna']
VALLEY_NAMES = ['Hollowmere', 'Stillwater Vale', 'Elderhame', 'The Hidden Combe', 'Greystead', 'Lowfold', 'Wythcombe',
                'Ashdene', 'Tarnholm']
VALLEY_KINDS = {
    'herders': dict(desc='herders who keep goats on terraces cut by the Empire', good='valley_cheese'),
    'wardens': dict(desc='the children of a Varnish garrison, who still guard what their fathers guarded', good='ring'),
    'keepers': dict(desc='keepers of a library that should have burned with the Empire', good='word'),
}


class Way:
    def __init__(self, wid, kind, name, cells):
        self.id, self.kind, self.name, self.cells = wid, kind, name, cells
        self.target = None              # ('poi', id) or ('site', id)


# ------------------------------------------------------------------ generation
def _cost_fn(allow_mountain=True):
    def cost(t):
        if t in (GRASS, SAND):
            return 4
        if t in (FOREST, HILLS):
            return 5
        if t == SWAMP:
            return 6
        if t == MOUNTAIN:
            return 9 if allow_mountain else None
        if t == RIVER:
            return 12
        if t in (TOWN, CITY):
            return 4
        if t == ROAD:
            return 25                   # the old ways keep away from the new
        if D.TILES[t].walk:
            return 6
        return None
    return cost


def _lay(m, world, cells, wid):
    """Mark a way on the land: mountains it crosses become a pass."""
    from .world import orthogonal
    ok = lambda x, y: m.tile(x, y) not in (WATER,) and (D.TILES[m.tile(x, y)].walk or m.tile(x, y) == MOUNTAIN)
    cells = orthogonal(m, cells, ok)
    out = []
    for x, y in cells:
        t = m.tile(x, y)
        if t in (ROAD, TOWN, CITY, D.ENTR, D.CASTLE, D.FORT) or t == WATER:
            continue
        if t == MOUNTAIN:
            m.set(x, y, HILLS)
        i = y * m.w + x
        if i not in world.way_of:
            world.way_of[i] = wid
            out.append(i)
    return out


def _glyphs(m, world):
    """Each cell of an old way as a faint, broken line."""
    m.oldway = {}
    for i, wid in world.way_of.items():
        x, y = i % m.w, i // m.w

        def j(dx, dy):
            k = (y + dy) * m.w + x + dx
            return 1 if m.inb(x + dx, y + dy) and (k in world.way_of or m.t[k] in (ROAD, TOWN, CITY)) else 0
        from .look import FENCE_GLYPH
        key = (j(0, -1), j(0, 1), j(-1, 0), j(1, 0))
        ch = FENCE_GLYPH.get(key, '·')
        if (x * 7 + y * 13) % 3 == 0:
            ch = '·'                      # broken: stretches where the path is lost under the grass
        m.oldway[i] = ch


def generate(game, m, world):
    """Lay out the old ways, the places they lead to, and the hidden valleys."""
    from .world import dijkstra_path
    world.ways = []
    world.way_of = {}
    w = m.w
    rnd = random.Random(world.settlements[0].x * 31 + world.settlements[0].y)
    # ---- hidden valleys: pockets of land walled in by mountains, reachable only over an old pass
    valleys = _valleys(game, m, world, rnd)
    # ---- shortcuts between towns where the roads go the long way round
    ss = [s for s in world.settlements]
    pairs = [(a, b) for a in ss for b in ss if a.id < b.id and 22 <= math.hypot(a.x - b.x, a.y - b.y) <= 70]
    rnd.shuffle(pairs)
    road_cost = lambda t: 1 if t in (ROAD, TOWN, CITY) else None
    made = 0
    for a, b in pairs[:70]:
        if made >= scaled(4):
            break
        if any(cheb(a.x, a.y, wy.cells[0] % w, wy.cells[0] // w) < 12 for wy in world.ways if wy.kind == 'shortcut'):
            continue
        rp = dijkstra_path(m, (a.x, a.y), (b.x, b.y), road_cost)
        if rp and len(rp) < 1.9 * cheb(a.x, a.y, b.x, b.y):
            continue
        p = dijkstra_path(m, (a.x, a.y), (b.x, b.y), _cost_fn())
        if not p or len(p) > (len(rp) * .6 if rp else 999):
            continue
        tiles = [m.tile(x, y) for x, y in p]
        mts, sw = tiles.count(MOUNTAIN), tiles.count(SWAMP)
        if mts < 2 and sw < 4 and rp:
            continue
        reg = world.region_at(*p[len(p) // 2]).name
        name = f'the Old Pass of {reg}' if mts >= 2 else f'the Drowned Causeway of {reg}' if sw >= 4 else f'the Varnish Way of {reg}'
        wy = Way(len(world.ways), 'shortcut', name, [])
        wy.cells = _lay(m, world, [(a.x, a.y)] + p, wy.id)
        if len(wy.cells) < 6:
            for i in wy.cells:
                world.way_of.pop(i, None)
            continue
        wy.ends = (a.id, b.id)
        world.ways.append(wy)
        made += 1
    # ---- paths to hidden places, far from the roads
    plan = ['waystation', 'waystation', 'vault', 'graveyard', 'smugglers', 'lostruin', 'lostruin']
    rnd.shuffle(plan)
    taken = [(s.x, s.y) for s in world.settlements] + [(q.x, q.y) for q in world.pois] + \
            [(q.x, q.y) for q in getattr(world, 'sites', [])] + [(d.x, d.y) for d in world.dungeons.values()]
    cells = list(range(w * m.h))
    rnd.shuffle(cells)
    for kind in plan:
        for i in cells[:20000]:
            x, y = i % w, i // w
            if not (4 <= x < w - 4 and 4 <= y < m.h - 4):
                continue
            t = m.tile(x, y)
            if not D.TILES[t].walk or t in (ROAD, TOWN, CITY, RIVER, D.ENTR) or i in world.way_of:
                continue
            if i in getattr(world, 'wonder_cells', ()):
                continue
            rd = world.road_dist[i]
            if not 9 <= rd <= 30:
                continue
            if any(cheb(x, y, a, b) < 8 for a, b in taken):
                continue
            # the way runs back to the nearest road
            near = _nearest_road(m, x, y, 40)
            if not near:
                continue
            p = dijkstra_path(m, (x, y), near, _cost_fn())
            if not p or len(p) < 8:
                continue
            poi = _make_poi(game, m, world, kind, x, y, rnd)
            wy = Way(len(world.ways), 'hidden', f'an old path to {poi.name}', [])
            wy.cells = _lay(m, world, [(x, y)] + p, wy.id)
            wy.target = ('poi', poi.id)
            world.ways.append(wy)
            taken.append((x, y))
            break
    # ---- the valleys: a pass from the nearest road over the mountains
    for site in valleys:
        near = _nearest_road(m, site.x, site.y, 60)
        if not near:
            continue
        p = dijkstra_path(m, (site.x, site.y), near, _cost_fn())
        if not p:
            continue
        wy = Way(len(world.ways), 'valley', f'the pass to {site.name}', [])
        wy.cells = _lay(m, world, [(site.x, site.y)] + p, wy.id)
        wy.target = ('site', site.id)
        world.ways.append(wy)
    # ---- milestones along the longer ways, each pointing at another secret
    for wy in world.ways:
        for k in range(18, len(wy.cells) - 6, 26):
            i = wy.cells[k]
            x, y = i % w, i // w
            if any(cheb(x, y, a, b) < 4 for a, b in taken):
                continue
            ms = _make_poi(game, m, world, 'milestone', x, y, rnd)
            ms.way = wy.id
            taken.append((x, y))
    _glyphs(m, world)


def _nearest_road(m, x, y, maxd):
    best, bd = None, 10 ** 9
    for yy in range(max(0, y - maxd), min(m.h, y + maxd + 1)):
        for xx in range(max(0, x - maxd), min(m.w, x + maxd + 1)):
            if m.t[yy * m.w + xx] == ROAD:
                d = cheb(x, y, xx, yy)
                if d < bd:
                    best, bd = (xx, yy), d
    return best


def _make_poi(game, m, world, kind, x, y, rnd):
    from .events import POI
    from .world import Dungeon
    used = {q.name for q in world.pois}
    pick = lambda: next((v for v in rnd.sample(VARNISH, len(VARNISH)) if not any(v in u for u in used)), rnd.choice(VARNISH))
    names = {'waystation': lambda: f'Varnish Waystation {pick()}',
             'vault': lambda: f'The Sealed Vault of {pick()}',
             'graveyard': lambda: rnd.choice(['The Forgotten Graveyard', 'The Field of Nameless Stones', 'The Legion Graves']),
             'smugglers': lambda: rnd.choice(["The Smugglers' Den", "Blackwater Hole", "The Moonrunners' Cave"]),
             'lostruin': lambda: f'{rnd.choice(["Lost", "Fallen", "Overgrown"])} {rnd.choice(["Fort", "Villa", "Temple"])} of {pick()}',
             'milestone': lambda: 'A Varnish milestone'}
    poi = POI(len(world.pois), kind, x, y, names[kind]())
    poi.secret = True
    if kind in ('vault', 'graveyard', 'smugglers', 'lostruin'):
        style, tag = {'vault': ('rooms', 'crypt'), 'graveyard': ('rooms', 'crypt'), 'smugglers': ('cave', 'dungeon'),
                      'lostruin': ('rooms', rnd.choice(['dungeon', 'crypt']))}[kind]
        did = f'secret{poi.id}'
        danger = world.danger_at(x, y) + 1
        wall = {'crypt': D.hexrgb('#7e869c'), 'dungeon': D.hexrgb('#a0835e')}.get(tag)
        dg = Dungeon(did, poi.name, rnd.randint(1, 2) if kind != 'vault' else 2, danger, style, tag, None, wall, x, y, False)
        dg.poi = True
        dg.varnish = True
        world.dungeons[did] = dg
        poi.did = did
        poi.sealed = kind == 'vault'
    world.pois.append(poi)
    return poi


def _valleys(game, m, world, rnd):
    """Find, or open up, one to three pockets of meadow walled in by mountains, and put a forgotten hamlet in each."""
    from .sites import Site
    w, h = m.w, m.h
    out = []
    names = VALLEY_NAMES[:]
    rnd.shuffle(names)
    kinds = list(VALLEY_KINDS)
    rnd.shuffle(kinds)
    want = rnd.randint(1, 3) + (1 if scaled(1) > 1 else 0)
    mts = [i for i, t in enumerate(m.t) if t == MOUNTAIN]
    rnd.shuffle(mts)
    taken = [(s.x, s.y) for s in world.settlements] + [(q.x, q.y) for q in getattr(world, 'sites', [])
                                                         if q.kind != 'farm'] + [(h.x, h.y) for h in world.holds]
    meadow = m.biome_names.index('meadow') if 'meadow' in getattr(m, 'biome_names', []) else None
    for i in mts:
        if len(out) >= want:
            break
        cx, cy = i % w, i // w
        if not (12 <= cx < w - 12 and 9 <= cy < h - 9) or any(cheb(cx, cy, a, b) < 11 for a, b in taken):
            continue
        if any(cheb(cx, cy, q.x, q.y) < 30 for q in out):
            continue
        r = 4
        # deep in a range: mountains all round, at some distance
        ring = [(cx + round(math.cos(a) * (r + 3) * 1.4), cy + round(math.sin(a) * (r + 3))) for a in
                [k * math.tau / 24 for k in range(24)]]
        if sum(1 for x, y in ring if m.inb(x, y) and m.tile(x, y) == MOUNTAIN) < 12:
            continue
        cells = [(x, y) for y in range(cy - r - 1, cy + r + 2) for x in range(cx - r * 2, cx + r * 2 + 1)
                 if ((x - cx) / (r * 1.5)) ** 2 + ((y - cy) / r) ** 2 + (rnd.random() - .5) * .25 < 1]
        if any(m.tile(x, y) in (ROAD, TOWN, CITY, WATER, D.ENTR) or (y * w + x) in getattr(world, 'wonder_cells', ()) for x, y in cells):
            continue
        inner = set(cells)
        wall = [(x, y) for y in range(cy - r - 4, cy + r + 5) for x in range(cx - r * 2 - 5, cx + r * 2 + 6)
                if (x, y) not in inner and ((x - cx) / ((r + 3) * 1.5)) ** 2 + ((y - cy) / (r + 3)) ** 2 < 1]
        if any(not m.inb(x, y) or m.tile(x, y) in (ROAD, TOWN, CITY, WATER, D.ENTR, RIVER) for x, y in wall):
            continue
        if any(cheb(x, y, s.x, s.y) < 3 for x, y in wall for s in getattr(world, 'sites', [])):
            continue
        mi = m.biome_names.index('mountain') if 'mountain' in m.biome_names else None
        for x, y in wall:                         # the walls hold: rock all round
            m.set(x, y, MOUNTAIN)
            if mi is not None:
                m.biome[y * w + x] = mi
        for x, y in cells:
            m.set(x, y, GRASS if rnd.random() > .12 else FOREST)
            if meadow is not None:
                m.biome[y * w + x] = meadow
        # make sure the walls hold: everything just outside stays mountain
        kind = kinds[len(out) % len(kinds)]
        site = Site(len(world.sites), 'valley', cx, cy, names.pop() if names else 'The Hidden Vale')
        site.valley = kind
        site.faction = None
        world.sites.append(site)
        taken.append((cx, cy))
        out.append(site)
    return out


# ------------------------------------------------------------------ discovery
def known(game):
    """The old ways you know of at all."""
    return game.__dict__.setdefault('ways_known', set())


def seen_cells(game):
    """The stretches of the old ways you have seen with your own eyes, or on a map: only these are drawn."""
    return game.__dict__.setdefault('ways_seen', set())


def reveal_cells(game, wid, cells):
    """Put a stretch of an old way on your map, and the milestones that stand on it."""
    w, om = game.world, game.maps['over']
    seen = seen_cells(game)
    new = [i for i in cells if i not in seen]
    if not new:
        return 0
    seen.update(new)
    for i in new:
        om.seen[i] = 1
    on = set(new)
    for poi in w.pois:
        if getattr(poi, 'way', None) == wid and not poi.found and (poi.y * om.w + poi.x) in on:
            poi.found = True
    return len(new)


def discover_way(game, wid, how=None, cells=()):
    """You learn that a way is there. What you see of it is only what `cells` shows: the rest you walk."""
    k = known(game)
    first = wid not in k
    k.add(wid)
    reveal_cells(game, wid, cells)
    if not first:
        return False
    wy = game.world.ways[wid]
    game.msg((how + ' ' if how else '') + f'You have found {wy.name}.', 'unique')
    game.gain_xp(10 + len(wy.cells) // 8)
    return True


def _visible_cells(game, wy):
    vis = game.vis
    return [i for i in wy.cells if i < len(vis) and vis[i]]


def on_step(game):
    """Walking on, or right beside, an old way shows you the stretch of it you can see from there. Walking along it
    shows you the rest, a stretch at a time."""
    w = game.world
    way_of = getattr(w, 'way_of', None)
    if not way_of or game.cur != 'over':
        return
    p, m = game.player, game.map
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            i = (p.y + dy) * m.w + p.x + dx
            wid = way_of.get(i)
            if wid is not None and wid not in known(game):
                game.compute_fov()
                discover_way(game, wid, 'Under the grass your feet find old paving stones.',
                             _visible_cells(game, w.ways[wid]) + [i])
    vis = game.vis
    near = set()
    for dy in range(-8, 9):
        for dx in range(-8, 9):
            i = (p.y + dy) * m.w + p.x + dx
            wid = way_of.get(i)
            if wid is not None and wid in known(game) and i < len(vis) and vis[i]:
                near.add(i)
    if near:
        seen = seen_cells(game)
        for i in near - seen:
            reveal_cells(game, way_of[i], [i])


def on_way(game, x, y):
    w = game.world
    wid = getattr(w, 'way_of', {}).get(y * game.map.w + x)
    return wid is not None


def from_tower(game, vis):
    """From a watchtower you can make out the line of an old way across the land: as far as you can see, no further."""
    w = game.world
    for wid, wy in enumerate(getattr(w, 'ways', [])):
        cells = [i for i in wy.cells if i < len(vis) and vis[i]]
        if len(cells) >= 4:
            discover_way(game, wid, 'From up here you can see a straight line through the land that no road follows.', cells)


def random_unknown(game, near=None):
    w = game.world
    left = [wy for wy in getattr(w, 'ways', []) if wy.id not in known(game)]
    if not left:
        return None
    if near:
        om = game.maps['over']
        left.sort(key=lambda wy: min(cheb(i % om.w, i // om.w, *near) for i in wy.cells[::4]))
        return left[0]
    return random.choice(left)


def start_of(game, wy):
    """Where a way leaves the land you know: the end nearest a road."""
    return wy.cells[0]


def stretch(wy, frac_from=0.0, frac_to=.4):
    """A piece of a way, never its end: a map or a chart shows where it starts and where it heads, not where it goes."""
    n = len(wy.cells)
    a, b = int(n * frac_from), max(int(n * frac_from) + 2, int(n * min(frac_to, .7)))
    return wy.cells[a:b]


def rumor(game):
    """Someone remembers an old path, and tells you where it leaves the road. Only that."""
    p = game.player
    pos = (p.x, p.y) if game.cur == 'over' else game.over_pos
    wy = random_unknown(game, pos)
    if not wy:
        return None
    i = start_of(game, wy)
    discover_way(game, wy.id, '', [i])
    om = game.maps['over']
    from .engine import dir_name
    x, y = i % om.w, i // om.w
    return random.choice(['My grandfather used to talk about the old Varnish paths. One leaves the land {d} of here; the '
                          'stones are still under the moss, if you know where to look.',
                          'There is a way the old ones walked, {d} of here. Shepherds use it, when the road is watched. '
                          'I will mark where it starts. Where it goes, I could not tell you.',
                          'They built roads before the kings did, the Varnish. One starts {d} of here. Leave the road there '
                          'and follow the stones.']).format(d=dir_name(x - pos[0], y - pos[1]))


def read_map(game, it):
    """An old Varnish map, found in a ruin: a stretch of a way, drawn by someone long dead."""
    wy = random_unknown(game)
    game.remove_one(it)
    if not wy:
        game.msg('The map shows paths you already know.')
        return 1
    discover_way(game, wy.id, 'You trace the faded lines on the map and match them to the land. The map is torn where '
                 'the line runs on.', stretch(wy, 0, random.uniform(.25, .45)))
    return 1


def buy_chart(game):
    p = game.player
    wy = random_unknown(game, (p.x, p.y) if game.cur == 'over' else game.over_pos)
    if not wy:
        game.msg('"You know every way we have charted. I have nothing more to sell you."')
        return False
    discover_way(game, wy.id, 'The Cartographer copies a line from an old chart onto your map. "Where it ends, nobody '
                 'has written down."', stretch(wy, 0, random.uniform(.35, .6)))
    return True


def make_map_item(game):
    from .entities import Item
    it = Item(game.new_id(), 'oldmap', 'oldmap')
    it.name = 'An old Varnish map'
    return it


# ------------------------------------------------------------------ the secret places
def on_poi(game, poi):
    from .events import ask
    w = game.world
    if poi.kind == 'milestone':
        wy = w.ways[poi.way] if getattr(poi, 'way', None) is not None else None
        other = random_unknown(game, (poi.x, poi.y))
        text = ('A worn stone post, taller than a man. Varnish letters run down it: a number of leagues, and a name '
                'worn too far to read.')
        if wy and wy.target:
            om = game.maps['over']
            end = wy.cells[-1]
            from .engine import dir_name
            text += f' An arrow points {dir_name(end % om.w - poi.x, end // om.w - poi.y)}.'
        if other:
            om = game.maps['over']
            near = min(other.cells[::3], key=lambda i: cheb(i % om.w, i // om.w, poi.x, poi.y))
            from .engine import dir_name
            text += (f' Below, half under the moss, a second line points {dir_name(near % om.w - poi.x, near // om.w - poi.y)}: '
                     'another way, somewhere out there.')
        game.request = ('dialog', poi.name, text)
        return True
    if poi.kind == 'waystation':
        if game.day < poi.ready_day:
            game.msg('The waystation is quiet. You rested here not long ago.')
            return True
        ask(game, 'waystation', poi.name,
            'A square of fitted stone walls under a roof of turf: a Varnish waystation, where the Empire\'s couriers changed '
            'horses. The hearth still draws. On the lintel an inscription: "Peace to the traveller. The road is long; '
            'the Empire is longer."', [('Rest by the hearth', 'rest'), ('Read the inscriptions', 'read'), ('Walk on', 'leave')],
            poi=poi.id)
        return True
    return False


def _target_name(game, wy):
    w = game.world
    if wy.target[0] == 'poi':
        return w.pois[wy.target[1]].name
    return w.sites[wy.target[1]].name


def r_waystation(game, choice, ctx):
    from . import lore as LORE
    poi = game.world.pois[ctx['poi']]
    p = game.player
    if choice == 'rest':
        s = game.stats()
        p.life, p.mana, p.poison = s['max_life'], s['max_mana'], None
        game.turn += 60
        poi.ready_day = game.day + 3
        game.msg('You sleep safely behind the old walls. Nothing comes near. (fully rested)', 'good')
    elif choice == 'read':
        other = random_unknown(game, (poi.x, poi.y))
        game.request = ('dialog', poi.name, random.choice(LORE.HISTORY) if hasattr(LORE, 'HISTORY') and LORE.HISTORY else
                        'The letters are old, the words older.')
        if other:
            discover_way(game, other.id, 'A map is carved into the wall beside the door.')


def vault_open(game, poi):
    """A sealed vault opens to the old word, or a Varnish key."""
    if not getattr(poi, 'sealed', False):
        return True
    if game.flags.get('varnish_word'):
        if not game.flags.get(f'vault{poi.id}'):
            game.flags[f'vault{poi.id}'] = True
            game.msg('You speak the old word. Stone grinds on stone, and the door of the vault sinks into the ground.', 'unique')
        return True
    key = next((it for it in game.player.inv if it.k == 'vkey'), None)
    if key:
        game.remove_one(key)
        poi.sealed = False
        game.msg('The Varnish key turns in a lock that has not moved in four hundred years.', 'unique')
        return True
    game.msg('A door of seamless stone, carved with an eye. There is no handle, no lock, only a line of Varnish letters: '
             '"Speak, and enter." You do not know what to say.', 'info')
    return False


def vault_loot(game, m, dg):
    """The first time you reach the bottom of a Varnish place, something of the Empire waits there."""
    from .entities import random_gear, make_set_item
    if getattr(m, 'varnish_loot', False) or m.depth != dg.depth:
        return
    m.varnish_loot = True
    up = m.t.index(D.UP) if D.UP in m.t else 0
    x, y = up % m.w, up // m.w
    floor = [i for i, t in enumerate(m.t) if t == D.FLOOR and cheb(i % m.w, i // m.w, x, y) > 8]
    if not floor:
        return
    i = random.choice(floor)
    lvl = dg.base + dg.depth
    sealed = dg.id.startswith('secret') and any(getattr(q, 'did', None) == dg.id and q.kind == 'vault' for q in game.world.pois)
    if sealed or random.random() < .4:
        st = D.SETS['varnish']
        it = make_set_item(game, 'varnish', random.randrange(len(st['pieces'])))
        it.ided = False
        game.spill(m, i % m.w, i // m.w, it)
    game.spill(m, i % m.w, i // m.w, random_gear(game, lvl + 2, 3, None, 'varnish'))
    if random.random() < .5:
        game.spill(m, i % m.w, i // m.w, make_map_item(game))


# ------------------------------------------------------------------ the hidden valleys
ARCHAIC = ['Thou art far from any road, stranger. Few come, and fewer go.', 'The Empire built these terraces. We but keep them.',
           'Mind the goats; they are older than thy kingdom, and wiser.', 'We speak as our fathers spake. The world below changed; we did not.',
           'The spring hath never failed us, not in four hundred winters.', 'Hast thou news of the Emperor? No? Then nothing hath changed.',
           'Coin? What would we do with coin? Bring us salt, or bread, or iron.']


def valley_talk(game, npc):
    from .events import ask
    site = game.world.sites[game.map.site]
    kind = getattr(site, 'valley', 'herders')
    if npc.role == 'valley':
        game.say(npc, random.choice(ARCHAIC))
        return
    f = game.flags
    first = not f.get(f'valley{site.id}')
    f[f'valley{site.id}'] = True
    if first:
        text = (f'The elder looks at you a long time before speaking. "So. Someone found the pass. We are {VALLEY_KINDS[kind]["desc"]}. '
                'We do not sell, and we do not buy. But we trade, with those who bring what we lack."')
    else:
        text = '"Thou art back. Sit, then. What wouldst thou?"'
    food = sum(it.n for it in game.player.inv if it.k == 'food')
    opts = [('Ask about the old days', 'lore')]
    if food >= 2:
        opts.append(('Trade two of your provisions', 'trade'))
    opts.append(('Take your leave', 'bye'))
    ask(game, 'valley', npc.name, text, opts, site=site.id)


def r_valley(game, choice, ctx):
    from . import lore as LORE
    site = game.world.sites[ctx['site']]
    kind = getattr(site, 'valley', 'herders')
    p = game.player
    if choice == 'lore':
        truth = LORE.true_lore(game) if hasattr(LORE, 'true_lore') else random.choice(LORE.HISTORY)
        other = random_unknown(game, (site.x, site.y))
        if other:
            truth += f' "And there is a way the Empire left, not far from here. Go and see."'
            discover_way(game, other.id, '')
        game.request = ('dialog', 'The elder', truth)
        return
    if choice != 'trade':
        return
    paid = 0
    for it in list(p.inv):
        while it.k == 'food' and it.n > 0 and paid < 2:
            game.remove_one(it)
            paid += 1
            if it not in p.inv:
                break
        if paid >= 2:
            break
    good = VALLEY_KINDS[kind]['good']
    if good == 'valley_cheese':
        from .hunger import make_food
        game.add_to_inv(make_food(game, 'valley_cheese', 2))
        game.msg('In return: two rounds of the valley\'s goat cheese, wrapped in leaves. It keeps for a month.', 'good')
    elif good == 'ring' and not game.flags.get('ward_ring'):
        from .entities import make_unique
        u = dict(name='Wardstone Ring', base='ring', lvl=6, aff={'res_all': (8, 12), 'sight': (1, 1), 'life': (10, 20)})
        it = make_unique(game, u)
        game.flags['ward_ring'] = True
        game.add_to_inv(it)
        game.msg('The elder presses a ring of grey stone into your hand. "Our fathers wore these on the wall. Wear it well."', 'unique')
    elif good == 'word' and not game.flags.get('varnish_word'):
        game.flags['varnish_word'] = True
        vaults = [q for q in game.world.pois if q.kind == 'vault']
        game.msg('In return, the keeper teaches you a word in the old tongue. "It opens what the Empire sealed." '
                 + (f'The vaults are marked on your map.' if vaults else ''), 'unique')
        for q in vaults:
            q.found = True
            game.maps['over'].seen[q.y * game.maps['over'].w + q.x] = 1
    else:
        from .hunger import make_food
        game.add_to_inv(make_food(game, 'valley_cheese', 1))
        game.msg('They give what they can spare: a round of goat cheese.', 'good')


def valley_map(game, site):
    """A forgotten hamlet: a handful of huts on terraces round a spring, an old tree or a Varnish stone,
    footpaths, goats, and an elder who does not trust you yet."""
    from .entities import GameMap, make_npc
    from .towns import town_names, townsfolk
    from .data import FLOOR, WALL, DOOR, PATH, FIELD, WELL, TREE, STATUE, ROCK, BED, TABLE
    kind = getattr(site, 'valley', 'herders')
    W, H = 72, 40
    m = GameMap(site.map_key, 'town', site.name, W, H, GRASS)
    m.radius, m.sid, m.hid, m.signs = 60, None, None, []
    m.site = site.id
    cx, cy = W // 2, H // 2
    # the mountain walls all round
    for y in range(H):
        for x in range(W):
            d = ((x - cx) / (W * .47)) ** 2 + ((y - cy) / (H * .45)) ** 2
            if d > 1 - random.random() * .08:
                m.set(x, y, ROCK)
            elif random.random() < .03:
                m.set(x, y, TREE)
    # the way in: a narrow cleft from the west
    for x in range(0, cx - 14):
        for dy in (-1, 0, 1) if x > 3 else (0,):
            m.set(x, cy + dy, PATH if dy == 0 else GRASS)
    m.entry = (0, cy)
    # the heart of the valley
    if kind == 'herders':
        m.set(cx, cy, WELL)
    elif kind == 'wardens':
        m.set(cx, cy, STATUE)                              # the pale Varnish stone
        m.signs.append((cx - 5, cy - 2, 'AES VARNIS'))
    else:
        m.set(cx, cy, TREE)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            m.set(cx + dx, cy + dy, TREE)
    # terraces on the slopes
    for k in range(4):
        ty = cy - 8 + k * 2 if k < 2 else cy + 4 + (k - 2) * 2
        for x in range(cx - 18, cx + 19):
            if m.tile(x, ty) == GRASS and (x + k) % 9:
                m.set(x, ty, FIELD)
    names = town_names('human')
    huts = []
    spots = [(cx - 14, cy - 5), (cx + 9, cy - 6), (cx - 10, cy + 6), (cx + 12, cy + 5), (cx - 3, cy - 12), (cx + 2, cy + 10),
             (cx + 18, cy - 1), (cx - 19, cy + 1)]
    random.shuffle(spots)
    for (hx, hy) in spots[:random.randint(5, 8)]:
        if not (2 < hx < W - 7 and 2 < hy < H - 6):
            continue
        if any(m.tile(x, y) == ROCK for x in range(hx, hx + 5) for y in range(hy, hy + 4)):
            continue
        for y in range(hy, hy + 4):
            for x in range(hx, hx + 5):
                m.set(x, y, WALL if y in (hy, hy + 3) or x in (hx, hx + 4) else FLOOR)
        door = (hx + 2, hy + 3 if hy < cy else hy)
        m.set(*door, DOOR)
        m.set(hx + 1, hy + 1, BED)
        huts.append((hx, hy, door))
        # a footpath to the heart
        x, y = door[0], door[1] + (1 if hy < cy else -1)
        while (x, y) != (cx, cy) and max(abs(x - cx), abs(y - cy)) > 1:
            if m.tile(x, y) in (GRASS, FIELD):
                m.set(x, y, PATH)
            x += (cx > x) - (cx < x) if abs(x - cx) > abs(y - cy) else 0
            y += (cy > y) - (cy < y) if abs(x - cx) <= abs(y - cy) else 0
    title = {'herders': 'Elder', 'wardens': 'Warden-Captain', 'keepers': 'Keeper'}[kind]
    if huts:
        hx, hy, _d = huts[0]
        m.set(hx + 3, hy + 1, TABLE)
        m.mons.append(make_npc(game, f'{title} {names.pop()}', 'valley_elder', '#e0d0a0', hx + 2, hy + 1, True))
    for hx, hy, door in huts[1:]:
        townsfolk(game, m, [(hx + 2, hy + 2)], (cx + random.randint(-6, 6), cy + random.randint(-4, 4)), names,
                  random.choice(['goatherd', 'weaver', 'terrace-keeper']), fg='#c0b090', role='valley')
    for _ in range(random.randint(3, 6) if kind == 'herders' else 2):
        x, y = cx + random.randint(-16, 16), cy + random.randint(-8, 8)
        if m.tile(x, y) in (GRASS, FIELD):
            m.mons.append(make_npc(game, 'A goat', 'livestock', '#c8b890', x, y, False, ch='g'))
    m.lights = []
    m.portal_pos = (cx + 2, cy + 2)
    for i in range(len(m.seen)):
        m.seen[i] = 1
    return m


def register():
    from . import events as EV
    EV.RESOLVERS['waystation'] = r_waystation
    EV.RESOLVERS['valley'] = r_valley


register()
