"""The shape of the world, made the Dwarf Fortress way: one great continent and a scatter of islands in a
cold-to-hot sea, mountains in long chains, and four smooth fields (elevation, temperature, rainfall and
drainage) from which the biomes follow in broad natural belts. Water gathers and runs to the sea in real
river systems. On top of that the world gets its wonders: rare sights, one of each at most.

Only numpy is used, so the game needs nothing more than it already had."""
import heapq
import math

import numpy as np


# ------------------------------------------------------------------ small stand-ins for scipy.ndimage
class _ND:
    @staticmethod
    def label(mask):
        """4-connected components: (labels, count)."""
        h, w = mask.shape
        lab = np.zeros((h, w), np.int32)
        n = 0
        m = mask.tolist()
        L = lab.tolist()
        for y in range(h):
            for x in range(w):
                if m[y][x] and not L[y][x]:
                    n += 1
                    st = [(y, x)]
                    L[y][x] = n
                    while st:
                        cy, cx = st.pop()
                        for ny_, nx_ in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                            if 0 <= ny_ < h and 0 <= nx_ < w and m[ny_][nx_] and not L[ny_][nx_]:
                                L[ny_][nx_] = n
                                st.append((ny_, nx_))
        return np.array(L, np.int32), n

    @staticmethod
    def sum(mask, lab, index):
        cnt = np.bincount(lab.ravel(), weights=np.asarray(mask, float).ravel(), minlength=max(index, default=0) + 1)
        return np.array([cnt[i] for i in index])

    @staticmethod
    def distance_transform_edt(mask):
        """Distance from each True cell to the nearest False cell (8-way chamfer, close to Euclidean)."""
        d = np.where(mask, 1e9, 0.0)
        steps = [((0, 1), 1.0), ((0, -1), 1.0), ((1, 0), 1.0), ((-1, 0), 1.0),
                 ((1, 1), 1.4142), ((1, -1), 1.4142), ((-1, 1), 1.4142), ((-1, -1), 1.4142)]
        h, w = d.shape
        for _ in range(max(h, w)):
            prev = d
            for (dy, dx), c in steps:
                sh = np.full_like(d, 1e9)
                ys, ye = max(0, dy), h + min(0, dy)
                xs, xe = max(0, dx), w + min(0, dx)
                sh[ys:ye, xs:xe] = d[ys - dy:ye - dy, xs - dx:xe - dx]
                d = np.minimum(d, sh + c)
            if np.array_equal(d, prev):
                break
        return np.minimum(d, 1e6)

    @staticmethod
    def gaussian_filter(a, sigma):
        r = max(1, int(sigma * 3))
        k = np.exp(-(np.arange(-r, r + 1) ** 2) / (2 * sigma * sigma))
        k /= k.sum()
        p = np.pad(a, r, mode='reflect')
        p = np.apply_along_axis(lambda v: np.convolve(v, k, mode='same'), 1, p)
        p = np.apply_along_axis(lambda v: np.convolve(v, k, mode='same'), 0, p)
        return p[r:-r, r:-r]

    @staticmethod
    def map_coordinates(f, coords, order=1):
        sy, sx = coords
        h, w = f.shape
        x0 = np.clip(np.floor(sx).astype(int), 0, w - 1)
        y0 = np.clip(np.floor(sy).astype(int), 0, h - 1)
        x1, y1 = np.clip(x0 + 1, 0, w - 1), np.clip(y0 + 1, 0, h - 1)
        tx, ty = sx - x0, sy - y0
        a, b, c, d = f[y0, x0], f[y0, x1], f[y1, x0], f[y1, x1]
        return a * (1 - tx) * (1 - ty) + b * tx * (1 - ty) + c * (1 - tx) * ty + d * tx * ty


ndimage = _ND()


def rankdata(a):
    r = np.empty(len(a))
    r[np.argsort(a, kind='stable')] = np.arange(1, len(a) + 1)
    return r


def generate(SEED, W=320, H=180):
    """Returns a dict with the biome grid B (H x W of names) and the fields and extras the game keeps."""
    rng = np.random.default_rng(SEED)
    # ------------------------------------------------------------------ noise
    GY, GX = np.mgrid[0:H, 0:W].astype(float)

    def value_noise(scale):
        gw, gh = int(W / scale) + 3, int(H / scale) + 3
        g = rng.random((gh, gw))
        ys, xs = GY, GX
        fx, fy = xs / scale, ys / scale
        ix, iy = fx.astype(int), fy.astype(int)
        tx, ty = fx - ix, fy - iy
        sx, sy = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
        a, b, c, d = g[iy, ix], g[iy, ix + 1], g[iy + 1, ix], g[iy + 1, ix + 1]
        return a + (b - a) * sx + (c - a) * sy + (a - b - c + d) * sx * sy


    def fbm(base, octaves=5, gain=.5):
        out, amp, tot, s = np.zeros((H, W)), 1.0, 0.0, base
        for _ in range(octaves):
            out += value_noise(max(1.5, s)) * amp
            tot += amp
            amp *= gain
            s /= 2
        return out / tot


    def warp(field_fn, strength):
        """Domain warp: sample a field at coordinates pushed around by other noise, for ragged coasts."""
        wx, wy = fbm(40, 4) - .5, fbm(40, 4) - .5
        f = field_fn
        ys, xs = np.mgrid[0:H, 0:W].astype(float)
        sx = np.clip(xs + wx * strength, 0, W - 1)
        sy = np.clip(ys + wy * strength, 0, H - 1)
        return ndimage.map_coordinates(f, [sy, sx], order=1)


    ys, xs = np.mgrid[0:H, 0:W].astype(float)
    nx, ny = xs / W, ys / H

    # ------------------------------------------------------------------ the main continent
    # the sea always rings the world: land fades out towards the edges, and a continent that still
    # reaches the border is thrown away and drawn again
    edge = np.sqrt(((nx - .5) / .5) ** 2 + ((ny - .5) / .5) ** 2)       # round, so the coast never turns square
    MARGIN = 12
    for attempt in range(40):
        cx, cy = .5 + rng.uniform(-.05, .05), .5 + rng.uniform(-.04, .04)
        # an uneven blob: a few lobes so the coast gets bays, peninsulas and an inland sea
        lobes = np.zeros((H, W))
        for _ in range(7):
            lx, ly = cx + rng.uniform(-.27, .27), cy + rng.uniform(-.22, .22)
            rx, ry = rng.uniform(.18, .28), rng.uniform(.18, .27)
            lobes = np.maximum(lobes, 1 - np.sqrt(((nx - lx) / rx) ** 2 + ((ny - ly) / ry) ** 2))
        land = lobes * .7 + fbm(50, 6) * .85 - np.clip(edge - .58, 0, 1) * 1.6    # the falloff, before the warp
        land = warp(land, 40)
        # an inland sea cut into the continent
        sx_, sy_ = cx + rng.uniform(-.12, .12), cy + rng.uniform(-.1, .1)
        sea = 1 - np.sqrt(((nx - sx_) / .07) ** 2 + ((ny - sy_) / .06) ** 2)
        land -= np.clip(sea, 0, 1) * .9 * warp(fbm(20, 3), 10) * 1.6
        thr = np.quantile(land, .55)               # a good 40% of the world is the continent
        mask = land > thr
        lab, n = ndimage.label(mask)
        sizes = ndimage.sum(mask, lab, range(1, n + 1))
        main = lab == (np.argmax(sizes) + 1)
        yy_, xx_ = np.nonzero(main)
        if (xx_.min() >= MARGIN and xx_.max() < W - MARGIN and yy_.min() >= MARGIN * .7 and yy_.max() < H - MARGIN * .7
                and main.sum() > W * H * .33):
            break
    continent = main.copy()

    # ------------------------------------------------------------------ islands, out at sea
    dist_land = ndimage.distance_transform_edt(~main)
    islands = np.zeros((H, W), bool)
    island_cells = []
    tries = 0
    want = rng.integers(4, 7)
    while len(island_cells) < want and tries < 400:
        tries += 1
        ix_, iy_ = rng.uniform(.06, .94) * W, rng.uniform(.08, .92) * H
        if not 9 < dist_land[int(iy_), int(ix_)] < 34:
            continue
        r = rng.uniform(5, 13) if len(island_cells) else rng.uniform(11, 16)   # one bigger island
        if any(math.hypot(ix_ - a, iy_ - b) < r + rb + 8 for a, b, rb in island_cells):
            continue
        d = np.sqrt(((xs - ix_) / (r * 1.3)) ** 2 + ((ys - iy_) / r) ** 2)
        blob = (1 - d) + (warp(fbm(8, 4), 8) - .5) * 1.4
        lab_i, n_i = ndimage.label(blob > .3)
        if n_i:
            sz = ndimage.sum(blob > .3, lab_i, range(1, n_i + 1))
            islands |= lab_i == (np.argmax(sz) + 1)
        island_cells.append((ix_, iy_, r))
    # a scatter of islets near the coasts
    for _ in range(rng.integers(10, 18)):
        ix_, iy_ = rng.uniform(.03, .97) * W, rng.uniform(.04, .96) * H
        if 3 < dist_land[int(iy_), int(ix_)] < 9:
            d = np.sqrt((xs - ix_) ** 2 + (ys - iy_) ** 2) / rng.uniform(1.5, 3.2)
            islands |= (1 - d + (fbm(4, 2) - .5) * .6) > .3
    is_land = main | islands
    is_land[[0, -1], :] = False
    is_land[:, [0, -1]] = False

    # ------------------------------------------------------------------ elevation
    coast = ndimage.distance_transform_edt(is_land)
    inland = np.clip(coast / 18, 0, 1)
    # ridged noise makes mountain chains instead of round blobs
    ridge = 1 - np.abs(fbm(46, 5) * 2 - 1)
    ridge = ridge ** 3
    elev = .35 * fbm(30, 5) + .45 * ridge * (.4 + .6 * inland) + .25 * inland
    elev = np.where(is_land, elev, 0)
    land_e = elev[is_land]
    e_hills, e_mount, e_peak = np.quantile(land_e, [.74, .88, .965])

    # ------------------------------------------------------------------ climate, the Dwarf Fortress way
    # Four smooth fields decide the land, as in DF's world generation: elevation (above), temperature,
    # rainfall and drainage. Biomes follow from where they meet, so they spread in broad natural belts and
    # patches instead of noise blobs.
    lat = ny                                   # 0 north (cold) .. 1 south (hot)
    temp = lat * 1.0 + .05 + (fbm(60, 3) - .5) * .12 - np.clip(elev - e_hills, 0, 1) * 1.4 - np.clip(elev - .45, 0, 1) * .25

    # rainfall: wet winds blow in from the western sea; they pick up water over the ocean and lose it over land,
    # most of all where the land rises; behind a mountain range the land lies dry (the rain shadow)
    rain = np.zeros((H, W))
    vap = np.full(H, .6)
    for x in range(W):
        col_land = is_land[:, x]
        cap = .5 + .6 * np.clip(temp[:, x], 0, 1)                 # warm air holds more water
        vap = np.where(col_land, vap, vap + (cap - vap) * .25)
        up = np.clip(elev[:, x] - (elev[:, x - 1] if x else 0), 0, None) * 2.5
        fall = np.where(col_land, vap * (.018 + up), 0)
        rain[:, x] = fall
        vap = np.clip(vap - fall, 0, None)
        vap = (vap + np.roll(vap, 1) + np.roll(vap, -1)) / 3        # winds mix a little north and south
    rain = ndimage.gaussian_filter(rain, 2.2)
    # rank the land from driest to wettest (0..1), as DF spreads its rainfall over the whole range
    rk = np.zeros((H, W))
    rk[is_land] = rankdata(rain[is_land]) / is_land.sum()
    rain = rk * .72 + fbm(26, 4) * .28
    # the belts of the world: a dry band in the warm south before the steaming far south
    rain *= 1 - .55 * np.exp(-((lat - .76) / .07) ** 2)
    rain *= 1 + .5 * np.clip((lat - .88) / .1, 0, 1)
    rain += (fbm(28, 4) - .5) * .35 + (fbm(9, 3) - .5) * .12     # local variation, so belts break into patches
    rain = np.clip(rain, 0, 1.5)
    drain = fbm(22, 4)                                           # how fast water runs off: marsh where it does not
    moist = rain                                                 # (the name the wonders use)

    # ------------------------------------------------------------------ rivers: water that gathers and runs to the sea
    elev_r = elev + fbm(4, 3) * .03        # a little roughness, so rivers wander instead of running straight
    filled = elev_r.copy()
    seen_ = np.zeros((H, W), bool)
    pq = []
    for y in range(H):
        for x in range(W):
            if not is_land[y, x]:
                seen_[y, x] = True
                if any(0 <= y + dy < H and 0 <= x + dx < W and is_land[y + dy, x + dx] for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    heapq.heappush(pq, (0.0, y, x))
    order = []
    while pq:                                                    # priority flood: fill every hollow up to its spill point
        e, y, x = heapq.heappop(pq)
        order.append((y, x))
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            yy, xx = y + dy, x + dx
            if 0 <= yy < H and 0 <= xx < W and not seen_[yy, xx]:
                seen_[yy, xx] = True
                filled[yy, xx] = max(elev_r[yy, xx], e + 1e-5)
                heapq.heappush(pq, (filled[yy, xx], yy, xx))
    lake = is_land & (filled - elev_r > .02)
    # water flows from each cell to the neighbour it drains into; process from high to low, adding up the rain
    acc = np.where(is_land, .2 + rain, 0)
    down = {}
    for y, x in order:
        best = None
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            yy, xx = y + dy, x + dx
            if 0 <= yy < H and 0 <= xx < W and filled[yy, xx] < filled[y, x] and (best is None or filled[yy, xx] < filled[best]):
                best = (yy, xx)
        if best:
            down[(y, x)] = best
    for y, x in reversed(order):
        if is_land[y, x] and (y, x) in down:
            acc[down[(y, x)]] += acc[y, x]
    river = is_land & (acc > np.quantile(acc[is_land], .972)) & ~lake
    # small lakes only: big flooded basins become marsh instead
    lab_l, n_l = ndimage.label(lake)
    sz_l = ndimage.sum(lake, lab_l, range(1, n_l + 1))
    for i, sz in enumerate(sz_l):
        if sz < 3 or sz > 90:
            lake[lab_l == i + 1] = False

    # ------------------------------------------------------------------ biomes
    patch = fbm(9, 3)
    jit_t, jit_r = (fbm(6, 2) - .5) * .06, (fbm(5, 2) - .5) * .12      # fuzzy borders: biomes interleave
    ocean_depth = ndimage.distance_transform_edt(~is_land)
    volcano_isle = island_cells[0] if island_cells else None
    B = np.empty((H, W), dtype=object)
    for y in range(H):
        for x in range(W):
            if not is_land[y, x]:
                d = ocean_depth[y, x]
                B[y, x] = 'shallows' if d <= 2 else 'sea' if d <= 7 else 'ocean'
                continue
            e, t, r, dr = elev[y, x], temp[y, x] + jit_t[y, x], rain[y, x] + jit_r[y, x], drain[y, x]
            if volcano_isle and math.hypot(x - volcano_isle[0], y - volcano_isle[1]) < volcano_isle[2] * .9 and not continent[y, x]:
                dv = math.hypot(x - volcano_isle[0], y - volcano_isle[1]) / volcano_isle[2]
                B[y, x] = 'volcano' if dv < .18 else 'ashland' if dv < .55 else ('jungle' if t > .6 else 'forest')
                continue
            if lake[y, x]:
                B[y, x] = 'lake'
            elif e > e_peak:
                B[y, x] = 'peak'
            elif e > e_mount:
                B[y, x] = 'mountain'
            elif t < .06:
                B[y, x] = 'glacier'
            elif t < .15:
                B[y, x] = 'tundra_hills' if e > e_hills else 'tundra'
            elif e > e_hills:
                B[y, x] = 'hills' if r > .25 else 'badlands' if t > .6 else 'hills'
            elif r > .62 and dr < .38 and t > .25:
                B[y, x] = 'swamp' if t > .45 else 'marsh'
            elif t < .33:                                                    # the cold belt
                B[y, x] = 'taiga' if r > .3 else 'tundra' if r < .15 else 'shrubland_cold'
            elif t < .66:                                                    # the temperate belt
                if r > .68:
                    B[y, x] = 'deep_forest' if patch[y, x] > .55 else 'forest'
                elif r > .46:
                    B[y, x] = 'forest' if t > .46 or patch[y, x] < .55 else 'conifer'
                elif r > .3:
                    B[y, x] = 'meadow' if patch[y, x] > .3 else 'forest'
                elif r > .2:
                    B[y, x] = 'steppe' if t > .5 else 'meadow'
                else:
                    B[y, x] = 'shrubland'
            else:                                                            # the warm belt
                if r > .8:
                    B[y, x] = 'jungle'
                elif r > .55:
                    B[y, x] = 'dry_forest'
                elif r > .3:
                    B[y, x] = 'savanna'
                elif r > .16:
                    B[y, x] = 'shrubland'
                else:
                    B[y, x] = 'desert' if dr > .4 or e < e_hills * .8 else 'badlands'
            if coast[y, x] <= 1.2 and B[y, x] in ('meadow', 'steppe', 'savanna', 'shrubland', 'desert') and patch[y, x] > .5:
                B[y, x] = 'beach'
            if river[y, x] and B[y, x] not in ('peak', 'glacier'):
                B[y, x] = 'river'


    fbm_floe = fbm(3, 2)


    def h_rand(x, y, s=0):
        n = (int(x) * 374761393 + int(y) * 668265263 + (s + SEED * 31) * 2246822519) & 0xFFFFFFFF
        n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
        return ((n ^ (n >> 16)) & 0xFFFF) / 65536


    def scale_c(c, k):
        return tuple(max(0, min(255, int(v * k))) for v in c)


    # ------------------------------------------------------------------ the polar north: pack ice, an ice shelf, icebergs
    pol = fbm(14, 4)
    for y in range(H):
        for x in range(W):
            if is_land[y, x]:
                continue
            edge_ = .07 + pol[y, x] * .11
            if ny[y, x] < edge_ * .45:
                B[y, x] = 'ice_shelf'
            elif ny[y, x] < edge_:
                B[y, x] = 'pack_ice' if fbm_floe[y, x] > .42 else 'icy_water'
            elif ny[y, x] < edge_ + .12 and h_rand(x, y) < .012 * (1 - (ny[y, x] - edge_) / .12):
                B[y, x] = 'berg'

    # ------------------------------------------------------------------ wonders: rare sights, one of each at most
    WONDERS = []          # (name, x, y)
    OVER = {}             # (x, y) -> (glyph, fg, bg or None): things drawn on top (bones, a rock in the sky)
    SHADOW = set()        # cells in the shadow of something above
    noise_a, noise_b = fbm(5, 3), fbm(3, 2)


    def spot(allowed, r, sea=False, far=28, south=None, north=None, inside=.8, extra=None):
        """A random centre whose surroundings (radius r) are mostly of the allowed biomes."""
        cand = np.argwhere(np.isin(B, list(allowed)))
        rng.shuffle(cand)
        for y, x in cand[:4000]:
            if not (r + 2 <= x < W - r - 2 and r + 2 <= y < H - r - 2):
                continue
            if south is not None and y < H * south or north is not None and y > H * north:
                continue
            if any(math.hypot(x - a, y - b) < far for _n, a, b in WONDERS):
                continue
            win = B[y - r:y + r + 1, x - r:x + r + 1]
            if np.isin(win, list(allowed)).mean() > (.97 if sea else inside) and (extra is None or extra(int(x), int(y))):
                return int(x), int(y)
        return None


    def blob(c, r, sx=1.4, rough=.6):
        """An organic patch: {cell: strength 0..1}, 1 at the heart, fading to 0 at a ragged edge."""
        x0, y0 = c
        out = {}
        R = int(r * sx * (1 + rough)) + 2
        for y in range(max(0, y0 - int(r * (1 + rough)) - 2), min(H, y0 + int(r * (1 + rough)) + 3)):
            for x in range(max(0, x0 - R), min(W, x0 + R + 1)):
                d = math.hypot((x - x0) / sx, y - y0) / r
                d += (noise_a[y, x] - .5) * rough * 1.6 + (noise_b[y, x] - .5) * rough * .6
                if d < 1:
                    out[(x, y)] = 1 - d
        return out


    def chance(x, y, p, salt=0):
        return h_rand(x, y, salt) < p


    def setb(x, y, b, keep=('river', 'peak')):
        if 0 <= x < W and 0 <= y < H and B[y, x] not in keep:
            B[y, x] = b


    LAND_OK = {'meadow', 'steppe', 'forest', 'savanna', 'hills', 'taiga', 'tundra', 'desert', 'deep_forest', 'jungle',
               'swamp', 'badlands', 'beach'}

    # the volcano: lava runs from the crater down to the sea
    if volcano_isle:
        vx, vy = int(volcano_isle[0]), int(volcano_isle[1])
        WONDERS.append(('The Burning Isle', vx, vy))
        for k in range(rng.integers(2, 4)):
            a = rng.uniform(0, math.tau)
            x, y = float(vx), float(vy)
            for step in range(40):
                a += rng.normal(0, .35)
                x, y = x + math.cos(a), y + math.sin(a) * .7
                ix, iy = int(round(x)), int(round(y))
                if not (0 <= ix < W and 0 <= iy < H) or not is_land[iy, ix]:
                    break
                if B[iy, ix] != 'volcano':
                    B[iy, ix] = 'lava'
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        if 0 <= ix + dx < W and 0 <= iy + dy < H and is_land[iy + dy, ix + dx] and B[iy + dy, ix + dx] not in ('lava', 'volcano'):
                            if chance(ix + dx, iy + dy, .5, 3):
                                B[iy + dy, ix + dx] = 'ashland'

    # a crater lake: a meteor struck long ago (kept round on purpose: it was made in one blow)
    c = spot({'meadow', 'steppe', 'forest', 'savanna'}, 8)
    if c:
        for (x, y), s in blob(c, 8, 1.3, .12).items():
            setb(x, y, 'crater_rim' if s < .35 else 'crater_lake')
        B[c[1], c[0]] = 'crater_isle'
        WONDERS.append(('Starfall Crater', *c))

    # the elder tree: one enormous ancient tree in a ring of old forest
    c = spot({'forest', 'deep_forest'}, 5)
    if c:
        for (x, y), s in blob(c, 7, 1.4, .5).items():
            if chance(x, y, s * 1.6, 4):
                setb(x, y, 'deep_forest')
        for (x, y), s in blob(c, 1.6, 1.5, .1).items():
            setb(x, y, 'elder_tree')
        WONDERS.append(('The Elder Tree', *c))

    # the sundering: a canyon that wanders across the dry lands, with side gullies
    c = spot({'steppe', 'desert', 'savanna', 'badlands', 'meadow'}, 6, south=.45)
    if c:
        def carve(x, y, a, length, width):
            for i in range(length):
                a += (noise_a[int(y) % H, int(x) % W] - .5) * .5 + rng.normal(0, .08)
                x, y = x + math.cos(a), y + math.sin(a) * .75
                ix, iy = int(round(x)), int(round(y))
                if not (2 <= ix < W - 2 and 2 <= iy < H - 2) or not is_land[iy, ix]:
                    return
                wd = width * (.6 + noise_b[iy, ix]) * min(1, (length - i) / 8, (i + 3) / 6)
                for dy in range(-3, 4):
                    for dx in range(-3, 4):
                        d = math.hypot(dx, dy * 1.3)
                        if d <= wd and is_land[iy + dy, ix + dx] and B[iy + dy, ix + dx] != 'river':
                            if d <= wd - 1.1:
                                B[iy + dy, ix + dx] = 'chasm'
                            elif B[iy + dy, ix + dx] != 'chasm':
                                B[iy + dy, ix + dx] = 'chasm_edge'
                if width > 1.5 and chance(ix, iy, .05, 9):
                    carve(x, y, a + rng.choice([-1, 1]) * rng.uniform(.7, 1.3), int(rng.integers(6, 14)), 1.3)
        a0 = rng.uniform(0, math.pi)
        carve(c[0], c[1], a0, 40, 1.9)
        carve(c[0], c[1], a0 + math.pi, 36, 1.9)
        WONDERS.append(('The Sundering', *c))

    # salt flats: a dead white plain in a dry basin, crusted, with brine pools
    c = spot({'desert', 'steppe', 'savanna'}, 7, south=.55)
    if c:
        for (x, y), s in blob(c, 8, 1.9, .9).items():
            if is_land[y, x] and B[y, x] != 'river':
                if s > .12 or chance(x, y, s * 6, 5):
                    B[y, x] = 'brine' if s > .55 and noise_b[y, x] > .66 else 'salt'
                elif chance(x, y, .5, 6):
                    B[y, x] = 'salt_edge'
        WONDERS.append(('The White Waste', *c))

    # a dune sea: ridges of sand in the heart of the desert
    c = spot({'desert', 'savanna', 'steppe'}, 6, south=.6, inside=.7)
    if c:
        for (x, y), s in blob(c, 14, 2.0, .7).items():
            if B[y, x] in ('desert', 'savanna', 'steppe'):
                wave = math.sin(y * 1.2 + math.sin(x * .18) * 2.2 + noise_a[y, x] * 4)
                B[y, x] = 'dune_crest' if wave > .6 else 'dune'
        WONDERS.append(('The Sea of Sand', *c))

    # a geyser field in the cold north: vents scattered through the taiga, each with a crust of sinter
    c = spot({'tundra', 'taiga', 'tundra_hills', 'hills'}, 5, north=.45)
    if c:
        for k in range(rng.integers(6, 11)):
            gx = c[0] + int(rng.normal(0, 4.5))
            gy = c[1] + int(rng.normal(0, 2.5))
            for (x, y), s in blob((gx, gy), rng.uniform(1, 2.2), 1.4, .5).items():
                if is_land[y, x] and B[y, x] not in ('river', 'peak', 'mountain'):
                    B[y, x] = 'sinter' if s < .5 else 'hotpool'
            setb(gx, gy, 'geyser')
        WONDERS.append(('The Steaming Fields', *c))

    # crystals breaking out of the hillsides near the mountains, thickest at the heart
    c = spot({'hills', 'tundra_hills', 'mountain'}, 4, inside=.6)
    if c:
        for (x, y), s in blob(c, 7, 1.5, .8).items():
            if is_land[y, x] and B[y, x] in ('hills', 'tundra_hills', 'mountain', 'meadow', 'steppe', 'taiga', 'forest'):
                if chance(x, y, s * .9, 11):
                    B[y, x] = 'crystal'
                elif chance(x, y, s * 1.2, 12):
                    B[y, x] = 'crystal_ground'
        WONDERS.append(('The Glass Hills', *c))

    # the Sky-Seat: a shard of the fallen Varnish capital still hangs in the air far out at sea. Beneath it the
    # sea turns in a maelstrom where the rest of the city went down, ringed by drowned towers and by a coral
    # atoll that the currents have torn open on one side: a crescent of reef and islets, and a wreck on it.
    # It lies in the warm southern sea, so far out that no one on land, not even on a watchtower, can see it.
    def sky_spot(margin, south, sink=False):
        ax, ay = 26 + margin, 17 + margin                 # the atoll's reach, plus open water around it
        yy, xx = np.ogrid[-ay:ay + 1, -ax:ax + 1]
        kern = (xx / ax) ** 2 + (yy / ay) ** 2 <= 1
        pad = np.zeros((H + 2 * ay, W + 2 * ax), dtype=bool)
        pad[ay:ay + H, ax:ax + W] = continent if sink else is_land
        cand = np.argwhere(np.isin(B, ['ocean', 'sea']))
        cand = cand[(cand[:, 0] >= max(H * south, 16)) & (cand[:, 0] < H - 19) & (cand[:, 1] >= 32) & (cand[:, 1] < W - 32)]
        rng.shuffle(cand)
        for y, x in cand[:6000]:
            if any(math.hypot(x - a, y - b) < ax + 12 for _n, a, b in WONDERS):
                continue
            if not (pad[y:y + 2 * ay + 1, x:x + 2 * ax + 1] & kern).any():
                if sink:
                    # small islands too near it sank with the city: the sea there is open and empty
                    for j in range(-ay, ay + 1):
                        for i in range(-ax, ax + 1):
                            X, Y = x + i, y + j
                            if kern[j + ay, i + ax] and 0 <= X < W and 0 <= Y < H and is_land[Y, X]:
                                is_land[Y, X] = river[Y, X] = lake[Y, X] = False
                                B[Y, X] = 'ocean'
                return int(x), int(y)
        return None

    c = None
    for margin_, south_, sink_ in ((16, .62, 0), (13, .58, 0), (14, .6, 1), (10, .55, 1), (6, .5, 1), (2, .4, 1), (0, .2, 1)):
        c = sky_spot(margin_, south_, sink_)                # there is always a Sky-Seat
        if c:
            break
    if c:
        x0, y0 = c
        open_a = rng.uniform(0, math.tau)
        rx = 23.0                                           # the ring's radius across; cells are square, so ry = rx / 1.6
        for y in range(max(0, y0 - 18), min(H, y0 + 19)):
            for x in range(max(0, x0 - 30), min(W, x0 + 31)):
                if is_land[y, x]:
                    continue
                dx, dy = (x - x0) / 1.6, (y - y0)
                d = math.hypot(dx, dy)
                a = math.atan2(dy, dx)
                ring_r = rx / 1.6 * (1 + .12 * (noise_a[(int(math.sin(a) * 6) + 50) % H, (int(math.cos(a) * 6) + 50) % W] - .5) * 2)
                ring_r *= 1 + .05 * math.sin(a * 3 + open_a)
                t = d - ring_r
                torn = math.cos(a - open_a) > .35
                b = None
                if t < -2.2:
                    b = 'lagoon' if d > ring_r * .55 else 'lagoon_deep'
                elif t < -.8:
                    b = 'reef_flat'
                elif t < .9:
                    b = 'reef'
                elif t < 1.9:
                    b = 'surf'
                if torn and t > -7:
                    b = None if t > -3 else 'lagoon_deep'
                    if -2 < t < 2 and h_rand(x, y, 61) < .18:
                        b = 'reef'                        # a few broken coral heads remain in the current
                if b:
                    B[y, x] = b
        # passes through the reef, and the islets along it
        for k in range(2):
            a = open_a + math.pi + (k - .5) * 1.6
            for r in np.linspace(rx / 1.6 - 3.5, rx / 1.6 + 2.5, 14):
                x, y = int(x0 + math.cos(a) * r * 1.6), int(y0 + math.sin(a) * r)
                if 0 <= x < W and 0 <= y < H and not is_land[y, x]:
                    B[y, x] = 'ocean'
        for k in range(9):
            a = (k + .3 + h_rand(k, 1, 62) * .5) / 9 * math.tau + open_a
            if math.cos(a - open_a) > .3:
                continue
            ix, iy = x0 + math.cos(a) * rx, y0 + math.sin(a) * rx / 1.6
            size = 1.4 + h_rand(k, 2, 63) * 2.8
            for y in range(max(0, int(iy) - 5), min(H, int(iy) + 6)):
                for x in range(max(0, int(ix) - 8), min(W, int(ix) + 9)):
                    px_, py_ = x - ix, (y - iy) * 1.6
                    u = (-px_ * math.sin(a) + py_ * math.cos(a)) / 1.6
                    v = (px_ * math.cos(a) + py_ * math.sin(a)) / 1.6
                    q = (u / (size * 1.8)) ** 2 + (v / (size * .55)) ** 2
                    if q < 1 + (h_rand(x, y, k) - .5) * .5:
                        B[y, x] = 'atoll_palm' if size > 2 and q < .45 else 'cay'
        wa = open_a + .75                                   # the wreck, where the reef gives out
        wx, wy = int(x0 + math.cos(wa) * rx * .98), int(y0 + math.sin(wa) * rx / 1.6)
        for x, y, ch in ((wx, wy, '╤'), (wx + 1, wy, '═'), (wx + 2, wy, '╛'), (wx + 1, wy - 1, '│')):
            OVER[(x, y)] = (ch, (150, 110, 70), None)
        # the maelstrom
        for y in range(y0 - 9, y0 + 10):
            for x in range(x0 - 15, x0 + 16):
                d = math.hypot((x - x0) / 1.6, y - y0)
                if d <= 8.5 + (noise_b[y, x] - .5) * 2:
                    a = math.atan2(y - y0, (x - x0) / 1.6)
                    B[y, x] = 'whirl_a' if math.sin(a * 2 + d * 1.1) > 0 else 'whirl_b'
                    if d < 1.8:
                        B[y, x] = 'whirl_b'
        B[y0, x0] = 'whirl_eye'
        for k in range(9):                                  # drowned towers
            a = rng.uniform(0, math.tau)
            rr = rng.uniform(5, 9.5)
            tx, ty = int(x0 + math.cos(a) * rr * 1.6), int(y0 + math.sin(a) * rr)
            OVER[(tx, ty)] = (str(rng.choice(['Π', '┼', '│', '╥'])), (196, 156, 96), None)
        for (x, y), s_ in blob((x0, y0 + 1), 4.5, 1.8, .2).items():
            SHADOW.add((x, y))
        rows = ['    ║  Π   ║    ', '  ┼Π║╥ΠΠ╥Π║Π┼  ', ' ▀▀▀▀▀▀▀▀▀▀▀▀▀▀ ', '▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓',
                ' ▓▓▓▓▓▓▓▓▓▓▓▓▓▓ ', '  ▒▓▓▓▓▓▓▓▓▓▓▒  ', '    ▒▓▓▓▓▓▓▒    ', '     ▒▓▓▓▓▒     ', '       ▒░       ',
                '        ░       ']
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch == ' ':
                    continue
                xx, yy = x0 - len(row) // 2 + i, y0 - 13 + j
                if ch in '║Π┼╥':
                    OVER[(xx, yy)] = (ch, (150, 230, 240) if ch == '║' or i % 3 == 0 else (214, 168, 96), (20, 40, 70))
                elif ch == '▀':
                    OVER[(xx, yy)] = (ch, (200, 180, 140), (120, 104, 84))
                else:
                    OVER[(xx, yy)] = (ch, {'▓': (150, 140, 128), '▒': (116, 108, 100), '░': (90, 84, 80)}[ch], (50, 46, 46))
        for k in range(10):
            sx_, sy_ = x0 + int(rng.normal(0, 2)), y0 - int(rng.uniform(1, 4))
            if (sx_, sy_) not in OVER:
                OVER[(sx_, sy_)] = (str(rng.choice(['·', '°', ':'])), (200, 230, 250), None)
        WONDERS.append(('The Sky-Seat', x0, y0 - 10))
    # fringing reefs along the warm southern coasts
    for y in range(int(H * .7), H):
        for x in range(W):
            if B[y, x] == 'shallows' and noise_a[y, x] > .62 and chance(x, y, .6, 13):
                B[y, x] = 'reef'

    # a petrified forest: a wood turned to stone at the edge of the dry country, half of it still green
    c = spot({'steppe', 'badlands', 'savanna', 'meadow', 'forest'}, 5)
    if c:
        for (x, y), s in blob(c, 7, 1.5, .8).items():
            if is_land[y, x] and B[y, x] not in ('river',):
                if chance(x, y, s * 1.8, 14):
                    B[y, x] = 'petrified'
                elif chance(x, y, s, 15):
                    B[y, x] = 'stone_ground'
        WONDERS.append(('The Stone Wood', *c))

    # tar pits: black pools scattered through the grass, oozing at the edges
    c = spot({'savanna', 'steppe', 'swamp', 'meadow'}, 4)
    if c:
        for k in range(rng.integers(6, 10)):
            px, py = c[0] + int(rng.normal(0, 4)), c[1] + int(rng.normal(0, 2.2))
            for (x, y), s in blob((px, py), rng.uniform(1.6, 3.4), 1.6, .6).items():
                if is_land[y, x] and B[y, x] != 'river':
                    B[y, x] = 'tar' if s > .3 else 'tar_edge'
        WONDERS.append(('The Black Mire', *c))

    # a grove of glowing mushrooms, spreading from the heart of the marsh or old forest
    c = spot({'swamp', 'deep_forest', 'forest', 'jungle'}, 4)
    if c:
        for (x, y), s in blob(c, 6, 1.4, .9).items():
            if is_land[y, x] and B[y, x] != 'river' and chance(x, y, s * 1.7, 16):
                B[y, x] = 'shroom'
        WONDERS.append(('The Glimmering', *c))

    # fjords: narrow arms of the sea cut deep into the cold northern coast, between steep walls
    coast_n = [(int(x), int(y)) for y, x in np.argwhere((B == 'shallows')) if y < H * .38]
    rng.shuffle(coast_n)
    made = []
    for sx0, sy0 in coast_n:
        if len(made) >= 5:
            break
        if any(abs(sx0 - a) < 9 for a in made):
            continue
        # head inland: towards the land, i.e. south
        x, y, a = float(sx0), float(sy0), math.pi / 2 + rng.normal(0, .3)
        cells = []
        for i in range(int(rng.integers(10, 22))):
            a += rng.normal(0, .25)
            x, y = x + math.cos(a) * .8, y + math.sin(a) * .8
            ix, iy = int(round(x)), int(round(y))
            if not (2 <= ix < W - 2 and 2 <= iy < H - 2):
                break
            cells.append((ix, iy))
        if len(cells) < 8 or sum(is_land[y_, x_] for x_, y_ in cells) < 6:
            continue
        made.append(sx0)
        n_ = len(cells)
        for k, (ix, iy) in enumerate(cells):
            wd = 2 if k < n_ * .6 else 1                     # wide at the mouth, narrow at the head
            for dx in range(-wd - 1, wd + 1):
                nx_ = ix + dx
                if not (0 <= nx_ < W):
                    continue
                if -wd < dx < wd or (dx == 0):
                    B[iy, nx_] = 'fjord'
                elif is_land[iy, nx_] and B[iy, nx_] != 'fjord':
                    B[iy, nx_] = 'cliff'
            for dx in (-wd - 2, wd + 1):
                if 0 <= ix + dx < W and is_land[iy, ix + dx] and B[iy, ix + dx] not in ('fjord', 'cliff') and chance(ix + dx, iy, .6, 17):
                    B[iy, ix + dx] = 'mountain'
        # the head of the fjord ends in cliffs
        hx_, hy_ = cells[-1]
        for dx in (-1, 0, 1):
            if is_land[hy_ + 1, hx_ + dx]:
                B[hy_ + 1, hx_ + dx] = 'cliff'
    if made:
        WONDERS.append(('The Fjords', made[len(made) // 2], int(H * .2)))

    # the ashen scar: where the old evil first broke through; burnt land, dead trees, a glowing wound
    c = spot({'meadow', 'forest', 'steppe', 'hills', 'savanna'}, 7, inside=.7)
    if c:
        for (x, y), s in blob(c, 11, 1.6, .9).items():
            if is_land[y, x] and B[y, x] not in ('river', 'peak'):
                if s > .75:
                    B[y, x] = 'scar_core'
                elif s > .2 or chance(x, y, s * 5, 18):
                    B[y, x] = 'dead_trees' if B[y, x] in ('forest', 'deep_forest', 'taiga') or chance(x, y, .25, 19) else 'scorched'
        WONDERS.append(('The Ashen Scar', *c))

    # the bones of a wyrm, half buried in the sand: skull, a long spine with a ribcage like a row of
    # chevrons, and a tapering tail. Facing west.
    def no_river(x, y):
        return not river[y - 4:y + 5, x - 16:x + 16].any()


    DESERT = {'desert', 'dune', 'dune_crest'}
    c = spot(DESERT, 8, inside=.85, extra=no_river)
    if not c:
        # no desert big enough: the driest hot land in the south becomes one, and the bones lie in it
        cand = [(moist[y, x], x, y) for y, x in np.argwhere(is_land) if y > H * .62 and coast[y, x] > 6 and no_river(x, y)
                and 18 <= x < W - 18]
        if cand:
            _m, dx_, dy_ = min(cand)
            for (x, y), s_ in blob((int(dx_), int(dy_)), 11, 2.0, .7).items():
                if is_land[y, x] and B[y, x] not in ('river', 'peak', 'mountain'):
                    B[y, x] = 'desert'
            c = (int(dx_), int(dy_))
    if c:
        x0, y0 = c
        ivory, shade = (246, 238, 214), (196, 186, 160)
        sag = lambda i: 1 if i >= 9 else 0                  # the body bends a little behind the shoulders
        for i in range(26):
            x, y = x0 - 10 + i, y0 + sag(i)
            if i < 18:
                ch = 'o' if i % 3 == 0 else '='
            else:
                ch = '-' if i < 23 else '·'                 # the tail tapers off
            if noise_b[y, x] > .78 and 4 < i < 22:           # buried under a drift
                ch, col = '~', (214, 180, 110)
            else:
                col = ivory if i < 18 else shade
            OVER[(x, y)] = (ch, col, None)
            if 2 <= i <= 16 and i % 3 == 2:                   # ribs, sweeping back from the spine
                ln = 2 if i in (2, 14) else 3
                for k in range(1, ln + 1):
                    for side, g in ((-1, '/'), (1, '\\')):
                        rx, ry = x + k - 1, y + side * k
                        if noise_b[ry, rx] > .8 and k > 1:
                            continue
                        OVER[(rx, ry)] = (g[0], scale_c(ivory, 1 - k * .07), None)
        # the skull, horns and jaw
        hx, hy = x0 - 10, y0
        for dx, dy, ch in ((-1, 0, ')'), (-2, 0, 'Θ'), (-3, 0, '='), (-4, 0, '<'), (-2, -1, '^'), (-1, -1, '/'), (-3, 1, '¬')):
            OVER[(hx + dx, hy + dy)] = (ch, (255, 250, 232) if ch == 'Θ' else ivory, None)
        # a few stray bones blown loose
        for k in range(6):
            bx_, by_ = x0 + int(rng.normal(4, 8)), y0 + int(rng.normal(0, 4))
            if (bx_, by_) not in OVER and 0 <= by_ < H and 0 <= bx_ < W and is_land[by_, bx_]:
                OVER[(bx_, by_)] = (rng.choice(['¬', '-', '·']), shade, None)
        # the sand around the bones lies bare and pale
        for (x, y), s_ in blob((x0 + 2, y0), 9, 2.0, .4).items():
            if is_land[y, x] and B[y, x] not in ('river',) and chance(x, y, s_ * 2.5, 21):
                B[y, x] = 'bone_sand'
        WONDERS.append(("The Wyrm's Bones", x0, y0))

    return dict(B=B, is_land=is_land, continent=continent, river=river, lake=lake, elev=elev, rain=rain,
                temp=temp, over=OVER, shadow=SHADOW, wonders=WONDERS)
