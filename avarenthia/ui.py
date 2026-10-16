"""Screens, rendering and input handling. Independent of tcod: it draws on a Canvas
and receives key tokens ('a', 'A', 'up', 'np7', 'enter', 'esc', '>' ...)."""
import math
import random
import time

from . import anim as AN
from . import seasons as SE
from . import living as LV
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
from .folk import unfound as FKunfound
from .tribes import LOOK as TRglow

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
        'np8': (0, -1), 'np2': (0, 1), 'np4': (-1, 0), 'np6': (1, 0), 'np7': (-1, -1), 'np9': (1, -1), 'np1': (-1, 1), 'np3': (1, 1),
        'home': (-1, -1), 'pageup': (1, -1), 'end': (-1, 1), 'pagedown': (1, 1)}
RUN_LETTERS = {}
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
        game.hook()                    # this world's factions, not those of a save the main menu peeked at
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
        if getattr(top, 'fast', False):
            return 1 / 30
        if getattr(top, 'ambient', False):
            return 1 / 10
        g = self.game
        if g and isinstance(top, GameScreen):
            m = g.map
            wk = getattr(top, 'weather', 'clear')
            if wk not in ('clear', 'night') and wk not in WX.STILL:
                return 1 / 24                      # falling rain and snow: smooth, at a steady pace
            if getattr(top, 'marks', False) or getattr(top, 'moving', False) or wk != 'clear':
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
        elif req[0] == 'quarter':
            from . import guilds as GU
            self.push(ShopScreen(self, 'g:' + req[1], quarter=req[1]))
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
        self.effects = [e for e in self.effects if t - e[1] < (e[2][4] if e[0] == 'flash' else
                                                               2 + len(e[2][3]) / 25 if e[0] == 'speech' else .8)]
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
                          'SOFTCORE: the priests raise you, for a fee from your purse; your pack and cargo stay '
                          'with your body. If you cannot pay the temple when you die, your tale ends here.')),
                ('World seed', (self.seed or 'random') + (' _' if self.sel == 1 else ''))]
        for i, (a, b) in enumerate(rows):
            y = 12 + i * 4
            sel = i == self.sel
            cv.text(26, y, ('► ' if sel else '  ') + a, GOLD if sel else FG)
            cv.wrap(44, y, 58, b, BAD if (i == 0 and self.hardcore) else FG, None, 3)
        cv.text_center(W // 2, 21, 'Up/Down: choose · Left/Right or Space: change mode · type digits for a seed', DIM)
        cv.text_center(W // 2, 23, 'Enter: begin · Esc: back', DIM)

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
        torchlit = m.kind == 'dungeon' or getattr(m, 'underground', False)
        deco = getattr(m, 'deco', None)
        night = TW.is_night(g)
        portal = m.portal_pos if (m.kind == 'town' and g.portal and g.portal.get('sid') == m.sid) else None
        vis = g.vis
        self.marks = self.moving = False
        day = g.turn // D.DAY_LEN
        season = SE.Now(g) if m.kind == 'over' else None
        fires = getattr(g.world, 'fires', None) if season else None
        beam = getattr(m, 'beacon', None) if m.kind == 'town' and TW.lamp_light(g) > 0 else None
        self.weather = wk = WX.shown(g)
        WX.frame(ox, oy, WX.wetness(g))
        inline = wk != 'clear' and wk not in WX.NEEDS_CANVAS
        lightning = WX.flash(t) if wk == 'storm' else 0.0
        pvx, pvy = p.x - ox, p.y - oy
        tgt_id = getattr(p, 'target', None)
        sight = g.over_sight() if m.kind == 'over' else 0
        taint = getattr(g.world, 'taint', None) if m.kind == 'over' else None
        ways = getattr(m, 'oldway', None) if m.kind == 'over' else None
        way_of = getattr(g.world, 'way_of', {})
        ways_seen = g.__dict__.get('ways_seen', set())
        traps = getattr(m, 'known_traps', None)
        # fire beetles and ember spiders light the dark around them
        glows = [(o.x, o.y, o.fg) for o in m.mons if lighting and not o.is_npc and 'glow' in o.tpl.get('beh', ())
                 and not getattr(o, 'lurk', False)]
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
                if season:
                    ch, fg, bg = SE.look(g, m, i, (ch, fg, bg), season, t)
                    if fires and v and i in fires:
                        self.moving = True
                if ways and i in ways and i in ways_seen:
                    ch, fg = ways[i], LOOK.PATH_FG
                if taint and taint[i]:
                    ch, fg, bg = LOOK.tainted((ch, fg, bg), g.world.evils[taint[i] - 1].d['taint'], i)
                    if v:                           # the marked land breathes, slowly
                        k = .9 + .1 * math.sin(t * .8 + (mx + my) * .12)
                        fg, bg, self.moving = scale(fg, k), scale(bg, k), True
                if deco and deco[i]:
                    ch, fg, bg = DR.deco_look(m, i, (ch, fg, bg))
                elif v and m.t[i] in AN.MOVING:
                    look = AN.cell(m, i, mx, my, (ch, fg, bg), t, night, day)
                    if look:
                        ch, fg, bg = look
                        self.moving = True
                if portal and (mx, my) == portal:
                    ch, fg = '0', AN.portal(t)
                    self.moving = True
                if lamps and (mx, my) in lamps and lamps[(mx, my)] in m.lamp_on:
                    fl = DR.flicker(m, 0, t + lamps[(mx, my)])
                    ch, fg, bg = 'Γ', (255, int(200 * fl), int(110 * fl)), (int(90 * fl), int(52 * fl), 16)
                if v and lighting:
                    lr, lg, lb = DR.light_at(m, i, t)
                    dd = ((mx - p.x) ** 2 + (my - p.y) ** 2) ** .5
                    # you carry a torch underground; in town at night only the lamps and windows give light
                    k = max(0.0, 1 - dd / 7.5) * .95 if torchlit else 0.0
                    for gx, gy, gc in glows:
                        gd = max(abs(mx - gx), abs(my - gy))
                        if gd <= 3:
                            gk = (1 - gd / 4) * .8
                            lr, lg, lb = lr + gk * gc[0] / 255, lg + gk * gc[1] / 255, lb + gk * gc[2] / 255
                    ch, fg, bg = DR.lit((ch, fg, bg), (lr + k, lg + k * .82, lb + k * .55))
                    if beam:
                        ch, fg, bg = AN.beacon(m, mx, my, (ch, fg, bg), t)
                        self.moving = True
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
                            fg, _on = AN.sparkle(fg, t, mx, my, 17)
                            self.moving = True
                    if traps and (mx, my) in traps:
                        ch, fg = '^', (220, 190, 110)
                    o = mons.get((mx, my))
                    if o and getattr(o, 'lurk', False) and o.tpl.get('disguise'):
                        ch, fg = o.tpl['disguise'][0], D.hexrgb(o.tpl['disguise'][1])     # a chest, a statue, a stone
                        o = None
                    if o and (getattr(o, 'lurk', False) or getattr(o, 'invis', 0)):
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
                            if getattr(o, 'faded', False):
                                fg = scale(fg, .45)
                            if o.id == tgt_id:
                                bg = (150, 44, 30)          # your target
                            if t - app.hit_times.get(o.id, -9) < .13:
                                fg, bg = (255, 255, 255), (120, 30, 20)
                    if mx == p.x and my == p.y:
                        ch, fg = '@', ((184, 240, 138) if p.poison else (255, 246, 220))
                    if m.kind == 'over':     # the edge of sight fades out softly
                        d = max(abs(mx - p.x), abs(my - p.y))
                        k = 1 - .45 * max(0.0, min(1.0, (d - (sight - 2)) / 2))
                        if k < 1:
                            fg, bg = scale(fg, k), scale(bg, .55 + .45 * k)
                elif not lighting and m.kind == 'over' and m.t[i] == D.ROAD:
                    fg, bg = mix(fg, (150, 124, 84), .6), (34, 28, 22)     # roads you know stay legible in the fog
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
            if season.midsummer:                     # the hill fires are seen from far off, beyond your sight
                for i in SE.bonfires(m):
                    bx, by = i % m.w, i // m.w
                    vx, vy = bx - ox, by - oy
                    if 0 <= vx < MAP_W and 0 <= vy < MAP_H and (bx, by) != (p.x, p.y):
                        f = AN.flame(t, bx, by)
                        cv.put(vx, vy, '☼', (255, int(190 * f), 70), (int(90 * f), 30, 8))
                        self.moving = True
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
        self.draw_labels(cv, m, p, ox, oy, mons)
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
                lines = wrap_text(txt, 30)[:4]             # a bubble of a few short lines, never cut off
                bw = max(len(ln) for ln in lines)
                vx = max(0, min(MAP_W - bw, x - ox - bw // 2))
                top = y - oy - len(lines)
                if top < 0:
                    top = y - oy + 1                        # no room above: speak below
                for k, ln in enumerate(lines):
                    vy = top + k
                    if 0 <= vy < MAP_H:
                        for j, chh in enumerate(ln.ljust(bw)):
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

    LABEL_NEAR = 8

    def draw_labels(self, cv, m, p, ox, oy, mons):
        """Hanging signs by the doors, and the names of buildings near you, outside them, away from the door."""
        for (hx, hy), (ch, col) in getattr(m, 'hang', {}).items():
            vx, vy = hx - ox, hy - oy
            if 0 <= vx < MAP_W and 0 <= vy < MAP_H and m.seen[hy * m.w + hx]:
                cv.put(vx, vy, ch, col, (58, 40, 22))
        taken = set()

        def free(cells):
            return all(m.inb(x, y) and m.tile(x, y) not in (D.WALL, D.DOOR, D.ODOOR) and (x, y) not in mons
                       and (x, y) != (p.x, p.y) and (x, y) not in taken for x, y in cells)

        def show(cells, text):
            for (x, y), ch in zip(cells, text):
                vx, vy = x - ox, y - oy
                if 0 <= vx < MAP_W and 0 <= vy < MAP_H:
                    _c, _f, bg = cv.get(vx, vy) if hasattr(cv, 'get') else (None, None, BG)
                    cv.put(vx, vy, ch, (196, 178, 136), mix(bg or BG, (34, 26, 16), .6))
            taken.update(cells)
        for b in getattr(m, 'buildings', []):
            x, y, w, h = b['box']
            if max(x - p.x, p.x - (x + w - 1), y - p.y, p.y - (y + h - 1), 0) > self.LABEL_NEAR:
                continue
            text = b['name']
            n = len(text)
            dx, dy = b['door']
            cx = x + w // 2 - n // 2

            def row(yy, x0):
                return [(x0 + j, yy) for j in range(n)]
            # centred on the building, or slid a little either way if something is in the way
            shifts = [0] + [d * k for k in range(1, n // 2 + 2) for d in (1, -1)]
            above = [row(y - 1, cx + sh) for sh in shifts]
            below = [row(y + h, cx + sh) for sh in shifts]
            left = [row(y + h // 2 + sh, x - 1 - n) for sh in (0, -1, 1, -2, 2)]
            right = [row(y + h // 2 + sh, x + w + 1) for sh in (0, -1, 1, -2, 2)]
            # the side away from the door first, then the others; never over walls, doors or people
            if dy >= y + h - 1:
                order = above + left + right + below
            elif dy <= y:
                order = below + left + right + above
            elif dx <= x:
                order = right + above + below + left
            else:
                order = left + above + below + right
            for cells in order:
                if free(cells):
                    show(cells, text)
                    break
        for sx_, sy_, text in getattr(m, 'signs', ()):            # other names (on a temple, a keep): only when near
            if max(abs(sx_ + len(text) // 2 - p.x), abs(sy_ - p.y)) > self.LABEL_NEAR + 2:
                continue
            cells = [(sx_ + j, sy_) for j in range(len(text))]
            if free(cells):
                show(cells, text.title() if text.isupper() else text)

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
        night = TW.is_night(g)
        for st in getattr(w, 'sites', ()):
            if om.seen[st.y * om.w + st.x] and not FKunfound(st):
                vx, vy = st.x - ox, st.y - oy
                if 0 <= vx < MAP_W and 0 <= vy < MAP_H and (st.x, st.y) != (p.x, p.y):
                    ch, col = st.glyph
                    bg = (40, 34, 26)
                    if night and st.kind in TRglow and g.vis[st.y * om.w + st.x]:
                        bg = AN.camp_glow(time.monotonic(), st.x, st.y)     # their fires, seen from afar
                        self.moving = True
                    cv.put(vx, vy, ch, col, bg)
        # settlements, by size; dwarven holds are a gate in the mountainside
        LOOKS = {'metropolis': ('█', (255, 232, 150), (90, 70, 30)), 'city': ('■', (255, 216, 96), (60, 44, 20)),
                 'town': ('⌂', (250, 206, 90), (52, 38, 18)), 'village': ('⌂', (226, 186, 90), None),
                 'hamlet': ('∩', (196, 160, 96), None), 'deephold': ('▼', (255, 200, 90), (60, 40, 20))}
        for s in w.settlements:
            if g.known_settlement(s) and s.kind in LOOKS:
                vx, vy = s.x - ox, s.y - oy
                if 0 <= vx < MAP_W and 0 <= vy < MAP_H and (s.x, s.y) != (p.x, p.y):
                    ch, col, bg = LOOKS[s.kind]
                    if LV.plundered(g, s):
                        col, bg = scale(col, .6), (64, 16, 10)          # burnt and half empty
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
        for ax, ay, r in hunt_areas(g):              # where the hunted is thought to be: hatched, no marker
            for yy in range(ay - r, ay + r + 1):
                for xx in range(ax - r, ax + r + 1):
                    vx, vy = xx - ox, yy - oy
                    if 0 <= vx < MAP_W and 0 <= vy < MAP_H and (xx - yy) % 4 == 0 and (xx, yy) != (p.x, p.y):
                        self._tint(cv, vx, vy, (70, 40, 20))
        for mi in MS.active(g):
            if mi.kind == 'hunt' and mi.state == 'active':
                continue
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
        # battlefields and crossroads shrines
        for b in getattr(w, 'battles', ()):
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    bx_, by_ = b['x'] + dx, b['y'] + dy
                    vx, vy = bx_ - ox, by_ - oy
                    if 0 <= vx < MAP_W and 0 <= vy < MAP_H and om.inb(bx_, by_) and om.seen[by_ * om.w + bx_] \
                            and (bx_, by_) != (p.x, p.y) and om.tile(bx_, by_) not in (D.WATER, D.MOUNTAIN, TOWN, D.CITY):
                        lk = LV.battle_look(g, bx_, by_)
                        if lk:
                            cv.put(vx, vy, *lk)
        for c in getattr(w, 'crossroads', ()):
            vx, vy = c['x'] - ox, c['y'] - oy
            if 0 <= vx < MAP_W and 0 <= vy < MAP_H and om.seen[c['y'] * om.w + c['x']] and (c['x'], c['y']) != (p.x, p.y):
                cv.put(vx, vy, LV.SHRINE_LOOK[0], LV.SHRINE_LOOK[1], (40, 32, 22))
        # travellers
        for wd in w.wanderers:
            if not g.visible(wd.x, wd.y):
                continue
            vx, vy = wd.x - ox, wd.y - oy
            if 0 <= vx < MAP_W and 0 <= vy < MAP_H and (wd.x, wd.y) != (p.x, p.y):
                bg = (50, 16, 60) if wd.kind == 'hunt' else (70, 20, 16) if wd.hostile else (20, 30, 50) if wd.kind == 'patrol' \
                    else (8, 18, 44) if wd.kind == 'ship' else BG
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
            if wk not in ('clear',) and wk not in WX.QUIET:
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
        from . import behave as BH
        cx = x
        for lab, col in BH.shown(g):                   # held, slowed, cursed...
            if cx + len(lab) > x + PW:
                break
            cv.text(cx, 14, lab, col, PANEL)
            cx += len(lab) + 1
        prev = E.xp_for(p.lvl - 1) if p.lvl > 1 else 0
        frac = (p.xp - prev) / max(1, E.xp_for(p.lvl) - prev)
        cv.text(x, 15, 'XP', DIM, PANEL)
        bw = PW - 3
        filled = int(bw * max(0, min(1, frac)))
        for i in range(bw):
            cv.put(x + 3 + i, 15, '█' if i < filled else '░', GOLD if i < filled else LINE, PANEL)
        from . import mercs as MC
        for row, mc in ((16, MC.get(g, 'merc')), (17, MC.get(g, 'beast'))):
            if not mc:                                 # the hireling and the beast: a name, a small bar, the orders
                continue
            first = mc.name.split()[0]
            cv.text(x, row, first[:9], (240, 224, 176) if mc.state == 'alive' else DIM, PANEL)
            if mc.state == 'alive':
                mx_ = MC.stats(g, mc)['max_hp']
                bw2 = 10
                fill = int(bw2 * max(0, min(1, mc.hp / max(1, mx_))))
                col = BAD if mc.hp < mx_ * .3 else (200, 180, 90) if mc.hp < mx_ * .6 else GOOD
                for i in range(bw2):
                    cv.put(x + 10 + i, row, '█' if i < fill else '░', col if i < fill else LINE, PANEL)
                word = 'fleeing' if mc.fleeing else MC.ORDER_WORD[mc.order].split()[0].lower()
                cv.text_right(x + PW - 1, row, word[:6], BAD if mc.fleeing else DIM, PANEL)
            else:
                cv.text_right(x + PW - 1, row, 'fallen', BAD, PANEL)
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
        cx = x
        for key, word in (('Enter', 'act'), ('Tab', 'aim'), ('Esc', 'menu')):
            cv.text(cx, H - 1, key, scale(GOLD, .7), PANEL)
            cv.text(cx + len(key) + 1, H - 1, word, scale(DIM, .8), PANEL)
            cx += len(key) + len(word) + 2

    def orb(self, cv, x, y, frac, col, alt=None, w=9, h=9):
        """A glass globe of life or mana, drawn with half blocks at twice the height: shaded liquid with a
        rippling surface, a dark empty top, a highlight on the glass and a gold rim."""
        import math
        frac = max(0.0, min(1.0, frac))
        liquid = alt or col
        t = time.monotonic()
        ph = h * 2
        cx, cy = (w - 1) / 2, (ph - 1) / 2
        rx, ry = w / 2 + .1, ph / 2 + .2            # a touch over half: the globe fills its box and stays round
        level = ph - frac * (ph - 1.5) - .75          # the row of the liquid's surface

        def inside(px, py):
            dx, dy = (px - cx) / rx, (py - cy) / ry
            return dx * dx + dy * dy <= 1.0

        def pixel(px, py):
            if not inside(px, py):
                return None
            dx, dy = (px - cx) / rx, (py - cy) / ry
            d = dx * dx + dy * dy
            # the rim: every pixel on the edge of the globe, diagonals included, so the glass is closed all round
            edge = any(not inside(px + ox_, py + oy_) for ox_ in (-1, 0, 1) for oy_ in (-1, 0, 1))
            if edge or d > .84:                      # lit from the top left
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
                        info = {'shrine': 'A place to pray.', 'camp': 'Outlaws and their loot.', 'orccamp': 'Orcs and their plunder.',
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
        picked = g.target()
        if not tgt and picked:
            tgt = picked
            cv.text(x, y - 1, 'Target', GOLD, PANEL)
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
        res = tgt.tpl.get('res', {})
        if res and g.lore(tgt.k) >= 1:            # you learn what it fears by fighting its kind
            strong = [k for k, v in res.items() if v > 0]
            weak = [k for k, v in res.items() if v < 0]
            words = (['resists ' + ', '.join(strong)] if strong else []) + (['weak to ' + ', '.join(weak)] if weak else [])
            cv.text(x, y + 3, '; '.join(words), scale(DIM, .9), PANEL, maxw=PW)

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
            g.log_mark = len(g.log)
            from . import lifeskills as LS
            water = LS.can_fish(g)
            if water:
                app.push(FishingScreen(app, water))
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
        elif tok == 'travel':
            app.push(WorldMapScreen(app, travel=True))
        elif tok == 'm':
            if g.map.kind == 'town' and getattr(g.map, 'buildings', None):
                app.push(TownPlanScreen(app))
            else:
                app.push(WorldMapScreen(app))
        elif tok == 'e':
            app.push(JournalScreen(app))
        elif tok == 'tab':
            g.log_mark = len(g.log)
            g.cycle_target(-1 if shift else 1)
        elif tok == 'quit':
            app.push(QuitScreen(app))
        elif tok in ('t', 'T'):
            g.log_mark = len(g.log)
            g.talk_nearby()
        elif tok == 'h':
            g.log_mark = len(g.log)
            from . import mercs as MC
            MC.menu(g)
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
            g.log_mark = len(g.log)
            if not g.clear_target():           # Esc first lets go of your target, then opens the menu
                app.push(MenuScreen(app))

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
    if it.k == 'gear':
        st = g.stats()
        need = []
        if it.req > 1:
            need.append((f'level {it.req}', it.req > g.player.lvl))
        if getattr(it, 'rstr', 0):
            need.append((f'{it.rstr} Strength', it.rstr > st['str']))
        if getattr(it, 'rdex', 0):
            need.append((f'{it.rdex} Dexterity', it.rdex > st['dex']))
        if need:
            cx = x
            cv.text(cx, yy, 'Requires', DIM, PANEL)
            cx += 9
            for i, (txt, bad) in enumerate(need):
                piece = txt + (',' if i < len(need) - 1 else '')
                cv.text(cx, yy, piece, BAD if bad else DIM, PANEL)
                cx += len(piece) + 1
            yy += 1
        sk = getattr(it, 'set_key', None)
        if sk:
            have = st.get('sets', {}).get(sk, 0)
            cv.text(x, yy, f"Set pieces worn: {have}/{len(D.SETS[sk]['pieces'])}", D.SET_COLOR, PANEL)
            yy += 1
    cv.text(x, yy, f'Value {fmt(it.value())}', DIM, PANEL)
    yy += 1
    if it.k == 'gear' and not g.is_equipped(it):
        cur = g.eq_item(g.slot_for(it))
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
    BAG_Y, BAG_ROWS = 16, 12
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
        cv.text(x + 2, y + 1, f'{len(g.player.inv)}/{E.INV_MAX} slots · {fmt(g.player.gold)}', DIM, PANEL)
        cv.text(x + 2, y + 3, 'EQUIPPED', DIM, PANEL)
        cv.text(x + 2, y + self.BAG_Y - 1, 'BACKPACK', DIM, PANEL)
        sc = self.bag_scroll()
        nbag = len(g.backpack())
        if sc > 0:
            cv.text(x + 50, y + self.BAG_Y - 1, '▲', GOLD, PANEL)
        if sc + self.BAG_ROWS < nbag:
            cv.text(x + 50, y + self.BAG_Y + self.BAG_ROWS, '▼', GOLD, PANEL)
        for idx, (kind, key, it) in enumerate(rows):
            sel = idx == self.sel
            bg = (52, 40, 28) if sel else PANEL
            if kind == 'eq':
                yy = y + 4 + idx
                cv.fill(x + 2, yy, 54, 1, ' ', FG, bg)
                cv.text(x + 4, yy, f'{D.SLOTNAME[key]:<8}', DIM, bg)
                if it:
                    cv.text(x + 13, yy, it.display_name(), it.color(), bg, maxw=41)
                elif key == 'shield' and g.two_handed(g.eq_item('weapon')):
                    cv.text(x + 13, yy, '(both hands on your weapon)', DIM, bg)
                else:
                    cv.text(x + 13, yy, '-', DIM, bg)
            else:
                if not sc <= key < sc + self.BAG_ROWS:
                    continue
                yy = y + self.BAG_Y + key - sc
                cv.fill(x + 2, yy, 54, 1, ' ', FG, bg)
                cv.text(x + 2, yy, LETTERS[key], GOLD, bg)
                cv.text(x + 4, yy, it.display_name(), it.color(), bg, maxw=48)
                if it.k == 'gear' and g.meets(it):
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
        if it.k == 'oldmap':
            from . import hidden as HP
            app.pop()
            HP.read_map(g, it)
            return
        if it.k == 'tool' and it.t == 'kit':
            app.pop()
            used = g.use_kit(it)
            if used:
                g.end_turn(used)
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
    PAGES = ['Character', 'Disciplines', 'Life skills', 'Guilds']

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
        [self.page_main, self.page_disc, self.page_life, self.page_guilds][self.page](cv, x, y + 3)
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
        cv.text(x + 3, y + 15, 'RESISTANCES', DIM, PANEL)
        cv.text_right(x + 68, y + 15, f'at most {D.RES_CAP}%', scale(DIM, .8), PANEL)
        for i, (key, nm, col) in enumerate(D.RESISTS):
            cx_ = x + 3 + i * 17
            cv.text(cx_, y + 16, nm, col, PANEL)
            cv.text_right(cx_ + 14, y + 16, f'{s[key]}%', FG if s[key] else DIM, PANEL)
        extra = [(f"+{s['mf']}% magic find") if s['mf'] else '', (f"damage taken -{s['dr']}%") if s['dr'] else '',
                 (f"thorns {s['thorns']}") if s['thorns'] else '', (f"+{s['sight']} light radius") if s['sight'] else '']
        extra = [e for e in extra if e]
        if extra:
            cv.text(x + 3, y + 17, ' · '.join(extra), DIM, PANEL, maxw=66)
        cv.text(x + 3, y + 18, 'CONDITION', DIM, PANEL)
        cv.text(x + 3, y + 19, 'Hunger', DIM, PANEL)
        self.bar(cv, x + 14, y + 19, 20, p.food / HU.MAX, GOOD if p.food >= HU.HUNGRY else GOLD if p.food >= HU.WEAK else BAD)
        cv.text(x + 36, y + 19, HU.state(p.food) or 'Fed', FG, PANEL)
        if p.buffs:
            cv.wrap(x + 3, y + 20, 66, 'Effects: ' + ', '.join(f'{b[3]} ({b[2]})' for b in p.buffs), GOOD, PANEL, 2)

    def page_disc(self, cv, x, y):
        p = self.game.player
        cv.text(x + 3, y, 'Disciplines grow by use, and decide which tomes you understand.', DIM, PANEL)
        for i, line in enumerate(SK.DISC_ORDER):          # one line each: name, rank, progress, skills, next tier
            yy = y + 2 + i
            r, prog = p.disc.get(line, [0, 0])
            d = SK.DISCIPLINES[line]
            cv.text(x + 3, yy, d['name'], FG if r else DIM, PANEL)
            cv.text_right(x + 24, yy, str(r), GOLD if r else DIM, PANEL)
            self.bar(cv, x + 27, yy, 16, prog / SK.need_for(r), INFO)
            nxt = next((k for k in SK.by_line(line) if k.unlock > r), None)
            n = len(SK.by_line(line))
            known = sum(1 for k in SK.by_line(line) if k.id in p.known)
            cv.text(x + 45, yy, f'{known}/{n} skills', DIM, PANEL)
            cv.text(x + 57, yy, f'next {nxt.unlock}' if nxt else 'all open', scale(DIM, .8), PANEL)

    def page_guilds(self, cv, x, y):
        from . import guilds as GU
        g = self.game
        st = GU.state(g)
        cv.text(x + 3, y, 'Two combat guilds at most; the crafts take anyone. Standing fades.',
                DIM, PANEL, maxw=66)
        rows = [k for k in GU.ORDER if st[k]['found']]
        for i, k in enumerate(rows):                    # one line each: name, rank (or kind), standing
            gd, s = GU.GUILDS[k], st[k]
            yy = y + 2 + i
            col = D.hexrgb(gd['fg'])
            cv.text(x + 3, yy, gd['name'], col if s['joined'] else scale(col, .55), PANEL, maxw=31)
            if s['joined']:
                r = GU.rank(g, k)
                cv.text(x + 35, yy, gd['ranks'][r], GOLD, PANEL, maxw=20)
                lo = GU.RANK_REP[r]
                hi = GU.RANK_REP[r + 1] if r < 4 else lo + 1
                idle = g.day - s['last']
                self.bar(cv, x + 56, yy, 10, (s['rep'] - lo) / max(1, hi - lo), BAD if idle > GU.DECAY_AFTER else col)
            else:
                cv.text(x + 35, yy, 'left' if s['left'] else ('combat' if gd['kind'] == 'combat' else 'craft'), DIM, PANEL)
        yy = y + 3 + len(rows)
        if any(st[k]['joined'] for k in rows):
            cv.text(x + 3, yy, 'The bar is your standing towards the next rank; red when it fades.', scale(DIM, .8), PANEL)
            yy += 1
        if len(rows) < len(GU.ORDER):
            cv.text(x + 3, yy, 'Some say there are guilds that do not hang out a sign.', scale(DIM, .8), PANEL)

    def page_life(self, cv, x, y):
        from . import lifeskills as LS
        p = self.game.player
        cv.text(x + 3, y, 'Crafts grow by doing them, with something new along the way.', DIM, PANEL)
        for i, key in enumerate(LS.LIFE_ORDER):
            yy = y + 2 + i * 4
            r, prog = p.life_sk.get(key, [0, 0])
            cv.text(x + 3, yy, LS.LIFE[key]['name'], FG if r else DIM, PANEL)
            cv.text_right(x + 24, yy, str(r), GOLD if r else DIM, PANEL)
            self.bar(cv, x + 27, yy, 20, prog / LS.need_for(r), GOOD)
            cv.wrap(x + 5, yy + 1, 64, LS.LIFE[key]['desc'], scale(DIM, .9), PANEL, 1)
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

    def __init__(self, app, key=None, quarter=None):
        super().__init__(app)
        self.pane = 0   # 0 = buy, 1 = sell
        self.sel = [0, 0]
        self.key = key if key is not None else self.game.home
        self.quarter = quarter
        self.mult = 1.0
        if quarter:
            from . import guilds as GU
            self.SUPPLIES = []
            self.title = 'Quartermaster, ' + GU.GUILDS[quarter]['short']
            self.mult = GU.quarter_mult(self.game, quarter)

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
        cv.text(x + 2, y + 1, f'"For members only. {round((1 - self.mult) * 100)}% off, for your rank."' if self.quarter
                else '"Fresh stock every time you come back to town."', DIM, PANEL)
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
                price = max(1, round(it.value() * self.mult)) if pane == 0 else max(1, it.value() // 4)
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
            cv.text(x + 67, y + 26, f'I: identify {n} item{"s" if n > 1 else ""} ({fmt(cost)})', GOLD, PANEL)
        nr, rc = g.repair_all(self.discount(), dry=True)
        if nr:
            cv.text(x + 67, y + 27, f'R: mend {nr} worn item{"s" if nr > 1 else ""} ({fmt(rc)})', GOLD, PANEL)
        cv.text_center(W // 2, y + 29, ' Tab: buy/sell · letter or arrows: select · Enter: buy or sell · I: identify · R: repair · Esc: leave ', DIM, PANEL)

    def discount(self):
        """Members of the Iron Company have their gear mended for less."""
        from . import guilds as GU
        if self.quarter:
            return GU.mend_discount(self.game, self.quarter)
        st = GU.state(self.game)['iron']
        return .1 + .05 * GU.rank(self.game, 'iron') if st['joined'] else 0.0

    def activate(self):
        g = self.game
        g.log_mark = len(g.log)
        i = self.sel[self.pane]
        if self.pane == 0:
            if i < len(self.SUPPLIES):
                g.buy_supply(i)
            else:
                g.buy_gear(i - len(self.SUPPLIES), self.key, self.mult)
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
        if tok in ('R', 'r'):
            self.game.log_mark = len(self.game.log)
            self.game.repair_all(self.discount())
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
            if g.has_visited('s', st.id) and not (here and here.id == st.id):
                out.append(('s', st.id, st.name, st.kind_name, st.x, st.y))
        for st in getattr(g.world, 'sites', ()):
            if g.has_visited('site', st.id):
                out.append(('site', st.id, st.name, st.kind, st.x, st.y))
        for d in g.world.dungeons.values():
            if g.has_visited('d', d.id) and getattr(d, 'town', None) is None:
                out.append(('d', d.id, d.name, 'dungeon', d.x, d.y))
        out.sort(key=lambda r: cheb(r[4], r[5], ox, oy))
        self.origin = (ox, oy)
        return out[:24]

    def render(self, cv):
        g = self.game
        pl = self.places()
        x, y = self.box(cv, 76, min(30, len(pl) + 6))
        cv.text(x + 2, y + 1, 'Walk to a place you have been, along the roads. Danger, travellers or hunger stop you.', DIM, PANEL, maxw=72)
        if not pl:
            cv.text(x + 2, y + 3, 'You have not been anywhere yet that you could find again.', DIM, PANEL)
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


class FishingScreen(Modal):
    """Fishing, in its own window over the game: the water, the bank, you, your rod, the line and the float.
    Wait for the bite and strike in time (Enter); then reel it in, keeping the fish in the green with the arrows
    while the line holds. A master angler (rank 20) can also take the quick way (Q)."""
    tall = False
    fast = True
    BW, BH = 76, 38
    TRACK = 50

    def __init__(self, app, water):
        super().__init__(app)
        from . import lifeskills as LS
        self.LS = LS
        self.water = water
        self.clock = time.monotonic
        self.place = LS.place_name(app.game)
        self.night = TW.is_night(app.game) and app.game.map.kind != 'dungeon'
        self.cast()

    # ------------------------------------------------------------- the states
    def cast(self):
        g = self.game
        self.pl = self.LS.plan(g, self.water)
        r = self.pl['rank']
        self.state = 'wait'
        self.t0 = self.clock()
        self.last = self.t0
        self.wait_for = random.uniform(1.6, 5.0) if self.pl['kind'] != 'none' else random.uniform(5.0, 7.0)
        self.window = .75 + min(.6, r * .025)
        self.zone_w = 8 + min(12, r * .5)
        self.ripples = []
        self.result = None
        self.leap = None

    def start_reel(self):
        f = self.pl
        lvl = self.LS.FISH[f['fish']][1] if f['kind'] == 'fish' else 0
        self.dif = min(1.0, lvl / 18 + (.15 if f['kind'] == 'fish' else 0))
        self.state = 'reel'
        self.fish_x = self.TRACK / 2
        self.fish_to = self.fish_x
        self.fish_next = 0
        self.zone = self.TRACK / 2
        self.progress = .1
        self.tension = .2
        self.t0 = self.clock()

    def finish(self, ok, text, col):
        g = self.game
        g.log_mark = len(g.log)
        turns = self.LS.land(g, self.pl, ok)
        if turns and not g.dead and g.map.kind != 'wild':
            g.end_turn(turns)
        self.state = 'done'
        self.result = (text, col)
        self.t0 = self.clock()
        if g.cur == 'wild' or g.dead:
            self.app.pop()

    def update(self):
        now = self.clock()
        dt = max(0.0, min(.25, now - self.last))
        self.last = now
        el = now - self.t0
        if self.state == 'wait':
            if random.random() < dt * .7:
                self.ripples.append((random.randint(-9, 9), random.randint(-1, 2), now))
            if el >= self.wait_for:
                if self.pl['kind'] == 'none':
                    self.finish(False, 'Nothing bites. You reel in an empty hook.', DIM)
                else:
                    self.state, self.t0 = 'bite', now
        elif self.state == 'bite':
            if el > self.window:
                self.pl['kind'] = 'missed' if self.pl['kind'] != 'monster' else 'monster'
                if self.pl['kind'] == 'monster':
                    self.finish(True, 'Something huge pulls back...', BAD)
                else:
                    self.pl['kind'] = 'none'
                    self.finish(False, 'Too slow. The bait is gone.', DIM)
        elif self.state == 'reel':
            if now >= self.fish_next:
                self.fish_to = random.uniform(2, self.TRACK - 3)
                self.fish_next = now + random.uniform(.35, 1.2) * (1.4 - self.dif * .6)
            speed = 5 + 16 * self.dif
            d = self.fish_to - self.fish_x
            self.fish_x += max(-speed * dt, min(speed * dt, d))
            r = self.pl['rank']
            inside = abs(self.fish_x - self.zone) <= self.zone_w / 2
            easy = 2.0 if self.pl['kind'] in ('junk', 'bottle') else 1.0
            if inside:
                self.progress += dt * .24 * (1 + r * .02) * easy
                self.tension = max(0.0, self.tension - dt * .3)
            else:
                self.progress = max(0.0, self.progress - dt * .05)
                self.tension += dt * (.22 + .38 * self.dif) * (1 - min(.5, r * .02))
            if self.progress >= 1:
                self.state, self.t0, self.leap = 'leap', now, True
            elif self.tension >= 1:
                self.state, self.t0, self.leap = 'snap', now, False
        elif self.state in ('leap', 'snap') and el > .9:
            if self.state == 'leap':
                name = {'fish': None, 'junk': 'Junk.', 'bottle': 'A bottle!'}.get(self.pl['kind'])
                self.finish(True, name or f"{self.LS.FISH[self.pl['fish']][0]}!", GOLD)
            else:
                self.finish(False, 'The line snaps! It got away.', BAD)

    # ------------------------------------------------------------- the keys
    def on_key(self, tok, shift):
        g = self.game
        if tok == 'esc':
            if self.state in ('wait', 'bite', 'reel'):
                g.end_turn(max(1, self.pl['turns'] // 2))
                g.msg('You reel in and wind up the line.')
            self.app.pop()
            return
        if self.state == 'done':
            if tok in ('enter', 'np_enter', 'a'):
                water = self.LS.can_fish(g)
                if water:
                    self.water = water
                    self.cast()
                else:
                    self.app.pop()
            return
        if tok in ('q', 'Q') and self.pl['rank'] >= 20 and self.state == 'wait':
            g.log_mark = len(g.log)
            self.pl = self.LS.plan(g, self.water)
            self.finish(True, 'A practised flick of the wrist...', GOLD)
            return
        if tok in ('enter', 'np_enter', 'space'):
            if self.state == 'wait':
                if self.pl['kind'] == 'none':
                    self.finish(False, 'You strike at nothing.', DIM)
                else:
                    self.pl['kind'] = 'none'
                    self.finish(False, 'Too early! Whatever was there is gone.', DIM)
            elif self.state == 'bite':
                if self.pl['kind'] == 'monster':
                    self.finish(True, 'Something huge pulls back...', BAD)
                else:
                    self.start_reel()
        elif self.state == 'reel' and tok in ('left', 'np4', 'right', 'np6'):
            step = 2.6 * (-1 if tok in ('left', 'np4') else 1)
            half = self.zone_w / 2
            self.zone = max(half, min(self.TRACK - half, self.zone + step))

    # ------------------------------------------------------------- the picture
    def render(self, cv):
        self.update()
        t = self.clock()
        x, y = self.box(cv, self.BW, self.BH, f' Fishing · {self.place} ')
        px0, py0, pw, ph = x + 2, y + 2, self.BW - 4, 22
        wk = self.water
        sky_rows = 0 if wk == 'cave' else 3
        far_rows = {'lake': 2, 'river': 2, 'swamp': 2, 'sea': 0, 'cave': 0}.get(wk, 1)
        bank_rows = 4
        top_water = sky_rows + far_rows
        waters = {'sea': ((24, 62, 104), (6, 22, 52)), 'lake': ((26, 66, 98), (8, 28, 54)), 'river': ((34, 78, 110), (12, 38, 66)),
                  'swamp': ((44, 58, 34), (20, 28, 16)), 'cave': ((14, 26, 44), (4, 8, 16))}
        w_top, w_bot = waters.get(wk, waters['lake'])
        if self.night:
            w_top, w_bot = scale(w_top, .55), scale(w_bot, .55)
        bank_col = {'sea': (54, 46, 30), 'cave': (34, 32, 30), 'swamp': (34, 30, 18)}.get(wk, (38, 32, 20))
        for yy in range(ph):
            for xx in range(pw):
                r = _h2(xx, yy, 3)
                if yy < sky_rows:
                    a, b = ((10, 14, 34), (24, 30, 60)) if self.night else ((60, 84, 126), (110, 136, 170))
                    bg = mix(a, b, yy / max(1, sky_rows))
                    ch, fg = (('·', (220, 220, 240)) if self.night and r < .05 else (' ', bg))
                elif yy < top_water:
                    far = (64, 56, 38) if wk != 'swamp' else (46, 50, 30)        # the far bank: bare earth
                    bg = scale(far, 1 if not self.night else .5)
                    ch, fg = ('▀' if yy == sky_rows else '▄' if yy == top_water - 1 else ' '), \
                        (scale((70, 96, 56), 1 if not self.night else .5) if yy == sky_rows else scale(w_top, .9))
                elif yy < ph - bank_rows:
                    k = (yy - top_water) / max(1, ph - bank_rows - top_water)
                    bg = mix(w_top, w_bot, k)
                    drift = t * (3.0 if wk == 'river' else .6 if wk == 'sea' else .25)
                    rr = _h2(int(xx + drift) if wk != 'cave' else xx, yy, 5)
                    ch, fg = (('~', mix((150, 190, 230), bg, .35)) if rr < .08 else ('≈', mix((110, 160, 210), bg, .4)) if rr < .12
                              else (' ', bg))
                    if wk == 'sea' and yy == top_water:
                        ch, fg = '─', mix((170, 200, 230), bg, .4)                # the horizon
                else:
                    bg = scale(bank_col, 1.0 if not self.night else .6)
                    ch, fg = (',' if r < .25 else '.' if r < .5 else ' '), scale(bank_col, 2.2)
                    if wk == 'cave':
                        ch = '.' if r < .3 else ' '
                if wk == 'cave' and yy < 2:
                    bg = (18, 16, 16)
                    ch, fg = ('▼' if r < .25 else ' '), (60, 56, 52)
                cv.put(px0 + xx, py0 + yy, ch, fg, bg)
        # you, the rod, the line and the float
        mx, my = px0 + 9, py0 + ph - bank_rows
        bx, by = px0 + 40, py0 + top_water + (ph - bank_rows - top_water) // 2
        bob = 0
        if self.state == 'wait':
            bob = 1 if math.sin(t * 2.6) > .85 else 0
        cv.put(mx, my, '@', (255, 246, 220), scale(bank_col, 1.0 if not self.night else .6))
        tipx, tipy = mx + 3, my - 3
        for k in range(1, 4):
            cv.put(mx + k, my - k, '/', (190, 150, 100), None)
        sag = .25 if self.state in ('wait', 'done') else 0
        n = max(1, bx - tipx)
        for k in range(1, n):
            fx = tipx + k
            f = k / n
            fy = round(tipy + (by - tipy) * f + sag * 6 * math.sin(f * math.pi))
            if self.state == 'snap' and f > .5:
                break
            cv.put(fx, fy, '·', (210, 210, 200), None)
        wbg = mix(w_top, w_bot, .5)
        if self.state == 'wait':
            cv.put(bx, by + bob, '°' if bob == 0 else 'o', (250, 110, 90), wbg)
            for rx, ry, t0 in self.ripples[-4:]:
                age = t - t0
                if age < 1.2:
                    col = mix((170, 210, 240), wbg, age / 1.2)
                    cv.put(bx + rx, by + ry, '○' if age < .5 else '·', col, wbg)
        elif self.state == 'bite':
            cv.put(bx, by + 1, '!', (255, 230, 80), wbg)
            for dx, dy in ((-2, 1), (2, 1), (-1, 0), (1, 0), (0, 2)):
                cv.put(bx + dx, by + dy, '~', (170, 220, 250), wbg)
        elif self.state == 'reel':
            sx = bx - 14 + round(self.fish_x / self.TRACK * 28)
            cv.put(bx, by, '≈', (170, 220, 250), wbg)
            dirc = '>' if self.fish_to > self.fish_x else '<'
            cv.put(sx, by + 2, dirc, scale(wbg, 2.2), wbg)
            cv.put(sx + (-1 if dirc == '>' else 1), by + 2, '=', scale(wbg, 1.8), wbg)
        elif self.state == 'leap':
            k = min(1.0, (t - self.t0) / .9)
            lx = round(bx - 6 * k)
            ly = round(by - 5 * math.sin(k * math.pi))
            cv.put(lx, ly, '<', (230, 230, 210), None)
            cv.put(lx + 1, ly, '≈', (200, 210, 220), None)
            cv.put(bx, by, '○', (190, 230, 255), wbg)
        elif self.state == 'snap':
            cv.put(bx, by, '○', (190, 230, 255), wbg)
        # the lower half: what is happening, and the bars
        ly = py0 + ph + 1
        for xx in range(x + 1, x + self.BW - 1):
            cv.put(xx, ly - 1, '─', LINE, PANEL)
        tx = x + 4
        if self.state == 'wait':
            cv.text(tx, ly + 1, 'The float bobs on the water. Wait for it...', FG, PANEL)
            cv.text(tx, ly + 3, 'Ripples come and go. That is not a bite.', DIM, PANEL)
            keys = 'Enter: strike · Esc: reel in and stop' + (' · Q: quick catch' if self.pl['rank'] >= 20 else '')
        elif self.state == 'bite':
            cv.text(tx, ly + 1, 'The float plunges!', (255, 230, 80), PANEL)
            cv.text(tx, ly + 3, 'STRIKE', (255, 120, 80), PANEL)
            left = max(0.0, 1 - (t - self.t0) / self.window)
            for k in range(30):
                cv.put(tx + 8 + k, ly + 3, '█' if k < left * 30 else '░', (255, 200, 90) if k < left * 30 else LINE, PANEL)
            keys = 'Enter: strike · Esc: stop'
        elif self.state in ('reel', 'leap', 'snap'):
            what = {'fish': 'Something on the line. It fights.', 'junk': 'Heavy, and it does not fight. Hm.',
                    'bottle': 'Something light, bobbing up.'}.get(self.pl['kind'], 'Something on the line.')
            if self.pl['kind'] == 'fish' and self.dif > .5:
                what = 'Something big. It fights like a devil.'
            cv.text(tx, ly, what, FG, PANEL)
            trx, ty = tx + 2, ly + 2
            cv.put(trx - 1, ty, '[', LINE, PANEL)
            cv.put(trx + self.TRACK, ty, ']', LINE, PANEL)
            z0, z1 = self.zone - self.zone_w / 2, self.zone + self.zone_w / 2
            for k in range(self.TRACK):
                inz = z0 <= k + .5 <= z1
                cv.put(trx + k, ty, '▒' if inz else '·', (90, 200, 110) if inz else (70, 80, 90), (30, 70, 40) if inz else (14, 24, 34))
            fx = trx + max(0, min(self.TRACK - 1, round(self.fish_x)))
            cv.put(fx, ty, '►' if self.fish_to > self.fish_x else '◄', (255, 240, 200), None)
            cv.text(trx, ty + 1, '←  →  keep the fish in the green', DIM, PANEL)
            cv.text(tx, ty + 3, 'Reeled in', DIM, PANEL)
            bw = 36
            pr = min(1.0, self.progress)
            for k in range(bw):
                cv.put(tx + 12 + k, ty + 3, '█' if k < pr * bw else '░', (110, 200, 230) if k < pr * bw else LINE, PANEL)
            cv.text(tx, ty + 5, 'Line', DIM, PANEL)
            te = min(1.0, self.tension)
            for k in range(bw):
                col = (127, 224, 122) if k < bw * .4 else (240, 200, 90) if k < bw * .7 else (255, 90, 74)
                cv.put(tx + 12 + k, ty + 5, '█' if k < te * bw else '░', col if k < te * bw else LINE, PANEL)
            cv.text(tx + 12 + bw + 2, ty + 5, 'slack' if te < .4 else 'tight' if te < .7 else 'about to go!',
                    GOOD if te < .4 else GOLD if te < .7 else BAD, PANEL)
            keys = '← →: steer · Esc: cut the line'
        else:
            text, col = self.result or ('', FG)
            cv.wrap(tx, ly + 1, self.BW - 8, text, col, PANEL, 2)
            keys = 'Enter: cast again · Esc: done'
        cv.text_center(x + self.BW // 2, y + self.BH - 1, f' {keys} ', DIM, PANEL)


def _h2(x, y, s=0):
    n = (x * 374761393 + y * 668265263 + s * 2246822519) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 65536


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
            ('arrows · numpad', 'Move. Walk into a monster to fight it, into a door to open it.'),
            ('Shift + direction', 'Run, until something interesting happens'),
            ('Enter  or  Space', 'Do the obvious thing here: go in, take the stairs, pick up,'),
            ('', 'talk to whoever is near, read a signpost, open a chest, fish.'),
            ('1  2  3  4  5  6', 'Use a skill from your bar (at your target, or the nearest enemy)'),
            ('Tab  Shift+Tab', 'Pick a target: the next or the previous enemy in sight'),
            ('q   w', 'Drink a health or a mana potion'),
            ('i', 'Your bag: what you carry and wear'),
            ('m', 'The map of the realm; in a town, the town plan (Tab: the realm)'),
            ('t', 'Talk to whoever is near you'),
            ('h', 'Your hireling: orders, gear, how he is doing'),
            ('Esc', 'Let go of your target; else the menu: everything else you can do'),
            ('', 'In a window, Esc goes back. Save and quit is in the menu, under Game.'),
            ('?', 'This help'),
            ('.  or  5', 'Wait a turn'),
            ('Panel, bottom', 'What you can do where you stand, with its key: Enter go in,'),
            ('', 't talk, a fish, E eat, F forage, R rest... Learn them as you go.'),
            ('', ''),
            ('That is all you need.', 'Everything else is in the menu (Esc). Each item there shows'),
            ('', 'a shortcut of its own, for when you know your way around:'),
            ('', 'c character, C life skills, z skills, v bestiary, e journal,'),
            ('', 'x explore, o look, g pick up, P brewing; travel: on the map (m, Tab).'),
            ('', 'A capital letter means: with Shift.'),
            ('F11  Alt+Enter', 'Fullscreen'),
        ]),
        ('The world', [
            ('Roads', 'Roads are patrolled and fairly safe. The further you stray, the worse it gets.'),
            ('Danger', 'Inspect the land (O) to see its danger. Night brings the dead and bigger packs.'),
            ('Knowledge', 'At first you only know where Thornfield lies. Signposts (┬), townsfolk and'),
            ('', 'travellers tell you where places lie, but the land you only learn by walking it.'),
            ('Π ruin', 'An old ruin with a way down. Small, with a skill tome at the bottom.'),
            ('† shrine', 'Pray for a blessing. An offering makes it last longer. Every shrine has its god.'),
            ('∆ camp', 'A bandit camp. Kill them all and the strongbox is yours.'),
            ('Ψ stones', 'Standing stones. Touch them to learn from old memories.'),
            ('¤ wagon', 'An abandoned wagon. Loot, or a trap.'),
            ('Events', 'On the road things happen: wounded travellers, peddlers, tolls, storms...'),
            ('@ travellers', 'Walk into a traveller to talk. Some have a job for you and wait for you afterwards'),
            ('', 'at the inn of the town they were going to (see the journal).'),
            ('Towns', 'Trader: goods · innkeeper: jobs, a bed, gossip (G) · outfitter: gear, identify, mend'),
            ('', 'temple: heal, curses, raise the dead · stablemaster: mules and carts'),
            ('', 'castellan (in strongholds): war jobs'),
            ('Factions', 'Different every world. Work for one to win favour; hurt it and its gates close.'),
            ('Peoples', 'Humans, elves, dwarves, halflings and half-orcs each like and distrust each other.'),
            ('', 'How a town sees your people changes its prices and how its faction greets you.'),
            ('News', 'News travels on foot, and slowly. Ask the innkeeper for gossip, the factor of the'),
            ('', "Merchants' Guild for prices and trade work, the captain for trouble and bounties,"),
            ('', 'travellers and sailors for news from far away. What comes from afar is old.'),
            ('Calendar', 'Twelve months of thirty days, from Deepfrost to Longnight; seven days in a week.'),
        ]),
        ('Ways and guilds', [
            ('Travel', 'On the map (M) Tab picks a place you have been and shows the way; Enter sets out:'),
            ('', 'by the roads. Enemies, travellers, events, hunger, wounds or any key stop you.'),
            ('Old ways', 'Hidden Varnish paths, a faint broken grey-green line. You see only what you have'),
            ('', 'seen: walk on one, hear a rumour (where it starts), read an old map or buy a chart'),
            ('', '(a stretch of it), or look out from a watchtower (as far as you can see). The rest'),
            ('', 'you walk. Faster than open land, never patrolled. They lead over passes, to'),
            ('', 'waystations (Σ, a safe rest), milestones (╥), vaults (Φ) that open to the old word,'),
            ('', "graveyards, a smugglers' den, lost ruins, and over a pass into a hidden valley (•)."),
            ('Glades', 'Elven glades (♠) hide deep in the woods, off the map until you walk close enough'),
            ('', 'to see their lanterns. An elder there knows the next glade, and the way to the'),
            ('', 'elven city under the Elder Tree.'),
            ('Gear', 'Ten slots. Normal, exceptional and elite grades; Strength and Dexterity needs.'),
            ('', 'Uniques roll within a range; sets of 2-4 pieces give bonuses. Two-handers take the'),
            ('', 'off-hand. Resist fire, cold, lightning and poison, up to 75%.'),
            ('Elements', 'Monsters resist some elements and fear others. Fight a kind to learn which.'),
            ('Guilds', 'At most two combat guilds, and rivals will not share you; the crafts take anyone.'),
            ('', 'Five ranks, earned with guild jobs. Masters teach techniques to those who earn them.'),
            ('', 'Standing fades if you do nothing for a guild, but not below your rank.'),
            ('Secrets', 'Some guilds hang out no sign. Listen for rumours, and watch the chalk marks.'),
            ('Harbours', 'A jetty in a hamlet, a quay in a town, a deep berth and a harbour wall in a city;'),
            ('', 'boats, ships, fish markets and sailors full of tales. No sailing yet.'),
        ]),
        ('Coin and company', [
            ('Money', 'Jobs pay modestly; trade is where the money is. Coin goes on beds, meals, repairs,'),
            ('', 'wages and the temple.'),
            ('Wear', 'Gear wears with use and breaks when worn out. Outfitters mend it (R); a repair kit'),
            ('', 'patches it up on the road.'),
            ('Guilds', 'Members buy from the quartermaster for less, sleep in the hall cheap or for nothing,'),
            ('', 'have their gear mended cheaper, and the higher their rank, the better the pay.'),
            ('Sleeping out', 'Rest in the open and you make camp: a fire keeps beasts off but draws robbers.'),
            ('', 'A tent keeps you dry and safer; a hireling keeps watch. An inn bed: Well rested.'),
            ('Hirelings', 'Sellswords sign on in the barracks of the cities, now and then in an inn: a fee,'),
            ('', 'a daily wage and their food. Unpaid or unfed, they sour, and in the end they walk.'),
            ('', 'Defender, warrior, archer, healer or mage; four pieces of gear that wear like yours.'),
            ('Orders (h)', 'Follow, defend me, attack my target (Tab), hold position, or stay out of it.'),
            ('Danger', 'Monsters choose whom to go for: who hurt them lately, who stands in their way, who'),
            ('', 'looks soft. Beasts go for the nearest; clever foes for the healer. A defender takes'),
            ('', 'blows meant for you. Hurt badly, a hireling may run, and come back when it is over.'),
            ('Death', 'Hardcore: a fallen hireling is dead, his gear on his body. Softcore: a temple raises'),
            ('', 'him for a fee. When you fall, he falls with you.'),
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
            ('Life skills', 'Grow by doing. Fishing (a by water, with a pole), foraging (Shift+F), herbalism'),
            ('', '(picking and knowing herbs), alchemy (potions, P) and brewing (ale, wine, mead, P).'),
            ('Magic items', 'Rare, and unidentified when found. Outfitters and priests identify them.'),
            ('', 'Some are cursed: once worn they stay on until a priest lifts the curse.'),
            ('Bestiary', 'Every kill teaches you. Higher knowledge: more damage against that kind,'),
            ('', 'and they hit you less often (V).'),
            ('Death', 'Hardcore: final. Softcore: the priests raise you, for a fee from your purse;'),
            ('', 'your pack stays with your body and you are weak for a day or two.'),
            ('', 'No coin for the temple: your tale ends there.'),
            ('Fishing', 'A game of its own (a, by water): strike when the float plunges, then keep the fish'),
            ('', 'in the green while the line holds.'),
            ('Rarity', 'normal · magic (blue) · rare (yellow) · unique (gold)'),
            ('x', 'Auto-explore and travel play out step by step; press any key to stop.'),
        ]),
    ]

    def __init__(self, app):
        super().__init__(app)
        self.page = 0

    @classmethod
    def lines(cls, page):
        """The rows of a page, with any description too long for the box carried on to the next row."""
        kw = 28 if page == 0 else 14
        out = []
        for k, d in cls.PAGES[page][1]:
            parts = wrap_text(d, 98 - kw) if d else ['']
            out.append((k, parts[0]))
            out += [('', more) for more in parts[1:]]
        return out

    def render(self, cv):
        name, rows = self.PAGES[self.page]
        x, y = self.box(cv, 104, 28, f'Help: {name} ({self.page + 1}/{len(self.PAGES)})')
        kw = 28 if self.page == 0 else 14
        for i, (k, d) in enumerate(self.lines(self.page)):
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
        labels = [wrap_text(label, 57) for label, _k in ev['options']]
        h = len(lines) + sum(len(lb) for lb in labels) + 7
        x, y = self.box(cv, 66, h, ev['title'])
        for i, ln in enumerate(lines):
            cv.text(x + 3, y + 2 + i, ln, FG, PANEL)
        yy = y + 3 + len(lines)
        for i, lb in enumerate(labels):
            cv.text(x + 3, yy, LETTERS[i], GOLD, PANEL)
            for ln in lb:
                cv.text(x + 5, yy, ln, FG, PANEL)
                yy += 1
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
        does = D.DOES.get(k)
        traits = [t for t, on in (('fast', d['fast']), ('slow', d['slow']), ('ranged', d['ranged']),
                                  ('spellcaster', d['caster']), ('poisonous', d['poison']), ('regenerates', d['regen']),
                                  ('drains life', d['leech']), ('erratic', d['erratic']), ('summoner', bool(d['summon'])))
                  if on]

        def word(v):
            return 'very low' if v < .7 else 'low' if v < .95 else 'average' if v < 1.25 else 'high' if v < 1.7 else 'very high'

        def section(head, text, col=FG, rows=3):
            nonlocal yy
            cv.text(rx, yy, head, DIM, PANEL)
            yy += 1
            yy += cv.wrap(rx, yy, w, text, col, PANEL, rows) + 1

        yy = y + 5
        yy += cv.wrap(rx, yy, w, lore[0], FG, PANEL, 3) + 1
        if does:
            # the three layers: how they look, what they do (3 slain), their weakness and home (10 slain)
            if r >= 1:
                section('WHAT THEY DO', does + (f" ({', '.join(traits)}.)" if traits else ''), FG, 4)
            else:
                cv.text(rx, yy, 'Slay 3 to learn what they do.', DIM, PANEL)
                yy += 2
            if r >= 2:
                section('WEAKNESS', lore[2], GOOD, 2)
                section('HOME', lore[1], FG, 2)
                yy += cv.wrap(rx, yy, w, f"Health {word(d['hp'])} · damage {word(d['dmg'])} · armor {word(d['df'])}"
                              + (f" · from danger level {d['min_l']}" if d.get('min_l') else ''), DIM, PANEL, 2)
            elif r == 1:
                cv.text(rx, yy, 'Slay 10 to learn their weakness and where they live.', DIM, PANEL)
                yy += 2
        else:
            if r >= 1:
                section('HABITAT', lore[1], FG, 2)
                cv.text(rx, yy, 'TRAITS', DIM, PANEL)
                yy += cv.wrap(rx + 8, yy, w - 8, ', '.join(traits) or 'none to speak of', FG, PANEL, 3) + 1
            else:
                cv.text(rx, yy, 'Slay 3 to learn where they live and how they fight.', DIM, PANEL)
                yy += 2
            if r >= 2:
                cv.text(rx, yy, 'STRENGTH', DIM, PANEL)
                yy += cv.wrap(rx + 10, yy, w - 10, f"health {word(d['hp'])} · damage {word(d['dmg'])} · armor {word(d['df'])}",
                              FG, PANEL, 3)
                if d.get('min_l'):
                    cv.text(rx + 10, yy, f"found from danger level {d['min_l']} and up", FG, PANEL, maxw=w - 10)
                    yy += 1
                yy += 1
            elif r == 1:
                cv.text(rx, yy, 'Slay 10 to judge their strength.', DIM, PANEL)
                yy += 2
            if r >= 3:
                section("HUNTER'S TIP", lore[2], GOOD, 2)
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
             'Enter does the obvious thing, Tab picks a target, Esc opens the menu, ? is help.'),
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
        end = 'In hardcore, death is final.' if p.hardcore else 'Your tale ends here.'
        cv.wrap(x + 3, y + 2, 54, f"{p.name} was slain by {g.cause or 'fate'} in {g.loc_name()}. {end}", FG, PANEL, 3)
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
    BOX_W, BOX_H = 104, 30

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
            cv.wrap(x + 56, y + 1, self.BOX_W - 58, D.EVENTS[s.event[0]]['text'].format(town=s.name), INFO, PANEL, 2)
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
        cheap, dear = ECO.in_season(SE.doy(g.day))
        names = lambda gs: ', '.join(D.GOODS[k]['name'] for k in gs) or 'nothing'
        cv.text(x + 2, y + self.BOX_H - 5, f'In season, cheap now: {names(cheap)}.', GOOD, PANEL, maxw=self.BOX_W - 4)
        cv.text(x + 2, y + self.BOX_H - 4, f'Out of season, dear now: {names(dear)}.', BAD, PANEL, maxw=self.BOX_W - 4)
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
             'hunt': 'Wanted: a named enemy',
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
        cv.text(x + 2, y + 1, f"{local}{D.FACTIONS[f]['short']}: {WAR.standing(frep)} ({frep})", DIM, PANEL)
        cv.text_right(x + self.BOX_W - 3, y + 1, f'{len(MS.active(g))}/{MS.MAX_ACTIVE} jobs taken', DIM, PANEL)
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
            nt = cv.wrap(x + 60, y + 3, 38, mi.title, GOLD, PANEL, 3)
            n = cv.wrap(x + 60, y + 4 + nt, 38, mi.desc, FG, PANEL, 10)
            yy = y + 5 + nt + n
            cv.text(x + 60, yy, f'Reward: {fmt(mi.reward)}', GOLD, PANEL)
            local_rep = src.rep if not self.hold else max(0, frep)
            if local_rep > 0:
                cv.text(x + 60, yy + 1, f'+{fmt(round(mi.reward * min(local_rep, 100) / 200))} reputation bonus', GOOD, PANEL)
            if mi.deadline:
                cv.text(x + 60, yy + 2, f'Deadline: {CAL.short(mi.deadline)}', DIM, PANEL)
                cv.text(x + 60, yy + 3, f'Today is {CAL.short(g.day)}.', DIM, PANEL)
            from . import jobs as JB
            cv.text(x + 60, yy + 4, self.KINDS.get(mi.kind) or JB.LABEL.get(mi.kind, mi.kind.capitalize()), INFO, PANEL)
            if mi.faction:
                cv.wrap(x + 60, yy + 5, 38, f"Reputation with the {D.FACTIONS[mi.faction]['short']}: +{mi.rep if self.hold else 2}", GOOD, PANEL, 2)
        from . import crime as CR
        notices = [st for st in CR.wanted_in(g) if self.hold or st.id != src.id]
        if notices:
            st = notices[0]
            what = (getattr(st, 'crimes', None) or ['crimes'])[-1]
            cv.text(x + 2, y + self.BOX_H - 5, 'Nailed to the board:', DIM, PANEL)
            cv.wrap(x + 2, y + self.BOX_H - 4, 55, f'WANTED: {g.player.name}, for {what} near {st.name}. Reward {fmt(CR.bounty(st))}.',
                    BAD, PANEL, 2)
        if not self.hold:
            cv.text(x + 60, y + self.BOX_H - 5, 'G: gossip with the innkeeper', GOLD, PANEL)
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
        elif tok == 'G' and not self.hold:
            from . import news as NW
            keeper = next((o for o in g.map.mons if getattr(o, 'role', '') == 'inn' and cheb(o.x, o.y, g.player.x, g.player.y) <= 3), None)
            self.app.push(DialogScreen(self.app, keeper.name if keeper else 'The innkeeper', NW.gossip(g)))
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


def hunt_areas(g):
    """(x, y, radius) of each named enemy you are hunting out in the land, of the missing and of the fallen star."""
    from . import named as NM
    from . import jobs as JB
    out = list(JB.areas(g))
    for mi in MS.active(g):
        if mi.kind == 'hunt' and mi.state == 'active':
            n = NM.get(g, mi.data.get('nid'))
            if n and n.alive and not n.did:
                out.append(NM.area(g, n))
    return out


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
                extra += f" · {mi.data.get('person', 'caravan')} health {mi.data['hp']}"
            from . import jobs as JB
            if mi.kind in JB.KINDS and JB.line(g, mi):
                extra += ' · ' + JB.line(g, mi)
            if mi.kind == 'hunt':
                from . import named as NM
                yy += cv.wrap(x + 4, yy + 1, 93, NM.job_line(g, mi), DIM, PANEL, 2) + 1
                continue
            yy += cv.wrap(x + 4, yy + 1, 93, extra, DIM, PANEL, 2) + 1
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

    def __init__(self, app, travel=False):
        super().__init__(app)
        g = self.game
        p = g.player
        here = g.here
        self.cx, self.cy = (here.x, here.y) if here else (p.x, p.y) if g.cur == 'over' else g.over_pos
        self.origin = (self.cx, self.cy)
        self.dests = self.destinations()
        self.pick = None                 # the place picked to travel to (index in dests)
        self.route = []
        if travel:
            WorldMapScreen.zoom = 1
            if self.dests:
                self.choose(0)

    def destinations(self):
        """The places you have been and could walk back to, nearest first (not the one you are in)."""
        g = self.game
        here = g.here
        site = g.world.sites[g.map.site] if getattr(g.map, 'site', None) is not None else None
        ox, oy = self.origin
        out = []
        for st in g.world.settlements:
            if g.has_visited('s', st.id) and not (here and here.id == st.id):
                out.append(('s', st.id, st.name, st.kind_name, st.x, st.y))
        for st in getattr(g.world, 'sites', ()):
            if g.has_visited('site', st.id) and st is not site:
                out.append(('site', st.id, st.name, st.kind, st.x, st.y))
        for d in g.world.dungeons.values():
            if g.has_visited('d', d.id) and getattr(d, 'town', None) is None:
                out.append(('d', d.id, d.name, 'dungeon', d.x, d.y))
        out.sort(key=lambda r: cheb(r[4], r[5], ox, oy))
        return [r for r in out if (r[4], r[5]) != (ox, oy)]

    def can_travel(self):
        return self.game.map.kind in ('over', 'town') and not getattr(self.game.map, 'underground', False)

    def choose(self, i):
        g = self.game
        self.pick = i % len(self.dests)
        k, ref, name, kind, x, y = self.dests[self.pick]
        self.cx, self.cy = x, y
        self.route = []
        if self.can_travel():
            p = g.player
            sx, sy = self.origin
            save = (p.x, p.y)
            p.x, p.y = sx, sy
            om = g.maps['over']
            cost = lambda t: (2 if t == D.ROAD else 3 if t in (D.TOWN, D.CITY) else D.TILES[t].cost * 3) if D.TILES[t].walk else None
            from . import world as WO
            self.route = WO.dijkstra_path(om, (sx, sy), (x, y), cost) or []
            p.x, p.y = save
            self.turns = sum(D.TILES[om.tile(cx_, cy_)].cost for cx_, cy_ in self.route)

    def eta(self):
        hours = max(1, round(getattr(self, 'turns', 0) / (D.DAY_LEN / 24)))
        if hours < 20:
            return f'about {hours} hours'
        days = hours / 24
        return 'about a day' if days < 1.5 else f'about {round(days)} days'

    def render(self, cv):
        if self.zoom:
            self.render_detail(cv)
        else:
            self.render_overview(cv)

    def render_detail(self, cv):
        g = self.game
        om = g.maps['over']
        w = g.world
        season = SE.Now(g)
        x, y = self.box(cv, 104, 58, 'Map of the realm (close-up)')
        vw, vh = 100, 55
        self.cx = max(vw // 2, min(om.w - vw // 2, self.cx))
        self.cy = max(vh // 2, min(om.h - vh // 2, self.cy))
        ox, oy = self.cx - vw // 2, self.cy - vh // 2
        bx, by = x + 2, y + 1
        taint = getattr(w, 'taint', None)
        ways = getattr(om, 'oldway', {})
        ways_seen = g.__dict__.get('ways_seen', set())
        for vy in range(vh):
            for vx in range(vw):
                mx, my = ox + vx, oy + vy
                if not om.inb(mx, my):
                    continue
                i = my * om.w + mx
                if not om.seen[i]:
                    continue
                ch, fg, bg = SE.look(g, om, i, LOOK.get(om, i), season)
                if i in ways and i in ways_seen:
                    ch, fg = ways[i], LOOK.PATH_FG
                if taint and taint[i]:
                    ch, fg, bg = LOOK.tainted((ch, fg, bg), w.evils[taint[i] - 1].d['taint'], i)
                if WorldMapScreen.show_factions:
                    bg = mix(bg, D.FACTIONS[w.region_at(mx, my).faction]['fg'], .25)
                cv.put(bx + vx, by + vy, ch, fg, bg)

        def inview(px, py):
            return ox <= px < ox + vw and oy <= py < oy + vh
        for st in getattr(w, 'sites', ()):
            if om.seen[st.y * om.w + st.x] and inview(st.x, st.y) and not FKunfound(st):
                cv.put(bx + st.x - ox, by + st.y - oy, st.glyph[0], st.glyph[1], (40, 34, 26))
        for poi in w.pois:
            if poi.found and inview(poi.x, poi.y):
                cv.put(bx + poi.x - ox, by + poi.y - oy, poi.glyph[0], poi.glyph[1], (34, 28, 22))
        for hd in w.holds:
            if om.seen[hd.y * om.w + hd.x] and inview(hd.x, hd.y):
                cv.put(bx + hd.x - ox, by + hd.y - oy, 'Ω' if hd.kind == 'castle' else '╬', D.FACTIONS[hd.faction]['fg'], (40, 30, 20))
        for ax, ay, r in hunt_areas(g):
            for yy in range(ay - r, ay + r + 1):
                for xx in range(ax - r, ax + r + 1):
                    if inview(xx, yy) and (xx - yy) % 3 == 0:
                        cv.put(bx + xx - ox, by + yy - oy, '/', (230, 170, 80), (70, 40, 20))
        for mi in MS.active(g):
            if mi.kind == 'hunt' and mi.state == 'active':
                continue
            (tx, ty), _ = MS.target_pos(g, mi)
            if inview(tx, ty):
                cv.put_bg(bx + tx - ox, by + ty - oy, (110, 80, 16))
        for rx_, ry_ in self.route:                   # the way you would walk
            if inview(rx_, ry_):
                cv.put_bg(bx + rx_ - ox, by + ry_ - oy, (96, 70, 30))
        if self.pick is not None:
            k_, ref_, name_, kind_, tx_, ty_ = self.dests[self.pick]
            if inview(tx_, ty_) and int(time.monotonic() * 2.5) % 2 == 0:
                cv.put_bg(bx + tx_ - ox, by + ty_ - oy, (200, 150, 40))
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
        if self.pick is not None:
            k_, ref_, name_, kind_, tx_, ty_ = self.dests[self.pick]
            if self.can_travel():
                line = f' {name_} ({kind_}) · {self.eta()} · Enter: travel · Tab: next place · Esc: close '
            else:
                line = f' {name_} ({kind_}) · you can only set out from the open land or a town · Tab: next '
            cv.text_center(W // 2, y + 57, line, GOLD, PANEL)
        else:
            hint = ' Tab: pick a place you have been' if self.dests else ''
            cv.text_center(W // 2, y + 57, f'{hint} · arrows: scroll · Z: whole realm · F: factions · Esc: close ', DIM, PANEL)

    def render_overview(self, cv):
        g = self.game
        om = g.maps['over']
        w = g.world
        season = SE.Now(g)
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
                ch, fg, bg = SE.look(g, om, bi, LOOK.get(om, bi), season)
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
        for ax, ay, r in hunt_areas(g):
            for yy in range(ay - r, ay + r + 1, 2):
                for xx in range(ax - r, ax + r + 1, 2):
                    if om.inb(xx, yy) and (xx - yy) % 6 == 0:
                        cv.put(bx + S(xx), by + S(yy), '/', (230, 170, 80), (70, 40, 20))
        for mi in MS.active(g):
            if mi.kind == 'hunt' and mi.state == 'active':
                continue
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
        if tok == 'tab' and self.dests:
            WorldMapScreen.zoom = 1
            self.choose((self.pick if self.pick is not None else -1) + (-1 if shift else 1))
            return
        if tok in ('enter', 'np_enter') and self.pick is not None and self.can_travel():
            g = self.game
            k, ref = self.dests[self.pick][:2]
            self.app.pop()
            g.log_mark = len(g.log)
            self.app.start_auto(g.travel_iter(k, ref), .025, 'Travelling')
            return
        if tok in ('z', 'Z', '+', '-'):
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


class TownPlanScreen(Modal):
    """The plan of the town you are in: a letter at every building, and what it is. Tab: the map of the realm."""
    tall = False

    def render(self, cv):
        g = self.game
        m = g.map
        x, y = self.box(cv, 104, 58, f'Plan of {m.name}')
        vw, vh = 72, 55
        f = max(1.0, m.w / vw, m.h / vh)
        bx, by = x + 2, y + 1
        pri = {D.WALL: 9, D.DOOR: 8, D.ODOOR: 8, D.FOUNTAIN: 7, D.WELL: 7, D.STALL: 6, D.WATER: 5, D.SHALLOW: 5, D.PATH: 4,
               D.PLANK: 3, D.FLOOR: 3, D.FIELD: 2, D.TREE: 2, D.GRASS: 1}
        for cy in range(min(vh, int(m.h / f) + 1)):
            for cx in range(min(vw, int(m.w / f) + 1)):
                best, bi = -1, None
                for yy in range(int(cy * f), min(m.h, int((cy + 1) * f))):
                    for xx in range(int(cx * f), min(m.w, int((cx + 1) * f))):
                        i = yy * m.w + xx
                        pr = pri.get(m.t[i], 1)
                        if pr > best:
                            best, bi = pr, i
                if bi is None:
                    continue
                ch, fg, bg = LOOK.get(m, bi)
                cv.put(bx + cx, by + cy, ch, scale(fg, .8), bg)
        p = g.player
        blds = sorted(getattr(m, 'buildings', []), key=lambda b: (b['box'][1], b['box'][0]))
        lx = x + 76
        cv.text(lx, y + 1, 'IN TOWN', DIM, PANEL)
        yy = y + 3
        for k, b in enumerate(blds[:24]):
            bx_, by_, bw_, bh_ = b['box']
            sx, sy = bx + int((bx_ + bw_ / 2) / f), by + int((by_ + bh_ / 2) / f)
            cv.put(sx, sy, LETTERS[k], (20, 16, 12), GOLD)
            glyph, col = TW.SIGN_GLYPH.get(b['kind'], ('·', DIM))
            cv.text(lx, yy, LETTERS[k], GOLD, PANEL)
            cv.put(lx + 2, yy, glyph, col, PANEL)
            n = cv.wrap(lx + 4, yy, 22, b['name'], FG, PANEL, 2)
            yy += n
            if yy > y + 54:
                break
        cv.put(bx + int(p.x / f), by + int(p.y / f), '@', (255, 246, 220), (150, 40, 28))
        cv.text_center(W // 2, y + 57, ' Tab: the map of the realm · Esc: close ', DIM, PANEL)

    def on_key(self, tok, shift):
        if tok == 'tab':
            self.app.replace(WorldMapScreen(self.app))
        elif tok in ('esc', 'm', 'enter', 'space'):
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
        x, y = self.box(cv, 72, 24, f' {self.name} ')
        cv.text(x + 3, y + 1, f"A temple of {gd['name']}, {gd['title']}", gd['fg'], PANEL)
        cv.text(x + 3, y + 2, f"{gd['domain'].capitalize()}.", DIM, PANEL, maxw=66)
        cv.text(x + 3, y + 3, f"Pleased by {gd['likes']}.", DIM, PANEL, maxw=66)
        cv.wrap(x + 3, y + 5, 66, self.said, FG, PANEL, 2)
        no = self.refused
        sick = any(k in ('diseased', 'cursed') for k in getattr(p, 'status', {}))
        hurt = p.life < s['max_life'] or p.mana < s['max_mana'] or p.poison or sick
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
        from . import mercs as MC
        mc = MC.fallen(g)
        if mc:
            fee = MC.raise_fee(g, mc)
            rows.append(('g', f'Raise {mc.name} from the dead', fmt(fee), p.gold >= fee and not no))
        for i, (k, a, b, ok) in enumerate(rows):
            yy = y + 8 + i * 2
            cv.text(x + 3, yy, k, GOLD if ok else DIM, PANEL)
            cv.text(x + 5, yy, a, FG if ok else DIM, PANEL)
            cv.text_right(x + 68, yy, b, GOLD if ok else DIM, PANEL)
        if g.here is not None and not no:
            cv.text(x + 3, y + 21, 'w', GOLD, PANEL)
            cv.text(x + 5, y + 21, 'Ask if the temple has work for you', FG, PANEL)
        cv.text(x + 3, y + 22, f'Your purse: {fmt(p.gold)}', DIM, PANEL)
        cv.text_right(x + 68, y + 22, GD.standing(g), GD.GODS[mine]['fg'] if mine else DIM, PANEL)
        cv.text_center(W // 2, y + 23, ' letter: choose · Esc: leave ', DIM, PANEL)

    def on_key(self, tok, shift):
        g = self.game
        p = g.player
        GD = self.GD
        g.log_mark = len(g.log)
        if tok == 'esc':
            self.app.pop()
            return
        if self.refused and tok in 'abcdefgw':
            self.said = '"You heard me. Out."'
            return
        if tok == 'w' and g.here is not None:
            from . import news as NW
            from . import jobs as JB
            priest = next((o for o in g.map.mons if getattr(o, 'role', '') == 'healer'), None)
            self.app.pop()
            if priest:
                NW.offer(g, priest, 'temple', JB.TEMPLE, 1.0, '"The faithful have need of someone like you:"')
            return
        if tok == 'a':
            s = g.stats()
            sick = any(k in ('diseased', 'cursed') for k in getattr(p, 'status', {}))
            if p.life >= s['max_life'] and p.mana >= s['max_mana'] and not p.poison and not sick:
                self.said = '"You look well, child. Come back when the world has had its way with you."'
                return
            p.life, p.mana, p.poison = s['max_life'], s['max_mana'], None
            from . import behave as BH
            BH.cure(g)
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
        elif tok == 'g':
            from . import mercs as MC
            mc = MC.fallen(g)
            if mc:
                if MC.raise_up(g, mc):
                    self.said = f'"Rise." Breath shudders back into {mc.name}.'
                else:
                    self.said = f'"The prayers for the dead are long, and the candles are dear. {fmt(MC.raise_fee(g))}."'
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
                   ('travel', 'Travel', 'on the map: Tab picks a place you have been, Enter sets out'), ('x', 'Explore', 'wander a dungeon until something turns up')]),
        ('Actions', [('t', 'Talk', 'to someone near you'), ('h', 'Hireling', 'orders and gear for your sellsword'), ('o', 'Look around', 'inspect anything you can see'),
                     ('g', 'Pick up', 'what lies at your feet'), ('d', 'Drop', 'something from your bag'),
                     ('E', 'Eat', 'the food that fits your hunger best'), ('F', 'Forage', 'search the wild for food and herbs'),
                     ('a', 'Fish', 'by water, with a fishing pole'), ('f', 'Shoot', 'at the nearest enemy, with a bow'),
                     ('P', 'Alchemy & brewing', 'potions, ale, wine and mead'), ('p', 'Town portal', 'read a scroll of town portal'),
                     ('R', 'Rest', 'until you are healed')]),
        ('Game', [('?', 'Help', 'keys and how things work'), ('quit', 'Save and quit', 'your hero waits for you')]),
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
            cv.text_right(x + 61, yy, '' if k == 'quit' else k, scale(GOLD, .8), bg)
        k, name, desc = items[self.sel]
        cv.wrap(x + 3, y + n + 3, 58, desc, DIM, PANEL, 2)
        cv.text_center(W // 2, y + n + 5, ' ←→ group · ↑↓ item · Enter: do it · Esc: close ', DIM, PANEL)

    def on_key(self, tok, shift):
        items = self.GROUPS[self.group][1]
        keys = [k for _g, its in self.GROUPS for k, _n, _d in its]
        if tok == 'esc':
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
        elif tok in keys and tok != 'quit':
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
