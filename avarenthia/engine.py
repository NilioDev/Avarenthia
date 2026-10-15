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
from . import calendar as CAL
from . import crime as CR
from . import hunger as HU
from . import gods as GD
from . import lore as LORE
from . import lifeskills as LS
from . import ai as AI
from . import weather as WX
from . import dress as DR
from . import sites as ST
from . import guilds as GU
from . import news as NW
from . import mercs as MC
from .money import fmt, purse
from . import world as WO
from . import worldgen as W
from .data import (FLOOR, DOOR, ODOOR, DOWN, UP, WATER, MOUNTAIN, TOWN, ENTR, WELL, ROAD, CITY)
from .entities import Item, Player, make_gear, make_unique, random_gear, make_monster
from .worldgen import D8, cheb

SAVE_VERSION = 16

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


SUPPLIES = [('potion', 'hp'), ('potion', 'mp'), ('scroll', 'tp'), ('tool', 'rod'), ('tool', 'kit'), ('tool', 'tent'), ('food', 'bread'),
            ('food', 'ration'), ('food', 'barley'), ('food', 'honey')]
INV_MAX = 32
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

        # you wake with nothing: whoever left you in the ditch took your sword and shield
        gear('quilted')
        self.add_to_inv(Item(self.new_id(), 'potion', 'hp', 2))
        self.add_to_inv(HU.make_food(self, 'bread', 2))
        s = self.stats()
        p.life, p.mana = s['max_life'], s['max_mana']

        over, world = WO.gen_world(self)
        self.maps['over'] = over
        self.world = world
        for st in world.settlements:
            st.services = WO.settlement_services(st)
        GU.setup(world)
        ECO.init_markets(world)
        home = world.settlements[0]
        self.over_pos = (home.x, home.y)
        # you know nothing of the land: only where Thornfield lies, a short walk from the temple
        over.seen[home.y * over.w + home.x] = 1
        self.home = 0
        EVL.setup_monsters(world)
        EVL.update(self, announce=False)
        # how the factions see you depends on who you are
        p.rep = {f: fd['start'] + (RC.relation(fd.get('race'), race) if f != 'cult' else 0) for f, fd in D.FACTIONS.items()}
        self.hook()
        # you wake on the floor of a temple near Thornfield, with no memory of how you got here
        ts = world.sites[world.start_temple] if getattr(world, 'start_temple', None) is not None else None
        if ts:
            self.over_pos = (ts.x, ts.y)
            self.cur = ts.map_key
            self.maps[self.cur] = ST.gen_site_map(self, ts)
            over.seen[ts.y * over.w + ts.x] = 1
            self.mark_visit('site', ts.id)
        else:
            self.cur = home.map_key
            self.maps[self.cur] = TW.gen_settlement_map(self, home)
        m = self.maps[self.cur]
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
        from . import foraging as FG
        FG.GAME = self
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
        if len(inv) >= INV_MAX:
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
                 leech=0, crit=5, regen=0, armor=0, dr=0, res_fire=0, res_cold=0, res_light=0, res_poison=0, res_all=0,
                 fire_dmg=0, cold_dmg=0, light_dmg=0, sight=0, undead=0, thorns=0, lpk=0, mpk=0, mf=0)
        sets = {}
        gear_dr = 0
        for slot in D.SLOTS:
            it = self.eq_item(slot)
            if not it or (getattr(it, 'mdur', 0) and it.dur <= 0):      # broken gear does nothing
                continue
            if getattr(it, 'set_key', None) and it.identified:
                sets[it.set_key] = sets.get(it.set_key, 0) + 1
            if it.identified:
                for st, v in it.aff:
                    if st == 'dr':
                        gear_dr += v
                    elif st != 'edef':
                        s[st] = s.get(st, 0) + v
            for st, v in getattr(it, 'curse', ()):
                if st != 'edef':
                    s[st] = s.get(st, 0) - v
            b = D.BASES[it.base]
            s['mana'] += b.get('mana', 0)
            s['hit'] += b.get('hit', 0)
            s['armor'] += it.armor_value()
        for k, n in sets.items():          # set bonuses: two pieces, and the whole set
            st = D.SETS[k]
            for bonus in ([st['partial']] if n >= 2 else []) + ([st['full']] if n >= len(st['pieces']) else []):
                for st_, v in bonus.items():
                    if st_ == 'dr':
                        gear_dr += v
                    else:
                        s[st_] = s.get(st_, 0) + v
        s['sets'] = sets
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
            elif k == 'frail':                      # back from the dead, and not yet yourself
                buff_dmg -= v
                s['frail'] = v
        if getattr(p, 'food', 500) < HU.WEAK:
            buff_dmg -= 15
        GD.apply(self, s)
        s['dr'] = min(60, s['dr'] + gear_dr)
        if getattr(p, 'race', '') == 'dwarf':
            s['res_poison'] += 20                    # dwarves shrug off venom
        for r in ('res_fire', 'res_cold', 'res_light', 'res_poison'):
            s[r] = min(D.RES_CAP, s[r] + s['res_all'])
        s['max_life'] = int(20 + s['vit'] * 2 + (p.lvl - 1) * 3 + s['life'])
        if s.get('frail'):
            s['max_life'] = max(5, round(s['max_life'] * (1 - s['frail'] / 100)))
        if getattr(p, 'toll', 0):                    # what Morrak has taken
            s['max_life'] = max(10, round(s['max_life'] * (1 - p.toll / 100)))
        s['max_mana'] = int(10 + s['ene'] * 2 + (p.lvl - 1) * 2 + s['mana'])
        w = self.eq_item('weapon')
        if w and getattr(w, 'mdur', 0) and w.dur <= 0:
            w = None
        line = SK.WEAPON_LINE.get(w.base) if w else 'unarmed'
        wr = (p.disc[line][0] + s.get('skill_' + line, 0)) if line in p.disc else 0
        bd = w.dmg if w else (1 + wr // 6, 3 + wr // 3)      # fists harden with practice
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
    def _see_wonders(self):
        """The first time one of the world's great sights comes into view, say so."""
        seen = self.__dict__.setdefault('wonders_seen', set())
        m = self.map
        for name, x, y in getattr(self.world, 'wonders', ()):
            if name in seen:
                continue
            if any(m.inb(x + dx, y + dy) and self.vis[(y + dy) * m.w + x + dx] for dx in (-3, 0, 3) for dy in (-3, 0, 3)):
                seen.add(name)
                text = LORE.WONDERS.get(name, ('You see ' + name + '.',))[0]
                self.msg(f'{name}. {text}', 'info')

    def compute_fov(self):
        m, p = self.map, self.player
        r = m.radius
        if m.kind in ('over', 'town') and TW.is_night(self) and not getattr(m, 'underground', False):
            r = 5 if m.kind == 'over' else 9
            if self.player.race in ('elf', 'goblin'):
                r += 2
        if m.kind in ('town', 'wild', 'siege') and not getattr(m, 'underground', False):
            r = WX.sight(self, r)
        if m.kind == 'dungeon' and p.race == 'goblin':
            r += 2
        if m.kind != 'over':
            r += self.stats().get('sight', 0)
        if m.kind == 'over':
            last = getattr(self, '_over_last', None)
            if last and last != (p.x, p.y):
                self.came_from = last                # which way you walked into a town
            self._over_last = (p.x, p.y)
            self.vis = fov.compute(m, p.x, p.y, self.over_sight(), dense={D.FOREST})
            self._see_wonders()
        elif m.kind == 'town' and getattr(m, 'lights', None) and TW.town_ambient(self, m) > .3:
            # at night you see as far as the lamps light the streets
            near = fov.compute(m, p.x, p.y, r)
            far = fov.cells(m, p.x, p.y, 45)
            lm = DR.light_map(m)
            amb = m.ambient
            self.vis = bytearray(1 if (near[i] or (far[i] and lm[i][0] > amb[0] + .18)) else 0 for i in range(len(far)))
        else:
            self.vis = fov.compute(m, p.x, p.y, r)
        MC.sync(self)
        if m.kind not in ('over', 'town'):
            for o in m.mons:
                if not o.is_npc and o.k not in self.bestiary and self.visible(o.x, o.y) and not getattr(o, 'lurk', False):
                    self.bestiary[o.k] = [self.day, 0]
                    self.msg(f"New bestiary entry: {D.MONSTERS[o.k]['name']}. (V)", 'info')

    def over_sight(self):
        """How far you see in the open land: far from the hills, little in the woods or the marsh, less at night."""
        p, m = self.player, self.map
        t = m.tile(p.x, p.y)
        r = {D.HILLS: 6, D.FOREST: 2, D.SWAMP: 3}.get(t, 4)
        if TW.is_night(self):
            r = max(1, r // 2)
        if p.race in ('elf', 'goblin') and TW.is_night(self):
            r += 2
        if p.race == 'elf' and t == D.FOREST:
            r += 2
        return WX.sight(self, r)

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
        return [o for o in self.map.mons if not o.is_npc and self.visible(o.x, o.y) and not getattr(o, 'lurk', False)]

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
        self.dist = W.bfs(m, p.x, p.y, lambda t: D.TILES[t].walk or D.TILES[t].door, maxd=45)

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
        self.mark_visit('d', did)
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
            if getattr(dg, 'varnish', False):
                from .hidden import vault_loot
                vault_loot(self, self.maps[key], dg)
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
        elif getattr(m, 'site', None) is not None:
            st = self.world.sites[m.site]
            self.over_pos = (st.x, st.y)
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
                CR.commit(self, 10, 'killing the law', 1.0)
            if wd.kind == 'hunt':
                self.msg(f"{self.world.evils[wd.evil].name}'s hunters fall. Somewhere far away, something howls in rage.", 'unique')
            else:
                self.msg(f'You have dealt with {wd.name[0].lower() + wd.name[1:]}.', 'good')
            MS.on_group_defeated(self, wd)
        else:
            wd.cooldown = 4

    def enter_town(self, sid, from_portal=False):
        self.mark_visit('s', sid)
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
            ex, ey = m.entry
            exits = getattr(m, 'exits', None)
            came = getattr(self, 'came_from', None)
            if exits and came:                       # come in by the road you were walking on
                dx, dy = came[0] - s.x, came[1] - s.y
                cx, cy = getattr(m, 'centre', (m.w // 2, m.h // 2))
                ex, ey = max(exits, key=lambda e: (e[0] - cx) * dx + (e[1] - cy) * dy)[:2]
            p.x, p.y = ex, ey
            for nx, ny in ((ex + 1, ey), (ex - 1, ey), (ex, ey + 1), (ex, ey - 1)):
                if m.inb(nx, ny) and D.TILES[m.tile(nx, ny)].walk and not (0 < ex < m.w - 1 and 0 < ey < m.h - 1):
                    if min(nx, ny, m.w - 1 - nx, m.h - 1 - ny) > min(ex, ey, m.w - 1 - ex, m.h - 1 - ey):
                        p.x, p.y = nx, ny            # one step in from the edge
                        break
        if 'shop' in s.services:
            self.shops[sid] = W.gen_shop(self, s.is_city)
        MS.refresh_board(self, s)
        esc = MS.escort_wanderer(self)
        if esc:
            esc.x, esc.y = s.x, s.y
        self.msg(f'You enter {s.name}.', 'info')
        MC.restock(self)
        MS.on_enter(self, sid)
        MS.place_clients(self, sid, m)
        GU.reveal_master(self, m)
        halls = [GU.GUILDS[k]['name'] for k in GU.halls_in(self, sid) if not GU.GUILDS[k]['secret']]
        if halls and not getattr(m, 'halls_told', False):
            m.halls_told = True
            self.msg(f"Guild halls here: {', '.join(halls)}.", 'info')
        TW.sync_lamps(self, m)
        self.compute_fov()
        self.request = ('save',)
        CR.at_gate(self, s)

    def enter_site(self, sid):
        self.mark_visit('site', sid)
        p = self.player
        site = self.world.sites[sid]
        if self.cur == 'over':
            self.over_pos = (p.x, p.y)
        if site.map_key not in self.maps:
            self.maps[site.map_key] = ST.gen_site_map(self, site)
        self.cur = site.map_key
        m = self.map
        p.x, p.y = m.entry[0] + 1, m.entry[1]
        TW.sync_lamps(self, m)
        self.msg(f'You come to {site.name}.', 'info')
        self.compute_fov()
        self.request = ('save',)

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
                if mon.role in ('escort', 'merc_ally') or (not mon.stay and mon.role in ('villager', 'guard', 'dog', 'livestock') and random.random() < .5):
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
            self.mark_visit('s', s.id)
            kind = s.kind_name
            self.msg(f'You stand at the gates of {s.name} ({kind}). Press > or Enter to go in.', 'info')
            return 10
        if t == ENTR:
            d = self.world.dungeon_at(p.x, p.y)
            self.mark_visit('d', d.id)
            self.msg(f"You stand at the entrance of {d.name}. Press > or Enter to descend.", 'info')
            return 10
        site = ST.site_at(self.world, p.x, p.y)
        if site:
            self.mark_visit('site', site.id)
            self.msg(f'{site.name}. Press > or Enter to go in.', 'info')
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
        from . import hidden as HP
        HP.on_step(self)
        old_way = HP.on_way(self, p.x, p.y)
        cost = round((min(D.TILES[t].cost, HP.WAY_COST) if old_way else D.TILES[t].cost) * WX.travel_factor(self))
        WX.strike(self)
        if self.dead:
            return cost
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
        if old_way:
            chance *= 1.3                           # nobody patrols the old ways
        chance *= WX.ambush_factor(self)                # fog and storms hide what waits by the road
        if cheb(p.x, p.y, *self._home_xy()) <= 4:
            chance = 0
        if random.random() < chance:
            lvl = w.danger_at(p.x, p.y) + (1 if night else 0)
            keys = EVL.wild_keys(self, p.x, p.y, lvl) or WA.wild_pack(reg.biome, lvl, night, getattr(reg, 'climate', None))
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
                if pl.get('stolen'):
                    self.msg('Some of your things are gone. Someone got here first.', 'bad')
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
            elif it.dropped or (it.k == 'gear' and it.rar == 'normal' and not it.name.startswith('Your')):
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
            site = ST.site_at(self.world, p.x, p.y)
            if site:
                self.enter_site(site.id)
                return 1
            if t == ENTR:
                self.enter_dungeon(self.dungeon_at(p.x, p.y), 1, 'up')
                return 1
            poi = EV.poi_at(self, p.x, p.y)
            if poi and poi.kind in EV.RUIN_KINDS:
                from . import hidden as HP
                if not HP.vault_open(self, poi):
                    return 0
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
        if t == UP and getattr(m, 'site', None) is not None:
            ST.climb_tower(self)
            return 5
        if t == UP and d != 'down':
            dg = self.world.dungeons.get(m.did)
            if m.depth == 1 and getattr(dg, 'town', None) is not None:
                self.enter_town(dg.town)
                tm = self.map
                if DOWN in tm.t:
                    i = tm.t.index(DOWN)
                    spots = W.free_around(self, tm, i % tm.w, i // tm.w, 1)
                    if spots:
                        p.x, p.y = spots[0]
                self.msg('You climb back up into the halls of the hold.')
                self.compute_fov()
                return 1
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
        if it.t == 'cure':
            p.poison = None
            p.life = min(s['max_life'], p.life + 10)
        if it.t in ('mp', 'rejuv'):
            h = round(s['max_mana'] * (.5 if it.t == 'mp' else .4)) + 8
            p.mana = min(s['max_mana'], p.mana + h)
            self.num(p.x, p.y + (1 if it.t == 'rejuv' else 0), f'+{h}', C_MANA, True)
        self.msg({'hp': 'You drink a health potion.', 'mp': 'You drink a mana potion.', 'rejuv': 'You drink a rejuvenation potion.',
                  'cure': 'You drink the antidote. The poison loses its grip.'}[it.t], 'good')
        return 1

    def stuck(self, slot):
        """A cursed item in this slot that cannot be taken off."""
        cur = self.eq_item(slot)
        if cur and cur.cursed:
            cur.curse_known = True
            self.msg(f'{cur.display_name()} is cursed and will not leave you. A priest in a temple can lift the curse.', 'bad')
            return True
        return False

    def slot_for(self, it):
        """Where an item goes on your body: rings on the first free hand."""
        if it.slot == 'ring':
            eq = self.player.eq
            for k in ('ring1', 'ring2'):
                if k not in eq or eq[k] == it.id:
                    return k
            return 'ring1'
        return it.slot

    def two_handed(self, it):
        return bool(it and D.BASES[it.base].get('two'))

    def meets(self, it):
        """What keeps you from using it: level, Strength or Dexterity. None if nothing does."""
        p, s = self.player, self.stats()
        if it.req > p.lvl:
            return f'You need to be level {it.req} to use that.'
        if getattr(it, 'rstr', 0) > s['str']:
            return f'You need {it.rstr} Strength to use that.'
        if getattr(it, 'rdex', 0) > s['dex']:
            return f'You need {it.rdex} Dexterity to use that.'
        return None

    def equip(self, it):
        p = self.player
        why = self.meets(it)
        if why:
            self.msg(why, 'bad')
            return False
        slot = self.slot_for(it)
        if self.stuck(slot):
            return False
        cur_w = self.eq_item('weapon')
        if it.slot == 'shield' and self.two_handed(cur_w):
            self.msg(f'You need both hands for your {D.BASES[cur_w.base]["name"].lower()}. Put it away first.', 'bad')
            return False
        if it.slot == 'weapon' and self.two_handed(it) and self.eq_item('shield'):
            if self.stuck('shield'):
                return False
            p.eq.pop('shield', None)
            self.msg('You put away what you held in your other hand; this needs both.')
        p.eq[slot] = it.id
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

    MEAL = 300

    def eat(self, it):
        return HU.eat(self, it)

    STEW = 40

    def inn_stew(self):
        p = self.player
        if p.gold < self.STEW:
            self.msg('You cannot afford even a bowl of stew.', 'bad')
            return
        if p.food >= HU.MAX - 50:
            self.msg('You are not hungry.')
            return
        p.gold -= self.STEW
        p.food = min(HU.MAX, p.food + 450)
        self.msg('A bowl of hot stew and a heel of bread. That hits the spot.', 'good')

    def inn_meal(self, price=None, line=None):
        p = self.player
        price = self.MEAL if price is None else price
        if p.gold < price:
            self.msg('You cannot afford a bed.', 'bad')
            return
        p.gold -= price
        p.food = HU.MAX
        s = self.stats()
        p.life, p.mana, p.poison = s['max_life'], s['max_mana'], None
        self.end_turn(D.DAY_LEN // 3, True)
        p.buffs = [b for b in p.buffs if b[0] != 'regen'] + [['regen', 2, D.DAY_LEN, 'Well rested']]
        self.msg((line or 'A bowl of stew, a mug of ale, a straw bed. You wake rested and full.') + ' (Well rested)', 'good')

    def eat_best(self):
        return HU.eat_best(self)

    def forage(self):
        from . import foraging as FG
        return FG.forage(self)

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
            self.stuck(next(k for k, v in p.eq.items() if v == it.id))
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
        k, t = SUPPLIES[i]
        if k == 'tool' and t in ('rod', 'tent') and any(x.k == 'tool' and x.t == t for x in self.player.inv):
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

    def buy_gear(self, i, key=None, mult=1.0):
        shop = self.shops.get(self.home if key is None else key, [])
        if i >= len(shop):
            return
        it, p = shop[i], self.player
        price = max(1, round(it.value() * mult))
        if p.gold < price:
            self.msg(f'That costs {fmt(price)}.', 'bad')
            return
        if not self.add_to_inv(it):
            self.msg('Your bag is full.', 'bad')
            return
        shop.pop(i)
        p.gold -= price
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

    def mon_res(self, mon, elem):
        """A monster's resistance to an element, in percent (negative: it is weak to it)."""
        if mon.is_npc or not elem:
            return 0
        r = mon.tpl['res'].get(elem, 0)
        if 'Fire Enchanted' in mon.mods and elem == 'fire':
            r = max(r, 50)
        return r

    def weapon_extra(self, mon, s):
        """What your weapon adds on a hit: fire, cold and lightning after the monster's resistance, and holy bane."""
        extra = 0
        for st, el in (('fire_dmg', 'fire'), ('cold_dmg', 'cold'), ('light_dmg', 'lightning')):
            v = s.get(st, 0)
            if v:
                extra += random.randint(max(1, v // 2), v) * (1 - self.mon_res(mon, el) / 100)
        return extra

    # ------------------------------------------------------------ wear and repair
    def wear(self, slot=None, chance=.25):
        """Use wears gear down: the weapon when you strike, a piece of armour when you are struck."""
        if random.random() >= chance:
            return
        if slot is None:
            slots = [s_ for s_ in ('armor', 'helm', 'shield', 'gloves', 'boots', 'belt') if self.eq_item(s_)]
            if not slots:
                return
            slot = random.choice(slots)
        it = self.eq_item(slot)
        if not it or not getattr(it, 'mdur', 0) or it.dur <= 0:
            return
        it.dur -= 1
        if it.dur == 0:
            self.msg(f'Your {it.name} breaks! It is no use until it is repaired.', 'bad')
            self.clamp_vitals()
        elif it.dur == it.mdur // 4:
            self.msg(f'Your {it.name} is badly worn. Have it repaired soon.', 'bad')

    def worn_gear(self):
        """Yours, and your hireling's: the smith mends it all."""
        return [it for it in self.player.inv if it.k == 'gear' and getattr(it, 'mdur', 0) and it.dur < it.mdur] + MC.worn(self)

    def repair_cost(self, it):
        miss = (it.mdur - it.dur) / max(1, it.mdur)
        mult = 1.5 if it.rar in ('unique', 'set') else 1.25 if D.BASES[it.base].get('grade') == 'elite' else 1
        return max(10, round(it.value() * .3 * miss * mult))

    def repair_all(self, discount=0.0, dry=False):
        its = self.worn_gear()
        cost = round(sum(self.repair_cost(it) for it in its) * (1 - discount))
        if dry:
            return len(its), cost
        if not its:
            self.msg('Your gear is in good order.')
            return
        if self.player.gold < cost:
            self.msg(f'Mending all your gear costs {fmt(cost)}. You cannot afford it.', 'bad')
            return
        self.player.gold -= cost
        for it in its:
            it.dur = it.mdur
        self.clamp_vitals()
        self.msg(f'Your gear is mended for {fmt(cost)}.', 'good')

    def use_kit(self, it):
        its = self.worn_gear()
        if not its:
            self.msg('Your gear is in good order.')
            return 0
        for g_ in its:
            g_.dur = min(g_.mdur, g_.dur + max(1, round(g_.mdur * .35)))
        self.remove_one(it)
        self.clamp_vitals()
        self.msg('You mend what you can with the repair kit. It will do, for now.', 'good')
        return 10

    def damage_mon(self, mon, dmg, crit=False, col=C_DMG, weapon=False, elem=None):
        p = self.player
        if weapon:
            self.wear('weapon', .2)
        if elem:
            dmg *= 1 - self.mon_res(mon, elem) / 100
        MC.add_threat(mon, 'p', dmg)
        if weapon and not mon.is_npc and mon.k in D.UNDEAD:
            und = self.stats().get('undead', 0)
            if und:
                dmg *= 1 + und / 100
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
        if not self.damage_mon(mon, random.randint(*s['dmg']) + self.weapon_extra(mon, s), crit, weapon=True):
            self.msg(f"You {'critically ' if crit else ''}hit {mon.the()}.")

    def weapon_strike(self, mon, pct, force_crit=False, ranged=False):
        s = self.stats()
        crit = force_crit or random.random() < s['crit'] / 100
        return self.damage_mon(mon, random.randint(*s['dmg']) * pct / 100 + self.weapon_extra(mon, s), crit, weapon=True)

    def hurt(self, dmg, src, elem=None):
        p = self.player
        s = self.stats()
        if elem in D.ELEMENT_RES:
            dmg *= 1 - s[D.ELEMENT_RES[elem]] / 100
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
        GD.on_kill(self, mon)
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
        if not mon.is_npc:
            s = self.stats()
            if s['lpk']:
                p.life = min(s['max_life'], p.life + s['lpk'])
            if s['mpk']:
                p.mana = min(s['max_mana'], p.mana + s['mpk'])
        if 'Fire Enchanted' in mon.mods:
            self.flash(ring(mon.x, mon.y, 1), (255, 122, 44), '*', .26)
            self.msg(f'{mon.name} explodes in flames!', 'bad')
            if cheb(mon.x, mon.y, p.x, p.y) <= 1:
                self.hurt(mon.dmg[1] * .8, mon.name, 'fire')
        self.drop_loot(mon)
        if mon.faction:
            WAR.on_kill(self, mon)
        if getattr(mon, 'commander', False) and getattr(m, 'hid', None) is not None:
            self.capture_hold(m.hid)
        if mon.k == 'snagtooth':
            self.flags['den'] = True
            sword = make_gear(self, 'shortsword', 'normal', 1)
            sword.name = 'Your Short Sword'
            shield = make_gear(self, 'buckler', 'normal', 1)
            shield.name = 'Your Buckler'
            self.spill(m, mon.x, mon.y, sword)
            self.spill(m, mon.x, mon.y, shield)
            from .entities import make_tome
            spell = random.choice(['firebolt', 'frost_shard', 'spark', 'mend', 'drain'])
            tome = Item(self.new_id(), 'tome', spell)
            tome.name = 'tome'
            self.spill(m, mon.x, mon.y, tome)
            for it in (sword, shield, tome):
                it.dropped = False
            self.msg('Among the chief\'s filthy hoard: your sword and shield! And a small book, its pages full of strange signs.', 'gold')
            self.msg('Now go to Thornfield and report to Elder Berend. Sister Ilse said he wanted to meet you.', 'info')
            th = self.world.settlements[0]
            self.reveal_place(th.x, th.y, 2)
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
        # only those who use gear drop gear, and what they drop is what they use
        uses = D.GEAR_USERS.get(mon.k)
        if not uses:
            n = 0
        elif boss:
            n = random.randint(2, 3)
        else:
            n = (random.randint(1, 2) if random.random() < .8 else 0) if mon.elite == 2 else \
                (1 if random.random() < .45 else 0) if mon.elite == 1 else (1 if random.random() < .08 else 0)
        if boss:
            u = next((u for u in D.UNIQUES if u.get('boss') == mon.k), None)
            if u:
                it = make_unique(self, u)
                self.spill(m, mon.x, mon.y, it)
                self.announce(it)
        for _ in range(n):
            it = random_gear(self, lvl, boost, uses, mon.k)
            if boost > 3 and it.rar == 'normal':
                up = make_gear(self, it.base, 'magic', lvl)
                it.rar, it.aff, it.name, it.ided = up.rar, up.aff, up.name, False
            self.spill(m, mon.x, mon.y, it)
            self.announce(it)
        if (uses or boss) and random.random() < (1 if boss else .2 if mon.elite == 2 else .06 if mon.elite == 1 else .006):
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
        if mon.k in HU.BEASTS and random.random() < .35:
            self.spill(m, mon.x, mon.y, HU.make_food(self, 'meat'))
        if (uses or carrier) and random.random() < (.5 if special else .06):
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
        if MC.intercept(self, mon):
            return
        if random.random() < self.mon_hit_chance(mon, df):
            dmg = random.randint(*mon.dmg)
            if 'weaken' in mon.effects:
                dmg = round(dmg * .7)
            if 'Vampiric' in mon.mods:
                mon.hp = min(mon.maxhp, mon.hp + round(dmg / 2))
            if mon.tpl['leech']:
                mon.hp = min(mon.maxhp, mon.hp + round(dmg / 3))
            elem = 'fire' if 'Fire Enchanted' in mon.mods else mon.tpl['elem']
            word = {'fire': ' with fire', 'cold': ' with frost', 'lightning': ' with lightning'}.get(elem, '')
            self.msg(f'{mon.the()[0].upper() + mon.the()[1:]} hits you{word}.', 'bad')
            if mon.tpl['poison'] and random.random() < .4:
                rp = self.stats()['res_poison']
                if random.random() * 100 >= rp:
                    turns = max(1, round((3 if getattr(p, 'race', '') == 'dwarf' else 6) * (1 - rp / 100)))
                    p.poison = [max(1, turns), max(1, round(mon.lvl / 2))]
                    self.msg('Venom burns in your veins!', 'bad')
            th = self.stats()['thorns']
            self.wear(None, .3)
            self.hurt(dmg, mon.the(), elem if elem != 'poison' else None)
            if th and not self.dead and mon in self.map.mons:
                self.num(mon.x, mon.y, str(th), (200, 170, 120))
                if mon.hp - th <= 0:
                    self.damage_mon(mon, th)
                else:
                    mon.hp -= th
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
            self.hurt(random.randint(*mon.dmg) * (.9 if spell else .8), mon.the(), (mon.tpl['elem'] or 'fire') if spell else None)
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
            self.hurt(random.randint(*mon.dmg) * .8, mon.name, d['elem'] or 'cold')
            return
        if MC.mon_turn(self, mon, df):
            return
        if AI.turn(self, mon, df):
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
        if AI.approach(self, mon):
            return
        self.step_toward(mon)

    def monsters_act(self):
        m, p = self.map, self.player
        key = self.cur
        self.compute_dist()
        MC.decay(m)
        df = self.stats()['def']
        for mon in m.mons[:]:
            if self.dead or self.cur != key or self.request == ('win',):
                return
            if mon not in m.mons:
                continue
            if mon.is_npc:
                if getattr(mon, 'ally', False):
                    MC.act(self, mon)
                    continue
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
                still = AI.asleep(self, mon)
                if still:
                    continue
                if still is None:
                    if self.visible(mon.x, mon.y) and random.random() < .65:
                        mon.awake = True
                        self.wake_pack(mon)
                        AI.on_wake(self, mon)
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
            HU.tick(self, WX.food_factor(self))
            if self.dead:
                return
            if self.turn % 4 == 0 and p.life < s['max_life'] and p.food >= HU.WEAK:
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
                GU.daily(self)
                EVL.daily(self)
                CR.daily(self)
                MC.daily(self)
            self.last_day = self.day
        EVL.whisper(self)
        WX.notice(self)
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

    def raise_fee(self, lvl=None):
        """What the priests ask to call someone back from the dead."""
        lvl = lvl or self.player.lvl
        return 100 + lvl * lvl * 25

    def respawn(self, cause):
        """Softcore death: the priests of the nearest temple call you back, for a fee from your purse. Your backpack
        and cargo stay with your body. Without the coin for the temple your tale ends here."""
        p = self.player
        fee = self.raise_fee()
        if p.gold < fee:
            self.dead = True
            p.life = 0
            self.cause = f'{cause}; there was no coin for the temple'
            self.msg('You have died, and there is no coin in your purse for the priests. Your tale ends here.', 'bad')
            return
        p.deaths += 1
        MC.on_player_death(self)
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
            corpse.name = f'your body ({CAL.short(self.day)})'
            corpse.payload = dict(items=[it for it in p.inv if not self.is_equipped(it) and it.k != 'quest'],
                                  cargo=dict(p.cargo), cost=dict(p.cost_basis), gold=0)
            corpse.x, corpse.y = cx, cy
            # whoever is around may help themselves
            dm = self.maps[key]
            thieves = [o for o in dm.mons if not o.is_npc and (o.k in D.GEAR_USERS or o.tpl['ch'] in '@hgk')] if key != 'over' else []
            risk = min(.85, .2 * len(thieves)) if key != 'over' else .3
            pl = corpse.payload
            kept = [o for o in pl['items'] if random.random() >= risk]
            stolen = len(pl['items']) - len(kept)
            pl['items'] = kept
            if random.random() < risk:
                taken = pl['gold'] * random.randint(50, 100) // 100
                pl['gold'] -= taken
                stolen += 1
            pl['stolen'] = stolen
            self.maps[key].items.append(corpse)
            self.corpses.append((key, corpse.id))
            p.inv = [it for it in p.inv if self.is_equipped(it) or it.k == 'quest']
            p.cargo, p.cost_basis = {}, {}
        here = self.world.settlements[self.home] if self.home is not None else None
        ox, oy = self.over_pos if self.cur != 'over' else (p.x, p.y)
        temples = [st for st in self.world.settlements if 'temple' in st.services] + \
            [st for st in getattr(self.world, 'sites', []) if st.kind in ('temple', 'monastery')]
        dest = min(temples, key=lambda st: cheb(st.x, st.y, ox, oy)) if temples else here
        s = self.stats()
        p.life, p.mana = max(1, s['max_life'] // 2), s['max_mana'] // 2
        p.poison = p.burn = None
        p.gold -= fee
        p.buffs = [['frail', 25, D.DAY_LEN * 2, 'Weakened by death']]
        self.cur = 'over'
        p.x, p.y = dest.x, dest.y
        if isinstance(dest, ST.Site):
            self.enter_site(dest.id)
            self.msg(f'You were slain by {cause}... and wake on the cold floor of {dest.name}.', 'bad')
        else:
            self.enter_town(dest.id)
            self.msg(f'You were slain by {cause}... and wake on the cold floor of the temple in {dest.name}.', 'bad')
        if corpse:
            where = 'in the wilds' if key == 'over' else self.maps[key].name
            self.msg(f'Your backpack and cargo lie with your body {where}. Go and get them back.', 'bad')
        self.msg(f'The priests took {fmt(fee)} for their prayers. You will be weak for a day or two.', 'bad')
        self.request = ('save',)

    # ------------------------------------------------------------ targeting (Tab, as in WoW)
    def target(self):
        """The enemy you have picked with Tab, while you can still see it."""
        p = self.player
        tid = getattr(p, 'target', None)
        if tid is None:
            return None
        for o in self.visible_hostiles():
            if o.id == tid:
                return o
        p.target = None
        return None

    def cycle_target(self, step=1):
        """Tab: the next enemy in sight, nearest first; Shift+Tab goes back."""
        p = self.player
        lst = sorted(self.visible_hostiles(), key=lambda o: (cheb(o.x, o.y, p.x, p.y), o.id))
        if not lst:
            p.target = None
            self.msg('No enemy in sight.')
            return
        ids = [o.id for o in lst]
        cur = getattr(p, 'target', None)
        k = (ids.index(cur) + step) % len(ids) if cur in ids else (0 if step > 0 else len(ids) - 1)
        p.target = p.last_target = ids[k]
        o = lst[k]
        self.msg(f'Target: {o.name}, level {o.lvl}, {cheb(o.x, o.y, p.x, p.y)} away.', 'info')

    def clear_target(self):
        p = self.player
        if getattr(p, 'target', None) is None:
            return False
        p.target = None
        self.msg('Target cleared.')
        return True

    def miss_target(self, default):
        self.msg(default if not getattr(self, '_out_of_range', False) else 'Your target is out of range.')

    def nearest_target(self, max_d, need_line):
        p = self.player
        self._out_of_range = False
        t = self.target()
        if t:      # a picked target: that one or nothing, as in WoW
            if cheb(t.x, t.y, p.x, p.y) <= max_d and (not need_line or self.line_clear(p.x, p.y, t.x, t.y)):
                return t
            self._out_of_range = True
            return None
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
            self.miss_target('No target in sight.')
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
        self.damage_mon(t, random.randint(*s['dmg']) + self.weapon_extra(t, s), crit, weapon=True)
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
        npc = {(o.x, o.y) for o in m.mons if o.is_npc and not getattr(o, 'ally', False)}
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
        p = self.player
        if self.map.kind in ('over', 'wild') and not self.hostile_visible():
            s = self.stats()
            if p.life < s['max_life'] or p.mana < s['max_mana'] or TW.is_night(self):
                self.make_camp()
                return
        self.rest_here()

    def rest_here(self, quiet=False):
        p, n = self.player, 0
        while n < 300 and not self.dead:
            s = self.stats()
            if self.hostile_visible():
                if not n:
                    self.msg('You cannot rest with enemies in sight.', 'bad')
                break
            if p.life >= s['max_life'] and p.mana >= s['max_mana'] and not p.poison:
                if not n and not quiet:
                    self.msg('You are already fully rested.')
                break
            self.end_turn(1, True)
            n += 1
        if n and not quiet:
            self.msg(f'You rest for {n} turns.')
        return n

    # ------------------------------------------------------------ sleeping out in the wild
    def make_camp(self):
        """Out in the open you can rest for free, but the night is not always kind."""
        tent = any(it.k == 'tool' and it.t == 'tent' for it in self.player.inv)
        EV.ask(self, 'camp_night', 'Make camp', 'You find a sheltered spot to rest' + (' and pitch your tent.' if tent else '.') +
               ' A fire keeps the beasts away, but it can be seen from far off.',
               [('Light a fire and rest', 'fire'), ('Rest in the dark, without a fire', 'dark'), ('Walk on', 'leave')])

    def camp(self, fire):
        """A night (or a rest) in the open: wild animals, robbers, a thief, or a bad night's sleep."""
        p, w = self.player, self.world
        ox, oy = (p.x, p.y) if self.cur == 'over' else self.over_pos
        danger = w.danger_at(ox, oy)
        near_road = w.off_road(ox, oy) <= 2
        tent = any(it.k == 'tool' and it.t == 'tent' for it in p.inv)
        night = TW.is_night(self)
        risk = (.05 + danger * .015) * (1.6 if night else .6) * (.65 if tent else 1)
        from . import mercs as MC
        guard = MC.on_watch(self)
        beasts = risk * (.4 if fire else 1) * (.6 if near_road else 1.2)
        robbers = risk * (1.7 if fire else .8) * (1.4 if near_road else .7)
        thief = risk * .5 * (.2 if guard else 1)
        if self.cur != 'over':
            beasts = robbers = 0
        r = random.random()
        rested = self.rest_here(quiet=True)
        if night:
            self.end_turn(max(0, D.DAY_LEN // 3 - rested), True)
        if self.dead or self.cur not in ('over', 'wild'):
            return
        reg = w.region_at(ox, oy)
        if r < beasts:
            pack = WA.wild_pack(reg.biome, danger, True, getattr(reg, 'climate', None))
            pack = [k for k in pack if k in HU.BEASTS] or ['wolf'] * random.randint(2, 3)
            self.msg('Something circles your camp in the dark. Eyes, teeth. You are up in an instant!' if not guard else
                     f'{guard.name} shakes you awake: "Beasts! On your feet!"', 'bad')
            if self.cur == 'over':
                self.start_encounter(None, self.maps['over'].tile(ox, oy), danger + 1, pack, 0)
        elif r < beasts + robbers:
            pack = ['bandit'] + [random.choice(['bandit', 'brigand']) for _ in range(random.randint(1, 2 + danger // 3))]
            self.msg('Shapes step out of the night around your fire: robbers, blades drawn!' if fire else
                     'Footsteps on the road, then voices: robbers have stumbled on your camp!', 'bad')
            if self.cur == 'over':
                self.start_encounter(None, self.maps['over'].tile(ox, oy), danger + 1, pack, 0)
        elif r < beasts + robbers + thief:
            loss = p.gold * random.randint(15, 40) // 100
            bag = [it for it in self.backpack() if it.k not in ('quest', 'corpse')]
            if bag and random.random() < .5:
                it = random.choice(bag)
                p.inv.remove(it)
                self.msg(f'You wake to find your pack open. Someone took {it.display_name()} in the night.', 'bad')
            elif loss:
                p.gold -= loss
                self.msg(f'You wake to find your purse lighter: {fmt(loss)} gone. A thief, in the night.', 'bad')
        else:
            wet = WX.current(self) in ('rain', 'downpour', 'storm', 'snow', 'blizzard', 'sleet', 'freezing') and not tent
            if wet:
                self.msg('Cold and wet, you hardly sleep. A tent would have helped.', 'bad')
                p.life = max(1, p.life - self.stats()['max_life'] // 5)
            else:
                self.msg('You sleep under the open sky, and wake with the birds.' if night else 'You rest a while.', 'good')

    def travel_to(self, kind, ref):
        for _ in self.travel_iter(kind, ref):
            pass

    def mark_visit(self, kind, ref):
        """Places you have stood at yourself: only these can you travel to without thinking."""
        self.__dict__.setdefault('visited', set()).add((kind, ref))

    def has_visited(self, kind, ref):
        return (kind, ref) in self.__dict__.get('visited', ())

    def travel_route(self, tgt):
        """The way to go: to the nearest road, along the roads, and the last stretch over open land."""
        p = self.player

        def cost(t):
            td = D.TILES[t]
            if not td.walk:
                return None
            if t == ROAD:
                return 2
            if t in (TOWN, CITY):
                return 3
            return td.cost * 3
        return WO.dijkstra_path(self.map, (p.x, p.y), tgt, cost)

    def travel_iter(self, kind, ref):
        """Walk to a place you have been ('s' settlement, 'site', 'd' dungeon), along the roads. One step per yield;
        time, hunger and weather pass as you walk, and anything worth your attention stops you."""
        if self.map.kind == 'town':
            self.leave_to_over()
        if self.cur != 'over':
            self.msg('You can only travel across the open land.')
            return
        w = self.world
        obj = w.settlements[ref] if kind == 's' else w.sites[ref] if kind == 'site' else w.dungeons[ref]
        if not self.has_visited(kind, ref):
            self.msg(f'You have never been to {obj.name}; you would have to find the way yourself.')
            return
        tgt = (obj.x, obj.y)
        p = self.player
        path = self.travel_route(tgt)
        if not path:
            self.msg('You cannot find a way there.')
            return
        self.msg(f'You set out for {obj.name}.')
        seen_folk = {wd.id for wd in w.wanderers if self.visible(wd.x, wd.y)}
        food0 = getattr(p, 'food', 500)
        for x, y in path:
            if self.dead or self.cur != 'over':
                break
            near = [wd for wd in w.wanderers if wd.hostile and wd.cooldown == 0 and self.visible(wd.x, wd.y)]
            if near:
                self.msg(f'You spot {near[0].name[0].lower() + near[0].name[1:]} and stop.', 'bad')
                break
            folk = [wd for wd in w.wanderers if not wd.hostile and wd.id not in seen_folk and self.visible(wd.x, wd.y)
                    and cheb(wd.x, wd.y, p.x, p.y) <= 4]
            if folk:
                self.msg(f'{folk[0].name} comes along the road. You stop.', 'info')
                break
            seen_folk |= {wd.id for wd in w.wanderers if self.visible(wd.x, wd.y)}
            food = getattr(p, 'food', 500)
            if food < HU.HUNGRY <= food0 or food < HU.WEAK <= food0:
                self.msg('Your stomach growls. You stop to think about food.', 'bad')
                break
            s = self.stats()
            if p.life < s['max_life'] * .4:
                self.msg('You are too badly hurt to walk on without care.', 'bad')
                break
            from .wanderers import wanderer_at
            for _wait in range(4):                   # someone on the road ahead: let them pass
                if not wanderer_at(self, x, y):
                    break
                self.end_turn(5, True)
            if wanderer_at(self, x, y):
                self.msg('The road ahead is blocked.', 'info')
                break
            used = self.try_move(x - p.x, y - p.y)
            if not used:
                break
            self.end_turn(used, True)
            if self.request and self.request[0] not in ('save',):
                break
            if self.pending or self.cur != 'over':
                break
            if (p.x, p.y) != tgt:
                yield 1
        if self.cur == 'over' and (p.x, p.y) == tgt:
            self.over_step()

    def deephold_name(self):
        holds = [s for s in self.world.settlements if s.kind == 'deephold']
        if not holds:
            return 'the dwarf halls under the mountains'
        h = min(holds, key=lambda q: cheb(q.x, q.y, *self._home_xy()))
        return f'{h.name}, the dwarf hold under the mountains to the {dir_name(h.x - self._home_xy()[0], h.y - self._home_xy()[1])}'

    def story(self):
        """The open story tasks, for the journal: (title, text)."""
        f = self.flags
        out = []
        if f.get('quest_den') and not f.get('den'):
            out.append(('Your sword and shield', f'Kobolds took your things to the Hollow Den, to the {self.dir_to("den")}. '
                        'Their chief, Snagtooth, has them. Get them back.'))
        elif f.get('den') and not f.get('met_elder'):
            out.append(('Elder Berend', 'Sister Ilse said the elder of Thornfield wanted to meet you. His house is on the green.'))
        if f.get('met_elder'):
            if not f.get('ratking'):
                out.append(('The Rat King', f'A monstrous Rat King plunders Thornfield\'s stores from the Rat Warrens, to the {self.dir_to("rat")}.'))
            elif not f.get('reward_rat'):
                out.append(('The Rat King is dead', 'Return to Elder Berend in Thornfield.'))
            if not f.get('grolm'):
                out.append(('Grolm the Digger', f'A mad dwarf exiled from {self.deephold_name().split(",")[0]} holds the Lost Mine, '
                            f'to the {self.dir_to("mine")}. Thornfield needs its iron back.'))
            elif not f.get('reward_grolm'):
                out.append(('Grolm is dead', 'Return to Elder Berend in Thornfield.'))
        if f.get('quest_fish') and not f.get('fish_done'):
            out.append(('A first catch', 'The old fisherman by the pond in Thornfield wants to see your first fish. '
                        'Stand by water and press A to cast.'))
        return out

    def reveal_route(self, a, b):
        """Hear where settlement b lies from a: only the place itself goes on the map, not the road or the land
        around it. You discover those by walking there. Returns the length of the road."""
        om = self.maps['over']
        path = WA.road_path(self, a, b) or []
        s = self.world.settlements[b]
        om.seen[s.y * om.w + s.x] = 1
        return len(path)

    def reveal_place(self, x, y, r=0):
        """Mark a place you have heard of on the map: just the spot, not the land around it."""
        om = self.maps['over']
        if om.inb(x, y):
            om.seen[y * om.w + x] = 1

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
                        ('\n\nYou mark roughly where they lie on your map. The roads and the land between you will '
                         'only come to know by walking them.' if new else ''))
        if new:
            self.msg(f'You hear of {new} new place{"s" if new > 1 else ""}.', 'info')

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
        if role == 'recruit':
            MC.talk_recruit(self, npc)
            return
        if role == 'merc_ally':
            MC.menu(self)
            return
        if role == 'factor':
            NW.talk_factor(self, npc)
            return
        if role == 'captain':
            NW.talk_captain(self, npc)
            return
        if role == 'sailor':
            NW.talk_sailor(self, npc)
            return
        if role == 'healer':
            if getattr(m, 'site', None) is not None and m.site == getattr(self.world, 'start_temple', None) \
                    and not f.get('met_priest'):
                f['met_priest'] = True
                s = self.stats()
                p.life = s['max_life']
                p.gold += 520
                self.request = ('dialog', npc.name,
                                f'"Easy now, easy. You are safe. This is the {self.world.sites[m.site].name}, '
                                f'a short walk from Thornfield.\n\n'
                                f'A farmer found you three days ago, lying in the ditch by the road. No horse, no purse, '
                                f'nothing but the clothes on your back, and a name you kept repeating: {p.name}.\n\n'
                                f'You do not remember? No... I thought not. It may come back in time. It may not.\n\n'
                                f'The farmer saw kobolds running from that ditch, with a sword and a shield. Yours, I would wager. '
                                f'They nest in the Hollow Den, to the {self.dir_to("den")}; old Snagtooth leads them. '
                                f'Without a blade you will have to use your fists. Be careful.\n\n'
                                f'Here, a few coppers from the poor box. Elder Berend will want to meet you too; his house is on the green. '
                                f'And {RC.address(self)}... whoever you were before, you can be someone new now."')
                f['quest_den'] = True
                om = self.maps['over']
                dd = self.world.dungeons['den']
                self.reveal_place(dd.x, dd.y, 1)
                return
            self.request = ('temple', npc.name)
            return
        if role == 'elder':
            if not f.get('met_elder'):
                f['met_elder'] = True
                text = (f'"So you are the stranger Sister Ilse found by the road. No memory, she says. Well, {RC.address(self)}, '
                        f'Thornfield could use a pair of hands, whoever you were.\n\n'
                        f'To the {self.dir_to("rat")} lie the Rat Warrens, where a monstrous Rat King sends his brood to plunder our stores. '
                        f'And to the {self.dir_to("mine")}, at the foot of the mountains, lies our old iron mine. Grolm the Digger holds it now: '
                        f'a dwarf, cast out of {self.deephold_name()} for digging where his people had forbidden it. Something he found '
                        f'down there broke his mind. He and his gang of cutthroats keep the mine, and Thornfield has no iron.\n\n'
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
        if role == 'guild':
            from . import guilds as GU
            GU.talk(self, npc)
            return
        if role in ('valley', 'valley_elder'):
            from . import hidden as HP
            HP.valley_talk(self, npc)
            return
        if role == 'thane':
            from .deephold import thane_talk
            thane_talk(self, npc)
            return
        if role == 'client':
            MS.client_talk(self, npc)
            return
        if role == 'dog':
            self.msg('The dog wags its tail and sniffs your boots.')
            return
        if role == 'livestock':
            self.msg(random.choice([f'{npc.name} chews and ignores you.', f'{npc.name} looks at you with mild suspicion.',
                                    f'{npc.name} shuffles away.']))
            return
        if role == 'tower':
            self.say(npc, random.choice(['Climb the stairs to the top and you can see half the province.',
                                         'Quiet watch so far. Keep it that way.', self.rumor()]))
            return
        if role == 'herbalist':
            from . import foraging as FG
            FG.herbalist_talk(self, npc)
            return
        if role == 'fisher':
            self.fisher_talk(npc)
            return
        if role == 'farmer':
            self.farmer_talk(npc)
            return
        if role == 'roadinn':
            EV.ask(self, 'roadinn', npc.name, f'"Come in, come in, out of the {self.weather_word()}! Food? A bed? '
                   f'The road is long and the night is longer."',
                   [(f'A bowl of stew ({fmt(self.STEW)})', 'stew'), (f'A hot meal and a bed for the night ({fmt(self.MEAL)})', 'meal'),
                    ('Any news from the road?', 'news'), ('Just passing through', 'leave')], npc=npc.id)
            return
        self.say(npc, LORE.chatter(self, npc))

    def weather_word(self):
        from . import weather as WX
        return WX.NAMES.get(WX.current(self), 'cold').lower() if WX.current(self) != 'clear' else 'cold'

    def farmer_talk(self, npc):
        """Farm folk are generous: once a day they share their table with a traveller."""
        p = self.player
        last = getattr(npc, 'fed_day', -1)
        if last != self.day and p.food < HU.MAX - 150:
            npc.fed_day = self.day
            p.food = min(HU.MAX, p.food + 300)
            self.request = ('dialog', npc.name, random.choice([
                '"You look half starved. Sit, sit. There is always enough stew for one more."',
                '"Travelling far? Have some bread and cheese, and tell us what they say in the towns."',
                '"Eat, eat. The harvest was kind to us this year. The gods know it is not every year."']) +
                '\n\n(You share a meal with the family.)')
            return
        self.say(npc, random.choice(['The crows are worse than the wolves this year.', 'Mind the gate, the goats get out.',
                                     'Rain tomorrow, my knee says.', self.rumor()]))

    def fisher_talk(self, npc):
        """The old fisherman by the pond in Thornfield: your first fishing pole, and your first catch."""
        from . import lifeskills as LS
        f, p = self.flags, self.player
        if not f.get('quest_fish'):
            f['quest_fish'] = True
            if not LS.has_pole(self):
                self.add_to_inv(Item(self.new_id(), 'tool', 'rod'))
            self.request = ('dialog', npc.name,
                            f'"Hm? Oh, you are the one they pulled out of the ditch. Nothing to do with yourself yet, eh?\n\n'
                            f'Here, take this old pole. I have three more. Stand by the water, press A to cast, and be patient. '
                            f'The perch in this pond are small, but they bite.\n\n'
                            f'Bring me your first fish and I will show you what an old man knows about the trade."\n\n'
                            f'(You receive a fishing pole.)')
            return
        if not f.get('fish_done'):
            fish = next((i for i in p.inv if i.k == 'fish'), None)
            if not fish:
                self.say(npc, random.choice(['Patience. The fish do not care how hungry you are.',
                                             'Stand close to the water and press A. Then wait.',
                                             'Nothing yet? Try again. And again. That is fishing.']))
                return
            f['fish_done'] = True
            name = fish.display_name().split('x ', 1)[-1]
            self.remove_one(fish)
            p.gold += 150
            self.add_to_inv(HU.make_food(self, 'bread'))
            LS.gain(self, 'fishing', 6)
            self.request = ('dialog', npc.name,
                            f'"A {name.lower()}! Ha, look at that. Not bad for a first catch.\n\n'
                            f'Now listen: rivers have trout, lakes have carp, and the sea has things you would not believe. '
                            f'The better you get, the bigger the fish that bite. And a fish on a fire beats any inn stew.\n\n'
                            f'Here, a loaf of bread, and a few coppers for the fish. I will have it for supper."\n\n'
                            f'(You receive 1 silver 50 copper and a loaf of bread. Your fishing improves.)')
            return
        self.say(npc, random.choice(['Caught anything big yet?', 'They say a golden carp lives in the deep rivers. I never saw it.',
                                     'The pike in the lakes will take your finger off. Mind it.', self.rumor()]))

    def usable_here(self):
        """Is there a way in, up or down where you stand?"""
        m, p = self.map, self.player
        if m.kind == 'over':
            w = self.world
            return bool(w.settlement_at(p.x, p.y) or w.hold_at(p.x, p.y) or ST.site_at(w, p.x, p.y)
                        or m.tile(p.x, p.y) == ENTR or EV.poi_at(self, p.x, p.y))
        return m.tile(p.x, p.y) in (DOWN, UP)

    def act_here(self):
        """The one action key: do the obvious thing where you stand. Go in or take the stairs, pick things up,
        talk to whoever is near, read a signpost or open a chest next to you, or fish if you stand by water."""
        m, p = self.map, self.player
        if self.usable_here():
            return self.use_stairs('auto')
        if any(i.x == p.x and i.y == p.y and i.k not in ('gold', 'orb') for i in m.items):
            return self.pickup()
        if self.nearby_people():
            return self.talk_nearby()
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0), (1, -1), (1, 1), (-1, 1), (-1, -1)):
            x, y = p.x + dx, p.y + dy
            if m.inb(x, y) and m.tile(x, y) in (D.SIGNPOST, D.CHEST):
                return self.try_move(dx, dy)
        if LS.has_pole(self) and LS.water_here(self) and not self.hostile_visible():
            return self.fish()
        self.msg('Nothing to do here. Esc opens the menu, with everything else.')
        return 0

    def context_hints(self):
        """What you could do right here, as (key, words): shown at the foot of the panel, so the shortcuts
        are learnt the moment they are useful."""
        m, p = self.map, self.player
        out = []
        foe = self.hostile_visible()
        if self.usable_here():
            out.append(('Enter', 'go in' if m.kind == 'over' else 'stairs'))
        elif any(i.x == p.x and i.y == p.y and i.k not in ('gold', 'orb') for i in m.items):
            out.append(('Enter', 'pick up'))
        elif self.nearby_people():
            out.append(('t', 'talk'))
        else:
            for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0), (1, -1), (1, 1), (-1, 1), (-1, -1)):
                if m.inb(p.x + dx, p.y + dy) and m.tile(p.x + dx, p.y + dy) in (D.SIGNPOST, D.CHEST):
                    out.append(('Enter', 'read' if m.tile(p.x + dx, p.y + dy) == D.SIGNPOST else 'open'))
                    break
        if foe:
            if self.stats()['ranged']:
                out.append(('f', 'shoot'))
            return out[:3]
        if LS.has_pole(self) and LS.water_here(self):
            out.append(('a', 'fish'))
        if HU.state(getattr(p, 'food', 500)) in ('Hungry', 'Weak', 'Fainting', 'Starving') and HU.has_food(self):
            out.append(('E', 'eat'))
        if m.kind in ('over', 'wild') and m.tile(p.x, p.y) in (D.GRASS, D.FOREST, D.SWAMP, D.HILLS):
            out.append(('F', 'forage'))
        s = self.stats()
        if p.life < s['max_life'] * .7 or p.mana < s['max_mana'] * .5:
            out.append(('R', 'rest'))
        return out[:3]

    def nearby_people(self):
        """Who you could talk to from where you stand: people within two steps (across a counter or a table)."""
        m, p = self.map, self.player
        out = []
        if m.kind == 'over':
            for wd in self.world.wanderers:
                if not wd.hostile and cheb(wd.x, wd.y, p.x, p.y) <= 1 and wd.kind in ('traveler', 'caravan'):
                    out.append(wd)
            return out
        for o in m.mons:
            if o.is_npc and cheb(o.x, o.y, p.x, p.y) <= 2 and self.visible(o.x, o.y):
                if cheb(o.x, o.y, p.x, p.y) == 2:
                    mid = ((p.x + o.x) // 2, (p.y + o.y) // 2), ((p.x + o.x + 1) // 2, (p.y + o.y + 1) // 2)
                    if all(D.TILES[m.tile(*c)].opaque for c in mid):
                        continue            # a wall between you
                out.append(o)
        animals = ('livestock', 'dog', 'escort')
        out.sort(key=lambda o: (o.role in animals, cheb(o.x, o.y, p.x, p.y)))
        return out

    def talk_to(self, who):
        """Talk to a person (or a traveller on the road)."""
        if self.map.kind == 'over':
            if who.kind == 'traveler':
                EV.talk_traveller(self, who)
            else:
                EV.talk_caravan(self, who)
            return
        self.talk(who)

    def talk_nearby(self):
        """The talk key: talk to the person next to you, or ask who."""
        people = self.nearby_people()
        if not people:
            self.msg('There is nobody near enough to talk to.')
            return 0
        humans = [o for o in people if getattr(o, 'role', 'traveler') not in ('livestock', 'dog', 'escort')]
        if len(humans) == 1 or (len(people) == 1):
            self.talk_to(humans[0] if humans else people[0])
            return 0
        self.request = ('talkpick', [o.id for o in people])
        return 0

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
            kind = s.kind_name
            f = D.FACTIONS[s.faction]['short']
            return (f"There is a {kind} called {s.name} to the {dir_name(s.x - ox, s.y - oy)}, "
                    f"{cheb(s.x, s.y, ox, oy)} leagues or so. {f} land.")
        return LORE.hint(self)


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
