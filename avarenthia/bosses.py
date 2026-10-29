"""Boss fights, the kit (round 15): bosses fight like a turn-based soulslike.

A great blow is announced in the log and the ground it will strike turns dark red; a blow that loads for two or three
turns shows a number that counts down on every tile (red: step out; purple: it can be broken; gold: stand in it).
What is marked is always true, and every marked blow leaves a free tile you can reach in time (checked when it loads).
Small blows come unmarked, as before.

A boss fights in a rhythm drawn from a deck (Gloomhaven): each phase has a beat of roles (k small, V set-up, G great,
Z heaviest, B move, O summon) and a few cards per role; one card is drawn per beat, an empty pile is shuffled again,
and about one beat in five the rhythm breaks. At its thresholds (two thirds and one third, or one half) a blow stops,
and the boss spends its next turn on the phase's trick; a critical hit while it is spent or staggered breaks through.
After its heaviest blow it stands spent; breaks and hits with its weakness fill three dots and stagger it. Its
resolve shrugs off the first two holds. Helpers come with a job (warder, mender, channeler, guard, swarm). End
bosses wait behind a veil of mist; the room shuts at the first blow, with one hard way out, a rotten wall. Fled from,
a boss heals and makes ready against you, up to four times.

State: `mon.bs` (a kit boss), `mon.cast` (any boss loading a marked blow), `m.arena` (the boss's room)."""
import random

from . import data as D
from .worldgen import cheb, free_around

RED, PURPLE, GOLDN = (255, 104, 80), (206, 132, 255), (255, 214, 90)
MARK_BG, MARK_HOT = (88, 18, 16), (140, 30, 22)
ROMAN = ('I', 'II', 'III', 'IV')
JOBS = {'warder': 'warding', 'mender': 'mending', 'channeler': 'channelling', 'guard': 'guarding',
        'swarm': 'swarming', 'bearer': 'bearing'}
D8 = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1))
RESOLVE = 2
MAX_PREP = 4

# ------------------------------------------------------------------ the moves
# role: k small, V set-up, G great, Z heaviest, B move, O summon. A shaped move loads `load` turns and strikes the
# marked cells with `power` (a share of your full life at the boss's level). brk: it can be broken (default: a load
# of two or more). fx: what it does besides the blow. say: the announcement; hit: when it strikes you.
MOVES = {
    'jab': dict(role='k', name='Spear Jab', kind='melee'),
    'claw': dict(role='k', name='Claw', kind='melee'),
    'touch': dict(role='k', name='Grave Touch', kind='melee'),
    'bone_spear': dict(role='k', name='Bone Spear', kind='bolt'),
    'snare_line': dict(role='V', name='Snare Line', kind='snares',
                       say='{name} scatters snares across the floor, three in a row.'),
    'bone_prison': dict(role='V', name='Bone Prison', kind='prison',
                        say='{name} points at you. Bones burst from the floor all round you!'),
    'grave_mist': dict(role='V', name='Grave Mist', shape='circle', r=2, at='aim', load=1, power=.12, elem='cold',
                       fx=dict(sick=10), say='{name} breathes out a grey mist that crawls along the floor...',
                       hit='The grave mist sinks into you. Your wounds will not close.'),
    'wing_buffet': dict(role='V', name='Wing Buffet', shape='cone', len=3, load=1, power=.1, fx=dict(push=3),
                        say='{name} spreads {his} wings wide...', hit='A blast from the great wings throws you back!'),
    'coin_toss': dict(role='G', name='Coin Toss', shape='circle', r=1, at='aim', load=1, brk=False, power=.26, fx=dict(coins=3),
                      say='{name} digs into {his} hoard and swings back a fistful of coins and stones...',
                      hit='Coins and stones crack against your head!'),
    'shield_rush': dict(role='G', name='Shield Rush', shape='line', len=4, load=1, power=.3, fx=dict(rush=1, push=2),
                        say='{name} lowers {his} pot-lid shield and paws the ground...',
                        hit='{name} slams into you behind {his} shield!'),
    'frost_nova': dict(role='G', name='Frost Nova', shape='ring', r=2, load=1, power=.3, elem='cold', fx=dict(hold=2),
                       say='Frost spreads from {name} across the floor...', hit='The frost bursts up and locks you in ice!'),
    'corpse_burst': dict(role='G', name='Corpse Burst', shape='corpses', load=1, power=.32, elem='cold',
                         say='The dead on the floor swell and split...', hit='A corpse bursts beside you in a spray of bone!'),
    'breath': dict(role='G', name='Breath of Fire', shape='cone', len=7, load=1, power=.34, elem='fire', fx=dict(burn=5),
                   say='{name} rears back. Light glows deep in {his} throat...', hit='Fire pours over you!'),
    'breath_follow': dict(role='G', name='Breath of Fire', shape='cone', len=7, load=2, follow=True, brk=False,
                          power=.34, elem='fire', fx=dict(burn=5),
                          say='{name} rears back and turns {his} head after you, fire glowing in {his} throat...',
                          hit='Fire pours over you!'),
    'tail_sweep': dict(role='G', name='Tail Sweep', shape='tail', load=1, power=.3, fx=dict(push=1),
                       say='{name} coils {his} tail...', hit='The great tail sweeps you off your feet!'),
    'dive': dict(role='G', name='Dive', shape='circle', r=1, at='aim', load=2, follow=True, brk=False, power=.36,
                 fx=dict(land=1), say='', hit='{name} drops out of the dark on top of you!'),
    'mark_doom': dict(role='Z', name='Mark of Doom', shape='mark', load=3, power=.5,
                      say='{name} draws a sign in the air, and it burns cold above {aim}. Get out of {his} sight!',
                      hit='The Mark of Doom falls on you!'),
    'blizzard': dict(role='Z', name='Blizzard', shape='room', load=3, power=.45, elem='cold', fx=dict(slow=3),
                     say='{name} rises from the floor. Snow begins to whirl through the tomb. Find cover!',
                     hit='The blizzard tears at you!'),
    'inferno': dict(role='Z', name='Inferno', shape='room', load=3, power=.52, elem='fire', fx=dict(burn=8, pillar=1),
                    say='{name} draws in a breath that empties the cave of air. Get behind the stone!',
                    hit='The inferno rolls over you!'),
    'call_kobolds': dict(role='O', name='Call', kind='call', helpers=(('kobold', 'guard'), ('kob_sorcerer', 'mender')),
                         say='{name} shrieks for help. Kobolds come running!'),
    'raise_dead': dict(role='O', name='Raise Dead', kind='raise', n=3,
                       say='{name} lifts {his} hands. The dead on the floor get up.'),
    'call_drakes': dict(role='O', name='Call Drakes', kind='call', helpers=(('drake', 'channeler'), ('drake', 'guard')),
                        say='{name} roars, and drakes come gliding out of the dark.'),
    'take_wing': dict(role='B', name='Take Wing', kind='wing',
                      say='{name} beats {his} great wings and rises into the dark above you!'),
    # the moves of the other bosses, now announced (round 16 gives them their own kits)
    'nova': dict(role='G', name='Nova', shape='ring', r=2, load=1, power=.25),
    'leap': dict(role='G', name='Leap', shape='circle', r=1, at='aim', load=1, power=.3, fx=dict(land=1)),
}

STANCE = {'k': '{He} watches your hands.', 'V': '{His} eyes go to the floor round your feet.',
          'G': '{He} draws {himself} up.', 'Z': 'Something gathers in {him}, slowly.', 'B': '{He} sets {his} feet.',
          'O': '{His} eyes go to the dark at the edges.'}

# ------------------------------------------------------------------ the kits
KITS = {
    'snagtooth': dict(weak=('cold',), things='hoard', phases=[
        dict(beat='kkG', cards=dict(k=['jab'], G=['coin_toss'])),
        dict(at=.5, beat='kVGO', cards=dict(k=['jab'], V=['snare_line'], G=['shield_rush', 'coin_toss'],
                                            O=['call_kobolds']), trick='call',
             say='{name} bangs {his} pot-lid shield and shrieks. The kobolds answer from the dark!')]),
    'lich': dict(weak=('fire',), things='tomb', phases=[
        dict(beat='kVGk', cards=dict(k=['bone_spear', 'bone_spear', 'touch'], V=['bone_prison'],
                                     G=['grave_mist', 'frost_nova'])),
        dict(at=.66, beat='kOGkZ', cards=dict(k=['bone_spear', 'touch'], O=['raise_dead'],
                                              G=['corpse_burst', 'frost_nova'], Z=['mark_doom']), trick='rise',
             say='{name} lifts {his} arms. All round the tomb the dead begin to stir.'),
        dict(at=.33, beat='kVGkZ', cards=dict(k=['bone_spear', 'touch'], V=['bone_prison', 'grave_mist'],
                                              G=['frost_nova', 'corpse_burst'], Z=['blizzard']), trick='dark',
             say='The grave-lights gutter and go out. {name} is only half there now, a cold shape in the dark.')]),
    'dragon': dict(weak=('cold',), things='lair', phases=[
        dict(beat='kGkVG', cards=dict(k=['claw'], G=['breath', 'tail_sweep'], V=['wing_buffet'])),
        dict(at=.66, beat='kGOkB', cards=dict(k=['claw'], G=['breath_follow', 'tail_sweep'], O=['call_drakes'],
                                              B=['take_wing']), trick='roar',
             say='{name} roars until the cave shakes. Far off in the dark, drakes answer.'),
        dict(at=.33, beat='kGkZ', cards=dict(k=['claw'], G=['breath_follow', 'tail_sweep'], Z=['inferno']),
             trick='burn', say='Fire runs in the cracks of the floor, and stone falls from the roof.')]),
}


def kit(mon):
    return KITS.get(mon.k) if not mon.is_npc else None


def st(mon):
    return mon.__dict__.get('bs')


def on_spawn(game, mon):
    """A kit boss gets its state when it is made."""
    if mon.k in KITS:
        mon.bs = dict(phase=0, pending=None, i=0, piles={}, spent=0, stag=0, dots=0, stun=0, resolve=RESOLVE,
                      seen_hold=0, sil=False, engaged=False, took={}, breaks=0, prep=[], weak_t=-1, fed=0)


def name_of(mon):
    from .behave import The
    return The(mon)


def fill(text, mon, aim=None):
    from .behave import his, him, PRON
    he = PRON[getattr(mon, 'gender', None)][0]
    out = text.replace('{name}', name_of(mon)).replace('{his}', his(mon)).replace('{him}', him(mon))
    out = out.replace('{aim}', aim or 'you').replace('{He}', he.capitalize()).replace('{His}', his(mon).capitalize())
    return out.replace('{himself}', him(mon) + 'self')


def phases(mon):
    k = kit(mon)
    return k['phases'] if k else []


def great_evil(game, mon):
    return any(getattr(e, 'd', {}).get('boss') == mon.k for e in getattr(game.world, 'evils', ()))


# ------------------------------------------------------------------ shapes
def _open(m, x, y):
    return m.inb(x, y) and not D.TILES[m.tile(x, y)].opaque


def clear_line(m, x0, y0, x1, y1):
    """Nothing that blocks sight between the two (creatures do not)."""
    from .engine import line
    return all(_open(m, x, y) for x, y in line(x0, y0, x1, y1)[:-1])


def area(game, mon):
    """The cells a room-wide blow can reach: its arena, or what lies round it."""
    m = game.map
    ar = arena_of(game, mon)
    if ar:
        return set(ar['cells'])
    return {(x, y) for x in range(mon.x - 8, mon.x + 9) for y in range(mon.y - 8, mon.y + 9) if _open(m, x, y)}


def cells_for(game, mon, mv, tx, ty):
    """The cells a shaped move strikes, aimed at (tx, ty)."""
    m = game.map
    shape = mv.get('shape')
    bx, by = mon.x, mon.y
    out = set()
    if shape == 'circle':
        r = mv.get('r', 1)
        out = {(x, y) for x in range(tx - r, tx + r + 1) for y in range(ty - r, ty + r + 1)}
    elif shape == 'ring':
        r = mv.get('r', 2)
        out = {(x, y) for x in range(bx - r, bx + r + 1) for y in range(by - r, by + r + 1) if (x, y) != (bx, by)}
    elif shape in ('line', 'cone'):
        dx, dy = tx - bx, ty - by
        n = max(1, (dx * dx + dy * dy) ** .5)
        ux, uy = dx / n, dy / n
        ln = mv.get('len', 4)
        for x in range(bx - ln, bx + ln + 1):
            for y in range(by - ln, by + ln + 1):
                vx, vy = x - bx, y - by
                d = (vx * vx + vy * vy) ** .5
                if not d or d > ln + .5:
                    continue
                along = vx * ux + vy * uy
                if along <= 0:
                    continue
                side = abs(vx * uy - vy * ux)
                if (shape == 'line' and side <= .75) or (shape == 'cone' and along >= d * .7):
                    out.add((x, y))
    elif shape == 'tail':                                   # the half behind it: where you are not
        dx, dy = tx - bx, ty - by
        for x in range(bx - 2, bx + 3):
            for y in range(by - 2, by + 3):
                if (x, y) != (bx, by) and (x - bx) * dx + (y - by) * dy <= 0:
                    out.add((x, y))
    elif shape == 'room':
        out = {c for c in area(game, mon) if clear_line(m, bx, by, c[0], c[1])}
    elif shape == 'corpses':
        own = area(game, mon)
        for k, x, y, _l in getattr(m, 'slain', ()):
            if (x, y) in own:
                out |= {(x + a, y + b) for a in (-1, 0, 1) for b in (-1, 0, 1)}
    elif shape == 'mark':
        return set()
    out = {c for c in out if _open(m, *c)}
    if shape not in ('room', 'circle', 'corpses'):
        out = {c for c in out if clear_line(m, bx, by, c[0], c[1])}
    return out


def need(game, mon, mv, cells, tx, ty, cap=3):
    """How many steps you need to get out of it (0: you are not in it); None if no free tile lies within `cap`.
    A blow loads at least that long, so there is always a way out in time."""
    m, p = game.map, game.player
    if mv.get('shape') == 'mark':
        safe = lambda c: not clear_line(m, mon.x, mon.y, c[0], c[1]) or m.tile(*c) == D.HALLOWED  # noqa: E731
        start = (tx, ty)
    else:
        if (p.x, p.y) not in cells and (tx, ty) not in cells:
            return 0
        safe = lambda c: c not in cells  # noqa: E731
        start = (p.x, p.y) if (p.x, p.y) in cells else (tx, ty)
    if safe(start):
        return 0
    ar = arena_of(game, mon)
    room = set(map(tuple, ar['cells'])) if ar and ar.get('sealed') else None
    seen, edge = {start}, [start]
    for k in range(1, cap + 1):
        nxt = []
        for x, y in edge:
            for a, b in D8:
                c = (x + a, y + b)
                if c in seen or not m.inb(*c) or not D.TILES[m.tile(*c)].walk or (room and c not in room):
                    continue
                o = m.mon_at(*c)
                if o is not None and o is not mon and not getattr(o, 'ally', False):
                    continue
                seen.add(c)
                if safe(c):
                    return k
                nxt.append(c)
        edge = nxt
    return None


def fair(game, mon, mv, cells, tx, ty):
    """Is there a way out in the turns it loads?"""
    n = need(game, mon, mv, cells, tx, ty, 4 if mv['role'] == 'Z' else 3)
    return n is not None and n <= max(mv.get('load', 1), 3)


# ------------------------------------------------------------------ who it aims at
def aim(game, mon):
    """(who, x, y): who it goes for, by threat (mercs.py)."""
    from . import mercs as MC
    p = game.player
    w = MC.pick(game, mon)
    if w != 'p':
        mc = next((c for c in MC.party(game) if c.who == w and c.body is not None and c.body in game.map.mons), None)
        if mc:
            return mc, mc.body.x, mc.body.y
    return 'p', p.x, p.y


def ref_life(game, lvl, full):
    """What a great blow is measured against: your full life, but no more than a hero of its level has."""
    return min(full, 40 + 10 * lvl)


# ------------------------------------------------------------------ the deck
def beat(game, mon):
    """The role of this beat, and whether the beat moves on after it."""
    bs = st(mon)
    ph = phases(mon)[bs['phase']]
    pat = ph['beat']
    role = pat[bs['i'] % len(pat)]
    if bs.get('wild') and role == 'V':
        role = 'k'                                           # the beast gone wild: no more set-ups
    if bs.get('stolen') and role == 'k' and random.random() < .15:
        return 'Z'
    if bs['i'] and random.random() < .2:                    # the rhythm breaks
        nxt = pat[(bs['i'] + 1) % len(pat)]
        if role == 'k' and nxt in 'GZ':
            bs['i'] += 1
            return nxt
        if role in 'GZV':
            bs['i'] -= 1                                     # an extra small one first
            return 'k'
    return role


def draw(mon, role):
    bs = st(mon)
    if role == 'Z' and bs.get('stolen') and random.random() < .5:
        return bs['stolen']
    ph = phases(mon)[bs['phase']]
    cards = ph['cards'].get(role) or ph['cards']['k']
    pile = bs['piles'].get(role)
    if not pile:
        pile = bs['piles'][role] = list(cards) * (2 if len(cards) < 3 else 1)     # the shuffle card: all back in
        random.shuffle(pile)
    return pile.pop()


# ------------------------------------------------------------------ a boss's turn
def turn(game, mon, df):
    """Before its usual moves. True if it used its turn."""
    if mon.is_npc or not mon.tpl.get('boss'):
        return False
    c = mon.__dict__.get('cast')
    if c:
        _go_on(game, mon, c)
        return True
    bs = st(mon)
    if bs is None:
        return _plain(game, mon)
    if bs.get('pending') is not None:
        _phase(game, mon, bs.pop('pending'), True)
        bs['pending'] = None
        return True
    p = game.player
    if not bs['engaged'] and mon.awake and game.visible(mon.x, mon.y) and cheb(mon.x, mon.y, p.x, p.y) <= 9:
        engage(game, mon)
    role = beat(game, mon)
    mvid = draw(mon, role)
    if do(game, mon, mvid, df):
        bs['i'] += 1
        return True
    if role != 'k':
        mvid = draw(mon, 'k')
    return _small(game, mon, mvid, df)


def _small(game, mon, mvid, df):
    """A small blow by the threat: a bolt, or a blow when it stands beside whom it wants."""
    from . import mercs as MC
    bs = st(mon)
    mv = MOVES[mvid]
    who, tx, ty = aim(game, mon)
    d = cheb(mon.x, mon.y, tx, ty)
    if mv.get('kind') == 'bolt' and 2 <= d <= 8 and 'silence' not in mon.effects:
        if who == 'p':
            if game.mon_shoot(mon, True, df):
                bs['i'] += 1
                return True
        elif game.line_clear(mon.x, mon.y, tx, ty):
            game.fx('bolt', cells=game.line_clear(mon.x, mon.y, tx, ty), src=(mon.x, mon.y), col=(220, 220, 255), ch='*')
            MC.hurt(game, who, random.randint(*mon.dmg) * .85, mon)
            bs['i'] += 1
            return True
    if d <= 1:
        bs['i'] += 1                                         # the engine strikes (mercs.py picks whom)
    return False


def _plain(game, mon):
    """The other bosses: their nova and their leap now come marked (round 16 gives them a kit)."""
    d, p = mon.tpl, game.player
    if not mon.awake or not game.visible(mon.x, mon.y):
        return False
    dist = cheb(mon.x, mon.y, p.x, p.y)
    if d.get('nova') and dist <= 2 and random.random() < .22:
        return start(game, mon, 'nova', say=d.get('nova_say', '{name} draws the air in round {him}. The ground about {him} darkens...'))
    if d.get('leap') and 2 <= dist <= 5 and game.line_clear(mon.x, mon.y, p.x, p.y) and random.random() < .3:
        return start(game, mon, 'leap', say='{name} crouches, eyes on the ground where you stand...')
    return False


def do(game, mon, mvid, df):
    """Use a card. False if it cannot be done now (it then makes a small move instead)."""
    mv = MOVES[mvid]
    kind = mv.get('kind')
    if kind in ('melee', 'bolt'):
        return False
    if mv.get('shape'):
        return start(game, mon, mvid)
    m, p = game.map, game.player
    if kind == 'snares':
        from .behave import traps
        tr = traps(m)
        line_ = list(game.cells_between((mon.x, mon.y), (p.x, p.y))[1:-1])
        spots = [c for c in line_ if m.tile(*c) == D.FLOOR and c not in tr][:3]
        if len(spots) < 3:
            spots += [c for c in free_around(game, m, p.x, p.y, 2) if m.tile(*c) == D.FLOOR and c not in tr
                      and c not in spots and cheb(*c, p.x, p.y) == 2][:3 - len(spots)]
        if not spots or cheb(mon.x, mon.y, p.x, p.y) > 9:
            return False
        for c in spots:
            tr[c] = max(2, mon.dmg[0])
        m.known_traps = getattr(m, 'known_traps', set()) | set(spots)
        game.msg(fill(mv['say'], mon), 'bad')
        return True
    if kind == 'prison':
        from . import spellmap as SM
        if cheb(mon.x, mon.y, p.x, p.y) > 8:
            return False
        ring = [(p.x + a, p.y + b) for a, b in D8]
        random.shuffle(ring)
        got = sum(1 for c in ring[2:] if SM.place(game, m, c[0], c[1], D.BONEWALL, 6))
        if not got:
            return False
        game.msg(fill(mv['say'], mon), 'bad')
        return True
    if kind == 'call':
        return call(game, mon, mv['helpers'], mv['say'])
    if kind == 'raise':
        return raise_dead(game, mon, mv['n'], mv['say'])
    if kind == 'wing':
        if cheb(mon.x, mon.y, p.x, p.y) > 10:
            return False
        if not start(game, mon, 'dive', say=mv['say']):
            return False
        mon.invis = 99
        st(mon)['air'] = True
        return True
    return False


def start(game, mon, mvid, say=None):
    """Load a marked blow: its cells go red. False if it would leave you no way out."""
    mv = MOVES[mvid]
    if mv.get('shape') == 'mark':
        who, tx, ty = aim(game, mon)
    elif mv.get('at') == 'aim' or mv.get('shape') in ('line', 'cone', 'tail'):
        who, tx, ty = aim(game, mon)
    else:
        who, tx, ty = 'p', game.player.x, game.player.y
    if mv.get('shape') not in ('ring', 'room', 'corpses') and cheb(mon.x, mon.y, tx, ty) > max(9, mv.get('len', 0)):
        return False
    cells = cells_for(game, mon, mv, tx, ty)
    if mv.get('shape') == 'corpses' and not cells:
        return False
    if mv.get('shape') not in ('mark',) and not cells:
        return False
    n = need(game, mon, mv, cells, tx, ty, 4 if mv['role'] == 'Z' else 3)
    if n is None:
        return False                                         # no way out: it picks another move
    load = max(mv.get('load', 1), n)                         # never faster than you can get out
    bs = st(mon)
    brk = mv.get('brk', load >= 2)
    if bs and 'unbroken' in bs['prep'] and bs['phase'] == len(phases(mon)) - 1:
        brk = False
    mon.cast = dict(mv=mvid, left=load, load=load, cells=sorted(cells), who=who if who == 'p' else who.who,
                    tx=tx, ty=ty, taken=0, brk=brk, told=[])
    text = say if say is not None else mv.get('say', '')
    if text:
        aim_name = 'you' if who == 'p' else who.name
        game.msg(fill(text, mon, aim_name), 'bad')
    from . import guide as GD
    if game.visible(mon.x, mon.y):
        GD.tip(game, 'red')
    return True


def _target_xy(game, mon, c):
    from . import mercs as MC
    if c['who'] == 'p':
        return game.player.x, game.player.y
    mc = next((x for x in MC.party(game) if x.who == c['who'] and x.body is not None and x.body in game.map.mons), None)
    return (mc.body.x, mc.body.y) if mc else (c['tx'], c['ty'])


def _go_on(game, mon, c):
    """One turn of a loading blow: it counts down; one that follows you moves along; at nought it strikes."""
    c['left'] -= 1
    mv = MOVES[c['mv']]
    if c['left'] <= 0:
        mon.cast = None
        release(game, mon, c)
        return
    if mv.get('follow'):                                     # it follows you, as long as you can still get out
        tx, ty = _target_xy(game, mon, c)
        cells = cells_for(game, mon, mv, tx, ty)
        n = need(game, mon, mv, cells, tx, ty, c['left'])
        if cells and n is not None and n <= c['left']:
            c['tx'], c['ty'] = tx, ty
            c['cells'] = sorted(cells)


def release(game, mon, c):
    """The blow lands on every cell that was marked: you, your company, and its own helpers too."""
    from .behave import give
    from . import spellmap as SM
    from . import mercs as MC
    m, p = game.map, game.player
    mv = MOVES[c['mv']]
    bs = st(mon)
    fx = mv.get('fx', {})
    cells = set(map(tuple, c['cells']))
    if bs and bs.get('air'):
        bs['air'] = False
        mon.invis = 0
    if fx.get('land'):                                       # it comes down where the circle was
        spot = (c['tx'], c['ty'])
        if not D.TILES[m.tile(*spot)].walk or game.occupied(m, *spot):
            near = [s for s in free_around(game, m, *spot, 1)] or free_around(game, m, mon.x, mon.y, 1)
            spot = near[0] if near else (mon.x, mon.y)
        if may_stand(game, mon, *spot):
            mon.x, mon.y = spot
    if fx.get('rush'):                                       # along the line, until something stops it
        from .engine import line
        for x, y in line(mon.x, mon.y, c['tx'], c['ty'])[:mv.get('len', 4)]:
            if (x, y) not in cells or not D.TILES[m.tile(x, y)].walk or game.occupied(m, x, y) or not may_stand(game, mon, x, y):
                break
            mon.x, mon.y = x, y
    col = {'fire': (255, 120, 40), 'cold': (160, 216, 255)}.get(mv.get('elem'), (255, 80, 60))
    if mv.get('shape') == 'mark':
        tx, ty = _target_xy(game, mon, c)
        safe = not clear_line(m, mon.x, mon.y, tx, ty) or m.tile(tx, ty) == D.HALLOWED
        cells = set() if safe else {(tx, ty)}
        if safe:
            game.msg('The Mark of Doom falls, and finds nothing: it cannot see its mark.', 'good')
    game.flash([cc for cc in cells if game.visible(*cc)], col, '*', .3)
    if c['mv'] in ('nova', 'leap') and game.visible(mon.x, mon.y):
        game.msg(mon.tpl.get(c['mv'] + '_msg', '{name} strikes!').format(name=name_of(mon)), 'bad')
    power = mv.get('power', .3) * (1 + (bs['fed'] if bs and mv['role'] == 'Z' else 0))
    if bs and mv['role'] == 'Z':
        bs['fed'] = 0
    lvl = mon.lvl
    s = game.stats()
    if (p.x, p.y) in cells and not game.dead:
        dmg = power * ref_life(game, lvl, s['max_life']) * random.uniform(.9, 1.1)
        if mv.get('hit'):
            game.msg(fill(mv['hit'], mon), 'bad')
        game.spare_full = True                               # a marked blow never kills from full life
        game.hurt(dmg, mon.the(), mv.get('elem'))
        game.__dict__.pop('spare_full', None)
        if not game.dead:
            if fx.get('hold'):
                give(game, 'held', fx['hold'], None)
                p.held_by = None
            if fx.get('slow'):
                give(game, 'slowed', fx['slow'])
            if fx.get('sick'):
                give(game, 'diseased', fx['sick'])
            if fx.get('push'):
                push(game, mon, p, fx['push'])
    elif c['who'] == 'p' and cells and mv.get('shape') != 'mark' and min(cheb(*cc, p.x, p.y) for cc in cells) <= 2:
        game.msg('The blow lands where you stood a moment ago.', 'info')
    for mc in MC.party(game):
        b = mc.body
        if b is None or b not in m.mons or (b.x, b.y) not in cells:
            continue
        mx = MC.stats(game, mc)['max_hp']
        dmg = power * ref_life(game, lvl, mx) * random.uniform(.9, 1.1) * (.5 if getattr(b, 'braced', False) else 1)
        if mc.hp >= mx:
            dmg = min(dmg, mc.hp - 1)
        b.braced = False
        MC.hurt(game, mc, max(1, dmg), mon)
    for o in [o for o in m.mons if o is not mon and not o.is_npc and (o.x, o.y) in cells]:
        dmg = max(1, round(o.maxhp * power * 1.6))
        o.hp -= dmg
        game.num(o.x, o.y, str(dmg), (240, 200, 150))
        if o.hp <= 0:
            if getattr(o, 'job', None) and game.visible(o.x, o.y):
                game.msg(f"{name_of(o)} is caught in {mon.the()}'s own blow!", 'good')
            game.kill(o)
    if fx.get('burn'):
        spots = [cc for cc in cells if D.TILES[m.tile(*cc)].walk]
        random.shuffle(spots)
        for cc in spots[:fx['burn'] * 2]:
            SM.place(game, m, cc[0], cc[1], D.BURNING, fx['burn'], max(2, lvl // 2))
    if fx.get('coins'):
        from .entities import Item
        spots = [cc for cc in cells if D.TILES[m.tile(*cc)].walk and cc != (p.x, p.y)]
        random.shuffle(spots)
        for cc in spots[:fx['coins']]:
            it = Item(game.new_id(), 'gold', 'gold', random.randint(1, 3))
            it.x, it.y = cc
            m.items.append(it)
    if fx.get('pillar'):
        break_pillar(game, mon)
    if bs and mv['role'] == 'Z' and not game.dead and mon in m.mons:
        bs['spent'] = 2 if random.random() < .25 else 1
        game.msg(f'{name_of(mon)} stands spent, {fill("{his}", mon)} strength gone for a moment. Now!', 'gold')


def push(game, mon, who, n):
    m = game.map
    dx, dy = (who.x > mon.x) - (who.x < mon.x), (who.y > mon.y) - (who.y < mon.y)
    if not dx and not dy:
        dx = 1
    for _ in range(n):
        nx, ny = who.x + dx, who.y + dy
        if not m.inb(nx, ny) or not D.TILES[m.tile(nx, ny)].walk or game.occupied(m, nx, ny):
            break
        ar = game.map.__dict__.get('arena')
        if ar and ar.get('sealed') and (nx, ny) not in ar['cells']:
            break
        who.x, who.y = nx, ny


# ------------------------------------------------------------------ helpers with a job
def helpers(game, mon):
    return [o for o in game.map.mons if getattr(o, 'boss_of', None) == mon.id]


def call(game, mon, which, say):
    from .entities import make_monster
    m = game.map
    if len(helpers(game, mon)) >= 4:
        return False
    ar = arena_of(game, mon)
    room = ar['cells'] if ar else None
    spots = [c for c in free_around(game, m, mon.x, mon.y, 5) if cheb(*c, mon.x, mon.y) >= 2 and (room is None or c in room)]
    if not spots:
        return False
    random.shuffle(spots)
    for (k, job), c in zip(which, spots):
        if k not in D.MONSTERS:
            continue
        o = make_monster(game, k, c[0], c[1], max(1, mon.lvl - 1))
        o.awake = o.called = True
        o.job, o.boss_of = job, mon.id
        m.mons.append(o)
        game.flash([c], (255, 214, 90), '*', .2)
    if say:
        game.msg(fill(say, mon), 'bad')
    return True


def raise_dead(game, mon, n, say):
    from .entities import make_monster
    m = game.map
    own = area(game, mon)
    sl = getattr(m, 'slain', [])
    here = [s for s in sl if (s[1], s[2]) in own and not game.occupied(m, s[1], s[2])][:n]
    if not here or len(helpers(game, mon)) >= 5:
        return False
    for s in here:
        sl.remove(s)
        o = make_monster(game, 'skeleton', s[1], s[2], max(1, mon.lvl - 3))
        o.awake = o.called = True
        o.job, o.boss_of = 'swarm', mon.id
        m.mons.append(o)
        game.flash([(s[1], s[2])], (196, 134, 255), '*', .2)
    if say:
        game.msg(fill(say, mon), 'bad')
    return True


def warded(game, mon):
    return any(o.job == 'warder' for o in helpers(game, mon))


def helper_turn(game, mon, df):
    """A helper does its job: the warder and the mender keep near their master; the channeler feeds its next blow."""
    boss = next((o for o in game.map.mons if o.id == getattr(mon, 'boss_of', None)), None)
    if boss is None:
        return False
    job = mon.job
    p = game.player
    if job in ('warder', 'mender', 'channeler') and cheb(mon.x, mon.y, p.x, p.y) > 1:
        if job == 'mender' and game.turn % 3 == 0 and boss.hp < boss.maxhp and clear_line(game.map, mon.x, mon.y, boss.x, boss.y):
            cap = cap_hp(boss)
            boss.hp = min(cap, boss.hp + max(2, boss.maxhp // 30))
            game.flash([(boss.x, boss.y)], (120, 240, 140), '+', .25)
            return True
        if job == 'channeler':
            bs = st(boss)
            if bs:
                bs['fed'] = min(.5, bs['fed'] + .05)
                if game.turn % 4 == 0:
                    game.flash([(mon.x, mon.y), (boss.x, boss.y)], (255, 160, 60), '~', .2)
            return True
        if cheb(mon.x, mon.y, boss.x, boss.y) > 2:
            return False                                     # it walks back to its master
        return True
    return False


def cap_hp(mon):
    """No healing past the threshold it has already crossed."""
    bs = st(mon)
    if not bs:
        return mon.maxhp
    ph = phases(mon)
    return mon.maxhp if bs['phase'] == 0 else round(mon.maxhp * ph[bs['phase']]['at'])


# ------------------------------------------------------------------ phases, spent, stagger, breaking
def _phase(game, mon, i, trick):
    bs = st(mon)
    bs['phase'], bs['i'], bs['piles'] = i, 0, {}
    mon.threat = {}                                          # who it wants is open again
    mon.cast = None
    if st(mon).get('air'):
        bs['air'] = False
        mon.invis = 0
    ph = phases(mon)[i]
    if not trick:
        return
    game.msg(fill(ph.get('say', '{name} changes.'), mon), 'bad')
    game.shake()
    t = ph.get('trick')
    ar = arena_of(game, mon)
    if t == 'call':
        call(game, mon, MOVES['call_kobolds']['helpers'], '')
    elif t == 'rise':
        raise_dead(game, mon, 3, '')
        call(game, mon, (('wraith', 'warder'),), '')
        game.msg('A wraith takes its place beside her and spreads its cold over her: it wards her.', 'bad')
    elif t == 'dark':
        bs['lichcraft'] = True
        if ar:
            ar['dark'] = True
    elif t == 'roar':
        call(game, mon, MOVES['call_drakes']['helpers'], '')
    elif t == 'burn':
        if ar:
            ar['dance'] = 0
        break_pillar(game, mon)


def add_dot(game, mon):
    bs = st(mon)
    bs['dots'] += 1
    if bs['dots'] >= 3:
        bs['dots'] = 0
        bs['stag'] = 2
        mon.cast = None
        game.msg(f'{name_of(mon)} staggers! Strike now!', 'gold')
        game.shake()


def do_break(game, mon, how):
    """A loading blow broken: gone, and it reels a turn."""
    c = mon.__dict__.get('cast')
    bs = st(mon)
    mon.cast = None
    if bs is not None:
        bs['stun'] = max(bs['stun'], 1)
        bs['breaks'] += 1
        if bs.get('air'):
            bs['air'] = False
            mon.invis = 0
        add_dot(game, mon)
    name = MOVES[c['mv']]['name'] if c else 'blow'
    game.flash([(mon.x, mon.y)], (206, 132, 255), '!', .35)
    game.msg(f"{how}{name_of(mon)}'s {name} breaks! {fill('{He}', mon)} reels.", 'gold')


def pre(game, mon):
    """Before a boss acts: new holds break its blow or meet its resolve; spent, staggered or reeling, it does nothing."""
    if mon.__dict__.get('twin'):
        twin_turn(game, mon)
    bs = st(mon)
    if bs is None:
        return False
    c = mon.__dict__.get('cast')
    if mon.hold > bs['seen_hold']:
        if c and c['brk']:
            mon.hold, mon.frozen = 0, False
            do_break(game, mon, '')
        elif bs['resolve'] > 0:
            bs['resolve'] -= 1
            mon.hold, mon.frozen = 0, False
            game.msg(f'{name_of(mon)} shrugs it off.', 'info')
        else:
            mon.hold = max(1, mon.hold // 2)
    sil = 'silence' in mon.effects
    if sil and not bs['sil'] and c and c['brk']:
        do_break(game, mon, '')
    bs['sil'] = sil
    if 'fear' in mon.effects:                                # it does not run; the light of the dawn breaks its spell
        del mon.effects['fear']
        c = mon.__dict__.get('cast')
        if c and c['brk'] and (mon.k in D.UNDEAD or mon.k == 'lich'):
            do_break(game, mon, 'The holy light tears through the spell. ')
        elif bs['resolve'] > 0:
            bs['resolve'] -= 1
            game.msg(f'{name_of(mon)} shrugs it off.', 'info')
    bs['seen_hold'] = max(0, mon.hold - 1)
    for k in ('stun', 'spent', 'stag'):
        if bs[k] > 0:
            bs[k] -= 1
            return True
    return False


def extra(game, mon, df):
    """One more small blow for each of your company beside you (D&D's legendary actions)."""
    from . import mercs as MC
    if st(mon) is None or mon.__dict__.get('cast') or mon not in game.map.mons:
        return
    p = game.player
    n = sum(1 for mc in MC.party(game) if mc.body is not None and mc.body in game.map.mons
            and cheb(mc.body.x, mc.body.y, p.x, p.y) <= 1)
    for _ in range(min(2, n)):
        if game.dead:
            return
        if cheb(mon.x, mon.y, p.x, p.y) <= 1:
            game.mon_attack(mon, df)
            continue
        mc = next((c for c in MC.party(game) if c.body is not None and c.body in game.map.mons
                   and cheb(c.body.x, c.body.y, mon.x, mon.y) <= 1), None)
        if mc:
            MC.hurt(game, mc, random.randint(*mon.dmg), mon)


# ------------------------------------------------------------------ your blows on it
def engage(game, mon):
    bs = st(mon)
    if bs is None or bs['engaged']:
        return
    bs['engaged'] = True
    game.banner = [mon.name.upper(), None]
    ar = arena_of(game, mon)
    if ar:
        if 'helper' in bs['prep'] and not helpers(game, mon):
            o = next((MOVES[c] for ph in phases(mon) for cs in ph['cards'].values() for c in cs
                      if MOVES[c].get('kind') == 'call'), None)
            if o:
                call(game, mon, o['helpers'][:1], '{name} is not alone this time.')
        p = game.player
        if (p.x, p.y) in ar['cells']:
            seal(game, ar)


def silvered(game):
    """Silver, fire or holy light: what still bites a lich that is half spirit."""
    from . import trees as TT
    s = game.stats()
    im = TT.imbue(game)
    return s.get('undead', 0) > 0 or s.get('fire_dmg', 0) > 0 or (im is not None and im[1] in ('burn', 'heal'))


def blow(game, mon, dmg, crit, weapon, elem):
    """Your blow on a kit boss: warded halves, spent and staggered take more; it stops at a threshold, unless a
    critical hit while it is spent or staggered breaks through."""
    if mon.is_npc:
        return dmg
    dmg = twin_blow(game, mon, dmg, weapon)
    bs = st(mon)
    if bs is None:
        return dmg
    if bs.get('air'):
        return 0
    engage(game, mon)
    mult = 1.0
    if warded(game, mon):
        mult *= .5
    if bs['spent'] or bs['stag']:
        mult *= 1.5
    if bs.get('lichcraft') and weapon and not silvered(game):
        mult *= .5
    dmg = max(1, round(dmg * mult))
    key = elem or ('weapon' if weapon else 'other')
    bs['took'][key] = bs['took'].get(key, 0) + dmg
    k = kit(mon)
    if elem and elem in k.get('weak', ()) and bs['weak_t'] != game.turn:
        bs['weak_t'] = game.turn
        game.msg({'cold': 'The cold bites deep!', 'fire': 'The fire bites deep!'}.get(elem, 'That bites deep!'), 'good')
        add_dot(game, mon)
    c = mon.__dict__.get('cast')
    if c and c['brk']:
        c['taken'] += dmg
        if c['taken'] >= mon.maxhp * .1:
            do_break(game, mon, 'Your blows shake it loose. ')
    ph = phases(mon)
    cur = bs['pending'] if bs.get('pending') is not None else bs['phase']
    nxt = cur + 1
    if nxt < len(ph):
        thr = round(mon.maxhp * ph[nxt]['at'])
        if mon.hp > thr >= mon.hp - dmg:
            last = nxt == len(ph) - 1
            if crit and (bs['spent'] or bs['stag']) and bs.get('pending') is None and not (last and great_evil(game, mon)):
                floor = round(mon.maxhp * ph[nxt + 1]['at']) + 1 if nxt + 1 < len(ph) else 1
                dmg = max(0, min(dmg, mon.hp - floor))
                _phase(game, mon, nxt, False)
                bs['stun'] = max(bs['stun'], 1)
                game.msg(f'Your blow tears through! {name_of(mon)} reels, and the change that was coming in '
                         f'{fill("{him}", mon)} never comes.', 'gold')
                game.shake()
                game.flash([(mon.x, mon.y)], (255, 214, 90), '*', .4)
                from . import chronicle as CH
                CH.add(game, 'Your deeds', f'You broke through {mon.name} in one blow, and the change in '
                       f'{fill("{him}", mon)} never came.', 'seen', quiet=True)
                bs['broke_through'] = True
            else:
                dmg = mon.hp - thr
                bs['pending'] = nxt
    return max(0, dmg)


def spare(game, mon):
    """It would die: but a threshold not yet crossed holds it, or a phylactery shard raises it again."""
    bs = st(mon)
    if bs is None or mon.hp > 0:
        return False
    ph = phases(mon)
    cur = bs['pending'] if bs.get('pending') is not None else bs['phase']
    if cur + 1 < len(ph):
        mon.hp = max(1, round(mon.maxhp * ph[cur + 1]['at']))
        bs['pending'] = cur + 1
        return True
    ar = arena_of(game, mon)
    if ar and any(game.map.tile(*c) == D.SHARD for c in ar.get('shards', ())):
        m = game.map
        if mon in m.mons:
            m.mons.remove(mon)
        mon.cast = None
        ar['rising'] = [3, mon]
        game.msg(f'{name_of(mon)} falls to dust... and the dust does not lie still. A shard ¤ glows in the dark.', 'bad')
        return True
    return False


def felled(game, mon):
    """It is dead: FOE FELLED, the way opens."""
    if mon.__dict__.get('twin'):
        twin_fell(game, mon)
        if twin_of(game, mon)[1] is not None and twin_of(game, mon)[1] in game.map.mons:
            return
    if st(mon) is None:
        return
    game.banner = ['FOE FELLED', None]
    ar = game.map.__dict__.get('arena')
    if ar and ar.get('boss') == mon.id:
        open_up(game, ar, True)


# ------------------------------------------------------------------ the arena
def arena_of(game, mon):
    ar = game.map.__dict__.get('arena')
    return ar if ar and ar.get('boss') == mon.id else None


def may_stand(game, mon, x, y):
    """A boss with a room never leaves it."""
    ar = arena_of(game, mon)
    return not ar or (x, y) in ar['cells']


def boss_of(game):
    """The boss the bar is for: one that fights you now, or rises again."""
    m = game.map
    ar = m.__dict__.get('arena')
    if ar and ar.get('rising'):
        return ar['rising'][1]
    for o in m.mons:
        bs = st(o)
        if bs is not None and (bs['engaged'] or game.visible(o.x, o.y)) and (bs['engaged'] or not getattr(o, 'invis', 0)):
            if bs['engaged'] and not (ar and ar.get('boss') == o.id and ar.get('sealed')) and not game.visible(o.x, o.y) \
                    and not bs.get('air'):
                continue
            return o
    return None


def on_level(game, m):
    """The bottom of a place with a kit boss: its room becomes an arena behind a veil of mist."""
    boss = next((o for o in m.mons if st(o) is not None), None)
    if boss is None:
        return
    build(game, m, boss)


def build(game, m, boss):
    from . import worldgen as W
    cells = None
    rof = getattr(m, 'room_of', None)
    if rof is not None:
        rid = rof[boss.y * m.w + boss.x]
        if rid != 255:
            cells = {(i % m.w, i // m.w) for i, r in enumerate(rof) if r == rid and D.TILES[m.t[i]].walk}
            if not 30 <= len(cells) <= 1400 or any(m.tile(*c) in (D.UP, D.DOWN) for c in cells):
                cells = None
    if cells is None:                                       # no room: a chamber round it, dug out
        blob = {(x, y) for y in range(boss.y - 4, boss.y + 5) for x in range(boss.x - 6, boss.x + 7)
                if 2 <= x < m.w - 2 and 2 <= y < m.h - 2 and ((x - boss.x) / 6.5) ** 2 + ((y - boss.y) / 4.5) ** 2 <= 1}
        near = {(x + a, y + b) for x, y in blob for a in (-1, 0, 1) for b in (-1, 0, 1)}
        if any(m.inb(*c) and m.tile(*c) in (D.UP, D.DOWN) for c in near):
            return None
        for x, y in blob:
            if not D.TILES[m.tile(x, y)].walk:
                m.set(x, y, D.FLOOR)
        cells = {c for c in blob if D.TILES[m.tile(*c)].walk}
    ring = {(x + a, y + b) for x, y in cells for a, b in D8} - cells
    gates = sorted(c for c in ring if m.inb(*c) and (D.TILES[m.tile(*c)].walk or D.TILES[m.tile(*c)].door))
    if not gates:
        return
    ups = [i for i, t in enumerate(m.t) if t == D.UP]
    if not ups:
        return
    ux, uy = ups[0] % m.w, ups[0] // m.w
    orig = {}
    for c in gates:
        orig[c] = m.tile(*c)
        m.set(c[0], c[1], D.VEIL)
    for o in [o for o in m.mons if (o.x, o.y) in gates]:
        sp = [s for s in free_around(game, m, o.x, o.y, 2) if s not in gates]
        if sp:
            o.x, o.y = sp[0]
    ar = dict(boss=boss.id, cells=sorted(cells), gates=gates, orig=orig, sealed=False, rotten=None, hits=0,
              home=(boss.x, boss.y), shards=[], pillars=[], dark=False, dance=None, flees=0, rising=None, done=False)
    m.arena = ar
    # the one hard way out: a rotten wall, with a short way dug behind it to the rest of the level
    from collections import deque
    dist = W.bfs(m, ux, uy, lambda t: D.TILES[t].walk or D.TILES[t].door or t == D.VEIL)
    shut = cells | ring
    srcs = [c for c in ring if c not in gates and m.inb(*c) and 1 <= c[0] < m.w - 1 and 1 <= c[1] < m.h - 1
            and min(cheb(*c, *g) for g in gates) >= 4
            and any((c[0] + a, c[1] + b) in cells for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    random.shuffle(srcs)
    par = {c: None for c in srcs}
    q = deque((c, 0) for c in srcs)
    end_ = None
    while q:
        (x, y), k = q.popleft()
        if k >= 16:
            continue
        for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            c = (x + a, y + b)
            if c in par or c in shut or not (1 <= c[0] < m.w - 1 and 1 <= c[1] < m.h - 1):
                continue
            par[c] = (x, y)
            if dist[c[1] * m.w + c[0]] >= 0 and D.TILES[m.tile(*c)].walk:
                end_ = c
                q.clear()
                break
            if m.tile(*c) in (D.UP, D.DOWN) or D.TILES[m.tile(*c)].door:
                continue
            q.append((c, k + 1))
    if end_ is not None:
        c = par[end_]
        while par[c] is not None:
            m.set(c[0], c[1], D.FLOOR)
            c = par[c]
        m.set(c[0], c[1], D.ROTTEN)
        ar['rotten'] = c
    furnish(game, m, boss, ar)


def _inner(m, ar, c, room, gap=2):
    x, y = c
    return all((x + a, y + b) in room for a in range(-gap, gap + 1) for b in range(-gap, gap + 1)) \
        and m.tile(x, y) == D.FLOOR and min(cheb(x, y, *g) for g in ar['gates']) > 2


def furnish(game, m, boss, ar):
    """What the kit's room holds: the hoard, the shards of the phylactery, the pillars of the dragon's cave."""
    room = set(ar['cells'])
    things = kit(boss).get('things')
    bx, by = boss.x, boss.y
    inner = [c for c in ar['cells'] if _inner(m, ar, c, room, 1) and cheb(*c, bx, by) >= 2]
    random.shuffle(inner)
    if things == 'hoard':
        for c in inner[:3]:
            m.set(c[0], c[1], D.GLITTER)
    elif things in ('tomb', 'lair'):
        # cover spread over the room, so that from anywhere a pillar or a shard is a few steps away
        pts = []
        for c in sorted(inner, key=lambda c: (c[0] // 6 + c[1] // 5) % 2):
            if all(cheb(*c, *q) >= 5 for q in pts) and cheb(*c, bx, by) >= 3 and _inner(m, ar, c, room, 1):
                pts.append(c)
        pts = pts[:12]
        random.shuffle(pts)
        if things == 'tomb':
            shards = sorted(pts, key=lambda c: -cheb(*c, bx, by))[:4]
            for c in shards:
                m.set(c[0], c[1], D.SHARD)
            ar['shards'] = shards
            pillars = [c for c in pts if c not in shards]
            sl = m.__dict__.setdefault('slain', [])
            for c in [c for c in inner if c not in pts][:3]:
                sl.append(('skeleton', c[0], c[1], boss.lvl))
        else:
            pillars = pts
            for c in [c for c in inner if cheb(*c, bx, by) == 2 and c not in pts][:2]:
                m.set(c[0], c[1], D.GLITTER)
        for c in pillars:
            m.set(c[0], c[1], D.PILLAR)
        ar['pillars'] = pillars
    # nothing in the room may cut the way through it
    from . import worldgen as W
    ups = [i for i, t in enumerate(m.t) if t == D.UP]
    if ups:
        dist = W.bfs(m, ups[0] % m.w, ups[0] // m.w, lambda t: D.TILES[t].walk or D.TILES[t].door or t == D.VEIL)
        for c in ar['cells']:
            if m.tile(*c) in (D.GLITTER, D.PILLAR, D.SHARD) and not any(
                    dist[g[1] * m.w + g[0]] >= 0 for g in ar['gates']):
                m.set(c[0], c[1], D.FLOOR)


def seal(game, ar):
    m = game.map
    if ar['sealed'] or ar['done']:
        return
    ar['sealed'] = True
    room = set(ar['cells'])
    for c in ar['gates']:
        o = m.mon_at(*c)
        if o is not None:
            sp = [s for s in free_around(game, m, *c, 2) if s in room]
            if sp:
                o.x, o.y = sp[0]
        m.set(c[0], c[1], D.SEALED)
    game.msg('Behind you the way crashes shut. Stones fill it from floor to roof!', 'bad')
    game.shake()
    from . import guide as GD
    GD.tip(game, 'shut')


def open_up(game, ar, fell):
    """The veil lifts when it falls (or the room opens again when you fled)."""
    m = game.map
    ar['sealed'] = False
    for c in ar['gates']:
        if m.tile(*c) in (D.SEALED, D.VEIL):
            m.set(c[0], c[1], ar['orig'].get(tuple(c), D.FLOOR) if fell else D.VEIL)
    if fell:
        ar['done'] = True
        ar['dark'] = False
        ar['dance'] = None
        game.msg('The stones in the way crumble, and the mist is gone.', 'info')
    elif ar['rotten'] and m.tile(*ar['rotten']) == D.FLOOR and not game.occupied(m, *ar['rotten']):
        m.set(ar['rotten'][0], ar['rotten'][1], D.ROTTEN)
        ar['hits'] = 0


def no_rest(game):
    ar = game.map.__dict__.get('arena')
    p = game.player
    return bool(ar and ar['sealed'] and (p.x, p.y) in set(map(tuple, ar['cells'])))


def sight(game, r):
    ar = game.map.__dict__.get('arena')
    if ar and ar.get('dark') and ar['sealed']:
        return min(r, 3)
    return r


def bump(game, x, y, t):
    """The veil asks once; the rotten wall gives after five blows; a shard breaks."""
    from . import events as EV
    m = game.map
    ar = m.__dict__.get('arena')
    if not ar:
        return None
    if t == D.VEIL:
        if (game.player.x, game.player.y) in set(map(tuple, ar['cells'])):
            return None                                       # from the inside it is only mist
        if ar.get('asked'):
            return None
        EV.ask(game, 'boss_veil', 'A veil of mist', 'A grey mist hangs in the way, still as a curtain, and the air '
               'beyond it is cold. Something waits on the other side. Once through, there may be no way back.',
               [('Step through the mist', 'go'), ('Stay back', 'bye')], cell=(x, y))
        return 0
    if t == D.ROTTEN:
        if not ar['sealed']:
            game.msg('The wall here is soft and black with rot.', 'info')
            return 0
        ar['hits'] += 1
        if ar['hits'] >= 5:
            m.set(x, y, D.FLOOR)
            game.msg('The rotten wall gives way! There is a way out.', 'good')
        else:
            game.msg(f'You hammer at the rotten wall. It gives a little. ({ar["hits"]}/5)', 'info')
        return 1
    if t == D.SHARD:
        m.set(x, y, D.DARKSHARD)
        game.msg('You smash the phylactery shard. Somewhere in the tomb a voice cries out.', 'good')
        game.shake()
        return 1
    if t == D.SEALED:
        game.msg('Fallen stones fill the way. It will not open while the fight goes on.', 'info')
        return 0
    return None


def r_veil(game, choice, ctx):
    if choice != 'go':
        return
    m, p = game.map, game.player
    ar = m.__dict__.get('arena')
    x, y = ctx['cell']
    if ar is None or game.occupied(m, x, y):
        return
    ar['asked'] = True
    p.x, p.y = x, y
    boss = next((o for o in m.mons if o.id == ar['boss']), None)
    if boss is not None and st(boss) and st(boss)['prep']:
        game.msg(f'{name_of(boss)} is waiting for you. {fill("{He}", boss)} has made ready this time.', 'bad')
    else:
        game.msg('You step through the mist. It closes behind you like cold water.', 'info')
    game.end_turn(1)


def tick(game):
    """Each turn on a map with an arena: fled from, the boss heals and makes ready; the dead lich rises; the floor
    burns in strips."""
    m, p = game.map, game.player
    ar = m.__dict__.get('arena')
    if not ar or ar['done']:
        return
    room = set(map(tuple, ar['cells']))
    if ar['sealed'] and (p.x, p.y) not in room and (p.x, p.y) not in set(map(tuple, ar['gates'])) \
            and (p.x, p.y) != (tuple(ar['rotten']) if ar['rotten'] else None):
        fled(game, ar)
        return
    if ar.get('rising'):
        rs = ar['rising']
        rs[0] -= 1
        if rs[0] <= 0:
            mon = rs[1]
            ar['rising'] = None
            shard = next((c for c in ar['shards'] if m.tile(*c) == D.SHARD), None)
            spot = ar['home'] if not game.occupied(m, *ar['home']) else (free_around(game, m, *ar['home'], 3) or [ar['home']])[0]
            mon.x, mon.y = spot
            m.mons.append(mon)
            if shard:
                m.set(shard[0], shard[1], D.DARKSHARD)
                mon.hp = max(1, mon.maxhp // 4)
                game.msg(f'The dust gathers and stands. {name_of(mon)} rises again! A shard goes dark.', 'bad')
                game.shake()
            else:
                mon.hp = 0
                game.msg('The dust stirs, and falls still. There is nothing left to call it back.', 'good')
                game.kill(mon)
    if ar.get('dance') is not None and ar['sealed']:
        _dance(game, ar, room)


def _dance(game, ar, room):
    """The burning floor: every other turn a strip of the floor is marked, and the next turn it burns."""
    from . import spellmap as SM
    m = game.map
    ar['dance'] += 1
    k = ar['dance']
    rows = sorted({c[1] for c in room})
    if not rows:
        return
    if k % 2 == 1:
        band = (k // 2) % 3
        ar['strip'] = [c for c in room if (c[1] - rows[0]) % 3 == band and D.TILES[m.tile(*c)].walk]
    else:
        lvl = getattr(m, 'level', 10)
        for c in ar.get('strip', ()):
            SM.place(game, m, c[0], c[1], D.BURNING, 1, 3 + lvl // 3)
        ar['strip'] = []


def fled(game, ar):
    """You got out. It heals, and makes ready against what you did (Shadow of Mordor), up to four times."""
    m = game.map
    boss = next((o for o in m.mons if o.id == ar['boss']), None)
    open_up(game, ar, False)
    ar['asked'] = False
    ar['flees'] += 1
    ar['dark'] = False
    ar['dance'] = None
    if boss is None:
        return
    bs = st(boss)
    boss.hp = boss.maxhp
    boss.cast = None
    boss.threat = {}
    boss.x, boss.y = ar['home'] if not game.occupied(m, *ar['home']) else (boss.x, boss.y)
    bs.update(phase=0, pending=None, i=0, piles={}, spent=0, stag=0, dots=0, stun=0, resolve=RESOLVE, engaged=False,
              lichcraft=False, air=False, fed=0)
    boss.invis = 0
    if len(bs['prep']) < MAX_PREP:
        took = bs['took']
        tot = sum(took.values()) or 1
        el = max((k for k in took if k in ('fire', 'cold', 'lightning', 'poison')), key=lambda k: took[k], default=None)
        if el and took[el] / tot >= .4 and f'res:{el}' not in bs['prep']:
            bs['prep'].append(f'res:{el}')
            boss.weak_res = dict(getattr(boss, 'weak_res', {}), **{el: 50})
        elif bs['breaks'] >= 2 and 'unbroken' not in bs['prep']:
            bs['prep'].append('unbroken')
        elif 'helper' not in bs['prep']:
            bs['prep'].append('helper')
        elif 'phase2' not in bs['prep']:
            bs['prep'].append('phase2')
    if 'phase2' in bs['prep'] and len(phases(boss)) > 2:
        _phase(game, boss, 1, False)
    bs['took'], bs['breaks'] = {}, 0
    game.msg(f'You hear {boss.the()} behind you, and then nothing. {fill("{He}", boss)} will be ready for you.', 'bad')


def break_pillar(game, mon):
    m = game.map
    ar = arena_of(game, mon)
    if not ar:
        return
    left = [c for c in ar['pillars'] if m.tile(*c) == D.PILLAR]
    if not left:
        return
    c = random.choice(left)
    m.set(c[0], c[1], D.FALLEN)
    game.msg('With a crack like thunder a pillar breaks and falls.', 'bad')
    game.shake()


# ------------------------------------------------------------------ your company in a boss fight
def marked(game):
    """Every cell a loading blow will strike, on this map."""
    out = set()
    for o in game.map.mons:
        c = o.__dict__.get('cast')
        if c:
            out |= set(map(tuple, c['cells']))
    return out


def ally_turn(game, mc, b):
    """Your hireling or beast plays it like you: out of the red, a shield into a loading boss. Better with rank."""
    m = game.map
    if mc.order in ('hold', 'passive'):
        return False
    red = marked(game)
    rank = getattr(mc, 'lvl', 1)
    good = min(.95, (.45 if mc.kind == 'beast' else .55) + rank * .04)
    if red and (b.x, b.y) in red:
        if mc.kind == 'defender' and mc.gear.get('shield') and cheb(b.x, b.y, game.player.x, game.player.y) <= 1 \
                and random.random() < .4:
            b.braced = True
            game.msg(f'{mc.name} sets {mc.his()} shield and braces.', 'info')
            return True
        if random.random() < good:
            room = m.__dict__.get('arena')
            cells = set(map(tuple, room['cells'])) if room and room.get('sealed') else None
            spots = [c for c in free_around(game, m, b.x, b.y, 1) if c not in red and (cells is None or c in cells)]
            if spots:
                b.x, b.y = random.choice(spots)
                game.msg(f'{mc.name} steps out of the red.', 'info')
                return True
        game.msg(f'{mc.name} does not move in time.', 'bad')
        return False
    for o in m.mons:
        c = o.__dict__.get('cast')
        if c and c['brk'] and cheb(o.x, o.y, b.x, b.y) <= 1 and mc.kind == 'defender' and mc.gear.get('shield') \
                and mc.cd == 0 and random.random() < good * .6:
            mc.cd = 5
            game.msg(f'{mc.name} smashes {mc.his()} shield into {o.the()}.', 'good')
            do_break(game, o, '')
            return True
    return False


def ally_target(game, mc, b, foes):
    """A spent or staggered boss first; then the warder, the mender, the channeler."""
    if mc.order in ('passive', 'hold', 'defend', 'attack'):
        return None
    for o in foes:
        bs = st(o)
        if bs and (bs['spent'] or bs['stag']) and cheb(o.x, o.y, b.x, b.y) <= 8:
            return o
    for job in ('warder', 'mender', 'channeler'):
        hs = [o for o in foes if getattr(o, 'job', None) == job and cheb(o.x, o.y, b.x, b.y) <= 8]
        if hs:
            return min(hs, key=lambda o: cheb(o.x, o.y, b.x, b.y))
    return None


# ------------------------------------------------------------------ what you see
def marks(game):
    """{(x, y): (number or None, its colour, hot)} for the map: the red ground, and the count where it loads long."""
    out = {}
    for o in game.map.mons:
        c = o.__dict__.get('cast')
        if not c:
            continue
        mv = MOVES[c['mv']]
        col = PURPLE if c['brk'] else RED
        num = str(c['left']) if c.get('load', mv.get('load', 1)) >= 2 else None
        hot = c['left'] <= 1
        cells = c['cells']
        if mv.get('shape') == 'mark':
            cells = [_target_xy(game, o, c)]
        for cc in cells:
            out[tuple(cc)] = (num, col, hot)
    ar = game.map.__dict__.get('arena')
    if ar and ar.get('strip'):
        for cc in ar['strip']:
            out.setdefault(tuple(cc), (None, RED, True))
    return out


def casting(o):
    return bool(o.__dict__.get('cast'))


def bar(game, mon):
    """What the bar under its name says: (phase, thresholds, state, colour, resolve, dots)."""
    bs = st(mon)
    ph = phases(mon)
    c = mon.__dict__.get('cast')
    ar = arena_of(game, mon)
    if ar and ar.get('rising'):
        state, col = f'Rising: {ar["rising"][0]}', RED
    elif c:
        left = c['left']
        state, col = f'Charging: {MOVES[c["mv"]]["name"]} {left}', PURPLE if c['brk'] else RED
    elif bs['stag']:
        state, col = 'Staggered', GOLDN
    elif bs['spent']:
        state, col = 'Spent', GOLDN
    elif bs.get('air'):
        state, col = 'Aloft', RED
    elif warded(game, mon):
        state, col = 'Warded', (160, 200, 255)
    else:
        state, col = '', None
    return dict(phase=ROMAN[min(bs['phase'], 3)], marks=[p_['at'] for p_ in ph[1:]], state=state, col=col,
                resolve=bs['resolve'], dots=bs['dots'])


def stance(game, mon):
    """A line in the look about how it stands: it changes with the next beat. It never says what it means."""
    bs = st(mon)
    if bs is None:
        return None
    if mon.__dict__.get('cast'):
        return None
    ph = phases(mon)[bs['phase']]
    role = ph['beat'][bs['i'] % len(ph['beat'])]
    return fill(STANCE.get(role, STANCE['k']), mon)


def rhythm(mon):
    """For the test build: the beat of its phase, and where it stands in it."""
    bs = st(mon)
    if bs is None:
        return ''
    pat = phases(mon)[bs['phase']]['beat']
    i = bs['i'] % len(pat)
    return f'{pat[:i]}[{pat[i]}]{pat[i + 1:]}'


# ------------------------------------------------------------------ twins
# Two bosses in one fight (Twin Emperors, Ornstein and Smough, the Swine Prince): mon.twin = dict(kind, other, role).
TWINS = {'shared': 'one life for two', 'survivor': 'the survivor takes all', 'opposites': 'opposites',
         'swap': 'they swap places', 'bound': 'bound together', 'master': 'master and beast'}


def link(a, b, kind):
    a.twin = dict(kind=kind, other=b.id, role='a')
    b.twin = dict(kind=kind, other=a.id, role='b')


def twin_of(game, mon):
    tw = mon.__dict__.get('twin')
    if not tw:
        return None, None
    return tw, next((o for o in game.map.mons if o.id == tw['other']), None)


def twin_blow(game, mon, dmg, weapon):
    """Opposites: one shrugs off weapons, the other spells. Shared life: the blow is felt by both."""
    tw, other = twin_of(game, mon)
    if not tw:
        return dmg
    if tw['kind'] == 'opposites' and (weapon if tw['role'] == 'a' else not weapon):
        dmg = max(1, round(dmg * .5))
    if tw['kind'] == 'shared' and other is not None:
        other.hp = max(1, other.hp - dmg)
    return dmg


def twin_turn(game, mon):
    """Bound together they mend each other, far apart they rage; every sixth turn the pair may swap places."""
    tw, other = twin_of(game, mon)
    if not tw or other is None:
        return
    if tw['kind'] == 'bound':
        if cheb(mon.x, mon.y, other.x, other.y) <= 1:
            mon.hp = min(cap_hp(mon), mon.hp + max(1, mon.maxhp // 100))
        elif cheb(mon.x, mon.y, other.x, other.y) > 6:
            mon.effects['frenzy'] = [2, 0]
    elif tw['kind'] == 'swap' and tw['role'] == 'a':
        if game.turn % 6 == 5:
            game.flash([(mon.x, mon.y), (other.x, other.y)], (206, 132, 255), '!', .4)
        elif game.turn % 6 == 0:
            mon.x, mon.y, other.x, other.y = other.x, other.y, mon.x, mon.y
            for o in helpers(game, mon) + helpers(game, other):
                o.awake = True
            if game.visible(mon.x, mon.y) or game.visible(other.x, other.y):
                game.msg(f'{name_of(mon)} and {other.the()} swap places in a flicker!', 'bad')


def twin_fell(game, mon):
    """One of the pair is dead: what becomes of the other."""
    tw, other = twin_of(game, mon)
    if not tw or other is None:
        return
    ar = game.map.__dict__.get('arena')
    if ar and ar.get('boss') == mon.id and tw['kind'] != 'shared':
        ar['boss'] = other.id                                # the room is the survivor's now
    k = tw['kind']
    if k == 'shared':
        other.hp = 0
        other.twin = None
        game.kill(other)
    elif k == 'survivor':
        other.hp = other.maxhp
        bo = st(other)
        z = next((c for ph in phases(mon) for c in ph['cards'].get('Z', ())), None)
        if bo is not None and z:
            bo['stolen'] = z
        game.msg(f'{other.the()[0].upper() + other.the()[1:]} takes up the strength of the fallen, and is whole again!', 'bad')
    elif k == 'master':
        if tw['role'] == 'b':
            other.effects['frenzy'] = [999, 0]
            game.msg(f'{other.the()[0].upper() + other.the()[1:]} howls over the body, mad with rage!', 'bad')
        else:
            other.effects['frenzy'] = [999, 0]
            if st(other) is not None:
                st(other)['wild'] = True
            game.msg(f'{other.the()[0].upper() + other.the()[1:]} goes wild, with no one to hold it back.', 'bad')
    other.twin = None


# ------------------------------------------------------------------ the test build (debug.py)
def spawn(game, k):
    """Set a kit boss down beside you, with its room if the map has none."""
    from .entities import make_monster
    m, p = game.map, game.player
    sp = free_around(game, m, p.x, p.y, 3)
    if not sp:
        return None
    x, y = sp[-1]
    o = make_monster(game, k, x, y, D.MONSTERS[k].get('lvl_fix', p.lvl))
    o.awake = True
    m.mons.append(o)
    return o


def set_phase(game, mon, i):
    ph = phases(mon)
    i = max(0, min(len(ph) - 1, i))
    mon.hp = round(mon.maxhp * ph[i]['at']) if i else mon.maxhp
    _phase(game, mon, i, True)


def check_fair(game, mon):
    """Every shaped move of its kit, from here: which would leave no way out."""
    bad = []
    for ph in phases(mon):
        for cs in ph['cards'].values():
            for c in cs:
                mv = MOVES[c]
                if mv.get('shape'):
                    who, tx, ty = aim(game, mon)
                    cells = cells_for(game, mon, mv, tx, ty)
                    if (cells or mv['shape'] == 'mark') and need(game, mon, mv, cells, tx, ty) is None:
                        bad.append(mv['name'])
    return sorted(set(bad))


from . import events as _EV  # noqa: E402

_EV.RESOLVERS['boss_veil'] = r_veil
