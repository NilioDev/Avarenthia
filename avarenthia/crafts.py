"""The crafts of making: Smithing (an anvil: ore becomes bars; metal arms, metal armour and tools; mending your metal
gear; honing a blade), Tailoring and Leatherworking (the workbench: cloth pieces, warm or cool; leather pieces; bandages,
rope, a fishing net). The materials come in tiers like everything else in the life skills: better ore lies deeper and in
harder land, better cloth further out, better hides on stronger beasts. The tier sets the grade of what you make
(A-B normal, C-D exceptional, E and the top elite) and the material adds its own property.

What you make has a quality: crude, fine or masterwork, by your rank against the work's.

A material is Item('mat', key, n): ores 'ore_<metal>', bars 'bar_<metal>', cloth 'cloth_<cloth>'. Iron ore is the
trade good 'ore' on your cart; leather stays Item('leather', <kind>) from the tanner (hunting.py)."""
import random

from . import data as D
from . import lifeskills as LS

# metal: name, tier, rank, property (see props)
METALS = {
    'iron': ('Iron', 'A', 0), 'bog': ('Bog Iron', 'B', 5), 'silver': ('Silver', 'B', 10),
    'deepiron': ('Deepiron', 'C', 20), 'bloodstone': ('Bloodstone', 'C', 22), 'frostvein': ('Frostvein', 'C', 24),
    'blackiron': ('Blackiron', 'D', 30), 'moonsilver': ('Moonsilver', 'D', 32), 'sunstone': ('Sunstone', 'D', 34),
    'adamant': ('Adamant', 'E', 40), 'wyrmstone': ('Wyrmstone', 'E', 44), 'star': ('Star-iron', 'T', 45),
}
ORE_NAME = {'iron': 'Iron Ore', 'bog': 'Bog Iron', 'silver': 'Silver Ore', 'deepiron': 'Deepiron Ore',
            'bloodstone': 'Bloodstone', 'frostvein': 'Frostvein Ore', 'blackiron': 'Blackiron Ore',
            'moonsilver': 'Moonsilver Ore', 'sunstone': 'Sunstone', 'adamant': 'Adamant Ore', 'wyrmstone': 'Wyrmstone',
            'star': 'Star-iron'}
# cloth: name, tier, rank, where you buy or find it
CLOTHS = {
    'linen': ('Linen', 'A', 0), 'wool': ('Wool', 'A', 0), 'hemp': ('Hemp Cloth', 'A', 3),
    'felt': ('Felt', 'B', 10), 'cotton': ('Cotton', 'B', 12), 'mohair': ('Mohair', 'B', 14),
    'spidersilk': ('Spider Silk', 'C', 20), 'highland': ('Highland Wool', 'C', 22), 'sandsilk': ('Sandsilk', 'C', 24),
    'shadowsilk': ('Shadowsilk', 'D', 30), 'mammoth': ('Mammoth Wool', 'D', 32), 'seasilk': ('Seasilk', 'D', 34),
    'queensilk': ("Queen's Silk", 'E', 40), 'emberthread': ('Emberthread', 'E', 44), 'feysilk': ('Fey Silk', 'T', 45),
}
# leather: name, tier, rank (the kind a tanned hide becomes: hunting.LEATHER_OF)
LEATHERS = {
    'leather': ('Leather', 'A', 0), 'sturdy': ('Sturdy Leather', 'B', 10), 'fur': ('Warm Fur', 'B', 10),
    'snake': ('Snakeskin', 'B', 12), 'thick': ('Thick Hide', 'C', 20), 'bearfur': ('Bear Fur', 'C', 22),
    'panther': ('Panther Pelt', 'C', 24), 'croc': ('Crocodile Hide', 'C', 25), 'cavefur': ('Cave Fur', 'D', 30),
    'sabre': ('Sabretooth Pelt', 'D', 32), 'mammothhide': ('Mammoth Hide', 'D', 34), 'rhino': ('Rhino Hide', 'D', 35),
    'drake': ('Drake Hide', 'E', 40),
}
GRADE_OF = {'A': 0, 'B': 0, 'C': 1, 'D': 1, 'E': 2, 'T': 2}
TIER_VAL = {'A': 1, 'B': 2, 'C': 4, 'D': 7, 'E': 12, 'T': 20}

# what each craft makes: key -> (name, family or tool, materials, rank)
SMITH = {
    'dagger': ('Dagger', 'dagger', 1, 0), 'shortsword': ('Short Sword', 'shortsword', 2, 0), 'spear': ('Spear', 'spear', 2, 2),
    'scimitar': ('Scimitar', 'scimitar', 2, 3), 'longsword': ('Long Sword', 'longsword', 3, 4), 'mace': ('Flanged Mace', 'mace', 3, 5),
    'flail': ('Flail', 'flail', 3, 6), 'greatsword': ('Greatsword', 'greatsword', 5, 6), 'scythe': ('War Scythe', 'scythe', 4, 6),
    'waraxe': ('War Axe', 'waraxe', 3, 7), 'halberd': ('Halberd', 'halberd', 5, 8), 'warhammer': ('War Hammer', 'warhammer', 4, 9),
    'greataxe': ('Great Axe', 'greataxe', 5, 9), 'bastard': ('Bastard Sword', 'bastard', 4, 10), 'maul': ('Maul', 'maul', 6, 12),
    'runeblade': ('Rune Blade', 'runeblade', 4, 13), 'throwknives': ('Throwing Knives', 'throwknives', 1, 2),
    'lightxbow': ('Light Crossbow', 'lightxbow', 3, 3), 'heavyxbow': ('Heavy Crossbow', 'heavyxbow', 5, 9),
    'cestus': ('Cestus', 'cestus', 1, 2), 'claws': ('Tiger Claws', 'claws', 1, 4),
    'buckler': ('Buckler', 'buckler', 2, 1), 'roundshield': ('Round Shield', 'roundshield', 3, 4),
    'kiteshield': ('Kite Shield', 'kiteshield', 4, 8), 'towershield': ('Tower Shield', 'towershield', 5, 12),
    'skullcap': ('Skull Cap', 'skullcap', 2, 4), 'fullhelm': ('Full Helm', 'fullhelm', 3, 8), 'greathelm': ('Great Helm', 'greathelm', 4, 12),
    'ringmail': ('Ring Mail', 'ringmail', 4, 5), 'chainmail': ('Chain Mail', 'chainmail', 5, 8), 'platemail': ('Plate Mail', 'platemail', 7, 12),
    'hgloves': ('Heavy Gloves', 'hgloves', 2, 4), 'gauntlets': ('Gauntlets', 'gauntlets', 2, 10),
    'platedbelt': ('Plated Belt', 'platedbelt', 2, 10), 'hboots': ('Heavy Boots', 'hboots', 2, 4), 'greaves': ('Greaves', 'greaves', 3, 10),
    'pick': ("Miner's Pick", 'tool:pick', 2, 0), 'knife': ('Skinning Knife', 'tool:knife', 1, 0),
    'hooks': ('Fish Hooks', 'tool:hooks', 1, 3), 'mailbarding': ('Mail Barding', 'tool:barding', 5, 15),
}
TAILOR = {
    'quilted': ('Quilted Armor', 'quilted', 3, 1), 'robe': ('Robe', 'robe', 4, 2), 'cap': ('Cap', 'cap', 1, 1),
    'hood': ('Hood', 'hood', 2, 2), 'sash': ('Sash', 'sash', 1, 1), 'wraps': ('Wraps', 'wraps', 1, 2),
    'softshoes': ('Soft Shoes', 'softshoes', 2, 1),
    'bandages': ('Bandages', 'tool:bandage', 1, 0), 'rope': ('Rope', 'tool:rope', 2, 3), 'net': ('Fishing Net', 'tool:net', 3, 5),
}
LEATHERWORK = {
    'leather': ('Leather Armor', 'leather', 4, 3), 'gloves': ('Leather Gloves', 'gloves', 1, 1),
    'boots': ('Boots', 'boots', 2, 1), 'belt': ('Belt', 'belt', 1, 5), 'waterskin': ('Waterskin', 'tool:waterskin', 1, 0),
    'bedroll': ('Bedroll', 'tool:bedroll', 2, 2), 'marshboots': ('Marsh Boots', 'boots', 3, 6),
    'sandboots': ('Sand Boots', 'boots', 3, 8), 'tent': ('Tent', 'tool:tent', 5, 8), 'snowboots': ('Snow Boots', 'boots', 3, 10),
    'barding': ('Light Barding', 'tool:barding', 4, 12), 'mountainboots': ('Mountain Boots', 'boots', 3, 12),
}
# boots for the road: travel over that land is quicker (engine: the world map's step)
ROAD = {'marshboots': 'marsh', 'sandboots': 'sand', 'snowboots': 'snow', 'mountainboots': 'mountain'}
ROAD_TILES = {'marsh': (D.SWAMP,), 'sand': (D.SAND,), 'snow': (D.SNOW,), 'mountain': (D.HILLS, D.MOUNTAIN)}
CRAFT_OF = {'smithing': SMITH, 'tailoring': TAILOR, 'leatherworking': LEATHERWORK}
STUFF = {'smithing': METALS, 'tailoring': CLOTHS, 'leatherworking': LEATHERS}
QUALITY = {'crude': .85, 'fine': 1.0, 'masterwork': 1.15}
BENCH_FEE = 20


def road_boots(game, t):
    """Boots for the road: over their own land a step on the world map costs a quarter less."""
    b = game.eq_item('boots')
    road = getattr(b, 'road', None) if b else None
    if road and t in ROAD_TILES[road] and not (getattr(b, 'mdur', 0) and b.dur <= 0):
        return .75
    if road == 'snow':
        from . import seasons as SE
        m, p = game.map, game.player
        if m.kind == 'over' and SE.snowy(m, p.y * m.w + p.x, SE.Now(game)):
            return .75
    return 1
ANVIL_FEE = 30


# ------------------------------------------------------------------ materials
def mat_name(key):
    kind, m = key.split('_', 1)
    if kind == 'ore':
        return ORE_NAME[m]
    if kind == 'bar':
        return f'{METALS[m][0]} Bar'
    return f'Bolt of {CLOTHS[m][0]}'


def tier_of(key):
    kind, m = key.split('_', 1)
    return (CLOTHS if kind == 'cloth' else METALS)[m][1]


def make_mat(game, key, n=1):
    from .entities import Item
    it = Item(game.new_id(), 'mat', key, n)
    it.name = mat_name(key)
    return it


def give(game, key, n=1):
    it = make_mat(game, key, n)
    if not game.add_to_inv(it):
        game.spill(game.map, game.player.x, game.player.y, it)


def count(game, key):
    if key == 'ore_iron':
        return game.player.cargo.get('ore', 0) + sum(i.n for i in game.player.inv if i.k == 'mat' and i.t == key)
    if key == 'ore_star':
        return sum(i.n for i in game.player.inv if i.k == 'star')
    if key.startswith('leather:'):
        return sum(i.n for i in game.player.inv if i.k == 'leather' and i.t == key[8:])
    return sum(i.n for i in game.player.inv if i.k == 'mat' and i.t == key)


def take(game, key, n):
    p = game.player
    if key == 'ore_iron':
        for it in [i for i in p.inv if i.k == 'mat' and i.t == key]:
            while n > 0 and it in p.inv:
                game.remove_one(it)
                n -= 1
        if n > 0:
            p.cargo['ore'] = p.cargo.get('ore', 0) - n
            if p.cargo['ore'] <= 0:
                p.cargo.pop('ore')
        return
    kind, t = ('star', None) if key == 'ore_star' else ('leather', key[8:]) if key.startswith('leather:') else ('mat', key)
    for it in [i for i in p.inv if i.k == kind and (t is None or i.t == t)]:
        while n > 0 and it in p.inv:
            game.remove_one(it)
            n -= 1


def stuff_key(craft, m):
    return {'smithing': 'bar_', 'tailoring': 'cloth_', 'leatherworking': 'leather:'}[craft] + m


# ------------------------------------------------------------------ mining: what a vein holds
def vein(game, x, y):
    """The metal of an ore vein, decided when you first strike it: deeper, harder land holds better ore."""
    m = game.map
    veins = m.__dict__.setdefault('veins', {})
    if (x, y) in veins:
        return veins[(x, y)]
    from . import cooking as CK
    lands = set(CK.here_lands(game)) | {CK.here_biome(game)}
    depth = (getattr(m, 'depth', 0) or 0) if m.kind == 'dungeon' else 0
    danger = LS.place_danger(game)
    from .weather import climate
    wx, wy = game.world_pos()
    cold = game.maps['over'].inb(wx, wy) and climate(game.world, game.world.region_at(wx, wy).id) == 'cold'
    can = {
        'bog': 'marsh' in lands, 'silver': 'mountain' in lands or depth >= 2, 'deepiron': depth >= 4,
        'bloodstone': 'canyon' in lands, 'frostvein': 'mountain' in lands and cold or bool(lands & {'peak', 'alpine'}),
        'blackiron': 'mountain' in lands or getattr(m, 'tribe', None) in ('orcs', 'warcamp'), 'moonsilver': 'karst' in lands,
        'sunstone': 'desert' in lands, 'adamant': depth >= 6, 'wyrmstone': 'canyon' in lands or 'mountain' in lands,
    }
    cands = [k for k, ok in can.items() if ok and danger >= LS.TIER_DANGER[METALS[k][1]]]
    metal = 'iron'
    if cands and random.random() < .55:
        metal = random.choices(cands, [1 + LS.TIER_RANK[METALS[k][1]] / 10 for k in cands])[0]
    veins[(x, y)] = metal
    return metal


def dig_vein(game, x, y):
    """The metal you get out of an ore vein: None if it is too hard for you yet (the vein stays)."""
    metal = vein(game, x, y)
    r = LS.rank(game, 'mining')
    at = METALS[metal][2]
    if at > r:
        LS.too_hard(game, 'mining', at, f'A vein of {ORE_NAME[metal].lower()}')
        return None
    return metal


# ------------------------------------------------------------------ the anvil
def anvil(game):
    """Walking into an anvil: smelt, forge, mend or hone."""
    from . import events as EV
    from .money import fmt
    opts = []
    if smeltable(game):
        opts.append(('Smelt ore into bars', 'smelt'))
    opts.append(('Forge something', 'forge'))
    if worn(game, 'smithing'):
        opts.append(('Mend metal gear, yours or your company\'s', 'mend'))
    if game.eq_item('weapon'):
        opts.append(('Hone your blade', 'hone'))
    extra(game, 'smithing', opts)
    opts.append(('Leave', 'leave'))
    r = LS.rank(game, 'smithing')
    fee = fee_here(game, ANVIL_FEE)
    EV.ask(game, 'anvil', 'The anvil', 'Hammer, tongs and a forge that is still warm.' +
           (f' The use of the forge costs {fmt(fee)}.' if fee else '') + (f'\n\nSmithing {r}.' if r else ''), opts)


def fee_here(game, fee):
    """In a town the smith or the tanner wants paying for the use of the forge or the bench; in the wild it is free."""
    return fee if game.map.kind == 'town' else 0


def pay(game, fee):
    p = game.player
    fee = fee_here(game, fee)
    if p.gold < fee:
        from .money import fmt
        game.msg(f'The use of it costs {fmt(fee)}. You cannot pay.', 'bad')
        return False
    p.gold -= fee
    return True


def smeltable(game):
    return [m for m in METALS if count(game, 'ore_' + m) >= (1 if m == 'star' else 2)]


def worn(game, craft='smithing'):
    """Worn gear of this craft's kind: yours, and your hireling's."""
    from . import mercs as MC
    mc = MC.get(game)
    gear = list(game.player.inv) + ([g for g in mc.gear.values() if g] if mc else [])
    return [i for i in gear if i.k == 'gear' and getattr(i, 'mdur', 0) and i.dur < i.mdur and craft_of(i) == craft]


def craft_of(it):
    """Which craft mends this piece: metal at the anvil, leather and cloth at the bench."""
    fam = D.BASES[it.base].get('family', it.base)
    for craft, table in CRAFT_OF.items():
        if any(v[1] == fam for v in table.values()):
            return craft
    return None


def metal_gear(it):
    return craft_of(it) == 'smithing'


def extra(game, craft, opts):
    """What a skilled hand may also do at the anvil or the bench: mend for the townsfolk, and from rank 40 Unmake."""
    if game.map.kind == 'town' and LS.rank(game, craft) >= 5 and \
            game.player.__dict__.get('mended_for', {}).get(craft) != (getattr(game.map, 'sid', None), game.day):
        opts.append(('Mend for the townsfolk, for a few coins', f'others:{craft}'))
    if LS.rank(game, craft) >= 40 and unmake_pairs(game, craft):
        opts.append(('Unmake a found piece onto your own work', f'unmake:{craft}'))


def r_anvil(game, choice, ctx):
    from . import events as EV
    if choice == 'smelt':
        ms = smeltable(game)
        opts = [(f'{METALS[m][0]}: ' + ('1 star-iron' if m == 'star' else f'2 {ORE_NAME[m].lower()}') + f' (you have {count(game, "ore_" + m)})',
                 f'smelt:{m}') for m in ms] + [('Never mind', 'leave')]
        EV.ask(game, 'anvil_do', 'Smelting', 'Which ore goes in the forge?', opts)
    elif choice == 'forge':
        pick_item(game, 'smithing')
    elif choice == 'mend':
        opts = [(f'{i.display_name()} ({i.dur}/{i.mdur}): one bar or one load of ore', f'mend:{i.id}') for i in worn(game)][:16]
        EV.ask(game, 'anvil_do', 'Mending', 'Which piece goes on the anvil?', opts + [('Never mind', 'leave')])
    elif choice == 'hone':
        hone(game)
    else:
        r_extra(game, choice)


def r_extra(game, choice):
    if not choice:
        return
    if choice.startswith('others:'):
        mend_others(game, choice[7:])
    elif choice.startswith('unmake:'):
        unmake_menu(game, choice[7:])


def r_anvil_do(game, choice, ctx):
    if not choice or choice == 'leave':
        return
    if choice.startswith('smelt:'):
        smelt(game, choice[6:])
    elif choice.startswith('mend:'):
        mend(game, int(choice[5:]))
    elif choice.startswith('bmend:'):
        mend(game, int(choice[6:]), 'bench')
    elif choice.startswith('road:'):
        mend(game, int(choice[5:]), 'road')


def smelt(game, m):
    need = 1 if m == 'star' else 2
    if count(game, 'ore_' + m) < need or not pay(game, ANVIL_FEE):
        return
    at = METALS[m][2]
    if at > LS.rank(game, 'smithing'):
        LS.too_hard(game, 'smithing', at, ORE_NAME[m])
        return
    take(game, 'ore_' + m, need)
    give(game, 'bar_' + m, 1)
    game.msg(f'The ore runs white in the crucible. You pour a {METALS[m][0].lower()} bar.', 'good')
    LS.gain(game, 'smithing', 1 + at / 10, at=at)
    game.end_turn(30)


def mend_stuff(craft):
    """What mending a piece of this craft takes, best last."""
    if craft == 'smithing':
        return ['ore_iron'] + ['bar_' + m for m in METALS]
    if craft == 'tailoring':
        return ['cloth_' + m for m in CLOTHS]
    return ['leather:' + m for m in LEATHERS]


def mend(game, iid, where='anvil'):
    it = next((i for i in worn(game, 'smithing') + worn(game, 'tailoring') + worn(game, 'leatherworking') if i.id == iid),
              None)
    if not it:
        return
    craft = craft_of(it)
    use = next((k for k in mend_stuff(craft) if count(game, k)), None)
    if not use:
        game.msg({'smithing': 'Mending wants one bar of metal, or one load of iron ore.',
                  'tailoring': 'Mending wants one bolt of cloth.', 'leatherworking': 'Mending wants one piece of leather.'}[craft],
                 'bad')
        return
    if where in ('anvil', 'bench') and not pay(game, (ANVIL_FEE if where == 'anvil' else BENCH_FEE) // 2):
        return
    take(game, use, 1)
    it.dur = it.mdur
    game.msg({'smithing': f'You hammer out the dents and rivet what was loose: {it.display_name()} is whole again.',
              'tailoring': f'You patch and darn {it.display_name()}. It is whole again.',
              'leatherworking': f'You stitch and oil {it.display_name()}. It is whole again.'}[craft], 'good')
    from . import mercs as MC
    mc = MC.get(game)
    if mc and it in mc.gear.values():
        MC.refresh_body(game, mc)
    LS.gain(game, craft, 1, at=D.BASES[it.base]['lvl'])
    game.end_turn(40 if where != 'road' else 60)


def mend_others(game, craft):
    """In a town: a morning's mending for the townsfolk. It pays little, and it teaches at your own height."""
    from .money import fmt
    p = game.player
    p.__dict__.setdefault('mended_for', {})[craft] = (getattr(game.map, 'sid', None), game.day)
    r = LS.rank(game, craft)
    coins = 40 + r * 6
    p.gold += coins
    what = {'smithing': 'a ploughshare, two hinges and a cauldron that leaked', 'tailoring': 'a heap of shirts and a torn sail',
            'leatherworking': 'a harness, a saddle and three pairs of boots'}[craft]
    game.msg(f'You spend the morning on {what}. The townsfolk pay you {fmt(coins)}.', 'good')
    LS.gain(game, craft, 3 + r / 10, at=r)
    game.end_turn(120)


def hone(game):
    w = game.eq_item('weapon')
    if not w:
        return
    p = game.player
    p.buffs = [b for b in p.buffs if b[0] != 'honed'] + [['honed', 6 + LS.rank(game, 'smithing') // 5, 300, 'A honed edge']]
    game.msg(f'You take the {w.name} to the whetstone. The edge comes up bright and keen.', 'good')
    LS.gain(game, 'smithing', .3)
    game.end_turn(15)


# ------------------------------------------------------------------ the workbench: leather and cloth
def bench(game):
    from . import events as EV
    from .money import fmt
    rl, rt = LS.rank(game, 'leatherworking'), LS.rank(game, 'tailoring')
    opts = [('Leatherwork: armour, gloves, boots, a belt; tent, bedroll, barding', 'leatherworking'),
            ('Tailoring: cloth, bandages, rope, a net', 'tailoring')]
    if worn(game, 'leatherworking') or worn(game, 'tailoring'):
        opts.append(('Mend leather or cloth, yours or your company\'s', 'mend'))
    extra(game, 'leatherworking', opts)
    extra(game, 'tailoring', opts)
    opts.append(('Leave', 'leave'))
    fee = fee_here(game, BENCH_FEE)
    EV.ask(game, 'bench', 'The workbench', 'Awls, needles, waxed thread, shears and a heavy knife.' +
           (f' The use of the bench costs {fmt(fee)}.' if fee else '') +
           (f'\n\nLeatherworking {rl}, Tailoring {rt}.' if rl or rt else ''), opts)


def r_bench(game, choice, ctx):
    from . import events as EV
    if choice in ('leatherworking', 'tailoring'):
        pick_item(game, choice)
    elif choice == 'mend':
        opts = [(f'{i.display_name()} ({i.dur}/{i.mdur}): one ' + ('bolt of cloth' if craft_of(i) == 'tailoring' else
                 'piece of leather'), f'bmend:{i.id}') for i in worn(game, 'leatherworking') + worn(game, 'tailoring')][:16]
        EV.ask(game, 'anvil_do', 'Mending', 'Which piece goes on the bench?', opts + [('Never mind', 'leave')])
    else:
        r_extra(game, choice)


# ------------------------------------------------------------------ making
def pick_item(game, craft):
    from . import events as EV
    r = LS.rank(game, craft)
    table = CRAFT_OF[craft]
    have = {m: count(game, stuff_key(craft, m)) for m in STUFF[craft]}
    opts, cols = [], []
    for k, (name, fam, need, rank) in table.items():
        enough = any(n >= need for n in have.values())
        tool = fam.startswith('tool:') and fam[5:] not in ('bandage',) and any(i.k == 'tool' and i.t == fam[5:] for i in game.player.inv)
        if tool:
            continue
        unit = {'smithing': 'bar', 'tailoring': 'cloth', 'leatherworking': 'leather'}[craft]
        lab = f'{name}: {need} {unit}' + (f' (rank {rank})' if rank > r else '')
        opts.append((lab, f'make:{k}') if enough and rank <= r else (lab, None))
        cols.append(LS.colour_of(game, craft, rank))
    opts = opts[:24] + [('Never mind', 'leave')]
    EV.ask(game, 'craft_item', LS.LIFE[craft]['name'], 'What will you make?', opts, craft=craft, colours=cols[:24])


def r_craft_item(game, choice, ctx):
    from . import events as EV
    if not choice or not choice.startswith('make:'):
        return
    craft, k = ctx['craft'], choice[5:]
    name, fam, need, rank = CRAFT_OF[craft][k]
    r = LS.rank(game, craft)
    opts, cols = [], []
    for m, (mn, tier, mr) in STUFF[craft].items():
        n = count(game, stuff_key(craft, m))
        if n < need:
            continue
        opts.append((f'{mn} ({n})' + (f': too hard for you yet ({mr})' if mr > r else ''), f'{k}|{m}' if mr <= r else None))
        cols.append(LS.colour_of(game, craft, max(rank, mr)))
    if not opts:
        return
    EV.ask(game, 'craft_stuff', name, 'Of what?', opts + [('Never mind', 'leave')], craft=craft, colours=cols)


def r_craft_stuff(game, choice, ctx):
    from . import events as EV
    if not choice or '|' not in choice:
        return
    craft = ctx['craft']
    k, m = choice.split('|')
    if craft == 'tailoring' and not CRAFT_OF[craft][k][1].startswith('tool:'):
        EV.ask(game, 'craft_feel', CRAFT_OF[craft][k][0], 'Warm, for the cold country, or cool, for the heat?',
               [('Warm', f'{k}|{m}|warm'), ('Cool', f'{k}|{m}|cool'), ('Never mind', 'leave')], craft=craft)
        return
    ask_part(game, craft, k, m, None, [])


def r_craft_feel(game, choice, ctx):
    if not choice or '|' not in choice:
        return
    k, m, feel = choice.split('|')
    ask_part(game, ctx['craft'], k, m, feel, [])


def slot_of(fam):
    from .itemdata import grades
    return D.BASES[grades(fam)[0]]['slot']


def ask_part(game, craft, k, m, feel, picked):
    """The power of the piece: one beast part of your choice (two from rank 40), or none."""
    from . import events as EV
    from types import SimpleNamespace
    from . import beastparts as BP
    name, fam, _need, _rank = CRAFT_OF[craft][k]
    if fam.startswith('tool:'):
        make(game, craft, k, m, feel)
        return
    cands = [c for c in BP.choices(game, SimpleNamespace(slot=slot_of(fam))) if c[1] not in picked]
    if not cands:
        make(game, craft, k, m, feel, picked)
        return
    opts = [(lab, key) for lab, key, _it in cands][:16] + [('No part' if not picked else 'No second part', '-')]
    EV.ask(game, 'craft_part', name, 'Which part gives it its power?' if not picked else
           'A master may set a second part in it. Which?', opts, craft=craft, k=k, m=m, feel=feel, picked=picked)


def r_craft_part(game, choice, ctx):
    if not choice or choice == 'leave':
        return
    picked = list(ctx['picked']) + ([choice] if choice != '-' else [])
    if choice != '-' and len(picked) < 2 and LS.rank(game, ctx['craft']) >= 40:
        ask_part(game, ctx['craft'], ctx['k'], ctx['m'], ctx['feel'], picked)
        return
    make(game, ctx['craft'], ctx['k'], ctx['m'], ctx['feel'], picked)


def quality(r, at):
    d = r - at
    roll = random.random()
    mw = 0 if r < 25 else min(.25, .04 + .01 * d) + (.15 if r >= 50 else 0)
    crude = max(.03, .4 - .03 * d - (.1 if r >= 5 else 0))
    return 'masterwork' if roll < mw else 'crude' if roll < mw + crude else 'fine'


def make(game, craft, k, m, feel=None, parts=()):
    """Make it: the grade from the material's tier, the material's property, the quality from your rank, and the
    power of the beast part you chose."""
    from .entities import Item, make_gear
    from .itemdata import grades
    from . import beastparts as BP
    name, fam, need, rank = CRAFT_OF[craft][k]
    key = stuff_key(craft, m)
    if count(game, key) < need:
        return
    if max(rank, STUFF[craft][m][2]) > LS.rank(game, craft):
        LS.too_hard(game, craft, max(rank, STUFF[craft][m][2]), f'{name} of {STUFF[craft][m][0].lower()}')
        return
    if not pay(game, ANVIL_FEE if craft == 'smithing' else BENCH_FEE):
        return
    take(game, key, need)
    r = LS.rank(game, craft)
    mn, tier, mr = STUFF[craft][m]
    at = max(rank, mr)
    p = game.player
    turns = 30 + need * 10
    if fam.startswith('tool:'):
        t = fam[5:]
        n = 3 if t == 'bandage' else 1
        it = Item(game.new_id(), 'tool', t, n)
        if t == 'barding':
            it.bard = (6 if k == 'mailbarding' else 3) + 3 * GRADE_OF[tier]
            it.name = f'{name} of {mn.lower()}'
        game.add_to_inv(it) or game.spill(game.map, p.x, p.y, it)
        game.msg(f'You make {getattr(it, "name", None) or name.lower()}.', 'good')
    else:
        base = grades(fam)[GRADE_OF[tier]]
        it = make_gear(game, base, 'normal', D.BASES[base]['lvl'])
        q = quality(r, at)
        it.made = (craft, m, q)
        mult = QUALITY[q]
        if it.arm:
            it.arm = max(1, round(it.arm * mult))
        if it.dmg:
            it.dmg = (max(1, round(it.dmg[0] * mult)), max(1, round(it.dmg[1] * mult)))
        if getattr(it, 'mdur', 0):
            it.mdur = it.dur = max(5, round(it.mdur * (.8 if q == 'crude' else 1.1 if q == 'masterwork' else 1)))
        props(it, craft, m)
        if feel or m in ('fur', 'bearfur', 'cavefur'):
            it.feel = feel or 'warm'
        bname = name if k in ROAD else D.BASES[base]["name"]
        it.name = f'{q.capitalize()} {mn} {bname}' if mn not in ('Leather',) else f'{q.capitalize()} {bname}'
        if k in ROAD:
            it.road = ROAD[k]
        for key in parts:
            got = BP.take(game, key)
            if got is not None:
                BP.apply(it, got)
        if getattr(it, 'named_part', None):
            from .named import poss
            it.name = f'{poss(it.named_part)} {bname}'
        game.add_to_inv(it) or game.spill(game.map, p.x, p.y, it)
        game.msg(f'You make {it.name}' + (f', {it.feel}' if getattr(it, 'feel', None) else '') + '.',
                 'gold' if q == 'masterwork' else 'good')
    LS.gain(game, craft, 2 + need + at / 10, at=at, what=f'{k}:{m}')
    from .gods import on_craft
    on_craft(game, craft)
    game.end_turn(turns)


def props(it, craft, m):
    """What the material adds of its own: always a plain property, never one of the powers of found gear."""
    weapon = it.slot == 'weapon'
    aff = []
    if craft == 'smithing':
        aff = {
            'silver': [('undead', 30)] if weapon else [],
            'bloodstone': [('lpk', 2)] if weapon else [('life', 8)],
            'frostvein': [('cold_dmg', 4)] if weapon else [('res_cold', 15)],
            'blackiron': [('ed', 20)] if weapon else [('edef', 25)],
            'sunstone': [('fire_dmg', 5)] if weapon else [('res_fire', 15)],
            'adamant': [('ed', 35)] if weapon else [('edef', 50)],
            'wyrmstone': [('fire_dmg', 4), ('cold_dmg', 4)] if weapon else [('res_fire', 15), ('res_cold', 15)],
            'star': [('ed', 40)] if weapon else [('edef', 40)],
        }.get(m, [])
        if m == 'star':
            aff.append(random.choice([('crit', 5), ('leech', 3)] if weapon else [('res_all', 8), ('dr', 3)]))
        if m in ('moonsilver', 'star'):
            it.rstr = round(it.rstr * (.6 if m == 'moonsilver' else .5))
        if getattr(it, 'mdur', 0):
            k = {'bog': .7, 'deepiron': 1.5}.get(m, 1)
            it.mdur = it.dur = max(5, round(it.mdur * k))
    elif craft == 'tailoring':
        aff = {'felt': [('edef', 20)], 'mohair': [('mana', 5)], 'spidersilk': [('mana', 10)], 'sandsilk': [('res_fire', 10)],
               'shadowsilk': [('dex', 4)], 'mammoth': [('res_cold', 15)], 'seasilk': [('res_light', 15)],
               'queensilk': [('mana', 25)], 'emberthread': [('res_fire', 25)], 'feysilk': [('mana', 15)]}.get(m, [])
        if m == 'feysilk':
            aff.append(random.choice([('res_all', 8), ('mpk', 2)]))
        if m == 'hemp' and getattr(it, 'mdur', 0):
            it.mdur = it.dur = round(it.mdur * 1.5)
    else:
        aff = {'snake': [('res_poison', 15)], 'thick': [('edef', 20)], 'bearfur': [('res_cold', 10)],
               'panther': [('dex', 4)], 'croc': [('edef', 30)], 'cavefur': [('res_cold', 20)], 'sabre': [('dex', 6)],
               'mammothhide': [('edef', 30)], 'rhino': [('edef', 40)], 'drake': [('res_fire', 25)]}.get(m, [])
        if m in ('sturdy', 'mammothhide') and getattr(it, 'mdur', 0):
            it.mdur = it.dur = round(it.mdur * (1.4 if m == 'sturdy' else 2))
    it.aff += [list(a) for a in aff]


# ------------------------------------------------------------------ Unmake
STRONG = {'leech', 'res_all', 'dr', 'crit', 'mpk', 'lpk'}


def found_pieces(game):
    """Found gear a maker may unmake: known powers, and not a unique or a piece of a set."""
    from .entities import unique_named
    return [i for i in game.player.inv if i.k == 'gear' and i.rar in ('magic', 'rare') and i.identified and i.aff
            and not getattr(i, 'made', None) and not i.set_key and not unique_named(i.name) and not game.is_equipped(i)]


def own_pieces(game, craft, master=False):
    """Your own work of this craft that has no moved power yet (for a great master: any plain piece of the craft)."""
    return [i for i in game.player.inv if i.k == 'gear' and craft_of(i) == craft and not getattr(i, 'moved', False)
            and (getattr(i, 'made', (None,))[0] == craft or (master and i.rar == 'normal'))]


def unmake_pairs(game, craft, master=False):
    return bool(found_pieces(game) and own_pieces(game, craft, master))


def strong(stat):
    return stat.startswith('skill') or stat in STRONG


def unmake_chance(game, craft, stat, master=False):
    """About 40% at rank 40, 55% at 45, 70% at 50, never above 80; a strong power costs 15. A great master: 50%."""
    if master:
        return 50
    r = LS.rank(game, craft)
    c = min(80, 40 + 3 * (r - 40))
    return max(5, c - (15 if strong(stat) else 0))


def unmake_menu(game, craft, master=None):
    from . import events as EV
    opts = [(i.display_name(), f'f:{i.id}') for i in found_pieces(game)][:14]
    EV.ask(game, 'unmake', 'Unmake', 'Which found piece will you take apart? It is lost, whatever comes of it.',
           opts + [('Never mind', 'leave')], craft=craft, master=master)


def r_unmake(game, choice, ctx):
    from . import events as EV
    from .itemdata import AFFTXT
    if not choice or choice == 'leave':
        return
    craft, master = ctx['craft'], ctx.get('master')
    p = game.player
    if choice.startswith('f:'):
        it = next((i for i in p.inv if i.id == int(choice[2:])), None)
        if not it:
            return
        opts = [(AFFTXT.get(st, st + ' {}').format(v), f'a:{it.id}:{n}') for n, (st, v) in enumerate(it.aff) if isinstance(v, int)]
        EV.ask(game, 'unmake', 'Unmake', f'Which power of {it.display_name()} will you move?', opts + [('Never mind', 'leave')],
               craft=craft, master=master)
    elif choice.startswith('a:'):
        _a, fid, n = choice.split(':')
        opts = [(i.display_name(), f'o:{fid}:{n}:{i.id}') for i in own_pieces(game, craft, bool(master))][:14]
        EV.ask(game, 'unmake', 'Unmake', 'Onto which of your own pieces?', opts + [('Never mind', 'leave')],
               craft=craft, master=master)
    elif choice.startswith('o:'):
        _o, fid, n, oid = choice.split(':')
        found = next((i for i in p.inv if i.id == int(fid)), None)
        if not found:
            return
        st, v = found.aff[int(n)]
        full = LS.rank(game, craft) >= 50 and not master
        val = v if full else max(1, round(v * 2 / 3))
        c = unmake_chance(game, craft, st, bool(master))
        own = next((i for i in p.inv if i.id == int(oid)), None)
        text = (f'{AFFTXT.get(st, st + " {}").format(val)} onto {own.display_name() if own else "your piece"}. '
                f'The chance it takes: {c}%. If it fails, {found.display_name()} is lost all the same, and now and then '
                f'your own piece is ruined or cursed.')
        if master:
            from .money import fmt
            text += f' The master asks {fmt(master)}, whatever comes of it.'
        EV.ask(game, 'unmake_do', 'Unmake', text, [('Do it', f'{fid}:{n}:{oid}:{val}:{c}'), ('Not now', 'leave')],
               craft=craft, master=master)


def r_unmake_do(game, choice, ctx):
    if not choice or choice == 'leave':
        return
    fid, n, oid, val, c = (int(x) for x in choice.split(':'))
    do_unmake(game, ctx['craft'], fid, n, oid, val, c, ctx.get('master'))


def do_unmake(game, craft, fid, n, oid, val, c, master=None):
    p = game.player
    found = next((i for i in p.inv if i.id == fid), None)
    own = next((i for i in p.inv if i.id == oid), None)
    if not found or not own:
        return False
    if master:
        if p.gold < master:
            from .money import fmt
            game.msg(f'The master wants {fmt(master)}, and you do not have it.', 'bad')
            return False
        p.gold -= master
    elif not pay(game, ANVIL_FEE if craft == 'smithing' else BENCH_FEE):
        return False
    st = found.aff[n][0]
    p.inv.remove(found)
    if random.randint(1, 100) <= c:
        for a in own.aff:
            if a[0] == st:
                a[1] += val
                break
        else:
            own.aff.append([st, val])
        own.moved = True
        game.msg(f'{found.display_name()} comes apart under ' + ('the master\'s hands' if master else 'your hands') +
                 f', and its power settles into {own.display_name()}.', 'unique')
        ok = True
    else:
        ok = False
        if random.random() < .25:
            if getattr(own, 'mdur', 0) and random.random() < .5:
                own.dur = 0
                game.msg(f'It goes wrong. {found.display_name()} crumbles, and {own.display_name()} cracks with it: broken.', 'bad')
            else:
                own.curse = list(getattr(own, 'curse', [])) + [['life', 10]]
                own.curse_known = True
                game.msg(f'It goes wrong. {found.display_name()} crumbles, and something sour seeps into '
                         f'{own.display_name()}: it is cursed.', 'bad')
        else:
            game.msg(f'It goes wrong. {found.display_name()} crumbles to nothing, and the power with it. '
                     f'{own.display_name()} is unharmed.', 'bad')
    if not master:
        LS.gain(game, craft, 6, at=LS.rank(game, craft))
    game.end_turn(60)
    return ok


def feel_count(game, feel):
    """How many pieces you wear that keep you warm (or cool); highland wool counts twice."""
    n = 0
    for slot in D.SLOTS:
        it = game.eq_item(slot)
        if it and getattr(it, 'feel', None) == feel:
            n += 2 if getattr(it, 'made', (0, ''))[1] == 'highland' else 1
    return n


# ------------------------------------------------------------------ where materials come from
def shop_cloth(game, s):
    """What cloth a settlement's outfitter has: the land decides, and the danger of the land the tier."""
    from . import cooking as CK
    from . import seasons as SE
    om = game.maps['over']
    lands = set(CK.lands_of(SE.biome(om, s.y * om.w + s.x)))
    from .weather import climate
    cl = climate(game.world, game.world.region_at(s.x, s.y).id)
    from .world import WORLD_H
    south = cl in ('arid', 'hot', 'tropical') or s.y > WORLD_H * .7
    danger = game.world.danger_at(s.x, s.y)
    want = []
    if lands & {'farm', 'steppe'} or not lands:
        want.append('linen')
    if lands & {'moor', 'mountain', 'steppe', 'tundra'}:
        want.append('wool')
    if 'water' in lands or 'marsh' in lands:
        want.append('hemp')
    if s.is_city:
        want += ['felt', 'linen']
    if south:
        want.append('cotton')
    if 'mountain' in lands:
        want += ['mohair', 'highland']
    if lands & {'desert'}:
        want.append('sandsilk')
    if 'coast' in lands and danger >= 8:
        want.append('seasilk')
    want = [w for w in dict.fromkeys(want) if danger >= LS.TIER_DANGER[CLOTHS[w][1]] or CLOTHS[w][1] == 'A'
            or (s.is_city and w == 'felt')]
    random.shuffle(want)
    return [make_mat(game, 'cloth_' + w, 3) for w in want[:2]]


def on_kill(game, mon):
    """Silk from spiders and their queens, emberthread from fire beetles."""
    k = mon.k
    fam = mon.tpl.get('family', k)
    m = game.map
    depth = (getattr(m, 'depth', 0) or 0) if m.kind == 'dungeon' else 0
    got = None
    if k == 'broodmother':
        got = 'queensilk'
    elif k == 'spider' or fam == 'spider':
        if random.random() < .35:
            got = 'shadowsilk' if depth >= 4 and LS.tier_open(game, 'D') else 'spidersilk'
    elif k == 'fire_beetle' and random.random() < .3 and LS.tier_open(game, 'E'):
        got = 'emberthread'
    if got:
        it = make_mat(game, 'cloth_' + got, 1)
        game.spill(m, mon.x, mon.y, it)


def fey_silk(game):
    """At night by the wisp fens and the fairy rings, a forager may find Fey Silk."""
    from . import towns as TW
    if TW.is_night(game) and LS.near_site(game, ('wisps', 'mound', 'starwell'), 3) and random.random() < .25:
        give(game, 'cloth_feysilk', 1)
        game.msg('Between the lights you find threads finer than spider silk, glimmering: Fey Silk.', 'unique')
        return True
    return False


# ------------------------------------------------------------------ the item
def use(game, it):
    """A bar, a bolt or a piece of leather from your pack: from rank 30 in its craft you mend with it on the road.
    Barding goes on your beast."""
    from . import events as EV
    if it.k == 'tool' and it.t == 'barding':
        return put_barding(game, it)
    if it.k == 'tool':
        game.msg(f'{it.display_name()}: a night in the open rests you better with it in your pack.', 'info')
        return 0
    craft = 'leatherworking' if it.k == 'leather' else 'tailoring' if it.t.startswith('cloth_') else 'smithing'
    if LS.rank(game, craft) >= 30 and worn(game, craft):
        opts = [(f'{i.display_name()} ({i.dur}/{i.mdur})', f'road:{i.id}') for i in worn(game, craft)][:16]
        EV.ask(game, 'anvil_do', 'Mending on the road', 'A master mends without a bench or an anvil. Which piece?',
               opts + [('Never mind', 'leave')])
        return 0
    if it.k == 'leather':
        from . import hunting as HT
        game.msg(f'{it.display_name()}: ' + HT.lines(game, it)[0], 'info')
        return 0
    game.msg(f'{it.display_name()}: ' + lines(game, it)[0], 'info')
    return 0


def put_barding(game, it):
    from . import mercs as MC
    mc = next((b for b in (MC.get(game, 'beast'), MC.get(game, 'beast2')) if b and b.state == 'alive'), None)
    if not mc:
        game.msg('Barding is for a beast at your side, and you have none.', 'info')
        return 0
    old = getattr(mc, 'barding', 0)
    game.remove_one(it)
    mc.barding = max(old, getattr(it, 'bard', 3))
    MC.refresh_body(game, mc)
    game.msg(f'You buckle the barding on {mc.name}. It shakes itself, and gets used to it.', 'good')
    return 20


def display(game, it):
    return (f'{it.n}x ' if it.n > 1 else '') + mat_name(it.t)


def lines(game, it):
    kind, m = it.t.split('_', 1)
    if kind == 'ore':
        return [f'Ore, tier {tier_of(it.t)}. Smelt it at an anvil: two make a bar (Smithing {METALS[m][2]}).']
    if kind == 'bar':
        return [f'A bar of {METALS[m][0].lower()}, tier {tier_of(it.t)}. Smiths forge it at an anvil (Smithing {METALS[m][2]}).']
    return [f'Cloth, tier {tier_of(it.t)}. Tailors work it at a workbench (Tailoring {CLOTHS[m][2]}).']


def value(game, it):
    kind, _m = it.t.split('_', 1)
    return TIER_VAL[tier_of(it.t)] * (1.5 if kind == 'bar' else .6 if kind == 'cloth' else .8)


def glyph(it):
    return {'ore': '*', 'bar': '=', 'cloth': '~'}[it.t.split('_', 1)[0]]


def color(it):
    kind, m = it.t.split('_', 1)
    if kind == 'cloth':
        return (200, 190, 230) if 'silk' in m else (210, 200, 170)
    return {'silver': (220, 225, 235), 'moonsilver': (200, 220, 255), 'bloodstone': (200, 70, 70), 'sunstone': (250, 180, 60),
            'frostvein': (170, 220, 255), 'blackiron': (110, 110, 120), 'adamant': (180, 240, 220), 'wyrmstone': (230, 120, 60),
            'star': (196, 214, 255), 'deepiron': (130, 140, 170), 'bog': (140, 110, 80)}.get(m, (170, 170, 175))


def register():
    from . import events as EV
    EV.RESOLVERS['anvil'] = r_anvil
    EV.RESOLVERS['anvil_do'] = r_anvil_do
    EV.RESOLVERS['bench'] = r_bench
    EV.RESOLVERS['craft_item'] = r_craft_item
    EV.RESOLVERS['craft_stuff'] = r_craft_stuff
    EV.RESOLVERS['craft_feel'] = r_craft_feel
    EV.RESOLVERS['craft_part'] = r_craft_part
    EV.RESOLVERS['unmake'] = r_unmake
    EV.RESOLVERS['unmake_do'] = r_unmake_do


register()
