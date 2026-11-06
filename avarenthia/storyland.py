"""The story on the land (round 58c): places where The Counted Sky can be touched, each a thing you walk into with
one outcome. Bardin Coalhand bound in a Varnish ruin, the altar stone by the Wyrm's Bones, Ferro the bound clerk in
an empty granary, Tam's tally on his wall tower, the dark ring on a star house's floor, Aerith chained in the Hall of
the Winds, the goblins' drains up into the Sky-Seat, the north's own ways, and the Northern Wall on the world map.

Which places hold what is on `world.storyland` (made with the world, or the first time it is asked for in an older
one); what this hero did is on `p.storyland`. The court under the hill is in feycourt.py."""
import math
import random

from . import data as D

WALL_FG = (150, 156, 172)          # the towers' colour, a little faded: the Wall on the world map


# ------------------------------------------------------------------ state
def st(game):
    p = game.player
    if not hasattr(p, 'storyland'):
        p.storyland = dict(bardin=None, tam=False, ferro=None, ring=False, aerith=False, drains=False, fed=set(),
                           altar=None, named=set())
    return p.storyland


def info(game):
    w = game.world
    V = getattr(w, 'storyland', None)
    if V is None:
        om = game.maps.get('over')
        reach = {i for i, t in enumerate(om.t) if D.TILES[t].walk} if om is not None else set()
        place(game, om, w, reach)
        V = w.storyland
    return V


def place(game, m, world, reach_set):
    """With the world, last: which Varnish places hold Bardin, Tam's tally and the dark ring; the altar stone by the
    Wyrm's Bones, Ferro's granary, and one barrow that is not what it seems. Dice of their own."""
    state = random.getstate()
    random.seed(game.seed * 7717 + 59)
    try:
        V = world.storyland = dict(bardin=None, tam=None, ring=None, altar=None, granary=None, howe=None, calm=None)
        if m is None:
            return
        sites = world.sites

        def one(kinds):
            c = [s for s in sites if s.kind in kinds]
            return random.choice(c).id if c else None
        V['bardin'] = one(('vcity',)) if any(s.kind == 'vcity' for s in sites) else one(('deadroad', 'harbour'))
        V['tam'] = one(('walltower',))
        V['ring'] = one(('starhouse',))
        from . import landmarks as LM
        lay = LM.Lay(game, m, world, reach_set)
        bones = next(((x, y) for n, x, y in getattr(world, 'wonders', ()) if n == "The Wyrm's Bones"), None)
        if bones:
            spot = lay.around(bones[0], bones[1], 3, 7)
            if spot:
                V['altar'] = lay.add('altarstone', spot, 'The Altar Stone', hidden=True).id
        spot = lay.search(lambda x, y: m.tile(x, y) in (D.GRASS, D.FIELD) and 2 <= lay.road(x, y) <= 8
                          and y > m.h * .25, 6)
        if spot:
            V['granary'] = lay.add('granary', spot, 'The Empty Granary').id
        from . import feycourt as FC
        FC.place(game, lay, V)
    finally:
        random.setstate(state)


def site_of(game, key):
    sid = info(game).get(key)
    return game.world.sites[sid] if sid is not None else None


# ------------------------------------------------------------------ the telling things (landmarks' frame)
def _things():
    from . import landmarks as LM
    for k, n, c, f in [('bardin', 'short broad figure in the stonework', '&', (196, 160, 120)),
                       ('altarstone', 'flat stone with a cup cut in it', '■', (210, 200, 176)),
                       ('bin', 'empty grain bin', '□', (170, 150, 120)),
                       ('ledger', 'clerk\'s desk', 'π', (190, 170, 130)),
                       ('darkring', 'ring of lead in the iron floor', 'o', (120, 120, 132)),
                       ('silverdot', 'dot of silver light in the iron floor', '·', (230, 236, 255)),
                       ('aerith', 'woman of wind, chained', '&', (200, 230, 255))]:
        LM.thing_kind(k, n, c, f)


def _put(m, x, y, key, walk=False):
    from . import landmarks as LM
    if not hasattr(m, 'tells'):
        m.tells = {}
    if not hasattr(m, 'over'):
        m.over = {}
    LM.put(m, x, y, key, walk)
    m._look = None


def bump(game, x, y):
    """A thing of the story. Returns the turns it took, or None."""
    from . import landmarks as LM
    m = game.map
    key = LM.thing_at(m, x, y)
    fn = BUMP.get(key)
    return fn(game, x, y) if fn else None


def on_enter(game, site, m):
    """Coming to a place: the story's things that lie there."""
    V = info(game)
    s = st(game)
    if site.id == V.get('bardin') and s['bardin'] is None and not getattr(m, 'bardin_put', False):
        spot = _wall_spot(m)
        if spot:
            _put(m, *spot, 'bardin')
            m.bardin_put = True
    if site.id == V.get('ring') and getattr(site, 'swept', False):
        if not getattr(m, 'ring_put', False):
            _ring(game, m)
        else:
            from . import skyseat as SKY
            from . import landmarks as LM
            if SKY.sh(game.world).get('won') and LM.thing_at(m, 28, 16) == 'darkring':
                _put(m, 28, 16, 'silverdot', walk=True)


def _wall_spot(m):
    """A stretch of old wall beside paving: the abutment of a bridge that is not there any more."""
    cells = [(x, y) for y in range(2, m.h - 2) for x in range(2, m.w - 2)
             if m.tile(x, y) in (D.VWALL, D.WALL, D.COLUMN) and any(D.TILES[m.tile(x + a, y + b)].walk
                                                                    for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    return random.choice(cells) if cells else None


# ---- Bardin Coalhand
def _bardin(game, x, y):
    from . import events as EV
    EV.ask(game, 'story', 'A short broad figure',
           'In the stonework of an old bridge abutment, where no bridge is any more, a short broad figure is bound '
           'standing, set into the wall like one more stone. A seal of lead hangs on his beard. Under the moss on the '
           'stone beside him someone has cut a name in dwarf runes, and then, in Varnish letters, a price.',
           [('Cut him free and carry him', 'bardin'), ('Leave him', 'bye')], x=x, y=y)
    return 0


def r_story(game, choice, ctx):
    if choice == 'bardin':
        from .entities import Item
        it = Item(game.new_id(), 'bardin', 'bardin')
        if not game.add_to_inv(it):
            game.msg('You would need both hands, and room on your back. Your bag is full.', 'bad')
            return
        from . import landmarks as LM
        LM.take(game.map, ctx['x'], ctx['y'], D.RUBBLE)
        st(game)['bardin'] = 'carried'
        game.end_turn(30)
        game.msg('It takes a long time, and a chisel. He is light, lighter than a dwarf should be, and stiff as wood. '
                 'You wrap him in your cloak. A dwarf hall would know what to do with him.', 'unique')
    elif choice == 'aerith':
        _free_aerith(game, ctx)
    elif choice == 'tam':
        st(game)['tam'] = True
        from . import chronicle as CH
        CH.deed(game, 'Tam counted', 'You counted Tam, a soldier of the Northern Wall: ten years and a day, and '
                                     'nobody had.')
        game.msg('You count him. One soldier, Tam, of the Wall, three thousand six hundred and fifty-one days. You say '
                 'the number out loud. The wind takes it north.', 'unique')
    elif choice == 'ferro_seal':
        o = next((o for o in game.map.mons if o.id == ctx.get('npc')), None)
        if o:
            game.map.mons.remove(o)
        st(game)['ferro'] = 'rest'
        from . import chronicle as CH
        CH.deed(game, 'Ferro at rest', 'You broke the seal of Ferro, a bound clerk of the Varnish, in an empty '
                                       'granary. He stopped counting.')
        game.msg('The lead seal breaks under your thumb. Ferro puts the pen down, very carefully, square to the edge of '
                 'the ledger. "Entered," he says, and is still.', 'unique')
    elif choice == 'altar':
        _offer(game)
    elif choice and choice.startswith('fey'):
        from . import feycourt as FC
        FC.r_fey(game, choice, ctx)


def home_bardin(game, s):
    """Carried into a dwarf hall: they lay him flat."""
    p = game.player
    it = next((i for i in p.inv if i.k == 'bardin'), None)
    if not it or s.race != 'dwarf':
        return False
    p.inv.remove(it)
    st(game)['bardin'] = 'home'
    from . import folkbooks as FB
    FB.st(game)['favour'].add('dwarf')
    from . import chronicle as CH
    CH.deed(game, 'Bardin brought home', f'You carried Bardin Coalhand, bound standing by the Varnish, to {s.name}, '
                                         'and the dwarves laid him flat.')
    CH.add(game, 'Peoples', 'Bardin Coalhand is home and lies flat. The grudge against the Varnish stays open; a debt '
                            'may not outlive the debtor, a grudge may. But every hold has your name in its book now.',
           'seen', where=s.name, key='sl:bardin', quiet=True)['head'] = 'folk:dwarf'
    game.request = ('dialog', 'Bardin Coalhand', 'They take him from you without a word. Six of them carry him down, '
                    'and in the lowest hall they lay him flat, at last, on cold stone, the way a dwarf should lie. The '
                    'keeper of the hall opens the Grudge Book at its oldest page and writes for a long time. Then she '
                    'turns the book round so you can see: your name, on the other side of the page.\n\n"The grudge '
                    'stays," she says. "But every hold will know you now. Entered."')
    return True


def bardin_known(game):
    """The Account of Bardin Coalhand, whole: where he stands."""
    s = site_of(game, 'bardin')
    if s is None:
        return
    from . import folk as FK
    from . import chronicle as CH
    if FK.unfound(s):
        FK.discover(game, s, None)
    game.reveal_place(s.x, s.y)
    CH.add(game, 'Places', f'Bardin Coalhand stands bound in the stonework of {s.name}.', 'read',
           who='The Account of Bardin Coalhand', place=(s.x, s.y), key='lead:bardin', quiet=True)
    game.msg(f'The last page says where the bridge was: {s.name}. You mark it on your map.', 'info')


# ---- the altar stone by the Wyrm's Bones
def altar_known(game):
    """The Fortieth Master tells of the altar stone a mile from the wyrm's bones."""
    s = site_of(game, 'altar')
    if s is None:
        return
    from . import folk as FK
    if FK.unfound(s):
        FK.discover(game, s, None)
    game.reveal_place(s.x, s.y)
    game.msg('A mile from the bones, the book says, the master who lived set up a stone. You mark it on your map.',
             'info')


def _m_altar(game, site):
    from . import landmarks as LM
    m = LM.land(game, site, 50, 30)
    cx, cy = m.w // 2, m.h // 2
    LM.clear(m, cx, cy, 6, 4, D.SAND if m.t[0] == D.SAND else D.GRASS)
    LM.put(m, cx, cy, 'altarstone')
    LM.way(m, (0, cy), (cx - 2, cy))
    return LM.finish(m, (0, cy))


def _altar(game, x, y):
    from . import calendar as CAL
    from . import events as EV
    p = game.player
    year = CAL._split(game.day)[0]
    if st(game)['altar'] == year:
        game.msg('The bread you left is gone. The sand lies still round the bones.', 'info')
        return 0
    text = ('A flat stone, waist high, with a cup cut in the top, black with old oil. Crumbs of bread lie round it, '
            'gone hard as grit. Far off over the sand the ribs of the wyrm stand up against the sky.\n\nThe master who '
            'lived set this stone here, the old book says, and every spring someone should leave bread and oil, so '
            'that the one who sleeps knows he is not forgotten.')
    bread = next((i for i in p.inv if i.k == 'food' and i.t == 'bread'), None)
    oil = next((i for i in p.inv if i.k == 'draught' and i.t == 'oil'), None) or \
        next((i for i in p.inv if i.k == 'food' and i.t == 'butter'), None)
    spring = CAL.season(game.day) == 'spring'
    opts = [('Leave bread and oil', 'altar' if bread and oil and spring else None), ('Leave it', 'bye')]
    if not spring:
        text += ' It is not spring.'
    elif not (bread and oil):
        text += ' You have no bread and oil with you.'
    EV.ask(game, 'story', 'The Altar Stone', text, opts)
    return 0


def _offer(game):
    from . import calendar as CAL
    p = game.player
    bread = next((i for i in p.inv if i.k == 'food' and i.t == 'bread'), None)
    oil = next((i for i in p.inv if i.k == 'draught' and i.t == 'oil'), None) or \
        next((i for i in p.inv if i.k == 'food' and i.t == 'butter'), None)
    if not (bread and oil):
        return
    game.remove_one(bread)
    game.remove_one(oil)
    year = CAL._split(game.day)[0]
    st(game)['altar'] = year
    w = game.world
    bones = next(((x, y) for n, x, y in getattr(w, 'wonders', ()) if n == "The Wyrm's Bones"), None)
    if bones:
        info(game)['calm'] = (w.region_at(*bones).id, year)
    from . import chronicle as CH
    CH.deed(game, 'Bread at the altar stone', 'You left bread and oil on the altar stone by the Wyrm\'s Bones, in '
                                              'spring, as the master who lived asked.')
    game.msg('You break the bread into the cup and pour the oil over it. Nothing happens. Then the wind drops, all '
             'at once, and the sand round the bones lies still. It stays still the rest of the year.', 'unique')


def calm(world, rid, day):
    """The desert round the bones lies still the year someone left bread at the stone."""
    from . import calendar as CAL
    c = (getattr(world, 'storyland', None) or {}).get('calm')
    return bool(c) and c[0] == rid and c[1] == CAL._split(day)[0]


# ---- Ferro in the empty granary
def _m_granary(game, site):
    from . import landmarks as LM
    m = LM.land(game, site, 52, 30)
    cx, cy = m.w // 2, m.h // 2
    LM.clear(m, cx, cy, 13, 7)
    LM.hut(m, cx - 11, cy - 5, 22, 10, 'w', D.WALL, D.FLOOR)
    for x in range(cx - 8, cx + 9, 3):
        LM.put(m, x, cy - 3, 'bin')
        LM.put(m, x, cy + 3, 'bin')
    LM.put(m, cx + 7, cy, 'ledger')
    if st(game)['ferro'] != 'rest':
        LM.npc(game, m, 'Ferro, a bound clerk', '#b8b0a0', cx + 6, cy, 'granary')
    LM.way(m, (0, cy), (cx - 12, cy))
    return LM.finish(m, (0, cy))


MEASURE = ('"The measure," he says, in a voice like a page turning. "Entered at the Founding, kept in every granary '
           'of the Empire. For one counted soul, for one day: bread, one loaf of the standard weight. Oil, one small '
           'cup. Beans or barley, two handfuls. Salt, as much as covers a thumbnail. Wine on feast days. On the ninth '
           'day, none."\n\nHe lifts the ledger and shows you a column, very long, of names, and a shorter column next '
           'to it, of nothing at all. "The uncounted were not entered. They needed nothing, it says here." He turns '
           'back to the first page, and starts again.')


def _t_granary(game, site, o):
    from . import landmarks as LM
    from . import chronicle as CH
    f = CH.add(game, 'The Varnish', 'The measure, as a bound clerk keeps it still: for one counted soul, one day, a '
                                    'loaf, a cup of oil, two handfuls of beans, a thumbnail of salt; for the '
                                    'uncounted, nothing.', 'heard', who='Ferro, a bound clerk', where=site.name,
               key='sl:ferro', quiet=True)
    f['head'] = 'Law and measure'
    if st(game)['ferro'] is None:
        st(game)['ferro'] = 'heard'
    LM.ask(game, site, o.name, 'A clerk of the Varnish sits at a desk in the empty granary, dry as his paper, a seal '
           'of lead on his chest. His pen moves down a column. "Name," he says, without looking up. "Count. Measure."\n'
           '\n' + MEASURE, [('Break his seal', 'ferro_seal'), ('Leave him to his count', 'bye')], npc=o.id)


def _c_granary(game, site, choice, ctx):
    r_story(game, choice, ctx)


# ---- Tam's tally (varnish.py's day marks on his tower)
def tally(game, site):
    """The day marks on a wall tower: on Tam's, his name and his ask."""
    if site is None or site.id != info(game).get('tam'):
        game.msg('The stone is scratched with days in fives, row on row. Whoever kept them stopped, one day, in the '
                 'middle of a row.', 'info')
        return 0
    if st(game)['tam']:
        game.msg('TAM, 3,651. Counted.', 'info')
        return 0
    from . import events as EV
    EV.ask(game, 'story', 'The day marks', 'The stone is scratched with days in fives, row on row, thousands of them, '
           'the last rows shaky. At the end of the last row someone has cut a name, TAM, and the number 3,651. Under '
           'it, smaller, as if he were ashamed to ask, two words: Count me.', [('Count him', 'tam'), ('Leave it', 'bye')])
    return 0


# ---- the dark ring on a star house's floor
def _ring(game, m):
    m.ring_put = True
    cx, cy = 28, 16
    from . import skyseat as SKY
    won = SKY.sh(game.world).get('won')
    for k in range(9):
        a = k * math.tau / 9
        x, y = round(cx + 3 * math.cos(a)), round(cy + 2 * math.sin(a))
        m.set(x, y, D.STARFLOOR)
        _put(m, x, y, 'darkring', walk=True)
    m.set(cx, cy, D.STARFLOOR)
    _put(m, cx, cy, 'silverdot' if won else 'darkring', walk=not won)


def _darkring(game, x, y):
    from . import chronicle as CH
    s = st(game)
    game.request = ('dialog', 'The dark ring', 'Under the dust the floor is iron, and set in it, in a ring, nine plugs '
                    'of dull lead round an empty hole the size of a fist. The tellers stood here and watched the sky '
                    'through the roof that is not there. The nine were the Crown of Vael. The hole was where she '
                    'stood, small and quiet, before they pulled her down.')
    if not s['ring']:
        s['ring'] = True
        CH.add(game, 'The Varnish', 'On the iron floor of a star house: nine plugs of lead in a ring round an empty hole, '
               'the Crown of Vael and the place she stood.', 'seen', key='sl:ring', quiet=True)['head'] = 'The last days'
    return 0


def _silverdot(game, x, y):
    game.request = ('dialog', 'The dark ring', 'In the empty hole in the middle of the ring, very small, a dot of '
                    'silver light lies on the iron, that was not there before. Look up through the roof that is not '
                    'there: far in the north, one light that was missing is back.')
    return 0


WIN_LINE = 'Far in the north, where nine stars went out, one light comes back.'


# ---- Aerith in the Hall of the Winds (skyseat.py, floor 2)
def on_floor(game, m, depth):
    if depth != 2 or st(game)['aerith'] or getattr(m, 'aerith_put', False):
        return
    from . import worldgen as W
    c = W.rand_free(game, m, lambda t: t == D.FLOOR)
    if c:
        _put(m, *c, 'aerith')
        m.aerith_put = True


def _aerith(game, x, y):
    from . import events as EV
    EV.ask(game, 'story', 'Aerith', 'Something is chained to the floor of the hall: a woman made of wind and nothing, '
           'her edges always moving. A chain of star-iron runs from her ankle to a ring in the bronze, and the wind of '
           'the whole hall comes out of her, round and round, because it cannot go anywhere else. Her name is cut on '
           'the ring: AERITH. She looks at you.', [('Break the chain', 'aerith'), ('Leave her', 'bye')], x=x, y=y)
    return 0


def _free_aerith(game, ctx):
    from . import landmarks as LM
    m = game.map
    LM.take(m, ctx['x'], ctx['y'], D.FLOOR)
    st(game)['aerith'] = True
    game.msg('You strike the ring. The wind in the hall goes mad: it screams round you, and things come out of it.',
             'bad')
    if 'storm_spirit' in D.MONSTERS:
        LM.beasts(game, m, ['storm_spirit'] * 3, (ctx['x'], ctx['y']), r=5, awake=True)
    from . import chronicle as CH
    CH.deed(game, 'Aerith freed', 'You broke the chain of Aerith in the Hall of the Winds. The winds round the Hollow '
                                  'King are only wind now.')
    game.msg('The last link parts. Aerith goes up through the roof without a sound, and when the storm she leaves '
             'behind has blown itself out, the hall is only a hall.', 'unique')


def aerith(game):
    return bool(st(game)['aerith'])


AERITH_TEXT = 'The winds round him are only wind: Aerith is not his any more.'


# ---- the goblins' drains (folkbooks: What We Heard Under the Collegium)
def drains_known(game):
    s = st(game)
    if s['drains']:
        return
    s['drains'] = True
    from . import chronicle as CH
    CH.add(game, 'The Shadow', 'The goblins know a second way up into the Sky-Seat: the old drains of the mud-city, '
                               'from the rocks under the chain into the Under-City. Narrow, and wet.', 'read',
           who='What We Heard Under the Collegium', key='sl:drains', quiet=True)
    game.msg('The goblins knew a second way up into the Sky-Seat: the drains. Your chronicle grows: The Shadow.', 'gold')


def drains(game):
    return bool(st(game)['drains'])


def up_drains(game):
    """The narrow way: an hour on your belly in the old drains, and you come up in the Under-City."""
    game.end_turn(60)
    if game.dead:
        return
    game.msg('An hour on your belly in the old drains, in the dark, in water that was mud once. Then a grate, and '
             'the Under-City.', 'info')
    from . import skyseat as SKY
    SKY.enter_floor(game, 1)


# ---- the north's own ways
def north_known(game):
    game.msg('Now you know why the north asks your name, and feeds you first: they were the ones not counted.', 'info')


def on_town(game, s, m):
    """In a dwarf hall with Bardin on your back; in a hall of the north, the north's ways."""
    if home_bardin(game, s):
        return
    from . import folkbooks as FB
    if not FB.north_of_wall(game, s.x, s.y):
        return
    k = st(game)['fed']
    if s.id in k:
        return
    k.add(s.id)
    p = game.player
    from . import hunger as HU
    p.food = max(p.food, HU.MAX - 40)
    game.request = ('dialog', s.name, 'Before anyone asks who you are, there is a bowl of hot fish broth in your '
                    'hands and a place on the bench by the fire. Only when you have eaten does the old woman of the '
                    'hall sit down across from you.\n\n"Now," she says. "Your name?"\n\nYou tell her. She says it '
                    f'back, slowly, twice, as if she were putting it somewhere safe. "{p.name}. Good. Stay as long as '
                    'the weather wants you to."')


NORTH = ['{name}. You came back. Good.', 'Eat first, {name}. Talk after.', 'We steer by the stars here, {name}. '
         'There is nothing else to steer by.', 'The south sends us nobody, {name}. You came anyway.',
         'The big wall? Old. Older than the old. Our grandmothers did not talk about it, {name}, so we do not.',
         'Count the stars? Why would anyone count the stars, {name}? You steer by them.',
         'You have a name, {name}. Everyone has a name. Use it, or it goes thin.']


def north_voice(game):
    return random.choice(NORTH).format(name=game.player.name)


# ------------------------------------------------------------------ the Northern Wall on the world map
_WALL = {}


def wall_cells(game):
    """{cell: sign} of the Wall's line on the world map: a broken grey line, gaps where it fell."""
    w = game.world
    key = (id(w), game.seed)
    got = _WALL.get(key)
    if got is not None:
        return got
    om = game.maps['over']
    cells = set((getattr(w, 'varnish', None) or {}).get('wall', ()))
    out = {}
    for i in cells:
        x, y = i % om.w, i // om.w
        if (x * 7 + y * 13 + game.seed) % 5 == 0:          # here it fell
            continue
        if om.t[i] in (D.WATER, D.TOWN, D.CITY, D.ENTR, D.ROAD, D.CASTLE, D.FORT):
            continue
        up = (y - 1) * om.w + x in cells and (y - 1) * om.w + x - 1 not in cells
        out[i] = '│' if up and (y + 1) * om.w + x in cells else '─'
    _WALL[key] = out
    return out


# ------------------------------------------------------------------ the bound Bardin you carry (entities.CRAFT)
def display(game, it):
    return 'Bardin Coalhand'


def lines(game, it):
    return ['A dwarf, bound standing by the Varnish, light and stiff as wood, wrapped in your cloak.',
            'A dwarf hall would know what to do with him.']


def value(game, it):
    return 0


def glyph(it):
    return '&'


def color(it):
    return (196, 160, 120)


BUMP = {'bardin': _bardin, 'altarstone': _altar, 'darkring': _darkring, 'silverdot': _silverdot, 'aerith': _aerith}


def register():
    from . import events as EV
    from . import entities as EN
    from . import landmarks as LM
    from . import sites as SI
    _things()
    EV.RESOLVERS['story'] = r_story
    EN.CRAFT['bardin'] = 'storyland'
    for k, look, desc in [('altarstone', ('■', (210, 200, 176)), 'A flat stone in the sand, waist high, with a cup cut '
                                                                  'in the top.'),
                          ('granary', ('⌂', (176, 160, 130)), 'A long stone granary of the old days, empty. The door '
                                                             'stands open.')]:
        LM.LOOK[k] = look
        LM.DESC[k] = desc
        LM.NAME[k] = ''
        SI.SITE_LOOK[k] = look
    LM.BUILD['altarstone'] = _m_altar
    LM.BUILD['granary'] = _m_granary
    LM.TALK['granary'] = _t_granary
    LM.CHOOSE['granary'] = _c_granary
    LM.ACT['altarstone'] = lambda game, site, key, x, y: _altar(game, x, y)
    LM.ACT['granary'] = lambda game, site, key, x, y: (
        game.msg('An empty grain bin. Dust, and the marks of a measure on the side.', 'info') if key == 'bin' else
        game.msg('The clerk\'s desk. The ledger on it is open at the first page, again.', 'info')) or 0
    LM.LINES['altarstone'] = 'Sand, and a flat stone, and far off the ribs of something enormous.'
    LM.LINES['granary'] = 'A long granary of grey stone, its doors open. Inside, someone is writing.'


register()
