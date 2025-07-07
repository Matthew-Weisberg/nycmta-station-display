import pygame
import os
import csv
from datetime import datetime
from collections import defaultdict, Counter
from gui.gui_utils import crop_transparent_border, draw_banner, draw_train_time, draw_no_train_time, add_transparent_border, get_train_text, Button
from gui.base_screen import BaseScreen 

class HomeScreen2(BaseScreen):
    def __init__(self, 
                 screen, 
                 frame_rate,
                 train_feed,
                 config,
                 weather_data):
        
        super().__init__(screen)
        self.screen = screen
        self.frame_rate = frame_rate
        self.WIDTH, self.HEIGHT = screen.get_size()
        self.config = config
        self.weather_current, self.weather_hourly, self.weather_daily = weather_data

        self.train_feed = train_feed
        self.num_trains = 4
        self.curr_train = 2
        self.old_train = 0
        self.north_next  = {'train_num': "",
                            'bullet': "",
                            'arrival_time': "",
                            'destination': "",
                            'minutes': ""}
        self.south_next = self.north_next
        self.north_following = self.north_next
        self.south_following = self.north_next

        # Layout constants
        self.BANNER_HEIGHT = int(self.HEIGHT * 0.12)
        self.SPACER = int(self.HEIGHT * 0.04)
        self.STATION_NAME_HEIGHT = int(self.HEIGHT * 0.09)
        self.ALERTS_HEIGHT = int(self.HEIGHT * 0.06)
        self.TRAIN_HEIGHT = (self.HEIGHT - (self.BANNER_HEIGHT + self.STATION_NAME_HEIGHT + self.ALERTS_HEIGHT + 5 * self.SPACER)) // 2

        self.WEATHER_SPLIT = 0.32

        # Colors
        self.SCREEN_BG = (0, 0, 0)
        self.BANNER_BG = (55, 55, 60)
        self.BORDER_COLOR = (255, 255, 255)
        self.BORDER_THICKNESS = 2

        self.ICON_TRANSPARENT_BORDER = 20

        # Train speed
        self.first_pass = True
        self.counter = 0
        self.TRAIN_SPEED = 2.0  # seconds to cross screen
        self.TRAIN_WAIT_TIME = 3.0 # seconds before next train

        self.divider = int(self.WEATHER_SPLIT * self.WIDTH)
        self.train_screen_width = self.WIDTH - self.divider
        self.weather_background_rect = pygame.Rect(0, self.BANNER_HEIGHT + self.BORDER_THICKNESS, self.divider, self.HEIGHT - (self.BANNER_HEIGHT + self.BORDER_THICKNESS))

        # Fonts
        self.banner_font = pygame.font.SysFont("Segoe UI", int(self.BANNER_HEIGHT * 0.60), bold=False)
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
            bg_color=self.BANNER_BG,
            text_color=(255, 255, 255),
            hover_color=self.BANNER_BG,
            icon=self.gear_icon  # must be a pygame.Surface
        )

        self.WEATHER_ICON_SPLIT = 0.5
        self.TEMP_VALUE_UNIT_SPLIT = 0.7

        self.wpo_conversion = {
            '53' : '51',
            '55' : '51',
            '81' : '80',
            '82' : '80',
            '63' : '61',
            '65' : '61',
            '57' : '56',
            '66' : '56',
            '67' : '56',
            '77' : '71',
            '73' : '71',
            '75' : '71',
            '86' : '85',
            '57' : '56',
            '96' : '95',
            '99' : '95'
        }

        weather_width_two_column = self.divider - 3 * self.SPACER
        self.weather_icon_size = int(weather_width_two_column * self.WEATHER_ICON_SPLIT)
        self.curr_temp_size = weather_width_two_column - self.weather_icon_size
        self.curr_temp_unit_x = self.divider - int(self.SPACER + self.curr_temp_size * (1 - self.TEMP_VALUE_UNIT_SPLIT))
        
        weather_width_three_column = self.divider - 4 * self.SPACER
        self.three_col_width = weather_width_three_column // 3

        weather_width_four_column = self.divider - 5 * self.SPACER
        self.four_col_width = weather_width_four_column // 4

# =================================================================================
        self.WEATHER_BG = (25, 25, 25)

        wpo = self.weather_current['weather_code']
        wpo = self.wpo_conversion.get(wpo, wpo)
        self.weather_image = self.wpo_icons[wpo]

        self.curr_temp = self.weather_current['temperature_2m']
        self.real_feel = self.weather_current['apparent_temperature']
        self.precip = self.weather_current['precipitation']
        self.humid = self.weather_current['relative_humidity_2m']
        self.wind = self.weather_current['wind_speed_10m']
        self.uv = self.weather_daily.at[0, 'uv_index_category']
        self.sunrise = self.weather_daily.at[0, 'sunrise']
        self.sunset = self.weather_daily.at[0, 'sunset']
# =================================================================================
        self.weather_image = add_transparent_border(self.weather_image, 28)
        orig_width, orig_height = self.weather_image.get_size()
        scale_factor = self.weather_icon_size / orig_height
        target_width = int(orig_width * scale_factor)
        self.weather_image = pygame.transform.smoothscale(self.weather_image, (target_width, self.weather_icon_size))
        
        # FONTS ------------------------------------------------------
        curr_temp_font = pygame.font.SysFont("Helvetica", int(self.curr_temp_size * 0.5), bold=False)
        curr_unit_font = pygame.font.SysFont("Helvetica", int(self.curr_temp_size * 0.25), bold=False)
        real_feel_font = pygame.font.SysFont("Helvetica", int(self.curr_temp_size * 0.15), bold=False, italic=False)
        stat_desc_font = pygame.font.SysFont("Helvetica", int(self.curr_temp_size * 0.12), bold=False, italic=False)
        curr_stat_font = pygame.font.SysFont("Helvetica", int(self.curr_temp_size * 0.15), bold=False)
        daily_desc_font = pygame.font.SysFont("Helvetica", int(self.curr_temp_size * 0.11), bold=False, italic=False)
        daily_value_font = pygame.font.SysFont("Helvetica", int(self.curr_temp_size * 0.13), bold=False)

        # CURRENT ------------------------------------------------------
        self.curr_temp_surface = curr_temp_font.render(self.curr_temp, True, (255, 255, 255))
        self.curr_unit_surface = curr_unit_font.render('°F', True, (255, 255, 255))
        self.real_feel_surface = real_feel_font.render(f'Feels like {self.real_feel}°', True, (220, 220, 220))
        
        # HOURLY ------------------------------------------------------
        self.hourly_stats = []

        HOURLY_TRANSPARENT_BORDER = 50

        orig_width, orig_height = self.weather_image.get_size()
        scale_factor = self.curr_temp_size * 0.12 / orig_height
        target_width = int(orig_width * scale_factor)
        target_height = int(self.curr_temp_size * 0.12)

        hourly_precip_icon = pygame.transform.smoothscale(add_transparent_border(self.weather_icons['raindrop'], 20), (target_width, target_height))
        
        orig_width, orig_height = self.weather_image.get_size()
        scale_factor = self.four_col_width / orig_height
        target_width = int(orig_width * scale_factor)
        target_height = int(self.four_col_width)

        for index, row in self.weather_hourly.iterrows():
            hour = curr_stat_font.render(row['hour_label'], True, (255, 255, 255)) 
            
            wpo = row['weather_code']
            wpo = self.wpo_conversion.get(wpo, wpo)
            icon = self.wpo_icons[wpo]
            icon = pygame.transform.smoothscale(add_transparent_border(icon, HOURLY_TRANSPARENT_BORDER), (target_width, target_height))

            temp = stat_desc_font.render(f"{round(row['temperature_2m'])}°F", True, (255, 255, 255)) 
            precip = stat_desc_font.render(f"{round(row['max_precip_last_hour'])}%", True, (255, 255, 255)) 

            self.hourly_stats.append([hour, icon, temp, hourly_precip_icon, precip])

        # DAY STATS ------------------------------------------------------
        self.stats_rows = 2
        self.stats_cols = 3

        precip_desc_surface = daily_desc_font.render(f'Precipitation', True, (220, 220, 220))
        humid_desc_surface = daily_desc_font.render(f'Humidity', True, (220, 220, 220))
        uv_desc_surface =  daily_desc_font.render(f'UV Index', True, (220, 220, 220))
        wind_desc_surface = daily_desc_font.render(f'Wind Speed', True, (220, 220, 220))
        sunrise_desc_surface = daily_desc_font.render(f'Sunrise', True, (220, 220, 220))
        sunset_desc_surface =  daily_desc_font.render(f'Sunset', True, (220, 220, 220)) 

        precip_value_surface = daily_value_font.render(f'{self.precip}%', True, (255, 255, 255))
        humid_value_surface = daily_value_font.render(f'{self.humid}%', True, (255, 255, 255))
        uv_value_surface =  daily_value_font.render(f'{self.uv}', True, (255, 255, 255))
        wind_value_surface = daily_value_font.render(f'{self.wind} mph', True, (255, 255, 255))
        sunrise_value_surface = daily_value_font.render(f'{self.sunrise}', True, (255, 255, 255))
        sunset_value_surface =  daily_value_font.render(f'{self.sunset}', True, (255, 255, 255))

        DAY_STATS_SCALER = 0.6

        orig_width, orig_height = self.weather_image.get_size()
        scale_factor = DAY_STATS_SCALER * self.three_col_width / orig_height
        target_width = int(orig_width * scale_factor)
        target_height = int(DAY_STATS_SCALER * self.three_col_width )


        precip_icon = pygame.transform.smoothscale(add_transparent_border(self.weather_icons["precipitation"], 2), (target_width, target_height))
        humid_icon = pygame.transform.smoothscale(add_transparent_border(self.weather_icons["humidity"], 13), (target_width, target_height))
        uv_icon = pygame.transform.smoothscale(add_transparent_border(self.weather_icons["uv"], 4), (target_width, target_height))
        wind_icon = pygame.transform.smoothscale(add_transparent_border(self.weather_icons["wind"], 8), (target_width, target_height))
        sunrise_icon = pygame.transform.smoothscale(add_transparent_border(self.weather_icons["sunrise"], 4), (target_width, target_height))
        sunset_icon = pygame.transform.smoothscale(add_transparent_border(self.weather_icons["sunset"], 4), (target_width, target_height))

        self.curr_stats = [
            [wind_icon, wind_desc_surface, wind_value_surface],
            [precip_icon, precip_desc_surface, precip_value_surface],
            [sunrise_icon, sunrise_desc_surface, sunrise_value_surface],
            [uv_icon, uv_desc_surface, uv_value_surface],
            [humid_icon, humid_desc_surface, humid_value_surface],
            [sunset_icon, sunset_desc_surface, sunset_value_surface]
        ]

    def load_images(self):
        assets_dir = os.path.join(os.path.dirname(__file__), "../../../assets/images")

        # Load icon for banner
        icons_dir = os.path.join(assets_dir, "icons")
        gear_path = os.path.join(icons_dir, "gear_filled.png")
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

        # Load subway bullets
        weather_dir = os.path.join(assets_dir, "weather_icons")
        self.weather_icons = {}  # Dictionary to store bullet images

        if os.path.exists(weather_dir):
            for filename in os.listdir(weather_dir):
                if filename.endswith(".png"):
                    weather_name = os.path.splitext(filename)[0]
                    weather_path = os.path.join(weather_dir, filename)
                    try:
                        weather_image = pygame.image.load(weather_path).convert_alpha()
                        self.weather_icons[weather_name] = weather_image
                    except pygame.error as e:
                        print(f"Failed to load {filename}: {e}")
        else:
            print(f"Subway bullets folder not found: {weather_dir}")

        # Load WPO Icons
        wpo_directory = os.path.join(assets_dir, "wpo_icons")
        self.wpo_icons = {}  # Dictionary to store bullet images

        if os.path.exists(wpo_directory):
            for filename in os.listdir(wpo_directory):
                if filename.endswith(".png"):
                    weather_name = os.path.splitext(filename)[0]
                    weather_path = os.path.join(wpo_directory, filename)
                    try:
                        weather_image = pygame.image.load(weather_path).convert_alpha()
                        self.wpo_icons[weather_name] = weather_image
                    except pygame.error as e:
                        print(f"Failed to load {filename}: {e}")
        else:
            print(f"Subway bullets folder not found: {wpo_directory}")
            

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

        if self.old_train != self.curr_train and self.train1_x < self.divider and self.train1_x + self.train_width > self.WIDTH:
            self.old_train = self.curr_train

            self.north_next = get_train_text('N', self.train_feed, 1, self.trips, self.route_headsigns)
            self.south_next = get_train_text('S', self.train_feed, 1, self.trips, self.route_headsigns)
            self.north_following = get_train_text('N', self.train_feed, self.curr_train, self.trips, self.route_headsigns)
            self.south_following = get_train_text('S', self.train_feed, self.curr_train, self.trips, self.route_headsigns)

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
                    self.curr_train = 2 

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

        
        if self.north_next:
            draw_train_time(screen=self.screen,
                            screen_width=self.WIDTH,
                            train_height=self.train_height,
                            text_y_center= train1_y + 3 * self.train_height // 10,
                            curr_train=self.north_next['train_num'],
                            destination=self.north_next['destination'],
                            minutes_to_arrival=self.north_next['minutes'],
                            bullet=self.north_next['bullet'],
                            bullets_dict=self.bullets,
                            divider=self.divider)
        else:
            draw_no_train_time(screen=self.screen,
                               screen_width=self.WIDTH,
                               train_height=self.train_height,
                               text_y_center= train1_y + 3 * self.train_height // 10,
                               curr_train=1,
                               divider=self.divider)
        
        if self.south_next:
            draw_train_time(screen=self.screen,
                            screen_width=self.WIDTH,
                            train_height=self.train_height,
                            text_y_center=train2_y + 3 * self.train_height // 10,
                            curr_train=self.south_next['train_num'],
                            destination=self.south_next['destination'],
                            minutes_to_arrival=self.south_next['minutes'],
                            bullet=self.south_next['bullet'],
                            bullets_dict=self.bullets,
                            divider=self.divider)
        else:
            draw_no_train_time(screen=self.screen,
                               screen_width=self.WIDTH,
                               train_height=self.train_height,
                               text_y_center= train2_y + 3 * self.train_height // 10,
                               curr_train=1,
                               divider=self.divider)
        
        if self.north_following:
            draw_train_time(screen=self.screen,
                            screen_width=self.WIDTH,
                            train_height=self.train_height,
                            text_y_center= train1_y + 7 * self.train_height // 10,
                            curr_train=self.north_following['train_num'],
                            destination=self.north_following['destination'],
                            minutes_to_arrival=self.north_following['minutes'],
                            bullet=self.north_following['bullet'],
                            bullets_dict=self.bullets,
                            divider=self.divider)
        else:
            draw_no_train_time(screen=self.screen,
                               screen_width=self.WIDTH,
                               train_height=self.train_height,
                               text_y_center= train1_y + 7 * self.train_height // 10,
                               curr_train=self.old_train,
                               divider=self.divider)

        if self.south_following:
            draw_train_time(screen=self.screen,
                            screen_width=self.WIDTH,
                            train_height=self.train_height,
                            text_y_center=train2_y + 7 * self.train_height // 10,
                            curr_train=self.south_following['train_num'],
                            destination=self.south_following['destination'],
                            minutes_to_arrival=self.south_following['minutes'],
                            bullet=self.south_following['bullet'],
                            bullets_dict=self.bullets,
                            divider=self.divider)
        else:
            draw_no_train_time(screen=self.screen,
                               screen_width=self.WIDTH,
                               train_height=self.train_height,
                               text_y_center= train2_y + 7 * self.train_height // 10,
                               curr_train=self.old_train,
                               divider=self.divider)
        
        pygame.draw.rect(self.screen, self.SCREEN_BG, train1_rect)
        pygame.draw.rect(self.screen, self.SCREEN_BG, train2_rect)

        # --- Draw trains on top ---
        self.screen.blit(self.train_flipped, (self.train1_x, train1_y))
        self.screen.blit(self.train_image, (self.train2_x, train2_y))

        # pygame.draw.rect(self.screen, self.WEATHER_BG, self.weather_background_rect)
        pygame.draw.rect(self.screen, self.WEATHER_BG, self.weather_background_rect)
        pygame.draw.line(self.screen, self.BORDER_COLOR, (self.divider, self.BANNER_HEIGHT + self.BORDER_THICKNESS), (self.divider, self.HEIGHT), 1)

        # ----------------------------------------------------------
        # ----------------- WEATHER SECTION ------------------------
        # ----------------------------------------------------------

        self.screen.blit(self.weather_image, (self.SPACER, self.SPACER + self.BANNER_HEIGHT))

        bottom_banner = self.BANNER_HEIGHT + self.BORDER_THICKNESS
        temp_y =  bottom_banner + self.SPACER + self.weather_icon_size // 2 - 9
        real_feel_y = bottom_banner + self.SPACER + self.weather_icon_size
        hourly_stats_y = real_feel_y + int(1.5 * self.SPACER)
        stat_text_y = real_feel_y + 2 * self.SPACER + self.three_col_width + 120


        curr_temp_rect = self.curr_temp_surface.get_rect(midright=(self.curr_temp_unit_x, temp_y))
        self.screen.blit(self.curr_temp_surface, curr_temp_rect)

        curr_unit_rect = self.curr_unit_surface.get_rect(midleft=(self.curr_temp_unit_x, temp_y - 8))
        self.screen.blit(self.curr_unit_surface, curr_unit_rect)

        real_feel_rect = self.real_feel_surface.get_rect(midbottom=(self.divider - (self.SPACER + self.curr_temp_size // 2 + 3), real_feel_y - 13))
        self.screen.blit(self.real_feel_surface, real_feel_rect)

        for i, (hour, icon, temp, precip_icon, precip) in enumerate(self.hourly_stats):
            x = self.SPACER + self.four_col_width // 2 + i * (self.four_col_width + self.SPACER)
            
            hour_rect = hour.get_rect(midbottom=(x, hourly_stats_y))
            self.screen.blit(hour, hour_rect)

            icon_rect = icon.get_rect(midtop=(x, hourly_stats_y))
            self.screen.blit(icon, icon_rect)

            temp_rect = temp.get_rect(midtop=(x, hourly_stats_y + self.four_col_width))
            self.screen.blit(temp, temp_rect)

            precip_icon_rect = precip_icon.get_rect(topright=(x - 4, hourly_stats_y + self.four_col_width + 14))
            self.screen.blit(precip_icon, precip_icon_rect)

            precip_rect = precip.get_rect(topleft=(x - 1, hourly_stats_y + self.four_col_width + 14))
            self.screen.blit(precip, precip_rect)

        y = precip_rect.bottom + int(self.SPACER * 1.3)

        for i, (icon, desc, stat) in enumerate(self.curr_stats):
            
            x = self.SPACER + self.three_col_width // 2 + (i % self.stats_cols) * (self.three_col_width + self.SPACER)
            y_top = y + int((i // self.stats_cols) * (self.three_col_width + 1.2 * self.SPACER))

            icon_rect = icon.get_rect(midtop=(x, y_top))
            self.screen.blit(icon, icon_rect)

            desc_rect = desc.get_rect(midbottom=(x, y_top + self.three_col_width - 8))
            self.screen.blit(desc, desc_rect)

            stat_rect = stat.get_rect(midtop=(x, y_top + self.three_col_width - 8))
            self.screen.blit(stat, stat_rect)