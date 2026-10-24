"""The debug menu's screens (F12, only when debug.ON): a tool for testing, in the game's own look. Letters pick,
Esc goes back a page, F12 closes. The rules behind each line are in debug.py."""
from . import data as D
from . import debug as DBG
from .canvas import wrap_text
from .ui import Modal, W, FG, DIM, GOLD, GOOD, BAD, INFO, PANEL

BOX_W, BOX_H = 104, 28
SEL_BG = (50, 40, 30)


class Page:
    title = 'Debug'

    def __init__(self, screen):
        self.screen = screen

    @property
    def game(self):
        return self.screen.game

    @property
    def app(self):
        return self.screen.app

    def render(self, cv, x, y):
        pass

    def on_key(self, tok, shift):
        """Return a Page to open, 'back', 'close' or None."""
        return None

    def help(self):
        return 'letter: choose · Esc: back · F12: close'


class MenuPage(Page):
    """Lettered lines in sections, in one or two columns: [(header, [(letter, label, action), ...]), ...]."""

    def __init__(self, screen, title, columns):
        super().__init__(screen)
        self.title = title
        self.columns = columns

    def actions(self):
        return {key: act for col in self.columns for _h, rows in col for key, _l, act in rows}

    def render(self, cv, x, y):
        cw = (BOX_W - 6) // max(1, len(self.columns))
        for c, col in enumerate(self.columns):
            yy = y + 2
            cx = x + 3 + c * cw
            for head, rows in col:
                cv.text(cx, yy, head, DIM, PANEL)
                yy += 1
                for key, label, _act in rows:
                    lab = label() if callable(label) else label
                    cv.text(cx, yy, key, GOLD, PANEL)
                    cv.text(cx + 3, yy, lab, FG, PANEL, maxw=cw - 4)
                    yy += 1
                yy += 1

    def on_key(self, tok, shift):
        act = self.actions().get(tok)
        return act() if act else None


class ListPage(Page):
    """A long list to search by typing: rows of (kind, name, value); Enter picks."""
    SHOW = 20

    def __init__(self, screen, title, rows, pick, note=None):
        super().__init__(screen)
        self.title = title
        self.rows = rows
        self.pick = pick
        self.note = note
        self.query = ''
        self.sel = 0

    def shown(self):
        q = self.query.lower()
        return [r for r in self.rows if q in r[1].lower() or q in r[0].lower()] if q else self.rows

    def render(self, cv, x, y):
        rows = self.shown()
        self.sel = max(0, min(self.sel, len(rows) - 1))
        cv.text(x + 3, y + 2, 'Search: ', DIM, PANEL)
        cv.text(x + 11, y + 2, self.query + '_', FG, (40, 32, 26))
        cv.text_right(x + BOX_W - 3, y + 2, f'{len(rows)} of {len(self.rows)}', DIM, PANEL)
        if self.note:
            cv.text(x + 40, y + 2, self.note(), INFO, PANEL, maxw=40)
        top = max(0, self.sel - self.SHOW + 3)
        for i, (kind, name, _v) in enumerate(rows[top:top + self.SHOW]):
            yy = y + 4 + i
            sel = top + i == self.sel
            bg = SEL_BG if sel else PANEL
            if sel:
                cv.fill(x + 2, yy, BOX_W - 4, 1, ' ', FG, bg)
            cv.text(x + 3, yy, kind, DIM, bg, maxw=24)
            cv.text(x + 29, yy, name, GOLD if sel else FG, bg, maxw=BOX_W - 33)
        if not rows:
            cv.text(x + 3, y + 4, 'Nothing fits.', DIM, PANEL)

    def help(self):
        return 'type to search · Up/Down: choose · Enter: take' + (' · Tab: grade' if self.note else '') + ' · Esc: back'

    def on_key(self, tok, shift):
        rows = self.shown()
        if tok in ('up', 'np8'):
            self.sel -= 1
        elif tok in ('down', 'np2'):
            self.sel += 1
        elif tok == 'pageup':
            self.sel -= self.SHOW
        elif tok == 'pagedown':
            self.sel += self.SHOW
        elif tok in ('enter', 'np_enter') and rows:
            return self.pick(rows[max(0, min(self.sel, len(rows) - 1))][2])
        elif tok == 'backspace':
            self.query = self.query[:-1]
            self.sel = 0
        elif tok == 'space':
            self.query += ' '
        elif len(tok) == 1 and (tok.isalnum() or tok in "-'"):
            self.query += tok
            self.sel = 0
        return None


class AskPage(Page):
    """One line to type: digits only, or any text. done(value) gives what to do next."""

    def __init__(self, screen, title, prompt, done, digits=True):
        super().__init__(screen)
        self.title, self.prompt, self.done, self.digits = title, prompt, done, digits
        self.text = ''

    def render(self, cv, x, y):
        n = cv.wrap(x + 3, y + 3, BOX_W - 6, self.prompt, FG, PANEL)
        cv.text(x + 3, y + 4 + n, self.text + '_', GOLD, (40, 32, 26))

    def help(self):
        return 'type · Enter: done · Esc: back'

    def on_key(self, tok, shift):
        if tok in ('enter', 'np_enter'):
            if self.digits:
                return self.done(int(self.text)) if self.text else None
            return self.done(self.text.strip())
        if tok == 'backspace':
            self.text = self.text[:-1]
        elif tok == 'space' and not self.digits:
            self.text += ' '
        elif len(tok) == 1 and (tok.isdigit() if self.digits else (tok.isprintable())) and len(self.text) < 80:
            self.text += tok
        return None


class DebugScreen(Modal):
    """F12: the debug menu over the game."""

    def __init__(self, app):
        super().__init__(app)
        self.pages = [self.root()]

    # ------------------------------------------------------------ the pages
    def flag(self, f):
        return lambda: f"{DBG.FLAG_NAME[f]}: {'on' if DBG.has(self.game, f) else 'off'}"

    def do(self, fn, close=False):
        """An action that runs and then stays on the page (or closes the menu)."""
        def act():
            fn()
            return 'close' if close else None
        return act

    def root(self):
        g = lambda: self.game  # noqa: E731
        left = [
            ('MOMENTS', [('a', 'Save a snapshot...', lambda: self.snap_page(True)),
                         ('b', 'Load a snapshot...', lambda: self.snap_page(False)),
                         ('r', 'Write a bug report...', self.report_page)]),
            ('THE WORLD', [('m', 'Show the whole map', self.do(lambda: DBG.reveal_map(g()))),
                           ('t', 'Teleport...', self.teleport_page),
                           ('d', 'Time...', self.time_page),
                           ('w', 'Weather...', self.weather_page),
                           ('s', 'Spawn a creature...', self.spawn_page),
                           ('z', 'Theme room or river...', self.theme_page),
                           ('T', 'Hear the tale of an older place', self.do(lambda: DBG.old_tale(g()), True)),
                           ('F', 'Change who holds this fort', self.do(lambda: DBG.fort_holder(g()), True)),
                           ('k', 'Kill all in sight', self.do(lambda: DBG.kill_in_sight(g()), True))]),
            ('LOOKING', [('v', self.flag('sight'), self.do(lambda: DBG.toggle(g(), 'sight'))),
                         ('o', self.flag('ai'), self.do(lambda: DBG.toggle(g(), 'ai'))),
                         ('u', self.flag('coords'), self.do(lambda: DBG.toggle(g(), 'coords')))]),
        ]
        right = [
            ('THE PLAYER', [('g', self.flag('god'), self.do(lambda: DBG.toggle(g(), 'god'))),
                            ('h', 'Full health', self.do(lambda: DBG.full_health(g()))),
                            ('c', 'Coin...', self.coin_page),
                            ('x', 'One level up', self.do(lambda: DBG.level_up(g(), 1))),
                            ('X', 'Five levels up', self.do(lambda: DBG.level_up(g(), 5))),
                            ('n', 'Skill ranks...', self.rank_page),
                            ('p', 'Rested here: spend tree points', self.do(lambda: DBG.rested(g()))),
                            ('i', 'Give an item...', self.item_page),
                            ('y', 'Identify all you carry', self.do(lambda: g().identify_all()))]),
            ('THE REST', [('j', 'Jobs...', self.job_page),
                          ('e', 'Force an event...', self.event_page),
                          ('f', 'Standing...', self.standing_page),
                          ('q', 'Guild rank...', self.guild_page),
                          ('l', 'Add a hireling...', self.hireling_page)]),
        ]
        return MenuPage(self, 'Debug', [left, right])

    def snap_page(self, saving):
        rows = []
        for i in range(1, DBG.SLOTS + 1):
            info = DBG.snap_info(i) or 'empty'
            if saving:
                rows.append((str(i), f'{i}  {info}', self.do(lambda i=i: DBG.save_snapshot(self.game, i))))
            else:
                rows.append((str(i), f'{i}  {info}', lambda i=i: self.load_snap(i)))
        return MenuPage(self, 'Save a snapshot' if saving else 'Load a snapshot',
                        [[('PICK A SLOT', [(k, lab[3:], act) for k, lab, act in rows])]])

    def load_snap(self, i):
        g = DBG.load_snapshot(i)
        if g is None:
            self.game.msg(f'Debug: snapshot {i} is empty or of an older version.', 'bad')
            return None
        self.app.start_game(g)
        g.compute_fov()
        g.msg(f'Debug: snapshot {i} loaded.', 'info')
        return 'close'

    def report_page(self):
        def done(note):
            DBG.bug_report(self.app, note)
            return 'close'
        return AskPage(self, 'Write a bug report', 'What went wrong? One line, in any words (Enter alone writes it without).',
                       done, digits=False)

    def teleport_page(self):
        rows = sorted(DBG.places(self.game), key=lambda r: (r[0], r[1]))

        def pick(act):
            DBG.teleport(self.game, act)
            return 'close'
        return ListPage(self, 'Teleport', rows, pick)

    def time_page(self):
        from . import calendar as CAL
        g = lambda: self.game  # noqa: E731
        months = [(str(i + 1), name, i) for i, name in enumerate(CAL.MONTHS)]

        def month_list():
            return ListPage(self, 'To the first day of...', months, lambda mo: (DBG.to_month(g(), mo), 'close')[1])
        return MenuPage(self, 'Time', [[('TIME RUNS ON', [
            ('a', 'Six hours', self.do(lambda: DBG.days_ahead(g(), .25))),
            ('b', 'One day', self.do(lambda: DBG.days_ahead(g(), 1))),
            ('c', 'A week', self.do(lambda: DBG.days_ahead(g(), 7))),
            ('d', 'A month', self.do(lambda: DBG.days_ahead(g(), 30))),
            ('e', 'A season', self.do(lambda: DBG.days_ahead(g(), 90))),
            ('f', 'To the first day of a month...', month_list)])]])

    def weather_page(self):
        from . import weather as WX
        rows = [(v[1], v[0], k) for k, v in WX.KINDS.items()]
        return ListPage(self, 'Weather', rows, lambda k: (DBG.set_weather(self.game, k), 'close')[1])

    def spawn_page(self):
        rows = sorted(((('boss' if d.get('boss') else d.get('tags', '').split(' ')[0] or 'creature'), d['name'], k)
                       for k, d in D.MONSTERS.items() if k != 'npc'), key=lambda r: r[1])
        return ListPage(self, 'Spawn a creature', rows, lambda k: (DBG.spawn(self.game, k), 'close')[1])

    def coin_page(self):
        g = lambda: self.game  # noqa: E731
        return MenuPage(self, 'Coin', [[('ADD TO YOUR PURSE', [
            ('a', '1 gold', self.do(lambda: DBG.give_coin(g(), 100 * 100))),
            ('b', '10 gold', self.do(lambda: DBG.give_coin(g(), 10 * 100 * 100))),
            ('c', '100 gold', self.do(lambda: DBG.give_coin(g(), 100 * 100 * 100))),
            ('d', 'Empty your purse', self.do(lambda: setattr(g().player, 'gold', 0)))])]])

    def rank_page(self):
        p = self.game.player

        def rank_of(key, kind):
            return (p.disc if kind == 'disc' else p.life_sk).get(key, [0])[0]
        rows = [('weapon or school' if kind == 'disc' else 'life skill', f'{name} (now {rank_of(key, kind)})', (key, kind, name))
                for key, name, kind in DBG.skill_lines()]

        def pick(v):
            key, kind, name = v
            return AskPage(self, f'{name}: rank', f'The new rank of {name}, 0 to 100:',
                           lambda r: (DBG.set_rank(self.game, key, kind, r), 'back')[1])
        return ListPage(self, 'Skill ranks', rows, pick)

    def item_page(self):
        state = {'rar': 'normal'}
        page = ListPage(self, 'Give an item', DBG.item_list(), lambda v: DBG.give(self.game, v, state['rar']) and None,
                        note=lambda: f"gear comes as: {state['rar']}")
        base_key = page.on_key

        def on_key(tok, shift):
            if tok == 'tab':
                state['rar'] = DBG.RARITIES[(DBG.RARITIES.index(state['rar']) + 1) % len(DBG.RARITIES)]
                return None
            return base_key(tok, shift)
        page.on_key = on_key
        return page

    def job_page(self):
        from . import missions as MS
        g = self.game
        rows = [('your job', mi.title, ('job', mi.id)) for mi in MS.active(g)]
        rows += [('make a job', kind, ('make', kind)) for kind in DBG.job_kinds()]

        def pick(v):
            if v[0] == 'make':
                DBG.make_job(self.game, v[1])
                return 'back'
            mi = MS.find(self.game, v[1])
            if not mi:
                return None
            return MenuPage(self, mi.title, [[('THIS JOB', [
                ('a', 'Finish it now', lambda: (DBG.finish_job(self.game, mi, True), 'close')[1]),
                ('b', 'Let it fail', lambda: (DBG.finish_job(self.game, mi, False), 'close')[1])])]])
        return ListPage(self, 'Jobs', rows, pick)

    def event_page(self):
        rows = [('event', label, k) for k, label in DBG.EVENTS]
        return ListPage(self, 'Force an event', rows, lambda k: (DBG.force_event(self.game, k), 'close')[1])

    def standing_page(self):
        p = self.game.player
        rows = [('faction', f"{fd['name']} (now {p.rep.get(f, 0)})", f) for f, fd in D.FACTIONS.items()]

        def pick(f):
            vals = [('a', -100), ('b', -50), ('c', 0), ('d', 25), ('e', 50), ('f', 100)]
            return MenuPage(self, D.FACTIONS[f]['name'], [[('SET THE STANDING TO', [
                (k, str(v), lambda v=v: (DBG.set_standing(self.game, f, v), 'back')[1]) for k, v in vals])]])
        return ListPage(self, 'Standing', rows, pick)

    def guild_page(self):
        from . import guilds as GU
        rows = [('guild', f"{GU.GUILDS[k]['name']} (now {GU.rank_name(self.game, k)})", k) for k in GU.ORDER]

        def pick(k):
            return MenuPage(self, GU.GUILDS[k]['name'], [[('JOIN AT THE RANK', [
                (str(r + 1), n, lambda r=r: (DBG.set_guild(self.game, k, r), 'back')[1])
                for r, n in enumerate(GU.GUILDS[k]['ranks'])])]])
        return ListPage(self, 'Guild rank', rows, pick)

    def theme_page(self):
        from . import pieces as PC
        rows = [('river', 'a river of water', 'river:water'), ('river', 'a river of fire', 'river:fire')] + \
            [(pc.part, f'{pc.name}: {pc.shape or pc.part}', pc.name) for pc in PC.load()]
        return ListPage(self, 'Theme room or river', rows, lambda k: (DBG.theme_level(self.game, k), 'close')[1])

    def hireling_page(self):
        from . import mercs as MC
        rows = [('hireling', v['name'], k) for k, v in MC.KINDS.items() if k != 'beast']
        return ListPage(self, 'Add a hireling', rows, lambda k: (DBG.add_hireling(self.game, k), 'close')[1])

    # ------------------------------------------------------------ drawing and keys
    def render(self, cv):
        page = self.pages[-1]
        x, y = self.box(cv, BOX_W, BOX_H, f' {page.title} ')
        page.render(cv, x, y)
        g = self.game
        if g.log:
            last, cls = g.log[-1]
            if last.startswith('Debug:'):
                col = BAD if cls == 'bad' else GOOD
                for i, ln in enumerate(wrap_text(last, BOX_W - 6)[:2]):
                    cv.text(x + 3, y + BOX_H - 4 + i, ln, col, PANEL)
        cv.text_center(W // 2, y + BOX_H - 1, f' {page.help()} ', DIM, PANEL)

    def on_key(self, tok, shift):
        if tok == 'f12':
            self.app.pop()
            return
        if tok == 'esc':
            if len(self.pages) > 1:
                self.pages.pop()
            else:
                self.app.pop()
            return
        res = self.pages[-1].on_key(tok, shift)
        if res == 'close':
            if self in self.app.screens:
                self.app.screens.remove(self)
        elif res == 'back':
            if len(self.pages) > 1:
                self.pages.pop()
                self.pages[-1] = self.refresh(self.pages[-1])
        elif isinstance(res, Page):
            self.pages.append(res)

    def refresh(self, page):
        """A list whose numbers changed (ranks, standing) is made again on the way back."""
        for make in (self.rank_page, self.standing_page, self.guild_page, self.job_page):
            if page.title == make().title:
                return make()
        return page
