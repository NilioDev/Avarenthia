"""The powers outside the empire and beside it, each with its own engine.

Dwarves keep a grudge book in every hold: a full book is a feud that ends only when the debt is paid. Elves defend
their wood: the empire's woodcutters push the forest's edge back (clear-cuts on the world map), and too far, the wood
is closed. Orc tribes with made names fight each other; a chief strong enough unites them into the Gorvash ("all
spears") and marches out of the badlands, until the warlord dies and it splits again.

Two or three raiding peoples per world, only where their land is: northern sea raiders, highland or steppe clans,
desert riders, ice raiders, pass clans, wreckers, canyon riders, the mist folk, island voyagers. Each has a hall
with a chief (guest right holds under his roof), raids in its season, and a strong one can take a barony.

Beside them: the Church and its holy order, the Border Watch on the northern forts (only with a raiding people in
the north), mercenary companies (when there is war), peasant revolts (when taxes, levies and hunger are heavy), an
exiled pretender (when someone loses a succession war) and witch circles on the moors and marshes.
Everything here lives in world.powers."""
import heapq
import random

from . import data as D
from .worldgen import cheb


def P(world):
    return world.powers


def raiders(world):
    return world.powers['raiders']


# ------------------------------------------------------------------ the raiding peoples
KINDS = {
    'sea': dict(label='sea raiders', title='Jarl', female='Jarl', hall='mead hall', months=(2, 3, 4, 5, 6, 7),
                troops=['sea_raider', 'sea_raider', 'berserker'], fg=(150, 190, 230), people=['Fjordmen', 'Skerrymen', 'Wavecarls'],
                land=(['Skar', 'Hrim', 'Vald', 'Ulf', 'Brim', 'Grim', 'Hroth', 'Kvel', 'Sval'], ['svik', 'fjord', 'heim', 'nes', 'holm', 'vik']),
                chief=(['Ulf', 'Bjar', 'Sig', 'Hrolf', 'Ketil', 'Thor', 'Asa', 'Gud', 'Ing', 'Rag'], ['rik', 'mund', 'vald', 'grim', 'run', 'dis', 'ny', 'nar'])),
    'barbarian': dict(label='clans', title='Chieftain', female='Chieftain', hall='clan hall', months=(0, 1, 11),
                      troops=['clan_warrior', 'clan_warrior', 'clan_rider'], fg=(170, 190, 110), people=['Clans'],
                      land=(['Craig', 'Ben', 'Glen', 'Strath', 'Dun', 'Kil'], ['morach', 'vorrin', 'gaul', 'dair', 'loch', 'brae']),
                      chief=(['Cal', 'Fer', 'Dun', 'Mor', 'Bri', 'Ais', 'Eo', 'Fin'], ['gus', 'chad', 'gal', 'nach', 'da', 'ra', 'lin'])),
    'desert': dict(label='desert riders', title='Rider-King', female='Rider-Queen', hall='great tent', months=(5, 6, 7),
                   troops=['dune_rider', 'dune_rider', 'dune_archer'], fg=(230, 200, 130), people=['Riders'],
                   land=(['Al', 'Zah', 'Qar', 'Sab', 'Ras', 'Mir', 'Tam'], ['ahar', 'imar', 'oud', 'esh', 'azir', 'ira'])),
    'ice': dict(label='ice raiders', title='Sledge-Lord', female='Sledge-Mother', hall='winter lodge', months=(11, 0, 1),
                troops=['ice_raider', 'ice_raider', 'sledge_hunter'], fg=(200, 220, 240), people=['Sledge-folk'],
                land=(['Iss', 'Kaa', 'Nuu', 'Tik', 'Ulu', 'Aar', 'Sen'], ['vik', 'luk', 'tuk', 'miut', 'aq', 'mak'])),
    'pass': dict(label='pass clans', title='Clan-Father', female='Clan-Mother', hall='stone hall', months=(),
                 troops=['pass_clansman', 'pass_clansman', 'pass_slinger'], fg=(190, 170, 150), people=['Pass Clans'],
                 land=(['Hoch', 'Grat', 'Alp', 'Firn', 'Stein', 'Joch'], ['wald', 'horn', 'egg', 'tal', 'berg', 'fels'])),
    'wreckers': dict(label='wreckers', title='Headman', female='Headwoman', hall='wreckers\' hall', months=(8, 9, 10),
                     troops=['wrecker', 'wrecker', 'wrecker'], fg=(140, 160, 140), people=['Wreckers'],
                     land=(['Black', 'Grim', 'Cold', 'Gull', 'Rook', 'Crab'], ['cove', 'mouth', 'rocks', 'strand', 'scar'])),
    'canyon': dict(label='canyon riders', title='Cliff-Lord', female='Cliff-Lady', hall='cliff village', months=(4, 5, 6, 7),
                   troops=['canyon_rider', 'canyon_rider', 'canyon_archer'], fg=(220, 140, 100), people=['Cliff Riders'],
                   land=(['Red', 'Sand', 'Hawk', 'Wind', 'Dust', 'Ochre'], ['rock', 'mesa', 'wall', 'gorge', 'spire'])),
    'mist': dict(label='mist folk', title='Mist-Father', female='Mist-Mother', hall='reed hall', months=(2, 3, 8, 9),
                 troops=['mist_stalker', 'mist_stalker', 'mist_stalker'], fg=(170, 180, 190), people=['Mist Folk'],
                 land=(['Fen', 'Dim', 'Grey', 'Whist', 'Murk', 'Sedge'], ['mere', 'mire', 'holm', 'water', 'reach'])),
    'island': dict(label='island voyagers', title='Navigator', female='Navigator', hall='canoe house', months=(),
                   troops=['reef_warrior', 'reef_warrior', 'reef_spear'], fg=(110, 210, 190), people=['Voyagers'],
                   land=(['Mo', 'Ta', 'Ka', 'Ra', 'Lu', 'Te'], ['nui', 'vaka', 'roa', 'hiti', 'mana', 'tua'])),
}
CHIEF_DEFAULT = (['Ar', 'Bel', 'Cas', 'Dar', 'Ess', 'Har', 'Ka', 'Tor', 'Zan', 'Ish'], ['ak', 'ir', 'an', 'oth', 'una', 'ek', 'al'])
COLD = {'tundra', 'taiga', 'conifer', 'shrubland_cold', 'tundra_hills', 'birch', 'alpine', 'glacier'}


def hall_fits(m, world, kind, x, y):
    """Can this people's hall stand here? Returns a score, or 0."""
    names = m.biome_names
    b = names[m.biome[y * m.w + x]]

    def near(bs, r=2):
        return sum(1 for dy in range(-r, r + 1) for dx in range(-r, r + 1)
                   if m.inb(x + dx, y + dy) and names[m.biome[(y + dy) * m.w + x + dx]] in bs)

    def sea(r=1):
        return any(m.inb(x + dx, y + dy) and m.tile(x + dx, y + dy) == D.WATER and names[m.biome[(y + dy) * m.w + x + dx]]
                   not in ('lake', 'crater_lake', 'oasis', 'hotpool') for dx in range(-r, r + 1) for dy in range(-r, r + 1))
    if kind == 'sea':
        if y > m.h * .45 or not sea():
            return 0
        return 1 + near(COLD, 2) / 6 + 2 * near(('fjord',), 2) if near(COLD, 3) >= 4 or near(('fjord',), 2) else 0
    if kind == 'barbarian':
        return 1 if b in ('alpine', 'tundra_hills', 'hills', 'steppe') and near(('alpine', 'tundra_hills', 'hills', 'steppe')) >= 14 else 0
    if kind == 'desert':
        return 1 + near(('oasis',), 3) if b in ('desert', 'dune', 'salt_edge') and near(('desert', 'dune', 'dune_crest')) >= 12 else 0
    if kind == 'ice':
        return 1 if b in ('tundra', 'taiga', 'tundra_hills') and near(('tundra', 'taiga', 'tundra_hills', 'glacier')) >= 16 else 0
    if kind == 'pass':
        return 1 if b == 'alpine' and any(m.inb(x + dx, y + dy) and m.tile(x + dx, y + dy) == D.MOUNTAIN
                                          for dx in (-1, 0, 1) for dy in (-1, 0, 1)) else 0
    if kind == 'wreckers':
        return 1 + near(('moor', 'cliff'), 2) / 4 if b in ('moor', 'cliff', 'shrubland', 'beach', 'meadow') and sea() and near(('moor', 'cliff'), 3) >= 3 else 0
    if kind == 'canyon':
        return 1 if b in ('canyon', 'badlands') and near(('canyon', 'mesa'), 3) >= 5 else 0
    if kind == 'mist':
        return 1 if b in ('moor', 'marsh') and near(('moor', 'marsh'), 2) >= 14 else 0
    if kind == 'island':
        return 1 if b in ('atoll_palm', 'cay', 'beach') and near(('lagoon', 'reef', 'reef_flat', 'atoll_palm', 'cay', 'lagoon_deep'), 3) >= 6 else 0
    return 0


def made(parts):
    a, b = parts
    nm = random.choice(a) + random.choice(b)
    return nm[0].upper() + nm[1:]


def place_raiders(game, m, world, R, taken):
    from .sites import Site
    w = m.w
    start = world.settlements[0]
    cells = [i for i in range(w * m.h) if 3 <= i % w < w - 3 and 3 <= i // w < m.h - 3 and D.TILES[m.t[i]].walk
             and m.t[i] not in (D.ROAD, D.TOWN, D.CITY, D.RIVER, D.ENTR, D.CASTLE, D.FORT) and i not in world.wonder_cells]
    random.shuffle(cells)
    found = {}
    for k in KINDS:
        best = None
        for i in cells[:9000]:
            x, y = i % w, i // w
            if cheb(x, y, start.x, start.y) < 40 or any(cheb(x, y, a, b) < 7 for a, b in taken):
                continue
            sc = hall_fits(m, world, k, x, y)
            if sc and (best is None or sc > best[0]):
                best = (sc, x, y)
                if sc > 2.5:
                    break
        if best:
            found[k] = best[1:]
    kinds = list(found)
    random.shuffle(kinds)
    kinds.sort(key=lambda k: k not in ('sea', 'barbarian', 'desert'))       # the great raiders first
    n = random.choice([2, 3, 3]) if len(kinds) >= 3 else len(kinds)
    out = []
    for k in kinds[:n]:
        x, y = found[k]
        t = KINDS[k]
        land = made(t['land'])
        people = random.choice(t['people'])
        if k == 'barbarian' and m.biome_names[m.biome[y * w + x]] == 'steppe':
            people = 'Horse-Clans'
        name = f'The {people} of {land}'
        g = random.choice(['male', 'male', 'female'])
        chief = made(t.get('chief', CHIEF_DEFAULT))
        st = Site(len(world.sites), 'hall', x, y, f'{land}, the {t["hall"]} of the {people}')
        st.faction = None
        st.raider = len(out)
        world.sites.append(st)
        taken.append((x, y))
        rd = dict(kind=k, people=people, land=land, name=name, fg=t['fg'], chief=chief, chief_g=g, site=st.id, x=x, y=y,
                  strength=random.randint(3, 6), raids=0, held=[], vassal=False, angry=0, warned={})
        out.append(rd)
        homeland(m, world, R, len(out) - 1, x, y)
    return out


def homeland(m, world, R, idx, x, y, cap=150):
    """The land a raiding people calls its own: grown from the hall, small."""
    w = m.w
    dist = {y * w + x: 0}
    heap = [(0, y * w + x)]
    while heap:
        d, i = heapq.heappop(heap)
        if d > dist.get(i, 1 << 30):
            continue
        R.raid_cells[i] = idx
        cx = i % w
        for j in (i - 1 if cx > 0 else -1, i + 1 if cx < w - 1 else -1, i - w, i + w):
            if j < 0 or j >= len(m.t) or m.t[j] == D.WATER or not D.TILES[m.t[j]].walk and m.t[j] != D.MOUNTAIN:
                continue
            nd = d + (30 if m.t[j] == D.MOUNTAIN else 10) + (j * 7) % 4
            if nd <= cap and nd < dist.get(j, 1 << 30) and world.regions[world.region_of[j]].faction != 'crown':
                dist[j] = nd
                heapq.heappush(heap, (nd, j))


def chief_style(rd):
    t = KINDS[rd['kind']]
    return f'{t["female"] if rd["chief_g"] == "female" else t["title"]} {rd["chief"]}'


# ------------------------------------------------------------------ making the powers
ORDER_NAMES = ['The Order of the Silver Flame', 'The Order of the White Hart', 'The Order of the Iron Lantern',
               'The Order of the Dawn Blade', 'The Knights of the Pale Rose', 'The Order of Saint Corwen']
WATCH_NAMES = ['The Border Watch', 'The Watch of the North', 'The Grey Watch', 'The Wall-Wardens']
COMPANY_A = ['Iron', 'Red', 'Black', 'Free', 'Golden', 'Silver', 'Grey', 'Bloody', 'Laughing', 'Broken']
COMPANY_B = ['Company', 'Lances', 'Banners', 'Shields', 'Blades', 'Hounds', 'Band', 'Spears']


def generate(game, m, world, R):
    from .sites import Site
    from .races import random_name
    world.powers = PW = dict(grudges={}, forest=dict(edge=random.randint(5, 25), cuts=[], closed=False), tribes=[],
                             gorvash=None, raiders=[], church={}, watch=None, companies=[], revolt=None,
                             pretender=None, circles=[], notes=[], gallows=[])
    world.clearcut = set()
    taken = [(s.x, s.y) for s in world.settlements] + [(h.x, h.y) for h in world.holds] + \
            [(d.x, d.y) for d in world.dungeons.values()] + [(q.x, q.y) for q in world.sites]
    # dwarves: a grudge book in every hold
    for s in world.settlements:
        if s.kind == 'deephold':
            PW['grudges'][s.id] = []
            for _ in range(random.randint(1, 3)):
                grudge(game, s.id, quiet=True, world=world, day=-random.randint(30, 3000))
    # orc tribes
    camps = [st for st in world.sites if st.kind in ('warcamp', 'ravine')]
    horde = [r for r in world.regions if r.faction == 'horde']
    homes = [(st.x, st.y, st.id) for st in camps] + [(r.cx, r.cy, None) for r in horde]
    from . import names as NM
    used = set()
    for x, y, sid in homes[:5] or []:
        for _ in range(20):
            nm = f'The {random.choice(NM.ORC_ADJ)} {random.choice(NM.ORC_N)}'
            if nm not in used:
                break
        used.add(nm)
        g = random.choice(['male', 'male', 'female'])
        PW['tribes'].append(dict(name=nm, chief=random_name('orc', g), chief_g=g, strength=random.randint(2, 6), x=x, y=y,
                                 site=sid))
        if sid is not None:
            world.sites[sid].tribe = len(PW['tribes']) - 1
    # the raiding peoples
    PW['raiders'] = place_raiders(game, m, world, R, taken)
    # the Church and its holy order
    em_city = world.settlements[R.great]
    g = random.choice(['male', 'female'])
    PW['church'] = dict(priest=random_name('human', g), priest_g=g, seat=em_city.id, bans=[], order=None)
    keep = free_site(m, world, taken, lambda x, y: world.regions[world.region_of[y * m.w + x]].faction == 'crown'
                     and m.tile(x, y) in (D.HILLS, D.GRASS) and 2 <= world.road_dist[y * m.w + x] <= 6)
    if keep:
        name = random.choice(ORDER_NAMES)
        st = Site(len(world.sites), 'orderkeep', keep[0], keep[1], f'The Keep of {name.replace("The ", "the ")}')
        st.faction = 'crown'
        world.sites.append(st)
        taken.append(keep)
        g = random.choice(['male', 'female'])
        PW['church']['order'] = dict(name=name, site=st.id, prior=random_name('human', g), prior_g=g, strength=8)
    # witch circles on the moors and in the marshes
    names = m.biome_names
    wet = {'moor', 'marsh', 'swamp'}
    for _ in range(random.randint(1, 3)):
        c = free_site(m, world, taken, lambda x, y: names[m.biome[y * m.w + x]] in wet and world.road_dist[y * m.w + x] >= 4)
        if not c:
            break
        g = 'female' if random.random() < .8 else 'male'
        st = Site(len(world.sites), 'circle', c[0], c[1], f'{random.choice(["Hag", "Crow", "Raven", "Old", "Thorn", "Mother"])}'
                                                          f'{random.choice(["stone", "mere", "hollow", "ring", "moss"])} Circle')
        st.hidden, st.found = True, False
        st.witch = random_name('human', g, family=False)
        st.witch_g = g
        world.sites.append(st)
        taken.append(c)
        PW['circles'].append(st.id)
    # the Border Watch: only with a raiding people in the north
    north = [rd for rd in PW['raiders'] if rd['kind'] in ('sea', 'barbarian', 'ice') or rd['y'] < m.h * .4]
    if north:
        make_watch(game, m, world, R, taken)


def free_site(m, world, taken, pred, tries=4000):
    w = m.w
    for _ in range(tries):
        x, y = random.randint(4, w - 5), random.randint(4, m.h - 5)
        i = y * w + x
        t = m.t[i]
        if not D.TILES[t].walk or t in (D.ROAD, D.TOWN, D.CITY, D.RIVER, D.ENTR, D.CASTLE, D.FORT) or i in world.wonder_cells:
            continue
        if any(cheb(x, y, a, b) < 6 for a, b in taken):
            continue
        if pred(x, y):
            return x, y
    return None


def make_watch(game, m, world, R, taken):
    """A line of forts along the northern edge of the empire."""
    from .sites import Site
    from .races import random_name
    w = m.w
    cr = [i for i in range(len(m.t)) if world.regions[world.region_of[i]].faction == 'crown' and D.TILES[m.t[i]].walk
          and m.t[i] not in (D.ROAD, D.TOWN, D.CITY, D.RIVER, D.ENTR, D.CASTLE, D.FORT)]
    if not cr:
        return
    xs = [i % w for i in cr]
    lo, hi = min(xs), max(xs)
    forts = []
    for k in range(3):
        band = [i for i in cr if lo + (hi - lo) * k / 3 <= i % w < lo + (hi - lo) * (k + 1) / 3]
        if not band:
            continue
        band.sort(key=lambda i: i // w)
        for i in band[:400]:
            x, y = i % w, i // w
            if any(cheb(x, y, a, b) < 6 for a, b in taken) or y < 4:
                continue
            forts.append((x, y))
            taken.append((x, y))
            break
    if not forts:
        return
    name = random.choice(WATCH_NAMES)
    ids = []
    for k, (x, y) in enumerate(forts):
        st = Site(len(world.sites), 'watchfort', x, y, f'{["Greywall", "Coldgate", "Watchmoor", "Northhold", "Wolfspike"][k % 5]} '
                                                         f'Fort of {name.replace("The ", "the ")}')
        st.faction = 'crown'
        world.sites.append(st)
        ids.append(st.id)
    g = random.choice(['male', 'female'])
    world.powers['watch'] = dict(name=name, forts=ids, strength=10, commander=random_name('human', g), commander_g=g)


def grudge(game, sid, against=None, what=None, quiet=False, world=None, day=None):
    """A new wrong in a dwarf hold's book."""
    world = world or game.world
    book = world.powers['grudges'].setdefault(sid, [])
    R = world.realm
    if against is None:
        opts = [('k', random.randrange(len(R.kingdoms)))] * 3 + [('elves',), ('tribes',)]
        against = random.choice(opts)
    if what is None:
        if against[0] == 'k':
            kg = R.kingdoms[against[1]]
            what = random.choice([f'iron sold to {kg.short} and never paid for', f'a dwarf hanged in {kg.short} for a theft he did not do',
                                  f'a pact with {kg.short} broken: the road toll taken twice', f'a mine claimed by a baron of {kg.short}'])
        elif against[0] == 'elves':
            what = random.choice(['a dwarf shot in the elven wood for cutting a tree', 'an heirloom axe kept by the elves',
                                  'an insult by an elven envoy at the gate'])
        else:
            what = random.choice(['a caravan of the hold burnt by orcs', 'three miners slain by goblins in the deep roads',
                                  'the old north gate taken by the tribes'])
    gid = len(book) + 1
    book.append(dict(id=gid, against=tuple(against), what=what, day=day if day is not None else game.day, weight=random.randint(1, 3),
                     settled=False))
    if not quiet and game is not None:
        s = world.settlements[sid]
        from . import realms as RL
        RL.news(game, f'A new grudge in the book of {s.name}: {what}.', s.x, s.y, 'Peoples')
    return book[-1]


def book_weight(world, sid):
    return sum(g['weight'] for g in world.powers['grudges'].get(sid, ()) if not g['settled'])


def settle(game, sid, gid, how):
    world = game.world
    g = next((g for g in world.powers['grudges'].get(sid, ()) if g['id'] == gid), None)
    if not g or g['settled']:
        return
    g['settled'] = how
    s = world.settlements[sid]
    from . import realms as RL
    RL.news(game, f'A grudge struck from the book of {s.name}: {g["what"]}, {how}.', s.x, s.y, 'Peoples')


# ------------------------------------------------------------------ the year
def note(game, kind, data):
    """Something one engine tells the others: a wedding to come, a war begun."""
    PW = P(game.world)
    if kind == 'wedding':
        PW['notes'].append(dict(kind='wedding', **data))
    elif kind == 'war':
        company(game, data)


def daily(game):
    PW = P(game.world)
    from . import rift as RF
    RF.daily(game)
    for n in list(PW['notes']):
        if n['kind'] == 'wedding' and game.day >= n['day']:
            PW['notes'].remove(n)
            R = game.world.realm
            a, b = (R.houses[h] for h in n['houses'])
            from . import realms as RL
            lo = R.lord(n['lid'])
            x, y = RL.place_of(game, lo) if lo else (0, 0)
            RL.news(game, f'House {a.name} and House {b.name} were joined in marriage, with a feast for three days.', x, y,
                    'Lords and houses')


def monthly(game):
    w = game.world
    PW = P(w)
    from . import calendar as CAL
    mo = ((CAL.START + game.day - 1) // CAL.DAYS_IN_MONTH) % 12
    dwarves_month(game)
    forest_month(game)
    tribes_month(game)
    for idx, rd in enumerate(PW['raiders']):
        raider_month(game, idx, rd, mo)
    church_month(game)
    watch_month(game)
    companies_month(game)
    revolt_month(game)
    pretender_month(game)
    from . import rift as RF
    RF.monthly(game)


def dwarves_month(game):
    w = game.world
    R = w.realm
    from . import realms as RL
    for sid, book in w.powers['grudges'].items():
        s = w.settlements[sid]
        if random.random() < .12:
            grudge(game, sid)
        open_ = [g for g in book if not g['settled']]
        if open_ and random.random() < .08:
            g = random.choice(open_)
            settle(game, sid, g['id'], random.choice(['paid in gold', 'paid in blood']))
        wt = book_weight(w, sid)
        feud = s.__dict__.get('feud')
        if wt >= 6 and not feud:
            g = max(open_, key=lambda q: q['weight'])
            s.feud = g['against']
            who = RL.realm_info(w, g['against'])[0] if g['against'][0] == 'k' else 'the elves' if g['against'][0] == 'elves' else 'the tribes'
            RL.news(game, f'The book of {s.name} is full. The dwarves will trade no iron with {who} and send their '
                          f'axes instead, until the debt is paid.', s.x, s.y, 'Peoples', title=f'The feud of {s.name}')
        elif feud and wt < 4:
            s.feud = None
            RL.news(game, f'The dwarves of {s.name} have closed their book on their feud. The gates open to trade again.',
                    s.x, s.y, 'Peoples')
        elif feud and feud[0] == 'k' and random.random() < .5:
            kg = R.kingdoms[feud[1]]
            for st in w.settlements:
                if st.region in R.baronies and R.baronies[st.region].kingdom == kg.id and 'tools' in st.market and random.random() < .3:
                    st.market['tools'][1] = max(st.market['tools'][1] - 6, 2)


def forest_month(game):
    """The woodcutters of the empire eat into the elves' wood."""
    w = game.world
    PW = P(w)
    fo = PW['forest']
    om = game.maps['over']
    R = w.realm
    from . import realms as RL
    wood = [r.id for r in w.regions if r.faction == 'circle']
    if not wood:
        return
    fo['edge'] = min(100, fo['edge'] + random.randint(1, 6))
    n = random.randint(4, 12) if fo['edge'] < 90 else 0
    cells = edge_cells(om, w, set(wood))
    random.shuffle(cells)
    cut = 0
    for i in cells[:n]:
        om.t[i] = D.GRASS
        if not hasattr(om, 'over') or om.over is None:
            om.over = {}
        om.over[i] = (',', (150, 110, 60), None)
        w.clearcut.add(i)
        fo['cuts'].append(i)
        cut += 1
    if cut and random.random() < .4:
        i = cells[0]
        RL.news(game, f'Woodcutters from the empire are felling the edge of the elven wood near {w.regions[w.region_of[i]].name}.',
                i % om.w, i // om.w, 'Peoples')
    if fo['edge'] >= 60 and not fo['closed']:
        fo['closed'] = True
        r = w.regions[wood[0]]
        RL.news(game, 'The elves have closed their wood. Woodcutters are found with arrows in their backs, and no '
                      'traveller is safe under the trees.', r.cx, r.cy, 'Peoples', title='The closing of the wood')
    elif fo['closed'] and fo['edge'] < 40:
        fo['closed'] = False
        r = w.regions[wood[0]]
        RL.news(game, 'The elves have opened their wood again, for now.', r.cx, r.cy, 'Peoples')


def edge_cells(om, w, wood):
    """Forest cells of the elven regions that touch imperial land."""
    out = []
    rof = w.region_of
    for i in range(om.w, len(om.t) - om.w):
        if om.t[i] != D.FOREST or rof[i] not in wood:
            continue
        for j in (i - 1, i + 1, i - om.w, i + om.w):
            if (w.regions[rof[j]].faction == 'crown' and om.t[j] != D.WATER) or j in w.clearcut:
                out.append(i)
                break
    return out


def wood_closed(world):
    return world.powers['forest']['closed']


# ------------------------------------------------------------------ the orc tribes and the Gorvash
def tribes_name(world):
    gv = world.powers.get('gorvash') if hasattr(world, 'powers') else None
    if gv:
        return f'The Gorvash of {gv["chief"]}'
    return D.FACTIONS.get('horde', {}).get('name', 'The Orc Tribes')


def tribes_month(game):
    w = game.world
    PW = P(w)
    tr = PW['tribes']
    from . import realms as RL
    gv = PW['gorvash']
    if gv:
        if game.day - gv['since'] > gv['lasts'] or random.random() < .06:
            end_gorvash(game, random.choice(['fell in battle', 'was poisoned by a rival', 'choked on a bone at a feast']))
            return
        from . import war as WAR
        if 'horde' in D.FACTIONS and random.random() < .6:
            WAR.launch(game, 'horde')
        return
    if len(tr) >= 2 and random.random() < .5:
        a, b = random.sample(range(len(tr)), 2)
        A, B = tr[a], tr[b]
        win, lose = (A, B) if A['strength'] * random.uniform(.6, 1.4) >= B['strength'] * random.uniform(.6, 1.4) else (B, A)
        win['strength'] += 1
        lose['strength'] = max(1, lose['strength'] - 1)
        RL.news(game, f'{win["name"]} beat {lose["name"].replace("The ", "the ")} in the badlands. {win["chief"]} grows stronger.',
                win['x'], win['y'], 'Peoples')
    for t in tr:
        if t['strength'] >= 10 and 'horde' in D.FACTIONS:
            gorvash(game, t)
            break


def gorvash(game, t):
    w = game.world
    PW = P(w)
    PW['gorvash'] = dict(chief=t['chief'], chief_g=t['chief_g'], tribe=t['name'], since=game.day, lasts=random.randint(120, 240))
    f = D.FACTIONS['horde']
    f['old_name'], f['old_short'] = f['name'], f['short']
    f['name'], f['short'] = f'The Gorvash of {t["chief"]}', 'Gorvash'
    w.factions['horde'].update(name=f['name'], short='Gorvash')
    from . import realms as RL
    RL.news(game, f'The Gorvash of {t["chief"]} marches! All the tribes follow {t["name"].replace("The ", "the ")} out of '
                  f'the badlands.', t['x'], t['y'], 'The Realms', title=f'The Gorvash of {t["chief"]}')
    from . import war as WAR
    for _ in range(2):
        WAR.launch(game, 'horde')


def end_gorvash(game, how):
    w = game.world
    PW = P(w)
    gv = PW['gorvash']
    if not gv:
        return
    PW['gorvash'] = None
    f = D.FACTIONS['horde']
    f['name'], f['short'] = f.get('old_name', 'The Orc Tribes'), f.get('old_short', 'Tribes')
    w.factions['horde'].update(name=f['name'], short=f['short'])
    for t in PW['tribes']:
        t['strength'] = random.randint(2, 5)
        if t['chief'] == gv['chief']:
            from .races import random_name
            t['chief_g'] = random.choice(['male', 'female'])
            t['chief'] = random_name('orc', t['chief_g'])
    t = next((t for t in PW['tribes'] if t['name'] == gv['tribe']), PW['tribes'][0] if PW['tribes'] else dict(x=0, y=0))
    from . import realms as RL
    RL.news(game, f'{gv["chief"]}, warlord of the Gorvash, {how}. The tribes fall to feuding among themselves again.',
            t['x'], t['y'], 'The Realms', title=f'The end of the Gorvash of {gv["chief"]}')


def distrusted(game):
    """During a march of the Gorvash, half-orcs and goblins are not trusted in the cities."""
    return bool(P(game.world).get('gorvash')) and game.player.race in ('orc', 'goblin')


# ------------------------------------------------------------------ the raiders' year
def raider_month(game, idx, rd, mo):
    w = game.world
    from . import realms as RL
    k = rd['kind']
    t = KINDS[k]
    if k == 'wreckers' and mo in t['months'] and random.random() < .4:
        coast = coast_villages(game, rd['x'], rd['y'], 40)
        if coast:
            s = random.choice(coast)
            RL.news(game, f'A ship went onto the rocks near {s.name} in the storm. Lights were seen on the cliffs that night, '
                          f'and nothing was saved.', s.x, s.y, 'Peoples')
            rd['strength'] += 1
        return
    if k == 'pass':
        if mo in (11, 0, 1) and random.random() < .3:
            RL.news(game, f'An avalanche closed the pass below {rd["land"]}. The pass clans say the mountain is angry with '
                          f'those who do not pay the toll.', rd['x'], rd['y'], 'Peoples')
        return
    if k == 'island':
        if rd['angry'] > 0:
            rd['angry'] -= 1
            raid(game, idx, rd)
        return
    hungry = k == 'barbarian' and any(s.event and s.event[0] == 'famine' for s in w.settlements)
    if (mo in t['months'] or hungry) and random.random() < .6:
        raid(game, idx, rd)
    for rid in list(rd['held']):
        b = w.realm.baronies.get(rid)
        if b and random.random() < .15 and not rd['vassal']:
            kg = w.realm.kingdoms[b.kingdom]
            if random.random() < .5:
                rd['vassal'] = True
                RL.news(game, f'{RL.style(w.realm, w.realm.lord(kg.king), False)} accepts {chief_style(rd)} as a vassal: '
                              f'the {b.name} is a jarldom of {kg.short} now.' if k == 'sea' else
                        f'{RL.style(w.realm, w.realm.lord(kg.king), False)} accepts {chief_style(rd)} as lord of the {b.name}.',
                        rd['x'], rd['y'])
            else:
                rd['held'].remove(rid)
                b.held_by = None
                rd['strength'] = max(2, rd['strength'] - 3)
                x, y = RL.seat_pos(w, b.seat) or (rd['x'], rd['y'])
                RL.news(game, f'The knights of {kg.short} have driven {rd["name"].replace("The ", "the ")} out of the {b.name}.', x, y)


def coast_villages(game, x, y, r):
    w = game.world
    om = game.maps['over']
    out = []
    for s in w.settlements:
        if s.kind in ('hamlet', 'village', 'town') and s.id != 0 and cheb(s.x, s.y, x, y) <= r:
            if any(om.inb(s.x + dx, s.y + dy) and om.tile(s.x + dx, s.y + dy) == D.WATER for dx in range(-3, 4) for dy in range(-3, 4)):
                out.append(s)
    return out


def raid(game, idx, rd):
    """A raiding party sets out from the hall for a village of the realm."""
    from .wanderers import Wanderer
    from .world import dijkstra_path
    w = game.world
    om = game.maps['over']
    R = w.realm
    rng = 140 if rd['kind'] == 'sea' else 70
    cands = coast_villages(game, rd['x'], rd['y'], rng) if rd['kind'] in ('sea', 'island') else \
        [s for s in w.settlements if s.kind in ('hamlet', 'village', 'town') and s.id != 0 and cheb(s.x, s.y, rd['x'], rd['y']) <= rng
         and w.regions[s.region].faction == 'crown']
    watch = P(w).get('watch')
    if watch and rd['kind'] in ('sea', 'barbarian', 'ice') and random.random() < watch['strength'] / 25:
        from . import realms as RL
        RL.news(game, f'{watch["name"]} turned back a war party of {rd["name"].replace("The ", "the ")} at the border.',
                rd['x'], rd['y'])
        return
    if not cands:
        return
    s = min(random.sample(cands, min(4, len(cands))), key=lambda q: cheb(q.x, q.y, rd['x'], rd['y']))
    if rd['kind'] in ('sea', 'island'):
        start = landing(game, s)                       # the longships beach a few leagues off
    else:
        start = (rd['x'], rd['y'])
    if not start:
        return
    path = dijkstra_path(om, start, (s.x, s.y), lambda t: D.TILES[t].cost if D.TILES[t].walk else None)
    if not path:
        return
    wd = Wanderer(game.new_id(), 'raid', start[0], start[1])
    wd.ch, wd.fg = 'R', rd['fg']
    wd.name = f'A war party of the {rd["people"]}'
    wd.path = path[:-1]
    wd.speed = 11
    wd.raider, wd.target_s = idx, s.id
    t = KINDS[rd['kind']]
    wd.group = dict(keys=[random.choice(t['troops']) for _ in range(min(6, 2 + rd['strength'] // 2))],
                    lvl=max(3, w.danger_at(s.x, s.y) + 2), elite=1 if rd['strength'] > 7 else 0, leader=None, faction=None)
    wd.hostile = not rd.get('friend')
    w.wanderers.append(wd)
    from . import realms as RL
    if rd['kind'] == 'sea':
        RL.news(game, f'Sails on the sea off {s.name}: the longships of {rd["name"].replace("The ", "the ")} are out.',
                start[0], start[1], 'The Realms')
    elif random.random() < .5:
        RL.news(game, f'A war party of {rd["name"].replace("The ", "the ")} rides out of {rd["land"]}.', rd['x'], rd['y'], 'The Realms')


def landing(game, s):
    om = game.maps['over']
    for r in range(4, 10):
        cells = [(s.x + dx, s.y + dy) for dx in range(-r, r + 1) for dy in range(-r, r + 1) if max(abs(dx), abs(dy)) == r]
        random.shuffle(cells)
        for x, y in cells:
            if om.inb(x, y) and D.TILES[om.tile(x, y)].walk and om.tile(x, y) not in (D.TOWN, D.CITY, D.RIVER) and \
                    any(om.inb(x + a, y + b) and om.tile(x + a, y + b) == D.WATER for a in (-1, 0, 1) for b in (-1, 0, 1)):
                return x, y
    return None


RAID_KINDS = {'raid'}


def step(game, wd):
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
    raided(game, wd)


def describe(wd, game):
    if wd.kind != 'raid':
        return None
    s = game.world.settlements[wd.target_s]
    return f'{wd.name}, making for {s.name}' + (', hostile to you.' if wd.hostile else '.')


def raided(game, wd):
    """The war party reaches its village: a watch on the beach turns it back, or the village burns."""
    w = game.world
    if wd in w.wanderers:
        w.wanderers.remove(wd)
    rd = raiders(w)[wd.raider]
    s = w.settlements[wd.target_s]
    from . import realms as RL
    from .living import plundered, PLUNDER_DAYS
    if rd['warned'].get(s.id, -1) >= game.day:
        rd['strength'] = max(1, rd['strength'] - 1)
        RL.news(game, f'{s.name} was ready: a watch on the beach and the bell rung in time. The war party of the '
                      f'{rd["people"]} went home with nothing.', s.x, s.y)
        return
    if plundered(game, s):
        return
    s.plundered = game.day + PLUNDER_DAYS
    s.event = ('war', random.randint(5, 8))
    for g in ('grain', 'ale', 'cloth'):
        s.market[g][0] = min(s.market[g][0], 4)
    rd['strength'] += 1
    rd['raids'] += 1
    captives = random.randint(2, 9)
    s.__dict__.setdefault('captives', [])
    s.captives.append(dict(raider=wd.raider, n=captives, day=game.day))
    RL.news(game, f'The {rd["people"]} of {rd["land"]} plundered {s.name} and took {captives} of its people for ransom.',
            s.x, s.y, 'The Realms')
    R = w.realm
    if rd['strength'] >= 9 and rd['kind'] in ('sea', 'barbarian', 'desert') and len(rd['held']) < 2:
        b = R.baronies.get(s.region)
        if b and getattr(b, 'held_by', None) is None and b.seat and b.seat != R.kingdoms[b.kingdom].seat:
            b.held_by = wd.raider
            rd['held'].append(b.rid)
            rd['strength'] -= 3
            x, y = RL.seat_pos(w, b.seat)
            word = 'jarldom' if rd['kind'] == 'sea' else 'land'
            RL.news(game, f'{chief_style(rd)} of {rd["land"]} has taken the {b.name} and stays: a {word} of the '
                          f'{rd["people"]} inside the empire.', x, y, title=f'{rd["chief"]} takes the {b.name}')


def outside_threat(game):
    PW = P(game.world)
    if PW.get('gorvash'):
        return f'the Gorvash of {PW["gorvash"]["chief"]}'
    for rd in PW['raiders']:
        if rd['held'] and not rd['vassal']:
            return rd['name'].replace('The ', 'the ')
    return None


# ------------------------------------------------------------------ the church, the watch, the companies
def church_month(game):
    w = game.world
    PW = P(w)
    R = w.realm
    from . import realms as RL
    ch = PW['church']
    for kg in R.kingdoms:
        if kg.rebel and kg.rebel['baron'] not in ch['bans'] and random.random() < .4:
            lo = R.lord(kg.rebel['baron'])
            if lo:
                ch['bans'].append(lo.id)
                kg.rebel['score'] -= 1
                s = w.settlements[ch['seat']]
                RL.news(game, f'The High Priest{"ess" if ch["priest_g"] == "female" else ""} {ch["priest"]} has banned '
                              f'{RL.style(R, lo, False)}: no priest may bless {lo.his} men.', s.x, s.y)
    od = ch.get('order')
    if od and PW['circles'] and random.random() < .1:
        sid = random.choice(PW['circles'])
        st = w.sites[sid]
        if not getattr(st, 'burnt', False) and not getattr(st, 'warned', 0) > game.day:
            st.burnt = True
            st.stale = True
            game.maps.pop(st.map_key, None) if game.cur != st.map_key else None
            RL.news(game, f'{od["name"]} burned {st.name} on the moor, and the witch with it.', st.x, st.y)


def watch_month(game):
    PW = P(game.world)
    wt = PW.get('watch')
    if not wt:
        return
    wt['strength'] = max(2, wt['strength'] - (1 if random.random() < .5 else 0))
    if wt['strength'] <= 4 and random.random() < .3:
        st = game.world.sites[wt['forts'][0]]
        from . import realms as RL
        RL.news(game, f'{wt["name"]} is short of men and bread. The raiders slip past the forts.', st.x, st.y)


def company(game, data):
    """A war brings a mercenary company with a camp near the front."""
    from .sites import Site
    from .races import random_name
    w = game.world
    PW = P(w)
    if len([c for c in PW['companies'] if not c.get('gone')]) >= 2:
        return
    R = w.realm
    kg = R.kingdoms[data['a']]
    om = game.maps['over']
    near = [rid for rid, b in R.baronies.items() if b.kingdom in (data['a'], data['b'])]
    if not near:
        return
    r = w.regions[random.choice(near)]
    taken = [(s.x, s.y) for s in w.settlements] + [(q.x, q.y) for q in w.sites] + [(h.x, h.y) for h in w.holds]
    spot = None
    for _ in range(300):
        x, y = r.cx + random.randint(-12, 12), r.cy + random.randint(-10, 10)
        if om.inb(x, y) and D.TILES[om.tile(x, y)].walk and om.tile(x, y) in (D.GRASS, D.HILLS) and \
                not any(cheb(x, y, a, b) < 5 for a, b in taken):
            spot = (x, y)
            break
    if not spot:
        return
    name = f'The {random.choice(COMPANY_A)} {random.choice(COMPANY_B)}'
    st = Site(len(w.sites), 'merccamp', spot[0], spot[1], f'The camp of {name.replace("The ", "the ")}')
    st.faction = None
    w.sites.append(st)
    g = random.choice(['male', 'male', 'female'])
    c = dict(name=name, captain=random_name('human', g), captain_g=g, site=st.id, x=spot[0], y=spot[1], employer=kg.id,
             strength=random.randint(6, 12), gone=False, fg=random.choice([(200, 60, 60), (200, 180, 70), (90, 90, 100)]))
    st.company = len(PW['companies'])
    PW['companies'].append(c)
    from . import realms as RL
    RL.news(game, f'{name}, a mercenary company, has made camp near {r.name} and fights for {kg.short}.', spot[0], spot[1])


def companies_month(game):
    w = game.world
    PW = P(w)
    R = w.realm
    from . import realms as RL
    for c in PW['companies']:
        if c['gone']:
            continue
        wars = [x for x in R.wars if c['employer'] in (x['a'], x['b'])]
        if not wars:
            c['gone'] = True
            st = w.sites[c['site']]
            st.empty = True
            st.stale = True
            RL.news(game, f'{c["name"]} has broken camp and gone to look for another war.', c['x'], c['y'])
            continue
        war = wars[0]
        other = war['b'] if war['a'] == c['employer'] else war['a']
        if random.random() < .08 + c.get('bribed', 0):
            c['employer'] = other
            c['bribed'] = 0
            RL.news(game, f'{c["name"]} has gone over to {R.kingdoms[other].short}: more gold, they say.', c['x'], c['y'])
        c['strength'] += random.choice([0, 1])
        side = 1 if war['a'] == c['employer'] else -1
        if random.random() < .3:
            war['score'] += side
        if c['strength'] >= 15 and random.random() < .1:
            towns = [s for s in w.settlements if s.kind == 'town' and cheb(s.x, s.y, c['x'], c['y']) < 40]
            if towns:
                s = random.choice(towns)
                s.event = ('war', 8)
                RL.news(game, f'Captain {c["captain"]} of {c["name"].replace("The ", "the ")} has taken {s.name} for '
                              f'{"herself" if c["captain_g"] == "female" else "himself"}, and calls it pay owed.', s.x, s.y)


def revolt_month(game):
    """Heavy taxes, levies and hunger raise the villages."""
    from .sites import Site
    from .races import random_name
    w = game.world
    PW = P(w)
    R = w.realm
    from . import realms as RL
    rv = PW['revolt']
    if rv:
        kg = R.kingdoms[rv['kid']]
        rv['score'] += random.choice([-1, 0, 1]) + rv.get('help', 0)
        rv['help'] = 0
        s = w.settlements[rv['sid']]
        if rv['score'] >= 3:
            s.free = True
            PW['revolt'] = None
            kg.burden = max(0, kg.burden - 3)
            RL.news(game, f'{s.name} is a free commune: the lords of {kg.short} could not break the rising of {rv["leader"]}.',
                    s.x, s.y, title=f'The free commune of {s.name}')
            mark_site(game, rv['site'], 'empty')
        elif rv['score'] <= -2 or game.day - rv['since'] > 150:
            PW['revolt'] = None
            kg.burden = max(0, kg.burden - 2)
            gallows(game, s)
            RL.news(game, f'The rising at {s.name} is put down. {rv["leader"]} and twenty more hang from gallows along the road.',
                    s.x, s.y, title=f'The rising at {s.name}')
            mark_site(game, rv['site'], 'empty')
        return
    for kg in R.kingdoms:
        hungry = [s for s in w.settlements if s.region in R.baronies and R.baronies[s.region].kingdom == kg.id
                  and s.kind in ('hamlet', 'village') and s.id != 0 and not getattr(s, 'free', False)]
        if kg.burden >= 5 and hungry and random.random() < .35 + .1 * (kg.burden - 5):
            s = random.choice([q for q in hungry if q.event and q.event[0] == 'famine'] or hungry)
            g = random.choice(['male', 'female'])
            leader = random_name('human', g)
            om = game.maps['over']
            spot = None
            for _ in range(200):
                x, y = s.x + random.randint(-6, 6), s.y + random.randint(-6, 6)
                if om.inb(x, y) and cheb(x, y, s.x, s.y) >= 3 and D.TILES[om.tile(x, y)].walk and \
                        om.tile(x, y) in (D.GRASS, D.FOREST, D.HILLS) and not any(cheb(x, y, q.x, q.y) < 3 for q in w.sites):
                    spot = (x, y)
                    break
            if not spot:
                return
            st = Site(len(w.sites), 'rising', spot[0], spot[1], f'The camp of {leader}')
            st.faction = None
            w.sites.append(st)
            PW['revolt'] = dict(kid=kg.id, sid=s.id, leader=leader, leader_g=g, site=st.id, since=game.day, score=0)
            RL.news(game, f'The villages of {kg.short} have risen: {leader} leads them from a camp near {s.name}. '
                          f'Taxes, levies and an empty larder.', s.x, s.y, title=f'The rising at {s.name}')
            return


def mark_site(game, sid, how):
    st = game.world.sites[sid]
    setattr(st, how, True)
    st.stale = True
    if game.cur != st.map_key:
        game.maps.pop(st.map_key, None)


def gallows(game, s):
    om = game.maps['over']
    w = game.world
    if not hasattr(om, 'over') or om.over is None:
        om.over = {}
    n = 0
    for r in range(2, 8):
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                x, y = s.x + dx, s.y + dy
                if n < 4 and om.inb(x, y) and om.tile(x, y) == D.GRASS and any(
                        om.inb(x + a, y + b) and om.tile(x + a, y + b) == D.ROAD for a in (-1, 0, 1) for b in (-1, 0, 1)):
                    i = y * om.w + x
                    if i not in om.over:
                        om.over[i] = ('Γ', (150, 120, 90), None)
                        w.powers['gallows'].append(i)
                        n += 1


def exile(game, lo, kg):
    """Someone who lost a succession war holds court in exile and waits for his moment."""
    from .sites import Site
    w = game.world
    PW = P(w)
    if PW['pretender'] or not lo.alive:
        return
    om = game.maps['over']
    where = random.choice(['camp', 'dwarves', 'sea'])
    site = None
    if where == 'dwarves':
        holds = [s for s in w.settlements if s.kind == 'deephold']
        where = 'sea' if not holds else where
        sid = random.choice(holds).id if holds else None
    if where == 'camp':
        taken = [(s.x, s.y) for s in w.settlements] + [(q.x, q.y) for q in w.sites]
        spot = free_site(om, w, taken, lambda x, y: om.tile(x, y) in (D.FOREST, D.HILLS) and w.road_dist[y * om.w + x] >= 6, 3000)
        if spot:
            st = Site(len(w.sites), 'exile', spot[0], spot[1], f'The hidden camp of {lo.first}')
            st.hidden, st.found = True, False
            w.sites.append(st)
            site = st.id
        else:
            where = 'sea'
    lo.title = 'heir'
    PW['pretender'] = dict(lid=lo.id, kid=kg.id, where=where, site=site, sid=sid if where == 'dwarves' else None,
                           since=game.day, followers=random.randint(1, 3))
    from . import realms as RL
    R = w.realm
    words = {'camp': 'in a hidden camp in the wilds', 'dwarves': f'with the dwarves of {w.settlements[sid].name}' if where == 'dwarves' else '',
             'sea': 'over the sea'}[where]
    x, y = RL.place_of(game, R.lord(kg.king))
    RL.news(game, f'{lo.first} {R.houses[lo.house].name}, who lost the war for the crown of {kg.short}, holds court {words} '
                  f'and waits.', x, y, 'Lords and houses')


def pretender_month(game):
    w = game.world
    PW = P(w)
    pt = PW['pretender']
    if not pt:
        return
    R = w.realm
    lo = R.lord(pt['lid'])
    kg = R.kingdoms[pt['kid']]
    if not lo or not lo.alive:
        PW['pretender'] = None
        return
    pt['followers'] += random.choice([0, 0, 1]) + pt.pop('letters', 0)
    if pt['followers'] >= 6 and not kg.civil and random.random() < .3:
        from . import realms as RL
        PW['pretender'] = None
        if pt['site'] is not None:
            mark_site(game, pt['site'], 'empty')
        RL.news(game, f'{lo.first} {R.houses[lo.house].name} has come back from exile with an army!', *RL.place_of(game, R.lord(kg.king)))
        RL.civil_war(game, kg, lo)


# ------------------------------------------------------------------ the people you talk to
ROLES = {'chief', 'prior', 'watch_captain', 'merc_captain', 'rebel_leader', 'pretender', 'witch'}


def talk(game, npc):
    role = getattr(npc, 'role', '')
    if role not in ROLES or role == 'chief' and getattr(npc, 'raider', None) is None:
        return False
    from . import events as EV
    from . import realmjobs as RJ
    giver = RJ.giver_of(game, npc)
    if giver and RJ.turn_in_giver(game, giver, npc):
        return True
    w = game.world
    PW = P(w)
    if role == 'chief':
        rd = raiders(w)[npc.raider]
        text = (f'"Sit, guest, and eat. Under my roof no blade is drawn: that is the law of the {rd["people"]}. '
                f'Outside it, we will see."')
        opts = [('Is there work for me?', 'work'), ('Tell me of your people', 'lore'), ('Goodbye', 'bye')]
    elif role == 'prior':
        od = PW['church']['order']
        text = f'"{od["name"]} watches. Necromancers, witches, the servants of the dark: we hunt them all."'
        opts = [('Is there work for me?', 'work'), ('Goodbye', 'bye')]
    elif role == 'watch_captain':
        wt = PW['watch']
        text = f'"{wt["name"]} takes anyone who can hold a spear. We are {wt["strength"] * 10} men on these forts. We were a thousand once."'
        opts = [('Is there work for me?', 'work'), ('Goodbye', 'bye')]
    elif role == 'merc_captain':
        c = PW['companies'][npc.company]
        text = f'"{c["name"]} fights for {w.realm.kingdoms[c["employer"]].short}, for now. Gold talks louder than banners."'
        opts = [('Is there work for me?', 'work'), ('Goodbye', 'bye')]
    elif role == 'rebel_leader':
        text = '"We are not bandits. We are the ones who grow your bread, and we have none left. Will you help us or hang us?"'
        opts = [('Is there work for me?', 'work'), ('Goodbye', 'bye')]
    elif role == 'pretender':
        text = '"You find me in a poor court. But a crown is a crown, wherever it waits. Will you serve the rightful king?"'
        opts = [('Is there work for me?', 'work'), ('Goodbye', 'bye')]
    else:
        st = w.sites[game.map.site]
        text = '"Herbs, a curse, or your fortune? The church burns us for all three. Choose."'
        opts = [('Buy healing herbs (40c)', 'herbs'), ('Have your fortune told (1s)', 'fortune'), ('Is there work for me?', 'work'),
                ('Goodbye', 'bye')]
    EV.ask(game, 'power', npc.name, text, opts, npc=npc.id)
    return True


def r_power(game, choice, ctx):
    npc = next((o for o in game.map.mons if o.id == ctx.get('npc')), None)
    if not npc:
        return
    from . import realmjobs as RJ
    if choice == 'work':
        RJ.offer_giver(game, npc)
    elif choice == 'lore':
        rd = raiders(game.world)[npc.raider]
        from . import history as HI
        game.say(npc, HI.raider_lore(game, rd))
    elif choice == 'herbs':
        p = game.player
        if p.gold < 40:
            game.msg('You cannot pay for that.', 'bad')
            return
        p.gold -= 40
        from . import foraging as FG
        key = random.choice(['yarrow', 'yarrow', 'feverfew', 'kingsfoil'])
        FG.learn(game, key, '')
        it = FG.make_plant(game, key, 2)
        if game.add_to_inv(it):
            game.msg(f'The witch gives you {it.display_name()}.', 'good')
    elif choice == 'fortune':
        p = game.player
        if p.gold < 100:
            game.msg('You cannot pay for that.', 'bad')
            return
        p.gold -= 100
        game.say(npc, fortune(game))


def fortune(game):
    """A foretelling: something true about what is coming, wrapped in smoke."""
    w = game.world
    PW = P(w)
    R = w.realm
    from . import realms as RL
    old = [lo for lo in R.lords.values() if lo.alive and lo.title in ('king', 'emperor', 'baron') and lo.age > 55]
    if old and random.random() < .4:
        lo = random.choice(old)
        return f'"I see a crown of {lo.first} going cold. Before the year turns, someone weeps in {RL.seat_name(w, R.houses[lo.house].seat) if R.houses[lo.house].seat else "a hall"}."'
    if PW['tribes'] and not PW['gorvash']:
        t = max(PW['tribes'], key=lambda q: q['strength'])
        return f'"In the badlands a spear grows long. {t["chief"]} of {t["name"].replace("The ", "the ")}... beware that name."'
    for rd in PW['raiders']:
        if rd['strength'] >= 7:
            return f'"Smoke over the villages. The {rd["people"]} are hungry and strong this year."'
    return random.choice(['"Your road forks soon. Take the harder one."', '"A debt comes back to you, in coin or in blood."',
                          '"The dead are restless under the hills. Do not sleep in old places."'])


def register():
    from . import events as EV
    EV.RESOLVERS['power'] = r_power


register()
