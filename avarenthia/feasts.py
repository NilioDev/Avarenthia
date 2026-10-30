"""Round 28: the feast days, the light-feast of the north and the great fair (the Fair of Skell).

Feasts after real ones from all over the world, with names of our own. Not everywhere: each feast belongs to a
region, a people or a faith and is kept only there; Ruin Night and Hearthnight are kept by all humans. A feast shows
where it is kept: its name on the line under the map, the square dressed for it, someone in the square to walk into
(one or two things to do), the townsfolk gathering at evening; it moves a few prices, fairly. The great fair comes to
each human city one week a year: travelling traders all week, a tenth more for what you sell, and more thieves.
What you did at a feast lives on the player (`p.feasts`)."""
import random

from . import data as D
from .worldgen import cheb

# month index (0 Deepfrost .. 11 Longnight), first day, how many days
FEASTS = [
    dict(key='ruin', name='Ruin Night', when=(0, 1, 1), who='humans', fig='A priest by the dark temple door',
         sight='At midnight every light goes out and the bells are still; then the fires are lit again, and it is the new year.',
         deco='°', acts=[('Keep the vigil at the temple until the light comes back', 'vigil:def:8:6:Blessing of the new year')]),
    dict(key='firstfoot', name='First-Footing', when=(0, 1, 1), who='north', fig='A household at its door',
         sight='The first to cross a threshold after midnight brings the luck of the year, with coal and salt in hand.',
         deco='°', acts=[('Knock with coal and salt', 'meal'), ('Ask for the news', 'rumour')]),
    dict(key='shipburn', name='The Ship Burning', when=(0, 14, 1), who='fjord', fig='A torch-bearer of the ship',
         sight='The fjord-folk drag a ship through the village with torches and set it on fire.',
         deco='▲', acts=[('Throw your torch on the ship', 'bless:dmg:4:3:Fire of the ship'), ('Ask who sails in spring', 'rumour')]),
    dict(key='masking', name='The Masking', when=(1, 26, 5), who='heartcity', fig='A mask seller',
         sight='Masks in every street, the world on its head: a Fool King crowned on a barrel rules for a day.',
         deco='♦', prices={'cloth': 1.15, 'wine': 1.15},
         acts=[('Buy a mask (2 silver): nobody knows you in it', 'mask:200'), ('Drink to the Fool King', 'rumour')]),
    dict(key='lean', name='The Lean Month', when=(2, 1, 30), who='heartwest', fig='A friar with a basket of bread',
         sight='No meat in the inns after the Masking: fish and bread are cheap, and the priests watch what you eat.',
         prices={'fish': .8, 'grain': .85, 'furs': 1.05}, acts=[('Take a loaf of the friar\'s bread', 'meal')]),
    dict(key='leaping', name='The Leaping', when=(2, 26, 3), who='steppe', fig='Herders by a fire',
         sight='The herders\' new year: they leap over fires, sweep their tents and make up old quarrels.',
         deco='▲', acts=[('Leap over the fire', 'leap'), ('Make up a quarrel', 'rumour')]),
    dict(key='colour', name='Colour Day', when=(3, 10, 1), who='savanna', fig='Children with bags of powder',
         sight='Everybody throws coloured powder at everybody; old quarrels are forgiven and ranks forgotten.',
         deco='*', acts=[('Throw the powder back', 'bless:crit:3:2:Bright as Colour Day')]),
    dict(key='greening', name='Greening Day', when=(3, 1, 1), who='heartwest', fig='Children with painted eggs',
         sight='The priests of Thessa bless the fields, and children hide painted eggs in the hedges.',
         deco='"', acts=[('Look in the hedges for an egg', 'egg'), ('Walk the fields with the priests', 'bless:regen:1:2:Thessa\'s green')]),
    dict(key='blossom', name='Blossom Eve', when=(4, 1, 1), who='west', fig='Young folk by the maypole',
         sight='A maypole on the green, fires the cattle are driven between, the young leaping over the flames. '
               'The fair folk are close tonight.', deco='¥', acts=[('Leap over the fire', 'leap'), ('Dance round the maypole', 'rumour')]),
    dict(key='walpurgis', name='Walpurgis Hill', when=(4, 1, 1), who='north', fig='A wise woman at the edge of town',
         sight='Far off on a bare hill a fire burns all night: the witches meet.',
         acts=[('Ask her what the fire means', 'rumour')]),
    dict(key='longtable', name='The Long Table', when=(5, 20, 1), who='halfling', fig='A halfling with a heap of parcels',
         sight='The whole town eats at one long table out on the green, and gives presents away.',
         deco='═', prices={'ale': .9, 'fruit': .9}, acts=[('Take a seat at the table', 'meal'), ('Take a little parcel', 'coin:40')]),
    dict(key='thirst', name='The Thirst Month', when=(6, 1, 30), who='desert', fig='A host at the evening meal',
         sight='By day the desert riders fast; at night they eat together, and a guest may not be turned away.',
         prices={'fruit': 1.1}, acts=[('Sit down at the evening meal', 'meal')]),
    dict(key='wetting', name='Wetting Day', when=(6, 15, 1), who='jungle', fig='A crowd with buckets',
         sight='Everybody throws water at everybody, and the statues of the gods are washed.',
         acts=[('Get soaked: cooler in the heat, harder to burn', 'bless:res_fire:15:2:Soaked to the skin')]),
    dict(key='lastsheaf', name='Last Sheaf', when=(7, 26, 3), who='heartwest', fig='Harvesters at the long tables',
         sight='The last sheaf goes on Thessa\'s harvest stone and the village eats at long tables out of doors.',
         deco='═', prices={'grain': .8, 'ale': .9}, acts=[('Eat with the harvesters', 'meal'), ('Hear the day labourers', 'rumour')]),
    dict(key='tapping', name='The Tapping', when=(8, 10, 3), who='dwarf', fig='A brewmaster at the first barrels',
         sight='The first barrels of the year are tapped in the hold; the dwarves are merry and talkative.',
         deco='o', prices={'ale': .8}, acts=[('Drink the first mug', 'rumour'), ('Toast the brewmaster', 'bless:str:1:2:The first barrel')]),
    dict(key='moonwatch', name='Moonwatch', when=(8, 15, 1), who='east', fig='A family on a roof with mooncakes',
         sight='Round cakes, and the whole village up on the roofs to watch the full moon.',
         acts=[('Share a mooncake: good food for the road', 'meal')]),
    dict(key='lightfeast', name='The Light-Feast', when=(9, 1, 1), who='northvillage', fig='A keeper at the village shrine',
         sight='The first dark night of the lights: lamps in every window, songs for the lights, cheap beds for travellers.',
         deco='°', acts=[('Take the shrine\'s blessing of the lights', 'bless:res_cold:15:3:Blessing of the lights'),
                         ('Hear the news of the north', 'rumour')]),
    dict(key='marigold', name='Marigold Days', when=(9, 20, 3), who='jungle', fig='A family at an altar of marigolds',
         sight='Altars of food and orange flowers for the dead; music in the graveyard. The dead are welcome here.',
         deco='*', acts=[('Leave food on the altar', 'bless:undead:15:3:Welcome of the dead')]),
    dict(key='lantriver', name='Lantern River', when=(9, 25, 1), who='river', fig='Children setting lights on the water',
         sight='Little lights float down the river to show the dead their way to the sea.',
         deco='°', acts=[('Set a light on the water', 'bless:undead:10:2:A light for the dead')]),
    dict(key='naming', name='The Naming', when=(9, 29, 2), who='heartwest', fig='A family saying the names of its dead',
         sight='Candles on the graves, hollow turnips with a light by the doors, salt on the thresholds. The dead are near.',
         deco='°', acts=[('Light a candle on a grave', 'bless:undead:20:2:The names of the dead')]),
    dict(key='lanternwalk', name='Lantern Walk', when=(10, 11, 1), who='humans', fig='Children with lanterns',
         sight='Children go from door to door with lanterns, singing; whoever is on the road gets a bowl of soup tonight.',
         deco='°', acts=[('Take a bowl of soup', 'meal')]),
    dict(key='firstfrost', name='First Frost', when=(10, 20, 1), who='gnome', fig='A gnome by the last open hatch',
         sight='On the first night of frost every hatch is shut, and the hamlet will be hard to find until the thaw.',
         acts=[('Leave a bowl of honey by the hatch', 'honey')]),
    dict(key='wanderer', name='Wanderer\'s Eve', when=(11, 5, 1), who='heart', fig='Children with their boots by the hearth',
         sight='Skell, the Grey Wanderer, comes by in the night. Boots stand by every hearth in the inn.',
         acts=[('Set your boot by the hearth, and sleep in the inn', 'boot')]),
    dict(key='eightlamps', name='Eight Lamps', when=(11, 10, 8), who='westport', fig='A trader closing old accounts',
         sight='Every night one more lamp in the windows; traders close their old accounts and open new ones.',
         deco='°', acts=[('Hear which debts are settled', 'rumour')]),
    dict(key='kite', name='Kite and Thunder', when=(11, 18, 1), who='bigport', fig='Dancers under a long cloth dragon',
         sight='Firecrackers and a long dragon of cloth through the streets drive out the evil spirits of the year.',
         deco='*', acts=[('Join the dragon', 'bless:undead:10:2:Thunder of the dragon')]),
    dict(key='hearth', name='Hearthnight', when=(11, 21, 1), who='humans', fig='A priest handing out Sky Bread',
         sight='Green in every house and a lamp in every window; the inns are full and beds dear. The temple takes in '
               'whoever has no roof tonight.', deco='°', prices={'ale': 1.15, 'wine': 1.15},
         acts=[('Take a piece of Sky Bread', 'meal'), ('Count who is at home, and name who is missing', 'rumour')]),
    dict(key='sunrope', name='Sun Rope', when=(11, 21, 1), who='canyon', fig='Riders with a rope at a stone post',
         sight='The canyon riders bind the sun to a stone post with a rope and a song, so that it comes back.',
         acts=[('Help pull the rope', 'bless:sight:1:3:The sun bound')]),
    dict(key='dawnmother', name='Dawnmother\'s Return', when=(11, 22, 1), who='humans', fig='Priests of Solmara on the hill path',
         sight='The priests of Solmara climb the hill to see the first sun after the longest night.',
         acts=[('Go up with them', 'bless:regen:2:3:Dawnmother\'s warmth')]),
    dict(key='starsong', name='Starsong', when=(6, 7, 1), who='elf', fig='An elf singing very softly',
         sight='One night a year they sing in every glade at once, so softly that only those in the wood can hear.',
         acts=[('Listen, and ask the way to another glade', 'glade')]),
    dict(key='tusks', name='Night of Tusks', when=(8, 1, 1), who='orc', fig='A chief at the duelling ring',
         sight='The tribes meet at the duelling ring: no war between tribes tonight, only duels.',
         deco='▲', acts=[('Drink with the champions', 'rumour')]),
    dict(key='swap', name='Swap Day', when=(4, 15, 1), who='goblin', fig='A goblin with a heap of odds and ends',
         sight='Everybody swaps whatever they have, and for one day a swap is honest.',
         acts=[('Swap for the truth about something', 'rumour')]),
    dict(key='shine', name='The Shine', when=(7, 14, 1), who='kobold', fig='A kobold polishing the hoard',
         sight='At the full moon the kobolds polish their hoard until it shines.',
         acts=[('Bring something shiny (a gem from your cargo) and look', 'shine')]),
    dict(key='hatching', name='The Hatching', when=(3, 20, 1), who='lizard', fig='A lizardfolk elder by the egg mounds',
         sight='The eggs hatch: the mounds are deadly today, but the folk are mild and trade.',
         acts=[('Wish the hatchlings well', 'rumour')]),
    dict(key='quench', name='Founders\' Quench', when=(2, 18, 1), who='dwarf', fig='The forge-master by the cold forge',
         sight='The birthday of the hold: the Great Forge is put out once, and lit again.',
         deco='▲', acts=[('Watch the forge lit again', 'bless:def:6:3:Fire of the founders')]),
    dict(key='oath', name='The Oath Day', when=(5, 1, 1), who='capital', fig='A herald of the king',
         sight='The barons swear fealty to their king; flags on every tower, and the small crimes are forgiven.',
         deco='¥', acts=[('Hear the amnesty read', 'amnesty')]),
]
BY_KEY = {f['key']: f for f in FEASTS}
FAIR = dict(key='fair', name='The Fair of Skell', fig='A showman of the travelling fair',
            sight='The travelling fair is in town for a week: stalls, jugglers and a merry-go-round, traders who pay '
                  'well, and thieves who know it.', deco='♦', acts=[('Try your luck at the fair', 'coin:30'),
                                                                   ('Hear the traders\' talk', 'rumour')])
FIG_FG = (255, 214, 120)


# ------------------------------------------------------------------ who keeps what
def _biome(game, x, y):
    om = game.maps.get('over')
    if om is None or not getattr(om, 'biome_names', None):
        return ''
    return om.biome_names[om.biome[y * om.w + x]]


def _human(s):
    return getattr(s, 'race', 'human') == 'human' and s.kind != 'deephold'


def keeps(game, s, who):
    """Does this settlement keep a feast of this kind?"""
    from . import names as NM
    om = game.maps['over']
    if who == 'dwarf':
        return s.kind == 'deephold' or getattr(s, 'race', '') == 'dwarf'
    if who in ('halfling', 'orc', 'elf'):
        return getattr(s, 'race', '') == who
    if not _human(s):
        return False
    d = NM.dialect(om, s.x, s.y)
    b = _biome(game, s.x, s.y)
    land = NM.land_at(om, s.x, s.y)
    return {'humans': True,
            'heart': d == 'heart', 'west': d == 'west', 'north': d == 'north',
            'heartwest': d in ('heart', 'west'), 'heartcity': d == 'heart' and s.is_city,
            'fjord': d == 'north' and 'coast' in land,
            'northvillage': d == 'north' and not s.is_city,
            'east': d == 'heart' and s.x > om.w * .66 and not s.is_city,
            'steppe': b in ('steppe', 'meadow') and d != 'north', 'savanna': b == 'savanna', 'desert': b in ('desert', 'badlands'),
            'jungle': b == 'jungle', 'canyon': b == 'badlands',
            'river': 'river' in land, 'westport': d == 'west' and getattr(s, 'harbour', False),
            'bigport': s.is_city and getattr(s, 'harbour', False),
            'capital': getattr(s, 'kind', '') == 'metropolis'}.get(who, False)


def keeps_site(site, who):
    return {'elf': site.kind == 'glade', 'gnome': site.kind == 'gnomes', 'orc': site.kind == 'warcamp',
            'goblin': site.kind == 'ravine', 'kobold': site.kind == 'kobolds', 'lizard': site.kind == 'stilts'}.get(who, False)


def _on(day, when):
    from . import calendar as CAL
    mo, d0, n = when
    y, m, d, _wd = CAL._split(day)
    return 0 <= (m * 30 + d - (mo * 30 + d0)) % 360 < n


def fair_week(s):
    """The week the great fair is in this city: (month, first day), the same every year."""
    h = (s.id * 2654435761) & 0xffff
    return (3 + h % 6, 1 + (h >> 4) % 22)


def has_fair(game, s, day=None):
    day = game.day if day is None else day
    if not (s.is_city and _human(s)):
        return False
    mo, d0 = fair_week(s)
    return _on(day, (mo, d0, 7))


def today(game, place=None, day=None):
    """The feasts kept here today: settlement or site (or where you are)."""
    day = game.day if day is None else day
    if place is None:
        place = here(game)
    if place is None:
        return []
    out = []
    if hasattr(place, 'market'):
        out = [f for f in FEASTS if _on(day, f['when']) and keeps(game, place, f['who'])]
        if has_fair(game, place, day):
            out.append(FAIR)
    else:
        out = [f for f in FEASTS if _on(day, f['when']) and keeps_site(place, f['who'])]
    return out


def here(game):
    """The settlement or people's site you are in, or None."""
    s = game.here
    if s is not None:
        return s
    m = game.map
    sid = getattr(m, 'site', None)
    if sid is None:
        sid = next((q.id for q in getattr(game.world, 'sites', ()) if q.map_key == m.key), None)
    return game.world.sites[sid] if sid is not None else None


def label(game):
    """For the line under the map: the first feast kept here today."""
    if game.map.kind != 'town':
        return None
    fs = today(game)
    return fs[0]['name'] if fs else None


# ------------------------------------------------------------------ prices
def daily(game):
    prices(game)
    _boot_morning(game)


def prices(game):
    """Set the feast prices of every town for today (economy.FEAST)."""
    from . import economy as ECO
    ECO.FEAST.clear()
    for s in game.world.settlements:
        if not s.market:
            continue
        for f in today(game, s):
            for g, k in f.get('prices', {}).items():
                ECO.FEAST[(s.id, g)] = ECO.FEAST.get((s.id, g), 1.0) * k
    ECO.FEAST['day'] = game.day


def fair_bonus(game, s):
    return 1.1 if has_fair(game, s) else 1.0


# ------------------------------------------------------------------ in the town
def on_enter(game, m):
    """A feast day: the square dressed, someone to walk into, the name in the log."""
    m.mons = [o for o in m.mons if not getattr(o, 'feast', None)]
    over = getattr(m, 'over', None)
    for i in getattr(m, 'feast_deco', ()):
        if over is not None:
            over.pop(i, None)
    m.feast_deco = []
    m.feast = None
    fs = today(game)
    if not fs:
        m._look = None
        return
    f = fs[0]
    m.feast = f['key']
    cx, cy = getattr(m, 'centre', (m.w // 2, m.h // 2))
    from .townlife import _free_near, _outdoor, _npc
    c = _free_near(m, cx, cy, 1, 6, _outdoor(m))
    if c:
        n = _npc(game, m, f['fig'], 'feast', FIG_FG, c[0], c[1], 'feast', stay=True)
        n.feast, n.life = f['key'], False
    if f.get('deco'):
        if over is None:
            m.over = over = {}
        for _ in range(14):
            d = _free_near(m, cx, cy, 2, 9, _outdoor(m))
            if d:
                i = d[1] * m.w + d[0]
                if i not in over:
                    over[i] = (f['deco'], FIG_FG if f['deco'] == '°' else (230, 120, 140) if f['deco'] in '*♦' else
                               (250, 150, 60) if f['deco'] == '▲' else (140, 200, 90), None)
                    m.feast_deco.append(i)
        m._look = None
    if getattr(m, 'feast_told', None) != (game.day, f['key']):
        m.feast_told = (game.day, f['key'])
        game.msg(f'{f["name"]}: {f["sight"]}', 'gold')
        from . import guide as GD
        GD.tip(game, 'feast')


def target(game, npc):
    """At a feast the folk gather in the square from five until late."""
    m = game.map
    if not getattr(m, 'feast', None) or getattr(npc, 'job', '') in ('guard', 'lamplighter', 'refugee', 'feast'):
        return None
    from .townlife import _hour, _free_near, _outdoor
    h = _hour(game)
    if 17 <= h < 23 and npc.id % 2:
        spot = getattr(npc, 'feast_pos', None)
        if spot is None:
            cx, cy = getattr(m, 'centre', (m.w // 2, m.h // 2))
            spot = npc.feast_pos = _free_near(m, cx, cy, 1, 7, _outdoor(m)) or npc.home_pos
        return spot
    return None


# ------------------------------------------------------------------ walking into the feast
def _year(game):
    from . import calendar as CAL
    return CAL._split(game.day)[0]


def done(game, key):
    return (key, _year(game)) in game.player.__dict__.setdefault('feasts', set())


def _mark(game, key):
    game.player.__dict__.setdefault('feasts', set()).add((key, _year(game)))


def talk(game, npc):
    from . import events as EV
    f = FAIR if npc.feast == 'fair' else BY_KEY[npc.feast]
    opts = []
    for i, (lab, act) in enumerate(f['acts']):
        one = act.split(':')[0] not in ('rumour',)
        opts.append((lab + (' (done this year)' if one and done(game, f'{f["key"]}:{i}') else ''),
                     None if one and done(game, f'{f["key"]}:{i}') else str(i)))
    opts.append(('Go on', 'bye'))
    EV.ask(game, 'feast', f['name'], f['sight'], opts, feast=f['key'], npc=npc.id)
    return True


def r_feast(game, choice, ctx):
    if choice in (None, 'bye'):
        return
    f = FAIR if ctx['feast'] == 'fair' else BY_KEY[ctx['feast']]
    i = int(choice)
    act = f['acts'][i][1]
    npc = next((o for o in game.map.mons if o.id == ctx.get('npc')), None)
    kind, *args = act.split(':')
    if kind != 'rumour':
        _mark(game, f'{f["key"]}:{i}')
    do(game, f, kind, args, npc)


def do(game, f, kind, args, npc=None):
    p = game.player
    from .money import fmt
    if kind == 'bless':
        k, v, days, lab = args[0], int(args[1]), int(args[2]), args[3]
        p.buffs = [b for b in p.buffs if b[3] != lab] + [[k, v, days * D.DAY_LEN, lab]]
        game.msg(f'{lab}: it stays with you for {days} days.', 'gold')
    elif kind == 'vigil':
        from .towns import is_night
        n = 0
        while is_night(game) and n < D.DAY_LEN // 2:
            game.end_turn(10, True)
            n += 10
        do(game, f, 'bless', args)
        game.msg('You watch until the fires are lit again. The priest touches your brow.', 'info')
    elif kind == 'meal':
        from . import hunger as HU
        p.food = HU.MAX
        game.msg('You eat your fill, and nobody asks you for a coin.', 'good')
    elif kind == 'rumour':
        if npc is not None:
            game.say(npc, game.rumor())
        else:
            game.msg(game.rumor(), 'info')
    elif kind == 'coin':
        n = int(args[0])
        got = random.randint(n // 3, n)
        p.gold += got
        game.msg(f'You come away {fmt(got)} the richer.', 'good')
    elif kind == 'leap':
        if random.random() < .8:
            do(game, f, 'bless', ['crit', '3', '2', 'Over the fire'])
        else:
            p.life = max(1, p.life - 3)
            game.msg('You leap a little short and singe your heels. Everyone cheers anyway.', 'info')
    elif kind == 'egg':
        from . import hunger as HU
        p.food = min(HU.MAX, p.food + 120)
        p.gold += 5
        game.msg('In a hedge you find a painted egg, and a copper coin pressed into the moss beside it.', 'good')
    elif kind == 'mask':
        price = int(args[0])
        if p.gold < price:
            game.msg('You have not got the coin for a mask.', 'bad')
            done_ = p.__dict__.setdefault('feasts', set())
            done_.discard((f'{f["key"]}:0', _year(game)))
            return
        p.gold -= price
        left = _left(game, f)
        p.buffs = [b for b in p.buffs if b[0] != 'masked'] + [['masked', 1, left, 'A Masking mask']]
        game.msg('You tie on a mask of painted leather. For as long as the Masking lasts, nobody knows your face.', 'gold')
    elif kind == 'honey':
        if p.cargo.get('honey', 0) >= 1:
            p.cargo['honey'] -= 1
            if not p.cargo['honey']:
                del p.cargo['honey']
            game.msg('A little bell rings behind the hatch. You will be welcome here, frost or no frost.', 'good')
            site = here(game)
            if site is not None:
                game.flags[f'gnomes{site.id}'] = True
        else:
            done_ = p.__dict__.setdefault('feasts', set())
            done_.discard((f'{f["key"]}:0', _year(game)))
            game.msg('You have no honey in your cargo.', 'bad')
    elif kind == 'boot':
        p.boot_day = game.day
        game.msg('You set your boot by the hearth with the others. Now to bed, here in the inn.', 'info')
    elif kind == 'glade':
        from . import folk as FK
        left = [q for q in game.world.sites if q.kind == 'glade' and FK.unfound(q)]
        if left:
            q = min(left, key=lambda q: cheb(q.x, q.y, *game.world_pos()))
            q.found = True
            game.msg(f'Under the song you hear the way: {q.name} lies hidden to the {_dirword(game, q)}.', 'gold')
        else:
            game.msg('The song is all you hear. It is enough.', 'info')
    elif kind == 'shine':
        if p.cargo.get('gems', 0) >= 1:
            p.cargo['gems'] -= 1
            if not p.cargo['gems']:
                del p.cargo['gems']
            game.msg('The kobolds coo over the gem and let you look at the hoard. "Found in the old stone city, this '
                     'one," says one, and points.', 'gold')
            if npc is not None:
                game.say(npc, game.rumor())
        else:
            done_ = p.__dict__.setdefault('feasts', set())
            done_.discard((f'{f["key"]}:0', _year(game)))
            game.msg('You have nothing shiny in your cargo.', 'bad')
    elif kind == 'amnesty':
        s = game.here
        if s is not None and s.rep < 0 and s.rep > -60:
            s.rep = 0
            s.crimes = []
            game.msg('The herald reads the amnesty: your small crimes here are forgiven.', 'good')
        else:
            game.msg('The herald reads the amnesty. Nothing in it is about you.', 'info')


def _dirword(game, q):
    from . import engine as E
    x, y = game.world_pos()
    return E.dir_name(q.x - x, q.y - y)


def _left(game, f):
    """Turns until this feast ends."""
    from . import calendar as CAL
    mo, d0, n = f['when']
    y, m, d, _wd = CAL._split(game.day)
    into = (m * 30 + d - (mo * 30 + d0)) % 360
    days = max(1, n - into)
    return days * D.DAY_LEN - game.turn % D.DAY_LEN


def masked(game):
    return any(b[0] == 'masked' for b in game.player.buffs)


def _boot_morning(game):
    """The morning after Wanderer's Eve: what is in your boot depends on your year."""
    p = game.player
    if getattr(p, 'boot_day', None) != game.day - 1:
        return
    p.boot_day = None
    from . import crime as CR
    if CR.wanted_in(game):
        game.msg('In your boot: a lump of coal. Nobody at the inn will look you in the eye. "Skell knows."', 'bad')
        return
    pick = random.random()
    if pick < .4:
        p.gold += random.randint(5, 20)
        game.msg('In your boot: an apple, and a few copper coins.', 'good')
    else:
        game.msg(f'In your boot: an apple, and a folded scrap with a rhyme on it. "{game.rumor()}"', 'gold')
    if getattr(p, 'god', None) == 'skell':
        p.buffs.append(['crit', 3, D.DAY_LEN * 3, 'Skell\'s luck'])


def table_rows():
    """The handbook's table: when, what, where."""
    from . import calendar as CAL
    where = {'humans': 'all human towns', 'heart': 'the heartland', 'west': 'the west', 'north': 'the north',
             'heartwest': 'the heartland and the west', 'heartcity': 'the cities of the heartland',
             'fjord': 'the fjords', 'northvillage': 'northern villages', 'east': 'the eastern farmland',
             'steppe': 'the steppe', 'savanna': 'the savanna', 'desert': 'the desert', 'jungle': 'the jungle',
             'canyon': 'the canyons', 'river': 'river towns', 'westport': 'the western ports', 'bigport': 'great harbours',
             'capital': 'the great city', 'dwarf': 'dwarves', 'elf': 'elves', 'halfling': 'halflings', 'gnome': 'gnomes',
             'orc': 'half-orcs and orcs', 'goblin': 'goblins', 'kobold': 'kobolds', 'lizard': 'lizardfolk'}
    rows = []
    for f in sorted(FEASTS, key=lambda f: (f['when'][0], f['when'][1])):
        mo, d0, n = f['when']
        when = f'{d0} {CAL.MONTHS[mo]}' + (f', {n} days' if n > 1 else '')
        rows.append([when, f'{f["name"]}, {where[f["who"]]}'])
    return rows


def _register():
    from . import events as EV
    EV.RESOLVERS['feast'] = r_feast


_register()
