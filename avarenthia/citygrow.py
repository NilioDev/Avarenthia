"""Cities that grew (round 24): human cities and the metropolis grow as old European towns grew, round a heart that
fits who rules them, with winding streets, row houses that share their walls, the line of an old wall as a ring
street, a wall with towers and a broad moat, a tamed river with quay walls and stone bridges. Flat harbour cities
get canal rings; border cities a bastioned wall. Made from the mockups Nilio approved (project files, steden/);
the rules he set are checked by `rules` (test part city_rules)."""
import math
import random
from collections import deque

from . import data as D
from .entities import GameMap

G, WALLT, FLOOR, PLANK, DOOR = D.GRASS, D.WALL, D.FLOOR, D.PLANK, D.DOOR
STREET, LANE, WATER, BRIDGE = D.ROAD, D.PATH, D.WATER, D.BRIDGE
STREETS = (STREET, LANE, BRIDGE)


class City:
    def __init__(self, key, name, w, h):
        self.W, self.H = w, h
        self.m = GameMap(key, 'town', name, w, h, G)
        self.houses = []                    # [x0, y0, x1, y1, door] of every house in a row
        self.great = []                     # (kind, (x, y, w, h), door) of the great buildings
        self.inside = bytearray(self.W * self.H)      # within the city wall
        self.reserved = bytearray(self.W * self.H)    # squares, great buildings, water: no houses here
        self.level = {}                     # street cell -> 0 main, 1 street, 2 lane
        self.dirs = {}                      # street cell -> direction it runs
        self.river = set()                  # the river's cells: only crossings of it get a stone bridge
        self.piers = set()                  # wooden jetties stay wood
        self.moat = set()
        self.deck, self.parapet, self.quaywall, self.planned = set(), set(), set(), []
        self.stalls, self.exits, self.gates = [], [], []
        self.cx, self.cy = w // 2, h // 2

    def t(self, x, y):
        return self.m.t[y * self.W + x]

    def set(self, x, y, k):
        if 0 <= x < self.W and 0 <= y < self.H:
            self.m.t[y * self.W + x] = k

    def ok(self, x, y):
        return 0 <= x < self.W and 0 <= y < self.H

    # ---------------------------------------------------------------- streets
    def street(self, pts, width, level, over_water=True):
        """Draw a street along a polyline. Over water it becomes a bridge: always for the great ways;
        with over_water='cross' only where the street crosses the water, never where it runs along it."""
        if over_water in ('cross', True):
            pts = self.through_bridges(pts, level)
        steps = []
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            n = max(1, int(math.hypot(bx - ax, by - ay) * 2))
            dx, dy = (bx - ax), (by - ay)
            ln = math.hypot(dx, dy) or 1
            d = (dx / ln, dy / ln)
            px = py = None
            for i in range(n + 1):
                x, y = ax + dx * i / n, ay + dy * i / n
                cx, cy = int(round(x)), int(round(y))
                if px is not None and cx != px and cy != py:      # keep lanes 4-connected
                    steps.append((cx, py, 1, d))
                steps.append((cx, cy, width, d))
                px, py = cx, cy
        wet = [self.ok(x, y) and self.t(x, y) in (WATER, D.SHALLOW, BRIDGE) for x, y, _, _ in steps]
        if over_water is True and level == 0:
            over_water = 'cross'            # a great way crosses the river; it never runs along in it
        ok = [over_water] * len(steps)
        if over_water == 'cross':
            i = 0
            while i < len(steps):
                if not wet[i]:
                    ok[i] = False
                    i += 1
                    continue
                j = i
                while j < len(steps) and wet[j]:
                    j += 1
                if all(self.t(x, y) == BRIDGE for x, y, _, _ in steps[i:j]):
                    pass                        # it runs over a bridge laid before it
                elif not any((x, y) in self.river for x, y, _, _ in steps[i:j]):
                    pass                        # a moat or a canal: its bridge is laid on its own
                elif j < len(steps):
                    if i > 0:
                        before = steps[i - 1][:2]
                    else:                       # the street starts at the water's edge
                        d = steps[0][3]
                        before = (int(round(steps[0][0] - d[0] * 2)), int(round(steps[0][1] - d[1] * 2)))
                    if j - i <= 7 and not any((x, y) in self.river for x, y, _, _ in steps[i:j]):
                        # a moat or a ditch: a drawbridge of planks straight across
                        (x0, y0), (x1, y1) = before, steps[j][:2]
                        m = max(abs(x1 - x0), abs(y1 - y0), 1)
                        for k in range(m + 1):
                            self._pave(int(round(x0 + (x1 - x0) * k / m)), int(round(y0 + (y1 - y0) * k / m)),
                                       width, 0, steps[i][3], 'always')
                    else:
                        self.cross(before, steps[i][:2], steps[j][:2], width, level)
                for k in range(i, j):
                    ok[k] = False
                i = j
        for (x, y, w, d), o in zip(steps, ok):
            self._pave(x, y, w, level, d, o)

    def wet_at(self, x, y):
        return self.ok(x, y) and self.t(x, y) in (WATER, D.SHALLOW, BRIDGE)

    def flow(self, px, py, r=8):
        """Which way the water runs at (px, py): the long axis of the water round it, as a unit vector."""
        pts = [(x, y) for y in range(py - r, py + r + 1) for x in range(px - r, px + r + 1)
               if (x - px) ** 2 + (y - py) ** 2 <= r * r and (self.wet_at(x, y) or (x, y) in self.__dict__.get('quaywall', ()))]
        if len(pts) < 5:
            return None
        mx = sum(x for x, _ in pts) / len(pts)
        my = sum(y for _, y in pts) / len(pts)
        sxx = sum((x - mx) ** 2 for x, _ in pts)
        syy = sum((y - my) ** 2 for _, y in pts)
        sxy = sum((x - mx) * (y - my) for x, y in pts)
        ang = .5 * math.atan2(2 * sxy, sxx - syy)
        return math.cos(ang), math.sin(ang)

    def across(self, px, py, d, least=40):
        """A bridge must cross the water, never run along it: at least `least` degrees off the way it flows."""
        f = self.flow(int(round(px)), int(round(py)))
        if f is None:
            return True
        cos = abs(d[0] * f[0] + d[1] * f[1]) / math.hypot(*d)
        return cos <= math.cos(math.radians(least))

    def cross(self, before, entry, after, width, level):
        """A street reaches the river at entry and goes on at after. Inside the walls the bridges were laid first
        (through_bridges brings the great ways onto them): a street that meets no bridge ends at the quay.
        Outside the walls a road lays its own bridge, straight or at 45 degrees, and bends onto both ends."""
        ex, ey = entry
        if self.ok(ex, ey) and self.inside[ey * self.W + ex]:
            return True
        mx, my = (ex + after[0]) // 2, (ey + after[1]) // 2
        if not self.wet_at(mx, my):
            mx, my = ex, ey
        d = self.snap(after[0] - before[0], after[1] - before[1])
        br = self.plan_bridge(mx, my, d, 'piers', spacing=14)
        if br is None:
            near = [b for b in getattr(self, 'planned', []) if math.hypot(b['mid'][0] - mx, b['mid'][1] - my) < 16]
            if not near:
                return False
            br = near[0]
        s0, s1 = br['s0'], br['s1']
        if math.hypot(before[0] - s0[0], before[1] - s0[1]) > math.hypot(before[0] - s1[0], before[1] - s1[1]):
            s0, s1 = s1, s0
        self.street([before, s0], width, level, over_water=False)
        self.street([s1, after], width, level, over_water=False)
        return True

    def quays(self, width=2):
        """Both banks of the river inside the walls are a quay street: whatever reaches the river meets it."""
        for (x, y) in list(self.river):
            for dy in range(-width, width + 1):
                for dx in range(-width, width + 1):
                    nx, ny = x + dx, y + dy
                    if self.ok(nx, ny) and self.inside[ny * self.W + nx] and self.t(nx, ny) in (G, D.TREE):
                        self.set(nx, ny, STREET)
                        self.level[(nx, ny)] = 1
                        self.dirs[(nx, ny)] = (1, 0)

    def plan_bridge(self, px, py=None, d=(0, 1), kind='piers', spacing=14, maxlen=24):
        """Lay a stone bridge, before any street: straight over the water through (px, py), bank to bank, onto
        the quays. d is its direction: straight across, or at 45 degrees as the way runs (8 directions).
        kind: 'statues' (the market bridge), 'piers' (lamps, cutwaters), 'canal' (short, a lamp at each end),
        'gate' (over the moat before a gate)."""
        planned = self.__dict__.setdefault('planned', [])
        quaywall = self.__dict__.setdefault('quaywall', set())
        px = int(round(px))
        if py is None:
            wet = [y for y in range(self.H) if (px, y) in self.river and self.wet_at(px, y)]
            if not wet:
                return None
            py = wet[len(wet) // 2]
        py = int(round(py))
        if not self.wet_at(px, py) or any(math.hypot(b['mid'][0] - px, b['mid'][1] - py) < spacing for b in planned):
            return None
        dx, dy = d
        water = lambda x, y: self.wet_at(x, y) or (x, y) in quaywall
        a = 0
        while water(px - dx * (a + 1), py - dy * (a + 1)) and a < 40:
            a += 1
        b = 0
        while water(px + dx * (b + 1), py + dy * (b + 1)) and b < 40:
            b += 1
        if a + b > maxlen or not self.across(px - dx * (a - b) / 2, py - dy * (a - b) / 2, d):
            return None
        s0 = (px - dx * (a + 1), py - dy * (a + 1))       # the landings on the quays
        s1 = (px + dx * (b + 1), py + dy * (b + 1))
        if kind == 'gate':                                # a gate bridge lands on dry ground at both ends
            if any(self.wet_at(sx + dx * sg * k, sy + dy * sg * k) for (sx, sy), sg in ((s0, -1), (s1, 1))
                   for k in range(1, 4)):
                return None
        else:                                             # room for a straight way on at both ends, inside the walls
            for (sx, sy), sg in ((s0, -1), (s1, 1)):
                for k in range(1, 6):
                    q = (sx + dx * sg * k, sy + dy * sg * k)
                    if not self.ok(*q) or not self.inside[q[1] * self.W + q[0]]:
                        return None
                    if q in self.__dict__.get('quaywall', ()):
                        if k > 1:                         # the way would run into the water again
                            return None
                    elif self.t(*q) not in (G, D.TREE, D.FIELD, D.GRAVE, STREET, LANE, D.STALL, D.WELL,
                                            D.FOUNTAIN, D.LAMP):
                        return None
        n = a + b + 2
        side = (0, 1) if dy == 0 else (1, 0)
        centres = [(s0[0] + dx * k, s0[1] + dy * k) for k in range(-1, n + 2)]
        deck = set()
        for (x, y) in centres:
            for o in (-1, 0, 1):
                deck.add((x + side[0] * o, y + side[1] * o))
        for (x, y) in deck:
            if self.ok(x, y) and (water(x, y) or self.t(x, y) in (G, D.TREE, D.FIELD, STREET, LANE)):
                self.set(x, y, STREET)
                self.level[(x, y)] = 0
                self.dirs[(x, y)] = d
                self.reserved[y * self.W + x] = 1
        parapet = self.__dict__.setdefault('parapet', set())
        for (x, y) in deck:
            for ex in (-1, 0, 1):
                for ey in (-1, 0, 1):
                    q = (x + ex, y + ey)
                    if q not in deck and self.ok(*q) and (self.t(*q) in (WATER, D.SHALLOW) or q in quaywall):
                        self.set(*q, WALLT)
                        parapet.add(q)
                        self.reserved[q[1] * self.W + q[0]] = 1
        # piers with cutwaters in the stream, statues or lamps on the parapets
        for k in range(1, n):
            x, y = s0[0] + dx * k, s0[1] + dy * k
            for sg in (-1, 1):
                par = (x + side[0] * 2 * sg, y + side[1] * 2 * sg)
                if par not in parapet or self.t(*par) != WALLT:
                    continue
                if k % 4 == 2 and kind in ('piers', 'statues') and n > 6:
                    for off, t in ((3, D.CLIFF), (4, D.BOULDER)):
                        q = (x + side[0] * off * sg, y + side[1] * off * sg)
                        if self.ok(*q) and self.t(*q) in (WATER, D.SHALLOW):
                            self.set(*q, t)
                if kind == 'statues' and k % 3 == 1:
                    self.set(*par, D.STATUE)
                elif kind == 'piers' and k % 4 == 0:
                    self.set(*par, D.LAMP)
        if kind in ('canal', 'gate'):
            for k in (1, n - 1):
                x, y = s0[0] + dx * k, s0[1] + dy * k
                for sg in (-1, 1):
                    par = (x + side[0] * 2 * sg, y + side[1] * 2 * sg)
                    if par in parapet and self.t(*par) == WALLT:
                        self.set(*par, D.LAMP)
        self.__dict__.setdefault('deck', set()).update(q for q in deck if self.ok(*q) and self.t(*q) == STREET and
                                                         any(water(q[0] + ex, q[1] + ey) or q2 in parapet
                                                             for ex in (-2, 0, 2) for ey in (-2, 0, 2)
                                                             for q2 in [(q[0] + ex, q[1] + ey)]))
        bridge = {'mid': (px, py), 'd': d, 's0': s0, 's1': s1, 'kind': kind}
        planned.append(bridge)
        return bridge

    def gate_angle(self, edge, ang, room=12, margin=10):
        """Turn a gate's place along the wall until it lies clear of the river."""
        for k in range(40):
            a = ang + (k // 2 + 1) * .05 * (1 if k % 2 else -1) if k else ang
            gx, gy = edge(a)
            if not (margin <= gx < self.W - margin and margin <= gy < self.H - margin):
                continue                            # room for the bridge and the road out before the map ends
            if not any((int(gx) + ox, int(gy) + oy) in self.river for ox in range(-room, room + 1, 2)
                       for oy in range(-room, room + 1, 2)):
                return a
        return None                                 # no good place: this way has no gate

    def quay_walls(self, cells=None):
        """A stone quay wall along every bank inside the walls: the edge of the water, drawn thin on the land side."""
        quaywall = self.__dict__.setdefault('quaywall', set())
        for (x, y) in list(cells if cells is not None else self.river):
            if not self.ok(x, y) or not self.inside[y * self.W + x] or self.t(x, y) not in (WATER, D.SHALLOW):
                continue
            if any(self.ok(x + ex, y + ey) and self.t(x + ex, y + ey) not in (WATER, D.SHALLOW, WALLT)
                   and self.inside[(y + ey) * self.W + x + ex]
                   for ex, ey in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                self.set(x, y, WALLT)
                quaywall.add((x, y))
                self.reserved[y * self.W + x] = 1

    @staticmethod
    def snap(vx, vy):
        """The way's heading over the river, snapped to one of the three ways a bridge can lie."""
        if vy < 0:
            vx, vy = -vx, -vy
        best = max(((0, 1), (1, 1), (-1, 1)), key=lambda d: (d[0] * vx + d[1] * vy) / math.hypot(*d))
        return best

    def crossings(self, pts):
        """Where a way runs over the river: the middle of each wet stretch and the way's heading there."""
        dense = self.densify(pts)
        out, i = [], 0
        wet = [(int(round(x)), int(round(y))) in self.river for x, y in dense]
        while i < len(dense):
            if not wet[i]:
                i += 1
                continue
            j = i
            while j < len(dense) and wet[j]:
                j += 1
            if 0 < i and j < len(dense):
                m = dense[(i + j) // 2]
                (ax, ay), (bx, by) = dense[max(0, i - 4)], dense[min(len(dense) - 1, j + 4)]
                out.append((m[0], m[1], self.snap(bx - ax, by - ay)))
            i = j
        return out

    @staticmethod
    def densify(pts):
        dense = []
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            n = max(1, int(math.hypot(bx - ax, by - ay)))
            dense += [(ax + (bx - ax) * k / n, ay + (by - ay) * k / n) for k in range(n)]
        dense.append(pts[-1])
        return dense

    def through_bridges(self, pts, level=0, a=8):
        """The bridges were laid first; a way that crosses the river is planned onto one: it leaves its course
        before the river, runs straight over the bridge in line with it for a good stretch (a cells each side)
        and takes up its course on the far side. A street with no bridge near gets its own; a lane never crosses:
        it ends at the quay. A crossing outside the walls is left to make its own bridge."""
        planned = self.__dict__.setdefault('planned', [])
        dense = self.densify(pts)
        wet = [(int(round(x)), int(round(y))) in self.river for x, y in dense]
        out, i, n = [], 0, len(dense)
        while i < n:
            if not wet[i]:
                out.append(dense[i])
                i += 1
                continue
            j = i
            while j < n and wet[j]:
                j += 1
            ex, ey = int(round(dense[i][0])), int(round(dense[i][1]))
            if i == 0 or j >= n or not (self.ok(ex, ey) and self.inside[ey * self.W + ex]):
                out += dense[i:j]
                i = j
                continue
            if level >= 2:
                return out                      # a lane ends at the quay
            m = dense[(i + j) // 2]
            br = min(planned, key=lambda b: math.hypot(b['mid'][0] - m[0], b['mid'][1] - m[1])) if planned else None
            if br is None or math.hypot(br['mid'][0] - m[0], br['mid'][1] - m[1]) > 18:
                (ax, ay), (bx, by) = dense[max(0, i - 6)], dense[min(n - 1, j + 6)]
                mx, my = int(round(m[0])), int(round(m[1]))
                new = None
                if self.wet_at(mx, my):
                    hx, hy = bx - ax, by - ay
                    for e in sorted(DIRS8, key=lambda e: -(e[0] * hx + e[1] * hy) / math.hypot(*e))[:3]:
                        new = self.plan_bridge(mx, my, e, 'piers', spacing=12)
                        if new:
                            break
                if new:
                    br = new
                elif br is None or math.hypot(br['mid'][0] - m[0], br['mid'][1] - m[1]) > 30:
                    out += dense[i:j]           # no way over here: it stops at the quay and goes on from the far one
                    i = j
                    continue
            (dx, dy), s0, s1 = br['d'], br['s0'], br['s1']
            mx, my = (s0[0] + s1[0]) / 2, (s0[1] + s1[1]) / 2
            reach = math.hypot(s1[0] - s0[0], s1[1] - s0[1]) / 2 + a + 2
            near = lambda q: math.hypot(q[0] - mx, q[1] - my) <= reach
            ends = [(s0[0] - dx * a, s0[1] - dy * a), (s1[0] + dx * a, s1[1] + dy * a)]
            if math.hypot(dense[i - 1][0] - ends[0][0], dense[i - 1][1] - ends[0][1]) > \
                    math.hypot(dense[i - 1][0] - ends[1][0], dense[i - 1][1] - ends[1][1]):
                ends.reverse()
            while out and near(out[-1]):
                out.pop()
            k = j
            while k < n and near(dense[k]):
                k += 1
            out += ends
            i = k
        return out

    def _pave(self, cx, cy, width, level, d, over_water):
        r = (width - 1) / 2
        for yy in range(int(cy - r - 1), int(cy + r + 2)):
            for xx in range(int(cx - r - 1), int(cx + r + 2)):
                if not self.ok(xx, yy) or math.hypot(xx - cx, yy - cy) > r + .5:
                    continue
                k = self.t(xx, yy)
                if k in (WATER, D.SHALLOW, BRIDGE):
                    if over_water == 'always' or over_water is True and level == 0:   # great ways and ring roads cross; the rest end at the quay
                        self.set(xx, yy, BRIDGE)
                        self.level[(xx, yy)] = min(level, self.level.get((xx, yy), 9))
                    continue
                if k not in (G, D.TREE, STREET, LANE, D.FIELD):
                    continue
                self.set(xx, yy, STREET if level < 2 else LANE)
                if self.level.get((xx, yy), 9) > level:
                    self.level[(xx, yy)] = level
                    self.dirs[(xx, yy)] = d

    def street_join(self, pts, width, level, skip=6, near=3, quay_ok=False):
        """Draw a street from pts[0] onwards, but stop where it meets another street: streets merge
        into each other instead of running side by side."""
        x0, y0 = pts[0]
        for k, (x, y) in enumerate(pts):
            if math.hypot(x - x0, y - y0) < skip:
                continue
            ix, iy = int(round(x)), int(round(y))
            hit = None
            for yy in range(iy - near, iy + near + 1):
                for xx in range(ix - near, ix + near + 1):
                    if self.ok(xx, yy) and self.t(xx, yy) in (STREET, LANE) and (xx, yy) in self.level:
                        d = math.hypot(xx - x, yy - y)
                        if hit is None or d < hit[0]:
                            hit = (d, xx, yy)
            if hit:
                self.street(pts[:k + 1] + [(hit[1], hit[2])], width, level)
                return True
        self.street(pts, width, level)
        return False

    def is_street(self, x, y):
        return self.ok(x, y) and self.t(x, y) in STREETS

    def grow_lanes(self, tries, mask, gap=3, maxlen=34, deadend=.04):
        """Lanes branch off the streets and wander until they meet another street: the town grew this way."""
        cells = list(self.level)
        made = 0
        for _ in range(tries):
            sx, sy = random.choice(cells)
            if not mask(sx, sy) or self.level[(sx, sy)] > 1 and random.random() < .5:
                continue
            dx, dy = self.dirs.get((sx, sy), (1, 0))
            side = random.choice((-1, 1))
            hx, hy = -dy * side, dx * side
            a = math.atan2(hy, hx) + random.gauss(0, .25)
            x, y = sx + .5 * math.cos(a), sy + .5 * math.sin(a)
            path, end, off = [], None, False
            # step off the street we start from
            for step in range(maxlen + 6):
                a += random.gauss(0, .12)
                x, y = x + math.cos(a), y + math.sin(a)
                c = (int(round(x)), int(round(y)))
                if not self.ok(*c) or not mask(*c) or self.reserved[c[1] * self.W + c[0]] and not self.is_street(*c):
                    break
                if self.is_street(*c):
                    if off:
                        end = c
                        break
                    if step > 5:
                        break
                    continue
                if c in path:
                    continue
                off = True
                path.append(c)
            if len(path) < gap + 2:
                continue
            if end is None and (random.random() > deadend or len(path) < 8):
                continue
            # too close along its middle to another street: it would only make a sliver of houses
            mid = path
            near = False
            for (cx, cy) in mid:
                for yy in range(cy - gap, cy + gap + 1):
                    for xx in range(cx - gap, cx + gap + 1):
                        if (xx, yy) not in path and self.is_street(xx, yy):
                            if math.hypot(xx - sx, yy - sy) > gap and (end is None or math.hypot(xx - end[0], yy - end[1]) > gap):
                                near = True
                                break
                    if near:
                        break
                if near:
                    break
            if near:
                continue
            self.street([(sx, sy)] + path + ([end] if end else []), 1, 2, over_water=False)
            cells = list(self.level)
            made += 1
        return made

    # ---------------------------------------------------------------- houses
    def parcels(self, depth_at, spacing_at, keep=None):
        """Houses along every street: the land is cut into plots that each face a street,
        plots share their walls, and what lies deeper than a house is yard and garden."""
        dist = [-1] * (self.W * self.H)
        q = deque()
        for (x, y) in self.level:
            if self.t(x, y) in (STREET, LANE):
                dist[y * self.W + x] = 0
                q.append((x, y))
        free = lambda x, y: self.ok(x, y) and self.inside[y * self.W + x] and not self.reserved[y * self.W + x] \
            and self.t(x, y) == G
        while q:
            x, y = q.popleft()
            d0 = dist[y * self.W + x]
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if free(nx, ny) and dist[ny * self.W + nx] < 0 and d0 < 12:
                    dist[ny * self.W + nx] = d0 + 1
                    q.append((nx, ny))
        built = [dist[i] > 0 and dist[i] <= depth_at(i % self.W, i // self.W) + 1 for i in range(self.W * self.H)]
        # seeds: one per house, along the street front
        front = [(i % self.W, i // self.W) for i in range(self.W * self.H) if dist[i] == 1]
        random.shuffle(front)
        seeds = []
        taken = set()
        for (x, y) in front:
            sp = spacing_at(x, y)
            if (x, y) in taken:
                continue
            seeds.append((x, y))
            for dx in range(-sp + 1, sp):
                for dy in range(-sp + 1, sp):
                    taken.add((x + dx, y + dy))
        lab = [-1] * (self.W * self.H)
        q = deque()
        for k, (x, y) in enumerate(seeds):
            lab[y * self.W + x] = k
            q.append((x, y))
        while q:
            x, y = q.popleft()
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                i = ny * self.W + nx
                if self.ok(nx, ny) and built[i] and lab[i] < 0:
                    lab[i] = lab[y * self.W + x]
                    q.append((nx, ny))
        # tiny plots join a neighbour
        size = {}
        for i, l in enumerate(lab):
            if l >= 0:
                size[l] = size.get(l, 0) + 1
        for i, l in enumerate(lab):
            if l >= 0 and size[l] < 10:
                x, y = i % self.W, i // self.W
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    j = ny * self.W + nx
                    if 0 <= nx < self.W and 0 <= ny < self.H and lab[j] >= 0 and lab[j] != l and size[lab[j]] >= 10:
                        lab[i] = lab[j]
                        break
        # plots with no room inside are left as yard
        for _ in range(2):
            cnt = {}
            for i, l in enumerate(lab):
                if l < 0:
                    continue
                x, y = i % self.W, i // self.W
                if all(0 <= x + dx < self.W and 0 <= y + dy < self.H and lab[(y + dy) * self.W + x + dx] == l
                       for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                    cnt[l] = cnt.get(l, 0) + 1
            for i, l in enumerate(lab):
                if l >= 0 and cnt.get(l, 0) < 3:
                    lab[i] = -1
        houses = {}
        for i, l in enumerate(lab):
            if l < 0:
                continue
            x, y = i % self.W, i // self.W
            wall = False
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    nx, ny = x + dx, y + dy
                    if not self.ok(nx, ny):
                        wall = True
                        continue
                    o = lab[ny * self.W + nx]
                    if o < 0 or o < l:          # shared walls: the higher number builds them
                        wall = True
            self.set(x, y, WALLT if wall else PLANK)
            houses.setdefault(l, []).append((x, y))
        # a door to the street, and a few things inside
        for l, cells in houses.items():
            floor = [c for c in cells if self.t(*c) == PLANK]
            if len(floor) < 2:
                for c in cells:
                    if self.t(*c) == PLANK:
                        self.set(*c, WALLT)
                continue
            fs = set(floor)
            doors = []
            for (x, y) in cells:
                if self.t(x, y) != WALLT:
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    if self.is_street(x + dx, y + dy) and (x - dx, y - dy) in fs:
                        doors.append((x, y))
            if doors:
                self.set(*random.choice(doors), DOOR)
            if len(floor) >= 8:
                inner = [c for c in floor if all(self.t(c[0] + dx, c[1] + dy) != DOOR for dx in (-1, 0, 1) for dy in (-1, 0, 1))]
                random.shuffle(inner)
                for k in (D.BED, D.TABLE)[:len(inner) // 4]:
                    self.set(*inner.pop(), k)
        # yards behind the houses
        for i in range(self.W * self.H):
            x, y = i % self.W, i // self.W
            if self.inside[i] and not self.reserved[i] and self.t(x, y) == G:
                r = random.random()
                if r < .07:
                    self.set(x, y, D.TREE)
                elif r < .075:
                    self.set(x, y, D.WELL)
        return houses

    def rows(self, size_at, passes=3):
        """Houses as rooms in a row: each stands with its front on a street, its door in the front,
        and shares its side walls with its neighbours. Gaps that are left become yards and alleys."""
        hw = self.housewall = getattr(self, 'housewall', set())
        def free(x, y):
            return self.ok(x, y) and self.inside[y * self.W + x] and not self.reserved[y * self.W + x] and self.t(x, y) in (G, D.TREE)
        front = []
        for y in range(self.H):
            for x in range(self.W):
                if not free(x, y):
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    if self.ok(x + dx, y + dy) and self.t(x + dx, y + dy) in (STREET, LANE):
                        front.append((x, y, -dx, -dy))
        made = 0
        for p in range(passes):
            random.shuffle(front)
            for (x, y, ax, ay) in front:
                if not free(x, y):
                    continue
                wa0, dp0 = size_at(x, y, p)
                tries = [(wa, off, dp) for wa in range(wa0, 3, -1) for dp in range(dp0, 3, -1)
                         for off in random.sample(range(1, wa - 1), wa - 2) + [0, wa - 1]][:80]
                for wa, off, dp in tries:
                    if ax == 0:
                        x0, x1 = x - off, x - off + wa - 1
                        y0, y1 = (y, y + dp - 1) if ay > 0 else (y - dp + 1, y)
                    else:
                        y0, y1 = y - off, y - off + wa - 1
                        x0, x1 = (x, x + dp - 1) if ax > 0 else (x - dp + 1, x)
                    # slide sideways onto a neighbour's wall, so the two share it
                    if ax == 0:
                        if (x0 - 1, y) in hw:
                            x0 -= 1
                        if (x1 + 1, y) in hw:
                            x1 += 1
                    else:
                        if (x, y0 - 1) in hw:
                            y0 -= 1
                        if (x, y1 + 1) in hw:
                            y1 += 1
                    good = True
                    for yy in range(y0, y1 + 1):
                        for xx in range(x0, x1 + 1):
                            edge = yy in (y0, y1) or xx in (x0, x1)
                            if not (free(xx, yy) or edge and (xx, yy) in hw):
                                good = False
                                break
                        if not good:
                            break
                    if not good:
                        continue
                    for yy in range(y0, y1 + 1):
                        for xx in range(x0, x1 + 1):
                            if yy in (y0, y1) or xx in (x0, x1):
                                self.set(xx, yy, WALLT)
                                hw.add((xx, yy))
                            else:
                                self.set(xx, yy, PLANK)
                    # the door: in the front, with the street before it
                    if ax == 0:
                        fr = [(xx, y) for xx in range(x0 + 1, x1) if self.is_street(xx, y - ay)]
                    else:
                        fr = [(x, yy) for yy in range(y0 + 1, y1) if self.is_street(x - ax, yy)]
                    if not fr:                  # on a slanting street: a step from the door to the street
                        if ax == 0:
                            cand = [(xx, y) for xx in range(x0 + 1, x1)]
                        else:
                            cand = [(x, yy) for yy in range(y0 + 1, y1)]
                        cand.sort(key=lambda q: abs(q[0] - x) + abs(q[1] - y))
                        q = cand[0]
                        st = (q[0] - ax, q[1] - ay)
                        if self.ok(*st) and self.t(*st) in (G, D.TREE):
                            self.set(*st, STREET)
                            fr = [q]
                    door = random.choice(fr) if fr else None
                    if door:
                        self.set(*door, DOOR)
                    self.houses.append([x0, y0, x1, y1, door])
                    inner = [(xx, yy) for yy in range(y0 + 2, y1 - 1) for xx in range(x0 + 2, x1 - 1)]
                    random.shuffle(inner)
                    for k in (D.BED, D.TABLE, D.HEARTH if random.random() < .3 else D.BED)[:len(inner) // 2]:
                        self.set(*inner.pop(), k)
                    made += 1
                    break
        # yards and gardens behind
        for i in range(self.W * self.H):
            x, y = i % self.W, i // self.W
            if self.inside[i] and not self.reserved[i] and self.t(x, y) == G:
                r = random.random()
                if r < .06:
                    self.set(x, y, D.TREE)
                elif r < .064:
                    self.set(x, y, D.WELL)
        return made

    # ---------------------------------------------------------------- walls
    def city_wall(self, inside_fn, tower_every=13, gates=(), moat=False, open_to=None, moat_w=4):
        for y in range(self.H):
            for x in range(self.W):
                self.inside[y * self.W + x] = 1 if inside_fn(x, y) else 0
        ring = []
        for y in range(self.H):
            for x in range(self.W):
                if self.inside[y * self.W + x] and any(not self.ok(x + dx, y + dy) or not self.inside[(y + dy) * self.W + x + dx]
                                                  for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                    if open_to and open_to(x, y):
                        continue
                    ring.append((x, y))
        for (x, y) in ring:
            self.set(x, y, WALLT)
            self.reserved[y * self.W + x] = 1
            if moat:                        # a broad moat, wide enough for a whole stone bridge at each gate
                for dx in range(-moat_w, moat_w + 1):
                    for dy in range(-moat_w, moat_w + 1):
                        nx, ny = x + dx, y + dy
                        if self.ok(nx, ny) and not self.inside[ny * self.W + nx] and self.t(nx, ny) in (G, D.TREE) \
                                and abs(dx) + abs(dy) <= moat_w + 1:
                            self.set(nx, ny, WATER)
                            self.moat.add((nx, ny))
        # towers
        random.shuffle(ring)
        towers = []
        for (x, y) in ring:
            if all(math.hypot(x - a, y - b) >= tower_every for a, b in towers):
                towers.append((x, y))
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        if self.ok(x + dx, y + dy) and self.t(x + dx, y + dy) != STREET:
                            self.set(x + dx, y + dy, WALLT)
                            self.reserved[(y + dy) * self.W + x + dx] = 1
        return ring

    def gate(self, pts, width=3):
        """Cut a gate where a road goes through the wall, with a tower on each side."""
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            n = max(1, int(math.hypot(bx - ax, by - ay) * 2))
            for i in range(n + 1):
                x, y = int(round(ax + (bx - ax) * i / n)), int(round(ay + (by - ay) * i / n))
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        if self.ok(x + dx, y + dy) and self.t(x + dx, y + dy) == WALLT and self.inside[(y + dy) * self.W + x + dx]:
                            self.set(x + dx, y + dy, STREET)


# ---------------------------------------------------------------- shapes
def canal_river(c, y0, y1, half, x0=-4, x1=None):
    """A river as the town has tamed it, like the Amstel: long straight reaches joined by turns of 45 degrees,
    one width all the way, so quay walls can run along both banks."""
    x1 = (c.m.w + 4) if x1 is None else x1
    x, y = x0, y0
    pts = [(x, y)]
    last, bend = 0, random.choice((1, -1))
    while x < x1:
        target = y0 + (y1 - y0) * (x - x0) / (x1 - x0)
        if last != 0:
            dy = 0                                  # after a turn always a straight reach
        elif abs(y - target) > 3:
            dy = 1 if target > y else -1
        else:
            bend = -bend                            # the river swings one way, then back the other
            dy = bend if random.random() < .6 else 0
        n = random.randint(14, 26) if dy == 0 else random.randint(3, 6)
        last = dy
        for _ in range(n):
            x, y = x + 1, y + dy
            pts.append((x, y))
    for (px, py) in pts:
        for oy in range(-half, half + 1):
            for ox in (-1, 0, 1):
                q = (px + ox, py + oy)
                if c.ok(*q):
                    c.set(*q, WATER)
                    c.river.add(q)
                    c.reserved[q[1] * c.m.w + q[0]] = 1
    return pts


def wobbly(a, b, wob, seg=7):
    ax, ay = a
    bx, by = b
    L = math.hypot(bx - ax, by - ay)
    n = max(2, int(L / seg))
    px, py = -(by - ay) / (L or 1), (bx - ax) / (L or 1)
    pts, off, v = [a], 0, 0
    for i in range(1, n):
        v = v * .6 + random.uniform(-wob, wob)
        off = off * .85 + v
        t = i / n
        pts.append((ax + (bx - ax) * t + px * off, ay + (by - ay) * t + py * off))
    pts.append(b)
    for _ in range(2):                          # Chaikin: round the corners
        new = [pts[0]]
        for p, q in zip(pts, pts[1:]):
            new += [(.75 * p[0] + .25 * q[0], .75 * p[1] + .25 * q[1]), (.25 * p[0] + .75 * q[0], .25 * p[1] + .75 * q[1])]
        new.append(pts[-1])
        pts = new
    return pts


def blob(cx, cy, rx, ry, rough=.12, k=None):
    k = k or [random.uniform(0, 6.3) for _ in range(4)]
    def r(a):
        return 1 + rough * (math.sin(2 * a + k[0]) * .6 + math.sin(3 * a + k[1]) * .5 + math.sin(5 * a + k[2]) * .3
                            + math.sin(7 * a + k[3]) * .15)
    def inside(x, y, scale=1.0):
        dx, dy = (x - cx) / rx, (y - cy) / ry
        return math.hypot(dx, dy) < r(math.atan2(dy, dx)) * scale
    def edge(a, scale=1.0):
        rr = r(a) * scale
        return cx + math.cos(a) * rx * rr, cy + math.sin(a) * ry * rr
    return inside, edge


def rect(c, x0, y0, w, h, wall=WALLT, floor=FLOOR, reserve=True):
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            edge = y in (y0, y0 + h - 1) or x in (x0, x0 + w - 1)
            c.set(x, y, wall if edge else floor)
            if reserve:
                c.reserved[y * c.W + x] = 1


def reserve(c, x0, y0, w, h):
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            if c.ok(x, y):
                c.reserved[y * c.W + x] = 1


def cathedral(c, x, y):
    """A cross-shaped church facing west: two towers, nave with pews, transept, apse with the altar."""
    nl, nw = 30, 9
    rect(c, x, y, nl, nw)                                   # nave
    rect(c, x + 17, y - 5, 8, nw + 10)                      # transept
    for yy in range(y + 1, y + nw - 1):                     # open the crossing
        for xx in range(x + 17, x + 25):
            c.set(xx, yy, FLOOR)
    for yy in range(y - 4, y + nw + 4):
        for xx in range(x + 18, x + 24):
            c.set(xx, yy, FLOOR)
    for dy in range(-6, 7):                                 # apse
        for dx in range(0, 7):
            d = math.hypot(dx, dy * 1.1)
            xx, yy = x + nl - 1 + dx, y + nw // 2 + dy
            if d < 5.6:
                c.set(xx, yy, FLOOR if d < 4.6 else WALLT)
                c.reserved[yy * c.W + xx] = 1
    for xx in range(x + nl - 2, x + nl + 1):
        for yy in range(y + 1, y + nw - 1):
            c.set(xx, yy, FLOOR)
    rect(c, x - 3, y - 2, 6, 5)                             # west towers
    rect(c, x - 3, y + nw - 3, 6, 5)
    c.set(x + nl + 2, y + nw // 2, D.ALTAR)
    for xx in range(x + 3, x + 16, 2):                      # pews
        for yy in (y + 2, y + 3, y + nw - 4, y + nw - 3):
            c.set(xx, yy, D.BENCH)
    c.set(x, y + nw // 2, DOOR)
    c.set(x + 21, y - 5, DOOR)
    c.set(x + 21, y + nw + 4, DOOR)
    reserve(c, x - 4, y - 6, nl + 12, nw + 12)
    church_square(c, x - 6, y - 8, nl + 16, nw + 16)
    c.great.append(('temple', (x - 3, y - 5, nl + 10, nw + 10), (x, y + nw // 2)))


def church_square(c, x0, y0, w, h):
    """A paved square round a church, not a patch of grass: the church stands free on it."""
    for yy in range(y0, y0 + h):
        for xx in range(x0, x0 + w):
            if c.ok(xx, yy) and c.t(xx, yy) in (G, D.TREE, D.GRAVE) and c.inside[yy * c.m.w + xx]:
                c.set(xx, yy, STREET)
                c.level[(xx, yy)] = 1
                c.dirs[(xx, yy)] = (1, 0)
                c.reserved[yy * c.m.w + xx] = 1


def castle(c, cx, cy):
    """A burgh on its own rise: curtain wall with corner towers, a keep, a hall, a yard."""
    x0, y0, w, h = cx - 17, cy - 11, 34, 22
    reserve(c, x0 - 2, y0 - 2, w + 4, h + 4)
    for y in range(y0 - 2, y0 + h + 2):                     # its own moat
        for x in range(x0 - 2, x0 + w + 2):
            if not (x0 <= x < x0 + w and y0 <= y < y0 + h):
                c.set(x, y, WATER)
    rect(c, x0, y0, w, h, floor=D.GRASS)
    for (tx, ty) in ((x0, y0), (x0 + w - 5, y0), (x0, y0 + h - 5), (x0 + w - 5, y0 + h - 5)):
        rect(c, tx - 1, ty - 1, 7, 7)
    rect(c, x0 + 4, y0 + 4, 12, 13)                         # the keep
    c.set(x0 + 10, y0 + 16, DOOR)
    c.great.append(('keep', (x0 + 4, y0 + 4, 12, 13), (x0 + 10, y0 + 16)))
    c.set(x0 + 10, y0 + 6, D.HIGHSEAT)
    rect(c, x0 + 19, y0 + 4, 11, 7)                         # hall
    c.set(x0 + 24, y0 + 10, DOOR)
    for xx in range(x0 + 21, x0 + 28, 2):
        c.set(xx, y0 + 7, D.TABLE)
    rect(c, x0 + 19, y0 + 13, 11, 5)                        # stables, smithy
    c.set(x0 + 24, y0 + 13, DOOR)
    c.set(x0 + 21, y0 + 15, D.ANVIL)
    for x in range(x0 + 15, x0 + 19):
        for y in range(y0 + 1, y0 + h - 1):
            c.set(x, y, LANE)
    gx = cx
    for y in range(y0 + h - 1, y0 + h + 2):                 # gate and drawbridge
        for x in (gx - 1, gx, gx + 1):
            c.set(x, y, BRIDGE if y >= y0 + h else STREET)
    for x in range(x0 + 1, x0 + w - 1):
        if c.t(x, y0 + h - 2) == D.GRASS and abs(x - gx) < 2:
            c.set(x, y0 + h - 2, LANE)
    for y in range(y0 + h - 4, y0 + h - 1):
        c.set(gx, y, LANE)
    return (gx, y0 + h + 2)


def palace(c, cx, cy):
    """An emperor's walled city within the city: a red wall and moat, then court behind court on one
    axis, each hall bigger than the last, the throne hall at the heart, a garden at the back."""
    x0, y0, w, h = cx - 22, cy - 22, 44, 46
    reserve(c, x0 - 3, y0 - 3, w + 6, h + 6)
    for y in range(y0 - 3, y0 + h + 3):
        for x in range(x0 - 3, x0 + w + 3):
            if not (x0 - 1 <= x < x0 + w + 1 and y0 - 1 <= y < y0 + h + 1):
                c.set(x, y, WATER)
            elif not (x0 <= x < x0 + w and y0 <= y < y0 + h):
                c.set(x, y, LANE)
    rect(c, x0, y0, w, h, floor=STREET)
    for (tx, ty) in ((x0, y0), (x0 + w - 3, y0), (x0, y0 + h - 3), (x0 + w - 3, y0 + h - 3)):
        rect(c, tx, ty, 3, 3)
    # cross walls make the courts
    for yy in (y0 + 13, y0 + 30):
        for x in range(x0, x0 + w):
            c.set(x, yy, WALLT)
        for x in (cx - 1, cx, cx + 1):
            c.set(x, yy, STREET)
    # halls on the axis
    rect(c, cx - 7, y0 + 4, 15, 6)
    c.set(cx, y0 + 9, DOOR)
    rect(c, cx - 10, y0 + 17, 21, 9)                        # the throne hall
    c.set(cx, y0 + 25, DOOR)
    c.great.append(('keep', (cx - 10, y0 + 17, 21, 9), (cx, y0 + 25)))
    c.set(cx, y0 + 19, D.HIGHSEAT)
    for yy in range(y0 + 20, y0 + 25, 2):
        c.set(cx - 5, yy, D.STATUE)
        c.set(cx + 5, yy, D.STATUE)
    rect(c, cx - 6, y0 + 33, 13, 5)
    c.set(cx, y0 + 37, DOOR)
    for side in (-1, 1):                                    # side courts with smaller halls
        for k, yy in enumerate((y0 + 2, y0 + 16)):
            rect(c, cx + side * 16 - 4, yy + 1, 8, 9 if k == 0 else 11)
            c.set(cx + side * 16 - side * 4 + (side < 0) * 7 - (side > 0) * 0 if False else cx + side * 12, yy + 4, DOOR)
    for yy in range(y0 + 39, y0 + h - 1):                   # the garden
        for x in range(x0 + 1, x0 + w - 1):
            c.set(x, yy, D.GRASS if random.random() > .25 else D.TREE)
    for x in range(cx - 3, cx + 4):
        c.set(x, y0 + 41, WATER)
        c.set(x, y0 + 42, WATER)
    for x in (cx - 1, cx, cx + 1):                          # the gate to the south
        c.set(x, y0 + h - 1, STREET)
        for y in range(y0 + h, y0 + h + 3):
            c.set(x, y, BRIDGE if c.t(x, y) == WATER else STREET)
    # the axis
    for y in range(y0 + 1, y0 + h - 1):
        if c.t(cx, y) == STREET:
            pass
    return (cx, y0 + h + 3)


def stone_bridges(c, first=('piers',), small=False):
    """Dress every crossing as a real bridge. Old towns built few bridges and made much of them:
    a deck of stone with parapets, piers with cutwaters in the stream, and then by kind:
    'houses'  shops and houses on both sides of the deck, as on the Ponte Vecchio or old London Bridge;
    'statues' statues of saints and kings along the parapets and a gate tower at each end, as on the Charles Bridge;
    'piers'   a plain bridge on broad piers with lamps on the parapets.
    Canal bridges (small): a short arched bridge with a parapet each side and a lamp at each end."""
    seen = set()
    comps = []
    for y in range(c.H):
        for x in range(c.W):
            if c.t(x, y) == BRIDGE and (x, y) not in seen:
                comp, q = [], [(x, y)]
                seen.add((x, y))
                while q:
                    a, b = q.pop()
                    comp.append((a, b))
                    for nx, ny in ((a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1)):
                        if c.ok(nx, ny) and (nx, ny) not in seen and c.t(nx, ny) == BRIDGE:
                            seen.add((nx, ny))
                            q.append((nx, ny))
                comps.append(comp)
    comps.sort(key=lambda k: -len(k))
    if getattr(c, 'market', None):           # the market's own bridge is the one with the shops
        mx_, my_ = c.market
        comps.sort(key=lambda k: math.hypot(sum(p[0] for p in k) / len(k) - mx_, sum(p[1] for p in k) / len(k) - my_))
    kinds = list(first)
    out = []
    wet = (WATER, D.SHALLOW)
    for comp in comps:
        if any(p in c.piers for p in comp):
            continue
        if not small and not any((x + dx, y + dy) in c.river for x, y in comp for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
            continue                         # a drawbridge or a moat crossing stays as it is
        if small:                            # a canal bridge: a stone deck, a parapet on each side, lamps
            cs = set(comp)
            for (x, y) in comp:
                c.set(x, y, STREET)
                c.level[(x, y)] = 0
            for (x, y) in comp:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if c.ok(nx, ny) and c.t(nx, ny) in (WATER, D.SHALLOW) and (nx, ny) not in c.river:
                        land = [(nx + ex, ny + ey) for ex, ey in ((1, 0), (-1, 0), (0, 1), (0, -1))
                                if c.ok(nx + ex, ny + ey) and c.t(nx + ex, ny + ey) not in (WATER, D.SHALLOW, STREET, WALLT)]
                        c.set(nx, ny, D.LAMP if land else WALLT)
                        c.reserved[ny * c.W + nx] = 1
            out.append(('small', comp[0]))
            continue
        xs, ys = [p[0] for p in comp], [p[1] for p in comp]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        # the span runs the short way over the water, whatever the street did
        mx, my = sum(xs) // len(xs), sum(ys) // len(ys)
        def run(dx, dy):
            k = 1
            while c.ok(mx + dx * k, my + dy * k) and c.t(mx + dx * k, my + dy * k) in (WATER, D.SHALLOW, BRIDGE) and k < 60:
                k += 1
            return k
        vertical = run(0, 1) + run(0, -1) <= run(1, 0) + run(-1, 0)
        # work in (along, across): along runs over the water
        if vertical:
            mid = sum(xs) // len(xs)
            a0, a1 = y0, y1
            cell = lambda al, ac: (mid + ac, al)
        else:
            mid = sum(ys) // len(ys)
            a0, a1 = x0, x1
            cell = lambda al, ac: (al, mid + ac)
        # the span runs from bank to bank
        while c.ok(*cell(a0 - 1, 0)) and c.t(*cell(a0 - 1, 0)) in wet + (BRIDGE,):
            a0 -= 1
        while c.ok(*cell(a1 + 1, 0)) and c.t(*cell(a1 + 1, 0)) in wet + (BRIDGE,):
            a1 += 1
        if a1 - a0 > 24:                     # not a crossing after all
            continue
        cx_, cy_ = cell((a0 + a1) // 2, 0)
        if small or len(comp) < 6:
            kind = 'small'
        elif not c.inside[cy_ * c.W + cx_]:
            kind = 'piers'                   # out in the fields: a plain bridge
        else:
            kind = kinds.pop(0) if kinds else 'piers'
        half = 1 if kind in ('small', 'piers', 'statues') else 1
        for p in comp:                       # the old planks go
            c.set(*p, WATER)
        span = range(a0, a1 + 1)
        def put(al, ac, t):
            x, y = cell(al, ac)
            if c.ok(x, y):
                c.set(x, y, t)
                c.reserved[y * c.W + x] = 1
        for al in span:
            for ac in range(-half, half + 1):
                put(al, ac, STREET)
                c.level[cell(al, ac)] = 0
            put(al, -half - 1, WALLT)
            put(al, half + 1, WALLT)
        n = len(span)
        if kind == 'small':
            for al in (a0, a1):
                for ac in (-half - 1, half + 1):
                    put(al, ac, D.LAMP)
        if kind in ('piers', 'statues', 'houses'):
            # piers with pointed cutwaters, every fourth step of the span
            for k, al in enumerate(span):
                if 1 <= k < n - 1 and k % 4 == 2:
                    for ac in (-half - 2, half + 2):
                        x, y = cell(al, ac)
                        if c.ok(x, y) and c.t(x, y) in wet:
                            put(al, ac, D.CLIFF)
                    for ac in (-half - 3, half + 3):
                        x, y = cell(al, ac)
                        if c.ok(x, y) and c.t(x, y) in wet:
                            put(al, ac, D.BOULDER)
        if kind == 'piers':
            for k, al in enumerate(span):
                if k % 4 == 0 and 0 < k < n - 1:
                    put(al, -half - 1, D.LAMP)
                    put(al, half + 1, D.LAMP)
        if kind == 'statues':
            for k, al in enumerate(span):
                if k % 3 == 1:
                    put(al, -half - 1, D.STATUE)
                    put(al, half + 1, D.STATUE)
            for al, step in ((a0 - 1, -1), (a1 + 1, 1)):      # a gate tower over each end of the bridge
                for d in range(0, 4):
                    for ac in range(-half - 2, half + 3):
                        edge = d in (0, 3) or abs(ac) == half + 2
                        if abs(ac) <= half:
                            put(al + step * d, ac, STREET)
                            c.level[cell(al + step * d, ac)] = 0
                        else:
                            put(al + step * d, ac, WALLT)
                        # it stands on the quay: the street through it stays open
        if kind == 'houses':
            # shops on both sides of the deck, their fronts on it, their backs over the water
            for side in (-1, 1):
                k = 0
                while k < n - 1:
                    ln = min(4, n - k)
                    if ln < 3:
                        break
                    for i in range(ln):
                        for d in range(1, 5):
                            al = a0 + k + i
                            edge = i in (0, ln - 1) or d in (1, 4)
                            put(al, side * (half + d), WALLT if edge else PLANK)
                    put(a0 + k + ln // 2, side * (half + 1), DOOR)
                    put(a0 + k + 1, side * (half + 2), D.STALL)
                    k += ln - 1
            for al in (a0, a1):
                put(al, -half - 1, D.LAMP)
                put(al, half + 1, D.LAMP)
        # the landing: the deck meets the quay
        for al, step in ((a0 - 1, -1), (a1 + 1, 1)):
            for ac in range(-half, half + 1):
                x, y = cell(al, ac)
                if c.ok(x, y) and c.t(x, y) in (G, D.TREE) + wet:
                    put(al, ac, STREET)
                    c.level[(x, y)] = 0
        out.append((kind, cell((a0 + a1) // 2, 0)))
    return out


def connect(c, start):
    """Every street must lead somewhere: flood from the market; a piece that does not reach it gets a lane along
    the shortest way over open ground to the nearest street that does. A piece walled in (a castle's yard with
    no way out) is noted, not forced."""
    from collections import deque
    walk = (STREET, LANE, BRIDGE)
    open_ground = (G, D.TREE, D.FIELD)
    c.enclosed = set()
    joined = 0

    def flood(src):
        seen = set(src)
        q = list(src)
        while q:
            x, y = q.pop()
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if (nx, ny) not in seen and c.ok(nx, ny) and c.t(nx, ny) in walk:
                    seen.add((nx, ny))
                    q.append((nx, ny))
        return seen
    for _ in range(400):
        reached = flood([start])
        lost = [(x, y) for y in range(c.H) for x in range(c.W) if c.t(x, y) in walk and (x, y) not in reached
                and c.inside[y * c.W + x] and (x, y) not in c.enclosed]
        if not lost:
            break
        piece = flood([lost[0]])
        if len(piece) < 3:
            for p in piece:
                c.set(*p, G)
            continue
        # the shortest way over open ground from the piece to the reached streets
        prev = {p: None for p in piece}
        dq = deque(piece)
        hit = None
        while dq and hit is None:
            x, y = dq.popleft()
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                q = (nx, ny)
                if q in prev or not c.ok(nx, ny):
                    continue
                if q in reached:
                    prev[q] = (x, y)
                    hit = q
                    break
                if c.t(nx, ny) in open_ground and not c.reserved[ny * c.W + nx] or c.t(nx, ny) in walk:
                    prev[q] = (x, y)
                    dq.append(q)
        if hit is None:
            c.enclosed |= piece
            continue
        p = prev[hit]
        while p is not None and p not in piece:
            if c.t(*p) in open_ground:
                c.set(*p, LANE)
                c.level[p] = 2
                c.dirs[p] = (1, 0)
            p = prev[p]
        joined += 1
    return joined


def straight_approaches(c, a=8):
    """Every bridge has a straight run of street in line with it at both ends, a cells long, so the way and the
    bridge never meet at an odd angle."""
    for b in getattr(c, 'planned', []):
        (dx, dy), s0, s1 = b['d'], b['s0'], b['s1']
        side = (0, 1) if dy == 0 else (1, 0)
        for (sx, sy), sg in ((s0, -1), (s1, 1)):
            for k in range(0, a + 1):
                x, y = sx + dx * sg * k, sy + dy * sg * k
                if not c.ok(x, y) or c.t(x, y) not in (G, D.TREE, D.FIELD, STREET, LANE, D.GRAVE):
                    break
                for o in (-1, 0, 1):
                    q = (x + side[0] * o, y + side[1] * o)
                    if c.ok(*q) and c.t(*q) in (G, D.TREE, D.FIELD, LANE, D.GRAVE):
                        c.set(*q, STREET)
                        c.level[q] = min(c.level.get(q, 9), 1)
                        c.dirs[q] = (dx, dy)


DIRS8 = ((0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1))


def drawbridges(c, gates):
    """Every gate has a stone bridge over the broad moat, laid like the other bridges: straight or at 45 degrees,
    in line with the road that leaves the gate, from the gateway to the far bank, where the road takes it up;
    a tower stands on the wall at each side of the gateway."""
    c.gates = list(gates)
    for (gx, gy) in gates:
        gx, gy = int(round(gx)), int(round(gy))
        out = [(x, y) for y in range(gy - 24, gy + 25) for x in range(gx - 24, gx + 25)
               if c.ok(x, y) and not c.inside[y * c.W + x] and c.t(x, y) == STREET and c.level.get((x, y), 9) <= 1
               and 7 < math.hypot(x - gx, y - gy) < 24]
        if out:
            vx = sum(x for x, _ in out) / len(out) - gx
            vy = sum(y for _, y in out) / len(out) - gy
        else:                                      # the land runs out soon: the road goes straight out from the town
            ins = [(x, y) for y in range(0, c.H, 4) for x in range(0, c.W, 4) if c.inside[y * c.W + x]]
            vx = gx - sum(x for x, _ in ins) / len(ins)
            vy = gy - sum(y for _, y in ins) / len(ins)
        for y in range(gy - 10, gy + 11):          # old planks, if any, go back to water
            for x in range(gx - 10, gx + 11):
                if c.ok(x, y) and c.t(x, y) == BRIDGE and not c.inside[y * c.W + x]:
                    c.set(x, y, WATER)
        br = None                                  # the heading nearest the road's that crosses the moat
        for d in sorted(DIRS8, key=lambda e: -(e[0] * vx + e[1] * vy) / math.hypot(*e))[:3]:
            x, y, k = gx, gy, 0                    # from the gateway outwards, through the wall, to the moat
            while k < 8 and c.ok(x, y) and not c.wet_at(x, y):
                x, y, k = x + d[0], y + d[1], k + 1
            if not c.wet_at(x, y):
                continue
            span = []
            while c.ok(x, y) and c.wet_at(x, y) and len(span) < 14:
                span.append((x, y))
                x, y = x + d[0], y + d[1]
            mx, my = span[len(span) // 2]
            br = c.plan_bridge(mx, my, d, 'gate', spacing=0)
            if br:
                break
        if br is None:                             # no room for one: the gate stays a way through the wall
            continue
        side = (0, 1) if d[1] == 0 else (1, 0)
        s0, s1 = br['s0'], br['s1']
        if math.hypot(s0[0] - gx, s0[1] - gy) > math.hypot(s1[0] - gx, s1[1] - gy):
            s0, s1 = s1, s0
        # the gateway, in line with its bridge
        n = max(abs(s0[0] - gx), abs(s0[1] - gy))
        for i in range(-9, n + 1):              # the street runs in line with the bridge well into the town
            px, py = gx + d[0] * i, gy + d[1] * i
            for o in (-1, 0, 1):
                q = (px + side[0] * o, py + side[1] * o)
                ok = (WALLT, D.WALL, G, D.TREE, LANE) if i >= -5 else (G, D.TREE, LANE)
                if c.ok(*q) and (c.inside[q[1] * c.W + q[0]] or i >= 0) and c.t(*q) in ok \
                        and q not in getattr(c, 'parapet', ()):
                    c.set(*q, STREET)
                    c.level[q] = 0
        # a tower on the wall each side of the gateway
        wx, wy = gx + d[0] * (n - 1), gy + d[1] * (n - 1)
        perp = (-d[1], d[0])
        wall = [(x2, y2) for y2 in range(wy - 6, wy + 7) for x2 in range(wx - 6, wx + 7)
                if c.ok(x2, y2) and c.t(x2, y2) == WALLT and c.inside[y2 * c.W + x2] and (x2, y2) not in getattr(c, 'parapet', ())]
        for sg in (-1, 1):
            side_w = [q for q in wall if ((q[0] - wx) * perp[0] + (q[1] - wy) * perp[1]) * sg > 2]
            if not side_w:
                continue
            tx, ty = min(side_w, key=lambda q: abs(math.hypot(q[0] - wx, q[1] - wy) - 3.5))
            for ex in (-1, 0, 1):
                for ey in (-1, 0, 1):
                    q = (tx + ex, ty + ey)
                    if c.ok(*q) and c.inside[q[1] * c.W + q[0]] and c.t(*q) in (WALLT, G, D.TREE):
                        c.set(*q, WALLT)
                        c.reserved[q[1] * c.W + q[0]] = 1
        # the road outside takes it up on the far bank: first the bridge and a straight stretch in line with it,
        # then the old road is joined to the end of that stretch; the old road's first bend is taken away
        a = 12
        if out:
            tgt = min(out, key=lambda q: math.hypot(q[0] - s1[0] - d[0] * (a + 2), q[1] - s1[1] - d[1] * (a + 2)))
            reach = math.hypot(tgt[0] - s1[0], tgt[1] - s1[1]) - 1
            deck = getattr(c, 'deck', set())
            for (x, y) in [(x, y) for y in range(gy - 24, gy + 25) for x in range(gx - 24, gx + 25)
                           if c.ok(x, y) and not c.inside[y * c.W + x] and c.t(x, y) == STREET and (x, y) not in deck
                           and math.hypot(x - s1[0], y - s1[1]) < reach and not c.wet_at(x, y)]:
                c.set(x, y, G)
        for k in range(0, a if out else 99):     # in line with the bridge out into the land
            for o in (-1, 0, 1):
                q = (s1[0] + d[0] * k + side[0] * o, s1[1] + d[1] * k + side[1] * o)
                if c.ok(*q) and c.t(*q) in (G, D.TREE, D.FIELD):
                    c.set(*q, STREET)
        if not out:
            continue
        for o in (-1, 0, 1):
            sx, sy = s1[0] + d[0] * (a - 1) + side[0] * o, s1[1] + d[1] * (a - 1) + side[1] * o
            m = max(abs(tgt[0] - sx), abs(tgt[1] - sy), 1)
            for i in range(m + 1):
                q = (int(round(sx + (tgt[0] - sx) * i / m)), int(round(sy + (tgt[1] - sy) * i / m)))
                if c.ok(*q) and c.t(*q) in (G, D.TREE, D.FIELD):
                    c.set(*q, STREET)


def fill_slivers(c, gap=3, dry=False):
    """Two streets running side by side with only a sliver between them: the sliver is paved and becomes a
    long little square, as a market street, rather than a strip of grass nobody can build on."""
    walk = (STREET, LANE)
    squares = c.__dict__.setdefault('squares', set())
    def free(x, y):
        return c.ok(x, y) and c.inside[y * c.W + x] and not c.reserved[y * c.W + x] and c.t(x, y) in (G, D.TREE)
    def dist(x, y, dx, dy):
        for k in range(1, gap + 2):
            q = (x + dx * k, y + dy * k)
            if not c.ok(*q):
                return 99
            if c.t(*q) in walk and q not in squares:
                return k
            if not free(*q) and q not in squares:
                return 99
        return 99
    made = 0
    for _ in range(1):
        marks = []
        for y in range(c.H):
            for x in range(c.W):
                if not free(x, y):
                    continue
                if dist(x, y, -1, 0) + dist(x, y, 1, 0) <= gap + 1 or dist(x, y, 0, -1) + dist(x, y, 0, 1) <= gap + 1 \
                        or dist(x, y, -1, -1) + dist(x, y, 1, 1) <= gap or dist(x, y, 1, -1) + dist(x, y, -1, 1) <= gap:
                    marks.append((x, y))
        if dry:
            return len(marks)
        for (x, y) in marks:
            c.set(x, y, STREET)
            c.level[(x, y)] = 1
            c.dirs[(x, y)] = (1, 0)
            c.reserved[y * c.W + x] = 1
            squares.add((x, y))
        made += len(marks)
    return made


def check_inside(c):
    """Niels' rule: no house outside the wall."""
    bad = [(x, y) for y in range(c.H) for x in range(c.W)
           if c.t(x, y) in (PLANK, DOOR) and not c.inside[y * c.W + x]]
    assert not bad, bad[:5]


STONE_FG, STONE_BG, RIVER_BG = (214, 204, 182), (74, 70, 64), (16, 34, 70)
HALF = {(1, 0): '▐', (-1, 0): '▌', (0, 1): '▄', (0, -1): '▀',
        (1, 1): '▗', (-1, 1): '▖', (1, -1): '▝', (-1, -1): '▘'}


# ---------------------------------------------------------------- the makers
def church(c, x, y):
    """A parish church: nave, a tower at the west end, the altar east, a paved square round it."""
    rect(c, x, y, 13, 7)
    rect(c, x - 3, y + 1, 4, 5)
    c.set(x + 11, y + 3, D.ALTAR)
    for xx in range(x + 2, x + 9, 2):
        c.set(xx, y + 2, D.BENCH)
        c.set(xx, y + 4, D.BENCH)
    c.set(x + 6, y + 6, DOOR)
    reserve(c, x - 4, y - 3, 19, 11)
    church_square(c, x - 5, y - 3, 21, 12)
    c.great.append(('chapel', (x - 3, y, 16, 7), (x + 6, y + 6)))


def square(c, cx, cy, rx, ry, rough=.18, well=True):
    """A little square where a quarter grew: paved, a well in the middle."""
    sin, sedge = blob(cx, cy, rx, ry, rough=rough)
    for y in range(int(cy - ry * 1.5), int(cy + ry * 1.5)):
        for x in range(int(cx - rx * 1.5), int(cx + rx * 1.5)):
            if c.ok(x, y) and sin(x, y) and c.t(x, y) in (G, D.TREE):
                c.set(x, y, STREET)
                c.level[(x, y)] = 1
                c.dirs[(x, y)] = (1, 0)
                c.reserved[y * c.W + x] = 1
    if well:
        c.set(int(cx), int(cy), D.WELL)
    return sin, sedge


def bastioned(inside, edge, n=7, size=8):
    """A fortress town's wall: pointed bastions stand out from it at even steps, their faces at 45 degrees."""
    a0 = random.uniform(0, 6.3)
    pts = [edge(a0 + k * 2 * math.pi / n, 1.02) for k in range(n)]
    return lambda x, y: inside(x, y) or any(abs(x - bx) + abs(y - by) <= size for bx, by in pts)


def markets(c, sq_in, sq_c, n):
    """Stalls on the great market, and the fountain in its middle."""
    sx, sy = sq_c
    c.set(sx, sy, D.FOUNTAIN)
    cells = [(x, y) for (x, y) in c.level if sq_in(x, y) and c.t(x, y) == STREET]
    random.shuffle(cells)
    for (x, y) in cells:
        if len(c.stalls) < n and math.hypot(x - sx, y - sy) > 3 and \
                all(c.t(x + dx, y + dy) == STREET for dx in (-1, 0, 1) for dy in (-1, 0, 1)) and \
                not any(c.t(x + dx, y + dy) == D.STALL for dx in range(-2, 3) for dy in range(-2, 3)):
            c.set(x, y, D.STALL)
            c.stalls.append((x, y))


def fields(c, n, top=0, ditches=False):
    """Fields round the walls (meadows with ditches on low land)."""
    for _ in range(n):
        fw, fh = random.randint(8, 16), random.randint(4, 7)
        fx, fy = random.randint(1, c.W - fw - 1), random.randint(top + 1, c.H - fh - 2)
        cells = [(x, y) for y in range(fy - 1, fy + fh + 2) for x in range(fx - 1, fx + fw + 1)]
        if any(not c.ok(x, y) or c.inside[y * c.W + x] or c.t(x, y) not in (G, D.TREE) for x, y in cells):
            continue
        for y in range(fy, fy + fh):
            for x in range(fx, fx + fw):
                c.set(x, y, D.FIELD)
        if ditches:
            for x in range(fx, fx + fw):
                c.set(x, fy + fh, D.SHALLOW)


def gate_road(c, gx, gy, ang, far):
    """The road out from a gate across the land to the map's edge, and where it leaves the map."""
    out = (c.cx + math.cos(ang) * far, c.cy + math.sin(ang) * far)
    road = wobbly((gx, gy), out, 2, 8)
    dense = c.densify(road)
    edge = None
    for x, y in dense:
        q = (int(round(x)), int(round(y)))
        if not (0 < q[0] < c.W - 1 and 0 < q[1] < c.H - 1):
            break
        edge = q
    return road, edge


def grown_city(c, heart, river, roads, fortress=False, top=0):
    """A human city that grew over the centuries round its heart: a cathedral on the great market, a burgh with its
    own moat, or an emperor's walled palace. roads: [(angle, other)] of the roads of the world map coming in;
    top: rows left free at the top for the harbour."""
    sx_, sy_ = c.W / 196, (c.H - top) / 110
    cx, cy = c.W // 2 + random.randint(-4, 4), top + (c.H - top) // 2 + random.randint(-2, 2)
    c.cx, c.cy = cx, cy
    inside, edge = blob(cx, cy, 88 * sx_, 49 * sy_, rough=.09)
    wall_in = bastioned(inside, edge) if fortress else inside
    for y in range(top, c.H):
        for x in range(c.W):
            if random.random() < .02:
                c.set(x, y, D.TREE)
    rv = None
    if river:
        rv = canal_river(c, cy + int(24 * sy_) + random.randint(-3, 3), cy + int(20 * sy_) + random.randint(-3, 3), 3)
    c.city_wall(lambda x, y: y > top + 2 and wall_in(x, y), moat=True)
    if heart == 'cathedral':
        sq_in, sq_edge = blob(cx, cy + 2, 17, 9, rough=.18)
    elif heart == 'castle':
        sq_in, sq_edge = blob(cx + 2, cy + 5, 16, 7, rough=.2)
    else:
        sq_in, sq_edge = blob(cx, cy + 32, 13, 4, rough=.15)
    for y in range(c.H):
        for x in range(c.W):
            if sq_in(x, y) and c.t(x, y) == G:
                c.set(x, y, STREET)
                c.level[(x, y)] = 0
                c.reserved[y * c.W + x] = 1
    if heart == 'cathedral':
        cathedral(c, cx - 15, cy - 14)
        sq_c = (cx, cy + 2)
    elif heart == 'castle':
        hx, hy = cx - 4, cy - 15
        castle(c, hx, hy)
        sq_c = (cx + 2, cy + 5)
        for y in range(hy + 13, cy + 1):
            for x in (hx - 1, hx, hx + 1):
                if c.t(x, y) == G:
                    c.set(x, y, STREET)
                    c.level[(x, y)] = 0
    else:
        palace(c, cx, cy - 4)
        sq_c = (cx, cy + 32)
        for y in range(cy + 21, cy + 29):                  # the imperial way to the square
            for x in range(cx - 2, cx + 3):
                c.set(x, y, STREET)
                c.level[(x, y)] = 0
    # the old wall, long gone, now a ring street round the old town
    old_in, old_edge = blob(sq_c[0], sq_c[1] - 3, 44 * sx_, 27 * sy_, rough=.14)
    a0 = random.uniform(0, 6.3)
    arc = [old_edge(a0 + i * .08) for i in range(int(random.uniform(.75, .95) * 6.3 / .08))]
    if rv:   # quay walls and quays first, then the bridges: one below the market, one where the ring road crosses
        c.quay_walls()
        c.quays()
        c.plan_bridge(sq_c[0], kind='statues')
        for x, y, d in c.crossings(arc):
            c.plan_bridge(x, y, d)
    c.street(arc, 2, 1, over_water='cross')
    # main streets: from the market out towards the wall, never straight, six of them as the town grew; a gate
    # only where a road of the land comes in (the nearest street takes it), the others end at the lane by the wall
    base = [math.pi + .35 + random.uniform(-.1, .1), -.35 + random.uniform(-.1, .1),
            -math.pi / 2 + random.uniform(-.3, .3), math.pi / 2 + random.uniform(-.3, .3),
            random.uniform(.5, 1.1), math.pi + random.uniform(.5, 1.0)]
    ways = [[a, None, False] for a in base]
    for ang, other in roads:
        free = [w for w in ways if not w[2]]
        near = min(free, key=lambda w: abs(math.remainder(w[0] - ang, 2 * math.pi)), default=None)
        if near is not None and abs(math.remainder(near[0] - ang, 2 * math.pi)) < .6:
            near[0], near[1], near[2] = ang, other, True
        else:
            ways.append([ang, other, True])
    gates = []
    for k, (ang, other, gated) in enumerate(ways):
        ang = c.gate_angle(edge, ang)              # no gate where the river goes through the wall
        if ang is None:
            continue
        if not gated:
            sx, sy = sq_edge(ang + (.8 if heart == 'cathedral' and -2.3 < ang < -.8 else 0), .9)
            if heart == 'palace' and -2.5 < ang < -.6:
                sx, sy = cx + (28 if ang > -1.57 else -28), cy - 4
            pts = wobbly((sx, sy), edge(ang, .955), 3.2 if k < 4 else 4.5, 8)
            if k < 4:
                c.street(pts, 2, 0)
            else:
                c.street_join(pts[::-1], 2, 1)
            continue
        gx, gy = edge(ang)
        sx, sy = sq_edge(ang + (.8 if heart == 'cathedral' and -2.3 < ang < -.8 else 0), .9)
        if heart == 'palace' and -2.5 < ang < -.6:
            sx, sy = cx + (28 if ang > -1.57 else -28), cy - 4
        pts = wobbly((sx, sy), (gx, gy), 3.2 if k < 4 else 4.5, 8)
        if k < 4:
            c.street(pts, 2, 0)
        else:                           # comes in from its gate and joins the first street it meets
            c.street_join(pts[::-1], 2, 1)
        road, out = gate_road(c, gx, gy, ang, 400)
        c.gate(pts[-3:] + road[:3])
        c.street(road, 2, 0 if k < 4 else 1)
        gates.append((gx, gy))
        c.exits.append((out, other))
    # a lane runs just inside the wall
    c.street([edge(i * .05, .955) for i in range(127)], 1, 2)
    if rv:
        river_quays(c)
    # little squares with a well where the town grew round them
    for _ in range(5):
        for _ in range(50):
            px, py = random.randint(15, c.W - 15), random.randint(top + 12, c.H - 12)
            if inside(px, py, .8) and not c.reserved[py * c.W + px] and c.t(px, py) == G \
                    and math.hypot(px - sq_c[0], (py - sq_c[1]) * 1.6) > 30:
                square(c, px, py, random.randint(4, 6), random.randint(3, 4), rough=.25)
                c.street_join(wobbly((px, py), (sq_c[0] + (px - sq_c[0]) * .3, sq_c[1] + (py - sq_c[1]) * .3), 3, 6), 1, 1)
                break
    if heart != 'cathedral':                       # a parish church on a square of its own
        for _ in range(200):
            px, py = random.randint(20, c.W - 20), random.randint(top + 14, c.H - 14)
            foot = [(xx, yy) for yy in range(py - 4, py + 9) for xx in range(px - 6, px + 16)]
            if all(c.ok(*q) and c.inside[q[1] * c.W + q[0]] and c.t(*q) in (G, D.TREE) and
                   not c.reserved[q[1] * c.W + q[0]] for q in foot):
                church(c, px, py)
                break
    n = sx_ * sy_                                  # the mock-up's tries, for the size of this map
    c.grow_lanes(int(2500 * n), lambda x, y: c.inside[y * c.W + x] and old_in(x, y), gap=5, maxlen=30)
    c.grow_lanes(int(5000 * n), lambda x, y: c.inside[y * c.W + x], gap=6, maxlen=40, deadend=.04)
    c.grow_lanes(int(2500 * n), lambda x, y: c.inside[y * c.W + x], gap=6, maxlen=28, deadend=.5)

    def size(x, y, p):
        if p == 2:
            return random.randint(4, 5), random.randint(4, 5)
        if old_in(x, y):
            return random.randint(5, 7), random.randint(6, 8)
        return random.randint(5, 8), random.randint(5, 6)
    finish(c, sq_c, gates, size)
    markets(c, sq_in, sq_c, 14)
    fields(c, 40, top)
    return sq_c


def metropolis(c, heart, roads, top=0):
    """The metropolis: an old core inside the line of the first wall, newer quarters inside the line of the second,
    the outer quarters inside today's wall, on a broad river."""
    sx_, sy_ = c.W / 360, (c.H - top) / 220
    cx, cy = c.W // 2 + random.randint(-6, 6), top + (c.H - top) // 2 + random.randint(-4, 4)
    c.cx, c.cy = cx, cy
    inside, edge = blob(cx, cy, 166 * sx_, 100 * sy_, rough=.08)
    for y in range(top, c.H):
        for x in range(c.W):
            if random.random() < .02:
                c.set(x, y, D.TREE)
    canal_river(c, cy + int(34 * sy_) + random.randint(-4, 4), cy + int(26 * sy_) + random.randint(-4, 4), 5)
    c.city_wall(lambda x, y: y > top + 2 and inside(x, y), tower_every=15, moat=True)
    sq_c = (cx, cy + 4)
    sq_in, sq_edge = blob(cx, cy + 4, 15, 7, rough=.2)
    if heart == 'palace':                          # the emperor's walled city stands over the great market
        palace(c, cx, cy - 34)
        for y in range(cy - 9, cy - 2):
            for x in range(cx - 2, cx + 3):
                c.set(x, y, STREET)
                c.level[(x, y)] = 0
    for y in range(c.H):
        for x in range(c.W):
            if sq_in(x, y) and c.t(x, y) == G:
                c.set(x, y, STREET)
                c.level[(x, y)] = 0
                c.reserved[y * c.W + x] = 1
    if heart == 'palace':
        cathedral(c, cx + 30, cy - 10)
    else:
        cathedral(c, cx - 15, cy - 14)
    castle(c, cx - 62, cy - 30)                    # the burgh on its rise at the edge of the old town
    for y in range(cy - 17, cy - 8):
        for x in (cx - 63, cx - 62, cx - 61):
            if c.t(x, y) == G:
                c.set(x, y, STREET)
                c.level[(x, y)] = 1
    c.quay_walls()
    c.quays()
    c.plan_bridge(sq_c[0], kind='statues')        # the market bridge
    core_in = mid_in = None
    for (rx, ry, wd, part) in ((44, 27, 2, .9), (100, 62, 3, 1.0)):
        oin, oedge = blob(sq_c[0], sq_c[1] - 4, rx * sx_, ry * sy_, rough=.12)
        a0 = random.uniform(0, 6.3)
        n = int(part * 6.3 / .04)
        for x, y, d in c.crossings([oedge(a0 + i * .04) for i in range(n + 1)]):
            c.plan_bridge(x, y, d)                # where the ring road crosses
        c.street([oedge(a0 + i * .04) for i in range(n + 1)], wd, 1, over_water='cross')
        if rx == 44:
            core_in = oin
        else:
            mid_in = oin
    gates = []
    for k, (ang, other) in sorted(enumerate(roads), key=lambda e: e[0] % 2):
        ang = c.gate_angle(edge, ang, margin=14)
        if ang is None:
            continue
        gx, gy = edge(ang)
        sx, sy = sq_edge(ang + (.9 if -2.3 < ang < -.8 else 0), .9)
        pts = wobbly((sx, sy), (gx, gy), 4, 9)
        if k % 2 == 0:                  # the great ways run from the market to their gates
            c.street(pts, 3, 0)
        else:                           # the others come in from their gate and join the first street they meet
            c.street_join(pts[::-1], 2, 0)
        road, out = gate_road(c, gx, gy, ang, 600)
        c.gate(pts[-3:] + road[:3])
        c.street(road, 2, 0)
        gates.append((gx, gy))
        c.exits.append((out, other))
    # streets that began outside the first wall run from the ring outwards
    for _ in range(10):
        a = random.uniform(0, 6.3)
        sx, sy = sq_c[0] + math.cos(a) * 46 * sx_, sq_c[1] - 4 + math.sin(a) * 29 * sy_
        ex, ey = edge(a, .94)
        c.street_join(wobbly((ex, ey), (sx, sy), 5, 9), 2, 1)
    c.street([edge(i * .025, .97) for i in range(253)], 1, 2)
    river_quays(c)
    # quarters grew round their own squares: a well, a parish church, a little market
    spots = []
    for _ in range(400):
        if len(spots) >= 16:
            break
        px, py = random.randint(20, c.W - 20), random.randint(top + 14, c.H - 14)
        if not inside(px, py, .9) or c.reserved[py * c.W + px] or c.t(px, py) != G:
            continue
        if math.hypot(px - sq_c[0], (py - sq_c[1]) * 1.6) < 40 or any(math.hypot(px - a, (py - b) * 1.6) < 34 for a, b in spots):
            continue
        spots.append((px, py))
        kind = len(spots) % 3
        rx, ry = (7, 4) if kind == 0 else (5, 3)
        square(c, px, py, rx, ry, well=kind != 0)
        if kind == 1 and c.t(px - 6, py - 11) == G:
            church(c, px - 6, py - 11)
        if kind == 0:
            for _ in range(5):
                q = (px + random.randint(-5, 5), py + random.choice((-2, 2)))
                if c.ok(*q) and c.t(*q) == STREET:
                    c.set(*q, D.STALL)
        tx, ty = sq_c[0] + (px - sq_c[0]) * .55, sq_c[1] + (py - sq_c[1]) * .55
        c.street_join(wobbly((px, py), (tx, ty), 3, 7), 2, 1)
    c.grow_lanes(5000, lambda x, y: c.inside[y * c.W + x] and core_in(x, y), gap=4, maxlen=26)
    c.grow_lanes(9000, lambda x, y: c.inside[y * c.W + x] and mid_in(x, y), gap=5, maxlen=34, deadend=.04)
    c.grow_lanes(12000, lambda x, y: c.inside[y * c.W + x], gap=6, maxlen=44, deadend=.04)
    c.grow_lanes(6000, lambda x, y: c.inside[y * c.W + x], gap=6, maxlen=28, deadend=.5)   # closes in the far yards

    def size(x, y, p):
        if p == 2:
            return random.randint(4, 5), random.randint(4, 5)
        if core_in(x, y):
            return random.randint(5, 7), random.randint(6, 8)
        if mid_in(x, y):
            return random.randint(5, 8), random.randint(5, 7)
        return random.randint(6, 9), random.randint(5, 6)
    finish(c, sq_c, gates, size)
    markets(c, sq_in, sq_c, 16)
    fields(c, 80, top)
    return sq_c


def river_quays(c):
    """Quays along the river inside the walls."""
    for (x, y) in [(i % c.W, i // c.W) for i in range(c.W * c.H) if c.m.t[i] == WATER]:
        for dx, dy in ((0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if c.ok(nx, ny) and c.inside[ny * c.W + nx] and c.t(nx, ny) == G:
                c.set(nx, ny, STREET)
                c.level[(nx, ny)] = 1
                c.dirs[(nx, ny)] = (1, 0)


def finish(c, sq_c, gates, size, passes=3, approach=8):
    """The bridges dressed, the gates' bridges over the moat, every way joined, and the houses in their rows."""
    c.market = sq_c
    c.bridges = stone_bridges(c)
    drawbridges(c, gates)
    straight_approaches(c, approach)
    connect(c, sq_c)
    fill_slivers(c)
    c.rows(size, passes)
    fill_slivers(c)
    connect(c, sq_c)


# ---------------------------------------------------------------- the canal city
RINGS = (14, 34, 54)            # the canals; blocks deep enough for two rows of canal houses
WALLR = 68                      # the bastioned wall
E = 18                          # the rings are stretched sideways by this much
K = 1.55                        # how much of each corner is cut off at 45 degrees: a horseshoe


def octi(a, b):
    """A way between two points with only straight and 45-degree reaches: first straight, then slanting."""
    (ax, ay), (bx, by) = a, b
    dx, dy = bx - ax, by - ay
    n = min(abs(dx), abs(dy))
    sx, sy = (1 if dx > 0 else -1 if dx < 0 else 0), (1 if dy > 0 else -1 if dy < 0 else 0)
    mid = (bx - sx * n, ay) if abs(dx) > abs(dy) else (ax, by - sy * n)
    return [a, mid, b]


def cells_of(pts):
    out = []
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        n = max(abs(bx - ax), abs(by - ay), 1)
        for i in range(n + 1):
            q = (round(ax + (bx - ax) * i / n), round(ay + (by - ay) * i / n))
            if not out or out[-1] != q:
                out.append(q)
    return out


def canal_city(c, roads, shore):
    """A harbour city with canal rings, after old Amsterdam and Haarlem: half rings of canals round the Dam, every
    reach straight and every turn 45 degrees; a stone quay wall along all water; the river tamed into a canal; a
    bastioned wall with a broad moat on the land side. The harbour lies above `shore`."""
    W, H = c.W, c.H
    cx, cy = W // 2 + random.randint(-4, 4), shore + 7               # cy: the Dam
    c.cx, c.cy = cx, cy

    def m(x, y):                                             # distance in rings: half an octagon round the Dam
        dxp = max(0, abs(x - cx) - E)
        dy = y - cy
        if dy < 0:
            return dxp
        return max(dxp, dy, (dxp + dy) / K)

    def normal(x, y):                                        # the way out from the Dam across the rings here
        dxp = max(0, abs(x - cx) - E)
        dy = max(0, y - cy)
        sx = 1 if x > cx else -1
        a, b, d = dxp, dy, (dxp + dy) / K
        if a >= b and a >= d:
            return (sx, 0)
        if b >= a and b >= d:
            return (0, 1)
        return (sx, 1)

    for y in range(shore, H):
        for x in range(W):
            if random.random() < .015:
                c.set(x, y, D.TREE)
    bast = []
    for sg in (-1, 1):
        bx, by = cx + sg * (E + WALLR), cy + int((K - 1) * WALLR)          # the long side meets the slant
        qx, qy = cx + sg * (E + int((K - 1) * WALLR)), cy + WALLR            # the slant meets the bottom
        bast += [(bx, by), (qx, qy), ((bx + qx) // 2, (by + qy) // 2), (bx, cy + 3)]
    bast.append((cx, cy + WALLR))
    inside_fn = lambda x, y: y >= shore and (m(x, y) < WALLR or any(abs(x - bx) + abs(y - by) <= 8 for bx, by in bast))
    c.city_wall(inside_fn, tower_every=500, moat=True, moat_w=5, open_to=lambda x, y: y <= shore + 1)
    canal = set()
    for y in range(shore, H):
        for x in range(W):
            if c.inside[y * W + x] and any(abs(m(x, y) - r) < 1.6 for r in RINGS):
                canal.add((x, y))
    ax = cx + 6                                  # the river, tamed: from the south wall up to the Dam, one turn
    for (x, y) in cells_of([(ax + 18, H), (ax + 18, cy + 46), (ax, cy + 28), (ax, cy + 5)]):
        for ox in (-2, -1, 0, 1, 2):
            canal.add((x + ox, y))
    for y in range(shore, cy - 3):              # the Damrak: the harbour arm from the shore to the Dam
        for ox in (-2, -1, 0, 1, 2):
            canal.add((cx + ox, y))
    for x0 in (cx - 14, cx + 15):               # two old town canals beside it
        for y in range(shore, cy + RINGS[0]):
            if m(x0, y) < RINGS[0]:
                for ox in (-1, 0, 1):
                    canal.add((x0 + ox, y))
    for (x, y) in canal:
        if c.ok(x, y) and c.t(x, y) != WALLT:
            c.set(x, y, WATER)
            c.reserved[y * W + x] = 1
            c.river.add((x, y))
    c.quay_walls(canal)
    for (x, y) in list(c.river) + [(x, shore - 1) for x in range(W)]:
        for ox in (-2, -1, 0, 1, 2):
            for oy in (-2, -1, 0, 1, 2):
                q = (x + ox, y + oy)
                if c.ok(*q) and c.inside[q[1] * W + q[0]] and c.t(*q) in (G, D.TREE):
                    c.set(*q, STREET)
                    c.level[q] = 1
                    nx, ny = normal(*q)
                    c.dirs[q] = (-ny, nx)
                    c.reserved[q[1] * W + q[0]] = 1
    for y in range(cy - 4, cy + 6):             # the Dam, the town hall on its west side
        for x in range(cx - 9, cx + 10):
            if c.t(x, y) in (G, D.TREE, STREET):
                c.set(x, y, STREET)
                c.level[(x, y)] = 0
                c.reserved[y * W + x] = 1
    rect(c, cx - 9, cy + 5, 12, 6)
    c.set(cx - 3, cy + 5, DOOR)
    c.set(cx - 3, cy + 8, D.HIGHSEAT)
    c.great.append(('keep', (cx - 9, cy + 5, 12, 6), (cx - 3, cy + 5)))
    gates = []
    for _ in range(600):                        # the great church in the old town, on dry land
        x, y = random.randint(cx - E - 30, cx + E + 10), random.randint(cy + RINGS[0] + 3, cy + RINGS[1] - 12)
        foot = [(xx, yy) for yy in range(y - 1, y + 10) for xx in range(x - 4, x + 17)]
        if all(c.ok(*q) and c.inside[q[1] * W + q[0]] and c.t(*q) in (G, D.TREE) and not c.reserved[q[1] * W + q[0]]
               for q in foot):
            rect(c, x, y, 15, 8)
            rect(c, x - 3, y + 1, 4, 6)
            c.set(x + 13, y + 4, D.ALTAR)
            for xx in range(x + 2, x + 11, 2):
                c.set(xx, y + 2, D.BENCH)
                c.set(xx, y + 5, D.BENCH)
            c.set(x + 7, y + 7, DOOR)
            reserve(c, x - 4, y - 1, 21, 11)
            church_square(c, x - 5, y - 2, 23, 13)
            c.great.append(('temple', (x - 3, y, 18, 8), (x + 7, y + 7)))
            break

    def ring_cells(mid):
        ring = [(x, y) for y in range(shore + 2, H) for x in range(W) if abs(m(x, y) - mid) < .5 and c.inside[y * W + x]]
        ring.sort(key=lambda q: math.atan2(q[1] - cy, q[0] - cx))
        return ring

    def outward(q):
        """From q straight out across the rings, square to every canal, to the wall."""
        nx, ny = normal(*q)
        x, y = q
        while c.ok(x + nx, y + ny) and c.inside[(y + ny) * W + x + nx] and m(x + nx, y + ny) < WALLR - 1:
            x, y = x + nx, y + ny
        return (x, y)
    lines = []
    core = ring_cells(RINGS[0] - 4)
    # the great ways: from the Dam to the first ring, then straight out across the rings to a gate; each world
    # road takes the way out nearest its own heading
    used = set()
    for ang, other in roads:
        cands = [f for f in (.12, .36, .6, .86) if f not in used]
        if not cands or not core:
            break
        f = min(cands, key=lambda f: abs(math.atan2(math.sin(ang - math.atan2(core[int(f * (len(core) - 1))][1] - cy,
                                                                               core[int(f * (len(core) - 1))][0] - cx)),
                                                     math.cos(ang - math.atan2(core[int(f * (len(core) - 1))][1] - cy,
                                                                               core[int(f * (len(core) - 1))][0] - cx)))))
        used.add(f)
        q = core[int(f * (len(core) - 1))]
        if abs(q[0] - (cx + 6)) < 8:
            q = core[min(len(core) - 1, int(f * (len(core) - 1)) + 10)]
        g = outward(q)
        dam = (cx - 11, cy + 2) if q[0] < cx else (cx + 10, cy + 2)    # round the town hall
        lines.append((octi(dam, q) + [g], 3, 0))
        gates.append(g)
        nx, ny = normal(*q)
        far = (g[0] + nx * 12, g[1] + ny * 12)
        road = [g, far] + wobbly(far, (g[0] + nx * 400, g[1] + ny * 400), 2, 8)[1:]
        c.street(road, 2, 0)
        edge = None
        for x, y in c.densify(road):
            p = (int(round(x)), int(round(y)))
            if not (0 < p[0] < W - 1 and 0 < p[1] < H - 1):
                break
            edge = p
        c.exits.append((edge, other))
    for q in ring_cells(RINGS[1] + 9)[10::40]:   # long cross streets right through the rings
        nx, ny = normal(*q)
        mq = m(*q)
        a = (q[0] - nx * (mq - RINGS[0] + 3), q[1] - ny * (mq - RINGS[0] + 3))
        b = (q[0] + nx * (WALLR - 4 - mq), q[1] + ny * (WALLR - 4 - mq))
        if math.hypot(a[0] - cx, a[1] - cy) > 12:
            lines.append(([(round(a[0]), round(a[1])), (round(b[0]), round(b[1]))], 2, 1))
    for r0, r1 in zip(RINGS, RINGS[1:] + (WALLR - 3,)):      # short cross streets: quay to quay across a block
        mid = (r0 + r1) / 2
        for q in ring_cells(mid)[random.randint(0, 8)::17]:
            nx, ny = normal(*q)
            a = (q[0] - nx * (mid - r0), q[1] - ny * (mid - r0))
            b = (q[0] + nx * (r1 - mid), q[1] + ny * (r1 - mid))
            lines.append(([(round(a[0]), round(a[1])), (round(b[0]), round(b[1]))], 1, 1))
    for pts, width, level in lines:
        cs = cells_of(pts)
        k = 0
        while k < len(cs):
            if cs[k] in canal and c.wet_at(*cs[k]) or cs[k] in getattr(c, 'quaywall', ()):
                j = k
                while j < len(cs) and (cs[j] in canal):
                    j += 1
                run = cs[k:j]
                if width >= 2 and run:
                    mx, my = run[len(run) // 2]
                    a, b = cs[max(0, k - 1)], cs[min(len(cs) - 1, j)]
                    d = (int(math.copysign(1, b[0] - a[0])) if b[0] != a[0] else 0,
                         int(math.copysign(1, b[1] - a[1])) if b[1] != a[1] else 0)
                    if c.wet_at(mx, my):
                        c.plan_bridge(mx, my, d, 'canal', spacing=3, maxlen=10)
                k = j
            k += 1
        c.street(pts, width, level, over_water=False)
    for x0 in range(cx - E - WALLR + 4, cx + E + WALLR - 12, 13):    # warehouses on the harbour quay
        if abs(x0 + 5 - cx) < 22:
            continue
        if all(c.ok(x, y) and c.t(x, y) in (G, D.TREE) and c.inside[y * W + x]
               for x in range(x0, x0 + 10) for y in range(shore + 3, shore + 8)):
            rect(c, x0, shore + 3, 10, 5)
            c.set(x0 + 5, shore + 3, DOOR)
            for x in range(x0 + 2, x0 + 8, 2):
                c.set(x, shore + 5, D.BARREL)
    c.grow_lanes(1600, lambda x, y: c.inside[y * W + x] and m(x, y) < RINGS[0] - 1.5, gap=4, maxlen=20)

    def size(x, y, p):
        if m(x, y) < RINGS[0]:
            return random.randint(5, 7), random.randint(5, 7)
        return random.randint(4, 5), random.randint(5, 6)     # narrow, deep canal houses
    c.market = (cx, cy)
    drawbridges(c, gates)
    straight_approaches(c, 5)
    connect(c, (cx, cy))
    fill_slivers(c)
    c.rows(size, passes=5)
    fill_slivers(c)
    connect(c, (cx, cy))
    for (x, y) in list(c.level):                # trees along the quays, by the quay wall
        if c.t(x, y) == STREET and c.level[(x, y)] == 1 and (x * 7 + y * 3) % 6 == 0 \
                and any((x + ex, y + ey) in c.quaywall for ex, ey in ((1, 0), (-1, 0), (0, 1), (0, -1))) \
                and (x, y) not in c.deck:
            c.set(x, y, D.TREE)
    dam_in = lambda x, y: cx - 9 <= x < cx + 10 and cy - 4 <= y < cy + 5
    markets(c, dam_in, (cx, cy), 10)
    fields(c, 60, shore, ditches=True)
    return (cx, cy)


# ---------------------------------------------------------------- into the game
# A city is made in its own frame, with the sea (if any) to the north and the river running west to east, then
# turned to face the world: the sea on its side, the river the way it runs on the world map.
def _to(frame, W, H):
    """Canonical (x, y) -> the map's own (x, y)."""
    return {'N': lambda x, y: (x, y), 'S': lambda x, y: (x, H - 1 - y),
            'W': lambda x, y: (y, x), 'E': lambda x, y: (H - 1 - y, x)}[frame]


def _dir_in(frame, dx, dy):
    """A heading on the map -> the same heading in the canonical frame."""
    return {'N': (dx, dy), 'S': (dx, -dy), 'W': (dy, dx), 'E': (dy, -dx)}[frame]


def ruler(game, s):
    """Who sits in the city decides its heart: the emperor's palace, a king's or baron's burgh, else the cathedral;
    and whether it is a fortress town: the seat of a march, a border land where the realm meets another power."""
    from . import realms as RL
    R = RL.get(game)
    if R is None:
        return 'cathedral', False
    seat = ('s', s.id)
    if R.great == s.id:
        heart = 'palace'
    elif any(kg.seat == seat for kg in R.kingdoms) or any(b.seat == seat for b in R.baronies.values()):
        heart = 'castle'
    else:
        heart = 'cathedral'
    b = R.baronies.get(s.region)
    return heart, bool(b and 'March' in b.name)


def plan(game, s):
    """What kind of city this is and how it lies: (maker, heart, fortress, frame, river)."""
    from . import towns as TW
    big = s.kind == 'metropolis'
    heart, border = ruler(game, s)
    harbour = getattr(s, 'harbour', False)
    W, H = (360, 220) if big else (240, 140)
    probe = GameMap('probe', 'town', '', W, H, G)
    course = TW.river_course(game, s, probe, 14)
    if harbour:
        frame = s.sea_side
    elif course and abs(course[-1][1] - course[0][1]) > abs(course[-1][0] - course[0][0]):
        frame = 'W'                                   # the river runs north and south: the city lies turned
    else:
        frame = 'N'
    if big:
        maker = 'metropolis'
    elif harbour and s.biome not in ('hills', 'mountain', 'mountains', 'tundra'):
        maker = 'canal'
    else:
        maker = 'grown'
    if maker == 'metropolis' and heart == 'castle':
        heart = 'cathedral'
    return maker, heart, border and maker == 'grown', frame, bool(course) or big


def grow(key, name, maker, heart='cathedral', fortress=False, river=True, roads=((math.pi / 2, None),), top=0):
    """The city itself, in its own frame, before it is turned and peopled: (City, the market's middle)."""
    W, H = (360, 220) if maker == 'metropolis' else (240, 140)
    c = City(key, name, W, H)
    roads = spread(list(roads))
    if maker == 'metropolis':
        sq = metropolis(c, heart, roads, top)
    elif maker == 'canal':
        sq = canal_city(c, roads, top)
    else:
        sq = grown_city(c, heart, river, roads, fortress, top)
    check_inside(c)
    crumbs(c)
    return c, sq


def spread(roads, least=.5):
    """Two roads of the land that come in from nearly the same side get gates a little apart, each its own."""
    out = []
    for ang, other in roads:
        for _ in range(8):
            near = [a for a, _ in out if abs(math.remainder(a - ang, 2 * math.pi)) < least]
            if not near:
                break
            ang = near[0] + (least if math.remainder(ang - near[0], 2 * math.pi) >= 0 else -least)
        out.append((ang, other))
    return out


def crumbs(c, most=6):
    """A scrap of street left cut off by the houses and water round it goes back to garden."""
    start = getattr(c, 'market', None)
    if start is None:
        return
    seen, q = {start}, [start]
    while q:
        x, y = q.pop()
        for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if n not in seen and c.ok(*n) and c.t(*n) in STREETS:
                seen.add(n)
                q.append(n)
    for cell in [q for q in c.level if q not in seen and c.t(*q) in (STREET, LANE)]:
        if cell in seen or cell not in c.level:
            continue
        part, q = {cell}, [cell]
        while q and len(part) <= most:
            x, y = q.pop()
            for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if n not in part and c.ok(*n) and c.t(*n) in STREETS:
                    part.add(n)
                    q.append(n)
        seen |= part
        if len(part) <= most and all(c.t(*n) in (STREET, LANE) for n in part):
            for n in part:
                c.set(*n, G)
                c.level.pop(n, None)


def rules(c):
    """The rules Nilio set while looking at the mock-ups, each counted: every count must be 0."""
    W, H = c.W, c.H
    out = {}
    river, deck = c.river, c.deck
    quay = {(x, y) for (x, y) in c.level if c.t(x, y) == STREET and
            any((x + ex, y + ey) in river for ex in range(-2, 3) for ey in range(-2, 3))}
    street = lambda x, y: c.ok(x, y) and c.t(x, y) in (STREET, LANE)
    sq = getattr(c, 'squares', set())
    # a way that reaches the river on both banks, across from each other, has a bridge
    bad = 0
    for x in range(W):
        col = [y for y in range(H) if (x, y) in river and c.inside[y * W + x]]
        if not col or max(col) - min(col) > 20:
            continue
        lo, hi = min(col), max(col)
        aim = lambda xx, ys: all(street(xx, y) and (xx, y) not in quay and (xx, y) not in sq for y in ys)
        north = any(aim(x + o, range(lo - 8, lo - 3)) and not street(x + o - 3, lo - 6) and not street(x + o + 3, lo - 6)
                    for o in (-1, 0, 1))
        south = any(aim(x + o, range(hi + 4, hi + 9)) and not street(x + o - 3, hi + 6) and not street(x + o + 3, hi + 6)
                    for o in (-1, 0, 1))
        if north and south and not any((x + o, y) in deck for o in range(-6, 7) for y in range(lo - 2, hi + 3)):
            bad += 1
    out['way without a bridge'] = bad
    out['two streets side by side'] = fill_slivers(c, dry=True)
    # a way runs in line with its bridge for a good stretch at both ends
    bad = 0
    keep = (D.STALL, D.WELL, D.FOUNTAIN, D.LAMP)
    for b in c.planned:
        (dx, dy), s0, s1 = b['d'], b['s0'], b['s1']
        for (sx, sy), sg in ((s0, -1), (s1, 1)):
            okk = lambda x, y: not c.ok(x, y) or x in (0, W - 1) or y in (0, H - 1) or street(x, y) or c.t(x, y) in keep
            if not all(okk(sx + dx * sg * k, sy + dy * sg * k) for k in range(1, 4 if b['kind'] == 'canal' else 6)):
                bad += 1
    out['way out of line with its bridge'] = bad
    out['bridge along the water'] = sum(1 for b in c.planned if not c.across(*b['mid'], b['d']))
    gb = [b['mid'] for b in c.planned if b['kind'] == 'gate']
    out['gate without a bridge'] = sum(1 for (gx, gy) in c.gates
                                       if not any(math.hypot(mx - gx, my - gy) < 18 for mx, my in gb))
    out['building in the water'] = sum(
        1 for y in range(H) for x in range(W) if c.t(x, y) in (PLANK, FLOOR) and
        any(c.ok(x + ex, y + ey) and c.t(x + ex, y + ey) in (WATER, D.SHALLOW) for ex in (-1, 0, 1) for ey in (-1, 0, 1)))
    start = getattr(c, 'market', None) or next(iter(c.level))
    q, seen = [start], {start}
    while q:
        x, y = q.pop()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) not in seen and c.ok(nx, ny) and c.t(nx, ny) in STREETS:
                seen.add((nx, ny))
                q.append((nx, ny))
    out['loose piece of street'] = sum(1 for (x, y) in c.level if c.t(x, y) in (STREET, LANE) and c.inside[y * W + x]
                                       and (x, y) not in seen and (x, y) not in getattr(c, 'enclosed', ()))
    return out


def make(game, s):
    """The map of a human city or the metropolis, grown as old towns grew (see docs/built.md, Cities that grew)."""
    from . import towns as TW, harbour as HB, guilds as GU
    maker, heart, fortress, frame, river = plan(game, s)
    big = maker == 'metropolis'
    W, H = (360, 220) if big else (240, 140)
    top = HB.depth_for(s) if getattr(s, 'harbour', False) else 0
    roads = []
    for dx, dy, other in (TW.road_dirs(game, s) or [(0, 1, None)]):
        cdx, cdy = _dir_in(frame, dx, dy)
        roads.append((math.atan2(cdy, cdx), other))
    if top:
        roads.append((-math.pi / 2, 'harbour'))      # a way down to the harbour
    roads.sort(key=lambda r: r[1] is None or r[1] == 'harbour')
    c, sq = grow(s.map_key, s.name, maker, heart, fortress, river, roads, top)
    to = _to(frame, W, H)
    mw, mh = (W, H) if frame in ('N', 'S') else (H, W)
    m = GameMap(s.map_key, 'town', s.name, mw, mh, G)
    for y in range(H):
        for x in range(W):
            nx, ny = to(x, y)
            m.t[ny * mw + nx] = c.m.t[y * W + x]
    tset = lambda cells: {to(*q) for q in cells if c.ok(*q)}
    deck, parapet, quay, draw = tset(c.deck), tset(c.parapet), tset(c.quaywall), tset(getattr(c, 'draw', ()))
    m.radius, m.sid, m.hid, m.signs = 60, s.id, None, []
    m.stone_bridges = True
    m.grown = maker
    m.exits = []
    for edge, other in c.exits:
        if edge is not None and other != 'harbour':
            ex, ey = to(*edge)
            m.exits.append((ex, ey, other))
    if not m.exits:                                   # the land had no road: the way in comes from the south
        ex, ey = to(int(c.cx), H - 2)
        m.exits.append((ex, ey, None))
    plots = []
    if top:
        plots.append(HB.carve(m, s))
    _dress(m, deck, parapet, quay, draw)
    px, py = to(*sq)
    buildings = _buildings(game, m, s, c, to, big, plots)
    stalls = [to(*q) for q in c.stalls]
    lamps = [(x, y) for y in range(mh) for x in range(mw) if m.t[y * mw + x] == D.LAMP]
    m.lamps, m.lamp_on = lamps, set()
    TW.place_lamps(m, _roadside(m, c, to))
    walk = (STREET, LANE)
    streets = [to(*q) for q, l in c.level.items() if l <= 1 and c.t(*q) in walk and c.inside[q[1] * W + q[0]]]
    names = TW.town_names(getattr(s, 'race', 'human'))
    TW.people_city(game, m, s, buildings, names, px, py, stalls or [(px + 2, py)], streets, 14 if big else 9)
    m.entry = m.exits[0][:2]
    for i in range(len(m.seen)):
        m.seen[i] = 1
    return m


def _dress(m, deck, parapet, quay, draw):
    """A stone bridge has its own look: a deck of grey flagstones and thin pale parapets standing in the water,
    drawn as half blocks on the deck side; the quay walls the same on the land side."""
    m.over = getattr(m, 'over', None) or {}
    wet = (WATER, D.SHALLOW)
    for (x, y) in quay | parapet:
        if not m.inb(x, y) or m.tile(x, y) != WALLT:
            continue
        look = ('■', STONE_FG, RIVER_BG)
        for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)):
            q = (x + dx, y + dy)
            if (x, y) in parapet and q in deck or (x, y) not in parapet and m.inb(*q) and \
                    m.tile(*q) not in wet + (WALLT, BRIDGE):
                look = (HALF[(dx, dy)], STONE_FG, RIVER_BG)
                break
        m.over[y * m.w + x] = look
    for (x, y) in deck:
        if m.inb(x, y) and m.tile(x, y) == STREET:
            m.over[y * m.w + x] = ('·' if (x * 7 + y * 3) % 5 else ' ', (150, 144, 132), STONE_BG)
    for (x, y) in draw:
        if m.inb(x, y) and m.tile(x, y) == BRIDGE:
            m.over[y * m.w + x] = ('≡' if (x + y) % 3 else '-', (176, 124, 70), (58, 38, 20))


def _roadside(m, c, to):
    """Lamp posts along the great ways, on the edge of the street, about every ten steps."""
    out = []
    for (x, y), l in sorted(c.level.items()):
        if l != 0 or c.t(x, y) != STREET or not c.inside[y * c.W + x] or (x * 3 + y * 7) % 10:
            continue
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if c.ok(*q) and c.t(*q) in (G, D.TREE) and c.inside[q[1] * c.W + q[0]]:
                out.append(to(*q))
                break
    return out


def _buildings(game, m, s, c, to, big, plots):
    """The houses of the rows become the town's buildings: inns by the gates, shops and guild halls by the market,
    the watch by the wall, the secret halls down a lane; the great buildings keep what they are."""
    from . import towns as TW, guilds as GU

    def plot(kind, x0, y0, x1, y1, door):
        (ax, ay), (bx, by) = to(x0, y0), to(x1, y1)
        pl = TW.Plot(min(ax, bx), min(ay, by), abs(bx - ax) + 1, abs(by - ay) + 1, kind)
        pl.door = to(*door) if door else None
        pl.inside = [(x, y) for y in range(pl.y + 1, pl.y + pl.h - 1) for x in range(pl.x + 1, pl.x + pl.w - 1)]
        pl.annex = None
        return pl
    out = []
    for kind, (x, y, w, h), door in c.great:
        pl = plot('temple' if kind in ('temple', 'chapel') else 'keep', x, y, x + w - 1, y + h - 1, door)
        pl.inside = [q for q in pl.inside if m.tile(*q) in (D.FLOOR, D.PLANK)]
        pl.great = kind
        out.append(pl)
        if pl.kind == 'temple' and pl.door:
            TW.add_sign(m, pl, TW.SIGN['temple'])
    if out and any(p.great == 'keep' for p in out):
        m.seat = next(p for p in out if p.great == 'keep')
    houses = [h for h in c.houses if h[4] and (h[2] - h[0] - 1) * (h[3] - h[1] - 1) >= 4]
    mx, my = c.market
    gates = getattr(c, 'gates', []) or [(c.cx, c.H - 2)]
    dist = lambda h, p: math.hypot((h[0] + h[2]) / 2 - p[0], (h[1] + h[3]) / 2 - p[1])
    area = lambda h: (h[2] - h[0] - 1) * (h[3] - h[1] - 1)
    taken = set()

    def pick(n, key, least=12, side=3):
        got = []
        for h in sorted(houses, key=key):
            if len(got) >= n:
                break
            if id(h) not in taken and area(h) >= least and min(h[2] - h[0], h[3] - h[1]) - 1 >= side:
                taken.add(id(h))
                got.append(h)
        return got
    want = []
    halls = [k for k in GU.halls_in(game, s.id) if k != 'anglers']
    for k in halls:
        if GU.GUILDS[k]['secret']:                  # an ordinary house down a lane, far from the market
            for h in pick(1, lambda h: -dist(h, (mx, my)) - (40 if c.level.get(h[4], 0) == 2 else 0), 9):
                want.append(('home', h, k))
        else:
            for h in pick(1, lambda h: dist(h, (mx, my)) - area(h) * .8, 20):
                want.append(('keep', h, k))
    for i in range(5 if big else 3):
        g = gates[i % len(gates)]
        for h in pick(1, lambda h: dist(h, g), 20, 4):
            want.append(('inn', h, None))
    for h in pick(3 if big else 2, lambda h: dist(h, (mx, my)), 16):
        want.append(('shop', h, None))
    if not any(p.kind == 'temple' for p in out):
        for h in pick(1, lambda h: dist(h, (mx, my)) - area(h), 24):
            want.append(('temple', h, None))
    for h in pick(1, lambda h: dist(h, gates[0]), 16):
        want.append(('stables', h, None))
    for i in range(3 if big else 2):
        g = gates[(i + 1) % len(gates)]
        for h in pick(1, lambda h: dist(h, g), 16):
            want.append(('barracks', h, None))
    for h in houses:
        if id(h) not in taken:
            want.append(('home', h, None))
    for kind, h, guild in want:
        pl = plot(kind, *h)
        if guild:
            pl.guild = guild
        if kind != 'home' or guild:
            TW.furnish(m, pl)
        out.append(pl)
        if guild:
            if GU.GUILDS[guild]['sign']:            # the secret ones hang out no sign
                TW.add_sign(m, pl, GU.GUILDS[guild]['name'])
        elif kind in TW.SIGN:
            TW.add_sign(m, pl, TW.SIGN[kind])
    m.homes = [pl for pl in out if pl.kind == 'home' and pl.door]
    lived = [pl for pl in m.homes if not getattr(pl, 'guild', None)]       # people in about as many homes as before
    random.shuffle(lived)
    empty = {id(pl) for pl in lived[110 if big else 58:]}
    return [pl for pl in out if id(pl) not in empty]
