# main.py — Entry point for Ava's Game Box

import pygame
import sys
from config import WIDTH, HEIGHT, FPS
from config import MAIN_MENU, GAMES_MENU, BUBBLE_POP, ANIMAL_SOUNDS, WHACK_A_CRITTER, SHOWS, REMOTE, VIDEOS
from app import App
from screens.main_menu import MainMenuScreen
from screens.games_menu import GamesMenuScreen
from screens.bubble_pop import BubblePopScreen
from screens.animal_sounds import AnimalSoundsScreen
from screens.whack_a_critter import WhackACritterScreen
from screens.shows import ShowsScreen
from screens.remote import RemoteScreen
from screens.videos import VideosScreen


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("Ava's Game Box")
    clock = pygame.time.Clock()

    app = App()

    # Register all screens
    app.register(MAIN_MENU, MainMenuScreen(app))
    app.register(GAMES_MENU, GamesMenuScreen(app))
    app.register(BUBBLE_POP, BubblePopScreen(app))
    app.register(ANIMAL_SOUNDS, AnimalSoundsScreen(app))
    app.register(WHACK_A_CRITTER, WhackACritterScreen(app))
    app.register(SHOWS, ShowsScreen(app))
    app.register(REMOTE, RemoteScreen(app))
    app.register(VIDEOS, VideosScreen(app))

    while True:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # ESC key to quit (development convenience)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            app.handle_event(event)

        app.update(dt)
        app.draw(screen)
        pygame.display.flip()


if __name__ == "__main__":
    main()
