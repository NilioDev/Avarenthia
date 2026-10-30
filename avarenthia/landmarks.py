"""The places of today (round 29): the newer places of part B and the 44 places of the peoples and powers, fixed in the
wild (project files poi/ideeen.md part B and poi/volken.md 1-44). Round 30 adds more of them in yearplaces.py, on the
same frame.

Each place is one cell of the world map with a small play map of its own. What matters there is a telling thing you
walk into (`m.tells`: cell -> thing key, drawn over the generic tile MARK and named by THINGS) or someone you talk to
(role 'landmark'). A place is data: its sign, name, words, where it lies (PLACE), how its map is laid out (BUILD) and
what its things and people do (ACT, TALK, CHOOSE). Some places come and go with the world: the realm's war camp, the
refugee camp and the prospectors' camp (`daily`). What is yours (a pilgrim's token, a stone laid on a cairn, a friend
of the kobolds) lives on the player, in p.marks."""
import math
import random

from . import data as D
from .data import GRASS, PATH, TREE, WALL, FLOOR, DOOR, WATER, SHALLOW, SAND, FIELD, FENCE, BED, TABLE
from .worldgen import cheb

MARK = D.MARK

# ------------------------------------------------------------------ the kinds
# kind: (sign on the world map, colour, the line in the look and the map's description)
LOOK, DESC = {}, {}
KINDS = []


def kind(k, ch, fg, desc):
    LOOK[k] = (ch, fg)
    DESC[k] = desc
    KINDS.append(k)


# part B: the newer things of the world of now
kind('logcamp', '┼', (196, 160, 110), 'A logging camp at the edge of the elven wood. More stumps every month.')
kind('charcoal', '▲', (150, 140, 130), 'A charcoal burners\' clearing: turf-covered stacks smoking day and night.')
kind('peat', '▬', (140, 110, 80), 'Peat cutters on the moor: long black cuts and stacks of turf drying in the wind.')
kind('saltpan', '□', (230, 230, 220), 'Salt pans on the shore: shallow beds of sea water drying white in the sun.')
kind('limekiln', '∩', (220, 214, 190), 'A lime kiln in the hills, its mouth glowing, white dust on everything.')
kind('realmcamp', '▲', (226, 120, 90), 'A war camp of a realm: tents, horse lines, smoke, a sutler\'s wagon.')
kind('refugees', '∩', (190, 170, 140), 'A refugee camp: people who fled a burned village, under sheets and branches.')
kind('beacon', '¥', (200, 170, 120), 'A beacon hill: a stack of timber on the top, ready to be lit when the enemy comes.')
kind('lighthouse', '¡', (250, 240, 190), 'A lighthouse on the coast, against the wreckers. A keeper lives in it.')
kind('tollbridge', '╬', (190, 170, 140), 'A baron\'s toll bridge: the shortest way over the river, for a fee.')
kind('serai', '■', (226, 196, 140), 'A caravanserai: a walled court on a long road, with stables, beds and a well.')
kind('prospect', '♦', (210, 190, 130), 'A prospectors\' camp, sprung up after a star fell: tents, quarrels, digging.')
kind('lodge', 'Ω', (170, 200, 120), 'A lord\'s hunting lodge and the wood that goes with it. Hunting here is poaching.')
# the realms
kind('bstone', '┴', (200, 196, 180), 'A boundary stone between two baronies, cut with two coats of arms.')
kind('loneinn', '╤', (236, 164, 84), 'A lone inn on a long road between two towns, the only roof for miles.')
kind('mill', '╪', (200, 180, 140), 'A mill on a stream outside the village: bread and flour, cheap.')
kind('bchapel', '±', (230, 220, 200), 'A small chapel on an old bridge, where travellers pray for the road.')
# the Church
kind('pilgchapel', '±', (255, 240, 200), 'A pilgrims\' chapel high on a rock, with steps cut up to it.')
kind('tithe', '⌂', (200, 170, 110), 'The Church\'s tithe barn in the fields, with a tenth of every harvest in it.')
kind('hwell', 'o', (170, 220, 255), 'The holy well of a local saint. Its water eases small ills.')
kind('pcross', '┼', (210, 200, 190), 'A plague cross where the roads meet. Bread was left here for the sick, once.')
# the Watch, the companies and the revolt (the pretender's hidden camp is powers.py's 'exile')
kind('blockhouse', '╦', (176, 184, 200), 'A blockhouse of the Watch on a border road, posters nailed by the door.')
kind('winterq', '⌂', (200, 160, 120), 'A sellsword company in winter quarters, in an empty farm. Bored men and dice.')
kind('outlaws', '♣', (150, 200, 120), 'A clearing round an old oak with a mark cut in it. The revolt meets here.')
# the witches
kind('witchcot', '⌂', (170, 210, 150), 'A witch\'s cottage deep in the wild. She heals and curses, for a price that is not money.')
kind('hangtree', '♠', (150, 150, 140), 'The hanging tree at the edge of a village, where they hanged witches long ago.')
# raiders and riders
kind('boatsheds', '▀', (170, 150, 120), 'Long boat-sheds of the Fjordmen, where their ships lie over the winter.')
kind('shipset', '◘', (190, 190, 180), 'A ship-setting: standing stones in the shape of a ship. A jarl\'s grave.')
kind('dwell', 'o', (210, 190, 130), 'A desert well, marked with the signs of a riding tribe.')
kind('pcairn', '▲', (190, 186, 176), 'A cairn of the pass clans. Every traveller adds a stone.')
kind('falselight', '¡', (240, 180, 90), 'A post with a lantern hook on a cliff. The wreckers hang their false light here.')
kind('ladders', '║', (200, 150, 100), 'Cliff ladders of the canyon riders: the only way up to their village.')
kind('stonerows', 'Π', (180, 190, 200), 'Long rows of standing stones on the heath. In the mist they show a way.')
kind('starcairn', '*', (200, 220, 255), 'Cairns of the island voyagers on a skerry, laid out like stars.')
# dwarves
kind('airshaft', 'o', (214, 176, 110), 'An air shaft of a dwarf hold: a grate on the mountainside, warm air, hammers below.')
kind('dwarfroad', 'Ω', (214, 176, 110), 'A gate of a dwarf road that runs through the mountain, faster than the pass.')
kind('grudgestone', '┬', (200, 160, 120), 'A grudge stone, where a dwarf was wronged. The grievance is cut into it.')
kind('sealed', '+', (190, 170, 150), 'A sealed door in the rock, with dwarf runes: "Not to be opened."')
# elves
kind('watchtree', '♠', (150, 230, 170), 'A watch tree at the edge of the elven wood, with a platform high in it.')
kind('burntgrove', '♠', (100, 90, 80), 'The burned grove: black trunks the elves leave standing, a place of mourning.')
kind('gravetree', '♣', (230, 240, 230), 'A grave tree that grew over a fallen elf, with a ring of stones round it.')
# halflings
kind('hedgegate', '#', (120, 200, 90), 'A gate in the boundary hedge of the halfling country, and a warden with tea.')
kind('partyfield', '♣', (230, 200, 120), 'A party field: a meadow with lanterns in the trees and a long table.')
kind('pipeweed', 'ⁿ', (170, 190, 90), 'Pipe-weed fields on a sunny slope: the best leaf in the world, sold only here.')
# gnomes
kind('beegarden', '◘', (240, 210, 90), 'A gnome bee garden in a clearing: hives under the roots of the trees.')
kind('stump', '♣', (200, 170, 110), 'A hollow lookout stump with a little bell in it.')
# orcs and the tribes
kind('duelring', '○', (220, 120, 90), 'A duel ring of stones on the steppe, where orcs settle who is the stronger.')
kind('wcairn', '▲', (200, 110, 90), 'A warlord\'s cairn, his weapons laid on top. Taboo.')
kind('midden', '%', (150, 130, 100), 'A goblin midden: a heap of rubbish goblins pick through.')
kind('ropebridge', '═', (190, 150, 100), 'A goblin rope bridge over a gorge. The shortest way, if it holds.')
kind('lure', '*', (240, 220, 130), 'Something shiny hung on a pole. A kobold lure.')
kind('boneyard', '%', (220, 210, 186), 'A gnoll bone yard: a clearing full of bones round a carrion tree.')
kind('eggmounds', '∩', (150, 190, 110), 'Lizardfolk egg mounds in the swamp.')
# for everyone
kind('othershrine', 'Ψ', (200, 200, 160), 'A shrine of a people who no longer live here.')
kind('waymarket', '○', (230, 200, 120), 'A ring of stones where the roads meet: a market of all the peoples, one day a month.')

NAME = {k: '' for k in KINDS}


def is_mark(site):
    return site.kind in LOOK


def describe(game, site):
    k = site.kind
    if k == 'realmcamp':
        return f'The war camp of {getattr(site, "realm_name", "a realm")}: tents, horse lines, a sutler\'s wagon.'
    return DESC[k]


# ------------------------------------------------------------------ the telling things
# key: (name, sign, colour)
THINGS = {}


def thing_kind(key, name, ch, fg):
    THINGS[key] = (name, ch, fg)


for _k, _n, _c, _f in [
    ('stumps', 'field of stumps', '∙', (170, 130, 90)), ('foreman', 'log pile', '≡', (170, 130, 80)),
    ('clamp', 'charcoal stack', '▲', (110, 100, 96)), ('turf', 'stack of turf', '■', (110, 80, 56)),
    ('pan', 'salt pan', '□', (236, 236, 226)), ('kiln', 'lime kiln', '∩', (236, 226, 200)),
    ('tent', 'tent', '▲', (200, 190, 160)), ('banner', 'war banner', '¶', (226, 120, 90)),
    ('pyre', 'beacon', '¥', (200, 170, 120)), ('lamp', 'great lamp', '¡', (255, 240, 180)),
    ('tollgate', 'toll gate', '╪', (190, 160, 110)), ('trough', 'water trough', '▬', (140, 180, 200)),
    ('claim', 'claim stake', '↑', (210, 190, 130)), ('trophy', 'antlers over the door', 'Ψ', (220, 210, 186)),
    ('bstone', 'boundary stone', '┴', (210, 206, 190)), ('wheel', 'mill wheel', '☼', (190, 170, 130)),
    ('altar', 'little altar', '±', (240, 230, 210)), ('chapel', 'chapel door', '±', (255, 240, 200)),
    ('barn', 'barn door', '+', (200, 150, 90)), ('well', 'holy well', 'o', (170, 220, 255)),
    ('cross', 'plague cross', '┼', (220, 210, 200)), ('posters', 'board of posters', '≡', (230, 220, 190)),
    ('cage', 'prisoner\'s cage', '╫', (160, 160, 170)), ('dice', 'dice table', 'π', (200, 160, 110)),
    ('oak', 'marked oak', '♠', (110, 190, 90)),
    ('cauldron', 'cauldron', 'o', (120, 190, 110)), ('htree', 'hanging tree', '♠', (150, 150, 140)),
    ('shed', 'boat-shed', '▀', (170, 150, 120)), ('shipstone', 'stone of the ship-setting', 'Π', (200, 200, 190)),
    ('dwell', 'tribal well', 'o', (210, 190, 130)), ('pcairn', 'cairn of the pass', '▲', (200, 196, 186)),
    ('post', 'lantern post', '¡', (240, 180, 90)), ('ladder', 'cliff ladder', '║', (200, 150, 100)),
    ('rowstone', 'standing stone', 'Π', (180, 190, 210)), ('starcairn', 'star cairn', '*', (200, 220, 255)),
    ('grate', 'grate of the air shaft', '#', (200, 170, 120)), ('dgate', 'dwarf gate', 'Ω', (214, 176, 110)),
    ('grudge', 'grudge stone', '┬', (200, 160, 120)), ('sdoor', 'sealed door', '+', (190, 170, 150)),
    ('platform', 'ladder to the platform', '║', (150, 230, 170)), ('blacktree', 'burned trunk', '♠', (90, 80, 70)),
    ('gtree', 'grave tree', '♣', (230, 240, 230)), ('hgate', 'hedge gate', '∩', (160, 220, 110)),
    ('longtable', 'long table', 'π', (220, 190, 120)), ('weed', 'pipe-weed plants', 'ⁿ', (170, 200, 90)),
    ('hive', 'hive under the roots', '◘', (240, 210, 90)), ('bell', 'hollow stump', '♣', (200, 170, 110)),
    ('ringstone', 'stone of the ring', '■', (200, 140, 110)), ('wcairn', 'warlord\'s cairn', '▲', (200, 110, 90)),
    ('heap', 'rubbish heap', '%', (150, 130, 100)), ('bridge', 'rope bridge', '═', (190, 150, 100)),
    ('shiny', 'shiny thing on a pole', '*', (250, 230, 140)), ('carrion', 'carrion tree', '♠', (200, 190, 170)),
    ('eggs', 'egg mound', '∩', (150, 190, 110)), ('shrine', 'old shrine', 'Ψ', (200, 200, 160)),
    ('mstone', 'market stone', '■', (230, 200, 120)), ('pit', 'pit', 'o', (90, 80, 70)),
]:
    thing_kind(_k, _n, _c, _f)


def thing_at(m, x, y):
    th = getattr(m, 'tells', None)
    return th.get(y * m.w + x) if th else None


def thing_name(m, i):
    th = getattr(m, 'tells', None)
    k = th.get(i) if th else None
    return THINGS[k][0] if k in THINGS else None


def put(m, x, y, key, walk=False):
    """Set a telling thing down: the tile MARK under it, drawn with its own sign."""
    if not m.inb(x, y):
        return
    i = y * m.w + x
    if not walk:
        m.t[i] = MARK
    m.tells[i] = key
    name, ch, fg = THINGS[key]
    m.over[i] = (ch, fg, None)


def take(m, x, y, tile=GRASS):
    """A thing taken away."""
    i = y * m.w + x
    m.tells.pop(i, None)
    m.over.pop(i, None)
    m.t[i] = tile


# ------------------------------------------------------------------ the player's own marks
def marks(game):
    return game.player.__dict__.setdefault('marks', {})


def once(game, key, every=None):
    """True the first time (or once in `every` days): the player has done this here."""
    mk = marks(game)
    last = mk.get(key)
    if last is not None and (every is None or game.day - last < every):
        return False
    mk[key] = game.day
    return True


def done(game, key):
    return key in marks(game)


# ------------------------------------------------------------------ where they lie
def _bio(m, x, y):
    n = getattr(m, 'biome_names', None)
    return n[m.biome[y * m.w + x]] if n else ''


class Lay:
    """What the placing needs: the world map, the taken cells, and the questions it asks of a cell."""

    def __init__(self, game, m, world, reach_set):
        self.game, self.m, self.w, self.reach = game, m, world, reach_set
        self.taken = [(s.x, s.y) for s in world.settlements] + [(q.x, q.y) for q in world.sites] + \
                     [(d.x, d.y) for d in world.dungeons.values()] + [(h.x, h.y) for h in world.holds]
        self.used = {s.name for s in world.sites}
        self.riv = getattr(m, 'river', None) or bytearray(m.w * m.h)

    def bio(self, x, y):
        return _bio(self.m, x, y)

    def free(self, x, y, gap=4):
        m, w = self.m, self.m.w
        i = y * w + x
        return (3 <= x < w - 3 and 3 <= y < m.h - 3 and i in self.reach and D.TILES[m.t[i]].walk
                and m.t[i] not in (D.ROAD, D.TOWN, D.CITY, D.ENTR, D.RIVER, D.CASTLE, D.FORT)
                and i not in self.w.wonder_cells and all(cheb(x, y, a, b) >= gap for a, b in self.taken))

    def road(self, x, y):
        return self.w.road_dist[y * self.m.w + x]

    def near_tile(self, x, y, tiles, r=1):
        m = self.m
        return any(m.inb(x + a, y + b) and m.tile(x + a, y + b) in tiles for a in range(-r, r + 1) for b in range(-r, r + 1))

    def near_bio(self, x, y, names, r=1):
        m = self.m
        return any(m.inb(x + a, y + b) and self.bio(x + a, y + b) in names for a in range(-r, r + 1) for b in range(-r, r + 1))

    def river_near(self, x, y, r=1):
        m = self.m
        return any(m.inb(x + a, y + b) and self.riv[(y + b) * m.w + x + a] for a in range(-r, r + 1) for b in range(-r, r + 1))

    def search(self, pred, gap=5, tries=5000, cells=None):
        """A free cell where pred holds; the land is full, so the gap to other places shrinks if it must. With cells,
        only those are tried (e.g. the cells beside a road)."""
        m = self.m
        for g in sorted({min(gap, 6), 4, 3}, reverse=True):
            for _ in range(tries // 3):
                if cells:
                    x, y = random.choice(cells)
                else:
                    x, y = random.randint(4, m.w - 5), random.randint(4, m.h - 5)
                if self.free(x, y, g) and pred(x, y):
                    return x, y
        return None

    def by_road(self):
        """The cells next to a road."""
        if getattr(self, '_by_road', None) is None:
            m = self.m
            self._by_road = [(i % m.w, i // m.w) for i, d in enumerate(self.w.road_dist) if d == 1
                             and 4 <= i % m.w < m.w - 4 and 4 <= i // m.w < m.h - 4]
        return self._by_road

    def around(self, x, y, lo, hi, gap=4, pred=None):
        spots = [(x + dx, y + dy) for dx in range(-hi, hi + 1) for dy in range(-hi, hi + 1) if lo <= max(abs(dx), abs(dy))]
        random.shuffle(spots)
        for g in sorted({min(gap, 4), 2}, reverse=True):
            got = next(((a, b) for a, b in spots if self.m.inb(a, b) and self.free(a, b, g) and (pred is None or pred(a, b))), None)
            if got:
                return got
        return None

    def add(self, kind_, xy, name, hidden=False, **kw):
        from .sites import Site
        w = self.w
        if name in self.used:
            name = f'{name} ({len(w.sites)})'
        st = Site(len(w.sites), kind_, xy[0], xy[1], name)
        st.faction = w.region_at(*xy).faction
        if hidden:
            st.hidden, st.found = True, False
        for k, v in kw.items():
            setattr(st, k, v)
        w.sites.append(st)
        self.taken.append(xy)
        self.used.add(name)
        return st


PLACE = {}          # kind: fn(lay) that sets this world's places of that kind down


def place(game, m, world, reach_set):
    """Set this world's places of today down, with dice of their own (so the rest of the world stays as it was)."""
    state = random.getstate()
    random.seed(game.seed * 4241 + 29)
    try:
        lay = Lay(game, m, world, reach_set)
        for k in KINDS:
            if k in PLACE:
                PLACE[k](lay)
        from . import yearplaces as YP
        YP.place(lay)
    finally:
        random.setstate(state)


def scaled(n):
    from .world import scaled as sc
    return sc(n)


def _town_name(lay, x, y):
    s = min(lay.w.settlements, key=lambda s: cheb(s.x, s.y, x, y))
    return s


# ------------------------------------------------------------------ the play maps
def _base(game, site, w, h, ground=GRASS):
    from .entities import GameMap
    m = GameMap(site.map_key, 'town', site.name, w, h, ground)
    m.glows, m.lights = [], []
    m.radius, m.sid, m.hid, m.signs = 60, None, None, []
    m.site = site.id
    m.lm = site.kind
    m.tells, m.over = {}, {}
    m.level = game.world.danger_at(site.x, site.y) + 1
    return m


def land(game, site, w=60, h=34):
    """A map whose ground and trees follow the world cell it lies on."""
    om = game.maps['over']
    b = _bio(om, site.x, site.y)
    t = om.tile(site.x, site.y)
    snow = b in ('tundra', 'tundra_hills', 'alpine', 'glacier', 'shrubland_cold', 'taiga')
    sand = b in ('desert', 'dune', 'beach', 'bone_sand', 'salt_edge', 'canyon', 'badlands', 'savanna')
    m = _base(game, site, w, h, D.SNOW if snow and b != 'taiga' else SAND if sand and b != 'savanna' else GRASS)
    wood = t == D.FOREST or b in ('forest', 'deep_forest', 'conifer', 'taiga', 'birch', 'jungle', 'dry_forest')
    rocky = t in (D.HILLS, D.MOUNTAIN)
    wet = t == D.SWAMP
    for i in range(w * h):
        r = random.random()
        if wood and r < .22:
            m.t[i] = TREE
        elif not wood and r < (.01 if sand else .04):
            m.t[i] = TREE
        elif rocky and r < .12:
            m.t[i] = D.BAREROCK if r < .09 else D.ROCK
        elif wet and r < .3:
            m.t[i] = D.SWAMP if r < .22 else SHALLOW
    m.wood, m.rocky, m.wet = wood, rocky, wet
    return m


def clear(m, cx, cy, rx, ry, tile=GRASS):
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            if m.inb(x, y) and ((x - cx) / max(1, rx)) ** 2 + ((y - cy) / max(1, ry)) ** 2 <= 1.05:
                if m.tile(x, y) in (TREE, D.ROCK, D.BAREROCK, D.SWAMP, SHALLOW):
                    m.set(x, y, tile)


def way(m, a, b, tile=PATH):
    from .nature import path
    path(m, a, b, tile, over=(GRASS, TREE, SAND, D.SNOW, D.GRIT, D.BAREROCK, D.SWAMP, D.RUBBLE, D.ROCK, SHALLOW))


def hut(m, x0, y0, w, h, door='s', wall=WALL, floor=FLOOR):
    """A small house: walls, a floor and a door on one side. Returns the door cell."""
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            edge = y in (y0, y0 + h - 1) or x in (x0, x0 + w - 1)
            m.set(x, y, wall if edge else floor)
    d = {'s': (x0 + w // 2, y0 + h - 1), 'n': (x0 + w // 2, y0), 'w': (x0, y0 + h // 2), 'e': (x0 + w - 1, y0 + h // 2)}[door]
    m.set(*d, DOOR)
    return d


def tent(m, x, y):
    """A small tent of hide: three cells of canvas with the opening south."""
    for dx in (-1, 0, 1):
        m.set(x + dx, y, D.HIDE)
    m.set(x - 1, y + 1, D.HIDE)
    m.set(x + 1, y + 1, D.HIDE)
    m.set(x, y + 1, GRASS if m.tile(x, y + 1) != SAND else SAND)


def fence_ring(m, x0, y0, x1, y1, gap, tile=FENCE):
    for x in range(x0, x1 + 1):
        for y in (y0, y1):
            m.set(x, y, tile)
    for y in range(y0, y1 + 1):
        for x in (x0, x1):
            m.set(x, y, tile)
    m.set(*gap, GRASS)


def scatter(m, tile, p, on=(GRASS,), box=None):
    x0, y0, x1, y1 = box or (0, 0, m.w - 1, m.h - 1)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if m.tile(x, y) in on and random.random() < p:
                m.set(x, y, tile)


def river_through(m, x=None, wide=2, ford=None):
    """A river from top to bottom; returns its middle column."""
    x = m.w // 2 if x is None else x
    for y in range(m.h):
        c = x + int(1.5 * math.sin(y * .25))
        for dx in range(-wide - 1, wide + 2):
            m.set(c + dx, y, WATER if abs(dx) <= wide else SHALLOW)
    return x


def sea_side(m, depth=10, side='e'):
    for y in range(m.h):
        edge = depth + int(2 * math.sin(y * .3))
        for x in range(m.w - edge, m.w) if side == 'e' else range(0, edge):
            dd = (x - (m.w - edge)) if side == 'e' else (edge - x)
            m.set(x, y, SAND if dd < 2 else SHALLOW if dd < 4 else WATER)


def npc(game, m, name, fg, x, y, kind_=None, stay=True, ch='☺', race=None, role='landmark'):
    from .entities import make_npc
    spot = free_near(m, x, y)
    if not spot:
        return None
    o = make_npc(game, name, role, fg, spot[0], spot[1], stay, ch=ch, race=race)
    o.lm = kind_ or m.lm
    o.job = 'any'
    o.home_pos = o.work_pos = spot
    m.mons.append(o)
    return o


def free_near(m, x, y, r=6):
    for d in range(r + 1):
        cells = [(x + a, y + b) for a in range(-d, d + 1) for b in range(-d, d + 1) if max(abs(a), abs(b)) == d]
        random.shuffle(cells)
        for c in cells:
            if m.inb(*c) and D.TILES[m.tile(*c)].walk and not m.mon_at(*c):
                return c
    return None


def beasts(game, m, keys, near, r=8, awake=False, lvl=None):
    from .entities import make_monster
    out = []
    for k in keys:
        spot = None
        for _ in range(60):
            c = (near[0] + random.randint(-r, r), near[1] + random.randint(-r, r))
            if m.inb(*c) and D.TILES[m.tile(*c)].walk and not m.mon_at(*c) and c != (game.player.x, game.player.y):
                spot = c
                break
        if spot:
            o = make_monster(game, k, *spot, lvl or m.level)
            o.awake = awake
            m.mons.append(o)
            out.append(o)
    return out


def finish(m, entry):
    """The way in, every telling thing in reach, and the map known."""
    from .oldplaces import _reach
    m.entry = entry
    if not D.TILES[m.tile(*entry)].walk:
        m.set(*entry, PATH)
    nxt = (entry[0] + 1, entry[1])
    if not D.TILES[m.tile(*nxt)].walk:
        m.set(*nxt, PATH)
    got = _reach(m, nxt)
    for i in list(m.tells):
        x, y = i % m.w, i // m.w
        if any((x + a, y + b) in got for a in (-1, 0, 1) for b in (-1, 0, 1)):
            continue
        way(m, (x, y + 1) if m.inb(x, y + 1) else (x, y - 1), nxt)
        if m.t[i] != MARK and not D.TILES[m.t[i]].walk:
            m.t[i] = MARK
        got = _reach(m, nxt)
    for i in range(len(m.seen)):
        m.seen[i] = 1
    m.lights = list(m.glows)
    return m


BUILD = {}           # kind: fn(game, site) -> map


def site_map(game, site):
    state = random.getstate()
    random.seed(game.seed * 5303 + site.x * 991 + site.y * 41 + 29)
    try:
        if site.kind in BUILD:
            m = BUILD[site.kind](game, site)
        else:
            from . import yearplaces as YP
            m = YP.BUILD[site.kind](game, site)
    finally:
        random.setstate(state)
    return m


def plain(game, site, things, who=(), size=(56, 32), entry_y=None, clearing=(9, 6)):
    """The common map: the land, a clearing in the middle with the things in it, a path in from the west.
    things: [(dx, dy, key)] from the middle; who: [(name, colour, dx, dy)]."""
    m = land(game, site, *size)
    cx, cy = m.w // 2, m.h // 2
    if clearing:
        clear(m, cx, cy, *clearing)
    ey = cy if entry_y is None else entry_y
    way(m, (0, ey), (cx - 2, cy))
    for dx, dy, key in things:
        put(m, cx + dx, cy + dy, key)
    for name, fg, dx, dy in who:
        npc(game, m, name, fg, cx + dx, cy + dy)
    m.centre = (cx, cy)
    return m


# ------------------------------------------------------------------ being there
ON_ENTER = {}        # kind: fn(game, site, m) -> the line, or None
LINES = {}           # kind: the line on coming in


def on_enter(game, site, m):
    k = site.kind
    fn = ON_ENTER.get(k)
    line = fn(game, site, m) if fn else None
    if line is None:
        line = LINES.get(k)
    if line:
        game.msg(line, 'info')
    from . import guide as GU
    GU.tip(game, 'landmark')


ACT = {}             # kind: fn(game, site, key, x, y) -> turns or None
TALK = {}            # kind: fn(game, site, npc)
CHOOSE = {}          # kind: fn(game, site, choice, ctx)


def bump(game, x, y):
    m = game.map
    key = thing_at(m, x, y)
    if key is None:
        return None
    site = game.world.sites[m.site]
    fn = ACT.get(site.kind)
    if fn is None:
        from . import yearplaces as YP
        fn = YP.ACT.get(site.kind)
    if fn is None:
        return None
    spent = fn(game, site, key, x, y)
    return 0 if spent is None else spent


def talk(game, npc):
    site = game.world.sites[game.map.site] if getattr(game.map, 'site', None) is not None else None
    k = getattr(npc, 'lm', None)
    fn = TALK.get(k)
    if fn is None:
        from . import yearplaces as YP
        fn = YP.TALK.get(k)
    if fn and site is not None:
        fn(game, site, npc)
    else:
        game.say(npc, 'Safe roads to you.')


def ask(game, site, who, text, options, **ctx):
    from . import events as EV
    EV.ask(game, 'lm', who, text, options, site=site.id, **ctx)


def r_lm(game, choice, ctx):
    if choice in ('bye', 'leave', None):
        return
    site = game.world.sites[ctx['site']]
    fn = CHOOSE.get(site.kind)
    if fn is None:
        from . import yearplaces as YP
        fn = YP.CHOOSE.get(site.kind)
    if fn:
        fn(game, site, choice, ctx)


def on_step(game):
    m = game.map
    site = game.world.sites[m.site]
    fn = STEP.get(site.kind)
    if fn is None:
        from . import yearplaces as YP
        fn = YP.STEP.get(site.kind)
    if fn:
        fn(game, site, m)


STEP = {}


def on_kill(game, mon):
    m = game.map
    if getattr(m, 'lm', None) == 'lodge' and mon.k in GAME_BEASTS:
        _poached(game, m)
    duel_won(game, mon)
    YP.on_kill(game, mon)


# ------------------------------------------------------------------ small helpers for the effects
def say(game, site, text, title=None):
    game.request = ('dialog', title or site.name, text)


def chron(game, site, text, key=None, chapter='Places'):
    from . import chronicle as CH
    CH.add(game, chapter, text, 'seen', where=site.name, place=(site.x, site.y), key=key or f'lm:{site.id}', quiet=True)


def pay(game, price, what='That'):
    from .money import fmt
    p = game.player
    if p.gold < price:
        game.msg(f'{what} costs {fmt(price)}.', 'bad')
        return False
    p.gold -= price
    return True


def give(game, it):
    if not game.add_to_inv(it):
        game.msg('Your pack is full.', 'bad')
        return False
    return True


def food(game, key, n=1):
    from .hunger import make_food
    return make_food(game, key, n)


def curio(game, key):
    from .nature import curio as cu
    return cu(game, key)


def buff(game, k, v, turns, label, text=None):
    p = game.player
    p.buffs = [b for b in p.buffs if b[0] != k or b[3] != label] + [[k, v, turns, label]]
    if text:
        game.msg(text, 'good' if v >= 0 else 'bad')


def heal(game, frac=1.0, poison=True):
    p = game.player
    s = game.stats()
    p.life = min(s['max_life'], p.life + round(s['max_life'] * frac))
    if poison:
        p.poison = None


def hurt(game, n, why):
    p = game.player
    p.life -= n
    game.num(p.x, p.y, f'-{n}', (255, 90, 70))
    if p.life <= 0:
        game.die(why)


def rep(game, faction, n, quiet=False):
    from .war import change_rep
    if faction in D.FACTIONS:
        change_rep(game, faction, n, quiet=quiet)


def gossip(game, npc=None):
    from . import news as NW
    line = NW.gossip(game)
    if npc is not None:
        game.say(npc, line)
    else:
        game.msg(line, 'talk')


def lore(game, npc):
    from . import history as HI
    text = HI.hint(game, npc) or 'Out here you hear the wind, and the wolves. Not much else.'
    game.request = ('dialog', npc.name, text if text.startswith('"') else f'"{text}"')


def cargo_buy(game, g, n, price):
    """Buy n units of a good into your cargo, at a price of the place's own."""
    from . import economy as ECO
    from .money import fmt
    p = game.player
    got = 0
    while got < n and p.gold >= price and ECO.free_cargo(p) >= D.GOODS[g]['w']:
        p.gold -= price
        p.cargo[g] = p.cargo.get(g, 0) + 1
        have = p.cargo[g]
        p.cost_basis[g] = (p.cost_basis.get(g, 0) * (have - 1) + price) / have
        got += 1
    if got:
        game.msg(f'You load {got} {D.GOODS[g]["name"].lower()} for {fmt(got * price)}.', 'gold')
    elif ECO.free_cargo(p) < D.GOODS[g]['w']:
        game.msg('You have no room left for cargo.', 'bad')
    else:
        game.msg(f'That costs {fmt(price)} a load.', 'bad')
    return got


def cargo_sell(game, goods, factor):
    """Sell what you carry of these goods, at the town price times factor. Returns the coin."""
    from .money import fmt
    p = game.player
    got = 0
    for g in goods:
        n = p.cargo.pop(g, 0)
        if n:
            p.cost_basis.pop(g, None)
            got += round(n * D.GOODS[g]['base'] * factor)
    if got:
        p.gold += got
        game.msg(f'They pay you {fmt(got)}.', 'gold')
    return got


def shop(game, site, key, n=6, kinds=None):
    from .worldgen import gen_shop
    k = f'lm{site.id}{key}'
    if game.day - marks(game).get(f'stock:{k}', -99) >= 5 or k not in game.shops:
        marks(game)[f'stock:{k}'] = game.day
        stock = gen_shop(game)
        if kinds:
            stock = [i for i in stock if i.k in kinds] or stock
        game.shops[k] = stock[:n]
    game.request = ('shop', k)


def to_world(game, x, y, turns, text):
    """Leave the place and come out somewhere else on the world map."""
    game.leave_to_over()
    p = game.player
    p.x, p.y = x, y
    game.over_pos = (x, y)
    game.msg(text, 'info')
    game.end_turn(turns)
    game.compute_fov()


def fight(game, keys, near=None, lvl=None, line=None):
    p = game.player
    out = beasts(game, game.map, keys, near or (p.x, p.y), r=6, awake=True, lvl=lvl)
    if line:
        game.msg(line, 'bad')
    return out


def night(game):
    from . import towns as TW
    return TW.is_night(game)


def season(game):
    from . import calendar as CAL
    return CAL.season(game.day)


def at_war(game):
    from . import realms as RL
    return bool(RL.get(game).wars)


def region_people(lay, x, y):
    s = min(lay.w.settlements, key=lambda s: cheb(s.x, s.y, x, y))
    return s


GAME_BEASTS = {'red_deer', 'boar', 'hare', 'elk', 'forest_hog'}


def _poached(game, m):
    from . import crime as CR
    keeper = next((o for o in m.mons if getattr(o, 'lm', None) == 'lodge' and o.role == 'landmark'), None)
    seen = keeper is not None and game.visible(keeper.x, keeper.y)
    if seen:
        game.say(keeper, 'That is my lord\'s deer! Poacher!')
    CR.commit(game, 8, 'poaching in a lord\'s wood', witnessed=1.0 if seen else .25,
              near=(game.world.sites[m.site].x, game.world.sites[m.site].y))


def register():
    from . import events as EV
    EV.RESOLVERS['lm'] = r_lm
    from .nature import CURIO
    CURIO.update({
        'armring': ('A jarl\'s arm-ring', 60, (230, 200, 110), 'A heavy ring of twisted gold off a dead jarl\'s arm.'),
        'pilgtoken': ('A pilgrim\'s token', 1, (230, 220, 190), 'A little lead token on a cord: you climbed to the chapel.'),
        'pipeweed': ('A pouch of pipe-weed', 3, (160, 190, 90), 'The best leaf in the world, the halflings say.'),
        'honeycomb': ('A comb of gnome honey', 4, (240, 210, 90), 'Wild honey, dark and sweet, in its wax.'),
        'eggshell': ('A lizard egg', 5, (170, 200, 130), 'A leathery egg, still warm.'),
        'junk': ('A goblin\'s treasure', 0, (150, 130, 100), 'A bent spoon, a button and a bit of string, tied together.'),
        'starshard': ('A splinter of star-iron', 25, (190, 200, 230), 'A sliver off the fallen star, black and heavy.'),
        'scale': ('An old dragon scale', 90, (200, 100, 70), 'A scale as big as a hand, hard as iron. A smith would want it.'),
        'stormwood': ('A billet of lightning wood', 30, (220, 220, 160), 'Oak struck by lightning many times. Staff makers pay well for it.'),
        'flood': ('A brass flood marker', 2, (190, 170, 110), 'A brass plate with a year on it, washed off a wall.'),
    })


# ================================================================== part B: the world of now
# ---- the logging camp at the edge of the elven wood
def _p_logcamp(lay):
    m = lay.m
    edge = lambda x, y: m.tile(x, y) == D.GRASS and lay.near_bio(x, y, ('forest', 'deep_forest', 'birch'), 1) \
        and lay.road(x, y) <= 8
    elves = [q for q in lay.w.sites if q.kind == 'glade'] + [s for s in lay.w.settlements if getattr(s, 'elder', False)]
    for k in range(scaled(2)):
        spot = None
        if elves:
            e = elves[k % len(elves)]
            spot = lay.around(e.x, e.y, 6, 22, 6, edge)
        spot = spot or lay.search(edge, 8)
        if spot:
            lay.add('logcamp', spot, f'{random.choice(["Axe", "Stump", "Saw", "Chip"])}{random.choice(["field", "end", "ley", "wick"])} Camp')


def _m_logcamp(game, site):
    m = land(game, site, 60, 34)
    for y in range(m.h):
        for x in range(m.w):
            if x > 30:
                m.set(x, y, TREE if random.random() < .45 else GRASS)
            elif x > 12 and random.random() < .2:
                put(m, x, y, 'stumps', walk=True)
    cx, cy = 22, m.h // 2
    clear(m, cx, cy, 6, 4)
    for dx in (-3, 3):
        tent(m, cx + dx, cy - 3)
    put(m, cx + 2, cy + 2, 'foreman')
    way(m, (0, cy), (cx, cy))
    npc(game, m, 'The foreman', '#d8b080', cx, cy)
    for k in range(3):
        npc(game, m, 'A woodcutter', '#b89870', cx + 6 + k * 2, cy + random.randint(-4, 4), role='landmark')
    return finish(m, (0, cy))


def _t_logcamp(game, site, o):
    if o.name != 'The foreman':
        game.say(o, random.choice(['Mind the trees on that side. The elves shoot.', 'Twelve trunks a day. They pay by the trunk.',
                                   'The wood goes back further every year. Not my doing; the timber merchants\'.']))
        return
    ask(game, site, o.name, '"The empire wants timber, and the elves want their wood. We get arrows in the night. Stand '
        'watch with my lads tonight, and I pay you a silver."',
        [('Stand watch for the camp (1s)', 'watch'), ('Spike the trees for the elves', 'spike'), ('Goodbye', 'bye')])


def _c_logcamp(game, site, choice, ctx):
    if choice == 'watch':
        if not once(game, f'watch:{site.id}', 7):
            game.msg('"You stood watch this week already. Come back next week."', 'talk')
            return
        game.player.gold += 100
        rep(game, 'league', 1, quiet=True)
        rep(game, 'circle', -2)
        game.end_turn(60)
        game.msg('You sit the night out by the log pile. Twice something moves at the edge of the wood; nobody shoots. '
                 'In the morning the foreman pays you a silver.', 'good')
    elif choice == 'spike':
        from . import crime as CR
        rep(game, 'circle', 4)
        CR.commit(game, 6, 'spiking the timber of a logging camp', witnessed=.4, near=(site.x, site.y))
        game.end_turn(30)
        game.msg('You drive old nails into the best trunks at the edge, where a saw will find them. The wood is quiet '
                 'around you, and somewhere above, someone is pleased.', 'info')


PLACE['logcamp'], BUILD['logcamp'], TALK['logcamp'], CHOOSE['logcamp'] = _p_logcamp, _m_logcamp, _t_logcamp, _c_logcamp
LINES['logcamp'] = 'Axes ring at the edge of the wood. Stumps everywhere, more of them than trees on this side.'


# ---- small work on the land: charcoal burners, peat cutters, salt pans, the lime kiln
def _p_work(kind_, pred, names, n):
    def fn(lay):
        for _ in range(scaled(n)):
            spot = lay.search(lambda x, y: pred(lay, x, y), 8)
            if spot:
                lay.add(kind_, spot, random.choice(names))
    return fn


PLACE['charcoal'] = _p_work('charcoal', lambda l, x, y: l.m.tile(x, y) == D.FOREST and l.road(x, y) <= 10,
                            ['The Burners\' Clearing', 'Smokewood', 'The Charcoal Hearths', 'Blackfoot Clearing'], 2)
PLACE['peat'] = _p_work('peat', lambda l, x, y: l.bio(x, y) in ('moor', 'marsh') or (l.m.tile(x, y) == D.SWAMP and l.road(x, y) <= 10),
                        ['The Turf Cuts', 'Blackbank', 'The Peat Hags', 'Moss Cuttings'], 2)
PLACE['saltpan'] = _p_work('saltpan', lambda l, x, y: l.m.tile(x, y) in (D.SAND, D.GRASS) and l.near_tile(x, y, (D.WATER,))
                           and not l.river_near(x, y, 2) and y > l.m.h * .35, ['The Salt Pans', 'Whitegarth Pans', 'The Salterns'], 2)
PLACE['limekiln'] = _p_work('limekiln', lambda l, x, y: l.m.tile(x, y) == D.HILLS and l.road(x, y) <= 8,
                            ['The Lime Kiln', 'Whitestone Kiln', 'The Old Kiln'], 1)
WORK = {'charcoal': ('clamp', 'A charcoal burner', '#9a9088', 'charcoal', '"Charcoal for the smiths. We do not go to town; '
                     'the carter comes. You have bread on you? Ale? We pay town prices and more for it."'),
        'peat': ('turf', 'A peat cutter', '#a08060', 'turf', '"Turf for the winter fires. Out here we see nobody for weeks. '
                 'Bread, ale, salt: whatever you carry, we pay well."'),
        'saltpan': ('pan', 'A salter', '#e0e0d8', 'salt', '"Sea salt, dried in the sun. Fair price, straight from the pan: '
                    'cheaper than any market."'),
        'limekiln': ('kiln', 'The lime burner', '#e0dcc8', 'lime', '"Lime for mortar and for the fields. Thirsty work. '
                     'If you carry ale, I buy it."')}


def _m_work(game, site):
    th, who, fg, _w, _t = WORK[site.kind]
    m = land(game, site, 54, 30)
    cx, cy = m.w // 2, m.h // 2
    if site.kind == 'saltpan':
        sea_side(m, 12)
        for y in range(cy - 6, cy + 7, 3):
            for x in range(cx - 8, cx + 6, 4):
                put(m, x, y, 'pan')
    else:
        clear(m, cx, cy, 10, 6)
        for k in range(4 if site.kind != 'limekiln' else 1):
            put(m, cx - 6 + k * 4, cy - 3 + (k % 2) * 4, th)
        hut(m, cx + 6, cy - 2, 5, 4, 'w')
    way(m, (0, cy), (cx - 7, cy))
    npc(game, m, who, fg, cx - 2, cy + 1)
    if site.kind == 'charcoal':
        m.glows.append((cx - 6, cy - 3, (255, 140, 60), 4))
    return finish(m, (0, cy))


def _t_work(game, site, o):
    th, who, fg, what, line = WORK[site.kind]
    from .money import fmt
    if site.kind == 'saltpan':
        ask(game, site, o.name, line, [(f'Load salt ({fmt(SALT_PRICE)} a load)', 'salt'), ('Any news?', 'news'),
                                       ('Goodbye', 'bye')])
        return
    p = game.player
    have = [g for g in ('grain', 'ale', 'salt', 'fish') if p.cargo.get(g)]
    if site.kind == 'limekiln':
        have = [g for g in have if g == 'ale']
    ask(game, site, o.name, line, [('Sell them what they want from your cargo', 'sell' if have else None),
                                   ('Any news?', 'news'), ('Goodbye', 'bye')])


SALT_PRICE = 9


def _c_work(game, site, choice, ctx):
    if choice == 'salt':
        cargo_buy(game, 'salt', 4, SALT_PRICE)
    elif choice == 'sell':
        goods = ('ale',) if site.kind == 'limekiln' else ('grain', 'ale', 'salt', 'fish')
        cargo_sell(game, goods, 1.35)
    elif choice == 'news':
        gossip(game)


def _a_work(game, site, key, x, y):
    game.msg({'clamp': 'A stack of wood under turf, smoking. Inside it the wood turns slowly to charcoal.',
              'turf': 'Black turf cut in bricks, stacked to dry in the wind.',
              'pan': 'A shallow bed of sea water. At the edges the salt dries white.',
              'kiln': 'The mouth of the kiln glows. The stone in it turns to lime.'}.get(key, ''))
    return 0


for _k in WORK:
    BUILD[_k], TALK[_k], CHOOSE[_k], ACT[_k] = _m_work, _t_work, _c_work, _a_work
LINES.update(charcoal='Blue smoke hangs over the clearing. It smells of burning wood, slow and sweet.',
             peat='Long black cuts in the moor, and turf stacked in rows to dry.',
             saltpan='The pans shine white in the sun. Gulls cry over the sea.',
             limekiln='White dust on the grass, on the stones, on the lime burner.')


# ---- the war camp of a realm: only while a war lasts (daily)
def realm_camps(game):
    """A realm at war has a camp near the front; when the war ends, it is gone."""
    from . import realms as RL
    w = game.world
    R = RL.get(game)
    om = game.maps['over']
    live = {(war['a'], war['b']) for war in R.wars}
    for st in [q for q in w.sites if q.kind == 'realmcamp']:
        st.gone = getattr(st, 'war', None) not in live
    for war in R.wars:
        key = (war['a'], war['b'])
        if any(q.kind == 'realmcamp' and getattr(q, 'war', None) == key for q in w.sites):
            continue
        kg = R.kingdoms[war['a']]
        near = [rid for rid, b in R.baronies.items() if b.kingdom == war['b']]
        mine = [rid for rid, b in R.baronies.items() if b.kingdom == war['a'] and any(n in R.adj.get(rid, ()) for n in near)]
        if not mine:
            continue
        rg = w.regions[random.choice(mine)]
        taken = [(s.x, s.y) for s in w.settlements] + [(q.x, q.y) for q in w.sites if not getattr(q, 'gone', False)]
        spot = None
        for _ in range(300):
            x, y = rg.cx + random.randint(-8, 8), rg.cy + random.randint(-8, 8)
            if om.inb(x, y) and om.tile(x, y) in (D.GRASS, D.HILLS) and all(cheb(x, y, a, b) >= 3 for a, b in taken):
                spot = (x, y)
                break
        if not spot:
            continue
        from .sites import Site
        st = Site(len(w.sites), 'realmcamp', spot[0], spot[1], f'The War Camp of {kg.short}')
        st.faction, st.war, st.realm_name = 'crown', key, kg.name
        w.sites.append(st)


def _m_realmcamp(game, site):
    m = land(game, site, 64, 36)
    cx, cy = m.w // 2, m.h // 2
    clear(m, cx, cy, 20, 12)
    for k in range(12):
        x, y = cx - 16 + (k % 6) * 6, cy - 7 + (k // 6) * 9
        tent(m, x, y)
    put(m, cx, cy, 'banner')
    for x in range(cx + 8, cx + 16):
        m.set(x, cy + 3, FENCE)
    way(m, (0, cy), (cx - 2, cy))
    npc(game, m, 'The sutler', '#d0b070', cx - 4, cy + 2)
    npc(game, m, 'The marshal\'s clerk', '#c0c8e0', cx + 3, cy - 2)
    for _ in range(5):
        npc(game, m, 'A soldier', '#a8b0c0', cx + random.randint(-14, 14), cy + random.randint(-8, 8), stay=False)
    if night(game) and random.random() < .5:
        npc(game, m, 'A man creeping off', '#8a8a80', cx + 18, cy + 8)
    m.glows.append((cx, cy + 1, (255, 140, 60), 4))
    return finish(m, (0, cy))


def _t_realmcamp(game, site, o):
    from .money import fmt
    if o.name == 'The sutler':
        ask(game, site, o.name, '"Everything a soldier needs, at war prices. Coin first."',
            [('See the goods', 'shop'), ('Goodbye', 'bye')])
    elif o.name.startswith('The marshal'):
        ask(game, site, o.name, f'"Sellswords sign here. Three days of service, {fmt(SIGN_PAY)}, and you fight where '
            f'you are sent."', [(f'Sign on for three days ({fmt(SIGN_PAY)})', 'sign'), ('Goodbye', 'bye')])
    elif o.name == 'A man creeping off':
        ask(game, site, o.name, '"Not a word. I have a wife in the hills and the war is not mine."',
            [('Let him go', 'bye'), ('Call the guard (a deserter brings a reward)', 'deserter')], npc=o.id)
    else:
        game.say(o, random.choice(['They say we march at the new moon.', 'The bread is mouldy and the pay is late.',
                                   'Three of ours took fever. War is mostly waiting.']))


SIGN_PAY = 900


def _c_realmcamp(game, site, choice, ctx):
    if choice == 'shop':
        shop(game, site, 'sutler', 8)
    elif choice == 'sign':
        if not once(game, f'signed:{site.id}', 10):
            game.msg('"You served your days. Come back next week, if the war lasts."', 'talk')
            return
        game.player.gold += SIGN_PAY
        rep(game, 'crown', 3)
        game.end_turn(240)
        fight(game, ['soldier', 'soldier', 'knight'] if random.random() < .5 else ['soldier', 'soldier'],
              line='Three days of marching and digging, and then the enemy\'s scouts find your picket.')
        for o in game.map.mons:
            if not o.is_npc and o.k in ('soldier', 'knight'):
                o.faction = 'enemy'
    elif choice == 'deserter':
        o = next((x for x in game.map.mons if x.id == ctx.get('npc')), None)
        if o:
            game.map.mons.remove(o)
        game.player.gold += 300
        game.msg('Two soldiers drag him back to the lines. The clerk pays you three silver and writes your name down.', 'info')


PLACE['realmcamp'] = lambda lay: None
BUILD['realmcamp'], TALK['realmcamp'], CHOOSE['realmcamp'] = _m_realmcamp, _t_realmcamp, _c_realmcamp
LINES['realmcamp'] = 'Rows of tents, horse lines, the smell of smoke and latrines. Drums somewhere.'


# ---- the refugee camp after a village burned (daily)
def refugee_camps(game):
    from .living import plundered
    w = game.world
    om = game.maps['over']
    for st in [q for q in w.sites if q.kind == 'refugees']:
        s = w.settlements[st.village]
        st.gone = game.day > st.until
    for s in w.settlements:
        if not plundered(game, s) or any(q.kind == 'refugees' and q.village == s.id and not getattr(q, 'gone', False)
                                         for q in w.sites):
            continue
        if getattr(s, 'refugee_day', -99) >= game.day - 30:
            continue
        s.refugee_day = game.day
        spot = None
        taken = [(q.x, q.y) for q in w.settlements] + [(q.x, q.y) for q in w.sites if not getattr(q, 'gone', False)]
        for _ in range(200):
            x, y = s.x + random.randint(-6, 6), s.y + random.randint(-6, 6)
            if om.inb(x, y) and cheb(x, y, s.x, s.y) >= 3 and om.tile(x, y) in (D.GRASS, D.FOREST, D.HILLS) and \
                    all(cheb(x, y, a, b) >= 2 for a, b in taken):
                spot = (x, y)
                break
        if not spot:
            continue
        from .sites import Site
        st = Site(len(w.sites), 'refugees', spot[0], spot[1], f'The Refugees of {s.name}')
        st.faction, st.village, st.until = s.faction, s.id, game.day + 40
        w.sites.append(st)


def _m_refugees(game, site):
    m = land(game, site, 54, 30)
    cx, cy = m.w // 2, m.h // 2
    clear(m, cx, cy, 12, 7)
    for k in range(7):
        tent(m, cx - 10 + k * 3 + random.randint(0, 1), cy - 4 + random.randint(0, 6))
    m.set(cx, cy + 4, D.FIREPIT)
    way(m, (0, cy), (cx - 2, cy))
    npc(game, m, 'The reeve of ' + game.world.settlements[site.village].name, '#c8b090', cx + 2, cy + 2)
    for _ in range(5):
        npc(game, m, 'A refugee', '#a89880', cx + random.randint(-10, 10), cy + random.randint(-6, 6), stay=False)
    m.glows.append((cx, cy + 4, (255, 140, 60), 4))
    return finish(m, (0, cy))


def _t_refugees(game, site, o):
    s = game.world.settlements[site.village]
    if o.name.startswith('The reeve'):
        food_ = [i for i in game.player.inv if i.k == 'food']
        ask(game, site, o.name, f'"They burned {s.name} and took the herds. We wait until it is safe to go back, if '
            'there is anything to go back to. Children are hungry."',
            [('Give them food', 'food' if food_ else None), ('Give them a silver', 'coin'), ('Goodbye', 'bye')])
    else:
        game.say(o, random.choice(['They came at night. We ran with what we wore.', 'My barn, my cows. All gone.',
                                   'Do you have anything to eat?']))


def _c_refugees(game, site, choice, ctx):
    from . import gods as GD
    p = game.player
    if choice == 'food':
        it = next((i for i in p.inv if i.k == 'food'), None)
        if it is None:
            return
        if getattr(it, 'n', 1) > 1:
            it.n -= 1
        else:
            p.inv.remove(it)
        if once(game, f'alms:{site.id}', 3):
            GD.gain(game, 2, 'alms')
        game.msg('A woman takes it with both hands and says nothing, which says enough.', 'good')
    elif choice == 'coin' and pay(game, 100):
        if once(game, f'alms:{site.id}', 3):
            GD.gain(game, 2, 'alms')
        game.msg('The reeve counts it twice, and thanks you.', 'good')


PLACE['refugees'] = lambda lay: None
BUILD['refugees'], TALK['refugees'], CHOOSE['refugees'] = _m_refugees, _t_refugees, _c_refugees
LINES['refugees'] = 'Sheets over branches, a cart without a horse, children with big eyes. A whole village, under the sky.'


# ---- beacon hills: lit at night when war or raiders are near
def _p_beacon(lay):
    m = lay.m
    for _ in range(scaled(2)):
        start = lay.search(lambda x, y: m.tile(x, y) == D.HILLS and 3 <= lay.road(x, y) <= 12, 12)
        if not start:
            continue
        chain = [start]
        lay.add('beacon', start, 'Beacon Hill')
        for _k in range(3):
            x, y = chain[-1]
            nxt = lay.around(x, y, 6, 12, 5, lambda a, b: m.tile(a, b) == D.HILLS)
            if not nxt:
                break
            chain.append(nxt)
            lay.add('beacon', nxt, f'{random.choice(["Fire", "Watch", "Warning", "Bale"])} Hill')
        for k, (x, y) in enumerate(chain):
            st = next(q for q in lay.w.sites if (q.x, q.y) == (x, y))
            st.chain = chain


def lit(game, site):
    """A beacon burns at night in a war or with raiders near."""
    from . import powers as PW
    if site.kind != 'beacon' or not night(game):
        return False
    if at_war(game):
        return True
    return any(cheb(wd.x, wd.y, site.x, site.y) <= 25 for wd in game.world.wanderers
               if getattr(wd, 'kind', '') in ('raid', 'warband', 'host'))


def glyph(site, game=None):
    ch, fg = LOOK[site.kind]
    if game is not None and site.kind == 'beacon' and lit(game, site):
        return ('¥', (255, 150, 60))
    return ch, fg


def _m_beacon(game, site):
    m = land(game, site, 50, 30)
    cx, cy = m.w // 2, m.h // 2
    for y in range(m.h):
        for x in range(m.w):
            if ((x - cx) / 14) ** 2 + ((y - cy) / 8) ** 2 < 1 and m.tile(x, y) in (D.ROCK, TREE):
                m.set(x, y, GRASS)
    put(m, cx, cy, 'pyre')
    hut(m, cx + 4, cy + 2, 5, 4, 'w')
    way(m, (0, cy + 3), (cx - 1, cy + 1))
    npc(game, m, 'The beacon warden', '#c8b8a0', cx + 2, cy + 1)
    m.lookout = 12
    return finish(m, (0, cy + 3))


def _a_beacon(game, site, key, x, y):
    from .nature import lookout
    if lit(game, site):
        game.msg('The beacon roars. From up here you see the next one burning on its hill, and the next.', 'bad')
    return lookout(game, site)


def _t_beacon(game, site, o):
    game.say(o, 'When the next hill burns, I light mine. Then every village knows.' if not at_war(game) else
             'War. I sleep by the pile now, with the flint in my hand.')


PLACE['beacon'], BUILD['beacon'], ACT['beacon'], TALK['beacon'] = _p_beacon, _m_beacon, _a_beacon, _t_beacon
LINES['beacon'] = 'A bare hilltop, a great stack of timber and pitch, and the wind.'


# ---- the lighthouse
def _p_lighthouse(lay):
    m = lay.m
    for _ in range(scaled(2)):
        spot = lay.search(lambda x, y: m.tile(x, y) in (D.GRASS, D.HILLS, D.SAND) and lay.near_tile(x, y, (D.WATER,))
                          and not lay.river_near(x, y, 3) and sum(1 for a in (-2, 0, 2) for b in (-2, 0, 2)
                                                                  if m.inb(x + a, y + b) and m.tile(x + a, y + b) == D.WATER) >= 4, 15)
        if spot:
            lay.add('lighthouse', spot, f'The {random.choice(["Gull", "Grey", "Wreck", "Long", "North", "Saint"])} Light',
                    dark=False)


def _m_lighthouse(game, site):
    m = land(game, site, 54, 30)
    sea_side(m, 16)
    cx, cy = m.w - 22, m.h // 2
    hut(m, cx - 3, cy - 3, 7, 7, 's')
    put(m, cx, cy - 1, 'lamp')
    way(m, (0, cy), (cx, cy + 3))
    npc(game, m, 'The lighthouse keeper', '#d8d0b0', cx - 1, cy + 1)
    return finish(m, (0, cy))


def _a_lighthouse(game, site, key, x, y):
    if getattr(site, 'dark', False) and night(game):
        site.dark = False
        game.player.gold += 200
        rep(game, 'league', 2)
        game.msg('The great lamp was out: someone cut the wick. You trim it and light it, and the beam goes out over the '
                 'sea. In the morning the harbour master sends two silver by the keeper\'s boy.', 'good')
        return 3
    game.msg('A great lamp behind thick glass, and a mirror of polished brass.')
    return 0


def _t_lighthouse(game, site, o):
    game.say(o, random.choice(['Three sails today, all for the south. Wine, I would say, by how low they sit.',
                               'The wreckers hate this light. Twice they cut my wick. Twice I lit it again.',
                               'Storm coming. You can smell it.']))


def _e_lighthouse(game, site, m):
    if night(game) and random.random() < .2 and once(game, f'dark:{site.id}', 10):
        site.dark = True
        return 'The lighthouse is dark tonight. That should not be.'
    return None


PLACE['lighthouse'], BUILD['lighthouse'], ACT['lighthouse'], TALK['lighthouse'] = \
    _p_lighthouse, _m_lighthouse, _a_lighthouse, _t_lighthouse
ON_ENTER['lighthouse'] = _e_lighthouse
LINES['lighthouse'] = 'A white tower on the rocks over the sea, and a keeper\'s cottage at its foot.'


# ---- the baron's toll bridge
def _p_tollbridge(lay):
    m = lay.m
    made = 0
    cells = [i for i, v in enumerate(lay.riv) if v and 2 <= lay.w.road_dist[i] <= 6]
    random.shuffle(cells)
    for i in cells:
        if made >= scaled(2):
            break
        x, y = i % m.w, i // m.w
        spot = lay.around(x, y, 1, 1, 10)
        if not spot:
            continue
        far = (x + (x - spot[0]), y + (y - spot[1]))
        if not (m.inb(*far) and D.TILES[m.tile(*far)].walk and m.tile(*far) != D.RIVER):
            continue
        rg = lay.w.region_at(*spot)
        lay.add('tollbridge', spot, f'{rg.name} Toll Bridge', far=far, toll=random.choice((20, 30, 40)))
        made += 1


def _m_tollbridge(game, site):
    m = land(game, site, 54, 30)
    rx = river_through(m)
    cy = m.h // 2
    for x in range(rx - 4, rx + 5):
        m.set(x, cy, D.BRIDGE)
    put(m, rx - 6, cy - 1, 'tollgate')
    way(m, (0, cy), (rx - 5, cy))
    way(m, (rx + 5, cy), (m.w - 1, cy))
    hut(m, rx - 12, cy - 6, 5, 4, 's')
    npc(game, m, 'The toll keeper', '#c8a878', rx - 6, cy + 1)
    m.set(rx - 5, cy, FENCE)
    return finish(m, (0, cy))


def _t_tollbridge(game, site, o):
    from .money import fmt
    ask(game, site, o.name, f'"The baron\'s bridge, the baron\'s toll. {fmt(site.toll)} a head, and the far bank is yours. '
        'Or swim."', [(f'Pay the toll ({fmt(site.toll)})', 'pay'), ('Climb past the gate', 'sneak'), ('Goodbye', 'bye')])


def _c_tollbridge(game, site, choice, ctx):
    from . import crime as CR
    if choice == 'pay':
        if pay(game, site.toll, 'The toll'):
            to_world(game, *site.far, 4, 'You pay, the bar goes up, and you cross the river dry.')
    elif choice == 'sneak':
        if CR.commit(game, 4, 'dodging the baron\'s toll', witnessed=.5, near=(site.x, site.y)):
            game.msg('"Oi!" The toll keeper saw you.', 'bad')
        to_world(game, *site.far, 4, 'You swing round the end of the gate and run across.')


PLACE['tollbridge'], BUILD['tollbridge'], TALK['tollbridge'], CHOOSE['tollbridge'] = \
    _p_tollbridge, _m_tollbridge, _t_tollbridge, _c_tollbridge
LINES['tollbridge'] = 'A bridge of stone over the river, and a gate across it with a bar and a box.'


# ---- the caravanserai
def _p_serai(lay):
    m = lay.m
    long = lambda x, y: lay.near_tile(x, y, (D.ROAD,)) and all(cheb(x, y, s.x, s.y) >= 14 for s in lay.w.settlements)
    for k in range(scaled(3)):
        dry = lambda x, y: long(x, y) and lay.bio(x, y) in ('steppe', 'desert', 'savanna', 'shrubland', 'badlands', 'meadow')
        spot = lay.search(dry if k < 2 else long, 14, 8000, lay.by_road())
        if spot:
            lay.add('serai', spot, f'The {random.choice(["Camel", "Twelve Wells", "Silk", "Long Road", "Dust", "Star"])} Caravanserai')


def _m_serai(game, site):
    m = land(game, site, 56, 32)
    cx, cy = m.w // 2, m.h // 2
    x0, y0, x1, y1 = cx - 12, cy - 8, cx + 12, cy + 8
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            edge = y in (y0, y1) or x in (x0, x1)
            m.set(x, y, WALL if edge else PATH)
    m.set(x0, cy, PATH)
    for x in range(x0 + 1, x1):
        if x % 3 == 0:
            m.set(x, y0 + 1, WALL)
            m.set(x, y1 - 1, WALL)
    for x in range(x0 + 2, x1 - 1, 3):
        m.set(x, y0 + 2, BED)
    put(m, cx, cy, 'trough')
    for k in range(4):
        m.set(x1 - 3, cy - 3 + k * 2, FENCE)
    way(m, (0, cy), (x0, cy))
    npc(game, m, 'The keeper of the serai', '#e0c090', cx - 3, cy + 2)
    if random.random() < .5:
        npc(game, m, 'A caravan master', '#d0b080', cx + 4, cy - 2)
    return finish(m, (0, cy))


def _t_serai(game, site, o):
    from .money import fmt
    if o.name == 'A caravan master':
        ask(game, site, o.name, '"We leave at dawn for the south. Silk and pepper. Want to see what we carry?"',
            [('See the goods', 'shop'), ('Goodbye', 'bye')])
        return
    ask(game, site, o.name, '"Peace on your road. Water is free; a bed is not. Your beasts and wagons are safe in my '
        'yard: no robber climbs these walls."',
        [(f'A bowl of stew ({fmt(game.STEW)})', 'stew'), (f'A meal and a bed for the night ({fmt(game.MEAL)})', 'meal'),
         ('Any news from the road?', 'news'), ('Goodbye', 'bye')])


def _c_serai(game, site, choice, ctx):
    if choice == 'stew':
        game.inn_stew()
    elif choice == 'meal':
        game.inn_meal()
    elif choice == 'news':
        gossip(game)
    elif choice == 'shop':
        shop(game, site, 'caravan', 7)


def _e_serai(game, site, m):
    from . import caravan as CV
    cv = CV.get(game.player)
    if cv and cv.get('at') == ('xy', site.x, site.y):
        return 'Your wagons roll into the yard of the caravanserai, out of reach of any robber.'
    return None


PLACE['serai'], BUILD['serai'], TALK['serai'], CHOOSE['serai'] = _p_serai, _m_serai, _t_serai, _c_serai
ON_ENTER['serai'] = _e_serai
LINES['serai'] = 'High mud walls, one gate, and inside a court with a trough, beds under the arches and camels dozing.'


# ---- the prospectors' camp after a Starfall (daily)
def prospectors(game):
    w = game.world
    star = getattr(game, 'star', None)
    for st in [q for q in w.sites if q.kind == 'prospect']:
        st.gone = game.day > st.until
    if not star or star.get('camp') or game.day - star['day'] > 20:
        return
    om = game.maps['over']
    taken = [(s.x, s.y) for s in w.settlements] + [(q.x, q.y) for q in w.sites if not getattr(q, 'gone', False)]
    for _ in range(200):
        x, y = star['x'] + random.randint(-5, 5), star['y'] + random.randint(-5, 5)
        if om.inb(x, y) and D.TILES[om.tile(x, y)].walk and om.tile(x, y) not in (D.ROAD, D.TOWN, D.CITY) and \
                all(cheb(x, y, a, b) >= 2 for a, b in taken):
            from .sites import Site
            st = Site(len(w.sites), 'prospect', x, y, 'The Prospectors\' Camp')
            st.until = game.day + 30
            w.sites.append(st)
            star['camp'] = st.id
            return


def _m_prospect(game, site):
    m = land(game, site, 54, 30)
    cx, cy = m.w // 2, m.h // 2
    clear(m, cx, cy, 14, 8)
    for k in range(6):
        tent(m, cx - 12 + k * 4, cy - 5 + (k % 2) * 3)
    for k in range(5):
        put(m, cx - 8 + k * 4, cy + 4, 'claim')
    way(m, (0, cy), (cx - 2, cy))
    for nm in ('A prospector', 'A prospector', 'A claim jumper'):
        npc(game, m, nm, '#c8b890', cx + random.randint(-8, 8), cy + random.randint(-2, 3), stay=False)
    npc(game, m, 'The ore buyer', '#e0c070', cx + 2, cy)
    return finish(m, (0, cy))


def _t_prospect(game, site, o):
    from .money import fmt
    if o.name == 'The ore buyer':
        ask(game, site, o.name, f'"Star-iron splinters, a silver each, no questions. Or buy one: {fmt(STAR_PRICE)}. A smith '
            'will pay you more, if you know one."',
            [('Sell your splinters of star-iron', 'sell'), (f'Buy a splinter ({fmt(STAR_PRICE)})', 'buy'), ('Goodbye', 'bye')])
    elif o.name == 'A claim jumper':
        game.say(o, 'That stake is mine. Was always mine. Anyone says different gets the pick.')
    else:
        game.say(o, random.choice(['Three days digging and a handful of black grit.', 'Somebody found a lump as big as '
                                   'a fist. Somebody else knifed him for it.', 'Two more weeks and we are all gone again.']))


STAR_PRICE = 3500


def _c_prospect(game, site, choice, ctx):
    p = game.player
    if choice == 'sell':
        it = [i for i in p.inv if i.k == 'curio' and i.t == 'starshard']
        if not it:
            game.msg('You carry no star-iron.')
            return
        for i in it:
            p.inv.remove(i)
        p.gold += 100 * len(it)
        game.msg(f'The buyer weighs them and pays {len(it)} silver.', 'gold')
    elif choice == 'buy' and pay(game, STAR_PRICE):
        give(game, curio(game, 'starshard'))
        game.msg('A splinter of black star-iron, heavy for its size.', 'good')


def _a_prospect(game, site, key, x, y):
    if once(game, f'dig:{site.id}', 3):
        game.end_turn(30)
        if random.random() < .25:
            give(game, curio(game, 'starshard'))
            game.msg('You dig beside an empty claim and find a splinter of black iron. Nobody saw. Probably.', 'good')
        else:
            game.msg('You dig for an hour beside a stake. Black grit and stones.')
        return 0
    game.msg('A stake with a name burnt into it: this claim is taken.')
    return 0


PLACE['prospect'] = lambda lay: None
BUILD['prospect'], TALK['prospect'], CHOOSE['prospect'], ACT['prospect'] = _m_prospect, _t_prospect, _c_prospect, _a_prospect
LINES['prospect'] = 'Tents thrown up anyhow, stakes with names on them, and everyone digging, and everyone watching everyone.'


# ---- a lord's hunting lodge
def _p_lodge(lay):
    m = lay.m
    for _ in range(scaled(2)):
        spot = lay.search(lambda x, y: m.tile(x, y) == D.FOREST and 2 <= lay.road(x, y) <= 8, 12)
        if spot:
            lay.add('lodge', spot, f'The {random.choice(["King", "Baron", "Earl"])}\'s Lodge')


def _m_lodge(game, site):
    m = land(game, site, 64, 36)
    for i in range(m.w * m.h):
        if m.t[i] == GRASS and random.random() < .2:
            m.t[i] = TREE
    cx, cy = 14, m.h // 2
    clear(m, cx, cy, 8, 6)
    d = hut(m, cx - 4, cy - 3, 9, 6, 's')
    put(m, d[0] + 2, d[1] - 6, 'trophy')
    way(m, (0, cy + 4), (d[0], d[1] + 1))
    npc(game, m, 'The gamekeeper', '#a8c890', cx + 4, cy + 4, stay=False)
    beasts(game, m, ['red_deer', 'red_deer', 'red_deer', 'boar'], (m.w - 16, cy), r=12)
    return finish(m, (0, cy + 4))


def _t_lodge(game, site, o):
    game.say(o, random.choice(['This is the lord\'s wood. Walk through it, by all means. Do not hunt in it.',
                               'A poacher loses a hand, in the old law. The lord is kinder. He only hangs them.',
                               'The lord comes in autumn with his hounds. Until then the deer are mine to count.']))


def _a_lodge(game, site, key, x, y):
    game.msg('Antlers over the door, dozens of them, each with a date burnt under it.')
    return 0


PLACE['lodge'], BUILD['lodge'], TALK['lodge'], ACT['lodge'] = _p_lodge, _m_lodge, _t_lodge, _a_lodge
LINES['lodge'] = 'A timber lodge with antlers over the door, and an old wood full of deer. The lord\'s deer.'


# ================================================================== the peoples and powers of today
# ---- the realms: a boundary stone, a lone inn, a mill, a bridge chapel
def _p_bstone(lay):
    m, w = lay.m, lay.w
    R = w.realm
    made = 0
    edge = [(x, y) for y in range(4, m.h - 4) for x in range(4, m.w - 5)
            if w.region_of[y * m.w + x] != w.region_of[y * m.w + x + 1] and w.road_dist[y * m.w + x] <= 4]
    random.shuffle(edge)
    for x, y in edge:
        if made >= scaled(3):
            break
        r0 = w.region_of[y * m.w + x]
        r1 = w.region_of[y * m.w + x + 1]
        if r0 not in R.baronies or r1 not in R.baronies or not lay.free(x, y, 3):
            continue
        lay.add('bstone', (x, y), f'The Stone of {R.baronies[r0].name} and {R.baronies[r1].name}', sides=(r0, r1))
        made += 1


def _m_simple(things, who=(), size=(50, 28), clearing=(8, 5)):
    def fn(game, site):
        m = plain(game, site, things, who, size, clearing=clearing)
        return finish(m, (0, m.h // 2))
    return fn


def _a_bstone(game, site, key, x, y):
    R = game.world.realm
    a, b = (R.baronies[r] for r in site.sides)
    moved = (game.day // 30 + site.id) % 3 == 0
    text = (f'A grey stone as high as your hip. On one face the arms of {a.name}, on the other those of {b.name}.')
    if moved and not done(game, f'reset:{site.id}:{game.day // 30}'):
        text += (' The grass round its foot is torn: it was dug up and set down again, a good stone\'s throw into '
                 f'{b.name}\'s land, at night. The old hole is still there.')
        ask(game, site, 'The stone', text, [('Set it back in its old hole', 'reset'), ('Leave it', 'bye')])
        return 0
    chron(game, site, f'{site.name}: the border of {a.name} and {b.name}.')
    say(game, site, text)
    return 0


def _c_bstone(game, site, choice, ctx):
    if choice == 'reset' and once(game, f'reset:{site.id}:{game.day // 30}'):
        game.end_turn(40)
        rep(game, 'crown', 2)
        game.player.gold += 150
        game.msg('It takes an hour and all your back. A shepherd who watched comes over and gives you a silver and a '
                 'half, from the reeve, he says, who will be glad.', 'good')


PLACE['bstone'], BUILD['bstone'], ACT['bstone'], CHOOSE['bstone'] = \
    _p_bstone, _m_simple([(0, 0, 'bstone')]), _a_bstone, _c_bstone
LINES['bstone'] = 'A grey stone by the track, where one barony ends and another begins.'


def _p_loneinn(lay):
    m, w = lay.m, lay.w
    for k in range(scaled(3)):
        far = 16 if k < 2 else 10
        spot = lay.search(lambda x, y: lay.near_tile(x, y, (D.ROAD,)) and all(cheb(x, y, s.x, s.y) >= far for s in w.settlements)
                          and m.tile(x, y) in (D.GRASS, D.FOREST, D.HILLS, D.SAND), 16, 8000, lay.by_road())
        if spot:
            from .sites import ROADINN_NAMES
            lay.add('loneinn', spot, random.choice(ROADINN_NAMES))


def _m_loneinn(game, site):
    m = land(game, site, 54, 30)
    cx, cy = m.w // 2, m.h // 2
    clear(m, cx, cy, 12, 7)
    d = hut(m, cx - 6, cy - 5, 13, 8, 's')
    for x in range(cx - 4, cx + 5, 3):
        m.set(x, cy - 3, TABLE)
    m.set(cx + 5, cy - 4, D.HEARTH)
    for x in range(cx - 5, cx + 6, 2):
        m.set(x, cy - 1, D.BED) if x > cx + 1 else None
    way(m, (0, cy + 3), (d[0], d[1] + 1))
    way(m, (d[0], d[1] + 1), (m.w - 1, cy + 3))
    npc(game, m, 'The innkeeper', '#e0a060', cx, cy - 2, role='roadinn')
    if random.random() < .3:
        npc(game, m, 'A hard-faced drinker', '#a09080', cx - 3, cy - 2)
    m.glows.append((cx + 5, cy - 4, (255, 140, 60), 4))
    return finish(m, (0, cy + 3))


def _t_loneinn(game, site, o):
    if o.name == 'A hard-faced drinker':
        ask(game, site, o.name, '"Long road, eh? Long and empty. A man could lose his purse out there." He looks at yours.',
            [('Buy him a drink (5c)', 'drink'), ('Tell him to look elsewhere', 'warn'), ('Goodbye', 'bye')], npc=o.id)
    else:
        game.say(o, 'Welcome.')


def _c_loneinn(game, site, choice, ctx):
    o = next((x for x in game.map.mons if x.id == ctx.get('npc')), None)
    if choice == 'drink' and pay(game, 5):
        game.msg('He drinks, and tells you which stretch of road his friends work, so that you can go round it.', 'info')
        gossip(game)
    elif choice == 'warn' and o:
        game.map.mons.remove(o)
        from .entities import make_monster
        b = make_monster(game, 'brigand', o.x, o.y, game.map.level)
        b.awake = True
        game.map.mons.append(b)
        game.msg('He stands up slowly, and the knife is already in his hand.', 'bad')


PLACE['loneinn'], BUILD['loneinn'], TALK['loneinn'], CHOOSE['loneinn'] = _p_loneinn, _m_loneinn, _t_loneinn, _c_loneinn
LINES['loneinn'] = 'A lone inn by the long road, smoke from its chimney, and nothing else in sight.'


def _p_mill(lay):
    m, w = lay.m, lay.w
    vill = [s for s in w.settlements if s.kind in ('village', 'town') and s.race == 'human']
    random.shuffle(vill)
    made = 0
    for s in vill:
        if made >= scaled(3):
            break
        spot = lay.around(s.x, s.y, 2, 6, 3, lambda x, y: lay.river_near(x, y, 1))
        if spot:
            lay.add('mill', spot, f'{s.name} Mill', village=s.id)
            made += 1


def _m_mill(game, site):
    m = land(game, site, 52, 30)
    rx = river_through(m, m.w // 2 + 8, 1)
    cx, cy = rx - 9, m.h // 2
    clear(m, cx, cy, 7, 5)
    hut(m, cx - 3, cy - 3, 7, 6, 'w')
    put(m, cx + 4, cy, 'wheel')
    way(m, (0, cy), (cx - 3, cy))
    npc(game, m, 'The miller', '#e8e0d0', cx - 5, cy + 1)
    return finish(m, (0, cy))


def _still(game):
    from . import calendar as CAL
    # one summer in three the stream runs too low to turn the wheel
    return CAL.season(game.day) == 'summer' and (CAL._split(game.day)[0] + game.seed) % 3 == 0


def _t_mill(game, site, o):
    from .money import fmt
    if _still(game):
        game.say(o, 'The stream is too low to turn the wheel. Come back after the rain.')
        return
    ask(game, site, o.name, f'"Flour for the village, bread for whoever asks. Three loaves, {fmt(MILL_BREAD)}: cheaper '
        'than any baker."', [(f'Buy three loaves ({fmt(MILL_BREAD)})', 'bread'), ('Goodbye', 'bye')])


MILL_BREAD = 12


def _c_mill(game, site, choice, ctx):
    if choice == 'bread' and pay(game, MILL_BREAD):
        give(game, food(game, 'bread', 3))
        game.msg('Three loaves, still warm.', 'good')


def _a_mill(game, site, key, x, y):
    game.msg('The wheel stands still in a trickle of water.' if _still(game) else 'The wheel turns and drips, slow and loud.')
    return 0


PLACE['mill'], BUILD['mill'], TALK['mill'], CHOOSE['mill'], ACT['mill'] = _p_mill, _m_mill, _t_mill, _c_mill, _a_mill
LINES['mill'] = 'A mill by the stream, flour dust in the doorway, the wheel turning.'


def _p_bchapel(lay):
    m = lay.m
    cells = [i for i, t in enumerate(m.t) if t == D.BRIDGE or (lay.riv[i] and lay.w.road_dist[i] == 0)]
    random.shuffle(cells)
    made = 0
    for i in cells:
        if made >= scaled(2):
            break
        x, y = i % m.w, i // m.w
        spot = lay.around(x, y, 1, 2, 8)
        if spot:
            lay.add('bchapel', spot, f'The Chapel of Saint {random.choice(["Aldra", "Corwen", "Brannoc", "Edith", "Ninian", "Hild"])} on the Bridge')
            made += 1


def _m_bchapel(game, site):
    m = land(game, site, 50, 28)
    rx = river_through(m)
    cy = m.h // 2
    for x in range(rx - 4, rx + 5):
        m.set(x, cy, D.BRIDGE)
        m.set(x, cy - 1, D.BRIDGE)
    hut(m, rx - 2, cy - 5, 5, 4, 's')
    m.set(rx, cy - 2, D.BRIDGE)
    put(m, rx, cy - 4, 'altar')
    way(m, (0, cy), (rx - 5, cy))
    way(m, (rx + 5, cy), (m.w - 1, cy))
    return finish(m, (0, cy))


def _a_bchapel(game, site, key, x, y):
    from . import gods as GD
    god = GD.temple_god(game) if hasattr(GD, 'temple_god') else None
    if not once(game, f'pray:{site.id}', 3):
        game.msg('You prayed here not long ago. The candles you lit still burn.')
        return 0
    if game.player.gold >= 5:
        game.player.gold -= 5
    buff(game, 'swift', 1, 600, 'Blessing of the Road', 'You leave a coin and a prayer for the road. Your feet feel '
         'lighter. (Blessing of the Road: you travel faster for a while.)')
    return 1


PLACE['bchapel'], BUILD['bchapel'], ACT['bchapel'] = _p_bchapel, _m_bchapel, _a_bchapel
LINES['bchapel'] = 'A little chapel stands on the old bridge, with candles inside and the river loud under it.'


# ---- the Church: a pilgrims' chapel, a tithe barn, a holy well, a plague cross
def _p_pilg(lay):
    m = lay.m
    for _ in range(scaled(2)):
        spot = lay.search(lambda x, y: m.tile(x, y) == D.HILLS and lay.near_tile(x, y, (D.MOUNTAIN,), 1) and lay.road(x, y) <= 10, 14)
        if spot:
            lay.add('pilgchapel', spot, f'The Chapel on {random.choice(["Hermon", "the Crag", "Saint Edda\'s Rock", "the Height", "Skell\'s Tooth"])}')


def _m_pilg(game, site):
    m = land(game, site, 50, 40)
    cx = m.w // 2
    for y in range(m.h):
        for x in range(m.w):
            if abs(x - cx) > 3 + y // 2 and y < 26:
                m.set(x, y, D.CLIFF if random.random() < .8 else D.ROCK)
            elif y < 26:
                m.set(x, y, D.BAREROCK)
    for y in range(6, m.h - 1):
        m.set(cx + int(2 * math.sin(y * .7)), y, D.STEPS)
    hut(m, cx - 3, 1, 7, 5, 's')
    put(m, cx, 2, 'chapel')
    npc(game, m, 'A pilgrim', '#e0d8c0', cx + 2, 30)
    return finish(m, (0, m.h - 4))


def _a_pilg(game, site, key, x, y):
    from . import gods as GD
    if done(game, f'pilgrim:{site.id}'):
        game.msg('A cold little chapel, a bell rope, and your own name scratched among the others by the door.')
        return 0
    once(game, f'pilgrim:{site.id}')
    GD.gain(game, 5, 'pilgrimage')
    give(game, curio(game, 'pilgtoken'))
    chron(game, site, f'{site.name}: you climbed the steps to the pilgrims\' chapel and rang the bell.')
    game.msg('You ring the bell. Far below, the land is small. The old monk who keeps the chapel ties a lead token on a '
             'cord round your wrist: the sign of a pilgrim.', 'good')
    return 5


PLACE['pilgchapel'], BUILD['pilgchapel'], ACT['pilgchapel'] = _p_pilg, _m_pilg, _a_pilg
TALK['pilgchapel'] = lambda game, site, o: gossip(game, o)
LINES['pilgchapel'] = 'Steps cut in the rock wind up and up to a chapel on the top. The wind tears at your cloak.'


def _p_tithe(lay):
    m, w = lay.m, lay.w
    vill = [s for s in w.settlements if s.kind in ('village', 'town') and s.race == 'human' and s.faction == 'crown']
    random.shuffle(vill)
    for s in vill[:scaled(2)]:
        spot = lay.around(s.x, s.y, 2, 5, 3, lambda x, y: m.tile(x, y) == D.GRASS)
        if spot:
            lay.add('tithe', spot, f'The Tithe Barn of {s.name}', village=s.id)


def _m_tithe(game, site):
    m = land(game, site, 56, 30)
    cx, cy = m.w // 2, m.h // 2
    for y in range(m.h):
        for x in range(m.w):
            if m.tile(x, y) == GRASS and (x < cx - 12 or x > cx + 12):
                m.set(x, y, FIELD)
    clear(m, cx, cy, 10, 6)
    d = hut(m, cx - 7, cy - 4, 15, 8, 's')
    m.set(*d, WALL)
    put(m, *d, 'barn')
    way(m, (0, cy + 5), (d[0], d[1] + 1))
    npc(game, m, 'The tithe-keeper', '#d0c0a0', d[0] + 2, d[1] + 2)
    npc(game, m, 'A guard of the Church', '#d8d8e0', d[0] - 2, d[1] + 1)
    return finish(m, (0, cy + 5))


def _t_tithe(game, site, o):
    PW = game.world.powers
    rev = PW.get('revolt')
    opts = [('Any news?', 'news'), ('Goodbye', 'bye')]
    if rev:
        opts.insert(0, ('Open the barn for the hungry villages', 'open'))
    ask(game, site, o.name, '"The barn of the Church. Move along."' if not rev else
        '"The villages are up in arms, and they look at this barn like wolves at a fold."', opts)


def _c_tithe(game, site, choice, ctx):
    from . import crime as CR
    if choice == 'news':
        gossip(game)
    elif choice == 'open' and once(game, f'opened:{site.id}', 60):
        CR.commit(game, 15, 'breaking open the tithe barn', witnessed=.8, near=(site.x, site.y))
        rep(game, 'crown', -4)
        from . import gods as GD
        GD.gain(game, 3, 'alms')
        game.msg('You knock the bar off the door. By evening the carts of three villages have come and gone, and the '
                 'barn is empty. Someone writes your name on the door, with a heart.', 'info')


PLACE['tithe'], BUILD['tithe'], TALK['tithe'], CHOOSE['tithe'] = _p_tithe, _m_tithe, _t_tithe, _c_tithe
ACT['tithe'] = lambda game, site, key, x, y: game.msg('A great oak door, barred and sealed with the bishop\'s wax.') or 0
LINES['tithe'] = 'A barn as big as a church, in the middle of the fields. The Church\'s tenth of every harvest is in it.'

SAINTS = ['Saint Edith', 'Saint Ninian', 'Saint Aldra', 'Old Mother Hild', 'Saint Brannoc', 'Saint Wendel', 'the Blind Monk',
          'Saint Corwen', 'the Drowned Girl']


def _p_hwell(lay):
    m = lay.m
    for _ in range(scaled(3)):
        spot = lay.search(lambda x, y: m.tile(x, y) in (D.GRASS, D.FOREST, D.HILLS) and 1 <= lay.road(x, y) <= 8, 12)
        if spot:
            saint = random.choice(SAINTS)
            lay.add('hwell', spot, f'The Well of {saint}', saint=saint)


def _a_hwell(game, site, key, x, y):
    if not once(game, f'drink:{site.id}', 1):
        game.msg('You drank from the well today. It is the same water.')
        return 0
    heal(game, .25)
    game.player.__dict__.pop('cold', None)
    chron(game, site, f'{site.name}: a holy well. Its water eases small ills, once a day.')
    game.msg(f'You drink the cold water of {site.saint}. Your aches ease, and whatever sat in your stomach is gone.', 'good')
    return 1


PLACE['hwell'], BUILD['hwell'], ACT['hwell'] = _p_hwell, _m_simple([(0, 0, 'well')], size=(44, 26)), _a_hwell
LINES['hwell'] = 'A well under an old thorn, rags tied in its branches: the prayers of the sick.'


def _p_pcross(lay):
    m = lay.m
    ring = (1, -1, m.w, -m.w, m.w + 1, m.w - 1, -m.w + 1, -m.w - 1)
    cross = [i for i, t in enumerate(m.t) if t == D.ROAD and sum(1 for o in ring if 0 <= i + o < len(m.t)
                                                                  and m.t[i + o] == D.ROAD) >= 3]
    random.shuffle(cross)
    made = 0
    for i in cross:
        if made >= scaled(2):
            break
        spot = lay.around(i % m.w, i // m.w, 1, 2, 8)
        if spot:
            lay.add('pcross', spot, 'The Plague Cross')
            made += 1


def _a_pcross(game, site, key, x, y):
    from . import gods as GD
    text = ('A stone cross on three steps, worn by weather. In the top step a hollow, where bread and coins were left for '
            'the sick of the plague years, washed in vinegar.')
    chron(game, site, f'{site.name}: where bread was left for the sick in the plague years.')
    say(game, site, text)
    if night(game) and once(game, f'vigil:{site.id}', 5):
        GD.gain(game, 2, 'vigil')
        game.msg('A priest comes at dusk, as one does every evening, and prays for the dead of the plague. You pray '
                 'with him.', 'good')
    return 0


PLACE['pcross'], BUILD['pcross'], ACT['pcross'] = _p_pcross, _m_simple([(0, 0, 'cross')], size=(44, 26)), _a_pcross
LINES['pcross'] = 'A stone cross where the roads meet, with a hollow in its lowest step.'


# ---- the Watch, the companies, the revolt
def _p_blockhouse(lay):
    m, w = lay.m, lay.w
    if not w.powers.get('watch'):
        return
    for _ in range(scaled(2)):
        spot = lay.search(lambda x, y: lay.near_tile(x, y, (D.ROAD,)) and y < m.h * .55 and
                          all(cheb(x, y, s.x, s.y) >= 8 for s in w.settlements), 12)
        if spot:
            lay.add('blockhouse', spot, f'The {random.choice(["Ford", "Pike", "Crow", "Gap", "Stone"])} Blockhouse')


def _m_blockhouse(game, site):
    m = land(game, site, 52, 30)
    cx, cy = m.w // 2, m.h // 2
    clear(m, cx, cy, 10, 6)
    d = hut(m, cx - 4, cy - 4, 9, 6, 's')
    put(m, d[0] - 2, d[1] + 1, 'posters')
    put(m, cx + 7, cy, 'cage')
    way(m, (0, cy + 3), (m.w - 1, cy + 3))
    npc(game, m, 'The sergeant of the Watch', '#b0b8d0', d[0] + 1, d[1] + 1)
    npc(game, m, 'A watchman', '#a0a8c0', cx - 6, cy + 3)
    return finish(m, (0, cy + 3))


def _a_blockhouse(game, site, key, x, y):
    from . import crime as CR
    if key == 'posters':
        wanted = CR.wanted_in(game)
        near = [s for s in wanted if cheb(s.x, s.y, site.x, site.y) <= 45]
        text = ('Posters nailed one over the other: outlaws, deserters, a horse thief with a drawing that could be anyone. '
                'Rewards in silver.')
        if near:
            text += ' One of them, new, could be you. Better not stand here long.'
        say(game, site, text, 'The posters')
        return 0
    ask(game, site, 'A man in the cage', '"Water, friend. And a word: the clearing with the marked oak, two days east '
        'of the Watch. That is where the risings meet. Get me out and I tell you more."',
        [('Give him water', 'water'), ('Goodbye', 'bye')])
    return 0


def _c_blockhouse(game, site, choice, ctx):
    if choice == 'water':
        game.msg('He drinks like a horse, and tells you of the risings: who leads them, and where they meet.', 'info')
        from .folk import discover
        cl = sorted((q for q in game.world.sites if q.kind == 'outlaws'), key=lambda q: cheb(q.x, q.y, site.x, site.y))
        if cl and getattr(cl[0], 'found', True) is False:
            discover(game, cl[0], 'The prisoner told you the way.')
    elif choice == 'report':
        cl = game.world.sites[ctx['clearing']]
        if once(game, f'betray:{cl.id}'):
            cl.betrayed = game.day
            game.player.gold += 1500
            rep(game, 'crown', 4)
            game.msg('The sergeant writes it down, and counts fifteen silver into your hand. "The Watch thanks you."', 'gold')


def _t_blockhouse(game, site, o):
    opts = [('Goodbye', 'bye')]
    known = [q for q in game.world.sites if q.kind == 'outlaws' and getattr(q, 'found', False) and not getattr(q, 'betrayed', None)]
    if known:
        opts.insert(0, ('Tell him where the outlaws meet (15s)', 'report'))
    ask(game, site, o.name, '"Papers? No? Nobody has papers out here. Keep your nose clean and the road is yours. If you '
        'know where outlaws hide, the Watch pays."', opts, clearing=known[0].id if known else None)


PLACE['blockhouse'], BUILD['blockhouse'], ACT['blockhouse'], TALK['blockhouse'], CHOOSE['blockhouse'] = \
    _p_blockhouse, _m_blockhouse, _a_blockhouse, _t_blockhouse, _c_blockhouse
LINES['blockhouse'] = 'A blockhouse of logs with arrow slits, a cage by the road, and a board of posters by the door.'


def _p_winterq(lay):
    m = lay.m
    for _ in range(scaled(1)):
        spot = lay.search(lambda x, y: m.tile(x, y) == D.GRASS and 3 <= lay.road(x, y) <= 8, 14)
        if spot:
            lay.add('winterq', spot, f'{random.choice(["Crow", "Long", "Black", "Hollow"])} Farm', company=random.choice(
                ['the Grey Company', 'the Free Lances', 'the Red Hands', 'the Wolves of Saint Corwen', 'the Lantern Company']))


def winter(game):
    from . import calendar as CAL
    return CAL.season(game.day) == 'winter'


def _m_winterq(game, site):
    m = land(game, site, 56, 30)
    cx, cy = m.w // 2, m.h // 2
    clear(m, cx, cy, 12, 7)
    d = hut(m, cx - 8, cy - 5, 11, 7, 's')
    hut(m, cx + 4, cy - 4, 7, 5, 's')
    fence_ring(m, cx - 12, cy + 3, cx + 10, cy + 7, (cx - 12, cy + 5))
    if winter(game):
        put(m, d[0] + 2, d[1] - 2, 'dice')
        npc(game, m, 'The captain', '#d8b880', d[0], d[1] + 1)
        for k in range(4):
            npc(game, m, 'A bored sellsword', '#b8a890', cx + random.randint(-9, 9), cy + random.randint(-1, 2), stay=False)
        from . import mercs as MC
        o = MC.make_offer(game)
        r = npc(game, m, f'{o["name"]}, sellsword', '#d8c8a0', d[0] + 3, d[1] + 1, role='recruit')
        if r:
            r.offer = o
    way(m, (0, cy), (d[0], d[1] + 1))
    return finish(m, (0, cy))


def _t_winterq(game, site, o):
    if o.name == 'The captain':
        ask(game, site, o.name, f'"{site.company[0].upper() + site.company[1:]}, wintering. No war, no pay. We sell what we '
            'do not need. Blades, mostly."', [('See what they sell', 'shop'), ('Goodbye', 'bye')])
    else:
        game.say(o, random.choice(['Roll you for it?', 'Spring. Spring, and a war somewhere, please.',
                                   'The captain owes me three months. He owes everyone three months.']))


def _a_winterq(game, site, key, x, y):
    ask(game, site, 'The dice table', '"Five copper a throw, high wins," says the man with the cup.',
        [('Throw (5c)', 'dice'), ('Goodbye', 'bye')])
    return 0


def _c_winterq(game, site, choice, ctx):
    if choice == 'shop':
        shop(game, site, 'arms', 7, kinds=('weapon', 'armor', 'shield', 'helm'))
    elif choice == 'dice' and pay(game, 5):
        a, b = random.randint(2, 12), random.randint(2, 12)
        if a > b:
            game.player.gold += 10
        game.msg(f'You throw {a}, he throws {b}. ' + ('You win five copper.' if a > b else 'He takes your coin.'),
                 'good' if a > b else 'info')


PLACE['winterq'], BUILD['winterq'], TALK['winterq'], ACT['winterq'], CHOOSE['winterq'] = \
    _p_winterq, _m_winterq, _t_winterq, _a_winterq, _c_winterq
ON_ENTER['winterq'] = lambda game, site, m: (f'{site.company[0].upper() + site.company[1:]} winters here: smoke from the '
                                              'chimneys, horses in the yard, men with nothing to do.' if winter(game) else
                                              'An empty farm. In winter a sellsword company lives here; now only the swallows.')


def _p_outlaws(lay):
    m = lay.m
    for _ in range(scaled(2)):
        spot = lay.search(lambda x, y: m.tile(x, y) == D.FOREST and 5 <= lay.road(x, y) <= 14, 12)
        if spot:
            lay.add('outlaws', spot, f'The {random.choice(["Hanging", "Moot", "Gospel", "Robin\'s", "Free"])} Oak', hidden=True)


def _m_outlaws(game, site):
    m = land(game, site, 52, 30)
    cx, cy = m.w // 2, m.h // 2
    clear(m, cx, cy, 8, 5)
    put(m, cx, cy - 2, 'oak')
    for a in range(10):
        x, y = cx + int(5 * math.cos(a * .63)), cy + 1 + int(3 * math.sin(a * .63))
        if m.tile(x, y) == GRASS:
            m.set(x, y, D.STONE)
    way(m, (0, cy), (cx - 6, cy))
    rev = game.world.powers.get('revolt')
    if rev and not getattr(site, 'betrayed', None):
        npc(game, m, 'A rebel with a bow', '#a0c080', cx + 2, cy + 2)
        npc(game, m, 'A rebel', '#90b070', cx - 3, cy + 1)
    return finish(m, (0, cy))


def _t_outlaws(game, site, o):
    rev = game.world.powers.get('revolt')
    s = game.world.settlements[rev['sid']] if rev else None
    text = (f'"{rev["leader"]} leads us, from the camp near {s.name}. The barons tax us to death and send our sons to '
            'their wars. Tell nobody you saw us."' if rev else '"Nothing to see here, traveller."')
    game.request = ('dialog', o.name, text)


def _a_outlaws(game, site, key, x, y):
    chron(game, site, f'{site.name}: an oak with a mark cut in it, where the risings of the villages meet.')
    say(game, site, 'An old oak with a mark cut deep in its bark: a sickle crossed with a key. Under it, a ring of stumps '
        'to sit on, and the ashes of a fire, not cold.' if game.world.powers.get('revolt') else
        'An old oak with a mark cut deep in its bark: a sickle crossed with a key. The risings of other years met here.')
    return 0


PLACE['outlaws'], BUILD['outlaws'], TALK['outlaws'], ACT['outlaws'] = _p_outlaws, _m_outlaws, _t_outlaws, _a_outlaws
LINES['outlaws'] = 'A clearing deep in the wood, round an old oak. Someone was here not long ago.'


# ---- the witches
def _p_witchcot(lay):
    m = lay.m
    for _ in range(scaled(2)):
        spot = lay.search(lambda x, y: m.tile(x, y) in (D.FOREST, D.SWAMP) and lay.road(x, y) >= 8, 14)
        if spot:
            from .races import random_name
            lay.add('witchcot', spot, f'{random.choice(["Mother", "Granny", "Old"])} {random_name("human", "female", family=False)}\'s Cottage')


def _m_witchcot(game, site):
    m = land(game, site, 50, 28)
    cx, cy = m.w // 2, m.h // 2
    clear(m, cx, cy, 7, 5)
    d = hut(m, cx - 3, cy - 3, 7, 5, 's')
    put(m, cx + 4, cy + 2, 'cauldron')
    for k in range(5):
        m.set(cx - 6 + k * 3, cy + 4, D.SHROOM) if m.tile(cx - 6 + k * 3, cy + 4) == GRASS else None
    way(m, (0, cy + 3), (d[0], d[1] + 1))
    npc(game, m, site.name.replace("'s Cottage", ''), '#a8d098', cx, cy - 1, race='human')
    return finish(m, (0, cy + 3))


def _t_witchcot(game, site, o):
    ask(game, site, o.name, '"Hurt? Cursed? Sick in the heart? I can mend it all. Not for coin, dearie. Coin is for '
        'fools. A lock of your hair, say. Or a little of your luck. Or one favour, some day."',
        [('Be healed, for a lock of your hair', 'hair'), ('Be healed, for a little of your luck', 'luck'),
         ('Buy herbs, no questions asked', 'herbs'), ('Goodbye', 'bye')])


def _c_witchcot(game, site, choice, ctx):
    p = game.player
    if choice in ('hair', 'luck'):
        heal(game, 1.0)
        p.buffs = [b for b in p.buffs if b[1] >= 0]
        if choice == 'luck':
            buff(game, 'dmg', -10, 800, 'Luck given away', 'She mutters over you and you are whole, every curse lifted. '
                 'But for a long while your blows land a little less true. (-10% damage)')
        else:
            marks(game)['witch_hair'] = game.day
            game.msg('She snips a lock of your hair and puts it in a jar with a lid. Every curse lifts, every wound closes. '
                     'She smiles. "Now I can always find you."', 'good')
    elif choice == 'herbs':
        from .foraging import make_plant
        for k in random.sample(['wolfsbane', 'valerian', 'mugwort', 'nightshade', 'kingsfoil', 'moonpetal'], 2):
            if pay(game, 30):
                give(game, make_plant(game, k, 2))
        game.msg('Two bundles of herbs, tied with black thread.', 'info')


def witch_night(game):
    """Who gave her a lock of hair may hear from her some night."""
    mk = marks(game)
    if 'witch_hair' in mk and night(game) and game.day - mk['witch_hair'] >= 20 and random.random() < .05:
        del mk['witch_hair']
        buff(game, 'dmg', -15, 300, 'The witch\'s pull', 'You dream of a jar with a lid, and wake weak. The witch has '
             'taken her price. (-15% damage for a while)')


PLACE['witchcot'], BUILD['witchcot'], TALK['witchcot'], CHOOSE['witchcot'] = _p_witchcot, _m_witchcot, _t_witchcot, _c_witchcot
ACT['witchcot'] = lambda game, site, key, x, y: game.msg('Something green bubbles in the cauldron. It smells of '
                                                         'river mud and violets.') or 0
LINES['witchcot'] = 'A crooked cottage with a turf roof, smoke going up straight. Mushrooms in rings round it.'


def _p_hangtree(lay):
    m, w = lay.m, lay.w
    vill = [s for s in w.settlements if s.kind in ('village', 'hamlet') and s.race == 'human']
    random.shuffle(vill)
    for s in vill[:scaled(2)]:
        spot = lay.around(s.x, s.y, 1, 3, 2)
        if spot:
            lay.add('hangtree', spot, f'The Hanging Tree of {s.name}')


def _m_hangtree(game, site):
    m = plain(game, site, [(0, 0, 'htree')], size=(44, 26))
    if night(game):
        npc(game, m, 'A woman in grey', '#c8c8d8', m.centre[0] + 1, m.centre[1] + 1)
    return finish(m, (0, m.h // 2))


def _t_hangtree(game, site, o):
    from .folk import discover
    circ = sorted((q for q in game.world.sites if q.kind == 'circle'), key=lambda q: cheb(q.x, q.y, site.x, site.y))
    if circ and not getattr(circ[0], 'found', True):
        discover(game, circ[0], 'The woman in grey lifts her hand and points, and is gone.')
    else:
        game.msg('She looks at you and says nothing. When you look again, nobody stands under the tree.', 'info')
    if o in game.map.mons:
        game.map.mons.remove(o)


def _a_hangtree(game, site, key, x, y):
    chron(game, site, f'{site.name}: where they hanged witches, long ago.')
    say(game, site, 'An old oak with one low, long branch, worn smooth where the ropes went. They hanged witches here '
        'in the old days, three in one year. The village children dare each other to touch it.')
    return 0


PLACE['hangtree'], BUILD['hangtree'], TALK['hangtree'], ACT['hangtree'] = _p_hangtree, _m_hangtree, _t_hangtree, _a_hangtree
ON_ENTER['hangtree'] = lambda game, site, m: ('Under the hanging tree stands a woman in grey, quite still.' if night(game)
                                              else 'An old oak at the edge of the village, with one long, low branch.')


# ---- raiders and riders
def _raiders(lay, kind_):
    return [rd for rd in lay.w.powers.get('raiders', ()) if rd['kind'] == kind_]


def _p_near_raiders(kind_, k, pred, name, n=1, lo=3, hi=14):
    def fn(lay):
        for rd in _raiders(lay, kind_)[:n]:
            spot = lay.around(rd['x'], rd['y'], lo, hi, 4, lambda x, y: pred(lay, x, y))
            if spot:
                lay.add(k, spot, name(rd), raiders=rd['name'])
    return fn


def _coast(l, x, y):
    return l.near_tile(x, y, (D.WATER,)) and not l.river_near(x, y, 2)


PLACE['boatsheds'] = _p_near_raiders('sea', 'boatsheds', _coast, lambda rd: f'The Boat-Sheds of {rd["land"]}')
PLACE['shipset'] = _p_near_raiders('sea', 'shipset', _coast, lambda rd: f'The Ship of Jarl {random.choice(["Hrolf", "Ketil", "Ulfar", "Sigrun", "Bjarni"])}', 1, 6, 20)
PLACE['dwell'] = _p_near_raiders('desert', 'dwell', lambda l, x, y: l.m.tile(x, y) == D.SAND,
                                 lambda rd: f'The Well of the {rd["people"] if isinstance(rd["people"], str) else "Riders"}', 2, 6, 24)
PLACE['pcairn'] = _p_near_raiders('pass', 'pcairn', lambda l, x, y: l.near_tile(x, y, (D.MOUNTAIN,)),
                                  lambda rd: f'The Cairn of {rd["land"]} Pass', 2, 3, 14)
PLACE['falselight'] = _p_near_raiders('wreckers', 'falselight', _coast, lambda rd: 'The Wreckers\' Post', 2, 3, 16)
PLACE['ladders'] = _p_near_raiders('canyon', 'ladders', lambda l, x, y: l.near_tile(x, y, (D.MOUNTAIN, D.HILLS)),
                                   lambda rd: f'The Ladders of {rd["land"]}', 1, 2, 5)
PLACE['stonerows'] = _p_near_raiders('mist', 'stonerows', lambda l, x, y: l.bio(x, y) in ('moor', 'marsh', 'shrubland_cold')
                                     or l.m.tile(x, y) == D.SWAMP, lambda rd: 'The Stone Rows', 2, 4, 20)
PLACE['starcairn'] = _p_near_raiders('island', 'starcairn', lambda l, x, y: _coast(l, x, y),
                                     lambda rd: 'The Star Cairns', 1, 2, 16)


def _m_boatsheds(game, site):
    m = land(game, site, 56, 30)
    sea_side(m, 18)
    cy = m.h // 2
    for k in range(3):
        y = cy - 8 + k * 6
        for x in range(m.w - 30, m.w - 18):
            m.set(x, y, WALL)
            m.set(x, y + 3, WALL)
        put(m, m.w - 31, y + 1, 'shed')
    way(m, (0, cy), (m.w - 32, cy))
    if winter(game):
        npc(game, m, 'A shed-warden of the Fjordmen', '#a8c0e0', m.w - 33, cy + 2)
    return finish(m, (0, cy))


def _a_boatsheds(game, site, key, x, y):
    if winter(game):
        game.msg('Under the long roof lies a dragon-ship, tarred and propped, dry for the winter. They sail in spring.')
    else:
        game.msg('The shed is empty but for props and shavings. The ships are out, on the summer raids.', 'bad')
    return 0


def _t_boatsheds(game, site, o):
    game.say(o, random.choice(['Touch the ships and I touch you, with this.', 'When the ice breaks, we sail. Pray it is '
                               'not for your coast.', 'The jarl sleeps all winter. So do I.']))


BUILD['boatsheds'], ACT['boatsheds'], TALK['boatsheds'] = _m_boatsheds, _a_boatsheds, _t_boatsheds
LINES['boatsheds'] = 'Long low sheds on the shore, roofed with turf, open to the sea.'


def _m_shipset(game, site):
    m = land(game, site, 52, 28)
    sea_side(m, 10)
    cx, cy = m.w // 2 - 4, m.h // 2
    for a in range(20):
        t = a / 19 * 2 * math.pi
        x, y = cx + int(11 * math.cos(t)), cy + int(3.2 * math.sin(t) * (1 if abs(math.cos(t)) < .9 else .3))
        put(m, x, y, 'shipstone')
    way(m, (0, cy), (cx - 12, cy))
    return finish(m, (0, cy))


def _a_shipset(game, site, key, x, y):
    if done(game, f'robbed:{site.id}'):
        game.msg('The stones stand where they stood. The earth in the middle is turned. You did that.')
        return 0
    ask(game, site, site.name, 'Stones set in the shape of a ship, high in the middle, low at the ends, pointing at the '
        'sea. A jarl lies under them with his treasure, the Fjordmen say, and woe to who digs.',
        [('Leave him in peace', 'bye'), ('Dig in the middle of the ship', 'dig')])
    return 0


def _c_shipset(game, site, choice, ctx):
    if choice == 'dig' and once(game, f'robbed:{site.id}'):
        game.end_turn(60)
        give(game, curio(game, 'armring'))
        give(game, curio(game, 'oldcoin'))
        buff(game, 'dmg', -15, 1500, 'The Jarl\'s Curse', 'Under a stone you find bones, an arm-ring of twisted gold and an '
             'old coin. The wind gets up from the sea, cold, and does not stop. (The Jarl\'s Curse: -15% damage)')
        rep(game, 'horde', -2, quiet=True)
        chron(game, site, f'{site.name}: you dug up the jarl\'s grave. His people will hear of it.')
        fight(game, ['sea_raider', 'sea_raider', 'berserker'] if 'berserker' in D.MONSTERS else ['sea_raider'] * 3,
              line='Men come up from the shore with axes. "Grave robber!"')


ACT['shipset'], CHOOSE['shipset'], BUILD['shipset'] = _a_shipset, _c_shipset, _m_shipset
LINES['shipset'] = 'A ring of standing stones on the cape, in the shape of a ship sailing for the sea.'


def _a_dwell(game, site, key, x, y):
    if done(game, f'well:{site.id}:{game.day}'):
        game.msg('You drank here today.')
        return 0
    ask(game, site, 'The well', 'Signs are cut into the stone of the well: a horse, a crescent, a hand. The riders own '
        'this water. A little hollow in the rim holds a few copper coins: the toll.',
        [('Leave a coin and drink (5c)', 'toll'), ('Just drink', 'drink'), ('Leave', 'bye')])
    return 0


def _c_dwell(game, site, choice, ctx):
    p = game.player
    if choice not in ('toll', 'drink'):
        return
    if choice == 'toll' and not pay(game, 5):
        return
    once(game, f'well:{site.id}:{game.day}')
    p.stamina = game.stats()['max_stamina']
    heal(game, .15, poison=False)
    game.msg('Cool water out of the dark. You drink until your belly is tight.', 'good')
    if choice == 'drink' and random.random() < .6:
        fight(game, ['dune_rider', 'dune_rider'], line='Riders come over the dune at a gallop: nobody drinks from their '
              'well without paying.')


BUILD['dwell'], ACT['dwell'], CHOOSE['dwell'] = _m_simple([(0, 0, 'dwell')], size=(46, 26), clearing=None), _a_dwell, _c_dwell
LINES['dwell'] = 'A well in the sand, with a stone rim marked by the riders, and a trough for horses.'


def _a_pcairn(game, site, key, x, y):
    if once(game, f'stone:{site.id}'):
        buff(game, 'swift', 1, 900, 'The pass clans\' good will', 'You add a stone to the cairn, as every traveller does. '
             'A clansman watching from the rocks lifts a hand: you know the custom. The paths seem shorter today.')
        rep(game, 'horde', 1, quiet=True)
        return 1
    game.msg('Your stone is somewhere in the cairn, among the thousands.')
    return 0


BUILD['pcairn'], ACT['pcairn'] = _m_simple([(0, 0, 'pcairn')], size=(46, 26)), _a_pcairn
LINES['pcairn'] = 'A great cairn where the path tops the pass. Every traveller has added a stone.'


def _m_falselight(game, site):
    m = land(game, site, 50, 28)
    sea_side(m, 14)
    cx, cy = m.w - 18, m.h // 2
    for y in range(m.h):
        m.set(m.w - 15, y, D.CLIFF)
    put(m, cx, cy, 'post')
    way(m, (0, cy), (cx - 1, cy))
    return finish(m, (0, cy))


def _a_falselight(game, site, key, x, y):
    from . import weather as WX
    storm = WX.current(game) in ('storm', 'rain', 'snowstorm', 'blizzard')
    if night(game) and storm:
        if once(game, f'doused:{site.id}', 20):
            give(game, curio(game, 'oldcoin'))
            game.player.gold += 300
            marks(game)['wreckers_grudge'] = game.day
            chron(game, site, f'{site.name}: you put out the wreckers\' false light on a storm night, and a ship came home.')
            game.msg('A lantern hangs on the post, swinging, like the harbour light it pretends to be. You smash it. Out on '
                     'the black water a ship goes about, safe. The wreckers will remember your face.', 'good')
            fight(game, ['wrecker', 'wrecker'], line='Two men come running along the cliff with clubs.')
            return 2
    game.msg('A post with an iron hook, black with soot. On storm nights the wreckers hang a light here, to lure ships '
             'onto the rocks.')
    return 0


BUILD['falselight'], ACT['falselight'] = _m_falselight, _a_falselight
LINES['falselight'] = 'A lonely post on the cliff top, an iron hook on it, and the rocks below.'


def _m_ladders(game, site):
    m = land(game, site, 50, 34)
    for y in range(0, 14):
        for x in range(m.w):
            m.set(x, y, D.CLIFF if y > 2 else D.BAREROCK)
    cx = m.w // 2
    for y in range(3, 14):
        put(m, cx, y, 'ladder') if y == 13 else m.set(cx, y, D.CLIFF)
    way(m, (0, m.h - 6), (cx, 14))
    return finish(m, (0, m.h - 6))


def _a_ladders(game, site, key, x, y):
    rd = next((r for r in game.world.powers.get('raiders', ()) if r['name'] == getattr(site, 'raiders', None)), None)
    from .war import is_hostile
    if rd is None:
        return 0
    if game.player.rep.get('horde', 0) <= -40 or (rd.get('faction') and is_hostile(game, rd['faction'])):
        game.msg('High above, faces look over the edge, and the ladders are pulled up, rung by rung. You are not welcome.',
                 'bad')
        return 0
    st = game.world.sites[rd['site']]
    to_world(game, st.x, st.y, 12, 'You climb the ladders, three of them, lashed one above the other, to the cliff '
             'village of the canyon riders.')
    return 0


BUILD['ladders'], ACT['ladders'] = _m_ladders, _a_ladders
LINES['ladders'] = 'A sheer cliff, and ladders of poles and rope going up it, out of sight.'


def _rows_pair(game, site):
    rows = [q for q in game.world.sites if q.kind == 'stonerows' and q is not site]
    return min(rows, key=lambda q: cheb(q.x, q.y, site.x, site.y)) if rows else None


def _m_stonerows(game, site):
    m = land(game, site, 60, 30)
    for k in range(3):
        y = m.h // 2 - 4 + k * 4
        for x in range(6, m.w - 6, 3):
            put(m, x, y, 'rowstone')
    return finish(m, (0, m.h // 2 - 2))


def _a_stonerows(game, site, key, x, y):
    o = _rows_pair(game, site)
    if o is None or cheb(o.x, o.y, site.x, site.y) > 40:
        game.msg('Rows of grey stones run off into the heath and the mist. Where they lead, nobody living knows.')
        return 0
    ask(game, site, site.name, 'Three rows of grey stones run off into the mist, straight as a rule. The mist folk walk '
        'them in any weather: where the rows go, the bog is firm.',
        [(f'Follow the rows to their far end ({cheb(o.x, o.y, site.x, site.y)} leagues)', 'follow'), ('Leave', 'bye')],
        to=o.id)
    return 0


def _c_stonerows(game, site, choice, ctx):
    if choice == 'follow':
        o = game.world.sites[ctx['to']]
        to_world(game, o.x, o.y, 6 * cheb(o.x, o.y, site.x, site.y) // 2,
                 'You walk from stone to stone through the mist, and the bog never takes your foot.')


BUILD['stonerows'], ACT['stonerows'], CHOOSE['stonerows'] = _m_stonerows, _a_stonerows, _c_stonerows
LINES['stonerows'] = 'Long rows of standing stones go off across the heath, into the mist.'


def _a_starcairn(game, site, key, x, y):
    if once(game, 'starpath'):
        chron(game, site, f'{site.name}: the island voyagers\' cairns, laid out as the stars they steer by.')
        game.msg('The cairns are laid out like stars, and lines of white pebbles join them: a chart of the night sky over '
                 'the atolls. You learn its shape. At sea, you will steer by it.', 'good')
        return 3
    game.msg('The star cairns. You know their shape now.')
    return 0


BUILD['starcairn'], ACT['starcairn'] = _m_simple([(-4, -2, 'starcairn'), (3, -3, 'starcairn'), (5, 2, 'starcairn'),
                                                 (-2, 3, 'starcairn'), (0, 0, 'starcairn')], size=(44, 26)), _a_starcairn
LINES['starcairn'] = 'Little cairns of white coral on a bare skerry, laid out in a pattern.'


# ---- dwarves: an air shaft, a dwarf road, a grudge stone, a sealed door
def _holds(lay):
    return [s for s in lay.w.settlements if s.kind == 'deephold']


def _p_airshaft(lay):
    for h in _holds(lay)[:scaled(2)]:
        spot = lay.around(h.x, h.y, 2, 6, 3, lambda x, y: lay.near_tile(x, y, (D.MOUNTAIN,)))
        if spot:
            lay.add('airshaft', spot, f'An Air Shaft of {h.name}', hold=h.id)


def _a_airshaft(game, site, key, x, y):
    h = game.world.settlements[site.hold]
    ask(game, site, 'The grate', f'A grate of black iron over a hole in the rock. Warm air comes up it, and far below, the '
        f'ring of hammers: {h.name} at work. The bars are old; one is loose. A rope would reach.',
        [('Climb down into the hold', 'down'), ('Leave it', 'bye')])
    return 0


def _c_airshaft(game, site, choice, ctx):
    from . import crime as CR
    if choice != 'down':
        return
    h = game.world.settlements[site.hold]
    if game.player.rep.get('clan', 0) < 0 or h.rep < 0:
        CR.commit(game, 10, f'creeping into {h.name} by an air shaft', witnessed=.5, near=(h.x, h.y))
    game.leave_to_over()
    game.player.x, game.player.y = h.x, h.y
    game.end_turn(20)
    game.enter_town(h.id)
    game.msg('You climb down the shaft, through warm dark, and drop into a side hall of the hold.', 'info')


PLACE['airshaft'], BUILD['airshaft'], ACT['airshaft'], CHOOSE['airshaft'] = \
    _p_airshaft, _m_simple([(0, 0, 'grate')], size=(44, 26)), _a_airshaft, _c_airshaft
LINES['airshaft'] = 'Warm air comes out of the mountainside, and the faint ring of hammers.'


def _p_dwarfroad(lay):
    m = lay.m
    made = 0
    for h in _holds(lay):
        if made >= scaled(1) + 1:
            break
        a = lay.around(h.x, h.y, 3, 10, 4, lambda x, y: lay.near_tile(x, y, (D.MOUNTAIN,)))
        if not a:
            continue
        b = None
        for _ in range(400):
            x, y = a[0] + random.randint(-18, 18), a[1] + random.randint(-18, 18)
            if m.inb(x, y) and 8 <= cheb(x, y, *a) <= 18 and lay.free(x, y, 3) and lay.near_tile(x, y, (D.MOUNTAIN,)):
                mid = ((x + a[0]) // 2, (y + a[1]) // 2)
                if m.tile(*mid) == D.MOUNTAIN:
                    b = (x, y)
                    break
        if not b:
            continue
        sa = lay.add('dwarfroad', a, f'The {h.name} Road, West Gate' if a[0] < b[0] else f'The {h.name} Road, East Gate', hold=h.id)
        sb = lay.add('dwarfroad', b, f'The {h.name} Road, East Gate' if a[0] < b[0] else f'The {h.name} Road, West Gate', hold=h.id)
        sa.other, sb.other = sb.id, sa.id
        made += 1


def _m_dwarfroad(game, site):
    m = land(game, site, 50, 28)
    for y in range(m.h):
        for x in range(m.w - 16, m.w):
            m.set(x, y, D.MOUNTAIN if x > m.w - 14 else D.CLIFF)
    cy = m.h // 2
    put(m, m.w - 16, cy, 'dgate')
    way(m, (0, cy), (m.w - 17, cy))
    npc(game, m, 'A dwarf gatewarden', '#d8b878', m.w - 18, cy + 1, race='dwarf')
    return finish(m, (0, cy))


def _a_dwarfroad(game, site, key, x, y):
    o = game.world.sites[site.other]
    if game.player.rep.get('clan', 0) < 0:
        game.msg('"The road is for friends of the hold. Take the pass, like the goats." The gate stays shut.', 'bad')
        return 0
    to_world(game, o.x, o.y, 30, 'The great doors open. You walk an hour through the mountain on a road of cut stone, '
             'lit by lamps that never go out, and come out on the other side.')
    return 0


PLACE['dwarfroad'], BUILD['dwarfroad'], ACT['dwarfroad'] = _p_dwarfroad, _m_dwarfroad, _a_dwarfroad
TALK['dwarfroad'] = lambda game, site, o: game.say(o, 'Through the mountain in an hour, for friends of the hold. Over '
                                                   'it in three days, for the rest.')
LINES['dwarfroad'] = 'Great doors in the mountainside, carved with runes, and a road of cut stone going in.'


def _p_grudgestone(lay):
    for h in _holds(lay):
        book = lay.w.powers['grudges'].get(h.id) or []
        if not book:
            continue
        spot = lay.around(h.x, h.y, 6, 16, 4)
        if spot:
            lay.add('grudgestone', spot, f'A Grudge Stone of {h.name}', hold=h.id, grudge=book[0]['id'])


def _a_grudgestone(game, site, key, x, y):
    from .money import fmt
    h = game.world.settlements[site.hold]
    g = next((g for g in game.world.powers['grudges'].get(site.hold, ()) if g['id'] == site.grudge), None)
    if not g:
        return 0
    if g['settled']:
        say(game, site, f'A grudge stone of {h.name}: "{g["what"][0].upper() + g["what"][1:]}." A deep line is cut '
            'through the words. The grudge is settled.')
        return 0
    price = 2000 * g['weight']
    ask(game, site, 'A grudge stone', f'A square stone with runes cut deep: a line from the Grudge Book of {h.name}. '
        f'"{g["what"][0].upper() + g["what"][1:]}." It stands where it happened. The dwarves do not forget.',
        [(f'Pay the blood-price at the stone and strike it out ({fmt(price)})', 'settle'), ('Leave', 'bye')], price=price)
    return 0


def _c_grudgestone(game, site, choice, ctx):
    from . import powers as PW
    if choice == 'settle' and pay(game, ctx['price']):
        PW.settle(game, site.hold, site.grudge, 'paid for by a traveller')
        rep(game, 'clan', 6)
        chron(game, site, f'{site.name}: you paid the blood-price, and a line was cut through the grudge.')
        game.msg('A dwarf comes the next day, takes the coin, and with a chisel cuts a line through the grudge. He '
                 'nods to you, once. That is a great deal, from a dwarf.', 'good')


PLACE['grudgestone'], BUILD['grudgestone'], ACT['grudgestone'], CHOOSE['grudgestone'] = \
    _p_grudgestone, _m_simple([(0, 0, 'grudge')], size=(44, 26)), _a_grudgestone, _c_grudgestone
LINES['grudgestone'] = 'A square stone by the way, cut with dwarf runes, old but sharp.'


def _p_sealed(lay):
    m = lay.m
    for _ in range(scaled(1)):
        spot = lay.search(lambda x, y: lay.near_tile(x, y, (D.MOUNTAIN,)) and lay.road(x, y) >= 6, 14)
        if spot:
            lay.add('sealed', spot, 'The Sealed Door')


def _m_sealed(game, site):
    m = land(game, site, 50, 30)
    for y in range(m.h):
        for x in range(m.w - 20, m.w):
            m.set(x, y, D.ROCK)
    cy = m.h // 2
    for y in range(cy - 4, cy + 5):                   # the vault behind the door
        for x in range(m.w - 14, m.w - 4):
            m.set(x, y, FLOOR)
    for x in range(m.w - 19, m.w - 14):
        m.set(x, cy, FLOOR)
    put(m, m.w - 20, cy, 'sdoor')
    m.set(m.w - 6, cy, D.CHEST)
    m.vault = (m.w - 14, cy)
    way(m, (0, cy), (m.w - 21, cy))
    return finish(m, (0, cy))


def _a_sealed(game, site, key, x, y):
    if done(game, f'opened:{site.id}'):
        take(game.map, x, y, FLOOR)
        return 0
    ask(game, site, 'The sealed door', 'A door of black stone set flush in the rock, bound with iron. Dwarf runes run '
        'round it, cut deep, and again and again the same three words: NOT TO BE OPENED.',
        [('Break the seals and open it', 'open'), ('Leave it shut', 'bye')], x=x, y=y)
    return 0


def _c_sealed(game, site, choice, ctx):
    if choice != 'open' or not once(game, f'opened:{site.id}'):
        return
    take(game.map, ctx['x'], ctx['y'], FLOOR)
    rep(game, 'clan', -8)
    chron(game, site, f'{site.name}: you broke the seals the dwarves set, and what they shut in came out.')
    m = game.map
    fight(game, ['wight' if random.random() < .5 else 'troll'], near=m.vault, lvl=m.level + 3,
          line='The door grinds open. Cold air, and the smell of a grave. Something inside stands up.')


PLACE['sealed'], BUILD['sealed'], ACT['sealed'], CHOOSE['sealed'] = _p_sealed, _m_sealed, _a_sealed, _c_sealed
LINES['sealed'] = 'A door of black stone in the cliff, sealed with iron and runes.'


# ---- elves: a watch tree, the burned grove, a grave tree
def _elves(lay):
    return [q for q in lay.w.sites if q.kind == 'glade'] + [s for s in lay.w.settlements if getattr(s, 'elder', False)]


def _p_elf(k, lo, hi, name, n=1, wood=True):
    def fn(lay):
        for e in _elves(lay)[:scaled(n) + 1]:
            spot = lay.around(e.x, e.y, lo, hi, 4, lambda x, y: (lay.m.tile(x, y) == D.FOREST) == wood or
                              (not wood and lay.near_tile(x, y, (D.FOREST,))))
            if spot:
                lay.add(k, spot, name(), toward=(e.x, e.y))
    return fn


PLACE['watchtree'] = _p_elf('watchtree', 5, 12, lambda: f'The {random.choice(["Hawk", "Owl", "Wind", "Grey"])} Watch Tree', 1, False)
PLACE['burntgrove'] = _p_elf('burntgrove', 6, 18, lambda: 'The Burned Grove', 1)
PLACE['gravetree'] = _p_elf('gravetree', 4, 14, lambda: f'The Grave of {random.choice(["Aelindra", "Thalion", "Ilsevel", "Caerwyn", "Elenath"])}', 1)


def _m_watchtree(game, site):
    m = plain(game, site, [(0, 0, 'platform')], size=(50, 28))
    if game.player.rep.get('circle', 0) >= 0:
        npc(game, m, 'An elf on the platform', '#b8f0c8', m.centre[0] + 1, m.centre[1] - 1, race='elf')
    return finish(m, (0, m.h // 2))


def _a_watchtree(game, site, key, x, y):
    from .nature import lookout
    if game.player.rep.get('circle', 0) < 0:
        game.msg('An arrow thuds into the trunk beside your hand. You are not welcome up there.', 'bad')
        return 0
    game.map.lookout = 12
    return lookout(game, site)


def _t_watchtree(game, site, o):
    if once(game, f'news:{site.id}', 3):
        from .folk import discover
        left = sorted((q for q in game.world.sites if q.kind == 'glade' and not getattr(q, 'found', True)),
                      key=lambda q: cheb(q.x, q.y, site.x, site.y))
        if left and game.player.rep.get('circle', 0) >= 20:
            discover(game, left[0], 'The elf points the way, once, between the trees.')
            return
    game.say(o, random.choice(['We saw you an hour ago, by the stream.', 'Woodcutters on the east side. Again.',
                               'The wood is quiet today. That is not always good.']))


BUILD['watchtree'], ACT['watchtree'], TALK['watchtree'] = _m_watchtree, _a_watchtree, _t_watchtree
LINES['watchtree'] = 'A great tree at the edge of the wood, with a platform high up in its crown.'


def _m_burntgrove(game, site):
    m = land(game, site, 54, 30)
    cx, cy = m.w // 2, m.h // 2
    for y in range(m.h):
        for x in range(m.w):
            if ((x - cx) / 16) ** 2 + ((y - cy) / 9) ** 2 < 1:
                m.set(x, y, D.ASH if random.random() < .5 else GRASS)
                if random.random() < .12:
                    put(m, x, y, 'blacktree')
    way(m, (0, cy), (cx, cy))
    return finish(m, (0, cy))


def _a_burntgrove(game, site, key, x, y):
    chron(game, site, f'{site.name}: black trunks the elves leave standing, where the woodcutters burned the wood.')
    ask(game, site, 'A burned trunk', 'A trunk black as coal, dead for years, still standing. The elves leave them all, so '
        'that nobody forgets. Ribbons of green are tied round some.',
        [('Tie a ribbon of grass round it', 'ribbon'), ('Cut it down for firewood', 'cut'), ('Leave', 'bye')])
    return 0


def _c_burntgrove(game, site, choice, ctx):
    if choice == 'ribbon' and once(game, f'ribbon:{site.id}'):
        rep(game, 'circle', 2)
        game.msg('You knot a long grass round the black trunk. Somewhere a bird starts to sing.', 'good')
    elif choice == 'cut':
        rep(game, 'circle', -10)
        game.msg('The axe bites into the dead wood. The wood around goes quiet, and stays quiet. The elves will know.', 'bad')


BUILD['burntgrove'], ACT['burntgrove'], CHOOSE['burntgrove'] = _m_burntgrove, _a_burntgrove, _c_burntgrove
LINES['burntgrove'] = 'Black trunks stand in the green, dead and left standing. Nobody has cleared them away.'


def _a_gravetree(game, site, key, x, y):
    spring = season(game) == 'spring'
    chron(game, site, f'{site.name}: a tree grown over a fallen elf, ringed with stones.')
    say(game, site, 'A slender tree inside a narrow ring of white stones. It grew over a fallen elf, and the elves say she '
        'is in it still.' + (' It is in flower, the only white among the green.' if spring else ''))
    if spring and once(game, f'bloom:{site.id}', 300):
        heal(game, .5)
        game.msg('The scent of the white flowers eases you.', 'good')
    return 0


BUILD['gravetree'], ACT['gravetree'] = _m_simple([(0, 0, 'gtree')], size=(44, 26)), _a_gravetree
LINES['gravetree'] = 'A slender tree in a ring of white stones, in a quiet glade.'


# ---- halflings: a hedge gate, a party field, pipe-weed fields
def _halfland(lay):
    return set(getattr(lay.w, 'halfling_land', ()) or ())


def _p_hedgegate(lay):
    land_ = _halfland(lay)
    if not land_:
        return
    m, w = lay.m, lay.w
    made = 0
    for t in range(6000):
        if made >= 2:
            break
        x, y = random.randint(4, m.w - 5), random.randint(4, m.h - 5)
        r = w.region_of[y * m.w + x]
        if r in land_ and any(w.region_of[(y + b) * m.w + x + a] not in land_ for a in (-2, 0, 2) for b in (-2, 0, 2)) \
                and lay.free(x, y, 4 if t < 3000 else 2) and (t >= 3000 or lay.road(x, y) <= 4):
            lay.add('hedgegate', (x, y), f'The {random.choice(["Bramble", "Holly", "Old", "Green"])} Hedge Gate')
            made += 1


def _p_halfin(k, n, pred, name):
    def fn(lay):
        land_ = _halfland(lay)
        if not land_:
            return
        for _ in range(n):
            spot = lay.search(lambda x, y: lay.w.region_of[y * lay.m.w + x] in land_ and pred(lay, x, y), 6)
            if spot:
                lay.add(k, spot, name())
    return fn


PLACE['hedgegate'] = _p_hedgegate
PLACE['partyfield'] = _p_halfin('partyfield', 2, lambda l, x, y: l.m.tile(x, y) == D.GRASS and l.road(x, y) <= 4,
                                lambda: f'The {random.choice(["Long", "Lantern", "Oak", "Merry"])} Field')
PLACE['pipeweed'] = _p_halfin('pipeweed', 2, lambda l, x, y: l.m.tile(x, y) in (D.HILLS, D.GRASS),
                              lambda: f'{random.choice(["Longbottom", "Sunbank", "Old Toby\'s", "Southfarthing"])} Leaf Fields')


def _m_hedgegate(game, site):
    m = land(game, site, 50, 28)
    cx, cy = m.w // 2, m.h // 2
    for y in range(m.h):
        m.set(cx, y, D.HEDGE)
        m.set(cx + 1, y, D.HEDGE)
    put(m, cx, cy, 'hgate')
    m.set(cx + 1, cy, GRASS)
    way(m, (0, cy), (cx - 1, cy))
    way(m, (cx + 2, cy), (m.w - 1, cy))
    npc(game, m, 'The hedge warden', '#c0e090', cx - 2, cy + 1, race='halfling')
    return finish(m, (0, cy))


def _a_hedgegate(game, site, key, x, y):
    game.msg('A round gate of woven willow in the great hedge. Beyond it, the halfling country: smoke from round '
             'chimneys, and every field tidy.')
    return 0


def _t_hedgegate(game, site, o):
    ask(game, site, o.name, '"Good morning! Or is it afternoon? Tea? There is always tea at the gate. Mind the '
        'gardens on the other side, and close gates behind you."', [('A cup of tea', 'tea'), ('Goodbye', 'bye')])


def _c_hedgegate(game, site, choice, ctx):
    if choice == 'tea':
        if once(game, f'tea:{site.id}', 1):
            heal(game, .1, poison=False)
            game.msg('Tea, with milk and honey, and a seed cake you did not ask for. The warden tells you everything that '
                     'happened in the halfling country for a month.', 'good')
            gossip(game)
        else:
            game.msg('"Another cup? You will float away, dear."', 'talk')


BUILD['hedgegate'], ACT['hedgegate'], TALK['hedgegate'], CHOOSE['hedgegate'] = _m_hedgegate, _a_hedgegate, _t_hedgegate, _c_hedgegate
LINES['hedgegate'] = 'A great hedge, as high as a house, and a gate in it with a bench and a teapot.'


def _halfling_feast(game, site):
    from . import feasts as FE
    s = min((q for q in game.world.settlements if q.race == 'halfling'), key=lambda q: cheb(q.x, q.y, site.x, site.y),
            default=None)
    return bool(s and FE.today(game, s))


def _m_partyfield(game, site):
    m = plain(game, site, [(-3, 0, 'longtable'), (0, 0, 'longtable'), (3, 0, 'longtable')], size=(52, 28), clearing=(14, 7))
    cx, cy = m.centre
    for a in range(12):
        x, y = cx + int(12 * math.cos(a * .52)), cy + int(6 * math.sin(a * .52))
        if m.tile(x, y) == GRASS:
            m.set(x, y, TREE)
            m.glows.append((x, y, (255, 140, 60), 4))
    if _halfling_feast(game, site):
        for k in range(8):
            npc(game, m, 'A halfling at the party', '#e0c890', cx + random.randint(-9, 9), cy + random.randint(-4, 4),
                stay=False, race='halfling')
    return finish(m, (0, cy))


def _a_partyfield(game, site, key, x, y):
    if _halfling_feast(game, site) and once(game, f'party:{site.id}', 30):
        give(game, food(game, 'cheese'))
        buff(game, 'regen', 1, 600, 'Full of party food', 'They sit you down, fill your plate, fill it again, and then '
             'there are fireworks. You leave happy and somewhat round.')
        return 6
    game.msg('A long table under the trees, lanterns hung ready. On a feast day all the halflings of the country '
             'are here.')
    return 0


BUILD['partyfield'], ACT['partyfield'] = _m_partyfield, _a_partyfield
ON_ENTER['partyfield'] = lambda game, site, m: ('Lanterns in the trees, music, and halflings everywhere: a party!'
                                                if _halfling_feast(game, site) else
                                                'A quiet meadow, a long table under the trees, lanterns hanging ready.')


def _m_pipeweed(game, site):
    m = land(game, site, 54, 30)
    cx, cy = m.w // 2, m.h // 2
    for y in range(cy - 7, cy + 8):
        for x in range(cx - 18, cx + 10):
            if m.inb(x, y) and y % 2 == 0:
                m.set(x, y, FIELD)
    put(m, cx - 6, cy + 1, 'weed')
    hut(m, cx + 12, cy - 2, 6, 5, 'w')
    way(m, (0, cy + 1), (cx - 7, cy + 1))
    npc(game, m, 'A leaf grower', '#c0d890', cx + 10, cy + 1, race='halfling')
    return finish(m, (0, cy + 1))


def _t_pipeweed(game, site, o):
    from .money import fmt
    ask(game, site, o.name, f'"Best leaf in the world. Ask anyone. A pouch is {fmt(LEAF_PRICE)}, and you will not find it '
        'anywhere else, not in the great city, not over the sea."', [(f'Buy a pouch ({fmt(LEAF_PRICE)})', 'buy'),
                                                                     ('Goodbye', 'bye')])


LEAF_PRICE = 40


def _c_pipeweed(game, site, choice, ctx):
    if choice == 'buy' and pay(game, LEAF_PRICE):
        give(game, curio(game, 'pipeweed'))
        game.msg('A pouch of fragrant leaf. Merchants in the cities pay well for it.', 'good')


BUILD['pipeweed'], TALK['pipeweed'], CHOOSE['pipeweed'] = _m_pipeweed, _t_pipeweed, _c_pipeweed
ACT['pipeweed'] = lambda game, site, key, x, y: game.msg('Broad leaves, sticky and sweet-smelling, in long neat rows.') or 0
LINES['pipeweed'] = 'Rows of broad-leaved plants on a sunny slope, and a drying shed.'


# ---- gnomes: a bee garden, a lookout stump
def _gnomes(lay):
    return [q for q in lay.w.sites if q.kind == 'gnomes']


def _p_gnome(k, lo, hi, name):
    def fn(lay):
        for g in _gnomes(lay)[:scaled(2)]:
            spot = lay.around(g.x, g.y, lo, hi, 2)
            if spot:
                lay.add(k, spot, name(), gnomes=g.id)
    return fn


PLACE['beegarden'] = _p_gnome('beegarden', 3, 8, lambda: f'The {random.choice(["Humming", "Honey", "Clover"])} Garden')
PLACE['stump'] = _p_gnome('stump', 2, 3, lambda: 'A Lookout Stump')


def _a_beegarden(game, site, key, x, y):
    ask(game, site, 'The hives', 'Hives of plaited straw under the roots of the trees, each with a tiny painted door. '
        'The bees are busy. A slate by them says, in very small letters: "Honey for salt. Leave the salt, take a comb."',
        [('Leave a load of salt and take honey', 'trade' if game.player.cargo.get('salt') else None),
         ('Take a comb anyway', 'steal'), ('Leave them be', 'bye')])
    return 0


def _c_beegarden(game, site, choice, ctx):
    p = game.player
    if choice == 'trade':
        p.cargo['salt'] -= 1
        if not p.cargo['salt']:
            del p.cargo['salt']
        for _ in range(3):
            give(game, curio(game, 'honeycomb'))
        game.msg('You leave the salt by the slate and take three combs. Something giggles in the roots.', 'good')
    elif choice == 'steal':
        give(game, curio(game, 'honeycomb'))
        hurt(game, 4 + game.player.lvl, 'bee stings')
        game.msg('The bees come out in a cloud. You run with one comb and a face full of stings.', 'bad')


PLACE['beegarden'], BUILD['beegarden'], ACT['beegarden'], CHOOSE['beegarden'] = \
    PLACE['beegarden'], _m_simple([(-2, 0, 'hive'), (1, -1, 'hive'), (3, 1, 'hive')], size=(44, 26)), _a_beegarden, _c_beegarden
LINES['beegarden'] = 'A clearing loud with bees, and little hives under the roots.'


def _a_stump(game, site, key, x, y):
    from .folk import discover
    g = game.world.sites[site.gnomes]
    if not getattr(g, 'found', True):
        discover(game, g, 'The little bell rings, and further on, between the roots, tiny shutters bang shut.')
    else:
        game.msg('A hollow stump with a little bell hung inside. It rings as you come near; further on, shutters close.')
    return 0


BUILD['stump'], ACT['stump'] = _m_simple([(0, 0, 'bell')], size=(44, 26)), _a_stump
LINES['stump'] = 'A hollow stump at the edge of the clearing. Something in it rings.'


# ---- orcs and the tribes
def _camps(lay, kinds):
    return [q for q in lay.w.sites if q.kind in kinds]


def _p_tribe(k, kinds, lo, hi, name, n=1, pred=None):
    def fn(lay):
        for c in _camps(lay, kinds)[:scaled(n) + 1]:
            spot = lay.around(c.x, c.y, lo, hi, 3, (lambda x, y: pred(lay, x, y)) if pred else None)
            if spot:
                lay.add(k, spot, name(), camp=c.id)
    return fn


PLACE['duelring'] = _p_tribe('duelring', ('warcamp',), 4, 12, lambda: 'The Ring of Challenge')
PLACE['wcairn'] = _p_tribe('wcairn', ('warcamp',), 8, 20, lambda: f'The Cairn of {random.choice(["Grukk", "Mazgul", "Ushbag", "Thrakka"])} the Red')
PLACE['midden'] = _p_tribe('midden', ('ravine',), 2, 6, lambda: 'The Goblin Midden', 2)
PLACE['ropebridge'] = _p_tribe('ropebridge', ('ravine',), 3, 10, lambda: 'The Rope Bridge', 1)
PLACE['lure'] = _p_tribe('lure', ('kobolds',), 3, 7, lambda: 'The Kobold Lure', 1)
PLACE['boneyard'] = _p_tribe('boneyard', ('gnolls',), 3, 8, lambda: 'The Bone Yard', 1)
PLACE['eggmounds'] = _p_tribe('eggmounds', ('stilts',), 2, 6, lambda: 'The Egg Mounds', 1)


def _m_duelring(game, site):
    m = land(game, site, 50, 28)
    cx, cy = m.w // 2, m.h // 2
    clear(m, cx, cy, 9, 6)
    for a in range(16):
        x, y = cx + round(7 * math.cos(a * .39)), cy + round(4 * math.sin(a * .39))
        put(m, x, y, 'ringstone') if a else None
    way(m, (0, cy), (cx - 8, cy))
    npc(game, m, 'An orc champion', '#e08060', cx + 2, cy, race='orc')
    return finish(m, (0, cy))


def _t_duelring(game, site, o):
    ask(game, site, o.name, '"You. Small. You come to the ring? Step in, and we see who is the stronger. Win, and the '
        'tribes speak your name. Lose, and they laugh at it."', [('Step into the ring', 'duel'), ('Not today', 'bye')],
        npc=o.id)


def _c_duelring(game, site, choice, ctx):
    from .entities import make_monster
    if choice != 'duel':
        return
    o = next((x for x in game.map.mons if x.id == ctx.get('npc')), None)
    if not o:
        return
    game.map.mons.remove(o)
    ch = make_monster(game, 'orc_berserker' if 'orc_berserker' in D.MONSTERS else 'orc', o.x, o.y, game.map.level + 2)
    ch.name = 'The orc champion'
    ch.awake = True
    ch.duel = site.id
    game.map.mons.append(ch)
    game.msg('He spits on his hands and comes at you. Orcs gather round the stones, shouting.', 'bad')


def duel_won(game, mon):
    if getattr(mon, 'duel', None) is None:
        return
    site = game.world.sites[mon.duel]
    if once(game, f'duel:{site.id}', 60):
        rep(game, 'horde', 8)
        from .entities import make_gear
        it = make_gear(game, random.choice(['waraxe', 'mace', 'spear']), 'normal', game.map.level + 2)
        it.ided = True
        give(game, it)
        chron(game, site, f'{site.name}: you beat an orc champion in the ring. The tribes speak your name.')
        game.msg('The orcs roar, for you this time. The champion\'s weapon is yours by right.', 'good')


BUILD['duelring'], TALK['duelring'], CHOOSE['duelring'] = _m_duelring, _t_duelring, _c_duelring
LINES['duelring'] = 'A ring of stones on the open steppe, the grass inside it trampled flat.'


def _a_wcairn(game, site, key, x, y):
    if done(game, f'took:{site.id}'):
        game.msg('The cairn, bare now. You took his weapons. The tribes have not forgotten.')
        return 0
    ask(game, site, site.name, 'A heap of stones as high as a man, and on top, rusting, the weapons of a dead warlord: a '
        'great axe, a spear, a shield painted with a red hand. No orc would touch them.',
        [('Take the axe', 'take'), ('Leave them', 'bye')])
    return 0


def _c_wcairn(game, site, choice, ctx):
    if choice == 'take' and once(game, f'took:{site.id}'):
        from .entities import make_gear
        it = make_gear(game, 'greataxe', 'magic', game.map.level + 3)
        it.ided = True
        give(game, it)
        rep(game, 'horde', -20)
        chron(game, site, f'{site.name}: you took a dead warlord\'s axe. The tribes hunt you for it.')
        fight(game, ['orc', 'orc', 'orc_spear' if 'orc_spear' in D.MONSTERS else 'orc'], line='A horn sounds from the hills. '
              'They saw.')


BUILD['wcairn'], ACT['wcairn'], CHOOSE['wcairn'] = _m_simple([(0, 0, 'wcairn')], size=(44, 26)), _a_wcairn, _c_wcairn
LINES['wcairn'] = 'A cairn on a rise, weapons rusting on top of it. Nothing grows close.'


def _a_midden(game, site, key, x, y):
    if not once(game, f'pick:{site.id}', 7):
        game.msg('Rubbish, and more rubbish. You picked through it already this week.')
        return 0
    game.end_turn(20)
    r = random.random()
    if r < .08:
        give(game, curio(game, 'oldcoin'))
        game.msg('Under a broken pot, an old coin. The goblins missed it.', 'good')
    elif r < .4:
        give(game, curio(game, 'junk'))
        game.msg('A bent spoon, a button and a bit of string. Goblin treasure.')
    else:
        game.msg('Bones, rags, broken pots. Nothing.')
    if random.random() < .3:
        fight(game, ['goblin', 'goblin'], line='Two goblins come out of the heap, very angry: that is their rubbish.')
    return 0


BUILD['midden'], ACT['midden'] = _m_simple([(0, 0, 'heap'), (2, 1, 'heap'), (-2, 1, 'heap')], size=(44, 26)), _a_midden
LINES['midden'] = 'It smells before you see it: a midden of everything goblins throw away. Which is not much.'


def _m_ropebridge(game, site):
    m = land(game, site, 50, 30)
    cx = m.w // 2
    for y in range(m.h):
        for x in range(cx - 4, cx + 5):
            m.set(x, y, D.CHASM)
    cy = m.h // 2
    put(m, cx - 5, cy, 'bridge')
    way(m, (0, cy), (cx - 6, cy))
    return finish(m, (0, cy))


def _a_ropebridge(game, site, key, x, y):
    om = game.maps['over']
    far = None
    for d in range(2, 6):
        for dx, dy in ((d, 0), (-d, 0), (0, d), (0, -d)):
            c = (site.x + dx, site.y + dy)
            if om.inb(*c) and D.TILES[om.tile(*c)].walk and om.tile(*c) not in (D.TOWN, D.CITY):
                far = c
                break
        if far:
            break
    if not far:
        return 0
    if random.random() < .15:
        hurt(game, 6 + game.player.lvl * 2, 'a cut rope bridge')
        if game.dead:
            return 0
        to_world(game, *far, 30, 'Half way over, the ropes go slack: goblins cut them. You fall, hit the water, and '
                 'crawl out far downstream.')
        return 0
    to_world(game, *far, 3, 'The bridge sways and creaks, and holds. You are over.')
    return 0


BUILD['ropebridge'], ACT['ropebridge'] = _m_ropebridge, _a_ropebridge
LINES['ropebridge'] = 'A bridge of rope and planks over a deep gorge, swaying in the wind.'


def _a_lure(game, site, key, x, y):
    mk = marks(game)
    if mk.get('kobold_friend'):
        game.msg('The pole is hung with shiny things. Yours is among them, and the kobolds remember.')
        return 0
    shiny = next((i for i in game.player.inv if i.k == 'curio' and i.t in ('trinket', 'oldcoin', 'amber', 'armring')), None)
    ask(game, site, 'The shiny thing', 'Hung on a pole, turning in the wind: a brass button, a spoon, a bit of mirror. The '
        'ground round the pole is too even, and too soft.',
        [('Grab the shiny thing', 'grab'), ('Hang something shiny of your own beside it', 'hang' if shiny else None),
         ('Leave it', 'bye')], item=shiny.id if shiny else None)
    return 0


def _c_lure(game, site, choice, ctx):
    p = game.player
    if choice == 'grab':
        hurt(game, 5 + p.lvl, 'a kobold pit')
        game.msg('The ground gives way under you: a pit, with stakes. The shiny thing was a spoon.', 'bad')
    elif choice == 'hang':
        it = next((i for i in p.inv if i.id == ctx.get('item')), None)
        if it:
            p.inv.remove(it)
        marks(game)['kobold_friend'] = game.day
        game.msg('You hang it on the pole beside the others. From the rocks, small voices chatter, pleased. The kobolds '
                 'will not forget a friend.', 'good')


BUILD['lure'], ACT['lure'], CHOOSE['lure'] = _m_simple([(0, 0, 'shiny')], size=(44, 26)), _a_lure, _c_lure
LINES['lure'] = 'Something glitters on a pole in the middle of nowhere.'


def _m_boneyard(game, site):
    m = plain(game, site, [(0, 0, 'carrion')], size=(50, 28), clearing=(11, 6))
    scatter(m, D.BONES, .08, box=(m.w // 2 - 10, m.h // 2 - 5, m.w // 2 + 10, m.h // 2 + 5))
    if night(game):
        beasts(game, m, ['gnoll_hunter', 'gnoll_hunter', 'hyena'], m.centre, r=5)
    return finish(m, (0, m.h // 2))


BUILD['boneyard'] = _m_boneyard
ACT['boneyard'] = lambda game, site, key, x, y: game.msg('A dead tree hung with skulls and strips of hide. The gnolls eat '
                                                         'here, and come back at dark.') or 0
ON_ENTER['boneyard'] = lambda game, site, m: ('Shapes move among the bones, and something laughs.' if night(game) else
                                              'A clearing white with bones round a dead tree. Nothing moves, for now.')


def _m_eggmounds(game, site):
    m = land(game, site, 50, 28)
    cx, cy = m.w // 2, m.h // 2
    for k in range(5):
        put(m, cx - 8 + k * 4, cy + random.randint(-2, 2), 'eggs')
    way(m, (0, cy), (cx - 10, cy))
    if season(game) in ('spring', 'summer'):
        beasts(game, m, ['lizard_warrior', 'lizard_spear'], (cx, cy), r=4, awake=True)
    return finish(m, (0, cy))


def _a_eggmounds(game, site, key, x, y):
    if season(game) in ('autumn', 'winter'):
        game.msg('A mound of rotting reeds, warm inside. Empty: the young hatched long ago.')
        return 0
    if once(game, f'eggs:{site.id}', 30):
        give(game, curio(game, 'eggshell'))
        rep(game, 'horde', -2, quiet=True)
        game.msg('You dig a leathery egg out of the warm reeds.', 'info')
    return 0


BUILD['eggmounds'], ACT['eggmounds'] = _m_eggmounds, _a_eggmounds
ON_ENTER['eggmounds'] = lambda game, site, m: ('Mounds of reeds steam in the swamp, and lizardfolk stand guard over them.'
                                               if season(game) in ('spring', 'summer') else
                                               'Mounds of rotting reeds in the swamp, cold and unguarded now.')


# ---- for everyone: a shrine of another people, a wayside market
OTHER = [('orc', 'An orc totem: a pole carved with tusked faces, painted red long ago.', 'horde'),
         ('dwarf', 'A dwarf shrine: a square stone with an anvil cut in it, and a niche for a lamp.', 'clan'),
         ('elf', 'An elven moonstone, white and cold, with a crescent cut in it.', 'circle')]


def _p_othershrine(lay):
    m, w = lay.m, lay.w
    for _ in range(scaled(3)):
        spot = lay.search(lambda x, y: w.region_at(x, y).faction == 'crown' and lay.road(x, y) <= 10, 10)
        if spot:
            people, text, f = random.choice(OTHER)
            lay.add('othershrine', spot, {'orc': 'The Old Totem', 'dwarf': 'The Anvil Stone', 'elf': 'The Moon Shrine'}[people],
                    people=people)


def _a_othershrine(game, site, key, x, y):
    people, text, f = next(o for o in OTHER if o[0] == site.people)
    chron(game, site, f'{site.name}: a shrine of the {people}s, in a land where no {people} lives now. Borders were '
          'once elsewhere.')
    say(game, site, text + ' No ' + people + ' has lived in these parts for a hundred years and more. The border was '
        'elsewhere once.')
    if once(game, f'honour:{site.id}', 30):
        rep(game, f, 1, quiet=True)
    return 0


PLACE['othershrine'], BUILD['othershrine'], ACT['othershrine'] = \
    _p_othershrine, _m_simple([(0, 0, 'shrine')], size=(44, 26)), _a_othershrine
LINES['othershrine'] = 'An old shrine stands by itself in the fields, not of the people who live here.'


def market_day(game):
    from . import calendar as CAL
    _y, _mo, d, _wd = CAL._split(game.day)
    return d == 15


def _p_waymarket(lay):
    m = lay.m
    ring = (1, -1, m.w, -m.w, m.w + 1, m.w - 1, -m.w + 1, -m.w - 1)
    cross = [i for i, t in enumerate(m.t) if t == D.ROAD and sum(1 for o in ring if 0 <= i + o < len(m.t)
                                                                  and m.t[i + o] == D.ROAD) >= 3]
    random.shuffle(cross)
    made = 0
    for i in cross:
        x, y = i % m.w, i // m.w
        if made >= scaled(2) or not all(cheb(x, y, s.x, s.y) >= 8 for s in lay.w.settlements):
            continue
        spot = lay.around(x, y, 1, 2, 8)
        if spot:
            lay.add('waymarket', spot, 'The Moot Stones')
            made += 1


def _m_waymarket(game, site):
    m = plain(game, site, [(0, 0, 'mstone')], size=(52, 28), clearing=(12, 6))
    cx, cy = m.centre
    for a in range(10):
        x, y = cx + int(9 * math.cos(a * .63)), cy + int(5 * math.sin(a * .63))
        if m.tile(x, y) == GRASS:
            m.set(x, y, D.STONE)
    if market_day(game):
        for name, fg, race in (('A dwarf trader', '#d8b878', 'dwarf'), ('A halfling trader', '#c0e090', 'halfling'),
                               ('An orc trader', '#c0a070', 'orc'), ('A human trader', '#e0c090', 'human')):
            npc(game, m, name, fg, cx + random.randint(-7, 7), cy + random.randint(-3, 3), race=race)
    return finish(m, (0, cy))


def _t_waymarket(game, site, o):
    ask(game, site, o.name, '"Peace of the market! No blades drawn on moot day. Look, buy, go in peace."',
        [('See the goods', 'shop'), ('Goodbye', 'bye')])


def _c_waymarket(game, site, choice, ctx):
    if choice == 'shop':
        shop(game, site, f'moot{game.day}', 6)


BUILD['waymarket'], TALK['waymarket'], CHOOSE['waymarket'] = _m_waymarket, _t_waymarket, _c_waymarket
PLACE['waymarket'] = _p_waymarket
ACT['waymarket'] = lambda game, site, key, x, y: game.msg('The market stone. Carved on it: "On the fifteenth day of every '
                                                          'month, the peace of the market."') or 0
ON_ENTER['waymarket'] = lambda game, site, m: ('It is market day at the moot stones: a dwarf, a halfling, an orc and a '
                                               'human, trading in peace.' if market_day(game) else
                                               'A ring of stones where the roads meet, empty. A market is held here '
                                               'on the fifteenth of every month.')


# ------------------------------------------------------------------ the days
def daily(game):
    realm_camps(game)
    refugee_camps(game)
    prospectors(game)
    witch_night(game)
    from . import yearplaces as YP
    YP.daily(game)


register()

from . import yearplaces as YP  # noqa: E402  (round 30 sets its kinds down in these tables)
