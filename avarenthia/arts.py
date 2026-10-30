"""The two classes that are not a school of magic or Warcraft (see "Classes, trees and the bar" in docs/plan.md):
Cunning (the Thieves' Guild's art: stealth, poison and traps; stamina) and Arcane (the Circle of Magi's: runes,
space and time; mana, the lowest damage of all, and it can take away what a spell left on the ground).

Cunning's rule: the first blow on one who does not see you coming lands twice (`first_blow`). Arcane's rule: Dispel
takes a spell's tile off the ground, or the magic off a foe. The tiles these arts lay (snares, caltrops, runes, gates,
smoke) are spell tiles (spellmap.py) and do their work when a foe steps on them (`mon_moved`)."""
import random

from . import data as D
from . import skills as SK
from .worldgen import cheb, free_around

SNEAK_COL, ARC = (150, 150, 170), (190, 150, 255)
MAGIC_MODS = ('Fast', 'Fire Enchanted', 'Vampiric', 'Frost-touched', 'Regenerating', 'Multishot', 'Fire-blooded')
RUNES = SK.RUNES_AT_ONCE           # runes you may have lying at once
STEALTH_NOTICE = .15            # a foe's chance each turn to notice you while you sneak (else .65)


def _tt():
    from . import trees as TT
    return TT


def classes(game):
    return getattr(game.player, 'classes', [])


def buff(game, k):
    return next((b for b in game.player.buffs if b[0] == k), None)


def drop_buff(game, k):
    game.player.buffs = [b for b in game.player.buffs if b[0] != k]


# ------------------------------------------------------------------ Cunning: the first blow, and not being seen
def unaware(game, mon):
    """Whether this foe does not see you coming: asleep or unaware, blinded, or (a Shade) cursed."""
    if mon.is_npc:
        return False
    TT = _tt()
    return (not mon.awake or 'blind' in mon.effects or buff(game, 'ambush') is not None
            or (TT.has(game, 'shade') and any(c in mon.effects for c in TT.CURSES)))


def first_blow(game, mon):
    """Cunning's rule: the first blow on one who does not see you coming lands twice (three times for a pure
    Rogue). Returns the multiplier, and spends the ambush."""
    p = game.player
    from . import epics as EP
    dance = EP.shadow_dance(game) and not mon.is_npc       # Shadow Dance: every blow is a first one
    if 'cunning' not in classes(game) or not dance and (not unaware(game, mon) or getattr(mon, 'ambushed', False)):
        return 1
    TT = _tt()
    mult = (3 if TT.has(game, 'rogue') else 2) * (1 + TT.total(game, 'ambush') / 100)
    mon.ambushed = True
    p.ambush_turn = game.turn
    drop_buff(game, 'ambush')
    game.num(mon.x, mon.y, 'unseen', (200, 190, 230))
    if TT.has(game, 'pickpocket') and not mon.is_npc and random.random() < .3:
        c = random.randint(1, 4) * max(1, mon.lvl)
        p.gold += c
        from .money import fmt
        game.msg(f'Your other hand finds {fmt(c)} on {mon.the()}.', 'gold')
    return mult


def broke_cover(game):
    """Striking, casting or running ends Sneak."""
    if buff(game, 'sneak'):
        drop_buff(game, 'sneak')
        game.msg('You come out of hiding.')


def notice(game, mon):
    """A foe's chance each turn to notice you, when it can see you."""
    from . import epics as EP
    ec = EP.notice(game, mon)                        # the Eclipse: it sees only the tile beside it
    if ec is not None:
        return ec
    calm = .5 if buff(game, 'calm') and 'wild' in mon.tpl.get('tags', '') else 1     # a draught of Calm: beasts notice you later
    if not buff(game, 'sneak'):
        return .65 * calm
    TT = _tt()
    near = cheb(mon.x, mon.y, game.player.x, game.player.y) <= 1
    return (.45 if near else STEALTH_NOTICE) * max(.2, 1 - TT.total(game, 'sneak') / 100) * calm


def lose_you(game, mons):
    for o in mons:
        o.awake = False
        o.ambushed = False
        o.ambushed_by = game.turn


def x_vanish(game, sk, r):
    p = game.player
    seen = game.visible_hostiles()
    lose_you(game, seen)
    p.buffs = [b for b in p.buffs if b[0] not in ('ambush', 'sneak')] + [['ambush', 1, 8, sk.name], ['sneak', 1, 30, 'Sneak']]
    game.fx('burst', x=p.x, y=p.y, r=1, col=sk.color, signs='░∙')
    game.msg('You are simply not there any more.' if seen else 'You melt into the shadows.', 'good')
    return True


def x_shadowstep(game, sk, r):
    p, m = game.player, game.map
    t = game.nearest_target(sk.range, False)
    if not t:
        game.miss_target('No foe close enough to step behind.')
        return False
    spots = [c for c in free_around(game, m, t.x, t.y, 1) if c != (t.x, t.y) and not game.occupied(m, *c)
             and cheb(c[0], c[1], t.x, t.y) == 1]
    if not spots:
        game.msg('There is no room behind it.')
        return False
    x, y = max(spots, key=lambda c: cheb(c[0], c[1], p.x, p.y))
    game.fx('trail', cells=game.cells_between((p.x, p.y), (x, y)), col=sk.color, ch='░')
    p.x, p.y = x, y
    p.last_target = t.id
    p.buffs = [b for b in p.buffs if b[0] != 'ambush' and b[3] != sk.name] + \
        [['ambush', 1, 5, sk.name], ['def', SK.STEP_DEF, SK.STEP_TURNS, sk.name]]
    game.compute_fov()
    game.msg(f'You step out of the shadows behind {t.the()}.', 'good')
    return True


def x_smoke(game, sk, r):
    from . import spellmap as SM
    p, m = game.player, game.map
    cells = [(p.x + dx, p.y + dy) for dx in range(-sk.radius, sk.radius + 1) for dy in range(-sk.radius, sk.radius + 1)]
    SM.area(game, m, cells, D.SMOKE, 6)
    near = [o for o in game.visible_hostiles() if cheb(o.x, o.y, p.x, p.y) <= sk.radius + 1]
    lose_you(game, near)
    game.fx('burst', x=p.x, y=p.y, r=sk.radius, col=sk.color, signs='▒░')
    game.compute_fov()
    game.msg('Grey smoke billows up round you. They have lost you in it.' if near else 'Grey smoke billows up round you.',
             'good')
    return True


def _toward_foe(game):
    """The tile beside you towards the nearest foe (or any free one)."""
    p, m = game.player, game.map
    t = game.nearest_target(8, False)
    free = [c for c in free_around(game, m, p.x, p.y, 1) if c != (p.x, p.y) and not game.occupied(m, *c)]
    if not free:
        return None
    if t:
        return min(free, key=lambda c: cheb(c[0], c[1], t.x, t.y))
    return random.choice(free)


def x_snare(game, sk, r):
    from . import spellmap as SM
    TT = _tt()
    m = game.map
    n = 2 if TT.has(game, 'two_snares') else 1
    laid = 0
    for _ in range(n):
        c = _toward_foe(game)
        if c and SM.place(game, m, c[0], c[1], D.SNARE, 60, 3 + TT.total(game, 'snare')):
            laid += 1
            game.flash([c], sk.color, '^', .2)
    if not laid:
        game.msg('There is no room to lay a snare.')
        return False
    game.msg('You set a snare in the dirt.' if laid == 1 else 'You set two snares in the dirt.', 'good')
    return True


def x_caltrops(game, sk, r):
    from . import spellmap as SM
    t = game.nearest_target(sk.range, False)
    if not t:
        game.miss_target('No target in sight.')
        return False
    cells = [(t.x + dx, t.y + dy) for dx in range(-sk.radius, sk.radius + 1) for dy in range(-sk.radius, sk.radius + 1)]
    SM.area(game, game.map, cells, D.CALTROPS, round(14 * getattr(sk, 'tdur', 1)), 2 + r // 20)
    game.fx('burst', x=t.x, y=t.y, r=sk.radius, col=sk.color, signs='÷∙')
    game.msg('Iron caltrops scatter across the ground.', 'good')
    return True


def envenom_hit(game, mon):
    """Envenom: your weapon carries poison while it lasts."""
    b = buff(game, 'envenom')
    if not b or mon not in game.map.mons:
        return
    TT = _tt()
    v = b[1] + TT.total(game, 'venom')
    t = 4 + TT.total(game, 'venom_t')
    mon.effects['poison'] = [t, max(1, v)]
    mon.effects['weaken'] = [t, 0]                  # the venom saps its strength: its blows land softer
    if TT.has(game, 'rimeknife'):
        mon.effects['slow'] = [2, 0]
    if TT.has(game, 'black_lotus'):
        for o in [o for o in game.visible_hostiles() if o is not mon and cheb(o.x, o.y, mon.x, mon.y) <= 1]:
            o.effects.setdefault('poison', [t, max(1, v // 2)])


# ------------------------------------------------------------------ Arcane: space
def x_blink(game, sk, r):
    p, m = game.player, game.map
    foes = game.visible_hostiles()
    cells = [(x, y) for x in range(p.x - sk.range, p.x + sk.range + 1) for y in range(p.y - sk.range, p.y + sk.range + 1)
             if m.inb(x, y) and (x, y) != (p.x, p.y) and D.TILES[m.tile(x, y)].walk and not game.occupied(m, x, y)
             and game.visible(x, y) and game.line_clear(p.x, p.y, x, y)]
    if not cells:
        game.msg('There is nowhere to blink to.')
        return False
    TT = _tt()
    if foes:
        if TT.has(game, 'trickster'):              # behind the nearest foe, and it never saw you go
            t = min(foes, key=lambda o: cheb(o.x, o.y, p.x, p.y))
            near = [c for c in cells if cheb(c[0], c[1], t.x, t.y) == 1]
            best = max(near, key=lambda c: cheb(c[0], c[1], p.x, p.y)) if near else None
        else:
            best = None
        if best is None:
            best = max(cells, key=lambda c: (min(cheb(c[0], c[1], o.x, o.y) for o in foes), -cheb(c[0], c[1], p.x, p.y)))
    else:
        best = max(cells, key=lambda c: cheb(c[0], c[1], p.x, p.y))
    ox, oy = p.x, p.y
    game.fx('burst', x=ox, y=oy, r=0, col=sk.color, signs='∙')
    p.x, p.y = best
    game.fx('burst', x=p.x, y=p.y, r=1, col=sk.color, signs='∙░', gather=True)
    _bring(game, ox, oy)
    if TT.has(game, 'stormweaver'):                 # a thunderclap where you stood
        for o in [o for o in foes if cheb(o.x, o.y, ox, oy) <= 1]:
            o.hold = max(o.hold, 1)
            game.damage_mon(o, 4 + r // 6, col=SK.STORM, elem='lightning')
    if TT.has(game, 'trickster') or TT.has(game, 'blink_strike'):
        if TT.has(game, 'trickster'):
            p.buffs = [b for b in p.buffs if b[0] != 'ambush'] + [['ambush', 1, 4, sk.name]]
        if TT.has(game, 'blink_strike'):
            p.buffs = [b for b in p.buffs if b[0] != 'blinkcheap'] + [['blinkcheap', 50, 5, 'Blink Strike']]
    game.compute_fov()
    game.msg('You blink.', 'good')
    return True


def _bring(game, ox, oy):
    """Fold, Soulbinder, Spiritcaller: who comes with you through a blink or a gate."""
    from . import mercs as MC
    TT = _tt()
    p, m = game.player, game.map
    who = []
    if TT.has(game, 'fold'):
        mc = MC.with_you(game, 'merc')
        if mc and mc.body is not None:
            who.append(mc.body)
    if TT.has(game, 'spiritcaller'):
        who += [b.body for b in MC.beasts(game) if b.body is not None and b.body in m.mons]
    if TT.has(game, 'soulbinder'):
        who += [o for o in getattr(game, 'thralls', []) if o in m.mons]
    for o in who:
        if cheb(o.x, o.y, ox, oy) > 4:
            continue
        spots = [c for c in free_around(game, m, p.x, p.y, 2) if c != (p.x, p.y) and not game.occupied(m, *c)]
        if spots:
            o.x, o.y = min(spots, key=lambda c: cheb(c[0], c[1], p.x, p.y))


def x_gate(game, sk, r):
    """Gate: the first cast opens a gate where you stand, the second its twin; step onto one to come out at the
    other, you and your company."""
    from . import spellmap as SM
    p, m = game.player, game.map
    g_ = [xy for xy in getattr(m, 'gates', []) if m.tile(*xy) == D.GATE]
    turns = round(20 * getattr(sk, 'tdur', 1))
    if len(g_) == 1 and cheb(g_[0][0], g_[0][1], p.x, p.y) > 10:
        game.msg('The other gate is too far: no more than ten tiles between them.', 'bad')
        return False
    if len(g_) != 1:
        for xy in g_:
            SM.clear(m, xy)
        g_ = []
    if not SM.place(game, m, p.x, p.y, D.GATE, turns):
        game.msg('A gate will not open here.')
        return False
    m.gates = g_ + [(p.x, p.y)]
    p.gate_skip = (p.x, p.y)
    game.fx('burst', x=p.x, y=p.y, r=1, col=sk.color, signs='Ω∙', gather=True)
    game.msg('A gate opens under your feet.' if len(m.gates) == 1 else 'A second gate opens: the two are one.', 'good')
    return True


def through_gate(game):
    p, m = game.player, game.map
    gs = [xy for xy in getattr(m, 'gates', []) if m.tile(*xy) == D.GATE]
    if (p.x, p.y) != getattr(p, 'gate_skip', None):
        p.gate_skip = None
    if len(gs) != 2 or (p.x, p.y) not in gs or getattr(p, 'gate_skip', None) == (p.x, p.y):
        return
    other = gs[1] if gs[0] == (p.x, p.y) else gs[0]
    if game.occupied(m, *other):
        return
    ox, oy = p.x, p.y
    p.x, p.y = other
    p.gate_skip = other
    from . import mercs as MC
    for mc in MC.party(game):
        b = mc.body
        if b is not None and b in m.mons and cheb(b.x, b.y, ox, oy) <= 3:
            spots = [c for c in free_around(game, m, p.x, p.y, 2) if c != (p.x, p.y) and not game.occupied(m, *c)]
            if spots:
                b.x, b.y = spots[0]
    _bring(game, ox, oy)
    game.fx('burst', x=p.x, y=p.y, r=1, col=(120, 160, 255), signs='Ω∙')
    game.compute_fov()
    game.msg('You step through the gate and out of the other.', 'info')


# ------------------------------------------------------------------ Arcane: runes, and taking spells away
def x_rune(game, sk, r):
    from . import spellmap as SM
    TT = _tt()
    m = game.map
    c = _toward_foe(game)
    if not c:
        game.msg('There is no room for a rune.')
        return False
    most = RUNES + (1 if TT.has(game, 'many_runes') else 0)
    mine = [xy for xy in getattr(m, 'runes', []) if m.tile(*xy) == D.RUNE]
    while len(mine) >= most:
        SM.clear(m, mine.pop(0))
    if not SM.place(game, m, c[0], c[1], D.RUNE, 80, 1 if getattr(sk, 'snaring', False) else 0):
        game.msg('The rune will not take here.')
        return False
    m.runes = mine + [c]
    m.__dict__.setdefault('rune_uses', {})[c] = 2 if TT.has(game, 'runeward') else 1
    game.flash([c], sk.color, 'Φ', .25)
    game.msg('You trace a rune on the ground. It glows, and fades to a faint line.', 'good')
    return True


def x_dispel(game, sk, r):
    from . import spellmap as SM
    TT = _tt()
    p, m = game.player, game.map
    foes = [o for o in game.visible_hostiles() if cheb(o.x, o.y, p.x, p.y) <= sk.range and
            any(md in o.mods for md in MAGIC_MODS)]
    done = False
    if foes:
        t = min(foes, key=lambda o: cheb(o.x, o.y, p.x, p.y))
        gone = [md for md in t.mods if md in MAGIC_MODS]
        t.mods = [md for md in t.mods if md not in MAGIC_MODS]
        game.fx('burst', x=t.x, y=t.y, r=0, col=sk.color, signs='∙')
        game.msg(f'The magic on {t.the()} comes apart: no longer {", ".join(gone).lower()}.', 'good')
        if TT.has(game, 'spellfire'):
            t.effects['burn'] = [4, 3 + r // 10]
        t.awake = True
        done = True
    else:
        f = getattr(m, 'fields', {})
        tiles = [xy for xy, fd in f.items() if fd[0] in SM.SPELL_TILES and cheb(xy[0], xy[1], p.x, p.y) <= 4]
        if tiles:
            xy = min(tiles, key=lambda c: cheb(c[0], c[1], p.x, p.y))
            name = D.TILES[f[xy][0]].name
            SM.clear(m, xy)
            game.flash([xy], sk.color, '∙', .2)
            game.msg(f'You unpick the spell: the {name} is gone.', 'good')
            done = True
    if not done:
        game.msg('There is no magic near to take away.')
        return False
    if TT.has(game, 'arcanist'):
        p.mana = min(game.stats()['max_mana'], p.mana + 8)
    return True


def counter(game, mon):
    """Counterspell (and a Sanctifier's Ward): the first hostile spell at you does not go off."""
    p = game.player
    TT = _tt()
    b = buff(game, 'counter')
    ward = TT.has(game, 'sanctifier') and buff(game, 'ward') is not None and not getattr(p, 'ward_caught', False)
    if not b and not ward:
        return False
    if b:
        b[1] -= 1
        if b[1] <= 0:
            drop_buff(game, 'counter')
    else:
        p.ward_caught = True
    game.flash([(p.x, p.y)], ARC, '○', .2)
    game.msg(f"You catch {mon.the()}'s spell and unmake it.", 'good')
    s = game.stats()
    if TT.has(game, 'arcanist'):
        p.mana = min(s['max_mana'], p.mana + 8)
    if TT.has(game, 'voidcaller'):
        game.heal(6 + p.disc['arcane'][0] // 6, show=True)
    return True


def haste_skip(game):
    """Haste: every second thing you do takes no time."""
    p = game.player
    if not buff(game, 'haste'):
        return False
    p.haste_flip = not getattr(p, 'haste_flip', False)
    return p.haste_flip


# ------------------------------------------------------------------ the tiles at work
def mon_moved(game, mon):
    """A foe stepped onto one of your tiles: a snare holds, caltrops bite, a rune throws it back."""
    from . import spellmap as SM
    TT = _tt()
    m = game.map
    xy = (mon.x, mon.y)
    f = getattr(m, 'fields', {})
    fd = f.get(xy)
    if not fd or mon.is_npc or getattr(mon, 'ally', False):
        return
    tile, _left, _u, power = fd
    p = game.player
    sprung = False
    if tile == D.SNARE:
        mon.hold = max(mon.hold, power)
        game.flash([xy], (200, 170, 120), '^', .2)
        game.msg(f'{mon.the()[0].upper() + mon.the()[1:]} steps into your snare.', 'good')
        SM.clear(m, xy)
        sprung = True
    elif tile == D.CALTROPS:
        mon.effects['slow'] = [2, 0]
        mon.effects['bleed'] = [3, max(1, power)]
        sprung = True
    elif tile == D.RUNE:
        if power:                                   # a snaring rune holds instead
            mon.hold = max(mon.hold, 3)
        else:
            dx, dy = (mon.x > p.x) - (mon.x < p.x), (mon.y > p.y) - (mon.y < p.y)
            from . import weaponskills as WS
            WS.push(game, mon, 2) if (dx or dy) else None
            mon.hold = max(mon.hold, 1 + TT.total(game, 'rune_hold'))
        game.flash([xy], ARC, 'Φ', .25)
        game.msg(f'The rune flares under {mon.the()}.', 'good')
        uses = m.__dict__.setdefault('rune_uses', {})
        uses[xy] = uses.get(xy, 1) - 1
        if uses[xy] <= 0:
            SM.clear(m, xy)
        if TT.has(game, 'leywalker'):
            SM.area(game, m, [(xy[0] + a, xy[1] + b) for a in (-1, 0, 1) for b in (-1, 0, 1)], D.ROOTS, 6)
    if sprung:
        if TT.has(game, 'killing_field'):
            mon.effects['poison'] = [5, 3 + p.disc['cunning'][0] // 10]
            game.damage_mon(mon, 4 + p.disc['cunning'][0] // 6)
        if TT.has(game, 'firestarter') and mon in m.mons:
            mon.effects['burn'] = [4, 3]
        if TT.has(game, 'sparkthief') and mon in m.mons:
            near = [o for o in game.visible_hostiles() if o is not mon and cheb(o.x, o.y, mon.x, mon.y) <= 2]
            if near:
                o = random.choice(near)
                game.fx('zap', cells=game.cells_between(xy, (o.x, o.y)), col=SK.STORM)
                game.damage_mon(o, 4 + p.disc['cunning'][0] // 8, col=SK.STORM, elem='lightning')


def on_tile(game, o, tile):
    """Each turn on smoke: who stands in it cannot see you."""
    if tile == D.SMOKE and o.awake and cheb(o.x, o.y, game.player.x, game.player.y) > 1:
        o.awake = False


EXEC = {'vanish': x_vanish, 'shadowstep': x_shadowstep, 'smoke': x_smoke, 'snare': x_snare, 'caltrops': x_caltrops,
        'blink': x_blink, 'gate': x_gate, 'rune': x_rune, 'dispel': x_dispel}
SK.EXEC.update(EXEC)
