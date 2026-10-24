"""More kinds of work, and the weight of the choices in them.

Village work, from the elder and the innkeeper: clear a nest, a bad harvest, find the missing, defend the village
from a raid that is coming, rescue a captive, the sick well, winter supplies for a hamlet far out, an escort for
someone who walks along (and can die), and the festivals of the year.
Trade, from the factor of the Merchants' Guild: a rush order for a town hit by bad news, a debt to collect, and
cargo the bandits took. War and the law, from the captain and the castellan: a deserter, a fortress to spy on,
and, when you are the one who is wanted, the chance to clear your name. Faith, from the temple: a pilgrimage, a
relic from a ruined temple, a shrine to take back from the dead. Exploring, for the Cartographers: a survey of a
place not yet on their map, an old way walked to its end, and the deep places mapped. The calendar: on the night
of the Starfall a star comes down whole, and whoever gets there first has star-iron. And your own company: a
sellsword with an old debt.

The guilds give some of these by rank (GUILD_JOBS). Choices in them leave marks on your standing in a town, with
a faction, with your god and your guild, on your record with the law, and on your hireling's loyalty (effects)."""
import random

from . import data as D
from . import calendar as CAL
from .money import fmt
from .worldgen import cheb

LABEL = {
    'nest': 'Clear a nest', 'harvest': 'Bad harvest', 'missing': 'Find the missing', 'defend': 'Defend a village',
    'rescue': 'Rescue a captive', 'well': 'The sick well', 'shrine': 'A desecrated shrine', 'boats': 'What took the boats',
    'bigone': 'The big one', 'deep': 'Map the deep', 'rush': 'Rush order', 'debt': 'Debt collector',
    'cargo': 'Recover stolen cargo', 'smuggle': 'Smuggle past the gate', 'spy': 'Spy on a fortress', 'deserter': 'A deserter',
    'name': 'Clear your name', 'pilgrim': 'Pilgrimage', 'relic': 'Relic of a god', 'survey': 'Survey',
    'lostway': 'A lost way', 'winter': 'Winter supplies', 'gather': 'Gather for the alchemist', 'starfall': 'The Starfall',
    'festival': 'The festival', 'mercdebt': "A sellsword's debt", 'desecrate': 'Desecrate a shrine',
}
KINDS = set(LABEL)
# what the job boards ask for: these make other kinds of mission ('escort' and 'hunt')
EXTRA = {'person', 'rival', 'legend'}

# the guilds, by rank: (from the first rank, from the third)
GUILD_JOBS = {
    'wardens': (['harvest', 'missing'], ['legend', 'rival']),
    'iron': (['person', 'cargo'], ['deserter', 'defend']),
    'dawn': (['shrine'], ['relic']),
    'magi': (['deep'], ['starfall']),
    'carto': (['survey'], ['lostway', 'deep']),
    'anglers': (['bigone'], ['boats']),
    'alembic': (['gather'], ['well']),
    'thieves': (['smuggle'], ['debt']),
    'coven': (['desecrate'], ['relic']),
}
VILLAGE = ['harvest', 'missing', 'nest', 'rescue', 'defend', 'well', 'person', 'winter', 'festival']
TOWN = ['person', 'missing', 'festival', 'nest', 'rescue']
CITY = ['person', 'festival']
CAPTAIN = ['defend', 'deserter', 'rescue']
FACTOR = ['rush', 'debt', 'cargo']
TEMPLE = ['pilgrim', 'relic', 'shrine']
HOLD = ['spy', 'deserter']

NEST_TAGS = ('antnest', 'spiderlair')
RUSH = {'plague': ('medicine', 'sick, and the healers have run out of medicine'), 'famine': ('grain', 'starving'),
        'fire': ('timber', 'half burned down'), 'war': ('arms', 'arming against a raid'),
        'undead': ('medicine', 'beset by the walking dead, and its wounded need medicine')}
FESTIVALS = [(2, 20, 'the Seedwake Fair'), (5, 15, 'Midsummer'), (8, 20, 'Harvest Home'), (11, 21, 'the Longnight Vigil')]
NAMES = ['Edda', 'Hob', 'Maud', 'Corwin', 'Tamsin', 'Osric', 'Wenna', 'Garrick', 'Agnes', 'Alwin', 'Bess', 'Dunstan',
         'Elsa', 'Ivo', 'Jessamy', 'Leofric', 'Mabel', 'Rowan', 'Sabine', 'Tobin', 'Hilde', 'Piers']
MISSING_WHO = [("the miller's boy", 'his'), ('a shepherd', 'her'), ("the reeve's daughter", 'her'), ('an old woodcutter', 'his'),
               ('a herb-woman', 'her'), ("the smith's apprentice", 'his'), ('a goose-girl', 'her')]
KEEPSAKE = ['a carved wooden horse', 'a copper ring', 'a knitted cap', 'a little knife with a bone handle', 'a pouch of buttons']
TRADES = ['cooper', 'chandler', 'tanner', 'vintner', 'wheelwright', 'saddler', 'dyer']
CONTRABAND = ['Varnish wine without a tax seal', 'a crate of black powder', 'poppy resin', 'a satchel of forged deeds',
              'a bale of untaxed silk']
GOD_RELIC = {'solmara': 'the Sunwheel of Saint Edda', 'valdric': "the Iron Judge's Seal", 'thessa': "the Green Mother's Sickle",
             'durnak': "Durnak's Anvil-stone", 'skell': "Skell's Loaded Die"}
BIG_FISH = ['Old Grandfather', 'the Silver Queen', 'Brother Whiskers', 'Old Tom', 'the Grey Ghost', 'Mother Mudd']
BIG_WHAT = ['a pike as long as a man', 'a carp older than the village', 'an eel as thick as your arm', 'a trout of the old stories']
RIVALS = ['Brannoc the Tracker', 'Ysolde Greyfeather', 'Hal Six-Fingers', 'Corra of the Marches', 'Old Ulf', 'Mirelle Vane']


# ------------------------------------------------------------------ helpers
def mission(game, src, kind, title, desc, reward_s, rep=(5, 10), deadline=None, hold=False, **data):
    from . import missions as MS
    m = MS.Mission(game.new_id(), kind, None if hold else src.id)
    if hold:
        m.hold = src.id
    m.title, m.desc = title, desc
    m.reward = round(reward_s) * 100
    m.rep = random.randint(*rep)
    m.deadline = deadline
    m.data = data
    m.faction = src.faction
    return m


def the(name):
    """'The Hollow Den' in the middle of a sentence: 'the Hollow Den'."""
    return 'the ' + name[4:] if name.startswith('The ') else name


def cap(text):
    return text[0].upper() + text[1:] if text else text


def _dir(a, x, y):
    from .engine import dir_name
    return dir_name(x - a.x, y - a.y)


def _region(game, x, y):
    from .named import place
    return place(game.world.region_at(x, y))


def _spot(game, x, y, lo, hi):
    from .named import _spot as sp
    return sp(game, x, y, lo, hi)


def _beside(game, x, y, lo, hi, tiles):
    """A walkable cell off the road beside one of these tiles (water, a river), between lo and hi from (x, y)."""
    om = game.maps['over']
    w = game.world
    for _ in range(800):
        cx, cy = x + random.randint(-hi, hi), y + random.randint(-hi, hi)
        if not om.inb(cx, cy) or cheb(cx, cy, x, y) < lo:
            continue
        t = om.tile(cx, cy)
        if not D.TILES[t].walk or t in (D.ROAD, D.TOWN, D.CITY, D.ENTR, D.CASTLE, D.FORT):
            continue
        if any(cheb(cx, cy, s.x, s.y) < 3 for s in w.settlements):
            continue
        if any(om.inb(cx + a, cy + b) and om.tile(cx + a, cy + b) in tiles for a in (-1, 0, 1) for b in (-1, 0, 1)):
            return cx, cy
    return None


def pos(game):
    """Where you are on the overworld."""
    p = game.player
    return (p.x, p.y) if game.cur == 'over' else getattr(game, 'over_pos', (p.x, p.y))


def road_len(game, a, b):
    from .wanderers import road_path
    return len(road_path(game, a, b) or [])


def _towns_by_road(game, s, lo, hi, pred=lambda o: True):
    out = []
    for o in game.world.settlements:
        if o.id == s.id or o.kind == 'deephold' or not pred(o) or cheb(o.x, o.y, s.x, s.y) > hi:
            continue
        n = road_len(game, s.id, o.id)
        if lo <= n <= hi:
            out.append((o, n))
    return out


def taken(game, key, value):
    """Is some job, taken or on offer, already about this place?"""
    from . import missions as MS
    for m in MS.active(game):
        if m.data.get(key) == value:
            return True
    return False


def name_of(game):
    return random.choice(NAMES)


def he(word):
    return 'he' if word == 'his' else 'she'


def him(word):
    return 'him' if word == 'his' else 'her'


def at(game, s, r=4):
    """Are you in or right beside this settlement?"""
    here = game.here
    if here is not None and here.id == s.id:
        return True
    if game.cur in ('over',) or game.map.kind in ('town', 'site'):
        x, y = pos(game)
        return cheb(x, y, s.x, s.y) <= r
    return False


def stat(game, key):
    s = game.stats()
    return s.get(key, getattr(game.player, key, 10))


# ------------------------------------------------------------------ the weight of a choice
def effects(game, town=(), faction=(), god=0, guild=(), crime=None, loyalty=0, quiet=False):
    """Choices leave marks. town: [(sid, n)], faction: [(f, n)], god: n for your own god, or (god, n) to count only
    if that god is yours; guild: [(key, n)]; crime: (severity, what, witnessed); loyalty: n for your hireling."""
    from .war import change_rep
    from . import gods as GD
    from . import guilds as GU
    from . import mercs as MC
    w, p = game.world, game.player
    lines = []
    for sid, n in town:
        if sid is None or not n:
            continue
        s = w.settlements[sid]
        s.rep = max(-100, min(100, s.rep + n))
        lines.append(f'{s.name} {"thinks better of you" if n > 0 else "thinks less of you"} ({n:+})')
    for f, n in faction:
        if f and f != 'cult' and n:
            change_rep(game, f, n, quiet=True)
            lines.append(f"the {D.FACTIONS[f]['short']} {'approve' if n > 0 else 'disapprove'} ({n:+})")
    g, n = god if isinstance(god, tuple) else (getattr(p, 'god', None), god)
    if n and g and getattr(p, 'god', None) == g:
        if n > 0:
            GD.gain(game, n)
        else:
            GD.lose(game, -n)
        lines.append(f"{GD.GODS[g]['name']} is {'pleased' if n > 0 else 'displeased'}")
    for key, n in guild:
        st = GU.state(game)[key]
        if n and (st['joined'] or st['rep']):
            st['rep'] = max(0, st['rep'] + n)
            lines.append(f"{GU.GUILDS[key]['short']} {'take note' if n > 0 else 'will not forget it'} ({n:+})")
    if loyalty:
        mc = MC.get(game, 'merc')
        if mc:
            mc.morale = max(0, min(100, mc.morale + loyalty))
            lines.append(f'{mc.name} {"is yours to the end" if loyalty >= 20 else "is grateful" if loyalty > 0 else "looks at you differently"}')
    if lines and not quiet:
        game.msg('This will be remembered: ' + '; '.join(lines) + '.', 'info')
    if crime:
        from . import crime as CR
        CR.commit(game, *crime)
    return lines


# ------------------------------------------------------------------ the calendar
def day_of(year, mo, dom):
    return year * 360 + mo * 30 + dom - 1 - CAL.START + 1


def next_festival(day):
    """(day, name) of the next festival, today included."""
    y = (CAL.START + day - 1) // 360
    best = None
    for yy in (y, y + 1):
        for mo, dom, name in FESTIVALS:
            d = day_of(yy, mo, dom)
            if d >= day and (best is None or d < best[0]):
                best = (d, name)
    return best


def next_starfall(day):
    from . import weather as WX
    for d in range(day, day + 361):
        if WX.starfall(d):
            return d
    return None


def star(game):
    """The star of this year's Starfall, once it has come down: dict(x, y, r, day, rivals, taken)."""
    return game.__dict__.get('star')


# ------------------------------------------------------------------ making offers
def board_kinds(game, s):
    """What the innkeeper's board asks for, besides the old kinds."""
    if s.is_city:
        return CITY
    if s.kind in ('village', 'hamlet'):
        return VILLAGE
    return TOWN


def guild_kinds(game, key):
    from . import guilds as GU
    low, high = GUILD_JOBS.get(key, ([], []))
    return list(low) + (list(high) * 2 if GU.rank(game, key) >= 2 else [])


def make(game, s, kind):
    fn = MAKE.get(kind)
    if not fn:
        return None
    try:
        m = fn(game, s)
    except IndexError:
        return None
    return m


def make_hold(game, h, kind):
    if kind == 'spy':
        return _spy(game, h, hold=True)
    if kind == 'deserter':
        return _deserter(game, h, hold=True)
    return None


def _nest(game, s):
    w = game.world
    cleared = w.__dict__.setdefault('nests_cleared', set())
    ds = [d for d in w.dungeons.values() if d.tag in NEST_TAGS and d.id not in cleared and d.boss
          and cheb(d.x, d.y, s.x, s.y) <= 80 and not taken(game, 'did', d.id)]
    if ds and random.random() < .7:
        d = min(ds, key=lambda d: cheb(d.x, d.y, s.x, s.y))
        what = 'Giant ants' if d.tag == 'antnest' else 'Spiders'
        boss = D.MONSTERS[d.boss]['name'].lower()
        m = mission(game, s, 'nest', f'Clear {the(d.name)}',
                    f'{what} from {the(d.name)}, to the {_dir(s, d.x, d.y)}, strip the fields and carry off the goats. Go down '
                    f'to the bottom of the nest and kill the {boss}, and the rest will scatter.',
                    25 + (d.base + d.depth) * 5, (6, 10), did=d.id, boss=d.boss)
        return m
    spot = _spot(game, s.x, s.y, 6, 20)
    if not spot:
        return None
    lvl = w.danger_at(*spot) + 1
    reg = _region(game, *spot)
    if random.random() < .5:
        keys = ['web_weaver'] + [random.choice(['spider_swarm', 'wolf_spider', 'jumping_spider']) for _ in range(random.randint(2, 4))]
        text = f'Webs hang over the old lane in {reg}, to the {_dir(s, *spot)}, thick as sails. The goats that go in do not come out.'
        intro = 'The trees close in, white with silk. Something big turns in the webs above you.'
    else:
        keys = ['ant_soldier', 'ant_soldier'] + ['ant_worker'] * random.randint(3, 5)
        text = f'A mound of giant ants has risen in {reg}, to the {_dir(s, *spot)}, and they are coming for the granaries.'
        intro = 'The ground shakes and splits. Ants as big as dogs pour out of the mound!'
    return mission(game, s, 'nest', 'Burn out a nest', text + ' Kill them all.', 18 + lvl * 4, (6, 10),
                   spot=list(spot), keys=keys, lvl=lvl, intro=intro, where='the nest')


def _harvest(game, s):
    if s.is_city:
        return None
    w = game.world
    spot = _spot(game, s.x, s.y, 4, 12)
    if not spot:
        return None
    lvl = w.danger_at(*spot) + 1
    r = random.random()
    if r < .45:
        keys = ['boar'] * random.randint(3, 5)
        text = f'Wild boars root up the fields of {s.name} by night. They lie up in the thickets to the {_dir(s, *spot)}.'
        intro = 'The thicket bursts open. Boars, a whole sounder of them, and they are not afraid of you.'
    elif r < .75 and lvl >= 3:
        keys = ['scarecrow'] + ['giant_hawk'] * random.randint(1, 2)
        text = (f'The crows came by the thousand to the fields of {s.name}, and something walks among them on straw legs. '
                f'The farmers will not go out to the {_dir(s, *spot)} any more.')
        intro = 'Crows rise from the stubble all at once. The scarecrow in the middle of the field turns its head.'
    else:
        keys = ['rat'] * random.randint(5, 8)
        text = f'Rats as big as cats are eating the seed corn of {s.name}. Their warren is in the old barn to the {_dir(s, *spot)}.'
        intro = 'The floor of the barn moves. It is rats, all of it.'
    return mission(game, s, 'harvest', f'Save the harvest of {s.name}', text, 14 + lvl * 4, (6, 10), game.day + 10,
                   spot=list(spot), keys=keys, lvl=lvl, intro=intro, where='the fields')


def _missing(game, s):
    w = game.world
    spot = _spot(game, s.x, s.y, 10, 26)
    if not spot:
        return None
    who, his = random.choice(MISSING_WHO)
    name = name_of(game)
    days = random.randint(1, 3)
    area = [spot[0] + random.randint(-4, 4), spot[1] + random.randint(-3, 3), 8]
    reg = _region(game, *spot)
    return mission(game, s, 'missing', f'Find {name}',
                   f'{name}, {who}, went into {reg} {days} day{"s" if days > 1 else ""} ago and has not come back. '
                   f'Look for tracks, and bring {him(his)} home, or word of what became of {him(his)}.',
                   16 + w.danger_at(*spot) * 4, (8, 12), game.day + 12,
                   spot=list(spot), area=area, name=name, who=who, his=his, since=game.day - days, reach=2)


def _defend(game, s):
    w = game.world
    v = s
    if s.is_city:
        vs = [o for o in w.settlements if o.kind in ('village', 'hamlet') and cheb(o.x, o.y, s.x, s.y) <= 40]
        if not vs:
            return None
        v = random.choice(vs)
    if taken(game, 'village', v.id):
        return None
    danger = w.danger_at(v.x, v.y)
    lvl = danger + 2
    if danger >= 3 and random.random() < .5:
        keys, who = ['orc', 'orc', 'orc_spear', 'orc', 'orc_shaman'][:3 + danger // 2], 'an orc warband'
    elif danger >= 2 and random.random() < .5:
        keys, who = ['gnoll_packlord', 'gnoll_hunter', 'gnoll_hunter', 'gnoll_hunter'], 'gnolls'
    else:
        keys, who = ['bandit', 'bandit', 'brigand', 'raider', 'bandit'][:3 + danger // 2], 'outlaws'
    day = game.day + random.randint(3, 6)
    m = mission(game, s, 'defend', f'Defend {v.name}',
                f'Shepherds saw {who} gathering in {_region(game, v.x, v.y)}. They will fall on {v.name} on the '
                f'{CAL.ordinal(CAL._split(day)[2])} of {CAL.MONTHS[CAL._split(day)[1]]}. Be there when they come.',
                30 + lvl * 6, (10, 14), day, village=v.id, day=day, keys=keys, lvl=lvl, who=who)
    m.target = v.id
    return m


def _rescue(game, s):
    w = game.world
    name = name_of(game)
    who, his = random.choice(MISSING_WHO)
    from . import tribes as TR
    camp = TR.near_camp(game, s, 'warcamp', 55)
    if camp and random.random() < .5 and not taken(game, 'camp', camp.id):
        lvl = TR.level(game, camp)
        short = camp.name.replace('Camp of the ', 'the ').replace(' Camp', '').replace('The ', 'the ', 1)   # a board line holds 42 letters
        title = f'Rescue {name} from {camp.name}'
        return mission(game, s, 'rescue', title if len(title) <= 42 else f'Rescue {name} from {short}',
                       f'Orcs took {name}, {who}, on the road and dragged {him(his)} off to {camp.name}, their war camp to '
                       f'the {_dir(s, camp.x, camp.y)}. They keep captives in a cage until they sell them. Break the cage, '
                       f'or buy {him(his)} out if they will deal with you.', 40 + lvl * 5, (8, 12), game.day + 14,
                       camp=camp.id, name=name, his=his, lvl=lvl, where=camp.name)
    camps = [q for q in w.pois if q.kind == 'orccamp' and q.ready_day < 10 ** 9 and cheb(q.x, q.y, s.x, s.y) <= 55
             and not taken(game, 'poi', q.id)]
    if camps and random.random() < .6:
        q = min(camps, key=lambda q: cheb(q.x, q.y, s.x, s.y))
        from .worldgen import band_keys
        lvl = w.danger_at(q.x, q.y) + 2
        keys = band_keys('orc_chief', random.randint(5, 7))
        return mission(game, s, 'rescue', f'Rescue {name} from the orcs',
                       f'Orcs took {name}, {who}, from the road and carried {him(his)} off to their camp, to the '
                       f'{_dir(s, q.x, q.y)}. {he(his).capitalize()} is still alive; the orcs keep their captives for a while.',
                       35 + lvl * 5, (8, 12), game.day + 10, spot=[q.x, q.y], poi=q.id, keys=keys, lvl=lvl, name=name,
                       his=his, where='the orc camp', intro='The orcs leap up from their fire, roaring. Behind the banner '
                       'a figure is tied to a stake.')
    spot = _spot(game, s.x, s.y, 8, 24)
    if not spot:
        return None
    lvl = w.danger_at(*spot) + 1
    keys = ['web_weaver', 'web_weaver'] + ['spiderling'] * random.randint(2, 4)
    return mission(game, s, 'rescue', f'Cut {name} out of the webs',
                   f'Spiders took {name}, {who}, in {_region(game, *spot)}, to the {_dir(s, *spot)}. They wrap what they take '
                   f'and keep it for later. There may still be time.', 30 + lvl * 5, (8, 12), game.day + 6,
                   spot=list(spot), keys=keys, lvl=lvl, name=name, his=his, where='the webs',
                   intro='Silk everywhere, and in it, a cocoon that moves and moans. The spiders come down on their threads.')


def _well(game, s):
    w = game.world
    v = s
    if s.is_city:
        vs = [o for o in w.settlements if o.kind in ('village', 'hamlet', 'town') and cheb(o.x, o.y, s.x, s.y) <= 45]
        if not vs:
            return None
        v = random.choice(vs)
    if taken(game, 'village', v.id):
        return None
    cause = random.choice(['drowned', 'poisoner', 'roots'])
    m = mission(game, s, 'well', f'The sick well of {v.name}',
                f'The well of {v.name} has turned. The water smells of something, the children are sick, and the cattle will '
                f'not drink. Find what poisons it, and put it right.', 25 + w.danger_at(v.x, v.y) * 5, (8, 12), game.day + 12,
                village=v.id, cause=cause)
    m.target = v.id
    return m


def _shrine(game, s):
    w = game.world
    qs = [q for q in w.pois if q.kind == 'shrine' and getattr(q, 'god', None) != 'morrak' and 6 <= cheb(q.x, q.y, s.x, s.y) <= 60
          and not getattr(q, 'defiled', False) and not taken(game, 'poi', q.id)]
    if not qs:
        return None
    q = random.choice(qs)
    lvl = w.danger_at(q.x, q.y) + 2
    if random.random() < .5:
        keys = ['zombie', 'skeleton', 'skeleton', 'ghoul'][:2 + lvl // 3]
        text = f'The dead have come up out of the ground around {q.name}, to the {_dir(s, q.x, q.y)}, and they will not leave it.'
        intro = 'The candles of the shrine are out. Around it, the dead stand waiting, and turn to you.'
    else:
        keys = ['cultist', 'cultist', 'skeleton']
        text = f"Servants of Morrak have taken {q.name}, to the {_dir(s, q.x, q.y)}, and foul it with blood every night."
        intro = 'Hooded figures around the shrine, and blood on the stone. They draw their knives.'
    return mission(game, s, 'shrine', f'Take back {q.name}', text + ' Drive them out, so that the faithful can pray there again.',
                   22 + lvl * 5, (8, 12), spot=[q.x, q.y], poi=q.id, keys=keys, lvl=lvl, intro=intro, where=q.name)


def _boats(game, s):
    if not getattr(s, 'harbour', False):
        return None
    w = game.world
    spot = _beside(game, s.x, s.y, 3, 16, (D.WATER,))
    if not spot:
        return None
    lvl = w.danger_at(*spot) + 2
    cause, keys = random.choice([('a sea hag', ['sea_hag', 'merrow']), ('a giant octopus', ['octopus', 'giant_crab', 'giant_crab']),
                                 ('brinefolk', ['brinefolk'] * random.randint(3, 4))])
    return mission(game, s, 'boats', f'What took the boats of {s.name}?',
                   f'Three boats of {s.name} went out and did not come back, and the nets come up torn. Something comes in by '
                   f'the rocks to the {_dir(s, *spot)} at dusk. The fishermen will not say what they fear.', 30 + lvl * 6, (8, 12),
                   spot=list(spot), keys=keys, lvl=lvl, cause=cause, where='the rocks',
                   intro=f'The water by the rocks boils. It is {cause}!')


def _bigone(game, s):
    spot = _beside(game, s.x, s.y, 4, 30, (D.WATER, D.SHALLOW, D.RIVER))
    if not spot:
        return None
    season = CAL.season(game.day)
    cond = random.choice([('rain', 'when it rains'), ('night', 'at night'), ('season', f'in {season}')])
    fish = f'{random.choice(BIG_FISH)}, {random.choice(BIG_WHAT)}'
    return mission(game, s, 'bigone', f'The big one: {fish.split(",")[0]}',
                   f'There is {fish.split(", ", 1)[1]} in the water near {_region(game, *spot)}, to the {_dir(s, *spot)}: '
                   f'{fish.split(",")[0]}, the old men call it. It bites only {cond[1]}. Bring it in, whole. You will need a pole, '
                   f'and a steady hand.', 28, (6, 10), game.day + 40,
                   spot=list(spot), cond=cond[0], when=cond[1], fish=fish, season=season, reach=6, where='the water')


def _deep(game, s):
    w = game.world
    ds = [d for d in w.dungeons.values() if d.depth >= 2 and d.id != 'den' and game.max_depth.get(d.id, 0) < d.depth
          and cheb(d.x, d.y, s.x, s.y) <= 80 and getattr(d, 'town', None) is None and not getattr(d, 'rise', False)
          and not taken(game, 'did', d.id)]
    if not ds:
        return None
    d = random.choice(ds)
    return mission(game, s, 'deep', f'Map the depths of {the(d.name)}',
                   f'Nobody has drawn {the(d.name)}, to the {_dir(s, d.x, d.y)}, below the first level. Go down to its deepest '
                   f'level and come back with what you saw.', 22 + d.depth * 8 + d.base * 3, (6, 10), did=d.id, deep=d.id)


def _rush(game, s):
    cands = []
    for o, n in _towns_by_road(game, s, 12, 100, lambda o: o.event and o.event[0] in RUSH):
        key, left = o.event
        from .missions import travel_days
        if left >= travel_days(n) + 1:
            cands.append((o, n, key, left))
    if not cands:
        return None
    o, n, key, left = random.choice(cands)
    g, why = RUSH[key]
    gd = D.GOODS[g]
    q = max(3, random.randint(6, 12) // gd['w'])
    m = mission(game, s, 'rush', f'Rush {q} {gd["name"]} to {o.name}',
                f'{o.name} is {why}. It needs {q} {gd["name"]} before {CAL.short(game.day + left)}, and the Guild has none to '
                f'spare. Buy them wherever you can and get them there in time. The Guild pays for the goods, and for the haste.',
                gd['base'] * q * 1.1 + n * .5 + 15, (6, 10), game.day + left, good=g, qty=q)
    m.target = o.id
    return m


def _debt(game, s):
    cands = _towns_by_road(game, s, 15, 90)
    if not cands:
        return None
    o, n = random.choice(cands)
    who = f'Master {name_of(game)} the {random.choice(TRADES)}'
    amount = random.randint(20, 60) * 100
    m = mission(game, s, 'debt', f'Collect a debt in {o.name}',
                f'{who} of {o.name} owes the Guild {fmt(amount)} and has not paid since the winter. Collect it and bring it back. '
                f'How you collect it is your business.', 8 + amount / 100 * .3, (5, 8), game.day + 14,
                debtor=who, amount=amount)
    m.target = o.id
    return m


def _cargo(game, s):
    w = game.world
    goods = list(s.produce) or list(D.GOODS)
    g = random.choice(goods)
    q = random.randint(6, 12)
    camps = [c for c in w.pois if c.kind == 'camp' and c.ready_day < 10 ** 9 and cheb(c.x, c.y, s.x, s.y) <= 55
             and not taken(game, 'poi', c.id)]
    if camps and random.random() < .6:
        c = min(camps, key=lambda c: cheb(c.x, c.y, s.x, s.y))
        spot, poi, where = [c.x, c.y], c.id, f'their camp, to the {_dir(s, c.x, c.y)}'
    else:
        sp = _spot(game, s.x, s.y, 10, 30)
        if not sp:
            return None
        spot, poi, where = list(sp), None, f'{_region(game, *sp)}, to the {_dir(s, *sp)}'
    lvl = w.danger_at(*spot) + 1
    leader = random.choice(D.BANDIT_LEADERS)
    keys = ['bandit'] + [random.choice(['bandit', 'brigand', 'raider']) for _ in range(random.randint(3, 4))]
    return mission(game, s, 'cargo', f'Recover the {D.GOODS[g]["name"].lower()} of {s.name}',
                   f'{leader} and their gang took a wagon of {q} {D.GOODS[g]["name"]} on the road out of {s.name}. They hole up in '
                   f'{where}. Get it back.', 26 + lvl * 5, (6, 10), game.day + 12,
                   spot=spot, poi=poi, keys=keys, lvl=lvl, good=g, qty=q, leader=leader, where='the outlaws',
                   intro=f'{leader} looks up from the stolen wagon and laughs. "You came for this? Come and take it."')


def _smuggle(game, s):
    cands = _towns_by_road(game, s, 12, 90, lambda o: o.kind != 'hamlet')
    if not cands:
        return None
    o, n = random.choice(cands)
    what = random.choice(CONTRABAND)
    from .missions import travel_days
    m = mission(game, s, 'smuggle', f'Smuggle goods into {o.name}',
                f'{cap(what)}, to a friend of ours in {o.name}. The guards at the gate search the carts. Get it past them. '
                f'If they find it, you never heard of us.', 22 + n * .6, (4, 8), game.day + travel_days(n) + 4,
                contraband=what, bribe=random.randint(8, 15) * 100)
    m.target = o.id
    return m


def _spy(game, src, hold=False):
    w = game.world
    enemies = [e for e in D.FACTIONS[src.faction]['enemies'] if e != src.faction]
    hs = [h for h in w.holds if h.faction in enemies and 8 <= cheb(h.x, h.y, src.x, src.y) <= 90 and not taken(game, 'hold_t', h.id)]
    if not hs:
        return None
    h = min(hs, key=lambda h: cheb(h.x, h.y, src.x, src.y))
    f = D.FACTIONS[h.faction]['short']
    m = mission(game, src, 'spy', f'Spy on {h.title}',
                f'Go to {h.title} ({f}), to the {_dir(src, h.x, h.y)}. Do not storm it. Count the men on the walls, see what is '
                f'stored in the yard, and come back without being known.', 40 + w.danger_at(h.x, h.y) * 5, (8, 12), game.day + 14,
                hold=hold, spot=[h.x, h.y], hold_t=h.id, reach=3, where=h.title)
    return m


def _deserter(game, src, hold=False):
    w = game.world
    vs = [o for o in w.settlements if o.kind in ('village', 'hamlet') and cheb(o.x, o.y, src.x, src.y) <= 60]
    if not vs:
        return None
    v = random.choice(vs)
    spot = _spot(game, v.x, v.y, 4, 12)
    if not spot:
        return None
    name = f'{name_of(game)} {random.choice(["Ashby", "Holloway", "Stonebrook", "Marsh", "Tanner", "Reed"])}'
    f = D.FACTIONS[src.faction]['short']
    where = src.title if hold else src.name
    m = mission(game, src, 'deserter', f'Bring back the deserter {name.split()[0]}',
                f'{name}, a soldier of the {f}, ran from {where} with a month of pay. He is hiding in the woods near his home '
                f'village of {v.name}, to the {_dir(src, v.x, v.y)}. Bring him back.', 25 + w.danger_at(*spot) * 3, (8, 12),
                game.day + 14, hold=hold, spot=list(spot), village=v.id, name=name, reach=1, where='the woods')
    return m


def _pilgrim(game, s):
    from . import gods as GD
    if 'temple' not in s.services:
        return None
    w = game.world
    god = GD.temple_god(game) if getattr(game.map, 'sid', None) == s.id else getattr(s, 'god', None)
    qs = [q for q in w.pois if q.kind == 'shrine' and 25 <= cheb(q.x, q.y, s.x, s.y) <= 110 and not getattr(q, 'defiled', False)]
    own = [q for q in qs if getattr(q, 'god', None) == god]
    qs = own or qs
    if not qs:
        return None
    q = random.choice(qs)
    d = cheb(q.x, q.y, s.x, s.y)
    from .missions import travel_days
    m = mission(game, s, 'pilgrim', f'A pilgrimage to {q.name}',
                f'Carry the offering of the faithful of {s.name} to {q.name}, far to the {_dir(s, q.x, q.y)}, and lay it on the '
                f'stone. Come back and tell us it is done.', 18 + d * .4, (8, 12), game.day + travel_days(int(d * 1.4)) * 2 + 6,
                spot=[q.x, q.y], poi=q.id, god=getattr(q, 'god', god), where=q.name)
    return m


def _relic(game, s):
    from . import gods as GD
    w = game.world
    god = GD.temple_god(game) if getattr(game.map, 'sid', None) == s.id and 'temple' in s.services else \
        random.choice(list(GOD_RELIC))
    god = god if god in GOD_RELIC else 'solmara'
    ruins = [q for q in w.pois if q.kind in ('ruined_temple', 'ruined_monastery') and q.did and w.dungeons[q.did].relic is None
             and cheb(q.x, q.y, s.x, s.y) <= 100]
    if not ruins:
        return None
    q = min(ruins, key=lambda q: cheb(q.x, q.y, s.x, s.y))
    d = w.dungeons[q.did]
    relic = GOD_RELIC[god]
    return mission(game, s, 'relic', f'Recover {relic}',
                   f'{cap(relic)} was lost when {q.name}, to the {_dir(s, q.x, q.y)}, fell to ruin. It lies somewhere in the deepest '
                   f'hall beneath it. Bring it home to {s.name}.', 40 + (d.base + d.depth) * 6, (8, 12),
                   dungeon=d.id, did=d.id, relic=relic, god=god, poi=q.id)


def _survey(game, s):
    om = game.maps['over']
    for _ in range(600):
        x, y = s.x + random.randint(-45, 45), s.y + random.randint(-30, 30)
        if not om.inb(x, y) or not 18 <= cheb(x, y, s.x, s.y) <= 45 or om.seen[y * om.w + x]:
            continue
        t = om.tile(x, y)
        if not D.TILES[t].walk or t in (D.ROAD, D.TOWN, D.CITY):
            continue
        d = cheb(x, y, s.x, s.y)
        return mission(game, s, 'survey', f'Survey {_region(game, x, y)}',
                       f'The Society has nothing on its maps of {_region(game, x, y)}, to the {_dir(s, x, y)}. Go there, take '
                       f'your bearings and sketch the lie of the land.', 14 + d * .4, (5, 8), game.day + 16,
                       spot=[x, y], reach=2, where=_region(game, x, y))
    return None


def _lostway(game, s):
    from . import hidden as HP
    ways = [wy for wy in getattr(game.world, 'ways', []) if len(wy.cells) >= 8 and not taken(game, 'way', wy.id)]
    if not ways:
        return None
    om = game.maps['over']
    unseen = [wy for wy in ways if wy.cells[-1] not in HP.seen_cells(game)]
    ways = unseen or ways
    wy = min(ways, key=lambda wy: cheb(wy.cells[0] % om.w, wy.cells[0] // om.w, s.x, s.y))
    ex, ey = wy.cells[-1] % om.w, wy.cells[-1] // om.w
    sx, sy = wy.cells[0] % om.w, wy.cells[0] // om.w
    return mission(game, s, 'lostway', f'Walk {wy.name} to its end',
                   f'An old Varnish chart shows a way that leaves the land we know near {_region(game, sx, sy)}, to the '
                   f'{_dir(s, sx, sy)}. Nobody knows where it ends. Walk it to its end and tell us.', 26 + len(wy.cells) * .15,
                   (6, 10), way=wy.id, spot=[ex, ey], reach=1, where='the end of the way')


def _winter(game, s):
    if CAL.season(game.day) != 'autumn':
        return None
    cands = _towns_by_road(game, s, 25, 110, lambda o: o.kind in ('hamlet', 'village'))
    if not cands:
        return None
    hamlets = [c for c in cands if c[0].kind == 'hamlet'] or cands
    o, n = max(hamlets, key=lambda c: c[1] + random.randint(0, 20))
    g = random.choice(['timber', 'grain', 'furs'])
    gd = D.GOODS[g]
    q = max(3, random.randint(8, 16) // gd['w'])
    from .missions import travel_days
    m = mission(game, s, 'winter', f'Winter {gd["name"].lower()} for {o.name}',
                f'{o.name} lies far out, at the end of a long road, and winter comes early there. Bring them {q} {gd["name"]} '
                f'before the snow closes the road. The goods you buy yourself; we pay well for them.',
                gd['base'] * q * 1.1 + n * .8 + 15, (8, 12), game.day + travel_days(n) + 6, good=g, qty=q)
    m.target = o.id
    return m


def _gather(game, s):
    from . import foraging as FG
    n = random.randint(4, 8)
    known = [k for k, v in FG.PLANTS.items() if v[1] == 'herb']
    if not known:
        return None
    return mission(game, s, 'gather', f'Gather {n} herbs for the alchemists',
                   f'The Guild needs {n} healing and working herbs, picked fresh, and nobody here has the time to go out and pick '
                   f'them. Any herb will do, as long as it is an herb.', 10 + n * 3, (4, 8), game.day + 12, n=n)


def _starfall(game, s):
    st = star(game)
    sd = next_starfall(game.day)
    fresh = st and not st.get('taken') and game.day - st['day'] <= 6
    if not fresh and (sd is None or sd - game.day > 30):
        return None
    if taken(game, 'starfall', 1):
        return None
    when = 'Last night a star came down whole' if fresh else \
        'On the night of the 12th of Emberwane the sky rains stars, and every year one of them comes down whole'
    return mission(game, s, 'starfall', 'The Starfall: star-iron for the Circle',
                   f'{when}. Be the first to reach it, and bring the Circle its star-iron. Others will be looking too, and they '
                   f'will not wait for you.', 45, (8, 12), (st['day'] if fresh else sd) + 8, starfall=1)


def _festival(game, s):
    fd, fname = next_festival(game.day)
    if not 1 <= fd - game.day <= 12 or taken(game, 'festival', s.id):
        return None
    return mission(game, s, 'festival', f'{cap(fname)} in {s.name}',
                   f'{s.name} keeps {fname} on {CAL.short(fd)}. The innkeeper needs strong arms for the tables, and a few brave '
                   f'fools for the contests. Be here on the day.', 5, (8, 12), fd, festival=s.id, day=fd, fest=fname)


def _desecrate(game, s):
    w = game.world
    qs = [q for q in w.pois if q.kind == 'shrine' and getattr(q, 'god', None) != 'morrak' and 15 <= cheb(q.x, q.y, s.x, s.y) <= 80
          and not getattr(q, 'defiled', False) and not taken(game, 'poi', q.id)]
    if not qs:
        return None
    q = random.choice(qs)
    m = mission(game, s, 'desecrate', f'Foul {q.name}',
                f'Go to {q.name}, to the {_dir(s, q.x, q.y)}. Put out the candles, foul the stone, and scratch the name of its '
                f'god away. Morrak wants it, and Morrak is patient only with his own.', 30, (4, 8),
                spot=[q.x, q.y], poi=q.id, where=q.name)
    m.dark = 'desecration'
    return m


def _person(game, s):
    from .missions import travel_days
    cands = _towns_by_road(game, s, 20, 100)
    if not cands:
        return None
    o, n = random.choice(cands)
    from .wanderers import road_path
    path = road_path(game, s.id, o.id)
    danger = max(game.world.region_at(x, y).danger for x, y in path)
    name = name_of(game)
    who = random.choice(['a pilgrim', 'a pilgrim', 'a merchant', 'a scholar', 'a widow with a dowry chest'])
    from . import missions as MS
    m = MS.Mission(game.new_id(), 'escort', s.id)
    m.target = o.id
    m.reward = round(30 + n * 1.2 + danger * 10) * 20
    m.deadline = game.day + travel_days(n) + 4
    m.data = dict(hp=24 + 6 * danger, danger=danger, person=name, who=who)
    m.title = f'Escort {name} to {o.name}'
    m.desc = (f'{name}, {who}, must reach {o.name} ({n} leagues) before {CAL.short(m.deadline)}, and will not walk the road '
              f'alone. {name} walks with you, and can die; keep them alive when the road turns ugly.')
    m.rep = random.randint(5, 10)
    m.faction = s.faction
    return m


def _rival(game, s):
    from . import named as NM
    mi = NM.offer(game, s, 'beast', 1)
    if not mi:
        return None
    n = NM.get(game, mi.data['nid'])
    r = random.choice(RIVALS)
    mi.data['rival'] = dict(name=r, left=random.randint(7, 12), state='racing')
    mi.desc += f' Word is that {r}, a bounty hunter, is after {n.him()} too. Be faster.'
    return mi


def _legend(game, s):
    from . import named as NM
    n = NM.make(game, s.x, s.y, 'beast', 'legendary')
    if not n:
        return None
    NM.report(game, n, age=1)
    return NM.hunt_mission(game, n, s.id)


MAKE = {'nest': _nest, 'harvest': _harvest, 'missing': _missing, 'defend': _defend, 'rescue': _rescue, 'well': _well,
        'shrine': _shrine, 'boats': _boats, 'bigone': _bigone, 'deep': _deep, 'rush': _rush, 'debt': _debt, 'cargo': _cargo,
        'smuggle': _smuggle, 'spy': _spy, 'deserter': _deserter, 'pilgrim': _pilgrim, 'relic': _relic, 'survey': _survey,
        'lostway': _lostway, 'winter': _winter, 'gather': _gather, 'starfall': _starfall, 'festival': _festival,
        'desecrate': _desecrate, 'person': _person, 'rival': _rival, 'legend': _legend}


def flavour(game, key, m):
    """A guild's own way with the work."""
    if key == 'thieves' and m.kind == 'debt':
        m.data['thieves'] = True
        m.desc = m.desc.replace('owes the Guild', 'owes us').replace('How you collect it is your business.',
                                                                    'Collect it our way. People should be afraid not to pay us.')
    elif key == 'coven' and m.kind == 'relic':
        m.title = m.title.replace('Recover', 'Steal')
        m.desc = m.desc.replace('Bring it home to', 'Bring it to us, in') + ' Morrak will enjoy it.'
        m.dark = 'desecration'


# ------------------------------------------------------------------ taking the job
def can_accept(game, m):
    from .economy import free_cargo
    p = game.player
    if m.kind in ('smuggle', 'pilgrim', 'alms') and free_cargo(p) < 1:
        game.msg('You need 1 free cargo space for this job.', 'bad')
        return False
    if m.kind == 'relic' and game.world.dungeons[m.data['dungeon']].relic is not None:
        game.msg('Someone else went after that relic already.', 'bad')
        return False
    return True


def on_accept(game, s, m):
    from . import missions as MS
    w, p = game.world, game.player
    d = m.data
    if d.get('did') is not None and m.kind in ('nest', 'deep'):
        dg = w.dungeons[d['did']]
        game.reveal_place(dg.x, dg.y)
    if d.get('poi') is not None:
        from .events import reveal
        reveal(game, w.pois[d['poi']])
    if m.target is not None:
        t = w.settlements[m.target]
        game.reveal_place(t.x, t.y)
    if d.get('spot') and m.kind not in ('survey', 'missing'):
        game.reveal_place(*d['spot'])
    if d.get('camp') is not None:
        st = w.sites[d['camp']]
        game.reveal_place(st.x, st.y)
    if m.kind == 'spy':
        h = w.holds[d['hold_t']]
        game.reveal_place(h.x, h.y)
    if m.kind == 'smuggle':
        p.parcels.append(dict(mid=m.id, name=cap(d['contraband']), w=1))
    elif m.kind == 'pilgrim':
        p.parcels.append(dict(mid=m.id, name=f'an offering for {w.pois[d["poi"]].name}', w=1))
    elif m.kind == 'alms':
        p.parcels.append(dict(mid=m.id, name=f'the temple\'s bread for {w.sites[d["site"]].name}', w=1))
    elif m.kind == 'relic':
        dg = w.dungeons[d['dungeon']]
        dg.relic = m.id
        key = f'{dg.id}:{dg.depth}'
        if key in game.maps:
            MS.place_relic(game, game.maps[key], m)
    elif m.kind == 'lostway':
        from . import hidden as HP
        wy = w.ways[d['way']]
        HP.discover_way(game, wy.id, 'The chart shows where it leaves the land you know.', HP.stretch(wy, 0, .2))
    elif m.kind == 'missing':
        ax, ay, r = d['area']
        game.reveal_place(ax, ay)


# ------------------------------------------------------------------ out in the land
def step(game):
    """A step on the overworld: places the jobs send you to, tracks of the missing, rivals, and the fallen star."""
    if game.cur != 'over' or game.pending:
        return False
    from . import missions as MS
    p = game.player
    for m in MS.active(game):
        d = m.data
        if m.kind in KINDS and m.state == 'active':
            spot = d.get('spot')
            if spot and not d.get('reached') and game.turn >= d.get('cool', 0) and cheb(p.x, p.y, *spot) <= d.get('reach', 1):
                fn = ARRIVE.get(m.kind)
                if fn and fn(game, m):
                    return True
            if m.kind == 'missing' and not d.get('reached'):
                track(game, m)
        elif m.kind == 'hunt' and m.state == 'active' and d.get('rival', {}).get('state') == 'racing':
            if rival_meet(game, m):
                return True
    st = star(game)
    if st and not st.get('taken'):
        if cheb(p.x, p.y, st['x'], st['y']) <= 1:
            find_star(game, st)
            return True
        if cheb(p.x, p.y, st['x'], st['y']) <= st['r'] and random.random() < .15:
            star_sign(game, st)
    return False


def fight(game, m, keys, lvl, elite=0, intro=None, then=None, terrain=None):
    """A fight for a job, on a battle map. How it ends is handled in after_fight."""
    if game.cur != 'over':
        game.leave_to_over()
    p = game.player
    om = game.maps['over']
    t = terrain if terrain is not None else om.tile(p.x, p.y)
    game.start_encounter(None, t, lvl, keys, elite, intro='')
    game.job_fight = (m.id, then or m.kind)
    wild = game.fight_map()
    leader = m.data.get('leader')
    if wild and leader:
        boss = next((o for o in wild.mons if not o.is_npc), None)
        if boss:
            boss.name, boss.fg = leader, D.UNIQUE_FG
    if intro:
        game.msg(intro, 'bad')
    game.msg(game.escape_hint())
    return True


def after_fight(game, wild):
    """The battle map is left: did the job's fight end in victory?"""
    from . import missions as MS
    jf = getattr(game, 'job_fight', None)
    game.job_fight = None
    if not jf:
        return
    mid, then = jf
    m = MS.find(game, mid)
    if not m or m.state not in ('active', 'turnin'):
        return
    won = wild is not None and not any(not o.is_npc for o in wild.mons)
    fn = WON.get(then)
    if fn:
        fn(game, m, won)


def _turnin(game, m, text):
    from . import missions as MS
    m.state = 'turnin'
    m.data['reached'] = True
    game.msg(f'{text} Return to {MS.giver_name(game, m)} for your reward.', 'gold')


def _won_simple(game, m, won):
    if not won:
        m.data['cool'] = game.turn + 60
        return
    text = {'nest': 'The nest is burned out.', 'harvest': 'The fields are safe again.',
            'shrine': 'The shrine is yours again. Someone will light the candles.',
            'boats': f'So it was {m.data.get("cause", "that")}. It will take no more boats.'}.get(m.kind, 'It is done.')
    if m.kind == 'shrine':
        q = game.world.pois[m.data['poi']]
        q.ready_day = 0
    _turnin(game, m, text)


def _arrive_fight(game, m):
    d = m.data
    if d.get('poi') is not None and m.kind in ('rescue', 'cargo'):
        game.encounter_poi = d['poi']
    fight(game, m, d['keys'], d['lvl'], 1 if m.kind in ('rescue', 'cargo') else 0, d.get('intro'))
    if d.get('poi') is not None and m.kind in ('rescue', 'cargo'):
        from .events import chest
        chest(game, d['lvl'], 1)
    return True


def _won_rescue(game, m, won):
    if not won:
        m.data['cool'] = game.turn + 60
        return
    d = m.data
    _turnin(game, m, f'You cut {d["name"]} loose. {he(d["his"]).capitalize()} is weak, but alive, and makes for home.')


def _won_cargo(game, m, won):
    if not won:
        m.data['cool'] = game.turn + 60
        return
    d = m.data
    d['reached'] = True
    gd = D.GOODS[d['good']]
    ask_later(game, 'jb_cargo', 'The stolen wagon', f'The wagon is still loaded: {d["qty"]} {gd["name"]}, hardly touched. It would '
           f'fetch a good price in any market, and nobody but you knows the outlaws are dead.',
           [(f'Bring it back to {game.world.settlements[m.giver].name}', 'back'), ('Keep it and sell it yourself', 'keep')], mid=m.id)


def r_cargo(game, choice, ctx):
    from . import missions as MS
    m = MS.find(game, ctx['mid'])
    if not m or m.state != 'active':
        return
    d = m.data
    gd = D.GOODS[d['good']]
    p = game.player
    if choice == 'keep':
        p.cargo[d['good']] = p.cargo.get(d['good'], 0) + d['qty']
        p.cost_basis.setdefault(d['good'], 0)
        MS.fail(game, m, f'You kept the {gd["name"].lower()}.')
        effects(game, faction=[(m.faction, -3)], god=('valdric', -3))
        return
    p.parcels.append(dict(mid=m.id, name=f'{d["qty"]} {gd["name"]} (recovered)', w=0))
    _turnin(game, m, 'You take the wagon by the reins.')


def track(game, m):
    """In the search area for someone who is missing: tracks, and the area shrinks."""
    from . import lifeskills as LS
    from .engine import dir_name
    p = game.player
    d = m.data
    ax, ay, r = d['area']
    if cheb(p.x, p.y, ax, ay) > r:
        return
    c = .08 + .015 * LS.rank(game, 'foraging')
    if random.random() >= c:
        return
    sx, sy = d['spot']
    what = random.choice(['a footprint in the mud, small and bare', 'a scrap of homespun cloth on a thorn', 'a cold campfire, '
                          'just a few sticks', 'a dropped sling and a few stones', 'a name scratched on a tree, and an arrow'])
    game.msg(f'You find {what}. The trail leads {dir_name(sx - p.x, sy - p.y)}.', 'info')
    d['area'] = [(sx + p.x) // 2 + random.randint(-1, 1), (sy + p.y) // 2 + random.randint(-1, 1), max(3, int(r * .6))]


def _arrive_missing(game, m):
    from . import events as EV
    d = m.data
    d['reached'] = True
    late = (game.day - d['since']) / 4
    r = random.random() + late * .15
    name, his = d['name'], d['his']
    if r < .55:
        if random.random() < .35:
            lvl = game.world.danger_at(*d['spot']) + 1
            d['outcome'] = 'alive'
            return fight(game, m, ['wolf'] * random.randint(2, 4), lvl, 0,
                         f'You hear a thin voice from up a tree. {name} is there, and wolves are circling under it!', 'missing')
        d['outcome'] = 'alive'
        _turnin(game, m, f'You find {name} in a hollow under the roots, cold and starving, but alive. {he(his).capitalize()} '
                f'walks home with you.')
    elif r < .85:
        d['outcome'] = 'wounded'
        EV.ask(game, 'jb_missing', name, f'You find {name} at the bottom of a gully, {his} leg broken and {his} lips blue with '
               f'cold. {he(his).capitalize()} cannot walk.',
               [(f'Carry {him(his)} home on your back (it will take half a day)', 'carry'),
                ('Make a fire, and go for help', 'help')], mid=m.id)
    else:
        d['outcome'] = 'dead'
        keep = random.choice(KEEPSAKE)
        d['keepsake'] = keep
        _turnin(game, m, f'You find {name} too late. You cover {him(his)} with stones, and take {keep} for the family.')
    return True


def _won_missing(game, m, won):
    d = m.data
    if not won:
        d['outcome'] = 'dead'
        d['keepsake'] = random.choice(KEEPSAKE)
        _turnin(game, m, f'When you come back, the wolves have been at the tree. You take {d["keepsake"]} for the family.')
        return
    _turnin(game, m, f'{d["name"]} climbs down, shaking, and walks home with you.')


def r_missing(game, choice, ctx):
    from . import missions as MS
    m = MS.find(game, ctx['mid'])
    if not m:
        return
    d = m.data
    if choice == 'carry':
        game.end_turn(D.DAY_LEN // 2, True)
        d['outcome'] = 'alive'
        _turnin(game, m, f'Half a day of hard walking with {d["name"]} on your back. Your legs are shaking, but you are on the way home.')
    else:
        d['outcome'] = 'help'
        _turnin(game, m, 'You build a fire, leave your waterskin, and mark the way.')


def _won_well(game, m, won):
    if not won:
        m.data['cool'] = game.turn + 60
        return
    v = game.world.settlements[m.data['village']]
    _turnin(game, m, f'The well of {v.name} will run clean again.')


def _arrive_poisoner(game, m):
    d = m.data
    keys = ['weald_hag'] if d['lvl'] >= 5 else ['cultist', 'cultist']
    return fight(game, m, keys, d['lvl'], 1, 'In a hut of sticks and bones, someone is grinding something grey into a pot.', 'well')


def _arrive_shrine_job(game, m):
    """Pilgrimage and desecration: at the shrine, a choice or an offering."""
    from . import events as EV
    d = m.data
    q = game.world.pois[d['poi']]
    p = game.player
    if m.kind == 'pilgrim':
        d['reached'] = True
        p.parcels = [pc for pc in p.parcels if pc['mid'] != m.id]
        from .events import reveal
        reveal(game, q)
        q.ready_day = 0
        effects(game, god=(d.get('god'), 6), quiet=True)
        _turnin(game, m, f'You lay the offering on the stone of {q.name} and say the old words.')
        game.gain_xp(15 + game.world.danger_at(q.x, q.y) * 4)
        return True
    EV.ask(game, 'jb_desecrate', q.name, f'{q.name}: candles, flowers left by someone this morning, a stone worn smooth by the '
           f'hands of pilgrims. Nobody is about.', [('Defile it', 'defile'), ('Leave it be', 'leave')], mid=m.id)
    return True


def r_desecrate(game, choice, ctx):
    from . import missions as MS
    m = MS.find(game, ctx['mid'])
    if not m or choice != 'defile':
        if m:
            m.data['cool'] = game.turn + 60
        return
    q = game.world.pois[m.data['poi']]
    q.defiled = True
    q.ready_day = 10 ** 9
    effects(game, crime=(8, 'the defiling of a shrine', .25))
    _turnin(game, m, f'The candles are out and the stone is foul. {q.name} is a shrine no more.')


def _arrive_spy(game, m):
    from . import events as EV
    h = game.world.holds[m.data['hold_t']]
    EV.ask(game, 'jb_spy', h.title, f'{h.title} rises against the sky, banners on its towers. Sentries walk the walls; carts go in '
           f'and out of the gate.', [('Lie in the grass and watch until dark', 'watch'), ('Walk in with the carts, as a carter', 'walk'),
                                     ('Not now', 'leave')], mid=m.id)
    return True


def r_spy(game, choice, ctx):
    from . import missions as MS
    from . import towns as TW
    m = MS.find(game, ctx['mid'])
    if not m or choice == 'leave':
        if m:
            m.data['cool'] = game.turn + 60
        return
    h = game.world.holds[m.data['hold_t']]
    p = game.player
    if choice == 'watch':
        game.end_turn(D.DAY_LEN // 3, True)
        risk = .2 if TW.is_night(game) else .3
    else:
        risk = .15 if p.rep.get(h.faction, 0) > -10 else .6
    if p.race in ('halfling', 'goblin'):
        risk *= .7
    if random.random() < risk:
        troops = D.FACTIONS[h.faction]['troops']
        m.data['seen'] = True
        fight(game, m, [random.choice(troops) for _ in range(3)], game.world.danger_at(h.x, h.y) + 3, 0,
              '"Spy!" A sentry has seen you. Riders come out of the gate.', 'spy')
        return
    m.data['count'] = h.garrison
    _turnin(game, m, f'You count {h.garrison} men on the walls and note when the guard changes.')


def _won_spy(game, m, won):
    from .war import change_rep
    h = game.world.holds[m.data['hold_t']]
    change_rep(game, h.faction, -4)
    if won:
        _turnin(game, m, f'They will not report you. You got a good look at {h.title}.')
    else:
        m.data['cool'] = game.turn + 60


def _arrive_deserter(game, m):
    from . import events as EV
    d = m.data
    v = game.world.settlements[d['village']]
    f = D.FACTIONS[m.faction]['short'] if m.faction else 'army'
    EV.ask(game, 'jb_deserter', d['name'], f'{d["name"]} is barely more than a boy. He has torn the {f} badge off his coat and is '
           f'sitting by a fire too small to warm anyone. He does not run. "They hang deserters," he says. "My mother is in '
           f'{v.name}. Please."', [('Take him back in chains', 'take'), ('Let him go home', 'free')], mid=m.id)
    return True


def r_deserter(game, choice, ctx):
    from . import missions as MS
    m = MS.find(game, ctx['mid'])
    if not m:
        return
    d = m.data
    if choice == 'take':
        d['taken'] = True
        game.player.parcels.append(dict(mid=m.id, name=f'{d["name"]}, in chains', w=0))
        effects(game, town=[(d['village'], -6)], god=('solmara', -2))
        _turnin(game, m, f'{d["name"]} holds out his wrists without a word.')
    else:
        d['reached'] = True
        MS.fail(game, m, f'{d["name"].split()[0]} goes home.')
        effects(game, town=[(d['village'], 6)], faction=[(m.faction, -3)] if random.random() < .5 else [], god=('solmara', 3))


def _arrive_survey(game, m):
    x, y = m.data['spot']
    om = game.maps['over']
    for yy in range(y - 6, y + 7):
        for xx in range(x - 9, x + 10):
            if om.inb(xx, yy):
                om.seen[yy * om.w + xx] = 1
    game.gain_xp(10)
    _turnin(game, m, 'You take your bearings from the hills and sketch the lie of the land.')
    return False


def _arrive_lostway(game, m):
    from . import hidden as HP
    wy = game.world.ways[m.data['way']]
    HP.discover_way(game, wy.id, None, wy.cells)
    game.gain_xp(20)
    _turnin(game, m, f'{wy.name} ends here.')
    return False


def _arrive_bigone(game, m):
    if not m.data.get('told'):
        m.data['told'] = True
        game.msg(f'This is the water where {m.data["fish"].split(",")[0]} lives. It bites only {m.data["when"]}.', 'info')
    return False


def big_bite(game, water):
    """Fishing where the big one lives, when it bites: True if it takes the bait."""
    from . import missions as MS
    from . import towns as TW
    from . import weather as WX
    if game.map.kind != 'over':
        return False
    p = game.player
    for m in MS.active(game):
        d = m.data
        if m.kind != 'bigone' or m.state != 'active' or cheb(p.x, p.y, *d['spot']) > d.get('reach', 6):
            continue
        cond = d['cond']
        ok = (cond == 'rain' and WX.KINDS.get(WX.current(game), ('', ''))[1] == 'rain') or \
             (cond == 'night' and TW.is_night(game)) or (cond == 'season' and CAL.season(game.day) == d['season'])
        if ok and random.random() < .35:
            game.fishing_job = m.id
            return True
    return False


def landed(game):
    """The big one is in."""
    from . import missions as MS
    from .entities import Item
    m = MS.find(game, getattr(game, 'fishing_job', None))
    game.fishing_job = None
    if not m or m.state != 'active':
        game.msg('Something enormous rolls in the water, and is gone.')
        return
    it = Item(game.new_id(), 'quest', 'legend')
    it.name = m.data['fish'].split(',')[0]
    it.name = it.name[0].upper() + it.name[1:]
    it.mission = m.id
    if not game.add_to_inv(it):
        game.msg('You have it on the bank, but your pack is too full to carry it. It flops back into the water.', 'bad')
        return
    game.msg(f'{it.name}! It is as long as you are tall, and older than anyone who ever fished for it.', 'unique')
    _turnin(game, m, 'The Brotherhood will want to see this.')


def _arrive_name(game, m):
    d = m.data
    return fight(game, m, d['keys'], d['lvl'], 1, f'{d["leader"]} sees you coming and knows why. "So they sent you."', 'name')


def _won_name(game, m, won):
    if not won:
        m.data['cool'] = game.turn + 60
        return
    _turnin(game, m, f'{m.data["leader"]} is dead. The reeve will be glad to hang the rest on a dead man.')


def _arrive_mercdebt(game, m):
    d = m.data
    return fight(game, m, d['keys'], d['lvl'], 0, f'"There he is!" {d["creditor"]}\'s men spread out across the road.', 'mercdebt')


def _won_mercdebt(game, m, won):
    from . import missions as MS
    from . import mercs as MC
    mc = MC.get(game, 'merc')
    if not won:
        m.data['cool'] = game.turn + 60
        return
    MS.complete(game, m, [])
    if mc:
        effects(game, loyalty=35)
        game.msg(f'{mc.name}: "That is the end of it, then. I will not forget this."', 'talk')


ARRIVE = {'nest': _arrive_fight, 'harvest': _arrive_fight, 'rescue': _arrive_fight, 'shrine': _arrive_fight,
          'boats': _arrive_fight, 'cargo': _arrive_fight, 'missing': _arrive_missing, 'well': _arrive_poisoner,
          'pilgrim': _arrive_shrine_job, 'desecrate': _arrive_shrine_job, 'spy': _arrive_spy, 'deserter': _arrive_deserter,
          'survey': _arrive_survey, 'lostway': _arrive_lostway, 'bigone': _arrive_bigone, 'name': _arrive_name,
          'mercdebt': _arrive_mercdebt}
WON = {'nest': _won_simple, 'harvest': _won_simple, 'shrine': _won_simple, 'boats': _won_simple, 'rescue': _won_rescue,
       'cargo': _won_cargo, 'missing': _won_missing, 'well': _won_well, 'spy': _won_spy, 'name': _won_name,
       'mercdebt': _won_mercdebt, 'defend': lambda g, m, won: _won_defend(g, m, won)}


# ------------------------------------------------------------------ in the dungeons
def on_kill(game, mon):
    from . import missions as MS
    did = getattr(game.map, 'did', None)
    w = game.world
    if did is not None and w.dungeons.get(did) is not None and w.dungeons[did].tag in NEST_TAGS and mon.k == w.dungeons[did].boss:
        w.__dict__.setdefault('nests_cleared', set()).add(did)
        for m in MS.active(game):
            if m.kind == 'nest' and m.state == 'active' and m.data.get('did') == did:
                _turnin(game, m, f'The {mon.name.lower()} is dead, and the nest dies with it.')


def on_level(game, did, depth):
    from . import missions as MS
    dg = game.world.dungeons[did]
    if depth != dg.depth:
        return
    for m in MS.active(game):
        if m.kind == 'deep' and m.state == 'active' and m.data.get('deep') == did:
            _turnin(game, m, f'This is the deepest level of {the(dg.name)}. You draw what you can see by the light of your eyes.')


# ------------------------------------------------------------------ in the towns
def on_enter(game, sid):
    """You walk into a settlement: deliveries, debts, the well, the gate, hand-ins. One question at a time."""
    from . import missions as MS
    from . import crime as CR
    p = game.player
    w = game.world
    s = w.settlements[sid]
    for m in MS.active(game):
        if m.kind not in KINDS:
            continue
        d = m.data
        if m.state == 'turnin' and m.giver == sid and m.hold is None:
            MS.complete(game, m, [sid] + ([m.target] if m.target is not None and m.target != sid else []))
            continue
        if m.state != 'active':
            continue
        if m.kind in ('rush', 'winter') and m.target == sid:
            g, q = d['good'], d['qty']
            if p.cargo.get(g, 0) >= q:
                p.cargo[g] -= q
                if not p.cargo[g]:
                    del p.cargo[g]
                    p.cost_basis.pop(g, None)
                game.msg(f"{s.name} takes the {q} {D.GOODS[g]['name']} with open arms.", 'good')
                MS.complete(game, m, [m.giver, sid])
            else:
                game.msg(f"{s.name} still waits for {q} {D.GOODS[g]['name']} (you carry {p.cargo.get(g, 0)}).", 'info')
        elif m.kind == 'gather' and m.giver == sid:
            have = herbs(game)
            if sum(it.n for it in have) >= d['n']:
                take_herbs(game, d['n'])
                MS.complete(game, m, [sid])
            else:
                game.msg(f"The alchemists still wait for {d['n']} herbs (you carry {sum(it.n for it in have)}).", 'info')
        elif m.kind == 'starfall' and m.giver == sid and m.hold is None:
            it = next((i for i in p.inv if i.k == 'star'), None)
            if it:
                p.inv.remove(it)
                game.msg('The Magi turn the star-iron over in their hands like a newborn child.', 'unique')
                MS.complete(game, m, [sid])
        elif s.rep <= CR.WANTED_AT:
            continue
        elif m.kind == 'debt' and m.target == sid and not game.pending:
            opts = []
            if p.gold >= d['amount']:
                opts.append((f'Pay the debt for him ({fmt(d["amount"])})', 'pay'))
            opts += [('Lean on him until he pays', 'threat'), ('Let it go', 'free')]
            ask_later(game, 'jb_debt', d['debtor'], f'{d["debtor"]} is behind his counter, in a shop half empty. Three children watch '
                   f'you from the stairs. "I have nothing," he says. "The winter took it all. I will pay, I swear it, only not now."',
                   opts, mid=m.id)
            return
        elif m.kind == 'well' and m.target == sid and not game.pending and not d.get('known'):
            ask_later(game, 'jb_well', f'The well of {s.name}', 'The well stands on the green, a bucket on a rope beside it. The water '
                   'smells of something sweet and wrong.', [('Climb down the well and look', 'climb'), ('Ask the villagers what changed', 'ask'),
                                                            ('Not now', 'leave')], mid=m.id)
            return
        elif m.kind == 'well' and m.target == sid and d.get('cause') == 'roots' and d.get('known'):
            if p.cargo.get('medicine', 0) >= 3:
                p.cargo['medicine'] -= 3
                if not p.cargo['medicine']:
                    del p.cargo['medicine']
                    p.cost_basis.pop('medicine', None)
                _turnin(game, m, 'The healer boils the medicine into the well. By morning the water is clean.')
            else:
                game.msg(f'The healer of {s.name} still needs 3 Medicine for the well.', 'info')
        elif m.kind == 'smuggle' and m.target == sid and not game.pending:
            opts = [('Walk through with a straight face', 'walk')]
            if p.gold >= d['bribe']:
                opts.append((f'Slip the sergeant a coin ({fmt(d["bribe"])})', 'bribe'))
            opts.append(('Turn back for now', 'back'))
            ask_later(game, 'jb_gate', f'The gate of {s.name}', 'The guards are going through every cart and every pack at the gate. '
                   'Yours is next.', opts, mid=m.id, sid=sid)
            return
        elif m.kind == 'festival' and d['festival'] == sid and game.day == d['day']:
            due(game, 'festival', m.id)
            return


def herbs(game):
    from . import foraging as FG
    return [it for it in game.player.inv if it.k == 'plant' and FG.PLANTS.get(it.t, ('', ''))[1] == 'herb']


def take_herbs(game, n):
    for it in herbs(game):
        while n and it in game.player.inv:
            game.remove_one(it)
            n -= 1
        if not n:
            return


def r_debt(game, choice, ctx):
    from . import missions as MS
    m = MS.find(game, ctx['mid'])
    if not m or m.state != 'active':
        return
    d = m.data
    p = game.player
    if choice == 'pay':
        p.gold -= d['amount']
        d['how'] = 'paid'
        effects(game, town=[(m.target, 8)], god=('solmara', 3))
        _turnin(game, m, 'You count out the coins for him. He cannot look at you.')
    elif choice == 'threat':
        d['how'] = 'threat'
        if d.get('thieves'):
            effects(game, town=[(m.target, -8)], crime=(4, 'extortion', .5))
            m.reward = round(m.reward * 1.5)
        else:
            effects(game, town=[(m.target, -5)])
        _turnin(game, m, 'He finds the coins in the end. They always do.')
    else:
        d['reached'] = True
        MS.fail(game, m, 'You let the debt go.')
        effects(game, town=[(m.target, 5)], god=('solmara', 2))


def r_well(game, choice, ctx):
    from . import missions as MS
    m = MS.find(game, ctx['mid'])
    if not m or choice == 'leave':
        return
    d = m.data
    v = game.world.settlements[d['village']]
    d['known'] = True
    if d['cause'] == 'drowned':
        if choice == 'ask':
            game.msg('"A peddler fell down it at midsummer," says an old woman. "We never got him out."', 'talk')
        game.msg('Something at the bottom of the well is not lying still. It is climbing.', 'bad')
        d['lvl'] = game.world.danger_at(v.x, v.y) + 2
        fight(game, m, ['drowned'] * random.randint(2, 3), d['lvl'], 0, 'The dead come up out of the well, dripping!',
              'well', terrain=D.GRASS)
    elif d['cause'] == 'poisoner':
        spot = _spot(game, v.x, v.y, 5, 14)
        if not spot:
            spot = (v.x + 6, v.y)
        d['spot'], d['lvl'] = list(spot), game.world.danger_at(*spot) + 2
        game.reveal_place(*spot)
        game.msg(f'{"At the bottom: a bundle of grey roots and bones, tied with hair." if choice == "climb" else "The goose-girl saw a woman at the well at night."} '
                 f'Somebody is poisoning it, and the tracks lead to the {_dir(v, *spot)}.', 'info')
    else:
        game.msg('The water seeps in through roots gone bad, black and soft. The healer says three Medicine boiled into the well '
                 'would clean it.', 'info')


def r_gate(game, choice, ctx):
    from . import missions as MS
    m = MS.find(game, ctx['mid'])
    if not m or m.state != 'active':
        return
    d = m.data
    p = game.player
    if choice == 'back':
        game.leave_to_over()
        return
    if choice == 'bribe':
        p.gold -= d['bribe']
        ok = random.random() < .85
    else:
        ok = random.random() < .5 + (.15 if getattr(p, 'god', None) == 'skell' else 0) + (.1 if p.race == 'halfling' else 0)
    if ok:
        game.msg('The guards wave you through. The man at the sign of the crossed keys takes the parcel without a word.', 'good')
        MS.complete(game, m, [])
        return
    p.parcels = [pc for pc in p.parcels if pc['mid'] != m.id]
    d['reached'] = True
    MS.fail(game, m, f'The guards find {d["contraband"]}.')
    effects(game, crime=(10, 'smuggling', 1.0))


def festival(game, m):
    from . import events as EV
    d = m.data
    d['reached'] = True
    EV.ask(game, 'jb_fest', cap(d['fest']), 'Bunting over the green, a pig on a spit, fiddles and drums. The tables are set and '
           'the contests are about to begin. The innkeeper puts a tankard in your hand. "Well? Which one?"',
           [('The tug-of-war (Strength)', 'str'), ('The archery butts (Dexterity)', 'dex'),
            ('The pie and ale table (Vitality)', 'vit'), ('Tell a tale by the fire (Energy)', 'ene')], mid=m.id)


def r_fest(game, choice, ctx):
    from . import missions as MS
    m = MS.find(game, ctx['mid'])
    if not m or m.state != 'active':
        return
    p = game.player
    v = getattr(p, choice, 10)
    win = random.random() < max(.15, min(.85, .3 + (v - 15) * .02))
    what = {'str': ('Your side drags the other into the mud.', 'The rope burns through your hands, and you go into the mud.'),
            'dex': ('Three arrows in the gold. The crowd roars.', 'Your last arrow takes the hat off the miller. They laugh for an hour.'),
            'vit': ('Seven pies and the ale to wash them down. Nobody comes close.', 'Four pies. The blacksmith eats nine.'),
            'ene': ('The whole green goes quiet for your tale, and cheers at the end of it.', 'You lose the thread halfway, '
                    'but they cheer anyway.')}[choice]
    s = game.world.settlements[m.giver]
    if win:
        m.reward += 800
        game.msg(what[0] + ' You win the prize, and a garland.', 'gold')
        effects(game, town=[(s.id, 6)], quiet=True)
    else:
        game.msg(what[1], 'info')
    p.buffs = [b for b in p.buffs if b[0] != 'regen'] + [['regen', 1, 400, 'Festival cheer']]
    MS.complete(game, m, [s.id])


def clear_name(game, s):
    """At the gate, wanted: swear it was someone else, and find someone to prove it on."""
    from . import missions as MS
    if len(MS.active(game)) >= MS.MAX_ACTIVE:
        game.msg(f'You already have {MS.MAX_ACTIVE} jobs. Finish one first.', 'bad')
        return False
    if any(m.kind == 'name' and m.giver == s.id for m in MS.active(game)):
        game.msg('The guards remember: you said you would bring in the real culprit. They are waiting.', 'info')
        return False
    spot = _spot(game, s.x, s.y, 10, 26)
    if not spot:
        return False
    leader = random.choice(D.BANDIT_LEADERS)
    lvl = game.world.danger_at(*spot) + 2
    what = (getattr(s, 'crimes', None) or ['your crimes'])[-1]
    m = mission(game, s, 'name', f'Clear your name in {s.name}',
                f'You swore to the guards of {s.name} that {what} was the work of {leader}, who works the same roads. Bring '
                f'{leader} in, dead, and the reeve will call it {leader}\'s doing. {leader} was last seen to the {_dir(s, *spot)}.',
                10, (0, 0), game.day + 10, spot=list(spot), keys=['bandit', 'bandit', 'brigand'], lvl=lvl, leader=leader,
                reach=1, where=leader)
    m.state = 'active'
    game.missions.append(m)
    game.reveal_place(*spot)
    game.msg(f'Job accepted: {m.title}.', 'gold')
    return True


# ------------------------------------------------------------------ the days
def daily(game):
    from . import missions as MS
    from . import weather as WX
    from . import news as NW
    w = game.world
    for m in MS.active(game):
        d = m.data
        if m.kind == 'defend' and m.state == 'active' and game.day == d['day']:
            v = w.settlements[d['village']]
            if at(game, v):
                due(game, 'defend', m.id)
            else:
                raided(game, m)
        elif m.kind == 'hunt' and m.state == 'active' and d.get('rival', {}).get('state') in ('racing', 'met'):
            rv = d['rival']
            rv['left'] -= 1
            if rv['left'] <= 0:
                from . import named as NM
                n = NM.get(game, d['nid'])
                rv['state'] = 'won'
                if n and n.alive:
                    n.alive = False
                    NW.post(game, 'danger', f'{rv["name"]} brought in the {n.trophy} of {n.full}.', n.x, n.y)
                MS.fail(game, m, f'{rv["name"]} got there first, and took the bounty.')
        elif m.kind == 'festival' and m.state == 'active' and game.day == d['day'] and game.here is not None \
                and game.here.id == d['festival']:
            due(game, 'festival', m.id)
    # the night of the Starfall: one star comes down whole
    if WX.starfall(game.day) and (not star(game) or star(game)['day'] != game.day):
        fall(game)
    st = star(game)
    if st and not st.get('taken') and game.day >= st['rivals']:
        st['taken'] = 'rivals'
        NW.post(game, 'trade', 'Seekers from the cities found the fallen star and carried its iron away.', st['x'], st['y'])
        game.msg('Word reaches you: others found the fallen star first.', 'bad')
        for m in MS.active(game):
            if m.kind == 'starfall' and m.state == 'active' and not any(i.k == 'star' for i in game.player.inv):
                MS.fail(game, m, 'Others found the star first.')
    # a sellsword's old debt
    from . import mercs as MC
    mc = MC.with_you(game, 'merc')
    if mc and mc.kind != 'beast' and mc.morale >= 40 and not getattr(mc, 'debt_told', False) and game.day >= 6 \
            and random.random() < .05:
        mc.debt_told = True
        due(game, 'mercdebt', None)


def due(game, what, mid):
    """Something that must be asked as soon as nothing else is open."""
    q = game.__dict__.setdefault('jb_due', [])
    if (what, mid) not in q:
        q.append((what, mid))


def ask_later(game, key, title, text, options, **ctx):
    """A question to put once the screen in front of it is gone (a town just entered, a battle just left)."""
    game.__dict__.setdefault('jb_due', []).append(('ask', dict(key=key, title=title, text=text, options=options, ctx=ctx)))


def pump(game):
    """Ask what is due, one at a time, when no other question is open."""
    q = game.__dict__.get('jb_due')
    if not q or game.pending or game.dead:
        return
    what, mid = q.pop(0)
    from . import missions as MS
    from . import events as EV
    if what == 'ask':
        EV.ask(game, mid['key'], mid['title'], mid['text'], mid['options'], **mid['ctx'])
        return
    m = MS.find(game, mid) if mid is not None else None
    if what == 'defend' and m and m.state == 'active':
        v = game.world.settlements[m.data['village']]
        EV.ask(game, 'jb_defend', f'The raid on {v.name}', f'Horns on the hill! {cap(m.data["who"])} are coming over the fields of '
               f'{v.name}, torches in their hands. The villagers grab pitchforks and look at you.',
               [(f'Stand with {v.name}', 'fight'), ('Stay out of it', 'leave')], mid=m.id)
    elif what == 'festival' and m and m.state == 'active':
        festival(game, m)
    elif what == 'mercdebt':
        from . import mercs as MC
        mc = MC.with_you(game, 'merc')
        if not mc:
            return
        creditor = f'{random.choice(["Captain", "Master", "Old"])} {random.choice(["Voss", "Harl", "Grimsby", "Tavik", "Odo"])}'
        amount = random.randint(25, 60) * 100
        EV.ask(game, 'jb_mercdebt', mc.name, f'{mc.name} has been quiet all day. At last: "I owe {creditor} {fmt(amount)}. Owed it '
               f'for years. His men are on the road behind us; I saw them at the last inn. I can run, as I always have. Or not."',
               [(f'Pay the debt for him ({fmt(amount)})', 'pay' if game.player.gold >= amount else None)]
               + [('Face his men with him', 'face'), ('It is not my problem', 'refuse')], creditor=creditor, amount=amount)


def r_defend(game, choice, ctx):
    from . import missions as MS
    m = MS.find(game, ctx['mid'])
    if not m or m.state != 'active':
        return
    if choice != 'fight':
        raided(game, m)
        return
    d = m.data
    fight(game, m, d['keys'], d['lvl'], 1, f'{cap(d["who"])} charge, and the villagers charge with you!', 'defend', terrain=D.GRASS)
    wild = game.fight_map()
    if wild:
        from .worldgen import free_around
        from . import mercs as MC
        for x, y in free_around(game, wild, game.player.x, game.player.y, 2)[:2]:
            MC.thrall(game, 'watchman', x, y, 400, 'A villager with a pitchfork', max(1, d['lvl'] - 2))


def _won_defend(game, m, won):
    from . import missions as MS
    v = game.world.settlements[m.data['village']]
    if won:
        game.msg(f'The raiders break and run. {v.name} cheers your name.', 'gold')
        effects(game, town=[(v.id, 10)], quiet=True)
        MS.complete(game, m, [v.id] + ([m.giver] if m.giver is not None and m.giver != v.id else []))
    else:
        raided(game, m)


def raided(game, m):
    from . import missions as MS
    from . import news as NW
    v = game.world.settlements[m.data['village']]
    for g in v.produce:
        v.market[g][0] *= .5
    NW.post(game, 'danger', f'{cap(m.data["who"])} raided {v.name} and burned the barns.', v.x, v.y)
    MS.fail(game, m, f'{cap(m.data["who"])} raided {v.name}.')


def r_mercdebt(game, choice, ctx):
    from . import missions as MS
    from . import mercs as MC
    mc = MC.with_you(game, 'merc')
    if not mc:
        return
    p = game.player
    if choice == 'pay':
        p.gold -= ctx['amount']
        effects(game, loyalty=30)
        game.msg(f'{mc.name}: "I do not know what to say. Nobody ever... thank you."', 'talk')
    elif choice == 'face':
        x, y = pos(game)
        spot = _spot(game, x, y, 3, 8) or (x + 3, y)
        lvl = game.world.danger_at(*spot) + 2
        from .engine import dir_name
        m = mission(game, game.world.settlements[0], 'mercdebt', f"{mc.name}'s old debt",
                    f"{ctx['creditor']}'s men are on the road, to the {dir_name(spot[0] - x, spot[1] - y)}. "
                    f'Face them, with {mc.name}.', 10, (0, 0), game.day + 3,
                    spot=list(spot), keys=['mercenary', 'mercenary', 'bandit'], lvl=lvl, creditor=ctx['creditor'], reach=2,
                    where=f"{ctx['creditor']}'s men")
        m.giver, m.faction = None, None
        m.state = 'active'
        if len(MS.active(game)) >= MS.MAX_ACTIVE:
            game.msg('You have too many jobs to take on this one as well.', 'bad')
            return
        game.missions.append(m)
        game.reveal_place(*spot)
        game.msg(f'{mc.name} nods slowly, and loosens his sword.', 'talk')
    else:
        effects(game, loyalty=-15)
        game.msg(f'{mc.name} says nothing more about it.', 'talk')


# ------------------------------------------------------------------ the rival hunter
def rival_meet(game, m):
    from . import named as NM
    from . import events as EV
    n = NM.get(game, m.data['nid'])
    if not n or not n.alive or n.did or not NM.in_area(game, n, *pos(game)) or random.random() >= .06:
        return False
    rv = m.data['rival']
    EV.ask(game, 'jb_rival', rv['name'], f'A rider in a bounty hunter\'s leathers sits a tired horse on the track, reading the ground. '
           f'"{rv["name"]}," they say, without getting down. "And you are after {n.full} too, I see. The bounty is not big enough '
           f'for two."', [('Race them to it', 'race'), ('Hunt it together and split the bounty', 'team'),
                          ('Make sure they never get there', 'cross')], mid=m.id)
    rv['state'] = 'met'
    return True


def r_rival(game, choice, ctx):
    from . import missions as MS
    from . import named as NM
    m = MS.find(game, ctx['mid'])
    if not m or m.state != 'active':
        return
    rv = m.data['rival']
    n = NM.get(game, m.data['nid'])
    if choice == 'race':
        game.msg(f'"Then may the faster one win." {rv["name"]} rides off.', 'talk')
    elif choice == 'team':
        rv['state'] = 'team'
        if n:
            NM.report(game, n, r=3)
        game.msg(f'{rv["name"]} shows you where the trail is freshest. "Half and half, then."', 'talk')
    else:
        rv['state'] = 'fight'
        lvl = n.lvl if n else game.player.lvl
        m.data['leader'] = rv['name']
        fight(game, m, ['huntsman', 'mercenary', 'mercenary'], lvl, 1, f'{rv["name"]} draws a long knife. "Like that, is it?"', 'rival')
        m.data.pop('leader', None)


def _won_rival(game, m, won):
    rv = m.data['rival']
    if won:
        rv['state'] = 'gone'
        effects(game, crime=(8, 'the murder of a bounty hunter', .3), god=('valdric', -4))
    else:
        rv['state'] = 'met'
        rv['left'] = max(1, rv['left'] - 2)


WON['rival'] = _won_rival


def on_named_meet(game, n):
    """A rival you hunt with fights at your side."""
    from . import missions as MS
    from . import mercs as MC
    from .worldgen import free_around
    for m in MS.active(game):
        if m.kind == 'hunt' and m.data.get('nid') == n.id and m.data.get('rival', {}).get('state') == 'team':
            sp = free_around(game, game.map, game.player.x, game.player.y, 1)
            if sp:
                MC.thrall(game, 'huntsman', sp[0][0], sp[0][1], 500, m.data['rival']['name'], n.lvl)
                game.msg(f'{m.data["rival"]["name"]} is at your side.', 'good')


# ------------------------------------------------------------------ the Starfall
def fall(game, rare=False):
    from . import news as NW
    from .engine import dir_name
    w = game.world
    om = game.maps['over']
    x0, y0 = pos(game)
    spot = None
    for _ in range(600):
        x, y = x0 + random.randint(-50, 50), y0 + random.randint(-34, 34)
        if om.inb(x, y) and D.TILES[om.tile(x, y)].walk and om.tile(x, y) not in (D.ROAD, D.TOWN, D.CITY) \
                and 14 <= cheb(x, y, x0, y0) and not any(cheb(x, y, s.x, s.y) < 6 for s in w.settlements):
            spot = (x, y)
            break
    if not spot:
        return
    cities = [s for s in w.settlements if s.is_city]
    near = min((cheb(s.x, s.y, *spot) for s in cities), default=60)
    game.star = dict(x=spot[0], y=spot[1], r=8, day=game.day, rivals=game.day + 2 + min(4, near // 18), taken=False,
                     cx=spot[0] + random.randint(-4, 4), cy=spot[1] + random.randint(-4, 4))
    if rare:
        game.msg(f'A star falls in the night, and does not burn out: it comes down whole, far to the '
                 f'{dir_name(spot[0] - x0, spot[1] - y0)}, and the ground shakes.', 'unique')
        NW.post(game, 'trade', 'A star fell on an ordinary night and came down whole. Seekers are on the road.', *spot)
        return
    game.msg(f'The sky rains stars tonight. One of them does not burn out: it comes down whole, far to the '
             f'{dir_name(spot[0] - x0, spot[1] - y0)}, and the ground shakes.', 'unique')
    NW.post(game, 'trade', 'A star came down whole on the night of the Starfall. Every seeker in the realm is on the road.', *spot)


def star_sign(game, st):
    from .engine import dir_name
    p = game.player
    what = random.choice(['scorched trees, all bent the same way', 'a smell of hot iron on the wind', 'glassy black stones in the grass',
                          'a trail of burnt earth'])
    game.msg(f'You see {what}. The star lies {dir_name(st["x"] - p.x, st["y"] - p.y)}.', 'info')
    st['cx'], st['cy'] = (st['x'] + p.x) // 2, (st['y'] + p.y) // 2
    st['r'] = max(3, int(st['r'] * .7))


def find_star(game, st):
    from .entities import Item
    st['taken'] = 'you'
    it = Item(game.new_id(), 'star', 'iron')
    it.name = 'Star-iron'
    if game.add_to_inv(it):
        game.msg('In a crater of steaming earth lies a lump of black iron, still warm, shot through with silver. Star-iron!', 'unique')
    else:
        st['taken'] = False
        game.msg('The star-iron lies here, but your pack is full.', 'bad')


# ------------------------------------------------------------------ what the map and the journal show
def areas(game):
    """Search areas to hatch on the maps: the missing, and the fallen star."""
    from . import missions as MS
    out = []
    for m in MS.active(game):
        if m.kind == 'missing' and m.state == 'active' and not m.data.get('reached'):
            out.append(tuple(m.data['area']))
    st = star(game)
    if st and not st.get('taken'):
        out.append((st['cx'], st['cy'], st['r']))
    return out


def target_pos(game, m):
    """Where this job wants you next, and what to call it."""
    w = game.world
    d = m.data
    if m.kind == 'realm':
        from . import realmjobs as RJ
        return RJ.target_pos(game, m)
    if m.kind == 'spirit':
        from . import aurora as AU
        return AU.target_pos(game, m)
    if m.state == 'turnin' or (m.kind == 'starfall' and any(i.k == 'star' for i in game.player.inv)) or m.kind == 'gather':
        if m.hold is not None:
            h = w.holds[m.hold]
            return (h.x, h.y), h.title
        if m.giver is not None:
            s = w.settlements[m.giver]
            return (s.x, s.y), s.name
    if m.kind == 'missing':
        return (d['area'][0], d['area'][1]), 'the search area'
    if m.kind == 'starfall':
        st = star(game)
        if st and not st.get('taken'):
            return (st['cx'], st['cy']), 'the fallen star'
        s = w.settlements[m.giver]
        return (s.x, s.y), s.name
    if m.kind == 'well' and d.get('spot') and d.get('known'):
        return tuple(d['spot']), 'the poisoner'
    if m.kind in ('nest', 'deep', 'relic') and d.get('did') is not None and not d.get('spot'):
        dg = w.dungeons[d['did']]
        return (dg.x, dg.y), the(dg.name)
    if d.get('spot'):
        return tuple(d['spot']), d.get('where', 'the place')
    if m.kind == 'defend':
        v = w.settlements[d['village']]
        return (v.x, v.y), v.name
    if m.kind == 'festival':
        s = w.settlements[d['festival']]
        return (s.x, s.y), s.name
    if m.target is not None:
        s = w.settlements[m.target]
        return (s.x, s.y), s.name
    if m.giver is not None:
        s = w.settlements[m.giver]
        return (s.x, s.y), s.name
    x, y = pos(game)
    return (x, y), 'here'


def line(game, m):
    """A line for the journal under the job's title."""
    d = m.data
    if m.state == 'turnin':
        return 'Return for your reward.'
    if m.kind == 'missing':
        ax, ay, r = d['area']
        return f'Last seen near {_region(game, ax, ay)} ({r} leagues around). Look for tracks.'
    if m.kind in ('rush', 'winter'):
        g = D.GOODS[d['good']]['name']
        return f"Bring {d['qty']} {g} (you carry {game.player.cargo.get(d['good'], 0)})."
    if m.kind == 'gather':
        return f"Bring {d['n']} herbs (you carry {sum(it.n for it in herbs(game))})."
    if m.kind == 'defend':
        return f"The raid comes on {CAL.short(d['day'])}. Be in {game.world.settlements[d['village']].name} that day."
    if m.kind == 'bigone':
        return f"It bites only {d['when']}. Fish from the bank there."
    if m.kind == 'festival':
        return f"Be in {game.world.settlements[d['festival']].name} on {CAL.short(d['day'])}."
    if m.kind == 'starfall':
        st = star(game)
        return 'The star has fallen. Follow the scorched earth.' if st and not st.get('taken') else \
            'On the night of the 12th of Emberwane, watch the sky.'
    if m.kind == 'well' and d.get('known') and d.get('cause') == 'roots':
        return 'Bring 3 Medicine to the healer.'
    return ''


# ------------------------------------------------------------------ before the pay
def before_complete(game, m):
    """A job ends well: what changes the pay, and what else it leaves behind."""
    d = m.data
    rv = d.get('rival')
    if rv and rv.get('state') == 'team':
        m.reward //= 2
        game.msg(f'You split the bounty with {rv["name"]}, as agreed.', 'info')
    if m.kind == 'missing':
        mult = {'alive': 1.0, 'help': .6, 'wounded': .8, 'dead': .4}.get(d.get('outcome'), 1.0)
        m.reward = round(m.reward * mult)
        if d.get('outcome') == 'dead':
            game.msg(f'You give {d["keepsake"]} to the family. Nobody says anything for a long time.', 'info')
            m.rep //= 2
        elif d.get('outcome') == 'help':
            game.msg(f'The villagers go out with a stretcher and bring {d["name"]} home.', 'info')
    elif m.kind == 'relic' and not getattr(m, 'dark', None):
        effects(game, god=(d.get('god'), 8), quiet=True)
    elif m.kind == 'shrine':
        effects(game, god=4, quiet=True)
    elif m.kind == 'name':
        s = game.world.settlements[m.giver]
        s.rep = max(s.rep, 0)
        s.crimes = []
        game.msg(f'The reeve of {s.name} strikes your name from the list. The crime was {d["leader"]}\'s, says the list now.', 'good')
    elif m.kind == 'deserter':
        effects(game, faction=[(m.faction, 4)], quiet=True)
    elif m.kind == 'debt' and d.get('how') == 'paid':
        game.msg('The Guild gets its money, and never asks where it came from.', 'info')


def on_fail(game, m):
    if m.kind == 'realm':
        from . import realmjobs as RJ
        RJ.on_fail(game, m)
    if m.kind == 'spirit':
        from . import aurora as AU
        AU.on_fail(game, m)
    if m.kind == 'relic':
        dg = game.world.dungeons.get(m.data.get('dungeon'))
        if dg is not None and dg.relic == m.id:
            dg.relic = None


# ------------------------------------------------------------------ the elder of a village
def talk_elder(game, npc):
    from . import news as NW
    NW.offer(game, npc, 'elder', VILLAGE, 1.0, f'"{random.choice(["Sit, sit.", "You look like someone who can handle themselves.", "Trouble never comes alone, they say."])} '
             f'Here is what the village needs:"')


def register():
    from . import events as EV
    EV.RESOLVERS.update(jb_cargo=r_cargo, jb_missing=r_missing, jb_desecrate=r_desecrate, jb_spy=r_spy, jb_deserter=r_deserter,
                        jb_debt=r_debt, jb_well=r_well, jb_gate=r_gate, jb_fest=r_fest, jb_defend=r_defend,
                        jb_mercdebt=r_mercdebt, jb_rival=r_rival)


register()
