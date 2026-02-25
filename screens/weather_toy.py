# screens/weather_toy.py — Weather simulation toy for toddlers

import pygame
import random
import math
from config import WIDTH, HEIGHT, WHITE, BLACK
from ui import draw_back_button, get_font, hsv_to_rgb, ScrollToolbar


# ---------------------------------------------------------------------------
# Scene constants
# ---------------------------------------------------------------------------
SCENE_SNOW = 0
SCENE_RAIN = 1
SCENE_FIREFLIES = 2
SCENE_CHERRY = 3
SCENE_AURORA = 4

SCENE_NAMES = ["Snow", "Rain", "Fireflies", "Blossoms", "Aurora"]

# Button strip layout — sits to the right of the back button
_BTN_Y = 10
_BTN_H = 58
_BTN_GAP = 6
_BTN_START_X = 110  # after back button (80px + gap)


# ---------------------------------------------------------------------------
# Gradient helper (cached per scene)
# ---------------------------------------------------------------------------
def _make_gradient(top, bottom):
    surf = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (WIDTH, y))
    return surf


def _make_dusk_gradient():
    """Three-stop gradient: deep blue -> purple -> orange horizon."""
    surf = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        t = y / HEIGHT
        if t < 0.5:
            u = t / 0.5
            r = int(10 + (60 - 10) * u)
            g = int(10 + (20 - 10) * u)
            b = int(60 + (80 - 60) * u)
        else:
            u = (t - 0.5) / 0.5
            r = int(60 + (180 - 60) * u)
            g = int(20 + (100 - 20) * u)
            b = int(80 + (40 - 80) * u)
        pygame.draw.line(surf, (r, g, b), (0, y), (WIDTH, y))
    return surf


def _make_night_sky():
    """Dark night sky for aurora scene."""
    surf = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(5 + 10 * t)
        g = int(5 + 8 * t)
        b = int(20 + 15 * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (WIDTH, y))
    return surf


# ---------------------------------------------------------------------------
# Scene icon drawing helpers (small 30x30 icons drawn with primitives)
# ---------------------------------------------------------------------------
def _draw_icon_snow(surface, cx, cy):
    """Tiny snowflake icon."""
    c = (220, 230, 255)
    for angle_deg in (0, 60, 120):
        a = math.radians(angle_deg)
        dx = int(math.cos(a) * 8)
        dy = int(math.sin(a) * 8)
        pygame.draw.line(surface, c, (cx - dx, cy - dy), (cx + dx, cy + dy), 2)


def _draw_icon_rain(surface, cx, cy):
    """Tiny rain drops icon."""
    c = (140, 180, 255)
    for ox in (-6, 0, 6):
        pygame.draw.line(surface, c, (cx + ox, cy - 6), (cx + ox - 2, cy + 6), 2)


def _draw_icon_fireflies(surface, cx, cy):
    """Tiny glowing dots icon."""
    for ox, oy in ((-5, -3), (4, 2), (-2, 5), (6, -5)):
        pygame.draw.circle(surface, (255, 255, 130), (cx + ox, cy + oy), 2)


def _draw_icon_cherry(surface, cx, cy):
    """Tiny petal icon."""
    for ox, oy in ((-4, -4), (3, 0), (-1, 5)):
        pygame.draw.circle(surface, (255, 180, 200), (cx + ox, cy + oy), 3)


def _draw_icon_aurora(surface, cx, cy):
    """Tiny wavy lines icon."""
    for i, col in enumerate([(80, 255, 180), (100, 200, 255), (180, 120, 255)]):
        y = cy - 4 + i * 4
        pts = [(cx - 8 + j * 4, y + int(math.sin(j + i) * 2)) for j in range(5)]
        pygame.draw.lines(surface, col, False, pts, 2)


_ICON_FUNCS = [_draw_icon_snow, _draw_icon_rain, _draw_icon_fireflies,
               _draw_icon_cherry, _draw_icon_aurora]

_SCENE_COLORS = [
    (100, 140, 180),  # snow button
    (60, 90, 140),    # rain button
    (60, 50, 100),    # fireflies button
    (180, 100, 140),  # cherry button
    (40, 80, 100),    # aurora button
]


# ---------------------------------------------------------------------------
# WeatherToyScreen
# ---------------------------------------------------------------------------
class WeatherToyScreen:

    def __init__(self, app):
        self.app = app
        self.scene = SCENE_SNOW
        self.time = 0.0
        self.particles = []
        self.splashes = []       # rain splashes / cherry gusts
        self.back_rect = None

        # Scrollable toolbar with bigger buttons
        self.toolbar = ScrollToolbar(
            left_x=_BTN_START_X, y=_BTN_Y, height=_BTN_H,
            btn_width=140, btn_gap=_BTN_GAP, btn_count=len(SCENE_NAMES)
        )

        # Pre-render backgrounds (lazy — built on first use)
        self._bg_cache = {}

        # Aurora state
        self._aurora_ripples = []  # (x, time_created)
        self._stars = []

        # Tap interaction
        self._tap_point = None
        self._tap_age = 0.0

    # ------------------------------------------------------------------
    # Background helpers
    # ------------------------------------------------------------------
    def _get_bg(self, scene):
        if scene not in self._bg_cache:
            if scene == SCENE_SNOW:
                self._bg_cache[scene] = _make_gradient((180, 200, 220), (220, 230, 245))
            elif scene == SCENE_RAIN:
                self._bg_cache[scene] = _make_gradient((50, 60, 80), (80, 90, 110))
            elif scene == SCENE_FIREFLIES:
                self._bg_cache[scene] = _make_dusk_gradient()
            elif scene == SCENE_CHERRY:
                self._bg_cache[scene] = _make_gradient((220, 180, 220), (170, 200, 240))
            elif scene == SCENE_AURORA:
                self._bg_cache[scene] = _make_night_sky()
        return self._bg_cache[scene]

    # ------------------------------------------------------------------
    # Particle initializers
    # ------------------------------------------------------------------
    def _init_snow(self):
        self.particles = []
        for _ in range(220):
            self.particles.append(self._new_snowflake(full_screen=True))

    def _new_snowflake(self, full_screen=False):
        return {
            "x": random.uniform(0, WIDTH),
            "y": random.uniform(0, HEIGHT) if full_screen else random.uniform(-40, -5),
            "vx": random.uniform(-10, 10),
            "vy": random.uniform(30, 80),
            "size": random.uniform(2, 6),
            "phase": random.uniform(0, math.pi * 2),
            "sway_speed": random.uniform(1.0, 3.0),
            "sway_amp": random.uniform(15, 40),
            "alpha": random.randint(160, 255),
        }

    def _init_rain(self):
        self.particles = []
        for _ in range(400):
            self.particles.append(self._new_raindrop(full_screen=True))

    def _new_raindrop(self, full_screen=False):
        return {
            "x": random.uniform(0, WIDTH),
            "y": random.uniform(0, HEIGHT) if full_screen else random.uniform(-60, -5),
            "vy": random.uniform(500, 900),
            "length": random.randint(8, 20),
            "alpha": random.randint(100, 200),
        }

    def _init_fireflies(self):
        self.particles = []
        for _ in range(80):
            self.particles.append(self._new_firefly())

    def _new_firefly(self):
        return {
            "x": random.uniform(20, WIDTH - 20),
            "y": random.uniform(80, HEIGHT - 20),
            "vx": random.uniform(-20, 20),
            "vy": random.uniform(-20, 20),
            "size": random.uniform(2, 5),
            "phase": random.uniform(0, math.pi * 2),
            "pulse_speed": random.uniform(1.5, 4.0),
            "hue": random.uniform(40, 70),  # warm yellows / greens
        }

    def _init_cherry(self):
        self.particles = []
        for _ in range(150):
            self.particles.append(self._new_petal(full_screen=True))

    def _new_petal(self, full_screen=False):
        return {
            "x": random.uniform(0, WIDTH),
            "y": random.uniform(0, HEIGHT) if full_screen else random.uniform(-40, -5),
            "vx": random.uniform(-15, 25),
            "vy": random.uniform(25, 70),
            "size": random.uniform(3, 7),
            "rotation": random.uniform(0, math.pi * 2),
            "rot_speed": random.uniform(1.0, 4.0),
            "phase": random.uniform(0, math.pi * 2),
            "sway_amp": random.uniform(20, 50),
            "sway_speed": random.uniform(0.8, 2.5),
            "shade": random.choice([
                (255, 183, 197), (255, 200, 210), (255, 220, 230),
                (255, 170, 190), (245, 160, 180), (255, 230, 240),
            ]),
        }

    def _init_aurora(self):
        self.particles = []  # not used for aurora
        self._aurora_ripples = []
        self._stars = []
        for _ in range(120):
            self._stars.append({
                "x": random.randint(0, WIDTH),
                "y": random.randint(int(HEIGHT * 0.45), HEIGHT),
                "size": random.choice([1, 1, 1, 2]),
                "alpha": random.randint(80, 255),
                "twinkle_speed": random.uniform(1.0, 4.0),
                "phase": random.uniform(0, math.pi * 2),
            })

    # ------------------------------------------------------------------
    # Scene switching
    # ------------------------------------------------------------------
    def _switch_scene(self, scene):
        self.scene = scene
        self.splashes = []
        self._tap_point = None
        self._tap_age = 0.0
        inits = [self._init_snow, self._init_rain, self._init_fireflies,
                 self._init_cherry, self._init_aurora]
        inits[scene]()

    # ------------------------------------------------------------------
    # Screen interface
    # ------------------------------------------------------------------
    def on_enter(self):
        self.time = 0.0
        self._switch_scene(SCENE_SNOW)

    def handle_event(self, event):
        # Let toolbar handle scroll gestures first
        if self.toolbar.handle_event(event):
            # Check if it was a tap (not a drag) on a button
            if event.type == pygame.MOUSEBUTTONUP:
                idx = self.toolbar.get_btn_at(event.pos)
                if idx >= 0 and idx != self.scene:
                    self._switch_scene(idx)
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            # Back button
            if self.back_rect and self.back_rect.collidepoint(pos):
                self.app.go_back()
                return
            # Scene button tap (when no scrolling needed)
            idx = self.toolbar.get_btn_at(pos)
            if idx >= 0:
                if idx != self.scene:
                    self._switch_scene(idx)
                return
            # Tap interaction within scene area
            self._tap_point = pos
            self._tap_age = 0.0
            self._handle_tap(pos)

    def _handle_tap(self, pos):
        tx, ty = pos
        if self.scene == SCENE_SNOW:
            # Blow snowflakes away from tap point
            for p in self.particles:
                dx = p["x"] - tx
                dy = p["y"] - ty
                dist = math.sqrt(dx * dx + dy * dy) + 0.1
                if dist < 150:
                    force = (150 - dist) / 150 * 300
                    p["vx"] += (dx / dist) * force
                    p["vy"] += (dy / dist) * force * 0.5

        elif self.scene == SCENE_RAIN:
            # Splash particles at tap
            for _ in range(20):
                angle = random.uniform(-math.pi, 0)  # upward hemisphere
                speed = random.uniform(100, 350)
                self.splashes.append({
                    "x": tx + random.uniform(-5, 5),
                    "y": ty + random.uniform(-3, 3),
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed,
                    "life": random.uniform(0.3, 0.7),
                    "size": random.uniform(2, 5),
                    "color": random.choice([
                        (140, 180, 255), (160, 200, 255), (100, 150, 230),
                        (180, 210, 255), (120, 170, 240),
                    ]),
                })

        elif self.scene == SCENE_FIREFLIES:
            # Attract nearby fireflies toward tap
            for p in self.particles:
                dx = tx - p["x"]
                dy = ty - p["y"]
                dist = math.sqrt(dx * dx + dy * dy) + 0.1
                if dist < 200:
                    strength = (200 - dist) / 200 * 60
                    p["vx"] += (dx / dist) * strength
                    p["vy"] += (dy / dist) * strength

        elif self.scene == SCENE_CHERRY:
            # Gust — petals near tap swirl upward
            for p in self.particles:
                dx = p["x"] - tx
                dy = p["y"] - ty
                dist = math.sqrt(dx * dx + dy * dy) + 0.1
                if dist < 160:
                    force = (160 - dist) / 160
                    # Swirl: perpendicular + upward
                    p["vx"] += (-dy / dist) * force * 200 + random.uniform(-40, 40)
                    p["vy"] += -force * 250

        elif self.scene == SCENE_AURORA:
            # Ripple in aurora bands
            self._aurora_ripples.append({"x": tx, "t": 0.0})

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------
    def update(self, dt):
        self.time += dt
        self.toolbar.update(dt)

        if self._tap_point:
            self._tap_age += dt
            if self._tap_age > 0.5:
                self._tap_point = None

        if self.scene == SCENE_SNOW:
            self._update_snow(dt)
        elif self.scene == SCENE_RAIN:
            self._update_rain(dt)
        elif self.scene == SCENE_FIREFLIES:
            self._update_fireflies(dt)
        elif self.scene == SCENE_CHERRY:
            self._update_cherry(dt)
        elif self.scene == SCENE_AURORA:
            self._update_aurora(dt)

    def _update_snow(self, dt):
        for p in self.particles:
            # Lateral sway
            sway = math.sin(self.time * p["sway_speed"] + p["phase"]) * p["sway_amp"]
            p["x"] += (p["vx"] + sway) * dt
            p["y"] += p["vy"] * dt
            # Dampen blow velocity
            p["vx"] *= 0.96
            # Wrap
            if p["y"] > HEIGHT + 10:
                p["y"] = random.uniform(-20, -5)
                p["x"] = random.uniform(0, WIDTH)
                p["vx"] = random.uniform(-10, 10)
            if p["x"] < -20:
                p["x"] = WIDTH + 10
            elif p["x"] > WIDTH + 20:
                p["x"] = -10

    def _update_rain(self, dt):
        for p in self.particles:
            p["y"] += p["vy"] * dt
            p["x"] += -30 * dt  # slight wind
            if p["y"] > HEIGHT + 10:
                p["y"] = random.uniform(-60, -5)
                p["x"] = random.uniform(0, WIDTH)
        # Update splashes
        for s in self.splashes:
            s["x"] += s["vx"] * dt
            s["y"] += s["vy"] * dt
            s["vy"] += 500 * dt  # gravity
            s["life"] -= dt
        self.splashes = [s for s in self.splashes if s["life"] > 0]

    def _update_fireflies(self, dt):
        for p in self.particles:
            # Random drift adjustments
            p["vx"] += random.uniform(-30, 30) * dt
            p["vy"] += random.uniform(-30, 30) * dt
            # Dampen
            p["vx"] *= 0.98
            p["vy"] *= 0.98
            # Clamp speed
            speed = math.sqrt(p["vx"] ** 2 + p["vy"] ** 2)
            if speed > 50:
                p["vx"] = p["vx"] / speed * 50
                p["vy"] = p["vy"] / speed * 50
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            # Soft boundary
            if p["x"] < 10:
                p["vx"] += 30 * dt
            elif p["x"] > WIDTH - 10:
                p["vx"] -= 30 * dt
            if p["y"] < 80:
                p["vy"] += 30 * dt
            elif p["y"] > HEIGHT - 10:
                p["vy"] -= 30 * dt

    def _update_cherry(self, dt):
        for p in self.particles:
            sway = math.sin(self.time * p["sway_speed"] + p["phase"]) * p["sway_amp"]
            p["x"] += (p["vx"] + sway) * dt
            p["y"] += p["vy"] * dt
            p["rotation"] += p["rot_speed"] * dt
            # Restore natural fall speed after gust
            p["vx"] *= 0.97
            if p["vy"] < 25:
                p["vy"] += 120 * dt  # gravity pull back down
            # Wrap
            if p["y"] > HEIGHT + 10:
                p["y"] = random.uniform(-30, -5)
                p["x"] = random.uniform(0, WIDTH)
                p["vx"] = random.uniform(-15, 25)
                p["vy"] = random.uniform(25, 70)
            if p["y"] < -80:
                p["vy"] = random.uniform(25, 70)
            if p["x"] < -30:
                p["x"] = WIDTH + 10
            elif p["x"] > WIDTH + 30:
                p["x"] = -10

    def _update_aurora(self, dt):
        # Update ripples
        for r in self._aurora_ripples:
            r["t"] += dt
        self._aurora_ripples = [r for r in self._aurora_ripples if r["t"] < 3.0]

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------
    def draw(self, surface):
        # Background
        surface.blit(self._get_bg(self.scene), (0, 0))

        if self.scene == SCENE_SNOW:
            self._draw_snow(surface)
        elif self.scene == SCENE_RAIN:
            self._draw_rain(surface)
        elif self.scene == SCENE_FIREFLIES:
            self._draw_fireflies(surface)
        elif self.scene == SCENE_CHERRY:
            self._draw_cherry(surface)
        elif self.scene == SCENE_AURORA:
            self._draw_aurora(surface)

        # UI on top
        self._draw_buttons(surface)
        self.back_rect = draw_back_button(surface)

    # -- Snow -----------------------------------------------------------
    def _draw_snow(self, surface):
        for p in self.particles:
            x = int(p["x"])
            y = int(p["y"])
            size = int(p["size"])
            # Slightly blue-tinted white
            shade = random.choice([(255, 255, 255), (220, 230, 250), (200, 220, 245)]) \
                if size > 4 else (255, 255, 255)
            pygame.draw.circle(surface, shade, (x, y), size)
            # Tiny bright center for larger flakes
            if size >= 4:
                pygame.draw.circle(surface, (255, 255, 255), (x, y), max(1, size // 2))

    # -- Rain -----------------------------------------------------------
    def _draw_rain(self, surface):
        for p in self.particles:
            x = int(p["x"])
            y = int(p["y"])
            length = p["length"]
            alpha = p["alpha"]
            color = (140, 170, 220 + min(35, alpha // 6))
            pygame.draw.line(surface, color,
                             (x, y), (x + 2, y + length), 1)
        # Splashes
        for s in self.splashes:
            alpha_ratio = max(0, s["life"] / 0.7)
            r = max(1, int(s["size"] * alpha_ratio))
            pygame.draw.circle(surface, s["color"],
                               (int(s["x"]), int(s["y"])), r)

    # -- Fireflies ------------------------------------------------------
    def _draw_fireflies(self, surface):
        for p in self.particles:
            pulse = (math.sin(self.time * p["pulse_speed"] + p["phase"]) + 1) * 0.5
            alpha = int(40 + 215 * pulse)
            size = p["size"]
            glow_r = int(size * 3 + pulse * 6)
            x = int(p["x"])
            y = int(p["y"])

            # Glow halo (small SRCALPHA surface)
            glow_size = glow_r * 2 + 2
            glow = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
            rgb = hsv_to_rgb(p["hue"], 0.8, 1.0)
            pygame.draw.circle(glow, (*rgb, alpha // 3),
                               (glow_size // 2, glow_size // 2), glow_r)
            pygame.draw.circle(glow, (*rgb, alpha // 2),
                               (glow_size // 2, glow_size // 2), max(1, glow_r // 2))
            surface.blit(glow, (x - glow_size // 2, y - glow_size // 2))

            # Core dot
            core_alpha = min(255, alpha)
            core_color = (
                min(255, rgb[0] + 60),
                min(255, rgb[1] + 60),
                min(255, rgb[2] + 20),
            )
            pygame.draw.circle(surface, core_color, (x, y), max(1, int(size * (0.6 + 0.4 * pulse))))

    # -- Cherry Blossoms ------------------------------------------------
    def _draw_cherry(self, surface):
        for p in self.particles:
            x = int(p["x"])
            y = int(p["y"])
            size = p["size"]
            rot = p["rotation"]
            shade = p["shade"]

            # Draw petal as a small ellipse-like shape using two offset circles
            dx = int(math.cos(rot) * size * 0.5)
            dy = int(math.sin(rot) * size * 0.5)
            s = max(2, int(size * 0.7))
            pygame.draw.circle(surface, shade, (x + dx, y + dy), s)
            pygame.draw.circle(surface, shade, (x - dx, y - dy), max(1, s - 1))
            # Bright center
            pygame.draw.circle(surface, (255, 240, 245), (x, y), max(1, s // 2))

    # -- Aurora Borealis ------------------------------------------------
    def _draw_aurora(self, surface):
        # Stars (below aurora)
        for star in self._stars:
            twinkle = (math.sin(self.time * star["twinkle_speed"] + star["phase"]) + 1) * 0.5
            alpha = int(star["alpha"] * (0.4 + 0.6 * twinkle))
            color = (alpha, alpha, min(255, alpha + 30))
            pygame.draw.circle(surface, color,
                               (star["x"], star["y"]), star["size"])

        # Aurora bands — draw as horizontal line strips across top portion
        band_bottom = int(HEIGHT * 0.55)
        band_top = 80
        num_bands = 5
        band_height = (band_bottom - band_top) // num_bands

        # Use a SRCALPHA surface for translucent aurora
        aurora_surf = pygame.Surface((WIDTH, band_bottom - band_top), pygame.SRCALPHA)

        for band_i in range(num_bands):
            base_hue = 120 + band_i * 35  # greens -> teals -> purples
            y_base = band_i * band_height

            for x in range(0, WIDTH, 3):
                # Compute ripple offset from taps
                ripple_offset = 0.0
                for rip in self._aurora_ripples:
                    dist = abs(x - rip["x"])
                    age = rip["t"]
                    wave_pos = age * 200  # expanding ring
                    if abs(dist - wave_pos) < 80:
                        ripple_strength = max(0, 1.0 - age / 3.0)
                        ripple_offset += math.sin((dist - wave_pos) * 0.1) * 25 * ripple_strength

                # Sine wave shape
                wave1 = math.sin(x * 0.008 + self.time * 0.5 + band_i * 0.7) * 30
                wave2 = math.sin(x * 0.015 + self.time * 0.8 + band_i * 1.2) * 15
                wave3 = math.sin(x * 0.003 + self.time * 0.3) * 20
                y_offset = wave1 + wave2 + wave3 + ripple_offset

                y_pos = int(y_base + band_height * 0.5 + y_offset)

                # Color from HSV with time-varying hue
                hue = (base_hue + math.sin(x * 0.005 + self.time * 0.4) * 20
                       + self.time * 8) % 360
                rgb = hsv_to_rgb(hue, 0.7, 1.0)

                # Fade alpha at edges of each band
                band_center = y_base + band_height // 2
                dist_from_center = abs(y_pos - band_center)
                alpha = max(0, min(120, int(120 * (1 - dist_from_center / (band_height * 0.8)))))

                if 0 <= y_pos < aurora_surf.get_height() - 4:
                    for dy in range(-2, 3):
                        fade = max(0, alpha - abs(dy) * 30)
                        if fade > 0:
                            aurora_surf.set_at((x, y_pos + dy),
                                               (*rgb, fade))
                            if x + 1 < WIDTH:
                                aurora_surf.set_at((x + 1, y_pos + dy),
                                                   (*rgb, fade))
                            if x + 2 < WIDTH:
                                aurora_surf.set_at((x + 2, y_pos + dy),
                                                   (*rgb, max(0, fade - 20)))

        surface.blit(aurora_surf, (0, band_top))

        # Faint ground silhouette (dark treeline)
        ground_y = int(HEIGHT * 0.88)
        pygame.draw.rect(surface, (8, 10, 15), (0, ground_y, WIDTH, HEIGHT - ground_y))
        # Jagged treeline
        for x in range(0, WIDTH, 12):
            tree_h = random.Random(x).randint(15, 50)  # deterministic per x
            pygame.draw.polygon(surface, (10, 15, 12), [
                (x, ground_y), (x + 6, ground_y - tree_h), (x + 12, ground_y)
            ])

    # -- Button strip ---------------------------------------------------
    def _draw_buttons(self, surface):
        font = get_font(20)
        btn_rects = self.toolbar.get_btn_rects()
        for i, rect in enumerate(btn_rects):
            # Skip buttons fully off-screen
            if rect.right < self.toolbar.left_x or rect.left > WIDTH:
                continue
            color = _SCENE_COLORS[i]
            is_active = (i == self.scene)

            if is_active:
                bright = tuple(min(255, c + 60) for c in color)
                pygame.draw.rect(surface, bright, rect, border_radius=14)
                pygame.draw.rect(surface, WHITE, rect, width=2, border_radius=14)
            else:
                btn_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                pygame.draw.rect(btn_surf, (*color, 160), (0, 0, rect.width, rect.height),
                                 border_radius=14)
                surface.blit(btn_surf, rect.topleft)

            # Icon centered above label
            icon_y = rect.centery - 10
            _ICON_FUNCS[i](surface, rect.centerx, icon_y)

            # Label centered below icon
            label = font.render(SCENE_NAMES[i], True, WHITE)
            surface.blit(label, label.get_rect(centerx=rect.centerx, bottom=rect.bottom - 5))

        self.toolbar.draw_scroll_hint(surface)
