import pygame
import os
import csv
from datetime import datetime
from collections import defaultdict, Counter
from gui.gui_utils import crop_transparent_border, draw_banner, draw_train_time, add_transparent_border, get_day_type, Button
from gui.base_screen import BaseScreen 

class HomeScreen2(BaseScreen):
    def __init__(self, 
                 screen, 
                 frame_rate,
                 train_feed,
                 config):
        
        super().__init__(screen)
        self.screen = screen
        self.frame_rate = frame_rate
        self.WIDTH, self.HEIGHT = screen.get_size()
        self.config = config

        self.train_feed = train_feed
        self.num_trains = 3
        self.curr_train = 1
        self.old_train = 0
        self.north_text  = {'train_num': "",
                            'bullet': "",
                            'arrival_time': "",
                            'destination': "",
                            'minutes': ""}
        self.south_text = self.north_text

        # Layout constants
        self.BANNER_HEIGHT = int(self.HEIGHT * 0.12)
        self.SPACER = int(self.HEIGHT * 0.04)
        self.STATION_NAME_HEIGHT = int(self.HEIGHT * 0.09)
        self.ALERTS_HEIGHT = int(self.HEIGHT * 0.06)
        self.TRAIN_HEIGHT = (self.HEIGHT - (self.BANNER_HEIGHT + self.STATION_NAME_HEIGHT + self.ALERTS_HEIGHT + 5 * self.SPACER)) // 2

        self.WEATHER_SPLIT = 0.32

        # Colors
        self.SCREEN_BG = (0, 0, 0)
        self.BANNER_BG = (40, 40, 40)
        self.BORDER_COLOR = (255, 255, 255)
        self.BORDER_THICKNESS = 2

        self.ICON_TRANSPARENT_BORDER = 150

        # Train speed
        self.first_pass = True
        self.counter = 0
        self.TRAIN_SPEED = 2.0  # seconds to cross screen
        self.TRAIN_WAIT_TIME = 3.0 # seconds before next train

        self.divider = int(self.WEATHER_SPLIT * self.WIDTH)
        self.train_screen_width = self.WIDTH - self.divider
        self.weather_background_rect = pygame.Rect(0, self.BANNER_HEIGHT + self.BORDER_THICKNESS, self.divider, self.HEIGHT - (self.BANNER_HEIGHT + self.BORDER_THICKNESS))


        # Fonts
        self.banner_font = pygame.font.SysFont("Helvetica", int(self.BANNER_HEIGHT * 0.7), bold=False)
        self.station_name_font = pygame.font.SysFont("Helvetica", int(self.STATION_NAME_HEIGHT * 0.99), bold=True)

        # Load and scale images
        self.load_images()

        self.load_trips()

        # --- Larger text behind trains ---
        self.train_time_font_size = int(self.train_height * 0.4)
        self.train_time_font = pygame.font.SysFont("Helvetica", self.train_time_font_size)

        # Train positions
        self.train1_x = -self.train_width + self.divider
        self.train2_x = self.WIDTH

        self.settings_button = Button(
            text=None,  # icon-only button
            pos=(self.WIDTH - self.BANNER_HEIGHT, 0),  # top-right corner
            size=(self.BANNER_HEIGHT,self.BANNER_HEIGHT),    # square button
            font=None,
            bg_color=(120, 150, 220),
            text_color=(255, 255, 255),
            hover_color=(100, 100, 100),
            icon=self.gear_icon  # must be a pygame.Surface
        )

    def load_images(self):
        assets_dir = os.path.join(os.path.dirname(__file__), "../../../assets/images")

        # Load icon for banner
        icons_dir = os.path.join(assets_dir, "icons")
        gear_path = os.path.join(icons_dir, "gear.png")
        self.gear_icon = pygame.image.load(gear_path).convert_alpha()
        self.gear_icon = add_transparent_border(self.gear_icon, self.ICON_TRANSPARENT_BORDER)

        # Load train image 
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
        bullets_dir = os.path.join(assets_dir, "bullets")
        self.bullets = {}  # Dictionary to store bullet images

        if os.path.exists(bullets_dir):
            for filename in os.listdir(bullets_dir):
                if filename.endswith(".png"):
                    bullet_name = os.path.splitext(filename)[0]
                    bullet_path = os.path.join(bullets_dir, filename)
                    try:
                        bullet_image = pygame.image.load(bullet_path).convert_alpha()
                        self.bullets[bullet_name.upper()] = bullet_image
                    except pygame.error as e:
                        print(f"Failed to load {filename}: {e}")
        else:
            print(f"Subway bullets folder not found: {bullets_dir}")
            

    def load_trips(self):
        assets_dir = os.path.join(os.path.dirname(__file__), "../../../assets/")
        gtfs_dir = os.path.join(assets_dir, "gtfs_subway")
        trips_path = os.path.join(gtfs_dir, "trips.txt")

        self.trips = []
        headsign_counts = defaultdict(lambda: defaultdict(Counter))

        with open(trips_path, newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)

            for row in reader:
                if 'trip_id' in row and '_' in row['trip_id']:
                    row['trip_id'] = row['trip_id'].split('_', 1)[1]

                self.trips.append(row)

                route_id = row.get('route_id')
                direction = row.get('direction_id')
                headsign = row.get('trip_headsign')

                if route_id and direction is not None and headsign:
                    direction_letter = 'N' if direction == '0' else 'S' if direction == '1' else direction
                    headsign_counts[route_id][direction_letter][headsign] += 1

        self.route_headsigns = {}
        for route_id, directions in headsign_counts.items():
            self.route_headsigns[route_id] = {}
            for direction_letter, counter in directions.items():
                most_common_headsign, _ = counter.most_common(1)[0]
                self.route_headsigns[route_id][direction_letter] = most_common_headsign

    def handle_event(self, event):
        if self.settings_button.handle_event(event):
            return "goto:SettingsScreen"
        return None

    def update(self):

        pixels_per_frame = (self.train_screen_width + 2 * self.train_width) // (self.TRAIN_SPEED * self.frame_rate)
        waiting_frames = self.TRAIN_WAIT_TIME * self.frame_rate
        self.train1_x += pixels_per_frame
        self.train2_x -= pixels_per_frame
        now = datetime.now().timestamp()

        if self.old_train != self.curr_train and self.train1_x < self.divider and self.train1_x + self.train_width > self.WIDTH:
            self.old_train = self.curr_train

            for train in self.train_feed.get('N', []):
                if train.get('order') == self.curr_train:

                    matching_trip = [
                        trip for trip in self.trips
                        if trip['route_id'] == train['route_id']
                        and trip['trip_id'] == train['trip_id']
                        and trip['service_id'] == get_day_type(train['arrival_time'])
                    ]

                    if len(matching_trip) != 1:
                        destination = self.route_headsigns[train['route_id']]['N'] + '*'
                    else:
                        destination = matching_trip[0]['trip_headsign']

                    self.north_text = {'train_num': self.curr_train,
                                       'bullet': train['route_id'],
                                       'arrival_time': train['arrival_time'],
                                       'destination': destination,
                                       'minutes': int((train['arrival_time'] - now) / 60) if (train['arrival_time'] - now) > 30 else 'now'}

            for train in self.train_feed.get('S', []):
                if train.get('order') == self.curr_train:
                    matching_trip = [
                        trip for trip in self.trips
                        if trip['route_id'] == train['route_id']
                        and trip['trip_id'] == train['trip_id']
                        and trip['service_id'] == get_day_type(train['arrival_time'])
                    ]

                    if len(matching_trip) != 1:
                        destination = self.route_headsigns[train['route_id']]['S'] + '*'
                    else:
                        destination = matching_trip[0]['trip_headsign']

                    self.south_text = {'train_num': self.curr_train,
                                       'bullet': train['route_id'],
                                       'arrival_time': train['arrival_time'],
                                       'destination': destination,
                                       'minutes': int((train['arrival_time'] - now) / 60) if (train['arrival_time'] - now) > 30 else 'now'}

        if self.train1_x > self.WIDTH:
            if self.first_pass:
                self.first_pass = False
            self.counter += 1
            if self.counter >= waiting_frames:
                self.train1_x = -self.train_width + self.divider
                self.train2_x = self.WIDTH
                self.counter = 0  
                self.curr_train += 1
                if self.curr_train > self.num_trains:
                    self.curr_train = 1 

    def render(self):
        self.screen.fill(self.SCREEN_BG)

        now_str = datetime.now().strftime("%A, %B %d     %I:%M %p")

        draw_banner(
            screen=self.screen,
            screen_width=self.WIDTH,
            banner_height=self.BANNER_HEIGHT,
            banner_font=self.banner_font,
            banner_background_color=self.BANNER_BG,
            banner_border_color=self.BORDER_COLOR,
            banner_border_thickness=self.BORDER_THICKNESS,
            left_text="",
            center_text=now_str,
            right_text="",
            right_button=self.settings_button
        )

        train1_y = self.BANNER_HEIGHT + self.STATION_NAME_HEIGHT + 2 * self.SPACER
        train2_y = train1_y + self.train_height + self.SPACER

        # --- Background rectangles behind text ---
        bg_rect_height = self.train_height

        # Placeholder y-values; adjust as needed
        rect1_y = self.BANNER_HEIGHT + self.BORDER_THICKNESS + self.STATION_NAME_HEIGHT + 2 * self.SPACER
        rect2_y = rect1_y + self.train_height + self.SPACER

        station_name_surface = self.station_name_font.render(self.config['station']['name'], True, (255, 255, 255))
        self.screen.blit(station_name_surface, (self.divider + self.SPACER, self.BANNER_HEIGHT + self.BORDER_THICKNESS + self.SPACER))
        
        if self.first_pass:
            train1_rect = pygame.Rect(self.train1_x, rect1_y, self.train_width + self.WIDTH, bg_rect_height)
            train2_rect = pygame.Rect(0, rect2_y, self.train2_x + self.train_width, bg_rect_height)
        else:
            train1_rect = pygame.Rect(self.train1_x, rect1_y, self.train_width, bg_rect_height)
            train2_rect = pygame.Rect(self.train2_x, rect2_y, self.train_width, bg_rect_height)

        draw_train_time(screen=self.screen,
                        screen_width=self.WIDTH,
                        train_height=self.train_height,
                        text_y_center= train1_y + self.train_height // 2,
                        curr_train=self.north_text['train_num'],
                        destination=self.north_text['destination'],
                        minutes_to_arrival=self.north_text['minutes'],
                        bullet=self.north_text['bullet'],
                        bullets_dict=self.bullets,
                        divider=self.divider)
        
        draw_train_time(screen=self.screen,
                        screen_width=self.WIDTH,
                        train_height=self.train_height,
                        text_y_center=train2_y + self.train_height // 2,
                        curr_train=self.south_text['train_num'],
                        destination=self.south_text['destination'],
                        minutes_to_arrival=self.south_text['minutes'],
                        bullet=self.south_text['bullet'],
                        bullets_dict=self.bullets,
                        divider=self.divider)
        
        pygame.draw.rect(self.screen, self.SCREEN_BG, train1_rect)
        pygame.draw.rect(self.screen, self.SCREEN_BG, train2_rect)

        # --- Draw trains on top ---
        self.screen.blit(self.train_flipped, (self.train1_x, train1_y))
        self.screen.blit(self.train_image, (self.train2_x, train2_y))

        pygame.draw.rect(self.screen, self.SCREEN_BG, self.weather_background_rect)
        pygame.draw.line(self.screen, self.BORDER_COLOR, (self.divider, self.BANNER_HEIGHT + self.BORDER_THICKNESS), (self.divider, self.HEIGHT), 1)