import pygame
from screens.screen_manager import ScreenManager

WIDTH, HEIGHT = 1600, 900
FRAME_RATE = 60

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("MTA + Weather Display")
    clock = pygame.time.Clock()
    frame_rate = 60

    manager = ScreenManager(screen, frame_rate)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                manager.handle_event(event)

        manager.update()
        manager.render()
        pygame.display.flip()
        clock.tick(frame_rate)

    pygame.quit()

if __name__ == "__main__":
    main()
