"""The peoples' books (round 58b): their pages in the world, reading them through the people, binding them by that
people, what a whole book shows, the peoples' own dawn tales, and the Peoples chapter of the chronicle.

The words are in folktexts.py. What lies where in this world is on `world.folkbooks`, made the first time it is
asked for (old worlds get theirs then, with dice of their own); what this hero has is on `p.folkbooks`."""
import random

from . import folktexts as T

# where a people lives: a settlement of that race, or one of these places on the land
HOME = {'dwarf': ('set:dwarf', 'site:grudgestone', 'site:dwarfroad', 'site:oldmine'),
        'elf': ('set:elf', 'site:glade'),
        'halfling': ('set:halfling', 'site:pipeweed', 'site:hedgegate', 'site:beehill'),
        'gnome': ('site:gnomes', 'site:mushwood', 'site:wrongmile'),
        'kobold': ('site:kobolds',), 'goblin': ('site:ravine', 'city'), 'gnoll': ('site:gnolls',),
        'lizard': ('site:stilts', 'site:eggmounds', 'site:causeway'),
        'orc': ('set:orc', 'site:orcfarm'), 'north': ('north',), 'fey': ('court',)}
# where that people binds a book you bring whole
BIND_AT = {'dwarf': ('set:dwarf',), 'elf': ('set:elf', 'site:glade'), 'halfling': ('set:halfling',),
           'gnome': ('site:gnomes',), 'goblin': ('city', 'site:ravine'), 'orc': ('set:orc',), 'north': ('north',)}
# how a page of a people comes to you in their town: handed over, with a word
GIVE = {'dwarf': 'An old dwarf at the hall door looks at you a long time, then hands you a ledger leaf. "Entered: lent. '
                 'Bring it back with its brothers."',
        'elf': 'An elf by the well hands you a ring of carved wood without looking at you. "You may hold it. Gently."',
        'halfling': 'A halfling grandmother presses a folded recipe into your hand, and a biscuit. "Read it. Eat that."',
        'orc': 'An orc woman at the gate gives you a leaf in the new letters. "Read it. Then you know us a little."',
        'north': 'An old woman of the hall gives you a roll of names. "You asked whose names they are. That is enough."',
        'goblin': 'A goblin in a doorway sells you a swap leaf for nothing at all. "First one is free. They all are, '
                  'really."'}


# ------------------------------------------------------------------ state
def st(game):
    p = game.player
    if not hasattr(p, 'folkbooks'):
        p.folkbooks = dict(pages=set(), read=set(), bound=set(), dawn=set(), favour=set(), given=set())
    return p.folkbooks


def info(game):
    """What lies where in this world: the books chosen and where each page is."""
    w = game.world
    V = getattr(w, 'folkbooks', None)
    if V is None:
        state = random.getstate()
        random.seed(game.seed * 7717 + 58)
        try:
            V = w.folkbooks = _choose(game)
        finally:
            random.setstate(state)
    return V


def north_of_wall(game, x, y):
    """Is this spot north of the Northern Wall (or, without a wall, in the far north)?"""
    om = game.maps.get('over')
    wall = (getattr(game.world, 'varnish', None) or {}).get('wall') or ()
    if om is not None and wall:
        ys = [i // om.w for i in wall if abs(i % om.w - x) <= 3]
        if ys:
            return y < min(ys)
    from .world import WORLD_H
    return y < WORLD_H * .16


def _locs(game, tag):
    """The places of a kind: ('town', sid) or ('site', id)."""
    w = game.world
    if tag.startswith('set:'):
        race = tag[4:]
        return [('town', s.id) for s in w.settlements if s.race == race and not north_of_wall(game, s.x, s.y)]
    if tag.startswith('site:'):
        kind = tag[5:]
        return [('site', s.id) for s in w.sites if s.kind == kind]
    if tag == 'north':
        return [('town', s.id) for s in w.settlements if north_of_wall(game, s.x, s.y)]
    if tag == 'city':
        return [('town', s.id) for s in w.settlements if s.is_city and s.race == 'human']
    if tag == 'court':
        return [('court', None)]
    return []


def _choose(game):
    """One or two books of each people (all of the small peoples' few), each spread over up to three places."""
    V = dict(books=[], pages={})
    for people in T.ORDER:
        books = [b for b in T.BOOKS if b['people'] == people]
        random.shuffle(books)
        keep = books if people in ('fey', 'north') else books[:random.choice((1, 2)) if len(books) > 2 else len(books)]
        for b in keep:
            locs = [lc for tag in b['where'] for lc in _locs(game, tag)]
            if not locs:
                continue
            random.shuffle(locs)
            locs = locs[:3]
            V['books'].append(b['key'])
            for n in range(len(b['pages'])):
                V['pages'][(b['key'], n)] = locs[n % len(locs)]
    return V


# ------------------------------------------------------------------ reading
def here_people(game):
    """Whose place you stand in, if a people's."""
    s = game.here
    if s is not None:
        if north_of_wall(game, s.x, s.y):
            return 'north'
        return s.race if s.race in T.PEOPLES else None
    sid = getattr(game.map, 'site', None)
    if sid is not None and game.cur != 'over':
        tag = 'site:' + game.world.sites[sid].kind
        return next((pe for pe, tags in HOME.items() if tag in tags), None)
    return None


def can_read(game, people):
    """Common letters anyone reads; a script needs one of that people: you, your hireling, or the folk round you."""
    if T.PEOPLES[people]['script'] is None:
        return True
    if getattr(game.player, 'race', 'human') == people:
        return True
    from . import mercs as MC
    if any(getattr(mc, 'race', None) == people for mc in MC.party(game)):
        return True
    return here_people(game) == people


def _fact(game, people, text, src, who, where, key, title=None):
    from . import chronicle as CH
    f = CH.add(game, 'Peoples', text, src, who=who, where=where, key=key, title=title, quiet=True)
    f['head'] = 'folk:' + people
    return f


def page_item(game, key):
    from .entities import Item
    it = Item(game.new_id(), 'fpage', 'fpage')
    it.fpage = key
    return it


def pick_page(game, it):
    """A page of a people goes in with your papers; you read it when you can."""
    s = st(game)
    key = it.fpage
    s['pages'].add(key)
    b = T.BOOK[key[0]]
    pe = T.PEOPLES[b['people']]
    if not can_read(game, b['people']):
        game.msg(f'You pick up a {pe["noun"]} written in {pe["script"]}. You cannot read it; you keep it with your '
                 'papers.', 'info')
        return
    read_page(game, key)


def read_page(game, key):
    s = st(game)
    if key in s['read']:
        return
    s['read'].add(key)
    bk, n = key
    b = T.BOOK[bk]
    pe = T.PEOPLES[b['people']]
    where = game.loc_name() if hasattr(game, 'loc_name') else None
    _fact(game, b['people'], b['pages'][n], 'read', f'a {pe["noun"]}, {b["title"]}', where, f'fp:{bk}:{n}')
    have = sum(1 for k in s['read'] if k[0] == bk)
    total = len(b['pages'])
    if have < total:
        game.msg(f'You read the {pe["noun"]}: {b["title"]}, {have} of {total}. Your chronicle grows: '
                 f'{pe["name"]}.', 'gold')
    elif pe['binder']:
        game.msg(f'You have all {total} of {b["title"]} now. {pe["binder"][0].upper() + pe["binder"][1:]} could bind '
                 'them.', 'unique')
    else:
        bind(game, bk, where, self_bound=True)


def read_carried(game):
    """Someone who can read them is with you now: the pages you carry are read."""
    s = st(game)
    left = sorted(k for k in s['pages'] if k not in s['read'] and can_read(game, T.BOOK[k[0]]['people']))
    for k in left:
        read_page(game, k)
    return len(left)


def complete(game):
    s = st(game)
    return [bk for bk in info(game)['books'] if bk not in s['bound']
            and all((bk, n) in s['read'] for n in range(len(T.BOOK[bk]['pages'])))]


# ------------------------------------------------------------------ binding, and what a whole book shows
def bind(game, bk, where, self_bound=False):
    from .entities import Item
    s = st(game)
    b = T.BOOK[bk]
    people = b['people']
    pe = T.PEOPLES[people]
    s['bound'].add(bk)
    for n in range(len(b['pages'])):
        s['pages'].add((bk, n))
        s['read'].add((bk, n))
    it = Item(game.new_id(), 'fbook', 'fbook')
    it.book = bk
    it.name = b['title']
    if not game.add_to_inv(it):
        game.spill(game.map, game.player.x, game.player.y, it)
    tell_dawn(game, people, pe['binder'] or b['title'], where)
    _fact(game, people, b['hidden'], 'read', b['title'], where, f'fb:{bk}', title=b['title'])
    _fact(game, people, b['chron'], 'read', b['title'], where, f'fbc:{bk}')
    if self_bound:
        game.msg(f'You lay the {pe["noun"]}s of {b["title"]} in order. Whole, they say more. Your chronicle grows.',
                 'unique')
    else:
        game.msg(f'{pe["binder"][0].upper() + pe["binder"][1:]} binds {b["title"]} for you, in the way of their '
                 'people. Your chronicle grows.', 'unique')
    effect(game, b.get('effect'), b['title'])


def tell_dawn(game, people, who, where):
    """The first whole book of a people: they tell you how the world began, their way."""
    s = st(game)
    if people in s['dawn']:
        return
    from . import varnish as VN
    before = VN.sky_open(game)
    s['dawn'].add(people)
    _fact(game, people, T.DAWN[people], 'heard', who, where, f'fd:{people}')
    game.msg(f'They tell you how the world began, as {T.PEOPLES[people]["name"].lower()} tell it.', 'gold')
    VN.sky_news(game, before)


def prologue_open(game):
    """Four peoples' own dawn tales, and the prologue of The Counted Sky opens."""
    return len(st(game)['dawn']) >= 4


def effect(game, eff, title):
    from . import varnish as VN
    if not eff:
        return
    kind = eff[0]
    if kind in ('place', 'recipe', 'way', 'riddle'):
        VN.effect(game, eff, title)
    elif kind == 'riddle_any':
        from . import varnishtexts as VT
        vs = VN.st(game)
        left = [i for i in range(len(VT.RIDDLE[eff[1]]['frags'])) if (eff[1], i) not in vs['frags']]
        if left:
            VN.riddle_frag(game, eff[1], left[0], title, 'in the bound book')
    elif kind == 'lore':
        VN.give_lore(game, 'read', title, game.loc_name())
    elif kind == 'favour':
        st(game)['favour'].add(eff[1])
        game.msg(f'{T.PEOPLES[eff[1]]["name"]} will know you read it. Their prices are a little kinder to you now.',
                 'good')
    elif kind in ('bardin', 'drains', 'north'):
        from . import storyland as SL
        getattr(SL, kind + '_known')(game)


def price_factor(game, town_race):
    """A people whose book you were given whole sells to you a little cheaper."""
    p = game.player
    return .95 if town_race in getattr(p, 'folkbooks', {}).get('favour', ()) else 1.0


# ------------------------------------------------------------------ being there
def _here_tags(game, s=None, site=None):
    if s is not None:
        tags = {'set:' + s.race}
        if north_of_wall(game, s.x, s.y):
            tags = {'north'}
        if s.is_city and s.race == 'human':
            tags.add('city')
        return tags
    return {'site:' + site.kind}


def on_town(game, s, m):
    """In a town of a people: one page of theirs handed over a day, reading through them, and binding."""
    V = info(game)
    loc = ('town', s.id)
    have = st(game)
    given = have['given']
    for key, where in sorted(V['pages'].items()):
        if where == loc and key not in have['pages'] and (s.id, game.day) not in given:
            given.add((s.id, game.day))
            people = T.BOOK[key[0]]['people']
            game.msg(GIVE.get(people, f'Someone here gives you a {T.PEOPLES[people]["noun"]}.'), 'info')
            pick_page(game, page_item(game, key))
            break
    read_carried(game)
    offer_bind(game, _here_tags(game, s=s))


def on_enter(game, site, m):
    """A people's place on the land: their pages lie here, and maybe one of them binds."""
    V = info(game)
    have = st(game)['pages']
    on = {getattr(i, 'fpage', None) for i in m.items}
    from .varnish import _spot
    for key, where in V['pages'].items():
        if where != ('site', site.id) or key in have or key in on:
            continue
        sp = _spot(m, (2, m.w - 3), (2, m.h - 3))
        if sp:
            it = page_item(game, key)
            it.x, it.y = sp
            m.items.append(it)
    read_carried(game)
    offer_bind(game, _here_tags(game, site=site))


def offer_bind(game, tags):
    from . import events as EV
    if getattr(game, 'pending', None):
        return
    for bk in complete(game):
        people = T.BOOK[bk]['people']
        if set(BIND_AT.get(people, ())) & tags:
            b = T.BOOK[bk]
            pe = T.PEOPLES[people]
            EV.ask(game, 'folkbind', pe['name'], f'You have every {pe["noun"]} of {b["title"]}. '
                   f'{pe["binder"][0].upper() + pe["binder"][1:]} here would bind them for you, their way.',
                   [('Have it bound', 'bind'), ('Not now', 'no')], book=bk)
            return


def r_bind(game, choice, ctx):
    if choice == 'bind' and ctx.get('book') in complete(game):
        bind(game, ctx['book'], game.loc_name())


def give_whole(game, bk):
    """A book you are given whole (the fey keep theirs bound)."""
    if bk not in st(game)['bound']:
        bind(game, bk, game.loc_name(), self_bound=True)


# ------------------------------------------------------------------ the chronicle's Peoples chapter
def source_text(key):
    """The text a fact of this chapter has in the books now (so a change to the words reaches old saves)."""
    try:
        kind, rest = key.split(':', 1)
        if kind == 'fp':
            bk, n = rest.rsplit(':', 1)
            return T.BOOK[bk]['pages'][int(n)]
        if kind == 'fb':
            return T.BOOK[rest]['hidden']
        if kind == 'fbc':
            return T.BOOK[rest]['chron']
        if kind == 'fd':
            return T.DAWN[rest]
    except (KeyError, ValueError, IndexError):
        return None
    return None


def blocks(game, fs):
    """Peoples: what people told you, then each people under its own heading: their dawn, their pages, their books."""
    from . import chronicle as CH
    out = []
    for f in fs:
        if (f.get('head') or '').startswith('folk:'):
            new = source_text(f['key'])
            if new and new != f['text']:
                f['text'] = new
    out += [('fact', f) for f in fs if not (f.get('head') or '').startswith('folk:')]
    s = st(game)
    for people in T.ORDER:
        got = [f for f in fs if f.get('head') == 'folk:' + people]
        if not got:
            continue
        out.append(('h', T.PEOPLES[people]['name']))
        dawn = [f for f in got if f['key'].startswith('fd:')]
        out += [('fact', f) for f in dawn]
        for bk in [b['key'] for b in T.BOOKS if b['people'] == people]:
            mine = [f for f in got if f['key'] in (f'fb:{bk}', f'fbc:{bk}') or f['key'].startswith(f'fp:{bk}:')]
            if not mine:
                continue
            b = T.BOOK[bk]
            if bk not in s['bound']:
                have = sum(1 for k in s['read'] if k[0] == bk)
                out.append(('p', f'{b["title"]}: {have} of {len(b["pages"])}.'))
            mine.sort(key=lambda f: (f['key'].startswith('fb'), f['key']))
            out += [('fact', f) for f in mine]
    unread = sorted({k[0] for k in s['pages'] if k not in s['read']})
    for bk in unread:
        pe = T.PEOPLES[T.BOOK[bk]['people']]
        out.append(('gap', f'You carry a {pe["noun"]} in {pe["script"]} that you cannot read. One of '
                           f'{pe["name"].lower()} could read it to you.'))
    for g in CH.gaps(game, 'Peoples'):
        out.append(('gap', g))
    if len(s['dawn']) < 4:
        out.append(('gap', 'Each people tells how the world began its own way. They tell it to those who have '
                           'read their books.'))
    return out or [('p', 'Nothing yet.')]


# ------------------------------------------------------------------ voices
def voice(game, npc):
    """A line in a people's own tone, or None."""
    race = getattr(npc, 'race', None)
    if race not in T.VOICES:
        return None
    if race == 'elf' and 'ninenames' in st(game)['bound'] and random.random() < .2:
        return T.ELF_KNOWN
    return random.choice(T.VOICES[race])


# ------------------------------------------------------------------ items (entities.CRAFT)
def display(game, it):
    if it.k == 'fbook':
        return it.name
    pe = T.PEOPLES[T.BOOK[it.fpage[0]]['people']]
    return f'A {pe["noun"]} of {pe["name"].lower()}'


def lines(game, it):
    if it.k == 'fbook':
        b = T.BOOK[it.book]
        return [f'A book of {T.PEOPLES[b["people"]]["name"].lower()}, whole.', b['chron']]
    return ['A page of a people\'s own book.']


def value(game, it):
    return 1 if it.k == 'fbook' else .1


def glyph(it):
    return '≡' if it.k == 'fbook' else '~'


def color(it):
    return (200, 180, 120) if it.k == 'fbook' else (216, 206, 176)


def read_bound(game, it):
    b = T.BOOK[it.book]
    game.request = ('dialog', b['title'], '\n\n'.join(b['pages'] + [b['hidden']]))
    return 0


def register():
    from . import events as EV
    from . import entities as EN
    EV.RESOLVERS['folkbind'] = r_bind
    EN.CRAFT.update({'fpage': 'folkbooks', 'fbook': 'folkbooks'})


register()
