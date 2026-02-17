import pygame
import random
import sys

# --- Configuration ---
WIDTH, HEIGHT = 720, 720  # HyperPixel 4.0 Square Resolution
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)
GOLD = (255, 215, 0)

class AvaGameBox:
    def __init__(self):
        pygame.init()
        # For HyperPixel, use full screen or specific dimensions
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("Ava's Game Box")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.SysFont("Arial", 150, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 50, bold=True)
        
        self.state = "SPLASH"
        self.bubbles = []
        self.btn_rect = pygame.Rect(WIDTH // 4, HEIGHT // 2 + 100, WIDTH // 2, 100)

    def draw_splash(self):
        self.screen.fill(SKY_BLUE)

        text_surf = self.font_large.render("AVA", True, WHITE)
        text_rect = text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))

        pygame.draw.rect(self.screen, GOLD, self.btn_rect, border_radius=20)

        play_surf = self.font_small.render("TAP TO PLAY", True, BLACK)
        play_rect = play_surf.get_rect(center=self.btn_rect.center)

        self.screen.blit(text_surf, text_rect)
        self.screen.blit(play_surf, play_rect)

    def spawn_bubble(self):
        radius = random.randint(30, 60)
        for _ in range(50):
            x = random.randint(radius, WIDTH - radius)
            y = random.randint(radius, HEIGHT - radius)
            if not any(((x - b["pos"][0])**2 + (y - b["pos"][1])**2)**0.5 < radius + b["radius"] for b in self.bubbles):
                break
        bubble = {
            "pos": [x, y],
            "radius": radius,
            "color": (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        }
        self.bubbles.append(bubble)

    def draw_bubbles(self):
        self.screen.fill(WHITE)
        for b in self.bubbles:
            pygame.draw.circle(self.screen, b["color"], b["pos"], b["radius"])
            shine_offset = b["radius"] // 3
            shine_radius = b["radius"] // 4
            pygame.draw.circle(self.screen, WHITE, (b["pos"][0] - shine_offset, b["pos"][1] - shine_offset), shine_radius)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN: # Works for touch
                    pos = event.pos
                    
                    if self.state == "SPLASH":
                        if self.btn_rect.collidepoint(pos):
                            self.state = "BUBBLES"
                            for _ in range(10):
                                self.spawn_bubble()

                    elif self.state == "BUBBLES":
                        for i, b in enumerate(self.bubbles):
                            dist = ((pos[0] - b["pos"][0])**2 + (pos[1] - b["pos"][1])**2)**0.5
                            if dist < b["radius"]:
                                self.bubbles.pop(i)
                                self.spawn_bubble()
                                break

            if self.state == "SPLASH":
                self.draw_splash()
            elif self.state == "BUBBLES":
                self.draw_bubbles()

            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = AvaGameBox()
    game.run()