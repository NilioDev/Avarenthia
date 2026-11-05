"""The belt (round 42, "The belt and the tally" in docs/plan.md): potions in four grades and the pockets you drink from.

- Grades: Minor, plain, Greater, Superior, for health and for mana (Rejuvenation and the Antidote stay as they are).
- Pockets come from the belt slot: none 2, a sash 3, a belt or plated belt 4; a rare belt's "+1 pocket" to 5.
- Each pocket holds one kind and grade, up to 3. A pocket's potions are the potions in the pack it has a claim on: the
  pack holds them all, the belt says how many of each are at hand. A new potion goes into a pocket of its kind, else
  an empty one; an empty pocket fills from the pack once no foe is in sight.
- Drinking from the belt takes a turn; from the pack three (you rummage), and a new foe or a blow breaks it off.
State on the player: `p.belt` = [[potion type or None, how many], ...]."""
from . import data as D

# type: (family, grade 0-3, share of the most, plus)
GRADE = {'hp_minor': ('hp', 0, .25, 5), 'hp': ('hp', 1, .45, 10), 'hp_greater': ('hp', 2, .60, 20),
         'hp_superior': ('hp', 3, .80, 30),
         'mp_minor': ('mp', 0, .30, 5), 'mp': ('mp', 1, .50, 8), 'mp_greater': ('mp', 2, .65, 15),
         'mp_superior': ('mp', 3, .80, 25)}
GRADE_NAME = ['Minor', '', 'Greater', 'Superior']
HOLD = 3
RUMMAGE = 3


def family(t):
    return GRADE[t][0] if t in GRADE else t


def heal_of(game, t):
    """(life, mana) a potion of this type gives."""
    s = game.stats()
    if t in GRADE:
        fam, _g, share, plus = GRADE[t]
        n = round((s['max_life'] if fam == 'hp' else s['max_mana']) * share) + plus
        return (n, 0) if fam == 'hp' else (0, n)
    if t == 'rejuv':
        return round(s['max_life'] * .4) + 10, round(s['max_mana'] * .4) + 8
    if t == 'cure':
        return 10, 0
    return 0, 0


def pockets(game):
    """How many pockets your belt slot gives."""
    it = game.eq_item('belt')
    n = 2
    if it is not None and not (getattr(it, 'mdur', 0) and it.dur <= 0):
        n = 3 if it.base.startswith('sash') else 4
        if it.identified:
            n += sum(v for st, v in it.aff if st == 'pocket')
    return min(5, n)


def state(game):
    p = game.player
    b = p.__dict__.setdefault('belt', [])
    n = pockets(game)
    while len(b) < n:
        b.append([None, 0])
    del b[n:]
    return b


def in_pack(game, t):
    return game.count('potion', t)


def sync(game):
    """Keep every pocket's claim within what the pack holds."""
    b = state(game)
    left = {}
    for pk in b:
        t = pk[0]
        if t is None:
            pk[1] = 0
            continue
        have = left.setdefault(t, in_pack(game, t))
        pk[1] = max(0, min(pk[1], have, HOLD))
        left[t] = have - pk[1]
        if pk[1] == 0 and have == 0:
            pk[0] = None
    return b


def free_of(game, t):
    """Potions of this type in the pack that no pocket holds."""
    b = sync(game)
    return in_pack(game, t) - sum(pk[1] for pk in b if pk[0] == t)


def put(game, t, n):
    """n potions of type t go to the belt: a pocket of their kind, else an empty one. Returns how many went."""
    if n <= 0:
        return 0
    b = sync(game)
    went = 0
    for pk in b:
        if pk[0] == t and pk[1] < HOLD and n:
            k = min(HOLD - pk[1], n)
            pk[1] += k
            n -= k
            went += k
    for i, pk in enumerate(b):
        if pk[0] is None and n:
            k = min(HOLD, n)
            pk[0], pk[1] = t, k
            n -= k
            went += k
            if i > 0:
                from . import guide as GDE
                GDE.tip(game, 'belt')
    return went


def gain(game, it):
    """After a potion went into the pack: to the belt if there is room."""
    if it.k == 'potion':
        put(game, it.t, min(it.n, free_of(game, it.t)))


def refill(game):
    """Once no foe is in sight: empty room in the pockets fills from the pack, kind by kind."""
    b = sync(game)
    for pk in b:
        if pk[0] is not None and pk[1] < HOLD:
            k = min(HOLD - pk[1], free_of(game, pk[0]))
            pk[1] += max(0, k)
    seen = {pk[0] for pk in b}
    for it in game.player.inv:
        if it.k == 'potion' and it.t not in seen and any(pk[0] is None for pk in b):
            put(game, it.t, free_of(game, it.t))
            seen.add(it.t)


def take(game, t):
    """Take one potion of type t from a pocket: True when the belt had one (it is still in the pack until drunk)."""
    b = sync(game)
    for pk in reversed(b):
        if pk[0] == t and pk[1] > 0:
            pk[1] -= 1
            return True
    return False


def choose(game, fam):
    """Q and W: the potion of this family to drink. From the belt first: the smallest grade that fills what you miss,
    the largest if none does; Rejuvenation last. Returns (type, on the belt?) or None."""
    p = game.player
    s = game.stats()
    miss = (s['max_life'] - p.life) if fam == 'hp' else (s['max_mana'] - p.mana)
    b = sync(game)

    def best(types):
        grades = sorted((GRADE[t][1], t) for t in types if t in GRADE and GRADE[t][0] == fam)
        if not grades:
            return None
        fills = [t for _g, t in grades if sum(heal_of(game, t)) >= miss]
        return fills[0] if fills else grades[-1][1]
    on_belt = {pk[0] for pk in b if pk[0] and pk[1] > 0}
    t = best(on_belt)
    if t:
        return t, True
    if 'rejuv' in on_belt:
        return 'rejuv', True
    t = best({it.t for it in p.inv if it.k == 'potion'})
    if t:
        return t, False
    if in_pack(game, 'rejuv'):
        return 'rejuv', False
    return None


def rummage(game):
    """Two turns spent looking through the pack before the third drinks; a new foe in sight or a blow breaks it
    off. True when you found it."""
    p = game.player
    for _ in range(RUMMAGE - 1):
        seen = {id(o) for o in game.visible_hostiles()}
        life = p.life
        game.end_turn(1)
        if game.dead:
            return False
        new = any(id(o) not in seen for o in game.visible_hostiles())
        if new or p.life < life:
            game.msg('You stop rummaging in your pack: ' + ('something comes into sight.' if new else 'a blow!'), 'bad')
            return False
    return True


def name(t):
    """The short name for the belt on the panel: the grade and the kind, without "Potion"."""
    n = D.POTIONS[t]['name'] if t in D.POTIONS else t
    return n.replace(' Potion', '')


def rows(game):
    """For the panel: (number, type or None, how many) per pocket."""
    return [(i + 1, pk[0], pk[1]) for i, pk in enumerate(sync(game))]
