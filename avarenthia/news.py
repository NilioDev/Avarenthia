"""News travels on foot. What happens in the world is not shouted into your ear: it is told in the inns, by the
people whose business it is. A trader of the Merchants' Guild knows where coin is to be made, and has work for those
who carry it; a travelling merchant knows the prices of the roads he has just come down; the captain of the watch
knows where the trouble is, and pays for heads; innkeepers hear everything, a little late; and travellers and sailors
bring word from far away.

News moves about twenty-five leagues a day. What you hear of a far place is old, and may no longer be true."""
import random

from . import data as D
from .worldgen import cheb

SPEED = 25            # leagues a day
KEEP = 40             # days before a tale is forgotten
NEAR = 45             # what counts as 'around here'


def store(game):
    return game.__dict__.setdefault('news', [])


def post(game, kind, text, x, y):
    """Something happened somewhere. Nobody tells you yet."""
    n = store(game)
    n.append(dict(day=game.day, kind=kind, text=text, x=x, y=y, told=0))
    if len(n) > 80:
        del n[:len(n) - 80]


def origin(game):
    p, here = game.player, game.here
    if here:
        return here.x, here.y
    return (p.x, p.y) if game.cur == 'over' else getattr(game, 'over_pos', (p.x, p.y))


def _age_words(days):
    if days < 1:
        return 'Just today'
    if days < 2:
        return 'Yesterday'
    if days < 7:
        return f'{days} days ago'
    if days < 14:
        return 'A week or so ago'
    return 'Some weeks back'


def known(game, kinds=None, near=NEAR, far=False):
    """What could have reached this place by now."""
    ox, oy = origin(game)
    out = []
    for n in store(game):
        if kinds and n['kind'] not in kinds:
            continue
        d = cheb(n['x'], n['y'], ox, oy)
        age = game.day - n['day']
        if age > KEEP or age * SPEED < d - 6:
            continue
        if far and d < near:
            continue
        if not far and d > near:
            continue
        out.append((n, age, d))
    return out


def tell(game, kinds=None, near=NEAR, far=False):
    """One piece of news, preferring the freshest that has been told least."""
    cands = known(game, kinds, near, far)
    if not cands:
        return None
    cands.sort(key=lambda r: (r[0]['told'], r[1]))
    n, age, d = cands[0]
    n['told'] += 1
    text = n['text'][0].lower() + n['text'][1:] if n['text'][:2] not in ('A ', 'I ') else n['text']
    return f'{_age_words(age)}, they say: {text}' if age >= 1 else f'Just today: {text}'


def trade_gossip(game):
    """A merchant's talk: where things are cheap or dear, on the roads near here. What was true when he passed."""
    line = tell(game, ('trade',))
    if line and random.random() < .6:
        return line
    ox, oy = origin(game)
    w = game.world
    here = game.here
    near = [s for s in w.settlements if cheb(s.x, s.y, ox, oy) <= NEAR and (not here or s.id != here.id) and s.kind != 'deephold']
    if not near:
        return line or 'Trade is slow everywhere. Nobody has coin.'
    s = random.choice(near)
    if random.random() < .5 and s.demand:
        g = random.choice(s.demand)
        return f'"{s.name} was paying well for {D.GOODS[g]["name"].lower()} when I came through. Might still be."'
    g = random.choice(s.produce)
    return f'"{D.GOODS[g]["name"]} is cheap in {s.name}. They make plenty of it there."'


def danger(game):
    return tell(game, ('danger', 'war'), near=60)


def far_news(game):
    return tell(game, None, far=True) or tell(game, ('war', 'danger', 'trade'), near=999)


def gossip(game):
    """The innkeeper: local news first, then whatever the road brought in."""
    return tell(game, None, near=30) or game.rumor()


# ------------------------------------------------------------------ the people who tell it
def board(game, key, kinds, mult, n=3):
    from . import missions as MS
    here = game.here
    if not here:
        return []
    b = here.__dict__.setdefault('boards', {})
    day = here.__dict__.setdefault('boards_day', {})
    if game.day - day.get(key, -99) >= 4 or not b.get(key):
        b[key] = []
        for _ in range(10):
            m = MS.make_offer(game, here, kinds=kinds)
            if m:
                m.reward = round(m.reward * mult)
                b[key].append(m)
            if len(b[key]) >= n:
                break
        day[key] = game.day
    return b[key]


def offer(game, npc, key, kinds, mult, intro):
    from . import events as EV
    from .money import fmt
    jobs = board(game, key, kinds, mult)
    if not jobs:
        game.say(npc, 'Nothing for you just now. Come back in a few days.')
        return
    opts = [(f'{m.title} ({fmt(m.reward)})', f'take:{i}') for i, m in enumerate(jobs)] + [('Not now', 'bye')]
    EV.ask(game, 'newsjob', npc.name, intro + '\n\n' + '\n'.join(f'- {m.desc}' for m in jobs), opts, board=key)


def r_newsjob(game, choice, ctx):
    from . import missions as MS
    here = game.here
    if not here or not choice.startswith('take:'):
        return
    jobs = here.__dict__.get('boards', {}).get(ctx['board'], [])
    i = int(choice[5:])
    if i >= len(jobs):
        return
    m = jobs[i]
    here.board.append(m)
    if MS.accept(game, here, m):
        jobs.remove(m)
    elif m in here.board:
        here.board.remove(m)


def talk_factor(game, npc):
    from . import events as EV
    EV.ask(game, 'factor', npc.name, '"The Merchants\' Guild has goods to move and letters to carry, and pays those who '
           'move them. And if you trade on your own account, I can tell you what I hear."',
           [('Ask for trade work', 'work'), ('What is selling where?', 'prices'), ('Goodbye', 'bye')], npc=npc.id)


def r_factor(game, choice, ctx):
    npc = next((o for o in game.map.mons if o.id == ctx.get('npc')), None)
    if not npc:
        return
    if choice == 'work':
        offer(game, npc, 'factor', ['freight', 'courier', 'rush', 'debt', 'cargo'], 1.2, '"Here is what the Guild needs done:"')
    elif choice == 'prices':
        game.say(npc, trade_gossip(game))


def talk_captain(game, npc):
    from . import events as EV
    EV.ask(game, 'captain', npc.name, '"Keep it short. What do you want?"',
           [('Any trouble about?', 'news'), ('Are there bounties?', 'work'), ('Nothing', 'bye')], npc=npc.id)


def r_captain(game, choice, ctx):
    npc = next((o for o in game.map.mons if o.id == ctx.get('npc')), None)
    if not npc:
        return
    if choice == 'news':
        game.say(npc, danger(game) or random.choice(['Quiet, for now. I do not trust quiet.',
                                                     'Nothing worth my breath. Keep your eyes open on the roads.']))
    elif choice == 'work':
        here = game.here
        extra = ['boats'] if here is not None and getattr(here, 'harbour', False) else []
        offer(game, npc, 'captain', ['hunt', 'hunt', 'bounty', 'escort', 'defend', 'deserter', 'rescue'] + extra, 1.1,
              '"The garrison pays for these:"')


def talk_sailor(game, npc):
    game.say(npc, far_news(game) or random.choice(['Calm seas, empty nets. Nothing more to tell.',
                                                   'Nothing from the far ports. Too quiet, if you ask me.']))


def register():
    from . import events as EV
    EV.RESOLVERS.update(newsjob=r_newsjob, factor=r_factor, captain=r_captain)


register()
