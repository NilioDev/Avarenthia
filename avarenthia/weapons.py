"""The weapons' own rules: what each kind brings to a fight that you notice (see "Weapons" in docs/built.md).
Reach for spears and staves, the thrown spear and throwing knives, crossbows that shoot and load in turn, the scimitar's
cut in passing, the flail over a shield, the war hammer through armour, fists in a cestus or claws, two weapons at once.
Monsters with gear carry one weapon of their kind (mon.wield): what they fight with is what they drop."""
import random

from . import data as D
from .worldgen import cheb

LIGHT = {'dagger', 'shortsword', 'scimitar', 'club'}          # may go in the second hand
REACH = {'staff', 'warstaff', 'spear', 'halberd', 'scythe'}   # Spears and Staves: strike two tiles away
CROSSBOWS = {'lightxbow', 'heavyxbow'}
KNIVES_MAX = 6
# heavy armour or a hard shell by nature: weapons do a quarter less, a war hammer a quarter more
ARMOURED = {'knight', 'robber_knight', 'holy_knight', 'clansman', 'thunderer', 'grey_dwarf', 'pass_clansman', 'soldier',
            'watch_soldier', 'hob_legionary', 'hob_captain', 'orc_chief', 'warlord', 'skeleton', 'skel_warrior', 'draugr',
            'animated_armour', 'clay_golem', 'varnish_guardian', 'gargoyle', 'fire_beetle', 'horn_beetle', 'rust_beetle',
            'bombardier', 'giant_crab', 'crabfolk', 'pincer_horror'}
BLEEDING_DEAD = {'zombie', 'ghoul', 'ghast', 'ghast_lord', 'vampire_spawn', 'draugr'}
C_SPARK = (210, 210, 215)


def family(it):
    return D.FAMILY_OF.get(it.base, it.base) if it is not None and it.k == 'gear' else None


def base(it):
    return D.BASES[it.base] if it is not None and it.k == 'gear' else {}


def working(it):
    return it is not None and not (getattr(it, 'mdur', 0) and it.dur <= 0)


def main_hand(game):
    w = game.eq_item('weapon')
    return w if working(w) else None


def wielded(game):
    """The family of the weapon in your hand, or None for empty hands."""
    return family(main_hand(game))


def off_hand(game):
    """A second weapon, carried where a shield would be."""
    o = game.eq_item('shield')
    return o if working(o) and o.slot == 'weapon' else None


def has_shield(game):
    o = game.eq_item('shield')
    return bool(working(o) and o.slot == 'shield' and o.arm)


def fist(game):
    """A cestus or tiger claws in the gloves slot, while your weapon hand is empty."""
    if game.eq_item('weapon'):
        return None
    gl = game.eq_item('gloves')
    return gl if working(gl) and base(gl).get('fist') else None


def armoured(mon):
    return not mon.is_npc and (mon.k in ARMOURED or mon.tpl.get('family') == 'construct')


def bleeds(mon):
    fam = mon.tpl.get('family')
    if mon.is_npc:
        return True
    if fam in ('construct', 'ooze', 'plant'):
        return False
    if fam == 'undead' or mon.k in D.UNDEAD:
        return mon.k in BLEEDING_DEAD
    return True


# ------------------------------------------------------------------ gear on monsters
def pick_wield(k):
    """The one weapon a monster of this kind fights with, from what its kind uses."""
    uses = D.GEAR_USERS.get(k)
    if not uses:
        return None
    arms = [f for f in uses if D.BASES.get(D.grades(f)[0], {}).get('slot') == 'weapon']
    return random.choice(arms) if arms else None


def drop_families(mon, uses):
    """What it can drop: its own weapon, and the rest of what its kind wears."""
    w = getattr(mon, 'wield', None)
    if not w:
        return uses
    return [f for f in uses if f == w or D.BASES.get(D.grades(f)[0], {}).get('slot') != 'weapon']


# ------------------------------------------------------------------ the numbers
def stats(game, s, mul):
    """What your hands add to your numbers (called from Game.stats)."""
    fam = wielded(game)
    if fam == 'flail':
        s['ar'] -= 10                                   # the head swings wild
    o = off_hand(game)
    if o and o.dmg:
        s['off'] = (max(1, int(o.dmg[0] * mul * .5)), max(1, int(o.dmg[1] * mul * .5)))
    s['fam'] = fam


def fist_damage(game, wr):
    """Fists in a cestus or claws: the glove's damage, or bare fists hardened with practice, whichever is more."""
    gl = fist(game)
    bare = (1 + wr // 6, 3 + wr // 3)
    if not gl:
        return bare
    lo, hi = base(gl)['fist']
    return max(lo, bare[0]), max(hi, bare[1])


def armour_mult(game, mon, weapon, ranged=False, sunder=False):
    """Heavy armour takes a quarter off a weapon's blow; a war hammer goes through and does more, a crossbow bolt or a
    skill made to break armour goes straight through."""
    if weapon and 'sunder' in mon.effects and not armoured(mon):
        return 1.15                                 # its guard broken: blows bite deeper
    if not weapon or not armoured(mon):
        return 1.0
    fam = wielded(game)
    if fam == 'warhammer' and not ranged:
        game.flash([(mon.x, mon.y)], C_SPARK, '*', .15)
        return 1.25
    if sunder or (ranged and fam in CROSSBOWS) or 'sunder' in mon.effects:
        return 1.0
    return .75


def over_shield(game):
    """A flail goes over a shield, a shield wall or a formation; so does a feint or Over the Shield."""
    return wielded(game) == 'flail' or getattr(game, '_unblockable', False)


def mon_over_block(mon):
    return getattr(mon, 'wield', None) == 'flail'


def blocked(game, mon):
    """Block: with a shield in hand the first blow each turn is caught; a flail swings over it."""
    p = game.player
    if not any(b[0] == 'block' for b in p.buffs) or not has_shield(game) or getattr(p, 'blocked', -1) == game.turn:
        return False
    if mon_over_block(mon):
        game.flash([(p.x, p.y)], C_SPARK, ']', .15)
        game.msg(f'{mon.the()[0].upper() + mon.the()[1:]} swings its flail over your shield.', 'bad')
        return False
    p.blocked = game.turn
    game.wear('shield', .5)
    game.flash([(p.x, p.y)], C_SPARK, '(', .15)
    game.msg(f'You catch {mon.the()} on your shield.', 'good')
    return True


def wear_mult(mon):
    """An enemy hammer wears your armour faster."""
    return 2.0 if getattr(mon, 'wield', None) == 'warhammer' else 1.0


# ------------------------------------------------------------------ a blow in melee
def on_melee(game, mon, s):
    """Before your blow lands: the scimitar's cut in passing. Returns a damage multiplier."""
    p = game.player
    k = 1.0
    st = getattr(p, 'stepped', None)
    if s.get('fam') == 'scimitar' and st is not None and 0 < game.turn - st <= 2:
        p.stepped = None                          # only the first blow after the step
        k *= 1.5
        game.msg('You cut in passing.', 'good')
        game.fx('trail', cells=[(mon.x, mon.y)], col=(235, 235, 240), ch='/' if (mon.x - p.x) * (mon.y - p.y) < 0 else '\\')
    return k


def after_melee(game, mon, s, crit, hit):
    """After your blow: a cestus stuns on a critical hit, claws draw blood, a scythe sweeps the arc, the second hand
    strikes too."""
    p, m = game.player, game.map
    gl = fist(game)
    if hit and gl and mon in m.mons:
        if crit and family(gl) == 'cestus':
            mon.hold = max(mon.hold, 1)
            game.fx('burst', x=mon.x, y=mon.y, col=(240, 230, 160), ch='°')
        if family(gl) == 'claws' and random.random() < .25:
            bleed(game, mon, max(1, (s['dmg'][0] + s['dmg'][1]) // 6))
    if s.get('fam') == 'scythe':
        dx, dy = (mon.x > p.x) - (mon.x < p.x), (mon.y > p.y) - (mon.y < p.y)
        for sx, sy in arc_sides(dx, dy):
            o = m.mon_at(p.x + sx, p.y + sy)
            if o and not o.is_npc and o is not mon:
                game.weapon_strike(o, 75)
    o = off_hand(game)
    if o and s.get('off') and mon in m.mons:
        game.wear('shield', .2)
        if random.random() < min(.95, .9 * s['ar'] / (s['ar'] + mon.df)):
            game.damage_mon(mon, random.randint(*s['off']), random.random() < s['crit'] / 100, weapon=True)


def arc_sides(dx, dy):
    """The two cells beside a blow in direction (dx, dy): the arc a scythe sweeps."""
    dirs = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
    i = dirs.index((dx, dy))
    return dirs[(i - 1) % 8], dirs[(i + 1) % 8]


def bleed(game, mon, v):
    """Bleeding stacks up to three times; who has no blood does not bleed."""
    if not bleeds(mon):
        return
    n = min(3, getattr(mon, 'bleeds', 0) + 1) if 'bleed' in mon.effects else 1
    mon.bleeds = n
    mon.effects['bleed'] = [4, v * n]
    game.fx('burst', x=mon.x, y=mon.y, col=(200, 40, 40), ch=',')


def blood_trail(game, m, x, y):
    """A bleeding foe leaves a red trail for a few turns."""
    trail = m.__dict__.setdefault('blood', {})
    trail[(x, y)] = game.turn + 12
    if len(trail) > 60:
        for c in [c for c, t in trail.items() if t < game.turn]:
            del trail[c]


def blood_at(game, m):
    trail = getattr(m, 'blood', None)
    if not trail:
        return {}
    return {c for c, t in trail.items() if t >= game.turn}


# ------------------------------------------------------------------ at a distance
def reach_target(game, mon):
    """A foe two tiles away in a straight line, with nothing solid between: a spear reaches it."""
    p, m = game.player, game.map
    dx, dy = mon.x - p.x, mon.y - p.y
    if max(abs(dx), abs(dy)) != 2 or dx not in (-2, 0, 2) or dy not in (-2, 0, 2):
        return False
    mx, my = p.x + dx // 2, p.y + dy // 2
    mid = m.mon_at(mx, my)
    if mid and not mid.is_npc:
        return False
    return D.TILES[m.tile(mx, my)].walk


def reach_past(game, dx, dy):
    """Walking into a friend with a foe behind them: with a reach weapon you strike past them."""
    if wielded(game) not in REACH:
        return None
    p, m = game.player, game.map
    o = m.mon_at(p.x + 2 * dx, p.y + 2 * dy)
    if o and not o.is_npc and game.visible(o.x, o.y) and reach_target(game, o):
        return o
    return None


def strike_reach(game, mon):
    p = game.player
    game.fx('bolt', cells=[(p.x + (mon.x - p.x) // 2, p.y + (mon.y - p.y) // 2), (mon.x, mon.y)], src=(p.x, p.y),
            col=(220, 220, 225), ch='-' if mon.y == p.y else '|' if mon.x == p.x else '/' if (mon.x - p.x) * (mon.y - p.y) < 0 else '\\')
    game.melee(mon)
    return 1


def fire(game):
    """The fire key with what you hold: reach, a thrown spear, a knife, a bolt (loaded or not), a sling stone.
    Returns the turns spent, or None to shoot as with a bow."""
    p = game.player
    w = main_hand(game)
    fam = family(w)
    if fam in CROSSBOWS and getattr(w, 'unloaded', False):
        w.unloaded = False
        game.msg(f'You wind the {base(w)["name"].lower()}. It is loaded.', 'info')
        return 2 if fam == 'heavyxbow' else 1
    if fam == 'throwknives' and getattr(w, 'ammo', KNIVES_MAX) <= 0:
        knife = next((i for i in p.inv if i.k == 'ammo' and i.t == 'knife'), None)
        if not knife:
            game.msg('You have no knives left to throw. Pick them up where they fell.', 'bad')
            return 0
        game.remove_one(knife)
        w.ammo = 1
    if fam in REACH:
        t = game.target()
        foes = [o for o in game.visible_hostiles() if reach_target(game, o)]
        if t is not None and t in foes:
            foes = [t]
        if foes:
            return strike_reach(game, min(foes, key=lambda o: o.hp))
        if fam != 'spear':
            game.msg('No foe two steps from you in a straight line. A spear or staff strikes past a friend, never through a wall.')
            return 0
        return None                               # a spear: thrown
    return None


def throw_spear(game, t, s):
    """The spear leaves your hand: it hits hard, and lies where it fell until you pick it up again."""
    p, m = game.player, game.map
    w = main_hand(game)
    game.fx('bolt', cells=game.path_to(t), src=(p.x, p.y), col=(220, 210, 180), ch='/')
    hit = random.random() < max(.25, min(.95, .95 * s['ar'] / (s['ar'] + t.df)))
    x, y = t.x, t.y
    if hit:
        crit = random.random() < s['crit'] / 100
        game.damage_mon(t, random.randint(*s['dmg']) * 1.5, crit, weapon=True)
    else:
        game.num(t.x, t.y, 'miss', (150, 150, 150))
        t.awake = True
    p.eq.pop('weapon', None)
    p.inv.remove(w)
    w.x, w.y, w.thrown = x, y, True
    m.items.append(w)
    game.msg(f'You throw your {w.name}.' + ('' if hit else ' It misses.'), 'info')
    return 1


def after_shot(game, t, hit):
    """What a shot leaves behind: a knife on the ground, a crossbow to load again."""
    w = main_hand(game)
    fam = family(w)
    if fam in CROSSBOWS:
        w.unloaded = True
    if fam == 'throwknives':
        w.ammo = getattr(w, 'ammo', KNIVES_MAX) - 1
        from .entities import Item
        k = Item(game.new_id(), 'ammo', 'knife')
        k.x, k.y = (t.x, t.y)
        game.map.items.append(k)


def shot_df(game, df):
    """A crossbow bolt goes through what would turn an arrow."""
    return df * .5 if wielded(game) in CROSSBOWS else df


def shown(game):
    """What your weapon hand says on the panel: a crossbow loaded or not, the knives left in the set."""
    w = main_hand(game)
    fam = family(w)
    if fam in CROSSBOWS:
        return [('unloaded', (200, 120, 90))] if getattr(w, 'unloaded', False) else [('loaded', (200, 200, 160))]
    if fam == 'throwknives':
        n = getattr(w, 'ammo', KNIVES_MAX)
        return [(f'knives {n}', (200, 200, 160) if n else (200, 120, 90))]
    if any(b[0] == 'block' for b in game.player.buffs) and has_shield(game):
        return [('block', (200, 200, 160))]
    return []


def hand_note(game, it):
    """A word after your weapon in the inventory."""
    fam = family(it)
    if fam in CROSSBOWS:
        return 'unloaded' if getattr(it, 'unloaded', False) else 'loaded'
    if fam == 'throwknives':
        return f"{getattr(it, 'ammo', KNIVES_MAX)} of {KNIVES_MAX}"
    return ''


def unloaded(game):
    w = main_hand(game)
    return family(w) in CROSSBOWS and getattr(w, 'unloaded', False)


def pick_up(game, it):
    """Your thrown spear back in your hand, your knives back with the rest. True if it was taken."""
    p = game.player
    if it.k == 'gear' and getattr(it, 'thrown', False):
        if not game.add_to_inv(it):
            return False
        it.thrown = False
        if not game.eq_item('weapon') and not game.meets(it):
            p.eq['weapon'] = it.id
            game.msg(f'You take up your {it.name} again.', 'info')
        else:
            game.msg(f'You pick up {it.display_name()}.')
        return True
    if it.k == 'ammo' and it.t == 'knife':
        w = main_hand(game)
        if family(w) == 'throwknives' and getattr(w, 'ammo', KNIVES_MAX) < KNIVES_MAX:
            w.ammo = min(KNIVES_MAX, getattr(w, 'ammo', KNIVES_MAX) + it.n)
            game.msg('You pick up your knife.')
            return True
        if game.add_to_inv(it):
            game.msg('You pick up a throwing knife.')
            return True
        return False
    return False


# ------------------------------------------------------------------ two weapons
def off_hand_slot(game, it):
    """Where a weapon you take up goes: a light one beside a one-handed one already in hand goes in the second hand."""
    if it.slot != 'weapon' or family(it) not in LIGHT:
        return 'weapon'
    w = game.eq_item('weapon')
    if w is None or w.id == it.id or base(w).get('two') or base(w).get('ranged'):
        return 'weapon'
    if game.eq_item('shield') is not None:
        return 'weapon'
    return 'shield'


# ------------------------------------------------------------------ ammunition as an item (entities.CRAFT)
def display(game, it):
    return (f'{it.n}x ' if it.n > 1 else '') + 'Throwing Knife' + ('s' if it.n > 1 else '')


def lines(game, it):
    return ['A balanced knife from a set of throwing knives. It goes back into the set when you pick it up.']


def value(game, it):
    return .5


def glyph(it):
    return ')'


def color(it):
    return (200, 200, 205)
