# screens/magic_garden.py — Magic Garden planting game for toddlers

import pygame
import random
import math
from config import WIDTH, HEIGHT, WHITE, BLACK
from ui import draw_back_button, get_font, ScrollToolbar


# ---------------------------------------------------------------------------
# Plant types
# ---------------------------------------------------------------------------
TOOL_FLOWER = 0
TOOL_TREE = 1
TOOL_BUTTERFLY = 2
TOOL_BEE = 3

MAX_ITEMS = 30

GRASS_TOP = HEIGHT - 200  # y where grass starts

# Petal color palette
PETAL_COLORS = [
    (255, 130, 170),  # pink
    (230, 60, 60),    # red
    (255, 220, 80),   # yellow
    (255, 160, 60),   # orange
    (200, 120, 255),  # purple
    (255, 180, 200),  # light pink
]

# Tool button definitions: (label, fill color, icon color)
TOOL_DEFS = [
    ("Flower", (255, 140, 180), (255, 80, 130)),
    ("Tree",   (110, 80, 50),   (60, 160, 60)),
    ("Fly",    (190, 130, 255), (230, 180, 255)),
    ("Bee",    (255, 220, 60),  (60, 50, 10)),
]


# ---------------------------------------------------------------------------
# Garden items
# ---------------------------------------------------------------------------

class Flower:
    """A flower that grows from a seed into a blooming flower with swaying stem."""

    def __init__(self, x, y):
        self.x = x
        self.base_y = y
        self.age = 0.0
        self.grow_time = 1.8  # seconds to fully grow
        self.petal_color = random.choice(PETAL_COLORS)
        self.center_color = (255, 230, 80)
        self.num_petals = random.randint(5, 7)
        self.max_height = random.randint(50, 100)
        self.sway_phase = random.uniform(0, math.pi * 2)
        self.sway_speed = random.uniform(1.5, 2.5)
        self.petal_size = random.randint(10, 16)

    def update(self, dt, time):
        self.age += dt

    def draw(self, surface, time):
        progress = min(1.0, self.age / self.grow_time)

        # Sway offset at the tip
        sway = math.sin(time * self.sway_speed + self.sway_phase) * 6 * progress

        # Stem growth
        stem_h = int(self.max_height * progress)
        tip_x = self.x + sway
        tip_y = self.base_y - stem_h

        if stem_h > 2:
            # Draw stem as a slightly curved line
            stem_color = (60, 160, 50)
            mid_x = self.x + sway * 0.4
            mid_y = self.base_y - stem_h * 0.5
            points = [
                (self.x, self.base_y),
                (int(mid_x), int(mid_y)),
                (int(tip_x), int(tip_y)),
            ]
            pygame.draw.lines(surface, stem_color, False, points, 3)

            # Small leaves on the stem once it is growing
            if progress > 0.4:
                leaf_y = int(self.base_y - stem_h * 0.45)
                leaf_x = int(self.x + sway * 0.3)
                pygame.draw.ellipse(surface, (80, 190, 60),
                                    (leaf_x - 8, leaf_y - 3, 16, 7))

        # Bloom
        if progress > 0.5:
            bloom = (progress - 0.5) / 0.5  # 0..1 during bloom phase
            r = int(self.petal_size * bloom)
            cr = max(2, int(r * 0.45))
            if r > 1:
                for i in range(self.num_petals):
                    angle = (2 * math.pi / self.num_petals) * i
                    px = int(tip_x + math.cos(angle) * r * 0.7)
                    py = int(tip_y + math.sin(angle) * r * 0.7)
                    pygame.draw.circle(surface, self.petal_color, (px, py), r)
                # Center
                pygame.draw.circle(surface, self.center_color,
                                   (int(tip_x), int(tip_y)), cr)
        elif progress > 0.05:
            # Seed / sprout dot
            pygame.draw.circle(surface, (100, 180, 70),
                               (int(tip_x), int(tip_y)), 3)


class Tree:
    """A tree that grows a trunk then expands a leafy crown."""

    def __init__(self, x, y):
        self.x = x
        self.base_y = y
        self.age = 0.0
        self.grow_time = 2.5
        self.max_height = random.randint(80, 140)
        self.crown_radius = random.randint(30, 50)
        self.trunk_width = random.randint(8, 14)
        self.sway_phase = random.uniform(0, math.pi * 2)
        self.leaf_color = (
            random.randint(40, 80),
            random.randint(150, 210),
            random.randint(40, 80),
        )
        self.leaf_highlight = (
            min(255, self.leaf_color[0] + 40),
            min(255, self.leaf_color[1] + 40),
            min(255, self.leaf_color[2] + 40),
        )

    def update(self, dt, time):
        self.age += dt

    def draw(self, surface, time):
        progress = min(1.0, self.age / self.grow_time)
        trunk_progress = min(1.0, progress / 0.5)  # trunk grows in first half
        crown_progress = max(0.0, (progress - 0.4) / 0.6)  # crown in second portion

        sway = math.sin(time * 1.2 + self.sway_phase) * 3 * progress

        trunk_h = int(self.max_height * trunk_progress)
        top_y = self.base_y - trunk_h
        top_x = self.x + sway

        # Trunk
        if trunk_h > 2:
            hw = self.trunk_width // 2
            # Slightly tapered trunk
            top_hw = max(2, hw - 2)
            points = [
                (self.x - hw, self.base_y),
                (self.x + hw, self.base_y),
                (int(top_x + top_hw), int(top_y)),
                (int(top_x - top_hw), int(top_y)),
            ]
            pygame.draw.polygon(surface, (110, 75, 45), points)
            # Bark highlight
            pygame.draw.line(surface, (140, 100, 60),
                             (self.x, self.base_y),
                             (int(top_x), int(top_y)), 2)

        # Crown
        if crown_progress > 0.0:
            cr = int(self.crown_radius * crown_progress)
            if cr > 2:
                # Main crown
                pygame.draw.circle(surface, self.leaf_color,
                                   (int(top_x), int(top_y - cr * 0.3)), cr)
                # Highlight blobs
                for dx, dy in [(-0.3, -0.4), (0.3, -0.5), (0, -0.7)]:
                    hx = int(top_x + cr * dx)
                    hy = int(top_y - cr * 0.3 + cr * dy)
                    pygame.draw.circle(surface, self.leaf_highlight,
                                       (hx, hy), int(cr * 0.5))


class Butterfly:
    """A butterfly that flutters around near its spawn point."""

    def __init__(self, x, y):
        self.home_x = x
        self.home_y = y
        self.x = float(x)
        self.y = float(y)
        self.age = 0.0
        self.wing_color = (
            random.randint(150, 255),
            random.randint(80, 255),
            random.randint(150, 255),
        )
        self.wing_accent = (
            min(255, self.wing_color[0] + 50),
            min(255, self.wing_color[1] + 50),
            max(0, self.wing_color[2] - 30),
        )
        self.phase_x = random.uniform(0, math.pi * 2)
        self.phase_y = random.uniform(0, math.pi * 2)
        self.speed_x = random.uniform(0.4, 0.9)
        self.speed_y = random.uniform(0.5, 1.0)
        self.range_x = random.uniform(40, 80)
        self.range_y = random.uniform(25, 50)
        self.wing_speed = random.uniform(5, 8)
        self.size = random.randint(10, 15)

    def update(self, dt, time):
        self.age += dt
        self.x = self.home_x + math.sin(time * self.speed_x + self.phase_x) * self.range_x
        self.y = self.home_y + math.sin(time * self.speed_y + self.phase_y) * self.range_y

    def draw(self, surface, time):
        # Wing flap: scale from 0.2 to 1.0
        flap = (math.sin(time * self.wing_speed) + 1) * 0.4 + 0.2
        s = self.size
        ix = int(self.x)
        iy = int(self.y)

        wing_w = int(s * flap)

        # Left wing
        if wing_w > 1:
            pygame.draw.ellipse(surface, self.wing_color,
                                (ix - wing_w - 2, iy - s, wing_w, s * 2))
            # Accent dot
            pygame.draw.ellipse(surface, self.wing_accent,
                                (ix - wing_w, iy - s // 2, max(1, wing_w // 2), s))
        # Right wing
        if wing_w > 1:
            pygame.draw.ellipse(surface, self.wing_color,
                                (ix + 2, iy - s, wing_w, s * 2))
            pygame.draw.ellipse(surface, self.wing_accent,
                                (ix + wing_w // 2 + 1, iy - s // 2, max(1, wing_w // 2), s))

        # Body
        pygame.draw.ellipse(surface, (40, 30, 30), (ix - 2, iy - s // 2, 4, s))
        # Antennae
        pygame.draw.line(surface, (60, 50, 50), (ix, iy - s // 2),
                         (ix - 4, iy - s // 2 - 6), 1)
        pygame.draw.line(surface, (60, 50, 50), (ix, iy - s // 2),
                         (ix + 4, iy - s // 2 - 6), 1)
        # Antenna tips
        pygame.draw.circle(surface, self.wing_color, (ix - 4, iy - s // 2 - 6), 2)
        pygame.draw.circle(surface, self.wing_color, (ix + 4, iy - s // 2 - 6), 2)


class Bee:
    """A bee that buzzes in a figure-8 pattern near its spawn point."""

    def __init__(self, x, y):
        self.home_x = x
        self.home_y = y
        self.x = float(x)
        self.y = float(y)
        self.age = 0.0
        self.phase = random.uniform(0, math.pi * 2)
        self.speed = random.uniform(1.5, 2.5)
        self.range_x = random.uniform(30, 60)
        self.range_y = random.uniform(20, 40)
        self.size = random.randint(8, 12)
        self.wing_speed = random.uniform(12, 18)

    def update(self, dt, time):
        self.age += dt
        t = time * self.speed + self.phase
        # Figure-8
        self.x = self.home_x + math.sin(t) * self.range_x
        self.y = self.home_y + math.sin(t * 2) * self.range_y

    def draw(self, surface, time):
        ix = int(self.x)
        iy = int(self.y)
        s = self.size

        # Wings (flutter)
        wing_up = math.sin(time * self.wing_speed) * 3
        wing_color = (200, 220, 255, 180)
        # Use opaque fallback since draw primitives don't support alpha well
        wing_draw = (200, 220, 255)
        pygame.draw.ellipse(surface, wing_draw,
                            (ix - s + 2, iy - s + int(wing_up), s, s - 2))
        pygame.draw.ellipse(surface, wing_draw,
                            (ix - 1, iy - s + int(-wing_up), s, s - 2))

        # Body — yellow with black stripes
        body_rect = (ix - s // 2, iy - s // 3, s, int(s * 0.7))
        pygame.draw.ellipse(surface, (255, 220, 50), body_rect)
        # Stripes
        stripe_w = max(1, s // 5)
        for sx in range(ix - s // 4, ix + s // 3, stripe_w * 2):
            pygame.draw.line(surface, BLACK, (sx, iy - s // 4),
                             (sx, iy + s // 4), max(1, stripe_w // 2))

        # Head
        pygame.draw.circle(surface, (50, 40, 10), (ix - s // 2, iy), max(2, s // 3))
        # Eyes
        pygame.draw.circle(surface, WHITE, (ix - s // 2 - 1, iy - 1), max(1, s // 6))

        # Stinger
        pygame.draw.circle(surface, (40, 30, 10),
                           (ix + s // 2 + 1, iy), max(1, s // 5))


# ---------------------------------------------------------------------------
# Sparkle particle for planting feedback
# ---------------------------------------------------------------------------

class Sparkle:
    """Small sparkle that pops up when something is planted."""

    def __init__(self, x, y, color):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(60, 180)
        self.x = float(x)
        self.y = float(y)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - 60
        self.color = color
        self.life = random.uniform(0.4, 0.8)
        self.max_life = self.life
        self.radius = random.uniform(2, 5)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 120 * dt
        self.life -= dt

    def draw(self, surface):
        if self.life > 0:
            alpha = self.life / self.max_life
            r = max(1, int(self.radius * alpha))
            pygame.draw.circle(surface, self.color,
                               (int(self.x), int(self.y)), r)


# ---------------------------------------------------------------------------
# Main screen
# ---------------------------------------------------------------------------

class MagicGardenScreen:

    # Sky gradient
    SKY_TOP = (135, 206, 250)
    SKY_BOTTOM = (200, 230, 255)
    # Grass gradient
    GRASS_TOP_COLOR = (100, 200, 80)
    GRASS_BOTTOM_COLOR = (60, 150, 50)

    def __init__(self, app):
        self.app = app
        self.items = []
        self.sparkles = []
        self.selected_tool = TOOL_FLOWER
        self.time = 0.0
        self.back_rect = None
        self.tool_rects = []
        self.clear_rect = None
        self.bg_surface = None

    def _build_bg(self):
        """Pre-render background gradient: sky + grass."""
        surf = pygame.Surface((WIDTH, HEIGHT))
        # Sky
        for y in range(GRASS_TOP):
            t = y / max(1, GRASS_TOP)
            r = int(self.SKY_TOP[0] + (self.SKY_BOTTOM[0] - self.SKY_TOP[0]) * t)
            g = int(self.SKY_TOP[1] + (self.SKY_BOTTOM[1] - self.SKY_TOP[1]) * t)
            b = int(self.SKY_TOP[2] + (self.SKY_BOTTOM[2] - self.SKY_TOP[2]) * t)
            pygame.draw.line(surf, (r, g, b), (0, y), (WIDTH, y))
        # Grass
        grass_h = HEIGHT - GRASS_TOP
        for y in range(grass_h):
            t = y / max(1, grass_h)
            r = int(self.GRASS_TOP_COLOR[0] + (self.GRASS_BOTTOM_COLOR[0] - self.GRASS_TOP_COLOR[0]) * t)
            g = int(self.GRASS_TOP_COLOR[1] + (self.GRASS_BOTTOM_COLOR[1] - self.GRASS_TOP_COLOR[1]) * t)
            b = int(self.GRASS_TOP_COLOR[2] + (self.GRASS_BOTTOM_COLOR[2] - self.GRASS_TOP_COLOR[2]) * t)
            pygame.draw.line(surf, (r, g, b), (0, GRASS_TOP + y), (WIDTH, GRASS_TOP + y))
        return surf

    def on_enter(self):
        self.items = []
        self.sparkles = []
        self.selected_tool = TOOL_FLOWER
        self.time = 0.0
        if self.bg_surface is None:
            self.bg_surface = self._build_bg()

    def _spawn_sparkles(self, x, y, color):
        for _ in range(10):
            shade = (
                min(255, max(0, color[0] + random.randint(-30, 40))),
                min(255, max(0, color[1] + random.randint(-30, 40))),
                min(255, max(0, color[2] + random.randint(-30, 40))),
            )
            self.sparkles.append(Sparkle(x, y, shade))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos

            # Back button
            if self.back_rect and self.back_rect.collidepoint(pos):
                self.app.go_back()
                return

            # Clear button
            if self.clear_rect and self.clear_rect.collidepoint(pos):
                self.items = []
                self.sparkles = []
                return

            # Tool buttons
            for i, rect in enumerate(self.tool_rects):
                if rect.collidepoint(pos):
                    self.selected_tool = i
                    return

            # Plant on grass area (below tool bar, on or above the grass)
            if pos[1] > 90 and len(self.items) < MAX_ITEMS:
                x, y = pos
                # Clamp planting to grass region for ground items, allow
                # butterflies/bees in the sky too
                if self.selected_tool == TOOL_FLOWER:
                    y = max(GRASS_TOP + 10, y)
                    item = Flower(x, y)
                    self._spawn_sparkles(x, y, item.petal_color)
                elif self.selected_tool == TOOL_TREE:
                    y = max(GRASS_TOP + 20, y)
                    item = Tree(x, y)
                    self._spawn_sparkles(x, y, (100, 200, 80))
                elif self.selected_tool == TOOL_BUTTERFLY:
                    item = Butterfly(x, y)
                    self._spawn_sparkles(x, y, item.wing_color)
                elif self.selected_tool == TOOL_BEE:
                    item = Bee(x, y)
                    self._spawn_sparkles(x, y, (255, 220, 60))
                else:
                    return
                self.items.append(item)

    def update(self, dt):
        self.time += dt
        for item in self.items:
            item.update(dt, self.time)
        for s in self.sparkles:
            s.update(dt)
        self.sparkles = [s for s in self.sparkles if s.life > 0]

    def draw(self, surface):
        # Background
        if self.bg_surface is None:
            self.bg_surface = self._build_bg()
        surface.blit(self.bg_surface, (0, 0))

        # Grass texture — a few darker blades scattered
        random.seed(42)  # deterministic so it doesn't flicker
        for _ in range(60):
            gx = random.randint(0, WIDTH)
            gy = random.randint(GRASS_TOP, HEIGHT)
            blade_h = random.randint(5, 15)
            shade = random.randint(0, 40)
            color = (60 - shade, 140 + random.randint(0, 30), 50 - shade)
            color = tuple(max(0, min(255, c)) for c in color)
            pygame.draw.line(surface, color, (gx, gy), (gx + random.randint(-3, 3), gy - blade_h), 1)
        random.seed()  # restore randomness

        # Horizon line (soft)
        pygame.draw.line(surface, (80, 180, 60), (0, GRASS_TOP), (WIDTH, GRASS_TOP), 2)

        # Sun in top-right sky
        sun_x, sun_y = WIDTH - 80, 70
        for r in range(50, 20, -5):
            alpha = 40 + (50 - r) * 3
            sun_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(sun_surf, (255, 240, 100, alpha), (r, r), r)
            surface.blit(sun_surf, (sun_x - r, sun_y - r))
        pygame.draw.circle(surface, (255, 240, 130), (sun_x, sun_y), 22)

        # Garden items — draw ground items (flowers, trees) first, then flying
        ground = [it for it in self.items if isinstance(it, (Flower, Tree))]
        flying = [it for it in self.items if isinstance(it, (Butterfly, Bee))]
        for item in ground:
            item.draw(surface, self.time)
        for item in flying:
            item.draw(surface, self.time)

        # Sparkles
        for s in self.sparkles:
            s.draw(surface)

        # --- UI overlay ---

        # Back button
        self.back_rect = draw_back_button(surface)

        # Tool buttons along top
        self.tool_rects = []
        btn_w, btn_h = 120, 62
        start_x = 110
        btn_y = 10
        font = get_font(18)

        for i, (label, fill, icon_col) in enumerate(TOOL_DEFS):
            x = start_x + i * (btn_w + 10)
            rect = pygame.Rect(x, btn_y, btn_w, btn_h)
            self.tool_rects.append(rect)

            # Selected highlight
            if i == self.selected_tool:
                # Glow behind
                pygame.draw.rect(surface, WHITE,
                                 rect.inflate(6, 6), border_radius=14)
            # Button bg
            pygame.draw.rect(surface, fill, rect, border_radius=10)
            # Border
            border_col = WHITE if i == self.selected_tool else (0, 0, 0, 80)
            pygame.draw.rect(surface, (60, 60, 60) if i != self.selected_tool else WHITE,
                             rect, width=2, border_radius=10)

            # Icon hint — small shape in the button
            cx, cy = rect.centerx, rect.centery - 4
            if i == TOOL_FLOWER:
                for a in range(5):
                    angle = (2 * math.pi / 5) * a
                    px = int(cx + math.cos(angle) * 8)
                    py = int(cy + math.sin(angle) * 8)
                    pygame.draw.circle(surface, icon_col, (px, py), 5)
                pygame.draw.circle(surface, (255, 230, 80), (cx, cy), 4)
            elif i == TOOL_TREE:
                pygame.draw.rect(surface, fill, (cx - 3, cy + 2, 6, 10))
                pygame.draw.circle(surface, icon_col, (cx, cy - 4), 10)
            elif i == TOOL_BUTTERFLY:
                pygame.draw.ellipse(surface, icon_col, (cx - 10, cy - 6, 9, 12))
                pygame.draw.ellipse(surface, icon_col, (cx + 1, cy - 6, 9, 12))
                pygame.draw.rect(surface, (60, 40, 80), (cx - 1, cy - 5, 2, 10))
            elif i == TOOL_BEE:
                pygame.draw.ellipse(surface, (255, 220, 50), (cx - 7, cy - 5, 14, 10))
                pygame.draw.line(surface, BLACK, (cx - 3, cy - 5), (cx - 3, cy + 5), 1)
                pygame.draw.line(surface, BLACK, (cx + 2, cy - 5), (cx + 2, cy + 5), 1)

            # Label below icon
            txt = font.render(label, True, WHITE)
            surface.blit(txt, txt.get_rect(centerx=rect.centerx, bottom=rect.bottom - 2))

        # Clear button (top right)
        clear_font = get_font(20)
        clear_w, clear_h = 80, 50
        clear_x = WIDTH - clear_w - 12
        clear_y = 16
        self.clear_rect = pygame.Rect(clear_x, clear_y, clear_w, clear_h)
        pygame.draw.rect(surface, (200, 70, 70), self.clear_rect, border_radius=10)
        pygame.draw.rect(surface, (160, 50, 50), self.clear_rect, width=2, border_radius=10)
        txt = clear_font.render("Clear", True, WHITE)
        surface.blit(txt, txt.get_rect(center=self.clear_rect.center))

        # Item count indicator (so the user knows when garden is full)
        if len(self.items) >= MAX_ITEMS:
            full_font = get_font(22)
            full_txt = full_font.render("Garden Full!", True, (200, 60, 60))
            surface.blit(full_txt, full_txt.get_rect(center=(WIDTH // 2, 80)))
