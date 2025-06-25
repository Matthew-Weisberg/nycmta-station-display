import toml
import os
import time
import pygame
from collections import defaultdict
from utils import *
from gui.screen_manager import ScreenManager

WIDTH, HEIGHT = 800, 450 
FRAME_RATE = 60

def load_config():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Build the full path to the config file
    config_path = os.path.join(base_dir, 'config', 'config.toml')
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Missing config file at {config_path}")
    return toml.load(config_path)

def main():
    config = load_config()
    station_id = config['station']['id']
    lat = config['station']['latitude']
    lon = config['station']['longitude']
    feed_url = config['feed_url']

    print(f"Checking trains for station {station_id} at lat={lat}, lon={lon}")

    feed = fetch_feed(feed_url)
    train_feed = extract_trains_for_station(feed, station_id)

    for direction, entries in train_feed.items():
        print(f"\nDirection {direction}:")
        for train in entries:
            formatted_time = time.strftime('%I:%M:%S %p', time.localtime(train['arrival_time']))
            print(f"  Route {train['route_id']} - Trip {train['trip_id']} - Arrival: {formatted_time}")

    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("MTA + Weather Display")
    clock = pygame.time.Clock()
    frame_rate = 60

    manager = ScreenManager(screen, 
                            frame_rate,
                            train_feed,
                            config)
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
