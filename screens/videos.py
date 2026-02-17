# screens/videos.py — Curated YouTube videos played via mpv (no YT UI, no algorithm)
#   Videos play fullscreen on the Pi display via mpv + yt-dlp
#   No YouTube interface = no recommendations, no rabbit holes

import subprocess
import threading
import pygame
from config import WIDTH, HEIGHT, SKY_BLUE, WHITE, BLACK, VIDEOS_DATA
from ui import (draw_header, draw_3d_card, draw_3d_button, get_font,
                draw_wrapped_text, PressTracker)


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
        self.playing = False

        # Scroll tracking
        self.touch_down_pos = None
        self.touch_prev_y = None
        self.is_scrolling = False

        # Content height
        num_rows = (len(VIDEOS_DATA) + self.COLS - 1) // self.COLS
        self.content_h = num_rows * self.CARD_H + max(0, num_rows - 1) * self.GAP
        self.visible_h = HEIGHT - self.GRID_TOP

        self.title_font = get_font(22)
        self.msg_font = get_font(20, bold=False)
        self.emoji_font = get_font(48)

    def on_enter(self):
        self.scroll_y = 0
        self.press = PressTracker(max(1, len(VIDEOS_DATA)))
        self.playing = False

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

    def _play_video(self, video_id):
        """Launch mpv to play a YouTube video fullscreen. Blocks until done."""
        url = f"https://www.youtube.com/watch?v={video_id}"
        try:
            subprocess.run([
                "mpv",
                "--fs",                          # fullscreen
                "--ytdl-format=best[height<=720]",  # cap quality for Pi
                "--no-terminal",                 # no terminal output
                "--really-quiet",                # suppress messages
                "--input-default-bindings=no",   # disable keyboard shortcuts
                "--osc=no",                      # no on-screen controller
                "--cursor-autohide=0.5",
                url
            ], timeout=1800)  # 30 min max
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            pass
        self.playing = False

    def handle_event(self, event):
        if self.playing:
            return

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
                            title, video_id, bg_color = VIDEOS_DATA[i]
                            self.playing = True
                            # Run mpv in a thread so pygame loop stays alive
                            # (needed to process quit events)
                            threading.Thread(
                                target=self._play_video,
                                args=(video_id,),
                                daemon=True
                            ).start()
                            break

            self.touch_down_pos = None
            self.touch_prev_y = None
            self.is_scrolling = False

    def update(self, dt):
        self.press.update(dt)

    def draw(self, surface):
        surface.fill(SKY_BLUE)

        if len(VIDEOS_DATA) == 0:
            # Empty state
            draw_wrapped_text(surface, "No videos yet!", self.title_font, WHITE,
                              WIDTH // 2, HEIGHT // 2 - 30, WIDTH - 60)
            draw_wrapped_text(surface, "Add videos in config.py", self.msg_font,
                              (200, 220, 240), WIDTH // 2, HEIGHT // 2 + 20, WIDTH - 60)
        elif self.playing:
            # Show "playing" state while mpv is running
            draw_wrapped_text(surface, "Playing video...", self.title_font, WHITE,
                              WIDTH // 2, HEIGHT // 2 - 10, WIDTH - 60)
            draw_wrapped_text(surface, "Tap screen in video to pause",
                              self.msg_font, (200, 220, 240),
                              WIDTH // 2, HEIGHT // 2 + 30, WIDTH - 60)
        else:
            # Draw video cards
            for i in range(len(VIDEOS_DATA)):
                rect = self._card_rect(i)
                if rect.bottom < self.HEADER_H or rect.top > HEIGHT:
                    continue

                title, video_id, bg_color = VIDEOS_DATA[i]
                text_color = BLACK if sum(bg_color) > 400 else WHITE
                pressed = self.press.is_pressed(i)

                face = draw_3d_card(surface, rect, bg_color, 16, pressed)

                # Play triangle icon
                play_cx = face.x + 45
                play_cy = face.centery
                tri_size = 18
                pygame.draw.polygon(surface, (*WHITE, 180) if not pressed else WHITE, [
                    (play_cx - tri_size // 2, play_cy - tri_size),
                    (play_cx - tri_size // 2, play_cy + tri_size),
                    (play_cx + tri_size, play_cy),
                ])

                # Title (word-wrapped, to the right of play icon)
                text_cx = face.x + (face.width + 70) // 2
                text_max_w = face.width - 90
                draw_wrapped_text(surface, title, self.title_font, text_color,
                                  text_cx, face.centery, text_max_w)

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
