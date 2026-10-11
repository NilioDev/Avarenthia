"""Screens, rendering and input handling. Independent of tcod: it draws on a Canvas
and receives key tokens ('a', 'A', 'up', 'np7', 'enter', 'esc', '>' ...)."""
import random
import time

from . import data as D
from . import economy as ECO
from . import engine as E
from . import events as EV
from . import missions as MS
from . import skills as SK
from . import towns as TW
from . import war as WAR
from .canvas import scale, mix, wrap_text
from .data import DOWN, UP, TOWN, ENTR, WALL
from .worldgen import cheb

W, H = 110, 30
MAP_W, MAP_H = 80, 23
LOG_Y = 24
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

ORB_MASK = ['  #####  ', ' ####### ', '#########', ' ####### ', '  #####  ']


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

    def key(self, tok, shift=False):
        self.top.on_key(tok, shift)
        self.after_action()

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
        elif req[0] == 'castellan':
            self.push(BoardScreen(self, req[1], hold=True))
        elif req[0] == 'dialog':
            self.push(DialogScreen(self, req[1], req[2]))
        elif req[0] == 'choice':
            if g.pending:
                self.push(ChoiceScreen(self))
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
            if s.overlay:
                cv.dim(.35)
            s.render(cv)
        t = time.monotonic()
        self.effects = [e for e in self.effects if t - e[1] < (e[2][4] if e[0] == 'flash' else 2.5 if e[0] == 'speech' else .8)]
        self.hit_times = {k: v for k, v in self.hit_times.items() if t - v < .15}


class Screen:
    overlay = False

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
TITLE = [
    ' ▄▄▄ █  █ ████  ▄▄▄  ████ ███    █   █  ▄▄  █    ████',
    '█    █  █ █▄▄▀ ▀▄▄▄  █▄▄  █  █   ▀▄ ▄▀ █▄▄█ █    █▄▄ ',
    '▀▄▄▄ ▀▄▄▀ █  █ ▄▄▄▀  █▄▄▄ █▄▄▀    ▀█▀  █  █ █▄▄▄ █▄▄▄',
]


class MainMenu(Screen):
    def __init__(self, app):
        super().__init__(app)
        self.saved = E.load_game()

    def render(self, cv):
        for i, ln in enumerate(TITLE):
            cv.text_center(W // 2, 7 + i, ln, BLOOD)
        cv.text_center(W // 2, 11, 'an ASCII action roguelike', DIM)
        y = 15
        if self.saved:
            p = self.saved.player
            cv.text_center(W // 2, y, f"[C] Continue as {p.name}, level {p.lvl} ({'hardcore' if p.hardcore else 'softcore'})", GOLD)
            y += 2
        cv.text_center(W // 2, y, '[N] New game', FG)
        cv.text_center(W // 2, y + 2, '[Esc] Quit', DIM)
        cv.wrap(25, 24, 50, 'Explore an ADOM-style vale, clear monster-packed dungeons, hunt magic, rare and unique loot, '
                            'and destroy the lich Morvenna. Hardcore: death is permanent.', DIM)

    def on_key(self, tok, shift):
        if tok == 'c' and self.saved:
            g = self.saved
            g.msg('Welcome back.', 'info')
            g.log_mark = len(g.log) - 1
            self.app.start_game(g)
        elif tok in ('n', 'enter'):
            self.app.replace(NameScreen(self.app))
        elif tok == 'esc':
            self.app.quit()


class NameScreen(Screen):
    def __init__(self, app):
        super().__init__(app)
        self.name = ''

    def render(self, cv):
        cv.text_center(W // 2, 12, 'What is your name, wanderer?', GOLD)
        box = (self.name + '_').ljust(20)
        cv.text(W // 2 - 10, 15, box, FG, (40, 32, 26))
        cv.text_center(W // 2, 18, 'Type a name and press Enter. Leave it empty to be called Wanderer.', DIM)
        cv.text_center(W // 2, 20, 'Esc goes back', DIM)

    def on_key(self, tok, shift):
        if tok == 'enter':
            self.app.replace(OptionsScreen(self.app, self.name.strip() or 'Wanderer'))
        elif tok == 'esc':
            self.app.replace(MainMenu(self.app))
        elif tok == 'backspace':
            self.name = self.name[:-1]
        elif tok == 'space' and len(self.name) < 18:
            self.name += ' '
        elif len(tok) == 1 and (tok.isalnum() or tok in "-'") and len(self.name) < 18:
            self.name += tok


class OptionsScreen(Screen):
    def __init__(self, app, name):
        super().__init__(app)
        self.name = name
        self.hardcore = False
        self.seed = ''
        self.sel = 0

    def render(self, cv):
        cv.text_center(W // 2, 4, f'A new life for {self.name}', GOLD)
        cv.wrap(28, 6, 54, 'You have no class. You become what you practise: swing a sword and you grow into a swordsman, '
                          'cast fire and the flames answer you. Every discipline unlocks new skills as it rises, '
                          'and you carry six of them at a time.', DIM)
        rows = [('Mode', ('HARDCORE: death is permanent.' if self.hardcore else
                          'SOFTCORE: you wake in a temple, but your backpack, cargo and gold stay with your body.')),
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
            self.app.start_game(E.Game(self.name, self.hardcore, int(self.seed) if self.seed else None))
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
        torch = m.kind in ('dungeon', 'siege')
        night = TW.is_night(g)
        portal = m.portal_pos if (m.kind == 'town' and g.portal and g.portal.get('sid') == m.sid) else None
        vis = g.vis
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
                tid = m.t[i]
                td = D.TILES[tid]
                ch = td.ch
                fg = m.wall_fg if (tid == WALL and m.wall_fg) else td.fg
                bg = td.bg or BG
                if portal and (mx, my) == portal:
                    ch, fg = '0', (90, 176, 255)
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
                    if o:
                        ch, fg = o.ch, o.fg
                        if not o.is_npc:
                            if o.elite or o.is_boss:
                                bg = mix(bg, o.fg, .25)
                            if o.hold > 0:
                                fg = (159, 216, 255)
                            if t - app.hit_times.get(o.id, -9) < .13:
                                fg, bg = (255, 255, 255), (120, 30, 20)
                    if mx == p.x and my == p.y:
                        ch, fg = '@', ((184, 240, 138) if p.poison else (255, 246, 220))
                else:
                    fg = scale(fg, .42 if m.kind == 'over' else .3)
                if night and m.kind in ('over', 'town'):
                    fg = mix(fg, (40, 50, 110), .35)
                    bg = scale(bg, .7)
                cv.put(vx, vy, ch, fg, bg)
        if m.kind == 'over':
            self.draw_overworld_extras(cv, ox, oy)
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
                for j, ch in enumerate(label):
                    if 0 <= lx + j < MAP_W:
                        cv.put(lx + j, vy, ch, (196, 160, 80))
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
                bg = (70, 20, 16) if wd.hostile else (20, 30, 50) if wd.kind == 'patrol' else BG
                cv.put(vx, vy, wd.ch, wd.fg, bg)

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
        cv.text(x, 0, p.name, GOLD, PANEL, maxw=PW - 8)
        cv.text_right(x + PW - 1, 0, f'Day {g.day}', DIM, PANEL)
        hr = TW.hour(g)
        cv.text(x, 1, f"Level {p.lvl} · {'hardcore' if p.hardcore else 'softcore'}", DIM, PANEL)
        cv.text_right(x + PW - 1, 1, f"{hr:02d}:00 {'○' if TW.is_night(g) else '☼'}", (150, 160, 220) if TW.is_night(g) else GOLD, PANEL)
        self.orb(cv, x, 2, p.life / max(1, s['max_life']), BLOOD, (100, 160, 60) if p.poison else None)
        self.orb(cv, x + PW - 9, 2, p.mana / max(1, s['max_mana']), MANA)
        cv.text_center(x + 4, 7, f"{max(0, p.life)}/{s['max_life']}", FG, PANEL)
        cv.text_center(x + PW - 5, 7, f"{p.mana}/{s['max_mana']}", FG, PANEL)
        cv.text_center(x + PW // 2, 3, 'LIFE' if not p.poison else 'POISON', BAD if p.poison else DIM, PANEL)
        cv.text_center(x + PW // 2, 5, 'MANA', DIM, PANEL)
        prev = E.xp_for(p.lvl - 1) if p.lvl > 1 else 0
        frac = (p.xp - prev) / max(1, E.xp_for(p.lvl) - prev)
        cv.text(x, 8, 'XP', DIM, PANEL)
        bw = PW - 3
        filled = int(bw * max(0, min(1, frac)))
        for i in range(bw):
            cv.put(x + 3 + i, 8, '█' if i < filled else '░', GOLD if i < filled else LINE, PANEL)
        cv.text(x, 9, 'SKILLS', DIM, PANEL)
        cv.text_right(x + PW - 1, 9, 'Z: change', scale(DIM, .8), PANEL)
        for i, sid in enumerate(p.bar):
            y = 10 + i
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
        cv.text(x, 17, 'Q', GOLD, PANEL)
        cv.text(x + 2, 17, f'Health x{hp}', D.POTIONS['hp']['col'] if hp else DIM, PANEL)
        cv.text(x + 14, 17, 'W', GOLD, PANEL)
        cv.text(x + 16, 17, f'Mana x{mp}', D.POTIONS['mp']['col'] if mp else DIM, PANEL)
        cv.text(x, 18, 'P', GOLD, PANEL)
        cv.text(x + 2, 18, f'Portal x{tp}', FG if tp else DIM, PANEL)
        cap, used = ECO.cargo_capacity(p), ECO.cargo_weight(p)
        cv.text_right(x + PW - 1, 18, f'Cargo {used}/{cap}', BAD if used >= cap else FG if used else DIM, PANEL)
        rows = [('Damage', f"{s['dmg'][0]}-{s['dmg'][1]}" + (' (bow)' if s['ranged'] else '')), ('Accuracy', str(s['ar'])),
                ('Defense', str(s['def']) + (f" -{s['dr']}%" if s['dr'] else '')),
                ('Critical', f"{s['crit']}%" + (f"  leech {s['leech']}%" if s['leech'] else '')), ('Gold', str(p.gold))]
        for i, (a, b) in enumerate(rows):
            cv.text(x, 20 + i, a, DIM, PANEL)
            cv.text_right(x + PW - 1, 20 + i, b, GOLD if a == 'Gold' else FG, PANEL)
        if p.stat_pts:
            cv.text(x, 25, f'C: {p.stat_pts} attribute points', GOLD, PANEL, maxw=PW)
        elif p.buffs:
            cv.text(x, 25, ', '.join(f'{b[3]} {b[2]}' for b in p.buffs), GOOD, PANEL, maxw=PW)
        self.draw_target(cv, x, 26)
        cv.text(x, H - 1, '? help · v beasts · e jobs', scale(DIM, .8), PANEL, maxw=PW)

    def orb(self, cv, x, y, frac, col, alt=None):
        frac = max(0.0, min(1.0, frac))
        level = frac * 5
        dark = (30, 22, 18)
        for r, row in enumerate(ORB_MASK):
            from_bottom = 4 - r
            for c, ch in enumerate(row):
                if ch != '#':
                    continue
                fill = level - from_bottom
                fc = alt or col
                if fill >= 1:
                    cv.put(x + c, y + r, ' ', FG, fc)
                elif fill > .5:
                    cv.put(x + c, y + r, '▄', fc, mix(dark, fc, .35))
                elif fill > 0:
                    cv.put(x + c, y + r, '▄', mix(dark, fc, .6), dark)
                else:
                    cv.put(x + c, y + r, ' ', FG, dark)

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
                    cv.text(x, y, f"{st.name} ({'city' if st.is_city else 'village'})", D.FACTIONS[st.faction]['fg'], PANEL, maxw=PW)
                    cv.text(x, y + 1, 'Makes: ' + ', '.join(D.GOODS[k]['name'] for k in st.produce), DIM, PANEL, maxw=PW)
                    cv.text(x, y + 2, 'Wants: ' + ', '.join(D.GOODS[k]['name'] for k in st.demand), DIM, PANEL, maxw=PW)
                elif EV.poi_at(g, mx, my) and EV.poi_at(g, mx, my).found:
                    poi = EV.poi_at(g, mx, my)
                    cv.text(x, y, poi.name, poi.glyph[1], PANEL, maxw=PW)
                    if poi.kind == 'ruin':
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
        elif tok in ('enter', 'np_enter'):
            self.act(lambda: g.use_stairs('auto'))
        elif tok == 'x':
            g.log_mark = len(g.log)
            g.explore()
        elif tok == 't':
            if g.map.kind in ('over', 'town'):
                app.push(TravelScreen(app))
            else:
                g.log_mark = len(g.log)
                g.msg('You can only travel from the open land or from a town.')
        elif tok == 'm':
            app.push(WorldMapScreen(app))
        elif tok in ('e', 'tab'):
            app.push(JournalScreen(app))
        elif tok == 'i':
            app.push(InventoryScreen(app))
        elif tok == 'd':
            app.push(InventoryScreen(app, drop=True))
        elif tok == 'c':
            app.push(CharacterScreen(app))
        elif tok == 'R':
            g.log_mark = len(g.log)
            g.rest()
        elif tok in ('?', 'f1'):
            app.push(HelpScreen(app))
        elif tok in ('v', 'f2'):
            app.push(BestiaryScreen(app))
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
    title = ''

    def box(self, cv, w, h, title=None):
        x, y = (W - w) // 2, (H - h) // 2
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
    cv.text(x, yy, f'Value {it.value()} gold', DIM, PANEL)
    yy += 1
    if it.k == 'gear' and not g.is_equipped(it):
        cur = g.eq_item(it.slot)
        yy += 1
        if cur:
            cv.text(x, yy, 'Equipped now:', DIM, PANEL)
            cv.text(x, yy + 1, cur.name, cur.color(), PANEL, maxw=w)
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
    BAG_Y, BAG_ROWS = 11, 17

    def bag_scroll(self):
        i = self.sel - 5
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
        cv.text(x + 2, y + 1, f'{len(g.player.inv)}/24 slots · {g.player.gold} gold', DIM, PANEL)
        cv.text(x + 2, y + 3, 'EQUIPPED', DIM, PANEL)
        cv.text(x + 2, y + 10, 'BACKPACK', DIM, PANEL)
        sc = self.bag_scroll()
        nbag = len(g.backpack())
        if sc > 0:
            cv.text(x + 50, y + 10, '▲', GOLD, PANEL)
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
                    cv.text(x + 12, yy, it.name, it.color(), bg, maxw=42)
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
                already = self.sel == 5 + i
                self.sel = 5 + i
                if self.drop_mode or already:
                    self.use()

    def on_click(self, x, y, button):
        bx, by = (W - self.BOX_W) // 2, (H - self.BOX_H) // 2
        sc = getattr(self, 'scroll', 0)
        if bx + 2 <= x < bx + 56:
            if by + 4 <= y < by + 9:
                self.sel = y - by - 4
            elif by + self.BAG_Y <= y < by + self.BAG_Y + self.BAG_ROWS and y - by - self.BAG_Y + sc < len(self.game.backpack()):
                new = 5 + y - by - self.BAG_Y + sc
                if new == self.sel:
                    self.use()
                self.sel = new


class CharacterScreen(Modal):
    def render(self, cv):
        g = self.game
        p, s = g.player, g.stats()
        x, y = self.box(cv, 96, 30, f"{p.name} · level {p.lvl}")
        cv.text(x + 2, y + 1, f'{p.stat_pts} attribute points to spend · {p.deaths} deaths · {"hardcore" if p.hardcore else "softcore"}',
                GOLD if p.stat_pts else DIM, PANEL)
        cv.text(x + 2, y + 3, 'ATTRIBUTES', DIM, PANEL)
        helps = {'str': '+1% melee damage (swords, axes)', 'dex': 'accuracy, defense, +1% dagger and bow damage',
                 'vit': '+2 life', 'ene': '+2 mana, +1 spell damage per 5'}
        for i, (st, nm) in enumerate((('str', 'Strength'), ('dex', 'Dexterity'), ('vit', 'Vitality'), ('ene', 'Energy'))):
            yy = y + 4 + i
            cv.text(x + 2, yy, f'{i + 1}', GOLD if p.stat_pts else DIM, PANEL)
            cv.text(x + 4, yy, nm, FG, PANEL)
            cv.text_right(x + 18, yy, str(s[st]), FG, PANEL)
            cv.text(x + 20, yy, helps[st], DIM, PANEL)
        cv.text(x + 2, y + 9, 'TOTALS', DIM, PANEL)
        tots = [('Life', f"{p.life}/{s['max_life']}"), ('Mana', f"{p.mana}/{s['max_mana']}"), ('Damage', f"{s['dmg'][0]}-{s['dmg'][1]}"),
                ('Accuracy', str(s['ar'])), ('Defense', str(s['def'])), ('Critical', f"{s['crit']}%"),
                ('Life leech', f"{s['leech']}%"), ('Experience', f'{p.xp}/{E.xp_for(p.lvl)}')]
        for i, (a, b) in enumerate(tots):
            cv.text(x + 2, y + 10 + i, a, DIM, PANEL)
            cv.text_right(x + 30, y + 10 + i, b, FG, PANEL)
        for yy in range(y + 3, y + 28):
            cv.put(x + 33, yy, '│', LINE, PANEL)
        cv.text(x + 35, y + 3, 'DISCIPLINES', DIM, PANEL)
        cv.text(x + 62, y + 3, 'grow by use', scale(DIM, .8), PANEL)
        for i, line in enumerate(SK.DISC_ORDER):
            yy = y + 4 + i * 2
            r, prog = p.disc[line]
            d = SK.DISCIPLINES[line]
            cv.text(x + 35, yy, d['name'], FG if r else DIM, PANEL)
            cv.text_right(x + 59, yy, str(r), GOLD if r else DIM, PANEL)
            need = SK.need_for(r)
            bw = 16
            fill = int(bw * prog / need)
            for j in range(bw):
                cv.put(x + 61 + j, yy, '█' if j < fill else '░', INFO if j < fill else LINE, PANEL)
            nxt = next((k for k in SK.by_line(line) if k.unlock > r), None)
            known = sum(1 for k in SK.by_line(line) if k.id in p.known)
            cv.text(x + 35, yy + 1, f'{known}/5 skills' + (f' · next: {nxt.name} at {nxt.unlock}' if nxt else ' · mastered'),
                    scale(DIM, .85), PANEL, maxw=58)
        cv.text_center(W // 2, y + 29, ' 1-4: add an attribute point · Z: skills · Esc: close ', DIM, PANEL)

    def on_key(self, tok, shift):
        g = self.game
        if tok == 'esc':
            self.app.pop()
        elif tok in ('1', '2', '3', '4'):
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
        cv.text(x + 2, y + 1, 'Your bar' + ('' if in_town else ' (you can only change it in a town or stronghold)'),
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
        cv.text(x + 54, y + 20, 'Locked skills unlock as their discipline', DIM, PANEL)
        cv.text(x + 54, y + 21, 'rises. Use a discipline to raise it.', DIM, PANEL)
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
    SUPPLIES = [('potion', 'hp'), ('potion', 'mp'), ('scroll', 'tp')]

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
        cv.text(x + 82, y + 1, 'Your gold:', DIM, PANEL)
        cv.text(x + 93, y + 1, str(g.player.gold), GOLD, PANEL)
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
                cv.text_right(lx + 29, yy, str(price), GOLD if (pane == 1 or g.player.gold >= price) else BAD, bg)
            if not rows:
                cv.text(lx, y + 4, 'Nothing to sell.' if pane else 'Sold out.', DIM, PANEL)
        for yy in range(y + 1, y + 29):
            cv.put(x + 65, yy, '│', LINE, PANEL)
        cur = lists[self.pane]
        if cur:
            item_detail(cv, g, cur[self.sel[self.pane]], x + 67, y + 3, 35, 22)
        cv.text_center(W // 2, y + 29, ' Tab: switch buy/sell · letter or arrows: select · Enter: buy or sell · Esc: leave ', DIM, PANEL)

    def activate(self):
        g = self.game
        g.log_mark = len(g.log)
        i = self.sel[self.pane]
        if self.pane == 0:
            if i < 3:
                g.buy_supply(i)
            else:
                g.buy_gear(i - 3, self.key)
        else:
            rows = self.sell_rows()
            if i < len(rows):
                g.sell(rows[i])

    def on_key(self, tok, shift):
        rows = self.buy_rows() if self.pane == 0 else self.sell_rows()
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
                out.append(('s', st.id, st.name, 'city' if st.is_city else 'village', st.x, st.y))
        for d in g.world.dungeons.values():
            if g.known_dungeon(d):
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
            g.travel_to(k, ref)


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
            ('arrows / numpad / hjkl yubn', 'Move. Walk into a monster to attack, into a person to talk.'),
            ('Shift + direction  HJKL..', 'Run until something interesting happens'),
            ('1 2 3 4 5 6', 'Use the skill in that slot (aims at the nearest enemy)'),
            ('F', 'Shoot the nearest enemy (needs a bow)'),
            ('Z', 'Skills: choose your six (only in a town or stronghold)'),
            ('Q   W', 'Drink a health or mana potion'),
            ('P', 'Read a Town Portal scroll. Step into the blue 0 to go back.'),
            ('G  ,', 'Pick up items. Gold, orbs and magic items are picked up for you.'),
            ('>  <  Enter', 'Enter a town, dungeon, ruin or stronghold · use stairs'),
            ('X', 'Auto-explore a dungeon until enemies appear'),
            ('T', 'Travel to a known town or dungeon (stops when danger shows up)'),
            ('R   S   5   .', 'Rest until healed · wait one turn'),
            ('I   D   C', 'Inventory · drop items · character sheet and attributes'),
            ('E  Tab', 'Journal: jobs, cargo, factions and news'),
            ('M', 'Map of the realm (F on the map shows faction lands)'),
            ('V  F2', 'Bestiary: the creatures you have met'),
            ('?  F1', 'This help'),
            ('F11  Alt+Enter', 'Toggle fullscreen'),
            ('mouse', 'Hover to inspect, click to step toward a spot'),
            ('Esc', 'Close a window · save and quit'),
        ]),
        ('The world', [
            ('Roads', 'Roads are patrolled and fairly safe. The further you stray, the worse it gets.'),
            ('Danger', 'Hover over the land to see its danger. Night brings the dead and bigger packs.'),
            ('Π ruin', 'An old ruin with a way down. Smaller than a dungeon, but loot is loot.'),
            ('† shrine', 'Pray for a blessing. An offering makes it last longer.'),
            ('∆ camp', 'A bandit camp. Kill them all and the strongbox is yours.'),
            ('Ψ stones', 'Standing stones. Touch them to learn from old memories.'),
            ('¤ wagon', 'An abandoned wagon. Loot, or a trap.'),
            ('Events', 'On the road things happen: wounded travellers, peddlers, tolls, storms...'),
            ('@ travellers', 'Walk into a traveller to talk. Some have a job for you, and wait for'),
            ('', 'you afterwards at the inn of the town they were going to (see the journal).'),
            ('Towns', 'Trader: goods · innkeeper: jobs · outfitter: gear · temple: healing'),
            ('', 'stablemaster: mules and carts · castellan (in strongholds): war jobs'),
            ('Factions', 'Work for a faction to gain its favour; hurt them and their gates close.'),
            ('Bestiary', 'Every kill teaches you. Higher knowledge: more damage against that kind,'),
            ('', 'and they hit you less often.'),
            ('Skills', 'You have no class. Use a discipline and it grows, unlocking new skills.'),
            ('Death', 'Hardcore: final. Softcore: you wake in a temple; your pack stays with your body.'),
            ('Rarity', 'normal · magic (blue) · rare (yellow) · unique (gold)'),
        ]),
    ]

    def __init__(self, app):
        super().__init__(app)
        self.page = 0

    def render(self, cv):
        name, rows = self.PAGES[self.page]
        x, y = self.box(cv, 104, 28, f'Help: {name} ({self.page + 1}/{len(self.PAGES)})')
        for i, (k, d) in enumerate(rows):
            cv.text(x + 3, y + 2 + i, k, GOLD, PANEL, maxw=27)
            cv.text(x + 31, y + 2 + i, d, FG, PANEL, maxw=71)
        cv.text_center(W // 2, y + 27, ' Left/Right or Space: next page · Esc: close ', DIM, PANEL)

    def on_key(self, tok, shift):
        if tok in ('right', 'space', 'np6', 'tab', 'l', 'enter', 'pagedown'):
            self.page = (self.page + 1) % len(self.PAGES)
        elif tok in ('left', 'np4', 'h', 'pageup'):
            self.page = (self.page - 1) % len(self.PAGES)
        else:
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
    """A short opening for a new game."""
    PAGES = [
        ('The Cursed Vale',
         'For three winters the vale has known no peace. The dead do not stay in their graves, wolves come down from '
         'the hills in packs no hunter has ever seen, and the old roads are the only places left where honest folk '
         'still dare to walk.\n\n'
         'The cause has a name: Morvenna the Undying, a sorceress who would not die, sleeping and scheming in a crypt '
         'somewhere in the wilds. Her curse seeps into the land a little further every year.'),
        ('A land at war with itself',
         'As if that were not enough, the lords of the vale fight each other. The Crown holds the heartland, the '
         'Merchant League buys what it cannot conquer, the Circle guards its old groves, and the Black Hand takes '
         'whatever is left on the roads. Castles and forts change hands. Patrols keep the roads, but beyond them '
         'the land grows wilder and more dangerous with every step.\n\n'
         'Ruins, shrines and hidden camps wait out there for those brave enough to leave the road.'),
        ('{name}',
         'You arrive in Thornfield, a small village at the heart of the vale, with a sword, a padded coat and a few '
         'coins. You are nobody yet. What you become is up to you: warrior, archer, mage, merchant, sellsword, '
         'or all of these at once.\n\n'
         'Speak with Elder Berend, find work on the inn board, trade goods between towns, talk to the travellers you '
         'meet, and grow strong enough to face what waits in the crypt.\n\n'
         'Press ? at any time for help.'),
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
        rows = [('Level', p.lvl), ('Experience', p.xp), ('Turns', g.turn), ('Kills', g.kills), ('Gold', p.gold)]
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
    title = 'The curse is broken'

    def render(self, cv):
        g = self.game
        p = g.player
        x, y = self.box(cv, 64, 15)
        cv.wrap(x + 3, y + 2, 58, f"{p.name} has destroyed Morvenna the Undying. Thornfield will sing of this for generations.", FG, PANEL)
        rows = [('Level', p.lvl), ('Turns', g.turn), ('Kills', g.kills), ('Gold', p.gold)]
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
        cv.text(x + 2, y + 1, f'Gold {p.gold}', GOLD, PANEL)
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
            cv.text(x + 22, yy, str(ECO.buy_price(s, gk)), FG, bg)
            cv.text(x + 29, yy, str(ECO.sell_price(s, gk)), FG, bg)
            sw = _stock_word(s, gk)
            cv.text(x + 36, yy, sw, {'none': BAD, 'scarce': BAD, 'some': FG, 'plenty': GOOD}[sw], bg)
            have = p.cargo.get(gk, 0)
            cv.text(x + 45, yy, str(have) if have else '-', GOLD if have else DIM, bg)
            if have and gk in p.cost_basis:
                cv.text(x + 53, yy, f'{p.cost_basis[gk]:.0f}', DIM, bg)
            best = ECO.best_known_sale(g, gk, s.id)
            if best:
                v, bsid, day = best
                age = g.day - day
                col = GOOD if v > ECO.buy_price(s, gk) else DIM
                cv.text(x + 60, yy, f"{v} in {g.world.settlements[bsid].name} ({'today' if age == 0 else f'{age}d ago'})", col, bg, maxw=42)
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
            cv.text_right(x + 55, yy, f'{mi.reward}g', GOLD, bg)
        for yy in range(y + 1, y + self.BOX_H - 1):
            cv.put(x + 58, yy, '│', LINE, PANEL)
        if offers:
            mi = offers[self.sel]
            cv.text(x + 60, y + 3, mi.title, GOLD, PANEL, maxw=38)
            n = cv.wrap(x + 60, y + 5, 38, mi.desc, FG, PANEL, 10)
            yy = y + 6 + n
            cv.text(x + 60, yy, f'Reward: {mi.reward} gold', GOLD, PANEL)
            local_rep = src.rep if not self.hold else max(0, frep)
            if local_rep > 0:
                cv.text(x + 60, yy + 1, f'+{round(mi.reward * min(local_rep, 100) / 200)} reputation bonus', GOOD, PANEL)
            if mi.deadline:
                cv.text(x + 60, yy + 2, f'Deadline: day {mi.deadline} (today is {g.day})', DIM, PANEL)
            cv.text(x + 60, yy + 3, self.KINDS[mi.kind], INFO, PANEL)
            if mi.faction:
                cv.text(x + 60, yy + 4, f"Reputation with the {D.FACTIONS[mi.faction]['short']}: +{mi.rep if self.hold else 2}", GOOD, PANEL)
        cv.text_center(W // 2, y + self.BOX_H - 1, ' letter or ↑↓ select · Enter accept · Esc leave ', DIM, PANEL)

    def on_key(self, tok, shift):
        g = self.game
        s = self.source
        if tok == 'esc':
            self.app.pop()
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
        x, y = self.box(cv, 100, 28, 'Journal')
        here = g.here
        ox, oy = (here.x, here.y) if here else (p.x, p.y) if g.cur == 'over' else g.over_pos
        cv.text(x + 2, y + 1, 'ACTIVE JOBS', DIM, PANEL)
        jobs = MS.active(g)
        yy = y + 2
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
            cv.text_right(x + 97, yy, f'{mi.reward}g', GOLD, PANEL)
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
        yy += 1
        for f in D.FACTION_ORDER:
            fd = D.FACTIONS[f]
            r = g.player.rep[f] if f != 'cult' else -100
            holds = sum(1 for h in g.world.holds if h.faction == f)
            regs = sum(1 for rg in g.world.regions if rg.faction == f)
            cv.text(x + 4, yy, fd['name'], fd['fg'], PANEL)
            cv.text(x + 32, yy, f'{WAR.standing(r)} ({r})', BAD if WAR.is_hostile(g, f) else GOOD if r >= 10 else FG, PANEL)
            cv.text(x + 52, yy, f'{regs} regions, {holds} strongholds', DIM, PANEL)
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
    """The whole overworld, each character covering 2x4 cells."""
    show_factions = False
    PRIORITY = {D.CITY: 9, D.TOWN: 8, D.ENTR: 7, D.ROAD: 6, D.WATER: 5, D.MOUNTAIN: 4, D.HILLS: 3, D.SWAMP: 3, D.FOREST: 2, D.SAND: 2, D.GRASS: 1}

    def render(self, cv):
        g = self.game
        om = g.maps['over']
        w = g.world
        x, y = self.box(cv, 84, 28, 'Map of the realm')
        bx, by = x + 2, y + 2
        p = g.player
        here = g.here
        px, py = (here.x, here.y) if here else (p.x, p.y) if g.cur == 'over' else g.over_pos
        for cy in range(om.h // 4 + 1):
            for cx in range(om.w // 2):
                best, bt = 0, None
                for yy in range(cy * 4, min(om.h, cy * 4 + 4)):
                    for xx in range(cx * 2, cx * 2 + 2):
                        i = yy * om.w + xx
                        if not om.seen[i]:
                            continue
                        t = om.t[i]
                        pr = self.PRIORITY.get(t, 0)
                        if pr > best:
                            best, bt = pr, t
                if bt is None:
                    continue
                td = D.TILES[bt]
                bg = td.bg or PANEL
                if WorldMapScreen.show_factions:
                    rf = w.regions[w.region_of[min(om.h - 1, cy * 4 + 1) * om.w + cx * 2]].faction
                    bg = mix(PANEL, D.FACTIONS[rf]['fg'], .28)
                cv.put(bx + cx, by + cy, td.ch, td.fg, bg)
        taken = set()
        for st in w.settlements:
            taken.add((bx + st.x // 2, by + st.y // 4))
        for st in sorted(w.settlements, key=lambda q: not q.is_city):
            if not g.known_settlement(st):
                continue
            lx, ly = bx + st.x // 2 + 1, by + st.y // 4
            name = st.name
            if lx + len(name) > x + 83:
                lx = bx + st.x // 2 - len(name)
            cells = {(lx + j, ly) for j in range(len(name) + 1)}
            if lx < x + 1 or cells & taken:
                continue
            taken |= cells
            cv.text(lx, ly, name, (230, 196, 120) if st.is_city else (176, 146, 80), PANEL)
        for mi in MS.active(g):
            (tx, ty), _ = MS.target_pos(g, mi)
            cv.put_bg(bx + tx // 2, by + ty // 4, (110, 80, 16))
        cv.put(bx + px // 2, by + py // 4, '@', (255, 246, 220), (150, 40, 28))
        for poi in w.pois:
            if poi.found:
                ch, col = poi.glyph
                cv.put(bx + poi.x // 2, by + poi.y // 4, ch, col if poi.ready_day < 10 ** 9 else scale(col, .5), PANEL)
        for hd in w.holds:
            if om.seen[hd.y * om.w + hd.x]:
                cv.put(bx + hd.x // 2, by + hd.y // 4, 'Ω' if hd.kind == 'castle' else '╬', D.FACTIONS[hd.faction]['fg'], PANEL)
        if WorldMapScreen.show_factions:
            lx = x + 2
            for f in D.FACTION_ORDER:
                cv.text(lx, y + 26, '■ ' + D.FACTIONS[f]['short'], D.FACTIONS[f]['fg'], PANEL)
                lx += len(D.FACTIONS[f]['short']) + 4
        else:
            cv.text(x + 2, y + 26, '⌂ village ■ city Ω castle ╬ fort > dungeon Π ruin † shrine ∆ camp Ψ stones ¤ wagon', DIM, PANEL)
        cv.text_center(W // 2, y + 27, ' F: show or hide factions · any other key: close ', DIM, PANEL)

    def on_key(self, tok, shift):
        if tok == 'f':
            WorldMapScreen.show_factions = not WorldMapScreen.show_factions
            return
        self.app.pop()


class StablesScreen(Modal):
    def render(self, cv):
        g = self.game
        p = g.player
        x, y = self.box(cv, 64, 12, 'Stables')
        cv.text(x + 2, y + 1, f'"Need something to carry your goods?"   Gold {p.gold}', DIM, PANEL)
        for i, k in enumerate(('mule', 'cart')):
            mt = D.MOUNTS[k]
            yy = y + 3 + i * 3
            owned = k in p.mounts
            cv.text(x + 2, yy, LETTERS[i], GOLD, PANEL)
            cv.text(x + 4, yy, mt['name'], FG if not owned else DIM, PANEL)
            cv.text_right(x + 60, yy, 'owned' if owned else f"{mt['price']} gold", DIM if owned else GOLD, PANEL)
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
