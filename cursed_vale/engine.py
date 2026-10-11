"""Game state and rules: movement, combat, monster AI, skills, loot, travel."""
import os
import pickle
import random

from . import data as D
from . import economy as ECO
from . import fov
from . import skills as SK
from . import missions as MS
from . import wanderers as WA
from . import war as WAR
from . import towns as TW
from . import events as EV
from . import evils as EVL
from . import factions as FA
from . import races as RC
from . import crime as CR
from .money import fmt, purse
from . import world as WO
from . import worldgen as W
from .data import (FLOOR, DOOR, ODOOR, DOWN, UP, WATER, MOUNTAIN, TOWN, ENTR, WELL, ROAD, CITY)
from .entities import Item, Player, make_gear, make_unique, random_gear, make_monster
from .worldgen import D8, cheb

SAVE_VERSION = 9

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
    return int(60 * lvl ** 2.35)


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


LORE_RANKS = [(0, 'Glimpsed'), (3, 'Familiar'), (10, 'Studied'), (25, 'Hunter'), (50, 'Slayer'), (100, 'Bane')]


def lore_rank(kills):
    r = 0
    for i, (n, _name) in enumerate(LORE_RANKS):
        if kills >= n:
            r = i
    return r


COIN_CARRIERS = {'kobold', 'goblin', 'gobarcher', 'orc', 'ogre', 'cultist', 'skeleton'}


class Game:
    def __init__(self, name, hardcore=True, seed=None, race='human', gender='other'):
        self.version = SAVE_VERSION
        self.seed = seed if seed is not None else random.randrange(1, 10 ** 9)
        random.seed(self.seed)
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
        self.pending = None     # an open choice (travel events, places, travellers)
        self.encounter_poi = None
        self.bestiary = {}      # monster key -> [seen, kills]

        self.corpses = []
        self.turn = D.DAY_LEN * 7 // 24      # the story starts at seven in the morning
        p = self.player = Player(name or 'Wanderer', hardcore)
        p.race, p.gender = race, gender
        for st, v in RC.RACES[race]['stats'].items():
            setattr(p, st, getattr(p, st) + v)
        p.x = p.y = -5
        self.cur = 'none'

        def gear(bk, equip=True):
            it = make_gear(self, bk, 'normal', 1)
            self.add_to_inv(it)
            if equip:
                p.eq[it.slot] = it.id

        gear('shortsword')
        gear('quilted')
        gear('shortbow', False)
        self.add_to_inv(Item(self.new_id(), 'potion', 'hp', 2))
        self.add_to_inv(Item(self.new_id(), 'potion', 'mp', 1))
        self.add_to_inv(Item(self.new_id(), 'scroll', 'tp', 1))
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
        # you only know the land around Thornfield; the rest you learn from people and signposts
        for y in range(home.y - 7, home.y + 8):
            for x in range(home.x - 11, home.x + 12):
                if over.inb(x, y):
                    over.seen[y * over.w + x] = 1
        rat = world.dungeons['rat']
        over.seen[rat.y * over.w + rat.x] = 1
        self.home = 0
        EVL.setup_monsters(world)
        EVL.update(self, announce=False)
        # how the factions see you depends on who you are
        p.rep = {f: fd['start'] + (RC.relation(fd.get('race'), race) if f != 'cult' else 0) for f, fd in D.FACTIONS.items()}
        self.hook()
        self.cur = home.map_key
        self.maps[self.cur] = TW.gen_settlement_map(self, home)
        m = self.maps[self.cur]
        # you wake on the floor of the temple, with no memory of how you got here
        p.x, p.y = m.entry[0] + 2, m.entry[1]
        priest = next((o for o in m.mons if o.role == 'healer'), None)
        if priest:
            spot = W.free_around(self, m, priest.x, priest.y, 1)
            if spot:
                p.x, p.y = spot[0]
        p.life = max(1, p.life * 2 // 3)
        self.shops = {0: W.gen_shop(self)}
        WA.populate(self)
        MS.refresh_board(self, home)
        self.msg('You wake on a cold stone floor. Candles. Incense. A temple.', 'gold')
        self.msg(f'You remember your name, {p.name}, and nothing else.', 'gold')
        self.msg('Talk to the priestess beside you. Press ? or F1 for help.', 'info')
        self.compute_fov()

    # ------------------------------------------------------------ basics
    def hook(self):
        """Install this world's factions, boss names and price rules (after creating or loading)."""
        FA.install(self.world.factions)
        EVL.setup_monsters(self.world)
        ECO.faction_rep = lambda st: self.player.rep.get(st.faction, 0)
        ECO.race_factor = lambda st: RC.price_factor(self, getattr(st, 'race', 'human'))

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
        if m is not None and m.kind == 'town' and getattr(m, 'sid', None) is not None:
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
        st['pending'] = None
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
        s = dict(str=p.str, dex=p.dex, vit=p.vit, ene=p.ene, life=0, mana=0, dmg_flat=0, ed=0, hit=0,
                 leech=0, crit=5, regen=0, armor=0, dr=0)
        for slot in D.SLOTS:
            it = self.eq_item(slot)
            if not it:
                continue
            if it.identified:
                for st, v in it.aff:
                    if st != 'edef':
                        s[st] = s.get(st, 0) + v
            for st, v in getattr(it, 'curse', ()):
                if st != 'edef':
                    s[st] = s.get(st, 0) - v
            b = D.BASES[it.base]
            s['mana'] += b.get('mana', 0)
            s['hit'] += b.get('hit', 0)
            s['armor'] += it.armor_value()
        buff_dmg = 0
        for k, v, _t, _src in p.buffs:
            if k == 'def':
                s['armor'] += v
            elif k == 'regen':
                s['regen'] += v
            elif k == 'dr':
                s['dr'] = max(s['dr'], v)
            elif k == 'dmg':
                buff_dmg += v
        s['max_life'] = int(20 + s['vit'] * 2 + (p.lvl - 1) * 3 + s['life'])
        s['max_mana'] = int(10 + s['ene'] * 2 + (p.lvl - 1) * 2 + s['mana'])
        w = self.eq_item('weapon')
        bd = w.dmg if w else (1, 3)
        line = SK.WEAPON_LINE.get(w.base) if w else None
        wr = p.disc[line][0] if line else 0
        dexy = line in ('daggers', 'archery')
        mul = 1 + (s['dex'] if dexy else s['str']) / 100 + s['ed'] / 100 + wr * .015 + buff_dmg / 100
        if getattr(p, 'race', '') == 'orc' and not (w and D.BASES[w.base].get('ranged')):
            mul += .1
        s['dmg'] = (max(1, int(bd[0] * mul + s['dmg_flat'])), max(1, int(bd[1] * mul + s['dmg_flat'])))
        s['ar'] = 20 + s['dex'] * 2 + p.lvl * 4 + s['hit'] + wr * 2
        s['def'] = s['armor'] + s['dex'] // 2
        s['line'] = line
        s['ranged'] = bool(w and D.BASES[w.base].get('ranged'))
        return s

    def clamp_vitals(self):
        s, p = self.stats(), self.player
        p.life = min(p.life, s['max_life'])
        p.mana = min(p.mana, s['max_mana'])

    # ------------------------------------------------------------ vision
    def compute_fov(self):
        m, p = self.map, self.player
        r = m.radius
        if m.kind in ('over', 'town') and TW.is_night(self):
            r = 5 if m.kind == 'over' else 9
            if self.player.race in ('elf', 'goblin'):
                r += 2
        if m.kind == 'dungeon' and p.race == 'goblin':
            r += 2
        self.vis = fov.compute(m, p.x, p.y, r)
        if m.kind not in ('over', 'town'):
            for o in m.mons:
                if not o.is_npc and o.k not in self.bestiary and self.visible(o.x, o.y):
                    self.bestiary[o.k] = [self.day, 0]
                    self.msg(f"New bestiary entry: {D.MONSTERS[o.k]['name']}. (V)", 'info')

    def say(self, npc, line):
        self.msg(f'{npc.name}: "{line}"', 'talk')
        self.events.append(('speech', npc.x, npc.y, line))

    def crime(self, severity, what, witnessed=1.0):
        return CR.commit(self, severity, what, witnessed)

    def say_text(self, name, line):
        self.msg(f'{name}: "{line}"', 'talk')
        self.request = ('dialog', name, f'"{line}"')

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
            if depth == dg.depth and getattr(dg, 'poi', False):
                from .entities import make_tome
                c = W.rand_free(self, self.maps[key], lambda t: t == FLOOR)
                if c:
                    tm = make_tome(self, dg.base + depth + 2)
                    tm.x, tm.y = c
                    self.maps[key].items.append(tm)
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
        lair = next((e for e in self.world.evils if e.did == did and not e.known), None)
        if first and depth == dg.depth:
            self.msg('An evil presence fills the air. This is the deepest level.', 'bad')
        self.compute_fov()
        self.request = ('save',)
        if lair:
            EVL.learn(self, lair)

    def leave_to_over(self):
        p = self.player
        m = self.map
        if m.kind == 'wild':
            self.resolve_encounter()
            self.maps.pop('wild', None)
        elif getattr(m, 'hid', None) is not None:
            h = self.world.holds[m.hid]
            self.over_pos = (h.x, h.y)
            if getattr(m, 'stale', False):
                self.maps.pop(m.key, None)
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
        if self.encounter_poi is not None:
            poi = self.world.pois[self.encounter_poi]
            self.encounter_poi = None
            if m and not any(not o.is_npc for o in m.mons):
                poi.ready_day = 10 ** 9
                self.msg(f'The {poi.name.lower()} is cleared.', 'good')
        if not wd:
            return
        alive = [o for o in m.mons if not o.is_npc] if m else []
        if not alive:
            self.world.wanderers.remove(wd)
            if getattr(wd, 'robbed', False):
                CR.caravan_plundered(self, wd)
            if wd.kind == 'lawmen':
                CR.commit(self, 6, 'killing the law', 1.0)
            if wd.kind == 'hunt':
                self.msg(f"{self.world.evils[wd.evil].name}'s hunters fall. Somewhere far away, something howls in rage.", 'unique')
            else:
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
            self.maps[s.map_key] = TW.gen_settlement_map(self, s)
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
        MS.place_clients(self, sid, m)
        self.compute_fov()
        self.request = ('save',)
        CR.at_gate(self, s)

    def enter_hold(self, hid):
        p = self.player
        h = self.world.holds[hid]
        hostile = WAR.is_hostile(self, h.faction)
        if self.cur == 'over':
            self.over_pos = (p.x, p.y)
        m = self.maps.get(h.map_key)
        if m is None or (m.kind == 'siege') != hostile:
            m = TW.gen_hold_map(self, h, hostile)
            self.maps[h.map_key] = m
        self.cur = h.map_key
        p.x, p.y = m.entry[0] + 1, m.entry[1]
        if hostile:
            self.msg(f'You storm the gate of {h.title}! Kill its commander to take the fortress.', 'bad')
        else:
            key = f'h{hid}'
            self.shops[key] = W.gen_shop(self, True)
            self.msg(f'You enter {h.title}.', 'info')
            MS.on_enter_hold(self, hid)
        self.compute_fov()
        self.request = ('save',)

    def start_encounter(self, wd=None, terrain=None, lvl=1, keys=None, elite=0):
        p = self.player
        self.over_pos = (p.x, p.y)
        if terrain is None:
            terrain = self.maps['over'].tile(p.x, p.y)
        if wd:
            g = wd.group
            lvl, keys, elite, leader = g['lvl'], g['keys'], g['elite'], g.get('leader')
            faction = g.get('faction')
            self.encounter = wd.id
        else:
            leader, faction = None, None
            self.encounter = None
        self.cur = 'wild'
        p.x = p.y = -5
        w = W.gen_wild(self, terrain, lvl, keys, elite, leader, faction)
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
            if m.kind in ('town', 'wild', 'siege'):
                if m.kind in ('wild', 'siege') and any(not o.is_npc and o.awake and cheb(o.x, o.y, p.x, p.y) <= 1 for o in m.mons):
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
                if wd.kind == 'traveler':
                    EV.talk_traveller(self, wd)
                    return 0
                if wd.kind == 'caravan':
                    EV.talk_caravan(self, wd)
                    return 0
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
            elif t == D.SIGNPOST:
                self.read_signpost()
            elif t == D.CHEST:
                W.open_chest(self, nx, ny)
                return 1
            elif t == D.CHEST_OPEN:
                self.msg('The chest is empty.')
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
        if any(i.x == p.x and i.y == p.y for i in m.items):
            self.auto_pickup()
        s = self.world.settlement_at(p.x, p.y)
        if s:
            kind = 'city' if s.is_city else 'village'
            self.msg(f'You stand at the gates of {s.name} ({kind}). Press > or Enter to go in.', 'info')
            return 10
        if t == ENTR:
            d = self.world.dungeon_at(p.x, p.y)
            self.msg(f"You stand at the entrance of {d.name}. Press > or Enter to descend.", 'info')
            return 10
        h = self.world.hold_at(p.x, p.y)
        if h:
            f = D.FACTIONS[h.faction]
            if WAR.is_hostile(self, h.faction):
                self.msg(f"{h.title} ({f['short']}) bars its gates against you. Press > to storm it.", 'bad')
            else:
                self.msg(f"You stand before {h.title} ({f['short']}). Press > or Enter to go in.", 'info')
            return 10
        poi = EV.poi_at(self, p.x, p.y)
        if poi:
            EV.reveal(self, poi)
            EV.on_poi(self, poi)
            return D.TILES[t].cost
        cost = D.TILES[t].cost
        w = self.world
        reg = w.region_at(p.x, p.y)
        off = w.off_road(p.x, p.y)
        evil = EVL.taint_at(self, p.x, p.y)
        night = TW.is_night(self) or bool(evil)
        cost += EVL.DIVE_COST.get(evil.d['taint'], 0) if evil else 0
        if t == ROAD:
            chance = .003 * (2 if night else 1)
        else:
            chance = min(.11, .012 + off * .004) * cost / 10 * (1.6 if night else 1)
        if p.race in ('halfling', 'goblin'):
            chance *= .75
        if cheb(p.x, p.y, *self._home_xy()) <= 4:
            chance = 0
        if random.random() < chance:
            lvl = w.danger_at(p.x, p.y) + (1 if night else 0)
            keys = EVL.wild_keys(self, p.x, p.y, lvl) or WA.wild_pack(reg.biome, lvl, night)
            r = random.random()
            elite = 1 if r < .08 + off * .004 else 0
            self.start_encounter(None, t, lvl, keys, elite)
            return 1
        if cheb(p.x, p.y, *self._home_xy()) > 4:
            EV.maybe_event(self, t == ROAD)
        return cost

    def _home_xy(self):
        h = self.world.settlements[0]
        return h.x, h.y

    def auto_pickup(self):
        m, p = self.map, self.player
        for it in [i for i in m.items if i.x == p.x and i.y == p.y]:
            if it.k == 'gold':
                p.gold += it.n
                self.num(p.x, p.y, '+' + fmt(it.n, True), C_GOLD)
                self.msg(f'You pick up {fmt(it.n)}.', 'gold')
            elif it.k == 'corpse':
                pl = it.payload
                left = []
                for o in pl['items']:
                    if not self.add_to_inv(o):
                        left.append(o)
                for g, q in pl['cargo'].items():
                    p.cargo[g] = p.cargo.get(g, 0) + q
                for g, c in pl['cost'].items():
                    p.cost_basis.setdefault(g, c)
                p.gold += pl['gold']
                self.corpses = [c for c in self.corpses if c[1] != it.id]
                self.msg(f"You recover your belongings and {fmt(pl['gold'])} from your body.", 'good')
                if left:
                    pl['items'], pl['cargo'], pl['gold'] = left, {}, 0
                    self.msg('Your bag is full; some items stay with your body.', 'bad')
                    continue
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
                ok, why = WAR.can_enter(self, s)
                if not ok:
                    self.msg(why, 'bad')
                    return 0
                self.enter_town(s.id)
                return 1
            h = self.world.hold_at(p.x, p.y)
            if h:
                self.enter_hold(h.id)
                return 1
            if t == ENTR:
                self.enter_dungeon(self.dungeon_at(p.x, p.y), 1, 'up')
                return 1
            poi = EV.poi_at(self, p.x, p.y)
            if poi and poi.kind == 'ruin':
                self.enter_dungeon(poi.did, 1, 'up')
                return 1
            if poi:
                EV.on_poi(self, poi)
                return 0
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

    def stuck(self, slot):
        """A cursed item in this slot that cannot be taken off."""
        cur = self.eq_item(slot)
        if cur and cur.cursed:
            cur.curse_known = True
            self.msg(f'{cur.display_name()} is cursed and will not leave you. A priest in a temple can lift the curse.', 'bad')
            return True
        return False

    def equip(self, it):
        p = self.player
        if it.req > p.lvl:
            self.msg(f'You need to be level {it.req} to use that.', 'bad')
            return False
        if self.stuck(it.slot):
            return False
        p.eq[it.slot] = it.id
        self.clamp_vitals()
        self.msg(f'You equip {it.display_name()}.', it.rar)
        if it.cursed:
            it.curse_known = True
            self.msg('A cold grip closes around you. The item is cursed!', 'bad')
            self.shake()
        return True

    def unequip(self, slot):
        if self.stuck(slot):
            return
        if self.player.eq.pop(slot, None) is not None:
            self.clamp_vitals()
            self.msg('You remove the item.')

    def fish(self):
        from . import lifeskills as LS
        return LS.fish(self)

    def eat(self, it):
        from . import lifeskills as LS
        return LS.eat(self, it)

    def read_tome(self, it):
        if SK.learn(self, it.t):
            self.remove_one(it)
            return 1
        return 0

    def identify_all(self, dry=False):
        its = [it for it in self.player.inv if it.k == 'gear' and not it.identified]
        cost = sum(it.id_cost() for it in its)
        if dry:
            return len(its), cost
        if not its:
            self.msg('You have nothing that needs identifying.')
            return
        if self.player.gold < cost:
            self.msg(f'Identifying everything costs {fmt(cost)}. You cannot afford it.', 'bad')
            return
        self.player.gold -= cost
        for it in its:
            it.ided = True
            if it.cursed:
                it.curse_known = True
            self.msg(f'Identified: {it.display_name()}.', it.rar)
        if any(it.cursed for it in its):
            self.msg('Something you carry is cursed. Do not wear it, or have a priest lift the curse.', 'bad')
        self.clamp_vitals()

    def uncurse_all(self, dry=False):
        its = [it for it in self.player.inv if it.k == 'gear' and it.cursed and (it.curse_known or self.is_equipped(it))]
        cost = sum(it.uncurse_cost() for it in its)
        if dry:
            return len(its), cost
        if not its:
            self.msg('You carry nothing known to be cursed.')
            return
        if self.player.gold < cost:
            self.msg(f'Lifting the curses costs {fmt(cost)}. You cannot afford it.', 'bad')
            return
        self.player.gold -= cost
        for it in its:
            it.curse = []
            it.curse_known = False
            self.msg(f'The curse on {it.display_name()} is lifted.', 'good')
        self.clamp_vitals()

    def drop(self, it):
        p = self.player
        if self.is_equipped(it) and it.cursed:
            self.stuck(it.slot)
            return 0
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
        pass

    def buy_supply(self, i):
        k, t = [('potion', 'hp'), ('potion', 'mp'), ('scroll', 'tp'), ('tool', 'rod')][i]
        if k == 'tool' and any(x.k == 'tool' for x in self.player.inv):
            self.msg('You already have a fishing pole.')
            return
        it = Item(self.new_id(), k, t)
        p = self.player
        if p.gold < it.value():
            return
        if not self.add_to_inv(it):
            self.msg('Your bag is full.', 'bad')
            return
        p.gold -= it.value()
        self.msg(f"You buy a {it.display_name()}.", 'gold')

    def buy_gear(self, i, key=None):
        shop = self.shops.get(self.home if key is None else key, [])
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
        self.msg(f'You sell {name} for {fmt(v)}.', 'gold')

    # ------------------------------------------------------------ combat
    def wake_pack(self, mon):
        if mon.pack is None:
            return
        for o in self.map.mons:
            if o.pack == mon.pack:
                o.awake = True

    def damage_mon(self, mon, dmg, crit=False, col=C_DMG, weapon=False):
        p = self.player
        if 'vuln' in mon.effects:
            dmg *= 1.25
        dmg *= 1 + .03 * self.lore(mon.k)
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
        if s['ranged']:
            s['dmg'] = (max(1, s['dmg'][0] // 2), max(1, s['dmg'][1] // 2))
        if random.random() >= clamp(.95 * s['ar'] / (s['ar'] + mon.df), .25, .95):
            self.num(mon.x, mon.y, 'miss', C_MISS)
            self.msg(f'You miss {mon.the()}.')
            mon.awake = True
            self.wake_pack(mon)
            return
        crit = random.random() < s['crit'] / 100
        if s['line'] and not s['ranged']:
            SK.gain(self, s['line'], 1)
        if not self.damage_mon(mon, random.randint(*s['dmg']), crit, weapon=True):
            self.msg(f"You {'critically ' if crit else ''}hit {mon.the()}.")

    def weapon_strike(self, mon, pct, force_crit=False, ranged=False):
        s = self.stats()
        crit = force_crit or random.random() < s['crit'] / 100
        return self.damage_mon(mon, random.randint(*s['dmg']) * pct / 100, crit, weapon=True)

    def hurt(self, dmg, src):
        p = self.player
        s = self.stats()
        dmg = max(1, round(dmg * (1 - s['dr'] / 100)))
        p.life -= dmg
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
        if not mon.tpl.get('tags', '').startswith('crypt') and mon.k not in ('ghost', 'wraith', 'skeleton', 'skarcher'):
            from .dress import add_blood
            add_blood(m, mon.x, mon.y, 2 if (mon.elite or mon.is_boss) else random.randint(0, 1))
        if not mon.is_npc:
            e = self.bestiary.setdefault(mon.k, [self.day, 0])
            before = lore_rank(e[1])
            e[1] += 1
            if lore_rank(e[1]) > before:
                self.msg(f"Your knowledge of the {D.MONSTERS[mon.k]['name'].lower()} grows: {LORE_RANKS[lore_rank(e[1])][1]}. (V)", 'gold')
        special = mon.elite or mon.is_boss
        self.msg(f"{mon.the()[0].upper() + mon.the()[1:]} {'is slain!' if mon.is_boss or mon.elite == 2 else 'dies.'}", 'gold' if special else '')
        self.gain_xp(max(1, round(mon.xp * clamp(1 - (p.lvl - mon.lvl - 1) * .15, .05, 1))))
        if 'Fire Enchanted' in mon.mods:
            self.flash(ring(mon.x, mon.y, 1), (255, 122, 44), '*', .26)
            self.msg(f'{mon.name} explodes in flames!', 'bad')
            if cheb(mon.x, mon.y, p.x, p.y) <= 1:
                self.hurt(mon.dmg[1] * .8, mon.name)
        self.drop_loot(mon)
        if mon.faction:
            WAR.on_kill(self, mon)
        if getattr(mon, 'commander', False) and getattr(m, 'hid', None) is not None:
            self.capture_hold(m.hid)
        if mon.k == 'ratking':
            self.flags['ratking'] = True
            self.msg('The rats scatter in every direction. Elder Berend will want to hear of this.', 'gold')
        elif mon.k == 'grolm':
            self.flags['grolm'] = True
            self.msg('The Lost Mine falls silent.', 'gold')
        if mon.tpl.get('boss'):
            EVL.on_kill(self, mon)

    def capture_hold(self, hid):
        h = self.world.holds[hid]
        old = h.faction
        cands = [f for f in D.FACTIONS[old]['enemies'] if f != 'cult']
        new = max(cands, key=lambda f: self.player.rep[f]) if cands else 'crown'
        old_title = h.title
        WAR.capture(self, h, new, 8)
        self.map.stale = True
        self.msg(f'{old_title} has fallen! You hand it to {D.FACTIONS[new]["name"]}. It is now {h.title}.', 'unique')
        WAR.change_rep(self, old, -20)
        WAR.change_rep(self, new, 20)
        MS.on_capture(self, hid)

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
        n = 4 if boss else random.randint(2, 3) if mon.elite == 2 else random.randint(1, 2) if mon.elite == 1 else (1 if random.random() < .2 else 0)
        if boss:
            u = next((u for u in D.UNIQUES if u.get('boss') == mon.k), None)
            if u:
                it = make_unique(self, u)
                self.spill(m, mon.x, mon.y, it)
                self.announce(it)
            n = 3
        for _ in range(n):
            it = random_gear(self, lvl, boost)
            if boost > 2 and it.rar == 'normal':
                up = make_gear(self, it.base, 'magic', lvl)
                it.rar, it.aff, it.name, it.ided = up.rar, up.aff, up.name, False
            self.spill(m, mon.x, mon.y, it)
            self.announce(it)
        if random.random() < (1 if boss else .3 if mon.elite == 2 else .12 if mon.elite == 1 else .012):
            from .entities import make_tome
            t = make_tome(self, lvl)
            self.spill(m, mon.x, mon.y, t)
            self.msg('A skill tome drops!', 'gold')
        special = mon.elite or boss
        # beasts carry no coin; people and the clever monsters do, and not much
        d = mon.tpl
        carrier = d['ch'] in '@hK' or 'faction' in d['tags'] or mon.k in COIN_CARRIERS
        if mon.k == 'merchant':
            self.spill(m, mon.x, mon.y, Item(self.new_id(), 'gold', 'gold', purse(lvl, 18)))
        elif carrier and random.random() < (1 if boss else .7 if mon.elite else .25):
            self.spill(m, mon.x, mon.y, Item(self.new_id(), 'gold', 'gold', purse(lvl, 8 if boss else 2.5 if mon.elite else 1)))
        if special or random.random() < .16:
            self.spill(m, mon.x, mon.y, Item(self.new_id(), 'orb', 'orb'))
        if random.random() < (.6 if special else .1):
            t = 'rejuv' if random.random() < .12 else 'hp' if random.random() < .6 else 'mp'
            self.spill(m, mon.x, mon.y, Item(self.new_id(), 'potion', t))

    def announce(self, it):
        if it.rar == 'unique':
            self.msg('A unique item drops!', 'unique')
        elif it.rar == 'rare':
            self.msg('A rare item drops.', 'rare')

    def gain_xp(self, n):
        p = self.player
        n = max(1, round(n * RC.RACES[p.race]['xp']))
        p.xp += n
        while p.xp >= xp_for(p.lvl):
            p.lvl += 1
            p.stat_pts += D.LEVEL_STAT_POINTS
            s = self.stats()
            p.life, p.mana = s['max_life'], s['max_mana']
            self.num(p.x, p.y, 'LEVEL UP', C_GOLD, True)
            self.shake()
            self.msg(f'You reach level {p.lvl}! Press C to spend {D.LEVEL_STAT_POINTS} attribute points.', 'gold')
            EVL.update(self)

    def mon_hit_chance(self, mon, df):
        return clamp(.9 * mon.hit_r / (mon.hit_r + df * .6) - .02 * self.lore(mon.k), .12, .9)

    def lore(self, k):
        e = self.bestiary.get(k)
        return lore_rank(e[1]) if e else 0

    def mon_attack(self, mon, df):
        p = self.player
        if random.random() < self.mon_hit_chance(mon, df):
            dmg = random.randint(*mon.dmg)
            if 'weaken' in mon.effects:
                dmg = round(dmg * .7)
            if 'Vampiric' in mon.mods:
                mon.hp = min(mon.maxhp, mon.hp + round(dmg / 2))
            if mon.tpl['leech']:
                mon.hp = min(mon.maxhp, mon.hp + round(dmg / 3))
            self.msg(f'{mon.the()[0].upper() + mon.the()[1:]} hits you.', 'bad')
            if mon.tpl['poison'] and random.random() < .4:
                p.poison = [3 if getattr(p, 'race', '') == 'dwarf' else 6, max(1, round(mon.lvl / 2))]
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
            self.msg(f"{name}'s {mon.tpl.get('bolt', 'firebolt') if spell else 'arrow'} hits you.", 'bad')
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
                self.msg(d.get('summon_msg', '{name} squeals. A rat scurries out of the dark!').format(name=mon.name), 'bad')
                return
        if d['nova'] and dist <= 2 and random.random() < .22:
            self.flash(ring(mon.x, mon.y, 2), d.get('nova_col', (159, 216, 255)), '*', .26)
            self.msg(d.get('nova_msg', '{name} unleashes a wave of grave-cold!').format(name=mon.name), 'bad')
            self.hurt(random.randint(*mon.dmg) * .8, mon.name)
            return
        if d['leap'] and seen and 2 <= dist <= 5 and random.random() < .3:
            sp = W.free_around(self, m, p.x, p.y, 1)
            if sp:
                x, y = min(sp, key=lambda c: cheb(c[0], c[1], mon.x, mon.y))
                self.flash(line(mon.x, mon.y, x, y), (232, 128, 60), '*', .2)
                mon.x, mon.y = x, y
                self.msg(d.get('leap_msg', '{name} leaps at you with a roar!').format(name=mon.name), 'bad')
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
        key = self.cur
        self.compute_dist()
        df = self.stats()['def']
        for mon in m.mons[:]:
            if self.dead or self.cur != key or self.request == ('win',):
                return
            if mon not in m.mons:
                continue
            if mon.is_npc:
                if not mon.stay and not hasattr(mon, 'work_pos') and random.random() < .3:
                    self.random_step(mon)
                continue
            d = mon.tpl
            if d['regen'] and mon.hp < mon.maxhp:
                mon.hp = min(mon.maxhp, mon.hp + -(-mon.maxhp // 40))
            if mon.effects:
                for k in list(mon.effects):
                    t, v = mon.effects[k]
                    if k in ('burn', 'bleed', 'poison') and v:
                        col = {'burn': (255, 140, 60), 'bleed': (220, 60, 60), 'poison': (143, 220, 90)}[k]
                        mon.hp -= v
                        self.num(mon.x, mon.y, str(v), col)
                        if mon.hp <= 0:
                            self.kill(mon)
                            break
                    if t <= 1:
                        del mon.effects[k]
                    else:
                        mon.effects[k][0] = t - 1
                if mon not in m.mons:
                    continue
            if mon.hold > 0:
                mon.hold -= 1
                if mon.hold == 0:
                    mon.frozen = False
                continue
            if not mon.awake:
                if self.visible(mon.x, mon.y) and random.random() < .65:
                    mon.awake = True
                    self.wake_pack(mon)
                else:
                    continue
            if d['slow'] and self.turn % 2 == 0:
                continue
            acts = 1 + (1 if d['fast'] and self.turn % 2 == 0 else 0) + (1 if 'Fast' in mon.mods else 0)
            while acts > 0 and not self.dead and mon in m.mons and self.cur == key:
                acts -= 1
                self.mon_turn(mon, df)

    def end_turn(self, cost, quiet=False):
        p = self.player
        for _ in range(cost):
            self.turn += 1
            if p.cooldowns:
                for k in list(p.cooldowns):
                    p.cooldowns[k] -= 1
                    if p.cooldowns[k] <= 0:
                        del p.cooldowns[k]
            if p.buffs:
                for b in p.buffs:
                    b[2] -= 1
                ended = [b for b in p.buffs if b[2] <= 0]
                p.buffs = [b for b in p.buffs if b[2] > 0]
                for b in ended:
                    self.msg(f'{b[3]} wears off.')
            s = self.stats()
            if self.turn % 4 == 0 and p.life < s['max_life']:
                p.life = min(s['max_life'], p.life + 1 + s['max_life'] // 60)
            if s['regen'] and p.life < s['max_life']:
                p.life = min(s['max_life'], p.life + s['regen'])
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
                WAR.daily(self)
                MS.daily(self)
                EVL.daily(self)
                CR.daily(self)
            self.last_day = self.day
        EVL.whisper(self)
        self.compute_fov()
        if self.map.kind == 'town':
            TW.live(self, self.map)
        if self.map.kind != 'over':
            self.monsters_act()
        elif self.cur == 'over':
            EV.discover(self)
            EVL.sense(self)
            wd = WA.hostile_adjacent(self) if not self.pending else None
            if wd:
                self.start_encounter(wd)
        if self.dead:
            return
        if self.turn - self.last_save > 40 and self.request is None:
            self.request = ('save',)

    def die(self, cause):
        if self.dead:
            return
        p = self.player
        if not p.hardcore:
            self.respawn(cause)
            return
        self.dead = True
        p.life = 0
        self.cause = cause
        self.msg('You have died.', 'bad')

    def respawn(self, cause):
        """Softcore death: wake in the nearest temple. Your backpack, cargo and gold stay with your body."""
        p = self.player
        p.deaths += 1
        m = self.map
        if m.kind == 'wild':
            self.resolve_encounter()
            self.maps.pop('wild', None)
            key, cx, cy = 'over', self.over_pos[0], self.over_pos[1]
        else:
            key, cx, cy = self.cur, p.x, p.y
        if m.kind == 'town':
            key = None   # dying in town: nothing is lost
        corpse = None
        if key:
            corpse = Item(self.new_id(), 'corpse', 'corpse')
            corpse.name = f'your body (day {self.day})'
            corpse.payload = dict(items=[it for it in p.inv if not self.is_equipped(it) and it.k != 'quest'],
                                  cargo=dict(p.cargo), cost=dict(p.cost_basis), gold=p.gold)
            corpse.x, corpse.y = cx, cy
            self.maps[key].items.append(corpse)
            self.corpses.append((key, corpse.id))
            p.inv = [it for it in p.inv if self.is_equipped(it) or it.k == 'quest']
            p.cargo, p.cost_basis, p.gold = {}, {}, 0
        here = self.world.settlements[self.home] if self.home is not None else None
        ox, oy = self.over_pos if self.cur != 'over' else (p.x, p.y)
        temples = [st for st in self.world.settlements if 'temple' in st.services]
        dest = min(temples, key=lambda st: cheb(st.x, st.y, ox, oy)) if temples else here
        s = self.stats()
        p.life, p.mana = max(1, s['max_life'] // 2), s['max_mana'] // 2
        p.poison = p.burn = None
        p.buffs = []
        self.cur = 'over'
        p.x, p.y = dest.x, dest.y
        self.enter_town(dest.id)
        self.msg(f'You were slain by {cause}... and wake on the cold floor of the temple in {dest.name}.', 'bad')
        if corpse:
            where = 'in the wilds' if key == 'over' else self.maps[key].name
            self.msg(f'Your backpack, cargo and gold lie with your body {where}. Go and get them back.', 'bad')
        self.request = ('save',)

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
        return SK.use(self, n)

    def fire(self):
        """Basic bow shot at the nearest enemy in sight."""
        s = self.stats()
        if not s['ranged']:
            self.msg('You need a bow equipped to shoot. Walk into enemies to fight in melee.')
            return 0
        if self.map.kind in ('over', 'town'):
            self.msg('There is nothing to shoot here.')
            return 0
        t = self.nearest_target(8, True)
        if not t:
            self.msg('No target in sight.')
            return 0
        p = self.player
        p.last_target = t.id
        self.flash(self.path_to(t)[:-1], (216, 208, 176), '-', .15)
        if random.random() >= clamp(.95 * s['ar'] / (s['ar'] + t.df), .25, .95):
            self.num(t.x, t.y, 'miss', C_MISS)
            t.awake = True
            self.wake_pack(t)
            return 1
        crit = random.random() < s['crit'] / 100
        self.damage_mon(t, random.randint(*s['dmg']), crit, weapon=True)
        SK.gain(self, 'archery', 1)
        return 1

    def path_to(self, mon):
        p = self.player
        return line(p.x, p.y, mon.x, mon.y)

    def cells_between(self, a, b):
        return line(a[0], a[1], b[0], b[1])

    def opaque(self, x, y):
        return D.TILES[self.map.tile(x, y)].opaque

    def heal(self, n, show=False):
        p = self.player
        s = self.stats()
        before = p.life
        p.life = min(s['max_life'], p.life + max(0, n))
        if show and p.life > before:
            self.num(p.x, p.y, f'+{p.life - before}', C_HEAL, True)

    # ------------------------------------------------------------ automation
    def explore_step(self):
        m, p = self.map, self.player
        w, n = m.w, m.w * m.h
        want = set()
        for it in m.items:
            if self.visible(it.x, it.y) and (it.k in ('gold', 'orb') or (not it.dropped and (it.k in ('potion', 'scroll', 'tome') or (it.k == 'gear' and it.rar != 'normal')))):
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
        for _ in self.explore_iter():
            pass

    def explore_iter(self):
        """Auto-explore one step at a time (a generator), so the UI can show every step."""
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
            if self.request and self.request[0] != 'save':
                break
            yield n
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
        for _ in self.travel_iter(kind, ref):
            pass

    def travel_iter(self, kind, ref):
        """Walk to a settlement ('s', id) or dungeon ('d', id), preferring roads. One step per yield."""
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
            if self.cur == 'over' and (p.x, p.y) != tgt:
                yield 1
        if self.cur == 'over' and (p.x, p.y) == tgt:
            self.over_step()

    def reveal_route(self, a, b):
        """Mark the road from settlement a to settlement b, and b itself, on the map."""
        om = self.maps['over']
        path = WA.road_path(self, a, b) or []
        for x, y in path:
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if om.inb(x + dx, y + dy):
                        om.seen[(y + dy) * om.w + x + dx] = 1
        s = self.world.settlements[b]
        om.seen[s.y * om.w + s.x] = 1
        return len(path)

    def reveal_place(self, x, y, r=3):
        om = self.maps['over']
        for yy in range(y - r, y + r + 1):
            for xx in range(x - r, x + r + 1):
                if om.inb(xx, yy):
                    om.seen[yy * om.w + xx] = 1

    def read_signpost(self):
        here = self.here
        if not here:
            return
        w = self.world
        nbrs = [b if a == here.id else a for a, b in getattr(w, 'road_edges', []) if here.id in (a, b)]
        if not nbrs:
            self.request = ('dialog', 'Signpost', 'The signpost is weathered blank.')
            return
        lines = []
        new = 0
        for b in nbrs:
            s = w.settlements[b]
            if not self.known_settlement(s):
                new += 1
            n = self.reveal_route(here.id, b)
            lines.append(f'{dir_name(s.x - here.x, s.y - here.y).capitalize():10} {s.name} ({n} leagues)')
        self.request = ('dialog', f'Signpost of {here.name}', 'The arms of the signpost point down the roads:\n\n' + '\n'.join(lines) +
                        ('\n\nYou mark the roads on your map.' if new else ''))
        if new:
            self.msg(f'You learn of {new} new place{"s" if new > 1 else ""} and the roads to them.', 'info')

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
        m = self.map
        hid = getattr(m, 'hid', None)
        if role == 'castellan':
            self.request = ('castellan', hid)
            return
        if role == 'shop':
            self.request = ('shop', f'h{hid}' if hid is not None else (here.id if here else 0))
            return
        if role in ('market', 'inn', 'stables'):
            self.request = (role, here.id if here else 0)
            return
        if role == 'guard':
            h = self.world.holds[hid] if hid is not None else None
            f = h.faction if h else (here.faction if here else 'crown')
            if here is not None and here.rep < 0:
                self.say(npc, random.choice(['I have my eye on you.', 'One wrong move, stranger.',
                                             f'They say you are trouble. Not in {here.name}, you are not.']))
                return
            wanted = CR.wanted_in(self)
            if wanted and random.random() < .4:
                st = random.choice(wanted)
                self.say(npc, f'Heard there is a price on someone\'s head over in {st.name}. Looked a bit like you, they say.')
                return
            self.say(npc, random.choice([f"Long live the {D.FACTIONS[f]['short']}.", 'Keep your weapons sheathed.',
                                         f"You are {WAR.standing(self.player.rep.get(f, 0)).lower()} among us.", self.rumor()]))
            return
        if role == 'healer':
            if here is not None and here.id == 0 and not f.get('met_priest'):
                f['met_priest'] = True
                s = self.stats()
                p.life = s['max_life']
                p.gold += 520
                self.request = ('dialog', npc.name,
                                f'"Easy now, easy. You are safe. You are in the temple of Thornfield.\n\n'
                                f'A farmer found you three days ago, lying in the ditch by the north road. No horse, no purse, '
                                f'no one with you. Just your weapons, and a name you kept repeating: {p.name}.\n\n'
                                f'You do not remember? No... I thought not. It may come back in time. It may not.\n\n'
                                f'Here, a few coppers from the poor box. Elder Berend asked to see you when you woke; '
                                f'his house is on the green. And {RC.address(self)}... whoever you were before, '
                                f'you can be someone new now."')
                return
            self.request = ('temple', npc.name)
            return
        if role == 'elder':
            if not f.get('met_elder'):
                f['met_elder'] = True
                text = (f'"So you are the stranger Sister Ilse found by the road. No memory, she says. Well, {RC.address(self)}, '
                        f'Thornfield could use a pair of hands, whoever you were.\n\n'
                        f'To the {self.dir_to("rat")} lie the Rat Warrens, where a monstrous Rat King sends his brood to plunder our stores. '
                        f'To the {self.dir_to("mine")}, at the foot of the mountains, the exiled dwarf Grolm the Digger has seized the old mine.\n\n'
                        f'Deal with either and you will have friends here. If it is coin you need, the board at the inn always has work, '
                        f'and the traders pay for goods hauled between towns. The signpost by the road tells you where the roads go."')
                om = self.maps['over']
                for k in ('rat', 'mine'):
                    d = self.world.dungeons[k]
                    om.seen[d.y * om.w + d.x] = 1
            elif f.get('ratking') and not f.get('reward_rat'):
                f['reward_rat'] = True
                p.gold += 4000
                it = make_gear(self, random.choice([k for k, b in D.BASES.items() if b['lvl'] <= p.lvl + 1]), 'rare', p.lvl + 1)
                self.add_to_inv(it)
                from .entities import make_tome
                tome = make_tome(self, 6)
                self.add_to_inv(tome)
                text = ('"The Rat King is dead? Then we eat this winter! Take this: forty silver, something from my old '
                        'adventuring days, and a book I never could make sense of. Perhaps you can."')
                self.msg(f'You receive 40 silver, {it.display_name()} and the {tome.display_name()}.', 'rare')
            elif f.get('grolm') and not f.get('reward_grolm'):
                f['reward_grolm'] = True
                p.gold += 10000
                it = make_gear(self, random.choice([k for k, b in D.BASES.items() if b['lvl'] <= p.lvl + 1]), 'rare', p.lvl + 2)
                self.add_to_inv(it)
                text = '"Grolm defeated! The mine is ours again. Here: a gold coin, the first you have held, I wager. And a treasure worthy of you."'
                self.msg(f'You receive 1 gold and {it.display_name()}.', 'rare')
            elif not f.get('ratking'):
                text = f'"The Rat Warrens lie to the {self.dir_to("rat")}. They are marked on your map (M)."'
            elif not f.get('grolm'):
                text = f'"The Lost Mine lies to the {self.dir_to("mine")}. Grolm leaps at his enemies. Wear good armor."'
            else:
                known = [e for e in EVL.active(self) if e.known]
                if known:
                    e = max(known, key=lambda q: q.lvl)
                    text = (f'"{e.name} grows bolder every season. Its lair lies to the {self.dir_to(e.did)}. '
                            f'Nobody would blame you for staying away. Nobody would forget you if you did not."')
                elif any(e.defeated for e in self.world.evils):
                    text = '"You have done this land a great service. Thornfield will remember."'
                else:
                    text = f'"You have done well, {RC.address(self)}. The vale is wide; go and see it. And listen to what people say on the road."'
            self.request = ('dialog', 'Elder Berend', text)
            return
        if role == 'client':
            MS.client_talk(self, npc)
            return
        if role == 'dog':
            self.msg('The dog wags its tail and sniffs your boots.')
            return
        line = random.choice(TW.BARKS.get(getattr(npc, 'job', 'any'), TW.BARKS['any'])) if random.random() < .3 else self.rumor()
        self.say(npc, line)

    def rumor(self):
        w = self.world
        r = random.random()
        p = self.player
        here = self.here
        ox, oy = (here.x, here.y) if here else ((p.x, p.y) if self.cur == 'over' else self.over_pos)
        unknown = [s for s in w.settlements if not self.known_settlement(s) and cheb(s.x, s.y, ox, oy) < 60]
        if unknown and r < .35:
            s = min(unknown, key=lambda q: cheb(q.x, q.y, ox, oy) + random.randint(0, 15))
            self.reveal_place(s.x, s.y, 2)
            kind = 'city' if s.is_city else 'village'
            f = D.FACTIONS[s.faction]['short']
            return (f"There is a {kind} called {s.name} to the {dir_name(s.x - ox, s.y - oy)}, "
                    f"{cheb(s.x, s.y, ox, oy)} leagues or so. {f} land. I marked it on your map.")
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
        if r < .85 and EVL.rumor(self):
            return EVL.rumor(self)
        if r < .9:
            sd = [d for d in w.dungeons.values() if not d.main]
            d = random.choice(sd)
            om = self.maps['over']
            om.seen[d.y * om.w + d.x] = 1
            for poi in w.pois:
                if poi.did == d.id:
                    EV.reveal(self, poi)
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
            g.hook()
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
