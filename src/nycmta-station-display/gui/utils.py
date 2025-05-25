import pygame                 # Import pygame library for GUI and graphics
import sys                    # Import sys to exit the program cleanly
import os                     # Import os for file path handling
from datetime import datetime # Import datetime to get current date/time

# -----------------------------------------------------------------------------------------------------------------
#   Input:      
#   Output:     
#   Desciption: 
# -----------------------------------------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------------------------------------
#   Function:   crop_transparent_border
#   Input:      image (pygame.Surface) – a surface that may contain transparent padding
#   Output:     image (pygame.Surface) – a new surface cropped to exclude transparent borders
#   Description: Analyzes the alpha channel of the input surface and crops out any fully
#                transparent regions around the visible (non-transparent) content. If the
#                image is fully transparent, the original surface is returned.
# -----------------------------------------------------------------------------------------------------------------
def crop_transparent_border(image: pygame.Surface) -> pygame.Surface:
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
#   Output:     None
#   Description: Renders a top banner with optional left, center, and right-aligned text.
#                Automatically scales down font size if needed to ensure all text fits.
# -----------------------------------------------------------------------------------------------------------------
def draw_banner(screen,
                screen_width,
                banner_height,
                banner_font,
                banner_background_color,
                banner_border_color,
                left_text="",
                center_text="",
                right_text=""):

    WHITE = (255, 255, 255)

    # Draw banner background
    pygame.draw.rect(screen, banner_background_color, (0, 0, screen_width, banner_height))

    # Draw bottom border line
    pygame.draw.line(screen, banner_border_color, (0, banner_height - 1), (screen_width, banner_height - 1), 2)

    # Try different font sizes until everything fits
    max_width = screen_width - 40  # leave padding
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

        total_width = left_surface.get_width() + center_surface.get_width() + right_surface.get_width() + 60  # padding
        if total_width <= max_width:
            break
        font_size -= 1

    # Center text vertically
    y_pos = (banner_height - center_surface.get_height()) // 2

    # Left-aligned
    screen.blit(left_surface, (20, y_pos))

    # Center-aligned
    center_x = (screen_width - center_surface.get_width()) // 2
    screen.blit(center_surface, (center_x, y_pos))

    # Right-aligned
    right_x = screen_width - right_surface.get_width() - 20
    screen.blit(right_surface, (right_x, y_pos))
