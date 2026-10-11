"""Factions are made fresh for every world: the same kinds of powers (a realm, merchants, wood folk, outlaws,
a cult, sometimes dwarf clans and orc tribes) but with their own peoples, names, colours and rivalries.

The keys stay fixed ('crown', 'league', ...) so the rules can refer to them; everything players see
comes from the generated data, which lives in world.factions and is installed into data.FACTIONS."""
import random

from . import data as D

LANDS = ['Aldmark', 'Valdren', 'Esterhal', 'Morwick', 'Caerlin', 'Thessaly', 'Brannock', 'Ilmarch', 'Oskvald', 'Lorwen']

ROLES = {
    'crown': dict(
        races=[('human', 6), ('elf', 2), ('dwarf', 1)], start=10,
        names={'human': ['The Crown of {land}', 'The Kingdom of {land}', 'The Throne of {land}', 'The Realm of {land}'],
               'elf': ['The Elven Throne of {land}', 'The Starlit Court of {land}'],
               'dwarf': ['The Iron Kingdom of {land}', 'The Mountain Throne of {land}']},
        short=['Crown', 'Kingdom', 'Throne', 'Realm'], fg=['#e8d070', '#e0c060', '#f0e090'],
        troops={'human': ['soldier', 'soldier', 'crossbow', 'knight'], 'elf': ['warden', 'warden', 'druid', 'knight'],
                'dwarf': ['clansman', 'clansman', 'thunderer', 'knight']},
        castle=['Castle', 'Royal Keep'], fort=['Watchfort', 'Border Fort'],
        desc='The old realm. Holds the heartland, its castles and most of its villages.'),
    'league': dict(
        races=[('human', 4), ('halfling', 3), ('gnome', 2), ('dwarf', 1)], start=5,
        names={'human': ['The Merchant League', 'The Free Cities', 'The Golden Compact', 'The Guild of the Silver Scale'],
               'halfling': ['The Hearthfoot Company', 'The Copper Kettle League', 'The Greenmarket Guild'],
               'dwarf': ['The Anvil Trading Company'],
               'gnome': ['The Cogwheel Consortium', 'The Brass Exchange']},
        short=['League', 'Compact', 'Guild', 'Company'], fg=['#e8a050', '#f0b860', '#d89848'],
        troops={'*': ['mercenary', 'mercenary', 'crossbow']},
        castle=['Counting Keep', 'Guild Hall'], fort=['Toll Fort', 'Customs House'],
        desc='Rich trading towns that pay mercenaries to keep the roads open.'),
    'circle': dict(
        races=[('elf', 5), ('halfling', 2), ('human', 2)], start=0,
        names={'elf': ['The Circle of Thorns', 'The Green Court', 'The Wardens of the Wild', 'The Eldergrove'],
               'halfling': ['The Hedge Wardens', 'The Barrow Watch'],
               'human': ['The Druids of the Oak', 'The Circle of Thorns']},
        short=['Circle', 'Court', 'Wardens', 'Grove'], fg=['#70c060', '#60b878', '#88cc58'],
        troops={'*': ['warden', 'druid', 'wolf']},
        castle=['Grove Hold', 'Moon Hall'], fort=['Thornwatch', 'Hollow Watch'],
        desc='Keepers of the deep woods and marshes. They distrust outsiders.'),
    'blackhand': dict(
        races=[('human', 5), ('orc', 2), ('goblin', 2)], start=-40,
        names={'human': ['The Black Hand', 'The Red Knives', 'The Iron Crows', 'The Grey Wolves', 'The Hanged Men'],
               'orc': ['The Broken Tusks', 'The Black Hand'], 'goblin': ['The Rat Kings', 'The Night Knives']},
        short=['Outlaws'], fg=['#d04040', '#c83848', '#b84030'],
        troops={'*': ['raider', 'raider', 'brigand', 'robber_knight']},
        castle=['Robber Keep', 'Gallows Hall'], fort=['Raider Fort', 'Cutthroat Tower'],
        desc='Robber knights and outlaws who tax the roads with steel.'),
    'clan': dict(
        races=[('dwarf', 4), ('gnome', 1)], start=0,
        names={'dwarf': ['Clan {fam}', 'The Hold of {fam}', 'The {fam} Clans'], 'gnome': ['The Burrows of {fam}']},
        short=['Clan'], fg=['#d89060', '#c8a078'],
        troops={'*': ['clansman', 'clansman', 'thunderer']},
        castle=['Deephall', 'Stonehold'], fort=['Gatehold', 'Watchstone'],
        desc='Proud dwarf clans of the hills and mountain roots. Slow to trust, never forget a debt.'),
    'horde': dict(
        races=[('orc', 3), ('goblin', 2)], start=-30,
        names={'orc': ['The {fam} Horde', 'The {fam} Tribes', 'The Clans of the Red Tusk'],
               'goblin': ['The {fam} Warrens', 'The Goblin Tribes of the {fam}']},
        short=['Horde', 'Tribes'], fg=['#a0c050', '#b8a040'],
        troops={'*': ['orc', 'orc', 'gobarcher', 'ogre']},
        castle=['War Camp', 'Skull Hall'], fort=['Raid Camp', 'Bone Fence'],
        desc='Orc tribes from the badlands. They respect strength, and little else.'),
}
GLYPH = {'crown': 'K', 'league': 'M', 'circle': 'D', 'blackhand': 'R', 'cult': 'U', 'clan': 'h', 'horde': 'O'}


def _pick(lst):
    return random.choices([a for a, _ in lst], [w for _, w in lst])[0]


def generate(evil):
    """Return the factions for a new world. evil is the EVILS entry whose cult serves it."""
    from .races import _SYL
    land = random.choice(LANDS)
    roles = ['crown', 'league', 'circle', 'blackhand']
    if random.random() < .75:
        roles.append('clan')
    if random.random() < .65:
        roles.append('horde')
    out = {}
    for r in roles:
        t = ROLES[r]
        race = _pick(t['races'])
        fam = random.choice(_SYL.get(race, _SYL['human'])['family'])
        name = random.choice(t['names'].get(race) or sum(t['names'].values(), [])).format(land=land, fam=fam)
        troops = t['troops'].get(race) or t['troops'].get('*')
        out[r] = dict(name=name, short=random.choice(t['short']), fg=D.hexrgb(random.choice(t['fg'])), start=t['start'],
                      enemies=[], troops=list(troops), castle=random.choice(t['castle']), fort=random.choice(t['fort']),
                      desc=t['desc'], race=race, glyph=GLYPH[r])
    if 'clan' in out and out['clan']['short'] == out['crown']['short']:
        out['clan']['short'] = 'Clans'
    cname, cshort, ctroops, ccastle, cfort = evil['cult']
    out['cult'] = dict(name=cname, short=cshort, fg=D.hexrgb('#b070ff') if evil['key'] == 'lich' else evil['fg'], start=-100,
                       enemies=[], troops=list(ctroops), castle=ccastle, fort=cfort,
                       race='orc' if evil['key'] == 'warlord' else 'human', glyph='U',
                       desc=f"Servants of {evil['name']}. They answer to no one living.")
    # who fights whom
    def war(a, b):
        if a in out and b in out:
            out[a]['enemies'].append(b)
            out[b]['enemies'].append(a)
    for f in out:
        if f != 'cult':
            war(f, 'cult')
    for f in ('crown', 'league', 'circle', 'clan'):
        war(f, 'blackhand')
        war(f, 'horde')
    if random.random() < .35:
        war('crown', 'league')
    elif random.random() < .35:
        war('crown', 'circle')
    if out.get('clan', {}).get('race') == 'dwarf' and out['circle']['race'] == 'elf' and random.random() < .4:
        war('clan', 'circle')
    for f in out.values():
        f['enemies'] = sorted(set(f['enemies']))
    return out


def install(factions):
    """Make these the factions the rules and screens use."""
    D.FACTIONS.clear()
    D.FACTIONS.update(factions)
    D.FACTION_ORDER[:] = [k for k in ('crown', 'league', 'circle', 'clan', 'horde', 'blackhand', 'cult') if k in factions]
