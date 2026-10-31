"""The gods of the vale: a small pantheon. Every temple, monastery and wayside shrine belongs to one of them.

You may devote yourself to one god at a temple of theirs. Your god grows fond of you through prayer, offerings
and deeds that please them, and blesses you in return. But faith has a price: the followers of rival gods
trust you less, and the priests of a god opposed to yours will not tend to you."""
import random

GODS = {
    'solmara': dict(name='Solmara', title='the Dawnmother', fg=(250, 226, 150), domain='light, healing and mercy',
                    likes='destroying the undead and the servants of the dark',
                    bless=('Her warmth keeps you on your feet (+6 life)', 'Her light shields you (+14 life)')),
    'valdric': dict(name='Valdric', title='the Iron Judge', fg=(190, 200, 230), domain='law, oaths and rightful kings',
                    likes='bringing outlaws and bandits to justice',
                    bless=('His oath hardens your skin (+3 armour)', 'His judgement is your shield (+8 armour)')),
    'thessa': dict(name='Thessa', title='the Green Mother', fg=(140, 210, 110), domain='harvest, beasts and the wild places',
                   likes='living off the land: foraging, herbs and fishing',
                   bless=('Her green breath clears your mind (+6 mana)', 'The wild sings through you (+14 mana)')),
    'durnak': dict(name='Durnak', title='the Deep Smith', fg=(230, 150, 90), domain='the forge, stone and the honoured dead',
                   likes='clearing the deep places of kobolds, goblins and worse',
                   bless=('Your blows ring like his hammer (+1 damage)', 'Your blows fall like his hammer (+3 damage)')),
    'skell': dict(name='Skell', title='the Grey Wanderer', fg=(200, 190, 160), domain='luck, roads, trade and thieves',
                  likes='trade on the roads and coin well spent',
                  bless=('Luck is on your side (+3% critical)', 'Fortune loves you (+7% critical)')),
    'morrak': dict(name='Morrak', title='the Hollow King', fg=(170, 90, 200), domain='death, night and endless hunger',
                   likes='blood', bless=('', '')),
}
GOD_ORDER = ['solmara', 'valdric', 'thessa', 'durnak', 'skell', 'morrak']
# old enmities between the faiths
OPPOSED = {frozenset(p) for p in (('solmara', 'morrak'), ('valdric', 'skell'), ('thessa', 'durnak'), ('valdric', 'morrak'),
                                  ('thessa', 'morrak'), ('durnak', 'morrak'), ('skell', 'morrak'))}
FRIENDS = {frozenset(p) for p in (('solmara', 'valdric'), ('solmara', 'thessa'), ('valdric', 'durnak'))}
# which god each faction holds dear
PATRON = {'crown': 'valdric', 'league': 'skell', 'circle': 'thessa', 'clan': 'durnak', 'horde': 'morrak',
          'blackhand': 'skell', 'cult': 'morrak'}
TIERS = [(0, 'noticed'), (10, 'favoured'), (30, 'chosen')]
DEVOTABLE = ['solmara', 'valdric', 'thessa', 'durnak', 'skell']

UNDEAD = {'skeleton', 'skarcher', 'zombie', 'ghost', 'wraith', 'lich', 'drowned', 'drowned_king', 'cultist'}
from .menagerie import UNDEAD as _UND
UNDEAD |= _UND | {'keening_woman', 'vampire_count'}
OUTLAWS = {'bandit', 'brigand', 'raider', 'robber_knight'}
DEEP = {'kobold', 'goblin', 'gobarcher', 'troll', 'ogre', 'grolm', 'snagtooth', 'spider'}


def opposed(a, b):
    return bool(a and b and frozenset((a, b)) in OPPOSED)


def friends(a, b):
    return bool(a and b and (a == b or frozenset((a, b)) in FRIENDS))


def tier(favor):
    """0, 1 or 2."""
    t = 0
    for i, (n, _w) in enumerate(TIERS):
        if favor >= n:
            t = i
    return t


def standing(game):
    p = game.player
    god = getattr(p, 'god', None)
    if not god:
        return 'You follow no god.'
    g = GODS[god]
    return f"{g['name']}, {g['title']}: {TIERS[tier(p.favor)][1]} ({int(p.favor)})"


def temple_god(game, m=None):
    """Whose temple is this map (or the temple in this town)?"""
    m = m or game.map
    w = game.world
    site = getattr(m, 'site', None)
    if site is not None:
        st = w.sites[site]
        if getattr(st, 'god', None) is None:
            rnd = random.Random(st.id * 7919 + 13)
            st.god = 'solmara' if site == getattr(w, 'start_temple', None) else rnd.choice(
                ['solmara', 'solmara', 'valdric', 'thessa', 'durnak'] if st.kind == 'temple' else ['solmara', 'thessa', 'durnak', 'valdric'])
        return st.god
    sid = getattr(m, 'sid', None)
    if sid is not None:
        s = w.settlements[sid]
        if getattr(s, 'god', None) is None:
            rnd = random.Random(s.id * 104729 + 7)
            if s.kind == 'deephold':
                s.god = 'durnak'
            elif s.id == 0:
                s.god = 'solmara'
            else:
                pat = PATRON.get(s.faction)
                s.god = pat if pat and rnd.random() < .6 else rnd.choice(['solmara', 'solmara', 'valdric', 'thessa', 'skell'])
        return s.god
    return 'solmara'


def apply(game, s):
    """Add your god's blessing to derived stats."""
    p = game.player
    god = getattr(p, 'god', None)
    if not god or god == 'morrak':
        return
    t = tier(p.favor)
    if t == 0:
        return
    k = t - 1
    if god == 'solmara':
        s['life'] += (6, 14)[k]
    elif god == 'valdric':
        s['armor'] += (3, 8)[k]
    elif god == 'thessa':
        s['mana'] += (6, 14)[k]
    elif god == 'durnak':
        s['dmg_flat'] += (1, 3)[k]
    elif god == 'skell':
        s['crit'] += (3, 7)[k]


def gain(game, amount, why=''):
    p = game.player
    if not getattr(p, 'god', None):
        return
    before = tier(p.favor)
    p.favor = min(100, p.favor + amount)
    after = tier(p.favor)
    if after > before:
        g = GODS[p.god]
        game.msg(f"{g['name']} is pleased with you. You are {TIERS[after][1]}: {g['bless'][after - 1]}.", 'gold')
        game.clamp_vitals()


def lose(game, amount, why=''):
    p = game.player
    if getattr(p, 'god', None):
        p.favor = max(0, p.favor - amount)
        if why:
            game.msg(why, 'bad')


def on_kill(game, mon):
    god = getattr(game.player, 'god', None)
    if not god or mon.is_npc:
        return
    k = mon.k
    if god == 'solmara' and k in UNDEAD:
        gain(game, 1.5)
    elif god == 'valdric' and k in OUTLAWS:
        gain(game, 1.5)
    elif god == 'durnak' and k in DEEP:
        gain(game, 1)
    elif god == 'thessa' and k in ('wolf', 'jackal', 'bat', 'rat') and random.random() < .5:
        lose(game, .5)


def on_craft(game, kind):
    """Thessa likes foraging, fishing and herbs; Skell likes trade."""
    god = getattr(game.player, 'god', None)
    if god == 'thessa' and kind in ('forage', 'fish', 'herb'):
        gain(game, .3)
    elif god == 'skell' and kind == 'trade':
        gain(game, .8)


def devote(game, god):
    """Swear yourself to a god. The faithful of rival gods take note."""
    from . import data as D
    p = game.player
    old = getattr(p, 'god', None)
    p.god, p.favor = god, 3
    g = GODS[god]
    game.msg(f"You kneel and swear yourself to {g['name']}, {g['title']}.", 'gold')
    if old and old != god:
        game.msg(f"{GODS[old]['name']} turns away from you.", 'bad')
    for fk, f in D.FACTIONS.items():
        pat = PATRON.get(fk)
        if not pat:
            continue
        if pat == god:
            p.rep[fk] = p.rep.get(fk, 0) + 8
        elif opposed(pat, god):
            p.rep[fk] = p.rep.get(fk, 0) - 10
            game.msg(f"The followers of {GODS[pat]['name']} in {f['name']} will not like this.", 'bad')
    game.clamp_vitals()


def pray(game, temple):
    """Pray at a temple or shrine of `temple`. Returns what the priest (or the silence) says."""
    p = game.player
    god = getattr(p, 'god', None)
    tg = GODS[temple]
    if not god:
        return f'"Pray, then. {tg["name"]} hears everyone, though answers only {tg["name"].endswith("a") and "her" or "his"} own."'
    if god != temple:
        if opposed(god, temple):
            return f'You cannot bring yourself to pray to {tg["name"]}. Your own god would not forgive it.'
        return f'You say a quiet prayer to {tg["name"]}. It is polite, but {GODS[god]["name"]} is your god.'
    if getattr(p, 'prayed_day', -1) == game.day:
        return 'You pray again. The candles flicker. You have been heard already today.'
    p.prayed_day = game.day
    gain(game, 3)
    t = tier(p.favor)
    if t >= 1:
        s = game.stats()
        p.life, p.mana, p.poison = s['max_life'], s['max_mana'], None
        return f'You pray to {tg["name"]}. A deep calm fills you, and your wounds close.'
    return f'You pray to {tg["name"]}. For a moment you feel watched over.'


def offering(game, amount=100):
    p = game.player
    if p.gold < amount:
        return False
    p.gold -= amount
    if getattr(p, 'god', None):
        gain(game, 2 * amount / 100)
    return True
