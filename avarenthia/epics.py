"""The epics (classes part 4; see "Classes part 4: the epics" in docs/built.md). A tier above the elites, on key 6
in the elite's place: two per class, 22 in all. An epic costs no mana or stamina but works once per rest (an inn's
bed, your camp); Phoenix waits on the key and burns you up instead of the blow that would kill you, once a day.

They are taught by hidden teachers, two of each class in every world, each in another part of it: an ash hermit, a
rime witch, a retired master thief... You hear of the teachers of your own classes only through a rumour, from rank
35 in that class; they teach from rank 40, after a deed of their own (a job in the jobs tab). When a teacher dies the
other remains; when both are gone, a pupil takes up the work elsewhere after a season.

What is yours (what you learnt, the deeds done, whether your epic is spent, Phoenix's flames) lives on the player
(`p.epic`); the teachers' huts are sites of the world (kind 'teacher')."""
import random

from . import data as D
from . import skills as SK
from .data import GRASS, FLOOR, WALL, DOOR, PATH, TREE
from .worldgen import cheb, free_around

TEACH_AT, HEAR_AT = 40, 35
GOLD = (255, 214, 90)
SIGN = '♦'
LOOK = {'teacher': ('î', (232, 200, 120))}
WHAT = {'teacher': 'the hut of a teacher'}
DESC = {'teacher': 'A hut far from the roads, where someone old lives alone and teaches what few can learn.'}
FLAMES = 4                  # Phoenix: the flames you carry after rising
FLAME_BITE = .05            # each turn they take this share of your life
SEASON = 90                 # days: a seed comes up, a pupil turns up


# ------------------------------------------------------------------ the 22 epics
def _S(sid, name, line, color, text, **kw):
    sk = SK.Skill(sid, name, line, 0, 0, 0, 'epic', color=color, glyph=SIGN, **kw)
    sk.epic, sk.text, sk.unlock = True, text, 0
    return sk


FIRE, ICE, STORM, HOLY, DARK, BONE, LEAF, BEAST, WAR, ARC, SNEAK = SK.FIRE, SK.ICE, SK.STORM, SK.HOLY, SK.DARK, \
    SK.BONE, SK.LEAF, SK.BEAST, SK.WAR, SK.ARC, SK.SNEAK
EPIC_LIST = [
    _S('sunfall', 'Sunfall', 'fire', (255, 214, 90), 'A small sun hangs a turn over your target, then falls: all within '
       '2 burn, and the ground burns 3 turns.'),
    _S('phoenix', 'Phoenix', 'fire', (255, 150, 60), 'While it is ready on [6], a blow that would kill you burns you up '
       'instead: you rise with a fifth of your life, foes within 2 catch fire, and you carry 4 flames that bite each '
       'turn. Water or a Health Potion puts one out. Once a day.'),
    _S('long_winter', 'Long Winter', 'frost', ICE, 'The ground within 3 freezes for 10 turns: who stands in it slows, '
       'who is slowed freezes.'),
    _S('glass_heart', 'Glass Heart', 'frost', (200, 236, 255), 'One foe is frozen 6 turns. Strike it, and it shatters: '
       'heavy damage to it and half to all beside it.'),
    _S('skyfathers_spear', "Skyfather's Spear", 'storm', STORM, 'One stroke from the sky along a line of 10 tiles '
       'toward your target; the wet are stunned.'),
    _S('eye_of_the_tempest', 'Eye of the Tempest', 'storm', (220, 230, 255), 'For 8 turns arrows miss you, and each '
       'turn a spark leaps to every foe within 3.'),
    _S('miracle', 'Miracle', 'restoration', HOLY, 'You and your company are wholly healed, and every ailment is gone.'),
    _S('epic_return', 'Return', 'restoration', (230, 250, 220), 'Your hireling or your beast gets up again, if it fell '
       'in the last 20 turns.'),
    _S('the_unmaking', 'The Unmaking', 'shadow', DARK, 'It costs a fifth of your life. A foe under a third of its life '
       'dies at once; any other loses half of what it has, a great one a quarter.', life_frac=.2),
    _S('eclipse', 'Eclipse', 'shadow', (120, 90, 170), 'For 6 turns every foe in sight sees only the tile beside it, '
       'and you are unseen.'),
    _S('lich_form', 'Lich Form', 'necromancy', BONE, 'For 10 turns you are undead: spells cost no life, poison and '
       'cold cannot touch you, and your blows steal life.'),
    _S('barrow_king', 'Barrow King', 'necromancy', (200, 214, 180), 'A barrow king rises from the ground, no corpse '
       'needed, and follows you until you rest.'),
    _S('wrath_of_the_wild', 'Wrath of the Wild', 'nature', LEAF, 'Everything within 3 grows shut: roots and thorns hold '
       'every foe, and the ground stays green.'),
    _S('oak_shape', 'Oak Shape', 'nature', (150, 200, 110), 'A fourth shape: a walking oak, slow, with much life; [1] '
       'Slam and [2] Root. Its key lets it go.'),
    _S('call_of_the_old_ones', 'Call of the Old Ones', 'beastcraft', BEAST, 'A great beast of this land comes to your '
       'side for 20 turns: a cave bear, a winter wolf or a giant hawk.'),
    _S('one_blood', 'One Blood', 'beastcraft', (220, 120, 90), 'For 10 turns your beast cannot die, and you share its '
       'life: what strikes you, half of it strikes the beast.'),
    _S('worldshaker', 'Worldshaker', 'warcraft', WAR, 'Strike the ground: every foe within 2 is struck, stunned and '
       'knocked down, the armoured too.'),
    _S('unstoppable', 'Unstoppable', 'warcraft', (255, 190, 90), 'For 8 turns nothing pushes, stuns or slows you, and '
       'every kill fills your stamina.'),
    _S('time_stop', 'Time Stop', 'arcane', (210, 210, 230), 'For 3 turns only you move and the world goes grey. You '
       'cannot harm anyone in it: walk, drink, heal or guard yourself, lay runes and snares.'),
    _S('unweave', 'Unweave', 'arcane', ARC, 'Everything magic within 3 is gone: the magic on foes, spells on the '
       'ground, creatures called up.'),
    _S('death_mark', 'Death Mark', 'cunning', SNEAK, 'You are unseen, and your next blow kills an ordinary foe outright; '
       'a great one takes it four times over.'),
    _S('shadow_dance', 'Shadow Dance', 'cunning', (170, 160, 200), 'For 5 turns every blow counts as an unseen first '
       'strike.'),
]
EPICS = {s.id: s for s in EPIC_LIST}
BY_LINE = {}
for _s in EPIC_LIST:
    BY_LINE.setdefault(_s.line, []).append(_s.id)
SK.SKILLS.update(EPICS)
assert len(EPICS) == 22 and all(len(v) == 2 for v in BY_LINE.values())


def is_epic(sk):
    return getattr(sk, 'epic', False)


# ------------------------------------------------------------------ what is yours
def st(game):
    p = game.player
    if not hasattr(p, 'epic'):
        p.epic = dict(spent=False, phoenix_day=-1, learnt={}, deeds={}, heard=set(), king=False, flames=0)
    return p.epic


def buff(game, k):
    return next((b for b in game.player.buffs if b[0] == k), None)


def has(game, k):
    return buff(game, k) is not None


def add_buff(game, k, turns, label, v=1):
    p = game.player
    p.buffs = [b for b in p.buffs if b[0] != k] + [[k, v, turns, label]]


def on_bar(game):
    """The epic on key 6, or None."""
    p = game.player
    sid = p.bar[5] if len(p.bar) > 5 else None
    return sid if sid in EPICS else None


def ready(game, sid):
    s = st(game)
    if sid == 'phoenix':
        return s['phoenix_day'] != game.day
    return not s['spent']


def rested(game):
    """A night in a bed or at your camp: the epic comes back, and the barrow king goes down again."""
    s = st(game)
    if s['spent'] and on_bar(game) and on_bar(game) != 'phoenix':
        game.msg(f'{EPICS[on_bar(game)].name} is with you again.', 'gold')
    s['spent'] = False
    if s['king']:
        s['king'] = False
        for o in [o for o in game.map.mons if getattr(o, 'barrow_king', False)]:
            game.map.mons.remove(o)
            game.msg('The barrow king sinks back into the ground. You hear it settle, far down.', 'info')
        game.thralls = [o for o in getattr(game, 'thralls', []) if not getattr(o, 'barrow_king', False)]


def describe(sk):
    return sk.text + (' Once a day.' if sk.id == 'phoenix' else ' Once per rest, and no mana or stamina.')


def x_epic(game, sk, r):
    if sk.id == 'phoenix':
        game.msg('Phoenix needs no calling: while it is ready on [6], the blow that would kill you burns you up '
                 'instead.', 'info')
        return False
    if sk.id == 'oak_shape' and oak(game):
        game.player.buffs = [b for b in game.player.buffs if not str(b[3]).endswith(' shape')]
        let_go_oak(game)
        game.msg('You let the oak go, and the bark falls from you.', 'good')
        return True
    if not ready(game, sk.id):
        game.msg(f'{sk.name} is spent. It comes back when you rest: an inn\'s bed or your camp.', 'bad')
        return False
    if time_stopped(game):
        game.msg('Time stands still. Nothing more can be woken in it.', 'bad')
        return False
    if not FN[sk.id](game, sk, r):
        return False
    st(game)['spent'] = True
    game.msg(f'{sk.name}!', 'gold')
    return True


SK.EXEC['epic'] = x_epic


# ------------------------------------------------------------------ the epics at work
def _target(game, rng=9):
    t = game.target()
    if t and t in game.visible_hostiles() and cheb(t.x, t.y, game.player.x, game.player.y) <= rng:
        return t
    t = game.nearest_target(rng, True)
    if not t:
        game.miss_target('No target in sight.')
    return t


def _dmg(game, lo, hi, r, k=1.0):
    return round((random.randint(lo, hi) + r * k) + game.stats()['ene'] // 5)


def _foes_near(game, x, y, rad):
    return [o for o in game.map.mons if not o.is_npc and cheb(o.x, o.y, x, y) <= rad and o.hp > 0]


def _area(x, y, rad):
    return [(x + dx, y + dy) for dy in range(-rad, rad + 1) for dx in range(-rad, rad + 1)]


def x_sunfall(game, sk, r):
    t = _target(game)
    if not t:
        return False
    m = game.map
    m.__dict__.setdefault('suns', []).append(dict(x=t.x, y=t.y, at=game.turn + 1, r=r))
    game.flash([(t.x, t.y)], GOLD, '☼', .5)
    game.msg('A small sun kindles over the spot and hangs there, white and gold.', 'good')
    return True


def _sun_falls(game, sun):
    from . import spellmap as SM
    m = game.map
    x, y, r = sun['x'], sun['y'], sun['r']
    game.fx('meteor', x=x, y=y, r=2, col=GOLD)
    game.fx('burst', x=x, y=y, r=2, col=(255, 170, 60), delay=.15, dust=True)
    game.shake()
    for o in _foes_near(game, x, y, 2):
        if not game.damage_mon(o, _dmg(game, 22, 34, r, .9), elem='fire') and o in m.mons:
            o.effects['burn'] = [4, 4 + r // 6]
    cells = [c for c in _area(x, y, 2) if m.inb(*c) and D.TILES[m.tile(*c)].walk]
    SM.area(game, m, cells, D.BURNING, 3, max(3, 2 + r // 8))
    p = game.player
    if cheb(p.x, p.y, x, y) <= 2:
        game.hurt(_dmg(game, 10, 16, r, .3), 'your own sun', 'fire')


def phoenix(game, cause):
    """The blow that would have killed you. Returns True when Phoenix burnt you up instead."""
    s = st(game)
    p = game.player
    if on_bar(game) != 'phoenix' or s['phoenix_day'] == game.day:
        return False
    s['phoenix_day'] = game.day
    st_ = game.stats()
    p.life = max(1, round(st_['max_life'] * .2))
    p.poison = None
    s['flames'] = FLAMES
    r = SK.rank(game, 'fire')
    for o in _foes_near(game, p.x, p.y, 2):
        o.effects['burn'] = [5, 4 + r // 6]
        o.awake = True
    game.fx('burst', x=p.x, y=p.y, r=2, col=(255, 150, 60), signs='*^·')
    game.fx('rise', x=p.x, y=p.y, col=GOLD)
    game.shake()
    game.msg(f'{cause[0].upper() + cause[1:] if cause else "The blow"} should have been the end of you. Instead you '
             'burn up, and rise out of the fire. Four flames still cling to you: water, or a Health Potion, puts them '
             'out one by one.', 'unique')
    from . import chronicle as CH
    CH.deed(game, 'Out of the fire', f'You fell to {cause}, and rose again out of the fire of the Phoenix.')
    return True


def flames(game):
    return st(game).get('flames', 0)


def quench(game, why):
    s = st(game)
    if s.get('flames', 0) > 0:
        s['flames'] -= 1
        game.msg(f'{why} One flame goes out.' + ('' if s['flames'] else ' The last of the fire is gone.'), 'good')


def x_long_winter(game, sk, r):
    from . import spellmap as SM
    p, m = game.player, game.map
    cells = [c for c in _area(p.x, p.y, 3) if m.inb(*c) and D.TILES[m.tile(*c)].walk and c != (p.x, p.y)]
    SM.area(game, m, cells, D.DRIFT, 10, 2)
    m.winter = dict(cells=set(cells), until=game.turn + 10)
    for o in _foes_near(game, p.x, p.y, 3):
        o.effects['slow'] = [2, 0]
        o.awake = True
    game.fx('wave', x=p.x, y=p.y, r=3, col=ICE, sign='*', dur=.4)
    game.msg('The cold comes up out of the ground round you, and the land goes white and hard.', 'good')
    return True


def x_glass_heart(game, sk, r):
    t = _target(game)
    if not t:
        return False
    t.hold = max(t.hold, 6)
    t.frozen = True
    t.glass = game.turn + 6
    t.awake = True
    game.fx('burst', x=t.x, y=t.y, r=0, col=(200, 236, 255), signs='♦*·')
    game.msg(f'{t.the()[0].upper() + t.the()[1:]} freezes through, clear as glass. One blow will shatter it.', 'good')
    return True


def x_skyfathers_spear(game, sk, r):
    p, m = game.player, game.map
    t = _target(game, 10)
    if not t:
        return False
    dx, dy = t.x - p.x, t.y - p.y
    n = max(abs(dx), abs(dy)) or 1
    far = (p.x + round(dx * 10 / n), p.y + round(dy * 10 / n))
    cells = []
    for c in game.cells_between((p.x, p.y), far):
        if c == (p.x, p.y):
            continue
        if not m.inb(*c) or D.TILES[m.tile(*c)].opaque:
            break
        cells.append(c)
        if len(cells) >= 10:
            break
    from . import spellmap as SM
    game.fx('sky', col=(255, 255, 255))
    game.fx('line', cells=cells, col=STORM)
    hit = [o for o in m.mons if not o.is_npc and (o.x, o.y) in cells]
    for o in hit:
        wet = SM.wet(game, o)
        if not game.damage_mon(o, _dmg(game, 28, 44, r, 1.1) * (1.25 if wet else 1), elem='lightning') and wet \
                and o in m.mons:
            o.hold = max(o.hold, 2)
    game.shake()
    game.msg('The sky opens along a line from you, and the stroke runs down it like a thrown spear.', 'good')
    return True


def x_eye_of_the_tempest(game, sk, r):
    p = game.player
    add_buff(game, 'eye', 8, sk.name)
    game.fx('wave', x=p.x, y=p.y, r=3, col=(220, 230, 255), sign='~')
    game.msg('The wind goes round you in a ring, and in the middle of it the air is still.', 'good')
    return True


def _sparks(game):
    p = game.player
    r = SK.rank(game, 'storm')
    for o in [o for o in game.visible_hostiles() if cheb(o.x, o.y, p.x, p.y) <= 3]:
        game.fx('zap', cells=game.cells_between((p.x, p.y), (o.x, o.y))[1:] or [(o.x, o.y)], col=STORM)
        game.damage_mon(o, round(random.randint(5, 10) + r / 4), elem='lightning')


def x_miracle(game, sk, r):
    from . import mercs as MC
    from . import behave as BH
    p = game.player
    s = game.stats()
    game.heal(s['max_life'] - p.life, show=True)
    p.poison = None
    p.burn = None
    BH.cure(game, tuple(BH.status(game)))
    st(game)['flames'] = 0
    for mc in MC.party(game):
        mc.hp = MC.stats(game, mc)['max_hp']
        MC.refresh_body(game, mc)
    game.fx('burst', x=p.x, y=p.y, r=2, col=HOLY, signs='+*·')
    game.fx('rise', x=p.x, y=p.y, col=HOLY)
    game.msg('Light comes down on you and yours, and every hurt closes.', 'good')
    return True


def x_epic_return(game, sk, r):
    from . import mercs as MC
    fell = st(game).get('fell')
    if fell:
        slot, mc = fell
        if game.turn - getattr(mc, 'fell_turn', -999) <= 20 and mc.state in ('fallen', 'gone') \
                and getattr(game, slot, None) in (None, mc):
            if mc.state == 'gone':                      # hardcore: the body is still warm
                m = game.map
                m.items = [it for it in m.items if not (it.k == 'corpse' and it.name == f'the body of {mc.name}')]
            setattr(game, slot, mc)
            mc.state = 'alive'
            mc.hp = MC.stats(game, mc)['max_hp'] // 2
            mc.fleeing = 0
            st(game)['fell'] = None
            MC.sync(game)
            b = mc.body
            if b is not None:
                b.hp = mc.hp
                game.fx('rise', x=b.x, y=b.y, col=(230, 250, 220))
            game.msg(f'{mc.name} draws a breath and gets up again.', 'good')
            return True
    game.msg('Nobody of yours has fallen in these last moments.', 'bad')
    return False


def x_the_unmaking(game, sk, r):
    p = game.player
    t = _target(game, 8)
    if not t:
        return False
    game.fx('inward', x=t.x, y=t.y, src=(p.x, p.y), col=DARK)
    great = t.is_boss or t.tpl.get('chief') or t.elite == 2
    if not great and t.hp < t.maxhp * .3:
        game.msg(f'{t.the()[0].upper() + t.the()[1:]} comes apart, and is not there any more.', 'good')
        t.hp = 0
        game.kill(t)
        return True
    loss = max(1, t.hp // (4 if great else 2))
    t.hp -= loss
    t.awake = True
    game.num(t.x, t.y, str(loss), DARK)
    game.msg(f'Something goes out of {t.the()}, and does not come back.', 'good')
    if t.hp <= 0:
        game.kill(t)
    return True


def x_eclipse(game, sk, r):
    from . import arts as ART
    p = game.player
    ART.lose_you(game, game.visible_hostiles())
    add_buff(game, 'eclipse', 6, sk.name)
    game.fx('burst', x=p.x, y=p.y, r=3, col=(90, 70, 130), signs='▒░∙')
    game.msg('The light goes out of the sky. Your foes grope in the dark, and cannot find you.', 'good')
    return True


def x_lich_form(game, sk, r):
    p = game.player
    add_buff(game, 'lich', 10, sk.name)
    p.poison = None
    game.fx('burst', x=p.x, y=p.y, r=1, col=BONE, signs='∙·', hollow=True)
    game.msg('The warmth goes out of you. Your hands are grey, and nothing hurts.', 'good')
    return True


def _king(game, x, y):
    from . import mercs as MC
    o = MC.thrall(game, 'wight', x, y, 10 ** 6, 'The Barrow King', game.player.lvl + 3)
    o.hp = o.maxhp = round(o.maxhp * 2.2)
    o.dmg = (round(o.dmg[0] * 1.5), round(o.dmg[1] * 1.5))
    o.fg = (214, 224, 190)
    o.barrow_king = True
    return o


def x_barrow_king(game, sk, r):
    p, m = game.player, game.map
    spots = [c for c in free_around(game, m, p.x, p.y, 2) if c != (p.x, p.y)]
    if not spots:
        game.msg('There is no room.', 'bad')
        return False
    x, y = min(spots, key=lambda c: cheb(c[0], c[1], p.x, p.y))
    o = _king(game, x, y)
    game.fx('raise', x=x, y=y, ch=o.ch, col=o.fg, from_col=(90, 80, 60))
    st(game)['king'] = True
    game.msg('The ground breaks open beside you, and a crowned dead thing climbs out of it. It turns to your foes.',
             'good')
    return True


def keep_king(game):
    """The barrow king walks with you from map to map, until you rest."""
    m = game.map
    if not st(game)['king'] or m.kind in ('over', 'town') or any(getattr(o, 'barrow_king', False) for o in m.mons):
        return
    p = game.player
    spots = [c for c in free_around(game, m, p.x, p.y, 2) if c != (p.x, p.y)]
    if spots:
        _king(game, *min(spots, key=lambda c: cheb(c[0], c[1], p.x, p.y)))


GREEN_ON = {FLOOR, D.ASH, D.SAND}


def x_wrath_of_the_wild(game, sk, r):
    from . import spellmap as SM
    p, m = game.player, game.map
    for o in _foes_near(game, p.x, p.y, 3):
        o.hold = max(o.hold, 3)
        o.awake = True
    cells = [c for c in _area(p.x, p.y, 3) if m.inb(*c) and D.TILES[m.tile(*c)].walk and c != (p.x, p.y)]
    SM.area(game, m, cells, D.ROOTS, 8, max(2, 2 + r // 8))
    f = SM.fields(m)
    for c in cells:
        fd = f.get(c)
        if fd and fd[2] in GREEN_ON:
            fd[2] = GRASS                               # when the roots let go, grass stays
    game.fx('wave', x=p.x, y=p.y, r=3, col=LEAF, sign='♣', dur=.4)
    game.msg('Roots heave up out of the ground and thorns grow over them, round every foe near you.', 'good')
    return True


def x_oak_shape(game, sk, r):
    from . import behave as BH
    p = game.player
    t = 30
    p.buffs = [b for b in p.buffs if not str(b[3]).endswith(' shape')]
    p.buffs += [['dmg', 10 + r // 4, t, 'Oak shape'], ['dr', 35, t, 'Oak shape'], ['life', 40 + r * 2, t, 'Oak shape']]
    BH.give(game, 'slowed', t)
    game.heal(40 + r * 2)
    from .skills import ring_cells
    game.flash(ring_cells(p.x, p.y, 1), (150, 200, 110), '♣', .3)
    game.msg('Your feet push down into the ground, your skin cracks into bark: you are an oak, and you walk.', 'good')
    return True


def oak(game):
    return any(b[3] == 'Oak shape' for b in game.player.buffs)


def let_go_oak(game):
    from . import behave as BH
    BH.clear(game, 'slowed', quiet=True)


OLD_ONES = {'cave_bear': 'Cave Bear', 'winter_wolf': 'Winter Wolf', 'giant_hawk': 'Giant Hawk'}


def _old_one(game):
    m = game.map
    if m.kind == 'dungeon' or getattr(m, 'underground', False):
        return 'cave_bear'
    from . import seasons as SN
    from .zones import here_biome
    b = here_biome(game) if getattr(m, 'zone', None) is not None else ''
    ox, oy = game.over_pos if game.cur != 'over' else (game.player.x, game.player.y)
    om = game.maps['over']
    b = b or SN.biome(om, oy * om.w + ox)
    if b in ('tundra', 'taiga', 'glacier', 'alpine', 'tundra_hills', 'shrubland_cold', 'steppe', 'ice_shelf'):
        return 'winter_wolf'
    if b in ('hills', 'mountain', 'peak', 'meadow', 'savanna', 'moor', 'desert', 'badlands', 'canyon', 'mesa'):
        return 'giant_hawk'
    return 'cave_bear'


def x_call_of_the_old_ones(game, sk, r):
    from . import mercs as MC
    p, m = game.player, game.map
    spots = [c for c in free_around(game, m, p.x, p.y, 2) if c != (p.x, p.y)]
    if not spots:
        game.msg('There is no room.', 'bad')
        return False
    k = _old_one(game)
    x, y = random.choice(spots)
    o = MC.thrall(game, k, x, y, 20, f'The Old {OLD_ONES[k]}', p.lvl + 2)
    o.hp = o.maxhp = round(o.maxhp * 1.6)
    game.flash([(x, y)], BEAST, o.ch, .3)
    game.msg(f'Something old answers out of the land: a great {OLD_ONES[k].lower()}, bigger than any you have seen, '
             'comes to your side.', 'good')
    return True


def x_one_blood(game, sk, r):
    b = SK.with_beast(game)
    if not b:
        game.msg('One Blood needs your beast at your side.', 'bad')
        return False
    add_buff(game, 'oneblood', 10, sk.name)
    p = game.player
    game.fx('drain', cells=game.cells_between((b.body.x, b.body.y), (p.x, p.y)), col=(220, 120, 90))
    game.msg(f'You and {b.name} are one blood now: what strikes one, the other feels.', 'good')
    return True


def one_blood(game, mc):
    """Whether this beast of yours may not die now."""
    return mc.kind == 'beast' and has(game, 'oneblood')


def x_worldshaker(game, sk, r):
    p, m = game.player, game.map
    foes = _foes_near(game, p.x, p.y, 2)
    game.fx('wave', x=p.x, y=p.y, r=2, col=(196, 160, 110), sign='!', dur=.36)
    game.shake()
    for o in foes:
        if o in m.mons and not game.weapon_strike(o, 130, sunder=True) and o in m.mons:
            o.hold = max(o.hold, 2)
    game.msg('You strike the ground, and it heaves: everything round you goes down.', 'good')
    return True


def x_unstoppable(game, sk, r):
    p = game.player
    from . import behave as BH
    for k in ('slowed', 'held', 'paralysed', 'stunned', 'asleep'):
        if BH.has(game, k):
            BH.clear(game, k, quiet=True)
    add_buff(game, 'unstoppable', 8, sk.name)
    game.fx('burst', x=p.x, y=p.y, r=1, col=(255, 190, 90), signs='!·', hollow=True)
    game.msg('Nothing will stop you now.', 'good')
    return True


def unstoppable(game):
    return has(game, 'unstoppable')


def x_time_stop(game, sk, r):
    add_buff(game, 'timestop', 4, sk.name)
    game.msg('The world stops. The leaves hang in the air, the foes stand in mid-step, and only you can move.', 'good')
    return True


def time_stopped(game):
    return has(game, 'timestop')


def x_unweave(game, sk, r):
    from . import arts as ART
    from . import spellmap as SM
    p, m = game.player, game.map
    n = 0
    for o in _foes_near(game, p.x, p.y, 3):
        gone = [md for md in o.mods if md in ART.MAGIC_MODS]
        if gone:
            o.mods = [md for md in o.mods if md not in ART.MAGIC_MODS]
            n += 1
        if getattr(o, 'called', False):
            game.flash([(o.x, o.y)], ARC, '∙', .2)
            m.mons.remove(o)
            n += 1
    f = SM.fields(m)
    for xy in [xy for xy, fd in f.items() if fd[0] in SM.SPELL_TILES and cheb(xy[0], xy[1], p.x, p.y) <= 3]:
        SM.clear(m, xy)
        n += 1
    game.fx('burst', x=p.x, y=p.y, r=3, col=ARC, signs='∙·', hollow=True)
    game.msg('You pull, and the magic round you comes undone like knitting.' if n else
             'You pull, and nothing round you was woven: the air is plain.', 'good')
    return True


def x_death_mark(game, sk, r):
    from . import arts as ART
    p = game.player
    ART.lose_you(game, game.visible_hostiles())
    p.buffs = [b for b in p.buffs if b[0] not in ('sneak', 'deathmark')] + \
        [['sneak', 1, 30, 'Sneak'], ['deathmark', 1, 30, sk.name]]
    game.fx('burst', x=p.x, y=p.y, r=1, col=SNEAK, signs='░∙')
    game.msg('You go still, and out of their sight. The next blow will be the last one.', 'good')
    return True


def x_shadow_dance(game, sk, r):
    p = game.player
    add_buff(game, 'shadowdance', 5, sk.name)
    game.fx('burst', x=p.x, y=p.y, r=1, col=(170, 160, 200), signs='░∙', hollow=True)
    game.msg('You move between one shadow and the next. Nobody sees a blow of yours coming.', 'good')
    return True


def shadow_dance(game):
    return has(game, 'shadowdance')


FN = {'sunfall': x_sunfall, 'long_winter': x_long_winter, 'glass_heart': x_glass_heart,
      'skyfathers_spear': x_skyfathers_spear, 'eye_of_the_tempest': x_eye_of_the_tempest, 'miracle': x_miracle,
      'epic_return': x_epic_return, 'the_unmaking': x_the_unmaking, 'eclipse': x_eclipse, 'lich_form': x_lich_form,
      'barrow_king': x_barrow_king, 'wrath_of_the_wild': x_wrath_of_the_wild, 'oak_shape': x_oak_shape,
      'call_of_the_old_ones': x_call_of_the_old_ones, 'one_blood': x_one_blood, 'worldshaker': x_worldshaker,
      'unstoppable': x_unstoppable, 'time_stop': x_time_stop, 'unweave': x_unweave, 'death_mark': x_death_mark,
      'shadow_dance': x_shadow_dance}
assert set(FN) | {'phoenix'} == set(EPICS)


# ------------------------------------------------------------------ hooks from the engine
def on_damage(game, mon, dmg, weapon, ranged=False):
    """A blow or spell on a foe: Glass Heart shatters, Death Mark kills, Lich Form drinks. Returns the damage."""
    p = game.player
    if getattr(mon, 'glass', -1) >= game.turn and mon.frozen and mon.hold > 0:
        mon.glass = -1
        mon.hold, mon.frozen = 0, False
        great = mon.is_boss or mon.tpl.get('chief')
        r = SK.rank(game, 'frost')
        extra = round(mon.maxhp * (.12 if great else .3)) + 20 + r
        game.fx('burst', x=mon.x, y=mon.y, r=1, col=(200, 236, 255), signs='*♦·')
        game.msg(f'{mon.the()[0].upper() + mon.the()[1:]} shatters like glass!', 'good')
        for o in _foes_near(game, mon.x, mon.y, 1):
            if o is not mon:
                o.hp -= extra // 2
                game.num(o.x, o.y, str(extra // 2), ICE)
                if o.hp <= 0:
                    game.kill(o)
        dmg += extra
    if weapon and has(game, 'deathmark') and not mon.is_npc:
        p.buffs = [b for b in p.buffs if b[0] != 'deathmark']
        great = mon.is_boss or mon.tpl.get('chief') or mon.elite == 2
        game.num(mon.x, mon.y, 'marked', (200, 190, 230))
        dmg = dmg * 4 if great else max(dmg, mon.hp + 1)
    if weapon and not ranged and has(game, 'lich'):
        game.heal(max(1, round(dmg * .25)))
    return dmg


def hurt(game, dmg, elem):
    """What strikes you, as Lich Form, One Blood and a duel bend it."""
    from . import mercs as MC
    if has(game, 'lich') and elem in ('cold', 'poison'):
        return 0
    if has(game, 'oneblood'):
        b = SK.with_beast(game)
        if b:
            half = dmg / 2
            MC.hurt(game, b, round(half))
            dmg -= half
    duel = getattr(game.map, 'duel', None)
    if duel is not None:
        s = game.stats()
        floor = s['max_life'] * .15
        if game.player.life - dmg < floor:
            dmg = max(0, game.player.life - floor)
            end_duel(game, False)
    return dmg


def arrows_miss(game):
    return has(game, 'eye')


def notice(game, mon):
    """Under the Eclipse a foe sees only the tile beside it. None when it does not apply."""
    if not has(game, 'eclipse'):
        return None
    return .65 if cheb(mon.x, mon.y, game.player.x, game.player.y) <= 1 else 0.0


def on_kill(game, mon):
    p = game.player
    if unstoppable(game) and not mon.is_npc:
        p.stamina = game.stats()['max_stamina']
    if mon.is_npc:
        return
    from . import spellmap as SM
    for m in _jobs(game):
        d = m.data
        if d['line'] == 'restoration' and SM.undead(mon):
            d['laid'] = d.get('laid', 0) + 1
            if d['laid'] == 5:
                game.msg('Five of the restless dead lie still now. The old saint will want to hear it.', 'gold')
        if d['line'] == 'necromancy' and getattr(mon, 'ep_crown', None) == m.id:
            from .entities import Item
            it = Item(game.new_id(), 'quest', 'crown')
            it.name = 'A barrow-king\'s crown'
            it.mission = m.id
            game.spill(game.map, mon.x, mon.y, it)
            game.msg('Its crown rolls from its head into the dust: old gold, green with age.', 'gold')


def poison_free(game):
    return has(game, 'lich')


def turn(game):
    """One turn of yours: Phoenix's flames bite, unless you stand in water."""
    s = st(game)
    if not s.get('flames'):
        return
    p, m = game.player, game.map
    from . import spellmap as SM
    if m.kind != 'over' and SM.under(m, p.x, p.y) in SM.WATERS or m.kind == 'over' and m.tile(p.x, p.y) == D.WATER:
        quench(game, 'The water hisses round you.')
        return
    dmg = max(1, round(game.stats()['max_life'] * FLAME_BITE))
    p.life -= dmg
    game.num(p.x, p.y, f'-{dmg}', (255, 140, 60))
    if p.life <= 0:
        s['flames'] = 0
        game.die('the fire of the Phoenix')


def after_mons(game):
    """After the foes have moved: a sun falls, the winter bites, the storm sparks."""
    m = game.map
    if time_stopped(game):
        return
    suns = getattr(m, 'suns', None)
    if suns:
        for sun in [s for s in suns if s['at'] <= game.turn]:
            suns.remove(sun)
            _sun_falls(game, sun)
            if game.dead:
                return
    w = getattr(m, 'winter', None)
    if w:
        if game.turn > w['until']:
            m.winter = None
        else:
            for o in [o for o in m.mons if not o.is_npc and (o.x, o.y) in w['cells']]:
                if 'slow' in o.effects and o.hold <= 0:
                    o.hold, o.frozen = 2, True
                else:
                    o.effects['slow'] = [2, 0]
    if has(game, 'eye'):
        _sparks(game)


def shown(game):
    """Your Phoenix flames, with your states."""
    n = flames(game)
    return [(f'Burning {n}', (255, 140, 60))] if n else []


def bar_note(game, sid):
    """What the bar shows for an epic instead of its cost."""
    return ('ready', GOLD) if ready(game, sid) else ('spent', (120, 110, 100))


# ------------------------------------------------------------------ the teachers
TEACHERS = {
    'fire': ('the ash hermit', 'in a burnt valley', ['Old Cinder', 'Brother Ashe', 'Mother Smoke', 'Tamsin Coal']),
    'frost': ('the rime witch', 'at a mountain pass', ['Old Hesk', 'Mother Rime', 'Grandmother Ise', 'Skadi Whitehand']),
    'storm': ('the storm hermit', 'on a lightning-split peak', ['Old Thunner', 'Brother Gale', 'Ivo Splitpeak',
                                                                 'Raina Bellward']),
    'restoration': ('the old saint', 'at a crossroads', ['Saint Aldwin', 'Mother Clemence', 'Father Osric',
                                                         'Sister Brigid']),
    'shadow': ('the witch', 'deep in the wood', ['Old Nan Grue', 'Black Agna', 'Mother Hollin', 'Dame Skerra']),
    'necromancy': ('the old gravedigger', 'by a barrow', ['Old Mattock', 'Grim Wenna', 'Barrow Tom', 'Silas Mould']),
    'nature': ('the old druid', 'at a wonder', ['Old Fern', 'Brannoc Oakheart', 'Mother Moss', 'Elowen Greenhand']),
    'beastcraft': ('the old hunter', 'in the wild', ['Old Garth', 'Wenna Longshot', 'Ulf Tracker', 'Hild Fourwinds']),
    'warcraft': ('the old champion', 'near an old battlefield', ['Edric the Grey', 'Old Brann', 'Dame Isolde',
                                                                  'Hakon Oathless']),
    'arcane': ('the magus in exile', 'by a lone tower', ['Magister Quillon', 'Old Vespera', 'Master Orrin',
                                                         'Lady Thessaly']),
    'cunning': ('the old master thief', 'outside a city', ['Old Silk', 'Nimble Jory', 'Mother Latch', 'Fingers Fenn']),
}
assert set(TEACHERS) == set(BY_LINE)
COLD = {'tundra', 'taiga', 'glacier', 'alpine', 'tundra_hills', 'shrubland_cold', 'ice_shelf'}
BURNT = {'volcano', 'ashland', 'burnt', 'scorched', 'lava'}
HOT = BURNT | {'hotpool', 'geyser', 'sinter'}


def is_teacher(site):
    return site is not None and site.kind == 'teacher'


def teachers(game, line=None):
    return [s for s in game.world.sites if is_teacher(s) and (line is None or s.cls == line)]


def place(game, m, world, reach_set):
    """Two teachers of each class, each in another part of the world. Placed last, with dice of their own, so the
    rest of the world comes out as it did."""
    state = random.getstate()
    random.seed(game.seed * 6263 + 13)
    try:
        for line in TEACHERS:
            names = TEACHERS[line][2][:]
            random.shuffle(names)
            first = None
            for k in range(2):
                st_ = _place_one(game, m, world, reach_set, line, names[k], first)
                first = first or st_
    finally:
        random.setstate(state)


def _cands(game, m, world, line):
    """Where a teacher of this school may live, best spots first."""
    from . import seasons as SN
    w = m.w
    sites = world.sites

    def near_sites(kinds, lo, hi):
        out = []
        for s in sites:
            if s.kind in kinds:
                out += [(s.x + dx, s.y + dy) for dx in range(-hi, hi + 1) for dy in range(-hi, hi + 1)
                        if lo <= max(abs(dx), abs(dy))]
        return out

    def by_cell(pred):
        return [(i % w, i // w) for i in range(len(m.t)) if pred(i)]

    mount = {i for i, t in enumerate(m.t) if t == D.MOUNTAIN}

    def by_mountain(i):
        return any(i + o in mount for o in (1, -1, w, -w, w + 1, w - 1, -w + 1, -w - 1))

    if line == 'fire':
        return by_cell(lambda i: SN.biome(m, i) in BURNT) or by_cell(lambda i: SN.biome(m, i) in ('badlands', 'desert'))
    if line == 'frost':
        return by_cell(lambda i: SN.biome(m, i) in COLD and by_mountain(i)) or by_cell(by_mountain)
    if line == 'storm':
        return by_cell(lambda i: m.t[i] == D.HILLS and by_mountain(i)) or by_cell(by_mountain)
    if line == 'restoration':
        road = D.ROAD
        return by_cell(lambda i: m.t[i] != road and sum(1 for o in (1, -1, w, -w) if 0 <= i + o < len(m.t) and
                                                         m.t[i + o] == road) >= 1 and
                       sum(1 for o in (1, -1, w, -w, w + 1, w - 1, -w + 1, -w - 1, 2, -2, 2 * w, -2 * w)
                           if 0 <= i + o < len(m.t) and m.t[i + o] == road) >= 4)
    if line == 'shadow':
        return near_sites(('circle',), 3, 7) or by_cell(lambda i: m.t[i] in (D.FOREST, D.SWAMP) and
                                                        world.road_dist[i] >= 6)
    if line == 'necromancy':
        return near_sites(('barrow',), 3, 6)
    if line == 'nature':
        out = []
        for nm, x, y in world.wonders:
            out += [(x + dx, y + dy) for dx in range(-6, 7) for dy in range(-6, 7) if 3 <= max(abs(dx), abs(dy))]
        return out
    if line == 'beastcraft':
        return by_cell(lambda i: m.t[i] in (D.FOREST, D.HILLS) and world.road_dist[i] >= 8)
    if line == 'warcraft':
        return near_sites(('oldfield',), 3, 6) or near_sites(('fort',), 3, 6)
    if line == 'arcane':
        return near_sites(('tower',), 3, 6)
    if line == 'cunning':
        out = []
        for s in world.settlements:
            if s.is_city:
                out += [(s.x + dx, s.y + dy) for dx in range(-8, 9) for dy in range(-8, 9) if 4 <= max(abs(dx), abs(dy))]
        return out
    return []


def _place_one(game, m, world, reach_set, line, name, first):
    from .sites import Site
    w = m.w
    taken = [(s.x, s.y) for s in world.settlements] + [(q.x, q.y) for q in world.sites] + \
            [(d.x, d.y) for d in world.dungeons.values()] + [(h.x, h.y) for h in world.holds]
    bad = (D.ROAD, D.TOWN, D.CITY, D.ENTR, D.RIVER, D.CASTLE, D.FORT, D.WATER)

    def free(x, y):
        if not (4 <= x < w - 4 and 4 <= y < m.h - 4):
            return False
        i = y * w + x
        return (i in reach_set and D.TILES[m.t[i]].walk and m.t[i] not in bad and i not in world.wonder_cells
                and all(cheb(x, y, a, b) >= 3 for a, b in taken))

    cands = _cands(game, m, world, line)
    random.shuffle(cands)

    def among(gap):
        for x, y in cands:
            if not free(x, y):
                continue
            if first is not None:
                if cheb(x, y, first.x, first.y) < gap:
                    continue
                if gap >= 60 and world.region_at(x, y).faction == first.faction:
                    continue                            # never both with the same people
            return x, y
        return None

    def wild(gap):                                     # nothing fits: somewhere wild, far from the first
        for _t in range(4000):
            x, y = random.randint(4, w - 5), random.randint(4, m.h - 5)
            if free(x, y) and world.road_dist[y * w + x] >= 4 and (first is None or cheb(x, y, first.x, first.y) >= gap):
                return x, y
        return None

    spot = (among(0) or wild(0)) if first is None else (among(150) or among(100) or among(60) or wild(60) or among(30) or
                                           among(0) or wild(0))
    if not spot:
        return None
    site = Site(len(world.sites), 'teacher', spot[0], spot[1], f"{name}'s Hut")
    site.faction = world.region_at(*spot).faction
    site.cls, site.who, site.teacher = line, TEACHERS[line][0], name
    site.hidden, site.found, site.alive, site.died = True, False, True, None
    world.sites.append(site)
    return site


def daily(game):
    """Each season a teacher may die (old age, a war, a raid); when both of a school are gone, a pupil takes up the
    work elsewhere after a season."""
    if game.day % SEASON:
        return
    from . import folk as FK
    w = game.world
    for site in teachers(game):
        if site.alive and random.random() < .04:
            site.alive, site.died = False, game.day
            if site.id in st(game)['heard'] or not FK.unfound(site):
                game.msg(f'Word goes round that {site.teacher}, {site.who} {TEACHERS[site.cls][1]}, is dead. '
                         'Raiders came through, or only the years.', 'info')
    for line in TEACHERS:
        ts = teachers(game, line)
        if ts and all(not s.alive and s.died is not None and game.day - s.died >= SEASON for s in ts) \
                and not any(getattr(s, 'pupil', False) and s.alive for s in ts):
            _pupil(game, line, ts)


def _pupil(game, line, old):
    w = game.world
    om = game.maps['over']
    used = {s.teacher for s in old}
    names = [n for n in TEACHERS[line][2] if n not in used] or TEACHERS[line][2]
    reach = {i for i, t in enumerate(om.t) if D.TILES[t].walk}
    site = _place_one(game, om, w, reach, line, random.choice(names), None)
    if site:
        site.pupil = True
        for s in old:
            s.died = None                              # mourned: no second pupil for them


def hear(game, npc=None):
    """A rumour: from rank 35 in a class of yours, someone knows of a teacher of it."""
    from . import classes as CL
    from . import folk as FK
    p = game.player
    s = st(game)
    lines = [c for c in CL.classes(game) if p.disc[c][0] >= HEAR_AT]
    pool = [t for t in teachers(game) if t.cls in lines and t.alive and t.id not in s['heard']]
    if not pool:
        return None
    ox, oy = game.over_pos if game.cur != 'over' else (p.x, p.y)
    t = min(pool, key=lambda q: cheb(q.x, q.y, ox, oy))
    s['heard'].add(t.id)
    if FK.unfound(t):
        FK.discover(game, t, None)
    from .engine import dir_name
    from . import jobs as JB
    where = JB._region(game, t.x, t.y)
    game.msg(f'You have heard of {t.teacher}, {t.who}. The hut is on your map now.', 'gold')
    return (f'They say {t.teacher} still lives {TEACHERS[t.cls][1]}, {where}, to the {dir_name(t.x - ox, t.y - oy)}: '
            f'{t.who}, who knew {CL.school(t.cls)} like nobody living. Few find the way, and fewer are taught.')


# ------------------------------------------------------------------ the hut
def site_map(game, site):
    state = random.getstate()
    random.seed(game.seed * 4421 + site.x * 977 + site.y * 37 + 7)
    try:
        m = _hut(game, site)
    finally:
        random.setstate(state)
    if site.alive:
        from .entities import make_npc
        hx, cy = m.hut
        o = make_npc(game, site.teacher, 'teacher', '#e8d098', hx + 2, cy, True)
        o.site = site.id
        m.mons.append(o)
    return m


GROUND = {'fire': D.ASH, 'frost': D.SNOW, 'storm': D.BAREROCK}


def _hut(game, site):
    from .entities import GameMap
    w, h = 50, 30
    line = site.cls
    m = GameMap(site.map_key, 'town', site.name, w, h, GROUND.get(line, GRASS))
    m.glows, m.lights, m.signs = [], [], []
    m.radius, m.sid, m.hid = 60, None, None
    m.site, m.teacher = site.id, True
    m.level = game.world.danger_at(site.x, site.y) + 2
    ground = GROUND.get(line, GRASS)
    for i in range(len(m.t)):
        if random.random() < (.18 if line in ('beastcraft', 'shadow', 'nature') else .05):
            m.t[i] = TREE if ground == GRASS else D.RUBBLE if line != 'frost' else ground
    cy = h // 2
    hx, hy = 24, cy - 3
    for y in range(hy - 1, hy + 7):
        for x in range(hx - 1, hx + 8):
            m.set(x, y, ground)
    for y in range(hy, hy + 6):
        for x in range(hx, hx + 7):
            m.set(x, y, WALL if y in (hy, hy + 5) or x in (hx, hx + 6) else FLOOR)
    m.set(hx, cy, DOOR)
    m.set(hx + 5, hy + 1, D.BED)
    m.set(hx + 4, hy + 4, D.FIREPIT)
    m.glows.append((hx + 4, hy + 4, (255, 140, 50), 4))
    m.hut = (hx, cy)
    from .nature import path
    path(m, (0, cy), (hx - 1, cy), PATH, (ground, TREE, D.RUBBLE))
    if line == 'storm':                                 # the old bell on the top, up a path of rock
        bx, by = hx + 3, 3
        for y in range(by, hy):
            m.set(bx, y, PATH)
        for dx in (-1, 0, 1):
            m.set(bx + dx, by - 1, D.MOUNTAIN)
        m.set(bx, by, D.BELL)
        m.set(bx, hy, DOOR)
        m.bell = (bx, by)
    m.entry = (0, cy)
    for i in range(len(m.seen)):
        m.seen[i] = 1
    m.lights = list(m.glows)
    return m


def on_enter(game, site, m):
    if not is_teacher(site):
        _place_errand(game, site, m)
        return
    if not site.alive:
        m.mons = [o for o in m.mons if getattr(o, 'role', '') != 'teacher']
        game.msg('The hut is cold. Nobody has lived here for a while, and the door hangs open.', 'info')
        return
    game.msg({'fire': 'Ash lies thick on the ground here, and nothing grows.',
              'frost': 'Snow, and wind off the pass. A thin smoke goes up from the hut.',
              'storm': 'The rock up here is split and blackened. A bell hangs on the top above the hut.',
              'restoration': 'The roads meet not far off. Someone has kept a little garden by the hut.',
              'shadow': 'The trees lean in close. Things hang from the eaves that you would rather not look at.',
              'necromancy': 'Spades lean on the wall, and the earth round the hut has been turned many times.',
              'nature': 'Everything grows here, more than it should. Birds sit on the roof and watch you.',
              'beastcraft': 'Hides are stretched to dry on frames round the hut. Something big was skinned here.',
              'warcraft': 'A post in the yard is hacked to splinters. An old shield hangs over the door.',
              'arcane': 'Signs are cut into the door frame, and they move when you are not looking at them.',
              'cunning': 'A neat little cottage. Too neat: three locks on the door, and they all look new.'}[site.cls],
             'info')


# ------------------------------------------------------------------ talking to a teacher
def talk(game, npc):
    from . import events as EV
    from . import classes as CL
    site = game.world.sites[npc.site]
    p, s = game.player, st(game)
    line = site.cls
    s['heard'].add(site.id)
    school = CL.school(line)
    if line not in CL.classes(game):
        game.say(npc, f'"I teach only those who walk the way of {school}. That is not your way, and nothing I know '
                      'would help you."')
        return
    if p.disc[line][0] < TEACH_AT:
        game.say(npc, f'"Not yet. Come back when {school} is deeper in you." ({school} {TEACH_AT})')
        return
    job = _job(game, line)
    if not s['deeds'].get(line):
        if job is None:
            text, done = DEED[line]
            EV.ask(game, 'epic', npc.name, f'{site.teacher} looks at you a long time. "{text}"',
                   [('Take the deed', 'deed'), ('Not now', 'bye')], site=site.id)
            return
        if deed_done(game, job):
            finish(game, job, site)
        else:
            opts = []
            if line == 'frost' and winter_night(game):
                opts.append(('Sit out the night outside, without fire', 'night'))
            if line == 'warcraft' and getattr(game.map, 'duel', None) is None:
                opts.append(('Fight the duel now', 'duel'))
            if opts:
                EV.ask(game, 'epic', npc.name, f'"{DEED[line][1]}"', opts + [('Not yet', 'bye')], site=site.id)
            else:
                game.say(npc, f'"{DEED[line][1]}"')
            return
    _teach(game, site, npc)


def _teach(game, site, npc):
    from . import events as EV
    s = st(game)
    line = site.cls
    have = s['learnt'].get(line)
    opts = []
    for sid in BY_LINE[line]:
        if sid == have:
            continue
        sk = EPICS[sid]
        opts.append((f'Forget {EPICS[have].name}, learn {sk.name}' if have else f'Learn {sk.name}', 'learn:' + sid))
    body = ' '.join(f'{EPICS[sid].name}: {EPICS[sid].text}' for sid in BY_LINE[line])
    say = (f'"You know {EPICS[have].name}. If you want the other, I will take it back and give you that instead."'
           if have else '"You did what I asked. Two things I can teach you, and you may have one of them."')
    EV.ask(game, 'epic', npc.name, f'{say} {body}', opts + [('Goodbye', 'bye')], site=site.id)


def learn(game, sid, quiet=False):
    """Take this epic; it goes on key 6 in the elite's place (the elite stays known)."""
    p, s = game.player, st(game)
    sk = EPICS[sid]
    old = s['learnt'].get(sk.line)
    if old and old in p.known:
        p.known.remove(old)
        for i, b in enumerate(p.bar):
            if b == old:
                p.bar[i] = None
    s['learnt'][sk.line] = sid
    if sid not in p.known:
        p.known.append(sid)
    while len(p.bar) < 6:
        p.bar.append(None)
    p.bar[5] = sid
    if not quiet:
        game.msg(f'You learn {sk.name}. It is on [6] now, in the elite\'s place.', 'gold')
        from . import chronicle as CH
        site = game.world.sites[game.map.site] if getattr(game.map, 'teacher', False) else None
        CH.deed(game, f'An epic: {sk.name}', f'{site.teacher if site else "A teacher"} taught you {sk.name}.')


def r_epic(game, choice, ctx):
    site = game.world.sites[ctx['site']]
    if choice == 'deed':
        start_deed(game, site)
    elif choice == 'night':
        sit_out(game, site)
    elif choice == 'duel':
        start_duel(game, site)
    elif choice and choice.startswith('learn:'):
        learn(game, choice[6:])
        game.end_turn(1)


# ------------------------------------------------------------------ the deeds
DEED = {
    'fire': ('Bring me an ember from the heart of a fire mountain. A glowing one, mind: one that has not gone out.',
             'An ember, still glowing. I can wait. The fire cannot.'),
    'frost': ('Live through a winter night outside my hut, without a fire. Then we will talk.',
              'A winter night, outside, no fire. Come when the snow lies and the dark is down.'),
    'storm': ('There is an old bell on the top above my hut. Ring it in a thunderstorm, and come down alive.',
              'The bell, in a thunderstorm. Not in a drizzle.'),
    'restoration': ('Five of the restless dead walk who should lie still. Lay five of them to rest.',
                    'Five of the restless dead. Lay them to rest, then come back.'),
    'shadow': ('The priests keep a relic on their altar and call it holy. Bring it to me.',
               'The relic from the altar. They will not give it to you; take it.'),
    'necromancy': ('A wight lies in a barrow not far from here, and wears a crown that was never his. Bring me the '
                   'crown.', 'The crown out of the barrow. The wight will not hand it over.'),
    'nature': ('Take this seed to another wonder of the world and put it in the ground there. Come back when it has '
               'come up: a season.', 'The seed, at another wonder, and a season for it to come up.'),
    'beastcraft': ('There is a beast out there they tell stories about. Track it, kill it, and bring me its hide.',
                   'The hide of the beast they tell of. Bring it.'),
    'warcraft': ('Win a duel against me. No hireling, no drink.', 'A duel. You, me, and nobody else. Say when.'),
    'arcane': ('Bring me a page that was lost: a page of the old empire, from a library or from the ground. I will '
               'copy it and give it back.', 'A lost page of the Varnish. Read one, then come.'),
    'cunning': ('A baron keeps a strongbox in his hall. Take something out of it, and let nobody see you do it.',
                'The baron\'s strongbox, and nobody sees you. Nobody.'),
}
TITLES = {'fire': 'An ember from the heart', 'frost': 'A winter night', 'storm': 'The bell in the storm',
          'restoration': 'Five laid to rest', 'shadow': 'The relic on the altar', 'necromancy': 'The barrow crown',
          'nature': 'A seed at a wonder', 'beastcraft': 'The beast of the story', 'warcraft': 'A duel',
          'arcane': 'A lost page', 'cunning': 'The baron\'s strongbox'}


def _jobs(game):
    from . import missions as MS
    return [m for m in MS.active(game) if m.kind == 'epic']


def _job(game, line):
    return next((m for m in _jobs(game) if m.data['line'] == line), None)


def start_deed(game, site):
    from . import missions as MS
    from . import jobs as JB
    from .engine import dir_name
    w = game.world
    line = site.cls
    if len(MS.active(game)) >= MS.MAX_ACTIVE:
        game.msg(f'You carry too many jobs already ({MS.MAX_ACTIVE} at most).', 'bad')
        return
    m = MS.Mission(game.new_id(), 'epic', None)
    m.faction = None
    m.reward = 0
    m.rep = 0
    d = m.data = dict(line=line, site=site.id, giver_name=site.teacher)
    m.title = f'{site.who.capitalize()}\'s deed: {TITLES[line].lower()}'
    m.desc = DEED[line][0]
    if line == 'fire':
        spot = _fire_spot(game, site)
        d['spot'] = spot
        m.desc += f' The nearest fire is {JB._region(game, *spot)}, to the {dir_name(spot[0] - site.x, spot[1] - site.y)}.'
        game.reveal_place(*spot)
    elif line == 'shadow':
        t = _nearest(game, site, lambda s: s.kind == 'temple')
        d['temple'] = t.id if t else None
        if t:
            m.desc += f' The nearest is {t.name}, to the {dir_name(t.x - site.x, t.y - site.y)}.'
            game.reveal_place(t.x, t.y)
    elif line == 'necromancy':
        b = _nearest(game, site, lambda s: s.kind == 'barrow')
        d['barrow'] = b.id if b else None
        if b:
            m.desc += f' It is {b.name}, to the {dir_name(b.x - site.x, b.y - site.y)}.'
            game.reveal_place(b.x, b.y)
    elif line == 'nature':
        spot, name = _wonder_spot(game, site)
        d.update(spot=spot, where=name, planted=None)
        m.desc += f' The nearest other wonder is {name}, to the {dir_name(spot[0] - site.x, spot[1] - site.y)}.'
        from .entities import Item
        it = Item(game.new_id(), 'quest', 'seed')
        it.name = 'A druid\'s seed'
        it.mission = m.id
        game.add_to_inv(it)
    elif line == 'beastcraft':
        from . import named as NM
        n = NM.make(game, site.x, site.y, 'beast', 'notorious')
        d['nid'] = n.id if n else None
        if n:
            m.desc += f' They call it {n.Full}, and it keeps {JB._region(game, n.x, n.y)}.'
            game.reveal_place(n.x, n.y)
    elif line == 'arcane':
        from . import varnish as VN
        d['pages_at'] = len(VN.st(game)['pages'])
    elif line == 'cunning':
        t = _nearest(game, site, lambda s: s.kind == 'seat' and not getattr(s, 'fallen', False))
        d['seat'] = t.id if t else None
        if t:
            m.desc += f' The nearest is {t.name}, to the {dir_name(t.x - site.x, t.y - site.y)}.'
            game.reveal_place(t.x, t.y)
    m.state = 'active'
    game.missions.append(m)
    game.msg(f'Job accepted: {m.title}.', 'gold')


def _nearest(game, site, pred):
    cands = [s for s in game.world.sites if pred(s)]
    return min(cands, key=lambda s: cheb(s.x, s.y, site.x, site.y)) if cands else None


def _fire_spot(game, site):
    from . import seasons as SN
    om = game.maps['over']
    for kinds in (('volcano', 'lava'), BURNT, HOT):
        cells = [i for i in range(len(om.t)) if SN.biome(om, i) in kinds]
        if cells:
            i = min(cells, key=lambda i: cheb(i % om.w, i // om.w, site.x, site.y))
            return i % om.w, i // om.w
    rf = getattr(game.world, 'rift', None)
    if rf:
        return rf['x'], rf['y']
    return site.x, site.y


def _wonder_spot(game, site):
    w = game.world
    others = [(nm, x, y) for nm, x, y in w.wonders if cheb(x, y, site.x, site.y) > 8 and nm != 'The Sky-Seat']
    if others:
        nm, x, y = min(others, key=lambda q: cheb(q[1], q[2], site.x, site.y))
        return (x, y), nm
    from . import nature as NT
    ns = [s for s in w.sites if NT.is_nature(s)]
    if ns:
        s = min(ns, key=lambda q: cheb(q.x, q.y, site.x, site.y))
        return (s.x, s.y), s.name
    return (site.x, site.y), 'the wonder'


def deed_done(game, m):
    d, p = m.data, game.player
    line = d['line']
    items = [it for it in p.inv if getattr(it, 'mission', None) == m.id]
    if line in ('fire', 'shadow', 'necromancy', 'cunning'):
        return any(it.t in ('ember', 'relic', 'crown', 'loot') for it in items)
    if line == 'restoration':
        return d.get('laid', 0) >= 5
    if line == 'beastcraft':
        return any(it.k == 'trophy' and getattr(it, 'named', None) == d.get('nid') for it in p.inv)
    if line == 'arcane':
        from . import varnish as VN
        return len(VN.st(game)['pages']) > d.get('pages_at', 0)
    return bool(d.get('done'))


def finish(game, m, site):
    p = game.player
    line = m.data['line']
    if line == 'beastcraft':
        hide = next((it for it in p.inv if it.k == 'trophy' and getattr(it, 'named', None) == m.data.get('nid')), None)
        if hide:
            p.inv.remove(hide)
    p.inv = [it for it in p.inv if getattr(it, 'mission', None) != m.id]
    m.state = 'done'
    st(game)['deeds'][line] = True
    game.msg(f'Job done: {m.title}.', 'gold')
    from . import chronicle as CH
    CH.deed(game, TITLES[line], f'You did the deed {site.teacher}, {site.who}, asked of you: '
            f'{TITLES[line].lower()}.')
    game.gain_xp(60 + p.lvl * 4)
    npc = next((o for o in game.map.mons if getattr(o, 'site', None) == site.id and o.is_npc), None)
    if npc:
        _teach(game, site, npc)


def target_pos(game, m):
    w, d = game.world, m.data
    site = w.sites[d['site']]
    if deed_done(game, m) or d['line'] in ('frost', 'storm', 'warcraft', 'arcane', 'restoration'):
        return (site.x, site.y), site.name
    line = d['line']
    if line == 'fire':
        return tuple(d['spot']), 'the fire'
    if line == 'nature':
        if d.get('planted') is not None or any(getattr(it, 'mission', None) == m.id for it in game.player.inv):
            return tuple(d['spot']), d['where']
    for key in ('temple', 'barrow', 'seat'):
        if d.get(key) is not None:
            s = w.sites[d[key]]
            return (s.x, s.y), s.name
    if line == 'beastcraft' and d.get('nid') is not None:
        from . import named as NM
        n = NM.get(game, d['nid'])
        if n and n.alive:
            return (n.x, n.y), n.Full
    return (site.x, site.y), site.name


def over_step(game):
    """On the world map: the heart of the fire, a wonder to plant at."""
    p = game.player
    for m in _jobs(game):
        d = m.data
        if d['line'] == 'fire' and d.get('spot') and cheb(p.x, p.y, *d['spot']) <= 2 \
                and not any(getattr(it, 'mission', None) == m.id for it in p.inv):
            from .entities import Item
            it = Item(game.new_id(), 'quest', 'ember')
            it.name = 'A glowing ember'
            it.mission = m.id
            if game.add_to_inv(it):
                game.msg('Where the ground is hottest you find it: an ember that does not go out, glowing in a pot of '
                         'clay you fill with ash. It is warm through the clay.', 'gold')
        if d['line'] == 'nature' and d.get('spot') and cheb(p.x, p.y, *d['spot']) <= 3:
            seed = next((it for it in p.inv if getattr(it, 'mission', None) == m.id), None)
            if seed and d.get('planted') is None:
                p.inv.remove(seed)
                d['planted'] = game.day
                game.msg(f'You put the druid\'s seed in the ground by {d["where"]}. Now it needs a season.', 'gold')
            elif d.get('planted') is not None and not d.get('done') and game.day - d['planted'] >= SEASON:
                d['done'] = True
                game.msg('Where you planted the seed a sapling stands, already knee high, its leaves the green of '
                         'spring whatever the season. The druid will know.', 'gold')


def winter_night(game):
    from . import calendar as CAL
    from . import towns as TW
    return CAL.season(game.day) == 'winter' and TW.is_night(game)


def sit_out(game, site):
    """The rime witch's deed: the night outside her hut, with no fire. It costs life; the cold decides how much."""
    from . import towns as TW
    m = _job(game, 'frost')
    if not m or not winter_night(game):
        return
    p = game.player
    p.x, p.y = game.map.hut[0] + 3, game.map.hut[1] + 3     # outside, with your back to the south wall
    n = 0
    while TW.is_night(game) and n < D.DAY_LEN and not game.dead:
        game.end_turn(1, True)
        n += 1
    s = game.stats()
    game.msg('You sit down in the snow with your back to the wall of the hut. The cold comes in, and in, and in.',
             'bad')
    game.hurt(s['max_life'] * .7, 'the winter night', 'cold')
    if game.dead:
        return
    m.data['done'] = True
    game.msg('The sky goes grey, then pale. You are alive, and you cannot feel your hands.', 'gold')


def start_duel(game, site):
    from .entities import make_monster
    m = game.map
    npc = next((o for o in m.mons if getattr(o, 'site', None) == site.id and o.is_npc), None)
    if not npc:
        return
    m.mons.remove(npc)
    o = make_monster(game, 'knight', npc.x, npc.y, game.player.lvl + 2)
    o.name = site.teacher
    o.duel, o.awake, o.site_of = True, True, site.id
    m.mons.append(o)
    m.duel = o.id
    game.msg(f'{site.teacher} takes the old shield down from over the door. Your company stand back to watch.', 'bad')


def end_duel(game, won):
    m = game.map
    o = next((o for o in m.mons if getattr(o, 'duel', False)), None)
    m.duel = None
    if o is None:
        return
    site = game.world.sites[o.site_of]
    m.mons.remove(o)
    from .entities import make_npc
    npc = make_npc(game, site.teacher, 'teacher', '#e8d098', o.x, o.y, True)
    npc.site = site.id
    m.mons.append(npc)
    job = _job(game, 'warcraft')
    if won:
        if job:
            job.data['done'] = True
        game.msg(f'{site.teacher} lowers the blade and laughs, short of breath. "Enough. You have it. Talk to me."',
                 'gold')
    else:
        game.msg(f'{site.teacher} stops a hand\'s breadth from your throat. "Not today. Come back when you are '
                 'better."', 'bad')


def duel_blow(game, mon, dmg):
    """A blow on the old champion: he yields before he falls."""
    if getattr(mon, 'duel', False) and mon.hp - dmg <= mon.maxhp * .2:
        mon.hp = max(1, round(mon.maxhp * .2))
        end_duel(game, True)
        return 0
    return dmg


def on_drink(game):
    if getattr(game.map, 'duel', None) is not None:
        game.msg('"No drink, I said."', 'bad')
        end_duel(game, False)


def bump(game, x, y, t):
    """A teacher's bell, the relic on a temple's altar, the baron's strongbox. Returns the turns it took, or None."""
    m = game.map
    if getattr(m, 'teacher', False) and t == D.BELL and getattr(m, 'bell', None) == (x, y):
        from . import weather as WX
        job = _job(game, 'storm')
        if WX.current(game) in ('storm', 'drystorm'):
            game.fx('sky', col=(255, 255, 255))
            game.fx('line', cells=[(x, y - k) for k in range(0, 4)][::-1], col=STORM)
            game.shake()
            game.msg('You heave on the rope and the bell booms out over the peak. The sky answers: the stroke hits the '
                     'bell, and you.', 'bad')
            game.hurt(game.stats()['max_life'] * .2, 'the lightning', 'lightning')
            if job and not game.dead:
                job.data['done'] = True
                game.msg('You are alive. The bell still hums under your hands.', 'gold')
        else:
            game.msg('The bell rings out over the rocks, thin under a quiet sky.' +
                     (' It wants a thunderstorm.' if job else ''), 'info')
        return 1
    site = game.world.sites[m.site] if getattr(m, 'site', None) is not None else None
    if t == D.ALTAR and site is not None and site.kind == 'temple':
        job = _job(game, 'shadow')
        if job and job.data.get('temple') == site.id and not any(getattr(it, 'mission', None) == job.id
                                                                  for it in game.player.inv):
            from .entities import Item
            from . import crime as CR
            it = Item(game.new_id(), 'quest', 'relic')
            it.name = 'A saint\'s finger bone in a silver case'
            it.mission = job.id
            game.add_to_inv(it)
            game.msg('You lift the relic off the altar and put it under your coat.', 'bad')
            seen = _watched(game, 8)
            CR.commit(game, 20, 'robbing a temple', 1.0 if seen else .15)
            return 1
    if t == D.CHEST and getattr(m, 'ep_box', None) == (x, y):
        job = _job(game, 'cunning')
        if job and not any(getattr(it, 'mission', None) == job.id for it in game.player.inv):
            if _watched(game, 7):
                game.msg('Not with someone there to see it. Nobody may see you.', 'bad')
                return 0
            from .entities import Item
            it = Item(game.new_id(), 'quest', 'loot')
            it.name = 'The baron\'s seal ring'
            it.mission = job.id
            game.add_to_inv(it)
            game.msg('The lock gives with a click. Inside, on velvet, lies the baron\'s seal ring. It goes in your '
                     'sleeve, and the lid goes down again.', 'gold')
            return 1
    return None


def _watched(game, r):
    """Whether anyone who would raise the alarm can see you, unless you sneak."""
    p = game.player
    if any(b[0] == 'sneak' for b in p.buffs):
        return False
    return any(o.is_npc and not getattr(o, 'ally', False) and o.role not in ('dog', 'livestock', 'cat') and
               cheb(o.x, o.y, p.x, p.y) <= r and game.visible(o.x, o.y) for o in game.map.mons)


def _place_errand(game, site, m):
    """The strongbox in a baron's hall."""
    job = _job(game, 'cunning')
    if job and job.data.get('seat') == site.id and getattr(m, 'ep_box', None) is None:
        fl = [(i % m.w, i // m.w) for i, t in enumerate(m.t) if t == FLOOR]
        if fl:
            x, y = max(fl, key=lambda c: cheb(c[0], c[1], *m.entry) + random.random())
            m.set(x, y, D.CHEST)
            m.ep_box = (x, y)
            game.msg('Somewhere in this hall stands the baron\'s strongbox.', 'info')


def on_level(game, m, dg):
    """A barrow's crowned wight, on its deepest level."""
    site = game.world.sites[dg.site] if getattr(dg, 'site', None) is not None else None
    if site is None or site.kind != 'barrow' or getattr(m, 'ep_wight', False):
        return
    job = _job(game, 'necromancy')
    if not job or job.data.get('barrow') != site.id or job.data.get('wight_put'):
        return
    from .entities import make_monster
    p = game.player
    fl = [(i % m.w, i // m.w) for i, t in enumerate(m.t) if t == FLOOR and not m.mon_at(i % m.w, i // m.w)]
    if not fl:
        return
    x, y = max(fl, key=lambda c: cheb(c[0], c[1], p.x, p.y) + random.random())
    o = make_monster(game, 'wight', x, y, m.level + 2 if hasattr(m, 'level') else p.lvl + 2, elite=1)
    o.ep_crown = job.id
    o.name = 'The Crowned Wight'
    m.mons.append(o)
    m.ep_wight = True
    job.data['wight_put'] = True
    game.msg('Somewhere below, metal scrapes on stone, slowly, as if something were getting up.', 'bad')


def register():
    from . import events as EV
    from . import jobs as JB
    EV.RESOLVERS['epic'] = r_epic
    JB.LABEL['epic'] = 'A teacher\'s deed'
    JB.KINDS.add('epic')


register()
