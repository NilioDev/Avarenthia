"""Jobs from the inn boards: courier, freight, bounty, escort and dungeon fetch."""
import math
import random

from . import data as D
from . import calendar as CAL
from .data import ROAD, TOWN, CITY, ENTR, FLOOR, UP
from .entities import Item
from .wanderers import Wanderer, make_group, road_path, ESCORT_FG
from .worldgen import cheb, free_around, rand_free, spawn_pack

MAX_ACTIVE = 5
REWARD_SCALE = 20             # a job pays about a fifth of what it used to: honest work, not a fortune
PARCELS = ['a sealed letter', 'a parcel of deeds', 'a small locked chest', 'a bundle of contracts', "a jeweller's pouch"]


class Mission:
    def __init__(self, mid, kind, giver):
        self.id, self.kind, self.giver = mid, kind, giver
        self.target = None
        self.title = ''
        self.desc = ''
        self.reward = 0
        self.rep = 0
        self.deadline = None
        self.state = 'offer'
        self.data = {}
        self.faction = None
        self.hold = None          # stronghold that gave the job, if any


def travel_days(plen):
    return max(1, math.ceil(plen * 9 / D.DAY_LEN))


def _other_settlement(game, s, lo, hi):
    w = game.world
    cands = []
    for o in w.settlements:
        if o.id == s.id:
            continue
        p = road_path(game, s.id, o.id)
        if p and lo <= len(p) <= hi:
            cands.append((o, len(p)))
    return random.choice(cands) if cands else (None, 0)


def make_offer(game, s, kinds=None, prey=None, max_rank=None):
    w = game.world
    want = kinds
    kinds = ['courier'] * 3 + ['freight'] * 3 + ['bounty'] * 2 + ['escort'] * 2 + ['hunt'] * 2
    if any(d.relic is None and not d.main for d in w.dungeons.values()):
        kinds += ['fetch'] * 2
    if want:
        kinds = [k for k in kinds if k in want] or ['courier']
    kind = random.choice(kinds)
    if kind == 'hunt':                  # a WANTED poster for a named enemy (named.py)
        from . import named as NM
        return NM.offer(game, s, prey, max_rank)
    m = Mission(game.new_id(), kind, s.id)
    if kind == 'courier':
        o, plen = _other_settlement(game, s, 15, 110)
        if not o:
            return None
        parcel = random.choice(PARCELS)
        m.target = o.id
        m.reward = round(25 + plen * 1.1 + w.region_at(o.x, o.y).danger * 8)
        m.deadline = game.day + travel_days(plen) + 2
        m.data = dict(parcel=parcel)
        m.title = f'Courier to {o.name}'
        m.desc = f'Deliver {parcel} to {o.name} ({plen} leagues by road) before {CAL.short(m.deadline)}.'
    elif kind == 'freight':
        goods = [g for g in s.produce if s.market[g][0] > 20]
        if not goods:
            return None
        g = random.choice(goods)
        buyers = [o for o in w.settlements if o.id != s.id and g in o.demand and road_path(game, s.id, o.id)]
        if not buyers:
            return None
        o = random.choice(buyers)
        plen = len(road_path(game, s.id, o.id))
        q = random.randint(6, 20) if D.GOODS[g]['w'] > 1 else random.randint(10, 30)
        m.target = o.id
        m.reward = round(20 + plen * .9 + q * D.GOODS[g]['w'] * 1.6)
        m.deadline = game.day + travel_days(plen) + 3
        m.data = dict(good=g, qty=q, w=q * D.GOODS[g]['w'])
        m.title = f"Haul {D.GOODS[g]['name']} to {o.name}"
        m.desc = (f"Carry {q} {D.GOODS[g]['name']} ({q * D.GOODS[g]['w']} cargo) to {o.name} ({plen} leagues) "
                  f'before {CAL.short(m.deadline)}. The goods are provided.')
    elif kind == 'bounty':
        reg_d = w.region_at(s.x, s.y).danger
        spot = None
        over = game.maps['over']
        for _ in range(300):
            x = s.x + random.randint(-36, 36)
            y = s.y + random.randint(-24, 24)
            if not over.inb(x, y) or cheb(x, y, s.x, s.y) < 12:
                continue
            t = over.tile(x, y)
            if not D.TILES[t].walk or t in (ROAD, TOWN, CITY, ENTR):
                continue
            if any(cheb(x, y, o.x, o.y) < 6 for o in w.settlements):
                continue
            spot = (x, y)
            break
        if not spot:
            return None
        reg = w.region_at(*spot)
        lvl = max(reg.danger, reg_d) + 2
        if random.random() < .5:
            leader = random.choice(D.BANDIT_LEADERS)
            keys = ['bandit'] + [random.choice(['bandit', 'brigand']) for _ in range(random.randint(2, 4))]
            what = f'the outlaw {leader}'
        else:
            k = random.choice(D.BIOME_MONSTERS[reg.biome])
            a, b, c = D.UNIQUE_NAME
            leader = random.choice(a) + random.choice(b) + ' ' + random.choice(c)
            keys = [k] * random.randint(2, 4)
            what = f"{leader}, a monstrous {D.MONSTERS[k]['name'].lower()}"
        m.reward = round(60 + lvl * 30)
        m.data = dict(spot=spot, lvl=lvl, keys=keys, leader=leader)
        m.title = f'Bounty: {leader}'
        m.desc = f'Hunt down {what}, last seen in {reg.name} to the {_dir(s, spot)}. Return to {s.name} for the reward.'
    elif kind == 'escort':
        o, plen = _other_settlement(game, s, 20, 110)
        if not o:
            return None
        path = road_path(game, s.id, o.id)
        danger = max(w.region_at(x, y).danger for x, y in path)
        m.target = o.id
        m.reward = round(50 + plen * 1.6 + danger * 12)
        m.deadline = game.day + travel_days(plen) + 3
        m.data = dict(hp=50 + 10 * danger, danger=danger)
        m.title = f'Escort a caravan to {o.name}'
        m.desc = (f'Guard a merchant caravan on the road to {o.name} ({plen} leagues) and arrive before {CAL.short(m.deadline)}. '
                  f'It follows you; keep it alive when bandits strike.')
    else:
        ds = [d for d in w.dungeons.values() if d.relic is None and not d.main]
        d = min(ds, key=lambda d: cheb(d.x, d.y, s.x, s.y))
        relic = random.choice(D.RELICS)
        m.reward = round(90 + (d.base + d.depth) * 25)
        m.data = dict(dungeon=d.id, relic=relic)
        m.title = f'Recover {relic}'
        m.desc = f'{relic[0].upper() + relic[1:]} lies at the bottom of {d.name}, to the {_dir(s, (d.x, d.y))}. A guardian watches over it. Bring it back to {s.name}.'
    m.rep = random.randint(5, 10)
    m.faction = s.faction
    m.reward *= REWARD_SCALE       # silver -> copper, kept modest: trade is how a fortune is made
    return m


def make_hold_offer(game, h):
    """Jobs from a castellan: war bounties, supply runs and assaults on enemy strongholds."""
    from .wanderers import road_path as _rp  # noqa: F401
    w = game.world
    f = h.faction
    enemies = [e for e in D.FACTIONS[f]['enemies']]
    kind = random.choice(['war_bounty', 'supply', 'supply', 'assault'])
    m = Mission(game.new_id(), kind, None)
    m.hold, m.faction = h.id, f
    fname = D.FACTIONS[f]['short']
    if kind == 'supply':
        g = random.choice(['arms', 'grain', 'tools', 'medicine', 'timber'])
        q = random.randint(8, 20)
        m.data = dict(good=g, qty=q)
        m.reward = round(D.GOODS[g]['base'] * q * 1.7 + 40)
        m.deadline = game.day + 8
        m.title = f"Supply {q} {D.GOODS[g]['name']} to {h.name}"
        m.desc = (f"The garrison of {h.title} needs {q} {D.GOODS[g]['name']}. Buy them wherever you can and bring them "
                  f'here before {CAL.short(m.deadline)}. Pays well above market price.')
    elif kind == 'assault':
        targets = [o for o in w.holds if o.faction in enemies and o.faction != f and cheb(o.x, o.y, h.x, h.y) <= 80]
        if not targets:
            return None
        t = min(targets, key=lambda o: cheb(o.x, o.y, h.x, h.y))
        m.data = dict(target_hold=t.id)
        m.reward = 300 + (150 if t.kind == 'castle' else 0)
        m.title = f'Take {t.title}'
        m.desc = (f"Storm {t.title} ({D.FACTIONS[t.faction]['short']}), to the {_dir(h, (t.x, t.y))}, and kill its commander. "
                  f'The {fname} will reward you richly.')
    else:
        foes = [e for e in enemies if e != 'cult'] or enemies
        foe = random.choice(foes)
        spot = None
        over = game.maps['over']
        for _ in range(300):
            x, y = h.x + random.randint(-30, 30), h.y + random.randint(-20, 20)
            if over.inb(x, y) and cheb(x, y, h.x, h.y) >= 10 and D.TILES[over.tile(x, y)].walk and over.tile(x, y) not in (ROAD, TOWN, CITY, ENTR):
                spot = (x, y)
                break
        if not spot:
            return None
        lvl = w.region_at(*spot).danger + 3
        leader = f"{random.choice(['Sir', 'Captain', 'Marshal', 'Warlord'])} {random.choice(D.BANDIT_LEADERS).split()[-1]}"
        troops = D.FACTIONS[foe]['troops']
        m.data = dict(spot=spot, lvl=lvl, keys=[random.choice(troops) for _ in range(random.randint(3, 5))], leader=leader, foe=foe)
        m.reward = 120 + lvl * 25
        m.title = f"Hunt {leader} of the {D.FACTIONS[foe]['short']}"
        m.desc = f"{leader} leads a {D.FACTIONS[foe]['short']} warband in {w.region_at(*spot).name}, to the {_dir(h, spot)}. End them."
    m.rep = random.randint(8, 14)
    # a supply run pays for the goods and a margin on top; the fighting pays modestly
    m.reward *= 100 if kind == 'supply' else REWARD_SCALE * 2
    return m


def refresh_hold_board(game, h):
    if h.board and game.day - h.board_day < 3:
        return
    h.board_day = game.day
    h.board = []
    for _ in range(12):
        if len(h.board) >= 3:
            break
        m = make_hold_offer(game, h)
        if m and not any(o.kind == m.kind == 'assault' for o in h.board):
            h.board.append(m)


def _dir(s, spot):
    from .engine import dir_name
    return dir_name(spot[0] - s.x, spot[1] - s.y)


def refresh_board(game, s):
    if s.board and game.day - s.board_day < 3:
        return
    s.board_day = game.day
    s.board = []
    tries = 0
    want = random.randint(3, 5)
    while len(s.board) < want and tries < 30:
        tries += 1
        m = make_offer(game, s)
        if m and not any(o.kind == m.kind and o.target == m.target and o.target is not None for o in s.board) \
                and not any(o.kind == m.kind == 'hunt' and o.data.get('nid') == m.data.get('nid') for o in s.board):
            s.board.append(m)


def active(game):
    return [m for m in game.missions if m.state in ('active', 'turnin')]


def accept(game, s, m):
    """s is whatever owns the board: a Settlement or a Stronghold."""
    p = game.player
    from .economy import free_cargo
    if len(active(game)) >= MAX_ACTIVE:
        game.msg(f'You already have {MAX_ACTIVE} jobs. Finish one first.', 'bad')
        return False
    if m.kind == 'escort' and any(x.kind == 'escort' and x.state == 'active' for x in game.missions):
        game.msg('You can only escort one caravan at a time.', 'bad')
        return False
    if m.kind == 'freight' and free_cargo(p) < m.data['w']:
        game.msg(f"You need {m.data['w']} free cargo space for this job.", 'bad')
        return False
    if m.kind == 'courier' and free_cargo(p) < 1:
        game.msg('You need 1 free cargo space for the parcel.', 'bad')
        return False
    s.board.remove(m)
    m.state = 'active'
    game.missions.append(m)
    w = game.world
    if m.kind in ('courier', 'freight', 'escort') and m.target is not None:
        t = w.settlements[m.target]
        game.reveal_place(t.x, t.y, 2)
    elif m.kind == 'fetch':
        d = w.dungeons[m.data['dungeon']]
        game.reveal_place(d.x, d.y, 1)
    elif m.kind == 'hunt':
        from . import named as NM
        n = NM.get(game, m.data['nid'])
        if n and n.did:
            d = w.dungeons[n.did]
            game.reveal_place(d.x, d.y, 1)
    if m.kind == 'courier':
        p.parcels.append(dict(mid=m.id, name=m.data['parcel'], w=1))
    elif m.kind == 'freight':
        p.parcels.append(dict(mid=m.id, name=f"{m.data['qty']} {D.GOODS[m.data['good']]['name']} (freight)", w=m.data['w']))
    elif m.kind in ('bounty', 'war_bounty'):
        x, y = m.data['spot']
        kind = 'bandits' if m.data['keys'][0] in ('bandit', 'brigand') else 'monsters'
        wd = make_group(game, kind, x, y, m.data['lvl'], m.data['keys'], 2, m.data['leader'])
        wd.kind = 'bounty'
        wd.mission = m.id
        wd.fg = D.UNIQUE_FG
        if m.kind == 'war_bounty':
            wd.group['faction'] = m.data['foe']
            wd.ch = '@'
        w.wanderers.append(wd)
    elif m.kind == 'escort':
        wd = Wanderer(game.new_id(), 'escort', s.x, s.y)
        wd.ch, wd.fg, wd.name, wd.mission = '♦', ESCORT_FG, 'Your caravan', m.id
        w.wanderers.append(wd)
    elif m.kind == 'fetch':
        d = w.dungeons[m.data['dungeon']]
        if getattr(d, 'poi', False):
            from .events import reveal
            for poi in w.pois:
                if poi.did == d.id:
                    reveal(game, poi)
        d.relic = m.id
        key = f'{d.id}:{d.depth}'
        if key in game.maps:
            place_relic(game, game.maps[key], m)
    game.msg(f'Job accepted: {m.title}.', 'gold')
    return True


def place_relic(game, mp, m):
    up = mp.t.index(UP) if UP in mp.t else 0
    ux, uy = up % mp.w, up // mp.w
    best = None
    for _ in range(400):
        c = rand_free(game, mp, lambda t: t == FLOOR)
        if c and (best is None or cheb(*c, ux, uy) > cheb(*best, ux, uy)):
            best = c
    if not best:
        return
    it = Item(game.new_id(), 'quest', 'relic')
    it.name = m.data['relic'][0].upper() + m.data['relic'][1:]
    it.mission = m.id
    it.x, it.y = best
    mp.items.append(it)
    d = game.world.dungeons[m.data['dungeon']]
    spawn_pack(game, mp, d.base + d.depth + 1, d.tag, best, elite=2, awake=False)


def complete(game, m, sids):
    from .war import change_rep
    p = game.player
    w = game.world
    m.state = 'done'
    from . import guilds as GU
    GU.job_done(game, m)
    local = w.settlements[m.giver].rep if m.giver is not None else max(0, p.rep.get(m.faction, 0))
    bonus = round(m.reward * min(local, 100) / 200)
    p.gold += m.reward + bonus
    for sid in sids:
        w.settlements[sid].rep = min(100, w.settlements[sid].rep + m.rep)
    if m.faction:
        change_rep(game, m.faction, m.rep if m.hold is not None else 2)
    p.parcels = [pc for pc in p.parcels if pc['mid'] != m.id]
    w.wanderers = [x for x in w.wanderers if x.mission != m.id]
    p.inv = [it for it in p.inv if getattr(it, 'mission', None) != m.id]
    from .money import fmt
    game.msg(f"Job done: {m.title}. You receive {fmt(m.reward + bonus)}{f' ({fmt(bonus)} reputation bonus)' if bonus else ''}.", 'gold')
    game.num(p.x, p.y, '+' + fmt(m.reward + bonus, True), (242, 196, 67), True)


def fail(game, m, why):
    p = game.player
    w = game.world
    m.state = 'failed'
    from . import guilds as GU
    GU.job_failed(game, m)
    if m.giver is not None:
        w.settlements[m.giver].rep = max(-50, w.settlements[m.giver].rep - 8)
    elif m.faction:
        from .war import change_rep
        change_rep(game, m.faction, -5)
    p.parcels = [pc for pc in p.parcels if pc['mid'] != m.id]
    w.wanderers = [x for x in w.wanderers if x.mission != m.id]
    game.msg(f'Job failed: {m.title}. {why}', 'bad')


def on_enter(game, sid):
    for m in active(game):
        if m.kind == 'personal':
            d = m.data
            if d['sub'] == 'letter' and d['rtown'] == sid:
                game.msg(f"You find {d['recipient']} at the inn and hand over the letter.", 'good')
                complete(game, m, [sid])
            elif d['wait'] == sid and d['sub'] != 'letter':
                game.msg(f"{d['client'].split()[0]} is waiting for you at the inn.", 'info')
            continue
        if m.kind in ('courier', 'freight') and m.target == sid:
            complete(game, m, [m.giver, sid])
        elif m.kind == 'escort' and m.target == sid:
            complete(game, m, [m.giver, sid])
        elif m.kind in ('bounty', 'fetch') and m.state == 'turnin' and m.giver == sid and m.hold is None:
            complete(game, m, [sid])


def on_group_defeated(game, wd):
    m = find(game, wd.mission)
    if m and m.kind in ('bounty', 'war_bounty', 'personal') and m.state == 'active':
        m.state = 'turnin'
        game.msg(f'{wd.group["leader"]} is dead. Return to {giver_name(game, m)} for your reward.', 'gold')


def on_pickup(game, it):
    m = find(game, getattr(it, 'mission', None))
    if m and m.state == 'active':
        m.state = 'turnin'
        game.msg(f'You found {it.name}! Bring it back to {giver_name(game, m)}.', 'unique')


def giver_name(game, m):
    if m.kind == 'personal':
        return f"{m.data['client'].split()[0]} at the inn in {game.world.settlements[m.data['wait']].name}"
    if m.hold is not None:
        return game.world.holds[m.hold].title
    return game.world.settlements[m.giver].name


def on_enter_hold(game, hid):
    p = game.player
    for m in active(game):
        if m.hold != hid:
            continue
        if m.kind == 'supply' and m.state == 'active':
            g, q = m.data['good'], m.data['qty']
            if p.cargo.get(g, 0) >= q:
                p.cargo[g] -= q
                if not p.cargo[g]:
                    del p.cargo[g]
                    p.cost_basis.pop(g, None)
                complete(game, m, [])
            else:
                game.msg(f"The quartermaster still waits for {q} {D.GOODS[g]['name']} (you carry {p.cargo.get(g, 0)}).", 'info')
        elif m.state == 'turnin':
            complete(game, m, [])


def on_capture(game, hid):
    for m in active(game):
        if m.kind == 'assault' and m.data.get('target_hold') == hid:
            m.state = 'turnin'
            game.msg(f'Return to {giver_name(game, m)} to claim your reward.', 'gold')


def on_escort_killed(game):
    for m in active(game):
        if m.kind == 'escort':
            fail(game, m, 'The caravan was destroyed.')


def find(game, mid):
    if mid is None:
        return None
    for m in game.missions:
        if m.id == mid:
            return m
    return None


def daily(game):
    for m in active(game):
        if m.deadline is not None and game.day > m.deadline and m.state == 'active':
            fail(game, m, 'You ran out of time.')
    game.missions = [m for m in game.missions if m.state in ('active', 'turnin')] + \
        [m for m in game.missions if m.state in ('done', 'failed')][-10:]


def escort_wanderer(game):
    for x in game.world.wanderers:
        if x.kind == 'escort':
            return x
    return None


def target_pos(game, m):
    """Where on the overworld this job wants you to go next."""
    w = game.world
    if m.kind == 'personal':
        d = m.data
        if m.state == 'active' and d['sub'] == 'letter':
            s = w.settlements[d['rtown']]
            return (s.x, s.y), s.name
        if m.state == 'active' and d['sub'] == 'hunt':
            return tuple(d['spot']), d['leader']
        if m.state == 'active' and d['sub'] == 'rescue':
            dg = w.dungeons[d['dungeon']]
            return (dg.x, dg.y), dg.name
        s = w.settlements[d['wait']]
        return (s.x, s.y), s.name
    if m.kind == 'hunt' and m.state == 'turnin':
        s = w.settlements[m.giver]
        return (s.x, s.y), s.name
    if m.state == 'turnin' or m.kind == 'supply':
        if m.hold is not None:
            h = w.holds[m.hold]
            return (h.x, h.y), h.title
        s = w.settlements[m.giver]
        return (s.x, s.y), s.name
    if m.kind == 'assault':
        h = w.holds[m.data['target_hold']]
        return (h.x, h.y), h.title
    if m.kind == 'war_bounty':
        return tuple(m.data['spot']), m.data['leader']
    if m.kind in ('courier', 'freight', 'escort'):
        s = w.settlements[m.target]
        return (s.x, s.y), s.name
    if m.kind == 'bounty':
        return tuple(m.data['spot']), m.data['leader']
    if m.kind == 'hunt':
        from . import named as NM
        n = NM.get(game, m.data['nid'])
        if n and n.did:
            dg = w.dungeons[n.did]
            return (dg.x, dg.y), dg.name
        if n and n.alive:
            ax, ay, _r = NM.area(game, n)
            return (ax, ay), 'the search area'
        s = w.settlements[m.giver]
        return (s.x, s.y), s.name
    d = w.dungeons[m.data['dungeon']]
    return (d.x, d.y), d.name


# ------------------------------------------------------------------ personal jobs from travellers
def accept_personal(game, wd, o):
    """A job from someone met on the road. They wait at the inn of the town they were heading for."""
    from .economy import free_cargo
    from .events import reveal
    p = game.player
    w = game.world
    if len(active(game)) >= MAX_ACTIVE:
        game.msg(f'You already have {MAX_ACTIVE} jobs. Finish one first.', 'bad')
        return False
    sub = o['sub']
    if sub == 'letter' and free_cargo(p) < 1:
        game.msg('You need 1 free cargo space for the letter.', 'bad')
        return False
    m = Mission(game.new_id(), 'personal', None)
    m.data = dict(o)
    m.reward = o['reward']
    m.rep = 0
    m.deadline = game.day + 14
    first = o['client'].split()[0]
    town = w.settlements[o['wait']].name
    if sub == 'letter':
        rt = w.settlements[o['rtown']].name
        m.title = f"{first}'s letter to {rt}"
        m.desc = f"Carry {first}'s letter to {o['recipient']} at the inn in {rt} before {CAL.short(m.deadline)}. Paid on delivery."
        p.parcels.append(dict(mid=m.id, name=f"{first}'s letter", w=1))
    elif sub == 'gather':
        g = D.GOODS[o['good']]['name']
        m.title = f"{o['qty']} {g} for {first}"
        m.desc = f"Bring {o['qty']} {g} to {first} at the inn in {town} before {CAL.short(m.deadline)}."
    elif sub == 'hunt':
        over = game.maps['over']
        spot = None
        for _ in range(400):
            x, y = wd.x + random.randint(-22, 22), wd.y + random.randint(-16, 16)
            if not over.inb(x, y) or cheb(x, y, wd.x, wd.y) < 8:
                continue
            t = over.tile(x, y)
            if D.TILES[t].walk and t not in (ROAD, TOWN, CITY, ENTR) and w.off_road(x, y) >= 3:
                spot = (x, y)
                break
        if not spot:
            game.msg('"Never mind, I think it has lost my trail."')
            return False
        reg = w.region_at(*spot)
        k = random.choice([k for k in D.BIOME_MONSTERS[reg.biome] if D.MONSTERS[k]['hp'] >= 2] or D.BIOME_MONSTERS[reg.biome])
        a, b, c = D.UNIQUE_NAME
        leader = random.choice(a) + random.choice(b) + ' ' + random.choice(c)
        lvl = w.danger_at(*spot) + 1
        keys = [k] + [random.choice(D.BIOME_MONSTERS[reg.biome]) for _ in range(random.randint(1, 3))]
        m.data.update(spot=spot, leader=leader, lvl=lvl)
        g = make_group(game, 'monsters', spot[0], spot[1], lvl, keys, 2, leader)
        g.kind = 'bounty'
        g.mission = m.id
        g.fg = D.UNIQUE_FG
        w.wanderers.append(g)
        over.seen[spot[1] * over.w + spot[0]] = 1
        m.title = f'Slay {leader}'
        m.desc = (f"Kill {leader}, a monstrous {D.MONSTERS[k]['name'].lower()} stalking {reg.name}, then find {first} "
                  f"at the inn in {town} before {CAL.short(m.deadline)}.")
    else:
        d = w.dungeons[o['dungeon']]
        if d.relic is not None:
            game.msg('"Someone else already went after it. Never mind."')
            return False
        d.relic = m.id
        for poi in w.pois:
            if poi.did == d.id:
                reveal(game, poi)
        key = f'{d.id}:{d.depth}'
        if key in game.maps:
            place_relic(game, game.maps[key], m)
        m.title = f"Recover {o['relic']} for {first}"
        m.desc = (f"Fetch {o['relic']} from the bottom of {d.name} and bring it to {first} at the inn in {town} "
                  f"before {CAL.short(m.deadline)}.")
    m.state = 'active'
    game.missions.append(m)
    for sid in (o['wait'], o.get('rtown')):
        if sid is not None:
            game.reveal_place(w.settlements[sid].x, w.settlements[sid].y, 2)
    game.msg(f'Job accepted: {m.title}. {first} will wait at the inn in {town}.', 'gold')
    return True


def place_clients(game, sid, mp):
    """Put the people waiting for you next to the innkeeper."""
    from .entities import make_npc
    from .worldgen import free_around as fa
    mp.mons = [o for o in mp.mons if getattr(o, 'role', None) != 'client']
    inn = next((o for o in mp.mons if o.role == 'inn'), None)
    for m in active(game):
        if m.kind != 'personal' or m.data['wait'] != sid or m.data['sub'] == 'letter':
            continue
        cx, cy = (inn.x, inn.y) if inn else mp.entry
        spots = fa(game, mp, cx, cy, 2)
        if not spots:
            continue
        x, y = random.choice(spots)
        npc = make_npc(game, m.data['client'], 'client', '#f0e68c', x, y, True)
        npc.mission = m.id
        mp.mons.append(npc)


def client_talk(game, npc):
    m = find(game, getattr(npc, 'mission', None))
    first = npc.name.split()[0]
    if not m or m.state not in ('active', 'turnin'):
        game.request = ('dialog', npc.name, '"Thank you again, friend. Safe travels."')
        return
    d = m.data
    p = game.player
    if d['sub'] == 'gather' and m.state == 'active':
        g, q = d['good'], d['qty']
        if p.cargo.get(g, 0) >= q:
            p.cargo[g] -= q
            if not p.cargo[g]:
                del p.cargo[g]
                p.cost_basis.pop(g, None)
            m.state = 'turnin'
        else:
            game.request = ('dialog', npc.name, f'"Did you bring the {q} {D.GOODS[g]["name"].lower()}? '
                            f'You only carry {p.cargo.get(g, 0)}. Any market should sell them."')
            return
    if m.state != 'turnin':
        what = {'hunt': f'"Is {d.get("leader", "the beast")} dead yet? I can still hear it howling at night."',
                'rescue': f'"Please, find {d.get("relic", "it")}. It means the world to me."'}.get(d['sub'], '"Any news?"')
        game.request = ('dialog', npc.name, what)
        return
    complete(game, m, [d['wait']])
    npc.mission = None
    from .money import fmt
    game.request = ('dialog', npc.name, f'"You did it! I knew I could trust you. Here, {fmt(m.reward)}, as promised." '
                    f'{first} shakes your hand warmly.')


def quest_mark(game, npc):
    """'!' over someone with work for you, '?' over someone you can hand a job in to, or None."""
    f, p = game.flags, game.player
    role = getattr(npc, 'role', None)
    if role == 'client':
        m = find(game, getattr(npc, 'mission', None))
        if not m or m.state not in ('active', 'turnin'):
            return None
        if m.state == 'turnin':
            return '?'
        d = m.data
        if d.get('sub') == 'gather' and p.cargo.get(d['good'], 0) >= d['qty']:
            return '?'
        return None
    if role == 'healer':
        m = game.map
        if getattr(m, 'site', None) is not None and m.site == getattr(game.world, 'start_temple', None) \
                and not f.get('met_priest'):
            return '!'
        return None
    if role == 'elder':
        if (f.get('ratking') and not f.get('reward_rat')) or (f.get('grolm') and not f.get('reward_grolm')):
            return '?'
        return '!' if not f.get('met_elder') else None
    if role == 'fisher':
        if not f.get('quest_fish'):
            return '!'
        if not f.get('fish_done') and any(i.k == 'fish' for i in p.inv):
            return '?'
        return None
    if role == 'herbalist':
        return '!' if not p.recipes else None
    if role == 'inn':
        sid = getattr(game.map, 'sid', None)
        if sid is None:
            return None
        s = game.world.settlements[sid]
        refresh_board(game, s)
        return '!' if s.board else None
    if role == 'castellan':
        hid = getattr(game.map, 'hid', None)
        if hid is None:
            return None
        h = game.world.holds[hid]
        refresh_hold_board(game, h)
        return '!' if h.board else None
    return None
