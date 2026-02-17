# screens/shows.py — 2-column vertically scrollable show cards + Roku launch
#   Horizontal swipe → Remote screen
#   Vertical drag → scroll
#   Card layout: show name on left (word-wrapped), image right-aligned, 3D depth

import os
import pygame
from config import WIDTH, HEIGHT, SKY_BLUE, WHITE, BLACK, SHOWS_DATA, REMOTE
from ui import draw_header, draw_3d_card, get_font, draw_wrapped_text, PressTracker
import roku


class ShowsScreen:
    # 2-column grid layout
    MARGIN = 14
    GAP_X = 12
    GAP_Y = 10
    CARD_W = (WIDTH - MARGIN * 2 - GAP_X) // 2   # ~347
    HEADER_H = 80
    GRID_TOP = HEADER_H + 10

    # Scale image to fit right side of card
    IMG_RATIO = 256 / 112
    IMG_W_IN_CARD = int(CARD_W * 0.58)
    IMG_H_IN_CARD = int(IMG_W_IN_CARD / IMG_RATIO)
    CARD_H = IMG_H_IN_CARD + 34
    IMG_PAD = 4

    def __init__(self, app):
        self.app = app
        self.back_rect = None
        self.images = {}
        self.scroll_y = 0

        # Swipe / scroll tracking
        self.touch_down_pos = None
        self.touch_prev_y = None
        self.is_scrolling = False

        # Press animation
        self.press = PressTracker(len(SHOWS_DATA))

        # Total content height
        num_rows = (len(SHOWS_DATA) + 1) // 2
        self.content_h = num_rows * self.CARD_H + (num_rows - 1) * self.GAP_Y
        self.visible_h = HEIGHT - self.GRID_TOP

        self.name_font = get_font(18)
        self.name_font_large = get_font(24)
        self.hint_font = get_font(13, bold=False)

        self._load_images()

    def _load_images(self):
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "shows")
        for i, (name, ch_id, c_id, m_type, bg_color, img_file) in enumerate(SHOWS_DATA):
            if img_file is None:
                continue
            path = os.path.join(assets_dir, img_file)
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path)
                    img = pygame.transform.smoothscale(img, (self.IMG_W_IN_CARD, self.IMG_H_IN_CARD))
                    self.images[i] = img
                except Exception:
                    pass

    def on_enter(self):
        self.scroll_y = 0
        self.press = PressTracker(len(SHOWS_DATA))

    @property
    def max_scroll(self):
        return max(0, self.content_h - self.visible_h)

    def _clamp_scroll(self):
        self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))

    def _card_rect(self, index):
        col = index % 2
        row = index // 2
        x = self.MARGIN + col * (self.CARD_W + self.GAP_X)
        y = self.GRID_TOP + row * (self.CARD_H + self.GAP_Y) - self.scroll_y
        return pygame.Rect(x, y, self.CARD_W, self.CARD_H)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            self.touch_down_pos = pos
            self.touch_prev_y = pos[1]
            self.is_scrolling = False

            if self.back_rect and self.back_rect.collidepoint(pos):
                self.app.go_back()
                self.touch_down_pos = None
                return

        elif event.type == pygame.MOUSEMOTION:
            if self.touch_down_pos is not None and self.touch_prev_y is not None:
                dy = event.pos[1] - self.touch_prev_y
                dx_total = abs(event.pos[0] - self.touch_down_pos[0])
                dy_total = abs(event.pos[1] - self.touch_down_pos[1])
                if not self.is_scrolling and dy_total > 10 and dy_total > dx_total:
                    self.is_scrolling = True
                if self.is_scrolling:
                    self.scroll_y -= dy
                    self._clamp_scroll()
                self.touch_prev_y = event.pos[1]

        elif event.type == pygame.MOUSEBUTTONUP:
            pos = event.pos
            if self.touch_down_pos is not None:
                dx = pos[0] - self.touch_down_pos[0]
                dy = pos[1] - self.touch_down_pos[1]

                if not self.is_scrolling and abs(dx) > 80 and abs(dx) > abs(dy) * 1.5:
                    if dx < 0:
                        self.app.go_to(REMOTE)
                elif not self.is_scrolling and abs(dx) < 15 and abs(dy) < 15:
                    for i in range(len(SHOWS_DATA)):
                        rect = self._card_rect(i)
                        if rect.collidepoint(pos) and rect.top >= self.HEADER_H - 10:
                            self.press.trigger(i)
                            name, channel_id, content_id, media_type, bg_color, img_file = SHOWS_DATA[i]
                            roku.launch_show(channel_id, content_id, media_type)
                            break

            self.touch_down_pos = None
            self.touch_prev_y = None
            self.is_scrolling = False

    def update(self, dt):
        self.press.update(dt)

    def draw(self, surface):
        surface.fill(SKY_BLUE)

        for i in range(len(SHOWS_DATA)):
            rect = self._card_rect(i)
            if rect.bottom < self.HEADER_H or rect.top > HEIGHT:
                continue

            name, channel_id, content_id, media_type, bg_color, img_file = SHOWS_DATA[i]
            text_color = BLACK if sum(bg_color) > 400 else WHITE
            pressed = self.press.is_pressed(i)

            face = draw_3d_card(surface, rect, bg_color, 12, pressed)
            p_off = 2 if pressed else 0

            if i in self.images:
                img = self.images[i]
                img_x = face.right - self.IMG_PAD - self.IMG_W_IN_CARD
                img_y = face.y + self.IMG_PAD
                if img_y >= self.HEADER_H - 20:
                    surface.blit(img, (img_x, img_y))

                text_area_w = face.width - self.IMG_W_IN_CARD - self.IMG_PAD * 3
                text_cx = face.x + self.IMG_PAD + text_area_w // 2
                text_cy = face.y + (self.IMG_H_IN_CARD + self.IMG_PAD * 2) // 2
                if text_cy >= self.HEADER_H:
                    draw_wrapped_text(surface, name, self.name_font, text_color,
                                      text_cx, text_cy, text_area_w - 8)
            else:
                if face.centery >= self.HEADER_H:
                    draw_wrapped_text(surface, name, self.name_font_large, text_color,
                                      face.centerx, face.centery, face.width - 20)

        # Scroll indicator
        if self.max_scroll > 0:
            bar_area_y = self.GRID_TOP
            bar_area_h = self.visible_h
            bar_h = max(30, int(bar_area_h * self.visible_h / self.content_h))
            bar_y = bar_area_y + int((bar_area_h - bar_h) * self.scroll_y / self.max_scroll)
            pygame.draw.rect(surface, (180, 180, 200), (WIDTH - 6, bar_y, 4, bar_h), border_radius=2)

        # Header
        pygame.draw.rect(surface, SKY_BLUE, (0, 0, WIDTH, self.HEADER_H))
        self.back_rect = draw_header(surface, "AVA'S SHOWS")

        # Swipe hint
        hint_surf = self.hint_font.render("swipe left for remote >", True, (100, 140, 180))
        hint_rect = hint_surf.get_rect(midright=(WIDTH - 12, HEIGHT - 14))
        surface.blit(hint_surf, hint_rect)
