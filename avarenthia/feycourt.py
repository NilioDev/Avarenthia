"""The court under the hill (round 58c): a secret of the fey, for whoever happens on it.

Deliberately not in the handbook, the Signs, a map layer, a rumour or the wiki (Nilio, 6 November 2026): one grassy
barrow per world looks like any other, with a ring of white mushrooms round it. At night under a full moon, walking
once round the hill widdershins inside the ring opens a door in its flank. Inside, a round hall of roots in a dusk
light from nowhere, alive with movement (the one place that breaks the look rule's "movement scarce", on purpose):
the floor's colours wave out from the dance, motes rise, candles never burn down, a honey stream runs uphill, the
root walls breathe; what moves leaves a fading trail, flowers open where you step and wilt behind you, the guests
keep changing sign, the mirror pool shows you walking the other way and lets you out on the far side, the date reads
"?", the words of a bargain light up gold in the log, honey wine turns the colours inside out and the log's letters
swap. A night inside is a season outside. What you take away is a memory: the fey's book, a purse with one coin, a
line under Your deeds. The hall keeps its shape."""
import math
import random

from . import data as D

KEY = 'fey:court'
W, H = 48, 28
CX, CY = 24, 13                 # the dance
POOL = (37, 14)
GOLD_WORDS = ['never empty', 'to the letter', 'one night', 'for ever and a day', 'freely given']
HOWE_NAMES = ['The Long Barrow', 'Ash Howe', 'Thorn Barrow', 'The Low Howe', 'Hob Barrow', 'The Green Mound',
              'Cold Barrow']


# ------------------------------------------------------------------ state
def st(game):
    from . import storyland as SL
    s = SL.st(game)
    s.setdefault('fey', dict(visits=0, bargains=set(), noname=False))
    return s['fey']


def place(game, lay, V):
    """One grassy barrow, like any other."""
    m = lay.m
    spot = lay.search(lambda x, y: m.tile(x, y) in (D.GRASS, D.HILLS) and 3 <= lay.road(x, y) <= 14
                      and y > m.h * .25, 6)
    if spot:
        V['howe'] = lay.add('howe', spot, random.choice(HOWE_NAMES)).id


def in_court(game):
    return game.cur == KEY


# ------------------------------------------------------------------ the barrow outside
def _m_howe(game, site):
    from . import landmarks as LM
    m = LM.land(game, site, 50, 34)
    cx, cy = m.w // 2, m.h // 2
    LM.clear(m, cx, cy, 11, 7)
    LM.way(m, (0, cy), (cx - 9, cy))
    m = LM.finish(m, (0, cy))
    for y in range(m.h):
        for x in range(m.w):
            d = math.hypot(x - cx, (y - cy) * 1.6)
            if d <= 3.6:
                LM.put(m, x, y, 'mound')
            elif 6.6 <= d <= 7.4 and (x + y) % 2 == 0:
                LM.put(m, x, y, 'mushring', walk=True)
    m.howe = dict(c=(cx, cy), turned=0.0, last=None, open=False)
    if getattr(game, '_fey_door', False):       # back out of the court: you come out by the door
        game._fey_door = False
        open_door(game, m, quiet=True)
    return m


def _angle(m, x, y):
    cx, cy = m.howe['c']
    return math.atan2(-(y - cy) * 1.6, x - cx)


def step_howe(game, m):
    """Once round the hill widdershins, inside the ring, at night under a full moon: the door."""
    hw = getattr(m, 'howe', None)
    if hw is None or hw['open']:
        return
    p = game.player
    cx, cy = hw['c']
    d = math.hypot(p.x - cx, (p.y - cy) * 1.6)
    if not 3.6 < d < 6.8:
        hw['turned'], hw['last'] = 0.0, None
        return
    a = _angle(m, p.x, p.y)
    if hw['last'] is not None:
        da = (a - hw['last'] + math.pi) % math.tau - math.pi
        hw['turned'] += da
    hw['last'] = a
    if hw['turned'] < -1:                     # sunwise undoes it: start again
        hw['turned'] = 0.0
    if hw['turned'] >= math.tau - .25:
        hw['turned'] = 0.0
        from . import nature as NT
        from . import towns as TW
        if TW.is_night(game) and NT.full_moon(game):
            open_door(game, m)
        elif TW.is_night(game):
            game.msg('Somewhere under your feet, very faintly, music stops, as if someone were listening.', 'info')


def open_door(game, m, quiet=False):
    from . import landmarks as LM
    hw = m.howe
    cx, cy = hw['c']
    hw['open'] = True
    x, y = cx, cy + 2
    LM.put(m, x, y, 'feydoor')
    m._look = None
    hw['door'] = (x, y)
    if not quiet:
        game.msg('A seam of pale light opens in the flank of the barrow, where there was only grass. Music comes out of '
                 'it, and the smell of honey.', 'unique')


def act(game, site, key, x, y):
    if key == 'mound':
        game.msg('Grass, and under the grass old earth. Nothing more.', 'info')
        return 0
    if key == 'mushring':
        return 0
    if key == 'feydoor':
        enter(game)
        return 1
    if key == 'feyexit':
        leave(game)
        return 1
    if key == 'candle':
        game.msg('A candle as tall as you, burning. It does not get any shorter.', 'info')
        return 0
    return None


# ------------------------------------------------------------------ the court
def make(game, site):
    from .entities import GameMap
    from . import landmarks as LM
    m = GameMap(KEY, 'town', 'Under the hill', W, H, D.FLOOR)
    m.glows, m.lights = [], []
    m.radius, m.sid, m.hid, m.signs = 60, None, None, []
    m.site = site.id
    m.lm = 'howe'
    m.tells, m.over = {}, {}
    m.level = 1
    m.underground = True
    stream, pool = set(), set()
    for y in range(H):
        for x in range(W):
            d = math.hypot((x - CX) / 21.5, (y - CY) / 11.5)
            if d > 1:
                m.set(x, y, D.WALL)
            elif 6 <= y <= 21 and x == 9 + (y % 3 == 0):
                m.set(x, y, D.SHALLOW)
                stream.add((x, y))
            elif math.hypot((x - POOL[0]) / 4.2, (y - POOL[1]) / 2.2) <= 1:
                m.set(x, y, D.SHALLOW)
                pool.add((x, y))
    for k in range(10):
        a = k * math.tau / 10
        LM.put(m, round(CX + 18 * math.cos(a)), round(CY + 9 * math.sin(a)), 'candle')
    for i in list(m.tells):
        if m.tells[i] == 'candle':
            m.glows.append((i % W, i // W, (255, 214, 140), 4))
    LM.put(m, CX, H - 2, 'feyexit')
    m.fey = dict(stream=stream, pool=pool, trail={}, flowers={}, last=None, moved={})
    host = LM.npc(game, m, 'The host of the hill', '#e8d8ff', CX, CY - 6, 'howe')
    if host:
        host.fey = 'host'
    for k in range(7):
        a = k * math.tau / 7
        o = LM.npc(game, m, 'A guest of the court', '#d0f0c0', round(CX + 6 * math.cos(a)),
                   round(CY + 3 * math.sin(a)), 'howe', stay=False)
        if o:
            o.fey = 'guest'
    for i in range(len(m.seen)):
        m.seen[i] = 1
    m.lights = list(m.glows)
    m.entry = (CX, H - 3)
    return m


def enter(game):
    m = game.map
    site = game.world.sites[m.site]
    s = st(game)
    s['visits'] += 1
    s['in'] = game.turn
    if KEY not in game.maps:
        game.maps[KEY] = make(game, site)
    c = game.maps[KEY]
    game.cur = KEY
    p = game.player
    p.x, p.y = c.entry
    c.fey['last'] = (p.x, p.y)
    game.compute_fov()
    game.msg('You step into the hill, and the music takes you by both hands.', 'unique')


def leave(game):
    """Out of the hill: one night inside, a season outside."""
    s = st(game)
    site = game.world.sites[game.map.site]
    game._fey_door = True
    game.maps.pop(site.map_key, None)
    game.enter_site(site.id)
    m = game.map
    door = getattr(m, 'howe', {}).get('door')
    if door:
        game.player.x, game.player.y = door[0], door[1] + 1
    game.turn += 90 * D.DAY_LEN
    game.end_turn(0, quiet=True)
    from . import calendar as CAL
    season = CAL.season(game.day)
    game.msg(f'You step out of the hill into a morning that smells wrong. The grass is another colour; the trees have '
             f'turned. It is {season} now. One night inside, and outside a season has gone.', 'unique')
    s['noname'] = False
    if s['visits'] == 1:
        from . import chronicle as CH
        CH.deed(game, 'A night under the hill', 'You danced one night in the court under the hill, and came out a '
                                                'season later. You do not remember all of it.')
    game.compute_fov()


# ------------------------------------------------------------------ in the court: each step
def court_step(game, m):
    F = m.fey
    p = game.player
    turn = game.turn
    last = F.get('last')
    if last and last != (p.x, p.y):
        F['trail'][last] = ('@', (190, 170, 120), turn)
    F['last'] = (p.x, p.y)
    if (p.x, p.y) not in F['pool']:
        F['flowers'][(p.x, p.y)] = turn
    for o in m.mons:
        if getattr(o, 'fey', None) != 'guest':
            continue
        was = F['moved'].get(o.id)
        if was and was != (o.x, o.y):
            F['trail'][was] = (o.ch, o.fg, turn)
        F['moved'][o.id] = (o.x, o.y)
        o.ch = random.choice('fcpn@☺')
        o.name = 'A guest of the court' if random.random() < .35 else random.choice(
            ['A fox in a green coat', 'A tall cat', 'A piper', 'Nobody', 'An old woman', 'A child', 'You',
             'A hare standing up', 'A lady of the court'])
    for k in [k for k, v in F['trail'].items() if turn - v[2] > 6]:
        del F['trail'][k]
    for k in [k for k, v in F['flowers'].items() if turn - v > 12]:
        del F['flowers'][k]
    if (p.x, p.y) in F['pool']:
        nx, ny = 2 * CX - p.x, p.y
        if m.inb(nx, ny) and D.TILES[m.tile(nx, ny)].walk and not m.mon_at(nx, ny):
            F['trail'][(p.x, p.y)] = ('@', (190, 210, 255), turn)
            p.x, p.y = nx, ny
            F['last'] = (nx, ny)
            game.msg('You step into the pool, and step out of it on the far side of the court, the wrong way round.',
                     'info')
            game.compute_fov()


def on_step(game, site, m):
    if m.key == KEY:
        court_step(game, m)
    else:
        step_howe(game, m)


# ------------------------------------------------------------------ the host and the guests
GUEST = ['You are late. You are early. Which is it?', 'Dance! Or do not. It comes to the same thing, here.',
         'What a lovely name you have. May I keep it? No? Pity.', 'The elves? Our little cousins. They grew up so '
         'serious.', 'Count the stars? Oh, you must not. They hate it.', 'Have a flower. Have another. They are '
         'yours anyway, you made them.', 'The moon is full. The moon is always full, here.', 'Shall I tell you the '
         'time? No. It would only upset you.']


def talk(game, site, o):
    from . import landmarks as LM
    if getattr(o, 'fey', None) != 'host':
        game.say(o, random.choice(GUEST))
        return
    s = st(game)
    b = s['bargains']
    opts = [('A purse that is never empty', 'fey_purse' if 'purse' not in b else None),
            ('A cup of honey wine', 'fey_wine'),
            ('Their book', 'fey_book' if 'book' not in b else None), ('Nothing, thank you', 'bye')]
    LM.ask(game, site, o.name, 'Someone sits on a chair of roots at the edge of the dance, taller than anyone, dressed '
           'in dusk. "A guest," the host says, and smiles all the way up. "Guests may ask. We keep every bargain, to '
           'the letter. Ask."', opts)


def r_fey(game, choice, ctx):
    from .entities import Item
    from . import chronicle as CH
    s = st(game)
    p = game.player
    if choice == 'fey_purse':
        s['bargains'].add('purse')
        s['noname'] = True
        it = Item(game.new_id(), 'curio', 'feypurse')
        if not game.add_to_inv(it):
            game.spill(game.map, p.x, p.y, it)
        game.msg('"A purse that is never empty," the host says. "To the letter. And for it, your name: one night."',
                 'info')
        game.msg('never empty. to the letter. one night.', 'gold')
        CH.add(game, 'Your deeds', 'You struck a bargain with the host of the hill: a purse that is never empty, for '
                                   'your name, one night.', 'seen', where='Under the hill', key='fey:purse',
               title='A bargain under the hill')
    elif choice == 'fey_wine':
        p.buffs = [b for b in p.buffs if b[0] != 'honeywine'] + [['honeywine', 0, 60, 'Honey wine']]
        game.msg('The wine is gold and tastes of every summer you remember. Then the world turns inside out, gently.',
                 'unique')
    elif choice == 'fey_book':
        s['bargains'].add('book')
        game.msg('"Freely given," the host says, which is not a word they use lightly, and hands you a book of thin '
                 'gold leaves.', 'info')
        game.msg('freely given.', 'gold')
        from . import folkbooks as FB
        FB.give_whole(game, 'feypact')


def _c_howe(game, site, choice, ctx):
    from . import storyland as SL
    SL.r_story(game, choice, ctx)


# ------------------------------------------------------------------ how it looks (ui.GameScreen draws every cell through here)
def _hue(h, s=.45, v=.6):
    i = int(h * 6) % 6
    f = h * 6 - int(h * 6)
    p, q, t = v * (1 - s), v * (1 - f * s), v * (1 - (1 - f) * s)
    r, g, b = [(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)][i]
    return int(r * 255), int(g * 255), int(b * 255)


def _mix(a, b, k):
    return tuple(int(a[j] + (b[j] - a[j]) * k) for j in range(3))


def cell(game, m, x, y, look, t):
    """The look of a cell of the court now."""
    ch, fg, bg = look
    F = m.fey
    i = y * m.w + x
    tile = m.t[i]
    turn = game.turn
    p = game.player
    o = m.mon_at(x, y)
    if tile == D.WALL:
        k = .5 + .5 * math.sin(t * .7 + (x + y) * .3)
        ch = '§%&'[(x * 7 + y * 3) % 3]
        fg = _mix((90, 60, 40), (150, 112, 70), k)
        bg = _mix((14, 10, 8), (30, 20, 14), k)
    elif (x, y) in F['stream']:
        g = max(0.0, math.sin(math.pi * ((y / 6 + t * .6) % 1.0)) - .6) * 2.5     # light runs up the stream
        ch, fg, bg = '≈' if (y + int(t * 3)) % 2 else '~', _mix((200, 150, 50), (255, 230, 140), g), (70, 46, 14)
    elif (x, y) in F['pool']:
        k = .5 + .5 * math.sin(t * 1.3 + x * .7)
        ch, fg, bg = '~' if (x + y + int(t)) % 4 == 0 else ' ', (150, 170, 220), _mix((18, 24, 50), (30, 40, 76), k)
        rx = POOL[0] - (p.x - POOL[0])
        if (x, y) == (rx, p.y) and (x, y) != (p.x, p.y):
            ch, fg = '@', (170, 190, 240)
    elif tile != D.MARK:
        d = math.hypot(x - CX, (y - CY) * 1.8)
        col = _hue((d * .045 - t * .12) % 1.0)
        bg = _mix((18, 14, 28), col, .38)
        fg = _mix(col, (255, 255, 255), .3)
        ch = '.' if (x * 31 + y * 17) % 3 else ','
        ph = (y / 13 + t * .18 + ((x * 37) % 11) / 11) % 1.0              # motes rise
        if (x * 13 + y * 7) % 19 == 0 and ph < .12:
            ch, fg = '·', (255, 244, 210)
    elif m.tells.get(i) == 'candle':
        from . import anim as AN
        f = AN.flame(t, x, y)
        ch, fg, bg = 'ì', (255, int(214 * f), int(140 * f)), (int(60 * f), 30, 12)
    if not o and (x, y) != (p.x, p.y):
        tr = F['trail'].get((x, y))
        if tr:
            age = (turn - tr[2]) / 6
            ch, fg = tr[0], _mix(tuple(tr[1]), bg, min(1.0, age + .3))
        fl = F['flowers'].get((x, y))
        if fl is not None and tile != D.WALL:
            a = turn - fl
            col = _hue(((x * 7 + y * 11) % 10) / 10, .5, .95)
            ch, fg = ('·', (150, 200, 120)) if a < 2 else ('*', col) if a < 8 else (',', (140, 110, 70))
    elif o and getattr(o, 'fey', None) == 'guest':
        k = .5 + .5 * math.sin(t * 2 + o.id)
        ch, fg = 'fcpn@'[int(t * .6 + o.id) % 5], _mix((200, 240, 190), (255, 210, 250), k)
    if any(b[0] == 'honeywine' for b in p.buffs):
        fg, bg = tuple(255 - c for c in bg), tuple(255 - c for c in fg)
    return ch, fg, bg


def date(game, text):
    """The date under the map while you are in the hill."""
    return '? ?' if in_court(game) else text


def long_date(game, text):
    return 'Day ?, ?, year ?' if in_court(game) else text


def shown_name(game):
    return '?' if in_court(game) and st(game).get('noname') else game.player.name


def gold_words(game):
    return GOLD_WORDS if st(game)['bargains'] or in_court(game) else ()


def swap(game, ln):
    """Honey wine: the letters of the log swap places."""
    if not any(b[0] == 'honeywine' for b in game.player.buffs):
        return ln
    out = []
    for wd in ln.split(' '):
        if len(wd) > 3:
            wd = wd[0] + wd[2] + wd[1] + wd[3:]
        out.append(wd)
    return ' '.join(out)


def register():
    from . import landmarks as LM
    from . import sites as SI
    from . import places as PL
    from .nature import CURIO
    for k, n, c, f in [('mound', 'grassy barrow', '∩', (120, 170, 96)), ('mushring', 'white mushrooms', '∙',
                                                                          (244, 240, 230)),
                       ('feydoor', 'seam of pale light', '▒', (240, 230, 255)), ('feyexit', 'way out', '▒',
                                                                                  (200, 190, 220)),
                       ('candle', 'tall candle', 'ì', (255, 214, 140))]:
        LM.thing_kind(k, n, c, f)
    look = (PL.SIGN['barrow'], PL.FG['human'])
    LM.LOOK['howe'] = look
    LM.DESC['howe'] = f'A barrow of the {PL.PLURAL["human"]}: the grave of someone great.'
    LM.NAME['howe'] = ''
    SI.SITE_LOOK['howe'] = look
    LM.BUILD['howe'] = _m_howe
    LM.ACT['howe'] = act
    LM.TALK['howe'] = talk
    LM.CHOOSE['howe'] = _c_howe
    LM.STEP['howe'] = on_step
    LM.LINES['howe'] = 'A grassy barrow, very old, with a ring of white mushrooms round it.'
    CURIO['feypurse'] = ('A purse that is never empty', 0, (230, 210, 120), 'A little purse of green silk. There is a '
                         'coin in it, one copper. There is always one copper in it. It is never empty.')


register()
