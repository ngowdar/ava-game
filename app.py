# app.py — App state machine and screen routing

from config import MAIN_MENU


class App:
    def __init__(self):
        self.screens = {}
        self.state = MAIN_MENU
        self.history = []

    def register(self, state, screen):
        """Register a screen object for a state."""
        self.screens[state] = screen

    def go_to(self, state):
        """Push current state to history and switch to new state."""
        self.history.append(self.state)
        self.state = state
        screen = self.screens.get(state)
        if screen and hasattr(screen, "on_enter"):
            screen.on_enter()

    def go_back(self):
        """Pop history and return to previous state."""
        if self.history:
            self.state = self.history.pop()
            screen = self.screens.get(self.state)
            if screen and hasattr(screen, "on_enter"):
                screen.on_enter()

    def handle_event(self, event):
        """Route event to current screen."""
        screen = self.screens.get(self.state)
        if screen:
            screen.handle_event(event)

    def update(self, dt):
        """Route update to current screen."""
        screen = self.screens.get(self.state)
        if screen:
            screen.update(dt)

    def draw(self, surface):
        """Route draw to current screen."""
        screen = self.screens.get(self.state)
        if screen:
            screen.draw(surface)
