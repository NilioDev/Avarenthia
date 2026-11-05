"""The first steps (round 40, "Playing it" in docs/plan.md): a sure first tome, a letter for the city, the baron's word.

- The first tome hangs on no one place: Snagtooth's hoard holds three tomes of three schools (one was yours; one bears
  a city bookseller's stamp), a village shop may sell one, the temple where you wake has a shelf with one of its god's
  school and a lectern, "The Eleven Ways", that tells of every class and the guild that keeps its tomes, and every
  combat guild's hall sells the first tome of its school once to someone still blank.
- A letter for the city: right after Snagtooth, Elder Berend sends you with a letter and a few loads of Thornfield's
  goods to a merchant in the nearest city; you sell the loads yourself, the merchant tells you what a city has, and his
  answer asks for a city good back home: your first trade on your own.
- The baron's word: in that city a messenger asks you to carry a sealed word to a lord's seat nearby; the lord shows
  you the realm and offers the first realm job.
What belongs to the player lives on the player: `p.first`."""
import random

from . import data as D

GOD_SCHOOL = {'solmara': 'restoration', 'valdric': 'warcraft', 'thessa': 'nature', 'durnak': 'fire', 'skell': 'cunning',
              'morrak': 'shadow'}
GUILD_SCHOOLS = {'magi': ('fire', 'frost', 'storm', 'arcane'), 'iron': ('warcraft',), 'dawn': ('restoration',),
                 'chapter': ('restoration',), 'coven': ('shadow',), 'moot': ('nature',), 'ossuary': ('necromancy',),
                 'hound': ('beastcraft',), 'thieves': ('cunning',)}
SHELF_PRICE = 800          # the temple's shelf: what the den or a first job pays
GUILD_PRICE = 1000         # a hall's first tome, once: what the first jobs pay
LETTER_PAY = 250           # the merchant's pay for the letter: modest
ANSWER_PAY = 150           # the lord's answer, back to the messenger
LOADS = 4
ANSWER_GOODS = ('salt', 'tools', 'cloth')

WAYS = [
    ('fire', 'Pyromancer', 'Fire burns what it touches and goes on burning: bolts, flames that spread, the ground set '
     'alight. A Pyromancer kills fast and is soft when the foe comes close. The Circle of Magi keeps its tomes.'),
    ('frost', 'Rimecaller', 'Frost slows, binds and shatters: a foe held in ice takes the next blow harder. The '
     'Rimecaller keeps a fight at arm\'s length. The Circle of Magi keeps its tomes.'),
    ('storm', 'Stormcaller', 'Storm is lightning that leaps from foe to foe and wind that throws them back. Best against '
     'many at once. The Circle of Magi keeps its tomes.'),
    ('arcane', 'Arcanist', 'Arcane is the craft of runes and gates: signs laid on the ground, a door to step through, '
     'a spell undone. Slow to learn, hard to corner. The Circle of Magi keeps its tomes.'),
    ('restoration', 'Cleric', 'Restoration heals, shields and smites: the dead fear it most. A Cleric lasts where others '
     'fall. The Order of Dawn and the Hallowed Chapter keep its tomes; this temple has one on its shelf.'),
    ('shadow', 'Warlock', 'Shadow pays in your own life for power: curses, drained strength, fire from below. Strong, '
     'and never free. The Hollow Coven keeps its tomes.'),
    ('necromancy', 'Necromancer', 'Necromancy raises the dead to fight for you and turns corpses into weapons. Others '
     'do the dying. The Quiet Ossuary keeps its tomes.'),
    ('nature', 'Druid', 'Nature binds with roots, heals with green things and lends the shape of beasts. The Green Moot '
     'keeps its tomes.'),
    ('beastcraft', 'Beastmaster', 'Beastcraft is a beast at your side and the skills to drive it: the pack fights, you '
     'lead. The Houndwardens\' Lodge keeps its tomes.'),
    ('warcraft', 'Warrior', 'Warcraft is the trained fighter: shield and blade, the shout that holds a line, the last '
     'stand. Plain and hard to kill. The Iron Company keeps its tomes.'),
    ('cunning', 'Rogue', 'Cunning strikes first and from the dark: snares, smoke, poison, the blow on a foe that does '
     'not see you. The Thieves\' Guild keeps its tomes.'),
]


def way(game, place):
    """Which way a place lies from where you are on the world map."""
    from .engine import dir_name
    x, y = game.world_pos()
    return dir_name(place.x - x, place.y - y)


def st(game):
    return game.player.__dict__.setdefault('first', {})


def blank(game):
    return not getattr(game.player, 'classes', [])


def first_skill(line):
    from . import skills as SK
    return next((s for s in SK.SKILL_LIST if s.line == line and s.tier == 0), None)


def tome_of(game, line):
    from .entities import Item
    sk = first_skill(line)
    it = Item(game.new_id(), 'tome', sk.id)
    it.name = f'Tome of {sk.name}'
    return it


def school_name(line):
    from . import skills as SK
    return SK.DISCIPLINES[line]['name']


# ------------------------------------------------------------------ the letter's city
def letter_city(game):
    """The city the letter goes to: the nearest to Thornfield (chosen once)."""
    s = st(game)
    w = game.world
    if s.get('city') is None:
        th = w.settlements[0]
        cities = [c for c in w.settlements if c.is_city and c.id != 0] or [c for c in w.settlements if c.id != 0]
        s['city'] = min(cities, key=lambda c: (max(abs(c.x - th.x), abs(c.y - th.y)), c.id)).id
    return w.settlements[s['city']]


# ------------------------------------------------------------------ Snagtooth's hoard
def hoard(game, m, x, y):
    """Three tomes of three schools in the hoard: one was yours, which you do not know; one bears the stamp of a
    bookseller in the letter's city."""
    from . import skills as SK
    from . import classes as CL
    schools = [k for k in SK.DISC_ORDER if CL.class_line(k)]
    three = random.sample(schools, 3)
    city = letter_city(game)
    stamped = random.randrange(3)
    out = []
    for i, line in enumerate(three):
        it = tome_of(game, line)
        if i == stamped:
            it.stamp, it.stamp_name = city.id, city.name
        it.dropped = False
        game.spill(m, x, y, it)
        out.append(it)
    st(game)['hoard'] = [it.id for it in out]
    return out


# ------------------------------------------------------------------ the temple where you wake
def dress_temple(game, site, m, cx, cy):
    """The start temple: a shelf with a tome of its god's school, and the lectern, The Eleven Ways."""
    m.first = {(cx + 15, cy - 8): 'shelf', (cx + 9, cy - 5): 'lectern'}
    m.set(cx + 9, cy - 5, D.CHAINBOOK)


def temple_school(game):
    from . import gods as GO
    ts = game.world.sites[game.world.start_temple] if getattr(game.world, 'start_temple', None) is not None else None
    god = getattr(ts, 'god', 'solmara') if ts else 'solmara'
    return GOD_SCHOOL.get(god, 'restoration') if god in GO.GODS else 'restoration'


def bump(game, x, y):
    """A thing of the first steps: returns the turns spent, or None when it is not one."""
    from . import events as EV
    from .money import fmt
    m = game.map
    what = getattr(m, 'first', {}).get((x, y))
    if what is None:
        return None
    s = st(game)
    if what == 'lectern':
        EV.ask(game, 'first_ways', 'The Eleven Ways', 'A heavy book on a lectern, chained to it. Each of its eleven '
               'chapters tells of one way a fighter may go, and who keeps the tomes of it. Which do you read?',
               [(f'{name}: {school_name(line)}', line) for line, name, _t in WAYS] + [('Close the book', 'no')])
        return 0
    line = temple_school(game)
    if s.get('shelf'):
        game.msg('The shelf holds hymn books and the temple\'s accounts now; the tome is gone.', 'info')
        return 0
    sk = first_skill(line)
    EV.ask(game, 'first_shelf', 'The temple\'s shelf', f'Among the hymn books stands one tome of {school_name(line)}, the '
           f'school of the temple\'s god: the Tome of {sk.name}. The sisters would part with it for {fmt(SHELF_PRICE)}, '
           'for the poor box.', [(f'Buy it ({fmt(SHELF_PRICE)})', 'buy'), ('Leave it', 'no')])
    return 0


def r_ways(game, choice, ctx):
    if choice == 'no':
        return
    row = next((r for r in WAYS if r[0] == choice), None)
    if row:
        game.request = ('dialog', f'The Eleven Ways: the {row[1]}', row[2])


def r_shelf(game, choice, ctx):
    from .money import fmt
    p = game.player
    if choice != 'buy':
        return
    if p.gold < SHELF_PRICE:
        game.msg(f'You have not the {fmt(SHELF_PRICE)} the sisters ask.', 'bad')
        return
    it = tome_of(game, temple_school(game))
    if not game.add_to_inv(it):
        game.msg('Your pack is full.', 'bad')
        return
    p.gold -= SHELF_PRICE
    st(game)['shelf'] = True
    game.msg(f'You put {fmt(SHELF_PRICE)} in the poor box and take the {it.display_name()}.', 'gold')


# ------------------------------------------------------------------ a guild's first tome
def guild_options(game, key):
    """A combat guild sells the first tome of its school once to someone still blank."""
    from .money import fmt
    if not blank(game) or st(game).get('guild_tome') or key not in GUILD_SCHOOLS:
        return []
    return [(f'Buy a first tome of {school_name(line)} ({fmt(GUILD_PRICE)}; once, for the blank)', 'firsttome:' + line)
            for line in GUILD_SCHOOLS[key]]


def buy_guild_tome(game, line):
    from .money import fmt
    p = game.player
    if p.gold < GUILD_PRICE:
        game.msg(f'The first tome costs {fmt(GUILD_PRICE)}. You cannot afford it.', 'bad')
        return
    it = tome_of(game, line)
    if not game.add_to_inv(it):
        game.msg('Your pack is full.', 'bad')
        return
    p.gold -= GUILD_PRICE
    st(game)['guild_tome'] = line
    game.msg(f'You pay {fmt(GUILD_PRICE)} for the {it.display_name()}. "Read it, and see if it reads you."', 'gold')


# ------------------------------------------------------------------ a letter for the city
def home_good(game):
    th = game.world.settlements[0]
    city = letter_city(game)
    goods = [g for g in getattr(th, 'produce', []) if g in D.GOODS]
    sold = [g for g in goods if g in getattr(city, 'market', {})]
    return (sold or goods or ['grain'])[0]


def give_letter(game, npc):
    """Berend, right after Snagtooth: the letter, the loads, the job."""
    from .entities import Item
    from . import economy as ECO
    s = st(game)
    p = game.player
    city = letter_city(game)
    good = home_good(game)
    n = max(1, min(LOADS, ECO.free_cargo(p) // max(1, D.GOODS[good]['w'])))
    p.cargo[good] = p.cargo.get(good, 0) + n
    letter = Item(game.new_id(), 'quest', 'letter')
    letter.name = f'Letter to a merchant of {city.name}'
    game.add_to_inv(letter)
    s.update(letter='carried', letter_item=letter.id, loads=(good, n))
    game.reveal_route(0, city.id)
    gname = D.GOODS[good]['name'].lower()
    game.request = ('dialog', 'Elder Berend', f'"Back from the Hollow Den with your sword! Then you can do me a service, '
                    f'and see a bit of the world besides.\n\nThis letter is for the trader on the market of '
                    f'{city.name}, to the {way(game, city)}. Thornfield owes that market, and this says how we shall pay. '
                    f'Take these {n} loads of our {gname} with you too: sell them on his market yourself. You will see '
                    f'what a load fetches there, against what it fetches here.\n\nThe road is on your map. When you are '
                    f'back, I have work for you nearer home."\n\n(You receive the letter and {n} loads of {gname}.)')
    from . import chronicle as CH
    CH.add(game, 'Your deeds', f'Elder Berend sent you with a letter and {n} loads of {gname} to {city.name}.', 'seen',
           where=game.loc_name(), key='first_letter', title='A letter for the city', quiet=True)


def merchant(game, npc):
    """The merchant takes the letter, pays, tells what a city has, and asks for a city good back home."""
    from .money import fmt
    from . import guide as GDE
    s = st(game)
    p = game.player
    city = letter_city(game)
    it = next((i for i in p.inv if i.id == s.get('letter_item')), None)
    if it:
        game.remove_one(it)
    p.gold += LETTER_PAY
    s['letter'] = 'given'
    have = [g for g in ANSWER_GOODS if g in city.market and g not in getattr(game.world.settlements[0], 'produce', [])]
    want = (have or [g for g in city.market if g != s.get('loads', ('grain',))[0]] or ['salt'])[0]
    s['want'] = want
    wname = D.GOODS[want]['name'].lower()
    text = (f'"From Berend? Good old Berend." He breaks the seal and reads, and nods. "Here, for your trouble: '
            f'{fmt(LETTER_PAY)}.\n\nFirst time in a city? Then hear this. The guild halls stand in their own streets: '
            f'each sells the first tome of its school to one who has none yet, once. The temple heals and raises the '
            f'dead, for a price. The board at the inn has work, and the caravans go out from the gate. And the market '
            f'pays for what it lacks: your {D.GOODS[s.get("loads", ("grain", 0))[0]]["name"].lower()} sells better here '
            f'than at home, did you see?\n\nMy answer for Berend: Thornfield needs {wname}. Buy some here, sell it '
            f'there, and keep what you make. That is the whole of trade."')
    tome = next((i for i in p.inv if i.k == 'tome' and getattr(i, 'stamp', None) == city.id), None)
    if tome or s.get('read_stamp'):
        text += (f'\n\nHe looks at the tome in your pack. "That stamp is Hessa\'s, the bookseller by the market. She sold '
                 f'that one a year ago, to a traveller who paid in old coin and gave no name. That is all she knows; I '
                 f'asked her once about another."')
        s['trace'] = True
        from . import chronicle as CH
        CH.add(game, 'Your deeds', f'A bookseller of {city.name} sold one of the tomes in Snagtooth\'s hoard to a '
               'traveller who paid in old coin and gave no name: a first trace of who you were.', 'heard',
               where=game.loc_name(), key='first_trace', title='A trace', quiet=True)
    game.request = ('dialog', npc.name, text)
    GDE.tip(game, 'cargo')
    messenger(game, npc)


# ------------------------------------------------------------------ the baron's word
def word_seat(game, city):
    """A lord's seat a day or two from the city: the nearest seat that has not fallen."""
    seats = [x for x in game.world.sites if x.kind == 'seat' and not getattr(x, 'fallen', False)]
    if not seats:
        return None
    return min(seats, key=lambda x: (max(abs(x.x - city.x), abs(x.y - city.y)), x.id))


def city_war(game, city):
    """The war the city's ruler is in, as (kingdom, foe) or None."""
    from . import realms as RL
    R = RL.get(game)
    if R is None:
        return None
    key = R.region_realm[city.region] if city.region < len(R.region_realm) else None
    if not key or key[0] != 'k':
        return None
    kg = R.kingdoms[key[1]]
    for war in R.wars:
        if kg.id in (war['a'], war['b']):
            foe = next((k for k in R.kingdoms if k.id == (war['b'] if war['a'] == kg.id else war['a'])), None)
            return kg, foe
    return None


def messenger(game, npc):
    """A messenger of the city's ruler waits by the market with a sealed word."""
    from .entities import make_npc
    from .worldgen import free_around
    s = st(game)
    if s.get('word') or s.get('word_done'):
        return
    seat = word_seat(game, letter_city(game))
    if seat is None:
        return
    spots = free_around(game, game.map, npc.x, npc.y, 3)
    if not spots:
        return
    m = make_npc(game, 'A messenger in livery', 'messenger', '#d8c890', spots[0][0], spots[0][1], True)
    game.map.mons.append(m)
    s['word'] = 'offered'
    s['seat'] = seat.id


def messenger_talk(game, npc):
    from .entities import Item
    from .money import fmt
    from . import realms as RL
    s = st(game)
    p = game.player
    seat = game.world.sites[s['seat']] if s.get('seat') is not None else None
    if seat is None:
        game.say(npc, 'Safe roads.')
        return
    if s.get('word') == 'offered':
        R = RL.get(game)
        h = R.houses[seat.house] if R and getattr(seat, 'house', None) is not None else None
        city = letter_city(game)
        war = city_war(game, city)
        about = (f'It is about the war with {war[1].short}: the lord is to send his men.' if war and war[1] else
                 'What it says is not for you to know.')
        it = Item(game.new_id(), 'quest', 'word')
        it.name = f'A sealed word for {seat.name}'
        game.add_to_inv(it)
        s.update(word='carried', word_item=it.id)
        game.reveal_place(seat.x, seat.y, 1)
        game.request = ('dialog', npc.name, f'"You are the one who brought Berend\'s letter? Then you know the roads. My '
                        f'lord of {city.name} has a sealed word for {seat.name}, the seat of House '
                        f'{h.name if h else "of the land"}, to the {way(game, seat)}. {about} Bring it there and '
                        f'bring me the answer, and there is coin in it."\n\n(You receive the sealed word. {seat.name} '
                        f'is on your map.)')
        return
    if s.get('word') == 'answer':
        it = next((i for i in p.inv if i.id == s.get('answer_item')), None)
        if it:
            game.remove_one(it)
        p.gold += ANSWER_PAY
        s['word'] = 'done'
        game.request = ('dialog', npc.name, f'"The answer, sealed. Good." He counts out {fmt(ANSWER_PAY)}. "The lords '
                        f'remember who carries their words well."')
        return
    game.say(npc, f'The seat lies to the {way(game, seat)}.' if s.get('word') == 'carried' else 'Safe roads.')


def lord_talk(game, npc):
    """At the seat: the lord takes the word, shows you the realm, offers the first realm job and an answer to take."""
    from .entities import Item
    from . import realms as RL
    from . import realmjobs as RJ
    from . import guide as GDE
    s = st(game)
    m = game.map
    if s.get('word') != 'carried' or getattr(m, 'site', None) != s.get('seat') or getattr(npc, 'role', '') != 'lord':
        return False
    R = RL.get(game)
    lo = R.lord(getattr(npc, 'lord', None)) if R else None
    if lo is None:
        return False
    p = game.player
    it = next((i for i in p.inv if i.id == s.get('word_item')), None)
    if it:
        game.remove_one(it)
    seat = game.world.sites[s['seat']]
    city = letter_city(game)
    game.reveal_route(city.id, city.id)
    show_realm(game, city, seat)
    if not lo.met:
        RL.lord_seen(game, lo)
    ans = Item(game.new_id(), 'quest', 'answer')
    ans.name = f'The answer of {seat.name}'
    game.add_to_inv(ans)
    s.update(word='answer', answer_item=ans.id)
    game.say(npc, '"So. A word from the city." The seal cracks. "Take my answer back with you. And if you want work, '
             'I have some."')
    GDE.tip(game, 'realms')
    RJ.offer(game, npc, lo)
    return True


def show_realm(game, city, seat):
    """The land between the city and the seat known on the map, and the name of the realm it lies in."""
    om = game.maps['over']
    x0, x1 = sorted((city.x, seat.x))
    y0, y1 = sorted((city.y, seat.y))
    for y in range(max(0, y0 - 3), min(om.h, y1 + 4)):
        for x in range(max(0, x0 - 3), min(om.w, x1 + 4)):
            om.seen[y * om.w + x] = 1
    R = getattr(game.world, 'realm', None)
    if R:
        from . import realms as RL
        key = RL.realm_key(game.world, seat.region if hasattr(seat, 'region') else city.region)
        lab = R.labels.get(key)
        if lab:
            om.seen[lab[1] * om.w + lab[0]] = 1


# ------------------------------------------------------------------ talking, selling, the journal
def talk(game, npc):
    """True when the first steps answered this person."""
    role = getattr(npc, 'role', '')
    here = game.here
    s = st(game)
    f = game.flags
    if role == 'elder' and here is not None and here.id == 0:
        if f.get('den') and not s.get('letter'):
            give_letter(game, npc)
            return True
        owed = (f.get('ratking') and not f.get('reward_rat')) or (f.get('grolm') and not f.get('reward_grolm'))
        if s.get('letter') == 'carried' and not owed:
            city = letter_city(game)
            game.request = ('dialog', 'Elder Berend', f'"The letter is for the trader on the market of {city.name}, to '
                            f'the {way(game, city)}. The road is on your map."')
            return True
        if s.get('letter') == 'given' and not s.get('home'):
            s['home'] = True
            if not f.get('met_elder'):
                return False                   # Berend's own welcome: the rats and the mine
            game.request = ('dialog', 'Elder Berend', '"The trader paid, and wants something back? Good: that is how it '
                            'starts. Now, the Rat Warrens and the mine still wait for someone."')
            return True
        return False
    if role == 'market' and here is not None and here.id == s.get('city') and s.get('letter') == 'carried':
        merchant(game, npc)
        return True
    if role == 'market' and game.player.cargo:
        from . import guide as GDE
        GDE.tip(game, 'cargo')
        return False
    if role == 'messenger':
        messenger_talk(game, npc)
        return True
    if role == 'lord':
        return lord_talk(game, npc)
    return False


def on_sell(game, s, g, n):
    """Selling the merchant's answer good at home: your first trade on your own."""
    fs = st(game)
    if s.id == 0 and fs.get('want') == g and not fs.get('traded'):
        fs['traded'] = True
        game.msg('Thornfield buys the ' + D.GOODS[g]['name'].lower() + ' you brought from the city: your first trade '
                 'on your own.', 'gold')
        from . import chronicle as CH
        CH.add(game, 'Your deeds', f'You bought {D.GOODS[g]["name"].lower()} in {letter_city(game).name} and sold it in '
               'Thornfield: your first trade on your own.', 'seen', where=game.loc_name(), key='first_trade',
               title='A first trade', quiet=True)


def story(game):
    """The open first steps, for the journal: (title, text)."""
    s = st(game)
    out = []
    if s.get('letter') == 'carried':
        c = letter_city(game)
        out.append(('A letter for the city', f'Bring Elder Berend\'s letter to the trader on the market of '
                    f'{c.name}, to the {way(game, c)}. Sell the loads of {D.GOODS[s["loads"][0]]["name"].lower()} '
                    'there yourself.'))
    elif s.get('letter') == 'given' and s.get('want') and not s.get('traded'):
        out.append(('Something back for Thornfield', f'The trader\'s answer: Thornfield needs '
                    f'{D.GOODS[s["want"]]["name"].lower()}. Buy it in {letter_city(game).name}, sell it in Thornfield.'))
    if s.get('word') in ('offered', 'carried', 'answer') and s.get('seat') is not None:
        seat = game.world.sites[s['seat']]
        if s['word'] == 'carried':
            out.append(('The sealed word', f'Bring the sealed word to the lord of {seat.name}, to the '
                        f'{way(game, seat)}.'))
        elif s['word'] == 'answer':
            out.append(('The answer', f'Bring the answer of {seat.name} back to the messenger in '
                        f'{letter_city(game).name}.'))
    return out


def register():
    from . import events as EV
    EV.RESOLVERS['first_ways'] = r_ways
    EV.RESOLVERS['first_shelf'] = r_shelf


register()
