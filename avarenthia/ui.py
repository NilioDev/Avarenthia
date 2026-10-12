"""Screens, rendering and input handling. Independent of tcod: it draws on a Canvas
and receives key tokens ('a', 'A', 'up', 'np7', 'enter', 'esc', '>' ...)."""
import random
import time

from . import data as D
from . import economy as ECO
from . import engine as E
from . import events as EV
from . import look as LOOK
from .money import fmt
from . import calendar as CAL
from . import dress as DR
from . import evils as EVL
from . import weather as WX
from . import missions as MS
from . import skills as SK
from . import towns as TW
from . import war as WAR
from .canvas import scale, mix, wrap_text, TallCanvas
from .data import DOWN, UP, TOWN, ENTR, WALL
from .worldgen import cheb

W, H = 110, 60          # square 8x8 cells: 880 x 480 pixels before scaling
MAP_W, MAP_H = 80, 51
LOG_Y = 52
PX = 82                 # panel x
PW = W - PX - 1         # panel width

BG = (13, 11, 10)
PANEL = (22, 18, 15)
LINE = (58, 46, 34)
FG = (221, 211, 189)
DIM = (143, 133, 115)
GOLD = (217, 165, 71)
BLOOD = (196, 58, 44)
MANA = (60, 99, 200)
GOOD = (134, 196, 111)
INFO = (136, 182, 220)
BAD = (236, 106, 92)
LOGCOL = {'talk': (200, 190, 160), '': FG, 'bad': BAD, 'good': GOOD, 'info': INFO, 'gold': GOLD,
          'magic': D.RARITY_COLOR['magic'], 'rare': D.RARITY_COLOR['rare'], 'unique': D.RARITY_COLOR['unique'], 'normal': FG}

DIRS = {'up': (0, -1), 'down': (0, 1), 'left': (-1, 0), 'right': (1, 0),
        'k': (0, -1), 'j': (0, 1), 'h': (-1, 0), 'l': (1, 0), 'y': (-1, -1), 'u': (1, -1), 'b': (-1, 1), 'n': (1, 1),
        'np8': (0, -1), 'np2': (0, 1), 'np4': (-1, 0), 'np6': (1, 0), 'np7': (-1, -1), 'np9': (1, -1), 'np1': (-1, 1), 'np3': (1, 1),
        'home': (-1, -1), 'pageup': (1, -1), 'end': (-1, 1), 'pagedown': (1, 1)}
RUN_LETTERS = {'K': 'k', 'J': 'j', 'H': 'h', 'L': 'l', 'Y': 'y', 'U': 'u', 'B': 'b', 'N': 'n'}
LETTERS = 'abcdefghijklmnopqrstuvwx'

ROOFED = {D.FLOOR, D.PLANK, D.BED, D.TABLE, D.BARREL, D.ALTAR, D.ANVIL, D.DOOR, D.ODOOR}
ORB_MASK = ['  #####  ', ' ####### ', '#########', '#########', '#########', '#########', '#########', ' ####### ', '  #####  ']


class App:
    def __init__(self, canvas):
        self.cv = canvas
        self.game = None
        self.running = True
        self.screens = [MainMenu(self)]
        self.effects = []          # (kind, t0, payload)
        self.hit_times = {}
        self.shake_until = 0
        self.hover = None
        self.reduced_motion = False
        self.auto = None           # a running step-by-step action (auto-explore, travel)
        self.auto_delay = .06
        self.auto_label = ''

    # ---------------------------------------------------------- plumbing
    @property
    def top(self):
        return self.screens[-1]

    def push(self, s):
        self.screens.append(s)

    def pop(self):
        if len(self.screens) > 1:
            self.screens.pop()

    def replace(self, s):
        self.screens[-1] = s

    def start_game(self, game):
        self.game = game
        self.effects.clear()
        self.screens = [GameScreen(self)]
        E.save_game(game)

    def quit(self):
        if self.game and not self.game.dead:
            E.save_game(self.game)
        self.running = False

    def animating(self):
        t = time.monotonic()
        return bool(self.effects) or self.shake_until > t or any(t - v < .15 for v in self.hit_times.values())

    def frame_delay(self):
        """How soon to draw the next frame without a key press: fast while effects play, slowly for the
        living world (flickering fires, twinkling stars), or never (None) when nothing moves."""
        if self.animating():
            return 1 / 30
        top = self.top
        if getattr(top, 'ambient', False):
            return 1 / 10
        g = self.game
        if g and isinstance(top, GameScreen):
            m = g.map
            if getattr(top, 'marks', False) or getattr(top, 'weather', 'clear') != 'clear':
                return 1 / 10
            if getattr(m, 'lights', None) and (m.kind == 'dungeon' or getattr(m, 'underground', False)
                                                or (m.kind == 'town' and TW.lamp_light(g) > 0)):
                return 1 / 10
        return None

    def key(self, tok, shift=False):
        if self.auto:
            self.stop_auto()           # any key interrupts auto-explore or travel
            return
        self.top.on_key(tok, shift)
        self.after_action()

    def start_auto(self, gen, delay, label):
        self.auto, self.auto_delay, self.auto_label = gen, delay, label
        self.tick()

    def stop_auto(self):
        if self.auto:
            self.auto.close()
        self.auto = None

    def tick(self):
        """Advance a running auto action by one step."""
        if not self.auto:
            return
        try:
            next(self.auto)
        except StopIteration:
            self.auto = None
        self.after_action()
        if self.game and (self.game.dead or not isinstance(self.top, GameScreen)):
            self.stop_auto()

    def run_auto(self, limit=2000):
        """Finish a running auto action at once (tests)."""
        while self.auto and limit:
            self.tick()
            limit -= 1

    def click(self, tx, ty, button=1):
        self.top.on_click(tx, ty, button)
        self.after_action()

    def after_action(self):
        g = self.game
        if not g:
            return
        now = time.monotonic()
        for ev in g.events:
            if ev[0] == 'shake':
                if not self.reduced_motion:
                    self.shake_until = now + .12
            elif ev[0] == 'speech':
                self.effects = [e for e in self.effects if e[0] != 'speech']
                self.effects.append(('speech', now, ev))
            else:
                self.effects.append((ev[0], now, ev))
        g.events.clear()
        for m in g.map.mons:
            if m.hit_flash:
                self.hit_times[m.id] = now
                m.hit_flash = 0
        req, g.request = g.request, None
        if g.dead and not isinstance(self.top, DeathScreen):
            E.delete_save()
            self.screens = [GameScreen(self), DeathScreen(self)]
            return
        if not req:
            return
        if req[0] == 'save':
            E.save_game(g)
        elif req[0] == 'shop':
            self.push(ShopScreen(self, req[1]))
        elif req[0] == 'market':
            self.push(MarketScreen(self, req[1]))
        elif req[0] == 'inn':
            self.push(BoardScreen(self, req[1]))
        elif req[0] == 'stables':
            self.push(StablesScreen(self))
        elif req[0] == 'temple':
            self.push(TempleScreen(self, req[1]))
        elif req[0] == 'castellan':
            self.push(BoardScreen(self, req[1], hold=True))
        elif req[0] == 'dialog':
            self.push(DialogScreen(self, req[1], req[2]))
        elif req[0] == 'choice':
            if g.pending:
                self.push(ChoiceScreen(self))
        elif req[0] == 'talkpick':
            self.push(TalkScreen(self, req[1]))
        elif req[0] == 'win':
            E.save_game(g)
            self.push(WinScreen(self))

    def render(self):
        cv = self.cv
        cv.clear(BG)
        # find the deepest opaque screen and draw from there
        start = 0
        for i, s in enumerate(self.screens):
            if not s.overlay:
                start = i
        for i, s in enumerate(self.screens[start:]):
            if s.overlay and getattr(s, 'dim', True):
                cv.dim(.35)
            s.render(TallCanvas(cv) if s.tall else cv)
        t = time.monotonic()
        self.effects = [e for e in self.effects if t - e[1] < (e[2][4] if e[0] == 'flash' else 2.5 if e[0] == 'speech' else .8)]
        self.hit_times = {k: v for k, v in self.hit_times.items() if t - v < .15}


class Screen:
    overlay = False
    tall = False        # laid out in text rows: drawn with every row doubled (see TallCanvas)

    def __init__(self, app):
        self.app = app

    @property
    def game(self):
        return self.app.game

    def render(self, cv):
        pass

    def on_key(self, tok, shift):
        pass

    def on_click(self, x, y, button):
        pass


# ====================================================================== main menu
GAME_TITLE = 'AVARENTHIA'
SUBTITLE = 'Tales of Fortune, Fame and Folly'
AUTHOR = 'Nilio'


class MainMenu(Screen):
    ambient = True          # the title picture moves a little: stars, water
    def __init__(self, app):
        super().__init__(app)
        self.saved = E.load_game()
        self._bg = None

    def render(self, cv):
        """The emblem of Avarenthia on a night sky full of slowly twinkling stars."""
        import math
        from . import logo as LG
        t = time.monotonic()
        night = (8, 6, 6)
        cv.fill(0, 0, cv.w, cv.h, ' ', None, night)
        if self._bg is None:
            rnd = random.Random(7)
            self._bg = [(rnd.randrange(cv.w), rnd.randrange(cv.h), rnd.random()) for _ in range(260)]
        for sx, sy, k in self._bg:
            tw = .5 + .5 * math.sin(t * (1.1 + k * 2.6) + k * 50)
            ch = '+' if k > .94 and tw > .75 else '·' if k > .5 else '∙'
            col = mix((40, 36, 50), (255, 248, 225) if k < .85 else (200, 220, 255), (.25 + .75 * tw) * (.4 + .6 * k))
            cv.put(sx, sy, ch, col, night)
        x0, y0 = (cv.w - LG.W) // 2, 2
        for x, y, ch, col, shine, edge in LG.CELLS:
            bg = (2, 1, 1) if edge else night
            if ch == ' ':
                cv.put(x0 + x, y0 + y, ' ', None, bg)
                continue
            k = .5 + .5 * math.sin(x * .12 - t * 2.0)                     # a slow shimmer across the gold
            cv.put(x0 + x, y0 + y, ch, mix(col, (255, 250, 225), .22 * k * shine / 100), bg)
        sub = f'·  {SUBTITLE}  ·'
        sx, sy = (cv.w - len(sub)) // 2, y0 + LG.SUBTITLE_ROW
        for j, c in enumerate(sub):
            if c == ' ' and cv.get(sx + j, sy)[0] not in (' ', '·', '∙', '+'):
                continue                                   # the blade passes behind the words
            cv.put(sx + j, sy, c, (236, 206, 150), night)
        # the menu, centred under the emblem
        opts = self.options()
        self.sel = min(getattr(self, 'sel', 0), len(opts) - 1)
        bw = max(len(o[1]) for o in opts) + 10
        bx, by = (cv.w - bw) // 2, min(cv.h - len(opts) * 2 - 3, y0 + LG.H + 1)
        for k, (key, lab, col) in enumerate(opts):
            yy = by + k * 2
            if k == self.sel:
                cv.fill(bx, yy, bw, 1, ' ', None, (52, 40, 28))
                cv.text(bx + 2, yy, '►', GOLD, (52, 40, 28))
                cv.text(bx + (bw - len(lab)) // 2, yy, lab, GOLD, (52, 40, 28))
                cv.text(bx + bw - 3, yy, '◄', GOLD, (52, 40, 28))
            else:
                cv.fill(bx, yy, bw, 1, ' ', None, night)
                cv.text(bx + (bw - len(lab)) // 2, yy, lab, col, night)
        credit = f'a game by {AUTHOR}'
        cv.text(cv.w - len(credit) - 2, cv.h - 2, credit, (150, 136, 120), night)

    def options(self):
        opts = []
        if self.saved:
            p = self.saved.player
            opts.append(('c', f"Continue as {p.name}, level {p.lvl}", FG))
        opts += [('n', 'New game', FG), ('esc', 'Quit', DIM)]
        return opts

    def on_key(self, tok, shift):
        opts = self.options()
        if tok in ('up', 'np8', 'k'):
            self.sel = (getattr(self, 'sel', 0) - 1) % len(opts)
            return
        if tok in ('down', 'np2', 'j'):
            self.sel = (getattr(self, 'sel', 0) + 1) % len(opts)
            return
        if tok in ('enter', 'space', 'np_enter'):
            tok = opts[getattr(self, 'sel', 0)][0]
        if tok == 'c' and self.saved:
            g = self.saved
            g.msg('Welcome back.', 'info')
            g.log_mark = len(g.log) - 1
            self.app.start_game(g)
        elif tok == 'n':
            self.app.replace(NameScreen(self.app))
        elif tok == 'esc':
            self.app.quit()


class NameScreen(Screen):
    tall = True
    """Character creation: name, people and gender."""
    ROWS = ['Name', 'People', 'Gender']

    def __init__(self, app):
        super().__init__(app)
        from . import races as RC
        self.RC = RC
        self.name = ''
        self.race = 0
        self.gender = 2
        self.sel = 0

    @property
    def race_key(self):
        return self.RC.RACE_ORDER[self.race]

    def render(self, cv):
        RC = self.RC
        cv.text_center(W // 2, 3, 'Who are you, wanderer?', GOLD)
        x0, y0 = 14, 7
        vals = [(self.name + ('_' if self.sel == 0 else '')).ljust(28),
                f"◄ {RC.RACES[self.race_key]['name']} ►", f"◄ {RC.GENDER_NAME[RC.GENDERS[self.gender]]} ►"]
        for i, (lab, v) in enumerate(zip(self.ROWS, vals)):
            y = y0 + i * 3
            sel = i == self.sel
            cv.text(x0, y, ('► ' if sel else '  ') + lab, GOLD if sel else FG)
            cv.text(x0 + 12, y, v, FG, (40, 32, 26) if i == 0 else None)
        cv.text(x0 + 12, y0 + 1, 'Tab: a random name for your people', DIM)
        r = RC.RACES[self.race_key]
        rx = 58
        cv.text(rx, y0, r['name'], r['fg'])
        n = cv.wrap(rx, y0 + 2, 46, r['desc'], FG)
        yy = y0 + 3 + n
        mods = ', '.join(f"{'+' if v > 0 else ''}{v} {k}" for k, v in r['stats'].items() if v) or 'no attribute changes'
        cv.text(rx, yy, mods, INFO)
        yy += 2
        for pk in r['perks']:
            cv.text(rx, yy, '• ' + pk, GOOD if 'more' not in pk and 'charge' not in pk else BAD, maxw=46)
            yy += 1
        yy += 1
        likes = [(RC.RACES[o]['plural'], v) for o, v in RC.RELATIONS.items() if o != self.race_key and RC.relation(o, self.race_key)]
        for nm, _v in likes:
            v = RC.relation([k for k in RC.RACES if RC.RACES[k]['plural'] == nm][0], self.race_key)
            cv.text(rx, yy, f"{nm} {'like' if v > 0 else 'distrust' if v > -15 else 'despise'} you", GOOD if v > 0 else BAD)
            yy += 1
        cv.text_center(W // 2, 28, 'Up/Down: choose a line · Left/Right: change · type your name · Enter: continue · Esc: back', DIM)

    def on_key(self, tok, shift):
        RC = self.RC
        if tok == 'enter':
            name = self.name.strip() or RC.random_name(self.race_key, RC.GENDERS[self.gender])
            self.app.replace(OptionsScreen(self.app, name, self.race_key, RC.GENDERS[self.gender]))
        elif tok == 'esc':
            self.app.replace(MainMenu(self.app))
        elif tok in ('up', 'np8'):
            self.sel = (self.sel - 1) % 3
        elif tok in ('down', 'np2'):
            self.sel = (self.sel + 1) % 3
        elif tok in ('left', 'right', 'np4', 'np6') and self.sel:
            d = -1 if tok in ('left', 'np4') else 1
            if self.sel == 1:
                self.race = (self.race + d) % len(RC.RACE_ORDER)
            else:
                self.gender = (self.gender + d) % 3
        elif tok == 'tab':
            self.name = RC.random_name(self.race_key, RC.GENDERS[self.gender])[:26]
        elif tok == 'backspace':
            self.name = self.name[:-1]
        elif tok == 'space' and len(self.name) < 26:
            self.name += ' '
        elif len(tok) == 1 and (tok.isalnum() or tok in "-'") and len(self.name) < 26:
            self.name += tok


class OptionsScreen(Screen):
    tall = True
    def __init__(self, app, name, race='human', gender='other'):
        super().__init__(app)
        self.name = name
        self.race, self.gender = race, gender
        self.hardcore = False
        self.seed = ''
        self.sel = 0

    def render(self, cv):
        cv.text_center(W // 2, 4, f'A new life for {self.name}', GOLD)
        cv.wrap(28, 6, 54, 'You have no class. You become what you practise: swing a sword and you grow into a swordsman, '
                          'cast fire and the flames answer you. Skills are learned from tomes you find, and you carry '
                          'six of them at a time.', DIM)
        rows = [('Mode', ('HARDCORE: death is permanent.' if self.hardcore else
                          'SOFTCORE: you wake in a temple, but your backpack, cargo and coins stay with your body.')),
                ('World seed', (self.seed or 'random') + (' _' if self.sel == 1 else ''))]
        for i, (a, b) in enumerate(rows):
            y = 12 + i * 3
            sel = i == self.sel
            cv.text(26, y, ('► ' if sel else '  ') + a, GOLD if sel else FG)
            cv.wrap(44, y, 46, b, BAD if (i == 0 and self.hardcore) else FG, None, 2)
        cv.text_center(W // 2, 20, 'Up/Down: choose · Left/Right or Space: change mode · type digits for a seed', DIM)
        cv.text_center(W // 2, 22, 'Enter: begin · Esc: back', DIM)

    def on_key(self, tok, shift):
        if tok in ('up', 'down', 'np8', 'np2', 'tab'):
            self.sel = 1 - self.sel
        elif tok in ('left', 'right', 'space', 'np4', 'np6') and self.sel == 0:
            self.hardcore = not self.hardcore
        elif self.sel == 1 and len(tok) == 1 and tok.isdigit() and len(self.seed) < 9:
            self.seed += tok
        elif self.sel == 1 and tok == 'backspace':
            self.seed = self.seed[:-1]
        elif tok == 'enter':
            self.app.start_game(E.Game(self.name, self.hardcore, int(self.seed) if self.seed else None, self.race, self.gender))
            self.app.push(IntroScreen(self.app))
        elif tok == 'esc':
            self.app.replace(NameScreen(self.app))


# ====================================================================== game screen
class GameScreen(Screen):
    def view_origin(self):
        g = self.game
        m, p = g.map, g.player
        ox = -((MAP_W - m.w) // 2) if m.w <= MAP_W else max(0, min(m.w - MAP_W, p.x - MAP_W // 2))
        oy = -((MAP_H - m.h) // 2) if m.h <= MAP_H else max(0, min(m.h - MAP_H, p.y - MAP_H // 2))
        return ox, oy

    def render(self, cv):
        g = self.game
        self.draw_map(cv)
        for x in range(MAP_W):
            cv.put(x, MAP_H, '─', LINE, BG)
        for y in range(H):
            cv.put(MAP_W, y, '│', LINE, BG)
        cv.put(MAP_W, MAP_H, '┤', LINE, BG)
        cv.text(2, MAP_H, f' {g.loc_name()} ', DIM, BG)
        if self.app.auto:
            cv.text_center(MAP_W // 2, MAP_H, f' {self.app.auto_label}... any key to stop ', GOLD, BG)
        cv.text_right(MAP_W - 2, MAP_H, f' turn {g.turn} ', DIM, BG)
        self.draw_log(cv)
        self.draw_panel(cv)

    # ---------------------------------------------------------- map
    def draw_map(self, cv):
        g, app = self.game, self.app
        m, p = g.map, g.player
        t = time.monotonic()
        ox, oy = self.view_origin()
        sx = sy = 0
        if app.shake_until > t:
            sx, sy = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
        self.origin = (ox, oy)
        mons = {(o.x, o.y): o for o in m.mons}
        items = {}
        for it in m.items:
            items[(it.x, it.y)] = it
        torch = m.kind == 'siege'
        lighting = m.kind == 'dungeon' or getattr(m, 'underground', False)
        lamps = {}
        if m.kind == 'town' and not lighting and TW.town_ambient(g, m) > 0:
            lighting = True                 # dusk and night in town: the street lamps light the way
            lamps = {xy: k for k, xy in enumerate(getattr(m, 'lamps', ()))}
        lmap = DR.light_map(m) if lighting else None
        deco = getattr(m, 'deco', None)
        night = TW.is_night(g)
        portal = m.portal_pos if (m.kind == 'town' and g.portal and g.portal.get('sid') == m.sid) else None
        vis = g.vis
        self.marks = False
        self.weather = wk = WX.shown(g)
        inline = wk != 'clear' and wk not in WX.NEEDS_CANVAS
        lightning = WX.flash(t) if wk == 'storm' else 0.0
        pvx, pvy = p.x - ox, p.y - oy
        sight = g.over_sight() if m.kind == 'over' else 0
        taint = getattr(g.world, 'taint', None) if m.kind == 'over' else None
        for vy in range(MAP_H):
            my = vy + oy - sy
            if not 0 <= my < m.h:
                continue
            for vx in range(MAP_W):
                mx = vx + ox - sx
                if not 0 <= mx < m.w:
                    continue
                i = my * m.w + mx
                v = vis[i] if i < len(vis) else 0
                if not v and not m.seen[i]:
                    continue
                ch, fg, bg = LOOK.get(m, i)
                if taint and taint[i]:
                    ch, fg, bg = LOOK.tainted((ch, fg, bg), g.world.evils[taint[i] - 1].d['taint'], i)
                if deco and deco[i]:
                    ch, fg, bg = DR.deco_look(m, i, (ch, fg, bg))
                if portal and (mx, my) == portal:
                    ch, fg = '0', (90, 176, 255)
                if lamps and (mx, my) in lamps and lamps[(mx, my)] in m.lamp_on:
                    fl = DR.flicker(m, 0, t + lamps[(mx, my)])
                    ch, fg, bg = 'Γ', (255, int(200 * fl), int(110 * fl)), (int(90 * fl), int(52 * fl), 16)
                if v and lighting:
                    lr, lg, lb = DR.light_at(m, i, t)
                    dd = ((mx - p.x) ** 2 + (my - p.y) ** 2) ** .5
                    k = max(0.0, 1 - dd / 7.5) * .95
                    ch, fg, bg = DR.lit((ch, fg, bg), (lr + k, lg + k * .82, lb + k * .55))
                elif lighting:
                    fg = mix(scale(fg, .42), (40, 52, 96), .4)
                    bg = mix(scale(bg, .35), (8, 10, 22), .5)
                if v:
                    if torch:
                        d = ((mx - p.x) ** 2 + (my - p.y) ** 2) ** .5
                        k = max(0.0, 1 - d / 8)
                        bg = (13 + int(34 * k), 11 + int(20 * k), 10 + int(8 * k))
                    it = items.get((mx, my))
                    if it:
                        ch, fg = it.glyph(), it.color()
                        if it.k == 'gear' and it.rar != 'normal':
                            bg = mix(bg, fg, .18)
                    o = mons.get((mx, my))
                    if o and getattr(o, 'lurk', False):
                        o = None                    # something waits there, unseen
                    if o:
                        ch, fg = o.ch, o.fg
                        if o.is_npc:
                            mark = MS.quest_mark(g, o)
                            if mark:
                                self.marks = True
                                if int(t * 2.2) % 2 == 0:       # blinks, like the marks over quest givers in WoW
                                    ch, fg = mark, (255, 214, 40)
                        if not o.is_npc:
                            if o.elite or o.is_boss:
                                bg = mix(bg, o.fg, .25)
                            if o.hold > 0:
                                fg = (159, 216, 255)
                            if t - app.hit_times.get(o.id, -9) < .13:
                                fg, bg = (255, 255, 255), (120, 30, 20)
                    if mx == p.x and my == p.y:
                        ch, fg = '@', ((184, 240, 138) if p.poison else (255, 246, 220))
                    if m.kind == 'over':     # the edge of sight fades out softly
                        d = max(abs(mx - p.x), abs(my - p.y))
                        k = 1 - .45 * max(0.0, min(1.0, (d - (sight - 2)) / 2))
                        if k < 1:
                            fg, bg = scale(fg, k), scale(bg, .55 + .45 * k)
                elif not lighting and m.kind == 'over':
                    # fog of war: land you remember, but cannot see now; grey and veiled
                    gr = (fg[0] + fg[1] + fg[2]) // 3
                    fg = mix(scale(mix(fg, (gr, gr, gr), .6), .42), (52, 58, 74), .3)
                    gb = (bg[0] + bg[1] + bg[2]) // 3
                    bg = mix(scale(mix(bg, (gb, gb, gb), .6), .45), (10, 12, 18), .5)
                    if LOOK._h(mx, my, 31) % 9 == 0:
                        bg = mix(bg, (26, 28, 36), .5)       # wisps of mist
                elif not lighting:
                    fg = scale(fg, .3)
                    bg = scale(bg, .55)
                if night and m.kind in ('over', 'town') and not lighting:
                    fg = mix(fg, (40, 50, 110), .35)
                    bg = scale(bg, .7)
                if inline:
                    if m.kind == 'town' and m.t[i] in ROOFED:
                        if lightning:
                            fg, bg = WX.sheltered_flash(fg, bg, lightning)
                    else:
                        ch, fg, bg = WX.cell(wk, ch, fg, bg, vx, vy, t, ((vx - pvx) ** 2 + (vy - pvy) ** 2) ** .5,
                                             lightning, MAP_W, MAP_H)
                cv.put(vx, vy, ch, fg, bg)
        if m.kind == 'over':
            self.draw_overworld_extras(cv, ox, oy)
        wk = self.weather
        if wk in WX.NEEDS_CANVAS:
            shelter = None
            if m.kind == 'town':                     # no weather under a roof
                shelter = {(vx, vy) for vy in range(MAP_H) for vx in range(MAP_W)
                           if m.inb(vx + ox, vy + oy) and m.t[(vy + oy) * m.w + vx + ox] in ROOFED}
            WX.apply(cv, 0, 0, MAP_W, MAP_H, wk, t, centre=(p.x - ox, p.y - oy), sheltered=shelter)
        elif wk != 'clear':
            WX.passes(cv, 0, 0, MAP_W, MAP_H, wk, t)
        for sx_, sy_, text in getattr(m, 'signs', ()):
            for j, ch in enumerate(text):
                mx_, my_ = sx_ + j, sy_
                if (mx_, my_) == (p.x, p.y) or (mx_, my_) in mons or not m.inb(mx_, my_):
                    continue
                vx, vy = mx_ - ox, my_ - oy
                if 0 <= vx < MAP_W and 0 <= vy < MAP_H:
                    cv.put(vx, vy, ch, (230, 196, 120), (46, 34, 20))
        # effects
        for kind, t0, ev in app.effects:
            age = t - t0
            if kind == 'flash':
                _, cells, col, ch, dur = ev
                for x, y in cells:
                    if g.visible(x, y):
                        self._put_map(cv, x, y, ch, col)
            elif kind == 'speech':
                _, x, y, txt = ev
                txt = txt if len(txt) <= 36 else txt[:35] + '…'
                vx, vy = x - ox - len(txt) // 2, y - oy - 1
                vx = max(0, min(MAP_W - len(txt), vx))
                if 0 <= vy < MAP_H:
                    for j, chh in enumerate(txt):
                        cv.put(vx + j, vy, chh, (240, 236, 220), (40, 34, 30))
            elif kind == 'num':
                _, x, y, txt, col, big = ev
                rise = int(age * 2.5)
                fade = max(0.0, 1 - age / .8)
                c = mix(BG, col, fade if not big else min(1, fade * 1.3))
                vx, vy = x - ox - len(txt) // 2, y - oy - 1 - rise
                if 0 <= vy < MAP_H:
                    for j, chh in enumerate(txt):
                        if 0 <= vx + j < MAP_W:
                            cv.put(vx + j, vy, chh, c)

    def draw_overworld_extras(self, cv, ox, oy):
        g = self.game
        p = g.player
        w = g.world
        # settlement names
        for s in w.settlements:
            if not g.known_settlement(s):
                continue
            vx, vy = s.x - ox, s.y - oy - 1
            label = s.name
            lx = vx - len(label) // 2
            if 0 <= vy < MAP_H and -len(label) < lx < MAP_W and not (p.y == s.y - 1 and lx <= p.x - ox < lx + len(label)):
                col = (255, 226, 140) if s.is_city else (236, 210, 150) if s.kind != 'hamlet' else (196, 176, 136)
                if s.kind == 'metropolis':
                    label = label.upper()
                for j, ch in enumerate(' ' + label + ' '):
                    if 0 <= lx + j - 1 < MAP_W:
                        cv.put(lx + j - 1, vy, ch, col, (30, 22, 14))
        # temples, monasteries and watchtowers
        om = g.map
        for st in getattr(w, 'sites', ()):
            if om.seen[st.y * om.w + st.x]:
                vx, vy = st.x - ox, st.y - oy
                if 0 <= vx < MAP_W and 0 <= vy < MAP_H and (st.x, st.y) != (p.x, p.y):
                    ch, col = st.glyph
                    cv.put(vx, vy, ch, col, (40, 34, 26))
        # settlements, by size; dwarven holds are a gate in the mountainside
        LOOKS = {'metropolis': ('█', (255, 232, 150), (90, 70, 30)), 'city': ('■', (255, 216, 96), (60, 44, 20)),
                 'town': ('⌂', (250, 206, 90), (52, 38, 18)), 'village': ('⌂', (226, 186, 90), None),
                 'hamlet': ('∩', (196, 160, 96), None), 'deephold': ('▼', (255, 200, 90), (60, 40, 20))}
        for s in w.settlements:
            if g.known_settlement(s) and s.kind in LOOKS:
                vx, vy = s.x - ox, s.y - oy
                if 0 <= vx < MAP_W and 0 <= vy < MAP_H and (s.x, s.y) != (p.x, p.y):
                    ch, col, bg = LOOKS[s.kind]
                    cv.put(vx, vy, ch, col, bg)
        # strongholds in their faction colour
        for h in w.holds:
            om = g.map
            if not om.seen[h.y * om.w + h.x]:
                continue
            vx, vy = h.x - ox, h.y - oy
            if 0 <= vx < MAP_W and 0 <= vy < MAP_H and (h.x, h.y) != (p.x, p.y):
                cv.put(vx, vy, 'Ω' if h.kind == 'castle' else '╬', D.FACTIONS[h.faction]['fg'], (40, 30, 20))
        # job markers
        for mi in MS.active(g):
            (tx, ty), _ = MS.target_pos(g, mi)
            vx, vy = tx - ox, ty - oy
            if 0 <= vx < MAP_W and 0 <= vy < MAP_H:
                if mi.kind == 'bounty' and mi.state == 'active' and not g.visible(tx, ty):
                    cv.put(vx, vy, 'X', (255, 214, 92), (70, 50, 10))
                else:
                    self._tint(cv, vx, vy, (90, 66, 14))
        # places found in the wilds
        for poi in w.pois:
            if not poi.found:
                continue
            vx, vy = poi.x - ox, poi.y - oy
            if 0 <= vx < MAP_W and 0 <= vy < MAP_H and (poi.x, poi.y) != (p.x, p.y):
                ch, col = poi.glyph
                if poi.ready_day >= 10 ** 9 or g.day < poi.ready_day:
                    col = scale(col, .5)
                elif not g.visible(poi.x, poi.y):
                    col = scale(col, .7)
                cv.put(vx, vy, ch, col, (34, 28, 22))
        # travellers
        for wd in w.wanderers:
            if not g.visible(wd.x, wd.y):
                continue
            vx, vy = wd.x - ox, wd.y - oy
            if 0 <= vx < MAP_W and 0 <= vy < MAP_H and (wd.x, wd.y) != (p.x, p.y):
                bg = (50, 16, 60) if wd.kind == 'hunt' else (70, 20, 16) if wd.hostile else (20, 30, 50) if wd.kind == 'patrol' else BG
                ch = '☺' if wd.ch == '@' and not wd.hostile and wd.kind not in ('hunt', 'lawmen', 'bounty') else wd.ch
                fg = wd.fg
                if getattr(wd, 'offer', None) and not wd.hostile:
                    self.marks = True
                    if int(time.monotonic() * 2.2) % 2 == 0:
                        ch, fg = '!', (255, 214, 40)
                cv.put(vx, vy, ch, fg, bg)

    def _tint(self, cv, vx, vy, bg):
        cv.put_bg(vx, vy, bg)

    def _put_map(self, cv, x, y, ch, col):
        ox, oy = self.origin
        vx, vy = x - ox, y - oy
        if 0 <= vx < MAP_W and 0 <= vy < MAP_H:
            cv.put(vx, vy, ch, col)

    # ---------------------------------------------------------- log
    def draw_log(self, cv):
        g = self.game
        lines = []
        for idx in range(len(g.log) - 1, -1, -1):
            text, cls = g.log[idx]
            wrapped = wrap_text(text, MAP_W - 2)
            for ln in reversed(wrapped):
                lines.append((ln, cls, idx >= g.log_mark))
            if len(lines) >= H - LOG_Y:
                break
        lines = lines[:H - LOG_Y][::-1]
        for i, (ln, cls, new) in enumerate(lines):
            col = LOGCOL.get(cls, FG) if new else scale(LOGCOL.get(cls, FG), .55)
            cv.text(1, LOG_Y + i, ln, col)

    # ---------------------------------------------------------- side panel
    def draw_panel(self, cv):
        g = self.game
        p = g.player
        s = g.stats()
        cv.fill(MAP_W + 1, 0, W - MAP_W - 1, H, ' ', FG, PANEL)
        x = PX
        cv.text(x, 0, p.name, GOLD, PANEL, maxw=PW - len(CAL.short(g.day)) - 1)
        cv.text_right(x + PW - 1, 0, CAL.short(g.day), DIM, PANEL)
        hr = TW.hour(g)
        cv.text(x, 1, f"Level {p.lvl} · {'hardcore' if p.hardcore else 'softcore'}", DIM, PANEL)
        cv.text_right(x + PW - 1, 1, f"{hr:02d}:00 {'○' if TW.is_night(g) else '☼'}", (150, 160, 220) if TW.is_night(g) else GOLD, PANEL)
        if g.map.kind != 'dungeon' and not getattr(g.map, 'underground', False):
            wk = getattr(self, 'weather', None) or WX.shown(g)
            from . import calendar as CAL2
            cv.text(x, 2, CAL2.season(g.day).capitalize(), DIM, PANEL)
            if wk not in ('clear',):
                lab = WX.NAMES.get(wk, wk)
                cv.text_right(x + PW - 1, 2, f'{lab} {WX.PANEL_ICON.get(wk, "")}', INFO, PANEL)
        self.orb(cv, x, 3, p.life / max(1, s['max_life']), BLOOD, (100, 160, 60) if p.poison else None)
        self.orb(cv, x + PW - 9, 3, p.mana / max(1, s['max_mana']), MANA)
        cv.text_center(x + 4, 12, 'LIFE' if not p.poison else 'POISON', BAD if p.poison else scale(BLOOD, 1.3), PANEL)
        cv.text_center(x + PW - 5, 12, 'MANA', scale(MANA, 1.3), PANEL)
        cv.text_center(x + 4, 13, f"{max(0, int(p.life))}/{s['max_life']}", FG, PANEL)
        cv.text_center(x + PW - 5, 13, f"{max(0, int(p.mana))}/{s['max_mana']}", FG, PANEL)
        for i, ch in enumerate('·♦·'):                  # a small ornament between the globes
            cv.put(x + PW // 2 - 1 + i, 7, ch, scale(GOLD, .6 if ch == '·' else .9), PANEL)
        prev = E.xp_for(p.lvl - 1) if p.lvl > 1 else 0
        frac = (p.xp - prev) / max(1, E.xp_for(p.lvl) - prev)
        cv.text(x, 15, 'XP', DIM, PANEL)
        bw = PW - 3
        filled = int(bw * max(0, min(1, frac)))
        for i in range(bw):
            cv.put(x + 3 + i, 15, '█' if i < filled else '░', GOLD if i < filled else LINE, PANEL)
        cv.text(x, 18, 'SKILLS', DIM, PANEL)
        from . import hunger as HU
        hs = HU.state(getattr(p, 'food', 500))
        if hs:
            cv.text_right(x + PW - 1, 18, hs, GOOD if hs == 'Satiated' else GOLD if hs == 'Hungry' else BAD, PANEL)
        else:
            cv.text_right(x + PW - 1, 18, 'Z: change', scale(DIM, .8), PANEL)
        for i, sid in enumerate(p.bar):
            y = 20 + i * 2
            cv.text(x, y, str(i + 1), GOLD, PANEL)
            if not sid:
                cv.text(x + 2, y, '-', scale(DIM, .6), PANEL)
                continue
            sk = SK.SKILLS[sid]
            cd = p.cooldowns.get(sid, 0)
            ok = p.mana >= sk.cost and not cd
            cv.text(x + 2, y, sk.name, FG if ok else DIM, PANEL, maxw=PW - 8)
            cv.text_right(x + PW - 1, y, f'{cd}t' if cd else f'{sk.cost}mp', BAD if cd else (INFO if ok else DIM), PANEL)
        hp = g.count('potion', 'hp') + g.count('potion', 'rejuv')
        mp = g.count('potion', 'mp') + g.count('potion', 'rejuv')
        tp = g.count('scroll')
        cv.text(x, 33, 'Q', GOLD, PANEL)
        cv.text(x + 2, 33, f'Health x{hp}', D.POTIONS['hp']['col'] if hp else DIM, PANEL)
        cv.text(x + 14, 33, 'W', GOLD, PANEL)
        cv.text(x + 16, 33, f'Mana x{mp}', D.POTIONS['mp']['col'] if mp else DIM, PANEL)
        cv.text(x, 35, 'P', GOLD, PANEL)
        cv.text(x + 2, 35, f'Portal x{tp}', FG if tp else DIM, PANEL)
        cap, used = ECO.cargo_capacity(p), ECO.cargo_weight(p)
        cv.text_right(x + PW - 1, 35, f'Cargo {used}/{cap}', BAD if used >= cap else FG if used else DIM, PANEL)
        from . import crime as CR
        wanted = CR.wanted_in(g)
        if wanted:
            st = CR.max_heat(g)
            cv.text(x, 37, 'WANTED', BAD, PANEL)
            cv.text(x + 7, 37, '*' * st, GOLD, PANEL)
            cv.text_right(x + PW - 1, 37, (wanted[0].name if len(wanted) == 1 else f'{len(wanted)} towns')[:PW - 14], BAD, PANEL)
        rows = [('Damage', f"{s['dmg'][0]}-{s['dmg'][1]}" + (' (bow)' if s['ranged'] else '')), ('Accuracy', str(s['ar'])),
                ('Defense', str(s['def']) + (f" -{s['dr']}%" if s['dr'] else '')),
                ('Critical', f"{s['crit']}%" + (f"  leech {s['leech']}%" if s['leech'] else '')), ('Money', fmt(p.gold, True))]
        for i, (a, b) in enumerate(rows):
            cv.text(x, 39 + i * 2, a, DIM, PANEL)
            cv.text_right(x + PW - 1, 39 + i * 2, b, GOLD if a == 'Money' else FG, PANEL)
        if p.stat_pts:
            cv.text(x, 49, f'C: {p.stat_pts} attribute points', GOLD, PANEL, maxw=PW)
        elif p.buffs:
            cv.text(x, 49, ', '.join(f'{b[3]} {b[2]}' for b in p.buffs), GOOD, PANEL, maxw=PW)
        self.draw_target(cv, x, 51)
        # what you can do right here, then the keys that always work
        hints = g.context_hints()
        if hints:
            cx = x
            for key, words in hints:
                piece = f'{key} {words}'
                if cx + len(piece) > x + PW:
                    break
                cv.text(cx, H - 3, key, GOLD, PANEL)
                cv.text(cx + len(key) + 1, H - 3, words, FG, PANEL)
                cx += len(piece) + 2
        cv.text(x, H - 1, 'Enter act  Tab menu  ? help', scale(DIM, .8), PANEL, maxw=PW)

    def orb(self, cv, x, y, frac, col, alt=None, w=9, h=9):
        """A glass globe of life or mana, drawn with half blocks at twice the height: shaded liquid with a
        rippling surface, a dark empty top, a highlight on the glass and a gold rim."""
        import math
        frac = max(0.0, min(1.0, frac))
        liquid = alt or col
        t = time.monotonic()
        ph = h * 2
        cx, cy = (w - 1) / 2, (ph - 1) / 2
        rx, ry = w / 2, ph / 2
        level = ph - frac * (ph - 1.5) - .75          # the row of the liquid's surface

        def pixel(px, py):
            dx, dy = (px - cx) / rx, (py - cy) / ry
            d = dx * dx + dy * dy
            if d > 1.0:
                return None
            if d > .78:                              # the rim, lit from the top left
                k = .5 - .5 * (dx + dy) / 1.4
                return mix((70, 50, 26), (230, 186, 110), k)
            shade = 1 - .55 * d                      # rounder: darker towards the edge
            wave = math.sin(px * 1.3 + t * 2.4) * .45 + math.sin(px * .7 - t * 1.6) * .3
            if py >= level + wave:
                depth = (py - level) / max(1.0, ph - level)
                c = mix(scale(liquid, 1.25), scale(liquid, .55), depth)
                c = scale(c, shade)
                if py < level + wave + 1:            # the bright surface line
                    c = mix(c, (255, 240, 220), .35)
            else:
                c = scale(mix((26, 20, 26), scale(liquid, .25), .35), shade)
            hx, hy = (px - (cx - rx * .38)) / (rx * .28), (py - (cy - ry * .45)) / (ry * .22)
            if hx * hx + hy * hy < 1:                # a highlight on the glass
                c = mix(c, (255, 255, 255), .55 * (1 - (hx * hx + hy * hy)))
            return c

        for row in range(h):
            for c_ in range(w):
                top, bot = pixel(c_, row * 2), pixel(c_, row * 2 + 1)
                if top is None and bot is None:
                    continue
                if top is None:
                    cv.put(x + c_, y + row, '▄', bot, PANEL)
                elif bot is None:
                    cv.put(x + c_, y + row, '▀', top, PANEL)
                else:
                    cv.put(x + c_, y + row, '▀', top, bot)

    def draw_target(self, cv, x, y):
        g = self.game
        m, p = g.map, g.player
        tgt = None
        hv = self.app.hover
        if hv and hasattr(self, 'origin'):
            mx, my = hv[0] + self.origin[0], hv[1] + self.origin[1]
            if hv[0] < MAP_W and hv[1] < MAP_H and m.inb(mx, my) and m.kind == 'over' and m.seen[my * m.w + mx]:
                from .wanderers import wanderer_at
                wd = wanderer_at(g, mx, my) if g.visible(mx, my) else None
                st = g.world.settlement_at(mx, my)
                dg = g.world.dungeon_at(mx, my)
                if wd:
                    cv.text(x, y, wd.name, wd.fg, PANEL, maxw=PW)
                    cv.wrap(x, y + 1, PW, wd.describe(g), DIM, PANEL, 2)
                elif g.world.hold_at(mx, my):
                    h = g.world.hold_at(mx, my)
                    f = D.FACTIONS[h.faction]
                    cv.text(x, y, h.title, f['fg'], PANEL, maxw=PW)
                    cv.text(x, y + 1, f"{f['short']} · garrison {h.garrison}", DIM, PANEL, maxw=PW)
                    cv.text(x, y + 2, 'Hostile to you' if WAR.is_hostile(g, h.faction) else 'Open to you', BAD if WAR.is_hostile(g, h.faction) else GOOD, PANEL)
                elif st:
                    cv.text(x, y, f"{st.name} ({st.kind_name})", D.FACTIONS[st.faction]['fg'], PANEL, maxw=PW)
                    cv.text(x, y + 1, 'Makes: ' + ', '.join(D.GOODS[k]['name'] for k in st.produce), DIM, PANEL, maxw=PW)
                    cv.text(x, y + 2, 'Wants: ' + ', '.join(D.GOODS[k]['name'] for k in st.demand), DIM, PANEL, maxw=PW)
                elif EV.poi_at(g, mx, my) and EV.poi_at(g, mx, my).found:
                    poi = EV.poi_at(g, mx, my)
                    cv.text(x, y, poi.name, poi.glyph[1], PANEL, maxw=PW)
                    if poi.kind in EV.RUIN_KINDS:
                        dd = g.world.dungeons[poi.did]
                        info = f'{dd.depth} level{"s" if dd.depth > 1 else ""}, monster level {dd.base + 1}+'
                    elif poi.ready_day >= 10 ** 9:
                        info = 'Nothing left here.'
                    elif g.day < poi.ready_day:
                        info = 'Quiet for now.'
                    else:
                        info = {'shrine': 'A place to pray.', 'camp': 'Outlaws and their loot.',
                                'stones': 'Old power sleeps here.', 'wagon': 'Might hold something.'}[poi.kind]
                    cv.text(x, y + 1, info, DIM, PANEL, maxw=PW)
                    cv.text(x, y + 2, f'Danger {g.world.danger_at(mx, my)}', BAD, PANEL, maxw=PW)
                elif dg:
                    cv.text(x, y, dg.name, (232, 96, 62), PANEL, maxw=PW)
                    cv.text(x, y + 1, f'{dg.depth} levels, monster level {dg.base + 1}+', DIM, PANEL, maxw=PW)
                else:
                    cv.text(x, y, D.TILES[m.tile(mx, my)].name.capitalize(), DIM, PANEL, maxw=PW)
                    cv.text(x, y + 1, g.world.region_at(mx, my).name, DIM, PANEL, maxw=PW)
                    dz = g.world.danger_at(mx, my)
                    cv.text(x, y + 2, f"Danger {dz}" + (' (road)' if m.tile(mx, my) == D.ROAD else ''),
                            GOOD if dz <= 2 else FG if dz <= 5 else BAD, PANEL, maxw=PW)
                    ev = EVL.taint_at(g, mx, my)
                    if ev:
                        cv.text(x, y + 3, ev.d['taint_name'].capitalize() + (f' of {ev.short}' if ev.known else ''), ev.fg, PANEL, maxw=PW)
                return
            if hv[0] < MAP_W and hv[1] < MAP_H and m.inb(mx, my) and g.visible(mx, my):
                o = m.mon_at(mx, my)
                if o:
                    tgt = o
                else:
                    its = [i for i in m.items if i.x == mx and i.y == my]
                    if its:
                        cv.text(x, y, its[-1].display_name(), its[-1].color(), PANEL, maxw=PW)
                        lines = its[-1].lines()
                        for i, ln in enumerate(lines[:4]):
                            cv.text(x, y + 1 + i, ln, DIM, PANEL, maxw=PW)
                        return
                    cv.text(x, y, D.TILES[m.tile(mx, my)].name.capitalize(), DIM, PANEL, maxw=PW)
                    return
        if not tgt:
            vis = g.visible_hostiles()
            last = [o for o in vis if o.id == p.last_target]
            tgt = last[0] if last else (min(vis, key=lambda o: cheb(o.x, o.y, p.x, p.y)) if vis else None)
        if not tgt:
            return
        cv.text(x, y, tgt.name, tgt.fg, PANEL, maxw=PW)
        if tgt.is_npc:
            cv.text(x, y + 1, 'Walk into them to talk.', DIM, PANEL)
            return
        bw = PW
        frac = max(0, tgt.hp) / tgt.maxhp
        for i in range(bw):
            cv.put(x + i, y + 1, ' ', FG, BLOOD if i < int(bw * frac + .99) else (40, 20, 16))
        cv.text(x, y + 1, f'{max(0, tgt.hp)}/{tgt.maxhp}', (255, 240, 220))
        extra = f'level {tgt.lvl}'
        if tgt.mods:
            extra += ' · ' + ', '.join(tgt.mods)
        cv.text(x, y + 2, extra, DIM, PANEL, maxw=PW)

    # ---------------------------------------------------------- input
    def act(self, fn):
        g = self.game
        if g.dead:
            return
        g.log_mark = len(g.log)
        used = fn()
        if used and not g.dead:
            g.end_turn(used)

    def on_key(self, tok, shift):
        g, app = self.game, self.app
        if g.dead:
            return
        d = DIRS.get(tok)
        if not d and tok in RUN_LETTERS:
            d, shift = DIRS[RUN_LETTERS[tok]], True
        if d:
            if shift and not g.hostile_visible():
                g.log_mark = len(g.log)
                g.run(*d)
            else:
                self.act(lambda: g.try_move(*d))
            return
        if tok in ('np5', '.', 's'):
            self.act(lambda: 1)
        elif tok in ('1', '2', '3', '4', '5', '6'):
            self.act(lambda: g.use_skill(int(tok) - 1))
        elif tok == 'f':
            self.act(g.fire)
        elif tok == 'a':
            self.act(g.fish)
        elif tok == 'E':
            self.act(g.eat_best)
        elif tok == 'F':
            self.act(g.forage)
        elif tok == 'P':
            app.push(BrewScreen(app))
        elif tok == 'z':
            app.push(SkillsScreen(app))
        elif tok == 'q':
            self.act(lambda: g.drink('hp'))
        elif tok == 'w':
            self.act(lambda: g.drink('mp'))
        elif tok == 'p':
            self.act(g.town_portal)
        elif tok in ('g', ','):
            self.act(g.pickup)
        elif tok == '>':
            self.act(lambda: g.use_stairs('down'))
        elif tok == '<':
            self.act(lambda: g.use_stairs('up'))
        elif tok in ('enter', 'np_enter', 'space'):
            self.act(g.act_here)
        elif tok == 'x':
            g.log_mark = len(g.log)
            app.start_auto(g.explore_iter(), .055, 'Exploring')
        elif tok == 't':
            if g.map.kind in ('over', 'town'):
                app.push(TravelScreen(app))
            else:
                g.log_mark = len(g.log)
                g.msg('You can only travel from the open land or from a town.')
        elif tok == 'm':
            app.push(WorldMapScreen(app))
        elif tok == 'e':
            app.push(JournalScreen(app))
        elif tok == 'tab':
            app.push(MenuScreen(app))
        elif tok == 'T':
            g.log_mark = len(g.log)
            g.talk_nearby()
        elif tok == 'i':
            app.push(InventoryScreen(app))
        elif tok == 'd':
            app.push(InventoryScreen(app, drop=True))
        elif tok == 'c':
            app.push(CharacterScreen(app))
        elif tok == 'C':
            app.push(CharacterScreen(app, page=2))
        elif tok == 'R':
            g.log_mark = len(g.log)
            g.rest()
        elif tok in ('?', 'f1'):
            app.push(HelpScreen(app))
        elif tok in ('v', 'f2'):
            app.push(BestiaryScreen(app))
        elif tok in ('o', ';'):
            app.push(LookScreen(app))
        elif tok == 'esc':
            app.push(QuitScreen(app))

    def on_click(self, tx, ty, button):
        g = self.game
        if g.dead or tx >= MAP_W or ty >= MAP_H or not hasattr(self, 'origin'):
            return
        mx, my = tx + self.origin[0], ty + self.origin[1]
        p = g.player
        dx = (mx > p.x) - (mx < p.x)
        dy = (my > p.y) - (my < p.y)
        if not dx and not dy:
            m = g.map
            if any(i.x == p.x and i.y == p.y for i in m.items):
                self.act(g.pickup)
            elif m.tile(p.x, p.y) in (DOWN, UP, TOWN, ENTR):
                self.act(lambda: g.use_stairs('auto'))
            else:
                self.act(lambda: 1)
            return
        self.act(lambda: g.try_move(dx, dy))


# ====================================================================== modal screens
class Modal(Screen):
    overlay = True
    tall = True
    title = ''

    def box(self, cv, w, h, title=None):
        x, y = (W - w) // 2, (cv.h - h) // 2
        cv.frame(x, y, w, h, LINE, PANEL, title or self.title, GOLD)
        return x, y

    def on_key(self, tok, shift):
        if tok == 'esc':
            self.app.pop()


def item_detail(cv, g, it, x, y, w, max_h=14):
    if not it:
        return
    cv.text(x, y, it.display_name(), it.color(), PANEL, maxw=w)
    yy = y + 1
    if it.k == 'gear':
        cv.text(x, yy, f"{D.SLOTNAME[it.slot]}{'' if it.rar == 'normal' else ' · ' + it.rar}", DIM, PANEL)
        yy += 1
    for ln in it.lines():
        if yy >= y + max_h:
            break
        yy += cv.wrap(x, yy, w, ln, FG, PANEL, 2)
    if it.k == 'gear' and it.req > 1:
        cv.text(x, yy, f'Requires level {it.req}', BAD if it.req > g.player.lvl else DIM, PANEL)
        yy += 1
    cv.text(x, yy, f'Value {fmt(it.value())}', DIM, PANEL)
    yy += 1
    if it.k == 'gear' and not g.is_equipped(it):
        cur = g.eq_item(it.slot)
        yy += 1
        if cur:
            cv.text(x, yy, 'Equipped now:', DIM, PANEL)
            cv.text(x, yy + 1, cur.display_name(), cur.color(), PANEL, maxw=w)
            yy += 2
            if it.dmg and cur.dmg:
                d = (it.dmg[0] + it.dmg[1]) - (cur.dmg[0] + cur.dmg[1])
                cv.text(x, yy, f'Base damage {"+" if d >= 0 else ""}{d / 2:g} avg', GOOD if d > 0 else BAD if d < 0 else DIM, PANEL)
                yy += 1
            if it.arm and cur.arm:
                d = it.armor_value() - cur.armor_value()
                cv.text(x, yy, f'Armor {"+" if d >= 0 else ""}{d}', GOOD if d > 0 else BAD if d < 0 else DIM, PANEL)
                yy += 1
        else:
            cv.text(x, yy, f'Nothing equipped as {D.SLOTNAME[it.slot].lower()}.', DIM, PANEL)


class InventoryScreen(Modal):
    title = 'Inventory'

    def __init__(self, app, drop=False):
        super().__init__(app)
        self.drop_mode = drop
        self.sel = 0

    def rows(self):
        g = self.game
        out = [('eq', s, g.eq_item(s)) for s in D.SLOTS]
        out += [('bag', i, it) for i, it in enumerate(g.backpack())]
        return out

    BOX_W, BOX_H = 104, 30
    BAG_Y, BAG_ROWS = 12, 16
    NE = len(D.SLOTS)

    def bag_scroll(self):
        i = self.sel - self.NE
        if i < 0:
            return getattr(self, 'scroll', 0)
        sc = getattr(self, 'scroll', 0)
        if i < sc:
            sc = i
        elif i >= sc + self.BAG_ROWS:
            sc = i - self.BAG_ROWS + 1
        self.scroll = sc
        return sc

    def render(self, cv):
        g = self.game
        rows = self.rows()
        self.sel = max(0, min(self.sel, len(rows) - 1))
        x, y = self.box(cv, self.BOX_W, self.BOX_H, 'Drop which item?' if self.drop_mode else 'Inventory')
        cv.text(x + 2, y + 1, f'{len(g.player.inv)}/24 slots · {fmt(g.player.gold)}', DIM, PANEL)
        cv.text(x + 2, y + 3, 'EQUIPPED', DIM, PANEL)
        cv.text(x + 2, y + 11, 'BACKPACK', DIM, PANEL)
        sc = self.bag_scroll()
        nbag = len(g.backpack())
        if sc > 0:
            cv.text(x + 50, y + 11, '▲', GOLD, PANEL)
        if sc + self.BAG_ROWS < nbag:
            cv.text(x + 50, y + self.BAG_Y + self.BAG_ROWS, '▼', GOLD, PANEL)
        for idx, (kind, key, it) in enumerate(rows):
            sel = idx == self.sel
            bg = (52, 40, 28) if sel else PANEL
            if kind == 'eq':
                yy = y + 4 + idx
                cv.fill(x + 2, yy, 54, 1, ' ', FG, bg)
                cv.text(x + 4, yy, f'{D.SLOTNAME[key]:<7}', DIM, bg)
                if it:
                    cv.text(x + 12, yy, it.display_name(), it.color(), bg, maxw=42)
                else:
                    cv.text(x + 12, yy, '-', DIM, bg)
            else:
                if not sc <= key < sc + self.BAG_ROWS:
                    continue
                yy = y + self.BAG_Y + key - sc
                cv.fill(x + 2, yy, 54, 1, ' ', FG, bg)
                cv.text(x + 2, yy, LETTERS[key], GOLD, bg)
                cv.text(x + 4, yy, it.display_name(), it.color(), bg, maxw=48)
                if it.k == 'gear' and it.req > g.player.lvl:
                    cv.text(x + 54, yy, '!', BAD, bg)
        if nbag == 0:
            cv.text(x + 4, y + self.BAG_Y, 'Your backpack is empty.', DIM, PANEL)
        for yy in range(y + 1, y + self.BOX_H - 1):
            cv.put(x + 58, yy, '│', LINE, PANEL)
        if rows:
            item_detail(cv, g, rows[self.sel][2], x + 60, y + 3, 42, 22)
        hint = 'letter: select · Enter: equip/use/remove · D: drop · Esc: close'
        if self.drop_mode:
            hint = 'letter or Enter: drop the item · Esc: close'
        cv.text_center(W // 2, y + self.BOX_H - 1, f' {hint} ', DIM, PANEL)

    def use(self):
        g, app = self.game, self.app
        rows = self.rows()
        if not rows:
            return
        kind, key, it = rows[self.sel]
        if kind == 'eq':
            if it:
                g.unequip(key)
            return
        if self.drop_mode:
            self.drop()
            return
        g.log_mark = len(g.log)
        if it.k == 'gear':
            g.equip(it)
            return
        if it.k == 'tome':
            g.read_tome(it)
            return
        if it.k in ('fish', 'food'):
            app.pop()
            if g.eat(it):
                g.end_turn(1)
            return
        if it.k == 'plant':
            from . import foraging as FGM
            app.pop()
            if FGM.eat_plant(g, it):
                g.end_turn(1)
            return
        if it.k not in ('potion', 'scroll'):
            return
        app.pop()
        used = g.drink(it.t) if it.k == 'potion' else g.town_portal()
        if used and not g.dead:
            g.end_turn(used)

    def drop(self):
        g, app = self.game, self.app
        rows = self.rows()
        if not rows:
            return
        kind, key, it = rows[self.sel]
        if not it:
            return
        g.log_mark = len(g.log)
        app.pop()
        g.drop(it)
        g.end_turn(1)

    def on_key(self, tok, shift):
        rows = self.rows()
        if tok == 'esc':
            self.app.pop()
        elif tok in ('up', 'np8'):
            self.sel = max(0, self.sel - 1)
        elif tok in ('down', 'np2'):
            self.sel = min(len(rows) - 1, self.sel + 1)
        elif tok in ('enter', 'np_enter'):
            self.use()
        elif tok in ('D', 'delete'):
            self.drop()
        elif len(tok) == 1 and tok in LETTERS:
            i = LETTERS.index(tok)
            if i < len(self.game.backpack()):
                already = self.sel == self.NE + i
                self.sel = self.NE + i
                if self.drop_mode or already:
                    self.use()

    def on_click(self, x, y, button):
        bx, by = (W - self.BOX_W) // 2, (cv.h - self.BOX_H) // 2
        sc = getattr(self, 'scroll', 0)
        if bx + 2 <= x < bx + 56:
            if by + 4 <= y < by + 4 + self.NE:
                self.sel = y - by - 4
            elif by + self.BAG_Y <= y < by + self.BAG_Y + self.BAG_ROWS and y - by - self.BAG_Y + sc < len(self.game.backpack()):
                new = self.NE + y - by - self.BAG_Y + sc
                if new == self.sel:
                    self.use()
                self.sel = new


class CharacterScreen(Modal):
    """Your hero, in three pages: who you are, your fighting disciplines and your life skills."""
    PAGES = ['Character', 'Disciplines', 'Life skills']

    def __init__(self, app, page=0):
        super().__init__(app)
        self.page = page

    def tabs(self, cv, x, y):
        xx = x + 2
        for i, name in enumerate(self.PAGES):
            sel = i == self.page
            label = f' {name} '
            cv.text(xx, y, label, (20, 16, 12) if sel else DIM, GOLD if sel else PANEL)
            xx += len(label) + 2

    def render(self, cv):
        g = self.game
        p = g.player
        x, y = self.box(cv, 72, 26, f"{p.name} · level {p.lvl}")
        self.tabs(cv, x, y + 1)
        [self.page_main, self.page_disc, self.page_life][self.page](cv, x, y + 3)
        hint = ' ←→ or Tab: page · 1-4: add an attribute point · Esc: close ' if self.page == 0 else ' ←→ or Tab: page · Esc: close '
        cv.text_center(W // 2, y + 25, hint, DIM, PANEL)

    def bar(self, cv, x, y, w, frac, col):
        fill = int(w * max(0.0, min(1.0, frac)))
        for j in range(w):
            cv.put(x + j, y, '█' if j < fill else '░', col if j < fill else LINE, PANEL)

    def page_main(self, cv, x, y):
        g = self.game
        p, s = g.player, g.stats()
        from . import races as RC
        from . import gods as GD
        who = f"{RC.RACES[p.race]['name']}{'' if p.gender == 'other' else ' ' + RC.GENDER_NAME[p.gender].lower()}"
        cv.text(x + 3, y, f'{who} · {"hardcore" if p.hardcore else "softcore"} · {p.deaths} deaths', FG, PANEL)
        cv.text(x + 3, y + 1, 'Faith: ' + GD.standing(g), GD.GODS[p.god]['fg'] if getattr(p, 'god', None) else DIM, PANEL)
        cv.text(x + 3, y + 3, 'ATTRIBUTES', DIM, PANEL)
        if p.stat_pts:
            cv.text_right(x + 68, y + 3, f'{p.stat_pts} points to spend', GOLD, PANEL)
        helps = {'str': '+1% melee damage', 'dex': 'aim, defense, bows', 'vit': '+2 life', 'ene': '+2 mana, spells'}
        for i, (st, nm) in enumerate((('str', 'Strength'), ('dex', 'Dexterity'), ('vit', 'Vitality'), ('ene', 'Energy'))):
            yy = y + 4 + i
            cv.text(x + 3, yy, f'{i + 1}', GOLD if p.stat_pts else DIM, PANEL)
            cv.text(x + 5, yy, nm, FG, PANEL)
            cv.text_right(x + 20, yy, str(s[st]), FG, PANEL)
            cv.text(x + 23, yy, helps[st], DIM, PANEL)
        cv.text(x + 3, y + 9, 'IN NUMBERS', DIM, PANEL)
        tots = [('Life', f"{p.life}/{s['max_life']}"), ('Mana', f"{p.mana}/{s['max_mana']}"), ('Damage', f"{s['dmg'][0]}-{s['dmg'][1]}"),
                ('Accuracy', str(s['ar'])), ('Defense', str(s['def'])), ('Critical', f"{s['crit']}%"),
                ('Life leech', f"{s['leech']}%"), ('Experience', f'{p.xp}/{E.xp_for(p.lvl)}')]
        for i, (a, b) in enumerate(tots):
            cx_ = x + 3 + (i % 2) * 34
            cv.text(cx_, y + 10 + i // 2, a, DIM, PANEL)
            cv.text_right(cx_ + 30, y + 10 + i // 2, b, FG, PANEL)
        from . import hunger as HU
        cv.text(x + 3, y + 15, 'CONDITION', DIM, PANEL)
        cv.text(x + 3, y + 16, 'Hunger', DIM, PANEL)
        self.bar(cv, x + 14, y + 16, 20, p.food / HU.MAX, GOOD if p.food >= HU.HUNGRY else GOLD if p.food >= HU.WEAK else BAD)
        cv.text(x + 36, y + 16, HU.state(p.food) or 'Fed', FG, PANEL)
        if p.buffs:
            cv.wrap(x + 3, y + 18, 66, 'Effects: ' + ', '.join(f'{b[3]} ({b[2]})' for b in p.buffs), GOOD, PANEL, 2)

    def page_disc(self, cv, x, y):
        p = self.game.player
        cv.text(x + 3, y, 'Fighting and magic grow by use. The more you use a discipline, the more tomes you understand.',
                DIM, PANEL, maxw=66)
        for i, line in enumerate(SK.DISC_ORDER):
            yy = y + 2 + i * 2
            r, prog = p.disc[line]
            d = SK.DISCIPLINES[line]
            cv.text(x + 3, yy, d['name'], FG if r else DIM, PANEL)
            cv.text_right(x + 24, yy, str(r), GOLD if r else DIM, PANEL)
            self.bar(cv, x + 27, yy, 20, prog / SK.need_for(r), INFO)
            nxt = next((k for k in SK.by_line(line) if k.unlock > r), None)
            known = sum(1 for k in SK.by_line(line) if k.id in p.known)
            cv.text(x + 49, yy, f'{known}/5 skills', DIM, PANEL)
            cv.text(x + 5, yy + 1, f'next tier at {nxt.unlock}' if nxt else 'all tiers open', scale(DIM, .8), PANEL)

    def page_life(self, cv, x, y):
        from . import lifeskills as LS
        p = self.game.player
        cv.text(x + 3, y, 'Crafts and pastimes grow by doing them, with something new along the way.', DIM, PANEL, maxw=66)
        for i, key in enumerate(LS.LIFE_ORDER):
            yy = y + 2 + i * 4
            r, prog = p.life_sk.get(key, [0, 0])
            cv.text(x + 3, yy, LS.LIFE[key]['name'], FG if r else DIM, PANEL)
            cv.text_right(x + 24, yy, str(r), GOLD if r else DIM, PANEL)
            self.bar(cv, x + 27, yy, 20, prog / LS.need_for(r), GOOD)
            cv.text(x + 5, yy + 1, LS.LIFE[key]['desc'], scale(DIM, .9), PANEL, maxw=64)
            nxt = min((k for k in LS.LIFE[key]['perks'] if k > r), default=None)
            cv.text(x + 5, yy + 2, f"next at {nxt}: {LS.LIFE[key]['perks'][nxt]}" if nxt else 'mastered', scale(GOLD, .75),
                    PANEL, maxw=64)

    def on_key(self, tok, shift):
        g = self.game
        if tok == 'esc':
            self.app.pop()
        elif tok in ('tab', 'right', 'np6', 'l'):
            self.page = (self.page + 1) % len(self.PAGES)
        elif tok in ('left', 'np4', 'h'):
            self.page = (self.page - 1) % len(self.PAGES)
        elif tok in ('1', '2', '3', '4') and self.page == 0:
            g.add_stat(['str', 'dex', 'vit', 'ene'][int(tok) - 1])
        elif tok == 'z':
            self.app.replace(SkillsScreen(self.app))


class SkillsScreen(Modal):
    """Choose which six skills to carry. Only possible in a town or stronghold."""

    def __init__(self, app):
        super().__init__(app)
        self.sel = 0
        self.slot = 0

    def known(self):
        p = self.game.player
        return [SK.SKILLS[k] for k in p.known]

    def render(self, cv):
        g = self.game
        p = g.player
        x, y = self.box(cv, 104, 30, 'Skills')
        in_town = g.map.kind == 'town'
        cv.text(x + 2, y + 1, 'Your bar' + ('' if in_town else ' · change it in a town or stronghold'),
                DIM if in_town else BAD, PANEL)
        for i, sid in enumerate(p.bar):
            yy = y + 2 + i
            sel = i == self.slot
            bg = (52, 40, 28) if sel else PANEL
            cv.fill(x + 2, yy, 48, 1, ' ', FG, bg)
            cv.text(x + 2, yy, str(i + 1), GOLD, bg)
            cv.text(x + 4, yy, SK.SKILLS[sid].name if sid else '- empty -', FG if sid else DIM, bg)
            if sid:
                cv.text_right(x + 49, yy, SK.DISCIPLINES[SK.SKILLS[sid].line]['name'], DIM, bg)
        known = self.known()
        self.sel = max(0, min(self.sel, len(known) - 1))
        cv.text(x + 2, y + 9, f'KNOWN SKILLS ({len(known)}/{len(SK.SKILL_LIST)})', DIM, PANEL)
        for i, sk in enumerate(known[:19]):
            yy = y + 10 + i
            sel = i == self.sel
            bg = (52, 40, 28) if sel else PANEL
            cv.fill(x + 2, yy, 48, 1, ' ', FG, bg)
            cv.text(x + 2, yy, LETTERS[i], GOLD, bg)
            on_bar = sk.id in p.bar
            cv.text(x + 4, yy, sk.name, GOOD if on_bar else FG, bg)
            cv.text_right(x + 49, yy, SK.DISCIPLINES[sk.line]['name'], DIM, bg)
        for yy in range(y + 1, y + 29):
            cv.put(x + 52, yy, '│', LINE, PANEL)
        if known:
            sk = known[self.sel]
            r = p.disc[sk.line][0]
            cv.text(x + 54, y + 2, sk.name, GOLD, PANEL)
            cv.text(x + 54, y + 3, f"{SK.DISCIPLINES[sk.line]['name']} {r} · {sk.cost} mana · recharge {sk.cd} turns", DIM, PANEL, maxw=48)
            n = cv.wrap(x + 54, y + 5, 47, SK.describe(sk, r), FG, PANEL, 10)
            d = SK.DISCIPLINES[sk.line]
            if d['kind'] == 'weapon':
                cv.wrap(x + 54, y + 6 + n, 47, f"Needs {d['weapon']} in your hands.", DIM, PANEL, 2)
        if not known:
            cv.wrap(x + 4, y + 10, 46, 'You know no skills yet. Fight with your weapon for now.', DIM, PANEL)
        cv.wrap(x + 54, y + 20, 47, 'New skills are learned from tomes: found on monsters, deep in ruins, at standing stones, '
                'and now and then sold by peddlers and city outfitters. Harder tomes need a higher discipline, '
                'which grows as you use it.', DIM, PANEL, 6)
        cv.text_center(W // 2, y + 29, ' ↑↓ or letter: pick a skill · 1-6: put it in that slot · Del: clear slot · Esc: close ', DIM, PANEL)

    def on_key(self, tok, shift):
        g = self.game
        p = g.player
        known = self.known()
        if tok == 'esc':
            self.app.pop()
        elif tok in ('up', 'np8'):
            self.sel = max(0, self.sel - 1)
        elif tok in ('down', 'np2'):
            self.sel = min(len(known) - 1, self.sel + 1)
        elif len(tok) == 1 and tok in LETTERS and LETTERS.index(tok) < len(known):
            self.sel = LETTERS.index(tok)
        elif tok in ('1', '2', '3', '4', '5', '6'):
            i = int(tok) - 1
            self.slot = i
            if g.map.kind != 'town':
                g.log_mark = len(g.log)
                g.msg('You can only change your skills in a town or stronghold.', 'bad')
                return
            sid = known[self.sel].id if known else None
            if sid in p.bar:
                p.bar[p.bar.index(sid)] = p.bar[i]
            p.bar[i] = sid
        elif tok in ('delete', 'backspace') and g.map.kind == 'town':
            p.bar[self.slot] = None


class ShopScreen(Modal):
    title = 'Outfitter'
    SUPPLIES = E.SUPPLIES

    def __init__(self, app, key=None):
        super().__init__(app)
        self.pane = 0   # 0 = buy, 1 = sell
        self.sel = [0, 0]
        self.key = key if key is not None else self.game.home

    def buy_rows(self):
        g = self.game
        from .entities import Item
        rows = [Item(0, k, t) for k, t in self.SUPPLIES]
        return rows + list(g.shops.get(self.key, []))

    def sell_rows(self):
        return [it for it in self.game.backpack() if it.k not in ('quest', 'corpse')]

    def render(self, cv):
        g = self.game
        x, y = self.box(cv, 104, 30)
        cv.text(x + 2, y + 1, '"Fresh stock every time you come back to town."', DIM, PANEL)
        cv.text_right(x + 101, y + 1, 'Your purse: ' + fmt(g.player.gold), GOLD, PANEL)
        lists = [self.buy_rows(), self.sell_rows()]
        for pane, (title, lx) in enumerate((('BUY', x + 2), ('SELL', x + 34))):
            active = pane == self.pane
            cv.text(lx, y + 3, title + (' ◄' if active else ''), GOLD if active else DIM, PANEL)
            rows = lists[pane]
            self.sel[pane] = max(0, min(self.sel[pane], len(rows) - 1))
            for i, it in enumerate(rows[:24]):
                yy = y + 4 + i
                sel = active and i == self.sel[pane]
                bg = (52, 40, 28) if sel else PANEL
                cv.fill(lx, yy, 30, 1, ' ', FG, bg)
                cv.text(lx, yy, LETTERS[i] if active else ' ', GOLD, bg)
                price = it.value() if pane == 0 else max(1, it.value() // 4)
                cv.text(lx + 2, yy, it.display_name(), it.color(), bg, maxw=22)
                cv.text_right(lx + 29, yy, fmt(price, True), GOLD if (pane == 1 or g.player.gold >= price) else BAD, bg)
            if not rows:
                cv.text(lx, y + 4, 'Nothing to sell.' if pane else 'Sold out.', DIM, PANEL)
        for yy in range(y + 1, y + 29):
            cv.put(x + 65, yy, '│', LINE, PANEL)
        cur = lists[self.pane]
        if cur:
            item_detail(cv, g, cur[self.sel[self.pane]], x + 67, y + 3, 35, 22)
        n, cost = g.identify_all(dry=True)
        if n:
            cv.text(x + 67, y + 27, f'I: identify {n} item{"s" if n > 1 else ""} ({cost}g)', GOLD, PANEL)
        cv.text_center(W // 2, y + 29, ' Tab: buy/sell · letter or arrows: select · Enter: buy or sell · I: identify · Esc: leave ', DIM, PANEL)

    def activate(self):
        g = self.game
        g.log_mark = len(g.log)
        i = self.sel[self.pane]
        if self.pane == 0:
            if i < len(self.SUPPLIES):
                g.buy_supply(i)
            else:
                g.buy_gear(i - len(self.SUPPLIES), self.key)
        else:
            rows = self.sell_rows()
            if i < len(rows):
                g.sell(rows[i])

    def on_key(self, tok, shift):
        rows = self.buy_rows() if self.pane == 0 else self.sell_rows()
        if tok == 'I':
            self.game.log_mark = len(self.game.log)
            self.game.identify_all()
            return
        if tok == 'esc':
            self.app.pop()
        elif tok in ('tab', 'left', 'right', 'np4', 'np6'):
            self.pane = 1 - self.pane
        elif tok in ('up', 'np8'):
            self.sel[self.pane] = max(0, self.sel[self.pane] - 1)
        elif tok in ('down', 'np2'):
            self.sel[self.pane] = min(len(rows) - 1, self.sel[self.pane] + 1)
        elif tok in ('enter', 'np_enter'):
            self.activate()
        elif len(tok) == 1 and tok in LETTERS and LETTERS.index(tok) < len(rows):
            i = LETTERS.index(tok)
            if self.sel[self.pane] == i:
                self.activate()
            self.sel[self.pane] = i


class TravelScreen(Modal):
    title = 'Travel'

    def places(self):
        g = self.game
        p = g.player
        here = g.here
        ox, oy = (here.x, here.y) if here else (p.x, p.y) if g.cur == 'over' else g.over_pos
        out = []
        for st in g.world.settlements:
            if g.known_settlement(st) and not (here and here.id == st.id):
                out.append(('s', st.id, st.name, st.kind_name, st.x, st.y))
        om = g.maps['over']
        for st in getattr(g.world, 'sites', ()):
            if om.seen[st.y * om.w + st.x]:
                out.append(('site', st.id, st.name, st.kind, st.x, st.y))
        for d in g.world.dungeons.values():
            if g.known_dungeon(d) and getattr(d, 'town', None) is None:
                out.append(('d', d.id, d.name, 'dungeon', d.x, d.y))
        out.sort(key=lambda r: cheb(r[4], r[5], ox, oy))
        self.origin = (ox, oy)
        return out[:24]

    def render(self, cv):
        g = self.game
        pl = self.places()
        x, y = self.box(cv, 76, min(30, len(pl) + 6))
        cv.text(x + 2, y + 1, 'Walk to a known place, along roads where possible. Danger nearby stops you.', DIM, PANEL)
        targets = {}
        for mi in MS.active(g):
            pos, _ = MS.target_pos(g, mi)
            targets[tuple(pos)] = mi.title
        ox, oy = self.origin
        for i, (k, ref, name, kind, px, py) in enumerate(pl):
            yy = y + 3 + i
            cv.text(x + 2, yy, LETTERS[i], GOLD, PANEL)
            cv.text(x + 4, yy, name, FG, PANEL)
            cv.text(x + 25, yy, kind, DIM, PANEL)
            d = cheb(px, py, ox, oy)
            cv.text(x + 34, yy, f'{d:>3} {E.dir_name(px - ox, py - oy) if d else "here"}', DIM, PANEL)
            if (px, py) in targets:
                cv.text(x + 50, yy, '► ' + targets[(px, py)], GOLD, PANEL, maxw=24)
        cv.text_center(W // 2, y + min(30, len(pl) + 6) - 1, ' letter: go · Esc: cancel ', DIM, PANEL)

    def on_key(self, tok, shift):
        g = self.game
        if tok == 'esc':
            self.app.pop()
            return
        pl = self.places()
        if len(tok) == 1 and tok in LETTERS[:len(pl)]:
            k, ref = pl[LETTERS.index(tok)][:2]
            self.app.pop()
            g.log_mark = len(g.log)
            self.app.start_auto(g.travel_iter(k, ref), .025, 'Travelling')


class DialogScreen(Modal):
    def __init__(self, app, title, text):
        super().__init__(app)
        self.title, self.text = title, text

    def render(self, cv):
        lines = wrap_text(self.text, 60)
        h = len(lines) + 5
        x, y = self.box(cv, 66, h)
        for i, ln in enumerate(lines):
            cv.text(x + 3, y + 2 + i, ln, FG, PANEL)
        cv.text_center(W // 2, y + h - 1, ' Enter or Esc to continue ', DIM, PANEL)

    def on_key(self, tok, shift):
        if tok in ('esc', 'enter', 'np_enter', 'space'):
            self.app.pop()


class QuitScreen(Modal):
    title = 'Leave the vale?'

    def render(self, cv):
        x, y = self.box(cv, 50, 7)
        cv.text(x + 3, y + 2, 'Your hero is saved and will be waiting.', FG, PANEL)
        cv.text(x + 3, y + 4, '[Y] Save and quit    [N] Keep playing', GOLD, PANEL)

    def on_key(self, tok, shift):
        if tok in ('y', 'Y', 'enter'):
            self.app.quit()
        elif tok in ('n', 'N', 'esc'):
            self.app.pop()


class HelpScreen(Modal):
    title = 'Help'
    PAGES = [
        ('Controls', [
            ('arrows · numpad · hjkl yubn', 'Move. Walk into a monster to fight it, into a door to open it.'),
            ('Shift + direction', 'Run, until something interesting happens'),
            ('Enter  or  Space', 'Do the obvious thing here: go in, take the stairs, pick up,'),
            ('', 'talk to whoever is near, read a signpost, open a chest, fish.'),
            ('1  2  3  4  5  6', 'Use a skill from your bar (it aims at the nearest enemy)'),
            ('q   w', 'Drink a health or a mana potion'),
            ('i', 'Your bag: what you carry and wear'),
            ('m', 'The map of the realm'),
            ('Tab', 'The menu: everything else you can do or look at'),
            ('Esc', 'Back, close a window; on the map: save and quit'),
            ('?', 'This help'),
            ('.  or  5', 'Wait a turn'),
            ('', ''),
            ('Panel, bottom', 'What you can do where you stand, with its key: Enter go in,'),
            ('', 'T talk, a fish, E eat, F forage, R rest... Learn them as you go.'),
            ('', ''),
            ('That is all you need.', 'Everything else is in the menu (Tab). Each item there shows'),
            ('', 'a shortcut of its own, for when you know your way around:'),
            ('', 'c character, C life skills, z skills, v bestiary, e journal,'),
            ('', 't travel, x explore, o look, g pick up, P brewing...'),
            ('', 'A capital letter means: with Shift.'),
            ('', ''),
            ('F11  Alt+Enter', 'Fullscreen'),
        ]),
        ('The world', [
            ('Roads', 'Roads are patrolled and fairly safe. The further you stray, the worse it gets.'),
            ('Danger', 'Inspect the land (O) to see its danger. Night brings the dead and bigger packs.'),
            ('Knowledge', 'You only know the land around Thornfield. Signposts (┬), townsfolk and travellers'),
            ('', 'tell you where places lie, but the land and roads you only learn by walking them.'),
            ('Π ruin', 'An old ruin with a way down. Small, with a skill tome at the bottom.'),
            ('† shrine', 'Pray for a blessing. An offering makes it last longer. Every shrine has its god.'),
            ('∆ camp', 'A bandit camp. Kill them all and the strongbox is yours.'),
            ('Ψ stones', 'Standing stones. Touch them to learn from old memories.'),
            ('¤ wagon', 'An abandoned wagon. Loot, or a trap.'),
            ('Events', 'On the road things happen: wounded travellers, peddlers, tolls, storms...'),
            ('@ travellers', 'Walk into a traveller to talk. Some have a job for you and wait for you afterwards'),
            ('', 'at the inn of the town they were going to (see the journal).'),
            ('Towns', 'Trader: goods · innkeeper: jobs · outfitter: gear, identify · temple: heal, curses'),
            ('', 'stablemaster: mules and carts · castellan (in strongholds): war jobs'),
            ('Factions', 'Different every world. Work for one to win favour; hurt it and its gates close.'),
            ('Peoples', 'Humans, elves, dwarves, halflings and half-orcs each like and distrust each other.'),
            ('', 'How a town sees your people changes its prices and how its faction greets you.'),
            ('News', 'Listen to the news and to rumours. The world changes while you are busy.'),
            ('Calendar', 'Twelve months of thirty days, from Deepfrost to Longnight; seven days in a week.'),
        ]),
        ('Weather', [
            ('Seasons', 'Each region has its own weather: the cold north and mountains, the hot dry south,'),
            ('', 'the marshes and the mild middle. It changes with the seasons, and by steps: drizzle'),
            ('', 'grows into rain before it pours, a blizzard dies down to snow before the sky clears.'),
            ('Sight', 'Rain, snow, mist, fog and dust shorten your sight; thick fog and sandstorms a lot.'),
            ('Travel', 'Snow, storms and sand slow you down; ambushes are likelier when you cannot see.'),
            ('Body', 'Cold weather makes you hungry sooner, and so does scorching heat.'),
            ('Magic', 'Fire sputters in the wet and burns hotter in the heat; storm magic loves a storm.'),
            ('Danger', 'In a thunderstorm, open land is no place to be: lightning strikes.'),
            ('Omens', 'Falling ash, a sickly miasma, smoke on the wind: a great evil is near.'),
            ('Quiet', 'Fireflies on summer nights, the northern lights in winter, dew in the morning.'),
            ('', 'Under a roof you stay dry.'),
            ('', ''),
            ('! and ?', 'A blinking ! over someone: they have work for you. A ? : you can hand a job in.'),
            ('Towns', 'Hamlet, village, town, city, metropolis. Farms along the roads share a meal with'),
            ('', 'travellers; roadside inns offer a bed and the news.'),
        ]),
        ('Gods', [
            ('Solmara', 'the Dawnmother: light, healing and mercy. Hates the undead.'),
            ('Valdric', 'the Iron Judge: law, oaths and kings. Patron of the crown. Hunts outlaws.'),
            ('Thessa', 'the Green Mother: harvest, beasts and the wild. Loves foragers and fishers.'),
            ('Durnak', 'the Deep Smith: forge, stone and the dead. God of the dwarves.'),
            ('Skell', 'the Grey Wanderer: luck, roads, trade and thieves.'),
            ('Morrak', 'the Hollow King: death and hunger. No honest temple serves him.'),
            ('', ''),
            ('Devotion', 'At a temple you can swear yourself to its god. Pray there once a day, leave'),
            ('', 'offerings and do what your god likes, and their favour grows: at "favoured" and'),
            ('', '"chosen" they bless you, and prayer at their temples heals you.'),
            ('Rivals', 'Solmara and Morrak, Valdric and Skell, Thessa and Durnak are old enemies.'),
            ('', 'Factions that worship a rival of your god trust you less, and the priests of'),
            ('', 'a rival temple will not tend to you. Choose with care, or choose no god at all.'),
        ]),
        ('Your hero', [
            ('Skills', 'You start with none. Learn them from tomes (≡) found on monsters, in ruins, at'),
            ('', 'standing stones, from peddlers and city outfitters. Disciplines grow by use and'),
            ('', 'decide which tomes you can understand. Carry six skills; change them in a town (Z).'),
            ('Life skills', 'Grow by doing. Fishing (A by water, with a pole), foraging (Shift+F), herbalism'),
            ('', '(picking and knowing herbs), alchemy (potions, P) and brewing (ale, wine, mead, P).'),
            ('Magic items', 'Rare, and unidentified when found. Outfitters and priests identify them.'),
            ('', 'Some are cursed: once worn they stay on until a priest lifts the curse.'),
            ('Bestiary', 'Every kill teaches you. Higher knowledge: more damage against that kind,'),
            ('', 'and they hit you less often (V).'),
            ('Death', 'Hardcore: final. Softcore: you wake in a temple; your pack stays with your body.'),
            ('Rarity', 'normal · magic (blue) · rare (yellow) · unique (gold)'),
            ('X  T', 'Auto-explore and travel play out step by step; press any key to stop.'),
        ]),
    ]

    def __init__(self, app):
        super().__init__(app)
        self.page = 0

    def render(self, cv):
        name, rows = self.PAGES[self.page]
        x, y = self.box(cv, 104, 28, f'Help: {name} ({self.page + 1}/{len(self.PAGES)})')
        kw = 28 if self.page == 0 else 14
        for i, (k, d) in enumerate(rows):
            cv.text(x + 3, y + 2 + i, k, GOLD, PANEL, maxw=kw)
            cv.text(x + 4 + kw, y + 2 + i, d, FG, PANEL, maxw=98 - kw)
        cv.text_center(W // 2, y + 27, ' Left/Right or Space: next page · Esc: close ', DIM, PANEL)

    def on_key(self, tok, shift):
        if tok in ('right', 'space', 'np6', 'tab', 'l', 'enter', 'pagedown'):
            self.page = (self.page + 1) % len(self.PAGES)
        elif tok in ('left', 'np4', 'h', 'pageup'):
            self.page = (self.page - 1) % len(self.PAGES)
        else:
            self.app.pop()


class LookScreen(Modal):
    tall = False
    """Inspect: move a cursor over the map and read what is there."""
    dim = False

    def __init__(self, app):
        super().__init__(app)
        g = self.game
        p = g.player
        self.x, self.y = p.x, p.y
        self.targets = self.find_targets()
        if self.targets:
            self.x, self.y = self.targets[0]
        self.ti = 0

    def find_targets(self):
        g = self.game
        p = g.player
        m = g.map
        pts = []
        if m.kind == 'over':
            pts += [(wd.x, wd.y) for wd in g.world.wanderers if g.visible(wd.x, wd.y)]
        else:
            pts += [(o.x, o.y) for o in m.mons if g.visible(o.x, o.y)]
            pts += [(it.x, it.y) for it in m.items if g.visible(it.x, it.y)]
        pts = sorted(set(pts), key=lambda c: cheb(c[0], c[1], p.x, p.y))
        return pts

    def render(self, cv):
        from . import describe as DS
        g = self.game
        gs = self.app.screens[0]
        ox, oy = getattr(gs, 'origin', (0, 0))
        vx, vy = self.x - ox, self.y - oy
        if 0 <= vx < MAP_W and 0 <= vy < MAP_H:
            cv.put_bg(vx, vy, (150, 120, 30))
        title, col, lines = DS.at(g, self.x, self.y)
        cv.fill(0, LOG_Y, MAP_W, H - LOG_Y, ' ', FG, (24, 20, 16))
        cv.text(1, LOG_Y, title, col, (24, 20, 16), maxw=MAP_W - 2)
        yy = LOG_Y + 1
        for ln in lines:
            for part in wrap_text(ln, MAP_W - 4):
                if yy < H - 1:
                    cv.text(2, yy, part, FG, (24, 20, 16))
                    yy += 1
        cv.text(1, H - 1, 'move: look around · Tab: next thing · Esc: done', DIM, (24, 20, 16))

    def on_key(self, tok, shift):
        d = DIRS.get(tok)
        if not d and tok in RUN_LETTERS:
            d, shift = DIRS[RUN_LETTERS[tok]], True
        if d:
            step = 5 if shift else 1
            m = self.game.map
            self.x = max(0, min(m.w - 1, self.x + d[0] * step))
            self.y = max(0, min(m.h - 1, self.y + d[1] * step))
        elif tok == 'tab' and self.targets:
            self.ti = (self.ti + 1) % len(self.targets)
            self.x, self.y = self.targets[self.ti]
        elif tok in ('esc', 'enter', 'o', ';', 'space'):
            self.app.pop()


class ChoiceScreen(Modal):
    """A small event: some text and a few lettered choices."""

    def render(self, cv):
        ev = self.game.pending
        if not ev:
            return
        lines = wrap_text(ev['text'], 60)
        h = len(lines) + len(ev['options']) + 7
        x, y = self.box(cv, 66, h, ev['title'])
        for i, ln in enumerate(lines):
            cv.text(x + 3, y + 2 + i, ln, FG, PANEL)
        yy = y + 3 + len(lines)
        for i, (label, _k) in enumerate(ev['options']):
            cv.text(x + 3, yy + i, LETTERS[i], GOLD, PANEL)
            cv.text(x + 5, yy + i, label, FG, PANEL, maxw=58)
        cv.text_center(W // 2, y + h - 1, ' press a letter to choose ', DIM, PANEL)

    def choose(self, key):
        g = self.game
        self.app.pop()
        g.log_mark = len(g.log)
        EV.resolve(g, key)

    def on_key(self, tok, shift):
        ev = self.game.pending
        if not ev:
            self.app.pop()
            return
        opts = ev['options']
        if len(tok) == 1 and tok in LETTERS[:len(opts)]:
            self.choose(opts[LETTERS.index(tok)][1])
        elif tok == 'esc':
            leave = [k for _l, k in opts if k == 'leave']
            if leave or len(opts) == 1:
                self.choose(leave[0] if leave else opts[0][1])


class BestiaryScreen(Modal):
    def __init__(self, app):
        super().__init__(app)
        self.sel = 0

    def entries(self):
        b = self.game.bestiary
        return sorted(b, key=lambda k: (D.MONSTERS[k].get('min_l', 1), D.MONSTERS[k]['name']))

    def render(self, cv):
        g = self.game
        x, y = self.box(cv, 100, 28, 'Bestiary')
        keys = self.entries()
        if not keys:
            cv.wrap(x + 3, y + 3, 90, 'You have not met any creatures yet. Every monster you see is recorded here, '
                    'and every one you kill teaches you more about its kind.', DIM, PANEL)
            cv.text_center(W // 2, y + 27, ' Esc: close ', DIM, PANEL)
            return
        self.sel = max(0, min(self.sel, len(keys) - 1))
        top = max(0, self.sel - 22)
        for i, k in enumerate(keys[top:top + 24]):
            d = D.MONSTERS[k]
            yy = y + 2 + i
            sel = top + i == self.sel
            if sel:
                cv.fill(x + 1, yy, 34, 1, ' ', FG, (50, 40, 30))
            bg = (50, 40, 30) if sel else PANEL
            cv.text(x + 2, yy, d['ch'], d['fg'], bg)
            cv.text(x + 4, yy, d['name'], FG if sel else DIM, bg, maxw=22)
            r = g.lore(k)
            cv.text_right(x + 34, yy, str(r), GOLD if r else DIM, bg)
        for yy in range(y + 1, y + 27):
            cv.put(x + 36, yy, '│', LINE, PANEL)
        k = keys[self.sel]
        d = D.MONSTERS[k]
        seen, kills = g.bestiary[k]
        r = g.lore(k)
        rx, w = x + 38, 59
        cv.text(rx, y + 2, d['ch'], d['fg'], PANEL)
        cv.text(rx + 2, y + 2, d['name'], d['fg'], PANEL)
        cv.text_right(rx + w - 1, y + 2, f'{E.LORE_RANKS[r][1]}', GOLD, PANEL)
        nxt = E.LORE_RANKS[r + 1][0] if r + 1 < len(E.LORE_RANKS) else None
        cv.text(rx, y + 3, f'First seen on day {seen} · {kills} slain' + (f' · next rank at {nxt}' if nxt else ' · mastered'), DIM, PANEL)
        lore = D.LORE.get(k, ('A creature of the vale.', 'Unknown.', 'No advice yet.'))
        yy = y + 5
        yy += cv.wrap(rx, yy, w, lore[0], FG, PANEL, 3) + 1
        if r >= 1:
            cv.text(rx, yy, 'HABITAT', DIM, PANEL)
            yy += 1
            yy += cv.wrap(rx, yy, w, lore[1], FG, PANEL, 2) + 1
            traits = [t for t, on in (('fast', d['fast']), ('slow', d['slow']), ('ranged', d['ranged']),
                                      ('spellcaster', d['caster']), ('poisonous', d['poison']), ('regenerates', d['regen']),
                                      ('drains life', d['leech']), ('erratic', d['erratic']), ('summoner', bool(d['summon'])))
                      if on]
            cv.text(rx, yy, 'TRAITS', DIM, PANEL)
            cv.text(rx + 8, yy, ', '.join(traits) or 'none to speak of', FG, PANEL, maxw=w - 8)
            yy += 2
        else:
            cv.text(rx, yy, 'Slay 3 to learn where they live and how they fight.', DIM, PANEL)
            yy += 2
        if r >= 2:
            cv.text(rx, yy, 'STRENGTH', DIM, PANEL)

            def word(v):
                return 'very low' if v < .7 else 'low' if v < .95 else 'average' if v < 1.25 else 'high' if v < 1.7 else 'very high'
            cv.text(rx + 10, yy, f"health {word(d['hp'])} · damage {word(d['dmg'])} · armor {word(d['df'])}", FG, PANEL, maxw=w - 10)
            yy += 1
            if d.get('min_l'):
                cv.text(rx + 10, yy, f"found from danger level {d['min_l']} and up", FG, PANEL, maxw=w - 10)
                yy += 1
            yy += 1
        elif r == 1:
            cv.text(rx, yy, 'Slay 10 to judge their strength.', DIM, PANEL)
            yy += 2
        if r >= 3:
            cv.text(rx, yy, "HUNTER'S TIP", DIM, PANEL)
            yy += 1
            yy += cv.wrap(rx, yy, w, lore[2], GOOD, PANEL, 2) + 1
        elif r == 2:
            cv.text(rx, yy, "Slay 25 to learn a hunter's secret.", DIM, PANEL)
            yy += 2
        cv.text(rx, y + 24, 'YOUR KNOWLEDGE', DIM, PANEL)
        cv.text(rx, y + 25, f'+{3 * r}% damage against them · they hit you {2 * r}% less often', GOLD if r else DIM, PANEL)
        cv.text_center(W // 2, y + 27, ' Up/Down: browse · Esc: close ', DIM, PANEL)

    def on_key(self, tok, shift):
        if tok in ('up', 'np8', 'k'):
            self.sel -= 1
        elif tok in ('down', 'np2', 'j'):
            self.sel += 1
        elif tok == 'pageup':
            self.sel -= 10
        elif tok == 'pagedown':
            self.sel += 10
        elif tok in ('esc', 'v', 'f2', 'enter'):
            self.app.pop()
        n = len(self.entries())
        self.sel = max(0, min(self.sel, n - 1)) if n else 0


class IntroScreen(Modal):
    """A short opening for a new game, written for this world."""

    @property
    def PAGES(self):
        g = self.game
        if not g:
            return [('', '')] * 3
        from . import races as RC
        p = g.player
        r = RC.RACES[p.race]
        return [
            ('...',
             'Darkness. Then voices, far away. Then the smell of candle smoke.\n\n'
             'You open your eyes on a stone ceiling. Your head aches, your mouth is dry, and when you try to remember '
             'how you got here, there is nothing. No road, no home, no faces. Nothing at all.'),
            ('A name',
             f'Only one thing is left: your name. {p.name}. You hold on to it like a rope in deep water.\n\n'
             f'Your hands are the hands of a {r["name"].lower()}. A padded coat lies beside your cot, the only thing '
             'that might be yours. Whatever you were before, nobody here knows it. Neither do you.'),
            ('{name}',
             'This is Avarenthia, in the year 1172 After the Ruin: an old land built on the bones of an older one. '
             'You are nobody here. What you become now is up to you: a sellsword, a trader, a scholar of forgotten '
             'magic, a thief on the roads, or something else entirely. Fortune, fame or folly.\n\n'
             'Talk to people, and listen: they know more than they think. The world is wide, and it does not wait.\n\n'
             'Enter does the obvious thing, Tab opens the menu, ? is help.'),
        ]

    def __init__(self, app):
        super().__init__(app)
        self.page = 0

    def render(self, cv):
        title, text = self.PAGES[self.page]
        title = title.format(name=self.game.player.name if self.game else 'You')
        x, y = self.box(cv, 72, 24, f' {title} ')
        yy = y + 2
        for para in text.split('\n\n'):
            yy += cv.wrap(x + 4, yy, 64, para, FG, PANEL) + 1
        dots = '  '.join('•' if i == self.page else '○' for i in range(len(self.PAGES)))
        cv.text_center(W // 2, y + 21, dots, GOLD, PANEL)
        last = self.page == len(self.PAGES) - 1
        cv.text_center(W // 2, y + 23, ' Enter: begin your journey ' if last else ' Enter: continue · Esc: skip ', DIM, PANEL)

    def on_key(self, tok, shift):
        if tok == 'esc':
            self.app.pop()
        elif tok in ('enter', 'space', 'right', 'np_enter', 'np6'):
            if self.page < len(self.PAGES) - 1:
                self.page += 1
            else:
                self.app.pop()
        elif tok in ('left', 'np4', 'backspace') and self.page:
            self.page -= 1


class DeathScreen(Modal):
    title = 'You have died'

    def render(self, cv):
        g = self.game
        p = g.player
        x, y = self.box(cv, 60, 15)
        cv.wrap(x + 3, y + 2, 54, f"{p.name} was slain by {g.cause or 'fate'} in {g.loc_name()}. In hardcore, death is final.", FG, PANEL)
        rows = [('Level', p.lvl), ('Experience', p.xp), ('Turns', g.turn), ('Kills', g.kills), ('Money', fmt(p.gold))]
        for i, (a, b) in enumerate(rows):
            cv.text(x + 3, y + 5 + i, a, DIM, PANEL)
            cv.text(x + 18, y + 5 + i, str(b), FG, PANEL)
        cv.text(x + 3, y + 12, '[N] New game    [Esc] Quit', GOLD, PANEL)

    def on_key(self, tok, shift):
        if tok in ('n', 'enter'):
            self.app.game = None
            self.app.screens = [NameScreen(self.app)]
        elif tok == 'esc':
            self.app.running = False


class WinScreen(Modal):
    title = 'The vale is saved'

    def render(self, cv):
        g = self.game
        p = g.player
        x, y = self.box(cv, 64, 15)
        names = ', '.join(e.name for e in g.world.evils)
        cv.wrap(x + 3, y + 2, 58, f"{p.name} has destroyed {names}. The vale is free, and Thornfield will sing of this for generations.", FG, PANEL, 3)
        rows = [('Level', p.lvl), ('Turns', g.turn), ('Kills', g.kills), ('Money', fmt(p.gold))]
        for i, (a, b) in enumerate(rows):
            cv.text(x + 3, y + 6 + i, a, DIM, PANEL)
            cv.text(x + 18, y + 6 + i, str(b), FG, PANEL)
        cv.text(x + 3, y + 12, '[Enter] Keep exploring    [N] New game', GOLD, PANEL)

    def on_key(self, tok, shift):
        if tok in ('enter', 'esc'):
            self.app.pop()
        elif tok == 'n':
            E.save_game(self.game)
            self.app.game = None
            self.app.screens = [NameScreen(self.app)]


# ====================================================================== trade and jobs
def _stock_word(s, g):
    st = s.market[g][0]
    return 'none' if st < 1 else 'scarce' if st < 12 else 'some' if st < 45 else 'plenty'


class MarketScreen(Modal):
    BOX_W, BOX_H = 104, 26

    def __init__(self, app, sid):
        super().__init__(app)
        self.sid = sid
        self.sel = 0
        ECO.record_prices(self.game, self.settlement)

    @property
    def settlement(self):
        return self.game.world.settlements[self.sid]

    def render(self, cv):
        g = self.game
        s = self.settlement
        p = g.player
        x, y = self.box(cv, self.BOX_W, self.BOX_H, f'{s.name} market')
        cap, used = ECO.cargo_capacity(p), ECO.cargo_weight(p)
        cv.text(x + 2, y + 1, f'Purse {fmt(p.gold)}', GOLD, PANEL)
        cv.text(x + 16, y + 1, f'Cargo {used}/{cap}', BAD if used >= cap else FG, PANEL)
        cv.text(x + 32, y + 1, f'Reputation here {s.rep}', DIM, PANEL)
        if s.event:
            cv.text(x + 56, y + 1, D.EVENTS[s.event[0]]['text'].format(town=s.name), INFO, PANEL, maxw=46)
        hdr = y + 3
        cols = [(4, 'Good'), (22, 'Buy'), (29, 'Sell'), (36, 'Stock'), (45, 'Yours'), (53, 'Paid'), (60, 'Best known sale elsewhere')]
        for cx, t in cols:
            cv.text(x + cx, hdr, t, DIM, PANEL)
        for i, gk in enumerate(D.GOOD_ORDER):
            yy = hdr + 1 + i
            sel = i == self.sel
            bg = (52, 40, 28) if sel else PANEL
            cv.fill(x + 2, yy, self.BOX_W - 4, 1, ' ', FG, bg)
            mark = '+' if gk in s.produce else '!' if gk in s.demand else ' '
            cv.text(x + 2, yy, mark, GOOD if mark == '+' else BAD if mark == '!' else DIM, bg)
            cv.text(x + 4, yy, D.GOODS[gk]['name'], FG, bg)
            cv.text(x + 22, yy, fmt(ECO.buy_price(s, gk), True), FG, bg)
            cv.text(x + 29, yy, fmt(ECO.sell_price(s, gk), True), FG, bg)
            sw = _stock_word(s, gk)
            cv.text(x + 36, yy, sw, {'none': BAD, 'scarce': BAD, 'some': FG, 'plenty': GOOD}[sw], bg)
            have = p.cargo.get(gk, 0)
            cv.text(x + 45, yy, str(have) if have else '-', GOLD if have else DIM, bg)
            if have and gk in p.cost_basis:
                cv.text(x + 53, yy, fmt(p.cost_basis[gk], True), DIM, bg)
            best = ECO.best_known_sale(g, gk, s.id)
            if best:
                v, bsid, day = best
                age = g.day - day
                col = GOOD if v > ECO.buy_price(s, gk) else DIM
                cv.text(x + 60, yy, f"{fmt(v, True)} in {g.world.settlements[bsid].name} ({'today' if age == 0 else f'{age}d ago'})", col, bg, maxw=42)
        cv.text(x + 2, y + self.BOX_H - 3, '+ made here (cheap)   ! wanted here (sells high)   weight: ' +
                f"{D.GOODS[D.GOOD_ORDER[self.sel]]['name']} {D.GOODS[D.GOOD_ORDER[self.sel]]['w']} per unit", DIM, PANEL)
        cv.text_center(W // 2, y + self.BOX_H - 1, ' ↑↓ select · b/s buy or sell 1 · B/S buy or sell 10 · A sell all · Esc leave ', DIM, PANEL)

    def on_key(self, tok, shift):
        g = self.game
        s = self.settlement
        gk = D.GOOD_ORDER[self.sel]
        if tok == 'esc':
            ECO.record_prices(g, s)
            self.app.pop()
            return
        if tok in ('up', 'np8', 'k'):
            self.sel = (self.sel - 1) % len(D.GOOD_ORDER)
        elif tok in ('down', 'np2', 'j'):
            self.sel = (self.sel + 1) % len(D.GOOD_ORDER)
        elif tok in ('b', 'B', 's', 'S', 'A'):
            g.log_mark = len(g.log)
            if tok in ('b', 'B'):
                ECO.buy(g, s, gk, 10 if tok == 'B' or shift else 1)
            else:
                n = g.player.cargo.get(gk, 0) if tok == 'A' else 10 if (tok == 'S' or shift) else 1
                if n:
                    ECO.sell(g, s, gk, n)


class BoardScreen(Modal):
    BOX_W, BOX_H = 100, 26
    KINDS = {'courier': 'Courier', 'freight': 'Freight', 'bounty': 'Bounty hunt', 'escort': 'Escort', 'fetch': 'Dungeon delve',
             'war_bounty': 'War: hunt a commander', 'supply': 'War: supply run', 'assault': 'War: storm a stronghold'}

    def __init__(self, app, ref, hold=False):
        super().__init__(app)
        self.ref, self.hold = ref, hold
        self.sel = 0
        if hold:
            MS.refresh_hold_board(self.game, self.source)
        else:
            MS.refresh_board(self.game, self.source)

    @property
    def source(self):
        w = self.game.world
        return w.holds[self.ref] if self.hold else w.settlements[self.ref]

    def render(self, cv):
        g = self.game
        src = self.source
        name = src.title if self.hold else src.name
        x, y = self.box(cv, self.BOX_W, self.BOX_H, f"{'Castellan' if self.hold else 'Job board'} · {name}")
        f = src.faction
        frep = g.player.rep.get(f, 0)
        local = f'Reputation here {src.rep} · ' if not self.hold else ''
        cv.text(x + 2, y + 1, f"{local}{D.FACTIONS[f]['short']}: {WAR.standing(frep)} ({frep}) · {len(MS.active(g))}/{MS.MAX_ACTIVE} jobs taken",
                DIM, PANEL)
        offers = src.board
        self.sel = max(0, min(self.sel, len(offers) - 1))
        if not offers:
            cv.text(x + 4, y + 3, 'No work today. Come back in a few days.', DIM, PANEL)
        for i, mi in enumerate(offers):
            yy = y + 3 + i
            sel = i == self.sel
            bg = (52, 40, 28) if sel else PANEL
            cv.fill(x + 2, yy, 54, 1, ' ', FG, bg)
            cv.text(x + 2, yy, LETTERS[i], GOLD, bg)
            cv.text(x + 4, yy, mi.title, FG, bg, maxw=42)
            cv.text_right(x + 55, yy, fmt(mi.reward, True), GOLD, bg)
        for yy in range(y + 1, y + self.BOX_H - 1):
            cv.put(x + 58, yy, '│', LINE, PANEL)
        if offers:
            mi = offers[self.sel]
            cv.text(x + 60, y + 3, mi.title, GOLD, PANEL, maxw=38)
            n = cv.wrap(x + 60, y + 5, 38, mi.desc, FG, PANEL, 10)
            yy = y + 6 + n
            cv.text(x + 60, yy, f'Reward: {fmt(mi.reward)}', GOLD, PANEL)
            local_rep = src.rep if not self.hold else max(0, frep)
            if local_rep > 0:
                cv.text(x + 60, yy + 1, f'+{fmt(round(mi.reward * min(local_rep, 100) / 200))} reputation bonus', GOOD, PANEL)
            if mi.deadline:
                cv.text(x + 60, yy + 2, f'Deadline: {CAL.short(mi.deadline)} (today {CAL.short(g.day)})', DIM, PANEL, maxw=38)
            cv.text(x + 60, yy + 3, self.KINDS[mi.kind], INFO, PANEL)
            if mi.faction:
                cv.text(x + 60, yy + 4, f"Reputation with the {D.FACTIONS[mi.faction]['short']}: +{mi.rep if self.hold else 2}", GOOD, PANEL)
        from . import crime as CR
        notices = [st for st in CR.wanted_in(g) if self.hold or st.id != src.id]
        if notices:
            st = notices[0]
            what = (getattr(st, 'crimes', None) or ['crimes'])[-1]
            cv.text(x + 2, y + self.BOX_H - 4, 'Nailed to the board:', DIM, PANEL)
            cv.text(x + 2, y + self.BOX_H - 3, f'WANTED: {g.player.name}, for {what} near {st.name}. Reward {fmt(CR.bounty(st))}.',
                    BAD, PANEL, maxw=56)
        if not self.hold:
            cv.text(x + 60, y + self.BOX_H - 4, f'm: a bowl of stew ({fmt(g.STEW)})', GOLD, PANEL)
            cv.text(x + 60, y + self.BOX_H - 3, f'M: a hot meal and a bed ({fmt(g.MEAL)})', GOLD, PANEL)
        cv.text_center(W // 2, y + self.BOX_H - 1, ' letter or ↑↓ select · Enter accept · Esc leave ', DIM, PANEL)

    def on_key(self, tok, shift):
        g = self.game
        s = self.source
        if tok == 'esc':
            self.app.pop()
        elif tok == 'M' and not self.hold:
            g.log_mark = len(g.log)
            g.inn_meal()
        elif tok == 'm' and not self.hold:
            g.log_mark = len(g.log)
            g.inn_stew()
        elif tok in ('up', 'np8'):
            self.sel = max(0, self.sel - 1)
        elif tok in ('down', 'np2'):
            self.sel = min(len(s.board) - 1, self.sel + 1)
        elif tok in ('enter', 'np_enter') and s.board:
            g.log_mark = len(g.log)
            MS.accept(g, s, s.board[self.sel])
        elif len(tok) == 1 and tok in LETTERS and LETTERS.index(tok) < len(s.board):
            i = LETTERS.index(tok)
            if i == self.sel:
                g.log_mark = len(g.log)
                MS.accept(g, s, s.board[i])
            self.sel = i


class JournalScreen(Modal):
    def render(self, cv):
        g = self.game
        p = g.player
        x, y = self.box(cv, 100, 28, f'Journal · {CAL.long(g.day)}')
        here = g.here
        ox, oy = (here.x, here.y) if here else (p.x, p.y) if g.cur == 'over' else g.over_pos
        yy = y + 1
        story = g.story()
        if story:
            cv.text(x + 2, yy, 'STORY', DIM, PANEL)
            yy += 1
            for title, text in story:
                cv.text(x + 2, yy, '♦', GOLD, PANEL)
                cv.text(x + 4, yy, title, GOLD, PANEL, maxw=24)
                yy += cv.wrap(x + 30, yy, 67, text, FG, PANEL, 2)
            yy += 1
        heard = getattr(g, 'rumours', [])[-4:]
        if heard:
            cv.text(x + 2, yy, 'HEARD ON THE ROAD', DIM, PANEL)
            yy += 1
            for line in reversed(heard):
                cv.text(x + 2, yy, '·', GOLD, PANEL)
                n = len(wrap_text(line, 93)[:2])
                cv.wrap(x + 4, yy, 93, line, scale(FG, .85), PANEL, 2)
                yy += n
            yy += 1
        cv.text(x + 2, yy, 'ACTIVE JOBS', DIM, PANEL)
        jobs = MS.active(g)
        yy += 1
        if not jobs:
            cv.text(x + 4, yy, 'None. Visit the inn of any town to find work.', DIM, PANEL)
            yy += 1
        for mi in jobs:
            (tx, ty), where = MS.target_pos(g, mi)
            d = cheb(tx, ty, ox, oy)
            status = 'return for reward' if mi.state == 'turnin' else 'in progress'
            cv.text(x + 2, yy, '•', GOLD, PANEL)
            cv.text(x + 4, yy, mi.title, FG, PANEL, maxw=44)
            cv.text(x + 50, yy, f'{where}: {d} {E.dir_name(tx - ox, ty - oy) if d else "here"}', INFO, PANEL, maxw=30)
            cv.text_right(x + 97, yy, fmt(mi.reward, True), GOLD, PANEL)
            extra = status
            if mi.deadline and mi.state == 'active':
                left = mi.deadline - g.day
                extra += f' · {left} day{"s" if left != 1 else ""} left' if left >= 0 else ' · overdue'
            if mi.kind == 'escort':
                extra += f" · caravan health {mi.data['hp']}"
            cv.text(x + 4, yy + 1, extra, DIM, PANEL)
            yy += 2
        yy += 1
        cv.text(x + 2, yy, 'CARGO', DIM, PANEL)
        yy += 1
        line = ', '.join(f"{q} {D.GOODS[k]['name']}" for k, q in p.cargo.items()) or 'empty'
        n = cv.wrap(x + 4, yy, 92, line + (f" · job cargo: {', '.join(pc['name'] for pc in p.parcels)}" if p.parcels else ''), FG, PANEL, 2)
        yy += n
        mounts = ', '.join(D.MOUNTS[k]['name'] for k in p.mounts) or 'none'
        cv.text(x + 4, yy, f'Capacity {ECO.cargo_capacity(p)} · animals: {mounts}', DIM, PANEL)
        yy += 2
        cv.text(x + 2, yy, 'FACTIONS', DIM, PANEL)
        from . import gods as GD
        cv.text_right(x + 97, yy, 'Faith: ' + GD.standing(g), GD.GODS[p.god]['fg'] if getattr(p, 'god', None) else DIM, PANEL)
        yy += 1
        for f in D.FACTION_ORDER:
            fd = D.FACTIONS[f]
            r = g.player.rep[f] if f != 'cult' else -100
            holds = sum(1 for h in g.world.holds if h.faction == f)
            regs = sum(1 for rg in g.world.regions if rg.faction == f)
            cv.text(x + 4, yy, fd['name'], fd['fg'], PANEL)
            cv.text(x + 32, yy, f'{WAR.standing(r)} ({r})', BAD if WAR.is_hostile(g, f) else GOOD if r >= 10 else FG, PANEL)
            cv.text(x + 52, yy, f"{regs} region{'s' if regs != 1 else ''}, {holds} stronghold{'s' if holds != 1 else ''}", DIM, PANEL)
            pat = GD.PATRON.get(f)
            if pat:
                cv.text_right(x + 97, yy, f"worships {GD.GODS[pat]['name']}", scale(GD.GODS[pat]['fg'], .75), PANEL)
            yy += 1
        yy += 1
        from . import crime as CR
        marked = [st for st in g.world.settlements if st.rep and g.known_settlement(st)]
        if marked:
            cv.text(x + 2, yy, 'STANDING IN TOWNS', DIM, PANEL)
            yy += 1
            line = '   '.join(f'{st.name}: {CR.standing_word(st.rep)} ({st.rep})' for st in sorted(marked, key=lambda q: q.rep)[:5])
            cv.text(x + 4, yy, line, BAD if any(st.rep <= CR.WANTED_AT for st in marked) else FG, PANEL, maxw=92)
            yy += 2
        known = [ev for ev in g.world.evils if ev.known]
        if known:
            cv.text(x + 2, yy, 'DARK POWERS', DIM, PANEL)
            yy += 1
            for ev in known:
                cv.text(x + 4, yy, ev.name, ev.fg if not ev.defeated else DIM, PANEL, maxw=28)
                cv.text(x + 32, yy, f'lair to the {g.dir_to(ev.did)}' if not ev.defeated else 'destroyed', FG if not ev.defeated else DIM, PANEL, maxw=64)
                yy += 1
            yy += 1
        cv.text(x + 2, yy, 'NEWS', DIM, PANEL)
        yy += 1
        evs = [st for st in g.world.settlements if st.event]
        if not evs:
            cv.text(x + 4, yy, 'All quiet across the land.', DIM, PANEL)
        for st in evs[:6]:
            if yy >= y + 26:
                break
            cv.text(x + 4, yy, D.EVENTS[st.event[0]]['text'].format(town=st.name) + f' ({st.event[1]} days)', FG, PANEL, maxw=92)
            yy += 1
        cv.text_center(W // 2, y + 27, ' Esc: close ', DIM, PANEL)

    def on_key(self, tok, shift):
        if tok in ('esc', 'e', 'tab', 'enter'):
            self.app.pop()


class WorldMapScreen(Modal):
    tall = False
    """The overworld: a scrollable close-up, or the whole realm with each character covering 2x2 cells."""
    show_factions = False
    PRIORITY = {D.CITY: 9, D.TOWN: 8, D.ENTR: 7, D.ROAD: 6, D.WATER: 5, D.MOUNTAIN: 4, D.HILLS: 3, D.SWAMP: 3, D.FOREST: 2, D.SAND: 2, D.GRASS: 1}
    zoom = 1          # 1: close-up you can scroll around, 0: the whole realm

    def __init__(self, app):
        super().__init__(app)
        g = self.game
        p = g.player
        here = g.here
        self.cx, self.cy = (here.x, here.y) if here else (p.x, p.y) if g.cur == 'over' else g.over_pos

    def render(self, cv):
        if self.zoom:
            self.render_detail(cv)
        else:
            self.render_overview(cv)

    def render_detail(self, cv):
        g = self.game
        om = g.maps['over']
        w = g.world
        x, y = self.box(cv, 104, 58, 'Map of the realm (close-up)')
        vw, vh = 100, 55
        self.cx = max(vw // 2, min(om.w - vw // 2, self.cx))
        self.cy = max(vh // 2, min(om.h - vh // 2, self.cy))
        ox, oy = self.cx - vw // 2, self.cy - vh // 2
        bx, by = x + 2, y + 1
        taint = getattr(w, 'taint', None)
        for vy in range(vh):
            for vx in range(vw):
                mx, my = ox + vx, oy + vy
                if not om.inb(mx, my):
                    continue
                i = my * om.w + mx
                if not om.seen[i]:
                    continue
                ch, fg, bg = LOOK.get(om, i)
                if taint and taint[i]:
                    ch, fg, bg = LOOK.tainted((ch, fg, bg), w.evils[taint[i] - 1].d['taint'], i)
                if WorldMapScreen.show_factions:
                    bg = mix(bg, D.FACTIONS[w.region_at(mx, my).faction]['fg'], .25)
                cv.put(bx + vx, by + vy, ch, fg, bg)

        def inview(px, py):
            return ox <= px < ox + vw and oy <= py < oy + vh
        for st in getattr(w, 'sites', ()):
            if om.seen[st.y * om.w + st.x] and inview(st.x, st.y):
                cv.put(bx + st.x - ox, by + st.y - oy, st.glyph[0], st.glyph[1], (40, 34, 26))
        for poi in w.pois:
            if poi.found and inview(poi.x, poi.y):
                cv.put(bx + poi.x - ox, by + poi.y - oy, poi.glyph[0], poi.glyph[1], (34, 28, 22))
        for hd in w.holds:
            if om.seen[hd.y * om.w + hd.x] and inview(hd.x, hd.y):
                cv.put(bx + hd.x - ox, by + hd.y - oy, 'Ω' if hd.kind == 'castle' else '╬', D.FACTIONS[hd.faction]['fg'], (40, 30, 20))
        for mi in MS.active(g):
            (tx, ty), _ = MS.target_pos(g, mi)
            if inview(tx, ty):
                cv.put_bg(bx + tx - ox, by + ty - oy, (110, 80, 16))
        p = g.player
        here = g.here
        px, py = (here.x, here.y) if here else (p.x, p.y) if g.cur == 'over' else g.over_pos
        if inview(px, py):
            cv.put(bx + px - ox, by + py - oy, '@', (255, 246, 220), (150, 40, 28))
        for st in w.settlements:
            if g.known_settlement(st) and inview(st.x, st.y):
                lx = bx + st.x - ox - len(st.name) // 2
                ly = by + st.y - oy - 1
                if by <= ly < by + vh:
                    lx = max(bx, min(bx + vw - len(st.name) - 2, lx))
                    cv.text(lx, ly, f' {st.name} ', (255, 226, 140) if st.is_city else (236, 210, 150), (30, 22, 14))
        for name, wx, wy in getattr(w, 'wonders', ()):
            if inview(wx, wy) and om.seen[wy * om.w + wx]:
                lx = max(bx, min(bx + vw - len(name) - 2, bx + wx - ox - len(name) // 2))
                ly = by + wy - oy - 2
                if by <= ly < by + vh:
                    cv.text(lx, ly, f' {name} ', (220, 196, 246), (34, 20, 44))
        cv.text_center(W // 2, y + 57, ' arrows/hjkl: scroll (Shift: faster) · Z: whole realm · F: factions · Esc: close ', DIM, PANEL)

    def render_overview(self, cv):
        g = self.game
        om = g.maps['over']
        w = g.world
        x, y = self.box(cv, 104, 60, 'Map of the realm')
        bx, by = x + 2, y + 1
        taint = getattr(w, 'taint', None)
        p = g.player
        here = g.here
        px, py = (here.x, here.y) if here else (p.x, p.y) if g.cur == 'over' else g.over_pos
        f = max(om.w / 100, om.h / 56)            # world cells per map character
        S = lambda v: int(v / f)
        for cy in range(int(om.h / f)):
            for cx in range(int(om.w / f)):
                best, bt, bi, nbl = 0, None, 0, 0
                for yy in range(int(cy * f), min(om.h, int((cy + 1) * f))):
                    for xx in range(int(cx * f), min(om.w, int((cx + 1) * f))):
                        i = yy * om.w + xx
                        if not om.seen[i]:
                            continue
                        if taint and taint[i]:
                            nbl = taint[i]
                        t = om.t[i]
                        pr = self.PRIORITY.get(t, 0)
                        if pr > best:
                            best, bt, bi = pr, t, i
                if bt is None:
                    continue
                ch, fg, bg = LOOK.get(om, bi)
                if bg == LOOK.BG:
                    bg = PANEL
                if nbl:
                    ch, fg, bg = LOOK.tainted((ch, fg, bg), w.evils[nbl - 1].d['taint'], bi)
                if WorldMapScreen.show_factions:
                    rf = w.regions[w.region_of[min(om.h - 1, int(cy * f)) * om.w + int(cx * f)]].faction
                    bg = mix(PANEL, D.FACTIONS[rf]['fg'], .28)
                cv.put(bx + cx, by + cy, ch, fg, bg)
        taken = set()
        for st in w.settlements:
            taken.add((bx + S(st.x), by + S(st.y)))
        for st in sorted(w.settlements, key=lambda q: not q.is_city):
            if not g.known_settlement(st):
                continue
            lx, ly = bx + S(st.x) + 1, by + S(st.y)
            name = st.name
            if lx + len(name) > x + 103:
                lx = bx + S(st.x) - len(name)
            cells = {(lx + j, ly) for j in range(len(name) + 1)}
            if lx < x + 1 or cells & taken:
                continue
            taken |= cells
            cv.text(lx, ly, name, (230, 196, 120) if st.is_city else (176, 146, 80), PANEL)
        for name, wx, wy in getattr(w, 'wonders', ()):
            if om.inb(wx, wy) and om.seen[wy * om.w + wx]:
                lx, ly = bx + S(wx) - len(name) // 2, by + S(wy) - 1
                cells = {(lx + j, ly) for j in range(len(name))}
                if not cells & taken and lx > x:
                    taken |= cells
                    cv.text(lx, ly, name, (200, 170, 230), PANEL)
        for mi in MS.active(g):
            (tx, ty), _ = MS.target_pos(g, mi)
            cv.put_bg(bx + S(tx), by + S(ty), (110, 80, 16))
        cv.put(bx + S(px), by + S(py), '@', (255, 246, 220), (150, 40, 28))
        for poi in w.pois:
            if poi.found:
                ch, col = poi.glyph
                cv.put(bx + S(poi.x), by + S(poi.y), ch, col if poi.ready_day < 10 ** 9 else scale(col, .5), PANEL)
        for hd in w.holds:
            if om.seen[hd.y * om.w + hd.x]:
                cv.put(bx + S(hd.x), by + S(hd.y), 'Ω' if hd.kind == 'castle' else '╬', D.FACTIONS[hd.faction]['fg'], PANEL)
        if WorldMapScreen.show_factions:
            lx = x + 2
            for f in D.FACTION_ORDER:
                cv.text(lx, y + 57, '■ ' + D.FACTIONS[f]['short'], D.FACTIONS[f]['fg'], PANEL)
                lx += len(D.FACTIONS[f]['short']) + 4
        else:
            cv.text(x + 2, y + 57, '⌂ village ■ city Ω castle ╬ fort > dungeon Π ruin † shrine ∆ camp Ψ stones ¤ wagon', DIM, PANEL)
        cv.text_center(W // 2, y + 59, ' Z or arrows: close-up · F: factions · Esc: close ', DIM, PANEL)

    def on_key(self, tok, shift):
        if tok in ('f', 'F'):
            WorldMapScreen.show_factions = not WorldMapScreen.show_factions
            return
        if tok in ('z', 'Z', 'tab', '+', '-'):
            WorldMapScreen.zoom = 1 - self.zoom
            return
        d = DIRS.get(tok)
        if not d and tok in RUN_LETTERS:
            d, shift = DIRS[RUN_LETTERS[tok]], True
        if d:
            if not self.zoom:
                WorldMapScreen.zoom = 1
            step = 16 if shift else 5
            self.cx += d[0] * step
            self.cy += d[1] * step
            return
        if tok in ('esc', 'm', 'enter', 'space', 'q'):
            self.app.pop()


class TempleScreen(Modal):
    """The priest: healing, identifying and lifting curses; prayer, offerings and devotion."""

    def __init__(self, app, name):
        super().__init__(app)
        from . import gods as GD
        self.GD = GD
        self.name = name
        self.god = GD.temple_god(app.game)
        g = app.game
        mine = getattr(g.player, 'god', None)
        gd = GD.GODS[self.god]
        if GD.opposed(mine, self.god):
            self.said = (f'"You wear the sign of {GD.GODS[mine]["name"]}. This is a house of {gd["name"]}. '
                         f'We do not tend to your kind here. Go."')
        elif mine == self.god:
            self.said = f'"Welcome home, child of {gd["name"]}. What troubles you?"'
        else:
            self.said = f'"Peace be with you, traveller. {gd["name"]}, {gd["title"]}, watches over this house. What troubles you?"'

    @property
    def refused(self):
        return self.GD.opposed(getattr(self.game.player, 'god', None), self.god)

    def render(self, cv):
        g = self.game
        p = g.player
        s = g.stats()
        GD = self.GD
        gd = GD.GODS[self.god]
        x, y = self.box(cv, 72, 22, f' {self.name} ')
        cv.text(x + 3, y + 1, f"A temple of {gd['name']}, {gd['title']}", gd['fg'], PANEL)
        cv.text(x + 3, y + 2, f"{gd['domain'].capitalize()}.", DIM, PANEL, maxw=66)
        cv.text(x + 3, y + 3, f"Pleased by {gd['likes']}.", DIM, PANEL, maxw=66)
        cv.wrap(x + 3, y + 5, 66, self.said, FG, PANEL, 2)
        no = self.refused
        hurt = p.life < s['max_life'] or p.mana < s['max_mana'] or p.poison
        ni, ci = g.identify_all(dry=True)
        nc, cc = g.uncurse_all(dry=True)
        mine = getattr(p, 'god', None)
        rows = [('a', 'Heal my wounds', 'free' if hurt else 'you are well', hurt and not no),
                ('b', f'Identify my unknown items ({ni})', fmt(ci) if ni else 'nothing to identify', ni > 0 and not no),
                ('c', f'Lift the curses I carry ({nc})', fmt(cc) if nc else 'no known curses', nc > 0 and not no),
                ('d', f"Pray to {gd['name']}", 'once a day' if mine == self.god else '', not no),
                ('e', 'Make an offering', fmt(100), p.gold >= 100 and not no)]
        if self.god in GD.DEVOTABLE and mine != self.god:
            rows.append(('f', f"Devote yourself to {gd['name']}", 'forsake ' + GD.GODS[mine]['name'] if mine else 'a vow', not no))
        for i, (k, a, b, ok) in enumerate(rows):
            yy = y + 8 + i * 2
            cv.text(x + 3, yy, k, GOLD if ok else DIM, PANEL)
            cv.text(x + 5, yy, a, FG if ok else DIM, PANEL)
            cv.text_right(x + 68, yy, b, GOLD if ok else DIM, PANEL)
        cv.text(x + 3, y + 20, f'Your purse: {fmt(p.gold)}', DIM, PANEL)
        cv.text_right(x + 68, y + 20, GD.standing(g), GD.GODS[mine]['fg'] if mine else DIM, PANEL)
        cv.text_center(W // 2, y + 21, ' letter: choose · Esc: leave ', DIM, PANEL)

    def on_key(self, tok, shift):
        g = self.game
        p = g.player
        GD = self.GD
        g.log_mark = len(g.log)
        if tok == 'esc':
            self.app.pop()
            return
        if self.refused and tok in 'abcdef':
            self.said = '"You heard me. Out."'
            return
        if tok == 'a':
            s = g.stats()
            if p.life >= s['max_life'] and p.mana >= s['max_mana'] and not p.poison:
                self.said = '"You look well, child. Come back when the world has had its way with you."'
                return
            p.life, p.mana, p.poison = s['max_life'], s['max_mana'], None
            g.num(p.x, p.y, 'healed', E.C_HEAL, True)
            self.said = '"Hold still." The priest lays hands on your wounds. You are fully restored.'
        elif tok == 'b':
            n, _c = g.identify_all(dry=True)
            g.identify_all()
            if n and not g.identify_all(dry=True)[0]:
                self.said = '"Let me see... yes. Every item has a story, and now you know it."'
        elif tok == 'c':
            n, _c = g.uncurse_all(dry=True)
            g.uncurse_all()
            if n and not g.uncurse_all(dry=True)[0]:
                self.said = '"Begone, darkness!" The priest\'s prayer burns the curse away.'
        elif tok == 'd':
            self.said = GD.pray(g, self.god)
        elif tok == 'e':
            if GD.offering(g, 100):
                self.said = ('"Bless you." The coins ring in the offering bowl.' if getattr(p, 'god', None) == self.god
                             else '"Bless you, stranger. The poor of the parish thank you."')
            else:
                self.said = '"Keep your coin, child. You need it more than we do."'
        elif tok == 'f' and self.god in GD.DEVOTABLE and getattr(p, 'god', None) != self.god:
            self.app.push(ConfirmScreen(self.app, f"Swear yourself to {GD.GODS[self.god]['name']}?",
                                        'Followers of rival gods will trust you less, and their priests may turn you away. '
                                        'If you serve another god now, you lose their favour.', self.devote))

    def devote(self):
        GD = self.GD
        GD.devote(self.game, self.god)
        self.said = f'"Then rise, child of {GD.GODS[self.god]["name"]}. Come back and pray with us, and bring the light with you."'


class MenuScreen(Modal):
    """Everything you can do or open, grouped (Tab). Left and right pick a group, up and down an item, Enter does it.
    Each item also shows its own shortcut key, for those who like them."""
    GROUPS = [
        ('Hero', [('i', 'Inventory', 'what you carry and wear'), ('c', 'Character', 'who you are, attributes and numbers'),
                  ('C', 'Life skills', 'fishing, foraging, herbalism, alchemy, brewing'),
                  ('z', 'Skills', 'your spells and abilities, and the six on your bar'),
                  ('v', 'Bestiary', 'the creatures you have met')]),
        ('World', [('m', 'World map', 'the lands you have seen'), ('e', 'Journal', 'story, jobs, rumours, cargo, factions, faith'),
                   ('t', 'Travel', 'walk the roads to a place you know'), ('x', 'Explore', 'wander a dungeon until something turns up')]),
        ('Actions', [('T', 'Talk', 'to someone near you'), ('o', 'Look around', 'inspect anything you can see'),
                     ('g', 'Pick up', 'what lies at your feet'), ('d', 'Drop', 'something from your bag'),
                     ('E', 'Eat', 'the food that fits your hunger best'), ('F', 'Forage', 'search the wild for food and herbs'),
                     ('a', 'Fish', 'by water, with a fishing pole'), ('f', 'Shoot', 'at the nearest enemy, with a bow'),
                     ('P', 'Alchemy & brewing', 'potions, ale, wine and mead'), ('p', 'Town portal', 'read a scroll of town portal'),
                     ('R', 'Rest', 'until you are healed')]),
        ('Game', [('?', 'Help', 'keys and how things work'), ('esc', 'Save and quit', 'your hero waits for you')]),
    ]

    def __init__(self, app):
        super().__init__(app)
        self.group = 0
        self.sel = 0

    def render(self, cv):
        n = max(len(items) for _g, items in self.GROUPS)
        x, y = self.box(cv, 64, n + 6, ' Menu ')
        for i, (name, _items) in enumerate(self.GROUPS):
            on = i == self.group
            cv.text(x + 2, y + 2 + i * 2, (' ► ' if on else '   ') + name.ljust(9), GOLD if on else DIM,
                    (52, 40, 28) if on else PANEL)
        for yy in range(y + 1, y + n + 3):
            cv.put(x + 16, yy, '│', LINE, PANEL)
        items = self.GROUPS[self.group][1]
        for j, (k, name, desc) in enumerate(items):
            yy = y + 2 + j
            on = j == self.sel
            bg = (52, 40, 28) if on else PANEL
            if on:
                cv.fill(x + 17, yy, 46, 1, ' ', None, bg)
            cv.text(x + 19, yy, name, FG if on else scale(FG, .85), bg)
            cv.text_right(x + 61, yy, 'Esc' if k == 'esc' else k, scale(GOLD, .8), bg)
        k, name, desc = items[self.sel]
        cv.text(x + 3, y + n + 3, desc, DIM, PANEL, maxw=58)
        cv.text_center(W // 2, y + n + 5, ' ←→ group · ↑↓ item · Enter: do it · Tab: close ', DIM, PANEL)

    def on_key(self, tok, shift):
        items = self.GROUPS[self.group][1]
        keys = [k for _g, its in self.GROUPS for k, _n, _d in its]
        if tok in ('tab', 'esc'):
            self.app.pop()
        elif tok in ('left', 'np4'):
            self.group, self.sel = (self.group - 1) % len(self.GROUPS), 0
        elif tok in ('right', 'np6'):
            self.group, self.sel = (self.group + 1) % len(self.GROUPS), 0
        elif tok in ('up', 'np8'):
            self.sel = (self.sel - 1) % len(items)
        elif tok in ('down', 'np2'):
            self.sel = (self.sel + 1) % len(items)
        elif tok in ('enter', 'np_enter', 'space'):
            self.pick(items[self.sel][0])
        elif tok in keys and tok != 'esc':
            self.pick(tok)

    def pick(self, k):
        self.app.pop()
        gs = self.app.top
        if isinstance(gs, GameScreen):
            gs.on_key(k, False)


class TalkScreen(Modal):
    """Who do you want to talk to?"""

    def __init__(self, app, ids):
        super().__init__(app)
        g = app.game
        pool = g.world.wanderers if g.map.kind == 'over' else g.map.mons
        self.people = [o for i in ids for o in pool if o.id == i]

    def render(self, cv):
        x, y = self.box(cv, 56, len(self.people) + 4, ' Talk to whom? ')
        for i, o in enumerate(self.people):
            cv.text(x + 3, y + 2 + i, LETTERS[i], GOLD, PANEL)
            cv.text(x + 5, y + 2 + i, getattr(o, 'ch', '☺'), o.fg, PANEL)
            cv.text(x + 7, y + 2 + i, o.name, FG, PANEL, maxw=46)
        cv.text_center(W // 2, y + len(self.people) + 3, ' letter: talk · Esc: never mind ', DIM, PANEL)

    def on_key(self, tok, shift):
        if tok == 'esc':
            self.app.pop()
        elif len(tok) == 1 and tok in LETTERS[:len(self.people)]:
            who = self.people[LETTERS.index(tok)]
            self.app.pop()
            g = self.game
            g.log_mark = len(g.log)
            g.talk_to(who)


class ConfirmScreen(Modal):
    """A yes/no question."""

    def __init__(self, app, title, text, yes):
        super().__init__(app)
        self.title, self.text, self.yes = title, text, yes

    def render(self, cv):
        x, y = self.box(cv, 60, 10, f' {self.title} ')
        cv.wrap(x + 3, y + 2, 54, self.text, FG, PANEL, 4)
        cv.text_center(W // 2, y + 8, ' y: yes · n/Esc: no ', GOLD, PANEL)

    def on_key(self, tok, shift):
        if tok == 'y':
            self.app.pop()
            self.yes()
        elif tok in ('n', 'esc'):
            self.app.pop()


class BrewScreen(Modal):
    """Crafting: alchemy (potions from herbs) and brewing (ale, wine and mead, at an inn or a cellar)."""

    def entries(self):
        from . import foraging as FGM
        from . import brewing as BR
        g = self.game
        return [('alchemy', k, v) for k, v in FGM.recipes(g)] + [('brewing', k, v) for k, v in BR.recipes(g)]

    def render(self, cv):
        from . import foraging as FGM
        from . import brewing as BR
        from . import lifeskills as LS
        from . import hunger as HU
        g = self.game
        x, y = self.box(cv, 80, 22, ' Alchemy & Brewing ')
        ents = self.entries()
        al = [e for e in ents if e[0] == 'alchemy']
        br = [e for e in ents if e[0] == 'brewing']
        yy = y + 1
        cv.text(x + 3, yy, f'ALCHEMY {LS.rank(g, "alchemy")}', GOLD, PANEL)
        cv.text(x + 18, yy, 'potions from herbs, anywhere', DIM, PANEL)
        yy += 2
        if not al:
            yy += cv.wrap(x + 3, yy, 72, 'You know no recipes yet. The herbalist monks in the monasteries teach the basics '
                          'to those who ask.', DIM, PANEL) + 1
        i = 0
        for _kind, k, (name, rank, ing, res) in al:
            ok = FGM.can_brew(g, k)
            cv.text(x + 3, yy, LETTERS[i], GOLD, PANEL)
            cv.text(x + 5, yy, name, FG if ok else DIM, PANEL)
            cv.text(x + 26, yy, ' + '.join(f'{n} {FGM.PLANTS[h][0]}' for h, n in ing.items()), GOOD if ok else DIM, PANEL, maxw=50)
            cv.text(x + 5, yy + 1, f"makes: {D.POTIONS[res]['name']}", scale(DIM, .85), PANEL)
            yy += 2
            i += 1
        yy += 1
        here = BR.where_ok(g)
        cv.text(x + 3, yy, f'BREWING {LS.rank(g, "brewing")}', GOLD, PANEL)
        cv.text(x + 18, yy, 'ale, wine and mead' + ('' if here else ': only at an inn or a monastery cellar'),
                DIM if here else BAD, PANEL)
        yy += 2
        for _kind, k, (name, rank, ing, res, n) in br:
            ok = BR.can_brew(g, k) and here
            cv.text(x + 3, yy, LETTERS[i], GOLD, PANEL)
            cv.text(x + 5, yy, name, FG if ok else DIM, PANEL)
            cv.text(x + 26, yy, ' + '.join(f'{c} {BR.ing_name(kd, kk)}' for (kd, kk), c in ing.items()),
                    GOOD if BR.can_brew(g, k) else DIM, PANEL, maxw=50)
            cv.text(x + 5, yy + 1, f"makes: {n}x {HU.FOODS[res][0]}", scale(DIM, .85), PANEL)
            yy += 2
            i += 1
        cv.text_center(W // 2, y + 21, ' letter: brew · Esc: close ', DIM, PANEL)

    def on_key(self, tok, shift):
        from . import foraging as FGM
        from . import brewing as BR
        g = self.game
        ents = self.entries()
        if tok == 'esc':
            self.app.pop()
        elif len(tok) == 1 and tok in LETTERS[:len(ents)]:
            g.log_mark = len(g.log)
            kind, k, _v = ents[LETTERS.index(tok)]
            used = FGM.brew(g, k) if kind == 'alchemy' else BR.brew(g, k)
            if used:
                g.end_turn(used, True)


class StablesScreen(Modal):
    def render(self, cv):
        g = self.game
        p = g.player
        x, y = self.box(cv, 64, 12, 'Stables')
        cv.text(x + 2, y + 1, f'"Need something to carry your goods?"   Purse {fmt(p.gold)}', DIM, PANEL)
        for i, k in enumerate(('mule', 'cart')):
            mt = D.MOUNTS[k]
            yy = y + 3 + i * 3
            owned = k in p.mounts
            cv.text(x + 2, yy, LETTERS[i], GOLD, PANEL)
            cv.text(x + 4, yy, mt['name'], FG if not owned else DIM, PANEL)
            cv.text_right(x + 60, yy, 'owned' if owned else fmt(mt['price']), DIM if owned else GOLD, PANEL)
            cv.text(x + 4, yy + 1, mt['desc'], DIM, PANEL)
        cv.text(x + 2, y + 9, f'Your cargo space: {ECO.cargo_capacity(p)}', FG, PANEL)
        cv.text_center(W // 2, y + 11, ' a/b: buy · Esc: leave ', DIM, PANEL)

    def on_key(self, tok, shift):
        g = self.game
        if tok == 'esc':
            self.app.pop()
        elif tok in ('a', 'b'):
            g.log_mark = len(g.log)
            g.buy_mount('mule' if tok == 'a' else 'cart')
