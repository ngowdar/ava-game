# screens/whack_a_critter.py — Whack-a-mole with themed critters and polish

import pygame
import random
import math
from config import WIDTH, HEIGHT, WHITE, BLACK
from ui import draw_header, draw_3d_button, get_font


class StarParticle:
    def __init__(self, x, y):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(150, 400)
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.color = random.choice([
            (255, 255, 100), (255, 200, 50), (255, 150, 0),
            (255, 255, 200), (255, 180, 255), (150, 255, 255),
        ])
        self.radius = random.randint(4, 10)
        self.life = 0.5
        self.max_life = self.life

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 100 * dt
        self.life -= dt

    def draw(self, surface):
        if self.life > 0:
            alpha = self.life / self.max_life
            r = max(1, int(self.radius * alpha))
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), r)


class ScorePopup:
    """Floating "+1" text."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.life = 0.7
        self.vy = -100

    def update(self, dt):
        self.y += self.vy * dt
        self.life -= dt

    def draw(self, surface):
        if self.life > 0:
            font = get_font(28)
            text = font.render("+1", True, (255, 255, 100))
            alpha = min(255, int(self.life * 500))
            text.set_alpha(alpha)
            surface.blit(text, (int(self.x) - 15, int(self.y)))


class ConfettiParticle:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-HEIGHT, 0)
        self.vy = random.uniform(100, 250)
        self.vx = random.uniform(-30, 30)
        self.color = random.choice([
            (255, 100, 100), (100, 255, 100), (100, 100, 255),
            (255, 255, 100), (255, 150, 255), (100, 255, 255),
        ])
        self.size = random.randint(4, 10)
        self.life = 4.0
        self.rot = random.uniform(0, 360)
        self.rot_speed = random.uniform(100, 300)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rot += self.rot_speed * dt
        self.life -= dt

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.rect(surface, self.color,
                (int(self.x), int(self.y), self.size, self.size))


# Themed critter types with distinct looks
CRITTER_TYPES = [
    {"name": "bunny",   "body": (255, 200, 220), "accent": (255, 150, 180), "ear": True},
    {"name": "frog",    "body": (120, 220, 120), "accent": (80, 180, 80),   "ear": False},
    {"name": "bear",    "body": (180, 130, 80),  "accent": (140, 100, 60),  "ear": True},
    {"name": "chick",   "body": (255, 230, 100), "accent": (255, 180, 50),  "ear": False},
    {"name": "piggy",   "body": (255, 180, 200), "accent": (255, 140, 170), "ear": True},
    {"name": "alien",   "body": (180, 220, 255), "accent": (130, 180, 255), "ear": False},
]


class Critter:
    def __init__(self, hole_index, hole_cx, hole_cy):
        self.hole_index = hole_index
        self.cx = hole_cx
        self.cy = hole_cy
        self.state = "rising"
        self.timer = 0.0
        self.visible_time = random.uniform(1.8, 3.0)
        self.rise_time = 0.2
        self.progress = 0.0
        self.critter_type = random.choice(CRITTER_TYPES)
        self.hit_timer = 0.0
        self.eye_blink_timer = random.uniform(1.0, 3.0)
        self.blinking = False

    def update(self, dt):
        self.timer += dt

        # Eye blink
        self.eye_blink_timer -= dt
        if self.eye_blink_timer <= 0:
            self.blinking = not self.blinking
            self.eye_blink_timer = 0.1 if self.blinking else random.uniform(1.5, 3.0)

        if self.state == "rising":
            self.progress = min(1.0, self.timer / self.rise_time)
            if self.progress >= 1.0:
                self.state = "visible"
                self.timer = 0.0
        elif self.state == "visible":
            if self.timer >= self.visible_time:
                self.state = "sinking"
                self.timer = 0.0
        elif self.state == "sinking":
            self.progress = max(0.0, 1.0 - self.timer / self.rise_time)
            if self.progress <= 0.0:
                self.state = "gone"
        elif self.state == "hit":
            self.hit_timer += dt
            if self.hit_timer > 0.4:
                self.state = "gone"

    def draw(self, surface):
        if self.state == "gone":
            return

        body_radius = 32
        offset_y = int((1.0 - self.progress) * body_radius * 2)
        bx = self.cx
        by = self.cy - body_radius - 5 + offset_y

        ct = self.critter_type
        body_color = ct["body"]
        accent = ct["accent"]

        if self.state == "hit":
            # Squished flat with dizzy expression
            squish_progress = min(1.0, self.hit_timer / 0.15)
            h = max(8, int(body_radius * 2 * (1.0 - squish_progress * 0.7)))
            w = int(body_radius * 2 * (1.0 + squish_progress * 0.3))
            pygame.draw.ellipse(surface, body_color, (bx - w // 2, by + body_radius - h, w, h))
            # Dizzy eyes
            ey = by + body_radius - h // 2
            for dx in [-10, 10]:
                ex = bx + dx
                pygame.draw.line(surface, BLACK, (ex - 4, ey - 4), (ex + 4, ey + 4), 2)
                pygame.draw.line(surface, BLACK, (ex + 4, ey - 4), (ex - 4, ey + 4), 2)
            # Stars around head
            for i in range(3):
                angle = self.hit_timer * 8 + i * (2 * math.pi / 3)
                sx = bx + int(25 * math.cos(angle))
                sy = ey - 10 + int(8 * math.sin(angle))
                pygame.draw.circle(surface, (255, 255, 100), (sx, sy), 3)
            return

        # Ears (drawn behind body)
        if ct["ear"]:
            ear_h = 20 if ct["name"] != "bunny" else 30
            ear_w = 14
            for dx in [-15, 15]:
                ear_rect = (bx + dx - ear_w // 2, by - body_radius - ear_h + 8, ear_w, ear_h)
                pygame.draw.ellipse(surface, body_color, ear_rect)
                inner_rect = (bx + dx - ear_w // 4, by - body_radius - ear_h + 12, ear_w // 2, ear_h - 8)
                pygame.draw.ellipse(surface, accent, inner_rect)

        # Body
        pygame.draw.circle(surface, body_color, (bx, by), body_radius)

        # Belly/face highlight
        pygame.draw.circle(surface, accent, (bx, by + 5), body_radius - 10)

        # Eyes
        eye_y = by - 8
        for dx in [-11, 11]:
            ex = bx + dx
            # White
            pygame.draw.circle(surface, WHITE, (ex, eye_y), 8)
            if self.blinking:
                # Closed eye line
                pygame.draw.line(surface, BLACK, (ex - 6, eye_y), (ex + 6, eye_y), 2)
            else:
                # Pupil
                pygame.draw.circle(surface, BLACK, (ex, eye_y), 4)
                # Shine
                pygame.draw.circle(surface, WHITE, (ex - 2, eye_y - 2), 2)

        # Mouth
        if ct["name"] == "frog":
            # Wide smile
            pygame.draw.arc(surface, BLACK, (bx - 14, by + 2, 28, 14), 3.4, 6.0, 2)
        elif ct["name"] == "chick":
            # Beak
            pygame.draw.polygon(surface, (255, 160, 50), [
                (bx - 6, by + 6), (bx + 6, by + 6), (bx, by + 14)
            ])
        elif ct["name"] == "piggy":
            # Snout
            pygame.draw.ellipse(surface, accent, (bx - 8, by + 4, 16, 10))
            pygame.draw.circle(surface, BLACK, (bx - 3, by + 9), 2)
            pygame.draw.circle(surface, BLACK, (bx + 3, by + 9), 2)
        else:
            # Simple smile
            pygame.draw.arc(surface, BLACK, (bx - 10, by + 2, 20, 12), 3.4, 6.0, 2)

        # Cheek blush
        pygame.draw.circle(surface, (*accent, 100), (bx - 20, by + 5), 6)
        pygame.draw.circle(surface, (*accent, 100), (bx + 20, by + 5), 6)

    def hit_test(self, pos):
        if self.state not in ("rising", "visible"):
            return False
        body_radius = 32
        offset_y = int((1.0 - self.progress) * body_radius * 2)
        bx = self.cx
        by = self.cy - body_radius - 5 + offset_y
        dist = ((pos[0] - bx) ** 2 + (pos[1] - by) ** 2) ** 0.5
        return dist < body_radius + 12


class WhackACritterScreen:
    ROUND_TIME = 45.0

    # Ground colors
    GRASS_TOP = (80, 170, 80)
    GRASS_BOTTOM = (50, 130, 50)

    def __init__(self, app):
        self.app = app
        self.back_rect = None
        self.score = 0
        self.time_left = self.ROUND_TIME
        self.game_over = False
        self.spawn_timer = 0.0
        self.critters = []
        self.particles = []
        self.score_popups = []
        self.confetti = []
        self.play_again_btn = pygame.Rect(210, 480, 300, 80)
        self.time_elapsed = 0.0

        # Hole positions
        self.holes = []
        for row, y in enumerate([250, 410, 570]):
            for col, x in enumerate([120, 360, 600]):
                self.holes.append((x, y))

        # Pre-render ground gradient
        self.ground = self._make_ground()

    def _make_ground(self):
        surf = pygame.Surface((WIDTH, HEIGHT))
        for y in range(HEIGHT):
            t = y / HEIGHT
            r = int(self.GRASS_TOP[0] + (self.GRASS_BOTTOM[0] - self.GRASS_TOP[0]) * t)
            g = int(self.GRASS_TOP[1] + (self.GRASS_BOTTOM[1] - self.GRASS_TOP[1]) * t)
            b = int(self.GRASS_TOP[2] + (self.GRASS_BOTTOM[2] - self.GRASS_TOP[2]) * t)
            pygame.draw.line(surf, (r, g, b), (0, y), (WIDTH, y))
        return surf

    def on_enter(self):
        self.score = 0
        self.time_left = self.ROUND_TIME
        self.game_over = False
        self.spawn_timer = 0.0
        self.critters = []
        self.particles = []
        self.score_popups = []
        self.confetti = []
        self.time_elapsed = 0.0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.back_rect and self.back_rect.collidepoint(pos):
                self.app.go_back()
                return

            if self.game_over:
                if self.play_again_btn.collidepoint(pos):
                    self.on_enter()
                return

            for critter in reversed(self.critters):
                if critter.hit_test(pos):
                    critter.state = "hit"
                    critter.hit_timer = 0.0
                    self.score += 1
                    for _ in range(12):
                        self.particles.append(StarParticle(critter.cx, critter.cy - 20))
                    self.score_popups.append(ScorePopup(critter.cx, critter.cy - 50))
                    break

    def update(self, dt):
        self.time_elapsed += dt

        if self.game_over:
            for c in self.confetti:
                c.update(dt)
            self.confetti = [c for c in self.confetti if c.life > 0]
            if len(self.confetti) < 50:
                self.confetti.append(ConfettiParticle())
            return

        self.time_left -= dt
        if self.time_left <= 0:
            self.time_left = 0
            self.game_over = True
            for _ in range(40):
                self.confetti.append(ConfettiParticle())
            return

        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_timer = random.uniform(0.8, 1.5)
            active_holes = {c.hole_index for c in self.critters if c.state != "gone"}
            if len(active_holes) < 3:
                available = [i for i in range(9) if i not in active_holes]
                if available:
                    idx = random.choice(available)
                    cx, cy = self.holes[idx]
                    self.critters.append(Critter(idx, cx, cy))

        for critter in self.critters:
            critter.update(dt)
        self.critters = [c for c in self.critters if c.state != "gone"]

        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.life > 0]

        for sp in self.score_popups:
            sp.update(dt)
        self.score_popups = [sp for sp in self.score_popups if sp.life > 0]

    def draw(self, surface):
        # Ground gradient
        surface.blit(self.ground, (0, 0))

        # Small decorative flowers on the ground
        for i in range(8):
            fx = 60 + i * 90
            fy = 180 + (i % 3) * 200
            petal_color = [(255, 200, 200), (255, 255, 180), (200, 220, 255)][i % 3]
            for a in range(5):
                angle = a * (2 * math.pi / 5) + self.time_elapsed * 0.3
                px = fx + int(8 * math.cos(angle))
                py = fy + int(8 * math.sin(angle))
                pygame.draw.circle(surface, petal_color, (px, py), 5)
            pygame.draw.circle(surface, (255, 255, 100), (fx, fy), 4)

        # Header
        self.back_rect = draw_header(surface, "WHACK!")

        # Score
        font = get_font(30)
        star_text = f"* {self.score}"
        score_surf = font.render(star_text, True, (255, 255, 100))
        surface.blit(score_surf, (WIDTH - 130, 18))

        if not self.game_over:
            # Timer
            timer_font = get_font(24)
            secs = int(self.time_left)
            # Flash red when low
            timer_color = (255, 80, 80) if secs <= 5 else WHITE
            timer_surf = timer_font.render(f":{secs:02d}", True, timer_color)
            timer_rect = timer_surf.get_rect(center=(WIDTH // 2, 95))
            surface.blit(timer_surf, timer_rect)

            # Holes with depth shadow
            for cx, cy in self.holes:
                # Outer shadow
                pygame.draw.ellipse(surface, (30, 60, 30), (cx - 50, cy - 14, 100, 28))
                # Inner hole
                pygame.draw.ellipse(surface, (20, 45, 20), (cx - 42, cy - 10, 84, 20))
                # Highlight rim at top
                pygame.draw.arc(surface, (90, 160, 90),
                    (cx - 48, cy - 13, 96, 26), 2.8, 6.5, 2)

            # Critters
            for critter in self.critters:
                critter.draw(surface)

            # Particles & popups
            for p in self.particles:
                p.draw(surface)
            for sp in self.score_popups:
                sp.draw(surface)
        else:
            # Confetti
            for c in self.confetti:
                c.draw(surface)

            # "GREAT JOB!" with shadow
            big_font = get_font(64)
            shadow_surf = big_font.render("GREAT JOB!", True, BLACK)
            shadow_surf.set_alpha(80)
            surface.blit(shadow_surf, shadow_surf.get_rect(center=(WIDTH // 2 + 3, 263)))
            text_surf = big_font.render("GREAT JOB!", True, (255, 255, 100))
            surface.blit(text_surf, text_surf.get_rect(center=(WIDTH // 2, 260)))

            # Score
            score_font = get_font(44)
            score_surf = score_font.render(f"Score: {self.score}", True, WHITE)
            surface.blit(score_surf, score_surf.get_rect(center=(WIDTH // 2, 370)))

            # Tier message
            tier_font = get_font(24, bold=False)
            if self.score >= 25:
                msg = "SUPER STAR!"
            elif self.score >= 15:
                msg = "AMAZING!"
            elif self.score >= 8:
                msg = "GREAT WORK!"
            else:
                msg = "NICE TRY!"
            tier_surf = tier_font.render(msg, True, (255, 220, 180))
            surface.blit(tier_surf, tier_surf.get_rect(center=(WIDTH // 2, 420)))

            # Play Again
            draw_3d_button(surface, "PLAY AGAIN", self.play_again_btn, (76, 175, 80), WHITE, 32, 20)
