"""The weapon in your hand gives you two skills, on keys 1 and 2 (see "Classes" in docs/plan.md): the first at once,
the second from rank 10 in its discipline. They cost stamina and grow the weapon's discipline. And each weapon family
has one rule that colours your class skills (`rule`), which never stacks with an imbue blow."""
import random

from . import data as _D
from . import skills as SK
from . import weapons as WP
from .worldgen import cheb, free_around

S = SK.Skill
SECOND = 10                 # the discipline rank that opens a weapon's second skill
STEEL, DUST, BLOOD = (226, 226, 232), (170, 140, 100), (200, 40, 40)
ARROW = SK.ARROW

WEAPON_SKILL_LIST = [
    # empty hands, cestus, tiger claws
    S('haymaker', 'Haymaker', 'unarmed', 0, 3, 4, 'melee', pct=170, pct_r=3, fx={'stun': 1}, color=STEEL),
    S('flurry', 'Flurry of Blows', 'unarmed', 0, 4, 5, 'melee', pct=55, pct_r=1.5, hits=3, color=STEEL),
    S('iron_fist', 'Iron Fist', 'unarmed', 0, 5, 7, 'melee', pct=180, pct_r=2.5, sunder=True, color=STEEL),
    S('throat_punch', 'Throat Punch', 'unarmed', 0, 4, 8, 'melee', pct=110, fx={'stun': 1, 'silence': 2}, color=STEEL),
    S('rake', 'Rake', 'unarmed', 0, 3, 5, 'melee', pct=70, pct_r=1.2, hits=2, fx={'bleed': (2, .2, 5)}, color=BLOOD),
    S('pounce', 'Pounce', 'unarmed', 0, 5, 8, 'leap', pct=150, pct_r=2, range=2, color=STEEL),
    # swords
    S('quick_cut', 'Quick Cut', 'swords', 0, 2, 2, 'melee', pct=90, pct_r=1, quick=True, color=STEEL),
    S('feint', 'Feint', 'swords', 0, 3, 8, 'self', buff=('feint', 1, 0, 4), color=STEEL, glyph='/'),
    S('lunge', 'Lunge', 'swords', 0, 3, 4, 'leap', pct=140, pct_r=2, range=2, color=STEEL),
    S('riposte', 'Riposte', 'swords', 0, 4, 10, 'self', buff=('riposte', 1, 0, 5), color=STEEL, glyph='/'),
    S('power_strike', 'Power Strike', 'swords', 0, 3, 4, 'melee', pct=150, pct_r=2, color=STEEL),
    S('half_sword', 'Half-Sword', 'swords', 0, 4, 6, 'melee', pct=130, pct_r=2, sunder=True, armoured=1.5, color=STEEL),
    S('rune_strike', 'Rune Strike', 'swords', 0, 4, 5, 'melee', pct=120, pct_r=1.5, rune=True, color=(180, 200, 255)),
    S('sever', 'Sever Artery', 'swords', 0, 4, 6, 'melee', pct=100, fx={'bleed': (3, .25, 6)}, color=BLOOD),
    S('whirl', 'Whirling Blade', 'swords', 0, 5, 6, 'adjacent', pct=110, pct_r=1.5, spin=True, color=STEEL),
    S('sunder', 'Sunder', 'swords', 0, 4, 8, 'melee', pct=110, pct_r=1.5, fx={'sunder': 8}, color=STEEL),
    S('dervish', 'Dervish', 'swords', 0, 4, 6, 'dervish', pct=100, pct_r=1.5, color=STEEL),
    S('hamstring', 'Hamstring', 'swords', 0, 4, 7, 'melee', pct=100, fx={'slow': 6}, color=STEEL),
    # axes and maces
    S('knock_out', 'Knock Out', 'axes', 0, 3, 6, 'melee', pct=110, fx={'stun': 2}, color=STEEL),
    S('heavy_blow', 'Heavy Blow', 'axes', 0, 3, 5, 'melee', pct=165, pct_r=2, color=STEEL),
    S('skull_crack', 'Skull Crack', 'axes', 0, 5, 9, 'melee', pct=140, fx={'stun': 2, 'fear': 2}, color=STEEL),
    S('armour_breaker', 'Armour Breaker', 'axes', 0, 4, 8, 'melee', pct=120, pct_r=1.5, fx={'sunder': 10}, color=STEEL),
    S('cleave', 'Cleave', 'axes', 0, 4, 5, 'arc', pct=120, pct_r=1.5, width=3, color=STEEL),
    S('rend', 'Rending Chop', 'axes', 0, 4, 7, 'melee', pct=130, fx={'bleed': (3, .3, 6)}, color=BLOOD),
    S('executioner', 'Executioner', 'axes', 0, 6, 9, 'melee', pct=150, pct_r=2.5, execute=2, color=STEEL),
    S('earthshaker', 'Earthshaker', 'axes', 0, 7, 12, 'around', pct=130, pct_r=1.5, radius=1, fx={'stun': 1}, quake=True,
      color=DUST, glyph=':'),
    S('flail_whirl', 'Whirl', 'axes', 0, 5, 6, 'adjacent', pct=100, pct_r=1.5, spin=True, color=STEEL),
    S('over_the_shield', 'Over the Shield', 'axes', 0, 4, 7, 'melee', pct=130, pct_r=1.5, fx={'stun': 1}, unblockable=True,
      color=STEEL),
    S('crush', 'Crush', 'axes', 0, 5, 7, 'melee', pct=140, pct_r=2, armoured=2, color=STEEL),
    # spears and staves
    S('push_back', 'Push Back', 'spears', 0, 3, 6, 'bash', pct=80, push=2, color=DUST, glyph='-'),
    S('focus', 'Focus', 'spears', 0, 2, 12, 'focus', color=(150, 190, 255), glyph='*'),
    S('sweep', 'Sweep', 'spears', 0, 5, 8, 'adjacent', pct=90, pct_r=1, fx={'stun': 1}, spin=True, color=DUST),
    S('spear_throw', 'Throw', 'spears', 0, 3, 3, 'throw', pct=160, pct_r=2, range=6, color=STEEL, glyph='/'),
    S('keep_back', 'Keep Back', 'spears', 0, 4, 12, 'self', buff=('keepback', 1, 0, 8), color=STEEL, glyph='-'),
    S('hook', 'Hook', 'spears', 0, 4, 6, 'hook', pct=90, pct_r=1, color=STEEL),
    S('long_cleave', 'Long Cleave', 'spears', 0, 5, 6, 'arc', pct=110, pct_r=1.5, width=3, reach=2, color=STEEL),
    S('reap', 'Reap', 'spears', 0, 4, 5, 'arc', pct=110, pct_r=1.5, width=5, color=STEEL),
    S('harvest', 'Harvest', 'spears', 0, 6, 9, 'arc', pct=100, pct_r=1.5, width=5, leech=.25, color=(200, 80, 80)),
    # daggers
    S('quick_stab', 'Quick Stab', 'daggers', 0, 2, 2, 'melee', pct=80, pct_r=1, quick=True, color=STEEL),
    S('assassinate', 'Assassinate', 'daggers', 0, 6, 10, 'melee', pct=150, pct_r=2.5, unseen=2, color=STEEL),
    S('fan', 'Fan of Knives', 'daggers', 0, 5, 7, 'fan', pct=80, pct_r=1, range=6, color=STEEL, glyph='x'),
    S('pin', 'Pin', 'daggers', 0, 4, 7, 'shot', pct=90, pct_r=1, range=8, fx={'stun': 2}, color=STEEL, glyph='x'),
    # bows, crossbows and the sling
    S('quick_shot', 'Quick Shot', 'archery', 0, 3, 4, 'shot', pct=70, pct_r=1, hits=2, color=ARROW, glyph='-'),
    S('crippling', 'Crippling Shot', 'archery', 0, 4, 6, 'shot', pct=100, fx={'slow': 6}, color=ARROW, glyph='-'),
    S('aimed', 'Aimed Shot', 'archery', 0, 3, 3, 'shot', pct=145, pct_r=2, color=ARROW, glyph='-'),
    S('volley', 'Volley', 'archery', 0, 7, 10, 'area_shot', pct=80, pct_r=1.2, radius=1, range=9, color=ARROW, glyph='-'),
    S('pierce', 'Piercing Arrow', 'archery', 0, 6, 7, 'pierce', pct=160, pct_r=2, color=ARROW, glyph='='),
    S('heavy_draw', 'Heavy Draw', 'archery', 0, 5, 6, 'shot', pct=170, pct_r=2, push=1, color=ARROW, glyph='-'),
    S('snap_shot', 'Snap Shot', 'archery', 0, 3, 5, 'snap', pct=100, pct_r=1.5, color=ARROW, glyph='-'),
    S('bolt_through', 'Bolt Through', 'archery', 0, 5, 6, 'pierce', pct=150, pct_r=2, color=ARROW, glyph='='),
    S('xbow_brace', 'Brace', 'archery', 0, 2, 6, 'reload', color=ARROW, glyph='-'),
    S('stunning_stone', 'Stunning Stone', 'archery', 0, 3, 5, 'shot', pct=90, pct_r=1, fx={'stun': 1}, color=DUST, glyph='∙'),
    S('skipping_stone', 'Skipping Stone', 'archery', 0, 4, 5, 'skip', pct=100, pct_r=1.2, color=DUST, glyph='∙'),
    # the shapes of beasts (the Shapeshifter branch of the Nature tree): teeth and claws instead of a weapon
    S('bite', 'Bite', 'nature', 0, 3, 3, 'melee', dtype='weapon', pct=120, pct_r=1.5, fx={'bleed': (2, .2, 4)}, color=BLOOD),
    S('wolf_lunge', 'Lunge', 'nature', 0, 4, 5, 'leap', dtype='weapon', pct=130, pct_r=1.5, range=3, color=STEEL),
    S('maul', 'Maul', 'nature', 0, 4, 4, 'melee', dtype='weapon', pct=160, pct_r=2, color=STEEL),
    S('roar', 'Roar', 'nature', 0, 5, 12, 'around', dtype='none', radius=2, fx={'fear': 3}, color=(214, 140, 76), glyph='!'),
    S('talons', 'Talons', 'nature', 0, 2, 3, 'melee', dtype='weapon', pct=60, pct_r=1, hits=2, color=STEEL),
    S('dive', 'Dive', 'nature', 0, 4, 6, 'leap', dtype='weapon', pct=110, pct_r=1.5, range=5, color=(220, 230, 255)),
]
# skills a knot of a tree teaches: on keys 3-5 like any class skill, never found as a tome
TREE_SKILL_LIST = [
    S('wolf_shape', 'Wolf Shape', 'nature', 0, 8, 40, 'shape', shape=('wolf', 30, 5, 25), color=SK.BEAST, glyph='C'),
    S('bear_shape', 'Bear Shape', 'nature', 0, 9, 45, 'shape', shape=('bear', 15, 30, 25), color=SK.BEAST, glyph='q'),
    S('hawk_shape', 'Hawk Shape', 'nature', 0, 6, 40, 'shape', shape=('hawk', -20, 0, 30), color=(220, 230, 255), glyph='v'),
]
# the two skills of each weapon kind; 'fists' is empty hands
KIT = {
    'fists': ('haymaker', 'flurry'), 'cestus': ('iron_fist', 'throat_punch'), 'claws': ('rake', 'pounce'),
    'shortsword': ('quick_cut', 'feint'), 'longsword': ('lunge', 'riposte'), 'bastard': ('power_strike', 'half_sword'),
    'runeblade': ('rune_strike', 'sever'), 'greatsword': ('whirl', 'sunder'), 'scimitar': ('dervish', 'hamstring'),
    'club': ('knock_out', 'heavy_blow'), 'mace': ('skull_crack', 'armour_breaker'), 'waraxe': ('cleave', 'rend'),
    'greataxe': ('executioner', 'cleave'), 'maul': ('earthshaker', 'heavy_blow'), 'flail': ('flail_whirl', 'over_the_shield'),
    'warhammer': ('crush', 'earthshaker'), 'staff': ('push_back', 'focus'), 'warstaff': ('sweep', 'focus'),
    'spear': ('spear_throw', 'keep_back'), 'halberd': ('hook', 'long_cleave'), 'scythe': ('reap', 'harvest'),
    'dagger': ('quick_stab', 'assassinate'), 'throwknives': ('fan', 'pin'), 'shortbow': ('quick_shot', 'crippling'),
    'longbow': ('aimed', 'volley'), 'warbow': ('pierce', 'heavy_draw'), 'lightxbow': ('snap_shot', 'bolt_through'),
    'heavyxbow': ('bolt_through', 'xbow_brace'), 'sling': ('stunning_stone', 'skipping_stone'),
    'wolf': ('bite', 'wolf_lunge'), 'bear': ('maul', 'roar'), 'hawk': ('talons', 'dive'),
}
SHAPE_KITS = ('wolf', 'bear', 'hawk')
RANGED_MODES = ('shot', 'pierce', 'area_shot', 'fan', 'snap', 'skip')
for _s in WEAPON_SKILL_LIST:
    _s.weapon_skill = True
    _s.unlock = 0
for _s in TREE_SKILL_LIST:
    _s.unlock, _s.tree_skill = 0, True
WSKILLS = {s.id: s for s in WEAPON_SKILL_LIST + TREE_SKILL_LIST}


def kit(game):
    """The family whose two skills you have now: your weapon's, or your fists' (a cestus or claws on them)."""
    from . import anim as AN
    sh = AN.shape_of(game.player)
    if sh in SHAPE_KITS:                            # in a beast's shape: its teeth and claws
        return sh
    fam = WP.wielded(game)
    if fam:
        return fam
    gl = WP.fist(game)
    return WP.family(gl) if gl else 'fists'


def skills_now(game):
    """The two weapon skills of what you hold: (first, second or None while your rank is under 10)."""
    k = KIT.get(kit(game))
    if not k:
        return None, None
    line = WSKILLS[k[0]].line
    r = game.player.disc.get(line, [0, 0])[0]
    return k[0], (k[1] if r >= SECOND or kit(game) in SHAPE_KITS else None)


def second_locked(game):
    k = KIT.get(kit(game))
    return k[1] if k and skills_now(game)[1] is None else None


# ------------------------------------------------------------------ the new kinds of blow
def _dir(a, b):
    return (b[0] > a[0]) - (b[0] < a[0]), (b[1] > a[1]) - (b[1] < a[1])


def _arc_cells(game, sk, t):
    """The tiles a sweep covers towards t: three or five in a fan, one or two tiles out."""
    p = game.player
    dx, dy = _dir((p.x, p.y), (t.x, t.y))
    dirs = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
    i = dirs.index((dx, dy))
    half = sk.width // 2
    out = []
    for k in range(-half, half + 1):
        ex, ey = dirs[(i + k) % 8]
        for n in range(1, getattr(sk, 'reach', 1) + 1):
            out.append((p.x + ex * n, p.y + ey * n))
    return out


def swing(game, cells, wide=False):
    """The swing arc of a weapon skill: \\ | / along the side of the target, white fading to steel."""
    if cells:
        game.fx('swing', cells=cells, src=(game.player.x, game.player.y), col=STEEL, wide=wide)


def x_arc(game, sk, r):
    p, m = game.player, game.map
    t = SK._melee_target(game) if getattr(sk, 'reach', 1) == 1 else \
        next((o for o in game.visible_hostiles() if cheb(o.x, o.y, p.x, p.y) <= sk.reach), None)
    if not t:
        game.msg('No enemy within reach.')
        return False
    p.last_target = t.id
    cells = _arc_cells(game, sk, t)
    swing(game, [(t.x, t.y)], sk.width >= 5)
    hit = 0
    for c in cells:
        o = m.mon_at(*c)
        if o and not o.is_npc:
            before = o.hp
            SK._hit(game, o, sk, r)
            hit += max(0, before - max(0, o.hp))
    if getattr(sk, 'leech', 0) and hit:
        game.heal(round(hit * sk.leech), show=True)
    return True


def x_dervish(game, sk, r):
    """Step and strike: up to two foes beside you."""
    p = game.player
    t = [o for o in game.visible_hostiles() if cheb(o.x, o.y, p.x, p.y) <= 1][:2]
    if not t:
        game.msg('No enemy within reach.')
        return False
    p.stepped = game.turn - 1                       # it counts as a step for the cut in passing
    for o in t:
        SK._hit(game, o, sk, r)
    return True


def x_hook(game, sk, r):
    """A halberd's hook: pull a foe two tiles away one tile in, and strike."""
    p, m = game.player, game.map
    t = game.target()
    cands = [o for o in game.visible_hostiles() if WP.reach_target(game, o) or cheb(o.x, o.y, p.x, p.y) == 1]
    if t not in cands:
        t = cands[0] if cands else None
    if not t:
        game.msg('No enemy within reach of the hook.')
        return False
    p.last_target = t.id
    if cheb(t.x, t.y, p.x, p.y) == 2:
        dx, dy = _dir((t.x, t.y), (p.x, p.y))
        nx, ny = t.x + dx, t.y + dy
        if D_walk(m, nx, ny) and not game.occupied(m, nx, ny) and not t.tpl.get('boss'):
            game.fx('trail', cells=[(t.x, t.y)], col=DUST, ch='·')
            t.x, t.y = nx, ny
    SK._hit(game, t, sk, r)
    return True


def D_walk(m, x, y):
    return m.inb(x, y) and _D.TILES[m.tile(x, y)].walk


def x_throw(game, sk, r):
    """The spear's Throw: a hard throw at range; the spear lies where it fell."""
    t = game.nearest_target(sk.range, True)
    if not t:
        game.miss_target('No target in sight.')
        return False
    s = game.stats()
    s['dmg'] = tuple(round(v * (sk.pct + sk.pct_r * r) / 150) for v in s['dmg'])
    game.player.last_target = t.id
    WP.throw_spear(game, t, s)
    return True


def x_fan(game, sk, r):
    """Fan of Knives: three knives at up to three foes."""
    p = game.player
    t = sorted([o for o in game.visible_hostiles() if cheb(o.x, o.y, p.x, p.y) <= sk.range
                and game.line_clear(p.x, p.y, o.x, o.y)], key=lambda o: cheb(o.x, o.y, p.x, p.y))[:3]
    if not t:
        game.miss_target('No target in sight.')
        return False
    for o in t:
        SK._fly(game, sk, game.path_to(o), (p.x, p.y), True)
        SK._hit(game, o, sk, r, True)
    return True


def x_area_shot(game, sk, r):
    """Volley: arrows on a small group round your target (a bow places it two tiles further)."""
    p = game.player
    t = game.nearest_target(sk.range + rule_range(game, sk), True)
    if not t:
        game.miss_target('No target in sight.')
        return False
    p.last_target = t.id
    for o in [o for o in game.visible_hostiles() if cheb(o.x, o.y, t.x, t.y) <= sk.radius]:
        SK._fly(game, sk, game.path_to(o), (p.x, p.y), True)
        SK._hit(game, o, sk, r, True)
    return True


def x_snap(game, sk, r):
    """Snap Shot: shoot, then step back from the foe."""
    p, m = game.player, game.map
    t = game.nearest_target(sk.range, True)
    if not t:
        game.miss_target('No target in sight.')
        return False
    SK.x_bolt(game, sk, r, ranged=True)
    dx, dy = _dir((t.x, t.y), (p.x, p.y))
    nx, ny = p.x + dx, p.y + dy
    if (dx or dy) and D_walk(m, nx, ny) and not game.occupied(m, nx, ny):
        game.fx('trail', cells=[(p.x, p.y)], col=DUST, ch='·')
        p.x, p.y = nx, ny
        game.compute_fov()
    return True


def x_skip(game, sk, r):
    """Skipping Stone: it strikes one foe and skips on to a second within three tiles."""
    p = game.player
    t = game.nearest_target(sk.range, True)
    if not t:
        game.miss_target('No target in sight.')
        return False
    p.last_target = t.id
    SK._fly(game, sk, game.path_to(t), (p.x, p.y), True)
    tx, ty = t.x, t.y
    SK._hit(game, t, sk, r, True)
    nxt = [o for o in game.visible_hostiles() if o is not t and cheb(o.x, o.y, tx, ty) <= 3]
    if nxt:
        o = min(nxt, key=lambda o: cheb(o.x, o.y, tx, ty))
        SK._fly(game, sk, game.cells_between((tx, ty), (o.x, o.y)), (tx, ty), True)
        SK._hit(game, o, sk, r, True)
    return True


def x_focus(game, sk, r):
    """Focus: a turn of stillness; mana comes back and your next spell costs less."""
    p = game.player
    s = game.stats()
    got = round(s['max_mana'] * .12 + r * .3)
    p.mana = min(s['max_mana'], p.mana + got)
    p.buffs = [b for b in p.buffs if b[0] != 'focus'] + [['focus', 30, 6, sk.name]]
    game.fx('rise', x=p.x, y=p.y, col=sk.color)
    game.msg(f'You gather yourself: {got} mana.', 'good')
    return True


def x_reload(game, sk, r):
    """Brace: stand fast and the heavy crossbow is wound at once."""
    w = WP.main_hand(game)
    if w is not None:
        w.unloaded = False
    game.player.buffs = [b for b in game.player.buffs if b[0] != 'braced'] + [['braced', 25, 2, sk.name]]
    game.msg('You brace and wind the crossbow in one pull. It is loaded.', 'good')
    return True


for _k, _f in (('arc', x_arc), ('dervish', x_dervish), ('hook', x_hook), ('throw', x_throw), ('fan', x_fan),
               ('area_shot', x_area_shot), ('snap', x_snap), ('skip', x_skip), ('focus', x_focus), ('reload', x_reload)):
    SK.EXEC[_k] = _f


# ------------------------------------------------------------------ each family's rule for your class skills
RULE = {'unarmed': 'Every third blow gives you some stamina or mana back.',
        'swords': 'Every blow takes a turn off the recharge of your class skills.',
        'axes': 'Class skills that do damage sometimes push the foe back a tile.',
        'staves': 'Spells cost 15% less mana.',
        'spears': 'Class skills aimed at a foe beside you reach two tiles in a line.',
        'daggers': 'Class skills strike critically more often on a foe beside you.',
        'archery': 'Area skills can be placed two tiles further.',
        'shield': 'Defensive skills last half as long again.',
        'grimoire': 'More mana.'}
STAVES = ('staff', 'warstaff')


def family_rule(game):
    """The key of the rule your weapon gives (RULE)."""
    fam = kit(game)
    if fam in STAVES:
        return 'staves'
    if fam == 'fists' or fam in ('cestus', 'claws'):
        return 'unarmed'
    return SK.WEAPON_LINE.get(fam)


def rule_range(game, sk):
    return 2 if family_rule(game) == 'archery' and sk.mode in ('target_area', 'area_shot', 'storm') else 0


def mana_mult(game):
    return .85 if family_rule(game) == 'staves' else 1.0


def buff_turns(game, sk, t):
    """A shield in your other hand lengthens defensive skills."""
    if WP.has_shield(game) and sk.buff and sk.buff[0] in ('def', 'dr', 'ward', 'block', 'unbroken', 'bond', 'riposte'):
        return round(t * 1.5)
    return t


def on_blow(game, mon, s):
    """After a blow with your weapon (a bump): the family's rule. Never with an imbue blow (part 2)."""
    p = game.player
    rule = family_rule(game)
    if rule == 'swords':
        for k in list(p.cooldowns):
            sk = SK.SKILLS.get(k)
            if sk and not getattr(sk, 'weapon_skill', False):
                p.cooldowns[k] -= 1
                if p.cooldowns[k] <= 0:
                    del p.cooldowns[k]
    elif rule == 'unarmed':
        p.blows = getattr(p, 'blows', 0) + 1
        if p.blows % 3 == 0:
            st = game.stats()
            if p.stamina < st['max_stamina'] or p.mana >= st['max_mana']:
                p.stamina = min(st['max_stamina'], p.stamina + 2 + st['max_stamina'] // 15)
                col = (230, 200, 90)
            else:
                p.mana = min(st['max_mana'], p.mana + 2 + st['max_mana'] // 15)
                col = (120, 160, 255)
            game.fx('drain', cells=game.cells_between((mon.x, mon.y), (p.x, p.y))[:-1], col=col, dur=.2)


def class_hit(game, mon, sk):
    """A class skill strikes a foe: an axe or mace may push it back a tile."""
    if family_rule(game) == 'axes' and random.random() < .25 and mon in game.map.mons and not mon.tpl.get('boss'):
        p, m = game.player, game.map
        dx, dy = _dir((p.x, p.y), (mon.x, mon.y))
        nx, ny = mon.x + dx, mon.y + dy
        if (dx or dy) and D_walk(m, nx, ny) and not game.occupied(m, nx, ny):
            mon.x, mon.y = nx, ny


def class_crit(game, mon):
    """A dagger's rule: class skills crit more often on a foe beside you (percent)."""
    p = game.player
    return 15 if family_rule(game) == 'daggers' and cheb(mon.x, mon.y, p.x, p.y) <= 1 else 0


def keep_back(game, mon, ox, oy):
    """Keep Back: a foe that comes up beside you meets the spear first."""
    p = game.player
    if not any(b[0] == 'keepback' for b in p.buffs) or mon.is_npc or mon not in game.map.mons:
        return
    if cheb(ox, oy, p.x, p.y) > 1 and cheb(mon.x, mon.y, p.x, p.y) == 1 and WP.wielded(game) in WP.REACH:
        game.msg(f'You meet {mon.the()} with the point of your {WP.base(WP.main_hand(game))["name"].lower()}.', 'good')
        game.weapon_strike(mon, 80)


def push(game, mon, n, sign=None):
    """Drive a foe n tiles away from you, leaving a little dust where it went."""
    p, m = game.player, game.map
    if mon not in m.mons or mon.tpl.get('boss'):
        return
    dx, dy = _dir((p.x, p.y), (mon.x, mon.y))
    trail = []
    for _ in range(n):
        nx, ny = mon.x + dx, mon.y + dy
        if not (dx or dy) or not D_walk(m, nx, ny) or game.occupied(m, nx, ny):
            break
        trail.append((mon.x, mon.y))
        mon.x, mon.y = nx, ny
    if trail:
        game.fx('trail', cells=trail, col=DUST, ch='·')


def rune_extra(game, mon):
    """Rune Strike: the runes on the blade carry a little of your first school."""
    from . import classes as CL
    c = CL.classes(game)
    elem = SK.LINE_ELEM.get(c[0]) if c else None
    r = game.player.disc[c[0]][0] if c else 0
    col = SK.DISC_COLOR.get(c[0], STEEL) if c else STEEL
    return game.damage_mon(mon, 4 + r // 3, col=col, elem=elem)


def riposte(game, mon):
    """Riposte: the first blow at you is turned aside and answered."""
    p = game.player
    if not any(b[0] == 'riposte' for b in p.buffs) or cheb(mon.x, mon.y, p.x, p.y) > 1 or WP.wielded(game) is None:
        return False
    p.buffs = [b for b in p.buffs if b[0] != 'riposte']
    game.msg(f'You turn {mon.the()}\'s blow aside and strike back.', 'good')
    swing(game, [(mon.x, mon.y)])
    game.weapon_strike(mon, 120)
    return True


def free_spots(game, m, x, y):
    return [c for c in free_around(game, m, x, y, 1) if not game.occupied(m, *c)]
