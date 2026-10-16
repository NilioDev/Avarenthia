"""The shape of the land, made the way Azgaar's Fantasy Map Generator makes it: a template of steps (hills,
mountain ranges, troughs, pits, straits, a mask) raises a coarse heightmap, so each world gets land with a real
silhouette: gulfs, peninsulas, necks of land, an inner sea. terrain.py roughens it and takes the coast from it.
Heights 0..100, sea level 20."""
import math
from collections import deque

import numpy as np

N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
N8 = N4 + ((1, 1), (1, -1), (-1, 1), (-1, -1))


class HM:
    def __init__(self, rng, w=160, h=90):
        self.rng, self.w, self.h = rng, w, h
        self.a = np.zeros((h, w))
        self.blob = .975                            # how far a hill spreads (Azgaar's power, for this grid)
        self.line = .82

    def pt(self, xr, yr):
        r = self.rng
        return int(r.uniform(*xr) / 100 * self.w), int(r.uniform(*yr) / 100 * self.h)

    def cnt(self, c):
        lo, hi = c
        return int(self.rng.integers(lo, hi + 1))

    def hill(self, count, height, xr, yr, sign=1):
        """Blobs that spread out from a point and fall off with a little noise (a pit when sign is -1)."""
        r = self.rng
        for _ in range(self.cnt(count)):
            ch = np.zeros((self.h, self.w))
            for _t in range(50):
                x, y = self.pt(xr, yr)
                if sign < 0 or self.a[y, x] + height[1] < 90:
                    break
            ch[y, x] = r.uniform(*height)
            q = deque([(x, y)])
            while q:
                cx, cy = q.popleft()
                for dx, dy in N4:
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < self.w and 0 <= ny < self.h and not ch[ny, nx]:
                        v = ch[cy, cx] ** self.blob * r.uniform(.9, 1.1)
                        if v > 1:
                            ch[ny, nx] = v
                            q.append((nx, ny))
            self.a = np.clip(self.a + sign * ch, 0, 100)

    def pit(self, count, height, xr, yr):
        self.hill(count, height, xr, yr, -1)

    def range(self, count, height, xr, yr, sign=1, end=None):
        """A mountain chain (a trough when sign is -1): a wandering line between two far points, raised and
        spread out on both sides, with spurs running down from it."""
        r = self.rng
        for _ in range(self.cnt(count)):
            sx, sy = self.pt(xr, yr)
            for _t in range(50):
                ex, ey = self.pt(*(end or ((10, 90), (15, 85))))
                if self.w / 8 < math.hypot(ex - sx, ey - sy) < self.w / 2:
                    break
            path, seen = [(sx, sy)], {(sx, sy)}
            cx, cy = sx, sy
            while (cx, cy) != (ex, ey) and len(path) < self.w * 2:
                best = None
                for dx, dy in N8:
                    nx, ny = cx + dx, cy + dy
                    if not (0 <= nx < self.w and 0 <= ny < self.h) or (nx, ny) in seen:
                        continue
                    d = math.hypot(ex - nx, ey - ny) + (r.random() * 6 if r.random() < .3 else 0)
                    if best is None or d < best[0]:
                        best = (d, nx, ny)
                if not best:
                    break
                cx, cy = best[1], best[2]
                path.append((cx, cy))
                seen.add((cx, cy))
            h = r.uniform(*height)
            used = set(path)
            front = list(path)
            while front and h > 2:
                for x, y in front:
                    self.a[y, x] = np.clip(self.a[y, x] + sign * h * r.uniform(.85, 1.15), 0, 100)
                h = h ** self.line - 1
                nxt = []
                for x, y in front:
                    for dx, dy in N4:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.w and 0 <= ny < self.h and (nx, ny) not in used:
                            used.add((nx, ny))
                            nxt.append((nx, ny))
                front = nxt
            if sign > 0:                                    # spurs: every few cells a ridge runs downhill
                for i in range(0, len(path), 6):
                    x, y = path[i]
                    for _s in range(int(self.w / 10)):
                        lo = min(((x + dx, y + dy) for dx, dy in N8 if 0 <= x + dx < self.w and 0 <= y + dy < self.h),
                                 key=lambda c: self.a[c[1], c[0]])
                        self.a[lo[1], lo[0]] = (self.a[y, x] * 2 + self.a[lo[1], lo[0]]) / 3
                        x, y = lo
                        if self.a[y, x] < 20:
                            break

    def trough(self, count, height, xr, yr, end=None):
        self.range(count, height, xr, yr, -1, end)

    def strait(self, width, vertical=True):
        """A channel of sea across the land, wandering from one edge to the other."""
        r = self.rng
        if vertical:
            x, y, ex, ey = int(r.uniform(.3, .7) * self.w), 0, int(r.uniform(.3, .7) * self.w), self.h - 1
        else:
            x, y, ex, ey = 0, int(r.uniform(.25, .75) * self.h), self.w - 1, int(r.uniform(.25, .75) * self.h)
        step = 0
        while (x, y) != (ex, ey) and step < self.w * 3:
            step += 1
            for dy in range(-width, width + 1):
                for dx in range(-width, width + 1):
                    if 0 <= x + dx < self.w and 0 <= y + dy < self.h and dx * dx + dy * dy <= width * width:
                        self.a[y + dy, x + dx] *= .55
            sx = np.sign(ex - x) if r.random() < .5 or y == ey else 0
            sy = np.sign(ey - y) if sx == 0 or r.random() < .5 else 0
            if r.random() < .25:
                sx, sy = (int(r.integers(-1, 2)), sy) if vertical else (sx, int(r.integers(-1, 2)))
            x, y = int(np.clip(x + sx, 0, self.w - 1)), int(np.clip(y + sy, 0, self.h - 1))

    def add(self, v, land_only=False):
        m = self.a >= 20 if land_only else np.ones_like(self.a, bool)
        self.a[m] = np.clip(self.a[m] + v, 0, 100)

    def mult(self, v, land_only=True):
        m = self.a >= 20 if land_only else np.ones_like(self.a, bool)
        self.a[m] = 20 + (self.a[m] - 20) * v if land_only else self.a[m] * v

    def smooth(self, k=2):
        p = np.pad(self.a, 1, mode='edge')
        s = sum(p[1 + dy:1 + dy + self.h, 1 + dx:1 + dx + self.w] for dx, dy in N8 + ((0, 0),)) / 9
        self.a = (self.a * (k - 1) + s) / k

    def inner_sea(self, rx, ry):
        """Sink the heart of the land under a great inner sea (where the old capital went down)."""
        ys, xs = np.mgrid[0:self.h, 0:self.w]
        cx, cy = self.rng.uniform(45, 55) / 100 * self.w, self.rng.uniform(45, 55) / 100 * self.h
        r = np.sqrt(((xs - cx) / (rx / 100 * self.w)) ** 2 + ((ys - cy) / (ry / 100 * self.h)) ** 2)
        self.a *= np.clip((r - .75) / .5, 0, 1) ** 2 * .9 + .1 * (r > 1)
        self.sea = (cx / self.w, cy / self.h, rx / 100 * .7, ry / 100 * .7)

    def mask(self, power=4):
        """Push the land away from the edges of the world, so the sea rings it."""
        ys, xs = np.mgrid[0:self.h, 0:self.w]
        nx, ny = 2 * xs / self.w - 1, 2 * ys / self.h - 1
        d = (1 - nx * nx) * (1 - ny * ny)
        self.a = self.a * (d * power + 1) / (power + 1) if power > 0 else self.a * d


# templates: few islands, real continents (after Azgaar's, tuned for one 320 x 180 world)
TEMPLATES = {
    'continents': [   # two or three big landmasses side by side
        ('hill', (1, 1), (80, 85), (60, 80), (40, 60)), ('hill', (1, 1), (80, 85), (20, 30), (40, 60)),
        ('hill', (5, 6), (15, 30), (25, 75), (15, 85)), ('mult', .6),
        ('hill', (7, 9), (5, 10), (15, 85), (20, 80)),
        ('range', (1, 2), (30, 60), (5, 15), (25, 75)), ('range', (1, 2), (30, 60), (80, 95), (25, 75)),
        ('range', (0, 2), (30, 60), (80, 90), (20, 80)),
        ('strait', 2, True), ('smooth', 3),
        ('trough', (2, 3), (15, 20), (15, 85), (20, 80)), ('pit', (2, 3), (10, 20), (15, 85), (20, 80)),
        ('mask', 4)],
    'pangea': [       # one great sprawling land
        ('hill', (1, 2), (25, 40), (15, 50), (0, 10)), ('hill', (1, 2), (5, 40), (50, 85), (0, 10)),
        ('hill', (1, 2), (25, 40), (50, 85), (90, 100)), ('hill', (1, 2), (5, 40), (15, 50), (90, 100)),
        ('hill', (6, 8), (20, 40), (20, 80), (48, 52)), ('smooth', 2), ('mult', .7),
        ('trough', (3, 4), (25, 35), (5, 95), (10, 20)), ('trough', (3, 4), (25, 35), (5, 95), (80, 90)),
        ('range', (4, 6), (30, 40), (10, 90), (35, 65)), ('pit', (2, 3), (10, 20), (15, 85), (20, 80)),
        ('mask', 3)],
    'peninsula': [    # a land that runs out from one side in long arms
        ('range', (2, 3), (20, 35), (40, 50), (0, 15)), ('add', 5),
        ('hill', (1, 1), (90, 100), (10, 90), (0, 5)), ('add', 13),
        ('hill', (3, 4), (3, 5), (5, 95), (80, 100)), ('hill', (1, 2), (3, 5), (5, 95), (40, 60)),
        ('trough', (5, 6), (10, 25), (5, 95), (5, 95)), ('smooth', 3), ('mask', 3)],
    'isthmus': [      # two lands joined by a narrow neck
        ('hill', (3, 5), (12, 22), (5, 30), (5, 25)), ('hill', (3, 5), (12, 22), (15, 45), (20, 40)),
        ('hill', (2, 3), (10, 16), (40, 60), (40, 60)), ('hill', (3, 5), (12, 22), (55, 85), (60, 80)),
        ('hill', (3, 5), (12, 22), (70, 95), (75, 95)), ('smooth', 2),
        ('trough', (4, 8), (15, 30), (0, 30), (0, 20)), ('trough', (4, 8), (15, 30), (10, 50), (20, 40)),
        ('trough', (4, 8), (15, 30), (30, 70), (40, 60)), ('trough', (4, 8), (15, 30), (50, 90), (60, 80)),
        ('trough', (4, 8), (15, 30), (70, 100), (80, 100)), ('mask', 3)],
    'mediterranean': [  # land all round a great inner sea
        ('hill', (2, 3), (40, 60), (10, 40), (20, 80)), ('hill', (2, 3), (40, 60), (60, 90), (20, 80)),
        ('hill', (4, 6), (20, 35), (15, 85), (10, 90)), ('mult', .8),
        ('range', (2, 3), (30, 50), (10, 90), (5, 25)), ('range', (2, 3), (30, 50), (10, 90), (75, 95)),
        ('trough', (2, 3), (15, 25), (10, 90), (10, 90)), ('smooth', 2),
        ('inner_sea', 17, 26), ('mask', 3)],
    'old_world': [    # a broad land with gulfs bitten deep into it
        ('range', (3, 3), (70, 70), (15, 85), (20, 80)), ('hill', (2, 3), (50, 70), (15, 45), (20, 80)),
        ('hill', (2, 3), (50, 70), (65, 85), (20, 80)), ('mult', .8), ('mask', 2),
        ('trough', (6, 8), (20, 50), (15, 85), (20, 80)), ('range', (2, 3), (20, 40), (15, 85), (20, 80)),
        ('strait', 2, True), ('smooth', 3), ('add', -5), ('hill', (1, 2), (3, 10), (15, 85), (20, 80))],
}


def build(rng, template, w=160, h=90):
    """The heightmap for a template, and where its inner sea lies (x, y, rx, ry as fractions; None if none)."""
    hm = HM(rng, w, h)
    hm.sea = None
    for step in TEMPLATES[template]:
        op, args = step[0], step[1:]
        if op == 'strait':
            hm.strait(args[0], args[1])
        elif op == 'add':
            hm.add(args[0])
        elif op == 'mult':
            hm.mult(args[0])
        elif op == 'smooth':
            hm.smooth(args[0])
        elif op == 'mask':
            hm.mask(args[0])
        elif op == 'inner_sea':
            hm.inner_sea(*args)
        else:
            getattr(hm, op)(*args)
    return hm.a, hm.sea
