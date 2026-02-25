# screens/finger_paint.py — Finger painting game for toddlers

import math
import pygame
from config import WIDTH, HEIGHT, WHITE, BLACK
from ui import draw_back_button, get_font, BACK_BTN_SIZE, BACK_BTN_MARGIN

# Palette colors
PALETTE = [
    (220, 30, 30),     # red
    (255, 140, 0),     # orange
    (255, 220, 0),     # yellow
    (30, 180, 50),     # green
    (30, 100, 220),    # blue
    (130, 40, 200),    # purple
    (255, 100, 180),   # pink
    (255, 255, 255),   # white
]

# Brush sizes
BRUSH_SIZES = [6, 14, 24]

# Layout constants
TOOLBAR_HEIGHT = 90          # bottom toolbar area
TOOLBAR_Y = HEIGHT - TOOLBAR_HEIGHT
SWATCH_SIZE = 60
SWATCH_PAD = 6
BRUSH_BTN_SIZE = 40
STAMP_BTN_SIZE = 56
CLEAR_BTN_W = 90
CLEAR_BTN_H = 44


class FingerPaintScreen:
    def __init__(self, app):
        self.app = app
        self.canvas = pygame.Surface((WIDTH, HEIGHT))
        self.drawing = False
        self.last_pos = None
        self.color = PALETTE[4]       # start with blue
        self.brush_size = BRUSH_SIZES[1]  # medium
        self.brush_index = 1
        self.stamp_mode = None        # None, "star", "heart", "paw"

    # ------------------------------------------------------------------ #
    def on_enter(self):
        """Reset canvas to white."""
        self.canvas.fill(WHITE)
        self.drawing = False
        self.last_pos = None
        self.color = PALETTE[4]
        self.brush_size = BRUSH_SIZES[1]
        self.brush_index = 1
        self.stamp_mode = None

    # ------------------------------------------------------------------ #
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            # --- Back button ---
            back_rect = pygame.Rect(BACK_BTN_MARGIN, BACK_BTN_MARGIN,
                                    BACK_BTN_SIZE, BACK_BTN_SIZE)
            if back_rect.collidepoint(mx, my):
                self.app.go_back()
                return

            # --- Clear button (top-right) ---
            clear_rect = self._clear_rect()
            if clear_rect.collidepoint(mx, my):
                self.canvas.fill(WHITE)
                return

            # --- Toolbar hit test ---
            if my >= TOOLBAR_Y:
                self._handle_toolbar_tap(mx, my)
                return

            # --- Canvas drawing / stamping ---
            if my < TOOLBAR_Y:
                if self.stamp_mode:
                    self._draw_stamp(mx, my)
                else:
                    self.drawing = True
                    self.last_pos = (mx, my)
                    pygame.draw.circle(self.canvas, self.color,
                                       (mx, my), self.brush_size)

        elif event.type == pygame.MOUSEMOTION and self.drawing:
            mx, my = event.pos
            if my < TOOLBAR_Y:
                pygame.draw.circle(self.canvas, self.color,
                                   (mx, my), self.brush_size)
                if self.last_pos:
                    pygame.draw.line(self.canvas, self.color,
                                    self.last_pos, (mx, my),
                                    self.brush_size * 2)
                self.last_pos = (mx, my)
            else:
                self.last_pos = None

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.drawing = False
            self.last_pos = None

    # ------------------------------------------------------------------ #
    def update(self, dt):
        pass  # no animations needed

    # ------------------------------------------------------------------ #
    def draw(self, surface):
        # Blit the persistent canvas
        surface.blit(self.canvas, (0, 0))

        # --- Toolbar background ---
        toolbar_bg = pygame.Surface((WIDTH, TOOLBAR_HEIGHT), pygame.SRCALPHA)
        toolbar_bg.fill((40, 40, 40, 220))
        surface.blit(toolbar_bg, (0, TOOLBAR_Y))

        # --- Color palette ---
        self._draw_palette(surface)

        # --- Brush size buttons ---
        self._draw_brush_buttons(surface)

        # --- Stamp buttons ---
        self._draw_stamp_buttons(surface)

        # --- Clear button ---
        self._draw_clear_button(surface)

        # --- Back button ---
        draw_back_button(surface)

    # ================================================================== #
    #  TOOLBAR: palette, brushes, stamps                                  #
    # ================================================================== #

    def _draw_palette(self, surface):
        """Draw 8 color swatches along the bottom-left."""
        start_x = SWATCH_PAD
        y = TOOLBAR_Y + (TOOLBAR_HEIGHT - SWATCH_SIZE) // 2
        for i, col in enumerate(PALETTE):
            x = start_x + i * (SWATCH_SIZE + SWATCH_PAD)
            rect = pygame.Rect(x, y, SWATCH_SIZE, SWATCH_SIZE)
            pygame.draw.rect(surface, col, rect, border_radius=8)
            # Outline for white swatch visibility
            pygame.draw.rect(surface, (160, 160, 160), rect, width=2, border_radius=8)
            # Selection indicator
            if col == self.color and self.stamp_mode is None:
                pygame.draw.rect(surface, WHITE, rect.inflate(6, 6),
                                 width=3, border_radius=10)

    def _draw_brush_buttons(self, surface):
        """Draw 3 brush size circles after the palette."""
        palette_end_x = SWATCH_PAD + 8 * (SWATCH_SIZE + SWATCH_PAD) + 10
        cy = TOOLBAR_Y + TOOLBAR_HEIGHT // 2
        for i, sz in enumerate(BRUSH_SIZES):
            cx = palette_end_x + i * (BRUSH_BTN_SIZE + 8) + BRUSH_BTN_SIZE // 2
            # Background circle
            pygame.draw.circle(surface, (80, 80, 80), (cx, cy), BRUSH_BTN_SIZE // 2)
            # Brush preview dot
            pygame.draw.circle(surface, WHITE, (cx, cy), sz // 2)
            # Selection ring
            if i == self.brush_index and self.stamp_mode is None:
                pygame.draw.circle(surface, (0, 220, 255), (cx, cy),
                                   BRUSH_BTN_SIZE // 2 + 3, width=3)

    def _draw_stamp_buttons(self, surface):
        """Draw star, heart, paw stamp buttons."""
        stamps = ["star", "heart", "paw"]
        labels = ["\u2605", "\u2665", "\u25C9"]  # unicode fallbacks
        base_x = SWATCH_PAD + 8 * (SWATCH_SIZE + SWATCH_PAD) + 10 + 3 * (BRUSH_BTN_SIZE + 8) + 12
        cy = TOOLBAR_Y + TOOLBAR_HEIGHT // 2
        for i, stamp in enumerate(stamps):
            cx = base_x + i * (STAMP_BTN_SIZE + 6) + STAMP_BTN_SIZE // 2
            rect = pygame.Rect(cx - STAMP_BTN_SIZE // 2, cy - STAMP_BTN_SIZE // 2,
                               STAMP_BTN_SIZE, STAMP_BTN_SIZE)
            bg = (100, 60, 160) if self.stamp_mode == stamp else (70, 70, 70)
            pygame.draw.rect(surface, bg, rect, border_radius=10)
            if self.stamp_mode == stamp:
                pygame.draw.rect(surface, (200, 140, 255), rect, width=3, border_radius=10)
            # Draw the stamp icon preview
            self._draw_stamp_icon(surface, stamp, cx, cy, 16, WHITE)

    def _draw_clear_button(self, surface):
        """Draw the clear button top-right."""
        rect = self._clear_rect()
        pygame.draw.rect(surface, (200, 50, 50), rect, border_radius=12)
        pygame.draw.rect(surface, (255, 100, 100), rect, width=2, border_radius=12)
        font = get_font(22)
        txt = font.render("CLEAR", True, WHITE)
        surface.blit(txt, txt.get_rect(center=rect.center))

    def _clear_rect(self):
        return pygame.Rect(WIDTH - CLEAR_BTN_W - 12, 16, CLEAR_BTN_W, CLEAR_BTN_H)

    # ================================================================== #
    #  TOOLBAR TAP HANDLING                                               #
    # ================================================================== #

    def _handle_toolbar_tap(self, mx, my):
        """Route a tap in the toolbar area to palette / brush / stamp."""
        # Palette swatches
        start_x = SWATCH_PAD
        sy = TOOLBAR_Y + (TOOLBAR_HEIGHT - SWATCH_SIZE) // 2
        for i, col in enumerate(PALETTE):
            x = start_x + i * (SWATCH_SIZE + SWATCH_PAD)
            rect = pygame.Rect(x, sy, SWATCH_SIZE, SWATCH_SIZE)
            if rect.collidepoint(mx, my):
                self.color = col
                self.stamp_mode = None
                return

        # Brush sizes
        palette_end_x = SWATCH_PAD + 8 * (SWATCH_SIZE + SWATCH_PAD) + 10
        cy = TOOLBAR_Y + TOOLBAR_HEIGHT // 2
        for i in range(3):
            cx = palette_end_x + i * (BRUSH_BTN_SIZE + 8) + BRUSH_BTN_SIZE // 2
            if math.hypot(mx - cx, my - cy) <= BRUSH_BTN_SIZE // 2 + 4:
                self.brush_index = i
                self.brush_size = BRUSH_SIZES[i]
                self.stamp_mode = None
                return

        # Stamps
        stamps = ["star", "heart", "paw"]
        base_x = palette_end_x + 3 * (BRUSH_BTN_SIZE + 8) + 12
        for i, stamp in enumerate(stamps):
            cx = base_x + i * (STAMP_BTN_SIZE + 6) + STAMP_BTN_SIZE // 2
            rect = pygame.Rect(cx - STAMP_BTN_SIZE // 2, cy - STAMP_BTN_SIZE // 2,
                               STAMP_BTN_SIZE, STAMP_BTN_SIZE)
            if rect.collidepoint(mx, my):
                # Toggle: tap same stamp to deselect
                self.stamp_mode = stamp if self.stamp_mode != stamp else None
                return

    # ================================================================== #
    #  STAMPS — drawn with pygame.draw primitives                         #
    # ================================================================== #

    def _draw_stamp(self, x, y):
        """Draw the selected stamp onto the canvas at (x, y)."""
        if self.stamp_mode == "star":
            self._draw_stamp_icon(self.canvas, "star", x, y, 30, self.color)
        elif self.stamp_mode == "heart":
            self._draw_stamp_icon(self.canvas, "heart", x, y, 30, self.color)
        elif self.stamp_mode == "paw":
            self._draw_stamp_icon(self.canvas, "paw", x, y, 30, self.color)

    def _draw_stamp_icon(self, surface, kind, cx, cy, size, color):
        """Render a stamp icon centered at (cx, cy) with given size."""
        if kind == "star":
            self._draw_star(surface, cx, cy, size, color)
        elif kind == "heart":
            self._draw_heart(surface, cx, cy, size, color)
        elif kind == "paw":
            self._draw_paw(surface, cx, cy, size, color)

    def _draw_star(self, surface, cx, cy, size, color):
        """Draw a 5-pointed star."""
        points = []
        for i in range(10):
            angle = math.radians(i * 36 - 90)
            r = size if i % 2 == 0 else size * 0.4
            points.append((cx + r * math.cos(angle),
                           cy + r * math.sin(angle)))
        pygame.draw.polygon(surface, color, points)

    def _draw_heart(self, surface, cx, cy, size, color):
        """Draw a heart shape using circles and a triangle."""
        r = int(size * 0.5)
        # Two circles for the top bumps
        pygame.draw.circle(surface, color, (cx - r // 2, cy - r // 3), r)
        pygame.draw.circle(surface, color, (cx + r // 2, cy - r // 3), r)
        # Triangle for the bottom point
        pygame.draw.polygon(surface, color, [
            (cx - size, cy - r // 6),
            (cx + size, cy - r // 6),
            (cx, cy + size),
        ])

    def _draw_paw(self, surface, cx, cy, size, color):
        """Draw a paw print: one big pad + 4 toe beans."""
        # Main pad (ellipse approximated with a larger circle)
        pad_r = int(size * 0.45)
        pygame.draw.circle(surface, color, (cx, cy + int(size * 0.15)), pad_r)
        # Four toes
        toe_r = int(size * 0.22)
        offsets = [
            (-size * 0.42, -size * 0.35),
            (-size * 0.13, -size * 0.55),
            (size * 0.13, -size * 0.55),
            (size * 0.42, -size * 0.35),
        ]
        for ox, oy in offsets:
            pygame.draw.circle(surface, color,
                               (int(cx + ox), int(cy + oy)), toe_r)
