import pygame
import os
import csv
from collections import defaultdict
from gui.gui_utils import crop_transparent_border, draw_banner, add_transparent_border, Button
from gui.base_screen import BaseScreen

class StationSelectScreen(BaseScreen):
    def __init__(self, screen, frame_rate, route_id):
        super().__init__(screen)
        self.screen = screen
        self.frame_rate = frame_rate
        self.WIDTH, self.HEIGHT = screen.get_size()
        self.route_id = route_id

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
        self.BUTTON_BORDER_THICKNESS = 20
        self.BUTTON_BORDER_SIDES = ["top", "bottom", "left", "right"]

        self.BULLET_BORDER_PADDING = 20

        self.ICON_TRANSPARENT_BORDER = 180

        # Fonts
        self.banner_font = pygame.font.SysFont("Helvetica", int(self.BANNER_HEIGHT * 0.6))

        self.load_images()

        self.load_stations_for_route_id(route_id)

        self.page = 0
        self.n_row = 5

        self.return_button = Button(
            text=None,  # icon-only button
            pos=(self.WIDTH - self.BANNER_HEIGHT, 0),  # top-right corner
            size=(self.BANNER_HEIGHT,self.BANNER_HEIGHT),    # square button
            font=None,
            bg_color=(150, 150, 150),
            text_color=(255, 255, 255),
            hover_color=(100, 100, 100),
            icon=self.undo_icon  
        )
        
        # Settings Buttons (initial visible set)
        self.station_buttons = []

        button_width = self.WIDTH - 2 * self.SPACER
        button_height = int((self.HEIGHT - ((self.n_row + 2) * self.SPACER + self.BANNER_HEIGHT + self.PAGE_SELECT_BUTTON_HEIGHT)) / self.n_row)
        self.button_font = pygame.font.SysFont("Helvetica", int(button_height * 0.5), bold=True)
                                       
        for i, station in enumerate(self.stations_for_route_id):
            button_y = (i % self.n_row) * (button_height + self.SPACER) + self.SPACER + self.BANNER_HEIGHT
            btn = Button(
                text=f"[left]        {station['stop_sequence']}.  {station['station_name']}",
                pos=(self.SPACER, button_y),
                size=(button_width, button_height),
                font=self.button_font,
                bg_color=self.BUTTON_BG_COLOR,
                text_color=(255, 255, 255),
                hover_color=(90, 90, 90),
                border_color=self.BUTTON_BORDER_COLOR,
                border_thickness=self.BORDER_THICKNESS,
                border_sides=self.BUTTON_BORDER_SIDES
            )
            self.station_buttons.append(btn)

        # Arrow Buttons
        arrow_button_size = (self.BANNER_HEIGHT, self.PAGE_SELECT_BUTTON_HEIGHT)
        arrow_y = self.HEIGHT - self.PAGE_SELECT_BUTTON_HEIGHT - self.SPACER
        arrow_padding = self.SPACER

        self.left_button = Button(
            text="<",
            pos=(arrow_padding, arrow_y),
            size=arrow_button_size,
            font=self.banner_font,
            bg_color=(80, 80, 80),
            text_color=(255, 255, 255),
            hover_color=(50, 50, 50)
        )

        self.right_button = Button(
            text=">",
            pos=(self.WIDTH - arrow_padding - arrow_button_size[0], arrow_y),
            size=arrow_button_size,
            font=self.banner_font,
            bg_color=(80, 80, 80),
            text_color=(255, 255, 255),
            hover_color=(50, 50, 50)
        )

    def load_images(self):

        assets_dir = os.path.join(os.path.dirname(__file__), "../../../assets/images")

        # Load icon for banner
        icons_dir = os.path.join(assets_dir, "icons")
        undo_path = os.path.join(icons_dir, "undo.png")
        self.undo_icon = pygame.image.load(undo_path).convert_alpha()
        self.undo_icon = add_transparent_border(self.undo_icon, self.ICON_TRANSPARENT_BORDER)

        # Load subway bullets
        bullets_dir = os.path.join(assets_dir, "bullets")
        self.bullets = {}  # Dictionary to store bullet images

        if os.path.exists(bullets_dir):
            for filename in os.listdir(bullets_dir):
                if filename.endswith(".png"):
                    bullet_name = os.path.splitext(filename)[0]
                    if not bullet_name.endswith('d'):
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
        self.stations_for_route_id = []

        # Step 1: Load all data, grouped by station_id
        station_routes = defaultdict(list)  # station_id -> list of rows
        with open(stations_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            all_rows = []
            for row in reader:
                route_id = row["route_id"].strip().upper()
                station_id = row["station_id"].strip()
                row["route_id"] = route_id
                row["station_id"] = station_id
                station_routes[station_id].append(route_id)
                all_rows.append(row)

        # Step 2: Filter for this route_id and annotate transfers
        for row in all_rows:
            if row["route_id"] == self.route_id.upper():
                transfers = [
                    rid for rid in station_routes[row["station_id"]]
                    if rid != self.route_id.upper()
                ]
                self.stations_for_route_id.append({
                    "route_id": row["route_id"],
                    "stop_sequence": int(row["stop_sequence"]),
                    "station_id": row["station_id"],
                    "station_name": row["station_name"],
                    "stop_lat": float(row["stop_lat"]),
                    "stop_lon": float(row["stop_lon"]),
                    "transfers": sorted(set(transfers))
                })

        # Sort final results by stop_sequence
        self.stations_for_route_id.sort(key=lambda x: x["stop_sequence"])
        print(f"Loaded {len(self.stations_for_route_id)} stations for bullet {self.route_id}")

    def handle_event(self, event):
        if self.return_button.handle_event(event):
            return "goto:BulletSelectScreen"
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            
            max_pages = (len(self.station_buttons) - 1) // (self.n_row)

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

        # Draw paging arrows
        self.left_button.hovered = self.left_button.rect.collidepoint(pygame.mouse.get_pos())
        self.left_button.draw(self.screen)

        self.right_button.hovered = self.right_button.rect.collidepoint(pygame.mouse.get_pos())
        self.right_button.draw(self.screen)

