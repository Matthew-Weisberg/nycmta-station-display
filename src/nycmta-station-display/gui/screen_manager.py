# screen_manager.py
from gui.home_screen import HomeScreen
from gui.settings_screen import SettingsScreen
from gui.bullet_select_screen import BulletSelectScreen
from gui.station_select_screen import StationSelectScreen

class ScreenManager:
    def __init__(self, screen, frame_rate, train_feed, config):
        self.screen = screen
        self.frame_rate = frame_rate
        self.train_feed = train_feed
        self.config = config
        self.current_screen = HomeScreen(screen, frame_rate, train_feed, config)

    def handle_event(self, event):
        result = self.current_screen.handle_event(event)
        if isinstance(result, str) and result.startswith("goto:"):
            screen_name = result.split("goto:")[1]
            self.change_screen(screen_name)
        elif isinstance(result, list) and result[0] == "config":
            return result

    def update(self, config, train_feed):
        self.config = config
        self.train_feed = train_feed
        self.current_screen.update()

    def render(self):
        self.current_screen.render()

    def change_screen(self, screen_name):
        if screen_name == "HomeScreen":
            self.current_screen = HomeScreen(self.screen, self.frame_rate, self.train_feed, self.config)
        elif screen_name == "SettingsScreen":
            self.current_screen = SettingsScreen(self.screen, self.frame_rate)
        elif screen_name == "BulletSelectScreen":
            self.current_screen = BulletSelectScreen(self.screen, self.frame_rate)
        elif screen_name.startswith("StationSelectScreen"):
            route_id = screen_name.split("StationSelectScreen:")[1]
            self.current_screen = StationSelectScreen(self.screen, self.frame_rate, route_id, self.config)
