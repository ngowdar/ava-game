# screens/games_menu.py — 3 game cards grid with 3D depth

import math
import pygame
from config import WIDTH, HEIGHT, SKY_BLUE, WHITE, BLACK, BUBBLE_POP, ANIMAL_SOUNDS, WHACK_A_CRITTER
from ui import draw_header, draw_3d_card, get_font, PressTracker


class GamesMenuScreen:
    def __init__(self, app):
        self.app = app
        # Top row: two cards
        self.card_bubble = pygame.Rect(30, 120, 310, 250)
        self.card_animal = pygame.Rect(380, 120, 310, 250)
        # Bottom row: one centered card
        self.card_whack = pygame.Rect(210, 410, 310, 250)
        self.cards = [self.card_bubble, self.card_animal, self.card_whack]
        self.states = [BUBBLE_POP, ANIMAL_SOUNDS, WHACK_A_CRITTER]
        self.colors = [(0, 180, 255), (255, 140, 50), (180, 50, 200)]
        self.names = ["BUBBLE POP", "ANIMAL SOUNDS", "WHACK-A-CRITTER"]
        self.back_rect = None
        self.press = PressTracker(3)
        self.pending_nav = None
        self.time = 0.0

    def on_enter(self):
        self.press = PressTracker(3)
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
        self.back_rect = draw_header(surface, "GAMES")

        icons = [self._draw_bubble_icon, self._draw_animal_icon, self._draw_whack_icon]

        for i, card in enumerate(self.cards):
            pressed = self.press.is_pressed(i)
            face = draw_3d_card(surface, card, self.colors[i], 20, pressed)

            # Icon
            icons[i](surface, face.centerx, face.y + 95, pressed)

            # Name
            font = get_font(22)
            text_surf = font.render(self.names[i], True, WHITE)
            offset_y = 2 if pressed else 0
            text_rect = text_surf.get_rect(center=(face.centerx, face.y + 195 + offset_y))
            surface.blit(text_surf, text_rect)

    def _draw_bubble_icon(self, surface, cx, cy, pressed):
        offset = 2 if pressed else 0
        cy += offset
        # Gentle bobbing
        bob = math.sin(self.time * 3) * 3
        pygame.draw.circle(surface, (100, 200, 255), (cx - 30, int(cy - 10 + bob)), 28)
        pygame.draw.circle(surface, WHITE, (cx - 40, int(cy - 20 + bob)), 8)
        pygame.draw.circle(surface, (255, 150, 200), (cx + 25, int(cy + 5 - bob)), 22)
        pygame.draw.circle(surface, WHITE, (cx + 18, int(cy - 2 - bob)), 6)
        pygame.draw.circle(surface, (150, 255, 150), (cx + 5, int(cy - 35 + bob * 0.5)), 18)
        pygame.draw.circle(surface, WHITE, (cx, int(cy - 42 + bob * 0.5)), 5)

    def _draw_animal_icon(self, surface, cx, cy, pressed):
        offset = 2 if pressed else 0
        cy += offset
        pygame.draw.circle(surface, WHITE, (cx, cy + 10), 22)
        pygame.draw.circle(surface, WHITE, (cx - 20, cy - 18), 12)
        pygame.draw.circle(surface, WHITE, (cx + 20, cy - 18), 12)
        pygame.draw.circle(surface, WHITE, (cx - 8, cy - 28), 12)
        pygame.draw.circle(surface, WHITE, (cx + 8, cy - 28), 12)

    def _draw_whack_icon(self, surface, cx, cy, pressed):
        offset = 2 if pressed else 0
        cy += offset
        # Handle
        pygame.draw.rect(surface, (180, 130, 70), (cx - 5, cy - 5, 10, 55))
        # Head
        pygame.draw.rect(surface, (120, 80, 40), (cx - 30, cy - 30, 60, 30), border_radius=6)
        # Stars
        for i in range(5):
            angle = i * (2 * math.pi / 5) - math.pi / 2 + self.time * 2
            x = cx + 35 + int(14 * math.cos(angle))
            y = cy - 25 + int(14 * math.sin(angle))
            pygame.draw.circle(surface, (255, 255, 100), (x, y), 4)
