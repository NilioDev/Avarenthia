"""The quest and the Sky-Seat (the great evils, part 2).

Mist and storm hide the piece of the Sky-Seat that never fell, until you know the truth (the riddle of the Hollow
King made whole) or the first servant breaks a seal; then the mist tears and the city shows over the sea. The
relics of fallen servants are the keys through the mist (or the Star-Iron Key, for whoever makes all five riddles
whole). No road you can travel by leads through his coast: you walk it. One skipper on the nearest coast dares the
whirlpool. The Varnish chained the city down with star-iron: you climb a chain (gusts, broken links, things that hang
there) and the glass underside (cracked panes, the wind over the edge, the fall to the sea), then five floors of
glass and bronze with a beacon on each, to the throne. The last fight has three phases, the winds, the dead and
himself; each relic you bring makes one lighter.

Dying there: he keeps those who die in his city, so the raising costs twice as much and you wake on the mainland,
and your body rises as your shade with your backpack. Where the dead are bound (his city, the barrows, the crypts,
the Rift) the same happens. What you opened stays open, the slain stay dead, a floor with its beacon lit stays calm;
on the others he sends new bound dead. If he wins (three seals): the Long Night. If you win: a closing screen, and a
world that heals. State on world.shadow."""
import copy
import math
import random

from . import data as D
from .worldgen import cheb

FLOORS = ['The Under-City', 'The Hall of the Winds', 'The Halls of the Dead', 'The Bronze Galleries',
          'The Throne of the Winds']
FARE = 2000                 # copper: twenty silver for a skipper who dares the whirlpool
CHAIN = 'skyseat:chain'
MIST = [('░', (150, 160, 176)), ('▒', (120, 130, 150)), ('░', (176, 184, 196)), ('~', (110, 126, 150))]
STARKEY = ('The Star-Iron Key', 'res_all', 2, 'A key of star-iron as long as your forearm, from the riddles\' answer.')
LIGHT_TEXT = ['The winds falter round him: one of your relics is cold as ice.',
              'The bound dead hang back from you: a relic in your pack holds them.',
              'He is less than he was: the last relic you carry burns in your pack.']


def sh(world):
    return getattr(world, 'shadow', None)


# ------------------------------------------------------------------ the mist
def setup(game, m, world):
    """At the making of the world: the Sky-Seat goes under mist, and its five floors wait."""
    s = sh(world)
    sky = s['sky']
    s.update(seen=False, seat_over={}, beacons=set(), won=False, kept=None, fare_paid=False)
    if not sky:
        return
    x0, y0 = sky[0], sky[1] + 10
    ov = m.over if getattr(m, 'over', None) is not None else {}
    m.over = ov
    for y in range(max(0, y0 - 24), min(m.h, y0 + 25)):
        for x in range(max(0, x0 - 46), min(m.w, x0 + 47)):
            i = y * m.w + x
            inside = ((x - x0) / 44) ** 2 + ((y - y0) / 22) ** 2 <= 1
            if not inside:
                continue
            if i in ov:
                s['seat_over'][i] = ov[i]
            if m.t[i] == D.WATER or i in ov or i in getattr(world, 'wonder_cells', ()):
                ch, fg = MIST[(x * 7 + y * 13) % len(MIST)]
                ov[i] = (ch, fg, (40, 46, 58))
    s['wonder'] = next((wd for wd in world.wonders if wd[0] == 'The Sky-Seat'), None)
    if s['wonder']:
        world.wonders = [wd for wd in world.wonders if wd[0] != 'The Sky-Seat']
    from .world import Dungeon
    dg = Dungeon('skyseat', 'The Sky-Seat', len(FLOORS), 18, 'rooms', 'skyseat', 'hollow_king',
                 D.hexrgb('#b08a4a'), sky[0], sky[1], True)
    dg.sky = True
    world.dungeons['skyseat'] = dg


def revealed(world):
    s = sh(world)
    return bool(s and s.get('seen'))


def check(game):
    """The mist tears when you know the truth, or when the first seal breaks."""
    from . import shadow as SH
    s = sh(game.world)
    if s and not s.get('seen') and s.get('sky') and (SH.know(game)['king'] or s.get('torn')):
        reveal(game)


def reveal(game):
    w = game.world
    s = sh(w)
    s['seen'] = True
    om = game.maps['over']
    x0, y0 = s['sky'][0], s['sky'][1] + 10
    for i in [i for i in om.over if abs(i % om.w - x0) <= 46 and abs(i // om.w - y0) <= 24]:
        if ((i % om.w - x0) / 44) ** 2 + ((i // om.w - y0) / 22) ** 2 <= 1:
            del om.over[i]
    om.over.update(s['seat_over'])
    if s.get('wonder'):
        w.wonders.append(s['wonder'])
    om._look = None
    game.msg('Far out over the sea the mist tears open. A city of glass and bronze hangs in the air above a '
             'turning sea: the Sky-Seat, the piece that never fell.', 'unique')
    from . import news as NW
    NW.post(game, 'danger', 'The fishermen say the mist out at sea has torn, and there is a city in the sky behind '
                            'it.', *(s['coast'] or s['sky']))
    from . import guide as GDE
    GDE.tip(game, 'skyseat')


# ------------------------------------------------------------------ the keys and the skipper
def keys(game):
    return [it for it in game.player.inv if it.k == 'relic']


def star_key(game):
    """All five riddles made whole: the Star-Iron Key, the hard other way through the mist."""
    if any(it.k == 'relic' and it.t == 'starkey' for it in game.player.inv) or game.__dict__.get('starkey'):
        return
    from .entities import Item
    game.starkey = True
    it = Item(game.new_id(), 'relic', 'starkey')
    it.name = STARKEY[0]
    if not game.add_to_inv(it):
        game.spill(game.map, game.player.x, game.player.y, it)
    game.msg('The answer to the last riddle is a place in an old vault, and in it lies a key of star-iron. You take '
             'it: it opens the mist as well as any relic.', 'unique')


def dares(game, here):
    """The one skipper who dares the whirlpool: on the harbour nearest his coast."""
    s = sh(game.world)
    if not s or not s.get('seen') or s.get('won') or not s.get('coast'):
        return False
    from .living import harbours
    hs = harbours(game)
    if not hs:
        return False
    cx, cy = s['coast']
    best = min(hs, key=lambda q: cheb(q.x, q.y, cx, cy))
    return here.id == best.id


def opt(game, here):
    return [('Out past the mist, to the whirlpool', 'whirl')] if dares(game, here) else []


def whirl(game):
    """The voyage out: a relic to show the mist, the fare, two days at sea, then the chain."""
    from .money import fmt
    from . import events as EV
    p = game.player
    if not keys(game):
        game.msg('"Into the mist? Not without something of his to show it. The mist knows its own. Bring me one of '
                 'the keys, and I will take you."', 'info')
        return
    if p.gold < FARE:
        game.msg(f'"{fmt(FARE)}, and I do not haggle. Nobody else would take you at all."', 'info')
        return
    EV.ask(game, 'skyseat', 'The whirlpool', f'"{fmt(FARE)}. Two days out, and I put you on the rocks where the '
           'chain comes down. I will wait three days. Not four." Your company cannot come in a boat this small.',
           [('Go aboard', 'go'), ('Not yet', 'bye')])


def r_sky(game, choice, ctx):
    if choice == 'go':
        p = game.player
        from .money import fmt
        if p.gold < FARE:
            return
        p.gold -= FARE
        game.end_turn(D.DAY_LEN * 2, True)
        if game.dead:
            return
        game.msg(f'Two days through the mist. The skipper keeps the {fmt(FARE)} and his eyes on the water.', 'info')
        to_chain(game)
    elif choice and choice.startswith('floor:'):
        enter_floor(game, int(choice.split(':')[1]))
    elif choice == 'climb':
        to_chain(game, top=False, ask=False)
    elif choice == 'home':
        home(game)
    elif choice == 'jump':
        fall(game, *ctx['cell'])


def to_chain(game, top=False, ask=True):
    s = sh(game.world)
    lit = sorted(s['beacons'])
    if ask and lit and not top:
        from . import events as EV
        EV.ask(game, 'skyseat', 'The rocks under the chain', 'The beacon you lit burns up there, and from it a rope of '
               'light hangs down to the rocks. You could climb the chain again, or go up the light.',
               [('Climb the chain', 'climb')] + [(f'Up the light to {FLOORS[d - 1]}', f'floor:{d}') for d in lit[-1:]])
        if game.cur != 'over':
            game.over_pos = game.world_pos()
        return
    if game.cur == 'over':
        game.over_pos = (game.player.x, game.player.y)
    if CHAIN not in game.maps:
        game.maps[CHAIN] = chain_map(game)
    m = game.maps[CHAIN]
    game.cur = CHAIN
    p = game.player
    p.x, p.y = m.top if top else m.entry
    game.compute_fov()
    if not top:
        game.msg('The boat bumps against black rock. Above you a chain of star-iron, each link as tall as a man, '
                 'goes up into the wind and the glass city.', 'unique')
    game.request = ('save',)


def enter_floor(game, d):
    game.enter_dungeon('skyseat', d, 'up')


def home(game):
    """Back aboard, and back to the harbour."""
    from .living import harbours
    s = sh(game.world)
    p = game.player
    hs = harbours(game)
    cx, cy = s['coast']
    best = min(hs, key=lambda q: cheb(q.x, q.y, cx, cy)) if hs else game.world.settlements[0]
    game.end_turn(D.DAY_LEN * 2, True)
    if game.dead:
        return
    game.cur = 'over'
    p.x, p.y = best.x, best.y
    game.enter_town(best.id)
    game.msg('Two days back through the mist, and the skipper does not say a word the whole way.', 'info')


# ------------------------------------------------------------------ the chain and the underside
def chain_map(game):
    """A chain of star-iron from the sea rocks up to the city's underside: the links three wide, empty air all
    round, handholds where the chain is bound to the rock (`D.CHAIN`, safe from a gust), broken links that give if
    you stand on them, things that hang there; then the underside of glass and bronze, its cracked panes, and the
    stair up into the city."""
    from .entities import GameMap, make_monster
    state = random.getstate()
    random.seed(game.seed * 911 + 77)
    try:
        w, h = 44, 96
        m = GameMap(CHAIN, 'dungeon', 'The Chain of the Sky-Seat', w, h, D.AIR)
        m.depth, m.did = 0, 'skyseat'
        m.skychain = True
        m.deco = bytearray(w * h)
        m.radius = 14
        for y in range(h - 8, h):
            for x in range(w):
                m.set(x, y, D.WATER)
        cx = w // 2
        for y in range(h - 7, h - 2):
            for x in range(cx - 7, cx + 8):
                if ((x - cx) / 7.5) ** 2 + ((y - (h - 5)) / 2.6) ** 2 <= 1:
                    m.set(x, y, D.BAREROCK)
        m.set(cx - 5, h - 4, D.RAFT)
        m.entry = (cx - 3, h - 4)
        # the chain: three links wide, swinging from side to side on its way up
        top = 26
        pts = []
        for y in range(h - 7, top - 1, -1):
            k = (h - 7 - y) / (h - 7 - top)
            x = round(cx + math.sin(k * math.pi * 2.2) * 9)
            pts.append((x, y))
        weak = 0
        for i, (x, y) in enumerate(pts):
            for dx in (-1, 0, 1):
                if m.tile(x + dx, y) in (D.AIR,):
                    m.set(x + dx, y, D.STARLINK)
            if i > 8 and i % 9 == 4 and weak < 7:
                side = random.choice((-1, 1))
                m.set(x + side, y, D.WEAKLINK)
                weak += 1
            if i % 7 == 0 and i > 3:
                side = random.choice((-2, 2))
                if m.tile(x + side, y) == D.AIR:
                    m.set(x + side, y, D.CHAIN)
        # the underside: glass and bronze, cracked panes, the edge all round
        for y in range(3, top + 1):
            for x in range(3, w - 3):
                if ((x - cx) / 19) ** 2 + ((y - 14) / 12) ** 2 <= 1:
                    m.set(x, y, D.GLASS)
        for _ in range(26):
            x, y = random.randint(5, w - 6), random.randint(5, top - 2)
            if m.tile(x, y) == D.GLASS and abs(x - pts[-1][0]) + abs(y - top) > 4:
                m.set(x, y, D.CRACKGLASS)
        for x, y in ((cx - 10, 8), (cx + 10, 8), (cx, 19), (cx - 14, 15), (cx + 14, 15)):
            if m.tile(x, y) in (D.GLASS, D.CRACKGLASS):
                m.set(x, y, D.CHAIN)                     # bronze ribs to hold on to
        m.set(cx, 4, D.UP)
        m.top = (cx, 5)
        for x in range(cx - 1, cx + 2):
            for y in range(4, 7):
                if m.tile(x, y) == D.CRACKGLASS:
                    m.set(x, y, D.GLASS)
        lvl = 18
        for i in range(10, len(pts) - 4, 11):
            x, y = pts[i]
            m.mons.append(make_monster(game, random.choice(['gloomwing', 'needlewing', 'storm_spirit']), x, y, lvl))
        for _ in range(4):
            x, y = random.randint(8, w - 9), random.randint(6, top - 3)
            if m.tile(x, y) == D.GLASS and not m.mon_at(x, y):
                m.mons.append(make_monster(game, random.choice(['bound_dead', 'gargoyle', 'storm_spirit']), x, y, lvl))
        m.gust = None
        m.held = {}
        for i in range(len(m.seen)):
            m.seen[i] = 0
    finally:
        random.setstate(state)
    return m


def holding(game, m):
    p = game.player
    return any(m.inb(p.x + dx, p.y + dy) and m.tile(p.x + dx, p.y + dy) == D.CHAIN for dx in (-1, 0, 1) for dy in (-1, 0, 1))


def turn(game):
    """Each turn on the chain: the gusts, sung a turn before by the chain, and links and panes that give."""
    m = game.map
    p = game.player
    t = m.tile(p.x, p.y)
    if t in (D.WEAKLINK, D.CRACKGLASS):
        n = m.held.get((p.x, p.y), 0) + 1
        m.held[(p.x, p.y)] = n
        if n == 1:
            game.msg('The broken link groans under you.' if t == D.WEAKLINK else 'The glass cracks further under your '
                     'feet.', 'bad')
        else:
            m.set(p.x, p.y, D.AIR)
            m.held.pop((p.x, p.y), None)
            game.msg('It gives way!', 'bad')
            fall(game, p.x, p.y)
            return
    for c in [c for c in m.held if c != (p.x, p.y)]:
        m.held.pop(c)
    g = m.gust
    if g is None:
        if random.random() < .13:
            dx = random.choice((-1, 1))
            m.gust = dict(t=game.turn + 1, dx=dx)
            game.msg(f'The chain starts to sing: a gust is coming from the {"west" if dx > 0 else "east"}. Hold on to '
                     'something.', 'bad')
        return
    if game.turn < g['t']:
        return
    m.gust = None
    if holding(game, m):
        game.msg('The gust tears at you, and you hold on.', 'info')
        return
    n = 2 if p.y < m.top[1] + 22 and t in (D.GLASS, D.CRACKGLASS) else 1
    for _ in range(n):
        nx = p.x + g['dx']
        tt = m.tile(nx, p.y) if m.inb(nx, p.y) else D.AIR
        if tt == D.AIR:
            game.msg('The gust takes you off the chain!', 'bad')
            fall(game, nx, p.y)
            return
        if not D.TILES[tt].walk or game.occupied(m, nx, p.y):
            break
        p.x = nx
    game.msg('The gust shoves you along the chain.', 'bad')
    game.compute_fov()


def edge(game, x, y):
    from . import events as EV
    EV.ask(game, 'skyseat', 'The edge', 'Nothing but wind below, and the sea a long way down. A fall like that may '
           'kill you.', [('Jump', 'jump'), ('Step back', 'bye')], cell=(x, y))
    return 0


def fall(game, x, y):
    """Off the chain or through the glass: down into the sea. It hurts by the height; the boat fishes you out."""
    m = game.maps[CHAIN]
    p = game.player
    s = game.stats()
    k = max(.15, 1 - y / m.h)
    dmg = round(s['max_life'] * (.15 + .45 * k) + random.randint(0, 4))
    game.cur = CHAIN
    p.x, p.y = m.entry
    game.shake()
    game.msg('You fall a long way, and hit the sea like a wall. The skipper hauls you out by the collar.', 'bad')
    game.hurt(dmg, 'a fall from the Sky-Seat')
    game.compute_fov()


def stairs(game, t, d):
    """The chain's top stair into the city; the first floor's way back down to the chain."""
    m = game.map
    if getattr(m, 'skychain', False):
        if t == D.UP and d != 'down':
            enter_floor(game, 1)
            return 1
        return None
    if getattr(m, 'did', None) == 'skyseat' and m.depth == 1 and t == D.UP and d != 'down':
        to_chain(game, top=True)
        game.msg('You climb back down onto the underside, into the wind.', 'info')
        return 1
    return None


def bump(game, x, y, t):
    m = game.map
    if t == D.RAFT and getattr(m, 'skychain', False):
        from . import events as EV
        EV.ask(game, 'skyseat', 'The boat', '"Back?" the skipper asks, and does not look at the chain.',
               [('Back to the mainland', 'home'), ('Not yet', 'bye')])
        return 0
    if t == D.BEACON:
        m.set(x, y, D.LITBEACON)
        m.lights = getattr(m, 'lights', []) + [(x, y, (255, 216, 96), 9)]
        sh(game.world)['beacons'].add(m.depth)
        game.msg(f'You light the beacon. Its fire is cold and gold, and the dead on {FLOORS[m.depth - 1]} lie still.',
                 'unique')
        from . import chronicle as CH
        CH.deed(game, f'A beacon lit in {FLOORS[m.depth - 1]}', f'You lit the beacon of {FLOORS[m.depth - 1]} in the '
                'Sky-Seat.')
        return 1
    if t == D.LITBEACON:
        game.msg('The beacon burns, cold and gold. This floor stays calm.', 'info')
        return 0
    return None


# ------------------------------------------------------------------ the five floors
def on_level(game, m, depth):
    """Each floor its name and its beacon; on the last, the throne and the Hollow King, lighter for every relic."""
    m.name = f'The Sky-Seat: {FLOORS[depth - 1]}'
    if not m.__dict__.get('beacon'):
        from . import worldgen as W
        c = W.rand_free(game, m, lambda t: t == D.FLOOR)
        if c:
            m.set(*c, D.BEACON)
            m.beacon = c
    game.msg(f'{FLOORS[depth - 1]}.', 'unique')
    if depth != len(FLOORS):
        return
    king = next((o for o in m.mons if o.k == 'hollow_king'), None)
    if king is None or king.__dict__.get('kit_over'):
        return
    s = sh(game.world)
    if s.get('night'):
        king.maxhp = king.hp = round(king.maxhp * 1.3)          # the Long Night: harder, never unbeatable
    n = min(3, len(keys(game)))
    from . import bosses as BS
    kt = copy.deepcopy(BS.KITS['hollow_king'])
    for i in range(n):
        ph = kt['phases'][i]
        ph['beat'] = ph['beat'].replace('Z', '')
        ph['cards'].pop('Z', None)
        ph.pop('trick', None)
        game.msg(LIGHT_TEXT[i], 'gold')
    king.kit_over = kt
    king.light = n
    near = [c for c in ((king.x + dx, king.y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)) if m.tile(*c) == D.FLOOR
            and (c[0], c[1]) != (king.x, king.y)]
    if near:
        m.set(*near[0], D.THRONE)


def in_seat(game):
    m = game.map
    return getattr(m, 'skychain', False) or getattr(m, 'did', None) == 'skyseat'


def binds(game):
    """Where the dead are bound, a body rises as a shade: his city, the barrows, the crypts, the Rift."""
    m = game.map
    if in_seat(game) or getattr(m, 'rift', False) or getattr(m, 'barrow', None):
        return True
    dg = game.world.dungeons.get(getattr(m, 'did', None)) if m.kind == 'dungeon' else None
    return bool(dg and dg.tag in ('crypt', 'barrow'))


def shade(game, key, corpse):
    """Your body rises as your shade: an echo of you, weaker, that does not heal; beat it for your backpack."""
    from .entities import make_monster
    p = game.player
    m = game.maps[key]
    o = make_monster(game, 'shade', corpse.x, corpse.y, max(1, p.lvl - 2))
    o.name = f'The shade of {p.name}'
    o.maxhp = o.hp = max(o.maxhp, game.stats()['max_life'] * 2 // 3)
    o.my_body = corpse
    o.regen = False
    o.awake = False
    m.mons.append(o)
    if corpse in m.items:
        m.items.remove(corpse)
    return o


def more_dead(game):
    """You fell in his city: he sends a few new bound dead to the floors whose beacon is not lit."""
    from .entities import make_monster
    from . import worldgen as W
    s = sh(game.world)
    for d in range(1, len(FLOORS) + 1):
        m = game.maps.get(f'skyseat:{d}')
        if m is None or d in s['beacons']:
            continue
        for _ in range(random.randint(2, 3)):
            c = W.rand_free(game, m, lambda t: t == D.FLOOR)
            if c and not m.mon_at(*c):
                m.mons.append(make_monster(game, 'bound_dead', c[0], c[1], 16 + d))


def on_kill(game, mon):
    body = mon.__dict__.get('my_body')
    if body is not None:
        body.x, body.y = mon.x, mon.y
        game.map.items.append(body)
        game.msg('Your shade comes apart like smoke, and leaves your backpack where it stood.', 'good')
        return True
    if mon.k == 'hollow_king':
        won(game)
        return True
    return False


# ------------------------------------------------------------------ the ends
def long_night(world):
    s = sh(world)
    return bool(s and s.get('night') and not s.get('won'))


def night_falls(game):
    """Three seals broken: the Long Night. The sky goes dark, his coast spreads, the cities shut their gates, the
    prices climb. He can still be beaten."""
    game.msg('The third seal breaks. The sky goes dark at noon and stays dark: the Long Night has come. Out over '
             'the sea the Sky-Seat burns like a second moon.', 'unique')
    from . import news as NW
    for s_ in game.world.settlements:
        if s_.is_city:
            NW.post(game, 'danger', f'{s_.name} has shut its gates at noon, and doubled the watch on the walls.',
                    s_.x, s_.y)
    from . import chronicle as CH
    CH.add(game, 'The Shadow', 'The third seal broke and the Long Night came: a dark sky, a growing coast, cities '
           'behind their walls.', 'seen', where='everywhere', key='sk:night', title='The Long Night')


def price_mult(world):
    return 1.2 if long_night(world) else 1.0


def won(game):
    """You won: one closing screen, then a world that heals."""
    w = game.world
    s = sh(w)
    s['won'] = True
    s['night'] = False
    s['wake'] = 0.0
    from . import chronicle as CH
    p = game.player
    CH.deed(game, 'The Hollow King destroyed', f'{p.name} climbed the chain of the Sky-Seat and destroyed the Hollow '
            'King on his throne.')
    CH.add(game, 'The Shadow', f'The Hollow King fell on his throne in the Sky-Seat, by the hand of {p.name}.', 'seen',
           where='the Sky-Seat', key='sk:won', title='The fall of the Hollow King')
    from . import evils as EVL
    EVL.compute_taint(game)
    from . import realms as RL
    R = getattr(w, 'realm', None)
    if R is not None and s.get('held'):
        rid = next(iter(s['held']))
        s['held'].clear()
        RL.refresh(w)
        rg = w.regions[rid]
        RL.news(game, 'With the Hollow King gone the lost baronies are free, and every baron in the empire has a '
                      'claim on them.', rg.cx, rg.cy, 'The Shadow')
    game.flags['saved'] = True
    game.request = ('win',)


def register():
    from . import entities as EN
    from . import events as EV
    EV.RESOLVERS['skyseat'] = r_sky
    for k in ('bound_dead', 'storm_spirit', 'wraith', 'gargoyle', 'chain_warden', 'animated_armour', 'skel_mage',
              'gloomwing'):
        if k in D.MONSTERS and 'skyseat' not in D.MONSTERS[k]['tags'].split():
            D.MONSTERS[k]['tags'] += ' skyseat'
    del EN


register()
