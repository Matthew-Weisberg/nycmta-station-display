import pygame                 # Import pygame library for GUI and graphics
import time
from datetime import datetime # Import datetime to get current date/time

# -----------------------------------------------------------------------------------------------------------------
#   Input:      
#   Output:     
#   Desciption: 
# -----------------------------------------------------------------------------------------------------------------

class Button:
    # -----------------------------------------------------------------------------------------------------------------
    #   Class:      Button
    #   Input:      text (str)                – label to display on the button (optional if icon is used)
    #               pos (tuple[int, int])     – (x, y) position of the top-left corner
    #               size (tuple[int, int])    – (width, height) of the button
    #               font (pygame.Font)        – font object used to render the text
    #               bg_color (tuple[int])     – background color in RGB
    #               text_color (tuple[int])   – color of the text in RGB
    #               hover_color (tuple[int])  – background color when mouse hovers over
    #               icon (pygame.Surface)     – optional icon image to display (centered)
    #               border_color (tuple[int]) – RGB color of the border (default: None = no border)
    #               border_thickness (int)    – thickness of the border lines (default: 0)
    #               border_sides (list[str])  – sides with borders: "top", "bottom", "left", "right"
    #   Output:     A button object that can be drawn to screen and respond to mouse/touch events
    #   Description: A reusable UI component that renders a clickable button with hover effect
    #                and optional icon support. Works with both mouse and touch screens.
    # -----------------------------------------------------------------------------------------------------------------
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

        if self.text:
            # Check for special flag to left-align
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

        # Scale icon
        if self.icon:
            self.icon = pygame.transform.smoothscale(self.icon, (min(size), min(size)))
            self.icon_rect = self.icon.get_rect(center=self.rect.center)
        else:
            self.icon_rect = None

    def draw(self, screen):
        # Draw button background
        color = self.hover_color if self.hovered else self.bg_color
        pygame.draw.rect(screen, color, self.rect)

        # Draw borders on specified sides
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
        # Compatible with touch screens since taps also generate MOUSEBUTTONDOWN events
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

def crop_transparent_border(image: pygame.Surface) -> pygame.Surface:
    # -----------------------------------------------------------------------------------------------------------------
    #   Function:   crop_transparent_border
    #   Input:      image (pygame.Surface) – a surface that may contain transparent padding
    #   Output:     image (pygame.Surface) – a new surface cropped to exclude transparent borders
    #   Description: Analyzes the alpha channel of the input surface and crops out any fully
    #                transparent regions around the visible (non-transparent) content. If the
    #                image is fully transparent, the original surface is returned.
    # -----------------------------------------------------------------------------------------------------------------

    # Create a mask identifying all non-transparent pixels (alpha > 0)
    mask = pygame.mask.from_surface(image)

    # Get a list of bounding rects (smallest rectangles covering non-transparent areas)
    rect = mask.get_bounding_rects()

    if rect:
        # Use the first bounding rectangle (usually the only one)
        bounding_rect = rect[0]

        # Crop the image to this bounding rectangle and return a new surface
        cropped = image.subsurface(bounding_rect).copy()
        return cropped
    else:
        # The image is fully transparent; return it as-is
        return image
    
def draw_banner(screen,
                screen_width,
                banner_height,
                banner_font,
                banner_background_color,
                banner_border_color,
                banner_border_thickness=2,
                left_text="",
                center_text="",
                right_text="",
                right_button=None):
    # -----------------------------------------------------------------------------------------------------------------
    #   Function:   draw_banner
    #   Inputs:
    #       screen (pygame.Surface)              – the main display surface to draw the banner on
    #       screen_width (int)                   – width of the screen in pixels
    #       banner_height (int)                  – height of the banner in pixels
    #       banner_font (pygame.font.Font)       – the base font to use for text
    #       banner_background_color (tuple)      – RGB color for the banner background
    #       banner_border_color (tuple)          – RGB color for the banner bottom border
    #       left_text (str)                      – text to display on the left side of the banner
    #       center_text (str)                    – text to display centered in the banner
    #       right_text (str)                     – text to display on the right side of the banner
    #       right_button (Button)                – optional Button object to render at the far right
    #   Output:     None
    #   Description: Renders a top banner with optional left, center, and right-aligned text.
    #                If provided, displays a square button at the far right of the banner.
    # -----------------------------------------------------------------------------------------------------------------

    WHITE = (255, 255, 255)

    # Draw banner background
    pygame.draw.rect(screen, banner_background_color, (0, 0, screen_width, banner_height))

    # Draw bottom border line
    pygame.draw.line(screen, banner_border_color, (0, banner_height), (screen_width, banner_height), banner_border_thickness)

    # Adjust width for right button
    button_width = banner_height if right_button else 0
    max_width = screen_width - button_width - 40  # padding

    # Font scaling loop
    font_size = banner_font.get_height()
    font_name = banner_font.get_name() if hasattr(banner_font, 'get_name') else None
    font_path = None
    if font_name:
        try:
            banner_font = pygame.font.SysFont(font_name, font_size)
        except:
            pass

    while font_size > 10:
        font = pygame.font.Font(font_path, font_size) if font_path else pygame.font.SysFont(font_name, font_size)
        left_surface = font.render(left_text, True, WHITE)
        center_surface = font.render(center_text, True, WHITE)
        right_surface = font.render(right_text, True, WHITE)

        total_width = left_surface.get_width() + center_surface.get_width() + right_surface.get_width() + 60
        if total_width <= max_width:
            break
        font_size -= 1

    y_pos = (banner_height - center_surface.get_height()) // 2

    # Render text
    screen.blit(left_surface, (20, y_pos))
    center_x = (screen_width - center_surface.get_width()) // 2
    screen.blit(center_surface, (center_x, y_pos))
    right_x = screen_width - right_surface.get_width() - button_width - 20
    screen.blit(right_surface, (right_x, y_pos))

    # Render right-side button (if present)
    if right_button:
        right_button.rect.topleft = (screen_width - banner_height, 0)
        #right_button.text_rect = right_button.text_surf.get_rect(center=right_button.rect.center)
        right_button.draw(screen)

def draw_train_time(screen,
                    screen_width,
                    train_height,
                    text_y_center,
                    curr_train,
                    destination,
                    minutes_to_arrival,
                    bullet,
                    bullets_dict):  # Pass the preloaded bullet images dictionary here

    WHITE = (255, 255, 255)

    # Initialize fonts (adjust sizes as needed)
    font_train_time = pygame.font.SysFont("helvetica", int(train_height * 0.27), bold=True)
    font_minute = pygame.font.SysFont("helvetica", int(train_height * 0.18), bold=True)

    # Render text surfaces
    train_surf = font_train_time.render(f"{curr_train}.", True, WHITE)
    dest_surf = font_train_time.render(f"{destination}", True, WHITE)
    minute_surf = font_train_time.render(f"{minutes_to_arrival}", True, WHITE)

    # Align text vertically centered at y = text_y_center
    train_rect = train_surf.get_rect(midleft=(int(screen_width * 0.03), text_y_center))
    dest_rect = dest_surf.get_rect(midleft=(int(screen_width * 0.15), text_y_center))

    # Right-align minute text inside its box (fixed width region ending at 80%)
    if minutes_to_arrival == 'now':
            minute_rect = minute_surf.get_rect(midright=(int(screen_width * 0.89), text_y_center))
    else:
        minute_rect = minute_surf.get_rect(midright=(int(screen_width * 0.875), text_y_center))

    # Blit text surfaces
    screen.blit(train_surf, train_rect)
    screen.blit(dest_surf, dest_rect)
    screen.blit(minute_surf, minute_rect)

    # Align label (min) so that its bottom matches minute_surf
    if not minutes_to_arrival == 'now':
        label_surf = font_minute.render("min", True, WHITE)
        label_rect = label_surf.get_rect(midleft=(int(screen_width * 0.87), 0))  # Temporary y=0
        label_rect.bottom = minute_rect.bottom - 7
        screen.blit(label_surf, label_rect)

    # Draw bullet image (if it exists)
    additional_scale_factor = 0.8
    bullet_key = bullet.upper()

    if bullet_key in bullets_dict:
        bullet_image = bullets_dict[bullet_key]

        # Scale bullet image to match train_surf height
        desired_height = additional_scale_factor * train_surf.get_height()
        scale_factor = desired_height / bullet_image.get_height()
        new_width = int(bullet_image.get_width() * scale_factor)
        scaled_bullet = pygame.transform.smoothscale(bullet_image, (new_width, int(desired_height)))

        # Align bullet image just right of train text
        bullet_rect = scaled_bullet.get_rect(midleft=(train_rect.right + 10, train_rect.centery))
        screen.blit(scaled_bullet, bullet_rect)

def add_transparent_border(image, padding):
    """Adds a transparent border around the given image."""
    width, height = image.get_size()
    new_width = width + 2 * padding
    new_height = height + 2 * padding

    # Create a new surface with transparency
    new_image = pygame.Surface((new_width, new_height), pygame.SRCALPHA)
    new_image.fill((0, 0, 0, 0))  # Fully transparent

    # Blit the original image in the center
    new_image.blit(image, (padding, padding))

    return new_image

def get_day_type(arrival_timestamp):
    # Get weekday as an integer (0 = Monday, 6 = Sunday)
    weekday_num = time.localtime(arrival_timestamp).tm_wday

    # Convert to 'Weekday', 'Saturday', or 'Sunday'
    if weekday_num == 6:
        day_type = 'Sunday'
    elif weekday_num == 5:
        day_type = 'Saturday'
    else:
        day_type = 'Weekday'

    return day_type
