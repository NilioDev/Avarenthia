"""Playtest with bots of different player types, each a little careless, as a real player is.
Run from the project folder:  python tests/playtest.py [type ...] [--days N] [--seed N]
Types: trader, fighter, explorer, homeowner, knight, newbie, gambler, camper, roamer, masher (all when none is given).

Each bot plays a fresh world through the real game (the engine, and the UI where a key is the way in), makes the
small mistakes a player makes (a wrong good bought, a tax forgotten, a fight taken too low on life), and writes what
happened: money in and out, deaths, what it met, and every crash with its traceback. The report goes to stdout and,
as JSON, to the file named by PLAYTEST_OUT."""
import collections
import json
import os
import random
import sys
import tempfile
import time
import traceback

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from avarenthia import engine as E, data as D, ui, events as EV, economy as ECO  # noqa: E402
from avarenthia.canvas import FakeCanvas  # noqa: E402
from avarenthia.worldgen import cheb  # noqa: E402

_RUN_DIR = tempfile.mkdtemp(prefix=f'avarenthia_play_{os.getpid()}_')
E.save_path = lambda: os.path.join(_RUN_DIR, 'avarenthia_play.dat')
ui.App.first_sight_cards = False

DIR_TOK = {(0, -1): 'up', (0, 1): 'down', (-1, 0): 'left', (1, 0): 'right',
           (-1, -1): 'np7', (1, -1): 'np9', (-1, 1): 'np1', (1, 1): 'np3'}


def sign(v):
    return (v > 0) - (v < 0)


class Bot:
    """What every bot can do: start a game, take its choices, walk, travel, fight, and note what happened."""
    kind = 'bot'
    sloppy = .2

    def __init__(self, seed, days):
        self.rng = random.Random(seed)
        random.seed(seed)
        self.seed, self.days = seed, days
        self.log = []
        self.crashes = []
        self.stats = collections.Counter()
        self.money = []
        self.start = time.time()
        self.app = self.new_app(seed)
        self.g = self.app.game
        self.p = self.g.player

    # -------------------------------------------------------------- the game
    def new_app(self, seed):
        app = ui.App(FakeCanvas(ui.W, ui.H))
        app.key('n')
        for ch in self.kind.capitalize()[:10]:
            app.key(ch)
        app.key('enter')
        app.key('down')
        for ch in str(seed):
            app.key(ch)
        app.key('enter')
        app.render()
        assert app.top.wait()
        for _ in range(3):
            app.render()
            app.key('enter')
        assert isinstance(app.top, ui.GameScreen), app.top
        return app

    def veteran(self, lvl, coin=0):
        """A player who has played the opening: some levels, their points spent, a weapon and armour worn."""
        from avarenthia.entities import random_gear
        g, p = self.g, self.p
        while p.lvl < lvl:
            g.gain_xp(max(10, p.lvl * 60))
        while p.stat_pts > 0:
            g.add_stat(self.rng.choice(['str', 'vit', 'vit', 'dex']))
        want = {'weapon', 'armor', 'shield', 'helm', 'boots', 'gloves'}
        best = None                                   # of the weapons it came across, the best one it can use
        for _ in range(500):
            it = random_gear(g, max(1, lvl))
            if it.cursed or g.meets(it):
                continue
            if it.slot == 'weapon':
                if it.dmg and (best is None or sum(it.dmg) > sum(best.dmg)):
                    best = it
                continue
            if it.slot in want:
                it.ided = True
                if g.add_to_inv(it):
                    g.equip(it)
                    want.discard(it.slot)
        if best is not None:
            best.ided = True
            if g.add_to_inv(best):
                g.equip(best)
        from avarenthia.entities import Item
        g.add_to_inv(Item(g.new_id(), 'potion', 'hp', 3))   # what anyone who has played a while carries
        p.life = g.stats()['max_life']
        p.gold += coin
        self.calm()

    def note(self, text):
        self.log.append(f'day {self.g.day}: {text}')

    def crash(self, where):
        tb = traceback.format_exc()
        self.crashes.append(dict(where=where, day=self.g.day, tb=tb[-2500:]))
        self.note(f'CRASH in {where}: {tb.strip().splitlines()[-1]}')
        self.app.screens = [ui.GameScreen(self.app)]
        self.g.pending = None
        self.g.request = None

    def calm(self):
        """Back to the game screen, every question answered."""
        app, g = self.app, self.g
        for _ in range(12):
            if g.pending:
                self.choose(g.pending)
                continue
            if not isinstance(app.top, ui.GameScreen):
                app.key('esc')
                if not isinstance(app.top, ui.GameScreen):
                    app.screens = [ui.GameScreen(app)]
                continue
            break
        app.after_action()

    def choose(self, pend):
        """A question: the bot's own taste, and sometimes just any answer."""
        opts = [(t, v) for t, v in pend.get('options', []) if v is not None]
        if not opts:
            self.g.pending = None
            return
        v = self.pick(pend, opts)
        try:
            EV.resolve(self.g, v)
        except Exception:
            self.crash(f'choice {pend.get("key")}={v}')
        self.app.after_action()

    def pick(self, pend, opts):
        if self.rng.random() < self.sloppy:
            return self.rng.choice(opts)[1]
        good = [v for t, v in opts if v not in ('leave', 'bye', 'no', 'nothing')]
        return good[0] if good else opts[0][1]

    def key(self, tok):
        try:
            self.app.key(tok)
            self.app.render() if self.rng.random() < .05 else None
        except Exception:
            self.crash(f'key {tok}')
        if self.g.pending:
            self.calm()

    def life_frac(self):
        s = self.g.stats()
        return self.p.life / max(1, s['max_life'])

    def dead(self):
        return self.g.dead

    # -------------------------------------------------------------- moving
    def toward(self, x, y):
        p = self.p
        d = (sign(x - p.x), sign(y - p.y))
        if d == (0, 0):
            return False
        self.key(DIR_TOK[d])
        return True

    def fight(self, limit=250):
        """Until no foe is in sight: the nearest first; a potion when low (if the bot remembers)."""
        g, p = self.g, self.p
        n = 0
        while n < limit and not g.dead:
            foes = g.visible_hostiles() if g.cur != 'over' else []
            if not foes:
                break
            n += 1
            if self.life_frac() < .35 and self.rng.random() > self.sloppy:
                before = p.life
                self.key('q')                              # the best health potion of the belt
                if p.life > before:
                    self.stats['potions'] += 1
                    continue
            f = min(foes, key=lambda o: cheb(o.x, o.y, p.x, p.y))
            d = (sign(f.x - p.x), sign(f.y - p.y))
            if d == (0, 0):
                break
            ox, oy = p.x, p.y
            self.key(DIR_TOK[d])
            if (p.x, p.y) == (ox, oy) and cheb(f.x, f.y, p.x, p.y) > 1:
                d2 = self.rng.choice(list(DIR_TOK))         # stuck on a wall: try round it
                self.key(DIR_TOK[d2])
        if n:
            self.stats['fights'] += 1
        return not g.dead

    def after_road(self):
        """Whatever stopped the walk: a fight, a question, a screen."""
        g = self.g
        self.calm()
        if g.cur != 'over' and (g.encounter is not None or getattr(g, 'zone_fight', False) or g.cur == 'wild'):
            self.fight()
            if not g.dead and g.cur != 'over':
                foes = g.visible_hostiles()
                if not foes:
                    try:
                        g.leave_to_over()
                    except Exception:
                        self.crash('leave after a fight')
            self.calm()

    def travel(self, kind, ref, tries=12):
        """Walk to a place along the roads, as T does; fights and questions on the way."""
        g = self.g
        g.mark_visit(kind, ref)
        if kind == 's':
            s = g.world.settlements[ref]
            tx, ty = s.x, s.y
        elif kind == 'd':
            d = g.world.dungeons[ref]
            tx, ty = d.x, d.y
        else:
            st = g.world.sites[ref]
            tx, ty = st.x, st.y
        self.goal = (tx, ty)
        for _ in range(tries):
            if g.dead:
                return False
            if g.cur != 'over':
                try:
                    g.leave_to_over()
                except Exception:
                    self.crash('leave to travel')
                self.calm()
            if g.cur == 'over' and (self.p.x, self.p.y) == (tx, ty):
                return True
            try:
                steps = 0
                for _ in g.travel_iter(kind, ref):
                    steps += 1
                    if steps > 3000:
                        break
                self.stats['steps'] += steps
            except Exception:
                self.crash(f'travel to {kind}{ref}')
                return False
            self.app.after_action()
            self.after_road()
            self.unstick()
        return g.cur == 'over' and (self.p.x, self.p.y) == (tx, ty)

    def unstick(self):
        """What stopped the road: hunger, wounds, someone hostile in sight; as a player would deal with it."""
        g, p = self.g, self.p
        if g.dead or g.cur != 'over':
            return
        from avarenthia import hunger as HU
        if getattr(p, 'food', 500) < HU.HUNGRY:
            try:
                g.eat_best()
                self.stats['meals'] += 1
            except Exception:
                self.crash('eat')
            self.calm()
        if self.life_frac() < .45:
            try:
                g.make_camp()
                self.stats['camps'] += 1
            except Exception:
                self.crash('camp')
            self.calm()
            self.after_road()
        near = [wd for wd in g.world.wanderers if wd.hostile and g.visible(wd.x, wd.y) and cheb(wd.x, wd.y, p.x, p.y) <= 6]
        if near and not g.dead and g.cur == 'over':
            wd = min(near, key=lambda q: cheb(q.x, q.y, p.x, p.y))
            if self.rng.random() < .6:                     # fall on them
                for _ in range(8):
                    if g.cur != 'over' or g.dead or wd not in g.world.wanderers:
                        break
                    self.toward(wd.x, wd.y)
                self.stats['road_fights'] += 1
                self.after_road()
            else:                                          # or wait for them to go
                try:
                    g.end_turn(30, True)
                except Exception:
                    self.crash('wait')
        elif not g.dead and g.cur == 'over' and getattr(self, 'goal', None) and \
                any(wd.hostile and g.visible(wd.x, wd.y) for wd in g.world.wanderers):
            try:                                           # seen far off: walk on by hand, as a player would
                path = g.travel_route(self.goal) or []
            except Exception:
                self.crash('route by hand')
                path = []
            for x, y in path[:12]:
                if g.dead or g.cur != 'over':
                    break
                self.toward(x, y)
            self.stats['by_hand'] += 1
            self.after_road()

    def town_here(self):
        if self.g.cur != 'over':
            return None
        return self.g.world.settlement_at(self.p.x, self.p.y)

    def report(self):
        p = self.p
        return dict(kind=self.kind, seed=self.seed, day=self.g.day, dead=self.g.dead, cause=getattr(self.g, 'cause', None),
                    deaths=getattr(p, 'deaths', 0), lvl=p.lvl, gold=p.gold,
                    stats=dict(self.stats), money=self.money[-40:], crashes=self.crashes, log=self.log[-60:],
                    seconds=round(time.time() - self.start))

    def run(self):
        try:
            self.play()
        except Exception:
            self.crash('play')
        if not self.g.dead:
            try:
                E.save_game(self.g)
                assert E.load_game() is not None
            except Exception:
                self.crash('save and load')
        return self.report()

    def play(self):
        raise NotImplementedError


# ------------------------------------------------------------------ the trader
class Trader(Bot):
    """Buys where a good is cheap and carries it to where it was dear, from the prices it has seen itself. A fifth of
    the time it buys on a hunch, and sometimes it forgets to sell the last of its cargo."""
    kind = 'trader'
    sloppy = .25

    def play(self):
        g, p = self.g, self.p
        w = g.world
        seen = {}                                          # sid -> {good: (buy, sell)}
        p.gold += 100 * 100                                # a purse from a few early jobs, to start a trade with
        here = min(w.settlements, key=lambda s: cheb(s.x, s.y, p.x, p.y) if g.cur == 'over' else 0)
        if g.cur != 'over':
            g.leave_to_over()
            self.calm()
        here = min(w.settlements, key=lambda s: cheb(s.x, s.y, p.x, p.y))
        if not self.travel('s', here.id):
            self.note('could not reach the first town')
        trips = 0
        while g.day < self.days and not g.dead and trips < 60:
            s = self.town_here()
            if s is None:
                s = min(w.settlements, key=lambda q: cheb(q.x, q.y, p.x, p.y))
                if not self.travel('s', s.id):
                    self.note(f'stuck on the way to {s.name}: ' + ' | '.join(t for t, c in g.log[-4:]))
                    break
                continue
            trips += 1
            seen[s.id] = {gk: (ECO.buy_price(s, gk), ECO.sell_price(s, gk)) for gk in s.market if gk in D.GOODS}
            got = 0
            for gk, q in list(p.cargo.items()):
                if q > 0 and (self.rng.random() > .1 or len(p.cargo) == 1):
                    before = p.gold
                    try:
                        ECO.sell(g, s, gk, q)
                    except Exception:
                        self.crash('sell')
                    got += p.gold - before
            self.provision(s)
            spent, bought, dest = self.buy(s, seen)
            self.money.append(dict(day=g.day, town=s.name, sold=got, spent=spent, good=bought, gold=p.gold))
            self.stats['sold'] += got
            self.stats['spent'] += spent
            if dest is None:
                near = sorted([q for q in w.settlements if q.id != s.id and 8 < cheb(q.x, q.y, s.x, s.y) < 60],
                              key=lambda q: cheb(q.x, q.y, s.x, s.y))
                dest = self.rng.choice(near[:6]) if near else self.rng.choice(w.settlements)
            had = dict(p.cargo)
            ok = self.travel('s', dest.id)
            lost = {k: v - p.cargo.get(k, 0) for k, v in had.items() if p.cargo.get(k, 0) < v}
            if lost:
                self.stats['robbed'] += 1
                self.note(f'lost cargo on the road to {dest.name}: {lost}')
            if not ok:
                self.stats['failed_trips'] += 1
                self.note(f'did not reach {dest.name}: ' + ' | '.join(t for t, c in g.log[-4:]))
                blk = [(wd.kind, wd.name, (wd.x, wd.y), getattr(wd, 'path_i', None), len(getattr(wd, 'path', []) or []))
                       for wd in g.world.wanderers if cheb(wd.x, wd.y, p.x, p.y) <= 1]
                self.note(f'  beside me: {blk}')
            if p.life < g.stats()['max_life'] * .5 and self.town_here():
                self.inn()

    def provision(self, s):
        """Bread for the road, most of the time; potions now and then."""
        g, p = self.g, self.p
        if self.rng.random() < self.sloppy * .6:
            return                                         # forgot to buy food
        from avarenthia.engine import supplies
        sup = supplies(g, s.id)
        food = sum(1 for it in p.inv if it.k == 'food')
        for i, (k, t) in enumerate(sup):
            want = (k == 'food' and t in ('bread', 'ration') and food < 6) or (k == 'potion' and t == 'hp' and
                                                                               self.rng.random() < .3)
            if want:
                before = p.gold
                try:
                    for _ in range(3 if k == 'food' else 1):
                        g.buy_supply(i, s.id)
                except Exception:
                    self.crash('buy supplies')
                self.stats['provisions'] += before - p.gold
        self.calm()

    def buy(self, s, seen):
        g, p = self.g, self.p
        best, dest = None, None
        for gk in s.market:
            if gk not in D.GOODS or ECO.units(s, gk) < 3:
                continue
            bp = ECO.buy_price(s, gk)
            for sid, pr in seen.items():
                if sid == s.id or gk not in pr:
                    continue
                gain = pr[gk][1] - bp
                if gain > 0 and (best is None or gain > best[0]):
                    best, dest = (gain, gk), g.world.settlements[sid]
        if best is None or self.rng.random() < self.sloppy:
            goods = [gk for gk in s.market if gk in D.GOODS and ECO.units(s, gk) >= 3]
            if not goods:
                return 0, None, None
            gk = min(goods, key=lambda k: ECO.buy_price(s, k) / D.GOODS[k]['base']) if self.rng.random() < .5 \
                else self.rng.choice(goods)
            dest = None if best is None else dest
        else:
            gk = best[1]
        bp = ECO.buy_price(s, gk)
        n = int(p.gold * .7 // max(1, bp))
        n = min(n, int(ECO.free_cargo(p) // max(1, D.GOODS[gk]['w'])))
        if n <= 0:
            return 0, None, dest
        before = p.gold
        try:
            ECO.buy(g, s, gk, n)
        except Exception:
            self.crash('buy')
        return before - p.gold, gk, dest

    def inn(self):
        g = self.g
        before = self.p.gold
        try:
            g.rest()
        except Exception:
            self.crash('rest')
        self.calm()
        self.stats['inn'] += before - self.p.gold


# ------------------------------------------------------------------ the fighter
class Fighter(Bot):
    """Goes down the nearest dungeon, fights what it finds, comes up to sell, mend and rest. It sometimes stays
    one fight too long."""
    kind = 'fighter'
    sloppy = .2

    def play(self):
        g, p = self.g, self.p
        w = g.world
        self.veteran(3, 2000)
        trips = 0
        while g.day < self.days and not g.dead and trips < 25:
            trips += 1
            if g.cur != 'over':
                g.leave_to_over()
                self.calm()
            ds = sorted(w.dungeons.values(), key=lambda d: cheb(d.x, d.y, p.x, p.y))
            d = ds[min(len(ds) - 1, self.rng.randrange(2))]
            if not self.travel('d', d.id):
                self.note(f'could not reach {d.name}')
                continue
            try:
                g.use_stairs('down')
            except Exception:
                self.crash('into the dungeon')
            self.calm()
            if g.cur == 'over':
                continue
            self.dive(d)
            if g.dead:
                break
            self.home()

    def dive(self, d):
        g, p = self.g, self.p
        floors = 0
        for _ in range(6):
            if g.dead:
                return
            for _step in range(600):
                if g.dead:
                    return
                if g.visible_hostiles():
                    self.fight()
                    continue
                if self.life_frac() < .3 and self.rng.random() > self.sloppy:
                    self.note(f'turns back low on life on floor {floors + 1} of {d.name}')
                    return
                try:
                    st = next(g.explore_iter(), None)
                except Exception:
                    self.crash('explore')
                    st = None
                self.calm()
                if st is None and not g.visible_hostiles():
                    break
            floors += 1
            self.stats['floors'] += 1
            if not self.stairs_down():
                return
            if p.lvl < floors * 2 and self.rng.random() > self.sloppy:
                return

    def stairs_down(self):
        """Walk to the stairs down and take them (a short breadth-first walk)."""
        g, p = self.g, self.p
        m = g.map
        goal = next(((x, y) for y in range(m.h) for x in range(m.w) if m.tile(x, y) == E.DOWN
                     and m.seen[y * m.w + x]), None)
        if goal is None:
            return False
        path = bfs(m, (p.x, p.y), goal)
        for c in path[1:]:
            if g.dead or g.visible_hostiles():
                self.fight()
            self.toward(*c)
        if (p.x, p.y) != goal:
            return False
        key = g.cur
        try:
            g.use_stairs('down')
        except Exception:
            self.crash('stairs down')
        self.calm()
        return g.cur != key

    def home(self):
        """Up to the nearest town: sell the loot, mend, rest at the inn, buy potions."""
        g, p = self.g, self.p
        w = g.world
        if g.cur != 'over':
            try:
                g.leave_to_over()
            except Exception:
                self.crash('out of the dungeon')
            self.calm()
        s = min(w.settlements, key=lambda q: cheb(q.x, q.y, p.x, p.y))
        if not self.travel('s', s.id):
            return
        before = p.gold
        for it in [it for it in p.inv if it.k == 'gear' and not g.is_equipped(it)]:
            try:
                g.sell(it)
            except Exception:
                self.crash('sell gear')
        self.stats['loot'] += p.gold - before
        before = p.gold
        try:
            g.repair_all()
        except Exception:
            self.crash('repair')
        self.stats['repairs'] += before - p.gold
        before = p.gold
        try:
            g.rest()
        except Exception:
            self.crash('rest')
        self.calm()
        self.stats['inn'] += before - p.gold
        self.money.append(dict(day=g.day, gold=p.gold, lvl=p.lvl))


def bfs(m, a, b):
    from collections import deque
    prev = {a: None}
    q = deque([a])
    while q:
        c = q.popleft()
        if c == b:
            break
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                n = (c[0] + dx, c[1] + dy)
                if n not in prev and m.inb(*n) and (D.TILES[m.tile(*n)].walk or D.TILES[m.tile(*n)].door or n == b):
                    prev[n] = c
                    q.append(n)
    if b not in prev:
        return [a]
    out = [b]
    while prev[out[-1]] is not None:
        out.append(prev[out[-1]])
    return out[::-1]


# ------------------------------------------------------------------ the explorer
class Explorer(Bot):
    """Walks off the road toward land it has not seen, goes into what it passes (sites, camps, holds), and leaves
    again. It walks on at night more than it should."""
    kind = 'explorer'
    sloppy = .3

    def play(self):
        g, p = self.g, self.p
        om = g.maps['over']
        self.veteran(3, 2000)
        if g.cur != 'over':
            g.leave_to_over()
            self.calm()
        moves = 0
        while g.day < self.days and not g.dead and moves < 9000:
            if g.cur != 'over':
                self.after_road()
                if g.cur != 'over':
                    try:
                        g.leave_to_over()
                    except Exception:
                        self.crash('leave')
                    self.calm()
                continue
            tx, ty = p.x + self.rng.randint(-40, 40), p.y + self.rng.randint(-25, 25)
            tx, ty = max(1, min(om.w - 2, tx)), max(1, min(om.h - 2, ty))
            for _ in range(60):
                if g.dead or g.cur != 'over':
                    break
                moves += 1
                ox, oy = p.x, p.y
                if not self.toward(tx, ty):
                    break
                if (p.x, p.y) == (ox, oy):
                    self.key(DIR_TOK[self.rng.choice(list(DIR_TOK))])
                self.peek()
            if self.life_frac() < .4 and g.cur == 'over':
                self.camp()

    def peek(self):
        """Something here? Go in, look round, come out."""
        g, p = self.g, self.p
        from avarenthia import sites as ST
        from avarenthia import camps as CM
        here = []
        if ST.site_at(g.world, p.x, p.y):
            here.append('site')
        if CM.at(g, p.x, p.y):
            here.append('camp')
        if not here or self.rng.random() < .3:
            return
        key = g.cur
        try:
            g.use_stairs('down')
        except Exception:
            self.crash(f'into a {here[0]}')
        self.calm()
        if g.cur != key:
            self.stats['went_in:' + here[0]] += 1
            for _ in range(30):
                if g.dead:
                    return
                if g.visible_hostiles():
                    self.fight(60)
                    break
                self.key(DIR_TOK[self.rng.choice(list(DIR_TOK))])
            if not g.dead and g.cur != 'over':
                try:
                    g.leave_to_over()
                except Exception:
                    self.crash('out again')
                self.calm()

    def camp(self):
        try:
            self.g.make_camp()
        except Exception:
            self.crash('camp')
        self.calm()
        self.after_road()
        self.stats['camps'] += 1


# ------------------------------------------------------------------ the homeowner
class Homeowner(Bot):
    """Saves up, buys a house in a town, furnishes it, then stakes a home out on the land and builds it up. Forgets
    the hearth tax now and then."""
    kind = 'homeowner'
    sloppy = .3

    def play(self):
        from avarenthia import homes as HM
        g, p = self.g, self.p
        w = g.world
        p.gold += 400 * 100 * 100                          # the savings of a career
        towns = sorted([s for s in w.settlements if s.kind in HM.FOR_SALE], key=lambda s: cheb(s.x, s.y, p.x, p.y))
        bought = None
        for s in towns[:6]:
            if not self.travel('s', s.id):
                continue
            g.enter_town(s.id)
            self.calm()
            sale = dict(getattr(g.map, 'sale', {}) or {})
            if not sale:
                continue
            door = next(iter(sale))
            try:
                HM.ask_buy(g, door)
                if g.pending:
                    EV.resolve(g, 'buy')
            except Exception:
                self.crash('buy a house')
            self.calm()
            if HM.homes(g):
                bought = HM.homes(g)[-1]
                self.note(f'bought a house in {s.name} for {sale[door] if isinstance(sale[door], int) else "?"}')
                break
        if bought is None:
            self.note('found no house for sale')
        gold0 = p.gold
        # a stake out on the land, built up stage by stage
        try:
            g.leave_to_over()
        except Exception:
            pass
        self.calm()
        built = None
        for _ in range(40):
            if g.cur == 'over' and not HM.stake_spot(g, p.x, p.y):
                break
            self.key(DIR_TOK[self.rng.choice(list(DIR_TOK))])
        try:
            stake = HM.stake_item(g)
            g.add_to_inv(stake)
            if HM.drive_stake(g, stake):
                built = HM.homes(g)[-1]
        except Exception:
            self.crash('drive a stake')
        self.calm()
        if built:
            self.note(f'staked a home out on the land at {built["x"]},{built["y"]}')
        week = 0
        while g.day < self.days and not g.dead:
            week += 1
            try:
                g.turn += 7 * D.DAY_LEN
                g.end_turn(0, quiet=True)
            except Exception:
                self.crash('a week passes')
            self.calm()
            for h in HM.homes(g):
                try:
                    if HM.owed(g, h) and self.rng.random() > self.sloppy:
                        HM.settle(g, h)
                        self.stats['tax_paid'] += 1
                    elif HM.owed(g, h):
                        self.stats['tax_forgotten'] += 1
                except Exception:
                    self.crash('the hearth tax')
            if built and built in HM.homes(g) and week % 2 == 0:
                try:
                    opts = HM.build_options(g, built)
                    ok = [v for t, v in opts if v]
                    if ok:
                        HM.start_build(g, built, ok[-1] == 'buildcart' and 'build' not in ok)
                        self.stats['builds'] += 1
                except Exception:
                    self.crash('build on')
            for h in HM.homes(g):
                st = h.get('state')
                if st and st != 'quiet':
                    self.stats['home:' + st] += 1
            self.money.append(dict(day=g.day, gold=p.gold, homes=len(HM.homes(g))))
        self.stats['spent_on_homes'] = gold0 - p.gold
        self.note('homes at the end: ' + ', '.join(f'{h["kind"]} {h.get("stage")} ({h.get("state")})' for h in HM.homes(g)))


# ------------------------------------------------------------------ the knight
class Knight(Bot):
    """Swears to a king, answers the call to war: the camps, a siege, the field battle with whatever task the
    captain gives."""
    kind = 'knight'
    sloppy = .25

    def play(self):
        from avarenthia import wars as WR, debug as DBG, camps as CM, missions as MS
        g, p = self.g, self.p
        self.veteran(9, 50 * 100 * 100)
        w = g.world
        R = w.realm
        if g.cur != 'over':
            g.leave_to_over()
            self.calm()
        war = DBG.war_start(g)
        if war is None:
            self.note('no war could start in this world')
            return
        kg = R.kingdoms[war['a']]
        p.knight = dict(lid=kg.king, kid=kg.id, day=g.day, word='Ser', calls=0)
        self.note(f'sworn to {kg.short}, at war with {R.kingdoms[war["b"]].short}')
        fields = 0
        for month in range(max(1, self.days // 15)):
            if g.dead or war not in R.wars:
                break
            # the field, if one is called
            job = next((m for m in MS.active(g) if m.kind == 'realm' and m.data.get('task') == 'field'), None)
            if job is None and self.rng.random() < .5:
                war['field'] = None
                DBG.war_field(g)
                job = next((m for m in MS.active(g) if m.kind == 'realm' and m.data.get('task') == 'field'), None)
            fd = war.get('field')
            if fd and fd.get('state') == 'pending':
                p.x, p.y = fd['x'], fd['y']
                try:
                    g.use_stairs('down')
                except Exception:
                    self.crash('to the field')
                self.calm()
                if getattr(g.map, 'battle', None):
                    fields += 1
                    self.battle()
            # a camp of the enemy by night
            if self.rng.random() < .5 and not g.dead:
                try:
                    c = DBG.camp_in(g, 'host', 'foe')
                    self.stats['camps_sneaked'] += 1
                    m = g.map
                    for (x, y), what in list(m.cthings.items())[:3]:
                        CM.bump(g, x, y)
                        self.calm()
                    self.fight(80)
                    if not g.dead and g.cur != 'over':
                        g.leave_to_over()
                    self.calm()
                    self.note(f'sneaked into {c["name"]}: {c["done"]}, alarm {c["alarm"]}')
                except Exception:
                    self.crash('a camp by night')
            try:
                g.turn += 15 * D.DAY_LEN
                g.end_turn(0, quiet=True)
            except Exception:
                self.crash('time')
            self.calm()
            if self.life_frac() < .5:
                try:
                    p.life = g.stats()['max_life']
                except Exception:
                    pass
        self.stats['fields'] = fields
        self.stats['war_score'] = war['score']
        self.note(f'the war: score {war["score"]}, ' + ('over' if war not in R.wars else 'still on'))
        self.note(f'your part: {WR.mine(g)}')

    def battle(self):
        g, p = self.g, self.p
        m = g.map
        bt = m.battle
        for n in range(500):
            if g.dead or g.cur != m.key or bt['done']:
                break
            if self.rng.random() < .02 and bt['result'] is None and n > 60:
                self.note('walked off the field before the end')
                g.leave_to_over()
                self.calm()
                return
            line = bt['front'][max(0, min(m.w - 1, p.x))]
            foes = g.visible_hostiles()
            near = [o for o in foes if cheb(o.x, o.y, p.x, p.y) <= 6]
            if self.life_frac() < .3:
                before = p.life
                self.key('q')
                if p.life > before:
                    self.stats['potions'] += 1
                    continue
                if self.rng.random() > self.sloppy:
                    self.toward(p.x, p.y + 1)                 # no potion: back behind your own line
                    continue
            if near and (sum(1 for o in near if cheb(o.x, o.y, p.x, p.y) <= 1) < 3 or self.rng.random() < self.sloppy):
                f = min(near, key=lambda o: cheb(o.x, o.y, p.x, p.y))
                self.toward(f.x, f.y)
            elif near:
                self.toward(p.x, p.y + 1)                     # too many on you: give ground to your line
            elif bt['task'] in ('captain', 'mage') and foes:
                f = min(foes, key=lambda o: cheb(o.x, o.y, p.x, p.y))
                self.toward(f.x, f.y)
            elif p.y < line + 2:
                self.toward(p.x + self.rng.randint(-1, 1), p.y + 1)
            else:
                self.toward(p.x + self.rng.randint(-1, 1), p.y)
        self.stats['field_' + str(bt.get('result'))] += 1
        self.note(f'field battle: task {bt["task"]}, {bt["kills"]} fell to the bot, result {bt["result"]} '
                  f'(after {bt["n"]} actions, phase {bt["phase"]}, now on {g.cur}, life {p.life})')
        if not g.dead and g.cur != 'over':
            g.leave_to_over()
            self.calm()


# ------------------------------------------------------------------ the careless newbie
class Newbie(Bot):
    """Presses what looks good: walks, opens every screen, answers whatever, buys and sells at random, never reads
    the handbook. Looks for crashes and dead ends."""
    kind = 'newbie'
    sloppy = .7
    TOKS = ['up', 'down', 'left', 'right', 'np7', 'np9', 'np1', 'np3'] * 6 + \
        ['enter', 'esc', '>', '<', 'i', 'c', 'm', 'j', 'T', 'R', 'g', 'e', 'q', 'w', '1', '2', 'tab', 'x', 'a', 'b',
         'H', '?', 'L', 'f', 's', 'd', 'z', '3', '4', '5']

    def play(self):
        g = self.g
        for i in range(4000):
            if g.dead or g.day > self.days:
                break
            tok = self.rng.choice(self.TOKS)
            self.key(tok)
            if not self.app.running:
                self.app.running = True
            if i % 400 == 399:
                self.calm()
            if getattr(self.app, 'auto', None):
                try:
                    self.app.stop_auto()
                except Exception:
                    self.crash('stop auto')
        if g.dead:
            self.note(f'died: {getattr(g, "death_cause", None) or getattr(self.p, "killed_by", "?")}')
        self.stats['keys'] = i

# ------------------------------------------------------------------ the gambler
class Gambler(Bot):
    """Goes from inn to inn and plays at the gaming table: Bones and The Count in the evening, Vigil at any hour.
    Presses the keys a player presses at a table, and some it should not."""
    kind = 'gambler'
    sloppy = .35
    TOKS = ['enter', 'enter', 'enter', 'left', 'right', 'up', 'down', 'up', 'down', 'np4', 'np6', 'np8', 'np2',
            'space', 'tab', 'x', 'esc']

    def play(self):
        from avarenthia import inngames as IG, debug_tests as DT
        g, p = self.g, self.p
        self.veteran(2, 30 * 100)
        gold0 = p.gold
        for n in range(max(6, self.days)):
            if g.dead or g.day >= self.days:
                break
            try:
                DT.s_inn(g, n, 'master' if n % 5 == 4 else None)
            except Exception:
                self.crash('to an inn')
            self.calm()
            if getattr(g.map, 'gametable', None) is None:
                self.stats['no_table'] += 1
                continue
            if n % 3:
                h = (g.turn % D.DAY_LEN) * 24 // D.DAY_LEN
                g.turn += ((20 - h) % 24) * D.DAY_LEN // 24
                g.end_turn(0, quiet=True)
                self.calm()
            for _round in range(self.rng.randint(1, 4)):
                if g.dead:
                    break
                gt = g.map.gametable
                if max(abs(gt[0] - p.x), abs(gt[1] - p.y)) > 1:
                    break
                try:
                    IG.table(g)
                except Exception:
                    self.crash('the table')
                pend = g.pending
                if not pend:
                    break
                opts = [v for t, v in pend.get('options', []) if v and v != 'leave']
                v = self.rng.choice(opts) if opts else 'leave'
                try:
                    EV.resolve(g, v)
                    self.app.after_action()
                except Exception:
                    self.crash(f'table {v}')
                self.stats['game:' + v] += 1
                top = self.app.top
                for k in range(400):
                    if isinstance(self.app.top, ui.GameScreen) or self.app.top is not top:
                        break
                    tok = self.rng.choice(self.TOKS[:-1] if self.rng.random() > .02 else self.TOKS)
                    vg = getattr(self.app.top, 'v', None)
                    if vg is not None and not vg.winner and vg.turn == vg.you and self.rng.random() < .8:
                        mvs = vg.moves(vg.you)
                        if mvs:                            # a move of its own on the board, by the cursor
                            f, t = self.rng.choice(mvs)
                            self.app.top.held = (f % IG.N, f // IG.N)
                            self.app.top.cur = (t % IG.N, t // IG.N)
                            tok = 'enter'
                    try:
                        self.app.key(tok)
                        self.app.render()
                    except Exception:
                        self.crash(f'{v} key {tok}')
                        break
                else:
                    self.stats['game_unended'] += 1
                    self.note(f'{v}: 400 keys and still at the table')
                self.calm()
            self.money.append(dict(day=g.day, gold=p.gold))
        self.stats['won_or_lost'] = p.gold - gold0
        self.note(f'games: {getattr(p, "games", None) if not isinstance(getattr(p, "games", None), dict) else {k: v for k, v in p.games.items() if not isinstance(v, (dict, list))}}')


# ------------------------------------------------------------------ the camper
class Camper(Bot):
    """Walks into camps of every people as friend, stranger and foe, by day and night, bumps into every telling thing
    and tent, and leaves; sometimes it starts a fight it should not."""
    kind = 'camper'
    sloppy = .3

    def play(self):
        from avarenthia import debug as DBG, camps as CM
        g, p = self.g, self.p
        self.veteran(6, 500 * 100)
        styles = list(CM.STYLES)
        rels = ['friend', 'stranger', 'foe', None]
        for n in range(max(10, self.days * 2)):
            if g.dead or g.day >= self.days:
                break
            st, rel = self.rng.choice(styles), self.rng.choice(rels)
            try:
                c = DBG.camp_in(g, st, rel)
            except Exception:
                self.crash(f'camp {st}/{rel}')
                self.calm()
                continue
            self.calm()
            self.stats[f'camp:{st}'] += 1
            m = g.map
            for _ in range(150):
                if g.dead or g.map is not m:
                    break
                things = list(getattr(m, 'cthings', {}).items())
                if things and self.rng.random() < .3:
                    (x, y), _what = self.rng.choice(things)
                    for _s in range(30):
                        if cheb(x, y, p.x, p.y) <= 1 or g.map is not m or g.dead:
                            break
                        ox, oy = p.x, p.y
                        self.toward(x, y)
                        if (ox, oy) == (p.x, p.y):
                            self.key(DIR_TOK[self.rng.choice(list(DIR_TOK))])
                    if cheb(x, y, p.x, p.y) <= 1 and g.map is m:
                        try:
                            CM.bump(g, x, y)
                        except Exception:
                            self.crash(f'bump {_what} in {st}')
                        self.calm()
                        self.stats['bumps'] += 1
                else:
                    self.key(self.rng.choice(list(DIR_TOK.values()) * 3 + ['>', '<', 'e', 'g', 'R']))
                if g.visible_hostiles() and self.rng.random() < .5:
                    self.fight(60)
                if self.rng.random() < .03:
                    break
            if not g.dead and g.cur != 'over':
                try:
                    g.leave_to_over()
                except Exception:
                    self.crash(f'out of a camp {st}')
                self.calm()
            if self.life_frac() < .5 and not g.dead:
                p.life = g.stats()['max_life']
            if n % 4 == 3:
                try:
                    g.turn += D.DAY_LEN // 2
                    g.end_turn(0, quiet=True)
                except Exception:
                    self.crash('half a day')
                self.calm()


# ------------------------------------------------------------------ the roamer
class Roamer(Trader):
    """A trader with wagons of its own, who goes far, leaves the wagons in a town now and then, and saves and loads
    the game every few towns (as a player who quits often)."""
    kind = 'roamer'
    sloppy = .3

    def play(self):
        from avarenthia import caravan as CV
        g, p = self.g, self.p
        self.veteran(4, 3000 * 100)
        p.mounts = list(set(list(getattr(p, 'mounts', []) or []) + ['cart']))
        w = g.world
        if g.cur != 'over':
            g.leave_to_over()
            self.calm()
        for hop in range(40):
            if g.dead or g.day >= self.days:
                break
            far = [s for s in w.settlements if 30 < cheb(s.x, s.y, p.x, p.y) < 120]
            dest = self.rng.choice(far or w.settlements)
            had = dict(p.cargo)
            ok = self.travel('s', dest.id)
            self.stats['hops'] += 1
            if not ok:
                self.stats['failed_trips'] += 1
                self.note(f'did not reach {dest.name}: ' + ' | '.join(t for t, c in g.log[-3:]))
                continue
            s = self.town_here()
            if s is None:
                continue
            try:
                g.enter_town(s.id)
            except Exception:
                self.crash('enter town')
            self.calm()
            cv = CV.get(p)
            if (not cv or len(cv['wagons']) < CV.most(g)) and self.rng.random() < .6:
                try:
                    CV.buy_wagon(g, self.rng.choice(list(CV.BEASTS)))
                    self.stats['wagons'] += 1
                except Exception:
                    self.crash('buy a wagon')
            for gk, q in list(p.cargo.items()):
                if q > 0:
                    try:
                        ECO.sell(g, s, gk, q)
                    except Exception:
                        self.crash('sell')
            self.provision(s)
            self.buy(s, {})
            if self.rng.random() < .2 and cv:
                try:
                    CV.leave(g, ('s', s.id))
                    self.stats['left_wagons'] += 1
                except Exception:
                    self.crash('leave the wagons')
            elif cv and cv.get('at') is not None and self.rng.random() < .7:
                try:
                    CV.rejoin(g)
                except Exception:
                    self.crash('rejoin')
            self.calm()
            if hop % 3 == 2:
                try:
                    E.save_game(g)
                    g2 = E.load_game()
                    assert g2 is not None
                    self.app.game = g2
                    self.app.screens = [ui.GameScreen(self.app)]
                    self.g = g = g2
                    self.p = p = g2.player
                    self.app.render()
                    self.stats['reloads'] += 1
                except Exception:
                    self.crash('save, load and play on')
            try:
                g.leave_to_over()
            except Exception:
                self.crash('out of town')
            self.calm()
            self.money.append(dict(day=g.day, gold=p.gold, wagons=len((CV.get(p) or {}).get('wagons', []))))


# ------------------------------------------------------------------ the masher
class Masher(Newbie):
    """The newbie's keys, in every kind of place the new rounds made (a town, a camp, a home, a field battle, a deep
    level), with the screen drawn after every key."""
    kind = 'masher'
    sloppy = .8
    TOKS = Newbie.TOKS + ['f1', 'f5', 'O', 'S', 'C', 'D', 'G', 'I', 'J', 'K', 'M', 'N', 'P', 'Q', 'U', 'V', 'W',
                          'X', 'Y', 'Z', 'space', 'backspace', 'home', 'end', 'pageup', 'pagedown', '6', '7', '0', 'l',
                          'h', 'k', 'n', 'o', 'p', 'r', 't', 'u', 'v', 'y', ',', '.', ';', '/', '-', '=']

    def play(self):
        from avarenthia import debug as DBG, debug_tests as DT, homes as HM
        g = self.g
        self.veteran(5, 2000 * 100)
        places = ['town', 'camp', 'inn', 'home', 'field', 'dungeon', 'over']
        for i in range(max(8, self.days)):
            if g.dead or g.day > self.days:
                break
            where = places[i % len(places)]
            try:
                if where == 'town':
                    s = self.rng.choice(g.world.settlements)
                    DBG.teleport(g, ('s', s.id))
                elif where == 'camp':
                    DBG.camp_in(g, self.rng.choice(['host', 'dwarf', 'elf', 'gorvash', 'sea', 'riders', 'traders',
                                                    'siege']), self.rng.choice(['friend', 'stranger', 'foe']))
                elif where == 'inn':
                    DT.s_inn(g, i)
                elif where == 'home':
                    DBG.home_stake(g)
                    if HM.homes(g):
                        h = HM.homes(g)[-1]
                        DBG.to_over(g, h['x'], h['y'])
                        g.use_stairs('down')
                elif where == 'field':
                    from avarenthia import wars as WR
                    war = DBG.war_start(g)
                    if war:
                        war['field'] = None
                        DBG.war_field(g)
                        fd = war.get('field')
                        if fd:
                            DBG.to_over(g, fd['x'], fd['y'])
                            g.use_stairs('down')
                elif where == 'dungeon':
                    ds = g.world.dungeons
                    d = self.rng.choice(list(ds.values()) if isinstance(ds, dict) else ds)
                    DBG.teleport(g, ('d', d.id))
                else:
                    if g.cur != 'over':
                        g.leave_to_over()
            except Exception:
                self.crash(f'to a {where}')
            self.calm()
            self.stats['place:' + where] += 1
            for k in range(300):
                if g.dead:
                    break
                tok = self.rng.choice(self.TOKS)
                try:
                    self.app.key(tok, self.rng.random() < .15)
                    self.app.render()
                except Exception:
                    self.crash(f'{where}: key {tok} on {type(self.app.top).__name__}')
                if not self.app.running:
                    self.app.running = True
                if g.pending and self.rng.random() < .5:
                    self.calm()
                if getattr(self.app, 'auto', None):
                    try:
                        self.app.stop_auto()
                    except Exception:
                        self.crash('stop auto')
            self.calm()
            if g.dead:
                break
            g.player.life = g.stats()['max_life']
        self.stats['keys'] = i


TYPES = {'trader': Trader, 'fighter': Fighter, 'explorer': Explorer, 'homeowner': Homeowner, 'knight': Knight,
         'newbie': Newbie, 'gambler': Gambler, 'camper': Camper, 'roamer': Roamer, 'masher': Masher}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    days = 60
    seed = 7
    for i, a in enumerate(sys.argv):
        if a == '--days':
            days = int(sys.argv[i + 1])
        if a == '--seed':
            seed = int(sys.argv[i + 1])
    kinds = [a for a in args if a in TYPES] or list(TYPES)
    out = []
    for k in kinds:
        print(f'== {k}', flush=True)
        try:
            bot = TYPES[k](seed, days)
        except Exception:
            print(traceback.format_exc())
            out.append(dict(kind=k, crashes=[dict(where='new game', tb=traceback.format_exc())]))
            continue
        r = bot.run()
        out.append(r)
        print(json.dumps({x: r.get(x) for x in ('kind', 'day', 'dead', 'cause', 'deaths', 'lvl', 'gold', 'stats', 'seconds')}, default=str),
              flush=True)
        for line in r['log'][-12:]:
            print('  ', line)
        for c in r['crashes'][:5]:
            print('   CRASH', c['where'], '\n', c['tb'][-1200:])
    path = os.environ.get('PLAYTEST_OUT')
    if path:
        with open(path, 'w') as f:
            json.dump(out, f, indent=1, default=str)


if __name__ == '__main__':
    main()
