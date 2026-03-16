# screens/videos.py — Curated YouTube videos launched via Roku YouTube app
#   Tap a card → launches video on the TV via Roku deep link
#   Cards show thumbnail + title overlay

import os
import pygame
from config import WIDTH, HEIGHT, SKY_BLUE, WHITE, BLACK, VIDEOS_DATA, YOUTUBE_CHANNEL_ID
from ui import (draw_header, draw_3d_card, get_font,
                draw_wrapped_text, PressTracker)
import roku


class VideosScreen:
    MARGIN = 20
    GAP = 16
    COLS = 2
    CARD_W = (WIDTH - MARGIN * 2 - GAP * (2 - 1)) // 2   # ~342
    CARD_H = 140
    HEADER_H = 80
    GRID_TOP = HEADER_H + 10

    def __init__(self, app):
        self.app = app
        self.back_rect = None
        self.press = PressTracker(max(1, len(VIDEOS_DATA)))
        self.scroll_y = 0

        # Scroll tracking
        self.touch_down_pos = None
        self.touch_prev_y = None
        self.is_scrolling = False

        # Content height
        num_rows = (len(VIDEOS_DATA) + self.COLS - 1) // self.COLS
        self.content_h = num_rows * self.CARD_H + max(0, num_rows - 1) * self.GAP
        self.visible_h = HEIGHT - self.GRID_TOP

        self.title_font = get_font(18)
        self.msg_font = get_font(20, bold=False)

        # Load thumbnails
        self.thumbnails = {}
        self._load_thumbnails()

    def _load_thumbnails(self):
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                  "assets", "videos")
        for i, entry in enumerate(VIDEOS_DATA):
            img_file = entry[3] if len(entry) > 3 else None
            if not img_file:
                continue
            path = os.path.join(assets_dir, img_file)
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path)
                    # Scale to fill the card area
                    img = pygame.transform.smoothscale(img, (self.CARD_W, self.CARD_H))
                    self.thumbnails[i] = img
                except Exception:
                    pass

    def on_enter(self):
        self.scroll_y = 0
        self.press = PressTracker(max(1, len(VIDEOS_DATA)))

    @property
    def max_scroll(self):
        return max(0, self.content_h - self.visible_h)

    def _clamp_scroll(self):
        self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))

    def _card_rect(self, index):
        col = index % self.COLS
        row = index // self.COLS
        x = self.MARGIN + col * (self.CARD_W + self.GAP)
        y = self.GRID_TOP + row * (self.CARD_H + self.GAP) - self.scroll_y
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

                if not self.is_scrolling and abs(dx) < 15 and abs(dy) < 15:
                    for i in range(len(VIDEOS_DATA)):
                        rect = self._card_rect(i)
                        if rect.collidepoint(pos) and rect.top >= self.HEADER_H - 10:
                            self.press.trigger(i)
                            video_id = VIDEOS_DATA[i][1]
                            roku.launch_show(YOUTUBE_CHANNEL_ID, video_id, "movie")
                            break

            self.touch_down_pos = None
            self.touch_prev_y = None
            self.is_scrolling = False

    def update(self, dt):
        self.press.update(dt)

    def draw(self, surface):
        surface.fill(SKY_BLUE)

        if len(VIDEOS_DATA) == 0:
            draw_wrapped_text(surface, "No videos yet!", self.title_font, WHITE,
                              WIDTH // 2, HEIGHT // 2 - 30, WIDTH - 60)
            draw_wrapped_text(surface, "Add videos in config.py", self.msg_font,
                              (200, 220, 240), WIDTH // 2, HEIGHT // 2 + 20, WIDTH - 60)
        else:
            for i in range(len(VIDEOS_DATA)):
                rect = self._card_rect(i)
                if rect.bottom < self.HEADER_H or rect.top > HEIGHT:
                    continue

                title, video_id, bg_color = VIDEOS_DATA[i][0], VIDEOS_DATA[i][1], VIDEOS_DATA[i][2]
                pressed = self.press.is_pressed(i)

                if i in self.thumbnails:
                    # Draw thumbnail card with 3D depth
                    face = draw_3d_card(surface, rect, bg_color, 16, pressed)

                    # Blit thumbnail clipped to card face
                    thumb = self.thumbnails[i]
                    thumb_rect = thumb.get_rect()
                    thumb_rect.topleft = (face.x, face.y)
                    # Clip to face area
                    clip = surface.get_clip()
                    surface.set_clip(face)
                    surface.blit(thumb, thumb_rect)
                    surface.set_clip(clip)

                    # Dark gradient overlay at bottom for text
                    grad_h = 50
                    grad = pygame.Surface((face.width, grad_h), pygame.SRCALPHA)
                    for y in range(grad_h):
                        alpha = int(180 * (y / grad_h))
                        pygame.draw.line(grad, (0, 0, 0, alpha),
                                        (0, y), (face.width, y))
                    surface.blit(grad, (face.x, face.bottom - grad_h))

                    # Title at bottom of thumbnail
                    label = self.title_font.render(title, True, WHITE)
                    label_rect = label.get_rect(
                        midbottom=(face.centerx, face.bottom - 6))
                    surface.blit(label, label_rect)
                else:
                    # Fallback: colored card with text
                    face = draw_3d_card(surface, rect, bg_color, 16, pressed)
                    text_color = BLACK if sum(bg_color) > 400 else WHITE
                    draw_wrapped_text(surface, title, self.title_font, text_color,
                                      face.centerx, face.centery, face.width - 20)

            # Scroll indicator
            if self.max_scroll > 0:
                bar_area_h = self.visible_h
                bar_h = max(30, int(bar_area_h * self.visible_h / self.content_h))
                bar_y = self.GRID_TOP + int((bar_area_h - bar_h) * self.scroll_y / self.max_scroll)
                pygame.draw.rect(surface, (180, 180, 200),
                                (WIDTH - 6, bar_y, 4, bar_h), border_radius=2)

        # Header (always on top)
        pygame.draw.rect(surface, SKY_BLUE, (0, 0, WIDTH, self.HEADER_H))
        self.back_rect = draw_header(surface, "COOL VIDEOS")
