# main.py — Entry point for Ava's Game Box

import pygame
import sys
from config import WIDTH, HEIGHT, FPS
from config import (MAIN_MENU, GAMES_MENU, SHOWS, REMOTE, VIDEOS,
                    FINGER_PAINT, SHAPE_SORTER, MAGIC_GARDEN,
                    FIREWORKS, PARTICLE_PLAYGROUND, WEATHER_TOY)
from app import App
from screens.main_menu import MainMenuScreen
from screens.games_menu import GamesMenuScreen
from screens.finger_paint import FingerPaintScreen
from screens.shape_sorter import ShapeSorterScreen
from screens.magic_garden import MagicGardenScreen
from screens.fireworks import FireworksScreen
from screens.particle_playground import ParticlePlaygroundScreen
from screens.weather_toy import WeatherToyScreen
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
    app.register(FINGER_PAINT, FingerPaintScreen(app))
    app.register(SHAPE_SORTER, ShapeSorterScreen(app))
    app.register(MAGIC_GARDEN, MagicGardenScreen(app))
    app.register(FIREWORKS, FireworksScreen(app))
    app.register(PARTICLE_PLAYGROUND, ParticlePlaygroundScreen(app))
    app.register(WEATHER_TOY, WeatherToyScreen(app))
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
