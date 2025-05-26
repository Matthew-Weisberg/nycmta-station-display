import pygame
import os
from screens.utils import crop_transparent_border, draw_banner, Button
from screens.base_screen import BaseScreen  # You’ll create this base class

class SettingsScreen(BaseScreen):
    def __init__(self, screen, frame_rate):
        super().__init__(screen)
        self.screen = screen
        self.frame_rate = frame_rate
        self.WIDTH, self.HEIGHT = screen.get_size()

        # Layout constants
        self.BANNER_HEIGHT = int(self.HEIGHT * 0.08)
        self.SPACER = int(self.HEIGHT * 0.05)

        # Colors
        self.SCREEN_BG = (0, 0, 0)
        self.BANNER_BG = (40, 40, 40)
        self.BORDER_COLOR = (255, 255, 255)
        self.BORDER_THICKNESS = 2

        # Fonts
        self.banner_font = pygame.font.SysFont("Helvetica", int(self.BANNER_HEIGHT * 0.6))

        # Load and scale images
        self.load_images()

        self.home_button = Button(
            text="S",  # icon-only button
            pos=(self.WIDTH - self.BANNER_HEIGHT, 0),  # top-right corner
            size=(self.BANNER_HEIGHT,self.BANNER_HEIGHT),    # square button
            font=self.banner_font,
            bg_color=(200, 30, 30),
            text_color=(255, 255, 255),
            hover_color=(50, 50, 50),
            icon=None  # must be a pygame.Surface
        )

    def load_images(self):
        ""

    def handle_event(self, event):
        if self.home_button.handle_event(event):
            return "goto:HomeScreen"
        return None

    def update(self):
        ""

    def render(self):
        self.screen.fill(self.SCREEN_BG)

        draw_banner(
            screen=self.screen,
            screen_width=self.WIDTH,
            banner_height=self.BANNER_HEIGHT,
            banner_font=self.banner_font,
            banner_background_color=self.BANNER_BG,
            banner_border_color=self.BORDER_COLOR,
            banner_border_thickness=self.BORDER_THICKNESS,
            left_text="Settings",
            center_text="",
            right_text="",
            right_button=self.home_button
        )