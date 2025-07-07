import gtfs_realtime_pb2
import requests
import toml
import os
import time
from collections import defaultdict

def load_config(config_path):
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

def fetch_train_feed(route_id, station_id, feed_urls):
    for key, value in feed_urls.items():
        if route_id in key:
            feed_url = value
            break
    else:
        raise ValueError(f"No feed URL found for route_id: {route_id}")

    feed = fetch_feed(feed_url)
    return extract_trains_for_station(feed, station_id)

def fetch_feed(feed_url):
    response = requests.get(feed_url)
    response.raise_for_status()
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(response.content)
    return feed

def extract_trains_for_station(feed, station_id):
    stop_ids = [f"{station_id}N", f"{station_id}S"]
    train_feed = defaultdict(list)
    now = int(time.time())  # current timestamp in seconds

    for entity in feed.entity:
        if not entity.HasField('trip_update'):
            continue

        trip = entity.trip_update.trip

        for stu in entity.trip_update.stop_time_update:
            if stu.stop_id not in stop_ids:
                continue

            direction = stu.stop_id[-1]  # 'N' or 'S'
            arrival_time = None

            if stu.HasField('arrival') and stu.arrival.HasField('time'):
                arrival_time = stu.arrival.time
            elif stu.HasField('departure') and stu.departure.HasField('time'):
                arrival_time = stu.departure.time

            # ⛔️ Skip trains more than 30 seconds in the past
            if arrival_time and arrival_time < now - 30:
                continue

            if arrival_time:
                train_feed[direction].append({
                    'trip_id': trip.trip_id,
                    'route_id': trip.route_id,
                    'arrival_time': arrival_time,
                })

    # Sort and assign order
    for direction in train_feed:
        train_feed[direction].sort(key=lambda x: x['arrival_time'])
        for i, train in enumerate(train_feed[direction], start=1):
            train['order'] = i

    return train_feed