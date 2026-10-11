"""Things to find and things that happen out in the wilds: hidden places, travel events and
the travellers you meet on the road."""
import random

from . import data as D
from .data import ROAD, TOWN, CITY, ENTR, WATER, MOUNTAIN
from .worldgen import cheb

POI_LOOK = {
    'ruin': ('Π', (176, 166, 150)),
    'shrine': ('†', (150, 210, 255)),
    'camp': ('∆', (232, 92, 72)),
    'stones': ('Ψ', (196, 126, 255)),
    'wagon': ('¤', (204, 164, 104)),
}
POI_PLAN = {'ruin': 10, 'shrine': 7, 'camp': 9, 'stones': 6, 'wagon': 12}
RUIN_NAMES = ['Ruins of Kaer Mor', 'Collapsed Watchtower', 'Sunken Temple', 'Forgotten Barrow', 'Abandoned Mine',
              "Smugglers' Cave", 'Burned Manor', 'Drowned Chapel', 'Hollow Hill', "Witch's Cellar", 'Broken Abbey',
              'Old Wolf Den']
SHRINE_NAMES = ['Shrine of the Dawn', 'Wayside Shrine', 'Shrine of the Hunter', 'Mossy Shrine', 'Shrine of Saint Edda',
                'Weathered Shrine', 'Shrine of the Storm']
TRAVELLER_KINDS = [('pilgrim', (210, 200, 160)), ('hunter', (170, 200, 130)), ('peddler', (220, 180, 110)),
                   ('minstrel', (220, 150, 200)), ('farmhand', (190, 180, 150)), ('hedge knight', (200, 200, 220))]
CLIENT_NAMES = ['Edda', 'Hob', 'Maud', 'Corwin', 'Tamsin', 'Osric', 'Wenna', 'Garrick', 'Agnes', 'Alwin', 'Bess',
                'Dunstan', 'Elsa', 'Ivo', 'Jessamy', 'Leofric', 'Mabel', 'Rowan', 'Sabine']
RECIPIENTS = ['sister', 'brother', 'old mother', 'betrothed', 'business partner', 'son']


class POI:
    def __init__(self, pid, kind, x, y, name):
        self.id, self.kind, self.x, self.y, self.name = pid, kind, x, y, name
        self.found = False
        self.ready_day = 0          # 10**9 once used up
        self.did = None             # ruins: the dungeon behind them

    @property
    def glyph(self):
        return POI_LOOK[self.kind]


# ------------------------------------------------------------------ generation
def gen_pois(game, m, world):
    from .world import Dungeon
    w = m.w
    taken = [(s.x, s.y) for s in world.settlements] + [(h.x, h.y) for h in world.holds] + \
            [(d.x, d.y) for d in world.dungeons.values()]
    start = world.settlements[0]
    ruins = RUIN_NAMES[:]
    shrines = SHRINE_NAMES[:]
    random.shuffle(ruins)
    random.shuffle(shrines)
    n_ruin = 0
    for kind, count in POI_PLAN.items():
        placed = 0
        for _ in range(6000):
            if placed >= count:
                break
            x, y = random.randint(3, m.w - 4), random.randint(3, m.h - 4)
            t = m.tile(x, y)
            if not D.TILES[t].walk or t in (ROAD, TOWN, CITY, ENTR, D.CASTLE, D.FORT, D.RIVER):
                continue
            if world.road_dist[y * w + x] > 60:
                continue
            if any(cheb(x, y, a, b) < 5 for a, b in taken):
                continue
            rd = world.road_dist[y * w + x]
            if random.random() > min(1.0, .12 + rd / 14):
                continue
            if kind == 'camp' and (world.region_of[y * w + x] == 0 or cheb(x, y, start.x, start.y) < 14):
                continue
            if kind == 'ruin':
                name = ruins.pop() if ruins else f'Old Ruin {n_ruin}'
            elif kind == 'shrine':
                name = shrines.pop() if shrines else 'Wayside Shrine'
            else:
                name = {'camp': 'Bandit Camp', 'stones': 'Standing Stones', 'wagon': 'Abandoned Wagon'}[kind]
            poi = POI(len(world.pois), kind, x, y, name)
            if kind == 'ruin':
                danger = world.danger_at(x, y)
                style = random.choice(['cave', 'rooms'])
                tag = 'cave' if style == 'cave' else random.choice(['dungeon', 'crypt'])
                did = f'ruin{n_ruin}'
                wall = {'crypt': D.hexrgb('#7e869c'), 'dungeon': D.hexrgb('#a0835e')}.get(tag)
                dg = Dungeon(did, name, random.randint(1, 2), max(0, danger - 1), style, tag, None, wall, x, y, False)
                dg.poi = True
                world.dungeons[did] = dg
                poi.did = did
                n_ruin += 1
            world.pois.append(poi)
            taken.append((x, y))
            placed += 1


def poi_at(game, x, y):
    for poi in game.world.pois:
        if poi.x == x and poi.y == y:
            return poi
    return None


def discover(game):
    """Mark places you can see for the first time, with a little experience for the find."""
    w = game.world
    for poi in w.pois:
        if not poi.found and game.visible(poi.x, poi.y):
            poi.found = True
            xp = 3 + w.danger_at(poi.x, poi.y) * 2
            game.msg(f'You discover {poi.name}! (+{xp} experience)', 'gold')
            game.gain_xp(xp)


def reveal(game, poi):
    poi.found = True
    om = game.maps['over']
    om.seen[poi.y * om.w + poi.x] = 1


# ------------------------------------------------------------------ choices
def ask(game, key, title, text, options, **ctx):
    """Open a choice dialog. options: list of (label, choice_key)."""
    game.pending = dict(key=key, title=title, text=text, options=options, ctx=ctx)
    game.request = ('choice',)


def resolve(game, choice):
    ev = game.pending
    game.pending = None
    if not ev:
        return
    fn = RESOLVERS.get(ev['key'])
    if fn:
        fn(game, choice, ev['ctx'])


def on_poi(game, poi):
    if poi.kind == 'ruin':
        game.msg(f'{poi.name}. A way down leads into the dark. Press > to enter.', 'info')
        return
    if game.day < poi.ready_day:
        game.msg({'shrine': f'The {poi.name} is quiet. Its blessing will return in time.',
                  'camp': 'The burned-out remains of a bandit camp.',
                  'stones': 'The standing stones are silent now.',
                  'wagon': 'An empty, looted wagon.'}[poi.kind])
        return
    if poi.kind == 'shrine':
        opts = [('Pray and leave an offering of 25 gold', 'offer'), ('Pray without an offering', 'pray'), ('Walk on', 'leave')]
        if game.player.gold < 25:
            opts = opts[1:]
        ask(game, 'shrine', poi.name, 'An old shrine, its stone worn smooth by the hands of pilgrims. Candles still burn here.', opts, poi=poi.id)
    elif poi.kind == 'camp':
        ask(game, 'camp', 'Bandit Camp', 'Smoke rises from a ring of tents. You count at least five outlaws around the fire, '
            'and a strongbox under a tarp.', [('Attack the camp', 'attack'), ('Sneak away', 'leave')], poi=poi.id)
    elif poi.kind == 'stones':
        ask(game, 'stones', 'Standing Stones', 'A ring of tall grey stones hums faintly. Old runes crawl across them.',
            [('Lay your hands on the stones', 'touch'), ('Leave them be', 'leave')], poi=poi.id)
    elif poi.kind == 'wagon':
        ask(game, 'wagon', 'Abandoned Wagon', 'A wagon lies on its side, one wheel broken. No sign of the driver or the horses.',
            [('Search the wagon', 'search'), ('Leave it', 'leave')], poi=poi.id)


def _poi(game, ctx):
    return game.world.pois[ctx['poi']]


def r_shrine(game, choice, ctx):
    poi = _poi(game, ctx)
    p = game.player
    if choice == 'leave':
        return
    if choice == 'offer':
        p.gold -= 25
    poi.ready_day = game.day + 5
    if choice == 'pray' and random.random() < .2:
        p.buffs = [b for b in p.buffs if b[0] != 'dmg'] + [['dmg', -15, 300, 'Curse of Frailty']]
        game.msg('A cold wind snuffs the candles. You feel weaker. (Curse of Frailty: -15% damage)', 'bad')
        return
    blessing = random.choice([('dmg', 15, 'Blessing of Might', '+15% damage'), ('def', 20, 'Blessing of Stone', '+20 defense'),
                              ('regen', 2, 'Blessing of Life', '+2 life per turn'), ('heal', 0, 'Blessing of Mercy', 'fully healed')])
    k, v, name, txt = blessing
    if k == 'heal':
        s = game.stats()
        p.life, p.mana, p.poison = s['max_life'], s['max_mana'], None
    else:
        p.buffs = [b for b in p.buffs if b[0] != k] + [[k, v, 400 if choice == 'offer' else 250, name]]
    game.msg(f'Warmth fills you. {name}: {txt}.', 'good')


def r_camp(game, choice, ctx):
    poi = _poi(game, ctx)
    if choice != 'attack':
        return
    w = game.world
    lvl = w.danger_at(poi.x, poi.y) + 1
    keys = ['bandit'] + [random.choice(['bandit', 'brigand', 'raider']) for _ in range(random.randint(3, 5))]
    game.encounter_poi = poi.id
    game.start_encounter(None, game.maps['over'].tile(poi.x, poi.y), lvl, keys, 2 if random.random() < .5 else 1)
    chest(game, lvl, 2)


def chest(game, lvl, n):
    """Loot dropped in the middle of the current battle map."""
    from .entities import Item, random_gear
    m = game.map
    cx, cy = m.entry
    it = Item(game.new_id(), 'gold', 'gold', random.randint(lvl * 12, lvl * 30))
    game.spill(m, cx, cy - 2, it)
    for _ in range(n):
        g = random_gear(game, lvl, 2)
        game.spill(m, cx, cy - 2, g)


def r_stones(game, choice, ctx):
    poi = _poi(game, ctx)
    if choice != 'touch':
        return
    from . import skills as SK
    poi.ready_day = 10 ** 9
    line = random.choice(['fire', 'frost', 'storm', 'restoration', 'shadow', 'warcraft'])
    game.msg(f"Visions of old battles flood your mind. Your {SK.DISCIPLINES[line]['name']} grows.", 'gold')
    SK.gain(game, line, 30)
    if random.random() < .6:
        from .entities import make_tome
        t = make_tome(game, game.world.danger_at(poi.x, poi.y) * 2, line)
        if game.add_to_inv(t):
            game.msg(f'When the visions fade, the words of a spell remain. You write them down: {t.display_name()}.', 'gold')
    game.gain_xp(20 + game.world.danger_at(poi.x, poi.y) * 10)


def r_wagon(game, choice, ctx):
    poi = _poi(game, ctx)
    if choice != 'search':
        return
    poi.ready_day = 10 ** 9
    loot_or_ambush(game, poi.x, poi.y)


def loot_or_ambush(game, x, y):
    from .entities import Item, random_gear
    w = game.world
    lvl = w.danger_at(x, y)
    p = game.player
    if random.random() < .6:
        gold = random.randint(6, 18) * lvl
        p.gold += gold
        found = [f'{gold} gold']
        if random.random() < .5:
            game.add_to_inv(Item(game.new_id(), 'potion', random.choice(['hp', 'hp', 'mp'])))
            found.append('a potion')
        if random.random() < .35:
            g = random_gear(game, lvl, 2)
            if game.add_to_inv(g):
                found.append(g.name)
        game.msg('You find ' + ', '.join(found) + '.', 'gold')
    else:
        game.msg('It was bait. Figures rise from the grass around you!', 'bad')
        keys = [random.choice(['bandit', 'brigand']) for _ in range(random.randint(2, 4))]
        game.start_encounter(None, game.maps['over'].tile(x, y), lvl, keys)


# ------------------------------------------------------------------ travel events
def maybe_event(game, on_road):
    if random.random() >= (.006 if on_road else .013):
        return False
    from .towns import is_night
    p = game.player
    night = is_night(game)
    cands = [('hurt', 3), ('peddler', 2), ('pilgrims', 2 if on_road else 0), ('tracks', 0 if on_road else 3),
             ('lights', 3 if night and not on_road else 0), ('storm', 1), ('cart', 2),
             ('toll', 2 if on_road and game.world.region_at(p.x, p.y).danger >= 2 else 0)]
    cands = [(k, wgt) for k, wgt in cands if wgt]
    key = random.choices([k for k, _ in cands], [wgt for _, wgt in cands])[0]
    EVENTS[key](game)
    return True


def e_hurt(game):
    opts = [('Give him a health potion', 'potion')] if game.count('potion', 'hp') else []
    opts += [('Go through his pack', 'rob'), ('Leave him', 'leave')]
    ask(game, 'hurt', 'A wounded traveller', 'A man lies groaning by the wayside, an arrow in his leg. "Please... anything..."', opts)


def r_hurt(game, choice, ctx):
    from .war import change_rep
    p = game.player
    f = game.world.region_at(p.x, p.y).faction
    if choice == 'potion':
        it = next(i for i in p.inv if i.k == 'potion' and i.t == 'hp')
        game.remove_one(it)
        change_rep(game, f, 3)
        if random.random() < .5:
            g = random.randint(20, 70)
            p.gold += g
            game.msg(f'"Bless you." He presses {g} gold into your hand.', 'good')
        else:
            hidden = [poi for poi in game.world.pois if not poi.found and poi.kind == 'ruin']
            if hidden:
                poi = min(hidden, key=lambda q: cheb(q.x, q.y, p.x, p.y))
                reveal(game, poi)
                game.msg(f'"I have no coin, but I know of a place: {poi.name}." He marks it on your map.', 'good')
            else:
                game.msg('"Bless you, stranger." He limps off toward the road.', 'good')
        game.gain_xp(15)
    elif choice == 'rob':
        g = random.randint(10, 40)
        p.gold += g
        change_rep(game, f, -6)
        game.msg(f'You take {g} gold from the dying man. Word of this will spread.', 'bad')


def e_peddler(game):
    from .entities import random_gear, make_gear, make_tome
    lvl = max(1, game.player.lvl)
    if random.random() < .4:
        it = make_tome(game, lvl + 2)
        price = round(it.value() * 1.3)
        what = f'the {it.display_name()}'
        lines = it.lines()[1]
    else:
        it = random_gear(game, lvl + 1, 3)
        if it.rar == 'normal':
            it = make_gear(game, it.base, 'magic', lvl + 1)
        it.ided = True
        it.curse = []
        price = round(it.value() * 1.2)
        what = it.name
        lines = ' · '.join(it.lines()[:3])
    opts = [(f'Buy it for {price} gold', 'buy')] if game.player.gold >= price else []
    opts.append(('No thanks', 'leave'))
    ask(game, 'peddler', 'A wandering peddler', f'A peddler with a laden mule waves you over. "Something special for you, '
        f'friend: {what}." ({lines})', opts, item=it, price=price)


def r_peddler(game, choice, ctx):
    if choice != 'buy':
        return
    it, price = ctx['item'], ctx['price']
    if game.add_to_inv(it):
        game.player.gold -= price
        game.msg(f'You buy {it.display_name()}.', it.rar)
    else:
        game.msg('Your bag is full.', 'bad')


def e_pilgrims(game):
    ask(game, 'pilgrims', 'Pilgrims on the road', 'A band of pilgrims shares bread and stories with you by the roadside.',
        [('Rest with them a while', 'rest')])


def r_pilgrims(game, choice, ctx):
    p = game.player
    s = game.stats()
    p.life = min(s['max_life'], p.life + s['max_life'] // 3)
    hidden = [poi for poi in game.world.pois if not poi.found]
    if hidden:
        poi = random.choice(hidden)
        reveal(game, poi)
        game.msg(f'They speak of {poi.name}, and show you where it lies.', 'info')
    game.end_turn(20, True)


def e_tracks(game):
    ask(game, 'tracks', 'Fresh tracks', 'Huge paw prints in the mud, still filling with water. Whatever made them is close.',
        [('Follow the tracks', 'follow'), ('Steer well clear', 'leave')])


def r_tracks(game, choice, ctx):
    if choice != 'follow':
        return
    from .wanderers import wild_pack
    p = game.player
    w = game.world
    lvl = w.danger_at(p.x, p.y) + 1
    keys = wild_pack(w.region_at(p.x, p.y).biome, lvl)
    game.start_encounter(None, game.maps['over'].tile(p.x, p.y), lvl, keys, 2)
    chest(game, lvl, 1)


def e_lights(game):
    ask(game, 'lights', 'Lights in the dark', 'Pale lights drift between the trees, just out of reach, as if leading the way.',
        [('Follow the lights', 'follow'), ('Look away and keep walking', 'leave')])


def r_lights(game, choice, ctx):
    if choice != 'follow':
        return
    p = game.player
    hidden = [poi for poi in game.world.pois if not poi.found and poi.kind == 'ruin']
    if hidden and random.random() < .55:
        poi = min(hidden, key=lambda q: cheb(q.x, q.y, p.x, p.y))
        reveal(game, poi)
        game.msg(f'The lights lead you to the edge of {poi.name} before they wink out. It is on your map now.', 'gold')
    else:
        game.msg('The lights gather into shapes. Cold, hungry shapes.', 'bad')
        lvl = game.world.danger_at(p.x, p.y) + 1
        game.start_encounter(None, game.maps['over'].tile(p.x, p.y), lvl, ['ghost'] * random.randint(2, 3) + ['wraith'])


def e_storm(game):
    ask(game, 'storm', 'A storm breaks', 'Thunder rolls over the land and rain comes down in sheets. You find what shelter you can.',
        [('Wait it out', 'wait')])


def r_storm(game, choice, ctx):
    game.end_turn(60, True)
    game.msg('The storm passes. Hours have gone by.')


def e_cart(game):
    ask(game, 'cart', 'An overturned cart', 'A merchant cart lies overturned in the ditch, its cargo scattered.',
        [('Search the wreck', 'search'), ('Keep moving', 'leave')])


def r_cart(game, choice, ctx):
    if choice == 'search':
        p = game.player
        loot_or_ambush(game, p.x, p.y)


def e_toll(game):
    p = game.player
    fee = 15 * game.world.danger_at(p.x, p.y)
    opts = [(f'Pay {fee} gold', 'pay')] if p.gold >= fee else []
    opts += [('Draw your weapon', 'fight'), ('Try to run', 'run')]
    bh = D.FACTIONS['blackhand']['name']
    ask(game, 'toll', 'A toll on the road', f'Armed men step onto the road. "Toll for {bh}. {fee} gold, or blood."', opts, fee=fee)


def r_toll(game, choice, ctx):
    from .war import change_rep
    p = game.player
    if choice == 'pay':
        p.gold -= ctx['fee']
        change_rep(game, 'blackhand', 2, quiet=True)
        game.msg('They count the coins and let you pass.', 'info')
        return
    if choice == 'run' and random.random() < .5:
        game.msg('You slip past them into the brush.', 'good')
        return
    lvl = game.world.danger_at(p.x, p.y) + 1
    keys = [random.choice(['raider', 'raider', 'brigand']) for _ in range(random.randint(3, 4))]
    game.start_encounter(None, game.maps['over'].tile(p.x, p.y), lvl, keys, 0)
    for o in game.map.mons:
        if not o.is_npc:
            o.faction = 'blackhand'


EVENTS = {'hurt': e_hurt, 'peddler': e_peddler, 'pilgrims': e_pilgrims, 'tracks': e_tracks, 'lights': e_lights,
          'storm': e_storm, 'cart': e_cart, 'toll': e_toll}


# ------------------------------------------------------------------ travellers
def spawn_traveller(game):
    from .wanderers import Wanderer, road_path
    w = game.world
    a, b = random.sample(w.settlements, 2)
    path = road_path(game, a.id, b.id)
    if not path or len(path) < 15:
        return
    kind, fg = random.choice(TRAVELLER_KINDS)
    name = random.choice(CLIENT_NAMES)
    i = random.randint(0, len(path) // 2)
    x, y = path[i]
    from .wanderers import wanderer_at
    if (game.cur == 'over' and (x, y) == (game.player.x, game.player.y)) or wanderer_at(game, x, y):
        return
    wd = Wanderer(game.new_id(), 'traveler', x, y)
    wd.ch, wd.fg = '@', fg
    wd.name = f'{name} the {kind}'
    wd.origin, wd.dest = a.id, b.id
    wd.path = list(path)
    wd.path_i = i + 1 if i else 0
    wd.speed = 13
    wd.offer = make_personal_offer(game, wd) if random.random() < .65 else None
    w.wanderers.append(wd)


def make_personal_offer(game, wd):
    w = game.world
    dest = w.settlements[wd.dest]
    sub = random.choice(['letter', 'gather', 'hunt', 'rescue'])
    data = dict(sub=sub, client=wd.name, wait=dest.id)
    if sub == 'letter':
        others = [s for s in w.settlements if s.id not in (wd.dest, wd.origin)]
        rs = random.choice(others)
        who = random.choice(RECIPIENTS)
        data.update(recipient=f"{random.choice(CLIENT_NAMES)}, {wd.name.split()[0]}'s {who}", rtown=rs.id,
                    reward=random.randint(40, 90))
    elif sub == 'gather':
        g = random.choice(['herbs', 'furs', 'salt', 'cloth', 'fish', 'ale', 'medicine'])
        q = max(3, min(10, round(random.uniform(60, 140) / D.GOODS[g]['base'])))
        data.update(good=g, qty=q, reward=round(D.GOODS[g]['base'] * q * 1.8 + 30))
    elif sub == 'hunt':
        data.update(reward=random.randint(90, 160))
    else:
        ruins = [p for p in w.pois if p.kind == 'ruin' and w.dungeons[p.did].relic is None]
        if not ruins:
            return None
        poi = min(ruins, key=lambda q: cheb(q.x, q.y, wd.x, wd.y))
        data.update(ruin=poi.id, dungeon=poi.did, relic=random.choice(['a silver locket', 'my father\'s sword',
                                                                       'a family bible', 'a carved wooden horse']),
                    reward=random.randint(120, 220))
    return data


def talk_traveller(game, wd):
    opts = [('Ask for news', 'news')]
    if getattr(wd, 'offer', None):
        opts.append(('Ask if they need help', 'help'))
    opts.append(('Farewell', 'leave'))
    wd.wait = 4
    dest = game.world.settlements[wd.dest].name
    ask(game, 'traveller', wd.name, f'"Well met. I am on my way to {dest}." {wd.name.split()[0]} leans on a walking staff.',
        opts, wd=wd.id)


def _wd(game, ctx):
    return next((x for x in game.world.wanderers if x.id == ctx['wd']), None)


def r_traveller(game, choice, ctx):
    wd = _wd(game, ctx)
    if not wd:
        return
    if choice == 'news':
        game.say_text(wd.name, game.rumor())
    elif choice == 'help' and wd.offer:
        o = wd.offer
        first = wd.name.split()[0]
        town = game.world.settlements[o['wait']].name
        if o['sub'] == 'letter':
            rt = game.world.settlements[o['rtown']].name
            text = (f'"Would you carry a letter for me? It must reach {o["recipient"]} at the inn in {rt}. '
                    f'They will pay you {o["reward"]} gold when it arrives."')
        elif o['sub'] == 'gather':
            text = (f'"I need {o["qty"]} {D.GOODS[o["good"]]["name"].lower()} and I am short on time. Bring them to me at the inn '
                    f'in {town} and I will pay {o["reward"]} gold."')
        elif o['sub'] == 'hunt':
            text = (f'"A beast has been stalking me since the hills, a big one. Kill it and find me at the inn in {town}. '
                    f'{o["reward"]} gold is yours."')
        else:
            poi = game.world.pois[o['ruin']]
            text = (f'"Robbers took {o["relic"]} and fled into {poi.name}. Bring it back to me at the inn in {town}, '
                    f'and {o["reward"]} gold is yours."')
        ask(game, 'traveller_job', wd.name, text + f' ({first} will wait at the inn in {town}.)',
            [('Agree to help', 'accept'), ('Not now', 'leave')], wd=wd.id)


def r_traveller_job(game, choice, ctx):
    wd = _wd(game, ctx)
    if not wd or choice != 'accept' or not wd.offer:
        return
    from . import missions as MS
    if MS.accept_personal(game, wd, wd.offer):
        wd.offer = None


RESOLVERS = {'shrine': r_shrine, 'camp': r_camp, 'stones': r_stones, 'wagon': r_wagon, 'hurt': r_hurt,
             'peddler': r_peddler, 'pilgrims': r_pilgrims, 'tracks': r_tracks, 'lights': r_lights, 'storm': r_storm,
             'cart': r_cart, 'toll': r_toll, 'traveller': r_traveller, 'traveller_job': r_traveller_job}
