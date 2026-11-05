"""Marked creatures (round 45, "Marked creatures" in docs/plan.md): one list of twenty affixes for champions (blue),
uniques (gold) and the named enemies, each fitting certain kinds, likelier by place and season, and each with an
answer the player already owns. The full table: project files `monsters/affixen.md`.

A champion has one affix (from level 15 sometimes two), a unique two or three and a name in the named enemies' style.
The affixes stand in `mon.mods`; the look line gives their sentence (TEXT)."""
import random

from . import data as D

AFFIXES = ['Venomous', 'Frost-touched', 'Fire-blooded', 'Stone Skin', 'Thorny', 'Vampiric', 'Regenerating', 'Swift',
           'Blink', 'Summoner', 'Splitting', 'Multishot', 'Berserk', 'Shielded', 'Cursing', 'Warcry',
           'Brutal', 'Warded', 'Ember-hearted', 'Grave-bound']
OLD = {'Fast': 'Swift', 'Extra Strong': 'Brutal', 'Fire Enchanted': 'Fire-blooded'}     # the names before round 45
TEXT = {'Venomous': 'its blows poison', 'Frost-touched': 'its touch is cold and slows you', 'Fire-blooded': 'it burns',
        'Stone Skin': 'its hide turns blades', 'Thorny': 'it cuts whoever strikes it', 'Vampiric': 'it heals as it wounds',
        'Regenerating': 'its wounds close by themselves, unless fire or acid stops them',
        'Swift': 'it is quick', 'Blink': 'it steps through the air',
        'Summoner': 'it calls its kin', 'Splitting': 'cut it and it splits', 'Multishot': 'it looses two shots at once',
        'Berserk': 'it rages when hurt', 'Shielded': 'it turns the first blows aside', 'Cursing': 'it curses',
        'Warcry': 'its war cry drives its band on', 'Brutal': 'it hits half again as hard',
        'Warded': 'it shrugs off {school}', 'Ember-hearted': 'where it dies the ground burns',
        'Grave-bound': 'it rises once more, unless the body is burnt or hallowed'}
WARD = {'fire': 'Fire Magic', 'cold': 'Frost Magic', 'lightning': 'Storm Magic', 'holy': 'Restoration'}
PEOPLE = {'orc', 'goblin', 'kobold', 'hobgoblin', 'gnoll', 'lizardfolk', 'viperkin', 'seafolk', 'hag'}
SUMMON = {'wolf': 'wolf', 'hyena': 'hyena', 'goblin': 'goblin', 'kobold': 'kobold', 'orc': 'orc', 'gnoll': 'gnoll',
          'spider': 'spider', 'skeleton': 'skeleton', 'zombie': 'zombie', 'rat': 'rat', 'bat': 'bat'}
MAGIC = ('Swift', 'Vampiric', 'Frost-touched', 'Regenerating', 'Multishot', 'Fire-blooded', 'Warded', 'Ember-hearted',
         'Blink')


def people(k):
    from . import named as NM
    d = D.MONSTERS[k]
    return k in NM.RACE or d.get('family') in PEOPLE or d['ch'] in '@☺'


def undead(k):
    return k in D.UNDEAD or D.MONSTERS[k].get('family') == 'undead'


def leader(k):
    d = D.MONSTERS[k]
    return bool(d.get('chief')) or any(w in k for w in ('chief', 'boss', 'captain', 'lord', 'king', 'queen', 'matriarch'))


def fits(k, a):
    """Whether this affix belongs to this kind."""
    d = D.MONSTERS[k]
    if a == 'Multishot':
        return bool(d.get('ranged'))
    if a == 'Splitting':
        return not people(k) and not undead(k) and d.get('family') not in ('construct', 'dragon')
    if a == 'Warcry':
        return leader(k) or people(k) and random.random() < .2
    if a == 'Grave-bound':
        return undead(k)
    if a == 'Summoner':
        return k in SUMMON or any(s in k for s in SUMMON)
    if a == 'Venomous':
        return not undead(k) and d.get('family') not in ('construct',)
    if a == 'Vampiric':
        return d.get('family') not in ('construct', 'plant', 'ooze')
    return True


def weights(game, k, have):
    """The affixes this kind may take, weighed by place, region and season."""
    from . import look as LOOK
    cold = fire = False
    try:
        m = game.map
        kind = LOOK.remembered_kind(m) if m.kind != 'over' else None
        fire = kind == 'ash'
        cold = kind == 'cold'
        from . import calendar as CAL
        cold = cold or CAL.season(game.day) == 'winter' or game.world_pos()[1] < game.maps['over'].h // 4
    except Exception:
        pass                                    # the world is still being made
    out = []
    for a in AFFIXES:
        if a in have or not fits(k, a):
            continue
        if a == 'Frost-touched' and 'Fire-blooded' in have or a == 'Fire-blooded' and 'Frost-touched' in have:
            continue
        w = 1.0
        if a == 'Frost-touched':
            w = 3.0 if cold else .5 if fire else 1.0
        if a == 'Fire-blooded':
            w = 3.0 if fire else .5 if cold else 1.0
        out.append((a, w))
    return out


def roll(game, k, n):
    have = []
    for _ in range(n):
        ws = weights(game, k, have)
        if not ws:
            break
        have.append(random.choices([a for a, _w in ws], [w for _a, w in ws])[0])
    return have


def unique_name(k, gender=None):
    """A unique's name in the named enemies' style: "Old Greytooth", "Grukka the Red", "Abbess Morwen the Hollow"."""
    from . import named as NM
    race = NM.RACE.get(k) or {'orc': 'orc', 'goblin': 'goblin', 'kobold': 'kobold', 'hobgoblin': 'hobgoblin',
                              'gnoll': 'gnoll', 'lizardfolk': 'lizard'}.get(D.MONSTERS[k].get('family'))
    if race in NM.NAMES:
        return f"{random.choice(NM.NAMES[race][0 if gender == 'f' else 1])} {random.choice(NM.EPITHET)}"
    if undead(k):
        titles, names = NM.DEAD[gender if gender in NM.DEAD else 'm']
        return f'{random.choice(titles)} {random.choice(names)} {random.choice(NM.DEAD_EPITHET)}'
    if people(k):
        return f"{random.choice(NM.NAMES['human'][1])} {random.choice(NM.EPITHET)}"
    return ('Old ' if random.random() < .5 else '') + random.choice(NM.BEAST_NAME)


def apply(mon, mods):
    """Give a monster its affixes, with what they change at once."""
    mon.mods = list(mods)
    if 'Brutal' in mods:
        mon.dmg = tuple(round(v * 1.5) for v in mon.dmg)
    if 'Stone Skin' in mods:
        mon.df *= 2
        mon.hp = mon.maxhp = round(mon.maxhp * 1.2)
    if 'Shielded' in mods:
        mon.shield = 4
    if 'Warded' in mods:
        mon.warded = random.choice(list(WARD))


def mark(game, mon):
    """A champion or a unique: its affixes (and a unique's name)."""
    if mon.elite == 1:
        n = 2 if mon.lvl >= 15 and random.random() < .3 else 1
    elif mon.elite == 2:
        n = random.choice((2, 2, 3))
        mon.name = unique_name(mon.k, getattr(mon, 'gender', None))
    else:
        return
    apply(mon, roll(game, mon.k, n))


def sentence(mon):
    """The look line's sentence of its marks: "Its blows poison; it is quick." """
    parts = []
    for a in mon.mods:
        a = OLD.get(a, a)
        t = TEXT.get(a)
        if t:
            parts.append(t.format(school=WARD.get(getattr(mon, 'warded', 'fire'), 'Fire Magic')))
    if not parts:
        return ''
    s = '; '.join(parts)
    return s[0].upper() + s[1:] + '.'


def label(mon):
    """For IN SIGHT: "venomous, swift"."""
    return label_of(mon.mods)


def label_of(mods):
    return ', '.join(OLD.get(a, a).lower() for a in mods)


# ------------------------------------------------------------------ in the fight
def turn(game, mon):
    """Berserk, Blink and Summoner for marked creatures that are not named enemies (named.py does its own).
    True when the turn is used."""
    if not mon.mods or getattr(mon, 'named', None) is not None:
        return False
    from .behave import The
    from .worldgen import free_around, cheb
    p, m = game.player, game.map
    hp = mon.hp / max(1, mon.maxhp)
    if 'Berserk' in mon.mods and hp < .4 and not getattr(mon, 'enraged', False):
        mon.enraged = True
        mon.dmg = tuple(round(v * 1.4) + 1 for v in mon.dmg)
        game.msg(f'{The(mon)} flies into a rage!', 'bad')
        return True
    d = cheb(mon.x, mon.y, p.x, p.y)
    if 'Blink' in mon.mods and d >= 3 and random.random() < .15 and getattr(mon, 'awake', True):
        sp = free_around(game, m, p.x, p.y, 1)
        if sp:
            mon.x, mon.y = random.choice(sp)
            game.msg(f'{The(mon)} steps through the air and is beside you!', 'bad')
            return True
    if 'Summoner' in mon.mods and mon.summons < 3 and random.random() < .1 and getattr(mon, 'awake', True):
        kin = next((v for s, v in SUMMON.items() if s in mon.k), None)
        sp = free_around(game, m, mon.x, mon.y, 1)
        if kin and kin in D.MONSTERS and sp:
            from .entities import make_monster
            x, y = random.choice(sp)
            o = make_monster(game, kin, x, y, max(1, mon.lvl - 2))
            o.awake, o.pack = True, mon.pack
            m.mons.append(o)
            mon.summons += 1
            game.msg(f'{The(mon)} calls, and {o.the()} answers!', 'bad')
            return True
    return False


def on_hit(game, mon, elem):
    """Fire or acid stops Regenerating for three turns."""
    if elem in ('fire', 'poison', 'acid'):
        mon.regen_stop = game.turn + 3
    mon.last_elem = elem


def regenerates(game, mon):
    return 'Regenerating' in mon.mods and game.turn >= getattr(mon, 'regen_stop', 0)


def rises(game, mon):
    """Grave-bound: the first death does not hold, unless the last blow was fire or holy, or it fell on hallowed
    ground. True when it rose."""
    if 'Grave-bound' not in mon.mods or getattr(mon, 'risen', False):
        return False
    m = game.map
    if getattr(mon, 'last_elem', None) in ('fire', 'holy') or m.tile(mon.x, mon.y) == D.HALLOWED:
        return False
    mon.risen = True
    mon.hp = max(1, mon.maxhp // 2)
    from .behave import The
    game.msg(f'{The(mon)} falls, and rises again! Burn it or hallow the ground.', 'bad')
    return True


def ember(game, mon):
    """Ember-hearted: the ground burns three by three where it dies."""
    if 'Ember-hearted' not in mon.mods:
        return
    from . import spellmap as SM
    m = game.map
    cells = [(mon.x + dx, mon.y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if m.inb(mon.x + dx, mon.y + dy)]
    if SM.area(game, m, cells, D.BURNING, power=max(2, mon.lvl // 2)):
        game.msg(f'{mon.name} dies, and the ground around it bursts into flame!', 'bad')


def part(game, mon):
    """A slain unique beast may give a part tied to one of its affixes (about a quarter of the time, with a knife)."""
    from . import beastparts as BP
    from . import hunting as HT
    from .named import kind_of, poss
    if mon.elite != 2 or getattr(mon, 'named', None) is not None or random.random() >= .25:
        return None
    kk = kind_of(mon.k)
    ts = [a for a in mon.mods if a in BP.TRAIT_POWER]
    if kk not in BP.WORD or not ts or not HT.has_knife(game):
        return None
    from .entities import Item
    t = random.choice(ts)
    it = Item(game.new_id(), 'npart', t)
    it.beast, it.nid, it.rank, it.src = mon.name, None, 'notable', mon.k
    it.word = random.choice(BP.WORD[kk])
    game.spill(game.map, mon.x, mon.y, it)
    game.msg(f'You take {poss(mon.name)} {it.word} off whole. Whatever is made of it will carry its {t.lower()} nature.',
             'unique')
    return it
