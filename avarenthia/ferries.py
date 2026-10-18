"""Ferries in villages: where a lane crosses a broad or wild river, a raft on a rope instead of a bridge.

The raft (`▬`) lies at one end of the rope, by a landing on each bank; the ferryman keeps a hut by one landing.
By day you bump the raft, the rope or the ferryman, pay a few copper and step off on the other bank; at night he
is home and the raft is tied up. A ferry is m.ferries[k] = (landing_a, landing_b, raft_a, raft_b): the two
landings, and the two ends of the rope where the raft can lie.
"""
import random

from . import data as D
from .money import fmt

FARE, HIGH_FARE = 3, 8


def lay(m, ox, oy, across, lo, hi):
    """Rope across the water from lo to hi along `across` from (ox, oy), the raft at one end. Returns the landings."""
    flip = random.random() < .5
    if flip:
        lo, hi, across = -hi, -lo, (-across[0], -across[1])
    at = lambda j: (ox + across[0] * j, oy + across[1] * j)
    for j in range(lo, hi + 1):
        if m.inb(*at(j)):
            m.set(*at(j), D.ROPE)
    ra, rb = at(lo), at(hi)
    m.set(*ra, D.RAFT)
    la, lb = at(lo - 1), at(hi + 1)
    if not hasattr(m, 'ferries'):
        m.ferries = []
    m.ferries.append((la, lb, ra, rb))
    return la, lb


def settle(game, m, s, plots, names):
    """A hut for each ferryman beside his landing, and the ferryman in it: at the raft by day, home at night."""
    from . import towns as TV
    from .races import who
    for k, (la, lb, ra, rb) in enumerate(getattr(m, 'ferries', [])):
        hut = None
        for _ in range(200):
            pw, ph = random.randint(5, 6), 4
            hx = la[0] + random.randint(-pw - 3, 3)
            hy = la[1] + random.randint(-ph - 3, 3)
            pl = TV.Plot(hx, hy, pw, ph, 'home')
            if hx < 2 or hy < 2 or hx + pw > m.w - 2 or hy + ph > m.h - 2 or any(pl.overlaps(o, 1) for o in plots):
                continue
            cells = [(x, y) for y in range(hy - 1, hy + ph + 1) for x in range(hx - 1, hx + pw + 1)]
            if any(m.tile(*c) not in (D.GRASS, D.TREE) for c in cells):
                continue
            hut = pl
            break
        if hut:
            plots.append(hut)
            TV.build(m, hut)
            out = TV.place_door(m, hut, la[0], la[1])
            TV.carve_path(m, out, la)
            TV.furnish(m, hut)
        full = names.pop() if names else 'Bram Reed'
        gender, race = who(full)
        work = next(((la[0] + dx, la[1] + dy) for dx, dy in ((0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1))
                     if m.inb(la[0] + dx, la[1] + dy) and D.TILES[m.tile(la[0] + dx, la[1] + dy)].walk), la)
        home = TV.free_inside(m, hut) if hut else []
        n = TV.townsfolk(game, m, home[:1] or [work], work, [], role='ferryman', fg='#c8a878')
        n.name = f"{full.split()[0]} the {'Ferrywoman' if gender == 'female' else 'Ferryman'}"
        n.gender, n.race = gender, race
        n.job, n.ferry = 'ferryman', k


def ferry_at(m, x, y):
    """The ferry whose raft or rope is at (x, y)."""
    for k, (la, lb, ra, rb) in enumerate(getattr(m, 'ferries', [])):
        dx, dy = (rb[0] > ra[0]) - (rb[0] < ra[0]), (rb[1] > ra[1]) - (rb[1] < ra[1])
        n = max(abs(rb[0] - ra[0]), abs(rb[1] - ra[1]))
        if any((ra[0] + dx * j, ra[1] + dy * j) == (x, y) for j in range(n + 1)):
            return k
    return None


def ferryman(game, m, k):
    return next((o for o in m.mons if getattr(o, 'role', '') == 'ferryman' and getattr(o, 'ferry', -1) == k
                 and o.hp > 0), None)


def at_work(game, npc):
    from . import towns as TV
    return TV.DAY_START <= TV.hour(game) < TV.DAY_END


def fare(game):
    """More when the river is in spate on the world map."""
    from . import seasons as SE
    m = game.map
    om = game.maps['over']
    s = game.world.settlements[m.sid] if getattr(m, 'sid', None) is not None else None
    if s is None or not getattr(om, 'river', None):
        return FARE
    st = SE.Now(game)
    near = [(y * om.w + x) for y in range(s.y - 2, s.y + 3) for x in range(s.x - 2, s.x + 3)
            if om.inb(x, y) and om.river[y * om.w + x]]
    return HIGH_FARE if any(SE.spate(om, i, st) for i in near) else FARE


def bump(game, x, y):
    """Walking into the raft or its rope."""
    m = game.map
    k = ferry_at(m, x, y)
    if k is None:
        return 0
    offer(game, k)
    return 0


def talk(game, npc):
    k = getattr(npc, 'ferry', None)
    if k is None:
        game.say(npc, 'The river gives and the river takes.')
        return
    offer(game, k, npc)


def offer(game, k, npc=None):
    from . import events as EV
    m = game.map
    man = npc or ferryman(game, m, k)
    if man is None:
        game.msg('The raft is tied up, and there is no ferryman to pole it over.')
        return
    if not at_work(game, man):
        if npc:
            game.say(man, random.choice(['The raft is tied up for the night. Come back in the morning.',
                                         'Not in the dark. The river keeps no promises at night.']))
        else:
            game.msg('The raft is tied up for the night. The ferryman has gone home.')
        return
    f = fare(game)
    p = game.player
    opts = [(f'Cross ({fmt(f)})', 'cross') if p.gold >= f else (f'Cross ({fmt(f)})', None), ('Not now', 'bye')]
    EV.ask(game, 'townferry', man.name, ('"High water, so it costs more. Hold on to the rope." ' if f > FARE else
                                         random.choice(['"Over the water? Stand in the middle and keep still."',
                                                        '"Step on, step on. She is older than me but she floats."'])) +
           f'\n\nThe fare is {fmt(f)}.', opts, ferry=k, fare=f)


def r_cross(game, choice, ctx):
    if choice != 'cross':
        return
    m, p = game.map, game.player
    k = ctx['ferry']
    if k >= len(getattr(m, 'ferries', [])):
        return
    if p.gold < ctx['fare']:
        game.msg('You cannot pay the fare.', 'bad')
        return
    la, lb, ra, rb = m.ferries[k]
    near_a = max(abs(p.x - la[0]), abs(p.y - la[1])) <= max(abs(p.x - lb[0]), abs(p.y - lb[1]))
    to, raft = (lb, rb) if near_a else (la, ra)
    spot = next((c for c in [to] + [(to[0] + dx, to[1] + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
                 if m.inb(*c) and D.TILES[m.tile(*c)].walk and not m.mon_at(*c)), None)
    if spot is None:
        game.msg('Someone is standing on the far landing. The ferryman waits.')
        return
    p.gold -= ctx['fare']
    for c in (ra, rb):
        m.set(*c, D.ROPE)
    m.set(*raft, D.RAFT)
    p.x, p.y = spot
    game.msg('The ferryman hauls the raft over on its rope. You step off on the other bank.', 'info')
    game.end_turn(10)


def register():
    from . import events as EV
    EV.RESOLVERS['townferry'] = r_cross


register()
