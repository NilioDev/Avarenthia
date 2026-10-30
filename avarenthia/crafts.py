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
    'hooks': ('Fish Hooks', 'tool:hooks', 1, 3),
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
}
CRAFT_OF = {'smithing': SMITH, 'tailoring': TAILOR, 'leatherworking': LEATHERWORK}
STUFF = {'smithing': METALS, 'tailoring': CLOTHS, 'leatherworking': LEATHERS}
QUALITY = {'crude': .85, 'fine': 1.0, 'masterwork': 1.15}
BENCH_FEE = 20
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
    if worn(game):
        opts.append(('Mend your metal gear', 'mend'))
    if game.eq_item('weapon'):
        opts.append(('Hone your blade', 'hone'))
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


def worn(game):
    return [i for i in game.player.inv if i.k == 'gear' and getattr(i, 'mdur', 0) and i.dur < i.mdur and metal_gear(i)]


def metal_gear(it):
    fam = D.BASES[it.base].get('family', it.base)
    return any(v[1] == fam for v in SMITH.values())


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


def r_anvil_do(game, choice, ctx):
    if not choice or choice == 'leave':
        return
    if choice.startswith('smelt:'):
        smelt(game, choice[6:])
    elif choice.startswith('mend:'):
        mend(game, int(choice[5:]))


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


def mend(game, iid):
    it = next((i for i in game.player.inv if i.id == iid), None)
    if not it:
        return
    use = next((k for k in ['bar_' + m for m in METALS] + ['ore_iron'] if count(game, k)), None)
    if not use:
        game.msg('Mending wants one bar of metal, or one load of iron ore.', 'bad')
        return
    if not pay(game, ANVIL_FEE // 2):
        return
    take(game, use, 1)
    it.dur = it.mdur
    game.msg(f'You hammer out the dents and rivet what was loose: {it.display_name()} is whole again.', 'good')
    LS.gain(game, 'smithing', 1, at=D.BASES[it.base]['lvl'])
    game.end_turn(40)


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
    opts = [('Leatherwork: armour, gloves, boots, a belt', 'leatherworking'),
            ('Tailoring: cloth, bandages, rope, a net', 'tailoring'), ('Leave', 'leave')]
    fee = fee_here(game, BENCH_FEE)
    EV.ask(game, 'bench', 'The workbench', 'Awls, needles, waxed thread, shears and a heavy knife.' +
           (f' The use of the bench costs {fmt(fee)}.' if fee else '') +
           (f'\n\nLeatherworking {rl}, Tailoring {rt}.' if rl or rt else ''), opts)


def r_bench(game, choice, ctx):
    if choice in ('leatherworking', 'tailoring'):
        pick_item(game, choice)


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
    make(game, craft, k, m)


def r_craft_feel(game, choice, ctx):
    if not choice or '|' not in choice:
        return
    k, m, feel = choice.split('|')
    make(game, ctx['craft'], k, m, feel)


def quality(r, at):
    d = r - at
    roll = random.random()
    mw = 0 if r < 25 else min(.25, .04 + .01 * d)
    crude = max(.03, .4 - .03 * d - (.1 if r >= 5 else 0))
    return 'masterwork' if roll < mw else 'crude' if roll < mw + crude else 'fine'


def make(game, craft, k, m, feel=None):
    """Make it: the grade from the material's tier, the material's property, the quality from your rank."""
    from .entities import Item, make_gear
    from .itemdata import grades
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
        game.add_to_inv(it) or game.spill(game.map, p.x, p.y, it)
        game.msg(f'You make {name.lower()}.', 'good')
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
        it.name = f'{q.capitalize()} {mn} {D.BASES[base]["name"]}' if mn not in ('Leather',) else \
            f'{q.capitalize()} {D.BASES[base]["name"]}'
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
    game.msg(f'{it.display_name()}: ' + lines(game, it)[0], 'info')
    return 0


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


register()
