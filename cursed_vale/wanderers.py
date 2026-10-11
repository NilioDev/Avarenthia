"""People and monsters that travel the overworld on their own: merchant caravans, city patrols,
bandit gangs and monster packs. They move in game time, so they keep travelling while you are
in a dungeon or a town."""
import random

from . import data as D
from .data import TOWN, CITY, ROAD
from .world import dijkstra_path
from .worldgen import D8, cheb

CARAVAN_FG = (222, 182, 98)
ESCORT_FG = (110, 226, 236)
PATROL_FG = (122, 156, 255)
BANDIT_FG = (226, 84, 72)


class Wanderer:
    def __init__(self, uid, kind, x, y):
        self.id, self.kind, self.x, self.y = uid, kind, x, y
        self.ch, self.fg, self.name = '?', (255, 255, 255), ''
        self.hostile = False
        self.speed = 10
        self.acc = 0
        self.path, self.path_i = [], 0
        self.origin = self.dest = None
        self.goods = None          # (good, qty)
        self.home = (x, y)
        self.group = None          # dict(keys=[...], lvl=n, elite=0|1|2, leader=name)
        self.mission = None
        self.cooldown = 0
        self.leg_start = (x, y)
        self.faction = None
        self.strength = 0
        self.target_hold = None

    def describe(self, game):
        w = game.world
        if self.kind == 'caravan':
            g, q = self.goods
            return f"A merchant caravan carrying {q} {D.GOODS[g]['name']} to {w.settlements[self.dest].name}."
        if self.kind == 'escort':
            return 'The caravan you are escorting.'
        if self.kind == 'patrol':
            return f'A patrol from {w.settlements[self.origin].name}' + (' (hostile to you).' if self.hostile else '.')
        if self.kind == 'warband':
            h = w.holds[self.target_hold]
            return (f"{self.strength} {D.FACTIONS[self.faction]['short']} troops marching on {h.title}"
                    + (', hostile to you.' if self.hostile else '.'))
        if self.kind == 'bounty':
            return f'{self.name}, the target of your bounty.'
        if self.kind == 'traveler':
            return f'{self.name}, on the way to {w.settlements[self.dest].name}.' + (' (has work)' if getattr(self, 'offer', None) else '')
        return self.name + '.'


def road_path(game, a, b):
    w = game.world
    key = (a, b)
    if key not in w.paths:
        sa, sb = w.settlements[a], w.settlements[b]
        p = dijkstra_path(game.maps['over'], (sa.x, sa.y), (sb.x, sb.y))
        w.paths[key] = p or []
        w.paths[(b, a)] = list(reversed(p[:-1])) + [(sa.x, sa.y)] if p else []
    return w.paths[key]


def passable(game, x, y, hostile):
    m = game.maps['over']
    if not m.inb(x, y):
        return False
    t = m.tile(x, y)
    return D.TILES[t].walk and not (hostile and t in (TOWN, CITY))


def wanderer_at(game, x, y):
    for wd in game.world.wanderers:
        if wd.x == x and wd.y == y:
            return wd
    return None


def greedy_step(game, wd, tx, ty, away=False):
    best, bd = None, None
    opts = D8[:]
    random.shuffle(opts)
    p = game.player
    for dx, dy in opts:
        nx, ny = wd.x + dx, wd.y + dy
        if not passable(game, nx, ny, wd.hostile) or wanderer_at(game, nx, ny):
            continue
        if game.cur == 'over' and (nx, ny) == (p.x, p.y):
            continue
        d = cheb(nx, ny, tx, ty)
        if away:
            d = -d
        if bd is None or d < bd:
            bd, best = d, (nx, ny)
    if best and (bd < (cheb(wd.x, wd.y, tx, ty) * (-1 if away else 1)) or random.random() < .3):
        wd.x, wd.y = best


def wander(game, wd, leash):
    if random.random() < .35:
        return
    if cheb(wd.x, wd.y, *wd.home) > leash:
        greedy_step(game, wd, *wd.home)
        return
    dx, dy = random.choice(D8)
    nx, ny = wd.x + dx, wd.y + dy
    if passable(game, nx, ny, wd.hostile) and not wanderer_at(game, nx, ny) and cheb(nx, ny, *wd.home) <= leash:
        if not (game.cur == 'over' and (nx, ny) == (game.player.x, game.player.y)):
            wd.x, wd.y = nx, ny


def step(game, wd):
    p = game.player
    on_over = game.cur == 'over'
    if wd.cooldown > 0:
        wd.cooldown -= 1
    if wd.kind == 'warband':
        from .war import step_warband
        step_warband(game, wd)
        return
    if wd.kind == 'patrol' and wd.hostile and on_over and wd.cooldown == 0 and cheb(wd.x, wd.y, p.x, p.y) <= 5 \
            and game.visible(wd.x, wd.y):
        greedy_step(game, wd, p.x, p.y)
        return
    if wd.kind in ('caravan', 'patrol', 'traveler'):
        if wd.kind == 'traveler' and getattr(wd, 'wait', 0) > 0:
            wd.wait -= 1
            return
        if wd.path_i < len(wd.path):
            nx, ny = wd.path[wd.path_i]
            if on_over and (nx, ny) == (p.x, p.y):
                return
            if not wanderer_at(game, nx, ny) or random.random() < .5:
                wd.x, wd.y = nx, ny
                wd.path_i += 1
            return
        if wd.kind == 'caravan':
            arrive(game, wd)
        elif wd.kind == 'traveler':
            if wd in game.world.wanderers:
                game.world.wanderers.remove(wd)
        else:
            if wd.path:
                end = wd.path[-1]
                wd.path = list(reversed(wd.path[:-1])) + [wd.leg_start]
                wd.leg_start = end
            wd.path_i = 0
        return
    # hostile groups
    chase = 7 if wd.kind == 'bandits' else 5 if wd.kind == 'bounty' else 6 + min(4, game.world.off_road(wd.x, wd.y) // 6)
    if on_over and wd.cooldown == 0 and cheb(wd.x, wd.y, p.x, p.y) <= chase and game.visible(wd.x, wd.y) \
            and game.maps['over'].tile(p.x, p.y) not in (TOWN, CITY):
        greedy_step(game, wd, p.x, p.y)
        return
    if wd.kind == 'bandits':
        prey = [c for c in game.world.wanderers if c.kind == 'caravan' and cheb(c.x, c.y, wd.x, wd.y) <= 5]
        if prey:
            c = min(prey, key=lambda c: cheb(c.x, c.y, wd.x, wd.y))
            greedy_step(game, wd, c.x, c.y)
            return
    wander(game, wd, 4 if wd.kind == 'bounty' else 8)


def arrive(game, wd):
    w = game.world
    if wd in w.wanderers:
        w.wanderers.remove(wd)
    s = w.settlements[wd.dest]
    g, q = wd.goods
    s.market[g][0] += q


def tick(game, turns):
    w = game.world
    for wd in w.wanderers[:]:
        if wd.kind == 'escort':
            continue
        wd.acc += turns
        while wd.acc >= wd.speed and wd in w.wanderers:
            wd.acc -= wd.speed
            step(game, wd)
    # bandits raid caravans, patrols chase off bandits
    for b in [x for x in w.wanderers if x.kind == 'bandits']:
        for c in [x for x in w.wanderers if x.kind == 'caravan' and cheb(x.x, x.y, b.x, b.y) <= 1]:
            if random.random() < .25:
                w.wanderers.remove(c)
                if game.cur == 'over' and (game.visible(c.x, c.y) or game.visible(b.x, b.y)):
                    game.msg(f'{b.name} plunder a caravan bound for {w.settlements[c.dest].name}!', 'bad')
                break
    from .war import tick_fights
    tick_fights(game)
    for pt in [x for x in w.wanderers if x.kind == 'patrol']:
        for b in [x for x in w.wanderers if x.kind == 'bandits' and cheb(x.x, x.y, pt.x, pt.y) <= 1]:
            if random.random() < .5 and b in w.wanderers:
                w.wanderers.remove(b)
                if game.cur == 'over' and game.visible(b.x, b.y):
                    game.msg(f'A patrol from {w.settlements[pt.origin].name} routs {b.name.lower()}.', 'info')


def hostile_adjacent(game):
    p = game.player
    for wd in game.world.wanderers:
        if wd.hostile and wd.cooldown == 0 and cheb(wd.x, wd.y, p.x, p.y) <= 1:
            return wd
    return None


# ------------------------------------------------------------------ spawning
def _far_cell(game, pred, min_player=12):
    m = game.maps['over']
    p = game.player
    w = game.world
    for _ in range(400):
        x, y = random.randint(1, m.w - 2), random.randint(1, m.h - 2)
        t = m.tile(x, y)
        if not pred(x, y, t):
            continue
        if game.cur == 'over' and cheb(x, y, p.x, p.y) < min_player:
            continue
        if any(cheb(x, y, s.x, s.y) < 6 for s in w.settlements):
            continue
        if wanderer_at(game, x, y):
            continue
        return x, y
    return None


def make_group(game, kind, x, y, lvl, keys, elite=0, leader=None):
    wd = Wanderer(game.new_id(), kind, x, y)
    wd.hostile = True
    wd.group = dict(keys=keys, lvl=lvl, elite=elite, leader=leader)
    if kind == 'bandits':
        wd.ch, wd.fg = '@', BANDIT_FG
        wd.name = f'{leader} and their gang' if leader else 'A bandit gang'
    else:
        t = D.MONSTERS[keys[0]]
        wd.ch, wd.fg = t['ch'], t['fg']
        if elite == 2:
            wd.fg = D.UNIQUE_FG
        elif elite == 1:
            wd.fg = D.CHAMPION_FG
        wd.name = f"{'Champion ' if elite == 1 else ''}{t['name']} pack" if len(keys) > 1 else t['name']
        if leader:
            wd.name = leader
    wd.speed = 9 if any(D.MONSTERS[k]['fast'] for k in keys) else 11
    return wd


def spawn_bandits(game):
    w = game.world
    c = _far_cell(game, lambda x, y, t: t == ROAD and w.region_at(x, y).danger >= 2)
    if not c:
        return
    lvl = w.region_at(*c).danger + 1
    keys = [random.choice(['bandit', 'bandit', 'brigand']) for _ in range(random.randint(2, 5))]
    elite = 2 if random.random() < .15 else 0
    leader = random.choice(D.BANDIT_LEADERS) if elite else None
    w.wanderers.append(make_group(game, 'bandits', c[0], c[1], lvl, keys, elite, leader))


def wild_pack(biome, lvl, night=False):
    """Monster keys for a wilderness pack: tougher kinds and bigger packs the more dangerous the spot."""
    pool = [k for k in D.BIOME_MONSTERS[biome] if D.MONSTERS[k]['min_l'] <= lvl + 1]
    if night:
        pool += [k for k in D.NIGHT_MONSTERS if D.MONSTERS[k]['min_l'] <= lvl + 1]
    pool = pool or D.BIOME_MONSTERS[biome][:1]
    k = random.choices(pool, [1 + D.MONSTERS[x]['min_l'] for x in pool])[0]
    big = D.MONSTERS[k]['hp'] >= 2
    n = random.randint(1, 2 + lvl // 6) if big else random.randint(2, 3 + lvl // 3)
    if random.random() < .3 and len(pool) > 1:
        k2 = random.choice(pool)
        return [k] * n + [k2] * random.randint(1, 2)
    return [k] * n


def spawn_monsters(game):
    w = game.world
    # far from the roads is where the beasts live
    c = None
    for _ in range(6):
        c = _far_cell(game, lambda x, y, t: t not in (ROAD, TOWN, CITY) and D.TILES[t].walk)
        if c and random.random() < min(1.0, .15 + w.off_road(*c) / 12):
            break
    if not c:
        return
    reg = w.region_at(*c)
    lvl = w.danger_at(*c) + random.randint(0, 1)
    keys = wild_pack(reg.biome, lvl)
    r = random.random()
    elite = 2 if r < .04 + lvl * .01 else 1 if r < .15 + lvl * .015 else 0
    wd = make_group(game, 'monsters', c[0], c[1], lvl, keys, elite)
    wd.home = c
    w.wanderers.append(wd)


def spawn_patrol(game, city):
    w = game.world
    villages = sorted((s for s in w.settlements if not s.is_city), key=lambda s: cheb(s.x, s.y, city.x, city.y))
    if not villages:
        return
    path = road_path(game, city.id, villages[0].id)
    from .war import is_hostile
    wd = Wanderer(game.new_id(), 'patrol', city.x, city.y)
    wd.ch, wd.fg, wd.name = '@', PATROL_FG, f'{city.name} patrol'
    wd.origin = city.id
    wd.faction = city.faction
    wd.fg = D.FACTIONS[city.faction]['fg']
    wd.hostile = is_hostile(game, city.faction)
    troops = D.FACTIONS[city.faction]['troops']
    wd.group = dict(keys=[random.choice(troops) for _ in range(4)], lvl=4, elite=0, leader=None, faction=city.faction)
    wd.path = list(path)
    wd.home = (city.x, city.y)
    w.wanderers.append(wd)


def spawn_caravan(game, s):
    w = game.world
    goods = [g for g in s.produce if s.market[g][0] > 30]
    if not goods:
        return
    g = random.choice(goods)
    buyers = [o for o in w.settlements if o.id != s.id and g in o.demand]
    if not buyers:
        buyers = [o for o in w.settlements if o.id != s.id and o.market[g][0] < o.market[g][1]]
    if not buyers:
        return
    dest = min(buyers, key=lambda o: o.market[g][0] + cheb(o.x, o.y, s.x, s.y) * .3)
    path = road_path(game, s.id, dest.id)
    if not path:
        return
    q = int(min(s.market[g][0] * .3, 40))
    s.market[g][0] -= q
    wd = Wanderer(game.new_id(), 'caravan', s.x, s.y)
    wd.ch, wd.fg, wd.name = '♦', CARAVAN_FG, 'A merchant caravan'
    wd.speed = 12
    wd.origin, wd.dest, wd.goods, wd.path = s.id, dest.id, (g, q), list(path)
    w.wanderers.append(wd)


def daily(game):
    w = game.world
    for s in w.settlements:
        if random.random() < (.45 if s.is_city else .3):
            spawn_caravan(game, s)
        if s.is_city and s.faction in ('crown', 'league') and not any(x.kind == 'patrol' and x.origin == s.id for x in w.wanderers):
            spawn_patrol(game, s)
    from .events import spawn_traveller
    for _ in range(4):
        if sum(1 for x in w.wanderers if x.kind == 'traveler') >= 10:
            break
        spawn_traveller(game)
    if sum(1 for x in w.wanderers if x.kind == 'bandits') < 7:
        spawn_bandits(game)
    while sum(1 for x in w.wanderers if x.kind == 'monsters') < 34:
        before = len(w.wanderers)
        spawn_monsters(game)
        if len(w.wanderers) == before:
            break


def populate(game):
    for _ in range(5):
        spawn_bandits(game)
    daily(game)
    for s in game.world.settlements:
        spawn_caravan(game, s)
