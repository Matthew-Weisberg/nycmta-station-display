import pygame
import os
from gui.gui_utils import crop_transparent_border, draw_banner, add_transparent_border, Button
from gui.base_screen import BaseScreen 

class SettingsScreen(BaseScreen):
    def __init__(self, screen, frame_rate):
        super().__init__(screen)
        self.screen = screen
        self.frame_rate = frame_rate
        self.WIDTH, self.HEIGHT = screen.get_size()

        # Layout constants
        self.BANNER_HEIGHT = int(self.HEIGHT * 0.12)
        self.SPACER = int(self.HEIGHT * 0.05)
        self.BUTTON_HEIGHT = int(self.HEIGHT * 0.10)
        self.BUTTON_WIDTH = self.WIDTH

        # Colors
        self.SCREEN_BG = (0, 0, 0)
        self.BANNER_BG = (40, 40, 40)
        self.BORDER_COLOR = (255, 255, 255)
        self.BORDER_THICKNESS = 2
        self.BUTTON_BG_COLOR = (20, 20, 20)
        self.BUTTON_BORDER_COLOR = (200, 200, 200)
        self.BUTTON_BORDER_THICKNESS = 20
        self.BUTTON_BORDER_SIDES = ["top", "bottom"]

        self.ICON_TRANSPARENT_BORDER = 15

        # Fonts
        self.banner_font = pygame.font.SysFont("Helvetica", int(self.BANNER_HEIGHT * 0.6))
        self.button_font = pygame.font.SysFont("Helvetica", int(self.BUTTON_HEIGHT * 0.5), bold=True)

        # Load and scale images
        self.load_images()

        self.home_button = Button(
            text=None,  # icon-only button
            pos=(self.WIDTH - self.BANNER_HEIGHT, 0),  # top-right corner
            size=(self.BANNER_HEIGHT,self.BANNER_HEIGHT),    # square button
            font=None,
            bg_color=self.BANNER_BG,
            text_color=(255, 255, 255),
            hover_color=self.BANNER_BG,
            icon=self.home_icon  # must be a pygame.Surface
        )

        # Settings Buttons (initial visible set)
        self.settings_labels = ["Choose Subway Station", "Config Settings", "Placeholder2", "Placeholder3"]
        self.setting_buttons = []
        for i, label in enumerate(self.settings_labels):
            btn = Button(
                text=label,
                pos=(self.SPACER, self.BANNER_HEIGHT + self.SPACER + i * (self.BUTTON_HEIGHT + self.SPACER)),
                size=(self.BUTTON_WIDTH - 2 * self.SPACER, self.BUTTON_HEIGHT),
                font=self.button_font,
                bg_color=self.BUTTON_BG_COLOR,
                text_color=(255, 255, 255),
                hover_color=(90, 90, 90),
                border_color=(200,200,200),
                border_thickness=2,
                border_sides=self.BUTTON_BORDER_SIDES
            )
            self.setting_buttons.append(btn)

    def load_images(self):
        assets_dir = os.path.join(os.path.dirname(__file__), "../../../assets/images")
        # Load icon for banner
        icons_dir = os.path.join(assets_dir, "icons")
        home_path = os.path.join(icons_dir, "home.png")
        self.home_icon = pygame.image.load(home_path).convert_alpha()
        self.home_icon = add_transparent_border(self.home_icon, self.ICON_TRANSPARENT_BORDER)

    def handle_event(self, event):
        if self.home_button.handle_event(event):
            return "goto:HomeScreen"
        if self.setting_buttons[0].handle_event(event):
            return "goto:BulletSelectScreen"
        return None

    def update(self):
        pass

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

        for button in self.setting_buttons:
            button.hovered = button.rect.collidepoint(pygame.mouse.get_pos())
            button.draw(self.screen)
