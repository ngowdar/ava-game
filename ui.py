# ui.py — Shared UI helpers for Ava's Game Box

import os
import math
import pygame
from config import WHITE, BLACK, BACK_BTN_SIZE, BACK_BTN_MARGIN, WIDTH

# Font paths — DejaVu Sans Bold is pre-installed on Raspberry Pi OS.
_FONT_BOLD_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
_FONT_REG_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# Cached fonts
_font_cache = {}


def get_font(size, bold=True):
    """Get DejaVu Sans font at given size, with fallback to pygame default."""
    key = (size, bold)
    if key not in _font_cache:
        path = _FONT_BOLD_PATH if bold else _FONT_REG_PATH
        if os.path.exists(path):
            _font_cache[key] = pygame.font.Font(path, size)
        else:
            _font_cache[key] = pygame.font.Font(None, size + 6)
    return _font_cache[key]


def wrap_text(text, font, max_width):
    """Word-wrap text to fit within max_width. Returns list of lines."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines if lines else [text]


def draw_wrapped_text(surface, text, font, color, center_x, center_y, max_width):
    """Draw word-wrapped text centered at (center_x, center_y)."""
    lines = wrap_text(text, font, max_width)
    line_height = font.get_linesize()
    total_h = line_height * len(lines)
    start_y = center_y - total_h // 2

    for i, line in enumerate(lines):
        text_surf = font.render(line, True, color)
        text_rect = text_surf.get_rect(center=(center_x, start_y + i * line_height + line_height // 2))
        surface.blit(text_surf, text_rect)


def hsv_to_rgb(h, s, v):
    """Convert HSV (h: 0-360, s: 0-1, v: 0-1) to RGB tuple (0-255)."""
    h = h % 360
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))


def darken(color, amount=40):
    """Return a darker version of a color."""
    return tuple(max(0, c - amount) for c in color[:3])


def brighten(color, amount=40):
    """Return a brighter version of a color."""
    return tuple(min(255, c + amount) for c in color[:3])


def draw_shadow(surface, rect, radius=20, offset=4, alpha=60):
    """Draw a soft drop shadow beneath a rect."""
    shadow = pygame.Surface((rect.width + offset * 2, rect.height + offset * 2), pygame.SRCALPHA)
    shadow_rect = pygame.Rect(offset, offset, rect.width, rect.height)
    pygame.draw.rect(shadow, (0, 0, 0, alpha), shadow_rect, border_radius=radius)
    surface.blit(shadow, (rect.x - offset + offset, rect.y - offset + offset + 3))


def draw_rounded_rect(surface, color, rect, radius=20):
    """Draw a filled rounded rectangle."""
    pygame.draw.rect(surface, color, rect, border_radius=radius)


def draw_3d_button(surface, text, rect, color, text_color=WHITE, font_size=32,
                   radius=20, pressed=False, shadow=True):
    """Draw a button with 3D depth effect — highlight on top, shadow on bottom."""
    if shadow and not pressed:
        draw_shadow(surface, rect, radius, offset=4, alpha=50)

    if pressed:
        # Pressed: shift down 2px, flatten
        draw_rect = pygame.Rect(rect.x, rect.y + 2, rect.width, rect.height - 2)
        pygame.draw.rect(surface, darken(color, 30), draw_rect, border_radius=radius)
        # Subtle inner shadow at top
        pygame.draw.rect(surface, darken(color, 50),
                        pygame.Rect(draw_rect.x, draw_rect.y, draw_rect.width, 4),
                        border_radius=radius)
    else:
        # Bottom edge (dark)
        bottom_rect = pygame.Rect(rect.x, rect.y + 4, rect.width, rect.height - 2)
        pygame.draw.rect(surface, darken(color, 60), bottom_rect, border_radius=radius)
        # Main face
        face_rect = pygame.Rect(rect.x, rect.y, rect.width, rect.height - 4)
        pygame.draw.rect(surface, color, face_rect, border_radius=radius)
        # Top highlight
        highlight = pygame.Surface((face_rect.width, face_rect.height // 3), pygame.SRCALPHA)
        pygame.draw.rect(highlight, (*brighten(color, 50), 80),
                        (0, 0, face_rect.width, face_rect.height // 3),
                        border_radius=radius)
        surface.blit(highlight, (face_rect.x, face_rect.y))

    # Text
    font = get_font(font_size)
    text_surf = font.render(text, True, text_color)
    offset_y = 2 if pressed else 0
    text_rect = text_surf.get_rect(center=(rect.centerx, rect.centery + offset_y - (0 if pressed else 2)))
    surface.blit(text_surf, text_rect)


def draw_3d_card(surface, rect, color, radius=16, pressed=False):
    """Draw a card with 3D depth effect. Returns the face rect for content placement."""
    if not pressed:
        draw_shadow(surface, rect, radius, offset=3, alpha=45)

    if pressed:
        draw_rect = pygame.Rect(rect.x + 1, rect.y + 2, rect.width - 2, rect.height - 2)
        pygame.draw.rect(surface, darken(color, 20), draw_rect, border_radius=radius)
        return draw_rect
    else:
        # Bottom edge
        bottom_rect = pygame.Rect(rect.x, rect.y + 3, rect.width, rect.height - 1)
        pygame.draw.rect(surface, darken(color, 50), bottom_rect, border_radius=radius)
        # Main face
        face_rect = pygame.Rect(rect.x, rect.y, rect.width, rect.height - 3)
        pygame.draw.rect(surface, color, face_rect, border_radius=radius)
        # Subtle top highlight
        hl_h = max(4, face_rect.height // 5)
        highlight = pygame.Surface((face_rect.width, hl_h), pygame.SRCALPHA)
        pygame.draw.rect(highlight, (*brighten(color, 40), 60),
                        (0, 0, face_rect.width, hl_h),
                        border_radius=radius)
        surface.blit(highlight, (face_rect.x, face_rect.y))
        # Thin bright border at top
        pygame.draw.rect(surface, brighten(color, 30), face_rect, width=1, border_radius=radius)
        return face_rect


def draw_back_button(surface):
    """Draw a semi-transparent back button (top-left circle with '<' arrow).
    Returns the rect for hit-testing."""
    x = BACK_BTN_MARGIN
    y = BACK_BTN_MARGIN
    size = BACK_BTN_SIZE

    # Shadow
    shadow = pygame.Surface((size + 4, size + 4), pygame.SRCALPHA)
    pygame.draw.circle(shadow, (0, 0, 0, 40), (size // 2 + 2, size // 2 + 4), size // 2)
    surface.blit(shadow, (x - 2, y - 2))

    # Button circle
    btn_surface = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(btn_surface, (0, 0, 0, 140), (size // 2, size // 2), size // 2)
    # Highlight arc at top
    pygame.draw.circle(btn_surface, (255, 255, 255, 30), (size // 2, size // 2 - 4), size // 2 - 2)
    pygame.draw.circle(btn_surface, (0, 0, 0, 140), (size // 2, size // 2 + 2), size // 2 - 6)
    surface.blit(btn_surface, (x, y))

    # Arrow '<'
    cx, cy = x + size // 2, y + size // 2
    arrow_size = 12
    pygame.draw.lines(surface, WHITE, False, [
        (cx + arrow_size // 2, cy - arrow_size),
        (cx - arrow_size // 2, cy),
        (cx + arrow_size // 2, cy + arrow_size),
    ], 3)

    return pygame.Rect(x, y, size, size)


def draw_header(surface, title, bg_color=None):
    """Draw a header bar with back button and title. Returns back button rect."""
    if bg_color:
        pygame.draw.rect(surface, bg_color, (0, 0, WIDTH, 80))

    back_rect = draw_back_button(surface)

    font = get_font(36)
    # Text shadow
    shadow_surf = font.render(title, True, (0, 0, 0))
    shadow_rect = shadow_surf.get_rect(center=(WIDTH // 2 + 2, 47))
    shadow_surf.set_alpha(60)
    surface.blit(shadow_surf, shadow_rect)
    # Text
    text_surf = font.render(title, True, WHITE)
    text_rect = text_surf.get_rect(center=(WIDTH // 2, 45))
    surface.blit(text_surf, text_rect)

    return back_rect


# --- Animation helper ---

class PressTracker:
    """Track press states for a list of buttons/cards for animation."""

    def __init__(self, count):
        self.press_timers = [0.0] * count  # >0 means animating press
        self.pressed = [False] * count

    def trigger(self, index):
        self.press_timers[index] = 0.15
        self.pressed[index] = True

    def update(self, dt):
        for i in range(len(self.press_timers)):
            if self.press_timers[i] > 0:
                self.press_timers[i] -= dt
                if self.press_timers[i] <= 0:
                    self.press_timers[i] = 0
                    self.pressed[i] = False

    def is_pressed(self, index):
        return self.pressed[index]

    def get_scale(self, index):
        """Return scale factor (1.0 normal, dips to ~0.95 on press, bounces back)."""
        t = self.press_timers[index]
        if t <= 0:
            return 1.0
        progress = 1.0 - (t / 0.15)
        if progress < 0.4:
            return 1.0 - 0.06 * (progress / 0.4)
        else:
            return 0.94 + 0.06 * ((progress - 0.4) / 0.6)


class ScrollToolbar:
    """Horizontally scrollable toolbar for button strips that exceed screen width.

    Usage:
        toolbar = ScrollToolbar(left_x=110, y=10, height=60, btn_width=130,
                                btn_gap=8, btn_count=5)
        # In handle_event: toolbar.handle_event(event)
        # In update:       toolbar.update(dt)
        # In draw:         toolbar.draw_begin(surface) -> draw buttons -> toolbar.draw_end(surface)
        # Hit test:        toolbar.get_btn_at(pos) -> index or -1
    """

    def __init__(self, left_x, y, height, btn_width, btn_gap, btn_count):
        self.left_x = left_x
        self.y = y
        self.height = height
        self.btn_width = btn_width
        self.btn_gap = btn_gap
        self.btn_count = btn_count
        self.scroll_x = 0.0
        self._dragging = False
        self._drag_start_x = 0
        self._drag_start_scroll = 0.0
        self._velocity = 0.0
        self._last_mx = 0
        self._was_drag = False  # true if finger moved enough to be a drag, not a tap

        total_content = btn_count * btn_width + (btn_count - 1) * btn_gap
        visible = WIDTH - left_x
        self.max_scroll = max(0, total_content - visible + 10)

    def get_btn_rects(self):
        """Return list of pygame.Rects for each button (scrolled positions)."""
        rects = []
        for i in range(self.btn_count):
            x = self.left_x + i * (self.btn_width + self.btn_gap) - self.scroll_x
            rects.append(pygame.Rect(int(x), self.y, self.btn_width, self.height))
        return rects

    def handle_event(self, event):
        """Handle touch events for scrolling. Returns True if event was consumed."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if self.y <= my <= self.y + self.height and mx >= self.left_x:
                self._dragging = True
                self._drag_start_x = mx
                self._drag_start_scroll = self.scroll_x
                self._last_mx = mx
                self._was_drag = False
                self._velocity = 0.0
                return True

        elif event.type == pygame.MOUSEMOTION and self._dragging:
            mx, my = event.pos
            dx = self._drag_start_x - mx
            if abs(dx) > 8:
                self._was_drag = True
            self.scroll_x = self._drag_start_scroll + dx
            self.scroll_x = max(0, min(self.max_scroll, self.scroll_x))
            self._velocity = (self._last_mx - mx) * 4
            self._last_mx = mx
            return True

        elif event.type == pygame.MOUSEBUTTONUP and self._dragging:
            self._dragging = False
            return self._was_drag  # consume if it was a drag, not a tap

        return False

    def update(self, dt):
        """Apply momentum scrolling."""
        if not self._dragging and abs(self._velocity) > 1:
            self.scroll_x += self._velocity * dt
            self.scroll_x = max(0, min(self.max_scroll, self.scroll_x))
            self._velocity *= 0.9  # friction

    def get_btn_at(self, pos):
        """Return button index at pos, or -1. Only valid if not a drag gesture."""
        if self._was_drag:
            return -1
        mx, my = pos
        if not (self.y <= my <= self.y + self.height):
            return -1
        for i, rect in enumerate(self.get_btn_rects()):
            if rect.collidepoint(mx, my):
                return i
        return -1

    def needs_scroll(self):
        """Return True if content exceeds visible area."""
        return self.max_scroll > 0

    def draw_scroll_hint(self, surface):
        """Draw subtle scroll indicators if there's more content."""
        if self.max_scroll <= 0:
            return
        # Right fade hint
        if self.scroll_x < self.max_scroll - 5:
            for i in range(20):
                alpha = int(80 * (1 - i / 20))
                x = WIDTH - 20 + i
                pygame.draw.line(surface, (0, 0, 0),
                                 (x, self.y), (x, self.y + self.height))
        # Left fade hint
        if self.scroll_x > 5:
            for i in range(20):
                alpha = int(80 * (i / 20))
                x = self.left_x + i
                pygame.draw.line(surface, (0, 0, 0),
                                 (x, self.y), (x, self.y + self.height))
