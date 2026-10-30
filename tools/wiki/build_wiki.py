"""Builds the Avarenthia wiki: one static HTML page with the lore, the great evils, every monster, skill, class and item,
the whole handbook and the plans, read straight from the game's code and docs/.

    python tools/wiki/build_wiki.py [repo] [out.html]       (default: this repo, wiki/avarenthia-wiki.html)

WIKI_NOTES may name a folder with design notes (poi/volken.md, poi/feestdagen.md) to add as planned lore.
CI builds it on every push; download it from the run's Artifacts as "Avarenthia wiki"."""
import html, re, sys, os, io, contextlib, subprocess, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else os.path.join(SRC, 'wiki', 'avarenthia-wiki.html'))
PF = os.environ.get('WIKI_NOTES', '/mnt/project-files')
sys.path.insert(0, SRC)
os.chdir(SRC)

import avarenthia.skills as SK
import avarenthia.weaponskills as WS
import avarenthia.data as D
import avarenthia.evils as EV
import avarenthia.shadow as SHD
import avarenthia.skyseat as SKY
import avarenthia.gods as GODS
import avarenthia.races as RC
import avarenthia.lore as LO
import avarenthia.factions as FA
import avarenthia.itemdata as ID
import avarenthia.classes as CL
import avarenthia.trees as TR
import avarenthia.named as NM
import avarenthia.powers as PW
import avarenthia.bestiary as BE
try:                                # the Varnish and the old places (round 10-12) are not on every branch yet
    import avarenthia.varnishtexts as VT
    import avarenthia.varnish as VA
    import avarenthia.oldplaces as OP
except ImportError:
    VT = VA = OP = None
import avarenthia.handbook as HB
import avarenthia.engine as E

e = html.escape


def rgb(c):
    if isinstance(c, str):
        return c
    return '#%02x%02x%02x' % tuple(c[:3])


def badge(kind):
    t = {'built': 'built', 'planned': 'planned', 'notes': 'design notes'}[kind]
    return f'<span class="badge b-{kind}">{t}</span>'


def inline_md(s):
    s = e(s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<![*\w])\*([^*\n]+)\*(?!\w)', r'<em>\1</em>', s)
    s = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', r'<a href="\2" target="_blank" rel="noopener">\1</a>', s)
    return s


def md(text, hshift=1):
    out, para, lst, tbl = [], [], None, []

    def flush():
        nonlocal para, lst, tbl
        if para:
            out.append('<p>' + inline_md(' '.join(para)) + '</p>')
            para = []
        if lst:
            tag, items = lst
            out.append(f'<{tag}>' + ''.join(f'<li>{inline_md(i)}</li>' for i in items) + f'</{tag}>')
            lst = None
        if tbl:
            rows = [r for r in tbl if not re.match(r'^\|[\s:|-]+\|?$', r)]
            cells = [[c.strip() for c in r.strip().strip('|').split('|')] for r in rows]
            h = '<tr>' + ''.join(f'<th>{inline_md(c)}</th>' for c in cells[0]) + '</tr>'
            b = ''.join('<tr>' + ''.join(f'<td>{inline_md(c)}</td>' for c in r) + '</tr>' for r in cells[1:])
            out.append(f'<div class="tw"><table>{h}{b}</table></div>')
            tbl = []
    for line in text.split('\n'):
        s = line.rstrip()
        m = re.match(r'^(#{1,6})\s+(.*)', s)
        if m:
            flush()
            lv = min(6, len(m.group(1)) + hshift)
            out.append(f'<h{lv}>{inline_md(m.group(2))}</h{lv}>')
            continue
        if s.startswith('|'):
            if para or lst:
                p, t = para, tbl
                tbl = []
                flush()
                tbl = t
            tbl.append(s)
            continue
        elif tbl:
            flush()
        m = re.match(r'^\s*([-*]|\d+\.)\s+(.*)', s)
        if m:
            tag = 'ol' if m.group(1)[0].isdigit() else 'ul'
            if para:
                p = para
                flush()
            if lst and lst[0] != tag:
                flush()
            if not lst:
                lst = (tag, [])
            lst[1].append(m.group(2))
            continue
        if not s.strip():
            flush()
            continue
        if lst and line.startswith(' '):
            lst[1][-1] += ' ' + s.strip()
            continue
        if lst:
            flush()
        para.append(s.strip())
    flush()
    return '\n'.join(out)


def section_of(path, head_prefix):
    """The text of one ## section of a markdown file."""
    t = open(path, encoding='utf-8').read()
    parts = re.split(r'(?m)^## ', t)
    for p in parts:
        if p.startswith(head_prefix):
            return '## ' + p
    return ''


def entry(title, body, kind=None, sub='', cls='', ident=''):
    b = badge(kind) if kind else ''
    st = f' <span class="sub">{sub}</span>' if sub else ''
    i = f' id="{ident}"' if ident else ''
    return f'<article class="entry {cls}"{i}><h3>{title}{st}{b}</h3>{body}</article>'


SECTIONS = []      # (id, group, title, html)


def add(sid, group, title, intro, body):
    SECTIONS.append((sid, group, title, f'<header class="sh"><h2>{e(title)}</h2>{intro}</header>{body}'))


# ---------------------------------------------------------------- what is built where
def _git(*a):
    try:
        return subprocess.run(['git', *a], cwd=SRC, capture_output=True, text=True).stdout.strip()
    except OSError:
        return ''


BRANCH = (f"Built from branch {os.environ.get('GITHUB_REF_NAME') or _git('rev-parse', '--abbrev-ref', 'HEAD')}, "
          f"commit {_git('rev-parse', '--short', 'HEAD')}, on {datetime.date.today():%d %B %Y}.")

# ---------------------------------------------------------------- the great evils
STAGES = ', '.join(dict.fromkeys(EV.STAGES))
evil_html = []
for k, v in EV.EVILS.items():
    boss = D.MONSTERS.get(v['boss'], {})
    hunt = ', '.join(D.MONSTERS[h]['name'] for h in v['hunt'] if h in D.MONSTERS)
    cult = v.get('cult')
    rows = [('Names', ', '.join(v['names'])), ('Lair', v['lair'].replace('{short}', '…') + f" ({v['style']}, {v['depth']} levels deep)"),
            ('Lives in', ', '.join(v['terrain'])), ('Mark on the land', v['taint_name']),
            ('Sends after you', hunt + ' (hunters: ' + '; '.join(n.replace('{short}', '…') for n in v['hunt_names']) + ')')]
    sv = SHD.SERVANT[k]
    rows = [('Weight', f"{EV.WEIGHT[k]} ({SHD.WEIGHT_WORD[EV.WEIGHT[k]]})"), ('Wants', sv['goal']),
            ('Its lever on the realms', sv['lever'])] + rows
    rows.append(('Lieutenants (three of)', '; '.join(f"{t} ({D.MONSTERS[mk]['name']}, a {pl})" for t, mk, pl, _p in sv['lts'])))
    rows.append(('Weakness', f"{sv['weak'][0]}: {sv['weak'][2]}"))
    rows.append(('Relic', f"{sv['relic'][0]}: {sv['relic'][3]} (+{sv['relic'][2]} {sv['relic'][1]} while carried)"))
    if cult:
        rows.append(('Cult', f"{cult[0]}: {', '.join(D.MONSTERS[c]['name'] for c in cult[2] if c in D.MONSTERS)}; seats: {cult[3]}, {cult[4]}"))
    if boss:
        lvl = boss.get('lvl_fix', 10)
        rows.append(('Boss', f"{e(boss['name'])}, level {lvl}: life x{boss['hp']}, damage x{boss['dmg']}, defence x{boss['df']}"
                     + (f"; resists {', '.join(f'{a} {b}%' for a, b in boss['res'].items())}" if boss.get('res') else '')))
    dl = ''.join(f'<dt>{a}</dt><dd>{e(str(b))}</dd>' for a, b in rows)
    lists = ''
    for lab, key in (('Signs on the land', None), ('Whispers', 'whispers'), ('Rumours', 'rumors')):
        items = EV.SIGNS.get(v['taint'], []) if key is None else v[key]
        lists += f'<details><summary>{lab} ({len(items)})</summary><ul>' + ''.join(f'<li>{e(x)}</li>' for x in items) + '</ul></details>'
    body = (f'<p class="lead">{e(v["lore"][0].upper() + v["lore"][1:])}</p><dl class="kv">{dl}</dl>'
            f'<p class="quote">Omen: {e(v["omen"].replace("{name}", v["names"][0]))}</p>'
            f'<p class="quote">Defeat: {e(v["defeat"].replace("{name}", v["names"][0]))}</p>{lists}')
    evil_html.append(entry(f'<span class="glyph" style="color:{rgb(v["fg"])}">{e(boss.get("ch", "?"))}</span> {e(v["title"].title())}',
                           body, 'built', ident='evil-' + k))
intro = (f'<p>{e(SHD.__doc__.strip())}</p><p>{e(EV.__doc__.strip())}</p><p>They grow through these stages: {e(STAGES)}.</p>'
         f'<p>{e(SKY.__doc__.strip())}</p><p>The five floors of the Sky-Seat: {e(", ".join(SKY.FLOORS))}.</p>')
add('evils', 'World', 'The great evils', intro, '<div class="cards">' + ''.join(evil_html) + '</div>')

# ---------------------------------------------------------------- lore
h = '<ol class="hist">' + ''.join(f'<li>{e(x)}</li>' for x in LO.HISTORY) + '</ol>'
won = ''.join(entry(e(n), f'<p class="lead">{e(t[0])}</p><ul>' + ''.join(f'<li>{e(x)}</li>' for x in t[1]) + '</ul>', 'built')
              for n, t in LO.WONDERS.items())
add('history', 'Lore', 'History of the vale', '<p>What the people of the vale tell of the past (lore.py). The game also makes a fresh history for every world.</p>',
    entry('The old days, as folk tell them', h, 'built') + '<h3 class="gh">Wonders of the world</h3><div class="cards">' + won + '</div>')

if VT:
    # Varnish
    fr = ''.join(entry(e(hd), '<ul>' + ''.join(f'<li>{e(x)}</li>' for x in items) + '</ul>', 'built') for hd, items in VT.FRAGS.items())
    books = ''
    for b in VT.BOOKS:
        books += entry(e(b['title']), f'<p class="meta">Thread: {e(VT.THREADS.get(b["thread"], b["thread"]))} · found at: {e(", ".join(b["where"]))} · {len(b["pages"])} pages</p>'
                       + '<details><summary>Read the pages</summary><ol>' + ''.join(f'<li>{e(p)}</li>' for p in b['pages']) + '</ol></details>', 'built')
    rid = ''
    for r in VT.RIDDLES:
        fr_l = ''.join(f'<li class="{"false" if (f[2] is False) else ""}">{e(f[0])} <span class="meta">({e(str(f[1]))})</span></li>' for f in r['frags'])
        extra = ''.join(f'<p><strong>{e(k2.title())}:</strong> {e(str(v2))}</p>' for k2, v2 in r.items() if k2 not in ('key', 'title', 'gap', 'frags'))
        rid += entry(e(r['title']), f'<p class="lead">{e(r["gap"])}</p><details><summary>Spoiler: fragments and answer</summary><ul>{fr_l}</ul>{extra}</details>', 'built')
    places = ''.join(f'<dt>{e(VA.WHAT.get(k, k))}</dt><dd>{e(v)}</dd>' for k, v in VA.DESC.items())
    last = f'<details><summary>Spoiler: {e(VT.LAST[0])}</summary><p>{e(VT.LAST[1])}</p></details>'
    cities = ', '.join(VT.CITY_NAMES)
    add('varnish', 'Lore', 'The Varnish Empire',
        f'<p>The old empire: its ruined cities, the Northern Wall, the lore scraps, the bound books and the five riddles (varnish.py, varnishtexts.py). {badge("built")}</p>',
        entry('Places of the Varnish', f'<dl class="kv">{places}</dl><p class="meta">City names: {e(cities)}</p>'
              f'<p class="meta">City deep bosses: {e(", ".join(D.MONSTERS[b]["name"] for b in VA.CITY_BOSSES if b in D.MONSTERS))}</p>', 'built')
        + entry('The truth of the Ruin', last, 'built')
        + '<h3 class="gh">Lore scraps, by subject</h3><div class="cards">' + fr + '</div>'
        + f'<h3 class="gh">Bound books ({len(VT.BOOKS)})</h3><div class="cards">' + books + '</div>'
        + '<h3 class="gh">The five riddles</h3><div class="cards">' + rid + '</div>')

    op = ''.join(f'<dt>{e(OP.NAMED.get(k, k))}</dt><dd>{e(v)}</dd>' for k, v in OP.DESC.items())
    add('oldplaces', 'Lore', 'Old places', f'<p>Places left by history on the land (oldplaces.py). {badge("built")}</p>',
        entry('Old places on the land', f'<dl class="kv">{op}</dl><p class="meta">Small sights: {e(", ".join(OP.POI_NAMED.values()))}</p>', 'built'))

# ---------------------------------------------------------------- peoples and gods
peo = ''
names = [RC.RACES[r]['name'] for r in RC.RACE_ORDER]
for k in RC.RACE_ORDER:
    r = RC.RACES[k]
    st = ', '.join(f'{a} {b:+d}' for a, b in r['stats'].items() if b)
    rel = ', '.join(f'{RC.RACES[o]["plural"]} {v:+d}' for o, v in RC.RELATIONS[k].items() if o != k)
    body = (f'<p class="lead">{e(r["desc"])}</p><ul>' + ''.join(f'<li>{e(p)}</li>' for p in r['perks']) + '</ul>'
            + (f'<p class="meta">Stats: {e(st)}</p>' if st else '') + f'<p class="meta">Feelings toward others: {e(rel)}</p>'
            + ''.join(f'<p class="quote">{e(x)}</p>' for x in LO.RACE_LORE.get(k, [])))
    peo += entry(f'<span class="glyph" style="color:{rgb(r["fg"])}">@</span> {e(r["plural"])}', body, 'built')
add('peoples', 'World', 'Peoples', '<p>The peoples you can play and meet (races.py, lore.py). The hostile peoples are under Monsters.</p>',
    '<div class="cards">' + peo + '</div>')

gd = ''
for k in GODS.GOD_ORDER:
    g = GODS.GODS[k]
    opp = [GODS.GODS[o]['name'] for p in GODS.OPPOSED if k in p for o in p if o != k]
    fri = [GODS.GODS[o]['name'] for p in GODS.FRIENDS if k in p for o in p if o != k]
    body = (f'<dl class="kv"><dt>Domain</dt><dd>{e(g["domain"])}</dd><dt>Likes</dt><dd>{e(g.get("likes", ""))}</dd>'
            + (f'<dt>Blessings</dt><dd>{e(" / ".join(g["bless"]))}</dd>' if g.get('bless') else '')
            + f'<dt>Friends</dt><dd>{e(", ".join(fri) or "none")}</dd><dt>Opposed</dt><dd>{e(", ".join(opp) or "none")}</dd>'
            + f'<dt>Devotion</dt><dd>{"yes" if k in GODS.DEVOTABLE else "no, not for the player"}</dd></dl>'
            + ''.join(f'<p class="quote">{e(x)}</p>' for x in LO.GOD_LORE.get(k, [])))
    gd += entry(f'<span class="glyph" style="color:{rgb(g["fg"])}">†</span> {e(g["name"])}', body, 'built', sub=e(g['title']))
vg = VT.FRAGS.get('Gods', []) if VT else []
gd_old = entry('The gods in Varnish days', '<ul>' + ''.join(f'<li>{e(x)}</li>' for x in vg) + '</ul>', 'built') if vg else ''
add('gods', 'World', 'Gods', f'<p>{e(GODS.__doc__.strip())}</p>', '<div class="cards">' + gd + gd_old + '</div>')

# ---------------------------------------------------------------- factions and powers
fa = ''
for k, f in D.FACTIONS.items():
    tr = ', '.join(D.MONSTERS[t]['name'] for t in dict.fromkeys(f.get('troops', [])) if t in D.MONSTERS)
    en = ', '.join(D.FACTIONS[x]['short'] for x in f.get('enemies', []) if x in D.FACTIONS)
    fa += entry(f'<span class="glyph" style="color:{rgb(f["fg"])}">{e(FA.GLYPH.get(k, "?"))}</span> {e(f["name"])}',
                f'<p class="lead">{e(f.get("desc", ""))}</p><p class="meta">Troops: {e(tr)} · Enemies: {e(en)}</p>', 'built')
pw = ''
for k, p in PW.KINDS.items():
    tr = ', '.join(D.MONSTERS[t]['name'] for t in dict.fromkeys(p.get('troops', [])) if t in D.MONSTERS)
    pw += entry(e(p.get('label', k).capitalize()), f'<p class="meta">Leader: {e(p.get("title", ""))} · seat: {e(p.get("hall", ""))} · troops: {e(tr)}</p>'
                + (f'<p class="meta">Peoples: {e(", ".join(p["people"]))}</p>' if p.get('people') else ''), 'built')
add('factions', 'World', 'Factions and powers', f'<p>The realm factions (data.py) and the other powers (powers.py). Factions take a fresh name per world, e.g. from: {e(", ".join(FA.LANDS))}.</p>',
    '<h3 class="gh">Factions</h3><div class="cards">' + fa + '</div><h3 class="gh">Other powers</h3><div class="cards">' + pw + '</div>')

# ---------------------------------------------------------------- monsters
sys.path.insert(0, HERE)
import abilities as AB
import avarenthia.ai as AI
PREY = {'kick': ('Kicks', 'When hunted, it kicks out at you up close.'),
        'rocks': ('Flees to the rocks', 'When hunted, it makes for rocky ground.'),
        'skittish': ('Skittish', 'When hunted, it notices you from 3 tiles further off.'),
        'far': ('Runs far', 'When hunted, it runs two steps every other turn.'),
        'small': ('Small game', 'When hunted, it does not slow down when hurt.')}
TRAIT_OF = {'kite': 'kite', 'rage': 'berserk', 'charge': 'charge', 'burrow': 'lurk', 'ambush': 'lurk', 'hunt': 'wander',
            'disguise': 'lurk', 'pack': 'pack', 'leader': 'chief'}
USERS = {}      # ability label -> [monster keys]


def abilities(k, m):
    """[(label, text)] for one monster: its flags, the old traits and its behaviours."""
    out = []
    behs = sorted(str(b) for b in m['beh'])
    covered = {TRAIT_OF[b] for b in behs if b in TRAIT_OF}
    for f, (lab, txt) in AB.FLAGS.items():
        v = m.get(f)
        if not v or f in covered:
            continue
        if f == 'summon':
            txt = f"Calls a {D.MONSTERS.get(v, {}).get('name', v).lower()} beside it now and then (chiefs up to 4, bosses up to 6)."
        elif f == 'caster' or (f == 'ranged' and m.get('shot')):
            what = m.get('bolt') if f == 'caster' else m.get('shot')
            if what:
                txt = txt.replace('a bolt', 'a ' + what) if f == 'caster' else f'Shoots its {what} from 2-7 tiles away.'
        elif f == 'split':
            txt = f"When it dies, two to four young ({D.MONSTERS.get(v, {}).get('name', v).lower()}) spill out."
        out.append((lab, txt))
    for t, (lab, txt) in AB.TRAITS.items():
        if k in AI.TRAITS.get(t, ()) and t not in covered:
            out.append((lab, txt))
    for b in behs:
        lab, txt = AB.BEH.get(b, (b, ''))
        if b == 'gaze' and m.get('gaze') and m['gaze'] != 'any':
            txt = txt.replace('paralyses, confuses or frightens you', {'paralysed': 'paralyses you for 2 turns',
                              'confused': 'confuses you for 3 turns', 'afraid': 'frightens you for 6 turns'}.get(m['gaze'], m['gaze']))
        out.append((lab, txt))
    for f, (lab, txt) in PREY.items():
        if m.get(f):
            out.append((lab, txt))
    if m.get('elem'):
        out.append(('Element', f"Its attacks are {m['elem']}."))
    seen = set()
    res = []
    for lab, txt in out:
        if lab not in seen:
            seen.add(lab)
            res.append((lab, txt))
            USERS.setdefault((lab, txt if lab != 'Element' else 'Its attacks carry an element.'), []).append(k)
    return res


evil_boss = {v['boss']: v['title'] for v in EV.EVILS.values()}
groups = {}
for k, m in D.MONSTERS.items():
    fam = m.get('family') or ('boss' if m['boss'] else (m['tags'].split() or ['other'])[0])
    if m['boss']:
        fam = 'bosses and legends'
    groups.setdefault(fam, []).append(k)


def mstats(m):
    lvl = m.get('lvl_fix') or m.get('min_l', 1)
    hp = round((4 + lvl * 4.5) * m['hp'])
    d1, d2 = max(1, round((2 + lvl * 1.4) * m['dmg'])), max(2, round((4 + lvl * 2.8) * m['dmg']))
    df = round((3 + lvl * 3) * m['df'])
    xp = round((5 + lvl * lvl * 1.6) * m['xp'])
    return lvl, hp, f'{d1}-{d2}', df, xp


mon_html = ''
for fam in sorted(groups, key=lambda f: (f == 'bosses and legends', f)):
    cards = ''
    for k in sorted(groups[fam], key=lambda k: (D.MONSTERS[k].get('lvl_fix') or D.MONSTERS[k]['min_l'], D.MONSTERS[k]['name'])):
        m = D.MONSTERS[k]
        lvl, hp, dmg, df, xp = mstats(m)
        ab = abilities(k, m)
        lore = D.LORE.get(k)
        txt = ''
        if lore:
            txt += f'<p class="lead">{e(lore[0])}</p>'
        if D.DOES.get(k):
            txt += f'<p>{e(D.DOES[k])}</p>'
        if lore and len(lore) > 2:
            txt += f'<p class="meta">Tip: {e(lore[2])}</p>'
        res = BE.resists(k)
        try:
            car = BE.carries(k)
        except Exception:
            car = ''
        where = lore[1] if lore and len(lore) > 1 else m.get('home', '')
        extra = [x for x in (('Where: ' + where) if where else '', ('Elements: ' + res) if res else '', ('Carries: ' + car) if car else '',
                             ('Tags: ' + m['tags']) if m['tags'] else '') if x]
        if k in evil_boss:
            extra.insert(0, 'Boss of ' + evil_boss[k])
        stats = (f'<div class="stats"><span><b>Lvl</b> {lvl}{"" if m.get("lvl_fix") else "+"}</span><span><b>Life</b> {hp}</span><span><b>Dmg</b> {dmg}</span>'
                 f'<span><b>Def</b> {df}</span><span><b>XP</b> {xp}</span><span class="mult">x{m["hp"]} / x{m["dmg"]} / x{m["df"]}</span></div>')
        chips = ''.join(f'<li><b>{e(a)}</b> {e(t)}</li>' for a, t in ab)
        cards += (f'<article class="entry mon" id="m-{k}"><h3><span class="glyph" style="color:{rgb(m["fg"])}">{e(m["ch"])}</span> {e(m["name"])}'
                  f'<span class="sub">{e(k)}</span>{badge("built")}</h3>{stats}{txt}' + (f'<ul class="abil">{chips}</ul>' if chips else '')
                  + ''.join(f'<p class="meta">{e(x)}</p>' for x in extra) + '</article>')
    mon_html += f'<h3 class="gh">{e(fam.capitalize())} <span class="count">{len(groups[fam])}</span></h3><div class="cards">{cards}</div>'
add('monsters', 'Creatures', f'Monsters ({len(D.MONSTERS)})',
    '<p>Every creature in the code (data.py, creatures.py, menagerie.py and the rest). Stats are shown at the lowest level it appears '
    '(bosses at their fixed level): life = (4 + 4.5·lvl)·x, damage = (2 + 1.4·lvl)…(4 + 2.8·lvl)·x, defence = (3 + 3·lvl)·x. '
    'The three multipliers are life / damage / defence. A champion has 2.5× life and 1.25× damage; a unique 3.5× life and one or two of: '
    + e(', '.join(D.ELITE_MODS)) + '.</p>', mon_html)

ab_rows = ''
for (lab, txt), ks in sorted(USERS.items(), key=lambda kv: kv[0][0].lower()):
    who = ', '.join(f'<a href="#m-{x}">{e(D.MONSTERS[x]["name"])}</a>' for x in sorted(ks, key=lambda x: D.MONSTERS[x]['name']))
    ab_rows += entry(e(lab), f'<p>{e(txt)}</p><p class="meta">{len(ks)}: {who}</p>', 'built')
st_rows = ''.join(f'<dt>{e(a)}</dt><dd>{e(b)}</dd>' for a, b in AB.STATES.items())
add('abilities', 'Creatures', 'Monster abilities',
    '<p>Everything a monster can do beyond walking up and hitting you, and who does it (engine.py, ai.py, behave.py, rift.py). '
    'Dangerous moves are announced a turn ahead: a web weaver lifts its abdomen, a goblin lights a fuse. Step aside.</p>',
    entry('The states they leave you in', f'<dl class="kv">{st_rows}</dl>', 'built') + '<div class="cards">' + ab_rows + '</div>')

import avarenthia.bosses as BS
ROLE = {'k': 'small', 'V': 'set-up', 'G': 'great', 'Z': 'heaviest', 'B': 'move', 'O': 'summon', 'R': 'stance'}
bs_html = ''
for k, kt in BS.KITS.items():
    rows = ''
    for i, ph in enumerate(kt['phases']):
        at = f" from {round(ph['at'] * 100)}% life" if ph.get('at') else ''
        beat = ', '.join(ROLE[c] for c in ph['beat'])
        cards = '; '.join(f"{ROLE[r]}: " + ', '.join(sorted({BS.MOVES[m]['name'] for m in ms})) for r, ms in ph['cards'].items())
        rows += f'<dt>Phase {BS.ROMAN[i]}{e(at)}</dt><dd>Beat: {e(beat)}. {e(cards)}.</dd>'
    rows += f"<dt>Weakness</dt><dd>{e(', '.join(kt['weak']))}</dd>"
    kind = 'roaming' if kt.get('roam') else 'theme boss' if kt.get('theme') else 'fixed boss'
    bs_html += entry(D.MONSTERS[k]['name'], f'<dl class="kv">{rows}</dl>', 'built', sub=kind)
mv_rows = ''.join(f"<dt>{e(mv['name'])}</dt><dd>{e(ROLE[mv['role']])}; {e(mv.get('shape') or mv.get('kind'))}"
                  f"{'; loads ' + str(mv['load']) if mv.get('load') else ''}{'; ' + mv['elem'] if mv.get('elem') else ''}</dd>"
                  for k, mv in sorted(BS.MOVES.items(), key=lambda kv: kv[1]['name']) if mv.get('kind') != 'call')
bs_html += entry('The move library', f'<dl class="kv">{mv_rows}</dl>', 'built')
add('bossfights', 'Creatures', 'Boss fights',
    '<p>Bosses with a kit (bosses.py) fight in a rhythm drawn from a deck: each phase has a beat of roles and a few '
    'moves per role. Great blows are marked on the ground with a count; every marked blow leaves a free tile. '
    'At each threshold a blow stops and the room changes. After the heaviest blow the boss is spent.</p>',
    '<div class="cards">' + bs_html + '</div>')

tr = ''.join(f'<dt>{e(t)}</dt><dd>{e(NM.TRAIT_TEXT.get(t, ""))}</dd>' for t in NM.TRAITS)
hb = ''.join(f'<dt>{e(a)}</dt><dd>{e(b)}</dd>' for a, b in NM.HABITS.items())
add('named', 'Creatures', 'Named enemies', '<p>Monsters that make a name for themselves as notable, notorious and legendary (named.py).</p>',
    entry('Traits', f'<dl class="kv">{tr}</dl>', 'built') + entry('Habits', f'<dl class="kv">{hb}</dl>', 'built')
    + entry('Epithets', f'<p>{e(", ".join(NM.EPITHET))}</p><p class="meta">Beasts: {e(", ".join(NM.BEAST_NAME))}</p>', 'built'))

# ---------------------------------------------------------------- skills
lines = {}
for s in SK.SKILLS.values():
    if getattr(s, 'weapon_skill', False):
        continue
    lines.setdefault(s.line, []).append(s)
sk_html = ''
for line in SK.DISC_ORDER:
    if line not in lines:
        continue
    rows = ''
    for s in sorted(lines[line], key=lambda s: (s.guild or bool(s.flavor), s.unlock)):
        try:
            d = SK.describe(s, 1)
        except Exception:
            d = ''
        src = e(s.flavor) if s.flavor else f'tome, rank {s.unlock}'
        cost = 'passive' if s.passive else f'{s.cost} {"stamina" if s.dtype == "weapon" else "mana"}, {s.cd} turns'
        if getattr(s, 'epic', False):               # epics.py: from a hidden teacher, after a deed
            from avarenthia import epics as EP
            src = f'epic: {EP.TEACHERS[s.line][0]}, rank {EP.TEACH_AT}, after a deed'
            cost = 'once a day' if s.id == 'phoenix' else 'once per rest'
        rows += f'<tr class="entry"><td><span class="glyph" style="color:{rgb(s.color)}">{e(s.glyph)}</span> <b>{e(s.name)}</b></td><td>{src}</td><td>{e(cost)}</td><td>{e(s.mode)}</td><td>{e(d)}</td></tr>'
    sk_html += (f'<h3 class="gh">{e(SK.DISCIPLINES[line]["name"])} <span class="count">{len(lines[line])}</span></h3>'
                f'<div class="tw"><table class="skills"><tr><th>Skill</th><th>Learned from</th><th>Cost</th><th>Kind</th><th>At rank 1</th></tr>{rows}</table></div>')
add('skills', 'Skills', 'Schools and skills', '<p>All tome skills, guild techniques and epics (skills.py, epics.py), by school or discipline. Descriptions are the game\'s own text at rank 1.</p>', sk_html)

wl = {}
for s in WS.WSKILLS.values():
    wl.setdefault(getattr(s, 'kind', None) or s.line, []).append(s)
w_html = ''
for kind, ss in wl.items():
    rows = ''
    for s in ss:
        try:
            d = SK.describe(s, 1)
        except Exception:
            d = ''
        rows += f'<tr class="entry"><td><b>{e(s.name)}</b></td><td>{e(str(s.cost))} st, {s.cd} t</td><td>{e(d)}</td></tr>'
    w_html += f'<h3 class="gh">{e(str(kind).capitalize())}</h3><div class="tw"><table class="skills"><tr><th>Skill</th><th>Cost</th><th>At rank 1</th></tr>{rows}</table></div>'
add('weaponskills', 'Skills', 'Weapon skills', '<p>Keys 1-2 come from the weapon in hand (weaponskills.py): the first at once, the second from rank 10.</p>', w_html)

# ---------------------------------------------------------------- classes
pure = ''.join(f'<tr class="entry"><td><b>{e(n)}</b></td><td>{e(SK.DISCIPLINES[l]["name"])}</td><td>{e(TR.RULES.get(n, ("",))[0])}</td></tr>' for l, n in CL.PURE.items())
pairs = ''.join(f'<tr class="entry"><td><b>{e(n)}</b></td><td>{e(SK.DISCIPLINES[a]["name"])} + {e(SK.DISCIPLINES[b]["name"])}</td><td>{e(TR.RULES.get(n, ("",))[0])}</td></tr>' for a, b, n in CL._PAIRS)
trees = ''
for line, branches in TR.TREES.items():
    bh = ''
    for br in branches:
        bh += f'<div class="branch"><h4>{e(br[0])} <span class="sub">{e(br[1])}</span></h4><ol>'
        for kn in br[2]:
            txt = kn[6].replace('{n}', str(kn[5])) if len(kn) > 6 and kn[6] else ''
            bh += f'<li><b>{e(kn[1])}</b> <span class="meta">({kn[2]} pts)</span> {e(txt)}</li>'
        bh += '</ol></div>'
    trees += entry(e(CL.PURE.get(line, line)) + ' tree', f'<div class="branches">{bh}</div>', 'built', sub=e(SK.DISCIPLINES[line]['name']))
add('classes', 'Skills', 'Classes and trees',
    f'<p>A blank start; the first tome read gives the first class, a second class from rank {CL.SECOND_AT} gives a pair name with its own rule (classes.py, trees.py). '
    f'A tree point every {TR.EVERY} ranks; a temple takes points back for {TR.RESPEC // 100} silver each.</p>',
    f'<h3 class="gh">Pure classes</h3><div class="tw"><table><tr><th>Name</th><th>School</th><th>Rule</th></tr>{pure}</table></div>'
    f'<h3 class="gh">Pairs ({len(CL._PAIRS)})</h3><div class="tw"><table><tr><th>Name</th><th>Schools</th><th>Rule</th></tr>{pairs}</table></div>'
    f'<h3 class="gh">Trees</h3><div class="cards wide">{trees}</div>')

# ---------------------------------------------------------------- items
by_slot = {}
for k, b in ID.BASES.items():
    by_slot.setdefault(b['slot'], []).append(b)
it = ''
for slot, bs in by_slot.items():
    rows = ''
    for b in sorted(bs, key=lambda b: (b['family'], b['lvl'])):
        stat = f'{b["dmg"][0]}-{b["dmg"][1]} dmg' if b.get('dmg') else (f'{b.get("df", b.get("armor", ""))} def' if b.get('df') or b.get('armor') else '')
        req = ', '.join(f'{a[1:]} {b[a]}' for a in ('rstr', 'rdex') if b.get(a))
        rows += f'<tr class="entry"><td><b>{e(b["name"])}</b></td><td>{e(b["grade"])}</td><td>{b["lvl"]}</td><td>{e(stat)}</td><td>{e(req)}</td><td>{b["val"]}c</td></tr>'
    it += f'<h3 class="gh">{e(ID.SLOTNAME.get(slot, slot))} <span class="count">{len(bs)}</span></h3><div class="tw"><table><tr><th>Item</th><th>Grade</th><th>Lvl</th><th>Stat</th><th>Needs</th><th>Value</th></tr>{rows}</table></div>'


def afftxt(aff):
    out = []
    for a, v in aff.items():
        t = ID.AFFTXT.get(a, a + ' {}')
        val = f'{v[0]}-{v[1]}' if isinstance(v, tuple) else str(v)
        try:
            out.append(t.format(val))
        except Exception:
            out.append(f'{a} {val}')
    return out


un = ''.join(entry(f'<span style="color:{rgb(D.RARITY_COLOR.get(u.get("rar"), (217, 165, 71)))}">{e(u["name"])}</span>',
                   f'<p class="meta">{e(ID.BASES.get(u["base"], {}).get("name", u["base"]))}, level {u["lvl"]} · drops from: {e(", ".join(u.get("src", [])))}</p><ul>'
                   + ''.join(f'<li>{e(x)}</li>' for x in afftxt(u.get('aff', {}))) + '</ul>', 'built') for u in ID.UNIQUES)
st = ''.join(entry(e(s['name']), f'<p class="lead">{e(s.get("lore", ""))}</p><ul>' + ''.join(
    f'<li><b>{e(p[0])}</b> ({e(ID.BASES.get(p[1], {}).get("name", p[1]))}): {e(", ".join(afftxt(p[2])))}</li>' for p in s['pieces']) + '</ul>', 'built')
    for s in ID.SETS.values())
af = ''.join(f'<tr class="entry"><td>{e(a["stat"])}</td><td>{"prefix" if a.get("pre") else "suffix"}</td><td>{e(", ".join(a["slots"]))}</td><td>'
             + e(' · '.join(f'{t[1]} (lvl {t[0]}: {t[2]}-{t[3]})' for t in a['tiers'])) + '</td></tr>' for a in ID.AFFIXES)
pot = ''.join(f'<li><b style="color:{rgb(p["col"])}">{e(p["name"])}</b>, {p["val"]}c</li>' for p in D.POTIONS.values())
add('items', 'Gear', 'Items and gear', f'<p>Base items, uniques, sets and affixes (itemdata.py). Grades: {e(", ".join(ID.GRADES))}.</p>',
    it + f'<h3 class="gh">Uniques ({len(ID.UNIQUES)})</h3><div class="cards">{un}</div><h3 class="gh">Sets</h3><div class="cards">{st}</div>'
    f'<h3 class="gh">Affixes</h3><div class="tw"><table><tr><th>Stat</th><th>Kind</th><th>Slots</th><th>Tiers</th></tr>{af}</table></div>'
    f'<h3 class="gh">Potions</h3><ul>{pot}</ul>')

# ---------------------------------------------------------------- the life skills: herbs, drinks, fish, materials
import avarenthia.foraging as FGW
import avarenthia.brewing as BRW
import avarenthia.lifeskills as LSW
import avarenthia.crafts as CRW
hb_rows = ''.join(f'<tr class="entry"><td>{e(FGW.PLANTS[k][0])}</td><td>{v[0]}</td><td>{e(", ".join(dict.fromkeys(v[1])))}</td>'
                  f'<td>{e(v[2])}</td></tr>' for k, v in sorted(FGW.HERBS.items(), key=lambda kv: ('ABCDET'.index(kv[1][0]), kv[0])))
dr_rows = ''.join(f'<tr class="entry"><td>{e(v[0])}</td><td>{v[1]}</td><td>{e(", ".join(f"{c} {BRW.ing_name(kd, kk)}" for (kd, kk), c in v[2].items()))}</td>'
                  f'<td>{e(v[5] or "")}</td></tr>' for v in BRW.RECIPES.values())
fi_rows = ''.join(f'<tr class="entry"><td>{e(v[0])}</td><td>{v[6]}</td><td>{v[1]}</td><td>{e(v[2])}</td><td>{e(v[7])}</td></tr>'
                  for k, v in LSW.FISH.items() if k != 'legend')
mt_rows = ''.join(f'<tr class="entry"><td>{e(v[0])}</td><td>{v[1]}</td><td>{v[2]}</td></tr>'
                  for tab in (CRW.METALS, CRW.CLOTHS, CRW.LEATHERS) for v in tab.values())
import avarenthia.beastparts as BPW
import avarenthia.archaeology as ARW
ar_rows = ''.join(f'<tr class="entry"><td>{e(v[0])}</td><td>{v[1]}</td>'
                  f'<td>{", ".join(t for t, ks in ARW.BY_TIER.items() if k in ks)}</td></tr>' for k, v in ARW.FINDS.items())
bp_rows = ''.join(f'<tr class="entry"><td>{e(v[0])}</td><td>{e(str(v[1]))} {e(str(v[2]))}</td><td>{e(v[3])}</td></tr>'
                  for v in BPW.PART.values())
tp_rows = ''.join(f'<tr class="entry"><td>{e(k)}</td><td>{e(str(v))}</td></tr>' for k, v in BPW.TRAIT_POWER.items())
add('lifeskills', 'Skills', 'Life skills: herbs, drinks, fish, materials',
    f'<p>{e(LSW.__doc__.strip().splitlines()[0])} Tiers A-E and the top; the rank each tier needs: '
    f'{e(", ".join(f"{t} {r}" for t, r in LSW.TIER_RANK.items()))}. {badge("built")}</p>',
    f'<h3 class="gh">Herbs ({len(FGW.HERBS)})</h3><div class="tw"><table><tr><th>Herb</th><th>Tier</th><th>Properties</th><th>Where</th></tr>{hb_rows}</table></div>'
    f'<h3 class="gh">Drinks</h3><div class="tw"><table><tr><th>Drink</th><th>Rank</th><th>Made of</th><th>Whose</th></tr>{dr_rows}</table></div>'
    f'<h3 class="gh">Fish</h3><div class="tw"><table><tr><th>Fish</th><th>Tier</th><th>Rank</th><th>Water</th><th>Also</th></tr>{fi_rows}</table></div>'
    f'<h3 class="gh">Metals, cloth and leather</h3><div class="tw"><table><tr><th>Material</th><th>Tier</th><th>Rank</th></tr>{mt_rows}</table></div>'
    f'<h3 class="gh">Beast parts</h3><div class="tw"><table><tr><th>Part</th><th>Gives</th><th>On</th></tr>{bp_rows}</table></div>'
    f'<h3 class="gh">Named beasts\' parts</h3><div class="tw"><table><tr><th>Trait</th><th>Gives</th></tr>{tp_rows}</table></div>'
    f'<h3 class="gh">Archaeology: finds</h3><p>{e(ARW.__doc__.strip().splitlines()[0])}</p>'
    f'<div class="tw"><table><tr><th>Find</th><th>Worth (silver)</th><th>Tiers</th></tr>{ar_rows}</table></div>')

# ---------------------------------------------------------------- the handbook, from a real game
with contextlib.redirect_stdout(io.StringIO()):
    g = E.Game('Wiki', False, 1)


def hb_text(t):
    out = ''
    for part in re.split(HB.KEY_RE, str(t)):
        if part.startswith('[') and part.endswith(']'):
            out += f'<kbd>{e(part[1:-1])}</kbd>'
        elif part.startswith('{') and part.endswith('}'):
            ch = part[1:-1]
            out += f'<span class="glyph" style="color:{rgb(HB.sign_col(ch))}">{e(ch)}</span>'
        else:
            out += e(part)
    return out


hb_html = ''
for i, (name, fn) in enumerate(HB.CHAPTERS):
    try:
        blocks = fn(g)
    except Exception as ex:
        blocks = [('p', f'(could not render: {ex})')]
    body = ''
    for b in blocks:
        t = b[0]
        if t == 'p':
            body += f'<p>{hb_text(b[1])}</p>'
        elif t == 'h':
            body += f'<h4>{hb_text(b[1])}</h4>'
        elif t == 'n':
            body += f'<p class="tip">{hb_text(b[1])}</p>'
        elif t == 'k':
            body += f'<p><kbd>{e(str(b[1]))}</kbd> {hb_text(b[2])}</p>'
        elif t in ('l', 'o'):
            tag = 'ul' if t == 'l' else 'ol'
            body += f'<{tag}>' + ''.join(f'<li>{hb_text(x)}</li>' for x in b[1]) + f'</{tag}>'
        elif t == 'r':
            body += '<dl class="kv">' + ''.join(f'<dt>{hb_text(a)}</dt><dd>{hb_text(c)}</dd>' for a, c in b[1]) + '</dl>'
        elif t == 't':
            body += '<div class="tw"><table><tr>' + ''.join(f'<th>{hb_text(c)}</th>' for c in b[1]) + '</tr>' + ''.join(
                '<tr>' + ''.join(f'<td>{hb_text(c)}</td>' for c in r) + '</tr>' for r in b[2]) + '</table></div>'
        elif t == 's':
            body += '<dl class="kv signs">' + ''.join(f'<dt>{"".join(hb_text("{" + c + "}") if c.strip() else e(c) for c in str(gl))}</dt><dd>{hb_text(x)}</dd>' for gl, x in b[1]) + '</dl>'
    hb_html += entry(e(name), body, 'built', cls='book')
add('handbook', 'Rules', "The Adventurer's Handbook", '<p>The in-game handbook (<kbd>?</kbd>), every chapter, rendered from a fresh world. This is how the built game explains itself.</p>', hb_html)

# ---------------------------------------------------------------- built list, plan, open, design notes
DOCS = os.path.join(SRC, 'docs')
built = section_of(os.path.join(DOCS, 'built.md'), 'At a glance') + '\n' + section_of(os.path.join(DOCS, 'built.md'), 'Built\n')
add('built', 'Status', 'What is built', f'<p>From docs/built.md. {badge("built")}</p>', f'<div class="prose">{md(built)}</div>')
plan = open(os.path.join(DOCS, 'plan.md'), encoding='utf-8').read()
add('plan', 'Status', 'What is planned', f'<p>docs/plan.md in full: approved, not built yet. {badge("planned")}</p>', f'<div class="prose planned">{md(plan)}</div>')
op_ = open(os.path.join(DOCS, 'open.md'), encoding='utf-8').read() + '\n\n' + open(os.path.join(DOCS, 'parked.md'), encoding='utf-8').read()
add('open', 'Status', 'Open and parked', '<p>docs/open.md and docs/parked.md: still to discuss, or set aside.</p>', f'<div class="prose">{md(op_)}</div>')
for sid, fn, title in (('volken', 'poi/volken.md', 'Places of the peoples'), ('feest', 'poi/feestdagen.md', 'Holidays')):
    p = os.path.join(PF, fn)
    if os.path.exists(p):
        add(sid, 'Planned lore', title, f'<p>Design notes from the project files ({e(fn)}), approved into plan.md. {badge("planned")}</p>',
            f'<div class="prose planned">{md(open(p, encoding="utf-8").read())}</div>')

# ---------------------------------------------------------------- the page
ORDER = ['World', 'Lore', 'Creatures', 'Skills', 'Gear', 'Rules', 'Status', 'Planned lore']
SECTIONS.sort(key=lambda t: ORDER.index(t[1]))
nav = ''
grp = None
for sid, group, title, _h in SECTIONS:
    if group != grp:
        nav += f'<li class="ng">{e(group)}</li>'
        grp = group
    nav += f'<li><a href="#{sid}" data-s="{sid}">{e(title)}</a></li>'
secs = ''.join(f'<section id="{sid}" data-title="{e(title)}">{h_}</section>' for sid, _g, title, h_ in SECTIONS)
tpl = open(os.path.join(os.path.dirname(__file__), 'template.html'), encoding='utf-8').read()
page = tpl.replace('%%NAV%%', nav).replace('%%SECTIONS%%', secs).replace('%%NOTE%%', e(BRANCH)).replace('%%MONS%%', str(len(D.MONSTERS)))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'w', encoding='utf-8').write(page)
print(f'{OUT}: {len(page) // 1024} KB, {len(SECTIONS)} chapters')
