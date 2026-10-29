"""Who you become (see "Classes, trees and the bar" in docs/plan.md). You start blank: the first tome you read wakes a
memory and is your first class; from then on you read only tomes of your class. At rank 20 in it you may read one tome
of a second school: it becomes your second class and you learn the name of your pair. Who never takes a second stays
pure. What you are lives on the player (`p.classes`).

The bar keeps six keys in three groups: 1-2 your weapon's two skills (weaponskills.py), 3-5 three class skills, 6 one
elite (for now any guild technique; guild elites are settled in classes part 3)."""

from . import skills as SK

SECOND_AT = 20
CLASS_LINES = ('fire', 'frost', 'storm', 'restoration', 'shadow', 'necromancy', 'nature', 'beastcraft', 'warcraft',
               'cunning', 'arcane')
PURE = {'fire': 'Pyromancer', 'frost': 'Rimecaller', 'storm': 'Stormcaller', 'restoration': 'Cleric', 'shadow': 'Warlock',
        'necromancy': 'Necromancer', 'nature': 'Druid', 'beastcraft': 'Beastmaster', 'warcraft': 'Warrior',
        'arcane': 'Arcanist', 'cunning': 'Rogue'}
_PAIRS = [
    ('fire', 'frost', 'Elementalist'), ('fire', 'storm', 'Stormbrand'), ('fire', 'restoration', 'Sunpriest'),
    ('fire', 'shadow', 'Hexblade'), ('fire', 'necromancy', 'Pyre Lord'), ('fire', 'nature', 'Ashwarden'),
    ('fire', 'beastcraft', 'Firetamer'), ('fire', 'warcraft', 'Firebrand'), ('frost', 'storm', 'Winterstorm'),
    ('frost', 'restoration', 'Snowsaint'), ('frost', 'shadow', 'Rimehex'), ('frost', 'necromancy', 'Lich'),
    ('frost', 'nature', 'Rimewarden'), ('frost', 'beastcraft', 'Winterwolf'), ('frost', 'warcraft', 'Iceguard'),
    ('storm', 'restoration', 'Stormsaint'), ('storm', 'shadow', 'Darkstorm'), ('storm', 'necromancy', 'Galvanist'),
    ('storm', 'nature', 'Skyshaper'), ('storm', 'beastcraft', 'Thunderhide'), ('storm', 'warcraft', 'Stormblade'),
    ('restoration', 'shadow', 'Penitent'), ('restoration', 'necromancy', 'Gravekeeper'),
    ('restoration', 'nature', 'Lifewarden'), ('restoration', 'beastcraft', 'Shepherd'),
    ('restoration', 'warcraft', 'Paladin'), ('shadow', 'necromancy', 'Dread Lord'), ('shadow', 'nature', 'Blightcaller'),
    ('shadow', 'beastcraft', 'Nightstalker'), ('shadow', 'warcraft', 'Reaver'), ('necromancy', 'nature', 'Rotwood'),
    ('necromancy', 'beastcraft', 'Bonetamer'), ('necromancy', 'warcraft', 'Bone Captain'),
    ('nature', 'beastcraft', 'Wildkin'), ('nature', 'warcraft', 'Thornguard'), ('beastcraft', 'warcraft', 'Warhound'),
    ('cunning', 'fire', 'Firestarter'), ('cunning', 'frost', 'Rimeknife'), ('cunning', 'storm', 'Sparkthief'),
    ('cunning', 'restoration', 'Hedge Doctor'), ('cunning', 'shadow', 'Shade'), ('cunning', 'necromancy', 'Graverobber'),
    ('cunning', 'nature', 'Poisoner'), ('cunning', 'beastcraft', 'Poacher'), ('cunning', 'warcraft', 'Cutthroat'),
    ('arcane', 'fire', 'Spellfire'), ('arcane', 'frost', 'Rimeweaver'), ('arcane', 'storm', 'Stormweaver'),
    ('arcane', 'restoration', 'Sanctifier'), ('arcane', 'shadow', 'Voidcaller'), ('arcane', 'necromancy', 'Soulbinder'),
    ('arcane', 'nature', 'Leywalker'), ('arcane', 'beastcraft', 'Spiritcaller'), ('arcane', 'warcraft', 'Spellbreaker'),
    ('arcane', 'cunning', 'Trickster')]
PAIRS = {frozenset((a, b)): n for a, b, n in _PAIRS}
WEAPON, CLASS, ELITE = (0, 1), (2, 3, 4), (5,)


def classes(game):
    return getattr(game.player, 'classes', [])


def title(game):
    """The name people know you by: your pair's, your pure class's, or None while you are blank."""
    c = classes(game)
    if len(c) == 2:
        return PAIRS.get(frozenset(c))
    return PURE.get(c[0]) if c else None


def rule_name(game):
    """Whose rule you fight by: your pair's, or your pure class's while you have one."""
    return title(game)


def pair_name(a, b):
    return PAIRS.get(frozenset((a, b)))


def school(line):
    return SK.DISCIPLINES[line]['name']


# ------------------------------------------------------------------ reading a tome
def read(game, it):
    """Read a tome: your class's, a first one that wakes a memory, a second school at rank 20, or none at all.
    Returns the turns spent (0 when nothing was read, or when a question waits)."""
    from . import events as EV
    sk = SK.SKILLS[it.t]
    line, c = sk.line, classes(game)
    if line in c or not class_line(line):
        return 1 if SK.learn(game, it.t) and _used(game, it) else 0
    if sk.id in game.player.known:
        game.msg(f'You already know {sk.name}.')
        return 0
    if not c:
        EV.ask(game, 'wake_class', 'A memory stirs',
               f'The first pages of the tome of {sk.name} pull at something in you. This will wake a memory: '
               f'{school(line)} will be your school, and you will be a {PURE[line]}. From then on only tomes of '
               f'{school(line)} speak to you, until much later a second school may open. Read on?',
               [('Read on', 'yes'), ('Not now', 'no')], item=it.id)
        return 0
    first = c[0]
    if len(c) == 1 and game.player.disc[first][0] >= SECOND_AT:
        EV.ask(game, 'second_class', 'A second school',
               f'You know {school(first)} well enough now that another way opens to you. Read the tome of {sk.name}, '
               f'and {school(line)} becomes your second school: you will be a {pair_name(first, line)}. There is no '
               f'third. Read on?', [('Read on', 'yes'), ('Not now', 'no')], item=it.id)
        return 0
    if len(c) == 1:
        game.msg(f'The tome is of {school(line)}; the words mean nothing to you. You may sell it, or keep it: at '
                 f'{school(first)} {SECOND_AT} a second school may open.', 'info')
    else:
        game.msg(f'The tome is of {school(line)}, and that is not one of your schools. Sell it, or keep it.', 'info')
    return 0


def class_line(line):
    return SK.DISCIPLINES[line]['kind'] != 'weapon'


def _used(game, it):
    game.remove_one(it)
    return True


def _tome(game, ctx):
    return next((i for i in game.player.inv if i.id == ctx.get('item') and i.k == 'tome'), None)


def r_wake(game, choice, ctx):
    it = _tome(game, ctx)
    if choice != 'yes' or not it:
        return
    line = SK.SKILLS[it.t].line
    game.player.classes = [line]
    game.msg(f'You remember. {school(line)} was always yours: you are a {PURE[line]}.', 'gold')
    from . import chronicle as CH
    CH.add(game, 'Your deeds', f'A tome of {school(line)} woke a memory: you are a {PURE[line]}.', 'seen',
           where=game.loc_name(), key='first_class', title='Who you are')
    if SK.learn(game, it.t):
        _used(game, it)
    from . import guide as GDE
    GDE.tip(game, 'class')
    game.end_turn(1)


def r_second(game, choice, ctx):
    it = _tome(game, ctx)
    if choice != 'yes' or not it:
        return
    p = game.player
    line = SK.SKILLS[it.t].line
    p.classes = [p.classes[0], line]
    name = title(game)
    game.msg(f'{school(line)} opens to you as well. You are a {name}.', 'gold')
    from . import chronicle as CH
    CH.add(game, 'Your deeds', f'A second school, {school(line)}: you are a {name}.', 'seen',
           where=game.loc_name(), key='second_class', title='A second school')
    if SK.learn(game, it.t):
        _used(game, it)
    game.end_turn(1)


# ------------------------------------------------------------------ the bar
def slot_skill(game, i):
    """The skill on key i+1: keys 1-2 come from your weapon, 3-6 from what you chose."""
    if i in WEAPON:
        from . import weaponskills as WS
        return WS.skills_now(game)[i]
    p = game.player
    return p.bar[i] if i < len(p.bar) else None


def _elites():
    from . import guilds as GU
    out = {sid for rows in GU.TEACH.values() for sid, rk, *_ in rows if rk >= 4}
    return out | {v[0] for v in GU.COMBOS.values()}


def is_elite(sk):
    """An elite: a guild's rank-4 technique, or one for those who serve two guilds. The others of rank 1 and 2 are
    ordinary skills of their school (or, from the weapon guilds, a weapon skill)."""
    return sk.guild and sk.id in _elites()


def weapon_guild(sk):
    """A technique of the Wardens or the Still Hand that may take the place of one of its weapon's two skills."""
    return sk.guild and not is_elite(sk) and SK.DISCIPLINES[sk.line]['kind'] == 'weapon'


def of_no_use(game, sid):
    """A guild master's word when a technique is of no use to you, or None."""
    sk = SK.SKILLS[sid]
    if is_elite(sk) or weapon_guild(sk) or sk.line in classes(game):
        return None
    return (f'"{sk.name} is of {school(sk.line)}, and that is not one of your schools. I could teach it, and you '
            f'could never use it. Keep your coin."')


def fits(game, sk, i):
    """Whether this skill may go on key i+1. Returns None if it fits, else why not."""
    if i in WEAPON:
        if weapon_guild(sk):
            from . import weaponskills as WS
            k = WS.KIT.get(WS.kit(game))
            if k and WS.WSKILLS[k[0]].line == sk.line:
                return None
            return f'{sk.name} needs {SK.DISCIPLINES[sk.line]["weapon"]} in your hands.'
        return 'Keys 1 and 2 are your weapon\'s own two skills: take up another weapon to change them.'
    if getattr(sk, 'weapon_skill', False) or weapon_guild(sk):
        return 'A weapon skill goes on keys 1 and 2.'
    epic = getattr(sk, 'epic', False)
    if i in ELITE:
        if epic:
            return None if sk.line in classes(game) else f'{sk.name} is not of your schools.'
        return None if is_elite(sk) else 'Key 6 is for one elite or one epic: a guild\'s highest technique, or a ' \
            'teacher\'s.'
    if is_elite(sk) or epic:
        return f'{sk.name} is {"an epic" if epic else "an elite"}: it can only go on key 6.'
    if sk.line not in classes(game):
        return f'{sk.name} is not of your schools.'
    return None


def place(game, sid):
    """Put a newly learnt skill in a free key it fits. Returns the index, or None."""
    p = game.player
    sk = SK.SKILLS[sid]
    for i in CLASS + ELITE:
        if p.bar[i] is None and not fits(game, sk, i):
            p.bar[i] = sid
            return i
    return None


def tidy(game):
    """Take off the bar what no longer fits there (an old save, a weapon skill on 3-6)."""
    p = game.player
    for i in range(len(p.bar)):
        sid = p.bar[i]
        if sid and (i in WEAPON or sid not in SK.SKILLS or fits(game, SK.SKILLS[sid], i)):
            p.bar[i] = None


def register():
    from . import events as EV
    EV.RESOLVERS['wake_class'] = r_wake
    EV.RESOLVERS['second_class'] = r_second


def known_names():
    return sorted(set(PURE.values()) | set(PAIRS.values()))


assert len(PAIRS) == 55 and all(a in SK.DISCIPLINES or a in ('arcane', 'cunning') for p_ in PAIRS for a in p_)

