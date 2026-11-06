"""Games at the inn (round 59): Bones, The Count and Vigil, played at an inn's gaming table.

The gaming table stands near the innkeeper of every inn (laid on entering, `lay`), with two regulars by it. Walk into
the table or a regular: Bones and The Count in the evening, for small stakes with a limit per inn per night; Vigil
at any hour, for name only. With Cunning you see a loaded bone or keep count of the cards; caught at it, or counting
too well too often, you are not served at that inn for some days. Vigil has a master in a few places over the land,
told by rumour; beat them all for a deed in the chronicle.

The rules are pure classes (`Bones`, `Count`, `Vigil`), drawn by `inngames_ui.py`. What lasts lives on the player:
`p.inngames` (the night's stakes, where you are barred, the masters beaten)."""
import random
import zlib

from . import data as D

GAMETABLE = D.GAMETABLE
REGULAR = 'gamer'

# each people's Bones: its name and its twist (the rule stays the same)
BONES = {
    'human': ('Bones', 'A skull ends your round with nothing, unless it is your first throw.'),
    'dwarf': ('Anvil and Spark', 'Three alike in one throw is an anvil: it counts double.'),
    'halfling': ('Pips', 'A one is lucky: it counts as six.'),
    'orc': ('Teeth', 'A skull in your first throw bites: the other bones of that throw count double.'),
}
BONES_OF = {'goblin': 'orc', 'kobold': 'orc', 'gnoll': 'orc', 'shanty': 'orc', 'gnome': 'halfling', 'elf': 'human',
            'lizard': 'human'}
# each people's Vigil board: its name and its colours (dark square, light square, rim, hearth)
BOARDS = {
    'human': ('the oak board', (40, 32, 24), (50, 40, 28), (80, 52, 30), (78, 60, 34)),
    'dwarf': ('the forge board', (36, 26, 22), (44, 30, 24), (92, 46, 26), (90, 60, 30)),
    'elf': ('the glade board', (24, 38, 26), (30, 46, 30), (40, 70, 44), (70, 80, 46)),
    'halfling': ('the kitchen board', (52, 40, 26), (62, 48, 30), (90, 60, 34), (96, 70, 40)),
    'orc': ('the bone board', (40, 34, 30), (52, 44, 38), (84, 40, 32), (80, 66, 50)),
    'gnome': ('the brass board', (40, 36, 24), (52, 46, 28), (96, 78, 36), (110, 90, 40)),
}
BOARD_OF = {'goblin': 'orc', 'kobold': 'orc', 'gnoll': 'orc', 'shanty': 'orc', 'lizard': 'elf'}
SIDES = ('the Watch', 'the Iron')
WIN_AT = 30                  # Bones: the first to bank this many
STAKES = (2, 5, 10, 20)      # copper
NIGHT_LIMIT = 50             # copper staked per inn per night (a city's inns take 100)
BARRED_DAYS = 5


# ------------------------------------------------------------------ the player's side
def state(game):
    p = game.player
    st = getattr(p, 'inngames', None)
    if st is None:
        st = p.inngames = {}
    st.setdefault('night', [None, None, 0])      # [night, inn, staked]
    st.setdefault('barred', {})                  # inn key -> the day it ends
    st.setdefault('masters', [])                 # settlement ids of the Vigil masters beaten
    st.setdefault('won', {'bones': 0, 'count': 0, 'vigil': 0})
    st.setdefault('counted', [None, 0])          # [night at this inn, hands won while counting]
    return st


def night(game):
    from .towns import hour
    return game.day if hour(game) >= 12 else game.day - 1


def evening(game):
    from .towns import hour
    h = hour(game)
    return h >= 17 or h < 2


def inn_key(game):
    return game.map.key


def settlement(game):
    from .townlife import _sett
    return _sett(game, game.map)


def limit(game):
    s = settlement(game)
    return NIGHT_LIMIT * 2 if s is not None and s.is_city else NIGHT_LIMIT


def staked(game):
    st = state(game)
    nt = st['night']
    return nt[2] if nt[0] == night(game) and nt[1] == inn_key(game) else 0


def stake_room(game):
    """How much more may be staked at this inn tonight."""
    return max(0, limit(game) - staked(game))


def put_stake(game, c):
    st = state(game)
    st['night'] = [night(game), inn_key(game), staked(game) + c]
    game.player.gold -= c


def barred(game):
    st = state(game)
    until = st['barred'].get(inn_key(game))
    if until is None:
        return False
    if game.day >= until:
        del st['barred'][inn_key(game)]
        return False
    return True


def bar(game, why):
    """Shown the door: no games and no service at this inn for some days, and the town hears of it."""
    st = state(game)
    st['barred'][inn_key(game)] = game.day + BARRED_DAYS
    s = settlement(game)
    if s is not None:
        s.rep -= 2
    game.msg(why, 'bad')
    game.msg(f'You are not welcome at this inn for {BARRED_DAYS} days.', 'bad')


def people(game):
    return getattr(game.map, 'people', None) or 'human'


def bones_kind(pp):
    pp = BONES_OF.get(pp, pp)
    return pp if pp in BONES else 'human'


def board_kind(pp):
    pp = BOARD_OF.get(pp, pp)
    return pp if pp in BOARDS else 'human'


def cunning(game):
    """Your rank in Cunning, or 0 if it is not your class."""
    from . import arts as ART
    from . import skills as SK
    return max(1, SK.rank(game, 'cunning')) if 'cunning' in ART.classes(game) else 0


# ------------------------------------------------------------------ the table on the map
def lay(game, m):
    """Set a gaming table in the inn (the one with the innkeeper, else the first) and two regulars by it, once."""
    from .entities import make_npc
    keeper = next((o for o in m.mons if o.is_npc and getattr(o, 'role', '') == 'inn'), None)
    inns = [b for b in getattr(m, 'buildings', ()) or () if isinstance(b, dict) and b.get('kind') == 'inn'
            and b.get('plot') is not None]
    if keeper is None and not inns:
        return None
    gt = getattr(m, 'gametable', None)
    if gt is None:
        cells = None
        if inns:
            home = next((b for b in inns if keeper and (keeper.x, keeper.y) in set(b['plot'].inside)), inns[0])
            cells = list(home['plot'].inside)
        else:
            cells = _near(m, keeper)
        gt = _spot(m, cells)
        if gt is None:
            return None
        m.set(gt[0], gt[1], GAMETABLE)
        m.gametable = gt
    regs = [o for o in m.mons if o.is_npc and getattr(o, 'role', '') == REGULAR]
    if not regs:
        from .races import random_name
        race = people(game) if people(game) not in ('shanty', None) else 'human'
        around = [(gt[0] + dx, gt[1] + dy) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dx or dy]
        free = [c for c in around if m.inb(*c) and m.tile(*c) in (D.FLOOR, D.PLANK) and not m.mon_at(*c)]
        free.sort(key=lambda c: c[0] != gt[0] and c[1] != gt[1])          # beside it before at its corners
        keep = random.getstate()                     # the regulars' names come from the map, not the world's dice
        random.seed(zlib.crc32(str(m.key).encode()))
        for c in free[:2]:
            o = make_npc(game, random_name(race if race in ('human', 'dwarf', 'elf', 'halfling', 'orc', 'gnome', 'goblin')
                                           else 'human'), REGULAR, '#c8a078', c[0], c[1], True, race=race)
            m.mons.append(o)
        random.setstate(keep)
    return gt


def _near(m, keeper):
    """The cells a keeper without an inn building can reach: over floor, across their counter, never by a door."""
    seen, todo, out = {(keeper.x, keeper.y)}, [(keeper.x, keeper.y, 0)], []
    while todo:
        x, y, d = todo.pop(0)
        out.append((x, y))
        if d >= 8:
            continue
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if (nx, ny) not in seen and m.inb(nx, ny) and m.tile(nx, ny) in (D.FLOOR, D.PLANK, D.TABLE, D.STALL):
                seen.add((nx, ny))
                todo.append((nx, ny, d + 1))
    return out


def _spot(m, cells):
    """A table among the cells with room round it and no door beside it; else a free floor with room to sit."""
    def free(c):
        return sum(1 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                   if m.inb(c[0] + dx, c[1] + dy) and m.tile(c[0] + dx, c[1] + dy) in (D.FLOOR, D.PLANK)
                   and not m.mon_at(c[0] + dx, c[1] + dy))

    def by_door(c):
        return any(m.inb(c[0] + dx, c[1] + dy) and D.TILES[m.tile(c[0] + dx, c[1] + dy)].door
                   for dy in (-1, 0, 1) for dx in (-1, 0, 1))
    cells = sorted(set(cells))
    for want, need in ((D.TABLE, 2), (D.TABLE, 1), (D.PLANK, 3), (D.FLOOR, 3)):
        for c in cells:
            if m.tile(*c) == want and free(c) >= need and not by_door(c) and not m.mon_at(*c):
                return c
    return None


def regulars(game):
    return [o for o in game.map.mons if o.is_npc and getattr(o, 'role', '') == REGULAR]


# ------------------------------------------------------------------ the masters of Vigil
def masters(game):
    """{settlement id: master's name}: the biggest town of each people keeps a master of Vigil (seven at most). Towns,
    for their inns are sure; a city may be laid out without one."""
    w = game.world
    cache = getattr(w, '_vigil_masters', None)
    if cache is not None:
        return cache
    best = {}
    size = {'town': 4, 'deephold': 3, 'village': 2}
    for s in w.settlements:
        if ('inn' not in getattr(s, 'services', ()) and s.kind != 'deephold') or s.kind not in size:
            continue
        pp = 'dwarf' if s.kind == 'deephold' else getattr(s, 'race', 'human')
        k = (size.get(s.kind, 1), -s.id)
        if pp not in best or k > best[pp][0]:
            best[pp] = (k, s)
    from .races import random_name
    keep = random.getstate()
    out = {}
    for pp, (_k, s) in sorted(best.items(), key=lambda kv: kv[1][1].id)[:7]:
        random.seed(s.id * 7919 + 59)
        out[s.id] = random_name(pp if pp in ('human', 'dwarf', 'elf', 'halfling', 'orc', 'gnome', 'goblin') else 'human')
    random.setstate(keep)
    w.__dict__['_vigil_masters'] = out
    return out


def master_here(game):
    s = settlement(game)
    if s is None:
        return None
    return masters(game).get(s.id)


def rumour(game):
    """A master of Vigil you have not beaten, and where."""
    st = state(game)
    left = [(sid, nm) for sid, nm in masters(game).items() if sid not in st['masters']]
    if not left:
        return None
    sid, nm = random.choice(left)
    s = game.world.settlements[sid]
    game.reveal_place(s.x, s.y, 1)
    return random.choice([f'Nobody beats {nm} at Vigil. Try the gaming table in {s.name}, if you want to lose.',
                          f'{nm} of {s.name} has played Vigil since before the war, and lost twice. Both times on purpose.',
                          f'If you think you can play Vigil, go to {s.name} and sit down across from {nm}.'])


# ------------------------------------------------------------------ walking into the table
def table(game):
    """The gaming table, or a regular by it: what to play."""
    from . import events as EV
    from .money import fmt
    m = game.map
    if barred(game):
        game.msg('The regulars turn their backs. Nobody here will play with you, not this week.', 'bad')
        return 0
    regs = regulars(game)
    a = regs[0].name.split()[0] if regs else 'a regular'
    b = regs[1].name.split()[0] if len(regs) > 1 else 'a carter'
    keeper = next((o for o in m.mons if o.is_npc and getattr(o, 'role', '') == 'inn'), None)
    dealer = keeper.name.split()[-1] if keeper else 'the innkeeper'
    nm = BONES[bones_kind(people(game))][0]
    master = master_here(game)
    eve = evening(game)
    room = stake_room(game)
    can = eve and room >= STAKES[0] and game.player.gold >= STAKES[0]
    opts = [(f'Play {nm} with {a} and {b}', 'bones' if can else None),
            (f'Play The Count, {dealer} deals', 'count' if can else None),
            (f'Play Vigil with {master + ", the master" if master else a}', 'vigil'),
            ('Leave the table', 'leave')]
    text = 'Bones and cards in a cup, a board under a cloth.'
    if not eve:
        text += ' The stakes wait for the evening; a game of Vigil can be had at any hour.'
    elif room < STAKES[0]:
        text += f' You have staked all this inn allows in one night ({fmt(limit(game))}).'
    else:
        text += f' Tonight you may stake {fmt(room)} more here.'
    if master:
        text += f'\n\n{master} sits by the board. They say nobody here has beaten {master} in years.'
    EV.ask(game, 'inngame', 'The gaming table', text, opts, a=a, b=b, dealer=dealer, master=master)
    return 0


def r_table(game, choice, ctx):
    if choice in ('bones', 'count', 'vigil'):
        from . import met as MET
        MET.saw(game, 'game: ' + choice)
        game.request = ('inngame', choice, dict(ctx))


def register():
    from . import events as EV
    EV.RESOLVERS['inngame'] = r_table


register()


# ------------------------------------------------------------------ Bones
class Bones:
    """Three knucklebones, press your luck. Faces 1-5 and a skull (0). Throw, set aside one or more, throw the rest
    or bank. A skull in any throw but the first of your round ends the round with nothing."""
    SKULL = 0

    def __init__(self, kind, names, stake, rng=None, cunning=0, loaded=False):
        self.kind, self.stake, self.rng = kind, stake, rng or random.Random()
        self.players = [dict(name='You', you=True, banked=0, cheat=loaded)]
        for nm in names:
            self.players.append(dict(name=nm, you=False, banked=0, cheat=self.rng.random() < .25,
                                     bank_at=self.rng.choice((10, 12, 14))))
        self.pot = stake * len(self.players)
        self.seen = None                         # the cheat your Cunning saw
        for pl in self.players[1:]:
            if pl['cheat'] and cunning and self.rng.random() < .5 + cunning * .02:
                self.seen = pl['name']
        self.loaded = loaded
        self.cur = self.rng.randrange(len(self.players))      # who throws first: the cup goes round
        self.log = []
        self.winner = None
        self.new_round()

    # one player's round
    def new_round(self):
        self.round = 0
        self.free = 3                            # bones still to throw
        self.thrown = []                         # faces of the last throw
        self.marked = []                         # which of them are set aside
        self.first = True
        self.phase = 'throw'                     # 'throw', 'pick', 'over'

    def face(self, loaded):
        if loaded:
            return self.rng.choice((5, 5, 5, 4, 3, 2))
        return self.rng.randint(0, 5)

    def throw(self):
        pl = self.players[self.cur]
        faces = [self.face(pl['cheat'] and k == 0) for k in range(self.free)]
        self.thrown, self.marked = faces, [False] * len(faces)
        skulls = faces.count(self.SKULL)
        who = 'You throw' if pl['you'] else f'{pl["name"]} throws'
        self.say(f'{who}: {words(faces)}.')
        if skulls and not self.first:
            self.say('A skull. The round is lost.' if pl['you'] else f'A skull! {pl["name"]} loses the round.')
            self.end_turn(bank=False)
            return False
        if skulls == len(faces):
            self.say('Nothing but skulls.')
            self.end_turn(bank=False)
            return False
        self.phase = 'pick'
        return True

    def value(self, faces, idx):
        """The worth of the bones set aside out of this throw."""
        kept = [faces[i] for i in idx]
        v = sum(6 if (f == 1 and self.kind == 'halfling') else f for f in kept)
        if self.kind == 'dwarf' and len(faces) == 3 and len(kept) == 3 and len(set(faces)) == 1:
            v *= 2
        if self.kind == 'orc' and self.first and self.SKULL in faces:
            v *= 2
        return v

    def can_mark(self, i):
        return 0 <= i < len(self.thrown) and self.thrown[i] != self.SKULL

    def toggle(self, i):
        if self.phase == 'pick' and self.can_mark(i):
            self.marked[i] = not self.marked[i]

    def take(self):
        idx = [i for i, m in enumerate(self.marked) if m]
        self.round += self.value(self.thrown, idx)
        self.free -= len(idx)
        if self.free == 0:
            self.free = 3                        # all three set aside: they come back
        self.first = False
        self.thrown, self.marked = [], []

    def throw_rest(self):
        """Set the marked bones aside and throw the others."""
        if self.phase != 'pick' or not any(self.marked):
            return False
        self.take()
        return self.throw()

    def bank(self):
        if self.phase != 'pick' or not any(self.marked):
            return False
        self.take()
        self.end_turn(bank=True)
        return True

    def end_turn(self, bank):
        pl = self.players[self.cur]
        if bank:
            pl['banked'] += self.round
            self.say(f'{"You bank" if pl["you"] else pl["name"] + " banks"} {self.round}: {pl["banked"]} in all.')
        if pl['banked'] >= WIN_AT:
            self.winner = self.cur
            self.phase = 'over'
            self.say('You win the pot!' if pl['you'] else f'{pl["name"]} wins the pot.')
            return
        self.cur = (self.cur + 1) % len(self.players)
        self.new_round()

    def ai(self):
        """The others play their rounds until it is your turn again (or the game is over)."""
        guard = 0
        while self.phase != 'over' and not self.players[self.cur]['you'] and guard < 200:
            guard += 1
            pl = self.players[self.cur]
            if not self.throw():
                continue
            good = [i for i, f in enumerate(self.thrown) if f != self.SKULL]
            for i in good:
                self.marked[i] = True
            idx = [i for i, m in enumerate(self.marked) if m]
            would = self.round + self.value(self.thrown, idx)
            left = self.free - len(idx)
            if pl['banked'] + would >= WIN_AT or would >= pl['bank_at'] or (left == 1 and would >= 8):
                self.bank()
            else:
                self.take()
                self.phase = 'throw'

    def say(self, s):
        self.log.append(s)
        del self.log[:-6]

    @property
    def you_won(self):
        return self.winner is not None and self.players[self.winner]['you']


def words(faces):
    return ', '.join('a skull' if f == 0 else str(f) for f in faces)


# ------------------------------------------------------------------ The Count
SUITS = ('Stars', 'Iron', 'Water')


class Count:
    """Draw towards 21 or stop, against the dealer. Three suits of 1-10; a Water card lies face down until both stop
    ("no one has ever counted the water"). Over 21 and the stake is the dealer's."""

    def __init__(self, rng=None):
        self.rng = rng or random.Random()
        self.deck = []
        self.shuffle()
        self.you, self.dealer = [], []
        self.phase = 'stake'                     # 'stake', 'play', 'done'
        self.stake = 0
        self.result = None                       # 'win', 'lose', 'push'
        self.log = []

    def shuffle(self):
        self.deck = [(n, s) for s in SUITS for n in range(1, 11)]
        self.rng.shuffle(self.deck)

    def deal(self, stake):
        if len(self.deck) < 10:
            self.shuffle()
            self.say('The deck is shuffled.')
        self.stake = stake
        self.you = [self.deck.pop(), self.deck.pop()]
        self.dealer = [self.deck.pop(), self.deck.pop()]
        self.phase = 'play'
        self.result = None
        if self.known(self.you) > 21:
            self.finish()

    @staticmethod
    def known(hand):
        return sum(n for n, s in hand if s != 'Water')

    @staticmethod
    def hidden(hand):
        return sum(1 for n, s in hand if s == 'Water')

    @staticmethod
    def total(hand):
        return sum(n for n, s in hand)

    def draw(self):
        if self.phase != 'play':
            return
        c = self.deck.pop()
        self.you.append(c)
        self.say('You draw: a Water card. It stays face down.' if c[1] == 'Water' else f'You draw the {c[0]} of {c[1]}.')
        if self.known(self.you) > 21 or not self.deck:
            self.finish()

    def stop(self):
        if self.phase == 'play':
            self.finish()

    def finish(self):
        """The dealer draws while short of 17 by what they can see (a face-down Water card counted as five and a
        half), then every card turns over."""
        if self.known(self.you) <= 21:
            while self.deck and self.known(self.dealer) + 5.5 * self.hidden(self.dealer) < 17:
                self.dealer.append(self.deck.pop())
        y, d = self.total(self.you), self.total(self.dealer)
        if y > 21:
            self.result = 'lose'
        elif d > 21 or y > d:
            self.result = 'win'
        elif y == d:
            self.result = 'push'
        else:
            self.result = 'lose'
        self.say({'win': f'{y} against {d}. The stake is yours.', 'lose': f'{y} against {d}. The dealer takes it.',
                  'push': f'{y} against {d}. Even: the stake comes back.'}[self.result] if y <= 21 else
                 f'{y}: over. The dealer takes it.')
        self.phase = 'done'

    def left(self):
        """What is still in the deck, by suit, and how many high cards (8-10): what counting tells you."""
        by = {s: sum(1 for n, q in self.deck if q == s) for s in SUITS}
        return by, sum(1 for n, q in self.deck if n >= 8)

    def say(self, s):
        self.log.append(s)
        del self.log[:-4]


# ------------------------------------------------------------------ Vigil
N = 9
HEARTH = (4, 4)
IRON_START = [(3, 0), (4, 0), (5, 0), (4, 1), (0, 3), (0, 4), (0, 5), (1, 4), (8, 3), (8, 4), (8, 5), (7, 4),
              (3, 8), (4, 8), (5, 8), (4, 7)]
WATCH_START = [(4, 2), (4, 3), (4, 5), (4, 6), (2, 4), (3, 4), (5, 4), (6, 4)]
DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))


class Vigil:
    """A tafl board of 9 x 9: the Iron That Said No (I, sixteen) against the Watch of the stars (W, eight, and Vael,
    V, on the hearth in the middle). Every piece moves like a rook; only Vael may stand on the hearth. A piece
    between two foes on a line (or a foe and the empty hearth) is taken. The Watch wins when Vael reaches the rim;
    the Iron wins when Vael is taken: closed in on four sides on the hearth or beside it, between two Iron further
    out (the old rule of the board). The Iron moves first."""

    def __init__(self, you='W', strength=1, rng=None):
        self.b = ['.'] * (N * N)
        for c, r in IRON_START:
            self.b[r * N + c] = 'I'
        for c, r in WATCH_START:
            self.b[r * N + c] = 'W'
        self.b[HEARTH[1] * N + HEARTH[0]] = 'V'
        self.you, self.strength = you, strength
        self.rng = rng or random.Random()
        self.turn = 'I'
        self.winner = None                     # 'I', 'W' or 'draw'
        self.plies = 0
        self.log = []
        self.taken = {'I': 0, 'W': 0}

    # the board
    def at(self, c, r):
        return self.b[r * N + c]

    @staticmethod
    def side(p):
        return 'W' if p in 'WV' else 'I' if p == 'I' else None

    def moves(self, side, b=None):
        b = b or self.b
        out = []
        for i, p in enumerate(b):
            if p == '.' or (p == 'I') != (side == 'I'):
                continue
            c, r = i % N, i // N
            for dc, dr in DIRS:
                nc, nr = c + dc, r + dr
                while 0 <= nc < N and 0 <= nr < N and b[nr * N + nc] == '.':
                    if (nc, nr) != HEARTH or p == 'V':
                        out.append((i, nr * N + nc))
                    nc, nr = nc + dc, nr + dr
        return out

    def legal_from(self, c, r):
        i = r * N + c
        return [t for f, t in self.moves(self.turn) if f == i]

    @staticmethod
    def apply(b, mv):
        """The board after a move, and how many it took."""
        f, t = mv
        b = b[:]
        p = b[f]
        b[t], b[f] = p, '.'
        side = 'I' if p == 'I' else 'W'
        c, r = t % N, t // N
        took = 0
        for dc, dr in DIRS:
            nc, nr = c + dc, r + dr
            fc, fr = nc + dc, nr + dr
            if not (0 <= fc < N and 0 <= fr < N):
                continue
            q = b[nr * N + nc]
            if q == '.' or q == 'V' or (q == 'I') == (side == 'I'):
                continue
            far = b[fr * N + fc]
            mine = (far == 'I') if side == 'I' else (far in 'WV')
            if mine or (far == '.' and (fc, fr) == HEARTH):
                b[nr * N + nc] = '.'
                took += 1
        return b, took

    @staticmethod
    def outcome(b):
        """'W' when Vael stands on the rim, 'I' when Vael is taken, else None. On the hearth or beside it Vael is
        taken only when closed in on four sides (the hearth counts as Iron); further out, between two Iron on a
        line, like any piece."""
        try:
            v = b.index('V')
        except ValueError:
            return 'I'
        c, r = v % N, v // N
        if c in (0, N - 1) or r in (0, N - 1):
            return 'W'

        def iron(cc, rr):
            q = b[rr * N + cc]
            return q == 'I' or (q == '.' and (cc, rr) == HEARTH)
        if abs(c - HEARTH[0]) + abs(r - HEARTH[1]) <= 1:
            return 'I' if all(iron(c + dc, r + dr) for dc, dr in DIRS) else None
        if (iron(c - 1, r) and iron(c + 1, r)) or (iron(c, r - 1) and iron(c, r + 1)):
            return 'I'
        return None

    def play(self, mv):
        """Make a move for the side to move. Returns True if it was legal."""
        if self.winner or mv not in self.moves(self.turn):
            return False
        p = self.b[mv[0]]
        self.b, took = self.apply(self.b, mv)
        foe = 'W' if self.turn == 'I' else 'I'
        self.taken[foe] += took
        who = 'You' if self.turn == self.you else 'They'
        self.say(f'{who}: {sq(mv[0])}-{sq(mv[1])}' + (f', {took} taken' if took else '') +
                 (' (Vael)' if p == 'V' else ''))
        self.plies += 1
        self.turn = foe
        w = self.outcome(self.b)
        if w:
            self.winner = w
        elif not self.moves(self.turn):
            self.winner = 'I' if self.turn == 'W' else 'W'
        elif self.plies >= 200:
            self.winner = 'draw'
        return True

    # the other player
    def score(self, b):
        """How good the board is for the Watch (the Iron wants it low)."""
        w = self.outcome(b)
        if w == 'W':
            return 10000
        if w == 'I':
            return -10000
        v = b.index('V')
        c, r = v % N, v // N
        s = 12 * sum(1 for p in b if p == 'W') - 7 * sum(1 for p in b if p == 'I')
        lines = 0
        for dc, dr in DIRS:
            nc, nr = c + dc, r + dr
            while 0 <= nc < N and 0 <= nr < N and b[nr * N + nc] == '.':
                nc, nr = nc + dc, nr + dr
            if not (0 <= nc < N and 0 <= nr < N):
                lines += 1                       # an open line to the rim
        s += 60 * lines + (400 if lines >= 2 else 0)
        s -= 4 * min(c, r, N - 1 - c, N - 1 - r)
        for dc, dr in DIRS:
            if b[(r + dr) * N + c + dc] == 'I':
                s -= 14
        return s

    def best(self):
        """The move the other player makes: deeper and steadier the stronger they are."""
        side = self.turn
        sign = 1 if side == 'W' else -1
        depth = {1: 1, 2: 2, 3: 2}.get(self.strength, 1)
        noise = {1: 40, 2: 10, 3: 0}.get(self.strength, 40)
        moves = self.moves(side)
        self.rng.shuffle(moves)
        scored = []
        for mv in moves:
            nb, _took = self.apply(self.b, mv)
            if depth == 1 or self.outcome(nb):
                v = sign * self.score(nb)
            else:
                v = self._reply(nb, 'I' if side == 'W' else 'W', sign, self.strength >= 3)
            scored.append((v + self.rng.uniform(0, noise), mv))
        return max(scored)[1] if scored else None

    def _reply(self, b, side, sign, full):
        """The best the other side can answer (from the mover's sight: the lowest of what follows)."""
        worst = None
        moves = self.moves(side, b)
        if not full and len(moves) > 40:
            moves = self._likely(b, moves, side)
        for mv in moves:
            nb, _took = self.apply(b, mv)
            v = sign * self.score(nb)
            if worst is None or v < worst:
                worst = v
                if v <= -9000:
                    break
        return worst if worst is not None else sign * self.score(b)

    def _likely(self, b, moves, side):
        """The replies worth looking at: Vael's, and those that take or land next to something."""
        out = []
        for mv in moves:
            if b[mv[0]] == 'V':
                out.append(mv)
                continue
            c, r = mv[1] % N, mv[1] // N
            if any(0 <= c + dc < N and 0 <= r + dr < N and b[(r + dr) * N + c + dc] != '.' for dc, dr in DIRS):
                out.append(mv)
        return out or moves

    def say(self, s):
        self.log.append(s)
        del self.log[:-5]


def sq(i):
    return f'{"abcdefghi"[i % N]}{N - i // N}'


# ------------------------------------------------------------------ the end of a game
def bones_over(game, g):
    """Settle a game of Bones: the pot, a loaded bone found out, the name you make."""
    p = game.player
    st = state(game)
    game.end_turn(20)
    if g.loaded and random.random() < max(.05, .25 - cunning(game) * .01):
        bar(game, 'A hand on your wrist: "That bone stands too still, friend." The pot goes to the others.')
        return
    if g.you_won:
        p.gold += g.pot
        st['won']['bones'] += 1
        game.msg(f'You win the pot of Bones: {g.pot}c.', 'good')
        _kind_word(game, 'bones')
    else:
        game.msg('The pot goes to ' + g.players[g.winner]['name'] + '.' if g.winner is not None else 'You leave the game.')


def count_hand(game, g, counting):
    """Settle one hand of The Count."""
    p = game.player
    st = state(game)
    game.end_turn(5)
    if g.result == 'win':
        p.gold += g.stake * 2
        st['won']['count'] += 1
        game.msg(f'You win the hand: {g.stake * 2}c back.', 'good')
        if counting:
            nt = [night(game), inn_key(game)]
            if st['counted'][0] != nt:
                st['counted'] = [nt, 0]
            st['counted'][1] += 1
            n = st['counted'][1]
            if n >= 3 and random.random() < .25 * (n - 2):
                bar(game, 'The dealer squares the deck and looks at you a long while. "You count, friend. '
                    'Not at my table."')
                return 'barred'
        if st['won']['count'] in (3, 10):
            _kind_word(game, 'count')
    elif g.result == 'push':
        p.gold += g.stake
    return None


def vigil_over(game, g, master=None):
    """Settle a game of Vigil: name only, and a master beaten."""
    from . import chronicle as CH
    st = state(game)
    game.end_turn(40)
    if g.winner == g.you:
        st['won']['vigil'] += 1
        s = settlement(game)
        if master and s is not None and s.id not in st['masters']:
            st['masters'].append(s.id)
            game.msg(f'You have beaten {master}, master of Vigil. The whole inn stands up to see the board.', 'good')
            s.rep += 2
            if all(sid in st['masters'] for sid in masters(game)):
                CH.deed(game, 'Keeper of the Vigil', f'Beat every master of Vigil in the land, the last of them {master} '
                        f'in {s.name}.')
                game.msg('You have beaten every master of Vigil in the land. They will call you the Keeper of the '
                         'Vigil.', 'good')
            else:
                left = len(masters(game)) - len([q for q in st['masters'] if q in masters(game)])
                game.msg(f'{master}: "There are {left} more who play as I do. Go and find them."', 'talk')
        else:
            game.msg('You win the game of Vigil.', 'good')
            _kind_word(game, 'vigil')
    elif g.winner == 'draw':
        game.msg('The night runs out before the game does. A draw.')
    else:
        game.msg('You lose the game of Vigil.')


def _kind_word(game, what):
    """Winning makes a little name: someone at the table tells you something."""
    regs = regulars(game)
    if not regs or random.random() < .5:
        return
    line = (rumour(game) if what == 'vigil' and random.random() < .5 else None) or game.rumor()
    game.say(regs[0], line)


def strength(game, master):
    if master:
        return 3
    s = settlement(game)
    return 2 if s is not None and s.kind in ('town', 'city', 'metropolis', 'deephold') else 1
