"""Faction politics: reputation, hostility, warbands marching on enemy strongholds, sieges."""
import random

from . import data as D
from .wanderers import Wanderer, wanderer_at
from .world import dijkstra_path, flip_region
from .worldgen import cheb

HOSTILE_AT = -25


def is_hostile(game, f):
    if f is None:
        return False
    if f == 'cult':
        return True
    return game.player.rep.get(f, 0) <= HOSTILE_AT


def standing(rep):
    if rep <= -60:
        return 'Hated'
    if rep <= HOSTILE_AT:
        return 'Hostile'
    if rep < 10:
        return 'Neutral'
    if rep < 40:
        return 'Friendly'
    if rep < 75:
        return 'Honored'
    return 'Exalted'


def change_rep(game, f, amount, quiet=False):
    if f is None or f == 'cult':
        return
    p = game.player
    before = is_hostile(game, f)
    p.rep[f] = max(-100, min(100, p.rep[f] + amount))
    after = is_hostile(game, f)
    if not quiet and amount:
        game.msg(f"{D.FACTIONS[f]['short']} reputation {'+' if amount > 0 else ''}{amount} ({standing(p.rep[f])}).",
                 'good' if amount > 0 else 'bad')
    if before != after:
        game.msg(f"{D.FACTIONS[f]['name']} now {'counts you as an enemy' if after else 'no longer counts you as an enemy'}.",
                 'bad' if after else 'good')
        refresh_hostility(game)


def on_kill(game, mon):
    f = mon.faction
    if not f:
        return
    change_rep(game, f, -2, quiet=True)
    for e in D.FACTIONS[f]['enemies']:
        if e != 'cult':
            change_rep(game, e, 1, quiet=True)


def refresh_hostility(game):
    for wd in game.world.wanderers:
        if wd.kind in ('warband', 'patrol'):
            wd.hostile = is_hostile(game, wd.faction)


def can_enter(game, s):
    f = s.faction
    if f == 'cult':
        return False, f'{s.name} is held by the Cult of the Undying. The dead guard its gates.'
    rep = game.player.rep.get(f, 0)
    if f == 'blackhand' and rep < -60:
        return False, f'The Black Hand holds {s.name}, and they know your face. The gates stay shut.'
    if f != 'blackhand' and rep <= HOSTILE_AT:
        return False, f"The guards of {s.name} ({D.FACTIONS[f]['short']}) turn you away."
    return True, ''


# ------------------------------------------------------------------ warbands
WARBAND_GLYPH = {'crown': 'K', 'league': 'M', 'circle': 'D', 'blackhand': 'R', 'cult': 'U'}


def launch(game, f):
    w = game.world
    own = [h for h in w.holds if h.faction == f and h.garrison >= 8]
    if not own:
        return
    src = random.choice(own)
    enemies = D.FACTIONS[f]['enemies']
    targets = [h for h in w.holds if h.faction in enemies and cheb(h.x, h.y, src.x, src.y) <= 90]
    if not targets:
        return
    tgt = min(targets, key=lambda h: cheb(h.x, h.y, src.x, src.y) + random.randint(0, 20))
    over = game.maps['over']
    path = dijkstra_path(over, (src.x, src.y), (tgt.x, tgt.y), lambda t: D.TILES[t].cost if D.TILES[t].walk else None)
    if not path:
        return
    strength = random.randint(8, 14) + (4 if src.kind == 'castle' else 0)
    src.garrison -= strength // 2
    wd = Wanderer(game.new_id(), 'warband', src.x, src.y)
    wd.faction = f
    wd.ch, wd.fg = WARBAND_GLYPH[f], D.FACTIONS[f]['fg']
    wd.name = f"A {D.FACTIONS[f]['short']} warband"
    wd.strength = strength
    wd.target_hold = tgt.id
    wd.path = path
    wd.speed = 12
    troops = D.FACTIONS[f]['troops']
    n = min(6, 2 + strength // 4)
    lvl = max(3, w.region_at(tgt.x, tgt.y).danger + 1)
    wd.group = dict(keys=[random.choice(troops) for _ in range(n)], lvl=lvl, elite=1 if strength > 14 else 0, leader=None, faction=f)
    wd.hostile = is_hostile(game, f)
    w.wanderers.append(wd)
    if game.cur == 'over' and cheb(src.x, src.y, game.player.x, game.player.y) < 25:
        game.msg(f"News: {D.FACTIONS[f]['short']} troops march out of {src.title}.", 'info')


def siege(game, wd):
    w = game.world
    h = w.holds[wd.target_hold]
    if wd in w.wanderers:
        w.wanderers.remove(wd)
    if h.faction == wd.faction:
        h.garrison = min(h.max_garrison, h.garrison + wd.strength // 2)
        return
    if wd.faction not in D.FACTIONS[h.faction]['enemies'] and h.faction not in D.FACTIONS[wd.faction]['enemies']:
        return
    atk = wd.strength * random.uniform(.7, 1.35)
    attacker, defender = D.FACTIONS[wd.faction], D.FACTIONS[h.faction]
    if atk > h.garrison:
        old_title = h.title
        capture(game, h, wd.faction, wd.strength // 2 + 2)
        game.msg(f"News: {attacker['name']} has taken {old_title}! It is now {h.title}.", 'info')
    else:
        h.garrison = max(2, h.garrison - wd.strength // 2)
        game.msg(f"News: {h.title} held against an attack by {attacker['short']} troops.", 'info')


def capture(game, h, faction, garrison):
    w = game.world
    old = h.faction
    h.faction = faction
    h.garrison = max(2, min(h.max_garrison, garrison))
    h.board = []
    if game.cur == h.map_key:
        game.maps[h.map_key].stale = True
    else:
        game.maps.pop(h.map_key, None)
    if not any(o.faction == old and o.region == h.region for o in w.holds):
        flip_region(game, h.region, faction)
        for st in w.settlements:
            if st.region == h.region and st.id != 0 and not st.event:
                st.event = ('war', random.randint(4, 7))
                st.market['arms'][1] = D.EVENTS['war']['target']
    refresh_hostility(game)


def tick_fights(game):
    """Warbands that meet an enemy fight it out; raiders plunder caravans."""
    w = game.world
    bands = [x for x in w.wanderers if x.kind == 'warband']
    for a in bands:
        if a not in w.wanderers:
            continue
        for b in bands:
            if b is a or b not in w.wanderers or a not in w.wanderers:
                continue
            if cheb(a.x, a.y, b.x, b.y) > 1 or b.faction not in D.FACTIONS[a.faction]['enemies']:
                continue
            win, lose = (a, b) if a.strength * random.uniform(.7, 1.3) >= b.strength * random.uniform(.7, 1.3) else (b, a)
            w.wanderers.remove(lose)
            win.strength = max(3, win.strength - lose.strength // 2)
            if game.cur == 'over' and (game.visible(a.x, a.y) or game.visible(b.x, b.y)):
                game.msg(f"{win.name} routs {lose.name.lower()} in a bloody clash.", 'info')
        if a in w.wanderers and a.faction in ('blackhand', 'cult'):
            for c in [x for x in w.wanderers if x.kind == 'caravan' and cheb(x.x, x.y, a.x, a.y) <= 1]:
                if random.random() < .4:
                    w.wanderers.remove(c)


def step_warband(game, wd):
    p = game.player
    on_over = game.cur == 'over'
    if wd.hostile and on_over and wd.cooldown == 0 and cheb(wd.x, wd.y, p.x, p.y) <= 6 and game.visible(wd.x, wd.y):
        from .wanderers import greedy_step
        greedy_step(game, wd, p.x, p.y)
        return
    if wd.path_i < len(wd.path):
        nx, ny = wd.path[wd.path_i]
        if on_over and (nx, ny) == (p.x, p.y):
            return
        if not wanderer_at(game, nx, ny) or random.random() < .5:
            wd.x, wd.y = nx, ny
            wd.path_i += 1
        return
    siege(game, wd)


def daily(game):
    w = game.world
    for h in w.holds:
        h.garrison = min(h.max_garrison, h.garrison + 1)
    for f in D.FACTION_ORDER:
        if sum(1 for x in w.wanderers if x.kind == 'warband' and x.faction == f) >= 2:
            continue
        if random.random() < (.12 if f == 'cult' else .2):
            launch(game, f)
    refresh_hostility(game)
