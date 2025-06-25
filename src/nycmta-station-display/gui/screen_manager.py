# screen_manager.py
from gui.home_screen import HomeScreen
from gui.settings_screen import SettingsScreen

class ScreenManager:
    def __init__(self, screen, frame_rate, train_feed, config):
        self.screen = screen
        self.frame_rate = frame_rate
        self.current_screen = HomeScreen(screen, frame_rate, train_feed, config)

    def handle_event(self, event):
        result = self.current_screen.handle_event(event)
        if isinstance(result, str) and result.startswith("goto:"):
            screen_name = result.split("goto:")[1]
            self.change_screen(screen_name)

    def update(self):
        self.current_screen.update()

    def render(self):
        self.current_screen.render()

    def change_screen(self, screen_name):
        if screen_name == "HomeScreen":
            self.current_screen = HomeScreen(self.screen, self.frame_rate, )
        elif screen_name == "SettingsScreen":
            self.current_screen = SettingsScreen(self.screen, self.frame_rate)
