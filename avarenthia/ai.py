"""How monsters fight. Beyond walking up and hitting you, each kind has its own habits:

coward   runs when badly hurt, and comes back when it has licked its wounds
pack     hunts together: they spread out and come at you from different sides
kite     archers and gunners back off when you close in, to shoot again
lurk     waits unseen in the dark until you are nearly on top of it
howl     wakes the rest of the pack (and anything else nearby) with a howl
berserk  goes into a rage when wounded: hits much harder
healer   patches up hurt friends
charge   lowers its head, then thunders at you in a straight line
wander   does not sleep: drifts about the place until it finds you"""
import random

from . import data as D
from .worldgen import cheb

TRAITS = {
    'coward': {'rat', 'kobold', 'goblin', 'gobarcher', 'jackal', 'bandit', 'brigand', 'merchant', 'deputy'},
    'pack': {'jackal', 'wolf', 'kobold', 'goblin', 'orc', 'soldier', 'raider', 'bandit', 'mercenary', 'clansman', 'watchman'},
    'kite': {'gobarcher', 'brigand', 'skarcher', 'crossbow', 'warden', 'huntsman', 'thunderer'},
    'lurk': {'spider', 'drowned'},
    'howl': {'wolf', 'jackal'},
    'berserk': {'orc', 'ogre', 'troll', 'raider', 'clansman', 'warlord', 'grolm'},
    'healer': {'cultist', 'druid'},
    'charge': {'ogre', 'troll', 'knight', 'robber_knight', 'drake'},
    'wander': {'bat', 'zombie', 'skeleton', 'ghost', 'rat'},
}
D8 = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
# the new kinds (creatures.py) bring their habits as behaviours; some of them are the old traits
_BEH_TRAIT = {'kite': 'kite', 'rage': 'berserk', 'charge': 'charge', 'burrow': 'lurk', 'ambush': 'lurk', 'hunt': 'wander'}
for _k, _d in D.MONSTERS.items():
    for _b in _d.get('beh', ()):
        if _b in _BEH_TRAIT:
            TRAITS[_BEH_TRAIT[_b]].add(_k)
TRAITS['coward'] |= {'gob_sneak', 'gob_bomber', 'gob_shaman', 'kob_slinger', 'kob_trapper', 'kob_sorcerer', 'hyena', 'locusts'}
TRAITS['pack'] |= {'wolf_spider', 'ant_worker', 'ant_soldier', 'hyena', 'gnoll_hunter', 'hob_legionary', 'lizard_warrior',
                   'viper_warrior', 'orc_berserker', 'deep_orc', 'gob_rider', 'gob_sneak', 'bloodwasp'}
TRAITS['wander'] |= {'ant_worker', 'locusts', 'moth', 'bloodwasp'}


def has(mon, trait):
    return mon.k in TRAITS[trait] and not getattr(mon, 'is_boss', False)


def free(game, x, y):
    m = game.map
    return m.inb(x, y) and D.TILES[m.tile(x, y)].walk and not game.occupied(m, x, y)


def step_away(game, mon):
    """One step that takes it further from you, if there is one."""
    p = game.player
    here = cheb(mon.x, mon.y, p.x, p.y)
    opts = [(cheb(mon.x + dx, mon.y + dy, p.x, p.y), mon.x + dx, mon.y + dy) for dx, dy in D8
            if free(game, mon.x + dx, mon.y + dy)]
    opts = [o for o in opts if o[0] > here]
    if not opts:
        return False
    _d, x, y = max(opts, key=lambda o: (o[0], random.random()))
    mon.x, mon.y = x, y
    return True


def flank_step(game, mon):
    """Pack hunters do not queue up behind each other: each heads for a free spot around you,
    as far as it can from where its friends already stand."""
    m, p = game.map, game.player
    friends = [o for o in m.mons if o is not mon and not o.is_npc and o.awake and cheb(o.x, o.y, p.x, p.y) <= 2]
    spots = [(p.x + dx, p.y + dy) for dx, dy in D8 if free(game, p.x + dx, p.y + dy) or (p.x + dx, p.y + dy) == (mon.x, mon.y)]
    if not spots or not friends:
        return False
    tx, ty = max(spots, key=lambda c: (min(cheb(c[0], c[1], o.x, o.y) for o in friends), -cheb(c[0], c[1], mon.x, mon.y)))
    if (tx, ty) == (mon.x, mon.y):
        return False
    best = None
    for dx, dy in D8:
        nx, ny = mon.x + dx, mon.y + dy
        if free(game, nx, ny) and (nx, ny) != (p.x, p.y):
            d = cheb(nx, ny, tx, ty)
            if best is None or d < best[0]:
                best = (d, nx, ny)
    if best and best[0] < cheb(mon.x, mon.y, tx, ty):
        mon.x, mon.y = best[1], best[2]
        return True
    return False


def on_wake(game, mon):
    """Called when a monster wakes: a howl, or a spider dropping out of the dark."""
    from . import behave as BH
    m = game.map
    if getattr(mon, 'lurk', False):
        mon.lurk = False
        if not BH.on_wake(game, mon):
            game.msg(f"{mon.the()[0].upper() + mon.the()[1:]} drops out of the dark!", 'bad')
            game.flash([(mon.x, mon.y)], (230, 230, 240), '!', .25)
    if has(mon, 'howl') and not getattr(mon, 'howled', False):
        mon.howled = True
        n = 0
        for o in m.mons:
            if not o.is_npc and not o.awake and cheb(o.x, o.y, mon.x, mon.y) <= 14:
                o.awake = True
                n += 1
        game.msg(f"{mon.the()[0].upper() + mon.the()[1:]} howls." + (' Howls answer from the dark.' if n else ''), 'bad')


def asleep(game, mon):
    """A turn for a monster that has not noticed you yet. Returns True if it is still unaware."""
    if has(mon, 'lurk') and not hasattr(mon, 'lurk'):
        mon.lurk = True
    p = game.player
    if getattr(mon, 'lurk', False):
        if cheb(mon.x, mon.y, p.x, p.y) <= 2 and game.visible(mon.x, mon.y):
            mon.awake = True
            on_wake(game, mon)
            return False
        return True
    if has(mon, 'wander') and random.random() < .35:
        game.random_step(mon)
    return None                                 # let the usual waking rules decide


def turn(game, mon, df):
    """Special moves before the usual ones. Returns True if the monster used its turn."""
    p = game.player
    dist = cheb(mon.x, mon.y, p.x, p.y)
    hp = mon.hp / max(1, mon.maxhp)
    name = mon.the()[0].upper() + mon.the()[1:]
    # rage
    if has(mon, 'berserk') and hp < .4 and not getattr(mon, 'enraged', False):
        mon.enraged = True
        mon.dmg = tuple(round(v * 1.4) + 1 for v in mon.dmg)
        game.msg(f'{name} roars and flies into a rage!', 'bad')
        game.flash([(mon.x, mon.y)], (255, 60, 40), '!', .3)
        return True
    # healing a hurt friend
    if has(mon, 'healer') and random.random() < .35:
        hurt = [o for o in game.map.mons if not o.is_npc and o is not mon and o.hp < o.maxhp * .6 and cheb(o.x, o.y, mon.x, mon.y) <= 6]
        if hurt:
            o = min(hurt, key=lambda q: q.hp / max(1, q.maxhp))
            amt = max(2, o.maxhp // 4)
            o.hp = min(o.maxhp, o.hp + amt)
            game.flash([(o.x, o.y)], (120, 240, 140), '+', .3)
            if game.visible(mon.x, mon.y):
                game.msg(f'{name} mutters a prayer. {o.the()[0].upper() + o.the()[1:]} looks better.', 'bad')
            return True
    # running away
    if has(mon, 'coward'):
        if hp < .3:
            if not getattr(mon, 'fleeing', False):
                mon.fleeing = True
                if game.visible(mon.x, mon.y):
                    game.msg(f'{name} turns and runs!', 'info')
            if step_away(game, mon):
                if dist > 6 and random.random() < .3:
                    mon.hp = min(mon.maxhp, mon.hp + 1)         # licking its wounds
                return True
            # cornered: fight like the cornered thing it is
        elif getattr(mon, 'fleeing', False) and hp >= .6:
            mon.fleeing = False
    # the charge: a turn of warning, then a rush in a straight line
    if has(mon, 'charge'):
        aim = getattr(mon, 'charging', None)
        if aim:
            mon.charging = None
            dx, dy = aim
            moved = 0
            for _ in range(6):
                nx, ny = mon.x + dx, mon.y + dy
                if (nx, ny) == (p.x, p.y):
                    game.msg(f'{name} slams into you!', 'bad')
                    game.shake()
                    if random.random() < game.mon_hit_chance(mon, df) + .15:
                        game.hurt(random.randint(*mon.dmg) * 1.6, mon.name)
                    return True
                if not free(game, nx, ny):
                    break
                mon.x, mon.y = nx, ny
                moved += 1
            if moved and game.visible(mon.x, mon.y):
                game.msg(f'{name} thunders past!', 'info')
            return True
        if 3 <= dist <= 6 and game.visible(mon.x, mon.y) and random.random() < .35:
            dx = (p.x > mon.x) - (p.x < mon.x)
            dy = (p.y > mon.y) - (p.y < mon.y)
            if abs(p.x - mon.x) == abs(p.y - mon.y) or p.x == mon.x or p.y == mon.y:      # a straight line
                mon.charging = (dx, dy)
                from . import behave as BH
                if mon.k == 'gob_rider':
                    game.msg(f'{name} levels {BH.his(mon)} spear and spurs {BH.his(mon)} wolf on...', 'bad')
                else:
                    game.msg(f'{name} lowers {BH.his(mon)} head and paws the ground...', 'bad')
                game.flash([(mon.x + dx, mon.y + dy)], (255, 200, 80), '!', .4)
                return True
    # archers back off to shoot again
    if has(mon, 'kite') and dist <= 1 and random.random() < .6:
        if step_away(game, mon):
            return True
    return False


def approach(game, mon):
    """Moving in: pack hunters fan out around you; the rest come straight on."""
    p = game.player
    if has(mon, 'pack') and cheb(mon.x, mon.y, p.x, p.y) <= 4 and flank_step(game, mon):
        return True
    return False
