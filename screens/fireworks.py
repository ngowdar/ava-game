# screens/fireworks.py — Tap-to-launch fireworks game for toddlers

import math
import random
import pygame
from config import WIDTH, HEIGHT, WHITE, BLACK
from ui import draw_back_button, get_font, hsv_to_rgb


class FireworksScreen:
    def __init__(self, app):
        self.app = app
        self.rockets = []       # list of rocket dicts
        self.explosions = []    # list of explosion particle lists
        self.trail_particles = []  # rocket trail particles
        self.stars = []         # background twinkling stars
        self.back_rect = None

    # ── lifecycle ──────────────────────────────────────────────

    def on_enter(self):
        self.rockets.clear()
        self.explosions.clear()
        self.trail_particles.clear()
        self._init_stars()

    def _init_stars(self):
        self.stars = []
        for _ in range(50):
            self.stars.append({
                "x": random.randint(0, WIDTH),
                "y": random.randint(0, HEIGHT - 100),
                "r": random.uniform(1.0, 2.5),
                "phase": random.uniform(0, math.tau),
                "speed": random.uniform(1.5, 3.5),
            })

    # ── events ─────────────────────────────────────────────────

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # Back button check
            if self.back_rect and self.back_rect.collidepoint(mx, my):
                self.app.go_back()
                return
            # Launch a rocket toward the tap point
            self._launch_rocket(mx, my)

    def _launch_rocket(self, tx, ty):
        # Clamp target so explosion stays on screen
        ty = min(ty, HEIGHT - 80)
        self.rockets.append({
            "x": WIDTH / 2,
            "y": float(HEIGHT),
            "tx": float(tx),
            "ty": float(ty),
            "speed": random.uniform(500, 650),
            "hue": random.uniform(0, 360),
            "trail_timer": 0.0,
        })

    # ── update ─────────────────────────────────────────────────

    def update(self, dt):
        self._update_stars(dt)
        self._update_rockets(dt)
        self._update_trail_particles(dt)
        self._update_explosions(dt)

    def _update_stars(self, dt):
        for s in self.stars:
            s["phase"] += s["speed"] * dt

    def _update_rockets(self, dt):
        to_remove = []
        for r in self.rockets:
            dx = r["tx"] - r["x"]
            dy = r["ty"] - r["y"]
            dist = math.hypot(dx, dy)
            if dist < 10:
                # Explode
                self._spawn_explosion(r["x"], r["y"], r["hue"])
                to_remove.append(r)
                continue
            # Move toward target
            vx = dx / dist * r["speed"]
            vy = dy / dist * r["speed"]
            r["x"] += vx * dt
            r["y"] += vy * dt
            # Spawn trail particles
            r["trail_timer"] += dt
            if r["trail_timer"] > 0.015:
                r["trail_timer"] = 0.0
                self.trail_particles.append({
                    "x": r["x"] + random.uniform(-3, 3),
                    "y": r["y"] + random.uniform(-2, 2),
                    "life": random.uniform(0.2, 0.45),
                    "max_life": 0.45,
                    "r": random.uniform(1.5, 3.0),
                    "color": hsv_to_rgb(r["hue"] + random.uniform(-20, 20), 0.8, 1.0),
                })
        for r in to_remove:
            self.rockets.remove(r)

    def _update_trail_particles(self, dt):
        alive = []
        for p in self.trail_particles:
            p["life"] -= dt
            if p["life"] > 0:
                alive.append(p)
        self.trail_particles = alive

    def _update_explosions(self, dt):
        alive_explosions = []
        for particles in self.explosions:
            alive = []
            for p in particles:
                p["life"] -= dt
                if p["life"] <= 0:
                    continue
                p["x"] += p["vx"] * dt
                p["y"] += p["vy"] * dt
                p["vy"] += p["gravity"] * dt
                alive.append(p)
            if alive:
                alive_explosions.append(alive)
        self.explosions = alive_explosions

    # ── explosion spawning ─────────────────────────────────────

    def _spawn_explosion(self, x, y, base_hue):
        pattern = random.choice(["starburst", "ring", "cascade", "spiral"])
        count = random.randint(50, 80)
        particles = []

        for i in range(count):
            hue = (base_hue + random.uniform(-25, 25)) % 360
            color = hsv_to_rgb(hue, random.uniform(0.7, 1.0), 1.0)
            life = random.uniform(1.5, 2.5)

            if pattern == "starburst":
                angle = random.uniform(0, math.tau)
                speed = random.uniform(60, 220)
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed

            elif pattern == "ring":
                angle = (math.tau / count) * i + random.uniform(-0.1, 0.1)
                speed = random.uniform(120, 170)
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed

            elif pattern == "cascade":
                angle = random.uniform(-math.pi * 0.8, -math.pi * 0.2)
                speed = random.uniform(80, 200)
                vx = math.cos(angle) * speed + random.uniform(-30, 30)
                vy = math.sin(angle) * speed - random.uniform(0, 60)

            else:  # spiral
                angle = (math.tau / count) * i * 3
                speed = 60 + (i / count) * 160
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed

            particles.append({
                "x": x + random.uniform(-2, 2),
                "y": y + random.uniform(-2, 2),
                "vx": vx,
                "vy": vy,
                "gravity": random.uniform(60, 120),
                "life": life,
                "max_life": life,
                "r": random.uniform(2.0, 4.0),
                "color": color,
            })

        self.explosions.append(particles)

    # ── draw ───────────────────────────────────────────────────

    def draw(self, surface):
        self._draw_background(surface)
        self._draw_stars(surface)
        self._draw_trail_particles(surface)
        self._draw_rockets(surface)
        self._draw_explosions(surface)
        self.back_rect = draw_back_button(surface)

    def _draw_background(self, surface):
        # Dark blue-black gradient (top darker, bottom slightly lighter)
        top_color = (5, 5, 25)
        bot_color = (15, 15, 50)
        # Draw in horizontal bands for speed
        band = 12
        for y in range(0, HEIGHT, band):
            t = y / HEIGHT
            r = int(top_color[0] + (bot_color[0] - top_color[0]) * t)
            g = int(top_color[1] + (bot_color[1] - top_color[1]) * t)
            b = int(top_color[2] + (bot_color[2] - top_color[2]) * t)
            pygame.draw.rect(surface, (r, g, b), (0, y, WIDTH, band))

    def _draw_stars(self, surface):
        for s in self.stars:
            alpha = (math.sin(s["phase"]) + 1.0) / 2.0  # 0..1
            brightness = int(120 + 135 * alpha)
            color = (brightness, brightness, brightness)
            radius = max(1, int(s["r"] * (0.6 + 0.4 * alpha)))
            pygame.draw.circle(surface, color, (int(s["x"]), int(s["y"])), radius)

    def _draw_trail_particles(self, surface):
        for p in self.trail_particles:
            alpha = max(0.0, p["life"] / p["max_life"])
            r, g, b = p["color"]
            color = (int(r * alpha), int(g * alpha), int(b * alpha))
            radius = max(1, int(p["r"] * alpha))
            pygame.draw.circle(surface, color, (int(p["x"]), int(p["y"])), radius)

    def _draw_rockets(self, surface):
        for r in self.rockets:
            color = hsv_to_rgb(r["hue"], 0.9, 1.0)
            pygame.draw.circle(surface, color, (int(r["x"]), int(r["y"])), 4)
            # Bright white core
            pygame.draw.circle(surface, WHITE, (int(r["x"]), int(r["y"])), 2)

    def _draw_explosions(self, surface):
        for particles in self.explosions:
            for p in particles:
                alpha = max(0.0, p["life"] / p["max_life"])
                r, g, b = p["color"]
                color = (int(r * alpha), int(g * alpha), int(b * alpha))
                radius = max(1, int(p["r"] * alpha))
                pygame.draw.circle(surface, color, (int(p["x"]), int(p["y"])), radius)
