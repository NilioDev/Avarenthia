"""What spells leave on the map, and the dead the fights leave behind.

Each school has a rule that shows on the ground. Fire leaves burning ground (in a dry summer it can set the grass
of the plain alight); frost raises ice walls, freezes water to walk on and drifts snow; roots and brambles grow where
Nature calls them; Necromancy closes a foe in bone walls; the Hallowed Chapter's ground keeps the undead out; the
Green Moot's spirit totem heals those beside it; Ball Lightning rolls along on its own. Every one is a real tile,
named in the data, so the look legend and the Signs know it, and each melts, burns out or crumbles after a while:
the tile it covered comes back.

The fallen leave a corpse, the sign %, where they died (`m.slain`, the last twelve): Necromancy's stronger spells
use them up."""
import random

from . import data as D
from .worldgen import cheb, free_around

WATERS = {D.WATER, D.SHALLOW, D.RIVER}
WALLS = {D.ICEWALL, D.BONEWALL, D.SPIRITTOTEM}
SPELL_TILES = {D.BURNING, D.ICEWALL, D.SPELLICE, D.ROOTS, D.BRAMBLE, D.BONEWALL, D.HALLOWED, D.SPIRITTOTEM, D.BALL, D.DRIFT,
               D.SNARE, D.CALTROPS, D.RUNE, D.GATE, D.SMOKE}
TURNS = {D.BURNING: 6, D.ICEWALL: 18, D.SPELLICE: 30, D.ROOTS: 8, D.BRAMBLE: 14, D.BONEWALL: 6, D.HALLOWED: 20,
         D.SPIRITTOTEM: 20, D.BALL: 8, D.DRIFT: 12, D.SNARE: 60, D.CALTROPS: 14, D.RUNE: 80, D.GATE: 20, D.SMOKE: 6}
KEEP_OFF = set()                 # stairs, doors and bridges keep their own tile (filled at the bottom)


def fields(m):
    """{(x, y): [tile, turns left, the tile it covers, power]}"""
    return m.__dict__.setdefault('fields', {})


def place(game, m, x, y, tile, turns=None, power=0):
    """Lay a spell tile; True if it took. Walls need an empty cell, ice needs water, the rest open ground."""
    if not m.inb(x, y):
        return False
    f = fields(m)
    old = f.get((x, y))
    under = old[2] if old else m.tile(x, y)
    if under in KEEP_OFF or (old and old[0] in WALLS and tile not in WALLS):
        return False
    if tile == D.SPELLICE:
        if under not in WATERS:
            return False
    elif not D.TILES[under].walk or under in WATERS:
        return False
    if tile in WALLS and game.occupied(m, x, y):
        return False
    if tile in WALLS and any(it.x == x and it.y == y for it in m.items):
        return False
    m.set(x, y, tile)
    f[(x, y)] = [tile, TURNS.get(tile, 8) if turns is None else turns, under, power]
    return True


def clear(m, xy):
    f = fields(m)
    fd = f.pop(xy, None)
    if fd and m.tile(*xy) == fd[0]:
        m.set(xy[0], xy[1], fd[2])


def under(m, x, y):
    """The tile beneath a spell tile (or the tile itself)."""
    fd = fields(m).get((x, y)) if getattr(m, 'fields', None) else None
    return fd[2] if fd else m.tile(x, y)


def area(game, m, cells, tile, turns=None, power=0):
    return sum(1 for c in cells if place(game, m, c[0], c[1], tile, turns, power))


# ------------------------------------------------------------------ fire in the dry grass
def grass_fire(game, m, x, y):
    """Burning ground on a dry summer plain can set the grass alight: a fire on the world map, as the seasons make."""
    if getattr(m, 'zone', None) is None or under(m, x, y) != D.GRASS:
        return
    from . import seasons as SE
    st = SE.Now(game)
    om, w = game.maps['over'], game.world
    ox, oy = game.over_pos
    i = oy * om.w + ox
    if not st.fire_season or om.t[i] != D.GRASS or SE.biome(om, i) not in SE.GRASSLAND or SE.cold(om)[i] >= .4:
        return
    if i in getattr(w, 'fires', {}) or random.random() > .25:
        return
    w.fires = getattr(w, 'fires', {})
    w.fires[i] = 3
    game.msg('The dry grass catches. A fire runs off across the plain, faster than a man can walk.', 'bad')
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        if random.random() < .6:
            place(game, m, x + dx, y + dy, D.BURNING, 5, 2)


# ------------------------------------------------------------------ every turn
def tick(game):
    """One turn of the spell tiles on the map you are on: they work on whoever stands in them, and wear away."""
    m = game.map
    f = getattr(m, 'fields', None)
    p = game.player
    if f:
        for xy, fd in list(f.items()):
            tile, left, _u, power = fd
            if m.tile(*xy) != tile:                    # something else took the cell
                f.pop(xy, None)
                continue
            o = m.mon_at(*xy)
            if o is not None and not o.is_npc:
                on_tile(game, o, tile, power)
            if tile == D.BURNING and xy == (p.x, p.y) and not _walk_in_fire(game):
                game.msg('You stand in fire!', 'bad')
                game.hurt(max(2, power), 'burning ground', 'fire')
                if game.dead:
                    return
            elif tile == D.SPIRITTOTEM:
                totem(game, xy, power)
            elif tile == D.BALL:
                if roll_ball(game, xy, fd):
                    continue
            fd[1] = left - 1
            if fd[1] <= 0:
                clear(m, xy)
    tempest(game)


def _walk_in_fire(game):
    from . import trees as TT
    return TT.walk_in_fire(game)


def on_tile(game, o, tile, power):
    if tile == D.SMOKE:
        from . import arts as ART
        ART.on_tile(game, o, tile)
    elif tile == D.BURNING:
        if 'burn' not in o.effects and game.mon_res(o, 'fire') < 75:
            o.effects['burn'] = [3, max(2, power)]
    elif tile == D.ROOTS:
        if o.hold <= 0 and not o.tpl.get('fly') and random.random() < .7:
            o.hold = 1
        from . import trees as TT
        TT.thorns_on(game, o, tile)
    elif tile == D.BRAMBLE:
        if 'bleed' not in o.effects and o.tpl.get('family') not in ('undead', 'construct', 'ooze', 'plant'):
            o.effects['bleed'] = [3, max(1, power)]
        from . import trees as TT
        TT.thorns_on(game, o, tile)
    elif tile == D.DRIFT:
        o.effects['slow'] = [2, 0]
    elif tile == D.HALLOWED and undead(o):
        dmg = max(2, power)
        o.hp -= dmg
        game.num(o.x, o.y, str(dmg), (255, 240, 200))
        if o.hp <= 0:
            game.kill(o)


def undead(o):
    return not o.is_npc and (o.k in D.UNDEAD or o.tpl.get('family') == 'undead')


def after_move(game, mon, ox, oy):
    """The undead cannot set foot on hallowed ground: one that stepped onto it is thrown back. Snares, caltrops
    and runes do their work on who steps onto them (arts.py)."""
    m = game.map
    if (mon.x, mon.y) == (ox, oy) or not getattr(m, 'fields', None) or mon not in m.mons:
        return
    from . import arts as ART
    ART.mon_moved(game, mon)
    if mon not in m.mons:
        return
    if m.tile(mon.x, mon.y) == D.HALLOWED and m.tile(ox, oy) != D.HALLOWED and undead(mon):
        mon.x, mon.y = ox, oy


def totem(game, xy, power):
    """The spirit totem heals you and your company beside it."""
    from . import mercs as MC
    p = game.player
    if cheb(p.x, p.y, *xy) <= 1:
        s = game.stats()
        if p.life < s['max_life']:
            amt = min(s['max_life'] - p.life, power)
            p.life += amt
            game.num(p.x, p.y, f'+{amt}', (140, 230, 160))
    for mc in MC.party(game):
        b = mc.body
        if b is not None and cheb(b.x, b.y, *xy) <= 1:
            mx = MC.stats(game, mc)['max_hp']
            if mc.hp < mx:
                mc.hp = min(mx, mc.hp + power)
                MC.refresh_body(game, mc)


def roll_ball(game, xy, fd):
    """Ball Lightning rolls one step towards the nearest enemy it can find and strikes all beside it.
    Returns True when it moved (its record is already under the new cell)."""
    m = game.map
    foes = [o for o in game.visible_hostiles() if cheb(o.x, o.y, *xy) <= 8]
    lo, hi = fd[3] if isinstance(fd[3], tuple) else (4, 8)
    hit = [o for o in foes if cheb(o.x, o.y, *xy) <= 1]
    for o in hit:
        game.flash([(o.x, o.y)], (255, 251, 176), '~', .15)
        game.damage_mon(o, random.randint(lo, hi), col=(242, 240, 122), elem='lightning')
    fd[1] -= 1
    if fd[1] <= 0:
        clear(m, xy)
        return True
    if hit or not foes:
        return True
    t = min(foes, key=lambda o: cheb(o.x, o.y, *xy))
    sx, sy = (t.x > xy[0]) - (t.x < xy[0]), (t.y > xy[1]) - (t.y < xy[1])
    nx, ny = xy[0] + sx, xy[1] + sy
    if game.occupied(m, nx, ny) or (nx, ny) in fields(m):
        return True
    left, power = fd[1], fd[3]
    clear(m, xy)
    place(game, m, nx, ny, D.BALL, left, power)
    return True


def tempest(game):
    """While the Tempest lasts, lightning comes down on an enemy in sight every turn."""
    p = game.player
    b = next((b for b in p.buffs if b[0] == 'tempest'), None)
    if not b or game.map.kind in ('over', 'town'):
        return
    foes = [o for o in game.visible_hostiles() if cheb(o.x, o.y, p.x, p.y) <= 8]
    if not foes:
        return
    o = random.choice(foes)
    game.flash([(o.x, o.y - 1), (o.x, o.y)], (255, 255, 255), '~', .2)
    dmg = round(b[1] * (1.25 if wet(game, o) else 1))
    game.damage_mon(o, random.randint(max(1, dmg // 2), dmg), col=(242, 240, 122), elem='lightning')


# ------------------------------------------------------------------ the rules of the schools
GREEN = {'forest', 'deep_forest', 'dry_forest', 'jungle', 'taiga', 'birch', 'conifer', 'meadow', 'steppe', 'savanna',
         'floodplain', 'alpine', 'grass'}
BARE = {'desert', 'dune_crest', 'salt_edge', 'badlands', 'glacier', 'ice_shelf', 'pack_ice', 'berg', 'ashland',
        'bone_sand', 'mesa'}


def nature_factor(game):
    """Nature is a quarter stronger in forest and grass, a quarter weaker in desert, on ice and under the ground."""
    m = game.map
    from . import trees as TT
    floor = 1.0 if TT.has(game, 'druid') else .75   # a Druid is never weaker
    if m.kind == 'dungeon' or getattr(m, 'underground', False):
        return floor
    from .cooking import here_biome
    b = here_biome(game)
    return 1.25 if b in GREEN else floor if b in BARE else 1.0


def wet(game, o):
    """Water conducts: an enemy in water, or out in the rain, takes the arc harder."""
    m = game.map
    if under(m, o.x, o.y) in WATERS or m.tile(o.x, o.y) in (D.SWAMP, D.SPELLICE) or 'soaked' in getattr(o, 'effects', {}):
        return True
    from . import trees as TT
    if TT.has(game, 'winterstorm') and getattr(o, 'frozen', False) and getattr(o, 'hold', 0) > 0:
        return True                                 # a Winterstorm's ice carries the arc like water
    if m.kind == 'dungeon' or getattr(m, 'underground', False):
        return False
    from . import weather as WX
    return WX.current(game) in ('rain', 'downpour', 'storm', 'sleet')


def freeze_water(game, cells):
    """Frost on water makes ice to walk on, for a while."""
    m = game.map
    return area(game, m, [c for c in cells if under(m, *c) in WATERS], D.SPELLICE)


# ------------------------------------------------------------------ corpses
def corpses(game, r=7):
    """The corpses you can see within r tiles, nearest first: (kind, x, y, level)."""
    m, p = game.map, game.player
    out = [c for c in getattr(m, 'slain', []) if cheb(c[1], c[2], p.x, p.y) <= r and game.visible(c[1], c[2])]
    return sorted(out, key=lambda c: cheb(c[1], c[2], p.x, p.y))


def use_corpses(game, n, r=7):
    """Take n corpses near you; None (and nothing taken) if there are fewer."""
    cs = corpses(game, r)
    if len(cs) < n:
        return None
    for c in cs[:n]:
        game.map.slain.remove(c)
    from . import trees as TT
    TT.marrow(game, n)
    return cs[:n]


def corpse_at(m):
    """{(x, y): kind} of the corpses on this map, for drawing."""
    return {(c[1], c[2]): c[0] for c in getattr(m, 'slain', ())}


def corpse_name(k):
    return f"corpse of a {D.MONSTERS[k]['name'].lower()}" if k in D.MONSTERS else 'corpse'


# ------------------------------------------------------------------ you, under a spell
def guard(game, dmg, src_mon=None):
    """What your wards, the Ice Tomb and the Bond of Blood leave of a blow (after armour). Returns the damage."""
    p = game.player
    if not p.buffs:
        return dmg
    kinds = {b[0]: b for b in p.buffs}
    if 'tomb' in kinds:
        game.num(p.x, p.y, '0', (159, 216, 255))
        return 0
    if 'bond' in kinds and dmg > 1:
        from . import mercs as MC
        bst = next((mc for mc in MC.beasts(game) if mc.state == 'alive' and mc.body is not None
                    and mc.body in game.map.mons), None)
        if bst:
            share = round(dmg * kinds['bond'][1] / 100)
            if share:
                MC.hurt(game, bst, share)
                dmg -= share
    if 'unbroken' in kinds:
        s = game.stats()
        p.stamina = min(s['max_stamina'], p.stamina + kinds['unbroken'][1])
    w = kinds.get('ward')
    if w and dmg > 0:
        took = min(w[1], dmg)
        w[1] -= took
        dmg -= took
        if w[1] <= 0:
            p.buffs.remove(w)
            game.msg(f'Your {w[3]} breaks.', 'info')
        elif not dmg:
            game.num(p.x, p.y, '0', (200, 230, 255))
    return dmg


def martyr(game):
    """Martyr's Grace: a blow that would kill you leaves you standing on one life, once."""
    p = game.player
    b = next((b for b in p.buffs if b[0] == 'martyr'), None)
    if not b:
        return False
    p.buffs.remove(b)
    p.life = 1
    game.flash([(p.x, p.y)], (255, 240, 200), '+', .3)
    game.msg('A blow that should have killed you does not. Grace holds you up, this once.', 'gold')
    return True


def chill(game, mon):
    """Frost Armor: who strikes you in melee is slowed."""
    if any(b[0] == 'chill' for b in game.player.buffs) and mon in game.map.mons:
        mon.effects['slow'] = [3, 0]


KEEP_OFF.update((D.DOOR, D.ODOOR, D.DOWN, D.UP, D.BRIDGE))


SPELL_WORD = {D.BURNING: 'in burning ground', D.ROOTS: 'held by roots', D.BRAMBLE: 'in the brambles',
              D.DRIFT: 'wading in snow', D.HALLOWED: 'on hallowed ground', D.SPELLICE: 'on the ice'}


def under_spell(game, o):
    """For IN SIGHT: what spell tile an enemy stands in, in a few words, or None."""
    m = game.map
    if not getattr(m, 'fields', None):
        return None
    return SPELL_WORD.get(m.tile(o.x, o.y))
