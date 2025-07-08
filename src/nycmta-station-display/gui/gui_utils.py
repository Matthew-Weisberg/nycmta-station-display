import pygame                 # Pygame library for GUI and graphics rendering
import time                   # Time module for timestamp and weekday calculations
from datetime import datetime # Datetime for getting the current timestamp

# -----------------------------------------------------------------------------------------------------------------
#   Class:      Button
#   Input:      text (str)                – Label to display on the button (optional if icon is used)
#               pos (tuple[int, int])     – (x, y) top-left position of the button
#               size (tuple[int, int])    – Width and height of the button
#               font (pygame.Font)        – Font used for rendering text
#               bg_color (tuple[int])     – RGB background color
#               text_color (tuple[int])   – RGB color for the text
#               hover_color (tuple[int])  – RGB color for hover state
#               icon (pygame.Surface)     – Optional icon to display instead of text
#               border_color (tuple[int]) – RGB color of the border (if any)
#               border_thickness (int)    – Thickness of the border in pixels
#               border_sides (list[str])  – List of sides ("top", "bottom", etc.) to show border
#   Output:     Button object with interactive drawing and hover/click support
#   Description: Reusable button class that supports hover states, optional icon/text, and borders
# -----------------------------------------------------------------------------------------------------------------

class Button:
    def __init__(self, text, pos, size, font, bg_color, text_color, hover_color,
                 icon=None, border_color=None, border_thickness=0, border_sides=None):
        self.text = text
        self.pos = pos
        self.size = size
        self.font = font
        self.bg_color = bg_color
        self.text_color = text_color
        self.hover_color = hover_color
        self.icon = icon
        self.border_color = border_color
        self.border_thickness = border_thickness
        self.border_sides = border_sides or []

        self.rect = pygame.Rect(pos, size)
        self.hovered = False

        # Render text surface (supporting optional "[left]" flag for alignment)
        if self.text:
            if isinstance(self.text, str) and self.text.startswith("[left]"):
                clean_text = self.text.replace("[left]", "", 1)
                self.text_surf = self.font.render(clean_text, True, self.text_color)
                self.text_rect = self.text_surf.get_rect(midleft=(self.rect.left + 10, self.rect.centery))
            else:
                self.text_surf = self.font.render(self.text, True, self.text_color)
                self.text_rect = self.text_surf.get_rect(center=self.rect.center)
        else:
            self.text_surf = None
            self.text_rect = None

        # Scale and center icon if provided
        if self.icon:
            self.icon = pygame.transform.smoothscale(self.icon, (min(size), min(size)))
            self.icon_rect = self.icon.get_rect(center=self.rect.center)
        else:
            self.icon_rect = None

    def draw(self, screen):
        # Draw background based on hover state
        color = self.hover_color if self.hovered else self.bg_color
        pygame.draw.rect(screen, color, self.rect)

        # Draw border on specified sides
        if self.border_color and self.border_thickness > 0:
            x, y, w, h = self.rect
            t = self.border_thickness
            if "top" in self.border_sides:
                pygame.draw.rect(screen, self.border_color, (x, y, w, t))
            if "bottom" in self.border_sides:
                pygame.draw.rect(screen, self.border_color, (x, y + h - t, w, t))
            if "left" in self.border_sides:
                pygame.draw.rect(screen, self.border_color, (x, y, t, h))
            if "right" in self.border_sides:
                pygame.draw.rect(screen, self.border_color, (x + w - t, y, t, h))

        # Draw text or icon
        if self.text_surf:
            screen.blit(self.text_surf, self.text_rect)
        elif self.icon and self.icon_rect:
            screen.blit(self.icon, self.icon_rect)

    def handle_event(self, event):
        # Update hover state on mouse move; detect click on button
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

# -----------------------------------------------------------------------------------------------------------------
#   Function:   crop_transparent_border
#   Input:      image (pygame.Surface) – surface that might have transparent padding
#   Output:     Cropped surface with transparent padding removed
#   Description: Uses alpha channel to crop out fully transparent edges around image content
# -----------------------------------------------------------------------------------------------------------------
def crop_transparent_border(image: pygame.Surface) -> pygame.Surface:
    mask = pygame.mask.from_surface(image)
    rect = mask.get_bounding_rects()
    if rect:
        return image.subsurface(rect[0]).copy()
    return image

# -----------------------------------------------------------------------------------------------------------------
#   Function:   draw_banner
#   Input:      screen (pygame.Surface), screen_width (int), banner_height (int),
#               banner_font (pygame.Font), banner_background_color (tuple),
#               banner_border_color (tuple), banner_border_thickness (int),
#               left_text (str), center_text (str), right_text (str),
#               right_button (Button)
#   Output:     None
#   Description: Draws a full-width banner at the top with optional aligned text and button
# -----------------------------------------------------------------------------------------------------------------
def draw_banner(screen, screen_width, banner_height, banner_font,
                banner_background_color, banner_border_color,
                banner_border_thickness=2,
                left_text="", center_text="", right_text="", right_button=None):

    WHITE = (255, 255, 255)

    pygame.draw.rect(screen, banner_background_color, (0, 0, screen_width, banner_height))
    pygame.draw.line(screen, banner_border_color, (0, banner_height), (screen_width, banner_height), banner_border_thickness)

    button_width = banner_height if right_button else 0

    # Render each text item
    left_surface = banner_font.render(left_text, True, WHITE)
    center_surface = banner_font.render(center_text, True, WHITE)
    right_surface = banner_font.render(right_text, True, WHITE)

    y_pos = (banner_height - center_surface.get_height()) // 2
    screen.blit(left_surface, (20, y_pos))
    screen.blit(center_surface, ((screen_width - center_surface.get_width()) // 2, y_pos))
    screen.blit(right_surface, (screen_width - right_surface.get_width() - button_width - 20, y_pos))

    # Draw right-aligned button if provided
    if right_button:
        right_button.rect.topleft = (screen_width - banner_height, 0)
        right_button.draw(screen)

# -----------------------------------------------------------------------------------------------------------------
#   Function:   draw_train_time
#   Input:      screen, screen_width, train_height, text_y_center, curr_train,
#               destination, minutes_to_arrival, bullet, bullets_dict, divider
#   Output:     None
#   Description: Draws one line of train info including destination, time, and bullet image
# -----------------------------------------------------------------------------------------------------------------
def draw_train_time(screen, screen_width, train_height, text_y_center,
                    curr_train, destination, minutes_to_arrival,
                    bullet, bullets_dict, divider):

    WHITE = (255, 255, 255) if curr_train == 1 else (200, 200, 200)
    bullet = bullet.replace("X", "D")  # Normalize bullet

    train_screen_width = screen_width - divider

    # Calculate font sizes
    font_size_main = int(train_height * 0.25)
    font_size_minute = int(train_height * 0.19)
    font_train_time = pygame.font.SysFont("helvetica", font_size_main, bold=True)
    font_minute = pygame.font.SysFont("helvetica", font_size_minute, bold=True)

    # Format minutes
    minutes_to_arrival = f' {minutes_to_arrival}' if len(str(minutes_to_arrival)) == 1 else minutes_to_arrival

    # Render main text surfaces
    train_surf = font_train_time.render(f"{curr_train}.", True, WHITE)
    minute_surf = font_train_time.render(f"{minutes_to_arrival}", True, WHITE)

    train_rect = train_surf.get_rect(midleft=(divider + int(train_screen_width * 0.03), text_y_center))
    if minutes_to_arrival == 'now':
        minute_rect = minute_surf.get_rect(center=(divider + int(train_screen_width * 0.88), text_y_center))
    else:
        minute_rect = minute_surf.get_rect(midright=(divider + int(train_screen_width * 0.865), text_y_center))

    # Adjust font size for destination text to fit space
    dest_x = divider + int(train_screen_width * 0.19)
    available_width = minute_rect.left - dest_x - 10

    font_size = font_size_main
    dest_font = pygame.font.SysFont("helvetica", font_size, bold=True)
    dest_surf = dest_font.render(destination, True, WHITE)

    # Shrink text if too wide
    if 0.73 * dest_surf.get_width() > available_width:
        dest_font = pygame.font.SysFont("helvetica", int(font_size_main * 0.70), bold=True)
    elif 0.82 * dest_surf.get_width() > available_width:
        dest_font = pygame.font.SysFont("helvetica", int(font_size_main * 0.775), bold=True)
    elif 0.91 * dest_surf.get_width() > available_width:
        dest_font = pygame.font.SysFont("helvetica", int(font_size_main * 0.85), bold=True)
    elif dest_surf.get_width() > available_width:
        dest_font = pygame.font.SysFont("helvetica", int(font_size_main * 0.925), bold=True)

    dest_surf = dest_font.render(destination, True, WHITE)
    dest_rect = dest_surf.get_rect(midleft=(dest_x, text_y_center))

    # Draw all surfaces
    screen.blit(train_surf, train_rect)
    screen.blit(dest_surf, dest_rect)
    screen.blit(minute_surf, minute_rect)

    if minutes_to_arrival != 'now':
        label_surf = font_minute.render("min", True, WHITE)
        label_rect = label_surf.get_rect(midleft=(divider + int(train_screen_width * 0.87), 0))
        label_rect.bottom = minute_rect.bottom - 2
        screen.blit(label_surf, label_rect)

    # Draw bullet icon
    bullet_key = bullet.upper()
    if bullet_key in bullets_dict:
        bullet_image = bullets_dict[bullet_key]
        scale_factor = (1.05 if "D" in bullet else 0.9)
        desired_height = scale_factor * train_surf.get_height()
        scale = desired_height / bullet_image.get_height()
        scaled_bullet = pygame.transform.smoothscale(bullet_image, (int(bullet_image.get_width() * scale), int(desired_height)))
        bullet_rect = scaled_bullet.get_rect(center=(train_rect.right + 25, train_rect.centery))
        screen.blit(scaled_bullet, bullet_rect)

# -----------------------------------------------------------------------------------------------------------------
#   Function:   draw_no_train_time
#   Description: Displays a fallback message when no arrival data is available
# -----------------------------------------------------------------------------------------------------------------
def draw_no_train_time(screen, screen_width, train_height, text_y_center, curr_train, divider):
    WHITE = (255, 255, 255) if curr_train == 1 else (200, 200, 200)
    font_size_main = int(train_height * 0.25)
    font_train_time = pygame.font.SysFont("helvetica", font_size_main, bold=True)
    train_screen_width = screen_width - divider

    train_surf = font_train_time.render(f"{curr_train}.  No train info available", True, WHITE)
    train_rect = train_surf.get_rect(midleft=(divider + int(train_screen_width * 0.03), text_y_center))
    screen.blit(train_surf, train_rect)

# -----------------------------------------------------------------------------------------------------------------
#   Function:   add_transparent_border
#   Description: Pads a surface with a transparent border
# -----------------------------------------------------------------------------------------------------------------
def add_transparent_border(image, padding):
    width, height = image.get_size()
    new_width = width + 2 * padding
    new_height = height + 2 * padding

    new_image = pygame.Surface((new_width, new_height), pygame.SRCALPHA)
    new_image.fill((0, 0, 0, 0))
    new_image.blit(image, (padding, padding))
    return new_image

# -----------------------------------------------------------------------------------------------------------------
#   Function:   get_day_type
#   Description: Returns 'Weekday', 'Saturday', or 'Sunday' from a timestamp
# -----------------------------------------------------------------------------------------------------------------
def get_day_type(arrival_timestamp):
    weekday_num = time.localtime(arrival_timestamp).tm_wday
    if weekday_num == 6:
        return 'Sunday'
    elif weekday_num == 5:
        return 'Saturday'
    else:
        return 'Weekday'

# -----------------------------------------------------------------------------------------------------------------
#   Function:   get_train_text
#   Description: Extracts displayable train information from real-time feed
# -----------------------------------------------------------------------------------------------------------------
def get_train_text(direction, train_feed, curr_train, trips, route_headsigns):
    train_text = None
    now = datetime.now().timestamp()

    for train in train_feed.get(direction, []):
        if train.get('order') == curr_train:
            matching_trip = [
                trip for trip in trips
                if trip['route_id'] == train['route_id']
                and trip['trip_id'] == train['trip_id']
                and trip['service_id'] == get_day_type(train['arrival_time'])
            ]

            if len(matching_trip) != 1:
                destination = route_headsigns[train['route_id']][direction] + '*'
            else:
                destination = matching_trip[0]['trip_headsign']

            minutes = int((train['arrival_time'] - now) / 60) if (train['arrival_time'] - now) > 30 else 'now'

            train_text = {
                'train_num': curr_train,
                'bullet': train['route_id'],
                'arrival_time': train['arrival_time'],
                'destination': destination,
                'minutes': minutes
            }

    return train_text
