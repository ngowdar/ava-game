# screens/main_menu.py — Magical animated main menu for Ava's Game Box

import math
import random
import pygame
from config import WIDTH, HEIGHT, WHITE, GREEN, ORANGE, GAMES_MENU, SHOWS, VIDEOS
from config import ADMIN_PIN, SHUTDOWN_ACTION
from ui import draw_3d_button, get_font, PressTracker, hsv_to_rgb


PURPLE = (156, 39, 176)

# ---------- Lava-lamp gradient background ----------

class LavaBlob:
    """A soft color blob that drifts around for the lava-lamp background."""
    def __init__(self):
        self.x = random.uniform(0, WIDTH)
        self.y = random.uniform(0, HEIGHT)
        self.vx = random.uniform(-20, 20)
        self.vy = random.uniform(-20, 20)
        self.radius = random.randint(180, 300)
        self.hue = random.uniform(0, 360)
        self.hue_speed = random.uniform(8, 25)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.hue = (self.hue + self.hue_speed * dt) % 360
        # Bounce off edges with padding
        if self.x < -100 or self.x > WIDTH + 100:
            self.vx *= -1
        if self.y < -100 or self.y > HEIGHT + 100:
            self.vy *= -1

    def get_color(self):
        return hsv_to_rgb(self.hue, 0.5, 0.95)


# ---------- Floating decorative shapes ----------

class FloatingShape:
    """A star, heart, sparkle, or bubble drifting across the screen."""
    SHAPES = ["star", "heart", "sparkle", "bubble"]

    def __init__(self):
        self.reset(random_pos=True)

    def reset(self, random_pos=False):
        if random_pos:
            self.x = random.uniform(0, WIDTH)
            self.y = random.uniform(0, HEIGHT)
        else:
            self.x = random.uniform(-40, -10)
            self.y = random.uniform(30, HEIGHT - 30)
        self.base_vx = random.uniform(12, 35)
        self.base_vy = random.uniform(-6, 6)
        self.vx = self.base_vx
        self.vy = self.base_vy
        self.size = random.randint(7, 16)
        self.phase = random.uniform(0, math.pi * 2)
        self.spin = random.uniform(0.5, 2.0)
        self.alpha = random.randint(50, 120)
        self.color = random.choice([
            (255, 200, 220), (200, 220, 255), (255, 255, 180),
            (220, 200, 255), (180, 255, 220), (255, 180, 200),
            (255, 220, 150), (180, 230, 255), (255, 190, 255),
        ])
        self.shape = random.choice(self.SHAPES)
        self.scatter_vx = 0.0
        self.scatter_vy = 0.0

    def scatter_from(self, tx, ty):
        """Push this shape away from a tap point."""
        dx = self.x - tx
        dy = self.y - ty
        dist = max(1, math.sqrt(dx * dx + dy * dy))
        if dist < 200:
            force = (200 - dist) * 2.5
            self.scatter_vx = (dx / dist) * force
            self.scatter_vy = (dy / dist) * force

    def update(self, dt, time):
        # Decay scatter velocity
        self.scatter_vx *= 0.93
        self.scatter_vy *= 0.93
        self.vx = self.base_vx + self.scatter_vx
        self.vy = self.base_vy + self.scatter_vy
        self.x += self.vx * dt
        self.y += self.vy * dt + math.sin(time * self.spin + self.phase) * 0.4
        if self.x > WIDTH + 40 or self.x < -60 or self.y < -60 or self.y > HEIGHT + 60:
            self.reset(random_pos=False)

    def draw(self, surface, time):
        s = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
        cx, cy = self.size * 2, self.size * 2
        color = (*self.color, self.alpha)

        if self.shape == "star":
            points = []
            for i in range(5):
                angle = i * (2 * math.pi / 5) - math.pi / 2 + time * self.spin
                outer = self.size
                inner = self.size * 0.4
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
        elif self.shape == "sparkle":
            # Four-pointed sparkle
            arm = self.size
            thin = max(2, self.size // 4)
            angle_off = time * self.spin
            for a in range(4):
                ang = a * math.pi / 2 + angle_off
                ex = cx + int(arm * math.cos(ang))
                ey = cy + int(arm * math.sin(ang))
                perp = ang + math.pi / 2
                px, py = int(thin * math.cos(perp)), int(thin * math.sin(perp))
                pts = [(cx + px, cy + py), (ex, ey), (cx - px, cy - py)]
                pygame.draw.polygon(s, color, pts)
        else:  # bubble
            pygame.draw.circle(s, (*self.color, self.alpha // 2), (cx, cy), self.size)
            pygame.draw.circle(s, (*self.color, self.alpha), (cx, cy), self.size, 1)
            # Tiny highlight
            pygame.draw.circle(s, (255, 255, 255, min(200, self.alpha + 60)),
                             (cx - self.size // 3, cy - self.size // 3),
                             max(1, self.size // 4))

        surface.blit(s, (int(self.x) - self.size * 2, int(self.y) - self.size * 2))


# ---------- Letter particle effects ----------

class LetterParticle:
    """Small particle that flies outward and fades when a letter is tapped."""
    def __init__(self, x, y, color):
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(100, 300)
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = 1.0
        self.decay = random.uniform(1.5, 2.5)
        self.size = random.randint(3, 7)
        self.color = color

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx *= 0.96
        self.vy *= 0.96
        self.vy += 80 * dt  # gentle gravity
        self.life -= self.decay * dt
        return self.life > 0

    def draw(self, surface):
        alpha = max(0, min(255, int(self.life * 255)))
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (self.size, self.size), self.size)
        surface.blit(s, (int(self.x) - self.size, int(self.y) - self.size))


# ---------- Finger trail ----------

class TrailDot:
    """A rainbow circle left by a finger drag."""
    def __init__(self, x, y, hue):
        self.x = x
        self.y = y
        self.color = hsv_to_rgb(hue, 0.8, 1.0)
        self.life = 1.0
        self.size = random.randint(6, 12)

    def update(self, dt):
        self.life -= dt * 2.0  # fade over ~0.5s
        return self.life > 0

    def draw(self, surface):
        alpha = max(0, min(255, int(self.life * 255)))
        sz = max(1, int(self.size * self.life))
        s = pygame.Surface((sz * 2, sz * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (sz, sz), sz)
        surface.blit(s, (int(self.x) - sz, int(self.y) - sz))


# ---------- Interactive AVA letter ----------

class AvaLetter:
    """A single tappable letter with bounce and color animation."""
    RAINBOW = [
        (255, 80, 80), (255, 160, 50), (255, 230, 50),
        (80, 220, 80), (80, 180, 255), (160, 80, 255),
        (255, 80, 200),
    ]

    def __init__(self, char, base_x, base_y, phase_offset):
        self.char = char
        self.base_x = base_x
        self.base_y = base_y
        self.phase = phase_offset
        self.color = WHITE
        self.scale = 1.0
        self.bounce_timer = 0.0
        self.particles = []

    def tap(self):
        """Trigger bounce and particle burst."""
        self.bounce_timer = 0.4
        self.color = random.choice(self.RAINBOW)
        # Spawn particles
        for _ in range(18):
            p_color = random.choice(self.RAINBOW)
            self.particles.append(LetterParticle(self.base_x, self.base_y, p_color))

    def get_rect(self, font):
        """Return approximate hit rect for this letter."""
        surf = font.render(self.char, True, WHITE)
        w, h = surf.get_size()
        return pygame.Rect(self.base_x - w // 2 - 10, self.base_y - h // 2 - 10,
                          w + 20, h + 20)

    def update(self, dt, time):
        # Bob up and down
        self.bob_y = math.sin(time * 1.8 + self.phase) * 10

        # Bounce animation
        if self.bounce_timer > 0:
            self.bounce_timer -= dt
            t = self.bounce_timer / 0.4
            # Scale up then back: peaks at t~0.7
            self.scale = 1.0 + 0.3 * math.sin(t * math.pi)
        else:
            self.scale = 1.0

        # Update particles (capped)
        self.particles = [p for p in self.particles if p.update(dt)]
        if len(self.particles) > 60:
            self.particles = self.particles[-60:]

    def draw(self, surface, font, time):
        # Draw particles behind letter
        for p in self.particles:
            p.draw(surface)

        # Render letter
        text_surf = font.render(self.char, True, self.color)
        if self.scale != 1.0:
            w, h = text_surf.get_size()
            new_w = int(w * self.scale)
            new_h = int(h * self.scale)
            text_surf = pygame.transform.smoothscale(text_surf, (new_w, new_h))

        # Shadow
        shadow_surf = font.render(self.char, True, (0, 0, 0))
        shadow_surf.set_alpha(50)
        if self.scale != 1.0:
            shadow_surf = pygame.transform.smoothscale(shadow_surf,
                (int(shadow_surf.get_width() * self.scale),
                 int(shadow_surf.get_height() * self.scale)))
        shadow_rect = shadow_surf.get_rect(
            center=(self.base_x + 3, self.base_y + self.bob_y + 4))
        surface.blit(shadow_surf, shadow_rect)

        # Main letter
        rect = text_surf.get_rect(center=(self.base_x, self.base_y + self.bob_y))
        surface.blit(text_surf, rect)


# ---------- PIN keypad overlay ----------

class PinOverlay:
    """Full-screen PIN entry overlay triggered by hidden tap zone."""

    def __init__(self):
        self.active = False
        self.entered = ""
        self.shake_timer = 0.0
        self.shake_offset = 0
        self.success = False
        self.success_timer = 0.0
        # Keypad layout: 3x4 grid
        self.btn_size = 100
        self.btn_gap = 16
        grid_w = 3 * self.btn_size + 2 * self.btn_gap
        grid_h = 4 * self.btn_size + 3 * self.btn_gap
        self.grid_x = (WIDTH - grid_w) // 2
        self.grid_y = (HEIGHT - grid_h) // 2 + 50
        self.keys = [
            ["1", "2", "3"],
            ["4", "5", "6"],
            ["7", "8", "9"],
            ["C", "0", "<"],
        ]
        self.pressed_key = None
        self.pressed_timer = 0.0

    def open(self):
        self.active = True
        self.entered = ""
        self.shake_timer = 0.0
        self.success = False
        self.success_timer = 0.0
        self.pressed_key = None

    def close(self):
        self.active = False
        self.entered = ""

    def _get_key_rect(self, row, col):
        x = self.grid_x + col * (self.btn_size + self.btn_gap)
        y = self.grid_y + row * (self.btn_size + self.btn_gap)
        return pygame.Rect(x, y, self.btn_size, self.btn_size)

    def handle_event(self, event):
        """Returns 'shutdown' if PIN correct, 'cancel' if dismissed, None otherwise."""
        if not self.active or self.success:
            return None

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            for r, row in enumerate(self.keys):
                for c, key in enumerate(row):
                    rect = self._get_key_rect(r, c)
                    if rect.collidepoint(pos):
                        self.pressed_key = (r, c)
                        self.pressed_timer = 0.12
                        if key == "C":
                            self.entered = ""
                        elif key == "<":
                            self.entered = self.entered[:-1]
                        else:
                            self.entered += key
                            if len(self.entered) == len(ADMIN_PIN):
                                if self.entered == ADMIN_PIN:
                                    self.success = True
                                    self.success_timer = 0.6
                                    return None  # will trigger on timer
                                else:
                                    self.shake_timer = 0.4
                                    self.entered = ""
                        return None

            # Tap outside keypad area = cancel
            keypad_area = pygame.Rect(
                self.grid_x - 30, self.grid_y - 120,
                3 * self.btn_size + 2 * self.btn_gap + 60,
                4 * self.btn_size + 3 * self.btn_gap + 150)
            if not keypad_area.collidepoint(pos):
                self.close()
                return "cancel"

        return None

    def update(self, dt):
        """Returns 'shutdown' when success animation completes."""
        if not self.active:
            return None

        if self.pressed_timer > 0:
            self.pressed_timer -= dt
            if self.pressed_timer <= 0:
                self.pressed_key = None

        if self.shake_timer > 0:
            self.shake_timer -= dt
            self.shake_offset = int(math.sin(self.shake_timer * 30) * 8)
            if self.shake_timer <= 0:
                self.shake_offset = 0

        if self.success:
            self.success_timer -= dt
            if self.success_timer <= 0:
                return "shutdown"

        return None

    def draw(self, surface):
        if not self.active:
            return

        # Dim overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        # PIN dots
        dot_y = self.grid_y - 70
        dot_spacing = 36
        pin_len = len(ADMIN_PIN)
        dots_width = (pin_len - 1) * dot_spacing
        dot_start_x = WIDTH // 2 - dots_width // 2 + self.shake_offset
        for i in range(pin_len):
            cx = dot_start_x + i * dot_spacing
            if i < len(self.entered):
                color = (100, 255, 100) if self.success else WHITE
                pygame.draw.circle(surface, color, (cx, dot_y), 12)
            else:
                pygame.draw.circle(surface, (120, 120, 120), (cx, dot_y), 12, 2)

        # Keypad buttons
        for r, row in enumerate(self.keys):
            for c, key in enumerate(row):
                rect = self._get_key_rect(r, c)
                is_pressed = self.pressed_key == (r, c) and self.pressed_timer > 0

                if is_pressed:
                    color = (80, 80, 80)
                    rect = pygame.Rect(rect.x, rect.y + 2, rect.width, rect.height - 2)
                else:
                    # Bottom edge
                    bottom = pygame.Rect(rect.x, rect.y + 3, rect.width, rect.height)
                    pygame.draw.rect(surface, (30, 30, 30), bottom, border_radius=16)
                    color = (60, 60, 60)

                pygame.draw.rect(surface, color, rect, border_radius=16)
                pygame.draw.rect(surface, (90, 90, 90), rect, width=1, border_radius=16)

                font = get_font(36)
                label = key
                if key == "<":
                    label = "\u2190"
                text = font.render(label, True, WHITE)
                text_rect = text.get_rect(center=rect.center)
                surface.blit(text, text_rect)


# ---------- Main screen class ----------

class MainMenuScreen:
    def __init__(self, app):
        self.app = app

        # Button layout
        btn_w, btn_h = 500, 100
        btn_x = (WIDTH - btn_w) // 2
        self.games_btn = pygame.Rect(btn_x, 330, btn_w, btn_h)
        self.shows_btn = pygame.Rect(btn_x, 455, btn_w, btn_h)
        self.videos_btn = pygame.Rect(btn_x, 580, btn_w, btn_h)
        self.buttons = [self.games_btn, self.shows_btn, self.videos_btn]
        self.btn_targets_y = [330, 455, 580]
        self.states = [GAMES_MENU, SHOWS, VIDEOS]
        self.btn_colors = [GREEN, ORANGE, PURPLE]
        self.btn_labels = ["PLAY GAMES", "WATCH SHOWS", "COOL VIDEOS"]
        self.press = PressTracker(3)

        self.time = 0.0
        self.pending_nav = None

        # Lava lamp blobs
        self.blobs = [LavaBlob() for _ in range(3)]

        # Background surface (updated every few frames for performance)
        self.bg_surface = pygame.Surface((WIDTH, HEIGHT))
        self.bg_frame_counter = 0
        self._rebuild_gradient()

        # AVA letters
        font = get_font(110)
        # Measure total width to center the letters
        a_w = font.size("A")[0]
        v_w = font.size("V")[0]
        total_w = a_w + v_w + a_w + 20  # 10px gap between letters
        start_x = (WIDTH - total_w) // 2 + a_w // 2
        letter_y = 160
        self.letters = [
            AvaLetter("A", start_x, letter_y, 0),
            AvaLetter("V", start_x + a_w // 2 + 10 + v_w // 2, letter_y, math.pi * 0.66),
            AvaLetter("A", start_x + a_w // 2 + 10 + v_w + 10 + a_w // 2, letter_y, math.pi * 1.33),
        ]

        # Floating shapes
        self.shapes = [FloatingShape() for _ in range(28)]

        # Finger trail
        self.trail = []
        self.trail_hue = 0.0
        self.dragging = False

        # Subtitle pulse
        self.subtitle_alpha = 180

        # Button slide-in animation
        self.enter_timer = 0.0
        self.entered = False

        # Hidden shutdown: 5 taps in top-right corner within 3 seconds
        self.secret_zone = pygame.Rect(WIDTH - 80, 0, 80, 80)
        self.secret_taps = []
        self.pin_overlay = PinOverlay()

    def _rebuild_gradient(self):
        """Render the lava-lamp gradient background to a cached surface."""
        # Start with a dark-ish base
        self.bg_surface.fill((30, 20, 50))

        # Draw each blob as a radial gradient (approximated with concentric circles)
        for blob in self.blobs:
            color = blob.get_color()
            temp = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            steps = 12
            for i in range(steps, 0, -1):
                frac = i / steps
                r = int(blob.radius * frac)
                alpha = int(60 * (1 - frac) + 10)
                cr = int(color[0] * frac + 30 * (1 - frac))
                cg = int(color[1] * frac + 20 * (1 - frac))
                cb = int(color[2] * frac + 50 * (1 - frac))
                pygame.draw.circle(temp, (cr, cg, cb, alpha),
                                 (int(blob.x), int(blob.y)), r)
            self.bg_surface.blit(temp, (0, 0))

    def _bounce_ease(self, t):
        """Attempt a bounce-out easing. t goes from 0 to 1."""
        if t < 0:
            return 0.0
        if t > 1:
            return 1.0
        # Simple bounce: overshoot then settle
        return 1 - math.pow(1 - t, 3) * math.cos(t * math.pi * 1.5)

    def on_enter(self):
        self.press = PressTracker(3)
        self.pending_nav = None
        self.time = 0.0
        self.enter_timer = 0.0
        self.entered = False
        self.trail.clear()
        self.dragging = False
        # Reset letter colors
        for letter in self.letters:
            letter.color = WHITE
            letter.particles.clear()
        self.secret_taps = []
        self.pin_overlay.close()

    def handle_event(self, event):
        # PIN overlay intercepts all events when active
        if self.pin_overlay.active:
            self.pin_overlay.handle_event(event)
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            self.dragging = True

            # Hidden shutdown zone: top-right corner
            if self.secret_zone.collidepoint(pos):
                now = pygame.time.get_ticks() / 1000.0
                self.secret_taps.append(now)
                # Keep only taps within the last 3 seconds
                self.secret_taps = [t for t in self.secret_taps if now - t < 3.0]
                if len(self.secret_taps) >= 5:
                    self.secret_taps = []
                    self.pin_overlay.open()
                return

            # Check button taps (use animated positions)
            for i, btn in enumerate(self.buttons):
                if btn.collidepoint(pos):
                    self.press.trigger(i)
                    self.pending_nav = (self.states[i], 0.12)
                    return

            # Check letter taps
            font = get_font(110)
            for letter in self.letters:
                r = letter.get_rect(font)
                if r.collidepoint(pos):
                    letter.tap()
                    return

            # Scatter floating shapes from tap
            for shape in self.shapes:
                shape.scatter_from(pos[0], pos[1])

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            # Add trail dots
            pos = event.pos
            self.trail_hue = (self.trail_hue + 8) % 360
            self.trail.append(TrailDot(pos[0], pos[1], self.trail_hue))

    def update(self, dt):
        # PIN overlay update
        if self.pin_overlay.active:
            result = self.pin_overlay.update(dt)
            if result == "shutdown":
                self.pin_overlay.close()
                if SHUTDOWN_ACTION == "shutdown":
                    import subprocess
                    subprocess.Popen(["sudo", "shutdown", "now"])
                pygame.quit()
                import sys
                sys.exit()
            return

        self.time += dt
        self.enter_timer += dt
        self.press.update(dt)

        # Update lava blobs and refresh gradient every 4 frames
        for blob in self.blobs:
            blob.update(dt)
        self.bg_frame_counter += 1
        if self.bg_frame_counter >= 4:
            self.bg_frame_counter = 0
            self._rebuild_gradient()

        # Update AVA letters
        for letter in self.letters:
            letter.update(dt, self.time)

        # Update floating shapes
        for shape in self.shapes:
            shape.update(dt, self.time)

        # Update finger trail
        self.trail = [d for d in self.trail if d.update(dt)]
        if len(self.trail) > 120:
            self.trail = self.trail[-120:]

        # Subtitle pulse
        self.subtitle_alpha = 140 + int(40 * math.sin(self.time * 2.5))

        # Button slide-in: stagger each button
        if not self.entered and self.enter_timer > 1.5:
            self.entered = True
        for i in range(3):
            delay = 0.15 + i * 0.12  # staggered start
            t = (self.enter_timer - delay) / 0.6  # 0.6s duration
            eased = self._bounce_ease(t)
            # Slide from below screen
            start_y = HEIGHT + 60 + i * 60
            target_y = self.btn_targets_y[i]
            self.buttons[i].y = int(start_y + (target_y - start_y) * eased)

        # Navigation with delay for press animation
        if self.pending_nav:
            state, timer = self.pending_nav
            timer -= dt
            if timer <= 0:
                self.pending_nav = None
                self.app.go_to(state)
            else:
                self.pending_nav = (state, timer)

    def draw(self, surface):
        # Lava-lamp gradient background
        surface.blit(self.bg_surface, (0, 0))

        # Floating shapes (behind everything interactive)
        for shape in self.shapes:
            shape.draw(surface, self.time)

        # Finger trail
        for dot in self.trail:
            dot.draw(surface)

        # AVA letters
        font = get_font(110)
        for letter in self.letters:
            letter.draw(surface, font, self.time)

        # "Game Box" subtitle
        sub_font = get_font(28, bold=False)
        sub_surf = sub_font.render("Game Box", True, (255, 255, 255))
        sub_surf.set_alpha(self.subtitle_alpha)
        # Position below the AVA letters (accounting for bob)
        sub_rect = sub_surf.get_rect(center=(WIDTH // 2, 230))
        surface.blit(sub_surf, sub_rect)

        # Buttons
        for i in range(3):
            draw_3d_button(surface, self.btn_labels[i], self.buttons[i],
                          self.btn_colors[i], WHITE, 34, 24,
                          pressed=self.press.is_pressed(i))

        # PIN overlay (drawn on top of everything)
        self.pin_overlay.draw(surface)
