# screens/games_menu.py — 2x3 game cards grid with 3D depth

import math
import pygame
from config import (WIDTH, HEIGHT, SKY_BLUE, WHITE, BACK_BTN_SIZE, BACK_BTN_MARGIN,
                    FINGER_PAINT, SHAPE_SORTER, MAGIC_GARDEN,
                    FIREWORKS, PARTICLE_PLAYGROUND, WEATHER_TOY)
from ui import draw_back_button, draw_3d_card, get_font, PressTracker


class GamesMenuScreen:
    def __init__(self, app):
        self.app = app

        # Full-screen 2x3 grid — maximize card size
        margin = 16
        top_y = BACK_BTN_MARGIN + BACK_BTN_SIZE + 10  # below back button
        gap_x, gap_y = 14, 14
        col_w = (WIDTH - 2 * margin - gap_x) // 2
        row_h = (HEIGHT - top_y - margin - 2 * gap_y) // 3

        self.cards = []
        for row in range(3):
            for col in range(2):
                x = margin + col * (col_w + gap_x)
                y = top_y + row * (row_h + gap_y)
                self.cards.append(pygame.Rect(x, y, col_w, row_h))

        self.states = [FINGER_PAINT, SHAPE_SORTER, MAGIC_GARDEN,
                       FIREWORKS, PARTICLE_PLAYGROUND, WEATHER_TOY]
        self.colors = [
            (255, 80, 120),   # Finger Paint - pink/red
            (80, 180, 255),   # Shape Sorter - blue
            (80, 200, 80),    # Magic Garden - green
            (255, 160, 40),   # Fireworks - orange
            (180, 60, 220),   # Particle Play - purple
            (60, 180, 200),   # Weather Toy - teal
        ]
        self.names = ["FINGER PAINT", "SHAPE SORTER", "MAGIC GARDEN",
                      "FIREWORKS", "PARTICLES", "WEATHER TOY"]
        self.icons = ["paint", "shapes", "flower", "rocket", "sparkle", "cloud"]
        self.back_rect = None
        self.press = PressTracker(6)
        self.pending_nav = None
        self.time = 0.0

    def on_enter(self):
        self.press = PressTracker(6)
        self.pending_nav = None
        self.time = 0.0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.back_rect and self.back_rect.collidepoint(pos):
                self.app.go_back()
                return
            for i, card in enumerate(self.cards):
                if card.collidepoint(pos):
                    self.press.trigger(i)
                    self.pending_nav = (self.states[i], 0.12)
                    break

    def update(self, dt):
        self.time += dt
        self.press.update(dt)
        if self.pending_nav:
            state, timer = self.pending_nav
            timer -= dt
            if timer <= 0:
                self.pending_nav = None
                self.app.go_to(state)
            else:
                self.pending_nav = (state, timer)

    def draw(self, surface):
        surface.fill(SKY_BLUE)

        for i, card in enumerate(self.cards):
            pressed = self.press.is_pressed(i)
            face = draw_3d_card(surface, card, self.colors[i], 18, pressed)

            # Draw icon — centered in upper portion of card
            cx = face.centerx
            icon_cy = face.y + face.height * 0.38
            off = 2 if pressed else 0
            self._draw_icon(surface, self.icons[i], cx, int(icon_cy) + off, face.height)

            # Name — larger font, in lower portion
            font = get_font(26)
            text_surf = font.render(self.names[i], True, WHITE)
            text_rect = text_surf.get_rect(center=(face.centerx, face.y + face.height * 0.78 + off))
            surface.blit(text_surf, text_rect)

        # Back button on top of everything
        self.back_rect = draw_back_button(surface)

    def _draw_icon(self, surface, icon, cx, cy, card_h):
        # Scale factor based on card size (larger cards = larger icons)
        s = card_h / 185.0  # normalize to original card height
        if icon == "paint":
            pygame.draw.line(surface, (255, 255, 200),
                             (cx - int(20*s), cy + int(28*s)),
                             (cx + int(14*s), cy - int(20*s)), max(3, int(8*s)))
            pygame.draw.circle(surface, WHITE, (cx + int(16*s), cy - int(24*s)), int(14*s))
            for j, col in enumerate([(255, 0, 0), (0, 200, 0), (0, 100, 255)]):
                pygame.draw.circle(surface, col,
                                   (cx - int(26*s) + int(j * 20*s), cy + int(38*s)), int(9*s))
        elif icon == "shapes":
            pygame.draw.polygon(surface, (255, 220, 80),
                                [(cx - int(34*s), cy + int(20*s)),
                                 (cx - int(12*s), cy - int(20*s)),
                                 (cx + int(8*s), cy + int(20*s))])
            pygame.draw.circle(surface, (100, 220, 255), (cx + int(28*s), cy - int(8*s)), int(16*s))
            pygame.draw.rect(surface, (255, 130, 130),
                             (cx + int(6*s), cy + int(2*s), int(28*s), int(28*s)))
        elif icon == "flower":
            for angle in range(0, 360, 72):
                rad = math.radians(angle)
                px = cx + int(20*s * math.cos(rad))
                py = cy + int(20*s * math.sin(rad))
                pygame.draw.circle(surface, (255, 180, 200), (px, py), int(13*s))
            pygame.draw.circle(surface, (255, 220, 80), (cx, cy), int(11*s))
            pygame.draw.line(surface, (80, 180, 80),
                             (cx, cy + int(20*s)), (cx, cy + int(42*s)), max(2, int(4*s)))
        elif icon == "rocket":
            pygame.draw.polygon(surface, WHITE,
                                [(cx, cy - int(35*s)),
                                 (cx - int(14*s), cy + int(8*s)),
                                 (cx + int(14*s), cy + int(8*s))])
            pygame.draw.rect(surface, (200, 200, 200),
                             (cx - int(11*s), cy + int(8*s), int(22*s), int(14*s)))
            bob = math.sin(self.time * 12) * int(4*s)
            pygame.draw.polygon(surface, (255, 160, 40),
                                [(cx - int(8*s), cy + int(22*s)),
                                 (cx, cy + int(35*s) + bob),
                                 (cx + int(8*s), cy + int(22*s))])
        elif icon == "sparkle":
            for j in range(8):
                angle = j * (math.pi / 4) + self.time * 2
                length = int((20 + math.sin(self.time * 5 + j) * 7) * s)
                x1 = cx + int(8*s * math.cos(angle))
                y1 = cy + int(8*s * math.sin(angle))
                x2 = cx + int(length * math.cos(angle))
                y2 = cy + int(length * math.sin(angle))
                col = [(255, 100, 255), (100, 200, 255), (255, 255, 100), (100, 255, 150)][j % 4]
                pygame.draw.line(surface, col, (x1, y1), (x2, y2), max(2, int(3*s)))
            pygame.draw.circle(surface, WHITE, (cx, cy), int(7*s))
        elif icon == "cloud":
            pygame.draw.circle(surface, WHITE, (cx - int(16*s), cy - int(8*s)), int(20*s))
            pygame.draw.circle(surface, WHITE, (cx + int(16*s), cy - int(8*s)), int(20*s))
            pygame.draw.circle(surface, WHITE, (cx, cy - int(20*s)), int(20*s))
            pygame.draw.rect(surface, WHITE,
                             (cx - int(28*s), cy - int(12*s), int(56*s), int(16*s)))
            for j in range(3):
                dy = (self.time * 40 + j * 15) % int(35*s)
                pygame.draw.circle(surface, (100, 180, 255),
                                   (cx - int(16*s) + int(j * 16*s), int(cy + 12*s + dy)), int(4*s))
