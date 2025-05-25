import pygame                 # Import pygame library for GUI and graphics
import sys                    # Import sys to exit the program cleanly
import os                     # Import os for file path handling
from datetime import datetime # Import datetime to get current date/time
from utils import *           # Import helper functions

# Initialize Pygame modules
pygame.init()
pygame.font.init()            # Initialize font module separately

# Screen settings: width and height of the window
WIDTH, HEIGHT = 1600, 960
# Create a window with given size
screen = pygame.display.set_mode((WIDTH, HEIGHT))
# Set the window title
pygame.display.set_caption("MTA + Weather Display")

# === Initialized variables for layout and colors ===
FRAME_RATE = 144
BANNER_HEIGHT = int(HEIGHT * (0.08))                      # Height of the banner at the top
BANNER_BACKGROUND_COLOR = (40, 40, 40)                                 # Dark grey color for banner background
BANNER_BORDER_COLOR = (255, 255, 255)                         # White color for the bottom line of banner
SPACER = int(HEIGHT * 0.05)                               # Vertical spacing between banner and trains and between trains
TRAIN_HEIGHT = (HEIGHT - BANNER_HEIGHT - 3 * SPACER) // 2   # Height to scale train image to

# Define color constants as RGB tuples
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Time in seconds for the train anim to cross the screen
TRAIN_SPEED = 2.0

# Set up banner_font for rendering text (Helvetica, size 24)
BANNER_FONT = pygame.font.SysFont("Helvetica", int(BANNER_HEIGHT * 0.6))

# Construct the absolute path to the assets/images folder relative to this file
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "../../../assets/images")
# Full path to the train image file (replace with your actual image filename)
IMAGE_PATH = os.path.join(ASSETS_DIR, "r211.png")

# Load the image into a pygame Surface with transparency enabled
train_image = pygame.image.load(IMAGE_PATH).convert_alpha()

# Crop the transparent background border
train_image = crop_transparent_border(train_image)

# Original image dimensions
orig_width, orig_height = train_image.get_size()

# Calculate scale factor to keep aspect ratio
scale_factor = TRAIN_HEIGHT / orig_height

# Calculate new width using scale factor
target_width = int(orig_width * scale_factor)

# Scale the images smoothly to new size
train_image = pygame.transform.smoothscale(train_image, (target_width, TRAIN_HEIGHT))
train_flipped = pygame.transform.flip(train_image, True, False)

# Update width and height variables for the resized images
train_width, train_height = train_image.get_size()

# Set initial horizontal positions for the two trains
# First train starts just off the left edge (negative width)
train1_x = -train_width
# Second train starts just off the right edge (window width)
train2_x = WIDTH

# Create a clock object to control the frame rate
clock = pygame.time.Clock()

def main():
    """Main game loop that runs the pygame window and animations."""
    global train1_x, train2_x                      # Use global variables to update positions

    running = True                                # Control variable for main loop
    while running:
        screen.fill(BLACK)                        # Fill the screen with black color

        # Event handling loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:        # If the user closes the window
                running = False                   # Exit the loop

        # Move the first train to the right by computed pixels per frame
        train1_x += (WIDTH + 2 * train_width) // (TRAIN_SPEED * FRAME_RATE)
        # Move the second (flipped) train to the left by computed pixels per frame
        train2_x -= (WIDTH + 2 * train_width) // (TRAIN_SPEED * FRAME_RATE)

        # Reset first train to left side if it fully passed the right edge
        if train1_x > WIDTH:
            train1_x = -train_width              # Start just off-screen left

        # Reset second train to right side if it fully passed the left edge
        if train2_x < -train_width:
            train2_x = WIDTH                       # Start just off-screen right

        now_str = datetime.now().strftime("%A, %B %d   %I:%M %p")

        # Draw the top banner (date, time, weather)
        draw_banner(screen=screen,
                    screen_width=WIDTH,
                    banner_height=BANNER_HEIGHT,
                    banner_font=BANNER_FONT,
                    banner_background_color=BANNER_BACKGROUND_COLOR,
                    banner_border_color=BANNER_BORDER_COLOR,
                    left_text=now_str,
                    center_text="test",
                    right_text="right text")

        # Calculate vertical positions of the trains using banner height and spacer
        train1_y = BANNER_HEIGHT + SPACER
        train2_y = train1_y + train_height + SPACER

        # Draw the first train image at current position
        screen.blit(train_flipped, (train1_x, train1_y))
        # Draw the flipped train at current position below the first train
        screen.blit(train_image, (train2_x, train2_y))

        # Update the full display surface to the screen
        pygame.display.flip()
        # Limit the frame rate to 60 frames per second
        clock.tick(FRAME_RATE)

    # Quit pygame and exit the program cleanly
    pygame.quit()
    sys.exit()

# If this script is run directly, start the main function
if __name__ == "__main__":
    main()
