import pygame
import os
from datetime import datetime
from screens.utils import crop_transparent_border, draw_banner, Button
from screens.base_screen import BaseScreen  # You’ll create this base class

class HomeScreen(BaseScreen):
    def __init__(self, screen, frame_rate):
        super().__init__(screen)
        self.screen = screen
        self.frame_rate = frame_rate
        self.WIDTH, self.HEIGHT = screen.get_size()

        # Layout constants
        self.BANNER_HEIGHT = int(self.HEIGHT * 0.10)
        self.SPACER = int(self.HEIGHT * 0.05)
        self.TRAIN_HEIGHT = (self.HEIGHT - self.BANNER_HEIGHT - 3 * self.SPACER) // 2

        # Colors
        self.SCREEN_BG = (0, 0, 0)
        self.BANNER_BG = (40, 40, 40)
        self.BORDER_COLOR = (255, 255, 255)
        self.BORDER_THICKNESS = 2

        # Train speed
        self.TRAIN_SPEED = 10.0  # seconds to cross screen

        # Fonts
        self.banner_font = pygame.font.SysFont("Helvetica", int(self.BANNER_HEIGHT * 0.6))

        # Load and scale images
        self.load_images()

        # --- Larger text behind trains ---
        self.train_time_font_size = int(self.train_height * 0.6)
        self.train_time_font = pygame.font.SysFont("Helvetica", self.train_time_font_size)

        # Text to show behind trains
        self.train1_text = self.train_time_font.render("Express A", True, (255, 255, 255))
        self.train2_text = self.train_time_font.render("Express B", True, (255, 255, 255))

        # Train positions
        self.train1_x = -self.train_width
        self.train2_x = self.WIDTH

        self.settings_button = Button(
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
        assets_dir = os.path.join(os.path.dirname(__file__), "../../../../assets/images")
        image_path = os.path.join(assets_dir, "r211.png")
        train_image = pygame.image.load(image_path).convert_alpha()
        train_image = crop_transparent_border(train_image)

        orig_width, orig_height = train_image.get_size()
        scale_factor = self.TRAIN_HEIGHT / orig_height
        target_width = int(orig_width * scale_factor)

        self.train_image = pygame.transform.smoothscale(train_image, (target_width, self.TRAIN_HEIGHT))
        self.train_flipped = pygame.transform.flip(self.train_image, True, False)
        self.train_width, self.train_height = self.train_image.get_size()

    def handle_event(self, event):
        if self.settings_button.handle_event(event):
            return "goto:SettingsScreen"
        return None

    def update(self):
        pixels_per_frame = (self.WIDTH + 2 * self.train_width) / (self.TRAIN_SPEED * self.frame_rate)
        self.train1_x += pixels_per_frame
        self.train2_x -= pixels_per_frame

        if self.train1_x > self.WIDTH:
            self.train1_x = -self.train_width

        if self.train2_x < -self.train_width:
            self.train2_x = self.WIDTH

    def render(self):
        self.screen.fill(self.SCREEN_BG)

        now_str = datetime.now().strftime("%A, %B %d   %I:%M %p")
        draw_banner(
            screen=self.screen,
            screen_width=self.WIDTH,
            banner_height=self.BANNER_HEIGHT,
            banner_font=self.banner_font,
            banner_background_color=self.BANNER_BG,
            banner_border_color=self.BORDER_COLOR,
            banner_border_thickness=self.BORDER_THICKNESS,
            left_text=now_str,
            center_text="test",
            right_text="right text",
            right_button=self.settings_button
        )

        train1_y = self.BANNER_HEIGHT + self.SPACER
        train2_y = train1_y + self.train_height + self.SPACER

        # --- Background rectangles behind text ---
        bg_rect_height = int(1.5 * self.SPACER + self.train_height)

        # Placeholder y-values; adjust as needed
        rect1_y = self.BANNER_HEIGHT + self.BORDER_THICKNESS
        rect2_y = rect1_y + self.train_height + 1.5 * self.SPACER
        
        train1_rect = pygame.Rect(self.train1_x, rect1_y, self.train_width + self.WIDTH, bg_rect_height)
        train2_rect = pygame.Rect(0, rect2_y, self.train2_x + self.train_width, bg_rect_height)

        # --- Draw text ---
        train1_text_rect = self.train1_text.get_rect(center=(self.WIDTH // 2, train1_y + self.train_height // 2))
        train2_text_rect = self.train2_text.get_rect(center=(self.WIDTH // 2, train2_y + self.train_height // 2))

        self.screen.blit(self.train1_text, train1_text_rect)
        self.screen.blit(self.train2_text, train2_text_rect)
        
        pygame.draw.rect(self.screen, self.SCREEN_BG, train1_rect)
        pygame.draw.rect(self.screen, self.SCREEN_BG, train2_rect)

        # --- Draw trains on top ---
        self.screen.blit(self.train_flipped, (self.train1_x, train1_y))
        self.screen.blit(self.train_image, (self.train2_x, train2_y))
