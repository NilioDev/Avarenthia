"""Boss fights, what was left (round 53): arenas dressed for the place they stand in, ways out other than the rotten
wall, the place that wakes or falls in behind you once its bosses fall, fights won another way (hold out, rescue,
break it), and bosses for the big one and the relic.

The kit and its arena live in `bosses.py` (`build` makes the room, `furnish` sets the kit's own things); this module
adds to them. The job bosses of `bossmaker.py` fight on battle maps, where a fight may end without the boss dying."""
import random

from . import data as D
from .worldgen import cheb, free_around

D8 = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

# ------------------------------------------------------------------ the arena fits the place
STYLE_LINE = {
    'nave': 'The fight is in the nave: pillars to put between you and the blow.',
    'crypt': 'The fight is among the tombs: statues of the dead stand in rows.',
    'forge': 'The fight is in a forge: a pool of molten metal glows in the floor.',
    'lake': 'The fight is by an underground lake: black water and a muddy shore.',
    'glade': 'The fight is in the open, among the trees.',
    'throne': 'The fight is in a lord\'s hall: the high seat, the columns of state.',
    'hall': 'The fight is in a great hall with pillars.',
}


def style_of(m):
    s = ' '.join(str(x) for x in (getattr(m, 'delve', ''), getattr(m, 'place', ''), getattr(m, 'dtag', ''),
                                  getattr(m, 'style', ''), getattr(m, 'name', ''))).lower()
    for words, st in ((('temple', 'abbey', 'monastery', 'chapel', 'shrine'), 'nave'),
                      (('crypt', 'catacomb', 'vault', 'barrow', 'tomb', 'bonechapel'), 'crypt'),
                      (('fallenhold', 'forge', 'deep', 'dwarf'), 'forge'),
                      (('fey', 'glade', 'outdoor', 'wild'), 'glade'),
                      (('castle', 'fort', 'manor', 'hold', 'steading', 'keep'), 'throne'),
                      (('cave', 'grotto', 'tide', 'icecave', 'lair', 'den', 'mine', 'warren', 'antnest'), 'lake')):
        if any(w in s for w in words):
            return st
    return 'hall'


def _joined(m, a, b, ar):
    from .worldgen import bfs
    dist = bfs(m, a[0], a[1], lambda t: D.TILES[t].walk or D.TILES[t].door or t in (D.VEIL, D.SEALED))
    return dist[b[1] * m.w + b[0]] >= 0


def dress(game, m, boss, ar):
    """Set the room for the place: pillars in a nave, statues among the tombs, a pool of metal in a forge, a lake's
    edge in a cave, trees in a glade. Only on bare floor, and never so that the way from the door to the boss shuts."""
    from . import bosses as BS
    st = style_of(m)
    ar['style'] = st
    if BS.kit(boss).get('things'):
        return                                              # the kit dresses its own room
    room = set(map(tuple, ar['cells']))
    inner = [c for c in ar['cells'] if all((c[0] + a, c[1] + b) in room for a, b in D8) and m.tile(*c) == D.FLOOR
             and cheb(*c, boss.x, boss.y) >= 2 and min(cheb(*c, *g) for g in ar['gates']) > 2]
    if not inner:
        return
    xs, ys = [c[0] for c in inner], [c[1] for c in inner]
    cx, cy = (min(xs) + max(xs)) // 2, (min(ys) + max(ys)) // 2
    put = []
    if st in ('nave', 'throne', 'hall'):
        wide = max(xs) - min(xs) >= max(ys) - min(ys)
        for c in inner:
            off = (c[1] - cy) if wide else (c[0] - cx)
            along = c[0] if wide else c[1]
            if abs(off) == 2 and along % 3 == 0:
                put.append((c, D.PILLAR))
        if st == 'throne':
            seat = min(inner, key=lambda c: -cheb(*c, *ar['gates'][0]))
            put.append((seat, D.HIGHSEAT))
    elif st == 'crypt':
        for c in inner:
            if (c[0] + c[1]) % 4 == 0 and c[0] % 2 == 0:
                put.append((c, D.STATUE))
    elif st == 'forge':
        corner = max(inner, key=lambda c: cheb(*c, boss.x, boss.y))
        put += [(c, D.MOLTEN) for c in inner if cheb(*c, *corner) <= 1]
        put += [(c, D.ANVIL) for c in random.sample(inner, min(2, len(inner)))]
    elif st == 'lake':
        corner = max(inner, key=lambda c: cheb(*c, boss.x, boss.y))
        for c in inner:
            dd = cheb(*c, *corner)
            put.append((c, D.WATER if dd <= 1 else D.SHALLOW if dd == 2 else None))
    elif st == 'glade':
        for c in random.sample(inner, min(len(inner), max(3, len(inner) // 25))):
            put.append((c, D.TREE))
    put = [(c, t) for c, t in put if t is not None]
    was = {c: m.tile(*c) for c, _t in put}
    for c, t in put:
        if not m.mon_at(*c) and (game.player.x, game.player.y) != c:
            m.set(c[0], c[1], t)
    if not _joined(m, ar['gates'][0], (boss.x, boss.y), ar):
        for c, t in was.items():
            m.set(c[0], c[1], t)


def told_style(game, ar):
    line = STYLE_LINE.get(ar.get('style'))
    if line and not ar.get('style_told'):
        ar['style_told'] = True
        game.msg(line, 'info')


# ------------------------------------------------------------------ the ways out
def way_out(game, m, ar):
    """One hard way out of a shut room: the rotten wall (bosses.build), or a rope up through the roof, or a hole down
    to the level below (not on the bottom)."""
    dg = game.world.dungeons.get(getattr(m, 'did', None))
    ways = ['rotten', 'rope']
    if dg is not None and getattr(m, 'depth', 0) and m.depth < dg.depth:
        ways.append('drop')
    way = random.choice(ways)
    if way == 'rotten' and ar.get('rotten'):
        ar['way'] = 'rotten'
        return
    room = set(map(tuple, ar['cells']))
    edge = [c for c in ar['cells'] if m.tile(*c) == D.FLOOR and not m.mon_at(*c)
            and any((c[0] + a, c[1] + b) not in room for a, b in D8)
            and min(cheb(*c, *g) for g in ar['gates']) >= 4]
    if way == 'rotten' or not edge:
        ar['way'] = 'rotten' if ar.get('rotten') else None
        return
    c = random.choice(edge)
    m.set(c[0], c[1], D.ROPEDOWN if way == 'rope' else D.HOLE)
    boss = next((o for o in m.mons if o.id == ar['boss']), None)
    if boss is not None and not _joined(m, ar['gates'][0], (boss.x, boss.y), ar):
        m.set(c[0], c[1], D.FLOOR)
        ar['way'] = 'rotten' if ar.get('rotten') else None
        return
    if ar.get('rotten'):                                     # the rotten wall stays wall then
        m.set(ar['rotten'][0], ar['rotten'][1], D.WALL)
        ar['rotten'] = None
    ar['way'], ar['way_cell'] = way, c


def bump(game, x, y, t):
    """The rope up and the hole down of a shut room."""
    m = game.map
    ar = m.__dict__.get('arena')
    if not ar or tuple(ar.get('way_cell') or ()) != (x, y) or t not in (D.ROPEDOWN, D.HOLE):
        return None
    if not ar['sealed']:
        game.msg('A rope hangs from a hole in the roof.' if t == D.ROPEDOWN else
                 'A hole in the floor. Far below, another level.', 'info')
        return 0
    if t == D.ROPEDOWN:
        from .worldgen import bfs
        ups = [i for i, tt in enumerate(m.t) if tt == D.UP]
        if not ups:
            return 0
        dist = bfs(m, ups[0] % m.w, ups[0] // m.w, lambda tt: D.TILES[tt].walk or D.TILES[tt].door)
        room = set(map(tuple, ar['cells']))
        out = [(i % m.w, i // m.w) for i, dd in enumerate(dist) if dd >= 0 and (i % m.w, i // m.w) not in room
               and not m.mon_at(i % m.w, i // m.w)]
        if not out:
            return 0
        p = game.player
        p.x, p.y = min(out, key=lambda c: cheb(*c, x, y))
        game.msg('You climb the rope through the hole in the roof and drop down on the far side of the wall. You are '
                 'out.', 'good')
        game.compute_fov()
        return 3
    from .worldgen import rand_free
    game.msg('You lower yourself through the hole and let go. You land hard on the level below.', 'bad')
    game.hurt(max(2, round(game.stats()['max_life'] * .08)), 'a drop through the floor')
    if game.dead:
        return 1
    game.enter_dungeon(m.did, m.depth + 1, 'up')
    c = rand_free(game, game.map, lambda tt: tt == D.FLOOR)
    if c:
        game.player.x, game.player.y = c
    game.compute_fov()
    return 1


# ------------------------------------------------------------------ the place wakes or falls in behind you
def felled(game, mon):
    """A boss fell in a place: count it there."""
    dg = game.world.dungeons.get(getattr(game.map, 'did', None))
    if dg is None:
        return
    dg.bosses_felled = getattr(dg, 'bosses_felled', 0) + 1
    if mon.k == getattr(dg, 'boss', None):
        dg.boss_felled = True


def leaving(game, dg):
    """Out into the daylight from a place whose boss fell (or that lost two of its bosses): it wakes or falls in."""
    if dg is None or getattr(dg, 'reacted', False) or getattr(dg, 'varnish', False):
        return
    if not (getattr(dg, 'boss_felled', False) or getattr(dg, 'bosses_felled', 0) >= 2):
        return
    dg.reacted = True
    for k in [k for k in game.maps if k.startswith(dg.id + ':')]:
        del game.maps[k]
    if getattr(dg, 'boss_felled', False):
        dg.boss = None                                       # it is dead, made again it is not there
    if random.random() < .5:
        dg.closed = True
        game.msg(f'Behind you the ground shudders. With a long roar {dg.name} falls in on itself, and dust rolls out '
                 'of the way in. Nobody will go down there again.', 'unique')
    else:
        dg.base += 2
        game.msg(f'Behind you, deep in {dg.name}, drums start up, and horns answer them. The place is awake now, and '
                 'more will come to it.', 'unique')
    from . import chronicle as CH
    CH.seen_place(game, f'after:{dg.id}', dg.name, f'{dg.name} ' + ('fell in after its master fell.' if
                  getattr(dg, 'closed', False) else 'woke after its master fell.'), (dg.x, dg.y))


def closed(game, dg):
    if getattr(dg, 'closed', False):
        game.msg(f'The way into {dg.name} has fallen in. There is nothing to go down into any more.', 'info')
        return True
    return False


# ------------------------------------------------------------------ fights won another way (job bosses)
WIN_FOR = {'shrine': 'break', 'boats': 'hold', 'missing': 'rescue'}
HOLD_TURNS = 30


def other_win(game, m, wild, boss):
    """Some job fights are won without the boss dying: hold out until it breaks off, free the one it holds, or
    break the altar it draws on."""
    how = WIN_FOR.get(m.kind)
    if how is None or random.random() < .5:
        return
    wild.win = dict(how=how, boss=boss.id, start=game.turn)
    p = game.player
    if how == 'hold':
        game.msg(f'You cannot hope to kill it. Hold out until {boss.name} has had enough.', 'info')
    elif how == 'break':
        spots = [c for c in free_around(game, wild, boss.x, boss.y, 3) if cheb(*c, boss.x, boss.y) >= 2]
        if spots:
            c = spots[0]
            wild.set(c[0], c[1], D.ALTAR)
            wild.win['altar'], wild.win['hits'] = c, 0
            game.msg(f'{boss.name} draws strength from a black altar. Break it and the power is gone.', 'info')
        else:
            del wild.win
    elif how == 'rescue':
        far = max(free_around(game, wild, boss.x, boss.y, 5) or [(boss.x, boss.y)], key=lambda c: cheb(*c, p.x, p.y))
        from .entities import make_npc
        who = m.data.get('person') or m.data.get('missing') or 'The captive'
        n = make_npc(game, f'{who}, bound', 'captive', '#e8d8a0', far[0], far[1], True)
        n.home_pos = n.work_pos = far
        wild.mons.append(n)
        game.msg(f'There they are, bound, behind {boss.name}. Get to them and cut them free.', 'info')


def won(game, wild, text):
    wild.won_other = True
    game.banner = ['WON', None]
    game.msg(text, 'good')


def turn(game):
    """Each turn on a battle map with another way to win."""
    wild = game.map
    w = getattr(wild, 'win', None)
    if not w or getattr(wild, 'won_other', False):
        return
    boss = next((o for o in wild.mons if o.id == w['boss']), None)
    if w['how'] == 'hold' and game.turn - w['start'] >= HOLD_TURNS:
        for o in [o for o in wild.mons if not o.is_npc]:
            wild.mons.remove(o)
        won(game, wild, f'{boss.name if boss else "It"} breaks off and is gone, and the rest go with it. You held.')


def bump_altar(game, x, y):
    wild = game.map
    w = getattr(wild, 'win', None)
    if not w or w.get('how') != 'break' or tuple(w.get('altar') or ()) != (x, y):
        return None
    w['hits'] += 1
    if w['hits'] < 4:
        game.msg(f'You hammer at the black altar. It cracks. ({w["hits"]}/4)', 'info')
        return 1
    wild.set(x, y, D.RUBBLE)
    boss = next((o for o in wild.mons if o.id == w['boss']), None)
    if boss is not None:
        boss.hp = 0
        game.kill(boss)
    won(game, wild, 'The altar breaks in two, and with it the power that held the thing together.')
    return 1


def talk_captive(game, npc):
    wild = game.map
    if npc.role != 'captive' or not getattr(wild, 'win', None):
        return False                                          # a theme room's captive is freed at the bars
    wild.mons.remove(npc)
    won(game, wild, f'You cut {npc.name.split(",")[0]} free. They run for it, and you can go too: that is what you came '
                    'for.')
    return True


# ------------------------------------------------------------------ bosses for the big one and the relic
def bigone_fight(game, m):
    """The big one does not come in quietly: it is a fight in the shallows."""
    from . import jobs as JB
    from . import bossmaker as BM
    spec = m.data.get('bspec')
    if not spec:
        return False
    fish = m.data['fish'].split(',')[0]
    JB.fight(game, m, [spec['mon']], spec['lvl'], intro=f'The line goes slack, and then the water bursts open: '
             f'{fish} comes up out of the river at you!', then='bigone_won')
    wild = game.fight_map()
    boss = next((o for o in wild.mons if not o.is_npc), None) if wild else None
    if boss is not None:
        boss.name = fish[0].upper() + fish[1:]
    return True


def won_bigone(game, m, won_):
    if not won_:
        game.msg('It is gone back into the deep water. It will bite again, another day.', 'info')
        return
    game.fishing_job = m.id
    from . import jobs as JB
    JB.landed(game)


def relic_guard(game, mp, m, at):
    """The relic's keeper: a boss of the job's own, beside it."""
    from . import bossmaker as BM
    from .entities import make_monster
    spec = m.data.get('bspec')
    if not spec:
        d = game.world.dungeons[m.data['dungeon']]
        spec = BM.draw(game, d.base + d.depth + 2, base=random.choice(['deadlord', 'cult', 'necromancer']))
        m.data['bspec'] = spec
    sp = free_around(game, mp, at[0], at[1], 2)
    if not sp or spec['mon'] not in D.MONSTERS:
        return None
    o = make_monster(game, spec['mon'], sp[0][0], sp[0][1], spec['lvl'])
    BM.apply(game, o, spec)
    mp.mons.append(o)
    return o
