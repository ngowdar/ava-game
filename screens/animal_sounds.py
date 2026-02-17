# screens/animal_sounds.py — 3x3 animal tap grid with animations

import pygame
import random
import math
from config import WIDTH, HEIGHT, SKY_BLUE, WHITE, BLACK, ANIMALS
from ui import draw_header, draw_rounded_rect


class Particle:
    def __init__(self, x, y, color):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(150, 400)
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.color = color
        self.radius = random.randint(5, 12)
        self.life = 0.6

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt
        self.radius = max(0, self.radius - dt * 15)

    def draw(self, surface):
        if self.life > 0 and self.radius > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.radius))


class AnimalSoundsScreen:
    def __init__(self, app):
        self.app = app
        self.back_rect = None
        self.tiles = []
        self.particles = []
        self.bounce_timers = {}  # index -> remaining bounce time
        self.name_display = None  # (name, timer)

        # Build tile rects: 3x3 grid, 190x190 tiles, 25px margins/gaps
        margin = 25
        tile_size = 190
        gap = (WIDTH - 2 * margin - 3 * tile_size) // 2
        start_y = 100
        for row in range(3):
            for col in range(3):
                x = margin + col * (tile_size + gap)
                y = start_y + row * (tile_size + gap)
                self.tiles.append(pygame.Rect(x, y, tile_size, tile_size))

    def on_enter(self):
        self.particles = []
        self.bounce_timers = {}
        self.name_display = None

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.back_rect and self.back_rect.collidepoint(pos):
                self.app.go_back()
                return
            for i, rect in enumerate(self.tiles):
                if rect.collidepoint(pos):
                    self._tap_animal(i)
                    break

    def _tap_animal(self, index):
        name, color, face_color = ANIMALS[index]
        # Bounce animation
        self.bounce_timers[index] = 0.3
        # Particle burst
        cx, cy = self.tiles[index].center
        for _ in range(10):
            c = (
                min(255, color[0] + random.randint(0, 80)),
                min(255, color[1] + random.randint(0, 80)),
                min(255, color[2] + random.randint(0, 80)),
            )
            self.particles.append(Particle(cx, cy, c))
        # Show name
        self.name_display = (name, 1.0)
        # Sound hook — uncomment when audio is connected:
        # try:
        #     from config import ANIMAL_SOUNDS
        #     sound = pygame.mixer.Sound(ANIMAL_SOUNDS[name])
        #     sound.play()
        # except Exception:
        #     pass

    def update(self, dt):
        # Update bounce timers
        expired = []
        for idx in self.bounce_timers:
            self.bounce_timers[idx] -= dt
            if self.bounce_timers[idx] <= 0:
                expired.append(idx)
        for idx in expired:
            del self.bounce_timers[idx]

        # Update particles
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.life > 0]

        # Update name display
        if self.name_display:
            name, timer = self.name_display
            timer -= dt
            if timer <= 0:
                self.name_display = None
            else:
                self.name_display = (name, timer)

    def draw(self, surface):
        surface.fill(SKY_BLUE)
        self.back_rect = draw_header(surface, "ANIMAL SOUNDS")

        # Draw tiles
        for i, rect in enumerate(self.tiles):
            name, color, face_color = ANIMALS[i]

            # Bounce scale
            if i in self.bounce_timers:
                t = self.bounce_timers[i]
                # Scale peaks at 1.2 then returns to 1.0
                progress = 1.0 - (t / 0.3)
                if progress < 0.5:
                    scale = 1.0 + 0.2 * (progress / 0.5)
                else:
                    scale = 1.2 - 0.2 * ((progress - 0.5) / 0.5)
            else:
                scale = 1.0

            w = int(rect.width * scale)
            h = int(rect.height * scale)
            draw_rect = pygame.Rect(0, 0, w, h)
            draw_rect.center = rect.center

            draw_rounded_rect(surface, color, draw_rect, 20)

            # Draw simple animal face
            cx, cy = draw_rect.centerx, draw_rect.centery - 15
            self._draw_animal_face(surface, cx, cy, name, face_color, scale)

            # Name below face
            font = pygame.font.Font(None, int(30 * scale))
            text_surf = font.render(name, True, WHITE)
            text_rect = text_surf.get_rect(center=(draw_rect.centerx, draw_rect.bottom - int(25 * scale)))
            surface.blit(text_surf, text_rect)

        # Draw particles
        for p in self.particles:
            p.draw(surface)

        # Draw name display
        if self.name_display:
            name, timer = self.name_display
            alpha = min(255, int(timer * 400))
            font = pygame.font.Font(None, 100)
            text_surf = font.render(name.upper(), True, WHITE)
            # Shadow
            shadow_surf = font.render(name.upper(), True, BLACK)
            sx = WIDTH // 2 - text_surf.get_width() // 2
            sy = HEIGHT // 2 - text_surf.get_height() // 2
            surface.blit(shadow_surf, (sx + 3, sy + 3))
            surface.blit(text_surf, (sx, sy))

    def _draw_animal_face(self, surface, cx, cy, name, face_color, scale):
        """Draw a simple animal face using pygame shapes."""
        s = scale
        r = int(35 * s)

        # Head circle
        pygame.draw.circle(surface, face_color, (cx, cy), r)

        # Eyes
        eye_dx = int(12 * s)
        eye_dy = int(-5 * s)
        eye_r = int(5 * s)
        pupil_r = int(3 * s)
        pygame.draw.circle(surface, WHITE, (cx - eye_dx, cy + eye_dy), eye_r)
        pygame.draw.circle(surface, WHITE, (cx + eye_dx, cy + eye_dy), eye_r)
        pygame.draw.circle(surface, BLACK, (cx - eye_dx, cy + eye_dy), pupil_r)
        pygame.draw.circle(surface, BLACK, (cx + eye_dx, cy + eye_dy), pupil_r)

        # Nose/mouth varies by animal
        nose_y = cy + int(8 * s)
        if name in ("Dog", "Cat", "Lion"):
            # Triangle nose
            ns = int(5 * s)
            pygame.draw.polygon(surface, BLACK, [
                (cx, nose_y - ns), (cx - ns, nose_y + ns // 2), (cx + ns, nose_y + ns // 2)
            ])
        elif name == "Pig":
            # Snout
            pygame.draw.ellipse(surface, (255, 130, 150), (cx - int(12*s), nose_y - int(5*s), int(24*s), int(14*s)))
            pygame.draw.circle(surface, BLACK, (cx - int(5*s), nose_y + int(2*s)), int(3*s))
            pygame.draw.circle(surface, BLACK, (cx + int(5*s), nose_y + int(2*s)), int(3*s))
        elif name == "Duck" or name == "Bird":
            # Beak
            beak_color = (255, 180, 0) if name == "Duck" else (255, 140, 0)
            pygame.draw.polygon(surface, beak_color, [
                (cx - int(10*s), nose_y - int(3*s)),
                (cx + int(10*s), nose_y - int(3*s)),
                (cx, nose_y + int(8*s))
            ])
        elif name == "Frog":
            # Wide mouth
            pygame.draw.arc(surface, BLACK,
                (cx - int(18*s), nose_y - int(10*s), int(36*s), int(20*s)),
                3.4, 6.0, int(2*s))
        elif name == "Cow":
            # Muzzle
            pygame.draw.ellipse(surface, (240, 200, 200),
                (cx - int(16*s), nose_y - int(6*s), int(32*s), int(16*s)))
            pygame.draw.circle(surface, BLACK, (cx - int(6*s), nose_y + int(2*s)), int(3*s))
            pygame.draw.circle(surface, BLACK, (cx + int(6*s), nose_y + int(2*s)), int(3*s))
        elif name == "Monkey":
            # Smile
            pygame.draw.arc(surface, BLACK,
                (cx - int(12*s), nose_y - int(8*s), int(24*s), int(16*s)),
                3.4, 6.0, int(2*s))
        else:
            # Default small mouth
            pygame.draw.circle(surface, BLACK, (cx, nose_y), int(3*s))

        # Ears for some animals
        ear_r = int(14 * s)
        if name in ("Cat", "Dog", "Lion", "Monkey", "Cow"):
            pygame.draw.circle(surface, face_color, (cx - r + int(5*s), cy - r + int(8*s)), ear_r)
            pygame.draw.circle(surface, face_color, (cx + r - int(5*s), cy - r + int(8*s)), ear_r)
        if name == "Frog":
            # Big eyes on top
            pygame.draw.circle(surface, (80, 200, 80), (cx - int(18*s), cy - r + int(2*s)), int(12*s))
            pygame.draw.circle(surface, (80, 200, 80), (cx + int(18*s), cy - r + int(2*s)), int(12*s))
