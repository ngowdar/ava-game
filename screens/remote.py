# screens/remote.py — D-pad, Home, Back, Play/Pause with 3D buttons

import pygame
from config import WIDTH, HEIGHT, WHITE, BLACK
from ui import draw_header, draw_3d_button, get_font, PressTracker, draw_shadow, darken, brighten
import roku


class RemoteButton:
    def __init__(self, rect, color, label, roku_key, arrow_dir=None):
        self.rect = rect
        self.color = color
        self.label = label
        self.roku_key = roku_key
        self.arrow_dir = arrow_dir


class RemoteScreen:
    def __init__(self, app):
        self.app = app
        self.back_rect = None
        self.buttons = []

        cx, cy = WIDTH // 2, 320
        bw, bh = 100, 80
        gap = 8

        blue = (55, 80, 180)
        green = (50, 170, 80)
        gray = (90, 90, 110)

        self.buttons = [
            RemoteButton(pygame.Rect(cx - bw // 2, cy - bh - gap - bh, bw, bh),
                         blue, "", "Up", "up"),
            RemoteButton(pygame.Rect(cx - bw - gap - bw // 2, cy - bh // 2, bw, bh),
                         blue, "", "Left", "left"),
            RemoteButton(pygame.Rect(cx - 60, cy - bh // 2, 120, bh),
                         green, "OK", "Select", None),
            RemoteButton(pygame.Rect(cx + gap + bw // 2, cy - bh // 2, bw, bh),
                         blue, "", "Right", "right"),
            RemoteButton(pygame.Rect(cx - bw // 2, cy + gap + bh // 2, bw, bh),
                         blue, "", "Down", "down"),
        ]

        bottom_y = cy + bh + gap + bh + 50
        btn_w, btn_h = 140, 70
        total_w = 3 * btn_w + 2 * 20
        start_x = (WIDTH - total_w) // 2

        self.buttons.extend([
            RemoteButton(pygame.Rect(start_x, bottom_y, btn_w, btn_h),
                         gray, "Home", "Home", None),
            RemoteButton(pygame.Rect(start_x + btn_w + 20, bottom_y, btn_w, btn_h),
                         gray, "Play/Pause", "Play", None),
            RemoteButton(pygame.Rect(start_x + 2 * (btn_w + 20), bottom_y, btn_w, btn_h),
                         gray, "Back", "Back", None),
        ])

        self.press = PressTracker(len(self.buttons))

    def on_enter(self):
        self.press = PressTracker(len(self.buttons))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.back_rect and self.back_rect.collidepoint(pos):
                self.app.go_back()
                return
            for i, btn in enumerate(self.buttons):
                if btn.rect.collidepoint(pos):
                    self.press.trigger(i)
                    roku.send_keypress(btn.roku_key)
                    break

    def update(self, dt):
        self.press.update(dt)

    def draw(self, surface):
        surface.fill((20, 20, 50))
        self.back_rect = draw_header(surface, "REMOTE")

        for i, btn in enumerate(self.buttons):
            pressed = self.press.is_pressed(i)
            rect = btn.rect
            color = btn.color

            # Draw 3D button
            if not pressed:
                draw_shadow(surface, rect, 14, offset=3, alpha=50)

            if pressed:
                draw_rect = pygame.Rect(rect.x, rect.y + 2, rect.width, rect.height - 2)
                pygame.draw.rect(surface, darken(color, 20), draw_rect, border_radius=14)
            else:
                # Bottom edge
                bottom = pygame.Rect(rect.x, rect.y + 4, rect.width, rect.height - 2)
                pygame.draw.rect(surface, darken(color, 60), bottom, border_radius=14)
                # Face
                face = pygame.Rect(rect.x, rect.y, rect.width, rect.height - 4)
                pygame.draw.rect(surface, color, face, border_radius=14)
                # Top highlight
                hl = pygame.Surface((face.width, face.height // 3), pygame.SRCALPHA)
                pygame.draw.rect(hl, (*brighten(color, 50), 70),
                                (0, 0, face.width, face.height // 3), border_radius=14)
                surface.blit(hl, (face.x, face.y))

            cx, cy = rect.centerx, rect.centery + (2 if pressed else -1)

            if btn.arrow_dir:
                s = 16
                if btn.arrow_dir == "up":
                    points = [(cx, cy - s), (cx - s, cy + s // 2), (cx + s, cy + s // 2)]
                elif btn.arrow_dir == "down":
                    points = [(cx, cy + s), (cx - s, cy - s // 2), (cx + s, cy - s // 2)]
                elif btn.arrow_dir == "left":
                    points = [(cx - s, cy), (cx + s // 2, cy - s), (cx + s // 2, cy + s)]
                elif btn.arrow_dir == "right":
                    points = [(cx + s, cy), (cx - s // 2, cy - s), (cx - s // 2, cy + s)]
                pygame.draw.polygon(surface, WHITE, points)
            else:
                font_size = 18 if len(btn.label) > 6 else 24
                font = get_font(font_size)
                text_surf = font.render(btn.label, True, WHITE)
                text_rect = text_surf.get_rect(center=(cx, cy))
                surface.blit(text_surf, text_rect)
