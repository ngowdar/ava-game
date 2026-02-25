# screens/particle_playground.py — Particle physics playground for toddlers

import math
import random
import pygame
from config import WIDTH, HEIGHT, WHITE, BLACK
from ui import draw_back_button, get_font, hsv_to_rgb, ScrollToolbar

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_PARTICLES = 2500
TOOLBAR_H = 80
GRAVITY = 400.0          # px/s^2
BOUNCE_DAMPING = 0.6     # energy kept on bounce
PARTICLE_LIFETIME = 4.0  # seconds
BG_COLOR = (10, 10, 18)

# Mode identifiers
MODE_FOUNTAIN = 0
MODE_RAIN = 1
MODE_SWIRL = 2
MODE_EXPLOSION = 3

MODE_LABELS = ["Fountain", "Rain", "Swirl", "Boom"]
MODE_COLORS = [(80, 180, 255), (100, 200, 120), (200, 130, 255), (255, 120, 80)]

# Palette identifiers
PAL_RAINBOW = 0
PAL_FIRE = 1
PAL_ICE = 2
PAL_NEON = 3

PAL_PREVIEW = [
    [(255, 0, 0), (255, 200, 0), (0, 255, 0), (0, 100, 255)],   # rainbow
    [(255, 60, 0), (255, 140, 0), (255, 220, 50)],                # fire
    [(100, 180, 255), (0, 255, 255), (220, 240, 255)],            # ice
    [(255, 50, 200), (50, 255, 100), (180, 50, 255)],             # neon
]

# ---------------------------------------------------------------------------
# Particle storage — struct-of-arrays for cache-friendly iteration
# ---------------------------------------------------------------------------

class ParticlePool:
    """Flat list-of-lists particle pool.  No per-particle objects or dicts."""

    __slots__ = ("cap", "count", "x", "y", "vx", "vy",
                 "r", "g", "b", "life", "max_life", "size")

    def __init__(self, capacity):
        self.cap = capacity
        self.count = 0
        self.x = [0.0] * capacity
        self.y = [0.0] * capacity
        self.vx = [0.0] * capacity
        self.vy = [0.0] * capacity
        self.r = [255] * capacity
        self.g = [255] * capacity
        self.b = [255] * capacity
        self.life = [0.0] * capacity
        self.max_life = [1.0] * capacity
        self.size = [2] * capacity

    def clear(self):
        self.count = 0

    def emit(self, px, py, pvx, pvy, pr, pg, pb, plife, psize):
        """Add one particle.  Returns False if pool is full."""
        i = self.count
        if i >= self.cap:
            return False
        self.x[i] = px
        self.y[i] = py
        self.vx[i] = pvx
        self.vy[i] = pvy
        self.r[i] = pr
        self.g[i] = pg
        self.b[i] = pb
        self.life[i] = plife
        self.max_life[i] = plife
        self.size[i] = psize
        self.count += 1
        return True

    # Inline-heavy update — avoids attribute lookups in the hot loop
    def update(self, dt, gravity):
        n = self.count
        x = self.x; y = self.y
        vx = self.vx; vy = self.vy
        life = self.life
        size = self.size
        grav_dt = gravity * dt
        w = WIDTH - 1
        h = HEIGHT - 1
        damp = BOUNCE_DAMPING

        i = 0
        while i < n:
            life[i] -= dt
            if life[i] <= 0.0:
                # Swap-remove
                n -= 1
                x[i] = x[n]; y[i] = y[n]
                vx[i] = vx[n]; vy[i] = vy[n]
                self.r[i] = self.r[n]; self.g[i] = self.g[n]; self.b[i] = self.b[n]
                life[i] = life[n]
                self.max_life[i] = self.max_life[n]
                size[i] = size[n]
                continue

            vy[i] += grav_dt
            x[i] += vx[i] * dt
            y[i] += vy[i] * dt

            # Bounce off walls
            xi = x[i]
            yi = y[i]
            if xi < 0:
                x[i] = 0; vx[i] = -vx[i] * damp
            elif xi > w:
                x[i] = w; vx[i] = -vx[i] * damp
            if yi > h:
                y[i] = h; vy[i] = -vy[i] * damp
            elif yi < TOOLBAR_H:
                y[i] = TOOLBAR_H; vy[i] = -vy[i] * damp

            i += 1
        self.count = n

    def draw(self, surface):
        """Draw all particles as tiny filled rects for speed."""
        n = self.count
        x = self.x; y = self.y
        r = self.r; g = self.g; b = self.b
        size = self.size
        life = self.life; max_life = self.max_life
        fill = surface.fill

        for i in range(n):
            # Fade alpha via brightness reduction in last 30% of life
            frac = life[i] / max_life[i] if max_life[i] > 0 else 1.0
            if frac < 0.3:
                f = frac / 0.3
                cr = int(r[i] * f)
                cg = int(g[i] * f)
                cb = int(b[i] * f)
            else:
                cr = r[i]; cg = g[i]; cb = b[i]
            s = size[i]
            fill((cr, cg, cb), (int(x[i]), int(y[i]), s, s))

# ---------------------------------------------------------------------------
# Color palette helpers
# ---------------------------------------------------------------------------

def _color_rainbow(hue_base):
    h = (hue_base + random.random() * 60) % 360
    return hsv_to_rgb(h, 1.0, 1.0)

def _color_fire(_):
    h = random.uniform(0, 50)
    return hsv_to_rgb(h, 1.0, random.uniform(0.8, 1.0))

def _color_ice(_):
    h = random.uniform(180, 220)
    s = random.uniform(0.3, 0.9)
    return hsv_to_rgb(h, s, 1.0)

def _color_neon(_):
    choice = random.randint(0, 2)
    if choice == 0:
        return (255, random.randint(30, 80), random.randint(180, 240))
    elif choice == 1:
        return (random.randint(30, 80), 255, random.randint(80, 140))
    else:
        return (random.randint(150, 200), random.randint(30, 80), 255)

_PALETTE_FNS = [_color_rainbow, _color_fire, _color_ice, _color_neon]

# ---------------------------------------------------------------------------
# Screen class
# ---------------------------------------------------------------------------

class ParticlePlaygroundScreen:

    def __init__(self, app):
        self.app = app
        self.pool = ParticlePool(MAX_PARTICLES)
        self.mode = MODE_FOUNTAIN
        self.palette = PAL_RAINBOW
        self.hue = 0.0
        self.touching = False
        self.touch_x = WIDTH // 2
        self.touch_y = HEIGHT // 2
        self.back_rect = None
        self._build_toolbar()

        # Rain state
        self._rain_timer = 0.0

    # ---- Toolbar layout ----

    def _build_toolbar(self):
        """Pre-compute button rects for mode and palette selectors."""
        # Scrollable mode buttons — bigger and easier to tap
        bw, bh = 120, 56
        gap = 8
        start_x = 110
        # Total width: 4 modes + 4 palette dots
        # Mode buttons + palette dots in one scrollable strip
        self.toolbar = ScrollToolbar(
            left_x=start_x, y=(TOOLBAR_H - bh) // 2, height=bh,
            btn_width=bw, btn_gap=gap, btn_count=4
        )

        # Palette dots — placed after mode buttons (also scroll)
        self.pal_rects = []
        dot_r = 20
        dot_gap = 10
        # Position palette dots after the last mode button
        mode_end = start_x + 4 * (bw + gap)
        px = mode_end + 8
        cy = TOOLBAR_H // 2
        for i in range(4):
            cx = px + i * (dot_r * 2 + dot_gap)
            self.pal_rects.append(pygame.Rect(cx - dot_r, cy - dot_r, dot_r * 2, dot_r * 2))

    # ---- Screen interface ----

    def on_enter(self):
        self.pool.clear()
        self.hue = 0.0
        self.touching = False
        self._rain_timer = 0.0

    def handle_event(self, event):
        # Toolbar scroll handling
        if self.toolbar.handle_event(event):
            if event.type == pygame.MOUSEBUTTONUP:
                idx = self.toolbar.get_btn_at(event.pos)
                if idx >= 0:
                    self.mode = idx
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            # Back button
            if self.back_rect and self.back_rect.collidepoint(mx, my):
                self.app.go_back()
                return

            # Mode buttons (tap without drag)
            idx = self.toolbar.get_btn_at((mx, my))
            if idx >= 0:
                self.mode = idx
                return

            # Palette buttons
            for i, r in enumerate(self.pal_rects):
                if r.collidepoint(mx, my):
                    self.palette = i
                    return

            # Touch in play area
            if my > TOOLBAR_H:
                self.touching = True
                self.touch_x = mx
                self.touch_y = my
                if self.mode == MODE_EXPLOSION:
                    self._emit_explosion(mx, my)

        elif event.type == pygame.MOUSEMOTION:
            if self.touching:
                mx, my = event.pos
                self.touch_x = mx
                self.touch_y = max(my, TOOLBAR_H)

        elif event.type == pygame.MOUSEBUTTONUP:
            self.touching = False

    def update(self, dt):
        self.hue = (self.hue + dt * 90) % 360  # full rainbow every 4s

        # Emit particles based on mode
        if self.mode == MODE_FOUNTAIN and self.touching:
            self._emit_fountain(dt)
        elif self.mode == MODE_RAIN:
            self._emit_rain(dt)
        elif self.mode == MODE_SWIRL and self.touching:
            self._emit_swirl(dt)
        # Explosion emits on tap, not continuously

        self.toolbar.update(dt)
        self.pool.update(dt, GRAVITY if self.mode != MODE_SWIRL else GRAVITY * 0.15)

        # Swirl: apply attraction toward touch point
        if self.mode == MODE_SWIRL and self.touching:
            self._apply_swirl_forces(dt)

        # Rain: apply wind from touch point
        if self.mode == MODE_RAIN and self.touching:
            self._apply_wind(dt)

    def draw(self, surface):
        surface.fill(BG_COLOR)

        # Particles
        self.pool.draw(surface)

        # Toolbar background
        pygame.draw.rect(surface, (20, 20, 30), (0, 0, WIDTH, TOOLBAR_H))
        pygame.draw.line(surface, (50, 50, 70), (0, TOOLBAR_H), (WIDTH, TOOLBAR_H), 2)

        # Mode buttons (scrollable)
        font = get_font(22)
        btn_rects = self.toolbar.get_btn_rects()
        for i, r in enumerate(btn_rects):
            if r.right < self.toolbar.left_x or r.left > WIDTH:
                continue
            selected = (i == self.mode)
            col = MODE_COLORS[i] if selected else (60, 60, 70)
            pygame.draw.rect(surface, col, r, border_radius=10)
            if selected:
                pygame.draw.rect(surface, WHITE, r, width=2, border_radius=10)
            txt = font.render(MODE_LABELS[i], True, WHITE if selected else (150, 150, 150))
            surface.blit(txt, txt.get_rect(center=r.center))
        self.toolbar.draw_scroll_hint(surface)

        # Palette dots
        for i, r in enumerate(self.pal_rects):
            selected = (i == self.palette)
            # Draw multicolored preview
            colors = PAL_PREVIEW[i]
            cx, cy = r.centerx, r.centery
            rad = r.width // 2
            # Draw a filled circle with first color, then arcs aren't cheap — just a circle
            pygame.draw.circle(surface, colors[0], (cx, cy), rad)
            if len(colors) > 1:
                pygame.draw.circle(surface, colors[1], (cx - 3, cy + 3), rad // 2 + 1)
            if len(colors) > 2:
                pygame.draw.circle(surface, colors[2], (cx + 3, cy - 3), rad // 2)
            if selected:
                pygame.draw.circle(surface, WHITE, (cx, cy), rad + 3, width=2)

        # Particle count (debug / showcase)
        cnt_font = get_font(16, bold=False)
        cnt_txt = cnt_font.render(f"{self.pool.count}", True, (80, 80, 100))
        surface.blit(cnt_txt, (WIDTH - cnt_txt.get_width() - 10, TOOLBAR_H + 5))

        # Back button (draw last so it's on top)
        self.back_rect = draw_back_button(surface)

    # ---- Emitters ----

    def _get_color(self):
        return _PALETTE_FNS[self.palette](self.hue)

    def _emit_fountain(self, dt):
        count = int(120 * dt) + 1  # ~120 particles/sec
        tx, ty = self.touch_x, self.touch_y
        pool = self.pool
        for _ in range(count):
            angle = -math.pi / 2 + random.gauss(0, 0.4)
            speed = random.uniform(150, 350)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            cr, cg, cb = self._get_color()
            life = random.uniform(2.0, PARTICLE_LIFETIME)
            sz = random.choice((2, 2, 2, 3))
            if not pool.emit(tx + random.uniform(-3, 3), ty,
                             vx, vy, cr, cg, cb, life, sz):
                break

    def _emit_rain(self, dt):
        self._rain_timer += dt
        rate = 200  # particles per second
        interval = 1.0 / rate
        while self._rain_timer >= interval:
            self._rain_timer -= interval
            px = random.uniform(0, WIDTH)
            py = TOOLBAR_H
            vx = random.uniform(-20, 20)
            vy = random.uniform(80, 200)
            cr, cg, cb = self._get_color()
            life = random.uniform(3.0, 5.0)
            sz = random.choice((1, 2, 2))
            if not self.pool.emit(px, py, vx, vy, cr, cg, cb, life, sz):
                break

    def _emit_swirl(self, dt):
        count = int(80 * dt) + 1
        tx, ty = self.touch_x, self.touch_y
        pool = self.pool
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(5, 40)
            px = tx + math.cos(angle) * dist
            py = ty + math.sin(angle) * dist
            # Tangential velocity (perpendicular to radius)
            speed = random.uniform(100, 250)
            vx = -math.sin(angle) * speed
            vy = math.cos(angle) * speed
            cr, cg, cb = self._get_color()
            life = random.uniform(2.5, PARTICLE_LIFETIME)
            sz = random.choice((2, 2, 3))
            if not pool.emit(px, py, vx, vy, cr, cg, cb, life, sz):
                break

    def _emit_explosion(self, ex, ey):
        pool = self.pool
        for _ in range(150):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(100, 500)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            cr, cg, cb = self._get_color()
            life = random.uniform(1.5, 3.5)
            sz = random.choice((2, 3, 3, 4))
            if not pool.emit(ex, ey, vx, vy, cr, cg, cb, life, sz):
                break

    # ---- Forces ----

    def _apply_swirl_forces(self, dt):
        """Pull particles toward touch and spin them tangentially."""
        pool = self.pool
        n = pool.count
        tx = float(self.touch_x)
        ty = float(self.touch_y)
        x = pool.x; y = pool.y
        vx = pool.vx; vy = pool.vy
        attract = 600.0 * dt
        tangent = 400.0 * dt

        for i in range(n):
            dx = tx - x[i]
            dy = ty - y[i]
            dist_sq = dx * dx + dy * dy
            if dist_sq < 1.0:
                continue
            inv_dist = 1.0 / math.sqrt(dist_sq)
            nx_ = dx * inv_dist
            ny_ = dy * inv_dist
            # Attract
            vx[i] += nx_ * attract
            vy[i] += ny_ * attract
            # Tangential push (perpendicular)
            vx[i] += -ny_ * tangent
            vy[i] += nx_ * tangent
            # Damping to prevent runaway speeds
            vx[i] *= 0.98
            vy[i] *= 0.98

    def _apply_wind(self, dt):
        """Push rain particles away from touch point."""
        pool = self.pool
        n = pool.count
        tx = float(self.touch_x)
        ty = float(self.touch_y)
        x = pool.x; y = pool.y
        vx = pool.vx; vy = pool.vy
        strength = 80000.0 * dt

        for i in range(n):
            dx = x[i] - tx
            dy = y[i] - ty
            dist_sq = dx * dx + dy * dy + 100.0  # avoid div-by-zero
            if dist_sq > 90000:  # ~300px radius
                continue
            force = strength / dist_sq
            inv_dist = 1.0 / math.sqrt(dist_sq)
            vx[i] += dx * inv_dist * force
            vy[i] += dy * inv_dist * force
