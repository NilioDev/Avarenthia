"""Guilds. You may fight for at most two combat guilds, and rivals will not have you both; the guilds of the
crafts take anyone. Each has five ranks, earned with the guild's own jobs. Only a guild master teaches the
advanced techniques, and only to those of high enough rank and skill. Two guilds are secret: the Thieves' Guild
is found through rumours and chalk marks, or it finds you after a crime or two; the Hollow Coven, who serve
Morrak, is found only through those who already know. Their work has a dark side, and the world notices.
The Quiet Ossuary, the necromancers, is half secret: you find it through the old graveyards along the Varnish ways.

Standing with a guild fades slowly if you do nothing for it, but never below the rank you hold;
the secret guilds are less patient and will let you fall."""
import random

from . import data as D
from .worldgen import cheb

RANK_REP = [0, 60, 160, 320, 560]
DECAY_AFTER = 10            # days without a guild job before your standing starts to fade
JOB_REP = 40

GUILDS = {
    'magi': dict(name='The Circle of Magi', short='Magi', kind='combat', secret=0, fg='#8fa8ff', sign='MAGI',
                 master='Archmagus {n}', ranks=['Novice', 'Apprentice', 'Adept', 'Magus', 'Archmagus'], rivals=['coven'],
                 jobs=['hunt', 'fetch', 'bounty', 'courier'], halls=3,
                 desc='Scholars of fire, frost and storm, who keep the old libraries of the cities.'),
    'iron': dict(name='The Iron Company', short='Iron Company', kind='combat', secret=0, fg='#c8ccd8', sign='IRON COMPANY',
                 master='Marshal {n}', ranks=['Recruit', 'Sellsword', 'Sergeant', 'Captain', 'Marshal'], rivals=[],
                 jobs=['hunt', 'escort', 'bounty', 'freight'], halls=3,
                 desc='Sellswords with a code: paid in advance, loyal to the contract, feared on the roads.'),
    'dawn': dict(name='The Order of Dawn', short='Order of Dawn', kind='combat', secret=0, fg='#ffe8a0', sign='ORDER OF DAWN',
                 master='Lord Commander {n}', ranks=['Postulant', 'Acolyte', 'Templar', 'Knight of Dawn', 'Dawnlord'],
                 rivals=['coven'], jobs=['hunt', 'bounty', 'fetch', 'courier'], halls=3,
                 desc='Holy knights sworn to burn out the dead and those who raise them.'),
    'wardens': dict(name='The Wardens of the Wild', short='Wardens', kind='combat', secret=0, fg='#70c060', sign='WARDENS',
                    master='Elder Warden {n}', ranks=['Tracker', 'Ranger', 'Pathfinder', 'Warden', 'Elder Warden'], rivals=[],
                    jobs=['hunt', 'bounty', 'fetch'], halls=0,
                    desc='Rangers of the deep woods, who keep the wild things out of the farms and the farms out of the wild.'),
    'thieves': dict(name="The Thieves' Guild", short='Thieves', kind='combat', secret=1, fg='#b0a090', sign=None,
                    master='The Fence, {n}', ranks=['Footpad', 'Cutpurse', 'Shadow', 'Nightblade', "Guildmaster's Hand"],
                    rivals=['dawn'], jobs=['hunt', 'courier', 'fetch', 'bounty'], halls=99, dark=True,
                    desc='Nobody admits it exists. Everybody pays it, one way or another.'),
    'coven': dict(name='The Hollow Coven', short='Coven', kind='combat', secret=2, fg='#b070ff', sign=None,
                  master='{n}, Voice of Morrak', ranks=['Seeker', 'Initiate', 'Witch', 'Warlock', 'Voice of Morrak'],
                  rivals=['dawn', 'magi'], jobs=['hunt', 'bounty', 'fetch'], halls=1, dark=True,
                  desc='Warlocks who bargain with Morrak, the Hollow One, for power. Morrak always collects.'),
    'moot': dict(name='The Green Moot', short='Green Moot', kind='combat', secret=0, fg='#78c858', sign='THE GREEN MOOT',
                 master='Grove-Mother {n}', ranks=['Sapling', 'Acorn', 'Thornkeeper', 'Oakheart', 'Voice of Thessa'],
                 rivals=['coven', 'ossuary'], jobs=['hunt', 'fetch', 'courier'], halls=0,
                 desc='Druids and shamans of Thessa, who keep the groves by the standing stones and speak for the wild.'),
    'chapter': dict(name='The Hallowed Chapter', short='Hallowed Chapter', kind='combat', secret=0, fg='#f8f0c8',
                    sign='THE HALLOWED CHAPTER', master='Abbess {n}', ranks=['Novice', 'Brother', 'Confessor', 'Prior', 'Hand of Solmara'],
                    rivals=['coven', 'ossuary'], jobs=['bounty', 'courier', 'fetch'], halls=3,
                    desc="Solmara's healers. They carry no sword: they mend, they shelter, and they bring back the fallen."),
    'ossuary': dict(name='The Quiet Ossuary', short='Ossuary', kind='combat', secret=1, fg='#c8d0b0', sign=None,
                    master='{n}, Keeper of Bones', ranks=['Gravedigger', 'Bonewright', 'Deathspeaker', 'Ossuarch', 'Keeper of the Quiet'],
                    rivals=['dawn', 'chapter', 'moot'], jobs=['fetch', 'bounty'], halls=1, dark=True,
                    desc='Necromancers. The dwarves tolerate them, for Durnak is god of the dead; the Crown and the Dawn '
                         'hunt them.'),
    'stillhand': dict(name='The Order of the Still Hand', short='Still Hand', kind='combat', secret=0, fg='#d8c8a8',
                      sign='MONASTERY', master='Master {n}', ranks=['Novice', 'Disciple', 'Brother of the Hand', 'Elder', 'Still Master'],
                      rivals=[], jobs=['hunt', 'bounty', 'escort'], halls=0,
                      desc='Monks who fight with their hands and feet. They say armour is a cage; they fight best without it.'),
    'hound': dict(name="The Houndwardens' Lodge", short='Houndwardens', kind='combat', secret=0, fg='#c89860',
                  sign="HOUNDWARDENS' LODGE", master='Huntmaster {n}', ranks=['Kennel-hand', 'Handler', 'Packleader', 'Beastmaster',
                                                                             'Lord of the Hunt'],
                  rivals=[], jobs=['hunt', 'bounty', 'fetch'], halls=0,
                  desc='Beastmasters of the hill country. They tame what others hunt, and keep a beast as well as a sellsword.'),
    # the crafts: no limit
    'alembic': dict(name='The Guild of Alembic and Barrel', short='Alembic and Barrel', kind='life', secret=0, fg='#e0a0e0',
                    sign='ALCHEMISTS', master='Mistress {n}', ranks=['Bottlewasher', 'Apprentice', 'Journeyman', 'Master', 'Grand Alembic'],
                    rivals=[], jobs=['freight', 'courier'], halls=3, skills=['alchemy', 'brewing'],
                    desc='Alchemists and brewers, who argue about everything except the price of good copper.'),
    'carto': dict(name="The Cartographers' Society", short='Cartographers', kind='life', secret=0, fg='#d8c890', sign='MAPMAKER',
                  master='Master Surveyor {n}', ranks=['Errand-runner', 'Surveyor', 'Mapmaker', 'Master Cartographer',
                                                      'Keeper of the Charts'],
                  rivals=[], jobs=['courier', 'fetch'], halls=2, skills=['foraging'],
                  desc='They draw the realm, and they keep old Varnish charts that show ways nobody walks any more.'),
    'anglers': dict(name='The Brotherhood of the Net', short='Anglers', kind='life', secret=0, fg='#80c0e0', sign='NET HALL',
                    master='Net-Elder {n}', ranks=['Netmender', 'Angler', 'Boatman', 'Master Angler', 'Sea-Elder'],
                    rivals=[], jobs=['freight', 'courier'], halls=0, skills=['fishing'],
                    desc='Fishers and boatmen of the harbours. They know every current, and every tale the sailors bring.'),
}
ORDER = list(GUILDS)

# the advanced techniques: (skill id, guild rank needed, discipline, discipline rank needed, price in silver)
TEACH = {
    'magi': [('mage_armor', 1, 'frost', 8, 60), ('arcane_barrage', 2, 'storm', 15, 140), ('inferno', 4, 'fire', 28, 400)],
    'iron': [('shield_wall', 1, 'warcraft', 6, 50), ('battle_drill', 2, 'warcraft', 14, 130), ('last_stand', 4, 'warcraft', 26, 380)],
    'dawn': [('smite', 1, 'restoration', 6, 60), ('holy_shield', 2, 'restoration', 14, 140), ('dawnbreak', 4, 'restoration', 28, 420)],
    'wardens': [('hunters_mark', 1, 'archery', 6, 50), ('rain_of_arrows', 2, 'archery', 16, 150), ('thornbind', 4, 'archery', 26, 360)],
    'thieves': [('garrote', 1, 'daggers', 6, 60), ('smoke_bomb', 2, 'daggers', 14, 150), ('deaths_kiss', 4, 'daggers', 28, 450)],
    'coven': [('hellfire', 1, 'shadow', 8, 80), ('pact_of_blood', 2, 'shadow', 16, 160), ('morraks_hand', 4, 'shadow', 30, 500)],
    'moot': [('entangle', 1, 'nature', 6, 60), ('spirit_totem', 2, 'nature', 14, 150), ('wild_shape', 4, 'nature', 26, 400)],
    'chapter': [('mass_mend', 1, 'restoration', 6, 60), ('hallowed_ground', 2, 'restoration', 14, 160),
                ('rite_of_return', 4, 'restoration', 26, 420)],
    'ossuary': [('raise_dead', 1, 'necromancy', 6, 80), ('bone_armour', 2, 'necromancy', 14, 150),
                ('corpse_burst', 4, 'necromancy', 28, 450)],
    'stillhand': [('still_flurry', 1, 'unarmed', 6, 50), ('stone_stance', 2, 'unarmed', 12, 120), ('pressure_point', 2, 'unarmed', 16, 150),
                  ('wind_step', 4, 'unarmed', 26, 380)],
    'hound': [('tame', 1, 'beastcraft', 4, 60), ('call_of_the_pack', 2, 'beastcraft', 14, 160), ('pack_fury', 4, 'beastcraft', 26, 380)],
}
# techniques only those who serve two guilds at once can learn: (guild a, guild b) -> (skill, rank in both, price)
COMBOS = {
    ('iron', 'magi'): ('spellblade', 2, 300), ('coven', 'thieves'): ('soul_knife', 2, 320),
    ('magi', 'wardens'): ('thornstorm', 2, 300), ('dawn', 'iron'): ('crusade', 2, 300),
    ('moot', 'wardens'): ('wildheart', 2, 320), ('coven', 'ossuary'): ('lichcraft', 2, 340),
    ('dawn', 'stillhand'): ('mendicant', 2, 300), ('hound', 'iron'): ('war_handler', 2, 320),
}
SECRET_WORDS = {
    'thieves': 'Chalk marks low on a doorpost, a circle crossed twice: those who know, knock there.',
    'coven': 'They say the Hollow Coven meets under {city}, behind a door that is not there by day.',
}


def state(game):
    """{guild: dict(joined, rep, last, found, board, board_day)}"""
    st = game.__dict__.setdefault('guilds', {})
    for k in ORDER:
        st.setdefault(k, dict(joined=False, rep=0, last=0, found=not GUILDS[k]['secret'], board=[], board_day=-99, left=False))
    return st


def rank(game, key):
    rep = state(game)[key]['rep']
    return max(i for i, v in enumerate(RANK_REP) if rep >= v)


def rank_name(game, key):
    return GUILDS[key]['ranks'][rank(game, key)]


def members(game, kind=None):
    return [k for k, s in state(game).items() if s['joined'] and (kind is None or GUILDS[k]['kind'] == kind)]


def life_bonus(game, skill):
    """Craft guilds speed up the crafts they keep: +10% progress per rank."""
    b = 1.0
    for k in members(game, 'life'):
        if skill in GUILDS[k].get('skills', ()):
            b += .1 * (rank(game, k) + 1)
    return b


# ------------------------------------------------------------------ where the guilds live
def setup(world):
    """Pick the cities, towns and villages where each guild keeps a hall."""
    rng = random.Random(len(world.settlements) * 7919 + world.settlements[0].x)
    cities = [s for s in world.settlements if s.is_city]
    halls = {k: [] for k in ORDER}
    for k, g in GUILDS.items():
        n = g['halls']
        if not n or not cities:
            continue
        if n >= len(cities):
            halls[k] = [s.id for s in cities]
        else:
            big = [s.id for s in cities if s.kind == 'metropolis']
            rest = [s.id for s in cities if s.kind != 'metropolis']
            rng.shuffle(rest)
            halls[k] = (big + rest)[:n]
    # the coven hides in a city the thieves also use, never in the greatest
    small = [s.id for s in cities if s.kind != 'metropolis'] or [s.id for s in cities]
    halls['coven'] = [rng.choice(small)] if small else []
    # the wardens keep lodges in the villages of the woods
    woods = [s for s in world.settlements if not s.is_city and s.kind in ('village', 'town') and s.biome in ('forest', 'hills', 'swamp')]
    rng.shuffle(woods)
    halls['wardens'] = [s.id for s in woods[:4]] or [s.id for s in world.settlements if not s.is_city][:2]
    halls['anglers'] = [s.id for s in world.settlements if getattr(s, 'harbour', False) and s.kind != 'hamlet']
    villages = [s for s in world.settlements if not s.is_city and s.kind in ('village', 'town')]
    # the Moot keeps groves in the forest villages, the monks their monasteries up in the hills, the Houndwardens
    # their lodges in the hill villages; the Ossuary meets under a city, behind a door nobody notices
    grove = [s.id for s in villages if s.biome in ('forest', 'swamp')]
    rng.shuffle(grove)
    halls['moot'] = grove[:3] or [s.id for s in villages][:2]
    hills = [s.id for s in villages if s.biome == 'hills']
    rng.shuffle(hills)
    halls['hound'] = hills[:3] or [s.id for s in villages][-2:]
    halls['stillhand'] = [i for i in hills if i not in halls['hound']][:2] or [s.id for s in villages if s.id not in halls['hound']][:2]
    old = [s.id for s in cities if s.id not in halls['coven']] or [s.id for s in cities]
    halls['ossuary'] = [rng.choice(old)] if old else []
    world.guild_halls = halls


def temple_mult(game):
    """The Hallowed Chapter raises its own, and its friends, for less."""
    return .6 if state(game)['chapter']['joined'] else 1.0


def unarmoured(game):
    """A monk of the Still Hand fights best without heavy armour: percent more damage."""
    if not state(game)['stillhand']['joined']:
        return 0
    it = game.eq_item('armor')
    if it and D.BASES[it.base].get('family', it.base) not in ('quilted', 'leather'):
        return 0
    return 10 + 5 * rank(game, 'stillhand')


def on_graveyard(game):
    """An old graveyard on the Varnish ways: someone has been digging here, and left a sign for those who know."""
    if not state(game)['ossuary']['found']:
        ids = game.world.guild_halls.get('ossuary', [])
        city = game.world.settlements[ids[0]].name if ids else 'the city'
        discover(game, 'ossuary', f'Among the old stones, fresh earth, and a bone carved with a word and a street in {city}. '
                 'The Quiet Ossuary leaves its mark where the dead are old.')


def halls_in(game, sid):
    return [k for k, ids in getattr(game.world, 'guild_halls', {}).items() if sid in ids]


def master_name(key, names):
    n = names.pop() if names else 'Aldo'
    return GUILDS[key]['master'].format(n=n)


def place_master(game, m, pl, key, names):
    """The master of a guild hall, behind the table; in a secret den he looks like anyone else."""
    from .towns import free_inside
    from .entities import make_npc
    spots = free_inside(m, pl)
    if not spots:
        return None
    c = random.choice(spots)
    g = GUILDS[key]
    npc = make_npc(game, master_name(key, names), 'guild', g['fg'], c[0], c[1], True)
    npc.guild = key
    if g['secret']:
        npc.true_name = npc.name
        npc.name = random.choice(['A quiet man', 'A pale woman', 'A tired cobbler', 'An old widow'])
        npc.fg = D.hexrgb('#a8aab4')
    m.mons.append(npc)
    return npc


def reveal_master(game, m):
    """Once you know the secret, the people in the den show who they are."""
    for o in m.mons:
        k = getattr(o, 'guild', None)
        if k and GUILDS[k]['secret'] and state(game)[k]['found'] and hasattr(o, 'true_name'):
            o.name = o.true_name
            o.fg = D.hexrgb(GUILDS[k]['fg'])


def discover(game, key, how):
    s = state(game)[key]
    if s['found']:
        return False
    s['found'] = True
    g = GUILDS[key]
    ids = getattr(game.world, 'guild_halls', {}).get(key, [])
    where = ', '.join(game.world.settlements[i].name for i in ids[:3]) if ids else 'the cities'
    game.msg(f'{how} You have found {g["name"]}. They meet in {where}.', 'unique')
    for k in ids:
        st = game.world.settlements[k]
        game.reveal_place(st.x, st.y, 0)
    if game.map.kind == 'town':
        reveal_master(game, game.map)
    return True


def on_crime(game):
    """Crime gets you noticed, by the wrong people."""
    c = game.__dict__.setdefault('crimes', 0) + 1
    game.crimes = c
    if c >= 2 and not state(game)['thieves']['found']:
        discover(game, 'thieves', 'Someone bumps into you in the crowd and is gone. In your pocket: a scrap of paper, a '
                 'circle crossed twice, and a street. "We noticed you," it says.')


def rumor(game):
    """A secret overheard, now and then, in a town that hides a guild."""
    here = game.here
    st = state(game)
    if not here:
        return None
    if not st['thieves']['found'] and here.id in game.world.guild_halls.get('thieves', ()) and random.random() < .25:
        discover(game, 'thieves', SECRET_WORDS['thieves'])
        return 'Watch the chalk marks on the doors, stranger. Some of them are not children\'s games.'
    if not st['coven']['found'] and game.day > 8 and random.random() < .08:
        ids = game.world.guild_halls.get('coven', [])
        if ids:
            city = game.world.settlements[ids[0]].name
            discover(game, 'coven', SECRET_WORDS['coven'].format(city=city))
            return f'People go missing in {city}. They say it is the Hollow Coven. They say a lot of things.'
    return None


# ------------------------------------------------------------------ talking to a master
def talk(game, npc):
    from . import events as EV
    from .money import fmt
    key = npc.guild
    g = GUILDS[key]
    s = state(game)[key]
    if g['secret'] and not s['found']:
        from . import lore as LORE
        game.say(npc, LORE.chatter(game, npc))
        return
    if g['secret'] and getattr(npc, 'true_name', None):
        npc.name, npc.fg = npc.true_name, D.hexrgb(g['fg'])
    opts = []
    if not s['joined']:
        why = cant_join(game, key)
        text = f'"{g["desc"]}' + (f' {why}"' if why else ' Do you want to join us?"')
        if not why:
            cost = ' Morrak takes his due: a tenth of your life, forever.' if key == 'coven' else ''
            text = text[:-1] + cost + '"'
            opts.append((f'Join {g["name"]}', 'join'))
    else:
        r = rank(game, key)
        text = (f'"Welcome back, {g["ranks"][r].lower()}." You stand at {s["rep"]} with {g["short"]}'
                + (f'; {RANK_REP[r + 1] - s["rep"]} more for {g["ranks"][r + 1]}.' if r < 4 else '. There is no higher rank.'))
        if game.day - s['last'] > DECAY_AFTER - 3:
            text += ' "We have not seen you working for us lately. People forget."'
        opts.append(('Ask for work', 'work'))
        for sid, rk, line, dr, price in TEACH.get(key, []) + combos_for(game, key):
            from .skills import SKILLS
            if sid in game.player.known:
                continue
            from .skills import DISCIPLINES
            opts.append((f'Learn {SKILLS[sid].name} ({fmt(price * 100)}; {g["ranks"][rk]}'
                         + (f', {DISCIPLINES[line]["name"]} {dr}' if line else ', both guilds') + ')', 'learn:' + sid))
        opts.append((f'Visit the quartermaster ({round((1 - quarter_mult(game, key)) * 100)}% off)', 'quarter'))
        nr, rc = game.repair_all(mend_discount(game, key), dry=True)
        if nr:
            opts.append((f'Have your gear mended ({fmt(rc)})', 'mend'))
        bed = bed_price(game, key)
        opts.append((f'Sleep in the guild hall ({fmt(bed) if bed else "free"})', 'bed'))
        if key == 'carto' and r >= 1:
            opts.append((f'Buy an old Varnish chart ({fmt(chart_price(game))})', 'chart'))
        opts.append(('Leave the guild', 'leave'))
    opts.append(('Goodbye', 'bye'))
    EV.ask(game, 'guild', npc.name, text, opts[:12], guild=key)


def combos_for(game, key):
    out = []
    for (a, b), (sid, rk, price) in COMBOS.items():
        if key in (a, b):
            other = b if key == a else a
            if state(game)[other]['joined']:
                out.append((sid, rk, None, 0, price))
    return out


def cant_join(game, key):
    g = GUILDS[key]
    st = state(game)
    if g['kind'] == 'combat':
        mine = members(game, 'combat')
        if len(mine) >= 2:
            return f'But you already fight for {GUILDS[mine[0]]["short"]} and {GUILDS[mine[1]]["short"]}. Two masters are enough for anyone.'
        for r in g['rivals']:
            if st[r]['joined']:
                return f'But you walk with {GUILDS[r]["name"]}. We will not share you with them.'
        for k in mine:
            if key in GUILDS[k]['rivals']:
                return f'But you walk with {GUILDS[k]["name"]}. We will not share you with them.'
    if st[key]['left'] and g['secret']:
        return 'You turned your back on us once. Nobody does it twice.'
    return None


def quarter_mult(game, key):
    """Members buy from the guild's own stores: 10% off, and 5% more for every rank."""
    return 1 - (.10 + .05 * rank(game, key))


def mend_discount(game, key):
    return .15 + .05 * rank(game, key)


def bed_price(game, key):
    """A cot in the hall: cheap for the low ranks, free from the middle rank up."""
    return 0 if rank(game, key) >= 2 else 80


def quarter_stock(game, key):
    """Better than the outfitter's: more magic, a little above your level."""
    from .entities import make_gear
    r = rank(game, key)
    lvl = max(1, game.player.lvl) + 1 + r // 2
    ks = [k for k, b in D.BASES.items() if b['lvl'] <= lvl + 2]
    out = []
    for _ in range(6 + r):
        rar = 'rare' if random.random() < .06 * r else 'magic' if random.random() < .45 + .08 * r else 'normal'
        out.append(make_gear(game, random.choice(ks), rar, lvl))
    return out


def chart_price(game):
    return 2500 - rank(game, 'carto') * 300


def resolve(game, choice, ctx):
    from .money import fmt
    from .skills import SKILLS, BAR_SIZE
    key = ctx['guild']
    g = GUILDS[key]
    s = state(game)[key]
    p = game.player
    if choice == 'join':
        why = cant_join(game, key)
        if why:
            game.msg(why.replace('But you', 'You'), 'bad')
            return
        s['joined'], s['last'] = True, game.day
        s['rep'] = max(s['rep'], 0)
        if key == 'coven':
            p.toll = getattr(p, 'toll', 0) + 10
            from . import gods as GD
            if getattr(p, 'god', None) == 'morrak':
                GD.gain(game, 15)
                game.msg('Morrak knows you already. He is pleased.', 'gold')
            else:
                GD.lose(game, 100, 'Your god turns away from you. Morrak has your name now.')
            game.clamp_vitals()
        game.msg(f'You join {g["name"]} as {g["ranks"][0].lower()}.', 'gold')
    elif choice == 'work':
        offer_work(game, key)
    elif choice == 'quarter':
        sk = 'g:' + key
        if game.day - s.get('quarter_day', -99) >= 7 or sk not in game.shops:
            game.shops[sk] = quarter_stock(game, key)
            s['quarter_day'] = game.day
        game.request = ('quarter', key)
    elif choice == 'mend':
        game.repair_all(mend_discount(game, key))
    elif choice == 'bed':
        game.inn_meal(bed_price(game, key), 'A hard cot in the guild hall, among your own. You sleep well.')
    elif choice.startswith('learn:'):
        sid = choice[6:]
        row = next((t for t in TEACH.get(key, []) + combos_for(game, key) if t[0] == sid), None)
        if not row:
            return
        _sid, rk, line, dr, price = row
        if rank(game, key) < rk:
            game.msg(f'Only a {g["ranks"][rk].lower()} may learn that.', 'bad')
            return
        if row in combos_for(game, key):
            pair = next(pr for pr in COMBOS if key in pr and COMBOS[pr][0] == sid)
            other = pair[0] if pair[1] == key else pair[1]
            if rank(game, other) < rk:
                game.msg(f'You must also be a {GUILDS[other]["ranks"][rk].lower()} of {GUILDS[other]["short"]}.', 'bad')
                return
        if line and p.disc[line][0] < dr:
            from .skills import DISCIPLINES
            game.msg(f'You need {DISCIPLINES[line]["name"]} {dr} for that.', 'bad')
            return
        if p.gold < price * 100:
            game.msg(f'That costs {fmt(price * 100)}.', 'bad')
            return
        p.gold -= price * 100
        p.known.append(sid)
        if None in p.bar[:BAR_SIZE]:
            p.bar[p.bar.index(None)] = sid
        if key == 'coven':
            p.toll = getattr(p, 'toll', 0) + 5
            game.clamp_vitals()
            game.msg('Morrak takes a little more of your life in return.', 'bad')
        game.msg(f'The master teaches you {SKILLS[sid].name}.', 'gold')
    elif choice == 'chart':
        price = chart_price(game)
        if p.gold < price:
            game.msg(f'A chart costs {fmt(price)}.', 'bad')
            return
        from . import hidden as HP
        if HP.buy_chart(game):
            p.gold -= price
    elif choice == 'leave':
        leave(game, key)


def leave(game, key):
    g = GUILDS[key]
    s = state(game)[key]
    s['joined'], s['left'] = False, True
    s['rep'] = RANK_REP[max(0, rank(game, key) - 2)]            # leaving costs you your standing
    s['board'] = []
    game.msg(f'You leave {g["name"]}.', 'info')
    if g['secret']:
        game.msg('The master says nothing. That is worse than anything they could have said.', 'bad')
        send_avengers(game, key)


def send_avengers(game, key):
    """Nobody leaves a secret guild alive, if the guild can help it."""
    from .wanderers import make_group
    w, p = game.world, game.player
    ox, oy = game.over_pos if game.cur != 'over' else (p.x, p.y)
    om = game.maps['over']
    for _ in range(200):
        x, y = ox + random.randint(-20, 20), oy + random.randint(-12, 12)
        if not om.inb(x, y) or not D.TILES[om.tile(x, y)].walk or cheb(x, y, ox, oy) < 8:
            continue
        keys = ['bandit', 'bandit', 'brigand'] if key == 'thieves' else ['cultist', 'cultist', 'skeleton']
        wd = make_group(game, 'bandits' if key == 'thieves' else 'monsters', x, y, p.lvl + 1, keys, 2,
                        'The Knives of the Guild' if key == 'thieves' else 'Morrak\'s Hollow Ones')
        wd.kind = 'avenger'
        wd.name = 'Knives of the Guild, sent for you' if key == 'thieves' else 'Hollow Ones, sent by Morrak'
        w.wanderers.append(wd)
        return wd
    return None


# ------------------------------------------------------------------ work
def offer_work(game, key):
    from . import missions as MS
    from . import events as EV
    s = state(game)[key]
    here = game.here
    if not here:
        return
    if game.day - s['board_day'] >= 5 or not s['board']:
        s['board'] = []
        for _ in range(12):
            from .named import GUILD_PREY
            m = MS.make_offer(game, here, kinds=GUILDS[key]['jobs'], prey=GUILD_PREY.get(key), max_rank=rank(game, key) // 2)
            if m:
                flavour(game, key, m)
                s['board'].append(m)
            if len(s['board']) >= 3:
                break
        s['board_day'] = game.day
    if not s['board']:
        game.msg('"Nothing for you today. Come back in a few days."')
        return
    opts = [(f'{m.title} ({fmt_reward(m)})', f'take:{i}') for i, m in enumerate(s['board'])] + [('Not now', 'bye')]
    text = '"Here is what we need:"\n\n' + '\n'.join(f'- {m.desc}' for m in s['board'])
    EV.ask(game, 'guildwork', GUILDS[key]['short'], text, opts, guild=key)


def fmt_reward(m):
    from .money import fmt
    return fmt(m.reward)


def resolve_work(game, choice, ctx):
    from . import missions as MS
    key = ctx['guild']
    s = state(game)[key]
    if not choice.startswith('take:'):
        return
    i = int(choice[5:])
    if i >= len(s['board']):
        return
    m = s['board'][i]
    here = game.here
    here.board.append(m)
    if MS.accept(game, here, m):
        s['board'].remove(m)
    elif m in here.board:
        here.board.remove(m)


def flavour(game, key, m):
    """A guild job: the same work as anywhere, with the guild's own colour, and for the secret ones, a price."""
    g = GUILDS[key]
    m.guild = key
    m.reward = round(m.reward * (1.2 + .2 * rank(game, key)))        # the higher your rank, the better the pay
    w = game.world
    if key == 'dawn' and m.kind == 'bounty':
        m.data['keys'] = [random.choice(['zombie', 'skeleton', 'skarcher', 'ghost']) for _ in range(random.randint(3, 5))]
        lead = m.data['leader']
        m.title = f'Lay {lead} to rest'
        m.desc = f'The dead walk under {lead}. ' + m.desc.split('. ', 1)[-1]
    elif key == 'thieves' and m.kind == 'courier':
        m.title = f'Smuggle goods to {w.settlements[m.target].name}'
        m.desc = 'A sealed crate, no questions. ' + m.desc
        m.dark = 'smuggle'
    elif key == 'thieves' and m.kind == 'fetch':
        m.title = 'Lift ' + m.title.split('Recover ', 1)[-1]
        m.dark = 'theft'
    elif key == 'coven' and m.kind == 'bounty':
        m.data['keys'] = ['soldier', 'soldier', 'crossbow']
        m.title = f'Silence the knights who hunt us'
        m.desc = 'A patrol of the Order of Dawn has come too close. ' + m.desc.split('. ', 1)[-1]
        m.dark = 'murder'
    elif key == 'ossuary' and m.kind == 'fetch':
        m.title = 'Rob the grave of ' + m.title.split('Recover ', 1)[-1]
        m.desc = 'Under the stones of an old grave lies what we want. Dig quietly. ' + m.desc
        m.dark = 'graverob'
    elif key == 'ossuary' and m.kind == 'bounty':
        m.data['keys'] = ['soldier', 'soldier', 'crossbow']
        m.title = 'Silence the grave-watch'
        m.desc = 'Templars of the Dawn are watching our graveyards. ' + m.desc.split('. ', 1)[-1]
        m.dark = 'murder'
    elif key == 'chapter' and m.kind == 'bounty':
        m.data['keys'] = [random.choice(['zombie', 'ghoul', 'skeleton']) for _ in range(random.randint(3, 5))]
        lead = m.data['leader']
        m.title = f'Give rest to {lead}'
        m.desc = f'The dead will not lie still around {lead}. ' + m.desc.split('. ', 1)[-1]
    elif key == 'coven' and m.kind == 'fetch':
        m.title = 'Bring Morrak ' + m.title.split('Recover ', 1)[-1]
        m.dark = 'desecration'
    m.title = f'{g["short"]}: {m.title}'


def job_done(game, m):
    key = getattr(m, 'guild', None)
    if not key:
        return
    s = state(game)[key]
    before = rank(game, key)
    s['rep'] += JOB_REP + (15 if getattr(m, 'dark', None) else 0)
    s['last'] = game.day
    after = rank(game, key)
    if after > before:
        game.msg(f'{GUILDS[key]["name"]} raises you to {GUILDS[key]["ranks"][after]}.', 'unique')
    if before >= 2 and random.random() < .2 + .1 * (before - 2):
        from .entities import random_gear
        it = random_gear(game, game.player.lvl + before, 2)
        if it and game.add_to_inv(it):
            game.msg(f'For a job well done, the guild adds {it.display_name()} to your pay.', 'gold')
    if after >= 2 and key in ('thieves', 'magi') and not state(game)['coven']['found']:
        ids = game.world.guild_halls.get('coven', [])
        if ids:
            discover(game, 'coven', f'"Since you are one of us now: beware {game.world.settlements[ids[0]].name}. '
                     'Something meets under it that calls itself the Hollow Coven."')
    consequences(game, m)


def consequences(game, m):
    """The dark side of the secret guilds: the world finds out, sometimes."""
    from . import gods as GD
    from .war import change_rep
    dark = getattr(m, 'dark', None)
    w = game.world
    if not dark:
        return
    if dark == 'smuggle' and random.random() < .35:
        t = w.settlements[m.target]
        t.rep = max(-100, t.rep - 8)
        game.msg(f'Word gets around {t.name} that you carry for the Guild. People there look at you differently.', 'bad')
    elif dark == 'theft':
        from . import crime as CR
        CR.commit(game, 6, 'theft for the Guild', .3)
    elif dark == 'murder':
        state(game)['dawn']['rep'] = max(0, state(game)['dawn']['rep'] - 80)
        change_rep(game, 'crown', -6)
        GD.lose(game, 20, 'The blood of holy knights is on your hands. Your god is silent.')
    elif dark == 'graverob':
        if random.random() < .3:                # it comes out: the faithful will not forget it
            for k in ('dawn', 'chapter'):
                state(game)[k]['rep'] = max(0, state(game)[k]['rep'] - 40)
            change_rep(game, 'crown', -4)
            here = game.here
            if here:
                here.rep = max(-100, here.rep - 8)
            game.msg('Someone saw you at the graves. Word gets around, and the faithful look at you with disgust.', 'bad')
    elif dark == 'desecration':
        if getattr(game.player, 'god', None) == 'morrak':
            GD.gain(game, 5)
        else:
            GD.lose(game, 25, 'What you brought to Morrak was holy once. Your god will not forget it.')
        here = game.here
        if here:
            here.rep = max(-100, here.rep - 5)


def job_failed(game, m):
    key = getattr(m, 'guild', None)
    if key:
        s = state(game)[key]
        s['rep'] = max(0, s['rep'] - 20)


def daily(game):
    """Standing fades when you do nothing for a guild: never below the rank you hold, except in the secret guilds."""
    for key, s in state(game).items():
        if not s['joined'] or game.day - s['last'] <= DECAY_AFTER:
            continue
        r = rank(game, key)
        if GUILDS[key]['secret']:
            s['rep'] = max(0, s['rep'] - 3)                  # the secret guilds let you fall
        else:
            s['rep'] = max(RANK_REP[r], s['rep'] - 3)        # the others keep you at your rank
        if rank(game, key) < r:
            game.msg(f'{GUILDS[key]["name"]} has not heard from you in a long time. You are only {GUILDS[key]["ranks"][rank(game, key)]} now.',
                     'bad')


def register():
    from . import events as EV
    EV.RESOLVERS['guild'] = resolve
    EV.RESOLVERS['guildwork'] = resolve_work


register()
