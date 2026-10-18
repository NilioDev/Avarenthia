"""The last two hundred years, and the places to read of them.

Making the world also works out a short history after the myth of lore.py: the founding of the empire, its
emperors and the dynasties that ended, the kings, the wars between the realms and with the raiders and the tribes,
the houses that married and the houses that fell (their seats are the ruins of today), the towns that were founded,
plagues and hard winters, the holy order, the dwarves' oldest grudges and the elves who shut their wood. Thirty to
sixty events, every one tied to a place on the map, kept in world.history.

Where you learn it: the old folk tell some of it as they tell the old days, sometimes wrong (a wrong year, a wrong
victor), and what you later read puts it right. A library is true but slow: the libraries of the cities, with
shelves and a scribe, the Grudge Book of a dwarf hold and its keeper, the hall of songs under the Elder Tree and its
loremaster. The scribe reads you a subject for a few hours and a few silver (a day for the old letters), free for the
Circle of Magi: The old days, The realms, A lord or house, This city, Varnish letters. Some of what you read leads
somewhere: the ruin where a fallen house had its seat, a field where a great battle was fought."""
import random

from . import calendar as CAL
from . import data as D
from .worldgen import cheb

HOUR = D.DAY_LEN // 24
PRICE = 300              # a subject at the library: three silver
LETTERS_PRICE = 800      # the Varnish letters: eight silver and a day
BOOK_PRICE = {False: 900, True: 400}     # what a library pays for an old book, unread / read

CAUSES = ['the Ford', 'Salt', 'the Two Crowns', 'the Bride', 'the Silver Road', 'the Broken Oath', 'the Seven Towers',
          'the Long Winter', 'the Toll Bridge', 'the Iron Hills', 'the Black Banner', 'the Stolen Seal']
FALLS = ['died out when its last heir drowned crossing the river', 'was put to the sword by a king it had defied',
         'was ruined by the plague and its lands sold', 'rose against the crown and lost',
         'was taken in one night by the dead out of the old tombs', 'burned with its hall in a winter fire',
         'was attainted for treason and its name struck out']
FOUNDERS = ['settlers from {o}', 'the younger sons of {o}', 'fishermen who stayed the winter', 'miners looking for silver',
            'a priest of Solmara and her flock', 'House {h}, as a market for its lands', 'shepherds out of the hills',
            'a free company that laid down its arms']
DISASTERS = [
    ('plague', 'The Grey Plague', 'the Grey Plague came up the roads to {t}; a third of the town died, and the dead were '
                                  'burned outside the walls.'),
    ('winter', 'The Hungry Winter', 'the Hungry Winter froze the rivers from Longnight to Seedwake; around {t} the '
                                    'wolves came into the villages.'),
    ('fire', 'The Great Fire', 'a fire went through {t} in one night and left only the stone houses standing.'),
    ('flood', 'The Flood', 'the river rose over {t} and took the lower town; the high-water marks are still on the walls.'),
    ('famine', 'The Lean Years', 'three harvests failed around {t}; the lords opened their granaries, or did not.'),
]


def ago(year):
    return CAL.YEAR - year


# ------------------------------------------------------------------ making it
def generate(game, m, world, R):
    from . import realms as RL
    H = []
    used = {h.name for h in R.houses}
    now = CAL.YEAR
    start = now - random.randint(190, 215)
    great = world.settlements[R.great]
    emp = R.lord(R.emperor)
    emp_house = R.houses[emp.house].name

    def ev(year, ch, kind, title, text, x, y, **kw):
        if text.startswith('The '):
            text = 'the ' + text[4:]
        H.append(dict(year=year, ch=ch, kind=kind, title=title, text=f'In {year} AR {text}', x=x, y=y, **kw))

    # the founding, and the dynasties of emperors since
    first_house = RL.family_name(used)
    g = random.choice(['male', 'male', 'female'])
    founder = RL.first_name('human', g)
    t = RL.TITLES['emperor'][g == 'female']
    ev(start, 'The Old Days', 'empire', f'The founding of {R.empire.replace("The ", "the ")}',
       f'{founder} of House {first_house} brought the {RL.NUMBERS.get(len(R.kingdoms) + 2, "many").lower()} crowns together at {great.name} and was '
       f'crowned the first {t}. So began {R.empire.replace("The ", "the ")}.', great.x, great.y, prio=3)
    houses = [first_house]
    if random.random() < .8:
        houses.append(RL.family_name(used))
    houses.append(emp_house)
    crowned = now - random.randint(1, max(2, min(30, emp.age - 18)))
    y = start
    for k, hn in enumerate(houses[1:], 1):
        y = start + (crowned - start) * k // len(houses) + random.randint(-8, 8)
        y = max(start + 12, min(crowned - 4, y))
        old = houses[k - 1]
        if random.random() < .5:
            ev(y, 'Lords and houses', 'dynasty', f'The end of House {old}',
               f'the last emperor of House {old} died without an heir, and the kings chose {RL.first_name("human", "male")} '
               f'of House {hn} to take the crown.', great.x, great.y, prio=2)
        else:
            war_site = random.choice([s for s in world.settlements if cheb(s.x, s.y, great.x, great.y) < 60] or [great])
            ev(y, 'The Realms', 'dynasty', f'The War of the Succession',
               f'House {hn} fought House {old} for the empty throne; it was won at {war_site.name}, and House {old} '
               f'was never seen at court again.', war_site.x, war_site.y, prio=2)
    ev(crowned, 'Lords and houses', 'crowned', f'{RL.style(R, emp, False)} crowned',
       f'{RL.style(R, emp, False)} was crowned at {great.name}, still the ruler of {R.empire.replace("The ", "the ")}.',
       great.x, great.y, about=emp.id, prio=3)
    # the kingdoms: how each came under the empire, and its king now
    for kg in R.kingdoms[1:]:
        x, y2 = RL.seat_pos(world, kg.seat)
        yr = start + random.randint(0, 80)
        how = random.choice(['swore to the emperor after a lost war', 'joined the empire by a marriage', 'bought its peace with gold and '
                             'a hostage', 'was the last to bend the knee'])
        ev(yr, 'The Realms', 'kingdom', f'{kg.name} joins the empire', f'{kg.name} {how}.', x, y2, kid=kg.id, prio=2)
        king = R.lord(kg.king)
        kc = now - random.randint(1, max(2, min(35, king.age - 16)))
        ev(kc, 'Lords and houses', 'crowned', f'{RL.style(R, king, False)} crowned',
           f'{RL.style(R, king, False)} took the crown of {kg.short}.', x, y2, about=king.id, kid=kg.id, prio=1)
    # wars between the realms, each with its field
    pairs = []
    for a in R.kingdoms:
        for b in R.kingdoms:
            if a.id < b.id:
                pairs.append((a, b))
    for _ in range(random.randint(3, 6)):
        if not pairs:
            break
        a, b = random.choice(pairs)
        ax, ay = RL.seat_pos(world, a.seat)
        bx, by = RL.seat_pos(world, b.seat)
        mx, my = (ax + bx) // 2, (ay + by) // 2
        field = min((s for s in world.settlements if s.kind in ('hamlet', 'village', 'town') and s.kind != 'deephold'),
                    key=lambda s: cheb(s.x, s.y, mx, my) + random.randint(0, 12), default=None)
        if not field:
            continue
        yr = random.randint(start + 10, now - 3)
        cause = random.choice(CAUSES)
        win, lose = (a, b) if random.random() < .5 else (b, a)
        lasted = random.randint(1, 9)
        end = random.choice(['and took a barony as the price of peace', 'and a princess went to the winner as a bride',
                             'and the loser paid tribute for twenty years', 'and nothing changed but the graves'])
        ev(yr, 'The Realms', 'war', f'The War of {cause}',
           f'{a.short} and {b.short} went to war over {cause.replace("the ", "the ")}. After {lasted} '
           f'year{"s" if lasted > 1 else ""} {win.short} won at the field of {field.name}, {end}.', field.x, field.y,
           field=True, win=win.short, lose=lose.short, prio=2)
    # the raiders and the tribes
    for rd in world.powers.get('raiders', []):
        vill = min(world.settlements, key=lambda s: cheb(s.x, s.y, rd['x'], rd['y']) + (99 if s.kind == 'deephold' else 0))
        yr = random.randint(start + 40, now - 5)
        ev(yr, 'The Realms', 'raiders', f'The first raid of the {rd["people"]}',
           f'the {rd["people"]} of {rd["land"]} first came, and burned {vill.name}. They have come again since.',
           vill.x, vill.y, prio=1)
    if world.powers.get('tribes'):
        tb = random.choice(world.powers['tribes'])
        yr = random.randint(start + 20, now - 30)
        near = min(world.settlements, key=lambda s: cheb(s.x, s.y, tb['x'], tb['y']) + (99 if s.kind == 'deephold' else 0))
        from .races import random_name
        ev(yr, 'The Realms', 'gorvash', 'The Gorvash',
           f'the orc tribes rose as one under the warlord {random_name("orc", "male", family=False)}, a Gorvash, and burned '
           f'their way west until they were broken at {near.name}.', near.x, near.y, field=True, prio=2)
    # houses that married
    big = [h for h in R.houses if h.rank in ('royal', 'baronial', 'imperial') and not h.fallen]
    for _ in range(random.randint(2, 5)):
        if len(big) < 2:
            break
        h1, h2 = random.sample(big, 2)
        if h2.id in h1.allies:
            continue
        h1.allies.append(h2.id)
        h2.allies.append(h1.id)
        pos = RL.seat_pos(world, h1.seat) or (great.x, great.y)
        yr = random.randint(now - 60, now - 2)
        ev(yr, 'Lords and houses', 'marriage', f'House {h1.name} weds House {h2.name}',
           f'a daughter of House {h1.name} married the heir of House {h2.name}; the two houses have stood together '
           f'since.', pos[0], pos[1], prio=1)
    # houses that fell: their seats are ruins now
    ruins = [d for d in world.dungeons.values() if getattr(d, 'mine', None) is None and d.style != 'cave'
             and not d.main]
    random.shuffle(ruins)
    for d in ruins[:random.randint(3, 6)]:
        hn = RL.family_name(used)
        yr = random.randint(start, now - 20)
        ev(yr, 'Lords and houses', 'fallen', f'The fall of House {hn}',
           f'House {hn} {random.choice(FALLS)}. Its seat is a ruin now: {d.name}.', d.x, d.y, lead=('dungeon', d.id), prio=2)
    # towns founded, and the old cities
    setts = [s for s in world.settlements if s.kind != 'deephold' and not getattr(s, 'elder', False) and s.race in
             ('human', 'halfling')]
    random.shuffle(setts)
    for s in setts[:random.randint(6, 10)]:
        if s.is_city:
            ev(start - random.randint(40, 300), 'The Old Days', 'city', f'The walls of {s.name}',
               f'the walls of {s.name} were raised; the city was already old when the empire was founded.', s.x, s.y,
               sid=s.id, prio=1)
            continue
        o = min((q for q in world.settlements if q.id != s.id and q.is_city), key=lambda q: cheb(q.x, q.y, s.x, s.y),
                default=great)
        who = random.choice(FOUNDERS).format(o=o.name, h=random.choice(R.houses).name)
        ev(random.randint(start, now - 15), 'The Old Days', 'founded', f'The founding of {s.name}',
           f'{s.name} was founded by {who}.', s.x, s.y, sid=s.id, prio=1)
    # hard times
    towns = [s for s in world.settlements if s.kind in ('town', 'city', 'metropolis', 'village')]
    for kind, title, text in random.sample(DISASTERS, random.randint(2, 4)):
        if not towns:
            break
        s = random.choice(towns)
        if kind == 'flood' and not getattr(s, 'river', False) and random.random() < .5:
            continue
        ev(random.randint(start, now - 4), 'The Old Days', kind, f'{title} of {s.name}', text.format(t=s.name), s.x, s.y,
           sid=s.id, prio=1)
    # the order, the Watch, the dwarves and the elves
    ch = world.powers.get('church') or {}
    od = ch.get('order')
    if od:
        st = world.sites[od['site']]
        ev(random.randint(start + 20, now - 40), 'The Old Days', 'order', f'The founding of {od["name"].replace("The ", "the ")}',
           f'{od["name"].replace("The ", "the ")} was founded to hunt the necromancers of the old tombs, and its keep was '
           f'built on the road.', st.x, st.y, prio=1)
    wt = world.powers.get('watch')
    if wt and wt.get('site') is not None:
        st = world.sites[wt['site']]
        ev(random.randint(now - 120, now - 10), 'The Realms', 'watch', f'{wt["name"]} raised',
           f'the emperor raised {wt["name"].replace("The ", "the ")} and built its fort, after the raiders came over the '
           f'border three summers in a row.', st.x, st.y, prio=1)
    for s in world.settlements:
        if s.kind == 'deephold':
            book = world.powers['grudges'].get(s.id, [])
            if book:
                gd = min(book, key=lambda q: q['day'])
                ev(year_of(gd['day']), 'Peoples', 'grudge', f'The oldest grudge of {s.name}',
                   f'the dwarves of {s.name} wrote in their Grudge Book: {gd["what"]}. It is not settled.', s.x, s.y,
                   sid=s.id, prio=1)
        elif getattr(s, 'elder', False):
            forest = world.powers.get('forest', {})
            ev(random.randint(start, now - 50), 'Peoples', 'elves', 'The elves shut their wood',
               f'the elves of {s.name} shut the old paths of their wood after the woodcutters of the empire burned a '
               f'grove to clear a road; they have let few in since.', s.x, s.y, sid=s.id, prio=1)
            forest.setdefault('history', True)
    # thirty to sixty, the most telling kept
    H.sort(key=lambda e: -e['prio'])
    del H[60:]
    H.sort(key=lambda e: e['year'])
    for i, e in enumerate(H):
        e['id'] = i
    world.history = H
    return H


def year_of(day):
    return CAL.YEAR + (CAL.START + day - 1) // (CAL.DAYS_IN_MONTH * 12)


def events(world):
    return getattr(world, 'history', [])


# ------------------------------------------------------------------ learning it
def known(game, e):
    from . import chronicle as CH
    return any(f['key'] == f'hist:{e["id"]}' for f in CH.facts(game))


def learn(game, e, src, who=None, where=None, quiet=True):
    """A true event of the history, heard or read; a wrong telling of it heard before is put right."""
    from . import chronicle as CH
    f = CH.add(game, e['ch'], e['text'], src, who, where, place=(e['x'], e['y']), title=e['title'], key=f'hist:{e["id"]}',
               quiet=quiet)
    if e.get('about') is not None:
        f['about'] = e['about']
    wrong = next((o for o in CH.facts(game) if o['key'] == f'hist:{e["id"]}f'), None)
    if wrong and not wrong['false']:
        CH.disprove(game, wrong['key'], f'Not so: {e["text"]}')
    if src == 'read' and e.get('lead'):
        lead(game, e)
    return f


def garble(e):
    """How the old folk get it wrong: the year, or who won."""
    text = e['text']
    if e.get('win') and random.random() < .6:
        return text.replace(f"{e['win']} won at", f"{e['lose']} won at", 1)
    wrong = e['year'] + random.choice([-1, 1]) * random.randint(15, 60)
    if wrong >= CAL.YEAR:
        wrong = e['year'] - random.randint(15, 60)
    return text.replace(f'In {e["year"]} AR', f'In {wrong} AR', 1)


def hint(game, npc=None):
    """lore.hint: an event of the last two hundred years told by someone who lives near where it happened. One time
    in four they have it wrong; what you read later puts it right."""
    from . import chronicle as CH
    x, y = game.over_pos
    near = [e for e in events(game.world) if cheb(e['x'], e['y'], x, y) <= 70 and not known(game, e)
            and not any(f['key'] == f'hist:{e["id"]}f' for f in CH.facts(game))]
    if not near:
        return None
    e = random.choice(near)
    who = CH.speaker(npc)
    if random.random() < .25:
        text = garble(e)
        if text and text != e['text']:
            CH.add(game, e['ch'], text, 'heard', who, place=(e['x'], e['y']), key=f'hist:{e["id"]}f', quiet=True)
            return _told(text)
    learn(game, e, 'heard', who)
    return _told(e['text'])


def _told(text):
    return random.choice(['My grandfather used to say: ', 'They tell it like this: ', 'Everybody here knows it. ', '']) + text


def lead(game, e):
    """A book names the place: it goes on your map."""
    from . import chronicle as CH
    k, ref = e['lead']
    if k == 'dungeon':
        d = game.world.dungeons.get(ref)
        if d:
            om = game.maps['over']
            if not om.seen[d.y * om.w + d.x]:
                game.reveal_place(d.x, d.y)
                game.msg(f'The record names {d.name}, and where it lies. You mark it on your map.', 'info')
            CH.add(game, 'Places', f'{d.name}: once the seat of a house, now a ruin.', 'read', 'the records', place=(d.x, d.y),
                   key=f'lead:hist:{e["id"]}', quiet=True)


def field_at(game, x, y):
    """A field where a great battle was fought, long ago."""
    for e in events(game.world):
        if e.get('field') and (e['x'], e['y']) != (x, y) and cheb(e['x'], e['y'], x, y) == 1:
            return e
    return None


def on_step(game):
    """Walking past an old battlefield beside the village it is named for: bones in the grass."""
    p = game.player
    e = field_at(game, p.x, p.y)
    if not e:
        return
    from . import chronicle as CH
    key = f'field:{e["id"]}'
    if any(f['key'] == key for f in CH.facts(game)):
        return
    CH.add(game, 'Places', f'You walked the old field: rusted iron and bones in the grass, where {e["title"]} was '
           f'decided {ago(e["year"])} years ago.', 'seen', where='with your own eyes', place=(e['x'], e['y']),
           key=key, quiet=True)
    game.msg(f'Rusted iron and old bones lie in the grass here. {e["title"]} was decided on this field.', 'info')
    if not known(game, e):
        learn(game, e, 'heard', 'a shepherd by the old field')


# ------------------------------------------------------------------ libraries
def library(game, m, s, b):
    """A city's library: shelves along the walls and a scribe at the table."""
    from .entities import make_npc
    from .races import random_name
    from .towns import free_inside
    pl = b['plot']
    door = pl.door
    inside = set(pl.inside)
    for c in pl.inside:
        x, y = c
        edge = any((x + dx, y + dy) not in inside for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        if edge and (door is None or cheb(x, y, door[0], door[1]) > 1) and not m.mon_at(x, y) and (x + y) % 3:
            m.set(x, y, D.SHELVES)
    for o in list(m.mons):
        if (o.x, o.y) in inside and getattr(o, 'role', '') not in ('guard',):
            m.mons.remove(o)
    sp = free_inside(m, pl)
    if not sp:
        return
    g = random.choice(['male', 'female'])
    npc = make_npc(game, f'{random_name("human", g, family=False)} the Scribe', 'scribe', '#c4aaff', sp[0][0], sp[0][1],
                   True, gender=g, race='human')
    m.mons.append(npc)
    b['name'], b['what'] = f'The Library of {s.name}', 'library'


def keeper(game, m, s, cell):
    """The keeper of a dwarf hold's Grudge Book, by the High Seat."""
    from .entities import make_npc
    from .races import random_name
    g = random.choice(['male', 'female'])
    npc = make_npc(game, f'{random_name("dwarf", g, family=False)}, Keeper of the Book', 'keeper', '#c4aaff', cell[0], cell[1],
                   True, gender=g, race='dwarf')
    m.mons.append(npc)
    return npc


def loremaster(game, m, s, cell):
    """The loremaster of the hall of songs under the Elder Tree."""
    from .entities import make_npc
    from .races import random_name
    g = random.choice(['male', 'female'])
    npc = make_npc(game, f'{random_name("elf", g, family=False)}, Loremaster', 'loremaster', '#c4aaff', cell[0], cell[1],
                   True, gender=g, race='elf')
    m.mons.append(npc)
    return npc


def furnish_folk(game, m, s):
    """The keeper of the Grudge Book beside a dwarf king's High Seat; the
    loremaster of the hall of songs under the Elder Tree."""
    if s.kind == 'deephold':
        lord = next((o for o in m.mons if getattr(o, 'role', '') == 'thane'), None)
        role = 'keeper'
    elif getattr(s, 'elder', False):
        lord = None
        role = 'loremaster'
    else:
        return
    cx, cy = (lord.x, lord.y) if lord else getattr(m, 'centre', (m.w // 2, m.h // 2))
    cells = sorted(((x, y) for y in range(max(1, cy - 8), min(m.h - 1, cy + 9)) for x in range(max(1, cx - 10), min(m.w - 1, cx + 11))
                    if D.TILES[m.tile(x, y)].walk and not m.mon_at(x, y) and cheb(x, y, cx, cy) >= 3),
                   key=lambda c: cheb(c[0], c[1], cx, cy))
    if not cells:
        return
    c = cells[0]
    (keeper if role == 'keeper' else loremaster)(game, m, s, c)


ROLES = {'scribe', 'keeper', 'loremaster'}


def free(game):
    from . import guilds as GU
    return 'magi' in GU.members(game)


def price(game, c):
    return 0 if free(game) else c


def talk(game, npc):
    role = getattr(npc, 'role', '')
    if role not in ROLES:
        return False
    from . import events as EV
    from .money import fmt
    p = game.player
    from . import realmjobs as RJ
    if role in ('keeper', 'loremaster'):
        g = RJ.giver_of(game, npc)
        if g and RJ.turn_in_giver(game, g, npc):
            return True

    def opt(label, key, c):
        lab = f'{label} ({fmt(c)})' if c and not free(game) else f'{label} (free to the Magi)' if c else label
        c = price(game, c)
        return (lab, key if p.gold >= c else None)
    if role == 'scribe':
        opts = [opt('The old days', 'old', PRICE), opt('The realms', 'realms', PRICE), opt('A lord or house', 'lords', PRICE),
                opt('This city', 'city', PRICE)]
        if not game.__dict__.get('varnish_letters'):
            opts.append(opt('Varnish letters', 'letters', LETTERS_PRICE))
        books = [it for it in p.inv if it.k == 'oldbook']
        if books:
            it = books[0]
            opts.append((f'Sell {it.name} ({fmt(BOOK_PRICE[bool(getattr(it, "read", False))])})', 'sell'))
        text = ('The scribe looks up from a ledger. "The library is open to anyone who can pay for the candles. What would '
                'you read?"')
    elif role == 'keeper':
        opts = [opt('Read the Grudge Book', 'grudges', 0), opt('The old days', 'old', PRICE), ('Is there work for me?', 'work')]
        text = ('The keeper rests a hand on a book bound in iron, as thick as a doorstep. "Every wrong done to this hold is '
                'in here, and every one that was put right. Few are put right."')
    else:
        opts = [opt('The songs of the old days', 'old', PRICE), opt('The realms of men', 'realms', PRICE),
                ('Is there work for me?', 'work')]
        text = ('"We remember," the loremaster says, "because we were there, or our mothers were. Sit, and listen. It '
                'takes as long as it takes."')
    opts.append(('Goodbye', 'bye'))
    EV.ask(game, 'library', npc.name, text, opts, npc=npc.id)
    return True


def r_library(game, choice, ctx):
    npc = next((o for o in game.map.mons if o.id == ctx.get('npc')), None)
    if not npc or choice in (None, 'bye'):
        return
    p = game.player
    if choice == 'work':
        from . import realmjobs as RJ
        RJ.offer_giver(game, npc)
        return
    if choice == 'sell':
        it = next((i for i in p.inv if i.k == 'oldbook'), None)
        if it:
            got = BOOK_PRICE[bool(getattr(it, 'read', False))]
            p.inv.remove(it)
            p.gold += got
            from .money import fmt
            game.say(npc, f'"{it.name}. We have not had a copy of that in a long time." The scribe counts out {fmt(got)}.')
        return
    cost = price(game, LETTERS_PRICE if choice == 'letters' else 0 if choice == 'grudges' else PRICE)
    if p.gold < cost:
        game.msg('You cannot pay for that.', 'bad')
        return
    p.gold -= cost
    where = game.loc_name()
    who = npc.name
    if choice == 'letters':
        game.varnish_letters = True
        game.end_turn(D.DAY_LEN, True)
        game.say(npc, '"A day, and you have the letters. Slowly, mind you: the Varnish wrote as they built, to last, not to '
                      'be read." You can read the old stones now.')
        from . import chronicle as CH
        CH.add(game, 'The Old Days', 'You learnt the Varnish letters: the old stones in the ruins can be read now.', 'seen',
               where=where, key='varnish_letters', title='The Varnish letters')
        return
    game.end_turn(HOUR * 3, True)
    got = {'old': read_old, 'realms': read_realms, 'lords': read_lords, 'city': read_city, 'grudges': read_grudges}[choice](
        game, npc, who, where)
    if got:
        from . import guide as GDE
        GDE.tip(game, 'library')
        game.msg(f'Your chronicle grows: {got} new page{"s" if got != 1 else ""} read in {where}.', 'gold')
    else:
        game.say(npc, '"You have read all we keep of that. Come back when there is more to write."')


def src_of(npc):
    return 'heard' if getattr(npc, 'role', '') == 'loremaster' else 'read'


def read_old(game, npc, who, where):
    """Five events of the old days and the houses, the oldest first; for the dwarves their own, for the elves theirs."""
    role = getattr(npc, 'role', '')
    evs = [e for e in events(game.world) if not known(game, e)]
    if role == 'keeper':
        evs = [e for e in evs if e['ch'] in ('Peoples', 'The Old Days') or e['kind'] in ('war', 'gorvash')]
    elif role == 'loremaster':
        evs.sort(key=lambda e: (e['kind'] not in ('elves', 'city', 'empire'), e['year']))
    n = 0
    for e in evs[:5]:
        learn(game, e, src_of(npc), who, where)
        n += 1
    if n and role != 'loremaster':
        lead_old(game, who, where)
    return n


def lead_old(game, who, where):
    """Sometimes the records also name a battlefield of the old wars you have not seen."""
    from . import chronicle as CH
    fields = [e for e in events(game.world) if e.get('field') and known(game, e)
              and not any(f['key'] == f'field:{e["id"]}' for f in CH.facts(game))]
    if fields and random.random() < .5:
        e = random.choice(fields)
        game.reveal_place(e['x'], e['y'])


def read_realms(game, npc, who, where):
    """The realm the library stands in, true and fresh; the other realms, true but old, and their kings."""
    from . import realms as RL
    from . import chronicle as CH
    from . import news as NW
    R = RL.get(game)
    if R is None:
        return 0
    x, y = game.over_pos
    rk = RL.cell_realm(game.world, y * game.maps['over'].w + x)
    here = R.kingdoms[rk[1]] if rk and rk[0] == 'k' else None
    n = 0
    src = src_of(npc)
    for kg in R.kingdoms:
        king = R.lord(kg.king)
        if not king:
            continue
        lines = [f'{kg.name} is ruled by {RL.style(R, king, False)} from {RL.seat_name(game.world, kg.seat)}.']
        if kg is here or kg.id == 0:
            for war in R.wars:
                if kg.id in (war['a'], war['b']):
                    o = R.kingdoms[war['b'] if war['a'] == kg.id else war['a']]
                    lines.append(f'It is at war with {o.short}, over {war["cause"]}.')
            if kg.civil:
                lines.append(f'{RL.style(R, R.lord(kg.civil["claimant"]), False)} claims its crown.')
            if kg.rebel:
                lines.append(f'{RL.style(R, R.lord(kg.rebel["baron"]), False)} is in revolt.')
        key = f'lib:{kg.id}:{game.day // 30 if kg is here else game.day // 90}'
        if not any(f['key'] == key for f in CH.facts(game)):
            CH.add(game, 'The Realms', ' '.join(lines), src, who, where, place=RL.seat_pos(game.world, kg.seat), key=key,
                   quiet=True)
            n += 1
    for e in events(game.world):
        if e['ch'] == 'The Realms' and not known(game, e) and n < 6:
            learn(game, e, src, who, where)
            n += 1
    # what the library has had word of puts the false talk right: everything in its own realm, far news when old
    posts = {q['fact']['key']: q for q in NW.store(game) if q.get('fact')}
    for f in list(CH.facts(game)):
        if f['src'] != 'heard' or f['false'] or not f['key'].endswith('f') or not f['key'].startswith('rl'):
            continue
        true = posts.get(f['key'][:-1])
        if not true:
            continue
        near = here and RL.cell_realm(game.world, true['y'] * game.maps['over'].w + true['x']) == ('k', here.id)
        if near or game.day - true.get('day', game.day) > 60:
            CH.add(game, true['fact']['ch'], true['text'], src, who, where, place=(true['x'], true['y']),
                   key=true['fact']['key'], quiet=True)
            CH.disprove(game, f['key'], f'Not so, the library says: {true["text"]}')
            n += 1
    return n


def read_lords(game, npc, who, where):
    """The lords of this realm: who they are, their arms, their heirs."""
    from . import realms as RL
    from . import chronicle as CH
    R = RL.get(game)
    if R is None:
        return 0
    x, y = game.over_pos
    rk = RL.cell_realm(game.world, y * game.maps['over'].w + x)
    kid = rk[1] if rk and rk[0] == 'k' else 0
    kg = R.kingdoms[kid]
    lords = [R.lord(kg.king), R.lord(R.emperor)] + RL.lords_of(R, kg)
    n = 0
    for lo in lords:
        if not lo or not lo.alive or n >= 5:
            continue
        key = f'lord:{lo.id}'
        if any(f['key'] == key for f in CH.facts(game)):
            continue
        h = R.houses[lo.house]
        f = CH.add(game, 'Lords and houses', RL.describe_lord(R, lo) + f' The arms of House {h.name}: '
                   f'{RL.arms_words(h.arms)}. "{h.motto}."', src_of(npc), who, where, place=RL.place_of(game, lo), key=key,
                   title=RL.style(R, lo, False), quiet=True)
        f['about'] = lo.id
        n += 1
    for e in events(game.world):
        if e['ch'] == 'Lords and houses' and not known(game, e) and n < 6:
            learn(game, e, src_of(npc), who, where)
            n += 1
    return n


def read_city(game, npc, who, where):
    """This city and the land around it."""
    here = game.here
    n = 0
    x, y = game.over_pos
    for e in sorted(events(game.world), key=lambda e: cheb(e['x'], e['y'], x, y)):
        if (e.get('sid') == getattr(here, 'id', None) or cheb(e['x'], e['y'], x, y) <= 25) and not known(game, e):
            learn(game, e, 'read', who, where)
            n += 1
            if n >= 4:
                break
    return n


def read_grudges(game, npc, who, where):
    """The Grudge Book of this hold: every wrong, and which are settled."""
    from . import chronicle as CH
    sid = getattr(game.map, 'sid', None)
    book = game.world.__dict__.get('powers', {}).get('grudges', {}).get(sid, [])
    n = 0
    for gd in book:
        key = f'grudge:{sid}:{gd["id"]}:{bool(gd["settled"])}'
        if any(f['key'] == key for f in CH.facts(game)):
            continue
        text = f'The Grudge Book of {game.world.settlements[sid].name}, {year_of(gd["day"])} AR: {gd["what"]}. ' + \
            (f'Settled: {gd["settled"]}.' if gd['settled'] else 'Not settled.')
        CH.add(game, 'Peoples', text, 'read', who, where, key=key, quiet=True)
        n += 1
    game.__dict__.setdefault('grudges_read', set()).add(sid)
    return n


def raider_lore(game, rd):
    """What a raider chief says of his own people, and it goes in the chronicle as heard."""
    from . import chronicle as CH
    from . import powers as PW
    t = PW.KINDS[rd['kind']]
    first = next((e for e in events(game.world) if e['kind'] == 'raiders' and rd['people'] in e['text']), None)
    since = f' We first came down on your kind in {first["year"]}, and you remember it.' if first else ''
    held = f' We hold land of yours now, and we will keep it.' if rd['held'] else ''
    text = (f'We are the {rd["people"]} of {rd["land"]}. Our {t["hall"]} stands where it stood when your kings were '
            f'still herding pigs.{since}{held} We come in our own months, and we take what the weak cannot hold.')
    CH.add(game, 'Peoples', f'{rd["name"]}, as their {t["title"].lower()} tells it: {text}', 'heard', rd['chief'],
           place=(rd['x'], rd['y']), key=f'raider:{rd["site"]}', quiet=True)
    return f'"{text}"'


def register():
    from . import events as EV
    EV.RESOLVERS['library'] = r_library


register()
