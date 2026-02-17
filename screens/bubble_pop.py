# screens/bubble_pop.py — Bubble-popping game with particles and polish

import pygame
import random
import math
from config import WIDTH, HEIGHT, WHITE, BLACK
from ui import draw_back_button, get_font


class PopParticle:
    """Colorful particle that bursts outward when a bubble pops."""
    def __init__(self, x, y, color):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(200, 500)
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.color = color
        self.radius = random.uniform(4, 10)
        self.life = random.uniform(0.3, 0.6)
        self.max_life = self.life

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 200 * dt  # gentle gravity
        self.life -= dt

    def draw(self, surface):
        if self.life > 0:
            alpha = self.life / self.max_life
            r = max(1, int(self.radius * alpha))
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), r)


class FloatingText:
    """"+1 POP!" text that floats upward and fades."""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.life = 0.8
        self.vy = -120

    def update(self, dt):
        self.y += self.vy * dt
        self.life -= dt

    def draw(self, surface):
        if self.life > 0:
            alpha = min(255, int(self.life * 400))
            font = get_font(22)
            text = font.render("POP!", True, self.color)
            text.set_alpha(alpha)
            surface.blit(text, (int(self.x) - text.get_width() // 2, int(self.y)))


class BackgroundCloud:
    """Gentle drifting cloud."""
    def __init__(self):
        self.x = random.randint(-100, WIDTH + 100)
        self.y = random.randint(50, HEIGHT - 100)
        self.speed = random.uniform(8, 25)
        self.size = random.randint(40, 90)
        self.alpha = random.randint(30, 70)

    def update(self, dt):
        self.x += self.speed * dt
        if self.x > WIDTH + 120:
            self.x = -120
            self.y = random.randint(50, HEIGHT - 100)

    def draw(self, surface):
        cloud = pygame.Surface((self.size * 2, self.size), pygame.SRCALPHA)
        color = (255, 255, 255, self.alpha)
        r = self.size // 3
        pygame.draw.circle(cloud, color, (self.size // 2, r + 5), r)
        pygame.draw.circle(cloud, color, (self.size, r), int(r * 1.3))
        pygame.draw.circle(cloud, color, (int(self.size * 1.5), r + 5), r)
        surface.blit(cloud, (int(self.x) - self.size, int(self.y)))


class BubblePopScreen:
    # Soft pastel background gradient colors
    BG_TOP = (200, 230, 255)     # light blue
    BG_BOTTOM = (255, 210, 240)  # light pink

    def __init__(self, app):
        self.app = app
        self.bubbles = []
        self.particles = []
        self.floating_texts = []
        self.clouds = [BackgroundCloud() for _ in range(6)]
        self.back_rect = None
        self.time = 0.0
        self.bg_surface = self._make_gradient()

    def _make_gradient(self):
        """Pre-render gradient background."""
        surf = pygame.Surface((WIDTH, HEIGHT))
        for y in range(HEIGHT):
            t = y / HEIGHT
            r = int(self.BG_TOP[0] + (self.BG_BOTTOM[0] - self.BG_TOP[0]) * t)
            g = int(self.BG_TOP[1] + (self.BG_BOTTOM[1] - self.BG_TOP[1]) * t)
            b = int(self.BG_TOP[2] + (self.BG_BOTTOM[2] - self.BG_TOP[2]) * t)
            pygame.draw.line(surf, (r, g, b), (0, y), (WIDTH, y))
        return surf

    def on_enter(self):
        self.bubbles = []
        self.particles = []
        self.floating_texts = []
        self.time = 0.0
        for _ in range(12):
            self.spawn_bubble()

    def spawn_bubble(self):
        radius = random.randint(30, 65)
        for _ in range(50):
            x = random.randint(radius + 10, WIDTH - radius - 10)
            y = random.randint(radius + 10, HEIGHT - radius - 10)
            if not any(
                ((x - b["pos"][0]) ** 2 + (y - b["pos"][1]) ** 2) ** 0.5
                < radius + b["radius"] + 5
                for b in self.bubbles
            ):
                break

        # Vibrant pastel colors
        palettes = [
            (255, 120, 150), (120, 200, 255), (180, 130, 255),
            (255, 200, 100), (100, 230, 180), (255, 160, 200),
            (150, 220, 255), (255, 150, 120), (200, 255, 180),
            (255, 180, 255), (120, 255, 200), (255, 230, 130),
        ]
        color = random.choice(palettes)

        bubble = {
            "pos": [x, y],
            "radius": radius,
            "color": color,
            "phase": random.uniform(0, math.pi * 2),  # for bobbing
            "bob_speed": random.uniform(1.5, 3.0),
            "bob_amount": random.uniform(2, 5),
        }
        self.bubbles.append(bubble)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.back_rect and self.back_rect.collidepoint(pos):
                self.app.go_back()
                return
            for i, b in enumerate(self.bubbles):
                bx = b["pos"][0]
                by = b["pos"][1] + math.sin(self.time * b["bob_speed"] + b["phase"]) * b["bob_amount"]
                dist = ((pos[0] - bx) ** 2 + (pos[1] - by) ** 2) ** 0.5
                if dist < b["radius"]:
                    # Pop! Spawn particles
                    for _ in range(15):
                        shade = (
                            min(255, b["color"][0] + random.randint(-30, 50)),
                            min(255, b["color"][1] + random.randint(-30, 50)),
                            min(255, b["color"][2] + random.randint(-30, 50)),
                        )
                        self.particles.append(PopParticle(bx, by, shade))
                    # Floating text
                    self.floating_texts.append(FloatingText(bx, by - b["radius"], b["color"]))
                    # Remove and respawn
                    self.bubbles.pop(i)
                    self.spawn_bubble()
                    break

    def update(self, dt):
        self.time += dt

        # Update clouds
        for cloud in self.clouds:
            cloud.update(dt)

        # Update particles
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.life > 0]

        # Update floating texts
        for ft in self.floating_texts:
            ft.update(dt)
        self.floating_texts = [ft for ft in self.floating_texts if ft.life > 0]

    def draw(self, surface):
        # Gradient background
        surface.blit(self.bg_surface, (0, 0))

        # Clouds
        for cloud in self.clouds:
            cloud.draw(surface)

        # Bubbles
        for b in self.bubbles:
            bx = b["pos"][0]
            by = b["pos"][1] + math.sin(self.time * b["bob_speed"] + b["phase"]) * b["bob_amount"]
            r = b["radius"]
            color = b["color"]

            # Outer glow
            glow = pygame.Surface((r * 3, r * 3), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*color, 25), (r * 3 // 2, r * 3 // 2), int(r * 1.3))
            surface.blit(glow, (int(bx - r * 1.5), int(by - r * 1.5)))

            # Main bubble
            pygame.draw.circle(surface, color, (int(bx), int(by)), r)

            # Darker outline
            darker = tuple(max(0, c - 40) for c in color)
            pygame.draw.circle(surface, darker, (int(bx), int(by)), r, 2)

            # Shine highlight (top-left)
            shine_x = int(bx - r * 0.3)
            shine_y = int(by - r * 0.3)
            shine_r = max(3, r // 4)
            pygame.draw.circle(surface, (255, 255, 255), (shine_x, shine_y), shine_r)

            # Secondary smaller shine
            pygame.draw.circle(surface, (255, 255, 255, 180),
                             (int(bx - r * 0.15), int(by - r * 0.5)), max(2, r // 6))

        # Particles (on top of bubbles)
        for p in self.particles:
            p.draw(surface)

        # Floating texts
        for ft in self.floating_texts:
            ft.draw(surface)

        # Back button
        self.back_rect = draw_back_button(surface)
