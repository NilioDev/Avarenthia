"""Realms, lords and wars: people who rule.

One emperor in the great city; under him three to five kings, each with a kingdom of baronies; a baron for every
region of the realm, seated in its castle, its chief town or a manor; under each baron two or three lesser houses,
knightly families with a seat of their own in the land (a fortified farm, a tower house or a walled manor) beside
the village they hold. In the cities rich merchant families buy with coin what the lords take with swords.

Every lord is a named person with an age, a trait or two, an heir and a loyalty to his liege; every house has a
name, arms, colours and a motto. Once a month each court has its small event, heard through the news: a death and
a succession (disputed, when the heir is a child or there is none), a baron who rebels or claims his neighbour's
land, a marriage that binds two houses or an insult that breaks them, a levy, and wars that also end: peace, a
barony changing hands, tribute, a hostage. Hosts march across the world map between the seats.

The player never rules and gets no land: he swears fealty and becomes a knight, and does the small work of the
lords (realmjobs.py). The other powers, each with its own engine, are in powers.py; the seats' own maps in
seats.py; the history of the last two hundred years and the libraries in history.py.

The realms map is a world-map layer (ui.WorldMapScreen, key 4): each realm washes the land in its colour, a bright
border where two realms meet, a faint one between baronies. The regions themselves grow over the land from their
centres (organic, below), so the borders follow rivers and ridges."""
import heapq
import random

from . import data as D
from .worldgen import cheb

# ------------------------------------------------------------------ the people
TRAITS = ['ambitious', 'greedy', 'pious', 'craven', 'honest', 'brave']
TRAIT_WORD = {'ambitious': 'ambitious', 'greedy': 'greedy', 'pious': 'pious', 'craven': 'craven', 'honest': 'honest',
              'brave': 'brave'}
TITLES = {'emperor': ('Emperor', 'Empress'), 'king': ('King', 'Queen'), 'baron': ('Baron', 'Baroness'),
          'lord': ('Lord', 'Lady'), 'heir': ('', ''), 'merchant': ('Master', 'Mistress')}
RANKS = ['emperor', 'king', 'baron', 'lord', 'merchant']


class Lord:
    def __init__(self, lid, first, gender, house, age):
        self.id, self.first, self.gender, self.house, self.age = lid, first, gender, house, age
        self.title = 'lord'
        self.traits = []
        self.heir = None          # the lord who follows him
        self.liege = None
        self.loyalty = 60
        self.alive = True
        self.died = None          # (day, how)
        self.met = False

    @property
    def he(self):
        return 'she' if self.gender == 'female' else 'he'

    @property
    def his(self):
        return 'her' if self.gender == 'female' else 'his'

    @property
    def him(self):
        return 'her' if self.gender == 'female' else 'him'


class House:
    def __init__(self, hid, name, people, rank):
        self.id, self.name, self.people, self.rank = hid, name, people, rank
        self.arms = ('♦', (230, 200, 90), (120, 30, 30))
        self.motto = ''
        self.wealth = 1           # 0 poor, 1 middling, 2 rich
        self.seat = None          # ('site', id) | ('hold', id) | ('s', sid)
        self.head = None
        self.members = []
        self.village = None       # the village a lesser house holds
        self.region = None
        self.fallen = None        # (day, why)
        self.allies = []          # houses bound by marriage
        self.feuds = []


class Kingdom:
    def __init__(self, kid, land, name, fg):
        self.id, self.short, self.name, self.fg = kid, land, name, fg
        self.king = None
        self.seat = None
        self.burden = 0           # taxes, levies and hunger: when it is heavy the villages rise
        self.civil = None         # dict(claimant, since, score): a disputed succession
        self.rebel = None         # dict(baron, rid, since, score)


class Barony:
    def __init__(self, rid, name, kingdom):
        self.rid, self.name, self.kingdom = rid, name, kingdom
        self.lord = None
        self.seat = None


class Realms:
    """Everything of the realms, kept in world.realm."""
    def __init__(self):
        self.empire = ''
        self.emperor = None
        self.great = None          # sid of the great city
        self.kingdoms = []
        self.baronies = {}
        self.houses = []
        self.lords = {}
        self.wars = []             # dict(a, b, since, cause, score, ...)
        self.next_id = 1
        self.month = 0
        self.adj = {}              # region -> neighbouring regions
        self.region_realm = []     # region -> realm key, see refresh
        self.labels = {}           # realm key -> (x, y)
        self.raid_cells = {}       # cell -> raider index: the raiders' own homelands
        self.events = 0

    def lord(self, lid):
        return self.lords.get(lid) if lid is not None else None

    def new_lord(self, first, gender, house, age):
        lid = self.next_id
        self.next_id += 1
        lo = Lord(lid, first, gender, house, age)
        self.lords[lid] = lo
        self.houses[house].members.append(lid)
        return lo


def get(game):
    return getattr(game.world, 'realm', None)


# ------------------------------------------------------------------ names: made, not picked
LAND_A = ['Ald', 'Val', 'Est', 'Mor', 'Cael', 'Bran', 'Il', 'Osk', 'Lor', 'Thes', 'Aer', 'Gal', 'Hal', 'Dun', 'Wester',
          'Nor', 'Ruth', 'Sel', 'Tor', 'Var', 'Wen', 'Ys', 'Cor', 'Mar', 'Eld', 'Ash', 'Kel', 'Lin', 'Brec', 'Hav']
LAND_M = ['', '', 'a', 'e', 'i', 'o', 'en', 'ar', 'ri', 'an']
LAND_B = ['mark', 'dren', 'hal', 'wick', 'lin', 'mond', 'more', 'land', 'garth', 'ria', 'vale', 'wald', 'heim', 'ford',
          'rest', 'mere', 'ney', 'ost', 'gard', 'don']
NORTH_B = ['heim', 'gard', 'mark', 'holm', 'vik', 'land', 'stad']
FORMS = ['The Kingdom of {}', 'The Realm of {}', 'The Crown of {}', 'The March of {}', 'The Principality of {}']
EMPIRE_FORMS = ['The {adj} Empire', 'The Empire of the {n} Crowns', 'The Empire of {land}', 'The {adj} Throne']
NUMBERS = {3: 'Three', 4: 'Four', 5: 'Five', 6: 'Six', 7: 'Seven'}
FAM_A = ['Ash', 'Black', 'Dun', 'Mor', 'Wolf', 'Hart', 'Grey', 'Raven', 'Thorn', 'Oak', 'Iron', 'Stone', 'Bright', 'Red',
         'Win', 'Hol', 'Al', 'Bar', 'Cor', 'Fen', 'Gar', 'Hal', 'Lan', 'Mal', 'Nor', 'Pen', 'Rath', 'Sed', 'Tre', 'Vey',
         'Wyn', 'Ell', 'Ever', 'Gold', 'Hawk', 'Kings', 'Lyn', 'March', 'Orme', 'Silver', 'Swan', 'Wake', 'Yew', 'Cress']
FAM_B = ['ford', 'wood', 'more', 'mont', 'hall', 'wick', 'ley', 'bourne', 'crest', 'vane', 'ward', 'helm', 'by',
         'brook', 'well', 'gard', 'ton', 'mere', 'fell', 'cliffe', 'holt', 'stone', 'combe', 'den', 'ridge', 'worth']
CHARGES = ['♦', '♥', '♣', '♠', '☼', 'Ω', '†', '¥', '○', '■', '▲', '*', 'Ψ', '∩', '§', '≈', '♪', 'ß', 'Θ', '¤']
TINCT = [(196, 40, 40), (40, 70, 170), (30, 120, 60), (20, 20, 24), (120, 40, 130), (200, 90, 30), (110, 70, 40)]
METAL = [(240, 210, 90), (230, 230, 236)]
CHARGE_NAME = {'♦': 'a lozenge', '♥': 'a heart', '♣': 'a trefoil', '♠': 'a leaf', '☼': 'a sun', 'Ω': 'a tower',
               '†': 'a cross', '¥': 'a forked staff', '○': 'a ring', '■': 'a block', '▲': 'a mountain', '*': 'a star',
               'Ψ': 'a trident', '∩': 'an arch', '§': 'a chain', '≈': 'waves', '♪': 'a bell', 'ß': 'a swan',
               'Θ': 'a shield', '¤': 'a wheel'}
TINCT_NAME = {(196, 40, 40): 'red', (40, 70, 170): 'blue', (30, 120, 60): 'green', (20, 20, 24): 'black',
              (120, 40, 130): 'purple', (200, 90, 30): 'orange', (110, 70, 40): 'brown',
              (240, 210, 90): 'gold', (230, 230, 236): 'silver'}
MOTTO_A = ['By', 'Through', 'Under', 'For', 'With', 'Before']
MOTTO_N = ['Oak and Iron', 'Fire and Faith', 'the Long Night', 'Stone', 'the Crown', 'Blood and Bread', 'the Old Road',
           'Our Own Hands', 'Sword and Plough', 'Rain and River', 'the Dawn', 'Hearth and Hall']
MOTTOS = ['We Stand', 'Ever Watchful', 'What Is Ours', 'Steadfast', 'The Night Is Long', 'We Do Not Bend', 'Last to Fall',
          'First to the Field', 'Remember', 'Patience Wins', 'Root and Branch', 'Ours the Fury', 'No Debt Unpaid',
          'Faith Keeps', 'We Hold', 'Quiet Waters Run Deep', 'Fortune Favours', 'The Wall Holds', 'Light in the Dark',
          'True to the End']
KINGDOM_FG = [(80, 120, 210), (190, 70, 110), (60, 160, 160), (200, 200, 210), (150, 90, 200), (110, 170, 90)]
EMPIRE_FG = (224, 190, 80)


def land_name(north=False):
    for _ in range(40):
        nm = random.choice(LAND_A) + random.choice(LAND_M) + random.choice(NORTH_B if north else LAND_B)
        if 5 <= len(nm) <= 10 and not any(nm[i] == nm[i + 1] == nm[i + 2] for i in range(len(nm) - 2)):
            return nm
    return random.choice(['Aldmark', 'Valdren', 'Esterhal'])


def family_name(used):
    for _ in range(60):
        nm = random.choice(FAM_A) + random.choice(FAM_B)
        if nm not in used and not (nm[-1] == nm[-2] == 'l'):
            used.add(nm)
            return nm
    nm = random.choice(FAM_A) + random.choice(FAM_B) + 'e'
    used.add(nm)
    return nm


def make_arms():
    field = random.choice(TINCT)
    charge = random.choice(CHARGES)
    return charge, random.choice(METAL), field


def arms_words(arms):
    ch, fg, bg = arms
    return f'{CHARGE_NAME.get(ch, "a charge")} of {TINCT_NAME.get(tuple(fg), "gold")} on {TINCT_NAME.get(tuple(bg), "red")}'


def motto():
    if random.random() < .35:
        return f'{random.choice(MOTTO_A)} {random.choice(MOTTO_N)}'
    return random.choice(MOTTOS)


def first_name(people, gender):
    from .races import random_name
    return random_name(people, gender, family=False)


# ------------------------------------------------------------------ how people are called
def style(R, lo, full=True):
    """'Baron Aldric Hale', 'Queen Edda of House Ashford', 'Edwin Hale, heir of House Hale'."""
    h = R.houses[lo.house]
    t = TITLES.get(lo.title, ('', ''))[1 if lo.gender == 'female' else 0]
    if lo.title == 'heir':
        return f'{lo.first} {h.name}' + (f', heir of House {h.name}' if full else '')
    if lo.title in ('king', 'emperor'):
        return f'{t} {lo.first}' + (f' of House {h.name}' if full else '')
    return f'{t} {lo.first} {h.name}'.strip()


def describe_lord(R, lo):
    """One plain sentence about a lord: who, how old, what like, who comes after."""
    tr = ' and '.join(TRAIT_WORD[t] for t in lo.traits) if lo.traits else 'little talked of'
    heir = R.lord(lo.heir)
    if heir and heir.alive:
        after = f'{lo.his} heir is {heir.first}, {heir.age}'
    else:
        after = f'{lo.he} has no heir'
    return f'{style(R, lo)}, {lo.age} years old, {tr}; {after}.'


def kingdom_of_region(R, rid):
    b = R.baronies.get(rid)
    return R.kingdoms[b.kingdom] if b is not None and b.kingdom is not None and b.kingdom >= 0 else None


def seat_pos(world, seat):
    if seat is None:
        return None
    k, ref = seat
    if k == 'hold':
        h = world.holds[ref]
        return h.x, h.y
    if k == 's':
        s = world.settlements[ref]
        return s.x, s.y
    st = world.sites[ref]
    return st.x, st.y


def seat_name(world, seat):
    k, ref = seat
    if k == 'hold':
        return world.holds[ref].title
    if k == 's':
        return world.settlements[ref].name
    return world.sites[ref].name


# ------------------------------------------------------------------ the shape of the regions
def organic(m, centers):
    """Every region grows over the land from its centre; mountains and rivers cost much to cross, so the borders
    follow the ridges and the rivers, with a little noise. Returns the region of every cell (water and islands
    nobody reaches go to the nearest centre)."""
    w, h = m.w, m.h
    n = w * h
    INF = 1 << 30
    dist = [INF] * n
    own = bytearray([255]) * n
    t, riv = m.t, getattr(m, 'river', None)
    cost = {D.GRASS: 10, D.SAND: 11, D.ROAD: 9, D.FOREST: 13, D.SWAMP: 18, D.HILLS: 20, D.MOUNTAIN: 90, D.RIVER: 70}
    heap = []
    for k, (x, y) in enumerate(centers):
        i = y * w + x
        dist[i] = 0
        own[i] = k
        heap.append((0, i))
    heapq.heapify(heap)
    pop, push = heapq.heappop, heapq.heappush
    while heap:
        d, i = pop(heap)
        if d > dist[i]:
            continue
        x = i % w
        o = own[i]
        for j in (i - 1 if x > 0 else -1, i + 1 if x < w - 1 else -1, i - w, i + w):
            if j < 0 or j >= n:
                continue
            c = cost.get(t[j])
            if c is None:
                tj = t[j]
                if tj == D.WATER or tj >= len(D.TILES):
                    continue
                c = 12 if D.TILES[tj].walk else 90
            if riv and riv[j]:
                c += 50
            c += ((j * 2654435761) >> 7) % 5            # the noise: borders do not run ruler-straight
            nd = d + c
            if nd < dist[j]:
                dist[j] = nd
                own[j] = o
                push(heap, (nd, j))
    if 255 in own:
        import numpy as np
        gy, gx = np.mgrid[0:h, 0:w]
        cxs = np.array([c[0] for c in centers])[:, None, None]
        cys = np.array([c[1] for c in centers])[:, None, None]
        nearest = ((gx[None] - cxs) ** 2 + (gy[None] - cys) ** 2).argmin(axis=0).ravel()
        a = np.frombuffer(bytes(own), dtype=np.uint8).copy()
        a[a == 255] = nearest[a == 255]
        own = bytearray(a.tobytes())
    return own


def adjacency(m, world):
    rof = world.region_of
    w = m.w
    adj = {r.id: set() for r in world.regions}
    for i in range(0, len(rof) - w - 1):
        a = rof[i]
        b, c = rof[i + 1], rof[i + w]
        if a != b and (i + 1) % w:
            adj[a].add(b)
            adj[b].add(a)
        if a != c:
            adj[a].add(c)
            adj[c].add(a)
    return {k: sorted(v) for k, v in adj.items()}


# ------------------------------------------------------------------ making the realm
def generate(game, m, world):
    """The empire, its kings, barons and lesser houses, the merchant families, and the other powers."""
    R = Realms()
    world.realm = R
    R.adj = adjacency(m, world)
    used = set()
    crown = [r for r in world.regions if r.faction == 'crown']
    if not crown:
        crown = [world.regions[0]]
        world.regions[0].faction = 'crown'
    setts = {}
    for s in world.settlements:
        setts.setdefault(s.region, []).append(s)
    tier = {'hamlet': 0, 'village': 1, 'town': 2, 'city': 3, 'metropolis': 4}
    # the great city: the largest town of the realm, and the emperor in it
    big = [s for r in crown for s in setts.get(r.id, []) if s.kind != 'deephold' and not getattr(s, 'elder', False)]
    great = max(big, key=lambda s: (tier.get(s.kind, 0), -s.id)) if big else world.settlements[0]
    R.great = great.id
    # the kingdoms: their seats as far apart as the land allows
    k_n = max(1, min(5, max(3, len(crown) // 5))) if len(crown) >= 3 else len(crown)
    seats = [('s', great.id, great.x, great.y)]
    cands = [('s', s.id, s.x, s.y) for s in big if s.kind in ('town', 'city', 'metropolis') and s.id != great.id] + \
            [('hold', h.id, h.x, h.y) for h in world.holds if h.faction == 'crown' and h.kind == 'castle']
    while len(seats) < k_n and cands:
        c = max(cands, key=lambda c: min(cheb(c[2], c[3], s[2], s[3]) for s in seats))
        if min(cheb(c[2], c[3], s[2], s[3]) for s in seats) < 30:
            break
        seats.append(c)
        cands.remove(c)
    north_line = m.h * .36
    for k, (kind, ref, sx, sy) in enumerate(seats):
        land = land_name(north=sy < north_line)
        name = random.choice(FORMS).format(land)
        kg = Kingdom(k, land, name, EMPIRE_FG if k == 0 else KINGDOM_FG[(k - 1) % len(KINGDOM_FG)])
        kg.seat = (kind, ref)
        R.kingdoms.append(kg)
    # each crown region to the nearest kingdom seat
    for r in crown:
        kid = min(range(len(seats)), key=lambda k: cheb(r.cx, r.cy, seats[k][2], seats[k][3]))
        R.baronies[r.id] = Barony(r.id, '', kid)
    for k, (kind, ref, sx, sy) in enumerate(seats):
        rid = world.region_of[sy * m.w + sx]
        if rid in R.baronies:
            R.baronies[rid].kingdom = k
    # the empire's name
    adj = R.kingdoms[0].short[:-1] + 'ic' if R.kingdoms[0].short[-1] in 'aeiouy' else R.kingdoms[0].short + 'ic'
    adj = adj.replace('kic', 'kian').replace('dic', 'dic')
    R.empire = random.choice(EMPIRE_FORMS).format(adj=random.choice(['Aldic', 'Varnic', adj]), n=NUMBERS.get(len(seats) + 2, 'Seven'),
                                                  land=R.kingdoms[0].short)
    if 'crown' in D.FACTIONS:
        D.FACTIONS['crown']['name'] = R.empire
        D.FACTIONS['crown']['short'] = 'Empire'
        D.FACTIONS['crown']['race'] = 'human'
        world.factions['crown'].update(name=R.empire, short='Empire', race='human')
    # baronies: their seats and names
    holds = {}
    for h in world.holds:
        if h.faction == 'crown':
            holds.setdefault(h.region, []).append(h)
    for rid, b in R.baronies.items():
        r = world.regions[rid]
        hs = sorted(holds.get(rid, []), key=lambda h: h.kind != 'castle')
        ss = sorted((s for s in setts.get(rid, []) if s.kind != 'deephold' and not getattr(s, 'elder', False)),
                    key=lambda s: -tier.get(s.kind, 0))
        kg = R.kingdoms[b.kingdom]
        if kg.seat[0] == 's' and world.settlements[kg.seat[1]].region == rid:
            b.seat = kg.seat
        elif kg.seat[0] == 'hold' and world.holds[kg.seat[1]].region == rid:
            b.seat = kg.seat
        elif hs:
            b.seat = ('hold', hs[0].id)
        elif ss:
            b.seat = ('s', ss[0].id)
        chief = seat_name(world, b.seat) if b.seat else r.name
        border = any(world.regions[o].faction not in ('crown', 'league') for o in R.adj.get(rid, []))
        if border and random.random() < .45:
            b.name = f'The {chief.replace("The ", "")} March' if b.seat else f'The March of {r.name}'
        else:
            b.name = f'Barony of {chief}'
    # houses and lords: the emperor's, the kings', the barons'
    for kg in R.kingdoms:
        h = new_house(R, used, 'human', 'royal' if kg.id else 'imperial', 2)
        h.seat = kg.seat
        king = founder(R, h, 'emperor' if kg.id == 0 else 'king', random.randint(28, 66))
        kg.king = king.id
        if kg.id == 0:
            R.emperor = king.id
    for rid, b in sorted(R.baronies.items()):
        kg = R.kingdoms[b.kingdom]
        if b.seat == kg.seat:
            b.lord = kg.king
            continue
        h = new_house(R, used, 'human', 'baronial', 1 + (random.random() < .4))
        h.region = rid
        h.seat = b.seat
        lo = founder(R, h, 'baron', random.randint(24, 70))
        lo.liege = kg.king
        b.lord = lo.id
    for kg in R.kingdoms:
        if kg.id:
            R.lords[kg.king].liege = R.emperor
    # lesser houses, each with a seat beside the village it holds
    place_seats(game, m, world, R, used, setts)
    # baronies with no castle or town of their own: the richest lesser house becomes the baron's
    for rid, b in R.baronies.items():
        if b.seat is not None:
            continue
        hs = [h for h in R.houses if h.rank == 'lesser' and h.region == rid]
        if hs:
            h = max(hs, key=lambda q: q.wealth)
            raise_house(R, world, h, b)
        else:
            kg = R.kingdoms[b.kingdom]
            b.seat = kg.seat
            b.lord = kg.king
    # merchant families in the cities
    for s in world.settlements:
        if s.is_city and s.faction in ('crown', 'league') and random.random() < .8:
            h = new_house(R, used, s.race if s.race in ('human', 'halfling', 'dwarf') else 'human', 'merchant', 2)
            h.seat = ('s', s.id)
            h.region = s.region
            founder(R, h, 'merchant', random.randint(30, 68))
    from . import powers as PW
    PW.generate(game, m, world, R)
    refresh(world)
    from . import history as HI
    HI.generate(game, m, world, R)


def new_house(R, used, people, rank, wealth):
    h = House(len(R.houses), family_name(used), people, rank)
    h.arms = make_arms()
    h.motto = motto()
    h.wealth = wealth
    R.houses.append(h)
    return h


def founder(R, h, title, age):
    """The head of a house, with an heir and sometimes a younger child."""
    g = random.choice(['male', 'male', 'female'])
    lo = R.new_lord(first_name(h.people, g), g, h.id, age)
    lo.title = title
    lo.traits = random.sample(TRAITS, random.choice([1, 1, 2]))
    lo.loyalty = random.randint(35, 90)
    h.head = lo.id
    if age >= 22 and random.random() < .85:
        heir = new_heir(R, h, lo)
        lo.heir = heir.id
    return lo


def new_heir(R, h, parent):
    g = random.choice(['male', 'female'])
    age = max(1, parent.age - random.randint(18, 34))
    lo = R.new_lord(first_name(h.people, g), g, h.id, age)
    lo.title = 'heir'
    lo.traits = random.sample(TRAITS, 1)
    lo.loyalty = parent.loyalty
    return lo


SEAT_STYLE = {0: 'farm', 1: 'tower', 2: 'manor'}
SEAT_NOUN = {'farm': ['Steading', 'Farm', 'Stead'], 'tower': ['Tower', 'Peel', 'Towerhouse'], 'manor': ['Hall', 'Manor', 'Court']}


def place_seats(game, m, world, R, used, setts):
    from .sites import Site
    taken = [(s.x, s.y) for s in world.settlements] + [(h.x, h.y) for h in world.holds] + \
            [(d.x, d.y) for d in world.dungeons.values()] + [(q.x, q.y) for q in world.sites]
    from .world import scaled
    cap = scaled(30)
    made = 0
    for rid, b in sorted(R.baronies.items(), key=lambda kv: random.random()):
        villages = [s for s in setts.get(rid, []) if s.kind in ('hamlet', 'village', 'town') and s.id != 0
                    and not getattr(s, 'dwarven', False) and s.kind != 'deephold']
        random.shuffle(villages)
        for v in villages[:random.choice([2, 2, 3])]:
            if made >= cap:
                return
            spot = seat_spot(m, world, v, taken)
            if not spot:
                continue
            wealth = random.choices([0, 1, 2], [5, 3, 2])[0]
            h = new_house(R, used, 'human', 'lesser', wealth)
            sty = SEAT_STYLE[wealth]
            st = Site(len(world.sites), 'seat', spot[0], spot[1], f'{h.name} {random.choice(SEAT_NOUN[sty])}')
            st.faction = 'crown'
            st.house = h.id
            st.style = sty
            world.sites.append(st)
            taken.append(spot)
            h.seat = ('site', st.id)
            h.village = v.id
            h.region = rid
            lo = founder(R, h, 'lord', random.randint(22, 72))
            lo.liege = b.lord
            made += 1


def seat_spot(m, world, v, taken):
    """Beside the village, fitting the land: a hill, a river bend, the edge of a wood."""
    best, score = None, -99
    for _ in range(90):
        x, y = v.x + random.randint(-7, 7), v.y + random.randint(-6, 6)
        if not (3 <= x < m.w - 3 and 3 <= y < m.h - 3) or cheb(x, y, v.x, v.y) < 3:
            continue
        t = m.tile(x, y)
        if not D.TILES[t].walk or t in (D.ROAD, D.TOWN, D.CITY, D.ENTR, D.RIVER, D.CASTLE, D.FORT, D.SWAMP):
            continue
        i = y * m.w + x
        if i in getattr(world, 'wonder_cells', ()) or world.region_of[i] != v.region:
            continue
        if any(cheb(x, y, a, b) < 4 for a, b in taken):
            continue
        sc = random.random()
        if t == D.HILLS:
            sc += 2
        around = [m.tile(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if m.inb(x + dx, y + dy)]
        if D.RIVER in around:
            sc += 1.6
        if D.FOREST in around and t != D.FOREST:
            sc += 1.2
        if world.road_dist[i] <= 2:
            sc += .5
        if sc > score:
            best, score = (x, y), sc
    return best


def raise_house(R, world, h, b):
    """A lesser house becomes the baron's: its head is the baron now, its seat the barony's."""
    h.rank = 'baronial'
    b.seat = h.seat
    old = R.lord(b.lord)
    b.lord = h.head
    lo = R.lord(h.head)
    lo.title = 'baron'
    lo.liege = R.kingdoms[b.kingdom].king
    if h.seat and h.seat[0] == 'site':
        st = world.sites[h.seat[1]]
        if st.style != 'manor':
            st.style = 'manor'                         # a house that rises gets a bigger seat
            st.name = f'{h.name} Hall'
            st.stale = True
    for o in R.houses:
        if o.rank == 'lesser' and o.region == b.rid and o.head is not None and R.lords[o.head].liege == (old.id if old else None):
            R.lords[o.head].liege = lo.id
    return lo


# ------------------------------------------------------------------ the realms layer
def refresh(world):
    """Which realm every region belongs to now, and where its name goes on the map."""
    R = world.realm
    out = []
    for r in world.regions:
        out.append(realm_key(world, r.id))
    R.region_realm = out
    sums = {}
    for r in world.regions:
        k = out[r.id]
        if k is None:
            continue
        a = sums.setdefault(k, [0, 0, 0])
        a[0] += r.cx
        a[1] += r.cy
        a[2] += 1
    R.labels = {k: (round(a[0] / a[2]), round(a[1] / a[2])) for k, a in sums.items()}


def realm_key(world, rid):
    R = world.realm
    r = world.regions[rid]
    b = R.baronies.get(rid)
    held = getattr(b, 'held_by', None) if b else None
    if held is not None:
        return ('raid', held)
    sv = getattr(world, 'shadow', None)
    if sv and b is not None and rid in sv['held']:
        return ('evil', sv['held'][rid])                # a servant of the Hollow King holds it (shadow.py)
    if r.faction == 'crown' and b is not None:
        return ('k', b.kingdom)
    if r.faction == 'crown':
        return ('k', 0)
    if r.faction in ('league', 'clan', 'circle', 'horde'):
        return (r.faction,)
    return None                                         # outlaws and the cult: lawless land


def realm_info(world, key):
    """(name, colour) of a realm on the map."""
    R = world.realm
    if key is None:
        return None, None
    if key[0] == 'k':
        kg = R.kingdoms[key[1]]
        return kg.short, kg.fg
    if key[0] == 'raid':
        from . import powers as PW
        rd = PW.raiders(world)[key[1]]
        return rd['land'], rd['fg']
    if key[0] == 'evil':
        e = world.evils[key[1]]
        return (e.name if e.known else 'Lost lands'), e.fg
    f = D.FACTIONS.get(key[0])
    if not f:
        return None, None
    if key[0] == 'horde':
        from . import powers as PW
        return PW.tribes_name(world), f['fg']
    return f['short'] if key[0] != 'league' else f['name'].replace('The ', ''), f['fg']


def cell_realm(world, i):
    R = world.realm
    rd = R.raid_cells.get(i)
    if rd is not None:
        return ('raid', rd)
    return R.region_realm[world.region_of[i]]


def layer_look(world, m, x, y):
    """(colour, border) for a cell in the realms layer: border 2 where two realms meet, 1 between baronies."""
    i = y * m.w + x
    key = cell_realm(world, i)
    if key is None:
        return None, 0
    col = realm_info(world, key)[1]
    rof = world.region_of
    r = rof[i]
    border = 0
    for j in (i - 1, i + 1, i - m.w, i + m.w):
        if 0 <= j < len(rof):
            if cell_realm(world, j) != key and m.t[j] != D.WATER:
                return col, 2
            if rof[j] != r:
                border = 1
    return col, border


def seats_on_map(world):
    """(x, y, sign) of the kings' seats and the barons' seats, for the realms layer."""
    R = world.realm
    out = []
    kings = {kg.seat for kg in R.kingdoms}
    for b in R.baronies.values():
        if b.seat and b.seat not in kings:
            p = seat_pos(world, b.seat)
            if p:
                out.append((p[0], p[1], '·'))
    for kg in R.kingdoms:
        p = seat_pos(world, kg.seat)
        if p:
            out.append((p[0], p[1], '♦'))
    return out


# ------------------------------------------------------------------ what people hear
def news(game, text, x, y, chapter='The Realms', key=None, false=None, title=None):
    """A court event, told in the inns from now on; kept in the chronicle as heard when someone tells it. With
    false, a garbled telling goes round as well; whoever hears it first may believe it."""
    from . import news as NW
    R = get(game)
    R.events += 1
    key = key or f'rl{R.events}'
    NW.post(game, 'realm', text, x, y)
    NW.store(game)[-1]['fact'] = dict(ch=chapter, key=key, title=title)
    if false:
        NW.post(game, 'realm', false, x, y)
        NW.store(game)[-1]['fact'] = dict(ch=chapter, key=key + 'f', truth=key, title=None, false=True)
    return key


def heard(game, n, npc=None):
    """news.tell calls this for a piece of news that carries a fact."""
    from . import chronicle as CH
    f = n.get('fact')
    if not f:
        return
    fs = CH.facts(game)
    if f.get('false'):
        if any(o['key'] == f['truth'] for o in fs):
            return                                       # you know better already
        CH.add(game, f['ch'], n['text'], 'heard', CH.speaker(npc), key=f['key'], quiet=True)
        return
    CH.add(game, f['ch'], n['text'], 'heard', CH.speaker(npc), key=f['key'], place=(n['x'], n['y']), title=f.get('title'))
    false = next((o for o in fs if o['key'] == f['key'] + 'f'), None)
    if false:
        CH.disprove(game, false['key'], f'Not so: {n["text"]}')


def lord_seen(game, lo):
    """You met this lord: a seen fact in Lords and houses, and an end to rumours of his death."""
    from . import chronicle as CH
    R = get(game)
    lo.met = True
    h = R.houses[lo.house]
    CH.add(game, 'Lords and houses', describe_lord(R, lo) + f' The arms of House {h.name}: {arms_words(h.arms)}. '
           f'"{h.motto}."', 'seen', where=game.loc_name(), key=f'lord:{lo.id}', title=style(R, lo, False), quiet=True)
    for f in CH.facts(game):
        if f.get('about') == lo.id and f['src'] == 'heard' and not f['false']:
            CH.disprove(game, f['key'], f'Not so: you met {style(R, lo, False)} yourself, {game.loc_name()}.')


# ------------------------------------------------------------------ the months
def daily(game):
    R = get(game)
    if R is None:
        return
    from . import calendar as CAL
    mo = (CAL.START + game.day - 1) // CAL.DAYS_IN_MONTH
    if mo != R.month:
        R.month = mo
        monthly(game)
    from . import powers as PW
    PW.daily(game)


def monthly(game):
    R = get(game)
    w = game.world
    for l in list(R.lords.values()):
        if l.alive and random.random() < 1 / 12:
            l.age += 1                                   # a birthday somewhere in the year
    for kg in R.kingdoms:
        if random.random() < .5:
            court_event(game, kg)
        civil_month(game, kg)
        rebel_month(game, kg)
        kg.burden = max(0, kg.burden - (1 if random.random() < .3 else 0))
    if random.random() < .25:
        emperor_event(game)
    for war in list(R.wars):
        war_month(game, war)
    from . import powers as PW
    PW.monthly(game)
    from . import shadow as SH
    SH.monthly(game)
    refresh(w)


def lords_of(R, kg):
    """Every living head of a house that answers to this kingdom."""
    out = []
    for b in R.baronies.values():
        if b.kingdom == kg.id and getattr(b, 'held_by', None) is None:
            lo = R.lord(b.lord)
            if lo and lo.alive:
                out.append(lo)
    for h in R.houses:
        if h.rank == 'lesser' and not h.fallen and h.region in R.baronies and R.baronies[h.region].kingdom == kg.id:
            lo = R.lord(h.head)
            if lo and lo.alive:
                out.append(lo)
    return out


def court_event(game, kg):
    R = get(game)
    lords = lords_of(R, kg)
    king = R.lord(kg.king)
    opts = ['death'] * 3 + ['marriage'] * 2 + ['insult'] * 2 + ['tax']
    if any(lo.title == 'baron' and 'ambitious' in lo.traits and lo.loyalty < 50 for lo in lords) and not kg.rebel:
        opts += ['rebel'] * 2
    if any(lo.title == 'baron' and 'ambitious' in lo.traits for lo in lords):
        opts += ['claim']
    if any(w_['a'] == kg.id or w_['b'] == kg.id for w_ in R.wars):
        opts += ['levy'] * 2
    if king and 'greedy' in king.traits:
        opts += ['tax']
    ev = random.choice(opts)
    if ev == 'death':
        cands = [lo for lo in lords + [king] if lo and lo.alive]
        if cands:
            lo = random.choices(cands, [max(1, lo.age - 35) ** 2 for lo in cands])[0]
            if random.random() < .25 + max(0, lo.age - 50) / 40:
                die(game, lo, random.choice(['a fever', 'a fall from his horse' if lo.gender != 'female' else 'a fall from her horse',
                                             'old age' if lo.age > 60 else 'a winter cough', 'a hunting accident',
                                             'a wasting sickness']))
    elif ev == 'marriage':
        marry(game, kg, lords)
    elif ev == 'insult':
        insult(game, kg, lords)
    elif ev == 'rebel':
        rebel(game, kg, lords)
    elif ev == 'claim':
        claim(game, kg, lords)
    elif ev == 'levy':
        levy(game, kg)
    elif ev == 'tax':
        tax(game, kg)


def place_of(game, lo):
    """Where a lord sits, as (x, y)."""
    R = get(game)
    w = game.world
    h = R.houses[lo.house]
    p = seat_pos(w, h.seat) if h.seat else None
    if p:
        return p
    s = w.settlements[R.great]
    return s.x, s.y


def die(game, lo, how):
    """A lord dies. The heir follows; a child heir or none at all makes trouble."""
    R = get(game)
    w = game.world
    lo.alive = False
    lo.died = (game.day, how)
    h = R.houses[lo.house]
    x, y = place_of(game, lo)
    heir = R.lord(lo.heir)
    title = lo.title
    if title == 'heir':
        news(game, f'{lo.first} {h.name}, heir of House {h.name}, died of {how}.', x, y, 'Lords and houses')
        for o in list(R.lords.values()):
            if o.heir == lo.id:
                o.heir = None
                if o.alive and o.age < 60 and random.random() < .5:
                    o.heir = new_heir(R, h, o).id
        return
    false = None
    if random.random() < .25:
        other = random.choice([o for o in R.lords.values() if o.alive and o.title in ('baron', 'lord') and o.id != lo.id] or [lo])
        false = f'{style(R, other, False)} is dead, of {how}.'
    news(game, f'{style(R, lo, False)} is dead, of {how}.', x, y, 'Lords and houses', false=false,
         title=f'The death of {lo.first} {h.name}' if title in ('king', 'emperor', 'baron') else None)
    if false:
        from . import news as NW
        NW.store(game)[-1]['fact']['about'] = other.id
    if heir and heir.alive and heir.age >= 16:
        succeed(game, lo, heir)
        return
    if title in ('king', 'emperor'):
        kg = next(k for k in R.kingdoms if k.king == lo.id)
        claimant = strongest(R, kg, lo)
        if heir and heir.alive:
            succeed(game, lo, heir, regent=True)
            if claimant and random.random() < .7:
                civil_war(game, kg, claimant)
        elif claimant:
            succeed(game, lo, claimant, quiet=True)
            news(game, f'{style(R, claimant, False)} takes the crown of {kg.short}; nobody else had a better claim.',
                 x, y, 'The Realms')
        return
    if title == 'baron':
        b = next((b for b in R.baronies.values() if b.lord == lo.id), None)
        if heir and heir.alive:
            succeed(game, lo, heir, regent=True)
            return
        cands = [o for o in R.houses if o.rank == 'lesser' and not o.fallen and b and o.region == b.rid]
        if cands and b:
            o = max(cands, key=lambda q: (q.wealth, random.random()))
            nl = raise_house(R, w, o, b)
            news(game, f'With no heir in House {h.name}, House {o.name} takes the {b.name}; '
                       f'{style(R, nl, False)} rules there now.', x, y, 'Lords and houses')
            fall(game, h, 'its last lord died without an heir')
        elif b:
            kg = R.kingdoms[b.kingdom]
            b.lord = kg.king
            news(game, f'The {b.name} falls to the crown of {kg.short}: House {h.name} died with its lord.', x, y)
            h.fallen = (game.day, 'its last lord died without an heir')
        return
    if title == 'lord':
        if heir and heir.alive:
            succeed(game, lo, heir, regent=True)
        else:
            fall(game, h, 'its last lord died without an heir')
        return
    if title == 'merchant':
        if heir and heir.alive:
            succeed(game, lo, heir, quiet=True)
        else:
            h.fallen = (game.day, 'the family died out')


def succeed(game, old, new, regent=False, quiet=False):
    """The heir takes the title (with a regent while he is a child), and the maps where the old lord stood know it."""
    R = get(game)
    h = R.houses[old.house]
    new.title = old.title
    new.liege = old.liege
    new.loyalty = max(20, old.loyalty + random.randint(-15, 10))
    if new.house != old.house:
        h = R.houses[new.house]
    h.head = new.id
    for kg in R.kingdoms:
        if kg.king == old.id:
            kg.king = new.id
            if R.emperor == old.id:
                R.emperor = new.id
    for b in R.baronies.values():
        if b.lord == old.id:
            b.lord = new.id
    for o in R.lords.values():
        if o.liege == old.id:
            o.liege = new.id
    if new.age >= 22 and random.random() < .7:
        new.heir = new_heir(R, h, new).id
    elif new.age < 22:
        sib = [o for o in h.members if R.lords[o].alive and R.lords[o].title == 'heir' and o != new.id]
        new.heir = sib[0] if sib else None
    x, y = place_of(game, new)
    if not quiet:
        word = ', with a regent until the child comes of age' if regent and new.age < 16 else ''
        news(game, f'{style(R, new, False)} follows {old.first} as head of House {h.name}{word}.', x, y, 'Lords and houses')
    swap_npcs(game, old, new)
    p = game.player
    kn = getattr(p, 'knight', None)
    if kn and kn['lid'] == old.id:
        kn['lid'] = new.id
        game.msg(f'Your liege {old.first} is dead. You owe your oath to {style(R, new, False)} now.', 'info')


def swap_npcs(game, old, new):
    R = get(game)
    for mp in game.maps.values():
        for o in getattr(mp, 'mons', ()):
            if getattr(o, 'lord', None) == old.id:
                o.lord = new.id
                o.name = style(R, new, False)
            elif getattr(o, 'lord', None) == new.id and getattr(o, 'role', '') == 'heir':
                o.role = 'lord'
                o.name = style(R, new, False)


def strongest(R, kg, dead):
    """Whoever would press a claim: the boldest baron of the kingdom."""
    cands = [lo for lo in lords_of(R, kg) if lo.title == 'baron' and lo.id != dead.id]
    if not cands:
        return None
    return max(cands, key=lambda lo: ('ambitious' in lo.traits, R.houses[lo.house].wealth, -lo.loyalty, random.random()))


def fall(game, h, why):
    """A lesser house falls: its seat stands burnt or empty, a ruin to explore."""
    R = get(game)
    w = game.world
    h.fallen = (game.day, why)
    if h.seat and h.seat[0] == 'site':
        st = w.sites[h.seat[1]]
        if st.kind == 'seat':
            st.fallen = True
            st.burnt = random.random() < .6
            st.stale = True
            game.maps.pop(st.map_key, None) if game.cur != st.map_key else None
            news(game, f'House {h.name} has fallen: {why}. {st.name} stands {"burnt" if st.burnt else "empty"}.',
                 st.x, st.y, 'Lords and houses')


def civil_war(game, kg, claimant):
    R = get(game)
    if kg.civil:
        return
    kg.civil = dict(claimant=claimant.id, since=game.day, score=0)
    x, y = place_of(game, claimant)
    news(game, f'{style(R, claimant, False)} claims the crown of {kg.short}. The lords of {kg.short} take sides: it is '
               f'civil war.', x, y, title=f'The war of the {kg.short} crown')
    kg.burden += 1


def civil_month(game, kg):
    R = get(game)
    c = kg.civil
    if not c:
        return
    claimant = R.lord(c['claimant'])
    king = R.lord(kg.king)
    if not claimant or not claimant.alive:
        kg.civil = None
        news(game, f'The war of the {kg.short} crown is over: the claimant is dead.', *place_of(game, king))
        return
    c['score'] += random.choice([-1, 0, 1]) + (1 if 'brave' in claimant.traits else 0) - (1 if 'brave' in king.traits else 0)
    battle_between(game, claimant, king, f'the men of {kg.short}')
    if c['score'] >= 3 or (game.day - c['since'] > 150 and c['score'] > 0):
        kg.civil = None
        news(game, f'{style(R, claimant, False)} has won the war of the {kg.short} crown. {king.first} flees into exile.',
             *place_of(game, claimant), title=f'{claimant.first} takes the crown of {kg.short}')
        from . import powers as PW
        PW.exile(game, king, kg)
        crown(game, kg, claimant)
    elif c['score'] <= -3 or game.day - c['since'] > 180:
        kg.civil = None
        news(game, f'{style(R, king, False)} has crushed the claim of {claimant.first} {R.houses[claimant.house].name}.',
             *place_of(game, king))
        from . import powers as PW
        PW.exile(game, claimant, kg)


def crown(game, kg, lo):
    """lo becomes king of kg; his old barony goes to his heir or the crown."""
    R = get(game)
    old = R.lord(kg.king)
    b_old = next((b for b in R.baronies.values() if b.lord == lo.id), None)
    lo.title = 'emperor' if R.emperor == (old.id if old else None) else 'king'
    if R.emperor == (old.id if old else None):
        R.emperor = lo.id
    lo.liege = None if lo.title == 'emperor' else R.emperor
    kg.king = lo.id
    for b in R.baronies.values():
        if old and b.lord == old.id:
            b.lord = lo.id
    for o in R.lords.values():
        if old and o.liege == old.id and o.id != lo.id:
            o.liege = lo.id
    if b_old:
        heir = R.lord(lo.heir)
        if heir and heir.alive and heir.age >= 16:
            heir.title = 'baron'
            heir.liege = lo.id
            b_old.lord = heir.id
    if old:
        old.title = 'heir' if old.alive else old.title
        swap_npcs(game, old, lo)


def battle_between(game, a, b, who):
    """Two lords' men meet in the field between their seats."""
    from .living import battle
    ax, ay = place_of(game, a)
    bx, by = place_of(game, b)
    x, y = (ax + bx) // 2, (ay + by) // 2
    om = game.maps['over']
    for _ in range(20):
        if om.inb(x, y) and D.TILES[om.tile(x, y)].walk and om.tile(x, y) not in (D.TOWN, D.CITY, D.CASTLE, D.FORT):
            battle(game, x, y, who)
            return x, y
        x += random.randint(-2, 2)
        y += random.randint(-2, 2)
    return None


def marry(game, kg, lords):
    R = get(game)
    if len(lords) < 2:
        return
    a, b = random.sample(lords, 2)
    ha, hb = R.houses[a.house], R.houses[b.house]
    if ha.id == hb.id or hb.id in ha.allies:
        return
    ha.allies.append(hb.id)
    hb.allies.append(ha.id)
    for f in (ha.feuds, hb.feuds):
        for o in (ha.id, hb.id):
            if o in f:
                f.remove(o)
    a.loyalty = min(100, a.loyalty + 8)
    b.loyalty = min(100, b.loyalty + 8)
    x, y = place_of(game, a)
    news(game, f'A marriage binds House {ha.name} and House {hb.name}: there will be a wedding at '
               f'{seat_name(game.world, ha.seat) if ha.seat else "the court"}.', x, y, 'Lords and houses')
    from . import powers as PW
    PW.note(game, 'wedding', dict(houses=(ha.id, hb.id), day=game.day + random.randint(8, 20), lid=a.id))


def insult(game, kg, lords):
    R = get(game)
    if len(lords) < 2:
        return
    a, b = random.sample(lords, 2)
    ha, hb = R.houses[a.house], R.houses[b.house]
    if ha.id == hb.id:
        return
    was = hb.id in ha.allies
    for x_, y_ in ((ha, hb), (hb, ha)):
        if y_.id in x_.allies:
            x_.allies.remove(y_.id)
        if y_.id not in x_.feuds:
            x_.feuds.append(y_.id)
    x, y = place_of(game, a)
    if random.random() < .2 and b.title != 'king':
        news(game, f'{style(R, a, False)} has had {b.first} {hb.name} murdered, they whisper. The houses are at feud.',
             x, y, 'Lords and houses')
        die(game, b, 'a knife in the dark')
    elif was:
        news(game, f'The bond between House {ha.name} and House {hb.name} is broken: an insult at table, and swords drawn.',
             x, y, 'Lords and houses')
    else:
        news(game, f'House {ha.name} and House {hb.name} are at feud over a stolen herd and a burnt mill.', x, y,
             'Lords and houses')


def rebel(game, kg, lords):
    R = get(game)
    cands = [lo for lo in lords if lo.title == 'baron' and 'ambitious' in lo.traits and lo.loyalty < 50]
    if not cands or kg.rebel:
        return
    lo = random.choice(cands)
    b = next((b for b in R.baronies.values() if b.lord == lo.id), None)
    if not b:
        return
    kg.rebel = dict(baron=lo.id, rid=b.rid, since=game.day, score=0)
    news(game, f'{style(R, lo, False)} of the {b.name} has risen against {style(R, R.lord(kg.king), False)}. '
               f'The gates of {seat_name(game.world, b.seat)} are shut.', *place_of(game, lo),
         title=f'The rising of the {b.name}')
    kg.burden += 1


def rebel_month(game, kg):
    R = get(game)
    rb = kg.rebel
    if not rb:
        return
    lo = R.lord(rb['baron'])
    king = R.lord(kg.king)
    if not lo or not lo.alive:
        kg.rebel = None
        return
    rb['score'] += random.choice([-1, -1, 0, 1]) + rb.get('help', 0)
    rb['help'] = 0
    battle_between(game, lo, king, f'the rebels of {lo.first} {R.houses[lo.house].name} and the king\'s men')
    b = R.baronies[rb['rid']]
    if rb['score'] >= 3:
        kg.rebel = None
        lo.loyalty = 60
        news(game, f'The king could not break {lo.first} {R.houses[lo.house].name}: the {b.name} keeps its lord and '
                   f'pays no tax for three years.', *place_of(game, lo))
    elif rb['score'] <= -2 or game.day - rb['since'] > 150:
        kg.rebel = None
        news(game, f'The rising of the {b.name} is put down. {style(R, lo, False)} is hanged at '
                   f'{seat_name(game.world, b.seat)}.', *place_of(game, lo))
        die(game, lo, 'the rope')


def claim(game, kg, lords):
    R = get(game)
    cands = [lo for lo in lords if lo.title == 'baron' and 'ambitious' in lo.traits]
    if not cands:
        return
    lo = random.choice(cands)
    b = next((b for b in R.baronies.values() if b.lord == lo.id), None)
    if not b:
        return
    near = [R.baronies[o] for o in R.adj.get(b.rid, []) if o in R.baronies and R.baronies[o].kingdom != b.kingdom
            and getattr(R.baronies[o], 'held_by', None) is None]
    if not near:
        return
    tgt = random.choice(near)
    other = R.kingdoms[tgt.kingdom]
    if any({w_['a'], w_['b']} == {kg.id, other.id} for w_ in R.wars):
        return
    start_war(game, kg, other, f'the claim of {lo.first} {R.houses[lo.house].name} to the {tgt.name}', tgt.rid)


def start_war(game, a, b, cause, rid=None):
    R = get(game)
    war = dict(a=a.id, b=b.id, since=game.day, cause=cause, score=0, rid=rid, host=None)
    R.wars.append(war)
    king = R.lord(a.king)
    news(game, f'War: {a.short} against {b.short}, over {cause}.', *place_of(game, king),
         title=f'The war of {a.short} and {b.short}')
    for k in (a, b):
        k.burden += 1
    from . import powers as PW
    PW.note(game, 'war', dict(a=a.id, b=b.id))
    summon(game, a, b)
    summon(game, b, a)


def summon(game, kg, foe):
    """A knight of a kingdom at war is called to the levy."""
    p = game.player
    kn = getattr(p, 'knight', None)
    if not kn or kn.get('kid') != kg.id:
        return
    from . import realmjobs as RJ
    RJ.levy(game, kg, foe)


def war_month(game, war):
    """A month of a war: a host marches from a seat to the enemy's, or the war ends."""
    R = get(game)
    a, b = R.kingdoms[war['a']], R.kingdoms[war['b']]
    age = game.day - war['since']
    if age > 60 and random.random() < .12 + age / 1200 + abs(war['score']) * .08:
        end_war(game, war)
        return
    if war.get('host') is not None and any(x.id == war['host'] for x in game.world.wanderers):
        return
    att, dfd = (a, b) if random.random() < .5 + war['score'] * .05 else (b, a)
    march(game, war, att, dfd)


def march(game, war, att, dfd):
    from .wanderers import Wanderer
    from .world import dijkstra_path
    R = get(game)
    w = game.world
    mine = [rid for rid, b in R.baronies.items() if b.kingdom == att.id]
    theirs = [rid for rid, b in R.baronies.items() if b.kingdom == dfd.id and b.seat]
    pairs = [(m_, t) for m_ in mine for t in R.adj.get(m_, []) if t in theirs]
    if pairs:
        src_r, tgt_r = random.choice(pairs)
    elif mine and theirs:
        src_r, tgt_r = random.choice(mine), random.choice(theirs)
    else:
        return
    sb, tb = R.baronies[src_r], R.baronies[tgt_r]
    sp = seat_pos(w, sb.seat) or (w.regions[src_r].cx, w.regions[src_r].cy)
    tp = seat_pos(w, tb.seat)
    om = game.maps['over']
    path = dijkstra_path(om, sp, tp, lambda t: D.TILES[t].cost if D.TILES[t].walk else None)
    if not path or len(path) < 3:
        return
    wd = Wanderer(game.new_id(), 'host', sp[0], sp[1])
    wd.ch, wd.fg = 'K', att.fg
    wd.name = f'The host of {att.short}'
    wd.path = path[:-1]
    wd.speed = 12
    wd.kingdom, wd.foe, wd.target_r = att.id, dfd.id, tgt_r
    wd.strength = random.randint(8, 16) + R.houses[R.lord(att.king).house].wealth * 2
    wd.group = dict(keys=['soldier', 'soldier', 'crossbow', 'knight'], lvl=max(4, w.danger_at(*tp) + 2), elite=0,
                    leader=None, faction='crown')
    wd.hostile = hostile_host(game, wd)
    w.wanderers.append(wd)
    war['host'] = wd.id
    news(game, f'The host of {att.short} marches on the {tb.name}.', sp[0], sp[1])


def hostile_host(game, wd):
    kn = getattr(game.player, 'knight', None)
    return bool(kn and kn.get('kid') == wd.foe)


KINDS = {'host'}


def step(game, wd):
    """A host on the march; at the end of its road, the battle for the seat."""
    from .wanderers import wanderer_at, greedy_step
    p = game.player
    if wd.hostile and game.cur == 'over' and wd.cooldown == 0 and cheb(wd.x, wd.y, p.x, p.y) <= 5 and game.visible(wd.x, wd.y):
        greedy_step(game, wd, p.x, p.y)
        return
    if wd.path_i < len(wd.path):
        nx, ny = wd.path[wd.path_i]
        if game.cur == 'over' and (nx, ny) == (p.x, p.y):
            return
        if not wanderer_at(game, nx, ny) or random.random() < .5:
            wd.x, wd.y = nx, ny
            wd.path_i += 1
        return
    arrive(game, wd)


def describe(wd, game):
    if wd.kind != 'host':
        return None
    R = get(game)
    tb = R.baronies.get(wd.target_r)
    return f'{wd.name}, {wd.strength} hundred strong, marching on the {tb.name if tb else "enemy"}' + \
        (', hostile to you.' if wd.hostile else '.')


def arrive(game, wd):
    R = get(game)
    w = game.world
    if wd in w.wanderers:
        w.wanderers.remove(wd)
    war = next((x for x in R.wars if x.get('host') == wd.id), None)
    tb = R.baronies.get(wd.target_r)
    if not war or not tb or tb.kingdom != wd.foe:
        return
    from .living import battle
    if len(wd.path) > 2:
        bx, by = wd.path[-2]
        battle(game, bx, by, f'the hosts of {R.kingdoms[wd.kingdom].short} and {R.kingdoms[wd.foe].short}')
    defend = 9 + R.houses[R.lord(tb.lord).house].wealth * 3 if R.lord(tb.lord) else 9
    att = R.kingdoms[wd.kingdom]
    sign = 1 if war['a'] == att.id else -1
    x, y = seat_pos(w, tb.seat)
    if wd.strength * random.uniform(.7, 1.4) > defend:
        war['score'] += sign
        burn_village(game, tb.rid, att.short)
        if abs(war['score']) >= 2 and random.random() < .6:
            take_barony(game, tb, att)
        else:
            news(game, f'The host of {att.short} beat the men of the {tb.name} in the field and burned what it could.', x, y)
    else:
        war['score'] -= sign
        news(game, f'The {tb.name} held against the host of {att.short}.', x, y)


def burn_village(game, rid, who):
    w = game.world
    from .living import plundered, PLUNDER_DAYS
    cands = [s for s in w.settlements if s.region == rid and s.id != 0 and not s.is_city
             and s.kind in ('hamlet', 'village') and not plundered(game, s)]
    if not cands or random.random() < .5:
        return
    s = random.choice(cands)
    s.plundered = game.day + PLUNDER_DAYS
    s.event = ('war', random.randint(6, 9))
    for g in ('grain', 'ale', 'cloth'):
        s.market[g][0] = min(s.market[g][0], 4)
    news(game, f'{s.name} was plundered by the men of {who}. Half of it burned.', s.x, s.y)


def take_barony(game, tb, att):
    """A barony changes hands: its baron swears to the new king, or is driven out and replaced."""
    R = get(game)
    w = game.world
    old = R.kingdoms[tb.kingdom]
    tb.kingdom = att.id
    lo = R.lord(tb.lord)
    x, y = seat_pos(w, tb.seat)
    if lo and lo.alive and lo.title == 'baron' and random.random() < .5:
        lo.liege = att.king
        lo.loyalty = 30
        news(game, f'The {tb.name} bows to {att.short} now: {style(R, lo, False)} has sworn to {style(R, R.lord(att.king), False)}.',
             x, y, title=f'The {tb.name} goes to {att.short}')
    else:
        if lo and lo.title == 'king':
            new_seat_for(game, old, tb)
        h = new_house(R, w.__dict__.setdefault('fam_used', set()), 'human', 'baronial', 1)
        h.region = tb.rid
        h.seat = tb.seat
        nl = founder(R, h, 'baron', random.randint(25, 55))
        nl.liege = att.king
        if lo:
            for o in R.lords.values():
                if o.liege == lo.id:
                    o.liege = nl.id
            swap_npcs(game, lo, nl)
        tb.lord = nl.id
        news(game, f'The {tb.name} is taken by {att.short}. {style(R, nl, False)} holds it for {style(R, R.lord(att.king), False)}.',
             x, y, title=f'The {tb.name} goes to {att.short}')
    for h in R.houses:
        if h.rank == 'lesser' and h.region == tb.rid and not h.fallen and h.head is not None:
            R.lords[h.head].liege = tb.lord
    if game.player.__dict__.get('knight', {}) and game.player.knight.get('kid') == old.id:
        game.msg(f'The {tb.name} is lost to {att.short}.', 'bad')


def new_seat_for(game, kg, lost):
    """A king who loses his own seat moves to another barony of his."""
    R = get(game)
    rest = [b for b in R.baronies.values() if b.kingdom == kg.id and b.rid != lost.rid and b.seat]
    if rest:
        b = max(rest, key=lambda q: q.seat[0] == 's')
        kg.seat = b.seat


def end_war(game, war):
    R = get(game)
    R.wars.remove(war)
    a, b = R.kingdoms[war['a']], R.kingdoms[war['b']]
    win, lose = (a, b) if war['score'] > 0 else (b, a) if war['score'] < 0 else (None, None)
    x, y = place_of(game, R.lord(a.king))
    if not win:
        text = f'Peace between {a.short} and {b.short}: nothing won, many dead.'
    else:
        how = random.choice(['tribute', 'hostage', 'land'])
        if how == 'land':
            near = [R.baronies[o] for rid in R.baronies if R.baronies[rid].kingdom == win.id
                    for o in R.adj.get(rid, []) if o in R.baronies and R.baronies[o].kingdom == lose.id]
            if near:
                take_barony(game, random.choice(near), win)
                text = f'Peace between {a.short} and {b.short}: {lose.short} gives up a barony.'
            else:
                how = 'tribute'
        if how == 'tribute':
            text = f'Peace between {a.short} and {b.short}: {lose.short} pays tribute to {win.short} for five years.'
            lose.burden += 1
        elif how == 'hostage':
            heir = R.lord(R.lord(lose.king).heir)
            who = f'{heir.first}, the heir of {lose.short},' if heir and heir.alive else 'a royal child'
            text = f'Peace between {a.short} and {b.short}: {who} goes to the court of {win.short} as a hostage.'
    news(game, text, x, y, title=f'The peace of {a.short} and {b.short}')
    for kg in (a, b):
        for st in game.world.settlements:
            if st.region in R.baronies and R.baronies[st.region].kingdom == kg.id and st.event and st.event[0] == 'war':
                st.event = None


def levy(game, kg):
    """The king calls his levy: bread and arms grow dear in his towns."""
    R = get(game)
    w = game.world
    n = 0
    for st in w.settlements:
        if st.region in R.baronies and R.baronies[st.region].kingdom == kg.id and st.id != 0 and not st.event and random.random() < .5:
            st.event = ('war', random.randint(5, 9))
            st.market['arms'][1] = D.EVENTS['war']['target']
            n += 1
    kg.burden += 1
    news(game, f'{style(R, R.lord(kg.king), False)} calls the levy of {kg.short}: every village sends men, and arms and '
               f'bread grow dear.', *place_of(game, R.lord(kg.king)))


def tax(game, kg):
    R = get(game)
    kg.burden += 1
    news(game, f'New taxes in {kg.short}: a tenth of every harvest, and a toll on the bridges.', *place_of(game, R.lord(kg.king)))


def emperor_event(game):
    """The emperor calls his vassals against an outside foe, or the court has its own small news."""
    R = get(game)
    from . import powers as PW
    foe = PW.outside_threat(game)
    em = R.lord(R.emperor)
    x, y = place_of(game, em)
    if foe:
        news(game, f'{style(R, em, False)} calls the kings of the empire to arms against {foe}.', x, y,
             title=f'The call to arms against {foe}')
        for kg in R.kingdoms:
            kg.burden += 1
            summon(game, kg, None)
    elif random.random() < .5:
        news(game, f'{style(R, em, False)} holds a great tourney in {game.world.settlements[R.great].name}. '
                   f'Every lord of the empire rides to it.', x, y)
    elif len(R.wars) and random.random() < .5:
        war = random.choice(R.wars)
        end_war(game, war)


# ------------------------------------------------------------------ the lords where you meet them
def place_lord(game, m, lo, cell, role='lord'):
    from .entities import make_npc
    R = get(game)
    h = R.houses[lo.house]
    npc = make_npc(game, style(R, lo, False), role, '#f0d890', cell[0], cell[1], True, gender=lo.gender)
    npc.lord = lo.id
    npc.fg = h.arms[1]
    m.mons.append(npc)
    return npc


def guards_of(game, m, lo, cells, n=2):
    from .towns import townsfolk
    R = get(game)
    h = R.houses[lo.house]
    for c in cells[:n]:
        g = townsfolk(game, m, [c], c, [f'A guard of House {h.name}'], 'guard', fg=h.arms[2] if sum(h.arms[2]) > 120
                      else h.arms[1], role='guard')
        g.house = h.id


def furnish_town(game, m, s):
    """The baron, king or emperor who sits in this town, in its finest house; the city's library; the merchant
    family's head. The houses they take get a sign of their own."""
    R = get(game)
    plots = sorted(getattr(m, 'homes', ()), key=lambda pl: -(pl.w * pl.h))
    if R is None or not plots:
        return
    from .towns import free_inside, add_sign
    lords = [b.lord for b in R.baronies.values() if b.seat == ('s', s.id)]
    lords += [kg.king for kg in R.kingdoms if kg.seat == ('s', s.id) and kg.king not in lords]
    lords = [R.lord(l) for l in lords if R.lord(l) and R.lord(l).alive]

    def take(name, what):
        while plots:
            pl = plots.pop(0)
            if len(free_inside(m, pl)) < 3:
                continue
            add_sign(m, pl, name)
            b = m.buildings[-1]
            b['name'], b['what'] = name, what
            return b
        return None
    for lo in lords[:1]:
        b = take(f'The House of {R.houses[lo.house].name}', 'hall')
        if not b:
            break
        sp = free_inside(m, b['plot'])
        place_lord(game, m, lo, sp[0])
        guards_of(game, m, lo, sp[1:])
    if s.is_city:
        b = take(f'The Library of {s.name}', 'library')
        if b:
            from . import history as HI
            HI.library(game, m, s, b)
    for h in R.houses:
        if h.rank == 'merchant' and h.seat == ('s', s.id) and not h.fallen:
            lo = R.lord(h.head)
            if not lo or not lo.alive:
                continue
            b = take(f'The House of {h.name}', 'merchant house')
            if b:
                sp = free_inside(m, b['plot'])
                place_lord(game, m, lo, sp[0], 'merchant_lord')


def furnish_hold(game, m, hd):
    """The baron (or king) who sits in this castle, in the keep."""
    R = get(game)
    if R is None:
        return
    lo = next((R.lord(b.lord) for b in R.baronies.values() if b.seat == ('hold', hd.id)), None)
    lo = lo or next((R.lord(kg.king) for kg in R.kingdoms if kg.seat == ('hold', hd.id)), None)
    if not lo or not lo.alive:
        return
    cells = [(x, y) for y in range(m.h) for x in range(m.w) if m.tile(x, y) in (D.FLOOR, D.PLANK) and not m.mon_at(x, y)]
    cast = next((o for o in m.mons if getattr(o, 'role', '') == 'castellan'), None)
    if cast:
        cells.sort(key=lambda c: cheb(c[0], c[1], cast.x, cast.y))
        cells = cells[2:]
    if cells:
        place_lord(game, m, lo, cells[0])


# ------------------------------------------------------------------ talking to a lord
ROLES = {'lord', 'heir', 'merchant_lord'}


def talk(game, npc):
    """Lords, heirs and merchant heads. True when this module answered."""
    role = getattr(npc, 'role', '')
    if role not in ROLES:
        from . import powers as PW
        from . import history as HI
        return PW.talk(game, npc) or HI.talk(game, npc)
    R = get(game)
    lo = R.lord(getattr(npc, 'lord', None))
    if lo and not lo.alive:
        h = R.houses[lo.house]
        nl = R.lord(h.head)
        if nl and nl.alive:
            npc.lord, npc.name, lo = nl.id, style(R, nl, False), nl
    if not lo:
        game.say(npc, 'Not now.')
        return True
    if not lo.met:
        lord_seen(game, lo)
    from . import realmjobs as RJ
    if RJ.turn_in(game, lo, npc):
        return True
    from . import events as EV
    h = R.houses[lo.house]
    opts = [('Is there work for me?', 'work'), ('What news of the realm?', 'news')]
    p = game.player
    kn = getattr(p, 'knight', None)
    if lo.title in ('baron', 'king', 'emperor') and npc.role == 'lord':
        if kn and kn['lid'] == lo.id:
            opts.append(('Renounce your oath', 'renounce'))
        elif not kn:
            opts.append(('Swear fealty to this lord', 'fealty'))
    opts.append(('Goodbye', 'bye'))
    EV.ask(game, 'lord', style(R, lo, False), f'{greeting(game, lo)}\n\n{describe_lord(R, lo)} The arms of House {h.name}: '
           f'{arms_words(h.arms)}. "{h.motto}."', opts, lid=lo.id, npc=npc.id)
    return True


def greeting(game, lo):
    p = game.player
    kn = getattr(p, 'knight', None)
    if kn and kn['lid'] == lo.id:
        return f'"Sir {p.name}." {style(get(game), lo, False)} nods to you as to one of {lo.his} own.' if p.gender != 'female' \
            else f'"Dame {p.name}." {style(get(game), lo, False)} nods to you as to one of {lo.his} own.'
    if 'greedy' in lo.traits:
        return '"Speak, and be quick. My time costs more than yours."'
    if 'pious' in lo.traits:
        return '"The gods keep you, traveller. What brings you to my hall?"'
    if 'ambitious' in lo.traits:
        return '"A sword for hire? I may have use for one. These are uncertain times."'
    if 'craven' in lo.traits:
        return f'{lo.he.capitalize()} looks past you, to the door, before {lo.he} speaks. "Yes? What is it?"'
    if 'brave' in lo.traits:
        return '"Well met. You have the look of someone who has seen a fight or two."'
    return '"You are welcome under my roof. What do you want of me?"'


def r_lord(game, choice, ctx):
    R = get(game)
    lo = R.lord(ctx.get('lid'))
    npc = next((o for o in game.map.mons if o.id == ctx.get('npc')), None)
    if not lo or not npc:
        return
    if choice == 'work':
        from . import realmjobs as RJ
        RJ.offer(game, npc, lo)
    elif choice == 'news':
        game.say(npc, court_news(game, lo))
    elif choice == 'fealty':
        fealty(game, npc, lo)
    elif choice == 'renounce':
        renounce(game, lo)


def court_news(game, lo):
    """What a lord tells of his own kingdom: true, and fresh. It goes into the chronicle as heard."""
    from . import chronicle as CH
    R = get(game)
    kg = next((k for k in R.kingdoms if k.king == lo.id), None) or kingdom_of_lord(R, lo)
    if not kg:
        return '"I keep out of the affairs of kings."'
    lines = []
    for war in R.wars:
        if kg.id in (war['a'], war['b']):
            other = R.kingdoms[war['b'] if war['a'] == kg.id else war['a']]
            lines.append(f'We are at war with {other.short}, over {war["cause"]}.')
    if kg.civil:
        c = R.lord(kg.civil['claimant'])
        lines.append(f'{style(R, c, False)} claims the crown; the lords are divided.')
    if kg.rebel:
        rb = R.lord(kg.rebel['baron'])
        lines.append(f'{style(R, rb, False)} is in revolt.')
    king = R.lord(kg.king)
    if not lines:
        lines.append(f'{style(R, king, False)} keeps the peace in {kg.short}, for now.')
    text = ' '.join(lines)
    CH.add(game, 'The Realms', f'{kg.name}: {text}', 'heard', style(R, lo, False), key=f'court:{kg.id}:{game.day // 30}',
           place=place_of(game, king), quiet=True)
    return f'"{text}"'


def kingdom_of_lord(R, lo):
    seen = set()
    while lo and lo.id not in seen:
        seen.add(lo.id)
        for kg in R.kingdoms:
            if kg.king == lo.id:
                return kg
        lo = R.lord(lo.liege)
    return None


# ------------------------------------------------------------------ fealty and knighthood
FEALTY_REP = 10          # Friendly with the empire
FEALTY_FAVOUR = 12       # done enough for this kingdom's lords


def favour(game, kid):
    return game.player.__dict__.setdefault('favour', {}).get(kid, 0)


def add_favour(game, kid, n):
    if kid is None:
        return
    fv = game.player.__dict__.setdefault('favour', {})
    fv[kid] = max(-50, min(100, fv.get(kid, 0) + n))


def fealty(game, npc, lo):
    R = get(game)
    p = game.player
    kg = kingdom_of_lord(R, lo)
    if not kg:
        return
    if p.rep.get('crown', 0) < FEALTY_REP or favour(game, kg.id) < FEALTY_FAVOUR:
        game.say(npc, f'"Swear to me? I do not know you. Serve the lords of {kg.short} first, and let your name go before you."')
        return
    word = 'Dame' if p.gender == 'female' else 'Sir' if p.gender == 'male' else 'Ser'
    p.knight = dict(lid=lo.id, kid=kg.id, day=game.day, word=word, calls=0)
    from .war import change_rep
    change_rep(game, 'crown', 5)
    game.msg(f'You kneel, and {style(R, lo, False)} lays a sword on your shoulder. You are {word} {p.name} now, '
             f'a knight of {kg.short}.', 'unique')
    from . import chronicle as CH
    CH.deed(game, f'Knighted by {lo.first} {R.houses[lo.house].name}', f'You swore fealty to {style(R, lo, False)} and '
            f'became a knight of {kg.short}.')
    from . import guide as GDE
    GDE.tip(game, 'knight')


def renounce(game, lo):
    R = get(game)
    p = game.player
    kn = getattr(p, 'knight', None)
    if not kn:
        return
    add_favour(game, kn['kid'], -30)
    from .war import change_rep
    change_rep(game, 'crown', -8)
    p.knight = None
    game.msg(f'You give back your oath to {style(R, lo, False)}. You are no one\'s knight now.', 'bad')


def knight_word(game):
    kn = getattr(game.player, 'knight', None)
    return kn['word'] if kn else None


def register():
    from . import events as EV
    EV.RESOLVERS['lord'] = r_lord


register()
