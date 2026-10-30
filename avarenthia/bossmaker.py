"""Boss fights part C (round 23): the boss maker and the job bosses.

Fifteen bases (a mage of a school, a necromancer, a cult leader, a witch, a wild druid, a champion of a weapon, a band
leader, an assassin, a hunter, a great beast in the Dwarf Fortress way of body, stuff and attack, a dead lord, a golem,
a chief of a hostile people, a pirate captain, a fey lord). A boss is drawn in steps with rules: its deck from the
move library (bossmoves.py) by role, one set-up and great-blow pair, one weakness, the heaviest blow only from level
eight, a third phase only from level ten, nothing that needs a roof out in the open; then up to two traits, a name, a
title, a deed and one rumour of a move or of the weakness. It fights with the kit of bosses.py (`mon.kit_over`).

Jobs: "A price on a head" on the boards and from the captain, and a boss at the end of the nest, shrine, boats,
missing and deserter jobs. A boss of the people may yield: kill, let go, or hand over. A beast leaves parts of its
body, the same for every class (the loot rule: only those who use gear drop gear). Floors above a fixed boss foretell
it, and the boss's level hides one thing that eases the fight."""
import copy
import random

from . import data as D

# base: monsters it can be, its people (True: it may yield), pools per role, weaknesses, helpers' summons, words
SCHOOLS = {'fire': dict(k=['firebolt'], V=['ring_of_fire'], G=['fireball', 'burning_lines'], Z=['meteor', 'inferno'],
                        weak=('cold',), word='Ashen'),
           'cold': dict(k=['frost_shard'], V=['ice_wall'], G=['cone_cold', 'ice_lance', 'frost_nova'],
                        Z=['blizzard', 'ice_tomb'], weak=('fire',), word='Rimed'),
           'storm': dict(k=['spark'], V=['static_field'], G=['chain_lightning', 'thunderclap', 'ball_lightning'],
                         Z=['call_storm', 'tempest'], weak=('cold',), word='Thundering')}
BASES = {
    'mage': dict(mon=['fallen_mage'], man=True, weak=None, O=[], words=['the {s} Magister', 'the {s} Adept']),
    'necromancer': dict(mon=['fallen_mage', 'cultist'], man=True, k=['bone_spear', 'touch'], V=['bone_prison', 'withering'],
                        G=['corpse_burst', 'life_drain'], Z=['army_dead'], O=['raise_dead'], weak=('fire', 'holy'),
                        words=['the Gravecaller', 'the Bone Saint', 'the Pale Hand']),
    'cult': dict(mon=['cultist'], man=True, k=['shadow_bolt'], V=['curse_weak', 'dread'], G=['morraks_hand', 'life_drain'],
                 Z=['mark_doom'], O=['call_spawn'], weak=('holy',), words=['the Voice Below', 'the Hollow Prophet']),
    'witch': dict(mon=['weald_hag', 'sea_hag'], man=True, k=['shadow_bolt'], V=['hex', 'withering', 'stench'],
                  G=['wail', 'gaze_ray'], Z=['mark_doom'], O=['call_hounds'], weak=('fire',),
                  words=['Mother of the Fen', 'the Crooked Wife']),
    'druid': dict(mon=['druid'], man=True, k=['spark', 'strike'], V=['roots', 'bramble'], G=['stones', 'venom_spit'],
                  Z=['wrath_oak'], O=['call_wolves'], weak=('fire',), words=['the Thornspeaker', 'the Wild Green']),
    'champion': dict(mon=['knight', 'robber_knight'], man=True, k=['strike'], V=['hook', 'sunder', 'hamstring'],
                     G=['cleave', 'whirl', 'charge', 'smash', 'maul'], Z=['executioner'], O=[], R=['riposte', 'shield_wall'],
                     weak=('lightning',), words=['the Unhorsed', 'Ironside', 'the Last Champion']),
    'band': dict(mon=['brigand', 'bandit'], man=True, k=['strike'], V=['pinning_shot', 'hamstring'], G=['volley', 'charge'],
                 Z=['rampage'], O=['call_band'], weak=('cold',), words=['Captain of the Road', 'the Red Hand']),
    'assassin': dict(mon=['bandit'], man=True, k=['strike'], V=['darkness', 'hamstring'], G=['garrote', 'fan_knives'],
                     Z=['executioner'], O=[], B=['shadowstep', 'smoke_bomb'], weak=('holy',),
                     words=['the Quiet Knife', 'No-Face']),
    'hunter': dict(mon=['huntsman'], man=True, k=['spear_throw'], V=['pinning_shot', 'snare_line'], G=['volley', 'charge'],
                   Z=['rampage'], O=['call_hounds'], B=['pounce'], weak=('fire',), words=['the Houndmaster', 'Long-Shot']),
    'beast': dict(mon=None, man=False, k=['bite', 'claw'], V=['roar', 'wing_buffet', 'coil'], G=['maul', 'charge', 'tail_sweep', 'leap'],
                  Z=['rampage'], O=[], weak=None, words=[]),
    'deadlord': dict(mon=['wight', 'ghast_lord'], man=False, k=['touch'], V=['dread', 'grave_mist'], G=['frost_nova', 'wail'],
                     Z=['army_dead'], O=['call_ghouls'], weak=('holy', 'fire'), words=['the Barrow Lord', 'the Unburied Thane']),
    'golem': dict(mon=['clay_golem'], man=False, k=['strike'], V=['sunder'], G=['smash', 'boulder', 'stones'],
                  Z=['earthshaker'], O=[], R=['shed_skin'], weak=('lightning',), words=['the Unmade', 'the Clay Warden']),
    'chief': dict(mon=['orc_chief', 'gnoll_packlord', 'hob_captain', 'gob_boss'], man=True, k=['strike'], V=['roar', 'hook'],
                  G=['charge', 'cleave'], Z=['rampage'], O=['war_cry'], weak=('lightning', 'cold'),
                  words=['Skullbreaker', 'the Gut-Ripper', 'Ironjaw']),
    'pirate': dict(mon=['brigand'], man=True, k=['strike'], V=['hook', 'pinning_shot'], G=['bomb_volley', 'cleave'],
                   Z=['tidal_wave'], O=['call_band'], weak=('lightning',), words=['the Sea Wolf', 'Black Gull']),
    'fey': dict(mon=['dryad', 'shade_elf'], man=False, k=['arcane_bolt'], V=['babble', 'slow_spell', 'runes'],
                G=['gaze_ray', 'starfall'], Z=['stop_time'], O=[], B=['blink'], R=['mirror'], weak=('cold',),
                words=['of the Hollow Hill', 'the Thorn Prince', 'the Pale Queen']),
}
CALLS = {'chief': {'orc_chief': 'war_cry', 'gnoll_packlord': 'call_gnolls', 'hob_captain': 'call_hobs',
                   'gob_boss': 'call_goblins'}}
# the great beast: a body, a stuff it is of, and how it strikes
BODIES = {'brown_bear': 'Bear', 'cave_bear': 'Bear', 'troll': 'Troll', 'ogre': 'Ogre', 'sabretooth': 'Cat',
          'wyvern': 'Wyvern', 'manticore': 'Manticore', 'basilisk': 'Basilisk', 'mammoth': 'Mammoth',
          'great_wolf': 'Wolf', 'drake': 'Drake'}
STUFF = {'fire': ('Ember', ('cold',), ['breath'], 'fire'), 'frost': ('Rime', ('fire',), ['frost_nova'], 'cold'),
         'stone': ('Stone', ('lightning',), ['boulder'], None), 'venom': ('Blight', ('fire',), ['venom_spit', 'acid_spray'], 'poison'),
         'storm': ('Storm', ('cold',), ['thunderclap'], 'lightning')}
TRAITS = ['armoured', 'warded', 'regenerating', 'twinned', 'unbroken', 'vengeful', 'swift', 'mirrored', 'bloodbound',
          'commanding', 'haunting', 'hoarder', 'grudge', 'waller', 'sentry', 'vortex', 'watchful', 'anchored']
TRAIT_WORD = {'armoured': 'armoured', 'warded': 'warded against spells', 'regenerating': 'its wounds close',
              'twinned': 'never alone', 'unbroken': 'hard to stop', 'vengeful': 'worse when hurt', 'swift': 'quick',
              'mirrored': 'turns blows back', 'bloodbound': 'drinks blood', 'commanding': 'calls help',
              'haunting': 'the dead follow it', 'hoarder': 'rich', 'grudge': 'remembers', 'waller': 'raises walls',
              'sentry': 'wards against spells', 'vortex': 'a wind about it', 'watchful': 'never caught unawares',
              'anchored': 'cannot be moved'}
TRAIT_CARD = {'mirrored': ('R', 'mirror'), 'bloodbound': ('R', 'soul_harvest'), 'commanding': ('O', 'call_band'),
              'haunting': ('O', 'raise_dead'), 'waller': ('V', 'ice_wall'), 'sentry': ('R', 'spell_ward'),
              'vortex': ('V', 'gust'), 'swift': ('B', 'pounce'), 'vengeful': ('Z', 'rampage')}
ROOF = {'drop_above', 'kick_prop', 'undermine', 'tunnel', 'tunnel_up', 'earthshaker', 'knot_split', 'deep_calls',
        'drag_under', 'whirlpool', 'tidal_wave'}
FIRST = {'m': ['Aldric', 'Brannoc', 'Dunmore', 'Edric', 'Fennick', 'Harrow', 'Jory', 'Kester', 'Ludo', 'Oswy', 'Piran',
               'Rook', 'Tobin', 'Vane', 'Wulfgar'],
         'f': ['Cedra', 'Gisela', 'Isbet', 'Morwen', 'Nell', 'Sabine', 'Ursel', 'Ysold', 'Brenna', 'Hild', 'Maud']}
DEEDS = ['burned the granary at {t}', 'hanged the reeve of {t}', 'took the tithe-cart on the road to {t}',
         'drowned three fishermen of {t}', 'carried off the miller\'s children of {t}', 'killed the watch at {t} gate',
         'poisoned the well of {t}', 'took the bell from the chapel of {t}']
ELEM_WORD = {'fire': 'fire', 'cold': 'the cold', 'lightning': 'lightning', 'holy': 'holy light', 'poison': 'poison'}
BOON = {'fire': 'a flask of lamp oil', 'cold': 'a jar of snow from a deep cellar', 'lightning': 'a rod of copper',
        'holy': 'a flask of holy water', 'poison': 'a pot of grave-salts'}
FORETELL = {'snagtooth': 'Kobold scratches on the walls point down, and a pot-lid shield is scratched beside them.',
            'lich': 'Frost lies on the stairs going down, though nothing here is cold.',
            'dragon': 'The stone is warm underfoot, and there are scales in the dust as big as your hand.',
            'ratking': 'Rats run past you, all one way: down.',
            'grolm': 'Picks ring somewhere below, and a voice curses the props.',
            'broodmother': 'Webs hang thicker on every stair, and egg shells crunch underfoot.',
            'warlord': 'War drums, far below. Someone is gathering an army.',
            'drowned_king': 'Water seeps up through the stairs, and it smells of the sea.',
            'cinder_lord': 'Ash drifts up the stairs on a hot wind.'}


def moves():
    from . import bosses as BS
    return BS.MOVES


def _pick(rnd, pool, n=1):
    pool = [c for c in pool if c in moves()]
    return rnd.sample(pool, min(n, len(pool))) if pool else []


def draw(game, lvl, base=None, rnd=None, outdoors=True, town=None):
    """A job boss, drawn in steps. Returns the spec: what apply() needs, and the rumour for the job's text."""
    rnd = rnd or random.Random()
    base = base or rnd.choice([b for b in BASES if lvl >= 4 or b not in ('deadlord', 'golem', 'fey')])
    B = BASES[base]
    pools = {r: list(B.get(r, [])) for r in 'kVGZOBR'}
    weak = B['weak']
    word, mon = None, None
    if base == 'mage':
        school = rnd.choice(list(SCHOOLS))
        S = SCHOOLS[school]
        for r in 'kVGZ':
            pools[r] = list(S[r])
        weak, word = S['weak'], S['word']
        mon = 'fallen_mage'
    elif base == 'beast':
        mon = rnd.choice([b for b in BODIES if b in D.MONSTERS])
        stuff = rnd.choice(list(STUFF))
        sw, weak, extra, _el = STUFF[stuff]
        pools['G'] = pools['G'] + extra
        word = sw
    else:
        mon = rnd.choice([k for k in B['mon'] if k in D.MONSTERS])
        if base in CALLS:
            pools['O'] = [CALLS[base][mon]]
    if outdoors:
        for r in pools:
            pools[r] = [c for c in pools[r] if c not in ROOF]
    weak = (rnd.choice(weak),) if weak else ('fire',)
    traits = rnd.sample(TRAITS, rnd.choice((0, 1, 1, 2)) if lvl >= 3 else 0)
    if base == 'golem' and 'regenerating' in traits:
        traits.remove('regenerating')
    for t in traits:
        if t in TRAIT_CARD:
            r, c = TRAIT_CARD[t]
            if c in moves() and (not outdoors or c not in ROOF):
                pools[r] = pools[r] + [c]
    # the deck: one set-up and great pair always; the heaviest from level eight; a third phase from level ten
    k = _pick(rnd, pools['k'], 2) or ['strike']
    V = _pick(rnd, pools['V'], 1)
    G = _pick(rnd, pools['G'], 2) or ['smash']
    Z = _pick(rnd, pools['Z'], 1) if lvl >= 8 else []
    O = _pick(rnd, pools['O'], 1)
    Bm = _pick(rnd, pools['B'], 1)
    R = _pick(rnd, pools['R'], 1)
    ph1 = dict(beat='k' + ('V' if V else '') + 'Gk', cards=dict(k=k, G=G[:1], **({'V': V} if V else {})))
    beat2 = 'k' + ('V' if V else '') + 'G' + ('O' if O else '') + 'k' + ('B' if Bm else '') + ('R' if R else '')
    cards2 = dict(k=k, G=G, **({'V': V} if V else {}), **({'O': O} if O else {}), **({'B': Bm} if Bm else {}),
                  **({'R': R} if R else {}))
    phs = [ph1]
    if lvl >= 10:
        phs.append(dict(at=.66, beat=beat2, cards=cards2, say='{name} stops holding back.',
                        **({'trick': 'call'} if O else {})))
        phs.append(dict(at=.33, beat=beat2 + ('Z' if Z else ''), cards=dict(cards2, **({'Z': Z} if Z else {})),
                        say='{name} is bleeding, and it only makes {him} worse.'))
    else:
        phs.append(dict(at=.5, beat=beat2 + ('Z' if Z else ''), cards=dict(cards2, **({'Z': Z} if Z else {})),
                        say='{name} stops holding back.', **({'trick': 'call'} if O else {})))
    kit = dict(weak=weak, phases=phs, maker=True)
    # the name, the title, the deed and one rumour
    tmpl = D.MONSTERS[mon]
    gender = tmpl.get('gender') if tmpl.get('gender') in ('m', 'f') else rnd.choice('mf')
    if base == 'beast':
        name = f'The {word} {BODIES[mon]}'
        title = 'of ' + _area(game, rnd)
    else:
        name = rnd.choice(FIRST[gender])
        title = rnd.choice(B['words']).format(s=word or '')
    t = town or 'a village nobody names'
    deed = rnd.choice(DEEDS).format(t=t)
    he = 'it' if base in ('beast', 'golem') else ('she' if gender == 'f' else 'he')
    if rnd.random() < .5:
        rumour = f'They say {he} cannot abide {ELEM_WORD.get(weak[0], weak[0])}.'
    else:
        mv = moves()[G[0]]
        rumour = f'They say {he} has a blow called {mv["name"]}: when the ground turns red, do not stand in it.'
    return dict(base=base, mon=mon, lvl=lvl, kit=kit, name=name, title=title, deed=deed, rumour=rumour,
                traits=traits, man=B['man'], weak=weak[0], gender=gender)


def _area(game, rnd):
    areas = [a['name'] for a in (getattr(game.world, 'areas', None) or [])[1:] if a]
    a = rnd.choice(areas) if areas else 'the Wilds'
    return a[0].lower() + a[1:] if a.startswith('The ') else a


def full_name(spec):
    return f"{spec['name']}, {spec['title']}" if not spec['title'].startswith('of ') else f"{spec['name']} {spec['title']}"


def apply(game, mon, spec):
    """Make this monster the drawn boss: its kit, its life, its traits."""
    from . import bosses as BS
    mon.kit_over = copy.deepcopy(spec['kit'])
    mon.bs = dict(phase=0, pending=None, i=0, piles={}, spent=0, stag=0, dots=0, stun=0, resolve=BS.RESOLVE,
                  seen_hold=0, sil=False, engaged=False, took={}, breaks=0, prep=[], weak_t=-1, fed=0)
    mon.name = full_name(spec)
    mon.fg = D.UNIQUE_FG
    if spec['base'] not in ('beast', 'golem'):
        mon.gender = spec.get('gender', 'm')
    mon.maker = dict(spec)
    mult = 3.5 + spec['lvl'] * .1
    mon.maxhp = mon.hp = round(mon.maxhp * mult)
    tr = spec['traits']
    if 'armoured' in tr:
        mon.armoured = True
        mon.df = round(mon.df * 1.3) + 1
    if 'warded' in tr:
        res = dict(mon.__dict__.get('weak_res', {}))
        for el in ('fire', 'cold', 'lightning', 'poison'):
            if el != spec['weak']:
                res[el] = res.get(el, 0) + 30
        mon.weak_res = res
    if 'unbroken' in tr:
        mon.bs['resolve'] = 4
    if 'watchful' in tr or 'anchored' in tr:
        mon.bs['resolve'] += 1
    if 'grudge' in tr:
        mon.maxhp = mon.hp = round(mon.maxhp * 1.15)
    if 'regenerating' in tr:
        mon.regen = True
    return mon


def twin(game, mon, spec):
    """A twinned boss brings its other half: the survivor takes all."""
    from . import bosses as BS
    from .entities import make_monster
    from .worldgen import free_around
    c = free_around(game.map, mon.x, mon.y)
    if not c:
        return None
    o = make_monster(game, mon.k, c[0], c[1], spec['lvl'])
    sp = dict(spec, traits=[t for t in spec['traits'] if t != 'twinned'], name=spec['name'] + "'s twin")
    apply(game, o, sp)
    o.name = f"{spec['name']}'s Shadow"
    game.map.mons.append(o)
    BS.link(mon, o, 'survivor')
    return o


# ------------------------------------------------------------------ in the fight
def on_turn(game, mon):
    """Before it acts: a regenerating boss closes its wounds, unless it burns."""
    if mon.__dict__.get('regen') and mon.hp < mon.maxhp and 'burn' not in getattr(mon, 'effects', {}):
        mon.hp = min(mon.maxhp, mon.hp + max(1, round(mon.maxhp * .02)))


def yields(game, mon):
    """A boss of the people at the end of its strength may yield. True if it does (then it does not die yet)."""
    mk = mon.__dict__.get('maker')
    if not mk or not mk['man'] or mon.__dict__.get('yielded') or random.random() < .4:
        return False
    from . import events as EV
    mon.yielded = True
    mon.hp = 1
    mon.hold = 99
    mon.cast = None
    EV.ask(game, 'yield', mon.name, f'{mon.name} throws down {("her" if mon.__dict__.get("gender") == "f" else "his")} '
           'weapon and goes to one knee. "Enough. Enough! I yield."',
           [('Kill', 'kill'), ('Let go', 'go'), ('Hand over to the law', 'law')], mon=mon.id)
    return True


def r_yield(game, choice, ctx):
    m = game.map
    mon = next((o for o in m.mons if o.id == ctx.get('mon')), None)
    if mon is None:
        return
    from . import chronicle as CH
    if choice == 'kill' or choice is None:
        mon.hp = 0
        mon.maker['man'] = False
        game.kill(mon)
        return
    m.mons.remove(mon)
    if choice == 'go':
        game.msg(f'{mon.name} gets up slowly, and goes, and does not look back.', 'info')
        CH.add(game, 'Your deeds', f'You let {mon.name} go, beaten.', 'seen', quiet=True)
    else:
        game.msg(f'You bind {mon.name} for the law. The bounty is worth more alive.', 'good')
        jf = getattr(game, 'job_fight', None)
        if jf:
            from . import missions as MS
            mj = MS.find(game, jf[0])
            if mj:
                mj.reward = round(mj.reward * 1.25)
        CH.add(game, 'Your deeds', f'You took {mon.name} alive and handed {mon.maker["name"]} to the law.', 'seen',
               quiet=True)


def felled(game, mon):
    """A beast leaves parts of its body; a hoarder its coin; the chronicle remembers the name."""
    mk = mon.__dict__.get('maker')
    if not mk:
        return
    from . import chronicle as CH
    CH.add(game, 'Your deeds', f'You killed {mon.name}, who {mk["deed"]}.', 'seen', where=game.loc_name(), quiet=True)
    if mk['base'] == 'beast':
        from . import beastparts as BP
        from .hunting import SKINS
        row = SKINS.get(mon.k)
        parts = [pt for pt, _c in row[4] if pt in BP.PART] if row else []
        part = random.choice(parts) if parts else random.choice(['fangs', 'claws', 'horn'])
        it = BP.make(game, part, mon.k if row else 'wolf', random.randint(1, 2))
        it.x, it.y = mon.x, mon.y
        game.map.items.append(it)
        game.msg(f'{mon.name} leaves {BP.part_name(it.t).lower()} worth taking.', 'good')
    if 'hoarder' in mk['traits']:
        from .entities import Item
        gold = Item(game.new_id(), 'gold', 'gold', 300 + mk['lvl'] * 120)
        gold.x, gold.y = mon.x, mon.y
        game.map.items.append(gold)
        game.msg('A hoard of coin spills where it fell.', 'gold')


# ------------------------------------------------------------------ the jobs
BOSS_JOBS = ('nest', 'shrine', 'boats', 'missing', 'deserter')


def for_job(game, m, lvl):
    """Give a job its boss, and the rumour to its text."""
    s = game.world.settlements[m.giver] if m.giver is not None else None
    spec = draw(game, lvl, base=_base_for(m.kind), town=s.name if s else None)
    m.data['bspec'] = spec
    m.desc += f' {spec["rumour"]}'
    return m


def _base_for(kind):
    return {'nest': random.choice(['beast', 'chief', 'beast']), 'shrine': random.choice(['cult', 'necromancer', 'deadlord']),
            'boats': random.choice(['beast', 'witch', 'pirate']), 'missing': random.choice(['band', 'witch', 'fey']),
            'deserter': random.choice(['champion', 'band', 'hunter'])}.get(kind)


def wrap(kind, fn):
    def make(game, s, *a, **kw):
        m = fn(game, s, *a, **kw)
        if m is not None and 'bspec' not in m.data:
            for_job(game, m, m.data.get('lvl') or game.world.danger_at(s.x, s.y) + 3)
        return m
    return make


def on_fight(game, m, wild):
    """jobs.fight: the job's leader becomes its boss."""
    spec = m.data.get('bspec')
    if not spec or wild is None:
        return
    mon = next((o for o in wild.mons if not o.is_npc), None)
    if mon is None:
        return
    if mon.k != spec['mon'] and spec['mon'] in D.MONSTERS:
        from .entities import make_monster
        o = make_monster(game, spec['mon'], mon.x, mon.y, spec['lvl'])
        wild.mons[wild.mons.index(mon)] = o
        mon = o
    apply(game, mon, spec)
    if 'twinned' in spec['traits']:
        twin(game, mon, spec)
    game.msg(f'{mon.name} is here. {spec["rumour"]}', 'bad')


def make_head(game, s):
    """A price on a head: a boss of the land, its name, deed and one rumour; harder ones pay more."""
    from . import jobs as JB
    from .worldgen import cheb
    w = game.world
    over = game.maps['over']
    spot = None
    for _ in range(300):
        x, y = s.x + random.randint(-36, 36), s.y + random.randint(-24, 24)
        if not over.inb(x, y) or cheb(x, y, s.x, s.y) < 10:
            continue
        t = over.tile(x, y)
        if not D.TILES[t].walk or t in (D.ROAD, D.TOWN, D.CITY, D.ENTR):
            continue
        if any(cheb(x, y, o.x, o.y) < 6 for o in w.settlements):
            continue
        spot = (x, y)
        break
    if not spot:
        return None
    lvl = w.danger_at(*spot) + 3
    spec = draw(game, lvl, town=s.name)
    helpers = {'band': ['bandit', 'brigand'], 'pirate': ['brigand', 'bandit'], 'chief': ['orc', 'goblin']}.get(spec['base'], [])
    keys = [spec['mon']] + [random.choice(helpers) for _ in range(random.randint(1, 3))] if helpers else [spec['mon']]
    keys = [k for k in keys if k in D.MONSTERS]
    pay = 40 + lvl * 9 + len(spec['traits']) * 15
    name = full_name(spec)
    return JB.mission(game, s, 'head', f'A price on a head: {spec["name"]}',
                      f'{name} {spec["deed"]}. The reeve of {s.name} pays for the head. Last seen to the '
                      f'{JB._dir(s, *spot)}. {spec["rumour"]}', pay, (6, 12), game.day + 30,
                      spot=list(spot), keys=keys, lvl=lvl, leader=name, bspec=spec, reach=1, where=spec['name'],
                      intro=f'{name} turns, and sees you, and knows why you came.')


def won_head(game, m, won):
    from . import jobs as JB
    if not won:
        m.data['cool'] = game.turn + 60
        return
    JB._turnin(game, m, f'{m.data["leader"]} will trouble nobody now.')


# ------------------------------------------------------------------ fixed bosses: foretold, and the thing that eases it
def on_level(game, m, dg, depth):
    """Going down toward a fixed boss: the floor above tells of it; the boss's own floor hides one thing that eases
    its fight."""
    boss = getattr(dg, 'boss', None) if dg else None
    if not boss or boss not in FORETELL:
        return
    told = game.player.__dict__.setdefault('foretold', set())
    if depth == dg.depth - 1 and (dg.id, depth) not in told:
        told.add((dg.id, depth))
        game.msg(FORETELL[boss], 'info')
    from . import bosses as BS
    kt = BS.KITS.get(boss)
    if depth == dg.depth and kt and not getattr(m, 'boon_set', False):
        m.boon_set = True
        weak = kt.get('weak', ('fire',))[0]
        from .entities import Item
        from .worldgen import free_around
        ar = m.__dict__.get('arena')
        cells = set(map(tuple, ar['cells'])) if ar else set()
        spots = [(x, y) for y in range(1, m.h - 1) for x in range(1, m.w - 1) if m.tile(x, y) == D.FLOOR
                 and (x, y) not in cells]
        if spots:
            x, y = random.choice(spots)
            it = Item(game.new_id(), 'boon', weak)
            it.name = BOON.get(weak, 'a strange charm')
            it.x, it.y = x, y
            m.items.append(it)


def boon_edge(game, mon):
    """You carry the thing that eases this fight: the boss starts a step from staggering."""
    p = game.player
    from . import bosses as BS
    kt = BS.kit(mon)
    bs = BS.st(mon)
    if not kt or bs is None or bs.get('boon'):
        return
    it = next((i for i in p.inv if i.k == 'boon' and i.t in kt.get('weak', ())), None)
    if not it:
        return
    bs['boon'] = True
    bs['dots'] = max(bs['dots'], 2)
    p.inv.remove(it)
    game.msg(f'You break {it.name} over {mon.the()}: it shrinks from it. One more good blow, and it reels.', 'gold')


def register():
    from . import events as EV
    from . import jobs as JB
    from . import entities as EN
    EV.RESOLVERS['yield'] = r_yield
    JB.LABEL['head'] = 'A price on a head'
    JB.KINDS.add('head')
    JB.MAKE['head'] = make_head
    JB.ARRIVE['head'] = JB._arrive_fight
    JB.WON['head'] = won_head
    for lst in (JB.TOWN, JB.CITY):
        if 'head' not in lst:
            lst.append('head')
    for k in BOSS_JOBS:
        if k in JB.MAKE and not getattr(JB.MAKE[k], 'boss_wrapped', False):
            JB.MAKE[k] = wrap(k, JB.MAKE[k])
            JB.MAKE[k].boss_wrapped = True
    EN.CRAFT['boon'] = 'bossmaker'


# the thing that eases a fight, as an item
def display(game, it):
    return getattr(it, 'name', 'a strange charm')


def lines(game, it):
    return [f'It might help against something that cannot abide {ELEM_WORD.get(it.t, it.t)}. Carry it into the fight.']


def value(game, it):
    return 2


def glyph(it):
    return '!'


def color(it):
    return (200, 220, 255)


def use(game, it):
    game.msg(lines(game, it)[0], 'info')
    return 0


register()
