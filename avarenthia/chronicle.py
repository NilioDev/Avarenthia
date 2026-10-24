"""Aldra's Chronicle: what your hero knows of this world, and how.

The handbook (?) says how the game works and is the same for every hero; the chronicle says what this hero has
heard, read and seen. Every fact keeps its source: heard (·, may be wrong or old), read (≡, a book or a stone) or
seen (☼, you were there), with who told it, where and on which day. Something heard can later prove false: a red
"Not so" line goes under it. The journal's Lore tab is its contents; Enter opens the book.

Where it comes from: what people tell (the old days, the gods, the peoples, places and wonders), what you see (great
sights, battlefields, the places you go down into, the named enemies you kill: Your deeds), inscribed stones in the
ruins (the Varnish ones only once you have learnt the old letters) and a few old books lost in the dungeons."""
import random

from . import calendar as CAL
from . import data as D

CHAPTERS = ['The Old Days', 'The Realms', 'Lords and houses', 'Peoples', 'Gods', 'Places', 'Wonders', 'Your deeds', 'Creatures', 'The kitchen', 'Signs']
MARK = {'heard': ('·', (217, 165, 71)), 'read': ('≡', (196, 170, 255)), 'seen': ('☼', (255, 226, 120))}


RANK = {'heard': 0, 'read': 1, 'seen': 2}      # a seen fact beats a read one, a read one beats what you heard


def facts(game):
    return game.__dict__.setdefault('chronicle', [])


def add(game, chapter, text, src, who=None, where=None, place=None, title=None, key=None, quiet=False):
    """A new fact for the chronicle; the same fact twice is kept once (seen beats read, read beats heard)."""
    fs = facts(game)
    key = key or text
    old = next((f for f in fs if f['key'] == key), None)
    if old:
        if RANK[src] > RANK[old['src']]:
            old.update(src=src, who=who, where=where or old['where'], day=game.day, new=True, text=text)
        return old
    if where is None:
        here = game.here
        where = here.name if here else game.map.name if game.cur != 'over' else 'on the road'
    f = dict(key=key, ch=chapter, text=text, src=src, who=who, where=where, day=game.day, place=place,
             title=title, false=None, new=True)
    fs.append(f)
    if title and not quiet:
        game.msg(f'Your chronicle grows: {title}.', 'gold')
    return f


def disprove(game, key, why):
    """What you heard is not so."""
    f = next((f for f in facts(game) if f['key'] == key), None)
    if f and not f['false']:
        f['false'] = why
        f['new'] = True
        game.msg(f'Your chronicle: what you heard was not so. {why}', 'info')


def count(game, ch):
    if ch == 'Creatures':
        return len(game.bestiary)
    if ch == 'The kitchen':
        from . import cooking as CK
        return len(CK.known(game))
    if ch == 'Signs':
        return None
    return sum(1 for f in facts(game) if f['ch'] == ch)


def unread(game, ch):
    return any(f['new'] for f in facts(game) if f['ch'] == ch)


# ------------------------------------------------------------------ heard: what people tell
def speaker(npc):
    return getattr(npc, 'name', None) if npc is not None else None


def heard_lore(game, line, npc=None):
    """A line of the old days, a god or a people, told by someone: kept, with who told it."""
    from . import lore as LORE
    if line in LORE.HISTORY:
        ch = 'The Old Days'
    elif any(line in v for v in LORE.GOD_LORE.values()):
        ch = 'Gods'
    elif any(line in v for v in LORE.RACE_LORE.values()):
        ch = 'Peoples'
    else:
        return
    add(game, ch, line, 'heard', speaker(npc))


def heard_place(game, line, place=None, npc=None, chapter='Places'):
    add(game, chapter, line, 'heard', speaker(npc), place=place)


# ------------------------------------------------------------------ seen: what you were there for
def seen_wonder(game, name, x, y):
    from . import lore as LORE
    text = LORE.WONDERS.get(name, ('You saw ' + name + '.',))[0]
    add(game, 'Wonders', f'{name}. {text}', 'seen', where='with your own eyes', place=(x, y), title=name, key='w:' + name)


def seen_place(game, key, title, text, place):
    add(game, 'Places', text, 'seen', where='with your own eyes', place=place, title=title, key=key, quiet=True)


def deed(game, title, text, place=None):
    add(game, 'Your deeds', text, 'seen', where=game.loc_name(), place=place, title=title, key='d:' + title + str(game.day))


def deeds(game):
    return [f for f in facts(game) if f['ch'] == 'Your deeds']


# ------------------------------------------------------------------ read: stones and books
STONES_COMMON = [
    ('The Hundred Winters', 'Cut in a hurry, in plain letters: "We held the pass for a hundred days. Remember us. '
                            'Year 9 after the Ruin."'),
    ('The first temple', '"Here the survivors gave thanks to the Dawnmother, who lit the first morning after the '
                         'Ruin."'),
    ('A boundary stone', '"Thus far the land of the Free Towns. Beyond it the wolves, and the dead."'),
    ('A grave of the Hundred Winters', '"Seven brothers, seven spears. The winter took the eighth."'),
    ('The founding stone', '"In the 40th year after the Ruin, the first market was held here, and the old road '
                           'was cleared."'),
    ('A plague stone', '"Leave bread here and go. The sickness is in this place. Year 212."'),
]
STONES_VARNISH = [
    ('The Sky-Seat', 'The old letters say: "From the Sky-Seat the Emperor sees all the land, and the winds go where '
                     'he bids."'),
    ('The binding of the dead', 'The old letters say: "The dead are bound to the stone and serve. Let no hand break '
                                'the seal."'),
    ('The roads of the Empire', 'The old letters say: "A day\'s march from here, the road of the Empire runs on to '
                                'the sea."'),
    ('The Hollow King', 'The old letters say: "To the Hollow King the mages gave their dead, and he gave them the '
                        'winds."'),
    ('The last order', 'The old letters say: "Seal the vaults. The sky is falling. Let whoever comes after not open '
                       'them."'),
    ('A tally of the legions', 'The old letters say: "Nine legions on the northern wall. The barbarians do not '
                               'come."'),
]
STELE = 75          # the tile, see data.TILES


def place_stone(game, m, dg, depth):
    """A worked dungeon may keep an inscribed stone on its first level."""
    if dg.style == 'cave' or depth != 1 or getattr(dg, 'mine', None) is not None or random.random() > .35:
        return
    from . import worldgen as W
    c = W.rand_free(game, m, lambda t: t == D.FLOOR)
    if c:
        m.set(c[0], c[1], STELE)


def read_stone(game, x, y):
    m = game.map
    r = random.Random(f'{m.key}:{x}:{y}')
    varnish = r.random() < .5
    title, text = r.choice(STONES_VARNISH if varnish else STONES_COMMON)
    if varnish and not game.__dict__.get('varnish_letters'):
        game.msg('The stone is cut with old letters you cannot read: Varnish. A scribe in a city library could teach '
                 'you them.', 'info')
        add(game, 'The Old Days', f'A stone in {m.name} is cut with Varnish letters you cannot read.', 'seen',
            where=m.name, key=f'stone:{m.key}:{x}:{y}', quiet=True)
        return 0
    game.msg(f'You read the stone. {text}', 'info')
    f = add(game, 'The Old Days', text, 'read', who='an inscribed stone', where=m.name, title=title,
            key=f'stone:{m.key}:{x}:{y}')
    f['src'] = 'read'
    if varnish and not f.get('lead'):
        f['lead'] = True
        from . import hidden as HP
        wy = HP.random_unknown(game, game.over_pos)
        if wy:
            HP.discover_way(game, wy.id, 'The stone names an old road, and you know where it leaves the land you '
                            'know.', [HP.start_of(game, wy)])
    return 1


BOOKS = [
    ('A Chronicle of the Hundred Winters', 'The Old Days',
     'After the Ruin the towns fought each other for a hundred winters, over bread and over the old roads, until the '
     'first kings made peace with the sword.'),
    ('The Book of the Sky-Seat', 'The Old Days',
     'The Sky-Seat was built over three lifetimes, of glass and bronze, on the cliffs above the sea. Its fall was '
     'heard in every land at once.'),
    ('On the Peoples of the Deep', 'Peoples',
     'The dwarves kept the old roads open under the mountains while the world above burned, and they still count '
     'what is owed to them.'),
    ('A Herbal of the Green Mother', 'Gods',
     'Thessa\'s shrines stand in the open because she will not be shut in, and her priests read the year in the '
     'herbs.'),
    ('The Wanderer\'s Roads', 'Places',
     'A traveller\'s book of the old roads, with the places where the Empire buried its dead.'),
    ('The Tale of the Elder Tree', 'Peoples',
     'The elves say the Elder Tree was old when the Empire was young, and that it remembers every promise.'),
]


def make_book(game):
    from .entities import Item
    taken = game.__dict__.setdefault('books_found', [])
    left = [b for b in BOOKS if b[0] not in taken]
    if not left:
        return None
    b = random.choice(left)
    taken.append(b[0])
    it = Item(game.new_id(), 'oldbook', 'oldbook')
    it.name = b[0]
    return it


def maybe_book(game, m, dg, depth):
    """A few old books per world lie in the deepest levels of the dungeons."""
    if depth != dg.depth or random.random() > .2 or len(game.__dict__.get('books_found', [])) >= len(BOOKS):
        return
    from . import worldgen as W
    it = make_book(game)
    c = W.rand_free(game, m, lambda t: t == D.FLOOR)
    if it and c:
        it.x, it.y = c
        m.items.append(it)


def read_book(game, it):
    b = next((b for b in BOOKS if b[0] == it.name), None)
    if not b:
        return 0
    if getattr(it, 'read', False):
        game.msg(f'You have read {it.name}. A library would pay something for it.')
        return 0
    it.read = True
    title, ch, text = b
    add(game, ch, text, 'read', who=title, where='in a book you found', title=title, key='book:' + title)
    lead = lead_place(game)
    if lead:
        name, x, y = lead
        om = game.maps['over']
        om.seen[y * om.w + x] = 1
        add(game, 'Places', f'{title} names {name}, and where it lies.', 'read', who=title, where='in a book',
                place=(x, y), key='lead:' + title, quiet=True)
        game.msg(f'The book names {name}. You mark it on your map.', 'info')
    return 10


def lead_place(game):
    """A tomb, a ruin or an old place the book names that you do not know yet."""
    om = game.maps['over']
    w = game.world
    cands = [(d.name, d.x, d.y) for d in w.dungeons.values() if not om.seen[d.y * om.w + d.x] and getattr(d, 'mine', None) is None
             and getattr(d, 'site', None) is None]
    return random.choice(cands) if cands else None


# ------------------------------------------------------------------ the pages
def source_line(f):
    day = CAL.short(f['day'])
    who = f['who']
    if f['src'] == 'heard':
        return f"heard from {who}, {f['where']}, {day}" if who else f"heard {f['where'] if f['where'] != 'on the road' else 'on the road'}, {day}"
    if f['src'] == 'read':
        return f"read: {who}, {f['where']}, {day}" if who else f"read {f['where']}, {day}"
    return f"seen {f['where']}, {day}" if f['where'] != 'with your own eyes' else f'seen with your own eyes, {day}'


def gaps(game, ch):
    """What you do not know yet, named without the answer."""
    fs = [f for f in facts(game) if f['ch'] == ch]
    out = []
    if ch == 'The Old Days':
        if not game.__dict__.get('varnish_letters'):
            out.append('What the Varnish cut on their stones you cannot read. The scribes of a city library teach the '
                       'old letters.')
        if len(fs) < 4:
            out.append('The old folk in every town remember the Ruin and the Hundred Winters. Ask them.')
    elif ch == 'The Realms':
        if len(fs) < 3:
            out.append('News of the courts and the wars comes late on the roads, and not always right. The library of a '
                       'city knows its own realm.')
    elif ch == 'Lords and houses':
        if len(fs) < 3:
            out.append('Who rules where, and who comes after them, the scribes keep. Or go and see the lords yourself.')
    elif ch == 'Wonders':
        left = sum(1 for n, _x, _y in getattr(game.world, 'wonders', ()) if not any(f['key'] == 'w:' + n for f in fs))
        if left:
            out.append(f'Of {left} great sight{"s" if left != 1 else ""} of this land you have no word from your own '
                       'eyes. Travellers talk of them.')
    elif ch == 'Gods':
        if len(fs) < 3:
            out.append('The priests know most of the gods. Talk to them in the temples.')
    elif ch == 'Peoples':
        if len(fs) < 3:
            out.append('Each people tells its own tale. Listen to a dwarf, an elf, a halfling.')
    elif ch == 'Your deeds' and not fs:
        out.append('Nothing yet that a bard would sing of.')
    elif ch == 'Places' and not fs:
        out.append('Places you go down into, and places others tell you of, are kept here.')
    return out


def blocks(game, i):
    """A chapter of the chronicle as book blocks (see handbook.py)."""
    ch = CHAPTERS[i]
    if ch == 'Creatures':
        rows = []
        for k, e in sorted(game.bestiary.items(), key=lambda kv: D.MONSTERS[kv[0]]['name']):
            from .engine import LORE_RANKS
            kills = e[1]
            mon = D.MONSTERS[k]
            rows.append(([(mon['ch'], D.hexrgb(mon['fg']))], f"{mon['name']}: {LORE_RANKS[game.lore(k)][1]}, "
                                                              f"{kills} slain"))
        out = [('p', 'Every kind you have met. [Enter] opens the bestiary, with all you learnt of them.')]
        return out + ([('s', rows)] if rows else [('p', 'You have met no creature yet.')])
    if ch == 'The kitchen':
        from . import cooking as CK
        rows = []
        for k in sorted(CK.known(game), key=lambda k: (('simple', 'hearty', 'luxury').index(CK.DISHES[k][1]), CK.DISHES[k][0])):
            name, tier, ings, *_r = CK.DISHES[k]
            words = ' '.join(CK.WORDS[e] for e in CK.effects(k) if e in CK.WORDS)
            rows.append((name, ' + '.join(CK.ing_name(i) for i in ings) + '. ' + words))
        return [('p', 'The dishes you know, and what goes in them. More you find in the pot, or hear of.'), ('r', rows)]
    if ch == 'Signs':
        from . import handbook as HB
        return HB.ch_signs(game)
    out = []
    fs = [f for f in facts(game) if f['ch'] == ch]
    for f in fs:
        out.append(('fact', f))
    for gp in gaps(game, ch):
        out.append(('gap', gp))
    if not out:
        out.append(('p', 'Nothing yet.'))
    return out


def seen_all(game, ch):
    for f in facts(game):
        if f['ch'] == ch:
            f['new'] = False


def places(game, i):
    """Where the facts of a chapter lie on the world map, in order."""
    return [f['place'] for f in facts(game) if f['ch'] == CHAPTERS[i] and f.get('place')]
