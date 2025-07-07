import pygame
import os
from gui.gui_utils import crop_transparent_border, draw_banner, add_transparent_border, Button
from gui.base_screen import BaseScreen 

class BulletSelectScreen(BaseScreen):
    def __init__(self, screen, frame_rate):
        super().__init__(screen)
        self.screen = screen
        self.frame_rate = frame_rate
        self.WIDTH, self.HEIGHT = screen.get_size()

        # Layout constants
        self.BANNER_HEIGHT = int(self.HEIGHT * 0.12)
        self.SPACER = int(self.HEIGHT * 0.05)

        self.PAGE_SELECT_BUTTON_HEIGHT = int(self.HEIGHT * 0.10)

        # Colors
        self.SCREEN_BG = (0, 0, 0)
        self.BANNER_BG = (55, 55, 60)
        self.BORDER_COLOR = (255, 255, 255)
        self.BORDER_THICKNESS = 2
        self.BUTTON_BG_COLOR = (20, 20, 20)
        self.BUTTON_BORDER_COLOR = (100, 100, 100)
        self.BUTTON_BORDER_THICKNESS = 20
        self.BUTTON_BORDER_SIDES = ["top", "bottom", "left", "right"]

        self.BULLET_BORDER_PADDING = 20

        self.ICON_TRANSPARENT_BORDER = 20

        # Fonts
        self.banner_font = pygame.font.SysFont("Segoe UI", int(self.BANNER_HEIGHT * 0.60))
        self.button_font = pygame.font.SysFont("Helvetica", 12, bold=True)

        self.load_images()

        self.page = 0
        self.n_row = 2
        self.n_col = 5

        self.return_button = Button(
            text=None,  # icon-only button
            pos=(self.WIDTH - self.BANNER_HEIGHT, 0),  # top-right corner
            size=(self.BANNER_HEIGHT,self.BANNER_HEIGHT),    # square button
            font=None,
            bg_color=self.BANNER_BG,
            text_color=(255, 255, 255),
            hover_color=self.BANNER_BG,
            icon=self.undo_icon  # must be a pygame.Surface
        )

        button_edge_len = min(
            int((self.WIDTH - ((self.n_col + 1) * self.SPACER)) / (self.n_col)),
            int(self.HEIGHT - (self.BANNER_HEIGHT + self.SPACER * (2 + self.n_row) + self.PAGE_SELECT_BUTTON_HEIGHT) / self.n_row)
            )

        # Settings Buttons (initial visible set)
        self.bullet_buttons = []

        for i, key in enumerate(sorted(self.bullets.keys())):
            button_x = (i % self.n_col) * (button_edge_len + self.SPACER) + self.SPACER
            button_y = ((i % (self.n_col * self.n_row)) // self.n_col) * (button_edge_len + self.SPACER) + self.SPACER + self.BANNER_HEIGHT
            btn = Button(
                text=None,
                pos=(button_x, button_y),
                size=(button_edge_len, button_edge_len),
                font=self.button_font,
                bg_color=self.BUTTON_BG_COLOR,
                text_color=(255, 255, 255),
                hover_color=(50, 50, 50),
                icon=self.bullets[key],
                border_color=(100,100,100),
                border_thickness=1,
                border_sides=self.BUTTON_BORDER_SIDES
            )
            self.bullet_buttons.append([key, btn])

        # Arrow Buttons
        arrow_button_size = (self.PAGE_SELECT_BUTTON_HEIGHT, self.PAGE_SELECT_BUTTON_HEIGHT)
        arrow_y = self.HEIGHT - self.PAGE_SELECT_BUTTON_HEIGHT - self.SPACER
        arrow_padding = self.SPACER

        self.left_button = Button(
            text=None,
            pos=(arrow_padding, arrow_y),
            size=arrow_button_size,
            font=self.banner_font,
            bg_color=self.SCREEN_BG,
            text_color=(255, 255, 255),
            hover_color=self.SCREEN_BG,
            icon=self.arrow_icon_left
        )

        self.right_button = Button(
            text=None,
            pos=(self.WIDTH - arrow_padding - arrow_button_size[0], arrow_y),
            size=arrow_button_size,
            font=self.banner_font,
            bg_color=self.SCREEN_BG,
            text_color=(255, 255, 255),
            hover_color=self.SCREEN_BG,
            icon=self.arrow_icon_right
        )

    def load_images(self):
        # Load train image 
        assets_dir = os.path.join(os.path.dirname(__file__), "../../../assets/images")

        # Load icon for banner
        icons_dir = os.path.join(assets_dir, "icons")
        undo_path = os.path.join(icons_dir, "undo.png")
        self.undo_icon = pygame.image.load(undo_path).convert_alpha()
        self.undo_icon = add_transparent_border(self.undo_icon, self.ICON_TRANSPARENT_BORDER)

        arrow_path = os.path.join(icons_dir, "arrow_subway.png")
        self.arrow_icon_right = pygame.image.load(arrow_path).convert_alpha()
        self.arrow_icon_left = pygame.transform.flip(self.arrow_icon_right, True, False)

        # Load subway bullets
        bullets_dir = os.path.join(assets_dir, "bullets")
        self.bullets = {}  # Dictionary to store bullet images

        if os.path.exists(bullets_dir):
            for filename in os.listdir(bullets_dir):
                if filename.endswith(".png"):
                    bullet_name = os.path.splitext(filename)[0]
                    if not bullet_name.endswith('d') or bullet_name.startswith('d'):
                        bullet_path = os.path.join(bullets_dir, filename)
                        try:
                            bullet_image = pygame.image.load(bullet_path).convert_alpha()
                            bullet_image = add_transparent_border(bullet_image, self.BULLET_BORDER_PADDING)
                            self.bullets[bullet_name.upper()] = bullet_image
                        except pygame.error as e:
                            print(f"Failed to load {filename}: {e}")
        else:
            print(f"Subway bullets folder not found: {bullets_dir}")

    def handle_event(self, event):
        if self.return_button.handle_event(event):
            return "goto:SettingsScreen"
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            
            max_pages = (len(self.bullet_buttons) - 1) // (self.n_row * self.n_col)

            if self.left_button.rect.collidepoint(mouse_pos):
                if self.page > 0:
                    self.page -= 1
                else:
                    self.page = max_pages

            if self.right_button.rect.collidepoint(mouse_pos):
                if self.page < max_pages:
                    self.page += 1
                else:
                    self.page = 0

            else:
                # Check visible bullet buttons
                start = self.page * self.n_row * self.n_col
                end = min(start + self.n_row * self.n_col, len(self.bullet_buttons))
                for key, button in self.bullet_buttons[start:end]:
                    if button.rect.collidepoint(mouse_pos):
                        return f"goto:StationSelectScreen:{key}"

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
            left_text="Station Select",
            center_text="",
            right_text="",
            right_button=self.return_button
        )

        # Draw visible bullet buttons
        start = self.page * self.n_row * self.n_col
        end = min(start + self.n_row * self.n_col, len(self.bullet_buttons))
        for key, button in self.bullet_buttons[start:end]:
            button.hovered = button.rect.collidepoint(pygame.mouse.get_pos())
            button.draw(self.screen)

        # Draw paging arrows
        self.left_button.hovered = self.left_button.rect.collidepoint(pygame.mouse.get_pos())
        self.left_button.draw(self.screen)

        self.right_button.hovered = self.right_button.rect.collidepoint(pygame.mouse.get_pos())
        self.right_button.draw(self.screen)

