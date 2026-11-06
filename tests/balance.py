"""The balance measure (round 57a, "The bar of seven keys" in docs/plan.md): the bot builds of the part `balance`,
each fought with today's bar and the new one, at levels 10, 20 and 30, with and without an epic.

The four ways to fight, all with the weapon's two skills on 1-2:
    old        three class skills and the elite (today's bar, no epic)
    old+epic   three class skills and the epic in the elite's place, once per rest (today's bar with an epic)
    new        four class skills, one of them the elite
    new+epic   four class skills, one of them the elite, and the epic on 7, filled by fighting (epics.fill, as in the game)
For each: waves won, turns, damage taken, and how often the epic filled. Then each of the 22 epics alone, in a
build of its own school at level 20: how often it fills per four waves, and its share of the damage dealt.

    python tests/balance.py [worlds] [seed]

The part `balance` of test_headless.py asserts the bands: the new bar no more than about 15% faster than the old
one, and an epic about once per hard fight."""
import os
import random
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
sys.path.insert(0, HERE)

from avarenthia import engine as E, data as D  # noqa: E402
from avarenthia import skills as SK, epics as EP  # noqa: E402
from avarenthia.entities import make_monster, make_gear  # noqa: E402
from avarenthia.worldgen import free_around, bfs, cheb  # noqa: E402

E.save_path = lambda: os.path.join(tempfile.gettempdir(), f'avarenthia_balance_{os.getpid()}.dat')

LEVELS = (10, 20, 30)
WAVES = 4                   # a run of waves without a rest: a hard fight's worth
FOE_BELOW = 5               # the foes' level below yours: the lowest that still fills the epic
MODES = ('old', 'old+epic', 'new', 'new+epic')
# name: (classes, weapon, wear, four class skills, the elite, the epic, (str, dex, vit, ene) at level 18)
BUILDS = {
    'Pyromancer': (['fire'], None, ['quilted', 'cap'], ['firebolt', 'fireball', 'searing_brand', 'immolate'], 'inferno',
                   'sunfall', (40, 60, 120, 120)),
    'Warrior': (['warcraft'], 'greatsword', ['chainmail', 'fullhelm'], ['rage', 'charge', 'iron_skin', 'warcry'],
                'last_stand', 'worldshaker', (120, 60, 120, 40)),
    'Firebrand': (['fire', 'warcraft'], 'longsword', ['chainmail', 'skullcap', 'roundshield'],
                  ['firebolt', 'rage', 'warcry', 'fireball'], 'inferno', 'sunfall', (90, 60, 120, 70)),
    'Reaver': (['shadow', 'warcraft'], 'waraxe', ['chainmail', 'skullcap', 'roundshield'],
               ['drain', 'rage', 'warcry', 'shadow_bolt'], 'soul_knife', 'the_unmaking', (100, 60, 120, 60)),
    'Rogue': (['cunning'], 'dagger', ['leather', 'cap'], ['envenom', 'garrote', 'shadowstep', 'cheap_shot'], None,
              'death_mark', (60, 120, 120, 40)),
}
# a weapon and wear for a build of each school, for the 22 epics alone
SCHOOL_KIT = {'warcraft': ('greatsword', ['chainmail', 'fullhelm'], (120, 60, 120, 40)),
              'cunning': ('dagger', ['leather', 'cap'], (60, 120, 120, 40))}
CASTER_KIT = (None, ['quilted', 'cap'], (40, 60, 120, 120))

_APPS = {}


def app_for(world):
    if world not in _APPS:
        from test_headless import new_app
        _APPS[world] = new_app('soft', seed=world)
    return _APPS[world]


def dress(g, lvl, classes, weapon, wear, stats):
    p = g.player
    k = lvl / 18
    p.lvl = lvl
    p.str, p.dex, p.vit, p.ene = (round(v * k) for v in stats)
    p.classes = list(classes)
    for line in classes:
        p.disc[line][0] = min(50, lvl * 2)
    p.inv, p.eq, p.buffs, p.cooldowns = [], {}, [], {}
    for base in ([weapon] if weapon else []) + wear:
        it = make_gear(g, base, 'normal', max(1, lvl // 2))
        g.add_to_inv(it)
        p.eq[D.BASES[base]['slot']] = it.id
    if weapon:
        p.disc[SK.WEAPON_LINE[weapon]][0] = min(50, round(lvl * 1.6))


def fight(world, lvl, kit, mode, epic):
    """One run of WAVES waves. Returns dict(won, turns, taken, dealt, fills, epic_dealt)."""
    classes, weapon, wear, four, elite, stats = kit
    app = app_for(world)
    g, p = app.game, app.game.player
    random.seed(world * 7 + lvl)          # one draw for every mode, so they fight the same foes
    dress(g, lvl, classes, weapon, wear, stats)
    with_epic = mode.endswith('+epic') and epic
    if mode.startswith('old'):
        cls = four[:3] + ([epic] if with_epic else [elite] if elite else [four[3]])
        bar = [None, None] + cls + [None]           # the old bar: the epic in the elite's place, not on key 7
    else:
        cls = (four[:3] + [elite]) if elite else four[:4]
        bar = [None, None] + cls + [epic if with_epic else None]
    p.known = [s for s in bar if s]
    p.bar = bar
    s = EP.st(g)
    s['phoenix_day'] = -1
    s['charge'] = EP.CHARGE_FULL if mode.startswith('old') else 0.0     # old: once per rest, so once a run
    if with_epic:
        s['learnt'][SK.SKILLS[epic].line] = epic
    g.dead = False
    g.request = None
    g.cur = 'over'
    g.enter_dungeon(list(g.world.dungeons)[0], 1, 'up')
    m = g.map
    st_ = g.stats()
    p.life, p.mana, p.stamina = st_['max_life'], st_['max_mana'], st_['max_stamina']
    out = dict(won=0, turns=0, taken=0, dealt=0, fills=0, uses=0, epic_dealt=0)
    eslot = bar.index(epic) if with_epic else None
    for wave in range(WAVES):
        if g.map is not m or not m.inb(p.x, p.y):      # a pit, a fall, a stair: the run is over
            break
        m.mons = [o for o in m.mons if o.is_npc]
        foes = []
        near = bfs(m, p.x, p.y, lambda k: D.TILES[k].walk, 5)
        for n, c in enumerate([c for c in free_around(g, m, p.x, p.y, 4) if cheb(c[0], c[1], p.x, p.y) >= 3
                               and 0 <= near[c[1] * m.w + c[0]] <= 5 and g.visible(*c) and not g.occupied(m, *c)][:3]):
            o = make_monster(g, random.choice(['goblin', 'orc', 'skeleton']), *c, max(1, lvl - FOE_BELOW),
                             elite=1 if (wave % 2 and n == 0) else 0)
            o.awake = wave % 2 == 0
            m.mons.append(o)
            foes.append(o)
        g.compute_fov()
        for _ in range(150):
            live = [o for o in foes if o in m.mons and not getattr(o, 'fleeing', False)]
            if not live or g.dead:
                break
            life = p.life
            before = s.get('charge', 0.0)
            hp0 = {o.id: max(0, o.hp) for o in foes if o in m.mons}
            used = 0
            epic_turn = False
            if with_epic and eslot is not None:
                if EP.ready(g, epic) and epic != 'phoenix' and not p.cooldowns.get(epic):
                    used = SK.use(g, eslot)
                    if used:
                        epic_turn = True
                        out['uses'] += 1
            if not used:
                for i in range(2, 6):
                    sid = bar[i]
                    sk = SK.SKILLS[sid] if sid else None
                    if sk and sk.buff and any(b[0] == sk.buff[0] for b in p.buffs):
                        continue
                    if sid and not p.cooldowns.get(sid) and SK.can_pay(g, sk):
                        used = SK.use(g, i)
                        if used:
                            break
                for i in (0, 1):
                    if used:
                        break
                    used = SK.use(g, i) if not p.cooldowns.get(bar[i] or '') else 0
            if not used:
                t = min(live, key=lambda o: cheb(o.x, o.y, p.x, p.y))
                if cheb(t.x, t.y, p.x, p.y) <= 1:
                    g.melee(t)
                else:
                    dx, dy = (t.x > p.x) - (t.x < p.x), (t.y > p.y) - (t.y < p.y)
                    if not g.try_move(dx, dy):
                        dist = bfs(m, t.x, t.y, lambda k: D.TILES[k].walk, 30)
                        step = [(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1) if m.inb(p.x + a, p.y + b)
                                and dist[(p.y + b) * m.w + p.x + a] >= 0]
                        if step:
                            a, b = min(step, key=lambda d: dist[(p.y + d[1]) * m.w + p.x + d[0]])
                            g.try_move(a, b)
                g.end_turn(1)
            else:
                g.end_turn(used)
            taken = max(0, life - p.life)
            dealt = sum(hp0[o.id] - (max(0, o.hp) if o in m.mons and o.hp > 0 else 0) for o in foes if o.id in hp0)
            felled = [o for o in foes if o.id in hp0 and (o not in m.mons or o.hp <= 0)]
            out['taken'] += taken
            out['dealt'] += dealt
            if epic_turn:
                out['epic_dealt'] += dealt
            if mode == 'new+epic' and before < EP.CHARGE_FULL <= s.get('charge', 0.0):
                out['fills'] += 1           # the game fills it itself (epics.fill), as you fight
            out['turns'] += 1
        if not g.dead and not any(o in m.mons and o.hp > 0 and not getattr(o, 'fleeing', False) for o in foes):
            out['won'] += 1
        if g.dead:
            break
    g.dead = False
    g.request = None
    g.cur = 'over'
    return out


def run(worlds=2, seed=11, quiet=False, levels=LEVELS, modes=MODES):
    """The table: {(build, level, mode): summed results}."""
    table = {}
    for name, (cl, weapon, wear, four, elite, epic, stats) in BUILDS.items():
        for lvl in levels:
            for mode in modes:
                tot = dict(won=0, turns=0, taken=0, dealt=0, fills=0, uses=0, epic_dealt=0, waves=0)
                for wd in range(seed, seed + worlds):
                    r = fight(wd, lvl, (cl, weapon, wear, four, elite, stats), mode, epic)
                    for k, v in r.items():
                        tot[k] += v
                    tot['waves'] += WAVES
                table[(name, lvl, mode)] = tot
            if not quiet:
                row = '  '.join(f'{md:>8}: {t["won"]:>2}/{t["waves"]} {t["turns"]:>4}t {t["taken"]:>5}hurt'
                                + (f' {t["fills"]}f' if md == 'new+epic' else '')
                                for md in modes for t in [table[(name, lvl, md)]])
                print(f'{name:>10} L{lvl:<2} {row}')
    return table


def epics_alone(worlds=1, seed=11, lvl=20, quiet=False):
    """Each epic in a build of its own school: fills per four waves, and its share of the damage dealt."""
    out = {}
    for ep in EP.EPIC_LIST:
        line = ep.line
        weapon, wear, stats = SCHOOL_KIT.get(line, CASTER_KIT)
        plain = [s.id for s in SK.SKILLS.values() if s.line == line and not getattr(s, 'epic', False)
                 and not getattr(s, 'weapon_skill', False) and not getattr(s, 'passive', False)
                 and s.mode not in ('passive',) and not s.guild][:4]
        if len(plain) < 4:
            plain += ['rage', 'warcry', 'charge', 'iron_skin'][:4 - len(plain)]
        tot = dict(won=0, turns=0, dealt=0, fills=0, uses=0, epic_dealt=0, waves=0, taken=0)
        try:
            for wd in range(seed, seed + worlds):
                r = fight(wd, lvl, ([line], weapon, wear, plain, None, stats), 'new+epic', ep.id)
                for k, v in r.items():
                    tot[k] += v
                tot['waves'] += WAVES
        except Exception as ex:      # a school a bot cannot fight with alone: say so, go on
            tot['error'] = repr(ex)[:60]
        out[ep.id] = tot
        if not quiet:
            share = tot['epic_dealt'] / max(1, tot['dealt'])
            print(f'  {ep.name:>24} ({line:>11}): {tot["fills"]} fills, {tot["uses"]} uses in {tot["waves"]} waves, '
                  f'{share:4.0%} of the damage, won {tot["won"]}/{tot["waves"]}' + (f'  {tot["error"]}' if 'error' in tot else ''))
    return out


def summary(table):
    """The two numbers the bands are about: how much faster the new bar is, and fills per run of waves."""
    old = sum(t['turns'] for (n, lv, md), t in table.items() if md == 'old+epic')
    new = sum(t['turns'] for (n, lv, md), t in table.items() if md == 'new+epic')
    runs = sum(1 for (n, lv, md) in table if md == 'new+epic')
    fills = sum(t['fills'] for (n, lv, md), t in table.items() if md == 'new+epic')
    worlds = max(1, table[next(iter(table))]['waves'] // WAVES)
    return dict(speedup=old / max(1, new), fills_per_run=fills / max(1, runs * worlds))


if __name__ == '__main__':
    worlds = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 11
    print(f'The balance measure: {worlds} world(s) from seed {seed}, {WAVES} waves a run, three foes a wave '
          '(an elite in every other), five levels below you.')
    tb = run(worlds, seed)
    sm = summary(tb)
    print(f'\nnew+epic against old+epic: {sm["speedup"]:.2f} times as fast (band: at most 1.15); '
          f'the epic filled {sm["fills_per_run"]:.2f} times per run of {WAVES} waves (band: about 1)')
    print('\nThe 22 epics alone, level 20:')
    epics_alone(1, seed)
