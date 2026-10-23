"""What you know of each kind of creature, kept on the player: when you first saw one, how many you slew, how many you
skinned. Knowledge grows by killing and skinning (and a library may teach the first step), in three steps shown in
the look line and on the bestiary page: its weakness and resistances, what it carries, its weak spot."""
from . import data as D

STEPS = ((3, 'weakness and resistances'), (10, 'what it carries'), (25, 'its weak spot'))
WEAK_CRIT = 10                  # a better chance of a critical hit once you know where to strike
ELEM_NAME = {'fire': 'fire', 'cold': 'cold', 'lightning': 'lightning', 'poison': 'poison'}
SPOT = {'beast': 'the throat', 'spider': 'the joint where the legs meet', 'insect': 'between the plates',
        'aberration': 'the eyes', 'undead': 'the spine', 'dragon': 'the soft scales under the jaw',
        'construct': 'the seams', 'ooze': 'the dark core', 'plant': 'the root knot', 'fiend': 'the brow',
        'crawler': 'behind the head', 'worm': 'the ring behind the mouth', 'ant': 'the narrow waist',
        'fey': 'the iron-shy heart'}


def entry(game, k):
    return game.player.bestiary.get(k)


def points(e):
    """Kills and skins together: what you have learnt with your own hands."""
    if not e:
        return 0
    return e[1] + (e[2] if len(e) > 2 else 0)


def step(game, k):
    """0 to 3: how far your knowledge of this kind has come."""
    n = points(entry(game, k))
    return sum(1 for need, _what in STEPS if n >= need)


def note(game, k, before):
    """Say so when a new step is reached."""
    now = step(game, k)
    if now > before:
        game.msg(f"You know the {D.MONSTERS[k]['name'].lower()} better: {STEPS[now - 1][1]}. (V)", 'gold')


def on_skin(game, k):
    if k not in D.MONSTERS:
        return
    e = game.player.bestiary.setdefault(k, [game.day, 0])
    while len(e) < 3:
        e.append(0)
    before = step(game, k)
    e[2] += 1
    note(game, k, before)


def study(game, n=3):
    """A library's books on beasts: the kinds you have met but know little of reach the first step."""
    b = game.player.bestiary
    weak = sorted((k for k in b if points(b[k]) < STEPS[0][0] and not D.MONSTERS[k].get('boss')),
                  key=lambda k: (D.MONSTERS[k].get('min_l', 1), k))[:n]
    for k in weak:
        e = b[k]
        while len(e) < 3:
            e.append(0)
        e[2] += STEPS[0][0] - points(e)
    return [D.MONSTERS[k]['name'] for k in weak]


def crit_bonus(game, mon):
    return WEAK_CRIT if not mon.is_npc and step(game, mon.k) >= 3 else 0


# ------------------------------------------------------------------ the words for each step
def resists(k):
    """'resists cold; weak to fire' or ''."""
    res = D.MONSTERS[k].get('res') or {}
    strong = [ELEM_NAME[e] + (' (immune)' if v >= 100 else '') for e, v in res.items() if v > 0 and e in ELEM_NAME]
    weak = [ELEM_NAME[e] for e, v in res.items() if v < 0 and e in ELEM_NAME]
    parts = ([('resists ' + ', '.join(strong))] if strong else []) + ([('weak to ' + ', '.join(weak))] if weak else [])
    return '; '.join(parts)


def carries(k):
    """What it carries: the gear its kind uses, and what a skinner takes from it."""
    from . import hunting as HT
    out = []
    uses = D.GEAR_USERS.get(k)
    if uses:
        names = []
        for f in uses:
            b = D.BASES.get(D.grades(f)[0])
            if b and b['name'].lower() not in names:
                names.append(b['name'].lower() if f not in ('ring', 'amulet') else f + 's')
        out.append('gear: ' + ', '.join(names[:6]) + (' and more' if len(names) > 6 else ''))
    sk = HT.SKINS.get(k)
    if sk:
        what = [sk[2].lower()] if sk[2] else []
        what += [HT.PARTS[p][0].lower() for p, _c in sk[4] if p in HT.PARTS]
        if sk[0]:
            what.append('meat')
        out.append('skinned: ' + ', '.join(what))
    return '; '.join(out) or 'nothing of use'


def weak_spot(k):
    fam = D.MONSTERS[k].get('family')
    where = SPOT.get(fam, 'the gap in its guard')
    return f'You know to strike at {where}: +{WEAK_CRIT}% chance of a critical hit.'


def look_lines(game, k):
    """The lines the look line adds for what you know (step 1 and up)."""
    s = step(game, k)
    out = []
    lore = D.LORE.get(k)
    if s >= 1:
        r = resists(k)
        out.append((lore[2] if lore else 'No weakness known.') + (f' It {r}.' if r else ''))
    if s >= 2:
        out.append('Carries ' + carries(k) + '.')
    if s >= 3:
        out.append(weak_spot(k))
    return out
