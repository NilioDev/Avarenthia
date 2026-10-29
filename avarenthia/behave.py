"""What the new kinds do beyond walking up and hitting you, and the states they can leave you in.

Each kind in creatures.py names one or two behaviours (beh). Dangerous moves are announced a turn ahead, as the
charge is: a web weaver lifts its abdomen, a goblin lights a fuse, a shade priestess gathers the shadows. Step aside.

Your own states (p.status: name -> turns left):
held       you cannot step away until you tear free (a strength roll each try); bites on you land
paralysed  you cannot act for a turn or two; afterwards a few turns in which it cannot happen again
asleep     as paralysed, but a blow wakes you
slowed     everything gets two moves to your one
confused   your feet do not always go where you send them
afraid     your blows falter now and then
blinded    in a cloud of darkness: you see almost nothing
diseased   no natural healing until cured or it passes
cursed     you deal less damage and heal less
weakened   your strength drained: you deal less damage
charmed    you cannot bring yourself to strike the one who charmed you"""
import random

from . import data as D
from . import weapons as WP
from .worldgen import cheb, free_around

STATUS = {
    'held': ('Held', (220, 220, 230)), 'paralysed': ('Paralysed', (255, 214, 90)), 'asleep': ('Asleep', (160, 160, 220)),
    'slowed': ('Slowed', (159, 216, 255)), 'confused': ('Confused', (230, 160, 230)), 'afraid': ('Afraid', (230, 200, 120)),
    'blinded': ('Blinded', (130, 120, 160)), 'diseased': ('Diseased', (170, 190, 90)), 'cursed': ('Cursed', (190, 110, 220)),
    'weakened': ('Weakened', (200, 150, 130)), 'charmed': ('Charmed', (240, 160, 220)),
    'hexed': ('Hexed', (150, 200, 110)),
}
STATUS_END = {'held': 'You are free.', 'paralysed': 'You can move again.', 'asleep': 'You wake.',
              'slowed': 'Your limbs warm and quicken.', 'confused': 'Your head clears.', 'afraid': 'The fear passes.',
              'blinded': 'The darkness lifts.', 'diseased': 'The fever breaks. You feel yourself again.',
              'cursed': 'The curse fades.', 'weakened': 'Your strength comes back.', 'charmed': 'The charm wears off.',
              'hexed': 'The hex lifts. You are yourself again.'}
HELPLESS = ('paralysed', 'asleep')
AREA_MODES = ('around', 'chain', 'storm', 'target_area', 'volley')

# old kinds that are female or male each (the rest stay 'it')
GENDERED = {'rat', 'kobold', 'goblin', 'gobarcher', 'jackal', 'wolf', 'bandit', 'brigand', 'orc', 'spider', 'ogre', 'cultist',
            'troll', 'soldier', 'crossbow', 'knight', 'mercenary', 'druid', 'warden', 'raider', 'robber_knight', 'watchman',
            'huntsman', 'deputy', 'sheriff', 'merchant', 'drake', 'clansman', 'thunderer', 'bat'}
FIXED_GENDER = {'ice_witch': 'f', 'broodmother': 'f', 'warlord': 'm', 'drowned_king': 'm', 'lich': 'f', 'snagtooth': 'm',
                'ratking': 'm', 'grolm': 'm'}
PRON = {'f': ('she', 'her', 'her', 'female'), 'm': ('he', 'his', 'him', 'male'), None: ('it', 'its', 'it', '')}


# ------------------------------------------------------------------ small helpers
def beh(mon, b):
    return not mon.is_npc and b in mon.tpl.get('beh', ())


def he(mon):
    return PRON[getattr(mon, 'gender', None)][0]


def his(mon):
    return PRON[getattr(mon, 'gender', None)][1]


def him(mon):
    return PRON[getattr(mon, 'gender', None)][2]


def cap(s):
    return s[0].upper() + s[1:] if s else s


def The(mon):
    return cap(mon.the())


def family(mon):
    return mon.tpl.get('family') or mon.k


def is_leader(mon):
    return not mon.is_npc and (beh(mon, 'leader') or mon.tpl.get('chief') or getattr(mon, 'named', None) is not None)


def on_spawn(game, mon):
    """Give a new monster its sex and its looks."""
    d = mon.tpl
    g = d.get('gender', 'mf' if mon.k in GENDERED else None)
    g = FIXED_GENDER.get(mon.k, g)
    mon.gender = random.choice('fm') if g == 'mf' else g if g in ('f', 'm') else None
    looks = d.get('looks')
    if looks:
        mon.look = fill(random.choice(looks), mon)
    if beh(mon, 'burrow') or beh(mon, 'ambush') or beh(mon, 'disguise'):
        mon.lurk = True
    if beh(mon, 'unseen'):
        mon.invis = 999
    if beh(mon, 'shield'):
        mon.shield = 3
    if beh(mon, 'phase'):
        mon.faded, mon.phase_t = False, random.randint(1, 3)


def noun(mon):
    d = mon.tpl
    ns = d.get('nouns')
    if ns and mon.gender in ('f', 'm'):
        return ns[0] if mon.gender == 'f' else ns[1]
    return d.get('noun', d['name'].lower())


def fill(text, mon):
    a, b, c, sex = PRON[getattr(mon, 'gender', None)]
    if not sex:
        text = text.replace('{sex} ', '')
    return text.format(noun=noun(mon), he=a, his=b, him=c, sex=sex)


# ------------------------------------------------------------------ your states
def status(game):
    p = game.player
    if not hasattr(p, 'status'):
        p.status = {}
    return p.status


def has(game, k):
    return status(game).get(k, 0) > 0


def give(game, k, turns, text=None):
    """Put a state on you. Paralysis and sleep cannot come again for a few turns after they end."""
    st = status(game)
    from . import epics as EP
    if k in HELPLESS + ('slowed', 'held') and EP.unstoppable(game):
        return False                                 # Unstoppable: nothing stops you
    if k in HELPLESS and (st.get('steady', 0) > 0 or any(st.get(h, 0) > 0 for h in HELPLESS)):
        return False
    if k in HELPLESS:
        from . import trees as TT
        if TT.no_stun(game):                         # Bulwark: a shield in hand keeps you on your feet
            return False
        turns = min(turns, 2)
    if k == 'diseased' and any(b[0] == 'hale' for b in game.player.buffs) and random.random() < .5:
        return False                                 # wild garlic bread and fever tea: hale and hearty
    st[k] = max(st.get(k, 0), turns)
    if text:
        game.msg(text, 'bad')
    return True


def clear(game, k, quiet=False):
    st = status(game)
    if st.pop(k, None) and not quiet:
        game.msg(STATUS_END.get(k, ''), 'good')
    if k == 'held':
        game.player.held_by = None
    if k in HELPLESS:
        st['steady'] = 6


def cure(game, kinds=('diseased', 'cursed', 'confused', 'blinded', 'afraid', 'slowed', 'weakened', 'charmed')):
    """A priest, an antidote or Purify: lift what can be lifted."""
    n = 0
    for k in kinds:
        if has(game, k):
            clear(game, k, quiet=True)
            n += 1
    return n


def shown(game):
    """Your states as (label, colour) for the panel."""
    from . import epics as EP
    return [(STATUS[k][0], STATUS[k][1]) for k, t in status(game).items() if t > 0 and k in STATUS] + WP.shown(game) + \
        EP.shown(game)


def tick(game):
    """One turn of your states."""
    st = status(game)
    p = game.player
    for k in list(st):
        if k == 'held':
            src = getattr(p, 'held_by', None)
            if src is not None:
                o = next((o for o in game.map.mons if o.id == src), None)
                if not o or cheb(o.x, o.y, p.x, p.y) > 1:
                    clear(game, 'held')
                    continue
        st[k] -= 1
        if st[k] <= 0:
            del st[k]
            if k in STATUS_END:
                game.msg(STATUS_END[k], 'good')
            if k == 'held':
                p.held_by = None
            if k in HELPLESS:
                st['steady'] = 6


def helpless(game):
    return any(has(game, k) for k in HELPLESS)


def on_hurt(game):
    if has(game, 'asleep'):
        clear(game, 'asleep')


def natural_regen(game):
    return not has(game, 'diseased')


def heal_mult(game):
    return .5 if has(game, 'cursed') else 1.0


def dmg_malus(game):
    """Percent off your damage from your states."""
    return (20 if has(game, 'cursed') else 0) + (10 if has(game, 'afraid') else 0) + (15 if has(game, 'weakened') else 0)


def sight(game, r):
    return 1 if has(game, 'blinded') else r


def before_move(game, dx, dy):
    """Your states when you try to step or strike. Returns (dx, dy, spent): spent is the turn cost if the try used it up."""
    p, m = game.player, game.map
    if m.kind == 'over':
        return dx, dy, None
    if has(game, 'confused') and random.random() < .4:
        dx, dy = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)])
        game.msg('You stumble the wrong way.', 'bad')
    mon = m.mon_at(p.x + dx, p.y + dy)
    if mon and not mon.is_npc:
        if has(game, 'charmed') and getattr(p, 'charmed_by', None) == mon.id:
            game.msg(f'You cannot bring yourself to strike {mon.the()}.', 'bad')
            return dx, dy, 1
        if has(game, 'afraid') and random.random() < .35:
            game.msg('Your nerve fails you. You hang back.', 'bad')
            return dx, dy, 1
        return dx, dy, None
    if has(game, 'held'):
        s = game.stats()
        if random.random() < .2 + s['str'] / 150:
            clear(game, 'held', quiet=True)
            game.msg('You tear yourself free!', 'good')
        else:
            game.msg(random.choice(['You strain, but you are held fast.', 'You cannot pull free.',
                                    'You struggle, and stay where you are.']), 'bad')
        return dx, dy, 1
    return dx, dy, None


# ------------------------------------------------------------------ traps
def traps(m):
    if not hasattr(m, 'traps'):
        m.traps = {}
    return m.traps


def stepped(game):
    """You step on a kobold snare."""
    p, m = game.player, game.map
    t = traps(m).pop((p.x, p.y), None)
    if t is None:
        return
    kind = getattr(m, 'trap_kind', {}).pop((p.x, p.y), None)
    if kind in ('wire', 'pit'):                                         # a goblin hole (delves.py)
        from . import delves as DV
        if kind == 'wire':
            DV.wire(game)
        else:
            DV.pit(game, t)
        return
    if kind == 'plate':                                                 # a trap corridor (themes.py)
        game.flash([(p.x, p.y)], (200, 200, 220), '^', .3)
        game.msg('A plate clicks under your foot. Darts spit from the walls!', 'bad')
        game.hurt(max(2, t), 'a dart trap')
        return
    game.flash([(p.x, p.y)], (220, 200, 120), '^', .3)
    game.msg('A snare snaps shut on your leg!', 'bad')
    game.hurt(max(2, t), 'a kobold snare')
    if not game.dead:
        give(game, 'held', 3)
        p.held_by = None


def spot_traps(game):
    """Traps you can see: those laid in your sight, and those you notice walking close."""
    p, m = game.player, game.map
    for (x, y), v in list(traps(m).items()):
        if cheb(x, y, p.x, p.y) <= 1 and game.visible(x, y) and random.random() < .25 + game.player.dex / 200:
            if (x, y) not in getattr(m, 'known_traps', set()):
                m.known_traps = getattr(m, 'known_traps', set()) | {(x, y)}
                game.msg('You spot a pressure plate in the floor.' if getattr(m, 'trap_kind', {}).get((x, y)) == 'plate'
                         else 'You spot a snare in the dirt.', 'info')


# ------------------------------------------------------------------ monster strength
def ally_near(game, mon, r=1, same_family=True):
    fam = family(mon)
    for o in game.map.mons:
        if o is not mon and not o.is_npc and (not same_family or family(o) == fam) and cheb(o.x, o.y, mon.x, mon.y) <= r:
            return o
    return None


def leader_near(game, mon):
    if mon.pack is None or is_leader(mon):
        return None
    for o in game.map.mons:
        if o is not mon and o.pack == mon.pack and is_leader(o) and cheb(o.x, o.y, mon.x, mon.y) <= 7:
            return o
    return None


def sun(game):
    """Daylight in the open: creatures of the deep fight worse in it."""
    from . import towns as TW
    m = game.map
    return m.kind in ('wild', 'siege') and not getattr(m, 'underground', False) and not TW.is_night(game)


def attack_mult(game, mon):
    """How hard it hits, beyond its level."""
    k = 1.0
    ld = leader_near(game, mon)
    if ld:
        k *= 1.3 if 'Warcry' in ld.mods else 1.15
    if 'frenzy' in mon.effects:
        k *= 1.3
    if beh(mon, 'formation') and ally_near(game, mon):
        k *= 1.1
    if beh(mon, 'sunblind') and sun(game):
        k *= .7
    if getattr(mon, 'ambush_ready', False):
        mon.ambush_ready = False
        k *= 1.8
        game.msg(f'{The(mon)} strikes from hiding!', 'bad')
    if beh(mon, 'backstab') and any(o is not mon and not o.is_npc and cheb(o.x, o.y, game.player.x, game.player.y) <= 1
                                    for o in game.map.mons):
        k *= 1.5
    return k


def hit_bonus(game, mon):
    b = 0.0
    if beh(mon, 'formation') and ally_near(game, mon):
        b += .08
    if beh(mon, 'sunblind') and sun(game):
        b -= .12
    if has(game, 'held') and getattr(game.player, 'held_by', None) == mon.id:
        b += 1
    if helpless(game):
        b += 1
    return b


def incoming(game, mon, dmg, weapon, elem):
    """Damage you deal to it after its habits: faded, a swarm, a shield wall."""
    if mon.is_npc:
        return dmg
    if getattr(mon, 'faded', False):
        game.msg(f'Your blow passes through {mon.the()}.', 'info')
        return None
    area = getattr(game, '_area', False)
    if beh(mon, 'blur') and not area and random.random() < .3:
        game.msg(f'Your blow strikes only an image; {mon.the()} was a step to one side.', 'info')
        return None
    if beh(mon, 'swarm'):
        if elem == 'fire' or area:
            dmg *= 2
        elif weapon:
            dmg *= .5
    guarded = (beh(mon, 'formation') and ally_near(game, mon)) or getattr(mon, 'shield', 0) > 0
    over = guarded and weapon and WP.over_shield(game)        # a flail's head swings over the shield
    if over:
        game.flash([(mon.x, mon.y)], WP.C_SPARK, ']', .15)
    elif beh(mon, 'formation') and ally_near(game, mon):
        dmg *= .8
    if getattr(mon, 'shield', 0) > 0 and not over:
        mon.shield -= 1
        game.msg(f'{The(mon)} turns the blow aside.', 'info')
        dmg *= .25
    if beh(mon, 'slag'):
        from . import rift as RF
        dmg = RF.incoming(game, mon, dmg, elem)
    if weapon and beh(mon, 'metal'):
        game.wear('weapon', .8)
        if random.random() < .25:
            game.msg(f"{The(mon)}'s feelers brush your weapon. The metal flakes away.", 'bad')
    return dmg


def struck(game, mon, dmg):
    """After it takes a blow from you: thorns, a phase spider fading out of reach."""
    if 'Thorny' in mon.mods and dmg > 0 and not game.dead:
        game.msg(f"{The(mon)}'s thorns cut you.", 'bad')
        game.hurt(max(1, round(dmg * .15)), mon.the())
    if beh(mon, 'slag') or beh(mon, 'ash'):
        from . import rift as RF
        RF.struck(game, mon, dmg)


# ------------------------------------------------------------------ on a hit
def on_hit(game, mon, dmg):
    """It has hit you: what its bite leaves behind."""
    p = game.player
    if game.dead:
        return
    name = The(mon)
    if beh(mon, 'grab') and not has(game, 'held') and random.random() < .4:
        give(game, 'held', random.randint(3, 5), f'{name} seizes you! You are held fast.')
        p.held_by = mon.id
    if beh(mon, 'paralyse') and random.random() < .25:
        w = mon.tpl.get('hit_word', 'bite')
        give(game, 'paralysed', random.randint(1, 2), f"{name}'s {w} {'numb' if w.endswith('s') else 'numbs'} you. You cannot move!")
    if (beh(mon, 'slows') or 'Frost-touched' in mon.mods) and random.random() < .35:
        give(game, 'slowed', random.randint(3, 5), 'The cold of the bite slows your limbs.')
    if beh(mon, 'disease') and random.random() < .3 and not has(game, 'diseased'):
        give(game, 'diseased', random.randint(150, 260), 'The bite festers. You feel feverish. (Diseased: no natural healing)')
    if 'Cursing' in mon.mods and random.random() < .2:
        give(game, 'cursed', 30, f'{name} speaks a word that sticks to you. You are cursed.')
    if 'Venomous' in mon.mods and random.random() < .4:
        p.poison = [5, max(1, mon.lvl // 2)]
    if beh(mon, 'acid') or beh(mon, 'metal'):
        game.wear(None, .9)
        if random.random() < .3:
            game.msg('Acid hisses on your armour.' if beh(mon, 'acid') else 'It gnaws at your armour.', 'bad')
    if beh(mon, 'latch') and not getattr(mon, 'latched', False):
        mon.latched = True
        game.msg(f'{name} fastens onto you and starts to drink!', 'bad')
    if beh(mon, 'eatfood') and random.random() < .35:
        food = [it for it in p.inv if it.k == 'food']
        if food:
            it = random.choice(food)
            game.remove_one(it)
            game.msg(f'{name} gets into your pack and devours your {it.name.lower()}!', 'bad')
    if beh(mon, 'knockback') and random.random() < .4:
        push(game, mon)
    if beh(mon, 'drain') and random.random() < .3:
        give(game, 'weakened', random.randint(40, 70), f"{name}'s touch is cold. Strength drains out of you. (Weakened)")
    if beh(mon, 'mindsip') and p.mana > 0 and random.random() < .5:
        n = min(p.mana, max(3, mon.dmg[1]))
        p.mana -= n
        game.msg(f'{name} drinks at your thoughts. Your mana runs out of you.', 'bad')
    if beh(mon, 'unseen') and getattr(mon, 'invis', 0):
        mon.invis = 0
        game.msg(f'{name} flickers into sight!', 'bad')
    if beh(mon, 'greedy') and not getattr(mon, 'stolen', 0) and p.gold > 50 and random.random() < .3:
        n = min(p.gold, max(20, round(p.gold * random.uniform(.04, .1))), 2500)
        p.gold -= n
        mon.stolen = n
        mon.fleeing = True
        from .money import fmt
        game.msg(f'{name} snatches {fmt(n)} from your purse and runs!', 'bad')


def push(game, mon):
    """Knocked back: up to two cells away from it; into a wall hurts."""
    p, m = game.player, game.map
    from . import epics as EP
    if EP.unstoppable(game):
        return
    dx, dy = (p.x > mon.x) - (p.x < mon.x), (p.y > mon.y) - (p.y < mon.y)
    moved = 0
    for _ in range(2):
        nx, ny = p.x + dx, p.y + dy
        if m.inb(nx, ny) and m.tile(nx, ny) == D.AIR and getattr(m, 'sky', None) is not None:
            from . import towers as TOW
            TOW.thrown(game, nx, ny)                        # knocked off a tower
            return
        if not m.inb(nx, ny) or not D.TILES[m.tile(nx, ny)].walk or game.occupied(m, nx, ny):
            if not (m.inb(nx, ny) and D.TILES[m.tile(nx, ny)].walk):
                game.msg('You slam into the wall.', 'bad')
                game.hurt(max(1, mon.dmg[0] // 2), mon.the())
            break
        p.x, p.y = nx, ny
        moved += 1
    if moved:
        game.msg(f'{The(mon)} sends you flying!', 'bad')
        game.shake()


# ------------------------------------------------------------------ special moves
def _line_ok(game, mon):
    p = game.player
    return game.visible(mon.x, mon.y) and game.line_clear(mon.x, mon.y, p.x, p.y)


def _blast(game, cx, cy, r, mon, mult, elem, col, ch='*'):
    """A burst of something nasty around a cell: hurts you if you are in it, and anything else caught."""
    p, m = game.player, game.map
    cells = [(x, y) for x in range(cx - r, cx + r + 1) for y in range(cy - r, cy + r + 1) if m.inb(x, y)]
    game.flash(cells, col, ch, .3)
    hit = cheb(p.x, p.y, cx, cy) <= r
    if hit:
        game.hurt(random.randint(*mon.dmg) * mult, mon.the(), elem)
    for o in m.mons[:]:
        if o is not mon and not o.is_npc and cheb(o.x, o.y, cx, cy) <= r and o in m.mons:
            o.hp -= max(1, round(random.randint(*mon.dmg) * mult * .6))
            if o.hp <= 0:
                game.kill(o)
    return hit


def turn(game, mon, df):
    """Special moves before the usual ones. Returns True if the monster used its turn."""
    if _turn(game, mon, df):
        return True
    if beh(mon, 'rooted'):          # a plant or a stonemaw: it bites what comes near, and nothing else
        return not mon.dmg[1] or cheb(mon.x, mon.y, game.player.x, game.player.y) > 1
    return False


def _turn(game, mon, df):
    p, m = game.player, game.map
    dist = cheb(mon.x, mon.y, p.x, p.y)
    seen = game.visible(mon.x, mon.y)
    name = The(mon)
    d = mon.tpl
    if getattr(mon, 'named', None) is not None:
        from . import named as NM
        if NM.mon_turn(game, mon, df):
            return True
    # an ambusher that is already aware of you waits, unseen, until you come close
    if getattr(mon, 'lurk', False):
        if dist <= (1 if beh(mon, 'disguise') else 2) and seen:
            from . import ai as AI
            AI.on_wake(game, mon)
            return True
        return True
    # the Ashen Deep (rift.py): a gaoler runs for the gong, a chain warden hooks you, a toad spits sulphur
    if beh(mon, 'gaoler') or beh(mon, 'hook') or beh(mon, 'sulphur'):
        from . import rift as RF
        if beh(mon, 'gaoler') and RF.gaoler(game, mon, dist, seen):
            return True
        if beh(mon, 'hook') and RF.hook(game, mon, dist):
            return True
        if beh(mon, 'sulphur') and RF.sulphur(game, mon, dist):
            return True
    # a totem does nothing but tend its band
    if beh(mon, 'still'):
        if random.random() < .5:
            band = [o for o in m.mons if o is not mon and not o.is_npc and o.pack == mon.pack and cheb(o.x, o.y, mon.x, mon.y) <= 5]
            if band:
                o = random.choice(band)
                if getattr(mon, 'kind', 'heal') == 'heal' and o.hp < o.maxhp:
                    from . import bosses as BS
                    if BS.st(o):                                 # a boss takes only a little, and not past its phase
                        o.hp = min(BS.cap_hp(o), o.hp + max(2, o.maxhp // 40))
                    else:
                        o.hp = min(o.maxhp, o.hp + max(2, o.maxhp // 8))
                    game.flash([(o.x, o.y)], (120, 240, 140), '+', .25)
                else:
                    o.effects['frenzy'] = [4, 0]
                    game.flash([(o.x, o.y)], (255, 80, 60), '!', .25)
        return True
    # the phase spider flickers in and out of the world
    if beh(mon, 'phase'):
        mon.phase_t = getattr(mon, 'phase_t', 1) - 1
        if mon.phase_t <= 0:
            mon.faded = not getattr(mon, 'faded', False)
            mon.phase_t = random.randint(1, 3) if mon.faded else random.randint(2, 3)
            if seen:
                game.msg(f"{name} {'fades out of the world' if mon.faded else 'flickers back, solid'}.", 'info')
        if mon.faded and dist <= 1:
            return True
    # a latched bloodsucker clings and drinks
    if getattr(mon, 'latched', False):
        if dist > 1:
            spot = [c for c in free_around(game, m, p.x, p.y, 1)]
            if spot and random.random() < .8:
                mon.x, mon.y = min(spot, key=lambda c: cheb(c[0], c[1], mon.x, mon.y))
                dist = 1
            else:
                mon.latched = False
                return False
        n = max(1, mon.dmg[0] // 2 + 1)
        game.msg(f'{name} drinks your blood.', 'bad')
        game.hurt(n, mon.the())
        mon.hp = min(mon.maxhp, mon.hp + n)
        return True
    # moths shed a choking dust on everything close
    if beh(mon, 'dust') and dist <= 1 and random.random() < .5:
        game.flash([(mon.x + dx, mon.y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)], (200, 190, 150), ':', .25)
        game.msg(f'{name} beats {his(mon)} wings; a choking dust falls on you.', 'bad')
        game.hurt(max(1, mon.dmg[0] // 2), mon.the())
        return True
    # a move announced last turn
    aim = getattr(mon, 'readying', None)
    if aim:
        mon.readying = None
        return _release(game, mon, aim, df)
    if beh(mon, 'walls') and dist > 1 and _through_wall(game, mon):
        return True
    if not seen or getattr(mon, 'fleeing', False):
        return _misc(game, mon, dist, seen)
    # moves that need a turn of warning
    if beh(mon, 'wail') and dist <= 6 and not has(game, 'afraid') and random.random() < .2:
        mon.readying = ('wail', p.x, p.y)
        game.msg(f'{name} draws in a long breath that is not air...', 'bad')
        return True
    if beh(mon, 'gaze') and 2 <= dist <= 7 and _line_ok(game, mon) and random.random() < .22:
        mon.readying = ('gaze', p.x, p.y)
        game.msg(f'{name} fixes {his(mon)} eyes on you...', 'bad')
        game.flash([(mon.x, mon.y)], (255, 120, 160), '!', .4)
        return True
    if beh(mon, 'web') and 2 <= dist <= 6 and not has(game, 'held') and _line_ok(game, mon) and random.random() < .3:
        mon.readying = ('web', p.x, p.y)
        game.msg(f'{name} lifts {his(mon)} abdomen towards you...', 'bad')
        return True
    if beh(mon, 'pounce') and 2 <= dist <= 5 and _line_ok(game, mon) and random.random() < .35:
        mon.readying = ('pounce', p.x, p.y)
        game.msg(f'{name} crouches low, ready to spring...', 'bad')
        game.flash([(p.x, p.y)], (255, 200, 80), '!', .4)
        return True
    if beh(mon, 'bomb') and 2 <= dist <= 6 and _line_ok(game, mon) and random.random() < .3:
        mon.readying = ('bomb', p.x, p.y)
        game.msg(f'{name} lights {his(mon)} fuse...', 'bad')
        game.flash([(p.x, p.y)], (255, 140, 60), '!', .4)
        return True
    if beh(mon, 'stink') and 2 <= dist <= 6 and _line_ok(game, mon) and random.random() < .2:
        mon.readying = ('stink', p.x, p.y)
        game.msg(f'{name} swings a reeking pot over {his(mon)} head...', 'bad')
        return True
    if beh(mon, 'acidcloud') and dist <= 2 and random.random() < .35:
        mon.readying = ('cloud', mon.x, mon.y)
        game.msg(f'{name} turns {his(mon)} back on you, {his(mon)} tail end smoking...', 'bad')
        return True
    if beh(mon, 'acidspit') and 2 <= dist <= 4 and _line_ok(game, mon) and random.random() < .3:
        mon.readying = ('spit', p.x, p.y)
        game.msg(f'{name} rears up, {his(mon)} throat working...', 'bad')
        return True
    if beh(mon, 'darkness') and 2 <= dist <= 7 and not has(game, 'blinded') and random.random() < .2:
        mon.readying = ('dark', p.x, p.y)
        game.msg(f'{name} draws the shadows together...', 'bad')
        game.flash([(p.x + dx, p.y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)], (80, 70, 110), '░', .4)
        return True
    # moves without warning (not dangerous in themselves)
    if beh(mon, 'shriek') and not getattr(mon, 'shrieked', False):
        mon.shrieked = True
        n = 0
        for o in m.mons:
            if not o.is_npc and o is not mon and not o.awake and cheb(o.x, o.y, mon.x, mon.y) <= 30:
                o.awake, n = True, n + 1
        game.flash([(mon.x, mon.y)], (230, 200, 255), '!', .4)
        game.msg(f'{name} screams, a long rising shriek.' + (' Everything on the level wakes.' if n else ''), 'bad')
        return True
    if beh(mon, 'stench') and dist <= 1 and not has(game, 'slowed') and random.random() < .25:
        give(game, 'slowed', 3, f'The stench of {mon.the()} turns your stomach. You retch and stagger.')
        return True
    if beh(mon, 'pollen') and dist <= 2 and random.random() < .25:
        game.flash([(mon.x + dx, mon.y + dy) for dx in (-2, -1, 0, 1, 2) for dy in (-2, -1, 0, 1, 2)], (240, 180, 220), '°', .3)
        game.msg(f'{name} sheds a cloud of sweet pollen.', 'bad')
        if random.random() * 100 >= game.stats()['res_poison']:
            give(game, 'asleep', 2, 'Your eyes close by themselves...')
        return True
    if beh(mon, 'pull') and 2 <= dist <= 4 and _line_ok(game, mon) and random.random() < .3:
        spots = free_around(game, m, mon.x, mon.y, 1)
        if spots:
            game.flash(game.line_clear(mon.x, mon.y, p.x, p.y)[:-1] or [(p.x, p.y)], (230, 120, 140), '~', .2)
            p.x, p.y = min(spots, key=lambda c: cheb(c[0], c[1], p.x, p.y))
            game.msg(f"{name}'s tongue lashes out and drags you in!", 'bad')
            return True
    if beh(mon, 'babble') and dist <= 4 and not has(game, 'confused') and random.random() < .2:
        give(game, 'confused', 3, f'The babbling of {mon.the()} gets into your head. The world tilts.')
        return True
    if beh(mon, 'charm') and dist <= 4 and not has(game, 'charmed') and random.random() < .15:
        give(game, 'charmed', random.randint(3, 5), mon.tpl.get('charm_msg', '{name} smiles at you')
             .format(name=name) + f', and you cannot bring yourself to hurt {him(mon)}. (Charmed)')
        p.charmed_by = mon.id
        return True
    if beh(mon, 'curse') and dist <= 6 and not has(game, 'cursed') and random.random() < .18:
        game.msg(f'{name} points at you and speaks a word that sticks. You are cursed. (Cursed: less damage, less healing)', 'bad')
        give(game, 'cursed', 40)
        return True
    if beh(mon, 'spores') and dist <= 2 and random.random() < .3:
        game.flash([(mon.x + dx, mon.y + dy) for dx in (-2, -1, 0, 1, 2) for dy in (-2, -1, 0, 1, 2)], (180, 200, 120), '°', .3)
        game.msg(f'{name} puffs out a cloud of spores.', 'bad')
        if random.random() * 100 >= game.stats()['res_poison']:
            give(game, 'confused', 3, 'You breathe them in. The world tilts.')
        return True
    if beh(mon, 'totem') and dist <= 8 and not getattr(mon, 'planted', False) and random.random() < .3:
        spots = free_around(game, m, mon.x, mon.y, 1)
        if spots:
            from .entities import make_monster
            x, y = random.choice(spots)
            t = make_monster(game, 'totem', x, y, mon.lvl)
            t.pack, t.awake = mon.pack, True
            t.kind = random.choice(['heal', 'frenzy'])
            t.name = 'Healing Totem' if t.kind == 'heal' else 'Bloodlust Totem'
            m.mons.append(t)
            mon.planted = True
            game.flash([(x, y)], (255, 160, 60), '¶', .3)
            game.msg(f"{name} plants a {t.name.lower()} and howls to it. {'Wounds close around it.' if t.kind == 'heal' else 'The band goes wild.'}", 'bad')
            return True
    if beh(mon, 'enlarge') and dist <= 3 and not getattr(mon, 'enlarged', False):
        mon.enlarged = True
        mon.dmg = tuple(round(v * 1.3) for v in mon.dmg)
        mon.maxhp = round(mon.maxhp * 1.3)
        mon.hp = round(mon.hp * 1.3)
        game.msg(f'{name} swells to twice {his(mon)} height!', 'bad')
        game.flash([(mon.x, mon.y)], (230, 200, 120), '!', .3)
        return True
    if beh(mon, 'invis') and mon.hp < mon.maxhp * .5 and not getattr(mon, 'went_invis', False):
        mon.went_invis = True
        mon.invis = 6
        game.msg(f'{name} fades from sight!', 'bad')
        return True
    if beh(mon, 'climb') and dist <= 1 and random.random() < .35:
        spots = [c for c in free_around(game, m, mon.x, mon.y, 4) if cheb(c[0], c[1], p.x, p.y) >= 3]
        if spots:
            mon.x, mon.y = random.choice(spots)
            game.msg(f'{name} scrambles up the wall and away.', 'info')
            return True
    return _misc(game, mon, dist, seen)


def _misc(game, mon, dist, seen):
    p, m = game.player, game.map
    # kobold trappers lay snares where you will walk
    if beh(mon, 'traps') and dist >= 3 and random.random() < .12 and m.tile(mon.x, mon.y) in (D.FLOOR,):
        tr = traps(m)
        if (mon.x, mon.y) not in tr and len(tr) < 12:
            tr[(mon.x, mon.y)] = max(2, mon.dmg[1])
            if seen:
                m.known_traps = getattr(m, 'known_traps', set()) | {(mon.x, mon.y)}
                game.msg(f'{The(mon)} sets a snare in the dirt.', 'info')
    # kobolds cannot walk past a coin: they pick it up, and it drops again when they fall
    if mon.tpl.get('family') == 'kobold' or mon.k == 'kobold':
        gold = next((i for i in m.items if i.k == 'gold' and (i.x, i.y) == (mon.x, mon.y)), None)
        if gold:
            m.items.remove(gold)
            mon.stolen = getattr(mon, 'stolen', 0) + gold.n
            if seen:
                game.msg(f'{The(mon)} snatches up the coins with a happy squeak.', 'info')
            return True
    # a thief with your coin, or a band whose leader fell, runs
    if getattr(mon, 'fleeing', False) and (getattr(mon, 'stolen', 0) or getattr(mon, 'broken', False)):
        from .ai import step_away
        if step_away(game, mon):
            return True
    if getattr(mon, 'invis', 0):
        mon.invis -= 1
    elif beh(mon, 'unseen') and dist > 2 and random.random() < .15:
        mon.invis = 999
        if seen:
            game.msg(f'{The(mon)} vanishes.', 'info')
    return False


def _through_wall(game, mon):
    """A draugr does not go round: it walks into the rock and out again, nearer to you."""
    p, m = game.player, game.map
    dx, dy = (p.x > mon.x) - (p.x < mon.x), (p.y > mon.y) - (p.y < mon.y)
    x, y = mon.x + dx, mon.y + dy
    if not m.inb(x, y) or D.TILES[m.tile(x, y)].walk or random.random() < .4:
        return False
    for _ in range(5):
        x, y = x + dx, y + dy
        if not m.inb(x, y):
            return False
        if D.TILES[m.tile(x, y)].walk:
            if game.occupied(m, x, y) or (x, y) == (p.x, p.y):
                return False
            mon.x, mon.y = x, y
            if game.visible(x, y):
                game.msg(f'{The(mon)} steps out of the wall!', 'bad')
            return True
    return False


def _release(game, mon, aim, df):
    """The move it warned you of."""
    p, m = game.player, game.map
    kind, tx, ty = aim
    name = The(mon)
    if kind == 'web':
        path = game.line_clear(mon.x, mon.y, p.x, p.y)
        if not path:
            return False
        game.flash(path[:-1], (230, 230, 240), '~', .25)
        if (p.x, p.y) != (tx, ty) and random.random() < .5:
            game.msg(f"{name}'s web strands sail past you.", 'info')
            return True
        give(game, 'held', 3, f'Sticky silk wraps around you. You are caught in the web!')
        p.held_by = None
        return True
    if kind == 'pounce':
        spots = free_around(game, m, tx, ty, 1)
        if (tx, ty) != (p.x, p.y) and m.inb(tx, ty) and D.TILES[m.tile(tx, ty)].walk and not game.occupied(m, tx, ty):
            spots.insert(0, (tx, ty))
        if not spots:
            return True
        x, y = min(spots, key=lambda c: cheb(c[0], c[1], tx, ty))
        from .engine import line
        game.flash(line(mon.x, mon.y, x, y), (232, 200, 80), '*', .2)
        mon.x, mon.y = x, y
        if cheb(x, y, p.x, p.y) <= 1:
            game.msg(f'{name} leaps on you!', 'bad')
            if random.random() < game.mon_hit_chance(mon, df) + .1:
                game.hurt(random.randint(*mon.dmg) * 1.5, mon.the())
                on_hit(game, mon, 0)
        else:
            game.msg(f'{name} leaps, and lands where you stood.', 'info')
        return True
    if kind == 'bomb':
        path = game.line_clear(mon.x, mon.y, tx, ty) or [(tx, ty)]
        game.flash(path[:-1], (255, 140, 60), '•', .2)
        if _blast(game, tx, ty, 1, mon, 1.1, 'fire', (255, 120, 40)):
            game.msg(f"{name}'s fire pot bursts at your feet!", 'bad')
        else:
            game.msg(f"{name}'s fire pot bursts where you stood.", 'info')
        return True
    if kind == 'stink':
        game.flash([(tx + dx, ty + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)], (150, 180, 80), '°', .35)
        if cheb(p.x, p.y, tx, ty) <= 1:
            give(game, 'slowed', 4, f"{name}'s stink pot breaks over you. You retch and stagger.")
        else:
            game.msg(f"{name}'s stink pot breaks where you stood.", 'info')
        return True
    if kind == 'cloud':
        if _blast(game, mon.x, mon.y, 2, mon, .9, 'fire', (220, 220, 90), '°'):
            game.msg(f'{name} sprays a boiling cloud of acid over you!', 'bad')
            game.wear(None, 1.0)
        else:
            game.msg(f'{name} sprays a boiling cloud of acid.', 'info')
        return True
    if kind == 'spit':
        path = game.line_clear(mon.x, mon.y, p.x, p.y)
        if not path or (p.x, p.y) != (tx, ty) and random.random() < .5:
            game.msg(f"{name}'s spit hisses on the ground.", 'info')
            return True
        game.flash(path[:-1], (190, 230, 80), '*', .2)
        game.msg(f'{name} spits acid over your armour!', 'bad')
        game.hurt(random.randint(*mon.dmg) * .8, mon.the())
        game.wear(None, 1.0)
        game.wear(None, 1.0)
        return True
    if kind == 'wail':
        game.fx('wave', x=mon.x, y=mon.y, r=3, col=(220, 230, 255), sign='sound')     # a wail bends out round it
        if cheb(p.x, p.y, mon.x, mon.y) <= 7 and game.visible(mon.x, mon.y):
            give(game, 'afraid', 6, f'{name} wails. The cry goes through you, and your courage drains away. (Afraid)')
        else:
            game.msg(f'{name} wails, far off.', 'info')
        return True
    if kind == 'gaze':
        if not _line_ok(game, mon):
            game.msg(f"{name}'s stare finds only stone.", 'info')
            return True
        st = mon.tpl.get('gaze', 'paralysed')
        if st == 'any':
            st = random.choice(['paralysed', 'confused', 'afraid', None])
        if st is None:
            return False                         # this eye shoots a ray instead
        text = {'paralysed': f'Your limbs stiffen under the gaze of {mon.the()}. You cannot move!',
                'confused': f'The gaze of {mon.the()} dazes you. The world tilts.',
                'afraid': f'You meet the eyes of {mon.the()}, and dread fills you. (Afraid)'}[st]
        give(game, st, {'paralysed': 2, 'confused': 3, 'afraid': 6}[st], text)
        return True
    if kind == 'dark':
        game.flash([(tx + dx, ty + dy) for dx in (-2, -1, 0, 1, 2) for dy in (-2, -1, 0, 1, 2)], (40, 30, 70), '▓', .4)
        if cheb(p.x, p.y, tx, ty) <= 2:
            give(game, 'blinded', 5, 'Darkness swallows you. You can barely see your own hands.')
        else:
            game.msg('A cloud of darkness settles where you stood.', 'info')
        return True
    return False


def shoot_extra(game, mon):
    """An arrow or a spell has hit you: a shade elf's dart puts you to sleep."""
    if beh(mon, 'sleepdart') and random.random() < .25:
        give(game, 'asleep', 2, 'A tiny dart stings your neck. Your eyes grow heavy...')


# ------------------------------------------------------------------ waking and death
def on_wake(game, mon):
    """Out of the ground, out of the dark."""
    if beh(mon, 'disguise'):
        mon.ambush_ready = True
        game.msg(mon.tpl.get('reveal', '{name} was no {thing}!').format(name=The(mon), thing='statue'), 'bad')
        game.flash([(mon.x, mon.y)], (255, 200, 80), '!', .3)
        return True
    if beh(mon, 'ambush'):
        mon.ambush_ready = True
        game.msg(f'{The(mon)} was there all along!', 'bad')
        return True
    if beh(mon, 'burrow'):
        game.msg(f'The ground heaves. {The(mon)} bursts out of the earth!', 'bad')
        game.flash([(mon.x, mon.y)], (170, 130, 80), '!', .25)
        return True
    return False


def on_death(game, mon):
    """A brood bursts, a band breaks, a thief drops your coin."""
    m = game.map
    name = The(mon)
    if getattr(mon, 'stolen', 0):
        from .entities import Item
        game.spill(m, mon.x, mon.y, Item(game.new_id(), 'gold', 'gold', mon.stolen))
        game.msg('Your coin spills on the ground.', 'good')
    if getattr(mon, 'carry', None):
        game.spill(m, mon.x, mon.y, mon.carry)
        game.msg(f'{mon.carry.display_name()} falls to the ground.', mon.carry.rar)
    if beh(mon, 'cinders'):
        from . import rift as RF
        RF.died(game, mon)
    sp = mon.tpl.get('split') or ('Splitting' in mon.mods and mon.k)
    if sp and sp in D.MONSTERS:
        from .entities import make_monster
        spots = free_around(game, m, mon.x, mon.y, 1)
        random.shuffle(spots)
        n = 0
        for x, y in spots[:random.randint(2, 4) if mon.tpl.get('split') else 2]:
            o = make_monster(game, sp, x, y, max(1, mon.lvl - (0 if mon.tpl.get('split') else 3)))
            o.awake, o.pack = True, mon.pack
            m.mons.append(o)
            n += 1
        if n:
            game.flash(spots[:n], (200, 120, 200), '*', .25)
            game.msg(f"{name} bursts open, and {'young spill out' if mon.tpl.get('split') else 'two smaller ones crawl from the wound'}!", 'bad')
    if is_leader(mon) and mon.pack is not None:
        band = [o for o in m.mons if o.pack == mon.pack and not o.is_npc and o is not mon and o.k != 'totem']
        broke = [o for o in band if random.random() < .55]
        for o in broke:
            o.fleeing, o.broken = True, True
        if broke and game.visible(mon.x, mon.y):
            game.msg('With their leader down, the rest break and run!' if len(broke) == len(band) else
                     'With their leader down, some of the band break and run!', 'good')
