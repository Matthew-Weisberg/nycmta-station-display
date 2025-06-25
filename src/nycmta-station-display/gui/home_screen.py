import pygame
import os
from datetime import datetime
from gui.gui_utils import crop_transparent_border, draw_banner, draw_train_time, Button
from gui.base_screen import BaseScreen  # You’ll create this base class

class HomeScreen(BaseScreen):
    def __init__(self, 
                 screen, 
                 frame_rate,
                 train_feed,
                 config):
        super().__init__(screen)
        self.screen = screen
        self.frame_rate = frame_rate
        self.WIDTH, self.HEIGHT = screen.get_size()

        self.train_feed = train_feed
        self.num_trains = 3
        self.curr_train = 1
        self.north_text  = ""
        self.south_text = ""

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
        self.first_pass = True
        self.counter = 0
        self.TRAIN_SPEED = 3.0  # seconds to cross screen
        self.TRAIN_WAIT_TIME = 3.0 # seconds before next train

        # Fonts
        self.banner_font = pygame.font.SysFont("Helvetica", int(self.BANNER_HEIGHT * 0.6))

        # Load and scale images
        self.load_images()

        # --- Larger text behind trains ---
        self.train_time_font_size = int(self.train_height * 0.45)
        self.train_time_font = pygame.font.SysFont("Helvetica", self.train_time_font_size)

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
        # Load train image 
        assets_dir = os.path.join(os.path.dirname(__file__), "../../../assets/images")
        train_path = os.path.join(assets_dir, "r211.png")
        train_image = pygame.image.load(train_path).convert_alpha()
        train_image = crop_transparent_border(train_image)

        # Resize to right height
        orig_width, orig_height = train_image.get_size()
        scale_factor = self.TRAIN_HEIGHT / orig_height
        target_width = int(orig_width * scale_factor)
        self.train_image = pygame.transform.smoothscale(train_image, (target_width, self.TRAIN_HEIGHT))
       
        # Create a flipped version of the train to run in the opposite direction
        self.train_flipped = pygame.transform.flip(self.train_image, True, False)
        self.train_width, self.train_height = self.train_image.get_size()

        # Load subway bullets
        bullets_dir = os.path.join(assets_dir, "subway_bullets")
        self.bullets = {}  # Dictionary to store bullet images

        if os.path.exists(bullets_dir):
            for filename in os.listdir(bullets_dir):
                if filename.endswith(".png"):
                    bullet_name = os.path.splitext(filename)[0]
                    bullet_path = os.path.join(bullets_dir, filename)
                    try:
                        bullet_image = pygame.image.load(bullet_path).convert_alpha()
                        self.bullets[bullet_name] = bullet_image
                    except pygame.error as e:
                        print(f"Failed to load {filename}: {e}")
        else:
            print(f"Subway bullets folder not found: {bullets_dir}")

    def handle_event(self, event):
        if self.settings_button.handle_event(event):
            return "goto:SettingsScreen"
        return None

    def update(self):

        pixels_per_frame = (self.WIDTH + 2 * self.train_width) // (self.TRAIN_SPEED * self.frame_rate)
        waiting_frames = self.TRAIN_WAIT_TIME * self.frame_rate
        self.train1_x += pixels_per_frame
        self.train2_x -= pixels_per_frame

        now = datetime.now().timestamp()

        for train in self.train_feed.get('N', []):
            if train.get('order') == self.curr_train:
                north_bound_arrival = train['arrival_time']
                north_bound_destination = "Court Sq"
                north_bound_min = int((north_bound_arrival - now) / 60)

        for train in self.train_feed.get('S', []):
            if train.get('order') == self.curr_train:
                south_bound_arrival = train['arrival_time']
                south_bound_destination = "Church Av"
                south_bound_min = int((south_bound_arrival - now) / 60)

        if self.train1_x <= 0 and self.train1_x + self.train_width > self.WIDTH:
            self.north_text = f"{self.curr_train}. {north_bound_destination:<12} {north_bound_min:>3} min"
            self.south_text = f"{self.curr_train}. {south_bound_destination:<12} {south_bound_min:>3} min"

        # Text to show behind trains
        self.train1_text = self.train_time_font.render(self.north_text, True, (255, 255, 255))
        self.train2_text = self.train_time_font.render(self.south_text, True, (255, 255, 255))

        if self.train1_x > self.WIDTH:
            if self.first_pass:
                self.first_pass = False
            self.counter += 1
            if self.counter >= waiting_frames:
                self.train1_x = -self.train_width
                self.train2_x = self.WIDTH
                self.counter = 0  
                self.curr_train += 1
                if self.curr_train > self.num_trains:
                    self.curr_train = 1 


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
        
        if self.first_pass:
            train1_rect = pygame.Rect(self.train1_x, rect1_y, self.train_width + self.WIDTH, bg_rect_height)
            train2_rect = pygame.Rect(0, rect2_y, self.train2_x + self.train_width, bg_rect_height)
        else:
            train1_rect = pygame.Rect(self.train1_x, rect1_y, self.train_width, bg_rect_height)
            train2_rect = pygame.Rect(self.train2_x, rect2_y, self.train_width, bg_rect_height)

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
