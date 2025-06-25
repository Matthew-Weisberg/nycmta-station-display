import gtfs_realtime_pb2
import requests
from collections import defaultdict

def fetch_feed(feed_url):
    response = requests.get(feed_url)
    response.raise_for_status()
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(response.content)
    return feed


def extract_trains_for_station(feed, station_id):
    # Add N and S to check both directions
    stop_ids = [f"{station_id}N", f"{station_id}S"]
    train_feed = defaultdict(list)

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

            if arrival_time:
                train_feed[direction].append({
                    'trip_id': trip.trip_id,
                    'route_id': trip.route_id,
                    'arrival_time': arrival_time,
                })

    # Sort and add order number
    for direction in train_feed:
        train_feed[direction].sort(key=lambda x: x['arrival_time'])
        for i, train in enumerate(train_feed[direction], start=1):
            train['order'] = i

    return train_feed