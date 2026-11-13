"""A roof of your own (round 64): a home that is yours, a small map with a fixed plan (walls, a door) and a floor you
furnish. Three ways to one, from cheap and safe to dear and risky:

- a town house, for sale behind a door marked $ in the hamlets, villages, towns, cities and the great city of every
  people; the house is one of the settlement's own (so the settlement rules hold). A hearth tax each season, paid
  when you come in or left in the chest by the door; a year unpaid and the town sells it.
- a home you build anywhere on the open land: a builder's stake from a carpenter, then stages from a camp to a keep,
  each with coin, timber, stone and days of building. The look follows the land.
- the empty seat of a fallen lesser house, bought from the baron when you are his knight or well known to his
  kingdom, restored in stages. Owned, never ruled.

Away from home each week brings a roll (theft, a broken piece, squatters, fire, flood, snow, a great evil), told
through the news; defences lower it. Every piece of furniture works with a bump or is decoration, and Comfort (one to
three stars) makes Well rested last longer.

Everything is on the player (p.homes, p.home_dyes): the multiplayer rule."""
import random

from . import data as D
from .worldgen import cheb

GOLD = 10000
SILVER = 100
YOU = (120, 200, 230)                   # your own colour on the land
HOME_CP = 0xE0F0
HOME_SIGN = chr(HOME_CP)                 # a sign of its own: a solid little house (⌂ is already a village)


def _sign():
    from . import owntiles as OT
    OT.SIGNS[HOME_CP] = ['...##...', '..####..', '.######.', '########', '.#....#.', '.#.##.#.', '.#.##.#.', '.######.']


_sign()

SEASON = 90                              # days in a season: the hearth tax falls due
SELL_AFTER = 360                         # a year unpaid and the town sells it
TOWN_PRICE = {'hamlet': 4, 'village': 7, 'town': 14, 'city': 24, 'metropolis': 40}       # gold, for a middling house
FOR_SALE = {'hamlet': 1, 'village': 1, 'town': 2, 'city': 3, 'metropolis': 5}
STAKE = 2 * GOLD

# the stages of a home you build: key, noun, coin (gold), timber, stone, days, chest room
STAGES = [('camp', 'camp', 0, 0, 0, 0, 10),
          ('hut', 'hut', 5, 4, 0, 3, 10),
          ('cabin', 'cabin', 12, 8, 2, 6, 10),
          ('house', 'stone house', 25, 4, 10, 10, 20),
          ('holdfast', 'holdfast', 30, 6, 12, 12, 20),
          ('keep', 'keep', 60, 8, 20, 20, 20)]
STAGE_WORD = {'camp': 'A fire, a bedroll, one chest.', 'hut': 'A door that locks.',
              'cabin': 'Two rooms and a hearth.', 'house': 'Stone walls and a cellar: chests hold twice as much.',
              'holdfast': 'A palisade round it and a watch post.', 'keep': 'A small stone tower-keep: your own castle.'}

SEAT_PRICE = {'farm': 120, 'tower': 200, 'manor': 300}
# restoring a seat: key, what, coin (gold), timber, stone, days
SEAT_STAGES = [('ruin', 'the ruin', 0, 0, 0, 0),
               ('cleared', 'Clear the rubble and the burnt beams', 10, 4, 0, 4),
               ('roofed', 'Roof the hall again', 20, 8, 2, 8),
               ('walled', 'Mend the gate and the wall', 25, 2, 12, 10),
               ('whole', 'Raise the tower again', 30, 6, 16, 14)]
STEWARD_WAGE, GUARD_WAGE = 60, 40        # copper a day
CARETAKER_WAGE, DOG_FOOD = 40, 3

# the look by the land: wall colour, floor, the ground round it, a word
LANDS = {'log': ((150, 104, 62), D.PLANK, D.GRASS, 'log'), 'stone': ((150, 146, 140), D.FLOOR, D.GRASS, 'stone'),
         'sod': ((118, 120, 70), D.FLOOR, D.GRASS, 'sod'), 'stilts': ((128, 110, 80), D.PLANK, D.SWAMP, 'stilted'),
         'clay': ((196, 150, 100), D.FLOOR, D.SAND, 'clay'), 'long': ((140, 112, 84), D.PLANK, D.SNOW, 'long'),
         'timber': ((170, 128, 84), D.PLANK, D.GRASS, 'timber')}
LAND_OF = {}
for _k, _bs in (('long', 'tundra tundra_hills taiga glacier alpine shrubland_cold ice_shelf pack_ice'),
                ('log', 'forest deep_forest conifer birch dry_forest jungle clearing dead_trees petrified'),
                ('stone', 'hills karst mesa stone_ground moor canyon crater_rim'),
                ('stilts', 'swamp marsh mangrove floodplain'),
                ('clay', 'desert dune dune_crest savanna oasis badlands salt_edge shrubland bone_sand'),
                ('sod', 'steppe meadow')):
    for _b in _bs.split():
        LAND_OF[_b] = _k

# ------------------------------------------------------------------ furniture
# key: name, sign, price (copper, oak), walkable, the real tile it is (or None: a piece of its own), what it does
PIECES = {
    'bed': ('Bed', '≡', 100 * SILVER // 1, False, 'BED', 'Sleep: rest, spend tree points, wake Well rested.'),
    'chest': ('Chest', '■', 60 * SILVER, False, None, 'Holds ten things.'),
    'strongbox': ('Strongbox', '■', 2 * GOLD, False, None, 'Holds twenty things; thieves seldom get it open.'),
    'rack': ('Weapon rack', '‡', 1 * GOLD, False, None, 'Swap the weapon and shield you hold for the ones on it.'),
    'stand': ('Armour stand', 'Ω', 120 * SILVER, False, None, 'Swap the armour you wear for the set on it.'),
    'shelf': ('Bookshelf', '║', 1 * GOLD, False, None, 'Your books and pages, to read again.'),
    'hearth': ('Hearth', '☼', 2 * GOLD, False, 'HEARTH', 'Cook here; warm in winter.'),
    'workbench': ('Workbench', '╤', 2 * GOLD, False, 'BENCH', 'Leatherwork and tailoring; the guild bench at Journeyman.'),
    'anvil': ('Anvil', '¥', 3 * GOLD, False, 'ANVIL', 'Smithing; the guild bench at Journeyman.'),
    'loom': ('Loom', '╥', 2 * GOLD, False, 'BENCH', 'Tailoring; the guild bench at Journeyman.'),
    'shrine': ('Shrine', '±', 150 * SILVER, False, None, 'A small blessing once a day.'),
    'herbbed': ('Herb bed', '"', 40 * SILVER, False, None, 'Herbs grow here over a few days.'),
    'kennel': ('Kennel', 'π', 80 * SILVER, False, None, 'Your beast can stay here while you are away.'),
    'stable': ('Stable stall', '▬', 3 * GOLD, False, None, 'Your beast stays here; a dog here keeps watch.'),
    'rug': ('Rug', '░', 30 * SILVER, True, None, 'Decoration.'),
    'tapestry': ('Tapestry', '▒', 80 * SILVER, False, None, 'Decoration, against a wall.'),
    'plant': ('Potted plant', '♣', 20 * SILVER, False, None, 'Decoration.'),
    'lamp': ('Lamp', 'Γ', 40 * SILVER, False, None, 'Light in the room.'),
    'table': ('Table', 'π', 50 * SILVER, False, 'TABLE', 'Decoration.'),
    'trophy': ('Trophy', 'ß', 0, False, None, 'Something you brought home: for the eye, and for Comfort.'),
    'post': ('Doorpost chest', '■', 0, False, None, 'The tax, the defences, building: the business of the house.'),
}
SHOP_ORDER = ['bed', 'chest', 'strongbox', 'rack', 'stand', 'shelf', 'hearth', 'workbench', 'anvil', 'loom', 'shrine',
              'herbbed', 'kennel', 'stable', 'rug', 'tapestry', 'plant', 'lamp', 'table']
DECOR = {'rug', 'tapestry', 'plant', 'lamp', 'table', 'trophy'}
# each people sells its own style: name, colour, price factor
STYLES = {'plain': ('plain', (150, 132, 110), .8), 'oak': ('oak', (178, 126, 74), 1.0),
          'stone': ('dwarf stone', (170, 172, 184), 1.3), 'elven': ('elven wood', (150, 204, 140), 1.4),
          'snug': ('halfling snug', (214, 164, 112), 1.1), 'hide': ('orc hide', (164, 120, 88), .9)}
STYLE_OF = {'human': 'oak', 'dwarf': 'stone', 'elf': 'elven', 'halfling': 'snug', 'orc': 'hide', 'halforc': 'hide'}
DYES = {'blue': (110, 150, 220), 'red': (200, 80, 70), 'green': (100, 170, 100), 'ochre': (214, 170, 70),
        'black': (90, 90, 100), 'white': (226, 222, 214)}
DYE_PRICE = 15 * SILVER
GUILD_OF = {'anvil': 'hammer', 'workbench': 'lodge', 'loom': 'needle'}

# what the weekly roll can bring, and what each defence takes off it
OUTCOMES = ('theft', 'broken', 'squatters', 'fire', 'flood', 'snow', 'raid', 'evil')
DEFENCES = {'lock': ('A lock', .25), 'palisade': ('The palisade', .3), 'dog': ('A dog', .3),
            'caretaker': ('A caretaker', .5), 'snares': ('Snares', .2), 'rune': ('A rune on the door', .2),
            'guards': ('Guards', .6)}
SQUAT = {'bandits': (['bandit', 'bandit', 'brigand'], 'bandits'), 'beast': (['wolf', 'wolf', 'boar'], 'a pack of beasts'),
         'goblins': (['goblin', 'goblin', 'goblin'], 'goblins')}


def homes(game):
    p = game.player
    if not isinstance(getattr(p, 'homes', None), list):
        p.homes = []
    return p.homes


def get(game, hid):
    return next((h for h in homes(game) if h['id'] == hid), None)


def dyes(game):
    p = game.player
    if not isinstance(getattr(p, 'home_dyes', None), list):
        p.home_dyes = []
    return p.home_dyes


def _new(game, kind, **kw):
    hs = homes(game)
    h = dict(id=max([o['id'] for o in hs], default=0) + 1, kind=kind, name='', map=None, x=0, y=0, sid=None,
             cells=[], door=None, stage=0, land='timber', build=None, paid=game.day + SEASON, coin=0, debt=0,
             state='quiet', news=None, heard=True, left=game.day, rolled=game.day, pieces=[], store=[], deliver=[],
             defence=[], squat=None, warmed=False, staff=dict(steward=False, guards=0), price=0, bought=game.day,
             hall=[], kept=None, site=None, lord=None, quartered=False, sown={}, blessed=-1, said_neighbour=False)
    h.update(kw)
    hs.append(h)
    return h


def piece(kind, style='plain', dye=None, item=None):
    return dict(k=kind, style=style, dye=dye, x=None, y=None, broken=False, items=[], set={}, item=item)


def piece_name(pc):
    if pc.get('name'):
        return pc['name']
    if pc['k'] == 'trophy' and pc.get('item') is not None:
        return pc['item'].display_name()
    nm = PIECES[pc['k']][0]
    if pc['k'] in ('post', 'trophy'):
        return nm
    st = STYLES.get(pc['style'], STYLES['plain'])[0]
    return f"{st[0].upper() + st[1:]} {nm.lower()}" + (f", dyed {pc['dye']}" if pc.get('dye') else '')


def piece_look(pc):
    ch = PIECES[pc['k']][1]
    if pc.get('broken'):
        return '%', (150, 120, 100)
    if pc['k'] == 'trophy':
        return ch, (226, 190, 130)
    if pc['k'] == 'post':
        return ch, (196, 160, 90)
    if pc['k'] == 'herbbed':
        return ch, (110, 180, 90)
    if pc['k'] == 'hearth':
        return ch, (240, 140, 60)
    if pc['k'] == 'lamp':
        return ch, (255, 210, 120)
    if pc.get('dye') in DYES:
        return ch, DYES[pc['dye']]
    return ch, STYLES.get(pc['style'], STYLES['plain'])[1]


def price_of(kind, style):
    return max(1, round(PIECES[kind][2] * STYLES.get(style, STYLES['plain'])[2]))


def noun(h):
    if h['kind'] == 'town':
        return 'house'
    if h['kind'] == 'seat':
        return 'seat'
    return STAGES[h['stage']][1]


def title(game, h):
    """'Your house in Thornfield', 'Your cabin, the Grey Fen', 'Ashcombe Manor, your seat'."""
    w = game.world
    if h['kind'] == 'town':
        return f"Your house in {w.settlements[h['sid']].name}"
    if h['kind'] == 'seat':
        st = w.sites[h['site']]
        return f'{st.name}, your seat'
    from . import lands as LN
    area = LN.area_at(w, h['x'], h['y']) or w.region_at(h['x'], h['y']).name
    word = LANDS[h['land']][3] if h['stage'] else ''
    n = STAGES[h['stage']][1]
    if h['land'] == 'long' and h['stage'] in (2, 3):
        n = 'longhouse'
    elif word and h['stage'] in (1, 2):
        n = f'{word} {n}'
    return f'Your {n}, {area}'


STATE_WORD = {'quiet': 'All quiet when you left.', 'theft': 'Someone has been in your chests.',
              'broken': 'Something is broken.', 'squatters': 'Squatters have moved in!', 'fire': 'Fire took part of it.',
              'flood': 'The water came in.', 'snow': 'Snow broke the roof.', 'evil': 'Burnt to the stake.',
              'raid': 'Raiders burnt part of it.',
              'tax': 'Hearth tax owed.', 'building': 'The builders are at work.', 'claimed': 'The new lord claims it.'}


def state_line(game, h):
    if h['kind'] == 'town' and owed(game, h):
        return f"Hearth tax owed: {_fmt(owed(game, h))}."
    if h.get('build'):
        left = h['build']['done'] - game.day
        return f"The builders are at work: {max(0, left)} day{'s' if left != 1 else ''} to go."
    return STATE_WORD.get(h['state'], '')


def _lower(name):
    """'Your cabin, The Grey Fen' inside a sentence: 'your cabin, the Grey Fen'."""
    if name.startswith('Your '):
        name = 'your ' + name[5:]
    return name.replace(', The ', ', the ')


def _where(game, h):
    w = title(game, h).split(', ', 1)[-1]
    return 'the ' + w[4:] if w.startswith('The ') else w


def _fmt(c):
    from .money import fmt
    return fmt(c)


# ------------------------------------------------------------------ where they are
def at(game, x, y):
    """Your built home on this world tile (a seat is entered as its site), or None."""
    return next((h for h in homes(game) if h['kind'] == 'built' and (h['x'], h['y']) == (x, y)), None)


def of_map(game, m):
    """Your homes that lie on map m: a town house on its settlement's map, a built home or seat on its own."""
    k = getattr(m, 'key', None)
    return [h for h in homes(game) if h['map'] == k]


def here(game):
    """The home you stand in, or None."""
    p = game.player
    for h in of_map(game, game.map):
        if h['kind'] != 'town' or (p.x, p.y) in set(map(tuple, h['cells'])) or (p.x, p.y) == tuple(h['door'] or ()):
            return h
    return None


def of_site(game, site):
    return next((h for h in homes(game) if h['kind'] == 'seat' and h['site'] == site.id), None)


def land_at(game, x, y):
    from .world import WORLD_H
    from . import tribes as TR
    b = TR.biome_at(game.maps['over'], x, y) or ''
    if y < WORLD_H * .22 and b not in LAND_OF:
        return 'long'
    return LAND_OF.get(b, 'timber')


def line(game):
    """The line under the map, where you stand on one of your homes (or the stake's tile)."""
    p = game.player
    h = at(game, p.x, p.y) if game.cur == 'over' else here(game)
    if not h:
        return None
    return f"Your {noun(h)}. {state_line(game, h)}" if game.cur == 'over' else state_line(game, h)


# ------------------------------------------------------------------ a town house
def lay_sale(game, s, m):
    """On coming to a settlement: one to a few of its empty houses for sale, a $ on the door. Laid once a season."""
    if s.kind not in FOR_SALE or not getattr(m, 'homes', None):
        return
    mine = {tuple(h['door']) for h in homes(game) if h['kind'] == 'town' and h['map'] == m.key and h['door']}
    sale = getattr(m, 'sale', None)
    if not isinstance(sale, dict) or getattr(m, 'sale_season', None) != game.day // SEASON:
        for door in list((sale or {}).keys()) if isinstance(sale, dict) else []:
            if m.tile(*door) == D.SALEDOOR:
                m.set(door[0], door[1], D.DOOR)
        sale = m.sale = {}
        m.sale_season = game.day // SEASON
        lived = {tuple(getattr(o, 'home_pos', None) or (-1, -1)) for o in m.mons if o.is_npc}
        cands = [i for i, pl in enumerate(m.homes) if pl.door and pl.inside and len(pl.inside) >= 12
                 and tuple(pl.door) not in mine and m.inb(*pl.door) and m.tile(*pl.door) in (D.DOOR, D.ODOOR)]
        random.shuffle(cands)
        cands.sort(key=lambda i: sum(1 for c in m.homes[i].inside if tuple(c) in lived))    # empty ones first
        poor = getattr(m, 'poor', None) or ()
        cx, cy = getattr(m, 'centre', (m.w // 2, m.h // 2))
        for i in cands[:FOR_SALE[s.kind]]:
            pl = m.homes[i]
            size = max(.7, min(1.4, len(pl.inside) / 30))
            near = 1.15 if cheb(pl.x, pl.y, cx, cy) < 18 else 1.0
            low = .6 if any(tuple(c) in poor for c in pl.inside[:3]) else 1.0
            price = round(TOWN_PRICE[s.kind] * size * near * low * 4) * GOLD // 4
            sale[tuple(pl.door)] = dict(i=i, price=price, tax=max(5 * SILVER, round(price / 60 / 500) * 500))
    for door in sale:
        if m.tile(*door) in (D.DOOR, D.ODOOR):
            m.set(door[0], door[1], D.SALEDOOR)


def sale_text(game, s, m, door, sale):
    pl = m.homes[sale['i']]
    rooms = 'two rooms' if getattr(pl, 'annex', None) else 'one room'
    owner = random.Random(door[0] * 31 + door[1]).choice(
        ['The owner moved to the city.', 'The old widow who lived here has died.', 'The family went west.',
         'The last tenant left in a hurry.', 'The owner wants coin more than a roof.'])
    kind = {'dwarf': 'A room cut in the rock', 'halfling': 'A snug home in the hill', 'elf': 'A house of living wood',
            'orc': 'A low house of timber and hide'}.get(s.race, 'A narrow house')
    return (f'{kind}, {rooms}, bare walls. {owner}\n\nPrice: {_fmt(sale["price"])}. Hearth tax: '
            f'{_fmt(sale["tax"])} a season.')


def ask_buy(game, door):
    from . import events as EV
    m, s = game.map, game.here
    sale = (getattr(m, 'sale', None) or {}).get(tuple(door))
    if not sale or s is None:
        return 0
    can = game.player.gold >= sale['price']
    EV.ask(game, 'home_buy', 'A house for sale', sale_text(game, s, m, door, sale),
           [(f'Buy it for {_fmt(sale["price"])}', 'buy' if can else None), ('Walk on', 'leave')], door=tuple(door))
    return 0


def r_buy(game, choice, ctx):
    if choice != 'buy':
        return
    m, s, p = game.map, game.here, game.player
    door = tuple(ctx['door'])
    sale = (getattr(m, 'sale', None) or {}).get(door)
    if not sale or p.gold < sale['price']:
        return
    p.gold -= sale['price']
    from . import tally as TY
    TY.add(game, 'spent_homes', sale['price'])
    pl = m.homes[sale['i']]
    del m.sale[door]
    m.set(door[0], door[1], D.DOOR)
    cells = sorted({tuple(c) for c in pl.inside if m.inb(*c) and D.TILES[m.tile(*c)].walk or
                    m.tile(*c) in (D.BED, D.TABLE, D.BARREL, D.CHEST, D.HEARTH)})
    floor = next((m.tile(*c) for c in cells if m.tile(*c) in (D.FLOOR, D.PLANK)), D.FLOOR)
    for c in cells:                                  # the last owner took his things
        if not D.TILES[m.tile(*c)].walk:
            m.set(c[0], c[1], floor)
    _move_out(game, m, pl, set(cells))
    style = STYLE_OF.get(s.race, 'plain')
    h = _new(game, 'town', map=m.key, sid=s.id, x=s.x, y=s.y, cells=[list(c) for c in cells], door=list(door),
             price=sale['price'], tax=sale['tax'], floor=floor)
    h['name'] = title(game, h)
    post = piece('post')
    h['store'] += [piece('bed', style), post]
    _put_first(game, h, m, post, near=door)
    _put_first(game, h, m, h['store'][0], far=door)
    apply(game, m)
    game.msg(f'The house is yours. The key is cold and heavy in your hand. Hearth tax: {_fmt(sale["tax"])} a season, '
             f'paid when you come in, or leave coin in the chest by the door.', 'good')
    from . import guide as GD
    GD.tip(game, 'furnish')


def _move_out(game, m, pl, cells):
    """Whoever lived in the house moves in with the neighbours."""
    others = [tuple(c) for o in m.homes if o is not pl for c in o.inside if D.TILES[m.tile(*c)].walk]
    for o in m.mons:
        if not o.is_npc:
            continue
        if tuple(getattr(o, 'home_pos', None) or (-1, -1)) in cells and others:
            o.home_pos = random.choice(others)
        if (o.x, o.y) in cells and others:
            o.x, o.y = o.home_pos if tuple(o.home_pos or (-1, -1)) not in cells else random.choice(others)
            o.path = []


def owed(game, h):
    """Hearth tax owed on a town house, in copper."""
    if h['kind'] != 'town':
        return 0
    seasons = max(0, (game.day - h['paid'] + SEASON - 1) // SEASON) if game.day > h['paid'] else 0
    return seasons * h.get('tax', 0)


def settle(game, h):
    """Coming home: the tax due is paid, from the chest by the door first, then from your purse."""
    p = game.player
    while h['kind'] == 'town' and game.day > h['paid']:
        tax = h.get('tax', 0)
        if h['coin'] >= tax:
            h['coin'] -= tax
        elif p.gold >= tax - h['coin']:
            p.gold -= tax - h['coin']
            h['coin'] = 0
        else:
            game.msg(f'The reeve has been: you owe {_fmt(owed(game, h))} of hearth tax, and cannot pay it all.', 'bad')
            return
        h['paid'] += SEASON
        from . import tally as TY
        TY.add(game, 'spent_homes', tax)
        game.msg(f'You pay the hearth tax for the season: {_fmt(tax)}.', 'info')


def _sell_unpaid(game, h):
    """A year unpaid: the town sells the house; half back, less the debt; your things wait at the town hall."""
    w = game.world
    s = w.settlements[h['sid']]
    debt = owed(game, h)
    back = max(0, h['price'] // 2 - debt)
    things = [it for pc in h['pieces'] + h['store'] for it in pc.get('items', [])]
    things += [pc['item'] for pc in h['pieces'] + h['store'] if pc.get('item') is not None]
    homes(game).remove(h)
    m = game.maps.get(h['map'])
    if m is not None:
        unapply(game, m, h)
    hall = game.player.__dict__.setdefault('home_hall', {})
    got = hall.setdefault(str(s.id), dict(coin=0, items=[]))
    got['coin'] += back
    got['items'] += things
    from . import news as NW
    NW.post(game, 'home', f'The town of {s.name} has sold a house for a year of unpaid hearth tax.', s.x, s.y)
    game.msg(f'Word reaches you: {s.name} has sold your house for a year of unpaid tax. The reeve keeps '
             f'{_fmt(back)} and your things for you at the town hall.', 'bad')


def town_hall(game, s):
    """In a town that sold your house: the reeve hands back the coin and your things."""
    hall = game.player.__dict__.get('home_hall') or {}
    got = hall.get(str(s.id))
    if not got:
        return
    p = game.player
    p.gold += got['coin']
    keep = []
    for it in got['items']:
        if not game.add_to_inv(it):
            keep.append(it)
    game.msg(f'The reeve hands you back {_fmt(got["coin"])}' + (' and the things from your chests.' if got['items'] else '.'), 'info')
    got['coin'], got['items'] = 0, keep
    if not keep:
        del hall[str(s.id)]


# ------------------------------------------------------------------ building anywhere
def stake_item(game):
    from .entities import Item
    it = Item(game.new_id(), 'tool', 'stake')
    it.name = "Builder's Stake"
    return it


def stake_spot(game, x, y):
    """Why this world tile will not take a stake, or None."""
    w, om = game.world, game.maps['over']
    if game.cur != 'over':
        return 'Drive the stake in out on the open land, on the world map.'
    t = om.tile(x, y)
    if not D.TILES[t].walk or t in (D.WATER, D.TOWN, D.CITY, D.ENTR, D.ROAD) or t == getattr(D, 'BRIDGE', -1):
        return 'Not here: you need open land, off the road.'
    if w.settlement_at(x, y) or w.hold_at(x, y):
        return 'Not here: this is someone\'s land.'
    from . import sites as ST
    from . import events as EV
    if ST.site_at(w, x, y) or EV.poi_at(game, x, y) or any((d.x, d.y) == (x, y) for d in w.dungeons.values()):
        return 'Not here: something else stands on this spot.'
    if any(cheb(s.x, s.y, x, y) <= 1 for s in w.settlements):
        return 'Too close to the houses of a settlement. Further out.'
    from . import tribes as TR
    for st in w.sites:
        if TR.is_camp(st) and cheb(st.x, st.y, x, y) <= 6 and not getattr(st, 'friendly', False):
            return 'Not here: a hostile camp is too near.'
    if any(h['kind'] == 'built' and cheb(h['x'], h['y'], x, y) < 3 for h in homes(game)):
        return 'Your own home stands right here.'
    return None


def drive_stake(game, it):
    p = game.player
    why = stake_spot(game, p.x, p.y)
    if why:
        game.msg(why, 'bad')
        return 0
    p.inv.remove(it)
    land = land_at(game, p.x, p.y)
    h = _new(game, 'built', x=p.x, y=p.y, land=land, stage=0, map=None)
    h['map'] = f"home:{h['id']}"
    h['name'] = title(game, h)
    style = 'plain'
    h['store'] += [piece('post'), piece('bed', style), piece('chest', style)]
    game.maps[h['map']] = gen_map(game, h)
    game.msg(f'You drive the stake into the ground. A fire ring, a bedroll, a chest: a camp, and yours. '
             f'Go in with >; from here it can grow, stage by stage, to a keep.', 'good')
    return 1


def need(h):
    """The next stage: (key, noun, coin, timber, stone, days) or None."""
    if h['kind'] == 'built':
        if h['stage'] + 1 >= len(STAGES):
            return None
        k, n, coin, tim, sto, days, _room = STAGES[h['stage'] + 1]
        return k, n, coin * GOLD, tim, sto, days
    if h['kind'] == 'seat':
        if h['stage'] + 1 >= len(SEAT_STAGES):
            return None
        k, n, coin, tim, sto, days = SEAT_STAGES[h['stage'] + 1]
        return k, n, coin * GOLD, tim, sto, days
    return None


def cart_price(game, good, n):
    """What the carpenter asks to cart goods out to you: half again over the base price."""
    return round(D.GOODS[good]['base'] * 100 * 1.5) * n


def build_options(game, h):
    nd = need(h)
    if not nd or h.get('build'):
        return []
    k, n, coin, tim, sto, days = nd
    p = game.player
    have_t, have_s = p.cargo.get('timber', 0), p.cargo.get('stone', 0)
    short = cart_price(game, 'timber', max(0, tim - have_t)) + cart_price(game, 'stone', max(0, sto - have_s))
    goods = ', '.join(x for x in (f'{tim} timber' if tim else '', f'{sto} stone' if sto else '') if x)
    label = (n[0].upper() + n[1:]) if h['kind'] == 'seat' else f'Build a {n}'
    out = [(f'{label}: {_fmt(coin)}' + (f', {goods}' if goods else '') + f', {days} days',
            'build' if p.gold >= coin and have_t >= tim and have_s >= sto else None)]
    if short:
        out.append((f'{label}, the goods carted out: {_fmt(coin + short)}, {days + 2} days',
                    'buildcart' if p.gold >= coin + short else None))
    return out


def start_build(game, h, cart):
    nd = need(h)
    if not nd:
        return
    k, n, coin, tim, sto, days = nd
    p = game.player
    cost = coin
    if cart:
        cost += cart_price(game, 'timber', max(0, tim - p.cargo.get('timber', 0))) + \
            cart_price(game, 'stone', max(0, sto - p.cargo.get('stone', 0)))
        days += 2
    if p.gold < cost:
        return
    for g, q in (('timber', tim), ('stone', sto)):
        use = min(q, p.cargo.get(g, 0))
        if use:
            p.cargo[g] -= use
            if not p.cargo[g]:
                del p.cargo[g]
    p.gold -= cost
    from . import tally as TY
    TY.add(game, 'spent_homes', cost)
    h['build'] = dict(to=h['stage'] + 1, done=game.day + days)
    game.msg(f'The builders come with their carts. In {days} days it will stand.' if days else 'It is done.', 'good')


def finish_build(game, h):
    b = h['build']
    h['build'] = None
    h['stage'] = b['to']
    if h['kind'] == 'built':
        h['name'] = title(game, h)
        if STAGES[h['stage']][0] in ('holdfast', 'keep') and 'palisade' not in h['defence']:
            h['defence'].append('palisade')
        if h['stage'] >= 1 and 'lock' not in h['defence']:
            h['defence'].append('lock')
    if h['state'] in ('fire', 'flood', 'snow', 'raid', 'evil', 'broken'):
        h['state'] = 'quiet'
    _remake(game, h)
    from . import news as NW
    NW.post(game, 'home', f'Builders say the {noun(h)} out at {_where(game, h)} is finished.', h['x'], h['y'])
    if game.cur == h['map']:
        game.msg(f'The builders finish: the {noun(h)} stands.', 'good')


def _remake(game, h):
    """The plan changed (a stage built, or lost): a new map; pieces keep their place where they still fit."""
    if h['kind'] == 'town':
        return
    old = game.maps.get(h['map'])
    if game.cur == h['map'] and old is not None:
        h['stale'] = True                 # remade when you next come in
        return
    game.maps[h['map']] = gen_map(game, h)


# ------------------------------------------------------------------ the plan of a home of your own
def gen_map(game, h):
    from .entities import GameMap
    W_, H_ = 46, 26
    wall_fg, floor, ground, _word = LANDS.get(h['land'], LANDS['timber'])
    seat = h['kind'] == 'seat'
    m = GameMap(h['map'], 'town', title(game, h), W_, H_, ground)
    m.home, m.sid, m.hid, m.site, m.signs = h['id'], None, None, None, []
    m.radius, m.wall_fg = 60, wall_fg
    rnd = random.Random(h['id'] * 977 + h['stage'])
    for y in range(H_):
        for x in range(W_):
            r = rnd.random()
            if h['land'] == 'log' and r < .12:
                m.set(x, y, D.TREE)
            elif h['land'] == 'stone' and r < .05:
                m.set(x, y, D.ROCK)
            elif h['land'] == 'stilts' and r < .3:
                m.set(x, y, D.SHALLOW)
            elif h['land'] == 'clay' and r < .02:
                m.set(x, y, D.ROCK)
    cx, cy = W_ // 2, H_ // 2
    for x in range(0, cx):
        m.set(x, cy, D.PATH)
    inside, glows = [], []
    if seat:
        inside, door = _seat_plan(m, h, cx, cy, floor, rnd)
    elif h['stage'] == 0:
        m.set(cx, cy, D.FIREPIT)
        glows.append((cx, cy, (255, 140, 50), 5))
        inside = [(x, y) for y in range(cy - 3, cy + 4) for x in range(cx - 6, cx + 7)
                  if ((x - cx) / 6.5) ** 2 + ((y - cy) / 3.5) ** 2 <= 1 and (x, y) != (cx, cy)]
        for c in inside:
            if not D.TILES[m.tile(*c)].walk or m.tile(*c) == D.SHALLOW:
                m.set(c[0], c[1], ground)
        door = (cx - 7, cy)
    else:
        key = STAGES[h['stage']][0]
        bw, bh = {'hut': (7, 5), 'cabin': (13, 7), 'house': (15, 9), 'holdfast': (15, 9), 'keep': (13, 11)}[key]
        x0, y0 = cx - bw // 2, cy - bh // 2
        if h['land'] == 'stilts':                 # a deck on posts over the wet ground
            for y in range(y0 - 2, y0 + bh + 2):
                for x in range(x0 - 2, x0 + bw + 2):
                    m.set(x, y, D.PLANK)
            for x in range(0, x0 - 2):
                m.set(x, cy, D.PLANK)
        thick = 2 if key == 'keep' else 1
        for y in range(y0, y0 + bh):
            for x in range(x0, x0 + bw):
                edge = x < x0 + thick or x >= x0 + bw - thick or y < y0 + thick or y >= y0 + bh - thick
                m.set(x, y, D.WALL if edge else floor)
        if key in ('cabin', 'house', 'holdfast'):  # a wall between two rooms, with a door
            wx = x0 + bw // 2
            for y in range(y0, y0 + bh):
                m.set(wx, y, D.WALL)
            m.set(wx, cy, D.DOOR)
        if key == 'keep':                          # towers at the corners
            for tx, ty in ((x0 - 1, y0 - 1), (x0 + bw - 2, y0 - 1), (x0 - 1, y0 + bh - 2), (x0 + bw - 2, y0 + bh - 2)):
                for y in range(ty, ty + 3):
                    for x in range(tx, tx + 3):
                        m.set(x, y, D.WALL)
        door = (x0, cy)
        for t in range(thick):
            m.set(x0 + t, cy, floor)
        m.set(x0, cy, D.DOOR)
        inside = [(x, y) for y in range(y0, y0 + bh) for x in range(x0, x0 + bw) if m.tile(x, y) == floor]
        if key in ('holdfast', 'keep'):           # the palisade (or a stone wall) round it, a gate to the west
            rx0, ry0, rx1, ry1 = x0 - 5, max(1, y0 - 4), x0 + bw + 4, min(H_ - 2, y0 + bh + 3)
            ring = D.WALL if key == 'keep' else D.PALISADE
            for x in range(rx0, rx1 + 1):
                for y in (ry0, ry1):
                    m.set(x, y, ring)
            for y in range(ry0, ry1 + 1):
                for x in (rx0, rx1):
                    m.set(x, y, ring)
            for y in range(ry0 + 1, ry1):
                for x in range(rx0 + 1, rx1):
                    if (x, y) not in inside and m.tile(x, y) in (D.TREE, D.ROCK, D.SHALLOW):
                        m.set(x, y, ground)
            m.set(rx0, cy, D.PATH)
            m.set(rx1 - 1, ry0 + 1, D.PALISADE if key == 'holdfast' else D.WALL)    # the watch post
        glows.append((x0 + 2, cy, (255, 150, 60), 3))
    m.inside = [list(c) for c in inside]
    m.glows = glows
    m.lights = list(glows)
    m.entry = (0, cy)
    m.centre = (cx, cy)
    for i in range(len(m.seen)):
        m.seen[i] = 1
    h['cells'] = [list(c) for c in inside]
    h['door'] = list(door)
    _refit(game, h, m)
    apply(game, m)
    return m


def _seat_plan(m, h, cx, cy, floor, rnd):
    """A seat: the hall, the chambers, a stable and a trophy hall inside a wall. The ruin first, mended stage by stage."""
    st = SEAT_STAGES[h['stage']][0]
    x0, y0, bw, bh = cx - 10, cy - 6, 21, 13
    for y in range(y0, y0 + bh):
        for x in range(x0, x0 + bw):
            edge = x in (x0, x0 + bw - 1) or y in (y0, y0 + bh - 1)
            m.set(x, y, D.WALL if edge else floor)
    for y in range(y0, y0 + bh):                  # the hall, the chambers, the trophy hall
        m.set(x0 + 12, y, D.WALL)
    for x in range(x0 + 12, x0 + bw):
        m.set(x, cy, D.WALL)
    m.set(x0 + 12, cy - 3, D.DOOR)
    m.set(x0 + 12, cy + 3, D.DOOR)
    m.set(x0 + 16, cy, D.DOOR)
    door = (x0, cy)
    m.set(x0, cy, D.DOOR)
    for y in range(y0 + bh + 1, y0 + bh + 5):     # the stable, below
        for x in range(x0 + 2, x0 + 11):
            m.set(x, y, D.WALL if y == y0 + bh + 4 or x in (x0 + 2, x0 + 10) else D.PLANK)
    m.set(x0 + 6, y0 + bh, D.DOOR)
    m.set(x0 + 6, y0 + bh - 1, floor)
    wx0, wy0, wx1, wy1 = x0 - 4, max(1, y0 - 3), x0 + bw + 3, min(m.h - 1, y0 + bh + 6)
    if st in ('walled', 'whole'):
        for x in range(wx0, wx1 + 1):
            m.set(x, wy0, D.WALL)
            m.set(x, wy1, D.WALL)
        for y in range(wy0, wy1 + 1):
            m.set(wx0, y, D.WALL)
            m.set(wx1, y, D.WALL)
        m.set(wx0, cy, D.PATH)
    if st == 'whole':
        for y in range(wy0, wy0 + 4):
            for x in range(wx1 - 3, wx1 + 1):
                m.set(x, y, D.WALL)
    inside = [(x, y) for y in range(y0, y0 + bh + 5) for x in range(x0, x0 + bw) if m.tile(x, y) in (floor, D.PLANK)]
    if st in ('ruin', 'cleared'):                 # a ruin: holes in the walls, burnt ground, fallen beams
        for y in range(y0, y0 + bh):
            for x in range(x0, x0 + bw):
                if m.tile(x, y) == D.WALL and rnd.random() < (.3 if st == 'ruin' else .15):
                    m.set(x, y, D.ASH)
                elif m.tile(x, y) == floor and rnd.random() < (.35 if st == 'ruin' else .1):
                    m.set(x, y, D.ASH)
        if st == 'ruin':                          # nothing to furnish yet but the corner by the gate: clear it first
            inside = [c for c in inside if cheb(c[0], c[1], *door) <= 3 and m.tile(*c) == floor]
    return inside, door


def _refit(game, h, m):
    """After a new plan: each piece stays where it still fits, else goes back to what you own unplaced."""
    cells = set(map(tuple, h['cells']))
    keep, taken = [], set()
    for pc in h['pieces']:
        c = (pc['x'], pc['y'])
        if c in cells and c not in taken:
            keep.append(pc)
            taken.add(c)
        else:
            pc['x'] = pc['y'] = None
            h['store'].append(pc)
    h['pieces'] = keep
    for pc in [pc for pc in h['store'] if pc['k'] == 'post']:
        _put_first(game, h, m, pc, near=tuple(h['door']))
    for pc in [pc for pc in h['store'] if pc['k'] in ('bed', 'chest') and h['kind'] != 'town'][:2]:
        _put_first(game, h, m, pc, far=tuple(h['door']))


def _put_first(game, h, m, pc, near=None, far=None):
    """Set a piece down on its own: by the door, or as far from it as can be."""
    taken = {(o['x'], o['y']) for o in h['pieces']}
    cells = [tuple(c) for c in h['cells'] if tuple(c) not in taken and D.TILES[m.tile(*c)].walk
             and (not near or tuple(c) != tuple(near))]
    if near:
        cells = [c for c in cells if not _blocks(m, h, c)]
        cells.sort(key=lambda c: cheb(c[0], c[1], *near))
    elif far:
        cells = [c for c in cells if not _blocks(m, h, c)]
        cells.sort(key=lambda c: -cheb(c[0], c[1], *far))
    if not cells:
        return False
    pc['x'], pc['y'] = cells[0]
    if pc in h['store']:
        h['store'].remove(pc)
    h['pieces'].append(pc)
    return True


def _blocks(m, h, c):
    """A piece here would shut the way through the door (keep the cells next to doors free)."""
    x, y = c
    return any(m.inb(x + dx, y + dy) and m.tile(x + dx, y + dy) in (D.DOOR, D.ODOOR, D.SALEDOOR)
               for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))


# ------------------------------------------------------------------ the pieces on the map
def apply(game, m):
    """Lay the pieces of your homes on map m: their tiles, the look of each (m.furn), the lamps' light."""
    mine = of_map(game, m)
    if not mine and not getattr(m, 'furn', None):
        return
    furn = {}
    benches = getattr(m, 'guild_bench', None)
    for h in mine:
        floor = h.get('floor') or LANDS.get(h['land'], LANDS['timber'])[1]
        cells = {tuple(c) for c in h['cells']}
        for c in cells:
            if m.inb(*c) and m.tile(*c) in PIECE_TILES:
                m.set(c[0], c[1], floor)
            if benches and c in benches:
                del benches[c]
        for pc in h['pieces']:
            c = (pc['x'], pc['y'])
            if c not in cells or not m.inb(*c):
                continue
            furn[c] = piece_look(pc)
            if PIECES[pc['k']][3]:
                continue
            real = PIECES[pc['k']][4]
            m.set(c[0], c[1], getattr(D, real) if real and not pc.get('broken') else D.PIECE)
            gk = GUILD_OF.get(pc['k'])
            if gk and not pc.get('broken') and _rank(game, gk) >= 2:
                m.__dict__.setdefault('guild_bench', {})[c] = gk
        lamps = [(pc['x'], pc['y']) for pc in h['pieces'] if pc['k'] in ('lamp', 'hearth') and not pc.get('broken')]
        if h['kind'] != 'town':
            base = [g_ for g_ in getattr(m, 'glows', []) if (g_[0], g_[1]) not in lamps and len(g_) == 4]
            m.glows = base + [(x, y, (255, 180, 90), 4) for x, y in lamps]
            m.lights = list(m.glows)
    m.furn = furn
    m._look = None


PIECE_TILES = set()


def _init_tiles():
    PIECE_TILES.update({D.PIECE, D.BED, D.HEARTH, D.ANVIL, D.BENCH, D.TABLE, D.BARREL, D.CHEST})


def unapply(game, m, h):
    floor = h.get('floor') or D.FLOOR
    for c in h['cells']:
        c = tuple(c)
        if m.inb(*c) and m.tile(*c) in PIECE_TILES:
            m.set(c[0], c[1], floor)
        if c in getattr(m, 'furn', {}):
            del m.furn[c]


def piece_at(game, x, y, m=None):
    m = m or game.map
    for h in of_map(game, m):
        for pc in h['pieces']:
            if (pc['x'], pc['y']) == (x, y):
                return h, pc
    return None, None


def _rank(game, gk):
    try:
        from . import guilds as GU
        st = GU.state(game)[gk]
        return GU.rank(game, gk) if st.get('joined') else 0
    except Exception:
        return 0


def can_place(game, h, m, pc, x, y):
    """Why the piece cannot go here, or None."""
    if [x, y] not in h['cells'] and (x, y) not in set(map(tuple, h['cells'])):
        return 'Only on the floor of your own home.'
    if any((o['x'], o['y']) == (x, y) for o in h['pieces']):
        return 'Something stands there already.'
    if m.mon_at(x, y) or (game.player.x, game.player.y) == (x, y):
        return 'Someone stands there.'
    if not PIECES[pc['k']][3] and _blocks(m, h, (x, y)):
        return 'It would block the door.'
    if pc['k'] == 'tapestry' and not any(m.inb(x + dx, y + dy) and m.tile(x + dx, y + dy) == D.WALL
                                         for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
        return 'A tapestry hangs against a wall.'
    if pc['k'] == 'herbbed' and h['kind'] == 'town' and False:
        return None
    return None


def place(game, h, pc, x, y):
    m = game.map
    why = can_place(game, h, m, pc, x, y)
    if why:
        return why
    pc['x'], pc['y'] = x, y
    if pc in h['store']:
        h['store'].remove(pc)
    h['pieces'].append(pc)
    if pc['k'] == 'herbbed':
        pc['sown'] = game.day
    apply(game, m)
    return None


def pick_up(game, h, pc):
    if pc['k'] == 'post':
        return 'The doorpost chest stays by the door.'
    m = game.map
    h['pieces'].remove(pc)
    c = (pc['x'], pc['y'])
    pc['x'] = pc['y'] = None
    h['store'].append(pc)
    if m.tile(*c) in PIECE_TILES:
        m.set(c[0], c[1], h.get('floor') or LANDS.get(h['land'], LANDS['timber'])[1])
    apply(game, m)
    return None


def colour(game, h, pc):
    """Cycle a piece through the dyes you own (and back to its own colour)."""
    ds = [d for d in DYES if d in dyes(game)]
    if not ds or pc['k'] in ('post', 'trophy'):
        return 'You have no dyes. The Needle and Loom sells them.'
    order = [None] + ds
    i = order.index(pc.get('dye')) if pc.get('dye') in order else 0
    pc['dye'] = order[(i + 1) % len(order)]
    apply(game, game.map)
    return None


# ------------------------------------------------------------------ comfort
def comfort(game, h):
    """One to three stars: from variety, a set of one style, and trophies. 0 when there is little to see."""
    ps = [pc for pc in h['pieces'] if pc['k'] != 'post' and not pc.get('broken')]
    kinds = {pc['k'] for pc in ps}
    stars = 0
    if len(kinds) >= 4:
        stars += 1
    if len(kinds) >= 8 or sum(1 for pc in ps if pc['k'] == 'trophy') >= 2:
        stars += 1
    styled = [pc['style'] for pc in ps if pc['k'] not in ('trophy',)]
    if len(styled) >= 6 and len(set(styled)) == 1 and styled[0] != 'plain':
        stars += 1                                   # a set of one people's style
    return min(3, stars)


def stars(n):
    return '♦' * n + '◊' * (3 - n)


# ------------------------------------------------------------------ bumping your things
def bump(game, x, y, t):
    """Walking into a door for sale or a piece of your own; None when it is none of these."""
    if t == D.SALEDOOR:
        return ask_buy(game, (x, y))
    h, pc = piece_at(game, x, y)
    if not pc:
        return None
    k = pc['k']
    if pc.get('broken'):
        from . import events as EV
        cost = max(10 * SILVER, price_of(k, pc['style']) // 3) if k not in ('trophy', 'post') else 20 * SILVER
        EV.ask(game, 'home_mend', piece_name(pc), f'The {piece_name(pc).lower()} is broken. A carpenter could mend it.',
               [(f'Mend it: {_fmt(cost)}', 'mend' if game.player.gold >= cost else None), ('Leave it', 'leave')],
               hid=h['id'], at=(x, y), cost=cost)
        return 0
    if k == 'post':
        return post_menu(game, h)
    if k == 'bed':
        return sleep(game, h)
    if k in ('chest', 'strongbox'):
        game.request = ('homechest', h['id'], (x, y))
        return 0
    if k in ('rack', 'stand'):
        return swap_set(game, h, pc)
    if k == 'shelf':
        game.msg('Your books and the pages you found stand on the shelf. You take one down.', 'info')
        game.request = ('journal', 3)
        return 0
    if k == 'hearth':
        from . import calendar as CAL
        if CAL.season(game.day) == 'winter':
            p = game.player
            p.buffs = [b for b in p.buffs if b[0] != 'warm'] + [['warm', 1, D.DAY_LEN // 2, 'Warmed by your hearth']]
        return None                                   # the hearth cooks, as every hearth does
    if k in ('anvil', 'workbench', 'loom'):
        return None                                   # the bench works as every bench does (crafts.py)
    if k == 'shrine':
        p = game.player
        if h.get('blessed') == game.day:
            game.msg('You have prayed here today already. The candle still burns.', 'info')
        else:
            h['blessed'] = game.day
            p.buffs = [b for b in p.buffs if b[3] != 'A blessing at home'] + [['dmg', 5, D.DAY_LEN, 'A blessing at home']]
            game.msg('You light a candle at your shrine and say the old words. (A blessing at home)', 'good')
        return 1
    if k == 'herbbed':
        return herbs(game, h, pc)
    if k in ('kennel', 'stable'):
        return kennel(game, h, pc)
    if k == 'trophy':
        game.msg(f'{piece_name(pc)}. Whoever comes in looks at it first.', 'info')
        return 0
    if k in DECOR:
        game.msg(f'{piece_name(pc)}.', 'info')
        return 0
    return 0


def r_mend(game, choice, ctx):
    if choice != 'mend':
        return
    h = get(game, ctx['hid'])
    _h, pc = piece_at(game, *ctx['at'])
    if not h or not pc or game.player.gold < ctx['cost']:
        return
    game.player.gold -= ctx['cost']
    pc['broken'] = False
    apply(game, game.map)
    if h['state'] == 'broken' and not any(o.get('broken') for o in h['pieces']):
        h['state'] = 'quiet'
    game.msg(f'The {piece_name(pc).lower()} is mended.', 'good')


def sleep(game, h):
    from . import hunger as HU
    from . import trees as TT
    p = game.player
    if game.hostile_visible():
        game.msg('You cannot sleep with enemies in sight.', 'bad')
        return 0
    s = game.stats()
    p.life, p.mana, p.stamina, p.poison = s['max_life'], s['max_mana'], s['max_stamina'], None
    p.food = max(p.food, HU.MAX // 3) if hasattr(HU, 'MAX') else p.food
    game.end_turn(D.DAY_LEN // 3, True)
    n = comfort(game, h)
    p.buffs = [b for b in p.buffs if b[0] != 'regen'] + [['regen', 2, round(D.DAY_LEN * (1 + .5 * n)), 'Well rested']]
    TT.rested(game)
    first = not h.get('warmed')
    h['warmed'] = True
    line = 'You sleep in your own bed, and wake Well rested.'
    if first:
        line = ('The first night under your own roof. ' +
                ('You lie awake a while and look at all you have made of it.' if n else 'It is bare yet, but it is yours.') +
                ' You wake Well rested.')
    if n:
        line += f' (Comfort {stars(n)}: you stay rested longer.)'
    game.msg(line, 'good')
    return 1


def swap_set(game, h, pc):
    """A weapon rack holds a weapon and a shield, an armour stand a set of armour: one bump swaps them with yours."""
    p = game.player
    slots = ('weapon', 'shield') if pc['k'] == 'rack' else ('helm', 'armor', 'gloves', 'belt', 'boots')
    on = pc.setdefault('set', {})
    moved = 0
    for sl in slots:
        if game.eq_item(sl) is not None and game.stuck(sl):
            continue
        cur = game.eq_item(sl)
        hang = on.pop(sl, None)
        if cur is not None:
            p.eq.pop(sl, None)
            if cur in p.inv:
                p.inv.remove(cur)
            on[sl] = cur
            moved += 1
        if hang is not None:
            if not game.add_to_inv(hang):
                on[sl] = hang
                continue
            game.equip(hang)
            moved += 1
    game.clamp_vitals()
    if not moved:
        game.msg(f'The {piece_name(pc).lower()} stands empty, and you have nothing in hand for it.', 'info')
        return 0
    game.msg(f'You swap your gear at the {piece_name(pc).lower()}.', 'info')
    return 1


HERB_KEYS = ('yarrow', 'moonpetal', 'feverfew', 'nettle', 'chamomile', 'mint')


def herbs(game, h, pc):
    from . import foraging as FG
    sown = pc.get('sown', game.day)
    if game.day - sown < 4:
        left = 4 - (game.day - sown)
        game.msg(f'Green shoots. In {left} day{"s" if left != 1 else ""} there will be something to pick.', 'info')
        return 0
    rnd = random.Random(h['id'] * 7 + sown)
    key = rnd.choice([k for k in HERB_KEYS if k in FG.PLANTS] or ['yarrow'])
    it = FG.make_plant(game, key, 2 + rnd.randint(0, 2))
    if not game.add_to_inv(it):
        game.msg('Your bag is full.', 'bad')
        return 0
    pc['sown'] = game.day
    game.msg(f'You pick {it.display_name()} from your herb bed.', 'good')
    return 1


def kennel(game, h, pc):
    from . import mercs as MC
    from . import events as EV
    kept = pc.get('kept')
    opts = []
    for slot in ('beast', 'beast2'):
        mc = MC.with_you(game, slot)
        if mc and not kept:
            opts.append((f'Leave {mc.name} here', f'leave:{slot}'))
    if kept is not None:
        opts.append((f'Take {kept.name} with you', 'take'))
    if not opts:
        game.msg(f'The {piece_name(pc).lower()} stands empty. A tamed beast could stay here while you are away.', 'info')
        return 0
    EV.ask(game, 'home_kennel', piece_name(pc), 'A dry stall, fresh straw, a bowl of water.', opts + [('Leave it', 'no')],
           hid=h['id'], at=(pc['x'], pc['y']))
    return 0


def r_kennel(game, choice, ctx):
    _h, pc = piece_at(game, *ctx['at'])
    h = get(game, ctx['hid'])
    if not pc or not h:
        return
    if choice.startswith('leave:'):
        slot = choice[6:]
        mc = getattr(game, slot, None)
        if not mc:
            return
        setattr(game, slot, None)
        game.map.mons = [o for o in game.map.mons if getattr(o, 'merc', None) is not mc and getattr(o, 'mc', None) is not mc]
        from . import mercs as MC
        MC.sync(game)
        pc['kept'] = mc
        if 'dog' not in h['defence'] and getattr(mc, 'species', '') in ('dog', 'wolf', 'hound'):
            h['defence'].append('dog')
        game.msg(f'{mc.name} settles into the straw. It will keep the place while you are gone.', 'info')
    elif choice == 'take':
        from . import mercs as MC
        slot = MC.beast_room(game)
        if not slot:
            game.msg('You already have as many beasts with you as you can keep.', 'bad')
            return
        mc = pc.pop('kept')
        setattr(game, slot, mc)
        mc.slot = slot
        MC.sync(game)
        game.msg(f'{mc.name} comes out, stretching.', 'info')


# ------------------------------------------------------------------ the doorpost chest: the business of the house
def post_menu(game, h):
    from . import events as EV
    p = game.player
    opts, text = [], [f'{h["name"]}. {state_line(game, h)}']
    if h['kind'] == 'town':
        due = owed(game, h)
        text.append(f'Hearth tax {_fmt(h["tax"])} a season, paid to the {_season_name(h["paid"])}. '
                    f'Coin left in the chest: {_fmt(h["coin"])}.')
        if due:
            opts.append((f'Pay the tax owed: {_fmt(due)}', 'pay' if p.gold >= due else None))
        opts.append((f'Leave {_fmt(h["tax"])} in the chest for the reeve', 'leavecoin' if p.gold >= h['tax'] else None))
    opts += build_options(game, h)
    if h['kind'] != 'town':
        for d, (nm, _cut) in DEFENCES.items():
            if d in h['defence'] or d in ('palisade', 'guards', 'lock'):
                continue
            if d == 'dog':
                opts.append((f'Keep a dog here: {_fmt(2 * GOLD)}, and {DOG_FOOD}c a day for its food',
                             'dog' if p.gold >= 2 * GOLD else None))
            elif d == 'caretaker':
                opts.append((f'Hire a caretaker to stay: {CARETAKER_WAGE}c a day', 'caretaker'))
            elif d == 'snares':
                ok = p.disc.get('cunning', [0])[0] >= 10
                opts.append(('Set snares round the house (Cunning 10)', 'snares' if ok else None))
            elif d == 'rune':
                ok = p.disc.get('arcane', [0])[0] >= 10
                opts.append(('Cut a rune on the door (Arcane 10)', 'rune' if ok else None))
        if 'caretaker' in h['defence']:
            opts.append(('Let the caretaker go', 'nocaretaker'))
        if h['defence']:
            text.append('Defences: ' + ', '.join(DEFENCES[d][0].lower() for d in h['defence'] if d in DEFENCES) + '.')
    if h['kind'] == 'seat':
        stf = h['staff']
        text.append(f'A steward {"keeps the books" if stf["steward"] else "would keep the books"} '
                    f'({STEWARD_WAGE}c a day); {stf["guards"]} guard{"s" if stf["guards"] != 1 else ""} on the wall '
                    f'({GUARD_WAGE}c a day each).')
        if not stf['steward']:
            opts.append(('Take on a steward', 'steward'))
        if stf['guards'] < 4:
            opts.append(('Take on a guard', 'guard'))
        if stf['guards']:
            opts.append(('Let a guard go', 'noguard'))
        opts.append((f'Leave coin for the wages: {_fmt(5 * GOLD)}', 'leavewages' if p.gold >= 5 * GOLD else None))
    opts.append(('Close the chest', 'leave'))
    EV.ask(game, 'home_post', 'The doorpost chest', '\n'.join(text), opts, hid=h['id'])
    return 0


def _season_name(day):
    from . import calendar as CAL
    return CAL.season(day) + ' ' + str(CAL._split(day)[0])


def r_post(game, choice, ctx):
    h = get(game, ctx['hid'])
    p = game.player
    if not h or choice in (None, 'leave'):
        return
    if choice == 'pay':
        settle(game, h)
    elif choice == 'leavecoin' and p.gold >= h['tax']:
        p.gold -= h['tax']
        h['coin'] += h['tax']
        game.msg(f'You leave {_fmt(h["tax"])} in the chest. The reeve will take the tax from it.', 'info')
    elif choice in ('build', 'buildcart'):
        start_build(game, h, choice == 'buildcart')
    elif choice == 'dog' and p.gold >= 2 * GOLD:
        p.gold -= 2 * GOLD
        h['defence'].append('dog')
        game.msg('A rough-coated dog from a farm nearby. It growls at every stranger.', 'info')
    elif choice == 'caretaker':
        h['defence'].append('caretaker')
        game.msg('An old soldier takes the job: he will sleep by the door and keep an eye on things.', 'info')
    elif choice == 'nocaretaker' and 'caretaker' in h['defence']:
        h['defence'].remove('caretaker')
        game.msg('You pay off the caretaker.', 'info')
    elif choice == 'snares':
        h['defence'].append('snares')
        game.end_turn(30, True)
        game.msg('You set snares in the brush round the house, where a stranger would come.', 'info')
    elif choice == 'rune':
        h['defence'].append('rune')
        game.msg('You cut a rune of warding in the door. It glows once, and is still.', 'info')
    elif choice == 'steward':
        h['staff']['steward'] = True
        game.msg('A steward comes to keep the books: he pays the wages from the chest.', 'info')
    elif choice == 'guard':
        h['staff']['guards'] += 1
        if 'guards' not in h['defence']:
            h['defence'].append('guards')
    elif choice == 'noguard' and h['staff']['guards']:
        h['staff']['guards'] -= 1
        if not h['staff']['guards'] and 'guards' in h['defence']:
            h['defence'].remove('guards')
    elif choice == 'leavewages' and p.gold >= 5 * GOLD:
        p.gold -= 5 * GOLD
        h['coin'] += 5 * GOLD
        game.msg(f'You leave {_fmt(5 * GOLD)} in the chest for the wages.', 'info')


def wages(h):
    w = 0
    if 'caretaker' in h['defence']:
        w += CARETAKER_WAGE
    if 'dog' in h['defence']:
        w += DOG_FOOD
    if h['kind'] == 'seat':
        w += (STEWARD_WAGE if h['staff']['steward'] else 0) + GUARD_WAGE * h['staff']['guards']
    return w


def upkeep(game):
    """About what your homes cost a day: taxes, wages, food."""
    return sum(wages(h) + (h.get('tax', 0) // SEASON if h['kind'] == 'town' else 0) for h in homes(game))


# ------------------------------------------------------------------ coming home
def enter(game, h):
    """Into a built home or a seat, from the world map."""
    p = game.player
    if game.cur == 'over':
        game.over_pos = (p.x, p.y) if h['kind'] == 'built' else (h['x'], h['y'])
    if h.pop('stale', False) or h['map'] not in game.maps:
        game.maps[h['map']] = gen_map(game, h)
    game.cur = h['map']
    m = game.map
    apply(game, m)
    p.x, p.y = m.entry[0] + 1, m.entry[1]
    game.msg(f'You come home to {_lower(h["name"])}. {state_line(game, h)}', 'info')
    on_enter(game, h, m)
    game.compute_fov()
    game.request = ('save',)
    return 1


def on_enter(game, h, m):
    h['heard'] = True
    settle(game, h)
    if h['squat']:
        _squatters(game, h, m)
    if h['state'] == 'theft':
        game.msg('The chests stand open. Someone has been through them.', 'bad')
        h['state'] = 'quiet'
    if h['state'] == 'claimed':
        claim(game, h)
    if h['kind'] != 'town' and any(pc['k'] == 'post' for pc in h['pieces']):
        from . import guide as GD
        GD.tip(game, 'furnish')
    arrived = [d for d in h['deliver'] if d['day'] <= game.day]
    for d in arrived:
        h['deliver'].remove(d)
        h['store'].append(d['piece'])
    if arrived:
        game.msg(f'The carter has left what you ordered by the door: {", ".join(piece_name(d["piece"]) for d in arrived)}.', 'info')


def on_town(game, s, m):
    """Coming to a settlement: houses for sale, your own house's tax, word of your other homes, the town hall."""
    lay_sale(game, s, m)
    town_hall(game, s)
    lay_carpenter(game, s, m)
    for h in of_map(game, m):
        apply(game, m)
        settle(game, h)
        n = comfort(game, h)
        if n >= 2 and not h.get('said_neighbour'):
            h['said_neighbour'] = True
            game.msg('A neighbour leans over the fence: "I hear you have made your house a fine one. Bring me in '
                     'some evening and show me."', 'info')
    heard(game, s)


def heard(game, s):
    """Word of your homes reaches you where you are, as fast as news walks."""
    from . import news as NW
    for h in homes(game):
        if h['heard'] or not h['news']:
            continue
        d = cheb(h['x'], h['y'], s.x, s.y)
        if (game.day - h.get('news_day', game.day)) * NW.SPEED >= d - 6:
            h['heard'] = True
            game.msg(h['news'], 'bad' if h['state'] not in ('quiet', 'building') else 'info')
            game.__dict__.setdefault('rumours', []).append(h['news'])


def _squatters(game, h, m):
    from .entities import make_monster
    keys, _who = SQUAT.get(h['squat'], SQUAT['bandits'])
    lvl = max(1, min(30, game.world.danger_at(h['x'], h['y']) * 2 + game.player.lvl // 3))
    cells = [tuple(c) for c in h['cells'] if not m.mon_at(*c) and D.TILES[m.tile(*c)].walk]
    random.shuffle(cells)
    for k, c in zip(keys, cells):
        mon = make_monster(game, k, c[0], c[1], lvl)
        mon.awake = True
        mon.squat = h['id']
        m.mons.append(mon)
    h['squat'] = None
    h['squat_on'] = True
    game.msg(f'There are {SQUAT.get(h.get("squat_kind") or "bandits", SQUAT["bandits"])[1]} in your home!', 'bad')


def after_fight(game):
    """Squatters beaten: the home is quiet again."""
    m = game.map
    hid = getattr(m, 'home', None)
    hs = [h for h in of_map(game, m) if h.get('squat_on')]
    for h in hs:
        if not any(getattr(o, 'squat', None) == h['id'] and o.hp > 0 for o in m.mons):
            h['squat_on'] = False
            h['state'] = 'quiet'
            game.msg('The last of the squatters is gone. Your home is your own again.', 'good')
    return hid


# ------------------------------------------------------------------ the week away: the roll
def chance(game, h):
    """The chance that something befalls this home this week (never zero in the wild)."""
    if h['kind'] == 'town':
        return 0.0
    w = game.world
    danger = w.danger_at(h['x'], h['y'])
    road = min(10, w.off_road(h['x'], h['y']) // 3)
    town = min((cheb(s.x, s.y, h['x'], h['y']) for s in w.settlements), default=40)
    c = .05 + danger * .015 + road * .01 + min(1.0, town / 40) * .04
    for d in h['defence']:
        if d in DEFENCES:
            c *= 1 - DEFENCES[d][1]
    return max(.02, min(.5, c))


def weights(game, h):
    """What it would be, if something comes: each outcome's weight here."""
    from . import calendar as CAL
    from .world import WORLD_H
    w = game.world
    season = CAL.season(game.day)
    om = game.maps['over']
    water = any(om.inb(h['x'] + dx, h['y'] + dy) and om.tile(h['x'] + dx, h['y'] + dy) == D.WATER
                for dx in range(-2, 3) for dy in range(-2, 3))
    out = {'theft': 4, 'broken': 3, 'squatters': 3 if h['stage'] >= 1 or h['kind'] == 'seat' else 1}
    if season == 'summer' and h['land'] in ('log', 'sod', 'clay', 'timber'):
        out['fire'] = 2
    if water:
        out['flood'] = 2
    if season == 'winter' and (h['y'] < WORLD_H * .3 or h['land'] == 'long'):
        out['snow'] = 2
    from . import tribes as TR
    for st in w.sites:                                # a roused camp nearby sends its warriors
        if TR.is_camp(st) and cheb(st.x, st.y, h['x'], h['y']) <= 10:
            cm = game.maps.get(st.map_key)
            if cm is not None and getattr(cm, 'roused', False):
                out['raid'] = 3
    tl = getattr(w, 'taint', None)
    from .world import WORLD_W
    if tl and tl[h['y'] * WORLD_W + h['x']]:
        out['evil'] = 3
    return out


def weekly(game):
    """Each week away: a roll for every home of yours out on the land."""
    for h in list(homes(game)):
        if h['kind'] == 'town' or game.cur == h['map']:
            h['rolled'] = game.day
            continue
        if game.day - h.get('rolled', game.day) < 7:
            continue
        h['rolled'] = game.day
        if h.get('quartered'):
            continue
        if random.random() < chance(game, h):
            ws = weights(game, h)
            roll(game, h, random.choices(list(ws), list(ws.values()))[0])


def roll(game, h, what):
    """Something befalls a home while you are away: what it does, and the word that goes round."""
    from . import news as NW
    where = _where(game, h)
    n = noun(h)
    who = random.choice(['A drover', 'A woodcutter', 'A pedlar', 'A shepherd', 'A carter', 'A pilgrim'])
    line = None
    if what == 'theft':
        boxes = [pc for pc in h['pieces'] if pc['k'] in ('chest', 'strongbox') and pc.get('items')]
        if boxes:
            pc = random.choice(boxes)
            if pc['k'] == 'strongbox' and random.random() < .6:
                line = f'{who} says someone tried the door of the {n} by {where}, and went away empty-handed.'
            else:
                take = max(1, len(pc['items']) // 3)
                for _ in range(take):
                    pc['items'].pop(random.randrange(len(pc['items'])))
                h['state'] = 'theft'
                line = f'{who} saw a stranger leave the {n} by {where} with a full sack.'
        else:
            line = f'{who} says thieves broke into the {n} by {where}, and found nothing worth the trouble.'
    elif what == 'broken':
        ps = [pc for pc in h['pieces'] if pc['k'] not in ('post', 'trophy') and not pc.get('broken')]
        if ps:
            random.choice(ps)['broken'] = True
            h['state'] = 'broken'
            line = f'{who} says the wind or worse has been at the {n} by {where}: something lies broken.'
    elif what == 'squatters':
        h['squat'] = h['squat_kind'] = random.choice(list(SQUAT))
        h['state'] = 'squatters'
        line = f'{who} says {SQUAT[h["squat"]][1]} have moved into the {n} by {where}.'
    elif what in ('fire', 'flood', 'snow', 'raid'):
        if h['stage'] > (1 if h['kind'] == 'seat' else 0):
            h['stage'] -= 1                            # a stage back, never lost outright
            _remake(game, h)
        for pc in random.sample(h['pieces'], min(2, len(h['pieces']))):
            if pc['k'] not in ('post',):
                pc['broken'] = True
        h['state'] = what
        line = {'fire': f'{who} says smoke rose over the {n} by {where}.',
                'flood': f'{who} says the water came up into the {n} by {where}.',
                'snow': f'{who} says the snow lay so deep on the {n} by {where} that the roof gave way.',
                'raid': f'{who} says warriors from a roused camp burnt the {n} by {where}.'}[what]
    elif what == 'evil':
        if h['kind'] == 'built':
            h['stage'] = 0                             # only a great evil burns it to the stake
            _remake(game, h)
        elif h['stage'] > 1:
            h['stage'] = 1
            _remake(game, h)
        h['state'] = 'evil'
        line = f'{who} says a darkness passed over {where}, and the {n} there burnt to the ground.'
    if line:
        h['news'], h['heard'], h['news_day'] = line, False, game.day
        NW.post(game, 'home', line, h['x'], h['y'])
    if h['kind'] == 'built':
        h['name'] = title(game, h)
    return line


def daily(game):
    """Each day: deliveries, the builders, the wages, the tax, the week's roll, a seat's lord."""
    p = game.player
    for h in list(homes(game)):
        if h.get('build') and game.day >= h['build']['done']:
            finish_build(game, h)
        w = wages(h)
        if w:
            if h['coin'] >= w:
                h['coin'] -= w
            elif p.gold >= w:
                p.gold -= w
            else:
                for d in ('caretaker', 'guards'):
                    if d in h['defence']:
                        h['defence'].remove(d)
                h['staff']['guards'] = 0
                h['staff']['steward'] = False
                game.msg(f'There is no coin for the wages at {h["name"]}: the hired folk have left.', 'bad')
        if h['kind'] == 'town' and game.day - h['paid'] >= SELL_AFTER:
            _sell_unpaid(game, h)
            continue
        if h['kind'] == 'seat':
            seat_lord(game, h)
    weekly(game)


# ------------------------------------------------------------------ a seat
def seat_offer(game, site):
    """At the empty seat of a fallen house: the baron's reeve keeps the keys, and sells to the baron's sworn men."""
    if site.kind != 'seat' or not getattr(site, 'fallen', False) or of_site(game, site):
        return
    from . import events as EV
    R = game.world.realm
    lo = _baron(game, site)
    price = SEAT_PRICE.get(getattr(site, 'style', 'tower'), 200) * GOLD
    if lo is None:
        return
    from . import realms as RL
    ok = _may_buy(game, site)
    who = RL.style(R, lo, False)
    text = (f'A reeve of {who} sits in what is left of the gatehouse, with the keys of {site.name} on his belt. '
            f'"My lord would sell it to one of his own: {_fmt(price)}, as it stands. You would hold it, not rule '
            f'it: no tenants, no dues, no men but those you pay."')
    if not ok:
        text += '\n\n"But you are not his sworn knight, and the lords of this land do not know you well enough."'
    EV.ask(game, 'home_seat', site.name, text,
           [(f'Buy {site.name}: {_fmt(price)}', 'buy' if ok and game.player.gold >= price else None), ('Not now', 'leave')],
           site=site.id, price=price, lord=lo.id)


def _baron(game, site):
    R = getattr(game.world, 'realm', None)
    if R is None or getattr(site, 'house', None) is None:
        return None
    hs = R.houses[site.house]
    b = R.baronies.get(hs.region)
    if b is None or b.lord is None:
        return None
    return R.lords.get(b.lord) if isinstance(R.lords, dict) else None


def _may_buy(game, site):
    R = game.world.realm
    p = game.player
    hs = R.houses[site.house]
    b = R.baronies.get(hs.region)
    kn = getattr(p, 'knight', None) or {}
    if b is not None and kn and kn.get('kid') == b.kingdom:
        return True
    try:
        from . import realms as RL
        return b is not None and RL.favour(game, b.kingdom) >= 2 * RL.FEALTY_FAVOUR
    except Exception:
        return False


def r_seat(game, choice, ctx):
    if choice != 'buy':
        return
    p = game.player
    site = game.world.sites[ctx['site']]
    if p.gold < ctx['price']:
        return
    p.gold -= ctx['price']
    from . import tally as TY
    TY.add(game, 'spent_homes', ctx['price'])
    h = _new(game, 'seat', site=site.id, x=site.x, y=site.y, stage=0, land=land_at(game, site.x, site.y),
             price=ctx['price'], lord=ctx['lord'], map=f'home:seat{site.id}')
    h['name'] = title(game, h)
    h['store'] += [piece('post'), piece('bed', 'oak'), piece('chest', 'oak')]
    game.msg(f'You count out the coin, and the reeve gives you the keys of {site.name}. A ruin, but yours: clear it '
             f'and mend it, stage by stage, at the doorpost chest.', 'good')
    enter(game, h)


def seat_lord(game, h):
    """If the baron who sold it is gone (a war lost, a death), the new lord may claim the seat."""
    lo = _baron(game, game.world.sites[h['site']])
    if lo is None or h.get('lord') in (None, lo.id) or h['state'] == 'claimed':
        return
    h['state'] = 'claimed'
    h['news'], h['heard'], h['news_day'] = (f'Word goes round that the new lord of the land claims {game.world.sites[h["site"]].name}.',
                                            False, game.day)


def claim(game, h):
    from . import events as EV
    price = h['price'] // 3
    EV.ask(game, 'home_claim', 'The new lord\'s man', f'A man in the new lord\'s colours waits in the hall. "My lord '
           f'does not know you. He takes this seat back, unless you pay him {_fmt(price)} for his leave to keep it. '
           f'Else you go with half of what you paid."',
           [(f'Pay {_fmt(price)} and keep it', 'pay' if game.player.gold >= price else None),
            (f'Give it up, for {_fmt(h["price"] // 2)}', 'give')], hid=h['id'], price=price)


def r_claim(game, choice, ctx):
    h = get(game, ctx['hid'])
    if not h:
        return
    lo = _baron(game, game.world.sites[h['site']])
    if choice == 'pay' and game.player.gold >= ctx['price']:
        game.player.gold -= ctx['price']
        h['lord'] = lo.id if lo else None
        h['state'] = 'quiet'
        game.msg('The man counts the coin and goes. The seat is yours, under the new lord.', 'info')
    elif choice == 'give':
        game.player.gold += h['price'] // 2
        for it in [it for pc in h['pieces'] + h['store'] for it in pc.get('items', [])]:
            game.add_to_inv(it)
        homes(game).remove(h)
        game.msg('You hand over the keys, and take what you can carry.', 'bad')
        game.leave_to_over()


def war_call(game):
    """A baron at war quarters his men in the seats of his sworn knights: no roll while they are there."""
    R = getattr(game.world, 'realm', None)
    if R is None:
        return
    for h in homes(game):
        if h['kind'] != 'seat':
            continue
        b = R.baronies.get(R.houses[game.world.sites[h['site']].house].region)
        war = b is not None and any(b.kingdom in (w_['a'], w_['b']) for w_ in R.wars)
        if war and not h['quartered']:
            h['quartered'] = True
            h['news'], h['heard'], h['news_day'] = (f'Your baron quarters his men at {game.world.sites[h["site"]].name} for '
                                                    'the war. They keep it safe, and eat from its stores.', False, game.day)
        elif not war and h['quartered']:
            h['quartered'] = False


# ------------------------------------------------------------------ the carpenter
def lay_carpenter(game, s, m):
    """Every hamlet and town has someone who builds and sells furniture: the carpenter, by the market."""
    if getattr(m, 'carpenter', False) or s.kind not in FOR_SALE:
        return
    m.carpenter = True
    if any(o.is_npc and o.role == 'carpenter' for o in m.mons):
        return
    from .entities import make_npc
    from .towns import town_names
    cx, cy = getattr(m, 'centre', (m.w // 2, m.h // 2))
    spots = [(x, y) for r in range(2, 16) for y in range(cy - r, cy + r + 1) for x in range(cx - r, cx + r + 1)
             if m.inb(x, y) and m.tile(x, y) in (D.PATH, D.GRASS, D.ROAD, D.PLANK, D.FLOOR) and not m.mon_at(x, y)]
    if not spots:
        return
    x, y = spots[0]
    names = town_names(s.race if s.race in ('dwarf', 'halfling', 'orc', 'elf') else 'human')
    word = {'dwarf': 'Stonewright', 'halfling': 'Joiner', 'orc': 'Builder', 'elf': 'Woodshaper'}.get(s.race, 'Carpenter')
    npc = make_npc(game, f'{names.pop() if names else "Hob"} the {word}', 'carpenter', '#c8a070', x, y, True)
    m.mons.append(npc)


def talk(game, npc):
    from . import events as EV
    s = game.here
    p = game.player
    style = STYLE_OF.get(getattr(s, 'race', 'human'), 'plain')
    opts = [(f"A builder's stake, to build out on the land: {_fmt(STAKE)}", 'stake' if p.gold >= STAKE else None)]
    if homes(game):
        opts += [(f'Furniture in the {STYLES[style][0]} style', f'shop:{style}')]
        if style != 'plain':
            opts += [('Plain furniture, cheaper', 'shop:plain')]
    from . import guilds as GU
    if s is not None and 'needle' in GU.halls_in(game, s.id):
        opts.append((f'Dyes of the Needle and Loom: {_fmt(DYE_PRICE)} each', 'dyes'))
    opts.append(('Nothing today', 'leave'))
    text = '"Wood, stone, a good joint. What do you need?"'
    if not homes(game):
        text += ' "Furniture I sell to those with a roof to put it under."'
    EV.ask(game, 'home_carp', npc.name, text, opts)


def r_carp(game, choice, ctx):
    from . import events as EV
    p = game.player
    if choice == 'stake' and p.gold >= STAKE:
        if not game.add_to_inv(stake_item(game)):
            game.msg('Your bag is full.', 'bad')
            return
        p.gold -= STAKE
        game.msg('A stake of seasoned oak, with your mark burnt in. Drive it in where you would build: out on the open '
                 'land, off the road.', 'good')
        from . import guide as GD
        GD.tip(game, 'stake')
    elif choice and choice.startswith('shop:'):
        style = choice[5:]
        opts = [(f'{piece_name(piece(k, style))}: {_fmt(price_of(k, style))}', f'{k}:{style}' if p.gold >= price_of(k, style) else None)
                for k in SHOP_ORDER]
        EV.ask(game, 'home_buypiece', 'Furniture', 'Delivered to your home in a few days, for a small fee, or carried '
               'straight in if your home is in this town.', opts + [('Nothing', 'leave')])
    elif choice == 'dyes':
        opts = [(f'{d[0].upper() + d[1:]} dye', d if p.gold >= DYE_PRICE and d not in dyes(game) else None) for d in DYES]
        EV.ask(game, 'home_dye', 'The Needle and Loom\'s dyes', 'A dye colours a piece of furniture: in your home, '
               'as you set things out.', opts + [('Nothing', 'leave')])


def r_dye(game, choice, ctx):
    if choice in DYES and game.player.gold >= DYE_PRICE:
        game.player.gold -= DYE_PRICE
        dyes(game).append(choice)
        game.msg(f'A crock of {choice} dye, sealed with wax.', 'info')


def r_buypiece(game, choice, ctx):
    from . import events as EV
    if not choice or ':' not in choice:
        return
    k, style = choice.split(':')
    hs = homes(game)
    if not hs:
        return
    if len(hs) == 1:
        return deliver(game, hs[0]['id'], k, style)
    EV.ask(game, 'home_where', 'Where to?', f'Where shall the {piece_name(piece(k, style)).lower()} go?',
           [(h['name'], str(h['id'])) for h in hs][:20], k=k, style=style)


def r_where(game, choice, ctx):
    if choice:
        deliver(game, int(choice), ctx['k'], ctx['style'])


def deliver(game, hid, k, style):
    h = get(game, hid)
    p = game.player
    cost = price_of(k, style)
    s = game.here
    near = s is not None and h['kind'] == 'town' and h['sid'] == s.id
    days = 0 if near else 2 + cheb(h['x'], h['y'], *(game.world_pos())) // 40
    fee = 0 if near else max(10 * SILVER, cost // 20)
    if p.gold < cost + fee:
        game.msg('You cannot afford it, with the carting.', 'bad')
        return
    p.gold -= cost + fee
    from . import tally as TY
    TY.add(game, 'spent_homes', cost + fee)
    pc = piece(k, style)
    if near:
        h['store'].append(pc)
        game.msg(f'You carry the {piece_name(pc).lower()} home yourself.', 'info')
    else:
        h['deliver'].append(dict(day=game.day + days, piece=pc))
        game.msg(f'The {piece_name(pc).lower()} will be at {_lower(h["name"])} '
                 f'in {days} days (carting {_fmt(fee)}).', 'info')


def rare(game, names):
    """Rare pieces (the broken named things of a great boss): carted to your newest home, to hang on its wall."""
    hs = homes(game)
    if not hs or not names:
        return
    h = hs[-1]
    for n in names:
        pc = piece('trophy', 'plain')
        pc['name'] = n
        h['deliver'].append(dict(day=game.day + 5, piece=pc))
    game.msg(f'You gather up the pieces all the same, and send them home to {_lower(h["name"])}: they would look well '
             'on a wall.', 'info')


def take_trophies(game, h):
    """The trophies in your bag can go on the wall: they become pieces you can set out."""
    p = game.player
    got = [it for it in p.inv if it.k == 'trophy' and not p.eq.get('trophy') == it.id]
    for it in got:
        p.inv.remove(it)
        h['store'].append(piece('trophy', 'plain', item=it))
    return len(got)


# ------------------------------------------------------------------ chests
def chest_room(h, pc):
    base = 20 if pc['k'] == 'strongbox' else 10
    if h['kind'] == 'built' and STAGES[h['stage']][0] in ('house', 'holdfast', 'keep'):
        base *= 2                                   # the cellar
    return base


def put_in(game, h, pc, it):
    p = game.player
    if len(pc['items']) >= chest_room(h, pc):
        return 'It is full.'
    if it.id in p.eq.values():
        return 'Take it off first.'
    if getattr(it, 'mission', None):
        return 'That is for a job; keep it with you.'
    p.inv.remove(it)
    pc['items'].append(it)
    return None


def take_out(game, h, pc, it):
    if not game.add_to_inv(it):
        return 'Your bag is full.'
    pc['items'].remove(it)
    return None


def init():
    _init_tiles()
    from . import events as EV
    EV.RESOLVERS.update({'home_buy': r_buy, 'home_mend': r_mend, 'home_kennel': r_kennel, 'home_post': r_post,
                         'home_seat': r_seat, 'home_claim': r_claim, 'home_carp': r_carp, 'home_dye': r_dye,
                         'home_buypiece': r_buypiece, 'home_where': r_where})
