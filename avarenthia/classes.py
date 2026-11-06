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
WEAPON, CLASS, EPIC = (0, 1), (2, 3, 4, 5), (6,)      # keys 1-2, 3-6 (at most one elite), 7 (round 57)
BAR = 7


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
    """The skill on key i+1: keys 1-2 come from your weapon, 3-7 from what you chose."""
    if i in WEAPON:
        from . import weaponskills as WS
        return WS.skills_now(game)[i]
    p = game.player
    return p.bar[i] if i < len(p.bar) else None


def can_change_bar(game):
    """The bar changes in a town, and right after a rest (an inn's bed or your camp) before you walk on; never
    with a foe in sight. None when you may, else why not."""
    from . import trees as TT
    if game.map.kind != 'town' and not TT.can_rest_spend(game):
        return 'You can change your bar in a town, or right after a rest before you walk on.'
    if game.hostile_visible():
        return 'Not with a foe in sight.'
    return None


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
    if i in EPIC:
        if epic:
            return None if sk.line in classes(game) else f'{sk.name} is not of your schools.'
        return 'Key 7 is for your epic, a teacher\'s highest gift.'
    if epic:
        return f'{sk.name} is an epic: it can only go on key 7.'
    if is_elite(sk):
        p = game.player
        other = next((s for k, s in enumerate(p.bar) if k in CLASS and k != i and s and s != sk.id
                      and s in SK.SKILLS and is_elite(SK.SKILLS[s])), None)
        return f'Only one elite on keys 3 to 6, and {SK.SKILLS[other].name} is there.' if other else None
    if sk.line not in classes(game):
        return f'{sk.name} is not of your schools.'
    return None


def pad(game):
    """The bar has seven places (an old save may have fewer)."""
    p = game.player
    while len(p.bar) < BAR:
        p.bar.append(None)


def place(game, sid):
    """Put a newly learnt skill in a free key it fits. Returns the index, or None."""
    p = game.player
    pad(game)
    sk = SK.SKILLS[sid]
    for i in CLASS + EPIC:
        if p.bar[i] is None and not fits(game, sk, i):
            p.bar[i] = sid
            return i
    return None


def tidy(game):
    """Take off the bar what no longer fits there (an old save, a weapon skill on 3-6, a second elite)."""
    p = game.player
    pad(game)
    for i in range(len(p.bar)):
        sid = p.bar[i]
        if sid and (i in WEAPON or i >= BAR or sid not in SK.SKILLS or fits(game, SK.SKILLS[sid], i)):
            p.bar[i] = None
    del p.bar[BAR:]


BOOK_TURNS = 3


def book_why(game, sid):
    """Whether a known skill may be cast from the book (the [z] list): None, or why not."""
    sk = SK.SKILLS[sid]
    p = game.player
    if sid in p.bar:
        return f'{sk.name} is on your bar: use its key.'
    if getattr(sk, 'epic', False) or is_elite(sk):
        return f'{sk.name} is {"an epic" if getattr(sk, "epic", False) else "an elite"}: it works only from the bar.'
    if getattr(sk, 'weapon_skill', False) or weapon_guild(sk) or not class_line(sk.line):
        return 'A weapon skill works only from keys 1 and 2.'
    if sk.line not in classes(game):
        return f'{sk.name} is not of your schools.'
    if sk.passive:
        return f'{sk.name} needs no calling: it is simply how you do things.'
    if p.cooldowns.get(sid, 0) > 0:
        return f'{sk.name} is recharging ({p.cooldowns[sid]} turns).'
    if not SK.can_pay(game, sk):
        return f'Not enough {SK.pool(sk)} for {sk.name}.'
    return None


def from_book(game, sid):
    """Cast a known skill that is not on the bar, from the book: two turns finding the page, the third casts it. A
    new foe in sight or a blow breaks it off; the turns are gone and nothing is cast. Returns the turns of the last
    step (the first two are spent here)."""
    why = book_why(game, sid)
    if why:
        game.msg(why, 'bad')
        return 0
    p = game.player
    for _ in range(BOOK_TURNS - 1):
        seen = {id(o) for o in game.visible_hostiles()}
        life = p.life
        game.end_turn(1)
        if game.dead:
            return 0
        new = any(id(o) not in seen for o in game.visible_hostiles())
        if new or p.life < life:
            game.msg('You lose your place in the book: ' + ('something comes into sight.' if new else 'a blow!'),
                     'bad')
            return 0
    return SK.use(game, None, book=sid)


def register():
    from . import events as EV
    EV.RESOLVERS['wake_class'] = r_wake
    EV.RESOLVERS['second_class'] = r_second


def known_names():
    return sorted(set(PURE.values()) | set(PAIRS.values()))


assert len(PAIRS) == 55 and all(a in SK.DISCIPLINES or a in ('arcane', 'cunning') for p_ in PAIRS for a in p_)

