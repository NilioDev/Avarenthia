"""Game state and rules: movement, combat, monster AI, skills, loot, travel."""
import os
import pickle
import random

from . import data as D
from . import economy as ECO
from . import fov
from . import missions as MS
from . import wanderers as WA
from . import world as WO
from . import worldgen as W
from .data import (FLOOR, DOOR, ODOOR, DOWN, UP, WATER, MOUNTAIN, TOWN, ENTR, WELL, ROAD, CITY)
from .entities import Item, Player, make_gear, make_unique, random_gear, make_monster
from .worldgen import D8, cheb

SAVE_VERSION = 4

C_DMG = (244, 234, 208)
C_CRIT = (255, 154, 60)
C_HURT = (255, 90, 74)
C_HEAL = (127, 224, 122)
C_MANA = (127, 162, 255)
C_MISS = (143, 133, 115)
C_GOLD = (242, 196, 67)


def clamp(v, a, b):
    return max(a, min(b, v))


def xp_for(lvl):
    return int(30 * lvl ** 2.1)


def line(x0, y0, x1, y1):
    pts = []
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err, x, y = dx + dy, x0, y0
    while not (x == x1 and y == y1):
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy
        pts.append((x, y))
    return pts


def ring(x, y, r):
    out = []
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            d = max(abs(dx), abs(dy))
            if d == r or (r > 1 and d == r - 1 and random.random() < .4):
                out.append((x + dx, y + dy))
    return out


def plural(n):
    return n[:-1] + 'ves' if n.endswith('f') else n + 's'


def dir_name(dx, dy):
    import math
    a = (math.degrees(math.atan2(dy, dx)) + 360 + 22.5) % 360
    return ['east', 'southeast', 'south', 'southwest', 'west', 'northwest', 'north', 'northeast'][int(a // 45)]


class Game:
    def __init__(self, name, cls):
        self.version = SAVE_VERSION
        self._next_id = 1
        self.turn = 0
        self.maps = {}
        self.cur = 'town'
        self.log = []
        self.log_mark = 0
        self.flags = {}
        self.dead = False
        self.cause = None
        self.kills = 0
        self.max_depth = {}
        self.last_save = 0
        self.portal = None
        self.shops = {}
        self.missions = []
        self.price_log = {}
        self.encounter = None
        self.last_day = 1
        self.low_warned = False
        self.events = []        # transient effects for the UI
        self.request = None     # transient: a screen the UI should open
        self.vis = bytearray()
        self.dist = None

        p = self.player = Player(name or 'Wanderer', cls)
        p.x = p.y = -5
        self.cur = 'none'

        def gear(bk):
            it = make_gear(self, bk, 'normal', 1)
            self.add_to_inv(it)
            p.eq[it.slot] = it.id

        if cls == 'barbarian':
            gear('shortsword'); gear('quilted')
            self.add_to_inv(Item(self.new_id(), 'potion', 'hp', 4))
        elif cls == 'rogue':
            gear('dagger'); gear('quilted')
            self.add_to_inv(Item(self.new_id(), 'potion', 'hp', 3))
            self.add_to_inv(Item(self.new_id(), 'potion', 'mp', 2))
        else:
            gear('staff'); gear('cap')
            self.add_to_inv(Item(self.new_id(), 'potion', 'hp', 3))
            self.add_to_inv(Item(self.new_id(), 'potion', 'mp', 4))
        self.add_to_inv(Item(self.new_id(), 'scroll', 'tp', 2))
        s = self.stats()
        p.life, p.mana = s['max_life'], s['max_mana']

        over, world = WO.gen_world(self)
        self.maps['over'] = over
        self.world = world
        for st in world.settlements:
            st.services = WO.settlement_services(st)
        ECO.init_markets(world)
        home = world.settlements[0]
        self.over_pos = (home.x, home.y)
        # the realm map you start with: every road and settlement, plus the land around Thornfield
        for i, t in enumerate(over.t):
            if t in (ROAD, TOWN, CITY):
                over.seen[i] = 1
        for y in range(home.y - 6, home.y + 7):
            for x in range(home.x - 9, home.x + 10):
                if over.inb(x, y):
                    over.seen[y * over.w + x] = 1
        rat = world.dungeons['rat']
        over.seen[rat.y * over.w + rat.x] = 1
        self.home = 0
        self.cur = home.map_key
        self.maps[self.cur] = WO.gen_settlement_map(self, home)
        m = self.maps[self.cur]
        p.x, p.y = m.entry[0] + 2, m.entry[1]
        self.shops = {0: W.gen_shop(self)}
        WA.populate(self)
        MS.refresh_board(self, home)
        self.msg(f'Welcome to Thornfield, {p.name}. A curse lies over the vale.', 'gold')
        self.msg('Talk to Elder Berend (the purple @) for your quest, or find work on the board at the inn.', 'info')
        self.msg('Press ? or F1 for controls.')
        self.compute_fov()

    # ------------------------------------------------------------ basics
    def new_id(self):
        self._next_id += 1
        return self._next_id

    @property
    def map(self):
        return self.maps[self.cur]

    @property
    def day(self):
        return self.turn // D.DAY_LEN + 1

    @property
    def here(self):
        """The settlement you are standing in, or None."""
        m = self.maps.get(self.cur)
        if m is not None and m.kind == 'town':
            return self.world.settlements[m.sid]
        return None

    def msg(self, text, cls=''):
        self.log.append((text, cls))
        if len(self.log) > 120:
            cut = len(self.log) - 120
            del self.log[:cut]
            self.log_mark = max(0, self.log_mark - cut)

    def num(self, x, y, text, col, big=False):
        self.events.append(('num', x, y, text, col, big))

    def flash(self, cells, col, ch='*', dur=.18):
        self.events.append(('flash', list(cells), col, ch, dur))

    def shake(self):
        self.events.append(('shake',))

    def occupied(self, m, x, y):
        return W.occupied(self, m, x, y)

    def __getstate__(self):
        st = self.__dict__.copy()
        st['events'] = []
        st['request'] = None
        st['vis'] = bytearray()
        st['dist'] = None
        return st

    # ------------------------------------------------------------ inventory
    def add_to_inv(self, it):
        inv = self.player.inv
        if it.stackable:
            for o in inv:
                if o.k == it.k and o.t == it.t:
                    o.n += it.n
                    return True
        if len(inv) >= 24:
            return False
        inv.append(it)
        return True

    def remove_one(self, it):
        inv = self.player.inv
        if it.n > 1:
            it.n -= 1
        elif it in inv:
            inv.remove(it)

    def eq_item(self, slot):
        iid = self.player.eq.get(slot)
        if iid is None:
            return None
        for it in self.player.inv:
            if it.id == iid:
                return it
        return None

    def is_equipped(self, it):
        return it.id in self.player.eq.values()

    def backpack(self):
        return [it for it in self.player.inv if not self.is_equipped(it)]

    def count(self, k, t=None):
        return sum(it.n for it in self.player.inv if it.k == k and (t is None or it.t == t))

    # ------------------------------------------------------------ derived stats
    def stats(self):
        p = self.player
        c = D.CLASSES[p.cls]
        s = dict(str=p.str, dex=p.dex, vit=p.vit, ene=p.ene, life=0, mana=0, dmg_flat=0, ed=0, hit=0,
                 leech=0, crit=5, regen=0, armor=0)
        for slot in D.SLOTS:
            it = self.eq_item(slot)
            if not it:
                continue
            for st, v in it.aff:
                if st != 'edef':
                    s[st] = s.get(st, 0) + v
            b = D.BASES[it.base]
            s['mana'] += b.get('mana', 0)
            s['hit'] += b.get('hit', 0)
            s['armor'] += it.armor_value()
        s['max_life'] = int(10 + s['vit'] * 2 + (p.lvl - 1) * c['life_lvl'] + s['life'])
        s['max_mana'] = int(s['ene'] * 2 + (p.lvl - 1) * c['mana_lvl'] + s['mana'])
        w = self.eq_item('weapon')
        bd = w.dmg if w else (1, 3)
        mul = 1 + (s['dex'] if p.cls == 'rogue' else s['str']) / 100 + s['ed'] / 100
        s['dmg'] = (max(1, int(bd[0] * mul + s['dmg_flat'])), max(1, int(bd[1] * mul + s['dmg_flat'])))
        s['ar'] = 20 + s['dex'] * 2 + p.lvl * 5 + s['hit']
        s['def'] = s['armor'] + s['dex'] // 2
        return s

    def clamp_vitals(self):
        s, p = self.stats(), self.player
        p.life = min(p.life, s['max_life'])
        p.mana = min(p.mana, s['max_mana'])

    # ------------------------------------------------------------ vision
    def compute_fov(self):
        m, p = self.map, self.player
        self.vis = fov.compute(m, p.x, p.y, m.radius)

    def visible(self, x, y):
        m = self.map
        return m.inb(x, y) and self.vis[y * m.w + x]

    def visible_hostiles(self):
        return [o for o in self.map.mons if not o.is_npc and self.visible(o.x, o.y)]

    def hostile_visible(self):
        return bool(self.visible_hostiles())

    def line_clear(self, x0, y0, x1, y1):
        m, p = self.map, self.player
        pts = line(x0, y0, x1, y1)
        for x, y in pts[:-1]:
            if D.TILES[m.tile(x, y)].opaque or m.mon_at(x, y) or (p.x == x and p.y == y):
                return None
        return pts

    def compute_dist(self):
        m = self.map
        p = self.player
        self.dist = W.bfs(m, p.x, p.y, lambda t: D.TILES[t].walk or D.TILES[t].door)

    def loc_name(self):
        m = self.map
        if m.kind == 'dungeon':
            return f'{m.name} - level {m.depth}'
        if m.kind == 'over':
            p = self.player
            return self.world.region_at(p.x, p.y).name
        return m.name

    def dir_to(self, k):
        d = self.world.dungeons[k]
        h = self.world.settlements[0]
        return dir_name(d.x - h.x, d.y - h.y)

    # ------------------------------------------------------------ map changes
    def enter_dungeon(self, did, depth, arrive):
        key = f'{did}:{depth}'
        p = self.player
        dg = self.world.dungeons[did]
        if self.cur == 'over':
            self.over_pos = (p.x, p.y)
        self.cur = key
        p.x = p.y = -5
        if key not in self.maps:
            self.maps[key] = W.gen_dungeon(self, did, depth)
            if depth == dg.depth and dg.relic is not None:
                mi = MS.find(self, dg.relic)
                if mi and mi.state == 'active':
                    MS.place_relic(self, self.maps[key], mi)
        m = self.map
        want = DOWN if arrive == 'down' else UP
        if want in m.t:
            i = m.t.index(want)
            p.x, p.y = i % m.w, i // m.w
        first = self.max_depth.get(did, 0) < depth
        if first:
            self.max_depth[did] = depth
        self.msg(f"{dg.name}, level {depth}.", 'info')
        if first and depth == dg.depth:
            self.msg('An evil presence fills the air. This is the deepest level.', 'bad')
        self.compute_fov()
        self.request = ('save',)

    def leave_to_over(self):
        p = self.player
        m = self.map
        if m.kind == 'wild':
            self.resolve_encounter()
            self.maps.pop('wild', None)
        elif m.kind == 'town':
            s = self.world.settlements[m.sid]
            self.over_pos = (s.x, s.y)
        self.cur = 'over'
        p.x, p.y = self.over_pos
        esc = MS.escort_wanderer(self)
        if esc and (esc.x, esc.y) != (p.x, p.y) and cheb(esc.x, esc.y, p.x, p.y) > 1:
            esc.x, esc.y = p.x, p.y
        self.msg(f'You are back on the road, in {self.loc_name()}.')
        self.compute_fov()
        self.request = ('save',)

    def resolve_encounter(self):
        wd = next((x for x in self.world.wanderers if x.id == self.encounter), None)
        self.encounter = None
        m = self.maps.get('wild')
        esc = next((o for o in m.mons if o.role == 'escort'), None) if m else None
        if esc:
            for mi in MS.active(self):
                if mi.kind == 'escort':
                    mi.data['hp'] = esc.hp
        if not wd:
            return
        alive = [o for o in m.mons if not o.is_npc] if m else []
        if not alive:
            self.world.wanderers.remove(wd)
            self.msg(f'You have dealt with {wd.name[0].lower() + wd.name[1:]}.', 'good')
            MS.on_group_defeated(self, wd)
        else:
            wd.cooldown = 4

    def enter_town(self, sid, from_portal=False):
        p = self.player
        s = self.world.settlements[sid]
        if self.cur == 'over':
            self.over_pos = (p.x, p.y)
        if s.map_key not in self.maps:
            self.maps[s.map_key] = WO.gen_settlement_map(self, s)
        self.cur = s.map_key
        self.home = sid
        m = self.map
        if from_portal:
            p.x, p.y = m.portal_pos[0], m.portal_pos[1] + 1
        else:
            p.x, p.y = m.entry[0] + (1 if m.entry[0] == 0 else 0), m.entry[1]
        if 'shop' in s.services:
            self.shops[sid] = W.gen_shop(self, s.is_city)
        MS.refresh_board(self, s)
        esc = MS.escort_wanderer(self)
        if esc:
            esc.x, esc.y = s.x, s.y
        self.msg(f'You enter {s.name}.', 'info')
        if s.event:
            self.msg('News: ' + D.EVENTS[s.event[0]]['text'].format(town=s.name), 'info')
        MS.on_enter(self, sid)
        self.compute_fov()
        self.request = ('save',)

    def start_encounter(self, wd=None, terrain=None, lvl=1, keys=None):
        p = self.player
        self.over_pos = (p.x, p.y)
        if terrain is None:
            terrain = self.maps['over'].tile(p.x, p.y)
        if wd:
            g = wd.group
            lvl, keys, elite, leader = g['lvl'], g['keys'], g['elite'], g.get('leader')
            self.encounter = wd.id
        else:
            elite, leader = 0, None
            self.encounter = None
        self.cur = 'wild'
        p.x = p.y = -5
        w = W.gen_wild(self, terrain, lvl, keys, elite, leader)
        self.maps['wild'] = w
        p.x, p.y = w.entry
        for mi in MS.active(self):
            if mi.kind == 'escort':
                spot = W.free_around(self, w, p.x, p.y, 1)
                if spot:
                    from .entities import make_npc
                    c = make_npc(self, 'Your caravan', 'escort', '#6ee2ec', spot[0][0], spot[0][1], True, ch='♦')
                    c.hp = c.maxhp = mi.data['hp']
                    w.mons.append(c)
        if wd:
            n = len(keys)
            what = wd.name if n == 1 or wd.kind in ('bounty', 'bandits') else f"{n} {plural(D.MONSTERS[keys[0]]['name'])}"
            self.msg(f'{what} attack{"s" if n == 1 or wd.kind in ("bounty", "bandits") else ""}!', 'bad')
        else:
            self.msg('You are ambushed!', 'bad')
        self.msg('Defeat them, or walk off the edge of the map to escape.')
        self.compute_fov()

    def dungeon_at(self, x, y):
        d = self.world.dungeon_at(x, y)
        return d.id if d else None

    # ------------------------------------------------------------ player actions (return turn cost)
    def try_move(self, dx, dy):
        m, p = self.map, self.player
        nx, ny = p.x + dx, p.y + dy
        if not m.inb(nx, ny):
            if m.kind in ('town', 'wild'):
                if m.kind == 'wild' and any(not o.is_npc and o.awake and cheb(o.x, o.y, p.x, p.y) <= 1 for o in m.mons):
                    self.msg('You cannot flee with an enemy next to you.', 'bad')
                    return 0
                self.leave_to_over()
                return 1
            return 0
        if m.kind == 'over':
            wd = WA.wanderer_at(self, nx, ny)
            if wd:
                if wd.hostile:
                    self.start_encounter(wd)
                    return 1
                if wd.kind == 'escort':
                    wd.x, wd.y = p.x, p.y
                    p.x, p.y = nx, ny
                    return self.over_step(moved_escort=True)
                self.msg(wd.describe(self), 'info')
                return 0
        mon = m.mon_at(nx, ny)
        if mon:
            if mon.is_npc:
                if mon.role == 'escort' or (not mon.stay and mon.role in ('villager', 'guard', 'dog') and random.random() < .5):
                    mon.x, mon.y, p.x, p.y = p.x, p.y, nx, ny
                    return 1
                self.talk(mon)
                return 0
            self.melee(mon)
            return 1
        t = m.tile(nx, ny)
        if t == DOOR:
            m.set(nx, ny, ODOOR)
            return 1
        if not D.TILES[t].walk:
            if t == WATER:
                self.msg('You cannot swim here.')
            elif t == MOUNTAIN:
                self.msg('The mountains are too steep to climb.')
            elif t == WELL:
                self.msg('An old well. The water is cool and clear.')
            return 0
        ox, oy = p.x, p.y
        p.x, p.y = nx, ny
        if m.kind == 'over':
            esc = MS.escort_wanderer(self)
            if esc:
                esc.x, esc.y = ox, oy
            return self.over_step()
        if m.kind == 'town' and self.portal and self.portal.get('sid') == m.sid and (nx, ny) == m.portal_pos:
            self.use_portal_back()
            return 1
        self.auto_pickup()
        self.describe_here()
        return 1

    def over_step(self, moved_escort=False):
        m, p = self.map, self.player
        t = m.tile(p.x, p.y)
        s = self.world.settlement_at(p.x, p.y)
        if s:
            kind = 'city' if s.is_city else 'village'
            self.msg(f'You stand at the gates of {s.name} ({kind}). Press > or Enter to go in.', 'info')
            return 10
        if t == ENTR:
            d = self.world.dungeon_at(p.x, p.y)
            self.msg(f"You stand at the entrance of {d.name}. Press > or Enter to descend.", 'info')
            return 10
        cost = D.TILES[t].cost
        reg = self.world.region_at(p.x, p.y)
        if t != ROAD and cheb(p.x, p.y, *self._home_xy()) > 4 and random.random() < .008 * cost / 10:
            k = random.choice(D.BIOME_MONSTERS[reg.biome])
            n = random.randint(1, 2) if D.MONSTERS[k]['hp'] >= 2 else random.randint(2, 3)
            self.start_encounter(None, t, reg.danger, [k] * n)
            return 1
        return cost

    def _home_xy(self):
        h = self.world.settlements[0]
        return h.x, h.y

    def auto_pickup(self):
        m, p = self.map, self.player
        for it in [i for i in m.items if i.x == p.x and i.y == p.y]:
            if it.k == 'gold':
                p.gold += it.n
                self.num(p.x, p.y, f'+{it.n}g', C_GOLD)
                self.msg(f'You pick up {it.n} gold.', 'gold')
            elif it.k == 'orb':
                s = self.stats()
                h = round(s['max_life'] * .25)
                p.life = min(s['max_life'], p.life + h)
                p.mana = min(s['max_mana'], p.mana + round(s['max_mana'] * .1))
                self.num(p.x, p.y, f'+{h}', C_HEAL)
                self.msg('The health orb restores you.', 'good')
            elif it.dropped or (it.k == 'gear' and it.rar == 'normal'):
                continue
            else:
                if not self.add_to_inv(it):
                    self.msg('Your bag is full.', 'bad')
                    continue
                self.msg(f'You pick up {it.display_name()}.', it.rar if it.k == 'gear' else '')
                if it.k == 'quest':
                    MS.on_pickup(self, it)
            m.items.remove(it)

    def describe_here(self):
        m, p = self.map, self.player
        its = [i for i in m.items if i.x == p.x and i.y == p.y]
        if len(its) == 1:
            self.msg(f'You see {its[0].display_name()}. Press g to pick it up.')
        elif its:
            self.msg('Several items lie here. Press g to pick them up.')
        t = m.tile(p.x, p.y)
        if t == DOWN:
            self.msg('Stairs lead down.')
        elif t == UP:
            self.msg('Stairs lead up.')

    def pickup(self):
        m, p = self.map, self.player
        its = [i for i in m.items if i.x == p.x and i.y == p.y and i.k not in ('gold', 'orb')]
        if not its:
            self.msg('There is nothing here.')
            return 0
        for it in its:
            if not self.add_to_inv(it):
                self.msg('Your bag is full.', 'bad')
                break
            it.dropped = False
            m.items.remove(it)
            self.msg(f'You pick up {it.display_name()}.', it.rar if it.k == 'gear' else '')
        return 1

    def use_stairs(self, d='auto'):
        m, p = self.map, self.player
        t = m.tile(p.x, p.y)
        if m.kind == 'over':
            if d == 'up':
                self.msg('You are already on the surface.')
                return 0
            s = self.world.settlement_at(p.x, p.y)
            if s:
                self.enter_town(s.id)
                return 1
            if t == ENTR:
                self.enter_dungeon(self.dungeon_at(p.x, p.y), 1, 'up')
                return 1
            self.msg('There is nothing to enter here.')
            return 0
        if t == DOWN and d != 'up':
            self.enter_dungeon(m.did, m.depth + 1, 'up')
            return 1
        if t == UP and d != 'down':
            if m.depth == 1:
                self.cur = 'over'
                p.x, p.y = self.over_pos
                self.msg('You climb back into the daylight.')
                self.compute_fov()
                self.request = ('save',)
            else:
                self.enter_dungeon(m.did, m.depth - 1, 'down')
            return 1
        self.msg('There are no stairs here.' if m.kind == 'dungeon' else 'Walk off the edge of the map to leave.')
        return 0

    def town_portal(self):
        p = self.player
        it = next((i for i in p.inv if i.k == 'scroll'), None)
        if not it:
            self.msg('You have no Scroll of Town Portal.')
            return 0
        m = self.map
        if m.kind == 'town':
            self.msg('You are already in town.')
            return 0
        if m.kind == 'over':
            self.msg('Town Portal only works in dungeons and battles. Walk to a town instead.')
            return 0
        if any(cheb(o.x, o.y, p.x, p.y) <= 1 for o in self.visible_hostiles()):
            self.msg('The portal will not open with an enemy at your side.', 'bad')
            return 0
        self.remove_one(it)
        home = self.world.settlements[self.home]
        self.portal = dict(map=self.cur, x=p.x, y=p.y, over=self.over_pos, sid=home.id)
        self.enter_town(home.id, from_portal=True)
        self.flash(ring(p.x, p.y - 1, 1), (90, 176, 255), '0', .3)
        self.msg('A shimmering blue portal opens. Step into it to return.', 'info')
        return 1

    def use_portal_back(self):
        pt, self.portal = self.portal, None
        if pt['map'] not in self.maps:
            self.msg('The portal collapses.')
            return
        p = self.player
        self.cur = pt['map']
        self.over_pos = pt['over']
        p.x, p.y = pt['x'], pt['y']
        self.msg('You step through the portal.', 'info')
        self.compute_fov()
        self.request = ('save',)

    def drink(self, kind):
        p = self.player
        it = next((i for i in p.inv if i.k == 'potion' and i.t == kind), None)
        if not it and kind != 'rejuv':
            it = next((i for i in p.inv if i.k == 'potion' and i.t == 'rejuv'), None)
        if not it:
            self.msg(f"You have no {'health' if kind == 'hp' else 'mana'} potions left.", 'bad')
            return 0
        s = self.stats()
        self.remove_one(it)
        if it.t in ('hp', 'rejuv'):
            h = round(s['max_life'] * (.45 if it.t == 'hp' else .4)) + 10
            p.life = min(s['max_life'], p.life + h)
            p.poison = None
            self.num(p.x, p.y, f'+{h}', C_HEAL, True)
        if it.t in ('mp', 'rejuv'):
            h = round(s['max_mana'] * (.5 if it.t == 'mp' else .4)) + 8
            p.mana = min(s['max_mana'], p.mana + h)
            self.num(p.x, p.y + (1 if it.t == 'rejuv' else 0), f'+{h}', C_MANA, True)
        self.msg({'hp': 'You drink a health potion.', 'mp': 'You drink a mana potion.', 'rejuv': 'You drink a rejuvenation potion.'}[it.t], 'good')
        return 1

    def equip(self, it):
        p = self.player
        if it.req > p.lvl:
            self.msg(f'You need to be level {it.req} to use that.', 'bad')
            return False
        p.eq[it.slot] = it.id
        self.clamp_vitals()
        self.msg(f'You equip {it.name}.', it.rar)
        return True

    def unequip(self, slot):
        if self.player.eq.pop(slot, None) is not None:
            self.clamp_vitals()
            self.msg('You remove the item.')

    def drop(self, it):
        p = self.player
        for k, v in list(p.eq.items()):
            if v == it.id:
                del p.eq[k]
        p.inv.remove(it)
        it.dropped = True
        it.x, it.y = p.x, p.y
        self.map.items.append(it)
        self.msg(f'You drop {it.display_name()}.')
        self.clamp_vitals()
        return 1

    def add_stat(self, st):
        p = self.player
        if p.stat_pts <= 0:
            return
        p.stat_pts -= 1
        setattr(p, st, getattr(p, st) + 1)
        if st == 'vit':
            p.life += 2
        if st == 'ene':
            p.mana += 2

    def learn_skill(self, i):
        p = self.player
        k = D.SKILLS[p.cls][i]
        r = p.skills.get(k.id, 0)
        if p.skill_pts > 0 and p.lvl >= k.lvl and r < 10:
            p.skill_pts -= 1
            p.skills[k.id] = r + 1
            self.msg(f'{k.name} is now rank {r + 1}.', 'gold')

    # ------------------------------------------------------------ shop
    def buy_supply(self, i):
        k, t = [('potion', 'hp'), ('potion', 'mp'), ('scroll', 'tp')][i]
        it = Item(self.new_id(), k, t)
        p = self.player
        if p.gold < it.value():
            return
        if not self.add_to_inv(it):
            self.msg('Your bag is full.', 'bad')
            return
        p.gold -= it.value()
        self.msg(f"You buy a {D.POTIONS[t]['name'] if k == 'potion' else 'Scroll of Town Portal'}.", 'gold')

    def buy_gear(self, i):
        shop = self.shops.get(self.home, [])
        if i >= len(shop):
            return
        it, p = shop[i], self.player
        if p.gold < it.value():
            return
        if not self.add_to_inv(it):
            self.msg('Your bag is full.', 'bad')
            return
        shop.pop(i)
        p.gold -= it.value()
        self.msg(f'You buy {it.name}.', it.rar)

    def buy_mount(self, key):
        p = self.player
        mt = D.MOUNTS[key]
        if key in p.mounts:
            self.msg(f"You already own a {mt['name'].lower()}.")
            return
        if key == 'cart' and 'mule' not in p.mounts:
            self.msg('A cart needs a pack mule to pull it. Buy the mule first.', 'bad')
            return
        if p.gold < mt['price']:
            self.msg('You cannot afford that.', 'bad')
            return
        p.gold -= mt['price']
        p.mounts.append(key)
        self.msg(f"You buy a {mt['name'].lower()}. Your cargo space is now {ECO.cargo_capacity(p)}.", 'gold')

    def sell(self, it):
        if self.is_equipped(it) or it.k == 'quest':
            return
        v = max(1, it.value() // 4)
        name = it.display_name() if it.n == 1 else (D.POTIONS[it.t]['name'] if it.k == 'potion' else 'Scroll of Town Portal')
        self.remove_one(it)
        self.player.gold += v
        self.msg(f'You sell {name} for {v} gold.', 'gold')

    # ------------------------------------------------------------ combat
    def wake_pack(self, mon):
        if mon.pack is None:
            return
        for o in self.map.mons:
            if o.pack == mon.pack:
                o.awake = True

    def damage_mon(self, mon, dmg, crit=False, col=C_DMG, weapon=False):
        p = self.player
        dmg = max(1, round(dmg * (2 if crit else 1)))
        mon.hp -= dmg
        mon.awake = True
        self.wake_pack(mon)
        mon.hit_flash = 1
        self.num(mon.x, mon.y, f'{dmg}!' if crit else str(dmg), C_CRIT if crit else col, crit)
        if crit:
            self.shake()
        if weapon:
            s = self.stats()
            if s['leech'] > 0:
                p.life = min(s['max_life'], p.life + max(1, round(dmg * s['leech'] / 100)))
        if mon.hp <= 0:
            self.kill(mon)
            return True
        return False

    def melee(self, mon):
        s = self.stats()
        self.player.last_target = mon.id
        if random.random() >= clamp(.95 * s['ar'] / (s['ar'] + mon.df), .25, .95):
            self.num(mon.x, mon.y, 'miss', C_MISS)
            self.msg(f'You miss {mon.the()}.')
            mon.awake = True
            self.wake_pack(mon)
            return
        crit = random.random() < s['crit'] / 100
        if not self.damage_mon(mon, random.randint(*s['dmg']), crit, weapon=True):
            self.msg(f"You {'critically ' if crit else ''}hit {mon.the()}.")

    def weapon_strike(self, mon, pct, force_crit=False):
        s = self.stats()
        crit = force_crit or random.random() < s['crit'] / 100
        return self.damage_mon(mon, random.randint(*s['dmg']) * pct / 100, crit, weapon=True)

    def hurt(self, dmg, src):
        p = self.player
        dmg = max(1, round(dmg))
        p.life -= dmg
        s = self.stats()
        big = dmg >= s['max_life'] * .2
        self.num(p.x, p.y, f'-{dmg}', C_HURT, big)
        if big:
            self.shake()
        if p.life <= 0:
            self.die(src)
            return
        if p.life < s['max_life'] * .3 and not self.low_warned:
            self.low_warned = True
            self.msg('Your life is low! Press Q to drink a health potion.', 'bad')
        if p.life >= s['max_life'] * .3:
            self.low_warned = False

    def kill(self, mon):
        m, p = self.map, self.player
        if mon not in m.mons:
            return
        m.mons.remove(mon)
        self.kills += 1
        special = mon.elite or mon.is_boss
        self.msg(f"{mon.the()[0].upper() + mon.the()[1:]} {'is slain!' if mon.is_boss or mon.elite == 2 else 'dies.'}", 'gold' if special else '')
        self.gain_xp(max(1, round(mon.xp * clamp(1 - (p.lvl - mon.lvl - 1) * .15, .05, 1))))
        if 'Fire Enchanted' in mon.mods:
            self.flash(ring(mon.x, mon.y, 1), (255, 122, 44), '*', .26)
            self.msg(f'{mon.name} explodes in flames!', 'bad')
            if cheb(mon.x, mon.y, p.x, p.y) <= 1:
                self.hurt(mon.dmg[1] * .8, mon.name)
        self.drop_loot(mon)
        if mon.k == 'ratking':
            self.flags['ratking'] = True
            self.msg('The rats scatter in every direction. Elder Berend will want to hear of this.', 'gold')
        elif mon.k == 'grolm':
            self.flags['grolm'] = True
            self.msg('The Lost Mine falls silent.', 'gold')
        elif mon.k == 'lich':
            self.flags['lich'] = True
            self.msg('Morvenna shrieks and crumbles to dust. The curse is broken!', 'unique')
            self.request = ('win',)

    def spill(self, m, x, y, it):
        p = self.player
        spots = [(x, y)] + [c for c in W.free_around(self, m, x, y, 2) if c != (p.x, p.y)]
        free = [c for c in spots if D.TILES[m.tile(*c)].walk and not any(o.x == c[0] and o.y == c[1] for o in m.items)]
        it.x, it.y = random.choice(free[:6]) if free else (x, y)
        m.items.append(it)

    def drop_loot(self, mon):
        m, lvl = self.map, mon.lvl
        boss = mon.is_boss
        boost = 4 if boss else 3 if mon.elite == 2 else 2 if mon.elite == 1 else 1
        n = 4 if boss else random.randint(2, 3) if mon.elite == 2 else random.randint(1, 2) if mon.elite == 1 else (1 if random.random() < .28 else 0)
        if boss:
            u = next((u for u in D.UNIQUES if u.get('boss') == mon.k), None)
            if u:
                it = make_unique(self, u)
                self.spill(m, mon.x, mon.y, it)
                self.announce(it)
            n = 3
        for _ in range(n):
            it = random_gear(self, lvl, boost)
            if boost > 1 and it.rar == 'normal':
                up = make_gear(self, it.base, 'magic', lvl)
                it.rar, it.aff, it.name = up.rar, up.aff, up.name
            self.spill(m, mon.x, mon.y, it)
            self.announce(it)
        special = mon.elite or boss
        if random.random() < (1 if boss else .9 if mon.elite else .4):
            self.spill(m, mon.x, mon.y, Item(self.new_id(), 'gold', 'gold', round(random.randint(lvl * 2, lvl * 6 + 5) * boost)))
        if special or random.random() < .16:
            self.spill(m, mon.x, mon.y, Item(self.new_id(), 'orb', 'orb'))
        if random.random() < (.6 if special else .1):
            t = 'rejuv' if random.random() < .12 else 'hp' if random.random() < .6 else 'mp'
            self.spill(m, mon.x, mon.y, Item(self.new_id(), 'potion', t))

    def announce(self, it):
        if it.rar == 'unique':
            self.msg(f'A unique item drops: {it.name}!', 'unique')
        elif it.rar == 'rare':
            self.msg(f'A rare item drops: {it.name}.', 'rare')

    def gain_xp(self, n):
        p = self.player
        p.xp += n
        while p.xp >= xp_for(p.lvl):
            p.lvl += 1
            p.stat_pts += 5
            p.skill_pts += 1
            s = self.stats()
            p.life, p.mana = s['max_life'], s['max_mana']
            self.num(p.x, p.y, 'LEVEL UP', C_GOLD, True)
            self.shake()
            self.msg(f'You reach level {p.lvl}! Press C to spend your stat and skill points.', 'gold')
            for k in D.SKILLS[p.cls]:
                if k.lvl == p.lvl:
                    self.msg(f'New skill available: {k.name}.', 'gold')

    def mon_hit_chance(self, mon, df):
        return clamp(.9 * mon.hit_r / (mon.hit_r + df * .6), .15, .9)

    def mon_attack(self, mon, df):
        p = self.player
        if random.random() < self.mon_hit_chance(mon, df):
            dmg = random.randint(*mon.dmg)
            if 'Vampiric' in mon.mods:
                mon.hp = min(mon.maxhp, mon.hp + round(dmg / 2))
            if mon.tpl['leech']:
                mon.hp = min(mon.maxhp, mon.hp + round(dmg / 3))
            self.msg(f'{mon.the()[0].upper() + mon.the()[1:]} hits you.', 'bad')
            if mon.tpl['poison'] and random.random() < .4:
                p.poison = [6, max(1, round(mon.lvl / 2))]
                self.msg('Venom burns in your veins!', 'bad')
            self.hurt(dmg, mon.the())
        else:
            self.num(p.x, p.y, 'miss', C_MISS)

    def mon_shoot(self, mon, spell, df):
        p = self.player
        path = self.line_clear(mon.x, mon.y, p.x, p.y)
        if not path:
            return False
        self.flash(path[:-1], (255, 122, 60) if spell else (216, 208, 176), '*' if spell else '-', .2)
        name = mon.the()[0].upper() + mon.the()[1:]
        if spell or random.random() < self.mon_hit_chance(mon, df):
            self.msg(f"{name}'s {'firebolt' if spell else 'arrow'} hits you.", 'bad')
            self.hurt(random.randint(*mon.dmg) * (.9 if spell else .8), mon.the())
        else:
            self.num(p.x, p.y, 'miss', C_MISS)
        return True

    def random_step(self, mon):
        m = self.map
        dx, dy = random.choice(D8)
        nx, ny = mon.x + dx, mon.y + dy
        if not m.inb(nx, ny) or not D.TILES[m.tile(nx, ny)].walk or self.occupied(m, nx, ny):
            return
        if mon.is_npc and not mon.stay and m.kind == 'town' and m.tile(nx, ny) == FLOOR and random.random() < .7:
            return
        mon.x, mon.y = nx, ny

    def step_toward(self, mon):
        m, p, dist = self.map, self.player, self.dist
        cd = dist[mon.y * m.w + mon.x]
        best, bd = None, cd if cd >= 0 else 9999
        opts = D8[:]
        random.shuffle(opts)
        for dx, dy in opts:
            nx, ny = mon.x + dx, mon.y + dy
            if not m.inb(nx, ny):
                continue
            di = dist[ny * m.w + nx]
            if di < 0 or di >= bd or self.occupied(m, nx, ny):
                continue
            bd, best = di, (nx, ny)
        if not best and cd < 0:
            sx = (p.x > mon.x) - (p.x < mon.x)
            sy = (p.y > mon.y) - (p.y < mon.y)
            nx, ny = mon.x + sx, mon.y + sy
            if m.inb(nx, ny) and (D.TILES[m.tile(nx, ny)].walk or D.TILES[m.tile(nx, ny)].door) and not self.occupied(m, nx, ny):
                best = (nx, ny)
        if not best:
            return
        if m.tile(*best) == DOOR:
            m.set(best[0], best[1], ODOOR)
            return
        mon.x, mon.y = best

    def mon_turn(self, mon, df):
        m, p, d = self.map, self.player, mon.tpl
        seen = self.visible(mon.x, mon.y)
        dist = cheb(mon.x, mon.y, p.x, p.y)
        if d['summon'] and seen and mon.summons < 6 and random.random() < .13:
            spots = W.free_around(self, m, mon.x, mon.y, 1)
            if spots:
                x, y = random.choice(spots)
                o = make_monster(self, d['summon'], x, y, max(1, mon.lvl - 2))
                o.awake = True
                m.mons.append(o)
                mon.summons += 1
                self.flash([(x, y)], (196, 134, 255), '*', .2)
                self.msg('Morvenna beckons, and a skeleton claws its way out of the ground!' if mon.k == 'lich'
                         else 'The Rat King squeals. A rat scurries out of the dark!', 'bad')
                return
        if d['nova'] and dist <= 2 and random.random() < .22:
            self.flash(ring(mon.x, mon.y, 2), (159, 216, 255), '*', .26)
            self.msg('Morvenna unleashes a wave of grave-cold!', 'bad')
            self.hurt(random.randint(*mon.dmg) * .8, mon.name)
            return
        if d['leap'] and seen and 2 <= dist <= 5 and random.random() < .3:
            sp = W.free_around(self, m, p.x, p.y, 1)
            if sp:
                x, y = min(sp, key=lambda c: cheb(c[0], c[1], mon.x, mon.y))
                self.flash(line(mon.x, mon.y, x, y), (232, 128, 60), '*', .2)
                mon.x, mon.y = x, y
                self.msg('Grolm leaps at you with a roar!', 'bad')
                if random.random() < self.mon_hit_chance(mon, df):
                    self.hurt(random.randint(*mon.dmg) * 1.4, mon.name)
                return
        if (d['ranged'] or d['caster']) and seen and 2 <= dist <= 7 and random.random() < (.45 if d['caster'] else .6):
            if self.mon_shoot(mon, d['caster'], df):
                return
        if d['erratic'] and random.random() < .5:
            self.random_step(mon)
            return
        esc = next((o for o in m.mons if o.role == 'escort'), None)
        if esc and cheb(mon.x, mon.y, esc.x, esc.y) < dist:
            if cheb(mon.x, mon.y, esc.x, esc.y) <= 1:
                if random.random() < .7:
                    dmg = random.randint(*mon.dmg)
                    esc.hp -= dmg
                    self.num(esc.x, esc.y, f'-{dmg}', C_HURT)
                    if esc.hp <= 0:
                        m.mons.remove(esc)
                        self.msg(f'{mon.the()[0].upper() + mon.the()[1:]} destroys your caravan!', 'bad')
                        MS.on_escort_killed(self)
                    elif esc.hp < esc.maxhp * .4 and random.random() < .3:
                        self.msg('Your caravan is under heavy attack!', 'bad')
            else:
                best = None
                for ddx, ddy in D8:
                    nx, ny = mon.x + ddx, mon.y + ddy
                    if m.inb(nx, ny) and D.TILES[m.tile(nx, ny)].walk and not self.occupied(m, nx, ny):
                        dd = cheb(nx, ny, esc.x, esc.y)
                        if best is None or dd < best[0]:
                            best = (dd, nx, ny)
                if best:
                    mon.x, mon.y = best[1], best[2]
            return
        if dist <= 1:
            self.mon_attack(mon, df)
            return
        self.step_toward(mon)

    def monsters_act(self):
        m, p = self.map, self.player
        self.compute_dist()
        df = self.stats()['def']
        for mon in m.mons[:]:
            if self.dead or self.flags.get('lich') and self.request == ('win',):
                return
            if mon not in m.mons:
                continue
            if mon.is_npc:
                if not mon.stay and random.random() < .3:
                    self.random_step(mon)
                continue
            d = mon.tpl
            if d['regen'] and mon.hp < mon.maxhp:
                mon.hp = min(mon.maxhp, mon.hp + -(-mon.maxhp // 40))
            if mon.hold > 0:
                mon.hold -= 1
                continue
            if not mon.awake:
                if self.visible(mon.x, mon.y) and random.random() < (.5 if p.cls == 'rogue' else .7):
                    mon.awake = True
                    self.wake_pack(mon)
                else:
                    continue
            if d['slow'] and self.turn % 2 == 0:
                continue
            acts = 1 + (1 if d['fast'] and self.turn % 2 == 0 else 0) + (1 if 'Fast' in mon.mods else 0)
            while acts > 0 and not self.dead and mon in m.mons:
                acts -= 1
                self.mon_turn(mon, df)

    def end_turn(self, cost, quiet=False):
        p = self.player
        for _ in range(cost):
            self.turn += 1
            s = self.stats()
            if self.turn % 4 == 0 and p.life < s['max_life']:
                p.life = min(s['max_life'], p.life + 1 + s['max_life'] // 60 + s['regen'])
            if self.turn % 2 == 0 and p.mana < s['max_mana']:
                p.mana = min(s['max_mana'], p.mana + 1 + s['max_mana'] // 40)
            if p.poison:
                p.life -= p.poison[1]
                if not quiet:
                    self.num(p.x, p.y, f'-{p.poison[1]}', (143, 220, 90))
                if p.life <= 0:
                    self.die('poison')
                    return
                p.poison[0] -= 1
                if p.poison[0] <= 0:
                    p.poison = None
                    self.msg('The poison wears off.', 'good')
        WA.tick(self, cost)
        if self.day != self.last_day:
            for _ in range(self.day - self.last_day):
                ECO.daily(self)
                WA.daily(self)
                MS.daily(self)
            self.last_day = self.day
        self.compute_fov()
        if self.map.kind != 'over':
            self.monsters_act()
        elif self.cur == 'over':
            wd = WA.hostile_adjacent(self)
            if wd:
                self.start_encounter(wd)
        if self.dead:
            return
        if self.turn - self.last_save > 40 and self.request is None:
            self.request = ('save',)

    def die(self, cause):
        if self.dead:
            return
        self.dead = True
        self.player.life = 0
        self.cause = cause
        self.msg('You have died.', 'bad')

    # ------------------------------------------------------------ skills
    def nearest_target(self, max_d, need_line):
        p = self.player
        lst = [o for o in self.visible_hostiles() if cheb(o.x, o.y, p.x, p.y) <= max_d]
        if need_line:
            lst = [o for o in lst if self.line_clear(p.x, p.y, o.x, o.y)]
        if not lst:
            return None
        for o in lst:
            if o.id == p.last_target:
                return o
        return min(lst, key=lambda o: cheb(o.x, o.y, p.x, p.y))

    def use_skill(self, n):
        p = self.player
        sks = D.SKILLS[p.cls]
        if n >= len(sks):
            return 0
        sk = sks[n]
        r = p.skills.get(sk.id, 0)
        m = self.map
        if not r:
            self.msg(f'{sk.name} unlocks at level {sk.lvl}.' if p.lvl < sk.lvl else f'Spend a skill point on {sk.name} first (C).')
            return 0
        if m.kind in ('over', 'town'):
            self.msg('Save your skills for the dungeons.')
            return 0
        if p.mana < sk.cost:
            self.msg(f'Not enough mana for {sk.name} ({sk.cost} needed).', 'bad')
            return 0
        ene = self.stats()['ene']

        def area(rad):
            return [o for o in self.visible_hostiles() if cheb(o.x, o.y, p.x, p.y) <= rad]

        def landing(t):
            sp = [c for c in W.free_around(self, m, t.x, t.y, 1) if self.visible(*c)]
            return sp

        sid = sk.id
        if sid == 'cleave':
            t = area(1)
            if not t:
                self.msg('No enemies next to you.')
                return 0
            self.flash(ring(p.x, p.y, 1), (255, 106, 74), '/', .16)
            for o in t:
                self.weapon_strike(o, 100 + r * 15)
        elif sid == 'warcry':
            t = area(3)
            if not t:
                self.msg('No enemies in range.')
                return 0
            self.flash(ring(p.x, p.y, 3) + ring(p.x, p.y, 2), (242, 196, 67), '!', .22)
            self.msg('You let out a terrifying war cry!', 'info')
            for o in t:
                o.hold = 2
                self.damage_mon(o, 6 + r * 5, col=(242, 196, 67))
        elif sid == 'leap':
            t = self.nearest_target(6, False)
            if not t:
                self.msg('No enemy within leaping range.')
                return 0
            if cheb(t.x, t.y, p.x, p.y) > 1:
                sp = landing(t)
                if not sp:
                    self.msg('There is no room to land.')
                    return 0
                dst = min(sp, key=lambda c: cheb(c[0], c[1], p.x, p.y))
                self.flash(line(p.x, p.y, *dst), (255, 106, 74), '*', .18)
                p.x, p.y = dst
            self.flash(ring(p.x, p.y, 1), (255, 106, 74), '*', .22)
            self.shake()
            for o in area(1):
                self.weapon_strike(o, 150 + r * 25)
        elif sid == 'knives':
            t = self.nearest_target(8, True)
            if not t:
                self.msg('No target in sight.')
                return 0
            p.last_target = t.id
            self.flash(line(p.x, p.y, t.x, t.y)[:-1], (216, 224, 240), '-', .15)
            self.weapon_strike(t, 85 + r * 15)
        elif sid == 'fan':
            t = area(2)
            if not t:
                self.msg('No enemies within reach.')
                return 0
            self.flash(ring(p.x, p.y, 2) + ring(p.x, p.y, 1), (216, 224, 240), 'x', .18)
            for o in t:
                self.weapon_strike(o, 70 + r * 15)
        elif sid == 'shadow':
            t = self.nearest_target(8, False)
            if not t:
                self.msg('No target in sight.')
                return 0
            sp = landing(t)
            if sp:
                dst = max(sp, key=lambda c: cheb(c[0], c[1], p.x, p.y))
                self.flash([(p.x, p.y)], (154, 124, 255), '%', .2)
                p.x, p.y = dst
            elif cheb(t.x, t.y, p.x, p.y) > 1:
                self.msg('No shadows to step into.')
                return 0
            p.last_target = t.id
            self.weapon_strike(t, 200 + r * 30, True)
        elif sid == 'firebolt':
            t = self.nearest_target(9, True)
            if not t:
                self.msg('No target in sight.')
                return 0
            p.last_target = t.id
            self.flash(line(p.x, p.y, t.x, t.y)[:-1], (255, 122, 44), '*', .17)
            self.damage_mon(t, random.randint(3 + r * 3, 7 + r * 4) + ene // 4, col=(255, 176, 112))
        elif sid == 'nova':
            t = area(2)
            self.flash(ring(p.x, p.y, 2) + ring(p.x, p.y, 1), (159, 216, 255), '*', .24)
            if not t:
                self.msg('The frost dissipates harmlessly.')
            for o in t:
                o.hold = 3
                self.damage_mon(o, random.randint(2 + r * 2, 5 + r * 3) + ene // 6, col=(191, 232, 255))
        elif sid == 'chain':
            t = self.nearest_target(9, True)
            if not t:
                self.msg('No target in sight.')
                return 0
            p.last_target = t.id
            hit = set()
            frm = (p.x, p.y)
            jumps = 3 + r // 2
            while t and jumps > 0:
                jumps -= 1
                self.flash(line(frm[0], frm[1], t.x, t.y), (242, 240, 122), '~', .2)
                hit.add(t.id)
                frm = (t.x, t.y)
                self.damage_mon(t, random.randint(5 + r * 4, 11 + r * 5) + ene // 3, col=(255, 250, 154))
                cand = [o for o in self.visible_hostiles() if o.id not in hit and cheb(o.x, o.y, *frm) <= 4]
                t = min(cand, key=lambda o: cheb(o.x, o.y, *frm)) if cand else None
        p.mana -= sk.cost
        return 1

    # ------------------------------------------------------------ automation
    def explore_step(self):
        m, p = self.map, self.player
        w, n = m.w, m.w * m.h
        want = set()
        for it in m.items:
            if self.visible(it.x, it.y) and (it.k in ('gold', 'orb') or (not it.dropped and (it.k in ('potion', 'scroll') or (it.k == 'gear' and it.rar != 'normal')))):
                want.add(it.y * w + it.x)
        npc = {(o.x, o.y) for o in m.mons if o.is_npc}
        par = [-2] * n
        start = p.y * w + p.x
        par[start] = -1
        q = [start]
        h = 0
        tiles, seen = m.t, m.seen
        while h < len(q):
            c = q[h]
            h += 1
            x, y = c % w, c // w
            if c != start:
                if c in want or any(m.inb(x + dx, y + dy) and not seen[(y + dy) * w + x + dx] for dx, dy in D8):
                    cur = c
                    while par[cur] != start:
                        cur = par[cur]
                    return (cur % w - p.x, cur // w - p.y)
            for dx, dy in D8:
                nx, ny = x + dx, y + dy
                if not (0 <= nx < w and 0 <= ny < m.h):
                    continue
                ni = ny * w + nx
                if par[ni] != -2 or not seen[ni]:
                    continue
                tt = D.TILES[tiles[ni]]
                if not (tt.walk or tt.door) or (nx, ny) in npc:
                    continue
                par[ni] = c
                q.append(ni)
        return None

    def explore(self):
        m = self.map
        if m.kind == 'over':
            self.msg('Press T to travel across the vale.')
            return
        if m.kind == 'town':
            self.msg('Nothing to explore in town. Press T to travel.')
            return
        n, key = 0, self.cur
        while n < 400 and not self.dead and self.cur == key and self.request not in (('win',),):
            if self.hostile_visible():
                if not n:
                    self.msg('Enemies nearby!', 'bad')
                break
            st = self.explore_step()
            if not st:
                if not n:
                    self.msg('This level is fully explored.')
                break
            used = self.try_move(*st)
            if not used:
                break
            self.end_turn(used, True)
            n += 1
        if n and self.hostile_visible():
            self.msg('You spot enemies!', 'bad')

    def run(self, dx, dy):
        key, n = self.cur, 0
        while n < 40 and not self.dead and self.cur == key:
            used = self.try_move(dx, dy)
            if not used:
                break
            self.end_turn(used, True)
            n += 1
            m, p = self.map, self.player
            t = m.tile(p.x, p.y)
            if self.hostile_visible() or any(i.x == p.x and i.y == p.y for i in m.items) or t in (DOWN, UP, TOWN, ENTR):
                break
            if self.request and self.request[0] != 'save':
                break

    def rest(self):
        p, n = self.player, 0
        while n < 300 and not self.dead:
            s = self.stats()
            if self.hostile_visible():
                if not n:
                    self.msg('You cannot rest with enemies in sight.', 'bad')
                break
            if p.life >= s['max_life'] and p.mana >= s['max_mana'] and not p.poison:
                if not n:
                    self.msg('You are already fully rested.')
                break
            self.end_turn(1, True)
            n += 1
        if n:
            self.msg(f'You rest for {n} turns.')

    def travel_to(self, kind, ref):
        """Walk to a settlement ('s', id) or dungeon ('d', id), preferring roads."""
        if self.map.kind == 'town':
            self.leave_to_over()
        if self.cur != 'over':
            self.msg('You can only travel across the open land.')
            return
        w = self.world
        obj = w.settlements[ref] if kind == 's' else w.dungeons[ref]
        tgt = (obj.x, obj.y)
        p = self.player
        path = WO.dijkstra_path(self.map, (p.x, p.y), tgt, lambda t: D.TILES[t].cost if D.TILES[t].walk else None)
        if not path:
            self.msg('You cannot find a way there.')
            return
        self.msg(f'You set out for {obj.name}.')
        for x, y in path:
            if self.dead or self.cur != 'over':
                break
            near = [wd for wd in w.wanderers if wd.hostile and wd.cooldown == 0 and self.visible(wd.x, wd.y)
                    and cheb(wd.x, wd.y, p.x, p.y) <= 7]
            if near:
                self.msg(f'You spot {near[0].name[0].lower() + near[0].name[1:]} nearby and stop.', 'bad')
                break
            used = self.try_move(x - p.x, y - p.y)
            if not used:
                break
            self.end_turn(used, True)
            if self.request and self.request[0] not in ('save',):
                break
        if self.cur == 'over' and (p.x, p.y) == tgt:
            self.over_step()

    def known_settlement(self, s):
        om = self.maps['over']
        return bool(om.seen[s.y * om.w + s.x])

    def known_dungeon(self, d):
        om = self.maps['over']
        return bool(om.seen[d.y * om.w + d.x])

    # ------------------------------------------------------------ talking
    def talk(self, npc):
        f, p = self.flags, self.player
        here = self.here
        role = npc.role
        if role in ('shop', 'market', 'inn', 'stables'):
            self.request = (role, here.id if here else 0)
            return
        if role == 'healer':
            s = self.stats()
            if p.life >= s['max_life'] and p.mana >= s['max_mana'] and not p.poison:
                self.request = ('dialog', npc.name, '"You look well, child. Come back when the world has had its way with you."')
                return
            p.life, p.mana, p.poison = s['max_life'], s['max_mana'], None
            self.num(p.x, p.y, 'healed', C_HEAL, True)
            self.request = ('dialog', npc.name, '"Hold still." She lays her hands on your wounds. You are fully restored.')
            return
        if role == 'elder':
            if not f.get('met_elder'):
                f['met_elder'] = True
                text = (f'"Welcome, traveller. Thornfield lives in fear.\n\n'
                        f'To the {self.dir_to("rat")} lie the Rat Warrens, where a monstrous Rat King sends his brood to plunder our stores. '
                        f'To the {self.dir_to("mine")}, at the foot of the mountains, the exiled dwarf Grolm the Digger has seized the old mine.\n\n'
                        f'But the true evil is Morvenna the Undying. From her crypt to the {self.dir_to("crypt")} she raises the dead. '
                        f'Destroy her and the curse on this land will be broken.\n\n'
                        f'Start with the rats, grow stronger. And if you need coin, the board at the inn always has work, '
                        f'and the traders pay well for goods hauled between towns."')
                om = self.maps['over']
                for k in ('rat', 'mine', 'crypt'):
                    d = self.world.dungeons[k]
                    om.seen[d.y * om.w + d.x] = 1
            elif f.get('ratking') and not f.get('reward_rat'):
                f['reward_rat'] = True
                p.gold += 100
                it = make_gear(self, random.choice([k for k, b in D.BASES.items() if b['lvl'] <= p.lvl + 1]), 'rare', p.lvl + 1)
                self.add_to_inv(it)
                text = '"The Rat King is dead? Then we eat this winter! Take this: a hundred gold and something from my old adventuring days."'
                self.msg(f'You receive 100 gold and {it.name}.', 'rare')
            elif f.get('grolm') and not f.get('reward_grolm'):
                f['reward_grolm'] = True
                p.gold += 250
                it = make_gear(self, random.choice([k for k, b in D.BASES.items() if b['lvl'] <= p.lvl + 1]), 'rare', p.lvl + 2)
                self.add_to_inv(it)
                text = '"Grolm defeated! The mine is ours again. Here, 250 gold and a treasure worthy of you. Only Morvenna remains."'
                self.msg(f'You receive 250 gold and {it.name}.', 'rare')
            elif not f.get('ratking'):
                text = f'"The Rat Warrens lie to the {self.dir_to("rat")}. They are marked on your map (M)."'
            elif not f.get('grolm'):
                text = f'"The Lost Mine lies to the {self.dir_to("mine")}. Grolm leaps at his enemies. Wear good armor."'
            else:
                text = f'"Morvenna waits to the {self.dir_to("crypt")}. Do not fight her at range; her bolts will find you anyway."'
            self.request = ('dialog', 'Elder Berend', text)
            return
        if role == 'dog':
            self.msg('The dog wags its tail and sniffs your boots.')
            return
        self.msg(f'{npc.name} says: "{self.rumor()}"', 'info')

    def rumor(self):
        w = self.world
        r = random.random()
        if r < .45:
            s = random.choice(w.settlements)
            g = random.choice(s.demand)
            return f"They say {s.name} pays well for {D.GOODS[g]['name'].lower()}."
        if r < .65:
            s = random.choice(w.settlements)
            g = random.choice(s.produce)
            return f"{D.GOODS[g]['name']} is cheap in {s.name}, they make plenty of it there."
        if r < .8:
            ev = [s for s in w.settlements if s.event]
            if ev:
                s = random.choice(ev)
                return D.EVENTS[s.event[0]]['text'].format(town=s.name)
        if r < .9:
            sd = [d for d in w.dungeons.values() if not d.main]
            d = random.choice(sd)
            om = self.maps['over']
            om.seen[d.y * om.w + d.x] = 1
            here = self.here or w.settlements[0]
            return f'There is an old place called {d.name} to the {dir_name(d.x - here.x, d.y - here.y)}. I marked it on your map.'
        return random.choice(D.RUMORS)


# ---------------------------------------------------------------- saving
def save_path():
    import sys
    if getattr(sys, 'frozen', False):
        # standalone executable: keep the save next to the .exe, not in the temp unpack folder
        return os.path.join(os.path.dirname(os.path.abspath(sys.executable)), 'savegame.dat')
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'savegame.dat')


def save_game(game):
    if game is None or game.dead:
        return
    game.last_save = game.turn
    try:
        with open(save_path() + '.tmp', 'wb') as f:
            pickle.dump(game, f)
        os.replace(save_path() + '.tmp', save_path())
    except OSError:
        pass


def load_game():
    try:
        with open(save_path(), 'rb') as f:
            g = pickle.load(f)
        if getattr(g, 'version', 0) == SAVE_VERSION and not g.dead:
            g.events, g.request = [], None
            g.compute_fov()
            return g
    except Exception:
        pass
    return None


def delete_save():
    try:
        os.remove(save_path())
    except OSError:
        pass
