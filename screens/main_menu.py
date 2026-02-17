# screens/main_menu.py — "AVA" title with floating stars/hearts + 3 buttons

import math
import random
import pygame
from config import WIDTH, HEIGHT, SKY_BLUE, WHITE, GREEN, ORANGE, GAMES_MENU, SHOWS, VIDEOS
from ui import draw_3d_button, get_font, PressTracker


PURPLE = (156, 39, 176)


class FloatingShape:
    """A star or heart that drifts gently across the screen."""
    SHAPES = ["star", "heart", "circle"]

    def __init__(self):
        self.reset()
        # Start at random position (not just left edge)
        self.x = random.uniform(0, WIDTH)
        self.y = random.uniform(0, HEIGHT)

    def reset(self):
        self.x = random.uniform(-40, -10)
        self.y = random.uniform(50, HEIGHT - 50)
        self.speed_x = random.uniform(15, 40)
        self.speed_y = random.uniform(-8, 8)
        self.size = random.randint(8, 18)
        self.phase = random.uniform(0, math.pi * 2)
        self.spin = random.uniform(0.5, 2.0)
        self.alpha = random.randint(40, 100)
        self.color = random.choice([
            (255, 200, 220), (200, 220, 255), (255, 255, 180),
            (220, 200, 255), (180, 255, 220), (255, 180, 200),
        ])
        self.shape = random.choice(self.SHAPES)

    def update(self, dt, time):
        self.x += self.speed_x * dt
        self.y += self.speed_y * dt + math.sin(time * self.spin + self.phase) * 0.3
        if self.x > WIDTH + 40:
            self.reset()

    def draw(self, surface, time):
        s = pygame.Surface((self.size * 3, self.size * 3), pygame.SRCALPHA)
        cx, cy = self.size * 3 // 2, self.size * 3 // 2
        color = (*self.color, self.alpha)

        if self.shape == "star":
            points = []
            for i in range(5):
                angle = i * (2 * math.pi / 5) - math.pi / 2 + time * self.spin
                outer = self.size
                inner = self.size * 0.45
                points.append((cx + int(outer * math.cos(angle)),
                              cy + int(outer * math.sin(angle))))
                angle2 = angle + math.pi / 5
                points.append((cx + int(inner * math.cos(angle2)),
                              cy + int(inner * math.sin(angle2))))
            pygame.draw.polygon(s, color, points)
        elif self.shape == "heart":
            r = self.size // 2
            pygame.draw.circle(s, color, (cx - r // 2, cy - r // 3), r)
            pygame.draw.circle(s, color, (cx + r // 2, cy - r // 3), r)
            pygame.draw.polygon(s, color, [
                (cx - self.size + 2, cy - 2),
                (cx + self.size - 2, cy - 2),
                (cx, cy + self.size)
            ])
        else:
            pygame.draw.circle(s, color, (cx, cy), self.size // 2)

        surface.blit(s, (int(self.x) - self.size * 3 // 2, int(self.y) - self.size * 3 // 2))


class MainMenuScreen:
    def __init__(self, app):
        self.app = app
        self.games_btn = pygame.Rect(110, 300, 500, 100)
        self.shows_btn = pygame.Rect(110, 430, 500, 100)
        self.videos_btn = pygame.Rect(110, 560, 500, 100)
        self.buttons = [self.games_btn, self.shows_btn, self.videos_btn]
        self.states = [GAMES_MENU, SHOWS, VIDEOS]
        self.press = PressTracker(3)
        self.time = 0.0
        self.pending_nav = None
        self.shapes = [FloatingShape() for _ in range(12)]

    def on_enter(self):
        self.press = PressTracker(3)
        self.pending_nav = None
        self.time = 0.0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            for i, btn in enumerate(self.buttons):
                if btn.collidepoint(pos):
                    self.press.trigger(i)
                    self.pending_nav = (self.states[i], 0.12)
                    break

    def update(self, dt):
        self.time += dt
        self.press.update(dt)
        for shape in self.shapes:
            shape.update(dt, self.time)
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

        # Floating decorative shapes (behind everything)
        for shape in self.shapes:
            shape.draw(surface, self.time)

        # Gentle floating "AVA" title
        bob = math.sin(self.time * 2.0) * 6
        title_y = 130 + bob

        font = get_font(110)
        # Shadow
        shadow_surf = font.render("AVA", True, (0, 0, 0))
        shadow_surf.set_alpha(50)
        shadow_rect = shadow_surf.get_rect(center=(WIDTH // 2 + 3, title_y + 4))
        surface.blit(shadow_surf, shadow_rect)
        # Title
        text_surf = font.render("AVA", True, WHITE)
        text_rect = text_surf.get_rect(center=(WIDTH // 2, title_y))
        surface.blit(text_surf, text_rect)

        # Subtitle
        sub_font = get_font(20, bold=False)
        sub_surf = sub_font.render("Game Box", True, (255, 255, 255))
        sub_surf.set_alpha(180)
        sub_rect = sub_surf.get_rect(center=(WIDTH // 2, title_y + 70))
        surface.blit(sub_surf, sub_rect)

        # 3D Buttons
        draw_3d_button(surface, "PLAY GAMES", self.games_btn, GREEN, WHITE, 34, 24,
                       pressed=self.press.is_pressed(0))
        draw_3d_button(surface, "WATCH SHOWS", self.shows_btn, ORANGE, WHITE, 34, 24,
                       pressed=self.press.is_pressed(1))
        draw_3d_button(surface, "COOL VIDEOS", self.videos_btn, PURPLE, WHITE, 34, 24,
                       pressed=self.press.is_pressed(2))
