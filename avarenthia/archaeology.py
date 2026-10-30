"""Archaeology (round 21): a life skill of the old places. Dig spots lie under the turf of the old places and the
Varnish ruins; you see one only once you have the eye for it, and the higher your rank, the more you see and the less
you break. Each place has the height of its land, and a spot far below you teaches nothing: you learn only at places
of your own height.
What a spot gives: lore (a piece of a Varnish riddle, or what the history tells of a battle or a village), now and then
the weakness of one of the Hollow King's servants, an old piece that a smith mends into gear with an old power (a
Varnish piece wants a shard of star-iron as well), a shard of star-iron, and old coins and finds that a city library
buys for more than a trader. Which spots are dug lives on the site; the rank on the player."""
import random

from . import data as D
from . import lifeskills as LS

KINDS = {'oldfield': 5, 'deserted': 4, 'oldbridge': 3, 'quarry': 3, 'fallenking': 2, 'wreck': 2, 'gallows': 1,
         'namestone': 1, 'vcity': 8, 'walltower': 3, 'windtower': 3, 'deadroad': 3, 'forge': 3, 'gate': 3, 'sluice': 3,
         'fallensky': 3, 'starhouse': 3, 'harbour': 3}
VARNISH = {'vcity', 'walltower', 'windtower', 'deadroad', 'forge', 'gate', 'sluice', 'fallensky', 'starhouse', 'harbour'}
GROUND = {D.GRASS, D.FLOOR, D.SAND, D.RUBBLE, D.PATH, D.VPAVE, D.DUST, D.GLASSSAND, D.FIELD}
# the finds to sell, by tier: (curio, name, worth in silver, look)
FINDS = {'sherd': ('A painted potsherd', 1, (196, 120, 80), 'A piece of a painted pot. Someone ate from it, long ago.'),
         'seal': ('An old seal', 8, (200, 170, 110), 'A signet of bronze, cut with a sign nobody uses now.'),
         'figurine': ('A small figure', 15, (176, 196, 160), 'A little figure of green stone: a god, or a child\'s toy.'),
         'torc': ('A gold torc', 30, (240, 200, 90), 'A neck ring of twisted gold, bent by the weight of the earth.')}
BY_TIER = {'A': ('sherd', 'oldcoin'), 'B': ('oldcoin', 'seal'), 'C': ('seal', 'figurine'), 'D': ('figurine', 'torc'),
           'E': ('torc', 'figurine')}
SELL = set(FINDS) | {'oldcoin'}
COLLECTOR = 1.5           # a library pays half again what a trader pays
PIECES = {'old': ('shortsword', 'waraxe', 'spear', 'mace', 'skullcap', 'ringmail', 'buckler'),
          'varnish': ('longsword', 'spear', 'mace', 'chainmail', 'fullhelm', 'roundshield', 'gauntlets')}
LOOK = ('÷', (214, 176, 110))


def tier_at(d):
    """The tier of a place, from the danger of its land."""
    return max((t for t in LS.TIERS if LS.TIER_DANGER[t] <= d), key=LS.TIERS.index)


def tier_of(need):
    return max((t for t in LS.TIERS if LS.TIER_RANK[t] <= need), key=LS.TIERS.index)


def has_tool(game):
    inv = game.player.inv
    return 'trowel' if any(i.k == 'tool' and i.t == 'trowel' for i in inv) else \
        'pick' if any(i.k == 'tool' and i.t == 'pick' for i in inv) else None


def sight(game):
    """How far above your rank you still see a spot."""
    r = LS.rank(game, 'archaeology')
    return 99 if r >= 50 else 3 + (3 if r >= 8 else 0)


# ------------------------------------------------------------------ the spots
def spots(game, site, m):
    """Where the spots of this place lie, and how hard each is: the same every time the map is made."""
    if getattr(m, 'digs', None) is not None:
        return m.digs
    m.digs, m.dig_under = {}, {}
    n = KINDS.get(site.kind, 0)
    if not n:
        return m.digs
    rnd = random.Random(game.seed * 3301 + site.x * 131 + site.y * 17 + 5)
    base = LS.TIER_RANK[tier_at(game.world.danger_at(site.x, site.y))] + (5 if site.kind in VARNISH else 0)
    dug = getattr(site, 'dug', set())
    cells = [(x, y) for y in range(2, m.h - 2) for x in range(2, m.w - 2) if m.tile(x, y) in GROUND and
             all(D.TILES[m.tile(x + dx, y + dy)].walk for dx in (-1, 0, 1) for dy in (-1, 0, 1))
             and abs(x - m.entry[0]) + abs(y - m.entry[1]) > 4]
    rnd.shuffle(cells)
    chosen = {}
    for x, y in cells:
        if len(chosen) >= n:
            break
        if any(abs(x - a) + abs(y - b) < 5 for a, b in chosen):
            continue
        chosen[(x, y)] = min(50, base + rnd.randint(0, 9))
    m.digs.update({k: v for k, v in chosen.items() if k not in dug})
    return m.digs


def on_enter(game, site, m):
    if site.kind in KINDS:
        spots(game, site, m)
        show(game)


def on_step(game):
    if getattr(game.map, 'digs', None):
        show(game)


def show(game):
    """The spots you have the eye for come up out of the turf."""
    m = game.map
    r = LS.rank(game, 'archaeology')
    if not has_tool(game) and not r:
        return
    see = r + sight(game)
    new = 0
    for (x, y), need in m.digs.items():
        if need <= see and m.tile(x, y) != D.DIGSPOT:
            m.dig_under[(x, y)] = m.tile(x, y)
            m.set(x, y, D.DIGSPOT)
            new += 1
    if new and not getattr(m, 'dig_said', False):
        m.dig_said = True
        game.msg('The turf lies wrong here and there: something was buried, long ago.' if new > 1 else
                 'The turf lies wrong in one place: something was buried, long ago.', 'info')


# ------------------------------------------------------------------ digging
def dig(game, x, y):
    """Walking into a dig spot."""
    m, p = game.map, game.player
    tool = has_tool(game)
    if not tool:
        game.msg('You need a trowel, or at least a pick, to dig here without ruining what lies below.', 'info')
        return 0
    site = game.world.sites[m.site]
    need = m.digs.pop((x, y), 0)
    m.set(x, y, m.dig_under.pop((x, y), D.GRASS))
    site.__dict__.setdefault('dug', set()).add((x, y))
    r = LS.rank(game, 'archaeology')
    game.end_turn(5 if r >= 30 else 10)
    p.food = max(0, p.food - 1)
    brk = .35 + .05 * (need - r) - (.05 if r >= 3 else 0) + (.15 if tool == 'pick' else 0)
    if r >= 25:
        brk *= .5
    brk = max(.05, min(.9, brk))
    xp = 6 + need * .6
    from . import debug as DBG
    if random.random() < brk and not DBG.has(game, 'oldfind'):
        game.msg('You dig carefully, but not carefully enough: what lay here crumbles in your hands.' if tool == 'trowel'
                 else 'The pick is too coarse: what lay here breaks under it.', 'bad')
        LS.gain(game, 'archaeology', xp * .5, at=need)
        return 0
    LS.gain(game, 'archaeology', xp, at=need, what=site.kind)
    find(game, site, need, r)
    return 0


def find(game, site, need, r):
    var = site.kind in VARNISH
    t = tier_of(need)
    roll = random.random()
    lore = (.22 if var else .15 if site.kind in ('oldfield', 'deserted') else 0) * (1.5 if r >= 40 else 1)
    if roll < lore and lore_find(game, site):
        return
    roll -= lore
    if r >= 20 and (var or site.kind == 'oldfield') and roll < .08 and clue(game, site):
        return
    roll -= .08
    piece = .18 + (.07 if r >= 15 else 0)
    if roll < piece:
        it = make_piece(game, var, need)
        if it and game.add_to_inv(it):
            game.msg(f'Under the earth, black and crusted: {display(game, it)}. A smith could mend it.', 'gold')
            return
    roll -= piece
    if var and roll < .12:
        from .nature import curio
        if game.add_to_inv(curio(game, 'stariron')):
            game.msg('A shard of star-iron, still bright under the earth after all these years.', 'good')
            return
    from .nature import curio
    k = random.choice(BY_TIER[t])
    it = curio(game, k)
    if game.add_to_inv(it):
        game.msg(f'You brush the earth off it: {it.name[0].lower() + it.name[1:]}.', 'good')


def lore_find(game, site):
    """A piece of what the place knows: a riddle at the Varnish, the battle or the village elsewhere."""
    if site.kind in VARNISH:
        from . import varnish as VN
        V, s = VN.info(game), VN.st(game)
        ok = ('library', f'place:{site.kind}') + (('stone',) if game.__dict__.get('varnish_letters') else ())
        pool = [k for k, v in V.get('src', {}).items() if v in ok and k not in s['frags']]
        if not pool:
            return False
        game.msg('In the earth lies a tablet of the Varnish, its words still clear.', 'gold')
        rk, i = random.choice(pool)
        return VN.riddle_frag(game, rk, i, 'what you dug up', site.name)
    from . import oldplaces as OP
    from . import history as HI
    from . import chronicle as CH
    e = OP.event_of(game, site)
    if not e:
        return False
    what = 'a buckle with a crown on it, and a broken standard pole' if site.kind == 'oldfield' else \
        'the iron of a door, and a pot with the dinner still burnt in it'
    game.msg(f'You dig up {what}. Now you know what happened here.', 'gold')
    HI.learn(game, e, 'seen', where=site.name)
    CH.add(game, 'Places', f'{site.name}: you dug up {what}. It was {e["title"].replace("The ", "the ")}, '
           f'{e["year"]} AR.', 'seen', where=site.name, place=(site.x, site.y), key=f'dig:{site.id}', quiet=True)
    return True


def clue(game, site):
    """The earth knows the servants too: an old warning, buried with the ones who learnt it."""
    from . import shadow as SH
    pool = [e for e in game.world.evils if e.known and not e.defeated
            and 'dig' not in SH.know(game)['src'].get(e.key, ())]
    if not pool:
        return False
    e = random.choice(pool)
    game.msg('Among the bones lies a lead plate, scratched with a warning for whoever comes after.', 'gold')
    return SH.clue(game, e, 'dig', site.name)


# ------------------------------------------------------------------ old pieces
def make_piece(game, var, need):
    from .entities import Item, base_for
    fams = [f for f in PIECES['varnish' if var else 'old'] if D.grades(f)]
    if not fams:
        return None
    lvl = max(1, game.map.level + 2 + need // 10)
    it = Item(game.new_id(), 'oldpiece', random.choice(fams))
    it.base = base_for(it.t, lvl)
    it.lvl, it.tier, it.varn = lvl, tier_of(need), var
    return it


def need_smith(it):
    return max(5, LS.TIER_RANK[it.tier])


def display(game, it):
    name = D.BASES[it.base]['name'].lower()
    return f'a corroded star-iron {name}' if it.varn else f'a rusted old {name}'


def lines(game, it):
    out = [f'Old work, of tier {it.tier}. A smith of rank {need_smith(it)} can mend it at an anvil, and an old power '
           'comes back with it.']
    if it.varn:
        out.append('It is Varnish work: the mending wants a shard of star-iron too.')
    return out


def value(game, it):
    return {'A': 2, 'B': 4, 'C': 7, 'D': 11, 'E': 16}[it.tier] * (2 if it.varn else 1)


def glyph(it):
    return '¬'


def color(it):
    return (150, 170, 220) if it.varn else (170, 120, 80)


def use(game, it):
    game.msg(f'{display(game, it)[0].upper() + display(game, it)[1:]}: ' + ' '.join(lines(game, it)), 'info')
    return 0


def mend_opts(game):
    """At the anvil: the old pieces in your pack."""
    r = LS.rank(game, 'smithing')
    star = any(i.k == 'curio' and i.t == 'stariron' for i in game.player.inv)
    out = []
    for it in [i for i in game.player.inv if i.k == 'oldpiece'][:8]:
        ok = r >= need_smith(it) and (star or not it.varn)
        why = '' if ok else f' (Smithing {need_smith(it)})' if r < need_smith(it) else ' (a shard of star-iron)'
        out.append((f'Mend {display(game, it)}{why}', f'oldmend:{it.id}' if ok else None))
    return out


def mend(game, iid):
    from . import crafts as CRF
    from .entities import make_gear
    p = game.player
    it = next((i for i in p.inv if i.id == iid and i.k == 'oldpiece'), None)
    if not it or not CRF.pay(game, CRF.ANVIL_FEE):
        return
    if it.varn:
        shard = next((i for i in p.inv if i.k == 'curio' and i.t == 'stariron'), None)
        if not shard:
            return
        game.remove_one(shard) if shard.stackable else p.inv.remove(shard)
    p.inv.remove(it)
    game.end_turn(60)
    g = make_gear(game, it.base, 'magic', it.lvl)
    base = D.BASES[g.base]['name']
    g.name = f'Varnish {base}' if it.varn else f'{base} of the Old Days'
    g.old = True
    game.add_to_inv(g)
    LS.gain(game, 'smithing', 10 + LS.TIER_RANK[it.tier], at=need_smith(it), what='oldpiece')
    game.msg(f'Hours of fire and file, and the old work comes back: {g.display_name()}.', 'gold')


# ------------------------------------------------------------------ the library buys finds
def finds(game):
    return [i for i in game.player.inv if i.k == 'curio' and i.t in SELL]


def worth(game):
    return sum(round(i.value() * COLLECTOR) * (i.n if i.stackable else 1) for i in finds(game))


def scribe_opts(game):
    if not finds(game):
        return []
    from .money import fmt
    return [(f'Show the scribe your old finds ({fmt(worth(game))})', 'finds')]


def r_scribe(game, npc, choice):
    if choice != 'finds':
        return False
    from .money import fmt
    got = worth(game)
    for it in finds(game):
        game.player.inv.remove(it)
    game.player.gold += got
    game.say(npc, f'"Where did you dig these up?" The scribe writes it all down, every one, and counts out {fmt(got)}.')
    return True


def register():
    from . import entities as EN
    from .nature import CURIO
    from . import shadow as SH
    EN.CRAFT['oldpiece'] = 'archaeology'
    CURIO.update(FINDS)
    SH.SOURCES['dig'] = 'what you dug up'


register()
