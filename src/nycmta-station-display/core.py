import toml
import os
import time
import pygame
from collections import defaultdict
from utils import *
from gui.screen_manager import ScreenManager

WIDTH, HEIGHT = 800, 480 
FRAME_RATE = 60

feed_urls = {
    ("A","C","E","SR") :                "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace",
    ("B","D","F","M","SF") :            "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm",
    ("G") :                             "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-g",
    ("J","Z") :                         "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-jz",
    ("N","Q","R","W") :                 "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw",
    ("L") :                             "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l",
    ("1","2","3","4","5","6","7","S") : "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
    ("SIR") :                           "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-si"
}

def load_config():
    # Build the full path to the config file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, 'config', 'config.toml')
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Missing config file at {config_path}")
    return toml.load(config_path)

def write_to_config(key_path, value):
    """
    Updates a nested key in config/config.toml using colon-delimited path (e.g., "station:latitude").

    Args:
        key_path (str): Colon-delimited string representing nested keys.
        value: The new value to set.
    """
    keys = key_path.split(":")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, 'config', 'config.toml')

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Missing config file at {config_path}")

    # Load existing config
    config = toml.load(config_path)

    # Traverse to the target nested dictionary
    d = config
    for key in keys[:-1]:
        if key not in d or not isinstance(d[key], dict):
            d[key] = {}
        d = d[key]

    # Set the new value
    d[keys[-1]] = value

    # Write the updated config back to file
    with open(config_path, 'w') as f:
        toml.dump(config, f)

def fetch_train_feed(route_id, station_id):
    for key, value in feed_urls.items():
        if route_id in key:
            feed_url = value
    
    feed = fetch_feed(feed_url)
    return extract_trains_for_station(feed, station_id)

def main():
    config = load_config()
    route_id = config['route']['id']
    station_id = config['station']['id']
    lat = config['station']['latitude']
    lon = config['station']['longitude']

    train_feed = fetch_train_feed(route_id, station_id)

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

    update_time = 15 # in seconds
    update_ticks = update_time * frame_rate
    counter = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                result = manager.handle_event(event)
                if isinstance(result, list) and result[0] == "config":
                    for item in result[1]:
                        key_path, value = item.split('|')
                        print(f"changing config {key_path} to {value}")

                        write_to_config(key_path, value)

                        config = load_config()
                        route_id = config['route']['id']
                        station_id = config['station']['id']
                        lat = config['station']['latitude']
                        lon = config['station']['longitude']

                        counter = update_ticks

        if counter >= update_ticks:
            train_feed = fetch_train_feed(route_id, station_id)
            counter = 0

        manager.update(config, train_feed)
        manager.render()
        pygame.display.flip()
        clock.tick(frame_rate)
        counter += 1

    pygame.quit()

if __name__ == "__main__":
    main()
