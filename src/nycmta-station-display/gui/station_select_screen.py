import pygame
import os
import csv
from collections import defaultdict
from gui.gui_utils import crop_transparent_border, draw_banner, add_transparent_border, Button
from gui.base_screen import BaseScreen

class StationSelectScreen(BaseScreen):
    def __init__(self, screen, frame_rate, route_id, config):
        super().__init__(screen)
        self.screen = screen
        self.frame_rate = frame_rate
        self.WIDTH, self.HEIGHT = screen.get_size()
        self.route_id = route_id
        self.config = config
        self.selected_station = config['station']['id']

        # Layout constants
        self.BANNER_HEIGHT = int(self.HEIGHT * 0.12)
        self.SPACER = int(self.HEIGHT * 0.05)

        self.PAGE_SELECT_BUTTON_HEIGHT = int(self.HEIGHT * 0.10)

        # Colors
        self.SCREEN_BG = (0, 0, 0)
        self.BANNER_BG = (40, 40, 40)
        self.BORDER_COLOR = (255, 255, 255)
        self.BORDER_THICKNESS = 1
        self.BUTTON_BG_COLOR = (20, 20, 20)
        self.BUTTON_BORDER_COLOR = (100, 100, 100)
        self.BUTTON_BORDER_THICKNESS = 1
        self.BUTTON_BORDER_SIDES = ["top", "bottom", "left", "right"]

        self.BULLET_BORDER_PADDING = 10

        self.RETURN_TRANSPARENT_BORDER = 20
        self.CHECK_TRANSPARENT_BORDER = 60

        self.BULLET_SIZE_SCALAR = 0.7
        self.CHECK_SIZE_SCALAR = 1.0

        # Fonts
        self.banner_font = pygame.font.SysFont("Helvetica", int(self.BANNER_HEIGHT * 0.6))

        self.load_images()
        self.station_rows = self.load_stations_for_route_id(route_id)  # now returns a list

        self.page = 0
        self.n_row = 5

        self.return_button = Button(
            text=None,  # icon-only button
            pos=(self.WIDTH - self.BANNER_HEIGHT, 0),
            size=(self.BANNER_HEIGHT, self.BANNER_HEIGHT),
            font=None,
            bg_color=self.BANNER_BG,
            text_color=(255, 255, 255),
            hover_color=self.BANNER_BG,
            icon=self.undo_icon
        )

        self.station_buttons = []
        self.button_width = self.WIDTH - 2 * self.SPACER
        self.button_height = int((self.HEIGHT - ((self.n_row + 2) * self.SPACER + self.BANNER_HEIGHT + self.PAGE_SELECT_BUTTON_HEIGHT)) / self.n_row)
        self.button_font = pygame.font.SysFont("Helvetica", int(self.button_height * 0.5), bold=True)

        for i, station in enumerate(self.station_rows):
            button_y = (i % self.n_row) * (self.button_height + self.SPACER) + self.SPACER + self.BANNER_HEIGHT
            btn = Button(
                text=f"[left]       {station['stop_sequence']}.  {station['station_name']}",
                pos=(self.SPACER, button_y),
                size=(self.button_width, self.button_height),
                font=self.button_font,
                bg_color=self.BUTTON_BG_COLOR,
                text_color=(255, 255, 255),
                hover_color=(90, 90, 90),
                border_color=self.BUTTON_BORDER_COLOR,
                border_thickness=self.BUTTON_BORDER_THICKNESS,
                border_sides=self.BUTTON_BORDER_SIDES
            )

            btn.route_id = station["route_id"]
            btn.station_name = station['station_name']
            btn.station_id = station["station_id"]
            btn.transfer_routes = station["transfer_routes"]
            btn.transfer_station_ids = station["transfer_station_ids"]

            # Add bullets for transfer routes (as long as they are not the main route)
            btn.bullets = []
            transfer_routes = station["transfer_routes"]
            for rid in transfer_routes:
                rid = rid.strip().upper()
                if rid and rid != self.route_id and rid in self.bullets:
                    bullet_img = self.bullets[rid]
                    scale_height = int(self.button_height * self.BULLET_SIZE_SCALAR)
                    scale_width = int(bullet_img.get_width() * (scale_height / bullet_img.get_height()))
                    scaled_bullet = pygame.transform.smoothscale(bullet_img, (scale_width, scale_height))
                    btn.bullets.append(scaled_bullet)

            self.station_buttons.append(btn)

        check_scale_height = int(self.button_height * self.CHECK_SIZE_SCALAR)
        check_scale_width = int(self.check_icon.get_width() * (check_scale_height / self.check_icon.get_height()))
        self.check_icon = pygame.transform.smoothscale(self.check_icon, (check_scale_height, check_scale_width))

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

        assets_dir = os.path.join(os.path.dirname(__file__), "../../../assets/images")

        # Load icon for banner
        icons_dir = os.path.join(assets_dir, "icons")
        undo_path = os.path.join(icons_dir, "undo.png")
        self.undo_icon = pygame.image.load(undo_path).convert_alpha()
        self.undo_icon = add_transparent_border(self.undo_icon, self.RETURN_TRANSPARENT_BORDER)
        
        check_path = os.path.join(icons_dir, "green_check.png")
        self.check_icon = pygame.image.load(check_path).convert_alpha()
        self.check_icon = add_transparent_border(self.check_icon, self.CHECK_TRANSPARENT_BORDER)

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

    def load_stations_for_route_id(self, route_id):
        assets_dir = os.path.join(os.path.dirname(__file__), "../../../assets")
        stations_dir = os.path.join(assets_dir, "gtfs_subway")
        stations_path = os.path.join(stations_dir, "route_stations.txt")

        matching_rows = []
        with open(stations_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row["route_id"] == route_id:
                    matching_rows.append(row)

        # Sort by stop_sequence (convert to int to ensure numeric order)
        matching_rows.sort(key=lambda x: int(x["stop_sequence"]))

        print(f"Loaded {len(matching_rows)} stations for bullet {route_id}")
        return matching_rows


    def handle_event(self, event):
        if self.return_button.handle_event(event):
            return "goto:BulletSelectScreen"
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            max_pages = (len(self.station_buttons) - 1) // self.n_row

            # Check for page arrows
            if self.left_button.rect.collidepoint(mouse_pos):
                if self.page > 0:
                    self.page -= 1
                else:
                    self.page = max_pages

            elif self.right_button.rect.collidepoint(mouse_pos):
                if self.page < max_pages:
                    self.page += 1
                else:
                    self.page = 0

            # Check for station button click
            start = self.page * self.n_row
            end = min(start + self.n_row, len(self.station_buttons))
            for button in self.station_buttons[start:end]:
                if button.rect.collidepoint(mouse_pos):
                    self.selected_station = button.station_id
                    return ["config", [
                                f"station:id|{button.station_id}",
                                f"route:id|{button.route_id}",
                                f"station:name|{button.station_name}"]
                            ]


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
        start = self.page * self.n_row

        end = min(start + self.n_row, len(self.station_buttons))

        for button in self.station_buttons[start:end]:
            button.hovered = button.rect.collidepoint(pygame.mouse.get_pos())
            button.draw(self.screen)
            # Draw bullets (transfer routes only) to the right of the button
            if hasattr(button, "bullets"):

                bullet_x = button.rect.right - self.BULLET_BORDER_PADDING
                bullet_y = button.rect.centery
                spacing = 5  # Pixels between bullets

                for bullet_img in reversed(button.bullets):  # right to left
                    rect = bullet_img.get_rect()
                    rect.midright = (bullet_x, bullet_y)
                    self.screen.blit(bullet_img, rect)
                    bullet_x -= rect.width + spacing

            if button.station_id == self.selected_station:
                check_x = button.rect.left
                check_y = button.rect.top
                rect = self.check_icon.get_rect(topleft=(check_x, check_y))  
                self.screen.blit(self.check_icon, rect)  


        # Draw paging arrows
        self.left_button.hovered = self.left_button.rect.collidepoint(pygame.mouse.get_pos())
        self.left_button.draw(self.screen)

        self.right_button.hovered = self.right_button.rect.collidepoint(pygame.mouse.get_pos())
        self.right_button.draw(self.screen)

