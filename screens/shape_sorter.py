# screens/shape_sorter.py — Shape sorting game for toddlers

import pygame
import random
import math
from config import WIDTH, HEIGHT, WHITE, BLACK
from ui import draw_back_button, get_font


# Pastel background
BG_COLOR = (230, 240, 255)

# Shape definitions: (name, color, outline_color)
SHAPE_DEFS = [
    ("circle",   (220, 50, 50),   (180, 40, 40)),
    ("square",   (50, 100, 220),  (40, 80, 180)),
    ("triangle", (240, 200, 30),  (200, 170, 20)),
    ("star",     (50, 190, 80),   (40, 150, 60)),
    ("hexagon",  (160, 60, 200),  (130, 50, 170)),
]

SHAPE_SIZE = 70  # approximate radius / half-size
SNAP_DIST = 55


def _star_points(cx, cy, outer_r, inner_r):
    """Return list of (x, y) for a 5-pointed star."""
    pts = []
    for i in range(10):
        angle = math.radians(-90 + i * 36)
        r = outer_r if i % 2 == 0 else inner_r
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return pts


def _hex_points(cx, cy, r):
    """Return list of (x, y) for a regular hexagon."""
    pts = []
    for i in range(6):
        angle = math.radians(60 * i - 30)
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return pts


def _draw_shape(surface, name, cx, cy, color, size, outline_only=False, outline_width=3):
    """Draw a shape centered at (cx, cy). If outline_only, draw just the border."""
    w = outline_width if outline_only else 0

    if name == "circle":
        pygame.draw.circle(surface, color, (int(cx), int(cy)), size, w)

    elif name == "square":
        rect = pygame.Rect(cx - size, cy - size, size * 2, size * 2)
        pygame.draw.rect(surface, color, rect, w)

    elif name == "triangle":
        pts = [
            (cx, cy - size),
            (cx - size, cy + size * 0.8),
            (cx + size, cy + size * 0.8),
        ]
        if outline_only:
            pygame.draw.polygon(surface, color, pts, w)
        else:
            pygame.draw.polygon(surface, color, pts)

    elif name == "star":
        pts = _star_points(cx, cy, size, size * 0.4)
        if outline_only:
            pygame.draw.polygon(surface, color, pts, w)
        else:
            pygame.draw.polygon(surface, color, pts)

    elif name == "hexagon":
        pts = _hex_points(cx, cy, size)
        if outline_only:
            pygame.draw.polygon(surface, color, pts, w)
        else:
            pygame.draw.polygon(surface, color, pts)


def _point_in_shape(name, px, py, cx, cy, size):
    """Simple hit test — use circle bounding for all shapes (good enough for toddler taps)."""
    dist = math.hypot(px - cx, py - cy)
    return dist <= size + 10  # small forgiveness margin


class SnapParticle:
    """Small colored circle that flies outward and fades on correct placement."""

    def __init__(self, x, y, color):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(150, 400)
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.color = color
        self.radius = random.uniform(4, 9)
        self.life = random.uniform(0.4, 0.8)
        self.max_life = self.life

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 150 * dt
        self.life -= dt

    def draw(self, surface):
        if self.life > 0:
            alpha = self.life / self.max_life
            r = max(1, int(self.radius * alpha))
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), r)


class ConfettiParticle:
    """Confetti for the celebration screen."""

    def __init__(self):
        self.x = random.uniform(0, WIDTH)
        self.y = random.uniform(-HEIGHT, 0)
        self.vx = random.uniform(-60, 60)
        self.vy = random.uniform(100, 300)
        self.color = random.choice([
            (220, 50, 50), (50, 100, 220), (240, 200, 30),
            (50, 190, 80), (160, 60, 200), (255, 140, 50),
            (255, 100, 180),
        ])
        self.size = random.randint(4, 10)
        self.rot = random.uniform(0, 360)
        self.rot_speed = random.uniform(-200, 200)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rot += self.rot_speed * dt

    def draw(self, surface):
        w = self.size
        h = int(self.size * 0.6)
        # Simple rectangle confetti
        rect_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(rect_surf, self.color, (0, 0, w, h))
        rotated = pygame.transform.rotate(rect_surf, self.rot)
        r = rotated.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated, r)


class Shape:
    """A draggable shape with snap animation state."""

    def __init__(self, name, color, outline_color, start_x, start_y, target_x, target_y):
        self.name = name
        self.color = color
        self.outline_color = outline_color
        self.start_x = start_x
        self.start_y = start_y
        self.x = start_x
        self.y = start_y
        self.target_x = target_x
        self.target_y = target_y
        self.placed = False
        self.dragging = False

        # Snap animation
        self.snap_anim = 0.0  # counts up from 0 to 0.3 when snapping
        self.snapping = False

    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
        self.placed = False
        self.dragging = False
        self.snap_anim = 0.0
        self.snapping = False

    def get_scale(self):
        """Return scale factor during snap animation (grows briefly then settles)."""
        if not self.snapping:
            return 1.0
        t = self.snap_anim / 0.3  # 0..1
        if t < 0.4:
            return 1.0 + 0.3 * (t / 0.4)  # grow to 1.3
        else:
            return 1.3 - 0.3 * ((t - 0.4) / 0.6)  # shrink back to 1.0


class ShapeSorterScreen:
    """Shape sorting game — drag shapes into their matching cutout targets."""

    def __init__(self, app):
        self.app = app
        self.shapes = []
        self.particles = []
        self.confetti = []
        self.dragged_shape = None
        self.drag_offset = (0, 0)
        self.celebrating = False
        self.celebrate_timer = 0.0
        self.back_rect = None

    def _build_shapes(self):
        """Create the 5 shapes with scattered start positions and target positions."""
        self.shapes = []
        self.particles = []
        self.confetti = []
        self.celebrating = False
        self.celebrate_timer = 0.0
        self.dragged_shape = None

        # Target positions: evenly spaced across lower portion of screen
        num = len(SHAPE_DEFS)
        spacing = WIDTH // (num + 1)
        target_y = HEIGHT - 150

        # Start positions: scattered in upper portion, avoiding back button area
        start_positions = []
        for i in range(num):
            sx = random.randint(120, WIDTH - 120)
            sy = random.randint(130, 300)
            start_positions.append((sx, sy))

        for i, (name, color, outline_color) in enumerate(SHAPE_DEFS):
            tx = spacing * (i + 1)
            ty = target_y
            sx, sy = start_positions[i]
            self.shapes.append(Shape(name, color, outline_color, sx, sy, tx, ty))

    def on_enter(self):
        self._build_shapes()

    def handle_event(self, event):
        if self.celebrating:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            # Back button
            if self.back_rect and self.back_rect.collidepoint(mx, my):
                self.app.go_back()
                return

            # Try to pick up a shape (check in reverse for top-most first)
            for shape in reversed(self.shapes):
                if shape.placed:
                    continue
                if _point_in_shape(shape.name, mx, my, shape.x, shape.y, SHAPE_SIZE):
                    shape.dragging = True
                    self.dragged_shape = shape
                    self.drag_offset = (shape.x - mx, shape.y - my)
                    # Move this shape to end of list so it draws on top
                    self.shapes.remove(shape)
                    self.shapes.append(shape)
                    break

        elif event.type == pygame.MOUSEMOTION:
            if self.dragged_shape:
                mx, my = event.pos
                self.dragged_shape.x = mx + self.drag_offset[0]
                self.dragged_shape.y = my + self.drag_offset[1]

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragged_shape:
                shape = self.dragged_shape
                shape.dragging = False
                self.dragged_shape = None

                # Check if near correct target
                dist = math.hypot(shape.x - shape.target_x, shape.y - shape.target_y)
                if dist < SNAP_DIST:
                    # Snap into place
                    shape.x = shape.target_x
                    shape.y = shape.target_y
                    shape.placed = True
                    shape.snapping = True
                    shape.snap_anim = 0.0

                    # Emit particles
                    for _ in range(12):
                        self.particles.append(
                            SnapParticle(shape.target_x, shape.target_y, shape.color)
                        )

                    # Check win
                    if all(s.placed for s in self.shapes):
                        self.celebrating = True
                        self.celebrate_timer = 2.5
                        # Spawn confetti
                        for _ in range(80):
                            self.confetti.append(ConfettiParticle())

    def update(self, dt):
        # Update snap animations
        for shape in self.shapes:
            if shape.snapping:
                shape.snap_anim += dt
                if shape.snap_anim >= 0.3:
                    shape.snap_anim = 0.3
                    shape.snapping = False

        # Update particles
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.life > 0]

        # Celebration
        if self.celebrating:
            self.celebrate_timer -= dt
            for c in self.confetti:
                c.update(dt)
            # Respawn confetti that falls off screen
            for c in self.confetti:
                if c.y > HEIGHT + 20:
                    c.y = random.uniform(-40, -10)
                    c.x = random.uniform(0, WIDTH)
                    c.vy = random.uniform(100, 300)
            if self.celebrate_timer <= 0:
                self._build_shapes()

    def draw(self, surface):
        surface.fill(BG_COLOR)

        # Draw a subtle dividing line between upper and lower halves
        divider_y = HEIGHT // 2 + 20
        pygame.draw.line(surface, (200, 210, 230), (30, divider_y), (WIDTH - 30, divider_y), 2)

        # Label areas
        font_sm = get_font(20)
        label = font_sm.render("drag shapes down to match!", True, (140, 150, 170))
        surface.blit(label, label.get_rect(center=(WIDTH // 2, divider_y - 15)))

        # Draw target cutouts (outlined shapes in lower area)
        for shape in self.shapes:
            _draw_shape(
                surface, shape.name,
                shape.target_x, shape.target_y,
                shape.outline_color, SHAPE_SIZE,
                outline_only=True, outline_width=3,
            )
            # Draw a dashed inner hint (smaller dotted outline)
            _draw_shape(
                surface, shape.name,
                shape.target_x, shape.target_y,
                (*shape.outline_color[:3],),
                SHAPE_SIZE - 6,
                outline_only=True, outline_width=1,
            )

        # Draw shapes (non-placed first, then placed, then dragged on top)
        for shape in self.shapes:
            if shape.dragging:
                continue  # draw last
            scale = shape.get_scale()
            sz = int(SHAPE_SIZE * scale)
            if shape.placed:
                _draw_shape(surface, shape.name, shape.x, shape.y, shape.color, sz)
            else:
                # Draw a slight shadow under movable shapes
                shadow_color = (180, 180, 200)
                _draw_shape(surface, shape.name, shape.x + 3, shape.y + 3, shadow_color, SHAPE_SIZE)
                _draw_shape(surface, shape.name, shape.x, shape.y, shape.color, SHAPE_SIZE)

        # Draw currently dragged shape on top with slight enlargement
        if self.dragged_shape:
            s = self.dragged_shape
            _draw_shape(surface, s.name, s.x + 3, s.y + 3, (160, 160, 180), SHAPE_SIZE + 4)
            _draw_shape(surface, s.name, s.x, s.y, s.color, SHAPE_SIZE + 4)

        # Draw particles
        for p in self.particles:
            p.draw(surface)

        # Celebration overlay
        if self.celebrating:
            # Semi-transparent overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 100))
            surface.blit(overlay, (0, 0))

            # Confetti
            for c in self.confetti:
                c.draw(surface)

            # "YAY!" text with pulsing scale
            pulse = 1.0 + 0.1 * math.sin(self.celebrate_timer * 8)
            yay_font = get_font(int(100 * pulse))
            # Shadow
            shadow = yay_font.render("YAY!", True, (0, 0, 0))
            shadow.set_alpha(80)
            sr = shadow.get_rect(center=(WIDTH // 2 + 3, HEIGHT // 2 + 3))
            surface.blit(shadow, sr)
            # Main text with rainbow-ish color cycle
            hue_shift = (self.celebrate_timer * 200) % 360
            r = int(127 + 127 * math.sin(math.radians(hue_shift)))
            g = int(127 + 127 * math.sin(math.radians(hue_shift + 120)))
            b = int(127 + 127 * math.sin(math.radians(hue_shift + 240)))
            yay_surf = yay_font.render("YAY!", True, (r, g, b))
            yr = yay_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            surface.blit(yay_surf, yr)

        # Back button (always on top)
        self.back_rect = draw_back_button(surface)
