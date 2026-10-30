"""Alchemy without fixed recipes, like cooking: every herb has two properties (foraging.HERBS). Pick two or three
herbs at [P] and what they share becomes the brew; three that share one property make it stronger; nothing shared is
a ruined brew. Its strength is the herbs' tier and your rank. A shared Venom, Flame or Silver makes a blade oil (a
short buff), a shared Sleep a flask to throw. Starmoss doubles a brew; alone it is the Starlight Elixir (+5 life for
good, once per hero). Strong spirits as the base make a tincture: it lasts twice as long.

A brew is Item('draught', form) with it.props (the shared properties), it.q (its strength) and it.long (a tincture)."""
import random

from . import foraging as FG
from . import lifeskills as LS

OILS = ('Venom', 'Flame', 'Silver')
WORD = {'Heal': 'Healing', 'Mana': 'Mana', 'Stamina': 'Vigour', 'Regen': 'Renewal', 'Cure': 'Cleansing',
        'Staunch': 'Staunching', 'Ward Fire': 'Fire Ward', 'Ward Cold': 'Cold Ward', 'Ward Poison': 'Poison Ward',
        'Sight': 'True Sight', 'Calm': 'Calm', 'Swift': 'Swiftness', 'Strength': 'Strength', 'Venom': 'Venom',
        'Flame': 'Fire', 'Silver': 'Silver'}
WHAT = {'Heal': 'heals', 'Mana': 'restores mana', 'Stamina': 'restores stamina', 'Regen': 'life comes back faster',
        'Cure': 'cures poison and sickness', 'Staunch': 'stops bleeding', 'Ward Fire': 'fire resistance',
        'Ward Cold': 'cold resistance', 'Ward Poison': 'poison resistance', 'Sight': 'you see what hides',
        'Calm': 'beasts notice you later', 'Swift': 'quicker on the road, and Dexterity', 'Strength': 'Strength',
        'Venom': 'your blows poison', 'Flame': 'your blows burn', 'Silver': 'your blows sear the dead'}
SPIRITS = ('juniper_spirits', 'spiced_spirits')
COL = {'draught': (190, 140, 230), 'oil': (230, 190, 90), 'flask': (150, 160, 230), 'starlight': (210, 220, 255)}


# ------------------------------------------------------------------ what you can put in the kettle
def herbs(game):
    """The herbs in your pack that alchemy uses (one row per kind)."""
    seen, out = set(), []
    for it in game.player.inv:
        if it.k == 'plant' and it.t in FG.HERBS and it.t != 'everbloom' and it.t not in seen:
            seen.add(it.t)
            out.append(it)
    return out


def spirit(game):
    return next((i for i in game.player.inv if i.k == 'food' and i.t in SPIRITS), None)


def herb_rank(key):
    return LS.TIER_RANK[FG.HERBS[key][0]]


def shared(keys):
    """What two or three herbs share: (properties, did three share one)."""
    plain = [k for k in keys if k != 'starmoss']
    count = {}
    for k in plain:
        for pr in set(FG.HERBS[k][1]):
            count[pr] = count.get(pr, 0) + 1
    out = [pr for pr in FG.PROPS if count.get(pr, 0) >= 2]
    return out, any(c >= 3 for c in count.values())


def form_of(props):
    if any(pr in OILS for pr in props):
        return 'oil', [pr for pr in props if pr in OILS]
    if 'Sleep' in props:
        return 'flask', ['Sleep']
    return 'draught', props


def strength(game, keys, triple):
    plain = [k for k in keys if k != 'starmoss']
    tier = sum(FG.TIER_VALUE[FG.HERBS[k][0]] for k in plain) / max(1, len(plain))
    s = round(tier) + LS.rank(game, 'alchemy') // 10 + (1 if triple else 0) + (1 if LS.rank(game, 'alchemy') >= 20 else 0)
    return s * (2 if 'starmoss' in keys else 1)


def preview(game, keys):
    """What the chosen herbs would make, as far as you know their properties."""
    if keys == ['starmoss']:
        return 'Starlight Elixir' if 0 in game.player.__dict__.get('herb_props', {}).get('starmoss', ()) else '?'
    plain = [k for k in keys if k != 'starmoss']
    if len(plain) < 2:
        return ''
    count, unknown = {}, False
    for k in plain:
        for pr in FG.props_known(game, k):
            if pr == '?':
                unknown = True
            else:
                count[pr] = count.get(pr, 0) + 1
    known = [pr for pr in FG.PROPS if count.get(pr, 0) >= 2]
    if known:
        return 'shares ' + ', '.join(known) + (' and perhaps more' if unknown else '')
    return 'shares nothing you know of' if unknown else 'shares nothing: a ruined brew'


# ------------------------------------------------------------------ the brew
def name_of(it):
    props = getattr(it, 'props', [])
    if it.t == 'starlight':
        return 'Starlight Elixir'
    s = getattr(it, 'q', 1)
    lead = 'Weak ' if s <= 2 else 'Strong ' if s >= 7 else 'Potent ' if s >= 10 else ''
    lead = 'Potent ' if s >= 10 else lead
    if it.t == 'flask':
        return f'{lead}Sleeping Flask'
    words = [WORD[pr] for pr in props]
    what = ' and '.join(words) if len(words) <= 2 else ', '.join(words[:-1]) + ' and ' + words[-1]
    tinct = 'Tincture' if getattr(it, 'long', False) else 'Draught'
    return f'{lead}{what} Oil' if it.t == 'oil' else f'{lead}{tinct} of {what}'


def brew(game, keys, use_spirit=False):
    """Into the kettle with them. Returns the turns it took (0 if nothing happened)."""
    from .entities import Item
    p = game.player
    keys = list(dict.fromkeys(keys))              # each herb once: two of the same share nothing new
    if not keys:
        return 0
    r = LS.rank(game, 'alchemy')
    for k in keys:
        if herb_rank(k) > r and k != 'starmoss':
            game.msg(f'{FG.PLANTS[k][0]}: too hard for you yet (Alchemy {herb_rank(k)}).', 'bad')
            return 0
    items = []
    for k in keys:
        it = next((i for i in p.inv if i.k == 'plant' and i.t == k), None)
        if it is None:
            game.msg('You do not have those herbs.', 'bad')
            return 0
        items.append(it)
    for it in items:
        game.remove_one(it)
    sp = spirit(game) if use_spirit else None
    if sp:
        game.remove_one(sp)
    if keys == ['starmoss']:
        out = Item(game.new_id(), 'draught', 'starlight')
        out.props, out.q, out.long = [], 10, False
        FG.learn_prop(game, 'starmoss', 0)
        game.add_to_inv(out) or game.spill(game.map, p.x, p.y, out)
        game.msg('The starmoss dissolves into a liquid that holds its own light: a Starlight Elixir.', 'unique')
        LS.gain(game, 'alchemy', 10, at=30, what='starlight')
        return 10
    if len([k for k in keys if k != 'starmoss']) < 2:
        game.msg('A brew wants two herbs at least.', 'bad')
        return 0
    props, triple = shared(keys)
    at = max(herb_rank(k) for k in keys if k != 'starmoss')
    if not props:
        game.msg('The herbs share nothing. The brew turns to a brown sludge: ruined.', 'bad')
        LS.gain(game, 'alchemy', .5, at=at)
        return 10
    if random.random() < max(.03, .22 - r * .02):
        game.msg('The brew boils over and blackens. Ruined.', 'bad')
        LS.gain(game, 'alchemy', 1, at=at)
        return 10
    form, props = form_of(props)
    out = Item(game.new_id(), 'draught', form)
    out.props, out.q, out.long = props, strength(game, keys, triple), bool(sp)
    for k in keys:
        FG.learn_prop(game, k, 0, True)
        FG.learn_prop(game, k, 1, True)
    game.add_to_inv(out) or game.spill(game.map, p.x, p.y, out)
    game.msg(f'You brew {name_of(out)}.', 'good')
    LS.gain(game, 'alchemy', 2 + at / 10, at=at, what=form + ':' + '+'.join(props))
    from .gods import on_craft
    on_craft(game, 'brew')
    return 10


# ------------------------------------------------------------------ using it
def turns(it, base):
    return base * (2 if getattr(it, 'long', False) else 1)


def use(game, it):
    """Drink a draught, oil your weapon, throw a flask. Returns the turns it took."""
    from . import behave as BH
    p = game.player
    s = getattr(it, 'q', 1)
    if it.t == 'starlight':
        if getattr(p, 'starlight', False):
            game.msg('You have had what the stars give. The elixir would do nothing more for you.', 'info')
            return 0
        game.remove_one(it)
        p.starlight = True
        game.clamp_vitals()
        p.life += 5
        game.msg('Starlight runs through your veins. You are more than you were: +5 life, for good.', 'unique')
        return 1
    if it.t == 'flask':
        foes = sorted(game.visible_hostiles(), key=lambda o: max(abs(o.x - p.x), abs(o.y - p.y)))
        foes = [o for o in foes if max(abs(o.x - p.x), abs(o.y - p.y)) <= 6 and game.line_clear(p.x, p.y, o.x, o.y)]
        if not foes:
            game.msg('There is no one in reach to throw it at.', 'info')
            return 0
        o = foes[0]
        game.remove_one(it)
        o.hold = max(getattr(o, 'hold', 0), 2 + s // 2)
        o.frozen = False
        game.flash([(o.x, o.y)], (150, 160, 230), '*', .2)
        game.msg(f'The flask bursts on {o.the()} in a pale cloud. It sinks down, asleep.', 'good')
        return 1
    if it.t == 'oil':
        if not game.eq_item('weapon'):
            game.msg('Oil for a blade: you hold no weapon.', 'info')
            return 0
        game.remove_one(it)
        for pr in it.props:
            k, v = {'Venom': ('oil_venom', 2 + s), 'Flame': ('fire_dmg', 2 * s + 2), 'Silver': ('undead', 15 + 8 * s)}[pr]
            p.buffs = [b for b in p.buffs if b[0] != k] + [[k, v, turns(it, 80), f'{WORD[pr]} Oil']]
        game.msg('You work the oil into the edge of your weapon.', 'good')
        return 3
    game.remove_one(it)
    st = game.stats()
    long = turns(it, 150)

    def buff(k, v, label):
        p.buffs[:] = [b for b in p.buffs if b[0] != k] + [[k, v, long, label]]
    for pr in it.props:
        if pr == 'Heal':
            game.heal(6 + 7 * s, True)
        elif pr == 'Mana':
            p.mana = min(st['max_mana'], p.mana + 5 + 6 * s)
        elif pr == 'Stamina':
            p.stamina = min(st['max_stamina'], getattr(p, 'stamina', 0) + round(st['max_stamina'] * min(1, .25 + .1 * s)))
        elif pr == 'Regen':
            buff('regen', 1 + s // 3, 'Renewal')
        elif pr in ('Cure', 'Staunch'):
            p.poison = None
            if pr == 'Cure':
                BH.cure(game, ('diseased', 'confused', 'slowed', 'weakened'))
            else:
                game.heal(2 * s, True)
        elif pr.startswith('Ward'):
            k = {'Ward Fire': 'res_fire', 'Ward Cold': 'res_cold', 'Ward Poison': 'res_poison'}[pr]
            buff(k, 10 + 5 * s, WORD[pr])
        elif pr == 'Sight':
            buff('seeall', 1, 'True Sight')
        elif pr == 'Calm':
            buff('calm', 1, 'Calm')
        elif pr == 'Swift':
            buff('swift', 1, 'Swiftness')
            buff('dex', s, 'Swiftness')
        elif pr == 'Strength':
            buff('str', 2 * s, 'Strength')
    game.msg(f'You drink the {name_of(it).lower()}.', 'good')
    return 1


def oil_hit(game, mon):
    """A venom oil on your blade: the blow poisons."""
    b = next((b for b in game.player.buffs if b[0] == 'oil_venom'), None)
    if b and mon in game.map.mons:
        mon.effects['poison'] = [4, max(1, b[1])]


def sees_hidden(game):
    return any(b[0] == 'seeall' for b in game.player.buffs)


# ------------------------------------------------------------------ the item
def display(game, it):
    return name_of(it)


def lines(game, it):
    if it.t == 'starlight':
        return ['Drink it: +5 life, for good. Once in a hero\'s life.']
    if it.t == 'flask':
        return ['Throw it (Enter) at the nearest foe within six steps: it falls asleep for a few turns.']
    out = [', '.join(WHAT[pr] for pr in it.props) + '.']
    if it.t == 'oil':
        out.append('Use it (Enter) to oil your weapon: it lasts a while.')
    if getattr(it, 'long', False):
        out.append('A tincture, in strong spirits: it lasts twice as long.')
    return out


def value(game, it):
    return 4 + getattr(it, 'q', 1) * 3 * max(1, len(getattr(it, 'props', [])))


def glyph(it):
    return '!'


def color(it):
    return COL.get(it.t, (190, 140, 230))
